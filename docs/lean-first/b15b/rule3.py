"""The rule-3 condition of lean-first batch 15b (docs/LEAN-FIRST-PLAN.md, section 5.2 row 15b; DRI answer 2/10).

Batch 15b deletes the two generator-internal duplicates of rule 3 (Rust's candidate evaluator `eval.rs` with the
order evaluator in `order.rs`, and the provers' internal Python replay) only if the implementation batch 2
measured preserves candidate order, first witness, charging, counts and exhaustion on the search fixtures and
the certificate cohorts, and meets each operation's deadline. Batch 2 could not check charging, because Lean's
evaluator had no budget; batch 15a added it (`ve_metered`, `VE.Route.Metered`, `VE.Route.NonVacuity`). This
script measures every row again with that evaluator, one record per query, base and head side by side:

* **Search** (base: Rust's search, `eval.rs` or the order evaluator, as `ve jsonl` answers it today; head: the same
  Rust candidate stream, `rust/ve/examples/rule3_enumerate.rs` or, for order@0,
  `rust/ve-core/examples/rule3_order_enumerate.rs`, evaluated by Lean's metered evaluator). The head charges
  exactly as Rust's loop does: one shared budget, the model and budget checks before each candidate, the
  non-vacuity guard first, then the premises as one document (they share the counter and stop at the first false
  one) and the conclusion, or the two formulas of a distinguishing query. Candidates go to `ve_metered` in
  batches, each case with the budget left at the start of its batch; a case whose answer depends on the smaller
  budget actually left at its turn (it ran out, or used more than was left) is asked again with that budget, so
  every count is Lean's own answer to the exact request.
* **Certificates** (base: the prover's self-replay in Python, `check_entailment_certificate(_background=False)`;
  head: the same certificate replayed by Lean's certificate route, `_check_certificate_lean`). The search is the
  same, so the prover's status and certificate are preserved exactly when the replay's validity is; charging is
  the replay's step count, and exhaustion is the replay at one step below that count.

Deadlines: a search is held to Rust search's deadline (`rust_jsonl.DEFAULT_TIMEOUT`, wall), a replay to the
certificate route's (`lean_service.DEADLINES["route"]`, CPU per case and per MiB; its wall is an upper bound).

Usage (from the repository root, after `python3 tools/rust_build.py build --release --locked --manifest-path
rust/Cargo.toml -p ve --example rule3_enumerate` and the same with `-p ve-core --features bench-internals
--example rule3_order_enumerate`)::

    uv run --frozen python docs/lean-first/b2/rule3.py capture-bluedot --out /tmp/bluedot-search.jsonl
    uv run --frozen python docs/lean-first/b15b/rule3.py --bluedot /tmp/bluedot-search.jsonl --out rule3.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
METERED = ROOT / "lean/.lake/build/bin/ve_metered"
ENUMERATE = ROOT / "rust/target/release/examples/rule3_enumerate"
ORDER_ENUMERATE = ROOT / "rust/target/release/examples/rule3_order_enumerate"
OPERATIONS = ("countermodel search", "guarded countermodel search", "distinguishing-model search",
              "bluedot countermodel search", "order countermodel search", "tableau prover replay",
              "closure prover replay", "order prover replay")
PROPERTIES = ("order", "first_witness", "charging", "counts", "exhaustion", "deadline")


def _dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _children_cpu() -> float:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


class Metered:
    """`ve_metered` over batches of cases, with its processes, bytes, CPU and wall."""

    def __init__(self):
        self.cost = {"processes": 0, "bytes": 0, "cpu": 0.0, "wall": 0.0}

    def run(self, cases: list[dict]) -> list[dict]:
        if not cases:
            return []
        text = _dumps(cases)
        cpu, started = _children_cpu(), time.perf_counter()
        answer = subprocess.run([str(METERED)], input=text, capture_output=True, text=True, check=True)
        self.cost["wall"] += time.perf_counter() - started
        self.cost["cpu"] += _children_cpu() - cpu
        self.cost["processes"] += 1
        self.cost["bytes"] += len(text.encode())
        rows = json.loads(answer.stdout)
        for case, row in zip(cases, rows, strict=True):
            if row.get("status") != "ok":
                raise SystemExit(f"ve_metered refused {case['id']}: {row}")
        return rows


class Exact:
    """One case of a batch: Lean's answer at the batch's budget, asked again at the exact budget when needed."""

    def __init__(self, metered: Metered, case: dict, row: dict, nonvacuity: bool):
        self.metered, self.case, self.row, self.nonvacuity = metered, case, row, nonvacuity

    def at(self, left: int) -> dict:
        row = self.row
        exhausted = row["exhausted"] if self.nonvacuity else row["evaluation"]["status"] == "ResourceLimit"
        work = row["evaluations"] if self.nonvacuity else row["evaluation"]["evaluations"]
        if (exhausted or work > left) and self.case["max_evaluations"] != left:
            row = self.metered.run([{**self.case, "max_evaluations": left}])[0]
        if self.nonvacuity:
            return {"suitable": row["suitable"], "work": row["evaluations"], "exhausted": row["exhausted"]}
        evaluation = row["evaluation"]
        return {"value": evaluation["value"], "work": evaluation["evaluations"],
                "exhausted": evaluation["status"] == "ResourceLimit"}


def lean_search(metered: Metered, query: dict, *, batch: int, order: bool) -> dict:
    """Rust enumerates, Lean's metered evaluator decides and charges every candidate."""
    environment, guard = query["environment"], query.get("nonvacuous_for")
    pair = (query["a"], query["b"]) if query.get("kind") == "distinguishing-model" else None
    stream = ({**query, "premises": [query["a"]], "conclusion": query["b"]} if pair else query)
    max_models, budget = query.get("max_models", 10_000), query.get("max_evaluations", 1_000_000)
    checked = used = 0
    status, witness, detail = None, None, ""
    enumerator = ORDER_ENUMERATE if order else ENUMERATE

    def bound(models: bool) -> str:
        # The search driver's own texts (`search.rs`, `order.rs` `order_search`), which stay Rust's.
        if not order:
            return "model-attempt or evaluation budget exhausted"
        return "model-attempt budget exhausted" if models else "evaluation budget exhausted"
    started = time.perf_counter()
    enumeration = 0.0
    process = subprocess.Popen([str(enumerator), str(batch)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
    try:
        process.stdin.write(_dumps(stream) + "\n")
        process.stdin.close()
        while status is None:
            ticked = time.perf_counter()
            line = process.stdout.readline()
            enumeration += time.perf_counter() - ticked
            if not line:
                error = process.stderr.read()
                if "ResourceLimit" not in error:
                    raise SystemExit(f"{query['id']}: enumerator stopped: {error}")
                status, detail = "ResourceLimit", "search relation atom space exceeds runtime limit"
                break
            packet = json.loads(line)
            models, exhausted = packet["models"], packet["exhausted"]
            left = budget - used
            cases, plan = [], []
            for index, model in enumerate(models):
                base = {"environment": environment, "model": model, "max_evaluations": left}
                steps = []
                if guard is not None:
                    steps.append(("guard", {**base, "id": f"g{index}", "kind": "non-vacuity", "formula": guard,
                                            "semantic_nonvacuity": query.get("semantic_nonvacuity", False)}))
                parts = ([("a", [pair[0]]), ("b", [pair[1]])] if pair else
                         ([("premises", query["premises"])] if query["premises"] else [])
                         + [("conclusion", [query["conclusion"]])])
                for name, ast in parts:
                    steps.append((name, {**base, "id": f"{name}{index}", "kind": "evaluate-budgeted", "ast": ast}))
                cases += [case for _, case in steps]
                plan.append(steps)
            rows = iter(metered.run(cases))
            answers = [[(name, Exact(metered, case, next(rows), name == "guard")) for name, case in steps]
                       for steps in plan]
            for model, steps in zip(models, answers, strict=True):
                if checked >= max_models or used >= budget:
                    status, detail = "ResourceLimit", bound(checked >= max_models)
                    break
                values, suitable = {}, True
                for name, exact in steps:
                    answer = exact.at(budget - used)
                    used += answer["work"]
                    if answer["exhausted"]:
                        status, detail = "ResourceLimit", "evaluation budget exhausted"
                        break
                    if name == "guard":
                        suitable = answer["suitable"]
                        if not suitable:
                            break
                        continue
                    values[name] = answer["value"]
                    if name == "premises" and answer["value"] is False:
                        break
                checked += 1
                if status is not None or not suitable:
                    if status is not None:
                        break
                    continue
                found = (values["a"] != values["b"]) if pair else (
                    values.get("premises", True) is True and values.get("conclusion") is False)
                if found:
                    status, witness = "Found", model
                    break
            else:
                if exhausted:
                    status = "NotFound"
                elif checked >= max_models:
                    # The stream stops at the model bound; Rust refuses the next model it would examine.
                    status, detail = "ResourceLimit", bound(True)
    finally:
        if process.poll() is None:
            process.terminate()
        process.wait()
    return {"status": status, "model": witness, "models_checked": checked, "evaluations": used,
            "detail": detail, "wall_s": round(time.perf_counter() - started, 6),
            "enumeration_s": round(enumeration, 6)}


def search_record(metered: Metered, operation: str, query: dict, *, batch: int, order: bool) -> dict:
    from ve.backends.rust_jsonl import DEFAULT_TIMEOUT, run as rust_run
    rust_case = {key: value for key, value in query.items() if key not in ("expected_search", "compare_counts")}
    started = time.perf_counter()
    base = rust_run(rust_case, timeout=3600)
    base_wall = time.perf_counter() - started
    if "models_checked" not in base:
        raise SystemExit(f"{query['id']}: {base}")
    before = dict(metered.cost)
    head = lean_search(metered, query, batch=batch, order=order)
    cost = {key: round(metered.cost[key] - before[key], 6) for key in metered.cost}
    same_model = head["model"] == base.get("model")
    found = base["status"] == "Found"
    passes = {
        # One stream: the order is kept when the first candidate either side stops at is the same one.
        "order": head["models_checked"] == base["models_checked"] and head["status"] == base["status"],
        "first_witness": same_model,
        "charging": head["evaluations"] == base["evaluations"],
        "counts": head["models_checked"] == base["models_checked"],
        "exhaustion": head["status"] == base["status"] and (found or head["detail"] == base["detail"]
                                                            or base["status"] == "NotFound"),
        "deadline": head["wall_s"] <= DEFAULT_TIMEOUT,
    }
    return {"operation": operation, "id": query["id"],
            "base": {"status": base["status"], "models_checked": base["models_checked"],
                     "evaluations": base["evaluations"], "detail": base.get("detail", ""),
                     "wall_s": round(base_wall, 6)},
            "head": {key: head[key] for key in ("status", "models_checked", "evaluations", "detail", "wall_s",
                                                "enumeration_s")} | {"lean": cost},
            "deadline_s": DEFAULT_TIMEOUT, "passes": passes}


def search_queries(bluedot: Path | None) -> list[tuple[str, dict, bool]]:
    from ve.backends.rust_jsonl import rust_environment
    fixtures = [q for q in json.loads((ROOT / "conformance/search.json").read_text()) if "expected_search" in q]
    queries = [("countermodel search", q, False) for q in fixtures]
    for q in fixtures:
        guard = q["premises"][0] if q["premises"] else q["conclusion"]
        for semantic in (False, True):
            queries.append(("guarded countermodel search",
                            {**q, "id": f"{q['id']}_guard{int(semantic)}", "nonvacuous_for": guard,
                             "semantic_nonvacuity": semantic}, False))
        queries.append(("distinguishing-model search",
                        {key: value for key, value in q.items() if key not in ("premises", "conclusion")}
                        | {"id": f"{q['id']}_distinguish", "kind": "distinguishing-model",
                           "a": q["premises"][0] if q["premises"] else ["top"], "b": q["conclusion"]}, False))
    if bluedot is not None:
        queries += [("bluedot countermodel search", {**json.loads(line), "id": f"bluedot-{n}"}, False)
                    for n, line in enumerate(bluedot.read_text().splitlines())]
    sys.path.insert(0, str(ROOT / "conformance"))
    import random
    import order as order_corpus
    from ve.ast import formula_to_data
    rng = random.Random(order_corpus.SEED)
    for index in range(40):
        env = order_corpus.environment(index % 7)
        premises, goal = order_corpus.gen_random(rng)
        queries.append(("order countermodel search", {
            "id": f"order_random_{index:03d}", "environment": rust_environment(env),
            "premises": [formula_to_data(env, f) for f in premises], "conclusion": formula_to_data(env, goal),
            "max_domain_size": 1, "min_domain_size": 0, "nonempty_domains": False, "max_models": 3000,
            "max_evaluations": 1_000_000}, True))
    return queries


def certificate_queries(per_cohort: int) -> list[tuple[str, str, object, list, object, int]]:
    import random
    sys.path.insert(0, str(ROOT / "conformance"))
    import certificates as cohorts
    import closure_certificates
    import order as order_corpus
    rng = random.Random(cohorts.SEED)
    fol = []
    for i in range(320):
        fol.append(("broadconstructive", i, cohorts.constructive(rng, i)))
    for i in range(320):
        fol.append(("constructive", i, cohorts.constructive(rng, i, simple=True)))
    for i in range(160):
        constants = bool(i % 2)
        env = cohorts.environment(constants, i + 320)
        ps = [cohorts.formula(rng, 3, constants=constants) for _ in range(rng.randrange(3))]
        fol.append(("unconditioned", i, (env, ps, cohorts.formula(rng, 3, constants=constants))))
    queries = [("tableau prover replay", f"{name}_{index:03d}", *query, 3000)
               for wanted in ("broadconstructive", "constructive", "unconditioned")
               for name, index, query in [q for q in fol if q[0] == wanted][:per_cohort]]
    env, reviewer = closure_certificates.reviewer_queries()
    queries += [("closure prover replay", f"closure_{name}", env, ps, goal, 400)
                for name, (ps, goal) in reviewer.items()]
    rng = random.Random(order_corpus.SEED)
    index = 0
    for name, (generate, _) in order_corpus.GENERATORS.items():
        for i in range(per_cohort // 4):
            env = order_corpus.environment(index % 7)
            index += 1
            premises, goal = generate(rng)
            queries.append(("order prover replay", f"order_{name}_{i:03d}", env, premises, goal, 4000))
    return queries


def certificate_record(operation: str, name: str, env, premises, conclusion, max_steps: int) -> dict | None:
    from ve.backends.dispatch import pinned
    from ve.backends.lean_service import DEADLINES
    from ve.entailment import _check_certificate_lean, _check_certificate_python, prove_entailment
    with pinned("python"):
        result = prove_entailment(env, premises, conclusion, max_steps=max_steps)
    if result.certificate is None:
        return {"operation": operation, "id": name, "certificate": False, "prover_status": result.status}
    budget = max(max_steps, 10_000) if getattr(env, "order", False) else max_steps
    args = (env, premises, conclusion, result.certificate)
    started = time.perf_counter()
    base = _check_certificate_python(*args, max_steps=budget, _background=False)
    base_wall = time.perf_counter() - started
    started = time.perf_counter()
    head = _check_certificate_lean(*args, budget)
    head_wall = time.perf_counter() - started
    below_base = _check_certificate_python(*args, max_steps=max(base.steps - 1, 0), _background=False)
    below_head = _check_certificate_lean(*args, max(base.steps - 1, 0))
    size = len(_dumps(result.certificate).encode()) / (1 << 20)
    per_case, per_mib = DEADLINES["route"]
    deadline = per_case + per_mib * size
    return {"operation": operation, "id": name, "certificate": True, "prover_status": result.status,
            "prover_steps": result.steps,
            "base": {"valid": base.valid, "status": base.status, "steps": base.steps,
                     "below": below_base.status, "wall_s": round(base_wall, 6)},
            "head": {"valid": head.valid, "status": head.status, "steps": head.steps,
                     "below": below_head.status, "wall_s": round(head_wall, 6)},
            "deadline_s": round(deadline, 6),
            "passes": {"order": True, "first_witness": head.valid == base.valid,
                       "charging": head.steps == base.steps, "counts": head.status == base.status,
                       "exhaustion": below_head.status == below_base.status,
                       "deadline": head_wall <= deadline}}


def summary(records: list[dict]) -> list[dict]:
    rows = []
    for operation in OPERATIONS:
        mine = [r for r in records if r["operation"] == operation and "passes" in r]
        if not mine:
            continue
        failing = {p: [r["id"] for r in mine if not r["passes"][p]] for p in PROPERTIES}
        row = {"operation": operation, "queries": len(mine),
               "failing": {p: ids for p, ids in failing.items() if ids},
               "passes": not any(failing.values())}
        if "base" in mine[0] and "evaluations" in mine[0]["base"]:
            row["base"] = {"wall_s": round(sum(r["base"]["wall_s"] for r in mine), 3),
                           "max_wall_s": max(r["base"]["wall_s"] for r in mine),
                           "evaluations": sum(r["base"]["evaluations"] for r in mine),
                           "models_checked": sum(r["base"]["models_checked"] for r in mine)}
            row["head"] = {"wall_s": round(sum(r["head"]["wall_s"] for r in mine), 3),
                           "max_wall_s": max(r["head"]["wall_s"] for r in mine),
                           "evaluations": sum(r["head"]["evaluations"] for r in mine),
                           "models_checked": sum(r["head"]["models_checked"] for r in mine),
                           "lean_cpu_s": round(sum(r["head"]["lean"]["cpu"] for r in mine), 3),
                           "lean_processes": sum(r["head"]["lean"]["processes"] for r in mine),
                           "bytes": sum(r["head"]["lean"]["bytes"] for r in mine)}
        else:
            row["base"] = {"wall_s": round(sum(r["base"]["wall_s"] for r in mine), 3),
                           "max_wall_s": max(r["base"]["wall_s"] for r in mine),
                           "steps": sum(r["base"]["steps"] for r in mine)}
            row["head"] = {"wall_s": round(sum(r["head"]["wall_s"] for r in mine), 3),
                           "max_wall_s": max(r["head"]["wall_s"] for r in mine),
                           "steps": sum(r["head"]["steps"] for r in mine)}
        row["deadline_s"] = min(r["deadline_s"] for r in mine)
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bluedot", type=Path)
    parser.add_argument("--batch", type=int, default=256)
    parser.add_argument("--cohort", type=int, default=40)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    metered = Metered()
    records = [search_record(metered, operation, query, batch=args.batch, order=order)
               for operation, query, order in search_queries(args.bluedot)]
    for operation, name, env, premises, conclusion, max_steps in certificate_queries(args.cohort):
        records.append(certificate_record(operation, name, env, premises, conclusion, max_steps))
    rows = summary(records)
    record = {"load": Path("/proc/loadavg").read_text().split()[0], "batch": args.batch,
              "condition_holds": all(row["passes"] for row in rows), "rows": rows, "records": records}
    Path(args.out).write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps({"condition_holds": record["condition_holds"], "rows": rows}, indent=1))


if __name__ == "__main__":
    main()
