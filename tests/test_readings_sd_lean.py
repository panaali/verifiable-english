"""Readings under the soft completion through the Lean service (docs/spec/rd-9-soft-chain.md 8.3; plan SC-4).

A document is under the soft completion when `readings@1` and `norm-defaults@0` are on the soft chain and a set is
content-bearing. Lean admits it (4.1), separates its readings on filled sides (4.2: S1's pair check on
`fill (asU N X)`, the situation over the filled author vocabulary, the witness's `Fill_T` on its completion) and
checks each choice on its layered source (4.3: `choiceLayeredG`, soft's premises regenerated on the filled tree).
Python decides nothing here: certificates and packages are proposed by the pinned pre-switch norm-defaults oracle and
the untrusted prover, and Lean replays them; every expected value is the spec's.
"""
from __future__ import annotations

import copy

import pytest

from conformance import norm_defaults_layered as layered
from tests import lean_routes
from tests.test_readings_s1_lean import EXCEPTED, M0, Q0, SOFT_PROFILES, entry, env_k, env_rights, k1_document, \
    norm, reading, reading_set, run, situation_id
from ve.ast import Binary, Forall, Var, formula_from_data, formula_to_data
from ve.entailment import prove_entailment
from ve.wire import digest

LEAN = "ve_readings_route"
SD = ("norm-defaults@0", *SOFT_PROFILES)
STALE = "certificate is stale or bound to different inputs"


@pytest.fixture(scope="module")
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    return LEAN


def env_sd(unspecified=("avoid_required",), extra=None):
    """S1's environment K under `norm-defaults@0`, the named predicates' completion `unspecified`."""
    raw = env_k(profiles=SD)
    raw["vocabulary"]["predicates"].update(extra or {})
    for p in unspecified:
        raw["vocabulary"]["predicates"][p]["regulated"]["default"] = "unspecified"
    return raw


def lower(raw):
    out = copy.deepcopy(raw)
    out["profiles"] = [p for p in out["profiles"] if p != "readings@1"]
    return out


def case(kind, raw, document, **fields):
    return {"id": kind, "kind": kind, "environment": raw, "document": document, **fields}


def one(lean, kind, raw, document, **fields):
    return run(lean, [case(kind, raw, document, **fields)])[0]


def filled_base(fill=(), relations=None):
    base = copy.deepcopy(M0)
    base["relations"].update(relations or {})
    base["relations"]["unsaid__avoid_required"] = [list(r) for r in fill]
    return base


def sigma_default(fill=(), value=False):
    """8.1's σDef: the default reading's table `excepted no-deception = {(a, u)}`, the filling `fill`."""
    return entry(filled_base(fill), "default", Q0, value, decisions=[EXCEPTED])


def fsd1(raw=None, sigma=None, fixed_units=()):
    raw = raw or env_sd()
    document, sid = k1_document(raw, situation=sigma or sigma_default(), fixed_units=fixed_units)
    return raw, document, sid


def layered_model(relations=None):
    """A base situation of a choice's layered source (`situationX`): complete, over `a` and `u`."""
    return {"complete": True, "domains": {"agent": ["a"], "user": ["u"]}, "constants": {},
            "relations": {"asks": [], **(relations or {})}}


def choice_case(raw, document, choice, inner):
    return case("readings-choice", raw, document, choice=[list(x) for x in choice], inner=inner)


# F-SD1: K1 with `avoid_required` unspecified.

def test_fsd1_validate_separates_on_filled_sides(lean):
    """8.3 F-SD1: admitted; the pair separated by 8.1's σ with one gap, `(a, u)` answered no; soft's premises empty
    on both readings (the default twin has no exception condition, no colliding partner); no `F_p` unit."""
    raw, document, sid = fsd1()
    row = one(lean, "readings-validate", raw, document)
    assert row["status"] == "ok", row
    [rs1] = row["sets"]
    pair = {"situation": sid, "witness": "default", "separated": True, "witness_admissible": True,
            "witness_value": False, "other_admissible": True, "other_value": True,
            "gaps": [["avoid_required", ["a", "u"], False]]}
    assert rs1["pairs"] == [{"reading": "strict", "other": "default", "pair": pair},
                            {"reading": "default", "other": "strict", "pair": pair}]
    assert [c["owned"] for c in rs1["candidates"]] == [
        [], [{"key": {"excepted": "no-deception"}, "name": "soft__excepted__no_deception"}]]
    # E25 until `decision_only_soundS` is proved (SC-3, off the path)
    assert rs1["findings"] == ["SeparatedByDecisionOnly: rs1: 0, 1 (not certified)"]
    assert row["soft_premises"] == [{"set": "rs1", "index": 0, "premises": []},
                                    {"set": "rs1", "index": 1, "premises": []}]
    assert row["fill_premises"] == [{"set": "rs1", "index": 0, "premises": []},
                                    {"set": "rs1", "index": 1, "premises": []}]
    filled = row["filled"]
    assert filled["environment"]["profiles"] == ["norms@0", "relational-fol@0", "soft-norms@0"]
    predicates = filled["environment"]["vocabulary"]["predicates"]
    assert predicates["unsaid__avoid_required"]["arguments"] == ["agent", "user"]
    assert predicates["avoid_required"]["regulated"]["default"] == "deny"
    assert [u["unit"] for u in filled["units"]] == ["u1", "u1"]


