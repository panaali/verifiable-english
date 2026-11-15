"""translim-predicates PART 1d: carry part of a keyed document's regulated predicates in a second frame.

Run on a COPY of usecases/anthropic-rsp placed at <tree>/usecases/anthropic-rsp, where <tree> mirrors the checkout
(every other top-level entry a symlink), never on the checkout's own case:

    uv run python docs/translim/translim-predicates/rsp_split.py <copy>/usecases/anthropic-rsp [--size 3] [--leak]

The recipe (REPORT.md section 1d):
1. Link two regulated predicates when a rule on one names the other in its guard or carve-outs, when one is the
   other's permission dual, when their rules stand in a precedence (`over`) pair, or when their rules are checked
   together (a conflict cluster or pair). The connected components are the units a split may move.
2. Frame A keeps the frame (every unregulated predicate) and the regulated predicates left; frame B is the same
   frame and the moved components. Each frame is one environment the soft-norms route accepts (<= 64 regulated).
3. Every document is built per frame from the rules on that frame's predicates; a question about predicate p is
   asked of p's frame. A conflict pair is asked of the frame holding both rules.
`closed_split` refuses a split that breaks step 1 (a rule whose guard reads a predicate of the other frame); `--leak`
skips that refusal and moves a predicate without its guard predicate (seeded bug (c)), so `--check` must fail.
Then the case's own `run.py --check` is run: results.json must be unchanged.
"""
from __future__ import annotations

import argparse
import copy
import importlib
import json
import sys
from functools import lru_cache
from pathlib import Path


def mentioned(formula):
    """Every predicate name an AST names (unary, binary and n-ary atoms)."""
    out = set()
    if isinstance(formula, list):
        if formula and formula[0] in ("unary", "binary", "atom", "nary") and len(formula) > 1 \
                and isinstance(formula[1], str):
            out.add(formula[1])
        for part in formula[1:]:
            out |= mentioned(part)
    return out


def links(rules, regulated, together=()):
    """Step 1's edges, as pairs of regulated predicates. `rules` are norm dicts; `regulated` maps a regulated
    predicate to its `regulated` field; `together` are groups of rule names checked in one document."""
    by_name = {r["name"]: r["predicate"] for r in rules}
    edges = set()
    for r in rules:
        for q in mentioned(r.get("guard")) | {p for u in r.get("unless", []) for p in mentioned(u)}:
            if q in regulated:
                edges.add((r["predicate"], q))
        for over in r.get("over", []):
            if over in by_name:
                edges.add((r["predicate"], by_name[over]))
    for p, field in regulated.items():
        if field.get("permission"):
            edges.add((p, field["permission"]))
    for group in together:
        preds = [by_name[n] for n in group if n in by_name]
        edges |= {(a, b) for a, b in zip(preds, preds[1:])}
    return edges


def components(nodes, edges):
    parent = {n: n for n in nodes}

    def find(n):
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n
    for a, b in edges:
        parent[find(a)] = find(b)
    groups = {}
    for n in nodes:
        groups.setdefault(find(n), set()).add(n)
    return sorted((sorted(g) for g in groups.values()), key=lambda g: (len(g), g))


