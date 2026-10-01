"""norm-defaults@0: the `unspecified` completion (docs/spec/norm-defaults.md).

An unspecified predicate is unconstrained where no rule decides, except by the
profile premise "whatever must be done may be done" (spec 2.2, 2.4). This
module is the untrusted producer of spec 8: it builds `fill` (2.3), `Fill_T`
(2.4), `table3` and the filling search (2.5), the conflict witnesses and
certificates (3.1) and the gap and default-reached evidence (3.2). Lean
(`VE.NormDefaults`) regenerates and checks each of them; nothing here is a
verdict authority. Every piece of evidence the search returns is also checked
here with the ordinary evaluator before it is returned.

Conventions that the Lean regenerator must share, byte for byte:

* `unspec` is the sorted list of unspecified predicate names;
* E‴ is the author environment without `norm-defaults@0`, each unspecified
  completion replaced by the placeholder `deny`, and one base predicate
  `unsaid__<p>` (p's argument sorts, description `fill_description(p)`) appended
  per unspecified `p` in `unspec` order;
* T‴ is the author rules in order, each root rule on an unspecified `p` with
  `over: [unsaid--<p'>]`, followed by the `F_p` rules in `unspec` order.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from itertools import product

from .ast import And, Binary, Bottom, Exists, Forall, Implies, Not, Or, Unary, _Checker, _to_data
from .environment import Environment
from .errors import InvalidModel, ResourceLimit, UnsupportedProfile, VEError
from .limits import MAX_EVALUATIONS, MAX_PREDICATES
from .norms import Norm, NormDocument, _atom, _bind, _any
from .search import _used_predicates
from .wire import digest

PROFILE = "norm-defaults@0"
MAX_UNSAID_ATOMS = 12
MAX_NAME_BYTES = 56


def unsaid_name(predicate):
    """The fresh base predicate that fills the gaps of `predicate`."""
    return "unsaid__" + predicate


def fill_description(predicate):
    """The description of `unsaid__<p>` (spec 2.3), as Lean's `baseEnvironmentJsonU` writes it."""
    return f"the text does not say whether {predicate}"


def fill_name(predicate):
    """The synthetic rule `F_p`; `_` becomes `-` so that it is a rule name."""
    return "unsaid--" + predicate.replace("_", "-")


class FilledBaseEnvironment(Environment):
    """Background_base(E‴) ++ Fill_T: the base vocabulary with the unsaid tables."""

    def __init__(self, data, premises=()):
        object.__setattr__(self, "fill_premises", tuple(premises))
        super().__init__(data)


class FilledNormDocument(NormDocument):
    """`fill U` (spec 2.3): an ordinary W1 tree over E‴.

    W1's selection, layers, targets and checks are reused unchanged; only the
    base environment gains `Fill_T` in its Background."""
    fill_premises = ()

    def base_environment(self):
        cached = getattr(self, "_filled_base", None)
        if cached is not None:
            return cached
        data = self.env.to_dict()
        data["vocabulary"]["predicates"] = {
            name: decl for name, decl in data["vocabulary"]["predicates"].items()
            if "regulated" not in decl}
        data["profiles"] = [p for p in data["profiles"] if p != "norms@0"]
        base = FilledBaseEnvironment(data, self.fill_premises)
        self._filled_base = base
        return base


@dataclass(frozen=True, slots=True)
class Status:
    """The status of one point (spec 2.5).

    `status` is SETTLED, UNDECIDED or UNKNOWN; `value` is the SETTLED value;
    `evidence` names what settled it (`table3`, `enumeration`), the witness
    pair of an UNDECIDED point (`fillings`), or the budget of an UNKNOWN one."""
    predicate: str
    values: tuple[str, ...]
    status: str
    value: bool | None = None
    evidence: str = ""
    fillings: tuple = ()


@dataclass(frozen=True, slots=True)
class ConflictReport:
    """A 3.1 verdict candidate. A witness carries its filling; `kind` is
    `settled` (the target holds under every filling) or `latent` (it holds
    under the named filling only)."""
    status: str
    target: str | None = None
    tuple: tuple[str, ...] = ()
    kind: str = ""
    filling: dict = field(default_factory=dict)
    under: tuple[tuple[str, tuple[str, ...], bool], ...] = ()
    detail: str = ""
    certificates: dict = field(default_factory=dict)


