"""The encoder's cases, from stock/app-levy/questions-enc.jsonl ONLY (no answers; questions.jsonl's tags are not read
here). SAME-FAMILY. Conventions: encode.py C1-C7. Each record lists the facts read as true (closed world), the stated
amounts (GBP), the questions (form charged / amount / allowance, item = the person asked about) and "judgement"
(anything the encoder decided beyond copying a stated fact or a convention of encode.py: listed as "encoder judgement").
PROBES: out-of-scope cases (every answer UNSUPPORTED). No bridge: every date comparison the facts leave to the reader is
an encoder judgement (listed), never a translation input.
"""
from __future__ import annotations

FIXED = "no company is a charity and s. 103 does not apply (fixed fact of the test)"


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


C = []
# L001-L007, L023, L027-L030, L034: one employer, not connected
C.append(Case("L001").co("ashgrove").pay("ashgrove", "amy", "2000000.00").pay("ashgrove", "ben", "1600000.00")
         .q12("ashgrove").ask("allowance", "ashgrove"))
C.append(Case("L002").co("birchfield").pay("birchfield", "carl", "1200000.00").pay("birchfield", "dina", "900000.00")
         .q12("birchfield"))
C.append(Case("L003").co("cedar").pay("cedar", "eve", "1750000.00").pay("cedar", "finn", "1250000.00").q12("cedar"))
C.append(Case("L004").co("delta").pay("delta", "gail", "3100000.00").pay("delta", "hugo", "20000.00")
         .pay("delta", "iris", "4000.00", "butfor").pay("delta", "jack", "500000.00", "none").q12("delta"))
C.append(Case("L005").ind("harriet").pay("harriet", "kate", "2500000.00").pay("harriet", "liam", "1500000.00")
         .q12("harriet"))
C.append(Case("L006").co("elm").pay("elm", "mia", "400000.00", "none").pay("elm", "noah", "300000.00", "none")
         .q12("elm").ask("allowance", "elm"))
C.append(Case("L007@2026-27").co("fern").pay("fern", "olga", "2000000.00")
         .askq("L007-1", "charged", "fern").askq("L007-2", "amount", "fern"))
C.append(Case("L007@2027-28", "2027-28").co("fern").pay("fern", "olga", "2000000.00").pay("fern", "paul", "2000000.00")
         .askq("L007-3", "charged", "fern").askq("L007-4", "amount", "fern"))
# L008-L015: determinations
C.append(Case("L008").co("grove", "heath").pay("grove", "quinn", "5000000.00").pay("heath", "rosa", "2000000.00")
         .group("grove", "heath").det(grove="15000.00", heath="0.00").q12("grove", "heath")
         .ask("allowance", "heath"))
C.append(Case("L009").co("ivy", "juniper").pay("ivy", "sam", "1200000.00").pay("juniper", "tess", "1200000.00")
         .group("ivy", "juniper").det(ivy="9000.00", juniper="6000.00").q12("ivy", "juniper"))
C.append(Case("L010").co("larch", "nettle", "oak").llp("maple").pay("larch", "uri", "1000000.00")
         .pay("maple", "vic", "1800000.00").pay("maple", "wes", "1200000.00").pay("nettle", "yan", "1000000.00")
         .pay("oak", "zoe", "400000.00").group("larch", "maple", "nettle", "oak")
         .det(larch="0.00", maple="7500.00", nettle="7500.00", oak="0.00").q12("larch", "maple", "nettle", "oak"))
C.append(Case("L011").co("pine", "quarry").pay("pine", "abby", "2500000.00").pay("pine", "bart", "1500000.00")
         .pay("quarry", "cleo", "600000.00", "none").group("pine", "quarry")
         .det(pine="7500.00", quarry="7500.00").q12("pine", "quarry")
         .judge("'agreed in writing that each of them is to have a levy allowance of GBP 7,500' read as a s. 101(2) "
                "determination (detmade)"))
C.append(Case("L012").co("rowan", "sorrel").pay("rowan", "dev", "3400000.00").pay("sorrel", "ella", "3400000.00")
         .q12("rowan", "sorrel"))  # not connected on 6 April 2026 (the beginning of the tax year): no group
C.append(Case("L013").co("tamarisk", "teasel").pay("tamarisk", "fay", "2000000.00").pay("teasel", "gus", "1000000.00")
         .group("tamarisk", "teasel").det(tamarisk="15000.00", teasel="0.00").q12("tamarisk", "teasel"))
C.append(Case("L014").co("vale", "willow").pay("vale", "hal", "3000000.00").pay("willow", "ines", "3000000.00")
         .group("vale", "willow").det(vale="12000.00", willow="3000.00").alt(vale="3000.00", willow="12000.00")
         .q12("vale", "willow"))
