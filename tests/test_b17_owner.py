"""Batch 17: reported assist and Cedar decisions must cross the Lean boundary."""

from ve.assist.session import AssistSession
from ve.ast import Top
from ve.backends.dispatch import authority_for
from ve.adapters.cedar import translate
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION


ENV = {"language": LANGUAGE, "profile": PROFILE, "spec_revision": SPEC_REVISION,
       "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}}}


def _session():
    session = object.__new__(AssistSession)
    session.env = Environment(ENV)
    session.options = {"max_proof_steps": 10_000, "max_domain_size": 2,
                       "max_models": 10, "max_evaluations": 1000}
    return session


def test_assist_decide_replays_found_in_lean(monkeypatch):
    session = _session()
    seen = []
    original = session._lean_replays

    def checked(*args):
        seen.append(args)
        return original(*args)

    monkeypatch.setattr(session, "_lean_replays", checked)
    assert session._decide((), Top()) == "yes"
    assert len(seen) == 1
    monkeypatch.setattr(session, "_lean_replays", lambda *_: False)
    assert session._decide((), Top()) != "yes"


def test_assist_positive_entailment_requires_lean_replay(monkeypatch):
    session = _session()
    assert session._entails((), Top()) is True
    monkeypatch.setattr(session, "_lean_replays", lambda *_: False)
    assert session._entails((), Top()) is False


def test_cedar_evaluates_each_request_under_lean(monkeypatch):
    from ve.adapters import cedar
    requests = [
        {"principal": 'User::"alice"', "action": 'Action::"read"', "resource": 'Doc::"one"'},
        {"principal": 'User::"bob"', "action": 'Action::"read"', "resource": 'Doc::"one"'},
    ]
    source = 'permit(principal, action, resource) when { principal == User::"alice" };'
    translated = translate(source, [], [], requests)
    calls = []
    real = cedar.evaluate

    def evaluated(env, formula, model, **kwargs):
        calls.append((authority_for("evaluate"), tuple(model.domains["request"])))
        return real(env, formula, model, **kwargs)

    monkeypatch.setattr(cedar, "evaluate", evaluated)
    assert [r["decision"] for r in translated.decisions()] == ["allow", "deny"]
    assert calls == [("lean", ("request0",)), ("lean", ("request0",)),
                     ("lean", ("request1",)), ("lean", ("request1",))]
