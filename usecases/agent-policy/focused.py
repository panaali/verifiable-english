"""A focused tableau search that emits ordinary VE entailment certificates.

VE's own prover finds each rule's applicability for one logged action within a
few hundred steps, but exhausts its budget on the 24-rule selection formulas
(PLAN section 12). The selection formulas are Boolean combinations of those
applicability formulas, so this search closes them against already proved
lemmas. It only chooses expansions: every step is VE's `_derive`/`_apply` rule,
every close node passes VE's `_closed` on replay, and the result is returned only after
`check_entailment_certificate` (or the norm variant) replays it. A search
failure proves nothing.

Two closed or open formulas with the same meaning under their parameter
bindings are closed in lock step (`pair`): the positive and negative copies are
expanded together down to complementary literals.
"""
from __future__ import annotations

from ve.ast import And, Atom, Binary, Bottom, Const, Eq, Exists, Forall, Implies, Not, Or, Top, Unary, Var
from ve.entailment import (_apply, _binding, _derive, _initial_branch, _kind,
                           _validate_inputs, check_entailment_certificate)


class Failed(Exception):
    """The focused search found no closing trace (inconclusive)."""


def _term(term, bindings, depth):
    if type(term) is Var:
        return ("var", term.index) if term.index < depth else bindings[term.index - depth]
    if type(term) is Const:
        return "c:" + term.name
    raise Failed("unsupported term")


_KEYS = {}


def key(formula, bindings=(), depth=0):
    """A binding-independent identity: free variables become their tokens."""
    cached = _KEYS.get((id(formula), bindings, depth))
    if cached is not None and cached[0] is formula:
        return cached[1]
    # Interned small integers keep hashing constant-time for large formulas.
    result = _INTERNED.setdefault(_key(formula, bindings, depth), len(_INTERNED))
    _KEYS[(id(formula), bindings, depth)] = (formula, result)
    return result


_INTERNED = {}


def _key(formula, bindings, depth):
    f = formula
    if type(f) is Unary:
        return ("u", f.predicate, _term(f.term, bindings, depth))
    if type(f) is Binary:
        return ("b", f.predicate, _term(f.left, bindings, depth), _term(f.right, bindings, depth))
    if type(f) is Atom:
        return ("a", f.predicate, *(_term(t, bindings, depth) for t in f.terms))
    if type(f) is Eq:
        return ("=", _term(f.left, bindings, depth), _term(f.right, bindings, depth))
    if type(f) in (Top, Bottom):
        return (type(f).__name__,)
    if type(f) is Not:
        return ("not", key(f.body, bindings, depth))
    if type(f) in (And, Or, Implies):
        return (type(f).__name__, key(f.left, bindings, depth), key(f.right, bindings, depth))
    if type(f) in (Forall, Exists):
        return (type(f).__name__, f.sort, key(f.body, bindings, depth + 1))
    raise Failed("unsupported formula")


def _value(f, bindings, known, exclude=None):
    """Kleene value from the branch items other than `exclude`: True, False or None."""
    for index, sign in known.get(key(f, bindings), ()):
        if index != exclude:
            return sign
    if type(f) is Top:
        return True
    if type(f) is Bottom:
        return False
    if type(f) is Not:
        v = _value(f.body, bindings, known, exclude)
        return None if v is None else not v
    if type(f) in (And, Or, Implies):
        left = _value(f.left, bindings, known, exclude)
        right = _value(f.right, bindings, known, exclude)
        if type(f) is Implies:
            left = None if left is None else not left
        if type(f) is And:
            if left is False or right is False:
                return False
            return True if left is True and right is True else None
        if left is True or right is True:
            return True
        return False if left is False and right is False else None
    return None


def _size(formula):
    return 1 + sum(_size(getattr(formula, f)) for f in ("left", "right", "body")
                   if hasattr(formula, f) and not isinstance(getattr(formula, f), (Const, Var)))


_LITERALS = (Unary, Binary, Atom, Eq, Top, Bottom)


def closed(branch):
    """A cheap sufficient test for VE's `_closed`: complementary literals over the
    same tokens, a true Bottom, a false Top or a false self-equality. VE's
    replay re-checks every close node with `_closed` itself."""
    signs = {}
    for item in branch.formulas:
        f = item.formula
        if type(f) not in _LITERALS:
            continue
        if (type(f) is Bottom and item.positive) or (type(f) is Top and not item.positive):
            return True
        if type(f) is Eq and not item.positive and \
                _term(f.left, item.bindings, 0) == _term(f.right, item.bindings, 0):
            return True
        k = key(f, item.bindings)
        if signs.setdefault(k, item.positive) != item.positive:
            return True
    return False


