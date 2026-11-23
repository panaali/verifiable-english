"""Hours of service, property-carrying drivers, 49 CFR 395.3 + 395.2 (statute corpus batch 3, law 2): the VE translation,
one pass with today's language. SAME-FAMILY (Opus writer, Opus translator/encoder).

Row statute-corpus-hos-driving (dri-statute-corpus-hos-driving-1123, Opus 5.5). Written from the pinned source only
(manage-agents reviews/spare/statute-corpus/stock/hos-driving/source.txt, sha256 97a3a6b4...14cc042). Evidence branch:
nothing here is a Lean kernel line, a profile, a refuses pair or a lint change; nothing merges.

UNITS maps each in-scope unit n of stock/hos-driving/units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).

THE LOG AS A CHAIN. A case's duty log is a list of PIECES in time order (encode.py: the writer's log entries, cut at each
asked moment and each window start by the bridge script; a cut piece's duration comes from the bridge, an uncut piece's is
the writer's stated duration). For each piece x the translation defines, after x (minutes, unit "minute"):
  on(x)       x is on-duty time (395.2 "On-duty time", limbs (1)-(9) with the (4)(i)-(iii) exclusions);
  rof<r>_x    the length of the run of consecutive off-duty time ending with x (0 if x is not off duty);
  els<r>_x    the time since coming on duty following 10 consecutive hours off duty (395.3(a)(2)); undefined until the log
              shows such 10 hours (the time before the log's first clock time is unknown: no answer depends on it);
  drv<r>_x    the driving time during that period (395.3(a)(3)(i));
  ndr_x       the length of the run of consecutive time not in driving status ending with x (395.3(a)(3)(ii): off-duty,
              sleeper berth or on-duty not driving time, alone or combined);
  dsb_x       the driving time since the last consecutive 30-minute interruption of driving status;
  ond_x       the on-duty time from the log's first clock time to the end of x (a SUM of stated durations, Lean-checked);
  rst<r>(x)   an off-duty period of 34 or more consecutive hours has been completed by the end of x (395.3(c));
  lrb<r>_x    the position (minutes from the log's first clock time) of the beginning of the last such period.
Every sum and every comparison with a limit (10, 14, 11, 8 hours, 30 minutes, 60 / 70 hours, 34 hours, 7 hours, 3 hours)
is a rule below; the bridge only turns pairs of clock times into durations and lists the starts of the 7 or 8 days.

TWO READINGS OF "OFF DUTY" (ISOLATION.md D1: where the text gives two outcomes at once, derive none). 395.2 defines
on-duty time and takes "time spent resting in a sleeper berth" out of it ((4)(ii)); 395.3(a)(3)(ii) lists "off-duty,
sleeper berth or on-duty not driving time" as three kinds; 395.3(a)(1), (a)(2) and (c) count "off duty" / "off-duty"
hours only, and the sleeper-berth provisions that would combine them are in 395.1 (out of scope). Reading A: off duty =
neither on-duty time nor sleeper-berth time. Reading B: off duty = not on-duty time. Both are grounded for a case whose
log has sleeper-berth time (for any other case the two readings are the same formulas); an answer is given only where
both readings give it; where they differ the question is REFUSED.

A MOMENT ASKED (end of piece k). Q1 may drive: els < 14 h, drv < 11 h, dsb < 8 h (each limit reached = may not
drive: the next minute of driving would break it) and the 395.3(b) limit for the carrier is not reached. Q2 driving
left before a limit of 395.3(a): the least of 14 h - els, 11 h - drv, 8 h - dsb, or 0. Q3 60 h / 7 days or 70 h / 8 days:
the on-duty time in some period of 7 (8) consecutive days that begins at the carrier's designated time on one of the 7
(8) days up to the moment (so contains it) and has not ended with the beginning of a 34-hour off-duty period completed
by the moment, is at least 60 (70) hours. A period that began before the log's first clock time counts only as a lower
bound (the on-duty time before the log is unknown). Q3 at a moment inside an off-duty run that the log continues past
34 hours (the period could be read as ended by a 34-hour period not yet completed at the moment) is answered only when
the answer does not turn on that.
"""
from __future__ import annotations

import hashlib
import json

MIN = "minute"
# 395.3 limits, minutes (the text's literals x 60; 30 minutes as given)
OFF10, PER14, DRIVE11, DRIVE8, BREAK30 = 600, 840, 660, 480, 30
LIM = {7: 3600, 8: 4200}          # (b)(1) 60 hours in 7 consecutive days; (b)(2) 70 hours in 8 consecutive days
RESTART34 = 2040                   # (c) 34 or more consecutive hours
SB7, RIDE3 = 420, 180              # 395.2 on-duty (4)(iii): at least 7 consecutive hours in the sleeper berth; up to 3 hours

