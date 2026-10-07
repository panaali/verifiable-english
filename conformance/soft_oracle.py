"""Frozen Python regeneration comparison for the pre-deletion soft oracle.

This module is used only by conformance, never by the product relay.
"""
from __future__ import annotations

from ve.ast import _Checker, _to_data, formula_to_data
from ve.background import background
from ve.errors import VEError

def _open_data(env, formula, sorts):
    """An open generated formula over a tuple of `sorts`, serialised through the checker."""
    _Checker(env, generated=True).formula(formula, tuple(reversed(sorts)))
    return _to_data(formula)


def check_regenerated(soft_document: SoftNormDocument, elaborated):
    """Compare every output of Lean's `soft-elaborate` row with Python's regeneration.

    Every generated formula is serialised through the checker's limits; an
    accepted document is within them (validation table 6.4 and 6.9 to 6.15)."""
    if soft_document.extended_env.to_dict() != elaborated["environment_prime"]:
        raise VEError("soft route regeneration mismatch: extended environment")
    decisions = {item["name"] for item in elaborated["decisions"]}
    if decisions != soft_document.extended_env.decision_names:
        raise VEError("soft route regeneration mismatch: decision predicates")
    env, doc = soft_document.extended_env, soft_document.elaborated
    py_derived = []
    for rule, prime in zip(soft_document.rules, doc.rules, strict=True):
        derived = prime.unless[-1] if len(prime.unless) > len(rule.core.unless) else None
        py_derived.append({"rule": rule.core.name, "ast": None if derived is None else _open_data(
            env, derived, env.predicates[rule.core.predicate].arguments)})
    if py_derived != elaborated["derived"]:
        raise VEError("soft route regeneration mismatch: derived carve-outs")
    if list(doc.order) != elaborated["order"]:
        raise VEError("soft route regeneration mismatch: layer order")
    py_pairs = [([left.core.name, right.core.name], label, formula_to_data(env, formula, _generated=True))
                for (left, right), (label, formula) in zip(soft_document.collisions,
                                                           soft_document.coherence_premises, strict=True)]
    if py_pairs != [(item["pair"], item["label"], item["ast"]) for item in elaborated["colliding_pairs"]]:
        raise VEError("soft route regeneration mismatch: colliding pairs")
    base = doc.base_environment()
    py_targets = [(name, list(sorts), _open_data(base, formula, sorts))
                  for name, sorts, formula in doc.conflict_targets()]
    if py_targets != [(item["target"], item["sorts"], item["ast"])
                      for item in elaborated["conflict_targets"]]:
        raise VEError("soft route regeneration mismatch: conflict targets")
    py_layers = [(label, formula_to_data(soft_document.extended_env, formula, _generated=True))
                 for label, formula in soft_document.elaborated.premises()]
    lean_layers = [(item["label"], item["ast"]) for item in elaborated["premises"]]
    if py_layers != lean_layers:
        raise VEError("soft route regeneration mismatch: norm layers")
    py_soft = [(label, formula_to_data(soft_document.extended_env, formula, _generated=True))
               for label, formula in soft_document.extended_env.soft_premises]
    lean_soft = [(item["label"], item["ast"]) for item in elaborated["background"]
                 if item.get("generator") == "soft"]
    if py_soft != lean_soft:
        raise VEError("soft route regeneration mismatch: soft background")
    # The soft route checks the correlated soft document. Rights limitation
    # premises are checked by the rights route over the same base vocabulary.
    py_background = [(premise.generator, formula_to_data(env, premise.formula, _generated=True))
                     for premise in background(env) if premise.generator != "rights"]
    if py_background != [(item["generator"], item["ast"]) for item in elaborated["background"]]:
        raise VEError("soft route regeneration mismatch: background")
    if list(soft_document.warnings) != elaborated["warnings"]:
        raise VEError("soft route regeneration mismatch: warnings")
    return elaborated
