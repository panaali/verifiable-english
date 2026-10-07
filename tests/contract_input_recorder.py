"""A pytest plugin that records every input of one wire unit that the tests themselves submit.

The unit is `VE_CONTRACT_UNIT` (`soft-norms@0` by default), or each unit of `VE_CONTRACT_UNITS` with
the test files whose inputs count for it. For `norms@0` and `norm-defaults@0`
(wire-contract-s5.md 7.1) it also wraps each unit's `legacy_validation` and `public_rejection`, the two
admission routes, `NormDocument` and `UnspecifiedDocument` built over an environment, and the Lean service
modes `norms` and `norm-defaults` and `diagnose` with a norm unit (through `tests/lean_routes.py`); a source is
recorded for the unit whose domain holds it. For the
pilot:

Loaded with `-p tests.contract_input_recorder` before any test module is imported, it wraps the ways a
test reaches the pilot: the Python engine (`conformance.wire_contract_engine.run` on `soft-norms@0`), the Python
legacy validator (`ve.softnorms.load_soft_document`, and `SoftNormDocument` over a `SoftEnvironment` the
test built from its raw environment), the soft route's runner (`ve.soft_route._run`), and the Lean service
modes `diagnose` (unit `soft-norms@0`) and `soft-norms` (through `tests/lean_routes.py`; an `admission` case
is recorded as the source its adapter selects). Only calls made from a file under `tests/`, or from the soft conformance module
`conformance/soft_norms.py` that a test runs, count: an input a helper derives internally is not a test's
input. At the end the inputs are written, deduplicated, to `VE_CONTRACT_INPUTS` as a JSON list of
`[test id, environment, norms]`.
"""

import itertools
import json
import os
from pathlib import Path
import sys

TESTS = Path(__file__).resolve().parent
SOFT_CONFORMANCE = TESTS.parent / "conformance/soft_norms.py"
# Unit -> input key -> (collection index of the recording test, -1 outside a test; its test id;
# sequence number).
_RECORDED = {}
_CURRENT = [-1]
_SEQUENCE = itertools.count()


def _from_tests(depth=2):
    caller = Path(sys._getframe(depth).f_code.co_filename).resolve()
    return caller.parent == TESTS or caller == SOFT_CONFORMANCE


# The unit whose inputs are recorded (`VE_CONTRACT_UNIT`, the pilot by default; wire-contract-s5.md 7.1),
# or several at once: `VE_CONTRACT_UNITS`, a JSON object from each unit to the test files whose inputs
# count for it (each unit's own `recorded_tests`), so that one run records every unit as its own runs would.
FILES = json.loads(os.environ.get("VE_CONTRACT_UNITS", "null"))
RECORDING = set(FILES) if FILES is not None else {os.environ.get("VE_CONTRACT_UNIT", "soft-norms@0")}
UNIT = next(iter(RECORDING)) if len(RECORDING) == 1 else None


def _record(environment, norms, unit="soft-norms@0"):
    if unit not in RECORDING:
        return
    label = os.environ.get("PYTEST_CURRENT_TEST", "?").rsplit(" ", 1)[0]
    if FILES is not None and label.split("::")[0] not in FILES[unit]:
        return
    key = json.dumps([environment, norms], sort_keys=True, default=repr)
    # The first recording in collection order names the input, under xdist too; the sequence
    # number orders the inputs one test records first as they were recorded.
    recording = (_CURRENT[0], label, next(_SEQUENCE))
    inputs = _RECORDED.setdefault(unit, {})
    if key not in inputs or recording < inputs[key]:
        inputs[key] = recording


def _install():
    from ve import soft_route, softnorms
    from conformance import softnorms_contract, wire_contract_engine as engine
    from conformance.softnorms_contract import soft_source
    from tests import lean_routes

    original_run, original_load = engine.run, softnorms.load_soft_document
    original_service = lean_routes._service_rows
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
        if (_from_tests() and isinstance(contract, dict) and contract.get("contract") in UNITS
                and isinstance(root, dict) and {"environment", "norms"} <= set(root)):
            _record(root["environment"], root["norms"], contract["contract"])
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

    def service_rows(mode, cases, timeout):
        # Frames: _from_tests, this wrapper, the lean_routes function, its caller.
        if _from_tests(3) and isinstance(cases, list):
            _record_norm_cases(mode, cases)
            for case in cases:
                if not isinstance(case, dict) or (mode, case.get("unit")) not in (
                        ("soft-norms", None), ("diagnose", "soft-norms@0")):
                    continue
                if case.get("kind") == "soft-elaborate":
                    _record(case.get("environment"), case.get("norms"))
                elif case.get("kind") == "admission":
                    try:
                        source = soft_source(case)
                    except Exception:
                        continue
                    _record(source["environment"], source["norms"])
        return original_service(mode, cases, timeout)

    engine.run, softnorms.load_soft_document = run, load_soft_document
    lean_routes._service_rows = service_rows
    if RECORDING - {"soft-norms@0"}:
        _install_norms()
    soft_route._run = route
    soft_route.admit_soft_document = admit_soft_document
    softnorms_contract.public_rejection = public_rejection
    softnorms.SoftEnvironment.__init__, softnorms.SoftNormDocument.__init__ = environment_init, document_init


