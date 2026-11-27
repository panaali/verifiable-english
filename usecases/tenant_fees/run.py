"""Run VE on the Tenant Fees Act cases (cases.py) and write the run file. SAME-FAMILY. The sealed answers are NOT read here.

Protocol (the staged route of usecases/pawhp/run.py, generalised; Staged/Prover adapted from it):
1. Ground the rules over the case's items (translation.rules), take the encoder's facts (cases.py).
2. Each derived atom is one step, proved (both polarities) from the rules that define it, the facts its rules mention and
   earlier steps. Each asked amount or date (proh_x, repay_x, repaylast_x) is one step over CANDIDATE values; the
   candidates come from a generic evaluator of the ground equations (eq / shift_days with one unknown) and a sentinel
   that no consistent premise set proves. One certificate -> the step holds; two or more -> inconsistent (refused);
   none -> OPEN. The candidate list is a search aid only: a value counts only through its certificate.
3. Lean replays every step certificate and admits one documents@1 quantity document per answer target; an answer counts
   only if Lean admitted every document it uses (else OPEN).
4. --mutants: each planted error (translation.MUTANTS) is run over all cases; it must change at least one answer.

Usage (repository root): uv run python -B usecases/tenant_fees/run.py [--cases T001,T002] [--mutants] [--out FILE]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
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

ASKED_BASES = ("proh", "repay", "repaylast")
SENTINEL = {T.GBP: ["decimal", T.GBP, "-0.01"], T.DAY: ["date", "1970-01-01"]}


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


# --- generic candidate evaluator (search aid; never an answer source) -----------------------------------------

def _num(term):
    """A literal term -> exact value in its unit's coordinates (pence / day number), else None."""
    if term[0] == "decimal":
        return Fraction(term[2]) * 100 if term[1] == T.GBP else Fraction(term[2])
    if term[0] == "date":
        return Fraction((dt.date.fromisoformat(term[1]) - dt.date(1970, 1, 1)).days)
    return None


def _lin(term):
    """term -> ({constant: coeff}, offset) or None."""
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


def _equations(f, out):
    if type(f) is not list or not f:
        return
    if f[0] == "eq":
        a, b = _lin(f[1]), _lin(f[2])
        if a is not None and b is not None:
            d = dict(a[0])
            for n, cf in b[0].items():
                d[n] = d.get(n, 0) - cf
            out.append((d, b[1] - a[1]))  # sum d*x = rhs
        return
    if f[0] == "shift_days":
        a, b = _lin(f[1]), _lin(f[2])
        if a is not None and b is not None:
            d = dict(a[0])
            for n, cf in b[0].items():
                d[n] = d.get(n, 0) - cf
            out.append((d, b[1] - a[1] + int(f[3])))
        return
    for part in f[1:]:
        _equations(part, out)


def candidates(formulas, units, stated=()):
    """Every value any ground equation gives a constant once the others are known (fixpoint over alternatives)."""
    eqs = []
    for f in formulas:
        _equations(f, eqs)
    known, fixed = {}, set()
    for d, rhs in eqs:  # stated literal values are fixed: never re-solved from another equation
        d = {n: cf for n, cf in d.items() if cf != 0}
        if len(d) == 1 and next(iter(d)) in stated:
            (n, cf), = d.items()
            fixed.add(n)
            known.setdefault(n, set()).add(rhs / cf)
    for _ in range(8):
        grew = False
        for d, rhs in eqs:
            d = {n: cf for n, cf in d.items() if cf != 0}
            for u in d:
                if u in fixed or any(n not in known for n in d if n != u):
                    continue
                options = [rhs]
                for n in d:
                    if n != u:
                        options = [o - d[n] * v for o in options for v in sorted(known[n])]
                vals = {o / d[u] for o in options}
                vals = {v for v in vals if v.denominator == 1}
                if vals and not vals <= known.get(u, set()):
                    known.setdefault(u, set()).update(vals)
                    grew = True
                if len(known.get(u, ())) > 40:
                    return known
        if not grew:
            break
    return known


def literal(unit, v):
    if unit == T.GBP:
        v = int(v)
        sign = "-" if v < 0 else ""
        return ["decimal", T.GBP, f"{sign}{abs(v) // 100}.{abs(v) % 100:02d}"]
    return ["date", (dt.date(1970, 1, 1) + dt.timedelta(days=int(v))).isoformat()]


