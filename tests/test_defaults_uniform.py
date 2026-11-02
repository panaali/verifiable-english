"""The defaults kinds' refusal of provider conditions through the relay (docs/spec/profile-composition.md 1.9, E1d).

Lean owns the guard and the refusal (`providerConditions`, `providerRefusal` in lean/VE/Defaults/Uniform.lean, read
by `defaultsRows`) and E1d's text, `providerE1d`, which no route produces yet. No pack on main states a condition
(`decodeLayered_uniform`), so no request reaches the refusal: the relay is shown Lean's rejection row and must raise its
text as Lean gives it.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from ve import defaults
from ve.backends import relay
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]


def _lean_string(name):
    """The literal (or `++` of literals) of Lean's `def <name> : String :=`."""
    source = (ROOT / "lean/VE/Defaults/Uniform.lean").read_text(encoding="utf-8")
    body = re.search(rf"^def {name} : String :=((?:\s*\"[^\"]*\"\s*(?:\+\+)?)+)", source, re.M)
    return "".join(re.findall(r"\"([^\"]*)\"", body.group(1)))


REFUSAL, E1D = _lean_string("providerRefusal"), _lean_string("providerE1d")


def test_the_texts_name_no_provider():
    assert REFUSAL == "UnsupportedProfile: defaults with provider conditions is not implemented"
    assert E1D.startswith("This question assumes no exception") and "weighing" not in REFUSAL + E1D


@pytest.mark.parametrize("kind", ["defaults-elaborate", "defaults-coherence", "defaults-certificate",
                                  "defaults-model"])
def test_the_refusal_is_relayed_verbatim(monkeypatch, kind):
    class Pool:
        def run_bound(self, mode, cases, *, timeout=None):
            assert mode == defaults.MODE
            return [{"code": "UnsupportedProfile", "result": {"id": c["id"], "status": "error", "error": REFUSAL}}
                    for c in cases]
    monkeypatch.setattr(relay, "_pool_for", lambda executable=None: Pool())
    with pytest.raises(VEError) as raised:
        defaults.run({"id": "c", "kind": kind, "environment": {}, "norms": []})
    assert str(raised.value) == REFUSAL


def test_no_python_copy_of_the_guard_or_its_sentence():
    assert [p for p in (ROOT / "ve").rglob("*.py")
            if "provider conditions" in (t := p.read_text(encoding="utf-8")) or E1D[:40] in t] == []


def test_every_record_of_e1d_says_no_route_produces_it():
    """Review pc-9 F1: E1d's text is only defined and `#guard`ed; a record that names `providerE1d` says no route
    produces it, and none says a route reads it. Wiring E1d into a route changes the first set and fails here, so the
    records are rewritten with it."""
    users = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "lean").rglob("*.lean")
                   if ".lake" not in p.parts and "providerE1d" in p.read_text(encoding="utf-8"))
    assert users == ["lean/VE/Defaults/Uniform.lean", "lean/VE/Defaults/UniformExamples.lean"]
    records = {name: (ROOT / name).read_text(encoding="utf-8") for name in users}
    records["tests/test_defaults_uniform.py"] = __doc__
    for name, record in records.items():
        text = " ".join(record.split())
        assert "`providerE1d`, which no route produces yet" in text, name
        assert not [claim for claim in ("its sentence E1d, read by", "and its sentence E1d", "`providerE1d` in")
                    if claim in text], name
