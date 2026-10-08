"""RD-6a's report (docs/readings-defaults/rd6a/DELTA.md) against its saved gate evidence.

Every number, commit and seeded bug the report states is a line rebuilt here from the saved evidence: the gate
note's committed copy (gate-note.json: `tools/gate.py`'s result, the corpus A/B comparison and the latency
measurement, as `tools/batch_evidence.py` accepted them for the gated commit), and gate-evidence.json (the Lean
checks, the statement checker, the commits from `git log main..<gated commit> --no-merges`, the tests added and the
seeded bugs). Nothing here reads git, so the test still holds after syncs with main and after the merge. Changing
any number, commit or seeded bug in the evidence makes the check fail (checklist 13 and 20).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tools.batch_evidence import problems

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/readings-defaults/rd6a/gate-evidence.json"
NOTE = ROOT / "docs/readings-defaults/rd6a/gate-note.json"
REPORT = ROOT / "docs/readings-defaults/rd6a/DELTA.md"


def _n(value: int) -> str:
    return f"{value:,}"


def expected_lines(ev: dict, note: dict) -> list[str]:
    """The report's lines that carry a number, a commit or a seeded bug, rebuilt from the evidence."""
    lean, checker = ev["lean"], ev["statement_checker"]
    later = ", ".join(f"`{name}`" for name in checker["rd6a_later"])
    amended = ", ".join(f"`{name}`" for name in checker["rd6a_amended"])
    pending = ", ".join(f"`{name}`" for name in checker["rd6a_pending"])
    lines = [f"`Build completed successfully ({lean['build_jobs']} jobs)`",
             f"PASS: {lean['audit_files']} source files, {_n(lean['audit_theorems'])} theorems",
             f"PASS ({_n(lean['statements'])} statements; RD-6a adds {lean['statements_added']}, removes "
             f"{lean['statements_removed']} and changes none)",
             f"layer graph kept ({lean['lean_modules']} modules)",
             f"RD-1: {checker['rd1_exact']} exact, {checker['rd1_pending']} pending; RD-6a: {checker['rd6a_checked']} "
             f"checked, {checker['rd6a_exact']} exact ({len(checker['rd6a_amended'])} amended by a DRI ruling"
             f"{': ' + amended if amended else ''}), {len(checker['rd6a_pending'])} pending{': ' + pending if pending else ''}, {len(checker['rd6a_later'])} not built ({later})",
             f"S +{ev['trust_map']['rd6a_S']}",
             f"Gated commit: `{ev['gated_commit']}`",
             f"at `{ev['base'][:8]}`",
             f"disk checked ({ev['disk_free_gb']} GB free before the gate)"]
    lines += [f"| `{c['sha']}` | {c['subject']} |" for c in ev["commits"]]
    lines += [f"| {b['id']} | `{b['file']}` | {b['bug']} | {b['failed']} |" for b in ev["seeded_bugs"]]
    lines += [f"| `{t['file']}` | {t['added']} |" for t in ev["tests_added"]]
    gate, counts, ab, latency = note["gate"], note["gate"]["counts"], note["corpus_ab"], note["latency"]
    lines += [f"`tools/gate.py` {gate['status']} on a clean worktree of the gated commit, stages "
              f"{', '.join(f'`{stage}`' for stage in gate['stages'])}",
              f"{_n(counts['passed'])} Python tests passed, {counts['skipped']} skipped (each on the gate's allowed "
              f"list), {counts['deselected']} deselected, {counts['failed']} failed; {counts['rust_passed']} Rust "
              f"tests passed",
              f"{_n(ab['totals']['same'])} results identical, {len(ab['differences'])} different, {ab['unlisted']} "
              f"unlisted, base `{ab['base_commit'][:8]}`"]
    lines += [f"| `{name}` | {_n(count)} |" for name, count in sorted(ab["records"].items())]
    retry = ab.get("retry")
    if retry is not None:
        lines += [f"`{retry['case']}`", retry["reason"]]
    lines += [f"| `{name}` | {row['calls_per_side']} | {row['base_cpu_ms']:.3f} | {row['head_cpu_ms']:.3f} |"
              for name, row in sorted(latency["samples"].items())]
    return lines


def mismatches(report: str, ev: dict, note: dict) -> list[str]:
    return [line for line in expected_lines(ev, note) if line not in report]


def _evidence() -> dict:
    return json.loads(EVIDENCE.read_text())


def _note() -> dict:
    return json.loads(NOTE.read_text())


def test_report_lines_come_from_the_saved_evidence():
    assert mismatches(REPORT.read_text(), _evidence(), _note()) == []


