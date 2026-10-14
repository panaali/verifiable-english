"""Containers for Lean-accepted soft norms and their regenerated premises."""
from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
import hashlib
import json

from .ast import _Decoder
from .environment import Environment
from .errors import CheckerUnavailable, UnsupportedProfile
from .norms import Norm, NormDocument


def soft_digest(domain, payload):
    """Hash the accepted soft wire form, including its nullable decider slots."""
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(domain.encode('ascii') + encoded).hexdigest()


def check_soft_source(environment, norms=None, *, generated=False, layers=frozenset(),
                      submitted_soft_route=False):
    """Relay the lower soft frame to Lean for a generated layer."""
    from .backends.soft_relay import run as _run, wire as _wire
    source = deepcopy(environment)
    if "rights@0" in layers:
        source["profiles"] = [p for p in source["profiles"] if p != "rights@0"]
        source["vocabulary"].pop("rights", None)
    if "readings@1" in layers:
        source["profiles"] = [p for p in source["profiles"] if p != "readings@1"]
    if "norm-defaults@0" in layers:
        vocabulary = source.get("vocabulary") if type(source) is dict else None
        predicates = vocabulary.get("predicates") if type(vocabulary) is dict else None
        if type(predicates) is dict and all(type(entry) is dict and
                                           type(entry.get("regulated", {})) is dict
                                           for entry in predicates.values()):
            from .norms import _norm_defaults_placeholder
            source = _norm_defaults_placeholder(source)
    if generated:
        source["vocabulary"]["predicates"] = {
            name: entry for name, entry in source["vocabulary"]["predicates"].items()
            if not name.startswith("soft__")}
    payload = {"id": "soft-elaborate", "kind": "soft-elaborate",
               "environment": _wire(source), "norms": _wire(list(norms or ()))}
    if not generated and "readings@1" in layers and not layers.intersection({"rights@0", "norm-defaults@0"}):
        payload["identity_environment"] = _wire(environment)
    row = _run(payload)
    bind_soft_elaboration(row, payload['norms'], source['vocabulary']['predicates'],
                          soft=source['vocabulary'].get('soft', {}))
    return row


def load_soft_document(environment, norms):
    """Build the Python containers after Lean accepts the complete soft source."""
    from .backends.soft_relay import run as _run, wire as _wire
    environment, norms = _wire(environment), _wire(norms)
    _run({"id": "soft-elaborate", "kind": "soft-elaborate",
          "environment": environment, "norms": norms})
    try:
        return SoftNormDocument(SoftEnvironment(environment), norms)
    except Exception as error:
        raise CheckerUnavailable(
            f"CheckerUnavailable: Python could not construct Lean-accepted soft source: {error}") from error


class SoftEnvironment(Environment):
    """A W1 environment with an identity-bound soft declaration block.

    The underlying Environment validates every ordinary declaration. The
    original soft metadata is restored in to_dict, so canonical identity binds
    it without changing the bytes of environments that lack the profile.
    """
    # The statement layers of `LAYER_ROUTES` whose route builds this class.
    LAYERS = frozenset()

    def __init__(self, data, *, generated=False):
        from .backends.soft_relay import wire
        data = wire(data)
        profiles = data.get("profiles") if type(data) is dict else None
        layers = set(self.LAYERS)
        if type(profiles) is list:
            layers.update(p for p in profiles if p in ("norm-defaults@0", "readings@1"))
        row = check_soft_source(data, generated=generated, layers=frozenset(layers))
        try:
            self._init_soft(data, row)
            object.__setattr__(self, '_generated_source', generated)
        except Exception as error:
            raise CheckerUnavailable(
                f"CheckerUnavailable: Python could not construct Lean-accepted soft environment: {error}") from error

    def _init_soft(self, data, row):
        raw = deepcopy(data)
        vocab = raw['vocabulary']
        has_block = 'soft' in vocab
        soft = vocab.pop('soft') if has_block else {
            'parties': [], 'ranks': [], 'outranks': [], 'ties': [], 'outranking': {'mode': 'strict'}}
        for entry in vocab['predicates'].values():
            entry.pop('instruction_of', None)
        object.__setattr__(self, 'soft', soft)
        object.__setattr__(self, 'soft_present', has_block)
        object.__setattr__(self, 'instruction_of', {
            name: entry['instruction_of'] for name, entry in sorted(data['vocabulary']['predicates'].items())
            if 'instruction_of' in entry})
        object.__setattr__(self, 'ranks_above', {
            name: set(above) for name, above in row['ranks_above'].items()})
        object.__setattr__(self, 'soft_premises', ())
        # Every declaration passed 2.3 under the same profiles; this cannot fail.
        super().__init__(raw, _validated_projection=True)

    def to_dict(self):
        data = super().to_dict()
        if getattr(self, 'soft_present', False):
            data['vocabulary']['soft'] = deepcopy(self.soft)
        for name, party in getattr(self, 'instruction_of', {}).items():
            data['vocabulary']['predicates'][name]['instruction_of'] = party
        return data


