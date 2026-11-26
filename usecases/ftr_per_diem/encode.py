"""The encoder's helper for the FTR per diem translation (statute corpus batch 4): a sub-case spec (cases.py, smoke_cases.py)
-> the translation's Ctx and the stated facts. CROSS-FAMILY questions, Opus encoder.

A Sub lists the items one question needs (the employee p is always there), each item's parent, the structural links of the
translation's Ctx (a rest-stop day's location, a long-term night's lodging, a hypothetical day's voluntary return, the
stated count of entitled long-term days, the nights with a stated arrival, a trip with UTC offsets) and the stated facts:
yes/no facts (fact) and stated values (val: dates YYYY-MM-DD, clock times as minutes of the day, offsets in minutes east of
UTC, durations as hours and minutes, amounts in USD). Nothing is computed here: every sum, comparison, date and minute
step, share, cap and deduction is a rule of translation.py (Lean checks it). Transcription conventions (not judgements):
E1 a clock time "HH:MM" is entered as the minute of the day 60 x HH + MM; E2 "UTC+09" is entered as the offset 540 and
"UTC-10" as -600; E3 a stated count of entitled long-term days n is entered as n (Ctx.n); E4 a place stated "in CONUS" is
entered conus (and ocon/dcon for a rest period's origin and destination), a place stated "a foreign area" frgn, a place in
Alaska, Hawaii or a U.S. territory stated "a non-foreign OCONUS area" nfo; E5 a fact the case states only for another
question is not entered.
"""
from __future__ import annotations

import translation as T

LIT = {T.USD: lambda v: T.usd(v), T.DAY: lambda v: ["date", v], T.MIN: lambda v: T.mn(v)}


class Sub:
    def __init__(self, judgement=()):
        self.items = [("p", "person")]
        self.parent = {}
        self.link = {}
        self.n = {}
        self.arr = set()
        self.zoned = set()
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

    def facts_(self, x, **kw):
        for pred, val in kw.items():
            self.fact(pred, x, val)
        return self

    def val(self, base, x, v):
        assert base in T.STATED_BASES, base
        self._add(T.Eq(T.k(base, x), LIT[T.UNIT_OF[base]](v)))
        return self

    def clock(self, base_d, base_m, x, day, hhmm):
        """E1: a stated moment (day, clock time) -> the day and the minute of the day."""
        h, m = (int(v) for v in hhmm.split(":"))
        return self.val(base_d, x, day).val(base_m, x, 60 * h + m)

    def _add(self, f):
        self.facts.append({"id": f"f{len(self.facts)}", "formula": f})


def build(spec):
    return T.Ctx(spec.items, spec.parent, spec.link, spec.n, spec.arr, spec.zoned), spec.facts, {}
