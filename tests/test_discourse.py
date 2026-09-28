"""Regression tests for the conservative Python discourse adapter."""
import json

import pytest

from tests.test_views import vocabulary
from ve.discourse import _joint, _same_witness, check_joint_extensions, joint_assertion
from ve.document import check_document, load_document, render_document
from ve.errors import VEError
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.readings import check_readings
from ve.environment import Environment
from ve.ast import formula_from_data
from ve.identity import meaning_id


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
    assert "Reviewed wording: Api is deployed." in render_document(path)


def test_empty_profile_preserves_base_meanings_and_changes_document_domain(tmp_path):
    source, front = _sample(tmp_path)
    source = source.replace(b"It is deployed.", b"Api is deployed.")
    front["units"][1]["span"][1] = len(source)
    front["discourse"] = {}
    newer = load_document(_write(tmp_path, front, source))
    older = {**front, "format": "ve-document@1", "environment": _environment()}
    older["environment"]["profiles"].remove("ve.discourse@1")
    older.pop("discourse")
    prior = load_document(_write(tmp_path, older, source))
    assert newer["environment"].environment_id == prior["environment"].environment_id
    assert [u["meaning_id"] for u in newer["units"]] == [u["meaning_id"] for u in prior["units"]]
    assert newer["document_id"] != prior["document_id"]


def test_retarget_and_content_tampering_fail(tmp_path):
    source, front = _sample(tmp_path)
    front["discourse"]["mentions"][0]["target"]["name"] = "alice"
    with pytest.raises(VEError, match="InaccessibleTarget"):
        load_document(_write(tmp_path, front, source))
    front["discourse"]["mentions"][0]["target"]["name"] = "api"
    front["units"][1]["content"]["ast"] = ["unary", "reviewed", ["const", "api"]]
    with pytest.raises(VEError, match="ManifestMismatch: bound.u2"):
        load_document(_write(tmp_path, front, source))


def test_unrecorded_and_wrong_surface_slots_fail(tmp_path):
    source, front = _sample(tmp_path)
    mention = front["discourse"]["mentions"].pop()
    with pytest.raises(VEError, match="UnrecordedSlot"):
        load_document(_write(tmp_path, front, source))
    # a recorded mention on "is" leaves "It" unrecorded (the Lean route's order)
    mention["span"] = [source.index(b"is deployed"), source.index(b"is deployed") + 2]
    front["discourse"]["mentions"].append(mention)
    with pytest.raises(VEError, match="UnrecordedSlot"):
        load_document(_write(tmp_path, front, source))
    # a recorded pronoun that is no slot of its sentence
    named = source.replace(b"It is deployed.", b"Api is deployed.")
    front["units"][1]["span"][1] = len(named)
    front["discourse"]["anchors"][0]["span"] = [0, len(named)]
    verb = named.index(b"is deployed")
    front["discourse"]["mentions"][0]["span"] = [verb, verb + 2]
    with pytest.raises(VEError, match="MentionNotSlot: m1"):
        load_document(_write(tmp_path, front, named))


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


def test_prior_quantifier_blocks_bare_pronoun(tmp_path):
    source, front = _sample(tmp_path)
    source = source.replace(b"Api is reviewed.", b"A service is reviewed.")
    cut = source.index(b"It")
    front["units"][0]["span"] = [0, cut]
    front["units"][0]["content"]["ast"] = ["exists", "item",
        ["unary", "reviewed", ["var", 0]]]
    front["units"][1]["span"] = [cut, len(source)]
    front["discourse"]["anchors"][0]["span"] = [0, len(source)]
    front["discourse"]["mentions"][0]["span"] = [cut, cut + 2]
    # the competing quantifier leaves no accessible candidate (spec beta)
    with pytest.raises(VEError, match="UnresolvedReference: m1"):
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


def test_same_witness_shape_rejects_split_quantifiers():
    p = ["unary", "active", ["var", 0]]
    q = ["unary", "reviewed", ["var", 0]]
    assert _same_witness(["exists", "item", ["and", p, q]])
    assert not _same_witness(["and", ["exists", "item", p],
                              ["exists", "item", q]])


