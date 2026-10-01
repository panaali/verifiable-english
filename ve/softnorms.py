"""Python schema and regeneration for the soft-norms@0 statement layer.

Decision symbols and soft background premises are derived from the source
norms, never accepted as authored premises or trusted wire fields.
"""
from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
import hashlib
import json

from .ast import (And, Binary, Const, Eq, Exists, Forall, Implies, Not, Or, Top, Bottom, Unary, Var,
                  _Checker, _Decoder, _to_data)
from .background import background, dependency_order
from .environment import Environment, valid_identifier
from .errors import DuplicateDeclaration, ResourceLimit, UnknownSymbol, UnsupportedProfile, VEError
from .limits import MAX_DEPTH, MAX_IDENTIFIER_BYTES, MAX_NODES, MAX_PREDICATES
from .norms import _NAME, Norm, NormDocument, _all, _any, _atom, _bind
from . import profiles as profile_registry
from .search import _used_predicates
from .wire import digest


def soft_diagnostic_code(message: str) -> str:
    """Stable soft rejection class; message wording and names are not part of the code."""
    if message.startswith('InvalidInput: rule '):
        if message.endswith(' needs an exception'):
            return 'SOFT_MISSING_EXCEPTION'
        if message.endswith(' is strict and declares an exception'):
            return 'SOFT_STRICT_EXCEPTION'
    checks = (
        ('InvalidInput: invalid ties pair', 'SOFT_INVALID_TIES_PAIR'),
        ('InvalidInput: invalid outranks pair', 'SOFT_INVALID_OUTRANKS_PAIR'),
        ('InvalidInput: invalid soft block', 'SOFT_INVALID_BLOCK'),
        ('InvalidInput: invalid outranking flag', 'SOFT_INVALID_OUTRANKING'),
        ('InvalidInput: invalid decider', 'SOFT_INVALID_DECIDER'),
        ('MissingExceptionDecider:', 'SOFT_MISSING_DECIDER'),
        ('InvalidInput: strict outranking has no decider', 'SOFT_STRICT_OUTRANKING_DECIDER'),
        ('InvalidInput: invalid soft name', 'SOFT_INVALID_NAME'),
        ('InvalidInput: reserved predicate', 'SOFT_INVALID_NAME'),
        ('InvalidInput: act-key predicate contains __', 'SOFT_INVALID_NAME'),
        ('DuplicateDeclaration:', 'SOFT_DUPLICATE_DECLARATION'),
        ('UnknownRank:', 'SOFT_UNKNOWN_RANK'),
        ('TieAgainstOrder:', 'SOFT_TIE_AGAINST_ORDER'),
        ('DependencyCycle:', 'SOFT_DEPENDENCY_CYCLE'),
        ('UnknownSymbol: party', 'SOFT_UNKNOWN_PARTY'),
        ('InvalidInput: exception sufficient must be an array', 'SOFT_EXCEPTION_ARRAY'),
        ('InvalidInput: exception necessary must be an array', 'SOFT_EXCEPTION_ARRAY'),
        ('InvalidInput: invalid factors', 'SOFT_INVALID_FACTORS'),
        ('InvalidInput: alterable of rule', 'SOFT_INVALID_ALTERABLE'),
        ('HardConstraintAltered:', 'SOFT_HARD_CONSTRAINT'),
        ('InvalidInput: exception condition of rule', 'SOFT_INVALID_EXCEPTION_CONDITION'),
        ('SoftOverHard:', 'SOFT_OVER_HARD'),
        ('ResourceLimit:', 'SOFT_RESOURCE_LIMIT'),
        ('UnsupportedProfile:', 'SOFT_UNSUPPORTED_PROFILE'),
        ('InvalidInput: invalid soft fields', 'SOFT_INVALID_RULE_FIELDS'),
        ('InvalidInput: invalid mode for rule', 'SOFT_INVALID_RULE_FIELDS'),
        ('InvalidInput: hard of rule', 'SOFT_INVALID_RULE_FIELDS'),
    )
    for prefix, code in checks:
        if message.startswith(prefix):
            return code
    if message.startswith('InvalidInput: ') and message.endswith(' must be an array'):
        return 'SOFT_INVALID_ARRAY'
    return 'SOFT_INVALID_INPUT'


def _code_soft_error(exc: VEError) -> VEError:
    """Classify an error raised after the validation table by its origin."""
    if getattr(exc, 'soft_checked', False):
        return exc
    if isinstance(exc, ResourceLimit):
        exc.code = 'SOFT_RESOURCE_LIMIT'
    elif isinstance(exc, UnsupportedProfile):
        exc.code = 'SOFT_UNSUPPORTED_PROFILE'
    else:
        exc.code = soft_diagnostic_code(str(exc))
    return exc


def soft_digest(domain, payload):
    """The soft norm wire permits null for inherited exception deciders."""
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(domain.encode('ascii') + encoded).hexdigest()


# The validation table of docs/spec/soft-norms.md section 8, as ordered phases.
# Each phase runs over the whole source before the next starts, and each check
# raises its own code; `Phases.lean` is the same list.

_ENVELOPE = {'language', 'profiles', 'spec_revision', 'vocabulary'}
_BLOCK_FIELDS = {'parties', 'ranks', 'outranks', 'ties', 'outranking', 'exception_decider'}
_W1_FIELDS = ('name', 'predicate', 'sign', 'guard', 'unless', 'over')
_SOFT_FIELDS = ('mode', 'rank', 'alterable', 'exception', 'hard')
_INHERITED_PROFILES = ('data@0', 'definitions@0', 'documents@1', 'norm-defaults@0', 'time@0')
_CHECKER_PROFILES = ('closure@0', 'nary@0', 'order@0')
SOFT_PROFILE = 'soft-norms@0'


