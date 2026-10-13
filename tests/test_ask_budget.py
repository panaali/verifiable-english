"""F4 (qa-q2 review): the plan's `ask` budget (Q2.6: Lean CPU at most 2 s) is a pass gate, met on U3 and A1. The
class, not the example: `ask` replayed each decided row's certificate citations once per reader of the row's key
(the relevant-set search, every group, every line, three renders), so its cost grew with rows times readers; the
answer now builds them once (`VE.Ask.memoTable`, `memoRead`). The figure is Lean's own CPU time on a warm service,
which load does not inflate."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ASK_CPU_BUDGET = 2.0  # seconds of Lean CPU per `ask` request (docs/spec/question-answering-PLAN.md, Q2.6)


def _measure():
    spec = importlib.util.spec_from_file_location("question_answering_measure",
                                                  ROOT / "tools/question_answering_measure.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("ident", ["U3", "A1"])
def test_ask_meets_the_cpu_budget(ident):
    from ve.backends.lean_service import DEFAULT_EXECUTABLE, LeanService
    measure = _measure()
    _, _, ask = measure.service_case(ident)
    with LeanService(DEFAULT_EXECUTABLE) as service:
        found = measure.measure_service(service, "ask", ask)
    if found["cpu_s"] is None:
        pytest.skip("the platform does not report the service's CPU time")
    assert found["cpu_s"] <= ASK_CPU_BUDGET, found
