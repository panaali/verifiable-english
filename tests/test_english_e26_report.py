"""English E2.6's report: every number comes from saved evidence (the readability comparison, the A/B summary, the
commit list of `main..HEAD --no-merges`, the seeded mutants, the gate result), never from a live checkout or git."""
import json
import re
from pathlib import Path

from conformance import english_lean_e2_6_report as R

ROOT = Path(__file__).resolve().parents[1]


def test_the_measured_section_is_the_rendering_of_the_saved_evidence():
    text = R.REPORT.read_text()
    assert text[text.index(R.BEGIN):text.index(R.END) + len(R.END)] == R.render()
    assert R.main([]) == 0


def test_every_cited_test_exists():
    """The tests the mutants failed, and those the report, DELTA and LEDGER cite, are functions of the suite."""
    cited = [t for m in R.load("mutants.json")["mutants"] for t in m["failed"]]
    for doc in ("docs/lean-first/e2/E2.6.md", "docs/lean-first/e2/DELTA.md", "docs/lean-first/e2/LEDGER.md",
                "docs/lean-first/e2/evidence/e2.6/ab-dispositions.md"):
        cited += re.findall(r"tests/[\w/]+\.py::\w+", (ROOT / doc).read_text())
    assert cited
    for item in cited:
        path, name = item.split(" ")[0].split("::")
        assert f"def {name}(" in (ROOT / path).read_text(), item


def test_the_commit_list_is_saved_and_whole():
    commits = R.load("commits.json")
    assert commits["range"].startswith("main..HEAD --no-merges")
    ids = [c["commit"] for c in commits["commits"]]
    assert ids and len(set(ids)) == len(ids) and all(re.fullmatch(r"[0-9a-f]{8,}", c) for c in ids)
    assert all(c["subject"] for c in commits["commits"])


def test_the_e2_report_rows_follow_the_saved_summaries():
    report = (ROOT / "docs/spec/english-lean-e2-report.md").read_text()
    ab = R.load("ab-summary.json")["summary"]
    readability = R.load("readability-comparison.json")
    rules = ab["verdict_rules"]
    row3 = next(line for line in report.splitlines() if line.startswith("| 3. Corpus A/B |"))
    for phrase in (f"{ab['records_per_side']:,} records per side", f"{rules['V-rights-readings-head']} rights",
                   f"{rules['V-quantity-certificate-exhausted']} quantity rows are Python bugs",
                   f"{rules['V-english-source-limit-span']} English rows", f"{rules['V-pilot-readings-slot']} pilot rows",
                   f"{rules['V-quantity-model-path']} quantity rows lose a `path`",
                   f"{ab['text_rows_kept_total']} of {ab['wording_order_rows']} wording and order rows",
                   f"{ab['text_rows_for_dri_total']} main-side"):
        assert phrase in row3, phrase
    assert ab["unexplained"] == 0 and ab["availability"] == 0 and "no availability row" in row3
    row4 = next(line for line in report.splitlines() if line.startswith("| 4. Readability items |"))
    words = {6: "six", 5: "five"}
    assert f"{readability['writing_attempts']} writing attempts" in row4
    assert f"{words[readability['writing_message_changes']]} changed messages" in row4
    assert f"{readability['reading_items']} reading items" in row4
    assert f"the {words[len(readability['lean_reading_items'])]} E2.5 lost answered by Lean" in row4


def test_the_gate_result_is_clean_and_on_the_last_listed_commit():
    if not R.GATE.exists():
        return  # the gate result is added by the report's last commit, after the gate ran on the listed head
    gate = json.loads(R.GATE.read_text())
    assert gate["status"] == "passed" and gate["dirty"] is False and not gate["failures"]
    counts = gate["counts"]
    assert counts["selected"] == counts["passed"] + counts["skipped"] + counts["failed"] and counts["failed"] == 0
    assert gate["commit_sha"].startswith(R.load("commits.json")["commits"][-1]["commit"])
