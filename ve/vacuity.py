"""Three-valued finite satisfiability report for a premise set."""
from __future__ import annotations

from .assurance import semantic_entry
from .ast import Bottom
from .entailment import check_entailment_certificate, prove_entailment
from .backends.rust_jsonl import RustTimeout
from .search import check_countermodel, find_countermodel, lean_budget, premise_budget


@semantic_entry("premise-status")
def premise_status(env, premises, *, max_proof_steps=None, max_domain_size=None,
                   max_models=None, max_evaluations=None):
    """Return a model, a replayed contradiction certificate, or UNKNOWN.

    A relabelling of one checked result: `INCONSISTENT` is one replayed
    certificate of ⊥, `model` one checked model of the premises. The prover and
    the model search are untrusted generators; the replay and the model check
    run on Lean under every authority (lean-first batch 13b).

    The budgets are Lean's (`ve.search.premise_budget`, premise-scale): a budget the caller
    leaves out is Lean's, and with Lean's domain bound come the sorts Lean raises above it.
    """
    from .backends.dispatch import owned
    budgets = {"max_proof_steps": max_proof_steps, "max_domain_size": max_domain_size,
               "max_models": max_models, "max_evaluations": max_evaluations}

    def run():
        return _premise_status(env, premises, **_budgets(env, premises, budgets))

    from .entailment import lean_check_scope
    return owned("premise_status", run) if lean_check_scope(env) else run()


def _budgets(env, premises, given):
    """The caller's budgets, Lean's for those left out; Lean's sort bounds with Lean's domain bound."""
    sort_bounds = {}
    if any(value is None for value in given.values()):
        lean = premise_budget(env, premises)
        given = {k: getattr(lean, k) if v is None else v for k, v in given.items()}
        if given["max_domain_size"] == lean.max_domain_size:
            sort_bounds = lean.sort_bounds
    return {**given, "sort_bounds": sort_bounds}


def search_premise_status_witness(env, premises):
    """Untrusted search proposal for an already expanded Lean premise list.

    The speech source route replays the returned model or certificate before
    publishing a status. This does not decide whether the evidence is valid.
    """
    budget = lean_budget()
    return _premise_status(env, premises, max_proof_steps=budget.max_proof_steps,
                           max_domain_size=budget.max_domain_size, max_models=budget.max_models,
                           max_evaluations=budget.max_evaluations, sort_bounds={},
                           include_witness=True, expanded=True)


def _search(env, premises, **options):
    """A Lean-checked model of `premises` from Rust's search, or None. A Rust call that times out
    is no witness: the premise check's answer is then Lean's alone (DRI decision ME1)."""
    try:
        found = find_countermodel(env, premises, Bottom(), **options)
    except RustTimeout:
        return None
    return found.model if found.status == "Found" else None


def _premise_status(env, premises, *, max_proof_steps, max_domain_size, max_models, max_evaluations,
                    sort_bounds, include_witness=False, expanded=False):
    def contradiction(budget):
        proof = prove_entailment(env, premises, Bottom(), max_steps=budget, _background=not expanded)
        if proof.status == "Found":
            replay = check_entailment_certificate(env, premises, Bottom(), proof.certificate,
                                                  max_steps=budget, _background=not expanded)
            if replay.valid:
                return {"status": "INCONSISTENT", "certificate": proof.certificate}
        return None

    quick = contradiction(min(max_proof_steps, 128))
    if quick is not None:
        return quick
    options = {"max_domain_size": max_domain_size, "max_models": max_models, "max_evaluations": max_evaluations,
               "sort_bounds": sort_bounds}
    # The search, then the ground-fact route: the premises' stated facts as their own model (premise-scale).
    for ground_only in (False, True):
        model = _search(env, premises, **options, ground_only=ground_only)
        if model is not None:
            witness = check_countermodel(env, premises, Bottom(), model, max_evaluations=max_evaluations)
            if witness.valid:
                result = {"status": "model", "model_id": model.model_id}
                if include_witness:
                    result["model"] = model.to_dict()
                return result
    if max_proof_steps > 128:
        full = contradiction(max_proof_steps)
        if full is not None:
            return full
    budget = {"max_proof_steps": max_proof_steps, "max_domain_size": max_domain_size, "max_models": max_models,
              "max_evaluations": max_evaluations}
    if sort_bounds:
        budget["sort_bounds"] = {k: list(v) for k, v in sort_bounds.items()}
    return {"status": "UNKNOWN", "budget": budget}
