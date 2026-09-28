"""Python schema and regeneration for the soft-norms@0 statement layer.

Decision symbols and soft background premises are derived from the source
norms, never accepted as authored premises or trusted wire fields.
"""
from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
import hashlib
import json

from .ast import And, Implies, Not, Or, Top, Bottom, _Checker, _Decoder, _to_data, formula_to_data
from .background import dependency_order
from .environment import Environment, valid_identifier
from .errors import DuplicateDeclaration, ResourceLimit, UnknownSymbol, UnsupportedProfile, VEError
from .norms import Norm, NormDocument, _all, _any, _atom, _bind
from .search import _used_predicates
from .wire import digest


def soft_digest(domain, payload):
    """The soft norm wire permits null for inherited exception deciders."""
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(domain.encode('ascii') + encoded).hexdigest()


def _decider(value, where):
    if type(value) is not str or not value or len(value.encode('utf-8')) > 64:
        raise VEError(f"InvalidInput: invalid decider for {where}")
    return value


def _names(values, label, maximum):
    if type(values) is not list:
        raise VEError(f"InvalidInput: {label} must be an array")
    if len(values) > maximum:
        raise ResourceLimit(label)
    seen = set()
    for name in values:
        if not valid_identifier(name) or '__' in name:
            raise VEError(f"InvalidInput: invalid soft name {name}")
        if name in seen:
            kind = "party" if label == "parties" else "rank"
            raise DuplicateDeclaration(f"DuplicateDeclaration: {kind} {name}")
        seen.add(name)
    return tuple(values)


