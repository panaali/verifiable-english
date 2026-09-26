"""Checked lemma bundles with transitive, labelled premise provenance.

The bundle format is deliberately small: every lemma lists its own labelled
hypotheses, earlier conclusion meaning IDs it cites, a certificate, and the
    complete transitive leaves it expects the report to carry. No citation is a
new trusted proof rule: the certificate is replayed with cited conclusions as
additional premises after the cited certificates have been checked. With
``lean_executable`` the whole bundle is re-checked in one Lean `route` run
(`VE.Definitions.Bundle`), which enforces the same citation rules and proves
them sound (`bundle_sound`).
"""
from __future__ import annotations

import subprocess

from .admission import validate_label
from .ast import formula_from_data, formula_to_data
from .background import background
from .entailment import check_entailment_certificate
from .environment import Environment
from .errors import ResourceLimit, VEError
from .identity import meaning_id
from .wire import canonical_json, digest, require_fields


def lean_bundle_verdict(lean_executable, environment, lemmas) -> dict:
    """The Lean route's verdict on a whole bundle, in one run."""
    from .wire import loads_json
    case = [{"id": "bundle", "kind": "bundle", "environment": environment, "lemmas": lemmas}]
    try:
        run = subprocess.run([str(lean_executable), "route"], input=canonical_json(case),
                             capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VEError("Lean lemma replay unavailable") from exc
    rows = loads_json(run.stdout)
    if type(rows) is not list or len(rows) != 1:
        raise VEError("Lean lemma replay returned a malformed result")
    return rows[0]


def check_bundle(data, *, lean_executable=None):
    require_fields(data, {"version", "environment", "lemmas"})
    if data["version"] != "ve-bundle@0" or type(data["lemmas"]) is not list:
        raise VEError("Unsupported lemma bundle version or lemmas array")
    if len(data["lemmas"]) > 256:
        raise ResourceLimit("Lemma bundle exceeds 256 lemmas")
    env = Environment(data["environment"])
    background_leaves = [{"label": "background:" + entry.generator,
                          "ast": formula_to_data(env, entry.formula)} for entry in background(env)]
    known = {}
    names = set()
    reports = []
    for item in data["lemmas"]:
        require_fields(item, {"name", "environment_id", "premises", "cites", "conclusion",
                              "meaning_id", "reading_choices", "transitive_leaves", "certificate"})
        if item["environment_id"] != env.environment_id:
            raise VEError("Citation has another environment or definitions version")
        if type(item["name"]) is not str or not item["name"]:
            raise VEError("Lemma name must be nonempty")
        if item["name"] in names:
            raise VEError("Duplicate lemma name")
        names.add(item["name"])
        if type(item["premises"]) is not list or type(item["cites"]) is not list:
            raise VEError("Premises and citations must be arrays")
        choices = item["reading_choices"]
        if type(choices) is not dict or any(type(k) is not str or type(v) is not str for k, v in choices.items()):
            raise VEError("Reading choices must map unit names to readings")
        leaves = list(background_leaves)
        own = []
        for premise in item["premises"]:
            require_fields(premise, {"label", "ast"})
            label = validate_label(premise["label"])
            formula = formula_from_data(env, premise["ast"])
            own.append(formula)
            leaves.append({"label": label, "ast": formula_to_data(env, formula)})
        cited = []
        inherited_choices = dict(choices)
        for reference in item["cites"]:
            if type(reference) is not str or reference not in known:
                raise VEError("Citation is absent, cyclic, or not earlier in the bundle")
            lemma = known[reference]
            for unit, reading in lemma["reading_choices"].items():
                if unit in inherited_choices and inherited_choices[unit] != reading:
                    raise VEError("Citation has incompatible reading choices")
                inherited_choices[unit] = reading
            for leaf in lemma["transitive_leaves"]:
                if leaf not in leaves:
                    leaves.append(leaf)
            cited.append(lemma["conclusion"])
        if item["transitive_leaves"] != leaves:
            raise VEError("Citation transitive leaf labels were changed or stripped")
        conclusion = formula_from_data(env, item["conclusion"])
        mid = meaning_id(env, conclusion)
        if item["meaning_id"] != mid or mid in known:
            raise VEError("Lemma meaning ID is stale or duplicated")
        premises = tuple(own + cited)
        replay = check_entailment_certificate(env, premises, conclusion, item["certificate"])
        if not replay.valid:
            raise VEError(f"Lemma {item['name']!r} certificate failed: {replay.status}")
        known[mid] = {"conclusion": conclusion, "reading_choices": inherited_choices,
                      "transitive_leaves": leaves}
        reports.append({"name": item["name"], "meaning_id": mid,
                        "reading_choices": inherited_choices, "transitive_leaves": leaves})
    lean_checked = False
    if lean_executable is not None and data["lemmas"]:
        row = lean_bundle_verdict(lean_executable, env.to_dict(), data["lemmas"])
        lean_checked = (row.get("status") == "ok" and
                        row.get("lemmas") == [report["meaning_id"] for report in reports])
        if not lean_checked:
            raise VEError("Lean did not accept every lemma certificate")
    return {"status": "Checked", "environment_id": env.environment_id,
            "bundle_id": digest("ve-bundle-v0\n", data), "lemmas": reports,
            "lean_checked": lean_checked}
