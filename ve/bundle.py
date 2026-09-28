"""Checked lemma bundles with transitive, labelled premise provenance.

The bundle format is deliberately small: every lemma lists its own labelled
hypotheses, earlier conclusion meaning IDs it cites, a certificate, and the
    complete transitive leaves it expects the report to carry. No citation is a
new trusted proof rule: the certificate is replayed with cited conclusions as
additional premises after the cited certificates have been checked. With
``document.reading_sets`` a reading label names exactly the registered formula
at its set version and index, which must be the latest registered version;
``all`` names that set's disjunction. A bundle
with reading labels requires this registry. With ``lean_executable`` the whole
bundle is re-checked in one Lean `route` run
(`VE.Definitions.Bundle`), which enforces the same citation rules and proves
them sound (`bundle_sound`).
"""
from __future__ import annotations

from .admission import _decode_reading_set, _disjunction, parse_label, validate_label
from .assurance import semantic_entry
from .ast import formula_from_data, formula_to_data
from .backends import lean as lean_backend
from .background import background
from .entailment import check_entailment_certificate
from .environment import Environment
from .errors import ResourceLimit, VEError
from .identity import meaning_id
from .wire import digest, require_fields

LEAN_REPLAY_TIMEOUT = 120


def _english(env, cited, conclusion):
    """The citation sentence, when the vocabulary has an English rendering."""
    from .surface.definitions import render_citation
    try:
        return render_citation(env, cited, conclusion)
    except VEError:
        return None


def _leaf_choices(leaves):
    """Canonical choices from all transitive reading leaves, including versions.

    An `all` leaf can coexist with a concrete choice at the same version;
    the concrete choice is then the effective branch choice.
    """
    choices = {}
    for leaf in leaves:
        label = parse_label(leaf["label"])
        if label.kind != "readings":
            continue
        unit, version, choice = label.args
        previous = choices.get(unit)
        if previous is not None:
            old_version, old_choice = previous
            if old_version != version or (old_choice is not None and choice is not None
                                          and old_choice != choice):
                raise VEError("Citation has incompatible reading choices")
            if choice is None:
                choice = old_choice
        choices[unit] = (version, choice)
    return {unit: f"{version}:{'all' if choice is None else choice}"
            for unit, (version, choice) in choices.items()}


def _bind_leaf(label, formula, reading_sets):
    parsed = parse_label(label)
    if parsed.kind == "cite":
        raise VEError("Unresolved citation hypothesis")
    if parsed.kind != "readings":
        return
    unit, version, index = parsed.args
    matches = [readings for rid, v, readings in reading_sets if rid == unit and v == version]
    if len(matches) != 1:
        raise VEError("Reading label has no unique registered reading set")
    if any(rid == unit and v > version for rid, v, _ in reading_sets):
        raise VEError("Reading label depends on a superseded reading set version")
    readings = matches[0]
    expected = _disjunction(readings) if index is None else (
        readings[index] if index < len(readings) else None)
    if expected != formula:
        raise VEError("Reading label is not bound to its registered reading formula")


def lean_bundle_verdict(lean_executable, environment, lemmas, document=None) -> dict:
    """The Lean route's verdict on a whole bundle, in one run.

    Raises `CheckerUnavailable` when Lean gives no well-formed answer; a
    returned row with `status: error` is Lean's rejection.
    """
    case = [{"id": "bundle", "kind": "bundle", "environment": environment, "lemmas": lemmas,
             **({} if document is None else {"document": document})}]
    return lean_backend.run("bundle.check", lean_executable, case, runner="ve_conformance",
                            mode="route", timeout=LEAN_REPLAY_TIMEOUT, fields={"lemmas": list})[0]


@semantic_entry("bundle.check")
def check_bundle(data, *, lean_executable=None):
    """Replay a lemma bundle; with `lean_executable`, Lean must also accept it.

    `lean_outcome` is `accepted`, `not_requested`, or `not_applicable` (no
    lemmas). A Lean rejection raises `VEError`; Lean giving no answer raises
    `CheckerUnavailable`, which is operational and never a verdict.
    """
    require_fields(data, {"version", "environment", "lemmas"} |
                   ({"document"} if type(data) is dict and "document" in data else set()))
    if data["version"] != "ve-bundle@0" or type(data["lemmas"]) is not list:
        raise VEError("Unsupported lemma bundle version or lemmas array")
    if len(data["lemmas"]) > 256:
        raise ResourceLimit("Lemma bundle exceeds 256 lemmas")
    env = Environment(data["environment"])
    document = data.get("document", {"reading_sets": []})
    require_fields(document, {"reading_sets"})
    if type(document["reading_sets"]) is not list:
        raise VEError("Document reading sets must be an array")
    reading_sets = [_decode_reading_set(env, entry) for entry in document["reading_sets"]]
    if len({(rid, version) for rid, version, _ in reading_sets}) != len(reading_sets):
        raise VEError("duplicate reading set version")
    background_leaves = [{"label": "background:" + entry.generator,
                          "ast": formula_to_data(env, entry.formula)} for entry in background(env)]
    known = {}
    names = set()
    names_by_id = {}
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
        own_leaves = []
        for premise in item["premises"]:
            require_fields(premise, {"label", "ast"})
            label = validate_label(premise["label"])
            formula = formula_from_data(env, premise["ast"])
            _bind_leaf(label, formula, reading_sets)
            own.append(formula)
            own_leaves.append({"label": label, "ast": formula_to_data(env, formula)})
            leaves.append(own_leaves[-1])
        cited = []
        for reference in item["cites"]:
            if type(reference) is not str or reference not in known:
                raise VEError("Citation is absent, cyclic, or not earlier in the bundle")
            lemma = known[reference]
            for leaf in lemma["transitive_leaves"]:
                if leaf not in leaves:
                    leaves.append(leaf)
            cited.append(lemma["conclusion"])
        for reference in item["cites"]:
            for leaf in known[reference]["transitive_leaves"]:
                if leaf not in background_leaves and leaf not in own_leaves:
                    raise VEError("Citation hypothesis is absent from the citing branch")
        inherited_choices = _leaf_choices(leaves)
        for leaf in leaves:
            _bind_leaf(leaf["label"], formula_from_data(env, leaf["ast"]), reading_sets)
        if choices != inherited_choices:
            raise VEError("Citation reading choices do not match transitive leaves")
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
                        "reading_choices": inherited_choices, "transitive_leaves": leaves,
                        "english": _english(env, [names_by_id[c] for c in item["cites"]], conclusion)})
        names_by_id[mid] = item["name"]
    lean_checked = False
    lean_outcome = "not_requested" if lean_executable is None else "not_applicable"
    if lean_executable is not None and data["lemmas"]:
        row = lean_bundle_verdict(lean_executable, env.to_dict(), data["lemmas"], document)
        lean_checked = (row.get("status") == "ok" and
                        row.get("lemmas") == [report["meaning_id"] for report in reports])
        if not lean_checked:
            raise VEError("Lean did not accept every lemma certificate")
        lean_outcome = "accepted"
    return {"status": "Checked", "environment_id": env.environment_id,
            "bundle_id": digest("ve-bundle-v0\n", data), "lemmas": reports,
            "lean_checked": lean_checked, "lean_outcome": lean_outcome}