def test_joint_verdict_uses_only_compatible_choices():
    data = _environment()
    data["profiles"].remove("ve.discourse@1")
    env = Environment(data)
    p = ["unary", "active", ["const", "api"]]
    sets = [{"id": "r1", "version": 1, "status": "open", "readings": [
                {"id": "a", "kind": "asserted", "content": p},
                {"id": "b", "kind": "asserted", "content": ["not", p]}]},
            {"id": "r2", "version": 1, "status": "open", "readings": [
                {"id": "a", "kind": "asserted", "content": ["top"]},
                {"id": "b", "kind": "asserted", "content": ["top"]}]}]
    joint = _joint({"constraints": [
        {"kind": "requires", "a": ["r1", 1, "a"], "b": ["r2", 1, "a"]},
        {"kind": "requires", "a": ["r1", 1, "b"], "b": ["r2", 1, "b"]}]}, sets)
    assert check_readings(env, sets, p, joint_choices=joint)["verdict"] == "SOME"


def test_joint_premise_and_report_extension():
    data = _environment()
    data["profiles"].remove("ve.discourse@1")
    env = Environment(data)
    p = ["unary", "active", ["const", "api"]]
    q = ["unary", "reviewed", ["const", "api"]]
    sets = [{"id": key, "version": 1, "status": "open", "readings": [
        {"id": "a", "kind": "asserted", "content": p},
        {"id": "b", "kind": "asserted", "content": q}]}
        for key in ("rs5", "rs6")]
    joint = _joint({"constraints": [
        {"kind": "excludes", "a": ["rs5", 1, "a"], "b": ["rs6", 1, "b"]},
        {"kind": "excludes", "a": ["rs5", 1, "b"], "b": ["rs6", 1, "a"]}]}, sets)
    assert joint["count"] == 2
    assert joint_assertion(env, sets, joint) is not None
    report = {"root": {"name": "root"}, "assumptions": [
        {"label": "readings:rs5@1:0"}, {"label": "readings:rs6@1:0"}]}
    check_joint_extensions({}, report, joint)
    report["assumptions"][1]["label"] = "readings:rs6@1:1"
    with pytest.raises(VEError, match="InvalidCompatibility: report root"):
        check_joint_extensions({}, report, joint)
    report["assumptions"] = []
    with pytest.raises(VEError, match="InvalidCompatibility: citation 2.1"):
        check_joint_extensions({"lemmas": [{"name": "2.1", "leaves": [
            {"label": "readings:rs5@1:0"}, {"label": "readings:rs6@1:1"}]}]}, report, joint)


def test_correlated_document_reaches_admission(tmp_path):
    source, front = _sample(tmp_path)
    data = _environment()
    data["profiles"].remove("ve.discourse@1")
    env = Environment(data)

    def reading_set(uid, rid, ast):
        return {"id": rid, "unit": uid, "version": 1, "status": "open", "readings": [
            {"id": "a", "kind": "asserted", "content": ast,
             "meaning_id": meaning_id(env, formula_from_data(env, ast)),
             "admission": {"who": "author", "why": "recorded choice",
                           "distinguishing_models": {}}}]}

    front["reading_sets"] = [
        reading_set("u1", "rs5", front["units"][0]["content"]["ast"]),
        reading_set("u2", "rs6", front["units"][1]["content"]["ast"])]
    front["discourse"]["constraints"] = [
        {"kind": "requires", "a": ["rs5", 1, "a"], "b": ["rs6", 1, "a"]}]
    front["graph"] = {"root": "root", "nodes": [
        {"name": "root", "ast": front["units"][1]["content"]["ast"],
         "label": "readings:rs6@1:0"}]}
    result = check_document(_write(tmp_path, front, source))
    assert result["admission"]["admitted"] is True
    assert result["joint_choices"]["count"] == 1
    assert result["premises"]["status"] == "model"


