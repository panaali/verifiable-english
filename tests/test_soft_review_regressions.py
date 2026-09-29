"""Regressions for the reviewed soft route and its visible open terms."""
import json
import time

import pytest

from ve.ast import Forall, Top, Unary, Var
from ve.ast import formula_from_data
from ve.document import check_document, coverage, render_document
from ve.entailment import prove_entailment
from ve.errors import SyntaxError, VEError
from ve.norm_english import parse_english, render_english
from ve.norm_strict import parse_strict, print_strict
from ve.norms import NormDocument, prove_norm_entailment, check_norm_entailment_certificate
from ve.softnorms import SoftNormDocument
from ve.softnorms import SoftEnvironment
from ve.soft_route import _run, classify_soft_pairs, check_soft_conflict, elaborate_soft_document
from ve.surface.softnorms import SoftNorm
from ve.surface.softnorms import rule_paraphrase
from ve.surface.softnorms import parse_header_options, render_header_options
from ve.wire import digest
from tests.test_english_unambiguity import _soft_env
from tests.test_soft_norms_lean import env, norm, should, ranks, base_prime
from ve.softnorms import load_soft_document, _fits, _size, _within_limits
from ve.ast import _Checker
from conformance.soft_norms import (RUST_FIXTURES, rust_fixture_rows, loop_recheck_reproducers,
                                    soft2_reproducers, soft3_reproducers, soft3_accepted,
                                    soft_limits_reproducers, multi_fault_cases, multi_faults,
                                    near_limit_cases, compare_near_limit, _strict_under_default,
                                    compare_rejected, main as conformance_main, soft4_reproducers,
                                    soft4_near_limit, _plain_chain, _negations, _opposed,
                                    _twice, _dual_outcomes, soft4_aggregate_reproducers,
                                    smallest_queries, _exact, _exception,
                                    soft_over_reproducers, soft_over_accepted)
from ve.softnorms import decode_rule
from subprocesses import ChildCPU

REJECTED_INPUTS = 4626
ACCEPTED_NEAR_LIMIT = 90
REJECTED_NEAR_LIMIT = 137


def test_english_default_cannot_enter_w1_semantics():
    environment = _soft_env()
    parsed = parse_english(environment, "Rule 1. Every act should be done.")
    assert isinstance(parsed, SoftNormDocument)
    assert "soft__excepted__rule_1" in parsed.extended_env.decision_names
    with pytest.raises(VEError, match="soft route"):
        prove_norm_entailment(parsed, (), Top())
    with pytest.raises(VEError, match="soft route"):
        check_norm_entailment_certificate(parsed, (), Top(), {})
    raw = NormDocument(environment, [SoftNorm("n", "required", True, Top(),
                                              mode="default", decided_by="assistant")])
    with pytest.raises(VEError, match="SoftNormDocument"):
        raw.premises()
    required = Forall("act", Unary("required", Var(0)))
    assert prove_norm_entailment(parsed.elaborated, (), required).status == "NotFound"


def test_soft_manifest_preserves_hard_and_factor_boundaries():
    environment = _soft_env()
    hard = NormDocument(environment, [SoftNorm("hard", "required", True, Top(), hard=True)])
    source, manifest = render_english(hard)
    assert manifest["blocks"][0]["hard"] is True
    assert parse_english(environment, source, manifest).rules[0].hard is True
    rendered_sources = []
    for factors in (("safety, honesty",), ("safety", "honesty"),
                    ('safety. honesty', 'the "user" said Rule 1')):
        authored = NormDocument(environment, [SoftNorm("n", "required", True, Top(),
            mode="default", decided_by="Dr. Ada", factors=factors)])
        source, manifest = render_english(authored)
        rendered_sources.append(source)
        parsed = parse_english(environment, source, manifest)
        assert tuple(parsed.rules[0].exception["factors"]) == factors
        assert parsed.rules[0].exception["decided_by"] == "Dr. Ada"
    assert rendered_sources[0] != rendered_sources[1]
    prose = ("Rule 1. Every act should be done. The exception to rule 1 "
             "takes account of safety, honesty, and care.")
    assert parse_english(environment, prose).rules[0].exception["factors"] == [
        "safety", "honesty", "care"]


