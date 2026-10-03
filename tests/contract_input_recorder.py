"""A pytest plugin that records every `soft-norms@0` input the tests themselves submit.

Loaded with `-p tests.contract_input_recorder` before any test module is imported, it wraps the ways a
test reaches the pilot: the Python engine (`ve.wire_contract.engine.run` on `soft-norms@0`), the Python
legacy validator (`ve.softnorms.load_soft_document`, and `SoftNormDocument` over a `SoftEnvironment` the
test built from its raw environment), the soft route's runner (`ve.soft_route._run`), and the Lean binaries
`ve_diagnose soft-norms@0` and `ve_soft_norms_route` (through `subprocess.run`; an `admission` case is
recorded as the source its adapter selects). Only calls made from a file under `tests/`, or from the soft conformance module
`conformance/soft_norms.py` that a test runs, count: an input a helper derives internally is not a test's
input. At the end the inputs are written, deduplicated, to `VE_CONTRACT_INPUTS` as a JSON list of
`[test id, environment, norms]`.
"""

import json
import os
from pathlib import Path
import subprocess
import sys

TESTS = Path(__file__).resolve().parent
SOFT_CONFORMANCE = TESTS.parent / "conformance/soft_norms.py"
_RECORDED = {}


def _from_tests():
    caller = Path(sys._getframe(2).f_code.co_filename).resolve()
    return caller.parent == TESTS or caller == SOFT_CONFORMANCE


# The unit whose inputs are recorded (`VE_CONTRACT_UNIT`, the pilot by default; wire-contract-s5.md 7.1).
UNIT = os.environ.get("VE_CONTRACT_UNIT", "soft-norms@0")


def _record(environment, norms, unit="soft-norms@0"):
    if unit != UNIT:
        return
    key = json.dumps([environment, norms], sort_keys=True, default=repr)
    _RECORDED.setdefault(key, os.environ.get("PYTEST_CURRENT_TEST", "?").rsplit(" ", 1)[0])


def _install():
    from ve import soft_route, softnorms, softnorms_contract
    from ve.softnorms_contract import soft_source
    from ve.wire_contract import engine

    original_run, original_load, original_subprocess = engine.run, softnorms.load_soft_document, subprocess.run
    original_route, original_environment = soft_route._run, softnorms.SoftEnvironment.__init__
    original_document = softnorms.SoftNormDocument.__init__
    original_admit = soft_route.admit_soft_document
    original_public = softnorms_contract.public_rejection
    # The raw environment of each `SoftEnvironment` a test built, by the object's id (the object is kept).
    environments = {}

    def environment_init(self, data, *args, **kwargs):
        if _from_tests():
            environments[id(self)] = (self, json.loads(json.dumps(data, default=repr)))
        return original_environment(self, data, *args, **kwargs)

    def document_init(self, env, units, *args, **kwargs):
        if _from_tests() and id(env) in environments and environments[id(env)][0] is env:
            _record(environments[id(env)][1], units)
        return original_document(self, env, units, *args, **kwargs)

    def route(case, *args, **kwargs):
        if _from_tests() and isinstance(case, dict) and case.get("kind") == "soft-elaborate":
            _record(case.get("environment"), case.get("norms"))
        return original_route(case, *args, **kwargs)

    def run(contract, root, *args, **kwargs):
        if (_from_tests() and isinstance(contract, dict) and contract.get("contract") == "soft-norms@0"
                and isinstance(root, dict) and {"environment", "norms"} <= set(root)):
            _record(root["environment"], root["norms"])
        return original_run(contract, root, *args, **kwargs)

    def load_soft_document(environment, norms, *args, **kwargs):
        if _from_tests():
            _record(environment, norms)
        return original_load(environment, norms, *args, **kwargs)

    def admit_soft_document(environment, document, *args, **kwargs):
        if (_from_tests() and not isinstance(environment, softnorms.SoftEnvironment)
                and kwargs.get("soft_document") is None):
            try:
                active = [unit["content"] for unit in document["units"]
                          if unit["kind"] == "norm" and type(unit.get("content")) is dict
                          and "norm" in unit["content"]]
            except (KeyError, TypeError):
                pass
            else:
                _record(environment, active)
        return original_admit(environment, document, *args, **kwargs)

    def public_rejection(environment, norms, error, *args, **kwargs):
        if _from_tests():
            _record(environment, norms)
        return original_public(environment, norms, error, *args, **kwargs)

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
    soft_route._run = route
    soft_route.admit_soft_document = admit_soft_document
    softnorms_contract.public_rejection = public_rejection
    softnorms.SoftEnvironment.__init__, softnorms.SoftNormDocument.__init__ = environment_init, document_init


_install()


def pytest_sessionfinish(session, exitstatus):
    path = os.environ.get("VE_CONTRACT_INPUTS")
    if path:
        rows = [[label, *json.loads(key)] for key, label in sorted(_RECORDED.items(), key=lambda item: item[1])]
        Path(path).write_text(json.dumps(rows))
