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


def test_python_and_lean_agree_on_m1_route_choices_and_vocabulary(lean):
    from ve.readings_route import elaborate

    raw = env_k()
    document = k1(raw)
    row = elaborate(raw, document["units"], document["reading_sets"], executable=lean)
    assert row["route"] == "superposed"
    assert row["choices"] == [[["rs1", 0]], [["rs1", 1]]]
    assert row["slot"][0]["label"] == QUIET


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


def test_m2_slot_is_the_same_in_lean_python_and_rust(lean):
    """The three evaluators agree on M2's admitted bases and rejected quiet-premise base."""
    from ve.ast import formula_from_data
    from ve.backends.dispatch import pinned
    from ve.backends.rust_jsonl import run as rust_run
    from ve.environment import Environment
    from ve.evaluate import evaluate
    from ve.model import FiniteModel
    from ve.readings_route import elaborate

    raw = env_k()
    document = k1(raw)
    slot = elaborate(raw, document["units"], document["reading_sets"], executable=lean)["slot"][0]["ast"]
    shadow_environment = {**raw, "profiles": ["relational-fol@0"], "vocabulary": {
        "sorts": {**raw["vocabulary"]["sorts"], "ve__reading": {"description": "reading"}},
        "constants": {"ve__here": {"sort": "ve__reading", "description": "here"}},
        "predicates": {"asks": raw["vocabulary"]["predicates"]["asks"],
                       BIT: {"arguments": ["ve__reading"], "description": "choice"},
                       EX2: {"arguments": ["agent", "user"], "description": "exception"}}}}
    environment = Environment(shadow_environment)
    formula = formula_from_data(environment, slot)
    for bit, excepted, expected in [(False, False, True), (True, True, True), (False, True, False)]:
        shown = model(bit, excepted)
        [checked] = run(lean, [case("readings-model", raw, document, model=shown)])
        with pinned("python"):
            python_model = FiniteModel.from_dict(environment, shown)
            python_value = evaluate(environment, formula, python_model, trace=False).value
        rust = rust_run({"id": "m2", "kind": "readings-superposed-evaluate", "untrusted": True,
                         "environment": shadow_environment, "model": shown, "slot": [slot],
                         "assertions": [], "conflict_targets": [], "conclusions": []})
        assert rust["untrusted"] is True and rust["values"]["slot"] == [expected]
        assert python_value is expected
        assert checked["valid"] is expected


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
    from ve.readings_route import elaborate
    checked = elaborate(raw, document["units"], document["reading_sets"], executable=lean)
    assert checked["route"] == "enumerated" and checked["finding"] == elaborated["finding"]


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


def test_m4_countermodel_outcome_agrees_in_three_evaluators(lean):
    from copy import deepcopy

    from ve.ast import _to_data, formula_from_data
    from ve.backends.dispatch import pinned
    from ve.backends.rust_jsonl import run as rust_run
    from ve.environment import Environment
    from ve.evaluate import evaluate
    from ve.model import FiniteModel
    from ve.readings_s1 import Document, S1Environment
    from ve.readings_sup import choice_vocabulary, superposed_contents
    from ve.softnorms import SoftEnvironment, SoftNormDocument

    raw = env_k()
    document = k1_document(raw, fixed_units=[("u0", norm("help-x", "help_required", True))])[0]
    source = Document(S1Environment(raw), document)
    vocabulary = choice_vocabulary(source.sets)
    frame = deepcopy(source.senv.soft_frame().to_dict())
    for sort in vocabulary["sorts"]:
        frame["vocabulary"]["sorts"][sort] = {"description": sort}
    for name, sort in vocabulary["constants"].items():
        frame["vocabulary"]["constants"][name] = {"sort": sort, "description": name}
    for name, sorts in vocabulary["predicates"].items():
        frame["vocabulary"]["predicates"][name] = {"arguments": sorts, "description": name}
    soft = SoftNormDocument(SoftEnvironment(frame, generated=True),
                            [c.raw for c in superposed_contents(source) if c.kind == "norm"])
    base_outcome = _to_data(soft.elaborated.outcome("avoid_required", base=True))
    conclusion = ["forall", "agent", ["forall", "user", base_outcome]]
    shared = ["forall", "agent", ["forall", "user",
              ["binary", "avoid_required", ["var", 1], ["var", 0]]]]
    shown = model(True, True)
    [lean_row] = run(lean, [case("readings-model", raw, document, model=shown,
                                assumed=[["rs1", 1]], conclusion=shared)])
    shadow = {**raw, "profiles": ["relational-fol@0"], "vocabulary": {
        "sorts": frame["vocabulary"]["sorts"], "constants": frame["vocabulary"]["constants"],
        "predicates": {"asks": raw["vocabulary"]["predicates"]["asks"],
                       BIT: frame["vocabulary"]["predicates"][BIT],
                       EX2: {"arguments": ["agent", "user"], "description": "exception"}}}}
    environment = Environment(shadow)
    with pinned("python"):
        python_model = FiniteModel.from_dict(environment, shown)
        python_value = evaluate(environment, formula_from_data(environment, conclusion),
                                python_model, trace=False).value
    rust = rust_run({"id": "m4", "kind": "readings-superposed-evaluate", "untrusted": True,
                     "environment": shadow, "model": shown, "slot": [], "assertions": [],
                     "conflict_targets": [], "conclusions": [conclusion]})
    assert lean_row["valid"] is True and lean_row["conclusion_value"] is False
    assert python_value is False and rust["values"]["conclusions"] == [False]


