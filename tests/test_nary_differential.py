"""Generated n-ary certificates and cross-language finite tables."""
from __future__ import annotations

import json
import os
import random
import shutil
from subprocesses import HANG_TIMEOUT
import subprocess
from pathlib import Path

import pytest

from ve.ast import And, Atom, Body, Const, Eq, Forall, Implies, Reach, Var, formula_to_data
from ve.ast import formula_from_data
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.background import background
from ve.identity import meaning_id
from ve.model import FiniteModel
from ve.closure import induction_step
from ve.profiles import LANGUAGE, SPEC_REVISION

ROOT = Path(__file__).resolve().parents[1]
LETTERS = "abcdef"


def environment(arity=6, *, literals=False):
    constants = {c: {"sort": "item", "description": c} for c in LETTERS}
    if literals:
        constants.update({"litone": {"sort": "$string"}, "littwo": {"sort": "$string"}})
    return Environment({
        "language": LANGUAGE,
        "profiles": ["closure@0", "nary@0", "relational-fol@0"],
        "spec_revision": SPEC_REVISION,
        "vocabulary": {"sorts": {"item": {"description": "Item"}},
                       "predicates": {"p": {"arguments": ["item"] * arity,
                                            "description": "Positional relation"}},
                       "constants": constants},
    })


def invoke(binary, command, cases, *, errors=False):
    result = subprocess.run([str(binary), command], input=json.dumps(cases), text=True,
                            capture_output=True, timeout=HANG_TIMEOUT)
    assert result.returncode == int(errors), result.stdout + result.stderr
    return json.loads(result.stdout)


def test_nary_route_regenerates_literal_background(lean_binary):
    raw = environment(3).to_dict()
    raw["vocabulary"]["constants"].update({
        "litone": {"sort": "$string"}, "littwo": {"sort": "$string"}})
    env = Environment(raw)
    row = invoke(lean_binary, "route", [{"id": "nary-background",
        "kind": "background", "environment": env.to_dict()}])[0]
    from ve.ast import formula_to_data
    premises = background(env)
    assert row["status"] == "ok"
    assert row["background"] == [formula_to_data(env, item.formula) for item in premises]
    assert row["generators"] == [item.generator for item in premises]


@pytest.fixture(scope="module")
def lean_binary():
    binary = ROOT / "lean/.lake/build/bin/ve_conformance"
    if os.environ.get("VE_LEAN_PREBUILT"):
        assert binary.is_file(), f"gate Lean build missing: {binary}"
        return binary
    if not binary.exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip("Lean is unavailable")
        result = subprocess.run([lake, "build", "ve_conformance"], cwd=ROOT / "lean",
                                capture_output=True, text=True, timeout=HANG_TIMEOUT)
        assert result.returncode == 0, result.stdout + result.stderr
    return binary


@pytest.fixture(scope="module")
def rust_binary():
    binary = (Path(os.environ["VE_RUST_BINARY"]) if os.environ.get("VE_RUST_PREBUILT")
              else ROOT / "rust/target/debug/ve")
    if os.environ.get("VE_RUST_PREBUILT"):
        assert binary.is_file(), f"gate Rust build missing: {binary}"
        return binary
    if not binary.exists():
        cargo = shutil.which("cargo")
        if cargo is None:
            pytest.skip("Rust is unavailable")
        env = {**os.environ, "CARGO_HOME": str(ROOT / ".cargo-home")}
        result = subprocess.run([cargo, "build", "-q", "-p", "ve"], cwd=ROOT / "rust",
                                env=env, capture_output=True, text=True, timeout=HANG_TIMEOUT)
        assert result.returncode == 0, result.stdout + result.stderr
    return binary


