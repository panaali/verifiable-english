"""Regressions for the reviewed soft route and its visible open terms."""
import json

import pytest

from ve.ast import Top
from ve.document import check_document, render_document
from ve.errors import VEError
from ve.norm_english import parse_english, render_english
from ve.norms import NormDocument, prove_norm_entailment, check_norm_entailment_certificate
from ve.softnorms import SoftNormDocument
from ve.softnorms import SoftEnvironment
from ve.soft_route import _run, classify_soft_pairs, check_soft_conflict
from ve.surface.softnorms import SoftNorm
from tests.test_english_unambiguity import _soft_env
from tests.test_soft_norms_lean import env, norm, should
from conformance.soft_norms import RUST_FIXTURES, rust_fixture_rows


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
    assert result["coverage"]["residual"]["soft_decisions"] == 1
    assert result["coverage"]["residual_total"] > 0
    assert "soft__excepted__a" in result["coverage"]["soft_residual_labels"]
    rendered = render_document(path)
    assert "Open rule reading:" in rendered
    assert "open decision by assistant" in rendered
    meta["units"][0]["meaning"] = {"open": ["soft__excepted__a"]}
    path.write_text("---\n" + json.dumps(meta) + "\n---\nA\n")
    assert check_document(path)["coverage"]["residual"]["soft_decisions"] == 1


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


def test_rust_soft_fixture_matches_both_regenerators():
    assert json.loads(RUST_FIXTURES.read_text()) == rust_fixture_rows()
