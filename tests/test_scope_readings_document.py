"""Scope spec 11 (sc-5rb): a reading set on a governed unit, checked once per joint choice by the document mode.

The part document is F1 (`tests/data/scope/hard-constraints.scope.md`, the hard-constraint block) with `readings@1`
listed and u0165.s03's reading set `scope-u0165-s03` as the pilot records it (`s03_scope.py`): readings `wide` and
`narrow`, each written as a part under the frame. Main refuses it with `ScopeReadings: u0165.s03`; Lean's
`checkDocSets` governs it once per choice (11.6 SR-1, DELTA row 1). The 11.6 fixtures themselves are `#guard`s in
`lean/VE/Scope/ReadingsExamples.lean`; these are the document-level ones of 11.7 item 6."""
from __future__ import annotations

import json

import pytest

from tests.test_readings_s1_lean import situation_id
from tests.test_scope_document import F1, ITEMS, _rows, _split, _text, _written_in_full, structural_mutants_accepted
from ve import document as D
from ve.backends.lean_service import CheckerUnavailable

SET = "scope-u0165-s03"
CW, MC, DMG = "creating_a_cyberweapon", "creating_malicious_code", "could_cause_significant_damage_if_deployed"


def _u(name):
    return ["unary", name, ["var", 0]]


CATEGORY = {"wide": ["and", ["or", _u(CW), _u(MC)], _u(DMG)], "narrow": ["or", _u(CW), ["and", _u(MC), _u(DMG)]]}


def _part(r):
    return {"part": {"name": "hc-cyberweapons", "predicate": "cyberweapon_creation_permitted", "guard": [
        "or", ["and", CATEGORY[r], ["binary", f"knowingly_engages_3_{r}", ["var", 1], ["var", 0]]],
        ["binary", f"thinks_quite_likely_3_{r}", ["var", 1], ["var", 0]]]}}


def _meta(edit=None):
    """F1 with u0165.s03's set; `edit(meta, set)` changes either before the distinguishing situation is recorded."""
    meta, body = _split(F1.read_text())
    env = meta["environment"]
    env["profiles"] = sorted(env["profiles"] + ["readings@1"])
    env["vocabulary"]["predicates"]["cyberweapon_creation_permitted"] = {
        "arguments": ["claude_instance", "situation"], "description": "Claude may create the cyberweapon or code.",
        "regulated": {"role": "permission", "default": "unspecified", "act": "{0} do the creation in {1}"}}
    rs = {"id": SET, "unit": "u0165.s03", "version": 1, "status": "open", "readings": [
        {"id": r, "kind": "norm", "meaning_id": f"m-{r}", "content": _part(r),
         "admission": {"who": "translator", "why": "the clause follows both nouns or only the second"}}
        for r in ("wide", "narrow")]}
    meta["reading_sets"] = [rs]
    if edit:
        edit(meta, rs)
    # the narrow reading's own belief term holds and nothing else: the wide reading is false there, the narrow true
    relations = {("unsaid__" + p if "regulated" in d else p): [] for p, d in env["vocabulary"]["predicates"].items()}
    entry = {"base": {"domains": {"claude_instance": ["c"], "situation": ["s"]}, "constants": {},
                      "relations": relations | {"thinks_quite_likely_3_narrow": [["c", "s"]]}},
             "fixed": [], "witness": "wide", "decisions": [], "value": False,
             "probe": {"selects": {"kind": "norm", "predicate": "cyberweapon_creation_permitted", "tuple": ["c", "s"]}}}
    sid = situation_id({**env, "profiles": [p for p in env["profiles"] if p != "scope@0"]}, entry)
    for s in meta.get("reading_sets", []):
        s["situations"] = {sid: entry}
        for r in s["readings"]:
            r["admission"]["distinguishing_models"] = {o["id"]: sid for o in s["readings"] if o["id"] != r["id"]}
    return meta, body


def _doc(edit=None):
    return _text(*_meta(edit))


