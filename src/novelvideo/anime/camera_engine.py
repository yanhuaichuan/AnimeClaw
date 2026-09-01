# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Manga camera language — presets so creators do not need film school."""

from __future__ import annotations

from novelvideo.anime.models import CameraPlan

CAMERA_PRESETS: dict[str, CameraPlan] = {
    "extreme_close_up": CameraPlan(shot_size="extreme_close_up", angle="eye_level", movement="static"),
    "close_up": CameraPlan(shot_size="close_up", angle="eye_level", movement="static"),
    "medium_shot": CameraPlan(shot_size="medium_shot", angle="eye_level", movement="static"),
    "full_shot": CameraPlan(shot_size="full_shot", angle="eye_level", movement="static"),
    "long_shot": CameraPlan(shot_size="long_shot", angle="eye_level", movement="static"),
    "over_shoulder": CameraPlan(shot_size="over_shoulder", angle="eye_level", movement="static"),
    "pov": CameraPlan(shot_size="pov", angle="eye_level", movement="static"),
    "low_angle": CameraPlan(shot_size="medium_shot", angle="low_angle", movement="static"),
    "high_angle": CameraPlan(shot_size="medium_shot", angle="high_angle", movement="static"),
    "dutch_angle": CameraPlan(shot_size="medium_shot", angle="dutch", movement="static"),
    "tracking": CameraPlan(shot_size="full_shot", angle="eye_level", movement="tracking"),
    "pan": CameraPlan(shot_size="medium_shot", angle="eye_level", movement="pan"),
    "zoom": CameraPlan(shot_size="close_up", angle="eye_level", movement="zoom"),
    "whip_pan": CameraPlan(shot_size="medium_shot", angle="eye_level", movement="whip_pan"),
    "impact_frame": CameraPlan(shot_size="close_up", angle="dutch", movement="impact"),
}

SHOT_TEMPLATES: dict[str, list[CameraPlan]] = {
    "dialogue": [CAMERA_PRESETS["medium_shot"], CAMERA_PRESETS["over_shoulder"]],
    "reaction": [
        CameraPlan(shot_size="close_up", angle="eye_level", movement="zoom", template="reaction"),
        CAMERA_PRESETS["impact_frame"],
    ],
    "romance": [CAMERA_PRESETS["close_up"], CAMERA_PRESETS["over_shoulder"]],
    "fight": [
        CAMERA_PRESETS["long_shot"],
        CAMERA_PRESETS["close_up"],
        CameraPlan(shot_size="full_shot", angle="low_angle", movement="tracking", template="fight"),
        CAMERA_PRESETS["impact_frame"],
    ],
    "death": [
        CameraPlan(shot_size="close_up", angle="eye_level", movement="slow_push_in", template="death"),
        CAMERA_PRESETS["close_up"],
    ],
    "reveal": [CAMERA_PRESETS["long_shot"], CAMERA_PRESETS["close_up"]],
    "flashback": [CameraPlan(shot_size="medium_shot", angle="high_angle", movement="static", template="flashback")],
    "comedy": [CAMERA_PRESETS["medium_shot"], CAMERA_PRESETS["extreme_close_up"]],
    "chase": [CAMERA_PRESETS["tracking"], CAMERA_PRESETS["whip_pan"]],
    "power_up": [CAMERA_PRESETS["low_angle"], CAMERA_PRESETS["impact_frame"]],
}


class MangaCameraEngine:
    def list_presets(self) -> dict[str, CameraPlan]:
        return dict(CAMERA_PRESETS)

    def list_templates(self) -> list[str]:
        return sorted(SHOT_TEMPLATES)

    def recommend(self, template: str) -> list[CameraPlan]:
        plans = SHOT_TEMPLATES.get(template, SHOT_TEMPLATES["dialogue"])
        return [plan.model_copy(update={"template": template}) for plan in plans]

    def plan_for_emotion(self, emotion: str) -> CameraPlan:
        mapping = {
            "surprised": CAMERA_PRESETS["close_up"].model_copy(
                update={"movement": "zoom", "template": "reaction"}
            ),
            "angry": CAMERA_PRESETS["low_angle"].model_copy(update={"template": "fight"}),
            "sad": CAMERA_PRESETS["close_up"].model_copy(update={"movement": "slow_push_in"}),
            "pain": CAMERA_PRESETS["extreme_close_up"].model_copy(update={"template": "reaction"}),
            "determined": CAMERA_PRESETS["low_angle"].model_copy(update={"template": "power_up"}),
        }
        return mapping.get(emotion, CAMERA_PRESETS["medium_shot"]).model_copy()

    def prompt_fragment(self, camera: CameraPlan) -> str:
        parts = [
            camera.shot_size.replace("_", " "),
            camera.angle.replace("_", " "),
            camera.movement.replace("_", " "),
        ]
        if camera.notes:
            parts.append(camera.notes)
        return ", ".join(part for part in parts if part)
