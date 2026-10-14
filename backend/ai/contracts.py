"""Protocols at the boundary between orchestration and model adapters."""

from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from backend.ai.domain import OcrPrediction, RecognitionPrediction

ImageArray = NDArray[np.uint8]


class OcrPipeline(Protocol):
    """Minimal interface implemented by a concrete model bundle."""

    @property
    def is_ready(self) -> bool: ...

    @property
    def model_version(self) -> str: ...

    def predict(self, source_image: ImageArray, *, debug: bool) -> OcrPrediction: ...


class ReadingRecognizer(Protocol):
    """Recognize a reading from an already localized RGB display crop."""

    def recognize_reading(self, display_crop: ImageArray) -> RecognitionPrediction: ...
