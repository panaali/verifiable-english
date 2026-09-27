"""Regressions for the reviewed soft route and its visible open terms."""
import json

import pytest

from ve.ast import Forall, Top, Unary, Var
from ve.ast import formula_from_data
from ve.document import check_document, coverage, render_document
from ve.entailment import prove_entailment
from ve.errors import VEError
from ve.norm_english import parse_english, render_english
from ve.norm_strict import parse_strict, print_strict
from ve.norms import NormDocument, prove_norm_entailment, check_norm_entailment_certificate
from ve.softnorms import SoftNormDocument
from ve.softnorms import SoftEnvironment
from ve.soft_route import _run, classify_soft_pairs, check_soft_conflict
from ve.surface.softnorms import SoftNorm
from ve.surface.softnorms import rule_paraphrase
from tests.test_english_unambiguity import _soft_env
from tests.test_soft_norms_lean import env, norm, should, ranks, base_prime
from conformance.soft_norms import RUST_FIXTURES, rust_fixture_rows, main as conformance_main


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
    for factors in (("safety, honesty",), ("safety", "honesty")):
        authored = NormDocument(environment, [SoftNorm("n", "required", True, Top(),
            mode="default", decided_by="assistant", factors=factors)])
        source, manifest = render_english(authored)
        parsed = parse_english(environment, source, manifest)
        assert tuple(parsed.rules[0].exception["factors"]) == factors


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
])
def test_python_lean_reject_same_soft_input(raw, rules, diagnostic):
    with pytest.raises(VEError) as python_error:
        SoftNormDocument(SoftEnvironment(raw), rules)
    with pytest.raises(VEError) as lean_error:
        _run({"id": "invalid", "kind": "soft-elaborate", "environment": raw, "norms": rules})
    assert str(python_error.value) == str(lean_error.value) == diagnostic


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


def test_rust_soft_fixture_matches_both_regenerators():
    assert json.loads(RUST_FIXTURES.read_text()) == rust_fixture_rows()


def test_generated_soft_conformance_is_part_of_suite(capsys):
    conformance_main()
    report = json.loads(capsys.readouterr().out)
    assert report["accepted_trees"] == 1000


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
