"""Training script for CRNN meter reading recognizer with exact-match evaluation."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from backend.ai.models.crnn import (
    CHARSET,
    CrnnRecognizer,
    decode_greedy,
)
from backend.ai.training.dataset import MeterCropDataset, collate_ocr_batch


def set_seed(seed: int) -> None:
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def calculate_metrics(
    predictions: list[str],
    ground_truths: list[str],
) -> dict[str, float]:
    """Calculate exact-match accuracy and character error rate (CER)."""
    if not ground_truths:
        return {"exact_match_accuracy": 0.0, "character_error_rate": 1.0}

    exact_matches = sum(
        1 for pred, gt in zip(predictions, ground_truths, strict=True) if pred == gt
    )
    exact_match_accuracy = exact_matches / len(ground_truths)

    total_edit_distance = 0
    total_gt_characters = 0

    for pred, gt in zip(predictions, ground_truths, strict=True):
        total_gt_characters += max(1, len(gt))
        # Simple Levenshtein distance
        dp = [[0] * (len(gt) + 1) for _ in range(len(pred) + 1)]
        for i in range(len(pred) + 1):
            dp[i][0] = i
        for j in range(len(gt) + 1):
            dp[0][j] = j
        for i in range(1, len(pred) + 1):
            for j in range(1, len(gt) + 1):
                cost = 0 if pred[i - 1] == gt[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost,
                )
        total_edit_distance += dp[len(pred)][len(gt)]

    character_error_rate = total_edit_distance / max(1, total_gt_characters)
    return {
        "exact_match_accuracy": round(exact_match_accuracy, 4),
        "character_error_rate": round(character_error_rate, 4),
    }


def evaluate(
    model: CrnnRecognizer,
    data_loader: DataLoader[Any],
    criterion: nn.CTCLoss,
    device: torch.device,
) -> tuple[float, dict[str, float]]:
    """Evaluate the model on validation data."""
    model.eval()
    total_loss = 0.0
    all_predictions: list[str] = []
    all_ground_truths: list[str] = []

    with torch.inference_mode():
        for images, targets, input_lengths, target_lengths, gts in data_loader:
            images = images.to(device)
            targets = targets.to(device)
            input_lengths = input_lengths.to(device)
            target_lengths = target_lengths.to(device)

            logits = model(images)  # [T, B, num_classes]
            log_probs = logits.log_softmax(dim=-1)
            loss = criterion(log_probs, targets, input_lengths, target_lengths)
            total_loss += float(loss.item()) * len(gts)

            decoded = decode_greedy(logits)
            preds = [item[0] for item in decoded]
            all_predictions.extend(preds)
            all_ground_truths.extend(gts)

    avg_loss = total_loss / max(1, len(all_ground_truths))
    metrics = calculate_metrics(all_predictions, all_ground_truths)
    return avg_loss, metrics


def train_model(
    data_dir: Path,
    output_dir: Path,
    *,
    epochs: int = 20,
    batch_size: int = 32,
    learning_rate: float = 5e-4,
    seed: int = 42,
    device_name: str | None = None,
    target_width: int = 160,
) -> Path:
    """Train CRNN model and save the best checkpoint."""
    set_seed(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    if device_name:
        device = torch.device(device_name)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_manifest = data_dir / "train_manifest.jsonl"
    val_manifest = data_dir / "val_manifest.jsonl"

    if not train_manifest.exists():
        raise FileNotFoundError(f"Training manifest not found: {train_manifest}")
    if not val_manifest.exists():
        raise FileNotFoundError(f"Validation manifest not found: {val_manifest}")

    train_dataset = MeterCropDataset(train_manifest, target_width=target_width)
    val_dataset = MeterCropDataset(val_manifest, target_width=target_width)

    print(f"Loaded {len(train_dataset)} train samples, {len(val_dataset)} val samples.")

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_ocr_batch,
        num_workers=0,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_ocr_batch,
        num_workers=0,
    )

    model = CrnnRecognizer(in_channels=3).to(device)
    criterion = nn.CTCLoss(blank=0, zero_infinity=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_exact_match = -1.0
    best_checkpoint_path = output_dir / "best.pt"
    history: list[dict[str, Any]] = []

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        train_samples = 0

        for images, targets, input_lengths, target_lengths, gts in train_loader:
            images = images.to(device)
            targets = targets.to(device)
            input_lengths = input_lengths.to(device)
            target_lengths = target_lengths.to(device)

            optimizer.zero_grad()
            logits = model(images)
            log_probs = logits.log_softmax(dim=-1)
            loss = criterion(log_probs, targets, input_lengths, target_lengths)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()

            train_loss += float(loss.item()) * len(gts)
            train_samples += len(gts)

        scheduler.step()
        avg_train_loss = train_loss / max(1, train_samples)
        val_loss, val_metrics = evaluate(model, val_loader, criterion, device)

        epoch_record = {
            "epoch": epoch,
            "train_loss": round(avg_train_loss, 4),
            "val_loss": round(val_loss, 4),
            **val_metrics,
        }
        history.append(epoch_record)
        print(
            f"Epoch {epoch:02d}/{epochs:02d} | "
            f"Train Loss: {avg_train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Exact Match: {val_metrics['exact_match_accuracy'] * 100:.2f}% | "
            f"CER: {val_metrics['character_error_rate']:.4f}"
        )

        current_exact_match = val_metrics["exact_match_accuracy"]
        if current_exact_match > best_exact_match:
            best_exact_match = current_exact_match
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "best_exact_match": best_exact_match,
                    "charset": CHARSET,
                    "target_width": target_width,
                    "target_height": 32,
                    "config": {
                        "epochs": epochs,
                        "batch_size": batch_size,
                        "learning_rate": learning_rate,
                        "seed": seed,
                    },
                },
                best_checkpoint_path,
            )
            print(f"Saved new best model checkpoint -> {best_checkpoint_path}")

    # Write training summary manifest
    report_path = output_dir / "training_report.json"
    report_data = {
        "best_exact_match": best_exact_match,
        "epochs": epochs,
        "seed": seed,
        "history": history,
    }
    report_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    print(f"Training finished. Report written to {report_path}")
    return best_checkpoint_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/interim/synthetic"),
        help="Directory containing train_manifest.jsonl and val_manifest.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("models/recognizer"),
        help="Directory to save checkpoints and evaluation reports",
    )
    parser.add_argument("--epochs", type=int, default=20, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=5e-4, help="Learning rate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--device", type=str, default=None, help="Device (cpu, cuda)")
    parser.add_argument("--target-width", type=int, default=160, help="Target image width")

    args = parser.parse_args()
    train_model(
        args.data_dir,
        args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        seed=args.seed,
        device_name=args.device,
        target_width=args.target_width,
    )


if __name__ == "__main__":
    main()
