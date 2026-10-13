"""Batch 14c: n-ary definitions have one Lean owner on the core family."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import subprocess

import pytest

from ve import Environment, FiniteModel
from ve.backends.validation import family_in_scope, model_in_scope
from ve.backends.service_schema import Invalid, check_row
from ve.definitions import compile_definitions
from ve.profiles import SPEC_REVISION
from tests.subprocesses import HANG_TIMEOUT


ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "lean/.lake/build/bin/ve_conformance"
METERED = ROOT / "lean/.lake/build/bin/ve_metered"


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


def test_nary_background_relay_refuses_missing_or_extra_generated_rows():
    env, _ = case()
    request = {"id": "bg", "kind": "background", "environment": env}
    row, = route([request])
    check_row("route", row, request, 0)
    for field in ("background", "premises", "generators"):
        for value in ([], row[field] + [row[field][0]]):
            mutant = deepcopy(row)
            mutant[field] = value
            with pytest.raises(Invalid):
                check_row("route", mutant, request, 0)
    mutant = deepcopy(row)
    mutant["background"][0] = ["top"]
    with pytest.raises(Invalid):
        check_row("route", mutant, request, 0)


def test_nary_derived_table_is_checked_by_lean():
    env, model = case()
    formula = ["exists", "s", ["exists", "s", ["exists", "s",
               ["atom", "derived", [["var", 2], ["var", 1], ["var", 0]]]]]]
    cases = [{"id": str(i), "kind": "evaluate", "environment": env,
              "model": {**model, "relations": {"base": rows}}, "ast": [formula]}
             for i, rows in enumerate(([["a", "a", "b"]], []))]
    rows = route(cases)
    assert [row.get("values") for row in rows] == [[True], [False]]


def test_nary_metered_zero_budget_is_unknown():
    env, model = case()
    cases = [{"id": str(limit), "kind": "evaluate-budgeted", "environment": env,
              "model": model, "ast": [["top"]], "max_evaluations": limit}
             for limit in (0, 100000)]
    result = subprocess.run([str(METERED), "-"], input=json.dumps(cases), text=True,
                            capture_output=True, check=False, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert [(row["evaluation"]["status"], row["evaluation"]["value"])
            for row in rows] == [("ResourceLimit", None), ("Satisfied", True)]


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


# ---------------------------------------------------------------- lf-14c review F1: one definition order

def mixed(definitions):
    """The case's environment with its defined predicates `(name, arity, mentions)` of arity 1
    or 3 in place of `derived`: a unary body mentions unary predicates, an n-ary body any."""
    env, _ = case()
    predicates = env["vocabulary"]["predicates"]
    del predicates["derived"]
    predicates["u"] = {"arguments": ["s"], "description": "u"}
    arities = {name: arity for name, arity, _ in definitions}

    def mention(name, arity):
        if arities.get(name, 1) == 1:
            return ["unary", name, ["var", 0]]
        return ["atom", name, [["var", index] for index in reversed(range(arity))]]

    for name, arity, mentions in definitions:
        body = ["unary", "u", ["var", 0]] if arity == 1 else ["atom", "base", [["var", 2], ["var", 1], ["var", 0]]]
        for other in mentions:
            body = ["and", body, mention(other, arity)]
        predicates[name] = {"arguments": ["s"] * arity, "description": name,
                            "defined": {"arguments": ["s"] * arity, "body": body}}
    return env


ORDERS = {
    # The review's reproducer: independent n-ary `aaa` and unary `zzz`.
    "independent": ([("aaa", 3, []), ("zzz", 1, [])], ["aaa", "zzz"]),
    # A ready n-ary definition comes before a unary one with a larger name, and after the unary one it mentions.
    "interleaved": ([("p3", 3, []), ("q1", 1, []), ("a3", 3, ["q1"]), ("b1", 1, [])], ["b1", "p3", "q1", "a3"]),
    "chain": ([("c3", 3, ["b3"]), ("b3", 3, ["a1"]), ("a1", 1, []), ("z1", 1, [])], ["a1", "b3", "c3", "z1"]),
}


@pytest.mark.parametrize("name", sorted(ORDERS))
def test_definitions_share_one_dependency_order_across_arities(monkeypatch, name):
    """Lean placed every unary or binary definition before every n-ary one; Python orders all of
    them in one dependency order. The Lean-owned compilation, the retained Python elaborator and
    the route's regenerated Background (every caller of `Core.Layers.background`) agree on it."""
    from ve import definitions
    definitions_, expected = ORDERS[name]
    raw = mixed(definitions_)
    env = Environment(raw)
    compiled = compile_definitions(env, env.definition_entries, version=env.environment_id)
    retained = definitions._compile_python(env, env.definition_entries, version=env.environment_id)
    assert [d.name for d in compiled] == [d.name for d in retained] == expected
    row, = route([{"id": "bg", "kind": "background", "environment": raw}])
    premises = [p for p, g in zip(row["premises"], row["generators"], strict=True) if g == "definitions"]
    assert [definitions._lean_definition(env, p).name for p in premises] == expected


