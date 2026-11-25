"""The encoder's transcription of questions-enc.jsonl: one record per AWARD (template; fill CASES, PROBES, PROBE_QIDS).

Each record: persons (lowercase ids), the anchor (the person the question names), the true unary facts per person (closed
world, encode.py C1), the links (C2), the stated integers (C3: ages, incomes, housing), the questions (form: max / award /
claim), and "judgement": every reading beyond copying a stated fact (encoder judgement).
award(aid, case, anchor, adults, young, facts, links, housing, qids, judgement): aid = record id (the case id, or
"<case>a"/"<case>b" when a case asks about two awards); qids = the numbers n of "<case>-<n>" this record answers (Q1, Q2, Q3
in that order: (1, 2, 3), or (4, 5, 6) for a second award).
"""
from __future__ import annotations

Q = {"Q1": "max", "Q2": "award", "Q3": "claim"}


def award(aid, case, anchor, adults, young=None, facts=None, links=(), housing="0.00", qids=(1, 2, 3), judgement=()):
    """adults: {person: (age or None, earned, unearned)}; young: {person: [facts]} (child/qyp + others)."""
    young = young or {}
    fs = {p: list(v) for p, v in (facts or {}).items()}
    for y, v in young.items():
        fs.setdefault(y, [])
        fs[y] += v
    ints = {f"housing_{aid.lower()}": housing}
    for p, (age, earn, unearn) in adults.items():
        if age is not None:
            ints[f"age_{p}"] = age
        ints[f"earn_{p}"] = earn
        ints[f"unearn_{p}"] = unearn
    persons = list(adults) + [y for y in young if y not in adults]
    kinds = ("Q1", "Q2", "Q3")
    return {"id": aid, "case": case, "anchor": anchor, "persons": persons, "facts": fs, "links": [list(l) for l in links],
            "ints": ints, "questions": [{"qid": f"{case}-{n}", "form": Q[kinds[(n - 1) % 3]]} for n in qids],
            "judgement": list(judgement)}


def lives(y, *xs):
    return [("lives", y, x) for x in xs]


NONE = ("0.00", "0.00")

# Conventions used below: every person with a stated age / earned / unearned income goes in the adults dict (children too:
# their stated age and 0.00 incomes are transcribed; the translation counts income only for claimants); child / qyp
# statuses and other unary facts go in young / facts; "X normally lives with Y" for a child or qyp X is lives(x, y).
Y = "0.00"
CHILD = ["child"]
POLY = [("couple", "ann", "bob"), ("couple", "bob", "cara"), ("married", "bob", "ann"), ("married", "bob", "cara"),
        ("poly_law", "bob", "ann"), ("poly_law", "bob", "cara"), ("earlier", "bob", "ann")]
EARLIER = "earlier(bob, ann): Bob's marriage to Ann (2018) precedes his marriage to Cara (2020) and still subsists"