def test_m5_narrowing_slot_and_choice_match_python(lean):
    from ve.readings_route import elaborate

    raw = env_k()
    document = k1(raw)
    document["units"].append({"id": "u2", "kind": "asserted", "content": ["top"]})
    narrowing = {"id": "n1", "set": "rs1", "version": 1, "keeps": ["strict"],
                 "by": "reviewer", "reason_spans": ["u2"]}
    [lean_row] = run(lean, [case("readings-elaborate", raw,
                                {**document, "narrowings": [narrowing]})])
    checked = elaborate(raw, document["units"], document["reading_sets"],
                        narrowings=[narrowing], executable=lean)
    assert checked == {key: value for key, value in lean_row.items() if key not in ("id", "status")}
    assert checked["route"] == "superposed" and checked["choices"] == [[["rs1", 0]]]
    assert [part["label"] for part in checked["slot"]] == [QUIET, "narrowing:n1"]


def test_m6_coupling_slot_agrees_in_three_evaluators(lean):
    """The coupled M6 choices and its distinguishing forbidden bit pair agree at all three sites."""
    from ve.ast import formula_from_data
    from ve.backends.dispatch import pinned
    from ve.backends.rust_jsonl import run as rust_run
    from ve.environment import Environment
    from ve.evaluate import evaluate
    from ve.model import FiniteModel
    from ve.readings_route import elaborate

    raw = env_k()
    document = k1(raw)
    for candidate, force in zip(document["reading_sets"][0]["readings"], ("strict", "default")):
        candidate["labels"] = {"force": force}
    probe = {"outcome": {"predicate": "help_required", "tuple": ["a", "u"]}}
    sigma = entry(M0, "default", probe, False,
                  decisions=[{"key": {"excepted": "be-kind"}, "tuples": [["a", "u"]]}])
    sid = situation_id(raw, sigma)
    second = reading_set("rs2", "u2", [
        reading("strict", norm("be-kind", "help_required", True), {"default": sid}),
        reading("default", norm("be-kind", "help_required", True, "default"), {"strict": sid})],
        {sid: sigma})
    for candidate, force in zip(second["readings"], ("strict", "default")):
        candidate["labels"] = {"force": force}
    document["units"].append({"id": "u2"})
    document["reading_sets"].append(second)
    coupling = {"id": "c1", "axis": "force", "sets": [
        {"set": "rs1", "version": 1}, {"set": "rs2", "version": 1}],
        "by": "reviewer", "reason_spans": ["u1"]}
    checked = elaborate(raw, document["units"], document["reading_sets"],
                        couplings=[coupling], executable=lean)
    assert checked["route"] == "superposed"
    assert checked["choices"] == [[['rs1', 0], ['rs2', 0]], [['rs1', 1], ['rs2', 1]]]
    assert [part["label"] for part in checked["slot"]] == [
        QUIET, "readings:rs2@1:1:quiet", "coupling:c1"]

    second_bit = "ve__bit__2__0"
    second_exception = "soft__excepted__rd_4_be_kind"
    vocabulary = checked["vocabulary"]
    shadow = {**raw, "profiles": ["relational-fol@0"], "vocabulary": {
        "sorts": {**raw["vocabulary"]["sorts"],
                  **{sort: {"description": sort} for sort in vocabulary["sorts"]}},
        "constants": {name: {"sort": sort, "description": name}
                      for name, sort in vocabulary["constants"].items()},
        "predicates": {"asks": raw["vocabulary"]["predicates"]["asks"],
                       **{part["name"]: {"arguments": part["arguments"], "description": part["name"]}
                          for part in vocabulary["predicates"]},
                       EX2: {"arguments": ["agent", "user"], "description": EX2},
                       second_exception: {"arguments": ["agent", "user"], "description": second_exception}}}}
    environment = Environment(shadow)
    slot = [part["ast"] for part in checked["slot"]]
    for first, second_bit_value, expected in ((False, False, True), (True, True, True),
                                               (False, True, False)):
        shown = {"complete": True,
                 "domains": {"agent": ["a"], "user": ["u"], "ve__reading": ["e"]},
                 "constants": {"ve__here": "e"},
                 "relations": {"asks": [], BIT: [["e"]] if first else [],
                               second_bit: [["e"]] if second_bit_value else [],
                               EX2: [["a", "u"]] if first else [],
                               second_exception: [["a", "u"]] if second_bit_value else []}}
        [lean_row] = run(lean, [case("readings-model", raw,
                                    {**document, "couplings": [coupling]}, model=shown)])
        with pinned("python"):
            python_model = FiniteModel.from_dict(environment, shown)
            python_values = [evaluate(environment, formula_from_data(environment, formula),
                                      python_model, trace=False).value for formula in slot]
        rust = rust_run({"id": "m6", "kind": "readings-superposed-evaluate", "untrusted": True,
                         "environment": shadow, "model": shown, "slot": slot,
                         "assertions": [], "conflict_targets": [], "conclusions": []})
        assert python_values == rust["values"]["slot"]
        assert lean_row["valid"] is expected and all(python_values) is expected
        if not expected:
            assert lean_row["first_failing"] == "coupling:c1"


