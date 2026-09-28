"""Check full-suite failures against selected files for one fault per layer.

This temporarily edits five *clean* source files, restoring each in a finally
block. Run only in a worktree without concurrent tests or source edits. The
faults never invoke a model service. Summary JSON goes to the path supplied by
--output; raw pytest logs go to /tmp/ve-layer-mutations.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from select_tests import ROOT, select

CASES = (
    (1, "ve/wire.py", "def canonical_json(value) -> bytes:\n    validate_json(value)\n",
     "def canonical_json(value) -> bytes:\n    validate_json(value)\n    return b'{}'  # injected layer-1 fault\n"),
    (2, "ve/profiles.py", "    checker = [p for p in profiles if p in ",
     "    return 'invalid'  # injected layer-2 fault\n    checker = [p for p in profiles if p in "),
    (3, "ve/grammar.py", "    if not isinstance(env, Environment):\n",
     "    return ''  # injected layer-3 fault\n    if not isinstance(env, Environment):\n"),
    (4, "ve/adapters/gatekeeper.py", "    if records is None:\n",
     "    return Exemption(False, ())  # injected layer-4 fault\n    if records is None:\n"),
    (5, "ve_experiments/t1c/materials.py", "    adjacency = defaultdict(list)\n",
     "    return {'reachable': False, 'path': [], 'visited': []}  # injected layer-5 fault\n    adjacency = defaultdict(list)\n"),
)
FAILURE = re.compile(r"^(?:FAILED|ERROR) (tests/[^ ]+)", re.MULTILINE)


def pytest_run(files: list[str], log: Path) -> tuple[int, set[str], float]:
    env = dict(os.environ)
    env["UV_CACHE_DIR"] = "/tmp/ve-layers-uv-cache"
    env["VE_LEAN_PREBUILT"] = "1"
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    command = ["uv", "run", "--frozen", "--group", "dev", "--with", "pytest-xdist",
               "python", "-m", "pytest", "-n", "8", "-q", *files]
    start = time.monotonic()
    with log.open("w") as output:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=output,
                                stderr=subprocess.STDOUT, check=False)
    body = log.read_text()
    return result.returncode, set(FAILURE.findall(body)), round(time.monotonic() - start, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/layer-mutation-results.json")
    args = parser.parse_args()
    results = []
    logs = Path("/tmp/ve-layer-mutations")
    logs.mkdir(exist_ok=True)
    for layer, relative, anchor, replacement in CASES:
        path = ROOT / relative
        original = path.read_text()
        if original.count(anchor) != 1:
            raise RuntimeError(f"mutation anchor missing or ambiguous in {relative}")
        baseline = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=ROOT,
                                  text=True, capture_output=True, check=True).stdout
        if original != baseline:
            raise RuntimeError(f"refusing to mutate already edited source: {relative}")
        plan = select([relative])
        print(f"layer {layer} {relative}: {len(plan['selected'])}/{plan['full_count']} files",
              flush=True)
        try:
            path.write_text(original.replace(anchor, replacement, 1))
            full_log = logs / f"layer{layer}-full.log"
            full_code, full_fail, full_seconds = pytest_run([], full_log)
        finally:
            path.write_text(original)
        failed_files = {test.split("::", 1)[0] for test in full_fail}
        missed = sorted(failed_files - set(plan["selected"]))
        row = {"layer": layer, "source": relative,
               "selected_files": plan["selected_count"], "full_files": plan["full_count"],
               "full_exit": full_code, "full_failures": sorted(full_fail),
               "missed": missed, "full_seconds": full_seconds}
        results.append(row)
        (ROOT / args.output).write_text(json.dumps(results, indent=2) + "\n")
        print(f"  failed tests: full {len(full_fail)}, "
              f"missed {len(row['missed'])}", flush=True)
        if full_code == 0 or not full_fail or row["missed"]:
            print(f"mutation comparison failed; inspect {logs}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
