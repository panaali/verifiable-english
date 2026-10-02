"""A pytest plugin that records every `soft-norms@0` input the tests themselves submit.

Loaded with `-p tests.contract_input_recorder` before any test module is imported, it wraps the three ways a
test reaches the pilot: the Python engine (`ve.wire_contract.engine.run` on `soft-norms@0`), the Python
legacy validator (`ve.softnorms.load_soft_document`), and the Lean binaries `ve_diagnose soft-norms@0` and
`ve_soft_norms_route` (through `subprocess.run`; an `admission` case is recorded as the source its adapter
selects). Only calls made from a file under `tests/` count: an input a helper derives internally is not a
test's input. At the end the inputs are written, deduplicated, to `VE_CONTRACT_INPUTS` as a JSON list of
`[test id, environment, norms]`.
"""

import json
import os
from pathlib import Path
import subprocess
import sys

TESTS = Path(__file__).resolve().parent
_RECORDED = {}


def _from_tests():
    frame = sys._getframe(2)
    return Path(frame.f_code.co_filename).resolve().parent == TESTS


def _record(environment, norms):
    key = json.dumps([environment, norms], sort_keys=True, default=repr)
    _RECORDED.setdefault(key, os.environ.get("PYTEST_CURRENT_TEST", "?").rsplit(" ", 1)[0])


def _install():
    from ve import softnorms
    from ve.softnorms_contract import soft_source
    from ve.wire_contract import engine

    original_run, original_load, original_subprocess = engine.run, softnorms.load_soft_document, subprocess.run

    def run(contract, root, *args, **kwargs):
        if (_from_tests() and isinstance(contract, dict) and contract.get("contract") == "soft-norms@0"
                and isinstance(root, dict) and {"environment", "norms"} <= set(root)):
            _record(root["environment"], root["norms"])
        return original_run(contract, root, *args, **kwargs)

    def load_soft_document(environment, norms, *args, **kwargs):
        if _from_tests():
            _record(environment, norms)
        return original_load(environment, norms, *args, **kwargs)

    def run_process(command, *args, **kwargs):
        if _from_tests() and isinstance(command, (list, tuple)) and command:
            name = Path(str(command[0])).name
            soft = name == "ve_soft_norms_route" or (name == "ve_diagnose" and "soft-norms@0" in map(str, command))
            if soft and isinstance(kwargs.get("input"), str):
                for case in json.loads(kwargs["input"]):
                    if case.get("kind") == "soft-elaborate":
                        _record(case.get("environment"), case.get("norms"))
                    elif case.get("kind") == "admission":
                        try:
                            source = soft_source(case)
                        except Exception:
                            continue
                        _record(source["environment"], source["norms"])
        return original_subprocess(command, *args, **kwargs)

    engine.run, softnorms.load_soft_document, subprocess.run = run, load_soft_document, run_process


_install()


def pytest_sessionfinish(session, exitstatus):
    path = os.environ.get("VE_CONTRACT_INPUTS")
    if path:
        rows = [[label, *json.loads(key)] for key, label in sorted(_RECORDED.items(), key=lambda item: item[1])]
        Path(path).write_text(json.dumps(rows))