@dataclass(frozen=True, slots=True)
class SoftRule:
    core: Norm
    mode: str
    rank: str | None
    alterable: tuple[str, ...]
    exception: dict | None
    hard: bool

    def to_dict(self):
        raw = self.core.to_dict()['norm']
        if self.mode == 'default':
            raw['mode'] = 'default'
        if self.rank is not None:
            raw['rank'] = self.rank
        if self.alterable:
            raw['alterable'] = list(self.alterable)
        if self.exception is not None:
            raw['exception'] = {k: v for k, v in self.exception.items()
                                if k != 'decided_by' or v is not None}
        if self.hard:
            raw['hard'] = True
        return {'norm': raw}


def _rule_source(env: SoftEnvironment):
    """The lower soft source used for individual quoted rules: under norm-defaults@0 its placeholder, each
    unspecified completion read as deny (norm-defaults 2.3)."""
    source = env.to_dict()
    if "norm-defaults@0" in source["profiles"]:
        from .norms import _norm_defaults_placeholder
        source = _norm_defaults_placeholder(source)
    source["profiles"] = [p for p in source["profiles"]
                          if p not in ("norm-defaults@0", "readings@1", "rights@0")]
    source["vocabulary"].pop("rights", None)
    source["vocabulary"]["predicates"] = {
        name: declaration for name, declaration in source["vocabulary"]["predicates"].items()
        if not name.startswith("soft__")}
    return source


def decode_rule(env: SoftEnvironment, content):
    """Ask Lean to check a quoted rule, then construct its display container."""
    from .backends.soft_relay import check_rule, wire as _wire
    check_rule(_wire(_rule_source(env)), _wire(content))
    try:
        return _hydrate_rule(content)
    except Exception as error:
        raise CheckerUnavailable(
            f"CheckerUnavailable: Python could not construct Lean-accepted soft rule: {error}") from error


def check_rule_batch(env: SoftEnvironment, contents):
    """Check many rules under one Lean-decoded source, retaining per-rule outcomes."""
    from .backends.soft_relay import check_rules, wire as _wire
    contents = list(contents)
    results = check_rules(_wire(_rule_source(env)), _wire(contents))
    if len(results) != len(contents):
        raise CheckerUnavailable("CheckerUnavailable: Lean soft rule count differs from the request")
    return results


def batch_rule(env: SoftEnvironment, content, result):
    """Hydrate a checked batch item when its position is reached by the caller."""
    if result["status"] == "error":
        decode_rule(env, content)  # Lean supplies the same public diagnostic and code.
        raise CheckerUnavailable("CheckerUnavailable: Lean soft rule checks disagree")
    try:
        return _hydrate_rule(content)
    except Exception as error:
        raise CheckerUnavailable(
            f"CheckerUnavailable: Python could not construct Lean-accepted soft rule: {error}") from error


def _hydrate_rule(content):
    """Build a Python AST from a rule that Lean has accepted."""
    raw = content['norm']
    decoder = _Decoder()
    core = Norm(raw['name'], raw['predicate'], raw['sign'], decoder.decode(raw['guard']),
                tuple(decoder.decode(item) for item in raw['unless']), tuple(raw['over']))
    return SoftRule(core, raw.get('mode', 'strict'), raw.get('rank'),
                    tuple(raw.get('alterable', ())), raw.get('exception'), raw.get('hard', False))


class SoftBaseEnvironment(Environment):
    def __init__(self, data, premises=()):
        object.__setattr__(self, 'soft_premises', tuple(premises))
        super().__init__(data)


class SoftenedNormDocument(NormDocument):
    def base_environment(self):
        data = self.env.to_dict()
        data['vocabulary'].pop('soft', None)
        data['vocabulary']['predicates'] = {
            name: {k: v for k, v in decl.items() if k != 'instruction_of'}
            for name, decl in data['vocabulary']['predicates'].items() if 'regulated' not in decl}
        # `readings@1` is the head's layer, never the base vocabulary's (DRI ruling 4's class).
        data['profiles'] = [p for p in data['profiles'] if p not in ('norms@0', 'soft-norms@0', 'readings@1')]
        return SoftBaseEnvironment(data, getattr(self, 'soft_premises', ()))


