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


def test_bundles_outside_the_lean_route_are_not_dispatched(monkeypatch):
    data = bundle()
    data["environment"]["profiles"] = ["closure@0", "relational-fol@0"]
    assert not __import__("ve.bundle", fromlist=["_lean_bundle_scope"])._lean_bundle_scope(data)
    seen = routed(monkeypatch, "lean")
    outcome(data)
    assert ("bundle", "lean") not in seen


def test_the_bundle_container_is_decoded_before_lean(monkeypatch):
    data = {**bundle(), "version": "wrong"}
    routed(monkeypatch, "lean")
    with pytest.raises(VEError, match="Unsupported lemma bundle version"):
        check_bundle(data)
