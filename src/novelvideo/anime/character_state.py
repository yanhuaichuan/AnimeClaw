# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Per-episode character state — what happened to this person now."""

from __future__ import annotations

from novelvideo.anime.models import CharacterState, EpisodeState


def state_lines(state: CharacterState) -> list[str]:
    extras = [f"{key}: {value}" for key, value in state.extras.items() if value]
    return [
        line
        for line in (
            "injured" if state.injured else "",
            state.left_arm and f"left arm: {state.left_arm}",
            state.right_arm and f"right arm: {state.right_arm}",
            state.emotion and f"emotion: {state.emotion}",
            state.clothes and f"clothes: {state.clothes}",
            *extras,
        )
        if line
    ]


def upsert_character_state(episode: EpisodeState, next_state: CharacterState) -> EpisodeState:
    kept = [
        item
        for item in episode.character_states
        if item.character_id != next_state.character_id
    ]
    kept.append(next_state)
    episode.character_states = kept
    return episode


def find_character_state(episode: EpisodeState, character_id: str) -> CharacterState | None:
    for item in episode.character_states:
        if item.character_id == character_id:
            return item
    return None
