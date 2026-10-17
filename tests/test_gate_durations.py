"""Each gate keeps its suite's per-test seconds in its record, and the next gate on that base orders its suite by them.

The durations are scheduling data only (tools/test_schedule.py): they decide which xdist worker runs a test and
when, never whether it runs or passes. Checked here: the record's compact field round-trips and a malformed one is
ignored; the overlay of the committed file with a base record's durations; `base_durations` against a real git
note; the gate's own run, which names the overlay to its suite and keeps its suite's seconds in the record and the
note; and the record's readers (tools/gate_collection.py, tools/batch_evidence.py) with the new field.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import zlib

import pytest

from subprocesses import HANG_TIMEOUT
from test_gate_integrity import PYTEST_STAGES, events, fake_trust, pin_base_collection, pin_rust_binary
from tools import gate, gate_collection, test_schedule

ROOT = Path(__file__).resolve().parents[1]
TIMED = {"tests/a.py::test_slow": 12.34, "tests/a.py::test_one": 1.0, "tests/b.py::test_quick": 0.5,
         "tests/b.py::test_quicker": 0.1}


def test_the_record_field_keeps_the_recorded_tests_and_the_mean_of_the_others():
    field = test_schedule.record_field(TIMED)
    assert field["format"] == test_schedule.FORMAT and field["tests"] == 4
    assert field["recorded_seconds"] == test_schedule.RECORDED_SECONDS
    assert test_schedule.read_record_field(json.loads(json.dumps(field))) == (
        {"tests/a.py::test_slow": 12.3, "tests/a.py::test_one": 1.0}, 0.3, None)
    assert test_schedule.read_record_field(test_schedule.record_field({})) == ({}, test_schedule.UNRECORDED_SECONDS,
                                                                               None)


def test_the_record_field_stays_small():
    """A suite's worth (17,000 tests, 2,500 of them recorded) adds little to the record and its git note: the
    collection the note already holds compresses to about 240 kB."""
    timed = {f"tests/test_m{i % 600}.py::test_case[{i}-some-parameter]": (2.0 + i % 50 if i % 7 == 0 else 0.05)
             for i in range(17000)}
    field = test_schedule.record_field(timed)
    assert sum(value >= test_schedule.RECORDED_SECONDS for value in timed.values()) > 2400
    assert len(json.dumps(field)) < 60_000
    assert len(test_schedule.read_record_field(field).durations) > 2400


def packed(value) -> str:
    return base64.b64encode(zlib.compress(json.dumps(value).encode())).decode()


GOOD = test_schedule.record_field(TIMED)
BAD = {
    "absent": None, "not an object": [GOOD], "format other": {**GOOD, "format": "ve-test-durations@2"},
    "format retyped": {**GOOD, "format": 1}, "seconds missing": {k: v for k, v in GOOD.items() if k != "seconds_zlib"},
    "seconds retyped": {**GOOD, "seconds_zlib": {"tests/a.py::test_slow": 12.3}},
    "seconds invalid base64": {**GOOD, "seconds_zlib": "***"},
    "seconds not zlib": {**GOOD, "seconds_zlib": base64.b64encode(b"not zlib").decode()},
    "seconds trailing data": {**GOOD, "seconds_zlib": base64.b64encode(
        base64.b64decode(GOOD["seconds_zlib"]) + b"x").decode()},
    "seconds not a map": {**GOOD, "seconds_zlib": packed([["tests/a.py::test_slow", 12.3]])},
    "seconds negative": {**GOOD, "seconds_zlib": packed({"tests/a.py::test_slow": -1})},
    "seconds a string": {**GOOD, "seconds_zlib": packed({"tests/a.py::test_slow": "12.3"})},
    "seconds a boolean": {**GOOD, "seconds_zlib": packed({"tests/a.py::test_slow": True})},
    "seconds too large": {**GOOD, "seconds_zlib": base64.b64encode(zlib.compress(
        b"{" + b" " * (test_schedule.MAX_RECORD_BYTES + 1) + b"}")).decode()},
    "unrecorded missing": {k: v for k, v in GOOD.items() if k != "unrecorded_seconds"},
    "unrecorded retyped": {**GOOD, "unrecorded_seconds": "0.3"},
    "unrecorded negative": {**GOOD, "unrecorded_seconds": -0.3},
}


@pytest.mark.parametrize("field", BAD.values(), ids=BAD)
def test_a_record_field_retyped_or_malformed_is_ignored(field):
    assert test_schedule.read_record_field(GOOD) is not None
    assert test_schedule.read_record_field(field) is None


def test_the_overlay_takes_each_measured_test_from_the_base_and_the_rest_from_the_committed_file():
    committed = test_schedule.Estimates({"tests/a.py::test_slow": 30.0, "tests/a.py::test_gone_short": 9.0,
                                         "tests/c.py::test_old": 4.0}, 0.2)
    base = test_schedule.Estimates({"tests/a.py::test_slow": 12.3, "tests/n.py::test_new": 150.0}, 0.07,
                                   frozenset({"tests/a.py::test_slow", "tests/a.py::test_gone_short",
                                              "tests/n.py::test_new", "tests/b.py::test_quick"}))
    data = json.loads(test_schedule.overlay_text(committed, base, source="here"))
    # A test the base measured as short leaves the recorded ones; one it did not measure keeps the committed time.
    assert data["seconds"] == {"tests/a.py::test_slow": 12.3, "tests/c.py::test_old": 4.0,
                               "tests/n.py::test_new": 150.0}
    assert data["unrecorded_seconds"] == 0.07 and data["source"] == "here"
    assert data["measured"] == sorted(base.measured | {"tests/c.py::test_old"})
    # Without the base's list of measured tests, nothing is overlaid by omission, nor named measured.
    data = json.loads(test_schedule.overlay_text(committed, base._replace(measured=None), source="here"))
    assert data["seconds"] == {**committed.durations, **base.durations} and "measured" not in data
    # Without a base, the committed durations as they are.
    data = json.loads(test_schedule.overlay_text(committed, None, source="here"))
    assert (data["seconds"], data["unrecorded_seconds"], "measured" in data) == (committed.durations, 0.2, False)


def git(repository: Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    return subprocess.run(["git", *args], cwd=repository, env=env, check=True, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT).stdout.strip()


@pytest.fixture
def repository(tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir()
    git(repository, "init", "-q", "-b", "main")
    (repository / "file.txt").write_text("one\n")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "base")
    return repository


IDS = ["tests/a.py::test_one", "tests/a.py::test_slow", "tests/b.py::test_quick", "tests/b.py::test_quicker"]


def note(repository: Path, commit: str, **result) -> None:
    gate_collection.write_record(commit, IDS, result={"status": "passed", "counts": {"selected": len(IDS)}, **result},
                                 cwd=repository)


def test_the_base_durations_come_from_the_base_gate_record(repository):
    base = git(repository, "rev-parse", "HEAD")
    result = {"collection": {"base": base}}
    assert gate.base_durations(result, None, repository) is None  # no record
    note(repository, base)
    assert gate.base_durations(result, None, repository) is None  # a record before durations were kept
    note(repository, base, durations=GOOD)
    found = gate.base_durations(result, None, repository)
    assert found == (base, ({"tests/a.py::test_slow": 12.3, "tests/a.py::test_one": 1.0}, 0.3, frozenset(IDS)))
    # A suite that did not time every test it selected (a worker crashed) names no measured tests.
    note(repository, base, durations=GOOD, counts={"selected": 5})
    assert gate.base_durations(result, None, repository)[1].measured is None
    note(repository, base, durations={**GOOD, "tests": True}, counts={"selected": 1})
    assert gate.base_durations(result, None, repository)[1].measured is None
    note(repository, base, durations=BAD["seconds not zlib"])
    assert gate.base_durations(result, None, repository) is None
    # A base-only record (no gate ran on it) holds no durations; neither does a commit no record names.
    gate_collection.write_record(base, IDS, cwd=repository)
    assert gate.base_durations(result, None, repository) is None
    assert gate.base_durations({"collection": {"base": "f" * 40}}, None, repository) is None
    assert gate.base_durations({}, None, repository) is None


def test_the_gate_names_the_overlay_to_its_suite_and_records_the_suites_seconds(tmp_path, monkeypatch, capsys):
    """A gate's suite runs with SOURCE_VARIABLE naming the overlay of the committed durations with the base's; the
    record keeps the suite's seconds (and the note the same record) and the log names the slowest tests."""
    for binary in [tmp_path / "rust/target/release/ve",
                   *(tmp_path / "lean/.lake/build/bin" / name for name in gate.LEAN_BINARIES)]:
        binary.parent.mkdir(parents=True, exist_ok=True)
        binary.write_text("binary")
        binary.chmod(0o755)
    pin_rust_binary(tmp_path)
    (tmp_path / "rust/Cargo.lock").write_text("version = 4\n")
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"version": 1, "optional_tests": [], "deselected_tests": []}))
    output = tmp_path / "record.json"
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "POLICY", policy)
    pin_base_collection(monkeypatch, events()["collected"])
    monkeypatch.setattr(gate, "REQUIRED_FAMILIES", ())
    monkeypatch.setattr(gate, "check_toolchains", lambda result, env: None)
    monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(output)])
    base = test_schedule.Estimates({"tests/b.py::test_b": 40.0}, 0.05, frozenset(events()["collected"]))
    monkeypatch.setattr(gate, "base_durations", lambda result, env: ("base-commit", base))
    timed = {"tests/a.py::test_a": 2.25, "tests/b.py::test_b": 0.5}
    overlays = []

    def fake_command(args, *, env, stage, cwd=None):
        fake_trust(args, stage)
        if stage == "Python environment":
            return str(tmp_path / ".venv")
        if stage == "native Rust tests":
            return "test result: ok. 2 passed; 0 failed; 0 ignored;"
        if stage in PYTEST_STAGES:
            Path(env["VE_GATE_PYTEST_RESULT"]).write_text(json.dumps({**events(), "seconds": timed}))
        if stage == "Python suite":
            overlays.append(test_schedule.read_source(Path(env[test_schedule.SOURCE_VARIABLE])))
        return "sha" if stage == "commit" else ""

    monkeypatch.setattr(gate, "command", fake_command)
    notes = []
    monkeypatch.setattr(gate, "record_collection", lambda commit, ids, env, result=None: (
        notes.append(json.loads(json.dumps(result))) or "written"))
    assert gate.main() == 0
    record = json.loads(output.read_text())
    committed = test_schedule.read_source(test_schedule.DURATIONS)
    (overlay,) = overlays
    assert overlay.durations == {**{k: v for k, v in committed.durations.items() if k not in base.measured},
                                 **base.durations}
    assert overlay.measured == base.measured | set(committed.durations)
    assert record["durations_source"] == {"committed": len(committed.durations), "base": "base-commit",
                                          "base_recorded": 1, "measured": 2}
    assert record["environment"]["pytest"][test_schedule.SOURCE_VARIABLE].endswith("/test-durations.json")
    assert test_schedule.read_record_field(record["durations"]) == ({"tests/a.py::test_a": 2.2}, 0.5, None)
    assert record["durations"]["tests"] == 2
    # The note the gate writes is this record, durations included.
    assert notes[-1]["durations"] == record["durations"] and notes[-1]["status"] == "passed"
    log = capsys.readouterr().out
    assert "[gate] slowest:      2.2 s tests/a.py::test_a\n[gate] slowest:      0.5 s tests/b.py::test_b" in log


