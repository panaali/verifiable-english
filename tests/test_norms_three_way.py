"""Committed W1 wire gate: regenerated Python/Lean formulas and Rust evaluation.

Rust receives generated formulas as untrusted inputs, as specified in 11.6;
it does not elaborate norms. The conflict and certificate verdicts are replayed
by Python and Lean, while Rust independently evaluates the generated formulas.
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
from pathlib import Path

import pytest

from ve.ast import Const, Exists, Not, Top, Unary, Var, _to_data, formula_to_data
from ve.adapters.cedar import translate
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.norms import NormDocument, _bind, _instantiate, check_conflict
from tests.test_norms import environment, model, obligation, permission, rule

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_norms_route"
RUST = ROOT / "rust/target/release/ve"


@pytest.fixture(scope="module")
def lean_executable():
    if not LEAN.exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip("lake is required for the W1 wire gate")
        built = subprocess.run([lake, "build"], cwd=ROOT / "lean", capture_output=True,
                               text=True, timeout=600)
        assert built.returncode == 0, built.stdout + built.stderr
    return LEAN


@pytest.fixture(scope="module")
def rust_executable():
    cargo = shutil.which("cargo")
    if cargo is None:
        pytest.skip("cargo is required for the W1 wire gate")
    env = {**os.environ, "CARGO_HOME": str(ROOT / ".cargo-home"),
           "CARGO_TARGET_DIR": str(ROOT / "rust/target")}
    built = subprocess.run([cargo, "build", "-j", "2", "--locked", "--release",
                            "--manifest-path", str(ROOT / "rust/Cargo.toml")],
                           cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    assert built.returncode == 0, built.stdout + built.stderr
    return RUST


def run(executable, cases):
    command = [str(executable)] + (["conformance"] if executable == RUST else []) + ["-"]
    result = subprocess.run(command, input=json.dumps(cases),
                            text=True, capture_output=True, timeout=180)
    assert result.returncode in (0, 1), result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    return rows


def corpus(count=1000):
    rng = random.Random(1102)
    for i in range(count):
        env = environment({"permitted": permission("allow" if i % 2 else "deny")},
                          base={"condition": {"arguments": ["act"], "description": "condition"}})
        rules = []
        for j in range(rng.randrange(1, 6)):
            parents = tuple(r.name for r in rules if rng.randrange(4) == 0)[:2]
            guard = (Top() if rng.randrange(2) else Unary("condition", Var(0)))
            unless = tuple(rng.choice((Top(), Unary("condition", Var(0))))
                           for _ in range(rng.randrange(3)))
            rules.append(rule(f"r{j}", "permitted", bool(rng.randrange(2)), guard,
                              unless=unless, over=parents))
        yield NormDocument(env, rules)


def pair_corpus(count=100):
    rng = random.Random(1103)
    for i in range(count):
        env = environment({"permitted": permission("allow" if i % 2 else "deny"),
                           "required": obligation("allow" if i % 3 else "deny")})
        rules = []
        for name in ("permitted", "required"):
            if rng.randrange(2):
                rules.append(rule(f"r-{name}", name, bool(rng.randrange(2))))
        yield NormDocument(env, rules)


def lean_case(index, doc):
    return {"id": str(index), "kind": "norms-elaborate", "environment": doc.env.to_dict(),
            "norms": [r.to_dict() for r in doc.rules]}


def test_1100_regenerated_documents_match_lean(lean_executable):
    docs = [*corpus(), *pair_corpus()]
    results = run(lean_executable, [lean_case(i, d) for i, d in enumerate(docs)])
    for i, (doc, got) in enumerate(zip(docs, results, strict=True)):
        assert got["status"] == "ok", (i, got)
        assert got["order"] == list(doc.order), i
        assert got["premises"] == [
            {"label": label, "ast": formula_to_data(doc.env, ast)}
            for label, ast in doc.premises()], i
        assert got["conflict_targets"] == [
            {"target": target, "sorts": list(sorts), "ast": _to_data(ast)}
            for target, sorts, ast in doc.conflict_targets()], i


def test_conflict_witness_and_certificates_match_lean(lean_executable):
    env = environment({"permitted": permission()},
                      base={"condition": {"arguments": ["act"], "description": "condition"}})
    yes = rule("yes", "permitted", True)
    no = rule("no", "permitted", False)
    pair = environment({"permitted": permission(), "required": obligation()})
    default_pair = environment({"permitted": permission(),
                                "required": obligation("allow")})
    examples = [NormDocument(env, [yes, no]),
                NormDocument(env, [no, rule("exception", "permitted", True, over=("no",))]),
                NormDocument(env, [no, rule("carved", "permitted", True, unless=(Top(),))]),
                NormDocument(pair, [rule("must", "required", True)]),
                NormDocument(default_pair, []),
                NormDocument(pair, [rule("must", "required", True),
                                    rule("may", "permitted", True)])]
    cases = []
    expected = []
    for i, doc in enumerate(examples):
        report = check_conflict(doc, model=model(doc))
        if report.status == "CONFLICT":
            cases.append({**lean_case(i, doc), "kind": "norms-conflict",
                          "witness": {"target": report.target, "model": model(doc).to_dict(),
                                      "tuple": list(report.tuple)}})
        else:
            from ve.entailment import prove_entailment
            packages = {}
            for target, sorts, formula in doc.conflict_targets():
                proof = prove_entailment(doc.base_environment(), (), _bind(Not(formula), sorts))
                assert proof.status == "Found"
                packages[target] = {"environment_id": doc.env.environment_id,
                                    "document_hash": doc.document_hash, "target": target,
                                    "certificate": proof.certificate}
            assert check_conflict(doc, certificates=packages).status == "CONFLICT-FREE"
            cases.append({**lean_case(i, doc), "kind": "norms-conflict", "packages": packages})
        expected.append("CONFLICT" if report.status == "CONFLICT" else "CONFLICT-FREE")
    results = run(lean_executable, cases)
    assert [r["verdict"] for r in results] == expected
    stale = json.loads(json.dumps(cases[1]))
    stale["packages"]["permitted"]["document_hash"] = "0" * 64
    assert run(lean_executable, [stale])[0]["verdict"] == "UNKNOWN"


def test_rust_evaluates_python_generated_conflicts(rust_executable):
    docs = list(corpus(48))
    cases = []
    expected = []
    for i, doc in enumerate(docs):
        base = doc.base_environment()
        witness = model(doc, condition=[["act0"]] if i % 2 else [])
        _, _, conflict = doc.conflict_targets()[0]
        closed = _bind(conflict, ("act",), binder=Exists)
        cases.append({"id": str(i), "environment": base.to_dict(), "model": witness.to_dict(),
                      "ast": [formula_to_data(base, closed)]})
        expected.append(evaluate(base, closed, witness).value)
    got = run(rust_executable, cases)
    assert [row["values"][0] for row in got] == expected


def test_rust_evaluates_python_generated_completions(rust_executable):
    from ve.evaluate import _Evaluator
    docs = list(corpus(48))
    cases = []
    expected = []
    for i, doc in enumerate(docs):
        condition = [["act0"]] if i % 2 else []
        base = model(doc, condition=condition)
        outcome = _Evaluator(doc.base_environment(), base, 100000, trace=False).formula(
            doc.outcome("permitted", base=True), (("act", "act0"),))[0]
        full = FiniteModel.from_dict(doc.env, {"complete": True,
            "domains": {"act": ["act0"]}, "constants": {},
            "relations": {"condition": condition,
                          "permitted": [["act0"]] if outcome else []}})
        premise = doc.elaborate("permitted")
        expected.append(evaluate(doc.env, premise, full).value)
        cases.append({"id": str(i), "environment": doc.env.to_dict(), "model": full.to_dict(),
                      "ast": [formula_to_data(doc.env, premise)]})
    got = run(rust_executable, cases)
    assert [row["values"][0] for row in got] == expected
    assert set(expected) == {False, True}


def test_rust_agrees_on_22_pinned_cedar_decisions(rust_executable):
    root = ROOT / "experiments/P3-formalisation-tax/items"
    cases = []
    expected = []
    for path in sorted(root.glob("c*_cit_*/item.json")):
        item = json.loads(path.read_text())
        policy = (path.parent / "source.cedar").read_text()
        questions = item["questions"]
        translated = translate(policy, item["world"].get("linked", []),
                               item["world"]["entities"], [q["request"] for q in questions])
        if translated.exclusions:
            continue
        base_data = translated.document.base_environment().to_dict()
        base_data["vocabulary"]["constants"]["query"] = {"sort": "request",
                                                          "description": "chosen request"}
        base = Environment(base_data)
        outcome = _instantiate(translated.document.outcome("permitted", base=True),
                               (Const("query"),))
        for decision, request_id in zip(translated.decisions(), translated.request_ids, strict=True):
            model_data = translated.model.to_dict()
            model_data["relations"].pop("permitted")
            model_data["constants"]["query"] = request_id
            finite = FiniteModel.from_dict(base, model_data)
            truth = decision["decision"] == "allow"
            assert evaluate(base, outcome, finite).value == truth
            cases.append({"id": f"cedar-{len(cases)}", "environment": base.to_dict(),
                          "model": finite.to_dict(), "ast": [formula_to_data(base, outcome)]})
            expected.append(truth)
    assert len(cases) == 22
    got = run(rust_executable, cases)
    assert [row["values"][0] for row in got] == expected
