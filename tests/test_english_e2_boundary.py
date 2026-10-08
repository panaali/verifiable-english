"""The E2 boundary validates every block its typing view drops (review B2 of English Lean E2; spec D7).

`english.read` reads formulas against the typing view of an environment, which drops the declarations of the
statement layers `speech-acts@0`, `reports@0` and `readings@1`. Before it drops them, the boundary validates
them as submitted with each route's own environment decoder, as S3 did for `alternatives@0` and `risk@0`. So a
request whose statement-layer declarations a route refuses is refused here too, even when it does not come
through Python's `Environment` (whose own checks run first on the admission path).
"""
from __future__ import annotations

import copy

import pytest

from ve import Environment
from ve import english as EN
from ve.backends import english_lean as L
from ve.backends import relay
from ve.profiles import LANGUAGE, SPEC_REVISION


def speech() -> dict:
    return {
        "language": LANGUAGE, "spec_revision": SPEC_REVISION,
        "profiles": ["norms@0", "relational-fol@0", "speech-acts@0"],
        "speech_acts": {"task": "t1", "addressee": {"sort": "user", "constant": "alice"}},
        "vocabulary": {
            "sorts": {s: {"description": s} for s in ("user", "service")},
            "predicates": {"reviewed": {"arguments": ["service"], "description": "reviewed",
                                        "verbalisation": "{0} is reviewed"}},
            "constants": {"alice": {"sort": "user", "description": "alice"},
                          "atlas": {"sort": "service", "description": "atlas"}}}}


def reports() -> dict:
    return {
        "language": LANGUAGE, "spec_revision": SPEC_REVISION, "profiles": ["relational-fol@0", "reports@0"],
        "vocabulary": {
            "reports": {"holders": ["person", "text"], "evidence": "evidence"},
            "sorts": {s: {"description": s} for s in ("person", "text", "evidence")},
            "predicates": {"safe": {"arguments": ["person"], "description": "safe",
                                    "verbalisation": "{0} is safe"}},
            "constants": {"article": {"sort": "text", "description": "article"},
                          "alice": {"sort": "person", "description": "Alice"},
                          "e1": {"sort": "evidence", "description": "evidence"}}}}


def readings() -> dict:
    return {
        "language": LANGUAGE, "spec_revision": SPEC_REVISION,
        "profiles": ["norms@0", "readings@1", "relational-fol@0"],
        "vocabulary": {
            "sorts": {"service": {"description": "service"}},
            "predicates": {"reviewed": {"arguments": ["service"], "description": "reviewed",
                                        "verbalisation": "{0} is reviewed"}},
            "constants": {"atlas": {"sort": "service", "description": "atlas"}}}}


SOURCES = {"speech": (speech, "Atlas is reviewed."), "reports": (reports, "Alice is safe."),
           "readings": (readings, "Atlas is reviewed.")}

# One malformed declaration per layer, each refused by its route's decoder.
def _no_scope_task(raw):
    del raw["speech_acts"]["task"]


def _unknown_scope_field(raw):
    raw["speech_acts"]["colour"] = "red"


def _evidence_unknown(raw):
    raw["vocabulary"]["reports"]["evidence"] = "nowhere"


def _holders_repeated(raw):
    raw["vocabulary"]["reports"]["holders"] = ["person", "person"]


def _reports_with_norms(raw):
    raw["profiles"] = ["norms@0", "relational-fol@0", "reports@0"]


def _readings_without_norms(raw):
    raw["profiles"] = ["readings@1", "relational-fol@0"]


MALFORMED = {"speech": [_no_scope_task, _unknown_scope_field], "reports": [_evidence_unknown, _holders_repeated,
                                                                           _reports_with_norms],
             "readings": [_readings_without_norms]}


def _row(raw: dict, source: str) -> dict:
    env = Environment(raw)
    case = L.request(env, source, EN.EnglishVocabulary(env), {})
    return env, case


@pytest.mark.parametrize("layer", sorted(SOURCES))
def test_a_valid_statement_layer_environment_is_read(layer):
    build, source = SOURCES[layer]
    env, case = _row(build(), source)
    [row] = relay.rows("english.read", [case])
    assert row["status"] == "ok" and row["result"]["status"] == "one", row
    assert row["result"]["identities"]["environment_id"] == env.environment_id


@pytest.mark.parametrize("layer, change", [(layer, change) for layer, changes in sorted(MALFORMED.items())
                                           for change in changes], ids=lambda x: getattr(x, "__name__", x))
def test_a_malformed_statement_layer_declaration_is_refused_at_the_boundary(layer, change):
    """Review B2: the typing view drops these declarations, so the boundary must decode them first. The request
    is built from a valid environment and then given the malformed one, as a caller that skips Python's
    `Environment` would send it."""
    build, source = SOURCES[layer]
    _, case = _row(build(), source)
    bad = copy.deepcopy(build())
    change(bad)
    with pytest.raises(Exception):
        Environment(bad)  # Python's own validation refuses it too, on the admission path
    [row] = relay.rows("english.read", [{**case, "environment": bad}])
    assert row["status"] == "error", row