class SoftEnvironment(Environment):
    """A W1 environment with an identity-bound soft declaration block.

    The underlying Environment validates every ordinary declaration. The
    original soft metadata is restored in to_dict, so canonical identity binds
    it without changing the bytes of environments that lack the profile.
    """
    def __init__(self, data, *, generated=False):
        if type(data) is not dict or 'soft-norms@0' not in data.get('profiles', []):
            raise UnsupportedProfile('soft-norms@0 is required')
        if 'norms@0' not in data['profiles']:
            raise UnsupportedProfile('soft-norms@0 requires norms@0')
        raw = deepcopy(data)
        vocab = raw.get('vocabulary')
        if type(vocab) is not dict:
            raise VEError('InvalidInput: missing vocabulary')
        soft = vocab.pop('soft', None)
        if soft is None:
            soft = {'parties': [], 'ranks': [], 'outranks': [], 'ties': [],
                    'outranking': {'mode': 'strict'}}
            has_block = False
        else:
            has_block = True
        if type(soft) is not dict or set(soft) - {'parties', 'ranks', 'outranks', 'ties', 'outranking', 'exception_decider'}:
            raise VEError('InvalidInput: invalid soft block')
        parties = _names(soft.get('parties', []), 'parties', 8)
        ranks = _names(soft.get('ranks', []), 'ranks', 16)
        flag = soft.get('outranking')
        if type(flag) is not dict or set(flag) - {'mode', 'decided_by'} or flag.get('mode') not in ('strict', 'holistic'):
            raise VEError('InvalidInput: invalid outranking flag')
        if flag['mode'] == 'holistic':
            if 'decided_by' not in flag:
                raise VEError('MissingExceptionDecider: outranking')
            _decider(flag['decided_by'], 'outranking')
        elif 'decided_by' in flag:
            raise VEError('InvalidInput: strict outranking has no decider')
        if 'exception_decider' in soft:
            _decider(soft['exception_decider'], 'exception')
        edges, ties = [], []
        for field, output in (('outranks', edges), ('ties', ties)):
            value = soft.get(field, [])
            if type(value) is not list:
                raise VEError(f'InvalidInput: {field} must be an array')
            for pair in value:
                if type(pair) is not list or len(pair) != 2 or any(type(x) is not str for x in pair):
                    raise VEError(f'InvalidInput: invalid {field} pair')
                for name in pair:
                    if name not in ranks:
                        raise VEError(f'UnknownRank: {name}')
                if pair[0] == pair[1] or tuple(pair) in output:
                    raise VEError(f'InvalidInput: invalid {field} pair')
                output.append(tuple(pair))
        dependencies = {r: set() for r in ranks}
        for higher, lower in edges:
            dependencies[higher].add(lower)
        dependency_order(dependencies)
        above = {r: set() for r in ranks}
        for higher, lower in edges:
            above[lower].add(higher)
        for rank in ranks:
            pending = list(above[rank])
            while pending:
                parent = pending.pop()
                for ancestor in above[parent] - above[rank]:
                    above[rank].add(ancestor)
                    pending.append(ancestor)
        for a, b in ties:
            if a in above[b] or b in above[a]:
                raise VEError(f'TieAgainstOrder: {a}, {b}')
        if len({frozenset(pair) for pair in ties}) != len(ties):
            raise DuplicateDeclaration('DuplicateDeclaration: tie')
        instructions = {}
        for name, entry in vocab.get('predicates', {}).items():
            if type(entry) is not dict:
                continue
            if 'instruction_of' in entry:
                party = entry.pop('instruction_of')
                if party not in parties:
                    raise UnknownSymbol(f'UnknownSymbol: party {party}')
                if 'regulated' in entry or 'defined' in entry:
                    raise VEError(f'InvalidInput: instruction_of on {name}')
                instructions[name] = party
            if not generated and name.startswith('soft__'):
                raise VEError(f'InvalidInput: reserved predicate {name}')
            if not generated and '__' in name and 'regulated' in entry:
                raise VEError(f'InvalidInput: act-key predicate contains __: {name}')
        object.__setattr__(self, 'soft', soft)
        object.__setattr__(self, 'soft_present', has_block)
        object.__setattr__(self, 'instruction_of', instructions)
        object.__setattr__(self, 'ranks_above', above)
        object.__setattr__(self, 'soft_premises', ())
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
    if type(content) is not dict or set(content) != {'norm'} or type(content['norm']) is not dict:
        raise VEError('InvalidInput: expected norm object')
    raw = content['norm']
    extra = set(raw) - {'name', 'predicate', 'sign', 'guard', 'unless', 'over',
                        'mode', 'rank', 'alterable', 'exception', 'hard'}
    if extra:
        raise VEError(f'InvalidInput: unknown soft norm fields {sorted(extra)}')
    core = NormDocument._decode({'norm': {k: raw[k] for k in ('name', 'predicate', 'sign', 'guard', 'unless', 'over')
                                         if k in raw}})
    mode = raw.get('mode', 'strict')
    if mode not in ('strict', 'default'):
        raise VEError(f'InvalidInput: invalid mode for rule {core.name}')
    rank = raw.get('rank')
    if rank is not None and rank not in env.soft.get('ranks', []):
        raise VEError(f'UnknownRank: rule {core.name}, {rank}')
    alterable = raw.get('alterable', [])
    if (type(alterable) is not list or any(type(x) is not str for x in alterable)
            or alterable != sorted(set(alterable))):
        raise VEError(f'InvalidInput: alterable of rule {core.name} must be sorted and distinct')
    for party in alterable:
        if party not in env.soft.get('parties', []):
            raise UnknownSymbol(f'UnknownSymbol: party {party}')
    hard = raw.get('hard', False)
    if type(hard) is not bool:
        raise VEError(f'InvalidInput: hard of rule {core.name} must be Boolean')
    if hard and (mode != 'strict' or alterable):
        raise VEError(f'HardConstraintAltered: rule {core.name}')
    exception = raw.get('exception')
    if mode == 'strict' and exception is not None:
        raise VEError(f'InvalidInput: rule {core.name} is strict and declares an exception')
    if mode == 'default':
        if (type(exception) is not dict or
                set(exception) - {'decided_by', 'sufficient', 'necessary', 'factors'} or
                not {'sufficient', 'necessary', 'factors'} <= set(exception)):
            raise VEError(f'InvalidInput: rule {core.name} needs an exception')
        decider = (env.soft.get('exception_decider') if exception.get('decided_by') is None
                   else exception['decided_by'])
        if decider is None:
            raise VEError(f'MissingExceptionDecider: rule {core.name}')
        _decider(decider, f'rule {core.name}')
        canonical_exception = {**exception}
        for kind in ('sufficient', 'necessary'):
            if type(exception[kind]) is not list:
                raise VEError(f'InvalidInput: exception {kind} must be an array')
            if core.predicate not in env.predicates:
                raise UnknownSymbol(f'predicate {core.predicate}')
            context = tuple(reversed(env.predicates[core.predicate].arguments))
            canonical_exception[kind] = []
            for data in exception[kind]:
                formula = _Decoder().decode(data)
                _Checker(env).formula(formula, context)
                canonical_exception[kind].append(_to_data(formula))
                for predicate in _used_predicates(formula):
                    decl = env.predicates[predicate]
                    if decl.regulated is not None or decl.defined is not None or predicate.startswith('soft__'):
                        raise VEError(f'InvalidInput: exception condition of rule {core.name} mentions {predicate}')
        if type(exception['factors']) is not list or any(type(x) is not str or len(x.encode('utf-8')) > 200
                                                        for x in exception['factors']):
            raise VEError(f'InvalidInput: invalid factors of rule {core.name}')
        exception = canonical_exception
    return SoftRule(core, mode, rank, tuple(alterable), exception, hard)


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


