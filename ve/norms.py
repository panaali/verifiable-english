"""W1 norm units, Catala selection, completions, and generated FOL premises.

The checker consumes only the generated formulas.  Norm objects and their
environment declarations are the source of those formulas, never supplied
premises from an untrusted document.
"""
from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
from itertools import product
import re

from .assurance import semantic_entry
from .ast import (And, Binary, Bottom, Exists, Forall, Implies, Not, Or,
                  Top, Unary, Var, _Checker, _Decoder, _to_data)
from .background import dependency_order
from .environment import UNSAID_PREFIX
from .errors import CheckerUnavailable, DuplicateDeclaration, ResourceLimit, VEError
from .search import _used_predicates
from .wire import digest, require_fields

_NAME = re.compile(r"[a-z][a-z0-9-]*\Z", re.ASCII)


def _norm_defaults_placeholder(data):
    """The lower W1 environment with each unspecified completion set to deny."""
    data = deepcopy(data)
    data["profiles"] = [p for p in data["profiles"] if p != "norm-defaults@0"]
    for decl in data["vocabulary"]["predicates"].values():
        if decl.get("regulated", {}).get("default") == "unspecified":
            decl["regulated"]["default"] = "deny"
    return data


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


def _instantiate(formula, terms, depth=0, *, nary_atoms=False):
    """Replace the tuple variables of an open formula, respecting inner binders.

    n-ary atoms are substituted only on request (`nary_atoms`): the Lean family
    route's untrusted generators ask for it, so they search and prove the
    targets Lean regenerates (lf-14b review F5). Every retained Python caller,
    and the base admission check on the Lean route, keeps the base expansion,
    which leaves them unsubstituted (lf-14b review F2/F3) until batch 14c moves
    n-ary scope with a DRI-signed delta."""
    from .ast import Atom, Eq, Reach, Body, Lt, Le
    if isinstance(formula, (Unary, Binary)):
        args = (formula.term,) if isinstance(formula, Unary) else (formula.left, formula.right)
        mapped = tuple(_replace_term(x, terms, depth) for x in args)
        return Unary(formula.predicate, mapped[0]) if len(mapped) == 1 else Binary(formula.predicate, *mapped)
    if isinstance(formula, Atom) and nary_atoms:
        return Atom(formula.predicate, tuple(_replace_term(x, terms, depth) for x in formula.terms))
    if isinstance(formula, (Eq, Lt, Le)):
        return type(formula)(_replace_term(formula.left, terms, depth),
                             _replace_term(formula.right, terms, depth))
    if isinstance(formula, Reach):
        edge = (Body(formula.edge.sort, _instantiate(formula.edge.formula, terms, depth + 2,
                                                 nary_atoms=nary_atoms))
                if isinstance(formula.edge, Body) else formula.edge)
        return Reach(formula.kind, edge, _replace_term(formula.left, terms, depth),
                     _replace_term(formula.right, terms, depth))
    if isinstance(formula, Not):
        return Not(_instantiate(formula.body, terms, depth, nary_atoms=nary_atoms))
    if isinstance(formula, (And, Or, Implies)):
        return type(formula)(_instantiate(formula.left, terms, depth, nary_atoms=nary_atoms),
                             _instantiate(formula.right, terms, depth, nary_atoms=nary_atoms))
    if isinstance(formula, (Forall, Exists)):
        return type(formula)(formula.sort, _instantiate(formula.body, terms, depth + 1,
                                                        nary_atoms=nary_atoms))
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


