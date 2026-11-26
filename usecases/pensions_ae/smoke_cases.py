"""Made-up smoke cases (written with the translation, NOT from the question file), hand-worked answers in EXPECT.
Each case: one or more employments; days carry a stated date ("day_<x>") and a bridged age / prescribed-period start
(bridge kinds "age", "pst" from the stated date of birth); windows are listed by the bridge ("days")."""
DOB = "1990-06-15"


def emp(j, days=(), periods=(), sums=(), members=(), lengths=None):
    return {"j": j, "days": list(days), "periods": list(periods), "sums": list(sums), "members": list(members),
            "lengths": {r: list(v) for r, v in (lengths or {}).items()}}


def case(cid, emps, qs, facts=None, ints=None, payin=(), days=None, dob=DOB, windows=None, gb_window=None,
         unplaced=(), open_cause=(), judgement=()):
    """days: {day item: date} (stated; age and pst bridged from dob); windows: {employment: (first, last)}."""
    bridge, ints = [], dict(ints or {})
    for x, d in (days or {}).items():
        ints[f"day_{x}"] = d
        bridge += [{"item": x, "kind": "age", "dob": dob, "day": d}, {"item": x, "kind": "pst", "day": d}]
    for j, w in (windows or {}).items():
        a, b = w[0], w[1]
        ints[f"wf_{j}"], ints[f"wl_{j}"] = a, b
        bridge.append({"item": j, "kind": "points", "first": a, "last": b, "dob": dob, "dates": list(w[2:])})
    c = {"id": cid, "emps": emps, "facts": {k: list(v) for k, v in (facts or {}).items()}, "ints": ints,
         "payin": [list(p) for p in payin], "bridge": bridge,          "gb_window": dict(gb_window or {}), "unplaced": list(unplaced), "open_cause": list(open_cause),
         "judgement": list(judgement), "questions": []}
    for i, (x, f) in enumerate(qs):
        c["questions"].append({"qid": f"{cid}-{i + 1}", "item": x, "form": f})
    return c


def month(r, first, last, n=1):
    return {f"pf_{r}": first, f"pt_{r}": last, f"pm_{r}": n}


