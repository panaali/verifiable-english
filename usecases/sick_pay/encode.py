"""The encoder for statutory sick pay (statute corpus batch 3, law 8): a sub-case spec (cases.py, smoke_test.py) -> the
translation's Ctx and the stated facts. SAME-FAMILY. Conventions (encoder judgement, listed in RESULT.md):
C1 the facts are those the case states; a day the case does not describe is UNKNOWN (no fact): its piece leaves every rule
   that reads it undetermined (never read as false);
C2 one sub-case per (employee, employer) (s. 153(4), 154(4) by structure);
C3 the day cut: pieces are runs of consecutive days with the same stated facts, cut at each asked day (a piece of its own),
   at the first and last day of each asked run, at the contract's first day and the day after its last, at the day the
   disqualifying period begins, and at each Sunday inside a run whose facts allow incapacity; the cut is a search aid only
   (Lean checks consecutiveness and week membership by date arithmetic);
C4 weeks: every week from the first to the last a piece touches (and the anchor week); a week's required / agreed days from
   the facts that state them for a range of weeks;
C5 the anchor: one day the facts name with its day of the week (the first such day in the facts);
C6 stated judgments ("cannot reasonably be expected to do that work") enter as stated facts.
"""
from __future__ import annotations

import datetime as dt

import translation as T

D = dt.date.fromisoformat


def sunday_of(d):
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)   # search aid only (Lean re-derives every Sunday)


def days(a, b):
    return (b - a).days


class Spec:
    """spans: [(first, last, {"dis","cannot","deemed"} subset of stated-true facts or None = unknown)];
    weekly: [(first_sunday, last_saturday, {"required": [j..]} or {"agreed": [j..]})]; contract: dict start, end, nwe,
    dq; asked: [dates]; runs: [(first, last)]; anchor: (date, weekday index 0 = Sunday)."""

    def __init__(self, sid, contract, spans, weekly, anchor, asked=(), runs=(), judgement=()):
        self.sid, self.contract = sid, dict(contract)
        self.spans = [(D(a), D(b), None if f is None else set(f)) for a, b, f in spans]
        self.weekly = [(D(a), D(b), dict(p)) for a, b, p in weekly]
        self.anchor = (D(anchor[0]), anchor[1])
        self.asked = [D(d) for d in asked]
        self.runs = [(D(a), D(b)) for a, b in runs]
        self.judgement = list(judgement)


def _facts_on(spec, d):
    for a, b, f in spec.spans:
        if a <= d <= b:
            return f
    return None


