"""
detector.py — Bias classifier with calibrated probabilities and severity scoring.

Classes:
  DetectionResult  — Structured output for a single prediction.
  BiasDetector     — Train, predict, save, and load the bias model.
"""

from dataclasses import dataclass, field, asdict

import joblib
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

from config import (
    SEVERITY_MAP, CONFIDENCE_LOW, CONFIDENCE_HIGH,
    SVM_C, SVM_MAX_ITER, CALIBRATION_CV, RANDOM_STATE,
)
from preprocessor import Preprocessor
from feature_engine import TfidfFeatureEngine


# ---------------------------------------------------------------------------
# Detection result
# ---------------------------------------------------------------------------

@dataclass
class DetectionResult:
    """Output of the bias detector for a single text."""
    text: str
    preprocessed: str
    predicted_category: str
    severity: int
    confidence: float
    probabilities: dict = field(default_factory=dict)
    is_biased: bool = False

    def __post_init__(self):
        self.is_biased = self.predicted_category != "neutral"

    def to_dict(self):
        return asdict(self)


# ---------------------------------------------------------------------------
# Bias detector
# ---------------------------------------------------------------------------

class BiasDetector:
    """
    Multi-class bias classifier with severity scoring.

    Uses LinearSVC + CalibratedClassifierCV to produce
    well-calibrated probability estimates for threshold routing.
    """

    def __init__(self):
        self.preprocessor = Preprocessor(remove_stopwords=False)
        self.feature_engine = TfidfFeatureEngine()
        self.classifier = CalibratedClassifierCV(
            LinearSVC(
                C=SVM_C,
                class_weight="balanced",
                max_iter=SVM_MAX_ITER,
                random_state=RANDOM_STATE,
            ),
            cv=CALIBRATION_CV,
            method="sigmoid",
        )
        self.is_trained = False
        self.label_classes = None

    def train(self, texts: list[str], labels: list[str]):
        """Train the full pipeline on labeled data."""
        print("[1/3] Preprocessing texts...")
        processed = self.preprocessor.process_batch(texts)

        print("[2/3] Extracting features...")
        X = self.feature_engine.fit_transform(processed)

        print("[3/3] Training classifier...")
        self.classifier.fit(X, labels)
        self.label_classes = self.classifier.classes_.tolist()
        self.is_trained = True
        print(f"      Training complete. Classes: {self.label_classes}")
        return self

    def predict(self, text: str) -> DetectionResult:
        """Predict bias category and severity for a single text."""
        assert self.is_trained, "Model must be trained before prediction."

        processed = self.preprocessor.process(text)
        X = self.feature_engine.transform([processed])

        predicted = self.classifier.predict(X)[0]
        proba = self.classifier.predict_proba(X)[0]

        prob_dict = {
            label: round(float(p), 4)
            for label, p in zip(self.label_classes, proba)
        }
        confidence = float(max(proba))

        # Severity scoring with confidence adjustment
        severity = SEVERITY_MAP.get(predicted, 1)
        if predicted != "neutral" and confidence < CONFIDENCE_LOW:
            severity = max(1, severity - 1)
        elif predicted != "neutral" and confidence > CONFIDENCE_HIGH:
            severity = min(3, severity + 1)

        return DetectionResult(
            text=text,
            preprocessed=processed,
            predicted_category=predicted,
            severity=severity,
            confidence=confidence,
            probabilities=prob_dict,
        )

    def predict_batch(self, texts: list[str]) -> list[DetectionResult]:
        """Predict on a batch of texts."""
        return [self.predict(t) for t in texts]

    def save(self, path: str):
        """Save trained model to disk."""
        joblib.dump({
            "preprocessor": self.preprocessor,
            "feature_engine": self.feature_engine,
            "classifier": self.classifier,
            "label_classes": self.label_classes,
        }, path)
        print(f"Model saved to {path}")

    @classmethod
    def load(cls, path: str) -> "BiasDetector":
        """Load a trained model from disk."""
        data = joblib.load(path)
        detector = cls()
        detector.preprocessor = data["preprocessor"]
        detector.feature_engine = data["feature_engine"]
        detector.classifier = data["classifier"]
        detector.label_classes = data["label_classes"]
        detector.is_trained = True
        print(f"Model loaded from {path}")
        return detector
