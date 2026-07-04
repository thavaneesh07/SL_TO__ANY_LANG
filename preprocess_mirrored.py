"""
Preprocess Mirrored Dataset.

Extracts hand landmarks from mirrored (horizontally flipped) gesture images.
"""

import csv
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from tqdm import tqdm

import config
from extractor import MediaPipeExtractor

MIRRORED_SUFFIX = "_mirrored"


def build_header() -> List[str]:
    """Build header list for CSV file representing 21 landmarks (x, y, z) + thumb features."""
    header = ["label"]
    for idx in range(21):
        header.extend([f"x{idx}", f"y{idx}", f"z{idx}"])
    header.extend(["dist_thumb_index", "dist_thumb_middle", "dist_thumb_pinky", "dist_thumb_wrist"])
    return header


def collect_mirrored_images() -> List[Tuple[str, Path]]:
    """Collect all mirrored (flipped) images from dataset directory."""
    items: List[Tuple[str, Path]] = []
    dataset_dir = config.PROJECT_ROOT / "data" / "dataset"
    if not dataset_dir.exists():
        return items

    # Find mirrored label directories (0_mirrored, 1_mirrored, etc.)
    label_dirs = sorted(
        (path for path in dataset_dir.iterdir() 
         if path.is_dir() and path.name.endswith(MIRRORED_SUFFIX)),
        key=lambda p: int(p.name.replace(MIRRORED_SUFFIX, "")),
    )
    
    for mirrored_dir in label_dirs:
        # Extract original label from directory name (e.g., "0_mirrored" -> "0")
        label = mirrored_dir.name.replace(MIRRORED_SUFFIX, "")
        
        for image_path in sorted(mirrored_dir.iterdir()):
            if image_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                items.append((label, image_path))
    
    return items


def main() -> bool:
    print("\n" + "="*70)
    print("PREPROCESSING MIRRORED DATASET")
    print("="*70)
    
    try:
        extractor = MediaPipeExtractor(mode=True)
    except Exception as exc:
        print(f"[ERROR] Failed to initialize MediaPipe Extractor: {exc}")
        return False

    samples = collect_mirrored_images()
    
    if not samples:
        print("\n[ERROR] No mirrored dataset images found!")
        print("Expected folders: data/dataset/0_mirrored/, 1_mirrored/, etc.")
        print("Please run mirror_dataset.py first.")
        extractor.close()
        return False
    
    print(f"\nFound {len(samples)} mirrored images")
    print(f"Output file: {config.MIRRORED_CSV}\n")
    
    config.MIRRORED_CSV.parent.mkdir(parents=True, exist_ok=True)

    processed = 0
    skipped = 0

    try:
        with config.MIRRORED_CSV.open("w", newline="", encoding="utf-8") as csv_file:
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
    
    print("\n" + "="*70)
    print(f"Preprocessing complete. processed={processed} skipped={skipped} total={len(samples)}")
    print(f"Saved: {config.MIRRORED_CSV}")
    print("="*70)
    
    return processed > 0


if __name__ == "__main__":
    main()
