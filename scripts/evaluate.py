"""Evaluate local extraction against 20 synthetic, explicitly labelled examples.

Includes difficult cases to expose limitations. Not an independent benchmark.
"""
import json
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from njia.engine import extract_skills, vocabulary


def main():
    fixtures = json.loads((ROOT / "tests/fixtures/cvs.json").read_text(encoding="utf-8"))
    vocabulary()  # Report warm extraction time, excluding corpus startup.
    results, durations = [], []
    tp = fp = fn = 0
    for item in fixtures:
        start = time.perf_counter()
        actual = set(extract_skills(item["text"]))
        durations.append((time.perf_counter() - start) * 1000)
        expected = set(item["skills"])
        tp += len(actual & expected)
        fp += len(actual - expected)
        fn += len(expected - actual)
        results.append({"id": item["id"], "expected": sorted(expected), "actual": sorted(actual), "false_positives": sorted(actual-expected), "false_negatives": sorted(expected-actual)})
    report = {
        "samples": len(fixtures), "true_positives": tp, "false_positives": fp, "false_negatives": fn,
        "precision": round(tp/(tp+fp), 4), "recall": round(tp/(tp+fn), 4),
        "exact_matches": sum(r["expected"] == r["actual"] for r in results),
        "warm_median_ms": round(statistics.median(durations), 2), "warm_max_ms": round(max(durations), 2),
        "inference_api_calls": 0, "inference_api_cost_usd": 0,
        "limitations": "Small synthetic developer-authored set, not independent validation. Local lexicon extraction; no LLM. Deliberately includes ambiguity, implication, and retrospective negation.",
        "results": results,
    }
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
