"""CLI script to generate synthetic meter training crops and JSONL manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.ai.training.synthetic.generator import SyntheticGenerator


def generate_dataset(
    output_dir: Path,
    *,
    train_count: int = 2000,
    val_count: int = 400,
    seed: int = 42,
) -> None:
    """Generate synthetic crops and write images with JSONL manifest files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    generator = SyntheticGenerator(seed=seed)

    splits = [
        ("train", train_count),
        ("val", val_count),
    ]

    for split_name, count in splits:
        manifest_path = output_dir / f"{split_name}_manifest.jsonl"
        manifest_records: list[str] = []

        for i in range(count):
            sample = generator.generate_sample(split=split_name)
            filename = f"{split_name}_{i:06d}_{sample.image_id}.png"
            relative_image_path = f"images/{filename}"
            full_image_path = images_dir / filename
            sample.image.save(full_image_path, format="PNG")

            record = dict(sample.metadata)
            record["relative_path"] = relative_image_path
            manifest_records.append(json.dumps(record, ensure_ascii=False))

        manifest_path.write_text("\n".join(manifest_records) + "\n", encoding="utf-8")
        print(f"Generated {count} {split_name} samples -> {manifest_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/interim/synthetic"),
        help="Directory to save generated images and manifests.",
    )
    parser.add_argument(
        "--train-count",
        type=int,
        default=2000,
        help="Number of training samples to generate.",
    )
    parser.add_argument(
        "--val-count",
        type=int,
        default=400,
        help="Number of validation samples to generate.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic generation.",
    )
    args = parser.parse_args()
    generate_dataset(
        args.output_dir,
        train_count=args.train_count,
        val_count=args.val_count,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
