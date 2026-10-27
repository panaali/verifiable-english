"""AR-16b split `ve/readings_verdicts.py` into the package `ve/readings_verdicts/`; these pin what the split must keep.

No name has two owners in the package, every name callers import is still importable from `ve.readings_verdicts`
as the owner's own object, each module imports only the modules before it and never the package itself, and no
test patches a name on the package that a module of it looks up (such a patch no longer reaches the code it meant
to replace).
"""
from __future__ import annotations

import ast
from collections import Counter
import importlib
from pathlib import Path

import pytest

import ve.readings_verdicts as V

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "ve/readings_verdicts"
# The modules in their order: each imports only modules before it (the package `__init__` imports them all).
MODULES = ("route", "binding", "choice", "superposed", "enumerated")
# The names other modules, tests and tools import from `ve.readings_verdicts` (an `ast` scan of the repository at
# the split), and the module's public names.
EXPORTED = (
    "BUDGET", "Enumerated", "INVALID_ANSWER", "PAIR_LABEL", "PENDING", "Pending", "ROW_PIECES", "SHOWN_IN",
    "Superposed", "_ChoiceDocument", "_FilledChoiceDocument", "_FilledView", "_Frame", "_check_answer",
    "_check_english", "_check_sup_answer", "_dead_certificates", "_need", "_public_sup_conflict", "_shown_of",
    "dead_finding", "relayed",
)
PATCHERS = ("setattr", "delattr", "object")  # `monkeypatch.setattr`, `monkeypatch.delattr`, `patch.object`


def _tree(name: str) -> ast.Module:
    return ast.parse((PACKAGE / f"{name}.py").read_text())


def _defined(name: str) -> set[str]:
    out = set()
    for node in _tree(name).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
        elif isinstance(node, ast.Assign):
            out |= {target.id for target in node.targets if isinstance(target, ast.Name)}
    return out


def _globals_read(name: str) -> set[str]:
    """The module-level names of `ve.readings_verdicts.<name>` its code reads: each one a patch must set on that
    module."""
    tree = _tree(name)
    bound = {(alias.asname or alias.name) for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
             for alias in node.names} | _defined(name)
    return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
            and node.id in bound}


def package_patches(path: Path) -> list[tuple[int, str]]:
    """(line, name) of every patch in `path` on the package `ve.readings_verdicts` itself:
    `monkeypatch.setattr(V, "name")`, `patch.object(V, "name")` and the like, where `V` is bound to
    `ve.readings_verdicts`, and the string forms `"ve.readings_verdicts.name"`."""
    tree = ast.parse(path.read_text())
    aliases = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "ve" and node.level == 0:
            aliases |= {alias.asname or alias.name for alias in node.names if alias.name == "readings_verdicts"}
        elif isinstance(node, ast.Import):
            aliases |= {alias.asname for alias in node.names if alias.name == "ve.readings_verdicts" and alias.asname}
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and node.args
                and (isinstance(node.func, ast.Attribute) and node.func.attr in (*PATCHERS, "patch")
                     or isinstance(node.func, ast.Name) and node.func.id == "patch")):
            continue
        first, second = node.args[0], node.args[1] if len(node.args) > 1 else None
        if isinstance(first, ast.Name) and first.id in aliases and isinstance(second, ast.Constant):
            out.append((node.lineno, second.value))
        elif (isinstance(first, ast.Constant) and isinstance(first.value, str)
              and first.value.startswith("ve.readings_verdicts.") and first.value.count(".") == 2):
            out.append((node.lineno, first.value.rsplit(".", 1)[1]))
    return out


def test_the_modules_are_the_package():
    assert {path.stem for path in PACKAGE.glob("*.py")} == {"__init__", *MODULES}


def test_no_name_is_defined_in_two_modules():
    """One owner per definition: a name two modules define would be two copies, one of them unpatched by a test."""
    owners = Counter(name for module in (*MODULES, "__init__") for name in _defined(module) if name != "__all__")
    assert [name for name, count in owners.items() if count > 1] == []


@pytest.mark.parametrize("name", EXPORTED)
def test_every_name_callers_import_is_the_owners_object(name):
    [owner] = [module for module in MODULES if name in _defined(module)]
    value = vars(importlib.import_module(f"ve.readings_verdicts.{owner}"))[name]
    assert getattr(V, name) is value
    if callable(value):
        assert value.__module__ == f"ve.readings_verdicts.{owner}"


def test_context_and_the_public_names_stay_the_packages():
    assert V.context.__module__ == "ve.readings_verdicts"
    assert V.__all__ == ["BUDGET", "Enumerated", "PENDING", "Pending", "Superposed", "context"]
    assert all(hasattr(V, name) for name in V.__all__)


@pytest.mark.parametrize("name", MODULES)
def test_each_module_imports_only_the_modules_before_it(name):
    siblings = {node.module for node in _tree(name).body
                if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module}
    assert siblings <= set(MODULES[:MODULES.index(name)]), siblings


@pytest.mark.parametrize("name", MODULES)
def test_no_module_imports_the_package_itself(name):
    """A module that imported `ve.readings_verdicts` would run the package `__init__`, and with it every sibling: it
    would join every cycle any sibling is on."""
    for node in ast.walk(_tree(name)):
        if isinstance(node, ast.ImportFrom):
            assert not (node.level == 1 and node.module is None), ast.unparse(node)
            assert not (node.level == 2 and node.module == "readings_verdicts"), ast.unparse(node)
            assert node.module != "ve.readings_verdicts", ast.unparse(node)
        elif isinstance(node, ast.Import):
            assert all(alias.name != "ve.readings_verdicts" for alias in node.names), ast.unparse(node)


def test_the_scanner_finds_a_patch_on_the_package(tmp_path):
    source = tmp_path / "test_x.py"
    source.write_text('from ve import readings_verdicts as V\nfrom ve.readings_verdicts import superposed\n'
                      'def test(monkeypatch):\n    monkeypatch.setattr(V, "_ChoiceDocument", None)\n'
                      '    monkeypatch.setattr(superposed, "_ChoiceDocument", None)\n'
                      '    monkeypatch.setattr("ve.readings_verdicts._check_answer", None)\n'
                      '    monkeypatch.setattr("ve.readings_verdicts.binding._check_answer", None)\n'
                      '    with patch.object(V, "BUDGET"), patch("ve.readings_verdicts._dead_certificates"):\n'
                      '        pass\n')
    assert package_patches(source) == [(4, "_ChoiceDocument"), (6, "_check_answer"), (8, "BUDGET"),
                                       (8, "_dead_certificates")]


def test_no_test_patches_the_package_where_a_module_looks_the_name_up():
    """A patch on `ve.readings_verdicts.<name>` replaces the package's attribute only; the module that reads `<name>`
    holds its own binding, so the patch must name that module (`ve.readings_verdicts.superposed._ChoiceDocument`)."""
    read = {name: module for module in MODULES for name in _globals_read(module)}
    stale = [f"{path.relative_to(ROOT)}:{line}: patch ve.readings_verdicts.{read[name]}.{name}, "
             f"not ve.readings_verdicts.{name}"
             for folder in ("tests", "tools", "conformance") for path in sorted((ROOT / folder).rglob("*.py"))
             for line, name in package_patches(path)
             if name in read]
    assert stale == []
