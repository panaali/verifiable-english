"""ap-parse-index: reading an act phrase stays within the 5 s CPU deadline at D-31's 128 frames (DRI 2026-11-09 ap-4
item 2, ap-parse-index items 1 and 2).

The act grammar is built in near-linear time and its rule table read once per request, so a request with many frames
is answered, or refused by the step budget as a deterministic `LIMIT`, never `CheckerUnavailable`. Each request below
runs under its mode's own CPU deadline (`DEADLINES`, `_CORE`: 5 s), so an answer means it ended within it; before this
item L6 with 126 frames more needed 479 s of CPU (docs/act-phrases/ap-parse-index/REPORT.md). The steps, which grow by
1,984 per frame, are `#guard`s in `lean/VE/Acts/ParseIndexExamples.lean`.
"""
from __future__ import annotations

import json

import pytest

from tests import lean_routes
from tests.lean_build import lean_build
from tests.test_acts_joined_route import FRAME, NORM_PROFILES, RULE, environment
from tests.test_acts_readings_lean import CITIES, V5, ask, frame
from ve.backends.lean_service import LeanService

pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="ve_service is not built")

L6 = "{0} to seek and to enjoy asylum" + "".join(" in " + c for c in CITIES[:6])
P400 = "{0} to seek" + " a" * 193 + " ab"
LETTERS = "abcdefghijklmnopqrstuvwxyz"
PAD = [frame(f"seek{LETTERS[i // 26]}{LETTERS[i % 26]}") for i in range(127)]


@pytest.mark.parametrize("more", [0, 30, 62, 124, 126])
def test_l6_reads_the_same_64_readings_with_up_to_128_frames(more):
    """The growing fixture: 2, 32, 64, 126 and 128 frames; the frames added read nothing in L6."""
    found = ask(L6, CITIES, {"frames": V5["frames"] + PAD[:more]}, role="obligation")
    assert found == ask(L6, CITIES, V5, role="obligation")
    assert found["verdict"] == "LISTED" and len(found["readings"]) == 64


@pytest.mark.parametrize("more", [31, 127])
def test_the_400_byte_phrase_is_listed_with_two_frames_and_a_step_limit_with_32_or_128(more):
    """ap-4 condition (a): at most 2 frames, `LISTED` as before; with 32 or 128 frames the step budget, a `LIMIT`
    (DRI 2026-11-09 ap-parse-index-2: the 128-frame case within the deadline)."""
    assert len(P400.encode()) == 400
    assert ask(P400, block={"frames": [frame("seek")]})["verdict"] == "LISTED"
    assert ask(P400, block={"frames": V5["frames"]})["verdict"] == "LISTED"
    over = ask(P400, block={"frames": [frame("seek")] + PAD[:more]})
    assert over == {"verdict": "LIMIT", "tokens": [], "readings": [],
                    "diagnostic": "ResourceLimit: this act phrase has too many readings to list; split the sentence"}


def norms(frames, acts=0):
    """The `norms` route's answer, under its CPU deadline, to the joined act of `test_acts_joined_route` and `acts`
    more joined acts, each with its rule."""
    env = environment(NORM_PROFILES, frames=frames)
    rules = [RULE]
    for i in range(acts):
        env["vocabulary"]["predicates"][f"q{i}"] = {"arguments": ["person"], "description": "d", "regulated": {
            "role": "permission", "default": "deny", "act": f"{{0}} to {PAD[i]['head']} asylum or refuge"}}
        rules.append({"norm": {**RULE["norm"], "name": f"s{i}", "predicate": f"q{i}"}})
    case = {"id": "c", "kind": "norms-elaborate", "environment": env, "norms": rules}
    with LeanService(lean_build("ve_service") / "ve_service") as service:
        _, response = service.exchange("norms", json.dumps([case], separators=(",", ":")), 1)
    return response["results"][0]["result"]


def test_a_norms_document_with_128_frames_reads_its_joined_act():
    row = norms((FRAME,) + tuple(PAD))
    assert [t["target"] for t in row["conflict_targets"]] == ["p027__1", "p027__2"]


def test_a_norms_document_reads_63_joined_acts_with_one_grammar():
    """`actsOf` builds the grammar once for all the acts: 63 joined acts (the most regulated predicates the route reads)
    under 128 frames are read within the deadline (one grammar per act took 4.85 s for 16 acts)."""
    targets = [t["target"] for t in norms((FRAME,) + tuple(PAD), acts=62)["conflict_targets"]]
    assert targets[:2] == ["p027__1", "p027__2"] and sorted(targets[2:]) == sorted(f"q{i}" for i in range(62))


def test_a_norms_document_with_129_frames_is_a_resource_limit():
    row = norms((FRAME,) + tuple(PAD) + (frame("seekzz"),))
    assert row["error"] == "ResourceLimit: more than 128 frames"


# F1 (ap-parse-index review): 128 frames with 64 modifiers each. Building this vocabulary's grammar takes about three
# times the route's deadline (the review's 32 modifiers cost about the deadline itself), so an act that never needs
# the grammar must never build it (`Acts.lazyReader`); such an act is answered in a tenth of the deadline.
MARKS = [f"q{x}{y}{z}" for x in LETTERS for y in LETTERS for z in LETTERS]
WIDE = tuple(frame(f"seek{LETTERS[i // 26]}{LETTERS[i % 26]}", modifiers=MARKS[64 * i:64 * i + 64]) for i in range(128))
JOINED_SLOT = "InvalidInput: act phrase for p027 has a slot joined to a word"


@pytest.mark.parametrize("act,arity,answer", [
    ("{0} be held", 1, ["p027"]),  # lexical: accepted by `Lexical.check`, never joined (Acts/Wire.lean checkActBy)
    ("{0} be held,", 1, "InvalidInput: act phrase for p027 ends with a comma"),  # lexical refusal
    ("{0} seek {1}s and enjoy asylum", 2, JOINED_SLOT),  # joined, refused before its listing (joinedActBy)
    ("{0} seek asylum and enjoy x{1}", 2, JOINED_SLOT),
    # No regulated predicate: under acts@0 a regulated predicate must carry an act, so this is the document whose
    # declarations have no act. `actsOf` runs on the empty list while the environment is decoded (`joinedActs`),
    # before the norm is refused.
    (None, 1, "UnknownSymbol: regulated predicate p027"),
])
def test_an_act_that_needs_no_grammar_is_answered_under_a_vocabulary_whose_grammar_is_slow(act, arity, answer):
    """The decoder builds the vocabulary's reader only when a joined act is listed, and shares it from then on: a
    lexical act, a lexical refusal, a slot joined to a word and a declaration without an act are answered under the route's CPU deadline, as on main
    (before the fix `actsOf` built the reader first and the lexical act was `CheckerUnavailable` at 5 s)."""
    env = environment(NORM_PROFILES, act=act, frames=WIDE)
    env["vocabulary"]["predicates"]["p027"]["arguments"] = ["person"] * arity
    if act is None:
        del env["vocabulary"]["predicates"]["p027"]["regulated"]
    case = {"id": "c", "kind": "norms-elaborate", "environment": env, "norms": [RULE]}
    with LeanService(lean_build("ve_service") / "ve_service") as service:
        _, response = service.exchange("norms", json.dumps([case], separators=(",", ":")), 1)
    row = response["results"][0]["result"]
    assert (row.get("error") or [t["target"] for t in row["conflict_targets"]]) == answer
