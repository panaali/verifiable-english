"""Minimal pytest event recorder for tools/gate.py (loaded with -p).

The gate runs pytest twice: once serially with --collect-only, where this plugin records
the collection (every collected, selected and deselected ID and every collection report),
and once under xdist, where the controller records each test's result and its seconds (setup +
call + teardown; xdist forwards the workers' reports) and the IDs each worker collected. Workers
write nothing. A quarantined test that failed runs once more, serially, recorded the same way.
No run stops early: the plugin refuses --maxfail, -x and --stepwise."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


def pytest_configure(config):
    # A gate never stops early: every collected test runs and has a result (docs/TESTING.md).
    early = [option for option, on in (("--maxfail/-x", config.getoption("maxfail", 0)),
                                       ("--stepwise", config.getoption("stepwise", False)),
                                       ("--stepwise-skip", config.getoption("stepwise_skip", False))) if on]
    if early:
        raise pytest.UsageError(f"the gate runs every test; it refuses {', '.join(early)}")
    config._ve_gate_events = {"collected": [], "selected": [], "deselected": [],
                              "collection_reports": [], "tests": {}, "seconds": {}, "workers": {}}


def pytest_itemcollected(item):
    # This fires before collection_modifyitems hooks can remove tests silently.
    _EVENTS["collected"].append(item.nodeid)


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    """Apply gate selectors from a file so long parametrized IDs never enter argv."""
    listing = os.environ.get("VE_GATE_PYTEST_IDS_FILE")
    if not listing:
        return
    selectors = json.loads(Path(listing).read_text())
    if not isinstance(selectors, list) or not selectors or any(type(s) is not str for s in selectors):
        raise pytest.UsageError("invalid gate selection file")

    def chosen(nodeid):
        return any(nodeid == selector or nodeid.startswith(selector + "::") or
                   nodeid.startswith(selector + "[") for selector in selectors)

    kept = [item for item in items if chosen(item.nodeid)]
    removed = [item for item in items if not chosen(item.nodeid)]
    if removed:
        config.hook.pytest_deselected(items=removed)
        items[:] = kept
    # As with pytest's own node selectors, unrelated tests in an assigned file
    # are outside this run's collection, not policy deselections.
    _EVENTS["collected"] = [node for node in _EVENTS["collected"] if chosen(node)]
    _EVENTS["deselected"] = [node for node in _EVENTS["deselected"] if chosen(node)]


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
    # Scheduling data only (tools/test_schedule.py): no outcome depends on it.
    _EVENTS["seconds"][report.nodeid] = _EVENTS["seconds"].get(report.nodeid, 0.0) + report.duration
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
