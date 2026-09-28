"""Python's declaration and authority boundary for alternatives@0."""
from copy import deepcopy
import json

import pytest

from conformance.alternatives import environment as fixture_environment, rules as fixture_rules

from ve.alternatives import run_case
from ve.document import check_document, coverage, load_document
from ve.ast import And, Binary, Const, Eq, Exists, Forall, Implies, Not, Unary, Var, formula_from_data, formula_to_data
from ve.environment import Environment
from ve.errors import CheckerUnavailable, VEError
from ve.evaluate import evaluate
from ve.norms import Norm, NormDocument, check_conflict
from ve.norm_english import parse_english as parse_norm_english, render_english as render_norm_english
from ve.english import EnglishParser, EnglishTraversal, EnglishVocabulary, parse_english_with_metadata
from ve.parser import parse as parse_strict
from ve.printer import print_document
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.surface.registry import by_tag, enabled


def source():
    sorts = {name: {"description": name} for name in ("robot", "action", "harm")}
    def base(args, words):
        return {"arguments": args, "description": words, "verbalisation": words}
    predicates = {
        "available": base(["action", "robot"], "{0} is available to {1}"),
        "leads_to": base(["action", "harm"], "{0} leads to {1}"),
        "inaction": base(["action"], "{0} is inaction"),
        "taken": base(["action"], "{0} is taken"),
        "causes": base(["action", "harm"], "{0} causes {1}"),
        "permitted": {"arguments": ["action"], "description": "permission",
                      "regulated": {"role": "permission", "default": "deny", "act": "{0} be done"}},
        "required": {"arguments": ["action"], "description": "obligation",
                     "regulated": {"role": "obligation", "default": "deny", "act": "{0} be done",
                                   "permission": "permitted"}},
        "prevent_required": {"arguments": ["robot", "harm"], "description": "prevent",
                             "regulated": {"role": "obligation", "default": "deny",
                                           "act": "{0} prevent {1}"}},
    }
    block = {"chooser": "robot", "action": "action", "harm": "harm",
             "available": "available", "leads_to": "leads_to", "outcomes": "signed",
             "decided_by": "case annotator", "performed": {"permission": "permitted", "obligation": "required"},
             "inaction": "inaction", "taken": "taken", "proximate": "causes",
             "fulfilments": [{"obligation": "prevent_required", "body": "avoids"}]}
    return {"language": LANGUAGE, "profiles": ["alternatives@0", "norms@0", "relational-fol@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": sorts, "predicates": predicates, "constants": {}},
            "alternatives": block}


def test_block_round_trip_and_identity():
    raw = source()
    env = Environment(raw)
    assert env.to_dict() == raw
    assert Environment(env.to_dict()).environment_id == env.environment_id
    changed = deepcopy(raw)
    changed["alternatives"]["outcomes"] = {"complete_by": "case annotator"}
    assert Environment(changed).environment_id != env.environment_id
    old = deepcopy(raw)
    del old["alternatives"]
    old["profiles"].remove("alternatives@0")
    assert "alternatives" not in Environment(old).to_dict()


@pytest.mark.parametrize("edit,diagnostic", [
    (lambda r: r["profiles"].remove("norms@0"), "alternatives@0 requires norms@0"),
    (lambda r: r["alternatives"].update(unknown=True), "InvalidInput: alternatives.unknown"),
    (lambda r: r["alternatives"].update(outcomes={}), "MissingOutcomeDecider"),
    (lambda r: r["alternatives"].update(outcomes={"complete_by": ""}), "MissingOutcomeDecider"),
    (lambda r: r["alternatives"].update(action="robot"), "sorts must be distinct"),
    (lambda r: r["alternatives"].update(available="missing"), "alternatives.available missing"),
    (lambda r: r["vocabulary"]["predicates"]["leads_to"].update(verbalisation="{0} risks {1}"),
     "AlternativesVerbalisation"),
    (lambda r: r["vocabulary"]["predicates"].update(allows={"arguments": ["action", "harm"],
                                                         "description": "collision"}), "AlternativesReserved"),
    (lambda r: r["vocabulary"]["predicates"].update(alias={"arguments": ["action", "harm"],
                                                       "description": "collision",
                                                       "verbalisation": "{0} prevents {1}"}),
     "AlternativesReserved: wording"),
    (lambda r: r["alternatives"].update(taken="inaction"), "AlternativesVerbalisation"),
    (lambda r: r["alternatives"].update(leads_to="available"),
     "AlternativesSort: leads_to expects \\(action, harm\\)"),
    (lambda r: r["alternatives"].update(performed={"permission": "required", "obligation": "permitted"}),
     "AlternativesPerformed"),
    (lambda r: r["alternatives"].update(fulfilments=[{"obligation": "prevent_required", "body": "avoids"}] * 2),
     "fulfilment prevent_required"),
])
def test_block_rejections(edit, diagnostic):
    raw = source()
    edit(raw)
    with pytest.raises(VEError, match=diagnostic):
        Environment(raw)


