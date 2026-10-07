"""Check the DRI decisions required by LEAN-FIRST-PLAN.md section 5.1.

The corpus comparator owns the delta classification. This file binds a human
decision to that exact listing; it does not classify or approve any change.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"


def digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def required(delta: dict) -> tuple[str | None, set[str]]:
    """One block for wording/order; one distinct approval per verdict/availability row."""
    block = {name: delta.get(name, []) for name in ("wording", "order")}
    block_id = digest(block) if any(block.values()) else None
    records = [*delta.get("verdict", []), *delta.get("availability", [])]
    ids = [digest(record) for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate verdict or availability record in delta")
    return block_id, set(ids)


def problems(delta: dict, signoff: dict | None) -> list[str]:
    block_id, record_ids = required(delta)
    if block_id is None and not record_ids:
        return []
    if signoff is None:
        return ["DRI signoff is absent"]
    if type(signoff) is not dict:
        return ["DRI signoff must be an object"]
    errors = []
    if set(signoff) != {"format", "wording_order", "verdicts"}:
        errors.append("signoff fields do not match the required schema")
    if signoff.get("format") != "lean-first-b12-signoff@1":
        errors.append("unrecognised signoff format")

    def signed(item: object, expected: str, label: str) -> None:
        if type(item) is not dict or set(item) != {"sha256", "signed_by", "date", "decision", "source"}:
            errors.append(f"{label}: incomplete signature")
            return
        if item["sha256"] != expected:
            errors.append(f"{label}: digest differs from delta")
        if item["signed_by"] != "DRI" or item["decision"] != "approved":
            errors.append(f"{label}: no DRI approval")
        if not all(type(item[key]) is str and item[key].strip()
                   for key in ("date", "source")):
            errors.append(f"{label}: date or source missing")

    block = signoff.get("wording_order")
    if block_id is None:
        if block is not None:
            errors.append("unneeded wording/order signature")
    else:
        signed(block, block_id, "wording/order")
    rows = signoff.get("verdicts")
    if type(rows) is not list:
        errors.append("verdict signature list missing")
        rows = []
    seen = set()
    for i, row in enumerate(rows):
        identifier = row.get("sha256") if type(row) is dict else None
        if type(identifier) is not str:
            errors.append(f"verdict {i}: invalid digest")
            continue
        if identifier in seen:
            errors.append(f"verdict {i}: duplicate signature")
        seen.add(identifier)
        if identifier not in record_ids:
            errors.append(f"verdict {i}: unlisted record")
        else:
            signed(row, identifier, f"verdict {i}")
    for identifier in sorted(record_ids - seen):
        errors.append(f"verdict {identifier}: unsigned")
    return errors


def check() -> list[str]:
    delta = json.loads((EVIDENCE / "delta.json").read_text())
    path = EVIDENCE / "signoff.json"
    signoff = json.loads(path.read_text()) if path.exists() else None
    return problems(delta, signoff)
