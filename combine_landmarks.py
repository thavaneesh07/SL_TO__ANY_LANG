"""
Combine Original and Mirrored Landmarks

Merges data/landmarks.csv and data/landmarks_mirrored.csv into a single
combined dataset for training. This gives the model both original and
mirrored gesture images, making it work well for both hand orientations.

Usage:
1. Run: python preprocess.py
2. Run: python preprocess_mirrored.py
3. Run: python combine_landmarks.py
4. Run: python train.py
"""

from pathlib import Path
import csv

ORIGINAL_CSV = Path("data/landmarks.csv")
MIRRORED_CSV = Path("data/landmarks_mirrored.csv")
COMBINED_CSV = Path("data/landmarks_combined.csv")


def read_csv(filepath):
    """Read CSV file and return header + rows."""
    if not filepath.exists():
        return None, []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        rows = list(reader)
    
    return header, rows


def combine_datasets():
    """Combine original and mirrored datasets."""
    print("\n" + "="*70)
    print("COMBINING ORIGINAL AND MIRRORED DATASETS")
    print("="*70)
    
    # Read both datasets
    print(f"\nReading: {ORIGINAL_CSV}")
    orig_header, orig_rows = read_csv(ORIGINAL_CSV)
    
    if orig_header is None:
        print(f"[ERROR] {ORIGINAL_CSV} not found!")
        print("   Run: python preprocess.py")
        return False
    
    print(f"[OK] Found {len(orig_rows)} original samples")
    
    print(f"\nReading: {MIRRORED_CSV}")
    mirror_header, mirror_rows = read_csv(MIRRORED_CSV)
    
    if mirror_header is None:
        print(f"[ERROR] {MIRRORED_CSV} not found!")
        print("   Run: python preprocess_mirrored.py")
        return False
    
    print(f"[OK] Found {len(mirror_rows)} mirrored samples")
    
    # Verify headers match
    if orig_header != mirror_header:
        print("\n[ERROR] Headers don't match!")
        print(f"  Original: {orig_header[:3]}...")
        print(f"  Mirrored: {mirror_header[:3]}...")
        return False
    
    # Combine rows
    all_rows = orig_rows + mirror_rows
    
    print(f"\nCombining...")
    print(f"  Original: {len(orig_rows)} samples")
    print(f"  Mirrored: {len(mirror_rows)} samples")
    print(f"  Total:    {len(all_rows)} samples")
    
    # Write combined file
    print(f"\nWriting: {COMBINED_CSV}")
    COMBINED_CSV.parent.mkdir(parents=True, exist_ok=True)
    
    with open(COMBINED_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(orig_header)
        writer.writerows(all_rows)
    
    print(f"[OK] Saved combined dataset: {COMBINED_CSV}")
    
    return True


def main():
    success = combine_datasets()
    
    if success:
        print("\n" + "="*70)
        print("DATASETS COMBINED SUCCESSFUL")
        print("="*70)
        print("\nNow you have:")
        print(f"  • Original landmarks: {ORIGINAL_CSV}")
        print(f"  • Mirrored landmarks:  {MIRRORED_CSV}")
        print(f"  • Combined landmarks:  {COMBINED_CSV}")
        print("\nNext step:")
        print("  python train.py")
        print("\nThis will train a model on both original and mirrored images,")
        print("making it work equally well for left and right hands!")
    else:
        print("\n" + "="*70)
        print("COMBINING FAILED")
        print("="*70)
        return False
    
    return True


if __name__ == "__main__":
    main()
