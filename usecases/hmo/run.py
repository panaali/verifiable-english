"""Run VE on the HMO in-scope cases (cases.py) and write the run file. SAME-FAMILY. The sealed answers are NOT read here.

Protocol (law 1's staged route, usecases/pawhp/run.py, unchanged in kind): for each case, ground rows.py over the case's
names (translation.py) and build the encoder's facts (encode.py); each derived atom is one step, proved in both polarities
from the rules that define it, the facts and earlier steps (one certificate -> holds; two -> inconsistent; none -> OPEN);
Lean replays every certificate and admits one documents@1 document per answer atom; an answer counts only if Lean admitted
its document(s). Q1 = hmo(premises), Q2 = prescribed(premises), Q3 = the s.254(1) limbs and Sch. 14 paragraphs that hold
(OPEN if any of them is OPEN). --mutants: each planted error must change at least one in-scope answer.

Usage (repository root): uv run python -B usecases/hmo/run.py [--cases H001,H002] [--mutants] [--no-lean] [--out FILE]
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

TESTS = [("standard", "standard test"), ("scf_test", "self-contained flat test"),
         ("converted_test", "converted building test"), ("decl", "HMO declaration"), ("s257", "section 257 block")]
SCH14 = [("sch14_2", "para 2"), ("sch14_2a", "para 2A"), ("sch14_2b", "para 2B"), ("sch14_5", "para 5"),
         ("sch14_6", "para 6"), ("sch14_7", "para 7")]
DERIVED_ANSWER_ATOMS = ["hmo", "prescribed", "standard", "scf_test", "converted_test"] + [a for a, _ in SCH14]


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
        facts, steps = [], []
        for a in sorted(atoms):
            if a == target:
                continue
            if a in self.defs:
                if a in self.steps:
                    steps.append(self.steps[a]["name"])
            else:
                facts += [f"fact:{f['id']}" for f in self.fact_atoms.get(a, [])]
        facts = list(dict.fromkeys(facts))
        return facts + steps + [f"rule:{r['id']}" for r in rules]

    def formula(self, name):
        return self.leaves[name] if name in self.leaves else self.by_name[name]["formula"]

    @property
    def by_name(self):
        return {s["name"]: s for s in self.steps.values()}

    def value(self, f):
        """Three-valued value of a ground formula from facts and established steps (search guidance only)."""
        h = f[0]
        if h in ("unary", "binary"):
            k = T.key(f)
            if k in self.steps:
                return self.steps[k]["formula"] == f
            for fact in self.fact_atoms.get(k, []):
                return fact["formula"] == f
            return None
        if h == "not":
            v = self.value(f[1])
            return None if v is None else not v
        if h in ("and", "or"):
            a, b = self.value(f[1]), self.value(f[2])
            if h == "and":
                return False if (a is False or b is False) else (True if a and b else None)
            return True if (a is True or b is True) else (False if a is False and b is False else None)
        if h == "implies":
            return self.value(["or", ["not", f[1]], f[2]])
        return None

    def rhs_value(self, target):
        rules = self.defs.get(target, [])
        if len(rules) != 1:
            return None
        f = rules[0]["formula"]
        if f[0] == "implies" and not T.is_iff(f):
            f = f[2]
        return self.value(f[1][2]) if T.is_iff(f) else None

    def witness(self, target, label):
        """For a positive candidate whose rule's right side is a disjunction: prove one true disjunct as its own step."""
        rules = self.defs.get(target, [])
        if len(rules) != 1:
            return None
        f = rules[0]["formula"]
        if f[0] == "implies" and not T.is_iff(f):
            f = f[2]
        if not T.is_iff(f):
            return None
        rhs, parts = f[1][2], []
        stack = [rhs]
        while stack:
            x = stack.pop()
            if x[0] == "or":
                stack += [x[2], x[1]]
            else:
                parts.append(x)
        if len(parts) < 2:
            return None
        for d in parts:
            if self.value(d) is True:
                atoms, consts = set(), set()
                scan(d, atoms, consts)
                names = []
                for a in sorted(atoms):
                    if a in self.steps:
                        names.append(self.steps[a]["name"])
                    else:
                        names += [f"fact:{x['id']}" for x in self.fact_atoms.get(a, [])]
                cert = self.prover.prove([self.formula(n) for n in names], d)
                if cert is None:
                    return None
                wk = "witness:" + label
                self.steps[wk] = {"name": f"step:{wk}", "formula": d, "premises": names, "certificate": cert}
                return f"step:{wk}"
        return None

    def attempt(self, target, label, candidates):
        names = self.premises_for(target)
        if True:
            w = self.witness(target, label)
            if w is not None:
                rule_names = [n for n in names if n.startswith("rule:")]
                guard = [n for n in names if n.startswith("step:") and "intrans" in n]
                cert = self.prover.prove([self.formula(n) for n in [w] + guard + rule_names], candidates[0])
                if cert is not None:
                    names = [w] + guard + rule_names
                    self.log.append({"target": label, "premises": names, "certified": 1, "witness": True})
                    self.steps[target] = {"name": f"step:{label}", "formula": candidates[0], "premises": names,
                                          "certificate": cert}
                    return candidates[0]
        premises = [self.formula(n) for n in names]
        found = []
        if self.rhs_value(target) is False:  # try the predicted polarity first; stop at the first certificate
            candidates = candidates[::-1]
        for cand in candidates:
            if found:
                break
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

    def run(self):
        for t in self.order():
            f = json.loads(t)
            self.attempt(t, label(f), [f, ["not", f]])
        yn = {True: "YES", False: "NO", None: "OPEN"}
        answers = {"Q1": yn[self.known(T.R.U("hmo", "premises"))], "Q2": yn[self.known(T.R.U("prescribed", "premises"))]}
        tests, sch, open_ = [], [], False
        for atom, lab in TESTS:
            v = self.known(T.R.U(atom, "premises"))
            open_ |= v is None
            if v:
                tests.append(lab)
        for atom, lab in SCH14:
            v = self.known(T.R.U(atom, "premises"))
            open_ |= v is None
            if v:
                sch.append(lab)
        answers["Q3"] = "OPEN" if open_ else {"tests": sorted(tests), "sch14": sorted(sch)}
        return answers

    def known(self, f):
        """A derived atom: its step; a base atom: its fact literal (None when unknown)."""
        k = T.key(f)
        step = self.steps.get(k)
        if step is not None:
            return step["formula"] == f
        for fact in self.fact_atoms.get(k, []):
            return fact["formula"] == f
        return None

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