def test_m8_precedence_leak_forces_enumeration(lean):
    """The fixed child cannot be run against both candidate copies at once."""
    from ve.readings_route import elaborate, validate

    raw = env_k()
    base = {**M0, "relations": {"asks": [["a", "u"]]}}
    sigma = entry(base, "b", Q0, False)
    sid = situation_id(raw, sigma)
    guard = ("binary", "asks", ["var", 1], ["var", 0])
    reading_set_ = reading_set("rs1", "u1", [
        reading("a", norm("waive-x", "avoid_required", False, guard=guard), {"b": sid}),
        reading("b", norm("waive-x", "avoid_required", False,
                          over=("base-x",), guard=guard), {"a": sid})], {sid: sigma})
    units = [{"id": "u0", "kind": "norm", "content": norm("base-x", "avoid_required", True)},
             {"id": "u1"},
             {"id": "u3", "kind": "norm", "content": norm("stop-x", "avoid_required", False,
                                                         over=("waive-x",))}]
    assert validate(raw, units, [reading_set_], executable=lean)["status"] == "ok"
    checked = elaborate(raw, units, [reading_set_], executable=lean)
    assert checked == {"route": "enumerated", "finding": {
        "text": "ReadingsNotSuperposable: rs1", "cause": "precedence under waive-x"},
        "choice_count": 2, "choices": [[['rs1', 0]], [['rs1', 1]]], "choices_checked": 2, "narrowings_stale": []}


# ---------------------------------------------------------------------------------------------------------------
# Review A1 (2026-10-03): no verdict over no reading (4.1 step 3)

EXPAND_CLOSE = {**CLOSE, "trace": {"rule": "expand", "at": 2, "children": [{"rule": "close"}]}}