FACTS = {  # unary facts of a piece (the encoder states each true or false from the log's named activity)
    "at_controls": "the time is spent at the driving controls of a commercial motor vehicle in operation",
    "head_work": "the driver has begun to work or is required to be in readiness to work and has not been relieved "
                 "from work and all responsibility for performing work (on-duty time, head)",
    "wait_dispatch": "the driver is at a plant, terminal, facility or other property of a motor carrier or shipper, "
                     "or on public property, waiting to be dispatched",
    "relieved": "the driver has been relieved from duty by the motor carrier",
    "inspecting": "the driver is inspecting, servicing or conditioning a commercial motor vehicle",
    "in_on_cmv": "the driver is in or on a commercial motor vehicle",
    "rest_parked": "the driver is resting in or on a parked vehicle",
    "rest_sleeper": "the driver is resting in a sleeper berth",
    "ride_passenger": "the driver is riding in the passenger seat of a property-carrying vehicle moving on the highway",
    "loading": "the driver is loading or unloading a commercial motor vehicle, supervising or assisting in it, "
               "attending a commercial motor vehicle being loaded or unloaded, remaining in readiness to operate it, "
               "or giving or receiving receipts for shipments loaded or unloaded",
    "disabled": "the driver is repairing, obtaining assistance or remaining in attendance upon a disabled commercial "
                "motor vehicle",
    "testing": "the driver is providing a breath sample or urine specimen (including travel to and from the "
               "collection site) to comply with testing required by part 382 when directed by a motor carrier",
    "carrier_work": "the driver is performing other work in the capacity, employ or service of a motor carrier",
    "paid_other": "the driver is performing compensated work for a person who is not a motor carrier",
    "every_day": "(the carrier item) the employing motor carrier operates commercial motor vehicles every day of the week",
}
DERIVED_UNARY = {
    "on": "the piece is on-duty time (395.2)",
    "aft": "the ride is immediately after a period of at least 7 consecutive hours in the sleeper berth",
    "bef": "the ride is immediately before a period of at least 7 consecutive hours in the sleeper berth",
    "excl": "the piece is riding time excluded from on-duty time by 395.2 on-duty (4)(iii)",
    "rsta": "an off-duty period of 34 or more consecutive hours has been completed by the end of the piece (reading A)",
    "rstb": "an off-duty period of 34 or more consecutive hours has been completed by the end of the piece (reading B)",
    "maya": "at the moment the driver may drive (395.3(a) and (b); reading A)",
    "mayb": "at the moment the driver may drive (395.3(a) and (b); reading B)",
    **{f"rch{n}{r}": f"at the moment the driver has been on duty {LIM[n] // 60} hours in a period of {n} consecutive days "
                     f"(395.3(b), (c); reading {r.upper()})" for n in (7, 8) for r in "ab"},
    **{f"fut{r}": f"the moment is inside an off-duty run that the log continues to 34 hours or more (reading {r.upper()})"
       for r in "ab"},
}
INT_UNITS = {  # per-item integer constants, unit minute: base -> words
    "dur": "the duration of the piece (stated by the writer, or from the bridge for a cut piece)",
    "tend": "the position of the end of the piece (minutes from the log's first clock time; bridge)",
    "pos": "the position of a window start (minutes from the log's first clock time; bridge; negative = before the log)",
    "len": "the duration of a part of a passenger-seat ride (395.2 on-duty (4)(iii))",
    "xrd": "the minutes of a passenger-seat ride excluded from on-duty time (395.2 on-duty (4)(iii))",
    "sbf": "the sleeper-berth run ending with the piece", "sbb": "the sleeper-berth run beginning with the piece",
    "ndr": "the run of time not in driving status ending with the piece",
    "dsb": "the driving time since the last 30-minute interruption of driving status",
    "ond": "the on-duty time from the log's first clock time to the end of the piece",
    **{f"rof{r}": f"the off-duty run ending with the piece (reading {r.upper()})" for r in "ab"},
    **{f"els{r}": f"the time since coming on duty following 10 consecutive hours off duty (reading {r.upper()})"
       for r in "ab"},
    **{f"drv{r}": f"the driving time in the 14-hour period (reading {r.upper()})" for r in "ab"},
    **{f"lrb{r}": f"the position of the beginning of the last completed 34-hour off-duty period (reading {r.upper()})"
       for r in "ab"},
    **{f"rbk{r}": f"the off-duty run from the piece onward to the end of that run (reading {r.upper()})" for r in "ab"},
    **{f"rem{r}": f"the driving time left before a limit of 395.3(a) (reading {r.upper()})" for r in "ab"},
}
STEP_BASES = tuple(b for b in INT_UNITS if b not in ("dur", "tend", "pos"))


