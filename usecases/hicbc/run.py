"""Run VE on the HICBC in-scope households (cases.py) and write the run file. SAME-FAMILY. The sealed answers are NOT read.

Protocol (law 1's staged route, usecases/pawhp/run.py on branch pawhp-build-1123, generalised):
1. Ground the rules over the household's persons, items, pairs and day-types (rules.py); build the facts (encode.py).
2. Each derived atom is one step, proved (both polarities) from the rules that define it, the facts those rules mention and
   earlier steps. One certificate -> the step holds; two -> inconsistent (recorded, the case is refused); none -> OPEN.
   The charge is one step over the bridged charges of 681C (rules.charge_rules).
3. Refusals: a step proving d3_unresolved or e3_unresolved (a tie the text does not resolve) or an inconsistent step:
   every answer of the case is OPEN (refused).
4. Lean replays every step certificate and admits one documents@1 quantity document per answer (Q3: one per person);
   an answer counts only if Lean admitted all its documents (else OPEN).
5. --mutants: each planted error (rules.MUTANTS) must change an answer of the household named for it.

Usage (repository root): uv run python -B usecases/hicbc/run.py [--cases H001,H002] [--mutants] [--no-lean] [--out FILE]
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
import rules as R  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.units import prove_quantity  # noqa: E402

BRIDGES_SHA256 = "a4fc0dcb42de7790590af0bc38c534d53c2c20be54f6425bde683989cd280ff6"  # bridge/bridges.jsonl as frozen before the headline run


def q(f):
    return {"format": "ve-quantity@1", "formula": f}


class Prover:
    def __init__(self):
        self.envs, self.cache, self.calls, self.searches = {}, {}, 0, 0

    def env(self, raw):
        k = R.key(raw)
        if k not in self.envs:
            self.envs[k] = Environment(raw)
        return self.envs[k]

    def prove(self, raw_env, premises, conclusion):
        self.calls += 1
        k = R.key([raw_env["vocabulary"]["constants"], premises, conclusion])
        if k not in self.cache:
            self.searches += 1
            self.cache[k] = prove_quantity(self.env(raw_env), [q(p) for p in premises], q(conclusion))
        return self.cache[k]


class Staged:
    def __init__(self, prover, raw_env, rules, facts, step_constants):
        self.prover, self.raw_env, self.step_constants = prover, raw_env, step_constants
        self.fact_atoms, self.fact_constants = {}, {}
        for f in facts:
            atoms, constants = set(), set()
            R.atoms_in(f["formula"], atoms, constants)
            for a in atoms:
                self.fact_atoms.setdefault(a, []).append(f)
            for c in constants:
                self.fact_constants.setdefault(c, []).append(f)
        self.defs = {}
        for r in rules:
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
            R.atoms_in(r["formula"], a, c)
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
        for c in sorted(constants):
            if c == target:
                continue
            facts += [f"fact:{f['id']}" for f in self.fact_constants.get(c, [])]
        facts = list(dict.fromkeys(facts))
        return facts + steps + [f"rule:{r['id']}" for r in rules]

    def formula(self, name):
        return self.leaves[name] if name in self.leaves else self.by_name[name]["formula"]

    @property
    def by_name(self):
        return {s["name"]: s for s in self.steps.values()}

    def attempt(self, target, label, candidates, names=None):
        names = self.premises_for(target) if names is None else names
        premises = [self.formula(n) for n in names]
        found = []
        for cand in candidates:
            cert = self.prover.prove(self.raw_env, premises, cand)
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
            a, c = set(), set()
            for r in rs:
                R.atoms_in(r["formula"], a, c)
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

    def known(self, f):
        step = self.steps.get(R.key(f))
        return None if step is None else step["formula"] == f

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
        for k, name in enumerate(leaf_names):
            uid = "u" + str(k)
            units.append({"id": uid, "span": [k, k + 1], "kind": "asserted", "content": q(self.leaves[name])})
            nodes.append({"name": name, "quantity": q(self.leaves[name]), "unit": uid})
        for step in self.steps.values():
            if step["name"] in needed:
                nodes.append({"name": step["name"], "quantity": q(step["formula"]),
                              "premises": step["premises"], "certificate": step["certificate"]})
        return {"units": units, "graph": {"root": root["name"], "nodes": nodes}}


def label(f):
    return f[1] + "." + ".".join(x[1] for x in f[2:])


def run_case(prover, case, br, mutant=None):
    dom, ani_people, facts, consts = E.case_model(case, br)
    raw_env = R.environment(consts)
    subj = E.pc(case["subject"])
    rules = R.rules(dom, ani_people, mutant)
    table = []
    if consts["charge"]:
        table = br["charge_table"]
        rules += R.charge_rules(subj, dom["item"], table)
    st = Staged(prover, raw_env, rules, facts, ["charge_" + subj])
    st.items = dom["item"]
    for t in st.order():
        if t.startswith("charge_"):
            continue
        f = json.loads(t)
        st.attempt(t, label(f), [f, ["not", f]])
    refused = [e["target"] for e in st.log if e.get("inconsistent")]
    for f in st.steps.values():
        if f["formula"][0] == "unary" and f["formula"][1] in ("d3_unresolved", "e3_unresolved"):
            refused.append(label(f["formula"]))
    liable = {p: st.known(R.U("liable", E.pc(p))) for p in case["people"]}
    answers = {"Q1": {True: "YES", False: "NO", None: "OPEN"}[liable[case["subject"]]]}
    if answers["Q1"] == "YES" and table:
        cands = sorted({r["charge"] for r in table}, key=lambda s: float(s))
        # premise selection: the one charge rule whose condition (which amounts are liable_for the subject) matches the
        # established steps, and those steps; no rule matches when a liable_for step is OPEN (then Q2 is OPEN)
        lf = [R.key(R.B("liable_for", subj, i)) for i in st.items]
        names = None
        if all(k in st.steps for k in lf):
            counted = [i for i, k in zip(st.items, lf) if st.known(json.loads(k))]
            for r in st.defs["charge_" + subj]:
                if sorted(r["counted"]) == sorted(counted):
                    names = [st.steps[k]["name"] for k in lf] + [f"rule:{r['id']}"]
        got = st.attempt("charge_" + subj, "charge", [["eq", ["const", "gbp_penny", "charge_" + subj],
                                                       ["decimal", "gbp_penny", v]] for v in cands],
                         names) if names else None
        answers["Q2"] = got[2][2].split(".")[0] if got else "OPEN"
    else:
        answers["Q2"] = "N/A" if answers["Q1"] == "NO" else "OPEN"
    answers["Q3"] = "OPEN" if any(v is None for v in liable.values()) else sorted(p for p, v in liable.items() if v)
    if refused:
        answers = {"Q1": "OPEN", "Q2": "OPEN", "Q3": "OPEN"}
    return answers, st, raw_env, refused


def answer_targets(case, answers):
    out = {}
    if answers["Q1"] in ("YES", "NO"):
        out["Q1"] = [R.key(R.U("liable", E.pc(case["subject"])))]
    if answers.get("Q2") not in (None, "OPEN", "N/A"):
        out["Q2"] = ["charge_" + E.pc(case["subject"])]
    if isinstance(answers.get("Q3"), list):
        out["Q3"] = [R.key(R.U("liable", E.pc(p))) for p in case["people"]]
    return out


def _check(group):
    """Lean replay of one household's cases; a batch the checker fails on is split in halves (its process has a fixed
    4 GiB address-space cap, ve/backends/lean_service.py ADDRESS_SPACE); a single case it still cannot answer is recorded
    as {"status": "checker-unavailable"} (its answer is then OPEN)."""
    from ve.backends.relay import rows
    from ve.errors import CheckerUnavailable
    try:
        got = rows("quantity", group)
        assert [r["id"] for r in got] == [c["id"] for c in group]
        return got
    except CheckerUnavailable as e:
        print(group[0]["id"], f"checker unavailable on {len(group)} cases:", str(e)[-60:], file=sys.stderr)
        if len(group) == 1:
            return [{"id": group[0]["id"], "status": "checker-unavailable"}]
        h = len(group) // 2
        return _check(group[:h]) + _check(group[h:])


def lean(cases, workers=4):
    """One request per household, households in parallel (separate Lean processes)."""
    from concurrent.futures import ProcessPoolExecutor
    groups = {}
    for c in cases:
        groups.setdefault(c["id"].split("/")[0], []).append(c)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        parts = list(pool.map(_check, list(groups.values())))
    return [r for part in parts for r in part]


def _mutant_task(item):
    mutant, cases, bridges, base = item
    prover = Prover()
    changed = []
    for c in cases:
        a = run_case(prover, c, bridges[c["id"]], mutant)[0]
        if a != base[c["id"]]:
            changed.append(c["id"])
    return mutant, changed


MUTANT_TARGETS = {"M1": ["H002"], "M2": ["H008"], "M3": ["H020"], "M4": ["H010"], "M5": ["H016"]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases")
    ap.add_argument("--mutants", action="store_true")
    ap.add_argument("--no-lean", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--lean-workers", type=int, default=4)
    args = ap.parse_args(argv)
    started = time.time()
    bridges = E.load_bridges(BRIDGES_SHA256)
    prover = Prover()
    cases = K.CASES
    if args.cases:
        cases = [c for c in cases if c["id"] in args.cases.split(",")]
    records, lean_cases = [], []
    for case in cases:
        t0 = time.time()
        answers, st, raw_env, refused = run_case(prover, case, bridges[case["id"]])
        rec = {"id": case["id"], "scope": "in", "staged": answers, "refused": refused,
               "rules": len(st.leaves) - sum(1 for k in st.leaves if k.startswith("fact:")),
               "facts": sum(1 for k in st.leaves if k.startswith("fact:")),
               "steps": [{k: v for k, v in e.items() if k != "premises"} | {"premise_count": len(e["premises"])}
                         for e in st.log],
               "encoder_judgement": case.get("judgement", []), "seconds": round(time.time() - t0, 1)}
        records.append(rec)
        for step in st.steps.values():
            lean_cases.append({"id": f"{case['id']}/cert/{step['name']}", "kind": "certificate", "environment": raw_env,
                               "premises": [q(st.formula(n)) for n in step["premises"]],
                               "conclusion": q(step["formula"]), "certificate": step["certificate"]})
        for question, targets in answer_targets(case, answers).items():
            for k, target in enumerate(targets):
                lean_cases.append({"id": f"{case['id']}/doc/{question}/{k}", "kind": "document", "environment": raw_env,
                                   "document": st.document(target)})
        print(case["id"], answers, rec["seconds"], "s", file=sys.stderr)
    lean_results = {} if args.no_lean else {r["id"]: r for r in lean(lean_cases, args.lean_workers)}
    for rec in records:
        hid = rec["id"]
        mine = {k: v for k, v in lean_results.items() if k.startswith(hid + "/")}
        certs = [v for k, v in mine.items() if "/cert/" in k]
        docs = {}
        for k, r in mine.items():
            if "/doc/" in k:
                qq = k.split("/")[2]
                docs.setdefault(qq, []).append(r.get("status") == "ok" and r.get("assurance") == "lean-admitted")
        rec["lean"] = {"certificates": len(certs),
                       "certificates_accepted": sum(r.get("status") == "ok" and r.get("valid") is True for r in certs),
                       "documents": {qq: all(v) for qq, v in sorted(docs.items())}}
        answers = dict(rec["staged"])
        case = next(c for c in cases if c["id"] == hid)
        for qq in answer_targets(case, answers):
            if args.no_lean or not rec["lean"]["documents"].get(qq):
                answers[qq] = "OPEN"
                rec.setdefault("lean_rejected", []).append(qq)
        rec["answers"] = answers
    for pid in K.PROBES:
        if not args.cases or pid in args.cases.split(","):
            records.append({"id": pid, "scope": "out", "answers": {"Q1": "UNSUPPORTED", "Q2": "UNSUPPORTED", "Q3": "UNSUPPORTED"}})
    mutants = {}
    if args.mutants:
        from concurrent.futures import ProcessPoolExecutor
        base = {r["id"]: r["staged"] for r in records if "staged" in r}
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            changed = dict(pool.map(_mutant_task, [(m, cases, bridges, base) for m in R.MUTANTS]))
        for m, (desc, _) in R.MUTANTS.items():
            must = [p for p in MUTANT_TARGETS[m] if p in base]
            mutants[m] = {"description": desc, "must_change": must, "changed": changed[m],
                          "killed": bool(must) and all(p in changed[m] for p in must)}
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "usecases/hicbc"],
                           capture_output=True, text=True).stdout.strip()
    enc = hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest()
    brs = hashlib.sha256((HERE / "bridge" / "bridges.jsonl").read_bytes()).hexdigest()
    out = {"format": "hicbc-run@1", "label": "SAME-FAMILY", "commit": commit, "tree_clean": dirty == "",
           "questions_enc_sha256": enc, "bridges_sha256": brs,
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
            k = v if v in ("YES", "NO", "OPEN", "N/A", "UNSUPPORTED") else "value"
            summary.setdefault(qq, {}).setdefault(k, 0)
            summary[qq][k] += 1
    print(json.dumps({"summary": summary, "seconds": out["seconds"], "commit": commit, "clean": out["tree_clean"],
                      "mutants": {m: v["killed"] for m, v in mutants.items()}}, indent=1))
    return out


if __name__ == "__main__":
    main()
