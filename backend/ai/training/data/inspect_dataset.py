"""Create a deterministic image inventory for a local dataset directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

IMAGE_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".webp"})


def build_inventory(dataset_path: Path) -> dict[str, object]:
    """Count supported image files without reading or modifying image content."""
    image_paths = sorted(
        path for path in dataset_path.rglob("*") if path.suffix.lower() in IMAGE_SUFFIXES
    )
    suffix_counts: dict[str, int] = {}
    for image_path in image_paths:
        suffix = image_path.suffix.lower()
        suffix_counts[suffix] = suffix_counts.get(suffix, 0) + 1
    return {
        "dataset_path": dataset_path.as_posix(),
        "image_count": len(image_paths),
        "suffix_counts": suffix_counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_path", type=Path)
    arguments = parser.parse_args()
    print(json.dumps(build_inventory(arguments.dataset_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
