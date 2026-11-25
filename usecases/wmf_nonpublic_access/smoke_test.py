"""Smoke test on MADE-UP cases (not from the question file), written with the translation: the staged route (Python prover,
no Lean) must give the hand-worked answers below, refuse where a reading refuses, and every planted error must change one.
CROSS-FAMILY set, Opus translator.  usage (repository root): .venv/bin/python -B usecases/wmf_nonpublic_access/smoke_test.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "bridge"))
import encode as E  # noqa: E402
import run as R  # noqa: E402
import translation as T  # noqa: E402
import wmf_bridge as WB  # noqa: E402

OK_FACTS = ["cert", "sub", "subvalid", "link", "linkvalid", "cs"]
OK_DAYS = {"certd": "2026-03-10", "subd": "2026-03-01", "linkd": "2026-03-01", "csd": "2026-03-12"}


def test(a, at=None, app=None, more=(), less=(), days=None):
    f = [x for x in OK_FACTS if x not in less] + list(more)
    ints = {f"{b}_{a}": v for b, v in {**OK_DAYS, **(days or {})}.items()}
    if at:
        ints[f"at_{a}"] = at
    if app:
        ints[f"app_{a}"] = app
    return f, ints


def mk(cid, qs, facts=None, ints=None, bridge=None, **items):
    c = {"id": cid, "facts": facts or {}, "ints": ints or {}, **items,
         "questions": [{"qid": f"{cid}-{i}", "item": x, "form": f} for i, (x, f) in enumerate(qs, 1)]}
    br = {(cid, x): WB.row(r) for x, r in (bridge or {}).items()}
    return c, br


def grant_case(cid, dob, at, app=None, ert=False, more=(), less=(), days=None, extra=None):
    f, ints = test("a1", at, app, more + (("ert",) if ert else ()), less, days)
    facts = {"a1": f}
    items = {"tests": ["a1"]}
    if extra:
        facts.update(extra.get("facts", {}))
        ints.update(extra.get("ints", {}))
        items.update(extra.get("items", {}))
    return mk(cid, [("a1", "ok")], facts, ints, {"a1": {"kind": "age", "dob": dob}}, **items)


CASES = [
    # S1 CheckUser applicant turning 18 on the grant day (dob 15 Mar 2008): everything in order -> yes
    (grant_case("S1", "2008-03-15", "2026-03-15", "2026-03-15"), ["yes"]),
    # S2 the day before the 18th birthday -> no
    (grant_case("S2", "2008-03-15", "2026-03-14", days={"certd": "2026-03-10", "csd": "2026-03-12"}), ["no"]),
    # S3 ERT applying at 15 (20 Apr), 16 on 1 May (the day asked): two readings -> OPEN
    (grant_case("S3", "2010-05-01", "2026-05-01", "2026-04-20", ert=True), ["OPEN"]),
    # S4 ERT exactly 16, verification requested 25 Apr and never completed -> no
    (grant_case("S4", "2010-05-01", "2026-05-01", "2026-05-01", ert=True, more=("vrq",),
                days={"vrqd": "2026-04-25"}), ["no"]),
    # S5 ERT role NOT applied for: 17-year-old applying for Steward -> no; with a Legal-reviewed age exemption -> yes
    (grant_case("S5", "2009-01-10", "2026-06-01", "2026-06-01"), ["no"]),
    (grant_case("S5b", "2009-01-10", "2026-06-01", "2026-06-01", more=("exm_age",)), ["yes"]),
    # S6 no Confidentiality Agreement -> no; community criteria unmet with all else met -> OPEN
    (grant_case("S6", "1990-01-01", "2026-06-01", less=("cs",)), ["no"]),
    (grant_case("S6b", "1990-01-01", "2026-06-01", more=("crit_unmet",)), ["OPEN"]),
    # S7 email change 1 Apr informed 8 Apr (day 7: in time); change 10 Apr never informed; grant tested 20 Apr -> no
    (mk("S7", [("e1", "inok"), ("e1", "chglim"), ("e2", "inok"), ("a1", "ok")],
        {"a1": OK_FACTS, "e1": ["inf"]},
        {**test("a1", "2026-04-20")[1], "chgd_e1": "2026-04-01", "infd_e1": "2026-04-08", "chgd_e2": "2026-04-10",
         "askd_e2": "2026-04-20"},
        {"a1": {"kind": "age", "dob": "1990-01-01"}}, tests=["a1"], changes=["e1", "e2"]),
     ["yes", "2026-04-08", "no", "no"]),
    # S8 the same with the grant tested on 17 Apr (the second change's week still running) -> yes
    (mk("S8", [("a1", "ok")], {"a1": OK_FACTS, "e1": ["inf"]},
        {**test("a1", "2026-04-17")[1], "chgd_e1": "2026-04-01", "infd_e1": "2026-04-08", "chgd_e2": "2026-04-10"},
        {"a1": {"kind": "age", "dob": "1990-01-01"}}, tests=["a1"], changes=["e1", "e2"]), ["yes"]),
    # S9 disclosure to a vendor for IP blocks on Mon 15 Jun 2026, explanation sent Mon 1 Jun, approval 10 Jun -> may
    (mk("S9", [("d1", "maydisc"), ("d1", "needappr"), ("d1", "lat"), ("d1", "nopre"), ("d1", "obliged"), ("d1", "early")],
        {"d1": ["r_vendor", "ipblk", "sent", "appr", "apprst", "disc"]},
        {"dday_d1": "2026-06-15", "sentd_d1": "2026-06-01", "apprd_d1": "2026-06-10"},
        {"d1": {"kind": "b10", "day": "2026-06-15", "holidays": []}}, discs=["d1"]),
     ["yes", "yes", "2026-06-01", "no", "no", "yes"]),
    # S10 the same, explanation sent Tue 2 Jun (nine business days) -> may not
    (mk("S10", [("d1", "maydisc"), ("d1", "early")], {"d1": ["r_vendor", "ipblk", "sent", "appr", "apprst", "disc"]},
        {"dday_d1": "2026-06-15", "sentd_d1": "2026-06-02", "apprd_d1": "2026-06-10"},
        {"d1": {"kind": "b10", "day": "2026-06-15", "holidays": []}}, discs=["d1"]), ["no", "no"]),
    # S11 (iv) with the user's permission, approval facts not stated -> OPEN; must obtain approval -> yes
    (mk("S11", [("d1", "maydisc"), ("d1", "needappr")], {"d1": ["r_auth", "uperm"]}, {"dday_d1": "2026-06-15"},
        {"d1": {"kind": "b10", "day": "2026-06-15", "holidays": []}}, discs=["d1"]), ["OPEN", "yes"]),
    # S12 emergency law-enforcement request, threat, disclosed -> may, no approval, no pre-authorization, email now
    (mk("S12", [("d1", "maydisc"), ("d1", "needappr"), ("d1", "nopre"), ("d1", "emailnow"), ("d1", "lat"),
                ("d1", "tolegal"), ("d2", "emailnow"), ("d2", "tolegal")],
        {"d1": ["r_le", "threat", "lereq", "emerg", "disc"], "d2": ["r_le", "threat", "lereq", "emerg"]},
        {"dday_d1": "2026-06-15", "dday_d2": "2026-06-15"},
        {"d1": {"kind": "b10", "day": "2026-06-15", "holidays": []},
         "d2": {"kind": "b10", "day": "2026-06-15", "holidays": []}}, discs=["d1", "d2"]),
     ["yes", "no", "yes", "yes", "none", "no", "yes", "yes"]),
    # S13 an attorney's subpoena: not listed -> may not; directed to legal
    (mk("S13", [("d1", "maydisc"), ("d1", "tolegal")], {"d1": ["subp"]}, {"dday_d1": "2026-06-15"},
        {"d1": {"kind": "b10", "day": "2026-06-15", "holidays": []}}, discs=["d1"]), ["no", "yes"]),
    # S14 existing holder (granted 1 Jan 2025), effective 1 Mar 2026 -> deadline 30 May 2026; CA certified 31 May -> no
    (mk("S14", [("m", "dl"), ("a1", "ok"), ("m", "covered")],
        {"m": ["granted"], "a1": OK_FACTS},
        {"eff_m": "2026-03-01", "gd_m": "2025-01-01", **{k: v for k, v in test("a1")[1].items()}, "csd_a1": "2026-05-31"},
        {"a1": {"kind": "age", "dob": "1990-01-01"}}, tests=["a1"], atdl=["a1"]), ["2026-05-30", "no", "yes"]),
    # S15 extended to 1 Jul 2026 -> deadline 1 Jul, CA on 31 May -> yes; a member granted after the effective day -> OPEN
    (mk("S15", [("m", "dl"), ("a1", "ok")], {"m": ["granted", "ext"], "a1": OK_FACTS},
        {"eff_m": "2026-03-01", "gd_m": "2025-01-01", "extd_m": "2026-07-01", **test("a1")[1], "csd_a1": "2026-05-31"},
        {"a1": {"kind": "age", "dob": "1990-01-01"}}, tests=["a1"], atdl=["a1"]), ["2026-07-01", "yes"]),
    (mk("S15b", [("m", "dl"), ("m", "covered")], {"m": []}, {"eff_m": "2026-03-01", "gd_m": "2026-04-01"}),
     ["OPEN", "no"]),
    # S16 tools, data, uses: revoked CheckUser data must be destroyed, Suppression data not; local policy unless cross-wiki
    (mk("S16", [("dat1", "destroy"), ("dat2", "destroy"), ("u1", "mayuse"), ("u2", "mayuse")],
        {"t1": ["rev"], "u1": ["pol", "cu", "locbad"], "u2": ["pol", "cu", "cross", "locbad"]},
        {"revd_t1": "2026-02-01", "xask_dat1": "2026-03-01", "xask_dat2": "2026-03-01"},
        tools=["t1", "t2"], datas=["dat1", "dat2"], uses=["u1", "u2"], **{"from": [("dat1", "t1"), ("dat2", "t2")]}),
     ["yes", "no", "no", "yes"]),
    # S17 complaints and information
    (mk("S17", [("k1", "ombuds"), ("k2", "ombuds"), ("k2", "commgov"), ("k3", "ombuds"), ("k3", "wmfref"), ("i1", "priv")],
        {"k1": ["infr"], "k2": ["excact"], "k3": ["excact", "ppsec"], "i1": ["subapp"]}, {},
        comps=["k1", "k2", "k3"], infos=["i1"]), ["yes", "OPEN", "yes", "yes", "yes", "yes"]),
    # S18 REVISION 11-25 (R6): the Agreement's six subjects, for the member and for a grant test
    (mk("S18", [("m", "agconf"), ("m", "agwhen"), ("m", "aguse"), ("m", "agdisc"), ("m", "agsafe"), ("m", "agrep"),
                ("a1", "agsafe"), ("a1", "agrep")], {"a1": OK_FACTS}, {**test("a1", "2026-06-01", "2026-06-01")[1]},
        {"a1": {"kind": "age", "dob": "1990-01-01"}}, tests=["a1"]),
     ["yes", "yes", "yes", "yes", "yes", "yes", "yes", "yes"]),
]


def run_one(c, br, mutant=None):
    import ve.environment as VE
    real = E.bridges
    E.bridges = lambda: br
    try:
        got = R.run_case(c, mutant)[0]
    finally:
        E.bridges = real
    return [got[q["qid"]]["answer"] for q in c["questions"]]


def main():
    fails, base = 0, {}
    for (c, br), want in CASES:
        got = run_one(c, br)
        base[c["id"]] = got
        if got != want:
            fails += 1
            print("FAIL", c["id"], "got", got, "want", want)
    print(f"smoke: {len(CASES) - fails}/{len(CASES)} cases as hand-worked")
    killed = {}
    for m in T.MUTANTS:
        killed[m] = any(run_one(c, br, m) != base[c["id"]] for (c, br), _ in CASES)
    print("mutants killed in smoke:", sum(killed.values()), "of", len(killed), {m: v for m, v in killed.items() if not v})
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
