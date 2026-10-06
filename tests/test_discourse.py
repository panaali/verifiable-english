"""Regression tests for the Python discourse relay: every verdict, diagnostic, reference, status
and joint choice is the Lean route's answer (docs/LEAN-FIRST-PLAN.md, batch 4)."""
import json

import pytest

from tests.test_views import vocabulary
from ve.document import check_document, load_document, render_document
from ve.errors import CheckerUnavailable, VEError
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.readings import check_readings
from ve.environment import Environment
from ve.ast import formula_from_data
from ve.identity import meaning_id
from ve.model import FiniteModel


def _environment():
    """The views vocabulary with `active` named by its word, `deployed`: the admission is the Lean
    route's, whose discourse fragment reads a predicate by its name (a verbalisation only Python's
    parser reads is outside it, `test_python_never_adds_an_admission`)."""
    data = vocabulary()
    predicates = data["vocabulary"]["predicates"]
    predicates["deployed"] = predicates.pop("active")
    data["language"] = LANGUAGE
    data.pop("profile")
    data["profiles"] = ["relational-fol@0", "ve.discourse@1"]
    data["spec_revision"] = SPEC_REVISION
    return data


def _nounless_environment():
    """`item` without its declared noun: Python's English parser reads a sort by its declared noun
    only, Lean's group opening by its name only, so a group spans the name in both."""
    data = _environment()
    data["vocabulary"]["sorts"]["item"].pop("verbalisation")
    return data


def _unit(uid, span, content):
    return {"id": uid, "span": span, "kind": "asserted", "meaning": "specified",
            "support": "assumption", "content": {"ast": content}}


OPEN_TERM = {"name": "t", "arguments": [], "decided_by": "reviewer", "necessary": [], "sufficient": [],
             "factors": [], "precedents": [], "jurisdiction": "policy", "version": 1}
OPEN_GRAPH = {"root": "n", "nodes": [{"name": "n", "ast": ["top"], "label": "open:t"}]}


def _write(tmp_path, front, source, graph=True):
    """The document text; a `@2` document gets a claim graph (one open-term leaf) unless it has one:
    the Lean route, whose verdict it is, admits documents with a graph (a graph-less `@2` document
    is an abstention, `test_graphless_document_is_an_abstention`)."""
    if graph and front.get("format") == "ve-document@2" and "graph" not in front:
        front = {**front, "graph": OPEN_GRAPH, "open_terms": [OPEN_TERM]}
    path = tmp_path / "discourse.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + source)
    return path


