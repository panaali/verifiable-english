"""The encoder's transcription of questions-enc.jsonl (sha256 51be9b0d...f0567c): one record per AWARD. SAME-FAMILY.

Written after translation.py was committed (297e87d748) and after questions-enc.jsonl was opened; the sealed answers were
not read. Each record: persons (lowercase ids), the anchor (the person the question names), the true unary facts per
person (closed world, encode.py C1), the links (C2), the stated integers (C3: ages, incomes, housing), the questions
(form: max / award / claim), and "judgement": every reading beyond copying a stated fact (encoder judgement).
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

CASES = [
    award("U001", "U001", "ann", {"ann": ("24", "500.00", "0.00")}),
    award("U002", "U002", "ann", {"ann": ("25", "0.00", "120.50")}, housing="450.00"),
    award("U003", "U003", "ann", {"ann": ("31", "600.00", "0.00")}, {"cara": ["child"]}, links=lives("cara", "ann")),
    award("U004", "U004", "ann", {"ann": ("28", "427.00", "0.00")}, {"cal": ["child"], "dev": ["child"]},
          links=lives("cal", "ann") + lives("dev", "ann"), housing="650.00"),
    award("U005", "U005", "ann", {"ann": ("22", "1027.00", "40.25")}, {"cal": ["child"]}, links=lives("cal", "ann"),
          housing="500.00"),
    award("U006", "U006", "ann", {"ann": ("24", "400.00", "0.00"), "bob": ("23", "300.00", "0.00")},
          links=[("couple", "ann", "bob")]),
    award("U007", "U007", "ann", {"ann": ("24", "0.00", "0.00"), "bob": ("26", "1510.00", "0.00")}, {"cal": ["child"]},
          links=[("couple", "ann", "bob")] + lives("cal", "ann", "bob")),
    award("U008", "U008", "ann", {"ann": ("35", "900.00", "0.00"), "bob": ("36", "427.00", "60.00")},
          {"cal": ["child"], "dev": ["child"], "eve": ["child", "dis_lower"]},
          links=[("couple", "ann", "bob")] + lives("cal", "ann", "bob") + lives("dev", "ann", "bob")
          + lives("eve", "ann", "bob"), housing="800.00",
          judgement=["Eve: DLA care component at the middle rate read as dis_lower only (not a rate named in 24(2)(b)(i))"]),
    award("U009", "U009", "ann", {"ann": ("29", "710.00", "0.00"), "bob": ("33", "0.00", "0.00")},
          {"cal": ["child", "dis_lower", "dis_higher"], "dev": ["child", "dis_lower"]},
          links=[("couple", "ann", "bob")] + lives("cal", "ann", "bob") + lives("dev", "ann", "bob"),
          judgement=["Cal: DLA care highest rate = 24(2)(b)(i) (dis_higher) and entitled to DLA (dis_lower)",
                     "Dev: child disability payment care middle rate = dis_lower only"]),
    award("U010", "U010", "ann", {"ann": ("40", "1000.00", "0.00")}, {"cara": ["child", "dis_higher"]},
          links=lives("cara", "ann"), housing="300.00",
          judgement=["Cara: 'certified as severely sight impaired or blind by a consultant ophthalmologist' read as "
                     "24(2)(b)(ii) '... blind' (the source prints the paragraph with an ellipsis)"]),
    award("U011", "U011", "bob", {"bob": ("45", "900.00", "0.00")},
          {"cara": ["child", "dis_lower", "dis_higher"], "dev": ["child"]}, facts={"bob": ["lcw"]},
          links=lives("cara", "bob") + lives("dev", "bob"),
          judgement=["Cara: CDP care highest rate under reg 11(5) DACYP = 24(2)(b)(i)"]),
    award("U012", "U012", "ann", {"ann": ("30", "800.00", "100.00")}, facts={"ann": ["lcw", "lcwra_el"]}),
    award("U013", "U013", "ann", {"ann": ("50", "300.00", "0.00")}, facts={"ann": ["lcw"]}, housing="400.00"),
    award("U014", "U014", "ann", {"ann": ("52", "1227.00", "0.00"), "bob": ("55", "0.00", "150.75")},
          facts={"bob": ["lcw", "lcwra_el", "pre2026"], "ann": ["carer_el"]}, links=[("couple", "ann", "bob")],
          housing="600.00"),
    award("U015", "U015", "ann", {"ann": ("23", "0.00", "0.00"), "bob": ("24", "1000.00", "0.00")},
          facts={"ann": ["lcw", "lcwra_el", "pre2026"]}, links=[("couple", "ann", "bob")],
          judgement=["'a claimant who is terminally ill' read into the pre2026 fact (the 429.80 row names all three)"]),
    award("U016", "U016", "ann", {"ann": ("67", "0.00", "200.00"), "bob": ("62", "600.00", "0.00")},
          facts={"ann": ["fails_b"]}, links=[("couple", "ann", "bob")]),
    award("U017", "U017", "ann", {"ann": ("19", "0.00", "0.00"), "bob": ("21", "627.00", "0.00")}, {"cara": ["child"]},
          facts={"ann": ["fails_d"]}, links=[("couple", "ann", "bob")] + lives("cara", "ann", "bob"), housing="350.00"),
    award("U018", "U018", "ann", {"ann": ("20", "300.00", "0.00"), "ben": (None, "100.00", "0.00")}, {"ben": ["qyp"]},
          facts={"ben": ["fails_a"]}, links=[("couple", "ann", "ben"), ("living_couple", "ann", "ben")]
          + lives("ben", "ann"),
          judgement=["Ben is both Ann's partner (stated couple) and a qualifying young person who normally lives with "
                     "her; no age given for Ben (not needed: Ann is the only claimant under reg. 3(3)(a))"]),
    award("U019", "U019", "ann", {"ann": ("33", "800.00", "0.00"), "bob": ("34", "0.00", "50.00")}, {"cal": ["child"]},
          facts={"bob": ["fails_c", "temp_absent"]}, links=[("couple", "ann", "bob")] + lives("cal", "ann", "bob"),
          housing="700.00",
          judgement=["Cal 'normally lives with Ann and Bob' while Bob is temporarily absent: lives links to both"]),
    award("U020", "U020", "ann", {"ann": ("26", "400.00", "0.00"), "bob": ("28", "0.00", "0.00")},
          facts={"bob": ["prisoner", "temp_absent"]}, links=[("couple", "ann", "bob")], housing="520.00",
          judgement=["Bob 'a prisoner since 1 September 2026', his absence not expected to exceed 6 months: "
                     "temp_absent true, abs_over6 false"]),
    award("U021", "U021", "ann", {"ann": ("41", "500.00", "0.00"), "bob": ("45", "0.00", "50.00")},
          facts={"bob": ["reg19", "lcw"]}, links=[("couple", "ann", "bob")]),
    award("U022", "U022", "ann", {"ann": ("29", "1200.00", "0.00"), "bob": ("31", "300.00", "0.00")},
          {"cal": ["child"], "dev": ["child"]}, facts={"bob": ["s115"]},
          links=[("couple", "ann", "bob")] + lives("cal", "ann", "bob") + lives("dev", "ann", "bob"), housing="900.00"),
    award("U023h", "U023", "hamid",
          {"hamid": ("50", "400.00", "0.00"), "wafa": ("48", "0.00", "0.00"), "zara": ("32", "200.00", "0.00")},
          facts={"wafa": ["same_household"], "zara": ["same_household"]},
          links=[("couple", "hamid", "wafa"), ("couple", "hamid", "zara"), ("married", "hamid", "wafa"),
                 ("married", "hamid", "zara"), ("poly_law", "hamid", "wafa"), ("poly_law", "hamid", "zara"),
                 ("earlier", "hamid", "wafa")],
          housing="600.00", qids=(1, 2, 3),
          judgement=["'Hamid and Zara are husband and wife' living in one house read as a stated couple link (s. 39), "
                     "which reg. 3(4) then disregards", "earlier(hamid, wafa): the 1998 marriage is earlier than "
                     "Hamid's 2015 marriage and subsists"]),
    award("U023z", "U023", "zara",
          {"zara": ("32", "200.00", "0.00"), "hamid": ("50", "400.00", "0.00"), "wafa": ("48", "0.00", "0.00")},
          facts={"wafa": ["same_household"], "hamid": ["same_household"]},
          links=[("couple", "hamid", "wafa"), ("couple", "hamid", "zara"), ("married", "hamid", "wafa"),
                 ("married", "hamid", "zara"), ("poly_law", "hamid", "wafa"), ("poly_law", "hamid", "zara"),
                 ("earlier", "hamid", "wafa")],
          housing="0.00", qids=(4, 5, 6),
          judgement=["as U023h; the anchor is Zara (questions 4-6)"]),
    award("U024", "U024", "zara", {"zara": ("32", "0.00", "0.00"), "hamid": ("50", "1410.00", "0.00"),
                                   "wafa": (None, "0.00", "0.00")},
          {"sana": ["child"]},
          links=[("couple", "hamid", "zara"), ("married", "hamid", "wafa"), ("married", "hamid", "zara"),
                 ("poly_law", "hamid", "wafa"), ("poly_law", "hamid", "zara"), ("earlier", "hamid", "wafa")]
          + lives("sana", "hamid", "zara"),
          judgement=["Wafa's income is not stated ('she makes no claim'): stated 0.00 (she is never a claimant here)"]),
    award("U025", "U025", "ann", {"ann": ("27", "900.00", "0.00"), "bob": ("30", "0.00", "200.00")}, {"cara": ["child"]},
          facts={"bob": ["temp_absent", "abs_over6"]}, links=[("couple", "ann", "bob")] + lives("cara", "ann"),
          housing="400.00",
          judgement=["'by the first day of the assessment period his absence has lasted more than 6 months' = "
                     "'does exceed' (abs_over6)", "Cara normally lives with Ann only (the facts name no other)"]),
    award("U026", "U026", "ann", {"ann": ("24", "300.00", "0.00"), "bob": ("25", "600.00", "0.00")},
          facts={"bob": ["temp_absent"]}, links=[("couple", "ann", "bob")]),
    award("U027a", "U027", "ann", {"ann": ("34", "1000.00", "0.00"), "bob": ("36", "700.00", "0.00")},
          {"cara": ["child"]}, links=lives("cara", "ann", "bob") + [("main_judged", "ann", "cara")], qids=(1, 2, 3)),
    award("U027b", "U027", "bob", {"bob": ("36", "700.00", "0.00"), "ann": ("34", "1000.00", "0.00")},
          {"cara": ["child"]}, links=lives("cara", "ann", "bob") + [("main_judged", "ann", "cara")], housing="550.00",
          qids=(4, 5, 6)),
    award("U028a", "U028", "ann", {"ann": ("27", "0.00", "75.40"), "bob": ("29", "627.00", "0.00")},
          {"cara": ["child", "nom_any"]}, links=lives("cara", "ann", "bob") + [("nominated", "bob", "cara")],
          qids=(1, 2, 3)),
    award("U028b", "U028", "bob", {"bob": ("29", "627.00", "0.00"), "ann": ("27", "0.00", "75.40")},
          {"cara": ["child", "nom_any"]}, links=lives("cara", "ann", "bob") + [("nominated", "bob", "cara")],
          housing="480.00", qids=(4, 5, 6)),
    award("U029", "U029", "bob", {"bob": ("38", "1000.00", "0.00"), "ann": (None, "0.00", "0.00")},
          {"cara": ["child", "dis_lower", "nom_any", "sos_any"], "dev": ["child", "nom_any", "sos_any"]},
          facts={"bob": ["lcw", "lcwra_el"]},
          links=lives("cara", "ann", "bob") + lives("dev", "ann", "bob")
          + [("nominated", "ann", "cara"), ("nominated", "ann", "dev"), ("sos_det", "bob", "cara"),
             ("sos_det", "bob", "dev")],
          judgement=["Cara: DLA care lowest rate = dis_lower", "Ann's age and income are not stated: income stated "
                     "0.00 (she is not a claimant of Bob's award)"]),
    award("U030", "U030", "ann", {"ann": ("30", "1527.00", "25.33"), "bob": (None, "0.00", "0.00")},
          {"cara": ["child", "sos_any"]}, links=lives("cara", "ann", "bob") + [("sos_det", "ann", "cara")],
          housing="600.00", judgement=["Bob's income not stated: 0.00 (not a claimant of Ann's award)"]),
    award("U031", "U031", "ann", {"ann": ("37", "1427.00", "0.00")}, {"cara": ["child"], "dev": ["child", "la_care"]},
          links=lives("cara", "ann") + lives("dev", "ann"), housing="700.00"),
    award("U032", "U032", "ann", {"ann": ("44", "600.00", "0.00")}, {"ed": ["qyp", "prisoner"]}, links=lives("ed", "ann")),
    award("U033", "U033", "ann", {"ann": ("30", "800.00", "0.00"), "bob": ("31", "400.00", "0.00")},
          {"cara": ["child"], "dev": ["child", "temp_absent", "abs_over6"],
           "eve": ["child", "temp_absent", "abs_over6", "abs_from_gb", "abs_over1m", "reg11_circ"]},
          links=[("couple", "ann", "bob")] + lives("cara", "ann", "bob") + lives("dev", "ann", "bob")
          + lives("eve", "ann", "bob"),
          judgement=["'has lasted more than 6 months' by the first day = 'does exceed' (Dev, Eve)",
                     "Eve: an absence over 6 months also exceeds one month (abs_over1m)"]),
    award("U034", "U034", "bob", {"bob": ("26", "827.00", "0.00")},
          {"cara": ["child", "temp_absent"], "dev": ["child", "temp_absent", "abs_from_gb"], "eve": ["child"]},
          links=lives("cara", "bob") + lives("dev", "bob") + lives("eve", "bob"), housing="400.00"),
    award("U035", "U035", "ann", {"ann": ("32", "1110.00", "0.00")},
          {"cara": ["child"], "dev": ["child", "temp_absent", "abs_from_gb", "abs_over1m"],
           "eve": ["child", "temp_absent", "abs_from_gb", "abs_over1m", "reg11_circ", "dis_lower", "dis_higher"]},
          links=lives("cara", "ann") + lives("dev", "ann") + lives("eve", "ann")),
]

PROBES = {
    "U041": "a childcare costs element (reg. 34 not pinned; the reg. 36 maximum for one child is never applied by a pinned sentence)",
    "U042": "a childcare costs element for three children (reg. 34; the two-or-more maximum)",
    "U043": "the benefit cap (not pinned)",
    "U044": "earned income from wages, tax, self-employment (Part 6 not pinned)",
    "U045": "the housing costs element from rent (reg. 26, Schedules 1-5 not pinned)",
    "U046": "limited capability for work not stated (regs 39-44 not pinned)",
    "U047": "children born before 6 April 2017 / reg. 4A (not pinned)",
    "U048": "an assessment period before 6 April 2026 and Northern Ireland (another instrument)",
    "U049": "entitlement: both fail s. 4(1)(b), capital (reg. 18 not pinned)",
    "U050": "a transitional element and a sanction (not pinned)",
}
PROBE_QIDS = {"U041": ["U041-1", "U041-2"], "U042": ["U042-1", "U042-2"], "U043": ["U043-1"], "U044": ["U044-1"],
              "U045": ["U045-1", "U045-2", "U045-3"], "U046": ["U046-1", "U046-2", "U046-3"],
              "U047": ["U047-1", "U047-2"], "U048": ["U048-1", "U048-2", "U048-3"], "U049": ["U049-1"],
              "U050": ["U050-1"]}
UNSUPPORTED = {}