def build(spec):
    """-> (ctx, facts, maps) maps: piece of each asked day, run id of each asked run."""
    cs = spec.contract
    lo = min([a for a, _, _ in spec.spans] + spec.asked + [a for a, _ in spec.runs])
    hi = max([b for _, b, _ in spec.spans] + spec.asked + [b for _, b in spec.runs])
    cuts = set()
    for a, b, f in spec.spans:
        cuts |= {a, b + dt.timedelta(days=1)}
    for d in spec.asked:
        cuts |= {d, d + dt.timedelta(days=1)}
    for a, b in spec.runs:
        cuts |= {a, b + dt.timedelta(days=1)}
    for key, plus in (("start", 0), ("end", 1), ("dq", 0)):
        if cs.get(key):
            cuts.add(D(cs[key]) + dt.timedelta(days=plus))
    d = lo
    while d <= hi:
        f = _facts_on(spec, d)
        if d.weekday() == 6 and (f is None or f & {"dis", "deemed"}):
            cuts.add(d)
        d += dt.timedelta(days=1)
    cuts = sorted(x for x in cuts if lo < x <= hi)
    bounds = [lo] + cuts + [hi + dt.timedelta(days=1)]
    raw = [(bounds[i], bounds[i + 1] - dt.timedelta(days=1)) for i in range(len(bounds) - 1)]
    # weeks (C4): the anchor week and every week a piece lies within
    asun = sunday_of(spec.anchor[0])
    pieces, piece_of, used = [], {}, {asun}
    for i, (a, b) in enumerate(raw):
        x = f"p{i}"
        f = _facts_on(spec, a)
        inweek = sunday_of(a) == sunday_of(b) and (f is None or f & {"dis", "deemed"} or a == b)
        w = sunday_of(a) if inweek else None
        if w is not None:
            used.add(w)
        pieces.append((x, w, (days(w, a), days(w, b)) if w is not None else None))
        if a == b:
            piece_of[a] = x
    suns = sorted(used)
    wid = {s: f"w{i}" for i, s in enumerate(suns)}
    weeks = [(wid[s], days(asun, s) // 7) for s in suns]
    pieces = [(x, None if w is None else wid[w], span) for x, w, span in pieces]
    runs, run_of = [], {}
    for i, (a, b) in enumerate(spec.runs):
        ps = [f"p{j}" for j, (pa, pb) in enumerate(raw) if a <= pa and pb <= b]
        runs.append((f"r{i}", ps))
        run_of[(a, b)] = f"r{i}"
    asked = sorted({piece_of[d] for d in spec.asked}, key=lambda x: int(x[1:]))
    ctx = T.Ctx("c", weeks, pieces, runs, asked, has_dq=bool(cs.get("dq")))
    facts = []

    def add(f):
        facts.append({"id": f"f{len(facts)}", "formula": f})

    cc = ctx.contract
    add(T.Eq(T.k("nwe", cc), T.gbp(cs["nwe"])))
    add(T.Eq(T.k("cst", cc), ["date", cs["start"]]))
    if cs.get("end"):
        add(T.U("has_end", cc))
        add(T.Eq(T.k("cen", cc), ["date", cs["end"]]))
    else:
        add(T.Not(T.U("has_end", cc)))
    if cs.get("dq"):
        add(T.U("has_dq", cc))
        add(T.Eq(T.k("dqs", cc), ["date", cs["dq"]]))
    else:
        add(T.Not(T.U("has_dq", cc)))
    for (x, _, _), (a, b) in zip(pieces, raw):
        add(T.Eq(T.k("st", x), ["date", a.isoformat()]))
        add(T.Eq(T.k("en", x), ["date", b.isoformat()]))
        f = _facts_on(spec, a)
        if f is not None:
            for p in ("dis", "cannot", "deemed"):
                add(T.U(p, x) if p in f else T.Not(T.U(p, x)))
    for s in suns:
        w = wid[s]
        pat = None
        for a, b, p in spec.weekly:
            if a <= s and s + dt.timedelta(days=6) <= b:
                pat = p
        if pat is None:
            continue   # C1: a week whose days the facts do not state: unknown
        agreed = "agreed" in pat
        add(T.U("agr", w) if agreed else T.Not(T.U("agr", w)))
        for j in range(7):
            if agreed:
                add(T.U(f"agd{j}", w) if j in pat["agreed"] else T.Not(T.U(f"agd{j}", w)))
            add(T.U(f"req{j}", w) if j in pat.get("required", ()) else T.Not(T.U(f"req{j}", w)))
    aw = wid[sunday_of(spec.anchor[0])]
    add(T.Eq(T.k("anc", aw), ["date", spec.anchor[0].isoformat()]))
    for j in range(7):
        add(T.U(f"anc{j}", aw) if j == spec.anchor[1] else T.Not(T.U(f"anc{j}", aw)))
    for (r, _), (a, b) in zip(runs, spec.runs):
        add(T.Eq(T.k("rs", r), ["date", a.isoformat()]))
        add(T.Eq(T.k("re", r), ["date", b.isoformat()]))
    return ctx, facts, {"piece_of": {d.isoformat(): x for d, x in piece_of.items()},
                        "run_of": {f"{a.isoformat()}/{b.isoformat()}": r for (a, b), r in run_of.items()}}
