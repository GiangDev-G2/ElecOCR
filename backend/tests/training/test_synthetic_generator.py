"""Unit tests for synthetic electricity meter display crop generation."""

from backend.ai.domain import DecimalStyle, MeterType
from backend.ai.reading import READING_PATTERN
from backend.ai.training.synthetic.generator import SyntheticGenerator


def test_generator_creates_valid_electronic_sample() -> None:
    generator = SyntheticGenerator(seed=123)
    sample = generator.generate_sample(
        split="train",
        meter_type=MeterType.ELECTRONIC,
        decimal_style=DecimalStyle.DOT,
    )

    assert sample.image.mode == "RGB"
    assert sample.image.width > 20
    assert sample.image.height > 15
    assert sample.meter_type == MeterType.ELECTRONIC
    assert sample.decimal_style == DecimalStyle.DOT
    assert isinstance(sample.reading_raw, str)
    assert isinstance(sample.reading_normalized, str)
    assert READING_PATTERN.fullmatch(sample.reading_normalized)
    assert "." in sample.reading_normalized


def test_generator_creates_valid_mechanical_sample_with_red_digit() -> None:
    generator = SyntheticGenerator(seed=456)
    sample = generator.generate_sample(
        split="val",
        meter_type=MeterType.MECHANICAL,
        decimal_style=DecimalStyle.RED_DIGITS,
    )

    assert sample.image.mode == "RGB"
    assert sample.meter_type == MeterType.MECHANICAL
    assert sample.decimal_style == DecimalStyle.RED_DIGITS
    # Target normalized reading must contain the decimal dot separator
    assert "." in sample.reading_normalized
    assert READING_PATTERN.fullmatch(sample.reading_normalized)
    assert sample.metadata["synthetic"] is True


def test_generator_preserves_leading_zeros() -> None:
    generator = SyntheticGenerator(seed=999)
    # Generate multiple samples to check string representations
    for _ in range(15):
        sample = generator.generate_sample()
        assert isinstance(sample.reading_raw, str)
        assert isinstance(sample.reading_normalized, str)
        # Verify it does not convert to numeric float or int
        assert not isinstance(sample.reading_normalized, (int, float))
