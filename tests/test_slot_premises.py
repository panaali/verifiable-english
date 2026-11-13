"""The premise slot of the soft route on the wire (kb-3): the `slot-certificate` and `slot-conflict` kinds.

Fixture (a): two strict rules over act X (`x_required`, one sort): `h` requires it where `v` holds, `k` forbids
it where `w` holds, so they collide where both hold. The fact FACT, `forall x. not (v(x) and w(x))`, excludes
that situation. Without facts the document is not CONFLICT-FREE (no certificate exists for the target
`x_required`); with FACT, Lean replays certificates over `Background_base′ ++ [FACT]` and answers CONFLICT-FREE;
a witness in the excluded situation is refused as not satisfying the facts. With `facts: []` each slot kind
answers what its soft twin answers (`slot_wire_empty`), checked on every recorded `soft-certificate` fixture.

The acceptance addendum's six cases (T1 to T6, DRI 2026-11-12 item 5) are the tests named after them. The
relay (`ve.soft_route.check_soft_conflict`, `check_soft_certificate`) checks schema and binding only: `facts`
is the number of facts SENT (`bind_facts`), and a certificate answer's counts are its certificate's premise list.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from tests.test_soft_norms_lean import (SERVICE, base_prime, canonical_norm, elaborate, env, identity, norm,
                                        packages, run, should)
from ve import soft_route
from ve.ast import formula_from_data
from ve.backends.service_schema import Invalid, check_row
from ve.entailment import prove_entailment
from ve.errors import CheckerUnavailable, VEError
from ve.softnorms import SoftEnvironment, SoftNormDocument
from ve.wire import digest

ROOT = Path(__file__).resolve().parents[1]
EXTRA = {name: {"arguments": ["assistant"], "description": name} for name in ("v", "w")}
RULES = [norm("h", "x_required", True, guard=("unary", "v", ["var", 0])),
         norm("k", "x_required", False, guard=("unary", "w", ["var", 0]))]
FACT = ["forall", "assistant", ["not", ["and", ["unary", "v", ["var", 0]], ["unary", "w", ["var", 0]]]]]
NOT_FACT = ["exists", "assistant", ["and", ["unary", "v", ["var", 0]], ["unary", "w", ["var", 0]]]]


def situation(v, w):
    """A base model over E′_base with one assistant `a`."""
    return {"complete": True, "domains": {"assistant": ["a"], "user": []}, "constants": {},
            "relations": {"v": [["a"]] if v else [], "w": [["a"]] if w else []}}


FACTS_MODEL = situation(True, False)  # v(a), not w(a): FACT holds
EXCLUDED = situation(True, True)  # both rules fire at a: the situation FACT excludes
WITNESS = {"target": "x_required", "model": EXCLUDED, "tuple": ["a"]}
# A base conclusion that follows from FACT (and from nothing else in the document).
CLAIM = ["forall", "assistant", ["implies", ["unary", "v", ["var", 0]], ["not", ["unary", "w", ["var", 0]]]]]


@pytest.fixture(scope="module")
def lean():
    if not SERVICE.exists():
        pytest.skip("the Lean service has not been built")


@pytest.fixture(scope="module")
def source(lean):
    raw = env(extra=EXTRA)
    return raw, elaborate("soft-norms", raw, RULES)


def document():
    return SoftNormDocument(SoftEnvironment(env(extra=EXTRA)), RULES)


def one(case):
    return run("soft-norms", [case])[0]


def slot_packages(raw, norms, row, facts):
    """Conflict packages over `Background_base′ ++ facts` (the slot twin of test_soft_norms_lean.packages)."""
    profiles = raw["profiles"]
    env_id = digest(f"ve-environment-{identity(profiles)}\n", raw)
    doc_hash = digest(f"ve-soft-norms-{identity(profiles)}\n",
                      {"environment_id": env_id, "document": [canonical_norm(n) for n in norms]})
    base = base_prime(row)
    premises = [formula_from_data(base, b["ast"]) for b in row["background"] if b["generator"] == "soft"]
    premises += [formula_from_data(base, fact) for fact in facts or ()]
    out = {}
    for t in row["conflict_targets"]:
        closed = ["not", t["ast"]]
        for sort in reversed(t["sorts"]):
            closed = ["forall", sort, closed]
        result = prove_entailment(base, premises, formula_from_data(base, closed))
        if result.status == "Found":
            out[t["target"]] = {"environment_id": env_id, "document_hash": doc_hash, "target": t["target"],
                                "certificate": result.certificate}
    return out


def slot_certificate(row, facts, conclusion, premises=()):
    """A certificate of `conclusion` over E′ from `background′ ++ facts ++ layer premises ++ premises`, bound as
    `replaySlotEntailment` binds it (the premise ids in that order)."""
    prime = row["environment_prime"]
    profiles = prime["profiles"]
    env_id = digest("ve-environment-v0.2:" + ",".join(profiles) + "\n", prime)
    decoded = SoftEnvironment(prime, generated=True)
    listed = ([item["ast"] for item in row["background"]] + list(facts) + [item["ast"] for item in row["premises"]]
              + list(premises))
    proof = prove_entailment(decoded, [formula_from_data(decoded, ast) for ast in listed[1:]],
                             formula_from_data(decoded, conclusion))
    assert proof.status == "Found", proof
    meaning = lambda ast: digest("ve-meaning-v0.2:" + ",".join(profiles) + "\n", {"environment_id": env_id, "ast": ast})
    return {**proof.certificate, "environment_id": env_id,
            "premise_meaning_ids": [meaning(ast) for ast in listed], "conclusion_meaning_id": meaning(conclusion)}


def conflict_case(raw, row, facts=None, *, witness=None, facts_model=None, certified_with=None):
    kind = "soft-conflict" if facts is None else "slot-conflict"
    case = {"id": "c", "kind": kind, "environment": raw, "norms": RULES}
    if facts is not None:
        case["facts"] = facts
    if facts_model is not None:
        case["facts_model"] = facts_model
    if witness is not None:
        case["witness"] = witness
    else:
        case["packages"] = slot_packages(raw, RULES, row, facts if certified_with is None else certified_with)
    return case


def certificate_case(raw, row, facts, *, conclusion=CLAIM, certified_with=None, facts_model=FACTS_MODEL):
    case = {"id": "c", "kind": "slot-certificate", "environment": raw, "norms": RULES, "premises": [],
            "conclusion": conclusion, "facts": facts,
            "certificate": slot_certificate(row, facts if certified_with is None else certified_with, conclusion)}
    if facts and facts_model is not None:
        case["facts_model"] = facts_model
    return case


# ---------------------------------------------------------------------------------------------------
# Fixture (a): the fact turns UNKNOWN into CONFLICT-FREE, and refuses a witness it excludes.

def test_fixture_a_is_conflict_free_only_with_the_fact(source):
    raw, row = source
    assert [t["target"] for t in row["conflict_targets"]] == ["x_permitted", "x_required", "x_required->x_permitted"]
    soft = one(conflict_case(raw, row))
    empty = one(conflict_case(raw, row, []))
    assert soft["verdict"] == empty["verdict"] == "UNKNOWN"
    assert empty["detail"] == soft["detail"] == "missing certificate for x_required"
    assert empty == {**soft, "facts": 0}
    with_fact = one(conflict_case(raw, row, [FACT], facts_model=FACTS_MODEL))
    assert with_fact["verdict"] == "CONFLICT-FREE", with_fact
    assert with_fact["facts"] == 1 and "detail" not in with_fact
    # The relay: the same verdicts, bound to the request.
    relayed = soft_route.check_soft_conflict(document(), packages=slot_packages(raw, RULES, row, [FACT]),
                                             facts=[FACT], facts_model=FACTS_MODEL)
    assert relayed["verdict"] == "CONFLICT-FREE" and relayed["facts"] == 1
    assert soft_route.check_soft_conflict(document(), packages=slot_packages(raw, RULES, row, []),
                                          facts=[])["verdict"] == "UNKNOWN"


def test_fixture_a_the_facts_certificates_do_not_serve_without_the_facts(source):
    """Packages proved over `Background_base′ ++ [FACT]` are bound to that list: sent without the fact (as soft or
    slot with no facts) they bind nothing, and the target is UNKNOWN."""
    raw, row = source
    for facts in (None, []):
        answer = one(conflict_case(raw, row, facts, certified_with=[FACT]))
        # No package binds, so the first target in order is the first failure.
        assert answer["verdict"] == "UNKNOWN" and answer["detail"] == "missing certificate for x_permitted"


def test_fixture_a_a_witness_in_the_excluded_situation_is_refused(source):
    raw, row = source
    soft = one(conflict_case(raw, row, witness=WITNESS))
    empty = one(conflict_case(raw, row, [], witness=WITNESS))
    assert soft["verdict"] == empty["verdict"] == "CONFLICT"
    assert empty == {**soft, "facts": 0}
    refused = one(conflict_case(raw, row, [FACT], witness=WITNESS))
    assert refused["status"] == "error"
    assert refused["error"] == "InvalidModel(facts): the model violates a fact"
    with pytest.raises(VEError, match=re.escape("InvalidModel(facts): the model violates a fact")):
        soft_route.check_soft_conflict(document(), witness=WITNESS, facts=[FACT])
    # A witness that also violates the soft background keeps the soft diagnostic.
    assert soft_route.check_soft_conflict(document(), witness=WITNESS, facts=[])["verdict"] == "CONFLICT"


def test_a_slot_certificate_with_its_fact_is_valid(source):
    raw, row = source
    answer = one(certificate_case(raw, row, [FACT]))
    assert answer["status"] == "ok" and answer["valid"] is True and answer["facts"] == 1
    relayed = soft_route.check_soft_certificate(document(), premises=[], conclusion=CLAIM,
                                                certificate=certificate_case(raw, row, [FACT])["certificate"],
                                                facts=[FACT], facts_model=FACTS_MODEL)
    assert relayed == {"valid": True, "background": len(row["background"]), "layers": len(row["premises"]),
                       "conditional_on": [], "facts": 1}


# ---------------------------------------------------------------------------------------------------
# (b): with no facts, slot-certificate is soft-certificate on every recorded soft-certificate fixture.

def recorded_soft_certificates():
    seen, out = set(), []
    for path in sorted((ROOT / "tests").rglob("*.jsonl")):
        for line in path.read_text().splitlines():
            if '"soft-certificate"' not in line:
                continue
            record = json.loads(line)
            for case in (x for x in (record if type(record) is list else [record]) if type(x) is dict):
                if case.get("kind") == "soft-certificate":
                    key = json.dumps(case, sort_keys=True)
                    if key not in seen:
                        seen.add(key)
                        out.append(case)
    return out


def test_slot_certificate_with_no_facts_is_soft_certificate_on_every_fixture(lean):
    fixtures = recorded_soft_certificates()
    assert len(fixtures) >= 2
    for case in fixtures:
        soft = one(case)
        assert soft["status"] == "ok", soft
        slot = one({**case, "kind": "slot-certificate", "facts": []})
        assert slot == {**soft, "facts": 0}, (case["conclusion"], slot, soft)
        # `facts` is required by the slot kinds (absent is refused, never read as the soft answer).
        absent = one({**case, "kind": "slot-certificate"})
        assert absent["error"] == "InvalidInput: a slot case needs a facts array"


# ---------------------------------------------------------------------------------------------------
# The acceptance addendum (T1 to T6).

def _all_kinds(raw, row, facts):
    """The three slot answers for `facts`: a certificate, a conflict over packages, a witness."""
    return {
        "slot-certificate": {**certificate_case(raw, row, [], conclusion=["top"]), "facts": facts,
                             "facts_model": FACTS_MODEL},
        "slot-conflict": {**conflict_case(raw, row, []), "facts": facts, "facts_model": FACTS_MODEL},
        "slot-conflict witness": {**conflict_case(raw, row, [], witness=WITNESS), "facts": facts},
    }


RULE_FACTS = {
    "the rule's regulated predicate": ["forall", "assistant", ["unary", "x_required", ["var", 0]]],
    "the obligation's permission": ["forall", "assistant", ["unary", "x_permitted", ["var", 0]]],
    "a layer symbol under a connective": ["forall", "assistant", ["implies", ["unary", "v", ["var", 0]],
                                                                  ["unary", "x_required", ["var", 0]]]],
}


@pytest.mark.parametrize("name", sorted(RULE_FACTS))
def test_slot_fact_cannot_discharge_rule(source, name):
    """T1 (F4): a fact naming a rule's regulated predicate, an obligation's act or a layer symbol is refused by the
    decoder's own diagnostic on both kinds (and the witness form), before anything is replayed; so a
    slot-certificate of a rule's conclusion is never made valid by a fact asserting it."""
    raw, row = source
    fact = RULE_FACTS[name]
    for kind, case in _all_kinds(raw, row, [fact]).items():
        answer = one(case)
        assert answer == {"id": "c", "status": "error", "error": "ill-typed or unbound formula",
                          "code": "SOFT_INVALID_INPUT"}, (kind, answer)
    # The rule's conclusion as the claim, the fact asserting it as the slot: refused, never `valid`.
    conclusion = RULE_FACTS["the rule's regulated predicate"]
    case = {"id": "c", "kind": "slot-certificate", "environment": raw, "norms": RULES, "premises": [],
            "conclusion": conclusion, "facts": [conclusion], "facts_model": FACTS_MODEL,
            "certificate": slot_certificate(row, [], conclusion, premises=[conclusion])}
    assert one(case)["error"] == "ill-typed or unbound formula"
    with pytest.raises(VEError, match="ill-typed or unbound formula"):
        soft_route.check_soft_certificate(document(), premises=[], conclusion=conclusion,
                                          certificate=case["certificate"], facts=[conclusion],
                                          facts_model=FACTS_MODEL)


