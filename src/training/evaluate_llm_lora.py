"""Evaluates the LoRA-fine-tuned Qwen2.5 severity model on
dataset/processed_v2/test.csv. Unlike a classification head, a generative
model can't be scored from teacher-forced logits alone -- this actually
generates a completion per test row (via inference_llm_lora.predict_batch)
and parses it, so it's slower than the earlier classifier eval scripts but
measures what the model actually produces at inference time.

Reports per-category precision/recall/F1 against the raw 1-5 ratings (exact
match per category, not the binary top-2 collapse the earlier from-scratch
classifiers needed) since a fine-tuned generative model doesn't need that
simplification to survive data scarcity the way a from-scratch head did.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report

from config_llm import NUM_SEVERITY_LEVELS, OUTPUT_DIR, TEST_PATH, TRAIN_PATH, VAL_PATH
from inference_llm_lora import predict_batch
from inference_severity_llm import CATEGORIES

METRICS_PATH = Path(OUTPUT_DIR) / "eval_metrics.json"


def main():
    df = pd.read_csv(TEST_PATH, encoding="utf-8-sig")
    texts = df["text"].tolist()
    true_ratings = df[CATEGORIES].to_numpy(dtype="int64")

    print(f"Generating predictions for {len(texts)} test rows...")
    results = predict_batch(texts)
    pred_ratings = np.array(
        [[results[i]["categories"][c]["rating"] for c in CATEGORIES] for i in range(len(texts))]
    )

    level_labels = list(range(1, NUM_SEVERITY_LEVELS + 1))
    per_category = []
    f1s = []
    exact_matches = []
    for i, name in enumerate(CATEGORIES):
        report = classification_report(
            true_ratings[:, i],
            pred_ratings[:, i],
            labels=level_labels,
            zero_division=0,
            output_dict=True,
        )
        f1s.append(report["macro avg"]["f1-score"])
        per_category.append(
            {
                "category": name,
                "macro_precision": round(report["macro avg"]["precision"], 4),
                "macro_recall": round(report["macro avg"]["recall"], 4),
                "macro_f1": round(report["macro avg"]["f1-score"], 4),
                "exact_match_rate": round(float(np.mean(true_ratings[:, i] == pred_ratings[:, i])), 4),
                "support": len(texts),
            }
        )
        exact_matches.append(true_ratings[:, i] == pred_ratings[:, i])

    all_categories_exact_match = float(np.mean(np.all(np.stack(exact_matches, axis=1), axis=1)))

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "Qwen2.5-1.5B-Instruct + LoRA",
        "dataset": {
            "train": len(pd.read_csv(TRAIN_PATH, encoding="utf-8-sig")),
            "val": len(pd.read_csv(VAL_PATH, encoding="utf-8-sig")),
            "test": len(df),
        },
        "overall": {
            "macro_f1_across_categories": round(float(np.mean(f1s)), 4),
            "all_categories_exact_match": round(all_categories_exact_match, 4),
        },
        "per_category": per_category,
    }

    print(json.dumps(snapshot, ensure_ascii=False, indent=2))

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"\nWrote metrics snapshot -> {METRICS_PATH}")


if __name__ == "__main__":
    main()
