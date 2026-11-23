"""Run VE on the 14 CFR 61.23 cases (cases.py) and write the run file. SAME-FAMILY. The sealed answers are NOT read here.

Protocol (law 1 PAWHP's run.py, the staged route, adapted; statute corpus law 4). For each case:
1. Ground the rules over the case's certificates and applications (translation.py), build the encoder's facts (encode.py).
2. Each derived atom is one step, proved (both polarities) from the rules that define it, the facts those rules mention
   and earlier steps; Q3's last day is one step over the case's bridged dates. One certificate -> the step holds;
   two -> inconsistent (recorded); none -> OPEN.
   Q1 = the one requirement atom (needs_first / second / third / none / cert_or_dl) proved TRUE (else OPEN); Q2 = meets;
   Q3 = NONE when no_last_day is proved, else the certified last day; N/A when meets is proved false.
3. Rules that constrain a STATED fact (e.g. row 18's 'throughout' union) are not used as step premises; each is checked
   against the facts (a certificate of bottom = the encoding contradicts the rule; recorded per case).
4. Lean replays every step certificate and admits one documents@1 quantity document per answer; an answer counts only if
   Lean admitted its document (else OPEN).
5. --mutants: each planted error (translation.MUTANTS) must change the answer of the person named for it.

Usage (from the repository root): uv run python -B usecases/faa-medical/run.py [--cases F001,F002] [--mutants] [--out FILE]
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

STEP_CONSTANTS = ("expiry", "dl_last", "last_day")  # day constants proved as their own step among the bridged dates
NEEDS = (("needs_first", "FIRST CLASS"), ("needs_second", "SECOND CLASS"), ("needs_third", "THIRD CLASS"),
         ("needs_none", "NONE"), ("needs_cert_or_dl", "CERTIFICATE OR LICENSE"))


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

    def literal_value(self, lit):
        """True/False when a fact or an established step fixes this literal; None otherwise."""
        neg = type(lit) is list and lit[:1] == ["not"]
        atom = lit[1] if neg else lit
        if type(atom) is not list or atom[:1] not in (["unary"], ["binary"]):
            return None
        k = T.key(atom)
        val = None
        if k in self.steps:
            val = self.steps[k]["formula"] == atom
        else:
            for f in self.fact_atoms.get(k, []):
                if f["formula"] == atom:
                    val = True
                elif f["formula"] == ["not", atom]:
                    val = False
        return None if val is None else (val != neg)

    def live(self, r):
        """Premise selection for a day-constant step: drop a rule whose 'if' part holds a literal already known false
        (sound: a smaller premise set; Lean still replays the certificate)."""
        f = r["formula"]
        if type(f) is not list or f[:1] != ["implies"]:
            return True
        return not any(self.literal_value(c) is False for c in T.conjuncts(f[1]))

    def premises_for(self, target):
        rules, seen = [], set()
        queue = [r for r in self.defs[target] if target not in STEP_CONSTANTS or self.live(r)]
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

    def run(self, dates):
        for t in self.order():
            if t in ("expiry", "dl_last"):
                self.attempt(t, t, [["eq", T.R.ci(t), T.R.day(d)] for d in dates])
                continue
            if t in STEP_CONSTANTS:
                continue
            if t.startswith("["):
                f = json.loads(t)
                self.attempt(t, label(f), [f, ["not", f]])
        true = [ans for atom, ans in NEEDS if self.known(T.R.U(atom)) is True]
        answers = {"Q1": true[0] if len(true) == 1 else "OPEN"}
        meets = self.known(T.R.U("meets"))
        answers["Q2"] = {True: "YES", False: "NO", None: "OPEN"}[meets]
        if meets is False:
            answers["Q3"] = "N/A"
        elif meets is True:
            none = self.known(T.R.U("no_last_day"))
            if none is True:
                answers["Q3"] = "NONE"
            elif none is False:
                got = self.attempt("last_day", "last_day", [["eq", T.R.ci("last_day"), T.R.day(d)] for d in dates])
                answers["Q3"] = got[2][1] if got else "OPEN"
            else:
                answers["Q3"] = "OPEN"
        else:
            answers["Q3"] = "OPEN"
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
    """The step each answer rests on (its Lean-admitted document): Q1 the requirement atom proved true, Q2 meets,
    Q3 no_last_day (NONE), the last_day step (a date) or meets (N/A)."""
    out = {}
    for atom, ans in NEEDS:
        if answers["Q1"] == ans:
            out["Q1"] = T.key(T.R.U(atom))
    if answers.get("Q2") in ("YES", "NO"):
        out["Q2"] = T.key(T.R.U("meets"))
    if answers.get("Q3") == "NONE":
        out["Q3"] = T.key(T.R.U("no_last_day"))
    elif answers.get("Q3") == "N/A":
        out["Q3"] = T.key(T.R.U("meets"))
    elif answers.get("Q3") not in (None, "OPEN"):
        out["Q3"] = "last_day"
    return out


def lean(cases):
    from ve.backends.relay import rows
    results = rows("quantity", cases)
    assert [r["id"] for r in results] == [c["id"] for c in cases]
    return results


def run_case(prover, case, mutant=None):
    certs, apps = E.records(case)
    rules = T.rules(certs, apps, mutant)
    facts, unknown = E.facts(case)
    staged = Staged(prover, rules, facts)
    return staged.run(E.candidate_days(case)), staged, rules, facts, unknown


def _mutant_task(item):
    mutant, cases, base = item
    prover = Prover(Environment(T.environment()))
    return mutant, [c["id"] for c in cases if run_case(prover, c, mutant)[0] != base[c["id"]]]


MUTANT_TARGETS = K.MUTANT_TARGETS


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
            records.append({"id": pid, "answers": {"Q1": "UNSUPPORTED", "Q2": "UNSUPPORTED", "Q3": "UNSUPPORTED"},
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
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "usecases/faa-medical"],
                           capture_output=True, text=True).stdout.strip()
    qe = HERE / "questions-enc.jsonl"
    enc = hashlib.sha256(qe.read_bytes()).hexdigest() if qe.exists() else None
    out = {"format": "faa-medical-run@1", "label": "SAME-FAMILY", "commit": commit, "tree_clean": dirty == "",
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
            v = v if qq != "Q3" or v in ("NONE", "OPEN", "N/A", "UNSUPPORTED") else "date"
            summary.setdefault(qq, {}).setdefault(v, 0)
            summary[qq][v] += 1
    print(json.dumps({"summary": summary, "seconds": out["seconds"], "commit": commit, "clean": out["tree_clean"],
                      "mutants": {m: v["killed"] for m, v in mutants.items()}}, indent=1))
    return out


if __name__ == "__main__":
    main()
