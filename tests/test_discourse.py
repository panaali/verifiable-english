"""Regression tests for the conservative Python discourse adapter."""
import json

import pytest

from tests.test_views import vocabulary
from ve.discourse import _joint
from ve.document import check_document, load_document
from ve.errors import VEError
from ve.profiles import LANGUAGE, SPEC_REVISION


def _environment():
    data = vocabulary()
    data["language"] = LANGUAGE
    data.pop("profile")
    data["profiles"] = ["relational-fol@0", "ve.discourse@1"]
    data["spec_revision"] = SPEC_REVISION
    return data


def _unit(uid, span, content):
    return {"id": uid, "span": span, "kind": "asserted", "meaning": "specified",
            "support": "assumption", "content": {"ast": content}}


def _write(tmp_path, front, source):
    path = tmp_path / "discourse.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + source)
    return path


def _sample(tmp_path):
    source = b"Api is reviewed.\nIt is deployed.\n"
    cut = source.index(b"It")
    front = {"format": "ve-document@2", "environment": _environment(),
             "units": [_unit("u1", [0, cut], ["unary", "reviewed", ["const", "api"]]),
                       _unit("u2", [cut, len(source)], ["unary", "active", ["const", "api"]])],
             "discourse": {"version": "ve.discourse@1", "anchors": [
                 {"id": "doc", "kind": "document", "label": "Policy", "span": [0, len(source)]}],
                 "names": [{"constant": "api", "display": "Api", "scope": "doc"}],
                 "mentions": [{"id": "m1", "unit": "u2", "span": [cut, cut + 2],
                               "form": "pronoun", "target": {"kind": "entity", "name": "api"}}]}}
    return source, front


def test_profile_adapter_and_explicit_expansion(tmp_path):
    source, front = _sample(tmp_path)
    path = _write(tmp_path, front, source)
    doc = load_document(path)
    assert doc["environment"].profiles == ("relational-fol@0",)
    result = check_document(path)
    assert result["format"] == "ve-document@2"
    assert result["reviewed_presentations"]["u2"].strip() == "Api is deployed."
    assert result["joint_choices"]["count"] == 1
    assert result["references"][0]["status"] == "resolved"


def test_retarget_and_content_tampering_fail(tmp_path):
    source, front = _sample(tmp_path)
    front["discourse"]["mentions"][0]["target"]["name"] = "alice"
    with pytest.raises(VEError, match="InaccessibleTarget"):
        load_document(_write(tmp_path, front, source))
    front["discourse"]["mentions"][0]["target"]["name"] = "api"
    front["units"][1]["content"]["ast"] = ["unary", "reviewed", ["const", "api"]]
    with pytest.raises(VEError, match="ManifestMismatch: bound.u2"):
        load_document(_write(tmp_path, front, source))


def test_rejects_partial_overlap_and_stale_version(tmp_path):
    source, front = _sample(tmp_path)
    cut = source.index(b"It")
    front["discourse"]["mentions"].append({"id": "m2", "unit": "u2",
        "span": [cut + 1, cut + 5], "form": "pronoun",
        "target": {"kind": "entity", "name": "api"}})
    with pytest.raises(VEError, match="overlap"):
        load_document(_write(tmp_path, front, source))
    front["discourse"]["mentions"].pop()
    front["discourse"]["definitions_version"] = "old"
    with pytest.raises(VEError, match="StaleTarget: definitions@old"):
        load_document(_write(tmp_path, front, source))


def test_joint_choices_correlate_and_detect_empty():
    active = [{"id": key, "version": 1, "status": "open", "readings":
               [{"id": "a"}, {"id": "b"}]} for key in ("r1", "r2")]
    block = {"constraints": [
        {"kind": "requires", "a": ["r1", 1, "a"], "b": ["r2", 1, "a"]},
        {"kind": "requires", "a": ["r1", 1, "b"], "b": ["r2", 1, "b"]}]}
    assert _joint(block, active)["count"] == 2
    block["constraints"].extend(
        {"kind": "excludes", "a": ["r1", 1, x], "b": ["r2", 1, y]}
        for x in ("a", "b") for y in ("a", "b"))
    with pytest.raises(VEError, match="InvalidCompatibility"):
        _joint(block, active)
    assert _joint({}, [])["choices"] == [{}]
