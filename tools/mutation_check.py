"""Prove excluded tests stay green for one detectable fault per layer.

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

from select_tests import ROOT, TESTS, select

CASES = (
    (1, "ve/wire.py", "tests/test_conformance.py",
     "def canonical_json(value) -> bytes:\n    validate_json(value)\n",
     "def canonical_json(value) -> bytes:\n    validate_json(value)\n    return b'{}'  # injected layer-1 fault\n"),
    (2, "ve/profiles.py", "tests/test_profiles.py",
     "    checker = [p for p in profiles if p in ",
     "    return 'invalid'  # injected layer-2 fault\n    checker = [p for p in profiles if p in "),
    (3, "ve/grammar.py", "tests/test_grammar.py",
     "    if not isinstance(env, Environment):\n",
     "    return ''  # injected layer-3 fault\n    if not isinstance(env, Environment):\n"),
    (4, "ve/adapters/gatekeeper.py", "tests/test_gatekeeper_adapter.py",
     "    if records is None:\n",
     "    return Exemption(False, ())  # injected layer-4 fault\n    if records is None:\n"),
    (5, "ve_experiments/t1c/materials.py", "tests/test_t1c.py",
     "    adjacency = defaultdict(list)\n",
     "    return {'reachable': False, 'path': [], 'visited': []}  # injected layer-5 fault\n    adjacency = defaultdict(list)\n"),
)
FAILURE = re.compile(r"^(?:FAILED|ERROR) (tests/[^ ]+)", re.MULTILINE)


def pytest_run(files: list[str], log: Path) -> tuple[int, set[str], float]:
    env = dict(os.environ)
    env["UV_CACHE_DIR"] = "/tmp/ve-layers-uv-cache"
    env["VE_LEAN_PREBUILT"] = "1"
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    command = ["uv", "run", "--frozen", "--group", "dev", "--with", "pytest-xdist",
               "python", "-m", "pytest", "-n", str(min(8, len(files))),
               "--dist=loadfile", "-q", *files]
    start = time.monotonic()
    with log.open("w") as output:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=output,
                                stderr=subprocess.STDOUT, check=False)
    body = log.read_text()
    return result.returncode, set(FAILURE.findall(body)), round(time.monotonic() - start, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/layer-mutation-results.json")
    parser.add_argument("--layers", nargs="+", type=int, choices=range(1, 6),
                        help="run only these layers; preserve other existing rows")
    args = parser.parse_args()
    output = ROOT / args.output
    results = json.loads(output.read_text()) if output.exists() else []
    logs = Path("/tmp/ve-layer-mutations")
    logs.mkdir(exist_ok=True)
    for layer, relative, witness, anchor, replacement in CASES:
        if args.layers and layer not in args.layers:
            continue
        path = ROOT / relative
        original = path.read_text()
        if original.count(anchor) != 1:
            raise RuntimeError(f"mutation anchor missing or ambiguous in {relative}")
        baseline = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=ROOT,
                                  text=True, capture_output=True, check=True).stdout
        if original != baseline:
            raise RuntimeError(f"refusing to mutate already edited source: {relative}")
        plan = select([relative])
        if witness not in plan["selected"]:
            raise RuntimeError(f"witness {witness} not selected")
        excluded = sorted({p.relative_to(ROOT).as_posix() for p in TESTS}
                          - set(plan["selected"]))
        print(f"layer {layer} {relative}: {len(plan['selected'])}/{plan['full_count']} files",
              flush=True)
        try:
            path.write_text(original.replace(anchor, replacement, 1))
            witness_log = logs / f"layer{layer}-witness.log"
            witness_code, witness_fail, witness_seconds = pytest_run([witness], witness_log)
            excluded_log = logs / f"layer{layer}-excluded.log"
            if excluded:
                excluded_code, excluded_fail, excluded_seconds = pytest_run(excluded, excluded_log)
            else:
                excluded_code, excluded_fail, excluded_seconds = 0, set(), 0.0
        finally:
            path.write_text(original)
        row = {"layer": layer, "source": relative,
               "selected_files": plan["selected_count"], "full_files": plan["full_count"],
               "witness": witness, "witness_exit": witness_code,
               "witness_failures": sorted(witness_fail), "witness_seconds": witness_seconds,
               "excluded_files": len(excluded), "excluded_exit": excluded_code,
               "excluded_failures": sorted(excluded_fail), "excluded_seconds": excluded_seconds}
        results = sorted((old for old in results if old["layer"] != layer),
                         key=lambda old: old["layer"]) + [row]
        results.sort(key=lambda old: old["layer"])
        output.write_text(json.dumps(results, indent=2) + "\n")
        print(f"  witness failures {len(witness_fail)}; excluded files {len(excluded)}, "
              f"excluded failures {len(excluded_fail)}", flush=True)
        if witness_code == 0 or not witness_fail or excluded_code or excluded_fail:
            print(f"mutation comparison failed; inspect {logs}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
