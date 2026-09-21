"""Capture-avoiding closure unfolding. No induction or cyclic proof rule.

The equations are justified by finite-path decomposition (Lean Path.unfold and
star_least). Python tableau replay of these equations is not yet Lean-certified.
"""
from . import ast


def map_free(formula, replacement, depth=0):
    """Replace outer indices; preserve and shift through every local binder."""
    def term(t):
        if type(t) is ast.Const or t.index < depth:
            return t
        value = replacement(t.index - depth)
        return ast.Var(value.index + depth) if type(value) is ast.Var else value

    kind = type(formula)
    if kind in (ast.Top, ast.Bottom):
        return formula
    if kind is ast.Unary:
        return ast.Unary(formula.predicate, term(formula.term))
    if kind in (ast.Binary, ast.Eq):
        args = (term(formula.left), term(formula.right))
        return ast.Binary(formula.predicate, *args) if kind is ast.Binary else ast.Eq(*args)
    if kind is ast.Not:
        return ast.Not(map_free(formula.body, replacement, depth))
    if kind in (ast.And, ast.Or, ast.Implies):
        return kind(map_free(formula.left, replacement, depth), map_free(formula.right, replacement, depth))
    if kind in (ast.Forall, ast.Exists):
        return kind(formula.sort, map_free(formula.body, replacement, depth + 1))
    if kind is ast.Reach:
        edge = formula.edge
        if type(edge) is ast.Body:
            edge = ast.Body(edge.sort, map_free(edge.formula, replacement, depth + 2))
        return ast.Reach(formula.kind, edge, term(formula.left), term(formula.right))
    raise TypeError("Unknown formula constructor")


def shift(formula, amount=1):
    return map_free(formula, lambda i: ast.Var(i + amount))


def edge_at(edge, source, destination):
    if type(edge) is ast.Named:
        return ast.Binary(edge.relation, source, destination)
    return map_free(edge.formula, lambda i: destination if i == 0 else source if i == 1 else ast.Var(i - 2))


def unfold(reach, sort):
    """An equivalent formula in the same context, for either sign of Reach."""
    if reach.kind == "star":
        return ast.Or(ast.Eq(reach.left, reach.right),
                      ast.Reach("plus", reach.edge, reach.left, reach.right))
    shifted = shift(reach)
    continuation = ast.Exists(sort, ast.And(
        edge_at(shifted.edge, shifted.left, ast.Var(0)),
        ast.Reach("plus", shifted.edge, ast.Var(0), shifted.right)))
    return ast.Or(edge_at(reach.edge, reach.left, reach.right), continuation)


def congruence_key(reach, bindings, representative):
    """Ground endpoints and captured parameters, retaining every local index.

    Equal parameters preserve the same body relation; different edge ASTs never
    collapse through an observed finite extension or guessed inclusion.
    """
    def walk(data, depth=0):
        tag = data[0]
        if tag == 'const':
            return ('entity', representative('c:' + data[1]))
        if tag == 'var':
            return ('local', data[1]) if data[1] < depth else (
                'entity', representative(bindings[data[1] - depth]))
        if tag in ('forall', 'exists'):
            return (tag, data[1], walk(data[2], depth + 1))
        if tag == 'reach':
            edge = data[2]
            key = tuple(edge) if edge[0] == 'named' else ('body', edge[1], walk(edge[2], depth + 2))
            return (tag, data[1], key, walk(data[3], depth), walk(data[4], depth))
        return tuple(walk(x, depth) if type(x) is list else x for x in data)
    return walk(ast._to_data(reach))
