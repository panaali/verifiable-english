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
from .errors import CheckerUnavailable, DuplicateDeclaration, ResourceLimit, UnknownSymbol, UnsupportedProfile, VEError
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
# The norm-defaults route needs this profile while constructing placeholder
# completions. A submitted soft source uses the narrower Lean soft-route list.
_INHERITED_PROFILES = ('data@0', 'definitions@0', 'documents@1', 'norm-defaults@0', 'time@0')
_SOFT_ROUTE_INHERITED_PROFILES = tuple(p for p in _INHERITED_PROFILES if p != 'norm-defaults@0')
# W1's text that names a profile as the remedy, for each profile the soft route removes before W1. A
# submitted source that lists the profile already has the remedy, so its rejection keeps the route's
# own text instead: the one Python gave it before S4-pre aligned the code.
_DROPPED_PROFILE_TEXTS = {
    'norm-defaults@0': ('UnsupportedProfile: unspecified completion requires norm-defaults@0',
                        'UnsupportedProfile: norm-defaults@0 documents are checked through fill '
                        '(ve.norm_defaults)'),
}
_CHECKER_PROFILES = ('closure@0', 'nary@0', 'order@0')
# Statement layers with their own route over a soft source. The Lean rights route
# strips `rights@0` before the soft decoder (`Rights/Wire.lean`), and the Lean soft
# route's registry does not have it, so check 3.2 refuses it unless that route is
# the caller (`check_soft_source(layers=...)`); a soft source that lists it is
# never accepted by the soft route alone (S3-pre).
LAYER_ROUTES = frozenset({'rights@0'})
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


def soft_route_environment(stripped, listed):
    """W1 over `stripped`, the source with only the profiles the soft route passes on; `listed` is the
    source's own profile list. A W1 text naming a removed profile that `listed` has is restated."""
    try:
        return Environment(stripped)
    except VEError as exc:
        for profile, (text, restated) in _DROPPED_PROFILE_TEXTS.items():
            if profile in listed and profile not in stripped['profiles'] and str(exc) == text:
                raise type(exc)(restated, span=exc.span, path=exc.path) from None
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


def _declarations(data, generated, *, submitted_soft_route=False):
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
    inherited = _SOFT_ROUTE_INHERITED_PROFILES if submitted_soft_route else _INHERITED_PROFILES
    profiles = sorted({p for p in data['profiles'] if p in inherited}
                      | {'norms@0', profile_registry.BASE})
    stripped = {**data, 'profiles': profiles, 'vocabulary': {
        'sorts': vocab['sorts'], 'constants': vocab['constants'],
        'predicates': {name: ({k: v for k, v in entry.items() if k != 'instruction_of'}
                              if type(entry) is dict else entry)
                       for name, entry in vocab['predicates'].items()}}}
    env = _inherited(soft_route_environment, stripped, data['profiles'])
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

def _profiles(data, env, layers=frozenset()):
    profiles = data['profiles']
    fail = lambda message: _fault('SOFT_UNSUPPORTED_PROFILE', f'UnsupportedProfile: {message}',
                                  UnsupportedProfile)
    if profiles != sorted(set(profiles)):
        raise fail('profiles must be sorted and unique')
    for profile in profiles:
        # speech-acts@0 is registered for its own route, not this soft route.
        if (profile not in profile_registry.BY_NAME or profile == 'speech-acts@0'
                or (profile in LAYER_ROUTES and profile not in layers)):
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


def check_soft_source(environment, norms=None, *, generated=False, layers=frozenset(),
                      submitted_soft_route=False):
    """Lean's ordered soft source checks, including a generated layer's lower frame."""
    from .backends.soft_relay import run as _run, wire as _wire
    source = deepcopy(environment)
    if "rights@0" in layers:
        source["profiles"] = [p for p in source["profiles"] if p != "rights@0"]
        source["vocabulary"].pop("rights", None)
    if generated:
        source["vocabulary"]["predicates"] = {
            name: entry for name, entry in source["vocabulary"]["predicates"].items()
            if not name.startswith("soft__")}
    return _run({"id": "soft-elaborate", "kind": "soft-elaborate",
                 "environment": _wire(source), "norms": _wire(list(norms or ()))})


def load_soft_document(environment, norms):
    """Build the Python containers after Lean accepts the complete soft source."""
    from .backends.soft_relay import run as _run, wire as _wire
    _run({"id": "soft-elaborate", "kind": "soft-elaborate",
          "environment": _wire(environment), "norms": _wire(norms)})
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
        if "norm-defaults@0" in data.get("profiles", ()):
            # Fill still constructs placeholder completions in Python (batch 10).
            # The stand-alone soft route rejects this profile before fill runs.
            _envelope(data, None)
            ctx = _declarations(data, generated)
            _profiles(data, ctx.env, self.LAYERS)
            _environment_references(ctx)
            row = {"ranks_above": {name: sorted(above)
                    for name, above in _rank_semantics(ctx).items()}}
        else:
            row = check_soft_source(data, generated=generated, layers=self.LAYERS)
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
        # `readings@1` is the head's layer, never the base vocabulary's (DRI ruling 4's class).
        data['profiles'] = [p for p in data['profiles'] if p not in ('norms@0', 'soft-norms@0', 'readings@1')]
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
        from .backends.soft_relay import run as _run, wire as _wire
        row = _run({"id": "soft-elaborate", "kind": "soft-elaborate",
                    "environment": _wire(env.to_dict()), "norms": _wire(units)})
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
        fields = [_rule_fields(unit, env.soft.get('exception_decider')) for unit in units]
        self.rules = tuple(_soft_rule(field) for field in fields)
        by_name = {rule.core.name: rule for rule in self.rules}
        self.core = NormDocument(env, [rule.core for rule in self.rules])
        self.decisions = {item['name']: item['arguments'] for item in row['decisions']}
        self.collisions = tuple((by_name[item['pair'][0]], by_name[item['pair'][1]])
                                for item in row['colliding_pairs'])
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
        self.expansion_sizes = self._expansion_sizes()

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
