# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Open plot threads so later episodes cannot forget a planted question."""

from __future__ import annotations

from novelvideo.anime.models import PlotThread
from novelvideo.anime.store import AnimeStore


def open_threads(store: AnimeStore) -> list[PlotThread]:
    return [item for item in store.load_plot_threads() if item.status == "open"]


def upsert_thread(store: AnimeStore, thread: PlotThread) -> list[PlotThread]:
    items = [item for item in store.load_plot_threads() if item.id != thread.id]
    items.append(thread)
    return store.save_plot_threads(items)
