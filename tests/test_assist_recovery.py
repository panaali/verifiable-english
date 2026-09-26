import json
from pathlib import Path

import pytest

from ve.assist.ambiguity_patterns import PATTERNS, review, candidates
from ve.assist.recovery import RecoveryService, nearest_wordings
from ve.ast import Unary, Const, Not
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.search import find_countermodel


def environment():
    names = ("alice", "bob", "team", "api", "service_a", "carol")
    return Environment({"language": LANGUAGE, "profile": PROFILE, "spec_revision": SPEC_REVISION,
        "vocabulary": {"sorts": {"service": {"description": "service"},
                                  "engineer": {"description": "engineer"},
                                  "server": {"description": "server"}},
                       "predicates": {**{p: {"arguments": ["service"], "description": p}
                                          for p in ("safe", "reviews", "checks")},
                                      "checks_pair": {"arguments": ["engineer", "server"],
                                                      "description": "checks"}},
                       "constants": {name: {"sort": "service", "description": name} for name in names}}})


def test_catalogue_fixtures_match_and_negative_cases():
    env = environment()
    path = Path(__file__).resolve().parents[1] / "experiments/authoring-gates/ambiguity-patterns/catalogue-v1.json"
    fixture = json.loads(path.read_text())
    assert len(fixture["fixtures"]) == len(PATTERNS)
    for row in fixture["fixtures"]:
        pattern = next(p for p in PATTERNS if p.id == row["pattern_id"])
        assert pattern.matches(row["source"])
        assert not pattern.matches(row["negative"])
        bindings = dict(row["bindings"])
        if row["pattern_id"] == "scope.every_some@1":
            bindings["relation"] = "checks_pair"
        rows, residual = candidates(env, row["source"], bindings, pattern_id=row["pattern_id"])
        assert not residual and len(rows) >= 2, (row["pattern_id"], residual)


def test_scope_card_requires_checked_distinction():
    env = environment()
    result = review(env, "Every engineer checks a server.",
        {"every_sort": "engineer", "some_sort": "server", "relation": "checks_pair"},
        pattern_id="scope.every_some@1")
    assert result["cards"] and result["cards"][0]["values"] in ([True, False], [False, True])
    assert not result["pending"]


def test_unproven_pair_remains_pending():
    env = environment()
    result = review(env, "It is safe.", {"predicate": "safe", "antecedents": ["api", "api"]},
                    pattern_id="discourse.reference@1")
    assert not result["cards"] and result["pending"]


def test_existential_reference_and_transitive_ellipsis_remain_residual():
    env = environment()
    rows, reason = candidates(env, "The API is deployed. Some service is reviewed. It is safe.",
                              {"predicate": "safe", "antecedents": ["api", "service_a"]},
                              pattern_id="discourse.reference@1")
    assert not rows and "scoped rewrite" in reason
    rows, reason = candidates(env, "Alice reviews the API. Carol does too.",
                              {"subject": "carol", "predicates": ["reviews", "checks"],
                               "transitive": True}, pattern_id="ellipsis.predicate_copy@1")
    assert not rows and "scoped completion" in reason


def test_revisioned_approval_and_invalidation():
    env = environment()
    situation = find_countermodel(env, (), Not(Unary("safe", Const("api")))).model.to_dict()
    carol_situation = find_countermodel(env, (), Not(Unary("safe", Const("carol")))).model.to_dict()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u1", "The API is safe.", {"start": 0, "end": 16})
    service.start("u1")
    assert service.classify("u1", parse_outcome="one") == "ready"
    service.approve("u1", Unary("safe", Const("api")), actor="author",
                    paraphrase="The API is safe.", presentation="Api is safe.", situation=situation)
    assert service.approval_valid("u1")
    approved_revision = service.units["u1"].revision
    ledger = service.to_ledger()
    assert service.verify_ledger(ledger)
    ledger["events"][-1]["unit_snapshot"]["source"] = "tampered"
    assert not service.verify_ledger(ledger)
    service.add("u2", "Carol agrees.", {"start": 17, "end": 30}, dependencies=["u1"])
    service.start("u2")
    service.classify("u2", parse_outcome="one")
    service.approve("u2", Unary("safe", Const("carol")), actor="author",
                    paraphrase="Carol is safe.", presentation="Carol is safe.", situation=carol_situation)
    service.edit("u1", source="The API is reviewed.")
    assert not service.approval_valid("u1") and service.units["u2"].state == "stale"
    assert service.events[-1]["revision"] == service.revision
    assert service.verify_ledger()
    restored = service.undo("u1", approved_revision)
    assert restored.state == "approved" and service.approval_valid("u1")
    assert service.units["u2"].state == "stale"
    assert service.verify_ledger()


def test_recovery_pending_translation_and_adapter_stubs():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "The API is safe.", {"start": 0}, mode="translation")
    service.start("u")
    assert service.classify("u", parse_outcome="one", discourse="incomplete") == "reading_review"
    service.set_readings("u", [{"id": "a"}, {"id": "b"}])
    with pytest.raises(ValueError, match="narrowing"):
        service.approve("u", Unary("safe", Const("api")), actor="author",
            paraphrase="API safe", presentation="API safe", situation={"checked": True})
    assert service.alias_prompt(source="staff", target="employees", argument_types=["person"],
                                direction="same", context="document")["status"] == "pending"
    with pytest.raises(RuntimeError, match="W2"):
        service.add_unit({}, anchor={})
    assert nearest_wordings("safe", ["safe", "reviewed", "deployed"])[0] == "safe"


def test_unique_parse_still_triggers_catalogue_review():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Every engineer checks a server.", {"start": 0})
    service.start("u")
    assert service.classify("u", parse_outcome="one") == "reading_review"
    assert service.units["u"].pending[0]["pattern_id"] == "scope.every_some@1"
    service.cancel("u")
    service.start("u")
    assert service.classify("u", parse_outcome="one", catalogue_bindings={
        "scope.every_some@1": {"every_sort": "engineer", "some_sort": "server",
                                "relation": "checks_pair"}}) == "ready"
    assert service.units["u"].catalogue_results["scope.every_some@1"]["cards"]


def test_invalid_situation_and_presentation_cannot_be_approved():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "The API is safe.", {"start": 0})
    service.start("u")
    service.classify("u", parse_outcome="one")
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    with pytest.raises(ValueError, match="correspondence"):
        service.approve("u", formula, actor="author", paraphrase="API safe",
                        presentation="Carol is safe.", situation=situation)
    situation["relations"]["safe"] = []
    with pytest.raises(ValueError, match="does not satisfy"):
        service.approve("u", formula, actor="author", paraphrase="API safe",
                        presentation="Api is safe.", situation=situation)


def test_proposer_reservation_and_explicit_retry():
    class Offline:
        def request(self, source, *, timeout_seconds):
            assert timeout_seconds == 50
            raise OSError("offline")
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Unknown wording.", {"start": 0})
    service.start("u")
    service.classify("u", parse_outcome="zero")
    assert service.request_proposer("u", Offline())["status"] == "exhausted"
    assert service.units["u"].proposals == 1
    assert service.events[-2]["action"] == "proposer_reserved"
    assert service.request_proposer("u", Offline())["status"] == "exhausted"
    assert service.units["u"].proposals == 2
    assert service.request_proposer("u", Offline())["status"] == "unresolved"