CASES = [
    # ---- single claimants, no children ----
    award("U001", "U001", "ann", {"ann": ("24", "200.00", "10.17")}),
    award("U002", "U002", "ann", {"ann": ("25", "0.00", "25.13")}, housing="300.00"),
    # ---- couples, no children ----
    award("U003", "U003", "ann", {"ann": ("22", "300.00", "10.01"), "bob": ("24", "100.00", "5.02")},
          links=[("couple", "ann", "bob")]),
    award("U004", "U004", "ann", {"ann": ("24", "400.00", "30.00"), "bob": ("25", "200.00", "20.00")},
          links=[("couple", "ann", "bob")], housing="400.00"),
    # ---- children ----
    award("U005", "U005", "ann", {"ann": ("30", "600.00", Y), "cara": ("8", Y, Y)}, young={"cara": CHILD},
          links=lives("cara", "ann")),
    award("U006", "U006", "ann", {"ann": ("24", "710.00", Y), "cara": ("8", Y, Y), "dan": ("6", Y, Y)},
          young={"cara": CHILD, "dan": CHILD}, links=lives("cara", "ann") + lives("dan", "ann")),
    award("U007", "U007", "ann", {"ann": ("25", "1000.00", "20.25"), "cara": ("8", Y, Y), "dan": ("6", Y, Y),
                                  "eva": ("4", Y, Y)},
          young={"cara": ["child", "dis_lower"], "dan": ["child", "dis_lower", "dis_higher"],
                 "eva": ["child", "dis_higher"]},
          links=lives("cara", "ann") + lives("dan", "ann") + lives("eva", "ann"),
          judgement=["dan: CDP care component at the highest rate (reg. 11(5) DACYP) read as dis_lower (entitled to "
                     "CDP) and dis_higher (reg. 24(2)(b)(i))",
                     "eva: certified blind read as dis_higher (reg. 24(2)(b)(ii)); no benefit entitlement stated, so "
                     "no dis_lower"]),
    award("U008", "U008", "ann", {"ann": ("23", "400.00", Y), "bob": ("24", "200.00", Y), "cara": ("8", Y, Y)},
          young={"cara": CHILD}, links=[("couple", "ann", "bob")] + lives("cara", "ann", "bob")),
    award("U009", "U009", "ann", {"ann": ("24", "400.00", Y), "bob": ("30", "310.00", Y), "cara": ("8", Y, Y)},
          young={"cara": CHILD}, links=[("couple", "ann", "bob")] + lives("cara", "ann", "bob")),
    award("U010", "U010", "ann", {"ann": ("35", "700.00", "10.11"), "bob": ("36", "300.00", "20.22"),
                                  "cara": ("8", Y, Y), "dan": ("6", Y, Y)},
          young={"cara": ["child", "dis_lower"], "dan": ["child", "dis_lower", "dis_higher"]},
          facts={"bob": ["carer_el"]},
          links=[("couple", "ann", "bob")] + lives("cara", "ann", "bob") + lives("dan", "ann", "bob"),
          judgement=["cara: ADP daily living component at the standard rate read as dis_lower only",
                     "dan: PIP daily living component at the enhanced rate read as dis_lower and dis_higher "
                     "(reg. 24(2)(b)(i))"]),
    # ---- limited capability for work, LCWRA, carer ----
    award("U011", "U011", "ann", {"ann": ("24", "300.00", Y)}, facts={"ann": ["lcw"]}, housing="200.00"),
    award("U012", "U012", "ann", {"ann": ("25", "427.00", Y)}, facts={"ann": ["lcw", "lcwra_el"]}, housing="300.00"),
    award("U013", "U013", "ann", {"ann": ("40", "800.00", "12.34")}, facts={"ann": ["lcw", "lcwra_el", "pre2026"]},
          housing="350.00"),
    award("U014", "U014", "ann", {"ann": ("23", "100.00", Y), "bob": ("24", "200.00", Y)}, facts={"ann": ["lcw"]},
          links=[("couple", "ann", "bob")], housing="250.00"),
    award("U015", "U015", "ann", {"ann": ("24", "200.00", Y), "bob": ("25", "227.00", Y)},
          facts={"bob": ["lcw", "lcwra_el", "pre2026"]}, links=[("couple", "ann", "bob")], housing="400.00",
          judgement=["bob: 'severe conditions criteria claimant' entered as pre2026 (the fact names all three statuses)"]),
    award("U016", "U016", "ann", {"ann": ("31", "600.00", Y), "bob": ("32", "400.00", Y)},
          facts={"ann": ["lcw", "lcwra_el", "pre2026"], "bob": ["carer_el"]}, links=[("couple", "ann", "bob")],
          housing="450.00",
          judgement=["ann: 'terminally ill' entered as pre2026 (the fact names all three statuses)"]),
    # ---- shared care: two awards ----
    award("U017a", "U017", "ann", {"ann": ("30", "800.00", Y), "bob": ("31", "200.00", Y), "cara": ("8", Y, Y)},
          young={"cara": CHILD}, links=lives("cara", "ann", "bob") + [("main_judged", "ann", "cara")]),
    award("U017b", "U017", "bob", {"ann": ("30", "800.00", Y), "bob": ("31", "200.00", Y), "cara": ("8", Y, Y)},
          young={"cara": CHILD}, links=lives("cara", "ann", "bob") + [("main_judged", "ann", "cara")], qids=(4, 5, 6)),
    award("U018a", "U018", "ann", {"ann": ("30", "600.00", Y), "bob": ("31", "600.00", Y), "cara": ("8", Y, Y)},
          young={"cara": ["qyp", "nom_any"]}, links=lives("cara", "ann", "bob") + [("nominated", "bob", "cara")],
          housing="200.00"),
    award("U018b", "U018", "bob", {"ann": ("30", "600.00", Y), "bob": ("31", "600.00", Y), "cara": ("8", Y, Y)},
          young={"cara": ["qyp", "nom_any"]}, links=lives("cara", "ann", "bob") + [("nominated", "bob", "cara")],
          housing="200.00", qids=(4, 5, 6)),
    award("U019a", "U019", "ann", {"ann": ("30", "600.00", Y), "bob": ("31", "800.00", Y), "cara": ("8", Y, Y)},
          young={"cara": ["child", "nom_any", "sos_any"]},
          links=lives("cara", "ann", "bob") + [("nominated", "ann", "cara"), ("sos_det", "bob", "cara")]),
    award("U019b", "U019", "bob", {"ann": ("30", "600.00", Y), "bob": ("31", "800.00", Y), "cara": ("8", Y, Y)},
          young={"cara": ["child", "nom_any", "sos_any"]},
          links=lives("cara", "ann", "bob") + [("nominated", "ann", "cara"), ("sos_det", "bob", "cara")],
          qids=(4, 5, 6)),
    # ---- qualifying young person as partner ----
    award("U020", "U020", "ann", {"ann": ("18", "100.00", Y), "bob": ("9", "100.00", Y)},
          young={"bob": ["qyp", "fails_a"]},
          links=[("couple", "ann", "bob"), ("living_couple", "ann", "bob")] + lives("bob", "ann"),
          judgement=["lives(bob, ann) from 'Ann and Bob ... normally live with each other' (Bob is a qyp)"]),
    # ---- reg. 4(6), 4(7) ----
    award("U021", "U021", "ann", {"ann": ("30", "100.00", Y), "cara": ("8", Y, Y), "dan": ("6", Y, Y)},
          young={"cara": ["child", "la_care"], "dan": ["child", "prisoner"]},
          links=lives("cara", "ann") + lives("dan", "ann"), housing="200.00"),
    award("U022", "U022", "ann", {"ann": ("30", "800.00", Y), "cara": ("8", Y, Y)},
          young={"cara": ["child", "temp_absent"]}, links=lives("cara", "ann")),
    award("U023", "U023", "ann", {"ann": ("30", "200.00", Y), "cara": ("8", Y, Y)},
          young={"cara": ["child", "temp_absent", "abs_over6"]}, links=lives("cara", "ann")),
    award("U024", "U024", "ann", {"ann": ("30", "800.00", Y), "cara": ("8", Y, Y)},
          young={"cara": ["child", "temp_absent", "abs_from_gb"]}, links=lives("cara", "ann")),
    award("U025", "U025", "ann", {"ann": ("30", "200.00", Y), "cara": ("8", Y, Y)},
          young={"cara": ["child", "temp_absent", "abs_from_gb", "abs_over1m"]}, links=lives("cara", "ann")),
    award("U026", "U026", "ann", {"ann": ("30", "800.00", Y), "cara": ("8", Y, Y)},
          young={"cara": ["child", "temp_absent", "abs_from_gb", "abs_over1m", "reg11_circ"]},
          links=lives("cara", "ann")),
    award("U027", "U027", "ann", {"ann": ("30", "200.00", Y), "cara": ("8", Y, Y)},
          young={"cara": ["child", "temp_absent", "abs_from_gb", "abs_over6", "reg11_circ"]},
          links=lives("cara", "ann")),
    # ---- reg. 3(2), 3(3) ----
    award("U028", "U028", "ann", {"ann": ("70", "600.00", Y), "bob": ("30", "400.00", Y), "cara": ("8", Y, Y)},
          young={"cara": CHILD}, facts={"ann": ["fails_b"]},
          links=[("couple", "ann", "bob")] + lives("cara", "ann", "bob")),
    award("U029", "U029", "ann", {"ann": ("24", "100.00", Y), "bob": ("26", "200.00", Y)}, facts={"ann": ["fails_d"]},
          links=[("couple", "ann", "bob")], housing="200.00"),
    award("U030", "U030", "ann", {"ann": ("30", "600.00", "5.00"), "bob": ("32", "400.00", "10.00")},
          facts={"ann": ["lcw"], "bob": ["temp_absent", "abs_from_gb", "fails_c"]},
          links=[("couple", "ann", "bob")], housing="300.00"),
    award("U031", "U031", "ann", {"ann": ("30", "300.00", Y), "bob": ("32", "500.00", Y)},
          facts={"bob": ["prisoner", "lcw"]}, links=[("couple", "ann", "bob")]),
    award("U032", "U032", "ann", {"ann": ("24", "500.00", "10.00"), "bob": ("32", "100.00", "5.00"),
                                  "cara": ("8", Y, Y)},
          young={"cara": CHILD}, facts={"bob": ["reg19"]},
          links=[("couple", "ann", "bob")] + lives("cara", "ann", "bob"), housing="200.00"),
    award("U033", "U033", "ann", {"ann": ("30", "100.00", Y), "bob": ("32", "200.00", "20.00")},
          facts={"bob": ["s115"]}, links=[("couple", "ann", "bob")]),
    # ---- polygamous marriages: two awards ----
    award("U034a", "U034", "ann", {"ann": ("35", "100.00", Y), "bob": ("40", "200.00", Y), "cara": ("28", "100.00", Y)},
          facts={x: ["same_household"] for x in ("ann", "bob", "cara")}, links=POLY,
          judgement=["same_household on all three from 'are living in the same household'", EARLIER]),
    award("U034b", "U034", "cara", {"ann": ("35", "100.00", Y), "bob": ("40", "200.00", Y), "cara": ("28", "100.00", Y)},
          facts={x: ["same_household"] for x in ("ann", "bob", "cara")}, links=POLY, qids=(4, 5, 6),
          judgement=["same_household on all three from 'are living in the same household'", EARLIER]),
    award("U035a", "U035", "ann", {"ann": ("35", "800.00", Y), "bob": ("40", "200.00", Y), "cara": ("28", "100.00", Y)},
          facts={"ann": ["lcw"], "bob": ["temp_absent", "abs_over6"]}, links=POLY,
          judgement=[EARLIER, "same_household false for bob and cara (Ann stated not in their household)"]),
    award("U035b", "U035", "bob", {"ann": ("35", "800.00", Y), "bob": ("40", "200.00", Y), "cara": ("28", "100.00", Y)},
          facts={"ann": ["lcw"], "bob": ["temp_absent", "abs_over6"]}, links=POLY, housing="300.00", qids=(4, 5, 6),
          judgement=[EARLIER, "temp_absent/abs_over6 kept on bob as stated (Bob absent from Ann's household), none on "
                     "ann; same_household false for ann (stated), not stated for cara"]),
]

