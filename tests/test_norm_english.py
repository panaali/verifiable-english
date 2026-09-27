import pytest

from ve.ast import Not, Top, Unary, Var
from ve.errors import VEError
from ve.norms import NormDocument
from ve.environment import Environment
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.norm_english import default_sentence, parse_english, render_english
from ve.norm_strict import parse_strict, print_strict
from tests.test_norms import environment, obligation, permission, rule


def test_four_wordings_and_identity_manifest():
    env = environment({"permitted": permission(), "required": obligation()})
    doc = NormDocument(env, [rule("ward-ban", "permitted", False),
                             rule("on-call-release", "permitted", True, over=("ward-ban",)),
                             rule("duty", "required", True),
                             rule("release-duty", "required", False)])
    text, manifest = render_english(doc)
    assert "Every act must not be done" in text
    assert "Every act may be done" in text
    assert "Every act must be done" in text
    assert "Every act need not be done" in text
    assert parse_english(env, text, manifest).rules == doc.rules
    assert parse_english(env, text).rules[0].name == "rule-1"
    assert default_sentence(env, "permitted") == "By default, an act must not be done."
    changed = text.replace("Every act may be done", "Every act must not be done")
    with pytest.raises(VEError, match="IdentityMetadataMismatch"):
        parse_english(env, changed, manifest)


def test_deontic_guard_and_carveout_round_trip():
    env = environment({"permitted": permission(), "required": obligation()})
    atom = Unary("permitted", Var(0))
    doc = NormDocument(env, [rule("may", "permitted", True),
                             rule("must", "required", True, atom, unless=(atom, Top()))])
    text, manifest = render_english(doc)
    assert "if that act may be done" in text
    assert text.count("Except when") == 2
    assert parse_english(env, text, manifest).rules == doc.rules
    negative = NormDocument(env, [rule("not-permitted", "required", False, Not(atom))])
    neg_text, neg_manifest = render_english(negative)
    assert "it is not the case that that act may be done" in neg_text
    assert parse_english(env, neg_text, neg_manifest).rules == negative.rules


def test_input_synonyms_and_rejected_wordings():
    env = environment({"permitted": permission()})
    no = parse_english(env, "Rule 1. No act may be done.")
    assert no.rules[0].sign is False
    with pytest.raises(VEError, match="single declared reading"):
        parse_english(env, "Rule 1. A act may be done.")
    with pytest.raises(VEError, match="single declared reading"):
        parse_english(env, "Rule 1. Every act should be done.")


def test_binary_each_binds_and_every_object_rejected():
    env = environment({"permitted": permission(act="{0} help {1}", args=("state", "person"))},
                      sorts=("state", "person"))
    text = "Rule 1. Every state may help each person."
    assert parse_english(env, text).rules[0].predicate == "permitted"
    assert parse_english(env, text.replace("each person", "any person")).rules[0].predicate == "permitted"
    with pytest.raises(VEError, match="each"):
        parse_english(env, text.replace("each person", "every person"))


def test_strict_named_rules_and_argument_order():
    env = environment({"permitted": permission(act="{0} help {1}", args=("state", "person"))},
                      sorts=("state", "person"))
    doc = NormDocument(env, [rule("ward-ban", "permitted", False, unless=(Top(),)),
                             rule("on-call-release", "permitted", True, over=("ward-ban",))])
    source = print_strict(doc)
    assert parse_strict(env, source).rules == doc.rules
    assert print_strict(parse_strict(env, source)) == source
    with pytest.raises(VEError, match="ConsequenceArguments"):
        parse_strict(env, source.replace("x0 permitted x1", "x1 permitted x0"))


def test_standalone_precedence_and_persistent_handles():
    env = environment({"permitted": permission()})
    text = ("Rule 1. Every act must not be done.\n"
            "Rule 2. Every act may be done.\n"
            "Rule 2 takes precedence over rule 1.")
    imported = parse_english(env, text)
    assert imported.rules[1].over == ("rule-1",)
    doc = NormDocument(env, [rule("ward-ban", "permitted", False),
                             rule("on-call-release", "permitted", True, over=("ward-ban",))])
    handles = {"ward-ban": "editor-a", "on-call-release": "editor-b"}
    rendered, manifest = render_english(doc, handles=handles)
    assert [b["handle"] for b in manifest["blocks"]] == ["editor-a", "editor-b"]
    assert parse_english(env, rendered, manifest).rules == doc.rules


def test_whole_block_earley_checks_multiple_parents_and_clause_boundary():
    env = environment({"permitted": permission()})
    text = ("Rule 1. Every act must not be done.\n"
            "Rule 2. Every act must not be done.\n"
            "Rule 3 (exception to rules 1 and 2). Every act may be done.")
    assert parse_english(env, text).rules[2].over == ("rule-1", "rule-2")
    with pytest.raises(VEError, match="all-derivations"):
        parse_english(env, text.replace("rules 1 and 2", "rules 1, and 2"))


def test_inline_except_when_is_canonicalized_to_unless():
    env = environment({"permitted": permission()})
    doc = parse_english(env, "Rule 1. Every act may be done, except when this holds in all cases.")
    assert "unless this holds in all cases" in render_english(doc)[0]


def test_plain_negative_is_inside_universal_and_uses_declared_negative():
    def plain(negative=None):
        predicate = {"arguments": ["item"], "description": "admitted",
                     "verbalisation": "{0} is admitted", "regulated": {"role": "plain", "default": "deny"}}
        if negative is not None:
            predicate["negative_verbalisation"] = negative
        return Environment({"language": LANGUAGE, "profiles": ["norms@0", "relational-fol@0"],
                            "spec_revision": SPEC_REVISION,
                            "vocabulary": {"sorts": {"item": {"description": "item"}},
                                           "predicates": {"admitted": predicate}, "constants": {}}})
    for negative in (None, "{0} is not admitted"):
        env = plain(negative)
        doc = NormDocument(env, [rule("ban", "admitted", False)])
        source, manifest = render_english(doc)
        assert "It is not the case that Every" not in source
        assert ("Every item is not admitted" if negative else
                "For every item, it is not the case that that item is admitted") in source
        assert parse_english(env, source, manifest).rules == doc.rules


def test_same_sort_binary_rule_round_trip_and_dangling_precedence():
    env = environment({"permitted": permission(act="{0} help {1}", args=("act", "act"))})
    doc = NormDocument(env, [rule("help", "permitted", True)])
    source, manifest = render_english(doc)
    assert "Every first act may help each second act" in source
    assert parse_english(env, source, manifest).rules == doc.rules
    assert parse_english(env, source.replace("each second act", "any second act")).rules[0].predicate == "permitted"
    with pytest.raises(VEError, match="UnknownRule"):
        parse_english(env, "Rule 9 takes precedence over rule 1.")
    with pytest.raises(VEError, match="UnknownRule"):
        parse_english(env, source + "\nRule 1 takes precedence over rule 9.")
