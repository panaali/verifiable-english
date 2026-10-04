"""Stage 3 shadow recorder: the shadow call, the classes, records and tallies.

The fixtures S1 to S20, C1 to C13, L1 to L7 and Z5 of docs/spec/mig3.md section 8,
with expectations written from sections 2 and 4.  Unless a test says otherwise
the two sides are plain functions given to `execute`, the authority is `shadow`
and `VE_SHADOW_DIR` is a fresh directory.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys

import pytest

from ve.backends import dispatch
from ve.backends.dispatch import execute, note_uncompared
from ve.backends.lean_service import CheckerUnavailable
from ve.errors import InvalidModel, ResourceLimit, Span, SyntaxError as VESyntaxError, VEError

ROOT = Path(__file__).resolve().parents[1]
COMMON = {"kind", "op", "input_digest", "python", "lean", "rust", "class", "python_ms", "backend_ms",
          "run", "test", "input"}


@pytest.fixture
def run_dir(monkeypatch, tmp_path):
    directory = tmp_path / "run"
    directory.mkdir()
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    for name in ("VE_AUTHORITY_OVERRIDES", "VE_SHADOW_LOG", "VE_SHADOW_RUN"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("VE_SHADOW_DIR", str(directory))
    yield directory
    dispatch._workers.pop((os.getpid(), str(directory)), None)


def records(directory) -> list[dict]:
    rows = []
    for path in sorted(Path(directory).glob("records-*.jsonl")):
        rows.extend(json.loads(line) for line in path.read_text().splitlines())
    return rows


def counts(directory, op) -> dict:
    return dispatch._workers[(os.getpid(), str(directory))].op(op)


def fails(exc):
    def raiser():
        raise exc
    return raiser


# --- 8.1 the shadow call ----------------------------------------------------------

def test_s1_agreement_returns_the_same_object_and_writes_nothing(run_dir):
    value = {"status": "Satisfied", "evaluations": 1}
    assert execute("evaluate", {}, lambda: value, lean=lambda: dict(value)) is value
    assert records(run_dir) == []
    tally = counts(run_dir, "evaluate")
    assert (tally["compared"], tally["agree"]) == (1, 1)


def test_s2_divergence_record(run_dir):
    python = {"status": "Satisfied", "evaluations": 1}
    result = execute("evaluate", {"ast": ["top"]}, lambda: python,
                     lean=lambda: {"status": "Violated", "evaluations": 2})
    assert result is python
    [row] = records(run_dir)
    assert row["kind"] == "divergence" and row["op"] == "evaluate"
    assert row["class"] == ["budget-outcome", "count-value", "verdict"]
    assert row["python"] == {"evaluations": 1, "status": "Satisfied"}
    assert row["lean"] == {"evaluations": 2, "status": "Violated"} and row["rust"] is None
    assert row["input"] == {"ast": ["top"]} and len(row["input_digest"]) == 64
    assert counts(run_dir, "evaluate")["zero_tolerance"] == 1


def test_s3_same_error_agrees_and_reraises_pythons_exception(run_dir):
    error = VEError("bad input")
    with pytest.raises(VEError) as raised:
        execute("parse", {}, fails(error), lean=fails(VEError("bad input")))
    assert raised.value is error
    assert records(run_dir) == [] and counts(run_dir, "parse")["agree"] == 1


def test_s4_different_text_is_a_message_difference(run_dir):
    error = VEError("bad input")
    with pytest.raises(VEError) as raised:
        execute("parse", {}, fails(error), lean=fails(VEError("other text")))
    assert raised.value is error
    [row] = records(run_dir)
    assert row["class"] == ["diagnostic-message"]
    assert counts(run_dir, "parse")["recorded_only"] == 1


def test_s5_different_code_is_a_code_difference(run_dir):
    with pytest.raises(VEError):
        execute("parse", {}, fails(VEError("same")), lean=fails(VESyntaxError("same")))
    assert records(run_dir)[0]["class"] == ["diagnostic-code"]


def test_s6_one_side_raising_is_verdict_and_schema(run_dir):
    python = {"status": "ok"}
    assert execute("label", {}, lambda: python, lean=fails(VEError("rejected"))) is python
    assert records(run_dir)[0]["class"] == ["schema", "verdict"]


def test_s7_resource_limit_on_one_side_is_also_budget_outcome(run_dir):
    execute("evaluate", {}, lambda: {"status": "Satisfied"}, lean=fails(ResourceLimit("budget")))
    assert records(run_dir)[0]["class"] == ["budget-outcome", "schema", "verdict"]


def test_s8_backend_unavailable_is_a_completion_failure(run_dir):
    python = {"status": "ok"}
    assert execute("check", {}, lambda: python, lean=fails(CheckerUnavailable("gone"))) is python
    [row] = records(run_dir)
    assert row["kind"] == "unavailable" and row["class"] == [] and row["sides"] == ["backend"]
    assert row["python"] == {"status": "ok"} and row["rust"] is None
    assert row["lean"] == {"code": "CheckerUnavailable", "message": "gone"}
    tally = counts(run_dir, "check")
    assert (tally["completion_failures"], tally["compared"]) == (1, 0)


def test_s9_no_lean_adapter_has_no_candidate_whatever_rust_passes(run_dir):
    ran = []
    execute("check", {}, lambda: {"status": "ok"})
    execute("check", {}, lambda: {"status": "ok"}, rust=lambda: ran.append(1) or {"status": "no"})
    rows = records(run_dir)
    assert len(rows) == 2 and not ran
    for row in rows:
        assert row["kind"] == "unavailable" and row["sides"] == ["backend"] and row["rust"] is None
        assert row["lean"] == {"code": "CheckerUnavailable", "message": "no adapter for check"}
        assert row["backend_ms"] is None


def test_s10_python_unavailable(run_dir):
    error = CheckerUnavailable("python gone")
    with pytest.raises(CheckerUnavailable) as raised:
        execute("check", {}, fails(error), lean=lambda: {"status": "ok"})
    assert raised.value is error
    [row] = records(run_dir)
    assert row["kind"] == "unavailable" and row["sides"] == ["python"]
    tally = counts(run_dir, "check")
    assert (tally["unavailable_other"], tally["completion_failures"]) == (1, 0)


def test_s11_both_unavailable_is_one_record(run_dir):
    with pytest.raises(CheckerUnavailable):
        execute("check", {}, fails(CheckerUnavailable("a")), lean=fails(CheckerUnavailable("b")))
    [row] = records(run_dir)
    assert row["sides"] == ["backend", "python"]
    assert counts(run_dir, "check")["unavailable_other"] == 1


class _Exploding:
    def to_dict(self):
        raise RuntimeError("cannot compare")


def test_s12_a_comparison_fault_is_a_recorder_fault(run_dir):
    python = {"status": "ok"}
    assert execute("check", {}, lambda: python, lean=_Exploding) is python
    [row] = records(run_dir)
    assert row["kind"] == "recorder-fault" and row["error"] == "RuntimeError: cannot compare"
    assert set(row) == COMMON | {"error"}
    assert counts(run_dir, "check")["recorder_faults"] == 1


def test_s13_an_unwritable_directory_never_reaches_the_caller(monkeypatch, tmp_path, capsys):
    if os.geteuid() == 0:
        target = tmp_path / "not-a-directory"
        target.write_text("")
    else:
        target = tmp_path / "locked"
        target.mkdir()
        target.chmod(0o500)
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    monkeypatch.delenv("VE_SHADOW_LOG", raising=False)
    monkeypatch.setenv("VE_SHADOW_DIR", str(target))
    try:
        python = {"status": "Satisfied"}
        assert execute("evaluate", {}, lambda: python, lean=lambda: {"status": "Violated"}) is python
        error = capsys.readouterr().err
        assert "ve shadow: cannot write tally: " in error
        assert "ve shadow: cannot write records: " in error
        assert dispatch._workers[(os.getpid(), str(target))].op("evaluate")["recorder_faults"] == 1
    finally:
        dispatch._workers.pop((os.getpid(), str(target)), None)
        if target.is_dir():
            target.chmod(0o700)


def test_s14_keyboard_interrupt_leaves_execute(run_dir):
    ran = []
    with pytest.raises(KeyboardInterrupt):
        execute("check", {}, fails(KeyboardInterrupt()), lean=lambda: ran.append(1))
    assert not ran
    with pytest.raises(KeyboardInterrupt):
        execute("check", {}, lambda: {"status": "ok"}, lean=fails(KeyboardInterrupt()))


@pytest.mark.parametrize("authority,expected", [("python", "p"), ("lean", "l"), ("rust-experimental", "r")])
def test_s15_other_authorities_write_nothing(run_dir, monkeypatch, authority, expected):
    monkeypatch.setenv("VE_AUTHORITY", authority)
    assert execute("check", {}, lambda: "p", lean=lambda: "l", rust=lambda: "r") == expected
    assert list(run_dir.iterdir()) == []
    if authority == "lean":
        with pytest.raises(CheckerUnavailable):
            execute("check", {}, lambda: "p")


def test_s16_constituents_inside_the_candidate_run_at_lean(run_dir):
    def b():
        return execute("countermodel_check", {"b": 1}, lambda: {"valid": True},
                       lean=lambda: {"valid": False})

    execute("countermodel_search", {"a": 1}, lambda: {"status": "Found"}, lean=lambda: b() and {"status": "Found"})
    assert counts(run_dir, "countermodel_search")["compared"] == 1
    assert counts(run_dir, "countermodel_check")["compared"] == 0
    assert [row["op"] for row in records(run_dir)] == []

    def python_a():
        b()
        return {"status": "Found"}

    execute("countermodel_search", {"a": 2}, python_a, lean=lambda: b() and {"status": "Found"})
    assert counts(run_dir, "countermodel_search")["compared"] == 2
    assert counts(run_dir, "countermodel_check")["compared"] == 1
    assert [row["op"] for row in records(run_dir)] == ["countermodel_check"]


def test_s17_an_explicit_log_comes_first(run_dir, monkeypatch, tmp_path):
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    execute("evaluate", {}, lambda: {"status": "Satisfied"}, lean=lambda: {"status": "Violated"})
    assert json.loads(log.read_text())["class"] == ["budget-outcome", "verdict"]
    assert list(run_dir.iterdir()) == []
    other = tmp_path / "other.jsonl"
    monkeypatch.setenv("VE_SHADOW_LOG", str(other))
    execute("evaluate", {}, lambda: {"status": "Satisfied"}, lean=lambda: {"status": "Satisfied"})
    assert not other.exists()


def test_s19_uncompared_calls_are_counted_by_reason(run_dir, monkeypatch):
    note_uncompared("parse", "parse-scope")
    assert counts(run_dir, "parse")["uncompared"] == {"parse-scope": 1}
    assert records(run_dir) == []
    monkeypatch.setenv("VE_AUTHORITY", "python")
    note_uncompared("parse", "parse-scope")
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    assert counts(run_dir, "parse")["uncompared"] == {"parse-scope": 1}
    note_uncompared("parse", "no-such-reason")
    tally = counts(run_dir, "parse")
    assert tally["uncompared"] == {"parse-scope": 1, "unregistered": 1}
    assert tally["recorder_faults"] == 1


SUBPROCESS = """
import json, os, sys
sys.path.insert(0, {root!r})
from ve.backends import dispatch
from pathlib import Path
directory = Path(os.environ["VE_SHADOW_DIR"])
{body}
"""


def _child(directory, body, **env):
    environment = {**os.environ, "VE_AUTHORITY": "shadow", "VE_SHADOW_DIR": str(directory), **env}
    environment.pop("VE_SHADOW_LOG", None)
    environment.pop("VE_AUTHORITY_OVERRIDES", None)
    return subprocess.run([sys.executable, "-c", SUBPROCESS.format(root=str(ROOT), body=body)],
                          env=environment, capture_output=True, text=True, timeout=600)


def _tallies(directory):
    return [json.loads(path.read_text()) for path in sorted(Path(directory).glob("tally-*.json"))]


def test_s20_a_worker_registers_before_its_first_shadow_call(tmp_path):
    body = """
