"""Bounded user-sort counting sugar, expanded before identity and certification."""
from __future__ import annotations

from .. import ast
from ..errors import ResourceLimit, UnsupportedProfile, VEError


def _rebase_term(t, extra, depth=0):
    if type(t) is ast.Var:
        return t if t.index < depth + 1 else ast.Var(t.index + extra)
    if type(t) in (ast.Num, ast.Const):
        return t
    if type(t) is ast.Add:
        return ast.Add(_rebase_term(t.left, extra, depth), _rebase_term(t.right, extra, depth))
    if type(t) is ast.Scale:
        return ast.Scale(t.coefficient, _rebase_term(t.term, extra, depth))
    raise VEError("Unknown counting term")


def _rebase(f, extra, depth=0):
    """Keep the counted variable at index 0; shift outer references by extra."""
    k = type(f)
    if k in (ast.Top, ast.Bottom):
        return f
    if k is ast.Unary:
        return ast.Unary(f.predicate, _rebase_term(f.term, extra, depth))
    if k is ast.Binary:
        return ast.Binary(f.predicate, _rebase_term(f.left, extra, depth),
                          _rebase_term(f.right, extra, depth))
    if k is ast.Atom:
        return ast.Atom(f.predicate, tuple(_rebase_term(t, extra, depth) for t in f.terms))
    if k in (ast.Eq, ast.Lt, ast.Le):
        return k(_rebase_term(f.left, extra, depth), _rebase_term(f.right, extra, depth))
    if k is ast.Not:
        return ast.Not(_rebase(f.body, extra, depth))
    if k in (ast.And, ast.Or, ast.Implies):
        return k(_rebase(f.left, extra, depth), _rebase(f.right, extra, depth))
    if k in (ast.Forall, ast.Exists):
        return k(f.sort, _rebase(f.body, extra, depth + 1))
    if k is ast.Reach:
        edge = f.edge
        if type(edge) is ast.Body:
            edge = ast.Body(edge.sort, _rebase(edge.formula, extra, depth + 2))
        return ast.Reach(f.kind, edge, _rebase_term(f.left, extra, depth),
                         _rebase_term(f.right, extra, depth))
    raise VEError("Unknown counting formula")


def _chain(parts):
    result = parts[-1]
    for part in reversed(parts[:-1]):
        result = ast.And(part, result)
    return result


def at_least(env, sort, n, body):
    """`body` has counted x at index 0, then the surrounding de Bruijn context."""
    if type(n) is not int or not 0 <= n <= 8:
        raise VEError("CountingBound(at least 8)")
    if sort == ast.INT_SORT:
        raise UnsupportedProfile("$int quantification requires the missing numbers2 route")
    if sort not in env.sorts:
        raise VEError(f"Unknown counting sort {sort}")
    if n == 0:
        return ast.Top()
    # The source body is checked as a formula under its counted binder by callers.
    def go(j):
        parts = [ast.Not(ast.Eq(ast.Var(0), ast.Var(j - i))) for i in range(1, j)]
        parts.append(_rebase(body, j - 1))
        if j < n:
            parts.append(go(j + 1))
        return ast.Exists(sort, _chain(parts)) if len(parts) > 1 else ast.Exists(sort, parts[0])
    return go(1)


def exactly(env, sort, n, body):
    if type(n) is not int or not 0 <= n <= 7:
        raise VEError("CountingBound(exactly 7)")
    return ast.And(at_least(env, sort, n, body), ast.Not(at_least(env, sort, n + 1, body)))


def at_most(env, sort, n, body):
    if type(n) is not int or not 0 <= n <= 7:
        raise VEError("CountingBound(at most 7)")
    return ast.Not(at_least(env, sort, n + 1, body))


def n_of_m(env, sort, n, m, selected, property):
    if type(n) is not int or type(m) is not int or not 0 <= n <= 7 or not 0 <= m <= 7:
        raise VEError("CountingBound(n of m: numerator and denominator at most 7)")
    return ast.And(exactly(env, sort, m, selected),
                   exactly(env, sort, n, ast.And(selected, property)))
