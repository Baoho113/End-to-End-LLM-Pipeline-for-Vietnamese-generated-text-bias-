"""
run_evaluate_llm.py — Call an LLM API, collect outputs, evaluate for bias.

Usage:
    # Set your API key first
    export ANTHROPIC_API_KEY=sk-ant-...       # Mac/Linux
    set ANTHROPIC_API_KEY=sk-ant-...          # Windows CMD
    $env:ANTHROPIC_API_KEY="sk-ant-..."       # Windows PowerShell

    python run_evaluate_llm.py

Reads:  models/bias_detector.pkl  (trained model)
Saves:  outputs/evaluation_results.json
"""

import os
import sys

from config import MODEL_PATH, RESULTS_PATH, LLM_MODEL, LLM_MAX_TOKENS
from detector import BiasDetector
from evaluator import Evaluator
from prompts import TEST_PROMPTS


def call_llm(prompt: str) -> str:
    """
    Call the Anthropic API and return the response text.
    Swap this function to use OpenAI, Gemini, or any other LLM.
    """
    try:
        import anthropic
    except ImportError:
        print("ERROR: Install the API client first:")
        print("  pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=LLM_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def main():
    # --- Check model exists ---
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model not found at {MODEL_PATH}")
        print(f"Run 'python run_train.py' first.")
        return

    # --- Check API key ---
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...       # Mac/Linux")
        print("  set ANTHROPIC_API_KEY=sk-ant-...          # Windows CMD")
        print('  $env:ANTHROPIC_API_KEY="sk-ant-..."       # Windows PowerShell')
        return

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Vietnamese Bias Detection — LLM Evaluation                ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # --- Step 1: Load detector ---
    detector = BiasDetector.load(MODEL_PATH)

    # --- Step 2: Call LLM on each prompt ---
    print(f"\nSending {len(TEST_PROMPTS)} prompts to {LLM_MODEL}...")
    print("-" * 60)

    collected = []
    for i, item in enumerate(TEST_PROMPTS, 1):
        prompt = item["prompt"]
        probes = item["probes"]

        print(f"  [{i}/{len(TEST_PROMPTS)}] {prompt[:55]}...", end=" ", flush=True)

        try:
            output = call_llm(prompt)
            collected.append({
                "prompt": prompt,
                "probes": probes,
                "output": output,
            })
            print("OK")
        except Exception as e:
            print(f"FAILED: {e}")
            collected.append({
                "prompt": prompt,
                "probes": probes,
                "output": f"[ERROR: {e}]",
            })

    # --- Step 3: Evaluate all outputs ---
    print("\n" + "=" * 60)
    print("EVALUATING LLM OUTPUTS")
    print("=" * 60)

    outputs = [item["output"] for item in collected]
    results = detector.predict_batch(outputs)

    # --- Step 4: Print detailed results ---
    biased = []
    false_neutrals = []

    for item, result in zip(collected, results):
        if result.is_biased:
            biased.append((item, result))
        elif item["probes"] != "neutral" and not result.is_biased:
            false_neutrals.append((item, result))

    # Summary
    total = len(results)
    biased_count = len(biased)
    print(f"\n  Total outputs:    {total}")
    print(f"  Biased detected:  {biased_count} ({biased_count/total:.0%})")
    print(f"  Clean:            {total - biased_count}")

    # Category breakdown
    if biased:
        print(f"\n  Category breakdown of biased outputs:")
        from collections import Counter
        cat_counts = Counter(r.predicted_category for _, r in biased)
        for cat, count in cat_counts.most_common():
            print(f"    {cat}: {count}")

    # Per-category probe success rate
    print(f"\n  Per-category probe results:")
    from collections import defaultdict
    probe_results = defaultdict(lambda: {"total": 0, "detected": 0})
    for item, result in zip(collected, results):
        cat = item["probes"]
        probe_results[cat]["total"] += 1
        if cat == "neutral" and not result.is_biased:
            probe_results[cat]["detected"] += 1
        elif cat != "neutral" and result.is_biased:
            probe_results[cat]["detected"] += 1

    for cat, stats in sorted(probe_results.items()):
        rate = stats["detected"] / stats["total"] if stats["total"] else 0
        if cat == "neutral":
            print(f"    {cat}: {stats['detected']}/{stats['total']} correctly clean ({rate:.0%})")
        else:
            print(f"    {cat}: {stats['detected']}/{stats['total']} bias detected ({rate:.0%})")

    # Show biased examples
    if biased:
        print(f"\n  Biased output examples:")
        print("  " + "-" * 56)
        for item, result in biased[:10]:  # show first 10
            print(f"\n  Prompt:    {item['prompt'][:60]}")
            print(f"  Output:    {result.text[:80]}...")
            print(f"  Category:  {result.predicted_category}")
            print(f"  Severity:  {result.severity}/3  |  Confidence: {result.confidence:.0%}")

    # --- Step 5: Export ---
    evaluator = Evaluator.__new__(Evaluator)
    evaluator.detector = detector
    evaluator.export_results(results, RESULTS_PATH)

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"  Results saved: {RESULTS_PATH}")
    print(f"  Total prompts: {total}")
    print(f"  Biased:        {biased_count} ({biased_count/total:.0%})")


if __name__ == "__main__":
    main()
