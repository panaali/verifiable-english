"""Test speed B5: the report's numbers are those of its saved evidence (docs/test-speed-b5)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/test-speed-b5"
EVIDENCE = HERE / "evidence"
REPORT = (HERE / "REPORT.md").read_text()


def load(name: str):
    return json.loads((EVIDENCE / name).read_text())


def measure():
    spec = importlib.util.spec_from_file_location("b5_measure", HERE / "measure.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_replay_is_recomputed_from_the_saved_durations():
    durations, saved = load("durations.json"), load("first-failure.json")
    assert {**measure().replay(durations["seconds"]), "map": durations["map"]} == saved


def test_the_replay_numbers_in_the_report():
    saved = load("first-failure.json")
    minutes = saved["saved_minutes"]
    for label, key in (("median", "median"), ("mean", "mean"), ("90th percentile", "p90"), ("max", "max")):
        assert f"| {label} | {minutes[key]} |" in REPORT, label
    assert f"covers {saved['files']} files and {saved['suite_seconds']:,} s of tests" in REPORT
    assert f"run on {saved['jobs']} workers" in REPORT
    assert f"the last file ends at {saved['makespan_name_order']:,} s" in REPORT
    assert f"{saved['files_saving_10_min_or_more']} of the {saved['files']} files" in REPORT
    assert saved["map"]["file"].startswith(f"tree-{saved['map']['tree'][:8]}") and \
        f"`tree-{saved['map']['tree'][:8]}`" in REPORT


def test_every_seeded_bug_was_caught_in_every_changed_python_file():
    mutants, scope = load("mutants.json"), load("scope.json")
    rows = mutants["mutants"]
    assert rows and all(row["caught"] and row["exit"] == 1 for row in rows)
    assert mutants["clean"] and not any(mutants["clean"].values())
    assert set(scope["product_python"]) == {row["file"] for row in rows}
    assert not scope["product_lean"] and not scope["product_rust"]
    assert f"All {len(rows)} bugs were caught" in REPORT
    for row in rows:
        assert f"| {row['id']} | `{row['file']}` |" in REPORT, row["id"]
        assert row["test"].split("::")[1] in REPORT


def test_the_demo_runs_show_the_order_and_the_stop():
    run = (EVIDENCE / "demo-run.log").read_text().splitlines()
    stop = (EVIDENCE / "demo-stop.log").read_text().splitlines()
    assert "order: failed last time ['tests/test_gate_quarantine.py']; changed ['tests/test_test_order.py']; " \
           "then the rest; --maxfail 5" in run
    passed = [line for line in run if line.startswith("  tests/")]
    assert len(passed) == 76 and all(" exit 0 " in line for line in passed)
    assert "recorded 77 units" in "\n".join(run) and "76 pytest files passed" in REPORT
    assert any(line.startswith("order: failed last time ['tools/test_layer_policy.py']") for line in stop)
    assert "stopping after 1 failed tests (--maxfail 1)" in stop
    stopped = next(line for line in stop if line.startswith("STOPPED EARLY"))
    assert stopped == ("STOPPED EARLY (--maxfail 1): 3 selected units did not run: tests/test_gate_collection.py, "
                       "tests/test_select_tests.py, tests/test_wire_gate_corpus.py")
    assert any(line.startswith("recorded 11 units") for line in stop) and "11 files had finished, and 3" in REPORT
