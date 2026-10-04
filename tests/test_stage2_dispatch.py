"""Authority boundaries: fail closed, preserve Python in shadow, classify drift."""
from __future__ import annotations

import json
import subprocess

import pytest

from ve.backends.diagnostics import checker_error
from ve.backends.dispatch import authority_for, execute
from ve.backends.lean_service import CheckerUnavailable
from ve.backends.rust_jsonl import run as rust_run
from ve.admission import AdmissionError, validate_label
from ve.errors import InvalidModel, ResourceLimit, VEError


def test_authority_override_and_rejection(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "evaluate=python,background=shadow")
    assert authority_for("evaluate") == "python"
    assert authority_for("background") == "shadow"
    assert authority_for("check") == "lean"
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "broken")
    with pytest.raises(ValueError):
        authority_for("evaluate")


def test_selected_authority_never_falls_back(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    with pytest.raises(CheckerUnavailable):
        execute("missing", {}, lambda: pytest.fail("Python executed"))


def test_shadow_returns_python_and_logs_drift(monkeypatch, tmp_path):
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    result = execute("evaluate", {"ast": ["top"]},
                     lambda: {"status": "Satisfied", "evaluations": 1},
                     lean=lambda: {"status": "Violated", "evaluations": 2})
    assert result == {"status": "Satisfied", "evaluations": 1}
    row = json.loads(log.read_text())
    assert row["class"] == ["budget-outcome", "count-value", "verdict"]
    assert row["op"] == "evaluate" and len(row["input_digest"]) == 64


def test_shadow_records_unavailable_checker(monkeypatch, tmp_path):
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    assert execute("check", {}, lambda: {"status": "ok"},
                   lean=lambda: (_ for _ in ()).throw(CheckerUnavailable("gone"))) == {"status": "ok"}
    assert json.loads(log.read_text())["lean"]["code"] == "CheckerUnavailable"


def test_checker_diagnostics_keep_code_and_generator():
    error = checker_error("InvalidModel(flags): mismatched relation")
    assert isinstance(error, InvalidModel) and error.generator == "flags"
    assert isinstance(checker_error("ResourceLimit: exhausted"), ResourceLimit)
    assert type(checker_error("unexpected decoder text")) is VEError


def test_shadow_classifies_nested_trace_and_composition(monkeypatch, tmp_path):
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    python = {"explanation": {"children": [{"kind": "top", "value": True}]},
              "composition": {"supporting_edge_ids": ["edge-a"]}}
    lean = {"explanation": {"children": [{"kind": "bottom", "value": True}]},
            "composition": {"supporting_edge_ids": ["edge-b"]}}
    assert execute("graph", {}, lambda: python, lean=lambda: lean) is python
    assert json.loads(log.read_text())["class"] == ["composition", "explanation"]


@pytest.mark.parametrize("response", [
    b'{"id":"x","status":"Satisfied","value":true,"evaluations":1,"evaluations":1}\n',
    b'{"id":"x","status":"Satisfied","value":true,"evaluations":2}\n',
    b'{"id":"x","status":"Satisfied","value":true,"evaluations":1,"explanation":null}\n',
])
def test_rust_rejects_malformed_evaluation_response(monkeypatch, tmp_path, response):
    executable = tmp_path / "ve"
    executable.write_bytes(b"mock")
    monkeypatch.setattr("ve.backends.rust_jsonl._run_checker", lambda *a, **kw:
                        subprocess.CompletedProcess(a, 0, response, b""))
    from hashlib import sha256
    case = {"id": "x", "kind": "evaluate-budgeted", "max_evaluations": 1}
    with pytest.raises(CheckerUnavailable):
        rust_run(case, executable=executable, expected_sha256=sha256(b"mock").hexdigest())


def recorded_rust(monkeypatch, tmp_path):
    """A call to a mock Rust checker, and the wall-clock wait each call is given."""
    executable = tmp_path / "ve"
    executable.write_bytes(b"mock")
    waits = []

    def checker(argv, *, input, timeout):
        waits.append(timeout)
        return subprocess.CompletedProcess(argv, 0, b'{"id":"x","status":"ok"}\n', b"")
    monkeypatch.setattr("ve.backends.rust_jsonl._run_checker", checker)
    from hashlib import sha256
    return waits, lambda **options: rust_run({"id": "x", "kind": "check"}, executable=executable,
                                             expected_sha256=sha256(b"mock").hexdigest(), **options)


def test_rust_wait_is_the_default_unless_configured(monkeypatch, tmp_path):
    """Load reproducer: under the Lean authority, a W6a generated case's Rust call
    timed out at the client's 5-second default in a 2 h 14 min suite. Users keep
    the 5 s (60 s for the readings replay); `VE_RUST_TIMEOUT` replaces both
    defaults; an explicit timeout is kept."""
    from ve.backends.rust_jsonl import configured_timeout
    waits, call = recorded_rust(monkeypatch, tmp_path)
    monkeypatch.delenv("VE_RUST_TIMEOUT")
    call()
    assert waits == [5.0] and configured_timeout(60.0) == 60.0
    monkeypatch.setenv("VE_RUST_TIMEOUT", "2.5")
    call()
    call(timeout=0.25)
    assert waits == [5.0, 2.5, 0.25] and configured_timeout(60.0) == 2.5


@pytest.mark.parametrize("value", ["", "0", "-1", "nan", "inf", "five"])
def test_rust_wait_setting_that_is_not_positive_seconds_is_refused(monkeypatch, tmp_path, value):
    waits, call = recorded_rust(monkeypatch, tmp_path)
    monkeypatch.setenv("VE_RUST_TIMEOUT", value)
    with pytest.raises(CheckerUnavailable, match="VE_RUST_TIMEOUT") as caught:
        call()
    assert not isinstance(caught.value, VEError) and waits == []


def test_rust_checker_slower_than_the_setting_is_stopped_at_it(monkeypatch, tmp_path):
    """The setting is the real wait of the checker process, which is killed."""
    script = tmp_path / "ve"
    script.write_text("#!/bin/sh\nexec sleep 600\n")
    script.chmod(0o755)
    from hashlib import sha256
    monkeypatch.setenv("VE_RUST_JSONL", str(script))
    monkeypatch.setenv("VE_RUST_SHA256", sha256(script.read_bytes()).hexdigest())
    monkeypatch.setenv("VE_RUST_TIMEOUT", "0.2")
    with pytest.raises(CheckerUnavailable, match="timed out after 0.2 seconds"):
        rust_run({"id": "x", "kind": "check"})


def test_the_suite_waits_its_hang_guard_for_every_checker():
    """Every test (and every process it starts) waits HANG_TIMEOUT for a Rust call,
    a Lean service request or a Lean service start, never the users' defaults."""
    import os
    from subprocesses import HANG_TIMEOUT
    from ve.backends.lean_service import configured_seconds
    from ve.backends.rust_jsonl import configured_timeout
    for variable in ("VE_RUST_TIMEOUT", "VE_LEAN_SERVICE_TIMEOUT", "VE_LEAN_SERVICE_STARTUP_TIMEOUT"):
        assert os.environ[variable] == str(HANG_TIMEOUT)
        assert configured_seconds(variable, 5.0) == HANG_TIMEOUT
    assert configured_timeout() == configured_timeout(60.0) == HANG_TIMEOUT


def test_lean_label_adapter_keeps_value_and_diagnostic(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = validate_label("asserted")
    with pytest.raises(AdmissionError) as original:
        validate_label("bad label")
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert validate_label("asserted") == expected
    with pytest.raises(AdmissionError) as candidate:
        validate_label("bad label")
    assert candidate.value.code == original.value.code


def test_pinned_constituents_ignore_per_operation_overrides(monkeypatch):
    from ve.backends import dispatch
    monkeypatch.setenv("VE_AUTHORITY", "python")
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "certificate_replay=python")
    with dispatch.pinned("lean"):
        assert authority_for("certificate_replay") == "lean"
        with dispatch.pinned("rust-experimental"):
            assert authority_for("evaluate") == "rust-experimental"
        assert authority_for("evaluate") == "lean"
    assert authority_for("certificate_replay") == "python"
    with pytest.raises(ValueError):
        with dispatch.pinned("shadow"):
            pass


@pytest.mark.parametrize("op", ["premise_status", "compare"])
def test_composing_adapters_check_their_constituents_on_lean(monkeypatch, op):
    """An override selecting only the composing operation still puts every
    certificate replay and model check under it on Lean."""
    from ve.ast import Bottom, Const, Not, Top, Unary
    from ve.backends import dispatch
    from ve.equivalence import Budgets, compare
    from ve.vacuity import premise_status
    from tests.probe_matrix import raw_environment
    from ve.environment import Environment
    env = Environment(raw_environment(()))
    atom = Unary("base", Const("x"))
    calls = {
        "premise_status": lambda: [premise_status(env, (atom, Not(atom)), max_proof_steps=64),
                                   premise_status(env, (atom,), max_proof_steps=64)],
        "compare": lambda: [compare(env, Top(), Bottom(), Budgets(64, 1, 4, 64)),
                            compare(env, atom, atom, Budgets(64, 1, 4, 64))],
    }
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = calls[op]()
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda name, authority: seen.append((name, authority))])
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", f"{op}=lean,certificate_replay=python,countermodel_check=python")
    assert calls[op]() == expected
    assert (op, "lean") in seen
    assert {"certificate_replay", "countermodel_check"} <= {name for name, authority in seen
                                                            if authority == "lean"}
    assert not [name for name, authority in seen if authority == "python"]
