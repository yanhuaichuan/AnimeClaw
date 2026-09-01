from __future__ import annotations

from pathlib import Path

from novelvideo.anime.acting_engine import ActingEngine
from novelvideo.anime.anime_pipeline import estimate_cost, export_episode, seed_ten_shot_demo
from novelvideo.anime.anime_prompt_builder import AnimePromptBuilder
from novelvideo.anime.anime_qa import AnimeQA
from novelvideo.anime.camera_engine import MangaCameraEngine
from novelvideo.anime.continuity_engine import ContinuityEngine
from novelvideo.anime.models import AnimeShot, CharacterBible, Dialogue
from novelvideo.anime.store import AnimeStore


def test_ten_shot_demo_keeps_the_same_person(tmp_path: Path) -> None:
    store = AnimeStore(tmp_path)
    bundle = seed_ten_shot_demo(store)

    assert len(bundle.shots) == 10
    assert [shot.title for shot in bundle.shots] == [
        "正面",
        "侧面",
        "跑步",
        "战斗",
        "受伤",
        "哭泣",
        "夜景",
        "近景",
        "全身",
        "回头",
    ]
    bible = store.get_character_bible("su-li")
    assert bible is not None
    assert bible.appearance.hair == "银白长发"
    assert bible.appearance.eyes == "赤红"
    assert "左手红绳" in bible.signature
    for shot in bundle.shots:
        assert "su-li" in shot.characters
        assert "银白长发" in shot.image_prompt
        assert "赤红" in shot.image_prompt
        assert "黑色长裙" in shot.image_prompt
        assert "左手红绳" in shot.image_prompt
        assert "银色耳坠" in shot.image_prompt


def test_continuity_flags_weapon_hand_swap(tmp_path: Path) -> None:
    store = AnimeStore(tmp_path)
    seed_ten_shot_demo(store)
    bible = store.get_character_bible("su-li")
    assert bible is not None
    shots = [
        AnimeShot(
            id="a",
            characters=["su-li"],
            scene_id="ye-yu-gate",
            image_prompt=_identity_blob(bible) + " sword in right hand",
            style_notes=store.load_style().art_style,
        ),
        AnimeShot(
            id="b",
            characters=["su-li"],
            scene_id="ye-yu-gate",
            image_prompt=_identity_blob(bible) + " sword in left hand",
            style_notes=store.load_style().art_style,
        ),
    ]
    issues = ContinuityEngine().check_shots(
        shots,
        {bible.id: bible},
        {item.id: item for item in store.list_scene_bibles()},
        store.load_style(),
    )
    kinds = {item.kind for item in issues}
    assert "weapon_hand" in kinds


def test_prompt_builder_is_layered() -> None:
    from novelvideo.anime.models import CharacterState, SceneBible, StoryWorld
    from novelvideo.anime.style_bible import default_style

    builder = AnimePromptBuilder()
    prompt = builder.build_image_prompt(
        world=StoryWorld(world="九州大陆", era="大荒历 307 年"),
        character=CharacterBible(
            id="su-li",
            name="苏璃",
            appearance={"hair": "银白长发", "eyes": "赤红"},
            costume="黑色长裙",
            signature=["左手红绳"],
        ),
        character_state=CharacterState(
            character_id="su-li",
            episode=1,
            injured=True,
            left_arm="bandaged",
        ),
        scene=SceneBible(id="gate", name="城门", lighting="moonlight"),
        shot=AnimeShot(id="s1"),
        style=default_style(),
    )
    assert "九州大陆" in prompt
    assert "银白长发" in prompt
    assert "bandaged" in prompt
    assert "moonlight" in prompt


def test_acting_engine_turns_dialogue_into_performance() -> None:
    plan = ActingEngine().plan(
        emotion="hurt",
        dialogue=Dialogue(speaker="苏璃", text="你骗我。"),
        pose="turn",
    )
    assert plan.eyes == "avoid"
    assert plan.mouth == "slightly trembling"
    assert plan.pause_sec == 0.6
    assert ActingEngine().voice_emotion(plan).startswith("hurt:")


def test_camera_templates_cover_fight_and_death() -> None:
    engine = MangaCameraEngine()
    fight = engine.recommend("fight")
    assert len(fight) >= 3
    assert any(item.movement == "impact" for item in fight)
    assert engine.plan_for_emotion("surprised").shot_size == "close_up"


def test_export_and_cost_and_qa(tmp_path: Path) -> None:
    store = AnimeStore(tmp_path)
    seed_ten_shot_demo(store)
    payload = export_episode(store, 1)
    assert payload["product"] == "AnimeClaw"
    assert payload["author"] == "yanhuaichuan"
    assert len(payload["shots"]) == 10
    qa = AnimeQA().score(store, 1)
    assert qa.overall >= 70
    cost = estimate_cost(10, "preview")
    assert cost["total"] == 1.6


def _identity_blob(bible: CharacterBible) -> str:
    return (
        f"{bible.appearance.hair} {bible.appearance.eyes} {bible.costume} "
        + " ".join(bible.signature)
        + " "
    )
