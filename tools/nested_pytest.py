"""The one builder of a pytest command that another process runs: a test, the gate, or a tool.

`tools/gate.py` runs the suite with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, so a nested command that relied
on an autoloaded plugin (`-n` without `-p xdist`) exited 4 under the gate and passed everywhere else.
A command built here names every plugin it uses, and its environment disables autoloading and drops
the outer run's pytest settings, so it runs the same under the gate, inside an xdist worker and from a
shell. `tests/test_nested_pytest.py` fails on a pytest command built anywhere else.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import sys

# The plugins every run loads, by module: the gate's suite and every nested run.
PLUGINS = ("hypothesis.extra.pytestplugin",)
# The xdist plugin, by its entry-point name; loaded for more than one worker, `auto` or `xdist=True`.
XDIST = "xdist"
# The options only a plugin loaded here may add; callers pass `workers` and `dist` instead.
PLUGIN_OPTIONS = ("-n", "--numprocesses", "--dist", "--maxprocesses", "-d")
# Environment names a nested run never inherits: pytest's own settings and the xdist worker
# identity of the outer run, and the outputs of the outer run's gate and profile plugins.
AMBIENT_PREFIXES = ("PYTEST_", "VE_GATE_PYTEST_")
AMBIENT_NAMES = ("VE_TEST_PROFILE_DIR",)


def command(arguments: Sequence[str], *, workers: int | str = 1, dist: str | None = None,
            xdist: bool = False, python: Sequence[str] = (sys.executable,)) -> list[str]:
    """`python -m pytest` with PLUGINS, then `arguments`. With more than one worker, `auto` (the
    load-aware count of tests/conftest.py) or `xdist=True` (one worker that is still an xdist
    worker, for runs that read xdist's reports), the run is on xdist (with `--dist=dist`)."""
    if not (workers == "auto" or type(workers) is int and workers >= 1):
        raise ValueError(f"workers must be a positive int or 'auto', not {workers!r}")
    arguments = [str(argument) for argument in arguments]
    for index, argument in enumerate(arguments):
        if argument.split("=", 1)[0] in PLUGIN_OPTIONS or (argument.startswith("-n") and argument[2:].isdigit()):
            raise ValueError(f"{argument!r}: pass workers= or dist= instead")
        if argument == "-p" and index + 1 < len(arguments) and arguments[index + 1] in (XDIST, *PLUGINS):
            raise ValueError(f"-p {arguments[index + 1]}: the builder loads it")
    plugins = [option for name in PLUGINS for option in ("-p", name)]
    parallel = (["-p", XDIST, "-n", str(workers), *([f"--dist={dist}"] if dist else [])]
                if xdist or workers != 1 else [])
    return [*python, "-m", "pytest", *plugins, *parallel, *arguments]


def environment(base: Mapping[str, str], **settings: str) -> dict[str, str]:
    """`base` without the ambient pytest names, plus `settings`, with plugin autoloading disabled."""
    env = {name: value for name, value in base.items()
           if not name.startswith(AMBIENT_PREFIXES) and name not in AMBIENT_NAMES}
    env.update(settings)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    return env
