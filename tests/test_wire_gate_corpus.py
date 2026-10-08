"""The soft-norms gate's corpus condition (wire loop final, wire2 loop): the gate replays every `soft-norms@0`
input that the contract and soft tests submit, every soft conformance fixture, and every source the soft
conformance module `conformance/soft_norms.py` builds.

The contract tests (`tests/test_*contract*`, which include `tests/test_wire_contract*`) and the soft tests
(`tests/test_soft*`, which run the conformance module's comparison) are run again under
`tests.contract_input_recorder`, which records each input they, or the conformance module, hand to either
engine or either legacy validator; an input missing from `gate_cases` fails the test, so a new test input that
the gate does not replay is caught when it is added. Independently, every source-building function of the
conformance module is called and each source it yields must be in the corpus, so a new generator is caught
even before a test runs it. This file's name matches neither glob, so it does not record itself.
"""

from functools import lru_cache
import importlib
import inspect
import json
import os
from pathlib import Path
import subprocess

import pytest

from conformance import soft_norms
from conformance.soft_norms import (RUST_FIXTURES, combined_invalid_soft_blocks, generated_invalid_soft_blocks,
                                    generated_invalid_soft_rules, rejected_sources, soft3_reproducers)
from conformance.wire_contract_gate import (EXAMPLES, PILOT, RECORDED_TESTS, TEST_INPUTS, gate_cases,
                                            record_all_test_inputs, source_key, unit_of)
from subprocesses import HANG_TIMEOUT
from tests.test_soft_norms_conformance import fixtures
from tools import nested_pytest
from tests.test_wire_contract_soft_lean import fixture_sources
from conformance.wire_contract_engine import load

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "conformance/wire-contract/soft-norms@0-golden.json"
# The test files that submit `soft-norms@0` inputs; each must record at least one.
SUBMITTING = {"test_softnorms_contract.py", "test_softnorms_public_contract.py",
              "test_wire_contract_faults.py", "test_wire_contract_precondition.py",
              "test_wire_contract_soft_lean.py", "test_wire_contract_three_way.py",
              "test_soft_norms_conformance.py", "test_soft_norms_lean.py", "test_soft_review_regressions.py"}
# The conformance module's functions that build no source of their own: the comparisons that run the
# validators on the sources the other functions build, and the fault mutations `multi_fault_cases` applies.
NOT_SOURCES = {"compare_generated", "compare_near_limit", "compare_rejected", "main", "multi_faults", "rust_fixture_rows",
               "smallest_queries"}


@lru_cache(maxsize=1)
def corpus():
    return frozenset(source_key(case[2], case[3]) for case in gate_cases(load("soft-norms@0")))


@pytest.fixture(scope="module")
def recorded_inputs(tmp_path_factory):
    """Every unit's recorded test inputs, from one run of the union of their recorded test files
    (each unit records only its own files' inputs, as `record_test_inputs` does for one unit)."""
    output = tmp_path_factory.mktemp("recorded") / "inputs.json"
    result = record_all_test_inputs(output, (PILOT, *UNITS))
    # A skipped or failed test may have submitted fewer inputs than it does when it runs.
    assert result.returncode == 0 and " skipped" not in result.stdout, result.stdout[-4000:] + result.stderr[-4000:]
    return json.loads(output.read_text())


def test_gate_corpus_holds_every_test_input_of_every_unit(recorded_inputs):
    """One recording run for the pilot and the units: the checks below, per unit."""
    assert set(recorded_inputs) == {PILOT, *UNITS}
    check_pilot_inputs(recorded_inputs[PILOT])
    for unit in UNITS:
        check_unit_inputs(unit, recorded_inputs[unit])


def test_one_run_records_each_unit_as_its_own_run_does(tmp_path):
    """The joint recording keeps each unit to its own test files: a file of one unit only adds
    nothing to another unit's inputs, though it submits some (the s5 admission tests submit
    norm sources)."""
    sample = ["tests/test_softnorms_public_contract.py", "tests/test_wire_contract_s5_admission.py"]
    output = tmp_path / "inputs.json"
    files = {unit: sample if unit == PILOT else [] for unit in (PILOT, *UNITS)}
    environment = {**os.environ, "VE_CONTRACT_INPUTS": str(output), "VE_CONTRACT_UNITS": json.dumps(files),
                   "VE_NATIVE_PREBUILT": "1", "PYTHONPATH": str(ROOT)}

    def record(env):
        result = subprocess.run(nested_pytest.command(["-q", "-p", "tests.contract_input_recorder",
                                                       "-p", "no:cacheprovider", "-o", "addopts=", "-m", "not live",
                                                       *sample]),
                                cwd=ROOT, env=nested_pytest.environment(env), capture_output=True, text=True,
                                timeout=HANG_TIMEOUT)
        assert result.returncode == 0, result.stdout[-4000:]
    record(environment)
    joint = json.loads(output.read_text())
    alone = tmp_path / "alone.json"
    environment = {key: value for key, value in environment.items() if key != "VE_CONTRACT_UNITS"}
    record({**environment, "VE_CONTRACT_INPUTS": str(alone)})
    assert joint[PILOT] == json.loads(alone.read_text()) and joint[PILOT]
    assert joint["norms@0"] == joint["norm-defaults@0"] == []
    # The same files, counted for the norm units too, do record norm sources.
    files = {unit: sample for unit in (PILOT, *UNITS)}
    record({**environment, "VE_CONTRACT_UNITS": json.dumps(files)})
    assert json.loads(output.read_text())["norms@0"]


