"""Answers that hold unless an exception applies, through the Lean service (defeasible plan 4.1 and 4.2, batch DF-1b).

Plan 4.1's synthetic fixtures (weighing's soft frame: one sort `assistant`, `x_required` unspecified with
`x_permitted` its allow-by-default dual, decider "the assistant") go through `ve.defaults.ask`: the strict question
first, then the default one with Python's untrusted search, every verdict, basis, form and assumption Lean's. P-1's
three probe documents (df-03's, `docs/research/evidence/defeasible/baseline/`) go through `ve document readings
--assume-no-exception`; without the flag their answers are df-03's recorded ones, byte for byte.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
from pathlib import Path

import pytest

from ve import defaults
from ve.backends import relay
from ve.document import cli, main
from ve.document.load import load_document
from ve.errors import CheckerUnavailable, UnsupportedProfile, VEError

BASELINE = Path(__file__).resolve().parents[1] / "docs/research/evidence/defeasible/baseline"
STRICT = {"outranking": {"mode": "strict"}}
HOLISTIC = {"ranks": ["safety", "helpfulness"], "outranks": [["safety", "helpfulness"]],
            "outranking": {"mode": "holistic", "decided_by": "assistant"}}


def _regulated(name, role, default, **extra):
    return {"arguments": ["assistant"], "description": name,
            "regulated": {"role": role, "default": default, "act": "{0} do x", **extra}}


def env(soft=STRICT, base=(), profiles=()):
    predicates = {"x_required": _regulated("x_required", "obligation", "unspecified", permission="x_permitted"),
                  "x_permitted": _regulated("x_permitted", "permission", "allow"),
                  **{p: {"arguments": ["assistant"], "description": p} for p in base}}
    return {"language": "ve.core@0.2", "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "profiles": sorted(["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0", *profiles]),
            "vocabulary": {"sorts": {"assistant": {"description": "assistant"}}, "predicates": predicates,
                           "constants": {}, "soft": soft}}


def rule(name, predicate, sign, default=True, sufficient=(), decider="assistant", **extra):
    norm = {"name": name, "predicate": predicate, "sign": sign, "guard": ["top"], "unless": [], "over": []}
    if default:
        norm.update(mode="default", exception={"decided_by": decider, "sufficient": list(sufficient),
                                               "necessary": [], "factors": []}, **extra)
    return {"norm": norm}


def un(p):
    return ["unary", p, ["var", 0]]


X_ALL = ["forall", "assistant", un("x_required")]
UNLESS_URGENT = ["forall", "assistant", ["implies", ["not", un("urgent")], un("x_required")]]
R1 = rule("r1", "x_required", True)
DOCS = {
    "alpha": (env(), [R1]),
    "beta": (env(base=["urgent"]), [rule("r1", "x_required", True, sufficient=[un("urgent")])]),
    "beta2": (env(base=["calm", "urgent"]), [rule("r1", "x_required", True, sufficient=[un("calm"), un("urgent")]),
                                             rule("r2", "x_required", True, sufficient=[un("urgent")])]),
    "gamma": (env(), [R1, rule("r2", "x_permitted", False)]),
    "gamma'": (env({"parties": ["operator"], **STRICT}), [R1, rule("r2", "x_permitted", False, decider="operator")]),
    "gamma2": (env(), [R1, rule("r2", "x_permitted", False), rule("r3", "x_permitted", False)]),
    "delta": (env(HOLISTIC), [rule("r1", "x_required", True, rank="safety"),
                              rule("r2", "x_permitted", False, rank="helpfulness")]),
    "epsilon": (env({"parties": ["user"], **STRICT}), [rule("r1", "x_required", True, alterable=["user"])]),
    "zeta": (env(), [rule("r0", "x_required", True, default=False), R1]),
}


def asked(monkeypatch, name, conclusion=X_ALL, premises=()):
    """`ask`'s answer on fixture `name`, and every (case, row) it sent the service."""
    sent, real = [], relay.decide

    def decide(mode, cases, **options):
        rows = real(mode, cases, **options)
        sent.extend(zip(copy.deepcopy(cases), copy.deepcopy(rows)))
        return rows
    monkeypatch.setattr(relay, "decide", decide)
    environment, norms = DOCS[name]
    out = defaults.ask(environment, norms, list(premises), conclusion)
    monkeypatch.setattr(relay, "decide", real)
    return out, sent


