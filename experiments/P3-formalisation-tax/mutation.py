"""Mutation adequacy of the differential test.

An all-green differential test means little unless the test would have caught a
wrong formalisation. For every item we apply small syntactic mutations to the
author's VE statement (plausible mistranslations: rtc<->tc, swapped closure
direction, closure -> single edge, and<->or, dropped conjunct/disjunct, dropped
negation, exists<->forall, implication -> consequent) and rerun exactly the same
differential test (item questions + perturbations, same reference answers). A
mutant is KILLED if any answer differs from the reference. Surviving mutants
are either equivalent on the tested worlds or blind spots of the test.

Usage: python mutation.py [items...]   (writes mutation_results.json when run on all)
"""
from __future__ import annotations

import json
import random
import sys

import harness as H
from ve import evaluate, find_distinguishing_model, prove_entailment
from ve.ast import (And, Binary, Document, Exists, Forall, Implies, Named, Not, Or, Reach,
                    check_formula)

MAX_MUTANTS = 25


def children(f):
    if isinstance(f, (And, Or, Implies)):
        return [("left", f.left), ("right", f.right)]
    if isinstance(f, Not):
        return [("body", f.body)]
    if isinstance(f, (Exists, Forall)):
        return [("body", f.body)]
    if isinstance(f, Reach) and not isinstance(f.edge, Named):
        return [("edge", f.edge.formula)]
    return []


def replace(f, path, new):
    if not path:
        return new
    head, rest = path[0], path[1:]
    if head == "edge":
        return Reach(f.kind, type(f.edge)(f.edge.sort, replace(f.edge.formula, rest, new)), f.left, f.right)
    kw = {s: getattr(f, s) for s in f.__slots__}
    kw[head] = replace(kw[head], rest, new)
    return type(f)(**kw)


def local_mutants(f):
    out = []
    if isinstance(f, Reach):
        out.append(("star<->plus", Reach("plus" if f.kind == "star" else "star", f.edge, f.left, f.right)))
        out.append(("swap-direction", Reach(f.kind, f.edge, f.right, f.left)))
        if isinstance(f.edge, Named):
            out.append(("closure->edge", Binary(f.edge.relation, f.left, f.right)))
    if isinstance(f, And):
        out += [("and->or", Or(f.left, f.right)), ("drop-right-conjunct", f.left), ("drop-left-conjunct", f.right)]
    if isinstance(f, Or):
        out += [("or->and", And(f.left, f.right)), ("drop-right-disjunct", f.left), ("drop-left-disjunct", f.right)]
    if isinstance(f, Not):
        out.append(("drop-negation", f.body))
    if isinstance(f, Exists):
        out.append(("exists->forall", Forall(f.sort, f.body)))
    if isinstance(f, Forall):
        out.append(("forall->exists", Exists(f.sort, f.body)))
    if isinstance(f, Implies):
        out.append(("implies->consequent", f.right))
    return out


def all_mutants(f, path=()):
    for name, m in local_mutants(f):
        yield path, name, m
    for slot, c in children(f):
        yield from all_mutants(c, path + (slot,))


def test_cases(item, env, doc, bindings, n):
    """(model, statement index, reference answer) for item questions + perturbations."""
    cases = []
    for q in item["questions"]:
        if isinstance(q.get("target"), dict) and q["target"].get("kind") == "check":
            continue
        w, r = H.question_world(item, q)
        cases.append(("item", H.build_model(env, item["family"], w, r, bindings, item["id"]),
                      q, H.ref_answer(item, q, w, r)))
    for p in H.perturbations(item, n) + H.targeted_perturbations(item):
        q = p["q"] or {}
        cases.append(("perturbed", H.build_model(env, item["family"], p["world"], p["request"], bindings, item["id"]),
                      q, H.ref_answer(item, q, p["world"], p["request"])))
    return cases


def classify_survivor(env, base, m):
    """Use VE itself: prove base <-> mutant (equivalent: the survivor is harmless), or find a
    small finite model where they differ (distinguishable: a blind spot of the test)."""
    try:
        fwd = prove_entailment(env, [base], m, max_steps=1500).status
        bwd = prove_entailment(env, [m], base, max_steps=1500).status if fwd == "Found" else None
        if fwd == "Found" and bwd == "Found":
            return "equivalent"
        d = find_distinguishing_model(env, base, m, max_domain_size=2, max_models=3000)
        if d.status == "Found":
            return "distinguishable"
    except Exception:
        pass
    return "unknown"


def run_item(item_id, n=H.N_PERTURB):
    item = H.load_item(item_id)
    env, doc, bindings = H.load_formalisation(item)
    cases = test_cases(item, env, doc, bindings, n)
    idx = bindings.get("statement_for", {}).get("assert", 0) if item["family"] == "alloy" else 0
    base = doc.formulas[idx]
    muts = []
    for path, name, local in all_mutants(base):
        m = replace(base, path, local)
        try:
            check_formula(env, m)
        except Exception:
            continue
        muts.append((path, name, m))
    rng = random.Random(f"{H.SEED}-mut-{item_id}")
    if len(muts) > MAX_MUTANTS:
        muts = rng.sample(muts, MAX_MUTANTS)
    rows = []
    for path, name, m in muts:
        killed_item = killed_pert = False
        for kind, model, q, ref in cases:
            v = evaluate(env, m, model, trace=False).value
            if v != ref:
                if kind == "item":
                    killed_item = True
                else:
                    killed_pert = True
                if killed_item:
                    break
        row = {"operator": name, "path": ".".join(path), "killed": killed_item or killed_pert,
               "killed_by_item_questions": killed_item}
        if not row["killed"]:
            row["survivor_class"] = classify_survivor(env, base, m)
        rows.append(row)
    surv = [r for r in rows if not r["killed"]]
    return {"item": item_id, "family": item["family"], "mutants": len(rows),
            "survivors_equivalent": sum(r["survivor_class"] == "equivalent" for r in surv),
            "survivors_distinguishable": sum(r["survivor_class"] == "distinguishable" for r in surv),
            "survivors_unknown": sum(r["survivor_class"] == "unknown" for r in surv),
            "killed": sum(r["killed"] for r in rows),
            "killed_by_item_questions_alone": sum(r["killed_by_item_questions"] for r in rows),
            "rows": rows}


if __name__ == "__main__":
    ids = sys.argv[1:] or sorted(p.name for p in H.ITEMS.iterdir() if p.is_dir())
    out = []
    for i in ids:
        r = run_item(i)
        out.append(r)
        print(f'{i:32s} mutants={r["mutants"]:3d} killed={r["killed"]:3d} by_item_q_only={r["killed_by_item_questions_alone"]:3d} '
              f'surv: equiv={r["survivors_equivalent"]} disting={r["survivors_distinguishable"]} unknown={r["survivors_unknown"]}',
              flush=True)
    if not sys.argv[1:]:
        (H.HERE / "mutation_results.json").write_text(json.dumps(out, indent=1) + "\n")
