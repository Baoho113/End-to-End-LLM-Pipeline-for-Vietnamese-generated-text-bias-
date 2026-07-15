"""Rebuilds dataset/processed/{train,val,test}.csv from dataset/raw/vietnamese_bias_dataset.csv.

The raw file has heavy row duplication (12,499 rows but only 4,277 unique
texts) and the previous processed split was built without deduping first,
which leaked hundreds of identical sentences across train/val/test. This
script dedupes by text, normalizes label spelling to the canonical set in
docs/annotation_guideline.md, and produces a stratified 80/10/10 split with
no overlap between splits. It also regenerates dataset/metadata/label_mapping.json
so it matches the label strings actually written to the processed CSVs.

Run from the repo root: python dataset/build_splits.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

RAW_PATH = Path("dataset/raw/vietnamese_bias_dataset.csv")
PROCESSED_DIR = Path("dataset/processed")
LABEL_MAPPING_PATH = Path("dataset/metadata/label_mapping.json")
SEED = 42

# id -> canonical label string, per docs/annotation_guideline.md section 7.
CANONICAL_LABELS = {
    0: "Non-bias",
    1: "Gender Bias",
    2: "Age Bias",
    3: "Class/Socioeconomic Bias",
    4: "Occupation Bias",
    5: "Educational Bias",
    6: "Religion/Belief Bias",
    7: "Ethnicity Bias",
    8: "Marital/Family Status Bias",
    9: "Political Bias",
    10: "Mental Health Bias",
    11: "Appearance Bias",
    12: "Regional Bias",
}

# The raw CSV uses shorthand spelling for some labels; map every raw variant
# seen in the file to its canonical form. Anything not listed here must
# already match a value in CANONICAL_LABELS (checked by _normalize_labels).
RAW_LABEL_ALIASES = {
    "non bias": "Non-bias",
    "gender": "Gender Bias",
    "Age": "Age Bias",
    "appearance": "Appearance Bias",
    "regional": "Regional Bias",
}

LABEL_TO_ID = {label: idx for idx, label in CANONICAL_LABELS.items()}


def _normalize_labels(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["label"] = df["label"].str.strip().replace(RAW_LABEL_ALIASES)
    unknown = sorted(set(df["label"]) - set(LABEL_TO_ID))
    if unknown:
        raise ValueError(f"Unrecognized label(s) in raw data: {unknown}")
    return df


def _dedupe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["text"] = df["text"].str.strip()
    before = len(df)
    df = df.drop_duplicates(subset="text", keep="first").reset_index(drop=True)
    print(f"Deduped {before} raw rows -> {len(df)} unique texts.")
    return df


def _stratified_split(df: pd.DataFrame, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_df, temp_df = train_test_split(
        df, test_size=0.2, stratify=df["label"], random_state=seed
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, stratify=temp_df["label"], random_state=seed
    )
    return (
        train_df.reset_index(drop=True),
        val_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


def _assert_no_leakage(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    train_texts = set(train_df["text"])
    val_texts = set(val_df["text"])
    test_texts = set(test_df["text"])
    overlaps = {
        "train/val": train_texts & val_texts,
        "train/test": train_texts & test_texts,
        "val/test": val_texts & test_texts,
    }
    for name, overlap in overlaps.items():
        if overlap:
            raise AssertionError(f"Leakage detected between {name}: {len(overlap)} shared texts")
    print("No leakage between splits: confirmed.")


def main() -> None:
    df = pd.read_csv(RAW_PATH, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]

    df = _normalize_labels(df)
    df = _dedupe(df)
    df["label_id"] = df["label"].map(LABEL_TO_ID)

    print("\nUnique texts per label after dedupe:")
    print(df["label"].value_counts().sort_index().to_string())

    train_df, val_df, test_df = _stratified_split(df, SEED)
    _assert_no_leakage(train_df, val_df, test_df)

    columns = ["text", "label", "bias_terms", "target_group", "severity", "safer_text", "label_id"]
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for name, split_df in [("train", train_df), ("val", val_df), ("test", test_df)]:
        out_path = PROCESSED_DIR / f"{name}.csv"
        split_df[columns].to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"Wrote {len(split_df):5d} rows -> {out_path}")

    LABEL_MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LABEL_MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump({label: idx for idx, label in CANONICAL_LABELS.items()}, f, ensure_ascii=False, indent=2)
    print(f"Wrote label mapping -> {LABEL_MAPPING_PATH}")


if __name__ == "__main__":
    main()