def test_sr1_the_set_inside_the_list_is_admitted_and_the_lead_in_takes_its_items_status():
    rows, row = _rows(_doc())
    f1, f1_row = _rows(F1.read_text())
    assert rows["u0164.s02"]["status"] == "OPEN" and rows["u0165.s03"]["status"] == "OPEN"
    # the other six rules as F1's, but for the meaning id, which names the environment (a predicate and readings@1)
    assert all({**rows[u], "meaning_id": 0} == {**f1[u], "meaning_id": 0} for u in ITEMS if u != "u0165.s03")
    assert row["coverage"]["bytes_by_status"] == f1_row["coverage"]["bytes_by_status"] == {"OPEN": 896,
                                                                                            "UNFORMALISED": 472}
    assert row["coverage"]["residual"]["unresolved_reading_sets"] == 1


def test_sr1_through_ve_document_check_two_choices(tmp_path):
    path = tmp_path / "sr1.ve.md"
    path.write_text(_doc())
    checked = D.check_document(path)
    assert checked["reading_plan"] == {"route": "enumerate", "choices": [{SET: 0}, {SET: 1}]}
    assert checked["coverage"]["bytes_by_status"] == {"OPEN": 896, "UNFORMALISED": 472}


@pytest.mark.parametrize("reading, other", [(1, "narrow"), (0, "wide")])
def test_sr_c_a_choice_that_conflicts_refuses_naming_the_choice(tmp_path, reading, other):
    def sign(meta, rs):
        rs["readings"][reading]["content"]["part"]["sign"] = False
    path = tmp_path / "src.ve.md"
    path.write_text(_doc(sign))
    with pytest.raises(Exception, match=f"^ScopeChoice: u0165.s03 {SET}@1:{other}: ScopeConflict: u0165.s03: sign$"):
        D.check_document(path)


def _on_lead(meta, rs):
    rs["unit"] = "u0164.s02"


def _with_content(meta, rs):
    next(u for u in meta["units"] if u["id"] == "u0165.s03")["content"] = _part("wide")


def _two_versions(meta, rs):
    meta["reading_sets"].append({**json.loads(json.dumps(rs)), "version": 2})


def _no_reading(meta, rs):
    rs["readings"] = []


@pytest.mark.parametrize("edit, text", [
    (_on_lead, "ScopeReadings: u0164.s02"), (_with_content, "ScopeReadings: u0165.s03"),
    (_two_versions, "ScopeReadings: u0165.s03"), (_no_reading, "ScopeReadings: u0165.s03")])
def test_sets_spec_11_1_does_not_govern_are_refused_as_today(edit, text):
    """The refusing side of each clause of 11.1 (SR-1 is the accepting side): the set on the governor's own unit, on
    a unit that also has content, in two versions, and with no reading."""
    assert _rows(_doc(edit))[1] == text


def test_sr0_without_a_governed_set_the_document_is_answered_as_govern_alone():
    """11.6 SR-0 end to end (`checkDocSets_no_sets`): F1 has no reading set, and the chain is handed no
    `reading_sets` of GOVERN's (copying them would read F1's absent member as null)."""
    rows, row = _rows(F1.read_text())
    assert rows["u0164.s02"]["status"] == "OPEN" and row["coverage"]["residual"]["unresolved_reading_sets"] == 0


def test_a_cases_own_reading_sets_member_is_no_input():
    """Only `withSets` hands the chain reading sets: a case's own `reading_sets` is dropped (`withUnits`)."""
    from ve.backends.relay import answer
    for text in (F1.read_text(), _doc()):
        plain = answer("document", {"id": "d", "document": text, "admit": True})
        forged = answer("document", {"id": "d", "document": text, "admit": True, "reading_sets": 7})
        assert forged == plain and plain[1] is None


def test_a_governed_readings_meaning_id_is_read_as_the_written_in_full_document_reads_it():
    """11.7 item 3: whatever reads a norm reading's `meaning_id` today reads it on the governed answer. The document
    mode reads none: a stated id that names no rule changes neither answer."""
    def stale(meta, rs):
        rs["readings"][0]["meaning_id"] = "0" * 64
    for edit in (None, stale):
        meta, body = _meta(edit)
        lead = meta["scope"]["governors"][0]["effect"]["frame"]
        full = _written_in_full(meta)
        for r in full["reading_sets"][0]["readings"]:
            r["content"] = {"norm": {**r["content"]["part"], **lead}}
        governed, written = _rows(_text(meta, body)), _rows(_text(full, body))
        assert governed[0] is not None and written[0] is not None
        assert governed[0]["u0165.s03"]["status"] == written[0]["u0165.s03"]["status"] == "OPEN"


