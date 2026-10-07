"""RD-6a's report (docs/readings-defaults/rd6a/DELTA.md) against its saved gate evidence (gate-evidence.json).

Every number, commit and seeded bug the report states is a line rebuilt here from the saved evidence, which was
written from the gate's logs on the gated commit and from `git log main..<gated commit> --no-merges` at that time.
Nothing here reads git, so the test still holds after syncs with main and after the merge. Changing any number,
commit or seeded bug in the evidence makes the check fail (checklist 13 and 20).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/readings-defaults/rd6a/gate-evidence.json"
REPORT = ROOT / "docs/readings-defaults/rd6a/DELTA.md"


def _n(value: int) -> str:
    return f"{value:,}"


def expected_lines(ev: dict) -> list[str]:
    """The report's lines that carry a number, a commit or a seeded bug, rebuilt from the evidence."""
    lean, checker, tests = ev["lean"], ev["statement_checker"], ev["pytest"]
    lines = [f"`Build completed successfully ({lean['build_jobs']} jobs)`",
             f"PASS: {lean['audit_files']} source files, {_n(lean['audit_theorems'])} theorems",
             f"PASS ({_n(lean['statements'])} statements; RD-6a adds {lean['statements_added']}, removes "
             f"{lean['statements_removed']} and changes none)",
             f"layer graph kept ({lean['lean_modules']} modules)",
             f"RD-1: {checker['rd1_exact']} exact, {checker['rd1_pending']} pending; RD-6a: {checker['rd6a_checked']} "
             f"checked, {checker['rd6a_exact']} exact, {len(checker['rd6a_pending'])} pending "
             f"({', '.join(f'`{name}`' for name in checker['rd6a_pending'])}), {len(checker['rd6a_later'])} not built "
             f"({', '.join(f'`{name}`' for name in checker['rd6a_later'])})",
             f"S +{ev['trust_map']['rd6a_S']}",
             f"Gated commit: `{ev['gated_commit']}`",
             f"at `{ev['base'][:8]}`",
             f"`tests/test_readings_defaults_statements.py` ({ev['tests_added']['statements']} new) and "
             f"`tests/test_readings_defaults_rd6a.py` ({ev['tests_added']['rd6a']})",
             f"PASS ({ev['tests_added']['collection_ids_added']} IDs added in `{ev['tests_added']['collection_commit']}`, "
             f"{ev['tests_added']['collection_ids_removed']} removed)",
             f"({ev['tests_added']['report_ids_added']} added, none removed)",
             f"disk checked ({ev['disk_free_gb']} GB free before the gate)"]
    chunks = tests["chunks"]
    for i, chunk in enumerate(chunks, 1):
        lines.append(f"| {i} | {chunk['files']} | {_n(chunk['passed'])} | {chunk['skipped']} | {chunk['failed']} |")
    lines.append(f"| all | {sum(c['files'] for c in chunks)} | {_n(sum(c['passed'] for c in chunks))} | "
                 f"{sum(c['skipped'] for c in chunks)} | {sum(c['failed'] for c in chunks)} |")
    slow = tests["slow"]
    lines.append(f"the {slow['tests']} slow tests alone (`-n {slow['workers']}`): {slow['passed']} passed, "
                 f"{slow['failed']} failed")
    lines.append(f"`-n {tests['workers']}`")
    lines += [f"| `{c['sha']}` | {c['subject']} |" for c in ev["commits"]]
    lines += [f"| {b['id']} | `{b['file']}` | {b['bug']} | {b['failed']} |" for b in ev["seeded_bugs"]]
    return lines


def mismatches(report: str, ev: dict) -> list[str]:
    return [line for line in expected_lines(ev) if line not in report]


def _evidence() -> dict:
    return json.loads(EVIDENCE.read_text())


def test_report_lines_come_from_the_saved_evidence():
    assert mismatches(REPORT.read_text(), _evidence()) == []


def test_saved_evidence_is_a_green_gate_on_the_last_listed_commit():
    ev = _evidence()
    assert ev["clean_worktree"] is True
    assert len(ev["gated_commit"]) == 40 and ev["gated_commit"].startswith(ev["commits"][-1]["sha"])
    assert ev["commits"] and all(c["subject"].startswith("readings-defaults RD-6a: ") for c in ev["commits"])
    assert ev["pytest"]["chunks"] and all(c["passed"] > 0 and c["failed"] == 0 for c in ev["pytest"]["chunks"])
    assert ev["pytest"]["slow"]["passed"] > 0 and ev["pytest"]["slow"]["failed"] == 0
    assert ev["lean"]["statements_removed"] == 0 and ev["lean"]["statements_added"] > 0
    assert len(ev["seeded_bugs"]) >= 3 and len({b["id"] for b in ev["seeded_bugs"]}) == len(ev["seeded_bugs"])


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


@pytest.mark.parametrize("path", [p for p in _paths(json.loads(EVIDENCE.read_text())) if p not in UNSTATED],
                         ids=lambda p: ".".join(map(str, p)))
def test_report_check_fails_on_every_changed_leaf(path):
    ev = _evidence()
    changed = copy.deepcopy(ev)
    node = changed
    for key in path[:-1]:
        node = node[key]
    old = node[path[-1]]
    node[path[-1]] = old + 1 if isinstance(old, int) else "x" + old
    assert mismatches(REPORT.read_text(), changed)


def test_report_check_fails_on_an_empty_report_or_empty_evidence():
    ev = _evidence()
    assert mismatches("", ev)
    empty = copy.deepcopy(ev)
    empty["pytest"]["chunks"], empty["commits"], empty["seeded_bugs"] = [], [], []
    assert mismatches(REPORT.read_text(), empty)