def test_fsd1_the_filling_yes_does_not_separate(lean):
    """8.1 F-SD1 separation, second value: with the filling yes the default side shows true, as the strict one does."""
    raw, document, sid = fsd1(sigma=sigma_default(fill=[("a", "u")]))
    assert one(lean, "readings-validate", raw, document)["error"] == \
        "distinguishing model does not separate readings"
    separate = one(lean, "readings-separate", raw, document, set="rs1", situation=sid, other="strict")
    assert separate["pair"]["separated"] is False and separate["pair"]["witness_value"] is True


def test_fsd1_separate_elaborate_and_choices(lean):
    raw, document, sid = fsd1()
    separate = one(lean, "readings-separate", raw, document, set="rs1", situation=sid, other="strict")
    assert separate["pair"] == {"situation": sid, "witness": "default", "separated": True,
                                "witness_admissible": True, "witness_value": False, "other_admissible": True,
                                "other_value": True, "gaps": [["avoid_required", ["a", "u"], False]]}
    elaborate = one(lean, "readings-elaborate", raw, document)
    assert {k: elaborate[k] for k in ("route", "finding", "choice_count", "choices", "choices_checked")} == {
        "route": "enumerated",
        "finding": {"text": "ReadingsNotSuperposable: rs1", "cause": "the unspecified completion"},
        "choice_count": 2, "choices": [[["rs1", 0]], [["rs1", 1]]], "choices_checked": 2}
    assert elaborate["soft_premises"] == [{"set": "rs1", "index": 0, "premises": []},
                                          {"set": "rs1", "index": 1, "premises": []}]
    # each choice's layered source: the soft branch's elaboration, `X = []`, the decision in its base environment
    rows = run(lean, [choice_case(raw, document, [("rs1", i)], {"kind": "norm-defaults-elaborate"}) for i in (0, 1)])
    for row in rows:
        assert row["status"] == "ok" and row["inner"]["status"] == "ok", row
        assert row["inner"]["soft"] == [] and row["inner"]["rights"] == []
    assert "soft__excepted__no_deception" in rows[1]["inner"]["base_environment"]["vocabulary"]["predicates"]
    assert "soft__excepted__no_deception" not in rows[0]["inner"]["base_environment"]["vocabulary"]["predicates"]
    # the superposed kinds refuse with the completion's finding; `readings-dead` is answered
    refusal = "ReadingsNotSuperposable: rs1 (the unspecified completion); use readings-choice"
    for kind in ("readings-conflict", "readings-certificate", "readings-model"):
        assert one(lean, kind, raw, document, assumed=[])["error"] == refusal
    dead = one(lean, "readings-dead", raw, document, set="rs1", index=0, certificate={})
    assert dead["status"] == "error" and not dead["error"].startswith("ReadingsNotSuperposable")


def test_fsd1_status_undecided_with_two_admissible_fillings(lean):
    """8.3 F-SD1.status: under the default reading where it is excepted, two admissible fillings give opposite values
    (UNDECIDED); under the strict reading the point is SETTLED yes by `table3`."""
    raw, document, _ = fsd1()
    excepted = layered_model({"soft__excepted__no_deception": [["a", "u"]]})
    undecided = {"kind": "norm-defaults-status", "model": excepted, "predicate": "avoid_required",
                 "tuple": ["a", "u"], "method": "undecided",
                 "yes": {"unsaid__avoid_required": [["a", "u"]]}, "no": {}}
    settled = {"kind": "norm-defaults-status", "model": layered_model(), "predicate": "avoid_required",
               "tuple": ["a", "u"],
               "method": "table3"}
    rows = run(lean, [choice_case(raw, document, [("rs1", 1)], undecided),
                      choice_case(raw, document, [("rs1", 0)], settled)])
    assert rows[0]["inner"]["point_status"] == "UNDECIDED", rows[0]
    assert rows[1]["inner"]["point_status"] == "SETTLED yes", rows[1]


# F-SD2: K18, K1 under the profile with nothing unspecified.