def _sample(tmp_path):
    source = b"Api is reviewed.\nIt is deployed.\n"
    cut = source.index(b"It")
    front = {"format": "ve-document@2", "environment": _environment(),
             "units": [_unit("u1", [0, cut], ["unary", "reviewed", ["const", "api"]]),
                       _unit("u2", [cut, len(source)], ["unary", "deployed", ["const", "api"]])],
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


@pytest.mark.parametrize("word", ["It's", "It’s", "It_", "Itʼs", "It-is", "It is"])
def test_joined_reference_word_is_a_slot(tmp_path, word):
    """looprecheck2 B (discourse.py:272): a reference word joined to anything but an ASCII letter
    or digit is found, so an unrecorded one is never unchecked meaning (the Lean segments)."""
    source, front = _sample(tmp_path)
    source = source.replace(b"It is", word.encode() + b" is")
    cut = source.index(b"It")
    front["units"][1]["span"][1] = len(source)
    front["discourse"]["anchors"][0]["span"] = [0, len(source)]
    front["discourse"]["mentions"] = []
    with pytest.raises(VEError, match=rf"UnrecordedSlot: u2: \[{cut}, {cut + 2}\)"):
        load_document(_write(tmp_path, front, source))


def test_rejects_partial_overlap_and_stale_version(tmp_path):
    source, front = _sample(tmp_path)
    cut = source.index(b"It")
    front["discourse"]["mentions"].append({"id": "m2", "unit": "u2",
        "span": [cut + 1, cut + 5], "form": "pronoun",
        "target": {"kind": "entity", "name": "api"}})
    # a range that starts inside the token `It` is no token range of its unit (the Lean `tokenSpan`)
    with pytest.raises(VEError, match="InvalidInput: mention m2 span"):
        load_document(_write(tmp_path, front, source))
    front["discourse"]["mentions"][0]["span"] = [cut, cut + 5]
    front["discourse"]["mentions"][1]["span"] = [cut + 3, cut + 14]
    with pytest.raises(VEError, match="overlap"):
        load_document(_write(tmp_path, front, source))
    front["discourse"]["mentions"].pop()
    front["discourse"]["mentions"][0]["span"] = [cut, cut + 2]
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


def _correlated(tmp_path, constraints, label=0, readings=None, sets=2):
    """The sample with `sets` (at least two) more units, each with an open reading set of two
    readings (`readings`, by default `reviewed` and `deployed` of api, told apart by the model
    where only `reviewed(api)` and `exempt(api)` hold), the constraints over them, and a graph
    citing reading `label` of rs6."""
    source, front = _sample(tmp_path)
    data = _environment()
    data["profiles"].remove("ve.discourse@1")
    env = Environment(data)
    p, q = readings or (front["units"][0]["content"]["ast"], front["units"][1]["content"]["ast"])
    # one entity per sort, `reviewed(api)` and `exempt(api)` true, the rest false: it separates p and q
    model = {"complete": True, "domains": {s: [f"e_{s}"] for s in env.model_sorts},
             "constants": {c: f"e_{d.sort}" for c, d in env.constants.items()},
             "relations": {name: ([[f"e_{env.constants['api'].sort}"]] if name in ("reviewed", "exempt") else [])
                           for name in env.predicates}}
    mid = FiniteModel.from_dict(env, model).model_id
    for uid in [f"u{3 + k}" for k in range(sets)]:
        start = len(source)
        source += b"Api is reviewed.\n"
        front["units"].append({"id": uid, "span": [start, len(source)], "kind": "asserted",
                               "meaning": "specified", "support": "assumption"})
    front["discourse"]["anchors"][0]["span"] = [0, len(source)]

    def reading_set(uid, rid):
        readings = [("a", p), ("b", q)]
        return {"id": rid, "unit": uid, "version": 1, "status": "open", "models": {mid: model}, "readings": [
            {"id": key, "kind": "asserted", "content": ast,
             "meaning_id": meaning_id(env, formula_from_data(env, ast)),
             "admission": {"who": "author", "why": "recorded choice",
                           "distinguishing_models": {other: mid for other, _ in readings if other != key}}}
            for key, ast in readings]}

    front["reading_sets"] = [reading_set(f"u{3 + k}", f"rs{5 + k}") for k in range(sets)]
    front["discourse"]["constraints"] = constraints
    front["graph"] = {"root": "root", "nodes": [{"name": "root", "ast": [p, q][label],
                                                 "label": f"readings:rs6@1:{label}"}]}
    return source, front


def test_joint_choices_are_leans(tmp_path):
    """The joint set (4.8) is Lean's `compatibleChoices`: the choices the relay reports and hands
    to the readings verdict are the admission's, and an empty enumeration is Lean's rejection."""
    requires = [{"kind": "requires", "a": ["rs5", 1, "a"], "b": ["rs6", 1, "a"]},
                {"kind": "requires", "a": ["rs5", 1, "b"], "b": ["rs6", 1, "b"]}]
    source, front = _correlated(tmp_path, requires)
    path = _write(tmp_path, front, source)
    doc = load_document(path)
    assert doc["discourse"]["joint"] == {"status": "complete", "count": 2, "constraints": 2,
                                         "choices": [{"rs5@1": 0, "rs6@1": 0}, {"rs5@1": 1, "rs6@1": 1}]}
    assert check_document(path)["joint_choices"] == {"status": "complete", "count": 2, "constraints": 2}
    excludes = [{"kind": "excludes", "a": ["rs5", 1, x], "b": ["rs6", 1, y]} for x in ("a", "b") for y in ("a", "b")]
    source, front = _correlated(tmp_path, excludes)
    with pytest.raises(VEError, match="^InvalidCompatibility: rs5, rs6$"):
        load_document(_write(tmp_path, front, source))


def test_composition_gate_is_leans(tmp_path):
    """A report label outside every compatible choice is Lean's `InvalidCompatibility` (the gate
    over `gateChoices`); the relay checks no extension of its own."""
    excludes = [{"kind": "excludes", "a": ["rs5", 1, x], "b": ["rs6", 1, "a"]} for x in ("a", "b")]
    source, front = _correlated(tmp_path, excludes, label=0)
    with pytest.raises(VEError, match="^InvalidCompatibility: report root$"):
        load_document(_write(tmp_path, front, source))
    source, front = _correlated(tmp_path, excludes, label=1)
    assert check_document(_write(tmp_path, front, source))["admission"]["admitted"] is True


FUSED = ["exists", "item", ["and", ["unary", "deployed", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]
TWICE = ["exists", "item", ["and", ["unary", "reviewed", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]


def test_group_openings_follow_lean(tmp_path):
    """The authority directive on groups: the Lean grammar reads a group opening by the sort's
    name only (`An item`), not by its declared noun (`A service`). The noun is Lean's rejection,
    the name Lean's admission, and a wrong reading Lean's `ManifestMismatch` (batch 4: Python's
    own fragment diagnostic, kept before when both rejected, is gone)."""
    fragment = "InvalidInput: group rs1@1:same-witness spans are outside the supported fragment"
    source, front = _group_front(FUSED, opening="A service is deployed.", data=_environment())
    with pytest.raises(VEError, match=f"^{fragment}$"):
        load_document(_write(tmp_path, front, source))
    source, front = _group_front(FUSED, data=_environment())
    result = check_document(_write(tmp_path, front, source))
    assert "discourse_hints" not in result
    assert result["coverage"]["bytes_by_status"] == {"OPEN": len(source)}
    source, front = _group_front(TWICE, data=_environment())
    with pytest.raises(VEError, match="^ManifestMismatch: groups.rs1@1:same-witness$"):
        load_document(_write(tmp_path, front, source))


def test_joint_verdict_uses_only_compatible_choices():
    data = _environment()
    data["profiles"].remove("ve.discourse@1")
    env = Environment(data)
    p = ["unary", "deployed", ["const", "api"]]
    sets = [{"id": "r1", "version": 1, "status": "open", "readings": [
                {"id": "a", "kind": "asserted", "content": p},
                {"id": "b", "kind": "asserted", "content": ["not", p]}]},
            {"id": "r2", "version": 1, "status": "open", "readings": [
                {"id": "a", "kind": "asserted", "content": ["top"]},
                {"id": "b", "kind": "asserted", "content": ["top"]}]}]
    # the joint set as the relay hands it over from Lean's answer (`discourse._joint`)
    joint = {"status": "complete", "count": 2, "constraints": 2,
             "choices": [{"r1@1": 0, "r2@1": 0}, {"r1@1": 1, "r2@1": 1}]}
    assert check_readings(env, sets, p, joint_choices=joint)["verdict"] == "SOME"


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
    source = b"An item is deployed.\nIt is reviewed.\n"
    cut = source.index(b"It")
    data = _nounless_environment()
    base = {**data, "profiles": ["relational-fol@0"]}
    env = Environment(base)
    formula = ["exists", "item", ["and", ["unary", "deployed", ["var", 0]],
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
                               {"u1": ["unary", "reviewed", ["const", "api"]], "u2": ["unary", "deployed", ["const", "api"]]})
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
                           {"u2": ["unary", "deployed", ["const", "api"]]})
    front = _front(source, units, [_mention(source, "m1", "u2", "The former", "ordinal_pair", pair)])
    doc = load_document(_write(tmp_path, front, source))
    assert doc["discourse"]["presentations"]["u2"].strip() == "Api is deployed."
    assert doc["discourse"]["references"][0]["status"] == "resolved"
    # the reviewer's reproducer: `the latter` resolved to the first member
    source, units = _units(["Api and Alice are reviewed.", "The latter is deployed."],
                           {"u2": ["unary", "deployed", ["const", "api"]]})
    front = _front(source, units, [_mention(source, "m1", "u2", "The latter", "ordinal_pair", pair)])
    with pytest.raises(VEError, match="UnresolvedReference: m1"):
        load_document(_write(tmp_path, front, source))
    # no coordination before it: nothing to refer back to
    source, units = _units(["Api is reviewed.", "The latter is deployed."],
                           {"u2": ["unary", "deployed", ["const", "api"]]})
    front = _front(source, units, [_mention(source, "m1", "u2", "The latter", "ordinal_pair", pair)])
    with pytest.raises(VEError, match="UnresolvedReference: m1"):
        load_document(_write(tmp_path, front, source))


def _group_front(reading_content, reading_id="same-witness", opening="An item is deployed.", data=None):
    source, units = _units([opening, "It is reviewed."], kinds={"u1": "asserted"})
    data = data or _nounless_environment()
    env = Environment({**data, "profiles": ["relational-fol@0"]})
    front = _front(source, units, environment=data, extra={"groups": [{"set": "rs1", "version": 1, "reading": reading_id,
                                                     "spans": ["u1", "u2"]}]})
    front["reading_sets"] = [{"id": "rs1", "unit": "u1", "version": 1, "status": "open", "readings": [
        {"id": reading_id, "kind": "asserted", "content": reading_content,
         "meaning_id": meaning_id(env, formula_from_data(env, reading_content)),
         "admission": {"who": "author", "why": "shared service", "distinguishing_models": {}}}]}]
    return source, front


def test_group_reading_is_regenerated_from_the_spans(tmp_path):
    """Astra A2 (Python side): the recorded shared-witness reading must be the spans' English."""
    fused = ["exists", "item", ["and", ["unary", "deployed", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]
    source, front = _group_front(fused)
    assert [u["status"] for u in load_document(_write(tmp_path, front, source))["units"]] == ["OPEN", "OPEN"]
    twice = ["exists", "item", ["and", ["unary", "reviewed", ["var", 0]], ["unary", "reviewed", ["var", 0]]]]
    source, front = _group_front(twice)
    with pytest.raises(VEError, match="ManifestMismatch: groups.rs1@1:same-witness"):
        load_document(_write(tmp_path, front, source))
    # Fable C: the witness check does not depend on the reading's id
    split = ["and", ["exists", "item", ["unary", "deployed", ["var", 0]]], ["exists", "item", ["unary", "reviewed", ["var", 0]]]]
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


def test_python_reports_lean_references(tmp_path):
    """Fable B5, under the Lean authority (discourse-authority-directive): a plural is Lean's to
    elaborate, a rejection with Lean's diagnostic or an admission whose references are Lean's; a
    plural has no reviewed wording (only pronouns, demonstratives and ordinal pairs are shown with
    their target's display). A location binding beside a pronoun is no resource limit."""
    plural = {"kind": "entity", "members": ["api", "alice"]}
    source, units = _units(["Api and Alice are reviewed.", "They are ready."])
    front = _front(source, units, [dict(_mention(source, "m1", "u2", "They", "plural", plural), reading="distributive")])
    with pytest.raises(VEError, match="^IllTypedTarget: m1: api, alice$"):
        load_document(_write(tmp_path, front, source))
    environment = _environment()
    environment["vocabulary"]["constants"]["bob"] = {"sort": "agent", "description": "Bob"}
    pair = {"kind": "entity", "members": ["alice", "bob"]}
    ready = [["unary", "ready", ["const", c]] for c in ("alice", "bob")]
    source, units = _units(["Alice and Bob are ready.", "They are ready."], {"u2": ["and", *ready]})
    names = [{"constant": "alice", "display": "Alice", "scope": "doc"}, {"constant": "bob", "display": "Bob", "scope": "doc"}]
    front = _front(source, units, [dict(_mention(source, "m1", "u2", "They", "plural", pair), reading="distributive")],
                   names=names, environment=environment)
    result = check_document(_write(tmp_path, front, source))
    assert [(r["mention"], r["status"]) for r in result["references"]] == [("m1", "resolved")]
    assert "discourse_hints" not in result
    assert "u2" not in result["reviewed_presentations"]
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


def test_lean_only_block_fields_are_lean_verdicts(tmp_path):
    """A validity claim Python does not evaluate was its `UnsupportedProfile` abstention; the
    verdict is now Lean's: a claim on a premise unit is `InvalidInput: validity unit u1`."""
    source, front = _sample(tmp_path)
    front["discourse"]["validity"] = [{"unit": "u1", "document": "x", "holds": True}]
    with pytest.raises(VEError, match="^InvalidInput: validity unit u1$"):
        load_document(_write(tmp_path, front, source))


def test_navigation_relabel_does_not_hide_a_slot(tmp_path):
    """looprecheck1 A (discourse.py:582): the reviewer's reproducer, `It` relabelled as a
    navigation mention to the document anchor, is an unrecorded slot, not 100% CHECKED."""
    source, front = _sample(tmp_path)
    front["discourse"]["mentions"][0]["form"] = "navigation"
    front["discourse"]["mentions"][0]["target"] = {"kind": "anchor", "name": "doc"}
    with pytest.raises(VEError, match=r"UnrecordedSlot: u2: \[17, 19\)"):
        check_document(_write(tmp_path, front, source))


def test_discourse_wording(tmp_path):
    """discourse2 loop A and B: a unit recording a reference is printable ASCII with canonical
    spacing once its surrounding layout is removed (4.1(4)), else one code: Lean's
    `canonicalWording` (its variants: tests/test_discourse_lean.py)."""
    source, front = _sample(tmp_path)
    cut = source.index(b"It")
    source = source[:cut] + b"It is deployed .\n"
    front["units"][1]["span"] = [cut, len(source)]
    with pytest.raises(VEError, match=r"^InvalidInput: discourse wording of u2$"):
        check_document(_write(tmp_path, front, source))


def _route_answers(monkeypatch, answer):
    """The Lean discourse route (service mode `discourse`) answers `answer`: its rows, or an exception."""
    from ve.backends import relay

    def rows(mode, cases, **_):
        assert mode == "discourse" and len(cases) == 1
        if isinstance(answer, BaseException):
            raise answer
        return answer
    monkeypatch.setattr(relay, "rows", rows)


def test_lean_unavailable_is_never_a_python_verdict(tmp_path, monkeypatch):
    """discourse-authority-directive 1: a `@2` document's admission is the Lean route's. Without an
    answer from it (no service, a crash, a row that is not one well-formed answer to the case)
    the result is `CheckerUnavailable`, never a Python-only CHECKED or rejection; a `@1` document
    never asks it."""
    from ve.backends import relay
    from ve.backends.lean_service import CheckerUnavailable, LeanServicePool
    source, front = _sample(tmp_path)
    path = _write(tmp_path, front, source)
    assert check_document(path)["references"][0]["status"] == "resolved"
    with monkeypatch.context() as missing:
        missing.setattr(relay, "_pool", LeanServicePool(size=1, executable=tmp_path / "missing"))
        for call in (load_document, check_document, render_document):
            with pytest.raises(CheckerUnavailable, match="^CheckerUnavailable: "):
                call(path)
    for answer in [CheckerUnavailable("CheckerUnavailable: the service crashed"),
                   [{"id": "python-admission", "status": "ok", "admitted": True}],
                   [{"id": "other", "status": "error", "error": "InvalidInput: x"}]]:
        _route_answers(monkeypatch, answer)
        for call in (load_document, check_document, render_document):
            with pytest.raises(CheckerUnavailable, match="^CheckerUnavailable: "):
                call(path)
    source, units = _units(["Api is reviewed."], {"u1": ["unary", "reviewed", ["const", "api"]]})
    older = {"format": "ve-document@1", "environment": {**_environment(), "profiles": ["relational-fol@0"]},
             "units": units}
    assert load_document(_write(tmp_path, older, source))["units"][0]["status"] == "CHECKED"


def test_python_follows_a_lean_verdict_it_would_not_reach(tmp_path, monkeypatch):
    """Python neither adds nor removes an admission: the route rejects the retargeted pronoun
    (`InaccessibleTarget`), yet an admission from the route is the result, with nothing of
    Python's beside it, and a route rejection of a document the route admits otherwise is the
    result too. A route answer missing a member the relay reads is no answer."""
    source, front = _sample(tmp_path)
    admitted = check_document(_write(tmp_path, front, source))
    front["discourse"]["mentions"][0]["target"]["name"] = "alice"
    retargeted = _write(tmp_path, front, source)
    with pytest.raises(VEError, match="^InaccessibleTarget: m1: alice$"):
        check_document(retargeted)
    retargeted_references = [{**admitted["references"][0], "target": {"kind": "entity", "name": "alice"}}]
    answer = {"id": "python-admission", "status": "ok", "admitted": True, "report_id": "f" * 64,
              "references": retargeted_references, "statuses": {"u1": "CHECKED", "u2": "OPEN"},
              "validity": {}, "joint": 1, "joint_choices": [[]], "joint_formula": ["top"],
              "bound": {"u2": ["unary", "deployed", ["const", "api"]]}}

    def answers(rows, code=0):
        _route_answers(monkeypatch, rows)
    answers([answer])
    result = check_document(retargeted)
    assert result["report_id"] == "f" * 64 and "discourse_hints" not in result
    assert result["references"] == retargeted_references
    # `alice` is no registered name: no reviewed wording shows it
    assert result["reviewed_presentations"] == {}
    assert result["coverage"]["bytes_by_status"] == {"CHECKED": 17, "OPEN": 16}
    # an answer about the document as it was before the retargeting is no answer to it
    answers([{**answer, "references": admitted["references"]}])
    with pytest.raises(CheckerUnavailable, match=r"^CheckerUnavailable: .* another document \(references\)$"):
        check_document(retargeted)
    front["discourse"]["mentions"][0]["target"]["name"] = "api"
    original = _write(tmp_path, front, source)
    answer["references"] = admitted["references"]
    answers([answer])
    assert check_document(original)["reviewed_presentations"] == {"u2": "Api is deployed.\n"}
    # a bound formula the shown wording does not parse to is never shown
    answers([{**answer, "bound": {"u2": ["unary", "reviewed", ["const", "api"]]}}])
    assert check_document(original)["reviewed_presentations"] == {}
    for key, value in [("validity", None), ("bound", None), ("bound", []), ("joint", True), ("joint", 2), ("joint_choices", [[], []]),
                       ("joint_choices", [[["rs1", True, 0]]]), ("joint_formula", None),
                       ("joint", "ResourceLimit: joint choices")]:
        broken = {**answer, key: value} if value is not None else {k: v for k, v in answer.items() if k != key}
        answers([broken])
        with pytest.raises(CheckerUnavailable, match="^CheckerUnavailable: the Lean discourse route returned no"):
            check_document(original)
    answers([{"id": "python-admission", "status": "error", "error": "StaleTarget: m1"}], code=1)
    with pytest.raises(VEError, match="^StaleTarget: m1$") as caught:
        check_document(original)
    assert caught.value.code == "StaleTarget"


@pytest.mark.parametrize("condition, text", [
    (["unary", "nonexistent", ["const", "api"]], "UnknownSymbol: Unknown predicate 'nonexistent'"),
    (["unary", "reviewed", ["const", "nobody"]], "UnknownSymbol: Unknown constant 'nobody'"),
    (["unary", "reviewed", ["var", 0]], "UnboundVariable: Variable index 0 is outside its scope")])
def test_ill_typed_open_term_condition_keeps_its_base_answer(tmp_path, condition, text):
    # Discrepancy fixture (lean-first 11a review B2): an open term's conditions are closed formulas over the
    # environment (document.md), but the discourse route reads only their structure and admits the document,
    # which Python's `validate_open_terms` then rejects: CheckerUnavailable, as at base. Making it Lean's
    # rejection is an `availability` change that needs a DRI signature (plan 5.1 item 2); it is proposed in
    # docs/lean-first/b11a/DELTA.md, not applied. Only the speech-source wrapper types the conditions.
    source, front = _sample(tmp_path)
    term = {**OPEN_TERM, "necessary": [condition]}
    path = _write(tmp_path, {**front, "graph": OPEN_GRAPH, "open_terms": [term]}, source)
    with pytest.raises(CheckerUnavailable) as raised:
        load_document(path)
    assert str(raised.value) == f"CheckerUnavailable: Lean admits the document but Python cannot report it ({text})"


# The shared W2 front-matter readers (`Discourse.Loader`) are relayed to Python verbatim (batch 4), so a change made
# for another route (the speech-source wrapper reads the same functions in their `python` mode) must not move one
# discourse answer without a signed DELTA (lean-first 11a review B2). Every single-fault mutant of the open terms,
# reading sets, narrowings and unit meanings of one document is answered by the route and compared with the answers
# the base checkout's route gave, captured once by `capture_w2_pins` and pinned in `W2_PINS`.
W2_PINS = __import__("pathlib").Path(__file__).parent / "data" / "w2-front-matter-pins.json"
W2_FIELDS = ("open_terms", "reading_sets", "narrowings", "units")


def _w2_front(tmp_path):
    requires = [{"kind": "requires", "a": ["rs5", 1, "a"], "b": ["rs6", 1, "a"]}]
    source, front = _correlated(tmp_path, requires)
    front["open_terms"] = [{**OPEN_TERM, "arguments": ["api"], "necessary": [["unary", "reviewed", ["const", "api"]]],
                            "factors": ["review record"], "precedents": ["p1"]}]
    front["units"][0]["meaning"] = {"open": ["t"]}
    front["narrowings"] = [{"id": "n1", "set": "rs5", "version": 1, "keeps": ["a"], "by": "author",
                            "reason_spans": ["u1"]}]
    return source, front


def w2_front_matter_cases(tmp_path):
    """(path, document text) for the template and each of its single-fault mutants in `W2_FIELDS`."""
    from tests.test_speech_acts_conformance import _MISSING, _replace_wire, _wire_mutations
    source, front = _w2_front(tmp_path)
    out = [("template", front)]
    for path, replacement in _wire_mutations(front):
        if path[0] in W2_FIELDS and not (path[0] == "units" and "content" in path):
            name = repr((*path, "MISSING" if replacement is _MISSING else replacement))
            out.append((name, _replace_wire(front, path, replacement)))
    return [(name, (b"---\n" + json.dumps(f).encode() + b"\n---\n" + source).decode()) for name, f in out]


def _w2_answers(executable, cases):
    import hashlib
    import subprocess

    from subprocesses import HANG_TIMEOUT
    batch = [{"id": str(i), "kind": "admission", "document": text, "files": {}} for i, (_, text) in enumerate(cases)]
    if executable is None:
        from tests import lean_routes
        rows = lean_routes.rows("ve_discourse_route", batch)
    else:
        done = subprocess.run([str(executable), "-"], input=json.dumps(batch).encode(), capture_output=True,
                              timeout=HANG_TIMEOUT * 4, check=False)
        rows = json.loads(done.stdout)
        assert len(rows) == len(cases), done.stderr[-300:]
    assert len(rows) == len(cases)
    return {name: (row["error"] if row.get("status") == "error" else
                   "ok " + hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest())
            for (name, _), row in zip(cases, rows)}


def capture_w2_pins(executable, tmp_path):
    """Write `W2_PINS` from `executable`, the base checkout's `ve_discourse_route` (run once per frozen change):
    `python -c "from pathlib import Path; import tempfile; from tests.test_discourse import capture_w2_pins;
    capture_w2_pins(Path('BASE/lean/.lake/build/bin/ve_discourse_route'), Path(tempfile.mkdtemp()))"`."""
    W2_PINS.write_text(json.dumps(_w2_answers(executable, w2_front_matter_cases(tmp_path)), indent=0,
                                  sort_keys=True) + "\n")


def test_w2_front_matter_diagnostics_are_pinned(tmp_path):
    pinned = json.loads(W2_PINS.read_text())
    cases = w2_front_matter_cases(tmp_path)
    assert pinned["template"].startswith("ok "), pinned["template"]
    assert len(cases) == len(pinned) > 500
    answers = _w2_answers(None, cases)
    assert {k: v for k, v in answers.items() if pinned[k] != v} == {}
