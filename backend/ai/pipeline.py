"""Initial pipeline adapter used until trained model artifacts are available."""

from backend.ai.contracts import ImageArray
from backend.ai.domain import OcrPrediction
from backend.ai.errors import ModelNotReadyError


class UnavailableOcrPipeline:
    """Explicitly reports that no model bundle has been installed yet."""

    def __init__(self, model_version: str = "unavailable") -> None:
        self._model_version = model_version

    @property
    def is_ready(self) -> bool:
        return False

    @property
    def model_version(self) -> str:
        return self._model_version

    def predict(self, source_image: ImageArray, *, debug: bool) -> OcrPrediction:
        del source_image, debug
        raise ModelNotReadyError("No OCR model bundle is currently loaded.")