def _fault(code, message, error=VEError):
    exc = error(message)
    exc.code = code
    exc.soft_checked = True
    return exc


def _inherited(call, *args, code='SOFT_INVALID_INPUT'):
    """Run an inherited W1/P0 check; its failure is classified by this position."""
    try:
        return call(*args)
    except VEError as exc:
        exc.code = code
        exc.soft_checked = True
        raise


def _utf8(value):
    return len(value.encode('utf-8'))


@dataclass(slots=True)
class _Context:
    env: Environment
    parties: tuple[str, ...]
    ranks: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    ties: tuple[tuple[str, str], ...]
    exception_decider: str | None
    instructions: dict


@dataclass(slots=True)
class _RuleFields:
    core: Norm
    mode: str
    rank: str | None
    alterable: tuple[str, ...]
    hard: bool
    exception: dict | None
    conditions: dict


# Phase 1: envelope and JSON shape.

def _envelope(data, norms):
    if type(data) is not dict or set(data) != _ENVELOPE:
        raise _fault('SOFT_INVALID_INPUT', 'InvalidInput: invalid environment envelope')
    if data['language'] != profile_registry.LANGUAGE:
        raise _fault('SOFT_UNSUPPORTED_PROFILE', 'UnsupportedProfile: Unsupported language',
                     UnsupportedProfile)
    if type(data['profiles']) is not list or any(type(p) is not str for p in data['profiles']):
        raise _fault('SOFT_UNSUPPORTED_PROFILE',
                     'UnsupportedProfile: profiles must be a sorted unique array', UnsupportedProfile)
    if data['spec_revision'] != profile_registry.SPEC_REVISION:
        raise _fault('SOFT_UNSUPPORTED_PROFILE',
                     'UnsupportedProfile: Unsupported specification revision', UnsupportedProfile)
    vocab = data['vocabulary']
    required = {'sorts', 'predicates', 'constants'}
    if (type(vocab) is not dict or not required <= set(vocab) <= required | {'soft'}
            or any(type(vocab[k]) is not dict for k in required)):
        raise _fault('SOFT_INVALID_INPUT', 'InvalidInput: invalid vocabulary')
    if norms is not None:
        _norm_array(norms)


def _norm_array(norms):
    if type(norms) not in (list, tuple):
        raise _fault('SOFT_INVALID_INPUT', 'InvalidInput: expected an array of norm objects')
    if len(norms) > 256:
        raise _fault('SOFT_RESOURCE_LIMIT', 'ResourceLimit: rules', ResourceLimit)


# Phase 2: vocabulary declarations.

def _names(block, label, maximum):
    values = block.get(label, [])
    if type(values) is not list:
        raise _fault('SOFT_INVALID_ARRAY', f'InvalidInput: {label} must be an array')
    if len(values) > maximum:
        raise _fault('SOFT_RESOURCE_LIMIT', f'ResourceLimit: {label}', ResourceLimit)
    seen = []
    for name in values:
        if type(name) is not str or not valid_identifier(name) or '__' in name:
            raise _fault('SOFT_INVALID_NAME', f'InvalidInput: invalid soft name {name}')
        if name in seen:
            kind = 'party' if label == 'parties' else 'rank'
            raise _fault('SOFT_DUPLICATE_DECLARATION', f'DuplicateDeclaration: {kind} {name}',
                         DuplicateDeclaration)
        seen.append(name)
    return tuple(values)


def _decider(value, where):
    if type(value) is not str or not value or _utf8(value) > 64:
        raise _fault('SOFT_INVALID_DECIDER', f'InvalidInput: invalid decider for {where}')
    return value


def _pairs(block, field):
    values = block.get(field, [])
    if type(values) is not list:
        raise _fault('SOFT_INVALID_ARRAY', f'InvalidInput: {field} must be an array')
    code = 'SOFT_INVALID_OUTRANKS_PAIR' if field == 'outranks' else 'SOFT_INVALID_TIES_PAIR'
    pairs = []
    for pair in values:
        if (type(pair) is not list or len(pair) != 2 or any(type(x) is not str for x in pair)
                or pair[0] == pair[1] or tuple(pair) in pairs):
            raise _fault(code, f'InvalidInput: invalid {field} pair')
        pairs.append(tuple(pair))
    return tuple(pairs)


