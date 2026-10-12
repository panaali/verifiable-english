"""Check the saved AR-9 evidence and rendered report at the batch gate.

This is deliberately outside pytest collection: D4 keeps batch report checks out
of the permanent suite. It reads only saved evidence, never live git.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
SPEC = importlib.util.spec_from_file_location("ar9_report", HERE / "report.py")
assert SPEC is not None and SPEC.loader is not None
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)
SPLIT_MODULES = {f"ve/assist/{name}.py" for parts in REPORT.SPLITS.values() for name in parts}


def _saved(name: str):
    return json.loads((EVIDENCE / name).read_text())


def check_report():
    text = (HERE / "REPORT.md").read_text()
    generated = text.split("<!-- BEGIN GENERATED AR-9 METRICS -->\n", 1)[1].split(
        "\n<!-- END GENERATED AR-9 METRICS -->", 1)[0]
    assert generated == REPORT.metrics()


def check_split():
    split = _saved("split.json")
    assert split["dirty"] is False and len(split["base"]) == len(split["head"]) == 40
    assert split["base"] != split["head"]
    rows = split["definitions"]
    assert len(rows) > 100 and len({row["name"] for row in rows}) == len(rows)
    assert {row["base_file"] for row in rows} == set(REPORT.SPLITS)
    assert all(row["head_file"] in SPLIT_MODULES and row["identical_up_to_seams"] for row in rows)
    seamed = [row for row in rows if not row["identical"]]
    assert seamed and all(row["head_owner"] in {"_Replay", "_Commands"} for row in seamed)
    assert split["missing_names"] == {"ve.assist.recovery": [], "ve.assist.session": []}
    base, head = split["files"]["base"], split["files"]["head"]
    assert set(REPORT.SPLITS) <= set(base) and SPLIT_MODULES <= set(head)
    assert all(row["lines"] <= REPORT.TARGET_LINES for path, row in head.items() if path.startswith("ve/assist/"))
    assert sum(r["function_imports"] for r in base.values()) == sum(r["function_imports"] for r in head.values())


def check_mutants():
    saved = _saved("mutants.json")
    mutants = saved["mutants"]
    assert len(mutants) >= 3 and len({m["bug"] for m in mutants}) == len(mutants)
    assert {m["claim"] for m in mutants} == {"names", "seams", "one owner"}
    for mutant in mutants:
        assert mutant["runs"] and set(mutant["files"]) <= SPLIT_MODULES
        for run in mutant["runs"]:
            assert run["exit_code"] != 0 and ("1 failed" in run["failure_excerpt"]
                                              or "1 error" in run["failure_excerpt"]), run["test"]
    tests = [run["test"] for mutant in mutants for run in mutant["runs"]]
    assert [row["test"] for row in saved["restored"]] == tests
    assert all(row["exit_code"] == 0 for row in saved["restored"])


def check_gate():
    scope, gate, split = _saved("scope.json"), _saved("gate.json"), _saved("split.json")
    assert scope["base"] == split["base"]
    assert scope["commits"] and scope["commits"][0]["hash"] == scope["head"]
    assert split["head"] in {row["hash"] for row in scope["commits"]}
    assert gate["commit_sha"] == scope["head"] and gate["dirty"] is False
    assert gate["status"] == "passed" and gate["failures"] == []
    counts = gate["counts"]
    assert counts["passed"] > 0 and counts["failed"] == 0 and counts["rust_passed"] > 0
    assert counts["passed"] + counts["skipped"] + counts["failed"] == counts["selected"]
    assert {"lean_build", "lean_audit", "cargo_test", "pytest"} <= set(gate["stages"])


def main():
    check_report()
    check_split()
    check_mutants()
    if (EVIDENCE / "gate.json").exists():
        check_gate()
        print("AR-9 saved evidence PASS (including final gate)")
    else:
        print("AR-9 saved evidence PASS (pre-gate checks)")


if __name__ == "__main__":
    main()
