"""Batch 16g precondition probe: whether Lean's `document` mode decides each named document, or Python keeps it.

`uv run --no-sync python docs/lean-first/b16g/live_probe.py <file.ve.md>...` prints, per file, "decided by Lean" or
"RETAINED", Lean's reason (None when `_document_case` keeps the text on Python's own path without asking Lean) and
whether the retained loader accepts it.
"""
from __future__ import annotations

from pathlib import Path
import sys

from tools.lean_first_diff import outcome
from ve import document as D
from ve.backends.relay import answer as relay_answer


def main() -> None:
    for name in sys.argv[1:]:
        path = Path(name).resolve()
        raw = path.read_bytes()
        if D._lean_answer(raw, True, path.parent) is not None:
            print(name, "| decided by Lean")
            continue
        case = D._document_case(raw, True, path.parent)
        reason = relay_answer("document", case)[1] if case is not None else None
        prior = outcome(lambda: D._report(D._load_document(raw, path, None)))
        print(name, "| RETAINED |", reason, "| prior:", "raised" if "raised" in prior else "accepted")


if __name__ == "__main__":
    main()
