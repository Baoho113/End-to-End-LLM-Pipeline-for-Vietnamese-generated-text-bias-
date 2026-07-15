"""Evaluates the fine-tuned checkpoint on the held-out test set.

Reports the full metric set docs/evaluation_plan.md asks for (accuracy,
precision, recall, macro F1, weighted F1, confusion matrix) plus a
per-class breakdown, since macro F1 alone hides which classes are weak.
"""

import json

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from transformers import AutoModelForSequenceClassification, Trainer

from config import OUTPUT_DIR, TEST_PATH
from metrics import compute_metrics
from trainer_utils import load_csv, tokenize

COLUMNS_TO_DROP = ["text", "label", "bias_terms", "target_group", "severity", "safer_text"]


def load_test_split():
    ds = load_csv(TEST_PATH)
    ds = ds.map(tokenize, batched=True)
    ds = ds.rename_column("label_id", "labels")
    ds = ds.remove_columns([c for c in COLUMNS_TO_DROP if c in ds.column_names])
    ds.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
    return ds


def main():
    model = AutoModelForSequenceClassification.from_pretrained(OUTPUT_DIR)
    id_to_label = model.config.id2label
    label_names = [id_to_label[i] for i in range(len(id_to_label))]

    test_ds = load_test_split()
    trainer = Trainer(model=model, compute_metrics=compute_metrics)
    output = trainer.predict(test_ds)

    preds = np.argmax(output.predictions, axis=-1)
    labels = output.label_ids

    print(classification_report(labels, preds, target_names=label_names, zero_division=0))

    cm = confusion_matrix(labels, preds)
    print("\nConfusion matrix (rows = true, cols = predicted):")
    header = "".join(f"{name[:10]:>12}" for name in label_names)
    print(f"{'':>22}{header}")
    for i, row in enumerate(cm):
        row_str = "".join(f"{v:>12}" for v in row)
        print(f"{label_names[i][:20]:>22}{row_str}")

    metrics = {k: float(v) for k, v in output.metrics.items()} if output.metrics else {}
    print("\nAggregate metrics:", json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
