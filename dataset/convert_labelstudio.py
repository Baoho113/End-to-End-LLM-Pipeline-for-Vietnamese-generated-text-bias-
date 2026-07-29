"""Converts dataset/raw_v2/*.json (Label Studio VNFairness task exports) into
dataset/processed_v2/{train,val,test}.csv for multi-label severity training.

Each JSON file is one task: a human_input/model_output pair rated across N
bias categories on an ordinal severity scale (see DATASET_CARD.md). The
single predictions[0].result block is the adjudicated gold annotation for
this export -- despite the Label Studio key name "predictions", it is not a
raw pre-label to second-guess (confirmed with the data owner).

Only uid_lang == "*_vi" tasks are kept (the model stays Vietnamese-only,
matching the base PhoBERT checkpoint), and tasks with sys_ref != "n000"
(attention checks / calibration anchors) are dropped -- they're synthetic
QC probes, not organic training examples.

The category set is discovered from the data itself (every "<prefix>_score"
rating field, prefix stripped) rather than hardcoded, so this script doesn't
silently drift from whatever categories the real batch actually contains.

Splits are grouped by uid, not by row: each task produces two rows (one for
human_input, one for model_output), and both must land in the same split or
a held-out split could leak related content from a task also seen in train.

Run from the repo root: python dataset/convert_labelstudio.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

RAW_DIR = Path("dataset/raw_v2")
PROCESSED_DIR = Path("dataset/processed_v2")
CATEGORY_MAPPING_PATH = Path("dataset/metadata/category_mapping_v2.json")
SEED = 42

RATING_SUFFIX = "_score"


def _category_from_field(from_name: str, prefix: str) -> str | None:
    if not from_name.startswith(prefix) or not from_name.endswith(RATING_SUFFIX):
        return None
    return from_name[len(prefix) : -len(RATING_SUFFIX)]


def _parse_task(path: Path) -> dict | None:
    with open(path, encoding="utf-8") as f:
        task = json.load(f)

    data = task["data"]
    uid_lang = data["uid_lang"]
    if not uid_lang.endswith("_vi"):
        return None
    if data.get("sys_ref", "n000") != "n000":
        return None

    predictions = task.get("predictions") or []
    if not predictions:
        return None
    result = predictions[0]["result"]

    human_scores: dict[str, int] = {}
    model_scores: dict[str, int] = {}
    human_reasoning = ""
    model_reasoning = ""
    for entry in result:
        from_name = entry["from_name"]
        if entry["type"] == "rating":
            rating = entry["value"]["rating"]
            cat = _category_from_field(from_name, "human_")
            if cat is not None:
                human_scores[cat] = rating
                continue
            cat = _category_from_field(from_name, "model_")
            if cat is not None:
                model_scores[cat] = rating
        elif entry["type"] == "textarea":
            text = " ".join(entry["value"].get("text", []))
            if from_name == "human_reasoning":
                human_reasoning = text
            elif from_name == "model_reasoning":
                model_reasoning = text

    return {
        "uid": data["uid"],
        "uid_lang": uid_lang,
        "human_input": data["human_input"],
        "model_output": data["model_output"],
        "human_scores": human_scores,
        "model_scores": model_scores,
        "human_reasoning": human_reasoning,
        "model_reasoning": model_reasoning,
    }


def _load_tasks() -> list[dict]:
    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"{RAW_DIR} does not exist -- populate it with the VNFairness task JSON files first."
        )
    paths = sorted(RAW_DIR.glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"No .json files found in {RAW_DIR}.")

    tasks = []
    skipped_filtered = 0
    skipped_errors = 0
    for path in paths:
        try:
            task = _parse_task(path)
        except (KeyError, IndexError, TypeError) as exc:
            print(f"Skipping {path.name}: malformed task ({exc})")
            skipped_errors += 1
            continue
        if task is None:
            skipped_filtered += 1
            continue
        tasks.append(task)

    print(
        f"Loaded {len(tasks)} tasks from {len(paths)} files "
        f"({skipped_filtered} filtered out [non-VI language / QC task / no predictions], "
        f"{skipped_errors} skipped due to malformed JSON)."
    )
    return tasks


def _category_set(tasks: list[dict]) -> list[str]:
    categories: set[str] = set()
    for task in tasks:
        categories.update(task["human_scores"])
        categories.update(task["model_scores"])
    if not categories:
        raise ValueError("No rating categories found across any task -- check the JSON schema.")
    return sorted(categories)


def _rows_for_task(task: dict, categories: list[str]) -> list[dict] | None:
    rows = []
    for source, text, scores, reasoning in (
        ("human_input", task["human_input"], task["human_scores"], task["human_reasoning"]),
        ("model_output", task["model_output"], task["model_scores"], task["model_reasoning"]),
    ):
        missing = [c for c in categories if c not in scores]
        if missing:
            print(f"Skipping uid={task['uid']} ({source}): missing ratings for {missing}")
            return None
        row = {
            "uid": task["uid"],
            "uid_lang": task["uid_lang"],
            "source": source,
            "text": text.strip(),
            "reasoning": reasoning,
        }
        row.update({c: scores[c] for c in categories})
        rows.append(row)
    return rows


def _group_split(df: pd.DataFrame, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_idx, temp_idx = next(
        GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed).split(df, groups=df["uid"])
    )
    train_df = df.iloc[train_idx].reset_index(drop=True)
    temp_df = df.iloc[temp_idx].reset_index(drop=True)

    val_idx, test_idx = next(
        GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=seed).split(temp_df, groups=temp_df["uid"])
    )
    val_df = temp_df.iloc[val_idx].reset_index(drop=True)
    test_df = temp_df.iloc[test_idx].reset_index(drop=True)
    return train_df, val_df, test_df


def _assert_no_leakage(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    train_uids, val_uids, test_uids = set(train_df["uid"]), set(val_df["uid"]), set(test_df["uid"])
    overlaps = {
        "train/val": train_uids & val_uids,
        "train/test": train_uids & test_uids,
        "val/test": val_uids & test_uids,
    }
    for name, overlap in overlaps.items():
        if overlap:
            raise AssertionError(f"Leakage detected between {name}: {len(overlap)} shared task uids")
    print("No leakage between splits (grouped by uid): confirmed.")


def main() -> None:
    tasks = _load_tasks()
    categories = _category_set(tasks)
    print(f"Found {len(categories)} rating categories: {categories}")

    rows = []
    for task in tasks:
        task_rows = _rows_for_task(task, categories)
        if task_rows is not None:
            rows.extend(task_rows)

    df = pd.DataFrame(rows)
    print(f"Built {len(df)} rows from {df['uid'].nunique()} tasks (human_input + model_output).")

    train_df, val_df, test_df = _group_split(df, SEED)
    _assert_no_leakage(train_df, val_df, test_df)

    columns = ["uid", "uid_lang", "source", "text", "reasoning"] + categories
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for name, split_df in [("train", train_df), ("val", val_df), ("test", test_df)]:
        out_path = PROCESSED_DIR / f"{name}.csv"
        split_df[columns].to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"Wrote {len(split_df):5d} rows -> {out_path}")

    CATEGORY_MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CATEGORY_MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump({cat: idx for idx, cat in enumerate(categories)}, f, ensure_ascii=False, indent=2)
    print(f"Wrote category mapping -> {CATEGORY_MAPPING_PATH}")


if __name__ == "__main__":
    main()
