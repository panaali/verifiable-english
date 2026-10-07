"""Check that the batch report's gate and comparison counts match saved evidence."""
from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"


def read(name):
    return json.loads((EVIDENCE / name).read_text())


def main():
    report = (HERE / "DELTA.md").read_text()
    gate = read("full-gate.json")
    counts = gate["counts"]
    assert gate["status"] == "failed" and gate["dirty"] is False
    assert f"{counts['passed']:,} passed, {counts['skipped']} skipped, **{counts['failed']} failed**" in report
    assert "tests/test_difffuzz.py::test_ci_run" in report

    comparison = read("core-readings-compare.json")
    assert comparison["totals"] == {"same": 65969}
    assert f"{comparison['totals']['same']:,} identical" in report

    pilots = read("pilots-compare.json")
    assert len(pilots["differences"]) == pilots["totals"]["availability"] == 1
    assert sum(pilots["totals"].values()) == pilots["records"]["pilots/default"] == 294
    assert f"{pilots['totals']['same']} identical" in report

    seeds = read("difffuzz-14-seeds.json")
    assert len(seeds) == 14
    assert all(not row["added"] and not row["removed"] and row["same_corpus"] and
               row["same_mutants"] for row in seeds)
    ci = read("difffuzz-ci.json")
    assert ci["base_new"] == ci["head_new"] == 11 and ci["same_signature_ids"]
    assert ci["added"] == ci["removed"] == []
    assert "zero added or removed signature IDs" in report

    soft = read("soft-corpus.json")
    assert soft["accepted_trees"] == soft["environment_matches"] == soft["layer_matches"] == 1000
    assert soft["soft_background_matches"] == soft["decision_matches"] == 1000
    assert f"{soft['rejected_inputs']:,} rejected inputs" in report


if __name__ == "__main__":
    main()
    print("PASS: batch 6 report matches saved gate and comparison evidence")
