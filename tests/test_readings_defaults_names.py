"""The `<reading>` slot (docs/spec/readings-defaults.md 2.3, review A4) names readings by what they say, and two
readings that say different things never share a name (Astra's review B of RD-1; DRI ruling 2026-10-07): the
italic verb only when the full sentences, notes included, differ in nothing else; otherwise each full sentence; a
sentence that would show two different contents names neither, and only an answer that names one is refused.

Reserved completion names are hidden only under `norm-defaults@0` (Fable's review B1)."""
from __future__ import annotations

import copy
import dataclasses
import itertools
import json

import pytest

from tests.test_readings_s1_lean import env_k, norm_object
from tests.test_readings_s2_document import ASKS, DF, HELP_X, S, _query, _report, every, norm, s2_document
from ve.errors import VEError
from ve.readings_s2_english import (Slots, Unnamed, canonical_sentence, gated, hidden_in, named_result,
                                    sentence_slots, shown)

# ---------------------------------------------------------------------------------------------------------------
# The class: every field of a rule, mutated alone and together with the deontic verb


def _soft_env():
    from ve.softnorms import SoftEnvironment
    raw = env_k()
    raw["vocabulary"]["soft"] = {"parties": ["operator", "user"], "ranks": ["helpfulness", "safety"],
                                 "outranks": [], "ties": [], "outranking": {"mode": "strict"}}
    return SoftEnvironment(raw)


ENV = _soft_env()
ASKED = ASKS  # a condition on (agent, user) for the unless and exception fields; conditions name base predicates
PLAIN = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}  # an exception with no note
BASES = {"strict": norm_object("waive-x", "avoid_required", True, guard=ASKS),
         "default": norm_object("waive-x", "avoid_required", True, "default", guard=ASKS)}


def _exception(rule, **fields):
    return {**rule, "exception": {**rule["exception"], **fields}}


# One mutation per field of the rule schema (`Norm`, `SoftRule`, the exception object): (field, base, mutation).
# A mutation the base cannot carry (a strict rule has no exception; a default rule is never hard) is left out.
MUTATIONS = [
    ("name", "*", lambda r: {**r, "name": "waive-y"}),
    ("predicate", "*", lambda r: {**r, "predicate": "help_required"}),
    ("sign", "*", lambda r: {**r, "sign": not r["sign"]}),
    ("guard", "*", lambda r: {**r, "guard": ["top"]}),
    ("unless", "*", lambda r: {**r, "unless": [ASKED]}),
    ("over", "*", lambda r: {**r, "over": ["base-x"]}),
    ("mode", "strict", lambda r: {**r, "mode": "default", "exception": {"decided_by": "unstated", "sufficient": [],
                                                                        "necessary": [], "factors": []}}),
    ("mode", "default", lambda r: {k: v for k, v in r.items() if k not in ("mode", "exception")}),
    ("rank", "*", lambda r: {**r, "rank": "helpfulness"}),
    ("alterable", "*", lambda r: {**r, "alterable": ["operator"]}),
    ("hard", "strict", lambda r: {**r, "hard": True}),
    ("exception", "default", lambda r: _exception(r, decided_by="operator", sufficient=[ASKED])),
    ("decided_by", "default", lambda r: _exception(r, decided_by="operator")),
    ("sufficient", "default", lambda r: _exception(r, sufficient=[ASKED])),
    ("necessary", "default", lambda r: _exception(r, necessary=[ASKED])),
    ("factors", "default", lambda r: _exception(r, factors=["cost"])),
]
VERB = ("sign", "mode")     # the fields the deontic verb shows
UNSEEN = ("name", "hard")   # the fields a reader is not owed (`rule_key`)


def test_every_field_of_the_rule_schema_is_mutated():
    """The table is checked against the schema, so a field added to a rule is a field this test must mutate."""
    from ve.norms import Norm
    from ve.softnorms import SoftRule
    schema = ({f.name for f in dataclasses.fields(Norm)} | {f.name for f in dataclasses.fields(SoftRule)} - {"core"}
              | {"decided_by", "sufficient", "necessary", "factors"})
    assert schema <= {field for field, _, _ in MUTATIONS}


