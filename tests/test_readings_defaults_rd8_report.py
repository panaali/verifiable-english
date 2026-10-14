"""The RD-8 report states the saved evidence (docs/readings-defaults/rd8/evidence.json) and nothing else.

Every number and list of the report is rebuilt here from the evidence file, which was written at the commit the
gate ran on. No test reads live git state, so the checks hold after syncs with main and after the merge.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs/readings-defaults/rd8"
EVIDENCE = json.loads((FOLDER / "evidence.json").read_text())
REPORT = (FOLDER / "DELTA.md").read_text()


def section(title: str) -> str:
    start = REPORT.index(f"## {title}")
    end = REPORT.find("\n## ", start + 1)
    return REPORT[start:end if end > 0 else len(REPORT)]


def test_the_evidence_is_complete():
    assert EVIDENCE["batch"] == "RD-8" and re.fullmatch(r"[0-9a-f]{8}", EVIDENCE["base"])
    assert EVIDENCE["commits"] and all(re.fullmatch(r"[0-9a-f]{8}", c["hash"]) and c["subject"]
                                       for c in EVIDENCE["commits"])
    assert EVIDENCE["gate"]["head"] == EVIDENCE["commits"][-2]["hash"]
    assert EVIDENCE["gate"]["failed"] == 0
    assert all(m["caught_by"] for m in EVIDENCE["mutants"])


def test_the_report_names_the_base_and_the_gate_head():
    assert f"from `{EVIDENCE['base']}`" in REPORT
    assert f"## Historical gate (run on `{EVIDENCE['gate']['head']}`, before the report commit)" in REPORT


def test_review_fix_commit_chain_and_final_gate_target():
    """The report commit is a self entry because its own hash cannot occur in committed JSON. It is the latest
    commit of that subject in HEAD's own history: each review round's report commit reuses the subject, and
    another branch's commits (`--all`) are not this tree's."""
    final = EVIDENCE["final_gate"]
    assert final["target"] == "self" and final["checks"] == ["lake build", "python3 lean/audit.py", "full pytest"]
    assert final["results"] == {check: "PASS" for check in final["checks"]}
    [report_commit] = subprocess.check_output(
        ["git", "log", "HEAD", "--format=%H", "-n", "1", "--grep=^docs: RD-8 review fixes and final gate evidence$"],
        cwd=ROOT, text=True).splitlines()
    rows = [line.split("\t", 1) for line in subprocess.check_output(
        ["git", "log", "--reverse", "--format=%H%x09%s", f"{EVIDENCE['base']}..{report_commit}"],
        cwd=ROOT, text=True).splitlines()]
    saved = EVIDENCE["commits"] + EVIDENCE["review_fix_commits"]
    assert len(rows) == len(saved) + 1
    assert all(sha.startswith(entry["hash"]) and subject == entry["subject"]
               for (sha, subject), entry in zip(rows[:-1], saved, strict=True))
    assert rows[-1][1] == "docs: RD-8 review fixes and final gate evidence"


def test_the_theorem_table_is_the_saved_list():
    table = re.findall(r"^\| `(VE\.[\w.]+)` \|", section("Theorems (all proved, no `sorry`)"), re.M)
    assert table == EVIDENCE["theorems"]
    assert f"these {len(EVIDENCE['theorems'])} were written" in REPORT
    assert f"review of the {len(EVIDENCE['theorems'])} statements" in REPORT


def test_every_saved_theorem_is_audited():
    """The theorems are RD-8's own: each is in the audit record and the audit list."""
    record = (ROOT / "lean/axioms.txt").read_text()
    audit = (ROOT / "lean/VE/Audit.lean").read_text()
    for name in EVIDENCE["theorems"]:
        assert f"'{name}'" in record, name
        assert f"#print axioms {name}\n" in audit, name


def test_the_test_counts_are_the_saved_ones():
    counts = EVIDENCE["tests_added"]
    for path, count in counts.items():
        assert f"{count} in `{path}`" in REPORT, path
    assert f"({sum(counts.values())} in all)" in REPORT


def test_the_seeded_bugs_are_the_saved_ones():
    rows = re.findall(r"^\| (M\d+) \| (.+?) \| `(.+?)` \| (.+?) \|$", section("Seeded bugs (each made a check fail, then was removed)"),
                      re.M)
    assert rows == [(m["id"], m["behaviour"], m["file"], m["caught_by"]) for m in EVIDENCE["mutants"]]
    assert len(rows) >= 3


def test_the_gate_numbers_are_the_saved_ones():
    gate = EVIDENCE["gate"]
    text = section(f"Historical gate (run on `{gate['head']}`, before the report commit)")
    chunks = gate["pytest_chunks"]
    assert (" + ".join(str(c["passed"]) for c in chunks) + " passed, " +
            " + ".join(str(c["skipped"]) for c in chunks) + f" skipped, {gate['failed']} failed") in text
    for fragment in (f"({gate['lake_build_jobs']} jobs)", f"{gate['audit_files']} source files",
                     f"{gate['audit_theorems']} theorems", f"{gate['statements']} statements",
                     f"({gate['lean_modules']} modules)", f"{gate['gate_collection_ids']} IDs",
                     f"| {gate['slow_tests_passed']} passed |", f"| {gate['tools_tests_passed']} passed |"):
        assert fragment in text, fragment


def test_the_trust_budget_figures_are_the_saved_ones():
    base, head = EVIDENCE["trust_budget"]["base"], EVIDENCE["trust_budget"]["head"]
    text = section(f"Historical gate (run on `{EVIDENCE['gate']['head']}`, before the report commit)")
    assert f"S {base['S']} and\nV {base['V']}" in text or f"S {base['S']} and V {base['V']}" in text
    assert f"S +{head['S'] - base['S']}" in text and f"V +{head['V'] - base['V']}" in text
    assert f"S {head['S']} and\nV {head['V']}" in text or f"S {head['S']} and V {head['V']}" in text
