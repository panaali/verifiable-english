"""Checkable semantic-tableau evidence for many-sorted relational FOL.

Proof search in this module is a convenience and is deliberately outside the
trust boundary.  A positive result is justified only by replaying its data-only
tableau with :func:`check_entailment_certificate`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Sequence

from .assurance import semantic_entry
from .ast import (And, Atom, Binary, Bottom, Const, Document, Eq, Exists, Forall, Implies,
                   Not, Or, Top, Unary, Var, Reach, Named, check_document, _Checker)
from .errors import CheckerUnavailable, ResourceLimit, UnsupportedProfile, VEError
from .identity import meaning_id
from .limits import MAX_NODES, MAX_TABLEAU_DEPTH
from .wire import canonical_json
from .order import Budget as _OrderBudget, InvalidTrace as _OrderInvalid


ENTAILMENT_CHECKER_VERSION = "ve-tableau-checker@2"
CLOSURE_CHECKER_VERSION = "ve-tableau-closure-checker@1"
CORE_CHECKER_VERSION = "ve-tableau-core-checker@1"


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
    signatures: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def copy(self) -> "_Branch":
        return _Branch(list(self.formulas), dict(self.parameters), set(self.expanded),
                       set(self.instantiated), self.next_witness, self.signatures)


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


def _validate_inputs(env: Any, premises: Sequence[Any], conclusion: Any, *,
                     background: bool = True,
                     generated_premises: Sequence[bool] | None = None) -> tuple[Any, ...]:
    """The checked list is Background ++ layer premises ++ caller premises.
    P0 has no executable layers, so its layer segment is empty. `background`
    is False only for an already expanded list or for admission graph edges,
    whose Background premises are explicit labelled leaves."""
    premises = _premises(premises)
    if generated_premises is not None:
        if background or len(generated_premises) != len(premises):
            raise ValueError("generated premise labels must match the explicit premises")
        checker = _Checker(env)
        for formula, generated in zip(premises, generated_premises, strict=True):
            checker.generated = generated
            checker.formula(formula)
        checker.generated = False
        checker.formula(conclusion)
    elif background:
        check_document(env, Document((*premises, conclusion)))
    else:
        from .background import background as generated_background
        generated = tuple(p.formula for p in generated_background(env))
        prefix = premises[:len(generated)]
        if prefix == generated:
            check_document(env, Document((*premises[len(generated):], conclusion)))
            checker = _Checker(env, generated=True)
            for formula in prefix:
                checker.formula(formula)
        else:
            check_document(env, Document((*premises, conclusion)))
    if background:
        from .background import background as generated_background
        generated = tuple(p.formula for p in generated_background(env))
        checker = _Checker(env, generated=True)
        for formula in generated:
            checker.formula(formula)
        premises = generated + premises
    return premises


def _initial_branch(env: Any, premises: tuple[Any, ...], conclusion: Any) -> _Branch:
    parameters = {f"c:{name}": decl.sort for name, decl in env.constants.items()}
    signed = [_Signed(formula, True) for formula in premises]
    signed.append(_Signed(conclusion, False))
    return _Branch(signed, parameters, set(), set(), signatures={
        name: tuple(decl.arguments) for name, decl in env.predicates.items()})


def _kind(item: _Signed) -> str:
    f, pos = item.formula, item.positive
    if type(f) is Reach: return "closure"
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
        elif type(f) is Reach:
            from .closure import congruence_key
            atom = congruence_key(f, item.bindings, find)
            (positive if item.positive else negative).add(atom)
        elif type(f) is Unary:
            atom = (f.predicate, find(_term_token(f.term, item.bindings)))
            (positive if item.positive else negative).add(atom)
        elif type(f) is Binary:
            atom = (f.predicate, find(_term_token(f.left, item.bindings)),
                    find(_term_token(f.right, item.bindings)))
            (positive if item.positive else negative).add(atom)
        elif type(f) is Atom:
            atom = (f.predicate, *(find(_term_token(t, item.bindings)) for t in f.terms))
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
    if kind == "closure":
        if parameter is not None:
            raise _InvalidTrace("closure unfolding has no supplied parameter")
        from .closure import unfold
        sort = branch.parameters[_term_token(f.left, bindings)]
        return [[_Signed(unfold(f, sort), pos, bindings)]]
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
        if kind is Atom: return ("Atom", f.predicate, *(term(t) for t in f.terms))
        if kind is Eq: return ("Eq", term(f.left), term(f.right))
        if kind is Reach:
            edge = (("Named", f.edge.relation) if type(f.edge) is Named else
                    ("Body", f.edge.sort, walk(f.edge.formula, bound + 2)))
            return ("Reach", f.kind, edge, term(f.left), term(f.right))
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
        if kind is Atom: return ("atom", positive, f.predicate, *(term(t) for t in f.terms))
        if kind is Eq: return ("eq", positive, frozenset((term(f.left), term(f.right))))
        if kind is Reach:
            # Edge truth is independent of the sign of the enclosing Reach.
            edge = (("named", f.edge.relation) if type(f.edge) is Named else
                    ("body", f.edge.sort, walk(f.edge.formula, True, bound + 2)))
            return ("reach", positive, f.kind, edge, term(f.left), term(f.right))
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
    def __init__(self, maximum: int, closure: bool = False, *, env=None, invariants=(), focused=False):
        self.maximum, self.steps = maximum, 0
        self.closure = closure
        self.env, self.invariants = env, invariants
        self.focused = focused
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
        if self.invariants:
            from .closure import induction_candidates
            from .ast import _to_data
            for at, sort, invariant, alternatives in induction_candidates(self.env, branch, self.invariants):
                if self.instance_key(alternatives[2][0]) in keys:
                    continue
                base = branch.copy()
                base.formulas.extend(alternatives[0])
                base_trace = {'rule': 'close'} if _closed(base) else None
                if base_trace is None:
                    f = alternatives[0][0].formula
                    if type(f) is And:
                        f = f.left
                    # A matching pair of endpoints is a useful base hint for
                    # relational invariants (e.g. edge inclusion). It is only
                    # scheduling: the base still needs a complete subproof.
                    if type(f) not in (Binary, Reach):
                        continue
                    endpoints = tuple(_term_token(t, alternatives[0][0].bindings)
                                      for t in (f.left, f.right))
                    if not any(a.positive and type(a.formula) in (Binary, Reach) and
                               tuple(_term_token(t, a.bindings) for t in
                                     (a.formula.left, a.formula.right)) == endpoints
                               for a in branch.formulas):
                        continue
                    base.expanded.update(i for i, a in enumerate(branch.formulas)
                                         if type(a.formula) is Reach)
                    attempt = _Searcher(min(250, self.maximum - self.steps), self.closure, focused=True)
                    try:
                        base_trace = attempt.prove(base)
                    except (_Budget, RecursionError):
                        base_trace = None
                    self.steps += attempt.steps
                    if base_trace is None:
                        continue
                step = branch.copy()
                step.formulas.extend(alternatives[1])
                # Suppress existing-path unfolding in this bounded search
                # attempt; other preservation proofs may need another schedule.
                step.expanded.update(i for i, a in enumerate(branch.formulas)
                                     if type(a.formula) is Reach)
                attempt = _Searcher(min(1000, self.maximum - self.steps), self.closure, focused=True)
                try:
                    step_trace = attempt.prove(step)
                except (_Budget, RecursionError):
                    step_trace = None
                self.steps += attempt.steps
                if step_trace is None:
                    continue
                continuation = branch.copy()
                continuation.formulas.extend(alternatives[2])
                child = self.search(continuation, depth + 1)
                if child is not None:
                    return {'rule': 'closure-induct@1', 'at': at, 'sort': sort,
                            'invariant': _to_data(invariant),
                            'children': [base_trace, step_trace, child]}
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
                            2 if kind == "delta" or (self.invariants and kind == "closure"
                                                     and item.positive) else
                            3 if kind == "gamma" else 4)
                rank = ((priority, -hits, counts.get(at, 0), at, order) if self.focused else
                        (priority, counts.get(at, 0), at, -hits, order))
                choices.append((rank, _rule(item), at, token, additions))
        if self.closure:
            from .closure import extra_candidates
            for rule, at, token, addition in extra_candidates(branch):
                if all(self.instance_key(x) in keys for x in addition):
                    continue
                # Goal-directed derived consequences avoid eagerly generating
                # infinitely many new existential witnesses from unfolded paths.
                connects = any(self.connection_key(x) in complements for x in addition)
                if connects or rule in ("closure-compose@0", "closure-edge@0"):
                    priority = -1 if connects else 3
                    choices.append(((priority, 0, at, 0, 0), rule, at, token, [addition]))
        if not choices: return None
        choices.sort(key=lambda choice: choice[0])
        # A depth frontier is a failed ordering, not a global budget abort.
        # Try other available expansions while retaining the global step cap.
        for _, rule, at, parameter, alternatives in choices:
            frontier = self.depth_cutoffs
            children = []
            for addition in alternatives:
                if rule in ("expand", "closure-plus@0", "closure-star@0"):
                    next_branch = _apply(branch, at, parameter, addition)
                else:
                    next_branch = branch.copy()
                    next_branch.formulas.extend(addition)
                child = self.search(next_branch, depth + 1)
                if child is None: break
                children.append(child)
            else:
                node: dict[str, Any] = {"rule": rule, "at": at, "children": children}
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


def _rule(item):
    if type(item.formula) is Reach:
        return "closure-" + item.formula.kind + "@0"
    return "expand"


def _binding(env: Any, premises: tuple[Any, ...], conclusion: Any, *,
             generated_premises: Sequence[bool] | None = None) -> dict[str, Any]:
    from .order import CHECKER_VERSION as ORDER_CHECKER_VERSION
    from .background import background as generated_background
    generated = tuple(p.formula for p in generated_background(env))
    return {"checker_version": (ORDER_CHECKER_VERSION if getattr(env, "order", False) else
                                CORE_CHECKER_VERSION if "nary@0" in env.profiles else
                                CLOSURE_CHECKER_VERSION if env.closure else ENTAILMENT_CHECKER_VERSION),
            "environment_id": env.environment_id,
            "premise_meaning_ids": [meaning_id(env, x, _generated=(generated_premises[i]
                                    if generated_premises is not None else
                                    i < len(generated) and x == generated[i]))
                                    for i, x in enumerate(premises)],
            "conclusion_meaning_id": meaning_id(env, conclusion)}


def prove_entailment(env: Any, premises: Sequence[Any], conclusion: Any, *,
                     max_steps: int = 10_000, invariants: Sequence[Any] = (),
                     _background: bool = True) -> EntailmentResult:
    """Search for a closed tableau. Failure is inconclusive, never refutation.

    In closure@0, invariants accepts unary formulas (index 0 is the node), or
    InductionInvariant hints with explicit captured tableau parameter tokens.
    The certificate includes each selected formula and all three subproofs.
    """
    if getattr(env, "alternatives", None) is not None:
        raise CheckerUnavailable("alternatives@0 requires the Lean checker")
    premises = _validate_inputs(env, premises, conclusion, background=_background)
    if type(max_steps) is not int or isinstance(max_steps, bool) or max_steps < 0:
        raise ValueError("max_steps must be a nonnegative integer")
    if invariants and not env.closure:
        raise ValueError("induction invariants require closure@0")
    if getattr(env, "order", False):
        return _prove_order(env, premises, conclusion, max_steps)
    searcher = _Searcher(max_steps, env.closure, env=env, invariants=tuple(invariants))
    try:
        trace = searcher.prove(_initial_branch(env, premises, conclusion))
    except (_Budget, RecursionError):
        return EntailmentResult("ResourceLimit", None, searcher.steps, "tableau step or certificate nesting budget exhausted")
    if trace is None:
        return EntailmentResult("NotFound", None, searcher.steps,
                                ("no certificate found by the implemented closure rules; failure is inconclusive"
                                 if env.closure else "saturated open branch; no entailment certificate found"))
    certificate = {**_binding(env, premises, conclusion), "trace": trace}
    # Treat search output like hostile input: replay before advertising success.
    checked = check_entailment_certificate(env, premises, conclusion, certificate,
                                           max_steps=max_steps, _background=False)
    if not checked.valid:
        return EntailmentResult("ResourceLimit" if checked.status == "ResourceLimit" else "NotFound",
                                None, searcher.steps, "generated trace did not replay")
    return EntailmentResult("Found", certificate, searcher.steps)


def _prove_order(env, premises, conclusion, max_steps) -> EntailmentResult:
    """order@0: untrusted Farkas-tableau search, then independent replay."""
    from .order import search
    trace, steps = search(env, premises, conclusion, max_steps)
    if trace is None:
        return EntailmentResult("NotFound", None, steps,
                                "no order@0 certificate found by the implemented rules; failure is inconclusive")
    certificate = {**_binding(env, premises, conclusion), "trace": trace}
    checked = check_entailment_certificate(env, premises, conclusion, certificate,
                                           max_steps=max(max_steps, 10_000), _background=False)
    if not checked.valid:
        return EntailmentResult("ResourceLimit" if checked.status == "ResourceLimit" else "NotFound",
                                None, steps, "generated trace did not replay")
    return EntailmentResult("Found", certificate, steps)


class _Replayer:
    def __init__(self, maximum: int, closure: bool = False, *, env=None, induction=False):
        self.maximum, self.steps, self.closure = maximum, 0, closure
        self.env, self.induction = env, induction

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
        from .closure import EXTRA_RULES, derive_extra
        if self.induction and rule == 'closure-induct@1':
            from .ast import _Decoder
            from .closure import derive_induction
            if set(node) != {'rule', 'at', 'sort', 'invariant', 'children'}:
                raise _InvalidTrace('malformed induction node')
            invariant = _Decoder().decode(node['invariant'])
            alternatives = derive_induction(self.env, branch, node['at'], node['sort'], invariant)
            if type(node['children']) is not list or len(node['children']) != 3:
                raise _InvalidTrace('induction requires three children')
            for additions, child in zip(alternatives, node['children'], strict=True):
                next_branch = branch.copy()
                next_branch.formulas.extend(additions)
                self.replay(next_branch, child, depth + 1)
            return
        if self.closure and rule in EXTRA_RULES:
            if not set(node) <= {"rule", "at", "children", "parameter"} or not {"rule", "at", "children"} <= set(node):
                raise _InvalidTrace("malformed closure consequence")
            additions = derive_extra(branch, rule, node["at"], node.get("parameter"))
            children = node["children"]
            if type(children) is not list or len(children) != 1:
                raise _InvalidTrace("closure consequence requires one child")
            child = branch.copy()
            child.formulas.extend(additions)
            self.replay(child, children[0], depth + 1)
            return
        allowed = {"rule", "at", "children", "parameter"}
        if rule not in ("expand", "closure-plus@0", "closure-star@0") or not set(node) <= allowed or not {"rule", "at", "children"} <= set(node):
            raise _InvalidTrace("malformed expansion node")
        parameter = node.get("parameter")
        alternatives = _derive(branch, node["at"], parameter)
        if rule != _rule(branch.formulas[node["at"]]):
            raise _InvalidTrace("wrong versioned rule for target formula")
        children = node["children"]
        if type(children) is not list or len(children) != len(alternatives):
            raise _InvalidTrace("wrong tableau branch count")
        for additions, child in zip(alternatives, children, strict=True):
            self.replay(_apply(branch, node["at"], parameter, additions), child, depth + 1)


@semantic_entry("certificate.check")
def check_entailment_certificate(env: Any, premises: Sequence[Any], conclusion: Any,
                                 certificate: Any, *, max_steps: int = 10_000,
                                 _background: bool = True,
                                 _generated_premises: Sequence[bool] | None = None) -> EntailmentCertificateCheck:
    """Replay a certificate under the selected authority.

    The prover's self-replay of a generated trace (`_background=False`) and
    replays with labelled generated premises belong to the retained proof
    generator and stay Python's.
    """
    from .backends.dispatch import authority_for, execute
    args = (env, premises, conclusion, certificate)
    options = {"max_steps": max_steps, "_background": _background,
               "_generated_premises": _generated_premises}
    if (authority_for("certificate_replay") == "python" or not _background
            or _generated_premises is not None):
        return _check_certificate_python(*args, **options)
    payload = {"environment_id": getattr(env, "environment_id", None),
               "certificate": certificate if type(certificate) is dict else None}
    return execute("certificate_replay", payload,
                   lambda: _check_certificate_python(*args, **options),
                   lean=lambda: _check_certificate_lean(env, premises, conclusion, certificate, max_steps))


def _trace_nodes(node: Any) -> int:
    """Python's replay charge, one step per trace node, counted structurally."""
    total, stack = 0, [node]
    while stack:
        item = stack.pop()
        if type(item) is not dict:
            raise _InvalidTrace("trace node must be an object")
        total += 1
        children = item.get("children", [])
        if type(children) is list:
            stack.extend(children)
    return total


