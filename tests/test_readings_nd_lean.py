"""Readings under the unspecified completion through the Lean service (docs/spec/readings-defaults.md 8.3; plan RD-2a).

A document is under the completion when `readings@1` and `norm-defaults@0` are on the norms chain and a set is
content-bearing. Lean admits it (4.1: S1's admission, reserved `unsaid--` names, norm-defaults' author checks on the
free document and each reading's, S1's checks of the filled document, each compatible choice), separates its readings
on one base and one shared filling (4.2) and checks each choice's evidence on the regenerated filled document (4.3).
Python decides nothing here: certificates and witnesses are proposed by the pinned pre-switch norm-defaults oracle
(`conformance.frozen_norm_defaults`, test tooling only) and Lean replays them; every expected value is the spec's,
written out.
"""
from __future__ import annotations

import copy

import pytest

from conformance import frozen_norm_defaults as oracle
from tests import lean_routes
from tests.test_readings_s1_lean import entry, env_k, env_rights, k1_document, norm, norm_object, reading, \
    reading_set, run, situation_id
from ve import norm_defaults as nd
from ve import norm_defaults_route as nd_route
from ve.ast import Binary, Forall, Top, Unary, Var, formula_to_data
from ve.environment import Environment
from ve.norms import Norm
from ve.profiles import LANGUAGE, SPEC_REVISION

LEAN = "ve_readings_route"
ND = ("norm-defaults@0", "norms@0", "readings@1", "relational-fol@0")
PLAIN = ("norms@0", "readings@1", "relational-fol@0")
GENERATED = "distinguishing model violates a generated premise"


@pytest.fixture(scope="module")
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    return LEAN


def regulated(role, completion, act, **extra):
    return {"role": role, "default": completion, "act": act, **extra}


def environment(predicates, sorts, profiles=ND):
    return {"language": LANGUAGE, "profiles": sorted(profiles), "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {s: {"description": s} for s in sorts}, "constants": {},
                           "predicates": predicates}}


def lower(raw):
    """The environment without `readings@1`: the norm-defaults route's source environment."""
    out = copy.deepcopy(raw)
    out["profiles"] = [p for p in out["profiles"] if p != "readings@1"]
    return out


def case(kind, raw, document, **fields):
    return {"id": kind, "kind": kind, "environment": raw, "document": document, **fields}


def one(lean, kind, raw, document, **fields):
    return run(lean, [case(kind, raw, document, **fields)])[0]


# F-ND1: "every agent must help each user" against "... each user who asks".

def env1(profiles=ND, completion="unspecified"):
    return environment({
        "asks": {"arguments": ["user", "agent"], "description": "{0} asks {1}"},
        "help_required": {"arguments": ["agent", "user"], "description": "obligation",
                          "regulated": regulated("obligation", completion, "{0} help {1}",
                                                 permission="help_permitted")},
        "help_permitted": {"arguments": ["agent", "user"], "description": "permission",
                           "regulated": regulated("permission", completion, "{0} help {1}")}},
        ("agent", "user"), profiles)


ASKS = ("binary", "asks", ["var", 0], ["var", 1])
PROBE1 = {"outcome": {"predicate": "help_required", "tuple": ["a", "u"]}}


def base1(permitted, required=()):
    return {"domains": {"agent": ["a"], "user": ["u"]}, "constants": {},
            "relations": {"asks": [], "unsaid__help_permitted": [list(r) for r in permitted],
                          "unsaid__help_required": [list(r) for r in required]}}


def doc1(raw, sigma=None, set_id="rs_1", unit="u1", rule="must-help"):
    sigma = sigma or entry(base1([["a", "u"]]), "every", PROBE1, True)
    sid = situation_id(raw, sigma)
    rs = reading_set(set_id, unit, [
        reading("every", norm(rule, "help_required", True), {"asks": sid}),
        reading("asks", norm(rule, "help_required", True, guard=ASKS), {"every": sid})], {sid: sigma})
    return {"units": [{"id": unit}], "reading_sets": [rs]}, sid


