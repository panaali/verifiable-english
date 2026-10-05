"""A pytest plugin that records every case the tests send to a statement-layer route mode.

Loaded with `-p tests.route_case_recorder` and `VE_ROUTE_CASES=<directory>`, it wraps
`LeanService._run_chunk`, through which every batch of the Lean service passes (`relay`,
`tests/lean_routes.py`, the use-case harnesses), and writes the distinct case texts of the modes
that replaced a one-shot executable in docs/LEAN-FIRST-PLAN.md batch 1 to
`<directory>/<worker>.jsonl`, one `[mode, case text]` per line. `docs/lean-first/b1/route_parity.py`
replays them through the one-shot executables of a build from before batch 1 (the Gate-1 byte
parity of the batch).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# The service modes of the one-shot route executables (`tests/lean_routes.py` MODES).
ROUTE_MODES = frozenset({"norms", "soft-norms", "rights", "speech-acts", "reports", "alternatives", "risk",
                         "risk-eval", "quantity", "norm-defaults", "discourse", "readings-route", "diagnose"})
_RECORDED: dict[tuple[str, str], None] = {}


def _install():
    from ve.backends.lean_service import LeanService
    original = LeanService._run_chunk

    def run_chunk(self, mode, chunk, timeout):
        if mode in ROUTE_MODES:
            for item in chunk:
                # A case sent with an environment handle is recorded with its environment (lean-first b2).
                _RECORDED.setdefault((mode, item if isinstance(item, str) else item.inline()), None)
        return original(self, mode, chunk, timeout)

    LeanService._run_chunk = run_chunk


def pytest_sessionfinish(session):
    directory = os.environ.get("VE_ROUTE_CASES")
    if not directory or not _RECORDED:
        return
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    path = Path(directory) / f"{worker}-{os.getpid()}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as out:
        for mode, text in _RECORDED:
            out.write(json.dumps([mode, text], ensure_ascii=False) + "\n")


_install()