def evidence_problems(ev: dict, note: dict) -> list[str]:
    """What makes the saved evidence not a green gate on its last listed commit."""
    errors = []
    if ev["clean_worktree"] is not True:
        errors.append("gate not on a clean worktree")
    if not ev["commits"] or len(ev["gated_commit"]) != 40 or not ev["gated_commit"].startswith(ev["commits"][-1]["sha"]):
        errors.append("the gated commit is not the last listed commit")
    if not all(c["subject"].startswith("readings-defaults RD-6a: ") for c in ev["commits"]):
        errors.append("a listed commit is not an RD-6a commit")
    if ev["lean"]["statements_removed"] != 0 or ev["lean"]["statements_added"] <= 0:
        errors.append("statements removed, or none added")
    if len(ev["seeded_bugs"]) < 3 or len({b["id"] for b in ev["seeded_bugs"]}) != len(ev["seeded_bugs"]):
        errors.append("fewer than three distinct seeded bugs")
    if not ev["tests_added"]:
        errors.append("no tests added")
    # The note is the one `tools/batch_evidence.py` accepts for the gated commit: gate, corpus A/B and latency.
    errors += problems(ev["gated_commit"], note["gate"], note["corpus_ab"], note["latency"])
    if note["gate"]["counts"]["failed"] != 0 or note["corpus_ab"]["differences"] != []:
        errors.append("a failed test or a corpus difference")
    return errors


def test_saved_evidence_is_a_green_gate_on_the_last_listed_commit():
    assert evidence_problems(_evidence(), _note()) == []


def test_a_replaced_corpus_record_states_why():
    """Follow-up of rd-6a-looprecheck1: a corpus A/B record replaced by a retry carries its original outcome and the
    reason, and its source is named as what it is (a git blob ID, not a SHA-256)."""
    note = _note()
    for retry in (note["corpus_ab"].get("retry"), note.get("pilot_retry")):
        if retry is None:
            continue
        assert retry["reason"] and retry["original_outcome"]
        assert len(retry["source_git_blob"]) == 40 and "source_sha256" not in retry


def _paths(value, path=()):
    """Every number and string leaf of the evidence, by its path."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _paths(item, path + (key,))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from _paths(item, path + (i,))
    elif isinstance(value, (int, str)) and not isinstance(value, bool):
        yield path


# Leaves the report does not state: the schema and the trust map's own note.
UNSTATED = {("schema",), ("trust_map", "check")}


def _changed(value, path):
    changed = copy.deepcopy(value)
    node = changed
    for key in path[:-1]:
        node = node[key]
    old = node[path[-1]]
    node[path[-1]] = old + 1 if isinstance(old, int) else "x" + old
    return changed


def test_report_check_fails_on_every_changed_leaf():
    """One loop, not one test ID per leaf, so the collected IDs do not change with the evidence (the report commit
    after the gate changes only the report directory)."""
    ev, note, report = _evidence(), _note(), REPORT.read_text()
    paths = [p for p in _paths(ev) if p not in UNSTATED]
    assert len(paths) > 50
    assert [p for p in paths if not mismatches(report, _changed(ev, p), note)] == []


# The note's leaves the report states (the rest is the raw tool output it keeps for audit).
NOTE_STATED = [("gate", "status"), ("gate", "counts", "passed"), ("gate", "counts", "skipped"),
               ("gate", "counts", "deselected"), ("gate", "counts", "failed"), ("gate", "counts", "rust_passed"),
               ("corpus_ab", "totals", "same"), ("corpus_ab", "unlisted"), ("corpus_ab", "base_commit")]


def test_report_check_fails_on_every_changed_note_value():
    ev, note, report = _evidence(), _note(), REPORT.read_text()
    paths = NOTE_STATED + [("gate", "stages", i) for i in range(len(note["gate"]["stages"]))]
    assert [p for p in paths if not mismatches(report, ev, _changed(note, p))] == []


def test_report_check_fails_on_a_changed_corpus_count_or_latency():
    note = _note()
    for name in note["corpus_ab"]["records"]:
        changed = copy.deepcopy(note)
        changed["corpus_ab"]["records"][name] += 1
        assert mismatches(REPORT.read_text(), _evidence(), changed)
    for name in note["latency"]["samples"]:
        changed = copy.deepcopy(note)
        changed["latency"]["samples"][name]["head_cpu_ms"] += 0.01
        assert mismatches(REPORT.read_text(), _evidence(), changed)


def test_report_check_fails_on_an_empty_report_or_empty_evidence():
    ev, note = _evidence(), _note()
    assert mismatches("", ev, note)
    for key in ("commits", "seeded_bugs", "tests_added"):
        empty = copy.deepcopy(ev)
        empty[key] = []
        assert evidence_problems(empty, note)
    stale = copy.deepcopy(note)
    stale["gate"]["commit_sha"] = "b" * 40
    assert evidence_problems(ev, stale)
