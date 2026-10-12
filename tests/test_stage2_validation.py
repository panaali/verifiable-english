"""Environment and model validation on the Lean authority (ve/backends/validation.py)."""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import pytest

from ve.backends import dispatch, relay, validation
from ve.environment import Environment
from ve.errors import CheckerUnavailable, InvalidModel, VEError
from ve.model import FiniteModel
from tests import probe_matrix as pm
from tests.test_norms import environment, obligation, permission

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")


def outcome(build):
    try:
        built = build()
    except VEError as exc:
        return ("rejected", exc.to_dict())
    return ("accepted", built.to_dict(), getattr(built, "environment_id", None),
            getattr(built, "model_id", None))


def inputs():
    """Every Stage 0 profile combination, valid and with an undeclared sort, and a
    valid and an ill-sorted model of each valid environment."""
    for family in pm.FAMILIES:
        for n in range(len(pm.LAYERS) + 1):
            for layers in itertools.combinations(pm.LAYERS, n):
                raw = pm.raw_environment((*family, *layers))
                bad = json.loads(json.dumps(raw))
                bad["vocabulary"]["predicates"]["base"]["arguments"] = ["absent"]
                yield raw, bad


def test_environments_and_models_match_frozen_python_on_every_profile_combination(
        monkeypatch, tmp_path, capfd):
    """The pre-deletion Python oracle runs in a separate, pinned checkout.

    Switching VE_AUTHORITY in this checkout does not switch these constructors:
    both settings call Lean. Keep the comparison independent of the relay.
    """
    from tools import lean_first_oracle

    cases = []
    for raw, bad in inputs():
        cases.append({"environment": raw, "models": []})
        cases.append({"environment": bad, "models": []})
        try:
            env = Environment(raw)
        except VEError:
            continue
        good = pm.model_wire(env)
        wrong = json.loads(json.dumps(good))
        wrong["constants"]["x"] = "absent"
        cases[-2]["models"] = [good, wrong]

    payload = tmp_path / "cases.json"
    payload.write_text(json.dumps(cases))
    script = tmp_path / "oracle.py"
    script.write_text(
        "import json, sys\n"
        "from ve.environment import Environment\n"
        "from ve.model import FiniteModel\n"
        "from ve.errors import VEError\n"
        "rows = []\n"
        "for case in json.load(open(sys.argv[1])):\n"
        "    try:\n"
        "        env = Environment(case['environment'])\n"
        "    except VEError:\n"
        "        rows.append(['rejected', []])\n"
        "        continue\n"
        "    models = []\n"
        "    for wire in case['models']:\n"
        "        try:\n"
        "            models.append(['accepted', FiniteModel.from_dict(env, wire).model_id])\n"
        "        except VEError:\n"
        "            models.append(['rejected'])\n"
        "    rows.append(['accepted', env.environment_id, models])\n"
        "print(json.dumps(rows))\n"
    )
    # oracle.run executes the script with the frozen package on PYTHONPATH.
    # Supply the payload path through argv in a tiny wrapper so the oracle's
    # runner need not acquire another interface for this test.
    wrapper = tmp_path / "run_oracle.py"
    wrapper.write_text("import runpy, sys\n"
                       f"sys.argv = [{str(script)!r}, {str(payload)!r}]\n"
                       f"runpy.run_path({str(script)!r}, run_name='__main__')\n")
    assert lean_first_oracle.run(wrapper, scratch=tmp_path) == 0
    expected = json.loads(capfd.readouterr().out)

    seen = []
    original = relay.decide
    def traced(mode, requests, **kw):
        seen.append(mode)
        return original(mode, requests, **kw)
    monkeypatch.setattr(relay, "decide", traced)
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    actual = []
    for case in cases:
        try:
            env = Environment(case["environment"])
        except VEError:
            actual.append(["rejected", []])
            continue
        models = []
        for wire in case["models"]:
            try:
                models.append(["accepted", FiniteModel.from_dict(env, wire).model_id])
            except VEError:
                models.append(["rejected"])
        actual.append(["accepted", env.environment_id, models])
    assert actual == expected
    assert "environment" in seen and "model" in seen


