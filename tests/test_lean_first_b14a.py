"""Lean-first batch 14a: the `definitions@0` surface sugar is Lean's.

`no S is P`, `every S x that is P, (A)`, `(A) iff (B)` and `define p(x, ...) as (A)` are read by the FOL, closure
and core family parsers (`VE.Surface.parseRawWith` and its closure and core copies; the gate refuses
`definitions@0` on the order family) and diagnosed by
`VE.Service.ParseDiagnostic.scan`; `ve.parser._parse_lean` no longer keeps Python's reading for them. The retained
Python reader (`_parse_python`, still the reader outside Lean's `parse` scope) is the oracle: every source here gets
the same document, canonical text, or code, message and span from Lean."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ve import parser
from ve.backends import relay, validation
from ve.environment import Environment
from ve.errors import VEError
from ve.parser import canonicalize, parse, parse_with_metadata
from ve.printer import print_document
from tests import probe_matrix as pm

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")

FAMILIES = [("definitions@0",), ("closure@0", "definitions@0"), ("closure@0", "nary@0", "definitions@0"),
            ("definitions@0", "norms@0"), ("data@0", "definitions@0")]

ACCEPTED = [
    "no item is base.\n",
    "no item is derived.\n",
    "every item a that is derived, (a is base).\n",
    "(@x is base) iff (@x is derived).\n",
    "define derived(a) as (a is base).\n@x is derived.\n",
    "not (no item is base).\n",
    "for every item b, (every item a that is base, ((a is base) iff (b is base))).\n",
    "(no item is base) and (every item a that is base, (true)).\n",
    "((true) iff (false)) or ((false) iff (true)).\n",
    "if (no item is base), then (every item a that is derived, (not (a is base))).\n",
    "define derived(a) as (a is base).\ndefine derived(b) as (b is base).\n",
]

REJECTED = [
    "no thing is base.\n",                                         # unknown sort
    "no item is nothing.\n",                                       # unknown unary predicate
    "no item base.\n",                                             # expected ' is '
    "no item is base",                                             # expected '.\n'
    "every item x that is base, (x is base).\n",                   # a constant is no binder name
    "every item a that is base, (every item a that is base, (a is base)).\n",  # shadowing
    "every item base that is base, (true).\n",                     # a predicate is no binder name
    "every item no that is base, (true).\n",                       # a reserved word is no binder name
    "every item a that base, (a is base).\n",                      # expected ' that is '
    "every item a that is base (a is base).\n",                    # expected ', ('
    "every thing a that is base, (true).\n",                       # unknown sort
    "every item a that is nothing, (true).\n",                     # unknown unary predicate
    "every item a that is base, (b is base).\n",                   # unbound variable
    "(true) iff true.\n",                                          # expected '('
    "(true) xor (true).\n",                                        # expected ') and (' or ') or ('
    "(true) iff (true.\n",                                         # expected ')'
    "define base(a) as (true).\n",                                 # not a defined predicate
    "define nothing(a) as (true).\n",                              # not a predicate at all
    "define derived(a) as (true).\n",                              # body differs
    "define derived(a) as (not (a is base)).\n",                   # body differs
    "define derived(base) as (base is base).\n",                   # repeated definition argument
    "define derived(x) as (x is base).\n",                         # a constant as argument
    "define derived(a, b) as (a is base).\n",                      # one argument only
    "define derived(a) as (b is base).\n",                         # unbound variable
    "define derived(a) as (a is base)\n",                          # expected '.\n'
    "define derived(a) is (a is base).\n",                         # expected ') as ('
    "true.\ndefine derived(a) as (true).\nfalse.\n",               # second statement's body
    "define derived(a) as (true).\nbroken.\n",                     # the first fault in source order
    "(@x is base) iff (@x step @x).\n",                            # unknown binary predicate (outside closure)
    "every item a that is base, (a is base) iff (true).\n",        # expected ')'
    "define  derived(a) as (a is base).\n",                        # double space
    "no  item is base.\n",
    "every item a that is base,  (true).\n",
]

# Binary and n-ary definitions: the premise's head binds the arguments in declared order.
NARY = [
    "define near(a, b) as (a step b).\n",
    "define near(a, b) as (b step a).\n",
    "define near(a, a) as (a step a).\n",
    "define near(a, b) as (a step b).\n@x near @x.\n",
    "define link(a, b, c) as (triple(a, b, c)).\n",
    "define link(a, b, c) as (triple(c, b, a)).\n",
    "define link(a, b) as (triple(a, b, a)).\n",
    "link(@x, @y, @x).\n",
]


def outcome(call):
    try:
        return ("accepted", call())
    except VEError as exc:
        data = exc.to_dict()
        if data["message"].startswith(data["code"] + ": "):
            data = {**data, "message": data["message"][len(data["code"]) + 2:]}
        return ("rejected", data)


def python_reading(env, source):
    """The retained Python reader: document and canonical text, or its diagnostic."""
    return outcome(lambda: (parser._parse_python(env, source).document,
                            print_document(env, parser._parse_python(env, source).document)))


def lean_reading(env, source):
    return outcome(lambda: (parse(env, source), canonicalize(env, source)))


def nary_environment():
    raw = pm.raw_environment(("closure@0", "nary@0", "definitions@0"))
    predicates = raw["vocabulary"]["predicates"]
    predicates["near"] = {"arguments": ["item", "item"], "description": "near",
                          "defined": {"arguments": ["item", "item"],
                                      "body": ["binary", "step", ["var", 1], ["var", 0]]}}
    predicates["link"] = {"arguments": ["item"] * 3, "description": "link",
                          "defined": {"arguments": ["item"] * 3,
                                      "body": ["atom", "triple", [["var", 2], ["var", 1], ["var", 0]]]}}
    return Environment(raw)


@pytest.fixture(autouse=True)
def default_authority(monkeypatch):
    monkeypatch.delenv("VE_AUTHORITY", raising=False)
    monkeypatch.setattr(validation, "_ACCEPTED", {})


@pytest.mark.parametrize("family", FAMILIES)
def test_sugar_is_read_by_lean_as_python_read_it(monkeypatch, family):
    """Every family parser reads the sugar: the same document and canonical text, or the same code, message and
    span, as the retained Python reader; and Lean, not Python, is asked."""
    env = Environment(pm.raw_environment(family))
    asked = []
    real = relay.decide

    def spy(mode, cases, **kw):
        asked.extend(case["source"] for case in cases if mode == "parse")
        return real(mode, cases, **kw)

    monkeypatch.setattr(relay, "decide", spy)
    for source in ACCEPTED + REJECTED:
        expected = python_reading(env, source)
        assert lean_reading(env, source) == expected, (family, source)
    assert set(asked) == set(ACCEPTED + REJECTED)
    assert all(lean_reading(env, source)[0] == "accepted" for source in ACCEPTED)


def test_binary_and_nary_definitions_bind_arguments_in_declared_order():
    env = nary_environment()
    for source in NARY:
        assert lean_reading(env, source) == python_reading(env, source), source
    accepted = {source for source in NARY if lean_reading(env, source)[0] == "accepted"}
    assert accepted == {NARY[0], NARY[3], NARY[4], NARY[7]}


def reordered(value):
    """`value` with every JSON object's keys in reverse order (lists keep their order: they are positional)."""
    if isinstance(value, dict):
        return {key: reordered(value[key]) for key in reversed(list(value))}
    if isinstance(value, list):
        return [reordered(item) for item in value]
    return value


