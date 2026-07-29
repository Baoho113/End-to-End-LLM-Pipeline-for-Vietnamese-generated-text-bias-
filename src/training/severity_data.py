"""Shared label logic for the severity pipeline: turns the raw 1..N per-category
severity ratings in dataset/processed_v2/*.csv into a multi-label binary presence
target, so both train_severity.py and evaluate_severity.py derive labels the same
way.

Rationale: rating every one of ~14 categories on every sample means most
categories are "1" (no bias) for most rows -- any given sentence is usually only
biased along one or two axes. Treating this as a 14-way independent 5-level
ordinal regression starves most categories of positive signal and collapses to
constant predictions in practice. Collapsing to "is this text neutral, and if
not, which up to two categories are its primary bias types" mirrors how the
original single-label PhoBERT model was framed (one primary category), relaxed
to two, and gives each category head a much simpler binary decision.
"""

import json

import numpy as np
import pandas as pd

from config_severity import CATEGORY_MAPPING_PATH


def load_categories() -> list[str]:
    with open(CATEGORY_MAPPING_PATH, encoding="utf-8") as f:
        cat_to_id = json.load(f)
    return sorted(cat_to_id, key=lambda c: cat_to_id[c])


def derive_top2_labels(df: pd.DataFrame, categories: list[str]) -> np.ndarray:
    """Collapses raw 1..N severity ratings into (N, num_categories) binary labels.

    A sample with every category rated 1 is neutral (all-zero row). Otherwise,
    the top-2 highest-rated categories are flagged positive (ties broken by
    category order, via a stable sort); every other category -- including any
    3rd+ ranked category that's also rated above 1 -- is a hard negative.
    """
    ratings = df[categories].to_numpy(dtype="int64")
    labels = np.zeros_like(ratings, dtype="float32")

    for i, row in enumerate(ratings):
        if (row <= 1).all():
            continue
        top2 = np.argsort(-row, kind="stable")[:2]
        for idx in top2:
            if row[idx] > 1:
                labels[i, idx] = 1.0

    return labels