def test_render_shows_a_set_composed_per_choice_naming_its_unit(tmp_path):
    """Render reads GOVERN's two rules for u0165.s03, each keyed to its authored reading."""
    path = tmp_path / "sr1.ve.md"
    path.write_text(_doc())
    row = D._lean_answer(path.read_bytes(), True)
    assert [(s["set"], s["version"], s["unit"]) for s in row["composed_readings"]] == [(SET, 1, "u0165.s03")]
    assert [r["id"] for r in row["composed_readings"][0]["readings"]] == ["wide", "narrow"]
    assert [r["content"]["norm"]["sign"] for r in row["composed_readings"][0]["readings"]] == [False, False]
    shown = D.render_document(path)
    assert "This sentence could mean:" in shown and "One reading is:" in shown and "Another reading is:" in shown
    assert "u0165.s03's reading set is composed per choice" not in shown


def test_render_keeps_an_unrelated_set_as_authored(tmp_path):
    """An ungoverned set is absent from the new field and still renders its authored rule."""
    def unrelated(meta, rs):
        frame = meta["scope"]["governors"][0]["effect"]["frame"]
        rule = {**_part("wide")["part"], **frame, "name": "unrelated"}
        meta["reading_sets"].append({"id": "unrelated", "unit": "u0166.s01", "version": 1,
                                     "status": "open", "readings": [{"id": "alone", "kind": "norm",
                                     "meaning_id": "m", "content": {"norm": rule},
                                     "admission": {"who": "translator", "why": "open"}}]})
    path = tmp_path / "unrelated.ve.md"
    path.write_text(_doc(unrelated))
    row = D._lean_answer(path.read_bytes(), True)
    assert [s["set"] for s in row["composed_readings"]] == [SET]
    loaded = D.load_document(path)
    assert loaded["meta"]["reading_sets"][1]["readings"][0]["content"]["norm"]["name"] == "unrelated"
    assert D.render_document(path).count("One reading is:") == 2


def test_document_answer_keeps_two_governed_sets():
    """The document route relays every composed set when two list items hold sets."""
    def second(meta, rs):
        unit = next(u for u in meta["units"] if u["id"] == "u0165.s04")
        content = unit.pop("content")
        meta["reading_sets"].append({"id": "second", "unit": "u0165.s04", "version": 1,
                                     "status": "open", "readings": [{"id": "only", "kind": "norm", "meaning_id": "m",
                                     "content": content, "admission": {"who": "translator", "why": "part under scope"}}]})
    rows, answer = _rows(_doc(second))
    assert rows is not None, answer
    assert [(s["set"], s["unit"], [r["id"] for r in s["readings"]]) for s in answer["composed_readings"]] == [
        (SET, "u0165.s03", ["wide", "narrow"]), ("second", "u0165.s04", ["only"])]


def test_every_structural_mutant_of_the_sr1_answer_is_refused(tmp_path, monkeypatch):
    accepted, count = structural_mutants_accepted(tmp_path, monkeypatch, _doc())
    assert count > 200 and not accepted, accepted


def _rules_in_full(effect):
    """The review's F1 probe: three rules under a lead-in, rule b's unit u2 written without content and holding one
    set whose reading is the rule b written in full, which the governor (`effect`) changes."""
    from tests.test_scope_document import _governed_text
    meta, body = _split(_governed_text("norms", effect))
    meta["environment"]["profiles"] = sorted(meta["environment"]["profiles"] + ["readings@1"])
    meta["scope"]["governors"][0].update(unit="u0", reach={"list": "u0"}, units=["u1", "u2", "u3"])
    reading = {"id": "r", "kind": "norm", "meaning_id": "m", "content": meta["units"][2].pop("content"),
               "admission": {"who": "t", "why": "w"}}
    meta["reading_sets"] = [{"id": "s", "unit": "u2", "version": 1, "status": "open", "readings": [reading]}]
    return _text(meta, body)