# ---------------------------------------------------------------- lf-14c review F2: direct entries' diagnostics

def _outcome(call):
    """`("ok", names)`, or the exception's class and text without the code prefix the relay writes."""
    from ve.errors import VEError
    try:
        return "ok", tuple(d.name for d in call())
    except VEError as exc:
        return type(exc).__name__, str(exc).removeprefix(f"{type(exc).__name__}: ")


def _paths(value, at=()):
    yield at
    if type(value) is list:
        for index, item in enumerate(value):
            yield from _paths(item, (*at, index))
    elif type(value) is dict:
        for key, item in value.items():
            yield from _paths(item, (*at, key))


def _put(value, at, item):
    if not at:
        return item
    value = deepcopy(value)
    node = value
    for key in at[:-1]:
        node = node[key]
    node[at[-1]] = item
    return value


REPLACEMENTS = (7, True, None, [], {}, "x", ["bogus"], ["not"], ["reach", "plus", ["named", "u"], ["var", 0], ["var", 0]])


@pytest.mark.parametrize("target", ["derived", "v"])
def test_direct_definition_diagnostics_are_pythons(target):
    """A direct `compile_definitions` entry, n-ary (`derived`) or unary (`v`), with each node of its
    arguments and body replaced by each JSON kind, a bad tag, a short node or a Reach: the
    Lean-owned answer is the retained Python elaborator's, class and text (the review's `bogus`
    tag gave `invalid indexed formula`; a mismatched argument list lost the quoted name; a
    `null` gave the restricted reader's offset). Only VEError escapes."""
    from ve import definitions
    from ve.errors import SyntaxError as VESyntaxError
    raw, _ = case()
    raw["vocabulary"]["predicates"]["u"] = {"arguments": ["s"], "description": "u"}
    raw["vocabulary"]["predicates"]["v"] = {"arguments": ["s"], "description": "v", "defined": {
        "arguments": ["s"], "body": ["and", ["unary", "u", ["var", 0]], ["not", ["bottom"]]]}}
    env = Environment(raw)
    version = env.environment_id
    with pytest.raises(VESyntaxError, match="'bogus'"):
        compile_definitions(env, {target: {**env.definition_entries[target], "body": ["bogus"]}}, version=version)
    seed = env.definition_entries[target]
    differ = []
    for at in _paths(seed):
        for item in REPLACEMENTS:
            entries = {target: _put(seed, at, item)}
            lean = _outcome(lambda: compile_definitions(env, entries, version=version))
            python = _outcome(lambda: definitions._compile_python(env, entries, version=version))
            if lean != python:
                differ.append((at, item, lean, python))
    assert differ == []


def _rust_binary():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import rust_build
    import os
    if os.environ.get("VE_RUST_PREBUILT"):
        return Path(os.environ["VE_RUST_BINARY"])
    binary = rust_build.RELEASE_BINARY
    if not binary.is_file() or rust_build.digest(binary) not in rust_build.pinned_digests():
        pytest.skip("build the pinned Rust release binary with python3 tools/rust_build.py")
    return binary


def test_definition_arguments_mismatch_quotes_the_name_on_every_engine():
    """Python's `Definition 'derived' arguments differ from its declaration`: the Lean route
    (environment construction) and Rust quote the name as Python's `repr` does."""
    from conformance import three_way
    raw, _ = case()
    raw["vocabulary"]["predicates"]["derived"]["defined"]["arguments"] = ["s", "s"]
    expected = "Definition 'derived' arguments differ from its declaration"
    with pytest.raises(Exception) as python:
        Environment(raw)
    assert str(python.value).endswith(expected)
    rust, = three_way.run([str(_rust_binary()), "conformance"],
                          [{"id": "env", **three_way.rust_envelope(raw)}])
    assert rust["status"] == "error" and rust["error"]["message"].endswith(expected), rust