def _lean_route(document) -> bool:
    """Whether a Lean norms route regenerates `document`.

    The norms route takes plain norm documents over FOL-family ve.core@0.2
    environments, with definitions and data flags; the family-norms mode takes
    every document on the closure, core and order families, first-order or not,
    with definitions of any arity (VE/Service/FamilyNorms.lean,
    VE/Norms/Family.lean; `family_in_scope`). Statement-layer environments (soft
    norms, reports, alternatives, quantities) are not on either:
    their operations are not dispatched and keep the retained Python.
    """
    env = document.env
    from .profiles import STATEMENT_LAYERS
    if type(document) is not NormDocument or env.language != "ve.core@0.2":
        return False
    if env.closure or env.order:
        from .backends.validation import family_in_scope
        return family_in_scope(env)
    return (env.alternatives is None and getattr(env, "unit_schema", None) is None
            and not STATEMENT_LAYERS & set(env.profiles))


def _lean_mode(document) -> str:
    """The service mode of `document`'s norms cases."""
    return "family-norms" if document.env.closure or document.env.order else "norms"


def _lean_case(document, kind, **fields):
    """A norms-route case over the document's own environment and norm objects."""
    from .environment_wire import encoded_environment
    return {"id": kind, "kind": kind,
            "environment": encoded_environment(document.env, "lean-norms", document.env.to_dict),
            "norms": [rule.to_dict() for rule in document.rules], **fields}


