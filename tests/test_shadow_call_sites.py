"""Stage 3 shadow call sites: the scans L11 to L13 and the payloads of L2.

docs/spec/mig3.md 2.2, 2.6 (requirement (I)), 2.7 and 2.12.
"""
from __future__ import annotations

from dataclasses import replace
import json
import os

import pytest

from tools import shadow_surface as surface
from ve.backends import dispatch

SOURCES, MANIFEST = surface.worktree_sources()


def test_l11_the_dispatch_names_and_their_modules():
    calls = surface.execute_calls(SOURCES)
    names = {name for found in calls.values() for name in found}
    assert None not in names, "a call of execute without a literal dispatch name"
    assert names == set(dispatch.DISPATCH_NAMES) and len(dispatch.DISPATCH_NAMES) == 23
    assert len(calls) == 17, sorted(calls)


def test_l12_every_static_branch_counts_its_uncompared_calls():
    branches = surface.static_branches(SOURCES)
    assert len(branches) == 14, [(b["path"], b["line"]) for b in branches]
    for branch in branches:
        where = f"{branch['path']}:{branch['line']}"
        note = branch["note"]
        assert note is not None, f"{where}: the static Python path does not call note_uncompared first"
        assert note["op"] == branch["op"], where
        assert note["reasons"] and set(note["reasons"]) <= set(dispatch.UNCOMPARED_REASONS), where


def test_every_uncompared_reason_is_used_and_registered():
    used = surface.uncompared_reasons_used(SOURCES)
    assert set(used) == set(dispatch.UNCOMPARED_REASONS), set(used) ^ set(dispatch.UNCOMPARED_REASONS)
    assert all(sentence.strip() for sentence in dispatch.UNCOMPARED_REASONS.values())


def test_l13_the_lean_only_handoffs_and_their_modules():
    assert surface.handoff_functions(SOURCES) == [
        "run_soft_case", "run_alternatives_case", "run_discourse_case", "run_reports_case",
        "run_norm_defaults_cases", "run_readings_cases"]
    assert surface.unmarked_process_starters(SOURCES) == []
    modules = surface.handoff_modules(SOURCES)
    assert sorted(modules) == ["ve/alternatives.py", "ve/discourse.py", "ve/norm_defaults_route.py",
                               "ve/readings_route.py", "ve/reports_route.py", "ve/rights_route.py",
                               "ve/risk.py", "ve/soft_route.py"]
    outside = set(surface.execute_calls(SOURCES)) | set(modules)
    assert len(outside) == 25


def test_the_candidate_surface_and_the_classed_paths():
    found = surface.candidate_surface(SOURCES, MANIFEST)
    for path in ("ve/backends/dispatch.py", "ve/parser.py", "ve/soft_route.py", "lean/VE/Service/Graph.lean",
                 "lean/Serve.lean", "lean/checkers.lock", "lean/VE/Bridge.lean", "lean/VE/Json.lean"):
        assert surface.on_surface(path, found), path
    for path in ("ve/english.py", "ve/wire.py", "ve/printer.py"):
        assert not surface.on_surface(path, found) and surface.classed(path, found), path
    for path in ("tests/test_x.py", "docs/spec/mig3.md", "conformance/shadow/ledger/2026-10-04.json"):
        assert not surface.classed(path, found), path


def test_the_scan_of_a_commit_reads_the_same_sources():
    sources, manifest = surface.tree_sources("HEAD")
    assert set(surface.execute_calls(sources)) == set(surface.execute_calls(SOURCES))
    assert manifest["lean_decoders"]["files"] == MANIFEST["lean_decoders"]["files"]


# --- L2: the payload determines the input ------------------------------------------------