def _both_narrowed(raw):
    """K1 with two narrowings in force on `rs1`, one keeping each candidate: no choice is compatible, and the slot
    holds `narrowing:keep-strict` = ¬b beside `narrowing:keep-default` = b."""
    document = k1(raw)
    document["units"].append({"id": "u2", "kind": "asserted", "content": ["top"]})
    document["narrowings"] = [
        {"id": "keep-strict", "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer", "reason_spans": ["u2"]},
        {"id": "keep-default", "set": "rs1", "version": 1, "keeps": ["default"], "by": "reviewer",
         "reason_spans": ["u2"]}]
    return document


def test_a1_unsatisfiable_readings_refused_before_any_verdict(lean):
    from ve.errors import VEError
    from ve.readings_route import elaborate

    raw = env_k()
    document = _both_narrowed(raw)
    text = "ReadingsUnsatisfiable: keep-default, keep-strict"
    certs = {"avoid_required": EXPAND_CLOSE, "help_required": EXPAND_CLOSE}
    rows = run(lean, [case("readings-elaborate", raw, document),
                      case("readings-certificate", raw, document, premises=[], conclusion=None,
                           conflict_certificates=certs, certificate=EXPAND_CLOSE),
                      case("readings-certificate", raw, document, premises=[], conclusion=SOME_ASKS,
                           conflict_certificates=certs, certificate=EXPAND_CLOSE),
                      case("readings-conflict", raw, document, conflict_certificates=certs),
                      case("readings-model", raw, document, model=model(True, True))])
    # Before the fix the certificate kinds accepted ⊥ with `conflict_free: true` over the inconsistent slot.
    assert all(row["status"] == "error" and row["error"] == text for row in rows), rows
    try:
        elaborate(raw, document["units"], document["reading_sets"], narrowings=document["narrowings"],
                  executable=lean)
    except VEError as exc:
        assert str(exc.message if hasattr(exc, "message") else exc) == text
    else:
        raise AssertionError("Python's elaboration admitted a document with no compatible choice")


def test_a1_one_narrowing_keeps_the_route(lean):
    raw = env_k()
    document = _both_narrowed(raw)
    document["narrowings"] = document["narrowings"][:1]
    [row] = run(lean, [case("readings-elaborate", raw, document)])
    assert row["status"] == "ok" and row["choices"] == [[["rs1", 0]]] and row["choices_checked"] == 1, row


# ---------------------------------------------------------------------------------------------------------------
# Review B1 / DRI ruling 5: the soft check of every compatible choice's document, run by the route


def test_ruling5_every_choice_document_checked(lean):
    from ve.readings_route import elaborate

    raw = env_k()
    document = k1(raw)
    [row] = run(lean, [case("readings-elaborate", raw, document)])
    assert row["route"] == "superposed" and row["choices_checked"] == 2
    checked = elaborate(raw, document["units"], document["reading_sets"], executable=lean)
    assert checked["choices_checked"] == 2


def test_ruling5_diagnostic_names_the_choice(monkeypatch):
    """A choice whose document the chain refuses is the chain's text under the choice, in source order (7)."""
    from ve import readings_s1
    from ve.readings_s1 import Document, S1Environment
    from ve.readings_sup import CHECK_BUDGET_TEXT, route_refusal

    raw = env_k()
    source = Document(S1Environment(raw), k1(raw))
    assert route_refusal(source, "superposed") is None
    calls = []

    def refuse(side):
        calls.append(side)
        return "ResourceLimit: generated background" if len(calls) == 2 else None

    monkeypatch.setattr(readings_s1.Side, "chain_text", refuse)
    assert route_refusal(source, "superposed") == "ResourceLimit: generated background under rs1@1:1"
    assert CHECK_BUDGET_TEXT == "ResourceLimit: more than 1024 readings to check"


def test_ruling5_over_budget_refuses_superposed_kinds(monkeypatch):
    """Past the budget no choice is checked, and the superposed verdict kinds would claim more than the check."""
    from ve import readings_sup
    from ve.readings_s1 import Document, S1Environment

    raw = env_k()
    source = Document(S1Environment(raw), k1(raw))
    monkeypatch.setattr(readings_sup, "MAX_CHOICE_CHECKS", 1)
    assert readings_sup.choices_checked(source.sets, "superposed") == "over 1"
    assert readings_sup.route_refusal(source, "superposed") is None