def test_fnd1_validate_separates_on_the_filled_document(lean):
    raw = env1()
    document, sid = doc1(raw)
    row = one(lean, "readings-validate", raw, document)
    assert row["status"] == "ok", row
    [rs1] = row["sets"]
    assert rs1["pairs"][0] == {"reading": "every", "other": "asks", "pair": {
        "situation": sid, "witness": "every", "separated": True, "witness_admissible": True, "witness_value": True,
        "other_admissible": True, "other_value": False}}
    assert [c["owned"] for c in rs1["candidates"]] == [[], []]
    # per reading its `Fill_T`, labelled by the pair
    assert [(e["set"], e["index"], [p["label"] for p in e["premises"]]) for e in row["fill_premises"]] == [
        ("rs_1", 0, ["unsaid:pair:help_required,help_permitted"]),
        ("rs_1", 1, ["unsaid:pair:help_required,help_permitted"])]
    filled = row["filled"]
    assert filled["environment"]["profiles"] == ["norms@0", "relational-fol@0"]
    predicates = filled["environment"]["vocabulary"]["predicates"]
    assert predicates["unsaid__help_required"]["arguments"] == ["agent", "user"]
    assert predicates["help_required"]["regulated"]["default"] == "deny"
    # the `F_p` units last, in the frame's regulated order (the decoder's, by name)
    assert [u["unit"] for u in filled["units"]] == ["u1", "u1", "unsaid--help-permitted", "unsaid--help-required"]
    assert [u["content"]["norm"]["over"] for u in filled["units"][:2]] == [["unsaid--help-required"]] * 2


def test_fnd1_separate_and_elaborate(lean):
    raw = env1()
    document, sid = doc1(raw)
    separate = one(lean, "readings-separate", raw, document, set="rs_1", situation=sid, other="asks")
    assert separate["pair"]["separated"] is True and separate["pair"]["witness_admissible"] is True
    elaborate = one(lean, "readings-elaborate", raw, document)
    assert {k: elaborate[k] for k in ("route", "finding", "choice_count", "choices", "choices_checked")} == {
        "route": "enumerated",
        "finding": {"text": "ReadingsNotSuperposable: rs_1", "cause": "the unspecified completion"},
        "choice_count": 2, "choices": [[["rs_1", 0]], [["rs_1", 1]]], "choices_checked": 2}


def test_fnd1_prime_the_witness_filling_must_satisfy_its_fill_premises(lean):
    """F-ND1′: with `help_permitted` filled 'no' where reading 0's duty holds, its `Fill_T` fails."""
    raw = env1()
    sigma = entry(base1([]), "every", PROBE1, True)
    document, sid = doc1(raw, sigma)
    assert one(lean, "readings-validate", raw, document)["error"] == GENERATED
    separate = one(lean, "readings-separate", raw, document, set="rs_1", situation=sid, other="asks")
    assert separate["pair"]["witness_admissible"] is False


def test_fnd1_the_other_way_and_not_separated(lean):
    """8.1 rows 1.7 and 1.8 through the wire: witness `asks` with value false separates; with value true not."""
    raw = env1()
    document, _ = doc1(raw, entry(base1([["a", "u"]]), "asks", PROBE1, False))
    assert one(lean, "readings-validate", raw, document)["status"] == "ok"
    document, _ = doc1(raw, entry(base1([["a", "u"]]), "asks", PROBE1, True))
    assert one(lean, "readings-validate", raw, document)["error"] == "distinguishing model does not separate readings"


def test_superposed_kinds_wait_for_rd6_and_dead_is_answered(lean):
    raw = env1()
    document, _ = doc1(raw)
    refusal = "ReadingsNotSuperposable: rs_1 (the unspecified completion); use readings-choice"
    for kind in ("readings-conflict", "readings-certificate", "readings-model"):
        assert one(lean, kind, raw, document, assumed=[])["error"] == refusal
    # `readings-dead` reads the couplings and narrowings only: it is answered (here its certificate is refused)
    dead = one(lean, "readings-dead", raw, document, set="rs_1", index=0, certificate={})
    assert dead["status"] == "error" and not dead["error"].startswith("ReadingsNotSuperposable")


# Choices: evidence produced by Python's norm-defaults prover and search, replayed by Lean on `choiceU N c`.

def choice_case(raw, document, choice, inner):
    return case("readings-choice", raw, document, choice=[list(x) for x in choice], inner=inner)


def bindings(lean, raw, document, choice):
    row = run(lean, [choice_case(raw, document, choice, {"kind": "norm-defaults-elaborate"})])[0]
    inner = row["inner"]
    assert inner["status"] == "ok", inner
    return {"environment_id": inner["environment_id"], "document_hash": inner["document_hash"]}, row


