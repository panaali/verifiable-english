"""Diagnostics of the checker that sends no code: the Rust JSONL checker.

The Lean service sends its own code, which `relay.py` relays; since lean-first batch 1 every Lean
route is a service mode, so no Lean row reaches this module. Rust leaves the code in the message's
`Class:` prefix; the text is kept verbatim (docs/LEAN-FIRST-PLAN.md, rule 2: no prefix stripping).
An unrecognised prefix is InvalidInput, never a verdict. Retained until Rust texts stop reaching
users (batch 15).
"""
from __future__ import annotations

import re

from ..errors import Span, VEError
from .relay import CLASSES, rejection


def checker_error(message: str, *, code: str | None = None,
                  span: dict | None = None, generator: str | None = None) -> VEError:
    """Make the existing VEError class from a Rust or one-shot Lean error record."""
    match = re.match(r"^InvalidModel\(([^)]*)\)", message)
    if match:
        code, generator = "InvalidModel", generator or match.group(1)
    elif code is None:
        code = message.partition(":")[0]
    error = rejection(code if code in CLASSES else "InvalidInput", message, generator=generator)
    if span is not None and isinstance(error, VEError):
        error.span = Span(**span)
    return error


def backend_rejection(error: VEError) -> VEError:
    """Mark `error` as naming a rejection a Lean or Rust checker returned.

    The mark is provenance only: the Gate 2 parity tool counts a rejection
    cell as backend-decided when the error the operation raised carries it."""
    error.backend_rejection = True
    return error


def require_ok(record: dict) -> dict:
    """Return a successful Rust record or raise its classified diagnostic.

    `record` has passed `rust_jsonl.record_problem`: a rejection carries its complete
    diagnostic (`code`, `message`, optional `span`), so nothing here supplies a default."""
    if record["status"] == "error":
        error = record["error"]
        raise backend_rejection(checker_error(error["message"], code=error["code"], span=error.get("span")))
    return record
