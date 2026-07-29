"""Evaluates the severity checkpoint on dataset/processed_v2/test.csv.

Mirrors evaluate.py's per-category breakdown, but each of the ~14 categories
gets its own binary precision/recall/F1 (flagged vs. not, per
severity_data.derive_top2_labels), since a text can be flagged on more than
one category at once (unlike the single-label model's one-of-13 classification).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import classification_report

from config_severity import OUTPUT_DIR, TEST_PATH, TRAIN_PATH, VAL_PATH
from severity_data import derive_top2_labels
from severity_model import load_checkpoint
from trainer_utils import segment

METRICS_PATH = Path(OUTPUT_DIR) / "eval_metrics.json"


def main():
    model, tokenizer, categories = load_checkpoint(OUTPUT_DIR)

    df = pd.read_csv(TEST_PATH, encoding="utf-8-sig")
    segmented = [segment(t) for t in df["text"].tolist()]
    inputs = tokenizer(segmented, return_tensors="pt", padding=True, truncation=True)

    with torch.no_grad():
        logits = model(**inputs)  # (N, num_categories)
    preds = (torch.sigmoid(logits) >= 0.5).int().numpy()
    labels = derive_top2_labels(df, categories).astype(int)

    per_category = []
    f1s = []
    for i, name in enumerate(categories):
        report = classification_report(
            labels[:, i],
            preds[:, i],
            labels=[0, 1],
            target_names=["not_flagged", "flagged"],
            zero_division=0,
            output_dict=True,
        )
        f1s.append(report["flagged"]["f1-score"])
        per_category.append(
            {
                "category": name,
                "precision": round(report["flagged"]["precision"], 4),
                "recall": round(report["flagged"]["recall"], 4),
                "f1": round(report["flagged"]["f1-score"], 4),
                "support": int(report["flagged"]["support"]),
            }
        )

    exact_match = float(np.mean(np.all(preds == labels, axis=1)))

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "train": len(pd.read_csv(TRAIN_PATH, encoding="utf-8-sig")),
            "val": len(pd.read_csv(VAL_PATH, encoding="utf-8-sig")),
            "test": len(df),
        },
        "overall": {
            "macro_f1_across_categories": round(float(np.mean(f1s)), 4),
            "exact_match": round(exact_match, 4),
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