def test_route_fails_closed_without_lean(monkeypatch, tmp_path):
    raw = source()
    case = {"id": "one", "kind": "alt-elaborate", "environment": raw, "norms": []}
    monkeypatch.setenv("VE_AUTHORITY", "python")
    with pytest.raises(CheckerUnavailable, match="Lean checker"):
        run_case(case)
    monkeypatch.delenv("VE_AUTHORITY")
    with pytest.raises(CheckerUnavailable, match="unavailable"):
        run_case(case, binary=tmp_path / "absent")


def test_profile_records_are_scoped():
    env = Environment(source())
    for word in ("avoidable", "unavoidable", "allows", "prevents",
                 "every-available", "every-other-available", "another-available"):
        record = by_tag("alternatives-" + word)
        assert record is not None and enabled(record, env)


def test_fixed_role_wordings_have_one_paraphrase():
    raw = source()
    raw["vocabulary"]["constants"] = {"pull": {"sort": "action", "description": "pull"},
                                       "r": {"sort": "robot", "description": "r"},
                                       "h": {"sort": "harm", "description": "h"}}
    env = Environment(raw)
    for sentence in ("pull is available to r.", "pull leads to h.",
                     "it is not the case that pull leads to h.", "pull is inaction.",
                     "pull is taken.", "pull causes h."):
        rendered = parse_english_with_metadata(env, sentence).paraphrase()["english_text"]
        assert rendered.strip().lower() == sentence.lower()
    undeclared = deepcopy(raw)
    del undeclared["alternatives"]["proximate"]
    with pytest.raises(VEError, match="AlternativesVerbalisation"):
        Environment(undeclared)


def test_derived_words_round_trip_without_declared_predicate_tables():
    raw = source()
    raw["vocabulary"]["constants"] = {
        "pull": {"sort": "action", "description": "pull"},
        "h": {"sort": "harm", "description": "harm"},
        "r": {"sort": "robot", "description": "robot"},
    }
    env = Environment(raw)
    for word, sentence, first, second in (
        ("avoidable", "h is avoidable by r.", "h", "r"),
        ("unavoidable", "h is unavoidable by r.", "h", "r"),
        ("allows", "pull allows h to happen.", "pull", "h"),
        ("prevents", "pull prevents h.", "pull", "h"),
    ):
        formula = parse_english_with_metadata(env, sentence).document.formulas[0]
        assert formula_to_data(env, formula) == ["binary", word, ["const", first], ["const", second]]
        source_text = f"@{first} {word} @{second}.\n"
        assert formula_to_data(env, parse_strict(env, source_text).formulas[0]) == formula_to_data(env, formula)
        assert print_document(env, parse_strict(env, source_text)) == source_text
    assert set(env.to_dict()["vocabulary"]["predicates"]) == set(raw["vocabulary"]["predicates"])
    old = deepcopy(raw)
    del old["alternatives"]
    old["profiles"].remove("alternatives@0")
    with pytest.raises(VEError, match="Unknown predicate"):
        formula_from_data(Environment(old), ["binary", "allows", ["const", "pull"], ["const", "h"]])
    with pytest.raises(CheckerUnavailable, match="Lean checker"):
        evaluate(env, Binary("allows", Const("pull"), Const("h")), None)
    author_rule = {"norm": {"name": "no-allowing", "predicate": "permitted", "sign": False,
                            "guard": ["exists", "harm", ["binary", "allows", ["var", 1], ["var", 0]]],
                            "unless": [], "over": []}}
    document = NormDocument(env, [author_rule])
    with pytest.raises(CheckerUnavailable, match="Lean checker"):
        check_conflict(document)