def test_500_certificates_and_2000_mutations_agree_with_lean(lean_binary):
    env = environment()
    cases, expected = [], []
    for index in range(500):
        digits = [LETTERS[index // (6 ** power) % 6] for power in range(4)]
        names = ["a", "b", *digits]
        premise = Atom("p", tuple(Const(name) for name in names))
        proof = prove_entailment(env, [premise], premise)
        assert proof.status == "Found"
        certificate = proof.certificate
        queries = [(premise, certificate, True)]
        for changed in (["b", "a", *digits], ["c", "b", *digits],
                        ["a", "c", *digits],
                        ["a", "b", LETTERS[(LETTERS.index(digits[0]) + 1) % 6], *digits[1:]]):
            conclusion = Atom("p", tuple(Const(name) for name in changed))
            mutant = {**certificate, "conclusion_meaning_id": meaning_id(env, conclusion)}
            queries.append((conclusion, mutant, False))
        for conclusion, cert, valid in queries:
            assert check_entailment_certificate(env, [premise], conclusion, cert).valid is valid
            cases.append({"id": str(len(cases)), "kind": "certificate",
                          "environment": env.to_dict(),
                          "premises": [formula_to_data(env, premise)],
                          "conclusion": formula_to_data(env, conclusion),
                          "certificate": cert})
            expected.append(valid)
    assert (sum(expected), len(expected) - sum(expected)) == (500, 2000)
    observed = []
    for start in range(0, len(cases), 250):
        observed += [result.get("valid") for result in invoke(lean_binary, "route", cases[start:start + 250])]
    assert observed == expected


def test_statement_profile_preserves_core_family(lean_binary, rust_binary):
    env = environment(3)
    raw = env.to_dict()
    raw["profiles"] = ["closure@0", "documents@1", "nary@0", "relational-fol@0"]
    combined = Environment(raw)
    atom = Atom("p", (Const("a"), Const("b"), Const("c")))
    proof = prove_entailment(combined, [atom], atom)
    assert proof.status == "Found"
    case = {"id": "documents", "kind": "certificate", "environment": raw,
            "premises": [formula_to_data(combined, atom)],
            "conclusion": formula_to_data(combined, atom), "certificate": proof.certificate}
    assert check_entailment_certificate(combined, [atom], atom, proof.certificate).valid
    assert invoke(lean_binary, "route", [case])[0]["valid"] is True
    model = {"complete": True, "domains": {"item": ["x"]},
             "constants": {name: "x" for name in LETTERS},
             "relations": {"p": [["x", "x", "x"]]}}
    evaluation = {"id": "documents-evaluation", "kind": "evaluate", "environment": raw,
                  "ast": [formula_to_data(combined, atom)], "model": model}
    assert invoke(lean_binary, "route", [evaluation])[0]["values"] == [True]
    assert invoke(rust_binary, "conformance", [evaluation])[0]["values"] == [True]


def test_stage0_core_nary_probe_checks_positions_and_replay(lean_binary, rust_binary):
    from tests import probe_matrix as probe

    env = Environment(probe.raw_environment(("closure@0", "nary@0")))
    model_wire = probe.model_wire(env)
    model = FiniteModel.from_dict(env, model_wire)
    atom = probe.semantic_formula(env)
    reversed_atom = Atom("triple", (Const("y"), Const("x"), Const("x")))
    assert [evaluate(env, formula, model).value for formula in (atom, reversed_atom)] == [True, False]
    case = {"id": "stage0-nary", "kind": "evaluate", "environment": env.to_dict(),
            "ast": [formula_to_data(env, formula) for formula in (atom, reversed_atom)],
            "model": model_wire}
    assert invoke(lean_binary, "route", [case])[0]["values"] == [True, False]
    assert invoke(rust_binary, "conformance", [case])[0]["values"] == [True, False]

    premises = (Forall("item", Atom("triple", (Var(0), Const("y"), Const("x")))),)
    proof = prove_entailment(env, premises, atom)
    assert proof.status == "Found"
    assert check_entailment_certificate(env, premises, atom, proof.certificate).valid
    replay = {"id": "stage0-nary-replay", "kind": "certificate",
              "environment": env.to_dict(),
              "premises": [formula_to_data(env, premise) for premise in premises],
              "conclusion": formula_to_data(env, atom), "certificate": proof.certificate}
    assert invoke(lean_binary, "route", [replay])[0]["valid"] is True


def test_substitution_quantification_and_body_closure_agree_with_lean(lean_binary):
    env = environment(3)
    a, b, c = (Const(name) for name in "abc")
    atom = Atom("p", (a, b, c))
    cases = [
        ([Eq(a, b), atom], Atom("p", (b, b, c)), "equality"),
        ([Forall("item", Atom("p", (Var(0), b, c)))], atom, "quantifier"),
        ([atom], Reach("plus", Body("item", Atom("p", (Var(1), Var(0), c))), a, b),
         "body closure"),
    ]
    wire = []
    for premises, conclusion, label in cases:
        proof = prove_entailment(env, premises, conclusion, max_steps=500)
        assert proof.status == "Found", label
        assert check_entailment_certificate(env, premises, conclusion, proof.certificate).valid
        wire.append({"id": label, "kind": "certificate", "environment": env.to_dict(),
                     "premises": [formula_to_data(env, premise) for premise in premises],
                     "conclusion": formula_to_data(env, conclusion),
                     "certificate": proof.certificate})
    assert [result["valid"] for result in invoke(lean_binary, "route", wire)] == [True] * 3


def test_nary_body_induction_certificate_agrees_with_lean(lean_binary):
    env = environment(3)
    invariant = Atom("p", (Var(0), Const("b"), Const("c")))
    edge = Body("item", Atom("p", (Var(1), Var(0), Const("c"))))
    goal = Forall("item", Implies(And(invariant, induction_step("item", edge, invariant)),
        Forall("item", Implies(Reach("plus", edge, Var(1), Var(0)), invariant))))
    proof = prove_entailment(env, [], goal, invariants=[invariant], max_steps=1000)
    assert proof.status == "Found"
    assert 'closure-induct@1' in json.dumps(proof.certificate)
    assert check_entailment_certificate(env, [], goal, proof.certificate).valid
    case = {"id": "induction", "kind": "certificate", "environment": env.to_dict(),
            "premises": [], "conclusion": formula_to_data(env, goal),
            "certificate": proof.certificate}
    assert invoke(lean_binary, "route", [case])[0]["valid"] is True


def test_5000_finite_table_pairs_agree_with_rust(rust_binary):
    randomizer = random.Random(4056)
    environments = {arity: environment(arity) for arity in range(3, 7)}
    domain = ["x", "y", "z"]
    constants = dict(zip(LETTERS, domain * 2, strict=True))
    cases, expected = [], []
    for index in range(5000):
        arity = 3 + index % 4
        env = environments[arity]
        names = [randomizer.choice(LETTERS) for _ in range(arity)]
        rows = {tuple(randomizer.choice(domain) for _ in range(arity))
                for _ in range(randomizer.randrange(1, 4))}
        model_wire = {"complete": True, "domains": {"item": domain},
                      "constants": constants,
                      "relations": {"p": [list(row) for row in sorted(rows)]}}
        model = FiniteModel.from_dict(env, model_wire)
        atom = Atom("p", tuple(Const(name) for name in names))
        expected.append(evaluate(env, atom, model, trace=False).value)
        cases.append({"id": str(index), "environment": env.to_dict(),
                      "ast": [formula_to_data(env, atom)], "model": model_wire})
    observed = []
    for start in range(0, len(cases), 250):
        observed += [result.get("values", [None])[0]
                     for result in invoke(rust_binary, "conformance", cases[start:start + 250])]
    assert observed == expected


def test_mixed_nary_background_validation_agrees(lean_binary, rust_binary):
    env = environment(3, literals=True)
    atom = Atom("p", (Const("a"), Const("a"), Const("b")))
    base = {"complete": True, "domains": {"item": ["x", "y"], "$string": ["one", "two"]},
            "constants": {**{c: "x" for c in LETTERS}, "litone": "one", "littwo": "two"},
            "relations": {"p": [["x", "x", "x"]]}}
    cases = []
    for alias in (False, True):
        wire = json.loads(json.dumps(base))
        if alias:
            wire["constants"]["littwo"] = "one"
        cases.append({"id": str(alias), "kind": "evaluate", "environment": env.to_dict(),
                      "ast": [formula_to_data(env, atom)], "model": wire})
    lean = invoke(lean_binary, "route", cases, errors=True)
    rust = invoke(rust_binary, "conformance", cases, errors=True)
    assert lean[0]["values"] == rust[0]["values"] == [True]
    assert lean[1]["generator"] == "literals"
    assert rust[1]["error"]["code"] == "InvalidModel"


def test_hostile_nary_wire_diagnostics_agree(lean_binary, rust_binary):
    env = environment(3)
    good = [["const", "a"], ["const", "a"], ["const", "b"]]
    wires = [
        (["atom", "p", good[:2]], "SyntaxError"),
        (["atom", "p", good + good + good[:1]], "SyntaxError"),
        (["atom", "p", "not-an-array"], "SyntaxError"),
        (["atom", "p", good[:2] + [["const", "missing"]]], "UnknownSymbol"),
    ]
    cases = []
    model = {"complete": True, "domains": {"item": ["x"]},
             "constants": {c: "x" for c in LETTERS},
             "relations": {"p": [["x", "x", "x"]]}}
    for index, (wire, diagnostic) in enumerate(wires):
        with pytest.raises(Exception) as error:
            formula_from_data(env, wire)
        assert type(error.value).__name__ == diagnostic
        cases.append({"id": str(index), "kind": "evaluate", "environment": env.to_dict(),
                      "ast": [wire], "model": model})
    repeated = ["atom", "p", good]
    assert formula_from_data(env, repeated) == Atom("p", (Const("a"), Const("a"), Const("b")))
    cases.append({"id": "repeated", "kind": "evaluate", "environment": env.to_dict(),
                  "ast": [repeated], "model": model})
    lean = invoke(lean_binary, "route", cases, errors=True)
    rust = invoke(rust_binary, "conformance", cases, errors=True)
    for index, (_, diagnostic) in enumerate(wires):
        assert rust[index]["error"]["code"] == diagnostic
        if diagnostic == "SyntaxError":
            assert lean[index]["error"] == rust[index]["error"]["message"]
        else:
            assert lean[index]["error"].startswith(diagnostic + ":")
    assert lean[-1]["values"] == rust[-1]["values"] == [True]

    wrong_sort = env.to_dict()
    wrong_sort["vocabulary"]["predicates"]["p"]["arguments"][2] = "missing"
    with pytest.raises(Exception) as error:
        Environment(wrong_sort)
    assert type(error.value).__name__ == "UnknownSymbol"
    bad_environment = [{"id": "unknown-third-sort", "kind": "evaluate",
                        "environment": wrong_sort, "ast": [repeated], "model": model}]
    lean_error = invoke(lean_binary, "route", bad_environment, errors=True)[0]["error"]
    rust_error = invoke(rust_binary, "conformance", bad_environment, errors=True)[0]["error"]
    assert lean_error.startswith("UnknownSymbol:")
    assert rust_error["code"] == "UnknownSymbol"


def test_frozen_v0_and_closure_evaluation_corpora_replay_through_core(lean_binary):
    cases, expected = [], []
    for filename in ("evaluation.json", "closure.json"):
        for old in json.loads((ROOT / "conformance" / filename).read_text()):
            raw = {key: value for key, value in old["environment"].items() if key != "profile"}
            raw.update(language=LANGUAGE, spec_revision=SPEC_REVISION,
                       profiles=["closure@0", "nary@0", "relational-fol@0"])
            env = Environment(raw)
            model = FiniteModel.from_dict(env, old["model"])
            formulas = [formula_from_data(env, wire) for wire in old["ast"]]
            assert [evaluate(env, formula, model, trace=False).value
                    for formula in formulas] == old["expected"]
            cases.append({"id": old["id"], "kind": "evaluate", "environment": raw,
                          "ast": old["ast"], "model": old["model"]})
            expected.append(old["expected"])
    observed = []
    for start in range(0, len(cases), 100):
        observed.extend(result.get("values") for result in
                        invoke(lean_binary, "route", cases[start:start + 100]))
    assert len(cases) == 747
    assert observed == expected
