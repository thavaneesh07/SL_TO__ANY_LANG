"""
Hand landmark extraction engine supporting both left and right hands equally.

Provides robust initialization, type safety, and custom drawing routines for MediaPipe.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

try:
    import mediapipe as mp
except ImportError as err:
    raise ImportError(
        "MediaPipe is not installed. Please run: pip install mediapipe"
    ) from err

import config

# MediaPipe connections configuration
HAND_CONNECTIONS: Tuple[Tuple[int, int], ...] = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
)

DEFAULT_TASK_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/"
    "hand_landmarker.task"
)

# Landmark Indices
WRIST_INDEX = 0
MCP_INDEX = 5  # Index finger MCP - used for scaling


class MediaPipeExtractor:
    """
    Hand landmark extraction engine using MediaPipe backend.
    
    Supports both solutions (classical) and tasks (modern) API.
    """

    def __init__(self, mode: bool = True, model_path: Optional[str | Path] = None) -> None:
        self.static_mode = mode
        self.backend: Optional[str] = None
        self.last_results: Any = None
        
        # Cache for all detected hands
        self.last_hand_landmarks: List[Any] = []
        self.last_hand_protos: List[Any] = []
        self.last_detected_handedness_all: List[str] = []
        
        self.mp_hands: Any = None
        self.mp_drawing: Any = None
        self.hands: Any = None
        self.landmarker: Any = None

        # Attempt to load the best available backend
        try:
            if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
                self._init_solutions_backend()
            else:
                self._init_tasks_backend(model_path)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to initialize MediaPipe Extractor backend: {exc}"
            ) from exc

    def _init_solutions_backend(self) -> None:
        """Initialize MediaPipe solutions backend (default legacy API)."""
        self.backend = "solutions"
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.static_mode,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )

    def _init_tasks_backend(self, model_path: Optional[str | Path]) -> None:
        """Initialize MediaPipe tasks backend (modern API)."""
        try:
            from mediapipe.tasks.python import vision
        except ImportError as err:
            raise ImportError(
                "MediaPipe vision tasks could not be imported."
            ) from err

        self.backend = "tasks"
        resolved_model_path = self._resolve_task_model_path(model_path)
        base_options = mp.tasks.BaseOptions(model_asset_path=str(resolved_model_path))
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def _resolve_task_model_path(self, model_path: Optional[str | Path]) -> Path:
        """Resolve the task model path or download it if missing."""
        candidates = []
        if model_path is not None:
            candidates.append(Path(model_path))
        
        # Local paths relative to config or current dir
        candidates.extend([
            config.PROJECT_ROOT / "assets" / "models" / "hand_landmarker.task",
            config.PROJECT_ROOT / "hand_landmarker.task",
            Path("assets/models/hand_landmarker.task"),
            Path("hand_landmarker.task"),
        ])

        for candidate in candidates:
            if candidate.exists():
                return candidate

        # Download if none exists
        download_path = config.PROJECT_ROOT / "assets" / "models" / "hand_landmarker.task"
        download_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading hand landmarker model to {download_path}...")
        try:
            urllib.request.urlretrieve(DEFAULT_TASK_MODEL_URL, str(download_path))
        except Exception as exc:
            raise RuntimeError(
                f"MediaPipe task model missing and auto-download failed: {exc}. "
                f"Please manually download the model to: {download_path}"
            ) from exc
        return download_path

    @staticmethod
    def _normalize_landmarks(landmarks_flat: np.ndarray) -> np.ndarray:
        """
        Make landmark features position- and scale-invariant.
        
        Wrist (0) becomes (0,0,0) origin, scaled by wrist-to-index MCP distance.
        Appends engineered thumb features to make thumb posture (tucked vs extended)
        much more impactful.
        """
        coords = landmarks_flat.reshape(21, 3).copy()

        # Translate so wrist is at origin
        wrist = coords[WRIST_INDEX].copy()
        coords -= wrist

        # Compute scale: distance from wrist to index MCP
        scale = float(np.linalg.norm(coords[MCP_INDEX]))
        if scale < 1e-6:
            scale = 1e-6

        # Scale-normalize
        coords /= scale

        # --- Engineered Thumb Features ---
        # Coordinates of key landmarks (post-normalization)
        thumb_tip = coords[4]
        index_mcp = coords[5]
        middle_mcp = coords[9]
        pinky_mcp = coords[17]

        # Calculate Euclidean distances to emphasize thumb open vs folded state
        dist_thumb_index = float(np.linalg.norm(thumb_tip - index_mcp))
        dist_thumb_middle = float(np.linalg.norm(thumb_tip - middle_mcp))
        dist_thumb_pinky = float(np.linalg.norm(thumb_tip - pinky_mcp))
        dist_thumb_wrist = float(np.linalg.norm(thumb_tip))  # Wrist is at (0,0,0)

        # Append thumb features to the 63 normalized coordinates (total = 67 features)
        features = np.hstack([
            coords.flatten(),
            [dist_thumb_index, dist_thumb_middle, dist_thumb_pinky, dist_thumb_wrist]
        ])

        return features.astype(np.float32)

    @staticmethod
    def _flatten_landmarks(landmarks: Any) -> np.ndarray:
        """Flatten 21 landmarks into a 63-element vector."""
        coords = []
        for lm in landmarks:
            coords.extend([lm.x, lm.y, lm.z])
        return np.array(coords, dtype=np.float32)

    def extract_all(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Extract normalized landmarks for all detected hands.
        
        Returns a list of dicts with 'label' and 'landmarks' keys.
        """
        if frame is None:
            self.last_results = None
            self.last_hand_landmarks = []
            self.last_hand_protos = []
            self.last_detected_handedness_all = []
            return []

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.last_hand_landmarks = []
        self.last_hand_protos = []
        self.last_detected_handedness_all = []

        output = []

        if self.backend == "solutions":
            self.last_results = self.hands.process(rgb_frame)
            if not self.last_results or not self.last_results.multi_hand_landmarks:
                return []

            for idx, hand_landmarks in enumerate(self.last_results.multi_hand_landmarks):
                label = "Unknown"
                if self.last_results.multi_handedness and idx < len(self.last_results.multi_handedness):
                    handedness = self.last_results.multi_handedness[idx]
                    label = getattr(handedness.classification[0], "label", "Unknown")

                self.last_hand_protos.append(hand_landmarks)
                self.last_hand_landmarks.append(hand_landmarks.landmark)
                self.last_detected_handedness_all.append(label)

                raw = self._flatten_landmarks(hand_landmarks.landmark)
                output.append({
                    "label": label,
                    "landmarks": self._normalize_landmarks(raw)
                })
            return output

        # Tasks backend
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        self.last_results = self.landmarker.detect(mp_image)
        if not self.last_results or not self.last_results.hand_landmarks:
            return []

        for idx, hand_landmarks in enumerate(self.last_results.hand_landmarks):
            label = "Unknown"
            if self.last_results.handedness and idx < len(self.last_results.handedness):
                cat = self.last_results.handedness[idx]
                label = getattr(cat[0], "category_name", "Unknown") if cat else "Unknown"

            self.last_hand_landmarks.append(hand_landmarks)
            self.last_detected_handedness_all.append(label)

            raw = self._flatten_landmarks(hand_landmarks)
            output.append({
                "label": label,
                "landmarks": self._normalize_landmarks(raw)
            })
        return output

    def extract(self, frame: np.ndarray) -> np.ndarray:
        """
        Extract normalized landmarks from the first detected hand.
        
        Kept for backward compatibility with dataset preprocessing.
        """
        zero_vector = np.zeros(63, dtype=np.float32)
        hands = self.extract_all(frame)
        if not hands:
            return zero_vector
        return hands[0]["landmarks"]

    def draw_hand_by_index(self, frame: np.ndarray, hand_index: int = 0) -> None:
        """Draw hand skeleton on frame by index."""
        if frame is None or not self.last_hand_landmarks:
            return
        
        if hand_index >= len(self.last_hand_landmarks):
            return
        
        if self.backend == "solutions":
            if hand_index < len(self.last_hand_protos):
                self.mp_drawing.draw_landmarks(
                    frame,
                    self.last_hand_protos[hand_index],
                    self.mp_hands.HAND_CONNECTIONS,
                )
            return
        
        # Tasks backend custom drawing
        height, width = frame.shape[:2]
        hand_landmarks = self.last_hand_landmarks[hand_index]
        points = []
        for lm in hand_landmarks:
            x_pos = int(lm.x * width)
            y_pos = int(lm.y * height)
            points.append((x_pos, y_pos))
            cv2.circle(frame, (x_pos, y_pos), 3, (0, 255, 255), -1)
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, points[a], points[b], (0, 255, 0), 2)

    def draw_all_hands(self, frame: np.ndarray) -> None:
        """Draw hand skeletons for all detected hands."""
        if frame is None or not self.last_hand_landmarks:
            return

        if self.backend == "solutions":
            for proto in self.last_hand_protos:
                self.mp_drawing.draw_landmarks(
                    frame,
                    proto,
                    self.mp_hands.HAND_CONNECTIONS,
                )
            return

        # Tasks backend custom drawing
        height, width = frame.shape[:2]
        for hand_landmarks in self.last_hand_landmarks:
            points = []
            for lm in hand_landmarks:
                x_pos = int(lm.x * width)
                y_pos = int(lm.y * height)
                points.append((x_pos, y_pos))
                cv2.circle(frame, (x_pos, y_pos), 3, (0, 255, 255), -1)
            for a, b in HAND_CONNECTIONS:
                cv2.line(frame, points[a], points[b], (0, 255, 0), 2)

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self.hands is not None:
            self.hands.close()
        if self.landmarker is not None:
            self.landmarker.close()