class Search:
    def __init__(self, max_nodes=200_000, parameters=()):
        self.nodes = 0
        self.max_nodes = max_nodes
        self.parameters = tuple(parameters)

    def tick(self):
        self.nodes += 1
        if self.nodes > self.max_nodes:
            raise Failed("node budget")

    # --- bookkeeping -----------------------------------------------------
    @staticmethod
    def _expand(branch, at, parameter=None):
        alternatives = _derive(branch, at, parameter)
        return [(_apply(branch, at, parameter, addition), len(branch.formulas)) for addition in alternatives]

    @staticmethod
    def _node(at, children, parameter=None):
        node = {"rule": "expand", "at": at, "children": children}
        if parameter is not None:
            node["parameter"] = parameter
        return node

    def _known(self, branch):
        """Signed keys on the branch. A passive premise stated as a negation
        also gives the value of its body; an active item's body appears
        only once it is expanded, so no item is valued by its own ancestor."""
        known = {}
        for index, item in enumerate(branch.formulas):
            f, positive = item.formula, item.positive
            known.setdefault(key(f, item.bindings), []).append((index, positive))
            while type(f) is Not and index < self.first_active:
                f, positive = f.body, not positive
                known.setdefault(key(f, item.bindings), []).append((index, positive))
        return known

    @staticmethod
    def _free(branch, at):
        return _kind(branch.formulas[at]) in ("gamma", "literal") or at not in branch.expanded

    def _partner(self, branch, at):
        """An unexpanded item with the same key and the opposite sign."""
        item = branch.formulas[at]
        k = key(item.formula, item.bindings)
        for j, other in enumerate(branch.formulas):
            if j != at and other.positive != item.positive and self._free(branch, j) \
                    and key(other.formula, other.bindings) == k:
                return j
        return None

    # --- lock-step closure of two complementary copies -------------------
    def pair(self, branch, p, n):
        """Close a branch holding item p (positive) and item n (negative) of equal meaning."""
        self.tick()
        if closed(branch):
            return {"rule": "close"}
        f = branch.formulas[p].formula
        if type(f) is Not:
            (b1, i), = self._expand(branch, p)
            (b2, j), = self._expand(b1, n)
            return self._node(p, [self._node(n, [self.pair(b2, j, i)])])
        if type(f) is And:
            (b1, i), = self._expand(branch, p)
            children = [self.pair(b, i + k, j) for k, (b, j) in enumerate(self._expand(b1, n))]
            return self._node(p, [self._node(n, children)])
        if type(f) is Or:
            (b1, i), = self._expand(branch, n)
            children = [self.pair(b, j, i + k) for k, (b, j) in enumerate(self._expand(b1, p))]
            return self._node(n, [self._node(p, children)])
        if type(f) is Implies:
            (b1, i), = self._expand(branch, n)
            (bl, jl), (br, jr) = self._expand(b1, p)
            return self._node(n, [self._node(p, [self.pair(bl, i, jl), self.pair(br, jr, i + 1)])])
        if type(f) is Exists:
            token = f"w:{branch.next_witness}"
            (b1, i), = self._expand(branch, p)
            (b2, j), = self._expand(b1, n, token)
            return self._node(p, [self._node(n, [self.pair(b2, i, j)], token)])
        if type(f) is Forall:
            token = f"w:{branch.next_witness}"
            (b1, i), = self._expand(branch, n)
            (b2, j), = self._expand(b1, p, token)
            return self._node(n, [self._node(p, [self.pair(b2, j, i)], token)])
        raise Failed("complementary literals did not close")

    def close_pair(self, branch, at, partner):
        return self.pair(branch, at, partner) if branch.formulas[at].positive else self.pair(branch, partner, at)

    # --- goal-directed refutation ----------------------------------------
    def refute(self, branch, at):
        """Close a branch whose item `at` is false under the known values."""
        self.tick()
        if closed(branch):
            return {"rule": "close"}
        partner = self._partner(branch, at)
        if partner is not None:
            return self.close_pair(branch, at, partner)
        item = branch.formulas[at]
        # Expose a lemma stated as a negation: (not X, s) holds (X, not s).
        target = (item.positive, key(item.formula, item.bindings))
        for j, other in enumerate(branch.formulas):
            if (type(other.formula) is Not and other.positive == target[0] and j not in branch.expanded
                    and key(other.formula.body, other.bindings) == target[1]):
                (b1, i), = self._expand(branch, j)
                return self._node(j, [self.close_pair(b1, at, i)])
        kind = _kind(item)
        if kind == "not":
            (b1, i), = self._expand(branch, at)
            return self._node(at, [self.refute(b1, i)])
        if kind == "alpha":
            (b1, i), = self._expand(branch, at)
            known = self._known(b1)
            for k in (0, 1):
                if self.refutable(b1, i + k, known):
                    return self._node(at, [self.refute(b1, i + k)])
            return self._node(at, [self.search(b1)])
        if kind == "beta":
            return self._node(at, [self.refute(b, j) for b, j in self._expand(branch, at)])
        raise Failed("no refutation for this item")

    def refutable(self, branch, at, known=None):
        item = branch.formulas[at]
        known = self._known(branch) if known is None else known
        return _value(item.formula, item.bindings, known, at) is (not item.positive)

    def search(self, branch, active=None):
        """Small complete-for-propositional search over the active items."""
        self.tick()
        if closed(branch):
            return {"rule": "close"}
        items = range(len(branch.formulas))
        known = self._known(branch)
        for at in items:
            if self._free(branch, at) and _kind(branch.formulas[at]) != "literal":
                if self._partner(branch, at) is not None:
                    return self.close_pair(branch, at, self._partner(branch, at))
        for at in items:
            if at not in branch.expanded and _kind(branch.formulas[at]) != "literal" \
                    and self.refutable(branch, at, known):
                return self.refute(branch, at)
        pending = [at for at in items if at not in branch.expanded and self.active(branch, at)]
        for at in pending:
            if _kind(branch.formulas[at]) in ("not", "alpha", "delta"):
                (b1, _), = self._expand(branch, at)
                return self._node(at, [self.search(b1)])
        betas = [at for at in pending if _kind(branch.formulas[at]) == "beta"]
        for at in betas:
            children = self._expand(branch, at)
            if any(closed(b) or self.refutable(b, j) for b, j in children):
                return self._node(at, [self.search(b) for b, _ in children])
        # Instantiate universals at the witnesses already on the branch before
        # splitting cases, so that case splits happen on small formulas.
        for at, item in enumerate(branch.formulas):
            if _kind(item) == "gamma" and self.active(branch, at):
                for token, sort in branch.parameters.items():
                    if sort == item.formula.sort and (at, token) not in branch.instantiated \
                            and (token.startswith("w:") or token in self.parameters):
                        (b1, _), = self._expand(branch, at, token)
                        return self._node(at, [self.search(b1)], token)
        if betas:
            at = min(betas, key=lambda i: _size(branch.formulas[i].formula))
            return self._node(at, [self.search(b) for b, _ in self._expand(branch, at)])
        raise Failed("open branch")

    def active(self, branch, at):
        return at >= self.first_active