def test_group_propagates_status_and_rejects_independent_fragment(tmp_path):
    source = b"A service is deployed.\nIt is reviewed.\n"
    cut = source.index(b"It")
    data = _environment()
    base = {**data, "profiles": ["relational-fol@0"]}
    env = Environment(base)
    formula = ["exists", "item", ["and", ["unary", "active", ["var", 0]],
                                      ["unary", "reviewed", ["var", 0]]]]
    front = {"format": "ve-document@2", "environment": data,
        "units": [{"id": "u1", "span": [0, cut], "kind": "asserted",
                   "meaning": "specified", "support": "assumption", "status": "OPEN"},
                  {"id": "u2", "span": [cut, len(source)],
                   "kind": "exposition", "meaning": "specified",
                   "support": "none", "status": "OPEN"}],
        "reading_sets": [{"id": "rs1", "unit": "u1", "version": 1, "status": "open",
            "readings": [{"id": "same-witness", "kind": "asserted", "content": formula,
                          "meaning_id": meaning_id(env, formula_from_data(env, formula)),
                          "admission": {"who": "author", "why": "shared service",
                                        "distinguishing_models": {}}}]}],
        "discourse": {"version": "ve.discourse@1", "anchors": [
            {"id": "doc", "kind": "document", "label": "Policy", "span": [0, len(source)]}],
            "groups": [{"set": "rs1", "version": 1, "reading": "same-witness",
                        "spans": ["u1", "u2"]}]}}
    path = _write(tmp_path, front, source)
    assert [u["status"] for u in load_document(path)["units"]] == ["OPEN", "OPEN"]
    front["units"][1]["content"] = {"ast": ["top"]}
    with pytest.raises(VEError, match="IndependentFragment"):
        load_document(_write(tmp_path, front, source))


# Regressions for the discourse reviews (manage-agents discourse-review-astra.final.md and
# reviews/discourse-review-fable.md).

def _units(sentences, contents=None, kinds=None):
    source, units = b"", []
    for i, sentence in enumerate(sentences):
        uid = f"u{i + 1}"
        start = len(source)
        source += sentence.encode() + b"\n"
        content = (contents or {}).get(uid)
        kind = (kinds or {}).get(uid, "asserted" if content is not None else "exposition")
        unit = {"id": uid, "span": [start, len(source)], "kind": kind, "meaning": "specified",
                "support": "assumption" if content is not None else "none"}
        if content is not None:
            unit["content"] = {"ast": content}
        units.append(unit)
    return source, units


def _front(source, units, mentions=(), names=None, extra=None, environment=None):
    block = {"version": "ve.discourse@1",
             "anchors": [{"id": "doc", "kind": "document", "label": "Policy", "span": [0, len(source)]}],
             "names": names if names is not None else [{"constant": "api", "display": "Api", "scope": "doc"},
                                                       {"constant": "alice", "display": "Alice", "scope": "doc"}],
             "mentions": list(mentions)}
    block.update(extra or {})
    return {"format": "ve-document@2", "environment": environment or _environment(), "units": units,
            "discourse": block}


def _mention(source, mid, uid, text, form, target, occurrence=0):
    index = -1
    for _ in range(occurrence + 1):
        index = source.index(text.encode(), index + 1)
    return {"id": mid, "unit": uid, "span": [index, index + len(text.encode())], "form": form, "target": target}


def test_unrecorded_surfaces_are_slots_with_or_without_a_block(tmp_path):
    """Astra A1 (Python side): every reference surface of a content unit must be recorded."""
    for sentence in ("This service is deployed.", "It is deployed.", "Its owner is deployed."):
        source, units = _units(["Api is reviewed.", sentence],
                               {"u1": ["unary", "reviewed", ["const", "api"]], "u2": ["unary", "active", ["const", "api"]]})
        with pytest.raises(VEError, match="UnrecordedSlot: u2"):
            load_document(_write(tmp_path, _front(source, units), source))
        front = _front(source, units)
        front["discourse"] = {}
        with pytest.raises(VEError, match="UnrecordedSlot: u2"):
            load_document(_write(tmp_path, front, source))


