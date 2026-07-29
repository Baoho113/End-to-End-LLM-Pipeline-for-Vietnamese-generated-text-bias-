MODEL_NAME = "vinai/phobert-base"

TRAIN_PATH = "dataset/processed_v2/train.csv"

VAL_PATH = "dataset/processed_v2/val.csv"

TEST_PATH = "dataset/processed_v2/test.csv"

CATEGORY_MAPPING_PATH = "dataset/metadata/category_mapping_v2.json"

OUTPUT_DIR = "checkpoints/phobert_severity_classifier"

MAX_LENGTH = 128

BATCH_SIZE = 16

LEARNING_RATE = 2e-5

EPOCHS = 5

# Multi-task heads are sensitive to a cold-start learning rate; a short warmup
# helps stabilize the first few hundred steps before the LR schedule kicks in.
WARMUP_RATIO = 0.1

# Assumes a 1-5 raw rating scale in the processed CSVs (values 1, 3, 4 observed
# in the one sample seen so far) -- used only to sanity-check the raw ratings
# before severity_data.derive_top2_labels() collapses them to binary presence.
# Fix this constant if the real dataset/raw_v2/ batch uses a different range.
NUM_SEVERITY_LEVELS = 5

# Caps each category's BCEWithLogitsLoss pos_weight (negatives/positives).
# Categories that are almost never in anyone's top-2 would otherwise get a
# runaway weight from a handful of positive examples, which is what destabilized
# the earlier 14-way ordinal model into collapsing to constant predictions.
MAX_POS_WEIGHT = 20.0

SEED = 42