def _or_nonempty(items):
    items = tuple(items)
    return _any(items) if items else Bottom()


class SoftNormDocument:
    """Validated soft tree, its W1 elaboration, and regenerated base premises."""
    def __init__(self, env: SoftEnvironment, units):
        if not isinstance(env, SoftEnvironment):
            raise UnsupportedProfile('soft-norms@0 is required')
        self.env = env
        self.rules = tuple(decode_rule(env, x) for x in units)
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
        self.collisions = tuple(sorted(((min(left, right, key=lambda r: r.core.name),
                                         max(left, right, key=lambda r: r.core.name))
                                        for i, left in enumerate(self.rules)
                                        for right in self.rules[i + 1:]
                                        if left.mode == right.mode == 'default'
                                        and self._incompatible(left, right)),
                                       key=lambda pair: (pair[0].core.name, pair[1].core.name)))
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
        self.exception_premises = self._exception_premises()
        self.coherence_premises = self._coherence_premises()
        for label, formula in (*self.exception_premises, *self.coherence_premises):
            try:
                formula_to_data(self.extended_env, formula, _generated=True)
            except ResourceLimit as exc:
                raise ResourceLimit(f'generated soft premise {label}') from exc
        object.__setattr__(self.extended_env, 'soft_premises',
                           (*self.exception_premises, *self.coherence_premises))
        self.elaborated.soft_premises = self.extended_env.soft_premises

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

    def _extended_environment(self):
        data = self.env.to_dict()
        predicates = data['vocabulary']['predicates']
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
        children = {r.core.name: [x for x in self.rules if r.core.name in x.core.over]
                    for r in self.rules}

        def strict_live(rule):
            return And(And(rule.core.guard, Not(_any(rule.core.unless))),
                       Not(self._switch(rule)))

        def strict_yields(rule, fuel):
            own = strict_live(rule) if rule.mode == 'strict' else Bottom()
            return Or(own, _any(strict_yields(child, fuel - 1) for child in children[rule.core.name])
                      if fuel else Bottom())

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
            if len(unless) > 8:
                raise ResourceLimit(f'derived carve-out of rule {core.name}')
            result.append(Norm(core.name, core.predicate, core.sign, core.guard, unless, core.over))
        try:
            return SoftenedNormDocument(self.extended_env, result)
        except ResourceLimit as exc:
            raise ResourceLimit('derived carve-out') from exc

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

    def _coherence_premises(self):
        selections = {p: self.elaborated.selection(p)[2] for p in self.elaborated.order}
        premises = []
        for left, right in self.collisions:
            a, b = sorted((left.core.name, right.core.name))
            la = self.elaborated._expand(selections[left.core.predicate][left.core.name],
                                         left.core.predicate)
            rb = self.elaborated._expand(selections[right.core.predicate][right.core.name],
                                         right.core.predicate)
            sorts = self.env.predicates[left.core.predicate].arguments
            premises.append((f'soft:coherence:{a},{b}', _bind(Not(And(la, rb)), sorts)))
        return tuple(premises)
