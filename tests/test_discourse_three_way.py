"""Spec α and α′: Python and Lean resolve; Rust checks the elaborated core."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tests.test_discourse import _sample, _unit, _write
from tests.test_discourse_lean import case as lean_case, document as lean_document, env as lean_env, run as lean_run
from ve.document import check_document, load_document

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_discourse_route"
RUST = ROOT / "rust/target/release/ve"
FORMULA = ["unary", "deployed", ["const", "api"]]


def shared_environment():
    data = lean_env()
    data["vocabulary"]["sorts"].pop("document")
    data["vocabulary"]["predicates"] = {
        name: value for name, value in data["vocabulary"]["predicates"].items()
        if name in {"reviewed", "deployed", "ready"}}
    return data


@pytest.mark.parametrize("earlier_alice", [False, True], ids=["alpha", "alpha_prime"])
def test_named_reference_three_way(tmp_path, earlier_alice):
    source, front = _sample(tmp_path)
    front["environment"] = shared_environment()
    front["units"][1]["content"]["ast"] = FORMULA
    if earlier_alice:
        source = b"Api is reviewed.\nAlice is ready.\nIt is deployed.\n"
        alice = source.index(b"Alice")
        it = source.index(b"It")
        front["units"] = [
            _unit("u1", [0, alice], ["unary", "reviewed", ["const", "api"]]),
            _unit("u2", [alice, it], ["unary", "ready", ["const", "alice"]]),
            _unit("u3", [it, len(source)], FORMULA),
        ]
        front["discourse"]["names"].append(
            {"constant": "alice", "display": "Alice", "scope": "doc"})
        front["discourse"]["mentions"][0]["unit"] = "u3"
        target_unit = "u3"
    else:
        it = source.index(b"It")
        target_unit = "u2"
    front["discourse"]["anchors"][0]["span"] = [0, len(source)]
    front["discourse"]["mentions"][0]["span"] = [it, it + 2]
    front["graph"] = {"root": "claim", "nodes": [
        {"name": "claim", "ast": FORMULA, "unit": target_unit}]}
    path = _write(tmp_path, front, source)
    python = check_document(path)
    assert python["admission"]["admitted"] is True
    assert python["admission"]["report"]["root"]["ast"] == FORMULA
    assert python["reviewed_presentations"][target_unit].strip() == "Api is deployed."

    sentences = ["Api is reviewed."]
    if earlier_alice:
        sentences.append("Alice is ready.")
    sentences.append("It is deployed.")
    lean = lean_document(sentences,
        [("m1", target_unit, "It", "pronoun", {"kind": "entity", "name": "api"})],
        names=[{"constant": "api", "display": "Api", "scope": "doc"},
               *([{"constant": "alice", "display": "Alice", "scope": "doc"}]
                 if earlier_alice else [])],
        graph={"root": "claim", "nodes": [
            {"name": "claim", "ast": FORMULA, "unit": target_unit}]}, contents={target_unit: FORMULA})
    resolved = lean_run([lean_case("discourse-resolve", lean, shared_environment())])[0]
    assert resolved["status"] == "ok", resolved
    assert resolved["units"][target_unit]["formula"] == FORMULA
    assert resolved["environment_id"] == load_document(path)["environment"].environment_id
    admitted = lean_run([lean_case("admission", lean, shared_environment())])[0]
    assert admitted["status"] == "ok", admitted
    assert admitted["report"]["root"]["ast"] == FORMULA

    model = {"complete": True, "domains": {"service": ["s"], "person": ["p"]},
             "constants": {"api": "s", "alice": "p", "bob": "p"},
             "relations": {"deployed": [["s"]], "reviewed": [["s"]], "ready": []}}
    case = {"id": "alpha-prime" if earlier_alice else "alpha", "environment": {
        **shared_environment(), "profiles": ["relational-fol@0"]},
        "ast": [FORMULA], "model": model}
    rust = subprocess.run([str(RUST), "conformance"], input=json.dumps(case),
                          text=True, capture_output=True, timeout=30)
    assert rust.returncode == 0, rust.stdout + rust.stderr
    checked = json.loads(rust.stdout)[0]
    assert checked["ast"] == [FORMULA]
    assert checked["value"] is True
