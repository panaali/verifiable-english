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


def _busy(seconds):
    """CPU-only delay: no sleep, so only a traced deadline can stop it."""
    end = time.perf_counter() + seconds
    while time.perf_counter() < end:
        pass


def _approved_parent_and_ready_child(env):
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
    return service


def test_nested_dependency_replay_cannot_extend_approval_deadline(monkeypatch):
    import ve.assist.recovery as recovery
    import ve.assist.ambiguity_patterns as catalogue
    import ve.english as english

    env = environment()
    service = _approved_parent_and_ready_child(env)
    original = english.parse_english_with_metadata
    def cpu_parse(*args, **kwargs):
        _busy(0.2)
        return original(*args, **kwargs)
    monkeypatch.setattr(english, "parse_english_with_metadata", cpu_parse)
    monkeypatch.setattr(catalogue, "parse_english_with_metadata", cpu_parse)
    monkeypatch.setattr(recovery, "OPERATION_SECONDS", 0.25)
    formula = Unary("safe", Const("carol"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    started = time.monotonic()
    with pytest.raises(ValueError, match="approval operation deadline"):
        service.approve("child", formula, actor="author", paraphrase="Carol is safe.",
                        presentation="Carol is safe.", situation=situation)
    assert time.monotonic() - started < 0.25 + 0.15
    assert service.units["child"].state == "ready"
    monkeypatch.undo()
    assert service.verify_ledger()


@pytest.mark.parametrize("step", ["evaluate", "background", "validate_background"])
def test_situation_evaluation_is_inside_approval_deadline(monkeypatch, step):
    import ve.assist.recovery as recovery
    import ve.background as background_module

    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "Api is safe.", {})
    service.start("u")
    service.classify("u", parse_outcome="one")
    formula = Unary("safe", Const("api"))
    situation = find_countermodel(env, (), Not(formula)).model.to_dict()
    module = recovery if step == "evaluate" else background_module
    original = getattr(module, step)
    def slow(*args, **kwargs):
        _busy(0.5)
        return original(*args, **kwargs)
    monkeypatch.setattr(module, step, slow)
    monkeypatch.setattr(recovery, "OPERATION_SECONDS", 0.1)
    started = time.monotonic()
    with pytest.raises(ValueError, match="approval operation deadline"):
        service.approve("u", formula, actor="author", paraphrase="Api is safe.",
                        presentation="Api is safe.", situation=situation)
    assert time.monotonic() - started < 0.1 + 0.15
    assert service.units["u"].state == "ready"


@pytest.mark.parametrize("step", ["checked_wording", "evaluate", "validate_background"])
def test_every_catalogue_review_step_is_inside_the_deadline(monkeypatch, step):
    import ve.assist.ambiguity_patterns as catalogue

    original = getattr(catalogue, step)
    def slow(*args, **kwargs):
        _busy(0.5)
        return original(*args, **kwargs)
    monkeypatch.setattr(catalogue, step, slow)
    started = time.monotonic()
    result = review(environment(), "It is safe.", {"predicate": "safe", "antecedents": ["api", "carol"]},
                    pattern_id="discourse.reference@1", deadline=time.monotonic() + 0.1)
    assert time.monotonic() - started < 0.1 + 0.15
    assert any("deadline" in row["reason"] for row in result["pending"])
    assert not result["cards"]


def test_classify_deadline_outcome_replays_without_reading_the_clock(monkeypatch):
    import json
    import ve.assist.recovery as recovery
    import ve.assist.ambiguity_patterns as catalogue

    env = environment()
    service = RecoveryService(env, grammar_version="g1", glossary_version="v1", reading_set_version="r1")
    service.add("u", "It is safe.", {}, mode="translation")
    service.start("u")
    original = catalogue.find_distinguishing_model
    def slow(*args, **kwargs):
        _busy(0.5)
        return original(*args, **kwargs)
    monkeypatch.setattr(catalogue, "find_distinguishing_model", slow)
    monkeypatch.setattr(recovery, "OPERATION_SECONDS", 0.1)
    assert service.classify("u", parse_outcome="one", catalogue_bindings={
        "discourse.reference@1": {"predicate": "safe", "antecedents": ["api", "carol"]}}) == "reading_review"
    assert service.to_ledger()["commands"][-1]["observed"]["deadlines"] != [None]
    monkeypatch.undo()
    restored = RecoveryService.from_ledger(env, json.loads(json.dumps(service.to_ledger())))
    assert restored.units["u"].pending == service.units["u"].pending
    assert restored.units["u"].catalogue_results == service.units["u"].catalogue_results
