from ve.argument import check_argument, outstanding_obligations, predicate_use_panel
from ve.argument_fixtures import (
    DEPLOYED_TO_OPS,
    explicit_bridge_example,
    infinite_only_example,
    merged_vocabulary_example,
    separated_vocabulary_example,
    worked_examples,
)


def test_worked_examples_are_fresh_and_retain_exact_source_bytes():
    first = worked_examples()
    second = worked_examples()
    assert tuple(first) == ("separated", "bridged", "merged")
    assert first["separated"] is not second["separated"]
    claim = next(c for c in first["separated"].claims if c.name == "operations_review")
    assert claim.source == DEPLOYED_TO_OPS
    assert claim.source.endswith(".\n")


def test_separated_vocabulary_has_checked_gap_witness():
    result = check_argument(separated_vocabulary_example())
    assert result.status == "Incomplete"
    assert result.findings["substituted_review"] == ("gap",)
    assert "follows" not in result.findings["substituted_review"]


def test_explicit_bridge_repairs_inference_but_remains_assumption():
    graph = explicit_bridge_example()
    result = check_argument(graph)
    assert result.status == "Checked"
    assert result.findings["explicit_bridge"] == ("follows",)
    assert "review_bridge" in result.remaining_assumptions
    obligations = outstanding_obligations(graph, result)
    assert any(item["claim"] == "review_bridge" for item in obligations["assumptions"])


def test_merged_vocabulary_follows_despite_incompatible_grounding_scopes():
    graph = merged_vocabulary_example()
    result = check_argument(graph)
    assert result.status == "Checked"
    assert result.findings["merged_review"] == ("follows",)

    panel = predicate_use_panel(graph, result)
    reviewed = next(item for item in panel["predicates"] if item["predicate"] == "reviewed")
    assert {use["claim"] for use in reviewed["premises"]} == {
        "operations_review", "security_policy",
    }
    assert {tuple(use["evidence_ids"]) for use in reviewed["premises"]} == {
        ("operations-records",), ("security-policy",),
    }
    assert {use["evidence"][0]["target_scope"] for use in reviewed["premises"]} == {
        "operations deployment-readiness review records",
        "security-policy approval review",
    }
    assert {use["evidence"][0]["judgment"] for use in reviewed["premises"]} == {"accepted"}


def test_infinite_only_fixture_encodes_the_language_spec_example():
    graph = infinite_only_example()
    assert tuple(c.name for c in graph.claims) == (
        "inhabited", "irreflexive", "transitive", "successor", "contradiction",
    )
    result = check_argument(graph)
    findings = result.findings["finite_search_is_incomplete"]
    # Not(false) is a theorem and may be recorded as ``refuted``.  Crucially,
    # bounded finite search cannot mistake absence of a finite model for either
    # a positive proof of false or a gap witness.
    assert "follows" not in findings
    assert "gap" not in findings
    gap_search = next(a for a in result.edges[0]["search_attempts"] if a["kind"] == "gap")
    assert gap_search["status"] == "NotFound"
    assert result.status == "ResourceLimit"
