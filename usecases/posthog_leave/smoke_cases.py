"""Made-up cases written with the translation (NOT from the question file), hand-worked answers in EXPECT. smoke_test.py."""


def C(cid, qs, **kw):
    c = {"id": cid, "members": ["m"], "absences": [], "years": [], "leaves": [], "blocks": [], "quarters": [], "facts": {},
         "ints": {}, "in_year": [], "bridge": [], "judgement": []}
    c.update(kw)
    c["questions"] = [{"qid": f"{cid}-{i + 1}", "item": x, "form": f} for i, (x, f) in enumerate(qs)]
    return c


def L(cid, kind, tm, td, start, logday=None, extra=(), ints=None, qs=(), **kw):
    facts = {"l": [kind, *extra]}
    facts.update(kw.pop("facts", {}))
    i = {"tm_l": tm, "td_l": td, "start_l": start}
    if logday:
        i["logday_l"] = logday
    i.update(ints or {})
    br = [{"item": "l", "kind": "deadline", "start": start}] + kw.pop("bridge", [])
    return C(cid, qs, leaves=["l"], facts=facts, ints=i, bridge=br, **kw)


CASES = [
    C("S01", [("y", "met"), ("y", "mindays")], absences=["a1", "a2"], years=["y"],
      facts={"a1": ["vac"], "a2": ["vac", "holiday"]}, ints={"days_a1": 20, "from_a1": "2027-03-01", "days_a2": 5,
                                                             "from_a2": "2027-12-25"}, in_year=[("a1", "y"), ("a2", "y")]),
    C("S02", [("y", "met")], absences=["a1", "a2"], years=["y"], facts={"a1": ["vac"], "a2": ["ill", "unexpected"]},
      ints={"days_a1": 20, "from_a1": "2027-03-01", "days_a2": 5, "from_a2": "2027-05-03"},
      in_year=[("a1", "y"), ("a2", "y")]),
    C("S03", [("y", "met")], absences=["a1", "a2"], years=["y"], facts={"a1": ["vac"], "a2": ["vac", "holiday"]},
      ints={"days_a1": 18, "from_a1": "2027-03-01", "days_a2": 6, "from_a2": "2027-12-24"},
      in_year=[("a1", "y"), ("a2", "y")]),
    L("S04", "maternity", 12, 0, "2027-06-30", "2027-02-28", qs=[("l", "weeks"), ("l", "loggedok"), ("l", "deadline"),
                                                                  ("l", "unpaidext"), ("l", "recvph")]),
    L("S05", "paternity", 12, 1, "2027-06-30", "2027-03-01", qs=[("l", "weeks"), ("l", "loggedok"), ("l", "unpaidext")]),
    L("S06", "maternity", 13, 0, "2027-08-31", extra=("haslocal", "localfull"), ints={"lwk_l": 26},
      qs=[("l", "weeks"), ("l", "recvph"), ("l", "recvlocal"), ("l", "deadline"), ("l", "inaddition")]),
    L("S07", "paternity", 5, 29, "2027-01-15", qs=[("l", "weeks"), ("l", "unpaidext")]),
    L("S08", "maternity", 20, 0, "2027-05-10", extra=("sales",), ints={"wtaken_l": 12, "att_q1": 50, "att_q2": 90,
                                                                         "att_q3": 120},
      quarters=["q1", "q2", "q3"], bridge=[{"item": "l", "kind": "window", "start": "2027-05-10"},
                                           {"item": "q1", "kind": "quarter", "year": 2026, "n": 3},
                                           {"item": "q2", "kind": "quarter", "year": 2026, "n": 4},
                                           {"item": "q3", "kind": "quarter", "year": 2027, "n": 1}],
      qs=[("l", "oteapplies"), ("l", "ote"), ("l", "weeks")]),
    L("S09", "maternity", 20, 0, "2027-05-10", extra=("sales",), ints={"wtaken_l": 11, "att_q2": 90, "att_q3": 95.5},
      quarters=["q2", "q3"], bridge=[{"item": "l", "kind": "window", "start": "2027-05-10"},
                                     {"item": "q2", "kind": "quarter", "year": 2026, "n": 4},
                                     {"item": "q3", "kind": "quarter", "year": 2027, "n": 1}],
      qs=[("l", "oteapplies"), ("l", "ote")]),
    L("S10", "maternity", 20, 0, "2027-05-10", extra=("sales",), ints={"wtaken_l": 16, "att_q2": 90, "att_q3": 95.5},
      quarters=["q2", "q3"], bridge=[{"item": "l", "kind": "window", "start": "2027-05-10"},
                                     {"item": "q2", "kind": "quarter", "year": 2026, "n": 4},
                                     {"item": "q3", "kind": "quarter", "year": 2027, "n": 1}],
      qs=[("l", "ote")]),
    C("S11", [("a1", "paidsick"), ("a2", "paidsick"), ("a3", "paidsick"), ("a3", "overlimit"), ("a2", "extended"),
              ("a1", "extended"), ("a1", "fitsick"), ("a1", "fitpto")],
      absences=["a1", "a2", "a3"], years=["y"],
      facts={"a1": ["ill", "unexpected"], "a2": ["ill", "unexpected"], "a3": ["ill", "unexpected"]},
      ints={"limit_m": 10, "days_a1": 4, "from_a1": "2027-01-11", "days_a2": 5, "from_a2": "2027-03-08", "days_a3": 3,
            "from_a3": "2027-05-03"}, in_year=[("a1", "y"), ("a2", "y"), ("a3", "y")]),
    C("S12", [("a1", "fitpto"), ("a1", "fitmedical"), ("a2", "fitmedical"), ("a2", "fitsick")], absences=["a1", "a2"],
      facts={"a2": ["medself", "ill"]}, ints={"days_a1": 3, "from_a1": "2027-01-11", "days_a2": 10,
                                              "from_a2": "2027-02-01"}),
    L("S13", "maternity", 8, 0, "2027-09-01", blocks=["b1", "b2"], facts={"b1": [], "b2": ["later"]},
      qs=[("b2", "paidblock"), ("b1", "paidblock"), ("l", "payssplit"), ("l", "weeks")]),
    C("S14", [("a1", "autook"), ("a1", "incal"), ("a1", "slackooo"), ("a2", "teamknows"), ("a2", "incal"),
              ("m", "candelete"), ("m", "countshours"), ("m", "ntypes"), ("m", "canparental")],
      absences=["a1", "a2"], facts={"a1": ["vac", "app", "auth", "subs"], "a2": ["vac", "deelonly"]},
      ints={"days_a1": 2, "from_a1": "2027-04-01", "days_a2": 1, "from_a2": "2027-05-01"}),
    C("S15", [("a1", "covered"), ("a1", "bminwk"), ("a1", "asksrel"), ("a2", "covered"), ("a2", "bminwk")],
      absences=["a1", "a2"], facts={"a1": ["pcloss"], "a2": ["bereaved"]},
      ints={"days_a1": 10, "from_a1": "2027-04-01", "days_a2": 5, "from_a2": "2027-06-01"}),
]
CASES += [
    L("S16", "maternity", 6, 0, "2027-10-29", qs=[("l", "weeks")]),
    C("S17", [("a1", "paidsick"), ("a1", "overlimit")], absences=["a1"], years=["y"], facts={"a1": ["ill", "unexpected"]},
      ints={"limit_m": 5, "days_a1": 5, "from_a1": "2027-01-11"}, in_year=[("a1", "y")]),
]
EXPECT = {
    "S01-1": "yes", "S01-2": "25", "S02-1": "OPEN", "S03-1": "no",
    "S04-1": "12", "S04-2": "yes", "S04-3": "2027-02-28", "S04-4": "yes", "S04-5": "yes",
    "S05-1": "6", "S05-2": "no", "S05-3": "no",
    "S06-1": "26", "S06-2": "no", "S06-3": "yes", "S06-4": "2027-04-30", "S06-5": "no",
    "S07-1": "2-3", "S07-2": "no",
    "S08-1": "yes", "S08-2": "100", "S08-3": "up to 24",
    "S09-1": "no", "S09-2": "OPEN", "S10-1": "92.75",
    "S11-1": "yes", "S11-2": "yes", "S11-3": "OPEN", "S11-4": "yes", "S11-5": "yes", "S11-6": "no", "S11-7": "yes",
    "S11-8": "no",
    "S12-1": "yes", "S12-2": "no", "S12-3": "yes", "S12-4": "no",
    "S13-1": "no", "S13-2": "OPEN", "S13-3": "no", "S13-4": "12",
    "S14-1": "yes", "S14-2": "yes", "S14-3": "yes", "S14-4": "no", "S14-5": "no", "S14-6": "no", "S14-7": "no",
    "S14-8": "4", "S14-9": "yes",
    "S15-1": "yes", "S15-2": "2", "S15-3": "no", "S15-4": "yes", "S15-5": "OPEN", "S16-1": "12", "S17-1": "yes", "S17-2": "no",
}
