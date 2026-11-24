"""Apprenticeship levy (FA 2016 ss. 99-101): TEMPLATE for the cross-family encoder: the build's record format, helpers
and conventions (encode.py C1-C7); records removed.

Each record (Case(...).record()): "id" (the case id; a case that names two tax years is one record per year, ids
<case>@<year>, encode.py C2), "year", "persons" (co / llp / ind), "earnings" (pay: one item per earner per employer, the
stated amount and liability kind), "groups" (group: companies stated connected at the beginning of the tax year), "facts"
(closed world), "ints" (stated amounts only, never computed), "questions" (qid -> form: charged = Q1, amount = Q2,
allowance = Q3; item = the person asked about; ask() numbers qids in order, askq() gives one explicitly), "judgement"
(anything the encoder decided beyond copying a stated fact or a convention of encode.py: listed as "encoder judgement").
PROBES: out-of-scope cases, id -> reason; PROBE_QIDS: id -> its qids (every answer UNSUPPORTED). UNSUPPORTED: in-scope
cases the vocabulary cannot state, id -> (reason, [qids]). No bridge: never compute a date, a period or an amount.
"""
from __future__ import annotations


class Case:
    def __init__(self, cid, year="2026-27"):
        self.cid, self.year = cid, year
        self.persons, self.earnings, self.groups = [], {}, {}
        self.facts, self.ints, self.questions, self.judgement = [], {}, [], []
        self._n = 0

    def co(self, *xs):
        for x in xs:
            self.persons.append(x)
            self.facts.append(f"company:{x}")
        return self

    def llp(self, *xs):
        for x in xs:
            self.persons.append(x)
            self.facts.append(f"llp:{x}")
        return self

    def ind(self, *xs):
        self.persons.extend(xs)
        return self

    def pay(self, payer, earner, amount, kind="liab"):
        """kind: liab (incl. a GBP 0 liability), butfor (s. 6(1)(b)), none."""
        j = f"j{earner}"
        self.earnings[j] = payer
        self.ints[f"earn_{j}"] = amount
        self.facts.append(f"sec:{j}")
        if kind in ("liab", "butfor"):
            self.facts.append(f"{kind}:{j}")
        return self

    def group(self, *xs, g="g"):
        self.groups[g] = list(xs)
        self.facts += [f"conn:{x}:{g}" for x in xs]
        return self

    def det(self, **amounts):
        self.facts.append("detmade:g")
        self.ints.update({f"det_{x}": v for x, v in amounts.items()})
        return self

    def alt(self, **amounts):
        self.facts.append("altmade:g")
        self.ints.update({f"alt_{x}": v for x, v in amounts.items()})
        return self

    def ret(self, **amounts):
        for x, v in amounts.items():
            self.facts += [f"ret9:{x}", f"aware:{x}"]
            self.ints[f"ret_{x}"] = v
        return self

    def fact(self, *fs):
        self.facts += list(fs)
        return self

    def num(self, **kv):
        self.ints.update(kv)
        return self

    def ask(self, form, item):
        self._n += 1
        self.questions.append({"qid": f"{self.cid.split('@')[0]}-{self._n}", "form": form, "item": item})
        return self

    def askq(self, qid, form, item):
        self.questions.append({"qid": qid, "form": form, "item": item})
        return self

    def q12(self, *xs):
        for x in xs:
            self.ask("charged", x).ask("amount", x)
        return self

    def judge(self, text):
        self.judgement.append(text)
        return self

    def record(self):
        return {"id": self.cid, "year": self.year, "persons": self.persons, "earnings": self.earnings,
                "groups": self.groups, "facts": self.facts, "ints": self.ints, "questions": self.questions,
                "judgement": self.judgement}


Z = "0.00"
JAWARE = "HMRC aware of the returns at the assessment time: knows from 2 March 2027, before 5 April 2027 (date compared)"
JNT = ("remedial action not taken within the notice period (ends 16 March 2027, before the assessment time; "
       "none taken up to then)")


def single(cid, x, kind, pays):
    """One employer, no group; pays: [(earner, amount, liability kind)]; paid GBP 0, due GBP 0 as stated."""
    c = Case(cid)
    (c.co if kind == "co" else c.ind)(x)
    for e, a, lk in pays:
        c.pay(x, e, a, lk)
    return c.num(**{f"paid_{x}": Z, f"due_{x}": Z}).q12(x)


def zero_dues(c, *xs):
    return c.num(**{f"paid_{x}": Z for x in xs}, **{f"due_{x}": Z for x in xs}).fact("dues_stated:g")


