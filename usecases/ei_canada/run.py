"""Run VE on the Canada EI cases (cases.py) and write the run file. SAME-FAMILY. The sealed answers are NOT read here.

Protocol (usecases/tenant_fees/run.py's staged route; Prover/Staged copied from it):
1. Ground the rules over the case's items (translation.rules), take the encoder's facts (encode.py from cases.py).
2. Each derived atom is one step, proved (both polarities) from the rules that define it, the facts its rules mention and
   earlier steps. Each staged amount (STEP constants) is one step over CANDIDATE values; the candidates come from a
   generic forward evaluator of the ground rules (a search aid, outside the trust boundary) plus a sentinel no consistent
   premise set proves. One certificate -> the step holds; two or more -> inconsistent (refused); none -> OPEN.
3. Lean replays every step certificate and admits one documents@1 quantity document per answer target; an answer counts
   only if Lean admitted every document it uses (else OPEN).
4. --mutants: each planted error (translation.MUTANTS) is run over all cases; it must change at least one answer.

Usage (repository root): .venv/bin/python -B usecases/ei_canada/run.py [--cases E001,E002] [--mutants] [--out FILE]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import translation as T  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.units import prove_quantity  # noqa: E402

STEP = ("reqh", "nweeks", "mwie", "maxweeks", "calcsum", "septotal", "total", "wie", "wiecap", "benefit")
SCALE = {T.CAD: 100, T.RATE: 10, T.HOUR: 1, T.WEEK: 1}
SENTINEL = {T.CAD: ["decimal", T.CAD, "-0.01"], T.WEEK: ["decimal", T.WEEK, "-1"], T.HOUR: ["decimal", T.HOUR, "-1"],
            T.RATE: ["decimal", T.RATE, "-0.1"], T.DAY: ["date", "1970-01-01"]}


class Prover:
    def __init__(self, env):
        self.env, self.cache, self.calls, self.searches = env, {}, 0, 0

    def prove(self, premises, conclusion):
        self.calls += 1
        kk = T.key([premises, conclusion])
        if kk not in self.cache:
            self.searches += 1
            self.cache[kk] = prove_quantity(self.env, [T.q(p) for p in premises], T.q(conclusion))
        return self.cache[kk]


# --- generic forward evaluator (search aid; never an answer source) ----------------------------------------------

def _num(term):
    if term[0] == "decimal":
        return Fraction(term[2]) * SCALE.get(term[1], 1)
    if term[0] == "date":
        return Fraction((dt.date.fromisoformat(term[1]) - dt.date(1970, 1, 1)).days)
    return None


def _lin(term):
    """term -> ({constant: coeff}, offset) or None (unit coordinates)."""
    v = _num(term)
    if v is not None:
        return {}, v
    if term[0] == "const" and len(term) == 3:
        return {term[2]: Fraction(1)}, Fraction(0)
    if term[0] == "add":
        a, b = _lin(term[2]), _lin(term[3])
        if a is None or b is None:
            return None
        d = dict(a[0])
        for n, cf in b[0].items():
            d[n] = d.get(n, 0) + cf
        return d, a[1] + b[1]
    if term[0] == "scale":
        a = _lin(term[3])
        if a is None:
            return None
        f = Fraction(term[2])
        return {n: cf * f for n, cf in a[0].items()}, a[1] * f
    return None


class Forward:
    """Three-valued forward evaluation of ground rules from the facts (candidate values only)."""

    def __init__(self, rules, facts):
        self.vals, self.truths = {}, {}
        self.rules = [r["formula"] for r in rules]
        for f in facts:
            self.apply(f["formula"])
        for _ in range(400):
            before = (len(self.vals), len(self.truths))
            for f in self.rules:
                self.fire(f)
            if (len(self.vals), len(self.truths)) == before:
                break

    def term(self, t):
        lin = _lin(t)
        if lin is None:
            return None
        tot = lin[1]
        for n, cf in lin[0].items():
            if n not in self.vals:
                return None
            tot += cf * self.vals[n]
        return tot

    def ev(self, f):
        h = f[0]
        if h == "true":
            return True
        if h in ("unary", "binary"):
            return self.truths.get(T.key(f))
        if h == "not":
            v = self.ev(f[1])
            return None if v is None else not v
        if h in ("and", "or"):
            a, b = self.ev(f[1]), self.ev(f[2])
            if h == "and":
                return False if (a is False or b is False) else (True if (a and b) else None)
            return True if (a is True or b is True) else (False if (a is False and b is False) else None)
        if h == "implies":
            a, b = self.ev(f[1]), self.ev(f[2])
            return True if (a is False or b is True) else (False if (a is True and b is False) else None)
        if h in ("eq", "lt", "le", "date_no_later"):
            a, b = self.term(f[1]), self.term(f[2])
            if a is None or b is None:
                return None
            return {"eq": a == b, "lt": a < b, "le": a <= b, "date_no_later": a <= b}[h]
        return None

    def fire(self, f):
        if T.is_iff(f):
            v = self.ev(f[1][2])
            if v is not None:
                self.truths.setdefault(T.key(f[1][1]), v)
            return
        if f[0] == "implies":
            if self.ev(f[1]) is True:
                self.apply(f[2])
            return
        self.apply(f)

    def apply(self, c):
        h = c[0]
        if h in ("unary", "binary"):
            self.truths.setdefault(T.key(c), True)
        elif h == "not" and c[1][0] in ("unary", "binary"):
            self.truths.setdefault(T.key(c[1]), False)
        elif h == "eq":
            a, b = _lin(c[1]), _lin(c[2])
            if a is None or b is None:
                return
            d = dict(a[0])
            for n, cf in b[0].items():
                d[n] = d.get(n, 0) - cf
            rhs = b[1] - a[1]
            unknown = [n for n, cf in d.items() if cf != 0 and n not in self.vals]
            if len(unknown) != 1:
                return
            u = unknown[0]
            for n, cf in d.items():
                if n != u and cf != 0:
                    rhs -= cf * self.vals[n]
            v = rhs / d[u]
            if v.denominator == 1:
                self.vals.setdefault(u, v)
        elif h == "and" and c[1][0] == "le" and c[2][0] == "lt":  # the half-up pair: a*b + o1 <= X < a*b + o2
            lhs, x = _lin(c[1][1]), self.term(c[1][2])
            if lhs is None or x is None or len(lhs[0]) != 1:
                return
            (u, a), = lhs[0].items()
            if u in self.vals:
                return
            v = Fraction(math.floor((x - lhs[1]) / a))
            if self.ev(["lt", c[2][1], c[2][2]]) is not False:
                self.vals.setdefault(u, v)


def literal(unit, v):
    if unit == T.DAY:
        return ["date", (dt.date(1970, 1, 1) + dt.timedelta(days=int(v))).isoformat()]
    s = SCALE[unit]
    v = Fraction(v)
    if s == 1:
        return ["decimal", unit, str(int(v))]
    places = {100: 2, 10: 1}[s]
    n = int(v)
    sign = "-" if n < 0 else ""
    return ["decimal", unit, f"{sign}{abs(n) // s}.{abs(n) % s:0{places}d}"]


class Staged:
    """tenant_fees/run.py's Staged, unchanged in logic: steps proved from defining rules, facts and earlier steps."""

    def __init__(self, prover, rules, facts):
        self.prover = prover
        self.fact_atoms, self.fact_constants = {}, {}
        for f in facts:
            atoms, constants = set(), set()
            T.atoms_in(f["formula"], atoms, constants)
            for a in atoms:
                self.fact_atoms.setdefault(a, []).append(f)
            for cname in constants:
                self.fact_constants.setdefault(cname, []).append(f)
        self.defs, self.constraints = {}, []
        for r in rules:
            if [t for t in r["defines"] if t in self.fact_atoms]:
                self.constraints.append(r)
                continue
            for target in r["defines"]:
                self.defs.setdefault(target, []).append(r)
        self.leaves = {f"rule:{r['id']}": r["formula"] for r in rules}
        self.leaves.update({f"fact:{f['id']}": f["formula"] for f in facts})
        self.steps, self.log = {}, []
        self.forward = Forward(rules, facts)

    def is_step_constant(self, name):
        return name in STEP

    def truth(self, f):
        if f[0] == "not":
            v = self.truth(f[1])
            return None if v is None else not v
        if f[0] not in ("unary", "binary"):
            return None
        kk = T.key(f)
        if kk in self.steps:
            return self.steps[kk]["formula"] == f
        for fact in self.fact_atoms.get(kk, []):
            if fact["formula"] == f:
                return True
            if fact["formula"] == ["not", f]:
                return False
        return None

    def dead(self, formula):
        """A rule 'A -> C' whose A has a conjunct already known false never fires: not sent as a premise."""
        if formula[0] != "implies":
            return False
        parts, stack = [], [formula[1]]
        while stack:
            p = stack.pop()
            if p[0] == "and" and not T.is_iff(p):
                stack += [p[1], p[2]]
            else:
                parts.append(p)
        # also a comparison the forward evaluator reads as false (e.g. a table row's band against the stated rate):
        # selection only, so the search aid can lose a proof here but never make one
        return any(self.truth(p) is False or (p[0] in ("lt", "le", "eq", "date_no_later")
                                               and self.forward.ev(p) is False) for p in parts)

    def premises_for(self, target):
        rules, seen, queue = [], set(), [r for r in self.defs.get(target, []) if not self.dead(r["formula"])]
        atoms, constants = set(), set()
        while queue:
            r = queue.pop(0)
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rules.append(r)
            a, cs = set(), set()
            T.atoms_in(r["formula"], a, cs)
            atoms |= a
            for name in cs - constants:
                constants.add(name)
                if name != target and not self.is_step_constant(name) and name in self.defs:
                    queue.extend(r2 for r2 in self.defs[name] if not self.dead(r2["formula"]))
        facts, steps = [], []
        for a in sorted(atoms):
            if a == target:
                continue
            if a in self.defs:
                if a in self.steps:
                    steps.append(self.steps[a]["name"])
            else:
                facts += [f"fact:{f['id']}" for f in self.fact_atoms.get(a, [])]
        for cname in sorted(constants):
            if cname != target and self.is_step_constant(cname) and cname in self.steps:
                steps.append(self.steps[cname]["name"])
            facts += [f"fact:{f['id']}" for f in self.fact_constants.get(cname, [])]
        facts = list(dict.fromkeys(facts))
        return facts + list(dict.fromkeys(steps)) + [f"rule:{r['id']}" for r in rules]

    def formula(self, name):
        return self.leaves[name] if name in self.leaves else self.by_name[name]["formula"]

    @property
    def by_name(self):
        return {s["name"]: s for s in self.steps.values()}

    def attempt(self, target, label, cands):
        names = self.premises_for(target)
        premises = [self.formula(n) for n in names]
        found = []
        for cand in cands:
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
        deps = {}
        for t, rs in self.defs.items():
            a, cs = set(), set()
            for r in rs:
                T.atoms_in(r["formula"], a, cs)
            deps[t] = sorted(x for x in (a | cs) if x != t and x in self.defs)
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

    def needed(self, roots):
        deps = {}
        for t, rs in self.defs.items():
            a, cs = set(), set()
            for r in rs:
                T.atoms_in(r["formula"], a, cs)
            deps[t] = [x for x in (a | cs) if x != t and x in self.defs]
        out, stack = set(), [r for r in roots if r in self.defs]
        while stack:
            t = stack.pop()
            if t in out:
                continue
            out.add(t)
            stack += deps[t]
        return out

    def run(self, units, roots=None):
        need = None if roots is None else self.needed(roots)
        for t in self.order():
            if need is not None and t not in need:
                continue
            if t.startswith("["):
                f = json.loads(t)
                self.attempt(t, label(f), [f, ["not", f]])
            elif self.is_step_constant(t):
                unit = units[t]
                cands = []
                if t in self.forward.vals:
                    cands.append(["eq", ["const", unit, t], literal(unit, self.forward.vals[t])])
                cands.append(["eq", ["const", unit, t], SENTINEL[unit]])
                self.attempt(t, t, cands)

    def value(self, name):
        step = self.steps.get(name)
        return None if step is None else step["formula"][2]

    def check_constraints(self):
        out = []
        for r in self.constraints:
            a, cs = set(), set()
            T.atoms_in(r["formula"], a, cs)
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
            units.append({"id": uid, "span": [i, i + 1], "kind": "asserted", "content": T.q(self.leaves[name])})
            nodes.append({"name": name, "quantity": T.q(self.leaves[name]), "unit": uid})
        for step in self.steps.values():
            if step["name"] in needed:
                nodes.append({"name": step["name"], "quantity": T.q(step["formula"]),
                              "premises": step["premises"], "certificate": step["certificate"]})
        return {"units": units, "graph": {"root": root["name"], "nodes": nodes}}


