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