class Staged:
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

    def is_step_constant(self, name):
        return name.split("_", 1)[0] in ASKED_BASES

    def truth(self, f):
        """True/False if an atom (or its negation) is a stated fact or an established step, else None."""
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
        """A rule 'A -> C' whose A has a conjunct already known false never fires: not sent as a premise
        (selection only: dropping a premise can lose a proof, never make one)."""
        if formula[0] != "implies":
            return False
        parts, stack = [], [formula[1]]
        while stack:
            p = stack.pop()
            if p[0] == "and" and not T.is_iff(p):
                stack += [p[1], p[2]]
            else:
                parts.append(p)
        return any(self.truth(p) is False for p in parts)

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
                names = self.premises_for(t)
                vals = candidates([self.formula(n) for n in names], units, set(self.fact_constants)).get(t, set())
                unit = units[t]
                cands = [["eq", ["const", unit, t], literal(unit, v)] for v in sorted(vals)]
                cands.append(["eq", ["const", unit, t], SENTINEL[unit]])
                self.attempt(t, t, cands)

    def known(self, f):
        step = self.steps.get(T.key(f))
        return None if step is None else step["formula"] == f

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


def money(term):
    return None if term is None else term[2]


# --- answers -------------------------------------------------------------------------------------------------

def grade_part(staged, x, pr):
    """The prompt's Q1 words: YES none prohibited; PART permitted only up to an amount; NO wholly prohibited (a
    permitted kind whose whole amount is excess, e.g. a cap of 0, is 'wholly prohibited'). The amount comparison reads
    the stated amount fact; OPEN if it is not stated."""
    if pr[2] == "0.00":
        return "YES"
    amt = [f["formula"][2][2] for f in staged.fact_constants.get(f"amt_{x}", []) if f["formula"][0] == "eq"]
    if not amt:
        return "OPEN"
    return "NO" if amt[0] == pr[2] else "PART"


def answer(staged, question):
    """One question's answer from the established steps -> (answer dict, [targets its documents root at])."""
    x, form = question["item"], question["form"]
    U = T.U
    if form == "permitted":  # Q1 "Is <x> a permitted payment?"
        p = staged.truth(U("permitted", x))
        pr = staged.value(f"proh_{x}")
        if p is False:
            return {"answer": "NO"}, [T.key(U("permitted", x))]
        if p is True and pr is not None:
            return {"answer": grade_part(staged, x, pr)}, [T.key(U("permitted", x)), f"proh_{x}"]
        return {"answer": "OPEN"}, []
    if form == "s1":  # Q1 "Does section 1 allow the landlord to require <x>?"
        e = staged.truth(U("engaged", x))
        if e is False:
            return {"answer": "YES"}, [T.key(U("engaged", x))]
        if e is True:
            pay = staged.truth(U("is_payment", x))
            b = staged.truth(U("breach", x))
            if b is False:
                return {"answer": "YES"}, [T.key(U("engaged", x)), T.key(U("breach", x))]
            if b is True and pay is not True:
                return {"answer": "NO"}, [T.key(U("engaged", x)), T.key(U("breach", x))]
            p = staged.truth(U("permitted", x))
            if b is True and p is False:
                return {"answer": "NO"}, [T.key(U("engaged", x)), T.key(U("breach", x)), T.key(U("permitted", x))]
            pr = staged.value(f"proh_{x}")
            if b is True and p is True and pr is not None:
                return ({"answer": grade_part(staged, x, pr)},
                        [T.key(U("engaged", x)), T.key(U("breach", x)), T.key(U("permitted", x)), f"proh_{x}"])
        return {"answer": "OPEN"}, []
    if form == "amount":  # Q2
        pr = staged.value(f"proh_{x}")
        return ({"answer": "AMOUNT", "gbp": pr[2]}, [f"proh_{x}"]) if pr is not None else ({"answer": "OPEN"}, [])
    if form == "repay":  # Q3
        m = staged.truth(U("must_repay", x))
        if m is False:
            return {"answer": "NO"}, [T.key(U("must_repay", x))]
        if m is True:
            amt = staged.value(f"repay_{x}")
            m3 = staged.truth(U("must_repay3", x))
            if amt is None or m3 is None:
                return {"answer": "OPEN"}, []
            if m3 is False:
                return ({"answer": "YES", "gbp": amt[2], "date": "NONE"},
                        [T.key(U("must_repay", x)), T.key(U("must_repay3", x)), f"repay_{x}"])
            last = staged.value(f"repaylast_{x}")
            if last is None:
                return {"answer": "OPEN"}, []
            return ({"answer": "YES", "gbp": amt[2], "date": last[1] if last[0] == "date" else None},
                    [T.key(U("must_repay", x)), T.key(U("must_repay3", x)), f"repay_{x}", f"repaylast_{x}"])
        return {"answer": "OPEN"}, []
    raise ValueError(form)


