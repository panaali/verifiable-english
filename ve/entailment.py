"""Checkable semantic-tableau evidence for many-sorted relational FOL.

Proof search in this module is a convenience and is deliberately outside the
trust boundary.  A positive result is justified only by replaying its data-only
tableau with :func:`check_entailment_certificate`.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Sequence

from .ast import (And, Binary, Bottom, Const, Document, Eq, Exists, Forall, Implies,
                  Not, Or, Top, Unary, Var, check_document)
from .errors import ResourceLimit, VEError
from .identity import meaning_id
from .limits import MAX_NODES, MAX_TABLEAU_DEPTH
from .wire import canonical_json


ENTAILMENT_CHECKER_VERSION = "ve-tableau-checker@2"


@dataclass(frozen=True, slots=True)
class EntailmentResult:
    status: str
    certificate: dict[str, Any] | None
    steps: int
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "certificate": self.certificate,
                "steps": self.steps, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class EntailmentCertificateCheck:
    valid: bool
    status: str
    steps: int
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "status": self.status,
                "steps": self.steps, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class _Signed:
    formula: Any
    positive: bool
    # De Bruijn index -> tableau parameter token.
    bindings: tuple[str, ...] = ()


@dataclass
class _Branch:
    formulas: list[_Signed]
    parameters: dict[str, str]
    expanded: set[int]
    instantiated: set[tuple[int, str]]
    next_witness: int = 0

    def copy(self) -> "_Branch":
        return _Branch(list(self.formulas), dict(self.parameters), set(self.expanded),
                       set(self.instantiated), self.next_witness)


class _Budget(Exception):
    pass


class _InvalidTrace(Exception):
    pass


def _premises(value: Sequence[Any]) -> tuple[Any, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise VEError("Premises must be an ordered sequence")
    if len(value) > MAX_NODES:
        raise ResourceLimit("Premise count exceeds aggregate AST limit")
    return tuple(value)


def _validate_inputs(env: Any, premises: Sequence[Any], conclusion: Any) -> tuple[Any, ...]:
    premises = _premises(premises)
    check_document(env, Document((*premises, conclusion)))
    return premises


def _initial_branch(env: Any, premises: tuple[Any, ...], conclusion: Any) -> _Branch:
    parameters = {f"c:{name}": decl.sort for name, decl in env.constants.items()}
    signed = [_Signed(formula, True) for formula in premises]
    signed.append(_Signed(conclusion, False))
    return _Branch(signed, parameters, set(), set())


def _kind(item: _Signed) -> str:
    f, pos = item.formula, item.positive
    if type(f) is Not: return "not"
    if type(f) is And: return "alpha" if pos else "beta"
    if type(f) is Or: return "beta" if pos else "alpha"
    if type(f) is Implies: return "beta" if pos else "alpha"
    if (type(f) is Forall and pos) or (type(f) is Exists and not pos): return "gamma"
    if type(f) in (Forall, Exists): return "delta"
    return "literal"


def _term_token(term: Any, bindings: tuple[str, ...]) -> str:
    if type(term) is Const:
        return f"c:{term.name}"
    if type(term) is Var and term.index < len(bindings):
        return bindings[term.index]
    raise _InvalidTrace("ill-scoped term in tableau")


def _closed(branch: _Branch) -> bool:
    """Congruence closure for this relation-only language, independent of search."""
    # Complementary compound formulas close just as complementary atoms do.
    # Including parameter bindings is essential under quantifier instantiation.
    positive_formulas = {(item.formula, item.bindings) for item in branch.formulas if item.positive}
    if any((item.formula, item.bindings) in positive_formulas
           for item in branch.formulas if not item.positive):
        return True
    parent = {token: token for token in branch.parameters}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        a, b = find(a), find(b)
        if a != b:
            parent[b] = a

    for item in branch.formulas:
        f = item.formula
        if type(f) is Bottom and item.positive: return True
        if type(f) is Top and not item.positive: return True
        if type(f) is Eq and item.positive:
            union(_term_token(f.left, item.bindings), _term_token(f.right, item.bindings))
    positive: set[tuple[Any, ...]] = set()
    negative: set[tuple[Any, ...]] = set()
    for item in branch.formulas:
        f = item.formula
        if type(f) is Eq:
            left = find(_term_token(f.left, item.bindings))
            right = find(_term_token(f.right, item.bindings))
            if not item.positive and left == right: return True
        elif type(f) is Unary:
            atom = (f.predicate, find(_term_token(f.term, item.bindings)))
            (positive if item.positive else negative).add(atom)
        elif type(f) is Binary:
            atom = (f.predicate, find(_term_token(f.left, item.bindings)),
                    find(_term_token(f.right, item.bindings)))
            (positive if item.positive else negative).add(atom)
    return bool(positive & negative)


def _derive(branch: _Branch, at: int, parameter: str | None) -> list[list[_Signed]]:
    if type(at) is not int or isinstance(at, bool) or not 0 <= at < len(branch.formulas):
        raise _InvalidTrace("invalid tableau target")
    item = branch.formulas[at]
    f, pos, bindings = item.formula, item.positive, item.bindings
    kind = _kind(item)
    if kind == "literal": raise _InvalidTrace("literal cannot be expanded")
    if kind != "gamma" and at in branch.expanded:
        raise _InvalidTrace("tableau formula expanded twice")
    if kind == "not":
        if parameter is not None: raise _InvalidTrace("unexpected parameter")
        return [[_Signed(f.body, not pos, bindings)]]
    if kind in ("alpha", "beta"):
        if parameter is not None: raise _InvalidTrace("unexpected parameter")
        if type(f) is And:
            pieces = [_Signed(f.left, pos, bindings), _Signed(f.right, pos, bindings)]
        elif type(f) is Or:
            pieces = [_Signed(f.left, pos, bindings), _Signed(f.right, pos, bindings)]
        else:
            pieces = [_Signed(f.left, not pos, bindings), _Signed(f.right, pos, bindings)]
        return [pieces] if kind == "alpha" else [[pieces[0]], [pieces[1]]]
    if kind == "gamma":
        if type(parameter) is not str or branch.parameters.get(parameter) != f.sort:
            raise _InvalidTrace("gamma parameter is absent or has the wrong sort")
        if (at, parameter) in branch.instantiated:
            raise _InvalidTrace("duplicate universal instantiation")
        return [[_Signed(f.body, pos, (parameter,) + bindings)]]
    if parameter is not None: raise _InvalidTrace("delta witnesses are checker-generated")
    token = f"w:{branch.next_witness}"
    if token in branch.parameters: raise _InvalidTrace("duplicate witness token")
    return [[_Signed(f.body, pos, (token,) + bindings)]]


def _apply(branch: _Branch, at: int, parameter: str | None,
           additions: list[_Signed]) -> _Branch:
    result = branch.copy()
    kind = _kind(result.formulas[at])
    if kind == "gamma":
        assert parameter is not None
        result.instantiated.add((at, parameter))
    else:
        result.expanded.add(at)
        if kind == "delta":
            f = result.formulas[at].formula
            token = f"w:{result.next_witness}"
            result.next_witness += 1
            result.parameters[token] = f.sort
    result.formulas.extend(additions)
    return result


def _instance_key(item: _Signed) -> tuple:
    """Search-only identity: ignore unused bindings and peel signed negations.

    This is NOT a closure rule. Every selected expansion and every close still
    goes through the unchanged replayer on the original, unnormalized inputs.
    """
    def walk(f, bound=0):
        def term(t):
            if type(t) is Const:
                return ("parameter", f"c:{t.name}")
            return (("bound", t.index) if t.index < bound else
                    ("parameter", item.bindings[t.index - bound]))
        kind = type(f)
        if kind in (Top, Bottom): return (kind.__name__,)
        if kind is Unary: return ("Unary", f.predicate, term(f.term))
        if kind is Binary: return ("Binary", f.predicate, term(f.left), term(f.right))
        if kind is Eq: return ("Eq", term(f.left), term(f.right))
        if kind is Not: return ("Not", walk(f.body, bound))
        if kind in (Forall, Exists): return (kind.__name__, f.sort, walk(f.body, bound + 1))
        return (kind.__name__, walk(f.left, bound), walk(f.right, bound))
    f, positive = item.formula, item.positive
    while type(f) is Not:
        f, positive = f.body, not positive
    return (positive, walk(f))


def _connection_key(item: _Signed, opposite: bool = False) -> tuple:
    """NNF + associative/commutative connectives for candidate ranking ONLY.

    Matching keys do not close a branch, rewrite its formulas, or skip a rule.
    In particular, quantifiers are never dropped on an assumed inhabited sort.
    """
    def connective(kind, parts):
        flat = set()
        identity = kind == "and"
        for part in parts:
            if part == ("truth", not identity): return part
            if part == ("truth", identity): continue
            if part[0] == kind: flat.update(part[1])
            else: flat.add(part)
        if not flat: return ("truth", identity)
        if len(flat) == 1: return next(iter(flat))
        return (kind, frozenset(flat))

    def walk(f, positive, bound=0):
        def term(t):
            if type(t) is Const: return ("parameter", f"c:{t.name}")
            return (("bound", t.index) if t.index < bound else
                    ("parameter", item.bindings[t.index - bound]))
        kind = type(f)
        if kind in (Top, Bottom): return ("truth", positive == (kind is Top))
        if kind is Unary: return ("unary", positive, f.predicate, term(f.term))
        if kind is Binary: return ("binary", positive, f.predicate, term(f.left), term(f.right))
        if kind is Eq: return ("eq", positive, frozenset((term(f.left), term(f.right))))
        if kind is Not: return walk(f.body, not positive, bound)
        if kind in (Forall, Exists):
            quantifier = "forall" if positive == (kind is Forall) else "exists"
            return (quantifier, f.sort, walk(f.body, positive, bound + 1))
        if kind is Implies:
            return connective("or" if positive else "and",
                              (walk(f.left, not positive, bound), walk(f.right, positive, bound)))
        connective_kind = "and" if positive == (kind is And) else "or"
        return connective(connective_kind, (walk(f.left, positive, bound), walk(f.right, positive, bound)))
    return walk(item.formula, item.positive != opposite)


def _ground_connections(key: tuple) -> frozenset[tuple]:
    """Ground literal hints, including beneath connectives/quantifiers.

    A hint is only a candidate ranking: it does not assert that a subformula
    holds, remove a binder, suppress an expansion, or close a branch.
    """
    if key[0] in ("and", "or"):
        return frozenset().union(*(_ground_connections(part) for part in key[1]))
    if key[0] in ("forall", "exists"):
        return _ground_connections(key[2])
    def has_bound(value):
        if not isinstance(value, (tuple, frozenset)):
            return False
        if isinstance(value, tuple) and value and value[0] == "bound":
            return True
        return any(has_bound(part) for part in value)
    return frozenset() if has_bound(key) or key[0] == "truth" else frozenset((key,))


class _Searcher:
    def __init__(self, maximum: int):
        self.maximum, self.steps = maximum, 0
        self.instance_limit = 1
        self.cutoff = False
        self.depth_cutoffs = 0
        self.instance_key = lru_cache(maxsize=4096)(_instance_key)
        self.connection_key = lru_cache(maxsize=4096)(_connection_key)
        self.ground_connections = lru_cache(maxsize=4096)(_ground_connections)

    def tick(self) -> None:
        if self.steps >= self.maximum: raise _Budget
        self.steps += 1

    def search(self, branch: _Branch, depth: int = 0) -> dict[str, Any] | None:
        self.tick()
        if depth > MAX_TABLEAU_DEPTH:
            self.depth_cutoffs += 1
            self.cutoff = True
            return None
        if _closed(branch): return {"rule": "close"}
        keys = {self.instance_key(item) for item in branch.formulas}
        complements = {self.connection_key(item, True) for item in branch.formulas}
        ground_complements = frozenset().union(*(self.ground_connections(key) for key in complements))
        counts: dict[int, int] = {}
        for at, _ in branch.instantiated:
            counts[at] = counts.get(at, 0) + 1
        choices = []
        for at, item in enumerate(branch.formulas):
            kind = _kind(item)
            if kind == "literal" or (kind != "gamma" and at in branch.expanded):
                continue
            if kind == "delta":
                # Existing witnesses only suppress redundant SEARCH work. Never
                # reuse a witness as a delta eigenparameter in a certificate.
                if any(self.instance_key(_Signed(item.formula.body, item.positive,
                        (token,) + item.bindings)) in keys
                       for token, sort in branch.parameters.items() if sort == item.formula.sort):
                    continue
            tokens = ([token for token, sort in branch.parameters.items()
                       if sort == item.formula.sort and (at, token) not in branch.instantiated]
                      if kind == "gamma" else [None])
            for order, token in enumerate(tokens):
                additions = _derive(branch, at, token)
                derived = [self.instance_key(x) for group in additions for x in group]
                if kind == "gamma" and all(key in keys for key in derived):
                    continue
                if kind == "gamma" and counts.get(at, 0) >= self.instance_limit:
                    self.cutoff = True
                    continue
                connects = any(self.connection_key(x) in complements or
                               self.connection_key(x) == ("truth", False)
                               for group in additions for x in group)
                # Eager signed NNF/alpha expansion uses ordinary recorded rules.
                # Rank partial ground connections too: an outer instantiation
                # can expose a relevant atom before its inner binder is opened.
                # Otherwise unused constants can consume the depth budget before
                # the pair of existential witnesses ever gets instantiated.
                hints = (frozenset().union(*(self.ground_connections(self.connection_key(x))
                                            for group in additions for x in group))
                         if kind == "gamma" else frozenset())
                hits = len(hints & ground_complements)
                # Preserve least-used/oldest universal scheduling. Hints rank
                # only the parameter choices of that same formula, so a new
                # relevant universal cannot starve an older one.
                priority = (0 if connects else 1 if kind in ("not", "alpha") else
                            2 if kind == "delta" else 3 if kind == "gamma" else 4)
                choices.append(((priority, counts.get(at, 0), at, -hits, order), at, token, additions))
        if not choices: return None
        choices.sort(key=lambda choice: choice[0])
        # A depth frontier is a failed ordering, not a global budget abort.
        # Try other available expansions while retaining the global step cap.
        for _, at, parameter, alternatives in choices:
            frontier = self.depth_cutoffs
            children = []
            for addition in alternatives:
                child = self.search(_apply(branch, at, parameter, addition), depth + 1)
                if child is None: break
                children.append(child)
            else:
                node: dict[str, Any] = {"rule": "expand", "at": at, "children": children}
                if parameter is not None: node["parameter"] = parameter
                return node
            if self.depth_cutoffs == frontier:
                # Saturation or an instantiation frontier: retry at the next
                # per-universal bound, rather than permuting this same round.
                return None
        return None

    def prove(self, branch: _Branch) -> dict[str, Any] | None:
        while self.instance_limit <= MAX_TABLEAU_DEPTH:
            self.cutoff = False
            trace = self.search(branch)
            if trace is not None or not self.cutoff:
                return trace
            self.instance_limit *= 2
        raise _Budget


def _binding(env: Any, premises: tuple[Any, ...], conclusion: Any) -> dict[str, Any]:
    return {"checker_version": ENTAILMENT_CHECKER_VERSION,
            "environment_id": env.environment_id,
            "premise_meaning_ids": [meaning_id(env, x) for x in premises],
            "conclusion_meaning_id": meaning_id(env, conclusion)}


def prove_entailment(env: Any, premises: Sequence[Any], conclusion: Any, *,
                     max_steps: int = 10_000) -> EntailmentResult:
    """Search for a closed tableau. Failure is inconclusive, never refutation."""
    premises = _validate_inputs(env, premises, conclusion)
    if type(max_steps) is not int or isinstance(max_steps, bool) or max_steps < 0:
        raise ValueError("max_steps must be a nonnegative integer")
    searcher = _Searcher(max_steps)
    try:
        trace = searcher.prove(_initial_branch(env, premises, conclusion))
    except (_Budget, RecursionError):
        return EntailmentResult("ResourceLimit", None, searcher.steps, "tableau step or certificate nesting budget exhausted")
    if trace is None:
        return EntailmentResult("NotFound", None, searcher.steps,
                                "saturated open branch; no entailment certificate found")
    certificate = {**_binding(env, premises, conclusion), "trace": trace}
    # Treat search output like hostile input: replay before advertising success.
    checked = check_entailment_certificate(env, premises, conclusion, certificate,
                                           max_steps=max_steps)
    if not checked.valid:
        return EntailmentResult("ResourceLimit" if checked.status == "ResourceLimit" else "NotFound",
                                None, searcher.steps, "generated trace did not replay")
    return EntailmentResult("Found", certificate, searcher.steps)


class _Replayer:
    def __init__(self, maximum: int): self.maximum, self.steps = maximum, 0

    def replay(self, branch: _Branch, node: Any, depth: int = 0) -> None:
        if depth > MAX_TABLEAU_DEPTH: raise _Budget
        if self.steps >= self.maximum: raise _Budget
        self.steps += 1
        if type(node) is not dict: raise _InvalidTrace("trace node must be an object")
        rule = node.get("rule")
        if rule == "close":
            if set(node) != {"rule"} or not _closed(branch):
                raise _InvalidTrace("open or malformed close node")
            return
        allowed = {"rule", "at", "children", "parameter"}
        if rule != "expand" or not set(node) <= allowed or not {"rule", "at", "children"} <= set(node):
            raise _InvalidTrace("malformed expansion node")
        parameter = node.get("parameter")
        alternatives = _derive(branch, node["at"], parameter)
        children = node["children"]
        if type(children) is not list or len(children) != len(alternatives):
            raise _InvalidTrace("wrong tableau branch count")
        for additions, child in zip(alternatives, children, strict=True):
            self.replay(_apply(branch, node["at"], parameter, additions), child, depth + 1)


def check_entailment_certificate(env: Any, premises: Sequence[Any], conclusion: Any,
                                 certificate: Any, *, max_steps: int = 10_000
                                 ) -> EntailmentCertificateCheck:
    """Replay a certificate against the exact environment and ordered formulas."""
    try:
        # Validate data before equality comparisons: even binding fields cannot
        # carry arbitrary Python objects or their overloaded comparison methods.
        canonical_json(certificate)
        premises = _validate_inputs(env, premises, conclusion)
        if type(max_steps) is not int or isinstance(max_steps, bool) or max_steps < 0:
            raise ValueError("max_steps must be a nonnegative integer")
        if type(certificate) is not dict or set(certificate) != set(_binding(env, premises, conclusion)) | {"trace"}:
            raise _InvalidTrace("certificate fields do not match the wire schema")
        expected = _binding(env, premises, conclusion)
        if any(certificate.get(key) != value for key, value in expected.items()):
            raise _InvalidTrace("certificate is stale or bound to different inputs")
        replayer = _Replayer(max_steps)
        replayer.replay(_initial_branch(env, premises, conclusion), certificate["trace"])
        return EntailmentCertificateCheck(True, "Valid", replayer.steps)
    except _Budget:
        return EntailmentCertificateCheck(False, "ResourceLimit", max_steps,
                                          "certificate replay budget exhausted")
    except (ResourceLimit, RecursionError) as exc:
        return EntailmentCertificateCheck(False, "ResourceLimit", 0, str(exc))
    except (VEError, ValueError, TypeError, KeyError, IndexError, AttributeError,
            _InvalidTrace) as exc:
        return EntailmentCertificateCheck(False, "InvalidCertificate", 0, str(exc))
