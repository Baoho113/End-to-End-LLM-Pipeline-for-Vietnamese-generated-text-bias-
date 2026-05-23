"""
evaluator.py — Training, cross-validation, and batch evaluation.

Classes:
  Evaluator — Orchestrates the full train → evaluate → export workflow.
"""

import json

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

from config import (
    BIAS_LABELS, TEST_SIZE, CROSS_VAL_FOLDS,
    SVM_C, SVM_MAX_ITER, CALIBRATION_CV, RANDOM_STATE,
)
from detector import BiasDetector, DetectionResult


class Evaluator:
    """
    End-to-end evaluation pipeline.

    Handles:
      - Loading and splitting the dataset
      - Training the detector
      - Cross-validation
      - Held-out test evaluation
      - Batch evaluation of new AI-generated texts
      - Report generation and export
    """

    def __init__(self, dataset_path: str, test_size: float = TEST_SIZE):
        self.dataset_path = dataset_path
        self.test_size = test_size
        self.detector = BiasDetector()
        self.results = None

    def load_data(self):
        """Load and split dataset into train/test."""
        df = pd.read_csv(self.dataset_path)
        df = df.dropna(subset=["text", "label"])
        df = df[df["label"].isin(BIAS_LABELS)]

        X_train, X_test, y_train, y_test = train_test_split(
            df["text"].tolist(),
            df["label"].tolist(),
            test_size=self.test_size,
            random_state=RANDOM_STATE,
            stratify=df["label"].tolist(),
        )
        print(f"Dataset loaded: {len(df)} samples")
        print(f"  Train: {len(X_train)}  |  Test: {len(X_test)}")
        print(f"  Labels: {df['label'].value_counts().to_dict()}")
        return X_train, X_test, y_train, y_test

    def cross_validate(self, texts, labels, cv=CROSS_VAL_FOLDS):
        """Run cross-validation and report mean F1."""
        print(f"\nRunning {cv}-fold cross-validation...")
        processed = self.detector.preprocessor.process_batch(texts)
        X = self.detector.feature_engine.fit_transform(processed)

        base_clf = CalibratedClassifierCV(
            LinearSVC(
                C=SVM_C, class_weight="balanced",
                max_iter=SVM_MAX_ITER, random_state=RANDOM_STATE,
            ),
            cv=CALIBRATION_CV, method="sigmoid",
        )

        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=RANDOM_STATE)
        f1_scores = cross_val_score(base_clf, X, labels, cv=skf, scoring="f1_macro")
        print(f"  Cross-val F1 (macro): {f1_scores.mean():.4f} ± {f1_scores.std():.4f}")
        return f1_scores

    def train_and_evaluate(self):
        """Full train → evaluate workflow."""
        X_train, X_test, y_train, y_test = self.load_data()

        # Cross-validate
        self.cross_validate(X_train, y_train)

        # Train on full training set
        print("\n" + "=" * 60)
        print("TRAINING ON FULL TRAINING SET")
        print("=" * 60)
        self.detector.train(X_train, y_train)

        # Evaluate on held-out test set
        print("\n" + "=" * 60)
        print("EVALUATING ON HELD-OUT TEST SET")
        print("=" * 60)
        results = self.detector.predict_batch(X_test)
        y_pred = [r.predicted_category for r in results]

        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, digits=4, zero_division=0))

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=BIAS_LABELS)
        cm_df = pd.DataFrame(cm, index=BIAS_LABELS, columns=BIAS_LABELS)
        print("Confusion Matrix:")
        print(cm_df.to_string())

        # Summary metrics
        f1_macro = f1_score(y_test, y_pred, average="macro")
        f1_weighted = f1_score(y_test, y_pred, average="weighted")
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nOverall Accuracy:  {accuracy:.4f}")
        print(f"Macro F1:          {f1_macro:.4f}")
        print(f"Weighted F1:       {f1_weighted:.4f}")

        # Severity distribution
        print("\nSeverity Distribution (test set predictions):")
        sev_counts = pd.Series([r.severity for r in results]).value_counts().sort_index()
        for sev, count in sev_counts.items():
            pct = count / len(results) * 100
            bar = "█" * int(pct / 2)
            print(f"  Severity {sev}: {count:>3} ({pct:5.1f}%) {bar}")

        # Bias detection rate
        bias_rate = sum(1 for r in results if r.is_biased) / len(results)
        print(f"\nBias Detection Rate: {bias_rate:.1%}")

        self.results = {
            "test_results": results,
            "y_test": y_test,
            "y_pred": y_pred,
            "accuracy": accuracy,
            "f1_macro": f1_macro,
            "f1_weighted": f1_weighted,
            "confusion_matrix": cm_df,
        }
        return self.results

    def evaluate_new_texts(self, texts: list[str]) -> list[DetectionResult]:
        """
        Evaluate a batch of new texts using the trained model.

        This is the primary interface for offline LLM evaluation:
          1. Generate Vietnamese text from your LLM
          2. Collect the outputs
          3. Pass them here
          4. Get per-text bias scores + aggregate metrics
        """
        assert self.detector.is_trained, "Train the model first with train_and_evaluate()."

        print(f"\nEvaluating {len(texts)} new texts...")
        results = self.detector.predict_batch(texts)

        biased = [r for r in results if r.is_biased]
        print(f"  Total:    {len(results)}")
        print(f"  Biased:   {len(biased)} ({len(biased)/len(results):.1%})")
        print(f"  Clean:    {len(results) - len(biased)}")

        if biased:
            print(f"\n  Category breakdown:")
            cat_counts = pd.Series([r.predicted_category for r in biased]).value_counts()
            for cat, count in cat_counts.items():
                print(f"    {cat}: {count}")

            print(f"\n  Severity breakdown:")
            sev_counts = pd.Series([r.severity for r in biased]).value_counts().sort_index()
            for sev, count in sev_counts.items():
                print(f"    Severity {sev}: {count}")

        return results

    def export_results(self, results: list[DetectionResult], path: str):
        """Export results to JSON for the developer dashboard."""
        output = {
            "total": len(results),
            "biased_count": sum(1 for r in results if r.is_biased),
            "bias_rate": round(
                sum(1 for r in results if r.is_biased) / len(results), 4
            ),
            "avg_severity": round(
                float(np.mean([r.severity for r in results])), 2
            ),
            "category_distribution": pd.Series(
                [r.predicted_category for r in results]
            ).value_counts().to_dict(),
            "severity_distribution": {
                str(k): int(v) for k, v in
                pd.Series([r.severity for r in results])
                .value_counts().sort_index().items()
            },
            "results": [r.to_dict() for r in results],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\nResults exported to {path}")

    def save_model(self, path: str):
        """Save the trained detector."""
        self.detector.save(path)

    @classmethod
    def load_and_evaluate(cls, model_path: str, texts: list[str]) -> list[DetectionResult]:
        """Load a saved model and evaluate new texts (no retraining)."""
        evaluator = cls.__new__(cls)
        evaluator.detector = BiasDetector.load(model_path)
        return evaluator.evaluate_new_texts(texts)
