"""Asimov v2: authored English, certified consistency, and spec scenarios."""
import json
from functools import lru_cache
from pathlib import Path

import pytest

from conformance.alternatives import base_environment, cases
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
    assert [(r.name, r.over) for r in doc.rules] == [
        ("law-3-permission", ()),
        ("law-2-permission", ("law-3-permission",)),
        ("law-1-direct", ("law-2-permission",)),
        ("law-1-inaction", ("law-2-permission",)),
        ("law-0-prevention-exception", ("law-1-direct", "law-1-inaction")),
        ("law-0-direct", ("law-1-direct", "law-0-prevention-exception")),
        ("law-0-inaction", ("law-1-inaction", "law-0-prevention-exception")),
        ("law-2-obey", ()),
        ("law-3-preserve", ()),
    ]


def test_checker_certifies_conflict_free_and_replays_dilemma():
    packages = conflict_packages()
    assert len(packages) == 4
    assert run_case(case("alt-conflict", packages=packages))["verdict"] == "CONFLICT-FREE"
    for name, diagnosis in (("b-A1", "NONE-PERMITTED"), ("j", "OVER-REQUIRED")):
        result = run_case(case("alt-followable", packages=packages,
                               witness={**spec_scenario(name), "chooser": "r"}))
        assert result["verdict"] == "DILEMMA"
        assert result["diagnosis"].startswith(diagnosis)


@pytest.mark.parametrize("name,clear", [
    ("a", ["pull"]),
    ("b-A0", ["pull"]),
    ("b-A1", []),
    ("b-A2", ["pull"]),
    ("b-B", ["pull"]),
    ("bprime-A", []),
    ("c-7", ["nothing", "pull"]),
    ("c-8", ["nothing", "pull"]),
    ("c-8m", ["nothing", "pull"]),
    ("d-full", ["shield", "retreat"]),
    ("d-prevention", ["shield", "retreat"]),
    ("e", ["act"]),
    ("j", []),
    ("o-7", ["act", "rescue"]),
    ("o-8", ["act", "rescue"]),
    ("bprime-A5", []),
    ("l5", ["pull", "pull2"]),
])
def test_spec_scenarios_show_inaction_priority_and_choice(name, clear):
    report = run_case(case("alt-validate", scenario=spec_scenario(name)))
    assert report["status"] == "ok"
    assert report["choosers"][0]["clear"] == clear
