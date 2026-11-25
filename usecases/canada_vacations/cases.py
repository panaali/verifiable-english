"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions, Opus encoder.

Encoder: dri-statute-corpus-canada-vacations-w-1124 (Opus 5.5), after the translation was committed (6efc49c476).
Each case: items by kind (translation.Ctx; employment "e", a first employer's employment "e2" where a question asks its own
termination day), "facts" {item: [true facts]} (C1: all others false), "days" {day constant: YYYY-MM-DD}, "cads" {money
constant: "d.cc"}, "cnts" {count constant: n}, "emp" (the dates the bridge reads, C4), "ydays" {year item: (first, last)},
"questions" [(qid, item, form)], "judgement" (anything the encoder decided beyond copying a stated fact: listed).
Forms: translation.DERIVED_UNARY names read as yes/no; "wk" Q1 weeks; "vp" a year's vacation pay; "pp" a period's pay;
"tdue" the amount owed on termination; "dl" the latest payment day (run.VALUE). NOFORM: no rule of translation.py decides the
question as asked: answered OPEN (refused), never forced into a nearby predicate.
Termination cases (encode.py C2, translation R7): every stated completed year whose vacation pay the case says was not paid is
an owed year ("owe", pd = the vacation pay stated as paid in respect of it); termination on a year's last day: "nopart"; the
part year's wages and the vacation pay paid during it as stated.
PROBES: out-of-scope cases (every answer UNSUPPORTED, from the scope field). UNSUPPORTED (in scope): none.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "9de76ea586c6cef3b587004868c82e236b06a1296a9434337c5fe2c31f6f0e35"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

NOFORM = "noform"


def case(cid, qs, emps=("e",), years=None, vacs=None, hols=None, xfers=None, facts=None, days=None, cads=None, cnts=None,
         emp=None, ydays=None, judgement=()):
    return {"id": cid, "emps": list(emps), "years": years or {}, "vacs": vacs or {}, "hols": hols or {},
            "xfers": xfers or {}, "facts": facts or {}, "days": days or {}, "cads": cads or {}, "cnts": cnts or {},
            "emp": emp or {}, "ydays": ydays or {},
            "questions": [{"qid": f"{cid}-{n}", "item": x, "form": fm} for (n, x, fm) in qs], "judgement": list(judgement)}


def AN(start):
    return {"start": start, "kind": "anniv"}


def SET(start, anchor):
    return {"start": start, "kind": "set", "anchor": anchor}


Y = {"y": "e"}
TERM3 = [(1, "y", "wk"), (2, "e", "tdue"), (3, "e", "dl")]


def term_year(cid, start, end, first, last, wages, part=None, pd="0.00", vppt="0.00", qs=TERM3, judgement=()):
    """A case with one year of employment (asked in Q1), employment ended on `end`; the year owed on termination when it is
    completed (the case states no vacation pay paid in respect of it); `part` the part year's stated wages."""
    owe = end >= last
    facts = {"e": ["ceased"] + ([] if part is not None else ["nopart"]), "y": ["owe"] if owe else []}
    cads = {"wy_y": wages, "pd_y": pd, "wt_e": part if part is not None else "0.00", "vppt_e": vppt}
    return case(cid, qs, years=Y, facts=facts, days={"td_e": end}, cads=cads, emp=AN(start), ydays={"y": (first, last)},
                judgement=judgement)


def year_only(cid, emp, first, last, wages, vppy="0.00", qs=((1, "y", "wk"), (2, "y", "vp")), **kw):
    cads = {"wy_y": wages, "vppy_y": vppy, **kw.pop("cads", {})}
    return case(cid, list(qs), years=Y, emp=emp, ydays={"y": (first, last)}, cads=cads, **kw)


def xfer(cid, qs, start1, end1, start2, end2, first, last, xd, tfacts, emps=("e",), extra_days=None, kind=None):
    """A lease/transfer/retendering case: the current employment e (second employer, ended end2), the transfer t."""
    days = {"td_e": end2, "l1_t": end1, "xd_t": xd, "s2_t": start2, **(extra_days or {})}
    emp = {"start": start2, "kind": "set", "anchor": first, "start1": start1, "end1": end1}
    facts = {"e": ["ceased"], "t": list(tfacts)}
    if "e2" in emps:
        facts["e2"] = ["ceased"]
    return case(cid, qs, emps=emps, years=Y, xfers={"t": "e"}, facts=facts, days=days,
                cads={"wy_y": "50000.00", "wt_e": "0.00"}, emp=emp, ydays={"y": (first, last)})


Q12 = [(1, "y", "wk"), (2, "y", "vp")]
Q123 = Q12 + [(3, "e", "dl")]

