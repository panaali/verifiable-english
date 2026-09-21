"""Executable versions of the debate protocol's worked examples.

These fixtures deliberately keep logical certification separate from empirical
evidence.  In particular, the merged-vocabulary graph is logically valid even
though its two leaves cite records with incompatible review scopes.
"""
from __future__ import annotations

import hashlib

from .argument import ArgumentGraph, Claim, Deduction, Evidence
from .environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from .model import FiniteModel


DEPLOYED_TO_OPS = "for every service s, (if (s is deployed), then (s is ops_reviewed)).\n"
SECURITY_TO_APPROVED = (
    "for every service s, (if (s is security_reviewed), then (s is approved)).\n"
)
OPS_TO_SECURITY = (
    "for every service s, (if (s is ops_reviewed), then (s is security_reviewed)).\n"
)
DEPLOYED_TO_REVIEWED = "for every service s, (if (s is deployed), then (s is reviewed)).\n"
REVIEWED_TO_APPROVED = "for every service s, (if (s is reviewed), then (s is approved)).\n"
DEPLOYED_TO_APPROVED = "for every service s, (if (s is deployed), then (s is approved)).\n"


def _environment(*, merged: bool) -> Environment:
    predicates = {
        "deployed": {"arguments": ["service"], "description": "Recorded as deployed."},
        "approved": {"arguments": ["service"], "description": "Recorded as approved."},
    }
    if merged:
        predicates["reviewed"] = {
            "arguments": ["service"],
            "description": "Recorded as reviewed.",
        }
    else:
        predicates.update({
            "ops_reviewed": {
                "arguments": ["service"],
                "description": "Recorded as reviewed by operations.",
            },
            "security_reviewed": {
                "arguments": ["service"],
                "description": "Recorded as reviewed under the security policy.",
            },
        })
    return Environment.from_dict({
        "language": LANGUAGE,
        "profile": PROFILE,
        "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {"service": {"description": "A service recorded in the inventory."}},
            "predicates": predicates,
            "constants": {},
        },
    })


def _snapshot_id(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _evidence(evidence_id: str, claim: Claim, content: str, passage: str, scope: str,
              *, judgment: str = "accepted") -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        claim_id=claim.claim_id,
        snapshot_id=_snapshot_id(content),
        passage=passage,
        reviewer="u1",
        target_scope=scope,
        judgment=judgment,
        kind="empirical",
    )


def separated_vocabulary_example() -> ArgumentGraph:
    """The invalid substitution, with the protocol's one-service countermodel."""
    env = _environment(merged=False)
    ops = Claim.create(env, "c1", DEPLOYED_TO_OPS)
    policy = Claim.create(env, "c2", SECURITY_TO_APPROVED)
    root = Claim.create(env, "c3", DEPLOYED_TO_APPROVED)
    model = FiniteModel.from_dict(env, {
        "complete": True,
        "domains": {"service": ["api"]},
        "constants": {},
        "relations": {
            "approved": [],
            "deployed": [["api"]],
            "ops_reviewed": [["api"]],
            "security_reviewed": [],
        },
    })
    edge = Deduction("e1", (ops.name, policy.name), root.name,
                     countermodels=(model,))
    return ArgumentGraph(env, (ops, policy, root), (edge,), root.name,
                         target_scope="security-policy approval review")


def explicit_bridge_example() -> ArgumentGraph:
    """The repaired split-vocabulary inference; the bridge stays a visible leaf."""
    env = _environment(merged=False)
    ops = Claim.create(env, "c1", DEPLOYED_TO_OPS)
    policy = Claim.create(env, "c2", SECURITY_TO_APPROVED)
    bridge = Claim.create(env, "c4", OPS_TO_SECURITY,
                          evidence_ids=("r1",))
    root = Claim.create(env, "c3", DEPLOYED_TO_APPROVED)
    bridge_record = "No external record establishes that operations review satisfies security review."
    evidence = _evidence(
        "r1", bridge, bridge_record, bridge_record,
        "relationship between operations and security review",
        judgment="unassessed",
    )
    edge = Deduction("e1", (ops.name, bridge.name, policy.name), root.name)
    return ArgumentGraph(env, (ops, policy, bridge, root), (edge,), root.name,
                         evidence=(evidence,), target_scope="security-policy approval review")


def merged_vocabulary_example() -> ArgumentGraph:
    """A valid logical composition whose evidence silently changes review scope."""
    env = _environment(merged=True)
    operations_record = "Operations register: api passed deployment readiness review."
    security_record = "Security policy: a reviewed service is eligible for approval."
    first = Claim.create(env, "c1", DEPLOYED_TO_REVIEWED,
                         evidence_ids=("r1",))
    second = Claim.create(env, "c2", REVIEWED_TO_APPROVED,
                          evidence_ids=("r2",))
    root = Claim.create(env, "c3", DEPLOYED_TO_APPROVED)
    evidence = (
        _evidence("r1", first, operations_record, operations_record,
                  "operations deployment-readiness review records"),
        _evidence("r2", second, security_record, security_record,
                  "security-policy approval review"),
    )
    edge = Deduction("e1", (first.name, second.name), root.name)
    return ArgumentGraph(env, (first, second, root), (edge,), root.name, evidence=evidence,
                         target_scope="security-policy approval review")


def infinite_only_example() -> ArgumentGraph:
    """A satisfiable premise set with only infinite models.

    This is the language specification's reminder that bounded finite search is
    incomplete: the edge to ``false`` is invalid, but has no finite witness.
    """
    env = Environment.from_dict({
        "language": LANGUAGE,
        "profile": PROFILE,
        "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {"item": {"description": "An item in an ordered collection."}},
            "predicates": {
                "precedes": {
                    "arguments": ["item", "item"],
                    "description": "The first item strictly precedes the second.",
                },
            },
            "constants": {},
        },
    })
    sources = (
        ("c1", "there exists item a, (true).\n"),
        ("c2", "for every item a, (not (a precedes a)).\n"),
        ("c3", "for every item a, (for every item b, (for every item c, "
         "(if ((a precedes b) and (b precedes c)), then (a precedes c)))).\n"),
        ("c4", "for every item a, (there exists item b, (a precedes b)).\n"),
    )
    premises = tuple(Claim.create(env, name, source) for name, source in sources)
    conclusion = Claim.create(env, "c5", "false.\n")
    edge = Deduction("e1", tuple(c.name for c in premises),
                     conclusion.name)
    return ArgumentGraph(env, premises + (conclusion,), (edge,), conclusion.name,
                         target_scope="ordered collection")


def worked_examples() -> dict[str, ArgumentGraph]:
    """Return fresh graphs for every worked case in the debate protocol."""
    return {
        "g1": separated_vocabulary_example(),
        "g2": explicit_bridge_example(),
        "g3": merged_vocabulary_example(),
    }


__all__ = [
    "explicit_bridge_example",
    "infinite_only_example",
    "merged_vocabulary_example",
    "separated_vocabulary_example",
    "worked_examples",
]


if __name__ == "__main__":
    import json
    from .argument import check_argument, outstanding_obligations, predicate_use_panel

    output = {}
    for name, graph in worked_examples().items():
        result = check_argument(graph)
        output[name] = {"check": result.to_dict(),
                        "outstanding_obligations": outstanding_obligations(graph, result),
                        "predicate_use_panel": predicate_use_panel(graph, result)}
    print(json.dumps(output, sort_keys=True, indent=2))