def _variants():
    """(base name, fields changed, rule): each base, each 1-fault mutation, and each mutation with the verb's
    fields changed too (2 faults: Astra's case is the verb and the precedence)."""
    out = []
    for base_name, base in BASES.items():
        out.append((base_name, (), base))
        for field, on, mutate in MUTATIONS:
            if on not in ("*", base_name):
                continue
            one = mutate(copy.deepcopy(base))
            out.append((base_name, (field,), one))
            if field not in VERB:
                out.append((base_name, (field, "sign"), {**one, "sign": not one["sign"]}))
    return out


def _named(rules):
    from ve.readings_route import rule_key, rule_sentence
    shown_ = [rule_sentence(ENV, rule) for rule in rules]
    return sentence_slots("rs1", [text for text, _ in shown_], [verb for _, verb in shown_],
                          [rule_key(ENV, rule) for rule in rules])


def _check_pair(a, b):
    from ve.readings_route import rule_key
    names = _named([a, b])
    ka, kb = rule_key(ENV, a), rule_key(ENV, b)
    if ka == kb:
        assert type(names[0]) is str and names[0] == names[1]
        return "same"
    assert all(type(name) is str for name in names) and names[0] != names[1], names
    if all(name.count(" ") <= 2 for name in names):  # the italic verb
        ka, kb = json.loads(ka), json.loads(kb)
        differs = {k for k in set(ka) | set(kb) if ka.get(k) != kb.get(k)}
        assert differs <= {"sign", "mode", "exception"}, (names, differs)
        # A strict rule and a default one differ in the exception too: only one with no note at all.
        assert "exception" not in differs or all(key.get("exception", PLAIN) == PLAIN for key in (ka, kb)), (
            names, ka, kb)
        return "verb"
    return "sentence"


def test_two_readings_get_one_name_exactly_when_they_mean_the_same():
    """For every pair of rule readings from 1- and 2-field mutations of a strict and a default rule: different
    meanings get different names that can be shown; the italic verb alone only when nothing but the verb differs;
    the same meaning (differing in a field the reader is not owed) the same name."""
    seen = {"same": 0, "verb": 0, "sentence": 0}
    for first, second in itertools.combinations(_variants(), 2):
        try:
            seen[_check_pair(first[2], second[2])] += 1
        except AssertionError as error:
            raise AssertionError(f"{first[:2]} / {second[:2]}: {error}") from None
    # Every outcome occurs, so the test can fail in each direction.
    assert all(seen.values()) and sum(seen.values()) > 1000, seen


def test_review_b_verb_and_precedence_differ():
    """Astra's case: `*must*` and `*need not*` named two readings that also differ in precedence, so the exception
    note was never shown. Now each is its full sentence."""
    must = norm_object("waive-x", "avoid_required", True, guard=ASKS)
    need_not = norm_object("waive-x", "avoid_required", False, over=("base-x",), guard=ASKS)
    names = _named([must, need_not])
    assert names[0].startswith("*Every agent must avoid deceiving each user")
    assert names[1].startswith("*Every agent need not avoid deceiving each user")
    assert names[1].endswith("It is an exception to rule base-x*")


def test_review_b_through_a_document(tmp_path):
    """Astra's reproduction as a document: the fixed rule base-x and a set whose readings differ in the verb and in
    the precedence over base-x. Both names are full sentences; the exception note is shown."""
    from ve.document import load_document
    from ve.readings_route import Wording
    path = s2_document(tmp_path, [
        ("fixed", "u0", norm("base-x", "avoid_required", True)),
        ("set", "rs1", "u1", [("a", norm("waive-x", "avoid_required", True, guard=ASKS), "norm", None),
                              ("b", norm("waive-x", "avoid_required", False, over=("base-x",), guard=ASKS), "norm",
                               None)])])
    names = Wording(load_document(path)).reading_names("rs1")
    assert names != ["*must*", "*need not*"]
    assert names[1].startswith("*Every agent need not avoid deceiving each user")
    assert names[1].endswith(". It is an exception to rule base-x*")
    lines, _ = _report(path)
    assert not any(" as *must*" in line or " as *need not*" in line for line in lines), lines


