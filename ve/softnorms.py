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
    return _run(payload)


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
        super().__init__(raw)

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
    """The lower soft source used for individual quoted rules."""
    source = env.to_dict()
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


class SoftNormDocument:
    """Validated soft tree, its W1 elaboration, and regenerated base premises."""
    def __init__(self, env: SoftEnvironment, units):
        from .backends.soft_relay import wire
        units = wire(units)
        profiles = env.to_dict().get("profiles", ())
        row = check_soft_source(env.to_dict(), units,
                                layers=frozenset(p for p in profiles
                                                 if p in ("norm-defaults@0", "readings@1", "rights@0")))
        try:
            self._init_soft(env, units, row)
        except Exception as exc:
            raise CheckerUnavailable(
                f"CheckerUnavailable: Python could not construct Lean-accepted soft document: {exc}") from exc
        self.document_hash = row["document_hash"]

    def _init_soft(self, env: SoftEnvironment, units, row):
        if not isinstance(env, SoftEnvironment):
            raise UnsupportedProfile('soft-norms@0 is required')
        self.env = env
        self.rules = tuple(_hydrate_rule(unit) for unit in units)
        by_name = {rule.core.name: rule for rule in self.rules}
        self.core = NormDocument(env, [rule.core for rule in self.rules])
        self.decisions = {item['name']: item['arguments'] for item in row['decisions']}
        self.collisions = tuple((by_name[item['pair'][0]], by_name[item['pair'][1]])
                                for item in row['colliding_pairs'])
        self.rule_acts = row['rule_acts']
        self.incompatible_pairs = frozenset(frozenset(pair) for pair in row['incompatible_pairs'])
        self.override_for_pair = {
            frozenset(item['pair']): item['outweighs'] for item in row['colliding_pairs']
            if item['outweighs'] is not None}
        self.document_hash = row['document_hash']
        self.warnings = tuple(row['warnings'])
        self.extended_env = SoftEnvironment(row['environment_prime'], generated=True)
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