@pytest.fixture
def digests(monkeypatch, tmp_path):
    """Run calls at `shadow` with every candidate replaced, and collect each
    shadow call's `(op, input_digest)` in order."""
    seen: list[tuple[str, str | None]] = []
    original = dispatch._shadow

    def shadow(op, payload, python, lean):
        seen.append((op, dispatch._input(payload)[0]))
        return original(op, payload, python, lambda: {"replaced": op})

    monkeypatch.setattr(dispatch, "_shadow", shadow)
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    monkeypatch.delenv("VE_AUTHORITY_OVERRIDES", raising=False)
    monkeypatch.setenv("VE_SHADOW_LOG", str(tmp_path / "shadow.jsonl"))

    def run(op, call):
        start = len(seen)
        try:
            call()
        except Exception:   # noqa: BLE001 - only the digests of the calls matter here
            pass
        mine = [digest for name, digest in seen[start:] if name == op]
        assert mine, f"no shadow call of {op}"
        assert None not in mine, f"a payload of {op} cannot be written"
        return mine[-1]
    return run


def _env(*profiles, extra=None):
    from ve.environment import Environment
    from tests.probe_matrix import raw_environment
    data = raw_environment(profiles)
    if extra:
        data["vocabulary"]["predicates"][extra] = {"arguments": ["item"], "description": extra}
    return Environment(data)


def _model(env):
    from ve.model import FiniteModel
    from tests.probe_matrix import model_wire
    return FiniteModel.from_dict(env, model_wire(env))


def _vary(run, op, calls):
    """Each call differs from the first in one argument; every digest differs."""
    found = [run(op, call) for call in calls]
    assert len(set(found)) == len(found), f"{op}: {found}"


def test_l2_parse_typing_environment_model(digests):
    from ve.ast import Bottom, Const, Top, Unary, check_formula
    from ve.environment import Environment
    from ve.model import FiniteModel
    from ve.parser import parse
    from tests.probe_matrix import model_wire, raw_environment
    env, other = _env(), _env(extra="other")
    _vary(digests, "parse", [lambda: parse(env, "true.\n"), lambda: parse(other, "true.\n"),
                             lambda: parse(env, "false.\n")])
    _vary(digests, "typing", [lambda: check_formula(env, Top()), lambda: check_formula(other, Top()),
                              lambda: check_formula(env, Unary("base", Const("x")))])
    _vary(digests, "environment_validation", [lambda: Environment(raw_environment(())),
                                              lambda: Environment(raw_environment(("data@0",)))])
    wire = model_wire(env)
    changed = {**wire, "relations": {**wire["relations"], "base": []}}
    model = FiniteModel.from_dict(env, wire)
    _vary(digests, "model_validation", [
        lambda: FiniteModel.from_dict(env, wire), lambda: FiniteModel.from_dict(other, model_wire(other)),
        lambda: FiniteModel.from_dict(env, changed),
        lambda: FiniteModel.from_dict(env, wire, _claimed={"environment_id": env.environment_id,
                                                         "model_id": model.model_id})])
    del Bottom


