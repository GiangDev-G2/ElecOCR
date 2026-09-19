"""Download the reproducible 119-image YUVA EB subset distributed by MathWorks."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import urllib.request
from pathlib import Path
from zipfile import ZipFile

DATASET_URL = "https://ssd.mathworks.com/supportfiles/vision/data/7SegmentImages.zip"
ARCHIVE_SHA256 = "974e88d1480c13ab3babe3a728d2d81e8be8c6e50ff9e29205c76abdf4d10a25"


def calculate_sha256(file_path: Path) -> str:
    """Return the lowercase SHA-256 checksum for a local file."""
    digest = hashlib.sha256()
    with file_path.open("rb") as file_handle:
        while chunk := file_handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_extract(archive_path: Path, destination: Path) -> None:
    destination_root = destination.resolve()
    with ZipFile(archive_path) as archive:
        for member in archive.infolist():
            member_path = (destination / member.filename).resolve()
            if destination_root not in member_path.parents and member_path != destination_root:
                raise ValueError(f"Unsafe archive member: {member.filename}")
        archive.extractall(destination)


def download_dataset(destination: Path) -> Path:
    """Download, verify and extract the dataset without modifying raw images."""
    destination.mkdir(parents=True, exist_ok=True)
    archive_path = destination / "7SegmentImages.zip"
    temporary_path = destination / "7SegmentImages.zip.part"

    if not archive_path.exists() or calculate_sha256(archive_path) != ARCHIVE_SHA256:
        with (
            urllib.request.urlopen(DATASET_URL, timeout=60) as response,
            temporary_path.open("wb") as output,
        ):
            shutil.copyfileobj(response, output)
        if calculate_sha256(temporary_path) != ARCHIVE_SHA256:
            temporary_path.unlink(missing_ok=True)
            raise ValueError("Downloaded archive checksum does not match the registry.")
        temporary_path.replace(archive_path)

    extraction_path = destination / "extracted"
    if not extraction_path.exists():
        _safe_extract(archive_path, extraction_path)
    return extraction_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path("data/raw/yuva_eb"),
    )
    arguments = parser.parse_args()
    extracted_path = download_dataset(arguments.destination)
    print(extracted_path)


if __name__ == "__main__":
    main()
