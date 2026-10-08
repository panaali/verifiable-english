"""Three-way P0 conformance: Python, Rust and the Lean `route` subcommand give
identical verdicts on every shipped case of the P0 families (PLAN-EXPAND2 3.10(2)).

Rust scope (plan 3.7, batch 15b): envelopes, Background, model validity, evaluation
and search. Rust has no certificate checker, so on a certificate or inconsistency case
its verdict is that bounded search finds no model; its evaluation verdict is the
document's value (the `evaluate-budgeted` kind). Admission, labels and dependency orders
are Python and Lean only. Rust checks supplied order countermodels but does not search
for them.
"""
from __future__ import annotations

import json
import os
from copy import deepcopy
import shutil
from subprocesses import HANG_TIMEOUT
import subprocess
from pathlib import Path

import pytest

from conformance.p0 import FAMILIES, lean_case
from conformance.three_way import lean_verdict, python_verdict, run, rust_envelope, rust_request, rust_verdict
from tools import rust_build

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_conformance"


def fixture(name):
    return json.loads((ROOT / f"conformance/{name}.json").read_text())


def active(name):
    return [case for case in fixture(name) if "pending" not in case]


def agrees(expected, verdict):
    return all(verdict.get(key) == value for key, value in expected.items())


@pytest.fixture(scope="module")
def lean_executable():
    if not LEAN.exists():
        pytest.skip("lean route runner is not built (lake build)")
    return LEAN


@pytest.fixture(scope="module")
def rust_executable():
    if os.environ.get("VE_RUST_PREBUILT"):
        binary = Path(os.environ["VE_RUST_BINARY"])
        assert binary.is_file(), f"gate Rust build missing: {binary}"
        return binary
    cargo = shutil.which("cargo")
    if not cargo:
        pytest.skip("cargo is not available")
    env = rust_build.cargo_env()
    built = subprocess.run([cargo, "build", "-j", "2", "--locked", "--release", "--manifest-path",
                            str(ROOT / "rust/Cargo.toml")], cwd=ROOT, env=env, capture_output=True,
                           text=True, timeout=HANG_TIMEOUT)
    assert built.returncode == 0, built.stdout + built.stderr
    return ROOT / "rust/target/release/ve"


def test_fixtures_are_generated():
    for name, build in FAMILIES.items():
        assert fixture(name) == json.loads(json.dumps(build())), name


@pytest.mark.parametrize("family", list(FAMILIES))
def test_python_matches_expected(family):
    for case in active(family):
        verdict = python_verdict(case)
        assert agrees(case["expected"], verdict), (case["id"], case["expected"], verdict)


@pytest.mark.parametrize("family", list(FAMILIES))
def test_lean_matches_expected(family, lean_executable):
    cases = active(family)
    results = run([str(lean_executable), "route", "-"], [lean_case(c) for c in cases])
    for case, result in zip(cases, results, strict=True):
        verdict = lean_verdict(case, result)
        assert agrees(case["expected"], verdict), (case["id"], case["expected"], result)


@pytest.mark.parametrize("family", list(FAMILIES))
def test_rust_matches_expected(family, rust_executable):
    requests = [(case, rust_request(case)) for case in active(family)]
    requests = [(case, request) for case, request in requests if request is not None]
    if not requests:
        pytest.skip(f"{family} is outside Rust scope")
    results = run([str(rust_executable), "conformance"], [r for _, r in requests])
    for (case, _), result in zip(requests, results, strict=True):
        verdict = rust_verdict(case, result)
        expected = dict(case["expected"])
        if case["kind"] == "vacuity" and expected["premises"] == "INCONSISTENT":
            expected["premises"] = "no model found"  # Rust never certifies inconsistency
        if case["kind"] == "certificate":
            expected = {"status": "ok", "valid": True}  # no countermodel within the bound
        if case["kind"] == "evaluate" and "values" in expected:
            expected["value"] = all(expected.pop("values"))  # the document's value
        assert agrees(expected, verdict), (case["id"], expected, result)