# Author names that look like the printer's generated binders (`x0`, `x1`).
GENERATED_NAMES = [
    "every item x0 that is derived, (x0 is base).\n",
    "for every item x0, (every item x1 that is base, ((x0 is base) iff (x1 is base))).\n",
    "define derived(x0) as (x0 is base).\n",
    "define near(x1, x0) as (x1 step x0).\n",
    "define near(x0, x1) as (x1 step x0).\n",
]


def test_reordered_environment_keys_and_generated_names_get_the_same_answer():
    """Checklist item 4: reversing every key order of the environment (predicates, the `defined` payload) changes
    no answer, and author binders named like the printer's generated ones read as the retained reader reads them."""
    env = nary_environment()
    turned = Environment(reordered(env.to_dict()))
    assert list(turned.to_dict()["vocabulary"]["predicates"]) != list(env.to_dict()["vocabulary"]["predicates"])
    for source in ACCEPTED + REJECTED + NARY + GENERATED_NAMES:
        expected = python_reading(env, source)
        assert lean_reading(env, source) == expected, source
        assert lean_reading(turned, source) == expected, source
    assert {source for source in GENERATED_NAMES if lean_reading(env, source)[0] == "accepted"} == \
        set(GENERATED_NAMES[:4])


def test_lean_answers_sugar_on_the_wire():
    """The service's own row: a sugared source is accepted with the desugared AST, and a wrong `define` body is
    Lean's diagnostic with its span (not the generic 'not accepted by the Lean surface parser')."""
    env = Environment(pm.raw_environment(("definitions@0",)))
    [row] = relay.decide("parse", [{"id": "p", "environment": env.to_dict(), "source": "no item is derived.\n"}])
    assert row["ast"] == [["forall", "item", ["not", ["unary", "derived", ["var", 0]]]]]
    assert row["canonical"] == "for every item x0, (not (x0 is derived)).\n"
    with pytest.raises(VEError) as exc:
        relay.decide("parse", [{"id": "p", "environment": env.to_dict(),
                                "source": "define derived(a) as (true).\n"}])
    assert exc.value.message == "SyntaxError: definition body differs from identity-bound declaration"
    assert (exc.value.span.start, exc.value.span.end) == (27, 28)