def test_fsd2_k18_is_admitted_on_the_enumerated_row(lean):
    """8.3 F-SD2: K18 reached the abstention before; now it takes the enumerated row, with K1's validate and separate
    answers plus the completion's fields, each empty."""
    raw = env_sd(unspecified=())
    document, sid = k1_document(raw)
    plain = env_k()
    plain_document, _ = k1_document(plain)
    row, k1 = one(lean, "readings-validate", raw, document), one(lean, "readings-validate", plain, plain_document)
    assert row["status"] == "ok", row
    [rs1], [k1_rs1] = row["sets"], k1["sets"]
    for pair, k1_pair in zip(rs1["pairs"], k1_rs1["pairs"]):
        assert pair["pair"].pop("gaps") == []
        assert {**pair["pair"], "situation": None} == {**k1_pair["pair"], "situation": None}
    assert [{k: v for k, v in c.items() if k != "document_hash"} for c in rs1["candidates"]] == \
        [{k: v for k, v in c.items() if k != "document_hash"} for c in k1_rs1["candidates"]]
    assert row["fill_premises"] == row["soft_premises"] == [{"set": "rs1", "index": 0, "premises": []},
                                                             {"set": "rs1", "index": 1, "premises": []}]
    predicates = row["filled"]["environment"]["vocabulary"]["predicates"]
    assert not [p for p in predicates if p.startswith("unsaid__")]
    assert "norm-defaults@0" not in row["filled"]["environment"]["profiles"]
    elaborate = one(lean, "readings-elaborate", raw, document)
    assert (elaborate["route"], elaborate["finding"]) == (
        "enumerated", {"text": "ReadingsNotSuperposable: rs1", "cause": "the unspecified completion"})
    assert one(lean, "readings-elaborate", plain, plain_document)["route"] == "superposed"
    # `readings-choice` answers the layered kinds (route `soft-norms@0`), not S2a's
    inner = run(lean, [choice_case(raw, document, [("rs1", 1)], {"kind": "norm-defaults-elaborate"})])[0]["inner"]
    assert inner["status"] == "ok" and inner["soft"] == [] and inner["unspecified"] == []


def test_fsd6_the_rights_chain_keeps_the_abstention(lean):
    """8.3 F-SD6: K19 (the rights chain) under `norm-defaults@0`: the abstention text, unchanged."""
    raw = env_rights()
    raw["profiles"] = sorted({*raw["profiles"], "norm-defaults@0"})
    arbitrary = ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]]

    def claim(mode):
        return {"right": {"name": "r9", "holder": "person", "guard": ["top"], "lines": [
            {"kind": "claim", "norm": norm("no-arbitrary-arrest", "arrest_permitted", False, mode,
                                           guard=arbitrary)["norm"]}]}}
    rs9 = reading_set("rs9", "u9", [reading("strict", claim("strict"), {}, kind="right"),
                                    reading("default", claim("default"), {}, kind="right")], {})
    row = one(lean, "readings-validate", raw, {"units": [{"id": "u9"}], "reading_sets": [rs9]})
    assert row["error"] == "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented"


# F-SD4: `coherent` beside its strict twin (soft's premises regenerated on the filled tree).

def env4():
    raw = env_k(profiles=SD)
    raw["vocabulary"]["sorts"] = {"assistant": {"description": "assistant"}}
    obligation = {"arguments": ["assistant"], "description": "obligation",
                  "regulated": {"role": "obligation", "default": "deny", "act": "{0} do x", "permission": "x_permitted"}}
    permission = {"arguments": ["assistant"], "description": "permission",
                  "regulated": {"role": "permission", "default": "deny", "act": "{0} do x"}}
    y = {"arguments": ["assistant"], "description": "permission",
         "regulated": {"role": "permission", "default": "unspecified", "act": "{0} do y"}}
    raw["vocabulary"]["predicates"] = {"x_required": obligation, "x_permitted": permission, "y_permitted": y,
                                       "c": {"arguments": ["assistant"], "description": "c"}}
    return raw


def doc4(raw):
    y = ["unary", "y_permitted", ["var", 0]]
    strict = norm("must-x", "x_required", True, guard=y)
    default = norm("must-x", "x_required", True, "default", guard=y)
    default["norm"]["exception"]["sufficient"] = [["unary", "c", ["var", 0]]]
    need_not = norm("need-not-x", "x_required", False, "default")
    rs = reading_set("rs1", "u1", [reading("strict", strict, {}), reading("default", default, {})], {})
    return {"units": [{"id": "u0", "kind": "norm", "content": need_not}, {"id": "u1"}], "reading_sets": [rs]}


def test_fsd4_soft_premises_are_regenerated_on_the_filled_tree(lean):
    """8.1 F-SD4: the strict reading has no soft premise; the default one its exception condition and the coherence
    premise of its pair, whose selections read the unsaid atom `unsaid__y_permitted`."""
    raw = env4()
    row = one(lean, "readings-elaborate", raw, doc4(raw))
    assert row["status"] == "ok", row
    soft = {(e["set"], e["index"]): e["premises"] for e in row["soft_premises"]}
    assert [p["label"] for p in soft[("rs1", 0)]] == []
    assert [p["label"] for p in soft[("rs1", 1)]] == ["soft:exception:must-x:sufficient:0",
                                                      "soft:coherence:must-x,need-not-x"]
    assert ["unsaid__y_permitted" in repr(p["ast"]) for p in soft[("rs1", 1)]] == [False, True]


# F-SD7: the vocabulary limit counts each document's decision predicates.