def sent_kind(sent, kind):
    return next((case, row) for case, row in sent if case.get("kind") == kind)


# DE1 and DE2 (tests/test_defaults_english.py has every form)
ALPHA_ENGLISH = ["Unless an exception applies, the conclusion follows: Every assistant must do x.",
                 "This assumes that the exception to rule r1 does not apply. The assistant decides where it applies; "
                 "the text names no case."]


def follows(basis, form, assumptions):
    return {"verdict": "FOLLOWS", "basis": basis, "form": form, "assumptions": assumptions,
            "deciders": ["assistant"]}


def test_alpha_needs_its_one_exception_and_the_strict_countermodel(monkeypatch):
    out, sent = asked(monkeypatch, "alpha")
    assert out == {"question": "default", "kind": "defaults-certificate",
                   "answer": follows("needs", "short", ["default:exception:r1"]), "english": ALPHA_ENGLISH}
    case, _ = sent_kind(sent, "defaults-certificate")
    assert {"certificate", "model", "strict_model"} <= set(case)
    # DF-α′: the same request without the strict countermodel is `unsettled`, never `needs`
    del case["strict_model"]
    assert defaults.answer(case, ["default:exception:r1"])["basis"] == "unsettled"


def test_beta_forced_exception_and_its_condition(monkeypatch):
    out, _ = asked(monkeypatch, "beta")
    assert out["kind"] == "defaults-model" and out["answer"]["verdict"] == "DOES-NOT-FOLLOW"
    [entry] = out["answer"]["forced"]
    assert (entry["rule"], entry["condition"], len(entry["tuple"])) == ("r1", 0, 1)
    out, _ = asked(monkeypatch, "beta", UNLESS_URGENT)
    assert out["answer"] == follows("needs", "long", ["default:exception:r1"])


def test_beta2_forced_entries_in_rule_then_tuple_order(monkeypatch):
    """Two rules, two conditions: each entry names the first condition that holds at its tuple, and Lean's order
    (rule order, then the model's tuple order) passes the relay's binding."""
    out, sent = asked(monkeypatch, "beta2", ["forall", "assistant", ["implies", ["not", un("urgent")],
                                                                     un("x_required")]])
    assert out["answer"]["verdict"] in ("FOLLOWS", "DOES-NOT-FOLLOW")
    case, _ = sent_kind(sent, "norm-defaults-elaborate")
    two = {"filling": {}, "model": {"complete": True, "constants": {}, "domains": {"assistant": ["e1", "e2"]},
                                    "relations": {"calm": [["e1"], ["e2"]], "urgent": [["e1"], ["e2"]],
                                                  "soft__excepted__r1": [["e1"], ["e2"]],
                                                  "soft__excepted__r2": [["e1"], ["e2"]]}}}
    row = defaults.answer({**{k: case[k] for k in ("environment", "norms")}, "id": "m", "kind": "defaults-model",
                           "premises": [], "conclusion": X_ALL, "model": two})
    assert [(e["rule"], e["condition"], e["tuple"]) for e in row["forced"]] == [
        ("r1", 0, ["e1"]), ("r1", 0, ["e2"]), ("r2", 0, ["e1"]), ("r2", 0, ["e2"])]


@pytest.mark.parametrize("name, deciders", [("gamma", ["assistant"]), ("gamma'", ["assistant", "operator"])])
def test_gamma_collision_gates_every_question(monkeypatch, name, deciders):
    out, _ = asked(monkeypatch, name)
    assert out["answer"] == {"verdict": "UNKNOWN", "reason": "with no exception, rules r1 and r2 conflict"}
    assert out["coherence"]["verdict"] == "COLLISION"
    assert out["coherence"]["collision"]["rules"] == ["r1", "r2"]
    assert out["coherence"]["collision"]["deciders"] == deciders


