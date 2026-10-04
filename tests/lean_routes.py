"""The statement-layer Lean routes for tests and harnesses, through the Lean service.

Since docs/LEAN-FIRST-PLAN.md batch 1 every one-shot route executable is a `ve_service` mode
(`lean/VE/Service/Protocol.lean`, pinned by `runMode_*`), and the executables are no longer
built by default. `MODES` maps each executable to its mode. `run` answers a case list as the
executable answered it: its exit status (0 when every row is an answer, 1 when a row is a
rejection, 2 when the whole batch is refused, as the one-shot's framing errors were), its rows
(`None` when refused), and the standard error the service printed meanwhile (Lean's `PANIC`
messages, for example; for a refused batch, the service's diagnostic).
"""
from __future__ import annotations

import atexit

from ve.backends.lean_service import LeanService
from ve.errors import VEError

MODES = {
    "ve_norms_route": "norms", "ve_soft_norms_route": "soft-norms", "ve_rights_route": "rights",
    "ve_speech_acts_route": "speech-acts", "ve_reports_route": "reports",
    "ve_alternatives_route": "alternatives", "ve_risk_route": "risk", "ve_risk_eval": "risk-eval",
    "ve_quantity": "quantity", "ve_norm_defaults_route": "norm-defaults", "ve_discourse_route": "discourse",
    "ve_readings_route": "readings-route", "ve_diagnose": "diagnose",
}

_service: LeanService | None = None


def _started() -> LeanService:
    global _service
    if _service is None:
        _service = LeanService()
        atexit.register(_service.close)
    _service.start()
    return _service


def run(route: str, cases: list, *, timeout: float | None = None) -> tuple[int, list | None, str]:
    """(exit status, rows, stderr) for `cases` on `route`, an executable name or a mode."""
    service = _started()
    start, _ = service.stderr()
    try:
        rows = service.run(MODES.get(route, route), cases, timeout=timeout)
    except VEError as refused:
        return 2, None, refused.message
    _, stderr = service.stderr(start)
    return (1 if any(type(r) is dict and r.get("status") == "error" for r in rows) else 0), rows, stderr


def rows(route: str, cases: list, *, timeout: float | None = None) -> list:
    """The rows of `run`; a refused batch raises its diagnostic."""
    service = _started()
    return service.run(MODES.get(route, route), cases, timeout=timeout)


def diagnose(unit: str, cases: list, *, timeout: float | None = None) -> list:
    """The rows `ve_diagnose <unit>` printed for `cases` (mode `diagnose`)."""
    return rows("diagnose", [{**case, "unit": unit} for case in cases], timeout=timeout)
