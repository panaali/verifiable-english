"""The encoder's helper for the GitLab travel-expense translation (statute corpus batch 4): a sub-case spec (cases.py,
smoke_cases.py) -> the translation's Ctx and the stated facts. CROSS-FAMILY questions, Opus encoder.

A Sub lists the items one question needs (the team member p is always there), each item's parent, and the stated facts:
yes/no facts (fact) and stated values (val: dates YYYY-MM-DD, clock times as minutes of the day, durations as hours and
minutes, amounts in USD, heights, class positions lowest first = 1). Nothing is computed here: every sum, comparison,
date step, count and cap is a rule of translation.py (Lean checks it). Conventions the encoder applies (listed as encoder
judgement on the case where used): E1 the classes the case lists are numbered from 1 (lowest) in the stated order; E2 a
clock time "HH:MM" is entered as the minute of the day 60 x HH + MM (the case's one time zone, UTC); E3 a fact the case
states only for the purpose of another question is not entered.
"""
from __future__ import annotations

import translation as T

LIT = {T.USD: lambda v: T.usd(v), T.DAY: lambda v: ["date", v], T.NDAYS: lambda v: T.nd(v), T.MIN: lambda v: T.mn(v),
       T.CNT: lambda v: T.cnt(v), T.RANK: lambda v: T.rk(v), T.HCM: lambda v: ["decimal", T.HCM, str(v)],
       T.INCH: lambda v: ["decimal", T.INCH, str(v)]}


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

    def val(self, base, x, v):
        assert base in T.STATED_BASES, base
        self._add(T.Eq(T.k(base, x), LIT[T.UNIT_OF[base]](v)))
        return self

    def seg(self, x, parent, hh, mm):
        self.item(x, "seg", parent)
        return self.val("hh", x, hh).val("mm", x, mm)

    def clock(self, base_d, base_m, x, day, hhmm):
        """E2: a stated moment (day, clock time) -> the day and the minute of the day."""
        h, m = (int(v) for v in hhmm.split(":"))
        return self.val(base_d, x, day).val(base_m, x, 60 * h + m)

    def _add(self, f):
        self.facts.append({"id": f"f{len(self.facts)}", "formula": f})


def build(spec):
    return T.Ctx(spec.items, spec.parent), spec.facts, {}