def test_l2_evaluation_and_search(digests):
    from ve.ast import Bottom, Not, Top
    from ve.evaluate import evaluate
    from ve.search import check_countermodel, find_countermodel, find_distinguishing_model
    env, other = _env(), _env(extra="other")
    model, model_other = _model(env), _model(other)
    _vary(digests, "evaluate", [
        lambda: evaluate(env, Top(), model, trace=False),
        lambda: evaluate(other, Top(), model_other, trace=False),
        lambda: evaluate(env, Bottom(), model, trace=False),
        lambda: evaluate(env, Top(), model, trace=True),
        lambda: evaluate(env, Top(), model, trace=False, max_evaluations=7),
        lambda: evaluate(env, Top(), model, trace=True, max_trace_nodes=3)])
    _vary(digests, "countermodel_check", [
        lambda: check_countermodel(env, (Top(),), Bottom(), model),
        lambda: check_countermodel(other, (Top(),), Bottom(), model_other),
        lambda: check_countermodel(env, (), Bottom(), model),
        lambda: check_countermodel(env, (Top(),), Not(Top()), model),
        lambda: check_countermodel(env, (Top(),), Bottom(), model, max_evaluations=9)])
    _vary(digests, "countermodel_search", [
        lambda: find_countermodel(env, (Top(),), Bottom(), max_domain_size=1),
        lambda: find_countermodel(other, (Top(),), Bottom(), max_domain_size=1),
        lambda: find_countermodel(env, (), Bottom(), max_domain_size=1),
        lambda: find_countermodel(env, (Top(),), Not(Top()), max_domain_size=1),
        lambda: find_countermodel(env, (Top(),), Bottom(), max_domain_size=2),
        lambda: find_countermodel(env, (Top(),), Bottom(), max_domain_size=1, max_models=3)])
    _vary(digests, "distinguishing_model", [
        lambda: find_distinguishing_model(env, Top(), Bottom(), max_domain_size=1),
        lambda: find_distinguishing_model(other, Top(), Bottom(), max_domain_size=1),
        lambda: find_distinguishing_model(env, Bottom(), Bottom(), max_domain_size=1),
        lambda: find_distinguishing_model(env, Top(), Top(), max_domain_size=1),
        lambda: find_distinguishing_model(env, Top(), Bottom(), max_domain_size=1, max_models=3)])


def test_l2_certificates_background_definitions(digests):
    from ve.ast import Bottom, Not, Top
    from ve.background import background, dependency_order, validate_background
    from ve.definitions import compile_definitions
    from ve.entailment import check_entailment_certificate, prove_entailment
    env, other = _env(), _env(extra="other")
    cert = prove_entailment(env, (), Top(), max_steps=100).certificate
    cert_two = prove_entailment(env, (Bottom(),), Top(), max_steps=100).certificate
    _vary(digests, "certificate_replay", [
        lambda: check_entailment_certificate(env, (), Top(), cert),
        lambda: check_entailment_certificate(other, (), Top(), cert),
        lambda: check_entailment_certificate(env, (Bottom(),), Top(), cert),
        lambda: check_entailment_certificate(env, (), Not(Bottom()), cert),
        lambda: check_entailment_certificate(env, (), Top(), cert_two),
        lambda: check_entailment_certificate(env, (), Top(), cert, max_steps=50)])
    _vary(digests, "background", [lambda: background(env), lambda: background(other)])
    _vary(digests, "dependency_order", [lambda: dependency_order({"a": set()}),
                                        lambda: dependency_order({"a": set(), "b": {"a"}})])
    model = _model(env)
    _vary(digests, "model_validation", [lambda: validate_background(env, model),
                                        lambda: validate_background(other, _model(other)),
                                        lambda: validate_background(env, replace(model, model_id="1" * 64))])
    defs, defs_other = _env("definitions@0"), _env("definitions@0", extra="other")
    entries = defs.definition_entries
    _vary(digests, "definitions_elaboration", [
        lambda: compile_definitions(defs, entries, version=defs.environment_id),
        lambda: compile_definitions(defs_other, entries, version=defs.environment_id),
        lambda: compile_definitions(defs, {"absent": {"arguments": ["item"], "body": ["top"]}},
                                    version=defs.environment_id),
        lambda: compile_definitions(defs, entries, version="other")])


