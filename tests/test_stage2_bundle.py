"""Lemma bundles on the Lean authority: Lean's route bundle case decides acceptance."""
from __future__ import annotations

from pathlib import Path

import pytest

from ve.backends import dispatch, lean_runner, validation
from ve.bundle import check_bundle
from ve.errors import VEError
from tests.test_bundle import bundle, _cyclic, _other_version

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")


def routed(monkeypatch, authority):
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda op, auth: seen.append((op, auth))])
    monkeypatch.setenv("VE_AUTHORITY", authority)
    return seen


def outcome(data):
    try:
        return check_bundle(data)
    except VEError as exc:
        return exc.to_dict()


@pytest.mark.parametrize("change", [None, _cyclic, _other_version])
def test_lean_bundle_verdict_and_report_match_python(monkeypatch, change):
    data = bundle()
    if change is not None:
        change(data)
    routed(monkeypatch, "python")
    expected = outcome(data)
    seen = routed(monkeypatch, "lean")
    assert outcome(data) == expected
    assert ("bundle", "lean") in seen


def test_a_lean_only_bundle_rejection_is_leans(monkeypatch):
    from ve.backends.diagnostics import checker_error
    data = bundle()
    routed(monkeypatch, "lean")
    real = lean_runner.run

    def reject(mode, cases, **kw):
        if cases and cases[0].get("kind") == "bundle":
            raise checker_error("lemma second: certificate rejected by Lean")
        return real(mode, cases, **kw)

    monkeypatch.setattr(lean_runner, "run", reject)
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    with pytest.raises(VEError, match="certificate rejected by Lean"):
        check_bundle(data)


def family_bundle(family):
    """Two lemmas, the second citing the first, over a probe environment of
    `family`, each proving the family's semantic formula (Background leaves first)."""
    from ve.ast import And, formula_to_data
    from ve.background import background
    from ve.entailment import prove_entailment
    from ve.environment import Environment
    from ve.identity import meaning_id
    from tests import probe_matrix as pm
    env = Environment(pm.raw_environment(family))
    bg = [{"label": "background:" + p.generator, "ast": formula_to_data(env, p.formula)}
          for p in background(env)]
    f = pm.semantic_formula(env)
    both = And(f, f)
    own = [{"label": "open:assumption", "ast": formula_to_data(env, f)}]
    first = {"name": "first", "environment_id": env.environment_id, "premises": own, "cites": [],
             "conclusion": formula_to_data(env, f), "meaning_id": meaning_id(env, f),
             "reading_choices": {}, "transitive_leaves": bg + own,
             "certificate": prove_entailment(env, (f,), f).certificate}
    second = {"name": "second", "environment_id": env.environment_id, "premises": own,
              "cites": [first["meaning_id"]], "conclusion": formula_to_data(env, both),
              "meaning_id": meaning_id(env, both), "reading_choices": {},
              "transitive_leaves": bg + own,
              "certificate": prove_entailment(env, (f, f), both).certificate}
    return {"version": "ve-bundle@0", "environment": env.to_dict(), "lemmas": [first, second]}


FAMILIES = [("closure@0",), ("closure@0", "nary@0"), ("order@0",), ("closure@0", "definitions@0"),
            ("closure@0", "nary@0", "data@0"), ("norms@0",), ("closure@0", "norms@0"),
            ("definitions@0", "norms@0")]


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("change", [None, _cyclic, _other_version])
def test_bundles_on_every_family_and_over_norms_are_leans(monkeypatch, family, change):
    """Bundles the route's bundle case refuses (closure, core and order families,
    norms environments) are checked by Lean's `bundle` mode (VE/Service/FamilyBundle.lean)."""
    data = family_bundle(family)
    if change is not None:
        change(data)
    routed(monkeypatch, "python")
    expected = outcome(data)
    assert (expected.get("status") == "Checked") == (change is None), expected
    seen = routed(monkeypatch, "lean")
    modes = []
    real = lean_runner.run

    def spy(mode, cases, **kw):
        modes.append(mode)
        return real(mode, cases, **kw)

    monkeypatch.setattr(lean_runner, "run", spy)
    monkeypatch.setattr(validation, "_ACCEPTED", {})
    assert outcome(data) == expected
    assert ("bundle", "lean") in seen and "bundle" in modes


def test_a_family_bundle_with_a_forged_certificate_is_rejected_by_lean(monkeypatch):
    data = family_bundle(("closure@0",))
    case = {"id": "b", "environment": data["environment"], "lemmas": data["lemmas"]}
    assert lean_runner.run("bundle", [case])[0]["checked"] == 2
    data["lemmas"][1]["certificate"] = data["lemmas"][0]["certificate"]
    with pytest.raises(VEError, match="stale|certificate failed"):
        lean_runner.run("bundle", [case])


def test_the_bundle_container_is_decoded_before_lean(monkeypatch):
    data = {**bundle(), "version": "wrong"}
    routed(monkeypatch, "lean")
    with pytest.raises(VEError, match="Unsupported lemma bundle version"):
        check_bundle(data)