def test_approved_alternatives_input_synonyms_normalize_to_canonical_text():
    raw = source()
    raw["vocabulary"]["constants"] = {
        name: {"sort": sort, "description": name}
        for name, sort in (("pull", "action"), ("r", "robot"), ("h", "harm"))}
    env = Environment(raw)
    for source_text, expected, canonical in (
        ("h is preventable by r.", ["binary", "avoidable", ["const", "h"], ["const", "r"]],
         "h is avoidable by r."),
        ("pull lets h happen.", ["binary", "allows", ["const", "pull"], ["const", "h"]],
         "pull allows h to happen."),
        ("pull does not lead to h.",
         ["not", ["binary", "leads_to", ["const", "pull"], ["const", "h"]]],
         "It is not the case that pull leads to h."),
    ):
        parsed = parse_english_with_metadata(env, source_text)
        assert formula_to_data(env, parsed.document.formulas[0]) == expected
        assert parsed.paraphrase()["english_text"] == canonical[0].upper() + canonical[1:] + "\n"


@pytest.mark.parametrize("wording,rewrite", [
    ("results in h", "leads to"),
    ("brings about h", "leads to"),
    ("could lead to h", "not Boolean"),
    ("risks h", "not Boolean"),
    ("increases the risk of h", "not Boolean"),
    ("contributes to h", "not Boolean"),
    ("provides uplift to h", "not Boolean"),
    ("through inaction allows h to happen", "two readings"),
    ("allows a harm to a human being to happen", "long form"),
])
def test_rejected_causal_wordings_offer_a_rewrite(wording, rewrite):
    raw = source()
    raw["vocabulary"]["constants"] = {
        "pull": {"sort": "action", "description": "pull"},
        "h": {"sort": "harm", "description": "h"}}
    with pytest.raises(VEError, match=rewrite):
        parse_english_with_metadata(Environment(raw), f"pull {wording}.")


def test_coverage_names_declared_alternatives_and_counterfactual_support():
    raw = source()
    raw["alternatives"]["outcomes"] = {"complete_by": "case annotator"}
    raw["vocabulary"]["constants"] = {
        name: {"sort": sort, "description": name}
        for name, sort in (("pull", "action"), ("wait", "action"), ("h", "harm"))}
    env = Environment(raw)
    units = [
        {"id": "choice", "span": [0, 1], "kind": "asserted", "status": "CHECKED",
         "meaning": "specified", "support": "testimony",
         "content": ["binary", "available", ["const", "pull"], ["const", "R"]]},
        {"id": "cell", "span": [1, 2], "kind": "asserted", "status": "CHECKED",
         "meaning": "specified", "support": "observation",
         "content": ["not", ["binary", "leads_to", ["const", "pull"], ["const", "h"]]]},
        {"id": "not-cause", "span": [2, 3], "kind": "asserted", "status": "CHECKED",
         "meaning": "specified", "support": "testimony",
         "content": ["not", ["binary", "causes", ["const", "pull"], ["const", "h"]]]},
    ]
    report = coverage({"environment": env, "units": units, "source": b"abc", "meta": {}})
    detail = report["alternatives"]
    assert detail["alternatives_declared"] == [
        {"action": "pull", "chooser": "R", "unit": "choice", "support": "testimony"}]
    assert detail["counterfactual_leaves"] == [
        {"action": "pull", "harm": "h", "leads_to": False, "decider": "case annotator",
         "unit": "cell", "support": "observation"}]
    assert detail["assumed_harm_free"] == [
        {"action": "wait", "harm": "h", "decider": "case annotator",
         "premise": "alternatives:table_complete"}]
    assert detail["table_complete"] == {"decider": "case annotator",
                                          "premise": "alternatives:table_complete"}
    assert detail["proximate_judgments"] == []
    assert report["residual"]["table_complete"] == 1
    assert report["residual"]["counterfactual_leaves"] == 1