def _declarations(data, generated):
    vocab = data['vocabulary']
    # Canonical key order: Lean enumerates JSON objects by key.
    predicates = sorted(vocab['predicates'].items())
    if not generated:
        for name, entry in predicates:
            if name.startswith('soft__') or ('__' in name and type(entry) is dict and 'regulated' in entry):
                raise _fault('SOFT_INVALID_NAME', f'InvalidInput: invalid soft name {name}')
    instructions = {}
    for name, entry in predicates:
        if type(entry) is dict and 'instruction_of' in entry:
            if type(entry['instruction_of']) is not str or 'regulated' in entry or 'defined' in entry:
                raise _fault('SOFT_INVALID_INPUT', f'InvalidInput: instruction_of on {name}')
            instructions[name] = entry['instruction_of']
    profiles = sorted({p for p in data['profiles'] if p in _INHERITED_PROFILES}
                      | {'norms@0', profile_registry.BASE})
    stripped = {**data, 'profiles': profiles, 'vocabulary': {
        'sorts': vocab['sorts'], 'constants': vocab['constants'],
        'predicates': {name: ({k: v for k, v in entry.items() if k != 'instruction_of'}
                              if type(entry) is dict else entry)
                       for name, entry in vocab['predicates'].items()}}}
    env = _inherited(Environment, stripped)
    if 'soft' not in vocab:
        return _Context(env, (), (), (), (), None, instructions)
    block = vocab['soft']
    if type(block) is not dict or 'outranking' not in block or set(block) - _BLOCK_FIELDS:
        raise _fault('SOFT_INVALID_BLOCK', 'InvalidInput: invalid soft block')
    parties = _names(block, 'parties', 8)
    ranks = _names(block, 'ranks', 16)
    flag = block['outranking']
    if (type(flag) is not dict or 'mode' not in flag or set(flag) - {'mode', 'decided_by'}
            or type(flag['mode']) is not str or flag['mode'] not in ('strict', 'holistic')):
        raise _fault('SOFT_INVALID_OUTRANKING', 'InvalidInput: invalid outranking flag')
    if flag['mode'] == 'strict' and 'decided_by' in flag:
        raise _fault('SOFT_STRICT_OUTRANKING_DECIDER', 'InvalidInput: strict outranking has no decider')
    if 'decided_by' in flag and type(flag['decided_by']) is not str:
        raise _fault('SOFT_INVALID_DECIDER', 'InvalidInput: invalid decider for outranking')
    if flag['mode'] == 'holistic' and 'decided_by' not in flag:
        raise _fault('SOFT_MISSING_DECIDER', 'MissingExceptionDecider: outranking')
    if 'decided_by' in flag:
        _decider(flag['decided_by'], 'outranking')
    exception_decider = None
    if 'exception_decider' in block:
        exception_decider = _decider(block['exception_decider'], 'exception')
    edges = _pairs(block, 'outranks')
    ties = _pairs(block, 'ties')
    return _Context(env, parties, ranks, edges, ties, exception_decider, instructions)


# Phase 3: profiles.

def _profiles(data, env):
    profiles = data['profiles']
    fail = lambda message: _fault('SOFT_UNSUPPORTED_PROFILE', f'UnsupportedProfile: {message}',
                                  UnsupportedProfile)
    if profiles != sorted(set(profiles)):
        raise fail('profiles must be sorted and unique')
    for profile in profiles:
        if profile not in profile_registry.BY_NAME:
            raise fail(f'Unsupported profile {profile}')
    if profile_registry.BASE not in profiles:
        raise fail(f'Missing profile {profile_registry.BASE}')
    if SOFT_PROFILE not in profiles:
        raise fail('soft-norms@0 is required')
    if 'norms@0' not in profiles:
        raise fail('soft-norms@0 requires norms@0')
    if any(p in _CHECKER_PROFILES for p in profiles):
        raise fail('the norms route admits FOL documents only')
    if any(decl.defined is not None for decl in env.predicates.values()):
        raise fail('norms route with definitions is not implemented')
    if any(decl.functional or decl.total for decl in env.predicates.values()):
        raise fail('norms route with data flags is not implemented')


# Phase 4: rule fields.

def _fol(data):
    """Decode one FOL formula, the fragment Lean's `decodeFormula 64` accepts."""
    formula = _inherited(_Decoder().decode, data)

    def term(t):
        if not ((isinstance(t, Var) and type(t.index) is int) or
                (isinstance(t, Const) and type(t.name) is str)):
            raise _fault('SOFT_INVALID_INPUT', 'InvalidInput: invalid indexed term')

    def walk(node):
        if isinstance(node, (Top, Bottom)):
            return
        if isinstance(node, Unary) and type(node.predicate) is str:
            return term(node.term)
        if isinstance(node, Binary) and type(node.predicate) is str:
            term(node.left)
            return term(node.right)
        if isinstance(node, Eq):
            term(node.left)
            return term(node.right)
        if isinstance(node, Not):
            return walk(node.body)
        if isinstance(node, (And, Or, Implies)):
            walk(node.left)
            return walk(node.right)
        if isinstance(node, (Forall, Exists)) and type(node.sort) is str:
            return walk(node.body)
        raise _fault('SOFT_INVALID_INPUT', 'InvalidInput: invalid indexed formula')

    walk(formula)
    return formula


