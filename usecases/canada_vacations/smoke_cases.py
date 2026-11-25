"""Made-up smoke cases with hand-worked answers (written with the translation, NOT from the question file).
Each case: the structure of cases.py (encode.py conventions C1-C5)."""


def case(cid, qs, years=None, vacs=None, hols=None, xfers=None, facts=None, days=None, cads=None, cnts=None, emp=None,
         ydays=None):
    return {"id": cid, "emps": ["e"], "years": years or {}, "vacs": vacs or {}, "hols": hols or {}, "xfers": xfers or {},
            "facts": facts or {}, "days": days or {}, "cads": cads or {}, "cnts": cnts or {}, "emp": emp or {},
            "ydays": ydays or {}, "questions": [{"qid": f"{cid}-{n}", "item": x, "form": fm} for (n, x, fm) in qs],
            "judgement": []}


AN = lambda start: {"start": start, "kind": "anniv"}  # noqa: E731
Y = {"y": "e"}

CASES = [
    # fifth year: 3 weeks, 6 %; vacation beginning on the last day of the ten months
    case("S01", [(1, "y", "wk"), (2, "y", "vp"), (3, "v", "startok")], years=Y, vacs={"v": "y"},
         emp=AN("2020-03-15"), ydays={"y": ("2024-03-15", "2025-03-14")}, cads={"wy_y": "52000.00"},
         days={"vs_v": "2026-01-14"}),
    # fourth year: 2 weeks, 4 % of wages with vacation pay paid during the year (s.186)
    case("S02", [(1, "y", "wk"), (2, "y", "vp"), (3, "e", "vpw")], years=Y, emp=AN("2020-03-15"),
         ydays={"y": ("2023-03-15", "2024-03-14")}, cads={"wy_y": "50000.00", "vppy_y": "2000.00"}),
    # termination: owed fifth year + part at 6 %; 30 days
    case("S03", [(1, "e", "tdue"), (2, "e", "dl")], years=Y, facts={"e": ["ceased"], "y": ["owe"]},
         emp=AN("2020-03-15"), ydays={"y": ("2024-03-15", "2025-03-14")}, days={"td_e": "2025-06-30"},
         cads={"wy_y": "52000.00", "pd_y": "0.00", "wt_e": "15000.00"}),
    # split: request without approval; with approval; period pay 1 of 3 weeks
    case("S04", [(1, "v1", "splitok"), (2, "v2", "splitok"), (3, "v2", "pp")], years=Y, vacs={"v1": "y", "v2": "y"},
         facts={"v1": ["reqw", "multi"], "v2": ["reqw", "aprw", "multi"]}, emp=AN("2020-03-15"),
         ydays={"y": ("2024-03-15", "2025-03-14")}, cads={"wy_y": "52000.00"}, cnts={"tkw_v2": 1},
         days={"vs_v1": "2025-06-01", "vs_v2": "2025-06-01"}),
    # general holidays: one on the first day of the vacation, one after it
    case("S05", [(1, "v", "ext"), (2, "v", "hwp"), (3, "v", "hws")], years=Y, vacs={"v": "y"},
         hols={"h1": "v", "h2": "v"}, emp=AN("2020-03-15"), ydays={"y": ("2024-03-15", "2025-03-14")},
         cads={"wy_y": "52000.00", "hw_h1": "200.00", "hw_h2": "180.00"},
         days={"vs_v": "2025-07-01", "ve_v": "2025-07-14", "hd_h1": "2025-07-01", "hd_h2": "2025-08-04"}),
    # sale of a federal business, second employer's first day 91 days after the earlier day: continuous (count B)
    case("S06", [(1, "y", "wk"), (2, "t", "gapcnt"), (3, "t", "sevapp"), (4, "t", "dc")], years=Y,
         xfers={"t": "e"}, facts={"t": ["lease", "conn", "fedb"]},
         emp={"start": "2025-04-01", "kind": "anniv", "start1": "2015-01-01", "end1": "2024-12-31"},
         ydays={"y": ("2025-04-01", "2026-03-31")},
         days={"l1_t": "2024-12-31", "xd_t": "2025-01-01", "s2_t": "2025-04-01"}),
    # the same on the 92nd day: not continuous (count A)
    case("S07", [(1, "y", "wk"), (2, "t", "late"), (3, "t", "dc")], years=Y, xfers={"t": "e"},
         facts={"t": ["lease", "conn", "fedb"]},
         emp={"start": "2025-04-02", "kind": "anniv", "start1": "2015-01-01", "end1": "2024-12-31"},
         ydays={"y": ("2025-04-02", "2026-04-01")},
         days={"l1_t": "2024-12-31", "xd_t": "2025-01-01", "s2_t": "2025-04-02"}),
    # a deleted Schedule IV portion established as a corporation (s.189(2))
    case("S08", [(1, "t", "fed"), (2, "t", "dc1")], xfers={"t": "e"},
         facts={"t": ["lease", "conn", "sch145", "deleted", "estcorp"]},
         days={"l1_t": "2024-12-31", "xd_t": "2025-01-01", "s2_t": "2025-01-01"}),
    # becomes federal due to the transfer
    case("S09", [(1, "t", "dc1")], xfers={"t": "e"}, facts={"t": ["lease", "conn", "becfed"]},
         days={"l1_t": "2024-12-31", "xd_t": "2025-01-01", "s2_t": "2025-01-01"}),
    # severance paid by the first employer
    case("S10", [(1, "t", "sevapp"), (2, "t", "dc")], xfers={"t": "e"}, facts={"t": ["lease", "conn", "fedb", "sevpaid"]},
         days={"l1_t": "2024-12-31", "xd_t": "2025-01-01", "s2_t": "2025-01-01"}),
    # change in activities
    case("S11", [(1, "e", "nfinc")], facts={"e": ["chg"]}),
    # retendering of a federal work
    case("S12", [(1, "t", "dc11"), (2, "t", "dc")], xfers={"t": "e"}, facts={"t": ["retender", "conn", "fedb"]},
         days={"l1_t": "2025-03-31", "xd_t": "2025-04-01", "s2_t": "2025-04-01"}),
    # the earlier day is the transfer day: late
    case("S13", [(1, "t", "late"), (2, "t", "dc")], xfers={"t": "e"}, facts={"t": ["lease", "conn", "fedb"]},
         days={"l1_t": "2025-03-31", "xd_t": "2025-01-01", "s2_t": "2025-04-03"}),
    # calendar kind, termination: 4 kind-years against 5 elapsed years: the percentage refused; the day answered
    case("S15", [(1, "e", "tdue"), (2, "e", "dl")], facts={"e": ["ceased"]},
         emp={"start": "2022-07-01", "kind": "set", "anchor": "2027-01-01"}, days={"td_e": "2027-09-30"},
         cads={"wt_e": "30000.00"}),
    # half-up rounding: 4 % and 6 %
    case("S16", [(1, "y1", "vp"), (2, "y2", "vp")], years={"y1": "e", "y2": "e"}, facts={"e": ["hu"]},
         emp=AN("2020-03-15"), ydays={"y1": ("2022-03-15", "2023-03-14"), "y2": ("2025-03-15", "2026-03-14")},
         cads={"wy_y1": "51234.57", "wy_y2": "51234.57"}),
    # days table: 5 of 15 working days
    case("S17", [(1, "v", "pp")], years=Y, vacs={"v": "y"}, facts={"v": ["multi", "wd5"]}, emp=AN("2020-03-15"),
         ydays={"y": ("2024-03-15", "2025-03-14")}, cads={"wy_y": "52000.00"}, cnts={"tkd_v": 5}),
    # less than one year at termination
    case("S18", [(1, "e", "tdue"), (2, "e", "dl")], facts={"e": ["ceased"]}, emp=AN("2026-03-15"),
         days={"td_e": "2026-12-01"}, cads={"wt_e": "20000.00"}),
    # year not completed: terminated the day before the first anniversary
    case("S19", [(1, "y", "wk"), (2, "y", "vp")], years=Y, facts={"e": ["ceased"]}, emp=AN("2026-03-15"),
         ydays={"y": ("2026-03-15", "2027-03-14")}, days={"td_e": "2027-03-13"}, cads={"wy_y": "40000.00", "wt_e": "0.00"}),
    # tenth year: 4 weeks, 8 %; a vacation beginning the day after the ten months
    case("S20", [(1, "y", "wk"), (2, "y", "vp"), (3, "v", "startok")], years=Y, vacs={"v": "y"}, emp=AN("2016-03-15"),
         ydays={"y": ("2025-03-15", "2026-03-14")}, cads={"wy_y": "60000.00"}, days={"vs_v": "2027-01-15"}),
    # ninth year, terminated on the last day of a year: owed year at 6 %, no part
    case("S21", [(1, "e", "tdue"), (2, "e", "dl"), (3, "y", "wk")], years=Y, facts={"e": ["ceased", "nopart"], "y": ["owe"]},
         emp=AN("2016-03-15"), ydays={"y": ("2024-03-15", "2025-03-14")}, days={"td_e": "2025-03-14"},
         cads={"wy_y": "50000.00", "pd_y": "1000.00", "wt_e": "0.00"}),
]

