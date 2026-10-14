"""The `--maxfail` of an agent's selected run (tools/select_tests.py --run), loaded with -p.

pytest's own `--maxfail` counts every failed test, a quarantined one too, while the run's exit status
does not count the quarantined ones (tools/quarantine.py): a quarantined failure could stop the run
early and the run still pass, with the tests after it never run. This plugin stops the run after
`--ve-maxfail N` failed tests outside the `--ve-quarantined` node IDs, the same tests the exit status
counts, and refuses pytest's own `--maxfail` and `-x` next to it. `select_tests.stop_options` is the one
place that builds these options, for the plain run and for each recorded unit alike.
"""
from __future__ import annotations

import pytest


def pytest_addoption(parser):
    group = parser.getgroup("ve selected run")
    group.addoption("--ve-maxfail", type=int, default=0, metavar="N",
                    help="stop after N failed tests outside the quarantine (0: never)")
    group.addoption("--ve-quarantined", action="append", default=[], metavar="NODEID",
                    help="a quarantined test: its failure does not count towards --ve-maxfail")


def pytest_configure(config):
    limit = config.getoption("ve_maxfail")
    if limit < 0:
        raise pytest.UsageError("--ve-maxfail is 0 or a positive count")
    if limit and config.getoption("maxfail", 0):
        raise pytest.UsageError("--ve-maxfail replaces --maxfail/-x, which would count quarantined failures")
    if limit:
        config.pluginmanager.register(MaxFail(limit, config.getoption("ve_quarantined")), "ve-maxfail")


class MaxFail:
    """Counts the failed tests outside the quarantine, as pytest counts its own `--maxfail` (a failed
    collection or test phase that is not an expected failure), but each test once."""

    def __init__(self, limit: int, quarantined: list[str]):
        self.limit, self.quarantined = limit, frozenset(quarantined)
        self.failed: set[str] = set()
        self.session = None

    def pytest_sessionstart(self, session):
        self.session = session

    def pytest_runtest_logreport(self, report):
        if not report.failed or hasattr(report, "wasxfail") or report.nodeid in self.quarantined:
            return
        self.failed.add(report.nodeid)
        if len(self.failed) >= self.limit and self.session is not None:
            self.session.shouldfail = (f"stopping after {len(self.failed)} failed tests outside the quarantine "
                                       f"(--maxfail {self.limit})")

    pytest_collectreport = pytest_runtest_logreport