# --- formula helpers (ve-quantity@1 wire shapes) ------------------------------------------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def m(v): return ["decimal", MIN, str(v)]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def add(a, b): return ["add", MIN, a, b]
TRUE, FALSE = ["top"], ["bottom"]


def And(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return TRUE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return FALSE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


def k(base, x):
    return ["const", MIN, f"{base}_{x}"]


# --- the case context ------------------------------------------------------------------------------------------

class Ctx:
    """pieces: ordered piece ids; ride: {entry id: (a-piece, b-piece)} for passenger-seat rides (both pieces carry the
    ride's facts; the translation splits the ride's duration between them); sleeper: piece ids with rest_sleeper (from
    the facts; decides only whether reading B is grounded and where the sleeper runs are); moments: {moment id: end
    piece index}; windows: {moment id: {n: [(window item, end piece index or None (= at the log's first clock time),
    known: position >= 0)]}}; carrier: the carrier item; asks: {moment id: set of forms asked}."""

    def __init__(self, pieces, ride=None, sleeper=(), moments=None, windows=None, carrier="car", asks=None,
                 every_day=True):
        self.pieces = list(pieces)
        self.ride = dict(ride or {})
        self.sleeper = set(sleeper)
        self.moments = dict(moments or {})
        self.windows = dict(windows or {})
        self.carrier = carrier
        self.asks = dict(asks or {})
        self.every_day = every_day
        self.readings = "ab" if self.sleeper else "a"
        self.ride_part = {}
        for e, (a, b) in self.ride.items():
            self.ride_part[a] = (e, "a")
            self.ride_part[b] = (e, "b")

    @property
    def items(self):
        ws = [w for per in self.windows.values() for lst in per.values() for (w, _, _) in lst]
        return [self.carrier] + self.pieces + list(self.ride) + list(self.moments) + ws

    def prev(self, i):
        return self.pieces[i - 1] if i > 0 else None


def dterm(ctx, x):
    """The duration of piece x: the stated / bridged duration, or the ride part's derived length."""
    return k("len", x) if x in ctx.ride_part else k("dur", x)


def off(ctx, x, r):
    """Reading A: neither on duty nor resting in a sleeper berth; reading B: not on duty."""
    return And(Not(U("on", x)), Not(U("rest_sleeper", x))) if r == "a" else Not(U("on", x))


# --- 395.2 definitions -------------------------------------------------------------------------------------------

def _driving(ctx, x):
    """Driving time: all time spent at the driving controls of a CMV in operation (the fact at_controls)."""
    return U("at_controls", x)


def _limb1(x): return And(U("wait_dispatch", x), Not(U("relieved", x)))
def _limb2(x): return U("inspecting", x)
def _limb4(ctx, x):
    return And(U("in_on_cmv", x), Not(U("rest_parked", x)), Not(U("rest_sleeper", x)),
               Not(U("excl", x)) if x in ctx.ride_part else None)
def _limb5(x): return U("loading", x)
def _limb6(x): return U("disabled", x)
def _limb7(x): return U("testing", x)
def _limb8(x): return U("carrier_work", x)
def _limb9(x): return U("paid_other", x)


LIMBS = {  # unit -> builder of the limb's formula for a piece
    12: lambda ctx, x: U("head_work", x), 13: lambda ctx, x: _limb1(x), 14: lambda ctx, x: _limb2(x),
    15: lambda ctx, x: _driving(ctx, x), 16: _limb4, 17: lambda ctx, x: _limb5(x), 18: lambda ctx, x: _limb6(x),
    19: lambda ctx, x: _limb7(x), 20: lambda ctx, x: _limb8(x), 21: lambda ctx, x: _limb9(x)}


def _on(ctx, limbs=None):
    limbs = limbs or LIMBS
    return [Iff(U("on", x), Or(*[limbs[n](ctx, x) for n in sorted(limbs)])) for x in ctx.pieces]


def _ride(ctx):
    """On-duty (4)(iii): up to 3 hours riding in the passenger seat immediately before or after at least 7 consecutive
    hours in the sleeper berth. A ride entry e is two pieces (a then b): after such a period the first min(d, 3 h) is
    excluded (piece a), before it the last min(d, 3 h) (piece b); a ride both after and before one is not written."""
    out = []
    idx = {x: i for i, x in enumerate(ctx.pieces)}
    # sleeper runs: forward / backward lengths over the sleeper pieces (rest_sleeper)
    for i, x in enumerate(ctx.pieces):
        if x in ctx.sleeper:
            p = ctx.prev(i)
            prevrun = k("sbf", p) if p in ctx.sleeper else m(0)
            out.append(Implies(U("rest_sleeper", x), Eq(k("sbf", x), add(prevrun, dterm(ctx, x)))))
    for i in range(len(ctx.pieces) - 1, -1, -1):
        x = ctx.pieces[i]
        if x in ctx.sleeper:
            n = ctx.pieces[i + 1] if i + 1 < len(ctx.pieces) else None
            nextrun = k("sbb", n) if n in ctx.sleeper else m(0)
            if n is None:
                continue  # a sleeper run at the end of the log: its length is unknown (no rule)
            out.append(Implies(U("rest_sleeper", x), Eq(k("sbb", x), add(dterm(ctx, x), nextrun))))
    for e, (a, b) in ctx.ride.items():
        ia, ib = idx[a], idx[b]
        p = ctx.prev(ia)
        n = ctx.pieces[ib + 1] if ib + 1 < len(ctx.pieces) else None
        aft = And(U("rest_sleeper", p), Le(m(SB7), k("sbf", p))) if p in ctx.sleeper else FALSE
        bef = And(U("rest_sleeper", n), Le(m(SB7), k("sbb", n))) if n in ctx.sleeper else FALSE
        d = k("dur", e)
        out += [Iff(U("aft", e), aft), Iff(U("bef", e), bef),
                Iff(U("excl", a), And(U("aft", e), Not(U("bef", e)))),
                Iff(U("excl", b), And(Not(U("aft", e)), U("bef", e))),
                # xrd = the excluded minutes: min(d, 3 h) next to such a period, else 0
                Implies(And(Or(U("aft", e), U("bef", e)), Le(d, m(RIDE3))), Eq(k("xrd", e), d)),
                Implies(And(Or(U("aft", e), U("bef", e)), Lt(m(RIDE3), d)), Eq(k("xrd", e), m(RIDE3))),
                Implies(And(Not(U("aft", e)), Not(U("bef", e))), Eq(k("xrd", e), m(0))),
                Implies(And(U("aft", e), Not(U("bef", e))), Eq(k("len", a), k("xrd", e))),
                Implies(And(U("aft", e), Not(U("bef", e))), Eq(add(k("len", b), k("xrd", e)), d)),
                Implies(And(Not(U("aft", e)), U("bef", e)), Eq(k("len", b), k("xrd", e))),
                Implies(And(Not(U("aft", e)), U("bef", e)), Eq(add(k("len", a), k("xrd", e)), d)),
                Implies(And(Not(U("aft", e)), Not(U("bef", e))), Eq(k("len", a), d)),
                Implies(And(Not(U("aft", e)), Not(U("bef", e))), Eq(k("len", b), m(0)))]
        # the a-piece's end position (for the 34-hour period's beginning): its start (the previous piece's end) + len
        if p is not None:
            out.append(Eq(k("tend", a), add(k("tend", p), k("len", a))))
        else:
            out.append(Eq(k("tend", a), k("len", a)))
    return out


# --- 395.3 as a chain over the pieces ----------------------------------------------------------------------------

def _off_run(ctx, r, thr10=OFF10):
    out = []
    for i, x in enumerate(ctx.pieces):
        p = ctx.prev(i)
        prev = k(f"rof{r}", p) if p else m(0)
        d = dterm(ctx, x)
        out += [Implies(off(ctx, x, r), Eq(k(f"rof{r}", x), add(prev, d))),
                Implies(Not(off(ctx, x, r)), Eq(k(f"rof{r}", x), m(0)))]
    return out


def _period14(ctx, r, thr10=OFF10):
    """(a)(1)/(a)(2): the 14-hour period runs from coming on duty following 10 consecutive hours off duty; 10 such
    hours completed by the end of a piece set it to 0 (the driver has not yet come on duty after them)."""
    out = []
    for i, x in enumerate(ctx.pieces):
        p = ctx.prev(i)
        rof = k(f"rof{r}", x)
        out.append(Implies(Le(m(thr10), rof), Eq(k(f"els{r}", x), m(0))))
        if p:
            out.append(Implies(Lt(rof, m(thr10)), Eq(k(f"els{r}", x), add(k(f"els{r}", p), dterm(ctx, x)))))
    return out


def _drive11(ctx, r, thr10=OFF10):
    """(a)(3)(i): driving time during the period of (a)(2)."""
    out = []
    for i, x in enumerate(ctx.pieces):
        p = ctx.prev(i)
        rof = k(f"rof{r}", x)
        out.append(Implies(Le(m(thr10), rof), Eq(k(f"drv{r}", x), m(0))))
        if p:
            out += [Implies(And(Lt(rof, m(thr10)), _driving(ctx, x)),
                            Eq(k(f"drv{r}", x), add(k(f"drv{r}", p), dterm(ctx, x)))),
                    Implies(And(Lt(rof, m(thr10)), Not(_driving(ctx, x))), Eq(k(f"drv{r}", x), k(f"drv{r}", p)))]
    return out


def _break30(ctx, brk=BREAK30):
    """(a)(3)(ii): the 30-minute interruption may be off-duty, sleeper berth or on-duty not driving time, or a
    combination: any consecutive time not in driving status."""
    out = []
    for i, x in enumerate(ctx.pieces):
        p = ctx.prev(i)
        nd = k("ndr", p) if p else m(0)
        out += [Implies(_driving(ctx, x), Eq(k("ndr", x), m(0))),
                Implies(Not(_driving(ctx, x)), Eq(k("ndr", x), add(nd, dterm(ctx, x)))),
                Implies(Le(m(brk), k("ndr", x)), Eq(k("dsb", x), m(0)))]
        if p:
            out += [Implies(And(Lt(k("ndr", x), m(brk)), _driving(ctx, x)),
                            Eq(k("dsb", x), add(k("dsb", p), dterm(ctx, x)))),
                    Implies(And(Lt(k("ndr", x), m(brk)), Not(_driving(ctx, x))), Eq(k("dsb", x), k("dsb", p)))]
    return out


def _onduty_sum(ctx):
    """395.3(b): on-duty time, summed over the log (the SUM is the law's; Lean checks each step)."""
    out = []
    for i, x in enumerate(ctx.pieces):
        p = ctx.prev(i)
        prev = k("ond", p) if p else m(0)
        out += [Implies(U("on", x), Eq(k("ond", x), add(prev, dterm(ctx, x)))),
                Implies(Not(U("on", x)), Eq(k("ond", x), prev))]
    return out


def _restart(ctx, r, thr=RESTART34):
    """(c): a period of 7 (8) consecutive days may end with the beginning of an off-duty period of 34 or more
    consecutive hours: rst = such a period completed by the end of the piece; lrb = where the last one began."""
    out = []
    for i, x in enumerate(ctx.pieces):
        p = ctx.prev(i)
        rof = k(f"rof{r}", x)
        out.append(Iff(U(f"rst{r}", x), Or(U(f"rst{r}", p) if p else None, Le(m(thr), rof))))
        out.append(Implies(Le(m(thr), rof), Eq(add(k(f"lrb{r}", x), rof), k("tend", x))))
        if p:
            out.append(Implies(Lt(rof, m(thr)), Eq(k(f"lrb{r}", x), k(f"lrb{r}", p))))
    return out


def _run_ahead(ctx, r):
    """The off-duty run from a piece onward (for Q3's guard): the log's last piece's run is unknown beyond the log."""
    out = []
    n = len(ctx.pieces)
    for i in range(n - 1, -1, -1):
        x = ctx.pieces[i]
        nxt = ctx.pieces[i + 1] if i + 1 < n else None
        out.append(Implies(Not(off(ctx, x, r)), Eq(k(f"rbk{r}", x), m(0))))
        if nxt:
            out.append(Implies(off(ctx, x, r), Eq(k(f"rbk{r}", x), add(dterm(ctx, x), k(f"rbk{r}", nxt)))))
    return out


def _windows(ctx, r, mutant_days=None):
    """395.3(b) with 395.2 'Seven / Eight consecutive days' and (c): rch<n> at a moment (end of piece j)."""
    out = []
    for mo, j in ctx.moments.items():
        x = ctx.pieces[j]
        for n, lst in ctx.windows.get(mo, {}).items():
            lim = LIM[n]
            rst, lrb, ond = U(f"rst{r}", x), k(f"lrb{r}", x), k("ond", x)
            known, unknown = [], []
            for (w, wj, is_known) in lst:
                active = Or(Not(rst), Lt(lrb, k("pos", w)))
                if is_known:
                    base = k("ond", ctx.pieces[wj]) if wj is not None else m(0)
                    known.append(And(Le(m(0), k("pos", w)), active, Le(add(m(lim), base), ond)))
                else:
                    unknown.append((And(Lt(k("pos", w), m(0)), active, Le(m(lim), ond)), And(Lt(k("pos", w), m(0)),
                                                                                       Not(active))))
            name = f"rch{n}{r}"
            out.append(Implies(Or(*known, *[u for (u, _) in unknown]), U(name, mo)))
            out.append(Implies(And(*[Not(f) for f in known], *[v for (_, v) in unknown]), Not(U(name, mo))))
    return out


def _future(ctx, r):
    """Q3's guard: the moment is inside an off-duty run that the log continues to 34 hours or more."""
    out = []
    for mo, j in ctx.moments.items():
        if "q3" not in ctx.asks.get(mo, ()):
            continue
        x = ctx.pieces[j]
        nxt = ctx.pieces[j + 1] if j + 1 < len(ctx.pieces) else None
        rof = k(f"rof{r}", x)
        if nxt is None:
            body = And(off(ctx, x, r), Lt(rof, m(RESTART34)))   # the run's continuation is unknown: guard holds if off
            out.append(Iff(U(f"fut{r}", mo), body))
        else:
            out.append(Iff(U(f"fut{r}", mo), And(off(ctx, x, r), Lt(rof, m(RESTART34)),
                                                  Le(m(RESTART34), add(rof, k(f"rbk{r}", nxt))))))
    return out


def _may(ctx, r, lim=(PER14, DRIVE11, DRIVE8)):
    """Q1: 395.3(a)(1)-(3) and (b) at the moment (end of piece j); the (b) limb by the carrier's every_day fact."""
    out = []
    l14, l11, l8 = lim
    car = ctx.carrier
    for mo, j in ctx.moments.items():
        if "q1" not in ctx.asks.get(mo, ()):
            continue
        x = ctx.pieces[j]
        b = Or(And(U("every_day", car), U(f"rch8{r}", mo)), And(Not(U("every_day", car)), U(f"rch7{r}", mo)))
        out.append(Iff(U(f"may{r}", mo), And(Lt(k(f"els{r}", x), m(l14)), Lt(k(f"drv{r}", x), m(l11)),
                                             Lt(k("dsb", x), m(l8)), Not(b))))
    return out


def _left(ctx, r, lim=(PER14, DRIVE11, DRIVE8)):
    """Q2: the driving time left before a limit of 395.3(a) = the least of the three, or 0 once one is reached."""
    out = []
    l14, l11, l8 = lim
    for mo, j in ctx.moments.items():
        if "q2" not in ctx.asks.get(mo, ()):
            continue
        x = ctx.pieces[j]
        E, D, X, R = k(f"els{r}", x), k(f"drv{r}", x), k("dsb", x), k(f"rem{r}", mo)
        live = And(Lt(E, m(l14)), Lt(D, m(l11)), Lt(X, m(l8)))
        e_le_d = Le(add(m(l14), D), add(m(l11), E))      # 14h - E <= 11h - D
        e_le_x = Le(add(m(l14), X), add(m(l8), E))       # 14h - E <= 8h - X
        d_le_x = Le(add(m(l11), X), add(m(l8), D))       # 11h - D <= 8h - X
        out += [Implies(Or(Le(m(l14), E), Le(m(l11), D), Le(m(l8), X)), Eq(R, m(0))),
                Implies(And(live, e_le_d, e_le_x), Eq(add(R, E), m(l14))),
                Implies(And(live, Not(e_le_d), d_le_x), Eq(add(R, D), m(l11))),
                Implies(And(live, Not(e_le_x), Not(d_le_x)), Eq(add(R, X), m(l8)))]
    return out


def per_r(fn):
    return lambda ctx: [f for r in ctx.readings for f in fn(ctx, r)]


UNITS = {
    1: ("PART", lambda ctx: [f for r in ctx.readings for f in _may(ctx, r)], "other:norm",
        "395.3(a) lead-in: the driver's prohibition is written as the classification 'may drive at the moment' "
        "(with (b)); the motor carrier's duty ('no motor carrier shall permit or require') is not carried; 'Except "
        "as otherwise provided in 395.1' is the fixed fact 'no exception of 395.1 applies'; 'regardless of the "
        "number of motor carriers' = on-duty time for any carrier counts (limbs (8), (9))"),
    2: ("RULE", per_r(lambda ctx, r: _off_run(ctx, r)),
        "(a)(1): 10 consecutive hours off duty = an off-duty run of 600 minutes or more (a SUM over the run's pieces); "
        "an answer exists only once the log shows such a run (els undefined before it)"),
    3: ("RULE", per_r(lambda ctx, r: _period14(ctx, r)),
        "(a)(2): the 14-hour period after coming on duty following 10 consecutive hours off duty"),
    4: ("RULE", lambda ctx: [f for r in ctx.readings for f in _drive11(ctx, r)] + _break30(ctx)
        + [f for r in ctx.readings for f in _left(ctx, r)],
        "(a)(3)(i) 11 hours of driving in that period; (ii) more than 8 hours of driving without a consecutive "
        "30-minute interruption by off-duty, sleeper-berth or on-duty not driving time, alone or combined; the short-"
        "haul exceptions are the fixed fact 'none'. Q2 = the least time left under (a)(2), (a)(3)(i), (a)(3)(ii)"),
    5: ("PART", lambda ctx: _onduty_sum(ctx), "other:norm",
        "395.3(b) lead-in: 'having been on duty' = the on-duty SUM over the log (ond, Lean-checked steps); the "
        "driver's prohibition is carried by the 'may drive' classification of unit 1 (its (b) conjunct); the motor "
        "carrier's duty is not carried"),
    6: ("RULE", per_r(lambda ctx, r: [f for f in _windows(ctx, r) if '"rch7' in json.dumps(f)]),
        "(b)(1): 60 hours in a period of 7 consecutive days, carrier not operating every day (every_day false)"),
    7: ("RULE", per_r(lambda ctx, r: [f for f in _windows(ctx, r) if '"rch8' in json.dumps(f)]),
        "(b)(2): 70 hours in a period of 8 consecutive days, carrier operating every day"),
    8: ("RULE", per_r(lambda ctx, r: _restart(ctx, r) + _future(ctx, r) + _run_ahead(ctx, r)),
        "(c)(1)/(2): a period may end with the beginning of an off-duty period of 34 or more consecutive hours "
        "(rst, lrb; a window is live unless the last such period began at or after its start)"),
    9: ("RULE", lambda ctx: [], "(c)(2): the same rule as (c)(1) for 8-day periods (unit 8's rules serve both)"),
    10: ("RULE", lambda ctx: [], "Driving time: the fact at_controls (time at the driving controls of a CMV in "
         "operation); 'commercial motor vehicle' is a fixed fact of the test (whether a vehicle is one is a probe)"),
    11: ("PART", lambda ctx: [], "date/age arithmetic",
         "Eight consecutive days: the 8 day-starts at the carrier's designated time up to the moment are LISTED by the "
         "bridge script (B5: list the days of a window) and turned into positions; the 70-hour comparison over each "
         "period is unit 7's rule (bridged: the listing of the days)"),
    12: ("RULE", lambda ctx: _on(ctx),
         "On-duty time: written as head OR limbs (1)-(9), each over the facts the encoder states for the activity the "
         "log names (the head's 'begins to work or is required to be in readiness to work until ... relieved from work "
         "and all responsibility' is the fact head_work; the activity readings are listed as encoder judgement)"),
    13: ("RULE", lambda ctx: [], "(1) waiting to be dispatched unless relieved (in unit 12's on(x))"),
    14: ("RULE", lambda ctx: [], "(2) inspecting, servicing or conditioning a CMV (in on(x))"),
    15: ("RULE", lambda ctx: [], "(3) all driving time (in on(x))"),
    16: ("RULE", lambda ctx: _ride(ctx) if ctx.ride else [],
         "(4) in or on a CMV other than (i) resting in or on a parked vehicle (397.5: fixed fact 'does not apply'), "
         "(ii) resting in a sleeper berth, (iii) up to 3 hours riding in the passenger seat immediately before or "
         "after at least 7 consecutive hours in the sleeper berth (the ride split min(d, 3 h) / rest; a ride both "
         "before and after such a period is not decided)"),
    17: ("RULE", lambda ctx: [], "(5) loading / unloading and the rest of the limb (in on(x))"),
    18: ("RULE", lambda ctx: [], "(6) a disabled CMV (in on(x))"),
    19: ("PART", lambda ctx: [], "cross-reference",
         "(7) a breath or urine test 'required by part 382' (outside the pinned source): the testing fact is stated"),
    20: ("RULE", lambda ctx: [], "(8) any other work for a motor carrier (in on(x))"),
    21: ("RULE", lambda ctx: [], "(9) compensated work for a person who is not a motor carrier (in on(x))"),
    22: ("PART", lambda ctx: [], "date/age arithmetic",
         "Seven consecutive days: as unit 11 (the 7 day-starts listed by the bridge; unit 6's rule compares)"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a case: [{"id", "unit", "formula", "defines"}]."""
    out = []
    table = units_table(mutant)
    for n, e in sorted(table.items()):
        if e[1] is None:
            continue
        for i, f in enumerate(e[1](ctx)):
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers --------------------------------------------------------------------------------------------

def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def is_iff(f):
    return (type(f) is list and f and f[0] == "and" and type(f[1]) is list and type(f[2]) is list
            and f[1][:1] == ["implies"] and f[2][:1] == ["implies"] and f[1][1] == f[2][2] and f[1][2] == f[2][1])


def conjuncts(f):
    if is_iff(f) or type(f) is not list or f[0] != "and":
        return [f]
    return conjuncts(f[1]) + conjuncts(f[2])


def atoms_in(f, atoms, constants):
    if type(f) is not list or not f:
        return
    if f[0] in ("unary", "binary"):
        atoms.add(key(f))
        return
    if f[0] == "const" and len(f) == 3:
        constants.add(f[2])
        return
    for part in f[1:]:
        atoms_in(part, atoms, constants)


def _first_const(t):
    if t[0] == "const" and len(t) == 3:
        return t[2]
    if t[0] == "add":
        return _first_const(t[2])
    return None


def defines(f):
    """The atoms / integer constants a ground rule fixes."""
    if is_iff(f):
        lhs = f[1][1]
        if lhs[0] in ("unary", "binary"):
            return [key(lhs)]
        raise ValueError(f"iff with a non-atom left side: {f}")
    if f[0] == "implies":
        return defines(f[2])
    if f[0] in ("unary", "binary"):
        return [key(f)]
    if f[0] == "not" and f[1][0] in ("unary", "binary"):
        return [key(f[1])]
    if f[0] == "eq":
        name = _first_const(f[1])
        if name is not None:
            return [name]
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

def environment(ctx, used=None):
    """The case's environment; `used` (constant names the case's rules and facts mention) keeps it to those."""
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
        for base, w in INT_UNITS.items():
            if used is not None and f"{base}_{x}" not in used:
                continue
            consts[f"{base}_{x}"] = {"sort": "$int", "unit": MIN, "description": f"{w[0].upper() + w[1:]} ({x}).",
                                     "verbalisation": f"{w} ({x})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **DERIVED_UNARY}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A log piece, ride, moment, window start or carrier."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {MIN: {"scale": "1", "display": {"kind": "decimal", "label": "minutes"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, builder):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], builder, *e[2:])
        return t
    return apply


def _json_sub(a, b):
    return lambda f: json.loads(json.dumps(f).replace(a, b))


def _wrap(n, walker):
    def apply(t):
        t = dict(t)
        e = t[n]
        old = e[1]
        t[n] = (e[0], lambda ctx: [walker(f) for f in old(ctx)], *e[2:])
        return t
    return apply


def _drop_limb(n):
    def apply(t):
        t = dict(t)
        limbs = {kk: v for kk, v in LIMBS.items() if kk != n}
        e = t[12]
        t[12] = (e[0], lambda ctx: _on(ctx, limbs), *e[2:])
        return t
    return apply


def _wrap_many(ns, walker):
    def apply(t):
        for n in ns:
            t = _wrap(n, walker)(t)
        return t
    return apply


MUTANTS = {
    "M1": ("TIME LIMIT: (a)(3)(i) 11 hours read as 10", _wrap_many((1, 4), _json_sub('"minute", "660"', '"minute", "600"'))),
    "M2": ("TIME LIMIT: (a)(2) 14 consecutive hours read as 13",
           _wrap_many((1, 4), _json_sub('"minute", "840"', '"minute", "780"'))),
    "M3": ("TIME LIMIT: (a)(1)/(a)(2) 10 consecutive hours off duty read as 9",
           _wrap_many((3, 4), _json_sub('"minute", "600"', '"minute", "540"'))),
    "M4": ("INTERRUPTION: (a)(3)(ii) consecutive 30-minute interruption read as 15 minutes",
           _wrap(4, _json_sub('"minute", "30"', '"minute", "15"'))),
    "M5": ("DEFINED TERM: on-duty limb (5) loading / unloading dropped", _drop_limb(17)),
    "M6": ("DEFINED TERM: on-duty limb (2) inspecting dropped", _drop_limb(14)),
    "M7": ("SUM: the on-duty sum adds 0 for every on-duty piece after the first",
           _swap(5, lambda ctx: _ond_drop(ctx))),
    "M8": ("WINDOW: (b)(2) 70 hours read as 60", _wrap(7, _json_sub('"minute", "4200"', '"minute", "3600"'))),
    "M9": ("RESTART: (c) 34 consecutive hours read as 24", _wrap(8, _json_sub('"minute", "2040"', '"minute", "1440"'))),
    "M10": ("EXCLUSION: on-duty (4)(iii) passenger-seat exclusion dropped (excl never holds)",
            _wrap(16, lambda f: Iff(f[1][1], FALSE) if is_iff(f) and f[1][1][1] == "excl" else f)),
}


def _ond_drop(ctx):
    out = []
    for i, x in enumerate(ctx.pieces):
        p = ctx.prev(i)
        prev = k("ond", p) if p else m(0)
        out += [Implies(U("on", x), Eq(k("ond", x), add(prev, m(0)) if i > 0 else add(m(0), dterm(ctx, x)))),
                Implies(Not(U("on", x)), Eq(k("ond", x), prev))]
    return out


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
