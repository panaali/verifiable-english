"""The encoder's helper for the GitHub Sponsors (Sponsored Developer) translation (statute corpus batch 5): a sub-case spec
(cases.py, smoke_cases.py) -> the translation's Ctx and the stated facts. CROSS-FAMILY questions, Opus encoder.

Nothing is computed here: every sum, cap, period in days, comparison and classification is a rule of translation.py (Lean
checks it). The calendar steps come from bridge/bridge.py and enter as facts marked "bridge" (never typed by the encoder).
Conventions the encoder applies (an encoder judgement wherever one decides anything; listed on the case):
E1 a named calendar month is entered as its first day (mf); its payments and deductions go under it in day order.
E2 PLAIN facts are closed (what the case does not say is false; the brief makes the writer state outside outcomes where a
   question turns on them); STATED facts (judgments) are entered only as the case states them.
E3 the months of a case form one chain since the last payout (chs on the first month the case gives, unless the case
   states an unpaid balance before it: then that earlier month is entered too).
E4 a refund or chargeback whose day lies in another month than its payment: one deduction under each of the two months,
   both marked xmon (R1: two readings).
E5 fd = the day the case says the first sponsorship was initiated (else the first stated sponsorship payment's day, an
   encoder judgement); hasfd follows it.
E6 an age the case states is entered as ag; a date of birth and a day: the bridge's whole years.
"""
from __future__ import annotations

import sys
from pathlib import Path

import translation as T

sys.path.insert(0, str(Path(__file__).resolve().parent / "bridge"))
import bridge as B  # noqa: E402

LIT = {T.USD: lambda v: T.usd(v), T.DAY: lambda v: ["date", v], T.AGE: lambda v: T.age(v)}


class Sub:
    def __init__(self, judgement=()):
        self.items = [("p", "dev")]
        self.parent = {}
        self.true = {"p": set()}
        self.stated = {"p": {}}
        self.consts = {}
        self.dob = None
        self.judgement = list(judgement)

    # --- items ---
    def _item(self, x, kind, parent=None):
        assert "_" not in x and x not in dict(self.items) and not (x[:1] == "x" and x[1:].isdigit()), x
        self.items.append((x, kind))
        self.true[x], self.stated[x] = set(), {}
        if parent is not None:
            self.parent[x] = parent
        return self

    def _set(self, x, kind, facts, stated):
        for f in facts:
            assert f in T.PLAIN[kind], (kind, f)
            self.true[x].add(f)
        for f, v in stated.items():
            assert f in T.STATED.get(kind, {}), (kind, f)
            self.stated[x][f] = v

    def dev(self, *facts, **stated):
        self._set("p", "dev", facts, stated)
        return self

    def val(self, base, x, v):
        assert base in T.STATED_BASES and base not in T.BRIDGED, base
        self.consts[f"{base}_{x}"] = v
        return self

    def born(self, dob, day):
        """E6: the age on day from a stated date of birth (bridged)."""
        self.dob = (dob, day)
        return self

    def month(self, m, first, *facts, mvd=None, mn=None):
        self._item(m, "mon")
        self._set(m, "mon", facts, {})
        self.val("mf", m, first)
        if mvd is not None:
            self.true[m].add("mv")
            self.val("mvd", m, mvd)
        if mn is not None:
            self.true[m].add("xbm")
            self.val("mn", m, mn)
        return self

    def pay(self, x, m, day, amount, kind, *facts, cbd=None):
        self._item(x, "pay", m)
        self._set(x, "pay", (kind,) + facts, {})
        self.val("dy", x, day).val("am", x, amount)
        if cbd is not None:
            self.true[x].add("cbk")
            self.val("cbd", x, cbd)
        return self

    def ded(self, d, m, day, amount, *facts):
        self._item(d, "ded", m)
        self._set(d, "ded", facts, {})
        self.val("dy", d, day).val("am", d, amount)
        return self

    def act(self, a, *facts, **stated):
        self._item(a, "act")
        self._set(a, "act", facts, stated)
        return self

    def duty(self, u, fact):
        self._item(u, "duty")
        self._set(u, "duty", () if fact is None else (fact,), {})
        return self

    def gh(self, g, fact):
        self._item(g, "gh")
        self._set(g, "gh", (fact,), {})
        return self

    # --- the bridge (never the encoder's own arithmetic) ---
    def bridged(self):
        out = {}
        tp = self.true["p"]
        method = "sc" if "sc" in tp else "aw" if ("ach" in tp or "wire" in tp) else None
        for x, kind in self.items:
            if kind == "mon":
                first = self.consts[f"mf_{x}"]
                out[f"ml_{x}"] = B.month_last(first)
                if method == "sc":
                    out[f"ps_{x}"] = B.next_22nd(first)
                elif method == "aw":
                    out[f"ps_{x}"] = B.next_third_thursday(first)
        if "ad_p" in self.consts:
            out["mlo_p"], out["mhi_p"] = B.twelve_months(self.consts["ad_p"])
        if "fd_p" in self.consts and method is not None:
            out["nx_p"] = B.next_after_60(self.consts["fd_p"], method)
        if "rc_p" in self.consts:
            out["rl_p"] = B.month_last(self.consts["rc_p"])
        if self.dob is not None:
            a = B.age(*self.dob)
            if a is not None:
                out["ag_p"] = a
        return out


def build(spec):
    ctx = T.Ctx(spec.items, spec.parent)
    if "fd_p" in spec.consts:
        spec.true["p"].add("hasfd")
    facts = []

    def add(fid, f, bridge=False):
        rec = {"id": fid, "formula": f}
        if bridge:
            rec["bridge"] = True
        facts.append(rec)

    for x, kind in spec.items:
        for f in T.PLAIN[kind]:
            a = T.U(f, x)
            add(f"{x}.{f}", a if f in spec.true[x] else T.Not(a))
        for f, v in spec.stated[x].items():
            a = T.U(f, x)
            add(f"{x}.{f}", a if v else T.Not(a))
    for name, v in sorted(spec.consts.items()):
        base = name.split("_", 1)[0]
        add(name, T.Eq(T.k(base, name.split("_", 1)[1]), LIT[T.UNIT_OF[base]](v)))
    for name, v in sorted(spec.bridged().items()):
        base = name.split("_", 1)[0]
        if name in spec.consts:
            continue
        add(f"bridge:{name}", T.Eq(T.k(base, name.split("_", 1)[1]), LIT[T.UNIT_OF[base]](v)), bridge=True)
    return ctx, facts, {}