def _replay_prechecks(env, premises, conclusion, certificate, max_steps):
    """Python's input, wire-schema and binding checks before a Lean replay.

    They run in Python's order with Python's wording. The result is the trace's
    node count (Python's replay charge), or the rejection record. They never
    accept a certificate: validity is the Lean replay's.
    """
    try:
        canonical_json(certificate)
        full = _validate_inputs(env, premises, conclusion, background=True)
        if type(max_steps) is not int or isinstance(max_steps, bool) or max_steps < 0:
            raise ValueError("max_steps must be a nonnegative integer")
        expected = _binding(env, full, conclusion)
        if type(certificate) is not dict or set(certificate) != set(expected) | {"trace"}:
            raise _InvalidTrace("certificate fields do not match the wire schema")
        if env.closure and "nary@0" not in env.profiles and certificate.get('checker_version') == 've-tableau-closure-checker@0':
            expected['checker_version'] = 've-tableau-closure-checker@0'
        if any(certificate.get(key) != value for key, value in expected.items()):
            raise _InvalidTrace("certificate is stale or bound to different inputs")
        return _trace_nodes(certificate["trace"])
    except (ResourceLimit, RecursionError) as exc:
        return EntailmentCertificateCheck(False, "ResourceLimit", 0, str(exc))
    except (VEError, ValueError, TypeError, KeyError, IndexError, AttributeError, _InvalidTrace) as exc:
        return EntailmentCertificateCheck(False, "InvalidCertificate", 0, str(exc))


