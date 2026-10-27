"""Seeded bugs of a relay's checks, enumerated from its source: each check weakened or deleted in turn.

A check is the test of an `if` whose body starts with `raise` (it refuses when the test holds). `weakenings` lists
each sub-condition whose replacement by a constant weakens the check (False where it refuses, True where it accepts;
`and`/`or` keep the polarity, `not` flips it), and `strengthenings` the whole check made always true. A helper
check is a call statement (`_tuple(...)`), which `deletions` drops. Because the sites are read from the AST, a check
written later is a seeded bug too, with no list to update. Used by tests/test_rights_licence_relay.py and
tests/test_defaults_checks.py.
"""
from __future__ import annotations

import ast
import copy


def checks(tree, select):
    """`(function, check)` for each `if ...: raise` of the module's top-level functions that `select(function, node)`
    accepts."""
    for function in tree.body:
        if isinstance(function, ast.FunctionDef):
            for node in ast.walk(function):
                if isinstance(node, ast.If) and isinstance(node.body[0], ast.Raise) and select(function.name, node):
                    yield function.name, node.test


def weakenings(node, refuses):
    """Every sub-condition of a check whose replacement by a constant weakens it: by False where it refuses, by True
    where it accepts. `and`/`or` keep the polarity; `not` flips it."""
    yield node, not refuses
    if isinstance(node, ast.BoolOp):
        for value in node.values:
            yield from weakenings(value, refuses)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        yield from weakenings(node.operand, not refuses)


def calls(tree, functions):
    """`(function, statement)` for each call statement (its value unused: a helper check) of `functions`."""
    for function in tree.body:
        if isinstance(function, ast.FunctionDef) and function.name in functions:
            for node in ast.walk(function):
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                    yield function.name, node


def replace(tree, old, new):
    for parent in ast.walk(tree):
        for field, value in ast.iter_fields(parent):
            if value is old:
                setattr(parent, field, new)
                return
            if isinstance(value, list) and any(item is old for item in value):
                value[[item is old for item in value].index(True)] = new
                return
    raise AssertionError("site not found")


def sites(tree, select, functions=()):
    """`(function, node, replacement, description)` for every seeded bug: each check's weakenings, each check made
    always true, and each call statement of `functions` deleted."""
    for function, check in checks(tree, select):
        for node, value in weakenings(check, True):
            yield function, node, ast.Constant(value), f"{ast.unparse(node)} -> {value}"
        yield function, check, ast.Constant(True), f"{ast.unparse(check)} -> True"
    for function, statement in calls(tree, functions):
        yield function, statement, ast.Pass(), f"{ast.unparse(statement)} deleted"


def mutants(source, filename, select, functions=()):
    """`(function, description, tree)` for each seeded bug: the module's tree with that one site replaced."""
    tree = ast.parse(source)
    for index, (function, node, _, description) in enumerate(sites(tree, select, functions)):
        mutated = copy.deepcopy(tree)
        _, old, new, _ = list(sites(mutated, select, functions))[index]
        replace(mutated, old, new)
        yield function, f"{filename}:{function}:{node.lineno}: {description}", ast.fix_missing_locations(mutated)
