"""Run VE on the GitHub Copilot Extension Developer Policy cases (cases.py; statute corpus batch 4, NON-STATUTE (c),
STAND-IN) and write the run file. CROSS-FAMILY questions (Codex writer), Opus translator. The sealed answers are NOT read here.

Protocol (the council_tax / pawhp staged route):
1. Ground the rules over the sub-case's items (translation.rules), take the encoder's facts (encode.build).
2. Each derived atom is one step, proved (both polarities) from the rules that define it, the facts its rules mention and
   earlier steps. Each step constant (translation.STEP_BASES) is one step over CANDIDATE values from a generic evaluator of
   the ground equations (eq / shift_days / elapsed_days with one unknown) plus a sentinel no consistent premise set proves.
   One certificate -> the step holds; two or more, or the sentinel -> inconsistent (refused); none -> OPEN. The candidate
   list is a search aid only: a value counts only through its certificate.
3. Lean replays every step certificate and admits one documents@1 quantity document per answer target; an answer counts
   only if Lean admitted every document it uses (else OPEN).
4. --mutants: each planted error (translation.MUTANTS) is run over all cases (staged route, no Lean); it must change at
   least one answer.

Usage (repository root): .venv/bin/python -B usecases/copilot_ext_policy/run.py [--cases G001,G002] [--mutants] [--no-lean] [--out FILE]
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

sys.setrecursionlimit(200000)
SENTINEL = {T.DAY: ["date", "9999-12-31"]}


class Prover:
    """ve.units.prove_quantity with Lean's per-statement admission rows cached and batched (one relay call per attempt
    for the statements not seen yet). The generator is untrusted either way: Lean replays every certificate."""

    def __init__(self, env):
        from ve.units import erased_environment
        self.env, self.cache, self.calls, self.searches = env, {}, 0, 0
        self.target = erased_environment(env)
        self.envd = env.to_dict()
        self.rows = {}

    def warm(self, formulas):
        from ve.backends.relay import decide
        todo = []
        for f in formulas:
            kk = T.key(f)
            if kk not in self.rows and kk not in [t[0] for t in todo]:
                todo.append((kk, f))
        for i in range(0, len(todo), 200):
            part = todo[i:i + 200]
            rows = decide("quantity", [{"id": f"q{n}", "environment": self.envd, "quantity": T.q(f)}
                                       for n, (_, f) in enumerate(part)])
            for (kk, _), row in zip(part, rows):
                if row["environment_id"] != self.env.environment_id:
                    from ve.errors import CheckerUnavailable
                    raise CheckerUnavailable("CheckerUnavailable: W6 environment identity mismatch")
                self.rows[kk] = row

    def prove(self, premises, conclusion):
        self.calls += 1
        kk = T.key([premises, conclusion])
        if kk not in self.cache:
            self.searches += 1
            self.cache[kk] = self._prove(premises, conclusion)
        return self.cache[kk]

    def _prove(self, premises, conclusion):
        from ve.ast import formula_from_data
        from ve.entailment import prove_entailment
        from ve.units import CERTIFICATE_FORMAT, check_quantity_limits
        self.warm([*premises, conclusion])
        rows = [self.rows[T.key(f)] for f in (*premises, conclusion)]
        ids = [row["meaning_id"] for row in rows]
        cores = [formula_from_data(self.target, row["core"]) for row in rows]
        check_quantity_limits(cores)
        result = prove_entailment(self.target, cores[:-1], cores[-1], max_steps=10_000)
        if result.certificate is None:
            return None
        return {"format": CERTIFICATE_FORMAT, "environment_id": self.env.environment_id,
                "premise_meaning_ids": ids[:-1], "conclusion_meaning_id": ids[-1], "core": result.certificate}


# --- generic candidate evaluator (search aid; never an answer source) -----------------------------------------

def _num(term):
    """A literal term -> exact value in its unit's coordinates (pence / day number), else None."""
    if term[0] == "decimal":
        return Fraction(term[2])
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
    if f[0] == "elapsed_days":  # elapsed from a to b equals n: n - b + a = 0
        a, b, n = _lin(f[1]), _lin(f[2]), _lin(f[3])
        if a is not None and b is not None and n is not None:
            d = dict(n[0])
            for nm, cf in b[0].items():
                d[nm] = d.get(nm, 0) - cf
            for nm, cf in a[0].items():
                d[nm] = d.get(nm, 0) + cf
            out.append((d, b[1] - a[1] - n[1]))
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
    if unit == T.DAY:
        return ["date", (dt.date(1970, 1, 1) + dt.timedelta(days=int(v))).isoformat()]
    return ["decimal", unit, str(int(v))]


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
            if not r["defines"] or [t for t in r["defines"] if t in self.fact_atoms]:
                self.constraints.append(r)
                continue
            for target in r["defines"]:
                self.defs.setdefault(target, []).append(r)
        self.leaves = {f"rule:{r['id']}": r["formula"] for r in rules}
        self.leaves.update({f"fact:{f['id']}": f["formula"] for f in facts})
        self.steps, self.log = {}, []

    def is_step_constant(self, name):
        return name.split("_", 1)[0] in T.STEP_BASES

    def term_value(self, term):
        """A term's exact value when every constant in it is a stated literal or an established step (selection only)."""
        lin = _lin(term)
        if lin is None:
            return None
        coeffs, off = lin
        total = off
        for name, cf in coeffs.items():
            v = None
            if name in self.steps and self.steps[name]["formula"][0] == "eq":
                v = _num(self.steps[name]["formula"][2])
            else:
                for fact in self.fact_constants.get(name, []):
                    g = fact["formula"]
                    if g[0] == "eq" and g[1] == ["const", g[1][1], name] and _num(g[2]) is not None:
                        v = _num(g[2])
            if v is None:
                return None
            total += cf * v
        return total

    def truth(self, f):
        """True/False if an atom (or its negation) is a stated fact or an established step, else None."""
        if f[0] == "not":
            v = self.truth(f[1])
            return None if v is None else not v
        if f[0] in ("le", "lt", "date_no_later", "date_before"):
            x, y = self.term_value(f[1]), self.term_value(f[2])
            if x is None or y is None:
                return None
            return x <= y if f[0] in ("le", "date_no_later") else x < y
        if f[0] == "and" and not T.is_iff(f):
            vs = [self.truth(f[1]), self.truth(f[2])]
            if False in vs:
                return False
            return True if vs == [True, True] else None
        if f[0] == "eq" and f[1][0] == "const" and len(f[1]) == 3 and f[2][0] == "decimal":
            v = self.value(f[1][2])   # an established step constant against a literal (selection only)
            return None if v is None else _num(v) == _num(f[2])
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
        self.prover.warm(premises + list(cands))
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
        return None if step is None or step["formula"][0] != "eq" else step["formula"][2]

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
            for cname in sorted(cs):
                facts += [f["formula"] for f in self.fact_constants.get(cname, [])]
                if cname in self.steps:
                    facts.append(self.steps[cname]["formula"])
            cert = self.prover.prove(facts + [r["formula"]], ["bottom"])
            out.append({"rule": r["id"], "contradicted": cert is not None})
        return out

    def document(self, root_target, cut=None):
        """A documents@1 quantity document rooted at a step. cut(step) marks earlier steps that enter as ASSERTED leaves
        (each proved by its own document: documents_for); returns (document, [keys of the cut steps it asserts])."""
        root = self.steps[root_target]
        by_name = self.by_name
        key_of = {st["name"]: kk for kk, st in self.steps.items()}
        needed, cut_leaves, stack = set(), set(), [root["name"]]
        while stack:
            name = stack.pop()
            if name in needed or name in cut_leaves:
                continue
            if cut is not None and name != root["name"] and name in by_name and cut(name):
                cut_leaves.add(name)
                continue
            needed.add(name)
            if name in by_name:
                stack.extend(by_name[name]["premises"])
        leaf_names = [n for n in self.leaves if n in needed]
        units, nodes = [], []
        for i, name in enumerate(leaf_names + sorted(cut_leaves)):
            uid = "u" + str(i)
            f = self.leaves[name] if name in self.leaves else by_name[name]["formula"]
            units.append({"id": uid, "span": [i, i + 1], "kind": "asserted", "content": T.q(f)})
            nodes.append({"name": name, "quantity": T.q(f), "unit": uid})
        for step in self.steps.values():
            if step["name"] in needed:
                nodes.append({"name": step["name"], "quantity": T.q(step["formula"]),
                              "premises": step["premises"], "certificate": step["certificate"]})
        return {"units": units, "graph": {"root": root["name"], "nodes": nodes}}, sorted(key_of[n] for n in cut_leaves)

    def documents_for(self, root_target, built):
        """The chain of documents that together establish root_target: its own, cut at the chain's carried values
        (CHAIN_CUT), and one for each carried value it asserts, recursively. built: key -> document (shared)."""
        todo, chain = [root_target], []
        while todo:
            t = todo.pop()
            if t in chain:
                continue
            chain.append(t)
            if t not in built:
                built[t] = self.document(t, cut=chain_cut)
            todo += built[t][1]
        return chain


