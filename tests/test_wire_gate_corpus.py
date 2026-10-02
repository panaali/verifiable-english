"""The soft-norms gate's corpus condition (wire loop final): the gate replays every `soft-norms@0` input that
the contract tests submit and every soft conformance fixture.

The contract tests (`tests/test_*contract*`, which include `tests/test_wire_contract*`) are run again under
`tests.contract_input_recorder`, which records each input they hand to either engine or either legacy
validator; an input missing from `gate_cases` fails the test, so a new test input that the gate does not
replay is caught when it is added. This file's name does not match the glob, so it does not record itself.
"""

import json
import os
from pathlib import Path
import subprocess
import sys

from conformance.soft_norms import (RUST_FIXTURES, combined_invalid_soft_blocks, generated_invalid_soft_blocks,
                                    generated_invalid_soft_rules, rejected_sources, soft3_reproducers)
from conformance.wire_contract_gate import EXAMPLES, gate_cases, source_key
from tests.test_soft_norms_conformance import fixtures
from tests.test_wire_contract_soft_lean import fixture_sources
from ve.wire_contract.engine import load

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "conformance/wire-contract/soft-norms@0-golden.json"
# The contract test files that submit `soft-norms@0` inputs; each must record at least one.
SUBMITTING = {"test_softnorms_contract.py", "test_wire_contract_faults.py", "test_wire_contract_precondition.py",
              "test_wire_contract_soft_lean.py", "test_wire_contract_three_way.py"}


def corpus():
    return {source_key(case[2], case[3]) for case in gate_cases(load("soft-norms@0"))}


def test_gate_corpus_holds_every_contract_test_input(tmp_path):
    files = sorted(ROOT.glob("tests/test_*contract*"))
    assert set(ROOT.glob("tests/test_wire_contract*")) <= set(files)
    assert Path(__file__) not in files
    output = tmp_path / "inputs.json"
    environment = {**os.environ, "VE_CONTRACT_INPUTS": str(output), "VE_NATIVE_PREBUILT": "1",
                   "PYTHONPATH": str(ROOT)}
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "tests.contract_input_recorder",
                             "-p", "no:cacheprovider", "-o", "addopts=", "-m", "not live", *map(str, files)],
                            cwd=ROOT, env=environment, capture_output=True, text=True, timeout=3600)
    # A skipped or failed test may have submitted fewer inputs than it does when it runs.
    assert result.returncode == 0 and " skipped" not in result.stdout, result.stdout[-4000:] + result.stderr[-4000:]
    recorded = json.loads(output.read_text())
    assert SUBMITTING <= {Path(label.split("::")[0]).name for label, _, _ in recorded}
    gate = corpus()
    missing = sorted({label for label, raw, norms in recorded if source_key(raw, norms) not in gate})
    assert missing == []


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
