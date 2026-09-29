"""Differential elaboration of definitions (PLAN-EXPAND2 W3(7)).

1,000 generated definition sets (random bodies, dependency depth up to 4,
declarations shuffled so the dependency order must be computed) are elaborated
by Python `ve.definitions.expand` and by the Lean route's `Definitions.expand`
(the `background` case kind); the Background lists must be identical. On a
random base model the defined tables computed by Python, Lean and Rust must
agree. Mutations (swapping two bodies, changing one body) change
`environment_id`, and a certificate bound to the original environment is
rejected by both certificate checkers.
"""
from __future__ import annotations

import json
import os
import random
import shutil
from subprocesses import HANG_TIMEOUT
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

from ve.profiles import LANGUAGE, SPEC_REVISION

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_conformance"
SETS = 1000
SEED = 20260926

BASE = {"p": ["s"], "q": ["t"], "r": ["s", "t"], "e": ["s", "s"]}
CONSTANTS = {"c": "s", "k": "t"}


def _terms(rng, sort, context):
    options = [["var", i] for i, s in enumerate(context) if s == sort]
    options += [["const", name] for name, s in CONSTANTS.items() if s == sort]
    return rng.choice(options)


def _formula(rng, depth, context, predicates):
    choice = rng.random()
    if depth == 0 or choice < 0.35:
        atoms = [(name, sig) for name, sig in predicates.items()]
        name, sig = rng.choice(atoms)
        if rng.random() < 0.1:
            sort = rng.choice(["s", "t"])
            return ["eq", _terms(rng, sort, context), _terms(rng, sort, context)]
        if len(sig) == 1:
            return ["unary", name, _terms(rng, sig[0], context)]
        return ["binary", name, _terms(rng, sig[0], context), _terms(rng, sig[1], context)]
    if choice < 0.45:
        return ["not", _formula(rng, depth - 1, context, predicates)]
    if choice < 0.75:
        tag = rng.choice(["and", "or", "implies"])
        return [tag, _formula(rng, depth - 1, context, predicates),
                _formula(rng, depth - 1, context, predicates)]
    sort = rng.choice(["s", "t"])
    tag = rng.choice(["forall", "exists"])
    return [tag, sort, _formula(rng, depth - 1, [sort] + context, predicates)]


def generate(index):
    """One environment with 1-6 definitions, some stacked four deep."""
    rng = random.Random(SEED * 10_000 + index)
    available = dict(BASE)
    level = {name: 0 for name in BASE}
    definitions = {}
    for n in range(rng.randint(1, 6)):
        name = f"d{n}"
        arguments = rng.choice([["s"], ["t"], ["s", "t"], ["s", "s"]])
        candidates = {p: sig for p, sig in available.items() if level[p] < 4}
        body = _formula(rng, rng.randint(0, 3), list(reversed(arguments)), candidates)
        definitions[name] = {"arguments": arguments, "description": f"defined {name}",
                             "defined": {"arguments": arguments, "body": body}}
        mentioned = _mentions(body)
        level[name] = 1 + max((level[p] for p in mentioned), default=0)
        available[name] = arguments
    names = list(definitions)
    rng.shuffle(names)
    predicates = {name: {"arguments": sig, "description": name} for name, sig in BASE.items()}
    predicates.update({name: definitions[name] for name in names})
    env = {"language": LANGUAGE, "profiles": ["definitions@0", "relational-fol@0"],
           "spec_revision": SPEC_REVISION,
           "vocabulary": {"sorts": {"s": {"description": "sort s"}, "t": {"description": "sort t"}},
                          "predicates": predicates,
                          "constants": {name: {"sort": sort, "description": name}
                                        for name, sort in CONSTANTS.items()}}}
    domains = {"s": ["a", "b"][:rng.randint(1, 2)], "t": ["u", "v"][:rng.randint(1, 2)]}
    relations = {}
    for name, sig in BASE.items():
        rows = [[x] for x in domains[sig[0]]] if len(sig) == 1 else [
            [x, y] for x in domains[sig[0]] for y in domains[sig[1]]]
        relations[name] = [row for row in rows if rng.random() < 0.5]
    model = {"complete": True, "domains": domains,
             "constants": {"c": domains["s"][0], "k": domains["t"][-1]}, "relations": relations}
    return env, model, max(level.values())


def _mentions(body):
    if body[0] in ("unary", "binary"):
        return {body[1]}
    return set().union(*(_mentions(x) for x in body[1:] if type(x) is list and x and
                         type(x[0]) is str and x[0] not in ("var", "const")))


