"""Seeded Python search -> independent Lean replay, with all denominators retained.

Run from the repository root. Two cohorts of 320 constructive random queries sample valid inference schemas;
160 further queries are unconditioned random formulas. This
is a development corpus, not an unbiased estimate of real-workload acceptance.
"""
from __future__ import annotations

import argparse
import copy
from collections import Counter
import json
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve.ast import (And, Binary, Bottom, Const, Eq, Exists, Forall, Implies,
                    Not, Or, Top, Unary, Var, document_from_data, formula_to_data)
from ve.argument_fixtures import worked_examples
from ve.entailment import (check_entailment_certificate, prove_entailment,
                           _apply, _derive, _initial_branch, _kind, _binding)
from ve.environment import Environment
from ve.search import check_countermodel

SEED = 20260923


def environment(constants=True, salt=0):
    # Exercise canonical escaping, UTF-8, multiblock SHA and metadata identity.
    description = f"Item {salt}: \b\t\f\n\r\x00 \" \\ café 😀 " + "x" * (salt % 80)
    return Environment.from_dict({
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {"item": {"description": description}, "place": {"description": "Place"}},
            "predicates": {**{p: {"arguments": ["item"], "description": p} for p in ("p", "q", "r")},
                           "rel": {"arguments": ["item", "item"], "description": "Rel"},
                           "visits": {"arguments": ["item", "place"], "description": "Visits"}},
            "constants": ({**{c: {"sort": "item", "description": c} for c in ("a", "b", "c", "d")},
                           "here": {"sort": "place", "description": "Here"}} if constants else {}),
        },
    })


def formula(rng, depth=2, bound=0, constants=True):
    terms = [Var(i) for i in range(bound)] + ([Const(c) for c in ("a", "b", "c")] if constants else [])
    if depth == 0 or rng.random() < .35:
        choices = [Top(), Bottom()]
        if terms:
            t, u = rng.choice(terms), rng.choice(terms)
            choices += [Unary(rng.choice(("p", "q", "r")), t), Eq(t, u), Binary("rel", t, u)]
        return rng.choice(choices)
    op = rng.randrange(6)
    if op == 0:
        return Not(formula(rng, depth-1, bound, constants))
    if op in (1, 2, 3):
        return (And, Or, Implies)[op-1](formula(rng, depth-1, bound, constants),
                                       formula(rng, depth-1, bound, constants))
    return (Forall if op == 4 else Exists)("item", formula(rng, depth-1, bound+1, constants))


def propositional_formula(rng, depth=2):
    if depth == 0:
        return rng.choice((Unary(rng.choice(("p", "q", "r")), Const(rng.choice(("a", "b", "c")))),
                           Eq(Const(rng.choice(("a", "b", "c"))), Const(rng.choice(("a", "b", "c"))))))
    op = rng.choice((Not, And, Or, Implies))
    a = propositional_formula(rng, depth-1)
    return op(a) if op is Not else op(a, propositional_formula(rng, depth-1))


def completeness_regression(constants=1, quantifier_duals=True):
    """Reviewer's existential weakening, with De Morgan applied twice.

    Unused declared constants must not bury the useful witness pair under
    unrelated ground instances. Include quantifier-dual and connective-only forms.
    """
    env = Environment.from_dict({
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {"item": {"description": "Item"}},
            "predicates": {"r": {"arguments": ["item", "item"], "description": "R"}},
            "constants": {f"a{i}": {"sort": "item", "description": "Unused"}
                          for i in range(constants)},
        },
    })
    yy, xx, xy = (Binary("r", Var(i), Var(j)) for i, j in ((0, 0), (1, 1), (1, 0)))
    left = Not(Or(Not(yy), xx))
    premise = Exists("item", Exists("item", And(left, xy)))
    weaker = Exists("item", Exists("item", Or(left, xy)))

    def de_morgan(f):
        if type(f) in (And, Or):
            dual = Or if type(f) is And else And
            return Not(dual(Not(de_morgan(f.left)), Not(de_morgan(f.right))))
        if type(f) is Not:
            return Not(de_morgan(f.body))
        if type(f) in (Forall, Exists):
            if quantifier_duals:
                dual = Exists if type(f) is Forall else Forall
                return Not(dual(f.sort, Not(de_morgan(f.body))))
            return type(f)(f.sort, de_morgan(f.body))
        return f

    return env, [premise], de_morgan(de_morgan(weaker))


