"""RD-3's report against committed evidence, with no read of the current git graph.

The commit list was saved from ``main..HEAD --no-merges`` before the report commit.
Reading it from evidence keeps this test valid after a sync or merge moves ``main``.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/readings-defaults/rd3"


def saved():
    evidence = json.loads((HERE / "evidence/summary.json").read_text())
    comparison_bytes = (HERE / "evidence/ab-compare.json").read_bytes()
    assert hashlib.sha256(comparison_bytes).hexdigest() == evidence["ab_sha256"]
    for side in ("base", "head"):
        record = (HERE / f"evidence/ab-{side}.jsonl.gz").read_bytes()
        assert hashlib.sha256(record).hexdigest() == evidence["ab_record_sha256"][side]
    comparison = json.loads(comparison_bytes)
    mutants = json.loads((HERE / "evidence/code-mutants.json").read_text())
    return evidence, comparison, mutants


def expected_lines(evidence, comparison, mutants):
    lean = evidence["lean"]
    lines = [
        f"from `main` at `{evidence['base']}`",
        f"Build completed successfully ({lean['build_jobs']} jobs)",
        f"PASS: {lean['audit_sources']} source files; {lean['audit_theorems']} named theorem declarations",
        f"PASS: {lean['statements']} Lean statements, none changed or removed",
        f"{lean['rd3_declarations']} exact RD-3 declarations",
        f"{evidence['fixtures']['passed']} passed",
        f"{sum(comparison['records'].values())} records; {comparison['totals']['same']} identical; "
        f"{comparison['totals']['wording']} scratch-path wording differences; "
        f"{comparison['unlisted']} unlisted; {sum(comparison['unavailable_both'].values())} unavailable on both sides",
    ]
    lines.extend(f"| `{c['sha']}` | {c['subject']} |" for c in evidence["commits_before_report"])
    lines.extend(f"| {m['id']} | `{m['file']}` | `{m['test']}` | exit {m['exit_code']} |" for m in mutants)
    return lines


def mismatches(report, evidence, comparison, mutants):
    return [line for line in expected_lines(evidence, comparison, mutants) if line not in report]


def test_report_numbers_and_commit_list_match_saved_evidence():
    evidence, comparison, mutants = saved()
    assert mismatches((HERE / "DELTA.md").read_text(), evidence, comparison, mutants) == []


def test_saved_commit_list_is_complete_for_the_gated_code():
    evidence, _, _ = saved()
    commits = evidence["commits_before_report"]
    assert commits and len(commits) == len({c["sha"] for c in commits})
    assert all(re.fullmatch(r"[0-9a-f]{8}", c["sha"]) for c in commits)
    assert all(c["subject"].startswith("readings-defaults RD-3: ") for c in commits)
    assert evidence["code_head"].startswith(commits[-1]["sha"])
    assert re.fullmatch(r"[0-9a-f]{40}", evidence["code_head"])


def test_saved_ab_evidence_is_complete_and_accounted():
    _, comparison, _ = saved()
    assert comparison["records"]["readings/default"] == 1137
    assert comparison["records"]["pilots/default"] > 0
    assert comparison["unlisted"] == 0
    assert (comparison["totals"]["same"] + comparison["totals"]["wording"]
            + sum(comparison["unavailable_both"].values()) == sum(comparison["records"].values()))
    assert not any(d["class"] in ("verdict", "order", "availability") for d in comparison["differences"])
    for difference in comparison["differences"]:
        if difference["class"] == "wording":
            assert difference["base"]["exit"] == difference["head"]["exit"] == 1
            assert difference["base"]["stdout"] == difference["head"]["stdout"] == ""
            assert all("Cannot read sense pack" in value["stderr"][0]
                       for value in (difference["base"], difference["head"]))


def test_saved_mutants_failed_real_tests_and_were_removed():
    _, _, mutants = saved()
    assert len(mutants) >= 3 and len(mutants) == len({m["id"] for m in mutants})
    for mutant in mutants:
        assert mutant["exit_code"] != 0 and "FAILED" in mutant["output"]
        path, name = mutant["test"].split("::", 1)
        name = name.split("[", 1)[0]
        assert re.search(rf"^def {re.escape(name)}\(", (ROOT / path).read_text(), re.M)
        assert (ROOT / mutant["file"]).exists()


def test_saved_lean_mutants_were_rejected_by_the_proofs():
    mutants = json.loads((HERE / "evidence/lean-mutants.json").read_text())
    assert {m["id"] for m in mutants} == {"L1", "L2", "L3"}
    report = (HERE / "DELTA.md").read_text()
    for mutant in mutants:
        assert mutant["exit_code"] != 0 and mutant["errors"] > 0
        assert "error: build failed" in mutant["output"]
        assert (f"| {mutant['id']} | `{mutant['file']}` | {mutant['behavior']} | "
                f"{mutant['errors']} errors |") in report


def test_saved_s2_fixtures_have_identical_public_verdicts_and_english():
    base = json.loads((HERE / "evidence/s2-base.json").read_text())
    head = json.loads((HERE / "evidence/s2-head.json").read_text())
    assert set(base) == {"M8", "M9", "M12"}
    assert base == head
    assert "M8, M9 and M12: identical verdicts and English" in (HERE / "DELTA.md").read_text()


def test_saved_latency_samples_are_within_the_existing_route_budget():
    record = json.loads((HERE / "evidence/latency.json").read_text())
    assert record["pass"] is True and len(record["samples"]) == 3
    report = (HERE / "DELTA.md").read_text()
    for name, row in record["samples"].items():
        assert (f"| `{name}` | {row['calls_per_side']} | {row['base_cpu_ms']:.3f} | "
                f"{row['head_cpu_ms']:.3f} |") in report


def test_report_check_rejects_changed_saved_numbers_and_commits():
    evidence, comparison, mutants = saved()
    report = (HERE / "DELTA.md").read_text()
    for path in (("lean", "build_jobs"), ("lean", "audit_theorems"),
                 ("lean", "statements"), ("fixtures", "passed")):
        altered = copy.deepcopy(evidence)
        altered[path[0]][path[1]] += 1
        assert mismatches(report, altered, comparison, mutants)
    altered = copy.deepcopy(evidence)
    altered["commits_before_report"][0]["sha"] = "00000000"
    assert mismatches(report, altered, comparison, mutants)
    altered = copy.deepcopy(comparison)
    altered["totals"]["same"] += 1
    assert mismatches(report, evidence, altered, mutants)
    altered = copy.deepcopy(mutants)
    altered[0]["exit_code"] += 1
    assert mismatches(report, evidence, comparison, altered)


def test_round3_mutants_were_rejected_and_reported():
    """Round 3 (DRI directive rd-3-fix3): each Lean mutant broke a proof, named in the report; each Python mutant
    failed tests that exist; the report's table rows are the saved ones."""
    mutants = json.loads((HERE / "evidence/round3-mutants.json").read_text())
    report = (HERE / "DELTA.md").read_text()
    statements = (ROOT / "lean/statements.txt").read_text()
    assert {m["id"] for m in mutants} == {"L4", "L5", "L6", "L7", "L8", "L9", "P1", "P2", "P3"}
    for mutant in mutants:
        assert mutant["exit_code"] != 0 and (ROOT / mutant["file"]).exists()
        if mutant["id"].startswith("L"):
            assert mutant["errors"] > 0 and mutant["first_error"].startswith("VE/Readings/VerdictsWire.lean:")
            assert re.search(rf"^theorem VE\.Readings(?:\.Run)?\.{re.escape(mutant['theorem'])}$", statements, re.M)
            assert (f"| {mutant['id']} | `{mutant['file']}` | {mutant['behavior']} | `{mutant['theorem']}` | "
                    f"{mutant['errors']} errors |") in report
        else:
            assert mutant["failed"]
            for test in mutant["failed"]:
                path, name = test.split("::", 1)
                assert re.search(rf"^def {re.escape(name.split('[', 1)[0])}\(", (ROOT / path).read_text(), re.M)
            assert f"| {mutant['id']} | `{mutant['file']}` | {mutant['behavior']} | {len(mutant['failed'])} failed |" \
                in report