def test_ordinal_reconstructs_its_coordination(tmp_path):
    """Astra B: `the former`/`the latter` select a member of an earlier coordination."""
    pair = {"kind": "entity", "name": "api", "pair": ["api", "alice"]}
    source, units = _units(["Api and Alice are reviewed.", "The former is deployed."],
                           {"u2": ["unary", "active", ["const", "api"]]})
    front = _front(source, units, [_mention(source, "m1", "u2", "The former", "ordinal_pair", pair)])
    doc = load_document(_write(tmp_path, front, source))
    assert doc["discourse"]["presentations"]["u2"].strip() == "Api is deployed."
    assert doc["discourse"]["references"][0]["status"] == "resolved"
    # the reviewer's reproducer: `the latter` resolved to the first member
    source, units = _units(["Api and Alice are reviewed.", "The latter is deployed."],
                           {"u2": ["unary", "active", ["const", "api"]]})
    front = _front(source, units, [_mention(source, "m1", "u2", "The latter", "ordinal_pair", pair)])
    with pytest.raises(VEError, match="UnresolvedReference: m1"):
        load_document(_write(tmp_path, front, source))
    # no coordination before it: nothing to refer back to
    source, units = _units(["Api is reviewed.", "The latter is deployed."],
                           {"u2": ["unary", "active", ["const", "api"]]})
    front = _front(source, units, [_mention(source, "m1", "u2", "The latter", "ordinal_pair", pair)])
    with pytest.raises(VEError, match="UnresolvedReference: m1"):
        load_document(_write(tmp_path, front, source))


def _group_front(reading_content, reading_id="same-witness"):
    source, units = _units(["A service is deployed.", "It is reviewed."], kinds={"u1": "asserted"})
    data = _environment()
    env = Environment({**data, "profiles": ["relational-fol@0"]})
    front = _front(source, units, extra={"groups": [{"set": "rs1", "version": 1, "reading": reading_id,
                                                     "spans": ["u1", "u2"]}]})
    front["reading_sets"] = [{"id": "rs1", "unit": "u1", "version": 1, "status": "open", "readings": [
        {"id": reading_id, "kind": "asserted", "content": reading_content,
         "meaning_id": meaning_id(env, formula_from_data(env, reading_content)),
         "admission": {"who": "author", "why": "shared service", "distinguishing_models": {}}}]}]
    return source, front