def test_omega_no_evidence_is_unknown_never_collision(monkeypatch):
    _, sent = asked(monkeypatch, "gamma")
    case, _ = sent_kind(sent, "defaults-coherence")
    bare = {k: v for k, v in case.items() if k not in ("coherence", "collision")}
    targets = sent_kind(sent, "defaults-elaborate")[1]["coherence_targets"]
    row = defaults.answer(bare, targets=targets)
    assert (row["verdict"], [p["status"] for p in row["pairs"]]) == ("UNKNOWN", ["unknown"])
    certificate, _ = sent_kind(sent, "defaults-certificate")
    no_gate = {k: v for k, v in certificate.items() if k not in ("coherence", "collision")}
    assert defaults.answer(no_gate)["reason"] == "no-exception coherence not checked"


def test_delta_rank_resolved_and_its_ranking_assumption(monkeypatch):
    out, _ = asked(monkeypatch, "delta")
    assert out["coherence"] == {"verdict": "COHERENT", "pairs": [{"rules": ["r1", "r2"], "status": "resolved"}]}
    answer = out["answer"]
    assert (answer["verdict"], answer["basis"], answer["form"]) == ("FOLLOWS", "needs", "long")
    assert {"default:exception:r1", "default:ranking:helpfulness:safety:x_permitted"} <= set(answer["assumptions"])


def test_epsilon_switch_is_the_long_form(monkeypatch):
    out, _ = asked(monkeypatch, "epsilon")
    assert out["answer"] == follows("needs", "long", ["default:exception:r1", "default:switch:r1:user"])


def test_zeta_strict_question_first(monkeypatch):
    """A conclusion the document's own premises give is answered by the strict question; no default case is sent."""
    out, sent = asked(monkeypatch, "zeta")
    assert out == {"question": "strict", "valid": True, "deciders": ["assistant"],
                   "english": ["This holds whatever the assistant decides."]}
    assert not any(case.get("kind") in ("defaults-certificate", "defaults-model") for case, _ in sent)


def test_de5_strict_decider_boundaries(monkeypatch):
    """DE5 names all of Lean's deciders, and is absent when there is no default premise."""
    monkeypatch.setitem(DOCS, "zeta0", (env(), [rule("r0", "x_required", True, default=False)]))
    out, sent = asked(monkeypatch, "zeta0")
    assert out == {"question": "strict", "valid": True}
    assert sent_kind(sent, "defaults-elaborate")[1]["deciders"] == []
    two = [rule("r0", "x_required", True, default=False), R1,
           rule("r2", "x_required", True, decider="operator")]
    monkeypatch.setitem(DOCS, "zeta2", (env({"parties": ["operator"], **STRICT}), two))
    out, sent = asked(monkeypatch, "zeta2")
    assert sent_kind(sent, "defaults-elaborate")[1]["deciders"] == ["assistant", "operator"]
    assert out == {"question": "strict", "valid": True, "deciders": ["assistant", "operator"],
                   "english": ["This holds whatever the assistant and the operator decide."]}


def test_eta_and_theta_are_lean_diagnostics(monkeypatch):
    with pytest.raises(VEError, match=r"^InvalidInput: a question that assumes no exception may state facts only; "
                                      r"it states whether rule r1's exception applies$"):
        asked(monkeypatch, "alpha", premises=[["exists", "assistant", un("soft__excepted__r1")]])
    monkeypatch.setitem(DOCS, "theta", (env(profiles=["weighing@0"]), [R1]))
    with pytest.raises(UnsupportedProfile):
        asked(monkeypatch, "theta")