CHAIN_CUT = ("forbidden", "inforce", "ends", "pd", "required", "last_")


def chain_cut(name):
    """Carried values: an act's forbidden / ends / pd classification, a day's in-force status, a duty's required status
    and a deletion's latest day (each proved by its own document: Lean's 1,000-node document limit)."""
    body = name.split(":", 1)[1]
    return body.split(".", 1)[0] in CHAIN_CUT or body.startswith("last_")


def label(f):
    return f[1] + "." + ".".join(t[1] for t in f[2:])


def money(term):
    return None if term is None else term[2]


# --- answers -------------------------------------------------------------------------------------------------

FORMS = {  # form -> (atom, yes-word when true, yes-word when false)
    "may": ("forbidden", "no", "yes"),          # Q1 a developer / Extension act (R1)
    "may_gh": ("ghmay", "yes", None),            # Q1 a GitHub act (R2, R11): only "yes" is derived
    "must": ("required", "yes", "no"),           # Q2 a duty item (R2)
    "inforce": ("inforce", "yes", "no"),         # Q2 the Agreement on a day (R8)
    "bound": ("bound", "yes", "no"),             # Q2 a duty on a day (R9)
    "met": ("met", "yes", "no"),                 # Q3 yes/no (R7)
    "keep": ("keep_ok", "yes", "no"),            # Q1 may the developer still hold the data on a day (R7)
    # added after questions-enc.jsonl was read (answer layer only; no rule changed): "must <developer> change / add /
    # replace X (so that ...)" asks whether the act as it stands fails a clause: yes when it is forbidden, no when not
    "must_cure": ("forbidden", "yes", "no"),
}


