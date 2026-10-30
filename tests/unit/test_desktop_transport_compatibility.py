from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from app.core.clients import proxy_websocket
from app.core.clients.native_egress import NativeEgressTransportError, NativeEgressWebSocket
from app.core.openai.requests import ResponsesRequest


@pytest.mark.asyncio
async def test_native_socket_receive_preserves_account_neutral_terminal_failure() -> None:
    native = AsyncMock(spec=NativeEgressWebSocket)
    native.receive.side_effect = NativeEgressTransportError("private native socket failure", failure_phase="transport")
    message = await proxy_websocket.NativeUpstreamWebSocket(native).receive()
    assert message.kind == "error"
    assert proxy_websocket.is_account_neutral_websocket_error_code(message.error_code)
    assert message.error is not None and "private" not in message.error
    native.receive.assert_awaited_once()


@pytest.mark.asyncio
async def test_native_socket_send_preserves_safe_reason_and_health_classification() -> None:
    native = AsyncMock(spec=NativeEgressWebSocket)
    native.send_text.side_effect = NativeEgressTransportError(
        "private socket error", failure_phase="transport", failure_reason="broken_pipe"
    )
    with pytest.raises(proxy_websocket.UpstreamWebSocketTransportError) as caught:
        await proxy_websocket.NativeUpstreamWebSocket(native).send_text("synthetic")
    assert str(caught.value) == "Upstream websocket send failed (native phase=transport reason=broken_pipe)"
    assert proxy_websocket.is_account_neutral_websocket_error_code(caught.value.error_code)
    native.send_text.assert_awaited_once_with("synthetic")


def test_desktop_output_include_is_preserved_without_allowing_unknown_values() -> None:
    payload = {
        "model": "gpt-6.1-sol",
        "instructions": "synthetic",
        "input": [],
        "include": ["reasoning.encrypted_content", "output.encrypted_content"],
    }
    assert ResponsesRequest.model_validate(payload).model_dump()["include"] == payload["include"]
    with pytest.raises(ValidationError):
        ResponsesRequest.model_validate({**payload, "include": ["unknown.include"]})
