"""Run VE on every Winter Fuel Payment profile and compare with the answer key.

Protocol: PLAN.md section 8. For each profile the premises are the rules of
translation.py and the profile's facts; the key is stripped before any premise is
built and is read only by `score`, after every answer is fixed.

1. Single shot: `prove_quantity` on all premises for Q1 (both polarities) and on
   bottom (consistency). Q2 to Q4 follow only a certified YES.
2. Staged fallback, run whenever single shot certifies no answer: each derived
   atom or amount is one step, proved from the rules that define it, the facts
   those rules mention, and earlier steps. The steps form a `documents@1` quantity
   document per answer, which Lean admits (`ve_quantity` case `document`).
3. Lean replays every certificate, and evaluates every premise in a fixture model
   built from the independent reference (non-vacuity).
4. Mutation check (PLAN section 8) on the staged route.

Usage: python run.py [--profiles A01,B02] [--no-single-shot] [--no-mutants] [--no-write]
Writes results.json and RESULTS.md beside this file (unless --no-write).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import date
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import translation as T  # noqa: E402
from ve.entailment import prove_entailment  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.units import _core_problem, elaborate_quantity, prove_quantity  # noqa: E402

LEAN = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_quantity"
STEP_CONSTANTS = ("amount", "recovered_amount", "kept")
LEVEL1 = ("reached_pa", "reached_80", "resident_in_week", "has_rb", "in_residential_care")
EXCLUSIONS = ("excluded_partner_benefit", "excluded_hospital", "excluded_custody",
              "excluded_care_benefit", "excluded_moved", "excluded_no_claim")


def q(formula):
    return T.q(formula)


def scan(formula, atoms, constants):
    """Collect predicate atoms (by key) and integer constant names in a formula."""
    if type(formula) is not list or not formula:
        return
    if formula[0] in ("unary", "binary"):
        atoms.add(T.key(formula))
        return
    if formula[0] == "const" and len(formula) == 3:
        constants.add(formula[2])
        return
    for part in formula[1:]:
        scan(part, atoms, constants)


CACHE = {}  # module level, so forked mutant workers inherit the baseline's searches


class Prover:
    """`prove_quantity` with a cache keyed by the exact problem."""

    def __init__(self, env):
        self.env, self.cache, self.calls, self.searches = env, CACHE, 0, 0

    def prove(self, premises, conclusion):
        self.calls += 1
        k = T.key([premises, conclusion])
        if k not in self.cache:
            self.searches += 1
            self.cache[k] = prove_quantity(self.env, [q(p) for p in premises], q(conclusion))
        return self.cache[k]


# --- single shot ---------------------------------------------------------------

def single_shot(env, rules, facts):
    """Whole-problem search: Q1 both ways and bottom. Records the search status."""
    premises = [q(f["formula"]) for f in facts] + [q(r["formula"]) for r in rules]
    out = {}
    for name, goal in (("entitled", T.entitled_goal()), ("not_entitled", T.entitled_goal(False)),
                       ("bottom", ["bottom"])):
        target, _, cores = _core_problem(env, premises, q(goal))
        result = prove_entailment(target, cores[:-1], cores[-1], max_steps=10_000)
        out[name] = {"status": result.status, "steps": result.steps,
                     "certified": result.certificate is not None}
    q1 = "YES" if out["entitled"]["certified"] else "NO" if out["not_entitled"]["certified"] else "OPEN"
    return {"searches": out, "Q1": q1}


# --- staged route ------------------------------------------------------------------

class Staged:
    def __init__(self, prover, rules, facts):
        self.prover = prover
        self.defs = {}
        for r in rules:
            for target in r["defines"]:
                self.defs.setdefault(target, []).append(r)
        self.fact_atoms, self.fact_constants = {}, {}
        for f in facts:
            atoms, constants = set(), set()
            scan(f["formula"], atoms, constants)
            for a in atoms:
                self.fact_atoms.setdefault(a, []).append(f)
            for c in constants:
                self.fact_constants.setdefault(c, []).append(f)
        self.leaves = {f"rule:{r['id']}": r["formula"] for r in rules}
        self.leaves.update({f"fact:{f['id']}": f["formula"] for f in facts})
        self.steps = {}  # target -> step
        self.log = []

    def premises_for(self, target):
        """Names of the premises of target's step: defining rules (and the rules
        fixing any integer constant they use), the facts they mention, and the
        established steps of the derived atoms and amounts they mention."""
        rules, seen, queue = [], set(), list(self.defs[target])
        atoms, constants = set(), set()
        while queue:
            r = queue.pop(0)
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rules.append(r)
            a, c = set(), set()
            scan(r["formula"], a, c)
            atoms |= a
            constants |= c
            for name in c:
                if name not in STEP_CONSTANTS and name in self.defs:
                    queue.extend(self.defs[name])
        facts, steps = [], []
        for a in sorted(atoms):
            if a == target:
                continue
            if a in self.defs:
                if a in self.steps:
                    steps.append(self.steps[a]["name"])
            else:
                facts += [f"fact:{f['id']}" for f in self.fact_atoms.get(a, [])]
        for c in sorted(constants):
            if c == target or c in self.defs and c not in STEP_CONSTANTS:
                continue
            if c in STEP_CONSTANTS:
                if c in self.steps:
                    steps.append(self.steps[c]["name"])
            else:
                facts += [f"fact:{f['id']}" for f in self.fact_constants.get(c, [])]
        facts = list(dict.fromkeys(facts))
        return facts + steps + [f"rule:{r['id']}" for r in rules]

    def formula(self, name):
        return self.leaves[name] if name in self.leaves else self.step_by_name[name]["formula"]

    @property
    def step_by_name(self):
        return {s["name"]: s for s in self.steps.values()}

    def attempt(self, target, label, candidates):
        names = self.premises_for(target)
        premises = [self.formula(n) for n in names]
        found = []
        for candidate in candidates:
            certificate = self.prover.prove(premises, candidate)
            if certificate is not None:
                found.append((candidate, certificate))
        entry = {"target": label, "premises": names, "certified": len(found)}
        self.log.append(entry)
        if len(found) == 1:
            candidate, certificate = found[0]
            self.steps[target] = {"name": f"step:{label}", "formula": candidate, "premises": names,
                                  "certificate": certificate}
            return candidate
        if len(found) > 1:
            entry["inconsistent"] = True
        return None

    def atom(self, formula, label):
        k = T.key(formula)
        result = self.attempt(k, label, [formula, T.Not(formula)])
        return None if result is None else result == formula

    def value(self, constant, candidates):
        result = self.attempt(constant, constant, [["eq", T.money_const(constant), T.gbp(v)]
                                                   for v in dict.fromkeys(candidates)])
        return None if result is None else result[2][2]

    def run(self):
        for r in T.ROLES:
            for p in LEVEL1:
                self.atom(T.U(p, r), f"{p}.{r}")
        for r in T.ROLES:
            self.atom(T.B("lives_with", r, T.OTHER[r]), f"lives_with.{r}")
        for r in T.ROLES:
            for p in EXCLUSIONS + ("excluded", "entitled"):
                self.atom(T.U(p, r), f"{p}.{r}")
        entitled = self.known(T.U("entitled", "applicant"))
        answers = {"Q1": {True: "YES", False: "NO", None: "OPEN"}[entitled]}
        if entitled is not True:
            fill = "N/A" if entitled is False else "OPEN"
            answers.update(Q2=fill, Q3=fill, Q4=fill)
            return answers
        amount = self.value("amount", T.AMOUNTS)
        recovered = self.atom(T.U("recovered", "applicant"), "recovered.applicant")
        answers["Q2"] = amount or "OPEN"
        answers["Q3"] = {True: "YES", False: "NO", None: "OPEN"}[recovered]
        if amount is None:
            answers["Q4"] = "OPEN"
            return answers
        self.value("recovered_amount", ["0.00", amount])
        kept = self.value("kept", [amount, "0.00"])
        answers["Q4"] = kept or "OPEN"
        return answers

    def known(self, formula):
        step = self.steps.get(T.key(formula))
        if step is None:
            return None
        return step["formula"] == formula

    def document(self, root_target, environment_units_start=0):
        """The `documents@1` quantity document whose root is a step: every step and
        leaf it rests on, leaves as asserted units in rule-then-fact order."""
        root = self.steps[root_target]
        by_name = self.step_by_name
        needed, stack = set(), [root["name"]]
        while stack:
            name = stack.pop()
            if name in needed:
                continue
            needed.add(name)
            if name in by_name:
                stack.extend(by_name[name]["premises"])
        leaf_names = [n for n in self.leaves if n in needed]
        units, nodes = [], []
        for i, name in enumerate(leaf_names):
            uid = "u" + str(i)
            units.append({"id": uid, "span": [i, i + 1], "kind": "asserted", "content": q(self.leaves[name])})
            nodes.append({"name": name, "quantity": q(self.leaves[name]), "unit": uid})
        for step in self.steps.values():  # established in dependency order
            if step["name"] in needed:
                nodes.append({"name": step["name"], "quantity": q(step["formula"]),
                              "premises": step["premises"], "certificate": step["certificate"]})
        return {"units": units, "graph": {"root": root["name"], "nodes": nodes}}


def answer_targets(answers):
    """The step targets whose documents carry each answered question."""
    out = {}
    if answers["Q1"] in ("YES", "NO"):
        out["Q1"] = T.key(T.U("entitled", "applicant"))
    if answers.get("Q2") not in (None, "OPEN", "N/A"):
        out["Q2"] = "amount"
    if answers.get("Q3") in ("YES", "NO"):
        out["Q3"] = T.key(T.U("recovered", "applicant"))
    if answers.get("Q4") not in (None, "OPEN", "N/A"):
        out["Q4"] = "kept"
    return out


# --- Lean ----------------------------------------------------------------------------

def lean(cases, limit=8 * 1024 * 1024):
    """Run cases through Lean `ve_quantity` in batches under its 16 MiB input limit."""
    batches, batch, size = [], [], 0
    for case in cases:
        n = len(json.dumps(case))
        if batch and size + n > limit:
            batches.append(batch)
            batch, size = [], 0
        batch.append(case)
        size += n
    if batch:
        batches.append(batch)
    results = []
    for part in batches:
        process = subprocess.run([str(LEAN), "-"], input=json.dumps(part), text=True,
                                 capture_output=True, timeout=1800)
        if process.returncode not in (0, 1):
            raise RuntimeError(process.stderr[:500])
        got = json.loads(process.stdout)
        assert [r["id"] for r in got] == [c["id"] for c in part]
        results += got
    return results


# --- fixture model from the independent reference (non-vacuity) ---------------------

def fixture_model(case_with_key, defaults):
    import reference as R
    absent = {"birth": "1970-08-19", "ew_from": None, "benefits": [], "income": "0.00"}
    p = R.person(case_with_key["applicant"], defaults)
    present = case_with_key["housemate"] is not None
    h = R.person(case_with_key["housemate"] if present else absent, defaults)
    people = {"applicant": p, "housemate": h}
    others = {"applicant": h if present else None, "housemate": p if present else None}
    relations = {name: [] for name in {**T.FACT_PREDICATES, **T.DERIVED_PREDICATES}}
    constants = {"applicant": "applicant", "housemate": "housemate", **{b: b for b in T.BENEFITS}}
    epoch = date(1970, 1, 1)
    dnum = lambda d: str((d - epoch).days)
    for r, x in people.items():
        o, other = T.OTHER[r], others[r]
        pa = T.PENSIONABLE_AGE[x["birth"].isoformat()]
        values = {"pa_date": date.fromisoformat(pa[1]), "eightieth": date.fromisoformat(T.EIGHTIETH[x["birth"].isoformat()]),
                  "ew_from": x["ew_from"], "ew_last_day": x["ew_last_day"], "scot_ni_from": x["scot_ni_from"]}
        if x["care"]:
            values["care_from"] = x["care"]["from"]
            constants[f"{r}_care_before_week"] = str((R.QW_START - x["care"]["from"]).days)
        if x["hospital"]:
            start = date.fromordinal(x["hospital"]["admitted"].toordinal() + 1)
            values.update(admitted=x["hospital"]["admitted"], discharged=x["hospital"]["discharged"],
                          treatment_start=start)
            constants[f"{r}_treatment_before_week"] = str((R.QW_START - start).days)
        if x["custody"]:
            values.update(custody_from=x["custody"]["from"], release=x["custody"]["release"])
        if x["claim"].get("claimed_on"):
            values["claim_date"] = x["claim"]["claimed_on"]
        for suffix, (unit, _) in T.ROLE_INTEGERS.items():
            name = f"{r}_{suffix}"
            if unit == "day":
                constants[name] = dnum(values[suffix]) if values.get(suffix) else "0"
            elif unit == "gbp_penny":
                constants[name] = str(int(x["income"] * 100))
            else:
                constants.setdefault(name, "0")
        facts = {"ever_resident_ew": x["ew_from"] is not None, "remains_resident_ew": x["ew_last_day"] is None,
                 "moved_to_scotland_or_ni": x["scot_ni_from"] is not None, "in_care_setting": x["care"] is not None,
                 "inpatient": x["hospital"] is not None, "detained_in_custody": x["custody"] is not None,
                 "under_sentence": bool(x["custody"] and x["custody"]["sentenced"]),
                 "claimed": x["claim"].get("claimed_on") is not None,
                 "paid_without_claim": x["claim"]["automatic"]}
        lives = R.lives_with(x, other)
        partners = present and h["partner"]  # cases.json records the couple on the housemate
        derived = {"reached_pa": R.reached_pensionable_age(x), "reached_80": R.reached_80(x),
                   "resident_in_week": R.resident_in_qw(x), "has_rb": R.relevant_benefit(x),
                   "in_residential_care": R.in_residential_care(x),
                   "excluded_partner_benefit": bool(other and partners and lives
                                                    and R.reached_pensionable_age(other) and R.relevant_benefit(other)),
                   "excluded_hospital": R.excluded_hospital(x), "excluded_custody": R.excluded_custody(x),
                   "excluded_care_benefit": R.in_residential_care(x) and R.relevant_benefit(x),
                   "excluded_moved": R.excluded_move(x), "excluded_no_claim": R.excluded_no_claim(x)}
        derived["excluded"] = any(derived[e] for e in EXCLUSIONS)
        derived["entitled"] = derived["reached_pa"] and derived["resident_in_week"] and not derived["excluded"]
        for name, value in {**facts, **derived}.items():
            if value:
                relations[name].append([r])
        for b in T.BENEFITS:
            if b in x["benefits"]:
                relations["paid_for_week"].append([r, b])
        if present:
            relations["shares_home"].append([r, o])
            if h["partner"]:
                relations["partner_of"].append([r, o])
            if lives:
                relations["lives_with"].append([r, o])
    got = R.answer(case_with_key, defaults)
    if got["entitled"]:
        amount = Decimal(got["amount"])
        recovered = got["recovered"]
        constants["amount"] = str(int(amount * 100))
        constants["recovered_amount"] = str(int(amount * 100) if recovered else 0)
        constants["kept"] = str(int(Decimal(got["kept"]) * 100))
        if recovered:
            relations["recovered"].append(["applicant"])
    else:
        constants.update(amount="0", recovered_amount="0", kept="0")
    return {"complete": True, "domains": {"person": ["applicant", "housemate"], "benefit": list(T.BENEFITS)},
            "relations": relations, "constants": constants}


# --- scoring (the only place the key is read) --------------------------------------

def score(answers, key):
    """Per scored question: True (correct), False (wrong). Q2 to Q4 are scored
    only when the key is entitled (PLAN section 3)."""
    expected = {"Q1": "YES" if key["entitled"] else "NO"}
    if key["entitled"]:
        expected.update(Q2=key["amount"], Q3="YES" if key["recovered"] else "NO", Q4=key["kept"])
    return {question: answers.get(question) == value for question, value in expected.items()}, expected


def run_profile(prover, env, case, defaults, mutant=None):
    staged = Staged(prover, T.rules(mutant), T.profile_facts(case, defaults))
    return {"staged": staged.run()}, staged


def _single_shot_task(case):
    data = T.load_cases()
    env = Environment(T.environment())
    return case["id"], single_shot(env, T.rules(), T.profile_facts(case, data["defaults"]))


def _mutant_task(item):
    mutant, cases, base = item
    data = T.load_cases()
    env = Environment(T.environment())
    prover = Prover(env)
    changed = [case["id"] for case in cases
               if run_profile(prover, env, case, data["defaults"], mutant=mutant)[0]["staged"] != base[case["id"]]]
    return mutant, changed


def pool_map(function, items, workers):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(function, items))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles")
    parser.add_argument("--no-single-shot", action="store_true")
    parser.add_argument("--no-mutants", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args(argv)
    started = time.time()
    raw_env = T.environment()
    env = Environment(raw_env)
    data = T.load_cases()  # keys stripped
    keyed = {c["id"]: c for c in T.load_cases(strip_keys=False)["cases"]}
    cases = data["cases"]
    if args.profiles:
        wanted = args.profiles.split(",")
        cases = [c for c in cases if c["id"] in wanted]
    prover = Prover(env)
    staged_runs = [(case, *run_profile(prover, env, case, data["defaults"])) for case in cases]
    single = {} if args.no_single_shot else dict(pool_map(_single_shot_task, cases, args.workers))
    profiles, lean_cases = [], []
    for case, result, staged in staged_runs:
        if case["id"] in single:
            result = {"single_shot": single[case["id"]], **result}
        record = {"id": case["id"], **result, "steps": [
            {k: v for k, v in e.items() if k != "premises"} | {"premise_count": len(e["premises"])}
            for e in staged.log]}
        profiles.append(record)
        for step in staged.steps.values():
            names = step["premises"]
            lean_cases.append({"id": f"{case['id']}/cert/{step['name']}", "kind": "certificate",
                               "environment": raw_env, "premises": [q(staged.formula(n)) for n in names],
                               "conclusion": q(step["formula"]), "certificate": step["certificate"]})
        for question, target in answer_targets(result["staged"]).items():
            lean_cases.append({"id": f"{case['id']}/doc/{question}", "kind": "document",
                               "environment": raw_env, "document": staged.document(target)})
        model = fixture_model(keyed[case["id"]], data["defaults"])
        premises = T.profile_facts(case, data["defaults"]) + T.rules()
        for item in premises:
            lean_cases.append({"id": f"{case['id']}/model/{item['id']}", "environment": raw_env,
                               "quantity": q(item["formula"]), "model": model})
    lean_results = {r["id"]: r for r in lean(lean_cases)}
    for record in profiles:
        pid = record["id"]
        mine = {k: v for k, v in lean_results.items() if k.startswith(pid + "/")}
        certs = [v for k, v in mine.items() if "/cert/" in k]
        docs = {k.rsplit("/", 1)[1]: v for k, v in mine.items() if "/doc/" in k}
        models = [v for k, v in mine.items() if "/model/" in k]
        record["lean"] = {
            "certificates": len(certs),
            "certificates_accepted": sum(r.get("status") == "ok" and r.get("valid") is True for r in certs),
            "documents": {question: r.get("status") == "ok" and r.get("assurance") == "lean-admitted"
                          for question, r in sorted(docs.items())},
            "model_premises": len(models),
            "model_premises_true": sum(r.get("status") == "ok" and r.get("value") is True for r in models),
            "model_premises_not_true": sorted(k.split("/model/")[1] for k, r in mine.items()
                                              if "/model/" in k and not (r.get("status") == "ok"
                                                                         and r.get("value") is True)),
        }
        answers = dict(record["staged"])
        # An answer counts only if Lean admitted its document; otherwise it is OPEN (a VE fault).
        for question, admitted in record["lean"]["documents"].items():
            if not admitted:
                answers[question] = "OPEN"
                record.setdefault("lean_rejected", []).append(question)
        record["answers"] = answers
        record["score"], record["key"] = score(answers, keyed[pid]["key"])
    mutants = {} if args.no_mutants else mutation_check(cases, profiles, args.workers)
    # Bridge B1 is a premise about two literals; certify it from no premises.
    b1 = prove_quantity(env, [], q(T.B1["formula"]))
    [b1_lean] = lean([{"id": "B1", "kind": "certificate", "environment": raw_env, "premises": [],
                       "conclusion": q(T.B1["formula"]), "certificate": b1}]) if b1 else [{}]
    english = english_facts(env, cases, data["defaults"])
    results = {"format": "wfp-eligibility-results@1", "environment_id": env.environment_id,
               "probes": probes(raw_env, env, profiles),
               "b1_certified": bool(b1) and b1_lean.get("valid") is True,
               "english": {"facts": len(english), "round_trip": sum(r["round_trip"] for r in english),
                           "rows": english},
               "profiles": profiles, "mutants": mutants,
               "prover": {"calls": prover.calls, "searches": prover.searches},
               "seconds": round(time.time() - started)}
    results["summary"] = summarize(results, keyed)
    if not args.no_write:
        text = json.dumps(results, indent=1, sort_keys=True) + "\n"
        (HERE / "results.json").write_text(text, encoding="utf-8")
        (HERE / "RESULTS.md").write_text(results_markdown(json.loads(text), keyed), encoding="utf-8")
        (HERE / "environment.json").write_text(json.dumps(raw_env, indent=1) + "\n", encoding="utf-8")
        (HERE / "rules.json").write_text(json.dumps({"format": "wfp-rules@1", "rules": T.rules()}, indent=1) + "\n",
                                         encoding="utf-8")
    print(json.dumps(results["summary"], indent=1))
    return results


def probes(raw_env, env, profiles):
    """Stage 0 probes P1 to P6 (PLAN section 8), each in Python and, where it is a
    statement, in Lean admission."""
    from ve.surface.time import parse_quantity_sentence, parse_w6_sentence, render_quantity_sentence

    def python(formula):
        try:
            elaborate_quantity(env, q(formula))
            return "admitted"
        except VEError as exc:
            return f"rejected: {exc}"

    def lean_admits(cases):
        got = lean([{"id": name, "environment": raw_env, "quantity": q(f)} for name, f in cases])
        return {r["id"]: "admitted" if r.get("status") == "ok" else f"rejected: {r.get('error')}" for r in got}

    out = {}
    p1 = ["date_no_later", T.num("applicant", "pa_date"), T.day("1960-06-27")]
    p2 = T.Implies(T.And(T.U("entitled", "applicant"), ["date_no_later", T.num("applicant", "claim_date"), T.day("2027-03-31")]),
                   ["lt", T.gbp("0.00"), T.money_const("amount")])
    p5a = ["elapsed_days", T.num("applicant", "care_from"), T.day(T.QW0), T.num("applicant", "care_before_week")]
    p5b = ["shift_days", T.num("applicant", "treatment_start"), T.num("applicant", "admitted"), "1"]
    got = lean_admits([("P1", p1), ("P2", p2), ("P5a", p5a), ("P5b", p5b)])
    out["P1"] = {"expected": "rejected, DateRange(1960-06-27)", "python": python(p1), "lean": got["P1"]}
    out["P2"] = {"expected": "admitted", "python": python(p2), "lean": got["P2"]}
    sentences = ["The applicant's pensionable-age date is no later than 2018-12-05.",
                 "The applicant's total income equals £35000.01.",
                 "The elapsed duration from the applicant's care start date to 2026-09-21 equals the applicant's care days before the week."]
    english = []
    for s in sentences:
        try:
            canonical = parse_w6_sentence(env, s)
            rendered = render_quantity_sentence(env, canonical)
            english.append({"sentence": s, "parsed": True, "rendered": rendered,
                            "round_trip": parse_w6_sentence(env, rendered) == canonical})
        except VEError as exc:
            english.append({"sentence": s, "parsed": False, "error": str(exc)})
    conditional = "If the applicant's claim date is no later than 2027-03-31, then the applicant's amount kept equals GBP 200.00."
    try:
        parse_w6_sentence(env, conditional)
        conditional_result = "parsed"
    except VEError as exc:
        conditional_result = f"rejected: {exc}"
    out["P3"] = {"expected": "facts parse uniquely and round-trip; the conditional is rejected",
                 "facts": english, "conditional": conditional_result}
    p4 = {}
    for s in ("The applicant's total income equals £35,000.00.", "The applicant's total income equals £35000.001."):
        try:
            parse_quantity_sentence(env, s)
            p4[s] = "parsed"
        except VEError as exc:
            p4[s] = f"rejected: {exc}"
    out["P4"] = {"expected": "both rejected (separator outside the surface; UnitPrecision)", "results": p4}
    out["P5"] = {"expected": "admitted", "elapsed_days": got["P5a"], "shift_days": got["P5b"]}
    a01 = next((p for p in profiles if p["id"] == "A01"), None)
    if a01 is not None:
        out["P6"] = {"expected": "a certificate for entitled(applicant) and for amount = GBP 200.00, accepted by Lean",
                     "single_shot": a01.get("single_shot", {}).get("searches"),
                     "staged": {"answers": a01["answers"], "documents_admitted": a01["lean"]["documents"]}}
    return out


def english_facts(env, cases, defaults):
    """Every distinct fact statement across the profiles: does it have a controlled
    English wording that parses back to itself with one reading?"""
    from ve.surface.time import parse_w6_sentence, render_quantity_sentence
    seen, rows = set(), []
    for case in cases:
        for f in T.profile_facts(case, defaults):
            k = T.key(f["formula"])
            if k in seen:
                continue
            seen.add(k)
            canonical, _ = elaborate_quantity(env, q(f["formula"]))
            try:
                sentence = render_quantity_sentence(env, canonical)
                ok = parse_w6_sentence(env, sentence) == canonical
            except VEError as exc:
                sentence, ok = f"no wording: {exc}", False
            rows.append({"fact": f["id"], "sentence": sentence, "round_trip": ok})
    return rows


MUTANT_TARGETS = {"M1": ["C14"], "M2": ["C14"], "M3": ["C10"], "M4": ["D01"], "M5": ["C01"], "M6": ["C04"],
                  "M7": ["B02"], "M8": ["B03"], "M9": ["B06"], "M10": ["C20"], "M11": ["C22"],
                  "M12": ["C17", "C19"], "M13": ["D05"], "M14": ["A08"], "M15": ["B11"], "M16": ["B12"],
                  "M17": ["B01", "B04"], "M18": ["B13"], "M19": ["B14"], "M20": ["B15", "B16", "B19"],
                  "M21": ["B16"], "M22": ["B19"], "M23": ["B17", "B18"]}


def mutation_check(cases, profiles, workers):
    """Run each mutated translation on the staged route over every profile; a
    mutant is killed when every profile PLAN section 8 names for it changes."""
    base = {p["id"]: p["staged"] for p in profiles}
    changes = dict(pool_map(_mutant_task, [(m, cases, base) for m in T.MUTANTS], workers))
    out = {}
    for mutant, description in T.MUTANTS.items():
        changed = changes[mutant]
        must = [p for p in MUTANT_TARGETS[mutant] if p in base]
        out[mutant] = {"description": description, "must_change": must, "changed": changed,
                       "killed": bool(must) and all(p in changed for p in must)}
    return out


def summarize(results, keyed):
    profiles = results["profiles"]
    per_q = {q: [0, 0] for q in ("Q1", "Q2", "Q3", "Q4")}
    answered = correct_answered = 0
    strict = 0
    disagreements = []
    single = {"answered": 0, "profiles": 0}
    for p in profiles:
        if "single_shot" in p:
            single["profiles"] += 1
            single["answered"] += p["single_shot"]["Q1"] != "OPEN"
        ok_all = True
        for question, ok in p["score"].items():
            per_q[question][0] += ok
            per_q[question][1] += 1
            got = p["answers"].get(question)
            if got not in ("OPEN", "N/A", None):
                answered += 1
                correct_answered += ok
            if not ok:
                ok_all = False
                disagreements.append({"profile": p["id"], "question": question, "key": p["key"][question],
                                      "ve": got})
        strict += ok_all
    total = [sum(v[0] for v in per_q.values()), sum(v[1] for v in per_q.values())]
    lean = {"certificates": sum(p["lean"]["certificates"] for p in profiles),
            "certificates_accepted": sum(p["lean"]["certificates_accepted"] for p in profiles),
            "documents": sum(len(p["lean"]["documents"]) for p in profiles),
            "documents_admitted": sum(sum(p["lean"]["documents"].values()) for p in profiles),
            "model_premises": sum(p["lean"]["model_premises"] for p in profiles),
            "model_premises_true": sum(p["lean"]["model_premises_true"] for p in profiles)}
    groups = {}
    for name, members in (("unflagged", [p for p in profiles if not keyed[p["id"]].get("flags")]),
                          ("guide", [p for p in profiles if p["id"] in GUIDE])):
        groups[name] = {"profiles": len(members),
                        "strict": sum(all(p["score"].values()) for p in members),
                        "correct": sum(sum(p["score"].values()) for p in members),
                        "scored": sum(len(p["score"]) for p in members)}
    mutants = results.get("mutants") or {}
    return {"profiles": len(profiles), "strict": strict,
            "per_question": {k: f"{v[0]}/{v[1]}" for k, v in per_q.items()},
            "total": f"{total[0]}/{total[1]}", "answered": answered, "correct_answered": correct_answered,
            "disagreements": disagreements, "groups": groups, "lean": lean, "single_shot": single,
            "mutants_killed": f"{sum(m['killed'] for m in mutants.values())}/{len(mutants)}" if mutants else None,
            "open": [{"profile": p["id"], "question": k} for p in profiles for k, v in p["answers"].items()
                     if v == "OPEN"]}


def results_markdown(results, keyed):
    """RESULTS.md (PLAN section 9), generated from results.json."""
    s = results["summary"]
    profiles = results["profiles"]
    lines = ["# Results: Winter Fuel Payment 2026 to 2027", "",
             "Generated by `run.py` from `results.json`; do not edit by hand. The plain-English",
             "account is in [README.md](README.md). Scoring follows PLAN.md section 3.", "",
             "## Accuracy (staged route, every answer admitted by Lean)", "",
             "| Measure | Result |", "|---|---|",
             f"| Strict, every scored question of a profile correct | {s['strict']}/{s['profiles']} |"]
    lines += [f"| {question} | {value} |" for question, value in s["per_question"].items()]
    lines += [f"| Total | {s['total']} |",
              f"| Answered (certified) | {s['answered']}/{s['total'].split('/')[1]} |",
              f"| Precision (correct / answered) | {s['correct_answered']}/{s['answered']} |"]
    for name in ("unflagged", "guide"):
        g = s["groups"][name]
        lines.append(f"| {name} profiles: strict | {g['strict']}/{g['profiles']} |")
        lines.append(f"| {name} profiles: questions | {g['correct']}/{g['scored']} |")
    lines += ["", "**Flagged profiles, one by one.**", "", "| Profile | Flags | Key | VE | Correct |", "|---|---|---|---|---|"]
    for p in profiles:
        flags = keyed[p["id"]].get("flags")
        if flags:
            key = " ".join(str(v) for v in p["key"].values())
            got = " ".join(str(p["answers"][k]) for k in p["key"])
            lines.append(f"| {p['id']} | {', '.join(flags)} | {key} | {got} | {'yes' if all(p['score'].values()) else 'no'} |")
    lines += ["", "**Disagreements.** " + ("None." if not s["disagreements"] else ""), ""]
    for d in s["disagreements"]:
        lines.append(f"- {d['profile']} {d['question']}: key {d['key']}, VE {d['ve']}")
    lines += ["**OPEN on the staged route.** " + ("None." if not s["open"] else ", ".join(
        f"{o['profile']} {o['question']}" for o in s["open"])), ""]
    single = s["single_shot"]
    lines += ["## Single shot (all rules and facts in one problem)", "",
              f"Q1 answered on {single['answered']} of {single['profiles']} profiles; Q2 to Q4 therefore OPEN everywhere.",
              "Every search stopped with status `NotFound`:", "",
              "| Search | Status | Steps | Searches |", "|---|---|---|---|"]
    from collections import Counter
    counts = Counter()
    for p in profiles:
        for name, v in p.get("single_shot", {}).get("searches", {}).items():
            counts[(name, v["status"], "124" if v["steps"] == 124 else "125 to 999")] += 1
    for (name, status, steps), n in sorted(counts.items()):
        lines.append(f"| {name} | {status} | {steps} | {n} |")
    lean = s["lean"]
    lines += ["", "## Evidence", "",
              f"- Step certificates produced: {lean['certificates']}; accepted by Lean `ve_quantity`: {lean['certificates_accepted']}.",
              f"- Answer documents (`documents@1`): {lean['documents']}; admitted by Lean: {lean['documents_admitted']}.",
              f"- Non-vacuity: {lean['model_premises_true']} of {lean['model_premises']} premise evaluations are true in the"
              " reference fixture models (Lean evaluation).",
              f"- Bridge B1 certified from no premises and accepted by Lean: {results['b1_certified']}.",
              f"- Proof searches: {results['prover']['searches']} distinct, {results['prover']['calls']} requested.",
              "", "## Probes (PLAN section 8, stage 0)", ""]
    for name, probe in results["probes"].items():
        lines.append(f"- **{name}**, expected {probe['expected']}: `{json.dumps({k: v for k, v in probe.items() if k != 'expected'}, ensure_ascii=False, sort_keys=True)}`")
    lines += ["", "## Mutants", "", f"Killed: {s['mutants_killed']}.", "",
              "| Mutant | Change | Must change | Changed | Killed |", "|---|---|---|---|---|"]
    for m, v in sorted(results["mutants"].items(), key=lambda item: int(item[0][1:])):
        changed = ", ".join(v["changed"]) if len(v["changed"]) <= 8 else f"{len(v['changed'])} profiles"
        lines.append(f"| {m} | {v['description']} | {', '.join(v['must_change'])} | {changed} | {'yes' if v['killed'] else 'no'} |")
    english = results["english"]
    lines += ["", "## English", "",
              f"{english['round_trip']} of {english['facts']} distinct fact statements have a controlled wording that"
              " parses back to the same statement with one reading. The rest are predicate literals, for which the"
              " W6a surface has no wording. Rules have no English (O8).", ""]
    return "\n".join(lines)


# Profiles whose basis is `guide` in PLAN.md section 5 (S2 states the answer).
GUIDE = {"A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10", "A11", "A12", "A13",
         "B01", "B04", "B05", "B07", "B08", "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08",
         "C09", "C10", "C13", "C15", "C22", "C23", "D01", "D02", "D03", "D04", "D05", "D06"}


if __name__ == "__main__":
    main()