def _rule_fields(content, exception_decider):
    invalid = lambda message: _fault('SOFT_INVALID_INPUT', f'InvalidInput: {message}')
    if type(content) is not dict or set(content) != {'norm'} or type(content['norm']) is not dict:
        raise invalid('expected norm object')
    raw = content['norm']
    if not set(_W1_FIELDS) <= set(raw) <= set(_W1_FIELDS) | set(_SOFT_FIELDS):
        raise invalid(f'invalid norm fields {sorted(raw)}')
    name = raw['name']
    if type(name) is not str or len(name) > 64 or not _NAME.fullmatch(name):
        raise invalid(f'invalid rule name {name!r}')
    if type(raw['predicate']) is not str:
        raise invalid('rule predicate and precedence edges must be strings')
    if type(raw['sign']) is not bool:
        raise invalid('invalid sign or too many carve-outs')
    if type(raw['unless']) is not list or type(raw['over']) is not list:
        raise invalid('unless and over must be arrays')
    if len(raw['unless']) > 8:
        raise invalid('invalid sign or too many carve-outs')
    if any(type(p) is not str for p in raw['over']):
        raise invalid('rule predicate and precedence edges must be strings')
    core = Norm(name, raw['predicate'], raw['sign'], _fol(raw['guard']),
                tuple(_fol(x) for x in raw['unless']), tuple(raw['over']))
    # `over` is a set of rule names (3.2): a repeated name is rejected, not merged.
    seen = set()
    for parent in core.over:
        if parent in seen:
            raise invalid(f'duplicate over {parent} in rule {name}')
        seen.add(parent)
    mode = raw.get('mode', 'strict')
    if type(mode) is not str or mode not in ('strict', 'default'):
        raise _fault('SOFT_INVALID_RULE_FIELDS', f'InvalidInput: invalid mode for rule {name}')
    rank = raw.get('rank')
    if rank is not None and type(rank) is not str:
        raise _fault('SOFT_INVALID_RULE_FIELDS', f'InvalidInput: invalid soft fields for {name}')
    alterable = raw.get('alterable', [])
    if (type(alterable) is not list or any(type(x) is not str for x in alterable)
            or alterable != sorted(set(alterable))):
        raise _fault('SOFT_INVALID_ALTERABLE',
                     f'InvalidInput: alterable of rule {name} must be sorted and distinct')
    hard = raw.get('hard', False)
    if type(hard) is not bool:
        raise _fault('SOFT_INVALID_RULE_FIELDS', f'InvalidInput: hard of rule {name} must be Boolean')
    if hard and (mode != 'strict' or alterable):
        raise _fault('SOFT_HARD_CONSTRAINT', f'HardConstraintAltered: rule {name}')
    exception = raw.get('exception')
    if mode == 'strict' and exception is not None:
        raise _fault('SOFT_STRICT_EXCEPTION', f'InvalidInput: rule {name} is strict and declares an exception')
    conditions = {}
    if mode == 'default':
        if (type(exception) is not dict or
                set(exception) - {'decided_by', 'sufficient', 'necessary', 'factors'} or
                not {'sufficient', 'necessary', 'factors'} <= set(exception)):
            raise _fault('SOFT_MISSING_EXCEPTION', f'InvalidInput: rule {name} needs an exception')
        decided_by = exception.get('decided_by')
        if decided_by is not None and type(decided_by) is not str:
            raise _fault('SOFT_INVALID_DECIDER', f'InvalidInput: invalid decider for rule {name}')
        if decided_by is None and exception_decider is None:
            raise _fault('SOFT_MISSING_DECIDER', f'MissingExceptionDecider: rule {name}')
        if decided_by is not None:
            _decider(decided_by, f'rule {name}')
        for kind in ('sufficient', 'necessary'):
            if type(exception[kind]) is not list:
                raise _fault('SOFT_EXCEPTION_ARRAY', f'InvalidInput: exception {kind} must be an array')
            conditions[kind] = tuple(_fol(x) for x in exception[kind])
        factors = exception['factors']
        if type(factors) is not list or any(type(x) is not str or _utf8(x) > 200 for x in factors):
            raise _fault('SOFT_INVALID_FACTORS', f'InvalidInput: invalid factors of rule {name}')
    return _RuleFields(core, mode, rank, tuple(alterable), hard, exception, conditions)


# Phase 5: cross references.

def _environment_references(ctx):
    for name, party in sorted(ctx.instructions.items()):
        if party not in ctx.parties:
            raise _fault('SOFT_UNKNOWN_PARTY', f'UnknownSymbol: party {party}', UnknownSymbol)
    for pairs in (ctx.edges, ctx.ties):
        for pair in pairs:
            for rank in pair:
                if rank not in ctx.ranks:
                    raise _fault('SOFT_UNKNOWN_RANK', f'UnknownRank: {rank}')


def _rule_references(env, parties, ranks, rule):
    """5.4 to 5.8 for one rule."""
    core = rule.core
    decl = env.predicates.get(core.predicate)
    if decl is None or decl.regulated is None:
        raise _fault('SOFT_INVALID_INPUT', f'UnknownSymbol: regulated predicate {core.predicate}')
    if rule.rank is not None and rule.rank not in ranks:
        raise _fault('SOFT_UNKNOWN_RANK', f'UnknownRank: rule {core.name}, {rule.rank}')
    for party in rule.alterable:
        if party not in parties:
            raise _fault('SOFT_UNKNOWN_PARTY', f'UnknownSymbol: party {party}', UnknownSymbol)
    context = tuple(reversed(decl.arguments))
    checker = _Checker(env)
    for formula in (core.guard, *core.unless):
        _inherited(checker.formula, formula, context)
    for kind in ('sufficient', 'necessary'):
        for formula in rule.conditions.get(kind, ()):
            _inherited(checker.formula, formula, context)
            for predicate in sorted(_used_predicates(formula)):
                used = env.predicates[predicate]
                if used.regulated is not None or used.defined is not None or predicate.startswith('soft__'):
                    raise _fault('SOFT_INVALID_EXCEPTION_CONDITION',
                                 f'InvalidInput: exception condition of rule {core.name} mentions {predicate}')


def _document_references(env, parties, ranks, rules):
    """5.3 to 5.9 over the whole document."""
    names = []
    for rule in rules:
        if rule.core.name in names:
            raise _fault('SOFT_DUPLICATE_DECLARATION', f'DuplicateDeclaration: rule {rule.core.name}',
                         DuplicateDeclaration)
        names.append(rule.core.name)
    by_name = {rule.core.name: rule.core for rule in rules}
    for rule in rules:
        _rule_references(env, parties, ranks, rule)
        for parent in rule.core.over:
            if parent not in by_name:
                raise _fault('SOFT_INVALID_INPUT', f'UnknownRule: rule {parent}')
            if by_name[parent].predicate != rule.core.predicate:
                raise _fault('SOFT_INVALID_INPUT',
                             f'PrecedenceAcrossPredicates: rule {rule.core.name} on {rule.core.predicate}, '
                             f'rule {parent} on {by_name[parent].predicate}')


# Phase 6, environment part: the rank order.

