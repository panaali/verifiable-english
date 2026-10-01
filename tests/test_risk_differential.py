"""risk.md 8.3: Lean's `possibleE`/`certainE`/`witnessE` against brute force, and Rust against both.

10,000 random small separable, unit-coefficient conditions (multi-quantity
terms through `add` and `scale`, quantities on both sides, points shared
between atoms, non-±1 coefficients in `<` and `≤` atoms, cancelling terms)
are decided by Lean (`ve_risk_eval`, the trusted functions on raw
conditions), by Rust's untrusted evaluator and by enumeration of the box in
Python. Non-separable and non-unit conditions are rejected by Lean and Rust
with the same diagnostic. Review B8 / Fable C1.
"""
from __future__ import annotations

import itertools
import json
import random
import subprocess
from pathlib import Path

import pytest

from conformance.risk import cell_env

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_risk_eval"
RUST = ROOT / "rust/target/release/ve"

pytestmark = pytest.mark.skipif(not (LEAN.exists() and RUST.exists()),
                                reason="ve_risk_eval or the Rust binary is not built")

D = "dimensionless"
SHARDS = 4
BOXES_PER_SHARD = 50
CONDITIONS_PER_BOX = 50


def qn(name):
    return ["quantity", name]


def lit(n):
    return ["decimal", D, str(n)]


def scaled(c, term):
    return term if c == 1 else ["scale", D, str(c), term]


def add(a, b):
    return ["add", D, a, b]


def term_of(rng, parts, constant):
    """A term Σ c·q + k from (name, coefficient) parts, in a random add/scale shape."""
    terms = [scaled(c, qn(name)) for name, c in parts]
    if constant or not terms:
        terms.append(lit(constant))
    rng.shuffle(terms)
    out = terms[0]
    for t in terms[1:]:
        out = add(out, t) if rng.randrange(2) else add(t, out)
    return out


def atom(rng, free, points):
    """One comparison over `free` (non-point, used by this atom only) and any points."""
    op = rng.choice(("lt", "le", "eq"))
    parts = []
    for name in free:
        c = rng.choice((1, -1)) if op == "eq" else rng.choice((1, -1, 2, -2, 3))
        parts.append((name, c))
    for name in points:
        if rng.randrange(3) == 0:
            parts.append((name, rng.choice((1, -1, 2, 3))))
    left, right = [], []
    for name, c in parts:
        # a part moved to the right side is negated, so left - right is Σ c·q as drawn
        (left.append((name, c)) if rng.randrange(2) else right.append((name, -c)))
    if rng.randrange(6) == 0 and free:
        # a cancelling pair on one side collects to nothing (4.2, k34)
        side = left if rng.randrange(2) else right
        side += [(free[0], 2), (free[0], -2)]
    k = rng.randrange(-4, 5)
    tree = [op, term_of(rng, left, k if rng.randrange(2) else 0),
            term_of(rng, right, 0 if rng.randrange(2) else -k)]
    return ["not", tree] if rng.randrange(3) == 0 else tree


def condition(rng, box, *, bad=None):
    free = [n for n, (lo, hi) in box.items() if lo != hi]
    points = [n for n, (lo, hi) in box.items() if lo == hi]
    rng.shuffle(free)
    groups, i = [], 0
    for _ in range(rng.randrange(1, 4)):
        take = rng.randrange(0, 3)
        groups.append(free[i:i + take])
        i += take
    atoms = [atom(rng, g, points) for g in groups]
    if bad == "shared" and free:
        atoms.append(["lt", qn(free[0]), lit(rng.randrange(-3, 4))])
        atoms[0] = ["le", add(qn(free[0]), lit(0)), lit(rng.randrange(-3, 4))]
    if bad == "coefficient" and free:
        atoms[0] = ["eq", scaled(2, qn(free[0])), lit(rng.randrange(-3, 4))]
    tree = atoms[0]
    for a in atoms[1:]:
        tree = [rng.choice(("and", "or")), tree, a] if rng.randrange(2) else [rng.choice(("and", "or")), a, tree]
    if rng.randrange(4) == 0:
        tree = ["not", tree]
    if rng.randrange(10) == 0:
        tree = [rng.choice(("and", "or")), tree, [rng.choice(("top", "bottom"))]]
    return tree


def value(term, v):
    tag = term[0]
    if tag == "quantity":
        return v[term[1]]
    if tag == "decimal":
        return int(term[2])
    if tag == "add":
        return value(term[2], v) + value(term[3], v)
    return int(term[2]) * value(term[3], v)


