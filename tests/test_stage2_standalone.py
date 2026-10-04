"""Standalone Lean service bindings compared with Python's public identities."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.lean_wording import lean_wording
from tests.probe_matrix import model_wire, raw_environment
from ve import Environment, FiniteModel, Top
from ve.ast import formula_to_data
from ve.backends.relay import decide as run
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
    """The decoder's rejection is named with Python's code and Lean's message (`lean_wording`)."""
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
        assert _typing_error(env, formula) == lean_wording(*expected), formula
        monkeypatch.delenv("VE_AUTHORITY")


def _legacy_environment(kind):
    from ve.environment import (LANGUAGE, PROFILE, SPEC_REVISION as V0_REV, CLOSURE_LANGUAGE,
                                CLOSURE_PROFILES, CLOSURE_REVISION, ORDER_PROFILES, ORDER_REVISION)
    raw = raw_environment(())
    raw.pop("profiles")
    if kind == "v0":
        raw.update(language=LANGUAGE, spec_revision=V0_REV, profile=PROFILE)
    else:
        raw.update(language=CLOSURE_LANGUAGE,
                   spec_revision=CLOSURE_REVISION if kind == "closure" else ORDER_REVISION,
                   profiles=list(CLOSURE_PROFILES if kind == "closure" else ORDER_PROFILES))
    return Environment(raw)


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("kind", ["v0", "closure", "order"])
def test_lean_typing_on_legacy_envelopes_matches_python(kind, monkeypatch):
    from ve.ast import Binary, Const, Forall, Unary, Var, check_formula
    env = _legacy_environment(kind)
    formula = Forall("item", Unary("base", Var(0)))
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert check_formula(env, formula) == formula
    row = run("check", [{"id": "c", "environment": env.to_dict(), "ast": formula_to_data(env, formula)}])[0]
    assert row["meaning_id"] == meaning_id(env, formula)
    monkeypatch.delenv("VE_AUTHORITY")
    for bad in (Unary("missing", Const("x")), Binary("base", Const("x"), Const("x"))):
        expected = _typing_error(env, bad)
        monkeypatch.setenv("VE_AUTHORITY", "lean")
        assert _typing_error(env, bad) == lean_wording(*expected)
        monkeypatch.delenv("VE_AUTHORITY")


def _nested(leaves):
    from ve.ast import And
    level = [Top() for _ in range(leaves)]
    while len(level) > 1:
        level = [And(level[i], level[i + 1]) if i + 1 < len(level) else level[i]
                 for i in range(0, len(level), 2)]
    return level[0]


def _negated(formula, times):
    from ve.ast import Not
    for _ in range(times):
        formula = Not(formula)
    return formula


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("kind", ["current", "order", "closure", "closure+nary", "v0"])
def test_lean_typing_budget_diagnostics_match_python(kind, monkeypatch):
    """Budget rejections are named where `_Checker` meets them, with its message."""
    from ve.ast import Add, And, Const, Document, Le, Num, Unary, check_document
    from ve.errors import VEError
    profiles = {"current": (), "order": ("order@0",), "closure": ("closure@0",),
                "closure+nary": ("closure@0", "nary@0")}
    env = _legacy_environment("v0") if kind == "v0" else Environment(raw_environment(profiles[kind]))
    deep = _negated(Top(), 64)
    cases = [deep, _negated(_nested(5000), 2), And(Unary("missing", Const("x")), deep),
             And(deep, Unary("missing", Const("x"))), Document((_nested(3000), _nested(3000)))]
    if kind == "order":
        term = Num(0)
        for _ in range(64):
            term = Add(Num(1), term)
        cases.append(Le(term, Num(0)))

    def error(case):
        if type(case) is Document:
            try:
                check_document(env, case)
            except VEError as exc:
                return exc.code, exc.message
            return None
        return _typing_error(env, case)

    for case in cases:
        expected = error(case)
        assert expected is not None and expected[0] in ("ResourceLimit", "UnknownSymbol")
        monkeypatch.setenv("VE_AUTHORITY", "lean")
        assert error(case) == lean_wording(*expected)
        monkeypatch.delenv("VE_AUTHORITY")
