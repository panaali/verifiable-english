"""The soft completion's differential (docs/spec/rd-9-soft-chain.md 3.11 and 8.3; plan SC-8; build checklist 2).

Seeded twin documents under `norm-defaults@0` on the soft chain, each twin's act unspecified: Python's search, an
untrusted generator, records a situation per pair over Lean's filled frame, and Lean's `readings-validate` is the only
answer. Every situation the search finds is accepted by Lean; a set for which it finds none is refused. Each input
is then mutated by one fault and by two (a reserved name, a decision table in a separation base, the vocabulary limit
at limit, limit + 1, a retyped field, null for an absent field, reordered keys): a fault is refused with the text of
the check it breaks, two faults with the earlier check's text in 3.11's order, and a mutation Lean reads as the same
input changes nothing. The route relays every row unchanged (code and text). Rust has no readings role: its replay
of the situations was deleted in lean-first batch 3 (composition-s1 9.3), so the third leg is Lean's own answer on
the unmutated input.
"""
from __future__ import annotations

import copy
import os
import random

import pytest

from tests import lean_routes
from tests.test_readings_s1_differential import (ASKS, SEARCH_FAILURES, norm, reading, reading_set, routed,
                                                 twins, unit)
from tests.test_readings_s1_lean import situation_id
from tests.test_readings_sd_lean import env_sd
from ve.readings_route import run_lean
from ve.readings_s1 import record_situations, search

SEED = 20261013
COUNT = int(os.environ.get("VE_SD_DIFFERENTIAL_COUNT", "12"))


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def soft_twins(rng):
    """S1's twins (`twins`), the twin's act unspecified under `norm-defaults@0`, sometimes the other act too."""
    _, document, _ = twins(rng)
    pred = document["reading_sets"][0]["readings"][0]["content"]["norm"]["predicate"]
    other = "help_required" if pred == "avoid_required" else "avoid_required"
    unspecified = (pred, other) if rng.random() < 0.3 else (pred,)
    return env_sd(unspecified=unspecified), document


def _validate(cases):
    rows = []
    for start in range(0, len(cases), 40):
        rows.extend(run_lean(cases[start:start + 40]))
    return rows


def _elaborated(raw, document):
    [row] = run_lean([{"id": "e", "kind": "readings-elaborate", "environment": raw, "document": document}])
    return row if row.get("status") == "ok" and "filled" in row else None


def generated(count=COUNT):
    rng = random.Random(SEED)
    out = []
    for n in range(count):
        raw, document = soft_twins(rng)
        rs = document["reading_sets"][0]
        filled = _elaborated(raw, document)
        found = {}
        if filled is not None:
            try:
                found = search(raw, document, rs["id"], filled=filled)
            except SEARCH_FAILURES:
                found = {}
        document["reading_sets"][0] = record_situations(rs, {k: v for k, v in found.items() if v is not None})
        complete = bool(found) and all(v is not None for v in found.values())
        out.append(({"id": f"c{n}", "kind": "readings-validate", "environment": raw, "document": document},
                    filled is not None, complete))
    return out


def test_every_situation_the_search_finds_is_leans():
    cases = generated()
    rows = _validate([c for c, _, _ in cases])
    admitted = refused = 0
    for n, ((case, elaborated, complete), row) in enumerate(zip(cases, rows)):
        if elaborated and complete:
            assert row["status"] == "ok", (n, row)
            assert all(p["pair"]["separated"] for s in row["sets"] for p in s["pairs"])
            admitted += 1
        elif elaborated:
            assert row["status"] == "error", (n, row)
            refused += 1
        if n % 10 == 0:
            # The route relays Lean's row, its code and text, unchanged.
            assert routed(case) == {k: v for k, v in row.items() if k != "id"}, n
    assert admitted >= COUNT // 4 and refused >= 1, (admitted, refused)


# --- one and two faults on F-SD1 (3.11's order: reserved names, then the author checks, then the situations)

def _base_case():
    """F-SD1 with its situation recorded by the search (the generated route)."""
    raw = env_sd()
    rs = reading_set("rs1", "u1", [reading("strict", norm("no-deception", "avoid_required", True)),
                                   reading("default", norm("no-deception", "avoid_required", True, "default"))])
    document = {"units": [unit("u1")], "reading_sets": [rs]}
    found = search(raw, document, "rs1", filled=_elaborated(raw, document))
    document["reading_sets"][0] = record_situations(rs, found)
    return {"id": "f", "kind": "readings-validate", "environment": raw, "document": document}


def reserved(case):
    """Row 2: a unit id beginning `unsaid--`."""
    case["document"]["units"].append(unit("unsaid--u9", ASKS_ALL_ASSERTED, "asserted"))


ASKS_ALL_ASSERTED = ["forall", "agent", ["forall", "user", ASKS]]


