"""Custom PhoBERT-based head for multi-label bias-category presence.

AutoModelForSequenceClassification (used by train_phobert.py) assumes one
softmax over mutually exclusive classes, which doesn't fit this task: every
bias category gets its own independent binary decision (is this text one of
its top-2 flagged categories -- see severity_data.derive_top2_labels), so a
text can be flagged on more than one category at once. This is a plain
nn.Module rather than a transformers.PreTrainedModel, so checkpoints are
saved/loaded manually via save_checkpoint()/load_checkpoint() instead of
save_pretrained()/from_pretrained().
"""

import json
from pathlib import Path

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

CONFIG_FILENAME = "severity_config.json"
WEIGHTS_FILENAME = "pytorch_model.bin"


class PhobertSeverityClassifier(nn.Module):
    def __init__(self, model_name: str, num_categories: int):
        super().__init__()
        self.model_name = model_name
        self.num_categories = num_categories
        self.encoder = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.1)
        self.head = nn.Linear(self.encoder.config.hidden_size, num_categories)

    def forward(self, input_ids, attention_mask):
        pooled = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state[:, 0]
        return self.head(self.dropout(pooled))  # (batch, num_categories) raw logits


def save_checkpoint(model: PhobertSeverityClassifier, tokenizer, categories: list[str], output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out / WEIGHTS_FILENAME)
    with open(out / CONFIG_FILENAME, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model_name": model.model_name,
                "num_categories": model.num_categories,
                "categories": categories,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    tokenizer.save_pretrained(output_dir)


def load_checkpoint(output_dir: str) -> tuple[PhobertSeverityClassifier, AutoTokenizer, list[str]]:
    out = Path(output_dir)
    with open(out / CONFIG_FILENAME, encoding="utf-8") as f:
        cfg = json.load(f)

    model = PhobertSeverityClassifier(cfg["model_name"], cfg["num_categories"])
    state_dict = torch.load(out / WEIGHTS_FILENAME, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(output_dir)
    return model, tokenizer, cfg["categories"]
