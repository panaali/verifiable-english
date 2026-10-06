"""The client's response schemas are generated from their one Lean source (lf-1 recheck B).

`ve/backends/lean_service_schema/*.json` is rendered from `lean/ResponseShape/Schemas` by
`ve_response_decode` (check `schemas`) and written by `tools/response_schemas.py`; the same Lean
shapes decide responses in `ve_response_decode`. A hand-written schema file, a hand edit of a
generated one, a stale rendering and a missing file each fail the check, so the client's schemas
and the Lean side cannot be two descriptions again.
"""
from __future__ import annotations

import json
import shutil

import pytest

from tests.lean_build import lean_build
from tools import response_schemas
from ve.backends.service_schema import DIRECTORY, MODES


@pytest.fixture(scope="module")
def documents():
    return response_schemas.rendered(lean_build("ve_response_decode") / "ve_response_decode")


def test_every_schema_file_is_the_lean_rendering(documents):
    assert response_schemas.differences(documents) == []
    assert set(documents) == {f"{mode}.json" for mode in MODES} | {"common.json", "envelope.json"}


@pytest.fixture
def copy(tmp_path):
    for path in DIRECTORY.glob("*.json"):
        shutil.copy(path, tmp_path / path.name)
    return tmp_path


def _edit(path, change):
    document = json.loads(path.read_text())
    change(document)
    path.write_text(response_schemas.text(document))


def test_a_hand_edit_of_a_generated_file_is_found(documents, copy):
    """The review's soft-norms mutant as a schema edit: `environment_prime` made optional by hand."""
    _edit(copy / "soft-norms.json", lambda d: d["$defs"]["elaborate"]["required"].remove("environment_prime"))
    assert response_schemas.differences(documents, copy) == [
        "soft-norms.json: differs from its rendering (edit lean/ResponseShape/Schemas, then --write)"]


def test_a_reformatted_file_is_found(documents, copy):
    path = copy / "route.json"
    path.write_text(json.dumps(json.loads(path.read_text())))
    assert [p.split(":")[0] for p in response_schemas.differences(documents, copy)] == ["route.json"]


def test_a_hand_written_or_missing_file_is_found(documents, copy):
    (copy / "extra.json").write_text('{"$id": "extra.json", "row": true}\n')
    (copy / "diagnose.json").unlink()
    assert response_schemas.differences(documents, copy) == [
        "diagnose.json: not written", "extra.json: not rendered by the Lean source"]


def test_write_then_check_round_trips(documents, copy, monkeypatch):
    (copy / "extra.json").write_text("{}\n")
    _edit(copy / "common.json", lambda d: d["$defs"]["code"]["enum"].append("Invented"))
    monkeypatch.setattr(response_schemas, "rendered", lambda decoder: documents)
    assert response_schemas.main(["--check", "--directory", str(copy)]) == 1
    assert response_schemas.main(["--write", "--directory", str(copy)]) == 0
    assert response_schemas.main(["--check", "--directory", str(copy)]) == 0
    assert not (copy / "extra.json").exists()


def test_lean_lists_are_the_rendered_enumerations(documents):
    """Enumerations rendered from Lean lists, not copies: the handshake's modes are every mode of
    the client, in the service's order, and its codes the row code domain."""
    handshake = documents["envelope.json"]["handshake"]["properties"]
    assert [c["contains"]["const"] for c in handshake["modes"]["allOf"]] == list(MODES)
    assert handshake["codes"]["const"] == documents["common.json"]["$defs"]["code"]["enum"]
