"""The encoder's cases, from questions-enc.jsonl ONLY (template: fill CASES, UNSUPPORTED, PROBES, PROBE_QIDS).

Each case: "dwelling" (w), "values" (Q1 value items), "days" (one item per single day asked), "persons" (the people the
facts name as residents on a day asked; encode.py C2), "years" (financial-year items) and "in_year" links, "facts"
(unary facts true of an item), "pd" ("<person>@<day>" -> binary facts true on that day; every other one false, C1),
"ints" (stated amounts, dates, D), "questions" (qid -> item and form: band = Q1, discount = Q2, amount = Q3 for one day),
"judgement" (anything the encoder decided beyond copying a stated fact: listed as "encoder judgement").
UNSUPPORTED: in-scope questions the translation cannot carry (counted not correct, listed): every Q3 over a run of
several days (a count of days times a day's amount is a product of two quantities; the frozen build's rule). Key
"<case>-run" (or another unique key) -> (why, [qids]).
PROBES: out-of-scope cases (every answer UNSUPPORTED): case id -> one line; PROBE_QIDS: case id -> its qids.
Bridge: a date of birth the facts state goes to out/inputs_xfam.jsonl, one line per (case, person, day):
{"case", "person", "day", "dob", "date"} (dob and the day's date copied from the facts); the frozen bridge
(branch/usecases/council_tax/bridge/age.py) decides "attained18" from it. Never type attained18 yourself.
"""
from __future__ import annotations

RES = ["resident"]
PRISON_UK_SENTENCE = ["in_custody", "basis_sentence", "uk_court"]   # held in a prison under a sentence/warrant of a UK court


def Q(*rows):
    return [{"qid": qid, "item": item, "form": form} for (qid, item, form) in rows]


def band_case(cid, values):
    """K001-K005: one value item per question (Q1)."""
    vs = [f"v{i}" for i in range(1, len(values) + 1)]
    return {"id": cid, "values": vs, "ints": {f"value_{v}": val for v, val in zip(vs, values)},
            "questions": Q(*[(f"{cid}-{i}", v, "band") for i, v in enumerate(vs, 1)])}


def fy(case_ints, y, days, amt=None, amtd=None):
    case_ints[f"days_{y}"] = days
    if amt:
        case_ints[f"amt_{y}"] = amt
    if amtd:
        case_ints[f"amtd_{y}"] = amtd
    return case_ints


def day_case(cid, band, year, days, persons, pd, qs, judgement=(), facts=None, more_ints=None, years=("y1",),
             in_year=None):
    """A dwelling case: band listed, financial year(s) with A / A for band D and D, single days asked."""
    ints = dict(year)
    ints.update({f"date_{d}": iso for d, iso in days.items()})
    ints.update(more_ints or {})
    f = {"w": [f"list_{band.lower()}"]}
    f.update(facts or {})
    return {"id": cid, "dwelling": "w", "days": list(days), "persons": persons, "years": list(years),
            "in_year": in_year or [(d, "y1") for d in days], "facts": f, "pd": pd, "ints": ints,
            "questions": Q(*qs), "judgement": list(judgement)}


def two(qid_disc, qid_amt, d):
    return [(qid_disc, d, "discount"), (qid_amt, d, "amount")]


FY2526 = lambda **kw: fy({}, "y1", "365", **kw)   # 2025-26, from 1 April 2025 to 31 March 2026, has 365 days
TEMP = ["temp_released", "basis_sentence", "uk_court"]  # temporarily discharged/released from a UK-court sentence detention


def pds(rows):
    """{"person@day": [facts]} from (person, [days], [facts])."""
    out = {}
    for p, ds, fs in rows:
        for d in ds:
            out.setdefault(f"{p}@{d}", []).extend(fs)
    return out


