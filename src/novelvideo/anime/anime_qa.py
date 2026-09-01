# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Episode quality scorecard after continuity + bible coverage."""

from __future__ import annotations

from novelvideo.anime.continuity_engine import ContinuityEngine
from novelvideo.anime.models import QAScorecard
from novelvideo.anime.store import AnimeStore


class AnimeQA:
    def __init__(self) -> None:
        self.continuity = ContinuityEngine()

    def score(self, store: AnimeStore, episode: int) -> QAScorecard:
        bundle = store.load_episode(episode)
        issues = self.continuity.check_episode(store, episode)
        errors = [item for item in issues if item.severity == "error"]
        warnings = [item for item in issues if item.severity == "warning"]
        shot_count = max(len(bundle.shots), 1)
        continuity = max(0, 100 - 8 * len(errors) - 3 * len(warnings))
        character = 92 if store.list_character_bibles() else 40
        if any(item.kind in {"hair", "eyes", "costume", "signature"} for item in errors):
            character = max(40, character - 12)
        visual = 88 if store.load_style().art_style else 50
        story = 80
        if bundle.episode.hook:
            story += 8
        if bundle.episode.cliffhanger:
            story += 7
        story = min(story, 99)
        audio = 90 if any(shot.dialogue and shot.dialogue.text for shot in bundle.shots) else 70
        notes = [f"{item.kind} @ {item.shot_id or 'episode'}" for item in issues[:12]]
        if shot_count >= 10:
            notes.append("10-shot continuity demo coverage met")
        overall = round(
            (story + character + visual + audio + continuity) / 5
        )
        return QAScorecard(
            story=story,
            character=character,
            visual=visual,
            audio=audio,
            continuity=continuity,
            overall=overall,
            notes=notes,
        )
