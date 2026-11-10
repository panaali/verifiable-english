"""The `ask` fixtures (docs/spec/question-answering.md 7.2, 7.4, 7.5; plan Q2.2: "from recorded evidence files, no
generator in the test").

Each fixture's request (the route's case with its evidence, and the reading names) was recorded by
`tools/ask_fixtures.py --write` from the untrusted generators; here it is replayed through Lean's `ask` mode, the
answer checked by the relay against the request (`ve.ask.answer_problem`), and compared with the whole recorded answer
(the version the loader puts back from `ve/english_grammar/LOCK.json` included) and with what the spec says of it: the lead, the cited sentences, the reading blocks, the unused-sentence line. A
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
    assert AF.differences(entry["result"], result) == [], ident
    assert EXPECT[ident](result), (ident, result["text"])
    assert result["text"][0].startswith("You asked whether ")


def test_the_agent_policy_answers_replay():
    """The zero-set route on the agent-policy documents (one test: each document's admission is slow)."""
    for ident in AGENT:
        entry = AF.load(ident)
        result = AF.replay(entry)
        assert AF.differences(entry["result"], result) == [], ident
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


# The fixture format (arch-20261105-2): no run-time `seconds` and no copy of `actions_version`; the loader puts the
# lock's version back, and the replay compares every field, the version included.


def _lock(directory, version):
    """A copy of `ve/english_grammar/LOCK.json` in `directory` with another `actions_version`."""
    lock = json.loads((ROOT / "ve/english_grammar/LOCK.json").read_text())
    (directory / "LOCK.json").write_text(json.dumps({**lock, "actions_version": version}))
    return directory


def test_the_loader_takes_the_version_from_the_lock(tmp_path, monkeypatch):
    from ve import english_grammar
    stored = json.loads((ROOT / "tests/fixtures/ask/G1.json").read_text())
    assert "actions_version" not in stored["result"]["identities"] and "seconds" not in stored
    assert AF.load("G1")["result"]["identities"]["actions_version"] == english_grammar.actions_version()
    monkeypatch.setattr(english_grammar, "HERE", _lock(tmp_path, "999"))
    entry = AF.load("G1")
    assert entry["result"]["identities"]["actions_version"] == "999"
    # Only the version is added: every other identity is the stored one, in the stored order.
    assert list(entry["result"]["identities"]) == sorted(entry["result"]["identities"])
    assert {k: v for k, v in entry["result"]["identities"].items() if k != "actions_version"} == stored["result"][
        "identities"]


def test_an_answer_under_another_version_than_the_locks_fails_the_replay(tmp_path, monkeypatch):
    """Lean answers under `Fixed.actionsVersion`; a lock that says another version (a raised lock with a stale build,
    or the reverse) makes the replay differ at the version and nowhere else. Under the real lock it replays."""
    from ve import english_grammar
    with monkeypatch.context() as patch:
        patch.setattr(english_grammar, "HERE", _lock(tmp_path, "999"))
        entry = AF.load("G1")
    result = AF.replay(entry)
    assert result["identities"]["actions_version"] == english_grammar.actions_version() != "999"
    assert AF.differences(entry["result"], result) == ["/identities/actions_version"]
    assert AF.differences(AF.load("G1")["result"], result) == []


def _leaves(value, at=()):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _leaves(item, (*at, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _leaves(item, (*at, index))
    yield at


def _set(value, at, new):
    copy_ = copy.deepcopy(value)
    node = copy_
    for step in at[:-1]:
        node = node[step]
    node[at[-1]] = new
    return copy_


def test_the_replay_compares_every_field_of_the_answer():
    """Each field of a genuine answer of each route, retyped, changed or dropped, is a difference at its path; the
    genuine answer has none. `true` is not `1` and `1` is not `1.0`, as JSON has them."""
    for ident in ("G1", "U3", "A1"):
        recorded = AF.load(ident)["result"]
        assert AF.differences(recorded, copy.deepcopy(recorded)) == []
        for at in _leaves(recorded):
            if not at:
                continue
            path = "/" + "/".join(map(str, at))
            node = recorded
            for step in at:
                node = node[step]
            for new in ([] if isinstance(node, list) else [7], "x" if node != "x" else "y", None):
                if type(new) is type(node) and new == node:
                    continue
                assert AF.differences(recorded, _set(recorded, at, new)) == [path], (ident, path, new)
            if isinstance(at[-1], str):
                dropped = copy.deepcopy(recorded)
                parent = dropped
                for step in at[:-1]:
                    parent = parent[step]
                del parent[at[-1]]
                assert AF.differences(recorded, dropped) == [path], (ident, path)
        assert AF.differences({"n": 1}, {"n": True}) == ["/n"] and AF.differences({"n": 1}, {"n": 1.0}) == ["/n"]
        assert AF.differences({"a": [1]}, {"a": [1, 1]}) == ["/a"] and AF.differences({}, {"extra": 0}) == ["/extra"]


@pytest.mark.parametrize("old", ["seconds", "actions_version", "both"])
def test_a_fixture_in_the_old_format_is_refused_by_name(old, tmp_path, monkeypatch):
    """A branch that recorded fixtures before this format merges loudly: the loader names the field and the
    command that records the fixture again. The same fixture in the new format loads."""
    entry = json.loads((ROOT / "tests/fixtures/ask/G1.json").read_text())
    (tmp_path / "G1.json").write_text(json.dumps(entry))
    monkeypatch.setattr(AF, "OUT", tmp_path)
    assert AF.load("G1")["result"]["lead"] == "yes"
    if old in ("seconds", "both"):
        entry["seconds"] = 1.5
    if old in ("actions_version", "both"):
        entry["result"]["identities"]["actions_version"] = AF.lock_version()
    (tmp_path / "G1.json").write_text(json.dumps(entry))
    with pytest.raises(ValueError, match=r"tools/ask_fixtures\.py --write G1") as refused:
        AF.load("G1")
    assert ("seconds" in str(refused.value)) == (old != "actions_version")
    assert ("result/identities/actions_version" in str(refused.value)) == (old != "seconds")


def test_every_recorded_fixture_is_in_the_current_format():
    for ident, _, _ in AF.FIXTURES:
        stored = json.loads((ROOT / f"tests/fixtures/ask/{ident}.json").read_text())
        assert AF.old_format(stored) == [], ident
        AF.load(ident)


def test_a_record_stores_no_version_and_refuses_another_version_than_the_locks():
    answer = {"lead": "yes", "identities": {"actions_version": AF.lock_version(), "document_id": "d"}}
    assert AF.stored(answer) == {"lead": "yes", "identities": {"document_id": "d"}}
    with pytest.raises(SystemExit, match="build Lean"):
        AF.stored({**answer, "identities": {**answer["identities"], "actions_version": "999"}})
