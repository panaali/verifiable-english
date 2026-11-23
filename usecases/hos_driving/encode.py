"""The encoder's pieces and facts for one case (cases.py), with the bridge trail. SAME-FAMILY.

Conventions (stated, the same for every case):
C1 closed world over translation.FACTS: a fact the activity reading (cases.ACTIVITY) does not make true is stated false;
C2 the log is the whole record from its first clock time; the time before it is unknown (no fact about it is stated:
   the translation gives no answer that depends on it);
C3 every number is a duration or position in minutes from bridge/clock.py ONLY (the one tested bridge script): a stated
   duration in minutes (clock.stated_minutes), the duration of a cut piece and the position of each piece end and window
   start (clock.minutes_between from the log's first clock time), and the day-starts of each window (clock.day_starts);
   the encoder never adds or compares durations;
C4 the log is cut at each asked moment and at each window day-start inside it (so each is the end of a piece); a cut
   piece keeps its entry's activity; an uncut piece's duration is the writer's stated duration. A passenger-seat ride is
   two pieces (the translation splits its duration, 395.2 on-duty (4)(iii)); no cut falls inside a ride in this set
   (checked: an error if it would).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "bridge"))

import clock  # noqa: E402
import translation as T  # noqa: E402
from cases import ACTIVITY  # noqa: E402

PIECE_FACTS = [f for f in T.FACTS if f != "every_day"]


class Trail:
    """Every bridge call, recorded (bridge trail in the run file)."""

    def __init__(self):
        self.calls = []

    def __call__(self, fn, *args):
        out = getattr(clock, fn)(*args)
        self.calls.append([fn, list(args), out])
        return out


def encode(case):
    """-> (ctx, facts, meta)."""
    br = Trail()
    log = case["log"]
    origin, last_end = log[0]["start"], log[-1]["end"]
    for a, b in zip(log, log[1:]):
        if a["end"] != b["start"]:
            raise ValueError(f"{case['id']}: gap in the log at {a['end']} / {b['start']}")
    mismatch = []
    for e in log:
        if br("stated_minutes", *e["stated"]) != br("minutes_between", e["start"], e["end"]):
            mismatch.append(e["start"])
    # moments and the windows each needs (Q1: the carrier's (b) limb; Q3: the limb the question names)
    moments, asks, need = {}, {}, {}
    for qn in case["questions"]:
        mo = qn["moment"]
        moments.setdefault(mo, f"t{len(moments) + 1}")
        asks.setdefault(moments[mo], set()).add(qn["form"])
        if qn["form"] == "q1":
            need.setdefault(mo, set()).add(8 if case["every_day"] else 7)
        if qn["form"] == "q3":
            need.setdefault(mo, set()).add(qn["n"])
    window_starts = {}
    for mo, ns in need.items():
        for n in sorted(ns):
            window_starts[(mo, n)] = br("day_starts", mo, case["designated"], n)
    cuts = set(moments)
    for lst in window_starts.values():
        cuts.update(w for w in lst if origin < w < last_end)
    # pieces
    pieces, info, ride = [], {}, {}
    for i, e in enumerate(log):
        inner = sorted(t for t in cuts if e["start"] < t < e["end"])
        facts = set(ACTIVITY[e["activity"]])
        if "ride_passenger" in facts:
            if inner:
                raise ValueError(f"{case['id']}: a cut inside a passenger-seat ride")
            eid = f"r{i}"
            a, b = f"p{i}a", f"p{i}b"
            ride[eid] = (a, b)
            pieces += [a, b]
            info[eid] = {"dur": br("stated_minutes", *e["stated"])}
            info[a] = {"facts": facts, "end": None, "entry": i}
            info[b] = {"facts": facts, "end": e["end"], "entry": i}
            continue
        bounds = [e["start"]] + inner + [e["end"]]
        for j, (s, t) in enumerate(zip(bounds, bounds[1:])):
            x = f"p{i}" if not inner else f"p{i}_{j}"
            pieces.append(x)
            dur = br("stated_minutes", *e["stated"]) if not inner else br("minutes_between", s, t)
            info[x] = {"facts": facts, "end": t, "dur": dur, "entry": i, "cut": bool(inner)}
    end_index = {info[x]["end"]: n for n, x in enumerate(pieces) if info[x]["end"] is not None}
    mo_index = {}
    for mo, mid in moments.items():
        if mo not in end_index:
            mo_index[mid] = None            # the moment is the log's first clock time or outside the log
        else:
            mo_index[mid] = end_index[mo]
    windows = {}
    win_pos = {}
    for (mo, n), lst in window_starts.items():
        mid = moments[mo]
        out = []
        for i, w in enumerate(lst):
            wid = f"{mid}w{n}d{i}"
            pos = br("minutes_between", origin, w)
            win_pos[wid] = pos
            if pos < 0:
                out.append((wid, None, False))
            elif pos == 0:
                out.append((wid, None, True))
            else:
                out.append((wid, end_index[w], True))
        windows.setdefault(mid, {})[n] = out
    sleeper = [x for x in pieces if "rest_sleeper" in info[x]["facts"]]
    live = {mid: j for mid, j in mo_index.items() if j is not None}
    ctx = T.Ctx(pieces, ride=ride, sleeper=sleeper, moments=live,
                windows={mid: w for mid, w in windows.items() if mid in live}, asks=asks,
                every_day=case["every_day"])
    facts = [{"id": "car.every_day", "formula": T.U("every_day", ctx.carrier) if case["every_day"]
              else ["not", T.U("every_day", ctx.carrier)]}]
    for x in pieces:
        for p in PIECE_FACTS:
            f = T.U(p, x)
            facts.append({"id": f"{x}.{p}", "formula": f if p in info[x]["facts"] else ["not", f]})
        if "dur" in info[x]:
            facts.append({"id": f"dur_{x}", "formula": ["eq", T.k("dur", x), T.m(info[x]["dur"])]})
        if info[x]["end"] is not None:
            facts.append({"id": f"tend_{x}", "formula": ["eq", T.k("tend", x),
                                                         T.m(br("minutes_between", origin, info[x]["end"]))]})
    for eid in ride:
        facts.append({"id": f"dur_{eid}", "formula": ["eq", T.k("dur", eid), T.m(info[eid]["dur"])]})
    for wid, pos in win_pos.items():
        facts.append({"id": f"pos_{wid}", "formula": ["eq", T.k("pos", wid), T.m(pos)]})
    qmap = {qn["qid"]: {"form": qn["form"], "n": qn["n"], "moment": moments[qn["moment"]],
                        "live": mo_index[moments[qn["moment"]]] is not None} for qn in case["questions"]}
    meta = {"pieces": len(pieces), "cut_pieces": sum(1 for x in pieces if info[x].get("cut")),
            "stated_vs_clock_mismatch": mismatch, "bridge": br.calls, "questions": qmap,
            "activities": sorted({e["activity"] for e in log}), "readings": ctx.readings}
    return ctx, facts, meta
