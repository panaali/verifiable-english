"""pytest plugin: the CPU seconds each test spends, its own process and the children it reaped.

Loaded by tools/bench/suite_time.py (`-p tools.bench.cpu_per_test`); each process appends
`{"nodeid", "cpu"}` lines to `VE_TEST_CPU_LOG`. CPU, unlike a test's elapsed time, is
what a loaded machine has to find for the test. A measurement, never a test criterion.
"""
import json
import os
import resource

import pytest


def _cpu():
    own, children = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    started = _cpu()
    yield
    log = os.environ.get("VE_TEST_CPU_LOG")
    if log:
        with open(log, "a") as stream:
            stream.write(json.dumps({"nodeid": item.nodeid, "cpu": round(_cpu() - started, 3)}) + "\n")
