"""Frozen Python regeneration oracle for conformance only."""
from ve.ast import _to_data, formula_to_data
from ve.background import background
from ve.errors import VEError
from conformance import frozen_norm_defaults as nd

def regeneration(document):
    """Python's outputs of `fill U`, in the fields and order of Lean `Wire.regeneratedU`."""
    filled, env = document.filled, document.filled.env
    base = filled.base_environment()
    regulated = sorted(p for p, d in document.env.predicates.items() if d.regulated is not None)
    return {
        "order": list(filled.order),
        "background": [{"generator": p.generator, "ast": formula_to_data(env, p.formula, _generated=True)}
                       for p in background(env)],
        "premises": [{"label": label, "ast": formula_to_data(env, formula, _generated=True)}
                     for label, formula in filled.premises()],
        "conflict_targets": [{"target": name, "sorts": list(sorts), "ast": _to_data(formula)}
                             for name, sorts, formula in filled.conflict_targets()],
        "fill": [{"generator": "fill", "ast": formula_to_data(base, formula, _generated=True)}
                 for _, formula in document.fill_premises],
        "unspecified": list(document.unspec),
        "unsaid": [{"name": nd.unsaid_name(p), "sorts": list(document.env.predicates[p].arguments),
                    "description": nd.fill_description(p)}
                   for p in document.unspec],
        "reached": [{"predicate": p, "sorts": list(document.env.predicates[p].arguments),
                     "ast": _to_data(document.reached(p))} for p in regulated],
    }

def check_regenerated(document, row):
    """Compare every output of Lean's `norm-defaults-elaborate` row with Python's."""
    for field, value in regeneration(document).items():
        if row.get(field) != value:
            raise VEError(f"norm-defaults route regeneration mismatch: {field}")
    return row
