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

A separate rule handles executables that no target builds any more (a `lean_exe` removed from the lakefile, or
renamed): Lake never touches them again, and a worktree carries them for good (2.1 GB of them in ve-integration,
docs/test-architecture/leanshare/REPORT.md). `obsolete(lean)` lists every file in that directory that is not a
`lean_exe` of the lakefile, or that executable's trace, Lake hash or the client's digest sidecar
(`ve/backends/lean_service.py`, `executable_sha256`); `drop_obsolete(lean)` removes them. The targets come from
`lakefile.toml`, read with the TOML library; a `lakefile.lean` (a configuration only Lake can evaluate) is an error,
so nothing is removed on a guess.

    python3 tools/lake_outputs.py                   # exit 1 and list them when any executable is stale
    python3 tools/lake_outputs.py --drop            # remove their traces, so `lake build` rebuilds them
    python3 tools/lake_outputs.py --obsolete        # exit 1 and list the files no lakefile target names
    python3 tools/lake_outputs.py --drop-obsolete   # remove those files
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
HASHER = ROOT / "tools/lake_output_hash.lean"
# The files an executable `<name>` owns in the bin directory besides itself: Lake's trace and output hash, and the
# client's SHA-256 sidecar (ve/backends/lean_service.py, executable_sha256).
OWNED_SUFFIXES = (".trace", ".hash", ".sha256-cache")


def lean_executable(env: dict | None = None, name: str = "lean") -> str:
    """The `lean` (or `name`: `lake`) of the pinned toolchain (elan's shim, `lean/lean-toolchain`) on the PATH of
    `env` (default: this process's), else in the account's elan; missing is an error. The account's home is the
    password database's, as in `tools/gate.py`: HOME is ambient and the gate replaces it."""
    path = (env if env is not None else os.environ).get("PATH")
    account = Path(pwd.getpwuid(os.getuid()).pw_dir)
    found = shutil.which(name, path=path) or shutil.which(name, path=str(account / ".elan/bin"))
    if found is None:
        raise RuntimeError(f"{name} is required to check Lake's executables against their traces")
    return found


def output_hashes(files: list[Path], env: dict | None = None) -> dict[Path, str]:
    """Lake's output hash of each file, computed by the toolchain `lean/lean-toolchain` pins, run in `env` (the
    caller's environment: the gate passes its own allowlisted one)."""
    if not files:
        return {}
    settings = env if env is not None else os.environ
    result = subprocess.run([lean_executable(env), "--run", str(HASHER), *map(str, files)], cwd=LEAN, env=env,
                            capture_output=True, text=True, check=False,
                            timeout=float(settings.get("VE_LEAN_TIMEOUT", "600")))
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


def stale(lean: Path = LEAN, env: dict | None = None) -> list[Path]:
    """The executables whose trace does not record the file on disk, in name order."""
    directory = lean / ".lake/build/bin"
    traced = sorted(trace.with_suffix("") for trace in directory.glob("*.trace")) if directory.is_dir() else []
    present = [binary for binary in traced if binary.is_file()]
    hashes = output_hashes(present, env)
    return [binary for binary in present
            if recorded(binary.with_name(binary.name + ".trace")) != hashes[binary]]


def drop_stale(lean: Path = LEAN, env: dict | None = None) -> list[Path]:
    """Remove the trace and the `.hash` of each stale executable; the executables dropped."""
    found = stale(lean, env)
    for binary in found:
        for suffix in (".trace", ".hash"):
            binary.with_name(binary.name + suffix).unlink(missing_ok=True)
    return found


def executables(lean: Path = LEAN) -> list[str]:
    """The file names of the lakefile's `lean_exe` targets, default or not, in lakefile order. Lake names the file
    `exeName`, by default the target's name (`LeanExeConfig.exeName`: the name's components joined by `-`); a name
    that is not one plain component, or a lakefile Lake alone can evaluate, is an error (fail closed)."""
    if (lean / "lakefile.lean").exists():
        raise RuntimeError(f"{lean / 'lakefile.lean'}: only Lake can read its targets")
    try:
        config = tomllib.loads((lean / "lakefile.toml").read_text())
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise RuntimeError(f"cannot read {lean / 'lakefile.toml'}: {error}") from None
    targets = config.get("lean_exe", [])
    if not isinstance(targets, list):
        raise RuntimeError("lakefile.toml: lean_exe is not a list of tables")
    names = []
    for target in targets:
        name = target.get("exeName", target.get("name")) if isinstance(target, dict) else None
        if not isinstance(name, str) or not name.isidentifier() or not name.isascii():
            raise RuntimeError(f"lakefile.toml: cannot tell the file name of the lean_exe {target!r}")
        names.append(name)
    return names


def obsolete(lean: Path = LEAN) -> list[Path]:
    """The files under `.lake/build/bin` that belong to no `lean_exe` of the lakefile, in name order."""
    directory = lean / ".lake/build/bin"
    if not directory.is_dir():
        return []
    owned = {f"{name}{suffix}" for name in executables(lean) for suffix in ("", *OWNED_SUFFIXES)}
    return sorted(path for path in directory.iterdir() if path.name not in owned)


def drop_obsolete(lean: Path = LEAN) -> list[Path]:
    """Remove every file `obsolete` lists; the files removed."""
    found = obsolete(lean)
    for path in found:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--drop", action="store_true", help="remove the traces of stale executables")
    action.add_argument("--obsolete", action="store_true", help="list the files no lakefile target names")
    action.add_argument("--drop-obsolete", action="store_true", help="remove the files no lakefile target names")
    parser.add_argument("--lean", type=Path, default=LEAN, help="the Lake project (default: lean/)")
    args = parser.parse_args(argv)
    if args.obsolete or args.drop_obsolete:
        found = drop_obsolete(args.lean) if args.drop_obsolete else obsolete(args.lean)
        for path in found:
            print(f"{'removed' if args.drop_obsolete else 'obsolete:'} {path}")
        return 0 if args.drop_obsolete or not found else 1
    found = drop_stale(args.lean) if args.drop else stale(args.lean)
    for binary in found:
        print(f"{'dropped the trace of' if args.drop else 'stale:'} {binary}")
    return 0 if args.drop or not found else 1


if __name__ == "__main__":
    sys.exit(main())