def _lean_formula(data):
    """A formula Lean regenerated and typed, read structurally."""
    return _Decoder().decode(data)


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
            if rule.name.startswith("unsaid--") and "norm-defaults@0" in env.profiles:
                # norm-defaults 2.1: reserved for the rules `fill` adds.
                raise VEError(f"InvalidInput: reserved name {rule.name}")
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

    def _require_completion(self):
        # An unspecified completion has no W1 layer of its own: norm-defaults
        # elaborates the document by `fill` into an ordinary W1 tree first.
        if "norm-defaults@0" in self.env.profiles:
            raise VEError("UnsupportedProfile: norm-defaults@0 documents are checked through fill "
                          "(ve.norm_defaults)")

    def outcome(self, predicate, *, base=False, nary_atoms=False):
        self._require_completion()
        positive, negative, _ = self.selection(predicate)
        default = self.env.predicates[predicate].regulated.default
        outcome = positive if default == "deny" else Not(negative)
        return self._expand(outcome, predicate, nary_atoms=nary_atoms) if base else outcome

    def _expand(self, formula, current, stack=(), *, nary_atoms=False):
        """Replace lower regulated atoms by completed outcomes (`_instantiate`
        says which callers substitute n-ary atoms)."""
        if isinstance(formula, (Unary, Binary)) and formula.predicate != current:
            decl = self.env.predicates[formula.predicate]
            if decl.regulated is not None:
                if formula.predicate in stack:
                    raise VEError("DependencyCycle: " + formula.predicate)
                args = (formula.term,) if isinstance(formula, Unary) else (formula.left, formula.right)
                return _instantiate(self._expand(self.outcome(formula.predicate), formula.predicate,
                                                  (*stack, formula.predicate), nary_atoms=nary_atoms),
                                    args, nary_atoms=nary_atoms)
        if isinstance(formula, Not):
            return Not(self._expand(formula.body, current, stack, nary_atoms=nary_atoms))
        if isinstance(formula, (And, Or, Implies)):
            return type(formula)(self._expand(formula.left, current, stack, nary_atoms=nary_atoms),
                                 self._expand(formula.right, current, stack, nary_atoms=nary_atoms))
        if isinstance(formula, (Forall, Exists)):
            return type(formula)(formula.sort, self._expand(formula.body, current, stack,
                                                            nary_atoms=nary_atoms))
        return formula

    def _lean_regenerated(self) -> dict:
        """Lean's `norms-elaborate` answer for this document, kept per document.

        The row is bound to the request (DRI-RULINGS R8): its order names each
        regulated predicate once and otherwise only defined predicates, and its
        premises are the regulated layers in that order."""
        cached = getattr(self, "_regenerated", None)
        if cached is None:
            from .backends.relay import decide
            row = decide(_lean_mode(self), [_lean_case(self, "norms-elaborate")])[0]
            regulated = {p for p, d in self.env.predicates.items() if d.regulated is not None}
            defined = {p for p, d in self.env.predicates.items() if d.defined is not None}
            order = row["order"]
            if (len(set(order)) != len(order) or not regulated <= set(order) <= regulated | defined
                    or [p["label"] for p in row["premises"]] != [f"layer:norms:{p}" for p in order
                                                                if p in regulated]):
                raise CheckerUnavailable("CheckerUnavailable: norms-elaborate row is not bound to the request")
            expected = _target_sorts(self.env)
            targets = row["conflict_targets"]
            if (len(targets) != len(expected) or {t["target"] for t in targets} != set(expected)
                    or any(t["sorts"] != expected[t["target"]] for t in targets)):
                raise CheckerUnavailable("CheckerUnavailable: norms-elaborate targets are not bound to the request")
            cached = self._regenerated = row
        return cached

    @semantic_entry("norms.elaborate")
    def elaborate(self, predicate):
        """The generated layer premise of `predicate`, from the selected authority."""
        self._require_completion()
        from .backends.dispatch import owned
        if not _lean_route(self):
            return self._elaborate_python(predicate)

        def lean():
            label = f"layer:norms:{predicate}"
            for item in self._lean_regenerated()["premises"]:
                if item.get("label") == label:
                    return _lean_formula(item["ast"])
            raise VEError(f"UnknownSymbol: regulated predicate {predicate}")

        return owned("norms_elaborate", lean)

    def _elaborate_python(self, predicate):
        positive, negative, _ = self.selection(predicate)
        decl = self.env.predicates[predicate]
        atom = _atom(predicate, len(decl.arguments))
        silence = And(Not(positive), Not(negative))
        default = atom if decl.regulated.default == "allow" else Not(atom)
        return _bind(_all((Implies(positive, atom), Implies(negative, Not(atom)),
                           Implies(silence, default))), decl.arguments)

    @semantic_entry("norms.elaborate")
    def premises(self):
        """The labelled layer premises in layer order, from the selected authority."""
        self._require_completion()
        from .backends.dispatch import owned
        if not _lean_route(self):
            return self._premises_python()

        def lean():
            return tuple((item["label"], _lean_formula(item["ast"]))
                         for item in self._lean_regenerated()["premises"])

        return owned("norms_elaborate", lean)

    def _premises_python(self):
        return tuple((f"layer:norms:{p}", self._elaborate_python(p)) for p in self.order)

    def meaning_id(self, name):
        """A rule identity binds its AST and environment, never its display number."""
        return norm_meaning_id(self.env, self.by_name[name])

    def conflict_targets(self, *, nary_atoms=False):
        targets = []
        for p in self.order:
            positive, negative, _ = self.selection(p)
            formula = And(self._expand(positive, p, nary_atoms=nary_atoms),
                          self._expand(negative, p, nary_atoms=nary_atoms))
            targets.append((p, self.env.predicates[p].arguments, formula))
        for required, decl in sorted(self.env.predicates.items()):
            reg = decl.regulated
            if reg is not None and reg.permission is not None:
                formula = And(self.outcome(required, base=True, nary_atoms=nary_atoms),
                              Not(self.outcome(reg.permission, base=True, nary_atoms=nary_atoms)))
                targets.append((f"{required}->{reg.permission}", decl.arguments, formula))
        return tuple(targets)

    def selected_rules(self, predicate, model, values, *, max_evaluations=1_000_000, nary_atoms=False):
        from .evaluate import _Evaluator
        sorts = self.env.predicates[predicate].arguments
        if len(values) != len(sorts) or any(v not in model.domains[s] for s, v in zip(sorts, values)):
            raise VEError("InvalidModel: witness tuple has wrong length or sort")
        _, _, selected = self.selection(predicate)
        bindings = tuple(zip(reversed(sorts), reversed(values)))
        evaluator = _Evaluator(self.base_environment(), model, max_evaluations, trace=False)
        return tuple(rule for rule in self.rules if rule.predicate == predicate and
                     evaluator.formula(self._expand(selected[rule.name], predicate, nary_atoms=nary_atoms),
                                       bindings)[0])

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
        self._require_completion()
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
        # `readings@1` is the head's layer, never the base vocabulary's (DRI ruling 4's class).
        data["profiles"] = [p for p in data["profiles"] if p not in ("norms@0", "readings@1")]
        if "speech-acts@0" in data["profiles"]:
            data["profiles"].remove("speech-acts@0")
            data.pop("speech_acts", None)
        return Environment(data)


