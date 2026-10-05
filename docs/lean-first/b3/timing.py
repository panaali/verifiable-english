"""Lean-first batch 3 timing: the readings route before and after the deletion of Python's regeneration.

    PYTHONPATH=<checkout> python docs/lean-first/b3/timing.py --corpus <readings corpus> [--pilots N]

Run once per side, each side importing its own checkout's `ve` (the corpus is `tools/lean_first_diff.py`'s
readings corpus, the same file for both). It times `ve.readings_route.validate` on every corpus document, one after
another, and `ve document check` on the constitution pilot's S1 documents (every `readings/s1.ve.md` of a
`pilot/cc-*` branch), `N` times each. CPU is this process's own (Python) and its children's (Lean, Rust), from
`resource.getrusage`.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def usage():
    self, children = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.perf_counter(), self.ru_utime + self.ru_stime, children.ru_utime + children.ru_stime


def spent(start):
    end = usage()
    return {"wall": round(end[0] - start[0], 2), "python_cpu": round(end[1] - start[1], 2),
            "children_cpu": round(end[2] - start[2], 2)}


def corpus(path):
    from ve.errors import CheckerUnavailable, VEError
    from ve.readings_route import validate
    outcomes = {"ok": 0, "rejected": 0, "unavailable": 0}
    start = usage()
    for case in json.loads(Path(path).read_text()):
        document = case["document"]
        units = [{"id": u["id"], "kind": u.get("kind"), **({"content": u["content"]} if "content" in u else {})}
                 for u in document["units"]]
        try:
            validate(case["environment"], units, document["reading_sets"])
            outcomes["ok"] += 1
        except CheckerUnavailable:
            outcomes["unavailable"] += 1
        except VEError:
            outcomes["rejected"] += 1
    return {**spent(start), **outcomes}


def pilots(repeat):
    root = Path(__file__).resolve().parents[3]
    git = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True).stdout  # noqa: E731
    branches = git("for-each-ref", "--format=%(refname:short)", "refs/heads/pilot/cc-*").decode().split()
    blobs = {}
    for branch in branches:
        for line in git("ls-tree", "-r", "--format=%(objectname) %(path)", branch, "--", "usecases").decode().splitlines():
            blob, path = line.split(" ", 1)
            if path.endswith("readings/s1.ve.md"):
                blobs.setdefault(blob, f"{branch}:{path}")
    import ve
    checkout = Path(ve.__file__).resolve().parents[1]
    out = {}
    env = {**os.environ}
    env.pop("VE_AUTHORITY", None)
    with tempfile.TemporaryDirectory() as tmp:
        for blob, name in sorted(blobs.items(), key=lambda item: item[1]):
            path = Path(tmp) / f"{blob}.ve.md"
            path.write_bytes(git("cat-file", "blob", blob))
            runs = []
            for _ in range(repeat):
                start = usage()
                done = subprocess.run([sys.executable, "-m", "ve", "document", "check", str(path)], env=env,
                                      cwd=checkout, capture_output=True)
                runs.append({**spent(start), "exit": done.returncode})
            out[name] = runs
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--pilots", type=int, default=0)
    args = parser.parse_args(argv)
    import ve
    result = {"ve": str(Path(ve.__file__).resolve().parent), "corpus": corpus(args.corpus)}
    if args.pilots:
        result["pilots"] = pilots(args.pilots)
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
