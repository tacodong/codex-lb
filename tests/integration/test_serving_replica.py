from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import Request, WebSocket
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketDenialResponse

import app.main as main_module
from app.core.auth import dependencies as auth
from app.core.config.settings import get_settings
from app.modules.proxy.api import _validate_proxy_api_key_authorization_for_connection

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("kind", ["http", "websocket"])
@pytest.mark.parametrize("authorization", [None, "Bearer invalid-isolated-key"])
def test_keyed_listener_routes_reject_missing_or_invalid_keys(
    app_instance, kind: str, authorization: str | None
) -> None:
    app_instance.state.proxy_api_keys_required = True
    headers = {"Authorization": authorization} if authorization else {}
    with TestClient(app_instance, client=("127.0.0.1", 50000)) as client:
        if kind == "http":
            response = client.post(
                "/backend-api/codex/responses",
                json={"model": "gpt-6.1-sol", "input": "isolated auth check", "stream": True},
                headers=headers,
            )
            assert response.status_code == 401
            assert response.json()["error"]["code"] == "invalid_api_key"
        else:
            with pytest.raises(WebSocketDenialResponse) as denial:
                with client.websocket_connect("/backend-api/codex/responses", headers=headers):
                    pytest.fail("a mandatory-key listener must reject an unauthenticated socket")
            assert denial.value.status_code == 401
            assert denial.value.json()["error"]["code"] == "invalid_api_key"


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["http", "websocket"])
async def test_listener_requires_native_key_without_shared_setting_change(app_instance, monkeypatch, kind: str) -> None:
    settings = SimpleNamespace(api_key_auth_enabled=False)
    monkeypatch.setattr(auth, "get_settings_cache", lambda: SimpleNamespace(get=AsyncMock(return_value=settings)))
    app_instance.state.proxy_api_keys_required = True
    scope = {"type": kind, "method": "POST", "path": "/v1/responses", "headers": [], "app": app_instance}
    connection = Request(scope) if kind == "http" else WebSocket(scope, AsyncMock(), AsyncMock())
    required = AsyncMock(side_effect=auth.ProxyAuthError("Missing API key"))
    monkeypatch.setattr(auth, "validate_required_proxy_api_key_authorization", required)
    with pytest.raises(auth.ProxyAuthError):
        await _validate_proxy_api_key_authorization_for_connection(None, connection)
    required.assert_awaited_once_with(None)
    assert settings.api_key_auth_enabled is False


@pytest.mark.asyncio
@pytest.mark.parametrize("bridge_enabled", [False, True])
async def test_serving_lifespan_leaves_primary_work_and_marker_alone(
    db_setup, monkeypatch, bridge_enabled: bool
) -> None:
    del db_setup
    monkeypatch.setenv("CODEX_LB_HTTP_RESPONSES_SESSION_BRIDGE_ENABLED", str(bridge_enabled).lower())
    monkeypatch.setenv("CODEX_LB_HTTP_RESPONSES_SESSION_BRIDGE_INSTANCE_ID", "isolated-serving-test")
    get_settings.cache_clear()
    owner_guard = Mock()
    monkeypatch.setattr(main_module, "require_sqlite_lifecycle_owner", owner_guard)
    primary_only = {}
    for name in [
        "init_db",
        "ensure_auto_bootstrap_token",
        "_purge_operation_spool_on_startup",
        "_close_db_and_record_clean_shutdown",
    ]:
        spy = AsyncMock()
        primary_only[name] = spy
        monkeypatch.setattr(main_module, name, spy)
    close = AsyncMock(return_value=True)
    monkeypatch.setattr(main_module, "close_db", close)
    schedulers = {}
    for name in vars(main_module):
        if name.startswith("build_") and name.endswith("_scheduler"):
            scheduler = SimpleNamespace(start=AsyncMock(), stop=AsyncMock())
            schedulers[name] = scheduler
            monkeypatch.setattr(main_module, name, Mock(return_value=scheduler))
    app = main_module.create_serving_replica_app()
    async with app.router.lifespan_context(app):
        assert app.state.sqlite_serving_replica is True
        assert app.state.proxy_api_keys_required is False
    owner_guard.assert_called_once()
    for spy in primary_only.values():
        spy.assert_not_awaited()
    for name, scheduler in schedulers.items():
        if name == "build_api_key_last_used_flush_scheduler":
            scheduler.start.assert_awaited_once()
        else:
            scheduler.start.assert_not_awaited()
    close.assert_awaited_once()


@pytest.mark.asyncio
async def test_serving_lifespan_refuses_an_implicit_identity(monkeypatch) -> None:
    monkeypatch.delenv("CODEX_LB_HTTP_RESPONSES_SESSION_BRIDGE_INSTANCE_ID", raising=False)
    get_settings.cache_clear()
    initialize = AsyncMock()
    monkeypatch.setattr(main_module, "init_db", initialize)
    app = main_module.create_serving_replica_app()
    with pytest.raises(RuntimeError, match="explicit bridge instance identity"):
        async with app.router.lifespan_context(app):
            pytest.fail("an implicit replica identity must not become ready")
    initialize.assert_not_awaited()
