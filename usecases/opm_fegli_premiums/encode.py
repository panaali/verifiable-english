"""The encoder's helper for the OPM FEGLI premium translation (statute corpus batch 4): a sub-case spec (cases.py,
smoke_cases.py) -> the translation's Ctx and the stated facts. CROSS-FAMILY questions, Opus encoder.

A Sub has the enrollee p, ONE premium period t (a biweekly pay period or one calendar month) and, under t, the coverages
the question names (basic b, opta oa, optb ob, optc oc) with one item per elected Option C multiple (m1, m2, ...). Stated
values: the age in whole years throughout the period (ag), the period's first day (st), the 65th birthday (bd), the
effective day of a later 75% Reduction election (sd), the Basic Insurance Amount or the Option B coverage amount (amt).
Nothing is computed here: every premium, sum, date comparison and age group is a rule of translation.py (Lean checks it).
Conventions the encoder applies: E1 a named calendar month is entered as its first day (st = YYYY-MM-01) and is not a
biweekly pay period; E2 "N multiples of Option C" is entered as N multiple items under the Option C coverage; E3 a fact
the case states only for another question (another period's age, an outside fact the rules do not read) is not entered;
E4 an election the case states is entered as a fact and the other Basic reductions as false (the case names one).
"""
from __future__ import annotations

import translation as T

LIT = {T.USD: lambda v: T.usd(v), T.DAY: lambda v: ["date", v], T.AGE: lambda v: T.age(v)}
KIND = {"basic": "b", "opta": "oa", "optb": "ob", "optc": "oc"}


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

    def period(self, start, age=None, biweekly=False):
        """The one premium period t: its first day, the age throughout it, biweekly pay period or calendar month (E1)."""
        self.item("t", "period").val("st", "t", start).fact("bw", "t", biweekly)
        if age is not None:
            self.val("ag", "t", age)
        return self

    def cov(self, kind, amount=None, multiples=None):
        x = KIND[kind]
        self.item(x, kind, "t")
        if amount is not None:
            self.val("amt", x, amount)
        for i in range(multiples or 0):   # E2
            self.item(f"m{i + 1}", "mult", x)
        return self

    def _add(self, f):
        self.facts.append({"id": f"f{len(self.facts)}", "formula": f})


def build(spec):
    return T.Ctx(spec.items, spec.parent), spec.facts, {}
