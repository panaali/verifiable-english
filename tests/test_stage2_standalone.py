"""Standalone Lean service bindings compared with Python's public identities."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.probe_matrix import model_wire, raw_environment
from ve import Environment, FiniteModel, Top
from ve.ast import formula_to_data
from ve.backends.lean_runner import run
from ve.identity import meaning_id, source_id

SERVICE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_service"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("data@0",), ("definitions@0",),
    ("closure@0",), ("closure@0", "nary@0"), ("order@0",)])
def test_environment_and_model_ids(profiles):
    env = Environment(raw_environment(profiles))
    model = FiniteModel.from_dict(env, model_wire(env))
    case = {"id": "binding", "environment": env.to_dict()}
    assert run("environment", [case])[0]["environment_id"] == env.environment_id
    assert run("model", [{**case, "model": model.to_dict()}])[0]["model_id"] == model.model_id


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_source_and_meaning_ids():
    env = Environment(raw_environment(()))
    case = {"id": "binding", "environment": env.to_dict()}
    assert run("identity", [{**case, "kind": "source", "source": "true.\n"}])[0][
        "identity_id"] == source_id("true.\n", env)
    assert run("identity", [{**case, "kind": "meaning", "ast": formula_to_data(env, Top())}])[0][
        "identity_id"] == meaning_id(env, Top())


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("data@0",), ("definitions@0",),
    ("closure@0",), ("closure@0", "nary@0"), ("order@0",)])
def test_standalone_check_matches_python_identity(profiles):
    from ve.ast import Document, check_document, check_formula, document_to_data
    env = Environment(raw_environment(profiles))
    formula = Top()
    case = {"id": "check", "environment": env.to_dict()}
    check_formula(env, formula)
    row = run("check", [{**case, "ast": formula_to_data(env, formula)}])[0]
    assert row == {"id": "check", "status": "ok", "well_typed": True,
                   "meaning_id": meaning_id(env, formula)}
    document = Document((formula,))
    check_document(env, document)
    row = run("check", [{**case, "ast": document_to_data(env, document)}])[0]
    assert row["well_typed"] is True
    assert row["meaning_id"] == meaning_id(env, document)


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_standalone_check_rejects_undeclared_predicate():
    from ve.errors import VEError
    env = Environment(raw_environment(()))
    with pytest.raises(VEError):
        run("check", [{"id": "bad", "environment": env.to_dict(),
                       "ast": ["unary", "missing", ["const", "x"]]}])


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_public_typing_uses_standalone_lean(monkeypatch):
    from ve.ast import Document, Unary, Const, check_document, check_formula
    from ve.errors import VEError
    env = Environment(raw_environment(()))
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert check_formula(env, Top()) == Top()
    assert check_document(env, Document((Top(),))) == Document((Top(),))
    with pytest.raises(VEError):
        check_formula(env, Unary("missing", Const("x")))


def _typing_error(env, formula):
    from ve.ast import check_formula
    from ve.errors import VEError
    try:
        check_formula(env, formula)
    except VEError as exc:
        return exc.code, exc.message
    return None


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("norms@0",), ("definitions@0",), ("data@0",),
    ("closure@0",), ("closure@0", "nary@0"), ("closure@0", "nary@0", "definitions@0"),
    ("closure@0", "norms@0"), ("order@0",)])
def test_lean_typing_diagnostics_match_python(profiles, monkeypatch):
    """The decoder's rejection is named with Python's code and message."""
    from ve.ast import (Atom, Binary, Const, Eq, Exists, Forall, Named, Reach, Unary, Var)
    env = Environment(raw_environment(profiles))
    cases = [Unary("missing", Const("x")), Unary("base", Const("absent")),
             Binary("base", Const("x"), Const("x")), Forall("absent", Top()),
             Exists("item", Unary("base", Var(1))), Eq(Const("x"), Var(0))]
    if "closure@0" in profiles:
        cases += [Reach("star", Named("base"), Const("x"), Const("x")),
                  Reach("star", Named("absent"), Const("x"), Const("x"))]
    if "nary@0" in profiles:
        cases += [Atom("triple", (Const("x"), Const("x"))), Atom("absent", (Const("x"),) * 3)]
    for formula in cases:
        expected = _typing_error(env, formula)
        assert expected is not None, formula
        monkeypatch.setenv("VE_AUTHORITY", "lean")
        assert _typing_error(env, formula) == expected, formula
        monkeypatch.delenv("VE_AUTHORITY")
