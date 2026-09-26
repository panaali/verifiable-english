"""A catalogue review must remain pending when its operation budget expires."""
import time

import pytest

from ve.assist.ambiguity_patterns import review
from ve.assist.recovery import RecoveryService
from ve.ast import Unary, Const, Not
from ve.search import find_countermodel
from test_assist_recovery import environment


def test_expired_single_candidate_review_stays_pending():
    result = review(environment(), "Alice and Bob are safe.",
                    {"predicate": "safe", "left": "alice", "right": "bob"},
                    pattern_id="coordination.list@1", deadline=time.monotonic() - 1)
    assert result["pending"] and "deadline" in result["pending"][0]["reason"]


def test_approval_stops_parsing_when_operation_budget_expires(monkeypatch):
    import ve.assist.recovery as recovery
    import ve.assist.ambiguity_patterns as catalogue
    import ve.english as english

    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Api is safe.", {})
    service.start("u")
    service.classify("u", parse_outcome="one")
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    original = english.parse_english_with_metadata
    calls = []
    def slow_parse(*args, **kwargs):
        calls.append(args[1])
        time.sleep(0.08)
        return original(*args, **kwargs)
    monkeypatch.setattr(english, "parse_english_with_metadata", slow_parse)
    monkeypatch.setattr(catalogue, "parse_english_with_metadata", slow_parse)
    monkeypatch.setattr(recovery, "OPERATION_SECONDS", 0.05)
    with pytest.raises(ValueError, match="approval operation deadline"):
        service.approve("u", formula, actor="author", paraphrase="Api is safe.",
                        presentation="Api is safe.", situation=situation)
    assert len(calls) == 1
    assert service.units["u"].state == "ready"


def test_dependency_validation_is_inside_approval_budget(monkeypatch):
    import ve.assist.recovery as recovery
    import ve.english as english

    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    for unit_id, name, dependencies in (("parent", "api", ()), ("child", "carol", ("parent",))):
        wording = f"{name.title()} is safe."
        service.add(unit_id, wording, {}, dependencies=dependencies)
        service.start(unit_id)
        service.classify(unit_id, parse_outcome="one")
        if unit_id == "parent":
            formula = Unary("safe", Const(name))
            situation = find_countermodel(env, (), Not(formula)).model.to_dict()
            service.approve(unit_id, formula, actor="author", paraphrase=wording,
                            presentation=wording, situation=situation)

    original = english.parse_english_with_metadata
    calls = []
    def slow_parse(*args, **kwargs):
        calls.append(args[1])
        time.sleep(0.08)
        return original(*args, **kwargs)
    monkeypatch.setattr(english, "parse_english_with_metadata", slow_parse)
    monkeypatch.setattr(recovery, "OPERATION_SECONDS", 0.05)
    formula = Unary("safe", Const("carol"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    with pytest.raises(ValueError, match="approval operation deadline"):
        service.approve("child", formula, actor="author", paraphrase="Carol is safe.",
                        presentation="Carol is safe.", situation=situation)
    assert len(calls) == 1
    assert service.units["child"].state == "ready"
