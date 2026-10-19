"""The retained Python evaluator as a test oracle (lean-first batch 18).

The public `evaluate` and `check_countermodel` are Lean's since batch 18: there is no `python`
authority to select. The Python evaluator stays as the search's and the Background generators'
internal one (rule 3), so the differential tests that compared the two authorities compare Lean's
public answer with it here instead. Nothing here is a product path.
"""
from __future__ import annotations

from ve.ast import Document, check_document, check_formula
from ve.evaluate import _evaluate_validated, _validate_model
from ve.identity import meaning_id
from ve.search import CountermodelCheck, _check_countermodel_values, _premises


def evaluate(env, value, model, *, max_evaluations: int = 1_000_000, max_trace_nodes: int = 10_000,
             trace: bool = True):
    """Python's answer to `ve.evaluate.evaluate(env, value, model, ...)`."""
    if isinstance(value, Document):
        check_document(env, value)
        formulas = value.formulas
    else:
        check_formula(env, value)
        formulas = (value,)
    model = _validate_model(env, model)
    return _evaluate_validated(formulas, model, max_evaluations=max_evaluations,
                               max_trace_nodes=max_trace_nodes, trace=trace)


def check_countermodel(env, premises, conclusion, model, *, max_evaluations: int = 1_000_000):
    """Python's answer to `ve.search.check_countermodel(...)`: the same sequencing over Python's evaluator."""
    premises = _premises(premises)
    model = _validate_model(env, model)

    def python(formula, budget):
        return _evaluate_validated((formula,), model, max_evaluations=budget)

    valid, values, conclusion_value, work, status = _check_countermodel_values(
        premises, conclusion, model, max_evaluations, python)
    return CountermodelCheck(valid, values, conclusion_value, work, env.environment_id, model.model_id, status,
                             tuple(meaning_id(env, x) for x in premises), meaning_id(env, conclusion))