def roots_for(case):
    """The atoms and constants the asked questions read (answer())."""
    U, out = T.U, []
    for qn in case["questions"]:
        x = qn["item"]
        if qn["form"] == "permitted":
            out += [T.key(U("permitted", x)), f"proh_{x}"]
        elif qn["form"] == "s1":
            out += [T.key(U("engaged", x)), T.key(U("breach", x)), T.key(U("permitted", x))]
        elif qn["form"] == "amount":
            out += [f"proh_{x}"]
        elif qn["form"] == "repay":
            out += [T.key(U("must_repay", x)), T.key(U("must_repay3", x)), f"repay_{x}", f"repaylast_{x}"]
    return out


def lean(cases):
    from ve.backends.relay import rows
    results = rows("quantity", cases)
    assert [r["id"] for r in results] == [c["id"] for c in cases]
    return results


def unit_map(ctx):
    out = {}
    for x in ctx.items:
        for base, (u, _) in T.INT_UNITS.items():
            out[f"{base}_{x}"] = u
    for n, (u, _) in T.CASE_INTS.items():
        out[n] = u
    return out


def run_case(case, mutant=None, prover=None):
    import encode as E
    ctx = T.Ctx(case["items"], case.get("links", ()))
    env_raw = T.environment(ctx)
    prover = prover or Prover(Environment(env_raw))
    rules = T.rules(ctx, mutant)
    facts = E.facts(case)
    staged = Staged(prover, rules, facts)
    staged.run(unit_map(ctx), roots_for(case))
    answers = {}
    targets = {}
    for qn in case["questions"]:
        a, ts = answer(staged, qn)
        answers[qn["qid"]] = a
        targets[qn["qid"]] = ts
    return answers, targets, staged, rules, facts, env_raw


def _mutant_task(item):
    mutant, cases, base = item
    changed = []
    for c in cases:
        got = run_case(c, mutant)[0]
        changed += [q for q in got if got[q] != base[q]]
    return mutant, changed


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
    records, lean_cases, env_ids = [], [], {}
    for case in cases:
        answers, targets, staged, rules, facts, env_raw = run_case(case)
        env_ids[case["id"]] = Environment(env_raw).environment_id
        rec = {"id": case["id"], "staged": answers, "rules": len(rules), "facts": len(facts),
               "constraints": staged.check_constraints(),
               "steps": [{k: v for k, v in e.items() if k != "premises"} | {"premise_count": len(e["premises"])}
                         for e in staged.log],
               "encoder_judgement": case.get("judgement", []), "targets": targets}
        records.append(rec)
        for step in staged.steps.values():
            lean_cases.append({"id": f"{case['id']}/cert/{step['name']}", "kind": "certificate",
                               "environment": env_raw, "premises": [T.q(staged.formula(n)) for n in step["premises"]],
                               "conclusion": T.q(step["formula"]), "certificate": step["certificate"]})
        docs = sorted({t for ts in targets.values() for t in ts})
        for i, t in enumerate(docs):
            lean_cases.append({"id": f"{case['id']}/doc/{i}", "kind": "document", "environment": env_raw,
                               "document": staged.document(t), "_target": t})
    doc_target = {lc["id"]: lc.pop("_target") for lc in lean_cases if "_target" in lc}
    lean_results = {} if args.no_lean else {r["id"]: r for r in lean(lean_cases)}
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
        from concurrent.futures import ProcessPoolExecutor
        base = {q: a for r in records if "staged" in r for q, a in r["staged"].items()}
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            changed = dict(pool.map(_mutant_task, [(m, cases, base) for m in T.MUTANTS]))
        for m, (desc, _) in T.MUTANTS.items():
            mutants[m] = {"description": desc, "changed": changed[m], "killed": bool(changed[m])}
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "usecases/tenant_fees"],
                           capture_output=True, text=True).stdout.strip()
    enc = hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest()
    out = {"format": "tenant-fees-run@1", "label": "SAME-FAMILY", "commit": commit, "tree_clean": dirty == "",
           "questions_enc_sha256": enc, "translation_sha256": T.translation_sha256(), "environment_ids": env_ids,
           "lean_cases": len(lean_cases), "records": records, "mutants": mutants,
           "seconds": round(time.time() - started)}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print("run file", args.out, hashlib.sha256(text.encode()).hexdigest())
    summary = {}
    for r in records:
        for qid, a in r["answers"].items():
            summary[a["answer"]] = summary.get(a["answer"], 0) + 1
    print(json.dumps({"summary": summary, "seconds": out["seconds"], "commit": commit, "clean": out["tree_clean"],
                      "mutants": {m: v["killed"] for m, v in mutants.items()}}, indent=1))
    return out


if __name__ == "__main__":
    main()
