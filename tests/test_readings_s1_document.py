"""S1 through the document path (docs/spec/composition-s1.md 2, 4.8, 6, 9.4): content-bearing sets admitted by
Lean with Python's and Rust's agreement, situations found by Python's search and checked by Lean, the section 6
report, the verdict `superposition pending`, and the English of 2.3 rendered from checked data only.

Review findings B (Astra 4, Fable 4 and 5) and A (Fable 1): each wording below is a regression of "E14 to E24 are
never rendered from checked data"; E25 replaces E15 while `decision_only_sound` is unproved (DRI ruling 2).
"""
from __future__ import annotations

import json

import pytest

from tests.test_document import unit, write_doc
from tests.test_readings_s1_lean import env_k, norm, norm_object
from ve.ast import formula_from_data
from ve.document import check_document, load_document, render_document
from ve.errors import VEError
from ve.identity import meaning_id
from ve.readings import s1_content_meaning_id
from ve.readings_route import document_wire
from ve.readings_s1 import record_situations, search
from ve.softnorms import SoftEnvironment

SHALL = b"Agents shall avoid deceiving users."
ASKS_ALL = ["forall", "agent", ["forall", "user", ["binary", "asks", ["var", 1], ["var", 0]]]]


def candidate(env, set_id, cid, content, kind="norm"):
    reading = {"id": cid, "kind": kind, "content": content}
    mid = (s1_content_meaning_id(env, set_id, reading) if kind != "asserted"
           else meaning_id(env, formula_from_data(env, content)))
    return {**reading, "meaning_id": mid, "admission": {"who": "reviewer", "why": "two readings",
                                                        "distinguishing_models": {}}}


def s1_document(tmp_path, candidates, *, raw=None, fixed=(), source=SHALL, word=(7, 12), situations=None):
    """A document of one open set on `u1` and fixed norm units; every pair's situation is Python's search
    result (or `situations`, a function of the set), recorded before the document is written."""
    raw = raw or env_k()
    env = SoftEnvironment(raw)
    readings = [candidate(env, "rs1", cid, content, kind) for cid, content, kind in candidates]
    for reading in readings:
        reading["admission"]["distinguishing_models"] = {r["id"]: "pending" for r in readings
                                                         if r["id"] != reading["id"]}
    reading_set = {"id": "rs1", "unit": "u1", "version": 1, "status": "open", "readings": readings}
    if word is not None:
        reading_set["source_word"] = list(word)
    text = source + b"\n"
    units = [unit("u1", 0, len(text), "norm", "specified")]
    for n, (uid, content) in enumerate(fixed):
        sentence = f"Rule {n} applies.\n".encode()
        units.append(unit(uid, len(text), len(text) + len(sentence), "norm", "specified", content))
        text += sentence
    wire_units = [{"id": u["id"], "kind": u["kind"], "content": u["content"]} for u in units]
    if situations is None:
        found = search(raw, document_wire(wire_units, [reading_set]), "rs1")
        reading_set = record_situations(reading_set, {k: v for k, v in found.items() if v is not None})
    else:
        reading_set = situations(reading_set)
    return write_doc(tmp_path, text, units, environment_json=raw, reading_sets=[reading_set])


def strict(name="no-deception"):
    return ("strict", norm(name, "avoid_required", True), "norm")


def default(name="no-deception", **exception):
    content = norm(name, "avoid_required", True, "default")
    content["norm"]["exception"].update(exception)
    return ("default", content, "norm")


def rendered(path):
    return render_document(path)


def test_h1_g4_e14_with_e25_on_k1(tmp_path):
    path = s1_document(tmp_path, [strict(), default()])
    report = check_document(path)
    assert report["premises"] == {"status": "UNKNOWN", "reason": "superposition pending"}
    [pair] = report["readings"]["sets"][0]["pairs"]
    assert pair["wording"] == "E14"
    assert pair["text"] == (
        "This sentence says *shall*. (1) *Every agent must avoid deceiving each user.* (2) *Every agent should "
        "avoid deceiving each user.* They differ here: suppose the decider decides the exception applies to a "
        "and u. Under (1) a still must. Under (2) a is not required to. It is not certified that these two "
        "readings differ only where the decider decides that the exception applies.")
    assert "suppose the decider decides the exception applies" in pair["text"]
    assert "and the exception applies" not in pair["text"]
    assert "No situation separates them without that decision" not in rendered(path)
    readings = report["readings"]
    assert readings["findings"] == {"SeparatedByDecisionOnly": 1, "SeparatedByActOnly": 0}
    assert readings["sets"][0]["not_certified"] == ["SeparatedByDecisionOnly: rs1: 0, 1 (not certified)"]
    assert readings["separations"] == {"outcome": 1, "selects": 0, "holds": 0}
    assert "S2 route and restrictions" in readings["checked_by"]["lean"]
    residual = report["coverage"]["residual"]
    assert (residual["separations"], residual["readings_findings"], residual["pending_candidates"]) == (1, 1, 0)


def test_h2_h3_e19_on_k6_and_k14_without_e25(tmp_path):
    never = ("u0", norm("never-avoid", "avoid_required", False))
    path = s1_document(tmp_path / "k6", [strict(), default()], fixed=[never])
    [pair] = check_document(path)["readings"]["sets"][0]["pairs"]
    assert pair["wording"] == "E19"
    assert pair["text"] == ("These two readings differ here: a is an agent; u is a user. Under *should*, a is not "
                            "required to. Under *must* that is not so, whatever is decided.")
    asks = ["binary", "asks", ["var", 1], ["var", 0]]
    path = s1_document(tmp_path / "k14", [strict(), default(sufficient=[asks], necessary=[["bottom"]])])
    [pair] = check_document(path)["readings"]["sets"][0]["pairs"]
    assert pair["text"] == ("These two readings differ here: a is an agent; u is a user; a has the recorded "
                            "relation \"asks\" to u. Under *must*, a still must. Under *should*, this situation is "
                            "ruled out, whatever is decided.")
    assert "It is not certified" not in rendered(path)


