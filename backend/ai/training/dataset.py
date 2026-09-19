"""PyTorch Dataset and Collate function for OCR meter crops."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

from backend.ai.models.crnn import encode_reading


class MeterCropDataset(Dataset[tuple[torch.Tensor, list[int], str]]):
    """Dataset loading cropped meter display images and normalized reading labels."""

    def __init__(
        self,
        manifest_path: Path,
        base_dir: Path | None = None,
        target_height: int = 32,
        target_width: int = 160,
    ) -> None:
        super().__init__()
        self.manifest_path = manifest_path
        self.base_dir = base_dir or manifest_path.parent
        self.target_height = target_height
        self.target_width = target_width

        self.entries: list[dict[str, str]] = []
        with manifest_path.open("r", encoding="utf-8") as file:
            for line in file:
                line_str = line.strip()
                if not line_str:
                    continue
                record = json.loads(line_str)
                if record.get("readability") == "readable" and record.get("reading_normalized"):
                    self.entries.append(
                        {
                            "relative_path": record["relative_path"],
                            "reading_normalized": str(record["reading_normalized"]),
                        }
                    )

    def __len__(self) -> int:
        return len(self.entries)

    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Resize image to target height while keeping aspect ratio, pad to target width."""
        image_rgb = image.convert("RGB")
        original_width, original_height = image_rgb.size

        # Resize keeping aspect ratio
        aspect_ratio = original_width / float(max(1, original_height))
        new_width = int(self.target_height * aspect_ratio)
        new_width = min(new_width, self.target_width)

        resized = image_rgb.resize((new_width, self.target_height), Image.Resampling.BILINEAR)

        # Pad with gray background to target_width
        padded_image = Image.new("RGB", (self.target_width, self.target_height), color=(30, 30, 30))
        padded_image.paste(resized, (0, 0))

        # Convert to float tensor BCHW normalized to [0, 1]
        np_arr = np.array(padded_image, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(np_arr).permute(2, 0, 1)  # [3, H, W]
        return tensor

    def __getitem__(self, index: int) -> tuple[torch.Tensor, list[int], str]:
        entry = self.entries[index]
        image_path = self.base_dir / entry["relative_path"]
        with Image.open(image_path) as img:
            image_tensor = self._preprocess_image(img)

        reading_str = entry["reading_normalized"]
        token_indices = encode_reading(reading_str)
        return image_tensor, token_indices, reading_str


def collate_ocr_batch(
    batch: list[tuple[torch.Tensor, list[int], str]],
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, list[str]]:
    """Collate function assembling tensors for CTCLoss.

    Returns:
        images: FloatTensor of shape [B, 3, H, W]
        targets: 1D LongTensor of concatenated target token IDs
        input_lengths: 1D LongTensor containing the model output time steps T
        target_lengths: 1D LongTensor containing the label length for each item
        ground_truth_readings: List of ground-truth reading strings
    """
    images = torch.stack([item[0] for item in batch], dim=0)
    ground_truth_readings = [item[2] for item in batch]

    # Target sequence lengths and concatenated 1D targets
    target_lengths_list = [len(item[1]) for item in batch]
    target_lengths = torch.tensor(target_lengths_list, dtype=torch.long)

    flat_targets: list[int] = []
    for item in batch:
        flat_targets.extend(item[1])
    targets = torch.tensor(flat_targets, dtype=torch.long)

    # For CRNN with 4 horizontal poolings: T = W // 4
    width = images.shape[3]
    time_steps = width // 4
    input_lengths = torch.full((len(batch),), time_steps, dtype=torch.long)

    return images, targets, input_lengths, target_lengths, ground_truth_readings
