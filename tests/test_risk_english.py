"""Fixture k19 (risk.md 2.1 to 2.3, 8.2): the gate of the risk English surface.

Each accepted wording has one derivation, one formula and its canonical
rendering; each rejected wording gives its rewrite in documents and in rule
guards alike; the scoped rewrites of "every … cannot lead to" parse to the two
formulas of 2.3; rule 2 of 2.5 has one derivation with alt's binder; P3's
compact coordination is rejected (k22 uses its strict text); c5 is registered
in risk-wording-probe-2's frozen wording "If <condition>, <action> leads to
<harm>", parses, renders and round-trips, and the first probe's trailing form is
rejected with that rewrite. Review B3, A4, B7, C11.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests import lean_routes

from conformance.risk import (Log, agent_ops, agent_ops_rules, asimov_risk, cell_env, condition, estimate, gt, q,
                              record)
from ve import ast
from ve.ast import formula_to_data
from ve.english import EnglishVocabulary, parse_english_with_metadata, render_english
from ve.environment import Environment
from ve.errors import CheckerUnavailable, UnsupportedProfile, VEError
from ve.norm_english import parse_english as parse_norm
from ve.surface.risk import SUFFICIENT_REWRITE, parse_wording, render_wording

ROOT = Path(__file__).resolve().parents[1]
BIN = "ve_risk_route"  # its service mode, through tests/lean_routes.py
HARMS = {"outage": ("an outage", "serious"), "loss": ("loss", "severe"), "delay": ("a delay", "minor")}


def _diagnostic_text(error):
    """E2 keeps rewrite advice separate from Lean's canonical diagnostic text."""
    reading = getattr(error, "lean_reading", None)
    advice = reading.response.get("advice") if reading is not None else None
    return str(error) + (" " + advice["text"] if advice else "")


def ops_raw():
    """agent-ops over one-word harm constants, without the W6 extension (see test_units_fail_closed)."""
    raw = agent_ops(harms=HARMS, extra_constants={
        "run": {"sort": "action", "description": "run"}, "wait": {"sort": "action", "description": "wait"},
        "bot": {"sort": "agent", "description": "bot"}})
    del raw["unit_schema"], raw["units"]
    for field in ("quantity_kinds", "required_estimators"):
        del raw["risk"][field]
    return raw


@pytest.fixture(scope="module")
def ops():
    return Environment(ops_raw())


def const(name):
    return ast.Const(name)


def b(p, x, y):
    return ast.Binary(p, const(x), const(y))


@pytest.mark.parametrize("text,formula", [
    ("run might lead to loss", b("risk__might_lead_to", "run", "loss")),                       # c1
    ("run cannot lead to loss", ast.Not(b("risk__might_lead_to", "run", "loss"))),             # c2
    ("run leads to loss", b("leads_to", "run", "loss")),                                      # c3a
    ("run might not lead to loss", ast.Not(b("leads_to", "run", "loss"))),                    # c4
    ("loss is severe", b("risk__class", "loss", "severe")),                                   # c8
    ("loss is serious or worse", b("risk__or_worse", "loss", "serious")),                     # c8
    ("wait has a less severe worst case than run", b("risk__less_worst", "wait", "run")),     # c9
    ("loss is avoidable by bot", b("avoidable", "loss", "bot")),                              # c10
    ("run allows loss to happen", b("allows", "run", "loss")),                                # c11
    ("run might prevent loss", b("prevents", "run", "loss")),                                 # c12
])
def test_each_wording_has_one_reading_and_renders_canonically(ops, text, formula):
    parsed = parse_english_with_metadata(ops, text + ".").document.formulas
    assert parsed == (formula,)
    assert render_english(formula, ops) == text[0].upper() + text[1:]


def test_alt_negative_cell_wording_stays_and_renders_might_not(ops):
    """2.3: `It is not the case that <action> leads to <harm>.` stays accepted and renders as c4."""
    formula = parse_english_with_metadata(ops, "It is not the case that run leads to loss.").document.formulas[0]
    assert formula == ast.Not(b("leads_to", "run", "loss"))
    assert render_english(formula, ops) == "Run might not lead to loss"


