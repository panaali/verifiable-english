"""Parsing on the Lean authority: Lean's surface parsers decide acceptance."""
from __future__ import annotations

from pathlib import Path

import pytest

from ve.backends import dispatch, lean_runner, validation
from ve.environment import Environment
from ve.errors import CheckerUnavailable, VEError
from ve.parser import canonicalize, parse
from ve.printer import print_formula
from tests import probe_matrix as pm

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")


def outcome(call):
    try:
        return ("accepted", call())
    except VEError as exc:
        return ("rejected", exc.to_dict())


def sources(env):
    good = print_formula(env, pm.semantic_formula(env)) + ".\n"
    return [good, good + good, "broken.\n", "x is missing.\n", "for every item a, (a is base).\n",
            "for every item a, (for every item a, (a is base)).\n", "x is base", "x  is base.\n",
            "é.\n", " " * 65537, good * 2000]


@pytest.mark.parametrize("family", [(), ("closure@0",), ("closure@0", "nary@0"), ("order@0",),
                                    ("data@0",), ("norms@0",), ("definitions@0",),
                                    ("closure@0", "definitions@0"),
                                    ("closure@0", "nary@0", "definitions@0")])
def test_parse_and_canonical_text_match_python(monkeypatch, family):
    env = Environment(pm.raw_environment(family))
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda op, authority: seen.append((op, authority))])
    for source in sources(env):
        results = {}
        for authority in ("python", "lean"):
            monkeypatch.setenv("VE_AUTHORITY", authority)
            results[authority] = (outcome(lambda: parse(env, source)),
                                  outcome(lambda: canonicalize(env, source)))
        assert results["lean"] == results["python"], source[:40]
    assert ("parse", "lean") in seen


SUGAR = ["no item is base.\n", "every item a that is derived, (a is base).\n",
         "(@x is base) iff (@x is derived).\n",
         "define derived(a) as (a is base).\n@x is derived.\n"]


def test_definitions_sources_without_sugar_are_leans(monkeypatch):
    """Over a definitions@0 environment Lean's parser decides every source that
    reads no definitions sugar."""
    env = Environment(pm.raw_environment(("definitions@0",)))
    asked = []
    fake(monkeypatch, lambda case: asked.append(case["source"]) or
         {"id": "parse", "status": "ok", "ast": [["unary", "derived", ["const", "x"]]]})
    parse(env, "@x is derived.\n")
    assert asked == ["@x is derived.\n"]


@pytest.mark.parametrize("source", SUGAR)
def test_definitions_sugar_stays_with_python(monkeypatch, source):
    """A source read through the definitions sugar keeps Python's reading (the
    sugar is in no Lean surface parser: a recorded scope gap); Lean is not asked."""
    env = Environment(pm.raw_environment(("definitions@0",)))
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = (outcome(lambda: parse(env, source)), outcome(lambda: canonicalize(env, source)))
    assert expected[0][0] == "accepted", source
    real = lean_runner.run
    fake(monkeypatch, lambda case: pytest.fail("Lean was asked about a sugared source"))
    assert (outcome(lambda: parse(env, source)), outcome(lambda: canonicalize(env, source))) == expected
    with pytest.raises(VEError):
        real("parse", [{"id": "parse", "environment": env.to_dict(), "source": source}])


def fake(monkeypatch, row):
    real = lean_runner.run

    def run(mode, cases, **kw):
        return [row(case) for case in cases] if mode == "parse" else real(mode, cases, **kw)

    monkeypatch.setattr(lean_runner, "run", run)
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    monkeypatch.setenv("VE_AUTHORITY", "lean")


def test_lean_acceptance_of_a_python_rejection_is_unavailable(monkeypatch):
    env = Environment(pm.raw_environment(()))
    fake(monkeypatch, lambda case: {"id": "parse", "status": "ok", "ast": [["top"]]})
    with pytest.raises(CheckerUnavailable, match="Python decoder rejects"):
        parse(env, "broken.\n")


def test_a_different_lean_document_is_unavailable(monkeypatch):
    env = Environment(pm.raw_environment(()))
    fake(monkeypatch, lambda case: {"id": "parse", "status": "ok", "ast": [["bottom"]]})
    with pytest.raises(CheckerUnavailable, match="identities differ"):
        parse(env, "true.\n")


def test_a_lean_only_rejection_is_leans(monkeypatch):
    from ve.backends.diagnostics import checker_error
    env = Environment(pm.raw_environment(()))

    def reject(case):
        raise checker_error("SyntaxError: the source is not accepted by the Lean surface parser")

    fake(monkeypatch, reject)
    with pytest.raises(VEError, match="not accepted by the Lean surface parser"):
        parse(env, "true.\n")