@dataclass(frozen=True, slots=True)
class ConflictReport:
    status: str
    target: str | None = None
    tuple: tuple[str, ...] = ()
    situation: str = ""
    detail: str = ""


def _reject_filling(document, model):
    """A filling table belongs to a norm-defaults@0 document (norm-defaults 8)."""
    relations = model.get("relations") if type(model) is dict else None
    if type(relations) is dict:
        for name in sorted(relations):
            if (type(name) is str and name.startswith(UNSAID_PREFIX)
                    and name not in document.env.predicates):
                from .errors import InvalidModel
                raise InvalidModel(f"{name} is a filling; supply it only with norm-defaults@0",
                                   generator="norms")


@semantic_entry("norms.conflict")
def check_witness(document: NormDocument, target: str, model, values):
    """Independently validate an asserted target and typed tuple."""
    from .evaluate import _Evaluator
    from .model import FiniteModel
    _reject_filling(document, model)
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
    from .backends.dispatch import owned
    if not _lean_route(document):
        return _norm_certificate_python(document, premises, conclusion, certificate)
    return owned("norms_certificate", lambda: _norm_certificate_lean(document, premises, conclusion, certificate))


def _norm_certificate_python(document, premises, conclusion, certificate):
    from .entailment import check_entailment_certificate
    layers = tuple(formula for _, formula in document.premises())
    return check_entailment_certificate(document.env, (*layers, *premises), conclusion, certificate)


def _norm_certificate_lean(document, premises, conclusion, certificate):
    """Lean owns the regenerated premises, binding, replay and step charge."""
    from .ast import _to_data
    from .backends.relay import decide
    from .entailment import EntailmentCertificateCheck
    try:
        case = _lean_case(document, "norms-certificate", premises=[_to_data(p) for p in premises],
                          conclusion=_to_data(conclusion), certificate=certificate)
        row = decide(_lean_mode(document), [case])[0]
    except ResourceLimit as exc:
        if str(exc).startswith("ResourceLimit: certificate replay exceeds"):
            return EntailmentCertificateCheck(False, "ResourceLimit", 10_000,
                                              "certificate replay budget exhausted")
        return EntailmentCertificateCheck(False, "ResourceLimit", 0, str(exc))
    except VEError as exc:
        return EntailmentCertificateCheck(False, "InvalidCertificate", 0, str(exc))
    if row["layers"] != sum(d.regulated is not None for d in document.env.predicates.values()):
        raise CheckerUnavailable("CheckerUnavailable: Lean certificate layer count is not bound to the request")
    if row["valid"]:
        return EntailmentCertificateCheck(True, "Valid", row["steps"])
    return EntailmentCertificateCheck(False, "InvalidCertificate", 0, "certificate does not replay")


def _base_model(document, env, model):
    """The witness model over the base environment. Decoding validates it,
    Background included, under the selected authority (FiniteModel.from_dict)."""
    from .model import FiniteModel
    model = FiniteModel.from_dict(env, model) if type(model) is dict else model
    if model.environment_id != env.environment_id:
        raise VEError("InvalidModel: witness environment does not match base environment")
    return model