def python_document(raw, rules):
    return nd.UnspecifiedDocument(Environment(lower(raw)), rules)


def proposed_conflict(raw, rules, **options):
    """Conflict evidence proposed by the pinned pre-switch oracle (as main's norm-defaults tests propose it); Lean
    replays every package and witness on the choice's own document."""
    return oracle.check_conflict(oracle.UnspecifiedDocument(Environment(lower(raw)), rules), **options)


def packages(lean, raw, document, choice, rules):
    bound, _ = bindings(lean, raw, document, choice)
    report = proposed_conflict(raw, rules, prove=True)
    assert report.status == "CONFLICT-FREE"
    return {target: {**package, **bound} for target, package in report.certificates.items()}


EVERY = [Norm("must-help", "help_required", True, Top(), (), ())]
ASKING = [Norm("must-help", "help_required", True, Binary("asks", Var(0), Var(1)), (), ())]


def test_fnd1_each_choice_conflict_free_and_certificate(lean):
    raw = env1()
    document, _ = doc1(raw)
    # each choice's packages are bound to that choice's own document: the hash Lean reports is the norm-defaults
    # route's hash of the choice's units, computed here independently (checklist 15: identity)
    for choice, rules in (([("rs_1", 0)], EVERY), ([("rs_1", 1)], ASKING)):
        bound, row = bindings(lean, raw, document, choice)
        expected = python_document(raw, rules)
        assert bound == {"environment_id": expected.env.environment_id, "document_hash": expected.document_hash}
        assert row["document_hash"] == expected.document_hash
    rows = run(lean, [choice_case(raw, document, [("rs_1", 0)], {
                          "kind": "norm-defaults-conflict", "packages": packages(lean, raw, document, [("rs_1", 0)], EVERY)}),
                      choice_case(raw, document, [("rs_1", 1)], {
                          "kind": "norm-defaults-conflict", "packages": packages(lean, raw, document, [("rs_1", 1)], ASKING)})])
    assert [r["inner"]["verdict"] for r in rows] == ["CONFLICT-FREE", "CONFLICT-FREE"]
    assert rows[0]["inner"]["targets"] == ["help_permitted", "help_required", "help_required->help_permitted"]
    # a certificate of the query under reading `every`, accepted with the choice's conflict packages
    pydoc = python_document(raw, EVERY)
    env = pydoc.filled.env
    conclusion = Forall("agent", Forall("user", Binary("help_required", Var(1), Var(0))))
    certificate = nd_route.prove_filled_entailment(pydoc, (), conclusion)
    inner = {"kind": "norm-defaults-certificate", "premises": [], "conclusion": formula_to_data(env, conclusion),
             "certificate": certificate,
             "conflict": {"packages": packages(lean, raw, document, [("rs_1", 0)], EVERY)}}
    row = run(lean, [choice_case(raw, document, [("rs_1", 0)], inner)])[0]
    assert (row["inner"]["valid"], row["conflict_free"], row["accepted"]) == (True, True, True)
    # F-ND8: the same certificate is no evidence for the other choice
    row = run(lean, [choice_case(raw, document, [("rs_1", 1)], {
        **inner, "conflict": {"packages": packages(lean, raw, document, [("rs_1", 1)], ASKING)}})])[0]
    assert row["accepted"] is False


def test_fnd8_a_package_bound_to_choice_0_is_no_evidence_for_choice_1(lean):
    raw = env1()
    document, _ = doc1(raw)
    stolen = packages(lean, raw, document, [("rs_1", 0)], EVERY)
    row = run(lean, [choice_case(raw, document, [("rs_1", 1)], {"kind": "norm-defaults-conflict",
                                                                 "packages": stolen})])[0]
    assert row["inner"]["verdict"] == "UNKNOWN"
    assert row["inner"]["detail"].startswith("missing certificate for ")


