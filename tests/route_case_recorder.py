"""A pytest plugin that records every case the tests send to a statement-layer route mode.

Loaded with `-p tests.route_case_recorder` and `VE_ROUTE_CASES=<directory>`, it wraps
`LeanService._run_chunk`, through which every batch of the Lean service passes (`relay`,
`tests/lean_routes.py`, the use-case harnesses), and writes the distinct case texts of the modes
that replaced a one-shot executable in docs/LEAN-FIRST-PLAN.md batch 1 to
`<directory>/<worker>.jsonl`, one `[mode, case text]` per line. `docs/lean-first/b1/route_parity.py`
replays them through the one-shot executables of a build from before batch 1 (the Gate-1 byte
parity of the batch).

With `VE_RELAY_CASES=<directory>` it also records, for `tools/relay_mutation_gate.py --record`, every
distinct case of every relayed Lean route: `["service", mode, case text]` for each service mode, and
`["one-shot", runner, mode, case text]` for each case `ve.backends.lean` sends a one-shot runner
(`ve_metered`, `ve_conformance`, `ve_senses_route`, `ve_speech_acts_route`, ...), written to
`<directory>/relay-<worker>-<pid>.jsonl`. Only requests the service answered without a request error,
and runs that exited 0, are kept.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# The service modes of the one-shot route executables (`tests/lean_routes.py` MODES).
ROUTE_MODES = frozenset({"norms", "soft-norms", "rights", "speech-acts", "reports", "alternatives", "risk",
                         "risk-eval", "quantity", "norm-defaults", "discourse", "readings-route", "diagnose"})
_RECORDED: dict[tuple[str, str], None] = {}
_RELAYED: dict[tuple[str, ...], None] = {}


def _install():
    from ve.backends import lean
    from ve.backends.lean_service import LeanService
    original = LeanService._run_chunk

    def run_chunk(self, mode, chunk, timeout):
        texts = [item if isinstance(item, str) else item.inline() for item in chunk]
        if mode in ROUTE_MODES:
            for text in texts:
                # A case sent with an environment handle is recorded with its environment (lean-first b2).
                _RECORDED.setdefault((mode, text), None)
        entries = original(self, mode, chunk, timeout)
        if os.environ.get("VE_RELAY_CASES"):
            for text in texts:
                _RELAYED.setdefault(("service", mode, text), None)
        return entries

    LeanService._run_chunk = run_chunk

    if not os.environ.get("VE_RELAY_CASES"):
        return
    real = lean.subprocess

    class Recording:
        """`subprocess` as `ve.backends.lean` sees it; `run` records the cases a Lean runner answered."""

        def __getattr__(self, name):
            return getattr(real, name)

        @staticmethod
        def run(argv, *args, **kwargs):
            done = real.run(argv, *args, **kwargs)
            runner = Path(str(argv[0])).name
            try:
                cases = json.loads(kwargs.get("input") or b"")
            except ValueError:
                cases = None
            if runner.startswith("ve_") and done.returncode == 0 and isinstance(cases, list):
                mode = str(argv[1]) if len(argv) > 1 else ""
                for case in cases:
                    _RELAYED.setdefault(("one-shot", runner, mode, json.dumps(case, separators=(",", ":"))), None)
            return done

    lean.subprocess = Recording()


def pytest_sessionfinish(session):
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    directory = os.environ.get("VE_ROUTE_CASES")
    if directory and _RECORDED:
        path = Path(directory) / f"{worker}-{os.getpid()}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as out:
            for mode, text in _RECORDED:
                out.write(json.dumps([mode, text], ensure_ascii=False) + "\n")
    directory = os.environ.get("VE_RELAY_CASES")
    if directory and _RELAYED:
        path = Path(directory) / f"relay-{worker}-{os.getpid()}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as out:
            for row in _RELAYED:
                # ASCII escapes: a case may hold a lone surrogate, which no UTF-8 file can.
                out.write(json.dumps(list(row)) + "\n")


_install()