def test_fsd7_the_vocabulary_limit_counts_the_decisions(lean):
    """252 declared predicates and 4 unspecified: the strict reading's document passes (252 + 0 + 4 = 256), the
    default reading's adds its decision predicate and fails (257)."""
    extra = {f"p{k}": {"arguments": ["agent"], "description": "base"} for k in range(244)}
    extra.update({q: {"arguments": ["agent", "user"], "description": "permission",
                      "regulated": {"role": "permission", "default": "deny", "act": f"{{0}} {verb} {{1}}"}}
                  for q, verb in (("q1_permitted", "greet"), ("q2_permitted", "thank"), ("q3_permitted", "call"))})
    raw = env_sd(unspecified=("avoid_required", "q1_permitted", "q2_permitted", "q3_permitted"), extra=extra)
    assert len(raw["vocabulary"]["predicates"]) == 250
    raw["vocabulary"]["predicates"].update({"r1": {"arguments": ["agent"], "description": "base"},
                                            "r2": {"arguments": ["agent"], "description": "base"}})
    raw, document, _ = fsd1(raw)
    assert one(lean, "readings-validate", raw, document)["error"] == "ResourceLimit: vocabulary size under rs1@1:1"
    del raw["vocabulary"]["predicates"]["r2"]
    _, document, _ = fsd1(raw)
    assert not one(lean, "readings-validate", raw, document).get("error", "").startswith("ResourceLimit")


# F-SD8: evidence for another choice, a filling as a table, a decision table in a separation base.

def test_fsd8_misbound_evidence_is_refused_or_unknown(lean):
    raw, document, _ = fsd1()
    bindings0 = run(lean, [choice_case(raw, document, [("rs1", 0)], {"kind": "norm-defaults-elaborate"})])[0]["inner"]
    doc0 = layered.document("soft", lower(raw), [norm("no-deception", "avoid_required", True)])
    report = layered.nd.check_conflict(doc0, prove=True)
    packages = {t: {**p, "environment_id": bindings0["environment_id"], "document_hash": bindings0["document_hash"]}
                for t, p in report.certificates.items()}
    rows = run(lean, [choice_case(raw, document, [("rs1", 0)], {"kind": "norm-defaults-conflict",
                                                                "packages": packages}),
                      choice_case(raw, document, [("rs1", 1)], {"kind": "norm-defaults-conflict",
                                                                "packages": packages})])
    assert rows[0]["inner"]["verdict"] == "CONFLICT-FREE", rows[0]
    assert rows[1]["inner"]["verdict"] == "UNKNOWN"
    # an `unsaid__` table in a layered model's relations is a filling, never a table (diagnostic 10)
    tabled = layered_model({"unsaid__avoid_required": [["a", "u"]]})
    row = run(lean, [choice_case(raw, document, [("rs1", 1)], {"kind": "choice-model", "model": tabled,
                                                                "filling": {}})])[0]
    assert row["inner"]["error"].startswith("InvalidModel(norm-defaults): unsaid__avoid_required is a filling")
    # a decision table in a separation base is no relation of the author's vocabulary (K2b, diagnostic 9)
    base = filled_base(relations={"soft__excepted__no_deception": [["a", "u"]]})
    raw, document, sid = fsd1(sigma=entry(base, "default", Q0, False, decisions=[EXCEPTED]))
    assert one(lean, "readings-validate", raw, document)["error"] == f"InvalidInput: invalid situation {sid}"


# F-SD9: seven sets, over 64 choices.

def test_fsd9_beyond_64_choices(lean):
    raw = env_sd()
    sets, units = [], []
    for k in range(7):
        rule = f"no-deception-{k}"
        sets.append(reading_set(f"rs{k}", f"u{k}", [reading("strict", norm(rule, "avoid_required", True), {}),
                                                    reading("default", norm(rule, "avoid_required", True, "default"),
                                                            {})], {}))
        units.append({"id": f"u{k}"})
    row = one(lean, "readings-elaborate", raw, {"units": units, "reading_sets": sets})
    assert row["status"] == "ok", row
    assert (row["route"], row["choice_count"], row["choices"]) == ("enumerated", "over 64", "over")


# F-SD10: one gap sentence per gap of the shown value (D9).

def test_fsd10_the_pair_lists_only_the_gap_its_value_reads(lean):
    """K1 with three more unspecified permissions and no rule on them: four unsaid atoms at `(a, u)`, one gap."""
    extra = {f"p{k}_permitted": {"arguments": ["agent", "user"], "description": "permission",
                                 "regulated": {"role": "permission", "default": "deny", "act": f"{{0}} {verb} {{1}}"}}
             for k, verb in ((1, "greet"), (2, "thank"), (3, "call"))}
    raw = env_sd(unspecified=("avoid_required", "p1_permitted", "p2_permitted", "p3_permitted"), extra=extra)
    base = filled_base()
    for k in (1, 2, 3):
        base["relations"][f"unsaid__p{k}_permitted"] = []
    raw, document, _ = fsd1(raw, sigma=entry(base, "default", Q0, False, decisions=[EXCEPTED]))
    row = one(lean, "readings-validate", raw, document)
    assert row["status"] == "ok", row
    assert [p["pair"]["gaps"] for p in row["sets"][0]["pairs"]] == [[["avoid_required", ["a", "u"], False]]] * 2


# F-SD11: a choice's certificate bound by the one binder (`bindCertX`).

ASKS_ALL = ["forall", "agent", ["forall", "user", ["binary", "asks", ["var", 1], ["var", 0]]]]


def _source_meaning(env, ast):
    return digest(f"ve-meaning-{env.identity_version}\n", {"environment_id": env.environment_id, "ast": ast})


