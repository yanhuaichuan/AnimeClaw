# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Anime Director — plan / check / recommend / repair. Never silent-generate."""

from __future__ import annotations

from novelvideo.anime.camera_engine import MangaCameraEngine
from novelvideo.anime.continuity_engine import ContinuityEngine
from novelvideo.anime.models import AnimeShot, ContinuityIssue
from novelvideo.anime.store import AnimeStore


class AnimeDirector:
    def __init__(self) -> None:
        self.camera = MangaCameraEngine()
        self.continuity = ContinuityEngine()

    def recommend(self, store: AnimeStore, episode: int) -> list[dict]:
        bundle = store.load_episode(episode)
        issues = self.continuity.check_episode(store, episode)
        notes: list[dict] = []
        for shot in bundle.shots:
            notes.extend(self._shot_notes(shot))
        for issue in issues:
            notes.append(
                {
                    "kind": "continuity",
                    "shot_id": issue.shot_id,
                    "message": _issue_message(issue),
                    "action": "repair",
                }
            )
        if bundle.episode.hook == "":
            notes.append(
                {
                    "kind": "hook",
                    "message": "First 3 seconds need an anomaly, conflict, or strong visual.",
                    "action": "plan",
                }
            )
        if bundle.episode.cliffhanger == "":
            notes.append(
                {
                    "kind": "cliffhanger",
                    "message": "Episode should end on a next-episode bait, not a closed story.",
                    "action": "plan",
                }
            )
        return notes

    def _shot_notes(self, shot: AnimeShot) -> list[dict]:
        notes: list[dict] = []
        emotion = shot.acting.emotion
        if emotion in {"surprised", "determined"} and shot.camera.shot_size in {
            "long_shot",
            "full_shot",
        }:
            notes.append(
                {
                    "kind": "camera",
                    "shot_id": shot.id,
                    "message": (
                        f"Shot {shot.id} should not stay on a wide frame — this is a "
                        f"{emotion} beat. Prefer Close Up + Eye Zoom."
                    ),
                    "action": "recommend",
                    "camera": self.camera.plan_for_emotion(emotion).model_dump(),
                }
            )
        return notes

    def repair(self, store: AnimeStore, episode: int, shot_id: str) -> AnimeShot | None:
        from novelvideo.anime.anime_prompt_builder import AnimePromptBuilder
        from novelvideo.anime.character_state import find_character_state

        bundle = store.load_episode(episode)
        shot = next((item for item in bundle.shots if item.id == shot_id), None)
        if shot is None:
            return None
        world = store.load_world()
        style = store.load_style()
        builder = AnimePromptBuilder()
        character_id = shot.characters[0] if shot.characters else ""
        bible = store.get_character_bible(character_id) if character_id else None
        scene = store.get_scene_bible(shot.scene_id) if shot.scene_id else None
        state = find_character_state(bundle.episode, character_id) if character_id else None
        if bible:
            builder.enrich_shot(
                shot,
                world=world,
                character=bible,
                character_state=state,
                scene=scene,
                style=style,
            )
        store.save_shots(episode, bundle.shots)
        return shot


def _issue_message(issue: ContinuityIssue) -> str:
    return (
        f"{issue.kind}: {issue.previous or '—'} → {issue.current or '—'}."
        + (f" {issue.fix}" if issue.fix else "")
    )
