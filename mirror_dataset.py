"""
Mirror Dataset Generator.

Creates horizontally flipped copies of all gesture images.
"""

import sys
from pathlib import Path
from typing import List

import cv2
from tqdm import tqdm

import config

MIRRORED_SUFFIX = "_mirrored"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def mirror_dataset() -> int:
    """
    Mirror all images in the dataset by flipping horizontally.
    
    Creates new folders: data/dataset/0_mirrored/, 1_mirrored/, etc.
    """
    dataset_dir = config.PROJECT_ROOT / "data" / "dataset"
    print("Starting dataset mirroring...")
    print(f"Reading from: {dataset_dir}")
    
    if not dataset_dir.exists():
        print(f"[ERROR] Dataset directory not found: {dataset_dir}")
        return 0
    
    # Find all numeric label directories
    label_dirs = sorted(
        [d for d in dataset_dir.iterdir() 
         if d.is_dir() and d.name.isdigit() and not d.name.endswith(MIRRORED_SUFFIX)],
        key=lambda p: int(p.name)
    )
    
    if not label_dirs:
        print("[ERROR] No gesture folders found in data/dataset/")
        print("Expected structure: data/dataset/0/, data/dataset/1/, ... data/dataset/9/")
        return 0
    
    total_mirrored = 0
    
    for label_dir in label_dirs:
        label = label_dir.name
        mirrored_dir = dataset_dir / f"{label}{MIRRORED_SUFFIX}"
        
        # Create mirrored directory
        mirrored_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all image files in this label directory
        image_files = [
            f for f in label_dir.iterdir()
            if f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        
        if not image_files:
            print(f"  Label {label}: No images found")
            continue
        
        print(f"\nLabel {label}: Processing {len(image_files)} images")
        
        for image_path in tqdm(image_files, desc="  Mirroring", unit="image"):
            img = cv2.imread(str(image_path))
            if img is None:
                print(f"    [WARNING] Could not read {image_path.name}")
                continue
            
            # Mirror image horizontally
            mirrored_img = cv2.flip(img, 1)
            
            output_path = mirrored_dir / image_path.name
            success = cv2.imwrite(str(output_path), mirrored_img)
            
            if success:
                total_mirrored += 1
            else:
                print(f"    [ERROR] Could not write {output_path}")
    
    return total_mirrored


def combine_datasets() -> int:
    """Copy mirrored images back to original folders to have one combined dataset."""
    dataset_dir = config.PROJECT_ROOT / "data" / "dataset"
    print("\n" + "="*70)
    print("Combining mirrored images with original dataset...")
    print("="*70)
    
    label_dirs = sorted(
        [d for d in dataset_dir.iterdir() 
         if d.is_dir() and d.name.isdigit() and not d.name.endswith(MIRRORED_SUFFIX)],
        key=lambda p: int(p.name)
    )
    
    total_combined = 0
    
    for label_dir in label_dirs:
        label = label_dir.name
        mirrored_dir = dataset_dir / f"{label}{MIRRORED_SUFFIX}"
        
        if not mirrored_dir.exists():
            continue
        
        mirrored_files = [
            f for f in mirrored_dir.iterdir()
            if f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        
        print(f"  Copying {len(mirrored_files)} mirrored images to label {label}/")
        
        for mirrored_path in tqdm(mirrored_files, desc="  Copying", unit="image"):
            stem = mirrored_path.stem
            suffix = mirrored_path.suffix
            new_name = f"{stem}_mirrored{suffix}"
            
            output_path = label_dir / new_name
            
            img = cv2.imread(str(mirrored_path))
            if img is not None and cv2.imwrite(str(output_path), img):
                total_combined += 1
    
    return total_combined


def main() -> None:
    print("\n" + "="*70)
    print("DATASET MIRRORING TOOL")
    print("="*70)
    
    combine = "--combine" in sys.argv
    
    total_mirrored = mirror_dataset()
    
    if total_mirrored == 0:
        print("\n[ERROR] No images were mirrored!")
        return

    print(f"\n[OK] Successfully mirrored {total_mirrored} images")

    if combine:
        combined = combine_datasets()
        print(f"\n[OK] Combined {combined} mirrored images into original dataset directories.")
    
    print("\n" + "="*70)
    print("MIRRORING COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()
