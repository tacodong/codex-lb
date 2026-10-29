from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import cast

import pytest

from app.core.errors import SYNTHETIC_TRANSPORT_FAILURE_MARKER
from app.core.types import JsonValue
from app.core.utils.sse import format_sse_event
from app.modules.proxy import api
from app.modules.proxy.service import ProxyResponseError


@pytest.mark.asyncio
@pytest.mark.parametrize("native", [False, True])
async def test_transport_error_closes_service_stream_before_return(native: bool) -> None:
    closed = asyncio.Event()

    async def upstream() -> AsyncGenerator[str]:
        try:
            yield format_sse_event(
                {
                    "type": "error",
                    "error": {"code": "upstream_unavailable", "message": "synthetic"},
                    SYNTHETIC_TRANSPORT_FAILURE_MARKER: True,
                }
            )
        finally:
            closed.set()

    source = upstream()
    errors = api._stream_response_error_events(
        source, owns_reservation=False, reservation=None, preserve_native_failure_lifecycle=native
    )
    normalized = api._normalize_public_responses_stream(errors, preserve_native_failure_lifecycle=native)
    try:
        if native:
            with pytest.raises(ProxyResponseError) as error:
                async for _ in normalized:
                    pass
            assert error.value.status_code == 502
            assert error.value.payload["error"]["code"] == "stream_incomplete"
        else:
            async for _ in normalized:
                pass
        assert closed.is_set()
    finally:
        await source.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize("adapter", ["public", "reasoning", "error"])
async def test_early_close_reaches_owned_upstream(adapter: str) -> None:
    closed = asyncio.Event()

    async def upstream() -> AsyncGenerator[str]:
        try:
            event: dict[str, JsonValue] = {"type": "response.output_text.delta", "delta": "synthetic"}
            yield format_sse_event(event)
            await asyncio.Event().wait()
        finally:
            closed.set()

    source = upstream()
    if adapter == "public":
        stream = api._normalize_public_responses_stream(source, enforce_openai_sdk_contract=False)
    elif adapter == "reasoning":
        stream = api._normalize_reasoning_summary_stream(source)
    else:
        stream = api._stream_response_error_events(source, owns_reservation=False, reservation=None)
    try:
        await anext(stream)
        await cast(AsyncGenerator[str], stream).aclose()
        assert closed.is_set()
    finally:
        await source.aclose()


@pytest.mark.asyncio
async def test_cancelled_iteration_closes_service_stream_and_preserves_cancellation() -> None:
    started = asyncio.Event()
    closed = asyncio.Event()

    async def upstream() -> AsyncGenerator[str]:
        try:
            started.set()
            await asyncio.Event().wait()
            yield "unreachable"
        finally:
            closed.set()

    source = upstream()
    stream = api._normalize_public_responses_stream(source)
    task = asyncio.ensure_future(anext(stream))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert closed.is_set()
