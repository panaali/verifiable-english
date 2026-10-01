"""Runs VE on every case of the asimov-extended use case and compares with the answer key.

`python usecases/asimov-extended/check.py` writes `results.json` and prints the
comparison with `answer-key.json`. VE's Lean route (`ve_risk_route`) decides
every record; the comparison reads the answer key only after every result is
computed. What runs (PLAN.md sections 7, 8 and 10):

1. The document checks: conflict certificates found by Python's prover and
   replayed by Lean, for base + additions and for the base rules alone, and
   followability with each expected dilemma record as the witness.
2. The 51 records of PLAN.md section 5, each under the base rules (1-13) and
   under base + additions (1-29), and the independent reading of `reading.py`.
3. Five seeded mutants (PLAN.md section 8).
4. 300 sampled records: Lean against the independent reading, and the sampled
   properties Q1-Q3 (PLAN.md section 7; these are not certificates).
"""
from __future__ import annotations

import json
import multiprocessing
import os
import random
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cases  # noqa: E402
import reading  # noqa: E402
from cases import HARMS, REPO  # noqa: E402
from ve.ast import Not, _Decoder  # noqa: E402
from ve.entailment import prove_entailment  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.norms import _bind  # noqa: E402

BINARY = REPO / "lean" / ".lake" / "build" / "bin" / "ve_risk_route"
WORKERS = int(os.environ.get("ASIMOV_EXTENDED_WORKERS", min(12, os.cpu_count() or 1)))
CHUNK = 4
PROVER_STEPS = 20000
SAMPLE, SEED = 300, 2026


def route(batch):
    out = subprocess.run([str(BINARY), "-"], input=json.dumps(batch), text=True, capture_output=True,
                         check=False, timeout=3600)
    if out.returncode != 0 and not out.stdout:
        raise RuntimeError(out.stderr)
    return json.loads(out.stdout)


def run(batch):
    """Every case through the Lean route, in chunks on parallel processes, results in order."""
    chunks = [batch[i:i + CHUNK] for i in range(0, len(batch), CHUNK)]
    with ThreadPoolExecutor(WORKERS) as pool:
        return [result for chunk in pool.map(route, chunks) for result in chunk]


def one(case):
    return route([case])[0]


def elaborate(env, rules):
    res = one({"id": "p", "kind": "risk-elaborate", "environment": env, "document": {"norms": rules}})
    if res.get("status") != "ok":
        raise RuntimeError(res)
    return res


def policy(env, rules):
    res = elaborate(env, rules)
    return res["environment_id"], res["document_hash"]


# ---------------------------------------------------------------------------- document checks

def _base_environment(env, elaborated):
    from tests.test_risk_fixtures import risk_base_environment
    return risk_base_environment(env, elaborated)


def conflict(env, rules, witness=None):
    """Prove each conflict target in Python and replay the certificates in Lean (or replay a witness)."""
    start = time.time()
    elaborated = elaborate(env, rules)
    base = Environment(_base_environment(env, elaborated))
    packages, unproved = {}, []
    for target in elaborated["conflict_targets"]:
        conclusion = _bind(Not(_Decoder().decode(target["ast"])), target["sorts"])
        proof = prove_entailment(base, (), conclusion, max_steps=PROVER_STEPS)
        if proof.status == "Found":
            packages[target["target"]] = {"environment_id": elaborated["environment_id"],
                                          "document_hash": elaborated["document_hash"],
                                          "target": target["target"], "certificate": proof.certificate}
        else:
            unproved.append(target["target"])
    case = {"id": "c", "kind": "risk-conflict", "environment": env, "document": {"norms": rules}}
    res = one(case | ({"witness": witness} if witness else {"packages": packages}))
    result = {"verdict": res.get("verdict"), "targets": [t["target"] for t in elaborated["conflict_targets"]],
              "unproved": unproved, "seconds": round(time.time() - start, 1)}
    return result, packages


def followable(env, rules, packages, record_id):
    model = cases.witness_model(env, cases.all_records()[record_id])
    res = one({"id": "f", "kind": "risk-followable", "environment": env, "document": {"norms": rules},
               "packages": packages, "witness": {"model": model, "chooser": "r"}})
    return {"witness": record_id, "verdict": res.get("verdict"), "diagnosis": res.get("diagnosis")}


