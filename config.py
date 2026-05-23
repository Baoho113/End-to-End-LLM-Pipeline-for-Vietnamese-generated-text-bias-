"""
config.py — Central configuration for the bias detection pipeline.

All paths, label definitions, model parameters, and severity mappings
live here. Edit this file to adjust the pipeline behaviour.
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

DATASET_PATH = os.path.join(DATA_DIR, "vietnamese_bias_claude.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "bias_detector.pkl")
RESULTS_PATH = os.path.join(OUTPUT_DIR, "evaluation_results.json")

# Ensure directories exist
for d in [DATA_DIR, MODEL_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Labels & categories
# ---------------------------------------------------------------------------
BIAS_LABELS = [
    "neutral",
    "gender_stereotype",
    "regional_bias",
    "socioeconomic_occupation_bias",
    "appearance_derogation",
]

# ---------------------------------------------------------------------------
# Severity mapping
# ---------------------------------------------------------------------------
# Default severity per category. The detector adjusts dynamically
# based on classifier confidence (see detector.py).
SEVERITY_MAP = {
    "neutral": 0,
    "gender_stereotype": 2,
    "regional_bias": 2,
    "socioeconomic_occupation_bias": 2,
    "appearance_derogation": 2,
}

# Confidence thresholds for severity adjustment
CONFIDENCE_LOW = 0.5    # below this → reduce severity by 1
CONFIDENCE_HIGH = 0.85  # above this → increase severity by 1

# ---------------------------------------------------------------------------
# Feature extraction settings
# ---------------------------------------------------------------------------
TFIDF_WORD_MAX_FEATURES = 15000
TFIDF_CHAR_MAX_FEATURES = 10000
TFIDF_WORD_NGRAM = (1, 3)
TFIDF_CHAR_NGRAM = (2, 5)
TFIDF_MIN_DF = 2
TFIDF_MAX_DF = 0.95

# ---------------------------------------------------------------------------
# Classifier settings
# ---------------------------------------------------------------------------
SVM_C = 1.0
SVM_MAX_ITER = 5000
CALIBRATION_CV = 3
RANDOM_STATE = 42
TEST_SIZE = 0.2
CROSS_VAL_FOLDS = 5

# ---------------------------------------------------------------------------
# LLM API settings
# ---------------------------------------------------------------------------
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_MAX_TOKENS = 300
# API key is read from environment: ANTHROPIC_API_KEY