def test_iota_and_kappa_are_unknown(monkeypatch):
    """DF-ι: premises no situation satisfies follow strictly (Lean's strict route, F-DF1′), and the default question
    on them is UNKNOWN, never FOLLOWS; DF-κ: a certificate bound to another premise list is no certificate."""
    contradictory = [["exists", "assistant", un("urgent")], ["forall", "assistant", ["not", un("urgent")]]]
    out, _ = asked(monkeypatch, "beta", UNLESS_URGENT, premises=contradictory)
    assert out == {"question": "strict", "valid": True, "deciders": ["assistant"],
                   "english": ["This holds whatever the assistant decides."]}
    _, sent = asked(monkeypatch, "beta", UNLESS_URGENT)
    case, _ = sent_kind(sent, "defaults-certificate")
    assert defaults.answer({**case, "premises": contradictory}, ["default:exception:r1"]) == {
        "id": "defaults", "status": "ok", "verdict": "UNKNOWN",
        "reason": "no checked situation where the premises hold with no exception"}
    _, sent = asked(monkeypatch, "alpha")
    case, _ = sent_kind(sent, "defaults-certificate")
    case["certificate"]["premise_meaning_ids"].pop()
    assert defaults.answer(case, ["default:exception:r1"])["reason"] == "no certificate"


# -- P-1 through `ve document readings` (plan 4.2; df-03's documents and questions)

P1 = json.loads((BASELINE / "baseline.json").read_text())["p1"]


def _readings(capsys, entry, *flags):
    assert main(["readings", entry["argv"][3], "--conclusion", entry["argv"][5], *flags]) == 0
    return capsys.readouterr().out


@pytest.mark.parametrize("entry", P1, ids=[entry["set"] for entry in P1])
def test_p1_follows_unless_an_exception_applies(capsys, monkeypatch, entry):
    monkeypatch.chdir(BASELINE.parents[4])
    out = json.loads(_readings(capsys, entry, "--assume-no-exception"))
    assert out["question"] == "default" and out["kind"] == "defaults-certificate"
    answer = out["answer"]
    assert (answer["verdict"], answer["basis"], answer["form"], len(answer["assumptions"])) == (
        "FOLLOWS", "needs", "short", 1)
    # DE1, then DE2·u: the rule's exception is decided by `unstated` (plan 4.2)
    head, assumed = out["english"]
    assert head.startswith("Unless an exception applies, the conclusion follows: For every instance of Claude, ")
    assert assumed.endswith("does not apply. The text names no case where it applies, and no one who decides.")
    # without the flag, df-03's recorded answer, unchanged
    assert _readings(capsys, entry) == entry["stdout"]


_ASKED = {"asked": "stub"}


def _flag(monkeypatch, path, *flags, conclusion=True):
    """`ve document readings PATH --conclusion C --assume-no-exception FLAGS` with `ask` stubbed: what it prints, or
    the refusal it raises before any question is asked."""
    monkeypatch.chdir(BASELINE.parents[4])
    monkeypatch.setattr(defaults, "ask", lambda environment, norms, premises, conclusion: _ASKED)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert cli.main(["readings", str(path), *(["--conclusion", P1[0]["argv"][5]] if conclusion else []),
                         "--assume-no-exception", *flags]) == 0
    return json.loads(out.getvalue())