def answer_targets(staged):
    out = {}
    for a in DERIVED_ANSWER_ATOMS:
        k = T.key(T.R.U(a, "premises"))
        if k in staged.steps:
            out[a] = k
    return out


LINE_LIMIT = 16_000_000  # under the Lean service's 16,777,216-byte line limit (MAX_LINE_BYTES)
LEAN_TIMEOUT = 600.0     # wall-clock seconds per request (100 certificates, or one document)


def lean(cases):
    """Lean replay in small requests, each with a wall-clock limit. A case over the wire's line limit is not sent; a request
    that fails (time limit, checker unavailable) is recorded as that error for each of its cases. Either way the answer
    that needs the case stays OPEN (refused)."""
    from ve.backends.relay import rows
    from ve.errors import CheckerUnavailable, VEError
    out, reqs, certs = [], [], []
    for c in cases:
        n = len(json.dumps(c))
        if n > LINE_LIMIT:
            reqs.append(("oversize", [c], n))
        elif c["kind"] == "certificate":
            certs.append(c)
            if len(certs) == 100:
                reqs.append(("ok", certs, 0))
                certs = []
        else:
            reqs.append(("ok", [c], 0))
    if certs:
        reqs.append(("ok", certs, 0))
    for kind, batch, n in reqs:
        if kind == "oversize":
            out.append({"id": batch[0]["id"], "status": "error",
                        "error": f"ResourceLimit: case of {n} bytes exceeds the line limit"})
            continue
        t0 = time.time()
        try:
            got = rows("quantity", batch, timeout=LEAN_TIMEOUT)
            assert [r["id"] for r in got] == [c["id"] for c in batch]
            out.extend(got)
        except (VEError, CheckerUnavailable) as e:
            msg = f"{type(e).__name__}: {str(e)[:160]} (after {round(time.time() - t0)} s)"
            print("lean request failed:", batch[0]["id"], len(batch), msg, file=sys.stderr, flush=True)
            out.extend({"id": c["id"], "status": "error", "error": msg} for c in batch)
    return out


def run_case(prover, case, mutant=None):
    rules = T.rules(E.domains(case), mutant)
    facts, unknown = E.facts(case)
    staged = Staged(prover, rules, facts)
    return staged.run(), staged, rules, facts, unknown


