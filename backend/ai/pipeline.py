"""Pipeline adapters implementing the OcrPipeline protocol."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

from backend.ai.contracts import ImageArray
from backend.ai.domain import OcrPrediction, RecognitionPrediction
from backend.ai.errors import ModelLoadError, ModelNotReadyError

if TYPE_CHECKING:
    import torch

    from backend.ai.models.crnn import CrnnRecognizer


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


class CrnnCropRecognizer:
    """CRNN adapter that recognizes an already localized display crop."""

    def __init__(
        self,
        model: CrnnRecognizer,
        model_version: str = "crnn_v1.0",
        target_height: int = 32,
        target_width: int = 160,
        device: torch.device | str | None = None,
    ) -> None:
        try:
            import torch
        except ImportError as err:
            raise ModelLoadError("PyTorch is required to run CrnnCropRecognizer.") from err

        self._model = model
        self._model_version = model_version
        self._target_height = target_height
        self._target_width = target_width
        self._device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model.to(self._device)
        self._model.eval()

    @classmethod
    def from_checkpoint(
        cls,
        checkpoint_path: Path,
        device: torch.device | str | None = None,
    ) -> CrnnCropRecognizer:
        """Load a crop recognizer directly from a saved checkpoint."""
        try:
            import torch

            from backend.ai.models.crnn import CrnnRecognizer
        except ImportError as err:
            raise ModelLoadError("PyTorch is required to load CrnnCropRecognizer.") from err

        target_device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(checkpoint_path, map_location=target_device, weights_only=True)
        model = CrnnRecognizer(in_channels=3)
        model.load_state_dict(checkpoint["model_state_dict"])
        target_height = int(checkpoint.get("target_height", 32))
        target_width = int(checkpoint.get("target_width", 160))
        version = f"crnn_epoch_{checkpoint.get('epoch', 'unknown')}"
        return cls(
            model=model,
            model_version=version,
            target_height=target_height,
            target_width=target_width,
            device=target_device,
        )

    @property
    def model_version(self) -> str:
        return self._model_version

    def _normalize_recognizer_input(self, display_crop: ImageArray) -> torch.Tensor:
        """Convert a uint8 HWC RGB array into a normalized BCHW tensor."""
        import torch

        image = Image.fromarray(display_crop, mode="RGB")
        original_width, original_height = image.size

        aspect_ratio = original_width / float(max(1, original_height))
        new_width = min(int(self._target_height * aspect_ratio), self._target_width)
        resized = image.resize((new_width, self._target_height), Image.Resampling.BILINEAR)

        padded = Image.new("RGB", (self._target_width, self._target_height), color=(30, 30, 30))
        padded.paste(resized, (0, 0))

        normalized_image_array = np.array(padded, dtype=np.float32) / 255.0
        normalized_image_batch = (
            torch.from_numpy(normalized_image_array).permute(2, 0, 1).unsqueeze(0)
        )
        return normalized_image_batch

    def recognize_reading(self, display_crop: ImageArray) -> RecognitionPrediction:
        """Recognize one RGB display crop without making an OCR status decision."""
        import torch

        from backend.ai.models.crnn import decode_greedy

        normalized_image_batch = self._normalize_recognizer_input(display_crop).to(self._device)

        with torch.inference_mode():
            character_logits = self._model(normalized_image_batch)
            decoded_readings = decode_greedy(character_logits)

        if not decoded_readings:
            return RecognitionPrediction(predicted_reading="", recognition_confidence=0.0)

        predicted_reading, recognition_confidence = decoded_readings[0]
        return RecognitionPrediction(
            predicted_reading=predicted_reading,
            recognition_confidence=round(recognition_confidence, 4),
        )