REJECTED = [
    ("may lead to", "Use 'might lead to': 'may' is permission."),
    ("does not lead to", "Choose 'cannot lead to' or 'might not lead to'."),
    ("could lead to", "Use 'might lead to' for possibility"),
    ("risks", "Use 'might lead to' for possibility"),
    ("is likely to lead to", "Use 'might lead to' for possibility"),
    ("increases the risk of", "Use 'might lead to' for possibility"),
    ("certainly leads to", "Use 'leads to' for certainty"),
    ("prevents", "Use 'might prevent' in a risk environment."),
]


@pytest.mark.parametrize("verb,rewrite", REJECTED)
def test_rejected_wordings_in_documents_and_rule_guards(ops, verb, rewrite):
    """Review B7: the rewrites of 2.3 also appear in rule guards (the cut phrase had no trailing space)."""
    with pytest.raises(VEError) as caught:
        parse_english_with_metadata(ops, f"run {verb} loss.")
    assert rewrite in _diagnostic_text(caught.value)
    with pytest.raises(VEError, match=rewrite):
        parse_norm(ops, f"Rule 1. Every action must not be performed, if that action {verb} loss.")


def test_is_safer_than_in_documents_and_rule_guards(ops):
    with pytest.raises(VEError) as caught:
        parse_english_with_metadata(ops, "wait is safer than run.")
    assert "has a less severe worst case than" in _diagnostic_text(caught.value)
    with pytest.raises(VEError, match="has a less severe worst case than"):
        parse_norm(ops, "Rule 1. Every action must not be performed, if that action is safer than wait.")


def test_every_cannot_offers_both_scoped_rewrites(ops):
    """2.3 and k37: both rewrites, each parsing to its formula."""
    for index, (parse, text) in enumerate(((lambda t: parse_english_with_metadata(ops, t),
                         "every action available to bot cannot lead to loss."),
                        (lambda t: parse_norm(ops, "Rule 1. Every action must not be performed, if " + t),
                         "every action available to bot cannot lead to loss."))):
        with pytest.raises(VEError) as caught:
            parse(text)
        message = str(caught.value)
        every_not = ("it is not the case that there is an action such that both that action is available to bot "
                     "and that action might lead to loss")
        not_every = "there is an action such that both that action is available to bot and that action cannot lead to loss"
        # Lean's text names both rewrites with the sentence's own chooser and harm (review B2), as Python's did
        assert every_not in message and not_every in message and "risk-every-cannot" not in message
    available = ast.Binary("available", ast.Var(0), const("bot"))
    might = ast.Binary("risk__might_lead_to", ast.Var(0), const("loss"))
    assert parse_english_with_metadata(ops, every_not[0].upper() + every_not[1:] + ".").document.formulas == (
        ast.Not(ast.Exists("action", ast.And(available, might))),)
    assert parse_english_with_metadata(ops, not_every[0].upper() + not_every[1:] + ".").document.formulas == (
        ast.Exists("action", ast.And(available, ast.Not(might))),)


def test_condition_wording_in_a_rule_is_record_only(ops):
    head = "Rule 1. Every action must not be performed, if that action cannot lead to loss"
    with pytest.raises(VEError, match="is a record statement"):
        parse_norm(ops, head + " unless that action leads to a delay.")
    with pytest.raises(VEError, match="is a record statement"):
        parse_norm(ops, "Rule 1. Every action must not be performed, if that action leads to loss exactly when "
                        "that action leads to delay.")
    # c5's first-probe trailing form inside a rule is record-only too, and the message names the frozen form
    with pytest.raises(VEError, match=re.escape("'If …, … leads to …'")):
        parse_norm(ops, "Rule 1. Every action must not be performed, if that action leads to loss if that action "
                        "leads to delay.")
    # the carve-out reading stays: ", unless" is W1's carve-out
    document = parse_norm(ops, head + ", unless that action leads to delay.")
    assert document.rules[0].unless == (ast.Binary("leads_to", ast.Var(0), const("delay")),)


