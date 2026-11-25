"""The encoder's helper for the GitLab US benefits translation (statute corpus batch 5): a sub-case spec (cases.py,
smoke_cases.py) -> the translation's Ctx and the stated facts. CROSS-FAMILY questions, Opus encoder.

A Sub lists the items one question needs (the team member p is always there), each item's parent, and the stated facts:
yes/no facts (fact) and stated values (val: dates YYYY-MM-DD, hours per week, ages in whole years, amounts in USD,
percentages, miles, weeks and days). Nothing is computed here: every sum, comparison, date step, cap and minimum is a rule
of translation.py (Lean checks it). The ONLY values not stated by the case come from the one bridge script (bridge.py),
through Sub.bridge, marked bridge (the question then uses a bridged value). Conventions the encoder applies (listed as
encoder judgement on the case where used): E1 the earnings for the year are entered equal to the annual base salary when
the case states no other earnings (the brief's fixed fact); E2 a yes/no fact the case states only for another question,
or does not state, is not entered (a family member not said to work at GitLab: gl false, the brief's one-person cases);
E3 a duration stated in weeks is entered as whole weeks and remaining days.
"""
from __future__ import annotations

import bridge as B
import translation as T

LIT = {T.USD: lambda v: T.usd(v), T.DAY: lambda v: ["date", v], T.NDAYS: lambda v: T.nd(v), T.HRS: lambda v: T.hrs(v),
       T.AGE: lambda v: T.yrs(v), T.PCT: lambda v: T.pct(v), T.MILE: lambda v: T.mil(v),
       T.WEEK: lambda v: ["decimal", T.WEEK, str(v)], T.CNT: lambda v: ["decimal", T.CNT, str(v)],
       T.MIN: lambda v: ["decimal", T.MIN, str(v)], T.YEAR: lambda v: ["decimal", T.YEAR, str(v)]}
BRIDGES = {
    "nm1": lambda a: B.first_of_next_month(a["date"]),
    "m15": lambda a: B.month_day_after(a["pye"], 3, 15),
    "m31": lambda a: B.month_day_after(a["pye"], 3, 31),
    "rb5": lambda a: B.business_days_after(B.month_day_of_year(a["year"], 3, 31), 5, a["calendar"]),
    "a22": lambda a: B.month_day_of_year(a["year"], 4, 22),
    "b3": lambda a: B.business_days_after(a["date"], 3, a["calendar"]),
}


class Sub:
    def __init__(self, judgement=()):
        self.items = [("p", "person")]
        self.parent = {}
        self.facts = []
        self.judgement = list(judgement)

    def item(self, x, kind, parent=None):
        assert "_" not in x and x not in dict(self.items), x
        assert not (x[:1] == "x" and x[1:].isdigit()), x   # x<digits> is reserved for generated binders (ve/parser.py)
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
        assert base in T.STATED_BASES and base not in T.BRIDGED_BASES, base
        self._add(T.Eq(T.k(base, x), LIT[T.UNIT_OF[base]](v)))
        return self

    def bridge(self, base, x, **args):
        """A bridged date (bridge.py); the fact is marked bridge."""
        assert base in T.BRIDGED_BASES, base
        v = BRIDGES[base](args)
        self._add(T.Eq(T.k(base, x), LIT[T.UNIT_OF[base]](v)), bridge=True)
        return self

    def weeks(self, x, weeks, days=0):
        """E3: a disability's length as whole weeks and remaining days."""
        return self.val("dwk", x, weeks).val("dxd", x, days)

    def _add(self, f, bridge=False):
        rec = {"id": f"f{len(self.facts)}", "formula": f}
        if bridge:
            rec["bridge"] = True
        self.facts.append(rec)


def build(spec):
    return T.Ctx(spec.items, spec.parent), spec.facts, {}
