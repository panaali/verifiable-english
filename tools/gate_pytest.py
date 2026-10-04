"""Minimal pytest event recorder for tools/gate.py (loaded with -p).

The gate runs pytest twice: once serially with --collect-only, where this plugin records
the collection (every collected, selected and deselected ID and every collection report),
and once under xdist, where the controller records each test's result (xdist forwards the
workers' reports) and the IDs each worker collected. Workers write nothing."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


def pytest_configure(config):
    config._ve_gate_events = {"collected": [], "selected": [], "deselected": [],
                              "collection_reports": [], "tests": {}, "workers": {}}


def pytest_itemcollected(item):
    # This fires before collection_modifyitems hooks can remove tests silently.
    _EVENTS["collected"].append(item.nodeid)


def pytest_collection_finish(session):
    _EVENTS["selected"] = [item.nodeid for item in session.items]


def pytest_collectreport(report):
    if report.failed or report.skipped:
        _EVENTS["collection_reports"].append({"nodeid": report.nodeid,
                                               "outcome": report.outcome,
                                               "reason": str(report.longrepr)})


def pytest_deselected(items):
    # The active config is attached to each item; the hook runs after collection.
    if items:
        items[0].config._ve_gate_events["deselected"].extend(item.nodeid for item in items)


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_node_collection_finished(node, ids):
    # The xdist controller: the final collection of one worker.
    _EVENTS["workers"][node.gateway.id] = list(ids)


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
    if hasattr(session.config, "workerinput"):  # an xdist worker: the controller records
        return
    path = Path(os.environ["VE_GATE_PYTEST_RESULT"])
    path.write_text(json.dumps(_EVENTS, indent=2, sort_keys=True) + "\n")
