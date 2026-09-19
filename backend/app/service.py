"""Application service orchestrating validation and OCR inference."""

from backend.ai.contracts import OcrPipeline
from backend.ai.domain import OcrPrediction
from backend.ai.errors import ImageTooLargeError, ModelNotReadyError
from backend.ai.image_validation import decode_and_canonicalize_image
from backend.app.settings import Settings


class OcrService:
    """Orchestrate one OCR request without depending on FastAPI objects."""

    def __init__(self, *, pipeline: OcrPipeline, settings: Settings) -> None:
        self._pipeline = pipeline
        self._settings = settings

    @property
    def is_ready(self) -> bool:
        return self._pipeline.is_ready

    @property
    def model_version(self) -> str:
        return self._pipeline.model_version

    def recognize(
        self,
        image_bytes: bytes,
        *,
        media_type: str | None,
        debug: bool,
    ) -> OcrPrediction:
        if len(image_bytes) > self._settings.max_image_bytes:
            raise ImageTooLargeError("The uploaded file exceeds the configured byte limit.")

        source_image = decode_and_canonicalize_image(
            image_bytes,
            media_type=media_type,
            max_image_side_px=self._settings.max_image_side_px,
        )
        if not self._pipeline.is_ready:
            raise ModelNotReadyError("No OCR model bundle is currently loaded.")
        return self._pipeline.predict(source_image, debug=debug)
