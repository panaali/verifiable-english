"""W2 admission for documents containing active W1 norm units, relayed to Lean's norms route.

Norm content remains a norm object in the source document. The only admitted
layer leaves are the premises Lean regenerates from the active units; claim
checking, citation closure and report identity are Lean's (lean-first batch 13b).
"""
from __future__ import annotations

from dataclasses import replace

from .assurance import semantic_entry
from .environment import Environment
from .norms import NormDocument


def _check_quoted(env, content):
    """A quoted norm never contributes a layer, but it is still a norm object
    over this environment: every single-rule check applies. Its precedence
    edges name rules of the quoted source, so they are not resolved here."""
    rule = NormDocument._decode(content)
    NormDocument(env, [replace(rule, over=())])


@semantic_entry("admission")
def admit_norm_document(environment, document):
    """Admit a document containing norm units: Lean's norms route decides under every authority
    (lean-first batch 13b)."""
    from .backends.dispatch import owned
    from .backends.relay import decide
    from .errors import CheckerUnavailable
    env = environment if type(environment) is Environment else Environment(environment)
    if env.alternatives is not None:
        from .admission import admit_document
        return admit_document(env, document)
    case = {"id": "admission", "kind": "admission", "environment": env.to_dict(), "document": document}

    def lean():
        row = decide("norms", [case])[0]
        if set(row) != {"id", "status", "admitted", "report", "report_id", "kinds"} or row["admitted"] is not True:
            raise CheckerUnavailable("CheckerUnavailable: malformed Lean norms admission result")
        return {key: row[key] for key in ("admitted", "report", "report_id", "kinds")}

    return owned("norms_admission", lean)
