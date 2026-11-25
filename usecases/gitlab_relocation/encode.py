"""The encoder's helper for the GitLab relocation translation (statute corpus batch 5): a sub-case spec (cases.py,
smoke_cases.py) -> the translation's Ctx and the stated facts. CROSS-FAMILY questions, Opus encoder. Written with the
translation, BEFORE any question existed (ISOLATION.md D-row of 2026-11-25).

A Sub lists the items one question needs (the team member p is always there), each item's parent, and the stated facts:
yes/no facts (fact) and stated values (val: dates YYYY-MM-DD). Nothing is computed here: every sum, comparison and date step
is a rule of translation.py (Lean checks it). The one exception is bridge/bridge.py's anniversary, entered as a fact marked
"bridge". Conventions the encoder applies (fixed now, before the questions; listed as encoder judgement on a case where used):
E1 the year asked about is entered by its name: 1 January of the year and of the next year (year());
E2 a place is entered by its name: the name facts of translation.NAMES are set for every listed name (true for its own name
   only); a place the text does not name gets the case's stated U.S. embargoed list membership (place());
E3 a yes/no fact the writer brief's FIXED FACTS say a case states where it matters (DESTINATION, PERSON, APPROVALS) and the
   case does not mention is entered as false, and listed as encoder judgement on the question;
E4 a fact the case states only for another question is not entered.
"""
from __future__ import annotations

import sys
from pathlib import Path

import translation as T

sys.path.insert(0, str(Path(__file__).resolve().parent / "bridge"))
import bridge as B  # noqa: E402

LIT = {T.DAY: lambda v: ["date", v], T.NDAYS: lambda v: T.nd(v)}


class Sub:
    def __init__(self, judgement=()):
        self.items = [("p", "person")]
        self.parent = {}
        self.facts = []
        self.judgement = list(judgement)

    def item(self, x, kind, parent=None):
        assert "_" not in x and x not in dict(self.items), x
        self.items.append((x, kind))
        if parent is not None:
            self.parent[x] = parent
        return self

    def fact(self, pred, x="p", val=True):
        assert pred in T.FACTS, pred
        f = T.U(pred, x)
        self._add(f if val else T.Not(f))
        return self

    def val(self, base, x, v, bridge=False):
        assert base in T.STATED_BASES, base
        self._add(T.Eq(T.k(base, x), LIT[T.UNIT_OF[base]](v)), bridge)
        return self

    def year(self, y, x="y"):
        """E1."""
        self.item(x, "year")
        return self.val("ya", x, f"{int(y):04d}-01-01").val("yb", x, f"{int(y) + 1:04d}-01-01")

    def place(self, x, name=None, onlist=None):
        """E2: name is a key of translation.NAMES or None (a place the text does not name)."""
        self.item(x, "place")
        assert name is None or name in T.NAMES, name
        for n in T.NAMES:
            self.fact(T.is_name(n), x, n == name)
        if onlist is not None:
            self.fact("onlist", x, onlist)
        return self

    def stay(self, x, place, first, last):
        self.item(x, "stay", place)
        return self.val("sf", x, first).val("sl", x, last)

    def start(self, day):
        """The start date and its bridged first anniversary (D8; a 29 February start raises: the question is refused)."""
        self.val("sd", "p", day)
        return self.val("an", "p", B.anniversary(day), bridge=True)

    def _add(self, f, bridge=False):
        self.facts.append({"id": f"f{len(self.facts)}", "formula": f, **({"bridge": True} if bridge else {})})


def build(spec):
    return T.Ctx(spec.items, spec.parent), spec.facts, {}
