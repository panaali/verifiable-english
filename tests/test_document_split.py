"""AR-16a split `ve/document.py` into the package `ve/document/`; these pin what the split must keep.

Every name the module defined has one owner in the package, every name callers import is still importable from
`ve.document` as the owner's own object, each module imports only the modules before it, and no test patches a name
on the package that a module of it looks up (such a patch no longer reaches the code it meant to replace).
"""
from __future__ import annotations

import ast
import importlib
from pathlib import Path
import subprocess
import sys

import pytest

from tests.subprocesses import HANG_TIMEOUT
import ve.document as D

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "ve/document"
# The modules in their order: each imports only modules before it (the package `__init__` imports them all).
MODULES = ("source", "containers", "lean", "load", "report", "render", "cli")
# The module-level names `ve/document.py` defined before the split.
DEFINED = (
    "MAX_DOCUMENT_BYTES", "SUPPORTS", "STATUSES", "_RIGHTS_KINDS", "_body", "front_matter", "_split", "_meaning",
    "_quantity_content", "_content", "_wire_unit", "_parts", "_english_fences", "_document_id", "_soft_contents",
    "_readings_routes", "_s1_attached", "_environment", "stored_identities", "base_environment", "load_document",
    "_load", "_document_case", "_lean_answer", "_spans_a_strict_fence", "_names_a_model_member", "_lean_document",
    "_BLOCK_LINES", "_bind_document_answer", "_soft_bound", "_no_lone_surrogate", "_load_document", "_free_norms",
    "_defaults_environment", "_reading_plan", "_fixed_and_active", "_fixed_premises", "_checking_environment",
    "_unresolved_norm_reading", "_assertion_disjunctions", "_rights_block", "_rights_source_units",
    "_content_bearing", "_lower_route", "_lower_rights_document", "_lower_soft_document", "_content_environment",
    "_rights_units", "_in_rights_source", "_rights_report", "coverage_defaults", "coverage", "_profile_lines",
    "_check_narrowing_choices", "quantity_admission_input", "_check_quantity_document", "check_document",
    "_check_document", "_report", "_graph_nodes", "render_document", "main",
)
# The names other modules, tests, tools and scripts import from `ve.document` (an `ast` scan of the repository at the
# split): the public names, the private ones they read, and three names the module imported.
EXPORTED = (
    "MAX_DOCUMENT_BYTES", "STATUSES", "SUPPORTS", "_bind_document_answer", "_body", "_check_narrowing_choices",
    "_checking_environment", "_content", "_content_bearing", "_document_case", "_english_fences", "_environment",
    "_fixed_and_active", "_fixed_premises", "_lean_answer", "_lean_document", "_load_document", "_meaning", "_parts",
    "_report", "_s1_attached", "_split", "base_environment", "check_document", "coverage", "coverage_defaults",
    "front_matter", "load_document", "main", "quantity_admission_input", "render_document", "stored_identities",
)
IMPORTED = {"Environment": "ve.environment", "digest": "ve.wire", "rights_meaning_id": "ve.readings"}
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
    """The module-level names of `ve.document.<name>` its code reads: each one a patch must set on that module."""
    tree = _tree(name)
    bound = {(alias.asname or alias.name) for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
             for alias in node.names} | _defined(name)
    return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
            and node.id in bound}


def package_patches(path: Path) -> list[tuple[int, str]]:
    """(line, name) of every patch in `path` on the package `ve.document` itself: `monkeypatch.setattr(D, "name")`,
    `patch.object(D, "name")` and the like, where `D` is bound to `ve.document`, and the string forms
    `"ve.document.name"`."""
    tree = ast.parse(path.read_text())
    aliases = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "ve" and node.level == 0:
            aliases |= {alias.asname or alias.name for alias in node.names if alias.name == "document"}
        elif isinstance(node, ast.Import):
            aliases |= {alias.asname for alias in node.names if alias.name == "ve.document" and alias.asname}
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
              and first.value.startswith("ve.document.") and first.value.count(".") == 2):
            out.append((node.lineno, first.value.rsplit(".", 1)[1]))
    return out


@pytest.mark.parametrize("name", DEFINED)
def test_every_name_the_module_defined_has_one_owner(name):
    owners = [module for module in MODULES if name in _defined(module)]
    assert len(owners) == 1, owners


@pytest.mark.parametrize("name", EXPORTED)
def test_every_name_callers_import_is_the_owners_object(name):
    [owner] = [module for module in MODULES if name in _defined(module)]
    value = vars(importlib.import_module(f"ve.document.{owner}"))[name]
    assert getattr(D, name) is value
    if callable(value):
        assert value.__module__ == f"ve.document.{owner}"


@pytest.mark.parametrize("name", sorted(IMPORTED))
def test_the_imported_names_callers_read_are_their_modules_objects(name):
    assert getattr(D, name) is getattr(importlib.import_module(IMPORTED[name]), name)


@pytest.mark.parametrize("name", MODULES)
def test_each_module_imports_only_the_modules_before_it(name):
    siblings = {node.module for node in _tree(name).body
                if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module}
    assert siblings <= set(MODULES[:MODULES.index(name)]), siblings


def test_the_scanner_finds_a_patch_on_the_package(tmp_path):
    source = tmp_path / "test_x.py"
    source.write_text('from ve import document as D\nfrom ve.document import load\n'
                      'def test(monkeypatch):\n    monkeypatch.setattr(D, "_load_document", None)\n'
                      '    monkeypatch.setattr(load, "_load_document", None)\n'
                      '    monkeypatch.setattr("ve.document._lean_answer", None)\n'
                      '    monkeypatch.setattr("ve.document.load._lean_answer", None)\n'
                      '    with patch.object(D, "Environment"), patch("ve.document.admit_document"):\n'
                      '        pass\n')
    assert package_patches(source) == [(4, "_load_document"), (6, "_lean_answer"), (8, "Environment"),
                                       (8, "admit_document")]


def test_no_test_patches_the_package_where_a_module_looks_the_name_up():
    """A patch on `ve.document.<name>` replaces the package's attribute only; the module that reads `<name>` holds
    its own binding, so the patch must name that module (`ve.document.load._load_document`, ...)."""
    read = {name: module for module in MODULES for name in _globals_read(module)}
    stale = [f"{path.relative_to(ROOT)}:{line}: patch ve.document.{read[name]}.{name}, not ve.document.{name}"
             for folder in ("tests", "tools", "conformance") for path in sorted((ROOT / folder).rglob("*.py"))
             for line, name in package_patches(path)
             if name in read]
    assert stale == []


def test_python_m_ve_document_runs_the_command_line():
    done = subprocess.run([sys.executable, "-m", "ve.document", "--help"], cwd=ROOT, capture_output=True,
                          text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0 and done.stdout.startswith("usage: ve document")
    assert importlib.import_module("ve.document.__main__").main is D.main  # importing it runs nothing
