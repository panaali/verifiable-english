"""Differential checks of Rust's untrusted endpoint evaluator on small boxes."""
import itertools
import json
from pathlib import Path
import random
import subprocess

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]


def _truth(tree, valuation):
    tag = tree[0]
    if tag == "not":
        return not _truth(tree[1], valuation)
    if tag == "and":
        return _truth(tree[1], valuation) and _truth(tree[2], valuation)
    if tag == "or":
        return _truth(tree[1], valuation) or _truth(tree[2], valuation)
    def term(node):
        return valuation[node[1]] if node[0] == "quantity" else int(node[2])
    left, right = term(tree[1]), term(tree[2])
    return {"lt": left < right, "le": left <= right, "eq": left == right}[tag]


def test_200_small_separable_conditions_match_enumeration():
    rng = random.Random(20260929)
    cases = []
    expected = []
    for index in range(200):
        ranges = {}
        atoms = []
        for name in ("q", "r"):
            lo = rng.randrange(-3, 3)
            hi = rng.randrange(lo, 4)
            ranges[name] = {"tag": "count", "lo": str(lo), "hi": str(hi)}
            comparison = [rng.choice(("lt", "le", "eq")), ["quantity", name],
                          ["decimal", "count", str(rng.randrange(-3, 4))]]
            atoms.append(["not", comparison] if rng.randrange(2) else comparison)
        tree = [rng.choice(("and", "or")), *atoms]
        cases.append({"id": str(index), "kind": "risk-condition", "condition": tree,
                      "ranges": ranges, "scales": {"count": "1"}})
        values = [_truth(tree, dict(zip(("q", "r"), pair))) for pair in itertools.product(
            range(int(ranges["q"]["lo"]), int(ranges["q"]["hi"]) + 1),
            range(int(ranges["r"]["lo"]), int(ranges["r"]["hi"]) + 1))]
        expected.append((any(values), all(values)))
    result = subprocess.run([str(ROOT / "rust/target/release/ve"), "conformance"],
                            input=json.dumps(cases), text=True, capture_output=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stdout + result.stderr
    rows = json.loads(result.stdout)
    assert [(row["possible"], row["certain"]) for row in rows] == expected


def test_200_prepared_records_match_enumerated_marginal_cells():
    rng = random.Random(20260930)
    cases = []
    expected = []
    for index in range(200):
        lo = rng.randrange(-3, 3)
        hi = rng.randrange(lo, 4)
        threshold = rng.randrange(-3, 4)
        op = rng.choice(("lt", "le", "eq"))
        necessary = [op, ["quantity", "q"], ["decimal", "count", str(threshold)]]
        classes = {"outage": "severe"}
        precaution = bool(rng.randrange(2))
        record = {"alternatives": ["run", "wait"], "harms": ["outage"], "classes": classes,
                  "always_possible": ["severe"] if precaution else [],
                  "unexamined": {"ruled_out_by": "team"},
                  "cells": [{"action": "run", "harm": "outage", "necessary": necessary}]}
        cases.append({"id": str(index), "kind": "risk-cells", "record": record,
                      "ranges": {"q": {"tag": "count", "lo": str(lo), "hi": str(hi)}},
                      "scales": {"count": "1"}})
        possible = any(_truth(necessary, {"q": q}) for q in range(lo, hi + 1))
        expected.append(((possible, False), (precaution, False)))
    result = subprocess.run([str(ROOT / "rust/target/release/ve"), "conformance"],
                            input=json.dumps(cases), text=True, capture_output=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stdout + result.stderr
    rows = json.loads(result.stdout)
    actual = [tuple((cell["might"], cell["leads"]) for cell in row["tables"]) for row in rows]
    assert actual == expected
