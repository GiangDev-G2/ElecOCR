"""CRNN model architecture and CTC decoding for meter reading recognition."""

from __future__ import annotations

from typing import cast

import torch
import torch.nn as nn

CHARSET = "0123456789."
BLANK_INDEX = 0
CHAR_TO_INDEX: dict[str, int] = {char: idx + 1 for idx, char in enumerate(CHARSET)}
INDEX_TO_CHAR: dict[int, str] = {idx + 1: char for idx, char in enumerate(CHARSET)}
NUM_CLASSES = len(CHARSET) + 1  # 11 characters + 1 blank


def encode_reading(text: str) -> list[int]:
    """Encode a normalized reading string into character token indices."""
    return [CHAR_TO_INDEX[char] for char in text if char in CHAR_TO_INDEX]


def decode_token_indices(indices: list[int]) -> str:
    """Decode token indices back into a string ignoring blank tokens."""
    return "".join(INDEX_TO_CHAR[idx] for idx in indices if idx in INDEX_TO_CHAR)


class CrnnRecognizer(nn.Module):
    """Convolutional Recurrent Neural Network for sequence recognition with CTC."""

    def __init__(
        self,
        in_channels: int = 3,
        num_classes: int = NUM_CLASSES,
        hidden_size: int = 256,
    ) -> None:
        super().__init__()

        # CNN Feature Extractor
        self.cnn = nn.Sequential(
            # Stage 1: [B, 3, 32, W] -> [B, 64, 16, W/2]
            nn.Conv2d(in_channels, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # Stage 2: [B, 64, 16, W/2] -> [B, 128, 8, W/4]
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # Stage 3: [B, 128, 8, W/4] -> [B, 256, 4, W/4]
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 1), stride=(2, 1)),
            # Stage 4: [B, 256, 4, W/4] -> [B, 512, 2, W/4]
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 1), stride=(2, 1)),
            # Stage 5: [B, 512, 2, W/4] -> [B, 512, 1, W/4]
            nn.Conv2d(512, 512, kernel_size=(2, 1), stride=1, padding=0),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
        )

        # 2-layer Bidirectional LSTM
        self.rnn = nn.LSTM(
            input_size=512,
            hidden_size=hidden_size,
            num_layers=2,
            bidirectional=True,
            batch_first=False,
        )

        # Output projection
        self.classifier = nn.Linear(hidden_size * 2, num_classes)

    def forward(self, image_batch: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            image_batch: Float tensor of shape [B, 3, 32, W] in range [0, 1].

        Returns:
            Logits tensor of shape [T, B, num_classes] where T = W / 4.
        """
        features = self.cnn(image_batch)  # [B, 512, 1, T]
        features = features.squeeze(2)  # [B, 512, T]
        features = features.permute(2, 0, 1)  # [T, B, 512]

        rnn_out, _ = self.rnn(features)  # [T, B, hidden_size * 2]
        logits = self.classifier(rnn_out)  # [T, B, num_classes]
        return cast(torch.Tensor, logits)


def decode_greedy(
    logits: torch.Tensor,
) -> list[tuple[str, float]]:
    """Decode CTC logits greedily with collapsed repeats and blank removal.

    Args:
        logits: Logits tensor of shape [T, B, num_classes].

    Returns:
        List of tuples (predicted_reading, average_confidence) for each batch item.
    """
    probabilities = torch.softmax(logits, dim=-1)  # [T, B, num_classes]
    max_probs, predictions = torch.max(probabilities, dim=-1)  # [T, B]

    time_steps, batch_size = predictions.shape
    decoded_results: list[tuple[str, float]] = []

    for b in range(batch_size):
        char_list: list[str] = []
        conf_list: list[float] = []
        previous_idx = -1

        for t in range(time_steps):
            idx = int(predictions[t, b].item())
            prob = float(max_probs[t, b].item())

            if idx != previous_idx:
                if idx != BLANK_INDEX and idx in INDEX_TO_CHAR:
                    char_list.append(INDEX_TO_CHAR[idx])
                    conf_list.append(prob)
                previous_idx = idx

        predicted_reading = "".join(char_list)
        overall_confidence = float(sum(conf_list) / len(conf_list)) if conf_list else 0.0
        decoded_results.append((predicted_reading, overall_confidence))

    return decoded_results