def test_fnd8_fillings_and_unsaid_tables_are_checked(lean):
    raw = env1()
    document, _ = doc1(raw)
    model = {"complete": True, "domains": {"agent": ["a"], "user": ["u"]}, "constants": {}, "relations": {"asks": []}}
    # an ill-typed filling tuple (user, agent) is refused, never a CONFLICT
    witness = {"target": "help_required->help_permitted", "model": model,
               "filling": {"unsaid__help_permitted": [["u", "a"]]}, "tuple": ["a", "u"]}
    row = run(lean, [choice_case(raw, document, [("rs_1", 0)], {"kind": "norm-defaults-conflict",
                                                                 "witness": witness})])[0]
    assert row["inner"]["status"] == "error" and "CONFLICT" not in row["inner"].get("verdict", "")
    # an `unsaid__` table in the base model is a filling, never a table
    tabled = copy.deepcopy(model)
    tabled["relations"]["unsaid__help_permitted"] = [["a", "u"]]
    row = run(lean, [choice_case(raw, document, [("rs_1", 0)], {"kind": "choice-model", "model": tabled,
                                                                 "filling": {}})])[0]
    assert row["inner"]["error"].startswith("InvalidModel(norm-defaults): unsaid__help_permitted is a filling")
    # and outside the profile it is no predicate of the author's base vocabulary
    plain = env1(PLAIN, "deny")
    document, _ = doc1(plain, entry(base1([["a", "u"]]), "every", PROBE1, True))
    assert one(lean, "readings-validate", plain, document)["error"].startswith("InvalidInput: invalid situation")


def test_choice_model_with_a_separate_filling(lean):
    """`modelCheckU`: under reading `asks`, nobody asks, the gap filled 'no': the query fails there."""
    raw = env1()
    document, _ = doc1(raw)
    model = {"complete": True, "domains": {"agent": ["a"], "user": ["u"]}, "constants": {}, "relations": {"asks": []}}
    query = ["forall", "agent", ["forall", "user", ["binary", "help_required", ["var", 1], ["var", 0]]]]
    rows = run(lean, [choice_case(raw, document, [("rs_1", 1)], {"kind": "choice-model", "model": model,
                                                                  "filling": {}, "conclusion": query}),
                      choice_case(raw, document, [("rs_1", 0)], {"kind": "choice-model", "model": model,
                                                                  "filling": {}, "conclusion": query})])
    assert [(r["inner"]["valid"], r["inner"]["conclusion_value"]) for r in rows] == [(True, False), (False, True)]


# F-ND2: norm-defaults' u6 as readings: a latent conflict under one reading.

def env2(profiles=ND):
    one_place = ["act"]
    return environment({
        "x_required": {"arguments": one_place, "description": "obligation",
                       "regulated": regulated("obligation", "unspecified", "{0} be done", permission="x_permitted")},
        "x_permitted": {"arguments": one_place, "description": "permission",
                        "regulated": regulated("permission", "unspecified", "{0} be done")},
        "y_permitted": {"arguments": one_place, "description": "permission",
                        "regulated": regulated("permission", "unspecified", "{0} be tried")}}, ("act",), profiles)


def doc2(raw):
    sigma = entry({"domains": {"act": ["a"]}, "constants": {}, "relations": {
        "unsaid__x_permitted": [], "unsaid__x_required": [], "unsaid__y_permitted": []}},
        "may-y", {"outcome": {"predicate": "y_permitted", "tuple": ["a"]}}, True)
    sid = situation_id(raw, sigma)
    rs = reading_set("rs_2", "u2", [
        reading("must-x", norm("must-x", "x_required", True, guard=("unary", "y_permitted", ["var", 0])),
                {"may-y": sid}),
        reading("may-y", norm("may-y", "y_permitted", True), {"must-x": sid})], {sid: sigma})
    units = [{"id": "u0", "kind": "norm", "content": norm("no-x", "x_permitted", False)}, {"id": "u2"}]
    return {"units": units, "reading_sets": [rs]}, sid


