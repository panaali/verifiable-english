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
J_CONN = "connected at 00:00 on 6 April 2026 read as at the beginning of the tax year (conn)"
J_AWARE = "HMRC knowing the returns from 2 March 2027 read as aware at the assessment time (aware)"
J_NOTTAKEN = "no action up to the 5 April 2027 assessment read as not taken within the 2-16 March 2027 period"
J_PAID = "paid / due are the stated figures at 2 March 2027 for the tax year (no later payment)"


def single(cid, who, kind, pays):
    """One employer, no group (C3, C5); pays: (earner, amount, liability kind); paid and due as stated (C6)."""
    c = Case(cid)
    getattr(c, kind)(who)
    for earner, amount, lk in pays:
        c.pay(who, earner, amount, lk)
    return c.num(**{f"paid_{who}": Z, f"due_{who}": Z}).q12(who)


def zero_paid(c, *xs):
    """Each member stated to have paid GBP 0 with GBP 0 due and payable (C6)."""
    return c.num(**{f"{b}_{x}": Z for x in xs for b in ("paid", "due")}).fact("dues_stated:g")


C = [
    single("L001", "alice", "ind", [("ben", "2000000.00", "liab")]),
    single("L002", "clara", "co", [("david", "3000000.00", "liab")]),
    single("L003", "edith", "co", [("felix", "3000002.00", "liab")]),
    single("L004", "grace", "co", [("hugo", "0.00", "none")]),
    single("L005", "iris", "co", [("jack", "1200000.00", "liab"), ("kate", "1600000.00", "liab")]),
    single("L006", "leo", "ind", [("maya", "2100000.00", "liab"), ("noah", "1000000.00", "liab")]),
    single("L007", "olive", "co", [("paul", "1000.00", "butfor")]),
    single("L008", "rosa", "co", [("sam", "3000000.00", "liab"), ("tara", "2.00", "butfor")]),
    single("L009", "uma", "co", [("victor", "2800000.00", "liab"), ("wendy", "900000.00", "none")]),
    single("L010", "xena", "co", [("yuri", "3100000.00", "liab")]),
    single("L011", "zoe", "co", [("adam", "2000000.00", "liab"), ("bella", "1200000.00", "liab")]),
    single("L012", "chloe", "ind", [("dylan", "2999900.00", "liab"), ("emma", "200.00", "butfor")]),
    single("L013", "finn", "co", [("gemma", "4000000.00", "none")]),
    single("L014", "hannah", "ind", []),
    single("L015", "isaac", "co", []),
    single("L016", "julia", "ind", [("kevin", "2999998.00", "liab")]),
    single("L017", "lena", "co", [("mark", "4000000.00", "liab")]),
    single("L018", "nina", "co", [("oscar", "600000.00", "liab"), ("pia", "700000.00", "liab"),
                                  ("quinn", "800000.00", "liab"), ("ravi", "900000.00", "liab")]),
    single("L019", "sara", "ind", [("theo", "800000.00", "liab"), ("ursula", "900000.00", "liab"),
                                   ("vera", "1400000.00", "liab")]),
    single("L020", "will", "co", [("yasmin", "4000000.00", "liab"), ("zara", "600.00", "butfor"),
                                  ("abel", "200000.00", "none")]),
    single("L021", "beth", "ind", [("carl", "3000200.00", "none"), ("dora", "100.00", "butfor")]),
    single("L022", "evan", "co", [("faye", "3200000.00", "liab"), ("glen", "800.00", "butfor")]),
    single("L023", "hope", "co", [("ivan", "1000000.00", "liab"), ("jade", "1000000.00", "liab"),
                                  ("kian", "1000000.00", "liab"), ("lily", "200.00", "liab")]),
    single("L024", "milo", "co", [("nora", "3000004.00", "liab")]),

    zero_paid(Case("L025").llp("alma").co("bea").group("alma", "bea")
              .pay("alma", "eli", "3000000.00").pay("bea", "flo", "1000000.00")
              .det(alma="15000.00", bea="0.00").fact("noreturns:g"), "alma", "bea")
    .q12("alma", "bea").ask("allowance", "bea").judge(J_CONN),

    zero_paid(Case("L026").co("alma", "bea", "cora").group("alma", "bea", "cora")
              .pay("alma", "eli", "2000000.00").pay("bea", "flo", "1000000.00").pay("cora", "gus", "800000.00")
              .det(alma="7000.00", bea="5000.00", cora="3000.00").fact("noreturns:g"), "alma", "bea", "cora")
    .q12("alma", "bea", "cora").judge(J_CONN),

    zero_paid(Case("L027").co("alma", "bea", "cora", "dana").group("alma", "bea", "cora", "dana")
              .pay("alma", "eli", "200000.00").pay("bea", "flo", "600000.00").pay("cora", "gus", "1000000.00")
              .pay("dana", "hana", "2000000.00")
              .det(alma="0.00", bea="2500.00", cora="5000.00", dana="7500.00").fact("noreturns:g"),
              "alma", "bea", "cora", "dana")
    .q12("alma", "bea", "cora", "dana").judge(J_CONN),

    zero_paid(Case("L028").co("alma", "bea").group("alma", "bea")
              .pay("alma", "eli", "2000000.00").pay("bea", "flo", "1200000.00")
              .det(alma="10000.00", bea="5000.00").alt(alma="8000.00", bea="7000.00").fact("noreturns:g"),
              "alma", "bea")
    .q12("alma", "bea").ask("allowance", "alma").judge(J_CONN)
    .judge("the members' 1 February 2027 agreement to assign 8,000 / 7,000 'instead' read as an alteration (altmade)"),

    zero_paid(Case("L029").co("alma", "bea").group("alma", "bea")
              .pay("alma", "eli", "2000000.00").pay("bea", "flo", "1200000.00")
              .det(alma="7000.00", bea="6000.00").alt(alma="9000.00", bea="6000.00").fact("noreturns:g"),
              "alma", "bea")
    .q12("alma", "bea").ask("allowance", "alma").judge(J_CONN),

    zero_paid(Case("L030").co("alma", "bea").group("alma", "bea")
              .pay("alma", "eli", "2000000.00").pay("bea", "flo", "2000000.00")
              .det(alma="9000.00", bea="6000.00").ret(alma="12000.00", bea="10000.00"), "alma", "bea")
    .q12("alma", "bea").judge(J_CONN).judge(J_AWARE),

    zero_paid(Case("L031").co("alma", "bea").group("alma", "bea")
              .pay("alma", "eli", "2000000.00").pay("bea", "flo", "2000000.00")
              .det(alma="7500.00", bea="7500.00").ret(alma="12000.00", bea="10000.00")
              .fact("notified8:alma", "notified8:bea"), "alma", "bea")
    .q12("alma", "bea").judge(J_CONN).judge(J_AWARE)
    .judge("action taken on 10 March 2027 read as within the 2-16 March 2027 period (not_taken8 absent)"),

    zero_paid(Case("L032").co("alma", "bea", "cora", "dana").group("alma", "bea", "cora", "dana")
              .pay("alma", "eli", "2000000.00").pay("bea", "flo", "2000000.00").pay("cora", "gus", "2000000.00")
              .pay("dana", "hana", "2000000.00")
              .det(alma="8000.00", bea="4000.00", cora="3000.00", dana="0.00")
              .ret(alma="12000.00", bea="8000.00", cora="0.00")
              .fact("notified8:alma", "notified8:bea", "notified8:cora", "not_taken8:g"),
              "alma", "bea", "cora", "dana")
    .q12("alma", "bea", "cora", "dana").ask("allowance", "dana").judge(J_CONN).judge(J_AWARE).judge(J_NOTTAKEN),

    zero_paid(Case("L033").co("alma", "bea").group("alma", "bea")
              .pay("alma", "eli", "428572.00").pay("bea", "flo", "4000000.00")
              .det(alma="7500.00", bea="7500.00").ret(alma="3000.00", bea="18000.00")
              .fact("notified8:alma", "notified8:bea", "not_taken8:g"), "alma", "bea")
    .q12("alma", "bea").ask("allowance", "alma").judge(J_CONN).judge(J_AWARE).judge(J_NOTTAKEN)
    .judge("HMRC's stated s. 101(7) roundings (2,142.86 up, 12,857.14 down) not encoded: rnd_* state s. 101(12) only"),

    Case("L034").co("alma", "bea").group("alma", "bea")
    .pay("alma", "eli", "4000000.00").pay("bea", "flo", "4000000.00")
    .det(alma="9000.00", bea="6000.00").fact("noreturns:g")
    .num(paid_alma="5000.00", due_alma="11000.00", paid_bea="10000.00", due_bea="14000.00").fact("dues_stated:g")
    .fact("notified13:alma", "notified13:bea", "not_taken13:g")
    .q12("alma", "bea").judge(J_CONN).judge(J_NOTTAKEN).judge(J_PAID),

    Case("L035").co("alma", "bea", "cora").group("alma", "bea", "cora")
    .pay("alma", "eli", "4000000.00").pay("bea", "flo", "4000000.00").pay("cora", "gus", "4000000.00")
    .det(alma="9000.00", bea="6000.00", cora="0.00").ret(alma="0.00")
    .num(paid_alma="5000.00", due_alma="11000.00", paid_bea="10000.00", due_bea="14000.00",
         paid_cora="20000.00", due_cora="20000.00").fact("dues_stated:g")
    .fact("insufficient:g", "notified13:alma", "notified13:bea", "notified13:cora", "not_taken13:g")
    .q12("alma", "bea", "cora").ask("allowance", "bea").judge(J_CONN).judge(J_NOTTAKEN).judge(J_PAID)
    .judge("HMRC knowing the return on 2 March 2027 read as aware at the assessment time (aware)")
    .judge("Alma's return silent on Bea, Cora and their allowance, determination not communicated: read as "
           "insufficient (s. 101(13)(b))"),
]

CASES = [c.record() for c in C]

PROBES = {
    "L036": "Alma is a charity (s. 102; charity out of scope)",
    "L037": "s. 103 applies to Alma (out of scope)",
    "L038": "s. 100(4) continental-shelf certificate and regulations (content not given; out of scope)",
    "L039": "the question is about a one-month period, not a tax year (out of scope)",
}
PROBE_QIDS = {
    "L036": ["L036-1", "L036-2", "L036-3"],
    "L037": ["L037-1", "L037-2", "L037-3"],
    "L038": ["L038-1", "L038-2"],
    "L039": ["L039-1", "L039-2"],
}
UNSUPPORTED = {}
