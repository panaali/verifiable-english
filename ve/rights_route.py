"""Relay rights decisions and reports from the Lean rights route."""
from __future__ import annotations

from collections import Counter
from string import Formatter

from .backends.relay import decide, decide_once
from .ast import decimal_value
from .errors import CheckerUnavailable
from .softnorms import _act_key, bind_soft_elaboration
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
        source_lines = []
        norms = []
        bars = 0
        rule_bar = False
        limit_units = []
        for unit in units:
            if 'norm' in unit:
                norms.append(unit)
            if 'bar' in unit:
                bars += 1
                rule_bar = rule_bar or unit['bar']['reading'] == 'rule'
            if 'limitation' in unit:
                limit_units.append(unit['limitation'])
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
                    fan = line.get('fan_out') or {}
                    counts[name] += len(fan) or 1
                    for bearer in (sorted(fan) if fan else (None,)):
                        source_lines.append((body.get('name', body.get('right')),
                                             line['kind'], name, bearer,
                                             fan[bearer] if bearer is not None else rule['predicate'],
                                             rule, line))

        if not bars and row['bars']:
            raise ValueError('unrequested bar rules')
        seen = Counter()
        correlated = {}
        for line in row['lines']:
            source = line.get('source_line', line['rule'])
            if source not in authored or line['node']['name'] != line['rule'] or line['rule'] in correlated:
                raise ValueError('unbound rights line')
            seen[source] += 1
            correlated[line['rule']] = {**authored[source], 'predicate': line['predicate']}
        if seen != counts:
            raise ValueError('rights line count')
        if len(row['lines']) != len(source_lines):
            raise ValueError('rights source line count')
        for entry, (right, kind, name, bearer, predicate, rule, source_line) in zip(row['lines'], source_lines):
            instance = (('powerLiberty' if source_line['kind'] == 'power' and
                         rule is source_line.get('liberty') else
                         'powerRecognition' if source_line['kind'] == 'power' else kind))
            node = entry['node']
            if (entry['right'] != right or entry['kind'] != kind or
                    entry['instance'] != instance or
                    entry.get('bearer') != bearer or
                    entry.get('source_line', entry['rule']) != name or
                    entry['predicate'] != predicate or node['predicate'] != predicate or
                    any(node[field] != rule.get(field, default) for field, default in
                        (('sign', None), ('hard', False), ('mode', 'strict'), ('over', [])))):
                raise ValueError('unbound rights source line')
        for bar in row['bars']:
            if bar['name'] in correlated or bar['predicate'] not in environment['vocabulary']['predicates']:
                raise ValueError('unbound bar rule')
            correlated[bar['name']] = bar
        predicates = environment['vocabulary']['predicates']
        bind_soft_elaboration(row, norms, predicates, rights_rules=correlated.items(),
                              soft=environment['vocabulary'].get('soft', {}))
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
        expected_acts = {}
        for limit in limit_units:
            acts = set()
            for right, kind, _, _, predicate, _, _ in source_lines:
                if ((limit['scope'] == 'all' or right in limit['scope']) and
                        (limit['kinds'] == 'all' or kind in limit['kinds'])):
                    acts.add(_act_key(predicate, predicates))
            expected_acts[limit['name']] = acts
        expected_limit_labels = {
            f"rights:limitation:{limit['name']}:{act}:{condition['role']}:{condition['name']}"
            for limit in limit_units for act in expected_acts[limit['name']]
            for condition in limit['conditions']}
        if (len(limitation_labels) != len(set(limitation_labels)) or
                set(limitation_labels) != expected_limit_labels or
                row['rights_background'] != [
                    {'generator': 'rights', 'label': entry['label'], 'ast': entry['ast']}
                    for entry in row['limitations']]):
            raise ValueError('duplicate or unmatched limitation premise')
        generated_names = set()
        generated_keys = set()
        prime_predicates = row['environment_prime']['vocabulary']['predicates']
        if row['environment_prime']['profiles'] != environment['profiles']:
            raise ValueError('unbound rights prime profiles')
        expected_lim = sorted((name, act) for name, acts in expected_acts.items() for act in acts)
        expected_cond = sorted((limit['name'], act, condition['name'])
                               for limit in limit_units for act in expected_acts[limit['name']]
                               for condition in limit['conditions'])
        permission_lines = {entry['predicate'] for entry in row['lines']
                            if entry['instance'] in ('liberty', 'powerLiberty')}
        expected_aimed = sorted(permission_lines) if bars else []
        expected_generated = ({('lim', limit, act, None): f'rights__lim__{i}'
                               for i, (limit, act) in enumerate(expected_lim, 1)} |
                              {('cond', limit, act, condition): f'rights__cond__{i}'
                               for i, (limit, act, condition) in enumerate(expected_cond, 1)} |
                              {('aimed', predicate): f'rights__bar__{i}'
                               for i, predicate in enumerate(expected_aimed, 1)})
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
            if expected_generated.get(key) != name or prime_predicates[name]['arguments'] != predicates[
                    entry['predicate'] if kind == 'aimed' else entry['act']]['arguments']:
                raise ValueError('unbound generated name or sorts')
        if generated_keys != set(expected_generated):
            raise ValueError('missing or extra generated predicate')
        original = environment['vocabulary']['predicates']
        decisions = {item['name'] for item in row['decisions']}
        if set(prime_predicates) != set(original) | generated_names | decisions or any(
                prime_predicates[name] != declaration for name, declaration in original.items()):
            raise ValueError('unbound rights prime vocabulary')
        if set(row['wordings']) != generated_names:
            raise ValueError('unbound generated wording')
        for name, wording in row['wordings'].items():
            arity = len(prime_predicates[name]['arguments'])
            for _, field, spec, conversion in Formatter().parse(wording):
                if field is not None and (not field.isascii() or not field.isdecimal() or
                                           decimal_value(field) >= arity or spec or conversion):
                    raise ValueError('invalid generated wording placeholder')
        aimed = Counter(entry['predicate'] for entry in row['generated']
                        if entry['kind'] == 'aimed')
        bar_nodes = Counter(entry['predicate'] for entry in row['bars'])
        if bar_nodes != (aimed if rule_bar else Counter()):
            raise ValueError('unbound bar nodes')
        positive_lines = {entry['rule'] for entry in row['lines'] if entry['node']['sign']}
        if any(len(entry['over']) != len(set(entry['over'])) or
               not set(entry['over']) <= positive_lines or
               any(line['predicate'] != entry['predicate'] for line in row['lines']
                   if line['rule'] in entry['over']) for entry in row['bars']):
            raise ValueError('unbound bar over rule')
        line_pairs = Counter((line['right'], line['rule']) for line in row['lines'])
        narrowing_pairs = Counter((entry['right'], entry['rule']) for entry in row['narrowings'])
        if narrowing_pairs != line_pairs:
            raise ValueError('unbound narrowing line')
        for entry in row['narrowings']:
            targets = [mechanism['target'] for mechanism in entry['mechanisms']]
            line = next(line for line in row['lines'] if line['rule'] == entry['rule'])
            rule = correlated[entry['rule']]
            allowed_rules = set(correlated) | {unit['norm']['name'] for unit in norms}
            def valid_mechanism(text):
                if text in ('limitation', 'exception', 'bar'):
                    return True
                if text.startswith('carve-out '):
                    index = text.removeprefix('carve-out ')
                    return (index.isascii() and index.isdecimal() and
                            1 <= decimal_value(index) <= len(rule.get('unless', [])))
                if text.startswith('switch '):
                    return text.removeprefix('switch ') in rule.get('alterable', [])
                for prefix in ('blockedBy ', 'dominatedBy ', 'exception '):
                    if text.startswith(prefix):
                        return text.removeprefix(prefix) in allowed_rules
                return False
            if (len(targets) != len(set(targets)) or
                    any(mechanism['target'] != f"{entry['rule']}:{mechanism['mechanism']}" or
                        not valid_mechanism(mechanism['mechanism']) for mechanism in entry['mechanisms'])):
                raise ValueError('unbound narrowing target')
            required = {f'carve-out {index}' for index in range(1, len(rule.get('unless', [])) + 1)}
            required.update(f'switch {party}' for party in rule.get('alterable', []))
            if rule.get('mode', 'strict') == 'default':
                required.add('exception')
            if any((limit['scope'] == 'all' or entry['right'] in limit['scope']) and
                   (limit['kinds'] == 'all' or line['kind'] in limit['kinds']) for limit in limit_units):
                required.add('limitation')
            if not required <= {mechanism['mechanism'] for mechanism in entry['mechanisms']}:
                raise ValueError('missing request-implied mechanism')
        distinction_predicates = {line['predicate'] for line in row['lines']}
        reported_predicates = [entry['predicate'] for entry in row['distinction']]
        if (len(reported_predicates) != len(set(reported_predicates)) or
                set(reported_predicates) != distinction_predicates):
            raise ValueError('missing or extra distinction row')
        protected = set(environment['vocabulary']['rights'].get('protected', []))
        for entry in row['distinction']:
            hits = [(hit['right'], hit['rule'], hit['protected']) for hit in entry['hits']]
            if (len(hits) != len(set(hits)) or
                    any((right, rule) not in line_pairs or name not in protected
                        for right, rule, name in hits)):
                raise ValueError('unbound distinction hit')
        expected_findings = [f"ProtectedInCone: {hit['protected']} in rule {hit['rule']} on right {hit['right']}"
                             for entry in row['distinction'] if not entry['independent']
                             for hit in entry['hits'] if not hit['cited']]
        if row['findings'] != expected_findings:
            raise ValueError('unbound distinction findings')
        conditional = row['conditional_on']
        pair_labels = {entry['label'] for entry in row['colliding_pairs']}
        open_labels = {entry['label'] for entry in row['colliding_pairs'] if not entry['comparable']}
        if len(conditional) != len(set(conditional)) or set(conditional) != open_labels:
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
        if row['verdict'] == 'CONFLICT-FREE':
            coherence = sum(label.startswith('soft:') for label in conditional)
            limitation = sum(label.startswith('rights:') for label in conditional)
            expected = (f'CONFLICT-FREE among rules on the same act, conditional on {coherence} '
                        f'coherence premises and {limitation} limitation premises')
            if row['status_text'] != expected:
                raise ValueError('unbound conflict status text')
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(
            f'CheckerUnavailable: Lean rights conflict is not bound to the request: {error}') from error


