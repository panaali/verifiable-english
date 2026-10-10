"""RD-6b report checks against committed evidence, independent of the current git graph."""

from __future__ import annotations

import copy
import gzip
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/readings-defaults/rd6b"
EVIDENCE = HERE / "evidence"


def saved():
    summary = json.loads((EVIDENCE / "summary.json").read_text())
    for name, digest in summary["sha256"].items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == digest, name
    gate = json.loads((EVIDENCE / "gate-code.json").read_text())
    comparison = json.loads((EVIDENCE / "ab-compare.json").read_text())
    delta = json.loads((EVIDENCE / "ab-delta.json").read_text())
    bench = json.loads((EVIDENCE / "latency.json").read_text())
    mutants = json.loads((EVIDENCE / "seeded-bugs.json").read_text())
    retries = json.loads(gzip.decompress((EVIDENCE / "ab-retries.json.gz").read_bytes()))
    records = {
        side: [json.loads(line) for line in gzip.decompress((EVIDENCE / f"ab-{side}.jsonl.gz").read_bytes()).splitlines()]
        for side in ("base", "head")
    }
    return summary, gate, comparison, delta, bench, mutants, retries, records


def expected_lines(summary, gate, comparison, bench, mutants):
    counts = gate["counts"]
    lean = summary["lean"]
    total = sum(comparison["records"].values())
    lines = [
        f"pinned merge-base commit `{summary['base_merge_commit']}`",
        f"`main` was `{summary['main_at_code_head']}`",
        f"Build completed successfully ({lean['build_jobs']} jobs)",
        f"PASS: {lean['audit_sources']} source files; {lean['audit_theorems']} named theorem declarations",
        f"PASS: {lean['statements']} statements; 0 added, removed or changed",
        f"{lean['rd6b_declarations']} approved declarations; 0 pending",
        f"Full gate on clean code head `{summary['code_head']}`: {counts['passed']} passed, {counts['skipped']} skipped, "
        f"{counts['failed']} failed, of {counts['collected']} collected ({counts['deselected']} live test deselected)",
        f"Rust: {counts['rust_passed']} passed, {counts['rust_ignored']} ignored",
        f"Readings and pilots: {total} records; {comparison['totals']['same']} identical; "
        f"{comparison['totals']['verdict']} route/payload differences; "
        f"{comparison['totals']['wording']} scratch-path wording differences; {comparison['unlisted']} unlisted",
        f"All {comparison['totals']['verdict']} changed pilot records",
        f"Five pilot checks hit the Rust subprocess",
    ]
    lines.extend(
        f"| `{name}` | {row['calls_per_side']} | {row['base_cpu_ms']:.3f} | {row['head_cpu_ms']:.3f} |"
        for name, row in bench["samples"].items()
    )
    lines.extend(f"| `{commit['sha'][:8]}` | {commit['subject']} |" for commit in summary["commits_before_report"])
    lines.extend(
        f"| {mutant['mutant']} | `{mutant['file']}` | `{mutant['test']}` | exit {mutant['exit_code']} |"
        for mutant in mutants
    )
    return lines


def mismatches(report, summary, gate, comparison, bench, mutants):
    return [line for line in expected_lines(summary, gate, comparison, bench, mutants) if line not in report]


def test_report_numbers_and_commit_rows_match_saved_evidence():
    summary, gate, comparison, _, bench, mutants, _, _ = saved()
    assert mismatches((HERE / "DELTA.md").read_text(), summary, gate, comparison, bench, mutants) == []
    assert gate["status"] == "passed" and gate["dirty"] is False
    assert gate["commit_sha"] == summary["code_head"] == bench["head_commit"]
    assert gate["counts"] == summary["gate_counts"]
    assert gate["counts"]["passed"] + gate["counts"]["skipped"] + gate["counts"]["failed"] == gate["counts"]["selected"]
    assert gate["counts"]["selected"] + gate["counts"]["deselected"] == gate["counts"]["collected"]
    assert gate["failures"] == []


def test_saved_commit_list_is_complete_for_the_gated_code():
    summary, *_ = saved()
    commits = summary["commits_before_report"]
    assert commits and len(commits) == len({item["sha"] for item in commits})
    assert all(re.fullmatch(r"[0-9a-f]{40}", item["sha"]) for item in commits)
    assert all(item["subject"].startswith("readings-defaults RD-6b: ") for item in commits)
    assert commits[-1]["sha"] == summary["code_head"]
    assert re.fullmatch(r"[0-9a-f]{40}", summary["base_merge_commit"])
    assert re.fullmatch(r"[0-9a-f]{40}", summary["main_at_code_head"])


