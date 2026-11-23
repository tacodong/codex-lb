from __future__ import annotations

from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

from app.modules.health import api as health

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("effective", "minimum", "present", "expected"),
    [
        ("0.159.2", "0.166.0", True, "below_minimum"),
        ("0.171.0", "0.166.0", True, "compatible"),
        ("0.10.0", "0.9.0", True, "compatible"),
        ("0.171.0", None, True, "version_unavailable"),
        ("0.171.0", None, False, "unknown_model"),
    ],
)
async def test_internal_sdk_version_uses_the_serving_process_state(
    app_instance,
    monkeypatch,
    effective,
    minimum,
    present,
    expected,
):
    monkeypatch.setattr(
        health,
        "get_codex_version_cache",
        lambda: SimpleNamespace(
            cached_version_or_default=lambda: effective,
        ),
    )
    models = {"gpt-6.2-sol": SimpleNamespace(minimal_client_version=minimum)} if present else {}
    monkeypatch.setattr(
        health,
        "get_model_registry",
        lambda: SimpleNamespace(
            get_models_with_fallback=lambda: models,
        ),
    )
    transport = ASGITransport(app=app_instance, client=("127.0.0.1", 50001))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/internal/sdk-client-version", params={"model": "gpt-6.2-sol"})
    assert response.status_code == 200
    assert response.json() == {
        "model": "gpt-6.2-sol",
        "effective_version": effective,
        "minimum_version": minimum,
        "status": expected,
    }


@pytest.mark.asyncio
async def test_internal_sdk_version_denies_remote_requests(app_instance):
    transport = ASGITransport(app=app_instance, client=("192.0.2.4", 50001))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/internal/sdk-client-version", params={"model": "gpt-6.2-sol"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_health_endpoint_unchanged(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_live_endpoint(async_client):
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_ready_endpoint_db_ok(async_client):
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["checks"] == {"database": "ok"}


@pytest.mark.asyncio
async def test_health_startup_endpoint(async_client):
    response = await async_client.get("/health/startup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