def answer(staged, question, ctx, refused):
    """One question's answer from the established steps -> (answer dict, [targets its documents root at])."""
    if refused:
        return {"answer": "OPEN", "refused": refused}, []
    x, form = question["item"], question["form"]
    if form == "last":                            # Q3 the latest day (R7)
        v = staged.value(f"last_{x}")
        if v is None or v[0] != "date":
            return {"answer": "OPEN"}, []
        return {"answer": "DATE", "value": v[1]}, [f"doc:last_{x}"]
    atom, if_true, if_false = FORMS[form]
    t = staged.known(T.U(atom, x))
    if t is None or (t is False and if_false is None):
        return {"answer": "OPEN"}, []
    return {"answer": if_true if t else if_false}, ["doc:" + T.A(atom, x)]


def roots_for(sub, ctx):
    out = []
    for qn in sub["questions"]:
        x = qn["item"]
        out += [f"last_{x}"] if qn["form"] == "last" else [T.A(FORMS[qn["form"]][0], x)]
    return out


def _lean_chunk(chunk):
    from ve.backends.relay import rows
    out = []
    for i in range(0, len(chunk), 40):   # small requests: one sub-case's long chain fits Lean's request deadline
        part = chunk[i:i + 40]
        res = rows("quantity", part, timeout=3600)
        assert [r["id"] for r in res] == [c["id"] for c in part]
        out += res
    return out


def lean(cases, workers=6):
    """Lean's rows for every certificate and document, one worker per sub-case (ids '<case>/s<k>/...')."""
    from concurrent.futures import ProcessPoolExecutor
    groups = {}
    for c in cases:
        groups.setdefault(c["id"].split("/cert/")[0].split("/doc/")[0], []).append(c)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        parts = list(pool.map(_lean_chunk, list(groups.values())))
    results = [r for part in parts for r in part]
    assert sorted(r["id"] for r in results) == sorted(c["id"] for c in cases)
    return results


def unit_map(ctx):
    out = {}
    for x, kind in ctx.items:
        for base, (u, _) in T.KINDS[kind].items():
            out[f"{base}_{x}"] = u
    return out


def used_constants(rules, facts):
    a, cs = set(), set()
    for r in rules:
        T.atoms_in(r["formula"], a, cs)
    for f in facts:
        T.atoms_in(f["formula"], a, cs)
    return cs