def test_sugar_needs_the_definitions_profile():
    """Without `definitions@0` the sugar words are what they were: `no` and `every` are reserved terms, and
    `iff` is no connective (no silent widening)."""
    env = Environment(pm.raw_environment(()))
    for source in ("no item is base.\n", "every item a that is base, (true).\n", "(true) iff (true).\n",
                   "define base(a) as (a is base).\n"):
        assert lean_reading(env, source)[0] == "rejected", source
        assert lean_reading(env, source) == python_reading(env, source), source


def test_a_definition_body_is_compared_with_the_identity_bound_one():
    """`define` accepts exactly the declared body: changing the declared body in the environment flips the
    answer (the comparison reads the environment, not a fixed table)."""
    raw = pm.raw_environment(("definitions@0",))
    source = "define derived(a) as (not (a is base)).\n"
    assert lean_reading(Environment(raw), source)[0] == "rejected"
    changed = copy.deepcopy(raw)
    changed["vocabulary"]["predicates"]["derived"]["defined"]["body"] = ["not", ["unary", "base", ["var", 0]]]
    env = Environment(changed)
    state, (document, canonical) = lean_reading(env, source)
    assert state == "accepted"
    assert canonical == ("for every item x0, ((if (x0 is derived), then (not (x0 is base))) and "
                         "(if (not (x0 is base)), then (x0 is derived))).\n")


def test_metadata_still_comes_from_the_python_constructor():
    """Python constructs the document and its spans after Lean accepts (rule 2)."""
    env = Environment(pm.raw_environment(("definitions@0",)))
    result = parse_with_metadata(env, "every item a that is derived, (a is base).\n")
    assert result.metadata.source_names[-1] == "a"
    assert len(result.metadata.spans) == len(result.metadata.source_names)


def test_the_retained_sugar_reading_is_deleted():
    """Batch 14a deleted the stage-2c fallback: the Python reader no longer marks sugar productions, and
    `_parse_lean` has no `definitions@0` branch that keeps Python's reading."""
    import inspect
    assert not hasattr(parser, "_parse_python_marked")
    assert "sugar" not in inspect.getsource(parser._Parser.__init__)
    assert "definitions@0" not in inspect.getsource(parser._parse_lean)


PERTURBATIONS = {
    "nbsp": lambda s: s.replace(" ", " ", 1),
    "double space": lambda s: s.replace(" ", "  ", 1),
    "tab": lambda s: s.replace(" ", "\t", 1),
    "carriage return": lambda s: s.replace("\n", "\r\n", 1),
    "curly quote": lambda s: "’" + s,
    "kelvin sign": lambda s: s.replace("item", "Kitem", 1),
    "dotted capital i": lambda s: s.replace("is", "İs", 1),
    "control character": lambda s: s.replace(" ", " \x01", 1),
}


@pytest.mark.parametrize("name", sorted(PERTURBATIONS))
def test_perturbed_sugar_gets_the_same_answer(name):
    """Checklist line 3: every accepted sugar fixture with one perturbation gets the retained reader's code,
    message and span from Lean (none is silently accepted)."""
    env = Environment(pm.raw_environment(("definitions@0",)))
    for source in ACCEPTED:
        changed = PERTURBATIONS[name](source)
        if changed == source:
            continue
        expected = python_reading(env, changed)
        assert expected[0] == "rejected", (name, changed)
        assert lean_reading(env, changed) == expected, (name, changed)


def test_two_faults_report_the_first_in_source_order():
    """Checklist line 2: two faulty sugar statements in one source; Lean reports the first, as the retained
    reader does (code, message and span)."""
    env = Environment(pm.raw_environment(("definitions@0",)))
    lines = [source for source in REJECTED if source.endswith(".\n") and source.count("\n") == 1]
    for index, first in enumerate(lines):
        second = lines[(index * 7 + 3) % len(lines)]
        for source in (first + second, ACCEPTED[index % len(ACCEPTED)] + first + second):
            assert lean_reading(env, source) == python_reading(env, source), source