def label(f):
    return f[1] + "." + ".".join(t[1] for t in f[2:])


# --- answers -------------------------------------------------------------------------------------------------

def answer(staged, question):
    """One question's answer from the established steps -> (answer dict, [targets its documents root at])."""
    form, U = question["form"], T.U
    if form == "qualify":  # Q1
        v = staged.truth(U("qualifies", T.CL))
        return ({"answer": "YES" if v else "NO"}, [T.key(U("qualifies", T.CL))]) if v is not None else ({"answer": "OPEN"}, [])
    bp = staged.truth(U("bp", T.CL))
    if bp is False:
        return {"answer": "NONE"}, [T.key(U("bp", T.CL))]
    if bp is None:
        return {"answer": "OPEN"}, []
    if form == "maxweeks":  # Q2
        v = staged.value("maxweeks")
        return ({"answer": "WEEKS", "weeks": int(v[2])}, [T.key(U("bp", T.CL)), "maxweeks"]) if v else ({"answer": "OPEN"}, [])
    if form == "rate":  # Q3
        v = staged.value("benefit")
        return ({"answer": "CAD", "cad": v[2]}, [T.key(U("bp", T.CL)), "benefit"]) if v else ({"answer": "OPEN"}, [])
    raise ValueError(form)


def roots_for(case):
    U = T.U
    return [T.key(U("qualifies", T.CL)), T.key(U("bp", T.CL)), "maxweeks", "benefit"]