class _Kleene:
    """Three-valued evaluation over a base situation with unknown unsaid atoms.

    A subformula that mentions neither an unsaid nor a regulated predicate is
    evaluated by the ordinary evaluator. `formula` returns `(value, atoms)`:
    a definite value holds under every filling that agrees with `assignment`,
    and an unknown value depends only on the unassigned unsaid atoms `atoms`
    (so the atoms of an unknown result form its cone)."""

    def __init__(self, document, situation, assignment=None, lookup=None, budget=None):
        from .evaluate import _Evaluator
        self.document = document
        self.unsaid = frozenset(unsaid_name(p) for p in document.unspec)
        self.regulated = frozenset(p for p, d in document.env.predicates.items() if d.regulated is not None)
        self.assignment = {} if assignment is None else assignment
        self.lookup = lookup
        self.evaluator = _Evaluator(document._raw_base(), document._unfilled(situation),
                                    MAX_EVALUATIONS if budget is None else budget, trace=False)
        self.domains = self.evaluator.model.domains
        self._plain = {}

    def plain(self, f):
        key = id(f)
        if key not in self._plain:
            used = _used_predicates(f)
            self._plain[key] = (f, not (used & self.unsaid) and not (used & self.regulated))
        return self._plain[key][1]

    def row(self, f, bindings):
        terms = (f.term,) if isinstance(f, Unary) else (f.left, f.right)
        return tuple(self.evaluator.term(t, bindings) for t in terms)

    def formula(self, f, bindings=()):
        if self.plain(f):
            return self.evaluator.formula(f, bindings)[0], frozenset()
        self.evaluator.tick()
        if isinstance(f, (Unary, Binary)):
            key = (f.predicate, self.row(f, bindings))
            if f.predicate in self.unsaid:
                if key in self.assignment:
                    return self.assignment[key], frozenset()
                return None, frozenset((key,))
            if self.lookup is None:
                raise VEError(f"InvalidInput: unexpanded regulated atom {f.predicate}")
            return self.lookup(*key), frozenset()
        if isinstance(f, Not):
            value, atoms = self.formula(f.body, bindings)
            return (None if value is None else not value), atoms
        if isinstance(f, Implies):
            return self._junction(Not(f.left), f.right, bindings, False)
        if isinstance(f, (And, Or)):
            return self._junction(f.left, f.right, bindings, isinstance(f, And))
        if isinstance(f, (Forall, Exists)):
            conjunctive = isinstance(f, Forall)
            atoms = set()
            unknown = False
            for entity in self.domains[f.sort]:
                value, inner = self.formula(f.body, ((f.sort, entity),) + bindings)
                if value is None:
                    unknown = True
                    atoms |= inner
                elif value is not conjunctive:
                    return value, frozenset()
            return (None, frozenset(atoms)) if unknown else (conjunctive, frozenset())
        raise VEError(f"InvalidInput: unsupported node {type(f).__name__} over an unsaid atom")

    def _junction(self, left, right, bindings, conjunctive):
        lv, la = self.formula(left, bindings)
        if lv is not None and lv is not conjunctive:
            return lv, frozenset()
        rv, ra = self.formula(right, bindings)
        if rv is not None and rv is not conjunctive:
            return rv, frozenset()
        if lv is None or rv is None:
            return None, (la if lv is None else frozenset()) | (ra if rv is None else frozenset())
        return conjunctive, frozenset()