def _case_task(case):
    t0 = time.time()
    raw_env = T.environment()
    prover = Prover(Environment(raw_env))
    answers, staged, rules, facts, unknown = run_case(prover, case)
    rec = {"id": case["id"], "staged": answers, "unknown": unknown, "rules": len(rules), "facts": len(facts),
           "constraints": staged.check_constraints(),
           "steps": [{k: v for k, v in e.items() if k != "premises"} | {"premise_count": len(e["premises"])}
                     for e in staged.log],
           "open_steps": [e["target"] for e in staged.log if e["certified"] == 0],
           "encoder_judgement": case.get("judgement", []), "seconds": round(time.time() - t0, 1),
           "prover": {"calls": prover.calls, "searches": prover.searches}}
    lc = []
    for step in staged.steps.values():
        lc.append({"id": f"{case['id']}/cert/{step['name']}", "kind": "certificate",
                   "environment": raw_env, "premises": [q(staged.formula(n)) for n in step["premises"]],
                   "conclusion": q(step["formula"]), "certificate": step["certificate"]})
    for atom, target in answer_targets(staged).items():
        lc.append({"id": f"{case['id']}/doc/{atom}", "kind": "document", "environment": raw_env,
                   "document": staged.document(target)})
    return rec, lc


def _mutant_task(item):
    mutant, case = item
    prover = Prover(Environment(T.environment()))
    return mutant, case["id"], run_case(prover, case, mutant)[0]


def needs(answers):
    """answer -> the derived atoms whose Lean documents it needs"""
    out = {"Q1": ["hmo"], "Q2": ["prescribed"], "Q3": ["standard", "scf_test", "converted_test"] + [a for a, _ in SCH14]}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases")
    ap.add_argument("--mutants", action="store_true")
    ap.add_argument("--no-lean", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args(argv)
    started = time.time()
    raw_env = T.environment()
    env = Environment(raw_env)
    prover = Prover(env)
    cases = K.CASES
    if args.cases:
        cases = [c for c in cases if c["id"] in args.cases.split(",")]
    records, lean_cases = [], []
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for rec, lc in pool.map(_case_task, cases):
            records.append(rec)
            lean_cases += lc
            print(rec["id"], rec["staged"], rec["seconds"], "s", file=sys.stderr, flush=True)
    records.sort(key=lambda r: r["id"])
    lean_results = {} if args.no_lean else {r["id"]: r for r in lean(lean_cases)}
    for rec in records:
        pid = rec["id"]
        mine = {k: v for k, v in lean_results.items() if k.startswith(pid + "/")}
        certs = [v for k, v in mine.items() if "/cert/" in k]
        docs = {k.rsplit("/", 1)[1]: v for k, v in mine.items() if "/doc/" in k}
        rec["lean_errors"] = sorted({r.get("error", "")[:80] for r in mine.values() if r.get("status") != "ok"})
        rec["lean"] = {"certificates": len(certs),
                       "certificates_accepted": sum(r.get("status") == "ok" and r.get("valid") is True for r in certs),
                       "documents": {a: r.get("status") == "ok" and r.get("assurance") == "lean-admitted"
                                     for a, r in sorted(docs.items())}}
        answers = dict(rec["staged"])
        if not args.no_lean:
            for qq, atoms in needs(answers).items():
                if answers[qq] == "OPEN":
                    continue
                if not all(rec["lean"]["documents"].get(a) for a in atoms):
                    answers[qq] = "OPEN"
                    rec.setdefault("lean_rejected", []).append(qq)
        rec["answers"] = answers
    for pid, why in K.PROBES.items():
        if not args.cases or pid in args.cases.split(","):
            records.append({"id": pid, "scope": "out", "answers": {"Q1": "UNSUPPORTED"}, "unsupported": why})
    mutants = {}
    if args.mutants:
        base = {r["id"]: r["staged"] for r in records if "staged" in r}
        changed = {m: [] for m in T.MUTANTS}
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            for m, cid, ans in pool.map(_mutant_task, [(m, c) for m in T.MUTANTS for c in cases]):
                if ans != base[cid]:
                    changed[m].append(cid)
        for m, (desc, _) in T.MUTANTS.items():
            mutants[m] = {"description": desc, "changed": sorted(changed[m]), "killed": bool(changed[m])}
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "usecases/hmo"],
                           capture_output=True, text=True).stdout.strip()
    enc = hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest()
    out = {"format": "hmo-run@1", "label": "SAME-FAMILY", "commit": commit, "tree_clean": dirty == "",
           "questions_enc_sha256": enc, "environment_id": env.environment_id,
           "prover": {"calls": sum(r.get("prover", {}).get("calls", 0) for r in records)},
           "lean_cases": len(lean_cases), "records": records, "mutants": mutants,
           "seconds": round(time.time() - started)}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print("run file", args.out, hashlib.sha256(text.encode()).hexdigest())
    summary = {}
    for r in records:
        for qq, v in r["answers"].items():
            v = v if isinstance(v, str) else "lists"
            summary.setdefault(qq, {}).setdefault(v, 0)
            summary[qq][v] += 1
    print(json.dumps({"summary": summary, "seconds": out["seconds"], "commit": commit, "clean": out["tree_clean"],
                      "mutants": {m: v["killed"] for m, v in mutants.items()}}, indent=1))
    return out


if __name__ == "__main__":
    main()
