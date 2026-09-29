"""The Gate 2 inventory lint (tools/inventory_lint.py)."""
from __future__ import annotations

import ast

from tools import inventory_lint as lint

# Retained consumers of check_argument, the class-A body that the graph mode's
# adapter replaces; nothing else may import a class-A body.
AWAITING_GRAPH_ADAPTER = {
    ("ve.argument_fixtures:<module>", "ve.argument:check_argument"),
    ("ve.assist.session:AssistSession._do_status", "ve.argument:check_argument"),
    ("ve.english:parse_english_argument", "ve.argument:check_argument"),
}


def test_only_the_graph_adapter_is_outstanding():
    found, excepted = lint.violations()
    assert {(row["consumer"], row["provider"]) for row in found} == AWAITING_GRAPH_ADAPTER
    assert all(row["reason"] for row in excepted)


def test_every_recorded_exception_is_still_used():
    _, excepted = lint.violations()
    used = {(row["consumer"].split(":")[0], row["consumer"].split(":")[1],
             row["provider"].split(":")[0], row["provider"].split(":")[1]) for row in excepted}
    assert used == set(lint.EXCEPTIONS)


def test_every_body_exists_in_its_module():
    from pathlib import Path
    for module, bodies in lint.BODIES.items():
        tree = ast.parse((Path(lint.ROOT) / (module.replace(".", "/") + ".py")).read_text())
        defined = {name for name, _ in lint.owners(tree)} | {
            node.name for node in tree.body if isinstance(node, ast.ClassDef)}
        assert bodies <= defined, (module, bodies - defined)


def uses_of(source, module="ve.example"):
    return {(consumer, provider, symbol) for consumer, provider, symbol, _ in
            lint.uses(module, ast.parse(source))}


def test_function_local_module_level_and_attribute_imports_are_seen():
    source = '''
from .norms import _check_conflict_python
from . import background

def local():
    from .ast import _Checker
    return _Checker

def module_level():
    return _check_conflict_python

def attribute():
    return background.validate_background
'''
    found = uses_of(source)
    assert ("local", "ve.ast", "_Checker") in found
    assert ("module_level", "ve.norms", "_check_conflict_python") in found
    assert ("attribute", "ve.background", "validate_background") in found