def _choice_certificate(lean, raw, document, choice, conclusion, assertions):
    """A certificate the untrusted prover finds over `premisesX L.U L.X A`, bound as `bindCertX` binds it: the source
    environment, Lean's regenerated premises (from the choice's elaboration row), the choice's assertions as written,
    the case's premises (none) and the conclusion."""
    row = run(lean, [choice_case(raw, document, choice, {"kind": "norm-defaults-elaborate"})])[0]["inner"]
    doc = layered.document("soft", lower(raw), [norm("no-deception", "avoid_required", True)])
    filled = doc.filled.env
    regenerated = [formula_from_data(filled, s["ast"], _generated=True) for s in row["soft"]]
    regenerated += [f for _, f in doc.fill_premises] + [f for _, f in doc.filled.premises()]
    asserted = [formula_from_data(filled, a) for a in assertions]
    proof = prove_entailment(filled, (*regenerated, *asserted), conclusion)
    assert proof.status == "Found", proof.status
    asts = ([b["ast"] for b in row["background"]] + [s["ast"] for s in row["soft"]] +
            [f["ast"] for f in row["fill"]] + [p["ast"] for p in row["premises"]] + list(assertions))
    certificate = {**proof.certificate, "environment_id": doc.env.environment_id,
                   "premise_meaning_ids": [_source_meaning(doc.env, a) for a in asts],
                   "conclusion_meaning_id": _source_meaning(doc.env, formula_to_data(filled, conclusion))}
    report = layered.nd.check_conflict(doc, prove=True)
    packages = {t: {**p, "environment_id": row["environment_id"], "document_hash": row["document_hash"]}
                for t, p in report.certificates.items()}
    return certificate, packages, doc


def test_fsd11_a_choice_certificate_binds_the_assertions_it_takes(lean):
    """8.3 F-SD11: F-SD1 with a fixed assertion unit. A certificate of the strict choice is valid and accepted with
    the choice's conflict packages; one whose binding leaves the assertion out, or adds one the choice does not take,
    is diagnostic 11 and not accepted."""
    raw, document, _ = fsd1(fixed_units=[("u0", ASKS_ALL)])
    conclusion = Forall("agent", Forall("user", Binary("avoid_required", Var(1), Var(0))))
    certificate, packages, doc = _choice_certificate(lean, raw, document, [("rs1", 0)], conclusion, [ASKS_ALL])
    inner = {"kind": "norm-defaults-certificate", "premises": [],
             "conclusion": formula_to_data(doc.filled.env, conclusion), "certificate": certificate,
             "conflict": {"packages": packages}}
    without = copy.deepcopy(inner)
    without["certificate"]["premise_meaning_ids"].pop()
    added = copy.deepcopy(inner)
    added["certificate"]["premise_meaning_ids"].append(_source_meaning(doc.env, ["top"]))
    rows = run(lean, [choice_case(raw, document, [("rs1", 0)], x) for x in (inner, without, added)])
    assert (rows[0]["inner"]["valid"], rows[0]["conflict_free"], rows[0]["accepted"]) == (True, True, True), rows[0]
    for row in rows[1:]:
        assert row["inner"] == {"id": "readings-choice", "status": "error", "error": STALE}
        assert row["accepted"] is False


def test_fsd11_a_certificate_without_conflict_free_packages_is_not_accepted(lean):
    """The soft runner's `conflict_free` is `conflictFreeX` on the case's own packages (spec 4.3, debate F4): a valid
    certificate with packages that bind nothing is not accepted, never CONFLICT-FREE (F-SD8)."""
    raw, document, _ = fsd1(fixed_units=[("u0", ASKS_ALL)])
    conclusion = Forall("agent", Forall("user", Binary("avoid_required", Var(1), Var(0))))
    certificate, _, doc = _choice_certificate(lean, raw, document, [("rs1", 0)], conclusion, [ASKS_ALL])
    inner = {"kind": "norm-defaults-certificate", "premises": [],
             "conclusion": formula_to_data(doc.filled.env, conclusion), "certificate": certificate,
             "conflict": {"packages": {}}}
    row = run(lean, [choice_case(raw, document, [("rs1", 0)], inner)])[0]
    assert (row["inner"]["valid"], row["conflict_free"], row["accepted"]) == (True, False, False)


# `fillHoldsS` through the wire (8.1's NSDq): the witness's `Fill_T` alone decides the pair.

def env_q():
    raw = env_sd(unspecified=())
    predicates = raw["vocabulary"]["predicates"]
    predicates["help_required"]["regulated"].update(default="unspecified", permission="help_permitted")
    predicates["help_permitted"] = {"arguments": ["agent", "user"], "description": "permission",
                                    "regulated": {"role": "permission", "default": "unspecified", "act": "{0} help {1}"}}
    predicates["greet_required"] = {"arguments": ["agent", "user"], "description": "obligation",
                                    "regulated": {"role": "obligation", "default": "deny", "act": "{0} greet {1}"}}
    return raw


