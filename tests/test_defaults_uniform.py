"""The defaults kinds' refusal of provider conditions through the relay (docs/spec/profile-composition.md 1.9 and
E1d, plan PC-9).

Lean owns the guard, the refusal and its sentence (`lean/VE/Defaults/Uniform.lean`: `providerConditions`,
`providerRefusal`, `providerE1d`; read by `defaultsRows` in `lean/VE/Defaults/Route.lean`). No pack on main states a
condition (`decodeLayered_uniform`), so no request reaches the refusal yet: the relay is shown Lean's rejection row,
and must raise its text as Lean gives it. No Python source holds a copy of either text.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from ve import defaults
from ve.backends import relay
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
UNIFORM = ROOT / "lean" / "VE" / "Defaults" / "Uniform.lean"


def _lean_string(name):
    """The string literal (or `++` of literals) Lean's `def <name> : String :=` gives."""
    source = UNIFORM.read_text(encoding="utf-8")
    body = re.search(rf"^def {name} : String :=((?:\s*\"[^\"]*\"\s*(?:\+\+)?)+)", source, re.M)
    assert body, name
    return "".join(re.findall(r"\"([^\"]*)\"", body.group(1)))


REFUSAL = _lean_string("providerRefusal")
E1D = _lean_string("providerE1d")


class _Pool:
    """A service whose every answer is Lean's rejection row with the refusal."""

    def __init__(self):
        self.modes = []

    def run_bound(self, mode, cases, *, timeout=None):
        self.modes.append(mode)
        return [{"code": "UnsupportedProfile",
                 "result": {"id": case["id"], "status": "error", "error": REFUSAL}} for case in cases]


def test_the_texts_are_leans():
    assert REFUSAL == "UnsupportedProfile: defaults with provider conditions is not implemented"
    assert E1D.startswith("This question assumes no exception, and this document's providers state decision")
    assert "weighing" not in REFUSAL + E1D


@pytest.mark.parametrize("kind", ["defaults-elaborate", "defaults-coherence", "defaults-certificate",
                                  "defaults-model"])
def test_the_refusal_is_relayed_verbatim(monkeypatch, kind):
    pool = _Pool()
    monkeypatch.setattr(relay, "_pool_for", lambda executable=None: pool)
    with pytest.raises(VEError) as raised:
        defaults.run({"id": "c", "kind": kind, "environment": {}, "norms": []})
    assert str(raised.value) == REFUSAL
    assert pool.modes == [defaults.MODE]


def test_no_python_copy_of_the_guard_or_its_sentence():
    copies = [str(path.relative_to(ROOT)) for path in sorted((ROOT / "ve").rglob("*.py"))
              if "provider conditions" in (text := path.read_text(encoding="utf-8")) or E1D[:40] in text]
    assert copies == []
