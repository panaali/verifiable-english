"""Run VE on the hours-of-service cases (cases.py; 49 CFR 395.3 + 395.2, statute corpus batch 3 law 2) and write the run file. SAME-FAMILY. The sealed answers are NOT read here.

Protocol (the staged route of usecases/pawhp/run.py, generalised; Staged/Prover adapted from it):
1. Ground the rules over the case's items (translation.rules), take the encoder's facts (cases.py).
2. Each derived atom is one step, proved (both polarities) from the rules that define it, the facts its rules mention and
   earlier steps. Each derived duration or position (every constant a rule defines) is one step over CANDIDATE values; the
   candidates come from a generic evaluator of the ground equations (eq / shift_days with one unknown) and a sentinel
   that no consistent premise set proves. One certificate -> the step holds; two or more -> inconsistent (refused);
   none -> OPEN. The candidate list is a search aid only: a value counts only through its certificate.
3. Lean replays every step certificate and admits one documents@1 quantity document per answer target; an answer counts
   only if Lean admitted every document it uses (else OPEN).
4. --mutants: each planted error (translation.MUTANTS) is run over all cases; it must change at least one answer.

5. Two readings of "off duty" (translation.py): where a case grounds both, an answer needs both and the same value;
   different values = REFUSED (ISOLATION.md D1). Q3 at a moment inside an off-duty run the log continues to 34 hours:
   REFUSED where the answer turns on it (translation.py, fut).

Usage (repository root): uv run python -B usecases/hos_driving/run.py [--cases H001,H002] [--mutants] [--out FILE]
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

SENTINEL = {T.MIN: ["decimal", T.MIN, "-999999"]}


def _memo_checked_quantity():
    """Search-side speed-up: Lean's W6 typing of one annotated statement is a pure function of (environment,
    statement); the certificate generator asks it again for every repeated premise, so it is memoised here. The
    headline still replays every step certificate and admits every answer document in Lean (lean() below)."""
    import ve.units as VU
    if getattr(VU, "_hos_memo", False):
        return
    orig, cache = VU._checked_quantity, {}

    def checked(env, payload):
        kk = (env.environment_id, T.key(payload))
        if kk not in cache:
            cache[kk] = orig(env, payload)
        return cache[kk]
    VU._checked_quantity = checked
    orig_env, envs = VU.erased_environment, {}

    def erased(env):
        if env.environment_id not in envs:
            envs[env.environment_id] = orig_env(env)
        return envs[env.environment_id]
    VU.erased_environment = erased
    VU._hos_memo = True


class Prover:
    def __init__(self, env):
        _memo_checked_quantity()
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
        return Fraction(term[2])
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
    return ["decimal", T.MIN, str(int(v))]


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
        return name in self.defs and name not in self.fact_constants

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
        if any(cand[0] == "eq" and cand[2] in SENTINEL.values() for cand, _ in found):
            # the sentinel is a value no consistent premise set proves: a proof of it means the premises have no
            # model (e.g. D x amount = A with no exact-penny amount), so nothing is established (refused)
            entry["inconsistent"] = True
            return None
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

    def document(self, root_target, cut=frozenset()):
        """The answer document rooted at a step; steps named in `cut` (other than the root) enter as asserted
        units (a checkpoint: each has its own Lean-admitted document, and its formula is the asserted one)."""
        root = self.steps[root_target]
        by_name = self.by_name
        needed, stack = set(), [root["name"]]
        while stack:
            name = stack.pop()
            if name in needed:
                continue
            needed.add(name)
            if name in by_name and (name == root["name"] or name not in cut):
                stack.extend(by_name[name]["premises"])
        leaf_names = [n for n in self.leaves if n in needed]
        cut_names = sorted(n for n in needed if n in cut and n != root["name"])
        units, nodes = [], []
        for i, name in enumerate(leaf_names + cut_names):
            uid = "u" + str(i)
            f = self.leaves[name] if name in self.leaves else by_name[name]["formula"]
            units.append({"id": uid, "span": [i, i + 1], "kind": "asserted", "content": T.q(f)})
            nodes.append({"name": name, "quantity": T.q(f), "unit": uid})
        for step in self.steps.values():
            if step["name"] in needed and (step["name"] == root["name"] or step["name"] not in cut):
                nodes.append({"name": step["name"], "quantity": T.q(step["formula"]),
                              "premises": step["premises"], "certificate": step["certificate"]})
        return {"units": units, "graph": {"root": root["name"], "nodes": nodes}}, cut_names


MAX_NODES = 990   # Lean's documents admit at most 1000 claim-graph nodes (VE.Cardinality.Document.maxGraphNodes)


def _item_of(step_name):
    """step:<pred>.<item> (an atom) or step:<base>_<item> (a constant) -> the item."""
    body = step_name[len("step:"):]
    if body.startswith("["):
        return None
    if "." in body and "_" not in body.split(".", 1)[0]:
        return body.split(".", 1)[1]
    return body.split("_", 1)[1] if "_" in body else None


def documents_for(staged, ctx, roots):
    """Lean documents for the answer roots: one document per root when it fits; otherwise checkpoint documents
    (the step values of every G-th piece, G = 12, 8, 5, 3) each with its own document, cited by later ones.
    -> (docs {doc id key: (root target, document, [cited step names])}, per root the doc keys it uses)."""
    by_name = staged.by_name
    target_of = {s["name"]: t for t, s in staged.steps.items()}
    index = {x: i for i, x in enumerate(ctx.pieces)}
    for g in (None, 12, 8, 5, 3, 2):
        if g is None:
            cut = frozenset()
        else:
            cut = frozenset(n for n in by_name if index.get(_item_of(n), -1) % g == g - 1)
        docs, uses, ok = {}, {}, True

        def build(name):
            if name in docs:
                return
            doc, cited = staged.document(target_of[name], cut)
            docs[name] = (target_of[name], doc, cited)
            for c in cited:
                build(c)
        for r in roots:
            build(staged.steps[r]["name"])
        if all(len(d["graph"]["nodes"]) <= MAX_NODES for (_, d, _) in docs.values()):
            for r in roots:
                seen, stack = set(), [staged.steps[r]["name"]]
                while stack:
                    n = stack.pop()
                    if n in seen:
                        continue
                    seen.add(n)
                    stack += docs[n][2]
                uses[r] = sorted(seen)
            return docs, uses, g
    return docs, {r: None for r in roots}, "too large"


def label(f):
    return f[1] + "." + ".".join(t[1] for t in f[2:])


def _per_reading(staged, ctx, get):
    vals = [get(r) for r in ctx.readings]
    if any(v is None for v in vals):
        return "OPEN"
    if len(set(vals)) > 1:
        return "REFUSED"
    return vals[0]


def answer(staged, ctx, qn):
    """One question's answer from the established steps -> (answer dict, [targets its documents root at])."""
    U, mo = T.U, qn["moment"]
    if not qn["live"] or mo not in ctx.moments:
        return {"answer": "OPEN", "why": "moment not the end of a piece of the log"}, []
    if qn["form"] == "q1":
        v = _per_reading(staged, ctx, lambda r: staged.truth(U(f"may{r}", mo)))
        ts = [T.key(U(f"may{r}", mo)) for r in ctx.readings]
        if v in ("OPEN", "REFUSED"):
            return {"answer": v}, []
        return {"answer": "yes" if v else "no"}, ts
    if qn["form"] == "q2":
        v = _per_reading(staged, ctx, lambda r: None if staged.value(f"rem{r}_{mo}") is None
                         else staged.value(f"rem{r}_{mo}")[2])
        ts = [f"rem{r}_{mo}" for r in ctx.readings]
        if v in ("OPEN", "REFUSED"):
            return {"answer": v}, []
        return {"answer": "DURATION", "minutes": int(v)}, ts
    if qn["form"] == "q3":
        n = qn["n"]

        def get(r):
            rch = staged.truth(U(f"rch{n}{r}", mo))
            fut = staged.truth(U(f"fut{r}", mo))
            if rch is False:
                return "no"
            if rch is True and fut is False:
                return "yes"
            if rch is True and fut is True:
                return "refused-c"
            return None
        v = _per_reading(staged, ctx, get)
        if v in ("OPEN", "REFUSED"):
            return {"answer": v}, []
        if v == "refused-c":
            return {"answer": "REFUSED", "why": "(c): the period could be read as ended by a 34-hour period the log "
                                                "completes after the moment"}, []
        ts = [T.key(U(f"rch{n}{r}", mo)) for r in ctx.readings]
        if v == "yes":
            ts += [T.key(U(f"fut{r}", mo)) for r in ctx.readings]
        return {"answer": v}, ts
    raise ValueError(qn["form"])