PROBES = {  # out-of-scope case id -> one line: what the case needs that the frozen translation does not state
    "U041": "childcare costs element and its one-child maximum (reg. 34 / table row not written; amount not supplied)",
    "U042": "childcare costs element and its two-or-more-children maximum (reg. 34 / table row not written)",
    "U043": "benefit cap, transitional element / protection, sanctions and other reductions (outside the pin)",
    "U044": "calculation of earned and unearned income from wages, tax, self-employment and capital (Part 6, MIF)",
    "U045": "the amount of the housing costs element from rent (reg. 26 and Sch. 4 not pinned; amount not supplied)",
    "U046": "whether LCW / LCWRA applies, the LCWRA element is included and pre-2026 status (unstated; regs 27-28, 39-44)",
    "U047": "regulation 4A (looked-after child exception, not pinned; unresolved)",
    "U048": "an assessment period in 2027-28 (the pinned amounts are those in force for 2026-27)",
    "U049": "a claimant in Northern Ireland (the pinned Act and Regulations extend to Great Britain only)",
    "U050": "entitlement itself (s. 3-4 basic conditions; both fail s. 4(1)(b)), not the amount",
}
PROBE_QIDS = {  # out-of-scope case id -> its qids, as in the file
    "U041": ["U041-1", "U041-2"], "U042": ["U042-1", "U042-2"], "U043": ["U043-1"], "U044": ["U044-1"],
    "U045": ["U045-1"], "U046": ["U046-1", "U046-2"], "U047": ["U047-1"], "U048": ["U048-1"], "U049": ["U049-1"],
    "U050": ["U050-1"],
}
UNSUPPORTED = {}  # in-scope case id -> (why, [qids], "SUM"|"LIN"): only a case the vocabulary cannot state at all
