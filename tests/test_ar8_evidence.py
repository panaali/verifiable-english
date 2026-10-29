"""AR-8's report agrees with its SAVED evidence (fixed base and head commits, never the live tree).

The evidence was measured at the batch's last code commit; the next commit (subject `REPORT_SUBJECT`) holds only
the report folder. The commit check reads only fixed commits: the report commit, found by its subject in HEAD's
history, and the batch's own `AR-8:` commits, so it holds after syncs with main and after the merge.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs/architecture/ar-8"
spec = importlib.util.spec_from_file_location("ar8_measure", FOLDER / "measure.py")
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)
EVIDENCE = json.loads((FOLDER / "evidence.json").read_text())


def git(*args: str) -> list[str]:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()


def test_report_table_is_rendered_from_the_saved_evidence():
    report = (FOLDER / "REPORT.md").read_text()
    assert measure.splice(report, measure.render(EVIDENCE)) == report


def test_saved_numbers_are_consistent():
    numstat = EVIDENCE["numstat"]
    assert EVIDENCE["totals"] == {"added": sum(a for a, _ in numstat.values()),
                                  "deleted": sum(d for _, d in numstat.values())}
    for path, count in EVIDENCE["lines"].items():
        added, deleted = numstat[path]
        assert count["base"] - deleted + added == count["head"], path
    assert EVIDENCE["lines"]["tools/rust-module-exceptions.json"]["head"] == 0  # deleted
    commits = EVIDENCE["commits"]
    assert commits and all(re.fullmatch(r"[0-9a-f]{40}", row["sha"]) for row in commits)
    assert commits[-1]["sha"] == EVIDENCE["head"] and EVIDENCE["base"] not in {row["sha"] for row in commits}
    assert EVIDENCE["range"] == "main..HEAD --no-merges" and EVIDENCE["report_subject"] == measure.REPORT_SUBJECT


def test_the_saved_commits_are_every_commit_before_the_report_commit():
    # Review F5: the evidence covers every non-merge commit of the batch up to the report commit, and the report
    # commit changes only the report folder; an `AR-8:` commit after it (a later fix) needs new evidence.
    [report] = git("log", "HEAD", "-n", "1", "--format=%H", "--fixed-strings", f"--grep={measure.REPORT_SUBJECT}")
    assert git("log", "-n", "1", "--format=%s", report) == [measure.REPORT_SUBJECT]
    saved = [row["sha"] for row in EVIDENCE["commits"]]
    assert git("log", "--no-merges", "--reverse", "--format=%H", f"{EVIDENCE['base']}..{report}") == saved + [report]
    assert git("log", "--no-merges", "--reverse", "--format=%H %s", f"{EVIDENCE['base']}..{EVIDENCE['head']}") == [
        f"{row['sha']} {row['subject']}" for row in EVIDENCE["commits"]]
    changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", "--no-renames", report)
    assert changed and all(path.startswith("docs/architecture/ar-8/") for path in changed), changed
    batch = git("log", "HEAD", "--no-merges", "--reverse", "--format=%H", "--extended-regexp", "--grep=^AR-8:")
    assert batch == saved + [report], "an AR-8 commit after the report commit: measure the evidence again"


def test_every_seeded_bug_failed_a_test():
    mutants = EVIDENCE["mutants"]
    assert [row["mutant"] for row in mutants] == [mutant[0] for mutant in measure.MUTANTS]
    for row in mutants:
        assert row["exit"] == 1 and re.search(r"\b[1-9]\d* failed\b", row["summary"]), row
