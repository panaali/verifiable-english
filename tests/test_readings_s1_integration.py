"""S1 content admission through the ordinary document entry point."""
from __future__ import annotations

import pytest

from tests.test_document import unit, write_doc
from tests.test_readings_s1_lean import env_k, k1_document
from ve.document import check_document, load_document
from ve.errors import VEError
from ve.readings import s1_content_meaning_id
from ve.softnorms import SoftEnvironment


def source_document(tmp_path, *, invalid=False):
    raw = env_k()
    wire, _ = k1_document(raw)
    env = SoftEnvironment(raw)
    for candidate in wire["reading_sets"][0]["readings"]:
        candidate["meaning_id"] = s1_content_meaning_id(env, "rs1", candidate)
    if invalid:
        wire["reading_sets"][0]["readings"][1]["admission"]["distinguishing_models"]["strict"] = "wrong"
    source = b"Avoid deception.\n"
    path = write_doc(tmp_path, source, [unit("u1", 0, len(source), "norm")],
                     environment_json=raw, reading_sets=wire["reading_sets"])
    return path


def test_content_set_is_admitted_by_lean_in_a_document(tmp_path):
    path = source_document(tmp_path)
    loaded = load_document(path)
    assert loaded["readings_s1"]["content_bearing"] is True
    pair = loaded["readings_s1"]["sets"][0]["pairs"][0]["pair"]
    assert pair["separated"] and pair["witness"] == "default"
    report = check_document(path)
    assert report["coverage"]["bytes_by_status"] == {"OPEN": len(b"Avoid deception.\n")}


def test_content_set_rejects_a_false_situation_id(tmp_path):
    with pytest.raises(VEError, match="distinguishing model id does not match model"):
        load_document(source_document(tmp_path, invalid=True))
