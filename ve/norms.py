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
from .errors import CheckerUnavailable, DuplicateDeclaration, ResourceLimit, VEError
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


_NON_FOL_TAGS = frozenset({"reach", "atom", "le", "lt", "num", "add", "scale"})


def _first_order(data) -> bool:
    """Whether a formula on the wire uses first-order constructs only."""
    stack = [data]
    while stack:
        node = stack.pop()
        if type(node) is list:
            if node and node[0] in _NON_FOL_TAGS:
                return False
            stack.extend(node[1:])
    return True


def _family_norms(document) -> bool:
    """Whether Lean's `family-norms` mode (VE/Service/FamilyNorms.lean) takes a
    norm document over the closure, core or order family: the norm formulas are
    first-order, every regulated predicate is unary or binary and no declaration
    uses `$int`, so the FOL route regenerates the document over the
    environment's FOL view; certificates are the family's."""
    from .backends.validation import family_in_scope
    env = document.env
    if not (env.closure or env.order) or not family_in_scope(env):
        return False
    if any(decl.regulated is not None and len(decl.arguments) > 2 for decl in env.predicates.values()):
        return False
    if any("$int" in decl.arguments for decl in env.predicates.values()) or any(
            decl.sort == "$int" for decl in env.constants.values()):
        return False
    return all(_first_order(rule.to_dict()["norm"]["guard"]) and
               all(_first_order(x) for x in rule.to_dict()["norm"]["unless"]) for rule in document.rules)


