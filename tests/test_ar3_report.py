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
    rows = replay["commits"]
    assert len(rows) == baseline["first_parent_commits"]
    for key in ("removed", "recorded", "labelled", "trailers"):
        assert replay[key] == sum(row[key] for row in rows)
    assert replay["unlabelled"] == sum(len(row["unlabelled"]) for row in rows)
    assert replay["commits_with_removals"] == sum(row["removed"] > 0 for row in rows)
    # No commit then carried a record: every removal is labelled or unlabelled, none recorded.
    assert replay["recorded"] == 0 and replay["labelled"] + replay["unlabelled"] == replay["removed"]
    assert (f"{replay['removed']:,} IDs were removed, in {replay['commits_with_removals']} of the "
            f"{baseline['first_parent_commits']} commits. The diff labels {replay['labelled']:,} of them; "
            f"{replay['unlabelled']} are unlabelled, all in one merge (`") in report
    [unlabelled] = [row for row in rows if row["unlabelled"]]
    assert f"(`{unlabelled['commit'][:8]}`, lf-1)" in report and "lf-1" in unlabelled["subject"]
    assert {nodeid.split("[")[0] for nodeid in unlabelled["unlabelled"]} == {
        "tests/test_assurance_manifest.py::test_every_declared_response_field_is_enforced"}
    others = [row for row in rows if row is not unlabelled and row["removed"]]
    assert (f"come to {replay['trailers']:,} for those {replay['removed']:,} IDs. {unlabelled['trailers']} of them "
            f"are lf-1's ({unlabelled['removed']:,} IDs") in report
    assert f"The other {len(others)} commits need {sum(row['trailers'] for row in others)}." in report
    assert (f"({unlabelled['trailers']} of {replay['trailers']:,} in the replay, one merge)" in report
            and f"cut lf-1's {unlabelled['trailers']}" in report)
    assert f"took {base['seconds']} s" in report and f"collected the {base['ids']:,} IDs" in report
    assert base["ids"] == baseline["ids"] and base["only_collected"] == base["only_pinned"] == []
    assert f"(measured {base['seconds']} s on this batch's base)" in flat(DELTA)
    assert (f"it labels {replay['labelled']:,} of {replay['removed']:,} removed IDs; the "
            f"{replay['unlabelled']} unlabelled are one merge's" in flat(DELTA))


def test_the_check_on_the_final_code_is_the_saved_one():
    scope = evidence("scope.json")
    text = (DOCS / "evidence/check.txt").read_text()
    # "<n> collected, <n> at <base>; <n> added, <n> removed by a trailer, <n> refused, <n> stale and <n> malformed
    # trailers"
    words = text.splitlines()[-1].replace(",", "").replace(";", "").split()
    assert words[1:4:2] + words[6:9:2] + words[13:16:2] + words[18:] == [
        "collected", "at", "added", "removed", "refused", "stale", "malformed", "trailers"]
    collected, at_base, added, removed = (int(words[index]) for index in (0, 2, 5, 7))
    assert words[4] == scope["base"] and words[12] == words[14] == words[17] == "0"
    assert sum(line.startswith("removed: ") for line in text.splitlines()) == removed
    assert (f"(`evidence/check.txt`): {collected:,} collected, {at_base:,} at the base, {added} added, {removed} "
            "removed by a trailer, none refused, stale or malformed.") in flat(REPORT)
    assert f"This batch's own removals: {removed} base IDs" in flat(REPORT)


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


def test_f2_the_delta_rows_name_tests_and_no_storage_delta_needs_a_signature():
    rows = [line for line in DELTA.splitlines() if line.startswith("| G")]
    assert [row.split(" | ")[0] for row in rows] == [f"| G{index}" for index in range(1, 9)]
    assert all("test_" in row for row in rows)
    assert not any("DRI-NEEDED" in row for row in rows)
    assert "G6 now uses the planned gate record" in flat(REPORT)