# ---------------------------------------------------------------------------- decisions

def summary(report):
    if report.get("status") != "ok":
        return {"error": report.get("text") or report.get("diagnostic") or json.dumps(report)[:300]}
    dilemmas = report["lines"]["dilemmas"]
    return {"clear": report["clear"],
            "permitted": [s["alternative"] for s in report["statuses"] if s["permitted"]],
            "required": [s["alternative"] for s in report["statuses"] if s["required"]],
            "dilemma": dilemmas[0].split(":")[0].split("(")[0] if dilemmas else None}


def decide(env, rules, specs):
    """`risk-decision` on every record spec, bound to the policy of `rules`."""
    bound = policy(env, rules)
    batch = [cases.decision_case(name, env, rules, spec, bound) for name, spec in specs.items()]
    return {name: summary(report) for name, report in zip(specs, run(batch))}


def category(base, ext):
    if not ext:
        return "DILEMMA"
    if base == ext:
        return "UNCHANGED"
    if not base:
        return "RESOLVED" if len(ext) == 1 else "TIE"
    return "SHARPENED" if set(ext) < set(base) else "CHANGED"


def read_all(specs, rank=None):
    return {name: {"base": reading.read(spec, False, rank), "ext": reading.read(spec, True, rank)}
            for name, spec in specs.items()}


def agrees(lean, independent):
    return all(lean[key] == independent[key] for key in ("clear", "permitted", "required"))


# ---------------------------------------------------------------------------- mutants

def mutant(name, env, ext_rules):
    """One seeded mutant (PLAN.md 8): its conflict verdict and the clear set of the record it is about."""
    by_name = {r["norm"]["name"]: r for r in ext_rules}
    rules, raw = deepcopy(ext_rules), deepcopy(env)
    edit = {
        "M1": ("tie-precaution", {"over": []}),
        "M2": ("tie-order-earlier", {"unless": []}),
        "M4": ("tie-possibly-harmful-human",
               {"guard": ["exists", "harm", ["binary", "risk__might_lead_to", ["var", 1], ["var", 0]]]}),
        "M5": ("tie-possibly-harmful-robot", {"unless": []}),
    }.get(name)
    if edit:
        assert edit[0] in by_name
        next(r for r in rules if r["norm"]["name"] == edit[0])["norm"].update(edit[1])
    if name == "M3":
        raw["risk"]["severity"]["more_severe"] = [["catastrophic", "fatal"], ["fatal", "damaging"],
                                                  ["damaging", "injuring"]]
    focus = {"M1": ["P:P3 ordered-possible-injury"], "M2": ["O:O2 j-later-more-authority"],
             "M3": ["P:P7 injury-vs-property", "S:b-A0 FI"], "M4": ["P:P4 ordered-possible-robot-loss"],
             "M5": ["P:P4 ordered-possible-robot-loss"]}[name]
    records = cases.all_records()
    witness = None
    if name == "M1":
        model = cases.witness_model(raw, records[focus[0]])
        witness = {"model": model, "target": "permitted", "tuple": ["obey"]}
    result, _ = conflict(raw, rules)
    if witness:
        result["witness"] = {"record": focus[0], "verdict": conflict(raw, rules, witness)[0]["verdict"]}
    if name != "M1":
        result["clear"] = {k: v["clear"] for k, v in decide(raw, rules, {k: records[k] for k in focus}).items()}
    return result


# ---------------------------------------------------------------------------- sampled records

def sampled(count=SAMPLE, seed=SEED):
    """Records with up to 4 actions: random certain and possible cells, orders, marks and order relations."""
    rng = random.Random(seed)
    out = {}
    for index in range(count):
        actions = ["nothing"] + [f"a{i}" for i in range(1, rng.randint(1, 3) + 1)]
        leads, might = [], []
        for a in actions:
            for h in HARMS:
                x = rng.random()
                (leads if x < 0.12 else might if x < 0.24 else []).append((a, h))
        choose = lambda p: [a for a in actions[1:] if rng.random() < p]  # noqa: E731
        ordered = choose(0.45)
        sequence = rng.sample(ordered, len(ordered))
        before = [(x, y) for i, x in enumerate(sequence) for y in sequence[i + 1:] if rng.random() < 0.7]
        rank = {a: rng.randint(0, 2) for a in ordered}
        outranks = [(x, y) for x in ordered for y in ordered if rank[x] > rank[y]]
        out[f"Q{index:03d}"] = cases.scenario(actions, leads=leads, might=might, ordered=ordered,
                                              injures_human=choose(0.15), injures_humanity=choose(0.06),
                                              protects_robot=choose(0.2), ordered_before=before,
                                              outranks=outranks)
    return out