def constructive(rng, index, simple=False):
    kind = index % 16
    env = environment(constants=kind not in (7, 8, 11, 12, 14, 15), salt=index)
    make = propositional_formula if simple else formula
    a, b = make(rng), make(rng)
    p, q = rng.sample(("p", "q", "r"), 2)
    c = Const(rng.choice(("a", "b", "c")))
    x = Var(0)
    px, qx = Unary(p, x), Unary(q, x)
    if kind == 0: ps, goal = [a, Implies(a, b)], b
    elif kind == 1: ps, goal = [And(a, b)], rng.choice((a, b))
    elif kind == 2: ps, goal = [a], Or(a, b)
    elif kind == 3: ps, goal = [Or(a, b), Not(a)], b
    elif kind == 4: ps, goal = [Not(Not(a))], a
    elif kind == 5: ps, goal = [], Implies(a, a)
    elif kind == 6: ps, goal = [Forall("item", px)], Unary(p, c)
    elif kind == 7:
        ps, goal = [Exists("item", px), Forall("item", Implies(px, qx))], Exists("item", qx)
    elif kind == 8:
        body = Binary("rel", Var(1), Var(0))
        ps = [Exists("item", Exists("item", body))]
        goal = Exists("item", Exists("item", Binary("rel", Var(0), Var(1))))
    elif kind == 9:
        ps = [Forall("item", Exists("place", Binary("visits", Var(1), Var(0))))]
        goal = Exists("place", Binary("visits", c, Var(0)))
    elif kind == 10:
        names = rng.sample(("a", "b", "c", "d"), 4)
        terms = [Const(n) for n in names]
        ps = [Eq(terms[i], terms[i+1]) for i in range(3)]
        # Fixed predicate/arity on each side, with substitution in both positions.
        ps += [Binary("rel", terms[0], terms[1])]
        goal = Binary("rel", terms[3], terms[2])
    elif kind == 11: ps, goal = [], Forall("item", Eq(x, x))
    elif kind == 12: ps, goal = [], Not(Exists("item", Bottom()))
    elif kind == 13: ps, goal = [a, Not(a)], b
    elif kind == 14:
        ps = [Forall("item", Implies(px, qx))]
        goal = Implies(Exists("item", px), Exists("item", qx))
    else:
        ps = [Not(Forall("item", Not(px)))]
        goal = Exists("item", px)
    return env, ps, goal


def envelope(name, env, premises, conclusion, certificate):
    return {"id": name, "environment": env.to_dict(),
            "premises": [formula_to_data(env, f) for f in premises],
            "conclusion": formula_to_data(env, conclusion), "certificate": certificate}


def replay_python(case):
    env = Environment.from_dict(case["environment"])
    fs = document_from_data(env, case["premises"] + [case["conclusion"]]).formulas
    return check_entailment_certificate(env, fs[:-1], fs[-1], case["certificate"]).valid


def trace_coverage(env, ps, c, trace, counts):
    def visit(branch, node):
        if node["rule"] == "close":
            counts["close"] += 1
            return
        from ve.closure import EXTRA_RULES, derive_extra
        if node['rule'] in EXTRA_RULES:
            counts[node['rule']] += 1
            child = branch.copy()
            child.formulas.extend(derive_extra(branch, node['rule'], node['at'], node.get('parameter')))
            visit(child, node['children'][0])
            return
        i, parameter = node["at"], node.get("parameter")
        item = branch.formulas[i]
        counts[f"{_kind(item)}:{type(item.formula).__name__}:{item.positive}"] += 1
        for added, child in zip(_derive(branch, i, parameter), node["children"], strict=True):
            visit(_apply(branch, i, parameter, added), child)
    visit(_initial_branch(env, tuple(ps), c), trace)


