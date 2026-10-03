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

    Raises `CheckerUnavailable` when Lean gives no well-formed answer (an `ok`
    row must carry `lemmas`, one meaning-ID string per submitted lemma, and
    `checked`, their count); a returned row with `status: error` is Lean's
    rejection.
    """
    case = [{"id": "bundle", "kind": "bundle", "environment": environment, "lemmas": lemmas,
             **({} if document is None else {"document": document})}]
    return lean_backend.run("bundle.check", lean_executable, case, runner="ve_conformance",
                            mode="route", timeout=lean_backend.configured_timeout(LEAN_REPLAY_TIMEOUT))[0]


def _lean_bundle_mode(data) -> str | None:
    """The Lean service mode that checks the bundle `data`, or None.

    `route` (the route's bundle case, `VE.Definitions.Bundle`, `bundle_sound`)
    takes FOL-family ve.core@0.2 environments without norm declarations or
    statement layers. `bundle` (`VE.Service.FamilyBundle`) takes every other
    ve.core@0.2 environment of any family (`validation.family_in_scope`),
    norms environments included, and the frozen v0 and v0.1 envelopes."""
    from .backends.validation import LEGACY_LANGUAGES, family_in_scope
    environment = data.get("environment") if type(data) is dict else None
    if type(environment) is dict and environment.get("language") in LEGACY_LANGUAGES:
        return "bundle"
    if type(environment) is not dict or environment.get("language") != "ve.core@0.2":
        return None
    if {"unit_schema", "units", "alternatives", "speech_acts"} & set(environment):
        return None
    try:
        env = Environment(environment)
    except VEError:
        return None
    if not family_in_scope(env):
        return None
    if env.closure or env.order or any(d.regulated is not None for d in env.predicates.values()):
        return "bundle"
    return "route"


@semantic_entry("bundle.check")
def check_bundle(data, *, lean_executable=None):
    """Replay a lemma bundle; with `lean_executable`, Lean must also accept it.

    `lean_outcome` is `accepted`, `not_requested`, or `not_applicable` (no
    lemmas). A Lean rejection raises `VEError`; Lean giving no answer raises
    `CheckerUnavailable`, which is operational and never a verdict.

    Under a backend authority the bundle's acceptance is Lean's route bundle
    verdict (`bundle_sound`); the report (leaves, reading choices, English) is
    built by the Python walk, which also names a rejection both make.
    """
    from .backends.dispatch import authority_for, execute

    def python():
        return _check_bundle_python(data, lean_executable=lean_executable)

    if authority_for("bundle") in ("python", "rust-experimental"):
        return python()
    mode = _lean_bundle_mode(data)
    if mode is None:
        return python()
    return execute("bundle", {"kind": "bundle"}, python,
                   lean=lambda: _explicit_lean(_check_bundle_lean(data, mode), data, lean_executable))


def _check_bundle_lean(data, mode="route"):
    from .backends.lean_runner import run
    from .backends.validation import decided, key
    _bundle_container(data)
    case = {"id": "bundle", **({"kind": "bundle"} if mode == "route" else {}),
            "environment": data["environment"],
            "lemmas": data.get("lemmas"), **({"document": data["document"]} if "document" in data else {})}
    try:
        cache = key("bundle", data)
    except (VEError, TypeError, ValueError, RecursionError):
        cache = None
    return decided(lambda: _check_bundle_python(data), cache, lambda: run(mode, [case])[0],
                   lambda report, row: row.get("lemmas") == [r["meaning_id"] for r in report["lemmas"]],
                   "a bundle")


def _bundle_container(data) -> None:
    """The bundle file format: fields, version and lemma array (structural)."""
    require_fields(data, {"version", "environment", "lemmas"} |
                   ({"document"} if type(data) is dict and "document" in data else set()))
    if data["version"] != "ve-bundle@0" or type(data["lemmas"]) is not list:
        raise VEError("Unsupported lemma bundle version or lemmas array")
    if len(data["lemmas"]) > 256:
        raise ResourceLimit("Lemma bundle exceeds 256 lemmas")


def _check_bundle_python(data, *, lean_executable=None):
    _bundle_container(data)
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
    report = {"status": "Checked", "environment_id": env.environment_id,
              "bundle_id": digest("ve-bundle-v0\n", data), "lemmas": reports,
              "lean_checked": False, "lean_outcome": "not_requested"}
    return _explicit_lean(report, data, lean_executable)


def _explicit_lean(report, data, lean_executable):
    """The caller's optional second check by the one-shot Lean runner."""
    if lean_executable is None:
        return report
    report = {**report, "lean_outcome": "not_applicable"}
    if data["lemmas"]:
        document = data.get("document", {"reading_sets": []})
        row = lean_bundle_verdict(lean_executable, Environment(data["environment"]).to_dict(),
                                  data["lemmas"], document)
        if not (row.get("status") == "ok" and
                row.get("lemmas") == [lemma["meaning_id"] for lemma in report["lemmas"]]):
            raise VEError("Lean did not accept every lemma certificate")
        report = {**report, "lean_checked": True, "lean_outcome": "accepted"}
    return report