def probes(env):
    """Formulas reading every defined table: for each defined p, one atom per
    argument tuple of the probe context."""
    out = []
    for name, entry in env["vocabulary"]["predicates"].items():
        if "defined" not in entry:
            continue
        sig = entry["arguments"]
        if len(sig) == 1:
            out.append(["exists", sig[0], ["unary", name, ["var", 0]]])
            out.append(["forall", sig[0], ["unary", name, ["var", 0]]])
        else:
            out.append(["forall", sig[0], ["exists", sig[1], ["binary", name, ["var", 1], ["var", 0]]]])
            out.append(["exists", sig[0], ["forall", sig[1], ["binary", name, ["var", 1], ["var", 0]]]])
        out.append(["unary", name, ["const", "c"]] if sig == ["s"] else
                   ["unary", name, ["const", "k"]] if sig == ["t"] else
                   ["binary", name, ["const", "c"], ["const", "k" if sig[1] == "t" else "c"]])
    return out


@pytest.fixture(scope="module")
def generated():
    from ve import Environment
    from ve.errors import VEError
    rows = []
    for index in range(SETS):
        env, model, depth = generate(index)
        try:
            Environment(env)
        except VEError as exc:
            rows.append((index, env, model, depth, exc))
            continue
        rows.append((index, env, model, depth, None))
    return rows


def _python(env, model, ast):
    from ve import Environment, FiniteModel
    from ve.ast import _to_data, document_from_data
    from ve.background import background
    from ve.evaluate import _evaluate_validated
    from ve.limits import MAX_EVALUATIONS
    e = Environment(env)
    doc = document_from_data(e, ast)
    m = FiniteModel.from_dict(e, model)  # validated, defined tables computed
    return ([_to_data(p.formula) for p in background(e)],
            [_evaluate_validated((f,), m, max_evaluations=MAX_EVALUATIONS).value for f in doc.formulas])


def _run(command, cases):
    completed = subprocess.run(command, input=json.dumps(cases), text=True, capture_output=True,
                               timeout=HANG_TIMEOUT)
    assert completed.returncode in (0, 1), completed.stderr
    results = json.loads(completed.stdout)
    assert len(results) == len(cases)
    return results


@pytest.mark.parametrize("size", [316, 317])
def test_sparse_defined_table_candidate_boundary(size):
    """Candidate pairs may exceed 100,000 while the computed table is empty."""
    from ve import Environment, FiniteModel
    env = {"language": LANGUAGE, "profiles": ["definitions@0", "relational-fol@0"],
           "spec_revision": SPEC_REVISION,
           "vocabulary": {"sorts": {"s": {"description": "items"}}, "constants": {},
                          "predicates": {"d": {"arguments": ["s", "s"], "description": "empty",
                                               "defined": {"arguments": ["s", "s"], "body": ["bottom"]}}}}}
    model = {"complete": True, "domains": {"s": [f"e{i}" for i in range(size)]},
             "constants": {}, "relations": {}}
    assert FiniteModel.from_dict(Environment(env), model).relations["d"] == frozenset()
    ast = [["top"]]
    if LEAN.exists():
        result = _run([str(LEAN), "route", "-"], [
            {"id": "sparse", "kind": "evaluate", "environment": env, "model": model, "ast": ast}])[0]
        assert result.get("values") == [True], result
    rust = Path(os.environ.get("VE_RUST_BINARY", str(ROOT / "rust/target/release/ve")))
    if rust.exists():
        result = _run([str(rust), "conformance"], [
            {"id": "sparse", "environment": env, "model": model, "ast": ast}])[0]
        assert result.get("values") == [True], result


def test_populated_defined_table_limit_boundary():
    """A populated 317² table exceeds the shared 100,000 tuple limit."""
    from ve import Environment, FiniteModel
    from ve.errors import ResourceLimit
    env = {"language": LANGUAGE, "profiles": ["definitions@0", "relational-fol@0"],
           "spec_revision": SPEC_REVISION,
           "vocabulary": {"sorts": {"s": {"description": "items"}}, "constants": {},
                          "predicates": {"d": {"arguments": ["s", "s"], "description": "full",
                                               "defined": {"arguments": ["s", "s"], "body": ["top"]}}}}}
    model = {"complete": True, "domains": {"s": [f"e{i}" for i in range(317)]},
             "constants": {}, "relations": {}}
    with pytest.raises(ResourceLimit):
        FiniteModel.from_dict(Environment(env), model)
    if LEAN.exists():
        result = _run([str(LEAN), "route", "-"], [
            {"id": "full", "kind": "evaluate", "environment": env, "model": model, "ast": [["top"]]}])[0]
        assert result["status"] == "error" and "ResourceLimit" in result["error"], result
    rust = Path(os.environ.get("VE_RUST_BINARY", str(ROOT / "rust/target/release/ve")))
    if rust.exists():
        result = _run([str(rust), "conformance"], [
            {"id": "full", "environment": env, "model": model, "ast": [["top"]]}])[0]
        assert result["status"] == "error" and result["error"]["code"] == "ResourceLimit", result