def test_slot_fact_cannot_name_a_soft_decision_predicate(lean):
    """T1, the soft layer's own symbols: an exception's decision predicate is an open term its decider decides
    (docs/spec/kernel-boundary.md 4.1), so a fact naming it is refused, though it is in the base vocabulary."""
    raw = env()
    rules = [should("d", "x_required", True)]
    excepted = ["forall", "assistant", ["unary", "soft__excepted__d", ["var", 0]]]
    answer = one({"id": "c", "kind": "slot-conflict", "environment": raw, "norms": rules, "packages": {},
                  "facts": [excepted]})
    assert answer["error"] == ("InvalidInput: facts: soft__excepted__d is a soft decision predicate; "
                               "its decider decides it, not a fact")
    assert one({"id": "c", "kind": "slot-conflict", "environment": raw, "norms": rules, "packages": {},
                "facts": []})["verdict"] == "UNKNOWN"


def _forged(row, **fields):
    return {**copy.deepcopy(row), **fields}


def test_slot_binding_from_request_not_answer(source, monkeypatch):
    """T2 (N1): Lean decodes P only from the request's `facts`, and the relay binds the answer's `facts` count and
    the certificate's premise list to what was SENT. A request that drops, adds or reorders a fact against its
    certificate is refused by Lean's binding; an answer whose count is not the number sent (as if taken from the
    answer itself) is refused by the relay."""
    raw, row = source
    two = [FACT, ["forall", "assistant", ["top"]]]
    case = certificate_case(raw, row, two)
    assert one(case)["valid"] is True
    for name, sent in {"dropped": two[:1], "added": two + [["top"]], "reordered": two[::-1]}.items():
        answer = one({**case, "facts": sent})
        assert answer["error"] == "certificate is stale or bound to different inputs", (name, answer)
    # The relay: the genuine answer is bound; a count other than the number sent is refused, whatever the
    # answer's other fields say.
    genuine = one(case)
    elaborated = row
    soft_route.bind_certificate(genuine, case, elaborated)
    for count in (0, 1, 3, True, "2", None):
        with pytest.raises(ValueError, match="facts count is not the number of facts sent"):
            soft_route.bind_certificate(_forged(genuine, facts=count), case, elaborated)
    # A consistent forgery: the count and the premise list both shifted by one is refused by the premise list.
    with pytest.raises(ValueError):
        soft_route.bind_certificate(_forged(genuine, facts=3, layers=genuine["layers"] - 1), case, elaborated)
    # The conflict relay binds the same count.
    conflict = conflict_case(raw, row, [FACT], facts_model=FACTS_MODEL)
    genuine = one(conflict)
    soft_route.bind_conflict(genuine, conflict, row)
    for count in (0, 2, False):
        with pytest.raises(ValueError, match="facts count is not the number of facts sent"):
            soft_route.bind_conflict(_forged(genuine, facts=count), conflict, row)
    with pytest.raises(ValueError, match="a soft answer names facts"):
        soft_route.bind_conflict(genuine, {k: v for k, v in conflict.items() if k != "facts"}, row)