def roots_for(ctx, meta):
    U, out = T.U, []
    for qid, qn in meta["questions"].items():
        mo = qn["moment"]
        if mo not in ctx.moments:
            continue
        for r in ctx.readings:
            if qn["form"] == "q1":
                out.append(T.key(U(f"may{r}", mo)))
            elif qn["form"] == "q2":
                out.append(f"rem{r}_{mo}")
            else:
                out += [T.key(U(f"rch{qn['n']}{r}", mo)), T.key(U(f"fut{r}", mo))]
    return out


def lean(cases):
    from ve.backends.relay import rows
    results = rows("quantity", cases)
    assert [r["id"] for r in results] == [c["id"] for c in cases]
    return results


def unit_map(ctx):
    return {f"{base}_{x}": T.MIN for x in ctx.items for base in T.INT_UNITS}


def run_case(case, mutant=None, prover=None):
    import encode as E
    ctx, facts, meta = E.encode(case)
    rules = T.rules(ctx, mutant)
    used = set()
    for f in [r["formula"] for r in rules] + [f["formula"] for f in facts]:
        T.atoms_in(f, set(), used)
    env_raw = T.environment(ctx, used)
    prover = prover or Prover(Environment(env_raw))
    staged = Staged(prover, rules, facts)
    staged.run(unit_map(ctx), roots_for(ctx, meta))
    answers, targets = {}, {}
    for qid, qn in meta["questions"].items():
        a, ts = answer(staged, ctx, qn)
        answers[qid] = a
        targets[qid] = ts
    meta["ctx"] = ctx
    return answers, targets, staged, rules, facts, env_raw, meta


