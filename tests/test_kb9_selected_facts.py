"""kb-9: the `soft-selected` case with `facts` (docs/spec/kernel-boundary.md 8.1, "one row per answer").

A case may send `facts`, closed formulas over the soft route's base vocabulary, decoded by the slot kinds' own
decoder (`VE.Compose.SlotWire.decodeFacts`). The answer then also has `facts` (every fact is true in the model)
and `coherent` (no colliding pair of default rules is selected at one tuple), read in the same model as the
selected rules (`soft_wire_selected_facts`); a false flag is reported, not refused. A case without `facts` is
answered as before. The relay (`bind_selected`) requires both flags exactly when facts were sent, each a bool;
`SoftenedNormDocument` keeps answers per document, model and the facts' encoded bytes and exposes the flags
(`selection_flags`).
"""
from __future__ import annotations

import copy

import pytest

from tests.test_soft_norms_lean import env, should
from tests.test_soft_selected import (BAD, BAD_IDS, EXTRA, GENUINE, MODEL, QUERIES, RULES, SENT, case, document,
                                      lean, rows)  # noqa: F401  (lean: the fixture)
from ve import ast as A
from ve import soft_route
from ve.errors import CheckerUnavailable, VEError
from ve.softnorms import SoftEnvironment, SoftNormDocument, facts_wire

# In MODEL: v holds at b only, w at a and c only.
SOME_V = ["exists", "assistant", ["unary", "v", ["var", 0]]]          # true
EVERY_W = ["forall", "assistant", ["unary", "w", ["var", 0]]]         # false (w fails at b)
NOT_V_AND_W = ["forall", "assistant", ["not", ["and", ["unary", "v", ["var", 0]], ["unary", "w", ["var", 0]]]]]  # true


def facts_case(facts, **kw):
    return {**case(**kw), "facts": facts}


# ---------------------------------------------------------------------------------------------------
# Lean's answer.

def test_a_false_fact_is_reported_and_the_selected_rules_are_still_answered(lean):
    without = soft_route.selected_at(document(), MODEL, QUERIES)
    answer = soft_route.selected_at(document(), MODEL, QUERIES, facts=[SOME_V, EVERY_W])
    assert answer == {"background": True, "facts": False, "coherent": True, "results": without["results"]}


def test_true_facts_and_an_empty_list_report_true(lean):
    for facts in ([SOME_V, NOT_V_AND_W], []):
        answer = soft_route.selected_at(document(), MODEL, QUERIES[:1], facts=facts)
        assert (answer["facts"], answer["coherent"], answer["background"]) == (True, True, True)


def test_the_last_fact_is_sent_and_read(lean):
    """A planted false fact at the end of the list makes the flag false (a relay that dropped it would not)."""
    assert soft_route.selected_at(document(), MODEL, QUERIES[:1], facts=[SOME_V, NOT_V_AND_W])["facts"] is True
    assert soft_route.selected_at(document(), MODEL, QUERIES[:1],
                                  facts=[SOME_V, NOT_V_AND_W, EVERY_W])["facts"] is False


def test_a_case_without_facts_is_answered_as_before(lean):
    [row] = rows([case()])
    assert set(row) == {"id", "status", "background", "results"}
    [with_facts] = rows([facts_case([SOME_V])])
    assert {k: v for k, v in with_facts.items() if k not in ("facts", "coherent")} == row


def test_python_formula_asts_are_written_by_the_case_encoder(lean):
    ast = A.Exists("assistant", A.Unary("v", A.Var(0)))
    assert facts_wire([ast, SOME_V]) == [SOME_V, SOME_V]
    assert soft_route.selected_at(document(), MODEL, QUERIES[:1], facts=[ast])["facts"] is True


def test_a_colliding_pair_selected_at_one_tuple_reports_coherent_false(lean):
    """Two unranked default rules of opposite sign whose guards both hold at `a`: both are selected and reported,
    and `coherent` is false (kb-10/SPEC.md 4.1); `background` alone does not see it."""
    exception = {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}
    rules = [should("p", "x_required", True, guard=("unary", "v", ["var", 0]), exception=exception),
             should("q", "x_required", False, guard=("unary", "w", ["var", 0]), exception=exception)]
    doc = SoftNormDocument(SoftEnvironment(env(req="deny", extra=EXTRA)), rules)
    model = {"complete": True, "domains": {"assistant": ["a", "b"], "user": []}, "constants": {},
             "relations": {"v": [["a"], ["b"]], "w": [["a"]], "s": [], "soft__excepted__p": [], "soft__excepted__q": []}}
    answer = soft_route.selected_at(doc, model, [("x_required", ["a"]), ("x_required", ["b"])], facts=[])
    assert (answer["background"], answer["coherent"], answer["facts"]) == (True, False, True)
    assert [r["selected"] for r in answer["results"]] == [["p", "q"], ["p"]]


