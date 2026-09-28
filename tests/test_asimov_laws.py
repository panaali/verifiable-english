"""Asimov v2: authored English, certified consistency, and spec scenarios."""
import json
from functools import lru_cache
from pathlib import Path

import pytest

from conformance.alternatives import base_environment, cases, scenario
from ve.alternatives import run_case
from ve.ast import Not, _Decoder
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.norm_english import parse_english, render_english
from ve.norms import _bind
from ve.wire import digest


ROOT = Path(__file__).resolve().parents[1] / "usecases" / "asimov-laws"


@lru_cache(maxsize=1)
def load():
    data = json.loads((ROOT / "environment.json").read_text())
    source = (ROOT / "rules.ve").read_text()
    manifest = json.loads((ROOT / "rules.manifest.json").read_text())
    env = Environment(data)
    doc = parse_english(env, source, manifest)
    return data, doc, source, manifest


def case(kind="alt-elaborate", **extra):
    data, doc, _, _ = load()
    return {"id": "asimov-v2", "kind": kind, "environment": data,
            "norms": [rule.to_dict() for rule in doc.rules], **extra}


def conflict_packages():
    source = case()
    env = Environment(source["environment"])
    base = Environment(base_environment(source["environment"]))
    elaborated = run_case(source)
    document_hash = digest(f"ve-alternatives-{env.identity_version}\n", {
        "environment_id": env.environment_id, "norms": source["norms"], "units": []})
    packages = {}
    for target in elaborated["conflict_targets"]:
        conclusion = _bind(Not(_Decoder().decode(target["ast"])), target["sorts"])
        proof = prove_entailment(base, (), conclusion, max_steps=20000)
        assert proof.status == "Found", target["target"]
        packages[target["target"]] = {
            "environment_id": env.environment_id, "document_hash": document_hash,
            "target": target["target"], "certificate": proof.certificate}
    return packages


def spec_scenario(name):
    return next(item["scenario"] for item in cases() if item["id"] == name)


def test_authored_rules_have_one_reading_and_declared_priority():
    data, doc, source, manifest = load()
    assert render_english(doc) == (source, manifest)
    assert data["alternatives"]["fulfilments"] == [
        {"obligation": "prevent_required", "body": "avoids"}]
    assert [(r.name, r.predicate, r.over, len(r.unless)) for r in doc.rules] == [
        ("law-3-permission", "permitted", (), 0),
        ("law-2-permission", "permitted", ("law-3-permission",), 0),
        ("law-1-injury", "breaks_first_law", (), 0),
        ("law-1-inaction", "breaks_first_law", (), 0),
        ("law-0-injury", "breaks_zeroth_law", (), 0),
        ("law-0-inaction", "breaks_zeroth_law", (), 0),
        ("lawful-option", "has_lawful_option", (), 0),
        ("law-1-ban", "permitted", ("law-2-permission",), 0),
        ("law-0-prevention-exception", "permitted", ("law-1-ban",), 1),
        ("law-0-ban", "permitted", ("law-1-ban", "law-0-prevention-exception"), 0),
        ("law-2-obey", "required", (), 0),
        ("law-3-preserve", "prevent_required", (), 0),
    ]


# Review finding P2 (natural English): the P0 listing markers disambiguate
# nested connectives for the parser, but they are not natural prose.
SCAFFOLDING = ("first clause", "second clause", "end first clause", "end second clause",
               "of the following hold", "the following holds", "(a)", "(b)", "(i)", "(ii)")


def test_rules_read_as_english_without_parser_scaffolding():
    _, doc, source, _ = load()
    lowered = source.lower()
    assert [marker for marker in SCAFFOLDING if marker in lowered] == []
    # Omission is not restricted to the designated inaction (review P1, rules 4 and 7).
    by_name = {rule.name: rule for rule in doc.rules}
    for name in ("law-1-inaction", "law-0-inaction"):
        assert "inaction" not in json.dumps(by_name[name].to_dict()["norm"]["guard"])