assert dispatch.authority_for("evaluate") == "shadow"
[tally] = [json.loads(p.read_text()) for p in directory.glob("tally-*.json")]
assert tally["final"] is False and tally["calls"] == 0, tally
assert not list(directory.glob("records-*.jsonl"))
"""
    completed = _child(tmp_path, body)
    assert completed.returncode == 0, completed.stderr
    [tally] = _tallies(tmp_path)
    assert tally["final"] is True and tally["calls"] == 0


POOL = """
import multiprocessing
def call(_):
    return dispatch.execute("evaluate", {}, lambda: 1, lean=lambda: 1)
pool = multiprocessing.get_context("fork").Pool(2)
assert pool.map(call, range(8)) == [1] * 8
pool.close()
pool.join()
"""


def test_s20_pool_workers_finalize_at_a_normal_exit(tmp_path):
    """A multiprocessing child exits by os._exit and never runs atexit: a pool
    worker that exits normally (close, join) finalizes all the same. A worker
    killed by a signal does not (L14)."""
    completed = _child(tmp_path, POOL)
    assert completed.returncode == 0, completed.stderr
    tallies = _tallies(tmp_path)
    workers = [t for t in tallies if t["calls"]]
    assert workers, tallies
    assert all(t["final"] for t in tallies), tallies
    assert sum(t["ops"]["evaluate"]["agree"] for t in workers) == 8


# --- 8.2 the classes and the projection ----------------------------------------------

def classes_of(directory, op, python, lean) -> list[str]:
    before = len(records(directory))
    execute(op, {}, lambda: python, lean=lambda: lean)
    rows = records(directory)[before:]
    assert len(rows) <= 1
    return rows[0]["class"] if rows else []


def test_c1_the_projection_drops_build_and_record_ids(run_dir):
    assert classes_of(run_dir, "evaluate", {"checker_build": "a", "x": {"y": {"record_id": 1}}},
                      {"checker_build": "b", "x": {"y": {"record_id": 2}}}) == []
    assert counts(run_dir, "evaluate")["agree"] == 1


def test_c2_identities(run_dir):
    assert classes_of(run_dir, "graph", {"graph_id": "a"}, {"graph_id": "b"}) == ["identity"]
    assert classes_of(run_dir, "graph", {"report_id": "a"}, {"report_id": "b"}) == ["identity"]


def test_c3_wording_map(run_dir, monkeypatch, tmp_path):
    wording = tmp_path / "wording.json"
    entry = {"op": "graph", "path": ["proof"], "python": "Python replay checked",
             "backend": "Lean graph report checked", "reviewed": "test"}
    monkeypatch.setattr(dispatch, "_WORDING", wording)
    monkeypatch.setattr(dispatch, "_wording_cache", None)

    def check(op, python, lean, entries):
        wording.write_text(json.dumps(entries))
        monkeypatch.setattr(dispatch, "_wording_cache", None)
        return classes_of(run_dir, op, python, lean)

    assert check("graph", {"proof": entry["python"]}, {"proof": entry["backend"]}, [entry]) == []
    assert check("graph", {"proof": entry["python"]}, {"proof": entry["backend"]}, []) == ["schema"]
    assert check("bundle", {"proof": entry["python"]}, {"proof": entry["backend"]}, [entry]) == ["schema"]
    assert check("graph", {"root": {"proof": entry["python"]}}, {"root": {"proof": entry["backend"]}},
                 [entry]) == ["schema"]


def test_c4_nested_explanation_and_composition(run_dir):
    python = {"explanation": {"children": [{"kind": "top", "value": True}]},
              "composition": {"supporting_edge_ids": ["edge-a"]}}
    lean = {"explanation": {"children": [{"kind": "bottom", "value": True}]},
            "composition": {"supporting_edge_ids": ["edge-b"]}}
    assert classes_of(run_dir, "graph", python, lean) == ["composition", "explanation"]


def test_c5_readings_verdict_is_also_composition(run_dir):
    assert classes_of(run_dir, "readings", {"verdict": "ALL"}, {"verdict": "SOME"}) == ["composition", "verdict"]
    assert classes_of(run_dir, "compare", {"verdict": "ALL"}, {"verdict": "SOME"}) == ["verdict"]


def test_c6_lengths(run_dir):
    assert classes_of(run_dir, "graph", {"assumptions": [1]}, {"assumptions": [1, 2]}) == ["composition", "schema"]
    assert classes_of(run_dir, "evaluate", {"values": [True]}, {"values": [True, False]}) == ["schema"]


def test_c7_a_boolean_is_not_an_integer(run_dir):
    assert classes_of(run_dir, "evaluate", {"value": True}, {"value": 1}) == ["schema"]


def test_c8_counts(run_dir):
    assert classes_of(run_dir, "evaluate", {"evaluations": 3}, {"evaluations": 4}) == ["count-value"]
    assert classes_of(run_dir, "evaluate", {"explanation": {"evaluations": 3}},
                      {"explanation": {"evaluations": 4}}) == ["explanation"]
    assert counts(run_dir, "evaluate")["count_members"]["evaluations"] == {"equal": 0, "different": 1}


def test_c9_detail_and_generator(run_dir):
    assert classes_of(run_dir, "evaluate", {"detail": "a"}, {"detail": "b"}) == ["diagnostic-message"]
    assert classes_of(run_dir, "model_validation", {"generator": "a"}, {"generator": "b"}) == ["diagnostic-code"]


def test_c10_other_members(run_dir):
    assert classes_of(run_dir, "evaluate", {"foo": 1}, {"foo": 2}) == ["schema"]
    assert classes_of(run_dir, "evaluate", {"foo": 1}, {}) == ["schema"]


def test_c11_status_and_message(run_dir):
    assert classes_of(run_dir, "evaluate", {"status": "Valid", "message": "a"},
                      {"status": "Invalid", "message": "b"}) == ["budget-outcome", "diagnostic-message", "verdict"]


def test_c12_one_projection_for_the_baseline_and_shadow():
    from tests import probe_matrix
    assert probe_matrix.baseline_projection is dispatch.baseline_projection
    baseline = json.loads((ROOT / "conformance/baseline-2026-09/python.json").read_text())
    for cell in baseline["cells"]:
        assert dispatch.baseline_projection(cell["output"]) == probe_matrix.baseline_projection(cell["output"])


def raised_classes(directory, op, python_error, lean_error) -> list[str]:
    before = len(records(directory))
    with pytest.raises(VEError):
        execute(op, {}, fails(python_error), lean=fails(lean_error))
    rows = records(directory)[before:]
    return rows[0]["class"] if rows else []


def test_c13_the_error_record_is_the_whole_public_record(run_dir):
    span = Span(0, 1, 1, 1)
    assert raised_classes(run_dir, "model_validation", InvalidModel("m", generator="a"),
                          InvalidModel("m", generator="b")) == ["diagnostic-code"]
    assert raised_classes(run_dir, "model_validation", InvalidModel("m", span=span),
                          InvalidModel("m", span=Span(0, 1, 2, 1))) == ["schema"]
    assert raised_classes(run_dir, "model_validation", InvalidModel("m", path="/a"),
                          InvalidModel("m", path="/b")) == ["schema"]
    assert raised_classes(run_dir, "model_validation", InvalidModel("m"),
                          InvalidModel("n")) == ["diagnostic-message"]
    assert raised_classes(run_dir, "admission", VEError("m", diagnostic={"text": "a"}),
                          VEError("m", diagnostic={"text": "b"})) == ["schema"]
    assert raised_classes(run_dir, "admission", VEError("m", diagnostic={"text": "a"}),
                          VEError("m")) == ["schema"]


def test_error_record_fallback_keeps_an_existing_code():
    class Coded(Exception):
        code = "Custom"
    assert dispatch.error_record(Coded("x")) == {"code": "Custom", "message": "x"}
    assert dispatch.error_record(KeyError("x")) == {"code": "KeyError", "message": "'x'"}


# --- 8.3 records and tallies ------------------------------------------------------------

def test_l1_record_bytes(run_dir):
    execute("evaluate", {"ast": ["top"]}, lambda: {"status": "Satisfied", "evaluations": 1},
            lean=lambda: {"status": "Violated", "evaluations": 2})
    [path] = run_dir.glob("records-*.jsonl")
    data = path.read_bytes()
    assert data.count(b"\n") == 1 and data.endswith(b"\n")
    row = json.loads(data)
    assert data == json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"
    assert set(row) == COMMON


def test_l3_input_limit(run_dir):
    base = len(json.dumps({"x": ""}, separators=(",", ":")))
    for size, kept in ((65_536, True), (65_537, False)):
        payload = {"x": "a" * (size - base)}
        execute("evaluate", payload, lambda: {"value": True}, lean=lambda: {"value": False})
        row = records(run_dir)[-1]
        assert (row["input"] == payload) is kept and len(row["input_digest"]) == 64
        if not kept:
            assert row["input"] is None


def test_l4_two_processes_two_files(tmp_path):
    body = """