SAL = ["conn", "da"]
CASES = [
    # S1 monthly 900.00 salary: over 833.33..., qe 380.00; form (a) AE date, no membership: duty
    case("S1", [emp("j", ["x"], ["r"], ["s"], lengths={"r": ("m", 1)})],
         [("x", "s3"), ("r", "qe"), ("x", "fails"), ("j", "duty3")],
         facts={"j": ["pnever"], "x": ["gb", "aestated"], "s": SAL}, payin=[("s", "r")],
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "900.00"}, days={"x": "2027-05-01"}),
    # S2 monthly 833.33: 12 x 833.33 = 9,999.96, not more than 10,000; qe 313.33
    case("S2", [emp("j", ["x"], ["r"], ["s"], lengths={"r": ("m", 1)})],
         [("x", "s3"), ("r", "qe"), ("x", "fails")],
         facts={"j": ["pnever"], "x": ["gb"], "s": SAL}, payin=[("s", "r")],
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "833.33"}, days={"x": "2027-05-10"}),
    # S3 one week 192.31: 52 x 192.31 = 10,000.12 > 10,000; qe 192.31 - 120 = 72.31
    case("S3", [emp("j", ["x"], ["r"], ["s"], lengths={"r": ("w", 1)})],
         [("x", "s3"), ("r", "qe")],
         facts={"j": ["pnever"], "x": ["gb"], "r": ["inweeks"], "s": SAL}, payin=[("s", "r")],
         ints={"pf_r": "2027-05-03", "pt_r": "2027-05-09", "pw_r": 1, "amt_s": "192.31"}, days={"x": "2027-05-05"}),
    # S4 monthly 5,000.00: capped, (50,270 - 6,240)/12 = 3,669.1666...: no exact answer
    case("S4", [emp("j", ["x"], ["r"], ["s"], lengths={"r": ("m", 1)})], [("r", "qe")],
         facts={"j": ["pnever"], "x": ["gb"], "s": SAL}, payin=[("s", "r")],
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "5000.00"}, days={"x": "2027-05-10"}),
    # S5 the same, half up stated: 3,669.17
    case("S5", [emp("j", ["x"], ["r"], ["s"], lengths={"r": ("m", 1)})], [("r", "qe")],
         facts={"j": ["pnever"], "x": ["gb"], "r": ["halfup"], "s": SAL}, payin=[("s", "r")],
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "5000.00"}, days={"x": "2027-05-10"}),
    # S6 the day before the 22nd birthday, 500.00 a month (no qualifying earnings: 500 <= 520), not in GB
    case("S6", [emp("j", ["x"], ["r"], ["s"], lengths={"r": ("m", 1)})], [("x", "fails"), ("x", "s3"), ("r", "qe")],
         facts={"j": ["pnever"], "s": SAL}, payin=[("s", "r")], dob="2005-05-11",
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "500.00"}, days={"x": "2027-05-10"}),
    # S7 form (b) window 1-5 May 2027, 22nd birthday 3 May: AE date 3 May; no membership: duty
    case("S7", [emp("j", [], ["r"], ["s"], lengths={"r": ("m", 1)})], [("j", "aedate"), ("j", "duty3")],
         facts={"j": ["pnever", "formb"], "s": SAL}, payin=[("s", "r")], dob="2005-05-03",
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "900.00"},
         windows={"j": ("2027-05-01", "2027-05-05")}, gb_window={"j": [None, None]}),
    # S8 form (b), the same window, 25 years old but under the trigger: none in the window; duty no
    case("S8", [emp("j", [], ["r"], ["s"], lengths={"r": ("m", 1)})], [("j", "aedate"), ("j", "duty3")],
         facts={"j": ["pnever", "formb"], "s": SAL}, payin=[("s", "r")], dob="2002-01-01",
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "800.00"},
         windows={"j": ("2027-05-01", "2027-05-05")}, gb_window={"j": [None, None]}),
    # S9 form (a) AE 1 May 2027; own notice, cessation 1 June 2026 (11 months before): s. 3(4): no duty
    case("S9", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("j", "duty3")],
         facts={"j": ["pnever"], "x": ["gb", "aestated"], "s": SAL, "m": ["qual", "ceased", "own"]}, payin=[("s", "r")],
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "900.00", "mf_m": "2025-01-01", "mt_m": "2026-05-31",
               "cday_m": "2026-06-01"}, days={"x": "2027-05-01"}),
    # S10 the same, cessation 1 March 2026 (14 months before): outside the prescribed period: duty
    case("S10", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("j", "duty3")],
         facts={"j": ["pnever"], "x": ["gb", "aestated"], "s": SAL, "m": ["qual", "ceased", "own"]}, payin=[("s", "r")],
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "900.00", "mf_m": "2025-01-01", "mt_m": "2026-02-28",
               "cday_m": "2026-03-01"}, days={"x": "2027-05-01"}),
    # S11 active member on the AE date: s. 3(3): no duty
    case("S11", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("j", "duty3")],
         facts={"j": ["pnever"], "x": ["gb", "aestated"], "s": SAL, "m": ["qual", "mopen"]}, payin=[("s", "r")],
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "900.00", "mf_m": "2025-01-01"},
         days={"x": "2027-05-01"}),
    # S12 salary 500 + SSP 400 + reimbursed expenses 300 in a month: earnings 900, over; qe 380.00
    case("S12", [emp("j", ["x"], ["r"], ["s", "t", "u"], lengths={"r": ("m", 1)})], [("x", "s3"), ("r", "qe")],
         facts={"j": ["pnever"], "x": ["gb"], "s": SAL, "t": ["conn", "db"], "u": ["conn"]},
         payin=[("s", "r"), ("t", "r"), ("u", "r")],
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "500.00", "amt_t": "400.00", "amt_u": "300.00"},
         days={"x": "2027-05-10"}),
    # S13 two employers at once, 600.00 a month each: neither over
    case("S13", [emp("j", ["x"], ["r"], ["s"], lengths={"r": ("m", 1)}),
                 emp("k", ["y"], ["q"], ["t"], lengths={"q": ("m", 1)})], [("x", "s3"), ("y", "s3")],
         facts={"j": ["pnever"], "k": ["pnever"], "x": ["gb"], "y": ["gb"], "s": SAL, "t": SAL},
         payin=[("s", "r"), ("t", "q")],
         ints={**month("r", "2027-05-01", "2027-05-31"), **month("q", "2027-05-01", "2027-05-31"),
               "amt_s": "600.00", "amt_t": "600.00"}, days={"x": "2027-05-10", "y": "2027-05-10"}),
    # S14 12-month period, exactly 10,000.00: not more than; qe 3,760.00
    case("S14", [emp("j", ["x"], ["r"], ["s"], lengths={"r": ("m", 12)})], [("x", "fails"), ("r", "qe")],
         facts={"j": ["pnever"], "x": ["gb"], "s": SAL}, payin=[("s", "r")],
         ints={**month("r", "2027-04-06", "2028-04-05", 12), "amt_s": "10000.00"}, days={"x": "2027-05-10"}),
    # S15 the 75th birthday (age outside), on the day pensionable age is reached
    case("S15", [emp("j", ["x"], ["r"], ["s"], lengths={"r": ("m", 1)})], [("x", "fails")],
         facts={"x": ["gb"], "s": SAL}, payin=[("s", "r")], dob="1952-05-10",
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "900.00", "pday_j": "2027-05-10"},
         days={"x": "2027-05-10"}),
    # S16 re-enrolment 1 June 2027, age 70, pensionable age reached, scheme closed by the employer 2026: s. 5(1B): duty
    case("S16", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("x", "s5"), ("x", "duty5")],
         facts={"x": ["gb", "reday"], "s": SAL, "m": ["qual", "ceased", "notown"]}, payin=[("s", "r")],
         dob="1957-01-01",
         ints={**month("r", "2027-06-01", "2027-06-30"), "amt_s": "900.00", "pday_j": "2023-01-01",
               "mf_m": "2020-01-01", "mt_m": "2026-03-31", "cday_m": "2026-04-01"}, days={"x": "2027-06-01"}),
    # S17 as S16 with a s. 4 deferral from 1 June 2027 (the re-enrolment date itself) to 1 September 2027: not (3A): duty
    case("S17", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("x", "duty5")],
         facts={"j": ["deferred"], "x": ["gb", "reday"], "s": SAL, "m": ["qual", "ceased", "notown"]},
         payin=[("s", "r")], dob="1957-01-01",
         ints={**month("r", "2027-06-01", "2027-06-30"), "amt_s": "900.00", "pday_j": "2023-01-01",
               "mf_m": "2020-01-01", "mt_m": "2026-03-31", "cday_m": "2026-04-01", "dfrom_j": "2027-06-01",
               "dto_j": "2027-09-01"}, days={"x": "2027-06-01"}),
    # S18 s. 5(1A): age 30, AE date 2024-01-01, stopped working in GB 2026-02-01 (period from then), back; under the trigger
    case("S18", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("x", "s5"), ("x", "duty5")],
         facts={"j": ["pnever", "hasaed"], "x": ["gb", "reday"], "s": SAL, "m": ["qual", "ceased", "gbqe"]},
         payin=[("s", "r")], open_cause=["m"],
         ints={**month("r", "2027-06-01", "2027-06-30"), "amt_s": "700.00", "aed_j": "2024-01-01",
               "mf_m": "2024-01-01", "mt_m": "2026-01-31", "cday_m": "2026-02-01", "gap_m": "2026-02-01"},
         days={"x": "2027-06-01"}),
    # S19 as S18 at 21 (under 22): (1), (1A) fail; (1B) not settled for a GB cessation: no answer
    case("S19", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("x", "s5")],
         facts={"j": ["pnever", "hasaed"], "x": ["gb", "reday"], "s": SAL, "m": ["qual", "ceased", "gbqe"]},
         payin=[("s", "r")], open_cause=["m"], dob="2006-01-01",
         ints={**month("r", "2027-06-01", "2027-06-30"), "amt_s": "700.00", "aed_j": "2024-01-01",
               "mf_m": "2024-01-01", "mt_m": "2026-01-31", "cday_m": "2026-02-01", "gap_m": "2026-02-01"},
         days={"x": "2027-06-01"}),
    # S20 a sum the encoder cannot place: no answer for the earnings
    case("S20", [emp("j", ["x"], ["r"], ["s", "t"], lengths={"r": ("m", 1)})], [("r", "qe"), ("x", "s3")],
         facts={"j": ["pnever"], "x": ["gb"], "s": SAL, "t": ["conn"]}, payin=[("s", "r"), ("t", "r")],
         unplaced=["t"], ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "900.00", "amt_t": "50.00"},
         days={"x": "2027-05-10"}),
    # S21 form (b) window 1 April - 31 May 2027, two monthly periods of 900.00, age 36: AE 1 April (s. 3 on both points)
    case("S21", [emp("j", [], ["r", "q"], ["s", "t"], lengths={"r": ("m", 1), "q": ("m", 1)})],
         [("j", "aedate"), ("j", "duty3")],
         facts={"j": ["pnever", "formb"], "s": SAL, "t": SAL}, payin=[("s", "r"), ("t", "q")],
         ints={**month("r", "2027-04-01", "2027-04-30"), **month("q", "2027-05-01", "2027-05-31"),
               "amt_s": "900.00", "amt_t": "900.00"},
         windows={"j": ("2027-04-01", "2027-05-31", "2027-05-01", "2027-06-01")}, gb_window={"j": [None, None]}),
    # S22 form (b) three years, yearly periods 6,239.99 / 6,240.00 / 6,240.01: s. 3 on no day; duty no
    case("S22", [emp("j", [], ["a", "b", "c"], ["s", "t", "u"],
                     lengths={"a": ("m", 12), "b": ("m", 12), "c": ("m", 12)})],
         [("j", "aedate"), ("j", "duty3"), ("c", "qe")],
         facts={"j": ["pnever", "formb"], "s": SAL, "t": SAL, "u": SAL}, payin=[("s", "a"), ("t", "b"), ("u", "c")],
         ints={**month("a", "2025-01-01", "2025-12-31", 12), **month("b", "2026-01-01", "2026-12-31", 12),
               **month("c", "2027-01-01", "2027-12-31", 12), "amt_s": "6239.99", "amt_t": "6240.00",
               "amt_u": "6240.01"},
         windows={"j": ("2025-01-01", "2027-12-31", "2026-01-01", "2027-01-01", "2028-01-01")},
         gb_window={"j": [None, None]}),
    # S23 form (b) window 30 June - 1 July 2027, worker stops working in Great Britain on 1 July, under the trigger on
    # 30 June (800.00 in June) and over it in July: s. 3 on no day; Q3 on 1 July
    case("S23", [emp("j", ["x"], ["r", "q"], ["s", "t"], lengths={"r": ("m", 1), "q": ("m", 1)})],
         [("j", "aedate"), ("x", "fails")],
         facts={"j": ["pnever", "formb"], "s": SAL, "t": SAL}, payin=[("s", "r"), ("t", "q")],
         ints={**month("r", "2027-06-01", "2027-06-30"), **month("q", "2027-07-01", "2027-07-31"),
               "amt_s": "800.00", "amt_t": "900.00"}, days={"x": "2027-07-01"},
         windows={"j": ("2027-06-30", "2027-07-01", "2027-07-01")}, gb_window={"j": [None, "2027-06-30"]}),
    # S24 as S9 but the scheme left by notice on 1 March 2027 is stated NOT qualifying: s. 3(4) does not apply: duty
    case("S24", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("j", "duty3")],
         facts={"j": ["pnever"], "x": ["gb", "aestated"], "s": SAL, "m": ["ceased", "own"]}, payin=[("s", "r")],
         ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "900.00", "mf_m": "2025-01-01", "mt_m": "2027-02-28",
               "cday_m": "2027-03-01"}, days={"x": "2027-05-01"}),
    # S25 a qualifying scheme's membership ceased 1 December 2026 because the person stopped working in Great Britain
    # (cause otherwise unstated), inside the prescribed period: s. 3(4) not settled: no answer
    case("S25", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("j", "duty3")],
         facts={"j": ["pnever"], "x": ["gb", "aestated"], "s": SAL, "m": ["qual", "ceased", "gbqe"]}, payin=[("s", "r")],
         open_cause=["m"], ints={**month("r", "2027-05-01", "2027-05-31"), "amt_s": "900.00", "mf_m": "2024-01-01",
                                 "mt_m": "2026-11-30", "cday_m": "2026-12-01", "gap_m": "2026-12-01"},
         days={"x": "2027-05-01"}),
    # S26 as S18 but the scheme is stated NOT qualifying: neither (1A) nor (1B); under the trigger: no duty
    case("S26", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("x", "s5"), ("x", "duty5")],
         facts={"j": ["pnever", "hasaed"], "x": ["gb", "reday"], "s": SAL, "m": ["ceased", "gbqe"]},
         payin=[("s", "r")], open_cause=["m"],
         ints={**month("r", "2027-06-01", "2027-06-30"), "amt_s": "700.00", "aed_j": "2024-01-01",
               "mf_m": "2024-01-01", "mt_m": "2026-01-31", "cday_m": "2026-02-01", "gap_m": "2026-02-01"},
         days={"x": "2027-06-01"}),
    # S27 age 36, under the trigger, a scheme stated NOT qualifying closed by the employer 1 March 2027: not (1B): no duty
    case("S27", [emp("j", ["x"], ["r"], ["s"], ["m"], lengths={"r": ("m", 1)})], [("x", "s5"), ("x", "duty5")],
         facts={"j": ["pnever"], "x": ["gb", "reday"], "s": SAL, "m": ["ceased", "notown"]}, payin=[("s", "r")],
         ints={**month("r", "2027-06-01", "2027-06-30"), "amt_s": "800.00", "mf_m": "2025-01-01",
               "mt_m": "2027-02-28", "cday_m": "2027-03-01"}, days={"x": "2027-06-01"}),
]
EXPECT = {
    "S1-1": "yes", "S1-2": "380.00", "S1-3": "none", "S1-4": "yes",
    "S2-1": "no", "S2-2": "313.33", "S2-3": "earnings not more than the threshold",
    "S3-1": "yes", "S3-2": "72.31",
    "S4-1": "OPEN",
    "S5-1": "3669.17",
    "S6-1": "not working in Great Britain; no qualifying earnings; under 22; earnings not more than the threshold",
    "S6-2": "no", "S6-3": "0.00",
    "S7-1": "2027-05-03", "S7-2": "yes",
    "S8-1": None, "S8-2": "no",
    "S9-1": "no", "S10-1": "yes", "S11-1": "no",
    "S12-1": "yes", "S12-2": "380.00",
    "S13-1": "no", "S13-2": "no",
    "S14-1": "earnings not more than the threshold", "S14-2": "3760.00",
    "S15-1": "age outside 16 to under 75; pensionable age reached",
    "S16-1": "yes", "S16-2": "yes", "S17-1": "yes",
    "S18-1": "yes", "S18-2": "yes", "S19-1": "OPEN",
    "S20-1": "OPEN", "S20-2": "OPEN",
    "S21-1": "2027-04-01", "S21-2": "yes",
    "S22-1": None, "S22-2": "no", "S22-3": "0.01",
    "S23-1": None, "S23-2": "not working in Great Britain",
    "S24-1": "yes", "S25-1": "OPEN", "S26-1": "no", "S26-2": "no", "S27-1": "no", "S27-2": "no",
}
