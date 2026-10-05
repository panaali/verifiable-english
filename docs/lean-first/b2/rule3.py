"""The rule-3 measurement of lean-first batch 2 (docs/LEAN-FIRST-PLAN.md, section 5.2 row 2; DRI answer 2/10).

Rule 3 retains two generator-internal duplicates of semantics pending question 10: Rust's candidate
evaluator (`eval.rs`, the order evaluator) and the provers' internal Python replay. Batch 2 measures
the compliant alternative for each, with one record:

* ``search``: Rust enumerates only, and Lean evaluates the candidates. The candidates are enumerated
  in the generator's order (`ve.search._models`, the order `search.rs` follows) and shipped to Lean's
  existing evaluation route (`lean_runner.evaluation_case`) in requests of `--batch` candidates, each
  naming the environment by handle (F2) with F3 batching. Per query: work units (candidates
  evaluated), requests, bytes sent, Lean CPU per candidate, and the split into transport and client
  (wall minus Lean CPU), decoding (the same requests evaluating `top` only) and semantic work (the
  rest), against Rust's own search of the same query (models checked, evaluations, first witness,
  wall) and the operation's F4 deadline. The preservation obligations of batch 15b are checked where
  Lean can check them: candidate order and first witness (the first candidate Lean values as a
  witness is Rust's witness), counts (models checked) and exhaustion. Charging (Rust's evaluation
  count, `ResourceLimit` at a budget) has no Lean counterpart before 15a and is reported as such;
  so is non-vacuity.
* ``certificates``: the provers replay through Lean's certificate route per prover step. On the
  certificate cohorts (`conformance/certificates.py`, sampled), per query: prover steps (trace
  nodes), the Python prover's own time (search and self-replay) and its replay alone, Lean's replay
  of the whole certificate (CPU, wall, bytes, by handle), and the per-request floor (the same
  environment, a trivial request). A per-step design is then, from these measured parts, either
  incremental (one request per step at the floor, every node replayed once: steps x floor + replay)
  or stateless (each step's request replays its prefix: about steps x (floor + replay / 2)); neither
  exists, so both are estimates from measured components.

Usage (from the repository root; a base checkout is measured with its own `--root`)::

    uv run --frozen python docs/lean-first/b2/rule3.py capture-bluedot --out /tmp/bluedot-search.jsonl
    uv run --frozen python docs/lean-first/b2/rule3.py measure [--bluedot FILE] [--cohort N] --out rule3.json

`capture-bluedot` records the search cases `ve document check` of the bluedot document sends to Rust
(`usecases/bluedot-grant/document.ve.md`, under `VE_AUTHORITY=lean`).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def _cpu(pid: int) -> float:
    return int(Path(f"/proc/{pid}/schedstat").read_text().split()[0]) / 1e9


def _dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def capture_bluedot(out: Path) -> None:
    os.environ["VE_AUTHORITY"] = "lean"
    from ve.backends import rust_jsonl
    from ve.document import check_document
    captured = []
    original = rust_jsonl.run

    def run(case, **options):
        if "premises" in case and "model" not in case and case.get("kind") is None:
            captured.append(case)
        return original(case, **options)
    rust_jsonl.run = run
    started = time.perf_counter()
    check_document(str(ROOT / "usecases/bluedot-grant/document.ve.md"))
    print(f"bluedot document check {time.perf_counter() - started:.1f} s, {len(captured)} search cases")
    out.write_text("".join(_dumps(case) + "\n" for case in captured))


class Meter:
    """One Lean service with handles, and its CPU, requests and bytes."""

    def __init__(self):
        from ve.backends.lean_service import LeanService
        self.service = LeanService(timeout=3600)
        self.service.start()
        self.bytes = 0
        write = self.service._write_all

        def counted(data, deadline):
            self.bytes += len(data)
            return write(data, deadline)
        self.service._write_all = counted

    def run(self, mode: str, cases: list) -> tuple[list, dict]:
        before = (_cpu(self.service.pid), self.bytes, self.service.stats["requests"], time.perf_counter())
        rows = self.service.run(mode, cases)
        after = (_cpu(self.service.pid), self.bytes, self.service.stats["requests"], time.perf_counter())
        return rows, {"lean_cpu": after[0] - before[0], "bytes": after[1] - before[1],
                      "requests": after[2] - before[2], "wall": after[3] - before[3]}

    def close(self):
        self.service.close()


def _add(total: dict, part: dict) -> None:
    for key, value in part.items():
        total[key] = total.get(key, 0) + value


def search_query(meter: Meter, query: dict, batch: int) -> dict:
    from ve.ast import document_from_data, formula_to_data
    from ve.backends import rust_jsonl
    from ve.backends.lean_runner import evaluation_case
    from ve.environment import Environment
    from ve.model import FiniteModel
    from ve.search import _models, _used_predicates, _validate_options
    env = Environment(query["environment"])
    formulas = document_from_data(env, [*query["premises"], query["conclusion"]]).formulas
    premises, conclusion = formulas[:-1], formulas[-1]
    nonvacuous = (None if query.get("nonvacuous_for") is None
                  else document_from_data(env, [query["nonvacuous_for"]]).formulas[0])
    max_models = query.get("max_models", 10_000)
    max_domain = query.get("max_domain_size", 2)
    minimum = _validate_options(query.get("min_domain_size", 0), max_domain, max_models,
                                query.get("max_evaluations", 1_000_000), query.get("nonempty_domains", False),
                                None, False)
    rust_case = {"id": "countermodel-search", **{k: v for k, v in query.items()
                                                 if k not in ("id", "expected_search", "compare_counts")}}
    rust_case["environment"] = rust_jsonl.rust_environment(env)
    started = time.perf_counter()
    rust = rust_jsonl.run(rust_case, timeout=3600)
    if "models_checked" not in rust:
        raise SystemExit(f"{query['id']}: {rust}")
    rust_wall = time.perf_counter() - started
    rust_model = (FiniteModel.from_dict(env, rust["model"]).to_dict() if rust.get("model") else None)

    ast = [formula_to_data(env, f) for f in formulas]
    used = _used_predicates(*premises, conclusion, nonvacuous)
    enumerate_seconds = 0.0
    totals: dict = {}
    decoding: dict = {}
    checked, witness, witness_model, exhausted = 0, None, None, False
    iterator = _models(env, minimum, max_domain, used, (*premises, conclusion, nonvacuous), _defer_model_id=True)
    while witness is None and checked < max_models:
        started = time.perf_counter()
        candidates = []
        for model in iterator:
            candidates.append(model)
            if len(candidates) >= min(batch, max_models - checked):
                break
        enumerate_seconds += time.perf_counter() - started
        if not candidates:
            exhausted = True
            break
        cases, tops = [], []
        for index, model in enumerate(candidates):
            mode, case = evaluation_case(env, f"c{checked + index}", ast, model.to_dict())
            cases.append(case)
            tops.append({**case, "ast": [["top"]]})
        rows, cost = meter.run(mode, cases)
        _add(totals, cost)
        _, cost = meter.run(mode, tops)
        _add(decoding, cost)
        for index, row in enumerate(rows):
            if row.get("status") != "ok":
                raise SystemExit(f"{query['id']}: Lean refused candidate {checked + index}: {row}")
            values = row["values"]
            if all(values[:-1]) and values[-1] is False:
                witness, witness_model = checked + index, candidates[index].to_dict()
                break
        checked += len(candidates) if witness is None else witness + 1 - checked
    if witness is None and not exhausted and checked >= max_models:
        # The search's exhaustion probe: is there one more candidate?
        exhausted = next(iterator, None) is None
    lean_status = "Found" if witness is not None else "NotFound" if exhausted else "ResourceLimit"
    agree = {
        "status": lean_status == rust["status"] or (rust["status"] == "ResourceLimit" and lean_status != "Found"),
        "models_checked": checked == rust["models_checked"],
        "first_witness": witness_model == rust_model,
    }
    cpu = totals.get("lean_cpu", 0.0)
    return {
        "id": query["id"], "candidates": checked, "requests": totals.get("requests", 0),
        "bytes": totals.get("bytes", 0), "lean_cpu_s": round(cpu, 6),
        "lean_cpu_per_candidate_ms": round(cpu / checked * 1000, 4) if checked else None,
        "decoding_cpu_s": round(decoding.get("lean_cpu", 0.0), 6),
        "semantic_cpu_s": round(cpu - decoding.get("lean_cpu", 0.0), 6),
        "transport_and_client_s": round(totals.get("wall", 0.0) - cpu, 6),
        "enumeration_s": round(enumerate_seconds, 6),
        "lean_wall_s": round(totals.get("wall", 0.0) + enumerate_seconds, 6),
        "rust": {"status": rust["status"], "models_checked": rust["models_checked"],
                 "evaluations": rust["evaluations"], "wall_s": round(rust_wall, 6)},
        "lean_status": lean_status, "agree": agree,
        "not_checkable_before_15a": ["charging"] + (["non-vacuity"] if nonvacuous is not None else []),
    }


def certificate_cohorts(meter: Meter, per_cohort: int) -> list[dict]:
    sys.path.insert(0, str(ROOT / "conformance"))
    import certificates as cohorts
    from ve.ast import formula_to_data
    from ve.backends.dispatch import pinned
    from ve.entailment import _trace_nodes, check_entailment_certificate, prove_entailment
    rng = random.Random(cohorts.SEED)
    queries = []
    for i in range(320):
        queries.append(("broadconstructive", i, cohorts.constructive(rng, i)))
    for i in range(320):
        queries.append(("constructive", i, cohorts.constructive(rng, i, simple=True)))
    for i in range(160):
        constants = bool(i % 2)
        env = cohorts.environment(constants, i + 320)
        ps = [cohorts.formula(rng, 3, constants=constants) for _ in range(rng.randrange(3))]
        queries.append(("unconditioned", i, (env, ps, cohorts.formula(rng, 3, constants=constants))))
    chosen = [q for name in ("broadconstructive", "constructive", "unconditioned")
              for q in [q for q in queries if q[0] == name][:per_cohort]]
    records = []
    for cohort, index, (env, premises, conclusion) in chosen:
        with pinned("python"):
            started = time.perf_counter()
            result = prove_entailment(env, premises, conclusion, max_steps=3000)
            prover = time.perf_counter() - started
            if result.certificate is None:
                records.append({"cohort": cohort, "index": index, "status": result.status, "steps": result.steps,
                                "prover_s": round(prover, 6)})
                continue
            started = time.perf_counter()
            assert check_entailment_certificate(env, premises, conclusion, result.certificate).valid
            python_replay = time.perf_counter() - started
        nodes = _trace_nodes(result.certificate["trace"])
        case = {"id": "certificate", "environment": env.to_dict(),
                "premises": [formula_to_data(env, p) for p in premises],
                "conclusion": formula_to_data(env, conclusion), "certificate": result.certificate}
        rows, cost = meter.run("check-certificate", [case])
        assert rows[0].get("valid") is True, rows[0]
        _, floor = meter.run("check", [{"id": "floor", "environment": env.to_dict(), "ast": [["top"]]}])
        replay_cpu, floor_cpu = cost["lean_cpu"], floor["lean_cpu"]
        records.append({
            "cohort": cohort, "index": index, "status": result.status, "prover_steps": nodes,
            "prover_s": round(prover, 6), "python_replay_s": round(python_replay, 6),
            "lean_replay_cpu_s": round(replay_cpu, 6), "lean_replay_wall_s": round(cost["wall"], 6),
            "lean_replay_bytes": cost["bytes"], "lean_floor_cpu_s": round(floor_cpu, 6),
            "lean_floor_wall_s": round(floor["wall"], 6),
            "per_step_incremental_estimate_s": round(nodes * floor["wall"] + replay_cpu, 6),
            "per_step_stateless_estimate_s": round(nodes * (floor["wall"] + replay_cpu / 2), 6),
        })
    return records


def measure(args) -> None:
    from ve.backends.lean_service import DEADLINES
    from ve.backends.rust_jsonl import DEFAULT_TIMEOUT, run as rust_run
    meter = Meter()
    try:
        rust_run({"id": "warm", "kind": "check", "environment": {"language": "ve.core@0", "profile": "relational-fol@0",
                  "spec_revision": "ve-v0-draft-2026-09-20", "vocabulary": {"sorts": {}, "predicates": {},
                                                                          "constants": {}}},
                  "ast": [["top"]]}, timeout=3600)
        # The fixtures with a search outcome (the others are countermodel checks of a given model).
        queries = [("search-fixtures", q) for q in json.loads((ROOT / "conformance/search.json").read_text())
                   if "expected_search" in q]
        if args.bluedot:
            queries += [("bluedot", {**json.loads(line), "id": f"bluedot-{n}"})
                        for n, line in enumerate(Path(args.bluedot).read_text().splitlines())]
        search = [{"corpus": corpus, **search_query(meter, query, args.batch)} for corpus, query in queries]
        certificates = certificate_cohorts(meter, args.cohort)
    finally:
        meter.close()
    found = [r for r in certificates if "prover_steps" in r]
    record = {
        "load": Path("/proc/loadavg").read_text().split()[0], "batch": args.batch,
        "deadlines": {"rust_search_wall_s": DEFAULT_TIMEOUT, "lean_route_cpu_s_per_case_and_per_mib": DEADLINES["route"]},
        "search": search,
        "search_totals": {
            "queries": len(search), "candidates": sum(r["candidates"] for r in search),
            "lean_cpu_s": round(sum(r["lean_cpu_s"] for r in search), 3),
            "decoding_cpu_s": round(sum(r["decoding_cpu_s"] for r in search), 3),
            "lean_wall_s": round(sum(r["lean_wall_s"] for r in search), 3),
            "rust_wall_s": round(sum(r["rust"]["wall_s"] for r in search), 3),
            "bytes": sum(r["bytes"] for r in search),
            "disagreements": [r["id"] for r in search if not all(r["agree"].values())],
            "over_rust_deadline": [r["id"] for r in search if r["lean_wall_s"] > DEFAULT_TIMEOUT],
        },
        "certificates": certificates,
        "certificate_totals": {
            "queries": len(certificates), "with_certificate": len(found),
            "prover_steps": sum(r["prover_steps"] for r in found),
            "prover_s": round(sum(r["prover_s"] for r in found), 3),
            "python_replay_s": round(sum(r["python_replay_s"] for r in found), 3),
            "lean_replay_cpu_s": round(sum(r["lean_replay_cpu_s"] for r in found), 3),
            "lean_replay_wall_s": round(sum(r["lean_replay_wall_s"] for r in found), 3),
            "per_step_incremental_estimate_s": round(sum(r["per_step_incremental_estimate_s"] for r in found), 3),
            "per_step_stateless_estimate_s": round(sum(r["per_step_stateless_estimate_s"] for r in found), 3),
        },
    }
    Path(args.out).write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps({"search_totals": record["search_totals"], "certificate_totals": record["certificate_totals"]},
                     indent=1))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    capture = sub.add_parser("capture-bluedot")
    capture.add_argument("--out", required=True)
    run = sub.add_parser("measure")
    run.add_argument("--bluedot")
    run.add_argument("--batch", type=int, default=256)
    run.add_argument("--cohort", type=int, default=40)
    run.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.command == "capture-bluedot":
        capture_bluedot(Path(args.out))
    else:
        measure(args)


if __name__ == "__main__":
    main()