@pytest.mark.parametrize("effect", ["reguard", "carve_out"])
def test_f1_a_composed_set_of_rules_in_full_answers_every_view(tmp_path, effect):
    """The readings routes, check, coverage and render all read GOVERN's composed rule."""
    from ve.readings_verdicts import context
    text = _rules_in_full(effect)
    assert _rows(text)[0] is not None
    path = tmp_path / "f1.ve.md"
    path.write_text(text)
    query = ["forall", "state", ["forall", "person", ["binary", "protect_required", ["var", 1], ["var", 0]]]]
    loaded = D.load_document(path)
    written = _split(text)[0]["reading_sets"][0]["readings"][0]["content"]
    composed = loaded["meta"]["reading_sets"][0]["readings"][0]["content"]
    assert composed["norm"] and composed != written
    assert D.check_document(path)["coverage"]["accounted_bytes"] > 0
    assert "One reading is:" in D.render_document(path)
    assert context(loaded).entailment(query)["verdict"] == ("NONE" if effect == "carve_out" else "ALL")


@pytest.mark.parametrize("field,value", [("set", "absent"), ("version", 2), ("version", True),
                                         ("unit", "absent"), ("reading", "absent"), ("extra", None),
                                         ("missing", None)])
def test_f1_the_composed_sets_are_bound_to_the_request(tmp_path, monkeypatch, field, value):
    from ve.backends import relay
    path = tmp_path / "sr1.ve.md"
    path.write_text(_doc())
    row = D._lean_answer(path.read_bytes(), True)
    changed = json.loads(json.dumps(row))
    target = changed["composed_readings"][0]
    if field == "reading":
        target["readings"][0]["id"] = value
    elif field == "extra":
        changed["composed_readings"].append(json.loads(json.dumps(target)))
    elif field == "missing":
        target["readings"].pop()
    else:
        target[field] = value
    monkeypatch.setattr(relay, "answer", lambda mode, case: (changed, None))
    with pytest.raises(CheckerUnavailable):
        D.load_document(path)


def _many_choices(meta, rs):
    """Two governed sets of 8 and 9 readings: 72 joint choices, above the limit of 64 (`VE.Scope.choiceLimit`)."""
    other = json.loads(json.dumps(rs))
    other.update(id="s5", unit="u0165.s05")
    meta["reading_sets"].append(other)
    next(u for u in meta["units"] if u["id"] == "u0165.s05").pop("content")
    for s, n in ((rs, 8), (other, 9)):
        s["readings"] = [{**s["readings"][0], "id": str(i)} for i in range(n)]


def test_f2_more_joint_choices_than_the_limit_is_leans_unknown_on_every_view(tmp_path):
    """Fix round 1 F2: Lean's `ResourceLimit: scope choices` (UNKNOWN, DELTA row 1) reaches every view, never the
    retained path's `UnsupportedProfile: scope@0`."""
    from ve.errors import ResourceLimit
    text = _doc(_many_choices)
    assert _rows(text) == (None, "ResourceLimit: scope choices")
    path = tmp_path / "f2.ve.md"
    path.write_text(text)
    for view in (D.load_document, D.check_document, D.render_document):
        with pytest.raises(ResourceLimit, match="^ResourceLimit: scope choices$"):
            view(path)


def test_f2_every_scope_resource_limit_is_leans(tmp_path):
    """The class of F2: a limit GOVERN reaches without any reading set (more than 256 governors) is Lean's too."""
    from tests.test_scope_document import _governed_text
    from ve.errors import ResourceLimit
    meta, body = _split(_governed_text("norms", "frame"))
    governor = meta["scope"]["governors"][0]
    meta["scope"]["governors"] = [{**governor, "id": f"g{i}"} for i in range(257)]
    path = tmp_path / "f2.ve.md"
    path.write_text(_text(meta, body))
    with pytest.raises(ResourceLimit, match="^ResourceLimit: scope governors$"):
        D.load_document(path)
