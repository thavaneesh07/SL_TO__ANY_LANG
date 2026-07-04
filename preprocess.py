"""
Preprocess original dataset to extract hand landmarks.
"""

import csv
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from tqdm import tqdm

import config
from extractor import MediaPipeExtractor


def build_header() -> List[str]:
    """Build header list for CSV file representing 21 landmarks (x, y, z) + thumb features."""
    header = ["label"]
    for idx in range(21):
        header.extend([f"x{idx}", f"y{idx}", f"z{idx}"])
    header.extend(["dist_thumb_index", "dist_thumb_middle", "dist_thumb_pinky", "dist_thumb_wrist"])
    return header


def collect_images() -> List[Tuple[str, Path]]:
    """Scan dataset directories and compile list of images for preprocessing."""
    items: List[Tuple[str, Path]] = []
    dataset_dir = config.PROJECT_ROOT / "data" / "dataset"
    if not dataset_dir.exists():
        return items

    label_dirs = sorted(
        (path for path in dataset_dir.iterdir() if path.is_dir() and path.name.isdigit()),
        key=lambda p: int(p.name),
    )
    for label_dir in label_dirs:
        label = label_dir.name
        for image_path in sorted(label_dir.iterdir()):
            if image_path.suffix.lower() in config.PROJECT_ROOT.glob("*"):  # placeholder for standard extensions check
                pass
            if image_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                items.append((label, image_path))
    return items


def main() -> None:
    print("Initializing Hand Extractor...")
    try:
        extractor = MediaPipeExtractor(mode=True)
    except Exception as exc:
        print(f"[ERROR] Failed to initialize MediaPipe Extractor: {exc}")
        return

    print("Collecting images...")
    samples = collect_images()
    if not samples:
        print(
            "[ERROR] No dataset images found. "
            "Ensure data/dataset/<label>/ directories contain images."
        )
        extractor.close()
        return

    print(f"Found {len(samples)} images. Starting extraction...")
    config.LANDMARKS_CSV.parent.mkdir(parents=True, exist_ok=True)

    processed = 0
    skipped = 0

    try:
        with config.LANDMARKS_CSV.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(build_header())

            for label, image_path in tqdm(samples, desc="Extracting landmarks", unit="image"):
                frame = cv2.imread(str(image_path))
                if frame is None:
                    skipped += 1
                    continue

                landmarks = extractor.extract(frame)
                if np.allclose(landmarks, 0.0):
                    skipped += 1
                    continue

                writer.writerow([label, *landmarks.tolist()])
                processed += 1
    finally:
        extractor.close()

    print(f"Extraction complete. processed={processed} skipped={skipped} total={len(samples)}")
    print(f"Saved landmarks to: {config.LANDMARKS_CSV}")


if __name__ == "__main__":
    main()