# A decision's key as Lean writes it (`SoftNorms.Wire.decisionKeyJson`): its fields in tuple order.
DECISION_KEY_FIELDS = {"excepted": ("excepted",), "off": ("off", "party"), "outweighs": ("outweighs", "lower", "higher")}


def _decision_key(raw):
    """A decision's key from Lean's row as a tuple: `("excepted", rule)`, `("off", rule, party)` or
    `("outweighs", act, lower, higher)`."""
    for kind, fields in DECISION_KEY_FIELDS.items():
        if type(raw) is dict and set(raw) == set(fields) and all(type(raw[f]) is str for f in fields):
            return (kind, *(raw[f] for f in fields))
    raise ValueError(f"undecodable decision key {raw!r}")


def bind_soft_elaboration(row, norms, predicates, *, rights_rules=(), soft=None):
    """Bind the IDs in a Lean soft elaboration to its submitted rules and vocabulary.

    Rights supplies its correlated rule names separately: their generated node names
    are checked against the authored lines by the rights route.  The decisions and
    collisions use this same binding for both public elaboration routes.
    """
    try:
        rules = {unit['norm']['name']: unit['norm'] for unit in norms}
        if len(rules) != len(norms):
            raise ValueError('duplicate rule')
        rules.update(rights_rules)
        acts = set(predicates)
        rule_acts = row.get('rule_acts')
        if rule_acts is not None and (set(rule_acts) != set(rules) or
                                      any(act not in acts for act in rule_acts.values())):
            raise ValueError('unbound rule act')

        expected = set()
        for name, rule in rules.items():
            if rule.get('mode', 'strict') == 'default':
                expected.add(('excepted', name))
            expected.update(('off', name, party) for party in rule.get('alterable', ()))

        seen_pairs = set()
        pair_labels = set()
        for pair in row['colliding_pairs']:
            names = pair['pair']
            if (len(names) != 2 or names[0] == names[1] or
                any(name not in rules for name in names) or pair['act'] not in acts or
                (rule_acts is not None and any(rule_acts[name] != pair['act'] for name in names))):
                raise ValueError('unbound colliding pair')
            pair_names = frozenset(names)
            if pair_names in seen_pairs:
                raise ValueError('duplicate colliding pair')
            seen_pairs.add(pair_names)
            if pair['label'] not in {f'soft:coherence:{names[0]},{names[1]}',
                                     f'soft:coherence:{names[1]},{names[0]}'} or pair['label'] in pair_labels:
                raise ValueError('unbound or duplicate coherence label')
            pair_labels.add(pair['label'])
            if pair['outweighs'] is not None:
                ranks = {rules[name].get('rank') for name in names}
                if None in ranks or len(ranks) != 2:
                    raise ValueError('unbound weighing ranks')
                expected.add(('outweighs', pair['act'], *sorted(ranks)))

        found = set()
        names = set()
        for decision in row['decisions']:
            key = _decision_key(decision['key'])
            if key[0] == 'outweighs':
                key = ('outweighs', key[1], *sorted(key[2:]))
            if key not in expected or key in found or decision['name'] in names:
                raise ValueError('unbound or duplicate decision')
            found.add(key)
            names.add(decision['name'])
        if found != expected:
            raise ValueError('missing decision')
        # Labels are request identities. The formula beside a label is Lean's
        # derived value, but a relay may not invent another premise.
        expected_labels = set(pair_labels)
        for name, rule in rules.items():
            if rule.get('mode', 'strict') != 'default':
                continue
            exception = rule.get('exception') or {}
            for role in ('sufficient', 'necessary'):
                expected_labels.update(
                    f'soft:exception:{name}:{role}:{i}'
                    for i in range(len(exception.get(role, ())))
                )
        background_labels = [entry['label'] for entry in row['background']
                             if entry['generator'] == 'soft']
        if (len(background_labels) != len(set(background_labels)) or
                set(background_labels) != expected_labels):
            raise ValueError('unbound, missing or duplicate soft background label')
        derived = [entry['rule'] for entry in row['derived']]
        if len(derived) != len(rules) or set(derived) != set(rules):
            raise ValueError('unbound, missing or duplicate derived rule')
        premises = [entry['label'] for entry in row['premises']]
        if (len(premises) != len(set(premises)) or
                any(label != f'layer:norms:{name}' for label, name in zip(premises, row['order'])) or
                len(premises) != len(row['order'])):
            raise ValueError('unbound layer premise')
        order = row['order']
        if len(order) != len(set(order)) or not set(order) <= acts:
            raise ValueError('unbound layer order')
        targets = [entry['target'] for entry in row['conflict_targets']]
        allowed_targets = acts | {f'{name}->{decl["regulated"]["permission"]}'
                                  for name, decl in predicates.items()
                                  if type(decl) is dict and type(decl.get('regulated')) is dict
                                  and decl['regulated'].get('role') == 'obligation'
                                  and decl['regulated'].get('permission') in acts}
        if len(targets) != len(set(targets)) or not set(targets) <= allowed_targets:
            raise ValueError('unbound conflict target')
        incompatible = [tuple(pair) for pair in row.get('incompatible_pairs', ())]
        if (len(incompatible) != len(set(incompatible)) or
                any(len(pair) != 2 or pair[0] == pair[1] or
                    not set(pair) <= set(rules) for pair in incompatible)):
            raise ValueError('unbound incompatible pair')
        if soft is not None:
            ranks = set(soft.get('ranks', ()))
            above = row['ranks_above']
            if (set(above) != ranks or any(len(values) != len(set(values)) or
                   not set(values) <= ranks for values in above.values())):
                raise ValueError('unbound rank')
            conditional = row['conditional_on']
            if len(conditional) != len(set(conditional)) or not set(conditional) <= pair_labels:
                raise ValueError('unbound or duplicate conditional label')
            defaults = [rule for rule in rules.values() if rule.get('mode', 'strict') == 'default']
            switches = sum(len(rule.get('alterable', ())) for rule in rules.values())
            overrides = sum(key[0] == 'outweighs' for key in found)
            bounds = {'default_exceptions': len(defaults), 'instruction_switches': switches,
                      'holistic_overrides': overrides, 'weighing_points': len(pair_labels)}
            if any(row['soft_residual'][field] > maximum for field, maximum in bounds.items()):
                raise ValueError('soft residual count exceeds request')
            decider_limits = {}
            for rule in defaults:
                decider = (rule.get('exception') or {}).get('decided_by') or soft.get('exception_decider') or 'unstated'
                decider_limits[decider] = decider_limits.get(decider, 0) + 1
            counts = row['default_exceptions_by_decider']
            if any(count == 0 or count > decider_limits.get(name, 0) for name, count in counts.items()):
                raise ValueError('unbound default exception decider or count')
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(f'CheckerUnavailable: Lean soft elaboration is not bound to the request: {error}') from error


