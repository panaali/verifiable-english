#!/usr/bin/env python3
"""Lake's executables as they are on disk, not as their traces say (finding class 13: a stale binary).

Lake decides that an executable is up to date from its `.trace` alone: the trace's input hash matches the
current inputs, so the file beside it is taken as the one that trace's build wrote (the `outputs` hash). A trace
copied from another checkout, or a binary restored without its trace, breaks that: Lake then reports the old
binary up to date and every test, fuzz run and gate stage uses it (rd-6b review B2: `ve_conformance` of an older
tree under a trace copied from ve-nightly).

`stale(lean)` lists every executable under `lean/.lake/build/bin` whose trace's `outputs` is not the hash Lake
computes for the file now (`tools/lake_output_hash.lean`, run by the pinned toolchain: the oracle is Lean's own
`hash`, never a copy of it). `drop_stale(lean)` removes the trace and the `.hash` of each, so the next
`lake build` links it again. A trace that cannot be read is stale too (fail closed).

    python3 tools/lake_outputs.py           # exit 1 and list them when any executable is stale
    python3 tools/lake_outputs.py --drop    # remove their traces, so `lake build` rebuilds them
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
HASHER = ROOT / "tools/lake_output_hash.lean"


def lean_executable() -> str:
    """The `lean` of the pinned toolchain (elan's shim, `lean/lean-toolchain`); missing is an error."""
    found = shutil.which("lean") or shutil.which("lean", path=str(Path.home() / ".elan/bin"))
    if found is None:
        raise RuntimeError("lean is required to check Lake's executables against their traces")
    return found


def output_hashes(files: list[Path]) -> dict[Path, str]:
    """Lake's output hash of each file, computed by the toolchain `lean/lean-toolchain` pins."""
    if not files:
        return {}
    result = subprocess.run([lean_executable(), "--run", str(HASHER), *map(str, files)], cwd=LEAN,
                            capture_output=True, text=True, check=False,
                            timeout=float(os.environ.get("VE_LEAN_TIMEOUT", "600")))
    if result.returncode:
        raise RuntimeError(f"{HASHER.name} failed: {result.stderr.strip()[-2000:]}")
    hashes = {}
    for line in result.stdout.splitlines():
        value, _, name = line.partition(" ")
        hashes[Path(name)] = value
    if set(hashes) != set(files):
        raise RuntimeError(f"{HASHER.name} did not hash every file it was given")
    return hashes


def recorded(trace: Path) -> str | None:
    """The `outputs` a trace records, or None when it cannot be read."""
    try:
        value = json.loads(trace.read_text())["outputs"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return str(value) if isinstance(value, (str, int)) and not isinstance(value, bool) else None


def stale(lean: Path = LEAN) -> list[Path]:
    """The executables whose trace does not record the file on disk, in name order."""
    directory = lean / ".lake/build/bin"
    traced = sorted(trace.with_suffix("") for trace in directory.glob("*.trace")) if directory.is_dir() else []
    present = [binary for binary in traced if binary.is_file()]
    hashes = output_hashes(present)
    return [binary for binary in present
            if recorded(binary.with_name(binary.name + ".trace")) != hashes[binary]]


def drop_stale(lean: Path = LEAN) -> list[Path]:
    """Remove the trace and the `.hash` of each stale executable; the executables dropped."""
    found = stale(lean)
    for binary in found:
        for suffix in (".trace", ".hash"):
            binary.with_name(binary.name + suffix).unlink(missing_ok=True)
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--drop", action="store_true", help="remove the traces of stale executables")
    parser.add_argument("--lean", type=Path, default=LEAN, help="the Lake project (default: lean/)")
    args = parser.parse_args(argv)
    found = drop_stale(args.lean) if args.drop else stale(args.lean)
    for binary in found:
        print(f"{'dropped the trace of' if args.drop else 'stale:'} {binary}")
    return 0 if args.drop or not found else 1


if __name__ == "__main__":
    sys.exit(main())