EXPECTED = {
    "S01-1": {"answer": "3 weeks", "value": "3"}, "S01-2": {"answer": "$3,120.00", "value": "3120.00"},
    "S01-3": {"answer": "yes"},
    "S02-1": {"answer": "2 weeks", "value": "2"}, "S02-2": {"answer": "$2,080.00", "value": "2080.00"},
    "S02-3": {"answer": "yes"},
    "S03-1": {"answer": "$4,020.00", "value": "4020.00"}, "S03-2": {"answer": "2025-07-30", "value": "2025-07-30"},
    "S04-1": {"answer": "no"}, "S04-2": {"answer": "yes"}, "S04-3": {"answer": "$1,040.00", "value": "1040.00"},
    "S05-1": {"answer": "yes"}, "S05-2": {"answer": "yes"}, "S05-3": {"answer": "$200.00", "value": "200.00"},
    "S06-1": {"answer": "4 weeks", "value": "4"}, "S06-2": {"answer": "no"}, "S06-3": {"answer": "yes"},
    "S06-4": {"answer": "yes"},
    "S07-1": {"answer": "2 weeks", "value": "2"}, "S07-2": {"answer": "yes"}, "S07-3": {"answer": "no"},
    "S08-1": {"answer": "yes"}, "S08-2": {"answer": "yes"},
    "S09-1": {"answer": "yes"},
    "S10-1": {"answer": "no"}, "S10-2": {"answer": "yes"},
    "S11-1": {"answer": "yes"},
    "S12-1": {"answer": "yes"}, "S12-2": {"answer": "yes"},
    "S13-1": {"answer": "yes"}, "S13-2": {"answer": "no"},
    "S15-1": "OPEN", "S15-2": {"answer": "2027-10-30", "value": "2027-10-30"},
    "S16-1": {"answer": "$2,049.38", "value": "2049.38"}, "S16-2": {"answer": "$3,074.07", "value": "3074.07"},
    "S17-1": {"answer": "$1,040.00", "value": "1040.00"},
    "S18-1": {"answer": "$800.00", "value": "800.00"}, "S18-2": {"answer": "2026-12-31", "value": "2026-12-31"},
    "S19-1": {"answer": "none", "value": "0"}, "S19-2": {"answer": "none", "value": "0.00"},
    "S20-1": {"answer": "4 weeks", "value": "4"}, "S20-2": {"answer": "$4,800.00", "value": "4800.00"},
    "S20-3": {"answer": "no"},
    "S21-1": {"answer": "$2,000.00", "value": "2000.00"}, "S21-2": {"answer": "2025-04-13", "value": "2025-04-13"},
    "S21-3": {"answer": "3 weeks", "value": "3"},
}