def _lean_replay_record(replay, nodes: int, max_steps: int) -> EntailmentCertificateCheck:
    """The public record of a Lean replay (`replay()` is Lean's validity).

    Lean decides validity over the whole trace; Python's budget charges one
    step per node before checking it. Below a trace's node count the outcome
    depends on where an invalid trace first fails, which Lean does not report,
    so that case is CheckerUnavailable rather than a guess.
    """
    try:
        valid = replay()
    except ResourceLimit as exc:
        if str(exc).startswith("ResourceLimit: certificate replay exceeds"):
            raise CheckerUnavailable("CheckerUnavailable: the trace exceeds the Lean route's "
                                     "replay cap") from None
        return EntailmentCertificateCheck(False, "ResourceLimit", 0, str(exc))
    except UnsupportedProfile as exc:
        # A case Lean does not implement is a gap, never an invalid certificate.
        raise CheckerUnavailable(f"CheckerUnavailable: {exc.message}") from None
    except VEError as exc:
        return EntailmentCertificateCheck(False, "InvalidCertificate", 0, str(exc))
    if nodes > max_steps:
        if valid:
            return EntailmentCertificateCheck(False, "ResourceLimit", max_steps,
                                              "certificate replay budget exhausted")
        raise CheckerUnavailable("CheckerUnavailable: the replay budget is below the trace size "
                                 "and Lean does not report where the trace fails")
    if valid:
        return EntailmentCertificateCheck(True, "Valid", nodes)
    return EntailmentCertificateCheck(False, "InvalidCertificate", 0, "certificate does not replay")


