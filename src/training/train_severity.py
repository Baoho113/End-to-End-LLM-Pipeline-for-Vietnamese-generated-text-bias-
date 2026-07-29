"""Trains the multi-label bias-category presence classifier on dataset/processed_v2/.

Run:
    python dataset/convert_labelstudio.py   (once, to build processed_v2/)
    python src/training/train_severity.py   (from the repo root)
"""

import pandas as pd
import torch
from datasets import Dataset
from transformers import Trainer, TrainingArguments

from config_severity import (
    BATCH_SIZE,
    EPOCHS,
    LEARNING_RATE,
    MAX_LENGTH,
    MAX_POS_WEIGHT,
    MODEL_NAME,
    NUM_SEVERITY_LEVELS,
    OUTPUT_DIR,
    TRAIN_PATH,
    VAL_PATH,
    WARMUP_RATIO,
)
from severity_data import derive_top2_labels, load_categories
from severity_metrics import compute_metrics_factory
from severity_model import PhobertSeverityClassifier, save_checkpoint
from trainer_utils import segment, tokenizer


def build_dataset(path: str, categories: list[str]) -> Dataset:
    df = pd.read_csv(path, encoding="utf-8-sig")
    segmented = [segment(t) for t in df["text"].tolist()]
    encodings = tokenizer(segmented, padding="max_length", truncation=True, max_length=MAX_LENGTH)

    raw_ratings = df[categories].to_numpy(dtype="int64")
    if raw_ratings.min() < 1 or raw_ratings.max() > NUM_SEVERITY_LEVELS:
        raise ValueError(
            f"Ratings out of expected 1..{NUM_SEVERITY_LEVELS} range in {path}: "
            f"min={raw_ratings.min()} max={raw_ratings.max()}. Check config_severity.NUM_SEVERITY_LEVELS."
        )
    labels = derive_top2_labels(df, categories)  # (N, num_categories) binary

    ds = Dataset.from_dict(
        {
            "input_ids": encodings["input_ids"],
            "attention_mask": encodings["attention_mask"],
            "labels": labels.tolist(),
        }
    )
    ds.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
    return ds


def compute_pos_weights(train_ds: Dataset, num_categories: int) -> torch.Tensor:
    """BCEWithLogitsLoss pos_weight per category: negatives/positives, capped at
    MAX_POS_WEIGHT so a category with only a handful of positive examples doesn't
    get an outsized weight that destabilizes training.
    """
    # train_ds["labels"] returns a datasets.Column, which doesn't support the
    # [:, c] indexing below -- train_ds[:]["labels"] forces the batched access
    # path, which stacks it into a proper (N, num_categories) tensor.
    labels = train_ds[:]["labels"]
    pos_weights = torch.zeros(num_categories)
    for c in range(num_categories):
        pos = labels[:, c].sum()
        neg = labels.shape[0] - pos
        pos_weights[c] = (neg / pos.clamp(min=1)).clamp(max=MAX_POS_WEIGHT)
    return pos_weights


class SeverityTrainer(Trainer):
    def __init__(self, *args, pos_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos_weights = pos_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        logits = model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])

        pos_weight = self.pos_weights.to(logits.device) if self.pos_weights is not None else None
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, labels, pos_weight=pos_weight)

        return (loss, {"logits": logits}) if return_outputs else loss


def main():
    categories = load_categories()
    num_categories = len(categories)
    print(f"Training on {num_categories} categories: {categories}")

    train_ds = build_dataset(TRAIN_PATH, categories)
    val_ds = build_dataset(VAL_PATH, categories)

    model = PhobertSeverityClassifier(MODEL_NAME, num_categories)
    pos_weights = compute_pos_weights(train_ds, num_categories)
    print(f"Per-category pos_weight (capped at {MAX_POS_WEIGHT}): {pos_weights.tolist()}")

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=EPOCHS,
        warmup_ratio=WARMUP_RATIO,
        weight_decay=0.01,
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        # Our model's forward() signature doesn't include "labels" (compute_loss
        # pops it before calling the model), so Trainer's column-pruning would
        # otherwise mistake it for an unused column and drop it. label_names
        # must be set explicitly for the same reason: Trainer infers it from
        # the model's forward signature by default, and since ours has no
        # "labels" param, it would otherwise call model(**inputs) directly
        # during eval (bypassing compute_loss) with "labels" still attached.
        remove_unused_columns=False,
        label_names=["labels"],
    )

    trainer = SeverityTrainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics_factory(categories),
        pos_weights=pos_weights,
    )

    trainer.train()
    save_checkpoint(trainer.model, tokenizer, categories, OUTPUT_DIR)


if __name__ == "__main__":
    main()
