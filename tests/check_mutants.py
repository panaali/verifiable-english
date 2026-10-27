"""Seeded bugs of a relay's checks, enumerated from its source: each check weakened or deleted in turn.

A check is the test of an `if` whose body starts with `raise` or `return`: an early exit, which refuses (`raise`) or
gives an answer (`return`, as `ask` shows the strict answer only when Lean says `valid` is true; review df-1b F9).
`weakenings` lists each sub-condition of a refusing check whose replacement by a constant weakens it (False where it
refuses, True where it accepts; `and`/`or` keep the polarity, `not` flips it), and `strengthenings` the whole check
made always true. A `return` exit can be wrong either way (an answer given too often or too rarely), so each of its
sub-conditions is forced both ways. A forced sub-condition is still evaluated (`c and False`, `c or True`): a check
that asks Lean and reads its answer keeps asking it, so the seeded bug is the weakened reading, not a missing call.
A helper check is a call statement (`_tuple(...)`), which `deletions` drops. Because the sites are read from the AST,
a check written later is a seeded bug too, with no list to update. Used by tests/test_rights_licence_relay.py and
tests/test_defaults_checks.py.
"""
from __future__ import annotations

import ast
import copy


EXITS = (ast.Raise, ast.Return)


def checks(tree, select):
    """`(function, check, refuses)` for each `if ...: raise` (`refuses`) and `if ...: return` of the module's
    top-level functions that `select(function, node)` accepts."""
    for function in tree.body:
        if isinstance(function, ast.FunctionDef):
            for node in ast.walk(function):
                if isinstance(node, ast.If) and isinstance(node.body[0], EXITS) and select(function.name, node):
                    yield function.name, node.test, isinstance(node.body[0], ast.Raise)


def weakenings(node, refuses):
    """Every sub-condition of a check whose replacement by a constant weakens it: by False where it refuses, by True
    where it accepts. `and`/`or` keep the polarity; `not` flips it."""
    yield node, not refuses
    if isinstance(node, ast.BoolOp):
        for value in node.values:
            yield from weakenings(value, refuses)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        yield from weakenings(node.operand, not refuses)


def forced(node, value):
    """`node` still evaluated, its value `value`: `node and False`, `node or True`."""
    return ast.BoolOp(ast.Or() if value else ast.And(), [node, ast.Constant(value)])


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
    """`(function, node, replacement, description)` for every seeded bug: each refusing check's weakenings and the
    check made always true, each sub-condition of a `return` exit forced both ways, and each call statement of
    `functions` deleted."""
    for function, check, refuses in checks(tree, select):
        for node, weakened in weakenings(check, True):
            for value in (weakened,) if refuses else (weakened, not weakened):
                yield function, node, forced(node, value), f"{ast.unparse(node)} -> {value}"
        if refuses:
            yield function, check, forced(check, True), f"{ast.unparse(check)} -> True"
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