def properties(specs, lean):
    """Q1-Q3 of PLAN.md section 7 on Lean's results, with the counts behind each."""
    q1 = [k for k in specs if lean["base"][k]["clear"] and not lean["ext"][k]["clear"]]
    none_permitted = [k for k in specs if lean["ext"][k]["dilemma"] == "NONE-PERMITTED"]
    every_breaks_zeroth = [k for k in specs if all(a in reading_zeroth(specs[k]) for a in specs[k]["actions"])]
    over = [k for k in specs if lean["ext"][k]["dilemma"] == "OVER-REQUIRED"]
    q3 = [k for k in over if len(lean["ext"][k]["required"]) < 2 or not no_prevailing(specs[k], lean["ext"][k])]
    return {"Q1_lost_clear": q1, "none_permitted": len(none_permitted),
            "Q2_failures": sorted(set(none_permitted) ^ set(every_breaks_zeroth)),
            "over_required": len(over), "Q3_failures": q3,
            "ext_dilemmas": dict(Counter(lean["ext"][k]["dilemma"] for k in specs if lean["ext"][k]["dilemma"]))}


def reading_zeroth(spec):
    cell, actions = spec["cells"], spec["actions"]
    marked = {row[0] for row in spec["facts"]["injures_humanity"]}
    return {a for a in actions if a in marked or any(
        cell[(a, h)] == "leads" and any(cell[(b, h)] != "leads" for b in actions if b != a)
        for h in cases.HUMANITY)}


def no_prevailing(spec, ext):
    """Q3: no required order prevails over another required order (rules 21-22, read on the record)."""
    outranks = {tuple(r) for r in spec["facts"]["outranks"]}
    before = {tuple(r) for r in spec["facts"]["ordered_before"]}
    required = ext["required"]
    return not any((b, a) in outranks or ((b, a) in before and (a, b) not in outranks)
                   for a in required for b in required if a != b)


# ---------------------------------------------------------------------------- the whole run

def _conflict_job(job):
    name, env, rules = job
    result, packages = conflict(env, rules)
    return name, result, packages


def compute(sample=SAMPLE):
    env = cases.environment()
    ext_rules, base_rules = cases.norms(True), cases.norms(False)
    records = cases.all_records()
    timing = {}

    start = time.time()
    jobs = [("ext", env, ext_rules), ("base", env, base_rules)]
    with multiprocessing.get_context("fork").Pool(min(len(jobs), WORKERS)) as pool:
        done = {name: (result, packages) for name, result, packages in pool.map(_conflict_job, jobs)}
    ext_conflict, ext_packages = done["ext"]
    timing["conflict_ext_seconds"] = ext_conflict.pop("seconds")
    timing["conflict_base_seconds"] = done["base"][0].pop("seconds")
    start = time.time()
    follow = [followable(env, ext_rules, ext_packages, k) for k in ("S:j", "P:P8 all-break-zeroth")]
    timing["followability_seconds"] = round(time.time() - start, 1)
    document = {"ext_conflict": ext_conflict, "base_conflict": done["base"][0], "ext_followable": follow}

    start = time.time()
    lean = {"base": decide(env, base_rules, records), "ext": decide(env, ext_rules, records)}
    timing["decisions_seconds"] = round(time.time() - start, 1)
    timing["decisions"] = 2 * len(records)
    independent = read_all(records)
    per_record = {}
    for name in records:
        base, ext = lean["base"][name], lean["ext"][name]
        per_record[name] = {"base": base, "ext": ext, "category": category(base.get("clear"), ext.get("clear")),
                            "independent_agrees": {side: agrees(lean[side][name], independent[name][side])
                                                   for side in ("base", "ext")}}

    start = time.time()
    with multiprocessing.get_context("fork").Pool(5) as pool:
        mutants = dict(zip(("M1", "M2", "M3", "M4", "M5"),
                           pool.starmap(mutant, [(m, env, ext_rules) for m in ("M1", "M2", "M3", "M4", "M5")])))
    for result in mutants.values():
        result.pop("seconds")
    timing["mutants_seconds"] = round(time.time() - start, 1)

    start = time.time()
    specs = sampled(sample)
    sample_lean = {"base": decide(env, base_rules, specs), "ext": decide(env, ext_rules, specs)}
    sample_reading = read_all(specs)
    disagreements = [k for k in specs for side in ("base", "ext")
                     if not agrees(sample_lean[side][k], sample_reading[k][side])]
    timing["sampled_seconds"] = round(time.time() - start, 1)
    sampled_result = {"records": len(specs), "seed": SEED, "lean_vs_reading_disagreements": sorted(set(disagreements)),
                      "base_clear": sum(bool(sample_lean["base"][k]["clear"]) for k in specs),
                      "ext_clear": sum(bool(sample_lean["ext"][k]["clear"]) for k in specs),
                      **properties(specs, sample_lean)}
    return {"document": document, "records": per_record, "mutants": mutants, "sampled": sampled_result,
            "timing": timing}


