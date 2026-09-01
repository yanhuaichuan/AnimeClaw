# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""Anime pipeline adapters: demo seed, animatic preview, episode export, cost."""

from __future__ import annotations

from datetime import datetime, timezone

from novelvideo.anime.acting_engine import ActingEngine
from novelvideo.anime.anime_prompt_builder import AnimePromptBuilder
from novelvideo.anime.anime_qa import AnimeQA
from novelvideo.anime.camera_engine import MangaCameraEngine
from novelvideo.anime.character_state import upsert_character_state
from novelvideo.anime.continuity_engine import ContinuityEngine
from novelvideo.anime.models import (
    AnimeBeat,
    AnimeShot,
    CameraPlan,
    CharacterBible,
    CharacterState,
    CostEstimate,
    Dialogue,
    EpisodeBundle,
    EpisodeState,
    SceneBible,
    StoryWorld,
)
from novelvideo.anime.store import AnimeStore
from novelvideo.anime.style_bible import default_style

DEMO_CHARACTER_ID = "su-li"

DEMO_SHOTS: list[dict] = [
    {"id": "shot-01", "title": "正面", "pose": "stand", "emotion": "determined", "camera": "medium_shot"},
    {"id": "shot-02", "title": "侧面", "pose": "stand", "emotion": "cold", "camera": "medium_shot"},
    {"id": "shot-03", "title": "跑步", "pose": "run", "emotion": "determined", "camera": "full_shot"},
    {"id": "shot-04", "title": "战斗", "pose": "fight", "emotion": "angry", "camera": "full_shot"},
    {"id": "shot-05", "title": "受伤", "pose": "fall", "emotion": "pain", "camera": "close_up"},
    {"id": "shot-06", "title": "哭泣", "pose": "cry", "emotion": "sad", "camera": "close_up"},
    {"id": "shot-07", "title": "夜景", "pose": "stand", "emotion": "cold", "camera": "long_shot"},
    {"id": "shot-08", "title": "近景", "pose": "idle", "emotion": "determined", "camera": "extreme_close_up"},
    {"id": "shot-09", "title": "全身", "pose": "idle", "emotion": "neutral", "camera": "full_shot"},
    {"id": "shot-10", "title": "回头", "pose": "look_back", "emotion": "surprised", "camera": "medium_shot"},
]

COST_TABLE = {
    "draft": CostEstimate(tier="draft", image=0.01, video=0.10, voice=0.01),
    "preview": CostEstimate(tier="preview", image=0.04, video=0.10, voice=0.02),
    "final": CostEstimate(tier="final", image=0.08, video=0.80, voice=0.05),
}


