"""Lean reads what Python reads on every environment of the probe matrix (review A of English Lean E2, recheck 1).

The E2.5 bulk comparison had no `nary@0` environment, so it missed that Lean's typed check decoded an n-ary
environment as submitted while every other family decoded its typing view: with `norms@0`, `data@0` or
`definitions@0` beside `nary@0`, every sentence came back `IllTyped`. The class is a profile combination on
which one reader's typed check sees another environment than the other's, so this test enumerates the
combinations instead of naming the one found: every family of `tests/probe_matrix.py` with every subset of its
layer profiles that Python's `Environment` admits, each predicate written once positively and once negatively
over the declared constants, plus the family's semantic formula. On each sentence Lean's verdict and formula
must be Python's.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

import pytest

from tests import probe_matrix as pm
from ve import Environment, ast
from ve import english as EN
from ve.backends import english_lean as L
from ve.backends import relay
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")


def environments():
    for family in pm.FAMILIES:
        for size in range(len(pm.LAYERS) + 1):
            for layers in combinations(pm.LAYERS, size):
                profiles = tuple(sorted({*family, *layers}))
                try:
                    yield profiles, Environment(pm.raw_environment(profiles))
                except VEError:
                    continue


ENVIRONMENTS = dict(environments())


def formulas(env):
    constants = sorted(env.constants)
    out = [pm.semantic_formula(env)]
    for name, decl in sorted(env.predicates.items()):
        terms = tuple(ast.Const(constants[i % len(constants)]) for i in range(len(decl.arguments)))
        atom = (ast.Unary(name, *terms) if len(terms) == 1 else ast.Binary(name, *terms) if len(terms) == 2
                else ast.Atom(name, terms))
        out += [atom, ast.Not(atom)]
    return out


def python(env, words, source):
    try:
        reading = EN._python_reading(env, source, words, {})
    except VEError as exc:
        return ("refused", type(exc).__name__)
    return ("one", [ast._to_data(f) for f in reading.document.formulas])


def lean(row):
    if row["status"] != "ok":
        return ("error", row.get("error"))
    result = row["result"]
    if result["status"] != "one":
        return ("refused", L.CODE_CLASSES.get(result.get("code"), result.get("code")))
    return ("one", result["ast"])


def test_the_matrix_reaches_every_family_with_every_layer():
    """The enumeration is not vacuous: every family is read, `nary@0` with each layer Python admits beside it."""
    assert {tuple(p for p in profiles if p in {"closure@0", "nary@0", "order@0"})
            for profiles in ENVIRONMENTS} == {tuple(f) for f in pm.FAMILIES}
    nary = {p for profiles in ENVIRONMENTS if "nary@0" in profiles for p in profiles}
    assert {"data@0", "definitions@0", "norms@0"} <= nary


@pytest.mark.parametrize("profiles", sorted(ENVIRONMENTS), ids=lambda p: "+".join(p) or "base")
def test_lean_reads_every_matrix_sentence_as_python_does(profiles):
    env = ENVIRONMENTS[profiles]
    words = EN.EnglishVocabulary(env)
    sources = [EN.EnglishTraversal(env, words).render(f) + "." for f in formulas(env)]
    rows = relay.rows(L.MODE, [L.request(env, source, words, {}) for source in sources])
    for source, row in zip(sources, rows):
        expected = python(env, words, source)
        assert expected[0] == "one", (source, expected)  # the rendering is Python's own wording
        assert lean(row) == expected, source
