# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Scene bible — locked locations, weather, lighting, props."""

from __future__ import annotations

from novelvideo.anime.models import SceneBible
from novelvideo.anime.store import AnimeStore
from novelvideo.utils.asset_names import path_safe_asset_name


def scene_lock_lines(bible: SceneBible) -> list[str]:
    return [
        line
        for line in (
            f"scene {bible.name}",
            bible.location and f"location: {bible.location}",
            bible.time and f"time: {bible.time}",
            bible.weather and f"weather: {bible.weather}",
            bible.lighting and f"lighting: {bible.lighting}",
            *([f"prop: {item}" for item in bible.props]),
            bible.description,
        )
        if line
    ]


def upsert_scene(store: AnimeStore, payload: dict) -> SceneBible:
    bible = SceneBible.model_validate(payload)
    if not bible.id:
        bible.id = path_safe_asset_name(bible.name)
    return store.save_scene_bible(bible)