CASES = [
    band_case("K001", ["39999.00"]),
    band_case("K002", ["40000.00"]),
    band_case("K003", ["40001.00"]),
    band_case("K004", ["68000.00"]),
    band_case("K005", ["88000.00"]),
    band_case("K006", ["120000.00"]),
    band_case("K007", ["160000.00"]),
    band_case("K008", ["320000.00"]),
    band_case("K009", ["320001.00"]),
    band_case("K010", ["52000.00"]),
    # K011: band C, A for band C stated; 1 June Ann only; 2 June Ann and Ben; 3 June nobody
    day_case("K011", "C", FY2526(amt="1460.00"), {"d1": "2025-06-01", "d2": "2025-06-02", "d3": "2025-06-03"},
             ["ann", "ben"], pds([("ann", ["d1", "d2"], RES), ("ben", ["d2"], RES)]),
             two("K011-1", "K011-2", "d1") + two("K011-3", "K011-4", "d2") + two("K011-5", "K011-6", "d3")),
    day_case("K012", "A", FY2526(amtd="1971.00"), {"d1": "2025-06-01", "d2": "2025-06-02"},
             ["bea", "cara", "dee", "eli"],
             pds([("bea", ["d1", "d2"], RES + ["student", "cond4b"]),
                  ("cara", ["d1", "d2"], RES + ["student_nurse", "cond4b"]),
                  ("dee", ["d1", "d2"], RES + ["apprentice"]), ("dee", ["d1"], ["cond4b"]),
                  ("eli", ["d1", "d2"], RES + ["ytt", "cond4b"])]),
             two("K012-1", "K012-2", "d1") + two("K012-3", "K012-4", "d2")),
    day_case("K013", "B", FY2526(amtd="1971.00"), {"d1": "2025-05-01", "d2": "2025-05-02"},
             ["ann", "ben"], pds([("ann", ["d1", "d2"], RES), ("ben", ["d1", "d2"], RES + PRISON_UK_SENTENCE)]),
             two("K013-1", "K013-2", "d1") + two("K013-3", "K013-4", "d2"),
             judgement=["2 May: a warrant giving effect to a UK court's decision carried as basis_sentence + uk_court"]),
    day_case("K014", "E", FY2526(amtd="1971.00"), {"d1": "2025-07-01", "d2": "2025-07-02"},
             ["ann", "ben"], pds([("ann", ["d1", "d2"], RES),
                                  ("ben", ["d1"], RES + ["in_custody", "basis_order", "service_offence"]),
                                  ("ben", ["d2"], RES + ["temp_released", "basis_order", "service_offence"])]),
             two("K014-1", "K014-2", "d1") + two("K014-3", "K014-4", "d2"),
             judgement=["2 July: basis_order + service_offence kept for the award detention Ben is released from"]),
    day_case("K015", "F", FY2526(amtd="1971.00"), {"d1": "2025-08-01", "d2": "2025-08-02", "d3": "2025-08-03"},
             ["ben"], pds([("ben", ["d1"], RES + ["in_custody", "under_ia1971"]),
                           ("ben", ["d2"], RES + ["in_custody", "under_mha1983"]),
                           ("ben", ["d3"], RES + ["in_custody", "under_scot"])]),
             two("K015-1", "K015-2", "d1") + two("K015-3", "K015-4", "d2") + two("K015-5", "K015-6", "d3"),
             judgement=["'physically held at a detention facility' read as in_custody on each day"]),
    day_case("K016", "G", FY2526(amtd="1971.00"), {"d1": "2025-09-01", "d2": "2025-09-02", "d3": "2025-09-03"},
             ["ann", "ben"], pds([("ann", ["d1", "d2", "d3"], RES),
                                  ("ben", ["d1", "d2", "d3"], RES + ["in_custody", "basis_order", "uk_court"]),
                                  ("ben", ["d1"], ["under_sch4_8"]), ("ben", ["d2"], ["fine_default"]),
                                  ("ben", ["d3"], ["only_cps1975"])]),
             two("K016-1", "K016-2", "d1") + two("K016-3", "K016-4", "d2") + two("K016-5", "K016-6", "d3")),
    day_case("K017", "H", FY2526(amtd="1971.00"), {"d1": "2025-09-04"},
             ["ann", "ben", "cal", "dee", "eli"],
             pds([("ann", ["d1"], RES)] + [(p, ["d1"], RES + TEMP) for p in ("ben", "cal", "dee", "eli")]),
             two("K017-1", "K017-2", "d1"),
             judgement=["basis_sentence + uk_court of the prison detention kept on the day each is discharged/released"]),
    day_case("K018", "C", FY2526(amtd="1971.00"), {"d1": "2025-10-09", "d2": "2025-10-10"},
             ["ann", "cal"], pds([("ann", ["d1", "d2"], RES),
                                  ("cal", ["d1", "d2"], RES + ["severe_imp", "appears_perm", "cond2c"])]),
             two("K018-1", "K018-2", "d1") + two("K018-3", "K018-4", "d2"),
             facts={"cal": ["has_cert"]}, more_ints={"certfrom_cal": "2025-10-10", "certto_cal": "2025-10-11"}),
    day_case("K019", "D", FY2526(amtd="1971.00"), {"d1": "2025-05-20", "d2": "2025-05-21", "d3": "2025-05-22"},
             ["ann", "cal"], pds([("ann", ["d1", "d2", "d3"], RES), ("cal", ["d1", "d2", "d3"], RES),
                                  ("cal", ["d1"], ["severe_imp", "appears_perm"]),
                                  ("cal", ["d2"], ["appears_perm", "cond2c"]),
                                  ("cal", ["d3"], ["severe_imp", "cond2c"])]),
             two("K019-1", "K019-2", "d1") + two("K019-3", "K019-4", "d2") + two("K019-5", "K019-6", "d3"),
             facts={"cal": ["has_cert"]}, more_ints={"certfrom_cal": "2025-05-20", "certto_cal": "2025-05-22"},
             judgement=["certificate 'throughout that period' read as 20 to 22 May 2025 (certfrom/certto)"]),
    # K020: Dee's age on each day asked comes from the bridge (out/inputs_xfam.jsonl)
    day_case("K020", "B", FY2526(amt="1460.00"), {"d1": "2025-06-01", "d2": "2025-06-02"},
             ["ann", "dee"], pds([("ann", ["d1", "d2"], RES), ("dee", ["d2"], RES),
                                  ("dee", ["d1", "d2"], ["cb_entitled"])]),
             two("K020-1", "K020-2", "d1") + two("K020-3", "K020-4", "d2"),
             judgement=["Dee (visiting, not resident on 1 June) is a person of the case: a resident on 2 June"]),
    day_case("K021", "E", FY2526(amtd="1971.00"), {"d1": "2025-05-15"},
             ["eli"], pds([("eli", ["d1"], RES + ["cb_but_for"])]),
             two("K021-1", "K021-2", "d1")),
    day_case("K022", "F", FY2526(amtd="1971.00"), {"d1": "2025-11-07", "d2": "2025-11-08"},
             ["iris", "jude"], pds([("iris", ["d1", "d2"], RES), ("jude", ["d1", "d2"], RES + ["student"]),
                                    ("jude", ["d2"], ["cond4b"])]),
             two("K022-1", "K022-2", "d1") + two("K022-3", "K022-4", "d2")),
    day_case("K023", "A", FY2526(amtd="1971.00"), {"d1": "2025-12-01", "d2": "2025-12-02"},
             ["ada"], pds([("ada", ["d1", "d2"], RES + ["smr_inst", "inst_hs_hospital", "inst_england"]),
                           ("ada", ["d1"], ["patient"])]),
             two("K023-1", "K023-2", "d1") + two("K023-3", "K023-4", "d2"),
             judgement=["'a health service hospital as defined by s. 275' carried as inst_hs_hospital only"]),
    day_case("K024", "B", FY2526(amtd="1971.00"), {"d1": "2025-12-03"},
             ["ada", "ben"], pds([(p, ["d1"], RES + ["patient", "smr_inst", "inst_mil_med", "inst_england"])
                                  for p in ("ada", "ben")]),
             two("K024-1", "K024-2", "d1")),
    day_case("K025", "C", FY2526(amtd="1971.00"), {"d1": "2025-12-04"},
             ["ada"], pds([("ada", ["d1"], RES + ["patient", "receiving_care", "smr_inst", "inst_england"])]),
             two("K025-1", "K025-2", "d1")),
    day_case("K026", "D", FY2526(amtd="1971.00"), {"d1": "2025-12-05"},
             ["dee"], pds([("dee", ["d1"], RES + ["smr_inst", "receiving_care", "inst_cs2000_care_home",
                                                  "inst_england"])]),
             two("K026-1", "K026-2", "d1")),
    day_case("K027", "E", FY2526(amtd="1971.00"), {"d1": "2025-12-06"},
             ["dee", "eli"], pds([("dee", ["d1"], RES + ["smr_inst", "inst_care_act", "inst_england", "receiving_care"]),
                                  ("eli", ["d1"], RES + ["smr_inst", "inst_care_act", "inst_england"])]),
             two("K027-1", "K027-2", "d1")),
    day_case("K028", "F", FY2526(amtd="1971.00"), {"d1": "2025-12-07"},
             ["dee"], pds([("dee", ["d1"], RES + ["smr_inst", "receiving_care", "inst_england"])]),
             two("K028-1", "K028-2", "d1")),
    day_case("K029", "G", FY2526(amtd="1971.00"), {"d1": "2025-12-08"},
             ["fran"], pds([("fran", ["d1"], RES + ["smr_inst", "patient", "receiving_care", "inst_s275_hospital",
                                                    "inst_england"])]),
             two("K029-1", "K029-2", "d1")),
    day_case("K030", "H", FY2526(amtd="1971.00"), {"d1": "2025-12-09"},
             ["fran"], pds([("fran", ["d1"], RES + ["smr_inst", "patient", "receiving_care", "inst_england"])]),
             two("K030-1", "K030-2", "d1")),
    day_case("K031", "A", FY2526(amtd="1971.00"), {"d1": "2025-12-10"},
             ["gale"], pds([("gale", ["d1"], RES + ["smr_inst", "receiving_care", "inst_hostel", "inst_england"])]),
             two("K031-1", "K031-2", "d1")),
    day_case("K032", "B", FY2526(amtd="1971.00"), {"d1": "2025-12-11"},
             ["gale"], pds([("gale", ["d1"], RES + ["smr_inst", "receiving_care", "inst_england"])]),
             two("K032-1", "K032-2", "d1")),
    day_case("K033", "C", FY2526(amtd="1971.00"), {"d1": "2025-12-12", "d2": "2025-12-13"},
             ["dee"], pds([("dee", ["d1", "d2"], RES + ["smr_inst", "inst_cs2000_care_home", "inst_england"]),
                           ("dee", ["d2"], ["receiving_care"])]),
             two("K033-1", "K033-2", "d1") + two("K033-3", "K033-4", "d2")),
    # K034: two financial years; 31 March 2024 in 2023-24 (y1), 1 April 2024 in 2024-25 (y2)
    day_case("K034", "B", fy(fy({}, "y1", "366", amtd="1976.40"), "y2", "365", amtd="2628.00"),
             {"d1": "2024-03-31", "d2": "2024-04-01"},
             ["ann"], pds([("ann", ["d1", "d2"], RES)]),
             two("K034-1", "K034-2", "d1") + two("K034-3", "K034-4", "d2"),
             years=("y1", "y2"), in_year=[("d1", "y1"), ("d2", "y2")]),
]

