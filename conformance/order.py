"""order@0 differential conformance: Python search and replay vs the Lean checker.

Run from the repository root (after `cd lean && lake build`):
    uv run python -m conformance.order
Writes conformance/order-report.json. Every generated certificate is replayed by
the Python checker (ve.order) and by the Lean checker (`ve_conformance order`),
whose soundness theorem is VE.Order.Tableau.checkCertificate_sound; verdicts must
be identical. Forged certificates must be rejected by both. Python evaluation and
countermodel search are compared with the Lean evaluator and the proved
`checkCountermodel` gate. This is a development corpus, not an estimate of real
workload coverage.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from collections import Counter
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve import evaluate, FiniteModel
from ve.ast import (Add, And, Binary, Bottom, Const, Document, Eq, Exists, Forall, Implies, Le, Lt,
                    Not, Num, Or, Scale, Top, Unary, Var, document_from_data, formula_to_data)
from ve.entailment import check_entailment_certificate, prove_entailment, _binding
from ve.environment import Environment
from ve.search import check_countermodel, find_countermodel

SEED = 20260922
INT = "$int"
INTS = ("n", "m", "k")


def environment(salt=0):
    return Environment.from_dict({
        "language": "ve.core@0.1", "profiles": ["order@0", "relational-fol@0"],
        "spec_revision": "ve-v0.1-order-2026-09-22",
        "vocabulary": {
            "sorts": {"item": {"description": f"Item {salt}: café \" \\ 😀"}},
            "predicates": {
                "p": {"arguments": ["item"], "description": "P"},
                "marked": {"arguments": [INT], "description": "Marked number"},
                "value": {"arguments": ["item", INT], "description": "Item value"},
                "bounded": {"arguments": [INT, INT], "description": "Bounded pair"},
            },
            "constants": {**{c: {"sort": INT, "description": c.upper()} for c in INTS},
                          "a": {"sort": "item", "description": "A"},
                          "b": {"sort": "item", "description": "B"}},
        },
    })


# ------------------------------------------------------------------ terms

def term(rng, depth=2):
    if depth == 0 or rng.random() < 0.35:
        return Const(rng.choice(INTS)) if rng.random() < 0.6 else Num(rng.randint(-6, 6))
    op = rng.randrange(4)
    if op == 0:
        return Add(term(rng, depth - 1), term(rng, depth - 1))
    if op == 1:
        return Scale(rng.choice((-3, -2, -1, 2, 3)), term(rng, depth - 1))
    if op == 2:
        return Add(term(rng, depth - 1), Scale(-1, term(rng, depth - 1)))  # t - u
    return Scale(-1, term(rng, depth - 1))


def rewrite(rng, t):
    """A semantics-preserving, syntax-changing term rewrite (never trusted)."""
    choice = rng.randrange(6)
    if choice == 0:
        return Add(t, Num(0))
    if choice == 1 and type(t) is Add:
        return Add(t.right, t.left)
    if choice == 2:
        return Scale(-1, Scale(-1, t))
    if choice == 3 and type(t) is Num:
        return Add(Num(t.value - 1), Num(1))
    if choice == 4 and type(t) is Scale and t.coefficient > 1:
        return Add(Scale(t.coefficient - 1, t.term), t.term)
    return Add(Num(0), t)


def rewrite_formula(rng, f, bound=0):
    kind = type(f)
    if kind in (Le, Lt, Eq) and not (kind is Eq and type(f.left) is Var):
        return kind(rewrite(rng, f.left), rewrite(rng, f.right))
    if kind is Unary and f.predicate == "marked":
        return Unary(f.predicate, rewrite(rng, f.term))
    if kind is Binary:
        right = f.right if type(f.right) is Var else rewrite(rng, f.right)
        left = f.left if type(f.left) is Var or f.predicate == "value" else rewrite(rng, f.left)
        return Binary(f.predicate, left, right)
    if kind is Not:
        return Not(rewrite_formula(rng, f.body, bound))
    if kind in (And, Or, Implies):
        return kind(rewrite_formula(rng, f.left, bound), rewrite_formula(rng, f.right, bound))
    if kind in (Forall, Exists):
        return kind(f.sort, rewrite_formula(rng, f.body, bound + 1))
    return f


def atom(rng, bound=0):
    items = [Var(i) for i in range(bound)] + [Const("a"), Const("b")]
    choice = rng.randrange(8)
    if choice in (0, 1):
        return Le(term(rng), term(rng))
    if choice == 2:
        return Lt(term(rng), term(rng))
    if choice == 3:
        return Eq(term(rng), term(rng))
    if choice == 4:
        return Unary("marked", term(rng))
    if choice == 5:
        return Binary("value", rng.choice(items), term(rng))
    if choice == 6:
        return Unary("p", rng.choice(items))
    return Binary("bounded", term(rng, 1), term(rng, 1))


def formula(rng, depth=2, bound=0, quantifiers=True):
    if depth == 0 or rng.random() < 0.3:
        return atom(rng, bound)
    op = rng.randrange(6 if quantifiers else 4)
    if op == 0:
        return Not(formula(rng, depth - 1, bound, quantifiers))
    if op in (1, 2, 3):
        return (And, Or, Implies)[op - 1](formula(rng, depth - 1, bound, quantifiers),
                                           formula(rng, depth - 1, bound, quantifiers))
    return (Forall if op == 4 else Exists)("item", formula(rng, depth - 1, bound + 1, quantifiers))


def linear_sum(ts):
    total = ts[0]
    for t in ts[1:]:
        total = Add(total, t)
    return total


# ----------------------------------------------------------- generators

def gen_farkas(rng):
    """Premises t_i <= u_i (some strict); conclusion: their sum, rewritten, with slack."""
    count = rng.randint(1, 4)
    left, right, premises, strict = [], [], [], 0
    for _ in range(count):
        t, u = term(rng, 1), term(rng, 1)
        if rng.random() < 0.4:
            premises.append(Lt(t, u)); strict += 1
        else:
            premises.append(Le(t, u))
        left.append(t); right.append(u)
    slack = rng.randint(0, 3)
    total_left, total_right = linear_sum(left), Add(linear_sum(right), Num(slack))
    if strict and rng.random() < 0.5 and slack == 0:
        goal = Lt(rewrite(rng, total_left), rewrite(rng, total_right))
    else:
        goal = Le(rewrite(rng, total_left), rewrite(rng, total_right))
    rng.shuffle(premises)
    return premises, goal


def gen_rewrite(rng):
    f = formula(rng, rng.randint(0, 3), quantifiers=rng.random() < 0.5)
    return [f], rewrite_formula(rng, f)


def gen_integer(rng):
    a, b = rng.choice(((2, 2), (2, 4), (3, 3), (3, 6), (4, 2), (6, 9))), None
    g = __import__("math").gcd(*a)
    r = rng.choice([x for x in range(1, g)]) if g > 1 else None
    x, y = Const(rng.choice(INTS)), Const(rng.choice(INTS))
    shape = rng.randrange(4)
    if shape == 0 and r is not None:
        # a0 x = a1 y + r has no integer solution when gcd(a0, a1) does not divide r.
        return [Eq(Scale(a[0], x), Add(Scale(a[1], y), Num(r + g * rng.randint(-2, 2))))], Bottom()
    if shape == 1:
        # x < y < x + 2 forces y = x + 1 over the integers only.
        return [Lt(x, y), Lt(y, Add(x, Num(2)))], Eq(y, Add(Num(1), x))
    if shape == 2:
        # 3x = 2y implies x != 1 (and x != -1).
        k = rng.choice((1, -1, 3))
        return [Eq(Scale(3, x), Scale(2, y))], Not(Eq(x, Num(k)))
    # 2x <= 2y + 1 and 2y <= 2x + 1 imply x = y.
    return [Le(Scale(2, x), Add(Scale(2, y), Num(1))), Le(Scale(2, y), Add(Scale(2, x), Num(1)))], Eq(x, y)


def gen_congruence(rng):
    t = term(rng)
    kind = rng.randrange(3)
    if kind == 0:
        return [Unary("marked", t)], Unary("marked", rewrite(rng, rewrite(rng, t)))
    if kind == 1:
        item = Const(rng.choice(("a", "b")))
        return [Binary("value", item, t)], Binary("value", item, rewrite(rng, t))
    u = term(rng, 1)
    return [Binary("bounded", t, u)], Binary("bounded", rewrite(rng, t), rewrite(rng, u))


def gen_quantified(rng):
    t = term(rng)
    item = Const(rng.choice(("a", "b")))
    shape = rng.randrange(3)
    if shape == 0:
        premise = Forall("item", Implies(Unary("p", Var(0)), Binary("value", Var(0), t)))
        return [premise, Unary("p", item)], Binary("value", item, rewrite(rng, t))
    if shape == 1:
        premise = Exists("item", And(Unary("p", Var(0)), Le(t, Num(3))))
        return [premise], Le(rewrite(rng, t), Num(rng.randint(3, 5)))
    premise = Forall("item", Binary("value", Var(0), t))
    return [premise], Forall("item", Binary("value", Var(0), rewrite(rng, t)))


def gen_random(rng):
    ps = [formula(rng, 2, quantifiers=rng.random() < 0.3) for _ in range(rng.randint(0, 3))]
    return ps, formula(rng, 2, quantifiers=rng.random() < 0.3)


GENERATORS = {"farkas": (gen_farkas, 170), "rewrite": (gen_rewrite, 140), "integer": (gen_integer, 80),
              "congruence": (gen_congruence, 80), "quantified": (gen_quantified, 60),
              "random": (gen_random, 160)}


def envelope(name, env, premises, conclusion, certificate, kind="certificate"):
    return {"id": name, "kind": kind, "environment": env.to_dict(),
            "premises": [formula_to_data(env, f) for f in premises],
            "conclusion": formula_to_data(env, conclusion), "certificate": certificate}


def replay_python(case):
    try:
        env = Environment.from_dict(case["environment"])
        fs = document_from_data(env, case["premises"] + [case["conclusion"]]).formulas
    except Exception:
        return False
    return check_entailment_certificate(env, fs[:-1], fs[-1], case["certificate"]).valid


def rule_counts(trace, counts):
    counts[trace["rule"]] += 1
    if trace["rule"] == "order-farkas@1" and trace["cuts"]:
        counts["gcd-cut"] += len(trace["cuts"])
    for child in trace.get("children", ()):
        rule_counts(child, counts)


def positive_cases(scale=1.0):
    rng = random.Random(SEED)
    cases, outcomes, counts, refuted = [], Counter(), Counter(), []
    index = 0
    for name, (generate, count) in GENERATORS.items():
        for i in range(int(count * scale)):
            env = environment(index % 7)
            index += 1
            premises, goal = generate(rng)
            result = prove_entailment(env, premises, goal, max_steps=4000)
            outcomes[f"{name}:{result.status}"] += 1
            if result.certificate is not None:
                case = envelope(f"{name}_{i:03d}", env, premises, goal, result.certificate)
                assert replay_python(case), case["id"]
                rule_counts(result.certificate["trace"], counts)
                cases.append(case)
            elif name == "random":
                found = find_countermodel(env, premises, goal, max_domain_size=1, max_models=3000)
                outcomes[f"random:countermodel:{found.status}"] += 1
                if found.model is not None:
                    refuted.append({"id": f"countermodel_{i:03d}", "kind": "countermodel",
                                    "environment": env.to_dict(),
                                    "premises": [formula_to_data(env, f) for f in premises],
                                    "conclusion": formula_to_data(env, goal),
                                    "model": found.model.to_dict()})
    return cases, refuted, dict(sorted(outcomes.items())), dict(sorted(counts.items()))


def _first(trace, rule):
    if trace["rule"] == rule:
        return trace
    for child in trace.get("children", ()):
        found = _first(child, rule)
        if found is not None:
            return found
    return None


def forged_cases(positive):
    """Mutations of accepted certificates and hand-built hazards. All must be rejected."""
    forged = []
    mutations = {
        "version": lambda c: c["certificate"].update(checker_version="ve-tableau-checker@2"),
        "environment_id": lambda c: c["certificate"].update(environment_id="0" * 64),
        "premise_ids": lambda c: c["certificate"].update(premise_meaning_ids=["0" * 64] * 7),
        "conclusion_id": lambda c: c["certificate"].update(conclusion_meaning_id="f" * 64),
        "extra_field": lambda c: c["certificate"].update(code="true"),
        "unknown_rule": lambda c: c["certificate"]["trace"].update(rule="order-omega@1"),
        "changed_conclusion": lambda c: c.update(conclusion=["top"] if c["conclusion"] == ["bottom"] else ["bottom"]),
    }
    for index, base in enumerate(positive[::6]):
        for name, mutate in mutations.items():
            case = copy.deepcopy(base)
            case["id"] = f"forged_{index}_{name}"
            mutate(case)
            forged.append(case)
    farkas_mutations = {
        "negative_inequality_multiplier": lambda n: [p.__setitem__(1, "-" + p[1]) for p in n["literals"][:1]
                                                     if not p[1].startswith("-")],
        "drop_literal": lambda n: n["literals"].pop(),
        "out_of_range": lambda n: n["literals"].append([9999, "1"]),
        "non_canonical": lambda n: n["literals"].append([0, "01"]),
        "zero_all": lambda n: n.update(literals=[[i, "0"] for i, _ in n["literals"]]),
        "drop_cuts": lambda n: n.update(cuts=[]),
        "bad_divisor": lambda n: [c.update(divisor="0") for c in n["cuts"]],
        "shifted_index": lambda n: n.update(literals=[[i + 1, k] for i, k in n["literals"]]),
    }
    for index, base in enumerate(positive):
        node = _first(base["certificate"]["trace"], "order-farkas@1")
        if node is None:
            continue
        for name, mutate in farkas_mutations.items():
            if name in ("drop_cuts", "bad_divisor") and not node["cuts"]:
                continue
            if name == "drop_literal" and not node["literals"]:
                continue
            case = copy.deepcopy(base)
            case["id"] = f"forged_farkas_{index}_{name}"
            mutate(_first(case["certificate"]["trace"], "order-farkas@1"))
            if case["certificate"] != base["certificate"]:
                forged.append(case)
    for index, base in enumerate(positive):
        node = _first(base["certificate"]["trace"], "order-split@1")
        if node is not None:
            for name, formula in (("object_split", ["le", ["const", "a"], ["const", "n"]]),
                                  ("predicate_split", ["unary", "marked", ["const", "n"]])):
                case = copy.deepcopy(base)
                case["id"] = f"forged_split_{index}_{name}"
                _first(case["certificate"]["trace"], "order-split@1")["formula"] = formula
                forged.append(case)
            case = copy.deepcopy(base)
            case["id"] = f"forged_split_{index}_premature_close"
            split = _first(case["certificate"]["trace"], "order-split@1")
            split.clear(); split["rule"] = "close"
            forged.append(case)
        node = _first(base["certificate"]["trace"], "order-neq@1")
        if node is not None:
            case = copy.deepcopy(base)
            case["id"] = f"forged_neq_{index}_index"
            _first(case["certificate"]["trace"], "order-neq@1")["at"] = 0
            forged.append(case)
            case = copy.deepcopy(base)
            case["id"] = f"forged_neq_{index}_one_child"
            _first(case["certificate"]["trace"], "order-neq@1")["children"].pop()
            forged.append(case)
    # Hazards named in the plan, each with an otherwise well-bound certificate.
    env = environment()
    n, m, one = Const("n"), Const("m"), Num(1)
    hazards = [
        ("marked_commuted_bare_close", [Unary("marked", Add(n, one))], Unary("marked", Add(one, n)),
         {"rule": "close"}),
        ("two_n_equals_one_no_cuts", [Eq(Scale(2, n), one)], Bottom(),
         {"rule": "order-farkas@1", "cuts": [], "literals": [[0, "1"], [0, "-1"]], "final_cuts": []}),
        ("two_n_equals_one_divisor_three", [Eq(Scale(2, n), one)], Bottom(),
         {"rule": "order-farkas@1", "cuts": [{"literals": [[0, "1"]], "cuts": [], "divisor": "3"},
                                             {"literals": [[0, "-1"]], "cuts": [], "divisor": "3"}],
          "literals": [], "final_cuts": [[0, "1"], [1, "1"]]}),
        ("neq_needs_split", [Le(n, m), Le(m, Add(n, Num(0)))], Eq(n, m), {"rule": "close"}),
        ("farkas_on_negated_equality", [Le(n, m), Le(m, n)], Not(Not(Eq(n, m))),
         {"rule": "expand", "at": 2, "children": [{"rule": "order-farkas@1", "cuts": [],
                                                   "literals": [[3, "1"]], "final_cuts": []}]}),
        ("nonnegative_constant", [Le(n, m)], Lt(n, m),
         {"rule": "order-farkas@1", "cuts": [], "literals": [[0, "1"], [1, "1"]], "final_cuts": []}),
        ("negative_cut_multiplier", [Eq(Scale(2, n), one)], Bottom(),
         {"rule": "order-farkas@1", "cuts": [{"literals": [[0, "1"]], "cuts": [], "divisor": "2"},
                                             {"literals": [[0, "-1"]], "cuts": [], "divisor": "2"}],
          "literals": [], "final_cuts": [[0, "-1"], [1, "1"]]}),
        ("future_cut_reference", [Eq(Scale(2, n), one)], Bottom(),
         {"rule": "order-farkas@1", "cuts": [{"literals": [], "cuts": [[1, "1"]], "divisor": "2"},
                                             {"literals": [[0, "-1"]], "cuts": [], "divisor": "2"}],
          "literals": [], "final_cuts": [[0, "1"], [1, "1"]]}),
    ]
    for name, ps, goal, trace in hazards:
        forged.append(envelope("hazard_" + name, env, ps, goal,
                               {**_binding(env, tuple(ps), goal), "trace": trace}))
    # closure@0 x order@0 stays rejected: the combined envelope never decodes.
    base = copy.deepcopy(positive[0])
    base["id"] = "combined_closure_order_profiles"
    base["environment"]["profiles"] = ["closure@0", "order@0", "relational-fol@0"]
    forged.append(base)
    for case in forged:
        # Certificate mutations are usually, not always, invalid (e.g. a shifted
        # index can hit an equivalent literal); their verdicts are compared with
        # Lean either way. Binding mutations and named hazards must be rejected.
        case["python_valid"] = replay_python(case)
        if not case["id"].startswith("forged_farkas_"):
            assert not case["python_valid"], case["id"]
    return forged


def evaluation_cases(count=200):
    rng = random.Random(SEED + 1)
    cases = []
    for i in range(count):
        env = environment(i % 5)
        size = rng.randint(0, 3)
        domain = [f"i{j}" for j in range(size)]
        ints = {c: str(rng.randint(-4, 4)) for c in INTS}
        values = [str(v) for v in range(-6, 7)]
        model = {"complete": True, "domains": {"item": domain},
                 "constants": {**ints, "a": domain[0] if domain else None,
                               "b": domain[-1] if domain else None},
                 "relations": {
                     "p": [[x] for x in domain if rng.random() < 0.5],
                     "marked": [[v] for v in values if rng.random() < 0.3],
                     "value": [[x, v] for x in domain for v in values if rng.random() < 0.15],
                     "bounded": [[v, w] for v in values[3:10] for w in values[3:10] if rng.random() < 0.2]}}
        if not domain:
            # Item constants need an inhabitant; use a one-element domain.
            model["domains"]["item"] = ["i0"]
            model["constants"].update(a="i0", b="i0")
        formulas = [formula(rng, rng.randint(0, 3)) for _ in range(rng.randint(1, 4))]
        model_obj = FiniteModel.from_dict(env, model)
        document = Document(tuple(formulas))
        values_py = [evaluate(env, f, model_obj, trace=False).value for f in formulas]
        cases.append(({"id": f"evaluate_{i:03d}", "kind": "evaluate", "environment": env.to_dict(),
                       "model": model_obj.to_dict(),
                       "ast": [formula_to_data(env, f) for f in document.formulas]}, values_py))
    return cases


def invoke(executable, cases):
    results = []
    for start in range(0, len(cases), 40):
        chunk = cases[start:start + 40]
        proc = subprocess.run([str(executable), "order"], input=json.dumps(chunk),
                              text=True, capture_output=True,
                              timeout=int(os.environ.get("VE_CONFORMANCE_HANG_TIMEOUT", "120")))
        assert proc.returncode in (0, 1), proc.stderr + proc.stdout
        rows = json.loads(proc.stdout)
        assert len(rows) == len(chunk), proc.stdout
        results.extend(rows)
    return results


def run(executable, scale=1.0, evaluations=200):
    positive, refuted, outcomes, counts = positive_cases(scale)
    forged = forged_cases(positive)
    accepted = invoke(executable, positive)
    rejected = invoke(executable, forged)
    disagreements = [row["id"] for row in accepted if not row.get("valid")]
    disagreements += [case["id"] for case, row in zip(forged, rejected, strict=True)
                      if bool(row.get("valid")) != case["python_valid"]]
    refutes = invoke(executable, refuted) if refuted else []
    for case in refuted:
        env = Environment.from_dict(case["environment"])
        fs = document_from_data(env, case["premises"] + [case["conclusion"]]).formulas
        assert check_countermodel(env, fs[:-1], fs[-1], FiniteModel.from_dict(env, case["model"])).valid
    disagreements += [row["id"] for row in refutes if not row.get("refutes")]
    evaluated = evaluation_cases(evaluations)
    lean_values = invoke(executable, [case for case, _ in evaluated])
    for (case, values), row in zip(evaluated, lean_values, strict=True):
        if row.get("values") != values:
            disagreements.append(case["id"])
    return {
        "seed": SEED,
        "certificates_replayed": len(positive),
        "python_accepted": len(positive),
        "lean_accepted": sum(bool(r.get("valid")) for r in accepted),
        "forged_replayed": len(forged),
        "python_rejected": sum(not case["python_valid"] for case in forged),
        "lean_rejected": sum(not r.get("valid") for r in rejected),
        "countermodels_checked": len(refuted),
        "lean_refutes": sum(bool(r.get("refutes")) for r in refutes),
        "evaluation_cases": len(evaluated),
        "evaluation_agreements": len(evaluated) - sum(1 for d in disagreements if d.startswith("evaluate_")),
        "disagreements": disagreements,
        "search_outcomes": outcomes,
        "trace_rule_counts": counts,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, default=ROOT / "lean/.lake/build/bin/ve_conformance")
    parser.add_argument("--output", type=Path, default=ROOT / "conformance/order-report.json")
    args = parser.parse_args()
    report = run(args.executable.resolve())
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("search_outcomes", "trace_rule_counts")},
                     indent=2))
    if report["disagreements"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