def lean(cases):
    from ve.backends.relay import rows
    results = rows("quantity", cases)
    assert [r["id"] for r in results] == [c["id"] for c in cases]
    return results


def unit_map(ctx):
    return {n: u for n, (u, _) in T.int_constants(ctx).items()}


def run_case(case, mutant=None, prover=None):
    import encode as E
    ctx = E.context(case)
    env_raw = T.environment(ctx)
    prover = prover or Prover(Environment(env_raw))
    rules = T.rules(ctx, mutant)
    facts = E.facts(case)
    staged = Staged(prover, rules, facts)
    staged.run(unit_map(ctx), roots_for(case))
    answers, targets = {}, {}
    for qn in case["questions"]:
        a, ts = answer(staged, qn)
        answers[qn["qid"]] = a
        targets[qn["qid"]] = ts
    return answers, targets, staged, rules, facts, env_raw


def _case_task(case):
    t0 = time.time()
    answers, targets, staged, rules, facts, env_raw = run_case(case)
    rec = {"id": case["id"], "staged": answers, "rules": len(rules), "facts": len(facts),
           "constraints": staged.check_constraints(),
           "steps": [{k: v for k, v in e.items() if k != "premises"} | {"premise_count": len(e["premises"])}
                     for e in staged.log],
           "encoder_judgement": case.get("judgement", []), "targets": targets, "prove_seconds": round(time.time() - t0, 1)}
    lean_cases = []
    for step in staged.steps.values():
        lean_cases.append({"id": f"{case['id']}/cert/{step['name']}", "kind": "certificate",
                           "environment": env_raw, "premises": [T.q(staged.formula(n)) for n in step["premises"]],
                           "conclusion": T.q(step["formula"]), "certificate": step["certificate"]})
    docs = sorted({t for ts in targets.values() for t in ts})
    for i, t in enumerate(docs):
        lean_cases.append({"id": f"{case['id']}/doc/{i}", "kind": "document", "environment": env_raw,
                           "document": staged.document(t), "_target": t})
    return rec, lean_cases, Environment(env_raw).environment_id


