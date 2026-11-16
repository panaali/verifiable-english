"""A toy use case with the anthropic-rsp adapter's shape, for tests/test_fidmech_worker.py (no Lean, no source).

A mutant sets MUTATED = True. Q1's answer is ALL on a clean, freshly imported module. It turns NONE when the module
is mutated, when RUNS shows the module was not imported fresh (a use-case module global that survived the purge), or
when a probe module outside usecases/ carries a leaked flag (a module global the purge cannot reach).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # as the real run.py does; the worker restores sys.path
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())["cases"]}
MUTATED = False
RUNS = 0
PROBE = "fidmech_leak_probe"


def atoms(case):
    return {("stated", "s", case["id"])}


def run():
    global RUNS
    RUNS += 1
    probe = sys.modules.get(PROBE)
    if MUTATED and probe is not None:
        probe.STATE["leaked"] = True
    stale = RUNS > 1 or (probe is not None and probe.STATE.get("leaked"))
    answer = "NONE" if MUTATED or stale else "ALL"
    items = {"Q1": {"route": "toy", "choices": [{"choice": {}, "holds": answer == "ALL", "rules": ["r-toy"]}]},
             "Q2": {"route": "toy", "undecided": "toy"}}
    return {"items": items, "comparison": [{"id": "Q1", "key": "ALL", "ve": answer, "agree": answer == "ALL"},
                                           {"id": "Q2", "key": "ALL", "ve": "UNDECIDED", "agree": False}]}


def main():
    raise AssertionError("the worker never runs main()")