def test_document_coverage_and_render_show_open_exception(tmp_path):
    raw = env()
    rule = should("a", "x_required", True)
    meta = {"format": "ve-document@1", "environment": raw,
            "units": [{"id": "u", "span": [0, 2], "kind": "norm",
                       "meaning": "specified", "support": "none", "content": rule}]}
    path = tmp_path / "default.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\nA\n")
    result = check_document(path)
    assert result["coverage"]["accounted_bytes"] == 2
    assert result["coverage"]["coverage_percent"] == 100
    assert result["coverage"]["soft_status"] == "OPEN"
    assert result["coverage"]["residual"]["default_exceptions"] == 1
    assert result["coverage"]["residual_total"] > 0
    assert "soft__excepted__a" in result["coverage"]["soft_residual_labels"]
    rendered = render_document(path)
    assert "Open rule reading:" in rendered
    assert "open decision by assistant" in rendered
    meta["units"][0]["meaning"] = {"open": ["soft__excepted__a"]}
    path.write_text("---\n" + json.dumps(meta) + "\n---\nA\n")
    assert check_document(path)["coverage"]["residual"]["default_exceptions"] == 1


@pytest.mark.parametrize("raw,rules,diagnostic", [
    (env({"ranks": ["Bad!"], "outranking": {"mode": "strict"}}), [],
     "InvalidInput: invalid soft name Bad!"),
    (env(), [norm("a", "x_required", True, mode="default", exception={
        "decided_by": "", "sufficient": [], "necessary": [], "factors": []})],
     "InvalidInput: invalid decider for rule a"),
    (env({"ranks": ["x", "y", "z"], "outranks": [["x", "y"], ["y", "z"], ["z", "y"]],
          "outranking": {"mode": "strict"}}), [], "DependencyCycle: x, y, z"),
    (env({"ranks": ["a", "a"], "outranking": {"mode": "strict"}}), [],
     "DuplicateDeclaration: rank a"),
    (env({"parties": ["a", "a"], "outranking": {"mode": "strict"}}), [],
     "DuplicateDeclaration: party a"),
    (env(), [norm("a", "x_required", True, alterable=["user"])],
     "UnknownSymbol: party user"),
])
def test_python_lean_reject_same_soft_input(raw, rules, diagnostic):
    with pytest.raises(VEError) as python_error:
        SoftNormDocument(SoftEnvironment(raw), rules)
    with pytest.raises(VEError) as lean_error:
        _run({"id": "invalid", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert str(python_error.value) == str(lean_error.value) == diagnostic


@pytest.mark.parametrize("raw,rules,diagnostic", [
    (env({"outranking": {"mode": "strict", "decided_by": "assistant"}}), [],
     "InvalidInput: strict outranking has no decider"),
    (env({"ranks": ["a", "b"], "ties": [["a", "b"], ["a", "b"]],
          "outranking": {"mode": "strict"}}), [], "InvalidInput: invalid ties pair"),
    (env({"ranks": ["a", "b"], "ties": [["a", "b"], ["b", "a"]],
          "outranking": {"mode": "strict"}}), [], "DuplicateDeclaration: tie"),
    (env({"ranks": ["a", "b"], "outranks": [["a", "b"], ["a", "b"]],
          "outranking": {"mode": "strict"}}), [], "InvalidInput: invalid outranks pair"),
    (env(), [norm("a", "x_required", True, mode="default",
                  exception={"decided_by": "assistant"})],
     "InvalidInput: rule a needs an exception"),
    (env(), [norm("a", "x_required", True, mode="default",
                  exception={**dict(decided_by="assistant", sufficient=[], necessary=[], factors=[]),
                             "unexpected": True})],
     "InvalidInput: rule a needs an exception"),
    (env(), [norm("a", "x_required", True, mode="default",
                  exception={"decided_by": "assistant", "sufficient": {},
                             "necessary": [], "factors": []})],
     "InvalidInput: exception sufficient must be an array"),
    (env(), [norm("a", "x_required", True, mode="default",
                  exception={"decided_by": "assistant", "sufficient": [],
                             "necessary": [], "factors": "safety"})],
     "InvalidInput: invalid factors of rule a"),
    (env(), [norm("a", "x_required", True, exception={})],
     "InvalidInput: rule a is strict and declares an exception"),
    (env({"parties": ["assistant", "user"], "outranking": {"mode": "strict"}}),
     [norm("a", "x_required", True, alterable=["user", "assistant"])],
     "InvalidInput: alterable of rule a must be sorted and distinct"),
])
def test_soft_validation_classes_match_python_and_lean(raw, rules, diagnostic):
    with pytest.raises(VEError) as python_error:
        SoftNormDocument(SoftEnvironment(raw), rules)
    with pytest.raises(VEError) as lean_error:
        _run({"id": "invalid", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert str(python_error.value) == str(lean_error.value) == diagnostic


def invalid_instruction_raw():
    raw = env({"parties": ["p"], "outranking": {"mode": "strict"}})
    raw["vocabulary"]["predicates"]["q"] = {
        "arguments": ["assistant"], "description": "q", "instruction_of": False}
    return raw


@pytest.mark.parametrize("raw,rules,code", [
    (env(), [norm("a", "x_required", True, mode="default")],
     "SOFT_MISSING_EXCEPTION"),
    (env({"ranks": ["a"], "ties": [["a"]], "outranking": {"mode": "strict"}}),
     [], "SOFT_INVALID_TIES_PAIR"),
    (env({}), [], "SOFT_INVALID_BLOCK"),
    (env({"ranks": ["needs an exception"], "outranking": {"mode": "strict"}}),
     [], "SOFT_INVALID_NAME"),
    (invalid_instruction_raw(), [], "SOFT_INVALID_INPUT"),
])
def test_reported_diagnostic_codes(raw, rules, code):
    with pytest.raises(VEError) as python_error:
        SoftNormDocument(SoftEnvironment(raw), rules)
    with pytest.raises(VEError) as lean_error:
        _run({"id": "invalid", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert python_error.value.code == lean_error.value.code == code
    assert python_error.value.to_dict()["code"] == code


@pytest.mark.parametrize("name,raw,rules,code",
                         [*loop_recheck_reproducers(), *soft2_reproducers(),
                          *soft3_reproducers(), *soft_limits_reproducers(), *soft4_reproducers(),
                          *soft4_aggregate_reproducers(), *soft_over_reproducers()])
def test_loop_recheck_diagnostic_precedence(name, raw, rules, code):
    with pytest.raises(VEError) as python_error:
        load_soft_document(raw, rules)
    with pytest.raises(VEError) as lean_error:
        _run({"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert python_error.value.code == lean_error.value.code == code
    assert python_error.value.to_dict()["code"] == code


@pytest.mark.parametrize("name,raw,rules", soft3_accepted())
def test_node_budgets_admit_the_same_sources(name, raw, rules):
    python = load_soft_document(raw, rules)
    lean = _run({"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert lean["environment_prime"] == python.extended_env.to_dict()
    # Accepted means elaborable: the public route serialises every generated formula,
    # and the smallest entailment and conflict queries on the elaboration type-check.
    assert elaborate_soft_document(python)["premises"] == lean["premises"]
    smallest_queries(python)


@pytest.mark.parametrize("rules,check", [
    ([norm("a", "x_required", True, guard=_exact(4981))], "ResourceLimit: generated norm layers"),
    ([should("a", "x_required", True, exception=_exception("sufficient", _exact(9996)))],
     "ResourceLimit: generated background")])
def test_aggregate_limits_are_checked_at_admission(rules, check):
    # soft4-looprecheck1 B1: strict-guard-4981 (layers of 10,021 nodes) and
    # premise-nodes-9996 (a background′ of 10,006) were accepted and elaborated,
    # then `prove_norm_entailment(d.elaborated, (), ⊤)` raised ResourceLimit: the
    # entailment route types the layers and the conclusion with one checker, and
    # background′ with another. Both validators now reject them at 6.15 and 6.14.
    with pytest.raises(VEError) as python_error:
        load_soft_document(env(), rules)
    with pytest.raises(VEError) as lean_error:
        _run({"id": "b1", "kind": "soft-elaborate", "environment": env(), "norms": rules})
    assert python_error.value.code == lean_error.value.code == "SOFT_RESOURCE_LIMIT"
    assert str(python_error.value) == str(lean_error.value) == check


@pytest.mark.parametrize("wrappers,check", [(54, "ResourceLimit: derived carve-out of rule d"),
                                            (53, "ResourceLimit: generated norm layer"),
                                            (44, "ResourceLimit: generated norm layer")])
def test_derived_depth_is_checked_by_both_validators(wrappers, check):
    # soft3-loop.final.md: Lean bounded the derived carve-out's nodes but not its depth.
    rules = _strict_under_default(wrappers)
    with pytest.raises(VEError) as python_error:
        load_soft_document(env(), rules)
    with pytest.raises(VEError) as lean_error:
        _run({"id": "d", "kind": "soft-elaborate", "environment": env(), "norms": rules})
    assert python_error.value.code == lean_error.value.code == "SOFT_RESOURCE_LIMIT"
    assert str(python_error.value).startswith(check) and str(lean_error.value).startswith(check)


def test_coherence_expansion_is_sized_before_it_is_built():
    # soft4-looprecheck1 B3: 26 plain predicates, each strict rule guarded by 40
    # negations of its predecessor, and two opposing defaults on the last. Python
    # expanded the coherence premise before checking it and raised RecursionError.
    raw, rules = _plain_chain(26, _negations(40), _opposed("p25"))
    check = "ResourceLimit: generated soft premise"
    with pytest.raises(VEError) as python_error:
        load_soft_document(raw, rules)
    with pytest.raises(VEError) as lean_error:
        _run({"id": "b3", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert python_error.value.code == lean_error.value.code == "SOFT_RESOURCE_LIMIT"
    assert str(python_error.value).startswith(check) and str(lean_error.value).startswith(check)


@pytest.mark.parametrize("count,target", [(11, "p10"), (10, "x_required->x_permitted")])
def test_expanded_conflict_targets_are_checked_before_acceptance(count, target):
    # soft4-looprecheck1 B2: each strict rule guarded by its predecessor twice. Both
    # validators accepted p0 … p10, and the public elaboration returned a p10
    # conflict target of 18,427 nodes that no decoder loads. The pair target states
    # two outcomes, so it is checked on its own too.
    raw, rules = _plain_chain(count, _twice) if target == "p10" else _dual_outcomes(count)
    check = f"ResourceLimit: generated conflict target {target}"
    with pytest.raises(VEError) as python_error:
        load_soft_document(raw, rules)
    with pytest.raises(VEError) as lean_error:
        _run({"id": "b2", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert python_error.value.code == lean_error.value.code == "SOFT_RESOURCE_LIMIT"
    assert str(python_error.value) == str(lean_error.value) == check
    # One predicate fewer is accepted, and every regenerated target serialises and matches.
    raw, rules = _plain_chain(count - 1, _twice) if target == "p10" else _dual_outcomes(count - 1)
    soft = load_soft_document(raw, rules)
    elaborated = elaborate_soft_document(soft)
    for item in elaborated["conflict_targets"]:
        body = ["not", item["ast"]]
        for sort in reversed(item["sorts"]):
            body = ["forall", sort, body]
        formula_from_data(soft.elaborated.base_environment(), body)


@pytest.mark.parametrize("name,raw,rules,code", list(soft4_reproducers()))
def test_exponential_unfoldings_are_rejected_without_being_built(name, raw, rules, code):
    # Each unfolding is beyond 2 ** 24 nodes; both validators size it from their
    # per-rule tables. A build of it would not finish within these bounds, which
    # are CPU seconds (tests/subprocesses.py), not elapsed time under load.
    started = time.process_time()
    with pytest.raises(VEError) as python_error:
        load_soft_document(raw, rules)
    assert time.process_time() - started < 10
    with ChildCPU() as lean_cpu, pytest.raises(VEError) as lean_error:
        _run({"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert lean_cpu.seconds < 30
    assert python_error.value.code == lean_error.value.code == code


def test_generated_sizes_equal_the_checker_walk():
    # The sizes both validators check are those of the formulas the route serialises.
    for name, raw, rules in [*soft3_accepted(), *soft4_near_limit()]:
        try:
            soft = load_soft_document(raw, rules)
        except VEError:
            continue
        for label, formula in (*soft.exception_premises, *soft.coherence_premises,
                               *soft.elaborated.premises()):
            assert _within_limits(soft.extended_env, formula) == _fits(_size(formula)), (name, label)
            counter = _Checker(soft.extended_env, generated=True)
            counter.formula(formula)
            assert counter.nodes == _size(formula)[0], (name, label)
        for predicate in soft.elaborated.order:
            assert soft.expansion_sizes[predicate] == _size(
                soft.elaborated.outcome(predicate, base=True)), (name, predicate)


def test_accepted_sources_elaborate_and_rejected_sources_share_codes():
    # Every accepted fixture and the near-limit generator: accepted implies Lean
    # accepts and the public regeneration check passes; rejected implies the same code.
    accepted, rejected = compare_near_limit(near_limit_cases())
    assert (accepted, rejected) == (ACCEPTED_NEAR_LIMIT, REJECTED_NEAR_LIMIT)


def test_multi_fault_generator_covers_the_table():
    faults = multi_faults()
    assert {f[2][0] for f in faults} == {1, 2, 3, 4, 5, 6}
    cases = list(multi_fault_cases())
    sizes = {name.count("+") + 1 for name, *_ in cases}
    assert sizes == {2, 3}
    phases = {name: {f[2][0] for f in faults if f[0] in name.split("+")} for name, *_ in cases}
    assert any(len(p) == 1 for p in phases.values())
    assert any(len(p) >= 2 for p in phases.values())
    assert len({code for *_, code in cases}) >= 20


def test_rejection_fixtures_and_generated_soft_inputs_share_codes():
    assert compare_rejected() == REJECTED_INPUTS


def test_document_checks_environment_and_rules_as_one_source(tmp_path):
    raw = env({"parties": ["p"], "outranking": {"mode": "strict"}})
    raw["vocabulary"]["predicates"]["z"] = {"arguments": ["assistant"], "description": "z",
                                            "instruction_of": "missing"}
    rule = should("a", "x_required", True)
    rule["norm"]["exception"]["factors"] = ["x" * 201]
    meta = {"format": "ve-document@1", "environment": raw,
            "units": [{"id": "u", "span": [0, 2], "kind": "norm",
                       "meaning": "specified", "support": "none", "content": rule}]}
    path = tmp_path / "faults.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\nA\n")
    with pytest.raises(VEError) as error:
        check_document(path)
    assert error.value.code == "SOFT_INVALID_FACTORS"


@pytest.mark.parametrize("parties", [("a",), ("a", "b"), ("a", "b", "c"),
                                     tuple("abcdefgh")])
def test_english_switches_round_trip_all_declared_parties(parties):
    raw = _soft_env().to_dict()
    raw["vocabulary"]["soft"]["parties"] = list(parties)
    environment = SoftEnvironment(raw)
    authored = SoftNormDocument(environment, [
        SoftNorm("a", "required", True, Top(), alterable=parties).to_dict()])
    source, manifest = render_english(authored)
    assert parse_english(environment, source, manifest).rules[0].alterable == parties
    assert parse_header_options(render_header_options((), parties)[2:-1]) == ((), parties)


@pytest.mark.parametrize("header", ["a and a may turn off", "a and may turn off",
                                   "a, b may turn off", "a and b and may turn off"])
def test_english_switches_reject_malformed_lists(header):
    with pytest.raises(SyntaxError):
        parse_header_options(header)


def test_strict_switch_rendering_shows_open_party(tmp_path):
    raw = env({"parties": ["user"], "outranking": {"mode": "strict"}})
    rule = norm("a", "x_required", True, alterable=["user"])
    meta = {"format": "ve-document@1", "environment": raw,
            "units": [{"id": "u", "span": [0, 2], "kind": "norm", "meaning": "specified",
                       "support": "none", "content": rule}]}
    path = tmp_path / "switch.ve.md"
    path.write_text("---\n" + json.dumps(meta) + "\n---\nA\n")
    assert check_document(path)["coverage"]["soft_status"] == "OPEN"
    rendered = render_document(path)
    assert "Open rule reading:" in rendered
    assert "user may turn it off for this situation" in rendered


def test_unused_coherence_is_not_a_certificate_dependency():
    raw = env()
    rules = [should("a", "x_required", True), should("b", "x_permitted", False)]
    row = _run({"id": "e", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert row["conditional_on"] == ["soft:coherence:a,b"]
    prime = row["environment_prime"]
    profiles = prime["profiles"]
    env_id = digest("ve-environment-v0.2:" + ",".join(profiles) + "\n", prime)
    premises = [item["ast"] for item in row["background"] + row["premises"]]
    meaning = lambda ast: digest("ve-meaning-v0.2:" + ",".join(profiles) + "\n",
                                 {"environment_id": env_id, "ast": ast})
    certificate = {"checker_version": "ve-tableau-checker@2",
                   "environment_id": env_id,
                   "premise_meaning_ids": [meaning(ast) for ast in premises],
                   "conclusion_meaning_id": meaning(["top"]),
                   "trace": {"rule": "close"}}
    result = _run({"id": "c", "kind": "soft-certificate", "environment": raw,
                   "norms": rules, "premises": [], "conclusion": ["top"],
                   "certificate": certificate})
    assert result["valid"] is True
    assert result["conditional_on"] == []


def test_substitutable_coherence_leaves_keep_a_sufficient_dependency():
    raw = env()
    rules = [should("a", "x_required", True), should("b", "x_permitted", False),
             should("c", "x_permitted", False)]
    row = _run({"id": "e", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    labels = ["soft:coherence:a,b", "soft:coherence:a,c"]
    assert row["conditional_on"] == labels
    leaves = {item["label"]: item["ast"] for item in row["background"] if "label" in item}
    conclusion = ["or", leaves[labels[0]], leaves[labels[1]]]
    prime = row["environment_prime"]
    # The proof uses either coherence leaf. Keeping the original premise positions
    # matters because the certificate is bound to the complete source background.
    decoded = SoftEnvironment(prime, generated=True)
    premises = [formula_from_data(decoded, item["ast"])
                for item in row["background"] + row["premises"]
                if item.get("generator") != "profile"]
    claim = formula_from_data(decoded, conclusion)
    proof = prove_entailment(decoded, premises, claim)
    assert proof.status == "Found"
    case = {"id": "c", "kind": "soft-certificate", "environment": raw,
            "norms": rules, "premises": [], "conclusion": conclusion,
            "certificate": proof.certificate}
    result = _run(case)
    assert result["valid"] is True
    assert len(result["conditional_on"]) == 1
    assert result["conditional_on"][0] in labels


def test_public_soft_pair_and_conflict_entrypoints():
    soft = SoftNormDocument(SoftEnvironment(env()),
                            [should("a", "x_required", True),
                             should("b", "x_permitted", False)])
    pairs = classify_soft_pairs(soft)
    assert pairs["pairs"][0]["status"] == "UNKNOWN"
    conflict = check_soft_conflict(soft)
    assert conflict["verdict"] == "UNKNOWN"
    assert "among rules on the same act" not in conflict["status_text"]
    assert "budget 10000" in conflict["status_text"]
    assert conflict["coherent_exhibit"] is False
    shown = check_soft_conflict(soft, coherent_model={
        "complete": True, "domains": {"assistant": ["a"], "user": []},
        "constants": {}, "relations": {"soft__excepted__a": [["a"]],
                                      "soft__excepted__b": []}}, budget=42)
    assert shown["coherent_exhibit"] is True
    assert shown["budget"] == 42


def test_rust_soft_fixture_matches_both_regenerators():
    assert json.loads(RUST_FIXTURES.read_text()) == rust_fixture_rows()


def test_generated_soft_conformance_is_part_of_suite(capsys):
    conformance_main()
    report = json.loads(capsys.readouterr().out)
    assert report["accepted_trees"] == 1000
    assert report["rejected_inputs"] == REJECTED_INPUTS
    assert report["near_limit_accepted"] == ACCEPTED_NEAR_LIMIT
    assert report["near_limit_rejected"] == REJECTED_NEAR_LIMIT


@pytest.mark.parametrize("role,sign,effect", [
    ("obligation", True, "required"),
    ("obligation", False, "not required"),
    ("permission", True, "permitted"),
    ("permission", False, "not permitted"),
])
def test_default_paraphrase_names_its_actual_effect(role, sign, effect):
    wording = rule_paraphrase(12, "default", role=role, sign=sign, decider="assistant")
    assert f"act {effect} unless" in wording
    assert "assistant decides" in wording
    assert "source names no decider" in rule_paraphrase(12, "default", decider="unstated")
    assert "act false unless" in rule_paraphrase(12, "default", role="plain", sign=False)


def test_soft_strict_text_round_trip_and_hard_identity():
    environment = _soft_env()
    authored = SoftNormDocument(environment, [
        SoftNorm("hard", "required", True, Top(), hard=True).to_dict(),
        SoftNorm("default", "permitted", False, Top(), mode="default",
                 decided_by="assistant", rank="helpfulness", alterable=("user",),
                 sufficient=(Top(),), necessary=(Top(),),
                 factors=("safety, honesty",)).to_dict(),
    ])
    source = print_strict(authored)
    assert "rule default default serves helpfulness alterable by user:" in source
    assert 'factor "safety, honesty"' in source
    parsed = parse_strict(environment, source)
    assert [r.to_dict() for r in parsed.rules] == [r.to_dict() for r in authored.rules]
    assert print_strict(parsed) == source
    tricky = source.replace('decided by "assistant"',
                            'decided by "assistant factor safety"')
    assert parse_strict(environment, tricky).rules[1].exception["decided_by"] == "assistant factor safety"


def test_disjoint_pair_is_removed_from_conditional_report():
    q = ["unary", "q", ["var", 0]]
    raw = env(extra={"q": {"arguments": ["assistant"], "description": "q"}})
    rules = [should("a", "x_required", True, guard=q),
             should("b", "x_required", False, guard=["not", q])]
    soft = SoftNormDocument(SoftEnvironment(raw), rules)
    row = _run({"id": "e", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    pair = row["colliding_pairs"][0]
    base = base_prime(row)
    claim = formula_from_data(base, pair["ast"])
    premises = [formula_from_data(base, item["ast"]) for item in row["background"]
                if item.get("label", "").startswith("soft:exception:")]
    proof = prove_entailment(base, premises, claim)
    assert proof.status == "Found"
    package = {"environment_id": soft.env.environment_id,
               "document_hash": soft.document_hash, "target": pair["label"],
               "certificate": proof.certificate}
    evidence = {pair["label"]: package}
    assert classify_soft_pairs(soft, pairs=evidence)["discharged"] == [pair["label"]]
    assert check_soft_conflict(soft, pairs=evidence)["conditional_on"] == []


def test_rank_resolved_pair_counts_override_but_no_weighing_point():
    soft = SoftNormDocument(SoftEnvironment(env(ranks(["high", "low"], "holistic"))),
                            [should("h", "x_required", True, rank="high"),
                             should("l", "x_required", False, rank="low")])
    report = coverage({"units": [], "source": b"", "meta": {}, "soft_document": soft})
    assert report["residual"]["default_exceptions"] == 2
    assert report["residual"]["holistic_overrides"] == 1
    assert report["residual"]["weighing_points"] == 0


def test_python_and_lean_report_rank_warning_and_undeclared_tie():
    raw = env({"ranks": ["high", "low", "other"], "outranks": [["high", "low"]],
               "outranking": {"mode": "strict"}})
    rules = [should("m", "x_required", True, rank="high"),
             should("n", "x_required", False, rank="low", over=["m"])]
    soft = SoftNormDocument(SoftEnvironment(raw), rules)
    row = elaborate_soft_document(soft)
    assert row["warnings"] == list(soft.warnings)
    assert "RankAgainstPrecedence: rule n over m" in row["warnings"]
    assert "undeclared tie: high, other" in row["warnings"]


@pytest.mark.parametrize("name,raw,rules,code", list(soft_over_reproducers()))
def test_repeated_over_is_rejected_at_decode(name, raw, rules, code):
    # soft4-loop.final B: `over: ["a"] * 41` was accepted by Python, which merged the
    # repeats, and rejected by Lean, which built one child per copy (a layer beyond
    # MAX_NODES); with two copies both accepted and the public elaboration raised
    # "regeneration mismatch: derived carve-outs". `over` is a set: both reject a
    # repeat at 4.2 with one code and one text.
    with pytest.raises(VEError) as python_error:
        load_soft_document(raw, rules)
    with pytest.raises(VEError) as lean_error:
        _run({"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert python_error.value.code == lean_error.value.code == code
    assert str(python_error.value) == str(lean_error.value)
    if code == "SOFT_INVALID_INPUT" and "repeat-before-predicate" not in name:
        assert str(python_error.value) == "InvalidInput: duplicate over a in rule b"
        # The W2 unit decoder (one norm unit on its own) rejects it the same way.
        with pytest.raises(VEError) as unit_error:
            decode_rule(SoftEnvironment(raw), next(r for r in rules if r["norm"]["name"] == "b"))
        assert (unit_error.value.code, str(unit_error.value)) == (code, str(python_error.value))


@pytest.mark.parametrize("name,raw,rules", list(soft_over_accepted()))
def test_children_are_sorted_by_name_on_both_sides(name, raw, rules):
    # soft4-loop.final B: distinct children given out of name order. Python built
    # them in document order and Lean by name, so the regenerated derived carve-outs
    # differed. The public elaboration regenerates with Lean and compares.
    python = load_soft_document(raw, rules)
    lean = _run({"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules})
    elaborated = elaborate_soft_document(python)
    assert elaborated["premises"] == lean["premises"]
    assert lean["environment_prime"] == python.extended_env.to_dict()
    # One canonical order for children: reversing every `over` list changes no derived
    # carve-out and no layer on either side.
    shuffled = [{"norm": {**r["norm"], "over": r["norm"]["over"][::-1]}} for r in rules]
    again = _run({"id": name, "kind": "soft-elaborate", "environment": raw, "norms": shuffled})
    assert (again["derived"], again["premises"]) == (lean["derived"], lean["premises"])
    assert elaborate_soft_document(load_soft_document(raw, shuffled))["premises"] == elaborated["premises"]
