"""Run VE on the PAWHP in-scope people (cases.py) and write the run file. SAME-FAMILY. The sealed answers are NOT read here.

Protocol (PAGE.md 'The number'): the staged route of usecases/eligibility/run.py, generalised. For each case:
1. Ground the rules over the case's people (translation.py), build the encoder's facts (encode.py).
2. Each derived atom is one step, proved (both polarities) from the rules that define it, the facts those rules mention
   and earlier steps; the amount is one step over the five amounts of reg. 10 / 9A(4). One certificate -> the step holds;
   two -> inconsistent (recorded); none -> OPEN.
3. Rules that constrain a STATED fact (e.g. row 18's 'throughout' union) are not used as step premises; each is checked
   against the facts (a certificate of bottom = the encoding contradicts the rule; recorded per case).
4. Lean replays every step certificate and admits one documents@1 quantity document per answer; an answer counts only if
   Lean admitted its document (else OPEN).
5. --mutants: each planted error (translation.MUTANTS) must change the answer of the person named for it.

Usage (from the repository root): uv run python usecases/pawhp/run.py [--cases P001,P002] [--mutants] [--out FILE]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import cases as K  # noqa: E402
import encode as E  # noqa: E402
import translation as T  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.units import prove_quantity  # noqa: E402

STEP_CONSTANTS = ("amount",)


def q(f):
    return T.q(f)


def scan(f, atoms, constants):
    T.atoms_in(f, atoms, constants)


class Prover:
    def __init__(self, env):
        self.env, self.cache, self.calls, self.searches = env, {}, 0, 0

    def prove(self, premises, conclusion):
        self.calls += 1
        k = T.key([premises, conclusion])
        if k not in self.cache:
            self.searches += 1
            self.cache[k] = prove_quantity(self.env, [q(p) for p in premises], q(conclusion))
        return self.cache[k]


class Staged:
    def __init__(self, prover, rules, facts):
        self.prover = prover
        self.fact_atoms, self.fact_constants = {}, {}
        for f in facts:
            atoms, constants = set(), set()
            scan(f["formula"], atoms, constants)
            for a in atoms:
                self.fact_atoms.setdefault(a, []).append(f)
            for c in constants:
                self.fact_constants.setdefault(c, []).append(f)
        self.defs, self.constraints = {}, []
        for r in rules:
            stated = [t for t in r["defines"] if t in self.fact_atoms]
            if stated:
                self.constraints.append(r)
                continue
            for target in r["defines"]:
                self.defs.setdefault(target, []).append(r)
        self.leaves = {f"rule:{r['id']}": r["formula"] for r in rules}
        self.leaves.update({f"fact:{f['id']}": f["formula"] for f in facts})
        self.steps, self.log = {}, []

    def premises_for(self, target):
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
            if c == target or (c in self.defs and c not in STEP_CONSTANTS):
                continue
            if c in STEP_CONSTANTS:
                if c in self.steps:
                    steps.append(self.steps[c]["name"])
            else:
                facts += [f"fact:{f['id']}" for f in self.fact_constants.get(c, [])]
        facts = list(dict.fromkeys(facts))
        return facts + steps + [f"rule:{r['id']}" for r in rules]

    def formula(self, name):
        return self.leaves[name] if name in self.leaves else self.by_name[name]["formula"]

    @property
    def by_name(self):
        return {s["name"]: s for s in self.steps.values()}

    def attempt(self, target, label, candidates):
        names = self.premises_for(target)
        premises = [self.formula(n) for n in names]
        found = []
        for cand in candidates:
            cert = self.prover.prove(premises, cand)
            if cert is not None:
                found.append((cand, cert))
        entry = {"target": label, "premises": names, "certified": len(found)}
        self.log.append(entry)
        if len(found) == 1:
            cand, cert = found[0]
            self.steps[target] = {"name": f"step:{label}", "formula": cand, "premises": names, "certificate": cert}
            return cand
        if len(found) > 1:
            entry["inconsistent"] = True
        return None

    def order(self):
        """Derived targets in dependency order (a target after every derived atom its rules mention)."""
        deps = {}
        for t, rs in self.defs.items():
            a, c = set(), set()
            for r in rs:
                scan(r["formula"], a, c)
            deps[t] = sorted(x for x in (a | c) if x != t and x in self.defs)
        out, state = [], {}

        def visit(t, path):
            if state.get(t) == 2:
                return
            if state.get(t) == 1:
                raise ValueError(f"cycle: {path + [t]}")
            state[t] = 1
            for d in deps[t]:
                visit(d, path + [t])
            state[t] = 2
            out.append(t)
        for t in sorted(self.defs):
            visit(t, [])
        return out

    def run(self, ask_q3):
        for t in self.order():
            if t in STEP_CONSTANTS:
                continue
            if t.startswith("["):
                f = json.loads(t)
                self.attempt(t, label(f), [f, ["not", f]])
        entitled = self.known(T.R.U("entitled", "applicant"))
        answers = {"Q1": {True: "YES", False: "NO", None: "OPEN"}[entitled]}
        if entitled is True:
            got = self.attempt("amount", "amount", [["eq", T.R.ci("amount"), T.R.gbp(v)] for v in T.AMOUNTS])
            answers["Q2"] = got[2][2] if got else "OPEN"
        else:
            answers["Q2"] = "N/A" if entitled is False else "OPEN"
        if ask_q3:
            t = self.known(T.R.U("application_in_time", "applicant"))
            answers["Q3"] = {True: "YES", False: "NO", None: "OPEN"}[t]
        return answers

    def known(self, f):
        step = self.steps.get(T.key(f))
        return None if step is None else step["formula"] == f

    def check_constraints(self):
        """Each constraint rule against the facts and established steps it mentions: a certificate of bottom =
        contradiction."""
        out = []
        for r in self.constraints:
            a, c = set(), set()
            scan(r["formula"], a, c)
            facts = []
            for x in sorted(a):
                facts += [f["formula"] for f in self.fact_atoms.get(x, [])]
                if x in self.steps:
                    facts.append(self.steps[x]["formula"])
            cert = self.prover.prove(facts + [r["formula"]], ["bottom"])
            out.append({"rule": r["id"], "contradicted": cert is not None})
        return out

    def document(self, root_target):
        root = self.steps[root_target]
        by_name = self.by_name
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
        for step in self.steps.values():
            if step["name"] in needed:
                nodes.append({"name": step["name"], "quantity": q(step["formula"]),
                              "premises": step["premises"], "certificate": step["certificate"]})
        return {"units": units, "graph": {"root": root["name"], "nodes": nodes}}


def label(f):
    return f[1] + "." + ".".join(t[1] for t in f[2:])


def answer_targets(answers):
    out = {}
    if answers["Q1"] in ("YES", "NO"):
        out["Q1"] = T.key(T.R.U("entitled", "applicant"))
    if answers.get("Q2") not in (None, "OPEN", "N/A"):
        out["Q2"] = "amount"
    if answers.get("Q3") in ("YES", "NO"):
        out["Q3"] = T.key(T.R.U("application_in_time", "applicant"))
    return out


def lean(cases):
    from ve.backends.relay import rows
    results = rows("quantity", cases)
    assert [r["id"] for r in results] == [c["id"] for c in cases]
    return results


def run_case(prover, case, mutant=None):
    people = [p["c"] for p in case["people"]]
    marriages = [m["c"] for m in case.get("marriages", [])]
    rules = T.rules(people, marriages, mutant)
    facts, unknown = E.facts(case)
    staged = Staged(prover, rules, facts)
    ask_q3 = case["people"][0].get("received") is not None
    return staged.run(ask_q3), staged, rules, facts, unknown


def _mutant_task(item):
    mutant, cases, base = item
    prover = Prover(Environment(T.environment()))
    return mutant, [c["id"] for c in cases if run_case(prover, c, mutant)[0] != base[c["id"]]]


MUTANT_TARGETS = {"M1": ["P001"], "M2": ["P004"], "M3": ["P002"], "M4": ["P037"], "M5": ["P007"]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases")
    ap.add_argument("--mutants", action="store_true")
    ap.add_argument("--no-lean", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args(argv)
    started = time.time()
    raw_env = T.environment()
    env = Environment(raw_env)
    prover = Prover(env)
    cases = K.CASES
    if args.cases:
        cases = [c for c in cases if c["id"] in args.cases.split(",")]
    records, lean_cases = [], []
    for case in cases:
        answers, staged, rules, facts, unknown = run_case(prover, case)
        rec = {"id": case["id"], "staged": answers, "unknown": unknown,
               "rules": len(rules), "facts": len(facts), "constraints": staged.check_constraints(),
               "steps": [{k: v for k, v in e.items() if k != "premises"} | {"premise_count": len(e["premises"])}
                         for e in staged.log],
               "encoder_judgement": case.get("judgement", [])}
        records.append(rec)
        for step in staged.steps.values():
            lean_cases.append({"id": f"{case['id']}/cert/{step['name']}", "kind": "certificate",
                               "environment": raw_env, "premises": [q(staged.formula(n)) for n in step["premises"]],
                               "conclusion": q(step["formula"]), "certificate": step["certificate"]})
        for question, target in answer_targets(answers).items():
            lean_cases.append({"id": f"{case['id']}/doc/{question}", "kind": "document", "environment": raw_env,
                               "document": staged.document(target)})
    lean_results = {} if args.no_lean else {r["id"]: r for r in lean(lean_cases)}
    for rec in records:
        pid = rec["id"]
        mine = {k: v for k, v in lean_results.items() if k.startswith(pid + "/")}
        certs = [v for k, v in mine.items() if "/cert/" in k]
        docs = {k.rsplit("/", 1)[1]: v for k, v in mine.items() if "/doc/" in k}
        rec["lean"] = {"certificates": len(certs),
                       "certificates_accepted": sum(r.get("status") == "ok" and r.get("valid") is True for r in certs),
                       "documents": {qq: r.get("status") == "ok" and r.get("assurance") == "lean-admitted"
                                     for qq, r in sorted(docs.items())}}
        answers = dict(rec["staged"])
        for qq in answer_targets(answers):
            if not rec["lean"]["documents"].get(qq):
                answers[qq] = "OPEN"
                rec.setdefault("lean_rejected", []).append(qq)
        rec["answers"] = answers
    for pid, why in K.PROBES.items():
        if not args.cases or pid in args.cases.split(","):
            records.append({"id": pid, "scope": "out", "answers": {"Q1": "UNSUPPORTED", "Q2": "UNSUPPORTED"},
                            "unsupported": why})
    mutants = {}
    if args.mutants:
        from concurrent.futures import ProcessPoolExecutor
        base = {r["id"]: r["staged"] for r in records if "staged" in r}
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            changed = dict(pool.map(_mutant_task, [(m, cases, base) for m in T.MUTANTS]))
        for m, (desc, _) in T.MUTANTS.items():
            must = [p for p in MUTANT_TARGETS[m] if p in base]
            mutants[m] = {"description": desc, "must_change": must, "changed": changed[m],
                          "killed": bool(must) and all(p in changed[m] for p in must)}
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "usecases/pawhp"],
                           capture_output=True, text=True).stdout.strip()
    enc = hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest()
    out = {"format": "pawhp-run@1", "label": "SAME-FAMILY", "commit": commit, "tree_clean": dirty == "",
           "questions_enc_sha256": enc, "environment_id": env.environment_id,
           "prover": {"calls": prover.calls, "searches": prover.searches},
           "lean_cases": len(lean_cases), "records": records, "mutants": mutants,
           "seconds": round(time.time() - started)}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print("run file", args.out, hashlib.sha256(text.encode()).hexdigest())
    summary = {}
    for r in records:
        for qq, v in r["answers"].items():
            summary.setdefault(qq, {}).setdefault(v if v in ("YES", "NO", "OPEN", "N/A", "UNSUPPORTED") else "amount", 0)
            summary[qq][v if v in ("YES", "NO", "OPEN", "N/A", "UNSUPPORTED") else "amount"] += 1
    print(json.dumps({"summary": summary, "seconds": out["seconds"], "commit": commit, "clean": out["tree_clean"],
                      "mutants": {m: v["killed"] for m, v in mutants.items()}}, indent=1))
    return out


if __name__ == "__main__":
    main()