@pytest.mark.parametrize("item, message", [
    (["forall", "assistant", ["unary", "undeclared", ["var", 0]]], "ill-typed or unbound formula"),
    (7, None),
    ("", None),
    ({"forall": "assistant"}, None),
    (["unary", "v", ["var", 0]], "ill-typed or unbound formula"),  # open: an unbound variable
])
def test_slot_every_fact_item_decoded(source, item, message):
    """T3 (N2): every item of `facts` decodes or the case is refused with a diagnostic; none is skipped or dropped,
    so the decoded count is the number of items sent."""
    raw, row = source
    for kind, case in _all_kinds(raw, row, [FACT, item]).items():
        answer = one(case)
        assert answer["status"] == "error", (kind, answer)
        if message is not None:
            assert answer["error"] == message, (kind, answer)
        assert answer["error"], (kind, answer)
    # Not an array (the restricted wire refuses `null` before Lean reads the case).
    for value in (7, "facts", {"0": FACT}, True):
        for kind, case in _all_kinds(raw, row, value).items():
            answer = one(case)
            assert answer["status"] == "error", (kind, value, answer)
            assert answer["error"] in ("InvalidInput: facts must be an array", "InvalidInput: a slot case needs a facts array")
    # Accepted: every item counted.
    accepted = one(conflict_case(raw, row, [FACT, FACT, ["top"]], facts_model=FACTS_MODEL,
                                 certified_with=[FACT, FACT, ["top"]]))
    assert accepted["facts"] == 3 and accepted["verdict"] == "CONFLICT-FREE"