def test_rust_and_python_share_search_models(rust_executable):
    """Beyond verdicts: the same model from bounded search as Python's own search gave at the base
    (tests/data/b15b-search-oracle.json; `python_verdict` searches with Rust since lean-first batch 15b,
    so it is no second engine: review B2), and a model Python's own check accepts. (Rust's identities
    are compared in its countermodel check, tests/test_rust_conformance.py.)"""
    from ve import Environment, FiniteModel
    from ve.ast import formula_from_data
    from ve.search import check_countermodel
    oracle = json.loads((ROOT / "tests/data/b15b-search-oracle.json").read_text())["p0_search_models"]
    cases = [c for c in active("elaborated-document") if c["kind"] == "search"
             and c["expected"]["status"] == "ok"]
    assert cases and set(oracle) == {c["id"] for c in cases}
    results = run([str(rust_executable), "conformance"], [rust_request(c) for c in cases])
    for case, result in zip(cases, results, strict=True):
        assert result["model"] == oracle[case["id"]], case["id"]
        env = Environment(case["environment"])
        assert check_countermodel(env, [formula_from_data(env, p) for p in case["premises"]],
                                  formula_from_data(env, case["conclusion"]),
                                  FiniteModel.from_dict(env, result["model"])).valid, case["id"]


def test_lean_seed_cases_are_the_shared_families():
    """lean/VE/Route/examples/route-cases.json is generated from these families."""
    seeds = json.loads((ROOT / "lean/VE/Route/examples/route-cases.json").read_text())
    expected = [lean_case(c) for name in FAMILIES for c in active(name)]
    assert seeds == json.loads(json.dumps(expected))


def test_python_claim_labels_follow_the_route_grammar():
    from conformance.p0 import environment
    from ve import Environment
    from ve.admission import AdmissionError
    from ve.argument import Claim
    env = Environment(environment())
    assert Claim.create(env, "c", "true.\n", label="background:literals").label == "background:literals"
    for label in ("background:strings", "readings:s@01:0", "free text"):
        with pytest.raises(AdmissionError, match="invalid label"):
            Claim.create(env, "c", "true.\n", label=label)


def test_python_certificates_always_bind_background_first():
    """A premise list that already starts with the Background premise is not
    merged with it: the checked list is Background ++ premises, as in Lean."""
    from conformance.p0 import DISTINCT, FIN_A, SAME, VOCAB, envelope
    from ve import Environment
    from ve.ast import formula_from_data
    from ve.entailment import prove_entailment
    from ve.identity import meaning_id
    env = Environment(envelope(VOCAB))
    premises = [formula_from_data(env, p) for p in (DISTINCT, ["or", SAME, FIN_A])]
    proof = prove_entailment(env, premises, formula_from_data(env, FIN_A))
    distinct = meaning_id(env, premises[0])
    assert proof.certificate["premise_meaning_ids"][:2] == [distinct, distinct]
    assert len(proof.certificate["premise_meaning_ids"]) == 3


def test_checked_premise_order_includes_layer_segment():
    from conformance.p0 import DISTINCT, FIN_A, VOCAB, envelope
    from ve import Environment
    from ve.ast import formula_from_data
    from ve.background import checked_premises
    env = Environment(envelope(VOCAB))
    bg = formula_from_data(env, DISTINCT)
    layer = formula_from_data(env, FIN_A)
    assert checked_premises(env, (layer,), (bg,)) == (bg, layer, bg)


def test_enabled_nary_family_reaches_empty_search_and_invalid_mix_still_gates():
    from conformance.p0 import environment
    from ve import Environment
    from ve.ast import Top
    from ve.errors import UnsupportedProfile
    from ve.search import find_countermodel, find_distinguishing_model
    raw = environment()
    raw["profiles"] = ["closure@0", "nary@0", "relational-fol@0"]
    env = Environment(raw)
    assert find_countermodel(env, (), Top(), max_domain_size=0).status == "NotFound"
    assert find_distinguishing_model(env, Top(), Top(), max_domain_size=0).status == "NotFound"
    raw["profiles"] = ["closure@0", "nary@0", "order@0", "relational-fol@0"]
    with pytest.raises(UnsupportedProfile, match="Unsupported profile combination"):
        Environment(raw)


def test_report_identity_binds_environment_and_document(lean_executable):
    from conformance.p0 import envelope, VOCAB
    from ve.admission import admit_document
    env = envelope(VOCAB)
    document = {"units": [{"id": "u", "span": [0, 1], "kind": "asserted", "content": ["top"]}],
                "graph": {"root": "c", "nodes": [{"name": "c", "ast": ["top"], "unit": "u"}]}}
    variants = [(env, document)]
    changed_env = deepcopy(env)
    changed_env["vocabulary"]["sorts"]["person"]["description"] = "a changed person"
    variants.append((changed_env, document))
    changed_doc = deepcopy(document)
    changed_doc["units"].append({"id": "q", "span": [1, 2],
                                  "kind": ["attributed", "bob", "denies", "asserted"],
                                  "content": ["top"]})
    variants.append((env, changed_doc))
    changed_readings = deepcopy(document)
    changed_readings["reading_sets"] = [{"id": "r", "version": 1, "readings": [["top"]]}]
    variants.append((env, changed_readings))
    cases = [{"id": str(i), "kind": "admission", "environment": e, "document": d}
             for i, (e, d) in enumerate(variants)]
    lean = run([str(lean_executable), "route", "-"], cases)
    python = [admit_document(e, d) for e, d in variants]
    assert [row["report_id"] for row in lean] == [row["report_id"] for row in python]
    assert len({row["report_id"] for row in python}) == len(variants)
    assert all(row["report"] == python[0]["report"] for row in python)


