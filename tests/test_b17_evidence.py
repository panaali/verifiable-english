"""Batch 17 report assertions read only saved evidence, never moving Git refs."""

import json
import gzip
import hashlib
from itertools import zip_longest
from pathlib import Path
import re
import pytest

from tools import b17_ab


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/lean-first/b17/evidence"
REPORT = ROOT / "docs/lean-first/b17/REPORT.md"


def saved(name):
    return json.loads((EVIDENCE / name).read_text())


def scope_report():
    scope = saved("scope.json")
    report = REPORT.read_text()
    assert scope["range"] == "main..HEAD --no-merges"
    commits = scope["commits"]
    assert commits and scope["captured_head"] == commits[0]
    assert len(commits) == len(set(commits))
    assert all(re.fullmatch("[0-9a-f]{40}", commit) for commit in commits)
    assert all(row["commit"] in commits for row in scope["files"])
    assert "Source commits (saved): " + ", ".join(commits) in report
    return scope, report


def test_b17_report_change_metrics_from_saved_scope():
    scope, report = scope_report()
    files = scope["files"]
    totals = scope["totals"]
    assert totals == {
        "added": sum(row["added"] for row in files),
        "deleted": sum(row["deleted"] for row in files),
        "lean_added": sum(row["added"] for row in files if row["path"].endswith(".lean")),
        "python_deleted": sum(row["deleted"] for row in files if row["path"].endswith(".py")),
    }
    assert f"Total lines deleted: {totals['deleted']}" in report
    assert f"Lean lines added: {totals['lean_added']}" in report
    assert f"Python lines deleted: {totals['python_deleted']}" in report


def test_b17_report_gate_from_saved_clean_run():
    scope, report = scope_report()
    gate = saved("gate.json")
    counts = gate["counts"]
    assert gate["commit_sha"] == scope["gate_head"]
    assert gate["status"] == "passed" and gate["dirty"] is False
    assert counts["selected"] == counts["passed"] + counts["skipped"] + counts["failed"]
    assert counts["failed"] == 0 and gate["failures"] == []
    assert counts["rust_ignored"] == 0
    assert f"Earlier full gate: {counts['passed']} passed, {counts['skipped']} skipped, 0 failed" in report
    assert f"Rust: {counts['rust_passed']} passed, 0 ignored" in report
    assert gate["commit_sha"] in report


def test_b17_path_ab_covers_both_changed_paths_and_signed_budget_deltas(tmp_path):
    base = EVIDENCE / "base-paths.json"
    head = EVIDENCE / "head-paths.json"
    delta = EVIDENCE.parent / "DELTA.json"
    output = tmp_path / "comparison.json"
    assert b17_ab.compare(base, head, delta, output) == 0
    comparison = json.loads(output.read_text())
    assert comparison == saved("path-ab.json")
    assert comparison["records"] == {"assist": 18, "cedar": 2}
    assert comparison["same"] == 18 and comparison["unlisted"] == 0
    assert {(row["path"], row["case"]) for row in comparison["differences"]} == {
        ("assist", "decide/top/proof_zero"), ("assist", "decide/forall/models_zero")}
    head_rows = b17_ab.load(head)
    assert head_rows["assist", "decide/top/adequate"] == {"returned": "yes"}
    assert head_rows["assist", "decide/forall/adequate"] == {"returned": "no"}
    assert [row["decision"] for row in head_rows["cedar", "permit"]["returned"]] == ["allow", "deny"]
    assert all("returned" in outcome for outcome in head_rows.values())
    assert all("returned" in outcome for outcome in b17_ab.load(base).values())
    assert "18 assist and 2 Cedar cases" in REPORT.read_text()

    # A missing changed path or a vacuous signed list cannot be accepted.
    rows = json.loads(head.read_text())
    (tmp_path / "missing.json").write_text(json.dumps([r for r in rows if r["path"] != "cedar"]))
    with pytest.raises(ValueError, match="incomplete case matrix"):
        b17_ab.compare(base, tmp_path / "missing.json", delta, output)
    (tmp_path / "unsigned.json").write_text(json.dumps({"verdict": []}))
    assert b17_ab.compare(base, head, tmp_path / "unsigned.json", output) == 1


def test_b17_saved_head_paths_match_current_code(tmp_path):
    live = tmp_path / "head.json"
    b17_ab.child(ROOT, live)
    assert b17_ab.load(live) == b17_ab.load(EVIDENCE / "head-paths.json")


