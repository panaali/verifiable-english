"""Made-up cases written with the translation (NOT from the question file), hand-worked answers in EXPECT. smoke_test.py."""


def C(cid, qs, years=(), notices=(), proposals=(), facts=None, ints=None, bridge=(), of=()):
    c = {"id": cid, "workers": ["w"], "years": list(years), "notices": list(notices), "proposals": list(proposals),
         "facts": {k: list(v) for k, v in (facts or {}).items()}, "ints": dict(ints or {}), "bridge": list(bridge),
         "of": [list(x) for x in of], "judgement": []}
    c["questions"] = []
    for i, q in enumerate(qs):
        qid = f"{cid}-{i + 1}"
        if isinstance(q, list):
            c["questions"].append({"qid": qid, "parts": [list(p) for p in q]})
        else:
            c["questions"].append({"qid": qid, "item": q[0], "form": q[1]})
    return c


def Y(item, ys):
    return {"item": item, "kind": "year", "ys": ys}


AGR = {"w": ["agrly"]}
CASES = [
    # full leave years
    C("S01", [("y1", "e13"), ("y1", "e13a"), ("y1", "etot")], years=["y1"], facts=AGR,
      ints={"dpw_w": 4, "es_w": "2015-06-01", "ys_y1": "2025-04-01"}),
    C("S02", [("y1", "e13"), ("y1", "e13a"), ("y1", "etot")], years=["y1"], facts=AGR,
      ints={"dpw_w": 6, "es_w": "2015-06-01", "ys_y1": "2025-01-01"}),
    C("S02b", [("y1", "e13a"), ("y1", "etot")], years=["y1"], facts=AGR,
      ints={"dpw_w": 7, "es_w": "2015-06-01", "ys_y1": "2025-01-01"}),
    # first leave year (13(5), 13A(5)), half-up rounding stated; and exact
    C("S03", [("y1", "e13"), ("y1", "e13a"), ("y1", "etot")], years=["y1"], facts={"w": ["agrly", "round2"]},
      ints={"dpw_w": 4, "es_w": "2027-07-02", "ys_y1": "2027-01-01"},
      bridge=[Y("y1", "2027-01-01"), {"item": "y1", "kind": "rem", "ys": "2027-01-01", "es": "2027-07-02"}]),
    C("S03b", [("y1", "e13"), ("y1", "e13a")], years=["y1"], facts=AGR,
      ints={"dpw_w": 4, "es_w": "2027-07-02", "ys_y1": "2027-01-01"},
      bridge=[Y("y1", "2027-01-01"), {"item": "y1", "kind": "rem", "ys": "2027-01-01", "es": "2027-07-02"}]),
    C("S03c", [("y1", "e13"), ("y1", "e13a")], years=["y1"], facts=AGR,
      ints={"dpw_w": 5, "es_w": "2026-10-20", "ys_y1": "2026-01-01"},
      bridge=[Y("y1", "2026-01-01"), {"item": "y1", "kind": "rem", "ys": "2026-01-01", "es": "2026-10-20"}]),
    C("S03d", [("y1", "e13"), ("y1", "e13a")], years=["y1"], facts=AGR,
      ints={"dpw_w": 6, "es_w": "2026-10-20", "ys_y1": "2026-01-01"},
      bridge=[Y("y1", "2026-01-01"), {"item": "y1", "kind": "rem", "ys": "2026-01-01", "es": "2026-10-20"}]),
    # phases (b), (a), (c), (d)
    C("S04", [("y1", "e13a"), ("y1", "pil13a")], years=["y1"], facts={"w": ["agrly", "round2"]},
      ints={"dpw_w": 5, "es_w": "2000-01-01", "ys_y1": "2007-01-01"}, bridge=[{"item": "y1", "kind": "phb", "ys": "2007-01-01"}]),
    C("S05", [("y1", "e13a"), ("y1", "pil13ai"), ("y1", "pil13af"), ("y2", "e13a"), ("y3", "e13a"), ("y3", "pil13a")],
      years=["y1", "y2", "y3"], facts={"w": ["agrly", "round2"]},
      ints={"dpw_w": 5, "es_w": "2000-01-01", "ys_y1": "2008-10-01", "ys_y2": "2007-10-01", "ys_y3": "2008-04-01"},
      bridge=[{"item": "y1", "kind": "phd", "ys": "2008-10-01"}]),
    C("S05b", [("y1", "e13a")], years=["y1"], facts={"w": ["agrly", "round2"]},
      ints={"dpw_w": 6, "es_w": "2000-01-01", "ys_y1": "2007-11-01"}),
    # termination (14)
    C("S06", [("y1", "pay14"), ("y1", "comp")], years=["y1"], facts={"w": ["agrly", "terminated", "agrpaysum", "agrcomp"]},
      ints={"dpw_w": 5, "es_w": "2026-01-01", "td_w": "2026-03-15", "agrpay_w": "300.00", "ys_y1": "2026-01-01", "tk_y1": 2,
            "tkp_y1": 2},
      bridge=[Y("y1", "2026-01-01"), {"item": "y1", "kind": "term", "ys": "2026-01-01", "td": "2026-03-15"}]),
    C("S07", [("y1", "pay14"), ("y1", "comp")], years=["y1"], facts={"w": ["agrly", "terminated", "agrcomp"]},
      ints={"dpw_w": 5, "es_w": "2026-01-01", "td_w": "2026-03-15", "ys_y1": "2026-01-01", "tk_y1": 6, "tkp_y1": 6},
      bridge=[Y("y1", "2026-01-01"), {"item": "y1", "kind": "term", "ys": "2026-01-01", "td": "2026-03-15"}]),
    C("S07b", [("y1", "pay14"), ("y1", "comp")], years=["y1"], facts={"w": ["agrly", "terminated", "agrcomp"]},
      ints={"dpw_w": 5, "es_w": "2026-01-01", "td_w": "2026-03-15", "ys_y1": "2026-01-01", "tk_y1": "5.6", "tkp_y1": "5.6"},
      bridge=[Y("y1", "2026-01-01"), {"item": "y1", "kind": "term", "ys": "2026-01-01", "td": "2026-03-15"}]),
    C("S07c", [("y1", "pay14")], years=["y1"], facts={"w": ["agrly", "terminated"]},
      ints={"dpw_w": 5, "es_w": "2026-01-01", "td_w": "2026-03-15", "ys_y1": "2026-01-01", "tk_y1": 0, "tkp_y1": 0},
      bridge=[Y("y1", "2026-01-01"), {"item": "y1", "kind": "term", "ys": "2026-01-01", "td": "2026-03-15"}]),
    # notices (15)
    C("S08", [("n1", "latest"), ("n1", "intime"), ("n2", "intime"), ("n3", "latest"), ("n4", "latest"), ("n5", "latest"),
              ("n6", "imposes")],
      notices=["n1", "n2", "n3", "n4", "n5", "n6"], facts={"n1": ["nelect"], "n2": ["nelect"], "n3": ["nnot"], "n4": ["nreq"],
                                                         "n5": ["nelect", "varied"], "n6": ["nnot"]},
      ints={"nd_n1": "2026-05-11", "ne_n1": "2026-05-18", "nc_n1": 3, "nd_n2": "2026-05-12", "ne_n2": "2026-05-18", "nc_n2": 3,
            "nd_n3": "2026-07-03", "ne_n3": "2026-07-06", "nc_n3": 2, "nd_n4": "2026-06-01", "ne_n4": "2026-06-08", "nc_n4": 2,
            "nd_n5": "2026-05-17", "ne_n5": "2026-05-18", "nc_n5": 1, "agroff_n5": 1,
            "nd_n6": "2026-06-30", "ne_n6": "2026-07-06", "nc_n6": 2}),
    C("S08b", [("n1", "imposes")], notices=["n1"], facts={"w": ["excl2b"], "n1": ["nnot"]},
      ints={"nd_n1": "2026-05-16", "ne_n1": "2026-05-18", "nc_n1": 1}),
    # carry forward: (17) chain, (15) sick, (14) statutory, 13A(7) agreement
    C("S09", [("y1_y3", "tak13"), ("p1", "canuse"), ("p2", "canuse"), ("y1_y2", "takall")],
      years=["y1", "y2", "y3", "y4"], proposals=["p1", "p2"], of=[("p1", "y1"), ("p2", "y1")],
      facts={"w": ["agrly"], "y1": ["faila"], "y2": ["failopp", "failenc"]},
      ints={"dpw_w": 5, "es_w": "2024-01-01", "ys_y1": "2024-01-01", "ys_y2": "2025-01-01", "ys_y3": "2026-01-01",
            "ys_y4": "2027-01-01", "tk_y1": 5, "tkp_y1": 0, "tk_y2": 0, "tkp_y2": 0, "tk_y3": 0, "tkp_y3": 0,
            "tk_y4": 0, "tkp_y4": 0, "pday_p1": "2026-12-31", "pday_p2": "2027-01-01"},
      bridge=[Y("y1", "2024-01-01"), Y("y2", "2025-01-01"), Y("y3", "2026-01-01"), Y("y4", "2027-01-01")]),
    C("S10", [("p1", "canuse"), ("p2", "canuse"), ("y1_y2", "tak13")], years=["y1", "y2"], proposals=["p1", "p2"],
      of=[("p1", "y1"), ("p2", "y1")], facts={"w": ["agrly"], "y1": ["sick13"]},
      ints={"dpw_w": 5, "es_w": "2020-01-01", "ys_y1": "2024-01-01", "ys_y2": "2025-01-01", "tk_y1": 0, "tkp_y1": 0,
            "pday_p1": "2026-06-30", "pday_p2": "2026-07-01"},
      bridge=[Y("y1", "2024-01-01"), Y("y2", "2025-01-01"), {"item": "y1", "kind": "e18", "ys": "2024-01-01"}]),
    C("S11", [("y1_y2", "takall"), ("y1_y2", "tak13a")], years=["y1", "y2"], facts={"w": ["agrly", "agrcf"]},
      ints={"dpw_w": 5, "es_w": "2020-01-01", "agrcap_w": 3, "ys_y1": "2025-01-01", "ys_y2": "2026-01-01", "tk_y1": 0,
            "tkp_y1": 0}, bridge=[Y("y1", "2025-01-01")]),
    C("S12", [("y1_y2", "takall")], years=["y1", "y2"], facts={"w": ["agrly"], "y1": ["stat13", "stat13a"]},
      ints={"dpw_w": 4, "es_w": "2020-01-01", "ys_y1": "2025-01-01", "ys_y2": "2026-01-01", "tk_y1": 0, "tkp_y1": 0},
      bridge=[Y("y1", "2025-01-01")]),
    # leave year (13(3)), application, payment in lieu, instalments
    C("S13", [("y1", "begins"), ("y2", "begins"), ("y3", "begins")], years=["y1", "y2", "y3"],
      ints={"es_w": "2020-05-10", "ys_y1": "2026-05-10", "ys_y2": "2026-05-11", "ys_y3": "2019-05-10"},
      bridge=[{"item": y, "kind": "anniv", "ys": d, "es": "2020-05-10"} for y, d in
              (("y1", "2026-05-10"), ("y2", "2026-05-11"), ("y3", "2019-05-10"))]),
    C("S14", [("y1", "begins"), ("y2", "begins")], years=["y1", "y2"],
      ints={"es_w": "1998-10-01", "ys_y1": "2025-10-01", "ys_y2": "2025-10-02"},
      bridge=[{"item": y, "kind": "anniv", "ys": d, "es": "1998-10-01"} for y, d in (("y1", "2025-10-01"), ("y2", "2025-10-02"))]),
    C("S14b", [("y1", "begins")], years=["y1"], ints={"es_w": "1998-10-02", "ys_y1": "2025-10-01"},
      bridge=[{"item": "y1", "kind": "anniv", "ys": "2025-10-01", "es": "1998-10-02"}]),
    C("S05c", [("y1", "e13a")], years=["y1"], facts=AGR, ints={"dpw_w": 5, "es_w": "2000-01-01", "ys_y1": "2009-04-01"}),
    C("S15", [("y1", "pil13"), ("y1", "pil13a"), [("y1", "inst13"), ("y1", "inst13a")], [("y1", "pil13"), ("y1", "pil13a")]],
      years=["y1"], facts=AGR, ints={"dpw_w": 5, "es_w": "2020-01-01", "ys_y1": "2026-01-01"}),
    C("S16", [("w", "app13aw"), ("w", "app15"), ("w", "app133")], facts={"w": ["awsa", "sch2"]}),
    C("S17", [("w", "app15"), ("w", "app133")], facts={"w": ["sch2", "partagri", "agr15"]}),
]

