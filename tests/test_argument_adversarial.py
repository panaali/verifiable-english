"""Adversarial binding, composition, and resource tests for argument packages."""
from dataclasses import replace

import pytest

from ve.argument import (ArgumentGraph, Claim, Deduction, Evidence, check_argument,
                         deduction_identity, outstanding_obligations,
                         predicate_use_panel)
from ve.ast import Not
from ve.entailment import prove_entailment
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.errors import VEError
from ve.model import FiniteModel


def env(*, description="P means the reviewed property."):
    return Environment.from_dict({
        "language": LANGUAGE, "profile": PROFILE, "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {"item": {"description": "An item."}},
            "predicates": {
                "p": {"arguments": ["item"], "description": description},
                "q": {"arguments": ["item"], "description": "Q."},
            },
            "constants": {"a": {"sort": "item", "description": "The item a."}},
        },
    })


P = "@a is p.\n"
Q = "@a is q.\n"


def claims(e):
    return Claim.create(e, "premise", P), Claim.create(e, "root", P)


def certified_graph():
    e = env()
    premise, root = claims(e)
    bare = ArgumentGraph(e, (premise, root),
                         (Deduction("step", (premise.name,), root.name),), root.name)
    edge = bare.deductions[0]
    proof = prove_entailment(e, (premise.ast,), root.ast)
    assert proof.status == "Found"
    envelope = {"edge_id": deduction_identity(bare, edge), "direction": "follows",
                "proof": proof.certificate}
    return ArgumentGraph(e, bare.claims,
                         (replace(edge, certificates=(envelope,)),), bare.root)


@pytest.mark.parametrize("field,value", [
    ("source_id", "0" * 64),
    ("meaning_id", "0" * 64),
    ("environment_id", "0" * 64),
    ("source", Q),
])
def test_direct_claim_substitution_is_rejected(field, value):
    e = env()
    premise, root = claims(e)
    forged = replace(premise, **{field: value})
    graph = ArgumentGraph(e, (forged, root),
                          (Deduction("step", (forged.name,), root.name),), root.name)
    result = check_argument(graph, search=False)
    assert result.status == "InvalidInput"
    assert not result.composed


def test_ast_source_mismatch_is_rejected_on_wire_decode():
    graph = certified_graph()
    wire = graph.to_dict()
    wire["claims"][0]["ast"] = wire["claims"][1]["ast"] = ["unary", "q", ["const", "a"]]
    with pytest.raises(VEError, match="does not match|stale|substituted"):
        ArgumentGraph.from_dict(wire)


def test_same_symbols_under_changed_environment_invalidate_package_and_proof():
    graph = certified_graph()
    other = env(description="P has a newly substituted meaning.")
    transplanted = ArgumentGraph(other, graph.claims, graph.deductions, graph.root)
    result = check_argument(transplanted, search=False)
    assert result.status == "InvalidInput"
    assert not result.findings


def test_certificate_envelope_is_bound_to_edge_identity_and_premise_order():
    e = env()
    first = Claim.create(e, "first", P)
    second = Claim.create(e, "second", "true.\n")
    root = Claim.create(e, "root", P)
    original = ArgumentGraph(e, (first, second, root),
        (Deduction("step", (first.name, second.name), root.name),), root.name)
    proof = prove_entailment(e, (first.ast, second.ast), root.ast)
    envelope = {"edge_id": deduction_identity(original, original.deductions[0]),
                "direction": "follows", "proof": proof.certificate}
    reordered = ArgumentGraph(e, original.claims,
        (Deduction("step", (second.name, first.name), root.name,
                   certificates=(envelope,)),), root.name)
    result = check_argument(reordered, search=False)
    assert result.status == "InvalidInput"
    assert result.findings["step"] == ("unresolved",) or result.findings["step"] == ()
    assert not result.composed


def test_proof_with_an_extra_hidden_assumption_cannot_certify_edge():
    e = env()
    shown = Claim.create(e, "shown", "true.\n")
    hidden = Claim.create(e, "hidden", P)
    root = Claim.create(e, "root", P)
    graph = ArgumentGraph(e, (shown, hidden, root),
                          (Deduction("step", (shown.name,), root.name),), root.name)
    proof = prove_entailment(e, (shown.ast, hidden.ast), root.ast)
    assert proof.status == "Found"
    envelope = {"edge_id": deduction_identity(graph, graph.deductions[0]),
                "direction": "follows", "proof": proof.certificate}
    submitted = replace(graph, deductions=(replace(graph.deductions[0],
                                                    certificates=(envelope,)),))
    result = check_argument(submitted, search=False)
    assert result.status == "InvalidInput"
    assert not result.composed
    assert "follows" not in result.findings["step"]


def test_cycles_and_self_support_are_rejected_even_outside_root_component():
    e = env()
    a = Claim.create(e, "a_claim", P)
    b = Claim.create(e, "b_claim", P)
    root = Claim.create(e, "root", "true.\n")
    cycle = ArgumentGraph(e, (a, b, root), (
        Deduction("to_a", (b.name,), a.name),
        Deduction("to_b", (a.name,), b.name),
    ), root.name)
    assert check_argument(cycle, search=False).status == "InvalidInput"
    self_cycle = ArgumentGraph(e, (a,), (Deduction("self_step", (a.name,), a.name),), a.name)
    assert check_argument(self_cycle, search=False).status == "InvalidInput"