def doc_q(raw, permitted):
    base = {"domains": {"agent": ["a"], "user": ["u"]}, "constants": {},
            "relations": {"asks": [], "unsaid__help_permitted": [list(r) for r in permitted],
                          "unsaid__help_required": []}}
    sigma = entry(base, "help", {"outcome": {"predicate": "help_required", "tuple": ["a", "u"]}}, True)
    sid = situation_id(raw, sigma)
    rs = reading_set("rs1", "u1", [reading("help", norm("must-help", "help_required", True), {"greet": sid}),
                                   reading("greet", norm("must-greet", "greet_required", True, "default"),
                                           {"help": sid})], {sid: sigma})
    return {"units": [{"id": "u1"}], "reading_sets": [rs]}, sid


def test_fill_holds_alone_decides_the_pair(lean):
    """8.1 NSDq: the other reading regulates another act, so S1's pair check holds on both bases; with
    `help_permitted` filled the witness's `Fill_T` holds and the pair separates, with it empty it fails: the witness
    is inadmissible and the pair not separated."""
    raw = env_q()
    document, sid = doc_q(raw, [("a", "u")])
    row = one(lean, "readings-validate", raw, document)
    assert row["status"] == "ok", row
    assert [p["label"] for p in row["fill_premises"][0]["premises"]] == ["unsaid:pair:help_required,help_permitted"]
    document, sid = doc_q(raw, [])
    assert one(lean, "readings-validate", raw, document)["error"] == \
        "distinguishing model violates a generated premise"
    separate = one(lean, "readings-separate", raw, document, set="rs1", situation=sid, other="greet")
    assert (separate["pair"]["witness_admissible"], separate["pair"]["separated"]) == (False, False)


# F-SD2 = K1 on generated documents (spec 8.1 F-SD2 and 8.5 F-SD0): with nothing unspecified the profile changes no
# answer of S1's but adds the completion's fields, each empty.

def _rekeyed(document, raw):
    """`document` with each recorded situation under its id in `raw` (the id binds the environment)."""
    out = copy.deepcopy(document)
    for rs in out["reading_sets"]:
        new = {sid: situation_id(raw, entry) for sid, entry in rs.get("situations", {}).items()}
        rs["situations"] = {new[sid]: entry for sid, entry in rs.get("situations", {}).items()}
        for r in rs["readings"]:
            models = r.get("admission", {}).get("distinguishing_models", {})
            r["admission"]["distinguishing_models"] = {o: new.get(m, m) for o, m in models.items()}
    return out


def test_fsd2_generated_documents_answer_as_without_the_profile(lean):
    import random
    from tests.test_readings_s1_differential import SEARCH_FAILURES, twins
    from ve.readings_s1 import record_situations, search
    rng = random.Random(20261012)
    compared = 0
    for _ in range(40):
        raw, document, _ = twins(random.Random(rng.random()))
        rs = document["reading_sets"][0]
        try:
            found = search(raw, document, rs["id"])
        except SEARCH_FAILURES:
            continue
        if not found or any(v is None for v in found.values()):
            continue
        document["reading_sets"][0] = record_situations(rs, found)
        nd_raw = {**raw, "profiles": sorted({*raw["profiles"], "norm-defaults@0"})}
        nd_document = _rekeyed(document, nd_raw)
        plain, nd = run(lean, [case("readings-validate", raw, document), case("readings-validate", nd_raw,
                                                                              nd_document)])
        assert plain["status"] == nd["status"], (plain, nd)
        if plain["status"] == "error":
            continue
        for p_set, n_set in zip(plain["sets"], nd["sets"]):
            assert p_set["findings"] == n_set["findings"]
            assert [{k: v for k, v in c.items() if k != "document_hash"} for c in p_set["candidates"]] == \
                [{k: v for k, v in c.items() if k != "document_hash"} for c in n_set["candidates"]]
            for p_pair, n_pair in zip(p_set["pairs"], n_set["pairs"]):
                facts = dict(n_pair["pair"])
                assert facts.pop("gaps") == []
                assert {**facts, "situation": None} == {**p_pair["pair"], "situation": None}
        # nothing unspecified: no `Fill_T`; soft's premises are the readings' own (an exception condition, a pair)
        assert all(e["premises"] == [] for e in nd["fill_premises"])
        compared += 1
    assert compared >= 10, compared


# SC-5: `readings-verdicts` under the soft completion (spec 4.4, 8.3 F-SD1.verdicts and F-SD2's verdicts).

AVOID_ALL = Forall("agent", Forall("user", Binary("avoid_required", Var(1), Var(0))))
TWINS = (norm("no-deception", "avoid_required", True), norm("no-deception", "avoid_required", True, "default"))
# A model of each choice's premises: the default choice's base declares its decision table.
FREE_MODELS = ({"model": layered_model(), "filling": {}},
               {"model": layered_model({"soft__excepted__no_deception": []}), "filling": {}})


def _bindings(lean, raw, document, choice):
    return run(lean, [choice_case(raw, document, choice, {"kind": "norm-defaults-elaborate"})])[0]["inner"]


def _packages(lean, raw, document, choice, *sources):
    """The choice's conflict packages, proposed by the pinned oracle on its source and bound to Lean's ids."""
    row = _bindings(lean, raw, document, choice)
    doc = layered.document("soft", lower(raw), list(sources))
    report = layered.nd.check_conflict(doc, prove=True)
    return {t: {**p, "environment_id": row["environment_id"], "document_hash": row["document_hash"]}
            for t, p in report.certificates.items()}


