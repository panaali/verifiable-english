#!/usr/bin/env python3
"""Lean output differential (bundle OUT of docs/CONSOLIDATION-PLAN.md, step 0).

The Lean twin of layers2's Rust bundle D. Before a Lean edit, copy every `lean_exe` of
`lean/lakefile.toml` aside, from a build of the committed sources:

    python3 tools/lean_output_diff.py --save-baseline

After it, rebuild and compare the two builds byte for byte (exit code, stdout and stderr) over
the same invocations:

    python3 tools/lean_output_diff.py --build [--recorded DIR] [--contract-inputs FILE]

The invocations are:

* every case-reading mode (`ve_conformance` with no mode, `check-certificate`, `order` and
  `route`; `ve_quantity`; every `ve_*_route`; `ve_diagnose <unit>` for every registered unit) over
  every `conformance/*.json` corpus that is a list of cases and every `lean/VE/*/examples/*.json`
  case file. A mode is given every corpus, matching or not: a corpus of another route's cases
  exercises its rejection path, which must not change either;
* with `--contract-inputs`, the `soft-norms@0` inputs that `tests/contract_input_recorder.py`
  wrote (`VE_CONTRACT_INPUTS`), as `soft-elaborate` cases for `ve_soft_norms_route` and
  `ve_diagnose soft-norms@0`;
* with `--recorded`, every Lean executable invocation the test suite made, as recorded by
  `tests/lean_input_recorder.py` (`VE_LEAN_INPUTS`): arguments, input files and standard input,
  `ve_service` sessions included.

`--save-baseline` refuses a build that is not of the committed Lean sources (uncommitted changes
under `lean/`, or `lake build --no-build` reports work to do) and a `ve_service` that is not
pinned in `lean/checkers.lock`. An executable whose new build is byte-identical to its baseline
is not run (identical programs, identical output); `--all` runs it anyway. A clean comparison is
evidence of equal output over these inputs only; a run that times out, or an empty invocation
list, makes the differential invalid (exit 1). The full recorded corpus of a suite run is large
(about 10,000 invocations, tens of minutes at `--jobs 8`).
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
BIN = LEAN / ".lake/build/bin"
BASELINE = LEAN / ".lake/ve-output-baseline"
LOCK = LEAN / "checkers.lock"
TIMEOUT = 300

# Executables that read a case list from a path or `-`, with their mode arguments. `ve_diagnose`
# units are read from `VE/WireContract/Diagnose.lean`.
CASE_MODES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ve_conformance", ()), ("ve_conformance", ("check-certificate",)), ("ve_conformance", ("order",)),
    ("ve_conformance", ("route",)), ("ve_quantity", ()), ("ve_norms_route", ()), ("ve_discourse_route", ()),
    ("ve_speech_acts_route", ()), ("ve_soft_norms_route", ()), ("ve_rights_route", ()),
    ("ve_reports_route", ()), ("ve_alternatives_route", ()), ("ve_risk_route", ()),
    ("ve_norm_defaults_route", ()), ("ve_readings_route", ()),
)


class Invocation(NamedTuple):
    exe: str
    label: str
    args: tuple[str, ...]
    stdin: bytes | None = None


def executables(root: Path = ROOT) -> list[str]:
    lakefile = tomllib.loads((root / "lean/lakefile.toml").read_text())
    return sorted(exe["name"] for exe in lakefile.get("lean_exe", []))


def diagnose_units(root: Path = ROOT) -> list[str]:
    text = (root / "lean/VE/WireContract/Diagnose.lean").read_text()
    return re.findall(r'\("([\w.-]+@\d+)", ⟨', text)


def case_corpora(root: Path = ROOT) -> list[Path]:
    """`conformance/*.json` files whose top level is a list, and the Lean example case files."""
    found = []
    for path in [*sorted((root / "conformance").glob("*.json")), *sorted((root / "lean/VE").glob("*/examples/*.json"))]:
        try:
            if isinstance(json.loads(path.read_text()), list):
                found.append(path)
        except ValueError:
            continue
    return found


def write(path: Path, data: str | bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode() if isinstance(data, str) else data)
    return str(path)


def static_invocations(root: Path = ROOT) -> list[Invocation]:
    modes = [*CASE_MODES, *(("ve_diagnose", (unit,)) for unit in diagnose_units(root))]
    found = []
    for corpus in case_corpora(root):
        name = corpus.relative_to(root).as_posix()
        for exe, mode in modes:
            found.append(Invocation(exe, f"{' '.join(mode)} {name}".strip(), (*mode, str(corpus))))
    return found


def contract_invocations(path: Path) -> list[Invocation]:
    rows = json.loads(path.read_text())
    cases = [{"id": f"recorded-{index}", "kind": "soft-elaborate", "environment": environment, "norms": norms}
             for index, (_label, environment, norms) in enumerate(rows)]
    text = json.dumps(cases, ensure_ascii=False).encode()
    return [Invocation("ve_soft_norms_route", f"contract inputs {path.name}", ("-",), text),
            Invocation("ve_diagnose", f"soft-norms@0 contract inputs {path.name}", ("soft-norms@0", "-"), text)]


def recorded_invocations(folder: Path, scratch: Path) -> list[Invocation]:
    """The invocations of `tests/lean_input_recorder.py`, deduplicated, input files restored."""
    found, seen = [], set()
    for path in sorted(folder.glob("*.jsonl")):
        for line in path.read_text().splitlines():
            record = json.loads(line)
            key = hashlib.sha256(json.dumps([record["exe"], record["args"], record["files"], record["stdin"]],
                                            sort_keys=True).encode()).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            args = []
            for arg in record["args"]:
                index = re.fullmatch(r"@file:(\d+)", arg)
                if index:
                    content = base64.b64decode(record["files"][int(index[1])]["data"])
                    name = record["files"][int(index[1])]["name"]
                    args.append(write(scratch / "recorded" / key[:16] / index[1] / name, content))
                else:
                    args.append(arg)
            stdin = base64.b64decode(record["stdin"]) if record["stdin"] is not None else None
            found.append(Invocation(record["exe"], f"recorded {record.get('test', '?')} [{key[:12]}]",
                                    tuple(args), stdin))
    return found


def run(binary: Path, invocation: Invocation) -> tuple[int | str, bytes, bytes]:
    """Exit code, stdout and stderr; a timed-out run keeps its partial output under the code "timeout"."""
    try:
        done = subprocess.run([str(binary), *invocation.args], input=invocation.stdin if invocation.stdin is not None
                              else b"", capture_output=True, cwd=ROOT, timeout=TIMEOUT, check=False)
    except subprocess.TimeoutExpired as expired:
        return "timeout", expired.stdout or b"", expired.stderr or b""
    return done.returncode, done.stdout, done.stderr


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True).stdout


def save_baseline(target: Path) -> int:
    dirty = [line for line in git("status", "--porcelain", "--untracked-files=all", "--", "lean").splitlines()
             if "/.lake/" not in line
             and re.search(r"\.lean$|lakefile\.toml$|lean-toolchain$|lake-manifest\.json$", line)]
    if dirty:
        print("uncommitted changes under lean/; the baseline must be a build of committed sources:\n  "
              + "\n  ".join(dirty[:10]), file=sys.stderr)
        return 2
    names = executables()
    built = subprocess.run(["lake", "build", "--no-build", *names], cwd=LEAN, capture_output=True, text=True,
                           check=False)
    if built.returncode:
        print("lake build --no-build reports work to do; run lake build on the committed sources first:\n"
              + built.stdout[-1500:] + built.stderr[-1500:], file=sys.stderr)
        return 2
    pinned = set(json.loads(LOCK.read_text()).get("ve_service", []))
    if digest(BIN / "ve_service") not in pinned:
        print(f"ve_service ({digest(BIN / 've_service')}) is not pinned in {LOCK.relative_to(ROOT)}", file=sys.stderr)
        return 2
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    manifest = {"commit": git("rev-parse", "HEAD").strip(), "executables": {}}
    for name in names:
        shutil.copy2(BIN / name, target / name)
        manifest["executables"][name] = digest(target / name)
    (target / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"baseline of {manifest['commit'][:12]}: {len(names)} executables copied to {target}")
    return 0


def weight(invocation: Invocation) -> int:
    """Input bytes, to start the longest runs first."""
    size = len(invocation.stdin or b"")
    for arg in invocation.args:
        path = Path(arg)
        if path.is_absolute() and path.is_file():
            size += path.stat().st_size
    return size


def compare(baseline: Path, new: Path, extra: list[Invocation], scratch: Path, *, jobs: int = 8,
            everything: bool = False) -> int:
    manifest_path = baseline / "manifest.json"
    if not manifest_path.is_file():
        print(f"no baseline at {baseline}; run --save-baseline before the Lean edit", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text())
    for name, value in manifest["executables"].items():
        if digest(baseline / name) != value:
            print(f"baseline {name} does not match its manifest digest", file=sys.stderr)
            return 2
    missing = [name for name in executables() if name not in manifest["executables"] or not (new / name).is_file()]
    if missing:
        print(f"executables missing from the baseline or the new build: {', '.join(missing)}", file=sys.stderr)
        return 2
    changed = sorted(name for name in manifest["executables"] if digest(new / name) != manifest["executables"][name])
    work = [*static_invocations(), *extra]
    # A byte-identical executable gives identical output on every input; its runs are skipped
    # unless --all asks for them.
    run_work = sorted((i for i in work if everything or i.exe in changed), key=weight, reverse=True)

    def both(invocation: Invocation) -> tuple[Invocation, tuple, tuple]:
        return invocation, run(baseline / invocation.exe, invocation), run(new / invocation.exe, invocation)

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        results = list(pool.map(both, run_work))
    differences, timeouts = [], []
    for invocation, old, fresh in results:
        parts = [part for part, a, b in zip(("exit code", "stdout", "stderr"), old, fresh) if a != b]
        if parts:
            differences.append(f"{invocation.exe} {invocation.label}: {', '.join(parts)} differ")
        sides = [side for side, result in (("baseline", old), ("new", fresh)) if result[0] == "timeout"]
        if sides:
            timeouts.append(f"{invocation.exe} {invocation.label}: {' and '.join(sides)} timed out after {TIMEOUT} s")
    print(f"baseline {manifest['commit'][:12]}; executables rebuilt with a different digest: "
          f"{', '.join(changed) if changed else 'none'}")
    print(", ".join(f"{name} {count}" for name, count in sorted(Counter(i.exe for i in work).items())))
    for line in (timeouts + differences)[:50]:
        print(line, file=sys.stderr)
    skipped = len(work) - len(run_work)
    print(f"{len(work)} invocations, {len(run_work)} run on both builds, {skipped} skipped as their executable "
          f"is byte-identical to the baseline; {len(differences)} differences, {len(timeouts)} timed out")
    if timeouts or not work:
        print("INVALID differential: " + (f"{len(timeouts)} invocations timed out, so their output was not "
                                          "compared in full" if timeouts else "no invocations"), file=sys.stderr)
    return 1 if differences or timeouts or not work else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--save-baseline", action="store_true", help="copy the current build to --baseline and stop")
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--build", action="store_true", help="run lake build before comparing")
    parser.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1), help="parallel invocations")
    parser.add_argument("--all", action="store_true",
                        help="also run executables that are byte-identical to the baseline")
    parser.add_argument("--new", type=Path, default=BIN, help="the folder of the executables to compare")
    parser.add_argument("--recorded", type=Path, help="a VE_LEAN_INPUTS folder of tests/lean_input_recorder.py")
    parser.add_argument("--contract-inputs", type=Path, help="a VE_CONTRACT_INPUTS file of "
                                                             "tests/contract_input_recorder.py")
    args = parser.parse_args(argv)
    if args.save_baseline:
        return save_baseline(args.baseline)
    if args.build:
        built = subprocess.run(["lake", "build"], cwd=LEAN, check=False, stdout=subprocess.DEVNULL)
        if built.returncode:
            return built.returncode
    with tempfile.TemporaryDirectory(prefix="ve-lean-output-diff-") as folder:
        extra: list[Invocation] = []
        if args.contract_inputs:
            extra += contract_invocations(args.contract_inputs)
        if args.recorded:
            recorded = recorded_invocations(args.recorded, Path(folder))
            if not recorded:
                print(f"no recorded invocations in {args.recorded}", file=sys.stderr)
                return 1
            extra += recorded
        return compare(args.baseline, args.new, extra, Path(folder), jobs=args.jobs, everything=args.all)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