from ve.backends.dispatch import execute
execute("evaluate", {}, lambda: {"value": True}, lean=lambda: {"value": False})
"""
    for _ in range(2):
        completed = _child(tmp_path, body)
        assert completed.returncode == 0, completed.stderr
    assert len(list(tmp_path.glob("records-*.jsonl"))) == 2
    tallies = _tallies(tmp_path)
    assert len(tallies) == 2 and sum(t["ops"]["evaluate"]["compared"] for t in tallies) == 2
    assert all(t["final"] and t["calls"] == 1 for t in tallies)


def test_l5_latency_histogram(run_dir, monkeypatch):
    ticks = iter([0.0, 0.0, 0.0, 0.00005, 1.0, 1.0, 1.0, 1.003, 2.0, 2.0, 2.0, 9.0])
    monkeypatch.setattr(dispatch.time, "monotonic", lambda: next(ticks))
    for _ in range(3):
        execute("evaluate", {}, lambda: {"value": True}, lean=lambda: {"value": True})
    latency = counts(run_dir, "evaluate")["latency"]["backend"]
    cells = latency["histogram"]
    assert cells[dispatch.LATENCY_BOUNDS.index(0.1)] == 1 and cells[dispatch.LATENCY_BOUNDS.index(5)] == 1
    assert cells[-1] == 1 and sum(cells) == 3
    assert latency["min"] == pytest.approx(0.05) and latency["max"] == pytest.approx(7_000)


def test_l6_unserializable_values(run_dir):
    execute("evaluate", {}, lambda: {"value": b"\x00"}, lean=lambda: {"value": "x"})
    assert records(run_dir)[0]["python"] == {"value": "<unserializable bytes>"}


def test_l7_a_record_survives_a_kill(tmp_path):
    body = """
