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
    (1, "ve/wire.py", "tests/test_conformance.py::test_jcs_utf16_key_order_and_string_escaping_golden",
     "def canonical_json(value) -> bytes:\n    validate_json(value)\n",
     "def canonical_json(value) -> bytes:\n    validate_json(value)\n    return b'{}'  # injected layer-1 fault\n"),
    (2, "ve/profiles.py", "tests/test_profiles.py::test_route_families_and_identity",
     "    checker = [p for p in profiles if p in ",
     "    return 'invalid'  # injected layer-2 fault\n    checker = [p for p in profiles if p in "),
    (3, "ve/grammar.py", "tests/test_grammar.py::test_all_dialects_are_nonempty_and_closed_vocabulary",
     "    if not isinstance(env, Environment):\n",
     "    return ''  # injected layer-3 fault\n    if not isinstance(env, Environment):\n"),
    (4, "ve/adapters/gatekeeper.py", "tests/test_gatekeeper_adapter.py::test_gatekeeper_exemption_uses_verified_globs",
     "    if records is None:\n",
     "    return Exemption(False, ())  # injected layer-4 fault\n    if records is None:\n"),
    (5, "ve_experiments/t1c/materials.py", "tests/test_t1c.py::test_generator_ground_truth",
     "    adjacency = defaultdict(list)\n",
     "    return {'reachable': False, 'path': [], 'visited': []}  # injected layer-5 fault\n    adjacency = defaultdict(list)\n"),
)
FAILURE = re.compile(r"^(?:FAILED|ERROR) (tests/\S+)", re.MULTILINE)


def pytest_run(files: list[str], log: Path, *, workers: int = 4,
               stop_early: bool = False) -> tuple[int, set[str], float]:
    env = dict(os.environ)
    env["UV_CACHE_DIR"] = "/tmp/ve-layers-uv-cache"
    env["VE_LEAN_PREBUILT"] = "1"
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    command = ["uv", "run", "--frozen", "--group", "dev", "--with", "pytest-xdist",
               "python", "-m", "pytest", "-n", str(min(workers, len(files))),
               "--dist=loadfile", "-q", *(["-x"] if stop_early else []), *files]
    start = time.monotonic()
    with log.open("w") as output:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=output,
                                stderr=subprocess.STDOUT, check=False, timeout=3600)
    body = log.read_text()
    return result.returncode, set(FAILURE.findall(body)), round(time.monotonic() - start, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/layer-mutation-results.json")
    parser.add_argument("--layers", nargs="+", type=int, choices=range(1, 6),
                        help="run only these layers; preserve other existing rows")
    parser.add_argument("--workers", type=int, default=4,
                        help="maximum pytest workers for each exclusion run")
    parser.add_argument("--chunk-size", type=int, default=11,
                        help="maximum excluded test files per pytest invocation")
    args = parser.parse_args()
    if args.workers < 1 or args.chunk_size < 1:
        parser.error("--workers and --chunk-size must be positive")
    output = ROOT / args.output
    results = json.loads(output.read_text()) if output.exists() else []
    logs = Path("/tmp/ve-layer-mutations") / f"run-{time.time_ns()}"
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
        if witness.split("::", 1)[0] not in plan["selected"]:
            raise RuntimeError(f"witness {witness} not selected")
        excluded = sorted({p.relative_to(ROOT).as_posix() for p in TESTS}
                          - set(plan["selected"]))
        print(f"layer {layer} {relative}: {len(plan['selected'])}/{plan['full_count']} files",
              flush=True)
        try:
            path.write_text(original.replace(anchor, replacement, 1))
            witness_log = logs / f"layer{layer}-witness.log"
            witness_code, witness_fail, witness_seconds = pytest_run([witness], witness_log)
            excluded_chunks = []
            for index in range(0, len(excluded), args.chunk_size):
                group = excluded[index:index + args.chunk_size]
                excluded_log = logs / f"layer{layer}-excluded-{index // args.chunk_size + 1}.log"
                code, failures, seconds = pytest_run(
                    group, excluded_log, workers=args.workers, stop_early=True)
                excluded_chunks.append({"files": group, "exit": code,
                                        "failures": sorted(failures), "seconds": seconds})
                print(f"  excluded chunk {index // args.chunk_size + 1}: "
                      f"{len(group)} files, exit {code}", flush=True)
                if code:
                    break
        finally:
            path.write_text(original)
        excluded_code = max((item["exit"] for item in excluded_chunks), default=0)
        excluded_fail = {failure for item in excluded_chunks for failure in item["failures"]}
        excluded_seconds = round(sum(item["seconds"] for item in excluded_chunks), 1)
        row = {"layer": layer, "source": relative,
               "selected_files": plan["selected_count"], "full_files": plan["full_count"],
               "witness": witness, "witness_exit": witness_code,
               "witness_failures": sorted(witness_fail), "witness_seconds": witness_seconds,
               "excluded_files": len(excluded), "excluded_exit": excluded_code,
               "excluded_failures": sorted(excluded_fail), "excluded_seconds": excluded_seconds,
               "excluded_chunks": excluded_chunks}
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
