from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "model.pkl"
LANDMARKS_CSV = PROJECT_ROOT / "data" / "landmarks.csv"
MIRRORED_CSV = PROJECT_ROOT / "data" / "landmarks_mirrored.csv"
COMBINED_CSV = PROJECT_ROOT / "data" / "landmarks_combined.csv"

FONT_CANDIDATES = (
    PROJECT_ROOT / "assets" / "fonts" / "NotoSansKannada-Regular.ttf",
    PROJECT_ROOT / "assets" / "fonts" / "NotoSansKannada-VariableFont_wdth,wght.ttf",
    PROJECT_ROOT / "NotoSansKannada-Regular.ttf",
)

# Inference Hyperparameters
HISTORY_LEN = 9             # Frames kept for majority-vote / EMA smoothing
MIN_VOTES = 3               # Minimum frames a class must win (if majority vote is used)
CONF_THRESHOLD = 0.28       # Minimum model confidence to accept a prediction
NO_HAND_TIMEOUT = 15        # Frames without detection before resetting display state
HAND_TIMEOUT_FRAMES = 10    # Frames before dropping a hand's history when it disappears
SEQ_MAX_GAP_SEC = 1.2       # Max gap between digits to keep same number
COMMIT_COOLDOWN_SEC = 0.35  # Debounce to prevent duplicate commits while holding
NUMBER_RESET_NO_HAND_FRAMES = 45  # Clear number buffer after extended no-hand period
EMA_ALPHA = 0.4             # Exponential Moving Average factor (higher = faster, lower = smoother)

# Color Palette (BGR format for OpenCV)
COL_WHITE = (255, 255, 255)
COL_BLACK = (20, 20, 20)
COL_GREEN = (0, 200, 0)
COL_AMBER = (0, 165, 255)
COL_RED = (0, 0, 220)
COL_CYAN = (220, 220, 0)
COL_DARK_BG = (30, 30, 30)