RULE_2_LISTED = ("Rule 1. Every action must not be performed, if there is an agent such that both of the following "
                 "hold: first clause: that action is available to that agent; end first clause; second clause: "
                 "another action available to that agent has a less severe worst case than that action; end second "
                 "clause, unless that action is classified as \"confirmed\".")


def test_rule_2_has_one_derivation_with_alts_binder(ops):
    """k19: rule 2 of 2.5 in alt's registered binder form has one derivation and 2.5's formulas."""
    rule = parse_norm(ops, RULE_2_LISTED).rules[0]
    strict = agent_ops_rules()[1]["norm"]
    assert formula_to_data(ops, ast.Forall("action", rule.guard)) == ["forall", "action", strict["guard"]]
    assert [formula_to_data(ops, ast.Forall("action", u)) for u in rule.unless] == [
        ["forall", "action", u] for u in strict["unless"]]
    # 2.5's compact spelling ("… such that that action is available to that agent and another action …")
    # is not a registered derivation of the surface; it is rejected, never read another way.
    with pytest.raises(VEError):
        parse_norm(ops, "Rule 1. Every action must not be performed, if there is an agent such that that action is "
                        "available to that agent and another action available to that agent has a less severe "
                        "worst case than that action.")


def test_p3_compact_coordination_is_rejected():
    """k19: P3's verb-phrase coordination is accepted only with one derivation; it is rejected here."""
    env = Environment(asimov_risk({"destruction": ("the robot's destruction", "severe"),
                                   "damage": ("the robot's damage", "minor")}, classes=("severe", "minor")))
    with pytest.raises(VEError):
        parse_norm(env, "Rule 1. Every action must not be performed, if there is a robot such that both of the "
                        "following hold: first clause: that action is available to that robot; end first clause; "
                        "second clause: another action available to that robot is lawful and has a less severe "
                        "worst case than that action; end second clause.")


def test_record_statement_forms_and_two_harms():
    """Review A4: with two or more harms, c6 and c7 still have exactly one reading."""
    env = Environment(ops_raw())
    actions = {"Running": "run", "Waiting": "wait"}
    harms = {"an outage": "outage", "loss": "loss", "a delay": "delay"}
    parse = lambda s: parse_wording(s, env, actions=actions, harms=harms, context="record")
    assert parse("Running cannot lead to loss unless the peak memory is greater than 8 GB.") == {
        "form": "necessary", "action": "run", "harm": "loss",
        "condition_text": "the peak memory is greater than 8 GB"}
    assert parse("Waiting leads to a delay exactly when the queue is at least 3.")["form"] == "exact"
    assert parse("Running might lead to an outage.")["form"] == "might"
    with pytest.raises(VEError, match="'might not lead to' is computed"):
        parse("Running might not lead to loss.")
    assert parse("If the peak memory is greater than 8 GB, Running leads to loss.") == {
        "form": "sufficient", "action": "run", "harm": "loss",
        "condition_text": "the peak memory is greater than 8 GB"}
    with pytest.raises(VEError, match="If <condition>, <action> leads to <harm>"):
        parse("Running leads to loss if the peak memory is greater than 8 GB.")


RECORD_LABELS = {"actions": {"Running": "run", "Waiting": "wait"},
                 "harms": {"an outage": "outage", "loss": "loss", "a delay": "delay"}}


