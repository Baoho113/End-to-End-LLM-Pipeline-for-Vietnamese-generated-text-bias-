"""
run_train.py — Train the bias detector on your dataset.

Usage:
    python run_train.py

Reads:  data/vietnamese_bias_claude.csv
Saves:  models/bias_detector.pkl
"""

import os
from config import DATASET_PATH, MODEL_PATH
from evaluator import Evaluator


def main():
    if not os.path.exists(DATASET_PATH):
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        print(f"Place your CSV file in the data/ folder.")
        return

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Vietnamese Bias Detection — Training                      ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    evaluator = Evaluator(DATASET_PATH)
    results = evaluator.train_and_evaluate()

    evaluator.save_model(MODEL_PATH)

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"  Model saved:    {MODEL_PATH}")
    print(f"  Test Accuracy:  {results['accuracy']:.4f}")
    print(f"  Test F1 Macro:  {results['f1_macro']:.4f}")
    print(f"\nNext step: python run_evaluate_llm.py")


if __name__ == "__main__":
    main()