def test_data_background_deduction_admission_matches_lean(lean_executable):
    """Explicit generated leaves remain generated at every graph edge position."""
    from tests.test_data_flags import environment
    from ve.admission import admit_document
    from ve.ast import Top, formula_to_data
    from ve.background import background
    from ve.entailment import prove_entailment
    from ve.identity import meaning_id

    env = environment()
    generated = background(env)
    proof = prove_entailment(env, (), Top())
    assert proof.status == "Found"
    leaves = [{"name": f"bg{i}", "ast": formula_to_data(env, item.formula, _generated=True),
               "label": f"background:{item.generator}"}
              for i, item in enumerate(generated)]
    ordinary = {"name": "ordinary", "ast": ["top"], "unit": "u"}
    units = [{"id": "u", "span": [0, 1], "kind": "asserted", "content": ["top"]}]
    orders = (leaves, list(reversed(leaves)), [leaves[0], ordinary, *leaves[1:]])
    cases = []
    for i, ordered in enumerate(orders):
        certificate = deepcopy(proof.certificate)
        certificate["premise_meaning_ids"] = [
            meaning_id(env, generated[int(node["name"][2:])].formula, _generated=True)
            if node["name"].startswith("bg") else meaning_id(env, Top())
            for node in ordered]
        document = {"units": units, "graph": {"root": "result", "nodes": [*ordered, {
            "name": "result", "ast": ["top"], "premises": [node["name"] for node in ordered],
            "certificate": certificate}]}}
        cases.append({"id": str(i), "kind": "admission", "environment": env.to_dict(),
                      "document": document})
    lean = run([str(lean_executable), "route", "-"], cases)
    python = [admit_document(env, case["document"]) for case in cases]
    assert all(row["status"] == "ok" for row in lean)
    assert [row["report"] for row in lean] == [row["report"] for row in python]
    assert [row["report_id"] for row in lean] == [row["report_id"] for row in python]


