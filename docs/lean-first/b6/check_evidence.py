"""Check that the batch report's gate, comparison and latency figures match saved evidence."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVIDENCE = HERE / "evidence"
_spec = importlib.util.spec_from_file_location("lean_first_b6_latency", HERE / "report.py")
latency = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(latency)


def read(name):
    return json.loads((EVIDENCE / name).read_text())


def check_gate(text):
    """The full-gate row states the saved gate record's counts, or says it is still pending."""
    if "| Full offline gate on clean head | Pending" in text:
        return
    gate = read("full-gate.json")
    counts = gate["counts"]
    assert gate["status"] == "passed" and gate["dirty"] is False and counts["failed"] == 0, gate["status"]
    assert f"Commit `{gate['commit_sha'][:8]}`" in text
    assert f"{counts['passed']:,} passed, {counts['skipped']} skipped, 0 failed" in text
    assert f"Rust {counts['rust_passed']} passed" in text


def main():
    text = (HERE / "DELTA.md").read_text()
    check_gate(text)

    comparison = read("core-readings-compare.json")
    assert comparison["totals"] == {"same": 65969}
    assert f"{comparison['totals']['same']:,} identical" in text

    pilots = read("pilots-compare.json")
    assert pilots["differences"] == [] and pilots["unlisted"] == 0
    assert pilots["totals"] == {"same": pilots["records"]["pilots/default"]} == {"same": 294}
    assert f"**{pilots['totals']['same']} identical**" in text

    seeds = read("difffuzz-14-seeds.json")
    assert len(seeds) == 14
    assert all(not row["added"] and not row["removed"] and row["same_corpus"] and
               row["same_mutants"] for row in seeds)
    assert "zero added or removed signature IDs" in text
    ci = read("difffuzz-ci.json")
    assert ci["base_new"] == ci["head_new"] == len(ci["signatures"]) == ci["reviewed_with_reason"] == 11
    assert ci["same_signature_ids"] and ci["added"] == ci["removed"] == [] and ci["head_new_after_review"] == 0
    baseline = json.loads((ROOT / "conformance/difffuzz-baseline.json").read_text())["entries"]
    reviewed = [e for e in baseline if e["signature"] in ci["signatures"]]
    assert len(baseline) == ci["baseline_entries_after_review"] and len(reviewed) == 11
    assert all(e.get("reason") and e["follow_up"].startswith("DF-") for e in reviewed)
    assert f"({ci['baseline_entries_after_review']} entries)" in text

    soft = read("soft-corpus.json")
    assert soft["accepted_trees"] == soft["environment_matches"] == soft["layer_matches"] == 1000
    assert soft["soft_background_matches"] == soft["decision_matches"] == 1000
    assert f"{soft['rejected_inputs']:,} rejected inputs" in text

    begin, end = latency.BEGIN, latency.END
    assert text.split(begin, 1)[1].split(end, 1)[0] == latency.render()
    summary = latency.summary()
    assert summary["identical"]
    assert summary["max_ratio"] <= latency.CPU_RATIO_LIMIT and summary["max_head_wall"] < latency.PILOT_WALL_LIMIT
    assert f"largest UDHR CPU ratio {summary['max_ratio']:.2f}" in text
    assert f"the slowest head run took {summary['max_head_wall']:.2f} s wall" in text
    before = read("timings.json")
    assert before["after_fix"] == "udhr-timing.json"
    for key in ("base_wall_seconds", "head_wall_seconds"):
        assert f"{before['before_fix']['udhr_large'][key]:.2f} s" in text


if __name__ == "__main__":
    main()
    print("PASS: batch 6 report matches saved gate, comparison and latency evidence")
