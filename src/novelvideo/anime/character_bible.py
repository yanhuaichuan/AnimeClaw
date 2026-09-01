# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Character bible helpers — identity that must not drift."""

from __future__ import annotations

from novelvideo.anime.models import CharacterBible
from novelvideo.anime.store import AnimeStore
from novelvideo.utils.asset_names import path_safe_asset_name


def identity_lock_lines(bible: CharacterBible) -> list[str]:
    appearance = bible.appearance
    lines = [
        f"character {bible.name}",
        appearance.hair and f"hair: {appearance.hair}",
        appearance.eyes and f"eyes: {appearance.eyes}",
        appearance.face and f"face: {appearance.face}",
        appearance.age and f"age: {appearance.age}",
        appearance.height is not None and f"height: {appearance.height}cm",
        bible.costume and f"costume: {bible.costume}",
        *([f"signature: {item}" for item in bible.signature]),
    ]
    return [line for line in lines if line]


def upsert_bible(store: AnimeStore, payload: dict) -> CharacterBible:
    bible = CharacterBible.model_validate(payload)
    if not bible.id:
        bible.id = path_safe_asset_name(bible.name)
    return store.save_character_bible(bible)
