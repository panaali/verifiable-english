"""Run one measurement job of this batch on the Mac test runner and decode what it sends back.

  python3 docs/test-architecture/cutoff/measure.py WORKTREE COMMIT OUT --steps '[{"kind": "replay"}]'
      [--overlay PATH ...] [--full-suite]

WORKTREE is a scratch git worktree, checked out at COMMIT (detached) and given this batch's job
(mac_job.py as tests/test_zz_cutoff_job.py, the job file, and each --overlay path copied from this
checkout) as uncommitted files; mac-pytest.sh runs it on the runner, which builds the Lean of that
tree. `--full-suite` instead runs the gate's own collection there (`-m "not live"`, the nightly
tests included) with nothing added. The log and every decoded block go to OUT.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MAC_PYTEST = "/home/seyran/code/manage-agents/mac-pytest.sh"
JOB = "tests/test_zz_cutoff_job.py"


def git(worktree: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(worktree), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def prepare(worktree: Path, commit: str, steps: list | None, overlays: list[str]) -> None:
    if not worktree.exists():
        subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(worktree), commit], check=True)
    git(worktree, "checkout", "-q", "-f", "--detach", commit)
    git(worktree, "clean", "-fdq")
    if steps is None:
        return
    shutil.copy(HERE / "mac_job.py", worktree / JOB)
    (worktree / "cutoff-job.json").write_text(json.dumps({"steps": steps}))
    for path in overlays:
        (worktree / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / path, worktree / path)


def decode(log: Path, out: Path) -> list[str]:
    names, name, chunks = [], None, []
    for line in log.read_text(errors="replace").splitlines():
        if line.startswith("CUTOFF-BEGIN "):
            name, chunks = line.split()[1], []
        elif line.startswith("CUTOFF:") and name:
            chunks.append(line[len("CUTOFF:"):])
        elif line == "CUTOFF-END" and name:
            (out / name).write_bytes(gzip.decompress(base64.b64decode("".join(chunks))))
            names.append(name)
            name = None
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("worktree", type=Path)
    parser.add_argument("commit")
    parser.add_argument("out", type=Path)
    parser.add_argument("--steps", help="the job's steps, as JSON")
    parser.add_argument("--overlay", nargs="*", default=[], help="paths of this checkout to copy in")
    parser.add_argument("--full-suite", action="store_true")
    parser.add_argument("--workers", default="6")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    prepare(args.worktree, args.commit, None if args.full_suite else json.loads(args.steps), args.overlay)
    pytest = (["-o", "addopts=-ra", "-m", "not live", "-q", "-rfE", "-n", args.workers, "tests"] if args.full_suite
              else ["-p", "no:xdist", "-q", "-s", JOB])
    # Standard output and standard error apart: ssh writes them independently, so one file would
    # interleave them inside the job's base64 lines.
    log, errors = args.out / "mac.log", args.out / "mac.err.log"
    with log.open("w") as handle, errors.open("w") as error_handle:
        code = subprocess.run(["zsh", MAC_PYTEST, "--worktree", str(args.worktree), "--", *pytest],
                              stdout=handle, stderr=error_handle,
                              env={**os.environ, "MAC_PYTEST_NOFALLBACK": "1"}).returncode
    names = decode(log, args.out)
    (args.out / "job.json").write_text(json.dumps({"commit": git(args.worktree, "rev-parse", "HEAD"),
                                                   "exit": code, "decoded": names, "full_suite": args.full_suite,
                                                   "steps": None if args.full_suite else json.loads(args.steps)},
                                                  indent=2) + "\n")
    print(f"exit {code}; decoded {names}; log {log}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