def test_loaded_document_coverage_keeps_formula_leaves(tmp_path):
    raw = source()
    raw["alternatives"]["outcomes"] = {"complete_by": "case annotator"}
    raw["vocabulary"]["constants"] = {
        name: {"sort": sort, "description": name}
        for name, sort in (("pull", "action"), ("wait", "action"), ("r", "robot"), ("h", "harm"))}
    atoms = [
        ["binary", "available", ["const", "pull"], ["const", "r"]],
        ["not", ["binary", "leads_to", ["const", "pull"], ["const", "h"]]],
        ["binary", "causes", ["const", "pull"], ["const", "h"]],
    ]
    units = [{"id": f"u{i}", "span": [i, i + 1], "kind": "asserted",
              "meaning": "specified", "support": "testimony", "content": {"ast": atom}}
             for i, atom in enumerate(atoms)]
    meta = {"format": "ve-document@1", "environment": raw, "units": units}
    path = tmp_path / "case.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\nabc")
    detail = coverage(load_document(path))["alternatives"]
    assert [x["unit"] for x in detail["alternatives_declared"]] == ["u0"]
    assert [x["unit"] for x in detail["counterfactual_leaves"]] == ["u1"]
    assert [x["unit"] for x in detail["proximate_judgments"]] == ["u2"]
    assert detail["assumed_harm_free"] == [
        {"action": "wait", "harm": "h", "decider": "case annotator",
         "premise": "alternatives:table_complete"}]


def test_document_check_dispatches_w2_admission_to_lean(tmp_path):
    raw = source()
    env = Environment(raw)
    premise = next(p for p in run_case({"id": "source", "kind": "alt-elaborate",
                                        "environment": raw, "norms": []})["alternatives"]
                   if p["label"] == "alternatives:own")
    meta = {"format": "ve-document@1", "environment": raw,
            "units": [{"id": "claim", "span": [0, 1], "kind": "asserted",
                       "meaning": "specified", "support": "observation",
                       "content": {"ast": ["top"]}}],
            "graph": {"root": "slot", "nodes": [
                {"name": "slot", "label": premise["label"], "ast": premise["ast"]}]}}
    path = tmp_path / "document.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\nx")
    result = check_document(path)
    assert result["admission"]["admitted"] is True
    assert result["admission"]["report"]["root"]["label"] == "alternatives:own"
    assert result["premises"]["status"] == "UNKNOWN"
    assert result["admission"]["vacuous"] is None
    assert env.environment_id == Environment(raw).environment_id


def test_other_action_rendering_preserves_which_outer_action_is_excluded():
    raw = source()
    raw["vocabulary"]["constants"] = {
        "r": {"sort": "robot", "description": "r"},
        "h": {"sort": "harm", "description": "h"}}
    env = Environment(raw)
    words = EnglishVocabulary(env)
    scope = (("action", "the second action"), ("action", "the first action"))
    rendered = []
    for index in (1, 2):
        formula = Forall("action", Implies(
            And(Binary("available", Var(0), Const("r")), Not(Eq(Var(0), Var(index)))),
            Binary("prevents", Var(0), Const("h"))))
        traversal = EnglishTraversal(env, words)
        traversal.maximum = {"action": 3}
        sentence = traversal.formula(formula, scope)
        parser = EnglishParser(env, sentence, words)
        assert parser.formula(scope) == formula
        assert parser.i == len(sentence)
        rendered.append(sentence)
    assert rendered[0] != rendered[1]
    assert "excluding the first action" in rendered[1]


def test_nested_action_guard_round_trips_as_a_norm_block():
    raw = source()
    raw["vocabulary"]["constants"] = {
        "r": {"sort": "robot", "description": "r"},
        "h": {"sort": "harm", "description": "h"}}
    env = Environment(raw)
    texts = []
    for index in (1, 2):
        inner = Forall("action", Implies(
            And(Binary("available", Var(0), Const("r")), Not(Eq(Var(0), Var(index)))),
            Binary("prevents", Var(0), Const("h"))))
        guard = Exists("action", And(Unary("inaction", Var(0)), inner))
        document = NormDocument(env, [Norm("nested", "permitted", True, guard)])
        text, manifest = render_norm_english(document)
        assert parse_norm_english(env, text, manifest).document_hash == document.document_hash
        texts.append(text)
    assert texts[0] != texts[1]
    assert "excluding that action" in texts[1]