def run_sub(sub, mutant=None):
    """sub: {"spec": encode.Spec, "questions": [{"qid", "form", "month"}]} -> answers, targets, ..."""
    import encode as E
    ctx, facts = E.build(sub["spec"])
    qs = [dict(qn) for qn in sub["questions"]]
    rules = T.rules(ctx, mutant)
    env_raw = T.environment(ctx, used_constants(rules, facts))
    prover = Prover(Environment(env_raw))
    staged = Staged(prover, rules, facts)
    prover.warm([f["formula"] for f in facts])
    staged.run(unit_map(ctx), roots_for({"questions": qs}, ctx))
    checks = staged.check_constraints()
    refused = "facts contradict a rule" if any(c["contradicted"] for c in checks) else None
    answers, targets = {}, {}
    for qn in qs:
        a, ts = answer(staged, qn, ctx, refused)
        answers[qn["qid"]] = a
        targets[qn["qid"]] = ts
    return answers, targets, staged, rules, facts, env_raw, checks, ctx


def run_case(case, mutant=None):
    out = {}
    for sub in case["subs"]:
        out.update(run_sub(sub, mutant)[0])
    return out


def _stage_task(job):
    """One sub-case's staged route in a worker -> its answers, targets, record and Lean cases."""
    import importlib
    sys.setrecursionlimit(200000)
    module, cid, si = job
    K = importlib.import_module(module)
    case = [c for c in K.CASES if c["id"] == cid][0]
    sub = case["subs"][si]
    answers, targets, staged, rules, facts, env_raw, checks, ctx = run_sub(sub)
    tag = f"{cid}/s{si}"
    lean_cases = []
    for step in staged.steps.values():
        lean_cases.append({"id": f"{tag}/cert/{step['name']}", "kind": "certificate",
                           "environment": env_raw, "premises": [T.q(staged.formula(n)) for n in step["premises"]],
                           "conclusion": T.q(step["formula"]), "certificate": step["certificate"]})
    built, chains = {}, {}
    for t in sorted({t[4:] for ts in targets.values() for t in ts if t.startswith("doc:")}):
        chains[t] = staged.documents_for(t, built)
    for i, (t, (doc, _)) in enumerate(sorted(built.items())):
        lean_cases.append({"id": f"{tag}/doc/{i}", "kind": "document", "environment": env_raw,
                           "document": doc, "_target": f"s{si}:doc:{t}"})
    targets = {qid: [x for t in ts for x in (["doc:" + c for c in chains[t[4:]]] if t.startswith("doc:") else [t])]
               for qid, ts in targets.items()}
    cert_of = {f"s{si}:{t}": f"{tag}/cert/{staged.steps[t[5:]]['name']}"
               for ts in targets.values() for t in ts if t.startswith("cert:")}
    bridge_leaves = {f"fact:{f['id']}" for f in facts if f.get("bridge")}
    uses_bridge = {}
    for qid, ts in targets.items():
        names = set()
        for t in ts:
            if t.startswith("doc:"):
                names |= {n["name"] for n in built[t[4:]][0]["graph"]["nodes"]}
        uses_bridge[qid] = bool(names & bridge_leaves)
    info = {"rules": len(rules), "facts": len(facts), "items": ctx.items, "checks": checks, "uses_bridge": uses_bridge,
            "constraints_contradicted": sum(c["contradicted"] for c in checks),
            "steps": [{kk: v for kk, v in e.items() if kk != "premises"} | {"premise_count": len(e["premises"])}
                      for e in staged.log]}
    return {"tag": tag, "environment_id": Environment(env_raw).environment_id, "answers": answers, "targets": targets,
            "sub": info, "lean_cases": lean_cases, "cert_of": cert_of}


def _mutant_sub_task(item):
    import importlib
    sys.setrecursionlimit(200000)
    mutant, module, cid, si, base = item
    K = importlib.import_module(module)
    case = [c for c in K.CASES if c["id"] == cid][0]
    got = run_sub(case["subs"][si], mutant)[0]
    return mutant, [q for q in got if got[q] != base[q]]


def _mutant_task(item):
    mutant, cases, base = item
    sys.setrecursionlimit(200000)
    changed = []
    for c in cases:
        got = run_case(c, mutant)
        changed += [q for q in got if got[q] != base[q]]
    return mutant, changed