C.append(Case("L015").co("yarrow", "zinnia").pay("yarrow", "joel", "2400000.00").pay("zinnia", "kira", "2000000.00")
         .group("yarrow", "zinnia").det(yarrow="10000.00", zinnia="8000.00").alt(yarrow="10000.00", zinnia="5000.00")
         .q12("yarrow", "zinnia").ask("allowance", "zinnia")
         .judge("'they replaced it with' read as an alteration of the determination (altmade)"))
# L016-L022, L032, L033: returns and s. 101(8)
C.append(Case("L016").co("acorn", "bramble").pay("acorn", "lars", "4000000.00").pay("bramble", "mona", "3000000.00")
         .group("acorn", "bramble").det(acorn="10000.00", bramble="5000.00").ret(acorn="15000.00", bramble="15000.00")
         .fact("notified8:acorn", "notified8:bramble", "not_taken8:g").q12("acorn", "bramble")
         .ask("allowance", "acorn"))
C.append(Case("L017").co("cobble", "dune").pay("cobble", "ned", "3000000.00").pay("dune", "opal", "1600000.00")
         .group("cobble", "dune").det(cobble="9000.00", dune="6000.00").ret(cobble="15000.00", dune="6000.00")
         .fact("notified8:cobble", "notified8:dune").q12("cobble", "dune")
         .judge("the action taken on 20 May 2027 read as taken within 'the period of 30 days beginning with 1 May "
                "2027' (date comparison by the encoder): not_taken8 false"))
C.append(Case("L018").co("ember", "flint").pay("ember", "pete", "2000000.00").pay("flint", "rhys", "1500000.00")
         .group("ember", "flint").det(ember="8000.00", flint="7000.00").ret(ember="12000.00", flint="8000.00")
         .fact("notified8:ember", "notified8:flint", "not_taken8:g").q12("ember", "flint")
         .judge("the action taken on 30 May 2027 read as NOT taken within 'the period of 21 days beginning with 2 May "
                "2027' (date comparison by the encoder): not_taken8 true"))
C.append(Case("L019").co("gorse", "holly").pay("gorse", "sara", "2600000.00").pay("holly", "theo", "2000000.00")
         .group("gorse", "holly").det(gorse="5000.00", holly="10000.00").ret(gorse="15000.00", holly="10000.00")
         .q12("gorse", "holly"))
C.append(Case("L020").co("jasper", "kelp", "lichen").pay("jasper", "una", "3000000.00").pay("kelp", "vera", "1000000.00")
         .pay("lichen", "walt", "800000.00").group("jasper", "kelp", "lichen")
         .det(jasper="5000.00", kelp="5000.00", lichen="5000.00").ret(jasper="10000.00", kelp="10000.00")
         .fact("notified8:jasper", "notified8:kelp", "not_taken8:g").q12("jasper", "kelp", "lichen"))
C.append(Case("L021").co("moss", "olive").pay("moss", "xavi", "3400000.00").pay("olive", "yuki", "600000.00")
         .group("moss", "olive").det(moss="9000.00", olive="6000.00").ret(moss="20000.00", olive="0.00")
         .fact("notified8:moss", "notified8:olive", "not_taken8:g").q12("moss", "olive"))
C.append(Case("L022").co("pebble", "quill").pay("pebble", "zack", "2000000.00").pay("quill", "ada", "1400000.00")
         .group("pebble", "quill").det(pebble="10000.00", quill="5000.00").ret(pebble="12000.00", quill="9000.00")
         .fact("notified8:pebble", "notified8:quill", "not_taken8:g").q12("pebble", "quill"))
C.append(Case("L023", "2027-28").llp("umbra").pay("umbra", "bram", "2600000.00").pay("umbra", "cara", "2400000.00")
         .q12("umbra"))
# L024-L026, L035: s. 101(13)
TOTALS = ("the stated TOTAL paid and TOTAL due and payable for the members are written on the first-named member's "
          "constants (paid_, due_) with GBP 0.00 on the others (the rule uses only the sums; representation)")
C.append(Case("L024").co("wilding", "yew", "zephyr").pay("wilding", "dan", "4000000.00").pay("yew", "edie", "1200000.00")
         .pay("zephyr", "flo", "900000.00").group("wilding", "yew", "zephyr")
         .det(wilding="15000.00", yew="0.00", zephyr="0.00")
         .fact("noreturns:g", "dues_stated:g", "notified13:wilding", "notified13:yew", "notified13:zephyr", "not_taken13:g")
         .num(paid_wilding="3000.00", paid_yew="0.00", paid_zephyr="0.00", due_wilding="15500.00", due_yew="0.00",
              due_zephyr="0.00").q12("wilding", "yew", "zephyr").ask("allowance", "yew").judge(TOTALS))
