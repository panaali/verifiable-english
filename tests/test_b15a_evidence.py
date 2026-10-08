"""Recompute batch 15a report numbers from frozen artifacts, never live Git."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parents[1] / "docs/lean-first/b15a"
EVIDENCE = HERE / "evidence"


def saved(name: str):
    return json.loads((EVIDENCE / name).read_text())


def test_saved_commit_list_and_line_totals_match_frozen_numstat():
    snapshot = saved("change-metrics.json")
    assert re.fullmatch(r"[0-9a-f]{40}\.\.[0-9a-f]{40} --no-merges", snapshot["range"])
    assert snapshot["range"] == (snapshot["base"] + ".." + snapshot["implementation_head"]
                                 + " --no-merges")
    assert len(snapshot["commits"]) == len(set(snapshot["commits"])) >= 2
    assert all(re.fullmatch(r"[0-9a-f]{40}", c) for c in snapshot["commits"])
    assert snapshot["commits"][-1] == snapshot["implementation_head"]
    files = snapshot["files"]
    assert len(files) == len({f["path"] for f in files})
    totals = snapshot["totals"]
    assert totals["added"] == sum(f["added"] for f in files)
    assert totals["deleted"] == sum(f["deleted"] for f in files)
    assert totals["lean_added"] == sum(f["added"] for f in files if f["path"].endswith(".lean"))
    assert totals["lean_deleted"] == sum(f["deleted"] for f in files if f["path"].endswith(".lean"))
    assert totals["python_decision_deleted"] == sum(
        f["deleted"] for f in files if f["path"].startswith("ve/") and f["path"].endswith(".py"))
    assert totals["rust_deleted"] == sum(
        f["deleted"] for f in files if f["path"].startswith("rust/") and f["path"].endswith(".rs"))
    report = (HERE / "REPORT.md").read_text()
    for label, value in (("Lean lines added", totals["lean_added"]),
                         ("Total lines deleted", totals["deleted"]),
                         ("Python decision lines deleted", totals["python_decision_deleted"])):
        assert f"{label}: **{value}**" in report
    assert all(c[:8] in report for c in snapshot["commits"])
    statements = (EVIDENCE / "statement-diff.txt").read_text()
    additions = [line for line in statements.splitlines() if line.startswith("  ")]
    assert f"added: {len(additions)}" in statements
    assert "removed: 0" in statements and "changed: 0" in statements
    assert f"{len(additions)} added statements" in report


def test_saved_corpus_rows_and_pilot_count_match_raw_recordings():
    records = saved("ab-recordings.json")
    raw_hashes = []
    for side in ("base-ab", "head-ab"):
        digest = hashlib.sha256()
        rows = 0
        size = 0
        with gzip.open(EVIDENCE / f"{side}.jsonl.gz", "rb") as stream:
            for line in stream:
                json.loads(line)
                digest.update(line)
                size += len(line)
                rows += 1
        assert {"bytes": size, "rows": rows, "sha256": digest.hexdigest()} == records[side]
        raw_hashes.append(digest.hexdigest())
    assert raw_hashes[0] == raw_hashes[1]
    comparison = saved("ab-compare.json")
    assert comparison["differences"] == [] and comparison["unlisted"] == 0
    assert comparison["unavailable_both"] == {}
    assert sum(comparison["records"].values()) == records["head-ab"]["rows"]
    assert comparison["totals"]["same"] == records["head-ab"]["rows"]
    assert comparison["records"]["pilots/default"] > 0
    report = (HERE / "REPORT.md").read_text()
    assert f"{records['head-ab']['rows']:,}/{records['head-ab']['rows']:,}" in report
    assert f"{comparison['records']['pilots/default']} historical pilot rows" in report
    binaries = saved("service-hashes.json")
    assert binaries["base"] == binaries["head"]
    assert re.fullmatch(r"[0-9a-f]{64}", binaries["head"])
    assert binaries["head"] in (HERE / "REPORT.md").read_text()


def test_saved_fuzz_baseline_and_mutant_failures():
    ci = saved("difffuzz-head-ci.json")
    assert ci["new"] == [] and ci["baseline"]["unreviewed"] == []
    assert ci["baseline"]["not_reproduced"] == []
    comparison = saved("difffuzz-ab.json")
    assert comparison["all_equal"] is True
    assert len(comparison["runs"]) == 15
    assert {row["run"] for row in comparison["runs"] if row["run"].startswith("--deep")} == {
        f"--deep 1 --seed 202609{day}" for day in range(23, 31)
    } | {f"--deep 1 --seed 202610{day:02d}" for day in range(1, 7)}
    assert {row["run"] for row in comparison["runs"] if not row["run"].startswith("--deep")} == {"--ci"}
    assert all(row["equal"] and row["same_new"] and row["findings_equal"]
               and row["new"][1] <= row["new"][0] for row in comparison["runs"])
    mutants = (EVIDENCE / "mutants.txt").read_text()
    for section in ("count", "trace", "nonvacuity"):
        part = mutants.split("## " + section + "\n", 1)[1].split("\n## ", 1)[0]
        assert "build exit: 0; focused pytest exit: 1" in part
        assert "FAILED tests/test_metered_lean.py::" in part
    assert "clean build exit: 0; focused pytest exit: 0" in mutants
    restored = mutants.split("## restored\n", 1)[1]
    completed = re.search(r"(\d+) passed", restored)
    assert completed is not None
    assert f"{completed.group(1)} tests" in (HERE / "REPORT.md").read_text()


def test_saved_full_gate_counts_and_clean_head():
    gate = saved("full-gate.json")
    assert gate["status"] == "passed" and gate["dirty"] is False
    assert gate["commit_sha"] == saved("change-metrics.json")["implementation_head"]
    assert gate["failures"] == []
    counts = gate["counts"]
    assert counts["selected"] == counts["passed"] + counts["failed"] + counts["skipped"]
    assert counts["collected"] == counts["selected"] + counts["deselected"]
    assert counts["failed"] == 0 and counts["rust_passed"] > 0
    report = (HERE / "REPORT.md").read_text()
    assert f"{counts['passed']} passed" in report
    assert f"{counts['skipped']} skipped" in report
