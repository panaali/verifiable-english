"""Fast countermodel search for ground (quantifier-free, equality-free) steps.

For closed quantifier-free formulas without equality, Herbrand models (one
entity per constant) are complete, so a propositional search over the ground
atoms suffices. This is only a SEARCH: every model it returns is re-checked by
``ve.search.check_countermodel`` before being reported, exactly as a model
from the generic bounded enumerator would be.
"""
from __future__ import annotations

from .. import ast
from ..model import FiniteModel

MAX_ATOMS = 64


def _atoms(formula, found):
    kind = type(formula)
    if kind in (ast.Top, ast.Bottom):
        return True
    if kind in (ast.Unary, ast.Binary):
        terms = (formula.term,) if kind is ast.Unary else (formula.left, formula.right)
        if any(type(t) is not ast.Const for t in terms):
            return False
        found.setdefault((formula.predicate, tuple(t.name for t in terms)), None)
        return True
    if kind is ast.Not:
        return _atoms(formula.body, found)
    if kind in (ast.And, ast.Or, ast.Implies):
        return _atoms(formula.left, found) and _atoms(formula.right, found)
    return False  # quantifiers, equality, closure: not handled here


def _value(formula, assignment):
    """Three-valued evaluation: True, False, or None (unassigned atom)."""
    kind = type(formula)
    if kind is ast.Top:
        return True
    if kind is ast.Bottom:
        return False
    if kind is ast.Unary:
        return assignment.get((formula.predicate, (formula.term.name,)))
    if kind is ast.Binary:
        return assignment.get((formula.predicate, (formula.left.name, formula.right.name)))
    if kind is ast.Not:
        v = _value(formula.body, assignment)
        return None if v is None else not v
    left = _value(formula.left, assignment)
    if kind is ast.And:
        if left is False:
            return False
        right = _value(formula.right, assignment)
        return False if right is False else (None if None in (left, right) else True)
    if kind is ast.Or:
        if left is True:
            return True
        right = _value(formula.right, assignment)
        return True if right is True else (None if None in (left, right) else False)
    if kind is ast.Implies:
        if left is False:
            return True
        right = _value(formula.right, assignment)
        if right is True:
            return True
        return None if None in (left, right) else False
    raise TypeError("unsupported ground formula")


def ground_countermodel(env, premises, conclusion):
    """Return (status, model): ('Found', FiniteModel), ('NotFound', None) or ('Unsupported', None).

    'NotFound' means no Herbrand countermodel exists, i.e. the ground step is
    valid; callers still require a replayed tableau certificate for 'follows'.
    """
    atoms = {}
    formulas = (*premises, ast.Not(conclusion))
    if not all(_atoms(f, atoms) for f in formulas) or len(atoms) > MAX_ATOMS:
        return "Unsupported", None
    order = list(atoms)
    assignment = {}

    def search(index):
        values = [_value(f, assignment) for f in formulas]
        if False in values:
            return False
        if all(v is True for v in values):
            return True
        if index == len(order):
            return False
        for choice in (True, False):
            assignment[order[index]] = choice
            if search(index + 1):
                return True
            del assignment[order[index]]
        return False

    if not search(0):
        return "NotFound", None
    # Unassigned atoms are irrelevant; leave them false.
    names = sorted(env.constants)
    domains = {sort: [] for sort in env.sorts}
    constants = {}
    for i, name in enumerate(names):
        entity = f"e{i}"
        domains[env.constants[name].sort].append(entity)
        constants[name] = entity
    relations = {name: [] for name in env.predicates}
    for (predicate, args), value in assignment.items():
        if value:
            relations[predicate].append([constants[a] for a in args])
    model = FiniteModel.from_dict(env, {"complete": True, "domains": domains,
                                        "constants": constants, "relations": relations})
    return "Found", model
