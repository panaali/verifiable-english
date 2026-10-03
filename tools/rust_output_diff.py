#!/usr/bin/env python3
"""Rust output differential (bundle D of docs/ARCHITECTURE-LAYERS-PLAN2.md).

Before a Rust edit, copy the pinned release binary aside:

    python3 tools/rust_output_diff.py --save-baseline

After it, rebuild and compare the two binaries byte for byte (stdout, stderr
and exit code) over the same invocations:

    python3 tools/rust_output_diff.py --build

The invocations are `ve conformance` and `ve jsonl` over every
`conformance/*.json` corpus and `lean/VE/Route/examples/route-cases.json`,
`ve canonical-json` over those files and every `conformance/wire.json` raw
input, and `parse`, `format`, `evaluate`, `countermodel` and
`check-countermodel` over the sources, environments and models of the
source-bearing corpora and `examples/`. A clean run is evidence of equivalence
over these exercised inputs only, alongside the dependency argument and the
required suites; it is not a proof independent of input coverage.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rust_build  # noqa: E402

ROOT = rust_build.ROOT
BASELINE = ROOT / "rust/target/ve-baseline"
CORPORA = [*sorted((ROOT / "conformance").glob("*.json")), ROOT / "lean/VE/Route/examples/route-cases.json"]
# Corpora whose cases carry an environment and a canonical source with one statement per line.
SOURCE_CORPORA = ("evaluation", "closure", "identity", "parser")
SEARCH_BOUNDS = ("--max-domain-size", "2", "--max-evaluations", "200000")
TIMEOUT = 300


class Invocation(NamedTuple):
    command: str
    label: str
    args: tuple[str, ...]
    stdin: bytes | None = None


def write(path: Path, data: str | bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode() if isinstance(data, str) else data)
    return str(path)


def cli_invocations(label: str, env: str, source: Path | None, model: str | None,
                    lines: list[str], scratch: Path) -> list[Invocation]:
    found = []
    if source is not None:
        found += [Invocation(name, label, (name, "--env", env, "--source", str(source)))
                  for name in ("parse", "format")]
        if model is not None:
            found.append(Invocation("evaluate", label, ("evaluate", "--env", env, "--source", str(source),
                                                        "--model", model)))
    if lines:
        premises = write(scratch / "premises.ve", "".join(lines[:-1]) or "true.\n")
        conclusion = write(scratch / "conclusion.ve", lines[-1])
        problem = ("--env", env, "--premises", premises, "--conclusion", conclusion)
        found.append(Invocation("countermodel", label, ("countermodel", *problem, *SEARCH_BOUNDS)))
        if model is not None:
            found.append(Invocation("check-countermodel", label,
                                    ("check-countermodel", *problem, "--model", model)))
    return found


def invocations(scratch: Path) -> list[Invocation]:
    found = []
    for corpus in CORPORA:
        name = corpus.relative_to(ROOT).as_posix()
        data = json.loads(corpus.read_text())
        cases = data if isinstance(data, list) else [data]
        stream = write(scratch / "jsonl" / f"{corpus.stem}.jsonl",
                       "".join(json.dumps(case) + "\n" for case in cases))
        found += [Invocation("conformance", name, ("conformance", str(corpus))),
                  Invocation("jsonl", name, ("jsonl", stream)),
                  Invocation("canonical-json", name, ("canonical-json", str(corpus)))]
    for case in json.loads((ROOT / "conformance/wire.json").read_text()):
        found.append(Invocation("canonical-json", f"conformance/wire.json:{case['id']}", ("canonical-json",),
                                case["raw"].encode()))
    examples = ROOT / "examples"
    env, model = str(examples / "environment.json"), str(examples / "model.json")
    for source in sorted(examples.glob("*.ve")):
        found += cli_invocations(f"examples/{source.name}", env, source, model, [], scratch)
    premise, conclusion = (examples / "premise.ve").read_text(), (examples / "conclusion.ve").read_text()
    found += cli_invocations("examples/premise.ve+conclusion.ve", env, None, model,
                             [premise, conclusion], scratch / "examples")
    for corpus in SOURCE_CORPORA:
        for number, case in enumerate(json.loads((ROOT / f"conformance/{corpus}.json").read_text())):
            if "environment" not in case or not isinstance(case.get("source"), str):
                continue
            folder = scratch / corpus / str(number)
            env = write(folder / "environment.json", json.dumps(case["environment"]))
            model = (write(folder / "model.json", json.dumps(case["model"]))
                     if "model" in case else None)
            source = Path(write(folder / "source.ve", case["source"]))
            lines = case["source"].splitlines(keepends=True) if corpus != "parser" else []
            found += cli_invocations(f"conformance/{corpus}.json:{case.get('id', number)}", env, source,
                                     model, lines, folder)
    return found


def run(binary: Path, invocation: Invocation) -> tuple[int | str, bytes, bytes]:
    try:
        done = subprocess.run([str(binary), *invocation.args], input=invocation.stdin, capture_output=True,
                              cwd=ROOT, timeout=TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        return "timeout", b"", b""
    return done.returncode, done.stdout, done.stderr


def save_baseline(target: Path) -> int:
    binary = rust_build.RELEASE_BINARY
    if not binary.is_file():
        print(f"no release binary at {binary}; run python3 tools/rust_build.py first", file=sys.stderr)
        return 2
    value = rust_build.digest(binary)
    if value not in rust_build.pinned_digests():
        print(f"{binary} ({value}) is not pinned in {rust_build.LOCK}; the baseline must be the pinned "
              "binary, so rebuild it from the pinned sources first", file=sys.stderr)
        return 2
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(binary, target)
    print(f"baseline {value} copied to {target}")
    return 0


def compare(baseline: Path, new: Path) -> int:
    if not baseline.is_file():
        print(f"no baseline at {baseline}; run --save-baseline before the Rust edit", file=sys.stderr)
        return 2
    old_digest, new_digest = rust_build.digest(baseline), rust_build.digest(new)
    if old_digest not in rust_build.pinned_digests():
        print(f"baseline {baseline} ({old_digest}) is not a pinned binary", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="ve-rust-output-diff-") as folder:
        work = invocations(Path(folder))

        def both(invocation: Invocation) -> tuple[Invocation, tuple, tuple]:
            return invocation, run(baseline, invocation), run(new, invocation)

        with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as pool:
            results = list(pool.map(both, work))
    counts = Counter(invocation.command for invocation in work)
    differences = []
    for invocation, old, fresh in results:
        parts = [part for part, a, b in zip(("exit code", "stdout", "stderr"), old, fresh) if a != b]
        if parts:
            differences.append(f"{invocation.command} {invocation.label}: {', '.join(parts)} differ")
    print(f"baseline {old_digest}\nnew      {new_digest} "
          f"({'pinned' if new_digest in rust_build.pinned_digests() else 'NOT pinned'})")
    print(", ".join(f"{name} {count}" for name, count in sorted(counts.items())))
    timeouts = sum(old[0] == "timeout" for _, old, _ in results)
    if timeouts:
        print(f"{timeouts} baseline invocations timed out after {TIMEOUT} s (compared as such)")
    for line in differences[:50]:
        print(line, file=sys.stderr)
    print(f"{len(work)} invocations, {len(differences)} differences")
    return 1 if differences else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--save-baseline", action="store_true",
                        help="copy the pinned release binary to --baseline and stop")
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--build", action="store_true",
                        help="rebuild the release binary with tools/rust_build.py before comparing")
    parser.add_argument("--new", type=Path, default=rust_build.RELEASE_BINARY,
                        help="the binary to compare against the baseline")
    args = parser.parse_args(argv)
    if args.save_baseline:
        return save_baseline(args.baseline)
    if args.build:
        built = subprocess.run([sys.executable, str(ROOT / "tools/rust_build.py")], cwd=ROOT, check=False)
        if built.returncode:
            return built.returncode
    return compare(args.baseline, args.new)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
