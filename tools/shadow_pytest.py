"""Pytest plugin for the pytest corpora of Stage 3 shadow mode (loaded with -p).

At the end of the session the controlling process writes ``{"cases": N}`` to
``VE_SHADOW_CASES``: the number of tests that ran (passed, failed or skipped),
which ``tools/shadow_run.py`` records as the run's ``cases`` (docs/spec/mig3.md 2.8).
Under pytest-xdist the workers report to the controller, which alone writes.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

_ran: set[str] = set()


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and not report.passed):
        _ran.add(report.nodeid)


def pytest_sessionfinish(session, exitstatus):
    target = os.environ.get("VE_SHADOW_CASES")
    if target and not hasattr(session.config, "workerinput"):
        Path(target).write_text(json.dumps({"cases": len(_ran)}) + "\n")
