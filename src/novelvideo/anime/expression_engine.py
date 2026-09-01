# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""First-pass expression sheet for AnimeClaw characters."""

from __future__ import annotations

EXPRESSIONS = (
    "neutral",
    "happy",
    "sad",
    "angry",
    "surprised",
    "fear",
    "disgust",
    "embarrassed",
    "cold",
    "tired",
    "pain",
    "determined",
)

_PROMPT = {
    "neutral": "neutral expression, relaxed brows",
    "happy": "soft smile, bright eyes",
    "sad": "downturned brows, glossy eyes",
    "angry": "furrowed brows, clenched jaw",
    "surprised": "wide eyes, raised brows, slightly open mouth",
    "fear": "tense eyes, pale lips",
    "disgust": "wrinkled nose, tight mouth",
    "embarrassed": "blush, averted gaze",
    "cold": "blank stare, closed mouth",
    "tired": "half-lidded eyes, slack expression",
    "pain": "tight eyes, gritted teeth",
    "determined": "sharp gaze, set jaw",
}


class ExpressionEngine:
    def list_expressions(self) -> list[str]:
        return list(EXPRESSIONS)

    def normalize(self, name: str) -> str:
        key = (name or "neutral").strip().lower()
        return key if key in EXPRESSIONS else "neutral"

    def prompt_fragment(self, name: str) -> str:
        return _PROMPT[self.normalize(name)]
