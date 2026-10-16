"""Relay rights decisions and reports from the Lean rights route."""
from __future__ import annotations

from collections import Counter
from string import Formatter

from .backends.relay import decide, decide_once
from .backends.service_schema import same_json
from .ast import decimal_value
from .errors import CheckerUnavailable
from .softnorms import _act_key, bind_prime_environment, bind_soft_elaboration
from .rights import LINE_RULE_FIELDS

def _wire(value):
    # The restricted Lean JSON input represents optional null fields by omission.
    if type(value) is dict:
        return {key: _wire(item) for key, item in value.items() if item is not None}
    if type(value) is list:
        return [_wire(item) for item in value]
    return value


# Scope.lean `mechText`, in the order Correlate.lean `narrowings` lists the slots: a slot that names a
# request item (a carve-out's number, a rule, a party) names it after the first space.
_NAMED_SLOTS = ('carve-out', 'exception', None, None, 'switch', 'blockedBy', 'dominatedBy', None)
_FIXED_SLOTS = {'limitation': 2, 'exception': 3, 'bar': 7}
_RULE_SLOTS = ('exception', 'blockedBy', 'dominatedBy')


def _slot(text):
    """A mechanism's slot `(order, kind, name)` read off its wire text, or ValueError."""
    if text in _FIXED_SLOTS:
        return _FIXED_SLOTS[text], text if text != 'exception' else 'excepted', None
    kind, space, name = text.partition(' ')
    if not space or not name or kind not in _NAMED_SLOTS:
        raise ValueError('unknown narrowing mechanism')
    if kind == 'carve-out' and not (name.isascii() and name.isdecimal() and name[0] != '0'):
        raise ValueError('non-canonical carve-out number')
    return _NAMED_SLOTS.index(kind), kind, name


def _bind_line_narrowings(entry, rule, *, limits, direct, line_rules, cites, aimed):
    """Bind one line's elaborated narrowings to the request (R8(b)); Lean chose them (Correlate.lean
    `narrowings`) and their licences (Run.lean `licence`, `licence_spec`).

    Each mechanism names a slot the request holds: an authored carve-out, a declared rule other than
    the line's own, a party the rule lets switch, the rule's own exception when it is a default rule,
    the limitations Lean lists in scope, the bar Lean finds reaching the line (`bar_mem_narrowings`,
    `limPack_mem_narrowings`). Every slot the request fixes is listed once, in Lean's order; a
    rule-named slot is listed where Lean's `rule_narrowings` row of that rule lists it. A licence names
    its grounds: the citation, which the request holds (`citedBy_sound`), the colliding right line or
    the strict rule, each the mechanism's own rule (`ground_collision`, `ground_effect`)."""
    own, default = entry['rule'], rule.get('mode', 'strict') == 'default'
    names = entry['limitations']
    if (len(names) != len(set(names)) or names != [name for name in limits if name in names] or
            entry['in_scope'] is not bool(names) or
            (entry['bar'] is not None and entry['bar'] not in aimed)):
        raise ValueError('unbound narrowing scope or bar')
    slots, seen = [], set()
    for mechanism in entry['mechanisms']:
        order, kind, name = _slot(mechanism['mechanism'])
        if mechanism['target'] != f"{own}:{mechanism['mechanism']}":
            raise ValueError('unbound narrowing target')
        position = (decimal_value(name) if kind == 'carve-out' else
                    name if kind == 'exception' else
                    (rule.get('alterable') or []).index(name) if kind == 'switch' and
                    name in (rule.get('alterable') or []) else
                    direct.index(name) if kind in _RULE_SLOTS and name in direct else 0)
        if ((kind == 'carve-out' and not 1 <= position <= len(rule.get('unless') or [])) or
                (kind in _RULE_SLOTS and (name not in direct or name == own)) or
                (kind == 'switch' and name not in (rule.get('alterable') or [])) or
                (kind in ('excepted', 'blockedBy', 'dominatedBy') and not default) or
                (kind == 'limitation' and not entry['in_scope']) or (kind == 'bar' and entry['bar'] is None)):
            raise ValueError('unbound narrowing mechanism')
        slots.append((order, position))
        seen.add(kind)
        licence, grounds = mechanism['licence'], mechanism['grounds']
        if kind in ('limitation', 'bar'):
            bound = licence == kind and grounds is None
        elif licence is None:
            bound = grounds is None
        elif licence == 'cited':
            citation = (grounds or {}).get('citation') or {}
            bound = set(grounds or {}) == {'citation'} and citation.get('key') in cites.get(citation.get('rule'), {})
        elif licence == 'collision':
            bound = kind in ('blockedBy', 'dominatedBy') and grounds == {'line': name} and name in line_rules
        else:
            bound = (kind == 'blockedBy' and grounds == {'rule': name} and
                     licence == f'effect delivered by strict rule {name}')
        if not bound:
            raise ValueError('unbound mechanism licence or grounds')
    if (slots != sorted(set(slots)) or
            [p for o, p in slots if o == 0] != list(range(1, len(rule.get('unless') or []) + 1)) or
            [p for o, p in slots if o == 4] != list(range(len(rule.get('alterable') or []))) or
            ('excepted' in seen) is not default or ('limitation' in seen) is not entry['in_scope'] or
            ('bar' in seen) is not (entry['bar'] is not None)):
        raise ValueError('missing, repeated or reordered narrowing mechanism')