def _twin_evidence(lean, raw, document, *, query=False, models=True):
    """F-SD1's evidence: each choice's packages; for the query a certificate of the strict choice and a countermodel
    of the default one (`excepted = {(a, u)}`, the filling no); a model of each choice's premises."""
    evidence = []
    for i, source in enumerate(TWINS):
        piece = {"choice": [["rs1", i]], "conflict": {"packages": _packages(lean, raw, document, [("rs1", i)], source)}}
        if models:
            piece["model"] = FREE_MODELS[i]
        evidence.append(piece)
    if query:
        certificate, _, _ = _choice_certificate(lean, raw, document, [("rs1", 0)], AVOID_ALL, [])
        evidence[0]["certificate"] = {"certificate": certificate}
        evidence[1]["countermodel"] = {"model": layered_model({"soft__excepted__no_deception": [["a", "u"]]}),
                                       "filling": {}}
    return evidence


def _verdicts(lean, raw, document, question, evidence, **fields):
    return one(lean, "readings-verdicts", raw, document, question=question, evidence=evidence, **fields)


def _query(raw):
    doc = layered.document("soft", lower(raw), [TWINS[0]])
    return formula_to_data(doc.filled.env, AVOID_ALL)


def test_fsd1_verdicts_conflict_free_with_decided_units(lean):
    """8.3 F-SD1.verdicts: CONFLICT-FREE under both readings, each row decided, so `decided_units` is the set's unit
    (1.12); under `--under rs1:0` the rows cover one choice, so none."""
    raw, document, _ = fsd1()
    evidence = _twin_evidence(lean, raw, document)
    answer = _verdicts(lean, raw, document, "conflict", evidence)
    assert answer["status"] == "ok", answer
    assert answer["result"]["status"] == "CONFLICT-FREE", answer["result"]
    assert [(e["choice"], e["conflict"]) for e in answer["per_choice"]] == [
        ([["rs1", 0]], "CONFLICT-FREE"), ([["rs1", 1]], "CONFLICT-FREE")]
    assert answer["finding_sets"] == ["rs1"] and answer["decided_units"] == ["u1"]
    under = _verdicts(lean, raw, document, "conflict", evidence, assumed=[["rs1", 0]])
    assert under["result"]["status"] == "CONFLICT-FREE" and under["decided_units"] == []
    premises = _verdicts(lean, raw, document, "premises", evidence)
    assert premises["result"]["status"] == "model" and premises["decided_units"] == ["u1"]


def test_fsd1_verdicts_query_some_all_none(lean):
    """8.3 F-SD1.verdicts: the query `∀ agent ∀ user. avoid_required` is SOME (choice 0 proved, choice 1 refuted by
    `excepted = {(a, u)}` and the filling no); ALL under `rs1:0`; NONE under `rs1:1`."""
    raw, document, _ = fsd1()
    evidence = _twin_evidence(lean, raw, document, query=True)
    fields = {"premises": [], "conclusion": _query(raw)}
    some = _verdicts(lean, raw, document, "query", evidence, **fields)
    assert some["status"] == "ok", some
    assert some["result"]["verdict"] == "SOME", some["result"]
    assert [e["query"] for e in some["per_choice"]] == ["proved", "refuted"]
    assert some["result"]["proof"]["choice"] == [["rs1", 0]]
    assert some["result"]["countermodel"]["choice"] == [["rs1", 1]]
    assert some["decided_units"] == ["u1"]
    every = _verdicts(lean, raw, document, "query", evidence, assumed=[["rs1", 0]], **fields)
    assert every["result"]["verdict"] == "ALL" and every["decided_units"] == []
    none = _verdicts(lean, raw, document, "query", evidence, assumed=[["rs1", 1]], **fields)
    assert none["result"]["verdict"] == "NONE" and none["decided_units"] == []


def test_fsd2_verdicts_take_the_enumerated_route(lean):
    """8.3 F-SD2, `readings-verdicts`: K18 answers RD-3's request on its two choices, not K1's superposed answer:
    CONFLICT-FREE; the query SOME, ALL under `rs1:0`, NONE under `rs1:1`; `decided_units` as F-SD1's."""
    raw = env_sd(unspecified=())
    document, _ = k1_document(raw)
    evidence = _twin_evidence(lean, raw, document, query=True)
    conflict = _verdicts(lean, raw, document, "conflict", evidence)
    assert (conflict["route"], conflict["result"]["status"], conflict["decided_units"]) == (
        "enumerated", "CONFLICT-FREE", ["u1"]), conflict
    fields = {"premises": [], "conclusion": _query(raw)}
    assert _verdicts(lean, raw, document, "query", evidence, **fields)["result"]["verdict"] == "SOME"
    assert _verdicts(lean, raw, document, "query", evidence, assumed=[["rs1", 0]], **fields)["result"]["verdict"] \
        == "ALL"
    assert _verdicts(lean, raw, document, "query", evidence, assumed=[["rs1", 1]], **fields)["result"]["verdict"] \
        == "NONE"


