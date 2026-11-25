"""Smoke test on MADE-UP cases (not from the question file), written with the translation: the staged route (Python prover,
no Lean) must give the hand-worked answers below, refuse where a reading refuses, and every planted error must change one.
CROSS-FAMILY set, Opus translator.  usage (repository root): .venv/bin/python -B usecases/hipaa_breach_notice/smoke_test.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as R  # noqa: E402
import translation as T  # noqa: E402

BASE = ["phi", "notperm", "acq"]


def mk(cid, qs, facts=None, days=None, cnts=None, states=None, **items):
    names = {}
    st = {}
    for n, (name, res) in enumerate(states or [], 1):
        st[f"s{n}"] = "i"
        names[f"s{n}"] = name
        cnts = {**(cnts or {}), f"res_s{n}": res}
    f = {"i": list(BASE)}
    for x, v in (facts or {}).items():
        f[x] = f.get(x, []) + list(v)
    return {"id": cid, "incs": ["i"], "states": st, "names": names, "facts": f, "days": days or {}, "cnts": cnts or {},
            **items, "questions": [{"qid": f"{cid}-{n}", "item": x, "form": fm} for n, (x, fm) in enumerate(qs, 1)]}


CASES = [
    # S1 412 Ohio + 95 Indiana = 507 individuals; discovery 3 Mar 2027: individuals and Secretary, no media; 2 May 2027
    (mk("S1", [("i", "bun"), ("i", "who_ce"), ("i", "li"), ("i", "ls"), ("i", "lm"), ("i", "logreq"), ("i", "plain")],
        days={"disc_i": "2027-03-03"}, states=[("Ohio", 412), ("Indiana", 95)]),
     ["yes", "individuals; Secretary", "2027-05-02", "2027-05-02", "none", "no", "yes"]),
    # S2 501 Texas residents; discovery 31 Dec 2027: media too; 60 days -> 29 Feb 2028 (leap year)
    (mk("S2", [("i", "who_ce"), ("i", "lm"), ("i", "big")], days={"disc_i": "2027-12-31"}, states=[("Texas", 501)]),
     ["individuals; media: Texas; Secretary", "2028-02-29", "yes"]),
    # S3 500 Texas residents: no media (not more than 500), Secretary contemporaneous (500 or more); stated individual day
    (mk("S3", [("i", "who_ce"), ("i", "ls")], days={"disc_i": "2027-06-01", "isd_i": "2027-06-20"},
        states=[("Texas", 500)]), ["individuals; Secretary", "2027-06-20"]),
    # S4 300 + 199 = 499: small; discovered 10 Jun 2027 -> 31 Dec 2027 + 60 = 29 Feb 2028; the log
    (mk("S4", [("i", "ls"), ("i", "logreq"), ("i", "big")], days={"disc_i": "2027-06-10"},
        states=[("Utah", 300), ("Idaho", 199)]), ["2028-02-29", "yes", "no"]),
    # S5 the risk assessment demonstrates a low probability: not a breach
    (mk("S5", [("i", "bun"), ("i", "who_ce"), ("i", "li")], facts={"i": ["lowprob"]}, days={"disc_i": "2027-03-03"},
        states=[("Ohio", 20)]), ["no", "none", "none"]),
    # S6 exclusion (i) fails on further impermissible disclosure -> breach; without it -> excluded
    (mk("S6", [("i", "bun")], facts={"i": ["wf", "unint", "gfs", "further"]}, days={"disc_i": "2027-03-03"},
        states=[("Ohio", 2)]), ["yes"]),
    (mk("S6b", [("i", "bun")], facts={"i": ["wf", "unint", "gfs"]}, days={"disc_i": "2027-03-03"},
        states=[("Ohio", 2)]), ["no"]),
    # S7 encrypted by a guidance method: not unsecured
    (mk("S7", [("i", "bun")], facts={"i": ["guid"]}, days={"disc_i": "2027-03-03"}, states=[("Ohio", 2)]), ["no"]),
    # S8 discovery by knowledge: the committer knew 5 Jan, a workforce member 20 Jan, reasonable diligence 15 Jan -> 15 Jan
    (mk("S8", [("i", "li")], facts={"k1": ["kce", "kcom"], "k2": ["kce"]},
        days={"kd_k1": "2027-01-05", "kd_k2": "2027-01-20", "dd_i": "2027-01-15"},
        states=[("Ohio", 2)], knows={"k1": ["ce", "i"], "k2": ["ce", "i"]}), ["2027-03-16"]),
    # S9 oral statement 1 Apr 2027 (criminal investigation), no written one: 1 May; documented; li refused (delayed)
    (mk("S9", [("o", "dly"), ("o", "docreq"), ("i", "li"), ("o", "dlyapp")], facts={"o": ["purp", "oral", "ab_ind"]},
        days={"disc_i": "2027-03-20", "od_o": "2027-04-01"}, states=[("Ohio", 2)], stmts={"o": "i"}),
     ["2027-05-01", "yes", "OPEN", "yes"]),
    # S10 oral then written within 30 days with a period to 1 Jul: 1 Jul; written after 30 days: refused (R6)
    (mk("S10", [("o", "dly")], facts={"o": ["purp", "oral", "fw", "fwper", "ab_ind"]},
        days={"disc_i": "2027-03-20", "od_o": "2027-04-01", "fwd_o": "2027-04-20", "fwend_o": "2027-07-01"},
        states=[("Ohio", 2)], stmts={"o": "i"}), ["2027-07-01"]),
    (mk("S10b", [("o", "dly")], facts={"o": ["purp", "oral", "fw", "fwper", "ab_ind"]},
        days={"disc_i": "2027-03-20", "od_o": "2027-04-01", "fwd_o": "2027-05-10", "fwend_o": "2027-07-01"},
        states=[("Ohio", 2)], stmts={"o": "i"}), ["OPEN"]),
    # S11 a written statement with no period: no delay; the notice's own day stands; oral, no qualifying purpose: no duty
    (mk("S11", [("o", "dlyapp"), ("i", "li"), ("o", "dly")], facts={"o": ["purp", "wr", "ab_ind"]},
        days={"disc_i": "2027-03-20", "od_o": "2027-04-01"}, states=[("Ohio", 2)], stmts={"o": "i"}),
     ["no", "2027-05-19", "OPEN"]),
    (mk("S11b", [("o", "docreq"), ("o", "dlyapp"), ("i", "li")], facts={"o": ["oral", "ab_ind"]},
        days={"disc_i": "2027-03-20", "od_o": "2027-04-01"}, states=[("Ohio", 2)], stmts={"o": "i"}),
     ["no", "no", "2027-05-19"]),
    # S12 the business associate: its employee learned 1 Feb 2027 -> covered entity, 2 Apr 2027
    (mk("S12", [("b", "who_ba"), ("b", "lb"), ("b", "binforeq")], facts={"b": ["bknow"], "k1": ["kba"]},
        days={"disc_i": "2027-02-10", "kd_k1": "2027-02-01"}, states=[("Ohio", 2)], bas={"b": "i"},
        knows={"k1": ["ba", "i"]}), ["covered entity", "2027-04-02", "yes"]),
    # S13 substitute notice: 10 individuals -> posting or media, toll-free; a 60-day posting falls short; 9 -> alternative
    (mk("S13", [("i", "wmreq"), ("i", "altok"), ("i", "tfreq"), ("i", "postok")], days={"disc_i": "2027-02-10"},
        cnts={"nins_i": 10, "pdays_i": 60}, states=[("Ohio", 40)]), ["yes", "no", "yes", "no"]),
    (mk("S13b", [("i", "altok"), ("i", "wmreq")], days={"disc_i": "2027-02-10"}, cnts={"nins_i": 9},
        states=[("Ohio", 40)]), ["yes", "no"]),
    # S14 individuals: e-mail agreed then withdrawn; deceased with the next of kin's address; next of kin unreachable
    (mk("S14", [("g1", "emailok"), ("g2", "nokreq"), ("g3", "substreq"), ("g4", "emailok")],
        facts={"g1": ["agr", "wdr"], "g2": ["dec", "nokad"], "g3": ["dec", "nokins"], "g4": ["agr"]},
        days={"disc_i": "2027-02-10"}, states=[("Ohio", 4)], groups={"g1": "i", "g2": "i", "g3": "i", "g4": "i"}),
     ["no", "yes", "no", "yes"]),
]


def main():
    bad = 0
    base = {}
    for case, want in CASES:
        got, _, _, _, _, _ = R.run_case(case)
        for qn, w in zip(case["questions"], want):
            g = got[qn["qid"]]["answer"]
            base[qn["qid"]] = got[qn["qid"]]
            if g != w:
                bad += 1
                print("FAIL", qn["qid"], qn["form"], "got", g, "want", w)
    print(f"smoke: {sum(len(w) for _, w in CASES) - bad}/{sum(len(w) for _, w in CASES)}")
    killed = 0
    for m, (desc, _) in T.MUTANTS.items():
        ch = []
        for case, _ in CASES:
            got = R.run_case(case, m)[0]
            ch += [q for q in got if got[q] != base[q]]
        killed += bool(ch)
        print(m, "killed" if ch else "SURVIVED", ch[:4], desc)
    print(f"mutants killed {killed}/{len(T.MUTANTS)}")
    return 1 if bad or killed < len(T.MUTANTS) else 0


if __name__ == "__main__":
    sys.exit(main())