def test_b17_report_ab_from_saved_comparison():
    _, report = scope_report()
    ab = saved("ab.json")
    delta = json.loads((EVIDENCE.parent / "DELTA.json").read_text())
    unavailable_count = sum(ab["unavailable_both"].values())
    assert ab["totals"] == {"same": sum(ab["records"].values()) - unavailable_count,
                            "unavailable": unavailable_count}
    assert ab["totals"]["same"] + ab["totals"]["unavailable"] == sum(ab["records"].values())
    assert all(row["class"] == "unavailable" and row["base"] == row["head"]
               and row["listed"] for row in ab["differences"])
    assert len(ab["differences"]) == ab["totals"]["unavailable"]
    assert ab["unlisted"] == 0
    assert {tuple(row[field] for field in ("corpus", "authority", "case", "op"))
            for row in delta["unavailable"]} == {
                tuple(row[field] for field in ("corpus", "authority", "case", "op"))
                for row in ab["differences"]}
    assert all(row["reason"].strip() for row in delta["unavailable"])
    assert f"A/B: {ab['totals']['same']} identical outcomes, {ab['totals']['unavailable']} unavailable on both sides" in report
    assert f"Pilots: {ab['records']['pilots/default']} documents" in report


def test_b17_saved_ab_rows_support_the_comparison():
    ab = saved("ab.json")
    counts = {}
    unavailable = []
    with gzip.open(EVIDENCE / "base-ab.jsonl.gz", "rt") as base, \
            gzip.open(EVIDENCE / "head-ab.jsonl.gz", "rt") as head:
        for left, right in zip_longest(base, head):
            assert left is not None and right is not None
            left, right = json.loads(left), json.loads(right)
            key = tuple(left[field] for field in ("corpus", "authority", "case", "op", "source_sha256"))
            assert key == tuple(right[field] for field in ("corpus", "authority", "case", "op", "source_sha256"))
            assert left["outcome"] == right["outcome"]
            bucket = f"{left['corpus']}/{left['authority']}"
            counts[bucket] = counts.get(bucket, 0) + 1
            output = left["outcome"]
            if bucket == "pilots/default" and isinstance(output, dict):
                stdout = output.get("stdout")
                if isinstance(stdout, dict) and stdout.get("status") == "CheckerUnavailable":
                    unavailable.append(left["case"])
    assert counts == ab["records"]
    assert len(unavailable) == ab["totals"]["unavailable"]
    assert sorted(unavailable) == sorted(row["case"] for row in ab["differences"])


def test_b17_saved_pilot_rerun_explains_transient_timeout():
    initial = saved("ab-initial.json")
    rerun = saved("bluedot-rerun.json")
    case = rerun["case"]
    differences = [row for row in initial["differences"] if row["case"] == case]
    assert len(differences) == 1 and differences[0]["class"] == "availability"
    assert differences[0]["head"]["stdout"]["status"] == "CheckerUnavailable"
    assert differences[0]["base"] == rerun["outcome"]
    assert all(row["case"] != case for row in saved("ab.json")["differences"])


def test_b17_report_difffuzz_from_saved_run():
    _, report = scope_report()
    ci = saved("difffuzz-ci.json")
    assert ci["passed"] is True and ci["new"] == []
    assert ci["baseline"]["unreviewed"] == [] and ci["baseline"]["not_reproduced"] == []
    assert f"Difffuzz CI: {ci['baseline']['entries']} baseline entries, 0 new signatures" in report


def test_b17_report_date_seeds_from_saved_pairs():
    _, report = scope_report()
    rows = saved("seeds.json")["rows"]
    with gzip.open(EVIDENCE / "date-reports.json.gz", "rt") as stream:
        reports = json.load(stream)
    assert len(rows) == 14 and len({row["seed"] for row in rows}) == 14
    assert set(reports) == {row["seed"] for row in rows}
    assert all(row["head_only"] == row["base_only"] == 0
               and row["head_new"] == row["base_new"]
               and row["head_signature_sha256"] == row["base_signature_sha256"]
               for row in rows)
    for row in rows:
        for side in ("base", "head"):
            raw = reports[row["seed"]][side]
            signatures = sorted(item["signature"] for item in raw["new"])
            digest = hashlib.sha256(json.dumps(signatures).encode()).hexdigest()
            assert row[f"{side}_new"] == len(signatures)
            assert row[f"{side}_signature_sha256"] == digest
            assert row["baseline_entries"] == raw["baseline"]["entries"]
    assert f"Date seeds: {len(rows)} paired, 0 head-only signatures" in report
    assert f"{sum(row['head_new'] for row in rows)} inherited signatures" in report


def test_b17_report_seeded_failures_from_saved_runs():
    _, report = scope_report()
    entries = saved("mutants.json")["mutants"]
    assert len(entries) >= 3 and len({row["name"] for row in entries}) == len(entries)
    assert all(row["mutant"]["exit_code"] != 0 and row["mutant"]["failed_test"]
               and row["restored"]["exit_code"] == 0 for row in entries)
    assert f"Seeded mutants: {len(entries)} failed as expected" in report
    assert all(row["name"] in report for row in entries)


def test_b17_statement_check_from_saved_run():
    _, report = scope_report()
    run = saved("statement-check.json")
    assert run["exit_code"] == 0
    assert hashlib.sha256(run["output"].encode()).hexdigest() == run["output_sha256"]
    assert "added: 0\nremoved: 0\nchanged: 0\n" in run["output"]
    assert "PASS: 4422 statements" in run["output"]
    assert "4422 statements, 0 added, removed or changed" in report