def _rank_semantics(ctx):
    dependencies = {r: set() for r in ctx.ranks}
    for higher, lower in ctx.edges:
        dependencies[higher].add(lower)
    _inherited(dependency_order, dependencies, code='SOFT_DEPENDENCY_CYCLE')
    above = {r: set() for r in ctx.ranks}
    for higher, lower in ctx.edges:
        above[lower].add(higher)
    for rank in ctx.ranks:
        pending = list(above[rank])
        while pending:
            parent = pending.pop()
            for ancestor in above[parent] - above[rank]:
                above[rank].add(ancestor)
                pending.append(ancestor)
    for a, b in ctx.ties:
        if a in above[b] or b in above[a]:
            raise _fault('SOFT_TIE_AGAINST_ORDER', f'TieAgainstOrder: {a}, {b}')
    if len({frozenset(pair) for pair in ctx.ties}) != len(ctx.ties):
        raise _fault('SOFT_DUPLICATE_DECLARATION', 'DuplicateDeclaration: tie', DuplicateDeclaration)
    return above


def check_soft_source(environment, norms=None, *, generated=False):
    """Phases 1 to 5 and the rank checks of phase 6 over one soft source.

    Raises the first failing check of the table with its code. A caller that
    holds the raw environment and norms together runs this before building
    `SoftEnvironment`, so an environment fault never masks an earlier-phase
    fault in a rule."""
    _envelope(environment, norms)
    ctx = _declarations(environment, generated)
    _profiles(environment, ctx.env)
    rules = [_rule_fields(unit, ctx.exception_decider) for unit in (norms or ())]
    _environment_references(ctx)
    _document_references(ctx.env, ctx.parties, ctx.ranks, rules)
    above = _rank_semantics(ctx)
    return ctx, rules, above


def load_soft_document(environment, norms):
    """A soft source from raw JSON, validated in table order over the whole source."""
    check_soft_source(environment, norms)
    return SoftNormDocument(SoftEnvironment(environment), norms)


class SoftEnvironment(Environment):
    """A W1 environment with an identity-bound soft declaration block.

    The underlying Environment validates every ordinary declaration. The
    original soft metadata is restored in to_dict, so canonical identity binds
    it without changing the bytes of environments that lack the profile.
    """
    def __init__(self, data, *, generated=False):
        try:
            self._init_soft(data, generated=generated)
        except VEError as exc:
            _code_soft_error(exc)
            raise

    def _init_soft(self, data, *, generated=False):
        ctx, _, above = check_soft_source(data, generated=generated)
        raw = deepcopy(data)
        vocab = raw['vocabulary']
        has_block = 'soft' in vocab
        soft = vocab.pop('soft') if has_block else {
            'parties': [], 'ranks': [], 'outranks': [], 'ties': [], 'outranking': {'mode': 'strict'}}
        for entry in vocab['predicates'].values():
            entry.pop('instruction_of', None)
        object.__setattr__(self, 'soft', soft)
        object.__setattr__(self, 'soft_present', has_block)
        object.__setattr__(self, 'instruction_of', dict(sorted(ctx.instructions.items())))
        object.__setattr__(self, 'ranks_above', above)
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


def decode_rule(env: SoftEnvironment, content):
    try:
        return _decode_rule(env, content)
    except VEError as exc:
        _code_soft_error(exc)
        raise


def _soft_rule(fields):
    exception = fields.exception
    if fields.mode == 'default':
        exception = {**exception, **{kind: [_to_data(f) for f in fields.conditions[kind]]
                                     for kind in ('sufficient', 'necessary')}}
    return SoftRule(fields.core, fields.mode, fields.rank, fields.alterable, exception, fields.hard)


def _decode_rule(env: SoftEnvironment, content):
    """One norm unit on its own: 4.1 to 4.14, then 5.4 to 5.8."""
    fields = _rule_fields(content, env.soft.get('exception_decider'))
    _rule_references(env, env.soft.get('parties', []), env.soft.get('ranks', []), fields)
    return _soft_rule(fields)


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
        data['profiles'] = [p for p in data['profiles'] if p not in ('norms@0', 'soft-norms@0')]
        return SoftBaseEnvironment(data, getattr(self, 'soft_premises', ()))


def _decision_name(rule, party=None):
    root = rule.core.name.replace('-', '_')
    return f'soft__off__{root}__{party}' if party else f'soft__excepted__{root}'


def _within_limits(env, *formulas, context=()):
    """Generated formulas, typed in order by one checker (one MAX_NODES budget),
    are within MAX_DEPTH and MAX_NODES.

    The checker stops at the first overrun, so formulas whose unfolding is far
    larger than MAX_NODES cost at most MAX_NODES + 1 steps."""
    checker = _Checker(env, generated=True)
    try:
        for formula in formulas:
            checker.formula(formula, context)
    except ResourceLimit:
        return False
    return True


class _Sized:
    """A stand-in for an expanded subformula whose size is already known."""
    __slots__ = ('size',)

    def __init__(self, size):
        self.size = size


def _size(formula, atom=None):
    """(nodes, depth) of `formula` as `_Checker` counts them, term nodes included.

    `atom` may give the size an atom takes after outcome substitution (an
    instantiated expansion has its expansion's size). Shared subformulas are
    measured once, iteratively, so the cost is the formula's size as a graph
    however large its unfolding, and no recursion limit is reached."""
    memo = {}
    pending = [(formula, False)]
    while pending:
        node, ready = pending.pop()
        key = id(node)
        if key in memo:
            continue
        kind = type(node)
        if kind is _Sized:
            memo[key] = node.size
        elif kind in (Top, Bottom):
            memo[key] = (1, 1)
        elif kind in (Unary, Binary):
            sized = atom(node) if atom is not None else None
            memo[key] = sized if sized is not None else (2 if kind is Unary else 3, 1)
        elif kind is Eq:
            memo[key] = (3, 1)
        elif kind in (Not, Forall, Exists, And, Or, Implies):
            parts = (node.body,) if kind in (Not, Forall, Exists) else (node.left, node.right)
            if ready:
                sizes = [memo[id(part)] for part in parts]
                memo[key] = (1 + sum(n for n, _ in sizes), 1 + max(d for _, d in sizes))
            else:
                pending.append((node, True))
                pending.extend((part, False) for part in parts)
        else:
            raise VEError(f'InvalidInput: unexpected generated node {kind.__name__}')
    return memo[id(formula)]


