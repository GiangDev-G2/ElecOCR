"""Safe image decoding and canonicalization at the API boundary."""

from io import BytesIO
from warnings import catch_warnings, simplefilter

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageOps, UnidentifiedImageError

from backend.ai.errors import ImageTooLargeError, InvalidImageError, UnsupportedImageError

SUPPORTED_MEDIA_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})


def decode_and_canonicalize_image(
    image_bytes: bytes,
    *,
    media_type: str | None,
    max_image_side_px: int,
) -> NDArray[np.uint8]:
    """Decode bytes to an EXIF-oriented RGB HWC uint8 array."""
    if media_type not in SUPPORTED_MEDIA_TYPES:
        raise UnsupportedImageError(f"Unsupported media type: {media_type!r}")

    try:
        with catch_warnings():
            simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(image_bytes)) as decoded_image:
                decoded_image.load()
                oriented_image = ImageOps.exif_transpose(decoded_image)
                if max(oriented_image.size) > max_image_side_px:
                    raise ImageTooLargeError(
                        "Decoded image dimensions exceed the configured limit."
                    )
                rgb_image = oriented_image.convert("RGB")
                source_image = np.asarray(rgb_image, dtype=np.uint8)
    except ImageTooLargeError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise ImageTooLargeError("The image exceeds safe pixel limits.") from error
    except (OSError, UnidentifiedImageError, ValueError) as error:
        raise InvalidImageError("The uploaded file cannot be decoded as an image.") from error

    if source_image.ndim != 3 or source_image.shape[2] != 3:
        raise InvalidImageError("The decoded image does not satisfy the RGB contract.")
    return source_image