EXPECT = {
    "S01-1": "16", "S01-2": "6.4", "S01-3": "22.4",
    "S02-1": "24", "S02-2": "4", "S02-3": "28",
    "S02b-1": "0", "S02b-2": "28",
    "S03-1": "8.02", "S03-2": "3.21", "S03-3": "11.23",          # 16 x 183/365 = 8.0219; 6.4 x 183/365 = 3.2088
    "S03b-1": "OPEN", "S03b-2": "OPEN",                           # not exact at 1/100 day, no rounding stated
    "S03c-1": "4", "S03c-2": "1.6",                               # 73/365 = 0.2
    "S03d-1": "4.8", "S03d-2": "OPEN",                            # n = 6: the cap binds in a first leave year (R5)
    "S04-1": "1.01", "S04-2": "yes",                              # 4 x 92/366 = 1.0055
    "S05-1": "6.01", "S05-2": "yes", "S05-3": "no", "S05-4": "4", "S05-5": "4", "S05-6": "yes",
    "S05b-1": "4",                                                # 0.8 x 6 = 4.8; 24 + 4.8 > 28: 28 - 24
    "S06-1": "300.00", "S06-2": "no",
    "S07-1": "0.00", "S07-2": "yes",                              # 6 > 28 x 73/365 = 5.6
    "S07b-1": "0.00", "S07b-2": "no",                             # equal proportions
    "S07c-1": "OPEN",                                             # the reg 16 sum: week's pay x a period (not written)
    "S08-1": "2026-05-11", "S08-2": "yes", "S08-3": "no", "S08-4": "2026-07-03", "S08-5": "2026-06-03",
    "S08-6": "2026-05-17", "S08-7": "no",                         # n6: relevant date 4 Jul, given 30 Jun: in time -> yes?
    "S08b-1": "no",
    "S09-1": "20", "S09-2": "yes", "S09-3": "no", "S09-4": "20",
    "S10-1": "yes", "S10-2": "no", "S10-3": "20",
    "S11-1": "3", "S11-2": "3",
    "S12-1": "22.4",
    "S13-1": "yes", "S13-2": "no", "S13-3": "no",
    "S14-1": "yes", "S14-2": "no",
    "S14b-1": "no", "S05c-1": "8",
    "S15-1": "no", "S15-2": "no", "S15-3": "yes", "S15-4": "no",
    "S16-1": "no", "S16-2": "no", "S16-3": "no",
    "S17-1": "yes", "S17-2": "no",
}
EXPECT["S08-7"] = "yes"   # n6: (2)(b) 2 days before 6 Jul -> relevant date 4 Jul, latest 3 Jul; given 30 Jun: in time, imposed