def positive_cases():
    rng = random.Random(SEED)
    cases, coverage, outcomes = [], Counter(), Counter()
    def add(name, env, ps, c, required):
        result = prove_entailment(env, ps, c, max_steps=3000)
        outcomes[name.split("_")[0] + ":" + result.status] += 1
        if required:
            assert result.status == "Found", (name, result.to_dict())
        if result.certificate is not None:
            case = envelope(name, env, ps, c, result.certificate)
            assert replay_python(case), name
            cases.append(case)
            trace_coverage(env, ps, c, result.certificate["trace"], coverage)
        return result
    for i in range(320):
        add(f"broadconstructive_{i:03d}", *constructive(rng, i), False)
    for i in range(320):
        add(f"constructive_{i:03d}", *constructive(rng, i, simple=True), True)
    for i in range(160):
        constants = bool(i % 2)
        env = environment(constants, i+320)
        ps = [formula(rng, 3, constants=constants) for _ in range(rng.randrange(3))]
        c = formula(rng, 3, constants=constants)
        add(f"unconditioned_{i:03d}", env, ps, c, False)
    worked = {}
    for name, graph in worked_examples().items():
        claims = {c.name: c.ast for c in graph.claims}
        edge = graph.deductions[0]
        ps, c = [claims[n] for n in edge.premises], claims[edge.conclusion]
        # Neutral fixture IDs do not encode validity. Retain and independently
        # check the separated-vocabulary counterexample instead of requiring a proof.
        for model in edge.countermodels:
            assert check_countermodel(graph.env, ps, c, model).valid
        result = add(f"worked_{name}", graph.env, ps, c, not edge.countermodels)
        if edge.countermodels:
            assert result.status == "NotFound", (name, result.to_dict())
        worked[name] = ("countermodel checked; search NotFound; forged close rejected"
                        if edge.countermodels else "accepted")
    for constants in (0, 1, 2, 4):
        for duals in (False, True):
            add(f"reviewer_{constants}_{int(duals)}",
                *completeness_regression(constants, duals), True)
    return cases, {"search_outcomes": dict(sorted(outcomes.items())),
                   "worked_examples": worked,
                   "trace_rule_counts": dict(sorted(coverage.items()))}


def forged_cases():
    cases = []
    for i in range(10):
        env = environment(salt=i)
        p, q = Unary("p", Const("a")), Unary("q", Const("b"))
        ps, goal = [And(p, q)], p
        result = prove_entailment(env, ps, goal)
        base = envelope(f"base_{i}", env, ps, goal, result.certificate)
        mutations = {
            "version": lambda c: c["certificate"].update(checker_version="ve-tableau-checker@999"),
            "environment_id": lambda c: c["certificate"].update(environment_id="0"*64),
            "premise_ids": lambda c: c["certificate"].update(premise_meaning_ids=[]),
            "conclusion_id": lambda c: c["certificate"].update(conclusion_meaning_id="f"*64),
            "extra_field": lambda c: c["certificate"].update(code="true"),
            "premature_close": lambda c: c["certificate"].update(trace={"rule": "close"}),
            "bad_index": lambda c: c["certificate"]["trace"].update(at=99999),
            "bool_index": lambda c: c["certificate"]["trace"].update(at=True),
            "missing_branch": lambda c: c["certificate"]["trace"].update(children=[]),
            "extra_branch": lambda c: c["certificate"]["trace"]["children"].append({"rule": "close"}),
            "unknown_rule": lambda c: c["certificate"]["trace"].update(rule="execute"),
            "illegal_parameter": lambda c: c["certificate"]["trace"].update(parameter="w:0"),
            "changed_environment": lambda c: c["environment"]["vocabulary"]["sorts"]["item"].update(description="changed"),
            "changed_conclusion": lambda c: c.update(conclusion=["top"]),
        }
        for name, mutate in mutations.items():
            case = copy.deepcopy(base)
            case["id"] = f"forged_{i}_{name}"
            mutate(case)
            assert not replay_python(case), case["id"]
            cases.append(case)
    # Quantifier-specific forgeries retain valid commitments and mutate only replay.
    env = environment()
    ps, goal = [Forall("item", Unary("p", Var(0)))], Unary("p", Const("a"))
    certificate = prove_entailment(env, ps, goal).certificate
    for token in ("w:0", "w:999", "w:00", "c:missing", "c:here", "a", "c:a:extra"):
        forged = copy.deepcopy(certificate)
        forged["trace"]["parameter"] = token
        cases.append(envelope("forged_gamma_"+token, env, ps, goal, forged))
    env = environment(False)
    ps = [Exists("item", Unary("p", Var(0)))]
    goal = Exists("item", Or(Unary("p", Var(0)), Bottom()))
    certificate = prove_entailment(env, ps, goal).certificate
    assert certificate["trace"]["rule"] == "expand" and certificate["trace"]["at"] == 0
    forged = copy.deepcopy(certificate)
    forged["trace"]["parameter"] = "w:0"
    cases.append(envelope("forged_delta_supplied_witness", env, ps, goal, forged))
    # Empty-sort fallacy: an invented parameter would 'prove' existence from a universal.
    ps, goal = [Forall("item", Unary("p", Var(0)))], Exists("item", Unary("p", Var(0)))
    trace = {"rule": "expand", "at": 0, "parameter": "w:0", "children": [
        {"rule": "expand", "at": 1, "parameter": "w:0", "children": [{"rule": "close"}]}]}
    cases.append(envelope("forged_empty_sort_inhabitation", env, ps, goal,
                          {**_binding(env, tuple(ps), goal), "trace": trace}))
    graph = next(g for g in worked_examples().values() if g.deductions[0].countermodels)
    claims = {c.name: c.ast for c in graph.claims}
    edge = graph.deductions[0]
    ps, goal = [claims[n] for n in edge.premises], claims[edge.conclusion]
    cases.append(envelope("forged_worked_separated", graph.env, ps, goal,
                          {**_binding(graph.env, tuple(ps), goal), "trace": {"rule": "close"}}))
    assert len(cases) >= 100
    for case in cases:
        assert not replay_python(case), case["id"]
    return cases


