import pytest

from backend.ai.errors import InvalidReadingError
from backend.ai.reading import normalize_reading


def test_normalize_reading_with_leading_zeros_preserves_zeros() -> None:
    assert normalize_reading("00012,3") == "00012.3"


@pytest.mark.parametrize("raw_reading", ["", "12..3", "12A3", ".123", "123."])
def test_normalize_reading_with_invalid_format_raises_error(raw_reading: str) -> None:
    with pytest.raises(InvalidReadingError):
        normalize_reading(raw_reading)