# the cases each planted error is tried on first (a search order only: a mutant runs case after case until one of its
# answers changes; chosen from the case facts, never from the sealed answers)
MUTANT_CASES = {"M10": ("H027", "H026", "H028")}   # the passenger-seat rides next to sleeper-berth time


def _mutant_task(item):
    """One planted error over the cases in order; stops at the first case whose answers change (killed)."""
    mutant, cases, base = item
    changed, ran = [], []
    for c in cases:
        got = run_case(c, mutant)[0]
        ran.append(c["id"])
        changed += [q for q in got if got[q] != base[q]]
        if changed:
            break
    return mutant, changed, ran


def _case_task(item):
    """Staged route for one case, then (unless no_lean) Lean's replay of its certificates and admission of its
    documents -> record."""
    case, no_lean = item
    answers, targets, staged, rules, facts, env_raw, meta = run_case(case)
    ctx = meta["ctx"]
    rec = {"id": case["id"], "staged": answers, "rules": len(rules), "facts": len(facts),
           "environment_id": Environment(env_raw).environment_id,
           "constraints": staged.check_constraints(),
           "steps": [{k: v for k, v in e.items() if k != "premises"} | {"premise_count": len(e["premises"])}
                     for e in staged.log],
           "targets": targets, "pieces": meta["pieces"], "cut_pieces": meta["cut_pieces"],
           "readings": meta["readings"], "prove_calls": staged.prover.calls,
           "stated_vs_clock_mismatch": meta["stated_vs_clock_mismatch"], "bridge": meta["bridge"],
           "activities": meta["activities"]}
    lean_cases = []
    for step in staged.steps.values():
        lean_cases.append({"id": f"{case['id']}/cert/{step['name']}", "kind": "certificate",
                           "environment": env_raw, "premises": [T.q(staged.formula(n)) for n in step["premises"]],
                           "conclusion": T.q(step["formula"]), "certificate": step["certificate"]})
    roots = sorted({t for ts in targets.values() for t in ts})
    docs, uses, grain = documents_for(staged, ctx, roots)
    doc_id = {}
    for i, (name, (t, doc, cited)) in enumerate(sorted(docs.items())):
        doc_id[name] = f"{case['id']}/doc/{i}"
        lean_cases.append({"id": doc_id[name], "kind": "document", "environment": env_raw, "document": doc})
    rec["documents_plan"] = {"checkpoint_every": grain, "documents": len(docs),
                             "max_nodes": max((len(d["graph"]["nodes"]) for (_, d, _) in docs.values()), default=0),
                             "cited_links": sum(len(c) for (_, _, c) in docs.values())}
    if no_lean:
        rec["answers"] = answers
        return rec
    results = {r["id"]: r for r in lean(lean_cases)}
    certs = [v for kk, v in results.items() if "/cert/" in kk]
    admitted = {name for name, i in doc_id.items()
                if results[i].get("status") == "ok" and results[i].get("assurance") == "lean-admitted"}
    errors = sorted({results[i].get("error", "") for name, i in doc_id.items() if name not in admitted})
    rec["lean"] = {"certificates": len(certs),
                   "certificates_accepted": sum(r.get("status") == "ok" and r.get("valid") is True for r in certs),
                   "documents": len(doc_id), "documents_admitted": len(admitted), "document_errors": errors}
    final = {}
    for qid, a in answers.items():
        ts = targets[qid]
        ok = all(uses.get(t) is not None and all(n in admitted for n in uses[t]) for t in ts)
        if a["answer"] not in ("OPEN", "REFUSED") and not ok:
            final[qid] = {"answer": "OPEN", "lean_rejected": True}
        else:
            final[qid] = a
    rec["answers"] = final
    return rec


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
    from concurrent.futures import ProcessPoolExecutor, as_completed
    records, env_ids, done = [], {}, {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(_case_task, (c, args.no_lean)): c["id"]
                for c in sorted(cases, key=lambda c: -len(c["log"]))}
        for fu in as_completed(futs):
            rec = fu.result()
            done[rec["id"]] = rec
            print(f"case {rec['id']} done: {len(rec['steps'])} steps, {rec.get('lean')}, "
                  f"{round(time.time() - started)} s", flush=True)
    for c in cases:
        rec = done[c["id"]]
        env_ids[rec["id"]] = rec.pop("environment_id")
        records.append(rec)
    for cid, qids in K.PROBES.items():
        if not args.cases or cid in args.cases.split(","):
            records.append({"id": cid, "scope": "out", "answers": {qid: {"answer": "UNSUPPORTED"} for qid in qids}})
    mutants = {}
    if args.mutants:
        from concurrent.futures import ProcessPoolExecutor
        base = {q: a for r in records if "staged" in r for q, a in r["staged"].items()}
        order = {m: [c for c in cases if c["id"] in MUTANT_CASES.get(m, ())] +
                 sorted([c for c in cases if c["id"] not in MUTANT_CASES.get(m, ())], key=lambda c: len(c["log"]))
                 for m in T.MUTANTS}
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            res = {m: (ch, ran) for m, ch, ran in pool.map(_mutant_task, [(m, order[m], base) for m in T.MUTANTS])}
        for m, (desc, _) in T.MUTANTS.items():
            mutants[m] = {"description": desc, "changed": res[m][0], "cases_run": res[m][1],
                          "killed": bool(res[m][0])}
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "usecases/hos_driving"],
                           capture_output=True, text=True).stdout.strip()
    enc = hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest()
    out = {"format": "hos-driving-run@1", "label": "SAME-FAMILY", "commit": commit, "tree_clean": dirty == "",
           "questions_enc_sha256": enc, "translation_sha256": T.translation_sha256(), "environment_ids": env_ids,
           "lean_cases": sum(r.get("lean", {}).get("certificates", 0) + r.get("lean", {}).get("documents", 0)
                             for r in records), "records": records, "mutants": mutants,
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
