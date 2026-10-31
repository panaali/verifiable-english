"""Measure one chunk of a test file under a plain pytest run: its wall time and the process's peak RSS (eff-20261030-1).

    uv run pytest -p tools.bench.chunk_probe --bench-chunk 2/4 -n 0 tests/test_x.py

Sets the chunk variable of tools/test_chunks.py before the suite's own `pytest_configure` reads it (so the suite's
hook keeps that chunk, exactly as in a selected run, where the selector sets it), and prints one line at the end:
`bench-chunk <i>/<k>: peak RSS <self> MiB (largest child <children> MiB)`. For runners that pass pytest arguments
but no environment (the Mac test runner). Measurement only: nothing in the suite or the gate loads it.
"""
from __future__ import annotations

import os
import resource
import sys

import pytest

from tools import test_chunks


def pytest_addoption(parser):
    parser.addoption("--bench-chunk", default=None, help="run only chunk <i>/<k> of the collected tests")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    value = config.getoption("--bench-chunk")
    if value is not None:
        test_chunks.setting(value)
        os.environ[test_chunks.VARIABLE] = value


def mebibytes(maxrss: int) -> float:
    """ru_maxrss in MiB: bytes on macOS, KiB on Linux."""
    return round(maxrss / (1024 * 1024 if sys.platform == "darwin" else 1024), 1)


def pytest_terminal_summary(terminalreporter, config):
    own = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    children = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    terminalreporter.write_line(f"bench-chunk {config.getoption('--bench-chunk') or 'whole'}: peak RSS "
                                f"{mebibytes(own)} MiB (largest child {mebibytes(children)} MiB)")