def test_fnd2_latent_conflict_under_one_reading(lean):
    raw = env2()
    document, sid = doc2(raw)
    row = one(lean, "readings-validate", raw, document)
    assert row["status"] == "ok", row
    assert row["sets"][0]["pairs"][0]["pair"]["witness"] == "may-y"
    assert row["sets"][0]["pairs"][0]["pair"]["separated"] is True
    no_x = Norm("no-x", "x_permitted", False, Top(), (), ())
    must_x = Norm("must-x", "x_required", True, Unary("y_permitted", Var(0)), (), ())
    may_y = Norm("may-y", "y_permitted", True, Top(), (), ())
    act = {"complete": True, "domains": {"act": ["a"]}, "constants": {}, "relations": {}}
    report = proposed_conflict(raw, [no_x, must_x], model=act)
    assert (report.status, report.target) == ("CONFLICT", "x_required->x_permitted")
    witness = {"target": report.target, "model": act,
               "filling": {name: [list(r) for r in rows] for name, rows in report.filling.items()},
               "tuple": list(report.tuple)}
    status = {"kind": "norm-defaults-status", "model": witness["model"], "predicate": "x_required", "tuple": ["a"],
              "method": "table3"}
    rows = run(lean, [
        choice_case(raw, document, [("rs_2", 0)], {"kind": "norm-defaults-conflict", "witness": witness}),
        choice_case(raw, document, [("rs_2", 1)], {"kind": "norm-defaults-conflict",
                                                   "packages": packages(lean, raw, document, [("rs_2", 1)],
                                                                        [no_x, may_y])}),
        choice_case(raw, document, [("rs_2", 1)], status)])
    assert [r["inner"].get("verdict") for r in rows[:2]] == ["CONFLICT", "CONFLICT-FREE"]
    assert rows[0]["inner"]["target"] == "x_required->x_permitted"
    assert rows[2]["inner"]["point_status"] == "SETTLED no"
    # the same witness under the other reading: no rule makes x required there, so no conflict
    row = run(lean, [choice_case(raw, document, [("rs_2", 1)], {"kind": "norm-defaults-conflict",
                                                                 "witness": witness})])[0]
    assert row["inner"].get("verdict") != "CONFLICT"


def test_inner_answers_are_the_norm_defaults_routes(lean):
    """Review B1's class: a choice's inner case is answered by the norm-defaults route's own dispatch
    (`layeredCase`), so each answer equals that route's on the choice's document, field for field. A copied dispatch
    dropped the fields main added (the CONFLICT row's `kind`, `rules`, `tuple` and `under`; the status row's)."""
    raw = env2()
    document, _ = doc2(raw)
    no_x = Norm("no-x", "x_permitted", False, Top(), (), ())
    must_x = Norm("must-x", "x_required", True, Unary("y_permitted", Var(0)), (), ())
    may_y = Norm("may-y", "y_permitted", True, Top(), (), ())
    act = {"complete": True, "domains": {"act": ["a"]}, "constants": {}, "relations": {}}
    report = proposed_conflict(raw, [no_x, must_x], model=act)
    filling = {f"unsaid__{p}": [] for p in ("x_permitted", "x_required", "y_permitted")}
    filling.update({name: [list(r) for r in rows] for name, rows in report.filling.items()})
    every = {name: [["a"]] for name in filling}
    status = {"kind": "norm-defaults-status", "model": act, "predicate": "x_required", "tuple": ["a"]}
    checked = 0
    for choice, rules in (([("rs_2", 0)], [no_x, must_x]), ([("rs_2", 1)], [no_x, may_y])):
        pydoc = python_document(raw, rules)
        # (the inner case, the same case as the norm-defaults route reads it: there a witness's filling is in its model)
        pairs = [
            ({"kind": "norm-defaults-conflict", "witness": {"target": report.target, "model": act,
                                                            "filling": filling, "tuple": list(report.tuple)}},
             {"kind": "norm-defaults-conflict", "witness": {"target": report.target, "tuple": list(report.tuple),
                                                            "model": {**act, "relations": filling}}}),
            ({"kind": "norm-defaults-conflict", "packages": {}}, None),
            ({**status, "method": "table3"}, None),
            ({**status, "method": "enumerate"}, None),
            ({**status, "predicate": "y_permitted", "method": "undecided", "yes": every, "no": {}}, None),
            ({"kind": "norm-defaults-report", "model": act}, None)]
        if choice == [("rs_2", 1)]:  # CONFLICT-FREE (reading 0 has the latent conflict)
            pairs.append(({"kind": "norm-defaults-conflict",
                           "packages": packages(lean, raw, document, choice, rules)}, None))
        rows = run(lean, [choice_case(raw, document, choice, inner) for inner, _ in pairs])
        for (inner, direct), row in zip(pairs, rows):
            direct = direct or inner
            expected = nd_route.run_case(nd_route.source_case(
                pydoc, direct["kind"], **{k: v for k, v in direct.items() if k != "kind"}))
            got = row["inner"]
            assert got["status"] == "ok", (inner, got)
            assert {k: v for k, v in got.items() if k != "id"} == {k: v for k, v in expected.items() if k != "id"}, \
                inner
            checked += 1
    assert checked == 13


