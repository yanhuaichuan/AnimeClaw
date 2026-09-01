# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""First-pass pose vocabulary."""

from __future__ import annotations

POSES = (
    "idle",
    "stand",
    "sit",
    "walk",
    "run",
    "fight",
    "fall",
    "turn",
    "look_back",
    "point",
    "cry",
    "hug",
    "kneel",
    "sleep",
)

_PROMPT = {
    "idle": "relaxed standing idle",
    "stand": "upright standing pose",
    "sit": "seated pose",
    "walk": "walking mid-stride",
    "run": "running, dynamic motion",
    "fight": "combat stance, ready to strike",
    "fall": "falling off balance",
    "turn": "turning the body",
    "look_back": "looking back over the shoulder",
    "point": "pointing forward",
    "cry": "crying, shoulders drawn in",
    "hug": "embracing",
    "kneel": "kneeling",
    "sleep": "sleeping / collapsed rest",
}

_ALIASES = {
    "lookback": "look_back",
    "look-back": "look_back",
}


class PoseEngine:
    def list_poses(self) -> list[str]:
        return list(POSES)

    def normalize(self, name: str) -> str:
        key = (name or "idle").strip().lower().replace(" ", "_")
        key = _ALIASES.get(key, key)
        return key if key in POSES else "idle"

    def prompt_fragment(self, name: str) -> str:
        return _PROMPT[self.normalize(name)]