C = [
    single("L001", "Alice", "ind", [("Ben", "2000000.00", "liab")]),
    single("L002", "Clara", "co", [("David", "3000000.00", "liab")]),
    single("L003", "Edith", "co", [("Felix", "3000002.00", "liab")]),
    single("L004", "Grace", "co", [("Hugo", "0.00", "none")]),
    single("L005", "Iris", "co", [("Jack", "1200000.00", "liab"), ("Kate", "1600000.00", "liab")]),
    single("L006", "Leo", "ind", [("Maya", "2100000.00", "liab"), ("Noah", "1000000.00", "liab")]),
    single("L007", "Olive", "co", [("Paul", "1000.00", "butfor")]),
    single("L008", "Rosa", "co", [("Sam", "3000000.00", "liab"), ("Tara", "2.00", "butfor")]),
    single("L009", "Uma", "co", [("Victor", "2800000.00", "liab"), ("Wendy", "900000.00", "none")]),
    single("L010", "Xena", "co", [("Yuri", "3100000.00", "liab")]),
    single("L011", "Zoe", "co", [("Adam", "2000000.00", "liab"), ("Bella", "1200000.00", "liab")]),
    single("L012", "Chloe", "ind", [("Dylan", "2999900.00", "liab"), ("Emma", "200.00", "butfor")]),
    single("L013", "Finn", "co", [("Gemma", "4000000.00", "none")]),
    single("L014", "Hannah", "ind", []),
    single("L015", "Isaac", "co", []),
    single("L016", "Julia", "ind", [("Kevin", "2999998.00", "liab")]),
    single("L017", "Lena", "co", [("Mark", "4000000.00", "liab")]),
    single("L018", "Nina", "co", [("Oscar", "600000.00", "liab"), ("Pia", "700000.00", "liab"),
                                  ("Quinn", "800000.00", "liab"), ("Ravi", "900000.00", "liab")]),
    single("L019", "Sara", "ind", [("Theo", "800000.00", "liab"), ("Ursula", "900000.00", "liab"),
                                   ("Vera", "1400000.00", "liab")]),
    single("L020", "Will", "co", [("Yasmin", "4000000.00", "liab"), ("Zara", "600.00", "butfor"),
                                  ("Abel", "200000.00", "none")]),
    single("L021", "Beth", "ind", [("Carl", "3000200.00", "none"), ("Dora", "100.00", "butfor")]),
    single("L022", "Evan", "co", [("Faye", "3200000.00", "liab"), ("Glen", "800.00", "butfor")]),
    single("L023", "Hope", "co", [("Ivan", "1000000.00", "liab"), ("Jade", "1000000.00", "liab"),
                                  ("Kian", "1000000.00", "liab"), ("Lily", "200.00", "liab")]),
    single("L024", "Milo", "co", [("Nora", "3000004.00", "liab")]),

    zero_dues(Case("L025").llp("Alma").co("Bea").group("Alma", "Bea")
              .pay("Alma", "Eli", "3000000.00").pay("Bea", "Flo", "1000000.00")
              .det(Alma="15000.00", Bea="0.00").fact("noreturns:g"), "Alma", "Bea")
    .q12("Alma", "Bea").ask("allowance", "Bea"),

    zero_dues(Case("L026").co("Alma", "Bea", "Cora").group("Alma", "Bea", "Cora")
              .pay("Alma", "Eli", "2000000.00").pay("Bea", "Flo", "1000000.00").pay("Cora", "Gus", "800000.00")
              .det(Alma="7000.00", Bea="5000.00", Cora="3000.00").fact("noreturns:g"), "Alma", "Bea", "Cora")
    .q12("Alma", "Bea", "Cora"),

    zero_dues(Case("L027").co("Alma", "Bea", "Cora", "Dana").group("Alma", "Bea", "Cora", "Dana")
              .pay("Alma", "Eli", "200000.00").pay("Bea", "Flo", "600000.00").pay("Cora", "Gus", "1000000.00")
              .pay("Dana", "Hana", "2000000.00")
              .det(Alma="0.00", Bea="2500.00", Cora="5000.00", Dana="7500.00").fact("noreturns:g"),
              "Alma", "Bea", "Cora", "Dana")
    .q12("Alma", "Bea", "Cora", "Dana"),

    zero_dues(Case("L028").co("Alma", "Bea").group("Alma", "Bea")
              .pay("Alma", "Eli", "2000000.00").pay("Bea", "Flo", "1200000.00")
              .det(Alma="10000.00", Bea="5000.00").alt(Alma="8000.00", Bea="7000.00").fact("noreturns:g"),
              "Alma", "Bea")
    .q12("Alma", "Bea").ask("allowance", "Alma")
    .judge("the members' 1 February 2027 agreement 'instead to assign' read as an alteration of the determination"),

    zero_dues(Case("L029").co("Alma", "Bea").group("Alma", "Bea")
              .pay("Alma", "Eli", "2000000.00").pay("Bea", "Flo", "1200000.00")
              .det(Alma="7000.00", Bea="6000.00").alt(Alma="9000.00", Bea="6000.00").fact("noreturns:g"),
              "Alma", "Bea")
    .q12("Alma", "Bea").ask("allowance", "Alma"),

    zero_dues(Case("L030").co("Alma", "Bea").group("Alma", "Bea")
              .pay("Alma", "Eli", "2000000.00").pay("Bea", "Flo", "2000000.00")
              .det(Alma="9000.00", Bea="6000.00").ret(Alma="12000.00", Bea="10000.00"), "Alma", "Bea")
    .q12("Alma", "Bea").judge(JAWARE),

    zero_dues(Case("L031").co("Alma", "Bea").group("Alma", "Bea")
              .pay("Alma", "Eli", "2000000.00").pay("Bea", "Flo", "2000000.00")
              .det(Alma="7500.00", Bea="7500.00").ret(Alma="12000.00", Bea="10000.00")
              .fact("notified8:Alma", "notified8:Bea"), "Alma", "Bea")
    .q12("Alma", "Bea").judge(JAWARE)
    .judge("remedial action taken on 10 March 2027, within the period 2-16 March 2027 (date compared): not_taken8 "
           "absent; the corrections are not returns, so the returns' amounts stand"),

    zero_dues(Case("L032").co("Alma", "Bea", "Cora", "Dana").group("Alma", "Bea", "Cora", "Dana")
              .pay("Alma", "Eli", "2000000.00").pay("Bea", "Flo", "2000000.00").pay("Cora", "Gus", "2000000.00")
              .pay("Dana", "Hana", "2000000.00")
              .det(Alma="8000.00", Bea="4000.00", Cora="3000.00", Dana="0.00")
              .ret(Alma="12000.00", Bea="8000.00", Cora="0.00")
              .fact("notified8:Alma", "notified8:Bea", "notified8:Cora", "not_taken8:g"),
              "Alma", "Bea", "Cora", "Dana")
    .q12("Alma", "Bea", "Cora", "Dana").ask("allowance", "Dana").judge(JAWARE).judge(JNT),

    zero_dues(Case("L033").co("Alma", "Bea").group("Alma", "Bea")
              .pay("Alma", "Eli", "428572.00").pay("Bea", "Flo", "4000000.00")
              .det(Alma="7500.00", Bea="7500.00").ret(Alma="3000.00", Bea="18000.00")
              .fact("notified8:Alma", "notified8:Bea", "not_taken8:g"), "Alma", "Bea")
    .q12("Alma", "Bea").ask("allowance", "Alma").judge(JAWARE).judge(JNT)
    .judge("HMRC's stated s. 101(7) roundings (Alma up to 2,142.86, Bea down to 12,857.14) not encoded: the "
           "vocabulary's rnd_* facts are for s. 101(12) shares only"),

    Case("L034").co("Alma", "Bea").group("Alma", "Bea")
    .pay("Alma", "Eli", "4000000.00").pay("Bea", "Flo", "4000000.00")
    .det(Alma="9000.00", Bea="6000.00").fact("noreturns:g", "dues_stated:g")
    .num(paid_Alma="5000.00", due_Alma="11000.00", paid_Bea="10000.00", due_Bea="14000.00")
    .fact("notified13:Alma", "notified13:Bea", "not_taken13:g")
    .q12("Alma", "Bea")
    .judge("the amounts paid and due and payable at 2 March 2027 (stated as used in the notice decision) taken as "
           "s. 101(13)(a)'s amounts").judge(JNT),

    Case("L035").co("Alma", "Bea", "Cora").group("Alma", "Bea", "Cora")
    .pay("Alma", "Eli", "4000000.00").pay("Bea", "Flo", "4000000.00").pay("Cora", "Gus", "4000000.00")
    .det(Alma="9000.00", Bea="6000.00", Cora="0.00").ret(Alma="0.00").fact("dues_stated:g")
    .num(paid_Alma="5000.00", due_Alma="11000.00", paid_Bea="10000.00", due_Bea="14000.00",
         paid_Cora="20000.00", due_Cora="20000.00")
    .fact("notified13:Alma", "notified13:Bea", "notified13:Cora", "not_taken13:g", "insufficient:g")
    .q12("Alma", "Bea", "Cora").ask("allowance", "Bea")
    .judge("insufficient: Alma's sole return (GBP 0, silent on Bea and Cora), the determination not communicated, read "
           "as returns not enabling HMRC to determine how the whole GBP 15,000 is used (s. 101(13)(b))")
    .judge("the amounts paid and due and payable at 2 March 2027 (stated as used in the notice decision) taken as "
           "s. 101(13)(a)'s amounts").judge("HMRC aware of Alma's return: knows the return facts on 2 March 2027")
    .judge(JNT),
]

CASES = [c.record() for c in C]

PROBES = {
    "L036": "Alma is a charity (s. 102; fixed fact of the build: no charity)",
    "L037": "s. 103 applies to Alma (fixed fact of the build: s. 103 does not apply)",
    "L038": "s. 100(4) regulations for continental shelf certificates (content not given; not in the vocabulary)",
    "L039": "a one-month levy period, not a tax year (one context = one tax year)",
}
PROBE_QIDS = {
    "L036": ["L036-1", "L036-2", "L036-3"],
    "L037": ["L037-1", "L037-2", "L037-3"],
    "L038": ["L038-1", "L038-2"],
    "L039": ["L039-1", "L039-2"],
}
UNSUPPORTED = {}
