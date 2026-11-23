"""Tests of the HICBC bridge (681H(3) calendar, 681C(2)-(3) arithmetic), each with a planted error that must fail it.

Run: python3 -I usecases/hicbc/bridge/test_bridges.py   (stdlib only; prints PASS/FAIL lines and the planted-error result)
"""
import copy
import datetime as dt
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load():
    spec = importlib.util.spec_from_file_location("bridges", HERE / "bridges.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def case(**kw):
    c = {"id": "T", "tax_year": "2025-26", "subject": "A", "people": ["A", "B", "C"], "ani": {"A": "70000", "B": "50000"},
         "cb": [{"claimant": "B", "child": "C", "weekly": "26.05", "from": "2025-04-07", "to": "2026-03-30", "basis": "a",
                 "election": None}], "rel": [], "lives": []}
    c.update(kw)
    return c


def tests(b):
    out = []

    def ok(name, got, want):
        out.append((name, got == want, got, want))

    D = dt.date
    ok("2024-25 has 52 Monday-weeks", len(b.mondays(*b.tax_year("2024-25"))), 52)
    ok("2025-26 has 52 Monday-weeks (6 April 2025 is a Sunday)", len(b.mondays(*b.tax_year("2025-26"))), 52)
    ok("2026-27 has 53 Monday-weeks (6 April 2026 and 5 April 2027 are Mondays)", len(b.mondays(*b.tax_year("2026-27"))), 53)
    ok("first week of 2025-26 begins Monday 7 April 2025", b.mondays(*b.tax_year("2025-26"))[0], D(2025, 4, 7))
    ok("last week of 2024-25 begins Monday 31 March 2025", b.mondays(*b.tax_year("2024-25"))[-1], D(2025, 3, 31))
    ok("tax year bounds 6 April to 5 April", b.tax_year("2024-25"), (D(2024, 4, 6), D(2025, 4, 5)))
    for ani, want in (("60000", 0), ("60001", 0), ("60199.99", 0), ("60200", 1), ("64350", 21), ("79999", 99),
                      ("80000", 100), ("80001", 100), ("150000", 100)):
        ok(f"pct({ani}) = {want}", b.pct(ani), want)
    br = b.case_bridge(case())
    ok("whole-year entitlement: one item of 52 weeks", [(i["weeks"], i["total_pence"]) for i in br["items"]], [(52, 135460)])
    tbl = b.charge_table(br, "A")
    ok("charge table: 50% of floor(1354.60) = 677", [r["charge"] for r in tbl], ["0.00", "677.00"])
    br2 = b.case_bridge(case(ani={"A": "64350", "B": "1"}))
    ok("charge 21% of 1354 = 284.34 rounded down to 284", b.charge_table(br2, "A")[1]["charge"], "284.00")
    c3 = case(cb=[{"claimant": "B", "child": "C", "weekly": "17.25", "from": "2025-04-07", "to": "2025-04-14", "basis": "a",
                   "election": None}], ani={"A": "80000", "B": "1"})
    ok("total 34.50 rounded down to 34 before the percentage", b.charge_table(b.case_bridge(c3), "A")[1]["charge"], "34.00")
    c3b = case(cb=[{"claimant": "B", "child": "C", "weekly": "1.99", "from": "2025-04-07", "to": "2025-04-07", "basis": "a",
                    "election": None}], ani={"A": "79999", "B": "1"})
    ok("total 1.99 rounded down to 1 before 99%: charge 0 (not 1)", b.charge_table(b.case_bridge(c3b), "A")[1]["charge"], "0.00")
    br4b = b.case_bridge(case(rel=[{"pair": ["A", "B"], "kind": "as_if_married", "from": "2025-04-07", "to": "2025-09-07"}]))
    ok("living together ending on Sunday 7 September 2025: no split week", [len(s["daytypes"]) for s in br4b["segments"]], [1, 1])
    # throughout the week: a marriage on a Wednesday splits that week
    br4 = b.case_bridge(case(rel=[{"pair": ["A", "B"], "kind": "married_or_cp", "from": "2025-09-10", "to": None}]))
    ok("marriage on Wednesday 10 September 2025: segments 22/1/29 weeks", [s["weeks"] for s in br4["segments"]], [22, 1, 29])
    ok("the marriage week holds two day-types", [len(s["daytypes"]) for s in br4["segments"]], [1, 2, 1])
    br5 = b.case_bridge(case(rel=[{"pair": ["A", "B"], "kind": "married_or_cp", "from": "2025-09-08", "to": None}]))
    ok("marriage on a Monday: no split week", [len(s["daytypes"]) for s in br5["segments"]], [1, 1])
    # a weekly record covers the weeks whose Monday lies in it
    c6 = case(cb=[{"claimant": "B", "child": "C", "weekly": "26.05", "from": "2026-03-30", "to": None, "basis": "a",
                   "election": None}])
    ok("open entitlement from the last Monday: 1 week in 2025-26", [i["weeks"] for i in b.case_bridge(c6)["items"]], [1])
    # 681D(4)
    recs = [{"claimant": "B", "child": "C", "weekly": "25.60", "from": "2024-04-08", "to": "2024-06-03", "basis": "a", "election": None},
            {"claimant": "B", "child": "C", "weekly": "25.60", "from": "2024-06-10", "to": "2024-08-26", "basis": "b", "election": None},
            {"claimant": "B", "child": "C", "weekly": "25.60", "from": "2024-09-02", "to": "2025-03-31", "basis": "a", "election": None}]
    br7 = b.case_bridge(case(tax_year="2024-25", cb=recs))
    ok("12-week (b) period between (a) weeks: short, before, after", [(i["d4_short"], i["d4_a_before"], i["d4_a_after"])
                                                                       for i in br7["items"] if i["basis"] == "b"], [(True, True, True)])
    recs2 = copy.deepcopy(recs)
    recs2[1]["to"], recs2[2]["from"] = "2025-06-09", "2025-06-16"
    br8 = b.case_bridge(case(tax_year="2024-25", cb=recs2))
    ok("53-week (b) period: not short", {i["d4_short"] for i in br8["items"] if i["basis"] == "b"}, {False})
    recs3 = copy.deepcopy(recs)
    recs3[1]["to"], recs3[2]["from"] = "2025-06-02", "2025-06-09"
    br9 = b.case_bridge(case(tax_year="2024-25", cb=recs3))
    ok("52-week (b) period: short (does not exceed 52)", {i["d4_short"] for i in br9["items"] if i["basis"] == "b"}, {True})
    # election weeks
    c10 = case(cb=[{"claimant": "B", "child": "C", "weekly": "26.05", "from": "2025-04-07", "to": "2026-03-30", "basis": "a",
                    "election": ["2025-10-06", None]}])
    ok("election from 6 October 2025: 26 + 26 weeks", [(i["weeks"], i["election_13a"]) for i in b.case_bridge(c10)["items"]],
       [(26, False), (26, True)])
    ok("quotes: a date not in the facts is reported", b.check_quotes(case(), "from 7 April 2025"), ["2026-03-30"])
    ok("quotes: all present", b.check_quotes(case(), "7 April 2025 to 30 March 2026"), [])
    return out


PLANTED = {
    "P1 week starts on Sunday": ("mondays", lambda m: (lambda s, e: [d - dt.timedelta(days=1) for d in m(s, e)])),
    "P2 percentage rounded to nearest": ("pct", lambda f: (lambda a: min(100, max(0, round((float(a) - 60000) / 200))))),
    "P3 'exceeds' read as at least": ("pct", lambda f: (lambda a: 1 if float(a) == 60000 else f(a))),
    "P4 total not rounded down before the percentage": (
        "charge_table", lambda f: (lambda br, s: [dict(r, charge=f"{int(sum(i['total_pence'] for i in br['items'] if i['item'] in r['counted']) * br['pct'][s] // 10000)}.00") for r in f(br, s)])),
    "P5 a relationship holds the day after its end": ("holds_on", lambda f: (lambda r, d: f(r, d) or f(r, d - dt.timedelta(days=1)))),
    "P6 52 weeks read as 'less than 52'": ("d4_facts", lambda f: (lambda c, r, m: (lambda x: (x[0] and (b_run_len(c, r, m) < 52), x[1], x[2]))(f(c, r, m)))),
    "P7 tax year from 5 April": ("tax_year", lambda f: (lambda ty: (f(ty)[0] - dt.timedelta(days=1), f(ty)[1] - dt.timedelta(days=1)))),
}


def b_run_len(c, r, m):
    return MOD.b_run(c, r, m)[0] or 0


def main():
    global MOD
    MOD = load()
    res = tests(MOD)
    for name, good, got, want in res:
        print(("PASS  " if good else "FAIL  ") + name + ("" if good else f" (got {got!r}, want {want!r})"))
    fails = sum(not g for _, g, _, _ in res)
    caught = 0
    for pname, (fn, wrap) in PLANTED.items():
        MOD = load()
        setattr(MOD, fn, wrap(getattr(MOD, fn)))
        try:
            r = tests(MOD)
            n = sum(not g for _, g, _, _ in r)
        except Exception as e:  # a planted error that crashes is caught too
            n = f"crash {type(e).__name__}"
        print(f"planted {pname}: {'CAUGHT' if n else 'MISSED'} ({n} failing)")
        caught += bool(n)
    print(f"result: {len(res) - fails} passed, {fails} failed; planted errors caught {caught} of {len(PLANTED)}")
    return 0 if fails == 0 and caught == len(PLANTED) else 1


if __name__ == "__main__":
    sys.exit(main())