@pytest.mark.parametrize("text,reading", [
    ("If the peak memory is greater than 8 GB, Running leads to loss.",
     {"form": "sufficient", "action": "run", "harm": "loss", "condition_text": "the peak memory is greater than 8 GB"}),
    ("If both the queue is at least 3 and the peak memory is at most 2 GB, Waiting leads to a delay.",
     {"form": "sufficient", "action": "wait", "harm": "delay",
      "condition_text": "both the queue is at least 3 and the peak memory is at most 2 GB"}),
    ("If it is not the case that the free memory is less than 4 GB, Running leads to an outage.",
     {"form": "sufficient", "action": "run", "harm": "outage",
      "condition_text": "it is not the case that the free memory is less than 4 GB"}),
    ("Running cannot lead to loss unless the peak memory is greater than 8 GB.",
     {"form": "necessary", "action": "run", "harm": "loss", "condition_text": "the peak memory is greater than 8 GB"}),
    ("Waiting leads to a delay exactly when the queue is at least 3.",
     {"form": "exact", "action": "wait", "harm": "delay", "condition_text": "the queue is at least 3"}),
    ("Running might lead to an outage.", {"form": "might", "action": "run", "harm": "outage"}),
    ("Running cannot lead to an outage.", {"form": "cannot", "action": "run", "harm": "outage"}),
    ("Running leads to an outage.", {"form": "leads", "action": "run", "harm": "outage"}),
])
def test_record_statements_parse_render_and_round_trip(text, reading):
    """c5 (frozen by risk-wording-probe-2) and the other record forms: one reading, one rendering, round trip."""
    env = Environment(ops_raw())
    parsed = parse_wording(text, env, context="record", **RECORD_LABELS)
    assert parsed == reading
    rendered = render_wording(parsed, **RECORD_LABELS)
    assert rendered == text
    assert parse_wording(rendered, env, context="record", **RECORD_LABELS) == parsed


@pytest.mark.parametrize("text,message", [
    # the first probe's trailing form (read as "only if") in every position it can take
    ("Running leads to loss if the peak memory is greater than 8 GB.", SUFFICIENT_REWRITE),
    ("Waiting leads to a delay if both the queue is at least 3 and the peak memory is at most 2 GB.",
     SUFFICIENT_REWRITE),
    ("If the queue is at least 3, Running leads to loss if the peak memory is greater than 8 GB.",
     SUFFICIENT_REWRITE),
    # "then" would make it the core surface's implication (risk-wording-probe-2 README)
    ("If the peak memory is greater than 8 GB, then Running leads to loss.", "Drop 'then'"),
    # no condition, or an unknown action or harm: no reading
    ("If , Running leads to loss.", "no unique registered reading"),
    ("If the peak memory is greater than 8 GB, Sleeping leads to loss.", "no unique registered reading"),
    ("If the peak memory is greater than 8 GB, Running leads to ruin.", "no unique registered reading"),
    # only "leads to" takes a fronted condition
    ("If the peak memory is greater than 8 GB, Running might lead to loss.", "no unique registered reading"),
])
def test_sufficient_condition_rejections(text, message):
    env = Environment(ops_raw())
    with pytest.raises(VEError, match=re.escape(message)):
        parse_wording(text, env, context="record", **RECORD_LABELS)


def test_sufficient_condition_is_a_record_statement_only():
    """2.3: a condition wording is record-only; in a guard the fronted form is rejected, the trailing one rewritten."""
    env = Environment(ops_raw())
    with pytest.raises(VEError, match="is a record statement"):
        parse_wording("If the peak memory is greater than 8 GB, Running leads to loss.", env, **RECORD_LABELS)
    with pytest.raises(VEError, match=re.escape(SUFFICIENT_REWRITE)):
        parse_wording("Running leads to loss if the peak memory is greater than 8 GB.", env, **RECORD_LABELS)


def test_render_wording_rejects_readings_it_cannot_name():
    labels = dict(RECORD_LABELS)
    for reading in ({"form": "sufficient", "action": "run", "harm": "loss"},
                    {"form": "sufficient", "action": "run", "harm": "loss", "condition_text": ""},
                    {"form": "leads", "action": "run", "harm": "loss", "condition_text": "q is 1"},
                    {"form": "sufficient", "action": "jump", "harm": "loss", "condition_text": "q is 1"},
                    {"form": "if", "action": "run", "harm": "loss", "condition_text": "q is 1"}):
        with pytest.raises(VEError, match="InvalidInput"):
            render_wording(reading, **labels)
    with pytest.raises(VEError, match="no unique label"):
        render_wording({"form": "sufficient", "action": "run", "harm": "loss", "condition_text": "q is 1"},
                       actions={"Running": "run", "running": "run"}, harms=labels["harms"])


