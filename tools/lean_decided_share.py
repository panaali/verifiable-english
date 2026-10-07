"""The Lean-decided share of a document (docs/spec/readings-defaults.md 1.10 and 10; plan 3.9 and RD-5): display only.

A unit is Lean-decided when every verdict VE reports about its formal content is a Lean answer that is not UNKNOWN.
Lean decides which units qualify and lists them as `decided_units` in its `readings-verdicts` answer; this script
decides nothing. It checks that list against the document (distinct unit ids, each a unit of the document) and sums
the units' span bytes, the spans the report's coverage block already uses (`ve/document.py` `coverage`).

Beside the share it prints what qualifies it (review E2): the maximum number of rules in one choice's document as
Lean reports it (`max_choice_rules`, null when the answer does not carry it), the decided bytes whose companions were
already checked outside the document (`--checked-outside`, a JSON list of unit ids), and the sentence that a reading
holding one rule is CONFLICT-FREE by construction.

Without `--answer` there is no Lean answer across readings (a document without a readings block, such as the UDHR
run of 2026-10-06), so no unit is decided and the share is 0.

Usage: ``python tools/lean_decided_share.py DOCUMENT [--answer ANSWER.json] [--checked-outside UNITS.json]``.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ONE_RULE = "A reading holding one rule is CONFLICT-FREE by construction: a single rule cannot contradict another."


def _unit_ids(value, what):
    """A list of distinct unit id strings, or a refusal naming `what`."""
    from ve.errors import VEError
    if type(value) is not list or any(type(u) is not str for u in value):
        raise VEError(f"InvalidInput: {what} is not a list of unit ids")
    if len(set(value)) != len(value):
        raise VEError(f"InvalidInput: {what} names a unit twice")
    return value


def share(units, source_bytes, answer=None, checked_outside=None):
    """The share from the document's units (`id`, `span`), its source length, Lean's answer (or None) and the
    units whose companions were checked outside the document (or None)."""
    from ve.errors import VEError
    spans = {u["id"]: u["span"][1] - u["span"][0] for u in units}
    if answer is None:
        decided, max_rules = [], None
    else:
        if type(answer) is not dict or "decided_units" not in answer:
            raise VEError("InvalidInput: the readings-verdicts answer has no decided_units")
        decided = _unit_ids(answer["decided_units"], "decided_units")
        max_rules = answer.get("max_choice_rules")
        if max_rules is not None and (type(max_rules) is not int or max_rules < 0):
            raise VEError("InvalidInput: max_choice_rules is not a count")
    outside = [] if checked_outside is None else _unit_ids(checked_outside, "the units checked outside")
    unknown = sorted(set(decided + outside) - set(spans))
    if unknown:
        raise VEError(f"InvalidInput: {unknown[0]} is not a unit of the document")
    decided_bytes = sum(spans[u] for u in decided)
    percent = (Decimal(100 * decided_bytes) / Decimal(source_bytes)).quantize(Decimal("0.01"), ROUND_HALF_UP) \
        if source_bytes else Decimal("0.00")
    return {"source_bytes": source_bytes, "decided_units": decided, "decided_bytes": decided_bytes,
            "decided_share_percent": str(percent),
            "max_choice_rules": max_rules,
            "decided_bytes_checked_outside": sum(spans[u] for u in decided if u in set(outside)),
            "one_rule": ONE_RULE,
            "basis": "readings-verdicts decided_units" if answer is not None else "no Lean answer across readings"}


def _json_file(path):
    """A given file's JSON value; null is refused, so a given file is never read as no file."""
    from ve.errors import VEError
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError, RecursionError) as error:
        raise VEError(f"InvalidInput: {path} is not a JSON file: {error}") from None
    if value is None:
        raise VEError(f"InvalidInput: {path} holds null")
    return value


def main(argv=None):
    from ve.document import load_document
    from ve.errors import VEError
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("document")
    parser.add_argument("--answer")
    parser.add_argument("--checked-outside")
    args = parser.parse_args(argv)
    try:
        doc = load_document(args.document)
        result = share(doc["units"], len(doc["source"]),
                       None if args.answer is None else _json_file(args.answer),
                       None if args.checked_outside is None else _json_file(args.checked_outside))
    except VEError as error:
        print(error.message, file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
