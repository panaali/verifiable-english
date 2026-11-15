"""Load a use case's script with its own sibling modules, apart from every other use case's.

The use cases import their siblings by bare names (`translation`, `run`, `reference`, `stage0`, ...), and
several use cases share those names. A test that puts one use case's directory on `sys.path` and imports
its script must not reuse another use case's module already in `sys.modules`, and must not leave its own
behind for the next test. The sibling names are every `*.py` stem in the directory, read from the tree,
so a new sibling module is covered without editing a list.
"""
from __future__ import annotations

import importlib.util
import sys
from contextlib import contextmanager
from pathlib import Path


def sibling_names(directory: Path) -> frozenset[str]:
    """The bare module names the use case in `directory` can import: one per `*.py` file in it."""
    return frozenset(path.stem for path in Path(directory).glob("*.py"))


@contextmanager
def usecase_scope(directory: Path):
    """While open: `directory` is first on `sys.path` and none of its sibling names is in `sys.modules`
    unless imported from it. On exit both are as they were (`sys.path` whole, whatever the script added to
    it): other use cases' modules come back, its own leave."""
    directory = str(directory)
    names = sibling_names(Path(directory))
    saved = {name: sys.modules.pop(name) for name in names if name in sys.modules}
    path = list(sys.path)
    sys.path.insert(0, directory)
    try:
        yield
    finally:
        sys.path[:] = path  # the scripts put their own directories on `sys.path` too
        for name in names:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


def load_script(path: Path, alias: str):
    """Execute the use case script at `path` as module `alias` inside its use case's scope; the scope is
    closed again when this returns (siblings it imports at load stay bound in the module's globals)."""
    path = Path(path)
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    with usecase_scope(path.parent):
        spec.loader.exec_module(module)
    return module