def test_l2_norms(digests):
    from ve.ast import Bottom, Top
    from ve.norms import (NormDocument, check_conflict, check_norm_entailment_certificate,
                          prove_norm_entailment)
    from ve.norm_admission import admit_norm_document
    env, other = _env("norms@0"), _env("norms@0", extra="other")
    doc, doc_other = NormDocument(env, []), NormDocument(other, [])
    proof = prove_norm_entailment(doc, (), Top(), max_steps=100).certificate
    proof_two = prove_norm_entailment(doc, (Bottom(),), Top(), max_steps=100).certificate
    _vary(digests, "norms_elaborate", [lambda: doc.elaborate("permitted"), lambda: doc_other.elaborate("permitted"),
                                       lambda: doc.elaborate("absent")])
    _vary(digests, "norms_certificate", [
        lambda: check_norm_entailment_certificate(doc, (), Top(), proof),
        lambda: check_norm_entailment_certificate(doc_other, (), Top(), proof),
        lambda: check_norm_entailment_certificate(doc, (Bottom(),), Top(), proof),
        lambda: check_norm_entailment_certificate(doc, (), Bottom(), proof),
        lambda: check_norm_entailment_certificate(doc, (), Top(), proof_two)])
    model = _model(env)
    _vary(digests, "norms_conflict", [
        lambda: check_conflict(doc), lambda: check_conflict(doc_other),
        lambda: check_conflict(doc, model=model), lambda: check_conflict(doc, certificates=[]),
        lambda: check_conflict(doc, max_evaluations=5), lambda: check_conflict(doc, prove=True),
        lambda: check_conflict(doc, prove=True, tableau_steps=3)])
    data = {"units": [{"id": "u", "span": [0, 5], "kind": "asserted", "content": ["top"]}],
            "graph": {"root": "r", "nodes": [{"name": "r", "ast": ["top"], "unit": "u"}]}}
    _vary(digests, "norms_admission", [lambda: admit_norm_document(env, data),
                                       lambda: admit_norm_document(other, data),
                                       lambda: admit_norm_document(env, {**data, "graph": {}})])


def test_l2_admission_label_readings_graph_bundle_composites(digests):
    from ve import ArgumentGraph, Claim
    from ve.admission import admit_document, validate_label
    from ve.argument import check_argument
    from ve.ast import Bottom, Top
    from ve.bundle import check_bundle
    from ve.equivalence import Budgets, compare
    from ve.readings import check_readings
    from ve.vacuity import premise_status
    env, other = _env(), _env(extra="other")
    data = {"units": [{"id": "u", "span": [0, 5], "kind": "asserted", "content": ["top"]}],
            "graph": {"root": "r", "nodes": [{"name": "r", "ast": ["top"], "unit": "u"}]}}
    _vary(digests, "admission", [lambda: admit_document(env, data), lambda: admit_document(other, data),
                                 lambda: admit_document(env, {**data, "graph": {}})])
    _vary(digests, "label", [lambda: validate_label("asserted"), lambda: validate_label("hypothesis")])
    sets = [{"id": "s", "version": 1, "readings": [
        {"kind": "asserted", "content": ["unary", "base", ["const", "x"]]},
        {"kind": "asserted", "content": ["not", ["unary", "base", ["const", "x"]]]}]}]
    _vary(digests, "readings", [
        lambda: check_readings(env, sets, ["bottom"]), lambda: check_readings(other, sets, ["bottom"]),
        lambda: check_readings(env, sets[:0], ["bottom"]), lambda: check_readings(env, sets, ["top"]),
        lambda: check_readings(env, sets, ["bottom"], max_steps=5),
        lambda: check_readings(env, sets, ["bottom"], fixed=[["top"]])])
    claim = Claim.create(env, "r", "true.\n")
    graph = ArgumentGraph(env, (claim,), (), "r")
    claim_other = Claim.create(other, "r", "true.\n")
    _vary(digests, "graph", [lambda: check_argument(graph, search=False),
                             lambda: check_argument(ArgumentGraph(other, (claim_other,), (), "r"), search=False),
                             lambda: check_argument(graph, search=True),
                             lambda: check_argument(graph, search=False, max_proof_steps=5)])
    bundle = {"version": "ve-bundle@0", "environment": env.to_dict(), "lemmas": []}
    _vary(digests, "bundle", [lambda: check_bundle(bundle),
                              lambda: check_bundle({**bundle, "environment": other.to_dict()})])
    _vary(digests, "premise_status", [lambda: premise_status(env, ()), lambda: premise_status(other, ()),
                                      lambda: premise_status(env, (Bottom(),)),
                                      lambda: premise_status(env, (), max_models=3)])
    _vary(digests, "compare", [lambda: compare(env, Top(), Bottom()), lambda: compare(other, Top(), Bottom()),
                               lambda: compare(env, Bottom(), Bottom()), lambda: compare(env, Top(), Top()),
                               lambda: compare(env, Top(), Bottom(), Budgets(5, 1, 2, 5))])