def test_flag_refusals(monkeypatch):
    """Each refusal of the flag on both sides, each fixture breaking one condition alone: the P-1 document is asked;
    without a conclusion, with `--under`, `--sentence` or `--narrowing`, on a document with no soft norms, on one
    with a split content-bearing set and on one with a reading set, it is refused before any question is sent; a
    content-bearing set takes the readings' answer (DF-3)."""
    p1 = P1[0]["argv"][3]
    assert _flag(monkeypatch, p1) == _ASKED
    with pytest.raises(VEError, match="requires --conclusion"):
        _flag(monkeypatch, p1, conclusion=False)
    for flags in (["--under", "s:0"], ["--sentence", "u0036.s05"], ["--narrowing", "n"]):
        with pytest.raises(VEError, match="takes no --under, --sentence or --narrowing"):
            _flag(monkeypatch, p1, *flags)
    with pytest.raises(VEError, match="applies to a soft-norms@0 document without open reading sets"):
        _flag(monkeypatch, BASELINE / "control-strict-no-soft-force-u0036-s05.ve.md")
    # DF-3: a content-bearing set (p2-ce4 has one) takes the readings' answer, except with --sentence or --narrowing
    # or beside a split; a reading set alone is still refused (the predicate on the loaded P-1 document)
    monkeypatch.setattr(cli, "_readings_without_exception", lambda doc, conclusion, args: _ASKED)
    assert _flag(monkeypatch, BASELINE / "p2-ce4.ve.md") == _ASKED
    with pytest.raises(VEError, match="takes no --under, --sentence or --narrowing"):
        _flag(monkeypatch, BASELINE / "p2-ce4.ve.md", "--narrowing", "n")
    doc, args = load_document(BASELINE.parents[4] / p1), argparse.Namespace(under=None, sentence=None, narrowing=None)
    assert cli._assume_no_exception(doc, X_ALL, args) == _ASKED
    reading_set = {"id": "s", "unit": "u", "version": 1}
    assert cli._assume_no_exception({**doc, "readings_s1": {"content_bearing": True}}, X_ALL, args) == _ASKED
    for changed in ({**doc, "readings_s1": {"content_bearing": True}, "readings_components": {}},
                    {**doc, "meta": {**doc["meta"], "reading_sets": [reading_set]}}):
        with pytest.raises(VEError, match="applies to a soft-norms@0 document without open reading sets"):
            cli._assume_no_exception(changed, X_ALL, args)


def test_flag_asks_with_the_documents_norms_and_facts(monkeypatch):
    """The flag asks about the document's norms, its facts as premises (an assertion with no content is none) and its
    environment without `readings@1` (Lean's layered route refuses that profile); a document with no soft document is
    refused (review df-1b F10's sweep: each value the flag sends is needed). A unit of any other kind with content (an
    assertion attributed to a party, an example, a question, a definition, an exposition) is neither a norm nor a
    premise (review df-1b hunt 1)."""
    asked_with = []
    monkeypatch.setattr(defaults, "ask", lambda *arguments: asked_with.append(arguments) or _ASKED)
    doc, args = load_document(BASELINE.parents[4] / P1[0]["argv"][3]), argparse.Namespace(
        under=None, sentence=None, narrowing=None)
    [norm] = [unit["content"] for unit in doc["units"]]
    fact = ["exists", "assistant", un("urgent")]
    quoted = ["forall", "assistant", un("urgent")]
    others = [{"kind": kind, "content": quoted} for kind in (["attributed", "bob", "says", "asserted"], "example",
                                                              "question", "definition", "exposition")]
    doc = {**doc, "units": [*doc["units"], {"kind": "asserted", "content": fact},
                            {"kind": "asserted", "content": None}, *others]}
    assert cli._assume_no_exception(doc, X_ALL, args) == _ASKED
    [(environment, norms, premises, conclusion)] = asked_with
    assert environment["profiles"] == ["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0",
                                       "soft-norms@0"]
    assert (norms, premises, conclusion) == ([norm], [fact], X_ALL)
    with pytest.raises(VEError, match="applies to a soft-norms@0 document without open reading sets"):
        cli._assume_no_exception({k: v for k, v in doc.items() if k != "soft_document"}, X_ALL, args)


def test_an_empty_budget_is_unknown(monkeypatch):
    """With no prover step and no domain element to search (budget 0) neither question has evidence: the strict
    question is not answered and the default one is UNKNOWN, never FOLLOWS."""
    monkeypatch.setattr(defaults, "MAX_STEPS", 0)
    monkeypatch.setattr(defaults, "MAX_DOMAIN", 0)
    for name in ("alpha", "zeta"):
        out, _ = asked(monkeypatch, name)
        assert (out["question"], out["answer"]["verdict"]) == ("default", "UNKNOWN"), out


@pytest.mark.parametrize("conclusion", [7, None, [], {}, "x", ["unary", "absent", ["var", 0]]])
def test_a_malformed_conclusion_is_a_diagnostic(monkeypatch, conclusion):
    with pytest.raises(VEError):
        asked(monkeypatch, "alpha", conclusion)