def _fits(size):
    return size[0] <= MAX_NODES and size[1] <= MAX_DEPTH


def _or_nonempty(items):
    items = tuple(items)
    return _any(items) if items else Bottom()


class SoftNormDocument:
    """Validated soft tree, its W1 elaboration, and regenerated base premises."""
    def __init__(self, env: SoftEnvironment, units):
        try:
            self._init_soft(env, units)
        except VEError as exc:
            _code_soft_error(exc)
            raise

    def _init_soft(self, env: SoftEnvironment, units):
        if not isinstance(env, SoftEnvironment):
            raise UnsupportedProfile('soft-norms@0 is required')
        self.env = env
        # Phases 1, 4 and 5 over the whole document; the environment passed
        # phases 1 to 3, 5 and 6.1 to 6.3 when it was built.
        _norm_array(units)
        fields = [_rule_fields(unit, env.soft.get('exception_decider')) for unit in units]
        _document_references(env, env.soft.get('parties', []), env.soft.get('ranks', []), fields)
        self.rules = tuple(_soft_rule(x) for x in fields)
        self.collisions = tuple(sorted(((min(left, right, key=lambda r: r.core.name),
                                         max(left, right, key=lambda r: r.core.name))
                                        for i, left in enumerate(self.rules)
                                        for right in self.rules[i + 1:]
                                        if left.mode == right.mode == 'default'
                                        and self._incompatible(left, right)),
                                       key=lambda pair: (pair[0].core.name, pair[1].core.name)))
        # 6.4: E′ is within the vocabulary limits before anything is elaborated.
        self.decisions = self._decisions()
        for prefix in ('soft__excepted__', 'soft__off__', 'soft__outweighs__'):
            for name in self.decisions:
                if name.startswith(prefix) and len(name.encode('utf-8')) > MAX_IDENTIFIER_BYTES:
                    raise ResourceLimit(f'ResourceLimit: decision predicate {name}')
        if len(env.predicates) + len(self.decisions) > MAX_PREDICATES:
            raise ResourceLimit('ResourceLimit: extended vocabulary')
        self.core = NormDocument(env, [r.core for r in self.rules])
        by_name = {r.core.name: r for r in self.rules}
        for rule in self.rules:
            if rule.mode == 'default':
                for parent in rule.core.over:
                    if by_name[parent].mode == 'strict':
                        raise VEError(f'SoftOverHard: rule {rule.core.name} over {parent}')
        self.document_hash = soft_digest(f've-soft-norms-{env.identity_version}\n',
                                         {'environment_id': env.environment_id,
                                          'document': [r.to_dict() for r in self.rules]})
        warnings = []
        for rule in self.rules:
            for parent_name in rule.core.over:
                parent = by_name[parent_name]
                if (rule.mode == parent.mode == 'default' and
                        self._incompatible(rule, parent) and
                        parent.rank is not None and rule.rank is not None and
                        parent.rank in env.ranks_above[rule.rank]):
                    warnings.append(f'RankAgainstPrecedence: rule {rule.core.name} over {parent_name}')
        ranks = tuple(env.soft.get('ranks', []))
        ties = {frozenset(pair) for pair in env.soft.get('ties', [])}
        for a in ranks:
            for b in ranks:
                if (a < b and a not in env.ranks_above[b] and
                        b not in env.ranks_above[a] and frozenset((a, b)) not in ties):
                    warnings.append(f'undeclared tie: {a}, {b}')
        self.warnings = tuple(warnings)
        self.extended_env = self._extended_environment()
        self.elaborated = self._soften()
        # 6.11 and 6.12: every generated premise, serialised on its own as the
        # soft route does, is within MAX_DEPTH and MAX_NODES, so an accepted
        # document's whole elaboration serialises. A coherence premise is sized
        # from the expansion table and built only if it fits.
        self.exception_premises = self._exception_premises()
        for label, formula in self.exception_premises:
            if not _within_limits(self.extended_env, formula):
                raise ResourceLimit(f'ResourceLimit: generated soft premise {label}')
        self.expansion_sizes = self._expansion_sizes()
        self.coherence_premises = self._coherence_premises()
        for label, formula in self.elaborated.premises():
            if not _within_limits(self.extended_env, formula):
                raise ResourceLimit(f'ResourceLimit: generated norm layer {label}')
        self._check_conflict_targets()
        object.__setattr__(self.extended_env, 'soft_premises',
                           (*self.exception_premises, *self.coherence_premises))
        self.elaborated.soft_premises = self.extended_env.soft_premises
        # 6.14 and 6.15: what the entailment route types with one checker, and
        # so one MAX_NODES budget: all of background′, and the layers followed by
        # the smallest conclusion ⊤ (`prove_norm_entailment(elaborated, (), ⊤)`).
        if not _within_limits(self.extended_env, *(p.formula for p in background(self.extended_env))):
            raise ResourceLimit('ResourceLimit: generated background')
        if not _within_limits(self.extended_env, *(f for _, f in self.elaborated.premises()), Top()):
            raise ResourceLimit('ResourceLimit: generated norm layers')

    def _act(self, rule):
        decl = self.env.predicates[rule.core.predicate]
        return decl.regulated.act or rule.core.predicate

    def _incompatible(self, left, right):
        l, r = left.core, right.core
        if (self._act(left) != self._act(right) or
                self.env.predicates[l.predicate].arguments != self.env.predicates[r.predicate].arguments):
            return False
        if l.predicate == r.predicate:
            return l.sign != r.sign
        ld, rd = self.env.predicates[l.predicate].regulated, self.env.predicates[r.predicate].regulated
        return ((ld.role == 'obligation' and ld.permission == r.predicate and l.sign and not r.sign)
                or (rd.role == 'obligation' and rd.permission == l.predicate and r.sign and not l.sign))

    def _rank_pair(self, left, right):
        if left.rank is None or right.rank is None:
            return None
        if left.rank in self.env.ranks_above[right.rank]:
            return (right.rank, left.rank)
        if right.rank in self.env.ranks_above[left.rank]:
            return (left.rank, right.rank)
        return None

    def _outweighs_name(self, low, high, act, sorts):
        # Act key is the permission predicate, or the only regulated predicate.
        keys = [name for name, decl in self.env.predicates.items()
                if decl.regulated is not None and (decl.regulated.act or name) == act
                and decl.arguments == sorts]
        permission = [name for name in keys
                      if self.env.predicates[name].regulated.role == 'permission']
        key = permission[0] if permission else keys[0]
        return f'soft__outweighs__{low}__{high}__{key}'

    def _decisions(self):
        """The decision predicates of E′ and their argument sorts."""
        generated = {}
        for rule in self.rules:
            args = list(self.env.predicates[rule.core.predicate].arguments)
            if rule.mode == 'default':
                generated[_decision_name(rule)] = args
            for party in rule.alterable:
                generated[_decision_name(rule, party)] = args
        if self.env.soft['outranking']['mode'] == 'holistic':
            for left, right in self.collisions:
                pair = self._rank_pair(left, right)
                if pair is not None:
                    name = self._outweighs_name(*pair, self._act(left),
                                                self.env.predicates[left.core.predicate].arguments)
                    generated[name] = list(self.env.predicates[left.core.predicate].arguments)
        return generated

    def _extended_environment(self):
        data = self.env.to_dict()
        predicates = data['vocabulary']['predicates']
        generated = self.decisions
        for name, args in generated.items():
            if name in predicates:
                raise VEError(f'InvalidInput: generated predicate collision {name}')
            predicates[name] = {'arguments': args, 'description': 'soft-norms decision'}
        result = SoftEnvironment(data, generated=True)
        object.__setattr__(result, 'decision_names', frozenset(generated))
        return result

    def _switch(self, rule):
        arity = len(self.env.predicates[rule.core.predicate].arguments)
        return _or_nonempty(_atom(_decision_name(rule, party), arity) for party in rule.alterable)

    def _strict_document(self):
        rules = []
        for rule in self.rules:
            if rule.mode == 'strict':
                core = rule.core
                switch = self._switch(rule)
                rules.append(Norm(core.name, core.predicate, core.sign, core.guard,
                                  (*core.unless, switch) if not isinstance(switch, Bottom) else core.unless,
                                  tuple(p for p in core.over if self.core.by_name[p].name in
                                        {r.core.name for r in self.rules if r.mode == 'strict'})))
        return NormDocument(self.extended_env, rules)

    def _soften(self):
        # Mirror Soften.lean's constructor order. Certificate identities bind
        # these syntax trees, so Boolean equivalence alone is insufficient.
        arity = {p: len(d.arguments) for p, d in self.env.predicates.items()
                 if d.regulated is not None}
        # W1 `children`: sorted by name, whatever the order of rules and `over` entries.
        children = {r.core.name: sorted((x for x in self.rules if r.core.name in x.core.over),
                                        key=lambda x: x.core.name)
                    for r in self.rules}

        def strict_live(rule):
            return And(And(rule.core.guard, Not(_any(rule.core.unless))),
                       Not(self._switch(rule)))

        yields = {}

        def strict_yields(rule, fuel):
            # Shared per rule and fuel, so a precedence DAG with many paths is
            # built as a graph; the limit checks walk its unfolding and stop.
            key = (rule.core.name, fuel)
            if key not in yields:
                own = strict_live(rule) if rule.mode == 'strict' else Bottom()
                yields[key] = Or(own, _any(strict_yields(child, fuel - 1)
                                           for child in children[rule.core.name])
                                 if fuel else Bottom())
            return yields[key]

        def strict_selects(rule):
            if rule.mode != 'strict':
                return Bottom()
            return And(strict_live(rule),
                       Not(_any(strict_yields(child, len(self.rules))
                                for child in children[rule.core.name])))

        def strict_decides(predicate, sign):
            return _any(strict_selects(rule) for rule in self.rules
                        if rule.core.predicate == predicate and rule.core.sign == sign)

        def blocked(rule):
            p = rule.core.predicate
            reg = self.env.predicates[p].regulated
            dual_neg = Bottom()
            dual_pos = Bottom()
            if rule.core.sign and reg.role == 'obligation' and reg.permission:
                dual_neg = strict_decides(reg.permission, False)
            if not rule.core.sign and reg.role == 'permission':
                required = next((q for q, d in self.env.predicates.items()
                                 if d.regulated is not None and d.regulated.permission == p), None)
                if required is not None:
                    dual_pos = strict_decides(required, True)
            return Or(Or(Or(strict_decides(p, True), strict_decides(p, False)),
                         dual_neg), dual_pos)

        def eligible(rule):
            if rule.mode != 'default':
                return Bottom()
            live = And(strict_live(rule),
                       Not(_atom(_decision_name(rule), arity[rule.core.predicate])))
            return And(live, Not(blocked(rule)))

        holistic = self.env.soft['outranking']['mode'] == 'holistic'
        effective = {}

        def eff(rule, fuel):
            key = (rule.core.name, fuel)
            if key not in effective:
                effective[key] = (eligible(rule) if fuel == 0 else
                                  And(eligible(rule), Not(dominated(rule, fuel - 1))))
            return effective[key]

        def dominated(rule, fuel):
            opponents = [other for other in self.rules
                         if other.mode == 'default' and other is not rule
                         and self._incompatible(rule, other)
                         and self._rank_pair(rule, other) is not None]
            terms = []
            for other in opponents:
                low, high = self._rank_pair(rule, other)
                outweighs = (_atom(self._outweighs_name(low, high, self._act(rule),
                                                       self.env.predicates[rule.core.predicate].arguments),
                                    arity[rule.core.predicate]) if holistic else Bottom())
                higher = (And(eff(other, fuel), Not(outweighs) if holistic else Top())
                          if other.rank == high else Bottom())
                lower = (And(eligible(other), outweighs)
                         if holistic and other.rank == low else Bottom())
                terms.append(Or(higher, lower))
            return _any(terms)

        result = []
        for rule in self.rules:
            core = rule.core
            if rule.mode == 'strict':
                derived = self._switch(rule)
            else:
                derived = Or(Or(Or(_atom(_decision_name(rule), arity[core.predicate]),
                                    self._switch(rule)), blocked(rule)),
                             dominated(rule, len(self.env.soft.get('ranks', []))))
            unless = (*core.unless, derived) if not isinstance(derived, Bottom) else core.unless
            if len(unless) > 8 or not _within_limits(self.extended_env, derived, context=(
                    tuple(reversed(self.env.predicates[core.predicate].arguments)))):
                raise ResourceLimit(f'ResourceLimit: derived carve-out of rule {core.name}')
            result.append(Norm(core.name, core.predicate, core.sign, core.guard, unless, core.over))
        try:
            return SoftenedNormDocument(self.extended_env, result)
        except ResourceLimit as exc:
            raise ResourceLimit('ResourceLimit: derived carve-out') from exc

    def _exception_premises(self):
        premises = []
        for rule in self.rules:
            if rule.exception is None:
                continue
            sorts = self.env.predicates[rule.core.predicate].arguments
            atom = _atom(_decision_name(rule), len(sorts))
            for kind in ('sufficient', 'necessary'):
                for index, wire in enumerate(rule.exception[kind]):
                    condition = _Decoder().decode(wire)
                    formula = (Implies(condition, atom) if kind == 'sufficient'
                               else Implies(atom, condition))
                    premises.append((f'soft:exception:{rule.core.name}:{kind}:{index}',
                                     _bind(formula, sorts)))
        return tuple(premises)

    def _expansion_sizes(self):
        """The size of each regulated predicate's expanded outcome, in layer order.

        `_expand` replaces an atom of a lower regulated predicate by that
        predicate's expanded outcome, so the size of an expansion is read from
        the entries before it without expanding anything."""
        sizes = {}
        for predicate in self.elaborated.order:
            sizes[predicate] = self._expanded_size(self.elaborated.outcome(predicate), predicate, sizes)
        return sizes

    def _expanded_size(self, formula, current, sizes=None):
        """The size of `self.elaborated._expand(formula, current)`, without expanding."""
        sizes = self.expansion_sizes if sizes is None else sizes
        return _size(formula, lambda atom: sizes[atom.predicate]
                     if atom.predicate != current and atom.predicate in sizes else None)

    def _check_conflict_targets(self):
        """6.13: the certified conclusion `∀x̄. ¬conflict` of each conflict target, in
        `conflict_targets` order, is within MAX_DEPTH and MAX_NODES on its own. A
        target expands every lower predicate's outcome, so it is sized from the
        expansion table and never built here."""
        doc = self.elaborated
        targets = []
        for predicate in doc.order:
            positive, negative, _ = doc.selection(predicate)
            targets.append((predicate, doc.env.predicates[predicate].arguments,
                            And(*(_Sized(self._expanded_size(f, predicate)) for f in (positive, negative)))))
        for required, decl in sorted(doc.env.predicates.items()):
            reg = decl.regulated
            if reg is not None and reg.permission is not None:
                targets.append((f'{required}->{reg.permission}', decl.arguments,
                                And(_Sized(self.expansion_sizes[required]),
                                    Not(_Sized(self.expansion_sizes[reg.permission])))))
        for name, sorts, conflict in targets:
            if not _fits(_size(_bind(Not(conflict), sorts))):
                raise ResourceLimit(f'ResourceLimit: generated conflict target {name}')

    def _coherence_premises(self):
        """6.11 for the coherence premises, in order: each is sized first and
        expanded only if it is within MAX_DEPTH and MAX_NODES."""
        selections = {p: self.elaborated.selection(p)[2] for p in self.elaborated.order}
        premises = []
        for left, right in self.collisions:
            a, b = sorted((left.core.name, right.core.name))
            label = f'soft:coherence:{a},{b}'
            sides = [(selections[r.core.predicate][r.core.name], r.core.predicate) for r in (left, right)]
            sorts = self.env.predicates[left.core.predicate].arguments
            shape = _bind(Not(And(*(_Sized(self._expanded_size(f, p)) for f, p in sides))), sorts)
            if not _fits(_size(shape)):
                raise ResourceLimit(f'ResourceLimit: generated soft premise {label}')
            la, rb = (self.elaborated._expand(f, p) for f, p in sides)
            premise = _bind(Not(And(la, rb)), sorts)
            if not _within_limits(self.extended_env, premise):
                raise ResourceLimit(f'ResourceLimit: generated soft premise {label}')
            premises.append((label, premise))
        return tuple(premises)
