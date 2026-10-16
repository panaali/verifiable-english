"""The suite-tail measurement (tools/bench/suite_tail.py) and the profile records it reads (tools/pytest_profile.py).

The numbers of docs/test-tail/report.md come from these summaries; the durations file the scheduler orders
the suite by comes from the same records.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from tests.subprocesses import HANG_TIMEOUT
from tools import nested_pytest, test_schedule

ROOT = Path(__file__).resolve().parents[1]
from tools.bench import suite_tail  # noqa: E402

PATCHED_CLOCKS = '''
import time


def test_injects_a_clock(monkeypatch):
    """As a deadline test does: the patched clocks run backwards from the real ones."""
    monkeypatch.setattr(time, "monotonic", lambda: -1e9)
    monkeypatch.setattr(time, "time", lambda: 1.0)


def test_plain():
    pass
'''


def test_profile_records_keep_real_times_when_a_test_patches_the_clocks(tmp_path):
    """A test that patches `time.monotonic` once gave a setup of -797,808 s in the profile (and so in the
    durations file): the plugin reads the clocks it imported."""
    (tmp_path / "test_clocks.py").write_text(PATCHED_CLOCKS)
    profile = tmp_path / "profile"
    before = time.time()
    result = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", "-p", "tools.pytest_profile",
                                                   "-o", "addopts=", "test_clocks.py"]),
                            cwd=tmp_path, env=nested_pytest.environment(os.environ, PYTHONPATH=str(ROOT),
                                                                        VE_TEST_PROFILE_DIR=str(profile)),
                            capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stdout[-4000:]
    after = time.time()
    rows = suite_tail.records(profile)
    assert sorted(row["nodeid"] for row in rows) == ["test_clocks.py::test_injects_a_clock", "test_clocks.py::test_plain"]
    for row in rows:
        assert all(row[phase] >= 0 for phase in ("setup", "call", "teardown")), row
        assert before <= row["start"] <= row["end"] <= after, row
        assert row["worker"] == "main"


def row(nodeid, worker, start, end, setup=0.0):
    return {"nodeid": nodeid, "worker": worker, "start": start, "end": end, "setup": setup,
            "call": end - start - setup, "teardown": 0.0}


def test_occupancy_is_the_share_of_worker_seconds_inside_a_test_per_minute():
    rows = [row("a", "gw0", 0, 120), row("b", "gw1", 0, 60), row("c", "gw1", 90, 105)]
    assert suite_tail.occupancy(rows, 2, 0, 120) == [100.0, 62.5]
    # The last, partial minute counts only its own seconds.
    assert suite_tail.occupancy([row("a", "gw0", 0, 90)], 1, 0, 90) == [100.0, 100.0]


def test_summary_names_the_tail_and_the_slowest_tests(monkeypatch):
    rows = [row("t::slow", "gw0", 100, 400, setup=50), row("t::quick", "gw1", 100, 110), row("t::mid", "gw1", 110, 200)]
    events = {"tests": {"t::slow": {"outcome": "passed"}, "t::quick": {"outcome": "passed"},
                        "t::mid": {"outcome": "skipped"}},
              "workers": {"gw0": ["t::quick", "t::mid", "t::slow"], "gw1": ["t::quick", "t::mid", "t::slow"]}}
    samples = [(100 + second, 0.5, 40.0) for second in range(300)]
    summary = suite_tail.summarise("x", rows, events, workers=2, start=100, end=400, samples=samples, returncode=0)
    assert summary["wall_seconds"] == 300 and summary["tests"] == 3
    assert summary["outcomes"] == {"passed": 2, "skipped": 1}
    assert summary["workers_collected_alike"] is True
    assert summary["worker_finished_seconds"] == {"gw0": 300, "gw1": 100}
    assert [entry["nodeid"] for entry in summary["slowest"]] == ["t::slow", "t::mid", "t::quick"]
    assert summary["slowest"][0] == {"nodeid": "t::slow", "seconds": 300, "setup": 50, "call": 250,
                                    "worker": "gw0", "started_at": 0}
    assert summary["setup_seconds_sum"] == 50 and summary["test_seconds_sum"] == 400
    assert summary["machine_busy_percent_per_minute"] == [50.0] * 5
    assert summary["load_per_minute"] == [40.0] * 5
    events["workers"]["gw1"] = ["t::quick", "t::slow", "t::mid"]
    assert not suite_tail.summarise("x", rows, events, workers=2, start=100, end=400, samples=samples,
                                    returncode=0)["workers_collected_alike"]


def test_durations_command_writes_the_scheduler_s_file(tmp_path, monkeypatch):
    profile = tmp_path / "profile"
    profile.mkdir()
    records = [{"kind": "test", "nodeid": "t::a", "setup": 0.5, "call": 6.04, "teardown": 0.0, "start": 1, "end": 2},
               {"kind": "test", "nodeid": "t::b", "setup": 0.0, "call": 0.4, "teardown": 0.0, "start": 1, "end": 2},
               {"kind": "proc", "exe": "lake", "test": "t::a", "wall": 3.0}]
    (profile / "gw0-123.jsonl").write_text("".join(json.dumps(record) + "\n" for record in records))
    # Another run: t::a took longer in the first (6.54 s) and t::b in this one, which alone measured t::c.
    early = tmp_path / "early"
    early.mkdir()
    (early / "main-7.jsonl").write_text(
        json.dumps({"kind": "test", "nodeid": "t::a", "setup": 0.0, "call": 3.0, "teardown": 0.0}) + "\n"
        + json.dumps({"kind": "test", "nodeid": "t::b", "setup": 0.0, "call": 8.0, "teardown": 0.0}) + "\n"
        + json.dumps({"kind": "test", "nodeid": "t::c", "setup": 0.0, "call": 2.0, "teardown": 0.0}) + "\n")
    output = tmp_path / "durations.json"
    # t::gone was measured, but the collection no longer has it.
    (profile / "gw1-124.jsonl").write_text(json.dumps({"kind": "test", "nodeid": "t::gone", "setup": 0.0,
                                                       "call": 50.0, "teardown": 0.0}) + "\n")
    collection = tmp_path / "collection.json"
    collection.write_text(json.dumps(["t::a", "t::b", "t::c"]))
    monkeypatch.setattr(sys, "argv", ["suite_tail.py", "durations", str(early), str(profile), "--output", str(output),
                                      "--source", "a test", "--collection", str(collection)])
    assert suite_tail.main() == 0
    assert test_schedule.read_durations(output) == {"t::a": 6.5, "t::b": 8.0, "t::c": 2.0}
    assert json.loads(output.read_text())["source"] == "a test"


def test_durations_command_counts_an_earlier_file_as_one_more_run(tmp_path, monkeypatch):
    """Profiling a few changed files adds their new and split tests' times without forgetting the rest: the
    earlier file is one more run (each test keeps its longest time, also a cold one this run measured warm)
    and keeps its estimate of an unrecorded test."""
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "gw0-1.jsonl").write_text("".join(json.dumps(row) + "\n" for row in (
        {"kind": "test", "nodeid": "t::split[0]", "call": 40.0},
        {"kind": "test", "nodeid": "t::warm", "call": 5.0},
        {"kind": "test", "nodeid": "t::longer", "call": 8.0},
        {"kind": "test", "nodeid": "t::quick", "call": 0.5},
    )))
    previous = tmp_path / "previous.json"
    previous.write_text(test_schedule.durations_text(
        {"t::split": 300.0, "t::warm": 90.0, "t::longer": 3.0, "t::kept": 12.0, "t::gone": 7.0, "t::short": 0.2},
        source="earlier"))
    collection = tmp_path / "collection.json"
    collection.write_text(json.dumps(["t::split[0]", "t::warm", "t::longer", "t::quick", "t::kept"]))
    output = tmp_path / "durations.json"
    monkeypatch.setattr(sys, "argv", ["suite_tail.py", "durations", str(profile), "--output", str(output),
                                      "--source", "remeasured", "--collection", str(collection),
                                      "--previous", str(previous)])
    assert suite_tail.main() == 0
    assert test_schedule.read_estimates(output) == (
        {"t::split[0]": 40.0, "t::warm": 90.0, "t::longer": 8.0, "t::kept": 12.0}, 0.2)
    previous.write_text("{}")
    with pytest.raises(SystemExit, match="not a durations file"):
        suite_tail.main()


def test_durations_command_collects_current_gate_ids_by_default(tmp_path, monkeypatch):
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "main-7.jsonl").write_text("".join(json.dumps(row) + "\n" for row in (
        {"kind": "test", "nodeid": "t::current", "call": 3.0},
        {"kind": "test", "nodeid": "t::gone", "call": 20.0},
    )))
    monkeypatch.setattr(suite_tail.gate_collection, "collect", lambda root: ["t::current"])
    output = tmp_path / "durations.json"
    monkeypatch.setattr(sys, "argv", ["suite_tail.py", "durations", str(profile), "--output", str(output),
                                      "--source", "a test"])
    assert suite_tail.main() == 0
    assert test_schedule.read_durations(output) == {"t::current": 3.0}