@pytest.mark.parametrize("note, rule", [
    ("It is an exception to rule base-x", {"over": ["base-x"]}),
    ("operator may turn it off for this situation", {"alterable": ["operator"]}),
    ("It records rank helpfulness", {"rank": "helpfulness"}),
])
def test_readings_that_differ_only_in_a_note(note, rule):
    """The DRI's test: readings with one verb that differ only in a precedence, switch or rank note are named by
    their full sentences, the note shown."""
    base = norm_object("waive-x", "avoid_required", True, guard=ASKS)
    names = _named([base, {**base, **rule}])
    assert note not in names[0] and note in names[1] and names[0] != names[1]


@pytest.mark.parametrize("note, fields", [
    ("Its exception applies when", {"sufficient": [ASKED]}),
    ("Its exception applies only when", {"necessary": [ASKED]}),
    ("Its exception takes account of", {"factors": ["cost"]}),
    ("Its exception is decided by operator", {"decided_by": "operator"}),
])
def test_default_readings_that_differ_only_in_their_exception(note, fields):
    base = BASES["default"]
    names = _named([base, _exception(base, **fields)])
    assert note not in names[0] and note in names[1]
    # With the verb changed too, the name is still the full sentence, never the verb alone.
    other = _exception({**base, "sign": False}, **fields)
    names = _named([base, other])
    assert names[1].startswith("*Every agent generally need not") and note in names[1]


def test_the_verb_alone_when_only_the_verb_differs():
    """S2a's M4 keeps the italic verb (spec 8.2): the strict rule and its default twin differ only in it."""
    strict, default = BASES["strict"], BASES["default"]
    assert _named([strict, default]) == ["*must*", "*should*"]
    assert _named([strict, {**strict, "sign": False}]) == ["*must*", "*need not*"]


# ---------------------------------------------------------------------------------------------------------------
# The slot function and its refusals, at use only


def test_sentence_slots():
    """A candidate's own sentence in italics without its final period; a candidate the slot cannot show is
    `Unnamed`; one sentence for two different contents names neither; one content keeps its one sentence."""
    no_content = Unnamed("an answer names a reading of rs_1 without content")
    assert sentence_slots("rs_1", ["Every agent must help each user.", no_content,
                                   "A must B. It is an exception to rule x."]) == [
        "*Every agent must help each user*", no_content, "*A must B. It is an exception to rule x*"]
    for twice in (["Every agent must help each user.", "Every agent must help each user."],
                  ["Every agent must help each user.", "Every agent must help each user"]):
        names = sentence_slots("rs_1", twice)
        assert all(type(name) is Unnamed for name in names)
        with pytest.raises(VEError, match="two different readings of rs_1 are shown by the same sentence"):
            shown(names[0])
    assert sentence_slots("rs_1", ["A must B.", "A must B."], keys=["k", "k"]) == ["*A must B*", "*A must B*"]
    with pytest.raises(VEError, match="without content"):
        shown(no_content)


def test_the_verb_alone_needs_one_frame_over_the_full_sentences():
    assert sentence_slots("s", ["A must B.", "A should B."], ["must", "should"]) == ["*must*", "*should*"]
    assert sentence_slots("s", ["A must B.", "A should B. It is an exception to rule x."], ["must", "should"]) == [
        "*A must B*", "*A should B. It is an exception to rule x*"]
    assert sentence_slots("s", ["A must B.", "A must B. Note."], ["must", "must"]) == ["*A must B*", "*A must B. Note*"]


def test_a_sentence_without_a_writable_form_is_a_refusal_not_a_crash(monkeypatch):
    """The renderer's ValueError ('No writable English form') is the slot's refusal, never an escaping error."""
    from ve import printer
    from ve.ast import Top
    from ve.environment import Environment

    def unwritable(*args, **kwargs):
        raise ValueError("No writable English form")

    monkeypatch.setattr(printer, "render", unwritable)
    frame = Environment(env_k())
    with pytest.raises(VEError, match="InvalidInput: does not read back"):
        canonical_sentence(frame, Top(), "does not read back")


