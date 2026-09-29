"""Replay rights reporting through the Lean rights route on source units."""
from __future__ import annotations

from pathlib import Path

from .ast import _Checker, _to_data, formula_to_data
from .backends.lean import run_soft_case
from .errors import VEError
from .soft_route import elaborate_soft_document

LEAN_ROUTE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_rights_route"


def _wire(value):
    # The restricted Lean JSON input represents optional null fields by omission.
    if type(value) is dict:
        return {key: _wire(item) for key, item in value.items() if item is not None}
    if type(value) is list:
        return [_wire(item) for item in value]
    return value


def run_rights_case(environment, units, kind, **extra):
    case = {"id": kind, "kind": kind, "environment": _wire(environment.to_dict()),
            "document": _wire(units), **extra}
    return run_soft_case(LEAN_ROUTE, case)


def expected_environment_prime(rights):
    """`E″′` as the Lean route prints it: the source environment with its rights
    block and profiles, plus the generated and soft decision declarations."""
    source = rights.env.to_dict()
    prime = rights.soft_document.extended_env.to_dict()
    prime["profiles"] = source["profiles"]
    prime["vocabulary"]["rights"] = source["vocabulary"]["rights"]
    return _wire(prime)


def check_rights_regenerated(rights, elaborated):
    """Fail closed unless the Lean route's regeneration of the same source is the
    Python correlation: the generated keys, E″′ byte for byte, every line
    instance with its node, Lim_D, the bar nodes and the soft route's layer,
    order, background and targets on T″′. Returns the soft elaboration."""
    soft = elaborate_soft_document(rights.soft_document)
    expected_generated = (
        [{"name": v, "kind": "lim", "limitation": k[0], "act": k[1]}
         for k, v in rights.limitation_names.items()] +
        [{"name": v, "kind": "cond", "limitation": k[0], "act": k[1], "condition": k[2]}
         for k, v in rights.condition_names.items()] +
        [{"name": v, "kind": "aimed", "predicate": k}
         for k, v in rights.bar_names.items()])
    if elaborated["generated"] != expected_generated:
        raise VEError("rights route regeneration mismatch: generated predicates")
    # E″′ is compared whole, generated declarations included: its bytes are the
    # environment every certificate over the regenerated document is bound to.
    if elaborated["environment_prime"] != expected_environment_prime(rights):
        raise VEError("rights route regeneration mismatch: environment")

    def node(rule):
        core = rule.core
        sorts = rights.environment.predicates[core.predicate].arguments

        def open_data(formula):
            _Checker(rights.environment, generated=True).formula(formula, tuple(reversed(sorts)))
            return _to_data(formula)

        return {"name": core.name, "predicate": core.predicate, "sign": core.sign,
                "mode": rule.mode, "guard": open_data(core.guard),
                "unless": [open_data(f) for f in core.unless],
                "over": list(core.over), "hard": rule.hard}

    expected_lines = []
    for instance, rule in zip(rights.instances, rights.soft_document.rules, strict=False):
        row = {"right": instance["right"], "kind": instance["source_kind"],
               "instance": instance["kind"], "rule": rule.core.name,
               "predicate": rule.core.predicate, "holder_slot": instance["holder_slot"],
               "node": node(rule)}
        if instance["bearer"] is not None:
            row.update(bearer=instance["bearer"],
                       source_line=instance["source_line"]["norm"]["name"])
        expected_lines.append(row)
    if elaborated["lines"] != expected_lines:
        raise VEError("rights route regeneration mismatch: lines")
    expected_limitations = [{"label": label,
                             "ast": formula_to_data(rights.environment, formula, _generated=True)}
                            for label, formula in rights.limitation_premises]
    if elaborated["limitations"] != expected_limitations:
        raise VEError("rights route regeneration mismatch: limitation premises")
    expected_bars = [node(rule) for rule in rights.soft_document.rules
                     if rule.core.name.startswith("rights-bar-")]
    if elaborated["bars"] != expected_bars:
        raise VEError("rights route regeneration mismatch: bars")
    if elaborated["rights_background"] != [{"generator": "rights", **item} for item in expected_limitations]:
        raise VEError("rights route regeneration mismatch: rights background")
    for field in ("order", "premises", "derived", "colliding_pairs", "conflict_targets",
                  "warnings", "decisions", "background"):
        if elaborated[field] != soft[field]:
            raise VEError(f"rights route regeneration mismatch: {field}")
    return soft


def report_rights(environment, units, rights):
    """Return the checked five-question rows available without submitted certificates."""
    elaborated = run_rights_case(environment, units, "rights-elaborate")
    check_rights_regenerated(rights, elaborated)
    scope = run_rights_case(environment, units, "rights-scope", certificates={})
    bar = run_rights_case(environment, units, "rights-bar", certificates={})
    conflict = run_rights_case(environment, units, "rights-conflict", packages={})
    return {
        "conflict": {key: conflict[key] for key in ("verdict", "status_text", "targets", "conditional_on")},
        "narrowings": scope["narrowings"],
        "unlicensed_limitations": scope["findings"],
        "distinction": elaborated["distinction"],
        "distinction_hits": elaborated["findings"],
        "bar": bar["bars"],
        "limitation_premises_used": conflict["conditional_on"],
        "decider_note": "No claim is made about the deciders of open terms.",
    }


def admit_rights_document(environment, document, rights):
    """Replay W2 admission on the independently regenerated rights source."""
    source = [{"source_units": [unit["id"] for unit in document["units"]]}] + [
        unit["content"] for unit in document["units"]
        if unit.get("kind") in ("right", "right_lines", "limitation", "bar", "norm")
        and type(unit.get("content")) is dict]
    report_rights(environment, source, rights)
    case = {"id": "admission", "kind": "admission", "environment": environment.to_dict(),
            "document": document}
    row = run_soft_case(LEAN_ROUTE, _wire(case))
    return {key: value for key, value in row.items() if key not in ("id", "status")}
