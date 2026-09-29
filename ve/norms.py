"""W1 norm units, Catala selection, completions, and generated FOL premises.

The checker consumes only the generated formulas.  Norm objects and their
environment declarations are the source of those formulas, never supplied
premises from an untrusted document.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import re

from .assurance import semantic_entry
from .ast import (And, Binary, Bottom, Exists, Forall, Implies, Not, Or,
                  Top, Unary, Var, _Checker, _Decoder, _to_data)
from .background import dependency_order
from .errors import DuplicateDeclaration, ResourceLimit, VEError
from .search import _used_predicates
from .wire import digest, require_fields

_NAME = re.compile(r"[a-z][a-z0-9-]*\Z", re.ASCII)


def _all(items):
    result = Top()
    for item in items:
        result = And(result, item)
    return result


def _any(items):
    result = Bottom()
    for item in items:
        result = Or(result, item)
    return result


def _atom(predicate, arity, terms=None):
    terms = tuple(Var(arity - i - 1) for i in range(arity)) if terms is None else tuple(terms)
    return Unary(predicate, terms[0]) if arity == 1 else Binary(predicate, *terms)


def _bind(formula, sorts, binder=Forall):
    for sort in reversed(sorts):
        formula = binder(sort, formula)
    return formula


def _shift_term(term, depth):
    from .ast import Add, Scale
    if isinstance(term, Var):
        return Var(term.index + depth)
    if isinstance(term, Add):
        return Add(_shift_term(term.left, depth), _shift_term(term.right, depth))
    if isinstance(term, Scale):
        return Scale(term.coefficient, _shift_term(term.term, depth))
    return term


def _instantiate(formula, terms, depth=0):
    """Replace the tuple variables of an open formula, respecting inner binders."""
    from .ast import Eq, Reach, Body, Lt, Le
    if isinstance(formula, (Unary, Binary)):
        args = (formula.term,) if isinstance(formula, Unary) else (formula.left, formula.right)
        mapped = tuple(_replace_term(x, terms, depth) for x in args)
        return Unary(formula.predicate, mapped[0]) if len(mapped) == 1 else Binary(formula.predicate, *mapped)
    if isinstance(formula, (Eq, Lt, Le)):
        return type(formula)(_replace_term(formula.left, terms, depth),
                             _replace_term(formula.right, terms, depth))
    if isinstance(formula, Reach):
        edge = (Body(formula.edge.sort, _instantiate(formula.edge.formula, terms, depth + 2))
                if isinstance(formula.edge, Body) else formula.edge)
        return Reach(formula.kind, edge, _replace_term(formula.left, terms, depth),
                     _replace_term(formula.right, terms, depth))
    if isinstance(formula, Not):
        return Not(_instantiate(formula.body, terms, depth))
    if isinstance(formula, (And, Or, Implies)):
        return type(formula)(_instantiate(formula.left, terms, depth),
                             _instantiate(formula.right, terms, depth))
    if isinstance(formula, (Forall, Exists)):
        return type(formula)(formula.sort, _instantiate(formula.body, terms, depth + 1))
    return formula


def _replace_term(term, terms, depth):
    from .ast import Add, Scale
    if isinstance(term, Var):
        return term if term.index < depth else _shift_term(terms[len(terms) - 1 - (term.index - depth)], depth)
    if isinstance(term, Add):
        return Add(_replace_term(term.left, terms, depth), _replace_term(term.right, terms, depth))
    if isinstance(term, Scale):
        return Scale(term.coefficient, _replace_term(term.term, terms, depth))
    return term


def _regulated_closure(formula, regulated):
    """A closure edge cannot be completed as an ordinary regulated atom."""
    from .ast import Reach, Named
    if isinstance(formula, Reach):
        edge = {formula.edge.relation} if isinstance(formula.edge, Named) else _used_predicates(formula.edge.formula)
        return bool(edge & regulated)
    if isinstance(formula, (Not, Forall, Exists)):
        return _regulated_closure(formula.body, regulated)
    if isinstance(formula, (And, Or, Implies)):
        return (_regulated_closure(formula.left, regulated) or
                _regulated_closure(formula.right, regulated))
    return False


@dataclass(frozen=True, slots=True)
class Norm:
    name: str
    predicate: str
    sign: bool
    guard: object
    unless: tuple[object, ...] = ()
    over: tuple[str, ...] = ()

    def to_dict(self):
        return {"norm": {"name": self.name, "predicate": self.predicate, "sign": self.sign,
                         "guard": _to_data(self.guard), "unless": [_to_data(x) for x in self.unless],
                         "over": list(self.over)}}


def norm_meaning_id(env, rule):
    """The W1 unit identity uses the same AST domain as formula units."""
    return digest(f"ve-meaning-{env.identity_version}\n",
                  {"environment_id": env.environment_id, "ast": rule.to_dict()})


class NormDocument:
    def __init__(self, env, units):
        if "norms@0" not in env.profiles:
            raise VEError("UnsupportedProfile: norms@0 is required")
        if len(units) > 256:
            raise ResourceLimit("rules")
        self.env = env
        self.rules = tuple(self._decode(x) if type(x) is dict else x for x in units)
        names = set()
        checker = _Checker(env)
        for rule in self.rules:
            if not isinstance(rule, Norm):
                raise VEError("InvalidInput: expected norm unit")
            if type(rule.name) is not str or len(rule.name) > 64 or not _NAME.fullmatch(rule.name):
                raise VEError(f"InvalidInput: invalid rule name {rule.name!r}")
            if rule.name in names:
                raise DuplicateDeclaration(f"rule {rule.name}")
            names.add(rule.name)
            if rule.predicate not in env.predicates or env.predicates[rule.predicate].regulated is None:
                raise VEError(f"UnknownSymbol: regulated predicate {rule.predicate}")
            if type(rule.sign) is not bool or len(rule.unless) > 8:
                raise VEError("InvalidInput: invalid sign or too many carve-outs")
            decl = env.predicates[rule.predicate]
            context = tuple(reversed(decl.arguments))
            for formula in (rule.guard, *rule.unless):
                checker.formula(formula, context)
                if _regulated_closure(formula, {p for p, d in env.predicates.items()
                                                if d.regulated is not None}):
                    raise VEError("UnsupportedProfile: regulated closure edge in norm guard")
        by_name = {r.name: r for r in self.rules}
        for rule in self.rules:
            for parent in rule.over:
                if parent not in by_name:
                    raise VEError(f"UnknownRule: rule {parent}")
                if by_name[parent].predicate != rule.predicate:
                    raise VEError(f"PrecedenceAcrossPredicates: rule {rule.name} on {rule.predicate}, rule {parent} on {by_name[parent].predicate}")
        dependency_order({r.name: set(r.over) for r in self.rules})
        children = {r.name: [] for r in self.rules}
        for rule in self.rules:
            for parent in rule.over:
                children[parent].append(rule.name)
        self.children = {name: tuple(sorted(items)) for name, items in children.items()}
        depth = {}
        def height(name):
            if name not in depth:
                depth[name] = 1 + max((height(child) for child in self.children[name]), default=0)
            return depth[name]
        if any(height(name) > 16 for name in children):
            raise ResourceLimit("precedence depth")
        dependencies = {p: set() for p, d in env.predicates.items() if d.regulated is not None}
        for rule in self.rules:
            dependencies[rule.predicate].update(
                q for f in (rule.guard, *rule.unless) for q in _used_predicates(f)
                if q in dependencies)
        self.order = dependency_order(dependencies)
        self.by_name = by_name
        self.document_hash = digest(f"ve-norms-{env.identity_version}\n",
                                    {"environment_id": env.environment_id,
                                     "document": [r.to_dict() for r in self.rules]})

    @staticmethod
    def _decode(data):
        require_fields(data, {"norm"})
        raw = data["norm"]
        require_fields(raw, {"name", "predicate", "sign", "guard", "unless", "over"})
        if type(raw["unless"]) is not list or type(raw["over"]) is not list:
            raise VEError("InvalidInput: unless and over must be arrays")
        if type(raw["predicate"]) is not str or not all(type(p) is str for p in raw["over"]):
            raise VEError("InvalidInput: rule predicate and precedence edges must be strings")
        decoder = _Decoder()
        return Norm(raw["name"], raw["predicate"], raw["sign"], decoder.decode(raw["guard"]),
                    tuple(decoder.decode(x) for x in raw["unless"]), tuple(raw["over"]))

    def selection(self, predicate):
        if type(self) is NormDocument and "soft-norms@0" in self.env.profiles:
            raise VEError("UnsupportedProfile: soft rules require SoftNormDocument.elaborated")
        rules = [r for r in self.rules if r.predicate == predicate]
        if predicate not in self.env.predicates or self.env.predicates[predicate].regulated is None:
            raise VEError(f"UnknownSymbol: regulated predicate {predicate}")
        applies = {r.name: And(r.guard, Not(_any(r.unless))) for r in rules}
        yields = {}
        def subtree(name):
            if name not in yields:
                yields[name] = Or(applies[name], _any(subtree(child) for child in self.children[name]))
            return yields[name]
        selected = {r.name: And(applies[r.name], Not(_any(subtree(c) for c in self.children[r.name])))
                    for r in rules}
        return (_any(selected[r.name] for r in rules if r.sign),
                _any(selected[r.name] for r in rules if not r.sign), selected)

    def outcome(self, predicate, *, base=False):
        positive, negative, _ = self.selection(predicate)
        default = self.env.predicates[predicate].regulated.default
        outcome = positive if default == "deny" else Not(negative)
        return self._expand(outcome, predicate) if base else outcome

    def _expand(self, formula, current, stack=()):
        """Replace lower regulated atoms by completed outcomes."""
        if isinstance(formula, (Unary, Binary)) and formula.predicate != current:
            decl = self.env.predicates[formula.predicate]
            if decl.regulated is not None:
                if formula.predicate in stack:
                    raise VEError("DependencyCycle: " + formula.predicate)
                args = (formula.term,) if isinstance(formula, Unary) else (formula.left, formula.right)
                return _instantiate(self._expand(self.outcome(formula.predicate), formula.predicate,
                                                  (*stack, formula.predicate)), args)
        if isinstance(formula, Not):
            return Not(self._expand(formula.body, current, stack))
        if isinstance(formula, (And, Or, Implies)):
            return type(formula)(self._expand(formula.left, current, stack),
                                 self._expand(formula.right, current, stack))
        if isinstance(formula, (Forall, Exists)):
            return type(formula)(formula.sort, self._expand(formula.body, current, stack))
        return formula

    @semantic_entry("norms.elaborate")
    def elaborate(self, predicate):
        positive, negative, _ = self.selection(predicate)
        decl = self.env.predicates[predicate]
        atom = _atom(predicate, len(decl.arguments))
        silence = And(Not(positive), Not(negative))
        default = atom if decl.regulated.default == "allow" else Not(atom)
        return _bind(_all((Implies(positive, atom), Implies(negative, Not(atom)),
                           Implies(silence, default))), decl.arguments)

    @semantic_entry("norms.elaborate")
    def premises(self):
        return tuple((f"layer:norms:{p}", self.elaborate(p)) for p in self.order)

    def meaning_id(self, name):
        """A rule identity binds its AST and environment, never its display number."""
        return norm_meaning_id(self.env, self.by_name[name])

    def conflict_targets(self):
        targets = []
        for p in self.order:
            positive, negative, _ = self.selection(p)
            formula = And(self._expand(positive, p), self._expand(negative, p))
            targets.append((p, self.env.predicates[p].arguments, formula))
        for required, decl in sorted(self.env.predicates.items()):
            reg = decl.regulated
            if reg is not None and reg.permission is not None:
                formula = And(self.outcome(required, base=True),
                              Not(self.outcome(reg.permission, base=True)))
                targets.append((f"{required}->{reg.permission}", decl.arguments, formula))
        return tuple(targets)

    def selected_rules(self, predicate, model, values, *, max_evaluations=1_000_000):
        from .evaluate import _Evaluator
        sorts = self.env.predicates[predicate].arguments
        if len(values) != len(sorts) or any(v not in model.domains[s] for s, v in zip(sorts, values)):
            raise VEError("InvalidModel: witness tuple has wrong length or sort")
        _, _, selected = self.selection(predicate)
        bindings = tuple(zip(reversed(sorts), reversed(values)))
        evaluator = _Evaluator(self.base_environment(), model, max_evaluations, trace=False)
        return tuple(rule for rule in self.rules if rule.predicate == predicate and
                     evaluator.formula(self._expand(selected[rule.name], predicate), bindings)[0])

    def overlap_witnesses(self, model):
        """Same-sign selections with a checked example; overlap is not conflict."""
        from .model import FiniteModel
        env = self.base_environment()
        model = FiniteModel.from_dict(env, model) if type(model) is dict else model
        if model.environment_id != env.environment_id:
            raise VEError("InvalidModel: witness environment does not match base environment")
        reports = []
        for predicate in self.order:
            sorts = self.env.predicates[predicate].arguments
            for values in product(*(model.domains[s] for s in sorts)):
                selected = self.selected_rules(predicate, model, values)
                for i, left in enumerate(selected):
                    for right in selected[i + 1:]:
                        if left.sign == right.sign:
                            reports.append((left.name, right.name, tuple(values)))
        return tuple(reports)

    def base_environment(self):
        if type(self) is NormDocument and "soft-norms@0" in self.env.profiles:
            raise VEError("UnsupportedProfile: soft rules require SoftNormDocument.elaborated")
        if self.env.alternatives is not None:
            from .errors import CheckerUnavailable
            raise CheckerUnavailable("alternatives@0 requires the Lean checker")
        from .environment import Environment
        data = self.env.to_dict()
        data["vocabulary"]["predicates"] = {
            name: decl for name, decl in data["vocabulary"]["predicates"].items()
            if "regulated" not in decl}
        data["profiles"] = [p for p in data["profiles"] if p != "norms@0"]
        return Environment(data)


@dataclass(frozen=True, slots=True)
class ConflictReport:
    status: str
    target: str | None = None
    tuple: tuple[str, ...] = ()
    situation: str = ""
    detail: str = ""


@semantic_entry("norms.conflict")
def check_witness(document: NormDocument, target: str, model, values):
    """Independently validate an asserted target and typed tuple."""
    from .evaluate import _Evaluator
    from .model import FiniteModel
    env = document.base_environment()
    model = FiniteModel.from_dict(env, model) if type(model) is dict else model
    if model.environment_id != env.environment_id:
        raise VEError("InvalidModel: witness environment does not match base environment")
    from .background import validate_background
    validate_background(env, model)
    for name, sorts, formula in document.conflict_targets():
        if name != target:
            continue
        if (type(values) not in (list, tuple) or len(values) != len(sorts)
                or any(v not in model.domains[s] for s, v in zip(sorts, values))):
            raise VEError("InvalidModel: witness tuple has wrong length or sort")
        _Checker(env).formula(formula, tuple(reversed(sorts)))
        return _Evaluator(env, model, 1_000_000, trace=False).formula(
            formula, tuple(zip(reversed(sorts), reversed(values))))[0]
    raise VEError(f"UnknownSymbol: conflict target {target}")


def prove_norm_entailment(document: NormDocument, premises, conclusion, **kwargs):
    """Produce a certificate for Background ++ regenerated norm layers ++ Γ."""
    if not isinstance(document, NormDocument):
        raise VEError("UnsupportedProfile: soft rules require the soft route")
    from .entailment import prove_entailment
    layers = tuple(formula for _, formula in document.premises())
    return prove_entailment(document.env, (*layers, *premises), conclusion, **kwargs)


@semantic_entry("norms.certificate")
def check_norm_entailment_certificate(document: NormDocument, premises, conclusion, certificate):
    """Replay the same ordered premise list used by `norms-certificate`."""
    if not isinstance(document, NormDocument):
        raise VEError("UnsupportedProfile: soft rules require the soft route")
    from .entailment import check_entailment_certificate
    layers = tuple(formula for _, formula in document.premises())
    return check_entailment_certificate(document.env, (*layers, *premises), conclusion, certificate)


@semantic_entry("norms.conflict")
def check_conflict(document: NormDocument, *, model=None, certificates=None,
                   max_evaluations=1_000_000, prove=False, tableau_steps=10_000):
    """A checked finite witness or certificates decide; exhaustion stays UNKNOWN."""
    if not isinstance(document, NormDocument):
        raise VEError("UnsupportedProfile: soft rules require the soft route")
    from .evaluate import _Evaluator, _Exhausted
    from .model import FiniteModel
    from .entailment import check_entailment_certificate, prove_entailment
    env = document.base_environment()
    if model is not None:
        model = FiniteModel.from_dict(env, model) if type(model) is dict else model
        if model.environment_id != env.environment_id:
            raise VEError("InvalidModel: witness environment does not match base environment")
        from .background import validate_background
        validate_background(env, model)
        evaluator = _Evaluator(env, model, max_evaluations, trace=False)
        try:
            for target, sorts, formula in document.conflict_targets():
                _Checker(env).formula(formula, tuple(reversed(sorts)))
                for values in product(*(model.domains[s] for s in sorts)):
                    bindings = tuple(zip(reversed(sorts), reversed(values)))
                    if evaluator.formula(formula, bindings)[0]:
                        setting = ", ".join(f"{sort} {value}" for sort, value in zip(sorts, values))
                        if target in document.order:
                            selected = document.selected_rules(target, model, values)
                            role = document.env.predicates[target].regulated.role
                            pos = "permits" if role == "permission" else "requires" if role == "obligation" else "affirms"
                            neg = "forbids" if role == "permission" else "releases" if role == "obligation" else "denies"
                            decisions = "; ".join(f"rule {r.name} {pos if r.sign else neg}" for r in selected)
                        else:
                            required, permitted = target.split("->", 1)
                            decisions = f"{required} is required, but {permitted} is not permitted"
                        situation = f"{setting}: {decisions}"
                        return ConflictReport("CONFLICT", target, tuple(values), situation)
        except _Exhausted:
            return ConflictReport("UNKNOWN", detail="MAX_EVALUATIONS")
    if prove:
        certificates = {}
        for target, sorts, formula in document.conflict_targets():
            conclusion = _bind(Not(formula), sorts)
            result = prove_entailment(env, (), conclusion, max_steps=tableau_steps)
            if result.status != "Found":
                return ConflictReport("UNKNOWN", detail=f"tableau budget or open branch: {target}")
            certificates[target] = {"environment_id": document.env.environment_id,
                                    "document_hash": document.document_hash,
                                    "target": target, "certificate": result.certificate}
    if certificates is not None:
        for target, sorts, formula in document.conflict_targets():
            package = certificates.get(target)
            if (type(package) is not dict or package.get("environment_id") != document.env.environment_id
                    or package.get("document_hash") != document.document_hash
                    or package.get("target") != target):
                return ConflictReport("UNKNOWN", detail=f"missing certificate for {target}")
            conclusion = _bind(Not(formula), sorts)
            checked = check_entailment_certificate(env, (), conclusion, package.get("certificate"))
            if not checked.valid:
                return ConflictReport("UNKNOWN", detail=f"invalid certificate for {target}")
        return ConflictReport("CONFLICT-FREE")
    return ConflictReport("UNKNOWN", detail="tableau budget or search bound")
