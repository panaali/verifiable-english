"""date-arith-remeasure (manage-agents reviews/dri-ruling-date-arith-20261123.md item 3): release B (Winter Fuel Payment),
same-family round V001-V050 (manage-agents reviews/relb/indq-v), BEFORE and AFTER. Measurement only.

Scratch branch remeasure-relb-1124: after-release e22d9ce609 (it contains the frozen translation commit 94a1826b0f17) with the
frozen usecases/eligibility files restored. The frozen runner is reviews/relb/indq-v/encoded/run_v.py; this file repeats its
--run path (the staged route, every step certificate and answer document sent to Lean, an answer counts only if Lean admits
its document) with one change in --after: the bridge B2/B3 facts the merged written form (ve/surface/dates.py) can write are
replaced by the Act's own rules, lowered to `cal` / `cal_cmp` nodes Lean evaluates:
  B2 <role>_pa_date: Pensions Act 1995 Sch. 4 para. 1, the rules that name an age (the shell copies them for the sex the
     encoder's bridge basis states; a person of unstated sex gets only the rules that apply to "a person"):
       man   "If the birth date of R is before 6 December 1953, then R's pensionable-age date is the day R attains the age of 65 years."
       woman "If the birth date of R is before 6 April 1950, then ... 60 years."
       any   "If the birth date of R is after 5 October 1954 and the birth date of R is before 6 April 1960, then ... 66 years."
       any   "If the birth date of R is after 5 March 1961 and the birth date of R is before 6 April 1977, then ... 67 years."
       any   "If the birth date of R is after 5 April 1978, then ... 68 years."
     as implies(range, date_on(<role>_pa_date, cal ...)), one per rule.
  B3 <role>_eightieth: "the day R attains the age of 80 years".
Stays the bridge, with the reason: a birth in a table 1-4 period (tables; the (7A) dates lie in table 3's span); a birth
before 6 December 1953 whose sex the question does not state (the translation's own bound); a 29 February birth (no reading
in the text; the build refuses it). BEFORE is structural, as the round's GRADES.md: an answer rests on a bridge when any
person of its profile has an encoder-added B2 or B3 value (run_v.py's bridge log "added").

usage (repository root): uv run --frozen python -B usecases/eligibility/remeasure_relb.py <inputs.json> --before OUT.json
                         uv run --frozen python -B usecases/eligibility/remeasure_relb.py <inputs.json> --after OUT.json
"""
import datetime as dt
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import translation as T  # noqa: E402
import run as R  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.surface import dates as DA  # noqa: E402

D = dt.date
TABLES = ((D(1950, 4, 6), D(1953, 12, 5), "table 1", "F"), (D(1953, 12, 6), D(1954, 10, 5), "table 2", None),
          (D(1960, 4, 6), D(1961, 3, 5), "table 3 / (7A)", None), (D(1977, 4, 6), D(1978, 4, 5), "table 4", None))
RULES = (("M", "the birth date of {p} is before 6 December 1953", 65),
         ("F", "the birth date of {p} is before 6 April 1950", 60),
         (None, "the birth date of {p} is after 5 October 1954 and the birth date of {p} is before 6 April 1960", 66),
         (None, "the birth date of {p} is after 5 March 1961 and the birth date of {p} is before 6 April 1977", 67),
         (None, "the birth date of {p} is after 5 April 1978", 68))


def load(inputs_path):
    """run_v.py's bridge step: add the encoder's B2/B3 values the frozen tables lack. Returns the bridge log and sexes."""
    inputs = json.loads(Path(inputs_path).read_text(encoding="utf-8"))
    log, sex = {}, {}
    for birth, b in sorted(inputs["bridges"].items()):
        mine = [tuple(v) for v in b["variants"]]
        basis = b.get("basis", [])
        sex[birth] = basis[0].split(":", 1)[0] if len(basis) == 1 else "unstated"
        if birth in T.PENSIONABLE_AGE:
            log[birth] = {"pa": "own"}
        else:
            assert len(mine) == 1, birth
            T.PENSIONABLE_AGE[birth] = mine[0]
            log[birth] = {"pa": "added"}
        if birth in T.EIGHTIETH:
            log[birth]["eightieth"] = "own"
        else:
            T.EIGHTIETH[birth] = b["eightieth"]
            log[birth]["eightieth"] = "added"
    return inputs, log, sex


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


def pa_status(birth, sex):
    d = D.fromisoformat(birth)
    if (d.month, d.day) == (2, 29):
        return "29 February birth: no reading in the text (refused by the build)"
    for lo, hi, name, only in TABLES:
        if lo <= d <= hi and (only is None or sex == only):
            return name
    if d < D(1953, 12, 6) and sex not in ("F", "M"):
        return "sex not stated before 6 December 1953 (the translation's own bound)"
    return None