@pytest.mark.parametrize("facts, message", [
    ([["unary", "v", ["var", 0]]], "ill-typed or unbound formula"),
    ([["exists", "assistant", ["unary", "x_required", ["var", 0]]]], "ill-typed or unbound formula"),
    ([["exists", "assistant", ["unary", "soft__excepted__d", ["var", 0]]]],
     "InvalidInput: facts: soft__excepted__d is a soft decision predicate; its decider decides it, not a fact"),
    ({"a": 1}, "InvalidInput: facts must be an array"),
])
def test_an_undecodable_fact_refuses_the_case_with_the_decoders_diagnostic(lean, facts, message):
    [row] = rows([facts_case(facts)])
    assert row["status"] == "error" and row["error"] == message
    if type(facts) is list:
        with pytest.raises(VEError, match=message):
            soft_route.selected_at(document(), MODEL, QUERIES[:1], facts=facts)


# ---------------------------------------------------------------------------------------------------
# Binding: the flags are present exactly when facts were sent, and are bools.

def _doc():
    return type("Doc", (), {"rules": [type("R", (), {"to_dict": lambda self, n=n: n})() for n in RULES],
                            "env": SoftEnvironment(env(extra=EXTRA))})()


GENUINE_FACTS = {**GENUINE, "facts": False, "coherent": True}


def _answer(monkeypatch, row, facts):
    sent = []
    monkeypatch.setattr(soft_route, "_run", lambda request: sent.append(request) or row)  # the relay never writes it
    return soft_route.selected_at(_doc(), MODEL, SENT, facts=facts), sent


def test_the_genuine_answer_with_facts_is_bound_and_every_fact_is_sent(monkeypatch):
    answer, sent = _answer(monkeypatch, GENUINE_FACTS, [SOME_V, EVERY_W])
    assert answer == {"background": True, "facts": False, "coherent": True, "results": GENUINE["results"]}
    assert sent[0]["facts"] == [SOME_V, EVERY_W]


# A retyped flag: every malformed value but a bool, which is a well-typed flag whose value is Lean's.
RETYPES = [(value, name) for value, name in zip(BAD + [1, 0, "true"], BAD_IDS + ["one", "zero", "string"])
           if type(value) is not bool]
FORGED = {
    "facts dropped": (lambda row: row.pop("facts"), [SOME_V]),
    "coherent dropped": (lambda row: row.pop("coherent"), [SOME_V]),
    "both dropped": (lambda row: (row.pop("facts"), row.pop("coherent")), [SOME_V]),
    "facts dropped beside empty facts": (lambda row: row.pop("facts"), []),
    "facts added, none sent": (lambda row: row.pop("coherent"), None),
    "coherent added, none sent": (lambda row: row.pop("facts"), None),
    "both added, none sent": (lambda row: None, None),
    **{f"facts retyped {name}": ((lambda value: lambda row: row.__setitem__("facts", value))(value), [SOME_V])
       for value, name in RETYPES},
    **{f"coherent retyped {name}": ((lambda value: lambda row: row.__setitem__("coherent", value))(value), [SOME_V])
       for value, name in RETYPES},
}


@pytest.mark.parametrize("name", sorted(FORGED))
def test_a_forged_flag_is_unavailable(monkeypatch, name):
    edit, facts = FORGED[name]
    row = {**copy.deepcopy(GENUINE), "facts": False, "coherent": True}
    edit(row)
    with pytest.raises(CheckerUnavailable, match="not bound to the request"):
        _answer(monkeypatch, row, facts)


# ---------------------------------------------------------------------------------------------------
# SoftenedNormDocument: kept answers per document, model and facts; the flags from the same answer.

def test_selected_rules_and_flags_come_from_one_case_per_document_model_and_facts(lean, monkeypatch):
    import ve.softnorms as softnorms
    elaborated = document().elaborated
    calls = []
    relay = softnorms._relay_run
    monkeypatch.setattr(softnorms, "_relay_run", lambda request: calls.append(request) or relay(request))
    facts = [SOME_V, EVERY_W]
    assert [r.name for r in elaborated.selected_rules("x_required", MODEL, ("c",), facts=facts)] == ["d"]
    assert elaborated.outcome_at("x_required", MODEL, ("c",), facts=facts) is True
    assert elaborated.selection_flags(MODEL, facts=facts) == {"background": True, "facts": False, "coherent": True}
    assert len(calls) == 1 and calls[0]["facts"] == facts
    # Other facts, or none, are another kept answer: one more case each.
    assert elaborated.selection_flags(MODEL, facts=[SOME_V])["facts"] is True
    assert elaborated.selection_flags(MODEL) == {"background": True}
    assert [r.name for r in elaborated.selected_rules("x_required", MODEL, ("c",))] == ["d"]
    assert len(calls) == 3 and "facts" not in calls[2]
    assert elaborated.selection_flags(MODEL, facts=[]) == {"background": True, "facts": True, "coherent": True}
    assert len(calls) == 4


def test_flags_need_the_soft_source():
    from ve.softnorms import SoftenedNormDocument
    hand = SoftenedNormDocument.__new__(SoftenedNormDocument)
    with pytest.raises(CheckerUnavailable, match="soft source"):
        hand.selection_flags(MODEL, facts=[])


# ---------------------------------------------------------------------------------------------------
# The harnesses' premise check (anthropic-rsp, openai-preparedness): Lean's flag, the text as before.