class UnspecifiedDocument:
    """`U = (D, unspec)` on the norms route: the validated author document, its
    limits (spec 8), `fill U` and `Fill_T`. `D` is the author tree itself here;
    the soft route's `D` is `soften T` (`UnspecifiedSoftDocument`)."""

    def __init__(self, env, units):
        if PROFILE not in env.profiles:
            raise UnsupportedProfile("UnsupportedProfile: norm-defaults@0 is required")
        if "soft-norms@0" in env.profiles or env.alternatives is not None:
            raise UnsupportedProfile("UnsupportedProfile: the norm-defaults route is built for norms@0 "
                                     "and soft-norms@0 (UnspecifiedSoftDocument) only")
        self.env = env
        # W1's checks, and the reserved `unsaid--` rule names (2.1).
        self.author = NormDocument(env, units)
        self._build()

    def _build(self):
        env = self.env
        self.unspec = tuple(sorted(p for p, d in env.predicates.items()
                                   if d.regulated is not None and d.regulated.default == "unspecified"))
        self._check_limits()
        self.filled_env = self._filled_environment()
        self._check_ast()
        self.filled = self._filled_class()(self.filled_env, self._filled_rules())
        self._install_soft_premises()
        self.fill_premises = self._fill_premises()
        self.filled.fill_premises = self.fill_premises
        self.filled._filled_base = None
        base = self.filled.base_environment()
        checker = _Checker(base, generated=True)
        for label, formula in self.fill_premises:
            try:
                checker.formula(formula)
            except ResourceLimit as exc:
                raise ResourceLimit(f"fill premise {label}") from exc
        self.document_hash = self.author.document_hash
        self.fill_hash = digest(f"ve-norm-defaults-fill-{env.identity_version}\n",
                                {"environment_id": env.environment_id,
                                 "premises": [[label, _to_data(f)] for label, f in self.fill_premises]})

    def _filled_class(self):
        return FilledNormDocument

    def _install_soft_premises(self):
        pass

    # Spec 8: the author-side limits, in order, before `fill` is built.
    def _check_limits(self):
        # E‴ is D's vocabulary (E′ on the soft route) plus the unsaid predicates.
        if len(self.author.env.predicates) + len(self.unspec) > MAX_PREDICATES:
            raise ResourceLimit("vocabulary size")
        if len(self.author.rules) + len(self.unspec) > 256:
            raise ResourceLimit("rules")
        if any(len(p.encode("utf-8")) > MAX_NAME_BYTES for p in self.unspec):
            raise ResourceLimit("unspecified name length")

    def _check_ast(self):
        checker = _Checker(self.filled_env)
        for rule in self.author.rules:
            context = tuple(reversed(self.env.predicates[rule.predicate].arguments))
            for formula in (rule.guard, *rule.unless):
                checker.formula(formula, context)
        for p in self.unspec:
            context = tuple(reversed(self.env.predicates[p].arguments))
            checker.formula(self._fill_guard(p), context)
        heights = {}

        def height(name):
            if name not in heights:
                heights[name] = 1 + max((height(c) for c in self.author.children[name]), default=0)
            return heights[name]
        if any(height(r.name) > 15 for r in self.author.rules if r.predicate in self.unspec):
            raise ResourceLimit("precedence depth")

    def _fill_guard(self, p):
        return _atom(unsaid_name(p), len(self.env.predicates[p].arguments))

    def _filled_environment(self):
        data = _placeholder(self.author.env.to_dict())
        predicates = data["vocabulary"]["predicates"]
        for p in self.unspec:
            predicates[unsaid_name(p)] = {"arguments": list(self.env.predicates[p].arguments),
                                          "description": fill_description(p)}
        return self._environment_class()(data)

    def _environment_class(self):
        return Environment

    def _filled_rules(self):
        unspec = set(self.unspec)
        rules = [Norm(r.name, r.predicate, r.sign, r.guard, r.unless, (fill_name(r.predicate),))
                 if r.predicate in unspec and not r.over else r for r in self.author.rules]
        rules.extend(Norm(fill_name(p), p, True, self._fill_guard(p)) for p in self.unspec)
        return rules

    # Spec 2.4 and 3.2.
    def author_sides(self, predicate):
        """P_p and N_p over the author rules only (unchanged by `fill`)."""
        return self.author.selection(predicate)[:2]

    def reached(self, predicate):
        """`reachedF`: no author rule decides, substituted on T‴ (open over p's tuple)."""
        positive, negative = self.author_sides(predicate)
        return And(Not(self.filled._expand(positive, predicate)),
                   Not(self.filled._expand(negative, predicate)))

    def gap(self, predicate):
        """`gapF`: `reachedF` for an unspecified predicate, ⊥ otherwise."""
        return self.reached(predicate) if predicate in self.unspec else Bottom()

    def pairs(self):
        """Declared pairs `(required, permission, sorts)`, in W1's target order."""
        return tuple((required, decl.regulated.permission, decl.arguments)
                     for required, decl in sorted(self.env.predicates.items())
                     if decl.regulated is not None and decl.regulated.permission is not None)

    def _fill_premises(self):
        premises = []
        for required, permission, sorts in self.pairs():
            if required not in self.unspec and permission not in self.unspec:
                continue
            conflict = And(self.filled.outcome(required, base=True),
                           Not(self.filled.outcome(permission, base=True)))
            body = Not(And(conflict, Or(self.gap(required), self.gap(permission))))
            premises.append((f"unsaid:pair:{required},{permission}", _bind(body, sorts)))
        return tuple(premises)

    def pair_members(self):
        """The members of declared pairs with an unspecified member."""
        members = set()
        for required, permission, _ in self.pairs():
            if required in self.unspec or permission in self.unspec:
                members.update((required, permission))
        return tuple(sorted(members))

    def completion(self, predicate):
        return self.env.predicates[predicate].regulated.default

    def inherits_from(self, predicate):
        """Unspecified predicates in the guard cone of `predicate` (spec 2.5)."""
        seen, pending, found = set(), [predicate], set()
        while pending:
            current = pending.pop()
            for rule in self.author.rules:
                if rule.predicate != current:
                    continue
                for formula in (rule.guard, *rule.unless):
                    for q in _used_predicates(formula):
                        decl = self.env.predicates.get(q)
                        if decl is None or decl.regulated is None or q in seen:
                            continue
                        seen.add(q)
                        pending.append(q)
                        if q in self.unspec:
                            found.add(q)
        found.discard(predicate)
        return tuple(sorted(found))

    # Situations and fillings.
    def situation_environment(self):
        """The author's base vocabulary: E‴'s base without the unsaid tables."""
        cached = getattr(self, "_situation_env", None)
        if cached is None:
            data = self.filled.base_environment().to_dict()
            for p in self.unspec:
                data["vocabulary"]["predicates"].pop(unsaid_name(p))
            cached = self._situation_env = Environment(data)
        return cached

    def situation(self, model):
        from .model import FiniteModel
        env = self.situation_environment()
        if type(model) is dict:
            relations = model.get("relations")
            if type(relations) is dict:
                for name in sorted(relations):
                    if type(name) is str and name.startswith("unsaid__"):
                        raise InvalidModel(f"{name} is a filling; supply it as a filling, not a table",
                                           generator="norm-defaults")
            model = FiniteModel.from_dict(env, model)
        if model.environment_id != env.environment_id:
            raise VEError("InvalidModel: situation environment does not match the base environment")
        from .background import validate_background
        validate_background(env, model)
        return model

    def canonical_filling(self, situation):
        """True for permission members of pairs, false elsewhere (spec 2.4)."""
        members = set(self.pair_members())
        filling = {}
        for p in self.unspec:
            sorts = self.env.predicates[p].arguments
            rows = (frozenset(product(*(situation.domains[s] for s in sorts)))
                    if p in members and self.env.predicates[p].regulated.role == "permission"
                    else frozenset())
            filling[unsaid_name(p)] = rows
        return filling

    def with_filling(self, situation, filling, *, checked=True):
        """`M.withFill F`: the situation extended by unsaid tables (absent ones empty).

        A checked model is validated against Background_base(E‴) ++ Fill_T, so an
        inadmissible filling is an InvalidModel; an unchecked one is for evaluation
        only and is validated against Background_base(E‴) alone."""
        from .model import FiniteModel
        data = situation.to_dict()
        for p in self.unspec:
            name = unsaid_name(p)
            data["relations"][name] = [list(row) for row in sorted(filling.get(name, ()))]
        return FiniteModel.from_dict(self.filled.base_environment() if checked else self._raw_base(), data)

    def _raw_base(self):
        cached = getattr(self, "_raw_base_env", None)
        if cached is None:
            cached = self._raw_base_env = Environment(self.filled.base_environment().to_dict())
        return cached

    def _unfilled(self, situation):
        cached = getattr(self, "_unfilled_cache", None)
        if cached is None or cached[0] is not situation:
            cached = self._unfilled_cache = (situation, self.with_filling(situation, {}, checked=False))
        return cached[1]

    def fill_valid(self, situation, filling):
        """`fillValid`: the filled situation satisfies Background_base(E‴) ++ Fill_T."""
        from .background import validate_background
        try:
            validate_background(self.filled.base_environment(), self.with_filling(situation, filling))
        except InvalidModel:
            return False
        return True

    def value(self, situation, filling, predicate, values):
        """`O‴_p°(ā)` on the filled situation, two-valued."""
        from .evaluate import _Evaluator
        sorts = self.env.predicates[predicate].arguments
        model = self.with_filling(situation, filling, checked=False)
        return _Evaluator(self._raw_base(), model, MAX_EVALUATIONS, trace=False).formula(
            self.filled.outcome(predicate, base=True), _bindings(sorts, values))[0]

    # Spec 2.5: table3, enumeration, witnesses.
    def table3(self, situation, *, budget=None):
        """Kleene outcomes in DAG order with every unsaid atom unknown, closed by
        the profile rule at gaps only; `None` is unknown.

        This is Lean's `table3` step for step (`tabK`): each symbol is placed once,
        and every row of it, with every close it makes, reads only the table before
        it, so no row reads another row's close. Where a pair closes, the rule sets
        the member being placed (`pairRule`) or the earlier member if it is still
        unknown (`closeRule`); a symbol placed between the two members keeps reading
        the earlier one as unknown, and enumeration settles it instead."""
        situation = self.situation(situation) if type(situation) is dict else situation
        table = {}
        partner = {}
        for required, permission, _ in self.pairs():
            partner[permission] = ("permission", required)
            partner[required] = ("required", permission)
        outcomes = {p: self.filled.outcome(p) for p in self.filled.order}
        gaps = {p: And(Not(self.author_sides(p)[0]), Not(self.author_sides(p)[1])) for p in self.unspec}
        kleene = _Kleene(self, situation, lookup=lambda p, row: table.get((p, row)), budget=budget)

        def at_gap(p, bindings):
            return p in self.unspec and kleene.formula(gaps[p], bindings)[0] is True

        for p in self.filled.order:
            sorts = self.env.predicates[p].arguments
            side, other = partner.get(p, (None, None))
            step = {}
            for row in product(*(situation.domains[s] for s in sorts)):
                bindings = _bindings(sorts, row)
                value, _ = kleene.formula(outcomes[p], bindings)
                if value is None and side is not None and at_gap(p, bindings):
                    if side == "permission" and table.get((other, row)) is True:
                        value = True
                    elif side == "required" and table.get((other, row)) is False:
                        value = False
                step[(p, row)] = value
                if (side is not None and (other, row) in table and table[(other, row)] is None
                        and at_gap(other, bindings)):
                    if side == "required" and value is True:
                        step[(other, row)] = True
                    elif side == "permission" and value is False:
                        step[(other, row)] = False
            # Every row of `p`, and every close it makes, reads the table before `p`.
            table.update(step)
        return table

    def instances(self, situation):
        """Every ground `Fill_T` instance: `(label, sorts, values, body)`."""
        result = []
        for label, formula in self.fill_premises:
            required = label.split(":", 2)[2].split(",")[0]
            sorts = self.env.predicates[required].arguments
            body = formula
            for _ in sorts:
                body = body.body
            for row in product(*(situation.domains[s] for s in sorts)):
                result.append((label, sorts, row, body))
        return tuple(result)

    def cone(self, situation, formula, sorts, values, *, budget=None):
        """The unsaid atoms on which the value of an open formula at `values` depends,
        closed under the `Fill_T` instances that mention them, and those instances.

        Returns `(value, atoms, instances)`; a definite `value` needs no atoms."""
        kleene = _Kleene(self, situation, budget=budget)
        value, atoms = kleene.formula(formula, _bindings(sorts, values))
        if value is not None:
            return value, frozenset(), ()
        pending = [(label, s, row, body, kleene.formula(body, _bindings(s, row)))
                   for label, s, row, body in self.instances(situation)]
        pending = [(label, s, row, body, found) for label, s, row, body, (v, found) in pending
                   if v is None]
        atoms, touching = set(atoms), []
        changed = True
        while changed:
            changed = False
            rest = []
            for item in pending:
                if item[4] & atoms:
                    atoms |= item[4]
                    touching.append(item[:4])
                    changed = True
                else:
                    rest.append(item)
            pending = rest
        return None, frozenset(atoms), tuple(touching)

    def _assignments(self, situation, atoms, instances, *, budget=None):
        """Every assignment of `atoms` that satisfies the instances in `instances`."""
        atoms = sorted(atoms)
        for bits in product((False, True), repeat=len(atoms)):
            assignment = dict(zip(atoms, bits))
            kleene = _Kleene(self, situation, assignment=assignment, budget=budget)
            if all(kleene.formula(body, _bindings(sorts, row))[0] is True
                   for _, sorts, row, body in instances):
                yield assignment

    def _extend(self, situation, assignment):
        """The assignment on its atoms, the canonical filling elsewhere."""
        filling = {name: set(rows) for name, rows in self.canonical_filling(situation).items()}
        for (name, row), value in assignment.items():
            (filling[name].add if value else filling[name].discard)(row)
        return {name: frozenset(rows) for name, rows in filling.items()}

    def status(self, situation, predicate, values, *, max_unsaid_atoms=MAX_UNSAID_ATOMS,
               max_evaluations=MAX_EVALUATIONS):
        """SETTLED, UNDECIDED or UNKNOWN at one point, with checked evidence."""
        from .evaluate import _Exhausted
        situation = self.situation(situation) if type(situation) is dict else situation
        values = tuple(values)
        sorts = self.env.predicates[predicate].arguments
        if len(values) != len(sorts) or any(v not in situation.domains[s] for s, v in zip(sorts, values)):
            raise VEError("InvalidModel: point tuple has wrong length or sort")
        try:
            cached = getattr(self, "_table3_cache", None)
            if cached is None or cached[0] is not situation or cached[1] != max_evaluations:
                cached = self._table3_cache = (situation, max_evaluations,
                                               self.table3(situation, budget=max_evaluations))
            settled = cached[2].get((predicate, values))
            if settled is not None:
                return Status(predicate, values, "SETTLED", settled, "table3")
            formula = self.filled.outcome(predicate, base=True)
            _, atoms, instances = self.cone(situation, formula, sorts, values, budget=max_evaluations)
            if len(atoms) <= max_unsaid_atoms:
                seen = {}
                for assignment in self._assignments(situation, atoms, instances, budget=max_evaluations):
                    kleene = _Kleene(self, situation, assignment=assignment, budget=max_evaluations)
                    value = kleene.formula(formula, _bindings(sorts, values))[0]
                    seen.setdefault(value, assignment)
                    if len(seen) == 2:
                        break
                if len(seen) == 1:
                    (value,) = seen
                    return Status(predicate, values, "SETTLED", value, "enumeration")
                if len(seen) == 2:
                    return self._undecided(situation, predicate, values, seen[True], seen[False])
                raise VEError("InvalidModel: no admissible filling of the situation")
            witness = self._flip_search(situation, predicate, values, formula, atoms, max_evaluations)
            if witness is not None:
                return witness
            return Status(predicate, values, "UNKNOWN", evidence="MAX_UNSAID_ATOMS")
        except _Exhausted:
            return Status(predicate, values, "UNKNOWN", evidence="MAX_EVALUATIONS")

    def _undecided(self, situation, predicate, values, yes, no):
        fillings = (self._extend(situation, yes), self._extend(situation, no))
        if not check_undecided(self, situation, predicate, values, *fillings):
            raise VEError("InvalidModel: undecided witness failed its own check")
        return Status(predicate, values, "UNDECIDED", None, "witness", fillings)

    def _flip_search(self, situation, predicate, values, formula, atoms, budget):
        """Start from the canonical filling and flip one cone atom at a time."""
        from .evaluate import _Evaluator
        sorts = self.env.predicates[predicate].arguments
        work = 0
        candidates = [{}] + [{atom: None} for atom in sorted(atoms)]
        found = {}
        canonical = self.canonical_filling(situation)
        for flip in candidates:
            filling = {name: set(rows) for name, rows in canonical.items()}
            for name, row in flip:
                filling[name] ^= {row}
            filling = {name: frozenset(rows) for name, rows in filling.items()}
            if not self.fill_valid(situation, filling):
                continue
            evaluator = _Evaluator(self._raw_base(), self.with_filling(situation, filling, checked=False),
                                   budget - work, trace=False)
            value = evaluator.formula(formula, _bindings(sorts, values))[0]
            work += evaluator.work
            found.setdefault(value, filling)
            if len(found) == 2:
                fillings = (found[True], found[False])
                if check_undecided(self, situation, predicate, values, *fillings):
                    return Status(predicate, values, "UNDECIDED", None, "witness", fillings)
                return None
        return None

    def statuses(self, situation, **options):
        situation = self.situation(situation) if type(situation) is dict else situation
        result = []
        for p in self.filled.order:
            sorts = self.env.predicates[p].arguments
            for row in product(*(situation.domains[s] for s in sorts)):
                result.append(self.status(situation, p, row, **options))
        return tuple(result)


