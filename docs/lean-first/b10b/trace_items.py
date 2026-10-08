"""Run a checkout's differential fuzzer against a named baseline and record every answer.

Batch 10a's trace (`docs/lean-first/b10a/trace_fuzzer.py`) gives per-surface and
baseline-replay digests. This wrapper keeps those digests and adds one record per
sampled input and per replayed baseline entry, so the batch 10b gate can name each
input whose answer changed. Inputs that mention norm-defaults keep their full answers,
since only that route's decoder changed; any other change has no answers recorded and
the gate fails closed on it.

Both checkouts are run against the same baseline file (`--baseline`), so the replay
inputs are the same on both sides.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

B10A_TRACE = Path(__file__).resolve().parents[1] / "b10a" / "trace_fuzzer.py"


def _load_b10a():
    spec = importlib.util.spec_from_file_location("b10a_trace_fuzzer", B10A_TRACE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(df, value) -> str:
    return hashlib.sha256(df.canonical(value).encode("utf-8")).hexdigest()


def record_run(df, run, baseline: Path):
    """Return (fuzzer result, 10a digest trace, per-input records) for one fuzzer run."""
    sampled: dict[str, list] = {}
    expected: dict[str, int] = {}
    replayed: list[dict] = []
    new: dict[str, str] = {}
    original = df.sample, df.evaluate, df.replay, df.fuzz, df.entry_for

    def entry_for(finding, profile, minimised, answers, *args, **kwargs):
        # The input digest of each new finding, as its sampled record names it (run unminimised).
        new[finding.signature] = _sha(df, [finding.seed.id, profile, minimised])
        return original[4](finding, profile, minimised, answers, *args, **kwargs)

    def sample(surface, *arguments):
        rows = original[0](surface, *arguments)
        expected[surface.name] = len(rows)
        sampled[surface.name] = []
        return rows

    def evaluate(surface, items):
        results = original[1](surface, items)
        rows = sampled.get(surface.name)
        if rows is not None and len(rows) < expected[surface.name]:
            for (seed, root), (_, _, answers, _) in zip(items, results, strict=True):
                text = [seed.id, surface.profile(seed, root), root]
                row = {"input": _sha(df, text), "answers_sha256": _sha(df, answers)}
                if "norm-defaults" in df.canonical(text):
                    row["profile"] = text[1]
                    row["answers"] = answers
                rows.append(row)
        return results

    def replay(entries, surfaces):
        results = original[2](entries, surfaces)
        # `replay` answers surface by surface; record in baseline order (10a's trace checks the match).
        by_entry = {id(returned): (status, now) for returned, status, now in results}
        for entry in entries:
            status, now = by_entry[id(entry)]
            replayed.append({"id": entry["id"], "input": _sha(df, entry), "status": status,
                             "answers_sha256": _sha(df, [status, now]),
                             **({} if status == "reproduces" else {"now": now})})
        return results

    df.sample, df.evaluate, df.replay, df.entry_for = sample, evaluate, replay, entry_for
    df.fuzz = functools.partial(original[3], baseline_path=baseline)
    try:
        result, trace = _load_b10a().trace_run(df, run)
    finally:
        df.sample, df.evaluate, df.replay, df.fuzz, df.entry_for = original
    for name, rows in sampled.items():
        if len(rows) != expected[name]:
            raise RuntimeError(f"incomplete item records: {name}")
    return result, trace, {"sampled": sampled, "replayed": replayed, "new": new}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("trace", type=Path)
    parser.add_argument("items", type=Path)
    parser.add_argument("--baseline", type=Path, required=True)
    args, fuzzer_args = parser.parse_known_args()
    sys.path.insert(0, str(args.root.resolve()))
    from tools import difffuzz as df

    result, trace, items = record_run(df, lambda: df.main(fuzzer_args), args.baseline.resolve())
    args.trace.write_text(json.dumps(trace, sort_keys=True) + "\n")
    args.items.write_text(json.dumps(items, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