def test_the_log_names_the_twenty_slowest_and_ignores_what_is_not_seconds(capsys):
    seconds = {f"tests/t.py::test_{i:02}": float(i) for i in range(30)} | {"tests/t.py::bad": "9", "tests/t.py::n": -1}
    result = {}
    gate.record_durations(result, {"seconds": seconds})
    lines = [line for line in capsys.readouterr().out.splitlines() if line.startswith("[gate] slowest:")]
    assert len(lines) == gate.SLOWEST == 20
    assert lines[0].endswith("tests/t.py::test_29") and lines[-1].endswith("tests/t.py::test_10")
    assert result["durations"]["tests"] == 30
    result = {}
    gate.record_durations(result, {"seconds": None})
    assert result == {}


def test_a_suite_run_without_seconds_merges_to_none():
    """An events file from a plugin that times nothing still merges, with no seconds."""
    collection = {**events(), "tests": {}, "workers": {}}
    suite = {"tests": events()["tests"], "workers": events()["workers"]}
    assert gate.merge_pytest_events(collection, suite)["seconds"] == {}
    assert gate.merge_pytest_events(collection, {**suite, "seconds": {"tests/a.py::test_a": 1.5}})["seconds"] == {
        "tests/a.py::test_a": 1.5}


def test_the_records_readers_take_a_record_with_durations(repository):
    """tools/gate_collection.py reads the note's collection and result as before: the durations are one more
    member (tests/test_batch_evidence.py checks the evidence's comparison with the note)."""
    commit = git(repository, "rev-parse", "HEAD")
    tree = git(repository, "rev-parse", f"{commit}^{{tree}}")
    gate_record = {"schema_version": 1, "commit_sha": commit, "tree_sha": tree, "dirty": False, "status": "passed",
                   "mode": "full", "stages": list(gate.REQUIRED_STAGES), "counts": {"selected": 4, "failed": 0},
                   "failures": [], "skips": [], "durations": GOOD,
                   "collection": {"collected_zlib": gate_collection.encode_ids(IDS)}}
    gate_collection.write_record(commit, IDS, result=gate_record, cwd=repository)
    assert gate_collection.read_record(commit, cwd=repository) == IDS
    assert gate_collection.read_gate_result(commit, cwd=repository) == gate_record
    assert gate.base_durations({"collection": {"base": commit}}, None, repository)[1].measured == frozenset(IDS)