RUN = "Q3 over a run of several days: a count of days times a day's amount (product of two quantities; frozen build)"
UNSUPPORTED = {
    "K011-run": (RUN, ["K011-7"]),
    "K012-run": (RUN, ["K012-5"]),
    "K013-run": (RUN, ["K013-5"]),
    "K018-run": (RUN, ["K018-5"]),
    "K020-run": (RUN, ["K020-5"]),
    "K034-run": (RUN, ["K034-5"]),
    "K035-run": (RUN + "; the case has no other question, so no record", ["K035-1"]),
}
PROBES = {
    "K036": "the Welsh valuation-band table (s. 5(3)), not in the translation",
    "K037": "Scottish discount rules incl. Sch. 1 para. 8 (Scotland), not in the translation",
    "K038": "Sch. 1 para. 9 (carers), not in the translation",
    "K039": "Sch. 1 para. 10 (night shelters etc.), not in the translation",
    "K040": "a Sch. 1 para. 11 order, not in the translation",
    "K041": "a long-term-empty-home premium over a run of days, not in the translation",
    "K042": "a local council tax reduction and an exemption over runs of days, not in the translation",
    "K043": "a substituted s. 5(4)(a) band proportion (not supplied) over a run of days",
    "K044": "a different s. 11(3) appropriate percentage by order (not supplied)",
    "K045": "the para. 2(2) 'appears to be permanent' judgment is not given (no stated judgment to enter)",
}
PROBE_QIDS = {
    "K036": ["K036-1"], "K037": ["K037-1", "K037-2"], "K038": ["K038-1", "K038-2"], "K039": ["K039-1", "K039-2"],
    "K040": ["K040-1", "K040-2"], "K041": ["K041-1"], "K042": ["K042-1", "K042-2"], "K043": ["K043-1"],
    "K044": ["K044-1", "K044-2"], "K045": ["K045-1", "K045-2"],
}

