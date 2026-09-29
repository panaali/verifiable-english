"""The W6a FRET re-rating (PLAN-EXPAND2 W6 acceptance (2)): the 30 sampled
items with time-indexed relations over a user time sort. Checks the record's
integrity and the one mechanical claim that moved items: bounded "within N
ticks" unrolls over a successor relation within the depth budget, and Lean
admits and evaluates the expansion."""
from collections import Counter
import json
from pathlib import Path
import re

import pytest

from tests.test_units_lean_w6a import LEAN, lean, quantity
from tests.test_w6a_review_regressions import raw_environment
from ve.environment import Environment
from ve.errors import ResourceLimit
from ve.units import elaborate_quantity

ROOT = Path(__file__).resolve().parents[1]
E0 = ROOT / "experiments" / "E0"


def records():
    base = [json.loads(line) for line in (E0 / "survey_samples" / "fret.jsonl").open()]
    rerated = [json.loads(line) for line in (E0 / "survey_samples" / "fret-w6a.jsonl").open()]
    return base, rerated


def test_rerating_covers_exactly_the_e0_sample():
    base, rerated = records()
    assert [r["id"] for r in rerated] == [b["id"] for b in base]
    assert [r["e0_class"] for r in rerated] == [b["class"] for b in base]
    assert Counter(r["w6a_class"] for r in rerated) == {"b": 10, "c": 16, "d": 4}
    moved = [i + 1 for i, r in enumerate(rerated) if r["w6a_class"] != r["e0_class"]]
    assert moved == [20, 26]
    # Every item still blocked says why: a numeric signal binder, real
    # arithmetic, or metric (non-tick) time.
    for r in rerated:
        if r["w6a_class"] in ("c", "d"):
            assert re.search(r"numbers2|real|arithmetic|metric|depth", r["reason"]), r


def test_report_table_matches_the_record():
    _, rerated = records()
    text = (E0 / "FRET-W6A-RERATING.md").read_text()
    rows = re.findall(r"^\| (\d+) \| ([abcd]) \| ([abcd]) \|", text, re.M)
    assert [(int(i), a, b) for i, a, b in rows] == \
        [(i + 1, r["e0_class"], r["w6a_class"]) for i, r in enumerate(rerated)]
    assert "| W6a (this re-rating) | 0 | 10 (33%) | 16 (53%) | 4 (13%) |" in text


def tick_env():
    return raw_environment({}, sorts={"tick": {"description": "a discrete time point"}}, predicates={
        "start": {"arguments": ["tick"], "description": "the first tick"},
        "next": {"arguments": ["tick", "tick"], "description": "one-tick successor"},
        "thrust_borne": {"arguments": ["tick"], "description": "lift_mode = thrust_borne"}})


def within(steps):
    """P now, or at a successor within `steps` more ticks; var 0 is the current tick."""
    body = ["unary", "thrust_borne", ["var", 0]]
    for _ in range(steps):
        body = ["or", ["unary", "thrust_borne", ["var", 0]],
                ["exists", "tick", ["and", ["binary", "next", ["var", 1], ["var", 0]], body]]]
    return ["exists", "tick", ["and", ["unary", "start", ["var", 0]], body]]


def chain(length, satisfied):
    ticks = [f"t{i}" for i in range(length)]
    return {"complete": True, "domains": {"tick": ticks}, "constants": {},
            "relations": {"start": [["t0"]], "next": [[a, b] for a, b in zip(ticks, ticks[1:])],
                          "thrust_borne": [[f"t{i}"] for i in satisfied]}}


def depth(node):
    if type(node) is not list or node[0] in ("unary", "binary"):
        return 0
    return 1 + max((depth(x) for x in node[1:] if type(x) is list), default=0)


@pytest.mark.skipif(not LEAN.exists(), reason="build the Lean ve_quantity runner first")
@pytest.mark.parametrize("steps,expected_depth", [(16, 51), (13, 42)])
def test_bounded_response_unrolls_and_lean_admits_it(steps, expected_depth):
    raw = tick_env()
    formula = within(steps)
    assert depth(formula) + 1 == expected_depth  # the atom at the bottom counts
    elaborate_quantity(Environment(raw), quantity(formula))
    cases = [{"id": f"{steps}:{at}", "environment": raw, "quantity": quantity(formula),
              "model": chain(steps + 4, [at])} for at in (0, steps, steps + 1)]
    got = lean(cases)
    assert [g["status"] for g in got] == ["ok"] * 3, got
    assert [g["value"] for g in got] == [True, True, False]


def test_persistence_over_one_hundred_ticks_exceeds_the_depth_budget():
    # Item 8's persisted(100, ...) cannot unroll: depth 64 bounds the expansion.
    with pytest.raises(ResourceLimit):
        elaborate_quantity(Environment(tick_env()), quantity(within(100)))