def test_readings_that_differ_only_in_the_rule_name_share_their_sentence():
    """Two rules that differ only in their own names mean the same to a reader, so they share one name rather than
    refusing (such a pair has no distinguishing model, so Lean's admission refuses it in a document anyway)."""
    rule = lambda name: norm_object(name, "avoid_required", True, guard=ASKS)  # noqa: E731
    names = _named([rule("waive-x"), rule("waive-y")])
    assert names[0] == names[1] and names[0].startswith("*Every agent must avoid deceiving each user")


def test_an_unshowable_reading_is_refused_only_where_an_answer_names_it(tmp_path, monkeypatch):
    """A reading the slot cannot show (here: its sentence does not read back) leaves the wording of the document
    buildable and every other reading nameable; only naming it is refused, with the reason."""
    from tests.test_readings_s2_document import _wording
    from ve.readings_route import Wording
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X)])
    original = Wording.candidate_sentence

    def unshowable(self, set_id, i):
        return (Unnamed("a reading of rs1 does not read back to its content"), None) if i == 1 else \
            original(self, set_id, i)

    monkeypatch.setattr(Wording, "candidate_sentence", unshowable)
    _, _, wording = _wording(path)
    assert wording.name("rs1", 0) == "*Every agent must avoid deceiving each user*"
    assert wording.names["rs1"][1] == Unnamed("a reading of rs1 does not read back to its content")
    with pytest.raises(VEError, match="does not read back"):
        wording.name("rs1", 1)


# ---------------------------------------------------------------------------------------------------------------
# Fable B1: the completion's reserved names are hidden only under `norm-defaults@0`


@pytest.mark.parametrize("name", ["unsaid__x", "unsaid--x"])
def test_reserved_prefixes_are_ordinary_names_without_the_completion(name):
    from ve.environment import RESERVED_PREFIXES, reserved_prefixes
    text = f"Read sentence 1 as *must*: the text does not say whether a {name} u: no rule decides this situation."
    plain = Slots(numbers={"1"}, readings={"*must*"}, clauses={f"a {name} u"},
                  reserved=reserved_prefixes(("readings@1", "norms@0")))
    assert named_result([(1, "*must*")], "undecided", plain, clause=f"a {name} u") == text
    completed = Slots(numbers={"1"}, readings={"*must*"}, clauses={f"a {name} u"},
                      reserved=reserved_prefixes(("readings@1", "norms@0", "norm-defaults@0")))
    with pytest.raises(VEError, match="generated name"):
        gated("E12", text, completed)
    with pytest.raises(VEError, match="generated name"):  # no environment: every reserved prefix is hidden
        gated("E12", text, Slots(numbers={"1"}, readings={"*must*"}, clauses={f"a {name} u"}))
    assert reserved_prefixes(["norm-defaults@0"]) == RESERVED_PREFIXES == ("unsaid__", "unsaid--")


def test_fable_b1_a_plain_readings_document_shows_its_own_unsaid_predicate(tmp_path):
    """Fable's case: a `readings@1` document (no `norm-defaults@0`) with an author predicate `unsaid__x` and no
    wording for it shows `recorded relation "unsaid__x"` in a query's conclusion; it was refused."""
    raw = env_k()
    raw["vocabulary"]["predicates"]["unsaid__x"] = {"arguments": ["agent", "user"], "description": "base"}
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X),
                                  ("fixed", "u2", every("unsaid__x"))], raw=raw)
    data, lines, wording = _query(path, every("unsaid__x"))
    assert data["verdict"] == "ALL" and wording.slots.reserved == ("soft__",)
    assert any('the conclusion follows: *For every agent, for every user, that agent has the recorded relation '
               '"unsaid__x" to that user.*' in line for line in lines), lines


# ---------------------------------------------------------------------------------------------------------------
# Recheck B: a generated or reserved name is a name that begins with its prefix, wherever author text is shown


def _hidden_prefixes():
    from ve.environment import RESERVED_PREFIXES, WORDING_LAYER_PREFIXES
    from ve.readings_s2_english import _HIDDEN
    return (*_HIDDEN, *RESERVED_PREFIXES, *(p for prefixes in WORDING_LAYER_PREFIXES.values() for p in prefixes))


