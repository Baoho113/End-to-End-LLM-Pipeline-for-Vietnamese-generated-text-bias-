"""Inference against the fine-tuned severity checkpoint: single text or a batch.

Unlike inference_test.py's single softmax label, this flags every bias
category independently (multi-label), since a text can be flagged on more
than one category at once -- see severity_data.derive_top2_labels for how
the model was trained to define "flagged."

CLI usage:
    Single line:
        python inference_severity.py "Nguoi gia thuong kho tiep thu."

    Mass score over a file (one sentence per line, or a CSV with a "text" column):
        python inference_severity.py --file sentences.txt
        python inference_severity.py --file input.csv --out results.json
"""

import argparse
import csv
import json

import torch

from config_severity import OUTPUT_DIR
from severity_model import load_checkpoint
from trainer_utils import segment

_model = None
_tokenizer = None
_categories = None


def _load():
    global _model, _tokenizer, _categories
    if _model is None:
        _model, _tokenizer, _categories = load_checkpoint(OUTPUT_DIR)
    return _model, _tokenizer, _categories


def predict(text: str) -> dict:
    return predict_batch([text])[0]


def predict_batch(texts: list[str], batch_size: int = 16) -> list[dict]:
    model, tokenizer, categories = _load()
    results = []

    for start in range(0, len(texts), batch_size):
        chunk = texts[start : start + batch_size]
        segmented = [segment(t) for t in chunk]
        inputs = tokenizer(segmented, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            logits = model(**inputs)  # (batch, num_categories)
        probs = torch.sigmoid(logits)

        for text, row in zip(chunk, probs):
            categories_out = {
                name: {
                    "flagged": bool(row[i].item() >= 0.5),
                    "confidence": round(row[i].item(), 4),
                }
                for i, name in enumerate(categories)
            }
            results.append({"text": text, "categories": categories_out})

    return results


def _read_texts(path: str) -> list[str]:
    if path.lower().endswith(".csv"):
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if "text" not in (reader.fieldnames or []):
                raise ValueError(f"{path} has no 'text' column")
            return [row["text"] for row in reader if row["text"].strip()]

    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", help="A single sentence to score")
    parser.add_argument("--file", help="Path to a .txt (one sentence per line) or .csv (with a 'text' column) to mass-score")
    parser.add_argument("--out", help="Write results to this JSON file instead of printing them (only with --file)")
    args = parser.parse_args()

    if args.file:
        texts = _read_texts(args.file)
        results = predict_batch(texts)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Wrote {len(results)} results -> {args.out}")
        else:
            print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        text = args.text or "Nguoi gia thuong kho tiep thu."
        print(json.dumps(predict(text), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
