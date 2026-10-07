"""Three-valued finite satisfiability report for a premise set."""
from __future__ import annotations

from .assurance import semantic_entry
from .ast import Bottom
from .entailment import check_entailment_certificate, prove_entailment
from .search import check_countermodel, find_countermodel


@semantic_entry("premise-status")
def premise_status(env, premises, *, max_proof_steps=10_000, max_domain_size=2,
                   max_models=10_000, max_evaluations=100_000):
    """Return a model, a replayed contradiction certificate, or UNKNOWN.

    A relabelling of one checked result: `INCONSISTENT` is one replayed
    certificate of ⊥, `model` one checked model of the premises. The prover and
    the model search are untrusted generators. Under a backend authority the
    replay and the model check run on that backend (`dispatch.composed`).
    """
    from .backends.dispatch import composed, execute
    budgets = {"max_proof_steps": max_proof_steps, "max_domain_size": max_domain_size,
               "max_models": max_models, "max_evaluations": max_evaluations}

    def run():
        return _premise_status(env, premises, **budgets)

    payload = {"environment_id": getattr(env, "environment_id", None), **budgets}
    return execute("premise_status", payload, run, lean=composed("lean", run),
                   rust=composed("rust-experimental", run))


def search_premise_status_witness(env, premises):
    """Untrusted search proposal for an already expanded Lean premise list.

    The speech source route replays the returned model or certificate before
    publishing a status. This does not decide whether the evidence is valid.
    """
    return _premise_status(env, premises, max_proof_steps=10_000, max_domain_size=2,
                           max_models=10_000, max_evaluations=100_000,
                           include_witness=True, expanded=True)


def _premise_status(env, premises, *, max_proof_steps, max_domain_size, max_models, max_evaluations,
                    include_witness=False, expanded=False):
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
    found = find_countermodel(env, premises, Bottom(), max_domain_size=max_domain_size,
                              max_models=max_models, max_evaluations=max_evaluations)
    if found.status == "Found":
        witness = check_countermodel(env, premises, Bottom(), found.model,
                                     max_evaluations=max_evaluations)
        if witness.valid:
            result = {"status": "model", "model_id": found.model.model_id}
            if include_witness:
                result["model"] = found.model.to_dict()
            return result
    if max_proof_steps > 128:
        full = contradiction(max_proof_steps)
        if full is not None:
            return full
    return {"status": "UNKNOWN", "budget": {"max_proof_steps": max_proof_steps,
            "max_domain_size": max_domain_size, "max_models": max_models,
            "max_evaluations": max_evaluations}}
