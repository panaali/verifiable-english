"""The Stage 0 baseline in shadow: fixtures L9 and Z3 of docs/spec/mig3.md (8.3, 8.5).

Usage: ``uv run python tools/shadow_baseline.py [--parity lean.json] [--json out.json]``

Every probe cell of ``tests/probe_matrix.py`` is rerun with its probed call at
``VE_AUTHORITY=shadow`` (inputs built by the retained Python, as
``tools/stage2_parity.py`` builds them), and for each cell:

* the shadow call's result must be today's Python result (V1);
* the cell has a compared call, or an uncompared call (``note_uncompared``),
  or neither; with ``--parity`` (the ``--json`` output of
  ``tools/stage2_parity.py --authority lean``) every cell with neither must be
  in the parity tool's class ``same, python`` (L9);
* on every compared call the public record of the object Python returned is
  the same before and after the candidate ran (V4, Z3).

Records go to a temporary ``VE_SHADOW_DIR``; their number is reported too.
Exit 0 when every check holds.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests import probe_matrix as probe  # noqa: E402
from tools import stage2_parity as parity  # noqa: E402
from ve.backends import dispatch  # noqa: E402

_python_outcome = probe.outcome
_v4: list[str] = []


def _totals() -> tuple[int, int]:
    worker = dispatch._worker()
    ops = worker.ops.values() if worker is not None else ()
    return (sum(counts["compared"] for counts in ops),
            sum(sum(counts["uncompared"].values()) for counts in ops))


def _checked_shadow(original):
    """`dispatch._shadow` with V4 checked: Python's returned object keeps its
    public record while the candidate runs."""
    def shadow(op, payload, python, lean):
        kept = []

        def python_side():
            value = python()
            try:
                kept.append((value, json.dumps(dispatch._record(value), sort_keys=True, default=repr)))
            except Exception as exc:  # noqa: BLE001 - an unrecordable value is reported, not compared
                _v4.append(f"{op}: the public record cannot be taken ({type(exc).__name__})")
            return value

        def candidate():
            try:
                return lean()
            finally:
                for value, before in kept:
                    if json.dumps(dispatch._record(value), sort_keys=True, default=repr) != before:
                        _v4.append(f"{op}: the candidate changed Python's returned object")

        return original(op, payload, python_side, None if lean is None else candidate)
    return shadow


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--parity", type=Path, help="tools/stage2_parity.py --authority lean --json output")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    def outcome(call, *, expected=()):
        before = _totals()
        os.environ["VE_AUTHORITY"] = "shadow"
        try:
            result = _python_outcome(call, expected=expected)
        finally:
            os.environ["VE_AUTHORITY"] = "python"
        after = _totals()
        return {**result, "shadow": [after[0] - before[0], after[1] - before[1]]}

    with tempfile.TemporaryDirectory() as scratch:
        os.environ["VE_SHADOW_DIR"] = scratch
        os.environ.pop("VE_SHADOW_LOG", None)
        os.environ.pop("VE_AUTHORITY_OVERRIDES", None)
        os.environ["VE_AUTHORITY"] = "python"
        dispatch._shadow = _checked_shadow(dispatch._shadow)
        now = probe.generate()
        probe.outcome = outcome
        shadow = probe.generate()
        records = sum(len(path.read_text().splitlines()) for path in Path(scratch).glob("records-*.jsonl"))
    cells = shadow["cells"]
    coverage = [tuple(row.get("shadow", (0, 0))) for row in cells]
    keys = [parity._key(row) for row in cells]
    mismatched = [key for key, old, new in zip(keys, now["cells"], cells)
                  if parity._projected(old) != parity._projected(new)]
    compared = [key for key, (c, _) in zip(keys, coverage) if c]
    uncompared = [key for key, (c, u) in zip(keys, coverage) if not c and u]
    neither = [key for key, (c, u) in zip(keys, coverage) if not c and not u]
    classes = None
    if args.parity:
        by_key = {tuple(tuple(part) if isinstance(part, list) else part for part in cell["key"]): cell["class"]
                  for cell in json.loads(args.parity.read_text())["cells"]}
        classes = Counter(by_key.get(key, "missing") for key in neither)
    summary = {"cells": len(cells), "compared": len(compared), "uncompared": len(uncompared),
               "neither": len(neither), "neither_parity_classes": dict(classes) if classes is not None else None,
               "shadow_differs_from_python": [list(key) for key in mismatched[:20]],
               "shadow_differs_count": len(mismatched), "v4_violations": _v4[:20],
               "v4_count": len(_v4), "records": records,
               "neither_by_operation": dict(Counter(key[2] for key in neither))}
    if args.json:
        args.json.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=1, sort_keys=True))
    ok = not mismatched and not _v4 and (classes is None or set(classes) <= {"same, python"})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
