"""Typed parse ASTs and source-bound diagnostics in the shared response schema."""
from __future__ import annotations

from copy import deepcopy

import pytest

from tests.probe_matrix import raw_environment
from ve import ast
from ve.backends.service_schema import Invalid, check_row


def _case(source="no item is base.\n"):
    return {"id": "p", "environment": raw_environment(("definitions@0",)), "source": source}


def _ok(formula):
    return {"id": "p", "status": "ok", "ast": [formula], "canonical": "canonical\n"}


@pytest.mark.parametrize("formula,path,bad", [
    (["forall", "item", ["not", ["unary", "base", ["var", 0]]]], (2, 1, 2, 1), False),
    (["unary", "base", ["const", "x"]], (2, 1), 7),
    (["binary", "step", ["var", 0], ["var", 1]], (1,), True),
    (["reach", "plus", ["body", "item", ["top"]], ["var", 0], ["var", 1]], (1,), False),
    (["atom", "triple", [["var", 0], ["var", 1], ["var", 2]]], (2, 0, 1), True),
    (["lt", ["num", "3"], ["add", ["var", 0], ["scale", "2", ["var", 1]]]], (2, 2, 1), False),
])
def test_f2_parse_ast_leaves_are_typed(formula, path, bad):
    row = _ok(formula)
    check_row("parse", row, _case(), 0)
    changed = deepcopy(row)
    leaf = changed["ast"][0]
    for index in path[:-1]:
        leaf = leaf[index]
    leaf[path[-1]] = bad
    with pytest.raises(Invalid):
        check_row("parse", changed, _case(), 0)


def test_f2_every_formula_constructor_and_primitive_leaf_is_typed():
    term = ["var", 0]
    form = ["top"]
    cases = {
        "top": ["top"], "bottom": ["bottom"],
        "unary": ["unary", "base", term],
        "binary": ["binary", "step", term, term],
        "atom": ["atom", "triple", [term, term, term]],
        "eq": ["eq", term, term],
        "lt": ["lt", ["num", "1"], ["scale", "2", term]],
        "le": ["le", ["add", term, term], term],
        "not": ["not", form],
        "and": ["and", form, form], "or": ["or", form, form],
        "implies": ["implies", form, form],
        "forall": ["forall", "item", form], "exists": ["exists", "item", form],
        "reach": ["reach", "star", ["body", "item", form], term, term],
    }
    assert set(cases) == set(ast.WIRE_TAGS.values())
    case = _case()
    for tag, formula in cases.items():
        row = _ok(formula)
        check_row("parse", row, case, 0)
        stack = [((), formula)]
        while stack:
            path, node = stack.pop()
            if isinstance(node, list):
                stack.extend((path + (i,), value) for i, value in enumerate(node))
                continue
            changed = deepcopy(row)
            target = changed["ast"][0]
            for index in path[:-1]:
                target = target[index]
            target[path[-1]] = False if type(node) is int else 7
            with pytest.raises(Invalid):
                check_row("parse", changed, case, 0)


@pytest.mark.parametrize("field,bad", [
    ("start", 999), ("end", 999), ("line", 999), ("column", 999),
    ("start", 18), ("end", 10), ("line", 2), ("column", 11),
])
def test_f3_parse_diagnostic_span_is_bound_to_source(field, bad):
    case = _case("no item is absent.\n")
    row = {"id": "p", "status": "error", "error": "UnknownSymbol: unknown unary predicate 'absent'",
           "span": {"start": 11, "end": 17, "line": 1, "column": 12}}
    check_row("parse", row, case, 0)
    changed = deepcopy(row)
    changed["span"][field] = bad
    with pytest.raises(Invalid):
        check_row("parse", changed, case, 0)


def test_f3_multiline_span_uses_the_line_of_its_start():
    case = _case("true.\nno item is absent.\n")
    row = {"id": "p", "status": "error", "error": "unknown unary predicate 'absent'",
           "span": {"start": 17, "end": 23, "line": 2, "column": 12}}
    check_row("parse", row, case, 0)
    for field in ("line", "column"):
        changed = deepcopy(row)
        changed["span"][field] = 1
        with pytest.raises(Invalid):
            check_row("parse", changed, case, 0)
