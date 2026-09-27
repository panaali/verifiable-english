"""Strict text for named norm units, sharing the ordinary formula grammar."""
from __future__ import annotations

import re

from . import ast
from .errors import SyntaxError, VEError
from .norms import Norm, NormDocument, _atom
from .parser import _Parser
from .printer import _Traversal

_HEADER = re.compile(r"rule ([a-z][a-z0-9-]*)(?: over ([a-z][a-z0-9-]*(?:, [a-z][a-z0-9-]*)*))?: ")
_BINDER = re.compile(r"for every ([a-z][a-z0-9_]*) (x[0-9]+)")


def print_strict(document: NormDocument):
    traversal = _Traversal(document.env, "ve_strict")
    lines = []
    for rule in document.rules:
        sorts = document.env.predicates[rule.predicate].arguments
        binders = ", ".join(f"for every {sort} x{i}" for i, sort in enumerate(sorts))
        scope = tuple(f"x{i}" for i in reversed(range(len(sorts))))
        atom = traversal.formula(_atom(rule.predicate, len(sorts)), scope)
        literal = atom if rule.sign else f"not ({atom})"
        line = f"rule {rule.name}"
        if rule.over:
            line += " over " + ", ".join(rule.over)
        line += f": {binders}, {literal}"
        if not isinstance(rule.guard, ast.Top):
            line += " if (" + traversal.formula(rule.guard, scope) + ")"
        for carveout in rule.unless:
            line += " unless (" + traversal.formula(carveout, scope) + ")"
        lines.append(line + ".")
    return "\n".join(lines)


def parse_strict(env, source):
    if type(source) is not str:
        raise SyntaxError("Strict norms source must be text")
    rules = []
    for line in source.splitlines():
        m = _HEADER.match(line)
        if m is None:
            raise SyntaxError("Expected rule <name>: ...")
        name = m[1]
        over = tuple(m[2].split(", ")) if m[2] else ()
        body = line[m.end():]
        binders = []
        while True:
            b = _BINDER.match(body)
            if b is None:
                break
            if b[2] != f"x{len(binders)}":
                raise SyntaxError("ConsequenceArguments: binder names must be x0, x1, ...")
            binders.append((b[2], b[1]))
            body = body[b.end():]
            if not body.startswith(", "):
                raise SyntaxError("Expected comma after each binder")
            body = body[2:]
        if not binders:
            raise SyntaxError("A rule needs situation binders")
        parser = _Parser(env, body)
        parser.binders = binders[:]
        literal = parser.formula()
        sign = not isinstance(literal, ast.Not)
        atom = literal if sign else literal.body
        if not isinstance(atom, (ast.Unary, ast.Binary)):
            raise VEError(f"ConsequenceArguments: rule {name}")
        predicate = atom.predicate
        if predicate not in env.predicates or env.predicates[predicate].regulated is None:
            raise VEError(f"UnknownSymbol: regulated predicate {predicate}")
        sorts = env.predicates[predicate].arguments
        if (tuple(sort for _, sort in binders) != sorts
                or atom != _atom(predicate, len(sorts))):
            raise VEError(f"ConsequenceArguments: rule {name}")
        guard = ast.Top()
        if body.startswith(" if (", parser.i):
            parser.i += len(" if (")
            guard = parser.formula()
            parser.literal(")")
        carveouts = []
        while body.startswith(" unless (", parser.i):
            parser.i += len(" unless (")
            carveouts.append(parser.formula())
            parser.literal(")")
        if body[parser.i:] != ".":
            raise SyntaxError("Unexpected text after rule")
        rules.append(Norm(name, predicate, sign, guard, tuple(carveouts), over))
    return NormDocument(env, rules)
