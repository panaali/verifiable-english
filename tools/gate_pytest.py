"""Minimal pytest event recorder for tools/gate.py (loaded with -p)."""
from __future__ import annotations

import json
import os
from pathlib import Path

def pytest_configure(config):
    config._ve_gate_events = {"collected": [], "deselected": [], "tests": {}}


def pytest_collection_modifyitems(session, config, items):
    config._ve_gate_events["collected"] = [item.nodeid for item in items]


def pytest_deselected(items):
    # The active config is attached to each item; the hook runs after collection.
    if items:
        items[0].config._ve_gate_events["deselected"].extend(item.nodeid for item in items)


def pytest_runtest_logreport(report):
    # Reports do not retain Config. The plugin module stores its single-session state.
    if report.when not in ("setup", "call", "teardown"):
        return
    row = _EVENTS["tests"].setdefault(report.nodeid, {"outcome": "passed"})
    if report.failed:
        row.update(outcome="failed", reason=str(report.longrepr))
    elif report.skipped:
        if hasattr(report.longrepr, "message"):
            reason = report.longrepr.message
        else:
            reason = str(report.longrepr)
        row.update(outcome="skipped", reason=reason)


def pytest_sessionstart(session):
    global _EVENTS
    _EVENTS = session.config._ve_gate_events


def pytest_runtest_setup(item):
    progress = os.environ.get("VE_GATE_PYTEST_PROGRESS")
    if progress:
        Path(progress).write_text(item.nodeid + "\n")


def pytest_sessionfinish(session, exitstatus):
    path = Path(os.environ["VE_GATE_PYTEST_RESULT"])
    path.write_text(json.dumps(_EVENTS, indent=2, sort_keys=True) + "\n")