def _generator_targets(document, *, lean):
    """Each conflict target as the base admitted it, paired with the formula the
    route's untrusted generators search and prove.

    The base expansion is always the admission check (an ill-typed one raises
    the base's `TypeMismatch`, lf-14b review F3). On the Lean family route the
    generators work on the targets Lean regenerates, whose n-ary atoms are
    substituted: searching the base expansion instead proposes witnesses Lean
    refutes and proves conclusions Lean does not check (lf-14b review F5).
    `test_lean_route_generators_search_the_targets_lean_regenerates` pins them
    to Lean's `norms-elaborate` targets."""
    base = document.conflict_targets()
    searched = document.conflict_targets(nary_atoms=True) if lean else base
    return tuple((name, sorts, admitted, formula)
                 for (name, sorts, admitted), (_, _, formula) in zip(base, searched, strict=True))


def _find_conflict(document, env, model, max_evaluations, *, lean=False):
    """Python's witness search: the first target and typed tuple whose conflict
    formula evaluates true on `model`, or None. Raises `_Exhausted`."""
    from .evaluate import _Evaluator
    evaluator = _Evaluator(env, model, max_evaluations, trace=False)
    for target, sorts, admitted, formula in _generator_targets(document, lean=lean):
        _Checker(env).formula(admitted, tuple(reversed(sorts)))
        for values in product(*(model.domains[s] for s in sorts)):
            bindings = tuple(zip(reversed(sorts), reversed(values)))
            if evaluator.formula(formula, bindings)[0]:
                return target, sorts, values
    return None


def _conflict_report(document, target, sorts, model, values, *, lean=False):
    """The CONFLICT record; its situation names the rules Python selects there."""
    setting = ", ".join(f"{sort} {value}" for sort, value in zip(sorts, values))
    if target in document.order:
        selected = document.selected_rules(target, model, values, nary_atoms=lean)
        role = document.env.predicates[target].regulated.role
        pos = "permits" if role == "permission" else "requires" if role == "obligation" else "affirms"
        neg = "forbids" if role == "permission" else "releases" if role == "obligation" else "denies"
        decisions = "; ".join(f"rule {r.name} {pos if r.sign else neg}" for r in selected)
    else:
        required, permitted = target.split("->", 1)
        decisions = f"{required} is required, but {permitted} is not permitted"
    return ConflictReport("CONFLICT", target, tuple(values), f"{setting}: {decisions}")


def _prove_targets(document, env, tableau_steps, *, lean=False):
    """Certificates for every conflict target from Python's (untrusted) prover,
    or the UNKNOWN record of the first target it cannot prove."""
    from .entailment import _validate_inputs, prove_entailment
    certificates = {}
    for target, sorts, admitted, formula in _generator_targets(document, lean=lean):
        if lean:  # the prover's own input check, run on the base's conclusion
            _validate_inputs(env, (), _bind(Not(admitted), sorts))
        result = prove_entailment(env, (), _bind(Not(formula), sorts), max_steps=tableau_steps)
        if result.status != "Found":
            return ConflictReport("UNKNOWN", detail=f"tableau budget or open branch: {target}")
        certificates[target] = {"environment_id": document.env.environment_id,
                                "document_hash": document.document_hash,
                                "target": target, "certificate": result.certificate}
    return certificates


@semantic_entry("norms.conflict")
def check_conflict(document: NormDocument, *, model=None, certificates=None,
                   max_evaluations=1_000_000, prove=False, tableau_steps=10_000):
    """A checked finite witness or certificates decide; exhaustion stays UNKNOWN."""
    if not isinstance(document, NormDocument):
        raise VEError("UnsupportedProfile: soft rules require the soft route")
    document._require_completion()
    _reject_filling(document, model)
    from .backends.dispatch import owned
    options = {"model": model, "certificates": certificates, "max_evaluations": max_evaluations,
               "prove": prove, "tableau_steps": tableau_steps}
    if not _lean_route(document):
        return _check_conflict_python(document, **options)
    return owned("norms_conflict", lambda: _check_conflict_lean(document, **options))


