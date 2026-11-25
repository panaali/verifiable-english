"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions (Codex writer).

Encoder: dri-statute-corpus-opm-fegli-premiums-w-1124 (Opus 5.5), after the translation was committed (644ad56d3b). Each
in-scope question is one sub-case: the enrollee, the one period it asks about, the coverages it names, and the case's
stated facts for them, transcribed by hand (encode.Sub; conventions E1-E4 there). The question's form names the atom or
value that answers it. "judgement": anything the encoder decided beyond copying a stated fact (listed as "encoder
judgement" on RESULT.md).
PROBES: out-of-scope cases (scope "out": every answer UNSUPPORTED). UNSUPPORTED: none.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from encode import Sub

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "f4dc55fede68b2b655717175efac6e8d765a416ddfcfdfa83efecff68d6dfb39"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

CASES = []
_by = {}


def add(qid, sub, form):
    cid = qid.split("-")[0]
    if cid not in _by:
        _by[cid] = {"id": cid, "subs": [], "judgement": []}
        CASES.append(_by[cid])
    _by[cid]["subs"].append({"spec": sub, "questions": [{"qid": qid, "form": form}]})
    for j in sub.judgement:
        if j not in _by[cid]["judgement"]:
            _by[cid]["judgement"].append(j)


BW, MO = True, False
TOT = ("amt", "tot", "t")


def emp(start, age, bw):
    """A federal employee with Basic insurance, one period (E1: a named month = its first day, not biweekly)."""
    return Sub().fact("emp").fact("ann", val=False).fact("basic").period(start, age, bw)


def ann(start, age, nrb, nrc):
    """An eligible annuitant (Options A, B, C only), one calendar month."""
    return Sub().fact("ann").fact("emp", val=False).fact("nrb", val=nrb).fact("nrc", val=nrc).period(start, age, MO)


def emp_all(start, age, bw, b, c):
    return emp(start, age, bw).cov("basic", "100000.00").cov("opta").cov("optb", b).cov("optc", multiples=c)


def ann_abc(start, age, b, c, nr):
    return ann(start, age, nr, nr).cov("opta").cov("optb", b).cov("optc", multiples=c)


def abasic(start, bd, col, s75=None, canc=False, basic_cov=True):
    """An eligible annuitant's Basic (E4): the elected reduction, a later 75% election, cancellation, 65th birthday."""
    s = Sub().fact("ann").fact("emp", val=False).fact("basic", val=not canc)
    for r in ("r75", "r50", "rno"):
        s.fact(r, val=(r == col))
    s.fact("s75", val=s75 is not None).fact("canc", val=canc)
    if s75 is not None:
        s.val("sd", "p", s75)
    if bd is not None:
        s.val("bd", "p", bd)
    if start is not None:
        s.period(start, None, MO)
        if basic_cov:
            s.cov("basic", "100000.00")
    return s


# --- F001-F011: employees, every age group, biweekly and monthly ---------------------------------------------------------
add("F001-1", emp_all("2026-03-02", 34, BW, "10000.00", 1), TOT)
add("F001-2", emp_all("2026-03-01", 34, MO, "10000.00", 1), TOT)
add("F001-3", emp("2026-03-02", 34, BW).cov("basic", "100000.00"), ("amt", "pr", "b"))
add("F001-4", emp("2026-03-01", 34, MO).cov("basic", "100000.00"), ("amt", "pr", "b"))
add("F001-5", emp("2026-03-01", 34, MO), ("yn", "agechg", "p"))
add("F001-6", emp("2026-03-01", 34, MO), ("yn", "avgc", "p"))
add("F001-7", emp("2026-03-01", 34, MO), ("yn", "hlth", "p"))

add("F002-1", emp_all("2022-03-02", 35, BW, "30000.00", 3), TOT)
add("F002-2", emp_all("2026-03-01", 39, MO, "30000.00", 3), TOT)
add("F002-3", emp_all("2023-03-01", 36, MO, "30000.00", 3), TOT)
add("F002-4", emp("2022-03-02", 35, BW), ("yn", "xb", "t"))
add("F002-5", emp("2023-03-01", 36, MO), ("yn", "xb", "t"))
add("F002-6", emp("2022-03-02", 35, BW), ("yn", "xbcost", "p"))

add("F003-1", emp_all("2022-03-02", 40, BW, "10000.00", 1), TOT)
add("F003-2", emp_all("2026-03-01", 44, MO, "10000.00", 1), TOT)
add("F003-3", emp("2022-03-02", 40, BW), ("yn", "xb", "t"))
add("F003-4", emp("2026-03-01", 44, MO), ("yn", "xb", "t"))

add("F004-1", emp_all("2022-03-02", 45, BW, "30000.00", 3), TOT)
add("F004-2", emp_all("2026-03-01", 49, MO, "30000.00", 3), TOT)
add("F004-3", emp("2022-03-02", 45, BW), ("yn", "xb", "t"))

for cid, (a1, a2, b, c) in {"F005": (50, 54, "10000.00", 1), "F006": (55, 59, "30000.00", 3),
                            "F007": (60, 64, "10000.00", 1), "F008": (65, 69, "30000.00", 3),
                            "F009": (70, 74, "10000.00", 1), "F010": (75, 79, "30000.00", 3),
                            "F011": (80, 84, "10000.00", 1)}.items():
    add(f"{cid}-1", emp_all("2022-03-02", a1, BW, b, c), TOT)
    add(f"{cid}-2", emp_all("2026-03-01", a2, MO, b, c), TOT)

# --- F012-F022: annuitants, Options A, B, C by age; No Reduction from F019 ------------------------------------------------
add("F012-1", ann_abc("2026-02-01", 34, "10000.00", 1, False), TOT)
add("F012-2", ann_abc("2026-03-01", 34, "10000.00", 1, False), TOT)
add("F012-3", ann("2026-03-01", 34, False, False).cov("opta"), ("amt", "pr", "oa"))

add("F013-1", ann_abc("2022-03-01", 35, "30000.00", 4, False), TOT)
add("F013-2", ann_abc("2026-03-01", 39, "30000.00", 4, False), TOT)
add("F013-3", ann_abc("2023-03-01", 36, "30000.00", 4, False), TOT)

for cid, (a1, a2, b, c, nr) in {"F014": (40, 44, "10000.00", 1, False), "F015": (45, 49, "30000.00", 4, False),
                                "F016": (50, 54, "10000.00", 1, False), "F017": (55, 59, "30000.00", 4, False),
                                "F018": (60, 64, "10000.00", 1, False), "F019": (65, 69, "30000.00", 4, True),
                                "F020": (70, 74, "10000.00", 1, True), "F021": (75, 79, "30000.00", 4, True),
                                "F022": (80, 84, "10000.00", 1, True)}.items():
    add(f"{cid}-1", ann_abc("2022-03-01", a1, b, c, nr), TOT)
    add(f"{cid}-2", ann_abc("2026-03-01", a2, b, c, nr), TOT)
add("F018-3", ann("2026-03-01", 64, False, False).cov("optb", "10000.00"), ("amt", "pr", "ob"))
add("F019-3", ann("2022-03-01", 65, True, True).cov("opta"), ("yn", "free", "oa"))
add("F022-3", ann("2026-03-01", 84, True, True).cov("optc", multiples=1), ("amt", "pr", "oc"))

# --- F023-F028: annuitant Basic around the 65th birthday ------------------------------------------------------------------
for cid, (bd, col) in {"F023": ("2026-03-01", "r75"), "F024": ("2026-03-31", "r75"), "F025": ("2026-03-01", "r50"),
                       "F026": ("2026-03-31", "r50"), "F027": ("2026-03-01", "rno"), "F028": ("2026-03-31", "rno")}.items():
    for qn, month in (("1", "2026-03-01"), ("2", "2026-04-01"), ("3", "2026-09-01")):
        add(f"{cid}-{qn}", abasic(month, bd, col), ("amt", "pr", "b"))   # F023-3: the outside in-force amount (E3)

# --- F029-F031: annuitants 65+ and the No Reduction exceptions -------------------------------------------------------------
add("F029-1", ann("2026-03-01", 65, False, False).cov("opta"), ("amt", "pr", "oa"))
add("F029-2", ann("2026-03-01", 65, False, False).cov("optb", "10000.00"), ("amt", "pr", "ob"))
add("F029-3", ann("2026-03-01", 65, False, False).cov("optc", multiples=2), ("amt", "pr", "oc"))
add("F030-1", ann("2026-03-01", 70, False, True).cov("optb", "20000.00"), ("amt", "pr", "ob"))
add("F030-2", ann("2026-03-01", 70, False, True).cov("optc", multiples=3), ("amt", "pr", "oc"))
add("F031-1", ann("2026-03-01", 75, True, False).cov("optb", "10000.00"), ("amt", "pr", "ob"))
add("F031-2", ann("2026-03-01", 75, True, False).cov("optc", multiples=1), ("amt", "pr", "oc"))

# --- F032-F033: for life, cancellation, a later 75% Reduction ---------------------------------------------------------------
add("F032-1", abasic(None, "2025-03-31", "r50", canc=True), ("yn", "life", "p"))
add("F033-1", abasic(None, "2025-03-01", "rno", s75="2026-02-01"), ("yn", "life", "p"))
add("F033-2", abasic("2026-03-01", "2025-03-01", "rno", s75="2026-02-01"), ("amt", "pr", "b"))

# --- F034-F035: the rate dates; employee totals; annuitant Basic ------------------------------------------------------------
add("F034-1", emp("2021-09-30", 36, BW), ("yn", "rap", "t"))
add("F034-2", emp("2021-10-01", 36, BW), ("yn", "rap", "t"))
add("F034-3", emp("2026-03-02", 41, BW), ("yn", "rap", "t"))
add("F034-4", emp("2026-03-01", 41, MO).cov("basic", "100000.00").cov("opta"), TOT)
add("F034-5", emp("2026-03-01", 41, MO).cov("basic", "100000.00").cov("optb", "20000.00"), TOT)
add("F034-6", emp("2026-03-01", 41, MO).cov("basic", "100000.00").cov("optc", multiples=3), TOT)


def iris_period(start):
    return Sub().fact("ann").fact("emp", val=False).period(start, None, BW)


add("F035-1", iris_period("2021-09-30"), ("yn", "rap", "t"))
add("F035-2", iris_period("2021-10-01"), ("yn", "rap", "t"))
add("F035-3", iris_period("2026-03-02"), ("yn", "rap", "t"))
add("F035-4", abasic(None, "2025-03-31", "r50"), ("yn", "life", "p"))
add("F035-5", abasic(None, "2025-03-31", "r50"), ("yn", "post65", "p"))
add("F035-6", abasic("2026-03-01", "2025-03-31", "r50"), ("amt", "pr", "b"))

# --- probes -------------------------------------------------------------------------------------------------------------
PROBES = {cid: "scope 'out' in questions-enc.jsonl (D12)" for cid in
          ("F036", "F037", "F038", "F039", "F040", "F041", "F042", "F043", "F044", "F045")}
PROBE_QIDS = {cid: [f"{cid}-1"] for cid in PROBES}
UNSUPPORTED = {}
