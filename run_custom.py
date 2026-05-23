"""
run_custom.py — Evaluate and mitigate any Vietnamese text you type.

Three ways to use:

  1. Interactive mode (type texts one by one):
       python run_custom.py

  2. Pass text directly as argument:
       python run_custom.py --text "Phụ nữ không nên làm giám đốc."

  3. Pass a plain .txt file (one sentence per line):
       python run_custom.py --file my_texts.txt

  Add --mitigate to also run mitigation on biased outputs:
       python run_custom.py --mitigate
       python run_custom.py --text "..." --mitigate
       python run_custom.py --file my_texts.txt --mitigate

  Add --export to save results to outputs/custom_results.json:
       python run_custom.py --mitigate --export
"""

import os
import sys
import json
import argparse
from datetime import datetime

from config import MODEL_PATH, OUTPUT_DIR
from detector import BiasDetector
from mitigator import MitigationPipeline


# ── Formatting helpers ──────────────────────────────────────────────────────

SEVERITY_LABELS = {0: "none", 1: "mild", 2: "moderate", 3: "severe"}
SEVERITY_COLORS = {0: "🟢", 1: "🟡", 2: "🟠", 3: "🔴"}
CATEGORY_SHORT = {
    "neutral":                        "neutral",
    "gender_stereotype":              "gender",
    "regional_bias":                  "regional",
    "socioeconomic_occupation_bias":  "socioeconomic",
    "appearance_derogation":          "appearance",
}

def divider(char="─", width=62):
    print(char * width)

def print_detection(result, index=None):
    prefix = f"[{index}] " if index is not None else ""
    icon = SEVERITY_COLORS[result.severity]
    sev_label = SEVERITY_LABELS[result.severity]
    cat = CATEGORY_SHORT.get(result.predicted_category, result.predicted_category)

    print(f"\n  {prefix}{icon}  {result.text}")
    if result.is_biased:
        print(f"       Category:   {cat}")
        print(f"       Severity:   {result.severity}/3 ({sev_label})")
        print(f"       Confidence: {result.confidence:.0%}")
        print(f"       All scores: " + "  ".join(
            f"{CATEGORY_SHORT.get(k,k)}={v:.0%}"
            for k, v in sorted(result.probabilities.items(), key=lambda x: -x[1])
        ))
    else:
        print(f"       Clean — confidence {result.confidence:.0%}")

def print_mitigation(mit_result):
    if not mit_result.changed:
        print(f"       Mitigation: no change (LLM disabled or rules insufficient)")
        return
    resolved = "✅ resolved" if not mit_result.still_biased else "⚠️  still biased"
    print(f"       Mitigation: [{mit_result.stage}] {resolved}")
    print(f"       Severity:   {mit_result.severity_before} → {mit_result.severity_after}")
    print(f"       Rewritten:  {mit_result.mitigated_text}")
    if mit_result.rules_applied:
        print(f"       Rules:      {'; '.join(mit_result.rules_applied[:2])}")


# ── Core evaluation function ────────────────────────────────────────────────

def evaluate_texts(
    texts: list[str],
    detector: BiasDetector,
    pipeline: MitigationPipeline | None,
    mitigate: bool,
    export: bool,
):
    texts = [t.strip() for t in texts if t.strip()]
    if not texts:
        print("No texts to evaluate.")
        return

    print(f"\n  Evaluating {len(texts)} text(s)...\n")
    divider()

    detection_results = detector.predict_batch(texts)
    mitigation_results = []

    if mitigate and pipeline:
        mitigation_results = pipeline.run_batch(detection_results)

    for i, dr in enumerate(detection_results):
        print_detection(dr, index=i + 1)
        if mitigate and mitigation_results:
            print_mitigation(mitigation_results[i])

    # Summary
    divider()
    biased = [r for r in detection_results if r.is_biased]
    print(f"\n  Summary: {len(biased)}/{len(detection_results)} biased")
    if biased:
        from collections import Counter
        cats = Counter(r.predicted_category for r in biased)
        for cat, count in cats.most_common():
            print(f"    {CATEGORY_SHORT.get(cat, cat)}: {count}")

    if mitigate and mitigation_results:
        resolved = sum(1 for r in mitigation_results if r.severity_before > 0 and not r.still_biased)
        still = sum(1 for r in mitigation_results if r.still_biased)
        print(f"\n  Mitigation: {resolved} resolved, {still} still biased")

    # Export
    if export:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(OUTPUT_DIR, f"custom_results_{timestamp}.json")

        output = {
            "timestamp": timestamp,
            "total": len(detection_results),
            "biased_count": len(biased),
            "detection": [r.to_dict() for r in detection_results],
            "mitigation": [r.to_dict() for r in mitigation_results] if mitigation_results else [],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n  Exported → {path}")


# ── Interactive mode ────────────────────────────────────────────────────────

def interactive_mode(detector, pipeline, mitigate):
    print("\n  Type Vietnamese text and press Enter to evaluate.")
    print("  Type 'quit' or press Ctrl+C to exit.\n")
    divider()

    while True:
        try:
            text = input("\n  Text: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Goodbye.")
            break

        if text.lower() in ("quit", "exit", "q", ""):
            print("\n  Goodbye.")
            break

        evaluate_texts([text], detector, pipeline, mitigate=mitigate, export=False)


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate custom Vietnamese text for bias.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_custom.py
  python run_custom.py --text "Phụ nữ không nên làm giám đốc."
  python run_custom.py --file my_texts.txt --mitigate --export
        """,
    )
    parser.add_argument("--text", type=str, help="Single text to evaluate")
    parser.add_argument("--file", type=str, help="Path to .txt file (one sentence per line)")
    parser.add_argument("--mitigate", action="store_true", help="Run mitigation on biased outputs")
    parser.add_argument("--no-llm", action="store_true", help="Rule-based mitigation only (no API)")
    parser.add_argument("--export", action="store_true", help="Export results to outputs/ as JSON")
    args = parser.parse_args()

    # --- Load model ---
    if not os.path.exists(MODEL_PATH):
        print(f"\nERROR: Model not found at {MODEL_PATH}")
        print("Run 'python run_train.py' first.")
        sys.exit(1)

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  Vietnamese Bias Detector — Custom Text Evaluation         ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    detector = BiasDetector.load(MODEL_PATH)
    pipeline = None
    if args.mitigate:
        use_llm = not args.no_llm
        pipeline = MitigationPipeline(detector, use_llm=use_llm)
        mode = "detect + mitigate (rule-based + LLM)" if use_llm else "detect + mitigate (rule-based only)"
        if use_llm and not os.environ.get("ANTHROPIC_API_KEY"):
            print("\n  WARNING: ANTHROPIC_API_KEY not set — LLM stage will be skipped.")
    else:
        mode = "detect only"

    print(f"\n  Mode:  {mode}")
    print(f"  Model: {MODEL_PATH}")

    # --- Route to mode ---
    if args.text:
        evaluate_texts([args.text], detector, pipeline, args.mitigate, args.export)
    elif args.file:
        if not os.path.exists(args.file):
            print(f"\nERROR: File not found: {args.file}")
            sys.exit(1)
        with open(args.file, encoding="utf-8") as f:
            texts = [line.strip() for line in f if line.strip()]
        print(f"\n  Loaded {len(texts)} lines from {args.file}")
        evaluate_texts(texts, detector, pipeline, args.mitigate, args.export)
    else:
        interactive_mode(detector, pipeline, args.mitigate)


if __name__ == "__main__":
    main()
