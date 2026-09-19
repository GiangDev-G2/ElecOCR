"""Fine-tuning wrapper for YOLO meter display detector."""

from __future__ import annotations

import argparse
from pathlib import Path


def train_detector(
    data_config: Path,
    output_dir: Path,
    *,
    base_model: str = "yolov8n.pt",
    epochs: int = 50,
    imgsz: int = 640,
    batch_size: int = 16,
    seed: int = 42,
    device: str = "",
) -> Path:
    """Fine-tune a YOLO nano detector on the single display class.

    Args:
        data_config: Path to dataset YAML configuration file.
        output_dir: Target directory for saving model artifacts.
        base_model: Base checkpoint name or path.
        epochs: Number of training epochs.
        imgsz: Training image dimension in pixels.
        batch_size: Batch size.
        seed: Random seed for reproducibility.
        device: Target device string (e.g. '0', 'cpu', or '' for auto).

    Returns:
        Path to the best saved model weights.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Deliberate lazy import: ultralytics is an optional training dependency
    try:
        from ultralytics import YOLO
    except ImportError as err:
        message = (
            "ultralytics is required for detector training. Install with: pip install ultralytics"
        )
        raise ImportError(message) from err

    print(f"Initializing detector with base model: {base_model}")
    model = YOLO(base_model)

    training_arguments: dict[str, object] = {
        "data": str(data_config.resolve()),
        "epochs": epochs,
        "imgsz": imgsz,
        "batch": batch_size,
        "project": str(output_dir.resolve()),
        "name": "display_detector",
        "seed": seed,
        "exist_ok": True,
    }
    if device:
        training_arguments["device"] = device

    print(f"Starting YOLO detector training on {data_config}...")
    model.train(**training_arguments)

    best_weights_path = output_dir / "display_detector" / "weights" / "best.pt"
    print(f"Detector training completed. Best weights: {best_weights_path}")
    return best_weights_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Path to YOLO dataset.yaml file defining train/val paths and display class.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("models/detector"),
        help="Directory to save detector checkpoints.",
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="yolov8n.pt",
        help="Base pretrained YOLO checkpoint.",
    )
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs.")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size in pixels.")
    parser.add_argument("--batch-size", type=int, default=16, help="Training batch size.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--device", type=str, default="", help="Device (e.g. '0', 'cpu').")

    args = parser.parse_args()
    train_detector(
        data_config=args.data,
        output_dir=args.output_dir,
        base_model=args.base_model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch_size=args.batch_size,
        seed=args.seed,
        device=args.device,
    )


if __name__ == "__main__":
    main()
