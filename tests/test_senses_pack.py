"""Transport and provenance checks for the Python part of senses B2."""

import json

import pytest

from ve.senses import bundled_pack, load_pack, review_status
from ve.errors import VEError
from ve.wire import canonical_json, loads_json


def test_fixture_pack_matches_spec_wordings():
    pack = loads_json(bundled_pack("fixtures@1"))
    assert pack["format"] == "ve.sense-pack@1"
    assert pack["name"] == "fixtures@1"
    assert {(item["word"], item["index"], item["wording"])
            for item in pack["senses"]} == {
        ("funny", 1, "{0} is funny"), ("funny", 2, "{0} is funny"),
        ("odd", 1, "{0} is odd"), ("odd", 2, "{0} is odd"),
        ("tells", 1, "{0} tells {1}"), ("deployed", 1, "{0} is deployed"),
        ("reviewed", 1, "{0} is reviewed"), ("reviewed", 2, "{0} is reviewed"),
        ("access", 1, "{0} may access {1}"),
    }
    assert {sort["name"]: sort["letter"] for sort in pack["sorts"]} == {
        "joke": "J", "service": "S", "person": "P", "number": "N",
        "principal": "A", "resource": "R",
    }
    assert [(sense["word"], sense["index"], sense["gloss"])
            for sense in pack["senses"]] == [
        ("funny", 1, "amusing"), ("funny", 2, "strange"),
        ("odd", 1, "strange"), ("odd", 2, "uneven"),
        ("tells", 1, "says aloud"), ("deployed", 1, "live"),
        ("reviewed", 1, "checked"), ("reviewed", 2, "rated"),
        ("access", 1, "read"),
    ]
    assert pack["senses"][-1]["negative"] == "{0} may not access {1}"


def test_loader_preserves_untrusted_bytes_for_lean(tmp_path):
    for raw in (b'{"description":null}', b'{"unknown":true}', b'not json'):
        path = tmp_path / "pack.json"
        path.write_bytes(raw)
        assert load_pack(path) == raw


def test_generic_canonicalization_is_stable_without_pack_schema():
    pack = loads_json(bundled_pack("fixtures@1"))
    reformatted = json.dumps(pack, sort_keys=True, indent=7).encode()
    assert canonical_json(loads_json(reformatted)) == canonical_json(pack)
    changed = json.loads(json.dumps(pack))
    changed["senses"][0]["gloss"] = "hilarious"
    assert canonical_json(changed) != canonical_json(pack)


def test_fixture_pack_is_unreviewed():
    assert review_status("fixtures@1", "id-from-lean") == "unreviewed"


def test_review_requires_matching_identity_and_complete_record(tmp_path, monkeypatch):
    monkeypatch.setattr("ve.senses.files", lambda _: tmp_path)
    path = tmp_path / "reviewed-packs.json"
    record = {"name": "fixtures@1", "dictionary_id": "id-from-lean",
              "reviewer": "Reviewer", "date": "2026-10-05", "scope": "fixture wordings"}
    path.write_text(json.dumps([record]))
    assert review_status("fixtures@1", "id-from-lean") == "reviewed"
    assert review_status("fixtures@1", "different-id") == "unreviewed"
    path.write_text(json.dumps([{**record, "scope": ""}]))
    assert review_status("fixtures@1", "id-from-lean") == "unreviewed"
    path.write_text("not json")
    assert review_status("fixtures@1", "id-from-lean") == "unreviewed"


@pytest.mark.parametrize("name", ["", ".", "..", "../other", "a/b", "a\\b", 7, True, None])
def test_bundled_pack_rejects_path_escape(name):
    with pytest.raises(VEError, match="Invalid sense pack name"):
        bundled_pack(name)