import signal
from ve.backends.dispatch import execute
execute("evaluate", {}, lambda: {"value": True}, lean=lambda: {"value": False})
os.kill(os.getpid(), signal.SIGKILL)
"""
    completed = _child(tmp_path, body)
    assert completed.returncode == -signal.SIGKILL
    [path] = tmp_path.glob("records-*.jsonl")
    assert json.loads(path.read_text())["class"] == ["verdict"]
    [tally] = _tallies(tmp_path)
    assert tally["final"] is False


def test_l14_a_worker_killed_before_its_first_call(tmp_path):
    body = """
import signal
dispatch.authority_for("evaluate")
os.kill(os.getpid(), signal.SIGKILL)
"""
    completed = _child(tmp_path, body)
    assert completed.returncode == -signal.SIGKILL
    [tally] = _tallies(tmp_path)
    assert tally["final"] is False and tally["calls"] == 0


def test_unwritten_tallies_are_not_counted_without_shadow(monkeypatch, tmp_path):
    """V2: at every other authority no worker registers and nothing is written."""
    monkeypatch.setenv("VE_SHADOW_DIR", str(tmp_path))
    monkeypatch.setenv("VE_AUTHORITY", "python")
    dispatch.authority_for("evaluate")
    note_uncompared("parse", "parse-scope")
    assert list(tmp_path.iterdir()) == []
    assert (os.getpid(), str(tmp_path)) not in dispatch._workers


# --- 8.5 conservativity ---------------------------------------------------------------

def test_z5_the_default_authority_and_the_manifest_are_unchanged(monkeypatch):
    for name in ("VE_AUTHORITY", "VE_AUTHORITY_OVERRIDES"):
        monkeypatch.delenv(name, raising=False)
    assert dispatch.authority_for("evaluate") == "python"
    assert all(dispatch.authority_for(name) == "python" for name in dispatch.DISPATCH_NAMES)
    manifest = json.loads((Path(dispatch.__file__).parents[1] / "assurance-manifest.json").read_text())
    authorities = [operation["authority"] for operation in manifest["operations"]]
    assert (authorities.count("python"), authorities.count("lean-only"), len(authorities)) == (24, 2, 26)
