"""Python never selects a wording Lean's lexicon validity refuses (recheck 1 of E2, B).

Python's n-ary template check admitted "the value of {0} at {1} is {2}", which Lean's V3 refuses (subject first,
S3 D8), so every text of such an environment was `CheckerUnavailable` "V3 predicate value"; an edited test
(commit 3388825a) hid it. The class is any declared wording whose Python selection Lean's V1 to V6 refuse: a
narrowing that leaves the whole environment unavailable instead of falling back to the mechanical form. This
test generates declared wordings of arity one to four over prefixes, connectors, hole orders, glued holes and
suffixes, and requires, for each, that Lean accepts the lexicon Python proposes and reads the sentence Python
writes with it to Python's formula.
"""
from __future__ import annotations

from itertools import product
from pathlib import Path

import pytest

from ve import Environment, ast
from ve import english as EN
from ve.backends import english_lean as L
from ve.backends import relay
from ve.errors import VEError
from ve.profiles import LANGUAGE, SPEC_REVISION

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")

SORTS = ("signal", "moment", "reading", "source")
PREFIXES = ("", "the value of ", "now ", "it is said that ")
SUFFIXES = ("", " today", ".")
CONNECTORS = {1: (" is ok", " is very ok", " ok"),
              2: (" owns", " is owned by", " records"),
              3: (" records", " at", " has"),
              4: (" relates", " maps", " links")}
FILLERS = ("as", "via")  # between the later holes; no logical word


def wordings(k: int):
    holes = [f"{{{i}}}" for i in range(k)]
    orders = [holes] + ([[holes[1], holes[0], *holes[2:]]] if k > 1 else [])
    for prefix, suffix, connector, order in product(PREFIXES, SUFFIXES, CONNECTORS[k], orders):
        if k == 1:
            yield prefix + order[0] + connector + suffix
        else:
            yield prefix + order[0] + connector + "".join(f" {h}" if i == 0 else f" {FILLERS[i - 1]} {h}"
                                                       for i, h in enumerate(order[1:])) + suffix
    yield "{0}s" + CONNECTORS[k][0] + "".join(f" {{{i}}}" for i in range(1, k))  # a glued hole


def environment(k: int, wording: str) -> Environment | None:
    sorts = SORTS[:k]
    raw = {"language": LANGUAGE, "spec_revision": SPEC_REVISION,
           "profiles": sorted({"relational-fol@0", *(("closure@0", "nary@0") if k > 2 else ())}),
           "vocabulary": {"sorts": {s: {"description": s} for s in sorts},
                          "predicates": {"value": {"arguments": list(sorts), "description": "value",
                                                   "verbalisation": wording}},
                          "constants": {f"c{i}": {"sort": s, "description": f"c{i}"} for i, s in enumerate(sorts)}}}
    try:
        return Environment(raw)
    except VEError:
        return None


CASES = [(k, w) for k in CONNECTORS for w in wordings(k)]


def test_the_wordings_reach_both_sides_of_the_rule():
    """Not vacuous: Python selects some declared wordings and refuses others at every arity, and the finding's
    wording is among those refused."""
    selected = {k: set() for k in CONNECTORS}
    for k, wording in CASES:
        env = environment(k, wording)
        if env is not None:
            selected[k].add(EN.EnglishVocabulary(env).predicates["value"] == wording)
    assert all(found == {True, False} for found in selected.values()), selected
    assert ((3, "the value of {0} at {1} as {2}") in CASES
            and EN.EnglishVocabulary(environment(3, "the value of {0} at {1} as {2}")).predicates["value"]
            != "the value of {0} at {1} as {2}")


@pytest.mark.parametrize("k", sorted(CONNECTORS))
def test_lean_accepts_every_selection_python_makes(k):
    envs = [(w, env) for kk, w in CASES if kk == k and (env := environment(k, w)) is not None]
    cases, expected = [], []
    for wording, env in envs:
        words = EN.EnglishVocabulary(env)
        formula = (ast.Unary if k == 1 else ast.Binary if k == 2 else ast.Atom)(
            "value", *([tuple(ast.Const(f"c{i}") for i in range(k))] if k > 2 else
                       [ast.Const(f"c{i}") for i in range(k)]))
        source = EN.EnglishTraversal(env, words).render(formula) + "."
        cases.append(L.request(env, source, words, {}))
        expected.append((wording, words.predicates["value"], source, [ast._to_data(formula)]))
    for (wording, selected, source, formulas), row in zip(expected, relay.rows(L.MODE, cases)):
        assert row["status"] == "ok", (wording, row)
        result = row["result"]
        assert result["status"] == "one", (wording, selected, source, result.get("text"))
        assert result["ast"] == formulas, (wording, source)