def _bind_narrowings(row, elaborated, *, empty_certificates=False):
    """Bind each reported line and mechanism to the checked elaboration."""
    try:
        def identities(rows):
            return [(entry['right'], entry['rule'],
                     [(mechanism['mechanism'], mechanism['target'])
                      for mechanism in entry['mechanisms']]) for entry in rows]

        if identities(row['narrowings']) != identities(elaborated['narrowings']):
            raise ValueError('missing or extra narrowing line or mechanism')
        expected_findings = []
        for actual, source in zip(row['narrowings'], elaborated['narrowings']):
            if actual['in_scope'] != source['in_scope']:
                raise ValueError('unbound scope choice')
            for mechanism in actual['mechanisms']:
                licence = mechanism['licence']
                text = mechanism['mechanism']
                fixed = ('limitation' if text == 'limitation' else 'bar' if text == 'bar' else None)
                if (licence not in (None, 'limitation', 'bar', 'cited', 'collision', 'certified') and
                        not (text.startswith('blockedBy ') and
                                 licence == 'effect delivered by strict rule ' + text.removeprefix('blockedBy '))):
                    raise ValueError('unbound mechanism licence')
                if fixed is not None and licence != fixed:
                    raise ValueError('unbound fixed mechanism licence')
                if empty_certificates and licence == 'certified':
                    raise ValueError('unrequested certificate licence')
                if actual['in_scope'] and licence is None:
                    expected_findings.append(
                        f"UnlicensedLimitation: {text} of rule {actual['rule']} on right {actual['right']}")
        if row['findings'] != expected_findings or row['licensed'] != (not expected_findings):
            raise ValueError('unbound scope findings or licence result')
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(
            f'CheckerUnavailable: Lean rights narrowings are not bound to the request: {error}') from error


