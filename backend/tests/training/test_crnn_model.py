"""Unit tests for CRNN architecture, CTC decoding, and pipeline integration."""

import numpy as np
import torch

from backend.ai.domain import OcrStatus
from backend.ai.models.crnn import (
    CHARSET,
    NUM_CLASSES,
    CrnnRecognizer,
    decode_greedy,
    decode_token_indices,
    encode_reading,
)
from backend.ai.pipeline import CrnnOcrPipeline
from backend.ai.training.train_recognizer import calculate_metrics


def test_encode_and_decode_tokens() -> None:
    text = "00123.4"
    tokens = encode_reading(text)
    decoded = decode_token_indices(tokens)
    assert decoded == text
    assert len(tokens) == 7


def test_crnn_forward_pass_shape() -> None:
    batch_size = 2
    height = 32
    width = 160
    model = CrnnRecognizer(in_channels=3, num_classes=NUM_CLASSES)
    dummy_input = torch.randn(batch_size, 3, height, width)

    logits = model(dummy_input)

    # W = 160 -> T = 160 / 4 = 40
    expected_time_steps = 40
    assert logits.shape == (expected_time_steps, batch_size, NUM_CLASSES)


def test_decode_greedy_handles_repeated_characters_and_blanks() -> None:
    time_steps = 5
    batch_size = 1
    logits = torch.zeros((time_steps, batch_size, NUM_CLASSES))

    # Token for '5'
    idx_5 = CHARSET.index("5") + 1
    # Time 0, 1: class '5' -> should collapse into single '5'
    logits[0, 0, idx_5] = 10.0
    logits[1, 0, idx_5] = 10.0
    # Time 2: blank (0)
    logits[2, 0, 0] = 10.0
    # Time 3: class '5' again -> separated by blank, so second '5' appears!
    logits[3, 0, idx_5] = 10.0
    # Time 4: blank
    logits[4, 0, 0] = 10.0

    decoded = decode_greedy(logits)
    assert len(decoded) == 1
    reading, confidence = decoded[0]
    assert reading == "55"
    assert confidence > 0.95


def test_calculate_metrics_exact_match() -> None:
    predictions = ["00123.4", "00543.1", "12345"]
    ground_truths = ["00123.4", "00543.2", "12345"]

    metrics = calculate_metrics(predictions, ground_truths)
    # 2 out of 3 match exactly -> 66.67%
    assert 0.66 <= metrics["exact_match_accuracy"] <= 0.67
    assert metrics["character_error_rate"] > 0.0


def test_crnn_ocr_pipeline_predict() -> None:
    model = CrnnRecognizer(in_channels=3)
    pipeline = CrnnOcrPipeline(model=model)
    assert pipeline.is_ready is True
    assert "crnn" in pipeline.model_version

    dummy_image = np.zeros((32, 160, 3), dtype=np.uint8)
    prediction = pipeline.predict(dummy_image, debug=False)
    assert prediction.status in (OcrStatus.OK, OcrStatus.REVIEW_REQUIRED, OcrStatus.UNREADABLE)
