"""ap-3db: a joined act under `acts@0` on the routes that elaborate it (act-phrases 6.4, DRI 2026-11-02 ap-3db).

The norms and norm-defaults routes run on the elaborated document, so their answers name the parts and never the
source predicate. Nothing relays this yet (ap-3dc): each case goes to the service directly, and `Environment(data)`
still refuses a joined act (`tests/test_acts_profile.py`). The Lean fixtures are in `lean/VE/Service/ActsExamples.lean`
and `lean/VE/Acts/DecodeExamples.lean`.
"""
from __future__ import annotations

import json

import pytest

from tests.lean_build import lean_build
from tests.subprocesses import HANG_TIMEOUT
from ve.backends.lean_service import LeanService

ACT = "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment"
FIXED = "cruel, inhuman or degrading treatment or punishment"
FRAME = {"head": "subjected", "markers": ["to"], "split": ["to"], "modifiers": []}
NORM_PROFILES = ["acts@0", "norms@0", "relational-fol@0"]
DEFAULT_PROFILES = ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
RULE = {"norm": {"name": "r027", "predicate": "p027", "sign": False, "guard": ["top"], "unless": [], "over": []}}


def environment(profiles, act=ACT, default="deny", frames=(FRAME,)):
    return {"language": "ve.core@0.2", "profiles": profiles, "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"person": {"description": "person"}}, "constants": {},
                           "acts": {"fixed": [FIXED], "frames": list(frames), "adverbs": []},
                           "predicates": {"p027": {"arguments": ["person"], "description": "d", "regulated": {
                               "role": "permission", "default": default, "act": act}}}}}


def ask(mode, case):
    """The service's answer to one raw case."""
    text = json.dumps([{"id": "c", **case}], ensure_ascii=False, separators=(",", ":"))
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as service:
        _, response = service.exchange(mode, text, 1, timeout=HANG_TIMEOUT)
    return response["results"][0]["result"]


def targets(row):
    return [t["target"] for t in row["conflict_targets"]]


def test_the_norms_route_answers_a_joined_act_with_its_parts_and_never_the_source():
    row = ask("norms", {"kind": "norms-elaborate", "environment": environment(NORM_PROFILES), "norms": [RULE]})
    assert targets(row) == ["p027__1", "p027__2"]
    assert '"p027"' not in json.dumps(row["conflict_targets"])


def test_the_norms_conflict_case_reads_the_parts():
    row = ask("norms", {"kind": "norms-conflict", "environment": environment(NORM_PROFILES), "norms": [RULE],
                        "packages": {}})
    assert row["targets"] == ["p027__1", "p027__2"]
    assert row["verdict"] == "UNKNOWN"


def test_the_norm_defaults_route_answers_with_the_parts():
    row = ask("norm-defaults", {"kind": "norm-defaults-elaborate", "norms": [RULE],
                                "environment": environment(DEFAULT_PROFILES, default="unspecified")})
    assert targets(row) == ["p027__1", "p027__2"]


def test_a_lexical_act_keeps_its_predicate():
    row = ask("norms", {"kind": "norms-elaborate", "norms": [RULE],
                        "environment": environment(NORM_PROFILES, act="{0} be held")})
    assert targets(row) == ["p027"]


@pytest.mark.parametrize("frames,text", [
    ((), "InvalidInput: act phrase for p027 has no reading under the declared frames"),
    ((FRAME, FRAME), "InvalidInput: frame 'subjected' is declared twice"),
])
def test_a_joined_act_the_frames_do_not_read_is_refused_with_the_spec_text(frames, text):
    row = ask("norms", {"kind": "norms-elaborate", "environment": environment(NORM_PROFILES, frames=frames),
                        "norms": [RULE]})
    assert row["error"] == text


def test_a_joined_act_with_no_rule_is_refused_not_read_as_one_predicate():
    row = ask("norms", {"kind": "norms-elaborate", "environment": environment(NORM_PROFILES), "norms": []})
    assert row["error"] == "InvalidInput: the joined act of p027 has no rule to read it by"