def compare(results, key):
    """Agreement with the answer key; every disagreement with what VE gave."""
    rows, disagreements = key["records"], []
    for name, expected in rows.items():
        got = results["records"][name]
        for side in ("base", "ext"):
            if sorted(got[side]["clear"]) != sorted(expected[side]):
                disagreements.append({"record": name, "side": side, "key": expected[side], "ve": got[side]["clear"]})
            elif not expected[side] and got[side]["dilemma"] != expected[f"{side}_dilemma"]:
                disagreements.append({"record": name, "side": side, "key": expected[f"{side}_dilemma"],
                                      "ve": got[side]["dilemma"]})
        if got["category"] != expected["category"]:
            disagreements.append({"record": name, "side": "category", "key": expected["category"],
                                  "ve": got["category"]})
    agree = lambda side: sum(sorted(results["records"][n][side]["clear"]) == sorted(rows[n][side])  # noqa: E731
                             for n in rows)
    doc, dkey = results["document"], key["document"]
    document = {
        "ext_conflict": doc["ext_conflict"]["verdict"] == dkey["ext_conflict"],
        "ext_conflict_targets": [len(doc["ext_conflict"]["targets"]), dkey["ext_conflict_targets"]],
        "base_conflict": doc["base_conflict"]["verdict"] == dkey["base_conflict"],
        "base_conflict_targets": [len(doc["base_conflict"]["targets"]), dkey["base_conflict_targets"]],
        "ext_followable": all(f["verdict"] == dkey["ext_followable"]
                              and f["diagnosis"].startswith(tuple(dkey["ext_witness_kinds"]))
                              for f in doc["ext_followable"]),
    }
    mutants = {}
    for name, expected in key["mutants"].items():
        got = results["mutants"][name]
        ok = got["verdict"] == expected["conflict"] or (got.get("witness") or {}).get("verdict") == expected["conflict"]
        if "record" in expected:
            ok = ok and sorted(got["clear"][expected["record"]]) == sorted(expected["ext"])
            for record, clear in expected.get("unchanged", {}).items():
                ok = ok and sorted(got["clear"][record]) == sorted(clear)
        mutants[name] = ok
    sample, skey = results["sampled"], key["sampled"]
    sampled = {"Q1": len(sample["Q1_lost_clear"]) == skey["Q1_lost_clear"], "Q2": not sample["Q2_failures"],
               "Q3": not sample["Q3_failures"], "lean_vs_reading": not sample["lean_vs_reading_disagreements"]}
    categories = Counter(results["records"][n]["category"] for n in rows)
    return {"base_agree": agree("base"), "ext_agree": agree("ext"), "records": len(rows),
            "disagreements": disagreements, "categories": dict(categories), "document": document,
            "mutants": mutants, "sampled": sampled}


def main():
    results = compute()
    key = json.loads((HERE / "answer-key.json").read_text())
    results["comparison"] = compare(results, key)
    (HERE / "results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps(results["comparison"], indent=1))
    print(json.dumps(results["timing"], indent=1))


if __name__ == "__main__":
    main()