def _check_conflict_python(document, *, model, certificates, max_evaluations, prove, tableau_steps):
    from .evaluate import _Exhausted
    from .entailment import check_entailment_certificate
    env = document.base_environment()
    if model is not None:
        model = _base_model(document, env, model)
        try:
            found = _find_conflict(document, env, model, max_evaluations)
            if found is not None:
                return _conflict_report(document, *found[:2], model, found[2])
        except _Exhausted:
            return ConflictReport("UNKNOWN", detail="MAX_EVALUATIONS")
    if prove:
        certificates = _prove_targets(document, env, tableau_steps)
        if isinstance(certificates, ConflictReport):
            return certificates
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


def _target_names(env):
    """The names of the conflict targets an environment declares: each regulated
    predicate and each obligation/permission pair."""
    return ({p for p, d in env.predicates.items() if d.regulated is not None} |
            {f"{p}->{d.regulated.permission}" for p, d in env.predicates.items()
             if d.regulated is not None and d.regulated.permission is not None})


def _target_sorts(env):
    return {name: list(env.predicates[name.split("->", 1)[0]].arguments)
            for name in _target_names(env)}


def _bound_targets(document, row):
    expected = _target_names(document.env)
    if len(row["targets"]) != len(expected) or set(row["targets"]) != expected:
        raise CheckerUnavailable("CheckerUnavailable: Lean conflict targets are not bound to the request")


def _check_conflict_lean(document, *, model, certificates, max_evaluations, prove, tableau_steps):
    """Lean's `norms-conflict` decides CONFLICT and CONFLICT-FREE.

    Python's witness search and prover are untrusted generators: a found
    witness is replayed by Lean (a refused one is a generator/check
    disagreement, CheckerUnavailable), and every certificate package is
    replayed by Lean over the regenerated targets. Exhausting either generator
    yields UNKNOWN, which asserts nothing. The model is validated as Python
    validates it until the model adapter lands; Lean validates it again.
    """
    from .backends.relay import decide
    from .evaluate import _Exhausted
    from .wire import canonical_json
    env = document.base_environment()
    if model is not None:
        model = _base_model(document, env, model)
        try:
            found = _find_conflict(document, env, model, max_evaluations, lean=True)
            if found is not None:
                target, sorts, values = found
                witness = {"target": target, "model": model.to_dict(), "tuple": list(values)}
                row = decide(_lean_mode(document), [_lean_case(document, "norms-conflict", witness=witness)])[0]
                _bound_targets(document, row)
                if row["verdict"] != "CONFLICT" or row.get("target") != target:
                    raise CheckerUnavailable("CheckerUnavailable: Lean does not confirm the conflict "
                                             "witness Python's search found")
                return _conflict_report(document, target, sorts, model, values, lean=True)
        except _Exhausted:
            return ConflictReport("UNKNOWN", detail="MAX_EVALUATIONS")
    if prove:
        certificates = _prove_targets(document, env, tableau_steps, lean=True)
        if isinstance(certificates, ConflictReport):
            return certificates
    if certificates is not None:
        try:
            canonical_json(certificates)
        except (VEError, TypeError, ValueError):
            certificates = {}  # packages that are not JSON bind nothing
        row = decide(_lean_mode(document), [_lean_case(document, "norms-conflict", packages=certificates)])[0]
        _bound_targets(document, row)
        if row["verdict"] == "CONFLICT-FREE":
            return ConflictReport("CONFLICT-FREE")
        if row["verdict"] != "UNKNOWN" or type(row.get("detail")) is not str:
            raise CheckerUnavailable("CheckerUnavailable: malformed Lean conflict result")
        names = _target_names(document.env)
        named = re.fullmatch(r"(?:missing|invalid) certificate for (.+)", row["detail"])
        if named is None or named.group(1) not in names:
            raise CheckerUnavailable("CheckerUnavailable: Lean conflict result is not bound to the request")
        return ConflictReport("UNKNOWN", detail=row["detail"])
    return ConflictReport("UNKNOWN", detail="tableau budget or search bound")