def test_rules_seven_to_nine_canonical_blocks_round_trip():
    env = Environment(fixture_environment())
    rules = fixture_rules()
    document = NormDocument(env, [rules[key] for key in ("3", "7", "8", "9")])
    text, manifest = render_norm_english(document)
    assert "allows that harm to happen" in text
    assert "avoidable by that robot" in text
    assert "for every second action" in text
    assert "the second action is available to that robot" in text
    assert parse_norm_english(env, text, manifest).document_hash == document.document_hash


def test_english_own_outcome_guard_names_the_semantic_change():
    env = Environment(source())
    with pytest.raises(VEError, match="DependencyCycle: permitted; GuardOnOwnOutcome: .*changes the rule's meaning"):
        parse_norm_english(env, "Rule 1. Every action may be done, "
                                "if that action may be done.")


def test_other_action_outcome_cycle_is_not_mislabeled_as_own_outcome():
    raw = source()
    raw["vocabulary"]["constants"] = {"r": {"sort": "robot", "description": "r"}}
    env = Environment(raw)
    with pytest.raises(VEError, match=r"^DependencyCycle: permitted$"):
        parse_norm_english(env, "Rule 1. Every action may be done, if every other "
                                "action available to r may be done.")


def test_available_guard_forms_bind_owner_and_distinguish_other_action():
    raw = source()
    raw["vocabulary"]["constants"] = {
        "r": {"sort": "robot", "description": "r"},
        "h": {"sort": "harm", "description": "h"},
    }
    env = Environment(raw)
    for phrase, quantifier in (
        ("every action available to r prevents h", "forall"),
        ("every other action available to r prevents h", "forall"),
        ("another action available to r prevents h", "exists"),
    ):
        document = parse_norm_english(env, f"Rule 1. Every action may be done, if {phrase}.")
        rendered, manifest = render_norm_english(document)
        assert parse_norm_english(env, rendered, manifest).document_hash == document.document_hash
        rule = document.rules[0]
        closed = formula_to_data(env, Forall("action", rule.guard))
        assert closed[2][0] == quantifier
        condition = closed[2][2][1]
        if "other" in phrase or phrase.startswith("another"):
            assert condition == ["and", ["binary", "available", ["var", 0], ["const", "r"]],
                                 ["not", ["eq", ["var", 0], ["var", 1]]]]
        else:
            assert condition == ["binary", "available", ["var", 0], ["const", "r"]]
    nested = ("there is a robot such that both of the following hold: "
              "first clause: that action is available to that robot; end first clause; "
              "second clause: every other action available to that robot prevents h; end second clause")
    document = parse_norm_english(env, f"Rule 1. Every action may be done, if {nested}.")
    rendered, manifest = render_norm_english(document)
    assert parse_norm_english(env, rendered, manifest).document_hash == document.document_hash
    guard = document.rules[0].guard
    assert formula_to_data(env, Forall("action", guard))[2][2][2][2][1][2] == [
        "not", ["eq", ["var", 0], ["var", 2]]]
    disjunctive = parse_norm_english(
        env, "Rule 1. Every action may be done, if every other action "
             "available to r either prevents h or allows h to happen.")
    rendered, manifest = render_norm_english(disjunctive)
    assert parse_norm_english(env, rendered, manifest).document_hash == disjunctive.document_hash
    explicit = parse_norm_english(
        env, "Rule 1. Every action may be done, if every other action "
             "available to r that other action prevents h.")
    assert explicit.rules[0].guard == parse_norm_english(
        env, "Rule 1. Every action may be done, if every other action "
             "available to r prevents h.").rules[0].guard
    with pytest.raises(VEError, match="Another action needs a rule on an action"):
        parse_english_with_metadata(env, "another action available to r prevents h.")
    with pytest.raises(VEError, match="there is a robot such that"):
        parse_norm_english(env, "Rule 1. Every action may be done, if every other "
                                "action available to that robot prevents h.")
