"""Domain values shared by the OCR application layer."""

from dataclasses import dataclass
from enum import StrEnum


class OcrStatus(StrEnum):
    """Closed set of business-level OCR outcomes."""

    OK = "ok"
    REVIEW_REQUIRED = "review_required"
    UNREADABLE = "unreadable"
    ERROR = "error"


class MeterType(StrEnum):
    """Supported electricity meter display families."""

    MECHANICAL = "mechanical"
    ELECTRONIC = "electronic"
    UNKNOWN = "unknown"


class DecimalStyle(StrEnum):
    """Observed visual representation of the fractional part."""

    DOT = "dot"
    COMMA = "comma"
    RED_DIGITS = "red_digits"
    NONE = "none"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class OcrPrediction:
    """Framework-independent OCR result returned by a pipeline adapter."""

    status: OcrStatus
    reading: str | None
    raw_reading: str | None
    confidence: float | None
    meter_type: MeterType = MeterType.UNKNOWN
    decimal_style: DecimalStyle = DecimalStyle.UNKNOWN
    warnings: tuple[str, ...] = ()
