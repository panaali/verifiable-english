"""date-arith-remeasure (manage-agents reviews/dri-ruling-date-arith-20261123.md item 3): 14 CFR 61.23, BEFORE and AFTER.

Measurement only, on scratch branch remeasure-faa-medical-1124 (frozen evidence commit 5a7c862e71 + after-release e22d9ce609).
Nothing here changes rows.py, translation.py, cases.py, run.py, encode.py or the bridge; this file wraps them.

BEFORE (--before): the audit's counterfactual (audit-faa-medical.md section (a)) rebuilt: the staged route without the Lean
replay, the bridge output changed one mechanism at a time (age under 40 flipped; the 60th birthday moved far into the past and
far into the future; every month end and window moved to the day before D and far after D; the "later" order reversed; after
2006 flipped). A graded answer that changes rests on that mechanism.

AFTER (--after): every bridged date fact is replaced by the law's own date rule, written in the merged written form
(ve/surface/dates.py) and lowered by it to `cal` / `cal_cmp` nodes that Lean evaluates while decoding:
  certN_endK       "the last day of the Kth month after the month of the date of examination of certN"     ((d) table)
  sixtieth         "the day the pilot attains the age of 60 years"                                          ((a)(1)(iii), (d)(1)(ii))
  course_end24     "the last day of the 24th month after the month of the date of the 68.3 course"          ((c)(3)(i)(C))
  basic_exam_end48 "the last day of the 48th month after the month of the date of the comprehensive examination" ((c)(3)(i)(D))
  under40_exam(k)  iff "the pilot is under the age of 40 on the date of examination of k"                   ((d) table)
  after_2006(k)    iff "the date of examination of k is after 14 July 2006"                                  ((c)(3)(i)(B))
  later(x, y)      iff "the date of examination of x is after the date of examination of y"                 ((c)(3)(ii) most recent)
  app_later(x, y)  iff "the date of application of x is after the date of application of y"                 ((c)(3)(ii) most recent)
The case dates (birth, examination, application, course, comprehensive examination, D) stay the encoder's transcriptions,
as before. The expiry / last-day candidate days (an untrusted search hint) are read from Lean's own elaboration of the
lowered terms, not from the bridge. --after-cf then repeats the BEFORE perturbations on the AFTER encoding.

usage (repository root): uv run --frozen python -B usecases/faa-medical/remeasure.py --before OUT.json
                         uv run --frozen python -B usecases/faa-medical/remeasure.py --after OUT-RUN.json [--mutants]
                         uv run --frozen python -B usecases/faa-medical/remeasure.py --after-cf OUT.json
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

import cases as K  # noqa: E402
import encode as E  # noqa: E402
import run as RUN  # noqa: E402
import translation as T  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.surface import dates as DA  # noqa: E402
from ve.units import elaborate_quantity  # noqa: E402

R = T.R
MECHS = ("under40", "sixtieth_past", "sixtieth_future", "ends_before", "ends_after", "later", "after2006")
GROUP = {"under40": "age under 40", "sixtieth_past": "60th birthday", "sixtieth_future": "60th birthday",
         "ends_before": "month ends and windows", "ends_after": "month ends and windows", "later": "which record is later",
         "after2006": "after 14 July 2006"}
FAR_PAST, FAR_FUTURE = "1971-01-01", "2099-12-31"
ORD = {6: "6th", 12: "12th", 24: "24th", 48: "48th", 60: "60th"}


def perturb(b, mech):
    b = copy.deepcopy(b)
    day_before = (dt.date.fromisoformat(b["flight_day"]) - dt.timedelta(days=1)).isoformat()
    if mech == "under40":
        for rec in b["certs"].values():
            if "under40_exam" in rec:
                rec["under40_exam"] = not rec["under40_exam"]
    elif mech in ("sixtieth_past", "sixtieth_future") and "sixtieth" in b:
        b["sixtieth"] = FAR_PAST if mech == "sixtieth_past" else FAR_FUTURE
    elif mech in ("ends_before", "ends_after"):
        v = day_before if mech == "ends_before" else FAR_FUTURE
        for rec in b["certs"].values():
            for n in (6, 12, 24, 60):
                rec[f"end{n}"] = v
        for k in ("course_end24", "basic_exam_end48"):
            if k in b:
                b[k] = v
    elif mech == "later":
        b["later"] = [[y, x] for x, y in b["later"]]
        b["app_later"] = [[y, x] for x, y in b["app_later"]]
    elif mech == "after2006":
        for rec in b["certs"].values():
            rec["after_2006"] = not rec["after_2006"]
    return b


# --- AFTER: the written forms ---------------------------------------------------------------------------------------

_ENV = None


def env():
    global _ENV
    if _ENV is None:
        _ENV = Environment(T.environment())
    return _ENV


def case_dates(case, b):
    d = {"the flight day": b["flight_day"]}
    if b.get("birth"):
        d["the birth date of the pilot"] = b["birth"]
    for k, rec in b["certs"].items():
        d[f"the date of examination of {k}"] = rec["exam"]
    for k, rec in b["apps"].items():
        d[f"the date of application of {k}"] = rec["day"]
    if b.get("course_day"):
        d["the date of the 68.3 course"] = b["course_day"]
    if b.get("basic_exam_day"):
        d["the date of the comprehensive examination"] = b["basic_exam_day"]
    return d


def item(case, b):
    return DA._Item(env(), {"dates": case_dates(case, b)}, (), None, ["the pilot"])


def lowered_term(it, text):
    kind, e = it.date(text)
    if kind != "ground":
        raise DA.DateRuleError(f"not a ground date: {text!r}")
    return ["cal", e]


def lowered_condition(it, text):
    readings = it.conditions(text)
    if len(readings) != 1:
        raise DA.DateRuleError(f"{len(readings)} readings: {text!r}")
    return readings[0]


def written(case, b):
    """{fact id: (prose, formula)} for every bridged fact of the case."""
    it = item(case, b)
    out = {}
    for k in sorted(case.get("certs", {})):
        for n in (6, 12, 24, 60):
            p = f"the last day of the {ORD[n]} month after the month of the date of examination of {k}"
            out[f"{k}.end{n}"] = (p, ["eq", R.ci(f"{k}_end{n}"), lowered_term(it, p)])
        if b.get("birth"):
            p = f"the pilot is under the age of 40 on the date of examination of {k}"
            out[f"{k}.under40_exam"] = (p, R.Iff(R.U("under40_exam", k), lowered_condition(it, p)))
        p = f"the date of examination of {k} is after 14 July 2006"
        out[f"{k}.after_2006"] = (p, R.Iff(R.U("after_2006", k), lowered_condition(it, p)))
    certs = sorted(case.get("certs", {}))
    for x in certs:
        for y in certs:
            if x != y:
                p = f"the date of examination of {x} is after the date of examination of {y}"
                out[f"{x}.later.{y}"] = (p, R.Iff(R.B("later", x, y), lowered_condition(it, p)))
    apps = sorted(case.get("apps", {}))
    for x in apps:
        for y in apps:
            if x != y:
                p = f"the date of application of {x} is after the date of application of {y}"
                out[f"{x}.app_later.{y}"] = (p, R.Iff(R.B("app_later", x, y), lowered_condition(it, p)))
    if b.get("birth"):
        p = "the day the pilot attains the age of 60 years"
        out["sixtieth"] = (p, ["eq", R.ci("sixtieth"), lowered_term(it, p)])
    if b.get("course_day"):
        p = "the last day of the 24th month after the month of the date of the 68.3 course"
        out["course_end24"] = (p, ["eq", R.ci("course_end24"), lowered_term(it, p)])
    if b.get("basic_exam_day"):
        p = "the last day of the 48th month after the month of the date of the comprehensive examination"
        out["basic_exam_end48"] = (p, ["eq", R.ci("basic_exam_end48"), lowered_term(it, p)])
    return out


# Reverted after the review seat (manage-agents reviews/spare/date-arith/remeasure/faa-review-out.txt): a rewritten sentence
# that says more or less than the source text goes back to its bridge and is counted as not moved.
REVERTED = {"after_2006": "W4 LESS: (c)(3)(i)(B) 'at any point after July 14, 2006, have held' read as 'examined after'",
            "later": "W7 LESS: 'most recently issued' ordered by examination date, strict (ties)",
            "app_later": "W8 MORE: 'most recent application' over every named application, no 'on or before D' bound"}


def reverted(fid):
    for k, why in REVERTED.items():
        if fid.endswith("." + k) or f".{k}." in fid:
            return why
    return None


_ORIG_FACTS, _ORIG_CAND = E.facts, E.candidate_days
_STILL = {}  # case id -> [(fact id, reason)] bridged facts left as they were


def facts_after(case):
    out, unknown = _ORIG_FACTS(case)
    b = E.bridges()[case["id"]]
    w = written(case, b)
    new, replaced = [], set()
    for f in out:
        if f["id"] in w and not reverted(f["id"]):
            new.append({"id": f["id"], "formula": w[f["id"]][1]})
            replaced.add(f["id"])
        else:
            new.append(f)
    bridged = {f["id"] for f in out if f["id"].endswith((".under40_exam", ".after_2006")) or ".later." in f["id"]
               or ".app_later." in f["id"] or f["id"] in ("sixtieth", "course_end24", "basic_exam_end48")
               or any(f["id"].endswith(f".end{n}") for n in (6, 12, 24, 60))}
    _STILL[case["id"]] = {fid: reverted(fid) or "not written" for fid in sorted(bridged - replaced)}
    return new, unknown


def _day_of(env_, formula):
    q, _ = elaborate_quantity(env_, RUN.q(formula))
    out = []

    def walk(x):
        if isinstance(x, list) and x:
            if x[0] == "date" and len(x) == 2 and isinstance(x[1], str):
                out.append(x[1])
            elif x[0] == "num" and len(x) == 3 and x[1] == "day":
                out.append((dt.date(1970, 1, 1) + dt.timedelta(days=int(x[2]))).isoformat())
            for y in x[1:]:
                walk(y)
    walk(q["formula"])
    return out


def candidates_after(case):
    """Candidate days for the expiry / dl_last / last_day steps: Lean's values of the lowered month ends (a search hint;
    each candidate is still certified by the prover and replayed by Lean)."""
    b = E.bridges()[case["id"]]
    w = written(case, b)
    days = set()
    for fid, (_, f) in w.items():
        if f[0] == "eq":
            days |= set(_day_of(env(), f))
    return sorted(days)


def install_after():
    E.facts = facts_after
    E.candidate_days = candidates_after


def staged_answers(prover, cases):
    return {c["id"]: RUN.run_case(prover, c)[0] for c in cases}


def counterfactual(cases):
    prover = RUN.Prover(env())
    base = staged_answers(prover, cases)
    real = dict(E.bridges())
    out = {"base": base, "changed": {}}
    for mech in MECHS:
        try:
            E._BRIDGES.clear()
            E._BRIDGES.update({cid: perturb(b, mech) for cid, b in real.items()})
            alt = staged_answers(prover, cases)
        finally:
            E._BRIDGES.clear()
            E._BRIDGES.update(real)
        out["changed"][mech] = sorted(f"{cid}/{qq}" for cid in base for qq in base[cid]
                                      if alt[cid].get(qq) != base[cid][qq])
        print(mech, len(out["changed"][mech]), flush=True)
    return out


def main(argv):
    mode, path = argv[0], argv[1]
    E.bridges()
    cases = K.CASES
    if mode == "--before":
        res = counterfactual(cases)
    elif mode == "--after-cf":
        install_after()
        res = counterfactual(cases)
        res["still_bridged"] = _STILL
    elif mode == "--after":
        install_after()
        extra = argv[2:]
        RUN.main(["--out", path, *extra])
        # the written sentences and the bridged facts left, beside the run file
        side = {c["id"]: {"written": {k: v[0] for k, v in written(c, E.bridges()[c["id"]]).items()},
                          "still_bridged": _STILL.get(c["id"])} for c in cases}
        Path(path + ".written.json").write_text(json.dumps(side, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    else:
        raise SystemExit(__doc__)
    Path(path).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
