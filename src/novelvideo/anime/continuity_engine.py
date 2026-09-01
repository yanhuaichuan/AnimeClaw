# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Shot-to-shot and episode-to-episode continuity rules."""

from __future__ import annotations

from novelvideo.anime.character_state import find_character_state
from novelvideo.anime.models import (
    AnimeShot,
    CharacterBible,
    CharacterState,
    ContinuityIssue,
    EpisodeState,
    SceneBible,
    StyleBible,
)
from novelvideo.anime.store import AnimeStore


class ContinuityEngine:
    def check_episode(self, store: AnimeStore, episode: int) -> list[ContinuityIssue]:
        bundle = store.load_episode(episode)
        bibles = {item.id: item for item in store.list_character_bibles()}
        scenes = {item.id: item for item in store.list_scene_bibles()}
        style = store.load_style()
        issues: list[ContinuityIssue] = []
        issues.extend(self.check_shots(bundle.shots, bibles, scenes, style))
        if episode > 1:
            previous = store.load_episode(episode - 1)
            issues.extend(
                self.check_story_states(previous.episode, bundle.episode, bibles)
            )
        store.save_continuity(episode, [item.model_dump() for item in issues])
        return issues

    def check_shots(
        self,
        shots: list[AnimeShot],
        bibles: dict[str, CharacterBible],
        scenes: dict[str, SceneBible],
        style: StyleBible,
    ) -> list[ContinuityIssue]:
        issues: list[ContinuityIssue] = []
        last_by_character: dict[str, AnimeShot] = {}
        last_scene: str | None = None
        for shot in shots:
            if last_scene and shot.scene_id and shot.scene_id != last_scene:
                if "scene" in shot.locks:
                    issues.append(
                        ContinuityIssue(
                            kind="scene",
                            shot_id=shot.id,
                            previous=last_scene,
                            current=shot.scene_id,
                            fix="Keep the locked scene unless the beat explicitly changes location.",
                        )
                    )
            if shot.scene_id:
                last_scene = shot.scene_id
            if shot.scene_id and shot.scene_id not in scenes:
                issues.append(
                    ContinuityIssue(
                        severity="warning",
                        kind="scene_missing",
                        shot_id=shot.id,
                        current=shot.scene_id,
                        fix="Create a Scene Bible before generating this shot.",
                    )
                )
            for character_id in shot.characters:
                bible = bibles.get(character_id)
                if bible is None:
                    issues.append(
                        ContinuityIssue(
                            kind="character_missing",
                            character_id=character_id,
                            shot_id=shot.id,
                            current=character_id,
                            fix="Bind this shot to a Character Bible.",
                        )
                    )
                    continue
                previous = last_by_character.get(character_id)
                issues.extend(self._compare_character(previous, shot, bible, style))
                last_by_character[character_id] = shot
        return issues

    def _compare_character(
        self,
        previous: AnimeShot | None,
        current: AnimeShot,
        bible: CharacterBible,
        style: StyleBible,
    ) -> list[ContinuityIssue]:
        issues: list[ContinuityIssue] = []
        blob = " ".join(
            part
            for part in (current.image_prompt, current.style_notes, current.motion_prompt)
            if part
        ).lower()
        for signature in bible.signature:
            if signature and signature.lower() not in blob:
                issues.append(
                    ContinuityIssue(
                        kind="signature",
                        character_id=bible.id,
                        shot_id=current.id,
                        previous=signature,
                        current="missing",
                        fix=f"Keep {signature} visible on {bible.name}.",
                    )
                )
        if bible.appearance.hair and bible.appearance.hair.lower() not in blob:
            issues.append(
                ContinuityIssue(
                    kind="hair",
                    character_id=bible.id,
                    shot_id=current.id,
                    previous=bible.appearance.hair,
                    current="unspecified",
                    fix=f"Lock hair as {bible.appearance.hair}.",
                )
            )
        if bible.appearance.eyes and bible.appearance.eyes.lower() not in blob:
            issues.append(
                ContinuityIssue(
                    kind="eyes",
                    character_id=bible.id,
                    shot_id=current.id,
                    previous=bible.appearance.eyes,
                    current="unspecified",
                    fix=f"Lock eyes as {bible.appearance.eyes}.",
                )
            )
        if bible.costume and bible.costume.lower() not in blob:
            issues.append(
                ContinuityIssue(
                    kind="costume",
                    character_id=bible.id,
                    shot_id=current.id,
                    previous=bible.costume,
                    current="unspecified",
                    fix=f"Keep costume: {bible.costume}.",
                )
            )
        if previous:
            issues.extend(self._handedness(previous, current, bible))
        if style.art_style and current.style_notes:
            if style.art_style.lower() not in current.style_notes.lower():
                issues.append(
                    ContinuityIssue(
                        severity="warning",
                        kind="style",
                        shot_id=current.id,
                        previous=style.art_style,
                        current=current.style_notes,
                        fix="Reuse the Style Bible art style.",
                    )
                )
        return issues

    def _handedness(
        self,
        previous: AnimeShot,
        current: AnimeShot,
        bible: CharacterBible,
    ) -> list[ContinuityIssue]:
        prev_hand = _weapon_hand(previous)
        curr_hand = _weapon_hand(current)
        if prev_hand and curr_hand and prev_hand != curr_hand:
            return [
                ContinuityIssue(
                    kind="weapon_hand",
                    character_id=bible.id,
                    shot_id=current.id,
                    previous=f"Sword → {prev_hand} hand",
                    current=f"Sword → {curr_hand} hand",
                    fix=f"Keep weapon in {prev_hand} hand.",
                )
            ]
        return []

    def check_story_states(
        self,
        previous: EpisodeState,
        current: EpisodeState,
        bibles: dict[str, CharacterBible],
    ) -> list[ContinuityIssue]:
        issues: list[ContinuityIssue] = []
        for prior in previous.character_states:
            now = find_character_state(current, prior.character_id)
            if prior.injured and now and not now.injured and not now.extras.get("healed"):
                name = bibles.get(prior.character_id).name if prior.character_id in bibles else prior.character_id
                issues.append(
                    ContinuityIssue(
                        kind="story_injury",
                        character_id=prior.character_id,
                        previous=f"EP{previous.episode:03d} injured={prior.injured} {prior.left_arm or prior.right_arm}",
                        current=f"EP{current.episode:03d} injured={now.injured}",
                        fix=f"{name} was injured — keep the wound or mark it healed in Character State.",
                    )
                )
        return issues

    def repair_shot_prompt(
        self,
        shot: AnimeShot,
        bible: CharacterBible,
        state: CharacterState | None,
    ) -> AnimeShot:
        from novelvideo.anime.character_bible import identity_lock_lines
        from novelvideo.anime.character_state import state_lines

        locks = identity_lock_lines(bible)
        if state:
            locks.extend(state_lines(state))
        prefix = ", ".join(locks)
        if prefix and prefix.lower() not in shot.image_prompt.lower():
            shot.image_prompt = f"{prefix}. {shot.image_prompt}".strip()
        return shot


def _weapon_hand(shot: AnimeShot) -> str | None:
    text = f"{shot.image_prompt} {shot.motion_prompt} {shot.acting.body}".lower()
    weapon = ("sword", "weapon", "blade", "剑")
    if not any(token in text for token in weapon):
        return None
    left = any(
        token in text
        for token in ("sword in left hand", "weapon in left", "left hand", "左手剑", "剑在左手")
    )
    right = any(
        token in text
        for token in ("sword in right hand", "weapon in right", "right hand", "右手剑", "剑在右手")
    )
    if left and not right:
        return "left"
    if right and not left:
        return "right"
    return None
