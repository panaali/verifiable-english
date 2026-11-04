"""Each gate keeps its suite's per-test seconds in its record, and the next gate on that base orders its suite by them.

The durations are scheduling data only (tools/test_schedule.py): they decide which xdist worker runs a test and
when, never whether it runs or passes. Checked here: the record's compact field round-trips and a malformed one is
ignored; the overlay of the committed file with a base record's durations; `base_durations` against a real git
note; a gate record file (`--durations-record`) for a base without a note, which weighs the shard plan, falls back to
the committed durations when it is missing, malformed or oversize, and loses to a base note; the gate's own run,
which names the overlay to its suite and keeps its suite's seconds in the record and the note; and the record's
readers (tools/gate_collection.py, tools/batch_evidence.py) with the new field.
"""
from __future__ import annotations

import ast
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zlib

import pytest

from subprocesses import HANG_TIMEOUT
from test_gate_integrity import PYTEST_STAGES, events, fake_trust, pin_base_collection, pin_rust_binary
from tools import gate, gate_collection, gate_shards, test_schedule

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
# JSON nested deeper than the parser's stack: json.loads raises RecursionError on it, not ValueError
# (`test_every_record_reader_leaves_a_value_nested_too_deep_unused` checks that it still does).
DEEP = b"[" * 100_000 + b"]" * 100_000
DEEP_ZLIB = base64.b64encode(zlib.compress(DEEP)).decode()
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
    "seconds nested 100k deep": {**GOOD, "seconds_zlib": DEEP_ZLIB},
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
    note(repository, base, durations=BAD["seconds nested 100k deep"])
    assert gate.base_durations(result, None, repository) is None
    deep = repository.parent / "deep-note.json"
    deep.write_bytes(DEEP)
    git(repository, "notes", f"--ref={gate_collection.NOTES_REF}", "add", "-f", "-F", str(deep), base)
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


# --- the durations of a gate record file (`--durations-record`), for a base without a note -----------------------

HEAVY = [f"tests/heavy.py::test_case[{i}]" for i in range(4)]
LIGHT = [f"tests/light_{name}.py::test_one" for name in "abcdef"]
COLLECTED = sorted([*HEAVY, *LIGHT])
# The committed file weighs the heavy file at a second a test; the measured run took a minute each.
COMMITTED = {**{nodeid: 1.0 for nodeid in HEAVY}, **{nodeid: 30.0 for nodeid in LIGHT}}
MEASURED = {**{nodeid: 60.0 for nodeid in HEAVY}, **{nodeid: 30.0 for nodeid in LIGHT}}
BASE_DURATIONS = gate.base_durations  # before a test replaces it


def record_file(path: Path, seconds: dict, ids: list[str] = COLLECTED, **fields) -> Path:
    """A full gate record file as a merged shard record carries it: its suite's seconds and its collection."""
    path.write_text(json.dumps({"status": "passed", "mode": "full", "counts": {"selected": len(ids)},
                                "durations": test_schedule.record_field(seconds),
                                "collection": {"collected_zlib": gate_collection.encode_ids(ids)}, **fields}))
    return path


@pytest.fixture
def committed_file(tmp_path, monkeypatch):
    """The committed durations are COMMITTED and the merge base has no gate record."""
    path = tmp_path / "committed-durations.json"
    path.write_text(test_schedule.durations_text(COMMITTED, source="fixture"))
    monkeypatch.setattr(test_schedule, "DURATIONS", path)
    monkeypatch.setattr(gate, "base_durations", lambda result, env: None)
    return path


def planned(tmp_path, record: Path | None, name: str) -> tuple[dict, dict]:
    """(the 3-shard plan of COLLECTED, the result) from the durations `suite_durations` writes."""
    result, path = {"collection": {"base": "c" * 40}}, tmp_path / f"{name}.json"
    gate.suite_durations(result, {}, path, record)
    return gate_shards.plan(COLLECTED, test_schedule.read_source(path), 3), result


def true_loads(plan: dict) -> list[float]:
    """Each shard's measured seconds under `plan`."""
    loads = [0.0] * plan["n"]
    for nodeid in COLLECTED:
        loads[plan["assignments"][test_schedule.unit_of(nodeid)] - 1] += MEASURED[nodeid]
    return loads


