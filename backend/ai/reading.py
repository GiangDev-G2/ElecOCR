"""Deterministic reading normalization and validation."""

import re

from backend.ai.errors import InvalidReadingError

READING_PATTERN = re.compile(r"^[0-9]+(?:\.[0-9]+)?$")


def normalize_reading(raw_reading: str) -> str:
    """Normalize the decimal separator without changing any digit."""
    normalized_reading = raw_reading.strip().replace(",", ".")
    if not READING_PATTERN.fullmatch(normalized_reading):
        raise InvalidReadingError("The recognized reading has an invalid format.")
    return normalized_reading