# --- S18: Lean-only calls -----------------------------------------------------------------

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
    for path in sorted(directory.glob("records-*.jsonl")):
        rows.extend(json.loads(line) for line in path.read_text().splitlines())
    return rows


def counts(directory, op) -> dict:
    return dispatch._workers[(os.getpid(), str(directory))].op(op)


def test_s18_lean_only_calls_are_recorded_one_per_case(run_dir, monkeypatch):
    from ve.backends.lean import run_readings_cases, run_soft_case
    from ve.readings_route import LEAN_ROUTE as READINGS
    from ve.readings_s1 import wire
    from ve.rights_route import LEAN_ROUTE as RIGHTS
    from tests.test_readings_s1_lean import env_rights
    if not (RIGHTS.exists() and READINGS.exists()):
        pytest.skip("the Lean route executables have not been built")
    environment = env_rights()
    environment["profiles"] = [p for p in environment["profiles"] if p != "readings@1"]
    case = {"id": "scope", "kind": "rights-scope", "environment": wire(environment),
            "document": [{"source_units": []}], "certificates": {}}
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = run_soft_case(RIGHTS, case)
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    assert run_soft_case(RIGHTS, case) == expected
    [row] = records(run_dir)
    assert row["kind"] == "lean-only" and row["python"] is None and row["class"] == []
    assert row["op"] == "ve_rights_route" and row["lean"] == expected and row["input"] == case
    assert counts(run_dir, "ve_rights_route")["lean_only"] == 1
    monkeypatch.delenv("VE_AUTHORITY")
    run_soft_case(RIGHTS, case)
    assert len(records(run_dir)) == 1
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    cases = [{"id": f"case-{index}", "kind": "unknown-kind"} for index in range(3)]
    rows = run_readings_cases(READINGS, cases)
    batch = [row for row in records(run_dir) if row["op"] == "ve_readings_route"]
    assert len(batch) == 3 and len({row["input_digest"] for row in batch}) == 3
    assert [row["lean"] for row in batch] == rows
    assert counts(run_dir, "ve_readings_route")["lean_only"] == 3


# --- L10: uncompared calls --------------------------------------------------------------

def _reports_raw():
    from tests.test_reports import environment
    return environment().to_dict()


class _WithSoftPremises:
    """An in-scope environment that carries soft premises (as a validated soft
    document's extended environment does)."""

    def __init__(self, env):
        from ve.ast import Top
        self._env, self.soft_premises = env, (("rule", Top()),)

    def __getattr__(self, name):
        return getattr(self._env, name)


def _non_first_order_norms():
    from ve.ast import Named, Reach, Var
    from ve.norms import NormDocument
    from tests.test_stage2_norms import flagged, rule
    env = flagged(family=("closure@0",), relation=True)
    return NormDocument(env, [rule("may", "permitted", True, Reach("star", Named("before"), Var(0), Var(0)))])


