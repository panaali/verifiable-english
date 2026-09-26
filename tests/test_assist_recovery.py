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
    service.add("u2", "Carol agrees.", {"start": 17, "end": 30}, dependencies=["u1"])
    service.start("u2")
    service.classify("u2", parse_outcome="one")
    service.approve("u2", Unary("safe", Const("carol")), actor="author",
                    paraphrase="Carol is safe.", presentation="Carol is safe.", situation=carol_situation)
    service.edit("u1", source="The API is reviewed.")
    assert not service.approval_valid("u1") and service.units["u2"].state == "stale"
    assert service.events[-1]["revision"] == service.revision


def test_recovery_pending_translation_and_adapter_stubs():
    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {"start": 0}, mode="translation")
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