def test_composition_retains_only_actual_undischarged_leaves():
    e = env()
    leaf = Claim.create(e, "leaf", P)
    unused = Claim.create(e, "unused", Q)
    middle = Claim.create(e, "middle", P)
    root = Claim.create(e, "root", P)
    graph = ArgumentGraph(e, (leaf, unused, middle, root), (
        Deduction("derive_middle", (leaf.name,), middle.name),
        Deduction("derive_root", (middle.name,), root.name),
    ), root.name)
    result = check_argument(graph)
    assert result.status == "Checked" and result.composed
    assert result.remaining_assumptions == ("leaf",)
    assert result.composition["assumption_claim_ids"] == [leaf.claim_id]
    assert unused.claim_id not in result.composition["assumption_claim_ids"]


def test_stale_evidence_binding_and_cross_claim_citation_are_rejected():
    e = env()
    premise = Claim.create(e, "premise", P)
    root = Claim.create(e, "root", Q)
    evidence = Evidence("record", premise.claim_id, "sha256:abc", "page 1", "reviewer",
                        "test scope", "accepted", "empirical")
    stale = replace(evidence, passage="substituted passage")
    cited = replace(premise, evidence_ids=(evidence.evidence_id,))
    base = ArgumentGraph(e, (cited, root), (), root.name, evidence=(stale,))
    assert check_argument(base, search=False).status == "InvalidInput"
    wrong_claim = replace(evidence, claim_id=root.claim_id,
                          assessment_binding="")
    wrong_claim = replace(wrong_claim, assessment_binding=wrong_claim.expected_binding())
    cross = replace(base, evidence=(wrong_claim,))
    assert check_argument(cross, search=False).status == "InvalidInput"


def test_untrusted_malformed_certificate_is_diagnostic_not_an_exception():
    e = env()
    premise, root = claims(e)
    malformed_values = (None, [], {"edge_id": 1, "direction": "follows", "proof": {}},
                        {"edge_id": "x", "direction": "execute", "proof": {}})
    for malformed in malformed_values:
        graph = ArgumentGraph(e, (premise, root),
            (Deduction("step", (premise.name,), root.name,
                       certificates=(malformed,)),), root.name)
        result = check_argument(graph, search=False)
        assert result.status == "InvalidInput"
        assert not result.composed


def test_zero_search_limits_are_resource_exhaustion_not_logical_findings():
    e = env()
    premise = Claim.create(e, "premise", P)
    root = Claim.create(e, "root", Q)
    graph = ArgumentGraph(e, (premise, root),
                          (Deduction("step", (premise.name,), root.name),), root.name)
    result = check_argument(graph, max_proof_steps=0, max_domain_size=0,
                            max_models=0, max_evaluations=0)
    assert result.status == "ResourceLimit"
    assert result.findings["step"] == ()
    assert result.edges[0]["status"] == "unresolved"
    assert not result.composed
    attempts = {a["kind"]: a["status"] for a in result.edges[0]["search_attempts"]}
    assert attempts == {"follows": "ResourceLimit", "refuted": "ResourceLimit", "gap": "NotFound"}
    # The size-zero finite space has no models because @a inhabits item.
    # Its vacuous exhaustion remains inconclusive and is not a search timeout.


def test_submitted_countermodel_evaluation_limit_is_resource_not_invalid_input():
    e = env()
    premise = Claim.create(e, "premise", P)
    root = Claim.create(e, "root", Q)
    model = FiniteModel.from_dict(e, {"complete": True, "domains": {"item": ["x"]},
        "constants": {"a": "x"}, "relations": {"p": [["x"]], "q": []}})
    graph = ArgumentGraph(e, (premise, root),
        (Deduction("step", (premise.name,), root.name, countermodels=(model,)),), root.name)
    result = check_argument(graph, search=False, max_evaluations=0)
    assert result.status == "ResourceLimit"
    assert result.findings["step"] == ()
    assert result.edges[0]["status"] == "unresolved"


def test_checker_conflict_retains_both_artifacts_and_withholds_composition(monkeypatch):
    """Inject a contradictory checker output; real sound checkers cannot produce it."""
    e = env()
    premise = Claim.create(e, "premise", P)
    root = Claim.create(e, "root", Q)
    model = FiniteModel.from_dict(e, {"complete": True, "domains": {"item": ["x"]},
        "constants": {"a": "x"}, "relations": {"p": [["x"]], "q": []}})
    bare_edge = Deduction("step", (premise.name,), root.name, countermodels=(model,))
    bare = ArgumentGraph(e, (premise, root), (bare_edge,), root.name)
    envelope = {"edge_id": deduction_identity(bare, bare_edge), "direction": "follows",
                "proof": {}}
    graph = replace(bare, deductions=(replace(bare_edge, certificates=(envelope,)),))

    class InjectedValid:
        valid = True
        status = "Valid"
        def to_dict(self):
            return {"valid": True, "status": "Valid", "steps": 0, "detail": "injected"}

    monkeypatch.setattr("ve.entailment.check_entailment_certificate",
                        lambda *args, **kwargs: InjectedValid())
    result = check_argument(graph, search=False)
    assert result.status == "CheckerConflict"
    assert result.findings["step"] == ("follows", "gap")
    assert not result.composed
    assert {artifact["kind"] for artifact in result.edges[0]["artifacts"]} == {
        "follows", "gap",
    }


def test_display_rejects_stale_check_record():
    graph = certified_graph()
    result = check_argument(graph, search=False)
    changed = replace(graph, target_scope="different deployment")
    with pytest.raises(VEError, match="stale"):
        outstanding_obligations(changed, result)
    with pytest.raises(VEError, match="stale"):
        predicate_use_panel(changed, result)


def test_boolean_budget_is_not_silently_treated_as_one():
    result = check_argument(certified_graph(), max_proof_steps=True)
    assert result.status == "InvalidInput"
