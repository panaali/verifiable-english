"""Bounded one-request client for Rust's JSON-lines evaluator and searcher."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess

from ..errors import ResourceLimit
from .diagnostics import require_ok
from .lean_service import CheckerUnavailable, _decode_json

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXECUTABLE = ROOT / "rust/target/release/ve"
BUILD_LOCK = ROOT / "lean/checkers.lock"
MAX_LINE_BYTES = 16 * 1024 * 1024
# Bound at import: a later monkeypatch of subprocess.run (a test fake for some
# other process) must not intercept the checker process.
_RUN = subprocess.run


def run(case: dict, *, executable: str | os.PathLike | None = None,
        timeout: float = 5.0, expected_sha256: str | None = None) -> dict:
    """Run one case and return its checked record, or a classified error.

    The subprocess is waited on before returning, so no worker outlives the
    call. A selected Rust backend never falls back to Python.
    """
    binary = Path(executable or os.environ.get("VE_RUST_JSONL") or DEFAULT_EXECUTABLE)
    if not binary.is_file():
        raise CheckerUnavailable(f"CheckerUnavailable: missing Rust executable {binary}")
    try:
        allowed = ([expected_sha256] if expected_sha256 is not None else
                   [os.environ["VE_RUST_SHA256"]] if "VE_RUST_SHA256" in os.environ else
                   json.loads(BUILD_LOCK.read_text())["rust_jsonl"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: invalid Rust build lock: {exc}") from None
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    if digest not in allowed:
        raise CheckerUnavailable(f"CheckerUnavailable: Rust executable hash mismatch: {binary}")
    data = json.dumps(case, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"
    if len(data) > MAX_LINE_BYTES:
        raise ResourceLimit(f"Rust case exceeds {MAX_LINE_BYTES} bytes")
    try:
        completed = _RUN([str(binary), "jsonl", "-"], input=data,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: Rust checker failed: {exc}") from None
    if len(completed.stdout) > MAX_LINE_BYTES:
        raise CheckerUnavailable("CheckerUnavailable: oversized Rust JSONL response")
    lines = completed.stdout.splitlines()
    if completed.returncode not in (0, 1) or len(lines) != 1:
        detail = completed.stderr[:200].decode("utf-8", "replace")
        raise CheckerUnavailable(
            f"CheckerUnavailable: Rust protocol failure (exit {completed.returncode}; {detail})")
    try:
        record = _decode_json(lines[0])
    except (UnicodeDecodeError, ValueError):
        raise CheckerUnavailable("CheckerUnavailable: malformed Rust JSONL response") from None
    if not isinstance(record, dict) or record.get("id") != case.get("id", ""):
        raise CheckerUnavailable("CheckerUnavailable: mismatched Rust response id")
    if (record.get("status") == "error") != (completed.returncode == 1):
        raise CheckerUnavailable("CheckerUnavailable: Rust exit status disagrees with response")
    if case.get("kind") == "evaluate-budgeted" and record.get("status") != "error":
        expected = {"id", "status", "value", "evaluations"}
        if case.get("trace") is True:
            expected.add("explanation")
        if (set(record) != expected or type(record["status"]) is not str or record["status"] not in
                {"Satisfied", "Violated", "ResourceLimit"}
                or type(record["evaluations"]) is not int
                or not 0 <= record["evaluations"] <= case["max_evaluations"]
                or record["value"] is not ({"Satisfied": True, "Violated": False,
                                             "ResourceLimit": None})[record["status"]]):
            raise CheckerUnavailable("CheckerUnavailable: malformed Rust evaluation result")
    if "premises" in case and "model" in case and record.get("status") != "error":
        expected = {"id", "status", "valid", "premise_values", "conclusion_value",
                    "evaluations", "environment_id", "model_id", "premise_meaning_ids",
                    "conclusion_meaning_id"}
        if (set(record) != expected or type(record["status"]) is not str or record["status"] not in
                {"Valid", "NotCountermodel", "ResourceLimit"}
                or type(record["valid"]) is not bool
                or type(record["evaluations"]) is not int
                or not 0 <= record["evaluations"] <= case["max_evaluations"]
                or type(record["premise_values"]) is not list
                or any(type(v) is not bool for v in record["premise_values"])
                or len(record["premise_values"]) > len(case["premises"])):
            raise CheckerUnavailable("CheckerUnavailable: malformed Rust countermodel result")
    return require_ok(record)