# The units other than the pilot (wire-contract-s5.md 7.1): each with the module of its contract.
UNITS = {"soft-norms@0", "norms@0", "norm-defaults@0"}
# The service modes of the norm routes (formerly `ve_norms_route` and `ve_norm_defaults_route`).
NORM_ROUTES = {"norms": "norms@0", "norm-defaults": "norm-defaults@0"}


def _norm_unit(environment):
    """The unit a norm source belongs to: `norm-defaults@0` when its environment lists that profile."""
    profiles = environment.get("profiles") if isinstance(environment, dict) else None
    return "norm-defaults@0" if isinstance(profiles, list) and "norm-defaults@0" in profiles else "norms@0"


def _record_norm(environment, norms):
    """Record a norm source for its unit, when it is in that unit's domain (2.2)."""
    from ve.norms_contract import in_domain
    environment = environment.to_dict() if hasattr(environment, "to_dict") else environment
    norms = [unit.to_dict() if hasattr(unit, "to_dict") else unit for unit in norms] \
        if isinstance(norms, (list, tuple)) else norms
    environment, norms = json.loads(json.dumps([environment, norms], default=repr))
    unit = _norm_unit(environment)
    if in_domain(environment, norms, defaults=unit == "norm-defaults@0"):
        _record(environment, norms, unit)


def _record_norm_cases(mode, cases):
    """The cases a test hands to a norm route's service mode, or to `diagnose` with a norm unit."""
    from ve.norms_contract import active_norms
    for case in cases:
        if not isinstance(case, dict) or not (mode in NORM_ROUTES or (
                mode == "diagnose" and case.get("unit") in ("norms@0", "norm-defaults@0"))):
            continue
        kind = case.get("kind")
        if kind == "admission":
            _record_norm(case.get("environment"), active_norms(case.get("document")))
        elif isinstance(kind, str) and (kind.startswith("norms-") or kind.startswith("norm-defaults-")):
            _record_norm(case.get("environment"), case.get("norms"))


def _install_norms():
    """The ways a test reaches `norms@0` and `norm-defaults@0`: each unit's `legacy_validation` and
    `public_rejection`, the admission routes, and `NormDocument` and `UnspecifiedDocument` built over an
    environment (wire-contract-s5.md 7.1). Only calls from a test file count."""
    import importlib
    from ve import norm_admission, norm_defaults, norm_defaults_route, norms
    from conformance import frozen_norm_defaults
    for module_name, unit in (("ve.norms_contract", "norms@0"), ("ve.norm_defaults_contract", "norm-defaults@0")):
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue
        for function in ("legacy_validation", "public_rejection"):
            original = getattr(module, function, None)
            if original is None:
                continue
            def wrapper(environment, norms_, *args, original=original, **kwargs):
                if _from_tests():
                    _record_norm(environment, norms_)
                return original(environment, norms_, *args, **kwargs)
            setattr(module, function, wrapper)
    for module, function in ((norm_admission, "admit_norm_document"),
                             (norm_defaults_route, "admit_norm_defaults_document")):
        original = getattr(module, function)
        def admit(environment, document, *args, original=original, **kwargs):
            if _from_tests():
                from ve.norms_contract import active_norms
                _record_norm(environment, active_norms(document))
            return original(environment, document, *args, **kwargs)
        setattr(module, function, admit)
    for cls in (norms.NormDocument, norm_defaults.UnspecifiedDocument,
                frozen_norm_defaults.UnspecifiedDocument):
        original = cls.__init__
        def init(self, env, units, *args, original=original, **kwargs):
            if _from_tests() and hasattr(env, "to_dict"):
                try:
                    _record_norm(env, list(units))
                except Exception:
                    pass
            return original(self, env, units, *args, **kwargs)
        cls.__init__ = init


_install()


def pytest_collection_finish(session):
    _INDEX.update((item.nodeid, index) for index, item in enumerate(session.items))


_INDEX = {}


def pytest_runtest_protocol(item, nextitem):
    _CURRENT[0] = _INDEX.get(item.nodeid, -1)


def pytest_sessionfinish(session, exitstatus):
    """Write the inputs: one unit's as a list, several as an object from unit to list. Under
    xdist each worker writes its own `<path>.<worker>` (it ends before the controller does) and
    the controller merges them: an input recorded by several tests keeps the first test in
    collection order, and the rows are in the order a serial run writes them."""
    path = os.environ.get("VE_CONTRACT_INPUTS")
    if not path:
        return
    # Not PYTEST_XDIST_WORKER: a controller started from inside an xdist worker inherits it.
    worker = getattr(session.config, "workerinput", {}).get("workerid")
    if worker:
        Path(f"{path}.{worker}").write_text(json.dumps(_RECORDED))
        return
    recorded = {unit: dict(_RECORDED.get(unit, {})) for unit in sorted(RECORDING)}
    for part in sorted(Path(path).parent.glob(f"{Path(path).name}.gw*")):
        for unit, inputs in json.loads(part.read_text()).items():
            for key, recording in inputs.items():
                recording = tuple(recording)
                if key not in recorded[unit] or recording < recorded[unit][key]:
                    recorded[unit][key] = recording
        part.unlink()
    rows = {unit: [[label, *json.loads(key)] for key, (_, label, _) in
                   sorted(inputs.items(), key=lambda item: (item[1][1], item[1][0], item[1][2]))]
            for unit, inputs in recorded.items()}
    Path(path).write_text(json.dumps(rows[UNIT] if FILES is None else rows))