def prove(env, premises, conclusion, *, instantiate=(), parameters=(), max_nodes=200_000,
          replay=None, active_premises=False):
    """Search, then replay; returns (certificate, nodes) or raises Failed.

    `premises` is the complete explicit list (for norms: the layers, then the
    caller's premises); Background is added as VE adds it. `instantiate` lists
    (premise index, constant name) pairs opened first, such as a norm layer at
    the logged action. The negated conclusion and everything derived after it
    are active; premises are expanded only to close against an active item,
    unless `active_premises` also makes the caller's premises active (for
    universal assumptions that must be instantiated at a witness).
    `replay(certificate)` must return VE's replay result; by default it is
    `check_entailment_certificate` over the same inputs.
    """
    validated = _validate_inputs(env, premises, conclusion)
    branch = _initial_branch(env, validated, conclusion)
    offset = len(validated) - len(premises)
    goal = len(validated)
    search = Search(max_nodes, parameters)
    search.first_active = offset if active_premises else goal
    prefix = []
    for index, constant in instantiate:
        at, token = offset + index, "c:" + constant
        (branch, _), = Search._expand(branch, at, token)
        prefix.append((at, token))
    trace = (search.refute(branch, goal) if search.refutable(branch, goal)
             else search.search(branch))
    for at, token in reversed(prefix):
        trace = Search._node(at, [trace], token)
    certificate = {**_binding(env, validated, conclusion), "trace": trace}
    result = (replay(certificate) if replay is not None else
              check_entailment_certificate(env, premises, conclusion, certificate, max_steps=1_000_000))
    if not result.valid:
        raise Failed("trace did not replay: " + result.status)
    return certificate, search.nodes
