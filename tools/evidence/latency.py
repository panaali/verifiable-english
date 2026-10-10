"""Paired base and head CPU samples and the 20% rule (gate item 4 of the lean-first and architecture batches).

A latency record is `{"head_commit", "pass", "allowance", "samples": {key: {"base_cpu_ms", "head_cpu_ms"}}}`.
A key names one workload exactly (a document's full path, never its file name). `problems` fails a record
that is empty, misses a key the batch names, holds an empty key (or, read with `tools.evidence.load`, a key
twice), a sample that is not a positive measurement on both sides (unavailable on both is no evidence), or a
head above `1 + allowance` times its base.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
import os
from pathlib import Path
import resource
import subprocess

ALLOWANCE = 0.2


def schedstat(path: str) -> tuple[int, int] | None:
    """(on-CPU ns, runqueue wait ns) of a task from its `/proc/.../schedstat`, or None where it is unavailable."""
    try:
        run, wait, _ = Path(path).read_text().split()
        return int(run), int(wait)
    except (OSError, ValueError):
        return None


def cpu_ns(pid: int) -> int:
    """The on-CPU nanoseconds of process `pid` so far; an unreadable value is an error, not zero."""
    stat = schedstat(f"/proc/{pid}/schedstat")
    if stat is None:
        raise OSError(f"no schedstat for process {pid}")
    return stat[0]


def paired(keys: Iterable[str], base: Callable[[str], float], head: Callable[[str], float],
           pairs: int) -> dict[str, dict]:
    """For each key, `pairs` alternating measurements of the base and the head (each a CPU time in ms), and the
    mean of each side. Alternation spreads host load over both sides alike."""
    if pairs <= 0:
        raise ValueError("pairs must be positive")
    samples: dict[str, dict] = {}
    for key in keys:
        if not isinstance(key, str) or not key:
            raise ValueError(f"a latency key must be a non-empty string, not {key!r}")
        if key in samples:
            raise ValueError(f"the latency key {key!r} occurs twice")
        base_ms, head_ms = [], []
        for _ in range(pairs):
            base_ms.append(base(key))
            head_ms.append(head(key))
        samples[key] = {"pairs": pairs, "base_cpu_ms": round(sum(base_ms) / pairs, 6),
                        "head_cpu_ms": round(sum(head_ms) / pairs, 6)}
    return samples


def within(row: dict, allowance: float = ALLOWANCE) -> bool:
    return row["head_cpu_ms"] <= (1 + allowance) * row["base_cpu_ms"]


def _measured(value) -> bool:
    return type(value) in (int, float) and value == value and value >= 0


def row_problems(samples, expected: Iterable[str] = (), allowance: float = ALLOWANCE) -> list[str]:
    """What keeps `samples` from showing the head within the allowance; [] when every row does."""
    if not isinstance(samples, dict) or not samples:
        return ["latency evidence is empty"]
    errors = [f"latency evidence has no sample for {key!r}" for key in sorted(set(expected) - samples.keys())]
    for key, row in samples.items():
        if not isinstance(key, str) or not key.strip():
            errors.append(f"latency evidence has an empty key {key!r}")
        if not isinstance(row, dict) or not _measured(row.get("base_cpu_ms")) or not _measured(
                row.get("head_cpu_ms")) or row["base_cpu_ms"] <= 0:
            errors.append(f"latency sample {key!r} is not measured on both sides")
        elif row.get("same_output", True) is not True:
            errors.append(f"latency sample {key!r}: the base and the head did not give one and the same output")
        elif not within(row, allowance):
            errors.append(f"latency sample {key!r}: head {row['head_cpu_ms']} ms is above "
                          f"{1 + allowance:g} x base {row['base_cpu_ms']} ms")
    return errors


def record(head_commit: str, samples: dict, method: str, allowance: float = ALLOWANCE, **extra) -> dict:
    """The latency record of `samples`; its `pass` is computed here, from the rows."""
    return {"head_commit": head_commit, "method": method, "allowance": allowance, "samples": samples,
            "pass": not row_problems(samples, allowance=allowance), **extra}


def problems(latency: dict, head: str, expected: Iterable[str] = (), allowance: float = ALLOWANCE) -> list[str]:
    """The errors of a saved latency record for the batch head `head`."""
    if not isinstance(latency, dict):
        return ["latency evidence is not a record"]
    errors = []
    if latency.get("head_commit") != head or latency.get("pass") is not True:
        errors.append("latency budget was not measured and passed on HEAD")
    rows = row_problems(latency.get("samples"), expected, allowance)
    if rows:
        errors.append(f"latency evidence is empty, malformed or above the {allowance:.0%} Lean CPU budget")
    return errors + rows


def run_command(root: Path, command: list[str], item: str) -> tuple[float, int, str]:
    """(CPU ms of the process tree, exit status, standard output) of `command` with `{input}` replaced by
    `item`, run in the checkout at `root` with its own sources first on the path."""
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    done = subprocess.run([part.replace("{input}", item) for part in command], cwd=root, capture_output=True,
                          text=True, env={**os.environ, "PYTHONPATH": str(root)})
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = after.ru_utime + after.ru_stime - usage.ru_utime - usage.ru_stime
    return cpu * 1000, done.returncode, done.stdout


def measure(base_root: Path, head_root: Path, command: list[str], inputs: Iterable[str], pairs: int,
            run=run_command) -> tuple[dict, list[str]]:
    """Paired samples of `command` on each input at both checkouts, keyed by the input's full path (two inputs
    with one file name are two rows), and the errors: unusable arguments, or an input whose output (exit
    status and standard output) is not one and the same non-empty output on every run of both sides."""
    inputs = list(inputs)
    if Path(base_root).resolve() == Path(head_root).resolve():
        return {}, [f"the base and head checkouts are the same directory {base_root}"]
    if not inputs or pairs <= 0 or not any("{input}" in part for part in command):
        return {}, ["latency measure needs inputs, a positive number of pairs and a command naming {input}"]
    missing = [item for item in inputs if not Path(item).is_file()]
    if missing:
        return {}, [f"no input {', '.join(missing)}"]
    keys = [str(Path(item).resolve()) for item in inputs]
    outputs = {key: {"base": set(), "head": set()} for key in keys}

    def side(name, root):
        def one(key):
            cpu, code, out = run(root, command, key)
            outputs[key][name].add((code, out))
            return cpu
        return one

    try:
        samples = paired(keys, side("base", base_root), side("head", head_root), pairs)
    except ValueError as exc:
        return {}, [str(exc)]
    errors = []
    for key, row in samples.items():
        seen = outputs[key]
        row["same_output"] = len(seen["base"]) == 1 and seen["base"] == seen["head"] and bool(
            next(iter(seen["base"]))[1])
        if not row["same_output"]:
            errors.append(f"latency input {key}: the output differs between runs or sides, or is empty")
    return samples, errors


def main(argv=None) -> int:
    import argparse
    import json
    import shlex

    from tools.evidence import EvidenceError, dump, load

    parser = argparse.ArgumentParser(prog="python -m tools.evidence latency", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="action", required=True)
    m = sub.add_parser("measure", help="run COMMAND on each input at both checkouts, alternating")
    m.add_argument("--base-root", type=Path, required=True)
    m.add_argument("--head-root", type=Path, required=True)
    m.add_argument("--head-commit", required=True)
    m.add_argument("--command", required=True, help="a shell-quoted command naming {input}")
    m.add_argument("--input", action="append", default=[], help="an input file (repeatable)")
    m.add_argument("--pairs", type=int, default=3)
    m.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("check", help="check a saved latency record")
    c.add_argument("latency", type=Path)
    c.add_argument("--head", required=True, help="the commit the record must have measured")
    c.add_argument("--key", action="append", default=[], help="a workload the record must hold")
    for p in (m, c):
        p.add_argument("--allowance", type=float, default=ALLOWANCE)
    args = parser.parse_args(argv)
    if args.action == "measure":
        samples, errors = measure(args.base_root, args.head_root, shlex.split(args.command), args.input, args.pairs)
        if samples:
            saved = record(args.head_commit, samples, f"paired runs of {args.command}; RUSAGE_CHILDREN CPU",
                           args.allowance)
            saved["pass"] = saved["pass"] and not errors
            dump(args.out, saved)
            errors += problems(saved, args.head_commit, allowance=args.allowance)
        print(json.dumps(samples, indent=1))
    else:
        try:
            errors = problems(load(args.latency), args.head, args.key, args.allowance)
        except EvidenceError as exc:
            errors = [str(exc)]
    print("\n".join(errors) if errors else "latency PASS")
    return 1 if errors else 0
