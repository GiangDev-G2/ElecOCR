"""Pipeline adapters implementing the OcrPipeline protocol."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
from PIL import Image

from backend.ai.contracts import ImageArray
from backend.ai.domain import DecimalStyle, MeterType, OcrPrediction, OcrStatus
from backend.ai.errors import ModelLoadError, ModelNotReadyError
from backend.ai.reading import normalize_reading

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


class CrnnOcrPipeline:
    """Concrete pipeline adapter using a trained CRNN recognizer model."""

    def __init__(
        self,
        model: CrnnRecognizer,
        model_version: str = "crnn_v1.0",
        target_height: int = 32,
        target_width: int = 160,
        device: Any | None = None,
    ) -> None:
        try:
            import torch
        except ImportError as err:
            raise ModelLoadError("PyTorch is required to run CrnnOcrPipeline.") from err

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
        device: Any | None = None,
    ) -> CrnnOcrPipeline:
        """Load a pipeline directly from a saved .pt checkpoint."""
        try:
            import torch

            from backend.ai.models.crnn import CrnnRecognizer
        except ImportError as err:
            raise ModelLoadError("PyTorch is required to load CrnnOcrPipeline.") from err

        target_device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(checkpoint_path, map_location=target_device, weights_only=False)
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
    def is_ready(self) -> bool:
        return True

    @property
    def model_version(self) -> str:
        return self._model_version

    def _preprocess_crop(self, source_image: ImageArray) -> torch.Tensor:
        """Convert a uint8 HWC RGB array into a normalized BCHW tensor."""
        import torch

        image = Image.fromarray(source_image, mode="RGB")
        original_width, original_height = image.size

        aspect_ratio = original_width / float(max(1, original_height))
        new_width = min(int(self._target_height * aspect_ratio), self._target_width)
        resized = image.resize((new_width, self._target_height), Image.Resampling.BILINEAR)

        padded = Image.new("RGB", (self._target_width, self._target_height), color=(30, 30, 30))
        padded.paste(resized, (0, 0))

        np_arr = np.array(padded, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(np_arr).permute(2, 0, 1).unsqueeze(0)  # [1, 3, H, W]
        return tensor

    def predict(self, source_image: ImageArray, *, debug: bool) -> OcrPrediction:
        del debug
        import torch

        from backend.ai.models.crnn import decode_greedy

        image_tensor = self._preprocess_crop(source_image).to(self._device)

        with torch.inference_mode():
            logits = self._model(image_tensor)
            decoded = decode_greedy(logits)

        if not decoded:
            return OcrPrediction(
                status=OcrStatus.UNREADABLE,
                reading=None,
                raw_reading=None,
                confidence=0.0,
            )

        raw_reading, confidence = decoded[0]
        if not raw_reading:
            return OcrPrediction(
                status=OcrStatus.UNREADABLE,
                reading=None,
                raw_reading="",
                confidence=0.0,
            )

        try:
            normalized = normalize_reading(raw_reading)
            status = OcrStatus.OK if confidence >= 0.70 else OcrStatus.REVIEW_REQUIRED
            decimal_style = DecimalStyle.DOT if "." in normalized else DecimalStyle.NONE
            return OcrPrediction(
                status=status,
                reading=normalized,
                raw_reading=raw_reading,
                confidence=round(confidence, 4),
                meter_type=MeterType.UNKNOWN,
                decimal_style=decimal_style,
            )
        except Exception:
            return OcrPrediction(
                status=OcrStatus.REVIEW_REQUIRED,
                reading=None,
                raw_reading=raw_reading,
                confidence=round(confidence, 4),
                warnings=("Reading validation failed for predicted sequence.",),
            )
