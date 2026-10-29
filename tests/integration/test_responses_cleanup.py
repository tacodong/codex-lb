from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from app.core.errors import SYNTHETIC_TRANSPORT_FAILURE_MARKER
from app.core.utils.sse import format_sse_event
from app.modules.proxy.service import ProxyResponseError, ProxyService

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_response_route_finalizes_service_after_transport_failure(async_client, monkeypatch, path: str) -> None:
    finalized = 0
    attempts = 0

    async def failed_stream(self: ProxyService, *args: object, **kwargs: object) -> AsyncIterator[str]:
        nonlocal finalized, attempts
        attempts += 1
        try:
            yield format_sse_event(
                {
                    "type": "response.created",
                    "response": {
                        "id": "resp_cleanup",
                        "object": "response",
                        "status": "in_progress",
                        "model": "gpt-5.4",
                        "output": [],
                    },
                }
            )
            yield format_sse_event(
                {
                    "type": "error",
                    "error": {"code": "upstream_unavailable", "message": "synthetic transport failure"},
                    SYNTHETIC_TRANSPORT_FAILURE_MARKER: True,
                }
            )
        finally:
            finalized += 1

    monkeypatch.setattr(ProxyService, "stream_responses", failed_stream)
    monkeypatch.setattr(ProxyService, "stream_http_responses", failed_stream)

    async def request():
        return await async_client.post(
            path,
            json={"model": "gpt-5.4", "instructions": "synthetic", "input": [], "stream": True},
            headers={"originator": "codex_cli_rs"},
        )

    if path == "/backend-api/codex/responses":
        with pytest.raises(ProxyResponseError) as error:
            await request()
        assert error.value.status_code == 502
        assert error.value.payload["error"]["code"] == "stream_incomplete"
    else:
        response = await request()
        assert response.status_code == 200
        assert "response.created" in response.text
        assert "response.failed" in response.text
    assert finalized == 1
    assert attempts == 1
