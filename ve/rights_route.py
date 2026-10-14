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
        right_names = set()
        counts = Counter()
        source_lines = []
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
            right_names.add(body.get('name', body.get('right')))
            for line in body['lines']:
                for field in LINE_RULE_FIELDS[line['kind']]:
                    rule = line[field]
                    name = rule['name']
                    if name in authored:
                        raise ValueError('duplicate authored rule')
                    authored[name] = rule
                    fan = line.get('fan_out') or {}
                    counts[name] += len(fan) or 1
                    for bearer in (sorted(fan) if fan else (None,)):
                        source_lines.append((body.get('name', body.get('right')),
                                             line['kind'], name, bearer,
                                             fan[bearer] if bearer is not None else rule['predicate']))

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
        if len(row['lines']) != len(source_lines):
            raise ValueError('rights source line count')
        for entry, (right, kind, name, bearer, predicate) in zip(row['lines'], source_lines):
            if (entry['right'] != right or entry['kind'] != kind or
                    entry.get('bearer') != bearer or
                    entry.get('source_line', entry['rule']) != name or
                    entry['predicate'] != predicate or entry['node']['predicate'] != predicate):
                raise ValueError('unbound rights source line')
        for bar in row['bars']:
            if bar['name'] in correlated or bar['predicate'] not in environment['vocabulary']['predicates']:
                raise ValueError('unbound bar rule')
            correlated[bar['name']] = bar
        predicates = environment['vocabulary']['predicates']
        bind_soft_elaboration(row, norms, predicates, rights_rules=correlated.items())
        limits = {unit['limitation']['name']: unit['limitation'] for unit in units
                  if 'limitation' in unit}
        limitation_labels = []
        for entry in row['limitations']:
            label = entry['label']
            parts = label.split(':', 5)
            if (len(parts) != 6 or parts[:2] != ['rights', 'limitation'] or
                    parts[2] not in limits or parts[3] not in environment['vocabulary']['predicates'] or
                    parts[4] not in ('necessary', 'sufficient') or
                    not any(condition['name'] == parts[5] and condition['role'] == parts[4]
                            for condition in limits[parts[2]]['conditions'])):
                raise ValueError('unbound limitation premise')
            limitation_labels.append(label)
        if (len(limitation_labels) != len(set(limitation_labels)) or
                row['rights_background'] != [
                    {'generator': 'rights', 'label': entry['label'], 'ast': entry['ast']}
                    for entry in row['limitations']]):
            raise ValueError('duplicate or unmatched limitation premise')
        generated_names = set()
        generated_keys = set()
        prime_predicates = row['environment_prime']['vocabulary']['predicates']
        for entry in row['generated']:
            name, kind = entry['name'], entry['kind']
            if name in generated_names or name not in prime_predicates:
                raise ValueError('duplicate or missing generated declaration')
            generated_names.add(name)
            if kind in ('lim', 'cond'):
                limit, act = entry['limitation'], entry['act']
                if limit not in limits or act not in environment['vocabulary']['predicates']:
                    raise ValueError('unbound generated limitation')
                condition = entry.get('condition')
                if kind == 'cond' and not any(c['name'] == condition for c in limits[limit]['conditions']):
                    raise ValueError('unbound generated condition')
                key = (kind, limit, act, condition)
            else:
                if not bars or entry['predicate'] not in environment['vocabulary']['predicates']:
                    raise ValueError('unbound generated bar')
                key = (kind, entry['predicate'])
            if key in generated_keys:
                raise ValueError('duplicate generated source key')
            generated_keys.add(key)
        if set(row['wordings']) != generated_names:
            raise ValueError('unbound generated wording')
        line_pairs = Counter((line['right'], line['rule']) for line in row['lines'])
        narrowing_pairs = Counter((entry['right'], entry['rule']) for entry in row['narrowings'])
        if narrowing_pairs != line_pairs:
            raise ValueError('unbound narrowing line')
        for entry in row['narrowings']:
            targets = [mechanism['target'] for mechanism in entry['mechanisms']]
            if (len(targets) != len(set(targets)) or
                    any(not target.startswith(entry['rule'] + ':') for target in targets)):
                raise ValueError('unbound narrowing target')
        for entry in row['distinction']:
            if entry['predicate'] not in environment['vocabulary']['predicates']:
                raise ValueError('unbound distinction predicate')
            if any((hit['right'], hit['rule']) not in line_pairs
                   for hit in entry['hits']):
                raise ValueError('unbound distinction hit')
        conditional = row['conditional_on']
        pair_labels = {entry['label'] for entry in row['colliding_pairs']}
        if len(conditional) != len(set(conditional)) or not set(conditional) <= pair_labels:
            raise ValueError('unbound soft coherence premise')
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(f'CheckerUnavailable: Lean rights elaboration is not bound to the request: {error}') from error


def _bind_conflict(row, elaborated):
    """Bind the conflict's displayed identities to the elaborated source."""
    try:
        targets = [entry['target'] for entry in elaborated['conflict_targets']]
        labels = {entry['label'] for entry in elaborated['colliding_pairs']}
        labels.update(entry['label'] for entry in elaborated['limitations'])
        conditional = row['conditional_on']
        if (row['targets'] != targets or len(targets) != len(set(targets)) or
                len(conditional) != len(set(conditional)) or not set(conditional) <= labels):
            raise ValueError('unbound conflict target or conditional premise')
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(
            f'CheckerUnavailable: Lean rights conflict is not bound to the request: {error}') from error


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
    elif kind == 'rights-conflict' and 'witness' not in extra:
        elaborated = run_rights_case(environment, units, 'rights-elaborate')
        _bind_conflict(row, elaborated)
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
