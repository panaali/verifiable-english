"""Checker boundaries: one owner per operation (no authority to select since lean-first batch 18), Rust
transport limits and diagnostic classes."""
from __future__ import annotations

import json
import subprocess

import pytest

from ve.backends.diagnostics import checker_error
from ve.backends.lean_service import CheckerUnavailable
from ve.backends.rust_jsonl import run as rust_run
from ve.admission import AdmissionError, validate_label
from ve.errors import InvalidModel, ResourceLimit, VEError


@pytest.mark.parametrize("setting", [{"VE_AUTHORITY": "python"}, {"VE_AUTHORITY": "shadow"},
                                     {"VE_AUTHORITY": "rust-experimental"},
                                     {"VE_AUTHORITY_OVERRIDES": "evaluate=python,countermodel_check=python"}])
def test_no_setting_selects_an_authority(monkeypatch, tmp_path, setting):
    """Lean-first batch 18: the `python` authority, its shadow and the overrides are gone. A leftover
    setting changes nothing: evaluation, the countermodel check and model validation run their one
    owner, Lean, which the observers see, and no shadow record is written."""
    from ve import Environment, FiniteModel
    from ve.ast import Bottom, Top
    from ve.backends import dispatch
    from ve.evaluate import evaluate
    from ve.search import check_countermodel
    from tests.probe_matrix import model_wire, raw_environment
    env = Environment(raw_environment(()))
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda name, owner: seen.append((name, owner))])
    monkeypatch.setenv("VE_SHADOW_LOG", str(tmp_path / "shadow.jsonl"))
    for name, value in setting.items():
        monkeypatch.setenv(name, value)
    python = []
    import importlib
    evaluate_module = importlib.import_module("ve.evaluate")
    monkeypatch.setattr(evaluate_module, "_evaluate_validated", lambda *a, **k: python.append(a) or pytest.fail(
        "the Python evaluator answered a public evaluation"))
    model = FiniteModel.from_dict(env, model_wire(env))
    assert evaluate(env, Top(), model).value is True
    assert check_countermodel(env, (), Bottom(), model).valid is True
    assert not python and not (tmp_path / "shadow.jsonl").exists()
    assert not hasattr(dispatch, "authority_for") and not hasattr(dispatch, "execute")
    assert all(dispatch.SINGLE_OWNER[op] == "lean" for op in ("evaluate", "countermodel_check", "model_validation"))


def test_checker_diagnostics_keep_code_and_generator():
    error = checker_error("InvalidModel(flags): mismatched relation")
    assert isinstance(error, InvalidModel) and error.generator == "flags"
    assert isinstance(checker_error("ResourceLimit: exhausted"), ResourceLimit)
    assert type(checker_error("unexpected decoder text")) is VEError


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
        # A record the producer's schema accepts for a `check` case (`ve/backends/rust_schema`).
        return subprocess.CompletedProcess(argv, 0, b'{"id":"x","status":"ok","well_typed":true}\n', b"")
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
    """The setting is the real wait of the checker process, which is killed. The
    checker never answers, and its deadline is injected as expired: the test waits
    for no deadline."""
    from ve.backends import rust_jsonl
    import time
    script = tmp_path / "ve"
    script.write_text("#!/bin/sh\nexec sleep 600\n")
    script.chmod(0o755)
    from hashlib import sha256
    monkeypatch.setenv("VE_RUST_JSONL", str(script))
    monkeypatch.setenv("VE_RUST_SHA256", sha256(script.read_bytes()).hexdigest())
    monkeypatch.setenv("VE_RUST_TIMEOUT", "1234.5")
    # The checker is a persistent process (lean-first b2, F6): its deadline is injected as
    # expired through the transport's clock, not through `communicate`.
    waits = []

    def expired(timeout):
        waits.append(timeout)
        return time.monotonic()
    monkeypatch.setattr(rust_jsonl, "_deadline", expired)
    with pytest.raises(CheckerUnavailable, match="timed out after 1234.5 seconds"):
        rust_run({"id": "x", "kind": "check"})
    assert waits == [1234.5]
    assert not any(c.argv[0] == str(script) for idle in rust_jsonl._idle.values() for c in idle)


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


def test_lean_label_adapter_keeps_value_and_diagnostic():
    assert validate_label("asserted") == "asserted"
    with pytest.raises(AdmissionError) as rejected:
        validate_label("bad label")
    assert rejected.value.code == "AdmissionError" and rejected.value.backend_rejection is True


@pytest.mark.parametrize("op", ["premise_status", "compare"])
def test_composing_adapters_check_their_constituents_on_lean(monkeypatch, op):
    """A composing operation's certificate replays and model checks are Lean's, as it is."""
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
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda name, owner: seen.append((name, owner))])
    calls[op]()
    assert (op, "lean") in seen
    assert {"certificate_replay", "countermodel_check"} <= {name for name, owner in seen if owner == "lean"}
    # Every call ran its registered owner: Lean, or Rust for a search Lean then checks.
    assert all(owner == dispatch.SINGLE_OWNER[name] for name, owner in seen)
