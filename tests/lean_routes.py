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
import json
from pathlib import Path

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


def mode(route) -> str:
    """The service mode of `route`: a mode, an executable name or an executable's path."""
    name = Path(str(route)).name
    return MODES.get(name, name)


def _started() -> LeanService:
    global _service
    if _service is None:
        _service = LeanService()
        atexit.register(_service.close)
    _service.start()
    return _service


def _service_rows(mode: str, cases: list, timeout: float | None) -> list:
    """Every case of this module goes through here (`tests/contract_input_recorder.py` wraps it)."""
    return _started().run(mode, cases, timeout=timeout)


def run(route: str, cases: list, *, timeout: float | None = None) -> tuple[int, list | None, str]:
    """(exit status, rows, stderr) for `cases` on `route` (`mode`)."""
    start, _ = _started().stderr()
    try:
        rows = _service_rows(mode(route), cases, timeout)
    except VEError as refused:
        return 2, None, refused.message
    _, stderr = _started().stderr(start)
    return (1 if any(type(r) is dict and r.get("status") == "error" for r in rows) else 0), rows, stderr


def rows(route: str, cases: list, *, timeout: float | None = None) -> list:
    """The rows of `run`; a refused batch raises its diagnostic."""
    return _service_rows(mode(route), cases, timeout)


def diagnose(unit: str, cases: list, *, timeout: float | None = None) -> list:
    """The rows `ve_diagnose <unit>` printed for `cases` (mode `diagnose`)."""
    return _service_rows("diagnose", [{**case, "unit": unit} for case in cases], timeout)


def diagnose_text(unit: str, text: str, *, timeout: float | None = None) -> list:
    """`diagnose` on a case array written as `text`, each case's members kept in their written
    order after a first member `unit`; a refused batch raises its diagnostic."""
    from ve.backends.lean_service import case_texts
    texts = case_texts(text)
    assert texts is not None and all(t.startswith("{") for t in texts), text[:200]
    member = '"unit":' + json.dumps(unit)
    texts = ["{" + member + ("," if t[1:].strip() != "}" else "") + t[1:] for t in texts]
    cases_text = "[" + ",".join(texts) + "]"
    _, response = _started().exchange("diagnose", cases_text, len(texts), timeout=timeout, texts=texts)
    if response.get("status") == "error":
        from ve.backends.relay import rejection
        raise rejection(response["code"], response["error"])
    return [entry["result"] for entry in response["results"]]


SERVICE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_service"


def completed(route, cases: list, *, text: bool = True, timeout: float | None = None):
    """`run` in the shape of the one-shot's `subprocess.run(..., capture_output=True)`: its exit
    status, its rows as the JSON text it printed (empty when the batch is refused) and its standard
    error."""
    import subprocess
    status, rows, stderr = run(route, cases, timeout=timeout)
    stdout = "" if rows is None else json.dumps(rows, ensure_ascii=False)
    return subprocess.CompletedProcess([str(route)], status, stdout if text else stdout.encode(),
                                       stderr if text else stderr.encode())


def completed_within(route, cases: list, cpu_seconds: float):
    """`completed` with the request's CPU deadline lowered to `cpu_seconds`, where the one-shot ran
    under `run_cpu_bounded` (tests/subprocesses.py): a request that needs more CPU raises
    `CheckerUnavailable` naming its mode, and is not retried (`lean_service.DEADLINES`)."""
    from ve.backends import lean_service
    name = mode(route)
    saved = lean_service.DEADLINES[name]
    lean_service.DEADLINES[name] = (cpu_seconds / max(len(cases), 1), 0.0)
    try:
        return completed(route, cases)
    finally:
        lean_service.DEADLINES[name] = saved
