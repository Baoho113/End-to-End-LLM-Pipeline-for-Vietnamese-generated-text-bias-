"""LoRA-fine-tunes Qwen2.5-1.5B-Instruct to rate Vietnamese/English text
across the 14 bias categories, instead of training a classifier from scratch.

Rationale: a from-scratch encoder classifier (PhoBERT, mDeBERTa, etc.) has to
learn the entire concept of "what sexism looks like" from ~900-2000 labeled
rows split across 14 categories -- several categories end up with single-digit
support. An instruction-tuned decoder model already has a working notion of
bias/stereotyping from its pretraining (the same reason the zero-shot prompted
approach in inference_severity_llm.py works reasonably well); fine-tuning it
only has to calibrate that existing understanding to this dataset's specific
rubric and labeling conventions, which should need much less data.

Reuses inference_severity_llm.py's category rubric (SYSTEM_PROMPT/CATEGORIES)
as the training prompt template, so the fine-tuned model and the zero-shot
Tier-1 module are directly comparable -- same instructions, same output format.

Trains with standard supervised fine-tuning: the prompt (rubric + input text)
is masked out of the loss, so only the JSON completion tokens are learned
from. LoRA + bf16 (no 4-bit quantization) keeps this within a 6GB GPU without
bitsandbytes' Windows-compatibility risk.

Run:
    python dataset/convert_labelstudio.py   (once, to build processed_v2/)
    python src/training/train_llm_lora.py   (from the repo root)
"""

import json

import pandas as pd
import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

from config_llm import (
    BATCH_SIZE,
    CATEGORY_MAPPING_PATH,
    EPOCHS,
    GRAD_ACCUMULATION_STEPS,
    LEARNING_RATE,
    LORA_ALPHA,
    LORA_DROPOUT,
    LORA_R,
    LORA_TARGET_MODULES,
    MAX_LENGTH,
    MODEL_NAME,
    NUM_SEVERITY_LEVELS,
    OUTPUT_DIR,
    TRAIN_PATH,
    VAL_PATH,
    WARMUP_RATIO,
)
from inference_severity_llm import CATEGORIES, SYSTEM_PROMPT


def load_categories() -> list[str]:
    with open(CATEGORY_MAPPING_PATH, encoding="utf-8") as f:
        cat_to_id = json.load(f)
    dataset_categories = sorted(cat_to_id, key=lambda c: cat_to_id[c])
    if set(dataset_categories) != set(CATEGORIES):
        raise ValueError(
            f"dataset/metadata/category_mapping_v2.json categories {dataset_categories} don't match "
            f"inference_severity_llm.CATEGORIES {CATEGORIES} -- the rubric and the real data have drifted "
            "apart, update one to match the other before training."
        )
    return CATEGORIES


def build_examples(tokenizer, path: str, categories: list[str]) -> list[dict]:
    df = pd.read_csv(path, encoding="utf-8-sig")
    raw_ratings = df[categories].to_numpy(dtype="int64")
    if raw_ratings.min() < 1 or raw_ratings.max() > NUM_SEVERITY_LEVELS:
        raise ValueError(
            f"Ratings out of expected 1..{NUM_SEVERITY_LEVELS} range in {path}: "
            f"min={raw_ratings.min()} max={raw_ratings.max()}. Check config_llm.NUM_SEVERITY_LEVELS."
        )

    examples = []
    for _, row in df.iterrows():
        completion = json.dumps({c: int(row[c]) for c in categories}, ensure_ascii=False)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": row["text"]},
        ]
        # apply_chat_template(tokenize=True) returns a BatchEncoding dict
        # ({"input_ids": [...], "attention_mask": [...]}), not a flat token
        # list -- pull "input_ids" out explicitly.
        prompt_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)["input_ids"]
        full_ids = tokenizer.apply_chat_template(
            messages + [{"role": "assistant", "content": completion}],
            tokenize=True,
            add_generation_prompt=False,
        )["input_ids"]

        if len(full_ids) > MAX_LENGTH:
            # Drop rather than silently truncate into the middle of the JSON
            # completion, which would teach the model to emit malformed JSON.
            print(f"Skipping a row: {len(full_ids)} tokens > MAX_LENGTH={MAX_LENGTH}")
            continue

        prompt_len = len(prompt_ids)
        labels = list(full_ids)
        labels[:prompt_len] = [-100] * prompt_len

        examples.append({"input_ids": full_ids, "labels": labels})

    return examples


class SFTCollator:
    """Dynamic padding to the batch's own max length (not a fixed MAX_LENGTH),
    since most rows are much shorter than the worst case and static padding
    would waste both memory and compute on a 6GB GPU.
    """

    def __init__(self, pad_token_id: int):
        self.pad_token_id = pad_token_id

    def __call__(self, features: list[dict]) -> dict:
        max_len = max(len(f["input_ids"]) for f in features)
        input_ids, attention_mask, labels = [], [], []
        for f in features:
            pad_len = max_len - len(f["input_ids"])
            input_ids.append(f["input_ids"] + [self.pad_token_id] * pad_len)
            attention_mask.append([1] * len(f["input_ids"]) + [0] * pad_len)
            labels.append(f["labels"] + [-100] * pad_len)
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
        }


def main():
    categories = load_categories()
    print(f"Training on {len(categories)} categories: {categories}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("Building training examples...")
    train_examples = build_examples(tokenizer, TRAIN_PATH, categories)
    val_examples = build_examples(tokenizer, VAL_PATH, categories)
    print(f"  train: {len(train_examples)} examples, val: {len(val_examples)} examples")

    train_ds = Dataset.from_list(train_examples)
    val_ds = Dataset.from_list(val_examples)

    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=torch.bfloat16).to("cuda")
    model.gradient_checkpointing_enable()
    model.config.use_cache = False

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUMULATION_STEPS,
        num_train_epochs=EPOCHS,
        warmup_ratio=WARMUP_RATIO,
        weight_decay=0.01,
        logging_steps=10,
        bf16=True,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=SFTCollator(tokenizer.pad_token_id),
    )

    trainer.train()

    # peft's save_pretrained on a LoRA-wrapped model writes only the small
    # adapter weights (a few MB), not the full 1.5B-parameter base model.
    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"Saved LoRA adapter -> {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
