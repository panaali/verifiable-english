"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions, Opus encoder.

Encoder: dri-statute-corpus-pensions-auto-enrolment-w-1124 (Opus 5.5), after the translation was committed (070993e7bf;
R7a structural change 50852f3951, before any answer was read); encode.py C1-C7.
Each question maps to one form of run.py on one item: Q1 s. 3(2) -> (employment, duty3); Q1 s. 5(2) -> (the re-enrolment
date's day, duty5); Q2 -> (period, qe); Q3 -> (the asked day, fails; the brief's list is the same for s. 3(1) and 5(1));
Q4 -> (employment, aedate). "judgement": anything the encoder decided beyond copying a stated fact (encoder judgement).
Every in-scope case states a window: form (b) cases give it to the bridge (points, C7) with the stated dates inside it on
which a fact changes (period first days, the pensionable age day, Great Britain change days, as the case states them);
form (a) cases (the automatic enrolment date stated, or the s. 4 deferral's later date) use the stated date as a day.
Every stated day: its age and prescribed-period start from the bridge (stated date of birth).
PROBES: out-of-scope cases (every answer UNSUPPORTED, D11). UNSUPPORTED (in scope): none.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "204b034cd5118610db8f734e49e7c2993c60409d72362bc5b8f527bf43afe30e"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

SAL = ["conn", "da"]
ALL_GB = [None, None]


def emp(j, days=(), periods=(), sums=(), members=(), lengths=None):
    return {"j": j, "days": list(days), "periods": list(periods), "sums": list(sums), "members": list(members),
            "lengths": {r: list(v) for r, v in (lengths or {}).items()}}


def case(cid, emps, qs, dob, facts=None, ints=None, payin=(), days=None, windows=None, gb_window=None,
         unplaced=(), open_cause=(), judgement=()):
    """days: {day item: stated date}; windows: {employment: (first, last, *stated change dates)}."""
    bridge, ints = [], dict(ints or {})
    for x, d in (days or {}).items():
        ints[f"day_{x}"] = d
        bridge += [{"item": x, "kind": "age", "dob": dob, "day": d}, {"item": x, "kind": "pst", "day": d}]
    for j, w in (windows or {}).items():
        ints[f"wf_{j}"], ints[f"wl_{j}"] = w[0], w[1]
        bridge.append({"item": j, "kind": "points", "first": w[0], "last": w[1], "dob": dob, "dates": list(w[2:])})
    c = {"id": cid, "emps": emps, "facts": {k: list(v) for k, v in (facts or {}).items()}, "ints": ints,
         "payin": [list(p) for p in payin], "bridge": bridge, "gb_window": dict(gb_window or {}),
         "unplaced": list(unplaced), "open_cause": list(open_cause), "judgement": list(judgement), "questions": []}
    for i, (x, f) in enumerate(qs):
        c["questions"].append({"qid": f"{cid}-{i + 1}", "item": x, "form": f})
    return c


def per(r, first, last, n, amount, unit="m", s=None):
    """A stated period r (first, last, length n months/weeks) with ONE stated salary sum s."""
    s = s or "s" + r
    ints = {f"pf_{r}": first, f"pt_{r}": last, (f"pw_{r}" if unit == "w" else f"pm_{r}"): n, f"amt_{s}": amount}
    return r, s, (unit, n), ints


def simple(cid, qs, dob, window, periods, j_facts=("pnever",), days=None, gb=ALL_GB, extra_dates=(), ints=None,
           facts=None, judgement=()):
    """One form (b) employment j with salary-only periods [(r, first, last, n, amount, unit)], a window and Q3 days."""
    ps, ss, lengths, allints, payin, f = [], [], {}, dict(ints or {}), [], {"j": list(j_facts) + ["formb"]}
    for p in periods:
        r, s, ln, pi = per(*p)
        ps.append(r)
        ss.append(s)
        lengths[r] = ln
        allints.update(pi)
        payin.append((s, r))
        f[s] = SAL
        if ln[0] == "w":
            f[r] = ["inweeks"]
    for x, d in (days or {}).items():
        on = (gb[0] is None or gb[0] <= d) and (gb[1] is None or d <= gb[1])
        f[x] = ["gb"] if on else []
    f.update(facts or {})
    dates = sorted({p[1] for p in periods} | set(extra_dates))
    return case(cid, [emp("j", list(days or {}), ps, ss, lengths=lengths)], qs, dob, facts=f, ints=allints,
                payin=payin, days=days, windows={"j": (window[0], window[1], *dates)}, gb_window={"j": gb},
                judgement=judgement)


def fixed(cid, qs, dob, x_day, periods, members=(), j_facts=("pnever",), x_facts=("gb",), ints=None, facts=None,
          open_cause=(), judgement=(), extra_days=None):
    """One form (a) / re-enrolment employment j: the stated day x (and extra stated days), salary-only periods."""
    ps, ss, lengths, allints, payin = [], [], {}, dict(ints or {}), []
    f = {"j": list(j_facts), "x": list(x_facts)}
    for p in periods:
        r, s, ln, pi = per(*p)
        ps.append(r)
        ss.append(s)
        lengths[r] = ln
        allints.update(pi)
        payin.append((s, r))
        f[s] = SAL
        if ln[0] == "w":
            f[r] = ["inweeks"]
    f.update(facts or {})
    days = {"x": x_day, **(extra_days or {})}
    return case(cid, [emp("j", list(days), ps, ss, list(members), lengths)], qs, dob, facts=f, ints=allints,
                payin=payin, days=days, open_cause=open_cause, judgement=judgement)


M = "m"
CASES = [
    # P001 window 1-3 May 2027, born 2 May 2005 (22 on 2 May), May 900.00
    simple("P001", [("j", "duty3"), ("d1", "fails"), ("d2", "fails"), ("d3", "fails"), ("j", "aedate")], "2005-05-02",
           ("2027-05-01", "2027-05-03"), [("r1", "2027-05-01", "2027-05-31", 1, "900.00")],
           days={"d1": "2027-05-01", "d2": "2027-05-02", "d3": "2027-05-03"}),
    # P002 window 28 Feb - 1 Mar 2026, born 29 Feb 2004; Feb 800.00, Mar 900.00
    simple("P002", [("j", "duty3"), ("d1", "fails"), ("j", "aedate"), ("r1", "qe")], "2004-02-29",
           ("2026-02-28", "2026-03-01"), [("r1", "2026-02-01", "2026-02-28", 1, "800.00"),
                                          ("r2", "2026-03-01", "2026-03-31", 1, "900.00")],
           days={"d1": "2026-02-28"}),
    # P003 window 31 May - 1 Jun 2027, born 1 Jun 2011 (16 on 1 Jun); 1,200.00 a month
    simple("P003", [("j", "duty3"), ("d1", "fails"), ("d2", "fails")], "2011-06-01", ("2027-05-31", "2027-06-01"),
           [("r1", "2027-05-01", "2027-05-31", 1, "1200.00"), ("r2", "2027-06-01", "2027-06-30", 1, "1200.00")],
           days={"d1": "2027-05-31", "d2": "2027-06-01"}),
    # P004 window 30 Jun - 1 Jul 2027, born 1 Jul 1952 (75 on 1 Jul), pensionable age 1 Jul 2019; 1,000.00 a month
    simple("P004", [("j", "duty3"), ("d1", "fails"), ("d2", "fails")], "1952-07-01", ("2027-06-30", "2027-07-01"),
           [("r1", "2027-06-01", "2027-06-30", 1, "1000.00"), ("r2", "2027-07-01", "2027-07-31", 1, "1000.00")],
           j_facts=(), ints={"pday_j": "2019-07-01"}, days={"d1": "2027-06-30", "d2": "2027-07-01"}),
    # P005 window 14-15 Aug 2027, born 15 Aug 1960, pensionable age 15 Aug 2027; Aug 1,000.00
    simple("P005", [("j", "duty3"), ("d1", "fails"), ("d2", "fails"), ("j", "aedate")], "1960-08-15",
           ("2027-08-14", "2027-08-15"), [("r1", "2027-08-01", "2027-08-31", 1, "1000.00")], j_facts=(),
           ints={"pday_j": "2027-08-15"}, extra_dates=("2027-08-15",), days={"d1": "2027-08-14", "d2": "2027-08-15"}),
    # P006 / P007 window 2027, one 12-month period, 10,000.00 / 10,000.01
    simple("P006", [("j", "duty3"), ("r1", "qe"), ("j", "aedate")], "1990-01-01", ("2027-01-01", "2027-12-31"),
           [("r1", "2027-01-01", "2027-12-31", 12, "10000.00")]),
    simple("P007", [("j", "duty3"), ("r1", "qe"), ("j", "aedate")], "1990-01-01", ("2027-01-01", "2027-12-31"),
           [("r1", "2027-01-01", "2027-12-31", 12, "10000.01")]),
    # P008 window Feb-Mar 2027: 833.33, 833.34
    simple("P008", [("j", "duty3"), ("d1", "fails"), ("j", "aedate")], "1990-02-01", ("2027-02-01", "2027-03-31"),
           [("r1", "2027-02-01", "2027-02-28", 1, "833.33"), ("r2", "2027-03-01", "2027-03-31", 1, "833.34")],
           days={"d1": "2027-02-01"}),
    # P009 window 1-14 Mar 2027: weekly 192.30, 192.31
    simple("P009", [("j", "duty3"), ("d1", "fails"), ("j", "aedate")], "1990-03-01", ("2027-03-01", "2027-03-14"),
           [("r1", "2027-03-01", "2027-03-07", 1, "192.30", "w"), ("r2", "2027-03-08", "2027-03-14", 1, "192.31", "w")],
           days={"d1": "2027-03-01"}),
    # P010 window 1 Apr - 26 May 2027: four-weekly 769.23, 769.24
    simple("P010", [("j", "duty3"), ("d1", "fails"), ("j", "aedate")], "1990-04-01", ("2027-04-01", "2027-05-26"),
           [("r1", "2027-04-01", "2027-04-28", 4, "769.23", "w"), ("r2", "2027-04-29", "2027-05-26", 4, "769.24", "w")],
           days={"d1": "2027-04-01"}),
    # P011 window Jan-Jun 2027: quarterly 2,500.00, 2,500.01
    simple("P011", [("j", "duty3"), ("d1", "fails"), ("j", "aedate")], "1990-01-01", ("2027-01-01", "2027-06-30"),
           [("r1", "2027-01-01", "2027-03-31", 3, "2500.00"), ("r2", "2027-04-01", "2027-06-30", 3, "2500.01")],
           days={"d1": "2027-01-01"}),
    # P012 window Feb-Apr 2027: 519.99, 520.00, 520.01
    simple("P012", [("j", "duty3"), ("r1", "qe"), ("r2", "qe"), ("r3", "qe")], "1990-02-01",
           ("2027-02-01", "2027-04-30"),
           [("r1", "2027-02-01", "2027-02-28", 1, "519.99"), ("r2", "2027-03-01", "2027-03-31", 1, "520.00"),
            ("r3", "2027-04-01", "2027-04-30", 1, "520.01")]),
    # P013 window 1-21 May 2027: weekly 119.99, 120.00, 120.01
    simple("P013", [("j", "duty3"), ("r1", "qe"), ("r2", "qe"), ("r3", "qe")], "1990-05-01",
           ("2027-05-01", "2027-05-21"),
           [("r1", "2027-05-01", "2027-05-07", 1, "119.99", "w"), ("r2", "2027-05-08", "2027-05-14", 1, "120.00", "w"),
            ("r3", "2027-05-15", "2027-05-21", 1, "120.01", "w")]),
    # P014 / P015 window 2025-2027: three 12-month periods
    simple("P014", [("j", "duty3"), ("r1", "qe"), ("r2", "qe"), ("r3", "qe")], "1990-01-01",
           ("2025-01-01", "2027-12-31"),
           [("r1", "2025-01-01", "2025-12-31", 12, "6239.99"), ("r2", "2026-01-01", "2026-12-31", 12, "6240.00"),
            ("r3", "2027-01-01", "2027-12-31", 12, "6240.01")]),
    simple("P015", [("j", "duty3"), ("r1", "qe"), ("r2", "qe"), ("r3", "qe")], "1990-01-01",
           ("2025-01-01", "2027-12-31"),
           [("r1", "2025-01-01", "2025-12-31", 12, "50269.99"), ("r2", "2026-01-01", "2026-12-31", 12, "50270.00"),
            ("r3", "2027-01-01", "2027-12-31", 12, "50270.01")]),
    # P016 window Jan-Sep 2027: quarterly 12,567.49 / .50 / .51
    simple("P016", [("j", "duty3"), ("r1", "qe"), ("r2", "qe"), ("r3", "qe")], "1990-01-01",
           ("2027-01-01", "2027-09-30"),
           [("r1", "2027-01-01", "2027-03-31", 3, "12567.49"), ("r2", "2027-04-01", "2027-06-30", 3, "12567.50"),
            ("r3", "2027-07-01", "2027-09-30", 3, "12567.51")]),
    # P017 window 2027-2028: one 24-month period 100,540.02
    simple("P017", [("j", "duty3"), ("r1", "qe"), ("j", "aedate")], "1990-01-01", ("2027-01-01", "2028-12-31"),
           [("r1", "2027-01-01", "2028-12-31", 24, "100540.02")]),
]

# P018 every s. 13(3) description, a prescribed sum, and three sums outside the list (12-month period, window 2027)
_P18 = [("a1", "2000.00", ["da"]), ("a2", "1000.00", ["da"]), ("a3", "1000.00", ["da"]), ("a4", "1000.00", ["da"]),
        ("a5", "1000.00", ["da"]), ("b", "1000.00", ["db"]), ("c", "1000.00", ["dc"]), ("dd", "1000.00", ["dd"]),
        ("e", "1000.00", ["de"]), ("ea", "1000.00", ["dea"]), ("eb", "1000.00", ["deb"]), ("ec", "1000.00", ["dec"]),
        ("f", "1000.00", ["df"]), ("x1", "800.00", []), ("x2", "2000.00", []), ("x3", "3000.00", [])]
_P19 = [("a1", "6240.00", ["da"]), ("x1", "5000.00", []), ("x2", "5000.00", []), ("x3", "5000.00", [])]


def _listed(cid, items, qs):
    """P018/P019: salary, wages, commission, bonuses, overtime (a); the statutory pays (b)-(ec); the retention award
    stated prescribed (f); reimbursed travel expenses, benefits in kind (not of a listed description); the pension from
    the earlier employment (not of a listed description; 'in connection with' the present employment not stated: conn
    false)."""
    sums = ["s" + n for n, _, _ in items]
    f = {"j": ["pnever", "formb"], "d1": ["gb"]}
    ints = {"pf_r1": "2027-01-01", "pt_r1": "2027-12-31", "pm_r1": 12}
    for n, amt, desc in items:
        f["s" + n] = (["conn"] if n != "x3" else []) + desc
        ints["amt_s" + n] = amt
    return case(cid, [emp("j", ["d1"], ["r1"], sums, lengths={"r1": ("m", 12)})], qs, "1990-01-01", facts=f, ints=ints,
                payin=[(s, "r1") for s in sums], days={"d1": "2027-01-01"},
                windows={"j": ("2027-01-01", "2027-12-31", "2027-01-01")}, gb_window={"j": ALL_GB})


CASES += [
    _listed("P018", _P18, [("j", "duty3"), ("r1", "qe"), ("d1", "fails")]),
    _listed("P019", _P19, [("j", "duty3"), ("r1", "qe"), ("d1", "fails")]),
    # P020 two employers at once in September 2027: Harbour Crafts (h) 900.00; Willow Music (w) 800.00, active member
    case("P020", [emp("h", [], ["rh"], ["sh"], lengths={"rh": ("m", 1)}),
                  emp("w", [], ["rw"], ["sw"], ["mw"], lengths={"rw": ("m", 1)})],
         [("h", "duty3"), ("w", "duty3"), ("rw", "qe")], "1990-09-01",
         facts={"h": ["pnever", "formb"], "w": ["pnever", "formb"], "sh": SAL, "sw": SAL, "mw": ["qual"]},
         ints={"pf_rh": "2027-09-01", "pt_rh": "2027-09-30", "pm_rh": 1, "amt_sh": "900.00",
               "pf_rw": "2027-09-01", "pt_rw": "2027-09-30", "pm_rw": 1, "amt_sw": "800.00",
               "mf_mw": "2027-09-01", "mt_mw": "2027-09-30"},
         payin=[("sh", "rh"), ("sw", "rw")],
         windows={"h": ("2027-09-01", "2027-09-30", "2027-09-01"), "w": ("2027-09-01", "2027-09-30", "2027-09-01")},
         gb_window={"h": ALL_GB, "w": ALL_GB}),
    # P021 a succession: Ash Textiles (a) January 2027, 850.00, active member all January; Beech Textiles (b) February,
    # 800.00
    case("P021", [emp("a", [], ["ra"], ["sa"], ["ma"], lengths={"ra": ("m", 1)}),
                  emp("b", [], ["rb"], ["sb"], lengths={"rb": ("m", 1)})],
         [("a", "duty3"), ("b", "duty3"), ("rb", "qe")], "1990-01-01",
         facts={"a": ["pnever", "formb"], "b": ["pnever", "formb"], "sa": SAL, "sb": SAL,
                "ma": ["qual", "ceased", "notown"]},
         ints={"pf_ra": "2027-01-01", "pt_ra": "2027-01-31", "pm_ra": 1, "amt_sa": "850.00",
               "pf_rb": "2027-02-01", "pt_rb": "2027-02-28", "pm_rb": 1, "amt_sb": "800.00",
               "mf_ma": "2027-01-01", "mt_ma": "2027-01-31", "cday_ma": "2027-02-01"},
         payin=[("sa", "ra"), ("sb", "rb")],
         windows={"a": ("2027-01-01", "2027-01-31", "2027-01-01"), "b": ("2027-02-01", "2027-02-28", "2027-02-01")},
         gb_window={"a": ALL_GB, "b": ALL_GB}),
    # P022 window 1-2 Nov 2027: in Great Britain on 1 November only; November 1,000.00
    simple("P022", [("j", "duty3"), ("d1", "fails"), ("j", "aedate")], "1990-11-01", ("2027-11-01", "2027-11-02"),
           [("r1", "2027-11-01", "2027-11-30", 1, "1000.00")], days={"d1": "2027-11-02"}, gb=[None, "2027-11-01"],
           extra_dates=("2027-11-02",)),
    # P023-P027 form (a): the s. 4 deferral's later date is the automatic enrolment date (the stated day x)
    fixed("P023", [("j", "duty3"), ("rr", "qe")], "1990-03-01", "2027-04-01",
          [("rr", "2027-04-01", "2027-04-30", 1, "1200.00")], members=["m"], j_facts=("pnever", "deferred"),
          x_facts=("gb", "aestated"), facts={"m": ["qual"]},
          ints={"dfrom_j": "2027-03-01", "dto_j": "2027-04-01", "mf_m": "2027-03-01", "mt_m": "2027-04-01"}),
    fixed("P024", [("j", "duty3"), ("x", "fails")], "1990-03-01", "2027-04-01",
          [("rr", "2027-04-01", "2027-04-30", 1, "1200.00")], members=["m"], j_facts=("pnever", "deferred"),
          x_facts=("gb", "aestated"), facts={"m": ["qual", "ceased", "notown"]},
          ints={"dfrom_j": "2027-03-01", "dto_j": "2027-04-01", "mf_m": "2027-03-01", "mt_m": "2027-03-31",
                "cday_m": "2027-04-01"}),
    fixed("P025", [("j", "duty3"), ("rr", "qe")], "1990-06-01", "2027-06-01",
          [("rr", "2027-06-01", "2027-06-30", 1, "1500.00")], members=["m"], j_facts=("pnever", "deferred"),
          x_facts=("gb", "aestated"), facts={"m": ["qual", "ceased", "own"]},
          ints={"dfrom_j": "2026-06-01", "dto_j": "2027-06-01", "mf_m": "2026-06-01", "mt_m": "2026-06-30",
                "cday_m": "2026-07-01"}),
    fixed("P026", [("j", "duty3"), ("rr", "qe")], "1990-04-01", "2027-06-01",
          [("rr", "2027-06-01", "2027-06-30", 1, "1500.00")], members=["m"], j_facts=("pnever", "deferred"),
          x_facts=("gb", "aestated"), facts={"m": ["qual", "ceased", "own"]},
          ints={"dfrom_j": "2026-04-01", "dto_j": "2027-06-01", "mf_m": "2026-04-01", "mt_m": "2026-04-30",
                "cday_m": "2026-05-01"}),
    fixed("P027", [("j", "duty3"), ("rr", "qe")], "1990-05-01", "2027-06-01",
          [("rr", "2027-06-01", "2027-06-30", 1, "1500.00")], members=["m"], j_facts=("pnever", "deferred"),
          x_facts=("gb", "aestated"), facts={"m": ["qual", "ceased", "own"]},
          ints={"dfrom_j": "2026-05-01", "dto_j": "2027-06-01", "mf_m": "2026-05-01", "mt_m": "2026-05-31",
                "cday_m": "2026-06-01"}),
    # P028-P035 re-enrolment: x = the stated automatic re-enrolment date
    fixed("P028", [("x", "duty5"), ("rr", "qe"), ("x", "fails")], "1990-01-01", "2027-06-01",
          [("rr", "2027-06-01", "2027-06-30", 1, "900.00")], members=["m"], j_facts=("pnever", "hasaed"),
          x_facts=("gb", "reday"), facts={"m": ["qual", "ceased", "own"]},
          ints={"aed_j": "2025-01-01", "mf_m": "2025-01-01", "mt_m": "2025-01-31", "cday_m": "2025-02-01"}),
    fixed("P029", [("x", "duty5"), ("x", "fails")], "1990-01-01", "2027-06-01",
          [("rr", "2027-06-01", "2027-06-30", 1, "900.00")], members=["m"], j_facts=("pnever", "hasaed"),
          x_facts=("gb", "reday"), facts={"m": ["qual"]},
          ints={"aed_j": "2025-01-01", "mf_m": "2025-01-01", "mt_m": "2027-06-01"}),
    fixed("P030", [("x", "duty5"), ("x", "fails")], "1990-05-01", "2027-06-01",
          [("rr", "2027-06-01", "2027-06-30", 1, "900.00")], j_facts=("pnever", "hasaed", "deferred"),
          x_facts=("gb", "reday"), ints={"aed_j": "2027-07-01", "dfrom_j": "2027-05-01", "dto_j": "2027-07-01"}),
    fixed("P031", [("x", "duty5"), ("x", "fails")], "1990-04-01", "2027-06-01",
          [("rr", "2027-06-01", "2027-06-30", 1, "900.00")], members=["m"], j_facts=("pnever", "hasaed", "deferred"),
          x_facts=("gb", "reday"), facts={"m": ["qual", "ceased", "own"]},
          ints={"aed_j": "2027-05-01", "dfrom_j": "2027-04-01", "dto_j": "2027-05-01", "mf_m": "2027-05-01",
                "mt_m": "2027-05-01", "cday_m": "2027-05-02"}),
    fixed("P032", [("x", "duty5"), ("x", "fails"), ("r1", "qe"), ("r2", "qe")], "1990-01-01", "2027-05-01",
          [("r1", "2027-04-01", "2027-04-30", 1, "520.00"), ("r2", "2027-05-01", "2027-05-31", 1, "700.00")],
          members=["m"], j_facts=("pnever", "hasaed"), x_facts=("gb", "reday"), facts={"m": ["qual", "ceased", "gbqe"]},
          open_cause=["m"],
          ints={"aed_j": "2025-01-01", "mf_m": "2025-01-01", "mt_m": "2027-03-31", "cday_m": "2027-04-01",
                "gap_m": "2027-04-01"},
          judgement=["P032: the stated cause (the April reduction in salary, at the jobholder's request) read as a "
                     "period in which s. 1(1)(c) was not met (April's 520.00), beginning 1 April 2027; whether the "
                     "request makes it the jobholder's own action is left open (no 'own'/'notown')"]),
    fixed("P033", [("x", "duty5"), ("x", "fails"), ("r2", "qe")], "1990-01-01", "2027-05-01",
          [("r1", "2027-04-01", "2027-04-30", 1, "700.00"), ("r2", "2027-05-01", "2027-05-31", 1, "700.00")],
          members=["m"], j_facts=("pnever", "hasaed"), x_facts=("gb", "reday"), facts={"m": ["qual", "ceased", "gbqe"]},
          open_cause=["m"],
          ints={"aed_j": "2025-01-01", "mf_m": "2025-01-01", "mt_m": "2027-03-31", "cday_m": "2027-04-01",
                "gap_m": "2027-04-01"},
          judgement=["P033: the stated cause (the move to work outside Great Britain for April, at the jobholder's "
                     "request) read as a period in which s. 1(1)(a) was not met, beginning 1 April 2027; own action "
                     "left open"]),
    fixed("P034", [("x", "duty5"), ("x", "fails"), ("rr", "qe")], "1957-05-01", "2027-05-01",
          [("rr", "2027-05-01", "2027-05-31", 1, "700.00")], members=["m"], j_facts=("hasaed",),
          x_facts=("gb", "reday"), facts={"m": ["qual", "ceased", "notown"]},
          ints={"pday_j": "2024-05-01", "aed_j": "2020-01-01", "mf_m": "2020-01-01", "mt_m": "2027-04-30",
                "cday_m": "2027-05-01"}),
    fixed("P035", [("x", "duty5"), ("x", "fails"), ("r2", "qe")], "1990-01-01", "2027-05-01",
          [("r1", "2027-04-01", "2027-04-30", 1, "100.00"), ("r2", "2027-05-01", "2027-05-31", 1, "520.00")],
          members=["m"], j_facts=("pnever", "hasaed"), x_facts=("gb", "reday"), facts={"m": ["qual", "ceased", "gbqe"]},
          open_cause=["m"],
          ints={"aed_j": "2025-01-01", "mf_m": "2025-01-01", "mt_m": "2027-03-31", "cday_m": "2027-04-01",
                "gap_m": "2027-04-01"},
          judgement=["P035: the stated cause (the April reduction in salary, at the jobholder's request) read as a "
                     "period in which s. 1(1)(c) was not met (April's 100.00); own action left open"]),
]

PROBES = {f"P0{n}": "out of scope (the writer's scope field; contributions, tax relief, opting out and refunds, "
                     "enforcement, s. 4 itself, pensionable age, Northern Ireland, other countries, scheme rules)"
          for n in range(36, 46)}
PROBE_QIDS = {cid: [f"{cid}-1"] for cid in PROBES}
UNSUPPORTED = {}