def test_group_reading_is_regenerated_from_the_spans(tmp_path):
    """Astra A2 (Python side): the recorded shared-witness reading must be the spans' English."""
    fused = ["exists", "item", ["and", ["unary", "active", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]
    source, front = _group_front(fused)
    assert [u["status"] for u in load_document(_write(tmp_path, front, source))["units"]] == ["OPEN", "OPEN"]
    twice = ["exists", "item", ["and", ["unary", "reviewed", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]
    source, front = _group_front(twice)
    with pytest.raises(VEError, match="ManifestMismatch: groups.rs1@1:same-witness"):
        load_document(_write(tmp_path, front, source))
    # Fable C: the witness check does not depend on the reading's id
    split = ["and", ["exists", "item", ["unary", "active", ["var", 0]]], ["exists", "item", ["unary", "reviewed", ["var", 0]]]]
    source, front = _group_front(split, reading_id="fused")
    with pytest.raises(VEError, match="WitnessSplit: rs1@1:fused"):
        load_document(_write(tmp_path, front, source))


def _document_environment():
    data = _environment()
    data["vocabulary"]["sorts"]["document"] = {"description": "Document"}
    data["vocabulary"]["constants"]["policy2"] = {"sort": "document", "description": "Policy 2"}
    return data


def _import_front(tmp_path, source_id, document_id, stored=True):
    stored_source, stored_units = _units(["Api is reviewed in policy two."], {"u1": ["unary", "reviewed", ["const", "api"]]})
    stored_front = {"format": "ve-document@1", "environment": {**_environment(), "profiles": ["relational-fol@0"]},
                    "units": stored_units}
    if stored:
        (tmp_path / "policy2.ve.md").write_bytes(b"---\n" + json.dumps(stored_front).encode() + b"\n---\n" + stored_source)
    source, units = _units(["Api is reviewed."], {"u1": ["unary", "reviewed", ["const", "api"]]})
    pins = {"source_id": source_id, "document_id": document_id}
    front = _front(source, units, environment=_document_environment(), extra={
        "document_sort": "document",
        "documents": [{"name": "policy2", "display": ["policy 2"], "refers": {"import": "policy2"}, "version": 2, **pins}],
        "imports": {"policy2": {**pins, "bytes": "policy2.ve.md"}}})
    return source, front


def test_import_pins_are_enforced(tmp_path):
    """Astra A5 (Python side): an import's bytes re-fingerprint to both pins."""
    source, front = _import_front(tmp_path, "x", "y")
    stored = load_document(tmp_path / "policy2.ve.md")
    good = _import_front(tmp_path, stored["source_id"], stored["document_id"])
    load_document(_write(tmp_path, good[1], good[0]))
    for sid, did in [("0" * 64, stored["document_id"]), (stored["source_id"], "0" * 64)]:
        source, front = _import_front(tmp_path, sid, did)
        with pytest.raises(VEError, match="StaleTarget: policy2"):
            load_document(_write(tmp_path, front, source))
    source, front = _import_front(tmp_path, stored["source_id"], stored["document_id"])
    front["discourse"]["documents"][0]["document_id"] = "1" * 64
    with pytest.raises(VEError, match="ManifestMismatch: documents.policy2"):
        load_document(_write(tmp_path, front, source))
    # bytes absent: nothing to check here (the claim would be unconfirmed)
    (tmp_path / "policy2.ve.md").unlink()
    source, front = _import_front(tmp_path, "x", "y", stored=False)
    load_document(_write(tmp_path, front, source))


def test_empty_block_keeps_w2_reading_labels(tmp_path):
    """Fable B4: a W2 document repeated as @2 with an empty block keeps its reading-labelled
    report (the joint set is the product of the active open sets)."""
    source, front = _sample(tmp_path)
    source = source.replace(b"It is deployed.", b"Api is deployed.")
    front["units"][1]["span"][1] = len(source)
    front["discourse"] = {}
    data = _environment()
    env = Environment({**data, "profiles": ["relational-fol@0"]})
    ast = front["units"][1]["content"]["ast"]
    front["units"][1].pop("content")
    front["reading_sets"] = [{"id": "rs6", "unit": "u2", "version": 1, "status": "open", "readings": [
        {"id": "a", "kind": "asserted", "content": ast, "meaning_id": meaning_id(env, formula_from_data(env, ast)),
         "admission": {"who": "author", "why": "recorded choice", "distinguishing_models": {}}}]}]
    front["graph"] = {"root": "root", "nodes": [{"name": "root", "ast": ast, "label": "readings:rs6@1:0"}]}
    result = check_document(_write(tmp_path, front, source))
    assert result["admission"]["admitted"] is True


def test_python_reports_only_what_it_checked(tmp_path):
    """Fable B5: `resolved` only for elaborated mentions; forms Python does not elaborate are
    recorded, and rejected on content units as UnsupportedProfile (not MentionNotSlot or a
    resource limit); a location binding beside a pronoun is no resource limit."""
    plural = {"kind": "entity", "members": ["api", "alice"]}
    source, units = _units(["Api and Alice are reviewed.", "They are ready."])
    front = _front(source, units, [dict(_mention(source, "m1", "u2", "They", "plural", plural), reading="distributive")])
    doc = load_document(_write(tmp_path, front, source))
    assert doc["discourse"]["references"][0]["status"] == "recorded"
    units[1]["kind"], units[1]["support"] = "asserted", "assumption"
    units[1]["content"] = {"ast": ["unary", "ready", ["const", "alice"]]}
    with pytest.raises(VEError, match="UnsupportedProfile: ve.discourse@1 plural elaboration is not implemented"):
        load_document(_write(tmp_path, front, source))
    source, front = _sample(tmp_path)
    front["discourse"]["mentions"].append(_mention(source, "m2", "u2", "deployed", "navigation",
                                                   {"kind": "anchor", "name": "doc"}))
    doc = load_document(_write(tmp_path, front, source))
    assert [r["status"] for r in doc["discourse"]["references"]] == ["resolved", "navigation"]


def test_legacy_profile_environment_still_loads_as_format_1(tmp_path):
    """Fable B6: the @1 path does not require the v0.2 `profiles` list."""
    from tests.test_views import vocabulary
    source, units = _units(["Api is reviewed."], {"u1": ["unary", "reviewed", ["const", "api"]]})
    front = {"format": "ve-document@1", "environment": vocabulary(), "units": units}
    assert load_document(_write(tmp_path, front, source))["units"][0]["status"] == "CHECKED"


def test_lean_only_block_fields_are_unsupported_not_misread(tmp_path):
    source, front = _sample(tmp_path)
    front["discourse"]["validity"] = [{"unit": "u1", "document": "x", "holds": True}]
    with pytest.raises(VEError, match="UnsupportedProfile: ve.discourse@1 validity claims are not implemented in Python"):
        load_document(_write(tmp_path, front, source))
