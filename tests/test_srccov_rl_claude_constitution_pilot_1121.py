"""srccov-rl-claude-constitution-pilot-1121: the three 'translation omission' units are reading choices, not omissions.

The source-coverage map (manage-agents reviews/source-coverage-1119, pin e53db4e8fc) tags three constitution sentences
'none: translation omission': S0443 (row 22), S0553 (row 23) and S0941 (row 42). Its shards could not count
`reading_sets` as carriers (its amendment 3). Each sentence's probe unit is a norm with no body because its force is an
open reading set with two candidates (`strict`, `default`). The two candidates use the same predicate and differ in
content. A single rule line would pick one of them, and a document has exactly one reading, never a guessed one. So
the item carries none of the three and drops each (docs/infra/srccov-rl-claude-constitution-pilot-1121/REPORT.md).

These tests hold the drop's reason. Each source sentence is read from the pinned translation's body (`tests/ce4`,
checked against its commit's blob) at the map's byte offsets and checked by its first and last words after the
project's quote normalisation (`tests.omission_rule.omit_norm`). Its probe unit must be inside that sentence. The unit
must have no body while its reading set is open with at least two different candidates on the unit's predicate. No
other unit's body may state that predicate. Across the probe, no unit may have both a body and an open reading set.
A later item that settles a reading closes or removes the set; it then gives the unit its body and changes this file.
The search, the model service and git are not called.
"""
from __future__ import annotations

import json

import pytest

from tests import ce4
from tests.omission_rule import REPO, omit_norm

PROBE = REPO / "usecases/claude-constitution-pilot/run-20261119-defs-carry/probe-translation.probe.md"
ROW = "srccov-claude-constitution-pilot-{}-1119"
# (map row, source unit, its bytes in the pinned body, its first and last words, the probe unit, its reading set,
# the predicate both candidates regulate)
DROPPED = (
    (22, "S0443", 77794, 77936, "Still, Claude should never directly deny", "seriously mislead the user.",
     "u0125.s04.p2", "force-u0125-s04-p2", "denial_of_being_claude_permitted"),
    (23, "S0553", 95093, 95192, "Claude shouldn’t actively deceive the user", "a system prompt or its content.",
     "u0156.s03", "force-u0156-s03", "system_prompt_deception_permitted"),
    (42, "S0941", 163742, 163859, "And in situations where Claude has explicitly", "it should comply.",
     "u0263.s04.p2", "force-u0263-s04-p2", "exploit_instruction_compliance_required"),
)
IDS = [f"{ROW.format(r[0])}:{r[1]}" for r in DROPPED]


def flat(units):
    for u in units:
        yield u
        yield from flat(u.get("children") or u.get("parts") or [])


@pytest.fixture(scope="module")
def probe():
    """The carried probe's front matter, its units by id and its reading sets by id, and the pinned body."""
    _, front, body = PROBE.read_bytes().split(b"---\n", 2)
    _, _, source = ce4.pinned_bytes().split(b"---\n", 2)
    assert body == source
    meta = json.loads(front)
    return meta, {u["id"]: u for u in flat(meta["units"])}, {s["id"]: s for s in meta["reading_sets"]}, source


@pytest.mark.parametrize("row", DROPPED, ids=IDS)
def test_the_probe_unit_lies_inside_the_source_sentence(probe, row):
    _, units, _, source = probe
    _, _, a, b, first, last, uid, _, _ = row
    text = omit_norm(source[a:b].decode("utf-8"))
    assert text.startswith(omit_norm(first)) and text.endswith(omit_norm(last)), text[:80]
    start, stop = units[uid]["span"]
    assert a <= start < stop <= b + 2, uid  # a unit's span may keep the line break after the sentence
    assert omit_norm(source[start:stop].decode("utf-8")) in text, uid


@pytest.mark.parametrize("row", DROPPED, ids=IDS)
def test_the_unit_has_no_body_while_its_reading_set_is_open(probe, row):
    """The drop's reason: the force of the sentence is still an open choice between different candidates."""
    _, units, sets, _ = probe
    *_, uid, set_id, predicate = row
    unit = units[uid]
    assert unit["kind"] == "norm" and "content" not in unit, uid
    reading_set = sets[set_id]
    assert reading_set["unit"] == uid and reading_set["status"] == "open", set_id
    contents = [r["content"] for r in reading_set["readings"]]
    assert {r["id"] for r in reading_set["readings"]} >= {"strict", "default"}, set_id
    assert all(c["norm"]["predicate"] == predicate for c in contents), set_id
    assert len({json.dumps(c, sort_keys=True) for c in contents}) == len(contents) >= 2, set_id


@pytest.mark.parametrize("row", DROPPED, ids=IDS)
def test_no_other_unit_states_the_open_predicate(probe, row):
    """No rule line elsewhere picks a reading by stating the predicate the open set regulates."""
    _, units, _, _ = probe
    predicate = row[-1]
    assert [uid for uid, u in units.items() if predicate in json.dumps(u.get("content", ""))] == []


def test_no_unit_has_both_a_body_and_an_open_reading_set(probe):
    _, units, sets, _ = probe
    assert {s["unit"] for s in sets.values() if s["status"] == "open"} >= {r[6] for r in DROPPED}
    assert [s["unit"] for s in sets.values() if s["status"] == "open" and "content" in units[s["unit"]]] == []
