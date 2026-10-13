"""Relay rights decisions and reports from the Lean rights route."""
from __future__ import annotations

from collections import Counter

from .backends.relay import decide, decide_once
from .errors import CheckerUnavailable
from .softnorms import bind_soft_elaboration
from .rights import LINE_RULE_FIELDS

def _wire(value):
    # The restricted Lean JSON input represents optional null fields by omission.
    if type(value) is dict:
        return {key: _wire(item) for key, item in value.items() if item is not None}
    if type(value) is list:
        return [_wire(item) for item in value]
    return value


def _bind_elaboration(row, units, environment):
    """Bind correlated soft rule IDs to the authored rights lines and norm units."""
    try:
        authored = {}
        counts = Counter()
        norms = []
        bars = 0
        for unit in units:
            if 'norm' in unit:
                norms.append(unit)
            if 'bar' in unit:
                bars += 1
            body = unit.get('right', unit.get('right_lines'))
            if body is None:
                continue
            for line in body['lines']:
                for field in LINE_RULE_FIELDS[line['kind']]:
                    rule = line[field]
                    name = rule['name']
                    if name in authored:
                        raise ValueError('duplicate authored rule')
                    authored[name] = rule
                    counts[name] += len(line.get('fan_out') or ()) or 1

        if not bars and row['bars']:
            raise ValueError('unrequested bar rules')
        seen = Counter()
        correlated = {}
        for line in row['lines']:
            source = line.get('source_line', line['rule'])
            if source not in authored or line['node']['name'] != line['rule'] or line['rule'] in correlated:
                raise ValueError('unbound rights line')
            seen[source] += 1
            correlated[line['rule']] = authored[source]
        if seen != counts:
            raise ValueError('rights line count')
        for bar in row['bars']:
            if bar['name'] in correlated or bar['predicate'] not in environment['vocabulary']['predicates']:
                raise ValueError('unbound bar rule')
            correlated[bar['name']] = bar
        predicates = row['environment_prime']['vocabulary']['predicates']
        bind_soft_elaboration(row, norms, predicates, rights_rules=correlated.items())
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(f'CheckerUnavailable: Lean rights elaboration is not bound to the request: {error}') from error


def run_rights_case(environment, units, kind, **extra):
    raw = environment.to_dict()
    # readings@1 is a head profile. Its lower rights chain is checked with
    # that profile removed, as the readings route does for each choice.
    raw["profiles"] = [p for p in raw["profiles"] if p != "readings@1"]
    case = {"id": kind, "kind": kind, "environment": _wire(raw),
            "document": _wire(units), **extra}
    row = decide_once("rights", case)
    if kind == 'rights-elaborate':
        _bind_elaboration(row, units, raw)
    return row


def expected_environment_prime(rights):
    """The full environment identity preimage supplied by the Lean owner."""
    return rights.elaborated["environment_prime"]


def report_rights(environment, units, rights=None):
    """Return the five-question rows available without submitted certificates."""
    elaborated = run_rights_case(environment, units, "rights-elaborate")
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


def admit_rights_document(environment, document, rights=None):
    """Replay W2 admission on the Lean-validated rights source."""
    source = [{"source_units": [unit["id"] for unit in document["units"]]}] + [
        unit["content"] for unit in document["units"]
        if unit.get("kind") in ("right", "right_lines", "limitation", "bar", "norm")
        and type(unit.get("content")) is dict]
    report_rights(environment, source, rights)
    case = {"id": "admission", "kind": "admission", "environment": environment.to_dict(),
            "document": document}
    row = decide("rights", [_wire(case)])[0]
    return {key: value for key, value in row.items() if key not in ("id", "status")}
