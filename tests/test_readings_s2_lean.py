"""Lean readings route, S2a case kinds (docs/spec/composition-s2.md 3, 8.5) on the fixtures of 9.2.

Every expectation is derived from the spec: K1's superposed document (M1), its bases (M2) and K1 with K6's fixed
strict rule (M3). The Lean executable decodes the environment and the document, builds `sup D`, and answers each
case kind from checks whose soundness the wire theorems state (`readings_wire_all_sound`,
`readings_wire_model_sound`). A model is the finite-model wire form over `sup D`'s base vocabulary: the frame's
sorts and `ve__reading`, the constant `ve__here`, the bits and the decision predicates of `sup D`.
"""
from __future__ import annotations

from tests.test_readings_s1_lean import (M0, Q0, entry, env_k, k1_document, lean, norm, reading,  # noqa: F401
                                         reading_set, run, situation_id)

EX2 = "soft__excepted__rd_2_no_deception"
BIT = "ve__bit__1__0"
QUIET = "readings:rs1@1:1:quiet"
CLOSE = {"checker_version": "ve-tableau-checker@2", "environment_id": "-", "premise_meaning_ids": [],
         "conclusion_meaning_id": "-", "trace": {"rule": "close"}}
SOME_ASKS = ["exists", "agent", ["exists", "user", ["binary", "asks", ["var", 1], ["var", 0]]]]


def model(bit, ex2):
    """M2's bases: `m0` with `ve__reading` = {e} and `ve__here` = e."""
    return {"complete": True, "domains": {"agent": ["a"], "user": ["u"], "ve__reading": ["e"]},
            "constants": {"ve__here": "e"},
            "relations": {"asks": [], BIT: [["e"]] if bit else [], EX2: [["a", "u"]] if ex2 else []}}


def k1(raw, *, never=False):
    if never:
        return k1_document(raw, situation=entry(M0, "default", Q0, False),
                           fixed_units=[("u0", norm("never-avoid", "avoid_required", False))])[0]
    return k1_document(raw)[0]


def case(kind, raw, document, **fields):
    return {"id": kind, "kind": kind, "environment": raw, "document": document, **fields}


def test_m1_elaboration(lean):
    raw = env_k()
    [row] = run(lean, [case("readings-elaborate", raw, k1(raw))])
    assert row["status"] == "ok", row
    assert row["route"] == "superposed" and row["finding"] is None
    assert row["choices"] == [[["rs1", 0]], [["rs1", 1]]] and row["choice_count"] == 2
    assert row["slot"] == [{"label": QUIET, "ast": [
        "forall", "agent", ["forall", "user", ["implies", ["binary", EX2, ["var", 1], ["var", 0]],
                                              ["unary", BIT, ["const", "ve__here"]]]]]}]
    [names] = row["names"]
    strict, default = names["candidates"]
    assert strict["names"] == [["no-deception", "rd-1-no-deception"]] and strict["position"] == 1
    assert default["names"] == [["no-deception", "rd-2-no-deception"],
                                ["soft__excepted__no_deception", EX2]] and default["position"] == 2
    rules = [u["content"]["norm"] for u in row["units"]]
    assert [(r["name"], r["mode"]) for r in rules] == [("rd-1-no-deception", "strict"), ("rd-2-no-deception", "default")]
    assert rules[0]["guard"] == ["and", ["top"], ["not", ["unary", BIT, ["const", "ve__here"]]]]
    assert rules[1]["guard"] == ["and", ["top"], ["unary", BIT, ["const", "ve__here"]]]


def test_m2_models_encode_one_choice_and_the_quiet_premise(lean):
    raw = env_k()
    document = k1(raw)
    rows = run(lean, [case("readings-model", raw, document, model=model(True, True)),
                      case("readings-model", raw, document, model=model(False, False)),
                      case("readings-model", raw, document, model=model(False, True))])
    b1, b0, b2 = rows
    assert b1["valid"] is True and b1["choice"] == [["rs1", 1]] and b1["first_failing"] is None, b1
    assert b0["valid"] is True and b0["choice"] == [["rs1", 0]] and b0["first_failing"] is None, b0
    # B2: ex2 holds at (a, u) with the bit false, so the quiescence premise fails; not a model of any reading.
    assert b2["valid"] is False and b2["first_failing"] == QUIET, b2
    # The default conclusion is the premise model's ⊥.
    assert b1["conclusion_value"] is False


def test_m3_conflict_witness_names_the_choice(lean):
    raw = env_k()
    document = k1(raw, never=True)
    witness = {"model": model(False, False), "target": "avoid_required", "tuple": ["a", "u"]}
    calm = {"model": model(True, True), "target": "avoid_required", "tuple": ["a", "u"]}
    rows = run(lean, [case("readings-conflict", raw, document, witness=witness),
                      case("readings-conflict", raw, document, witness=calm),
                      case("readings-conflict", raw, document)])
    conflict, unknown, uncertified = rows
    # Choice 0: rd-1-no-deception and never-avoid both select at (a, u).
    assert conflict == {"id": "readings-conflict", "status": "ok", "verdict": "CONFLICT", "target": "avoid_required",
                        "assumed": [], "choice": [["rs1", 0]]}
    # Choice 1 with the exception taken: only never-avoid selects; this model witnesses nothing.
    assert unknown["verdict"] == "UNKNOWN" and unknown["choice"] == [["rs1", 1]]
    # No conflict certificate: the status is not CONFLICT-FREE.
    assert uncertified["verdict"] == "UNKNOWN"
    assert uncertified["targets"] == ["avoid_required", "help_required"]
    assert uncertified["reading_premises"] == [QUIET]


