"""Capture-avoiding closure unfolding. No induction or cyclic proof rule.

The independent Lean checker proves these equations and each extra rule over
all admissible structures; conformance tests compare the Python implementation.
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


EXTRA_RULES = frozenset({"closure-edge@0", "closure-compose@0", "closure-first@0",
                         "closure-last@0", "closure-named-body@0"})


def derive_extra(branch, rule, at, parameter):
    """Mirror the proved, total VE.Closure.Tableau.deriveExtra rules.

    Composition uses exact edge syntax, middle term and captured bindings.
    Eigenparameters for existential consequences still come from ordinary delta.
    """
    from .entailment import _InvalidTrace, _Signed, _term_token
    if type(at) is not int or not 0 <= at < len(branch.formulas):
        raise _InvalidTrace("invalid closure consequence target")
    item = branch.formulas[at]
    f, pos, bindings = item.formula, item.positive, item.bindings
    if rule == "closure-compose@0":
        if type(parameter) is not str or not parameter.isascii() or not parameter.isdigit():
            raise _InvalidTrace("composition requires another formula index")
        j = int(parameter)
        if not 0 <= j < len(branch.formulas):
            raise _InvalidTrace("invalid composition source")
        other = branch.formulas[j]
        g = other.formula
        if not (pos and other.positive and type(f) is ast.Reach and type(g) is ast.Reach
                and bindings == other.bindings and f.edge == g.edge and f.right == g.left):
            raise _InvalidTrace("composition requires matching positive paths")
        kind = "star" if f.kind == g.kind == "star" else "plus"
        return [_Signed(ast.Reach(kind, f.edge, f.left, g.right), True, bindings)]
    if parameter is not None:
        raise _InvalidTrace("unexpected closure consequence parameter")
    if rule == "closure-edge@0" and pos and type(f) is ast.Binary:
        signature = branch.signatures.get(f.predicate)
        if signature is None or len(signature) != 2 or signature[0] != signature[1]:
            raise _InvalidTrace("edge inclusion requires a homogeneous signature")
        return [_Signed(ast.Reach("plus", ast.Named(f.predicate), f.left, f.right), True, bindings)]
    if type(f) is not ast.Reach:
        raise _InvalidTrace("closure consequence requires Reach")
    if rule == "closure-named-body@0" and type(f.edge) is ast.Named:
        sort = branch.parameters[_term_token(f.left, bindings)]
        if branch.signatures.get(f.edge.relation) != (sort, sort):
            raise _InvalidTrace("Named conversion requires a homogeneous signature")
        body = ast.Body(sort, ast.Binary(f.edge.relation, ast.Var(1), ast.Var(0)))
        return [_Signed(ast.Reach(f.kind, body, f.left, f.right), pos, bindings)]
    if rule in ("closure-first@0", "closure-last@0") and pos and f.kind == "plus":
        sort = branch.parameters[_term_token(f.left, bindings)]
        if ((type(f.edge) is ast.Named and branch.signatures.get(f.edge.relation) != (sort, sort))
                or (type(f.edge) is ast.Body and f.edge.sort != sort)):
            raise _InvalidTrace("end edge requires the path sort")
        shifted = shift(f)
        body = (edge_at(shifted.edge, ast.Var(0), shifted.right) if rule == "closure-last@0"
                else edge_at(shifted.edge, shifted.left, ast.Var(0)))
        return [_Signed(ast.Exists(sort, body), True, bindings)]
    raise _InvalidTrace("inapplicable closure consequence")


def extra_candidates(branch):
    """Untrusted candidate enumeration; the replayer checks every selected rule."""
    from .entailment import _InvalidTrace
    for at, item in enumerate(branch.formulas):
        rules = ("closure-edge@0",) if type(item.formula) is ast.Binary and item.positive else (
            ("closure-first@0", "closure-last@0", "closure-named-body@0")
            if type(item.formula) is ast.Reach else ())
        for rule in rules:
            try:
                yield rule, at, None, derive_extra(branch, rule, at, None)
            except _InvalidTrace:
                pass
        if type(item.formula) is ast.Reach and item.positive:
            for j, other in enumerate(branch.formulas):
                if type(other.formula) is not ast.Reach or not other.positive:
                    continue
                try:
                    yield "closure-compose@0", at, str(j), derive_extra(branch, "closure-compose@0", at, str(j))
                except _InvalidTrace:
                    pass
