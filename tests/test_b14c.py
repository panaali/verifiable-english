"""Batch 14c: n-ary definitions have one Lean owner on the core family."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

from ve import Environment, FiniteModel
from ve.backends.validation import family_in_scope, model_in_scope
from ve.definitions import compile_definitions
from ve.profiles import SPEC_REVISION
from tests.subprocesses import HANG_TIMEOUT


ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "lean/.lake/build/bin/ve_conformance"


def case():
    env = {
        "language": "ve.core@0.2",
        "profiles": ["closure@0", "definitions@0", "nary@0", "relational-fol@0"],
        "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {"s": {"description": "items"}},
            "constants": {},
            "predicates": {
                "base": {"arguments": ["s"] * 3, "description": "base"},
                "derived": {
                    "arguments": ["s"] * 3,
                    "description": "derived",
                    "defined": {
                        "arguments": ["s"] * 3,
                        "body": ["atom", "base", [["var", 2], ["var", 1], ["var", 0]]],
                    },
                },
            },
        },
    }
    model = {"complete": True, "domains": {"s": ["a", "b"]}, "constants": {},
             "relations": {"base": [["a", "a", "b"]]}}
    return env, model


def route(cases):
    result = subprocess.run([str(ROUTE), "route", "-"], input=json.dumps(cases), text=True,
                            capture_output=True, check=False, timeout=HANG_TIMEOUT)
    assert result.returncode in (0, 1), result.stderr
    return json.loads(result.stdout)


def test_nary_background_is_lean_regenerated_and_ordered():
    env, _ = case()
    row, = route([{"id": "bg", "kind": "background", "environment": env}])
    assert row["status"] == "ok"
    assert row["generators"] == ["definitions"]
    assert row["premises"][0][0:2] == ["forall", "s"]
    body = row["premises"][0]
    for _ in range(3):
        body = body[2]
    assert body[0] == "and"
    assert body[1][1][:2] == ["atom", "derived"]


def test_nary_derived_table_is_checked_by_lean():
    env, model = case()
    formula = ["exists", "s", ["exists", "s", ["exists", "s",
               ["atom", "derived", [["var", 2], ["var", 1], ["var", 0]]]]]]
    cases = [{"id": str(i), "kind": "evaluate", "environment": env,
              "model": {**model, "relations": {"base": rows}}, "ast": [formula]}
             for i, rows in enumerate(([["a", "a", "b"]], []))]
    rows = route(cases)
    assert [row.get("values") for row in rows] == [[True], [False]]


def test_nary_dependencies_are_ordered_before_table_computation():
    env, model = case()
    predicates = env["vocabulary"]["predicates"]
    higher = {"arguments": ["s"] * 3, "description": "higher",
              "defined": {"arguments": ["s"] * 3,
                          "body": ["atom", "derived", [["var", 2], ["var", 1], ["var", 0]]]}}
    env["vocabulary"]["predicates"] = {"higher": higher, **predicates}
    background, value = route([
        {"id": "bg", "kind": "background", "environment": env},
        {"id": "ev", "kind": "evaluate", "environment": env, "model": model,
         "ast": [["exists", "s", ["exists", "s", ["exists", "s",
                  ["atom", "higher", [["var", 2], ["var", 1], ["var", 0]]]]]]]},
    ])
    assert background["status"] == "ok"
    assert [entry[1][1][1] for entry in (background["premises"][0][2][2][2],
                                        background["premises"][1][2][2][2])] == ["derived", "higher"]
    assert value["values"] == [True]


def test_python_routes_nary_definitions_to_lean(monkeypatch):
    env, model = case()
    built = Environment(env)
    assert model_in_scope(built) and family_in_scope(built)
    from ve import definitions

    def forbidden(*args, **kwargs):
        raise AssertionError("the retired Python n-ary definition fallback ran")

    monkeypatch.setattr(definitions, "_compile_python", forbidden)
    ordered = compile_definitions(built, built.definition_entries, version=built.environment_id)
    assert [definition.name for definition in ordered] == ["derived"]
    assert FiniteModel.from_dict(built, model).relations["derived"] == {("a", "a", "b")}
