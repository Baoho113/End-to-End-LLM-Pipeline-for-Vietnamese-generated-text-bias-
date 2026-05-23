"""
mitigator.py — Orchestrator for two-stage bias mitigation pipeline.

Routing logic:
  severity 0          → pass through (no mitigation needed)
  severity 1–2        → Stage 1: rule-based rewrite
                         └─ re-run detector
                            ├─ still biased → Stage 2: LLM rewrite
                            └─ clean        → return rule-based result
  severity 3          → skip rules, go straight to Stage 2: LLM rewrite

Usage:
    from mitigator import MitigationPipeline
    from detector import BiasDetector, DetectionResult

    detector = BiasDetector.load("models/bias_detector.pkl")
    pipeline = MitigationPipeline(detector)

    result = pipeline.run("Phụ nữ không nên làm giám đốc.", "gender_stereotype", severity=2)
    print(result.mitigated_text)
    print(result.stage)
"""

import json
from dataclasses import dataclass, field

from mitigator_rules import RuleBasedMitigator, MitigationResult
from mitigator_llm import LLMMitigator


# ═══════════════════════════════════════════════════════════════════════════
#  Extended result — includes before/after detection scores
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class FullMitigationResult:
    """Complete record of one mitigation run."""
    original_text: str
    mitigated_text: str
    category: str
    severity_before: int
    severity_after: int
    confidence_before: float
    confidence_after: float
    stage: str                         # "none" | "rule_based" | "llm_rewrite" | "both"
    rules_applied: list[str] = field(default_factory=list)
    changed: bool = False
    still_biased: bool = False

    def __post_init__(self):
        self.changed = self.original_text.strip() != self.mitigated_text.strip()

    def to_dict(self):
        return {
            "original_text": self.original_text,
            "mitigated_text": self.mitigated_text,
            "category": self.category,
            "severity_before": self.severity_before,
            "severity_after": self.severity_after,
            "confidence_before": round(self.confidence_before, 4),
            "confidence_after": round(self.confidence_after, 4),
            "stage": self.stage,
            "rules_applied": self.rules_applied,
            "changed": self.changed,
            "still_biased": self.still_biased,
        }

    def summary(self) -> str:
        arrow = "→"
        return (
            f"[{self.stage.upper()}] "
            f"sev {self.severity_before}{arrow}{self.severity_after} | "
            f"conf {self.confidence_before:.0%}{arrow}{self.confidence_after:.0%} | "
            f"{'✓ resolved' if not self.still_biased else '⚠ still biased'}"
        )


# ═══════════════════════════════════════════════════════════════════════════
#  Mitigation pipeline
# ═══════════════════════════════════════════════════════════════════════════

