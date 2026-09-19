from pathlib import Path

from backend.ai.training.data.inspect_dataset import build_inventory


def test_build_inventory_counts_supported_images(tmp_path: Path) -> None:
    (tmp_path / "meter.JPG").touch()
    (tmp_path / "notes.txt").touch()

    inventory = build_inventory(tmp_path)

    assert inventory["image_count"] == 1
    assert inventory["suffix_counts"] == {".jpg": 1}