C.append(Case("L025").co("alder", "beech").pay("alder", "gwen", "1600000.00").pay("beech", "ivo", "2400000.00")
         .group("alder", "beech").det(alder="3000.00", beech="12000.00")
         .fact("noreturns:g", "dues_stated:g", "notified13:alder", "not_taken13:g")
         .num(paid_alder="0.00", paid_beech="0.00", due_alder="5000.00", due_beech="0.00").q12("alder", "beech")
         .judge(TOTALS))
C.append(Case("L026").co("dahlia").llp("elder").pay("dahlia", "jon", "2000000.00").pay("elder", "lulu", "2000000.00")
         .group("dahlia", "elder").det(dahlia="12000.00", elder="3000.00")
         .fact("noreturns:g", "dues_stated:g", "notified13:dahlia", "notified13:elder", "not_taken13:g")
         .num(paid_dahlia="7000.00", paid_elder="0.00", due_dahlia="7000.00", due_elder="0.00").q12("dahlia", "elder")
         .judge(TOTALS))
C.append(Case("L027").co("garnet").pay("garnet", "hana", "2996000.00").pay("garnet", "ivan", "6000.00", "butfor")
         .pay("garnet", "jude", "4000.00", "butfor").q12("garnet"))
C.append(Case("L028").co("sable").pay("sable", "uma", "3000123.45").fact("halfup:sable").q12("sable"))
C.append(Case("L029", "2027-28").co("tansy").pay("tansy", "yara", "3000001.00").fact("halfup:tansy").q12("tansy"))
C.append(Case("L030", "2025-26").co("vireo").pay("vireo", "kai", "1250000.00").pay("vireo", "lena", "980000.00")
         .pay("vireo", "milo", "1100000.00").pay("vireo", "nora", "7500.00", "butfor")
         .pay("vireo", "owen", "250000.00", "none").pay("vireo", "pia", "12500.00").q12("vireo"))
C.append(Case("L031").co("wisp", "yarrowby").pay("wisp", "abel", "7000.00", "butfor").pay("wisp", "bea", "5000.00", "butfor")
         .pay("yarrowby", "cy", "3000000.00").group("wisp", "yarrowby").det(wisp="10000.00", yarrowby="5000.00")
         .q12("wisp", "yarrowby"))
C.append(Case("L032").co("juno", "kite").pay("juno", "dov", "3000000.00").pay("kite", "esme", "1000000.00")
         .group("juno", "kite").det(juno="9000.00", kite="6000.00").ret(juno="6000.00", kite="6000.00")
         .fact("notified8:juno", "notified8:kite", "not_taken8:g").q12("juno", "kite"))
C.append(Case("L033", "2025-26").llp("lumen").co("marrow").pay("lumen", "finn", "3000000.00")
         .pay("marrow", "gia", "2000000.00").group("lumen", "marrow").det(lumen="5000.00", marrow="10000.00")
         .ret(lumen="20000.00", marrow="5000.00").fact("notified8:lumen", "notified8:marrow", "not_taken8:g")
         .q12("lumen", "marrow").ask("allowance", "marrow"))
C.append(Case("L034", "2027-28").co("wharf").pay("wharf", "rhea", "4000000.50").pay("wharf", "saul", "5999999.50")
         .pay("wharf", "tara", "3000000.00", "none").q12("wharf"))
C.append(Case("L035").co("bay").llp("cove").pay("bay", "hugh", "3600000.00").pay("cove", "isla", "2400000.00")
         .group("bay", "cove").det(bay="15000.00", cove="0.00")
         .fact("noreturns:g", "dues_stated:g", "notified13:bay", "notified13:cove", "not_taken13:g")
         .num(paid_bay="0.00", paid_cove="0.00", due_bay="1000.00", due_cove="0.00").q12("bay", "cove")
         .judge(TOTALS + " (for the period 6 April to 5 May 2026, 'any period in a tax year')"))

CASES = [c.record() for c in C]

PROBES = {
    "L036": "a company that is a charity (s. 102: out of scope)",
    "L037": "s. 103 applies (out of scope)",
    "L038": "continental shelf certificate (s. 100(4) regulations: out of scope)",
    "L039": "whether a payment is earnings / a Class 1 liability arises is not stated (out of scope)",
    "L040": "whether a secondary Class 1 liability arises is not stated (out of scope)",
    "L041": "the levy for a period shorter than a tax year (out of scope)",
    "L042": "apprenticeship funding drawn from the levy (out of scope)",
    "L043": "a connected company that is a charity (s. 102: out of scope)",
}
PROBE_QIDS = {"L036": ["L036-1", "L036-2"], "L037": ["L037-1", "L037-2"], "L038": ["L038-1"], "L039": ["L039-1"],
              "L040": ["L040-1"], "L041": ["L041-1"], "L042": ["L042-1"], "L043": ["L043-1", "L043-2"]}
UNSUPPORTED = {}