def main(argv=None):
    import importlib
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases")
    ap.add_argument("--mutants", action="store_true")
    ap.add_argument("--no-lean", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only-mutants")
    ap.add_argument("--cases-module", default="cases")
    args = ap.parse_args(argv)
    K = importlib.import_module(args.cases_module)
    started = time.time()
    cases = K.CASES
    if args.cases:
        cases = [c for c in cases if c["id"] in args.cases.split(",")]
    records, lean_cases, env_ids = [], [], {}
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(args.cases_module, case["id"], si) for case in cases for si in range(len(case["subs"]))]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        staged_out = dict(zip(jobs, pool.map(_stage_task, jobs)))
    for case in cases:
        rec = {"id": case["id"], "staged": {}, "targets": {}, "subs": [],
               "encoder_judgement": case.get("judgement", [])}
        for si in range(len(case["subs"])):
            r = staged_out[(args.cases_module, case["id"], si)]
            env_ids[r["tag"]] = r["environment_id"]
            rec["staged"].update(r["answers"])
            rec["targets"].update({qid: [f"s{si}:{t}" for t in ts] for qid, ts in r["targets"].items()})
            rec["subs"].append(r["sub"])
            rec.setdefault("cert_of", {}).update(r["cert_of"])
            lean_cases += r["lean_cases"]
        records.append(rec)
    doc_target = {lc["id"]: lc.pop("_target") for lc in lean_cases if "_target" in lc}
    lean_results = {} if args.no_lean else {r["id"]: r for r in lean(lean_cases, args.workers)}
    for rec in records:
        cid = rec["id"]
        mine = {kk: v for kk, v in lean_results.items() if kk.startswith(cid + "/")}
        certs = [v for kk, v in mine.items() if "/cert/" in kk]
        admitted = {doc_target[kk] for kk, v in mine.items() if "/doc/" in kk
                    and v.get("status") == "ok" and v.get("assurance") == "lean-admitted"}
        rec["lean"] = {"certificates": len(certs),
                       "certificates_accepted": sum(r.get("status") == "ok" and r.get("valid") is True for r in certs),
                       "documents": len([kk for kk in mine if "/doc/" in kk]), "documents_admitted": len(admitted)}
        accepted = {kk for kk, v in mine.items() if "/cert/" in kk and v.get("status") == "ok" and v.get("valid") is True}
        ok = lambda t: (t in admitted) if ":doc:" in t else (rec["cert_of"].get(t) in accepted)  # noqa: E731
        answers = {}
        for qid, a in rec["staged"].items():
            ts = rec["targets"][qid]
            if a["answer"] != "OPEN" and not args.no_lean and not all(ok(t) for t in ts):
                answers[qid] = {"answer": "OPEN", "lean_rejected": True}
            else:
                answers[qid] = a
        rec["answers"] = answers
    for cid, why in K.PROBES.items():
        if not args.cases or cid in args.cases.split(","):
            records.append({"id": cid, "scope": "out", "unsupported": why,
                            "answers": {qid: {"answer": "UNSUPPORTED"} for qid in K.PROBE_QIDS[cid]}})
    for cid, qids in getattr(K, "REFUSED", {}).items():   # encoder refusals (cases.py REFUSED): OPEN with the reason
        if not args.cases or cid in args.cases.split(","):
            records.append({"id": cid, "scope": "in", "encoder_refused": True,
                            "answers": {qid: {"answer": "OPEN", "refused": why} for qid, why in qids.items()}})
    for cid, (why, qids) in K.UNSUPPORTED.items():
        if not args.cases or cid in args.cases.split(","):
            records.append({"id": cid, "scope": "in", "unsupported": why,
                            "answers": {qid: {"answer": "UNSUPPORTED"} for qid in qids}})
    mutants = {}
    if args.mutants:
        from concurrent.futures import ProcessPoolExecutor
        base = {q: a for r in records if "staged" in r for q, a in r["staged"].items()}
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            ms = args.only_mutants.split(",") if args.only_mutants else list(T.MUTANTS)
            mjobs = [(m, args.cases_module, case["id"], si, base) for m in ms for case in cases
                     for si in range(len(case["subs"]))]
            changed = {m: [] for m in ms}
            for m, ch in pool.map(_mutant_sub_task, mjobs):
                changed[m] += ch
        for m, (desc, _) in T.MUTANTS.items():
            if m not in changed:
                continue
            mutants[m] = {"description": desc, "changed": changed[m], "killed": bool(changed[m])}
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "usecases/copilot_ext_policy"],
                           capture_output=True, text=True).stdout.strip()
    encp = HERE / "questions-enc.jsonl"
    enc = hashlib.sha256(encp.read_bytes()).hexdigest() if encp.exists() else None
    out = {"format": "copilot-ext-policy-run@1", "label": "CROSS-FAMILY questions, Opus translator", "commit": commit, "tree_clean": dirty == "",
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