def _placeholder(data):
    """The environment without norm-defaults@0, each unspecified completion the placeholder deny."""
    data = copy.deepcopy(data)
    data["profiles"] = [p for p in data["profiles"] if p != PROFILE]
    for decl in data["vocabulary"]["predicates"].values():
        if decl.get("regulated", {}).get("default") == "unspecified":
            decl["regulated"]["default"] = "deny"
    return data


class FilledSoftBaseEnvironment(Environment):
    """Background_base(E′‴) ++ Soft_T (++ the rights limitation premises) ++ Fill_T."""

    def __init__(self, data, soft_premises=(), fill_premises=(), rights_premises=()):
        object.__setattr__(self, "soft_premises", tuple(soft_premises))
        object.__setattr__(self, "rights_premises", tuple(rights_premises))
        object.__setattr__(self, "fill_premises", tuple(fill_premises))
        super().__init__(data)


def _filled_soft_class():
    from .softnorms import SoftenedNormDocument

    class FilledSoftNormDocument(SoftenedNormDocument):
        """`fill (soften T)`: a W1 tree over E′‴ whose base carries Soft_T and Fill_T."""
        fill_premises = ()
        soft_premises = ()
        rights_premises = ()

        def base_environment(self):
            cached = getattr(self, "_filled_base", None)
            if cached is not None:
                return cached
            data = self.env.to_dict()
            data["vocabulary"].pop("soft", None)
            data["vocabulary"]["predicates"] = {
                name: {k: v for k, v in decl.items() if k != "instruction_of"}
                for name, decl in data["vocabulary"]["predicates"].items() if "regulated" not in decl}
            data["profiles"] = [p for p in data["profiles"] if p not in ("norms@0", "soft-norms@0")]
            base = FilledSoftBaseEnvironment(data, self.soft_premises, self.fill_premises,
                                             self.rights_premises)
            self._filled_base = base
            return base

    return FilledSoftNormDocument


