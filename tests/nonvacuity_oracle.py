"""Frozen answers of the pre-deletion Python non-vacuity check, the oracle of Lean's.

Lean-first batch 15b deleted `ve.search._nonvacuous` (Lean's `VE.Route.NonVacuity` owns the check).
The batch-15a tests that compare Lean with it keep their oracle as a frozen record (DRI answer 7:
the pre-deletion Python stays a test oracle, isolated from the checker): `ORACLE` maps the SHA-256
(first 80 bits) of a canonical request (environment, model, formula, budget, semantic mode) to Python's
`[suitable, evaluations, exhausted]`. It was recorded at commit `RECORDED_AT`, before the
deletion, by running the tests that call `answer` with `VE_RECORD_NONVACUITY` naming the output
file (one process, no xdist). A request missing from the record fails: it cannot be computed any
more, so a test that changes its requests must be recorded again from a pre-deletion checkout.
"""
from __future__ import annotations

import atexit
import gzip
import hashlib
import json
import os
from pathlib import Path

ORACLE = Path(__file__).resolve().parent / "data/nonvacuity-oracle.json.gz"
RECORDED_AT = "bc580837"
_RECORD = os.environ.get("VE_RECORD_NONVACUITY")
_recorded: dict[str, list] = {}
_frozen: dict[str, list] | None = None


def key(raw, wire, item, budget: int, semantic: bool) -> str:
    request = [raw, wire, item, budget, semantic]
    return hashlib.sha256(json.dumps(request, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()[:20]


def answer(raw, wire, item, budget: int, semantic: bool, *, env=None, formula=None, model=None) -> list:
    """Python's frozen answer to one request (or, while recording, the live pre-deletion one)."""
    global _frozen
    name = key(raw, wire, item, budget, semantic)
    if _RECORD:
        from ve.search import _nonvacuous  # only in a pre-deletion checkout
        _recorded[name] = list(_nonvacuous(env, formula, model, budget, semantic=semantic))
        return _recorded[name]
    if _frozen is None:
        with gzip.open(ORACLE, "rt") as stream:
            _frozen = json.load(stream)
    if name not in _frozen:
        raise AssertionError(f"request {name} is not in the frozen non-vacuity oracle {ORACLE.name}")
    return _frozen[name]


def _write() -> None:
    target = Path(_RECORD)
    old = {}
    if target.exists():
        with gzip.open(target, "rt") as stream:
            old = json.load(stream)
    with gzip.GzipFile(target, "wb", mtime=0) as stream:
        stream.write(json.dumps({**old, **_recorded}, sort_keys=True, separators=(",", ":")).encode())


if _RECORD:
    atexit.register(_write)
