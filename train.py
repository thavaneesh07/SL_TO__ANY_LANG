"""
Train the Sign2Kannada Gesture Classifier.

Trains a Random Forest classifier on the extracted hand landmark dataset.
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split, cross_val_score
import joblib
import numpy as np

import config


def main() -> None:
    print("Loading landmark dataset...")
    if not config.LANDMARKS_CSV.exists():
        print(f"[ERROR] Missing input file: {config.LANDMARKS_CSV}")
        print("Please run preprocess.py and combine_landmarks.py first.")
        return

    try:
        data = np.loadtxt(str(config.LANDMARKS_CSV), delimiter=",", skiprows=1)
    except Exception as exc:
        print(f"[ERROR] Failed to load CSV data: {exc}")
        return

    if data.size == 0:
        print("[ERROR] landmarks.csv has no samples. Please ensure features are extracted.")
        return

    if data.ndim == 1:
        data = data.reshape(1, -1)
    if data.shape[1] != 68:
        print(f"[ERROR] Invalid landmarks shape: expected 68 columns (label + 63 landmarks + 4 thumb features), got {data.shape[1]}.")
        return
    if np.isnan(data).any():
        print("[ERROR] landmarks.csv contains invalid numeric values (NaN).")
        return

    y = data[:, 0].astype(int)
    X = data[:, 1:]

    if len(y) < 2:
        print("[ERROR] Need at least 2 samples to train classifier.")
        return

    classes, class_counts = np.unique(y, return_counts=True)
    if len(classes) < 2:
        print(
            f"[ERROR] Need at least 2 distinct gesture labels. Found labels: {classes.tolist()}"
        )
        return
    if np.any(class_counts < 2):
        print(
            "[ERROR] Each class must have at least 2 samples for stratified split. "
            f"Current class counts: {dict(zip(classes.tolist(), class_counts.tolist()))}"
        )
        return

    print(f"Dataset loaded: {len(y)} samples, {len(classes)} classes: {classes.tolist()}")
    print(f"Samples per class: {dict(zip(classes.tolist(), class_counts.tolist()))}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\nTraining on {len(X_train)} samples, testing on {len(X_test)} samples...")

    from sklearn.neighbors import KNeighborsClassifier
    print("\nTraining KNN Classifier...")
    model = KNeighborsClassifier(n_neighbors=5, weights="distance", n_jobs=-1)
    model.fit(X_train, y_train)

    # 5-fold cross-validation
    print("Evaluating model with 5-Fold Cross-Validation...")
    try:
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy", n_jobs=-1)
        print(f"5-Fold CV Accuracy: {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
    except Exception as exc:
        print(f"[WARNING] Cross-validation evaluation skipped/failed: {exc}")

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print("\nClassification report (held-out test set):")
    print(classification_report(y_test, y_pred))
    print(f"Test Accuracy: {accuracy:.4f}")

    try:
        joblib.dump(model, config.MODEL_PATH)
        print(f"\nSaved model: {config.MODEL_PATH}")
        print("Done! Run main.py to start real-time recognition.")
    except Exception as exc:
        print(f"[ERROR] Failed to save trained model: {exc}")


if __name__ == "__main__":
    main()