@pytest.mark.parametrize("name, fact", [
    ("a made-up constant", ["unary", "v", ["const", "nobody"]]),
    ("a made-up predicate", ["forall", "assistant", ["unary", "made_up_act", ["var", 0]]]),
    ("a declared predicate at the wrong arity", ["forall", "assistant", ["binary", "v", ["var", 0], ["var", 0]]]),
    ("a declared predicate at the wrong sort", ["forall", "user", ["unary", "v", ["var", 0]]]),
])
def test_slot_fact_unknown_target_refused(source, name, fact):
    """T4 (F6): a fact naming a constant or act the base vocabulary does not declare, or a declared symbol at the
    wrong sort or arity, is refused."""
    raw, row = source
    for kind, case in _all_kinds(raw, row, [fact]).items():
        answer = one(case)
        assert answer["status"] == "error" and answer["code"] == "SOFT_INVALID_INPUT", (name, kind, answer)
        assert answer["error"] == "ill-typed or unbound formula", (name, kind, answer)


def test_slot_inconsistent_facts_refused(source):
    """T5 (N3): facts that contradict each other or the base never yield CONFLICT-FREE or `valid`: a non-empty slot
    needs a `facts_model` in which the background and every fact hold (`factsModel`;
    `slot_wire_conflict_facts`, `slot_wire_entailment_facts`), and none exists for [p(a), not p(a)]."""
    raw, row = source
    p, not_p = ["forall", "assistant", ["unary", "v", ["var", 0]]], ["forall", "assistant", ["not", ["unary", "v", ["var", 0]]]]
    inconsistent = [p, not_p]
    for model in (situation(True, False), situation(False, False), None):
        conflict = one(conflict_case(raw, row, inconsistent, facts_model=model, certified_with=inconsistent))
        certificate = one(certificate_case(raw, row, inconsistent, facts_model=model))
        for answer in (conflict, certificate):
            assert answer["status"] == "error", answer
            assert answer["error"] in ("InvalidModel(facts): the model violates a fact",
                                       "InvalidInput: facts need a facts_model: a base model of the background and the facts")
    # The same facts one at a time are consistent: each is answered.
    assert one(conflict_case(raw, row, [p], facts_model=situation(True, False)))["status"] == "ok"
    assert one(conflict_case(raw, row, [not_p], facts_model=situation(False, False)))["status"] == "ok"
    # Contradicting the fixture's own fact: NOT_FACT with FACT.
    answer = one(conflict_case(raw, row, [FACT, NOT_FACT], facts_model=EXCLUDED, certified_with=[FACT, NOT_FACT]))
    assert answer["error"] == "InvalidModel(facts): the model violates a fact"
    # A facts model must also pass the soft background.
    soft_raw = env()
    rules = [should("d", "x_required", True)]
    bad = {"complete": True, "domains": {"assistant": ["a"], "user": []}, "constants": {}, "relations": {}}
    answer = one({"id": "c", "kind": "slot-conflict", "environment": soft_raw, "norms": rules, "packages": {},
                  "facts": [["forall", "assistant", ["top"]]], "facts_model": bad})
    assert answer["status"] == "error", answer