def _mutant_task(item):
    mutant, case, base = item
    got = run_case(case, mutant)[0]
    return mutant, [q for q in got if got[q] != base[q]]


def _forward_view(case, mutant=None):
    import encode as E
    ctx = E.context(case)
    fw = Forward(T.rules(ctx, mutant), E.facts(case))
    return (fw.truths.get(T.key(T.U("qualifies", T.CL))), fw.vals.get("maxweeks"), fw.vals.get("benefit"))


def mutant_cases(cases, per=3):
    """Where each planted error is run with full proofs: the first `per` cases (by id) whose forward-evaluated view
    (qualifies, maxweeks, benefit) the error changes. Selection only: the kill itself is the staged, proved answers."""
    base = {c["id"]: _forward_view(c) for c in cases}
    return {m: [c for c in cases if _forward_view(c, m) != base[c["id"]]][:per] for m in T.MUTANTS}


def main(argv=None):
    import cases as K
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases")
    ap.add_argument("--mutants", action="store_true")
    ap.add_argument("--no-lean", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args(argv)
    started = time.time()
    cases = K.CASES
    if args.cases:
        cases = [c for c in cases if c["id"] in args.cases.split(",")]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        done = list(pool.map(_case_task, cases))
    records, lean_cases, env_ids = [], [], {}
    for rec, lcs, eid in done:
        records.append(rec)
        lean_cases += lcs
        env_ids[rec["id"]] = eid
    doc_target = {lc["id"]: lc.pop("_target") for lc in lean_cases if "_target" in lc}
    t_lean = time.time()
    lean_results = {} if args.no_lean else {r["id"]: r for r in lean(lean_cases)}
    lean_seconds = round(time.time() - t_lean)
    for rec in records:
        cid = rec["id"]
        mine = {kk: v for kk, v in lean_results.items() if kk.startswith(cid + "/")}
        certs = [v for kk, v in mine.items() if "/cert/" in kk]
        admitted = {doc_target[kk] for kk, v in mine.items() if "/doc/" in kk
                    and v.get("status") == "ok" and v.get("assurance") == "lean-admitted"}
        rec["lean"] = {"certificates": len(certs),
                       "certificates_accepted": sum(r.get("status") == "ok" and r.get("valid") is True for r in certs),
                       "documents": len([kk for kk in mine if "/doc/" in kk]), "documents_admitted": len(admitted)}
        answers = {}
        for qid, a in rec["staged"].items():
            ts = rec["targets"][qid]
            if a["answer"] != "OPEN" and not args.no_lean and not all(t in admitted for t in ts):
                answers[qid] = {"answer": "OPEN", "lean_rejected": True}
            else:
                answers[qid] = a
        rec["answers"] = answers
    for cid, why in K.PROBES.items():
        if not args.cases or cid in args.cases.split(","):
            records.append({"id": cid, "scope": "out", "unsupported": why,
                            "answers": {qid: {"answer": "UNSUPPORTED"} for qid in K.PROBE_QIDS[cid]}})
    for cid, (why, qids) in K.UNSUPPORTED.items():
        if not args.cases or cid in args.cases.split(","):
            records.append({"id": cid, "scope": "in", "unsupported": why,
                            "answers": {qid: {"answer": "UNSUPPORTED"} for qid in qids}})
    mutants = {}
    if args.mutants:
        base = {q: a for r in records if "staged" in r for q, a in r["staged"].items()}
        changed = {m: [] for m in T.MUTANTS}
        sel = mutant_cases(cases)
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for m, ch in pool.map(_mutant_task, [(m, c, base) for m in T.MUTANTS for c in sel[m]]):
                changed[m] += ch
        for m, (desc, _) in T.MUTANTS.items():
            mutants[m] = {"description": desc, "run_on": [c["id"] for c in sel[m]], "changed": changed[m],
                          "killed": bool(changed[m])}
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "usecases/ei_canada"],
                           capture_output=True, text=True).stdout.strip()
    encf = HERE / "questions-enc.jsonl"
    enc = hashlib.sha256(encf.read_bytes()).hexdigest() if encf.exists() else None
    out = {"format": "ei-canada-run@1", "label": "SAME-FAMILY", "commit": commit, "tree_clean": dirty == "",
           "questions_enc_sha256": enc, "translation_sha256": T.translation_sha256(), "environment_ids": env_ids,
           "lean_cases": len(lean_cases), "lean_seconds": lean_seconds, "records": records, "mutants": mutants,
           "seconds": round(time.time() - started)}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print("run file", args.out, hashlib.sha256(text.encode()).hexdigest())
    summary = {}
    for r in records:
        for qid, a in r["answers"].items():
            summary[a["answer"]] = summary.get(a["answer"], 0) + 1
    print(json.dumps({"summary": summary, "seconds": out["seconds"], "lean_seconds": lean_seconds, "commit": commit,
                      "clean": out["tree_clean"], "mutants": {m: v["killed"] for m, v in mutants.items()}}, indent=1))
    return out


if __name__ == "__main__":
    main()
