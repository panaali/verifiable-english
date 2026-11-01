"""The generated Rust contract tables and the Rust engine (docs/spec/wire-contract-s4-2.md 9). F3: the rows a
cargo test dumps from every generated table equal the rows `tools/wire_contract.py` reads from the contract
JSON. F5: the engine corpus run in Rust gives Lean's records (engine-golden.json) and Python's, byte for byte,
wherever Rust does not defer; every deferred outcome is counted, never compared."""

import json
import shutil
import subprocess

import pytest

from conformance.wire_contract_engine import CLEAN, Deferred
from tests.subprocesses import HANG_TIMEOUT
from tests.test_wire_contract_corpus import _run as python_run
from tests.test_wire_contract_lean import DEFER, DEMO
from tools import rust_build
from tools.wire_contract import DATA, KEYS, ROOT, UNITS, table_rows
from ve.wire import canonical_json, loads_json

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
    keys = loads_json((ROOT / KEYS[0]).read_bytes())
    return rows + table_rows(keys, {"keys@0": keys}, {})


def _cargo_test(target, name, env):
    cargo = shutil.which("cargo")
    if cargo is None:
        pytest.skip("cargo is required for the Rust contract tests")
    run = subprocess.run([cargo, "test", "-j", "2", "--locked", "-p", "ve-kernel", "--test", target,
                          "--", "--exact", name, "--nocapture"],
                         cwd=ROOT / "rust", env={**rust_build.cargo_env(), **env},
                         capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout[-4000:] + run.stderr[-4000:]
    return run.stderr


def test_rust_table_rows_equal_the_contract_rows(tmp_path):
    dump = tmp_path / "rows.jsonl"
    _cargo_test("contract_tables", "dump_rows", {"VE_CONTRACT_DUMP": str(dump)})
    dumped = [json.loads(line) for line in dump.read_text(encoding="utf-8").splitlines()]
    expected = _expected()
    assert {row["contract"] for row in dumped} == set(UNITS) | set(_contracts(CORPUS)) | {"keys@0"}
    for got, want in zip(dumped, expected):
        assert got == want
    assert len(dumped) == len(expected)
    # The key outside the BMP sorts after U+FF5A by code point; UTF-16 order would put it first.
    assert next(row for row in dumped if row["contract"] == "keys@0")["keys"][0] == ["ｚ", "\U0001f600"]


# Every case of engine-golden.json with its root: the Lean corpus's `demo@0` and `defer@0` cases.
CASES = [("demo@0", name, root, lean) for name, (root, lean) in DEMO.items()] + \
        [("defer@0", name, root, lean) for name, (root, lean) in DEFER.items()]
GOLDEN = json.loads((ROOT / "conformance/wire-contract/engine-golden.json").read_text(encoding="utf-8"))


def share(rows):
    """Plan row d: Rust's fault and clean rows, each equal to Lean's record, the golden and Python's
    (canonical JSON), and its deferred rows, counted and never compared. Returns the two lists of ids."""
    compared, deferred = [], []
    for (unit, name, root, lean), row in zip(CASES, rows, strict=True):
        assert row["id"] == name
        if row["outcome"] == "deferred":
            deferred.append(name)
            continue
        rust = "clean" if row["outcome"] == "clean" else canonical_json(row["record"])
        python = python_run(unit, root)
        assert not isinstance(python, Deferred), name
        python = "clean" if python is CLEAN else canonical_json(python.record)
        assert rust == lean == (GOLDEN[unit][name] if GOLDEN[unit][name] == "clean" else canonical_json(GOLDEN[unit][name])) == python, name
        compared.append(name)
    return compared, deferred


@pytest.fixture(scope="module")
def rust_rows(tmp_path_factory):
    directory = tmp_path_factory.mktemp("engine")
    cases, out = directory / "cases.json", directory / "out.jsonl"
    cases.write_text(json.dumps([{"unit": unit, "id": name, "root": root} for unit, name, root, _ in CASES]))
    printed = _cargo_test("contract_engine", "engine_corpus_equals_the_golden",
                          {"VE_ENGINE_CASES": str(cases), "VE_ENGINE_OUT": str(out)})
    print(next(line for line in printed.splitlines() if line.startswith("engine corpus in Rust")))
    return [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]


def test_rust_engine_records_equal_lean_python_and_the_golden(rust_rows):
    """F5 over every golden case: 31 equal, byte for byte; 12 deferred, at the view `3.4` or the hook `d2`."""
    assert {(unit, name) for unit, name, _, _ in CASES} == {
        (unit, name) for unit in ("demo@0", "defer@0") for name in GOLDEN[unit]}
    compared, deferred = share(rust_rows)
    assert (len(compared), len(deferred)) == (31, 12)
    assert {row["deferred"] for row in rust_rows if row["outcome"] == "deferred"} == {"3.4", "d2"}


def test_the_deferred_share_is_counted_and_never_compared(rust_rows):
    """A deferred row passes `share` whatever its record says; a fault row with a wrong record does not."""
    rows = [dict(row) for row in rust_rows]
    for row in rows:
        if row["outcome"] == "deferred":
            row["record"] = {"wrong": True}
    assert share(rows) == share(rust_rows)
    fault = next(row for row in rows if row["outcome"] == "fault")
    fault["record"] = {**fault["record"], "text": "other"}
    with pytest.raises(AssertionError):
        share(rows)