def _bind_bar(row, elaborated, units):
    """Bind bar identities and references to the authored source."""
    try:
        readings = {unit['bar']['reading'] for unit in units if 'bar' in unit}
        aimed = [(entry['predicate'], entry['name']) for entry in elaborated['generated']
                 if entry['kind'] == 'aimed']
        rows = row['bars']
        if (len(readings) > 1 or
                [(entry['predicate'], entry['aimed']) for entry in rows] != aimed or
                any(entry['reading'] not in readings for entry in rows)):
            raise ValueError('missing or extra bar row')
        line_rules = {entry['rule']: entry['node'] for entry in elaborated['lines']}
        derived_rules = {entry['rule'] for entry in elaborated['derived']}
        all_rules = dict(line_rules)
        all_rules.update({unit['norm']['name']: unit['norm'] for unit in units if 'norm' in unit})
        for entry in rows:
            if entry['reading'] == 'rule':
                predicate = entry['predicate']
                for field, allowed in (
                        ('barred', {name for name, rule in line_rules.items()
                                    if rule['predicate'] == predicate and rule['sign']}),
                        ('blocked_defaults', {name for name, rule in all_rules.items()
                                              if rule.get('mode', 'strict') == 'default'}),
                        ('composition_candidates', {name for name, rule in all_rules.items()
                                                    if rule.get('mode', 'strict') == 'strict' and rule['sign']})):
                    names = entry[field]
                    if len(names) != len(set(names)) or not set(names) <= allowed:
                        raise ValueError(f'unbound bar {field}')
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(
            f'CheckerUnavailable: Lean rights bar is not bound to the request: {error}') from error