class UnspecifiedSoftDocument(UnspecifiedDocument):
    """`U = (soften D, unspec)` (spec 2.3 order: `fill` runs after `soften`).

    The soft document is validated and softened over the placeholder
    completions, which `soften` never reads; `fill` then adds the gaps. Exc_T is
    unchanged and Coh_T is regenerated on the filled tree, so its selections
    carry unsaid atoms where guards mention unspecified predicates (3.3)."""

    def __init__(self, env, units):
        from .softnorms import SoftEnvironment, SoftNormDocument
        if PROFILE not in env.profiles:
            raise UnsupportedProfile("UnsupportedProfile: norm-defaults@0 is required")
        if not isinstance(env, SoftEnvironment):
            raise UnsupportedProfile("UnsupportedProfile: soft-norms@0 is required")
        self.env = env
        self.soft = SoftNormDocument(SoftEnvironment(_placeholder(env.to_dict())), units)
        for rule in self.soft.rules:
            if rule.core.name.startswith("unsaid--"):
                raise VEError(f"InvalidInput: reserved name {rule.core.name}")
        self.author = self.soft.elaborated
        self._build()

    def _filled_class(self):
        return _filled_soft_class()

    def _environment_class(self):
        from .softnorms import SoftEnvironment
        return lambda data: SoftEnvironment(data, generated=True)

    def _install_soft_premises(self):
        filled = self.filled
        premises = list(self.soft.exception_premises)
        for left, right in self.soft.collisions:
            a, b = sorted((left.core.name, right.core.name))
            sides = [filled._expand(filled.selection(r.core.predicate)[2][r.core.name], r.core.predicate)
                     for r in (left, right)]
            sorts = self.env.predicates[left.core.predicate].arguments
            premises.append((f"soft:coherence:{a},{b}", _bind(Not(And(*sides)), sorts)))
        filled.soft_premises = tuple(premises)
        filled.rights_premises = tuple(getattr(self.soft.extended_env, "rights_premises", ()))
        filled._filled_base = None