# Limits and admission's order (4.1, section 5).

def env4(profiles=ND):
    two = ["agent", "user"]
    preds = {}
    for p in ("p", "q"):
        preds[f"{p}_required"] = {"arguments": two, "description": "obligation", "regulated": regulated(
            "obligation", "unspecified", "{0} " + p + " {1}", permission=f"{p}_permitted")}
        preds[f"{p}_permitted"] = {"arguments": two, "description": "permission",
                                   "regulated": regulated("permission", "unspecified", "{0} " + p + " {1}")}
    return environment(preds, ("agent", "user"), profiles)


def chain_document(k):
    """`k` fixed rules on `p_required`, each over the one before, and one reading over the last: precedence height
    `k` in the free document and `k + 1` in the reading's."""
    units = [{"id": f"f{i}", "kind": "norm",
              "content": norm(f"r{i}", "p_required", True, over=((f"r{i - 1}",) if i else ()))} for i in range(k)]
    units.append({"id": "u1"})
    return {"units": units, "reading_sets": [reading_set("rs_1", "u1", [
        reading("top", norm("more", "p_required", True, over=(f"r{k - 1}",)), {})], {})]}


def test_fnd4_a_readings_document_beyond_an_author_limit(lean):
    """4.1 step 3 per reading, with `checkAuthorN`'s precedence limit (height 15 on an unspecified predicate). The
    spec's F-ND4 (252 rules on one predicate) is not reachable on the wire: one predicate's generated layer passes the
    depth limit at about 52 rules, and S1's admission of 250 fixed units exceeds the service's CPU deadline (both
    measured, docs/readings-defaults/rd2a/DELTA.md); the rule limit itself is pinned by `UnspecifiedExamples.lean`."""
    raw = env4()
    rows = run(lean, [case("readings-validate", raw, chain_document(k)) for k in (14, 15, 17)])
    assert [r.get("error", r["status"]) for r in rows] == [
        "ok", "ResourceLimit: precedence depth under rs_1@1:0", "ResourceLimit: precedence depth"]
    # S1 alone has no such limit: the same document with the completions `deny` and no profile is admitted
    plain = env4(PLAIN)
    for entry_ in plain["vocabulary"]["predicates"].values():
        entry_["regulated"]["default"] = "deny"
    assert one(lean, "readings-validate", plain, chain_document(15))["status"] == "ok"


def test_fnd5_reserved_names_before_any_document_check(lean):
    raw = env1()
    document = {"units": [{"id": "u0", "kind": "norm", "content": norm("be-helpful", "help_required", True)},
                          {"id": "u1"}],
                "reading_sets": [reading_set("rs_1", "u1", [
                    reading("named", norm("unsaid--help-required", "help_permitted", True), {})], {})]}
    assert one(lean, "readings-validate", raw, document)["error"] == \
        "InvalidInput: reserved name unsaid--help-required"
    document["units"][0]["id"] = "unsaid--u0"
    document["reading_sets"][0]["readings"][0]["content"] = norm("named", "help_permitted", True)
    assert one(lean, "readings-validate", raw, document)["error"] == "InvalidInput: reserved name unsaid--u0"


def nested(k):
    guard = list(ASKS)
    for _ in range(k):
        guard = ["not", guard]
    return guard


def deep_document(k):
    return {"units": [{"id": "u1"}], "reading_sets": [reading_set("rs_1", "u1", [
        reading("deep", norm("must-help", "help_required", True, guard=tuple(nested(k))), {})], {})]}


def test_fnd9_a_generated_layer_of_the_filled_tree(lean):
    """Depth 52 passes S1's checks on the author's document (the completion off) and fails on the filled tree's
    generated layer (4.1 step 4); depth 56 fails both; depth 50 passes both (sizes found by this test's search)."""
    text = "ResourceLimit: generated norm layer layer:norms:help_required under rs_1@1:0"
    plain = env1(PLAIN, "deny")
    rows = run(lean, [case("readings-validate", raw, deep_document(k))
                      for k in (50, 52, 56) for raw in (env1(), plain)])
    assert [r.get("error", r["status"]) for r in rows] == ["ok", "ok", text, "ok", text, text]