def _check_certificate_lean(env, premises, conclusion, certificate, max_steps) -> EntailmentCertificateCheck:
    """Validate inputs and bindings as Python does, then replay in Lean."""
    from .ast import _to_data
    from .backends.lean_runner import route_mode
    from .backends.relay import decide
    if getattr(env, "alternatives", None) is not None:
        return EntailmentCertificateCheck(False, "InvalidCertificate", 0,
                                          "alternatives@0 requires the Lean checker")
    nodes = _replay_prechecks(env, premises, conclusion, certificate, max_steps)
    if isinstance(nodes, EntailmentCertificateCheck):
        return nodes
    case = {"id": "certificate", "environment": env.to_dict(),
            "premises": [_to_data(p) for p in premises], "conclusion": _to_data(conclusion),
            "certificate": certificate}
    if env.language == "ve.core@0.2":
        # Lean's own cap is the trace size, so it reports validity; the public
        # budget is applied below. The norms route's Plain glue also answers
        # environments with statement layers; soft and rights premises are a
        # validated soft or rights document's Background slots, carried by the case.
        from .profiles import STATEMENT_LAYERS
        layered = STATEMENT_LAYERS & set(env.profiles)
        mode = "norms" if layered else route_mode(env)
        # Background order: the environment's generators, then soft, then rights.
        soft = (*getattr(env, "soft_premises", ()), *getattr(env, "rights_premises", ()))
        case = {**case, "kind": "certificate", "max_steps": max(nodes, 10_000),
                **({"soft_premises": [_to_data(f) for _, f in soft]} if soft else {})}
    elif env.order:
        mode, case = "order", {**case, "kind": "certificate"}
    else:
        mode = "check-certificate"
    return _lean_replay_record(lambda: decide(mode, [case])[0]["valid"], nodes, max_steps)