CASES = [
    # termination on the last day of a year / the day after; first, fifth, tenth anniversaries
    term_year("V001", "2026-04-01", "2027-03-31", "2026-04-01", "2027-03-31", "50000.00"),
    term_year("V002", "2026-04-01", "2027-04-01", "2026-04-01", "2027-03-31", "50000.00", part="500.00"),
    term_year("V003", "2022-04-01", "2027-03-31", "2026-04-01", "2027-03-31", "50000.00"),
    term_year("V004", "2022-04-01", "2027-04-01", "2026-04-01", "2027-03-31", "50000.00", part="500.00"),
    term_year("V005", "2017-04-01", "2027-03-31", "2026-04-01", "2027-03-31", "50000.00"),
    term_year("V006", "2017-04-01", "2027-04-01", "2026-04-01", "2027-03-31", "50000.00", part="500.00"),
    # less than one year: the year asked about is not completed; the part's wages on termination
    term_year("V007", "2026-09-01", "2027-01-01", "2026-09-01", "2027-08-31", "0.00", part="20000.00"),
    # an owed prior year and the completed portion together; 30 days across a month end (31 January, 28 February)
    term_year("V008", "2024-06-01", "2027-01-31", "2025-06-01", "2026-05-31", "50000.00", part="30000.00"),
    term_year("V009", "2024-06-01", "2027-02-28", "2025-06-01", "2026-05-31", "50000.00", part="30000.00",
              pd="2000.00", vppt="2000.00"),
    term_year("V010", "2026-12-01", "2028-02-29", "2026-12-01", "2027-11-30", "40000.00", part="12000.00"),
    term_year("V011", "2025-06-01", "2027-12-15", "2026-06-01", "2027-05-31", "50000.00", part="24000.00"),
    # an employer-determined year (calendar or other) for an industrial establishment
    year_only("V012", SET("2025-12-30", "2026-01-01"), "2026-01-01", "2026-12-31", "40000.00"),
    year_only("V013", SET("2022-04-01", "2026-04-03"), "2026-04-03", "2027-04-02", "50000.00"),
    year_only("V014", SET("2022-04-01", "2026-03-31"), "2026-03-31", "2027-03-30", "50000.00"),
    year_only("V015", SET("2017-04-01", "2026-04-03"), "2026-04-03", "2027-04-02", "50000.00"),
    year_only("V016", SET("2017-04-01", "2026-03-31"), "2026-03-31", "2027-03-30", "50000.00"),
    # vacation pay paid during the year (s.186)
    year_only("V017", AN("2023-01-01"), "2026-01-01", "2026-12-31", "50000.00", vppy="2000.00",
              qs=Q12 + [(3, "e", "vpw")]),
    # one period without a written request (s.184.1 does not need one): no rule of the translation decides "may it be taken
    # in one period" (unit 6 is carried as "more than one period"): refused
    year_only("V018", AN("2024-01-01"), "2026-01-01", "2026-12-31", "50000.00",
              qs=[(1, "y", "wk"), (2, "y", "vp"), (3, "v", NOFORM)], vacs={"v": "y"},
              days={"vs_v": "2027-06-01", "ve_v": "2027-06-14"},
              judgement=["V018-2: the pay for the single vacation period read as the year's vacation pay (s.185(b)(i): "
                         "taken in one period, the vacation pay in respect of that vacation)"]),
    # two periods: written request and written approval; the pay for the 7-day period of a 3-week vacation
    year_only("V019", AN("2020-01-01"), "2026-01-01", "2026-12-31", "60000.00",
              qs=[(1, "y", "wk"), (2, "v1", "pp"), (3, "v1", "splitok")], vacs={"v1": "y", "v2": "y"},
              facts={"v1": ["multi", "reqw", "aprw", "wd7"], "v2": ["multi", "reqw", "aprw", "wd7"]},
              days={"vs_v1": "2027-06-01", "ve_v1": "2027-06-07", "vs_v2": "2027-09-01", "ve_v2": "2027-09-14"},
              cnts={"tkd_v1": 7, "tkd_v2": 14}),
    year_only("V020", AN("2024-01-01"), "2026-01-01", "2026-12-31", "50000.00",
              qs=[(1, "y", "wk"), (2, "y", "vp"), (3, "v", "splitok")], vacs={"v": "y"},
              facts={"v": ["multi", "reqw", "wd7"]}, days={"vs_v": "2027-06-01", "ve_v": "2027-06-07"}),
    year_only("V021", AN("2024-01-01"), "2026-01-01", "2026-12-31", "50000.00",
              qs=[(1, "y", "wk"), (2, "y", "vp"), (3, "v", "splitok")], vacs={"v": "y"},
              facts={"v": ["multi", "aprw", "wd7"]}, days={"vs_v": "2027-06-01", "ve_v": "2027-06-07"}),
    # the last day of the ten months and the next day (February 2028, leap; February 2027)
    year_only("V022", AN("2024-05-01"), "2026-05-01", "2027-04-30", "50000.00",
              qs=[(1, "y", "wk"), (2, "y", "vp"), (3, "v1", "startok"), (4, "v2", "startok")],
              vacs={"v1": "y", "v2": "y"}, days={"vs_v1": "2028-02-29", "ve_v1": "2028-03-13", "vs_v2": "2028-03-01",
                                                 "ve_v2": "2028-03-14"}),
    year_only("V023", AN("2023-05-01"), "2025-05-01", "2026-04-30", "50000.00",
              qs=[(1, "y", "wk"), (2, "y", "vp"), (3, "v1", "startok"), (4, "v2", "startok")],
              vacs={"v1": "y", "v2": "y"}, days={"vs_v1": "2027-02-28", "ve_v1": "2027-03-13", "vs_v2": "2027-03-01",
                                                 "ve_v2": "2027-03-14"}),
    # general holidays during a vacation
    year_only("V024", AN("2024-01-01"), "2026-01-01", "2026-12-31", "50000.00",
              qs=[(1, "y", "wk"), (2, "y", "vp"), (3, "v", "ext"), (4, "v", "hwp"), (5, "v", NOFORM)],
              vacs={"v": "y"}, hols={"h1": "v", "h2": "v"},
              days={"vs_v": "2027-07-01", "ve_v": "2027-07-14", "hd_h1": "2027-07-01", "hd_h2": "2027-07-05"},
              cads={"hw_h1": "200.00", "hw_h2": "200.00"},
              judgement=["V024-3: 'extended by two days' read as the permission of s.187 (one day for each holiday that "
                         "occurs; the two stated holidays)",
                         "V024-4: 'pay $400.00 in general-holiday wages' read as the duty to pay the stated wages of the "
                         "holidays that occur ($200.00 each)"]),
    # sale of a federal business: second employer's first day 90 / 91 / 92 days after the earlier day
    xfer("V025", Q123 + [(4, "t", "gapcnt")], "2020-01-01", "2025-12-31", "2026-04-01", "2027-12-31", "2027-01-01",
         "2027-12-31", "2026-01-10", ["lease", "conn", "fedb"]),
    xfer("V026", Q123 + [(4, "e2", "dl")], "2020-01-01", "2026-01-10", "2026-04-02", "2027-12-31", "2027-01-01",
         "2027-12-31", "2025-12-31", ["lease", "conn", "fedb"], emps=("e", "e2"), extra_days={"td_e2": "2026-01-10"}),
    xfer("V027", Q123, "2020-01-01", "2026-01-10", "2026-04-01", "2027-12-31", "2027-01-01", "2027-12-31", "2025-12-31",
         ["retender", "conn", "fedb"]),
    xfer("V028", Q123 + [(4, "e2", "dl")], "2020-01-01", "2025-12-31", "2026-04-02", "2027-12-31", "2027-01-01",
         "2027-12-31", "2026-01-10", ["retender", "conn", "fedb"], emps=("e", "e2"), extra_days={"td_e2": "2025-12-31"}),
    xfer("V029", Q123 + [(4, "e2", "dl")], "2020-01-01", "2025-12-31", "2026-04-02", "2027-12-31", "2027-01-01",
         "2027-12-31", "2026-01-10", ["lease", "conn", "fedb"], emps=("e", "e2"), extra_days={"td_e2": "2025-12-31"}),
    xfer("V030", Q123, "2020-01-01", "2025-12-31", "2026-04-01", "2027-12-31", "2027-01-01", "2027-12-31", "2026-01-10",
         ["retender", "conn", "fedb"]),
    # a change in activities (s.189(1.3))
    year_only("V031", AN("2020-01-01"), "2027-01-01", "2027-12-31", "50000.00", qs=Q12 + [(3, "e", "nfinc")],
              facts={"e": ["chg"]}),
    # becomes federal due to the transfer; a deleted Schedule IV portion; a severed Schedule V portion; a merger
    xfer("V032", Q123, "2020-01-01", "2026-06-30", "2026-07-01", "2027-12-31", "2027-01-01", "2027-12-31", "2026-07-01",
         ["lease", "conn", "becfed"]),
    xfer("V033", Q123, "2015-01-01", "2026-06-30", "2026-07-01", "2027-12-31", "2027-01-01", "2027-12-31", "2026-07-01",
         ["lease", "conn", "sch145", "deleted", "estcorp"]),
    xfer("V034", Q123 + [(4, "t", "sevapp")], "2015-01-01", "2026-06-30", "2026-07-01", "2027-12-31", "2027-01-01",
         "2027-12-31", "2026-07-01", ["lease", "conn", "inclp", "severed", "estcorp", "sevpaid"]),
    xfer("V035", Q123 + [(4, "t", "sevapp")], "2020-01-01", "2026-06-30", "2026-07-01", "2027-12-31", "2027-01-01",
         "2027-12-31", "2026-07-01", ["lease", "conn", "fedb"]),
]

PROBES = {
    "V036": "severance pay under s.235 (not in the pinned text)",
    "V037": "pay in lieu of notice under s.230 (not in the pinned text; s.189(1.5) out of scope)",
    "V038": "a province's vacation law",
    "V039": "another country's vacation law",
    "V040": "the time the regulations prescribe for paying vacation pay",
    "V041": "which days are general holidays",
    "V042": "general-holiday wages",
    "V043": "a collective agreement above the minimum",
    "V044": "sick leave",
    "V045": "parental leave",
}
PROBE_QIDS = {cid: [f"{cid}-1"] for cid in PROBES}
UNSUPPORTED = {}