def test_fsd4_a_conflict_free_answer_rests_on_the_coherence_premise(lean):
    """8.3 F-SD4: `coherent` beside its strict twin (here with `x_permitted` allowed, so the packages close). Under
    the default reading the CONFLICT-FREE answer is `conditional_on` the coherence premise its packages use, and the
    plan cites it after E3; under the strict reading nothing."""
    raw = env4()
    raw["vocabulary"]["predicates"]["x_permitted"]["regulated"]["default"] = "allow"
    document = doc4(raw)
    need_not, units = document["units"][0]["content"], document["reading_sets"][0]["readings"]
    evidence = [{"choice": [["rs1", i]], "conflict": {"packages": _packages(
        lean, raw, document, [("rs1", i)], need_not, units[i]["content"])}} for i in (0, 1)]
    label = "soft:coherence:must-x,need-not-x"
    default = _verdicts(lean, raw, document, "conflict", evidence, assumed=[["rs1", 1]])
    assert default["result"]["status"] == "CONFLICT-FREE", default
    assert default["result"]["conditional_on"] == [label] and default["labels"] == [label]
    assert [line["label"] for line in default["english"] if line["label"]] == [label]
    strict = _verdicts(lean, raw, document, "conflict", evidence, assumed=[["rs1", 0]])
    assert strict["result"]["status"] == "CONFLICT-FREE" and strict["result"]["conditional_on"] == []


def test_fsd8_evidence_for_another_choice_is_never_a_verdict(lean):
    """8.3 F-SD8 in `readings-verdicts`: the strict choice's packages and certificate supplied as the default choice's
    are refused there: its rows are UNKNOWN, so the answer is neither CONFLICT-FREE nor ALL."""
    raw, document, _ = fsd1()
    evidence = _twin_evidence(lean, raw, document, query=True)
    evidence[1]["conflict"] = copy.deepcopy(evidence[0]["conflict"])
    evidence[1]["certificate"] = copy.deepcopy(evidence[0]["certificate"])
    del evidence[1]["countermodel"]
    conflict = _verdicts(lean, raw, document, "conflict", evidence)
    assert conflict["result"]["status"] == "UNKNOWN", conflict["result"]
    assert [e["conflict"] for e in conflict["per_choice"]] == ["CONFLICT-FREE", "UNKNOWN"]
    under = _verdicts(lean, raw, document, "query", evidence, assumed=[["rs1", 1]], premises=[],
                      conclusion=_query(raw))
    assert under["result"]["verdict"] == "UNKNOWN", under["result"]
    assert [e["query"] for e in under["per_choice"]] == ["UNKNOWN"]
    assert under["per_choice"][0]["errors"]["certificate"] == STALE


def test_fsd9_verdicts_beyond_64_choices(lean):
    """8.3 F-SD9: seven sets, 128 choices: the query is W2's budget answer (UNKNOWN) and `decided_units` is `[]`."""
    raw = env_sd()
    sets, units = [], []
    for k in range(7):
        rule = f"no-deception-{k}"
        sets.append(reading_set(f"rs{k}", f"u{k}", [reading("strict", norm(rule, "avoid_required", True), {}),
                                                    reading("default", norm(rule, "avoid_required", True, "default"),
                                                            {})], {}))
        units.append({"id": f"u{k}"})
    document = {"units": units, "reading_sets": sets}
    answer = _verdicts(lean, raw, document, "query", [], premises=[], conclusion=_query(raw))
    assert answer["status"] == "ok", answer
    assert answer["result"]["verdict"] == "UNKNOWN" and answer["result"]["budget"] == {"max_choices": 64}
    assert answer["decided_units"] == [] and answer["per_choice"] == []
    conflict = _verdicts(lean, raw, document, "conflict", [])
    assert conflict["result"]["status_text"] == "UNKNOWN: more than 64 compatible readings"


def test_fsd11_a_verdict_certificate_binds_the_assertions_it_takes(lean):
    """8.3 F-SD11 in `readings-verdicts`: with a fixed assertion unit, the strict choice's certificate is accepted
    (ALL under `rs1:0`); with its binding leaving the assertion out, the piece is refused and the row UNKNOWN."""
    raw, document, _ = fsd1(fixed_units=[("u0", ASKS_ALL)])
    certificate, packages, doc = _choice_certificate(lean, raw, document, [("rs1", 0)], AVOID_ALL, [ASKS_ALL])
    fields = {"premises": [], "conclusion": formula_to_data(doc.filled.env, AVOID_ALL), "assumed": [["rs1", 0]]}
    evidence = [{"choice": [["rs1", 0]], "conflict": {"packages": packages}, "certificate": {"certificate": certificate}}]
    every = _verdicts(lean, raw, document, "query", evidence, **fields)
    assert every["result"]["verdict"] == "ALL", every
    without = copy.deepcopy(evidence)
    without[0]["certificate"]["certificate"]["premise_meaning_ids"].pop()
    answer = _verdicts(lean, raw, document, "query", without, **fields)
    assert answer["result"]["verdict"] == "UNKNOWN"
    assert answer["per_choice"][0]["query"] == "UNKNOWN"
    assert answer["per_choice"][0]["errors"] == {"certificate": STALE}