def seed_ten_shot_demo(store: AnimeStore, episode: int = 1) -> EpisodeBundle:
    """The product demo: one character, ten shots, same face / clothes / hair."""
    world = StoryWorld(
        world="九州大陆",
        era="大荒历 307 年",
        rules=["凡人不能直接使用灵力", "妖族可以化形"],
        factions=["天玄宗", "青丘", "魔域"],
        locations=["夜雨城门", "青丘旧街"],
        events=["城门夜袭"],
    )
    store.save_world(world)
    store.save_style(default_style())
    bible = CharacterBible(
        id=DEMO_CHARACTER_ID,
        name="苏璃",
        appearance={
            "hair": "银白长发",
            "eyes": "赤红",
            "height": 165,
            "face": "清冷鹅蛋脸",
            "age": "十八",
        },
        costume="黑色长裙",
        personality={"calm": 0.8, "aggressive": 0.2, "notes": "话少，句短"},
        signature=["左手红绳", "银色耳坠"],
        habits=["左手习惯性按住红绳"],
        combat_style="近身剑术，剑在右手",
        voice="清冷女声",
        expression_sheet=["neutral", "cold", "determined", "pain", "sad"],
        pose_sheet=["idle", "run", "fight", "cry", "look_back"],
    )
    store.save_character_bible(bible)
    scene = SceneBible(
        id="ye-yu-gate",
        name="夜雨城门",
        location="九州 · 夜雨城",
        time="night",
        weather="light rain",
        lighting="moonlight rim, wet stone reflections",
        props=["长剑", "城门灯笼"],
        description="雨夜城门，青石反光，远处魔域火光",
    )
    store.save_scene_bible(scene)

    acting = ActingEngine()
    camera = MangaCameraEngine()
    builder = AnimePromptBuilder()
    style = store.load_style()

    episode_state = EpisodeState(
        episode=episode,
        title="夜雨初见",
        hook="城门灯笼突然灭了一排。",
        cliffhanger="门后，一只赤红的眼睛睁开。",
        pacing="hook",
    )
    upsert_character_state(
        episode_state,
        CharacterState(
            character_id=DEMO_CHARACTER_ID,
            episode=episode,
            injured=True,
            left_arm="bandaged",
            emotion="angry",
            clothes="damaged",
        ),
    )

    shots: list[AnimeShot] = []
    beats: list[AnimeBeat] = []
    for index, spec in enumerate(DEMO_SHOTS, start=1):
        cam = camera.list_presets().get(spec["camera"], camera.plan_for_emotion(spec["emotion"]))
        plan = acting.plan(emotion=spec["emotion"], pose=spec["pose"])
        shot = AnimeShot(
            id=spec["id"],
            title=spec["title"],
            characters=[DEMO_CHARACTER_ID],
            scene_id=scene.id,
            camera=cam if isinstance(cam, CameraPlan) else CameraPlan(),
            acting=plan,
            dialogue=Dialogue(speaker="苏璃", text="你骗我。") if spec["id"] == "shot-06" else None,
            lighting=scene.lighting,
            style_notes=style.art_style,
            locks=["character", "costume", "scene", "style"],
            duration_sec=2.4 if spec["id"] != "shot-05" else 1.8,
            beat_id=f"beat-{index:02d}",
        )
        builder.enrich_shot(
            shot,
            world=world,
            character=bible,
            character_state=episode_state.character_states[0],
            scene=scene,
            style=style,
        )
        shots.append(shot)
        beats.append(
            AnimeBeat(
                id=f"beat-{index:02d}",
                title=spec["title"],
                summary=f"{bible.name} · {spec['title']}",
                emotion=spec["emotion"],
                camera=shot.camera,
                acting=plan,
                expression=plan.expression,
                pose=plan.pose,
                motion=plan.body,
                shot_ids=[shot.id],
            )
        )

    bundle = EpisodeBundle(episode=episode_state, beats=beats, shots=shots)
    bundle.preview = build_preview(bundle)
    store.save_episode(bundle)
    ContinuityEngine().check_episode(store, episode)
    return bundle


def build_preview(bundle: EpisodeBundle) -> dict:
    cursor = 0.0
    frames: list[dict] = []
    for shot in bundle.shots:
        frames.append(
            {
                "shot_id": shot.id,
                "title": shot.title,
                "start": round(cursor, 2),
                "duration": shot.duration_sec,
                "dialogue": shot.dialogue.text if shot.dialogue else "",
                "camera": shot.camera.shot_size,
                "pose": shot.acting.pose,
                "expression": shot.acting.expression,
            }
        )
        cursor += shot.duration_sec
    return {
        "kind": "animatic",
        "total_sec": round(cursor, 2),
        "frames": frames,
        "hook": bundle.episode.hook,
        "cliffhanger": bundle.episode.cliffhanger,
    }


def export_episode(store: AnimeStore, episode: int) -> dict:
    bundle = store.load_episode(episode)
    issues = ContinuityEngine().check_episode(store, episode)
    qa = AnimeQA().score(store, episode)
    payload = {
        "product": "AnimeClaw",
        "author": "yanhuaichuan",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "world": store.load_world().model_dump(),
        "style": store.load_style().model_dump(),
        "characters": [item.model_dump() for item in store.list_character_bibles()],
        "scenes": [item.model_dump() for item in store.list_scene_bibles()],
        "episode": bundle.episode.model_dump(),
        "beats": [item.model_dump() for item in bundle.beats],
        "shots": [item.model_dump() for item in bundle.shots],
        "preview": bundle.preview or build_preview(bundle),
        "continuity": [item.model_dump() for item in issues],
        "qa": qa.model_dump(),
    }
    store.save_export(episode, payload)
    return payload


def estimate_cost(shot_count: int, tier: str = "preview") -> dict:
    unit = COST_TABLE.get(tier, COST_TABLE["preview"])
    return {
        "tier": unit.tier,
        "shots": shot_count,
        "image": round(unit.image * shot_count, 2),
        "video": round(unit.video * shot_count, 2),
        "voice": round(unit.voice * shot_count, 2),
        "total": round((unit.image + unit.video + unit.voice) * shot_count, 2),
        "currency": unit.currency,
    }
