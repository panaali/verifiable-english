"""The `english.statement` shadow comparator (docs/spec/en-e3-norm.md 2.4, Shadow; fixtures E14 and P5).

Each record of the shadow has exactly one class, from Python's outcome and Lean's checked answer; `lean-unavailable`
is tested first (verifier 3). The shadow runs only with `VE_STATEMENT_COMPARATOR=1` and `VE_SHADOW_LOG` both set. The
relay that feeds it and the saved delta report are en-e3bb's (reviews/dri-decisions-20261110-en-e3b.md item 1).
"""
from __future__ import annotations

import pytest

from tests.test_norms import environment, permission
from ve.english_grammar import codes, statement_codes
from ve.errors import CheckerUnavailable, SyntaxError
from ve.norm_english import parse_english, statement_class, statement_record, statement_shadow_log

NODE = {"name": "rule-1", "predicate": "in_scope", "sign": True, "guard": ["unary", "publicly_deployed", ["var", 0]],
        "unless": [], "over": []}


def refusal(status: str, code: str) -> dict:
    return {"status": status, "code": code, "text": "t", "class": codes()[0][code], "identities": {}}


def one(*nodes: dict) -> dict:
    return {"status": "one", "identities": {}, "statements": [
        {"kind": "rule", "number": i, "exception_to": [], "node": {"norm": node}, "span": [0, 1]}
        for i, node in enumerate(nodes, 1)]}


# E14's Lean answers by the class each takes when Python admits (section 8, from E1, E3, E6, E9, E11, E12, E16).
UNAVAILABLE = [refusal("rejected", "Internal"), refusal("invalidGrammar", "InvalidGrammar"),
               CheckerUnavailable("CheckerUnavailable: the answer is not bound to the request")]
UNKNOWN = [refusal("budget", "Budget"), refusal("rejected", "NodeLimit")]
STRICTER = [refusal("rejected", "NodeRefused"), refusal("rejected", "StrayConsequence"),
            refusal("none", "NoDerivation"), refusal("unformalised", "UnformalisedSpan"),
            refusal("invalidGrammar", "InvalidOverlay"), refusal("many", "Ambiguous")]
REFUSED = SyntaxError("Expected Rule 1 with its own block")


@pytest.mark.parametrize("lean", UNAVAILABLE, ids=repr)
def test_an_unavailable_answer_is_a_delta_row_whatever_python_did(lean):
    """verifier 3: a `CheckerUnavailable` answer (a relay failure, or a code of that class) is `lean-unavailable`
    when Python admits and when it refuses, never `both-refuse` or `lean-stricter`."""
    assert statement_class([NODE], lean) == statement_class(REFUSED, lean) == "lean-unavailable"


@pytest.mark.parametrize("lean", UNKNOWN + STRICTER, ids=repr)
def test_a_lean_refusal_is_classed_by_python_outcome(lean):
    """Python admits: a budget or ResourceLimit answer is `lean-unknown` (not a rejection), any other refusal
    `lean-stricter`; Python refuses: `both-refuse`, UNKNOWN included."""
    assert statement_class([NODE], lean) == ("lean-unknown" if lean in UNKNOWN else "lean-stricter")
    assert statement_class(REFUSED, lean) == "both-refuse"


def test_a_lean_reading_is_compared_by_position():
    """E1's `one`: `agree` when the nodes are equal after both sides name rule i `rule-i` (Python's names follow
    `existing_names`), `different-node` when they differ, `lean-looser` when Python refuses."""
    second = {**NODE, "name": "rule-2", "over": ["rule-1"]}
    renamed = [{**NODE, "name": "rule-7"}, {**second, "name": "rule-8", "over": ["rule-7"]}]
    assert statement_class(renamed, one(NODE, second)) == "agree"
    assert statement_class([NODE, {**second, "over": []}], one(NODE, second)) == "different-node"
    assert statement_class([{**NODE, "sign": False}], one(NODE)) == "different-node"
    assert statement_class([NODE], one(NODE, second)) == "different-node"
    assert statement_class(REFUSED, one(NODE)) == "lean-looser"


def test_a_record_holds_both_outcomes_and_one_class():
    record = statement_record("Rule 1. X.", REFUSED, refusal("rejected", "NodeRefused"))
    assert record == {"source_sha256": "b9f1e10dd9b146f928cd661dd716561decb1c7b41a7cf58e9680e90ff3ce94e1",
                      "python": {"class": "SyntaxError", "message": str(REFUSED)},
                      "lean": {"status": "rejected", "code": "NodeRefused", "nodes": []}, "class": "both-refuse"}
    assert statement_record("Rule 1. X.", [NODE], one(NODE))["lean"]["nodes"] == [NODE]
    assert statement_record("", [NODE], UNAVAILABLE[2])["lean"] == {"status": "unavailable",
                                                                    "message": str(UNAVAILABLE[2])}


def test_the_shadow_needs_both_flags(monkeypatch, tmp_path):
    """P5: with `VE_STATEMENT_COMPARATOR=1` and `VE_SHADOW_LOG` unset, Lean is not called and no file is written in
    the working directory; the log is the path `VE_SHADOW_LOG` names only when both are set."""
    from ve.backends import relay
    from ve.backends.lean_service import LeanService
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VE_STATEMENT_COMPARATOR", "1")
    monkeypatch.delenv("VE_SHADOW_LOG", raising=False)
    modes = []

    def recording(original, at):
        def call(*args, **kwargs):
            modes.append(args[at])
            return original(*args, **kwargs)
        return call
    for owner, name, at in ((relay, "decide_once", 0), (relay, "decide", 0), (LeanService, "run", 1)):
        monkeypatch.setattr(owner, name, recording(getattr(owner, name), at))
    env = environment({"permitted": permission()})
    assert statement_shadow_log() is None
    document = parse_english(env, "Rule 1. Every act may be done.")
    assert [rule.name for rule in document.rules] == ["rule-1"]
    assert "english.statement" not in modes and list(tmp_path.iterdir()) == []
    monkeypatch.setenv("VE_SHADOW_LOG", str(tmp_path / "shadow.jsonl"))
    assert statement_shadow_log() == tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_STATEMENT_COMPARATOR", "0")
    assert statement_shadow_log() is None


def test_the_statement_tables_are_the_lean_export():
    """`statement_codes()` reads english.statement's tables from codes.json: the field table has exactly the code
    table's statuses (`Run.statementFields_statuses`), every EN-2 code is classed (the render codes are EN-3's
    rows), and a rejection's optional members are `sentence` and `span`."""
    statuses, fields, unsentenced = statement_codes()
    classes = codes()[0]
    assert list(fields) == list(statuses) and "rendered" in statuses
    assert {code for found in statuses.values() for code in found} - set(classes) == {
        "RenderUnread", "RenderMismatch", "NoWording", "InvalidInput"}
    assert fields["rejected"] == (("code", "text", "class"), ("sentence", "span"))
    assert fields["one"] == (("statements",), ()) and "NodeRefused" in unsentenced
