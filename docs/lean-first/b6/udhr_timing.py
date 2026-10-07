"""Base against head on every UDHR translation (batch 6 latency evidence, evidence/udhr-timing.json).

    python3 docs/lean-first/b6/udhr_timing.py BASE_ROOT HEAD_ROOT OUT.json [--python PY] [--repeat-large N]

Each `translation.ve.md` of the `pilot/udhr-*` branches (deduplicated by content) is checked with
`ve document check` in both checkouts, the two processes started together so they share the machine's load.
Wall and CPU time come from /usr/bin/time: the CPU is user + system of the process and of the children it
waited for, which include the Lean service processes it starts and closes. The parsed JSON reports of the
two sides are compared. The large document of 2026-10-03 06:00 runs `--repeat-large` times.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

LARGE = "20261003T0600Z"


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True).stdout


def documents(root):
    """{blob: "branch:path"} of every UDHR translation, first branch first."""
    out = {}
    branches = git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads/pilot/").decode().split()
    for branch in sorted(b for b in branches if b.startswith("pilot/udhr-")):
        listing = git(root, "ls-tree", "-r", "--format=%(objectname) %(path)", branch, "--", "usecases")
        for line in listing.decode().splitlines():
            blob, path = line.split(" ", 1)
            if path.endswith("/translation.ve.md") and blob not in out:
                out[blob] = f"{branch}:{path}"
    return out


def side(python, root, path, scratch):
    env = {k: v for k, v in os.environ.items() if k != "VE_AUTHORITY"}
    env["PYTHONPATH"] = str(root)
    with tempfile.NamedTemporaryFile(dir=scratch, delete=False) as handle:
        timing = Path(handle.name)
    done = subprocess.run(["/usr/bin/time", "-f", "%e %U %S", "-o", str(timing), python, "-m", "ve", "document",
                           "check", str(path)], cwd=root, env=env, capture_output=True)
    wall, user, system = map(float, timing.read_text().split()[-3:])
    timing.unlink()
    try:
        report = json.loads(done.stdout)
    except ValueError:
        report = done.stdout.decode(errors="replace")
    return {"exit": done.returncode, "wall": round(wall, 2), "cpu": round(user + system, 2)}, report


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("base", type=Path)
    parser.add_argument("head", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repeat-large", type=int, default=3)
    args = parser.parse_args(argv)
    rows = []
    with tempfile.TemporaryDirectory() as scratch:
        for blob, name in sorted(documents(args.head).items(), key=lambda item: item[1]):
            path = Path(scratch) / f"{blob}.ve.md"
            path.write_bytes(git(args.head, "cat-file", "blob", blob))
            for run in range(args.repeat_large if LARGE in name else 1):
                with ThreadPoolExecutor(2) as pool:
                    base, head = pool.map(lambda root: side(args.python, root, path, scratch), (args.base, args.head))
                row = {"document": name, "run": run + 1, "bytes": path.stat().st_size, "base": base[0],
                       "head": head[0], "output_equal": base[1] == head[1], "load": round(os.getloadavg()[0], 1)}
                rows.append(row)
                print(json.dumps(row), flush=True)
    args.out.write_text(json.dumps(rows, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