# Correlate.lean `barNode`: every bar rule is strict, hard and negative, with no carve-out.
BAR_NODE = {'sign': False, 'hard': True, 'mode': 'strict', 'unless': []}


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
        fan_instances = 0
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
                        # Tree.lean `instancesOf`: the k-th fan-out instance in
                        # document order is named `rights-fan-<k>`.
                        if bearer is not None:
                            fan_instances += 1
                        source_lines.append((body.get('name', body.get('right')),
                                             line['kind'], name, bearer,
                                             fan[bearer] if bearer is not None else rule['predicate'],
                                             rule, line,
                                             name if bearer is None else f'rights-fan-{fan_instances}'))

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
        # Run.lean `elaboratedNarrowingsJson`: one row per line instance, in the lines' order.
        if [(entry['right'], entry['rule']) for entry in row['narrowings']] != [
                (line['right'], line['rule']) for line in row['lines']]:
            raise ValueError('unbound narrowing line')
        holders = {unit['right']['name']: unit['right']['holder'] for unit in units if 'right' in unit}
        # Scope.lean `citesOf`: a line instance's source citations, else an outside norm unit's.
        cites = {unit['norm']['name']: unit.get('cites') or {} for unit in norms}
        line_rules = set()
        predicates = environment['vocabulary']['predicates']
        for entry, scoped, (right, kind, name, bearer, predicate, rule, source_line, rule_id) in zip(
                row['lines'], row['narrowings'], source_lines):
            instance = (('powerLiberty' if source_line['kind'] == 'power' and
                         rule is source_line.get('liberty') else
                         'powerRecognition' if source_line['kind'] == 'power' else kind))
            # Tree.lean `holderSlot`: the subject slot of a liberty half, else the authored
            # `holder_slot`, else the first object slot of the right's holder sort.
            objects = predicates[predicate]['arguments'][1:]
            holder_slot = (0 if instance in ('liberty', 'powerLiberty') else
                           source_line['holder_slot'] if source_line.get('holder_slot') is not None else
                           1 if right not in holders else
                           (objects.index(holders[right]) if holders[right] in objects else len(objects)) + 1)
            node = entry['node']
            cites[rule_id] = source_line.get('cites') or {}
            line_rules.add(rule_id)
            if (entry['right'] != right or entry['kind'] != kind or
                    entry['instance'] != instance or
                    type(entry['holder_slot']) is not int or entry['holder_slot'] != holder_slot or
                    entry.get('bearer') != bearer or
                    entry['rule'] != rule_id or
                    entry.get('source_line', entry['rule']) != name or
                    entry['predicate'] != predicate or node['predicate'] != predicate or
                    any(node[field] != rule.get(field, default) for field, default in
                        (('sign', None), ('hard', False), ('mode', 'strict'), ('over', []))) or
                    # Correlate.lean `nodeOf`: the authored carve-outs, then the limitation pack when Lean
                    # finds a limitation in scope (the line's narrowing row).
                    len(node['unless']) != len(rule.get('unless') or []) + (scoped['in_scope'] is True) or
                    not same_json(node['unless'][:len(rule.get('unless') or [])], rule.get('unless') or [])):
                raise ValueError('unbound rights source line')
        for bar in row['bars']:
            if (bar['name'] in correlated or bar['predicate'] not in environment['vocabulary']['predicates'] or
                    any(bar[field] != value for field, value in BAR_NODE.items())):
                raise ValueError('unbound bar rule')
            correlated[bar['name']] = bar
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
        # Tree.lean `limActs`: the act keys of the lines each limitation scopes, as Lean lists them.
        expected_acts = {limit['name']: set() for limit in limit_units}
        for scoped, line in zip(row['narrowings'], row['lines']):
            for name in scoped['limitations']:
                expected_acts[name].add(_act_key(line['predicate'], predicates))
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
        expected_lim = sorted((name, act) for name, acts in expected_acts.items() for act in acts)
        expected_cond = sorted((limit['name'], act, condition['name'])
                               for limit in limit_units for act in expected_acts[limit['name']]
                               for condition in limit['conditions'])
        permission_lines = {entry['predicate'] for entry in row['lines']
                            if entry['instance'] in ('liberty', 'powerLiberty')}
        aimed_index = {predicate: i for i, predicate in
                       enumerate(sorted(permission_lines) if bars else [], 1)}
        expected_generated = ({('lim', limit, act, None): f'rights__lim__{i}'
                               for i, (limit, act) in enumerate(expected_lim, 1)} |
                              {('cond', limit, act, condition): f'rights__cond__{i}'
                               for i, (limit, act, condition) in enumerate(expected_cond, 1)} |
                              {('aimed', predicate): f'rights__bar__{i}'
                               for predicate, i in aimed_index.items()})
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
        bind_prime_environment(row, environment, generated_names)
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
        if bar_nodes != (aimed if rule_bar else Counter()) or any(
                entry['name'] != f"rights-bar-{aimed_index[entry['predicate']]}" for entry in row['bars']):
            raise ValueError('unbound bar nodes')
        if any(entry['over'] != [line['rule'] for line in row['lines']
                                 if line['predicate'] == entry['predicate'] and line['node']['sign']]
               for entry in row['bars']):
            raise ValueError('unbound bar over rule')
        line_pairs = Counter((line['right'], line['rule']) for line in row['lines'])
        # `directNodes` (Correlate.lean): the line instances, then the norm units, without bars; per rule,
        # Lean's `rule_narrowings` row lists its source's citations in key order (`citesOf`).
        direct = [line['rule'] for line in row['lines']] + [unit['norm']['name'] for unit in norms]
        rows = row['rule_narrowings']
        if ([entry['rule'] for entry in rows] != direct or
                any([citation['key'] for citation in entry['citations']] != sorted(cites.get(entry['rule'], {}))
                    for entry in rows)):
            raise ValueError('unbound rule narrowing row')
        for entry, line in zip(row['narrowings'], row['lines']):
            _bind_line_narrowings(entry, correlated[entry['rule']], limits=list(limits), direct=direct,
                                  line_rules=line_rules, cites=cites,
                                  aimed=set(aimed_index) if rule_bar else set())
        mechanisms = [mechanism for entry in row['narrowings'] for mechanism in entry['mechanisms']]
        named = [(slot[2], mechanism['target']) for mechanism in mechanisms
                 for slot in [_slot(mechanism['mechanism'])] if slot[1] in _RULE_SLOTS]
        grounded = [(mechanism['grounds']['citation']['rule'], mechanism['grounds']['citation']['key'],
                     mechanism['target']) for mechanism in mechanisms if mechanism['licence'] == 'cited']
        # Each rule-named mechanism is listed under its rule, and each citation licenses exactly the
        # mechanisms whose grounds name it (Run.lean `ruleNarrowingsJson`).
        if (Counter(named) != Counter((entry['rule'], target) for entry in rows for target in entry['narrows']) or
                Counter(grounded) != Counter((entry['rule'], citation['key'], target) for entry in rows
                                             for citation in entry['citations'] for target in citation['licenses'])):
            raise ValueError('unbound rule narrowing or citation licence')
        distinction_predicates = {line['predicate'] for line in row['lines']}
        reported_predicates = [entry['predicate'] for entry in row['distinction']]
        if (len(reported_predicates) != len(set(reported_predicates)) or
                set(reported_predicates) != distinction_predicates):
            raise ValueError('missing or extra distinction row')
        protected = set(environment['vocabulary']['rights'].get('protected', []))
        for entry in row['distinction']:
            hits = [(hit['right'], hit['rule'], hit['protected']) for hit in entry['hits']]
            # Distinction.lean `distinctionHits`: a hit is cited when its line cites a guard source.
            if (len(hits) != len(set(hits)) or
                    any((right, rule) not in line_pairs or name not in protected
                        for right, rule, name in hits) or
                    any(hit['cited'] is not ('guard' in cites[hit['rule']]) for hit in entry['hits'])):
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