def _in_slot(slot, text):
    """E12 with `text` in one slot kind: the `<reading>` name, R7's `<clause>`, R4's `<situation>` or R2's
    `<conclusion>`, gated with every reserved prefix hidden."""
    reading = text if slot == "reading" else "*must*"
    slots = Slots(numbers={"1"}, readings={reading}, clauses={text}, situations={text}, conclusions={text})
    kind, field = {"reading": ("conflict_free", None), "clause": ("undecided", "clause"),
                   "situation": ("conflict", "situation"), "conclusion": ("follows", "conclusion")}[slot]
    return named_result([(1, reading)], kind, slots, **({field: text} if field else {}))


SLOT_KINDS = ("reading", "clause", "situation", "conclusion")
# Inside a name: after a letter, a digit, `_`, `-` or a non-ASCII letter. At a name's start: after anything else.
INSIDE = ("standa", "x-", "x_", "x9", "é")
AT_START = ("", " ", "*", '"', "(", "'", ", ", "rule ")


@pytest.mark.parametrize("slot", SLOT_KINDS)
def test_a_prefix_inside_an_author_name_is_shown(slot):
    """The reviewer's `standard-x` (the `rd-` inside it) as a class: every hidden prefix inside a name, in every
    slot that shows author text, is shown; the same prefix where a name begins is refused."""
    for prefix in _hidden_prefixes():
        for before in INSIDE:
            text = f"a {before}{prefix}y u"
            assert text in _in_slot(slot, text), (slot, prefix, before)
        for before in AT_START:
            with pytest.raises(VEError, match="generated name"):
                _in_slot(slot, f"a {before}{prefix}y u".replace("a  ", "a "))


def test_may_not_is_refused_anywhere():
    """G9 has no exception (composition.md 13.20): `may not` is refused inside a word too."""
    for text in ("a user may not", "dismay nothing", "x may notify u"):
        assert hidden_in(text) == "may not"
        for slot in SLOT_KINDS:
            with pytest.raises(VEError, match="may not"):
                _in_slot(slot, text)


def test_hidden_in_reads_the_reserved_prefixes_given():
    assert hidden_in("rule unsaid--x", ()) is None
    assert hidden_in("rule unsaid--x", ("unsaid__", "unsaid--")) == "unsaid--"
    assert hidden_in("rule unsaid--x") == "unsaid--"  # no environment: every reserved prefix is hidden
    assert hidden_in("rule my_unsaid--x") is None and hidden_in("standard-x and rd-1-x") == "rd-"


@pytest.mark.parametrize("fixed", ["standard-x", "record-keeping", "hazard-rd-x", "ward-rd-2"])
def test_recheck_b_rule_names_containing_rd_are_named(tmp_path, fixed):
    """The recheck's reproduction: Astra's review-B document with the fixed rule renamed. The precedence note
    names it, and the query answers SOME with the full sentences, as it does for `base-x`."""
    path = s2_document(tmp_path, [
        ("fixed", "u0", norm(fixed, "avoid_required", True)),
        ("set", "rs1", "u1", [("a", norm("waive-x", "avoid_required", True, guard=ASKS), "norm", None),
                              ("b", norm("waive-x", "avoid_required", False, over=(fixed,), guard=ASKS), "norm",
                               None)])])
    data, lines, wording = _query(path, every("avoid_required", negated=True, guard=ASKS))
    assert data["verdict"] == "SOME"
    assert any(f"It is an exception to rule {fixed}*" in line for line in lines), lines
    assert all(hidden_in(line, wording.slots.reserved) is None for line in lines)


@pytest.mark.parametrize("predicate", ["save__x", "microsoft__x", "copyrights__x"])
def test_author_predicates_containing_a_generated_prefix_are_shown(tmp_path, predicate):
    """The same class in the `<conclusion>` slot: an author predicate that contains `ve__`, `soft__` or `rights__`
    (but does not begin with it) is shown in the conclusion, as Fable's `unsaid__x` is."""
    raw = env_k()
    raw["vocabulary"]["predicates"][predicate] = {"arguments": ["agent", "user"], "description": "base"}
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X),
                                  ("fixed", "u2", every(predicate))], raw=raw)
    data, lines, _ = _query(path, every(predicate))
    assert data["verdict"] == "ALL"
    assert any(f'"{predicate}" to that user.*' in line for line in lines), lines


