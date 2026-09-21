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
    assert tuple(first) == ("g1", "g2", "g3")
    assert first["g1"] is not second["g1"]
    claim = next(c for c in first["g1"].claims if c.name == "c1")
    assert claim.source == DEPLOYED_TO_OPS
    assert claim.source.endswith(".\n")


def test_separated_vocabulary_has_checked_gap_witness():
    result = check_argument(separated_vocabulary_example())
    assert result.status == "Incomplete"
    assert result.findings["e1"] == ("gap",)
    assert "follows" not in result.findings["e1"]


def test_explicit_bridge_repairs_inference_but_remains_assumption():
    graph = explicit_bridge_example()
    result = check_argument(graph)
    assert result.status == "Checked"
    assert result.findings["e1"] == ("follows",)
    assert "c4" in result.remaining_assumptions
    obligations = outstanding_obligations(graph, result)
    assert any(item["claim"] == "c4" for item in obligations["assumptions"])


def test_merged_vocabulary_follows_despite_incompatible_grounding_scopes():
    graph = merged_vocabulary_example()
    result = check_argument(graph)
    assert result.status == "Checked"
    assert result.findings["e1"] == ("follows",)

    panel = predicate_use_panel(graph, result)
    reviewed = next(item for item in panel["predicates"] if item["predicate"] == "reviewed")
    assert {use["claim"] for use in reviewed["premises"]} == {
        "c1", "c2",
    }
    assert {tuple(use["evidence_ids"]) for use in reviewed["premises"]} == {
        ("r1",), ("r2",),
    }
    assert {use["evidence"][0]["target_scope"] for use in reviewed["premises"]} == {
        "operations deployment-readiness review records",
        "security-policy approval review",
    }
    assert {use["evidence"][0]["judgment"] for use in reviewed["premises"]} == {"accepted"}


def test_infinite_only_fixture_encodes_the_language_spec_example():
    graph = infinite_only_example()
    assert tuple(c.name for c in graph.claims) == (
        "c1", "c2", "c3", "c4", "c5",
    )
    result = check_argument(graph)
    findings = result.findings["e1"]
    # Not(false) is a theorem and may be recorded as ``refuted``.  Crucially,
    # bounded finite search cannot mistake absence of a finite model for either
    # a positive proof of false or a gap witness.
    assert "follows" not in findings
    assert "gap" not in findings
    gap_search = next(a for a in result.edges[0]["search_attempts"] if a["kind"] == "gap")
    assert gap_search["status"] == "NotFound"
    assert result.status == "Incomplete"
    assert result.warnings


def test_display_has_no_condition_labels_and_scopes_are_meaningful():
    import json
    import re

    for graph in (*worked_examples().values(), infinite_only_example()):
        result = check_argument(graph)
        displays = (graph.to_dict(), result.to_dict(), outstanding_obligations(graph, result),
                    predicate_use_panel(graph, result))
        text = json.dumps(displays).lower()
        assert not re.search(r'substitut|merged|separated|bridged|explicit_bridge|review_bridge|fixture.author|finite_search_is_incomplete', text)
        assert all(re.fullmatch(r'c\d+', c.name) for c in graph.claims)
        assert all(re.fullmatch(r'e\d+', e.name) for e in graph.deductions)
        assert all(re.fullmatch(r'r\d+', e.evidence_id) for e in graph.evidence)
        assert graph.target_scope != 'unspecified'
    graph = merged_vocabulary_example()
    obligations = outstanding_obligations(graph, check_argument(graph))
    assert [a['scope_matches_target'] for a in obligations['assumptions']] == [False, True]


def test_checked_gap_survives_tiny_proof_budget():
    graph = separated_vocabulary_example()
    result = check_argument(graph, max_proof_steps=1)
    assert result.status == 'Incomplete'
    assert result.findings['e1'] == ('gap',)
    assert result.warnings
    assert outstanding_obligations(graph, result)['warnings']


def test_checked_proof_survives_bogus_extra_gap():
    from dataclasses import replace
    from ve.model import FiniteModel

    graph = merged_vocabulary_example()
    model = FiniteModel.from_dict(graph.env, {
        'complete': True, 'domains': {'service': ['a']}, 'constants': {},
        'relations': {p: [] for p in graph.env.predicates},
    })
    graph = replace(graph, deductions=(replace(graph.deductions[0], countermodels=(model,)),))
    result = check_argument(graph)
    assert result.status == 'Checked' and result.composed
    assert result.findings['e1'] == ('follows',)
    assert any(w['code'] == 'NotCountermodel' for w in result.warnings)
    assert not result.errors
