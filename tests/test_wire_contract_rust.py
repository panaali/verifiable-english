"""The generated Rust contract tables (docs/spec/wire-contract-s4-2.md 9, F3): the rows a cargo test dumps
from every generated table equal the rows `tools/wire_contract.py` reads from the contract JSON."""

import json
import shutil
import subprocess

import pytest

from tests.subprocesses import HANG_TIMEOUT
from tools import rust_build
from tools.wire_contract import DATA, ROOT, UNITS, table_rows
from ve.wire import loads_json

CORPUS = ROOT / "conformance/wire-contract/contracts"


def _contracts(directory):
    return {value["contract"]: value for value in
            (loads_json(path.read_bytes()) for path in sorted(directory.glob("*@*.json")))}


def _expected():
    rows = []
    for directory, units in ((DATA, UNITS), (CORPUS, None)):
        contracts = _contracts(directory)
        limits = loads_json((directory / "limits.json").read_bytes())
        for unit in sorted(units or contracts):
            rows += table_rows(contracts[unit], contracts, limits)
    return rows


def test_rust_table_rows_equal_the_contract_rows(tmp_path):
    cargo = shutil.which("cargo")
    if cargo is None:
        pytest.skip("cargo is required for the Rust table dump")
    dump = tmp_path / "rows.jsonl"
    run = subprocess.run([cargo, "test", "-j", "2", "--locked", "-p", "ve-kernel", "--test", "contract_tables",
                          "--", "--exact", "dump_rows"],
                         cwd=ROOT / "rust", env={**rust_build.cargo_env(), "VE_CONTRACT_DUMP": str(dump)},
                         capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout[-4000:] + run.stderr[-4000:]
    dumped = [json.loads(line) for line in dump.read_text(encoding="utf-8").splitlines()]
    expected = _expected()
    assert {row["contract"] for row in dumped} == set(UNITS) | set(_contracts(CORPUS))
    for got, want in zip(dumped, expected):
        assert got == want
    assert len(dumped) == len(expected)
    # The key outside the BMP sorts after U+FF5A by code point; UTF-16 order would put it first.
    assert next(row for row in dumped if row["contract"] == "keys@0")["keys"][0] == ["ｚ", "\U0001f600"]