def test_generated_sets_cover_the_plan(generated):
    accepted = [row for row in generated if row[4] is None]
    assert len(accepted) == SETS
    assert max(row[3] for row in accepted) == 4
    assert sum(row[3] >= 3 for row in accepted) >= 50


def test_python_and_lean_elaborate_identically(generated):
    if not LEAN.exists():
        pytest.skip("lean route runner is not built (lake build)")
    cases, expected = [], []
    for index, env, model, _, _ in generated:
        ast = probes(env)
        background, values = _python(env, model, ast)
        cases.append({"id": f"bg{index}", "kind": "background", "environment": env})
        cases.append({"id": f"ev{index}", "kind": "evaluate", "environment": env, "model": model, "ast": ast})
        expected.append((background, values))
    results = _run([str(LEAN), "route", "-"], cases)
    for (background, values), bg, ev in zip(expected, results[0::2], results[1::2], strict=True):
        assert bg.get("status") == "ok", bg
        assert bg["background"] == background, bg["id"]
        assert ev.get("values") == values, (ev["id"], ev, values)


def test_rust_computes_the_same_tables(generated):
    import os
    if os.environ.get("VE_RUST_PREBUILT"):
        assert Path(os.environ["VE_RUST_BINARY"]).is_file(), "gate Rust build missing"
    else:
        cargo = shutil.which("cargo")
        if not cargo:
            pytest.skip("cargo is not available")
        env_vars = {**os.environ, "CARGO_HOME": str(ROOT / ".cargo-home"), "CARGO_TARGET_DIR": str(ROOT / "rust/target")}
        built = subprocess.run([cargo, "build", "-j", "2", "--locked", "--release", "--manifest-path",
                                str(ROOT / "rust/Cargo.toml")], cwd=ROOT, env=env_vars, capture_output=True,
                               text=True, timeout=HANG_TIMEOUT)
        assert built.returncode == 0, built.stderr
    requests, expected = [], []
    for index, env, model, _, _ in generated:
        ast = probes(env)
        requests.append({"id": f"ev{index}", "environment": env, "model": model, "ast": ast})
        expected.append(_python(env, model, ast)[1])
    results = _run([os.environ.get("VE_RUST_BINARY", str(ROOT / "rust/target/release/ve")),
                    "conformance"], requests)
    for values, result in zip(expected, results, strict=True):
        assert result.get("values") == values, result


def _mutate(env, rng):
    """Swap two same-signature bodies, or replace one body by its negation."""
    env = deepcopy(env)
    defined = [(n, e) for n, e in env["vocabulary"]["predicates"].items() if "defined" in e]
    pairs = [(a, b) for a in defined for b in defined
             if a[0] < b[0] and a[1]["arguments"] == b[1]["arguments"]
             and a[1]["defined"]["body"] != b[1]["defined"]["body"]]
    if pairs:
        (_, a), (_, b) = rng.choice(pairs)
        a["defined"]["body"], b["defined"]["body"] = b["defined"]["body"], a["defined"]["body"]
    else:
        _, a = rng.choice(defined)
        a["defined"]["body"] = ["not", a["defined"]["body"]]
    return env


def test_mutations_change_identity_and_reject_bound_certificates(generated):
    from ve import Environment
    from ve.ast import Top
    from ve.entailment import check_entailment_certificate, prove_entailment
    from ve.errors import VEError
    rng = random.Random(SEED)
    lean_cases = []
    checked = 0
    for index, env, _, _, _ in generated[:200]:
        original = Environment(env)
        certificate = prove_entailment(original, [], Top()).certificate
        mutated_json = _mutate(env, rng)
        try:
            mutated = Environment(mutated_json)
        except VEError:
            continue  # a swap can create a cycle; rejection is also a change
        assert mutated.environment_id != original.environment_id, index
        assert not check_entailment_certificate(mutated, [], Top(), certificate).valid, index
        lean_cases.append({"id": f"m{index}", "kind": "certificate", "environment": mutated_json,
                           "premises": [], "conclusion": ["top"], "certificate": certificate})
        checked += 1
    assert checked >= 150
    if LEAN.exists():
        for result in _run([str(LEAN), "route", "-"], lean_cases):
            assert result.get("valid") is False, result
            assert result.get("error") == "certificate is stale or bound to different inputs", result
