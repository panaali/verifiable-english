from dataclasses import replace
import json

import pytest

from ve import (ArgumentGraph, Claim, Deduction, Evidence, Environment, FiniteModel,
                check_argument, deduction_identity, outstanding_obligations,
                predicate_use_panel)
from ve.errors import VEError
from ve.argument_fixtures import merged_vocabulary_example, separated_vocabulary_example
from ve.entailment import EntailmentCertificateCheck


def simple(sources, edges, root):
    env = Environment.from_dict({"language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20", "vocabulary": {
            "sorts": {}, "predicates": {}, "constants": {}}})
    claims = tuple(Claim.create(env, name, source) for name, source in sources.items())
    return ArgumentGraph(env, claims, tuple(Deduction(*edge) for edge in edges), root)


def certified(graph):
    checked = check_argument(graph)
    edges = []
    for edge, record in zip(graph.deductions, checked.edges, strict=True):
        certs = tuple(a["certificate"] for a in record["artifacts"] if "certificate" in a)
        edges.append(replace(edge, certificates=certs))
    return replace(graph, deductions=tuple(edges))


def test_committed_graph_and_generated_certificates_roundtrip_and_replay():
    graph = certified(merged_vocabulary_example())
    clone = ArgumentGraph.from_json(graph.to_json())
    assert clone == graph
    result = check_argument(clone, search=False)
    assert result.status == "Checked" and result.composed
    assert result.remaining_assumptions == ("c1", "c2")
    data = json.loads(result.to_json())
    assert len(data["checker_build"]) == 64
    assert len(data["record_id"]) == 64
    assert data["approval"] == "unassessed"
    assert len(data["composition"]["assumption_claim_ids"]) == 2


def test_composition_of_shared_dag_preserves_leaves_once():
    graph = simple({"a": "true.\n", "b": "true.\n", "c": "true.\n", "root": "true.\n"},
                   [("ab", ("a",), "b"), ("ac", ("a",), "c"),
                    ("bcroot", ("b", "c"), "root")], "root")
    result = check_argument(graph)
    assert result.composed and result.remaining_assumptions == ("a",)
    assert len(result.composition["supporting_edge_ids"]) == 3


def test_assuming_root_does_not_discharge_it():
    graph = simple({"answer": "false.\n"}, [], "answer")
    result = check_argument(graph)
    assert result.composed
    assert result.remaining_assumptions == ("answer",)
    display = outstanding_obligations(graph, result)
    assert display["assumptions"][0]["outstanding"]
    assert display["interpretation"]["outstanding"]
    assert display["approval"] == "unassessed"


def test_data_background_composes_and_renders_with_generated_string_binders():
    from tests.test_data_flags import environment
    from ve.ast import formula_to_data
    from ve.background import background
    from ve.identity import meaning_id

    env = environment()
    graph = ArgumentGraph(env, (Claim.create(env, "root", "true.\n"),), (), "root")
    result = check_argument(graph, search=False)
    assert result.status == "Checked" and result.composed
    premises = background(env)
    rows = result.composition["assumptions"]
    assert len(rows) == 1 + len(premises)
    for row, premise in zip(rows[1:], premises, strict=True):
        assert row["label"] == "background:" + premise.generator
        assert row["ast"] == formula_to_data(env, premise.formula, _generated=True)
        assert row["meaning_id"] == meaning_id(env, premise.formula, _generated=True)
    assert [row["ast"] for row in outstanding_obligations(graph, result)["assumptions"][1:]] == [
        row["ast"] for row in rows[1:]]


def test_unchecked_intermediate_is_obligation_not_leaf():
    graph = simple({"leaf": "true.\n", "middle": "false.\n", "root": "true.\n"},
        [("bad", ("leaf",), "middle"), ("final", ("middle",), "root")], "root")
    result = check_argument(graph)
    assert result.status == "ContradictoryPremises" and not result.composed
    assert result.remaining_assumptions == ("leaf",)
    assert result.unresolved_obligations == ("middle",)
    assert result.findings["bad"] == ("refuted", "gap")
    assert "follows" in result.findings["final"]


def test_inconsistent_premises_record_both_directions_not_checker_conflict():
    graph = simple({"leaf": "false.\n", "root": "true.\n"},
                   [("deduce", ("leaf",), "root")], "root")
    result = check_argument(graph)
    assert result.status == "ContradictoryPremises" and not result.composed
    assert result.contradictory_premises == ("deduce",)
    assert outstanding_obligations(graph, result)["contradictory_premises"] == ["deduce"]
    assert result.findings["deduce"] == ("follows", "refuted")
    assert result.edges[0]["contradictory_premises"]
    assert result.remaining_assumptions == ("leaf",)