def invoke(executable, cases):
    # Keep the envelope well below the 16 MiB input cap; retain order and every case.
    results = []
    for start in range(0, len(cases), 40):
        chunk = cases[start:start+40]
        proc = subprocess.run([str(executable), "check-certificate"], input=json.dumps(chunk),
                              text=True, capture_output=True, timeout=120)
        assert proc.returncode in (0, 1), proc.stderr + proc.stdout
        rows = json.loads(proc.stdout)
        assert len(rows) == len(chunk), proc.stdout
        results.extend(rows)
    return results


def run(executable):
    positive, report = positive_cases()
    forged = forged_cases()
    from conformance.closure_certificates import positive_cases as closure_positive, forged_cases as closure_forged
    closure, closure_outcomes = closure_positive()
    closure_attacks = closure_forged(closure)
    closure_coverage = Counter()
    for case in closure:
        env = Environment(case['environment'])
        fs = document_from_data(env, case['premises'] + [case['conclusion']]).formulas
        trace_coverage(env, fs[:-1], fs[-1], case['certificate']['trace'], closure_coverage)
    positive.extend(closure)
    forged.extend(closure_attacks)
    accepted = invoke(executable, positive)
    rejected = invoke(executable, forged)
    gaps = [{"id": c["id"], "result": r} for c, r in zip(positive, accepted, strict=True)
            if r != {"id": c["id"], "status": "ok", "valid": True}]
    false_accepts = [c["id"] for c, r in zip(forged, rejected, strict=True) if r["valid"]]
    report.update(seed=SEED, constructive_random_queries=320, broad_constructive_random_queries=320,
                  unconditioned_random_queries=160, completeness_regression_queries=8,
                  python_accepted=len(positive), lean_accepted=len(positive)-len(gaps),
                  forged=len(forged), lean_rejected_forged=len(forged)-len(false_accepts),
                  python_accepted_lean_rejected=gaps, forged_lean_accepted=false_accepts)
    closure_gaps = [g for g in gaps if g['id'].startswith('closure_')]
    closure_false_accepts = [name for name in false_accepts if name.startswith('closure_')]
    report.update(closure_python_accepted=len(closure), closure_lean_accepted=len(closure)-len(closure_gaps),
                  closure_forged=len(closure_attacks), closure_lean_rejected_forged=len(closure_attacks)-len(closure_false_accepts),
                  closure_reviewer_outcomes=closure_outcomes,
                  closure_trace_rule_counts=dict(sorted(closure_coverage.items())))
    assert not gaps, gaps
    assert not false_accepts, false_accepts
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, default=ROOT / "lean/.lake/build/bin/ve_conformance")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = run(args.executable.resolve())
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.write_text(text)
    print(text, end="")
