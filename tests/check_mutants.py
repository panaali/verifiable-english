"""Seeded bugs of a relay's checks, enumerated from its source: each check weakened or deleted in turn.

A check is the test of an `if` whose body starts with `raise` or `return`: an early exit, which refuses (`raise`) or
gives an answer (`return`, as `ask` shows the strict answer only when Lean says `valid` is true; review df-1b F9).
`weakenings` lists each sub-condition of a refusing check whose replacement by a constant weakens it (False where it
refuses, True where it accepts; `and`/`or` keep the polarity, `not` flips it), and `strengthenings` the whole check
made always true. A `return` exit can be wrong either way (an answer given too often or too rarely), so each of its
sub-conditions is forced both ways. A forced sub-condition is still evaluated (`c and False`, `c or True`): a check
that asks Lean and reads its answer keeps asking it, so the seeded bug is the weakened reading, not a missing call.
A helper check is a call statement (`_tuple(...)`), which `deletions` drops. `values` seeds the bugs of the values
that feed a check (review df-1b F10: the fallback chain that computes the expected decider): each operand of a value's
`and`/`or` chain dropped and each adjacent pair swapped, each `.get` default changed (dropped, or one added: the constant it is compared with), and each
comparison flipped. Because the sites are read from the AST, a check written later is a seeded bug too, with no list to
update. Used by tests/test_rights_licence_relay.py and tests/test_defaults_checks.py.
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


# Each comparison operator and its negation.
NEGATED = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.GtE, ast.GtE: ast.Lt, ast.Gt: ast.LtE, ast.LtE: ast.Gt,
           ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Is: ast.IsNot, ast.IsNot: ast.Is}


def _conditions(function):
    """The ids of the nodes a condition is made of: each test of an `if`, `while`, conditional expression, assertion
    or comprehension filter, and its `and`/`or` operands and `not` operand, down to the first other node."""
    tests = [n.test for n in ast.walk(function) if isinstance(n, (ast.If, ast.While, ast.IfExp, ast.Assert))]
    tests += [test for n in ast.walk(function) if isinstance(n, ast.comprehension) for test in n.ifs]
    found = set()
    while tests:
        node = tests.pop()
        found.add(id(node))
        if isinstance(node, ast.BoolOp):
            tests.extend(node.values)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            tests.append(node.operand)
    return found


def values(tree, functions):
    """`(function, node, replacement, description)` for each seeded bug of a value that feeds a check, in the
    top-level functions `functions(name)` accepts: each operand of a value's `and`/`or` chain dropped and each adjacent
    pair of operands swapped (a condition's chain is `weakenings`'), each `.get` default dropped or, where there is
    none, one added (the constant the `.get` is compared with, else "mutant"), and each comparison operator replaced
    by its negation."""
    for function in tree.body:
        if not (isinstance(function, ast.FunctionDef) and functions(function.name)):
            continue
        conditions = _conditions(function)
        # A `.get` compared with a constant other than None gets that constant as its default (`rule.get("mode",
        # "default") != "default"`): any other added default compares the same as None.
        compared = {id(n.left): n.comparators[0].value for n in ast.walk(function)
                    if isinstance(n, ast.Compare) and isinstance(n.comparators[0], ast.Constant)
                    and n.comparators[0].value is not None}
        for node in ast.walk(function):
            text = ast.unparse(node)
            if isinstance(node, ast.BoolOp) and id(node) not in conditions:
                for i, value in enumerate(node.values):
                    rest = node.values[:i] + node.values[i + 1:]
                    yield (function.name, node, rest[0] if len(rest) == 1 else ast.BoolOp(node.op, rest),
                           f"{text} drops {ast.unparse(value)}")
                for i in range(len(node.values) - 1):
                    swapped = list(node.values)
                    swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
                    yield function.name, node, ast.BoolOp(node.op, swapped), f"{text} swaps operands {i}, {i + 1}"
            elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get"
                  and 1 <= len(node.args) <= 2 and not node.keywords):
                added = ast.Constant(compared.get(id(node), "mutant"))
                args = node.args[:1] if len(node.args) == 2 else [node.args[0], added]
                change = "no default" if len(args) == 1 else f"default {ast.unparse(added)}"
                yield function.name, node, ast.Call(node.func, args, []), f"{text} -> {change}"
            elif isinstance(node, ast.Compare):
                for i, op in enumerate(node.ops):
                    ops = list(node.ops)
                    ops[i] = NEGATED[type(op)]()
                    yield function.name, node, ast.Compare(node.left, ops, node.comparators), f"{text} flips op {i}"


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


def sites(tree, select, functions=(), feeding=lambda function: False):
    """`(function, node, replacement, description)` for every seeded bug: each refusing check's weakenings and the
    check made always true, each sub-condition of a `return` exit forced both ways, each call statement of
    `functions` deleted, and the `values` of the functions `feeding` accepts."""
    for function, check, refuses in checks(tree, select):
        for node, weakened in weakenings(check, True):
            for value in (weakened,) if refuses else (weakened, not weakened):
                yield function, node, forced(node, value), f"{ast.unparse(node)} -> {value}"
        if refuses:
            yield function, check, forced(check, True), f"{ast.unparse(check)} -> True"
    for function, statement in calls(tree, functions):
        yield function, statement, ast.Pass(), f"{ast.unparse(statement)} deleted"
    yield from values(tree, feeding)


def mutants(source, filename, select, functions=(), feeding=lambda function: False):
    """`(function, description, tree)` for each seeded bug: the module's tree with that one site replaced."""
    tree = ast.parse(source)
    for index, (function, node, _, description) in enumerate(sites(tree, select, functions, feeding)):
        mutated = copy.deepcopy(tree)
        _, old, new, _ = list(sites(mutated, select, functions, feeding))[index]
        replace(mutated, old, new)
        yield function, f"{filename}:{function}:{node.lineno}: {description}", ast.fix_missing_locations(mutated)
