"""A stale or incomplete batch gate cannot be reported as a pass."""
from __future__ import annotations

from copy import deepcopy

import pytest

from tools.batch_evidence import REQUIRED_STAGES, problems


HEAD = "a" * 40
GATE = {"commit_sha": HEAD, "dirty": False, "status": "passed", "stages": list(REQUIRED_STAGES),
        "counts": {"passed": 1, "rust_passed": 1}}
AB = {"head_commit": HEAD, "unlisted": 0, "unavailable_both": {},
      "records": {f"{name}/default": 1 for name in
                  ("probe", "conformance", "readings", "pilots", "discourse", "rights", "quantity")}}
LATENCY = {"head_commit": HEAD, "pass": True,
           "samples": {"readings": {"base_cpu_ms": 1, "head_cpu_ms": 1}}}


def test_complete_head_evidence_passes():
    errors = problems(HEAD, GATE, AB, LATENCY)
    assert errors == []


@pytest.mark.parametrize("which,change", [
    ("gate", {"commit_sha": "b" * 40}),
    ("gate", {"dirty": True}),
    ("gate", {"stages": list(REQUIRED_STAGES[:-1])}),
    ("comparison", {"head_commit": "b" * 40}),
    ("comparison", {"records": {"probe/default": 1}}),
    ("comparison", {"unavailable_both": {"readings/default": 1}}),
    ("latency", {"head_commit": "b" * 40}),
    ("latency", {"samples": {}}),
    ("latency", {"samples": {"readings": {"base_cpu_ms": 1, "head_cpu_ms": 1.21}}}),
])
def test_stale_or_incomplete_evidence_fails(which, change):
    values = {"gate": deepcopy(GATE), "comparison": deepcopy(AB), "latency": deepcopy(LATENCY)}
    values[which].update(change)
    assert problems(HEAD, values["gate"], values["comparison"], values["latency"])