class MitigationPipeline:
    """
    Two-stage mitigation orchestrator.

    Args:
        detector:        Trained BiasDetector instance for re-evaluation.
        use_llm:         Enable Stage 2 LLM rewriting (requires API key).
        llm_model:       Which Anthropic model to use for LLM rewriting.
    """

    def __init__(self, detector, use_llm: bool = True, llm_model: str = "claude-sonnet-4-20250514"):
        self.detector = detector
        self.rule_mitigator = RuleBasedMitigator()
        self.llm_mitigator = LLMMitigator(model=llm_model) if use_llm else None
        self.use_llm = use_llm

    def run(
        self,
        text: str,
        category: str,
        severity: int,
        confidence: float = 1.0,
    ) -> FullMitigationResult:
        """
        Run the full two-stage mitigation on a single text.

        Args:
            text:       The biased Vietnamese text.
            category:   Detected bias category.
            severity:   Detected severity (0–3).
            confidence: Detector confidence score.

        Returns:
            FullMitigationResult with before/after metrics.
        """
        original = text
        severity_before = severity
        confidence_before = confidence
        stage = "none"
        rules_applied = []

        # --- Severity 0: nothing to do ---
        if severity == 0:
            after = self.detector.predict(text)
            return FullMitigationResult(
                original_text=original,
                mitigated_text=text,
                category=category,
                severity_before=severity_before,
                severity_after=after.severity,
                confidence_before=confidence_before,
                confidence_after=after.confidence,
                stage="none",
            )

        # --- Severity 1–2: try rules first ---
        if severity <= 2:
            rule_result = self.rule_mitigator.mitigate(text, category)
            rules_applied = rule_result.rules_applied
            stage = "rule_based"

            # Re-evaluate after rule-based rewrite
            after = self.detector.predict(rule_result.mitigated_text)

            # If still biased and LLM is available → escalate
            if after.is_biased and self.use_llm and self.llm_mitigator:
                print(f"  Rules insufficient (still biased at sev {after.severity}), escalating to LLM...")
                llm_result = self.llm_mitigator.mitigate(
                    rule_result.mitigated_text,
                    category,
                    severity=after.severity,
                    original_text=original,
                )
                after2 = self.detector.predict(llm_result.mitigated_text)
                stage = "both"
                return FullMitigationResult(
                    original_text=original,
                    mitigated_text=llm_result.mitigated_text,
                    category=category,
                    severity_before=severity_before,
                    severity_after=after2.severity,
                    confidence_before=confidence_before,
                    confidence_after=after2.confidence,
                    stage=stage,
                    rules_applied=rules_applied + llm_result.rules_applied,
                    still_biased=after2.is_biased,
                )

            return FullMitigationResult(
                original_text=original,
                mitigated_text=rule_result.mitigated_text,
                category=category,
                severity_before=severity_before,
                severity_after=after.severity,
                confidence_before=confidence_before,
                confidence_after=after.confidence,
                stage=stage,
                rules_applied=rules_applied,
                still_biased=after.is_biased,
            )

        # --- Severity 3: skip rules, go straight to LLM ---
        if self.use_llm and self.llm_mitigator:
            print(f"  Severity 3 — sending directly to LLM rewriter...")
            llm_result = self.llm_mitigator.mitigate(text, category, severity=3)
            after = self.detector.predict(llm_result.mitigated_text)
            return FullMitigationResult(
                original_text=original,
                mitigated_text=llm_result.mitigated_text,
                category=category,
                severity_before=severity_before,
                severity_after=after.severity,
                confidence_before=confidence_before,
                confidence_after=after.confidence,
                stage="llm_rewrite",
                rules_applied=llm_result.rules_applied,
                still_biased=after.is_biased,
            )

        # Fallback: LLM disabled, severity 3 — return original with warning
        after = self.detector.predict(text)
        return FullMitigationResult(
            original_text=original,
            mitigated_text=text,
            category=category,
            severity_before=severity_before,
            severity_after=after.severity,
            confidence_before=confidence_before,
            confidence_after=after.confidence,
            stage="none",
            rules_applied=["LLM disabled — severity 3 text returned unchanged"],
            still_biased=True,
        )

    def run_batch(self, detection_results: list) -> list[FullMitigationResult]:
        """
        Run mitigation on a list of DetectionResult objects from the detector.

        Args:
            detection_results: List of DetectionResult from detector.predict_batch()

        Returns:
            List of FullMitigationResult, one per input.
        """
        results = []
        biased = [r for r in detection_results if r.is_biased]
        print(f"\nRunning mitigation on {len(biased)}/{len(detection_results)} biased texts...")

        for i, dr in enumerate(detection_results):
            if not dr.is_biased:
                # Pass-through for clean texts
                results.append(FullMitigationResult(
                    original_text=dr.text,
                    mitigated_text=dr.text,
                    category=dr.predicted_category,
                    severity_before=0,
                    severity_after=0,
                    confidence_before=dr.confidence,
                    confidence_after=dr.confidence,
                    stage="none",
                ))
                continue

            print(f"\n  [{i+1}/{len(detection_results)}] {dr.text[:60]}...")
            result = self.run(
                text=dr.text,
                category=dr.predicted_category,
                severity=dr.severity,
                confidence=dr.confidence,
            )
            print(f"  {result.summary()}")
            results.append(result)

        return results

    def report(self, results: list[FullMitigationResult]) -> dict:
        """Generate a summary report from batch mitigation results."""
        biased_results = [r for r in results if r.severity_before > 0]
        resolved = [r for r in biased_results if not r.still_biased]
        still_biased = [r for r in biased_results if r.still_biased]

        stage_counts = {}
        for r in biased_results:
            stage_counts[r.stage] = stage_counts.get(r.stage, 0) + 1

        avg_sev_before = (
            sum(r.severity_before for r in biased_results) / len(biased_results)
            if biased_results else 0
        )
        avg_sev_after = (
            sum(r.severity_after for r in biased_results) / len(biased_results)
            if biased_results else 0
        )

        return {
            "total": len(results),
            "biased_inputs": len(biased_results),
            "resolved": len(resolved),
            "still_biased": len(still_biased),
            "resolution_rate": round(len(resolved) / len(biased_results), 4) if biased_results else 1.0,
            "avg_severity_before": round(avg_sev_before, 2),
            "avg_severity_after": round(avg_sev_after, 2),
            "severity_reduction": round(avg_sev_before - avg_sev_after, 2),
            "stages_used": stage_counts,
            "results": [r.to_dict() for r in results],
        }

    def export(self, results: list[FullMitigationResult], path: str):
        """Export full mitigation report to JSON."""
        report = self.report(results)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nMitigation report exported to {path}")