def _predicates(case, count):
    predicates = case["environment"]["vocabulary"]["predicates"]
    for k in range(count):
        predicates[f"p{k}"] = {"arguments": ["agent"], "description": "base"}
        # A situation's base lists every base relation of the vocabulary.
        for entry in case["document"]["reading_sets"][0]["situations"].values():
            entry["base"]["relations"][f"p{k}"] = []
    # The situation ids bind the environment.
    _rekey(case)


def at_limit(case):
    """Row 3's limit, at the limit: declared + generated + unspecified + the reading's decision = 256."""
    _predicates(case, 256 - 3 - 1 - 1)


def over_limit(case):
    """Row 3, at limit + 1: `ResourceLimit: vocabulary size` (each document's own decision predicates counted)."""
    _predicates(case, 256 - 3 - 1 - 1 + 1)


def decision_in_base(case):
    """Row 8: a separation base names a decision predicate (K2b)."""
    rs = case["document"]["reading_sets"][0]
    for entry in rs["situations"].values():
        entry["base"]["relations"]["soft__excepted__no_deception"] = [["a", "u"]]
    _rekey(case)


def _rekey(case):
    rs = case["document"]["reading_sets"][0]
    new = {sid: situation_id(case["environment"], entry) for sid, entry in rs["situations"].items()}
    rs["situations"] = {new[sid]: entry for sid, entry in rs["situations"].items()}
    for r in rs["readings"]:
        models = r["admission"]["distinguishing_models"]
        r["admission"]["distinguishing_models"] = {o: new.get(m, m) for o, m in models.items()}


def retyped(case):
    """A type swap: the set's version as a string."""
    case["document"]["reading_sets"][0]["version"] = "1"


def nulled(case):
    """null for an absent optional field: Lean reads `cites: null` as absent (the same input)."""
    case["document"]["reading_sets"][0]["readings"][0]["content"]["cites"] = None


def reordered(case):
    """Reordered keys of every object: the same input."""
    def sort(value):
        if isinstance(value, dict):
            return {k: sort(value[k]) for k in reversed(list(value))}
        if isinstance(value, list):
            return [sort(v) for v in value]
        return value
    case["environment"] = sort(case["environment"])
    case["document"] = sort(case["document"])


# fault → (3.11 row, the text Lean's answer starts with); None: Lean reads the same input, so the same answer.
FAULTS = {reserved: (2, "InvalidInput: reserved name unsaid--u9"),
          over_limit: (3, "ResourceLimit: vocabulary size"),
          decision_in_base: (8, "InvalidInput: invalid situation"),
          retyped: (1, "invalid or duplicate reading set version"),
          at_limit: None, nulled: None, reordered: None}


def _mutant(*faults):
    case = _base_case()
    for fault in faults:
        fault(case)
    return case


def test_one_fault_is_refused_with_its_checks_text():
    base = _base_case()
    [genuine] = _validate([base])
    assert genuine["status"] == "ok", genuine
    cases = [_mutant(fault) for fault in FAULTS]
    for (fault, expected), case, row in zip(FAULTS.items(), cases, _validate(cases)):
        if expected is None:
            assert {k: v for k, v in row.items() if k != "id"} == {k: v for k, v in genuine.items() if k != "id"} \
                or fault is at_limit and row["status"] == "ok", (fault.__name__, row)
        else:
            assert row["status"] == "error" and row["error"].startswith(expected[1]), (fault.__name__, row)
        assert routed(case) == {k: v for k, v in row.items() if k != "id"}, fault.__name__


def test_two_faults_are_refused_with_the_earlier_checks_text():
    refusing = [(f, e) for f, e in FAULTS.items() if e is not None and f is not retyped]
    pairs = [(a, b) for a in refusing for b in refusing if a[1][0] < b[1][0]]
    assert pairs
    cases = [_mutant(b[0], a[0]) for a, b in pairs]
    for (a, b), case, row in zip(pairs, cases, _validate(cases)):
        assert row["status"] == "error" and row["error"].startswith(a[1][1]), (a[0].__name__, b[0].__name__, row)
    # a fault beside a mutation Lean reads as the same input keeps its own text
    case = _mutant(reordered, reserved)
    [row] = _validate([case])
    assert row["error"].startswith(FAULTS[reserved][1]), row
    assert routed(case) == {k: v for k, v in row.items() if k != "id"}


def test_the_fault_table_can_fail():
    """Checklist 13: the unmutated input is admitted and matches no fault's text, so a route that refused every input
    (or answered every input with one fault's text) fails the tests above."""
    [row] = _validate([copy.deepcopy(_base_case())])
    assert row["status"] == "ok"
    assert not any(row.get("error", "").startswith(e[1]) for e in FAULTS.values() if e is not None)