def written(role, birth, sex):
    """(pa formula or None, pa reason, pa prose, 80th formula or None, 80th reason, 80th prose)."""
    it = DA._Item(env(), {"dates": {f"the birth date of {role}": birth}}, (), None, [role])
    why = pa_status(birth, sex)
    pa = prose = None
    if why is None:
        parts, prose = [], []
        for s, cond, age in RULES:
            if s is not None and s != sex:
                continue
            c = cond.format(p=role)
            when = f"the day {role} attains the age of {age} years"
            prose.append(f"If {c}, then {role}'s pensionable-age date is {when}.")
            parts.append(["implies", one(it, c), ["date_on", T.num(role, "pa_date"), ground(it, when)]])
        pa = parts[0]
        for p in parts[1:]:
            pa = ["and", pa, p]
    d = D.fromisoformat(birth)
    if (d.month, d.day) == (2, 29):
        return pa, why, prose, None, "29 February birth: no reading in the text (refused by the build)", None
    when = f"the day {role} attains the age of 80 years"
    return pa, why, prose, ["date_on", T.num(role, "eightieth"), ground(it, when)], None, f"{role}'s 80th birthday is {when}"


SEX = {}
STATUS = {}
_ORIG_ROLE_FACTS = T.role_facts


def role_facts_after(r, p, other_present, housemate=None):
    facts = _ORIG_ROLE_FACTS(r, p, other_present, housemate)
    if p is None:
        return facts
    pa, why, prose, e80, why80, prose80 = written(r, p["birth"], SEX.get(p["birth"], "unstated"))
    STATUS.setdefault(CURRENT[0], {})[r] = {"birth": p["birth"], "pa": prose if pa else why, "eightieth": prose80 or why80}
    out = []
    for f in facts:
        if f["id"] == f"{r}.pa_date" and pa is not None:
            f = T.fact(f["id"], pa, "written")
        elif f["id"] == f"{r}.eightieth" and e80 is not None:
            f = T.fact(f["id"], e80, "written")
        out.append(f)
    return out


CURRENT = [None]


def before(inputs, log):
    rows = {}
    for case in inputs["cases"]:
        added = []
        for role in ("applicant", "housemate"):
            p = case.get(role)
            if p and p.get("birth"):
                lg = log[p["birth"]]
                if lg["pa"] == "added" or lg["eightieth"] == "added":
                    added.append(f"{role} {p['birth']}")
        rows[case["id"]] = added
    return rows


def run(inputs, out_path):
    raw_env = T.environment()
    env_ = env()
    defaults = inputs["defaults"]
    prover = R.Prover(env_)
    records, lean_cases = [], []
    started = time.time()
    for case in inputs["cases"]:
        CURRENT[0] = case["id"]
        result, staged = R.run_profile(prover, env_, case, defaults)
        records.append({"id": case["id"], "staged": result["staged"]})
        for step in staged.steps.values():
            lean_cases.append({"id": f"{case['id']}/cert/{step['name']}", "kind": "certificate",
                               "environment": raw_env, "premises": [T.q(staged.formula(n)) for n in step["premises"]],
                               "conclusion": T.q(step["formula"]), "certificate": step["certificate"]})
        for question, target in R.answer_targets(result["staged"]).items():
            lean_cases.append({"id": f"{case['id']}/doc/{question}", "kind": "document",
                               "environment": raw_env, "document": staged.document(target)})
    lean_results = {r["id"]: r for r in R.lean(lean_cases)}
    for rec in records:
        pid = rec["id"]
        mine = {k: v for k, v in lean_results.items() if k.startswith(pid + "/")}
        certs = [v for k, v in mine.items() if "/cert/" in k]
        docs = {k.rsplit("/", 1)[1]: v for k, v in mine.items() if "/doc/" in k}
        rec["lean"] = {"certificates": len(certs),
                       "certificates_accepted": sum(r.get("status") == "ok" and r.get("valid") is True for r in certs),
                       "documents": {q: r.get("status") == "ok" and r.get("assurance") == "lean-admitted"
                                     for q, r in sorted(docs.items())}}
        answers = dict(rec["staged"])
        for question, admitted in rec["lean"]["documents"].items():
            if not admitted:
                answers[question] = "OPEN"
                rec.setdefault("lean_rejected", []).append(question)
        rec["answers"] = answers
        rec["dates"] = STATUS.get(pid, {})
    out = {"format": "relb-indq-v-remeasure@1", "environment_id": env_.environment_id, "profiles": records,
           "lean_cases": len(lean_cases), "seconds": round(time.time() - started)}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    Path(out_path).write_text(text, encoding="utf-8")
    print("run file", out_path, hashlib.sha256(text.encode()).hexdigest(), "seconds", out["seconds"])


def main(argv):
    inputs, log, sex = load(argv[0])
    SEX.update(sex)
    if argv[1] == "--before":
        Path(argv[2]).write_text(json.dumps(before(inputs, log), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    elif argv[1] == "--after":
        T.role_facts = role_facts_after
        run(inputs, argv[2])
    elif argv[1] == "--frozen-replay":
        run(inputs, argv[2])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
