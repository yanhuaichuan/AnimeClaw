# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Emotion + intent + dialogue → acting plan → prompt fragments."""

from __future__ import annotations

from novelvideo.anime.expression_engine import ExpressionEngine
from novelvideo.anime.models import ActingPlan, Dialogue
from novelvideo.anime.pose_engine import PoseEngine

_EYES = {
    "hurt": "avoid",
    "sad": "downcast",
    "angry": "glare",
    "surprised": "wide",
    "embarrassed": "averted",
    "cold": "narrow",
    "determined": "locked on target",
    "fear": "darting",
    "pain": "squeezed shut",
}

_MOUTH = {
    "hurt": "slightly trembling",
    "sad": "trembling",
    "angry": "tight",
    "surprised": "open",
    "embarrassed": "pressed",
    "determined": "set",
    "pain": "gritted",
}

_BODY = {
    "hurt": "turn away",
    "sad": "shoulders drop",
    "angry": "lean forward",
    "surprised": "recoil",
    "embarrassed": "cover face",
    "determined": "step forward",
    "fear": "shrink back",
    "pain": "clutch injury",
    "fight": "combat ready",
}


class ActingEngine:
    def __init__(self) -> None:
        self.expressions = ExpressionEngine()
        self.poses = PoseEngine()

    def plan(
        self,
        *,
        emotion: str = "neutral",
        intent: str = "",
        dialogue: Dialogue | None = None,
        pose: str = "idle",
    ) -> ActingPlan:
        emotion_key = (emotion or "neutral").strip().lower()
        if emotion_key not in _EYES and emotion_key not in self.expressions.list_expressions():
            emotion_key = self.expressions.normalize(emotion)
        intensity = 0.72 if (dialogue and dialogue.text) else 0.5
        if emotion_key in {"angry", "pain", "determined"}:
            intensity = max(intensity, 0.72)
        pause = 0.6 if emotion_key in {"hurt", "sad", "surprised"} else 0.0
        return ActingPlan(
            emotion=emotion_key,
            emotion_intensity=intensity,
            intent=intent or (dialogue.text if dialogue else ""),
            eyes=_EYES.get(emotion_key, "forward"),
            mouth=_MOUTH.get(emotion_key, "closed"),
            body=_BODY.get(emotion_key, "idle"),
            pause_sec=pause,
            expression=self.expressions.normalize("sad" if emotion_key == "hurt" else emotion_key),
            pose=self.poses.normalize(pose),
        )

    def image_fragment(self, acting: ActingPlan) -> str:
        return ", ".join(
            part
            for part in (
                self.expressions.prompt_fragment(acting.expression),
                self.poses.prompt_fragment(acting.pose),
                f"eyes {acting.eyes}" if acting.eyes else "",
                f"mouth {acting.mouth}" if acting.mouth else "",
                acting.body,
            )
            if part
        )

    def voice_emotion(self, acting: ActingPlan) -> str:
        return f"{acting.emotion}:{acting.emotion_intensity:.2f}"

    def motion_fragment(self, acting: ActingPlan) -> str:
        bits = [acting.body, acting.pose.replace("_", " ")]
        if acting.pause_sec:
            bits.append(f"pause {acting.pause_sec:.1f}s")
        return ", ".join(bits)
