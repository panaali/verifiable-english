"""DEVELOPMENT CHECK ONLY, never an answer source: an independent minute-by-minute reading of the same rules
(translation.py's readings T1-T5, ISOLATION.md), written as segments over a minute timeline instead of the chain, to
catch grounding mistakes. Compares with a run file's staged answers. Not Lean-checked; not counted anywhere.

usage: .venv/bin/python -B usecases/hos_driving/dev_reference.py RUN.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "bridge"))
import cases as K  # noqa: E402
import clock  # noqa: E402

LIMBS_ON = {"inspecting", "loading", "disabled", "testing", "carrier_work", "paid_other", "at_controls"}


def timeline(case):
    log = case["log"]
    origin = log[0]["start"]
    mins = []  # per minute: dict(drive, on, sb)
    entries = []
    for e in log:
        f = set(K.ACTIVITY[e["activity"]])
        n = clock.minutes_between(e["start"], e["end"])
        entries.append((len(mins), n, f))
        for _ in range(n):
            mins.append({"drive": "at_controls" in f, "sb": "rest_sleeper" in f, "f": f, "ride": "ride_passenger" in f})
    # on-duty per minute (rides first without exclusion)
    for mm in mins:
        f = mm["f"]
        limb4 = "in_on_cmv" in f and "rest_parked" not in f and "rest_sleeper" not in f
        limb1 = "wait_dispatch" in f and "relieved" not in f
        mm["on"] = bool(f & LIMBS_ON) or limb4 or limb1
    # (4)(iii): ride minutes next to >= 7 h of sleeper berth
    for (s, n, f) in entries:
        if "ride_passenger" not in f:
            continue
        j = s - 1
        run = 0
        while j >= 0 and mins[j]["sb"]:
            run += 1
            j -= 1
        aft = run >= 420
        j = s + n
        run = 0
        while j < len(mins) and mins[j]["sb"]:
            run += 1
            j += 1
        bef = run >= 420
        if aft and bef:
            for i in range(s, s + n):
                mins[i]["on"] = None
        elif aft:
            for i in range(s, s + min(n, 180)):
                mins[i]["on"] = False
        elif bef:
            for i in range(s + n - min(n, 180), s + n):
                mins[i]["on"] = False
    return origin, mins


def off(mm, r):
    if mm["on"] is None:
        return None
    return (not mm["on"]) and (r == "b" or not mm["sb"])


def runs(flags, t):
    """maximal runs of True in flags[0:t] -> [(begin, end)]"""
    out, b = [], None
    for i in range(t):
        if flags[i] and b is None:
            b = i
        if not flags[i] and b is not None:
            out.append((b, i))
            b = None
    if b is not None:
        out.append((b, t))
    return out


def answer(case, q, r):
    origin, mins = timeline(case)
    t = clock.minutes_between(origin, q["moment"])
    offs = [off(mm, r) for mm in mins]
    if any(o is None for o in offs[:t]):
        return None
    ten = [rr for rr in runs(offs, t) if rr[1] - rr[0] >= 600]
    nd = [not mm["drive"] for mm in mins]
    thirty = [rr for rr in runs(nd, t) if rr[1] - rr[0] >= 30]
    if q["form"] in ("q1", "q2"):
        if not ten or not thirty:
            return None
        e = ten[-1][1]
        E = t - e
        D = sum(1 for i in range(e, t) if mins[i]["drive"])
        X = sum(1 for i in range(thirty[-1][1], t) if mins[i]["drive"])
        rem = max(0, min(840 - E, 660 - D, 480 - X))
        if q["form"] == "q2":
            return rem
    n = q["n"] if q["form"] == "q3" else (8 if case["every_day"] else 7)
    lim = 3600 if n == 7 else 4200
    starts = clock.day_starts(q["moment"], case["designated"], n)
    rest = [rr for rr in runs(offs, t) if rr[1] - rr[0] >= 2040]
    b = rest[-1][0] if rest else None
    reach, unknown = False, False
    for w in starts:
        p = clock.minutes_between(origin, w)
        active = b is None or b < p
        if not active:
            continue
        cnt = sum(1 for i in range(max(p, 0), t) if mins[i]["on"])
        if p < 0 and cnt < lim:
            unknown = True
        if cnt >= lim:
            reach = True
    if not reach and unknown:
        return None
    if q["form"] == "q1":
        return "yes" if rem > 0 and not reach else "no"
    # q3 guard: inside an off-duty run that the log continues to >= 34 h
    if reach and t > 0 and offs[t - 1]:
        j = t - 1
        while j >= 0 and offs[j]:
            j -= 1
        k = t
        while k < len(offs) and offs[k]:
            k += 1
        if t - (j + 1) < 2040 and (k - (j + 1) >= 2040 or k == len(offs)):
            return "REFUSED"
    return "yes" if reach else "no"


def main(path):
    run = json.load(open(path, encoding="utf-8"))
    staged = {qid: a for rec in run["records"] for qid, a in rec.get("staged", rec["answers"]).items()}
    diff = 0
    for c in K.CASES:
        rs = "ab" if any("rest_sleeper" in K.ACTIVITY[e["activity"]] for e in c["log"]) else "a"
        for q in c["questions"]:
            vals = [answer(c, q, r) for r in rs]
            ref = None if None in vals else ("REFUSED" if len(set(map(str, vals))) > 1 else vals[0])
            a = staged[q["qid"]]
            ve = a.get("minutes", a["answer"]) if a["answer"] == "DURATION" else a["answer"]
            ve = None if ve == "OPEN" else ve
            if str(ref) != str(ve):
                diff += 1
                print("DIFF", q["qid"], "ref", ref, "ve", ve)
    print("differences", diff)


if __name__ == "__main__":
    main(sys.argv[1])
