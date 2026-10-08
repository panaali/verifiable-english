"""RD-2b's report against its saved evidence (build checklist 20): every number in
docs/readings-defaults/rd2b/DELTA.md is regenerated here from evidence/gate.json and the files it names, never from
a live run or a live git diff, so the report keeps checking after syncs with main and after the merge."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/readings-defaults/rd2b"
DELTA = (HERE / "DELTA.md").read_text()
LEDGER = (HERE / "LEDGER.md").read_text()
GATE = json.loads((HERE / "evidence/gate.json").read_text())


def test_suite_chunks():
    chunks = GATE["suite"]["chunks"]
    assert len(chunks) == 6 and all(c["passed"] > 0 for c in chunks)
    for key in ("passed", "skipped", "failed"):
        values = [str(c[key]) for c in chunks]
        assert ", ".join(values[:-1]) + " and " + values[-1] + f" {key}" in DELTA, key
    failed = [f["test"] for f in GATE["suite"]["failures"]]
    assert len(failed) == sum(c["failed"] for c in chunks)
    for test in failed:
        path, name = test.split("::")
        assert name in DELTA and (ROOT / path).exists()
    assert all(f["base"].startswith(f"fails the same at {GATE['base']}") for f in GATE["suite"]["failures"])
    assert f"HEAD `{GATE['suite']['head']}`" in DELTA


def test_lean_numbers():
    lean = GATE["lean"]
    assert f"{lean['build_jobs']} jobs, success" in DELTA
    assert f"{lean['audit_source_files']} source files, {lean['audit_theorems']} theorems (base " \
           f"{lean['audit_theorems_base']})" in DELTA
    assert f"PASS: {lean['statements']} statements (base {lean['statements_base']}), {lean['statements_changed']} " \
           f"changed, {lean['statements_removed']} removed" in DELTA
    assert lean["statements_changed"] == lean["statements_removed"] == 0
    for batch, label in (("rd1", "RD-1"), ("rd2a", "RD-2a")):
        check = GATE["statement_check"][batch]
        assert check["exact"] == check["declarations"] and check["pending"] == 0
        assert f"{label}: {check['exact']} exact, {check['pending']} pending" in DELTA
    assert f"RD-6a: {GATE['statement_check']['rd6a']['exact']} exact" in DELTA
    fixtures = GATE["fixtures"]
    assert f"fixtures `{fixtures['file']}` | {fixtures['tests']} passed" in DELTA
    assert f"(`{lean['base_service_sha256'][:8]}`)" in DELTA and f"(`{lean['service_sha256'][:8]}`)" in DELTA


def test_ab_totals_are_the_evidence_files():
    ab = GATE["ab"]
    records = same = unavailable = unlisted = 0
    for name, summary in ab["files"].items():
        data = json.loads((HERE / "evidence" / name).read_text())
        counted = sum(data["records"].values())
        assert (counted, data["totals"].get("same", 0), data["unlisted"], sum(data["unavailable_both"].values())) == \
            (summary["records"], summary["same"], summary["unlisted"], summary["unavailable_both"]), name
        # every difference is a record unavailable on both sides: no changed answer
        assert all(row["class"] == "unavailable" for row in data["differences"]), name
        assert f"({counted})" in DELTA or f"({counted} records)" in DELTA, name
        records, same = records + counted, same + data["totals"].get("same", 0)
        unavailable, unlisted = unavailable + sum(data["unavailable_both"].values()), unlisted + data["unlisted"]
    assert (records, same, unavailable) == (ab["records"], ab["same"], ab["unavailable_both"])
    assert records == same + unavailable and unlisted == unavailable
    assert f"{records} records, {same} the same, {unavailable} unavailable on both sides, 0 changed" in DELTA
    assert f"base `{GATE['base']}`, head `{ab['head']}`" in DELTA
    assert f"({same} of {records} the same; the other {unavailable} are" in " ".join(LEDGER.split())


def test_latency_rows_are_the_saved_runs():
    first, repeat = (json.loads((HERE / "evidence" / name).read_text()) for name in GATE["latency"])
    assert first["before_build"] == repeat["before_build"] == GATE["lean"]["base_service_sha256"]
    assert first["after_build"] == repeat["after_build"] == GATE["lean"]["service_sha256"]
    assert f"({first['calls']} calls)" in DELTA and f"({repeat['calls']} calls)" in DELTA
    for a, b in zip(first["rows"], repeat["rows"], strict=True):
        assert a["fixed_units"] == b["fixed_units"]
        cells = [a["elaborate"]["before"], a["elaborate"]["after"], b["elaborate"]["before"], b["elaborate"]["after"]]
        assert f"| {a['fixed_units']} | " + " | ".join(str(c) for c in cells) + " |" in DELTA
    # the claim of the paragraph: in the repeat, the filled document costs 1.4 to 1.7 s at every size
    added = [r["elaborate"]["after"] - r["elaborate"]["before"] for r in repeat["rows"]]
    assert all(1.3 < x < 1.8 for x in added) and "about 1.4 to 1.7 s" in DELTA


def test_seeded_bugs_name_real_tests_and_rows():
    bugs = json.loads((HERE / "evidence" / GATE["seeded_bugs"]).read_text())
    assert len(bugs) >= 3 and len({b["id"] for b in bugs}) == len(bugs)
    for bug in bugs:
        row = re.search(rf"^\| {bug['id']} \| (.*)$", DELTA, re.M)
        assert row, bug["id"]
        assert (ROOT / bug["file"]).exists()
        count = bug["failed_count"]
        assert count >= 1 and f"{count} {'test' if count == 1 else 'tests'}" in row[1], bug["id"]
        assert any(test.split("::")[1] in row[1] for test in bug["failed"]), bug["id"]
        for test in bug["failed"]:
            path, name = test.split("::")
            assert re.search(rf"^def {re.escape(name)}\(", (ROOT / path).read_text(), re.M), test


def test_the_reported_head_is_the_last_commit_listed():
    commits = GATE["commits_before_report"]
    assert len(commits) == len(set(commits)) and all(re.fullmatch(r"[0-9a-f]{8}", c) for c in commits)
    assert commits[-1] == GATE["suite"]["head"] and GATE["ab"]["head"] in commits
    assert f"from `main` at `{GATE['base']}`" in DELTA
