from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str


class BridgeRingInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ring_fingerprint: str | None = None
    ring_size: int = 0
    instance_id: str | None = None
    is_member: bool = False
    error: str | None = None


class HealthCheckResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str
    checks: dict[str, str] | None = None
    bridge_ring: BridgeRingInfo | None = None


class SDKClientVersionResponse(BaseModel):
    model: str
    effective_version: str
    minimum_version: str | None
    status: Literal["compatible", "below_minimum", "unknown_model", "version_unavailable"]
