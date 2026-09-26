"""Three-valued finite satisfiability report for a premise set."""
from __future__ import annotations

from .ast import Bottom
from .entailment import check_entailment_certificate, prove_entailment
from .search import check_countermodel, find_countermodel


def premise_status(env, premises, *, max_proof_steps=10_000, max_domain_size=2,
                   max_models=10_000, max_evaluations=100_000):
    """Return a model, a replayed contradiction certificate, or UNKNOWN."""
    def contradiction(budget):
        proof = prove_entailment(env, premises, Bottom(), max_steps=budget)
        if proof.status == "Found":
            replay = check_entailment_certificate(env, premises, Bottom(), proof.certificate,
                                                  max_steps=budget)
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
            return {"status": "model", "model_id": found.model.model_id}
    if max_proof_steps > 128:
        full = contradiction(max_proof_steps)
        if full is not None:
            return full
    return {"status": "UNKNOWN", "budget": {"max_proof_steps": max_proof_steps,
            "max_domain_size": max_domain_size, "max_models": max_models,
            "max_evaluations": max_evaluations}}
