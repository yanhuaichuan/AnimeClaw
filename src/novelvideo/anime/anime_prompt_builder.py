# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Layered prompt builder — never novel → image in one hop."""

from __future__ import annotations

from novelvideo.anime.acting_engine import ActingEngine
from novelvideo.anime.camera_engine import MangaCameraEngine
from novelvideo.anime.character_bible import identity_lock_lines
from novelvideo.anime.character_state import state_lines
from novelvideo.anime.models import (
    AnimeShot,
    CharacterBible,
    CharacterState,
    SceneBible,
    StoryWorld,
    StyleBible,
)
from novelvideo.anime.scene_bible import scene_lock_lines
from novelvideo.anime.style_bible import negative_prompt, style_lock_lines


class AnimePromptBuilder:
    def __init__(self) -> None:
        self.camera = MangaCameraEngine()
        self.acting = ActingEngine()

    def build_image_prompt(
        self,
        *,
        world: StoryWorld,
        character: CharacterBible,
        character_state: CharacterState | None,
        scene: SceneBible | None,
        shot: AnimeShot,
        style: StyleBible,
    ) -> str:
        layers = [
            *style_lock_lines(style),
            world.world and f"world: {world.world}",
            world.era and f"era: {world.era}",
            *identity_lock_lines(character),
            *(state_lines(character_state) if character_state else []),
            *(scene_lock_lines(scene) if scene else []),
            self.camera.prompt_fragment(shot.camera),
            self.acting.image_fragment(shot.acting),
            shot.dialogue.text if shot.dialogue and shot.dialogue.text else "",
            shot.lighting,
            shot.style_notes,
            "cinematic manga composition, readable silhouette",
        ]
        return ", ".join(part for part in layers if part)

    def build_motion_prompt(self, shot: AnimeShot) -> str:
        return ", ".join(
            part
            for part in (
                self.acting.motion_fragment(shot.acting),
                self.camera.prompt_fragment(shot.camera),
                shot.motion_prompt,
            )
            if part
        )

    def build_negative(self, style: StyleBible) -> str:
        return negative_prompt(style)

    def enrich_shot(
        self,
        shot: AnimeShot,
        *,
        world: StoryWorld,
        character: CharacterBible,
        character_state: CharacterState | None,
        scene: SceneBible | None,
        style: StyleBible,
    ) -> AnimeShot:
        shot.image_prompt = self.build_image_prompt(
            world=world,
            character=character,
            character_state=character_state,
            scene=scene,
            shot=shot,
            style=style,
        )
        shot.motion_prompt = self.build_motion_prompt(shot)
        return shot
