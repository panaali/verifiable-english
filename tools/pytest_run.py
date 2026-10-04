"""The one way to start a nested pytest run (tools, conformance harnesses and tests).

The gate runs pytest with plugin autoload off (PYTEST_DISABLE_PLUGIN_AUTOLOAD=1), and its
children inherit that, so a nested run that relies on an autoloaded plugin (xdist's `-n`,
a conftest hook of xdist) fails in the gate though it passes on a developer's machine.
Every nested run therefore turns autoload off itself and names the plugins it uses:
it behaves the same in both places. tests/test_gate.py fails on a `-m pytest` command
built anywhere else."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

PLUGINS = ("-p", "xdist.plugin", "-p", "hypothesis.extra.pytestplugin")
# Ambient settings that would change what a nested run loads or selects.
AMBIENT = ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")


def pytest_command(python: Sequence[str], *arguments: str) -> list[str]:
    """`python -m pytest` with the suite's plugins named; `python` is the interpreter
    command (`[sys.executable]`, or `["uv", "run", ..., "python"]`)."""
    return [*python, "-m", "pytest", *PLUGINS, *arguments]


def pytest_environment(env: Mapping[str, str]) -> dict[str, str]:
    """`env` with plugin autoload off and no ambient pytest options."""
    return {**{name: value for name, value in env.items() if name not in AMBIENT},
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