class UnspecifiedRightsDocument(UnspecifiedSoftDocument):
    """`U = (soften (correlate D), unspec)`: correlate and soften run over the
    placeholder completions, then `fill` (spec 2.3, 3.3). The limitation
    premises stay in the filled base; `F_p` is no right line and no narrowing."""

    def __init__(self, env, units):
        from .rights import RightsDocument, RightsEnvironment
        if PROFILE not in env.profiles:
            raise UnsupportedProfile("UnsupportedProfile: norm-defaults@0 is required")
        if not isinstance(env, RightsEnvironment):
            raise UnsupportedProfile("UnsupportedProfile: rights@0 is required")
        self.env = env
        self.rights = RightsDocument(RightsEnvironment(_placeholder(env.to_dict())), units)
        self.soft = self.rights.soft_document
        for rule in self.soft.rules:
            if rule.core.name.startswith("unsaid--"):
                raise VEError(f"InvalidInput: reserved name {rule.core.name}")
        self.author = self.soft.elaborated
        self._build()


def _bindings(sorts, values):
    return tuple(zip(reversed(sorts), reversed(tuple(values))))


def load_document(env, units):
    return UnspecifiedDocument(env, units)


def check_undecided(document, situation, predicate, values, first, second):
    """`undecided_witness_sound`'s premises: both fillings admissible, values opposite."""
    return (document.fill_valid(situation, first) and document.fill_valid(situation, second)
            and document.value(situation, first, predicate, values) is True
            and document.value(situation, second, predicate, values) is False)


def check_settled_by_table3(document, situation, predicate, values):
    return document.table3(situation).get((predicate, tuple(values)))


def _package(document, target, certificate):
    return {"environment_id": document.env.environment_id, "document_hash": document.document_hash,
            "fill_hash": document.fill_hash, "target": target, "certificate": certificate}


def _render_under(document, atoms_values):
    return tuple((name[len("unsaid__"):], row, value) for (name, row), value in sorted(atoms_values.items()))


def check_conflict(document: UnspecifiedDocument, *, model=None, certificates=None, prove=False,
                   max_unsaid_atoms=MAX_UNSAID_ATOMS, max_evaluations=MAX_EVALUATIONS,
                   tableau_steps=10_000):
    """Spec 3.1: a filled witness is a CONFLICT (settled or latent); certificates
    over Background_base(E‴) ++ Fill_T give CONFLICT-FREE; otherwise UNKNOWN."""
    from .entailment import check_entailment_certificate, prove_entailment
    from .evaluate import _Exhausted
    from .norms import check_witness
    base = document.filled.base_environment()
    if model is not None:
        situation = document.situation(model)
        try:
            for target, sorts, formula in document.filled.conflict_targets():
                for values in product(*(situation.domains[s] for s in sorts)):
                    value, atoms, instances = document.cone(situation, formula, sorts, values,
                                                            budget=max_evaluations)
                    if value is True:
                        filling = document.canonical_filling(situation)
                        kind, under = "settled", {}
                    elif value is None and len(atoms) <= max_unsaid_atoms:
                        filling = None
                        for assignment in document._assignments(situation, atoms, instances,
                                                                budget=max_evaluations):
                            kleene = _Kleene(document, situation, assignment=assignment,
                                             budget=max_evaluations)
                            if kleene.formula(formula, _bindings(sorts, values))[0] is True:
                                filling = document._extend(situation, assignment)
                                kind, under = "latent", {atom: assignment[atom] for atom in atoms}
                                break
                        if filling is None:
                            continue
                    else:
                        continue
                    filled = document.with_filling(situation, filling)
                    if not check_witness(document.filled, target, filled, values):
                        raise VEError("InvalidModel: conflict witness failed its own check")
                    return ConflictReport("CONFLICT", target, tuple(values), kind,
                                          {k: sorted(v) for k, v in filling.items()},
                                          _render_under(document, under))
        except _Exhausted:
            return ConflictReport("UNKNOWN", detail="MAX_EVALUATIONS")
    if prove:
        certificates = {}
        for target, sorts, formula in document.filled.conflict_targets():
            result = prove_entailment(base, (), _bind(Not(formula), sorts), max_steps=tableau_steps)
            if result.status != "Found":
                return ConflictReport("UNKNOWN", detail=f"tableau budget or open branch: {target}")
            certificates[target] = _package(document, target, result.certificate)
    if certificates is not None:
        for target, sorts, formula in document.filled.conflict_targets():
            package = certificates.get(target)
            expected = _package(document, target, None)
            if (type(package) is not dict or
                    any(package.get(k) != expected[k] for k in expected if k != "certificate")):
                return ConflictReport("UNKNOWN", detail=f"missing certificate for {target}")
            checked = check_entailment_certificate(base, (), _bind(Not(formula), sorts),
                                                   package.get("certificate"))
            if not checked.valid:
                return ConflictReport("UNKNOWN", detail=f"invalid certificate for {target}")
        return ConflictReport("CONFLICT-FREE", certificates=dict(certificates))
    return ConflictReport("UNKNOWN", detail="tableau budget or search bound")


# Spec 3.2 and 5: gaps, default reached, grounding, inheritance.

