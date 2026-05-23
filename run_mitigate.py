"""
run_mitigate.py — Run the two-stage mitigation pipeline.

Loads the trained detector, runs it on sample texts, then applies
rule-based and/or LLM-based mitigation and reports results.

Usage:
    # Rule-based only (no API key needed):
    python run_mitigate.py --no-llm

    # Full two-stage (requires API key):
    set ANTHROPIC_API_KEY=sk-ant-...
    python run_mitigate.py

    # Evaluate how much mitigation reduces bias vs baseline:
    python run_mitigate.py --compare
"""

import os
import sys
import argparse
import json

from config import MODEL_PATH, OUTPUT_DIR
from detector import BiasDetector
from mitigator import MitigationPipeline


# ── Sample texts for standalone testing ────────────────────────────────────
SAMPLE_TEXTS = [
    # gender_stereotype (severity 1-2 — rule-based should fix)
    ("Công việc điều dưỡng phù hợp với phụ nữ vì họ có bản năng chăm sóc tự nhiên.",
     "gender_stereotype"),

    # gender_stereotype (severity 3 — needs LLM)
    ("Phụ nữ không bao giờ có thể điều hành công ty lớn vì họ thiếu lý trí và tầm nhìn chiến lược.",
     "gender_stereotype"),

    # regional_bias (rule-based)
    ("Giọng miền Trung nghe khó chịu và không phù hợp làm phát thanh viên quốc gia.",
     "regional_bias"),

    # regional_bias (severe)
    ("Dân Nghệ An thực tế là ai cũng biết rằng họ thường hung hãn và khó hợp tác.",
     "regional_bias"),

    # socioeconomic (rule-based)
    ("Người không có bằng đại học thì không thể nào đóng góp ý kiến về chính sách.",
     "socioeconomic_occupation_bias"),

    # socioeconomic (severe)
    ("Người làm nghề ve chai không đáng tin cậy và không nên được giao trọng trách gì cả.",
     "socioeconomic_occupation_bias"),

    # appearance (rule-based)
    ("Nhân viên béo không nên làm ở bộ phận lễ tân vì ảnh hưởng hình ảnh công ty.",
     "appearance_derogation"),

    # appearance (severe)
    ("Da đen thì không bao giờ phù hợp làm đại diện thương hiệu mỹ phẩm cao cấp.",
     "appearance_derogation"),

    # neutral — should pass through
    ("Hội nghị về phát triển bền vững sẽ diễn ra tại Đà Nẵng vào tháng tới.",
     "neutral"),
]


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def run_mitigation(use_llm: bool, compare: bool):
    # --- Load model ---
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model not found at {MODEL_PATH}")
        print("Run 'python run_train.py' first.")
        sys.exit(1)

    print_section("Vietnamese Bias Mitigation Pipeline")
    detector = BiasDetector.load(MODEL_PATH)
    pipeline = MitigationPipeline(detector, use_llm=use_llm)

    mode = "Rule-based + LLM" if use_llm else "Rule-based only"
    print(f"\nMode: {mode}")
    if use_llm and not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY not set — LLM stage will fail gracefully.")

    # --- Step 1: Detect ---
    print_section("Step 1 — Bias Detection")
    texts = [t for t, _ in SAMPLE_TEXTS]
    detection_results = detector.predict_batch(texts)

    for dr in detection_results:
        status = "🔴 BIASED" if dr.is_biased else "🟢 CLEAN"
        print(f"\n  {status} [{dr.predicted_category}] sev={dr.severity} conf={dr.confidence:.0%}")
        print(f"  Text: {dr.text[:70]}...")

    # --- Step 2: Mitigate ---
    print_section("Step 2 — Mitigation")
    mitigation_results = pipeline.run_batch(detection_results)

    # --- Step 3: Show results ---
    print_section("Step 3 — Results")
    for orig_dr, mit_r in zip(detection_results, mitigation_results):
        if not orig_dr.is_biased:
            print(f"\n  🟢 CLEAN — passed through")
            print(f"  Text: {orig_dr.text[:70]}...")
            continue

        resolved = "✅ RESOLVED" if not mit_r.still_biased else "⚠️  STILL BIASED"
        print(f"\n  {resolved} | Stage: {mit_r.stage.upper()}")
        print(f"  Original:  {mit_r.original_text[:75]}...")
        if mit_r.changed:
            print(f"  Rewritten: {mit_r.mitigated_text[:75]}...")
        else:
            print(f"  Rewritten: (unchanged)")
        print(f"  Severity:  {mit_r.severity_before} → {mit_r.severity_after}")
        if mit_r.rules_applied:
            print(f"  Rules:     {'; '.join(mit_r.rules_applied[:2])}")

    # --- Step 4: Summary report ---
    print_section("Summary Report")
    report = pipeline.report(mitigation_results)
    biased = report["biased_inputs"]
    resolved = report["resolved"]
    rate = report["resolution_rate"]

    print(f"  Total texts:         {report['total']}")
    print(f"  Biased inputs:       {biased}")
    print(f"  Resolved:            {resolved} ({rate:.0%})")
    print(f"  Still biased:        {report['still_biased']}")
    print(f"  Avg severity before: {report['avg_severity_before']:.2f}")
    print(f"  Avg severity after:  {report['avg_severity_after']:.2f}")
    print(f"  Severity reduction:  {report['severity_reduction']:.2f}")
    print(f"  Stages used:         {report['stages_used']}")

    # --- Step 5: Compare mode ---
    if compare:
        print_section("Comparison: Baseline vs Mitigated")
        print(f"  {'Text':<45} {'Before':>10} {'After':>10} {'Stage':<12}")
        print(f"  {'-'*45} {'-'*10} {'-'*10} {'-'*12}")
        for r in mitigation_results:
            if r.severity_before > 0:
                print(
                    f"  {r.original_text[:43]:<45} "
                    f"  sev={r.severity_before}        "
                    f"  sev={r.severity_after}    "
                    f"  {r.stage}"
                )

    # --- Export ---
    output_path = os.path.join(OUTPUT_DIR, "mitigation_results.json")
    pipeline.export(mitigation_results, output_path)
    print(f"\n  Full results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Vietnamese Bias Mitigation Pipeline")
    parser.add_argument("--no-llm", action="store_true", help="Use rule-based mitigation only")
    parser.add_argument("--compare", action="store_true", help="Show before/after comparison table")
    args = parser.parse_args()

    run_mitigation(use_llm=not args.no_llm, compare=args.compare)


if __name__ == "__main__":
    main()