def test_certificate_needs_conflict_freedom(lean):
    raw = env_k()
    rows = run(lean, [case("readings-certificate", raw, k1(raw), premises=[SOME_ASKS], conclusion=SOME_ASKS,
                           certificate=CLOSE),
                      case("readings-certificate", raw, k1(raw), premises=[], conclusion=SOME_ASKS,
                           certificate=CLOSE)])
    proved, unproved = rows
    # The certificate checks on sup D's premises, but nothing is accepted without certified conflict-freedom.
    assert proved["valid"] is True and proved["conflict_free"] is False and proved["accepted"] is False, proved
    assert unproved["valid"] is False and unproved["accepted"] is False, unproved


def test_dead_and_unsatisfiable_need_a_certificate(lean):
    raw = env_k()
    rows = run(lean, [case("readings-dead", raw, k1(raw), set="rs1", index=0, certificate=CLOSE),
                      case("readings-dead", raw, k1(raw), certificate=CLOSE)])
    assert rows[0] == {"id": "readings-dead", "status": "ok", "accepted": False, "finding": None}
    assert rows[1] == {"id": "readings-dead", "status": "ok", "accepted": False, "finding": None}


def test_choice_runs_the_lower_route_on_the_choice_document(lean):
    raw = env_k()
    [row] = run(lean, [case("readings-choice", raw, k1(raw), choice=[["rs1", 1]], inner={"kind": "soft-elaborate"})])
    assert row["status"] == "ok" and row["choice"] == [["rs1", 1]], row
    assert row["inner"]["status"] == "ok"
    assert [d["name"] for d in row["inner"]["decisions"]] == ["soft__excepted__no_deception"]
    [bad] = run(lean, [case("readings-choice", raw, k1(raw), choice=[["rs1", 5]], inner={"kind": "soft-elaborate"})])
    assert bad["status"] == "error" and "not a compatible complete choice" in bad["error"]


def test_assumed_reading_must_be_a_candidate(lean):
    raw = env_k()
    [row] = run(lean, [case("readings-conflict", raw, k1(raw), assumed=[["rs1", 7]])])
    assert row == {"id": "readings-conflict", "status": "error", "error": "InvalidInput: assumed reading is no candidate"}


def test_m16_generated_name_over_64_bytes_in_sup_only(lean):
    """DRI ruling 2: a candidate's own decision name fits (62 bytes), its qualified copy in sup D does not (67)."""
    raw = env_k()
    name = "a" * 46
    sigma = entry(M0, "default", Q0, False, decisions=[{"key": {"excepted": name}, "tuples": [["a", "u"]]}])
    sid = situation_id(raw, sigma)
    rs1 = reading_set("rs1", "u1", [
        reading("strict", norm(name, "avoid_required", True), {"default": sid}),
        reading("default", norm(name, "avoid_required", True, "default"), {"strict": sid})], {sid: sigma})
    document = {"units": [{"id": "u1"}], "reading_sets": [rs1]}
    validated, elaborated = run(lean, [case("readings-validate", raw, document),
                                       case("readings-elaborate", raw, document)])
    assert validated["status"] == "ok", validated
    assert elaborated["route"] == "enumerated", elaborated
    assert elaborated["finding"] == {"text": "ReadingsNotSuperposable: rs1",
                                     "cause": "ResourceLimit: decision predicate soft__excepted__rd_2_" + name}


def test_m4_countermodel_under_should(lean):
    """M4's model part: B1 of M2 under [(rs1, 1)] is the countermodel to φ′ (SOME), and satisfies φ."""
    raw = env_k()
    document = k1_document(raw, fixed_units=[("u0", norm("help-x", "help_required", True))])[0]
    every = lambda p: ["forall", "agent", ["forall", "user", ["binary", p, ["var", 1], ["var", 0]]]]  # noqa: E731
    rows = run(lean, [case("readings-model", raw, document, model=model(True, True), assumed=[["rs1", 1]],
                           conclusion=every("avoid_required")),
                      case("readings-model", raw, document, model=model(True, True), assumed=[["rs1", 1]],
                           conclusion=every("help_required")),
                      case("readings-model", raw, document, model=model(True, True), assumed=[["rs1", 0]],
                           conclusion=every("avoid_required"))])
    counter, holds, wrong_reading = rows
    assert counter["valid"] is True and counter["conclusion_value"] is False and counter["choice"] == [["rs1", 1]]
    assert holds["valid"] is True and holds["conclusion_value"] is True
    # The model encodes choice 1, so the assumed atom of candidate 0 fails.
    assert wrong_reading["valid"] is False and wrong_reading["first_failing"] == "readings:rs1:0"
