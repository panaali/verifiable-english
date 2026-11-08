"""Records main's document-mode answer for the UDHR part document without a rights reach (sc-6's DELTA fixture). Run
from this checkout with main's service: `VE_LEAN_SERVICE=<main>/lean/.lake/build/bin/ve_service uv run python
docs/scope/sc-6/record_absent.py <main commit>`; `tests/test_scope_rights_reach.py` compares."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tests.test_scope_rights_reach import ABSENT, udhr_text  # noqa: E402
from ve.backends.relay import answer  # noqa: E402

row, error = answer("document", {"id": "d", "document": udhr_text(), "admit": True})
assert error is None, error
ABSENT.write_text(json.dumps({"main": sys.argv[1], "answers": {"udhr": row}}, indent=1, sort_keys=True,
                             ensure_ascii=False) + "\n")
