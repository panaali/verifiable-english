"""Smoke test on MADE-UP cases (not from the question file), written with the translation: the staged route (Python prover,
no Lean) must give the hand-worked answers below and refuse (OPEN) where readings R1 / R4 refuse. SAME-FAMILY.
usage (repository root): .venv/bin/python -B usecases/totting_up/smoke_test.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "bridge"))
import encode as E  # noqa: E402
import totting_bridge as TB  # noqa: E402
import run as R  # noqa: E402

DE = ["disc", "oend"]  # discretionary disqualification + obligatory endorsement


def mk(cid, conv, lo, pts, offences, prevs=(), circs=(), vfacts=(), unknown=None, qs=(), tot_stated=()):
    """offences: [(o, facts)]; prevs: [(p, imp, {base ints}, facts)]; circs: [(c, occ or None, facts)]."""
    facts, ints = {"v1": list(vfacts)}, {"conv_v1": conv, "lo_v1": lo, "pts_v1": pts}
    for o, fl in offences:
        facts[o] = list(fl)
    for p, imp, base, fl in prevs:
        facts[p] = ["prior"] + list(fl)
        ints[f"imp_{p}"] = imp
        ints.update({f"{k}_{p}": v for k, v in base.items()})
    for c, occ, fl in circs:
        facts[c] = list(fl)
        if occ:
            ints[f"occ_{c}"] = occ
    case = {"id": cid, "convictions": ["v1"], "offences": {o: "v1" for o, _ in offences},
            "prevs": {p[0]: "v1" for p in prevs}, "circs": {c[0]: "v1" for c in circs}, "facts": facts,
            "unknown": unknown or {}, "ints": ints, "tot_stated": list(tot_stated),
            "questions": [{"qid": f"{cid}-{i}", "form": f, "args": a} for i, (f, a) in enumerate(qs, 1)]}
    br = {(cid, r["item"], r["conv"]): TB.row(r) for r in E.bridge_inputs(case)}
    return case, br


Q12 = [("must", ["v1"]), ("minimum", ["v1"])]
D60 = {"based": 60, "extd": 0}
CASES = [
    # S1 12 points, no previous disqualification, not satisfied: must, 6 months
    (mk("S1", "2026-03-10", "2025-11-02", 12, [("o1", DE)], qs=Q12), ["yes", "6 months"]),
    # S2 11 points: (1)(b) fails: no, none
    (mk("S2", "2026-03-10", "2025-11-02", 11, [("o1", DE)], qs=Q12), ["no", "none"]),
    # S3 two previous fixed disqualifications of 60 days and 6 months within three years: 2 years; Q3 both yes
    (mk("S3", "2026-03-10", "2025-11-02", 13, [("o1", DE)],
        prevs=[("p1", "2024-01-15", D60, ["fixed", "in_days"]), ("p2", "2023-06-01", {"basem": 6}, ["fixed", "in_months"])],
        qs=Q12 + [("counts", ["p1", "v1"]), ("counts", ["p2", "v1"])]), ["yes", "2 years", "yes", "yes"]),
    # S4 one of 55 days (no), one under s.26 (5: no), one imposed four years before (no), one of 56 days (yes): 1 year
    (mk("S4", "2026-03-10", "2025-11-02", 12, [("o1", DE)],
        prevs=[("p1", "2024-01-15", {"based": 55, "extd": 0}, ["fixed", "in_days"]),
               ("p2", "2024-02-15", D60, ["fixed", "in_days", "u_s26"]),
               ("p3", "2021-10-01", D60, ["fixed", "in_days"]),
               ("p4", "2025-01-01", {"based": 56, "extd": 0}, ["fixed", "in_days"])],
        qs=Q12 + [("counts", [p, "v1"]) for p in ("p1", "p2", "p3", "p4")]), ["yes", "1 year", "no", "no", "no", "yes"]),
    # S5 (2A): 40 days + 30 days' extension under s.35A (no); 40 + 30 under another section (yes); 70 stated total with a
    # 20-day extension under s.166 (base 50: no): 1 year
    (mk("S5", "2026-03-10", "2025-11-02", 12, [("o1", DE)],
        prevs=[("p1", "2024-01-15", {"based": 40, "extd": 30}, ["fixed", "in_days", "ext", "ext_35a"]),
               ("p2", "2024-02-15", {"based": 40, "extd": 30}, ["fixed", "in_days", "ext"]),
               ("p3", "2024-03-15", {"totd": 70, "extd": 20}, ["fixed", "in_days", "ext", "ext_166"])],
        tot_stated=["p3"], qs=Q12 + [("counts", [p, "v1"]) for p in ("p1", "p2", "p3")]),
     ["yes", "1 year", "no", "yes", "no"]),
    # S6 (5A): aiding an obligatory offence, obligatory endorsement, s.34 order made: treated as discretionary: (1) applies
    (mk("S6", "2026-03-10", "2025-11-02", 12, [("o1", ["oblig", "oend", "s34", "aid", "aid_oblig"])], qs=Q12),
     ["yes", "6 months"]),
    # S7 obligatory offence with a s.34 order (not aided): (1A)(b) fails: no, none
    (mk("S7", "2026-03-10", "2025-11-02", 14, [("o1", ["oblig", "oend", "s34"])], qs=Q12), ["no", "none"]),
    # S8 satisfied court: must no; Q4: ordinary hardship no, exceptional yes, taken within 3 years no, taken 4 years ago yes
    (mk("S8", "2026-03-10", "2025-11-02", 12, [("o1", DE)], vfacts=["satisfied"],
        circs=[("c1", None, ["hardship"]), ("c2", None, ["hardship", "exceptional"]),
               ("c3", "2024-05-01", ["taken"]), ("c4", "2022-01-01", ["taken"]), ("c5", None, ["nserious"])],
        qs=Q12 + [("may", [c, "v1"]) for c in ("c1", "c2", "c3", "c4", "c5")]),
     ["no", "6 months", "no", "yes", "no", "yes", "no"]),
    # S9 refusals: satisfied but declines (R1), satisfaction resting on ordinary hardship (R1), anniversary date (R4)
    (mk("S9", "2026-03-10", "2024-05-01", 12, [("o1", DE)], vfacts=["satisfied", "declines"],
        prevs=[("p1", "2021-05-01", D60, ["fixed", "in_days"])], qs=Q12 + [("counts", ["p1", "v1"])]),
     ["OPEN", "OPEN", "OPEN"]),
    (mk("S10", "2026-03-10", "2025-11-02", 12, [("o1", DE)], vfacts=["satisfied"],
        circs=[("c1", None, ["hardship", "rests"])], qs=Q12 + [("may", ["c1", "v1"])]), ["OPEN", "6 months", "no"]),
    # S11 (5) attempt to steal a vehicle; not fixed (until test passed); imposed after the latest offence: none counts
    (mk("S11", "2026-03-10", "2025-11-02", 12, [("o1", DE)],
        prevs=[("p1", "2024-01-15", D60, ["fixed", "in_days", "attempt", "o_steal"]),
               ("p2", "2024-01-15", {}, []),
               ("p3", "2025-12-01", D60, ["fixed", "in_days"])],
        qs=Q12 + [("counts", [p, "v1"]) for p in ("p1", "p2", "p3")]), ["yes", "6 months", "no", "no", "no"]),
    # S12 unknown endorsement on an aided obligatory offence: (1A)(a) undecided: OPEN
    (mk("S12", "2026-03-10", "2025-11-02", 12, [("o1", ["oblig", "s34", "aid", "aid_oblig"])], unknown={"o1": ["oend"]},
        qs=Q12), ["OPEN", "OPEN"]),
]


def main():
    bad = 0
    for (case, br), want in CASES:
        import translation as T
        orig = E.bridges
        E.bridges = lambda br=br: br
        try:
            answers = R.run_case(case)[0]
        finally:
            E.bridges = orig
        got = [answers[q["qid"]]["answer"] for q in case["questions"]]
        ok = got == want
        bad += not ok
        print(("ok  " if ok else "FAIL"), case["id"], got, "" if ok else f"want {want}")
    print(f"{len(CASES) - bad}/{len(CASES)} made-up cases")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