def check_pilot_inputs(recorded):
    """A missing input is a test input no source of the corpus builds: `python -m
    conformance.wire_contract_gate --record-test-inputs` records it into `TEST_INPUTS`, which the gate replays
    (Lean reads none that carries a `null`, which only the in-process API can)."""
    files = {path for pattern in RECORDED_TESTS for path in ROOT.glob(pattern)}
    assert set(ROOT.glob("tests/test_wire_contract*")) | set(ROOT.glob("tests/test_softnorms*")) <= files
    assert Path(__file__) not in files
    assert SUBMITTING <= {Path(label.split("::")[0]).name for label, _, _ in recorded}
    # The conformance module's comparison ran under the recorder: every source it submits was recorded.
    submitted = {source_key(raw, norms) for label, raw, norms in recorded}
    assert {source_key(raw, norms) for _, raw, norms in soft_norms.exercised_sources()} <= submitted
    gate = corpus()
    missing = sorted({label for label, raw, norms in recorded if source_key(raw, norms) not in gate})
    assert missing == []
    # The stored inputs are each recorded by a test today and built by no other source of the corpus.
    stored = json.loads(TEST_INPUTS.read_text())
    others = {source_key(case[2], case[3]) for case in gate_cases(load("soft-norms@0"), recorded=False)}
    assert {source_key(raw, norms) for _, raw, norms in stored} <= submitted - others


def _sources(row):
    """The (environment, norms) pairs in one row a source-building function yields."""
    row = row if isinstance(row, tuple) else (row,)
    return [(raw, norms) for raw, norms in zip(row, row[1:])
            if isinstance(raw, dict) and "vocabulary" in raw and isinstance(norms, list)]


def test_gate_corpus_holds_every_source_of_the_soft_conformance_module():
    """Wire2 loop (B): 56 sources of `expected_rejections()`, 24 of `generated_invalid_exceptions()` and 205
    of `near_limit_cases()` were missing. Every public function of `conformance/soft_norms.py` is called (one
    that needs arguments or builds no source must be named here, so a new generator cannot be skipped) and
    every source it yields must be in the gate's corpus, with the seeded trees `main` examines."""
    functions = {name: value for name, value in vars(soft_norms).items()
                 if inspect.isfunction(value) and value.__module__ == soft_norms.__name__ and not name.startswith("_")}
    assert NOT_SOURCES | {"generated"} <= set(functions)
    gate = corpus()
    missing, built = {}, {}
    for name, function in sorted(functions.items()):
        if name in NOT_SOURCES or name == "generated":
            continue
        required = [p for p in inspect.signature(function).parameters.values() if p.default is p.empty]
        assert not required, f"{name} needs arguments: call it here, or name it in NOT_SOURCES"
        result = function()
        # A function that returns one source (`multi_fault_base`) returns its pair, not rows.
        sources = [source for row in ([result] if isinstance(result, tuple) else result) for source in _sources(row)]
        built[name] = len(sources)
        missing[name] = [i for i, (raw, norms) in enumerate(sources) if source_key(raw, norms) not in gate]
    assert all(built.values()), built
    # `generated(seed)`, at every seed `main` examines.
    seeds = [seed for seed, _, _, _ in soft_norms.generated_trees()]
    assert seeds == list(range(len(seeds))) and len(seeds) >= soft_norms.TREES
    missing["generated"] = [seed for seed in seeds if source_key(*soft_norms.generated(seed)) not in gate]
    assert missing == {name: [] for name in missing}
    # The finding's three generators, by count.
    assert built["expected_rejections"] == len(soft_norms.expected_rejections()) > 3000
    assert built["generated_invalid_exceptions"] == 24 and built["near_limit_cases"] == 227


