"""Strict text for named norm units, sharing the ordinary formula grammar."""
from __future__ import annotations

import re
import json

from . import ast
from .errors import SyntaxError, VEError
from .norms import Norm, NormDocument, _atom
from .parser import _Parser
from .printer import _Traversal

_HEADER = re.compile(r"rule ([a-z][a-z0-9-]*)(?: over ([a-z][a-z0-9-]*(?:, [a-z][a-z0-9-]*)*))?: ")
_BINDER = re.compile(r"for every ([a-z][a-z0-9_]*) (x[0-9]+)")


def print_strict(document: NormDocument, *, _w1=False):
    if not _w1 and "soft-norms@0" in document.env.profiles:
        return _print_soft_strict(document)
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


def parse_strict(env, source, *, _w1=False):
    if not _w1 and "soft-norms@0" in env.profiles:
        return _parse_soft_strict(env, source)
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


_SOFT_LINE = re.compile(
    r"rule ([a-z][a-z0-9-]*)(?: over ([a-z][a-z0-9-]*(?:, [a-z][a-z0-9-]*)*))?"
    r"( default)?(?: serves ([a-z][a-z0-9_]*))?"
    r"(?: alterable by ([a-z][a-z0-9_]*(?:, [a-z][a-z0-9_]*)*))?( hard)?: (.*)\Z")
_EXCEPTION_LINE = re.compile(r"exception of ([a-z][a-z0-9-]*)(.*)\.\Z")


def _print_soft_strict(document):
    from .softnorms import SoftEnvironment, SoftNormDocument
    from .surface.softnorms import SoftNorm
    if isinstance(document, SoftNormDocument):
        from .ast import _Decoder
        rules = []
        for source in document.rules:
            core = source.core
            exception = source.exception or {}
            rules.append(SoftNorm(core.name, core.predicate, core.sign, core.guard,
                                  core.unless, core.over, source.mode, source.rank,
                                  source.alterable, exception.get("decided_by"),
                                  tuple(_Decoder().decode(x) for x in exception.get("sufficient", ())),
                                  tuple(_Decoder().decode(x) for x in exception.get("necessary", ())),
                                  tuple(exception.get("factors", ())), source.hard))
    else:
        rules = [r if isinstance(r, SoftNorm) else SoftNorm(
            r.name, r.predicate, r.sign, r.guard, r.unless, r.over)
            for r in document.rules]
        soft_env = (document.env if isinstance(document.env, SoftEnvironment)
                    else SoftEnvironment(document.env.to_dict()))
        SoftNormDocument(soft_env, [r.to_dict() for r in rules])
    core = NormDocument(document.env, [Norm(r.name, r.predicate, r.sign, r.guard,
                                             r.unless, r.over) for r in rules])
    base_lines = print_strict(core, _w1=True).splitlines()
    traversal = _Traversal(document.env, "ve_strict")
    lines = []
    for rule, line in zip(rules, base_lines):
        header, body = line.split(": ", 1)
        if rule.mode == "default":
            header += " default"
        if rule.rank is not None:
            header += " serves " + rule.rank
        if rule.alterable:
            header += " alterable by " + ", ".join(rule.alterable)
        if rule.hard:
            header += " hard"
        lines.append(header + ": " + body)
        if rule.mode == "default":
            detail = "exception of " + rule.name
            if rule.decided_by is not None:
                detail += " decided by " + json.dumps(rule.decided_by, ensure_ascii=False)
            sorts = document.env.predicates[rule.predicate].arguments
            scope = tuple(f"x{i}" for i in reversed(range(len(sorts))))
            for kind in ("sufficient", "necessary"):
                for formula in getattr(rule, kind):
                    detail += f" {kind} (" + traversal.formula(formula, scope) + ")"
            for factor in rule.factors:
                detail += " factor " + json.dumps(factor, ensure_ascii=False)
            lines.append(detail + ".")
    return "\n".join(lines)


def _parse_soft_strict(env, source):
    from .softnorms import SoftEnvironment, SoftNormDocument
    from .surface.softnorms import SoftNorm
    if type(source) is not str:
        raise SyntaxError("Strict norms source must be text")
    normalized = []
    metadata = []
    exceptions = {}
    for line in source.splitlines():
        if line.startswith("rule "):
            m = _SOFT_LINE.fullmatch(line)
            if m is None:
                raise SyntaxError("Invalid soft strict rule header")
            header = "rule " + m[1] + (" over " + m[2] if m[2] else "")
            normalized.append(header + ": " + m[7])
            metadata.append((m[1], "default" if m[3] else "strict", m[4],
                             tuple(m[5].split(", ")) if m[5] else (), bool(m[6])))
        else:
            m = _EXCEPTION_LINE.fullmatch(line)
            if m is None or m[1] in exceptions:
                raise SyntaxError("Invalid or duplicate soft strict exception")
            exceptions[m[1]] = m[2]
    core = parse_strict(env, "\n".join(normalized), _w1=True)
    if len(core.rules) != len(metadata):
        raise SyntaxError("Soft strict rule count mismatch")
    rules = []
    for rule, (name, mode, rank, alterable, hard) in zip(core.rules, metadata):
        if name != rule.name or (mode == "strict" and name in exceptions) or (mode == "default" and name not in exceptions):
            raise SyntaxError("Soft strict exception does not match its rule")
        decided_by = None
        sufficient, necessary, factors = [], [], []
        if mode == "default":
            detail = exceptions.pop(name)
            if detail.startswith(" decided by "):
                tail = detail[len(" decided by "):]
                try:
                    decided_by, end = json.JSONDecoder().raw_decode(tail)
                except ValueError as exc:
                    raise SyntaxError("Invalid quoted exception decider") from exc
                if type(decided_by) is not str or not decided_by:
                    raise SyntaxError("Invalid quoted exception decider")
                detail = tail[end:]
            while detail:
                matched = next((kind for kind in ("sufficient", "necessary")
                                if detail.startswith(f" {kind} (")), None)
                if matched is not None:
                    parser = _Parser(env, detail[len(matched) + 3:])
                    sorts = env.predicates[rule.predicate].arguments
                    parser.binders = [(f"x{i}", sort) for i, sort in enumerate(sorts)]
                    formula = parser.formula()
                    parser.literal(")")
                    (sufficient if matched == "sufficient" else necessary).append(formula)
                    detail = parser.s[parser.i:]
                elif detail.startswith(" factor "):
                    decoder = json.JSONDecoder()
                    try:
                        factor, end = decoder.raw_decode(detail[len(" factor "):])
                    except ValueError as exc:
                        raise SyntaxError("Invalid quoted exception factor") from exc
                    if type(factor) is not str:
                        raise SyntaxError("Invalid quoted exception factor")
                    factors.append(factor)
                    detail = detail[len(" factor ") + end:]
                else:
                    raise SyntaxError("Invalid soft strict exception clause")
        rules.append(SoftNorm(rule.name, rule.predicate, rule.sign, rule.guard, rule.unless,
                              rule.over, mode, rank, alterable, decided_by,
                              tuple(sufficient), tuple(necessary), tuple(factors), hard))
    if exceptions:
        raise SyntaxError("Exception names an unknown rule")
    soft_env = env if isinstance(env, SoftEnvironment) else SoftEnvironment(env.to_dict())
    return SoftNormDocument(soft_env, [rule.to_dict() for rule in rules])
