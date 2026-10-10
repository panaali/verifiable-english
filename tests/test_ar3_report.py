"""AR-3's report and DELTA against their saved evidence (docs/arch/AR-3/evidence), never the live tree or history."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/arch/AR-3"
REPORT = (DOCS / "REPORT.md").read_text()
DELTA = (DOCS / "DELTA.md").read_text()


def evidence(name):
    return json.loads((DOCS / "evidence" / name).read_text())


def flat(text):
    return " ".join(text.split())


def test_the_outcome_is_the_saved_measurement():
    measure, report = evidence("measure.json"), flat(REPORT)
    baseline, replay, base = measure["baseline"], measure["replay"], measure["base_collection"]
    assert "14 days" in report and measure["days"] == 14
    assert (f"`tools/gate-collection.json`, {baseline['lines']:,} lines ({baseline['bytes']:,} bytes, "
            f"{baseline['ids']:,} IDs)") in report
    assert f"{baseline['commits']} commits on `main` (merges not counted) changed that file" in report
    assert f"for each of the {baseline['first_parent_commits']} first-parent commits" in report
    assert len(replay["commits"]) == baseline["first_parent_commits"]
    assert replay["removed"] == sum(row["removed"] for row in replay["commits"])
    assert replay["explained"] + replay["refused"] == replay["removed"]
    assert (f"{replay['removed']:,} IDs were removed; the rule explains {replay['explained']:,} and refuses "
            f"{replay['refused']}, all in one merge (`") in report
    [refusing] = [row for row in replay["commits"] if row["refused"]]
    assert f"(`{refusing['commit'][:8]}`, lf-1)" in report and "lf-1" in refusing["subject"]
    assert {nodeid.split("[")[0] for nodeid in refusing["refused"]} == {
        "tests/test_assurance_manifest.py::test_every_declared_response_field_is_enforced"}
    assert f"took {base['seconds']} s" in report and f"collected the {base['ids']:,} IDs" in report
    assert base["ids"] == baseline["ids"] and base["only_collected"] == base["only_pinned"] == []
    assert f"(measured {base['seconds']} s on this batch's base)" in flat(DELTA)
    assert (f"would have refused {replay['refused']} of {replay['removed']:,} removed IDs, all in one merge"
            in flat(DELTA))


def test_the_base_and_commits_are_the_saved_scope():
    scope, measure = evidence("scope.json"), evidence("measure.json")
    assert scope["range"] == "main..HEAD --no-merges" and scope["base"] == measure["base"]
    assert f"base `{scope['base'][:8]}`" in REPORT
    listed = [line[2:] for line in REPORT.split("## Commits")[1].splitlines() if line.startswith("- ")]
    assert listed == [f"{commit['sha'][:8]} {commit['subject']}" for commit in reversed(scope["commits"])]
    # Every changed path outside this directory is named among the files touched.
    touched = flat(REPORT.split("## Coordination")[1].split("- Overlap")[0])
    assert all(f"`{path}`" in touched for path in scope["files"] if not path.startswith("docs/arch/AR-3/"))
    assert scope["files"]["tools/gate-collection.json"] == {"added": 0,
                                                             "deleted": measure["baseline"]["lines"]}


def test_every_seeded_bug_is_in_the_table_and_in_a_changed_file():
    mutants, scope = evidence("mutants.json"), evidence("scope.json")
    rows = [line.split(" | ") for line in REPORT.split("## Seeded bugs")[1].split("## Tests")[0].splitlines()
            if line.startswith("| ") and not line.startswith(("| Bug", "|---"))]
    assert [[cell.strip("| ") for cell in row] for row in rows] == [
        [mutant["bug"], mutant["file"], mutant["test"].split("::", 1)[1]] for mutant in mutants]
    assert all(mutant["file"] in scope["files"] and mutant["exit_code"] != 0
               and "1 failed" in mutant["failure_excerpt"] for mutant in mutants)
    assert len(mutants) >= 3


def test_the_delta_rows_name_their_tests_and_the_unsigned_one():
    rows = [line for line in DELTA.splitlines() if line.startswith("| G")]
    assert [row.split(" | ")[0] for row in rows] == [f"| G{index}" for index in range(1, 7)]
    assert all("test_" in row or "DRI-NEEDED" in row for row in rows)
    assert [row.split(" | ")[0] for row in rows if "DRI-NEEDED" in row] == ["| G6"]
    assert "(G6, where the IDs are stored) needs a DRI signature" in flat(REPORT)
