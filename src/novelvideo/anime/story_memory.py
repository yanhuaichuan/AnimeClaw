# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Long-form IP memory — facts the next episode must still know."""

from __future__ import annotations

from novelvideo.anime.models import StoryMemory
from novelvideo.anime.store import AnimeStore


def remember(store: AnimeStore, **updates: list[str] | dict[str, str]) -> StoryMemory:
    memory = store.load_memory()
    for key, value in updates.items():
        current = getattr(memory, key, None)
        if isinstance(current, list) and isinstance(value, list):
            merged = list(current)
            for item in value:
                if item not in merged:
                    merged.append(item)
            setattr(memory, key, merged)
        elif isinstance(current, dict) and isinstance(value, dict):
            current.update(value)
    return store.save_memory(memory)


def context_block(memory: StoryMemory) -> str:
    chunks = []
    if memory.events:
        chunks.append("events: " + "; ".join(memory.events[-12:]))
    if memory.secrets:
        chunks.append("secrets: " + "; ".join(memory.secrets[-8:]))
    if memory.injuries:
        chunks.append("injuries: " + "; ".join(memory.injuries[-8:]))
    if memory.knowledge:
        chunks.append("knowledge: " + "; ".join(memory.knowledge[-8:]))
    if memory.relationships:
        chunks.append(
            "relationships: "
            + "; ".join(f"{key}={value}" for key, value in memory.relationships.items())
        )
    return "\n".join(chunks)