def test_saved_ab_records_are_complete_and_every_delta_is_reviewed():
    summary, _, comparison, delta, _, _, retries, records = saved()
    assert comparison["records"] == summary["ab_records"] == {"pilots/default": 454, "readings/default": 1137}
    assert comparison["totals"] == summary["ab_totals"] == {"same": 1555, "verdict": 29, "wording": 7}
    assert comparison["unlisted"] == summary["ab_unlisted"] == 0
    assert len(comparison["differences"]) == 36
    assert all(len(records[side]) == 1591 for side in ("base", "head"))
    assert all({(row["corpus"], row["authority"], row["case"], row["op"]) for row in records[side]}
               == {(row["corpus"], row["authority"], row["case"], row["op"]) for row in records["base"]}
               for side in ("base", "head"))
    assert len(delta["verdict"]) == 29 and len(delta["wording"]) == 1
    assert not delta["order"] and not delta["availability"] and not delta["unavailable"]
    for difference in comparison["differences"]:
        assert difference["listed"] is True
        if difference["class"] == "verdict":
            base = difference["base"]["stdout"]["readings"]
            head = difference["head"]["stdout"]["readings"]
            assert difference["corpus"] == "pilots"
            assert (base["route"], head["route"]) == ("enumerated", "superposed")
            assert base["conflict"]["status"] == head["conflict"]["status"]
            assert {key: difference[key] for key in ("corpus", "authority", "case", "op", "base", "head")} in delta["verdict"]
        else:
            assert difference["class"] == "wording" and difference["base"]["exit"] == difference["head"]["exit"] == 1
            assert difference["base"]["stdout"] == difference["head"]["stdout"] == ""
            assert {side: difference[side]["stderr"][0] for side in ("base", "head")} in delta["wording"]
            assert all("Cannot read sense pack" in difference[side]["stderr"][0] for side in ("base", "head"))
    assert len(retries) == 5
    assert all("timed out after" in str(item["original"]) and item["retry"]["exit"] == 0 for item in retries)


def test_saved_latency_and_seeded_bugs():
    summary, _, _, _, bench, mutants, _, _ = saved()
    assert bench["pass"] is summary["latency_pass"] is True
    assert len(bench["samples"]) == 3
    assert all(row["calls_per_side"] == 500 and row["head_cpu_ms"] <= 1.2 * row["base_cpu_ms"]
               for row in bench["samples"].values())
    assert len(mutants) == summary["seeded_bugs"] == 3
    assert len({mutant["mutant"] for mutant in mutants}) == 3
    for mutant in mutants:
        assert mutant["exit_code"] != 0 and mutant["failed"] is True and "FAILED" in mutant["tail"]
        assert (ROOT / mutant["file"]).is_file()
        path, name = mutant["test"].split("::", 1)
        name = name.split("[", 1)[0]
        assert re.search(rf"^def {re.escape(name)}\(", (ROOT / path).read_text(), re.M)


def test_report_check_rejects_mutated_saved_numbers_commits_and_failures():
    summary, gate, comparison, _, bench, mutants, _, _ = saved()
    report = (HERE / "DELTA.md").read_text()
    for section, name in (("lean", "build_jobs"), ("lean", "audit_theorems"),
                          ("lean", "statements"), ("lean", "rd6b_declarations")):
        altered = copy.deepcopy(summary)
        altered[section][name] += 1
        assert mismatches(report, altered, gate, comparison, bench, mutants)
    altered = copy.deepcopy(summary)
    altered["commits_before_report"][0]["sha"] = "0" * 40
    assert mismatches(report, altered, gate, comparison, bench, mutants)
    altered = copy.deepcopy(gate)
    altered["counts"]["passed"] += 1
    assert mismatches(report, summary, altered, comparison, bench, mutants)
    altered = copy.deepcopy(comparison)
    altered["totals"]["verdict"] += 1
    assert mismatches(report, summary, gate, altered, bench, mutants)
    altered = copy.deepcopy(bench)
    first = next(iter(altered["samples"].values()))
    first["head_cpu_ms"] += 1
    assert mismatches(report, summary, gate, comparison, altered, mutants)
    altered = copy.deepcopy(mutants)
    altered[0]["exit_code"] = 0
    assert mismatches(report, summary, gate, comparison, bench, altered)
