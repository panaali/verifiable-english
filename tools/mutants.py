"""Seeded-mutant harness: every committed mutant must make its named tests fail.

    uv run python tools/mutants.py MUTANTS.json [--id ID ...] [--evidence OUT.json] [--no-baseline]

`MUTANTS.json` is `{"mutants": [...]}`; each mutant is

    {"id": "M1", "file": "ve/x.py", "find": "...", "replace": "...",
     "tests": ["tests/test_x.py::test_y", ...],      # pytest node ids, or
     "command": ["python", "tools/gate.py", ...],     # a command expected to exit non-zero
     "claim": "the behaviour the tests guard"}

For each mutant the harness checks that `find` occurs exactly once in `file`, runs the tests on the unmutated
file (they must pass: a test that already fails proves nothing), applies the replacement, runs them again and
requires that at least one named test FAILED (pytest exit 1 with the node in its failure summary; a
collection error or an interrupted run is not a kill), or that the command exits non-zero. The file's exact
bytes are restored in every case, also on an interrupt. Exit 1 if any mutant survives, any baseline fails or
any `find` is missing or ambiguous; `--evidence` writes the per-mutant results.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import nested_pytest  # noqa: E402
FAILED = re.compile(r"^(?:FAILED|ERROR) (\S+?)(?: - .*)?$", re.MULTILINE)


class MutantError(Exception):
    """A mutant that cannot be applied as written."""


@contextmanager
def applied(path: Path, find: str, replace: str):
    """`path` with its one occurrence of `find` replaced, restored to its exact bytes afterwards (also when
    the process is interrupted or terminated)."""
    original = path.read_bytes()
    text = original.decode()
    if text.count(find) != 1:
        raise MutantError(f"{path.name}: the find text occurs {text.count(find)} times, not once")
    previous = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}

    def restore_and_exit(signum, frame):
        raise KeyboardInterrupt  # the finally below restores the file

    for sig in previous:
        signal.signal(sig, restore_and_exit)
    stat = path.stat()
    try:
        path.write_text(text.replace(find, replace, 1))
        # Python trusts a cached .pyc whose source has the same size and mtime (in whole seconds): a
        # same-length mutant written within the second of the last import would run the old bytecode.
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 2_000_000_000))
        yield
    finally:
        path.write_bytes(original)
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def _pytest(tests: list[str], root: Path) -> tuple[int, set[str], str]:
    done = subprocess.run(nested_pytest.command(["-q", "-rfE", "-p", "no:cacheprovider", *tests]), cwd=root,
                          env=nested_pytest.environment(os.environ), capture_output=True, text=True)
    output = done.stdout + done.stderr
    return done.returncode, set(FAILED.findall(output)), output[-1500:]


def _command(argv: list[str], root: Path) -> tuple[int, str]:
    argv = [sys.executable if part == "python" else part for part in argv]
    done = subprocess.run(argv, cwd=root, capture_output=True, text=True)
    return done.returncode, (done.stdout + done.stderr)[-1500:]


def _killed_by(tests: list[str], code: int, failed: set[str]) -> list[str]:
    """The named tests the run reports as failed (a node id names its parametrized cases too)."""
    if code != 1:
        return []
    return sorted({test for test in tests for node in failed if node == test or node.startswith(test + "[")
                   or node.startswith(test + "::")})


def run(mutant: dict, baseline: bool = True, root: Path = ROOT) -> dict:
    """One mutant's result row (see the module docstring); `root` is the tree its paths and tests are in."""
    path = root / mutant["file"]
    tests, command = mutant.get("tests"), mutant.get("command")
    if bool(tests) == bool(command):
        raise MutantError(f"{mutant['id']}: name either tests or a command")
    row = {"id": mutant["id"], "file": mutant["file"], "claim": mutant.get("claim", ""),
           "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
           **({"tests": tests} if tests else {"command": command})}
    started = time.monotonic()
    if baseline:
        if tests:
            code, failed, tail = _pytest(tests, root)
        else:
            code, tail = _command(command, root)
        row["baseline_exit"] = code
        if code != 0:
            row.update(killed=False, problem="the tests fail without the mutant", output_tail=tail)
            return row
    with applied(path, mutant["find"], mutant["replace"]):
        if tests:
            code, failed, tail = _pytest(tests, root)
            row["killed_by"] = _killed_by(tests, code, failed)
            row["killed"] = bool(row["killed_by"])
        else:
            code, tail = _command(command, root)
            row["killed"] = code != 0
    row.update(mutant_exit=code, seconds=round(time.monotonic() - started, 1), output_tail=tail)
    if not row["killed"]:
        row["problem"] = "the mutant survives"
    if hashlib.sha256(path.read_bytes()).hexdigest() != row["source_sha256"]:
        raise MutantError(f"{mutant['file']} was not restored")
    return row


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("mutants", type=Path)
    parser.add_argument("--id", action="append", help="run only this mutant (repeatable)")
    parser.add_argument("--evidence", type=Path, help="write the per-mutant results here")
    parser.add_argument("--no-baseline", action="store_true", help="skip the unmutated run")
    args = parser.parse_args(argv)
    mutants = json.loads(args.mutants.read_text())["mutants"]
    ids = [mutant["id"] for mutant in mutants]
    if len(set(ids)) != len(ids):
        raise SystemExit("mutant ids must be unique")
    unknown = set(args.id or ()) - set(ids)
    if unknown:
        raise SystemExit(f"unknown mutants: {sorted(unknown)}")
    rows = []
    for mutant in mutants:
        if args.id and mutant["id"] not in args.id:
            continue
        try:
            row = run(mutant, baseline=not args.no_baseline)
        except MutantError as exc:
            row = {"id": mutant["id"], "file": mutant.get("file"), "killed": False, "problem": str(exc)}
        rows.append(row)
        print(f"{row['id']}: {'killed' if row['killed'] else 'NOT KILLED'}"
              f"{' by ' + ', '.join(row['killed_by']) if row.get('killed_by') else ''}"
              f"{' (' + row['problem'] + ')' if row.get('problem') else ''}", flush=True)
    if args.evidence:
        args.evidence.write_text(json.dumps({"mutants": rows}, indent=1) + "\n")
    survivors = [row["id"] for row in rows if not row["killed"]]
    print(f"mutants: {len(rows) - len(survivors)}/{len(rows)} killed"
          + (f"; not killed: {', '.join(survivors)}" if survivors else ""))
    return 1 if survivors or not rows else 0


if __name__ == "__main__":
    sys.exit(main())