def closed_split(moved, rules, regulated, together=()):
    """None when no edge of step 1 crosses the two frames; else the first crossing edge's text."""
    for a, b in sorted(links(rules, regulated, together)):
        if (a in moved) != (b in moved):
            return f"the split separates {a} from {b}"
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", type=Path)
    parser.add_argument("--size", type=int, default=3, help="move components until at least this many predicates")
    parser.add_argument("--leak", action="store_true", help="seeded bug (c): move a predicate without its guard")
    args = parser.parse_args()
    here = args.case.resolve()
    if here == (Path(__file__).resolve().parents[3] / "usecases/anthropic-rsp").resolve():
        raise SystemExit("run on a copy, never on the checkout's own case")
    sys.path.insert(0, str(here))
    run = importlib.import_module("run")
    T, V = run.T, run.V
    rules = [json.loads(T.parsed_rule(b.id)) for b in T.rule_blocks()]
    for r in rules:
        r["over"] = list(T.PRECEDENCE.get(r["name"], ()))
    regulated = {p: e["regulated"] for p, e in V.REGULATED.items()}
    together = [tuple(m) for m in run.CLUSTERS.values()] + [tuple(p) for p in run.opposite_sign_pairs()]
    comps = components(sorted(regulated), links(rules, regulated, together))
    keep = {run.G1_ACT, "plans_in_place"}  # the gap probe's own vocabulary stays in frame A
    moved = set()
    if args.leak:
        # a rule whose guard reads another regulated predicate: move the rule's predicate, keep its guard's
        rule = next(r for r in rules if mentioned(r["guard"]) & set(regulated) - {r["predicate"]})
        comp = next(c for c in comps if rule["predicate"] in c)
        guard = sorted(mentioned(rule["guard"]) & set(regulated) - {rule["predicate"]})
        moved = set(comp) - set(guard)
        print("leak: moved", sorted(moved), "without", guard, "(guard of", rule["name"] + ")")
    else:
        for comp in comps:
            if len(moved) >= args.size:
                break
            if not set(comp) & keep:
                moved |= set(comp)
        problem = closed_split(moved, rules, regulated, together)
        if problem:
            raise SystemExit(problem)
    frame_a = sorted(set(regulated) - moved)
    print(f"components {len(comps)} (sizes {[len(c) for c in comps]}); frame A {len(frame_a)} regulated, "
          f"frame B {len(moved)}: {sorted(moved)}")

    full = V.environment

    class Lookup(dict):
        """Frame A's predicates; a predicate of frame B is still found by name (its arguments)."""
        def __missing__(self, key):
            return full()["vocabulary"]["predicates"][key]

    def frame_env(names, default="deny"):
        current = V.environment
        V.environment = full  # the case's own vocabulary (a mutant's extra slot included), then cut to the frame
        try:
            raw = run.vocabulary(default)
        finally:
            V.environment = current
        preds = raw["vocabulary"]["predicates"]
        raw["vocabulary"]["predicates"] = Lookup({p: e for p, e in preds.items()
                                                  if "regulated" not in e or p in names})
        return raw

    V.environment = lambda default="deny": frame_env(frame_a, default)
    frames = {"A": frame_a, "B": sorted(moved)}

    class Routed:
        """One SoftNormDocument per frame; `pick` gives the document of a predicate's frame."""
        def __init__(self, docs, owner):
            self.docs, self.owner = docs, owner

        def pick(self, predicate):
            return self.docs[self.owner(predicate)]

    plain_document = run.document

    @lru_cache(maxsize=None)
    def document(names, default, include=None):
        # the rule list as the case selects it (its own `document`, in the one frame of today's <= 64)
        V.environment = full
        try:
            base = plain_document.__wrapped__(names, default, include)
        finally:
            V.environment = lambda d="deny": frame_env(frame_a, d)
        docs = {}
        for frame, members in frames.items():
            env = frame_env(members, default)
            env["vocabulary"]["predicates"] = dict(env["vocabulary"]["predicates"])
            mine = [{"norm": r.to_dict()["norm"]} for r in base.rules if r.core.predicate in members]
            if mine or frame == "A":
                docs[frame] = run.SoftNormDocument(run.SoftEnvironment(env), mine)
        if include is not None:
            [frame] = {("B" if r.core.predicate in moved else "A") for r in base.rules} or {"A"}
            return docs[frame]
        return Routed(docs, lambda p: "B" if p in moved else "A")

    document.__wrapped__ = plain_document.__wrapped__
    run.document = document
    plain_env, plain_doc = run.SoftEnvironment, run.SoftNormDocument

    def soft_environment(raw):
        raw = copy.deepcopy(raw)
        raw["vocabulary"]["predicates"] = dict(raw["vocabulary"]["predicates"])
        return plain_env(raw)

    def soft_document(env, rules):
        """A document built in a frame carries the rules on that frame's predicates (the gap probe's, m3's)."""
        names = set(env.predicates)
        return plain_doc(env, [r for r in rules if r["norm"]["predicate"] in names])
    run.SoftEnvironment, run.SoftNormDocument = soft_environment, soft_document
    plain_selected, plain_completed, plain_model, plain_premises = run.selected, run.completed, run.model, \
        run.check_premises
    run.selected = lambda doc, case, p, *a, **k: plain_selected(
        doc.pick(p) if isinstance(doc, Routed) else doc, case, p, *a, **k)
    run.completed = lambda doc, case, p, *a, **k: plain_completed(
        doc.pick(p) if isinstance(doc, Routed) else doc, case, p, *a, **k)
    run.model = lambda doc, case: plain_model(doc.docs["A"] if isinstance(doc, Routed) else doc, case)
    run.check_premises = lambda doc, case, choice: plain_premises(
        doc.docs["A"] if isinstance(doc, Routed) else doc, case, choice)
    run.main(["--check"])


if __name__ == "__main__":
    main()
