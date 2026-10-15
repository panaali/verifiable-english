"""The `ask` fixtures (docs/spec/question-answering.md 7.2, 7.4, 7.5; plan Q2.2: "from recorded evidence files, no
generator in the test").

Each fixture's request (the route's case with its evidence, and the reading names) was recorded by
`tools/ask_fixtures.py --write` from the untrusted generators; here it is replayed through Lean's `ask` mode, the
answer checked by the relay against the request (`ve.ask.answer_problem`), and compared with the recorded answer and
with what the spec says of it: the lead, the cited sentences, the reading blocks, the unused-sentence line. A
fixture whose spec lead was only *derived* (spec 7.2, 7.4, 7.5) records the lead Lean gives on the recorded
evidence; the differences are listed in docs/spec/question-answering-q2-report.md.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from ve.errors import CheckerUnavailable, VEError

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("ask_fixtures", ROOT / "tools/ask_fixtures.py")
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)

FAST = ["G1", "G2", "G3", "G4", "G10", "U2", "U3", "U5", "U6", "U7"]
AGENT = ["A1", "A2", "A3", "A4", "A5", "A7", "A8"]
UNUSED_U = ("VE did not use 9 sentences of this document that it could not read formally: "
            "sentences 3, 5, 6, 7, 8, 11, 17, 18 and 19.")


def units(result, choice=None):
    """The units a row cites, in order (of the row of `choice`, else of the only row)."""
    rows = result["rows"] if choice is None else [r for r in result["rows"] if r["choice"] == choice]
    [row] = rows
    return [s.get("unit") or s.get("predicate") for s in row["cited"]]


def leads_by(result, set_id):
    """{index of `set_id`: the set of leads of the rows reading it so}."""
    out = {}
    for row in result["rows"]:
        out.setdefault(dict(row["choice"])[set_id], set()).add(row["lead"])
    return out


EXPECT = {
    # G (plain adapter): spec 7.2.
    "G1": lambda r: r["lead"] == "yes" and units(r) == ["g1", "g2"] and r["text"][:2] == [
        "You asked whether every member is eligible.", "Yes."],
    "G2": lambda r: r["lead"] == "yes" and units(r) == ["g1", "g2"],
    "G3": lambda r: r["lead"] == "notNecessarily" and r["text"][2].startswith(
        "Here is a situation the document allows where it fails: "),
    "G4": lambda r: r["lead"] == "no" and units(r) == ["g1", "g2"] and r["text"][1] == "No. The document rules this out.",
    "G10": lambda r: r["lead"] == "yes" and units(r) == ["g1", "g2"],
    # U (readings route): spec 7.5.
    "U2": lambda r: r["lead"] == "yes" and r["text"][1:] == [
        "Yes.", 'Sentence 14 says: "and higher education shall be equally accessible to all on the basis of merit."',
        "Every way of reading the document gives this answer.", UNUSED_U],
    "U3": lambda r: r["lead"] == "by_reading" and leads_by(r, "rs_u096") == {0: {"notSettled"}, 1: {"yes"}} and
        'If sentence 10 means "Every person must be spared exclusion from education" (VE has not checked this '
        "wording), yes." in r["text"] and 'Sentence 10 says: "1. Everyone has the right to education."' in r["text"]
        and r["text"].count(UNUSED_U) == 1 and r["text"][-1] == UNUSED_U,
    "U5": lambda r: r["lead"] == "by_reading" and leads_by(r, "rs_u087") == {
        0: {"notSettled"}, 1: {"notSettled"}, 2: {"yes"}} and r["text"][-1] == UNUSED_U,
    "U6": lambda r: r["lead"] == "yes" and r["text"][1:] == [
        "Yes.", 'Sentence 12 says: "Elementary education shall be compulsory."',
        "Every way of reading the document gives this answer.", UNUSED_U],
    "U7": lambda r: r["lead"] == "by_reading" and {row["lead"] for row in r["rows"]} == {"notSettled", "unknown"},
    # A (zero-set route): spec 7.4, on the recorded evidence.
    "A1": lambda r: r["lead"] == "notSettled" and r["text"][-1] == 'The text does not say whether "a27" may be performed.',
    "A2": lambda r: r["lead"] == "unknown" and r["rows"][0]["reason"] == "X4",
    "A3": lambda r: r["lead"] == "notNecessarily",
    "A4": lambda r: r["lead"] == "unknown" and r["rows"][0]["reason"] == "X4",
    "A5": lambda r: r["lead"] == "unknown" and r["rows"][0]["reason"] == "X1" and r["text"][2].startswith(
        "The document's rules or defaults conflict in this situation, so VE cannot answer: "),
    "A7": lambda r: r["lead"] == "notSettled",
    "A8": lambda r: r["lead"] == "notSettled",
}


@pytest.mark.parametrize("ident", FAST)
def test_a_recorded_answer_replays_and_says_what_the_spec_says(ident):
    entry = AF.load(ident)
    result = AF.replay(entry)
    assert result == entry["result"], ident
    assert EXPECT[ident](result), (ident, result["text"])
    assert result["text"][0].startswith("You asked whether ")


def test_the_agent_policy_answers_replay():
    """The zero-set route on the agent-policy documents (one test: each document's admission is slow)."""
    for ident in AGENT:
        entry = AF.load(ident)
        result = AF.replay(entry)
        assert result == entry["result"], ident
        assert EXPECT[ident](result), (ident, result["text"])


def test_the_deny_document_is_refused_with_leans_reason():
    """A1d: a `norms@0` document without `norm-defaults@0` but with `data@0` flags is outside every route of ask."""
    entry = AF.load("A1d")
    assert entry["error"]["class"] == "UnsupportedProfile"
    assert "data flags" in entry["error"]["message"]


def test_every_fixture_of_the_spec_is_recorded():
    assert {ident for ident, _, _ in AF.FIXTURES} == set(FAST) | set(AGENT) | {"A1d"} == set(EXPECT) | {"A1d"}


def test_a_replay_can_fail():
    """The comparison is not vacuous: without G1's certificate Lean cannot say yes; without U3's splits the readings
    whose countermodel turns on a gap are only "not necessarily"; with G1's question over G3's case Lean refuses."""
    g1 = AF.load("G1")
    no_proof = copy.deepcopy(g1)
    del no_proof["case"]["evidence"]["certificate"]
    assert AF.replay(no_proof)["lead"] != "yes"
    u3 = AF.load("U3")
    no_split = copy.deepcopy(u3)
    for entry in no_split["case"]["evidence"]:
        entry.pop("split", None)
    assert leads_by(AF.replay(no_split), "rs_u096")[0] == {"notNecessarily"}
    other = copy.deepcopy(g1)
    other["case"] = AF.load("G3")["case"]
    with pytest.raises(VEError, match="does not ask this question"):
        AF.replay(other)


def test_a_case_of_another_document_is_not_this_documents():
    """The binding (5.2 `CaseBinding`): the UDHR case sent with the G document is refused before any replay."""
    g1 = AF.load("G1")
    swapped = copy.deepcopy(g1)
    swapped["case"] = AF.load("U6")["case"]
    with pytest.raises(CheckerUnavailable, match="the case is not this document's"):
        AF.replay(swapped)
    # An environment the replay could not even decode is refused as another document's, before the replay.
    undecodable = copy.deepcopy(g1)
    undecodable["case"]["environment"]["vocabulary"]["constants"]["cy"] = {"sort": "nosuch", "description": "x"}
    with pytest.raises(CheckerUnavailable, match="another environment"):
        AF.replay(undecodable)
    edited = copy.deepcopy(g1)
    edited["case"]["document"]["units"][0]["content"] = ["unary", "verified", ["const", "bo"]]
    with pytest.raises(CheckerUnavailable, match="a unit differs"):
        AF.replay(edited)
    environment = copy.deepcopy(g1)
    environment["case"]["environment"]["vocabulary"]["constants"]["cy"] = {"sort": "member", "description": "a member"}
    with pytest.raises(CheckerUnavailable, match="another environment"):
        AF.replay(environment)


def test_the_recorded_fixtures_are_the_tools_list():
    names = sorted(p.stem for p in (ROOT / "tests/fixtures/ask").glob("*.json") if not p.stem.startswith("packages-"))
    assert names == sorted(ident for ident, _, _ in AF.FIXTURES)
    for p in (ROOT / "tests/fixtures/ask").glob("packages-*.json"):
        assert json.loads(p.read_text()).keys() == {"packages"}
