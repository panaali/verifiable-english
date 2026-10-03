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
from pathlib import Path

import pytest

from conformance import soft_norms
from conformance.soft_norms import (RUST_FIXTURES, combined_invalid_soft_blocks, generated_invalid_soft_blocks,
                                    generated_invalid_soft_rules, rejected_sources, soft3_reproducers)
from conformance.wire_contract_gate import (EXAMPLES, RECORDED_TESTS, TEST_INPUTS, gate_cases,
                                            record_test_inputs, source_key, unit_of)
from tests.test_soft_norms_conformance import fixtures
from tests.test_wire_contract_soft_lean import fixture_sources
from ve.wire_contract.engine import load

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "conformance/wire-contract/soft-norms@0-golden.json"
# The test files that submit `soft-norms@0` inputs; each must record at least one.
SUBMITTING = {"test_softnorms_contract.py", "test_softnorms_public_contract.py",
              "test_wire_contract_faults.py", "test_wire_contract_precondition.py",
              "test_wire_contract_soft_lean.py", "test_wire_contract_three_way.py",
              "test_soft_norms_conformance.py", "test_soft_norms_lean.py", "test_soft_review_regressions.py"}
# The conformance module's functions that build no source of their own: the comparisons that run the
# validators on the sources the other functions build, and the fault mutations `multi_fault_cases` applies.
NOT_SOURCES = {"compare_near_limit", "compare_rejected", "main", "multi_faults", "rust_fixture_rows",
               "smallest_queries"}


@lru_cache(maxsize=1)
def corpus():
    return frozenset(source_key(case[2], case[3]) for case in gate_cases(load("soft-norms@0")))


def test_gate_corpus_holds_every_contract_and_soft_test_input(tmp_path):
    """A missing input is a test input no source of the corpus builds: `python -m
    conformance.wire_contract_gate --record-test-inputs` records it into `TEST_INPUTS`, which the gate replays
    (Lean reads none that carries a `null`, which only the in-process API can)."""
    files = {path for pattern in RECORDED_TESTS for path in ROOT.glob(pattern)}
    assert set(ROOT.glob("tests/test_wire_contract*")) | set(ROOT.glob("tests/test_softnorms*")) <= files
    assert Path(__file__) not in files
    output = tmp_path / "inputs.json"
    result = record_test_inputs(output)
    # A skipped or failed test may have submitted fewer inputs than it does when it runs.
    assert result.returncode == 0 and " skipped" not in result.stdout, result.stdout[-4000:] + result.stderr[-4000:]
    recorded = json.loads(output.read_text())
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
UNIT_SUBMITTING = {"norms@0": {"test_norms_contract.py", "test_norm_admission.py", "test_norms.py",
                               "test_norms_three_way.py"},
                   "norm-defaults@0": {"test_norm_defaults_contract.py", "test_norm_defaults.py",
                                       "test_norm_defaults_three_way.py", "test_norm_defaults_differential.py"}}
UNIT_TESTS = {"norms@0": "tests.test_norms_contract", "norm-defaults@0": "tests.test_norm_defaults_contract"}


@lru_cache(maxsize=None)
def unit_corpus(unit):
    return frozenset(source_key(case[2], case[3]) for case in gate_cases(load(unit)))


@pytest.mark.parametrize("unit", UNITS)
def test_unit_gate_corpus_holds_every_recorded_test_input(unit, tmp_path):
    """A missing input is a test input no source of the unit's corpus builds: `python -m
    conformance.wire_contract_gate --unit <unit> --record-test-inputs` records it into the unit's test inputs."""
    output = tmp_path / "inputs.json"
    result = record_test_inputs(output, unit)
    assert result.returncode == 0 and " skipped" not in result.stdout, result.stdout[-4000:] + result.stderr[-4000:]
    recorded = json.loads(output.read_text())
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
    """The fixtures of the unit's statement spec that its tests build, and its examples."""
    module = unit_of(unit).module
    sources = importlib.import_module(UNIT_TESTS[unit]).fixture_sources() + module.example_sources()
    gate = unit_corpus(unit)
    assert len(module.example_sources()) >= 2
    assert [label for label, raw, norms in sources if source_key(raw, norms) not in gate] == []