def test_rights_prefix_is_an_author_predicate_without_rights_layer(tmp_path):
    """Looprecheck2 B: the admitted `rights__x` conclusion is worded, not turned into InvalidInput."""
    raw = env_k()  # soft-norms@0 is active; rights@0 is absent
    raw["vocabulary"]["predicates"]["rights__x"] = {"arguments": ["agent", "user"], "description": "base"}
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X),
                                  ("fixed", "u2", every("rights__x"))], raw=raw)
    data, lines, wording = _query(path, every("rights__x"))
    assert data["verdict"] == "ALL"
    assert any('"rights__x" to that user.*' in line for line in lines), lines
    assert "rights__" not in wording.slots.reserved
    assert all(hidden_in(line, wording.slots.reserved) is None for line in lines)


def test_soft_prefix_is_an_author_predicate_without_soft_layer(tmp_path):
    """The norms-only route accepts and words an author's soft__ predicate across a reading set."""
    raw = env_k(profiles=("norms@0", "readings@1", "relational-fol@0"))
    raw["vocabulary"]["predicates"]["soft__x"] = {"arguments": ["agent", "user"], "description": "base"}
    path = s2_document(tmp_path, [
        ("set", "rs1", "u1", [("a", norm("no-deception", "avoid_required", True), "norm", None),
                              ("b", norm("no-deception", "avoid_required", False), "norm", None)]),
        ("fixed", "u2", every("soft__x"))], raw=raw)
    data, lines, wording = _query(path, every("soft__x"))
    assert data["verdict"] == "ALL" and wording.slots.reserved == ()
    assert any('"soft__x" to that user.*' in line for line in lines), lines
    assert all(hidden_in(line, wording.slots.reserved) is None for line in lines)


def test_s2_hidden_prefixes_follow_every_optional_layer_combination():
    """Each optional producer's prefix is hidden exactly when its profile is active, in every wording slot."""
    import itertools
    from ve.environment import WORDING_LAYER_PREFIXES, wording_reserved_prefixes

    optional = ("norm-defaults@0", *WORDING_LAYER_PREFIXES)
    for flags in itertools.product((False, True), repeat=len(optional)):
        profiles = {profile for profile, on in zip(optional, flags) if on}
        reserved = wording_reserved_prefixes(profiles)
        for profile, prefix in (("norm-defaults@0", "unsaid__"),
                                ("norm-defaults@0", "unsaid--"),
                                *((profile, p) for profile, prefixes in WORDING_LAYER_PREFIXES.items()
                                  for p in prefixes)):
            for slot in SLOT_KINDS:
                text = f"a {prefix}x u"
                reading = text if slot == "reading" else "*must*"
                slots = Slots(numbers={"1"}, readings={reading}, clauses={text}, situations={text},
                              conclusions={text}, reserved=reserved)
                kind, field = {"reading": ("conflict_free", None), "clause": ("undecided", "clause"),
                               "situation": ("conflict", "situation"),
                               "conclusion": ("follows", "conclusion")}[slot]
                build = lambda: named_result([(1, reading)], kind, slots,
                                             **({field: text} if field else {}))
                if profile in profiles:
                    with pytest.raises(VEError, match="generated name"):
                        build()
                else:
                    assert text in build()
        assert hidden_in("rule ve__here", reserved) == "ve__"
        assert hidden_in("rule rd-1-x", reserved) == "rd-"


def test_the_lint_and_the_checker_share_one_reserved_table():
    import importlib.util
    from pathlib import Path
    from ve.environment import RESERVED_PREFIXES
    from ve.norm_defaults import fill_name, unsaid_name
    spec = importlib.util.spec_from_file_location("relay_lint", Path(__file__).resolve().parents[1] /
                                                  "tools/relay_lint.py")
    lint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lint)
    assert lint.RESERVED is RESERVED_PREFIXES
    assert unsaid_name("p").startswith(RESERVED_PREFIXES[0]) and fill_name("p").startswith(RESERVED_PREFIXES[1])
    assert json.dumps(RESERVED_PREFIXES)