def holds(tree, v):
    tag = tree[0]
    if tag in ("top", "bottom"):
        return tag == "top"
    if tag == "not":
        return not holds(tree[1], v)
    if tag == "and":
        return holds(tree[1], v) and holds(tree[2], v)
    if tag == "or":
        return holds(tree[1], v) or holds(tree[2], v)
    a, b = value(tree[1], v), value(tree[2], v)
    return {"lt": a < b, "le": a <= b, "eq": a == b}[tag]


def shard(seed):
    rng = random.Random(seed)
    boxes, conditions, kinds = [], [], []
    for _ in range(BOXES_PER_SHARD):
        box = {}
        for name in ("q0", "q1", "q2", "q3")[:rng.randrange(1, 5)]:
            lo = rng.randrange(-3, 4)
            box[name] = (lo, lo + rng.choice((0, 0, 1, 2, 3)))
        rows, row_kinds = [], []
        for _ in range(CONDITIONS_PER_BOX):
            bad = rng.choice((None,) * 8 + ("shared", "coefficient"))
            rows.append(condition(rng, box, bad=bad))
            row_kinds.append(bad)
        boxes.append(box)
        conditions.append(rows)
        kinds.append(row_kinds)
    return boxes, conditions, kinds


def lean_eval(boxes, conditions):
    env = cell_env()
    cases = [{"environment": env, "quantities": [{"name": n, "tag": D, "lo": lo, "hi": hi}
                                                 for n, (lo, hi) in box.items()],
              "conditions": rows} for box, rows in zip(boxes, conditions)]
    out = subprocess.run([str(LEAN)], input=json.dumps(cases), text=True, capture_output=True, timeout=500)
    assert out.returncode == 0, out.stderr
    rows = json.loads(out.stdout)
    assert all(r["status"] == "ok" for r in rows), rows[:1]
    return [r["results"] for r in rows]


def rust_eval(boxes, conditions):
    cases = [{"id": f"{i}-{j}", "kind": "risk-condition", "condition": tree,
              "ranges": {n: {"tag": D, "lo": str(lo), "hi": str(hi)} for n, (lo, hi) in box.items()},
              "scales": {}}
             for i, (box, rows) in enumerate(zip(boxes, conditions)) for j, tree in enumerate(rows)]
    out = subprocess.run([str(RUST), "conformance"], input=json.dumps(cases), text=True, capture_output=True,
                         timeout=500)
    rows = json.loads(out.stdout)
    it = iter(rows)
    return [[next(it) for _ in box_rows] for box_rows in conditions]


@pytest.mark.parametrize("seed", range(SHARDS))
def test_conditions_agree_with_enumeration(seed):
    boxes, conditions, kinds = shard(20260929 + seed)
    lean = lean_eval(boxes, conditions)
    rust = rust_eval(boxes, conditions)
    decided = rejected = 0
    for box, rows, row_kinds, lean_rows, rust_rows in zip(boxes, conditions, kinds, lean, rust):
        names = list(box)
        valuations = [dict(zip(names, values)) for values in
                      itertools.product(*(range(lo, hi + 1) for lo, hi in box.values()))]
        for tree, bad, l, r in zip(rows, row_kinds, lean_rows, rust_rows):
            if "error" in l:
                # rejected in both, with one text; only the constructed bad kinds are rejected
                assert r["status"] == "error", (tree, box, l, r)
                assert f'{r["error"]["code"]}: {r["error"]["message"]}' == l["error"], (tree, box, l, r)
                assert l["error"].startswith(("RiskConditionShared", "RiskEqualityCoefficient")), l
                assert bad is not None, (tree, box, l)
                rejected += 1
                continue
            truth = [holds(tree, v) for v in valuations]
            expected = (any(truth), all(truth))
            assert (l["possible"], l["certain"]) == expected, (tree, box, l)
            assert r["status"] == "ok" and (r["possible"], r["certain"]) == expected, (tree, box, r)
            if l["possible"]:
                w = l["witness"]
                assert all(box[n][0] <= w[n] <= box[n][1] for n in names), (tree, box, w)
                assert holds(tree, w), (tree, box, w)
            else:
                assert l["witness"] is None
            decided += 1
    assert decided + rejected == BOXES_PER_SHARD * CONDITIONS_PER_BOX
    assert decided > rejected > 0