def test_gate_corpus_holds_every_soft_conformance_fixture():
    """The fixtures P1 to P17 of 8.3 (one source per golden record), the acceptance fixtures of soft-norms.md
    10, the Rust fixtures' sources, the contract's examples and the soft corpora of `conformance/soft_norms.py`."""
    golden = json.loads(GOLDEN.read_text())["fixtures"]
    pilot = fixture_sources()
    assert len(pilot) == len(golden)
    sources = {"pilot": pilot, "acceptance": [row[1:3] for row in fixtures()],
               "rust": [(row["source"]["environment"], row["source"]["norms"])
                        for row in json.loads(RUST_FIXTURES.read_text())],
               "examples": [(value["environment"], value["norms"])
                            for value in (json.loads(path.read_text()) for path in sorted(EXAMPLES.glob("*.json")))],
               "rejected": rejected_sources(), "blocks": generated_invalid_soft_blocks(),
               "combined": combined_invalid_soft_blocks(), "rules": generated_invalid_soft_rules(),
               "soft3": [row[1:3] for row in soft3_reproducers()]}
    gate = corpus()
    missing = {name: [i for i, (raw, norms) in enumerate(rows) if source_key(raw, norms) not in gate]
               for name, rows in sources.items()}
    assert all(rows for rows in sources.values())
    assert missing == {name: [] for name in sources}


# wire-contract-s5.md 8.7: the same three tests for each unit after the pilot. Each unit's fault catalogue module
# names its recorded test files (`RECORDED_TESTS`), builds its conformance scripts' sources
# (`conformance_sources`) and its examples; its test module holds its fixtures (`fixture_sources`).
UNITS = ("norms@0", "norm-defaults@0")
# Astra review B: the recorded files omitted the S5 contract tests, whose D8, D12 and D13 sources were not in
# the corpus. Each submitting file below must be the first to record at least one input of the unit (the
# recorder keeps a source's first test id, so a file whose sources another file submits first is not named;
# `tests/test_wire_contract_s5_admission.py` is such a file, recorded through the globs below).
UNIT_SUBMITTING = {"norms@0": {"test_norms_contract.py", "test_norm_admission.py", "test_norms.py",
                               "test_norms_three_way.py", "test_wire_contract_s5_lean.py"},
                   "norm-defaults@0": {"test_norm_defaults_contract.py", "test_norm_defaults.py",
                                       "test_norm_defaults_three_way.py", "test_norm_defaults_differential.py",
                                       "test_wire_contract_s5_lean.py"}}
# wire-contract-s5.md 7.1: the globs every unit after the pilot records.
UNIT_GLOBS = ("tests/test_norm*", "tests/test_*contract*")
UNIT_TESTS = {"norms@0": "tests.test_norms_contract", "norm-defaults@0": "tests.test_norm_defaults_contract"}


@lru_cache(maxsize=None)
def unit_corpus(unit):
    return frozenset(source_key(case[2], case[3]) for case in gate_cases(load(unit)))


def check_unit_inputs(unit, recorded):
    """A missing input is a test input no source of the unit's corpus builds: `python -m
    conformance.wire_contract_gate --unit <unit> --record-test-inputs` records it into the unit's test inputs."""
    files = {path for pattern in unit_of(unit).recorded_tests for path in ROOT.glob(pattern)}
    assert {path for pattern in UNIT_GLOBS for path in ROOT.glob(pattern)} <= files
    assert {ROOT / "tests" / name for name in UNIT_SUBMITTING[unit]} | {
        ROOT / "tests/test_wire_contract_s5_admission.py"} <= files
    assert Path(__file__) not in files
    assert UNIT_SUBMITTING[unit] <= {Path(label.split("::")[0]).name for label, _, _ in recorded}
    submitted = {source_key(raw, norms) for label, raw, norms in recorded}
    gate = unit_corpus(unit)
    assert sorted({label for label, raw, norms in recorded if source_key(raw, norms) not in gate}) == []
    stored = json.loads(unit_of(unit).test_inputs.read_text())
    others = {source_key(case[2], case[3]) for case in gate_cases(load(unit), recorded=False)}
    assert {source_key(raw, norms) for _, raw, norms in stored} <= submitted - others


@pytest.mark.parametrize("unit", UNITS)
def test_unit_gate_corpus_holds_every_source_of_its_conformance_scripts(unit):
    sources = unit_of(unit).module.conformance_sources()
    gate = unit_corpus(unit)
    assert sources and [label for label, raw, norms in sources if source_key(raw, norms) not in gate] == []


@pytest.mark.parametrize("unit", UNITS)
def test_unit_gate_corpus_holds_every_fixture(unit):
    """The fixtures of the unit's statement spec that its tests build (its contract test's and the Lean
    fixture test's, which builds D8, D12 and D13 its own way), and its examples."""
    from tests.test_wire_contract_s5_lean import fixture_sources as lean_fixture_sources
    module = unit_of(unit).module
    sources = (importlib.import_module(UNIT_TESTS[unit]).fixture_sources() + lean_fixture_sources(unit)
               + module.example_sources())
    gate = unit_corpus(unit)
    assert len(module.example_sources()) >= 2
    assert [label for label, raw, norms in sources if source_key(raw, norms) not in gate] == []