def test_a_durations_record_file_weighs_the_file_the_committed_durations_underweight(tmp_path, committed_file):
    """The committed durations put the heavy file with two light ones (it weighs 4 s there, 240 s measured); the
    record file's plan puts it alone, and the heaviest shard's measured load against the mean drops."""
    committed_plan, _ = planned(tmp_path, None, "committed")
    record = record_file(tmp_path / "gate-record.json", MEASURED)
    record_plan, result = planned(tmp_path, record, "record")
    heavy = record_plan["assignments"]["tests/heavy.py"]
    assert [file for file, shard in record_plan["assignments"].items() if shard == heavy] == ["tests/heavy.py"]
    assert len([file for file, shard in committed_plan["assignments"].items()
                if shard == committed_plan["assignments"]["tests/heavy.py"]]) == 3
    before, after = true_loads(committed_plan), true_loads(record_plan)
    assert max(after) / (sum(after) / 3) < max(before) / (sum(before) / 3)
    assert result["durations_source"] == {
        "committed": len(COMMITTED), "base": None, "base_recorded": len(MEASURED), "measured": len(COLLECTED),
        "record_file": {"used": True, "sha256": hashlib.sha256(record.read_bytes()).hexdigest(),
                        "recorded": len(MEASURED)}}
    # The plan is a function of the file: every shard given it plans the same.
    assert planned(tmp_path, record, "again")[0] == record_plan


def oversize_seconds(path: Path) -> Path:
    data = json.loads(record_file(path, MEASURED).read_text())
    data["durations"]["seconds_zlib"] = BAD["seconds too large"]["seconds_zlib"]
    path.write_text(json.dumps(data))
    return path


def deep_seconds(path: Path) -> Path:
    data = json.loads(record_file(path, MEASURED).read_text())
    data["durations"]["seconds_zlib"] = DEEP_ZLIB
    path.write_text(json.dumps(data))
    return path


BAD_FILES = {
    "missing": lambda path: path,
    "not JSON": lambda path: (path.write_text("{not json"), path)[1],
    "not an object": lambda path: (path.write_text(json.dumps([1, 2])), path)[1],
    "no durations": lambda path: (path.write_text(json.dumps({"status": "passed"})), path)[1],
    "durations malformed": lambda path: (path.write_text(json.dumps(
        {"durations": BAD["seconds not zlib"], "counts": {"selected": 1}})), path)[1],
    "seconds over MAX_RECORD_BYTES": oversize_seconds,
    "not a file": lambda path: (path.mkdir(), path)[1],
    "nested 100k deep": lambda path: (path.write_text("[" * 100_000 + "]" * 100_000), path)[1],
    "not UTF-8": lambda path: (path.write_bytes(b'{"durations": "\xff"}'), path)[1],
    "seconds nested 100k deep": deep_seconds,
}


@pytest.mark.parametrize("make", BAD_FILES.values(), ids=BAD_FILES)
def test_a_missing_malformed_or_oversize_record_file_leaves_the_committed_plan(tmp_path, committed_file, make,
                                                                               capsys):
    committed_plan, committed_result = planned(tmp_path, None, "committed")
    record = make(tmp_path / "gate-record.json")
    plan, result = planned(tmp_path, record, "record")
    assert plan == committed_plan
    assert result["durations_source"] == {**committed_result["durations_source"],
                                          "record_file": {"used": False, "sha256": None, "recorded": None}}
    assert capsys.readouterr().out.count("[gate] durations record") == 1


def test_a_record_file_larger_than_the_limit_is_not_read(tmp_path, committed_file, monkeypatch):
    committed_plan, _ = planned(tmp_path, None, "committed")
    record = record_file(tmp_path / "gate-record.json", MEASURED)
    monkeypatch.setattr(gate, "MAX_DURATIONS_RECORD_BYTES", len(record.read_bytes()) - 1)
    assert planned(tmp_path, record, "record")[0] == committed_plan
    monkeypatch.setattr(gate, "MAX_DURATIONS_RECORD_BYTES", len(record.read_bytes()))
    assert planned(tmp_path, record, "record")[0] != committed_plan


def test_a_record_file_that_did_not_time_its_whole_selection_names_no_measured_tests(tmp_path, committed_file):
    record = record_file(tmp_path / "gate-record.json", MEASURED, counts={"selected": len(COLLECTED) + 1})
    assert gate.record_file_durations(record)[1].measured is None
    record = record_file(tmp_path / "gate-record.json", MEASURED, collection={"collected_zlib": "***"})
    assert gate.record_file_durations(record)[1].measured is None
    # IDs nested too deep are malformed IDs too: the durations are used, with no measured tests.
    record = record_file(tmp_path / "gate-record.json", MEASURED, collection={"collected_zlib": DEEP_ZLIB})
    assert gate.record_file_durations(record)[1].measured is None
    result = planned(tmp_path, record, "deep ids")[1]
    assert result["durations_source"]["measured"] is None and result["durations_source"]["record_file"]["used"]
    assert gate.record_file_durations(record_file(tmp_path / "gate-record.json", MEASURED))[1].measured == \
        frozenset(COLLECTED)


