"""Public HTTP response schemas."""

from pydantic import BaseModel, ConfigDict, Field

from backend.ai.domain import DecimalStyle, MeterType, OcrStatus


class StrictSchema(BaseModel):
    """Base schema rejecting undocumented response fields."""

    model_config = ConfigDict(extra="forbid")


class HealthResponse(StrictSchema):
    status: str


class ReadinessResponse(StrictSchema):
    status: str
    model_version: str


class VersionResponse(StrictSchema):
    api_version: str
    app_version: str
    model_version: str


class OcrLatency(StrictSchema):
    total: float = Field(ge=0)
    canonicalization: float = Field(ge=0)
    localization: float = Field(ge=0)
    recognition: float = Field(ge=0)
    fallback: float = Field(ge=0)
    decision: float = Field(ge=0)


class OcrResponse(StrictSchema):
    request_id: str
    status: OcrStatus
    reading: str | None
    raw_reading: str | None
    confidence: float | None = Field(default=None, ge=0, le=1)
    meter_type: MeterType
    decimal_style: DecimalStyle
    display_polygon: list[tuple[int, int]]
    alternatives: list[str]
    warnings: list[str]
    latency_ms: OcrLatency
    model_version: str


class ApiError(StrictSchema):
    code: str
    message: str


class ApiErrorResponse(StrictSchema):
    request_id: str
    status: OcrStatus = OcrStatus.ERROR
    error: ApiError