def test_follows_and_valid_gap_injected_checker_fault_is_integrity_error(monkeypatch):
    # A real sound checker cannot produce this state. Inject a component fault to
    # check the integrity guard without weakening the production checking path.
    graph = separated_vocabulary_example()
    edge = graph.deductions[0]
    envelope = {"edge_id": deduction_identity(graph, edge), "direction": "follows", "proof": {}}
    graph = replace(graph, deductions=(replace(edge, certificates=(envelope,)),))
    monkeypatch.setattr("ve.entailment.check_entailment_certificate",
                        lambda *a, **kw: EntailmentCertificateCheck(True, "Valid", 1))
    result = check_argument(graph, search=False)
    assert result.status == "CheckerConflict" and not result.composed
    assert result.findings[edge.name] == ("follows", "gap")
    assert len(result.edges[0]["artifacts"]) == 2
    assert result.composition == {}


def test_inconsistent_certificates_and_model_of_premises_is_conflict(monkeypatch):
    graph = simple({"root": "true.\n"}, [("deduce", (), "root")], "root")
    edge = graph.deductions[0]
    certs = tuple({"edge_id": deduction_identity(graph, edge), "direction": d, "proof": {}}
                  for d in ("follows", "refuted"))
    model = FiniteModel.from_dict(graph.env, {"complete": True, "domains": {}, "constants": {}, "relations": {}})
    graph = replace(graph, deductions=(replace(edge, certificates=certs, countermodels=(model,)),))
    monkeypatch.setattr("ve.entailment.check_entailment_certificate",
                        lambda *a, **kw: EntailmentCertificateCheck(True, "Valid", 1))
    result = check_argument(graph, search=False)
    assert result.status == "CheckerConflict"
    assert result.edges[0]["satisfying_premise_model_ids"] == [model.model_id]


def test_zero_search_budget_remains_inconclusive():
    graph = simple({"root": "true.\n"}, [("deduce", (), "root")], "root")
    result = check_argument(graph, max_proof_steps=0, max_models=0)
    assert result.status == "ResourceLimit"
    assert result.findings == {"deduce": ()}
    assert result.edges[0]["status"] == "unresolved"
    assert all(a["status"] == "ResourceLimit" for a in result.edges[0]["search_attempts"])


def test_evidence_changes_invalidate_assessments_and_old_display_records():
    graph = merged_vocabulary_example()
    result = check_argument(graph)
    changed = replace(graph, evidence=(replace(graph.evidence[0], snapshot_id="new-snapshot"), graph.evidence[1]))
    assert check_argument(changed).status == "InvalidInput"
    # A freshly recorded review is valid metadata but requires a new graph check.
    revised = replace(graph.evidence[0], snapshot_id="new-snapshot", assessment_binding="")
    changed = replace(graph, evidence=(revised, graph.evidence[1]))
    with pytest.raises(VEError, match="stale"):
        outstanding_obligations(changed, result)
    with pytest.raises(VEError, match="stale"):
        predicate_use_panel(changed, result)


def test_panel_lists_intermediate_premises_and_all_evidence_citations():
    graph = merged_vocabulary_example()
    extra = Claim.create(graph.env, "again", graph.claims[-1].source)
    newedge = Deduction("again_edge", (graph.root,), extra.name)
    graph = replace(graph, claims=graph.claims + (extra,), deductions=graph.deductions + (newedge,), root=extra.name)
    rows = {r["claim"]: r for p in predicate_use_panel(graph)["predicates"] for r in p["premises"]}
    assert graph.claims[-2].name in rows
    assert rows["c1"]["evidence_ids"] == ["r1"]
    assert not rows["c3"]["is_leaf"]


@pytest.mark.parametrize("mutation", [
    lambda g: replace(g, root="missing"),
    lambda g: replace(g, claims=g.claims + (g.claims[0],)),
    lambda g: replace(g, deductions=g.deductions + (g.deductions[0],)),
    lambda g: replace(g, deductions=(replace(g.deductions[0], premises=("missing",)),)),
    lambda g: replace(g, deductions=(replace(g.deductions[0], premises=(g.root,)),)),
    lambda g: replace(g, claims=(replace(g.claims[0], name=[]), *g.claims[1:])),
    lambda g: replace(g, deductions=(replace(g.deductions[0], countermodels=({},)),)),
])
def test_graph_structural_rejections(mutation):
    assert check_argument(mutation(merged_vocabulary_example())).status == "InvalidInput"


def test_multiple_statements_cannot_be_one_claim():
    env = merged_vocabulary_example().env
    with pytest.raises(VEError, match="exactly one"):
        Claim.create(env, "many", "true.\nfalse.\n")


def test_argument_json_rejects_duplicate_keys_and_unknown_fields():
    graph = merged_vocabulary_example()
    data = graph.to_dict()
    data["claims"][0]["invented"] = True
    with pytest.raises(VEError):
        ArgumentGraph.from_dict(data)
    with pytest.raises(VEError):
        ArgumentGraph.from_json('{"root":"a","root":"b"}')


@pytest.mark.parametrize("changes", [{"domains": None}, {"model_id": "stale"}, {"environment_id": "stale"}])
def test_invalid_in_memory_model_is_diagnostic(changes):
    graph = separated_vocabulary_example()
    edge = graph.deductions[0]
    graph = replace(graph, deductions=(replace(edge, countermodels=(replace(edge.countermodels[0], **changes),)),))
    result = check_argument(graph)
    assert result.status == "InvalidInput"
    assert result.errors[0]["code"] == "InvalidModel"