def test_a_base_note_wins_over_the_record_file(tmp_path, repository, committed_file, monkeypatch):
    """When the merge base has a gate record (its git note), its durations weigh the plan and the file is not read."""
    base = git(repository, "rev-parse", "HEAD")
    gate_collection.write_record(base, COLLECTED, result={"status": "passed", "counts": {"selected": len(COLLECTED)},
                                                          "durations": test_schedule.record_field(COMMITTED)},
                                 cwd=repository)
    monkeypatch.setattr(gate, "base_durations", lambda result, env: BASE_DURATIONS(result, env, repository))
    record = record_file(tmp_path / "gate-record.json", MEASURED)
    result, path = {"collection": {"base": base}}, tmp_path / "durations.json"
    gate.suite_durations(result, {}, path, record)
    assert test_schedule.read_source(path).durations == COMMITTED
    assert result["durations_source"]["base"] == base
    assert result["durations_source"]["record_file"] == {"used": False, "sha256": None, "recorded": None}


def test_every_record_reader_leaves_a_value_nested_too_deep_unused(tmp_path):
    """Each reader that leaves a malformed gate record, note or durations file unused does so for one nested deeper
    than the parser's stack, which raises RecursionError, not ValueError (eff-20261103-1 F1): the file or note
    itself, or a compressed field inside it."""
    with pytest.raises(RecursionError):
        json.loads(DEEP)
    path = tmp_path / "deep.json"
    path.write_bytes(DEEP)
    assert test_schedule.json_value(DEEP) is None and test_schedule.json_value(DEEP.decode()) is None
    assert test_schedule.zlib_json_value(DEEP_ZLIB, len(DEEP)) is None
    assert test_schedule.read_record_field(BAD["seconds nested 100k deep"]) is None
    assert gate_collection.decode_ids(DEEP_ZLIB) is None
    assert gate_collection.parse_record(DEEP.decode(), "c" * 40, "t" * 40) is None
    assert test_schedule.read_source(path) == ({}, test_schedule.UNRECORDED_SECONDS, None)
    assert gate.read_previous(path) is None
    assert gate.record_file_durations(path) is None
    assert gate.record_file_durations(deep_seconds(tmp_path / "deep-seconds.json")) is None


def test_the_compressed_field_decoder_takes_exactly_its_limit():
    encoded = packed(["tests/a.py::t"])
    size = len(json.dumps(["tests/a.py::t"]).encode())
    assert test_schedule.zlib_json_value(encoded, size) == ["tests/a.py::t"]
    assert test_schedule.zlib_json_value(encoded, size - 1) is None
    assert test_schedule.json_value(b"[1]") == [1] and test_schedule.json_value("null") is None
    for malformed in (None, 7, True, [encoded], "***", base64.b64encode(b"not zlib").decode(), "é"):
        assert test_schedule.zlib_json_value(malformed, size) is None


# The json.loads calls of the gate's record modules outside `test_schedule.json_value`, and why each may raise:
# every other reader of a record, note, durations or retry file parses through json_value, so none lets the parser's
# RecursionError out of a reader that leaves a malformed input unused.
PARSER_CALLS = {
    ("tools/gate.py", "read_trust"): "trust_map's own output: a malformed one fails the gate",
    ("tools/gate.py", "collect"): "the gate's own collection events: a malformed one fails the gate",
    ("tools/gate.py", "main"): "the committed policy and the suite's own events: malformed ones fail the gate",
    ("tools/gate_collection.py", "collect"): "the collection's own events: a malformed one fails the collection",
    ("tools/gate_collection.py", "read_gate_result"): "the note text parse_record has just parsed",
    ("tools/test_schedule.py", "record_field"): "durations_text's own output",
    ("tools/test_schedule.py", "json_value"): "the one parser that leaves no parser error out",
}


def json_parser_calls(file: str) -> set[tuple[str, str]]:
    """(file, innermost enclosing function or "<module>") of each json.load(s) call in `file`."""
    found = set()

    def visit(node, owner: str) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            owner = node.name
        if isinstance(node, ast.ImportFrom) and node.module == "json":
            found.add((file, f"from json import in {owner}"))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"load", "loads"} \
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "json":
            found.add((file, owner))
        for child in ast.iter_child_nodes(node):
            visit(child, owner)

    visit(ast.parse((ROOT / file).read_text()), "<module>")
    return found


def test_the_record_modules_parse_untrusted_json_only_through_json_value():
    files = sorted({file for file, _ in PARSER_CALLS})
    assert set().union(*(json_parser_calls(file) for file in files)) == set(PARSER_CALLS)
