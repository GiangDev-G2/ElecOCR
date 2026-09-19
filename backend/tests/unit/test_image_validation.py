from io import BytesIO

import numpy as np
import pytest
from PIL import Image

from backend.ai.errors import InvalidImageError, UnsupportedImageError
from backend.ai.image_validation import decode_and_canonicalize_image


def _png_bytes() -> bytes:
    image = Image.new("RGBA", (4, 3), color=(10, 20, 30, 128))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_decode_image_with_rgba_returns_rgb_uint8_array() -> None:
    source_image = decode_and_canonicalize_image(
        _png_bytes(),
        media_type="image/png",
        max_image_side_px=100,
    )

    assert source_image.shape == (3, 4, 3)
    assert source_image.dtype == np.uint8


def test_decode_image_with_unsupported_media_type_raises_error() -> None:
    with pytest.raises(UnsupportedImageError):
        decode_and_canonicalize_image(
            _png_bytes(),
            media_type="image/gif",
            max_image_side_px=100,
        )


def test_decode_image_with_invalid_bytes_raises_error() -> None:
    with pytest.raises(InvalidImageError):
        decode_and_canonicalize_image(
            b"not-an-image",
            media_type="image/png",
            max_image_side_px=100,
        )
