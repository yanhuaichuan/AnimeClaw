from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient


def _client(monkeypatch, tmp_path):
    from novelvideo.api.routes import anime

    async def fake_resolve(project: str, user: dict, required_role: str = "viewer"):
        return SimpleNamespace(
            ctx=None,
            username="alice",
            project_name=project,
            project_dir=tmp_path,
            output_dir=str(tmp_path),
            state_dir=str(tmp_path / "state"),
            runtime_dir=str(tmp_path / "runtime"),
        )

    monkeypatch.setattr(anime, "resolve_project_scope", fake_resolve)
    app = FastAPI()
    app.include_router(anime.router, prefix="/api/v1")
    app.dependency_overrides[anime.get_api_user] = lambda: {"username": "alice"}
    return TestClient(app)


def test_anime_catalog_and_ten_shot_demo(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    catalog = client.get("/api/v1/anime/catalog")
    assert catalog.status_code == 200
    assert "close_up" in catalog.json()["data"]["cameras"]

    demo = client.post("/api/v1/anime/projects/demo/demo/ten-shots")
    assert demo.status_code == 200
    shots = demo.json()["data"]["shots"]
    assert len(shots) == 10

    bible = client.get("/api/v1/anime/projects/demo/characters/su-li/bible")
    assert bible.status_code == 200
    assert bible.json()["data"]["appearance"]["hair"] == "银白长发"

    continuity = client.post("/api/v1/anime/projects/demo/episodes/1/continuity/check")
    assert continuity.status_code == 200
    assert isinstance(continuity.json()["data"], list)

    preview = client.get("/api/v1/anime/projects/demo/episodes/1/preview")
    assert preview.status_code == 200
    assert preview.json()["data"]["kind"] == "animatic"
    assert len(preview.json()["data"]["frames"]) == 10

    exported = client.post("/api/v1/anime/projects/demo/episodes/1/export")
    assert exported.status_code == 200
    assert exported.json()["data"]["author"] == "yanhuaichuan"

    qa = client.get("/api/v1/anime/projects/demo/episodes/1/qa")
    assert qa.status_code == 200
    assert qa.json()["data"]["overall"] >= 70


def test_anime_route_order_is_specific_first() -> None:
    from novelvideo.api.routes.anime import router

    paths = [route.path for route in router.routes]
    assert "/anime/projects/{project}/demo/ten-shots" in paths
    assert "/anime/projects/{project}/characters/{character}/bible" in paths
    assert "/anime/projects/{project}/episodes/{episode}/continuity/check" in paths