class SoftNormDocument:
    """Validated soft tree, its W1 elaboration, and regenerated base premises.

    `deferred` (docs/lean-first/b6/DELTA.md, Latency): a container of a document that Lean checks
    elsewhere, such as a readings candidate's chain document (`readings_s1.Side`, which Lean's
    readings route checks as `sideWF`), holds only `env`, `rules` and `core` until a field Lean
    supplies is first read. That read asks Lean for the document, as eager construction does, and
    raises its diagnostic; nothing Lean supplies is ever read without Lean's answer. Readers that
    need only the rules no longer cost one whole-document Lean request per candidate."""
    def __init__(self, env: SoftEnvironment, units, *, deferred=False):
        from .backends.soft_relay import wire
        units = wire(units)
        self._source = (env, units)
        self._extended = {}
        self._deferred = deferred
        if deferred:
            try:
                self._init_rules(env, units)
                return
            except Exception:  # noqa: BLE001  (Lean's diagnostic for the source comes first)
                self._deferred = False
        self._elaborate()

    def __getattr__(self, name):
        # Reached only for an attribute the instance lacks: a field Lean supplies, on a deferred document.
        if name.startswith("__") or not self.__dict__.get("_deferred"):
            raise AttributeError(name)
        self._elaborate()
        return getattr(self, name)

    def decision_name(self, key):
        """The decision predicate Lean generates for `key` (`keyedDecisions`): `("excepted", rule)`,
        `("off", rule, party)` or `("outweighs", act, lower, higher)`."""
        return self.decision_by_key[key]

    def extend(self, **attributes):
        """Set `attributes` on `extended_env`, now or once Lean's answer builds it."""
        self._extended.update(attributes)
        if not self._deferred:
            for name, value in attributes.items():
                object.__setattr__(self.extended_env, name, value)

    def _elaborate(self):
        env, units = self._source
        profiles = env.to_dict().get("profiles", ())
        row = check_soft_source(env.to_dict(), units,
                                generated=getattr(env, '_generated_source', False),
                                layers=frozenset(p for p in profiles
                                                 if p in ("norm-defaults@0", "readings@1", "rights@0")))
        try:
            self._init_soft(env, units, row)
        except Exception as exc:
            raise CheckerUnavailable(
                f"CheckerUnavailable: Python could not construct Lean-accepted soft document: {exc}") from exc
        self.document_hash = row["document_hash"]
        for name, value in self._extended.items():
            object.__setattr__(self.extended_env, name, value)
        self._deferred = False

    def _init_rules(self, env: SoftEnvironment, units):
        if not isinstance(env, SoftEnvironment):
            raise UnsupportedProfile('soft-norms@0 is required')
        self.env = env
        self.rules = tuple(_hydrate_rule(unit) for unit in units)
        self.core = NormDocument(env, [rule.core for rule in self.rules])

    def _init_soft(self, env: SoftEnvironment, units, row):
        self._init_rules(env, units)
        vocabulary = env.to_dict()['vocabulary']
        bind_soft_elaboration(row, units, vocabulary['predicates'], soft=vocabulary.get('soft', {}))
        by_name = {rule.core.name: rule for rule in self.rules}
        self.decisions = {item['name']: item['arguments'] for item in row['decisions']}
        # What each decision decides, as Lean keys it (`keyedDecisions`); a reader finds a decision's name by its key
        # and never spells one. Each key is bound to the request: a declared rule (default for an exception, with the
        # party among its switches for a switch), or a colliding pair's `outweighs` decision on the pair's act and
        # between the pair's two ranks.
        outweighs = {(item['outweighs'], item['act'], frozenset(by_name[n].rank for n in item['pair']))
                     for item in row['colliding_pairs'] if item['outweighs'] is not None}
        self.decision_by_key = {}
        for item in row['decisions']:
            key = _decision_key(item['key'])
            if key[0] == 'excepted':
                bound = by_name[key[1]].mode == 'default'
            elif key[0] == 'off':
                bound = key[2] in by_name[key[1]].alterable
            else:
                bound = (item['name'], key[1], frozenset(key[2:])) in outweighs
            if not bound or key in self.decision_by_key:
                raise ValueError(f"decision {item['name']} is not bound to the request")
            self.decision_by_key[key] = item['name']
        self.collisions = tuple((by_name[item['pair'][0]], by_name[item['pair'][1]])
                                for item in row['colliding_pairs'])
        self.rule_acts = row['rule_acts']
        self.incompatible_pairs = frozenset(frozenset(pair) for pair in row['incompatible_pairs'])
        self.override_for_pair = {
            frozenset(item['pair']): item['outweighs'] for item in row['colliding_pairs']
            if item['outweighs'] is not None}
        self.document_hash = row['document_hash']
        self.warnings = tuple(row['warnings'])
        prime = deepcopy(row['environment_prime'])
        if getattr(env, '_generated_source', False):
            # A norms-only source may declare an ordinary soft__ predicate. The
            # internal soft relay removes that prefix while validating its
            # generated layer; restore the author's declarations for Python's
            # subsequent assertion typing and situation search.
            source = env.to_dict()['vocabulary']['predicates']
            target = prime['vocabulary']['predicates']
            for name, declaration in source.items():
                if name.startswith('soft__') and name not in target:
                    target[name] = deepcopy(declaration)
        self.extended_env = SoftEnvironment(prime, generated=True)
        object.__setattr__(self.extended_env, 'decision_names', frozenset(self.decisions))
        derived = {item['rule']: item['ast'] for item in row['derived']}
        softened = []
        for rule in self.rules:
            core = rule.core
            ast = derived[core.name]
            unless = core.unless if ast is None else (*core.unless, _Decoder().decode(ast))
            softened.append(Norm(core.name, core.predicate, core.sign, core.guard, unless, core.over))
        self.elaborated = SoftenedNormDocument(self.extended_env, softened)
        self.exception_premises = tuple(
            (item['label'], _Decoder().decode(item['ast'])) for item in row['background']
            if item['generator'] == 'soft' and item['label'].startswith('soft:exception:'))
        self.coherence_premises = tuple(
            (item['label'], _Decoder().decode(item['ast'])) for item in row['colliding_pairs'])
        object.__setattr__(self.extended_env, 'soft_premises',
                           (*self.exception_premises, *self.coherence_premises))
        self.elaborated.soft_premises = self.extended_env.soft_premises
