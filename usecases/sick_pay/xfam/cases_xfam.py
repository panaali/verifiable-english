"""The encoder's cases for the CROSS-FAMILY statutory sick pay set, from questions-enc.jsonl ONLY (sha256 checked at
import). Copy this file to out/cases_xfam.py and fill S, JUDGEMENT, CALENDAR, NOTES and UNSUPPORTED.

Record format (encode.Spec; encode.py's docstring, conventions C1-C6, binds you):
- one sub(...) per (case, employer) the case's questions name (C2). The employer is the name after "by" in a payable /
  amount question or after "from" in a weekly-rate question (parse_q below reads it; your key must equal it exactly);
- contract: C(start, end, nwe, dq): the day the contract of service first takes effect, the day it expires or is brought
  to an end (None if not stated), the normal weekly earnings as stated (a string, e.g. "120.00"), the day a disqualifying
  period begins (None if none);
- spans: [(first, last, facts)] in time order, covering every day the questions need: facts is a subset of
  {"dis", "cannot", "deemed"} that the case STATES true for every day of the range (N = none true, I = {"dis", "cannot"},
  ILLCAN = {"dis"} = ill but able to do the work, DM = {"deemed"}), or None for a range whose facts are not stated (C1);
- weekly: [(first_sunday, last_saturday, {"required": [j..]} or {"agreed": [j..]})], j = 0 Sunday ... 6 Saturday: the
  week's days the contract requires the employee to be available for work on, or the qualifying days the employee and
  employer agree, for every week from first_sunday to last_saturday (each range must be whole weeks, Sunday to Saturday);
- anchor: (date, j): one day and its day of the week (0 Sunday ... 6 Saturday) (C5; translation R9 builds every week's
  Sunday from it in Lean).
Dates are ISO strings "YYYY-MM-DD". The asked days and runs come from the questions (parse_q); you do not list them.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

from encode import Spec

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "0a9a08898a97c6e9f1c05b63ad368d41f164f0ceb624b8b6056bea3087f153c3"
ENC_PATH = next(p for p in (HERE / "questions-enc.jsonl", HERE.parent / "questions-enc.jsonl") if p.exists())
if hashlib.sha256(ENC_PATH.read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

N, I, ILLCAN, DM = set(), {"dis", "cannot"}, {"dis"}, {"deemed"}
MF, ALL7 = [1, 2, 3, 4, 5], list(range(7))
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
DATE = r"(?:(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday) )?(\d{1,2}) (\w+) (\d{4})"


def iso(m):
    return dt.date(int(m[2]), MONTHS.index(m[1]) + 1, int(m[0])).isoformat()


def parse_q(text):
    """-> (employer, form, args) from a question's text (this set's phrasings; a day may or may not carry its weekday)."""
    m = re.match(r"What is the weekly rate of statutory sick pay for \w+ from (.+)\?$", text)
    if m:
        return m[1], "rate", {}
    m = re.match(r"Is statutory sick pay payable by (.+) to \w+ for " + DATE + r"\?$", text)
    if m:
        return m[1], "pay", {"date": iso(m.groups()[1:])}
    m = re.match(r"What amount of statutory sick pay is payable by (.+) to \w+ for the days from " + DATE + " to " + DATE
                 + r"\?$", text)
    if m:
        g = m.groups()
        return g[0], "run", {"first": iso(g[1:4]), "last": iso(g[4:7])}
    m = re.match(r"What amount of statutory sick pay is payable by (.+) to \w+ for " + DATE + r"\?$", text)
    if m:
        return m[1], "amount", {"date": iso(m.groups()[1:])}
    raise ValueError(text)


ENC = {c["id"]: c for c in map(json.loads, ENC_PATH.read_text(encoding="utf-8").splitlines())}

S = {}   # case id -> employer -> (contract, spans, weekly, anchor)


def sub(cid, employer, contract, spans, weekly, anchor):
    S.setdefault(cid, {})[employer] = (contract, spans, weekly, anchor)


def C(start, end, nwe, dq=None):
    return {"start": start, "end": end, "nwe": nwe, "dq": dq}


# ---- the encoder's sub-cases (fill in) -----------------------------------------------------------------------------
# Every in-scope case says "Outside the stated intervals, on all dates needed here, <employee> has no disease or
# disablement, can do all the contract work, and is not deemed incapable by regulations" (S028 Drew, S029 Felix: "Outside
# that day / interval ..."). That general range is read (JUDGEMENT, every case) as LO..HI below: N on every day of it
# outside the stated intervals. LO is more than 57 days before every stated incapacity, so the chain's first piece is a
# stated non-incapacity day (R1, R7). The weekly agreement is copied for the whole weeks WLO..WHI that hold LO..HI
# (WLO, WHI: the Sunday on or before LO and the Saturday on or after HI, taken from datetime).
LO, HI = "2025-11-01", "2026-12-31"
WLO, WHI = "2025-10-26", "2027-01-02"
MWF, TT = [1, 3, 5], [2, 4]
SUN, WED = [0], [3]


def _iso_add(iso, n):
    return (dt.date.fromisoformat(iso) + dt.timedelta(days=n)).isoformat()


def fill(*stated):
    """The stated intervals [(first, last, facts)] in time order, with N on the other days of LO..HI (the general
    'outside the stated intervals' fact)."""
    out, cur = [], LO
    for a, b, f in stated:
        if a > cur:
            out.append((cur, _iso_add(a, -1), N))
        out.append((a, b, f))
        cur = _iso_add(b, 1)
    if cur <= HI:
        out.append((cur, HI, N))
    return out


def agreed(days):
    return [(WLO, WHI, {"agreed": days})]


Y26 = ("2026-01-01", "2026-12-31")   # start, end of the 1 January 2026 - 31 December 2026 contracts

sub("S001", "Beth", C(*Y26, "120.00"), fill(("2026-05-04", "2026-05-04", I)), agreed(MWF), ("2026-05-04", 1))
sub("S002", "Carl", C(*Y26, "105.00"), fill(("2026-05-04", "2026-05-06", DM)), agreed(MWF), ("2026-05-04", 1))
sub("S003", "Dan", C(*Y26, "150.00"), fill(("2026-05-08", "2026-05-11", I)), agreed(MF), ("2026-05-08", 5))
sub("S004", "Ella", C(*Y26, "100.00"), fill(("2026-05-10", "2026-05-10", DM)), agreed(SUN), ("2026-05-10", 0))
sub("S005", "Finn", C(*Y26, "100.00"), fill(("2026-05-09", "2026-05-09", I)), agreed(MF), ("2026-05-09", 6))
sub("S006", "Gail", C(*Y26, "105.00"), fill(("2026-05-03", "2026-05-09", DM)), agreed(ALL7), ("2026-05-03", 0))
sub("S007", "Hugh", C(*Y26, "200.00"), fill(("2026-05-04", "2026-05-08", I)), agreed(MF), ("2026-05-04", 1))
sub("S008", "Iris", C(*Y26, "50.00"), fill(("2026-05-04", "2026-05-04", DM)), agreed(MF), ("2026-05-04", 1))
sub("S009", "Jack", C(*Y26, "154.05"), fill(("2026-05-04", "2026-05-04", DM)), agreed(MWF), ("2026-05-04", 1))
sub("S010", "Kate", C(*Y26, "154.10"), fill(("2026-05-04", "2026-05-04", DM)), agreed(MF), ("2026-05-04", 1))
sub("S011", "Leo", C(*Y26, "100.00"), fill(("2026-05-04", "2026-05-04", ILLCAN)), agreed(MF), ("2026-05-04", 1))
sub("S012", "Lena", C(*Y26, "105.00"), fill(("2026-05-04", "2026-05-07", I)), agreed(ALL7), ("2026-05-04", 1))
sub("S013", "Mark", C("2026-05-04", "2026-12-31", "105.00"), fill(("2026-05-01", "2026-05-06", DM)), agreed(MWF),
    ("2026-05-01", 5))
sub("S014", "Nina", C("2026-05-03", "2026-12-31", "100.00"), fill(("2026-05-01", "2026-05-05", DM)), agreed(MF),
    ("2026-05-01", 5))
sub("S015", "Owen", C("2026-04-01", "2026-12-31", "150.00"),
    fill(("2026-03-01", "2026-03-02", DM), ("2026-04-28", "2026-04-30", DM)), agreed(MF), ("2026-03-01", 0))
sub("S016", "Paula", C("2026-04-01", "2026-12-31", "150.00"),
    fill(("2026-03-01", "2026-03-02", DM), ("2026-04-29", "2026-05-01", DM)), agreed(MF), ("2026-03-01", 0))
sub("S017", "Quentin", C("2026-01-01", "2026-05-05", "150.00"), fill(("2026-05-04", "2026-05-08", I)), agreed(MF),
    ("2026-05-04", 1))
sub("S018", "Rosa", C("2026-01-01", "2026-05-05", "150.00"), fill(("2026-05-04", "2026-05-08", I)), agreed(MF),
    ("2026-05-04", 1))
sub("S019", "Sam", C(*Y26, "150.00"), fill(("2026-05-04", "2026-05-05", I)), agreed(MF), ("2026-05-04", 1))
sub("S020", "Tom", C(*Y26, "150.00", "2026-05-06"), fill(("2026-05-04", "2026-05-08", DM)), agreed(MF),
    ("2026-05-04", 1))
sub("S021", "Umar", C(*Y26, "200.00", "2026-05-04"), fill(("2026-05-01", "2026-05-06", DM)), agreed(MF),
    ("2026-05-01", 5))
sub("S022", "Wendy", C(*Y26, "150.00"), fill(("2026-01-07", "2026-07-24", DM)), agreed(MF), ("2026-01-07", 3))
sub("S023", "Yara", C(*Y26, "105.00"), fill(("2026-01-07", "2026-07-24", DM)),
    [(WLO, "2026-01-10", {"agreed": MWF}), ("2026-01-11", WHI, {"agreed": MF})], ("2026-01-07", 3))
sub("S024", "Zane", C(*Y26, "150.00"),
    fill(("2026-01-05", "2026-07-17", DM), ("2026-09-12", "2026-09-14", DM)), agreed(MF), ("2026-01-05", 1))
sub("S025", "Adam", C(*Y26, "150.00"),
    fill(("2026-01-05", "2026-07-17", DM), ("2026-09-13", "2026-09-14", DM)), agreed(MF), ("2026-01-05", 1))
sub("S026", "Blake", C(*Y26, "150.00"),
    fill(("2026-01-05", "2026-01-11", DM), ("2026-03-09", "2026-03-15", DM), ("2026-05-11", "2026-11-10", DM)),
    agreed(MF), ("2026-01-05", 1))
sub("S027", "Bruno", C("2026-01-01", "2026-05-04", "120.00"), fill(("2026-05-01", "2026-05-07", DM)), agreed(MWF),
    ("2026-05-01", 5))
sub("S028", "Cody", C(*Y26, "120.00"), fill(("2026-05-04", "2026-05-04", I)), agreed(MWF), ("2026-05-04", 1))
sub("S028", "Drew", C(*Y26, "100.00"), fill(("2026-05-04", "2026-05-04", I)), agreed(MF), ("2026-05-04", 1))
sub("S029", "Evan", C(*Y26, "150.00"), fill(("2026-01-05", "2026-07-22", DM)), agreed(MF), ("2026-01-05", 1))
sub("S029", "Felix", C("2026-05-04", "2026-12-31", "100.00"), fill(("2026-01-05", "2026-07-22", DM)), agreed(MF),
    ("2026-01-05", 1))
sub("S030", "Gina", C(*Y26, "105.00"), fill(("2026-05-08", "2026-05-12", DM)),
    [(WLO, "2026-05-09", {"agreed": MWF}), ("2026-05-10", WHI, {"agreed": ALL7})], ("2026-05-08", 5))
sub("S031", "Hector", C(*Y26, "120.00"), fill(("2026-05-03", "2026-05-10", DM)), agreed(SUN), ("2026-05-03", 0))
sub("S032", "Ines", C(*Y26, "105.00"), fill(("2026-05-04", "2026-05-10", DM)), agreed(WED), ("2026-05-04", 1))
sub("S033", "Jon", C(*Y26, "200.00"), fill(("2026-05-04", "2026-05-04", DM)), agreed(MWF), ("2026-05-04", 1))
sub("S034", "Kira", C(*Y26, "151.01"), fill(("2026-05-04", "2026-05-04", DM)), agreed(MF), ("2026-05-04", 1))
sub("S035", "Louis", C(*Y26, "120.00"), fill(("2026-05-05", "2026-05-07", I)), agreed(TT), ("2026-05-05", 2))

_ANCHOR = {cid: sorted({e[3] for e in emps.values()}) for cid, emps in S.items()}
_WD = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
_GENERAL = ("'on all dates needed here' (outside the stated intervals: no disease, can work, not deemed) read as "
            f"{LO}..{HI} (N spans), so the chain starts more than 57 days before any stated incapacity (R1, R7)")
_WEEKS = (f"'every week beginning with Sunday that contains a date described here' read as every whole week "
          f"{WLO}..{WHI} holding that range (only weeks with a stated incapacity day, an asked day or the anchor are used)")

# Encoder judgement: a reading beyond copying a stated fact (case id -> [one line each]).
JUDGEMENT = {cid: [_GENERAL] for cid in S}
for _cid in S:
    if _cid not in ("S023", "S030"):
        JUDGEMENT[_cid].append(_WEEKS if _cid != "S028" else _WEEKS + "; for Drew the facts say 'every week' (a copy)")
JUDGEMENT["S011"].append("'mild wrist sprain' read as a bodily disablement (dis true); the stated judgment that Jane "
                         "can reasonably be expected to do and can do the work: cannot false (ILLCAN)")
JUDGEMENT["S013"].append("the deemed days 1-3 May 2026 lie before the contract first takes effect (4 May 2026): "
                         "stated as deemed all the same (152(6)); R3 decides their period of entitlement")
JUDGEMENT["S014"].append("the deemed days 1-2 May 2026 lie before the contract first takes effect (3 May 2026): "
                         "stated as deemed all the same (152(6)); R3 decides")
JUDGEMENT["S020"].append("'Her disqualifying period, a maternity pay period, begins on 6 May 2026': dq 2026-05-06, "
                         "has_dq true (153(2)(d), (12)(a))")
JUDGEMENT["S021"].append("'Her disqualifying period, a maternity allowance period, begins on 4 May 2026': dq "
                         "2026-05-04, has_dq true (153(2)(d), (12)(b))")
JUDGEMENT["S023"].append("weeks 'up to and including the week beginning 4 January 2026' read from WLO (2025-10-26); "
                         "'from 11 January 2026 onward' read to WHI (2027-01-02)")
JUDGEMENT["S029"].append("Felix: the deemed days 5 January - 3 May 2026 lie before Felix's contract first takes effect "
                         "(4 May 2026): stated as deemed all the same (152(6)); R3 decides")
JUDGEMENT["S030"].append("weeks 'through the week beginning 3 May 2026' read from WLO (2025-10-26); 'from 10 May 2026 "
                         "onward' read to WHI (2027-01-02)")
for _cid in ("S033", "S034"):
    JUDGEMENT[_cid].append("the stated rounding convention ('no rounding until the answer; the answer to the nearest "
                           "penny, half up') has no fact in the vocabulary: not encoded; the build answers as it can")

# Calendar facts the case does not state (e.g. the anchor's day of the week, computed with Python's datetime, never by
# hand): case id -> [one line each]. Listed apart from JUDGEMENT; both count as "outside Lean".
CALENDAR = {}
for _cid, _ans in _ANCHOR.items():
    CALENDAR[_cid] = [f"anchor {d} is a {_WD[j]}: not stated, computed with datetime" for d, j in _ans]
    CALENDAR[_cid].append(f"weekly range bounds {WLO} (a Sunday) and {WHI} (a Saturday): not stated, computed with "
                          "datetime")
CALENDAR["S023"].append("2026-01-10 (Saturday ending the week beginning 4 January 2026) computed with datetime")
CALENDAR["S030"].append("2026-05-09 (Saturday ending the week beginning 3 May 2026) computed with datetime")
# Transcription notes (copies of stated facts, not judgement).
NOTES = {
    "S028": ["two employers, two sub-cases (C2): Cody (MWF, £120.00) and Drew (Mon-Fri, £100.00); 4 May 2026 the same "
             "back injury with the stated judgment for each contract (I)"],
    "S029": ["two employers, two sub-cases (C2): Evan (from 1 January 2026, £150.00) and Felix (from 4 May 2026, "
             "£100.00); deemed 5 January - 22 July 2026 under each contract"],
    "S015": ["the stated gap (3 March - 27 April 2026) is the N span between the two deemed intervals"],
    "S016": ["the stated gap (3 March - 28 April 2026) is the N span between the two deemed intervals"],
    "S024": ["the stated gap (18 July - 11 September 2026) is the N span between the two deemed intervals"],
    "S025": ["the stated gap (18 July - 12 September 2026) is the N span between the two deemed intervals"],
    "S026": ["the stated gaps (12 January - 8 March, 16 March - 10 May 2026) are the N spans between the deemed intervals"],
    "S018": ["'brought to an end by mutual agreement on 5 May 2026': contract end 2026-05-05"],
}
for _cid in S:
    NOTES.setdefault(_cid, []).append("N span bounds next to a stated interval (the day before its first day, the day "
                                      "after its last) are the edges of 'outside the stated intervals' (a copy)")
# In-scope cases the vocabulary cannot state: case id -> (reason, [qids]).
UNSUPPORTED = {}

# self-check of the computed weekdays (datetime): every anchor's stated index matches the calendar
for _cid, _ans in _ANCHOR.items():
    for _d, _j in _ans:
        assert (dt.date.fromisoformat(_d).weekday() + 1) % 7 == _j, (_cid, _d, _j)
assert dt.date.fromisoformat(WLO).weekday() == 6 and dt.date.fromisoformat(WHI).weekday() == 5


# ---- do not edit below ---------------------------------------------------------------------------------------------
def _build():
    cases, probes, probe_qids = [], {}, {}
    for cid, c in ENC.items():
        if c["scope"] == "out":
            probes[cid] = "out-of-scope probe (questions-enc.jsonl scope 'out')"
            probe_qids[cid] = [q["qid"] for q in c["questions"]]
            continue
        if cid in UNSUPPORTED:
            continue
        by_emp = {}
        for q in c["questions"]:
            emp, form, args = parse_q(q["text"])
            by_emp.setdefault(emp, []).append({"qid": q["qid"], "form": form, **args})
        subs = []
        for emp, qs in by_emp.items():
            contract, spans, weekly, anchor = S[cid][emp]
            asked = sorted({q["date"] for q in qs if q["form"] in ("pay", "amount")})
            runs = sorted({(q["first"], q["last"]) for q in qs if q["form"] == "run"})
            spec = Spec(f"{cid}/{emp}", contract, spans, weekly, anchor, asked=asked, runs=runs)
            subs.append({"employer": emp, "spec": spec, "questions": qs})
        cases.append({"id": cid, "subs": subs, "judgement": JUDGEMENT.get(cid, []),
                      "calendar": CALENDAR.get(cid, [])})
    return cases, probes, probe_qids


CASES, PROBES, PROBE_QIDS = _build()
