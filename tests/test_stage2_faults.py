"""Per-adapter fault injection (Gate 2): every public operation dispatched to a
backend fails closed when that backend is missing, is an unlisted build, crashes
or hangs. The call raises CheckerUnavailable, which is operational: never a
verdict, never a `VEError`, and never Python's answer in the backend's place.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import ve.ast
from ve import ArgumentGraph, Claim, check_argument
from ve.admission import admit_document, validate_label
from ve.ast import Bottom, Const, Not, Top, Unary
from ve.background import background, dependency_order
from ve.backends import lean_runner, rust_jsonl, validation
from ve.backends.lean_service import LeanServicePool
from ve.bundle import check_bundle
from ve.definitions import compile_definitions
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.environment import Environment
from ve.equivalence import Budgets, compare
from ve.errors import CheckerUnavailable, VEError
from ve.evaluate import evaluate
from ve.identity import meaning_id
from ve.model import FiniteModel
from ve.norm_admission import admit_norm_document
from ve.norms import (NormDocument, check_conflict, check_norm_entailment_certificate,
                      prove_norm_entailment)
from ve.parser import parse
from ve.readings import check_readings
from ve.search import check_countermodel, find_countermodel, find_distinguishing_model
from ve.vacuity import premise_status
from tests import probe_matrix as pm
from tests.test_lean_service import ALL, expire_service_waits, fake

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")


def fresh(document):
    """A copy of a norm document built under the Python authority, without any
    Lean answer kept on it."""
    from copy import copy
    clone = copy(document)
    clone.__dict__.pop("_regenerated", None)
    return clone


def inputs():
    """Every input is built under the Python authority, before a fault is injected."""
    env = Environment(pm.raw_environment(()))
    norms = Environment(pm.raw_environment(("norms@0",)))
    definitions = Environment(pm.raw_environment(("definitions@0",)))
    model = FiniteModel.from_dict(env, pm.model_wire(env))
    atom = Unary("base", Const("x"))
    certificate = prove_entailment(env, (), Top()).certificate
    doc = NormDocument(norms, [])
    norm_certificate = prove_norm_entailment(doc, (), Top(), max_steps=100).certificate
    admission = {"units": [{"id": "u", "span": [0, 5], "kind": "asserted", "content": ["top"]}],
                 "graph": {"root": "r", "nodes": [{"name": "r", "ast": ["top"], "unit": "u"}]}}
    lemma = {"name": "l", "environment_id": env.environment_id,
             "premises": [{"label": "open:assumption", "ast": ["top"]}], "cites": [],
             "conclusion": ["top"], "meaning_id": meaning_id(env, Top()), "reading_choices": {},
             "transitive_leaves": [{"label": "open:assumption", "ast": ["top"]}],
             "certificate": prove_entailment(env, (Top(),), Top()).certificate}
    graph = ArgumentGraph(env, (Claim.create(env, "root", "true.\n"),), (), "root")
    return {
        "typing": lambda: ve.ast.check_formula(env, atom),
        "background": lambda: background(norms),
        "dependency_order": lambda: dependency_order({"a": set(), "b": {"a"}}),
        "label": lambda: validate_label("asserted"),
        "admission": lambda: admit_document(env, admission),
        "certificate_replay": lambda: check_entailment_certificate(env, (), Top(), certificate),
        "evaluate": lambda: evaluate(env, atom, model, trace=False),
        "countermodel_check": lambda: check_countermodel(env, (atom,), Bottom(), model),
        "countermodel_search": lambda: find_countermodel(env, (atom,), Bottom(), max_domain_size=1),
        "distinguishing_model": lambda: find_distinguishing_model(env, atom, Not(atom), max_domain_size=1),
        # A fresh document per call: Lean's regeneration is kept per document.
        "norms_elaborate": lambda: fresh(doc).elaborate("permitted"),
        "norms_certificate": lambda: check_norm_entailment_certificate(fresh(doc), (), Top(), norm_certificate),
        "norms_conflict": lambda: check_conflict(fresh(doc), prove=True, tableau_steps=64),
        "norms_admission": lambda: admit_norm_document(norms, admission),
        "premise_status": lambda: premise_status(env, (atom,), max_proof_steps=16),
        "compare": lambda: compare(env, atom, atom, Budgets(64, 1, 4, 64)),
        "environment_validation": lambda: Environment(pm.raw_environment(())),
        "model_validation": lambda: FiniteModel.from_dict(env, pm.model_wire(env)),
        "definitions_elaboration": lambda: compile_definitions(definitions, definitions.definition_entries,
                                                               version="v"),
        "bundle": lambda: check_bundle({"version": "ve-bundle@0", "environment": env.to_dict(),
                                        "lemmas": [lemma]}),
        "parse": lambda: parse(env, "x is base.\n"),
        "graph": lambda: check_argument(graph, search=False).require_available(),
        "readings": lambda: check_readings(env, [{"id": "s", "version": 1, "readings": [
            {"kind": "asserted", "content": ["unary", "base", ["const", "x"]]},
            {"kind": "asserted", "content": ["top"]}]}], ["top"], max_steps=64),
    }


# Operations whose verdict path runs Rust under the Lean authority.
RUST = ("evaluate", "countermodel_check", "countermodel_search", "distinguishing_model")
# Operations Lean alone answers under the Lean authority (search publishes
# its witness through the Lean countermodel check).
LEAN = (
    "typing", "background", "dependency_order", "label", "admission", "certificate_replay",
    "evaluate", "countermodel_check", "countermodel_search", "distinguishing_model",
    "norms_elaborate", "norms_certificate", "norms_conflict", "norms_admission", "premise_status",
    "compare", "environment_validation", "model_validation", "definitions_elaboration", "bundle",
    "parse", "graph", "readings")


@pytest.fixture(scope="module")
def calls():
    return inputs()


@pytest.fixture(autouse=True)
def lean_authority(monkeypatch):
    # No cached Lean answer may stand in for the faulty backend.
    monkeypatch.setattr(ve.ast, "_LEAN_TYPED", {})
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    monkeypatch.setenv("VE_AUTHORITY", "lean")


def use_pool(monkeypatch, executable, **options):
    pool = LeanServicePool(size=1, executable=executable, **options)
    monkeypatch.setattr(lean_runner, "_pool", pool)
    return pool


def lean_fault(monkeypatch, tmp_path, fault):
    if fault == "missing":
        return use_pool(monkeypatch, tmp_path / "absent")
    if fault == "unlisted":
        # A working service whose build the lock does not list.
        return use_pool(monkeypatch, fake(tmp_path, "scripted"))
    if fault == "crash":
        return use_pool(monkeypatch, fake(tmp_path, "crash"), allow_unlisted_build=True)
    # A service that never answers: every request's deadline is injected as expired.
    expire_service_waits(monkeypatch).requests = ALL
    return use_pool(monkeypatch, fake(tmp_path, "hang"), allow_unlisted_build=True)


def test_every_dispatched_operation_has_a_fault_case(calls):
    from tools.stage2_parity import ADAPTERS
    assert set(ADAPTERS.values()) == set(calls) == set(LEAN)


@pytest.mark.parametrize("fault", ["missing", "unlisted", "crash", "hang"])
@pytest.mark.parametrize("op", LEAN)
def test_lean_faults_fail_closed_in_every_adapter(monkeypatch, tmp_path, calls, op, fault):
    pool = lean_fault(monkeypatch, tmp_path, fault)
    try:
        with pytest.raises(CheckerUnavailable) as caught:
            calls[op]()
        assert not isinstance(caught.value, VEError)
        assert caught.value.code == "CheckerUnavailable"
    finally:
        pool.close()


def rust_fault(monkeypatch, tmp_path, fault):
    if fault == "missing":
        monkeypatch.setenv("VE_RUST_JSONL", str(tmp_path / "absent"))
        return
    script = tmp_path / "ve"
    script.write_text("#!/bin/sh\nexit 3\n")
    script.chmod(0o755)
    monkeypatch.setenv("VE_RUST_JSONL", str(script))
    if fault == "unlisted":
        return
    import hashlib
    monkeypatch.setenv("VE_RUST_SHA256", hashlib.sha256(script.read_bytes()).hexdigest())
    if fault == "hang":
        def timeout(argv, *, input, timeout):
            raise subprocess.TimeoutExpired(argv, timeout)
        monkeypatch.setattr(rust_jsonl, "_run_checker", timeout)


@pytest.mark.parametrize("fault", ["missing", "unlisted", "crash", "hang"])
@pytest.mark.parametrize("op", RUST)
def test_rust_faults_fail_closed_in_every_adapter(monkeypatch, tmp_path, calls, op, fault):
    rust_fault(monkeypatch, tmp_path, fault)
    with pytest.raises(CheckerUnavailable) as caught:
        calls[op]()
    assert not isinstance(caught.value, VEError)


@pytest.mark.parametrize("op", LEAN)
def test_the_python_path_never_answers_for_a_failed_backend(monkeypatch, tmp_path, calls, op):
    """The retained Python implementations are not consulted after a failure:
    the observed dispatch runs the operation on the backend only."""
    from ve.backends import dispatch
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda name, authority: seen.append((name, authority))])
    pool = lean_fault(monkeypatch, tmp_path, "crash")
    try:
        with pytest.raises(CheckerUnavailable):
            calls[op]()
    finally:
        pool.close()
    assert seen and all(authority == "lean" for _, authority in seen)