def test_lean_checks_the_norms_profile_of_a_model(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    env = environment({"required": obligation(), "permitted": permission()})
    wire = {"complete": True, "domains": {"act": ["a"]}, "constants": {},
            "relations": {"required": [["a"]], "permitted": []}}
    with pytest.raises(InvalidModel, match="required relation required exceeds permission permitted") as caught:
        relay.decide("model", [{"id": "m", "environment": env.to_dict(), "model": wire}])
    assert caught.value.generator == "profile"
    with pytest.raises(InvalidModel, match="required relation"):
        FiniteModel.from_dict(env, wire)


def fake_lean(monkeypatch, row):
    calls = []

    def run(mode, cases, **kw):
        calls.append(mode)
        return [row(mode, case) for case in cases]

    monkeypatch.setattr(relay, "decide", run)
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    return calls


def test_a_lean_only_rejection_carries_leans_diagnostic(monkeypatch):
    from ve.backends.diagnostics import checker_error

    def reject(mode, case):
        raise checker_error("UnknownSymbol: lean refuses this vocabulary")

    fake_lean(monkeypatch, reject)
    with pytest.raises(VEError, match="^UnknownSymbol: lean refuses this vocabulary$"):
        Environment(pm.raw_environment(()))


def test_speech_scope_references_are_checked_before_construction():
    from tests.test_environment_field_types import _speech
    raw = _speech()
    raw["speech_acts"]["addressee"]["sort"] = "absent"
    with pytest.raises(VEError, match="^UnknownSymbol: sort absent$"):
        Environment(raw)


def test_reviewed_environment_findings_have_one_python_lean_diagnostic():
    """Replay every reviewed environment mutation, including stale minimized ones."""
    from tools.difffuzz import EnvironmentSurface, evaluate, seed_of

    entries = [entry for entry in json.loads(
        (ROOT / "conformance/difffuzz-baseline.json").read_text())["entries"]
        if entry["surface"] == "environment"]
    surface = EnvironmentSurface()
    try:
        for entry, (_, _, answers, _) in zip(
                entries, evaluate(surface, [(seed_of(entry), entry["input"]) for entry in entries]),
                strict=True):
            python, lean = answers["python"], answers["lean"]
            fields = ("outcome", "code", "text")
            assert tuple(python.get(field) for field in fields) == tuple(lean.get(field) for field in fields), entry["id"]
    finally:
        surface.close()


def test_soft_metadata_survives_the_lean_environment_identity():
    from tools.difffuzz_corpus import environments
    raw = next(data for origin, data in environments()
               if origin == "conformance/soft_norms_rust.json/9/source/environment")
    env = Environment(raw)
    assert env.to_dict() == raw
    assert relay.decide("environment", [{"id": "e", "environment": raw}])[0]["environment_id"] == env.environment_id


def test_model_identity_is_bound_from_leans_answer(monkeypatch):
    env = Environment(pm.raw_environment(()))
    fake_lean(monkeypatch, lambda mode, case: {"id": "model", "status": "ok",
                                               "valid": True, "model_id": "f" * 64})
    assert FiniteModel.from_dict(env, pm.model_wire(env)).model_id == "f" * 64


def test_lean_names_a_rejection_both_checkers_make(monkeypatch):
    from ve.backends.diagnostics import checker_error
    raw = pm.raw_environment(())
    raw["vocabulary"]["predicates"]["base"]["arguments"] = ["absent"]
    fake_lean(monkeypatch, lambda mode, case: (_ for _ in ()).throw(checker_error("different words")))
    with pytest.raises(VEError, match="different words"):
        Environment(raw)


def test_lean_acceptance_with_wrong_identity_is_unavailable(monkeypatch):
    raw = pm.raw_environment(())
    raw["vocabulary"]["predicates"]["base"]["arguments"] = ["absent"]
    fake_lean(monkeypatch, lambda mode, case: {"id": "environment", "status": "ok",
                                               "environment_id": "0" * 64})
    with pytest.raises(CheckerUnavailable, match="identities differ"):
        Environment(raw)


def test_lean_acceptance_of_an_unconstructible_source_is_unavailable(monkeypatch):
    raw = pm.raw_environment(())
    del raw["vocabulary"]["sorts"]
    fake_lean(monkeypatch, lambda mode, case: {"id": "environment", "status": "ok",
                                               "environment_id": "0" * 64})
    with pytest.raises(CheckerUnavailable, match="Python could not construct a Lean-accepted environment"):
        Environment(raw)


def test_identity_mismatch_is_unavailable_and_acceptance_is_cached(monkeypatch):
    raw = pm.raw_environment(())
    identity = Environment(raw).environment_id
    calls = fake_lean(monkeypatch, lambda mode, case: {"id": "environment", "status": "ok",
                                                       "environment_id": "0" * 64})
    with pytest.raises(CheckerUnavailable, match="identities differ"):
        Environment(raw)
    calls = fake_lean(monkeypatch, lambda mode, case: {"id": "environment", "status": "ok",
                                                       "environment_id": identity})
    Environment(raw)
    Environment(raw)
    assert calls == ["environment"]


def test_all_authorities_use_lean_for_environment_and_model(monkeypatch):
    raw = pm.raw_environment(())
    original = relay.decide
    calls = []
    def traced(mode, cases, **kw):
        calls.append(mode)
        return original(mode, cases, **kw)
    monkeypatch.setattr(relay, "decide", traced)
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    monkeypatch.setenv("VE_AUTHORITY", "rust-experimental")
    env = Environment(raw)
    FiniteModel.from_dict(env, pm.model_wire(env))
    assert "environment" in calls and "model" in calls


def test_lean_rejects_a_model_whose_claimed_identity_is_stale(monkeypatch):
    """An existing FiniteModel's claimed identities are checked by Lean's model
    mode: a stale model_id or a model of another environment is Lean's
    rejection, named with Python's diagnostic."""
    from dataclasses import replace
    from ve.ast import Unary, Const
    from ve.evaluate import evaluate
    env = Environment(pm.raw_environment(()))
    other = Environment(pm.raw_environment(("data@0",)))
    monkeypatch.setenv("VE_AUTHORITY", "python")
    model = FiniteModel.from_dict(env, pm.model_wire(env))
    formula = Unary("base", Const("x"))
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    row = relay.decide("model", [{"id": "m", "environment": env.to_dict(), "model": pm.model_wire(env),
                                     "claimed": {"environment_id": env.environment_id,
                                                 "model_id": model.model_id}}])[0]
    assert row["model_id"] == model.model_id
    for stale, message in ((replace(model, model_id="0" * 64), "does not match its contents"),
                           (replace(model, environment_id=other.environment_id), "different environment")):
        with pytest.raises(InvalidModel, match=message) as raised:
            evaluate(env, formula, stale)
        assert getattr(raised.value, "backend_rejection", False) is True
        with pytest.raises(VEError, match=f"InvalidModel: model .*{message}"):
            relay.decide("model", [{"id": "m", "environment": env.to_dict(), "model": pm.model_wire(env),
                                       "claimed": {"environment_id": stale.environment_id,
                                                   "model_id": stale.model_id}}])


def test_model_identity_sorts_domains_as_python_does(monkeypatch):
    """Python's model identity sorts each domain's entities (`j10` before `j2`)."""
    env = Environment(pm.raw_environment(()))
    wire = pm.model_wire(env)
    wire["domains"]["item"] = ["j2", "i", "j10"]
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = FiniteModel.from_dict(env, wire).model_id
    row = relay.decide("model", [{"id": "m", "environment": env.to_dict(), "model": wire}])[0]
    assert row["model_id"] == expected
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert FiniteModel.from_dict(env, wire).model_id == expected


def chained(family=()):
    """A definition over another definition, declared in the reverse order."""
    raw = pm.raw_environment((*family, "definitions@0"))
    predicates = raw["vocabulary"]["predicates"]
    predicates["top_derived"] = {"arguments": ["item"], "description": "top derived",
                                 "defined": {"arguments": ["item"],
                                             "body": ["not", ["unary", "derived", ["var", 0]]]}}
    return raw


@pytest.mark.parametrize("family", [(), ("closure@0",), ("closure@0", "nary@0")])
def test_definitions_elaborate_in_lean_in_python_order(monkeypatch, family):
    from ve.definitions import compile_definitions
    seen = []
    original = relay.decide
    def traced(mode, cases, **kw):
        seen.append(mode)
        return original(mode, cases, **kw)
    monkeypatch.setattr(relay, "decide", traced)
    records = {}
    for authority in ("python", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        env = Environment(chained(family))
        records[authority] = [(d.name, d.arguments, d.body)
                              for d in compile_definitions(env, env.definition_entries, version="v")]
    assert records["lean"] == records["python"]
    assert [name for name, _, _ in records["lean"]] == ["derived", "top_derived"]
    assert "route" in seen


def test_a_definition_cycle_both_checkers_reject_is_named_by_python(monkeypatch):
    from ve.definitions import compile_definitions
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    env = Environment(chained())
    entries = {**env.definition_entries,
               "derived": {"arguments": ["item"], "body": ["unary", "top_derived", ["var", 0]]}}
    with pytest.raises(VEError, match="DependencyCycle"):
        compile_definitions(env, entries, version="v")


def test_definitions_are_leans_answer_and_python_does_not_arbitrate(monkeypatch):
    """Lean-first batch 13b: Lean's Background answer is the definitions under every authority. Python no
    longer re-decides them (`validation.decided` is deleted): an entry Python once rejected is whatever Lean
    answers, and a row whose premises and generators do not pair is CheckerUnavailable."""
    from ve.definitions import compile_definitions
    env = Environment(chained())
    entries = {**env.definition_entries,
               "derived": {"arguments": ["item"], "body": ["unary", "missing", ["var", 0]]}}
    fake_lean(monkeypatch, lambda mode, case: {"id": "definitions", "status": "ok",
                                               "premises": [], "generators": [], "background": []})
    monkeypatch.setenv("VE_AUTHORITY", "python")
    assert compile_definitions(env, entries, version="v-accepted") == ()
    fake_lean(monkeypatch, lambda mode, case: {"id": "definitions", "status": "ok",
                                               "premises": [["top"]], "generators": [], "background": []})
    monkeypatch.setenv("VE_AUTHORITY", "python")
    with pytest.raises(CheckerUnavailable, match="malformed Lean Background result"):
        compile_definitions(env, {**entries, "derived": {"arguments": ["item"], "body": ["top"]}},
                            version="v-malformed")


@pytest.mark.parametrize("kind", ["v0", "closure", "order"])
def test_frozen_envelopes_and_their_models_are_validated_in_lean(monkeypatch, kind):
    from dataclasses import replace
    from ve.ast import Const, Unary
    from ve.evaluate import evaluate
    from tests.test_stage2_graph import legacy_environment
    monkeypatch.setenv("VE_AUTHORITY", "python")
    env = legacy_environment(kind)
    data = env.to_dict()
    bad = json.loads(json.dumps(data))
    bad["vocabulary"]["predicates"]["base"]["arguments"] = ["absent"]
    wire = pm.model_wire(env)
    wrong = {**wire, "constants": {"x": "absent"}}
    expected = [outcome(lambda: Environment(x)) for x in (data, bad)] + \
        [outcome(lambda: FiniteModel.from_dict(env, w)) for w in (wire, wrong)]
    seen = []
    original = relay.decide
    def traced(mode, cases, **kw):
        seen.append(mode)
        return original(mode, cases, **kw)
    monkeypatch.setattr(relay, "decide", traced)
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert [outcome(lambda: Environment(x)) for x in (data, bad)] + \
        [outcome(lambda: FiniteModel.from_dict(env, w)) for w in (wire, wrong)] == expected
    assert "environment" in seen and "model" in seen
    model = FiniteModel.from_dict(env, wire)
    with pytest.raises(InvalidModel, match="does not match its contents") as raised:
        evaluate(env, Unary("base", Const("x")), replace(model, model_id="0" * 64))
    assert getattr(raised.value, "backend_rejection", False) is True
