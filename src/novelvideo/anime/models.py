# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""AnimeClaw domain models. Stored as JSON beside DramaClaw project state."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


ProductionMode = Literal["fast", "balanced", "quality"]
CostTier = Literal["draft", "preview", "final"]
LockKey = Literal["character", "costume", "scene", "style", "camera", "lighting"]


class Appearance(BaseModel):
    hair: str = ""
    eyes: str = ""
    height: float | None = None
    face: str = ""
    body: str = ""
    age: str = ""


class Personality(BaseModel):
    calm: float = 0.5
    aggressive: float = 0.5
    notes: str = ""


class CharacterBible(BaseModel):
    """Who this person is — identity that must survive across episodes."""

    id: str
    name: str
    appearance: Appearance = Field(default_factory=Appearance)
    costume: str = ""
    personality: Personality = Field(default_factory=Personality)
    voice: str = ""
    expression_sheet: list[str] = Field(default_factory=list)
    pose_sheet: list[str] = Field(default_factory=list)
    body: str = ""
    relationships: dict[str, str] = Field(default_factory=dict)
    backstory: str = ""
    habits: list[str] = Field(default_factory=list)
    combat_style: str = ""
    signature: list[str] = Field(default_factory=list)
    current_status: dict[str, Any] = Field(default_factory=dict)


class CharacterState(BaseModel):
    """Who this person is *in this episode*."""

    character_id: str
    episode: int
    injured: bool = False
    left_arm: str = ""
    right_arm: str = ""
    emotion: str = "neutral"
    clothes: str = ""
    extras: dict[str, Any] = Field(default_factory=dict)


class SceneBible(BaseModel):
    id: str
    name: str
    location: str = ""
    era: str = ""
    time: str = ""
    weather: str = ""
    lighting: str = ""
    props: list[str] = Field(default_factory=list)
    description: str = ""
    rules: list[str] = Field(default_factory=list)


class StyleBible(BaseModel):
    art_style: str = "cel-shaded anime, clean linework"
    line_style: str = "crisp ink lines"
    color_palette: list[str] = Field(default_factory=list)
    lighting: str = "soft rim light"
    character_rendering: str = "consistent face, large expressive eyes"
    background_rendering: str = "painterly but readable"
    face_style: str = "anime face, stable bone structure"
    eye_style: str = "detailed iris, catchlight"
    shadow_style: str = "cel shadow, two-tone"
    negative_profile: list[str] = Field(default_factory=list)


class StoryWorld(BaseModel):
    world: str = ""
    era: str = ""
    rules: list[str] = Field(default_factory=list)
    factions: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    timeline: list[str] = Field(default_factory=list)
    events: list[str] = Field(default_factory=list)
    notes: str = ""


class CameraPlan(BaseModel):
    shot_size: str = "medium_shot"
    angle: str = "eye_level"
    movement: str = "static"
    template: str = "dialogue"
    notes: str = ""


class ActingPlan(BaseModel):
    emotion: str = "neutral"
    emotion_intensity: float = 0.5
    intent: str = ""
    eyes: str = "forward"
    mouth: str = "closed"
    body: str = "idle"
    pause_sec: float = 0.0
    expression: str = "neutral"
    pose: str = "idle"


class Dialogue(BaseModel):
    speaker: str = ""
    text: str = ""


class AnimeShot(BaseModel):
    id: str
    title: str = ""
    characters: list[str] = Field(default_factory=list)
    scene_id: str = ""
    camera: CameraPlan = Field(default_factory=CameraPlan)
    acting: ActingPlan = Field(default_factory=ActingPlan)
    dialogue: Dialogue | None = None
    image_prompt: str = ""
    motion_prompt: str = ""
    lighting: str = ""
    style_notes: str = ""
    locks: list[LockKey] = Field(default_factory=list)
    duration_sec: float = 2.4
    beat_id: str = ""


class AnimeBeat(BaseModel):
    id: str
    title: str = ""
    summary: str = ""
    emotion: str = "neutral"
    camera: CameraPlan = Field(default_factory=CameraPlan)
    acting: ActingPlan = Field(default_factory=ActingPlan)
    expression: str = "neutral"
    pose: str = "idle"
    motion: str = ""
    transition: str = "cut"
    shot_ids: list[str] = Field(default_factory=list)


class EpisodeState(BaseModel):
    episode: int
    title: str = ""
    mode: ProductionMode = "balanced"
    character_states: list[CharacterState] = Field(default_factory=list)
    open_threads: list[str] = Field(default_factory=list)
    hook: str = ""
    cliffhanger: str = ""
    pacing: str = "hook"


class ContinuityIssue(BaseModel):
    severity: Literal["error", "warning"] = "error"
    kind: str
    character_id: str = ""
    shot_id: str = ""
    previous: str = ""
    current: str = ""
    fix: str = ""


class PlotThread(BaseModel):
    id: str
    status: Literal["open", "resolved"] = "open"
    question: str
    first_introduced: int = 1
    expected_reveal: int | None = None


class StoryMemory(BaseModel):
    characters: list[str] = Field(default_factory=list)
    relationships: dict[str, str] = Field(default_factory=dict)
    events: list[str] = Field(default_factory=list)
    secrets: list[str] = Field(default_factory=list)
    items: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    promises: list[str] = Field(default_factory=list)
    injuries: list[str] = Field(default_factory=list)
    deaths: list[str] = Field(default_factory=list)
    knowledge: list[str] = Field(default_factory=list)


class QAScorecard(BaseModel):
    story: int = 0
    character: int = 0
    visual: int = 0
    audio: int = 0
    continuity: int = 0
    overall: int = 0
    notes: list[str] = Field(default_factory=list)


class CostEstimate(BaseModel):
    tier: CostTier
    image: float
    video: float
    voice: float
    currency: str = "USD"


class EpisodeBundle(BaseModel):
    episode: EpisodeState
    beats: list[AnimeBeat] = Field(default_factory=list)
    shots: list[AnimeShot] = Field(default_factory=list)
    continuity: list[ContinuityIssue] = Field(default_factory=list)
    qa: QAScorecard | None = None
    preview: dict[str, Any] = Field(default_factory=dict)