# ---------------------------------------------------------------------------------------------------
# (d): `facts` retyped or rebound in the two answers is refused by the schema and by the relay.

RETYPED = {"deleted": ..., "7": 7, "true": True, "null": None, "[]": [], "{}": {}, "1.5": 1.5, "-1": -1,
           "lone surrogate": "\ud800", "deep list": None, "shifted up": "+1", "shifted down": "-1"}


def _deep():
    value = []
    for _ in range(10_000):
        value = [value]
    return value


def _retyped(row, name):
    forged = copy.deepcopy(row)
    if name == "deleted":
        del forged["facts"]
    elif name == "deep list":
        forged["facts"] = _deep()
    elif name in ("shifted up", "shifted down"):
        forged["facts"] = row["facts"] + (1 if name == "shifted up" else -1)
    else:
        forged["facts"] = RETYPED[name]
    return forged


def genuine_answers(raw, row):
    """(case, row, call) for each slot answer with one fact: a certificate, a conflict over packages, a witness
    (with facts [] the excluded witness is the one that conflicts)."""
    certificate = certificate_case(raw, row, [FACT])
    conflict = conflict_case(raw, row, [FACT], facts_model=FACTS_MODEL)
    witness = conflict_case(raw, row, [], witness=WITNESS)
    return {
        "slot-certificate": (certificate, lambda: soft_route.check_soft_certificate(
            document(), premises=[], conclusion=CLAIM, certificate=certificate["certificate"], facts=[FACT],
            facts_model=FACTS_MODEL)),
        "slot-conflict": (conflict, lambda: soft_route.check_soft_conflict(
            document(), packages=conflict["packages"], facts=[FACT], facts_model=FACTS_MODEL)),
        "slot-conflict witness": (witness, lambda: soft_route.check_soft_conflict(document(), witness=WITNESS,
                                                                                   facts=[])),
    }


