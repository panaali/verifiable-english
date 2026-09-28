"""Bounded one-request client for Rust's JSON-lines evaluator and searcher."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess

from ..errors import ResourceLimit
from .diagnostics import require_ok
from .lean_service import CheckerUnavailable

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXECUTABLE = ROOT / "rust/target/release/ve"
BUILD_LOCK = ROOT / "lean/checkers.lock"
MAX_LINE_BYTES = 16 * 1024 * 1024


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
        completed = subprocess.run([str(binary), "jsonl", "-"], input=data,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: Rust checker failed: {exc}") from None
    lines = completed.stdout.splitlines()
    if completed.returncode not in (0, 1) or len(lines) != 1:
        detail = completed.stderr[:200].decode("utf-8", "replace")
        raise CheckerUnavailable(
            f"CheckerUnavailable: Rust protocol failure (exit {completed.returncode}; {detail})")
    try:
        record = json.loads(lines[0])
    except (UnicodeDecodeError, ValueError):
        raise CheckerUnavailable("CheckerUnavailable: malformed Rust JSONL response") from None
    if not isinstance(record, dict) or record.get("id") != case.get("id", ""):
        raise CheckerUnavailable("CheckerUnavailable: mismatched Rust response id")
    if record.get("status") != "error" and completed.returncode != 0:
        raise CheckerUnavailable("CheckerUnavailable: Rust exit status disagrees with response")
    return require_ok(record)
