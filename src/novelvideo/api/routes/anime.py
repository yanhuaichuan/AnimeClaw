# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
"""AnimeClaw REST surface — /api/v1/anime. File-backed, no new database."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from novelvideo.anime.acting_engine import ActingEngine
from novelvideo.anime.anime_director import AnimeDirector
from novelvideo.anime.anime_pipeline import estimate_cost, export_episode, seed_ten_shot_demo
from novelvideo.anime.anime_prompt_builder import AnimePromptBuilder
from novelvideo.anime.anime_qa import AnimeQA
from novelvideo.anime.camera_engine import MangaCameraEngine
from novelvideo.anime.character_bible import upsert_bible
from novelvideo.anime.character_state import find_character_state, upsert_character_state
from novelvideo.anime.continuity_engine import ContinuityEngine
from novelvideo.anime.expression_engine import ExpressionEngine
from novelvideo.anime.models import (
    AnimeShot,
    CharacterState,
    Dialogue,
    EpisodeState,
    StoryWorld,
    StyleBible,
)
from novelvideo.anime.pose_engine import PoseEngine
from novelvideo.anime.scene_bible import upsert_scene
from novelvideo.anime.store import AnimeStore
from novelvideo.anime.style_bible import default_style
from novelvideo.api.auth import get_api_user
from novelvideo.api.deps import resolve_project_scope

router = APIRouter(prefix="/anime", tags=["anime"])


async def _store(project: str, user: dict, *, required_role: str = "viewer") -> AnimeStore:
    resolved = await resolve_project_scope(project, user, required_role=required_role)
    return AnimeStore(resolved.state_dir)


@router.get("/catalog")
async def anime_catalog(user: dict = Depends(get_api_user)) -> dict[str, Any]:
    _ = user
    return {
        "ok": True,
        "data": {
            "cameras": list(MangaCameraEngine().list_presets()),
            "templates": MangaCameraEngine().list_templates(),
            "expressions": ExpressionEngine().list_expressions(),
            "poses": PoseEngine().list_poses(),
            "costs": {
                "draft": estimate_cost(1, "draft"),
                "preview": estimate_cost(1, "preview"),
                "final": estimate_cost(1, "final"),
            },
        },
    }


@router.get("/projects/{project}/world")
async def get_world(project: str, user: dict = Depends(get_api_user)) -> dict[str, Any]:
    store = await _store(project, user)
    return {"ok": True, "data": store.load_world().model_dump()}


@router.put("/projects/{project}/world")
async def put_world(
    project: str,
    body: dict[str, Any],
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    world = store.save_world(StoryWorld.model_validate(body))
    return {"ok": True, "data": world.model_dump()}


@router.get("/projects/{project}/style")
async def get_style(project: str, user: dict = Depends(get_api_user)) -> dict[str, Any]:
    store = await _store(project, user)
    style = store.load_style()
    if not style.art_style:
        style = default_style()
    return {"ok": True, "data": style.model_dump()}


@router.put("/projects/{project}/style")
async def put_style(
    project: str,
    body: dict[str, Any],
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    style = store.save_style(StyleBible.model_validate(body))
    return {"ok": True, "data": style.model_dump()}


@router.get("/projects/{project}/characters")
async def list_characters(project: str, user: dict = Depends(get_api_user)) -> dict[str, Any]:
    store = await _store(project, user)
    return {"ok": True, "data": [item.model_dump() for item in store.list_character_bibles()]}


@router.get("/projects/{project}/characters/{character}/bible")
async def get_character_bible(
    project: str,
    character: str,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user)
    bible = store.get_character_bible(character)
    if bible is None:
        raise HTTPException(status_code=404, detail="Character bible not found")
    return {"ok": True, "data": bible.model_dump()}


@router.put("/projects/{project}/characters/{character}/bible")
async def put_character_bible(
    project: str,
    character: str,
    body: dict[str, Any],
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    body = {**body, "id": body.get("id") or character}
    bible = upsert_bible(store, body)
    return {"ok": True, "data": bible.model_dump()}


@router.get("/projects/{project}/scenes")
async def list_scenes(project: str, user: dict = Depends(get_api_user)) -> dict[str, Any]:
    store = await _store(project, user)
    return {"ok": True, "data": [item.model_dump() for item in store.list_scene_bibles()]}


@router.put("/projects/{project}/scenes/{scene}")
async def put_scene(
    project: str,
    scene: str,
    body: dict[str, Any],
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    body = {**body, "id": body.get("id") or scene}
    bible = upsert_scene(store, body)
    return {"ok": True, "data": bible.model_dump()}


@router.get("/projects/{project}/episodes/{episode}/state")
async def get_episode_state(
    project: str,
    episode: int,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user)
    return {"ok": True, "data": store.load_episode(episode).model_dump()}


@router.put("/projects/{project}/episodes/{episode}/state")
async def put_episode_state(
    project: str,
    episode: int,
    body: dict[str, Any],
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    bundle = store.load_episode(episode)
    incoming = EpisodeState.model_validate({**body, "episode": episode})
    bundle.episode = incoming
    store.save_episode(bundle)
    return {"ok": True, "data": bundle.model_dump()}


@router.put("/projects/{project}/episodes/{episode}/characters/{character}/state")
async def put_character_state(
    project: str,
    episode: int,
    character: str,
    body: dict[str, Any],
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    bundle = store.load_episode(episode)
    state = CharacterState.model_validate({**body, "character_id": character, "episode": episode})
    upsert_character_state(bundle.episode, state)
    store.save_episode(bundle)
    return {"ok": True, "data": state.model_dump()}


@router.get("/projects/{project}/episodes/{episode}/shots")
async def list_shots(
    project: str,
    episode: int,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user)
    bundle = store.load_episode(episode)
    return {"ok": True, "data": [item.model_dump() for item in bundle.shots]}


@router.put("/projects/{project}/episodes/{episode}/shots/{shot}")
async def put_shot(
    project: str,
    episode: int,
    shot: str,
    body: dict[str, Any],
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    bundle = store.load_episode(episode)
    incoming = AnimeShot.model_validate({**body, "id": shot})
    shots = [item for item in bundle.shots if item.id != shot]
    shots.append(incoming)
    shots.sort(key=lambda item: item.id)
    store.save_shots(episode, shots)
    return {"ok": True, "data": incoming.model_dump()}


@router.post("/projects/{project}/episodes/{episode}/shots/{shot}/acting")
async def post_acting(
    project: str,
    episode: int,
    shot: str,
    body: dict[str, Any],
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    bundle = store.load_episode(episode)
    current = next((item for item in bundle.shots if item.id == shot), None)
    if current is None:
        raise HTTPException(status_code=404, detail="Shot not found")
    dialogue = None
    if body.get("dialogue"):
        dialogue = Dialogue.model_validate(body["dialogue"])
        current.dialogue = dialogue
    current.acting = ActingEngine().plan(
        emotion=str(body.get("emotion") or current.acting.emotion),
        intent=str(body.get("intent") or ""),
        dialogue=dialogue or current.dialogue,
        pose=str(body.get("pose") or current.acting.pose),
    )
    store.save_shots(episode, bundle.shots)
    return {"ok": True, "data": current.model_dump()}


@router.post("/projects/{project}/episodes/{episode}/shots/{shot}/prompt")
async def post_prompt(
    project: str,
    episode: int,
    shot: str,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    bundle = store.load_episode(episode)
    current = next((item for item in bundle.shots if item.id == shot), None)
    if current is None:
        raise HTTPException(status_code=404, detail="Shot not found")
    character_id = current.characters[0] if current.characters else ""
    bible = store.get_character_bible(character_id) if character_id else None
    if bible is None:
        raise HTTPException(status_code=400, detail="Shot has no Character Bible")
    scene = store.get_scene_bible(current.scene_id) if current.scene_id else None
    state = find_character_state(bundle.episode, character_id)
    AnimePromptBuilder().enrich_shot(
        current,
        world=store.load_world(),
        character=bible,
        character_state=state,
        scene=scene,
        style=store.load_style() or default_style(),
    )
    store.save_shots(episode, bundle.shots)
    return {"ok": True, "data": current.model_dump()}


@router.post("/projects/{project}/episodes/{episode}/continuity/check")
async def post_continuity(
    project: str,
    episode: int,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    issues = ContinuityEngine().check_episode(store, episode)
    return {"ok": True, "data": [item.model_dump() for item in issues]}


@router.post("/projects/{project}/episodes/{episode}/director")
async def post_director(
    project: str,
    episode: int,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user)
    return {"ok": True, "data": AnimeDirector().recommend(store, episode)}


@router.post("/projects/{project}/episodes/{episode}/shots/{shot}/repair")
async def post_repair(
    project: str,
    episode: int,
    shot: str,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    repaired = AnimeDirector().repair(store, episode, shot)
    if repaired is None:
        raise HTTPException(status_code=404, detail="Shot not found")
    return {"ok": True, "data": repaired.model_dump()}


@router.get("/projects/{project}/episodes/{episode}/qa")
async def get_qa(
    project: str,
    episode: int,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user)
    return {"ok": True, "data": AnimeQA().score(store, episode).model_dump()}


@router.get("/projects/{project}/episodes/{episode}/preview")
async def get_preview(
    project: str,
    episode: int,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    from novelvideo.anime.anime_pipeline import build_preview

    store = await _store(project, user)
    bundle = store.load_episode(episode)
    preview = bundle.preview or build_preview(bundle)
    return {"ok": True, "data": preview}


@router.post("/projects/{project}/episodes/{episode}/export")
async def post_export(
    project: str,
    episode: int,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    return {"ok": True, "data": export_episode(store, episode)}


@router.get("/projects/{project}/episodes/{episode}/cost")
async def get_cost(
    project: str,
    episode: int,
    tier: str = "preview",
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user)
    bundle = store.load_episode(episode)
    return {"ok": True, "data": estimate_cost(len(bundle.shots) or 10, tier)}


@router.post("/projects/{project}/demo/ten-shots")
async def post_ten_shot_demo(
    project: str,
    user: dict = Depends(get_api_user),
) -> dict[str, Any]:
    store = await _store(project, user, required_role="editor")
    bundle = seed_ten_shot_demo(store, episode=1)
    return {"ok": True, "data": bundle.model_dump()}
