"""Batch 16d: norm-defaults and fenced documents are Lean document answers."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from ve import document as D
from ve.backends import relay
from ve.backends.service_schema import Context, Invalid, ROWS
from ve.errors import CheckerUnavailable, InvalidModel

SEED = Path(__file__).parent / "data/readings_s2/constitution-nd-readings.ve.md"
PILOTS = Path(__file__).parent / "data/tarch-b8"


def pilot(name, digest):
    """Use the two pilot blobs recorded for 16d, independent of moving pilot refs."""
    raw = (PILOTS / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    return raw


def test_norm_defaults_readings_and_english_fence_are_decided_by_lean(monkeypatch):
    raw = SEED.read_bytes()
    expected = D._report(D._load_document(raw, SEED, None))
    assert D._lean_answer(raw, True) is not None
    monkeypatch.setattr(D, "_load_document", lambda *_: pytest.fail("retained document loader ran"))
    assert D.check_document(SEED) == expected


def test_norm_defaults_coverage_uses_lean_report():
    raw = SEED.read_bytes()
    expected = D._report(D._load_document(raw, SEED, None))["coverage"]
    assert D.check_document(SEED)["coverage"] == expected


def test_pending_reading_metadata_is_checked_by_lean(tmp_path):
    raw = SEED.read_bytes()
    meta, rest = raw.split(b"\n---\n", 1)
    front = json.loads(meta[4:])
    models = front["reading_sets"][0]["models"]
    models[next(iter(models))]["relations"]["human"] = 7
    path = tmp_path / "invalid-pending.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front, ensure_ascii=False).encode() + b"\n---\n" + rest)
    assert D._lean_answer(path.read_bytes(), True) is None
    with pytest.raises(InvalidModel, match="relation must be an array"):
        D.check_document(path)


def test_coupled_pilot_reading_plan_matches_prior_path(tmp_path):
    raw = pilot("nd-op.ve.md", "77a7f103a063f57ff1c22fef1feb3d911d00b040dc8f188a119c5ffa925f6824")
    path = tmp_path / "nd-op.ve.md"
    path.write_bytes(raw)
    expected = D._report(D._load_document(raw, path, None))["reading_plan"]
    assert D.check_document(path)["reading_plan"] == expected


def test_labeled_pending_pilot_is_lean_decided(tmp_path, monkeypatch):
    raw = pilot("translation-without-content.ve.md", "4c10dfcb2deac28417836f1367bba340847e0dc723b2ab9b97f29fa421105199")
    path = tmp_path / "without-content.ve.md"
    path.write_bytes(raw)
    expected = D._report(D._load_document(raw, path, None))
    assert D._lean_answer(raw, True) is not None
    monkeypatch.setattr(D, "_load_document", lambda *_: pytest.fail("retained loader ran"))
    assert D.check_document(path) == expected


def test_norm_content_is_bound_to_the_authored_node(monkeypatch):
    raw = SEED.read_bytes()
    row = D._lean_answer(raw, False)
    forged = deepcopy(row)
    node = forged["units"][1]["content"]["norm"]
    node["name"] += "-forged"
    env = D.Environment(D._split(raw)[0]["environment"])
    forged["units"][1]["meaning_id"] = D.digest(
        f"ve-meaning-{env.identity_version}\n",
        {"environment_id": env.environment_id, "ast": forged["units"][1]["content"]})
    # The forged node is itself typed and has a matching identity. Only request binding refuses it.
    ROWS["document"][0](forged, Context({"id": "document", "document": raw.decode(), "admit": False}), {})
    monkeypatch.setattr(relay, "answer", lambda *_: (forged, None))
    with pytest.raises(CheckerUnavailable, match="not bound to the document sent"):
        D.load_document(SEED)


def test_every_norm_field_is_typed_and_every_row_bound():
    raw = SEED.read_bytes()
    row = D._lean_answer(raw, True)
    meta, source, _ = D._split(raw)
    declared = list(D._parts(meta["units"]))
    case = Context({"id": "document", "document": raw.decode(), "admit": True})
    schema = ROWS["document"][0]
    schema(row, case, {})

    def replace(path, value):
        changed = deepcopy(row)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return changed

    def leaves(value, path):
        yield path, value
        if type(value) is dict:
            for key, child in value.items():
                yield from leaves(child, (*path, key))
        elif type(value) is list:
            for index, child in enumerate(value):
                yield from leaves(child, (*path, index))

    paths = list(leaves(row["units"][1]["content"], ("units", 1, "content")))
    assert len(paths) >= 13
    for path, value in paths:
        wrong = (7 if type(value) in (str, bool) else True if type(value) is int else
                 [] if type(value) is dict else {} if type(value) is list else 7)
        changed = replace(path, wrong)
        try:
            schema(changed, case, {})
        except Invalid:
            continue
        with pytest.raises((ValueError, CheckerUnavailable), match="not bound|disagrees"):
            D._bind_document_answer(source, meta, declared, changed)

    for units in ([], row["units"] + [deepcopy(row["units"][0])]):
        changed = deepcopy(row)
        changed["units"] = units
        with pytest.raises(ValueError, match="disagrees"):
            D._bind_document_answer(source, meta, declared, changed)
    for value in (True, "1", -1, 0):
        changed = replace(("coverage", "residual", "assumptions"), value)
        try:
            schema(changed, case, {})
        except Invalid:
            continue
        with pytest.raises(ValueError, match="disagrees"):
            D._bind_document_answer(source, meta, declared, changed)
