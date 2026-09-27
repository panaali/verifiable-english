"""The checked, deliberately limited action reading of Asimov's laws."""
from dataclasses import replace
import json
from pathlib import Path

from ve.environment import Environment
from ve.evaluate import _Evaluator
from ve.model import FiniteModel
from ve.norm_english import parse_english, render_english
from ve.norms import NormDocument, check_conflict


ROOT = Path(__file__).resolve().parents[1] / "usecases" / "asimov-laws"


def load():
    env = Environment(json.loads((ROOT / "environment.json").read_text()))
    source = (ROOT / "rules.ve").read_text()
    manifest = json.loads((ROOT / "rules.manifest.json").read_text())
    doc = parse_english(env, source, manifest)
    return doc, source, manifest


def scenario(doc, *, ordered=False, protects=False, human_harm=False, humanity_harm=False):
    relations = {p: [] for p in doc.base_environment().predicates}
    for predicate, holds in (("ordered", ordered), ("protects_robot", protects),
                             ("injures_human", human_harm), ("injures_humanity", humanity_harm)):
        if holds:
            relations[predicate] = [["act"]]
    return FiniteModel.from_dict(doc.base_environment(), {
        "complete": True, "domains": {"action": ["act"]},
        "constants": {}, "relations": relations,
    })


def outcome(doc, model, predicate, action="act"):
    evaluator = _Evaluator(doc.base_environment(), model, 100_000, trace=False)
    return evaluator.formula(doc.outcome(predicate, base=True), (("action", action),))[0]


def test_authoring_round_trip_priority_and_conflict_certificate():
    doc, source, manifest = load()
    assert render_english(doc) == (source, manifest)
    assert [(r.name, r.over) for r in doc.rules[:4]] == [
        ("law-3-permission", ()),
        ("law-2-permission", ("law-3-permission",)),
        ("law-1-direct", ("law-2-permission",)),
        ("law-0-direct", ("law-1-direct",)),
    ]
    assert check_conflict(doc, prove=True).status == "CONFLICT-FREE"


def test_order_to_harm_human_and_safe_order():
    doc, _, _ = load()
    harmful = scenario(doc, ordered=True, human_harm=True)
    assert not outcome(doc, harmful, "permitted")
    assert not outcome(doc, harmful, "required")
    assert check_conflict(doc, model=harmful, prove=True).status == "CONFLICT-FREE"

    safe = scenario(doc, ordered=True)
    assert outcome(doc, safe, "permitted")
    assert outcome(doc, safe, "required")


def test_zeroth_direct_ban_and_self_protection():
    doc, _, _ = load()
    collective_harm = scenario(doc, ordered=True, humanity_harm=True)
    assert not outcome(doc, collective_harm, "permitted")
    assert not outcome(doc, collective_harm, "required")

    protection = scenario(doc, protects=True)
    assert outcome(doc, protection, "permitted")
    assert outcome(doc, protection, "required")


def test_harmful_order_without_first_law_precedence_has_plain_english_witness():
    doc, _, _ = load()
    rules = [replace(r, over=()) if r.name == "law-1-direct" else r for r in doc.rules]
    unprioritised = NormDocument(doc.env, rules)
    witness = check_conflict(unprioritised, model=scenario(unprioritised, ordered=True, human_harm=True))
    assert witness.status == "CONFLICT"
    assert witness.target == "permitted"
    assert "rule law-2-permission permits" in witness.situation
    assert "rule law-1-direct forbids" in witness.situation


def test_two_compatible_protective_alternatives_expose_law_three_approximation():
    doc, _, _ = load()
    relations = {p: [] for p in doc.base_environment().predicates}
    relations["protects_robot"] = [["shield"], ["retreat"]]
    model = FiniteModel.from_dict(doc.base_environment(), {
        "complete": True, "domains": {"action": ["shield", "retreat"]},
        "constants": {}, "relations": relations,
    })
    for action in ("shield", "retreat"):
        assert outcome(doc, model, "permitted", action)
        assert outcome(doc, model, "required", action)
    assert check_conflict(doc, model=model, prove=True).status == "CONFLICT-FREE"

    readme = (ROOT / "README.md").read_text()
    assert "Rule 6 is an illustrative assumption" in readme
    assert "**UNFORMALISED:** The source's Law 3 preservation obligation" in readme


def test_completion_defaults_allow_unclassified_action_without_requiring_it():
    doc, _, _ = load()
    unclassified = scenario(doc)
    assert outcome(doc, unclassified, "permitted")
    assert not outcome(doc, unclassified, "required")

    readme = (ROOT / "README.md").read_text()
    assert "permission defaults to allow" in readme
    assert "obligation defaults to not required" in readme
