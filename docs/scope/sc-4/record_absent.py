"""Records main's document-mode answers for the documents without `forward` (sc-4's DELTA fixture, the DRI's decision
of 2026-11-01 item 1(a)). Run from this checkout with main's service: `VE_LEAN_SERVICE=<main>/lean/.lake/build/bin/
ve_service uv run python docs/scope/sc-4/record_absent.py <main commit>`; `tests/test_scope_forward.py` compares."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tests.test_scope_forward import ABSENT, absent_documents  # noqa: E402
from ve.backends.relay import answer  # noqa: E402

answers = {}
for name, text in absent_documents().items():
    row, error = answer("document", {"id": "d", "document": text, "admit": True})
    assert error is None, (name, error)
    answers[name] = row
ABSENT.write_text(json.dumps({"main": sys.argv[1], "answers": answers}, indent=1, sort_keys=True,
                             ensure_ascii=False) + "\n")