def tmp(tmp_path, name):
    (tmp_path / name).mkdir()
    return tmp_path / name


@pytest.fixture(autouse=True)
def _dirs(tmp_path):
    for name in ("k6", "k14", "k12", "k13", "a", "b", "c", "d", "e"):
        (tmp_path / name).mkdir()


def test_h3_e19_case_3_on_k12_and_h5_e24_for_holds(tmp_path):
    cands = [("assert", ASKS_ALL, "asserted"), strict()]
    path = s1_document(tmp_path / "k12", cands)
    [pair] = check_document(path)["readings"]["sets"][0]["pairs"]
    assert pair["wording"] == "E19"
    assert "Under reading 1, a is not required to. Under reading 2, a still must." in pair["text"]

    def holds(reading_set):
        entry = {"base": {"domains": {"agent": ["a"], "user": ["u"]}, "constants": {}, "relations": {"asks": []}},
                 "fixed": [], "witness": "strict", "decisions": [], "probe": "holds", "value": True}
        from ve.readings_s1 import S1Environment
        sid = S1Environment(env_k()).situation_id(entry)
        out = json.loads(json.dumps(reading_set))
        for reading in out["readings"]:
            reading["admission"]["distinguishing_models"] = {r["id"]: sid for r in out["readings"]
                                                             if r["id"] != reading["id"]}
        out["situations"] = {sid: entry}
        return out
    path = s1_document(tmp_path / "k13", cands, situations=holds)
    report = check_document(path)
    [pair] = report["readings"]["sets"][0]["pairs"]
    assert (pair["wording"], pair["text"]) == ("E24", "These two readings differ in a checked situation that VE "
                                                      "cannot yet show in words.")
    assert report["readings"]["separations"]["holds"] == 1


def test_e21_between_two_assertions(tmp_path):
    not_asks = ["forall", "agent", ["forall", "user", ["not", ["binary", "asks", ["var", 1], ["var", 0]]]]]
    path = s1_document(tmp_path / "a", [("asks", ASKS_ALL, "asserted"), ("not-asks", not_asks, "asserted"),
                                        strict()])
    pairs = check_document(path)["readings"]["sets"][0]["pairs"]
    [e21] = [p for p in pairs if set(p["readings"]) == {"asks", "not-asks"}]
    assert e21["wording"] == "E21"
    assert e21["text"].endswith("the sentence is true there. Under reading 1, it is false there.") or \
        e21["text"].endswith("the sentence is true there. Under reading 2, it is false there.")


def test_h6_e16_on_k4(tmp_path):
    path = s1_document(tmp_path / "b", [("avoid", norm("avoid-x", "avoid_required", True), "norm"),
                                        ("help", norm("help-x", "help_required", True), "norm")])
    assert ("These two readings are about different acts: *avoid deceiving* / *help*. No situation separates "
            "them on a shared act.") in rendered(path)
    assert check_document(path)["readings"]["findings"]["SeparatedByActOnly"] == 1


def test_h4_e22_and_e23_only_under_their_conditions(tmp_path):
    asks = ["binary", "asks", ["var", 1], ["var", 0]]
    against = ("u0", {"norm": norm_object("never-avoid", "avoid_required", False, guard=asks)})
    text = check_document(s1_document(tmp_path / "c", [strict(), default()], fixed=[against]))
    [pair] = text["readings"]["sets"][0]["pairs"]
    assert pair["wording"] == "E14" and "(1) contradicts that rule and (2) gives way to it." in pair["text"]
    # K9: a strict rule that is an exception to the twin: no E22.
    exception = ("u0", {"norm": norm_object("except-x", "avoid_required", False, over=("no-deception",),
                                             guard=asks)})
    [pair] = check_document(s1_document(tmp_path / "d", [strict(), default()], fixed=[exception]))[
        "readings"]["sets"][0]["pairs"]
    assert "contradicts that rule" not in pair["text"]
    other = ("u0", {"norm": norm_object("lenient", "avoid_required", False, "default", guard=asks)})
    [pair] = check_document(s1_document(tmp_path / "e", [strict(), default()], fixed=[other]))[
        "readings"]["sets"][0]["pairs"]
    assert "Under (1), a rule on the same act that says should" in pair["text"]


def test_g6_g9_no_generated_name_and_no_may_not(tmp_path):
    path = s1_document(tmp_path, [strict(), default()], source=b"Agents may not deceive users.", word=(7, 14))
    text = rendered(path)
    pairs = check_document(path)["readings"]["sets"][0]["pairs"]
    assert pairs[0]["wording"] == "E19"
    s1_lines = [p["text"] for p in pairs]
    for sentence in s1_lines:
        assert not any(name in sentence for name in ("ve__", "rd-", "soft__", "rights__"))
        assert "may not" not in sentence
    assert "This sentence says" not in text


def test_the_search_finds_no_situation_for_renamed_twins(tmp_path):
    """F22, K3: a pair that differs only in a rule name has no situation; the set is refused by both."""
    path = s1_document(tmp_path, [("a", norm("no-deception-a", "avoid_required", True), "norm"),
                                  ("b", norm("no-deception-b", "avoid_required", True), "norm")])
    with pytest.raises(VEError, match="distinguishing model id does not match model"):
        load_document(path)
