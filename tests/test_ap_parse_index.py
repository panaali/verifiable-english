"""ap-parse-index: reading an act phrase stays within the 5 s CPU deadline at D-31's 128 frames (DRI 2026-11-09 ap-4
item 2, ap-parse-index items 1 and 2).

The act grammar is built in near-linear time and its rule table read once per request, so a request with many frames
is answered, or refused by the step budget as a deterministic `LIMIT`, never `CheckerUnavailable`. Each request below
runs under its mode's own CPU deadline (`DEADLINES`, `_CORE`: 5 s), so an answer means it ended within it; before this
item L6 with 126 frames more needed 305 s of CPU (docs/act-phrases/ap-parse-index/REPORT.md). The steps, which grow by
1,984 per frame, are `#guard`s in `lean/VE/Acts/GrammarExamples.lean`.
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


def test_the_400_byte_phrase_is_listed_with_two_frames_and_a_step_limit_with_32():
    """ap-4 condition (a): at most 2 frames, `LISTED` as before; with 32 frames the step budget, a `LIMIT`."""
    assert len(P400.encode()) == 400
    assert ask(P400, block={"frames": [frame("seek")]})["verdict"] == "LISTED"
    assert ask(P400, block={"frames": V5["frames"]})["verdict"] == "LISTED"
    over = ask(P400, block={"frames": [frame("seek")] + PAD[:31]})
    assert over == {"verdict": "LIMIT", "tokens": [], "readings": [],
                    "diagnostic": "ResourceLimit: this act phrase has too many readings to list; split the sentence"}


def norms(frames):
    """The `norms` route's answer, under its CPU deadline, to the joined act of `test_acts_joined_route`."""
    case = {"id": "c", "kind": "norms-elaborate", "environment": environment(NORM_PROFILES, frames=frames),
            "norms": [RULE]}
    with LeanService(lean_build("ve_service") / "ve_service") as service:
        _, response = service.exchange("norms", json.dumps([case], separators=(",", ":")), 1)
    return response["results"][0]["result"]


def test_a_norms_document_with_128_frames_reads_its_joined_act():
    row = norms((FRAME,) + tuple(PAD))
    assert [t["target"] for t in row["conflict_targets"]] == ["p027__1", "p027__2"]


def test_a_norms_document_with_129_frames_is_a_resource_limit():
    row = norms((FRAME,) + tuple(PAD) + (frame("seekzz"),))
    assert row["error"] == "ResourceLimit: more than 128 frames"
