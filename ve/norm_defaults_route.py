"""Python entry points for the Lean norm-defaults route (service mode `norm-defaults`)
(docs/spec/norm-defaults.md 3, 6 and 8).

Lean owns `fill U`, `Fill_T` and their identities (`elaborate`, the
`norm-defaults-elaborate` row) and replays every piece of evidence;
`admit_norm_defaults_document` relays W1's admission on `fill U` (Lean
`Admission.admitDocument`). `prove_filled_entailment` is an untrusted generator
whose certificate Lean replays.
"""
from __future__ import annotations

from .assurance import semantic_entry
from .backends.relay import decide, rows
from .ast import formula_to_data
from .background import background
from .environment import Environment
from .errors import CheckerUnavailable
from .wire import digest

def run_cases(cases):
    """Lean's rows for `cases`, in case order (rejections are rows)."""
    return rows("norm-defaults", cases)


def run_case(case):
    """Lean's row for one case; a rejection raises Lean's diagnostic."""
    return decide("norm-defaults", [case])[0]


def source_case(document, kind, **fields):
    """A case over `document`'s source environment and author norm objects."""
    return {"id": kind, "kind": kind, "environment": document.env.to_dict(),
            "norms": [rule.to_dict() for rule in document.author.rules], **fields}


def elaborate(document):
    """The Lean owner's regeneration of `fill U`."""
    return run_case(source_case(document, "norm-defaults-elaborate"))


# Entailment over `fill U` (Lean `Wire.replayEntailmentU`).

def _filled_premises(document, premises):
    """`Background(E‴) ++ Fill_T ++ T‴ ++ Γ`, with the generated flag of each."""
    env = document.filled.env
    generated = [p.formula for p in background(env)]
    regenerated = [f for _, f in document.fill_premises] + [f for _, f in document.filled.premises()]
    return ([(f, True) for f in generated] + [(f, True) for f in regenerated]
            + [(f, False) for f in premises])


def _source_binding(document, premises, conclusion):
    """The binding Lean checks: the source environment (profile included) by
    `ve.core@0.2` identity and the ASTs of the premise list and conclusion."""
    env, filled = document.env, document.filled.env

    def meaning(formula, generated):
        return digest(f"ve-meaning-{env.identity_version}\n",
                      {"environment_id": env.environment_id,
                       "ast": formula_to_data(filled, formula, _generated=generated)})
    return {"environment_id": env.environment_id,
            "premise_meaning_ids": [meaning(f, g) for f, g in _filled_premises(document, premises)],
            "conclusion_meaning_id": meaning(conclusion, False)}


def _filled_proof(document, premises, conclusion, **kwargs):
    """The untrusted prover on `Background(E‴) ++ Fill_T ++ T‴ ++ Γ ⊢ φ`. `document` needs `env` (the source
    environment), `fill_premises` and `filled` (`env`, `premises()`): an `UnspecifiedDocument`, or a view of a Lean
    row that carries them (a readings choice's filled document, `ve/readings_verdicts.py`)."""
    from .entailment import prove_entailment
    # The prover lists Background(E‴) first; the rest is Fill_T ++ T‴ ++ Γ.
    regenerated = [f for _, f in document.fill_premises] + [f for _, f in document.filled.premises()]
    return prove_entailment(document.filled.env, (*regenerated, *premises), conclusion, **kwargs)


def filled_certificate(document, premises, conclusion, **kwargs):
    """A certificate for `Background(E‴) ++ Fill_T ++ T‴ ++ Γ ⊢ φ`, bound to the source, or None when the prover
    finds none within its budget."""
    proof = _filled_proof(document, premises, conclusion, **kwargs)
    if proof.status != "Found":
        return None
    return {**proof.certificate, **_source_binding(document, premises, conclusion)}


def prove_filled_entailment(document, premises, conclusion, **kwargs):
    """A certificate for `Background(E‴) ++ Fill_T ++ T‴ ++ Γ ⊢ φ`, bound to the source."""
    proof = _filled_proof(document, premises, conclusion, **kwargs)
    if proof.status != "Found":
        # An exhausted generator yields no verdict (plan rule 3).
        raise CheckerUnavailable(f"CheckerUnavailable: no certificate: {proof.status}")
    return {**proof.certificate, **_source_binding(document, premises, conclusion)}


# W2 admission on `fill U` (spec 2.3 and 3.2; Lean `VE.NormDefaults.Admission`).

def fill_labels(document):
    """`Fill_T` premises under their wire labels (`unsaid:pair:<r>,<m>`)."""
    return dict(document.fill_premises)


def filled_environment_json(document):
    """The regenerated `E‴` JSON that admission certificates bind (Lean `fillJson`)."""
    return document.filled.env.to_dict()


@semantic_entry("admission")
def admit_norm_defaults_document(environment, document):
    """Relay W1 admission on `fill U` to the Lean owner."""
    env = environment if type(environment) is Environment else Environment(environment)
    answer = run_case({"id": "admission", "kind": "admission",
                       "environment": env.to_dict(), "document": document})
    return {key: value for key, value in answer.items() if key not in ("id", "status")}