def _harness(name):
    import importlib.util
    import sys
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "usecases" / name / "run.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(f"kb9_{name.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Block:
    def __init__(self, id_):
        self.id = id_


@pytest.mark.parametrize("name", ["anthropic-rsp", "openai-preparedness"])
def test_a_harness_premise_check_reads_the_flag_of_the_selection_case(lean, monkeypatch, name):
    import importlib
    import ve.softnorms as softnorms
    evaluation = importlib.import_module("ve.evaluate")  # the module (`ve.evaluate` the attribute is the function)
    harness = _harness(name)
    # Kept answers are per process: facts no other test keys on, one list per harness.
    first = (SOME_V, NOT_V_AND_W) if name == "anthropic-rsp" else (NOT_V_AND_W, SOME_V)
    blocks = [(_Block("b1"), first), (_Block("b2"), (NOT_V_AND_W, EVERY_W))]
    monkeypatch.setattr(harness, "selected_facts", lambda choice: blocks if choice.get("RS3o") == "bad" else blocks[:1])
    monkeypatch.setattr(harness, "model", lambda doc, case: MODEL)
    monkeypatch.setattr(harness, "atoms", lambda *args: frozenset())
    monkeypatch.setattr(evaluation, "evaluate", lambda *args, **kw: pytest.fail("a per-formula evaluation"))
    calls = []
    relay = softnorms._relay_run
    monkeypatch.setattr(softnorms, "_relay_run", lambda request: calls.append(request) or relay(request))
    doc = document()
    good, bad = {"RS3o": "good", "RS3i": "x", "RS2": "good"}, {"RS3o": "bad", "RS3i": "x", "RS2": "bad"}
    case_ = {"id": "c"} if name == "anthropic-rsp" else frozenset({("v", "b")})
    facts = harness.check_premises(doc, case_, good)
    assert facts == first
    elaborated_rules = doc.elaborated.selected_rules("x_required", MODEL, ("c",), facts=facts)
    assert [r.name for r in elaborated_rules] == ["d"]
    assert [c["kind"] for c in calls if c["kind"] == "soft-selected"] == ["soft-selected"]  # one case: both answers
    case_bad = {"id": "c2"} if name == "anthropic-rsp" else frozenset({("w", "a")})
    text = ("case c2 does not satisfy premise b2: Violated" if name == "anthropic-rsp"
            else "case model does not satisfy premise b2: Violated")
    with pytest.raises(AssertionError, match=f"^{text}$"):
        harness.check_premises(doc, case_bad, bad)


@pytest.mark.parametrize("value", BAD + [object(), "abc", 7.5], ids=BAD_IDS + ["object", "string", "number"])
def test_a_malformed_facts_value_or_item_is_refused_with_a_diagnostic(lean, value):
    """`facts` itself, or one item of it, replaced by a malformed value: only VEError (Lean's refusal, or the relay's
    for a value no case can carry) or CheckerUnavailable leaves the relay, never a TypeError."""
    for facts in ([value], [SOME_V, value]):
        with pytest.raises((VEError, CheckerUnavailable)):
            soft_route.selected_at(document(), MODEL, QUERIES[:1], facts=facts)
    if value is not None and type(value) not in (list, tuple):  # None: no facts (the default)
        with pytest.raises(VEError, match="facts must be a list"):
            soft_route.selected_at(document(), MODEL, QUERIES[:1], facts=value)


def test_the_records_say_what_soft_wire_selected_states_since_facts():
    """Review kb-9 F2: since `SelectedAnswer` reads "∃ sent facts", `soft_wire_selected` and its prepared twin
    admit the flag fields with any `facts` value for every case (the Lean examples at the end of
    lean/VE/SoftNorms/SelectedExamples.lean check this); only `soft_wire_selected_facts` ties them to the case.
    No record may say the theorem still rules them out or that its meaning is unchanged for a case without facts."""
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    spec = " ".join((root / "docs/spec/kernel-boundary.md").read_text().split())
    report = " ".join((root / "docs/kernel/kb-9/REPORT.md").read_text().split())
    lean = (root / "lean/VE/SoftNorms/SelectedSound.lean").read_text()
    examples = (root / "lean/VE/SoftNorms/SelectedExamples.lean").read_text()
    start = spec.index("Since kb-10a it also lists `VE.SoftNorms.Run.soft_wire_selected`")
    paragraph = spec[start:spec.index("`selected_semantics`", start)]
    assert "is exactly `Wire.ok`" not in paragraph
    assert "`facts`" in paragraph and "`coherent`" in paragraph and "`soft_wire_selected_facts`" in paragraph
    assert "its meaning is unchanged" not in report
    header, _, rest = lean.partition("kb-9: a case that sends `facts`")
    assert "no other field" not in header
    doc = rest[:rest.index("def SelectedAnswer (")]
    doc = doc[doc.rindex("/--"):]
    assert "for a case that sent `facts`" not in doc and "cannot see the case" in doc
    assert "SelectedAnswer id D M qs answer := ⟨true, b, h⟩" in examples