def _lean_route(document) -> bool:
    """Whether a Lean norms route regenerates `document`.

    The norms route takes plain norm documents over FOL-family ve.core@0.2
    environments, with definitions and data flags; the family-norms mode takes
    first-order documents on the closure, core and order families
    (`_family_norms`). Statement-layer environments (soft norms, reports,
    alternatives, quantities) are not on either: their operations are not
    dispatched and keep the retained Python.
    """
    env = document.env
    from .profiles import STATEMENT_LAYERS
    if type(document) is not NormDocument or env.language != "ve.core@0.2":
        return False
    if env.closure or env.order:
        return _family_norms(document)
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

    def outcome(self, predicate, *, base=False):
        self._require_completion()
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

    def _lean_regenerated(self) -> dict:
        """Lean's `norms-elaborate` answer for this document, kept per document."""
        cached = getattr(self, "_regenerated", None)
        if cached is None:
            from .backends.relay import decide
            cached = self._regenerated = decide(_lean_mode(self), [_lean_case(self, "norms-elaborate")])[0]
        return cached

    @semantic_entry("norms.elaborate")
    def elaborate(self, predicate):
        """The generated layer premise of `predicate`, from the selected authority."""
        self._require_completion()
        from .backends.dispatch import authority_for, execute
        if authority_for("norms_elaborate") == "python" or not _lean_route(self):
            return self._elaborate_python(predicate)

        def lean():
            label = f"layer:norms:{predicate}"
            for item in self._lean_regenerated()["premises"]:
                if item.get("label") == label:
                    return _lean_formula(item["ast"])
            raise VEError(f"UnknownSymbol: regulated predicate {predicate}")

        return execute("norms_elaborate", {"document_hash": self.document_hash, "predicate": predicate},
                       lambda: self._elaborate_python(predicate), lean=lean)

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
        from .backends.dispatch import authority_for, execute
        if authority_for("norms_elaborate") == "python" or not _lean_route(self):
            return self._premises_python()

        def lean():
            return tuple((item["label"], _lean_formula(item["ast"]))
                         for item in self._lean_regenerated()["premises"])

        return execute("norms_elaborate", {"document_hash": self.document_hash},
                       self._premises_python, lean=lean)

    def _premises_python(self):
        return tuple((f"layer:norms:{p}", self._elaborate_python(p)) for p in self.order)

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
            if (type(name) is str and name.startswith("unsaid__")
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
    from .backends.dispatch import authority_for, execute
    if authority_for("norms_certificate") == "python" or not _lean_route(document):
        return _norm_certificate_python(document, premises, conclusion, certificate)
    payload = {"document_hash": document.document_hash,
               "certificate": certificate if type(certificate) is dict else None}
    return execute("norms_certificate", payload,
                   lambda: _norm_certificate_python(document, premises, conclusion, certificate),
                   lean=lambda: _norm_certificate_lean(document, premises, conclusion, certificate))


def _norm_certificate_python(document, premises, conclusion, certificate):
    from .entailment import check_entailment_certificate
    layers = tuple(formula for _, formula in document.premises())
    return check_entailment_certificate(document.env, (*layers, *premises), conclusion, certificate)


def _norm_certificate_lean(document, premises, conclusion, certificate):
    """Python's input and binding checks, then Lean's `norms-certificate` replay.

    Lean regenerates Background (flags first) and the layer premises itself and
    binds the certificate to them; the layers named in the pre-checks are
    Lean's too (`premises()` is dispatched).
    """
    from .ast import _to_data
    from .backends.relay import decide
    from .entailment import EntailmentCertificateCheck, _lean_replay_record, _replay_prechecks
    max_steps = 10_000
    layers = tuple(formula for _, formula in document.premises())
    nodes = _replay_prechecks(document.env, (*layers, *premises), conclusion, certificate, max_steps)
    if isinstance(nodes, EntailmentCertificateCheck):
        return nodes
    case = _lean_case(document, "norms-certificate", premises=[_to_data(p) for p in premises],
                      conclusion=_to_data(conclusion), certificate=certificate)
    return _lean_replay_record(lambda: decide(_lean_mode(document), [case])[0]["valid"], nodes, max_steps)


def _base_model(document, env, model):
    """The witness model over the base environment. Decoding validates it,
    Background included, under the selected authority (FiniteModel.from_dict)."""
    from .model import FiniteModel
    model = FiniteModel.from_dict(env, model) if type(model) is dict else model
    if model.environment_id != env.environment_id:
        raise VEError("InvalidModel: witness environment does not match base environment")
    return model


def _find_conflict(document, env, model, max_evaluations):
    """Python's witness search: the first target and typed tuple whose conflict
    formula evaluates true on `model`, or None. Raises `_Exhausted`."""
    from .evaluate import _Evaluator
    evaluator = _Evaluator(env, model, max_evaluations, trace=False)
    for target, sorts, formula in document.conflict_targets():
        _Checker(env).formula(formula, tuple(reversed(sorts)))
        for values in product(*(model.domains[s] for s in sorts)):
            bindings = tuple(zip(reversed(sorts), reversed(values)))
            if evaluator.formula(formula, bindings)[0]:
                return target, sorts, values
    return None


def _conflict_report(document, target, sorts, model, values):
    """The CONFLICT record; its situation names the rules Python selects there."""
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
    return ConflictReport("CONFLICT", target, tuple(values), f"{setting}: {decisions}")


def _prove_targets(document, env, tableau_steps):
    """Certificates for every conflict target from Python's (untrusted) prover,
    or the UNKNOWN record of the first target it cannot prove."""
    from .entailment import prove_entailment
    certificates = {}
    for target, sorts, formula in document.conflict_targets():
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
    from .backends.dispatch import authority_for, execute
    options = {"model": model, "certificates": certificates, "max_evaluations": max_evaluations,
               "prove": prove, "tableau_steps": tableau_steps}
    if authority_for("norms_conflict") == "python" or not _lean_route(document):
        return _check_conflict_python(document, **options)
    return execute("norms_conflict", {"document_hash": document.document_hash, "prove": prove},
                   lambda: _check_conflict_python(document, **options),
                   lean=lambda: _check_conflict_lean(document, **options))


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
            found = _find_conflict(document, env, model, max_evaluations)
            if found is not None:
                target, sorts, values = found
                witness = {"target": target, "model": model.to_dict(), "tuple": list(values)}
                row = decide(_lean_mode(document), [_lean_case(document, "norms-conflict", witness=witness)])[0]
                if row["verdict"] != "CONFLICT" or row.get("target") != target:
                    raise CheckerUnavailable("CheckerUnavailable: Lean does not confirm the conflict "
                                             "witness Python's search found")
                return _conflict_report(document, target, sorts, model, values)
        except _Exhausted:
            return ConflictReport("UNKNOWN", detail="MAX_EVALUATIONS")
    if prove:
        certificates = _prove_targets(document, env, tableau_steps)
        if isinstance(certificates, ConflictReport):
            return certificates
    if certificates is not None:
        try:
            canonical_json(certificates)
        except (VEError, TypeError, ValueError):
            certificates = {}  # packages that are not JSON bind nothing
        row = decide(_lean_mode(document), [_lean_case(document, "norms-conflict", packages=certificates)])[0]
        if row["verdict"] == "CONFLICT-FREE":
            return ConflictReport("CONFLICT-FREE")
        if row["verdict"] != "UNKNOWN" or type(row.get("detail")) is not str:
            raise CheckerUnavailable("CheckerUnavailable: malformed Lean conflict result")
        return ConflictReport("UNKNOWN", detail=row["detail"])
    return ConflictReport("UNKNOWN", detail="tableau budget or search bound")
