"""Synthetic crop generator for electricity meter digits with varied styles."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from backend.ai.domain import DecimalStyle, MeterType

SEGMENT_MAP: dict[str, tuple[int, ...]] = {
    "0": (1, 1, 1, 1, 1, 1, 0),
    "1": (0, 1, 1, 0, 0, 0, 0),
    "2": (1, 1, 0, 1, 1, 0, 1),
    "3": (1, 1, 1, 1, 0, 0, 1),
    "4": (0, 1, 1, 0, 0, 1, 1),
    "5": (1, 0, 1, 1, 0, 1, 1),
    "6": (1, 0, 1, 1, 1, 1, 1),
    "7": (1, 1, 1, 0, 0, 0, 0),
    "8": (1, 1, 1, 1, 1, 1, 1),
    "9": (1, 1, 1, 1, 0, 1, 1),
}


@dataclass(frozen=True, slots=True)
class SyntheticSample:
    """A generated synthetic meter image and its associated metadata."""

    image: Image.Image
    image_id: str
    reading_raw: str
    reading_normalized: str
    meter_type: MeterType
    decimal_style: DecimalStyle
    metadata: dict[str, Any]


class SyntheticGenerator:
    """Generates synthetic cropped display meter images."""

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)

    def _draw_seven_segment_digit(
        self,
        draw: ImageDraw.ImageDraw,
        x: float,
        y: float,
        width: float,
        height: float,
        digit: str,
        active_color: tuple[int, int, int],
        ghost_color: tuple[int, int, int],
        draw_dot: bool = False,
    ) -> None:
        """Draw a single 7-segment digit with active and faint inactive segments."""
        segment_state = SEGMENT_MAP.get(digit, (0, 0, 0, 0, 0, 0, 0))
        half_height = height / 2.0
        thickness = max(2.0, width * 0.16)
        margin = thickness * 0.4

        # 7 segments geometry: (a, b, c, d, e, f, g)
        segments = [
            # a: top horizontal
            [
                (x + margin + thickness, y),
                (x + width - margin - thickness, y),
                (x + width - margin - thickness * 1.4, y + thickness),
                (x + margin + thickness * 1.4, y + thickness),
            ],
            # b: top-right vertical
            [
                (x + width - thickness, y + margin + thickness),
                (x + width, y + margin + thickness * 1.4),
                (x + width, y + half_height - margin * 0.5),
                (x + width - thickness, y + half_height - margin * 0.5),
            ],
            # c: bottom-right vertical
            [
                (x + width - thickness, y + half_height + margin * 0.5),
                (x + width, y + half_height + margin * 0.5),
                (x + width, y + height - margin - thickness * 1.4),
                (x + width - thickness, y + height - margin - thickness),
            ],
            # d: bottom horizontal
            [
                (x + margin + thickness * 1.4, y + height - thickness),
                (x + width - margin - thickness * 1.4, y + height - thickness),
                (x + width - margin - thickness, y + height),
                (x + margin + thickness, y + height),
            ],
            # e: bottom-left vertical
            [
                (x, y + half_height + margin * 0.5),
                (x + thickness, y + half_height + margin * 0.5),
                (x + thickness, y + height - margin - thickness),
                (x, y + height - margin - thickness * 1.4),
            ],
            # f: top-left vertical
            [
                (x, y + margin + thickness * 1.4),
                (x + thickness, y + margin + thickness),
                (x + thickness, y + half_height - margin * 0.5),
                (x, y + half_height - margin * 0.5),
            ],
            # g: middle horizontal
            [
                (x + margin + thickness * 1.2, y + half_height - thickness * 0.5),
                (x + width - margin - thickness * 1.2, y + half_height - thickness * 0.5),
                (x + width - margin - thickness * 1.5, y + half_height + thickness * 0.5),
                (x + margin + thickness * 1.5, y + half_height + thickness * 0.5),
            ],
        ]

        for is_active, poly in zip(segment_state, segments, strict=False):
            color = active_color if is_active else ghost_color
            draw.polygon(poly, fill=color)

        if draw_dot:
            dot_radius = thickness * 0.9
            dot_x = x + width + margin
            dot_y = y + height - dot_radius
            draw.ellipse(
                [
                    (dot_x, dot_y - dot_radius),
                    (dot_x + dot_radius * 2, dot_y + dot_radius),
                ],
                fill=active_color,
            )

    def _render_electronic(
        self,
        integer_part: str,
        decimal_part: str | None,
        decimal_style: DecimalStyle,
    ) -> Image.Image:
        """Render an LCD/electronic 7-segment meter display crop."""
        digit_count = len(integer_part) + (len(decimal_part) if decimal_part else 0)
        digit_width = self._rng.randint(18, 26)
        digit_height = int(digit_width * self._rng.uniform(1.8, 2.3))
        spacing = self._rng.randint(4, 7)
        dot_width = 8 if decimal_part else 0
        padding_x = self._rng.randint(8, 16)
        padding_y = self._rng.randint(6, 12)

        image_width = (
            padding_x * 2 + digit_count * digit_width + (digit_count - 1) * spacing + dot_width
        )
        image_height = padding_y * 2 + digit_height

        # Background LCD hues (greenish-gray or neutral gray)
        bg_brightness = self._rng.randint(160, 210)
        bg_color = (
            bg_brightness - self._rng.randint(0, 10),
            bg_brightness + self._rng.randint(0, 8),
            bg_brightness - self._rng.randint(5, 15),
        )
        active_color = (
            self._rng.randint(20, 50),
            self._rng.randint(25, 55),
            self._rng.randint(20, 45),
        )
        ghost_color = (
            min(255, bg_color[0] - 25),
            min(255, bg_color[1] - 25),
            min(255, bg_color[2] - 25),
        )

        image = Image.new("RGB", (image_width, image_height), color=bg_color)
        draw = ImageDraw.Draw(image)

        # Draw outer subtle border
        draw.rectangle(
            [(1, 1), (image_width - 2, image_height - 2)],
            outline=(max(0, bg_color[0] - 40), max(0, bg_color[1] - 40), max(0, bg_color[2] - 40)),
            width=1,
        )

        current_x = float(padding_x)
        current_y = float(padding_y)

        # Draw integer part
        for idx, digit in enumerate(integer_part):
            has_dot_after = (
                decimal_part is not None
                and idx == len(integer_part) - 1
                and decimal_style in (DecimalStyle.DOT, DecimalStyle.COMMA)
            )
            self._draw_seven_segment_digit(
                draw,
                current_x,
                current_y,
                float(digit_width),
                float(digit_height),
                digit,
                active_color,
                ghost_color,
                draw_dot=has_dot_after,
            )
            current_x += digit_width + spacing
            if has_dot_after:
                current_x += dot_width

        # Draw decimal part
        if decimal_part:
            for digit in decimal_part:
                self._draw_seven_segment_digit(
                    draw,
                    current_x,
                    current_y,
                    float(digit_width),
                    float(digit_height),
                    digit,
                    active_color,
                    ghost_color,
                    draw_dot=False,
                )
                current_x += digit_width + spacing

        return image

    def _render_mechanical(
        self,
        integer_part: str,
        decimal_part: str | None,
        decimal_style: DecimalStyle,
    ) -> Image.Image:
        """Render a mechanical odometer/drum meter display crop."""
        digit_count = len(integer_part) + (len(decimal_part) if decimal_part else 0)
        wheel_width = self._rng.randint(22, 30)
        wheel_height = int(wheel_width * self._rng.uniform(1.7, 2.1))
        padding_x = self._rng.randint(6, 12)
        padding_y = self._rng.randint(4, 8)
        border_width = 2

        image_width = padding_x * 2 + digit_count * wheel_width + (digit_count - 1) * border_width
        image_height = padding_y * 2 + wheel_height

        image = Image.new("RGB", (image_width, image_height), color=(30, 30, 30))
        draw = ImageDraw.Draw(image)

        full_digits = integer_part + (decimal_part if decimal_part else "")
        decimal_start_idx = len(integer_part) if decimal_part else -1

        current_x = padding_x
        for idx, digit in enumerate(full_digits):
            is_decimal_wheel = idx >= decimal_start_idx and decimal_start_idx != -1
            is_red_style = is_decimal_wheel and decimal_style == DecimalStyle.RED_DIGITS

            if is_red_style:
                # Red background wheel with white text
                bg_color = (
                    self._rng.randint(180, 225),
                    self._rng.randint(20, 45),
                    self._rng.randint(20, 45),
                )
                text_color = (
                    self._rng.randint(235, 255),
                    self._rng.randint(235, 255),
                    self._rng.randint(235, 255),
                )
            else:
                # Standard wheel: dark background with white digit, or reverse
                is_black_wheel = True
                if is_black_wheel:
                    bg_color = (
                        self._rng.randint(15, 35),
                        self._rng.randint(15, 35),
                        self._rng.randint(15, 35),
                    )
                    text_color = (
                        self._rng.randint(230, 255),
                        self._rng.randint(230, 255),
                        self._rng.randint(230, 255),
                    )
                else:
                    bg_color = (
                        self._rng.randint(220, 245),
                        self._rng.randint(220, 245),
                        self._rng.randint(220, 245),
                    )
                    text_color = (
                        self._rng.randint(10, 30),
                        self._rng.randint(10, 30),
                        self._rng.randint(10, 30),
                    )

            # Draw wheel box
            wheel_box = [
                (current_x, padding_y),
                (current_x + wheel_width, padding_y + wheel_height),
            ]
            draw.rectangle(wheel_box, fill=bg_color, outline=(70, 70, 70), width=1)

            # Draw top and bottom cylinder shadow gradients
            shadow_height = int(wheel_height * 0.22)
            draw.rectangle(
                [(current_x, padding_y), (current_x + wheel_width, padding_y + shadow_height)],
                fill=(max(0, bg_color[0] - 40), max(0, bg_color[1] - 40), max(0, bg_color[2] - 40)),
            )
            draw.rectangle(
                [
                    (current_x, padding_y + wheel_height - shadow_height),
                    (current_x + wheel_width, padding_y + wheel_height),
                ],
                fill=(max(0, bg_color[0] - 40), max(0, bg_color[1] - 40), max(0, bg_color[2] - 40)),
            )

            # Draw digit (using clean block lines or PIL text)
            self._draw_drum_digit(
                draw,
                current_x + wheel_width * 0.18,
                padding_y + wheel_height * 0.15,
                wheel_width * 0.64,
                wheel_height * 0.7,
                digit,
                text_color,
            )

            # Draw decimal separator comma or dot between wheels if specified
            if (
                idx == len(integer_part) - 1
                and decimal_part
                and decimal_style in (DecimalStyle.COMMA, DecimalStyle.DOT)
            ):
                sep_x = current_x + wheel_width + border_width / 2.0
                sep_y = padding_y + wheel_height * 0.8
                draw.ellipse(
                    [(sep_x - 1.5, sep_y - 1.5), (sep_x + 1.5, sep_y + 1.5)],
                    fill=(200, 200, 200),
                )

            current_x += wheel_width + border_width

        return image

    def _draw_drum_digit(
        self,
        draw: ImageDraw.ImageDraw,
        x: float,
        y: float,
        width: float,
        height: float,
        digit: str,
        color: tuple[int, int, int],
    ) -> None:
        """Draw an odometer drum digit with thick legible strokes."""
        # Simple geometric stroke representation of 0-9 to be independent of OS fonts
        stroke_width = max(2, int(width * 0.2))
        pad = stroke_width / 2.0

        if digit == "0":
            draw.rounded_rectangle(
                [(x + pad, y + pad), (x + width - pad, y + height - pad)],
                radius=int(width * 0.3),
                outline=color,
                width=stroke_width,
            )
        elif digit == "1":
            draw.line(
                [(x + width * 0.55, y + pad), (x + width * 0.55, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + width * 0.3, y + height * 0.25), (x + width * 0.55, y + pad)],
                fill=color,
                width=stroke_width,
            )
        elif digit == "2":
            draw.line(
                [(x + pad, y + pad), (x + width - pad, y + pad)], fill=color, width=stroke_width
            )
            draw.line(
                [(x + width - pad, y + pad), (x + width - pad, y + height * 0.5)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + width - pad, y + height * 0.5), (x + pad, y + height * 0.5)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + pad, y + height * 0.5), (x + pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + pad, y + height - pad), (x + width - pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
        elif digit == "3":
            draw.line(
                [(x + pad, y + pad), (x + width - pad, y + pad)], fill=color, width=stroke_width
            )
            draw.line(
                [(x + width - pad, y + pad), (x + width - pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + pad, y + height * 0.5), (x + width - pad, y + height * 0.5)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + pad, y + height - pad), (x + width - pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
        elif digit == "4":
            draw.line(
                [(x + pad, y + pad), (x + pad, y + height * 0.5)], fill=color, width=stroke_width
            )
            draw.line(
                [(x + pad, y + height * 0.5), (x + width - pad, y + height * 0.5)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + width - pad, y + pad), (x + width - pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
        elif digit == "5":
            draw.line(
                [(x + width - pad, y + pad), (x + pad, y + pad)], fill=color, width=stroke_width
            )
            draw.line(
                [(x + pad, y + pad), (x + pad, y + height * 0.5)], fill=color, width=stroke_width
            )
            draw.line(
                [(x + pad, y + height * 0.5), (x + width - pad, y + height * 0.5)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + width - pad, y + height * 0.5), (x + width - pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + width - pad, y + height - pad), (x + pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
        elif digit == "6":
            draw.line(
                [(x + width - pad, y + pad), (x + pad, y + pad)], fill=color, width=stroke_width
            )
            draw.line(
                [(x + pad, y + pad), (x + pad, y + height - pad)], fill=color, width=stroke_width
            )
            draw.line(
                [(x + pad, y + height * 0.5), (x + width - pad, y + height * 0.5)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + width - pad, y + height * 0.5), (x + width - pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + width - pad, y + height - pad), (x + pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
        elif digit == "7":
            draw.line(
                [(x + pad, y + pad), (x + width - pad, y + pad)], fill=color, width=stroke_width
            )
            draw.line(
                [(x + width - pad, y + pad), (x + width * 0.45, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
        elif digit == "8":
            draw.rounded_rectangle(
                [(x + pad, y + pad), (x + width - pad, y + height * 0.5)],
                radius=int(width * 0.2),
                outline=color,
                width=stroke_width,
            )
            draw.rounded_rectangle(
                [(x + pad, y + height * 0.5), (x + width - pad, y + height - pad)],
                radius=int(width * 0.2),
                outline=color,
                width=stroke_width,
            )
        elif digit == "9":
            draw.line(
                [(x + pad, y + pad), (x + width - pad, y + pad)], fill=color, width=stroke_width
            )
            draw.line(
                [(x + pad, y + pad), (x + pad, y + height * 0.5)], fill=color, width=stroke_width
            )
            draw.line(
                [(x + pad, y + height * 0.5), (x + width - pad, y + height * 0.5)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + width - pad, y + pad), (x + width - pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )
            draw.line(
                [(x + pad, y + height - pad), (x + width - pad, y + height - pad)],
                fill=color,
                width=stroke_width,
            )

    def _apply_augmentations(self, image: Image.Image) -> Image.Image:
        """Apply safe augmentations: subtle blur, slight noise, small angle rotation."""
        # Slight rotation (-2 to +2 degrees)
        angle = self._rng.uniform(-2.0, 2.0)
        augmented = image.rotate(
            angle, resample=Image.Resampling.BILINEAR, expand=False, fillcolor=(30, 30, 30)
        )

        # Random subtle blur
        if self._rng.random() < 0.3:
            augmented = augmented.filter(
                ImageFilter.GaussianBlur(radius=self._rng.uniform(0.3, 0.7))
            )

        # Random noise
        if self._rng.random() < 0.4:
            arr = np.array(augmented, dtype=np.int16)
            noise = np.random.normal(0, self._rng.uniform(2.0, 6.0), arr.shape).astype(np.int16)
            arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
            augmented = Image.fromarray(arr)

        return augmented

    def generate_sample(
        self,
        *,
        split: str = "train",
        meter_type: MeterType | None = None,
        decimal_style: DecimalStyle | None = None,
    ) -> SyntheticSample:
        """Generate one synthetic reading sample."""
        chosen_meter_type = meter_type or self._rng.choice(
            [MeterType.ELECTRONIC, MeterType.MECHANICAL]
        )

        # Generate reading string: 4-6 integer digits with leading zeros possible
        integer_len = self._rng.randint(4, 5)
        # Preserve leading zeros
        integer_value = "".join(str(self._rng.randint(0, 9)) for _ in range(integer_len))

        # Decide decimal part
        if decimal_style is None:
            if chosen_meter_type == MeterType.MECHANICAL:
                chosen_decimal_style = self._rng.choice(
                    [
                        DecimalStyle.RED_DIGITS,
                        DecimalStyle.COMMA,
                        DecimalStyle.DOT,
                        DecimalStyle.NONE,
                    ]
                )
            else:
                chosen_decimal_style = self._rng.choice(
                    [
                        DecimalStyle.DOT,
                        DecimalStyle.COMMA,
                        DecimalStyle.NONE,
                    ]
                )
        else:
            chosen_decimal_style = decimal_style

        if chosen_decimal_style != DecimalStyle.NONE:
            decimal_part: str | None = str(self._rng.randint(0, 9))
            if chosen_decimal_style == DecimalStyle.COMMA:
                reading_raw = f"{integer_value},{decimal_part}"
            elif chosen_decimal_style == DecimalStyle.RED_DIGITS:
                reading_raw = f"{integer_value}{decimal_part}"
            else:
                reading_raw = f"{integer_value}.{decimal_part}"
            reading_normalized = f"{integer_value}.{decimal_part}"
        else:
            decimal_part = None
            reading_raw = integer_value
            reading_normalized = integer_value

        # Render display
        if chosen_meter_type == MeterType.ELECTRONIC:
            base_image = self._render_electronic(integer_value, decimal_part, chosen_decimal_style)
        else:
            base_image = self._render_mechanical(integer_value, decimal_part, chosen_decimal_style)

        augmented_image = self._apply_augmentations(base_image)

        # Generate deterministic image ID from content
        image_bytes = augmented_image.tobytes()
        image_id = hashlib.sha256(image_bytes).hexdigest()[:16]

        metadata: dict[str, Any] = {
            "image_id": image_id,
            "source": "synthetic_generator",
            "source_version": "v1.0",
            "license_id": "internal",
            "split": split,
            "meter_type": chosen_meter_type.value,
            "readability": "readable",
            "reading_raw": reading_raw,
            "reading_normalized": reading_normalized,
            "decimal_style": chosen_decimal_style.value,
            "synthetic": True,
        }

        return SyntheticSample(
            image=augmented_image,
            image_id=image_id,
            reading_raw=reading_raw,
            reading_normalized=reading_normalized,
            meter_type=chosen_meter_type,
            decimal_style=chosen_decimal_style,
            metadata=metadata,
        )