@dataclass(frozen=True, slots=True)
class PredicateReport:
    """The 3.2 lines of one regulated predicate.

    `reached` is `none` (a certificate that the rules decide every situation,
    however lower gaps are filled), `reachable` (a checked situation and filling
    where no author rule decides) or `unknown`. For an unspecified predicate it
    is the `gaps` line; for deny and allow it is `default reached`."""
    predicate: str
    completion: str
    reached: str
    witness: tuple = ()
    certificate: dict = field(default_factory=dict)
    inherits_from: tuple[str, ...] = ()
    grounding: str = ""
    situation: object = None

    def lines(self):
        result = [f"completion: {self.completion}"]
        if self.completion == "unspecified":
            result.append(f"gaps: {self.reached}")
        else:
            result.append(f"default reached: {self.reached}")
        if self.grounding:
            result.append(self.grounding)
        if self.inherits_from:
            result.append("inherits_from: [" + ", ".join(self.inherits_from) + "]")
        return tuple(result)


def validate_completions(document, block, unit_ids):
    """The `completions` grounding block (spec 5): each deny or allow completion
    it names cites existing source units and gives a reason."""
    if type(block) is not dict:
        raise VEError("InvalidInput: completions must be an object")
    for predicate, item in block.items():
        decl = document.env.predicates.get(predicate)
        if decl is None or decl.regulated is None:
            raise VEError(f"UnknownSymbol: regulated predicate {predicate}")
        if decl.regulated.default == "unspecified":
            raise VEError(f"InvalidInput: completion of {predicate} is unspecified and cites nothing")
        if (type(item) is not dict or set(item) != {"cites", "reason"} or type(item["cites"]) is not list
                or not item["cites"] or not all(type(x) is str for x in item["cites"])
                or len(set(item["cites"])) != len(item["cites"])
                or type(item["reason"]) is not str or not item["reason"].strip()):
            raise VEError(f"InvalidInput: invalid completion grounding for {predicate}")
        if not set(item["cites"]) <= set(unit_ids):
            raise VEError(f"InvalidInput: completion grounding for {predicate} cites an unknown unit")
    return block


def _reached_witness(document, situation, predicate, max_unsaid_atoms, max_evaluations):
    """A situation tuple and admissible filling where no author rule decides."""
    formula = document.reached(predicate)
    sorts = document.env.predicates[predicate].arguments
    for values in product(*(situation.domains[s] for s in sorts)):
        value, atoms, instances = document.cone(situation, formula, sorts, values, budget=max_evaluations)
        filling = None
        if value is True:
            filling = document.canonical_filling(situation)
        elif value is None and len(atoms) <= max_unsaid_atoms:
            for assignment in document._assignments(situation, atoms, instances, budget=max_evaluations):
                kleene = _Kleene(document, situation, assignment=assignment, budget=max_evaluations)
                if kleene.formula(formula, _bindings(sorts, values))[0] is True:
                    filling = document._extend(situation, assignment)
                    break
        if filling is not None and check_reached(document, situation, filling, predicate, values):
            return tuple(values), filling
    return None


def search_reached(document, predicate, *, max_domain_size=2, max_models=10_000):
    """An untrusted small-model search for a situation, filling and tuple where no
    author rule on `predicate` decides; every result is checked by `check_reached`."""
    from .search import find_countermodel
    sorts = document.env.predicates[predicate].arguments
    base = document.filled.base_environment()
    result = find_countermodel(base, [formula for _, formula in document.fill_premises],
                               _bind(Not(document.reached(predicate)), sorts),
                               max_domain_size=max_domain_size, max_models=max_models)
    if result.status != "Found":
        return None
    data = result.model.to_dict()
    filling = {unsaid_name(p): frozenset(tuple(row) for row in data["relations"].pop(unsaid_name(p)))
               for p in document.unspec}
    situation = document.situation(data)
    for values in product(*(situation.domains[s] for s in sorts)):
        if check_reached(document, situation, filling, predicate, values):
            return situation, tuple(values), filling
    return None


def check_reached(document, situation, filling, predicate, values):
    """A `gaps: reachable` or `default reached` witness: an admissible filling at
    which the reached formula holds."""
    from .evaluate import _Evaluator
    if not document.fill_valid(situation, filling):
        return False
    sorts = document.env.predicates[predicate].arguments
    model = document.with_filling(situation, filling, checked=False)
    return _Evaluator(document._raw_base(), model, MAX_EVALUATIONS, trace=False).formula(
        document.reached(predicate), _bindings(sorts, values))[0] is True


def check_reached_certificate(document, predicate, package):
    """`gaps: none` / no `default reached`: ∀x̄. P° ∨ N° over Background_base(E‴) ++ Fill_T."""
    from .entailment import check_entailment_certificate
    expected = _package(document, f"reached:{predicate}", None)
    if type(package) is not dict or any(package.get(k) != expected[k] for k in expected if k != "certificate"):
        return False
    sorts = document.env.predicates[predicate].arguments
    return check_entailment_certificate(document.filled.base_environment(), (),
                                        _bind(Not(document.reached(predicate)), sorts),
                                        package.get("certificate")).valid


