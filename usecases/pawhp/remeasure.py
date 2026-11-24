"""date-arith-remeasure (manage-agents reviews/dri-ruling-date-arith-20261123.md item 3): PAWHP (SSI 2024/351), BEFORE and AFTER.

Measurement only, on scratch branch remeasure-pawhp-1124 (after-release e22d9ce609, which contains the frozen run commit
873c9ea940, with the frozen run's usecases/pawhp files restored). Wraps run.py / encode.py; changes no rule, case or key.

BEFORE (--before): the audit's bridge flips (audit-pawhp.md section (a), first row), rebuilt: the staged route without the Lean
replay, the bridge output changed one way at a time (the applicant's pensionable-age date moved to 1970-01-01 / 2099-12-31;
the applicant's 80th birthday likewise; another person's reached-pensionable-age and reached-80 flags flipped). A counted
answer that changes rests on the bridge.

AFTER (--after): the bridge facts the merged written form (ve/surface/dates.py) can write are replaced by the Act's own rules,
lowered by it to `cal` / `cal_cmp` nodes Lean evaluates:
  Pensions Act 1995 Sch. 4 para. 1 (the rules that name an age; the shell copies the rules for the person's stated sex):
    man   "If the birth date of P is before 6 December 1953, then P's date is the day P attains the age of 65 years."
    woman "If the birth date of P is before 6 April 1950, then ... 60 years."
    any   "If the birth date of P is after 5 October 1954 and the birth date of P is before 6 April 1960, then ... 66 years."
    any   "If the birth date of P is after 5 March 1961 and the birth date of P is before 6 April 1977, then ... 67 years."
    any   "If the birth date of P is after 5 April 1978, then ... 68 years."
  applicant_pa_date: the conjunction of those rules (implies(range, eq(applicant_pa_date, cal ...))).
  other P reached_pa: conjunction of implies(range, reached_pa(P) iff "P has attained the age of N on the last day of the week
    beginning the third Monday in September 2026") (reg. 2 qualifying week; reg. 6).
  applicant_eightieth: "the day the applicant attains the age of 80 years" (reg. 10).
  other P reached_80: iff "P has attained the age of 80 on the last day of the week beginning the third Monday in September 2026".
Stays the bridge: a pensionable-age date or flag for a birth in a table 1-4 period (the tables; (7A) dates sit in table 3's
span). The rows' own week constants (rows_v2.py QW0, QW1, QW_MINUS_12W, hand-worked) are not in the audit's bridge count and
are left as they were. --after-cf repeats the BEFORE flips on the AFTER encoding.
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

R = T.R
D = dt.date
MECHS = ("pa_past", "pa_future", "e80_past", "e80_future", "reached_pa", "reached_80")
FAR_PAST, FAR_FUTURE = "1970-01-01", "2099-12-31"
TABLES = ((D(1950, 4, 6), D(1953, 12, 5), "table 1", "F"), (D(1953, 12, 6), D(1954, 10, 5), "table 2", None),
          (D(1960, 4, 6), D(1961, 3, 5), "table 3 / (7A)", None), (D(1977, 4, 6), D(1978, 4, 5), "table 4", None))
WEEK_END = "the last day of the week beginning the third Monday in September 2026"
RULES = (("M", "the birth date of {p} is before 6 December 1953", 65),
         ("F", "the birth date of {p} is before 6 April 1950", 60),
         (None, "the birth date of {p} is after 5 October 1954 and the birth date of {p} is before 6 April 1960", 66),
         (None, "the birth date of {p} is after 5 March 1961 and the birth date of {p} is before 6 April 1977", 67),
         (None, "the birth date of {p} is after 5 April 1978", 68))


def perturb(births, mech):
    births = copy.deepcopy(births)
    for b in births:
        if mech in ("pa_past", "pa_future"):
            b["pa_date"] = [FAR_PAST if mech == "pa_past" else FAR_FUTURE for _ in b["pa_date"]]
        elif mech in ("e80_past", "e80_future"):
            b["eightieth"] = FAR_PAST if mech == "e80_past" else FAR_FUTURE
        elif mech == "reached_pa" and isinstance(b["reached_pa_by_week_end"], bool):
            b["reached_pa_by_week_end"] = not b["reached_pa_by_week_end"]
        elif mech == "reached_80":
            b["reached_80_by_week_end"] = not b["reached_80_by_week_end"]
    return births


def table_of(born, sex):
    d = D.fromisoformat(born)
    for lo, hi, name, only in TABLES:
        if lo <= d <= hi and (only is None or sex == only):
            return name
    return None


_ENV = None


def env():
    global _ENV
    if _ENV is None:
        _ENV = Environment(T.environment())
    return _ENV


def one(it, text):
    readings = it.conditions(text)
    if len(readings) != 1:
        raise DA.DateRuleError(f"{len(readings)} readings: {text!r}")
    return readings[0]


def ground(it, text):
    kind, e = it.date(text)
    if kind != "ground":
        raise DA.DateRuleError(f"not a ground date: {text!r}")
    return ["cal", e]


def written(case):
    """{fact id: (prose list, formula)} for the bridge facts the written form can write; {fact id: reason} for the rest."""
    out, still = {}, {}
    for p in case["people"]:
        c = p["c"]
        if p.get("b") is None:
            continue
        b = E.BRIDGES[case["id"]][p["b"]]
        it = DA._Item(env(), {"dates": {f"the birth date of {c}": b["born"]}}, (), None, [c])
        tab = table_of(b["born"], p.get("sex"))
        rules = [(cond.format(p=c), age) for sex, cond, age in RULES
                 if sex is None or sex == p.get("sex")]
        if c == "applicant":
            if tab:
                still["applicant.pa_date"] = tab
            else:
                prose, parts = [], []
                for cond, age in rules:
                    when = f"the day {c} attains the age of {age} years"
                    prose.append(f"If {cond}, then the applicant's pensionable-age date is {when}.")
                    parts.append(R.Implies(one(it, cond), ["eq", R.ci("applicant_pa_date"), ground(it, when)]))
                out["applicant.pa_date"] = (prose, R.And(*parts))
            when = f"the day {c} attains the age of 80 years"
            out["applicant.eightieth"] = ([f"the applicant's 80th birthday is {when}"],
                                          ["eq", R.ci("applicant_eightieth"), ground(it, when)])
        else:
            if tab:
                still[f"{c}.reached_pa"] = tab
            else:
                prose, parts = [], []
                for cond, age in rules:
                    reached = f"{c} has attained the age of {age} on {WEEK_END}"
                    prose.append(f"If {cond}, then ({c} has reached pensionable age by the week's end iff {reached}).")
                    parts.append(R.Implies(one(it, cond), R.Iff(R.U("reached_pa", c), one(it, reached))))
                out[f"{c}.reached_pa"] = (prose, R.And(*parts))
            reached = f"{c} has attained the age of 80 on {WEEK_END}"
            out[f"{c}.reached_80"] = ([f"{c} has reached 80 by the week's end iff {reached}"],
                                      R.Iff(R.U("reached_80", c), one(it, reached)))
    return out, still


_ORIG_FACTS = E.facts
_STILL = {}


def facts_after(case):
    out, unknown = _ORIG_FACTS(case)
    w, still = written(case)
    new = [{"id": f["id"], "formula": w[f["id"]][1]} if f["id"] in w else f for f in out]
    _STILL[case["id"]] = still
    return new, unknown


def install_after():
    E.facts = facts_after


def staged_answers(prover, cases):
    return {c["id"]: RUN.run_case(prover, c)[0] for c in cases}


def counterfactual(cases):
    prover = RUN.Prover(env())
    base = staged_answers(prover, cases)
    real = copy.deepcopy(E.BRIDGES)
    out = {"base": base, "changed": {}}
    for mech in MECHS:
        try:
            for cid in real:
                E.BRIDGES[cid] = perturb(real[cid], mech)
            alt = staged_answers(prover, cases)
        finally:
            E.BRIDGES.update(copy.deepcopy(real))
        out["changed"][mech] = sorted(f"{cid}/{qq}" for cid in base for qq in base[cid]
                                      if alt[cid].get(qq) != base[cid][qq])
        print(mech, len(out["changed"][mech]), flush=True)
    return out


def main(argv):
    mode, path = argv[0], argv[1]
    cases = K.CASES
    if mode == "--before":
        res = counterfactual(cases)
    elif mode == "--after-cf":
        install_after()
        res = counterfactual(cases)
        res["still_bridged"] = _STILL
    elif mode == "--after":
        install_after()
        RUN.main(["--out", path, *argv[2:]])
        side = {}
        for c in cases:
            w, still = written(c)
            side[c["id"]] = {"written": {k: v[0] for k, v in w.items()}, "still_bridged": still}
        Path(path + ".written.json").write_text(json.dumps(side, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    else:
        raise SystemExit(__doc__)
    Path(path).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