def test_checker_certifies_conflict_free_and_replays_dilemma():
    packages = conflict_packages()
    assert sorted(packages) == sorted([
        "breaks_first_law", "breaks_zeroth_law", "has_lawful_option", "permitted",
        "prevent_required", "required", "required->permitted"])
    assert run_case(case("alt-conflict", packages=packages))["verdict"] == "CONFLICT-FREE"
    for name, diagnosis in (("b-A0", "NONE-PERMITTED"), ("b-A1", "NONE-PERMITTED"),
                            ("j", "OVER-REQUIRED")):
        result = run_case(case("alt-followable", packages=packages,
                               witness={**spec_scenario(name), "chooser": "r"}))
        assert result["verdict"] == "DILEMMA"
        assert result["diagnosis"].startswith(diagnosis)


@pytest.mark.parametrize("name,clear", [
    ("a", ["pull"]),
    ("b-A0", []),
    ("b-A1", []),
    ("b-A2", []),
    ("b-B", []),
    ("bprime-A", []),
    ("c-7", ["nothing", "pull"]),
    ("c-8", ["nothing", "pull"]),
    ("c-8m", ["nothing", "pull"]),
    ("d-full", ["shield", "retreat"]),
    ("d-prevention", ["shield", "retreat"]),
    ("e", ["act"]),
    ("j", []),
    ("o-7", ["rescue"]),
    ("o-8", ["rescue"]),
    ("bprime-A5", []),
    ("l5", ["pull2"]),
])
def test_spec_scenarios_show_inaction_priority_and_choice(name, clear):
    report = run_case(case("alt-validate", scenario=spec_scenario(name)))
    assert report["status"] == "ok"
    assert report["choosers"][0]["clear"] == clear


SELF, HUMAN, HUMANITY = ("hs",), ("hp",), ("hh",)
HARMS = SELF + HUMAN + HUMANITY


def model(actions, positive, *, ordered=(), injured=(), injured_humanity=()):
    return scenario(list(actions), list(HARMS), tuple(positive), injured=injured,
                    human=HUMAN, humanity=HUMANITY,
                    facts={"harm_to": [[h, "r"] for h in SELF],
                           "ordered": [[a] for a in ordered],
                           "injures_humanity": [[a] for a in injured_humanity]})


# Review findings P1: each reproducer, then its class.
REGRESSIONS = {
    # Rule 5: the Zeroth Law excuses only a necessary First Law breach.
    "ordered-unnecessary-injury": (
        model(["nothing", "act", "rescue"], [("nothing", "hh")], ordered=["act"],
              injured=["act"]), ["rescue"]),
    "unnecessary-injury": (
        model(["nothing", "act", "rescue"], [("nothing", "hh")], injured=["act"]), ["rescue"]),
    "unnecessary-allowed-human-harm": (
        model(["nothing", "act", "rescue"], [("nothing", "hh"), ("act", "hp")]), ["rescue"]),
    "necessary-injury": (model(["nothing", "act"], [("nothing", "hh")], injured=["act"]),
                         ["act"]),
    "two-necessary-injuries": (
        model(["nothing", "act", "act2"], [("nothing", "hh")], injured=["act", "act2"]),
        ["act", "act2"]),
    "harmless-looking-rescue-breaks-zeroth-law": (
        model(["nothing", "act", "rescue"], [("nothing", "hh"), ("rescue", "hh")],
              injured=["act"], injured_humanity=["rescue"]), ["act"]),
    # Rules 4 and 7: any alternative that lets an avoidable harm happen, not only inaction.
    "unrelated-work-while-human-harmed": (
        model(["nothing", "work", "rescue"], [("nothing", "hp"), ("work", "hp")]), ["rescue"]),
    "unrelated-work-while-humanity-harmed": (
        model(["nothing", "work", "rescue"], [("nothing", "hh"), ("work", "hh")]), ["rescue"]),
    "ordered-unrelated-work": (
        model(["nothing", "work", "rescue"], [("nothing", "hp"), ("work", "hp")],
              ordered=["work"]), ["rescue"]),
    "unavoidable-harm": (model(["nothing", "work"], [("nothing", "hp"), ("work", "hp")]),
                         ["nothing", "work"]),
}


@pytest.mark.parametrize("name", REGRESSIONS)
def test_review_reproducers_have_the_source_reading(name):
    situation, clear = REGRESSIONS[name]
    report = run_case(case("alt-validate", scenario=situation))
    assert report["status"] == "ok"
    assert report["choosers"][0]["clear"] == clear