def report(document, *, model=None, prove=False, certificates=None, completions=None,
           translation=False, max_unsaid_atoms=MAX_UNSAID_ATOMS, max_evaluations=MAX_EVALUATIONS,
           tableau_steps=10_000, search_domain_size=None, predicates=None):
    """One PredicateReport per regulated predicate, in layer order (spec 3.2);
    `predicates` restricts the report to the named ones.

    A witness needs a supplied base situation; a certificate is proved (`prove`)
    or replayed (`certificates`, keyed by predicate). `UngroundedDefault` is
    reported for translation documents only, and only for a deny or allow
    completion with a `default reached` witness and no `completions` citation."""
    from .entailment import prove_entailment
    from .evaluate import _Exhausted
    situation = document.situation(model) if model is not None else None
    completions = {} if completions is None else completions
    result = []
    for predicate in document.filled.order:
        if predicates is not None and predicate not in predicates:
            continue
        completion = document.completion(predicate)
        reached, witness, certificate, found_in = "unknown", (), {}, situation
        if situation is not None:
            try:
                found = _reached_witness(document, situation, predicate, max_unsaid_atoms, max_evaluations)
            except _Exhausted:
                found = None
            if found is not None:
                reached, witness = "reachable", found
        elif search_domain_size is not None:
            found = search_reached(document, predicate, max_domain_size=search_domain_size)
            if found is not None:
                found_in, witness, reached = found[0], (found[1], found[2]), "reachable"
        if reached == "unknown":
            package = (certificates or {}).get(predicate)
            if package is None and prove:
                sorts = document.env.predicates[predicate].arguments
                proof = prove_entailment(document.filled.base_environment(), (),
                                         _bind(Not(document.reached(predicate)), sorts),
                                         max_steps=tableau_steps)
                if proof.status == "Found":
                    package = _package(document, f"reached:{predicate}", proof.certificate)
            if package is not None and check_reached_certificate(document, predicate, package):
                reached, certificate = "none", package
        grounding = ""
        if completion != "unspecified":
            if predicate in completions:
                grounding = "grounded: " + ", ".join(completions[predicate]["cites"])
            elif translation and reached == "reachable":
                grounding = f"UngroundedDefault: {predicate}"
        result.append(PredicateReport(predicate, completion, reached, witness, certificate,
                                      document.inherits_from(predicate), grounding,
                                      found_in if reached == "reachable" else None))
    return tuple(result)


def gaps_residual(reports):
    """The document residual line `gaps` (spec 3.2)."""
    return {"gaps": sorted(r.predicate for r in reports
                           if r.completion == "unspecified" and r.reached == "reachable"),
            "ungrounded_defaults": sum(r.grounding.startswith("UngroundedDefault") for r in reports)}


# Spec 6.3: the migration audit (untrusted, report-only; it never rewrites).

def _profiled(raw, switched=()):
    """The environment under norm-defaults@0 with the named completions switched."""
    data = copy.deepcopy(raw)
    data["profiles"] = sorted(set(data["profiles"]) | {PROFILE})
    for predicate in switched:
        data["vocabulary"]["predicates"][predicate]["regulated"]["default"] = "unspecified"
    return Environment(data)


def audit_completions(env, units, *, model=None, prove=True, **options):
    """For every deny or allow completion: its `default reached` evidence; if it
    is reached, the statuses that switching it to `unspecified` changes on the
    supplied situation; if not, the `gaps` line of the predicate on the switched
    document, whose certificate is the one that switching preserves meaning.

    `unreached_switch` (spec 7) needs "no admissible filling of `U.switch p`
    reaches `p`": a `default reached: none` certificate on `U` is not enough,
    because switching `p` can make a filling of another gap admissible that
    `U`'s pair premises excluded (spec 6.3's counterexample). So the certificate
    is proved on `_profiled(raw, (p,))`, never taken from `U`'s own report."""
    raw = env.to_dict()
    document = UnspecifiedDocument(_profiled(raw), units)
    lines = {r.predicate: r for r in report(document, model=model, prove=prove, **options)}
    before = None
    if model is not None:
        situation = document.situation(model)
        before = {(s.predicate, s.values): s for s in document.statuses(situation)}
    result = []
    for predicate in document.filled.order:
        if document.completion(predicate) == "unspecified":
            continue
        line = lines[predicate]
        entry = {"predicate": predicate, "completion": line.completion, "default_reached": line.reached}
        if line.reached == "reachable":
            entry["witness"] = _witness_json(line.witness)
        switched = UnspecifiedDocument(_profiled(raw, (predicate,)), units)
        if line.reached != "reachable":
            (gap,) = report(switched, model=model, prove=prove, predicates=(predicate,), **options)
            entry["switched_gaps"] = gap.reached
            if gap.reached == "none":
                entry["certificate"] = gap.certificate
            elif gap.reached == "reachable":
                entry["switched_witness"] = _witness_json(gap.witness)
        if before is not None:
            situation = switched.situation(model)
            changes = []
            for status in switched.statuses(situation):
                old = before[(status.predicate, status.values)]
                if (old.status, old.value) != (status.status, status.value):
                    changes.append({"predicate": status.predicate, "tuple": list(status.values),
                                    "before": _status_text(old), "after": _status_text(status)})
            entry["changes_if_switched"] = changes
        result.append(entry)
    return {"environment_id": env.environment_id, "completions": result}


def _witness_json(witness):
    values, filling = witness
    return {"tuple": list(values), "filling": {k: [list(r) for r in sorted(v)] for k, v in filling.items()}}


def _status_text(status):
    if status.status == "SETTLED":
        return "SETTLED " + ("yes" if status.value else "no")
    return status.status if status.status == "UNDECIDED" else f"UNKNOWN ({status.evidence})"


def load_audit_source(raw: bytes):
    """The environment and active norm units of a ve-document@1 (norm units not
    under an active reading set) or of JSON `{"environment", "norms"}`."""
    from .wire import loads_json
    if raw.startswith(b"---\n"):
        from .document import _parts, _split
        from .readings import active_reading_sets
        meta, _, _ = _split(raw)
        units = [unit for unit, _ in _parts(meta.get("units", []))]
        under = {r["unit"] for r in active_reading_sets(meta.get("reading_sets", []))}
        norms = [u["content"] for u in units if u.get("kind") == "norm" and u.get("id") not in under
                 and type(u.get("content")) is dict and set(u["content"]) == {"norm"}]
        return Environment(meta["environment"]), norms
    data = loads_json(raw)
    if type(data) is not dict or set(data) != {"environment", "norms"} or type(data["norms"]) is not list:
        raise VEError("InvalidInput: expected a ve-document@1 or {environment, norms}")
    return Environment(data["environment"]), data["norms"]