@pytest.mark.parametrize("name", sorted(RETYPED))
def test_facts_retyped_or_rebound_is_unavailable(source, monkeypatch, name):
    raw, row = source
    for kind, (case, call) in genuine_answers(raw, row).items():
        genuine = one(case)
        assert genuine["status"] == "ok" and genuine["facts"] == len(case["facts"]), (kind, genuine)
        check_row("soft-norms", genuine, case, 0)
        forged = _retyped(genuine, name)
        if name == "shifted down" and genuine["facts"] == 0:
            forged["facts"] = -1
        with pytest.raises(Invalid):
            check_row("soft-norms", forged, case, 0)
        real = soft_route._run
        with monkeypatch.context() as patch:  # past the schema: the relay's own binding
            patch.setattr(soft_route, "_run", lambda request: forged  # the relay never writes to the row
                          if request["kind"].startswith("slot-") else real(request))
            with pytest.raises(CheckerUnavailable, match="not bound to the request"):
                call()
        assert call()["facts"] == genuine["facts"]


def test_certificate_conditional_labels_are_bound(lean):
    """A certificate answer's `conditional_on` names open coherence labels of the document, once each, and none beside
    an invalid certificate (`bind_certificate`); the genuine labels are kept."""
    raw = env()
    rules = [should("a", "x_required", True), should("b", "x_permitted", False)]
    row = elaborate("soft-norms", raw, rules)
    assert row["conditional_on"] == ["soft:coherence:a,b"]
    for kind, facts in (("soft-certificate", None), ("slot-certificate", [])):
        case = {"id": kind, "kind": kind, "environment": raw, "norms": rules, "premises": [], "conclusion": ["top"],
                "certificate": {"premise_meaning_ids": [0] * (len(row["background"]) + len(row["premises"]))}}
        if facts is not None:
            case["facts"] = facts
        genuine = {"id": kind, "status": "ok", "valid": True, "background": len(row["background"]),
                   "layers": len(row["premises"]), "conditional_on": ["soft:coherence:a,b"],
                   **({"facts": 0} if facts is not None else {})}
        assert soft_route.bind_certificate(genuine, case, row)["conditional_on"] == ["soft:coherence:a,b"]
        for forged in (["ghost"], ["soft:coherence:a,b"] * 2, ["soft:coherence:b,a"], [7]):
            with pytest.raises(ValueError, match="unbound certificate conditional labels"):
                soft_route.bind_certificate(_forged(genuine, conditional_on=forged), case, row)
        with pytest.raises(ValueError, match="unbound certificate conditional labels"):
            soft_route.bind_certificate(_forged(genuine, valid=False), case, row)


REPORT = ROOT / "docs/kernel/kb-3a/REPORT.md"
CLAIM_ROW = re.compile(r"^\| (?P<claim>[^|]+?) \| `(?P<verdict>[^`]+)` \| `(?P<test>tests/[^`]+?)(?:::(?P<name>\w+))?` \|$",
                       re.M)


def test_slot_report_claims_have_runs():
    """T6 (pcfd-text-1): every verdict the REPORT's claim table states names the test that produces it, and that
    test asserts the exact string the REPORT prints."""
    text = REPORT.read_text()
    section = text[text.index("## Claims and their runs"):]
    section = section[:section.index("\n## ", 3)] if "\n## " in section[3:] else section
    rows = list(CLAIM_ROW.finditer(section))
    assert len(rows) >= 8, "the claim table is missing or unparsed"
    for match in rows:
        source = (ROOT / match["test"]).read_text()
        body = source
        if match["name"]:
            start = source.index(f"def {match['name']}(")
            end = source.find("\ndef ", start + 1)
            body = source[start:end if end != -1 else None]
        assert match["verdict"] in body, (match["claim"], match["verdict"], match["test"], match["name"])
