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
input. (Rust has no source commands since lean-first batch 15b: `parse`,
`format`, `evaluate`, `countermodel` and `check-countermodel` are gone, and
`ve conformance` refuses a case it reads no kind of.) A clean run is evidence of equivalence
over these exercised inputs only, alongside the dependency argument and the
required suites; it is not a proof independent of input coverage. A run that
times out (either binary, any invocation) or an empty invocation list makes the
differential invalid (exit 1): partial output is not evidence of equal output.
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
    return found


def run(binary: Path, invocation: Invocation) -> tuple[int | str, bytes, bytes]:
    """Exit code, stdout and stderr; a timed-out run keeps its partial output under the code "timeout"."""
    try:
        done = subprocess.run([str(binary), *invocation.args], input=invocation.stdin, capture_output=True,
                              cwd=ROOT, timeout=TIMEOUT, check=False)
    except subprocess.TimeoutExpired as expired:
        return "timeout", expired.stdout or b"", expired.stderr or b""
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
    if new.is_file() and baseline.resolve() == new.resolve():
        print(f"--new is the baseline itself ({baseline}); compare a build of the edited sources", file=sys.stderr)
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
    differences, timeouts = [], []
    for invocation, old, fresh in results:
        parts = [part for part, a, b in zip(("exit code", "stdout", "stderr"), old, fresh) if a != b]
        if parts:
            differences.append(f"{invocation.command} {invocation.label}: {', '.join(parts)} differ")
        sides = [side for side, result in (("baseline", old), ("new", fresh)) if result[0] == "timeout"]
        if sides:
            timeouts.append(f"{invocation.command} {invocation.label}: {' and '.join(sides)} timed out "
                            f"after {TIMEOUT} s")
    print(f"baseline {old_digest}\nnew      {new_digest} "
          f"({'pinned' if new_digest in rust_build.pinned_digests() else 'NOT pinned'})")
    print(", ".join(f"{name} {count}" for name, count in sorted(counts.items())))
    for line in (timeouts + differences)[:50]:
        print(line, file=sys.stderr)
    print(f"{len(work)} invocations, {len(differences)} differences, {len(timeouts)} timed out")
    if timeouts or not work:
        print("INVALID differential: " + (f"{len(timeouts)} invocations timed out, so their output was not "
                                          "compared in full" if timeouts else "no invocations"), file=sys.stderr)
    return 1 if differences or timeouts or not work else 0


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
