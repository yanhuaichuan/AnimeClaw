# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""File-backed AnimeClaw store under ``{state_dir}/anime/``."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from novelvideo.anime.models import (
    AnimeBeat,
    AnimeShot,
    CharacterBible,
    EpisodeBundle,
    EpisodeState,
    PlotThread,
    SceneBible,
    StoryMemory,
    StoryWorld,
    StyleBible,
)
from novelvideo.utils.asset_names import path_safe_asset_name

T = TypeVar("T", bound=BaseModel)


def _atomic_write(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


def _read_json(path: Path) -> dict | list | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def episode_dirname(episode: int) -> str:
    return f"ep{int(episode):03d}"


class AnimeStore:
    """JSON documents for world / bible / episode continuity."""

    def __init__(self, state_dir: str | Path):
        self.root = Path(state_dir) / "anime"
        self.root.mkdir(parents=True, exist_ok=True)

    def episode_dir(self, episode: int) -> Path:
        path = self.root / "episodes" / episode_dirname(episode)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def load_world(self) -> StoryWorld:
        raw = _read_json(self.root / "story_world.json")
        return StoryWorld.model_validate(raw or {})

    def save_world(self, world: StoryWorld) -> StoryWorld:
        _atomic_write(self.root / "story_world.json", world.model_dump())
        return world

    def load_style(self) -> StyleBible:
        raw = _read_json(self.root / "style_bible.json")
        return StyleBible.model_validate(raw or {})

    def save_style(self, style: StyleBible) -> StyleBible:
        _atomic_write(self.root / "style_bible.json", style.model_dump())
        return style

    def load_memory(self) -> StoryMemory:
        raw = _read_json(self.root / "story_memory.json")
        return StoryMemory.model_validate(raw or {})

    def save_memory(self, memory: StoryMemory) -> StoryMemory:
        _atomic_write(self.root / "story_memory.json", memory.model_dump())
        return memory

    def _bible_dir(self, kind: str) -> Path:
        path = self.root / kind
        path.mkdir(parents=True, exist_ok=True)
        return path

    def list_character_bibles(self) -> list[CharacterBible]:
        items: list[CharacterBible] = []
        for path in sorted(self._bible_dir("character_bible").glob("*.json")):
            raw = _read_json(path)
            if isinstance(raw, dict):
                items.append(CharacterBible.model_validate(raw))
        return items

    def get_character_bible(self, character_id: str) -> CharacterBible | None:
        safe = path_safe_asset_name(character_id)
        raw = _read_json(self._bible_dir("character_bible") / f"{safe}.json")
        return CharacterBible.model_validate(raw) if isinstance(raw, dict) else None

    def save_character_bible(self, bible: CharacterBible) -> CharacterBible:
        safe = path_safe_asset_name(bible.id)
        _atomic_write(self._bible_dir("character_bible") / f"{safe}.json", bible.model_dump())
        return bible

    def list_scene_bibles(self) -> list[SceneBible]:
        items: list[SceneBible] = []
        for path in sorted(self._bible_dir("scene_bible").glob("*.json")):
            raw = _read_json(path)
            if isinstance(raw, dict):
                items.append(SceneBible.model_validate(raw))
        return items

    def get_scene_bible(self, scene_id: str) -> SceneBible | None:
        safe = path_safe_asset_name(scene_id)
        raw = _read_json(self._bible_dir("scene_bible") / f"{safe}.json")
        return SceneBible.model_validate(raw) if isinstance(raw, dict) else None

    def save_scene_bible(self, bible: SceneBible) -> SceneBible:
        safe = path_safe_asset_name(bible.id)
        _atomic_write(self._bible_dir("scene_bible") / f"{safe}.json", bible.model_dump())
        return bible

    def load_plot_threads(self) -> list[PlotThread]:
        raw = _read_json(self.root / "plot_threads.json")
        if not isinstance(raw, list):
            return []
        return [PlotThread.model_validate(item) for item in raw]

    def save_plot_threads(self, threads: list[PlotThread]) -> list[PlotThread]:
        _atomic_write(
            self.root / "plot_threads.json",
            [item.model_dump() for item in threads],
        )
        return threads

    def load_episode(self, episode: int) -> EpisodeBundle:
        folder = self.episode_dir(episode)
        state_raw = _read_json(folder / "state.json")
        state = (
            EpisodeState.model_validate(state_raw)
            if isinstance(state_raw, dict)
            else EpisodeState(episode=episode)
        )
        beats_raw = _read_json(folder / "beats.json") or []
        shots_raw = _read_json(folder / "shots.json") or []
        preview_raw = _read_json(folder / "preview.json") or {}
        return EpisodeBundle(
            episode=state,
            beats=[AnimeBeat.model_validate(item) for item in beats_raw]
            if isinstance(beats_raw, list)
            else [],
            shots=[AnimeShot.model_validate(item) for item in shots_raw]
            if isinstance(shots_raw, list)
            else [],
            preview=preview_raw if isinstance(preview_raw, dict) else {},
        )

    def save_episode(self, bundle: EpisodeBundle) -> EpisodeBundle:
        folder = self.episode_dir(bundle.episode.episode)
        _atomic_write(folder / "state.json", bundle.episode.model_dump())
        _atomic_write(folder / "beats.json", [item.model_dump() for item in bundle.beats])
        _atomic_write(folder / "shots.json", [item.model_dump() for item in bundle.shots])
        if bundle.preview:
            _atomic_write(folder / "preview.json", bundle.preview)
        return bundle

    def save_shots(self, episode: int, shots: list[AnimeShot]) -> list[AnimeShot]:
        folder = self.episode_dir(episode)
        _atomic_write(folder / "shots.json", [item.model_dump() for item in shots])
        return shots

    def save_continuity(self, episode: int, issues: list[dict]) -> None:
        _atomic_write(self.episode_dir(episode) / "continuity.json", issues)

    def save_export(self, episode: int, payload: dict) -> Path:
        path = self.episode_dir(episode) / "export.json"
        _atomic_write(path, payload)
        return path