def test_fnd3_over_64_choices(lean):
    raw = env1()
    sets, units = [], []
    for k in range(7):
        document, _ = doc1(raw, set_id=f"rs_{k + 1}", unit=f"u{k + 1}", rule=f"must-help-{k + 1}")
        sets += document["reading_sets"]
        units += document["units"]
    row = one(lean, "readings-elaborate", raw, {"units": units, "reading_sets": sets})
    assert (row["route"], row["choice_count"], row["choices"], row["choices_checked"]) == \
        ("enumerated", "over 64", "over", "over 64")


# Conservativity (4.6, SR5): outside the completion nothing changes.

def test_fnd6_soft_chain_keeps_the_abstention(lean):
    raw = env_k(profiles=("norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"))
    document, _ = k1_document(raw)
    for kind in ("readings-validate", "readings-elaborate", "readings-choice"):
        row = one(lean, kind, raw, document, choice=[["rs1", 0]], inner={"kind": "soft-conflict"})
        assert row["error"] == "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented"


def test_fnd6_rights_chain_keeps_the_abstention(lean):
    """The completion is the norms chain's alone (1.1, `routeOf`): a rights-chain set of right readings beside
    `norm-defaults@0` keeps the abstention on every readings kind, as the soft chain does (K18 above)."""
    raw = env_rights()
    raw["profiles"] = sorted({*raw["profiles"], "norm-defaults@0"})

    def claim(mode):
        return {"right": {"name": "r9", "holder": "person", "guard": ["top"], "lines": [
            {"kind": "claim", "norm": norm_object("no-arrest", "arrest_permitted", False, mode)}]}}
    sigma = entry({"domains": {"state": ["s"], "person": ["p"]}, "constants": {},
                   "relations": {"arbitrary_arrest": [], "journalist": []}}, "default",
                  {"outcome": {"predicate": "arrest_permitted", "tuple": ["s", "p"]}}, True,
                  decisions=[{"key": {"excepted": "no-arrest"}, "tuples": [["s", "p"]]}])
    sid = situation_id(raw, sigma)
    rs9 = reading_set("rs9", "u9", [reading("strict", claim("strict"), {"default": sid}, kind="right"),
                                    reading("default", claim("default"), {"strict": sid}, kind="right")],
                      {sid: sigma})
    document = {"units": [{"id": "u9"}], "reading_sets": [rs9]}
    for kind in ("readings-validate", "readings-elaborate", "readings-choice"):
        row = one(lean, kind, raw, document, choice=[["rs9", 0]], inner={"kind": "rights-conflict"})
        assert row["error"] == "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented"


def test_a_document_without_content_keeps_w2s_route(lean):
    raw = env1()
    document, _ = doc1(raw)
    for r in document["reading_sets"][0]["readings"]:
        r["content"] = None
        r["kind"] = "norm"
    rows = run(lean, [case("readings-validate", raw, document), case("readings-elaborate", raw, document)])
    assert rows[0]["content_bearing"] is False and "fill_premises" not in rows[0]
    assert rows[1]["route"] == "w2"


def test_without_unspecified_predicates_the_answer_is_s1s(lean):
    """`fillDoc_conservative` on the wire: completions `deny` under the profile give S1's rows and no `unsaid__`."""
    raw = env1(ND, "deny")
    sigma = entry({"domains": {"agent": ["a"], "user": ["u"]}, "constants": {}, "relations": {"asks": []}},
                  "every", PROBE1, True)
    document, sid = doc1(raw, sigma)
    row = one(lean, "readings-validate", raw, document)
    assert row["status"] == "ok", row
    assert row["fill_premises"] == [{"set": "rs_1", "index": 0, "premises": []},
                                    {"set": "rs_1", "index": 1, "premises": []}]
    assert [u["unit"] for u in row["filled"]["units"]] == ["u1", "u1"]
    plain = env1(PLAIN, "deny")
    document_plain, _ = doc1(plain, sigma)
    plain_row = one(lean, "readings-validate", plain, document_plain)
    strip = lambda r: [{**p, "pair": {k: v for k, v in p["pair"].items() if k != "situation"}}
                       for p in r["sets"][0]["pairs"]]
    assert strip(row) == strip(plain_row)
