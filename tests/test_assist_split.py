"""AR-9 split the assist recovery and session modules; these pin what the split must keep.

Every name the two modules defined is still importable from them, the moved code reaches
the module names callers set or replace only through the facade, and every method has one
owner, with the methods the assurance manifest reviews still defined where it names them.
"""
from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path

import pytest

import ve.assist.recovery as recovery
import ve.assist.session as session
from ve.assist.recovery import RecoveryService
from ve.assist.session import AssistSession

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {
    recovery: ("ve.assist.recovery_journal", "ve.assist.recovery_replay", "ve.assist.recovery_commands"),
    session: ("ve.assist.session_state", "ve.assist.session_proposals", "ve.assist.session_views"),
}
# The module-level names each module defined before the split.
DEFINED = {
    recovery: ("RECOVERY_VERSION", "MAX_REPLIES", "TASK_SECONDS", "MAX_PROPOSALS", "PROPOSAL_SECONDS",
               "STATES", "_digest", "DocumentAdapter", "GlossaryAdapter", "ProposerAdapter",
               "nearest_wordings", "Unit", "_Observations", "_InvalidLedger", "_canonical", "LEDGER_KEYS",
               "DIVERGED", "RecoveryService", "COMMANDS"),
    session: ("SESSION_FORMAT", "TOOL_VERSION", "ORIGINS", "DEFAULT_OPTIONS", "AssistError",
              "LedgerReplayError", "_now", "_sha", "config_digest", "_ident", "_names", "_predicates_of",
              "_symbols_of", "_conjuncts", "_constants_of", "Node", "AssistSession"),
}
# Module names that tests and callers set or replace on the facade; moved code must not bind its own.
SEAMED = {
    recovery: {"OPERATION_SECONDS": "_operation_seconds", "checked_wording": "_checked_wording",
               "evaluate": "_evaluate", "formula_to_data": "_formula_to_data",
               "formula_from_data": "_formula_from_data"},
    session: {"prove_entailment": None, "check_entailment_certificate": None, "ground_countermodel": None,
              "find_countermodel": None, "check_countermodel": None},
}
# Methods that read the session seams above stay on AssistSession in session.py.
SESSION_DECISIONS = ("_decide", "_entails", "_check", "_lean_replays", "_lean_refutes", "_validity")


def _bound_names(module_name: str, *, imports: bool = True) -> set[str]:
    """Names a module binds at module level: definitions, assignments and (unless excluded) imports."""
    tree = ast.parse(Path(importlib.import_module(module_name).__file__).read_text())
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)) and imports:
            names |= {(alias.asname or alias.name).split(".")[0] for alias in node.names}
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names |= {target.id for target in node.targets if isinstance(target, ast.Name)}
    return names


@pytest.mark.parametrize("module,name", [(m, n) for m, names in DEFINED.items() for n in names],
                         ids=lambda v: getattr(v, "__name__", v))
def test_every_name_the_module_defined_is_still_importable_from_it(module, name):
    family = [module.__name__, *FAMILIES[module]]
    owners = [m for m in family if name in _bound_names(m, imports=False)]
    assert len(owners) == 1, owners
    value = vars(importlib.import_module(owners[0]))[name]
    assert getattr(module, name) is value
    if isinstance(value, type) or callable(value):
        assert value.__module__ == owners[0]


@pytest.mark.parametrize("module_name", [m for family in FAMILIES.values() for m in family])
def test_moved_code_does_not_bind_the_names_the_facade_owns(module_name):
    facade = next(m for m, family in FAMILIES.items() if module_name in family)
    assert not _bound_names(module_name) & set(SEAMED[facade])


@pytest.mark.parametrize("name,seam", sorted(SEAMED[recovery].items()))
def test_each_recovery_seam_reads_the_facade_name_when_called(monkeypatch, name, seam):
    marker = object()
    if name == "OPERATION_SECONDS":
        monkeypatch.setattr(recovery, name, marker)
        assert RecoveryService._operation_seconds() is marker
        return
    calls = []
    monkeypatch.setattr(recovery, name, lambda *args, **kwargs: calls.append((args, kwargs)) or marker)
    assert getattr(RecoveryService, seam)(1, "two", three=3) is marker
    assert calls == [((1, "two"), {"three": 3})]


def test_session_decisions_stay_on_the_class_that_reads_the_session_names():
    for name in SESSION_DECISIONS:
        assert name in vars(AssistSession), name
        assert getattr(AssistSession, name).__module__ == "ve.assist.session"


@pytest.mark.parametrize("cls", [RecoveryService, AssistSession], ids=lambda c: c.__name__)
def test_every_member_has_one_owner(cls):
    owners = {}
    for klass in cls.__mro__[:-1]:
        for name in vars(klass):
            if not (name.startswith("__") and name.endswith("__")):
                owners.setdefault(name, []).append(klass.__name__)
    assert {name: where for name, where in owners.items() if len(where) > 1} == {}
    assert len(cls.__mro__) == 5


def test_reviewed_broad_handlers_stay_where_the_manifest_names_them():
    manifest = json.loads((ROOT / "ve/assurance-manifest.json").read_text())["reviewed_broad_handlers"]
    classes = {"ve/assist/recovery.py": RecoveryService, "ve/assist/session.py": AssistSession}
    reviewed = [key.split(":") for key in manifest if key.split(":")[0] in classes]
    assert len(reviewed) == 6
    for path, qualname in reviewed:
        class_name, method = qualname.split(".")
        cls = classes[path]
        assert class_name == cls.__name__ and method in vars(cls), qualname