def test_declared_wording_that_reuses_a_risk_form_keeps_its_identifier():
    """V4 also checks selected risk wording against another predicate's declared wording."""
    for wording in ("{0} risks {1}", "{0} might lead to {1}"):
        raw = ops_raw()
        raw["vocabulary"]["predicates"]["alias"] = {"arguments": ["action", "harm"], "description": "alias",
                                                    "verbalisation": wording}
        env = Environment(raw)
        words = EnglishVocabulary(env)
        assert words.predicates["alias"] == '{0} has the recorded relation "alias" to {1}'
        if wording == "{0} might lead to {1}":
            # A recorded narrowing (docs/lean-first/e2/DELTA.md, `availability`): V4 compares the risk form
            # with every declared wording, so Lean refuses Python's lexicon. It is an operational refusal of
            # the vocabulary, Lean's text verbatim, never an input error.
            with pytest.raises(CheckerUnavailable, match=r"^The vocabulary selection was not accepted "
                               r"\(invalidGrammar lexicon: V4 predicate risk__might_lead_to\)\. No text was read\.$"):
                parse_english_with_metadata(env, "run might lead to loss.")
        else:
            assert parse_english_with_metadata(env, "run might lead to loss.").document.formulas == (
                b("risk__might_lead_to", "run", "loss"),)
            with pytest.raises(VEError) as caught:
                parse_english_with_metadata(env, "run risks loss.")
            assert "Use 'might lead to' for possibility" in _diagnostic_text(caught.value)
    # "{0} risks {1}" is an accepted wording outside risk@0; inside, it collides with a rejected form
    raw = ops_raw()
    raw["vocabulary"]["predicates"]["alias"] = {"arguments": ["action", "harm"], "description": "alias",
                                                "verbalisation": "{0} risks {1}"}
    assert any(i.code == "DUPLICATE_TEMPLATE" and "/alias/" in i.path
               for i in EnglishVocabulary(Environment(raw)).issues)


def test_class_names_take_the_reserved_word_check():
    raw = ops_raw()
    raw["risk"]["severity"]["classes"] = ["severe", "serious", "every"]
    raw["risk"]["severity"]["more_severe"] = [["severe", "serious"], ["serious", "every"]]
    raw["risk"]["harm_classes"] = [[h, "every" if c == "minor" else c] for h, c in raw["risk"]["harm_classes"]]
    raw["risk"]["always_possible"] = ["severe"]
    env = Environment(raw)
    assert EnglishVocabulary(env).constants["every"] == '"every"'
    # A recorded narrowing (docs/lean-first/e2/DELTA.md, `availability`): the generated class constant `every`
    # is a reserved name in Lean's typing view, so the environment is refused at the boundary with the frozen
    # schema's text (batch 12's shared `VE.Bridge.checkVocabularyNames`).
    with pytest.raises(VEError, match="Schema identifier 'every' is reserved"):
        render_english(b("risk__class", "delay", "every"), env)


def test_units_fail_closed():
    """The English surface refuses a unit-carrying risk environment rather than reading it."""
    with pytest.raises(UnsupportedProfile, match="W6 annotated admission route"):
        parse_norm(Environment(agent_ops()), "Rule 1. Every action must not be performed, if that action "
                                             "might lead to \"data_loss\".")


def test_k29_bare_prevents_is_rejected_with_its_rewrite():
    env = Environment(asimov_risk({"p_death": ("P's death", "fatal"), "q_injury": ("Q's injury", "injuring")}))
    with pytest.raises(VEError, match="Use 'might prevent'"):
        parse_wording("Rescuing P prevents P's death.", env, actions={"Rescuing P": "rescue_p"},
                      harms={"P's death": "p_death"})


# ---------------------------------------------------------------------------- the paraphrases (Lean's legend)

def _lean(case):
    out = lean_routes.completed(BIN, [case])
    return json.loads(out.stdout)[0]


@pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="the Lean service is not built")
def test_paraphrases_are_the_legend_lines():
    """2.2, 2.4: each word the policy uses gets its paraphrase; excludes and avoids get theirs."""
    raw = asimov_risk({"death": ("the person's death", "fatal"), "bruising": ("the person's bruising", "injuring")},
                      fulfilment="excludes")
    words = ["exists", "harm", ["and", ["and", ["binary", "risk__or_worse", ["var", 0], ["const", "fatal"]],
                                        ["binary", "allows", ["var", 1], ["var", 0]]],
                                ["binary", "prevents", ["var", 1], ["var", 0]]]]
    less = ["exists", "action", ["binary", "risk__less_worst", ["var", 0], ["var", 1]]]
    norms = [{"norm": {"name": "r1", "predicate": "permitted", "sign": False, "guard": words, "unless": [], "over": []}},
             {"norm": {"name": "r2", "predicate": "permitted", "sign": False, "guard": less, "unless": [], "over": []}},
             {"norm": {"name": "r8", "predicate": "prevent_required", "sign": True,
                       "guard": ["binary", "avoidable", ["var", 0], ["var", 1]], "unless": [], "over": []}}]
    legend = _lean({"id": "l", "kind": "risk-elaborate", "environment": raw, "document": {"norms": norms}})["legend"]
    for line in (
        '"<action> might lead to <harm>" means the declared estimates, conditions and statements do not rule the harm out.',
        '"<action> cannot lead to <harm>" means they rule it out.',
        '"<action> leads to <harm>" means it happens in every case they allow.',
        '"<action> might not lead to <harm>" means some case they allow avoids the harm.',
        '"<harm> is <class> or worse" means the harm is <class> or more severe than <class>.',
        '<a> has a less severe worst case than <b> when <b> might lead to a harm more severe than every harm <a> might lead to.',
        '"<harm> is avoidable by <chooser>" means some action available to the chooser might not lead to the harm.',
        '"<action> allows <harm> to happen" means the action leads to the harm, and another action available to the same chooser might not lead to it.',
        '"<action> might prevent <harm>" means the action might not lead to the harm, and another action available to the same chooser leads to it.',
        "A robot prevent by taking an action that cannot lead to the harm.",
    ):
        assert line in legend, line


@pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="the Lean service is not built")
def test_sufficient_condition_renders_its_frozen_legend_line():
    """k2, k19: c5's legend line uses the frozen wording, with no "(wording pending)"; necessary and exact forms
    render their lines."""
    env = cell_env()
    policy = _lean({"id": "p", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}})
    log = Log()
    log.add(1, "E1", "estimate", estimate("peak_memory", "11", "12", "profiler", "statistical"))
    log.add(2, "E2", "estimate", estimate("free_memory", "8", "10", "monitor", "observation"))
    log.add(3, "C", "condition", condition("act", "server_outage", "sufficient", gt(q("peak_memory"), q("free_memory"))))
    log.add(4, "C4", "condition", condition("act", "job_failure", "exact", gt(q("peak_memory"), q("free_memory"))))
    quantities = [{"name": n, "label": n, "tag": "gb"} for n in ("peak_memory", "free_memory")]
    dx = log.add(5, "DX", "decision", record("x", "the_agent", "the agent", (policy["environment_id"],
                 policy["document_hash"]), [{"name": "act", "label": "acting"},
                 {"name": "nothing", "label": "doing nothing", "inaction": True}], quantities,
                 log.cite("E1", "E2", "C", "C4")))
    res = _lean({"id": "d", "kind": "risk-decision", "environment": env, "document": {"norms": []},
                 "decision": dx, "entries": log.entries[:-1]})
    assert res["status"] == "ok", res
    assert res["legend"] == [
        '"<action> leads to <harm> exactly when <condition>" means the harm happens in every case they allow in '
        'which the condition holds, and in no case they allow in which it does not hold.',
        '"If <condition>, <action> leads to <harm>" means the harm happens in every case they allow in which the '
        'condition holds.']
    assert not any("wording pending" in line for line in res["legend"])
