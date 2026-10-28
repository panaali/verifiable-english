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
        forged = answer("document", {"id": "d", "document": text, "admit": True, "reading_sets": []})
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


def test_render_refuses_a_set_composed_per_choice_naming_its_unit(tmp_path):
    """Render shows each reading, which here is a part Lean composes: not relayed yet (sc-5rc), so unavailable, with
    the unit main's refusal named (DELTA row 2)."""
    path = tmp_path / "sr1.ve.md"
    path.write_text(_doc())
    with pytest.raises(CheckerUnavailable, match="u0165.s03's reading set is composed per choice"):
        D.render_document(path)


def test_every_structural_mutant_of_the_sr1_answer_is_refused(tmp_path, monkeypatch):
    accepted, count = structural_mutants_accepted(tmp_path, monkeypatch, _doc())
    assert count > 200 and not accepted, accepted
