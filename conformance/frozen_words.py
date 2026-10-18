"""The Python producers of situation and point wording before Q2.4 moved them to Lean (`VE.Words`), for the A/B.

The sources are kept in Git history so the production tree has one implementation (as `frozen_norm_defaults.py`
does); no product entry point imports this module. `ve_frozen` is a package view of `ve` at `REVISION`: the
modules of `FROZEN` are that revision's source (each pinned by its SHA-256), every other module is the current
`ve` module of the same name, so a frozen function computes the old English from the same inputs as the current
code. `tools/words_ab.py` compares the two on the readings, norm-defaults and pilot corpora.
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.abc
import importlib.util
from pathlib import Path
import subprocess
import sys
from types import ModuleType

_ROOT = Path(__file__).resolve().parents[1]
REVISION = "41887e90"
FROZEN = {
    "norm_defaults_english": "0ffbeb82354c0b52a8d80d244b29fb26b76beecf7566a2c23aa888bbd6346085",
    "norm_english": "48a92121a1825f99774fc0e130a5f830baebe0acd720ffc19ab6d7b1b6d60778",
    "readings_s2_wording": "5e0d10bdca8b8998b92e800b379cb0459830a36fc567b630b09c860f1afd3739",
    "readings_s2_english": "68886fd5d05be3af3cf95b07034c7964829746345256844a46df1091a24b96c1",
    "readings_route": "46ad643506bf8bf275221b50fd07c214a12e9316573c2c348f2206fdd9c57865",
    "norm_defaults": "b48607867a7a3241a52e2b373955402bf95947f1c845d793aa1b05be3f73d936",
}
PACKAGE = "ve_frozen"


def _source(name: str) -> bytes:
    source = subprocess.check_output(["git", "show", f"{REVISION}:ve/{name}.py"], cwd=_ROOT)
    if hashlib.sha256(source).hexdigest() != FROZEN[name]:
        raise RuntimeError(f"the frozen source of ve/{name}.py changed")
    return source


class _Finder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """`ve_frozen.X`: the frozen source of `X` when `X` is in `FROZEN`, else the current `ve.X` itself."""

    def __init__(self):
        self._specs = {}

    def find_spec(self, fullname, path=None, target=None):
        if fullname != PACKAGE and not fullname.startswith(PACKAGE + "."):
            return None
        return importlib.util.spec_from_loader(fullname, self, is_package=fullname == PACKAGE
                                               or fullname.removeprefix(PACKAGE + ".") not in FROZEN
                                               and importlib.util.find_spec("ve." + fullname.removeprefix(
                                                   PACKAGE + ".")).submodule_search_locations is not None)

    def create_module(self, spec):
        if spec.name == PACKAGE:
            return None
        name = spec.name.removeprefix(PACKAGE + ".")
        if name in FROZEN:
            return None
        current = importlib.import_module("ve." + name)
        self._specs[current.__name__] = current.__spec__
        return current

    def exec_module(self, module):
        if module.__name__ == PACKAGE:
            module.__path__ = []
            return
        if module.__name__ in self._specs:
            # an alias: the import system set its `__spec__` to the alias's; the current module keeps its own
            module.__spec__ = self._specs.pop(module.__name__)
            return
        name = module.__name__.removeprefix(PACKAGE + ".")
        if name in FROZEN and module.__name__.startswith(PACKAGE):
            module.__package__ = PACKAGE
            exec(compile(_source(name), f"{REVISION}:ve/{name}.py", "exec"), module.__dict__)


if not any(isinstance(finder, _Finder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _Finder())


def module(name: str) -> ModuleType:
    """The frozen module `ve/<name>.py` (a name of `FROZEN`)."""
    if name not in FROZEN:
        raise KeyError(name)
    return importlib.import_module(f"{PACKAGE}.{name}")