def _run_rights_case(environment, units, kind, extra, elaborated=None):
    raw = environment.to_dict()
    # readings@1 is a head profile. Its lower rights chain is checked with
    # that profile removed, as the readings route does for each choice.
    raw["profiles"] = [p for p in raw["profiles"] if p != "readings@1"]
    case = {"id": kind, "kind": kind, "environment": _wire(raw),
            "document": _wire(units), **extra}
    row = decide_once("rights", case)
    if kind == 'rights-elaborate':
        _bind_elaboration(row, units, raw)
    elif kind in ('rights-scope', 'rights-bar'):
        elaborated = elaborated or run_rights_case(environment, units, 'rights-elaborate')
        if kind == 'rights-scope':
            _bind_narrowings(row, elaborated, empty_certificates=not extra.get('certificates'))
        else:
            _bind_bar(row, elaborated, units)
    elif kind == 'rights-conflict' and 'witness' not in extra:
        elaborated = run_rights_case(environment, units, 'rights-elaborate')
        _bind_conflict(row, elaborated)
    return row


def run_rights_case(environment, units, kind, **extra):
    return _run_rights_case(environment, units, kind, extra)


def expected_environment_prime(rights):
    """The full environment identity preimage supplied by the Lean owner."""
    return rights.elaborated["environment_prime"]


def report_rights(environment, units, rights=None, *, _with_elaboration=False):
    """Return the five-question rows available without submitted certificates."""
    elaborated = run_rights_case(environment, units, "rights-elaborate")
    scope = _run_rights_case(environment, units, "rights-scope", {"certificates": {}}, elaborated)
    bar = _run_rights_case(environment, units, "rights-bar", {"certificates": {}}, elaborated)
    conflict = run_rights_case(environment, units, "rights-conflict", packages={})
    report = {
        "conflict": {key: conflict[key] for key in ("verdict", "status_text", "targets", "conditional_on")},
        "narrowings": scope["narrowings"],
        "unlicensed_limitations": scope["findings"],
        "distinction": elaborated["distinction"],
        "distinction_hits": elaborated["findings"],
        "bar": bar["bars"],
        "limitation_premises_used": conflict["conditional_on"],
        "decider_note": "No claim is made about the deciders of open terms.",
    }
    return (report, elaborated) if _with_elaboration else report


def admit_rights_document(environment, document, rights=None):
    """Replay W2 admission on the Lean-validated rights source."""
    source = [{"source_units": [unit["id"] for unit in document["units"]]}] + [
        unit["content"] for unit in document["units"]
        if unit.get("kind") in ("right", "right_lines", "limitation", "bar", "norm")
        and type(unit.get("content")) is dict]
    _, elaborated = report_rights(environment, source, rights, _with_elaboration=True)
    case = {"id": "admission", "kind": "admission", "environment": environment.to_dict(),
            "document": document}
    row = decide("rights", [_wire(case)])[0]
    try:
        labels = (elaborated['conditional_on'] +
                  [entry['label'] for entry in elaborated['limitations']])
        reported = {assumption.get('label') for assumption in row['report']['assumptions']}
        if row['conditional_on'] != [label for label in labels if label in reported]:
            raise ValueError('unbound rights admission conditional labels')
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(f'CheckerUnavailable: Lean rights admission is not bound to the request: {error}') from error
    return {key: value for key, value in row.items() if key not in ("id", "status")}