def _check_certificate_python(env: Any, premises: Sequence[Any], conclusion: Any,
                              certificate: Any, *, max_steps: int = 10_000,
                              _background: bool = True,
                              _generated_premises: Sequence[bool] | None = None) -> EntailmentCertificateCheck:
    """Replay a certificate against the exact environment and ordered formulas."""
    if getattr(env, "alternatives", None) is not None:
        return EntailmentCertificateCheck(False, "InvalidCertificate", 0,
                                          "alternatives@0 requires the Lean checker")
    try:
        # Validate data before equality comparisons: even binding fields cannot
        # carry arbitrary Python objects or their overloaded comparison methods.
        canonical_json(certificate)
        premises = _validate_inputs(env, premises, conclusion, background=_background,
                                    generated_premises=_generated_premises)
        if type(max_steps) is not int or isinstance(max_steps, bool) or max_steps < 0:
            raise ValueError("max_steps must be a nonnegative integer")
        if type(certificate) is not dict or set(certificate) != set(_binding(
                env, premises, conclusion, generated_premises=_generated_premises)) | {"trace"}:
            raise _InvalidTrace("certificate fields do not match the wire schema")
        expected = _binding(env, premises, conclusion, generated_premises=_generated_premises)
        if env.closure and "nary@0" not in env.profiles and certificate.get('checker_version') == 've-tableau-closure-checker@0':
            expected['checker_version'] = 've-tableau-closure-checker@0'
        if any(certificate.get(key) != value for key, value in expected.items()):
            raise _InvalidTrace("certificate is stale or bound to different inputs")
        if getattr(env, "order", False):
            from .order import replay_trace
            valid, steps = replay_trace(env, premises, conclusion, certificate["trace"], max_steps)
            if not valid:
                raise _InvalidTrace("order certificate does not replay")
            return EntailmentCertificateCheck(True, "Valid", steps)
        replayer = _Replayer(max_steps, env.closure, env=env,
                            induction=env.closure and certificate['checker_version'] in
                            (CLOSURE_CHECKER_VERSION, CORE_CHECKER_VERSION))
        replayer.replay(_initial_branch(env, premises, conclusion), certificate["trace"])
        return EntailmentCertificateCheck(True, "Valid", replayer.steps)
    except _Budget:
        return EntailmentCertificateCheck(False, "ResourceLimit", max_steps,
                                          "certificate replay budget exhausted")
    except _OrderBudget:
        return EntailmentCertificateCheck(False, "ResourceLimit", max_steps,
                                          "certificate replay budget exhausted")
    except _OrderInvalid as exc:
        return EntailmentCertificateCheck(False, "InvalidCertificate", 0, str(exc))
    except (ResourceLimit, RecursionError) as exc:
        return EntailmentCertificateCheck(False, "ResourceLimit", 0, str(exc))
    except (VEError, ValueError, TypeError, KeyError, IndexError, AttributeError,
            _InvalidTrace) as exc:
        return EntailmentCertificateCheck(False, "InvalidCertificate", 0, str(exc))