def test_frozen_lean_sources_are_in_suite():
    result = subprocess.run([shutil.which("python3") or "python", "VE/Route/frozen.py"],
                            cwd=ROOT / "lean", capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_hostile_wire_diagnostics_match_three_ways(lean_executable, rust_executable):
    from conformance.p0 import environment
    base = environment()
    empty = deepcopy(base)
    empty["vocabulary"] = {"sorts": {}, "predicates": {}, "constants": {}}
    no_vocab = deepcopy(base)
    no_vocab["vocabulary"] = {}
    nonstring = deepcopy(base)
    nonstring["profiles"] = [42]
    legacy = deepcopy(base)
    legacy["language"] = "ve.core@0.1"
    model = {"complete": True, "domains": {"$string": ["a", "b"]},
             "constants": {"alpha": "a", "beta": "b"}, "relations": {}}
    cases = [
        {"id": "label-bad-vocabulary", "kind": "label", "environment": no_vocab,
         "label": "asserted"},
        {"id": "nonstring-profile", "kind": "label", "environment": nonstring,
         "label": "asserted"},
        {"id": "legacy-string", "kind": "evaluate", "environment": legacy,
         "model": model, "ast": [["top"]]},
        {"id": "extraneous-string-domain", "kind": "evaluate", "environment": empty,
         "model": model, "ast": [["top"]]},
        {"id": "missing-string-domain", "kind": "evaluate", "environment": base,
         "model": {"complete": True, "domains": {}, "constants": {}, "relations": {}},
         "ast": [["top"]]},
    ]
    lean = run([str(lean_executable), "route", "-"], cases)
    # Rust has no label route: it decodes a label case's envelope through a typing case.
    rust = run([str(rust_executable), "conformance"],
               [{"id": c["id"], **rust_envelope(c["environment"])} if c["kind"] == "label"
                else rust_request(c) for c in cases])
    def reason(message):
        if "sorts" in message and "predicates" in message and "constants" in message and "field" in message:
            return "vocabulary fields"
        if "profile" in message.lower() and ("string" in message or "array" in message):
            return "profile type"
        if "language" in message or "profiles or specification revision" in message:
            return "legacy envelope"
        if ("domains" in message or "declared sorts, constants and predicates" in message or
                ("fields do not match" in message and "$string" in message)):
            return "model declaration shape"
        return None
    expected_reasons = ("vocabulary fields", "profile type", "legacy envelope",
                        "model declaration shape", "model declaration shape")
    for case, l, r, expected in zip(cases, lean, rust, expected_reasons, strict=True):
        py = python_verdict(case)
        le = lean_verdict(case, l)
        ru = rust_verdict(case, r)
        assert py["status"] == le["status"] == ru["status"] == "error", case["id"]
        assert [reason(v["error"]) for v in (py, le, ru)] == [expected] * 3, (case["id"], py, le, ru)


def test_stale_proof_does_not_become_search_agreement(lean_executable, rust_executable):
    from conformance.p0 import environment, certificate
    env = environment()
    proof = certificate(env, [], ["top"])
    stale = deepcopy(proof)
    stale["conclusion_meaning_id"] = "0" * 64
    cases = [{"id": tag, "kind": "certificate", "environment": env,
              "premises": [], "conclusion": ["top"], "certificate": cert}
             for tag, cert in (("valid", proof), ("stale", stale))]
    lean = run([str(lean_executable), "route", "-"], cases)
    py = [python_verdict(c) for c in cases]
    assert [p.get("valid") for p in py] == [True, False]
    assert lean[0]["valid"] is True
    assert lean[1]["status"] == "error" and lean[1]["valid"] is False
    # Rust's bounded search is an operational check, never proof replay.
    search = [{"id": c["id"], "environment": env, "premises": [],
               "conclusion": ["top"], "max_domain_size": 2} for c in cases]
    rust = run([str(rust_executable), "conformance"], search)
    assert [r["status"] for r in rust] == ["NotFound", "NotFound"]


def test_order_countermodel_three_way_agreement(lean_executable, rust_executable):
    from conformance.p0 import ORDER_MODEL, ORDER_VOCAB, envelope
    env = envelope(ORDER_VOCAB, ("order@0", "relational-fol@0"))
    case = {"id": "order-refutation", "kind": "countermodel", "environment": env,
            "model": ORDER_MODEL, "premises": [["top"]], "conclusion": ["bottom"]}
    py = python_verdict(case)
    lean = lean_verdict(case, run([str(lean_executable), "route", "-"], [case])[0])
    rust = rust_verdict(case, run([str(rust_executable), "conformance"], [rust_request(case)])[0])
    assert py["refutes"] is lean["refutes"] is rust["refutes"] is True
    from ve import Environment
    from ve.ast import Top
    from ve.search import find_countermodel
    bounded = find_countermodel(Environment(env), (), Top(), max_domain_size=1)
    assert bounded.status == "NotFound" and bounded.models_checked == 0


def test_hedged_bridge_and_kind_depth_boundary(lean_executable):
    from conformance.p0 import environment
    env = environment()
    kind = "asserted"
    for _ in range(15):
        kind = ["hedged", "likely", kind]
    document = {"units": [{"id": "u", "span": [0, 1], "kind": kind,
                           "content": ["top"]}],
                "graph": {"root": "c", "nodes": [{"name": "c", "ast": ["top"],
                        "unit": "u", "label": "bridge:accepts(alice,u)"}]}}
    case = {"id": "hedged-depth-16", "kind": "admission", "environment": env,
            "document": document}
    py = python_verdict(case)
    le = lean_verdict(case, run([str(lean_executable), "route", "-"], [case])[0])
    assert py == {k: le[k] for k in py}
    document["units"][0]["kind"] = ["hedged", "likely", kind]
    py = python_verdict(case)
    le = lean_verdict(case, run([str(lean_executable), "route", "-"], [case])[0])
    assert py["status"] == le["status"] == "error"
    assert "kind depth" in py["error"] and "kind depth" in le["error"]


def test_argument_lean_replay_uses_route(lean_executable):
    from conformance.p0 import environment
    from ve import ArgumentGraph, Claim, Deduction, Environment, check_argument
    env = Environment(environment())
    graph = ArgumentGraph(env,
                          (Claim.create(env, "premise", "true.\n"),
                           Claim.create(env, "root", "true.\n")),
                          (Deduction("step", ("premise",), "root"),), "root")
    result = check_argument(graph, lean_executable=lean_executable, max_models=0)
    assert result.composed and result.lean_checked, result.to_dict()