def _bind_conflict(row, elaborated, witness=None):
    """Bind the conflict's displayed identities to the elaborated source."""
    try:
        targets = [entry['target'] for entry in elaborated['conflict_targets']]
        if witness is not None:
            # The schema binds `target` to the submitted witness (`x-equals: /witness/target`).
            if row['targets'] != targets:
                raise ValueError('unbound conflict witness targets')
            return
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
            for mechanism, bound in zip(actual['mechanisms'], source['mechanisms']):
                licence = mechanism['licence']
                text = mechanism['mechanism']
                # The elaboration bound each licence to the request; only a sent certificate
                # can license a mechanism it left unlicensed (Run.lean `narrowingsJson`).
                if licence != bound['licence'] and not (
                        bound['licence'] is None and licence == 'certified' and not empty_certificates):
                    raise ValueError('unbound mechanism licence')
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
        line_rules = [entry['node'] for entry in elaborated['lines']]
        outside_rules = [unit['norm'] for unit in units if 'norm' in unit]
        predicates = elaborated['environment_prime']['vocabulary']['predicates']
        for entry in rows:
            if entry['reading'] == 'rule':
                predicate = entry['predicate']
                def dual(rule):
                    return _act_key(rule['predicate'], predicates) == predicate and rule['predicate'] != predicate
                expected = {
                    'barred': [rule['name'] for rule in line_rules
                               if rule['predicate'] == predicate and rule['sign']],
                    'blocked_defaults': [rule['name'] for rule in line_rules + outside_rules
                                         if rule.get('mode', 'strict') == 'default' and
                                         (rule['predicate'] == predicate or (rule['sign'] and dual(rule)))],
                    'composition_candidates':
                        [rule['name'] for rule in outside_rules if rule.get('mode', 'strict') == 'strict' and
                         rule['sign'] and (rule['predicate'] == predicate or dual(rule))] +
                        [rule['name'] for rule in line_rules if rule.get('mode', 'strict') == 'strict' and
                         rule['sign'] and dual(rule)],
                }
                for field, names in expected.items():
                    if entry[field] != names:
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
    elif kind == 'rights-conflict':
        elaborated = run_rights_case(environment, units, 'rights-elaborate')
        _bind_conflict(row, elaborated, extra.get('witness'))
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
        from .admission import bind_report
        bind_report(document, row['report'])
        labels = (elaborated['conditional_on'] +
                  [entry['label'] for entry in elaborated['limitations']])
        reported = {assumption.get('label') for assumption in row['report']['assumptions']}
        if row['conditional_on'] != [label for label in labels if label in reported]:
            raise ValueError('unbound rights admission conditional labels')
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(f'CheckerUnavailable: Lean rights admission is not bound to the request: {error}') from error
    return {key: value for key, value in row.items() if key not in ("id", "status")}