def _uncompared_inputs():
    """One input for each reason of `dispatch.UNCOMPARED_REASONS`, as `(op, call)`."""
    from ve import ArgumentGraph
    from ve.admission import admit_document
    from ve.argument import check_argument
    from ve.ast import Top, check_formula
    from ve.background import validate_background
    from ve.bundle import check_bundle
    from ve.definitions import compile_definitions
    from ve.entailment import check_entailment_certificate, prove_entailment
    from ve.environment import Environment
    from ve.model import FiniteModel
    from ve.parser import parse
    from ve.readings import check_readings
    from tests.probe_matrix import model_wire
    from tests.test_units_w6a import environment as quantity_raw
    plain = _env()
    reports_raw = _reports_raw()
    reports = Environment(reports_raw)
    reports_model = {"complete": True, "domains": {"person": ["p"], "text": ["t"], "evidence": ["e"]},
                     "constants": {"article": "t", "alice": "p", "e1": "e"}, "relations": {"safe": []}}
    soft = _WithSoftPremises(plain)
    model = _model(plain)
    cert = prove_entailment(plain, (), Top(), max_steps=100).certificate
    return {
        "parse-scope": ("parse", lambda: parse(reports, "true.\n")),
        "typing-scope": ("typing", lambda: check_formula(Environment(quantity_raw()), Top())),
        "environment-generated-reports": ("environment_validation",
                                          lambda: Environment(plain.to_dict(), _generated_reports=True)),
        "environment-scope": ("environment_validation", lambda: Environment(reports_raw)),
        "model-deferred-id": ("model_validation",
                              lambda: FiniteModel.from_dict(plain, model_wire(plain), _defer_model_id=True)),
        "model-scope": ("model_validation", lambda: FiniteModel.from_dict(reports, reports_model)),
        "background-scope": ("model_validation", lambda: validate_background(reports, model)),
        "background-soft": ("model_validation", lambda: validate_background(soft, model)),
        "background-no-model-id": ("model_validation",
                                   lambda: validate_background(plain, replace(model, model_id=""))),
        "definitions-scope": ("definitions_elaboration",
                              lambda: compile_definitions(reports, {}, version=reports.environment_id)),
        "readings-scope": ("readings", lambda: check_readings(reports, [], ["bottom"])),
        "graph-scope": ("graph", lambda: check_argument(ArgumentGraph(reports, (), (), "r"), search=False)),
        "bundle-scope": ("bundle", lambda: check_bundle({"version": "ve-bundle@0", "environment": {},
                                                         "lemmas": []})),
        "certificate-self-replay": ("certificate_replay", lambda: check_entailment_certificate(
            plain, (), Top(), cert, _background=False)),
        "certificate-generated-premises": ("certificate_replay", lambda: check_entailment_certificate(
            plain, (), Top(), cert, _generated_premises=())),
        "norms-route": ("norms_elaborate", lambda: _non_first_order_norms().elaborate("permitted")),
        "admission-soft": ("admission", lambda: admit_document(
            {**plain.to_dict(), "profiles": ["relational-fol@0", "soft-norms@0"]}, {})),
    }


@pytest.mark.parametrize("reason", sorted(dispatch.UNCOMPARED_REASONS))
def test_l10_each_scope_gap_is_counted_under_its_reason(run_dir, reason):
    op, call = _uncompared_inputs()[reason]
    before, written = counts(run_dir, op)["uncompared"].get(reason, 0), len(records(run_dir))
    try:
        call()
    except Exception:   # noqa: BLE001 - Python's own answer does not matter here
        pass
    assert counts(run_dir, op)["uncompared"].get(reason, 0) - before == 1, counts(run_dir, op)["uncompared"]
    assert not [row for row in records(run_dir)[written:] if row["op"] == op]


def test_l10_a_coupled_reading_set_is_a_compared_call(run_dir):
    from ve.readings import check_readings
    sets = [{"id": "s", "version": 1, "readings": [
        {"kind": "asserted", "content": ["unary", "base", ["const", "x"]]},
        {"kind": "asserted", "content": ["not", ["unary", "base", ["const", "x"]]]}]}]
    try:
        check_readings(_env(), sets, ["bottom"], couplings=[{"id": "c", "sets": ["s"]}])
    except Exception:   # noqa: BLE001 - the comparison, not the answer, is tested
        pass
    tally = counts(run_dir, "readings")
    assert tally["compared"] == 1 and tally["uncompared"] == {}
