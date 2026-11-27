"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-council-tax-1123 (Opus 5.5), after the translation was committed (5488edc452, 15:28Z).
Each case: "dwelling" (w), "values" (Q1 value items), "days" (one item per single day asked), "persons" (the people the
facts name as residents on a day asked; encode.py C2), "years" (financial-year items) and "in_year" links, "facts"
(unary facts true of an item), "pd" ("<person>@<day>" -> binary facts true on that day; every other one false, C1),
"ints" (stated amounts, dates, D), "questions" (qid -> item and form: band = Q1, discount = Q2, amount = Q3 for one day),
"judgement" (anything the encoder decided beyond copying a stated fact: listed as "encoder judgement").
UNSUPPORTED: in-scope questions the translation cannot carry (counted not correct, listed): every Q3 over a run of
several days (ISOLATION.md D3a: a count of days times a day's amount is a product of two quantities; ledger unit 11).
PROBES: out-of-scope cases (every answer UNSUPPORTED). Bridge: bridge/inputs.jsonl (dates of birth copied from facts).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "7b45adca2550e74ad760452f002e976e2fcddb5a4c0699c3ce6e5184ea5317ac"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

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


CASES = [
    band_case("K001", ["40000.00", "40001.00", "39999.00"]),
    band_case("K002", ["52000.00", "52001.00", "68000.00"]),
    band_case("K003", ["68001.00", "88000.00", "88001.00"]),
    band_case("K004", ["120000.00", "120001.00", "160000.00"]),
    band_case("K005", ["160001.00", "320000.00", "320001.00", "1250000.00"]),
    day_case("K006", "B", fy({}, "y1", "365", amtd="2102.40"), {"d1": "2025-05-10"}, ["ann"],
             {"ann@d1": RES}, two("K006-1", "K006-2", "d1")),
    day_case("K007", "H", fy({}, "y1", "365", amtd="1971.00"), {"d1": "2025-11-14"}, ["cy", "dot"],
             {"cy@d1": RES, "dot@d1": RES}, two("K007-1", "K007-2", "d1")),
    day_case("K008", "A", fy({}, "y1", "365", amt="1182.60"), {"d1": "2025-07-15"}, [],
             {}, two("K008-1", "K008-2", "d1"),
             judgement=["K008: nobody is a resident on 15 July 2025; Eric (liable, lives elsewhere) is not a person of "
                        "the case (C2)"]),
    day_case("K009", "C", fy({}, "y1", "365", amt="1606.00"), {"d1": "2025-06-20"}, ["ann", "ben"],
             {"ann@d1": RES}, two("K009-1", "K009-2", "d1")),
    day_case("K010", "D", fy({}, "y1", "365", amt="1839.60"), {"d1": "2025-08-12"}, ["carl", "dana"],
             {"carl@d1": RES + PRISON_UK_SENTENCE, "dana@d1": RES}, two("K010-1", "K010-2", "d1")),
    day_case("K011", "B", fy({}, "y1", "365", amt="1489.20"), {"d1": "2025-09-05", "d2": "2025-10-10"}, ["saul"],
             {"saul@d1": RES + ["temp_released", "basis_sentence", "uk_court"], "saul@d2": RES},
             two("K011-1", "K011-2", "d1") + two("K011-3", "K011-4", "d2"),
             judgement=["K011 d1: on temporary release under rules under s. 47(5) Prison Act 1952 Saul is not in "
                        "custody that day; the detention he is released from is by virtue of the Crown Court's sentence"]),
    day_case("K012", "E", fy({}, "y1", "365", amtd="1708.20"), {"d1": "2026-02-03", "d2": "2026-03-10"}, ["dev", "eva"],
             {"dev@d1": RES + PRISON_UK_SENTENCE + ["fine_default"], "eva@d1": RES,
              "dev@d2": RES + PRISON_UK_SENTENCE, "eva@d2": RES},
             two("K012-1", "K012-2", "d1") + two("K012-3", "K012-4", "d2"),
             judgement=["K012 d1: detention under a magistrates' warrant of commitment for fine default read as by "
                        "virtue of a warrant (basis_sentence) of a UK court AND as s. 76 MCA 1980 fine default",
                        "K012 d2: remand under a Crown Court warrant read as by virtue of a warrant (para. 1(5))"]),
    day_case("K013", "C", fy({}, "y1", "365", amt="1343.20"), {"d1": "2025-08-20", "d2": "2025-08-23"}, ["gail", "hal"],
             {"gail@d1": RES + ["in_custody", "basis_sentence", "service_offence"], "hal@d1": RES,
              "gail@d2": RES + ["temp_released", "basis_sentence", "service_offence"], "hal@d2": RES},
             two("K013-1", "K013-2", "d1") + two("K013-3", "K013-4", "d2"),
             judgement=["K013: a military corrective training centre read as 'any other place'; the Court Martial's "
                        "sentence read as an order (para. 1(5)) made in service offence proceedings; not a UK court "
                        "stated or decided (it sat in Cyprus): uk_court false"]),
    day_case("K014", "F", fy({}, "y1", "365", amt="2277.60"), {"d1": "2025-06-01"}, ["ivan"],
             {"ivan@d1": RES + ["in_custody", "basis_order"]}, two("K014-1", "K014-2", "d1")),
    day_case("K015", "B", fy({}, "y1", "365", amtd="1576.80"), {"d1": "2026-01-08", "d2": "2026-02-20"}, ["jo", "kim"],
             {"jo@d1": RES + ["in_custody", "under_mha1983"], "kim@d1": RES,
              "jo@d2": RES + ["patient"], "kim@d2": RES},
             two("K015-1", "K015-2", "d1") + two("K015-3", "K015-4", "d2"),
             judgement=["K015 d2: 'stays on as an informal patient' read as a patient (para. 6 not engaged: the "
                        "hospital is not Jo's sole or main residence, stated)"]),
    day_case("K016", "A", fy({}, "y1", "365", amt="1036.60"), {"d1": "2025-12-15", "d2": "2025-12-01"}, ["lee"],
             {"lee@d1": RES + ["in_custody", "under_ia1971"], "lee@d2": RES},
             two("K016-1", "K016-2", "d1") + two("K016-3", "K016-4", "d2"),
             judgement=["K016: an immigration removal centre read as 'any other place' (para. 1(1)(b) needs only "
                        "'detained under')"]),
    day_case("K017", "D", fy({}, "y1", "365", amt="1912.60"), {"d1": "2025-08-14"}, ["mona"],
             {"mona@d1": RES + ["in_custody", "under_scot"]}, two("K017-1", "K017-2", "d1")),
    day_case("K018", "E", fy({}, "y1", "366", amt="1756.80"), {"d1": "2024-02-29"}, ["nina", "omar"],
             {"nina@d1": RES + PRISON_UK_SENTENCE + ["under_sch4_8"], "omar@d1": RES}, two("K018-1", "K018-2", "d1"),
             judgement=["K018: detention under Sch. 4 para. 8 regulations under a magistrates' warrant of commitment "
                        "read as by virtue of a warrant of a UK court AND under those regulations"]),
    day_case("K019", "C", fy({}, "y1", "365", amtd="1445.40"), {"d1": "2026-03-03"}, ["pat", "quinn"],
             {"pat@d1": RES + ["severe_imp", "appears_perm", "cond2c"], "quinn@d1": RES}, two("K019-1", "K019-2", "d1"),
             facts={"pat": ["has_cert"]}, more_ints={"certfrom_pat": "2025-01-10", "certto_pat": "2027-01-09"}),
    day_case("K020", "B", fy({}, "y1", "365", amt="1401.60"), {"d1": "2025-09-15", "d2": "2025-10-15"}, ["rhea"],
             {"rhea@d1": RES + ["severe_imp", "appears_perm", "cond2c"],
              "rhea@d2": RES + ["severe_imp", "appears_perm", "cond2c"]},
             two("K020-1", "K020-2", "d1") + two("K020-3", "K020-4", "d2"),
             facts={"rhea": ["has_cert"]}, more_ints={"certfrom_rhea": "2025-04-01", "certto_rhea": "2025-09-30"}),
    day_case("K021", "D", fy({}, "y1", "365", amt="1795.80"), {"d1": "2025-08-12", "d2": "2025-09-12"}, ["rob", "sue"],
             {"rob@d1": RES + ["severe_imp", "appears_perm"], "sue@d1": RES,
              "rob@d2": RES + ["severe_imp", "appears_perm", "cond2c"], "sue@d2": RES},
             two("K021-1", "K021-2", "d1") + two("K021-3", "K021-4", "d2"),
             facts={"rob": ["has_cert"]}, more_ints={"certfrom_rob": "2025-01-01", "certto_rob": "2026-12-31"}),
    day_case("K022", "C", fy({}, "y1", "365", amt="1460.00"), {"d1": "2025-11-04"}, ["tom"],
             {"tom@d1": RES + ["severe_imp", "cond2c"]}, two("K022-1", "K022-2", "d1"),
             facts={"tom": ["has_cert"]}, more_ints={"certfrom_tom": "2025-10-01", "certto_tom": "2026-03-31"}),
    day_case("K023", "D", fy({}, "y1", "365", amt="1971.00"), {"d1": "2025-09-20"}, ["vic", "uma"],
             {"vic@d1": RES, "uma@d1": RES + ["cb_entitled"]}, [("K023-1", "d1", "discount"), ("K023-2", "d1", "amount")]),
    day_case("K024", "A", fy({}, "y1", "365", amtd="1182.60"), {"d1": "2026-01-12"}, ["yara", "zoe"],
             {"yara@d1": RES + ["cb_but_for"], "zoe@d1": RES}, two("K024-1", "K024-2", "d1")),
    day_case("K025", "B", fy({}, "y1", "365", amt="1401.60"), {"d1": "2026-03-04"}, ["wes", "xena"],
             {"wes@d1": RES, "xena@d1": RES}, two("K025-1", "K025-2", "d1")),
    day_case("K026", "A", fy({}, "y1", "365", amt="1051.20"), {"d1": "2025-10-06"}, ["abe", "bea"],
             {"abe@d1": RES + ["student", "cond4b"], "bea@d1": RES + ["apprentice", "cond4b"]},
             two("K026-1", "K026-2", "d1")),
    day_case("K027", "C", fy({}, "y1", "365", amt="1489.20"), {"d1": "2025-12-15", "d2": "2026-01-15"}, ["cara", "dan"],
             {"cara@d1": RES + ["student_nurse"], "dan@d1": RES + ["ytt", "cond4b"],
              "cara@d2": RES + ["student_nurse", "cond4b"], "dan@d2": RES + ["ytt", "cond4b"]},
             two("K027-1", "K027-2", "d1") + two("K027-3", "K027-4", "d2")),
    day_case("K028", "E", fy({}, "y1", "365", amt="2190.00"), {"d1": "2026-02-02", "d2": "2026-03-02"},
             ["eli", "flo", "gil"],
             {"eli@d1": RES, "flo@d1": RES + ["student", "cond4b"], "gil@d1": RES + PRISON_UK_SENTENCE,
              "eli@d2": RES, "flo@d2": RES + ["student"], "gil@d2": RES + PRISON_UK_SENTENCE},
             two("K028-1", "K028-2", "d1") + two("K028-3", "K028-4", "d2")),
    day_case("K029", "D", fy({}, "y1", "365", amt="2029.40"), {"d1": "2025-06-15", "d2": "2025-07-15"}, ["gus", "hana"],
             {"gus@d1": RES + ["patient", "inst_hs_hospital", "receiving_care"], "hana@d1": RES,
              "gus@d2": RES + ["patient", "smr_inst", "inst_hs_hospital", "receiving_care"],
              "hana@d2": RES},
             two("K029-1", "K029-2", "d1") + two("K029-3", "K029-4", "d2")),
    day_case("K030", "F", fy({}, "y1", "366", amt="2196.00"), {"d1": "2028-02-29"}, ["ike"],
             {"ike@d1": RES + ["patient", "smr_inst", "inst_mil_med"]}, two("K030-1", "K030-2", "d1")),
    day_case("K031", "G", fy({}, "y1", "365", amtd="1839.60"), {"d1": "2025-05-05"}, ["jan", "ken"],
             {"jan@d1": RES + ["patient", "smr_inst", "inst_s275_hospital", "inst_england", "receiving_care"],
              "ken@d1": RES}, two("K031-1", "K031-2", "d1")),
    day_case("K032", "B", fy({}, "y1", "365", amtd="1314.00"), {"d1": "2025-05-01", "d2": "2025-05-10"}, ["lia"],
             {"lia@d1": RES + ["inst_cs2000_care_home", "inst_england", "receiving_care"],
              "lia@d2": RES + ["smr_inst", "inst_cs2000_care_home", "inst_england", "receiving_care"]},
             two("K032-1", "K032-2", "d1") + two("K032-3", "K032-4", "d2")),
    day_case("K033", "C", fy({}, "y1", "365", amt="1664.40"), {"d1": "2025-04-20", "d2": "2025-06-20"}, ["mo", "ned"],
             {"mo@d1": RES + ["smr_inst", "inst_care_act", "inst_england", "receiving_care"], "ned@d1": RES,
              "mo@d2": RES + ["smr_inst", "inst_care_act", "inst_england"], "ned@d2": RES},
             two("K033-1", "K033-2", "d1") + two("K033-3", "K033-4", "d2")),
    day_case("K034", "D", fy({}, "y1", "365", amt="1620.60"), {"d1": "2025-09-09"}, ["ola", "pia"],
             {"ola@d1": RES + ["smr_inst", "inst_england", "receiving_care"], "pia@d1": RES},
             two("K034-1", "K034-2", "d1")),
    day_case("K035", "A", fy({}, "y1", "365", amt="1138.80"), {"d1": "2025-11-10", "d2": "2025-12-10"}, ["ray"],
             {"ray@d1": RES + ["smr_inst", "inst_hostel", "inst_england", "receiving_care"],
              "ray@d2": RES + ["smr_inst", "inst_england", "receiving_care"]},
             two("K035-1", "K035-2", "d1") + two("K035-3", "K035-4", "d2")),
]

UNSUPPORTED = {  # in-scope questions the translation cannot carry (D3a): Q3 over a run of several days
    "K007-run": ("amount over a run of 4 days across two financial years (SUM of count x day amount)", ["K007-3"]),
    "K009-run": ("amount over a run of 30 days in two parts (SUM of count x day amount)", ["K009-3"]),
    "K011-run": ("amount over a run of 6 days in two parts (SUM of count x day amount)", ["K011-5"]),
    "K020-run": ("amount over a run of 4 days in two parts (SUM of count x day amount)", ["K020-5"]),
    "K023-run": ("amount over a run of 4 days in two parts (SUM of count x day amount)", ["K023-3"]),
    "K032-run": ("amount over a run of 10 days in two parts (SUM of count x day amount)", ["K032-5"]),
}
PROBES = {
    "K036": "Wales: s. 5(3) Table and s. 5(1A) proportion out of scope", "K037": "Scotland: out of scope",
    "K038": "care worker, Sch. 1 para. 9 out of scope", "K039": "Scottish care home service, para. 8 out of scope",
    "K040": "night shelter, para. 10 out of scope", "K041": "long-term empty homes premium, s. 11B out of scope",
    "K042": "council tax reduction scheme out of scope", "K043": "order under s. 11(3) changing the percentage",
    "K044": "judgment not stated (para. 2(2))", "K045": "who is liable (s. 6) out of scope",
}
PROBE_QIDS = {"K036": ["K036-1", "K036-2", "K036-3"], "K037": ["K037-1", "K037-2"], "K038": ["K038-1", "K038-2"],
              "K039": ["K039-1", "K039-2"], "K040": ["K040-1", "K040-2"], "K041": ["K041-1", "K041-2"],
              "K042": ["K042-1"], "K043": ["K043-1", "K043-2"], "K044": ["K044-1", "K044-2"],
              "K045": ["K045-1", "K045-2"]}
