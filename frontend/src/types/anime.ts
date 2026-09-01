// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan

export type ProductionMode = "fast" | "balanced" | "quality";
export type LockKey = "character" | "costume" | "scene" | "style" | "camera" | "lighting";

export interface Appearance {
  hair: string;
  eyes: string;
  height: number | null;
  face: string;
  body: string;
  age: string;
}

export interface Personality {
  calm: number;
  aggressive: number;
  notes: string;
}

export interface CharacterBible {
  id: string;
  name: string;
  appearance: Appearance;
  costume: string;
  personality: Personality;
  voice: string;
  expression_sheet: string[];
  pose_sheet: string[];
  body: string;
  relationships: Record<string, string>;
  backstory: string;
  habits: string[];
  combat_style: string;
  signature: string[];
  current_status: Record<string, unknown>;
}

export interface CharacterState {
  character_id: string;
  episode: number;
  injured: boolean;
  left_arm: string;
  right_arm: string;
  emotion: string;
  clothes: string;
  extras: Record<string, unknown>;
}

export interface SceneBible {
  id: string;
  name: string;
  location: string;
  era: string;
  time: string;
  weather: string;
  lighting: string;
  props: string[];
  description: string;
  rules: string[];
}

export interface StyleBible {
  art_style: string;
  line_style: string;
  color_palette: string[];
  lighting: string;
  character_rendering: string;
  background_rendering: string;
  face_style: string;
  eye_style: string;
  shadow_style: string;
  negative_profile: string[];
}

export interface StoryWorld {
  world: string;
  era: string;
  rules: string[];
  factions: string[];
  locations: string[];
  timeline: string[];
  events: string[];
  notes: string;
}

export interface CameraPlan {
  shot_size: string;
  angle: string;
  movement: string;
  template: string;
  notes: string;
}

export interface ActingPlan {
  emotion: string;
  emotion_intensity: number;
  intent: string;
  eyes: string;
  mouth: string;
  body: string;
  pause_sec: number;
  expression: string;
  pose: string;
}

export interface Dialogue {
  speaker: string;
  text: string;
}

export interface AnimeShot {
  id: string;
  title: string;
  characters: string[];
  scene_id: string;
  camera: CameraPlan;
  acting: ActingPlan;
  dialogue?: Dialogue | null;
  image_prompt: string;
  motion_prompt: string;
  lighting: string;
  style_notes: string;
  locks: LockKey[];
  duration_sec: number;
  beat_id: string;
}

export interface AnimeBeat {
  id: string;
  title: string;
  summary: string;
  emotion: string;
  camera: CameraPlan;
  acting: ActingPlan;
  expression: string;
  pose: string;
  motion: string;
  transition: string;
  shot_ids: string[];
}

export interface EpisodeState {
  episode: number;
  title: string;
  mode: ProductionMode;
  character_states: CharacterState[];
  open_threads: string[];
  hook: string;
  cliffhanger: string;
  pacing: string;
}

export interface ContinuityIssue {
  severity: "error" | "warning";
  kind: string;
  character_id: string;
  shot_id: string;
  previous: string;
  current: string;
  fix: string;
}

export interface QAScorecard {
  story: number;
  character: number;
  visual: number;
  audio: number;
  continuity: number;
  overall: number;
  notes: string[];
}

export interface PreviewFrame {
  shot_id: string;
  title: string;
  start: number;
  duration: number;
  dialogue: string;
  camera: string;
  pose: string;
  expression: string;
}

export interface AnimePreview {
  kind: string;
  total_sec: number;
  frames: PreviewFrame[];
  hook: string;
  cliffhanger: string;
}

export interface EpisodeBundle {
  episode: EpisodeState;
  beats: AnimeBeat[];
  shots: AnimeShot[];
  continuity: ContinuityIssue[];
  qa?: QAScorecard | null;
  preview: AnimePreview | Record<string, unknown>;
}

export interface CostEstimate {
  tier: string;
  shots: number;
  image: number;
  video: number;
  voice: number;
  total: number;
  currency: string;
}

export interface AnimeCatalog {
  cameras: string[];
  templates: string[];
  expressions: string[];
  poses: string[];
  costs: Record<string, CostEstimate>;
}

export type AnimePanel =
  | "studio"
  | "world"
  | "characters"
  | "styles"
  | "story"
  | "episodes"
  | "qa";
