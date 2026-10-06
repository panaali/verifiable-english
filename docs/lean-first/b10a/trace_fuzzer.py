"""Run either checkout's differential fuzzer and fingerprint every sampled answer.

This wrapper lives outside the checkout under test. It instruments the existing
fuzzer at its evaluation boundary, so old and new checkouts use the same trace
format without modifying the base revision or its baseline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def trace_run(df, run):
    """Return (fuzzer result, per-surface digests) for one complete fuzzer run."""
    sampled = {}
    replayed = {"count": 0, "inputs": hashlib.sha256(), "answers": hashlib.sha256()}
    original_sample, original_evaluate, original_replay = df.sample, df.evaluate, df.replay

    def sample(surface, *arguments):
        rows = original_sample(surface, *arguments)
        if surface.name in sampled:
            raise RuntimeError(f"sampled surface twice: {surface.name}")
        sampled[surface.name] = {
            "count": 0, "expected": len(rows),
            "inputs": hashlib.sha256(), "answers": hashlib.sha256(),
        }
        return rows

    def evaluate(surface, items):
        results = original_evaluate(surface, items)
        state = sampled.get(surface.name)
        if state is not None and state["count"] < state["expected"]:
            if len(items) != len(results) or state["count"] + len(items) > state["expected"]:
                raise RuntimeError(f"sample trace length mismatch: {surface.name}")
            for (seed, root), (_, _, answers, _) in zip(items, results):
                for field, value in (("inputs", [seed.id, surface.profile(seed, root), root]),
                                     ("answers", answers)):
                    state[field].update(df.canonical(value).encode("utf-8") + b"\n")
                state["count"] += 1
        return results

    def replay(entries, surfaces):
        results = original_replay(entries, surfaces)
        if len(results) != len(entries):
            raise RuntimeError("baseline replay trace length mismatch")
        for entry, (returned_entry, status, now) in zip(entries, results):
            if returned_entry != entry:
                raise RuntimeError("baseline replay trace order mismatch")
            replayed["inputs"].update(df.canonical(entry).encode("utf-8") + b"\n")
            replayed["answers"].update(df.canonical([status, now]).encode("utf-8") + b"\n")
            replayed["count"] += 1
        return results

    df.sample, df.evaluate, df.replay = sample, evaluate, replay
    try:
        result = run()
        trace = {}
        for name, state in sorted(sampled.items()):
            if state["count"] != state["expected"] or state["count"] == 0:
                raise RuntimeError(f"incomplete sample trace: {name}")
            trace[name] = {"count": state["count"],
                           "inputs_sha256": state["inputs"].hexdigest(),
                           "answers_sha256": state["answers"].hexdigest()}
        if not trace:
            raise RuntimeError("no samples traced")
        trace["baseline_replay"] = {"count": replayed["count"],
                                    "inputs_sha256": replayed["inputs"].hexdigest(),
                                    "answers_sha256": replayed["answers"].hexdigest()}
        return result, trace
    finally:
        df.sample, df.evaluate, df.replay = original_sample, original_evaluate, original_replay


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("trace", type=Path)
    args, fuzzer_args = parser.parse_known_args()
    sys.path.insert(0, str(args.root.resolve()))
    from tools import difffuzz as df

    result, trace = trace_run(df, lambda: df.main(fuzzer_args))
    args.trace.write_text(json.dumps(trace, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
