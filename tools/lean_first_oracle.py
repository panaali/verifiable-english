"""The frozen pre-deletion Python, kept as a test oracle (docs/LEAN-FIRST-PLAN.md, section 6.2;
DRI answer 7).

The oracle is the commit tagged `lean-first/oracle-python` (batch 0's base): the Python checkers
before any Lean-first batch deleted a line. `conformance/lean-first/oracle.json` freezes, by
SHA-256 at that commit, what the oracle depends on: its dependency lock, the baseline artifacts,
the frozen conformance fixtures and the contracts. It is run in isolation as
`conformance/replay_baseline.py` runs its pinned code: a `git archive` of the commit in a
temporary directory, imported from there with this checkout's Python environment, which must
still be the frozen lock's. It labels new fixtures `oracle: lean+pinned-python` and is deleted
after batch 18 plus 14 clean days.

Usage::

    tools/lean_first_oracle.py --check          # the tag and every frozen file are intact
    tools/lean_first_oracle.py --write          # (batch 0 only) record the manifest
    tools/lean_first_oracle.py run SCRIPT.py    # run SCRIPT in the oracle; its stdout is the answer
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "conformance/lean-first/oracle.json"
TAG = "lean-first/oracle-python"
# What the oracle's answers depend on: dependencies, baselines, fixtures with their expectations,
# and the contracts. Directories are frozen file by file.
FROZEN = ("uv.lock", "pyproject.toml", "lean/checkers.lock", "docs/spec/v0-language.md",
          "conformance/baseline-2026-09", "conformance/wire-contract", "ve/wire_contract",
          "conformance/evaluation.json", "conformance/countermodels.json", "conformance/parser.json",
          "conformance/identity.json", "conformance/validation.json", "conformance/closure.json",
          "conformance/labels.json", "conformance/admission.json", "conformance/dependency-order.json",
          "conformance/v0-replay-baseline.json")
# The oracle runs these trees of the commit.
TREES = ("ve", "conformance", "tests", "tools", "examples")


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout


def frozen_files(commit: str) -> dict[str, str]:
    """SHA-256 of every frozen file at `commit`."""
    paths = git("ls-tree", "-r", "--name-only", commit, "--", *FROZEN).decode().split()
    return {path: hashlib.sha256(git("show", f"{commit}:{path}")).hexdigest() for path in sorted(paths)}


def check() -> list[str]:
    manifest = json.loads(MANIFEST.read_text())
    problems = []
    try:
        commit = git("rev-parse", f"refs/tags/{manifest['tag']}^{{commit}}").decode().strip()
    except subprocess.CalledProcessError:
        return [f"tag {manifest['tag']} does not exist"]
    if commit != manifest["commit"]:
        problems.append(f"tag {manifest['tag']} names {commit}, not {manifest['commit']}")
    files = frozen_files(manifest["commit"])
    if files != manifest["files"]:
        changed = sorted(set(files.items()) ^ set(manifest["files"].items()))
        problems.append(f"frozen files differ at the oracle commit: {changed[:5]}")
    lock = hashlib.sha256((ROOT / "uv.lock").read_bytes()).hexdigest()
    if lock != manifest["files"].get("uv.lock"):
        problems.append("this checkout's uv.lock is not the oracle's: its environment cannot run the oracle")
    return problems


def write() -> None:
    commit = git("rev-parse", f"refs/tags/{TAG}^{{commit}}").decode().strip()
    MANIFEST.write_text(json.dumps({"format": "lean-first-oracle@1", "tag": TAG, "commit": commit,
                                    "trees": list(TREES), "files": frozen_files(commit)},
                                   indent=1, sort_keys=True) + "\n")


def run(script: Path) -> int:
    problems = check()
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 2
    manifest = json.loads(MANIFEST.read_text())
    archive = git("archive", manifest["commit"], *manifest["trees"])
    with tempfile.TemporaryDirectory(prefix="ve-lean-first-oracle-") as directory:
        with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
            tree.extractall(directory, filter="data")
        env = {**os.environ, "PYTHONPATH": directory, "VE_AUTHORITY": "python"}
        return subprocess.run([sys.executable, str(script.resolve())], cwd=directory, env=env).returncode


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("run")
    p.add_argument("script", type=Path)
    args = parser.parse_args(argv)
    if args.write:
        write()
    if args.command == "run":
        return run(args.script)
    problems = check()
    print("\n".join(problems) if problems else "PASS: the oracle's tag and frozen files are intact")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