# Open facts (encode.py C5), added by the council-tax fidelity fix (fidfix-council-tax-1126): one fresh Opus 5.5 encoder
# seat read only the facts of questions-enc.jsonl (never sealed/) and recorded sch1_closed per case and inst_s275_hs per
# (person, day) where the facts name an institution (manage-agents reviews/spare/statute-corpus/fidelity-check/sweep/
# council-tax/fix/encoder/). Applied verbatim; "unstated" values are left out (unknown).
SCH1_CLOSED = ["K011", "K012", "K013", "K014", "K015", "K016", "K017", "K018", "K019", "K020", "K021", "K022", "K023", "K024", "K025", "K026", "K027", "K028", "K029", "K030", "K031", "K032", "K033", "K034"]
OPEN = {"K023": {"ada@d1": {"inst_s275_hs": True}, "ada@d2": {"inst_s275_hs": True}}, "K024": {"ada@d1": {"inst_s275_hs": False}, "ben@d1": {"inst_s275_hs": False}}, "K025": {"ada@d1": {"inst_s275_hs": False}}, "K026": {"dee@d1": {"inst_s275_hs": False}}, "K027": {"dee@d1": {"inst_s275_hs": False}, "eli@d1": {"inst_s275_hs": False}}, "K028": {"dee@d1": {"inst_s275_hs": False}}, "K029": {"fran@d1": {"inst_s275_hs": False}}, "K030": {"fran@d1": {"inst_s275_hs": False}}, "K031": {"gale@d1": {"inst_s275_hs": False}}, "K032": {"gale@d1": {"inst_s275_hs": False}}, "K033": {"dee@d1": {"inst_s275_hs": False}, "dee@d2": {"inst_s275_hs": False}}}
# adj_none per case, from a second fresh Opus 5.5 encoder seat on the same facts only (fix/encoder2/): true for all 24.
ADJ_NONE = ["K011", "K012", "K013", "K014", "K015", "K016", "K017", "K018", "K019", "K020", "K021", "K022", "K023", "K024", "K025", "K026", "K027", "K028", "K029", "K030", "K031", "K032", "K033", "K034"]
# eng_chargeable per case, from a third fresh Opus 5.5 encoder seat on the same facts only (fix/encoder3/).
ENG_CHARGEABLE = ["K011", "K012", "K013", "K014", "K015", "K016", "K017", "K018", "K019", "K020", "K021", "K022", "K023", "K024", "K025", "K026", "K027", "K028", "K029", "K030", "K031", "K032", "K033", "K034"]
for _c in CASES:
    if _c["id"] in ENG_CHARGEABLE:
        _c["eng_chargeable"] = True
    if _c["id"] in ADJ_NONE:
        _c["adj_none"] = True
    if _c["id"] in SCH1_CLOSED:
        _c["sch1_closed"] = True
    if _c["id"] in OPEN:
        _c["open"] = OPEN[_c["id"]]
