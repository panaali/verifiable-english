"""order@0 certificates: a signed tableau with a Farkas closing rule.

The replayer here mirrors ``VE.Order.Tableau.checkCertificate`` in Lean, whose
soundness is proved over every admissible structure with standard unbounded
integers. Proof search (``prove``) is an untrusted convenience: every
certificate it emits is replayed before it is returned, and failure to find a
certificate is inconclusive, never a refutation.

Certificate trace nodes (checker ``ve-order-farkas-checker@1``):

* ``{"rule": "close"}``: complementary formulas, or complementary predicate
  atoms whose arguments are equal by an identical resolved token, an identical
  linear term, or a certified ``t <= u`` and ``u <= t`` already on the branch
  (never by normalising terms); also a negated equality of equal arguments.
* ``{"rule": "expand", "at": i, "children": [...], "parameter"?: token}``:
  ordinary propositional and user-sort quantifier rules (as in v0).
* ``{"rule": "order-split@1", "formula": <le/lt AST>, "children": [pos, neg]}``:
  a cut on a linear comparison, e.g. ``c <= k`` or ``c >= k + 1``.
* ``{"rule": "order-neq@1", "at": i, "children": [lt, gt]}``: a negated integer
  equality ``t != u`` splits into ``t < u`` or ``u < t``.
* ``{"rule": "order-farkas@1", "cuts": [...], "literals": [[i, "k"], ...],
  "final_cuts": [[j, "k"], ...]}``: branch literals read as ``0 <= p``
  (``t < u`` as ``t + 1 <= u``; equalities as ``0 = p`` and may take negative
  multipliers), combined with nonnegative integer multipliers, plus earlier
  Chvatal-Gomory cuts (a combination whose collected coefficients are all
  divisible by ``divisor`` > 0, divided and rounded down). The final sum must
  have all coefficients zero and a negative constant: ``0 <= -k``, ``k > 0``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import math
import re
from typing import Any, Sequence

from . import ast
from .ast import (INT_SORT, Add, And, Binary, Bottom, Const, Eq, Exists, Forall, Implies,
                  Le, Lt, Not, Num, Or, Scale, Top, Unary, Var, _Decoder, _to_data,
                  decimal_from_wire, decimal_to_wire)
from .errors import ResourceLimit, VEError
from .limits import MAX_TABLEAU_DEPTH

CHECKER_VERSION = "ve-order-farkas-checker@1"
REPLAY_FUEL = 125
_WITNESS = re.compile(r"w:(0|[1-9][0-9]*)\Z")


class InvalidTrace(Exception):
    pass


class Budget(Exception):
    pass


# ----------------------------------------------------------------- branches

@dataclass(frozen=True, slots=True)
class Signed:
    formula: Any
    positive: bool
    bindings: tuple[str, ...] = ()


@dataclass
class Branch:
    formulas: list[Signed]
    witnesses: list[str] = field(default_factory=list)
    expanded: set[int] = field(default_factory=set)
    instantiated: set[tuple[int, str]] = field(default_factory=set)

    def copy(self) -> "Branch":
        return Branch(list(self.formulas), list(self.witnesses), set(self.expanded),
                      set(self.instantiated))

    def add(self, items) -> "Branch":
        result = self.copy()
        result.formulas.extend(items)
        return result


def parse_token(text) -> str | None:
    if type(text) is not str:
        return None
    if text.startswith("c:"):
        return text
    if text.startswith("w:"):
        return text if _WITNESS.match(text) else None
    return None


def token_sort(env, branch: Branch, token: str):
    if token.startswith("c:"):
        declaration = env.constants.get(token[2:])
        return None if declaration is None else declaration.sort
    index = int(token[2:])
    return branch.witnesses[index] if index < len(branch.witnesses) else None


def _scoped(branch: Branch) -> bool:
    n = len(branch.witnesses)
    return all(not t.startswith("w:") or int(t[2:]) < n
               for a in branch.formulas for t in a.bindings)


def _known(env, branch: Branch) -> bool:
    return all(token_sort(env, branch, t) is not None for a in branch.formulas for t in a.bindings)


def _rule(item: Signed):
    f, p = item.formula, item.positive
    mk = lambda g, q: Signed(g, q, item.bindings)
    kind = type(f)
    if kind is Not:
        return ("one", [mk(f.body, not p)])
    if kind is And:
        return ("one", [mk(f.left, True), mk(f.right, True)]) if p else ("two", mk(f.left, False), mk(f.right, False))
    if kind is Or:
        return ("two", mk(f.left, True), mk(f.right, True)) if p else ("one", [mk(f.left, False), mk(f.right, False)])
    if kind is Implies:
        return ("two", mk(f.left, False), mk(f.right, True)) if p else ("one", [mk(f.left, True), mk(f.right, False)])
    if (kind is Forall and p) or (kind is Exists and not p):
        return ("gamma", f.sort, f.body)
    if kind in (Forall, Exists):
        return ("delta", f.sort, f.body)
    return ("literal",)


def next_branches(env, branch: Branch, index, parameter) -> list[Branch] | None:
    """Mirror of Lean ``next``: None rejects."""
    if type(index) is not int or isinstance(index, bool) or not 0 <= index < len(branch.formulas):
        return None
    item = branch.formulas[index]
    rule = _rule(item)
    if rule[0] == "literal":
        return None
    if rule[0] == "gamma":
        token = parse_token(parameter) if parameter is not None else None
        # Lean compares against SortName.user: a binder named $int never matches.
        if (token is None or rule[1] == INT_SORT or token_sort(env, branch, token) != rule[1]
                or (index, token) in branch.instantiated):
            return None
        child = branch.add([Signed(rule[2], item.positive, (token,) + item.bindings)])
        child.instantiated.add((index, token))
        return [child]
    if parameter is not None or index in branch.expanded:
        return None
    base = branch.copy()
    base.expanded.add(index)
    if rule[0] == "one":
        return [base.add(rule[1])]
    if rule[0] == "two":
        return [base.add([rule[1]]), base.add([rule[2]])]
    token = f"w:{len(branch.witnesses)}"
    base.witnesses.append(rule[1])
    return [base.add([Signed(rule[2], item.positive, (token,) + item.bindings)])]


# ------------------------------------------------------------ linear forms
# A form is (constant, coefficients): coefficients is a list of (name, k)
# pairs in Lean's order; only order-independent properties are ever checked.

def linearize(env, term):
    kind = type(term)
    if kind is Var:
        return None
    if kind is Const:
        declaration = env.constants.get(term.name)
        if declaration is None or declaration.sort != INT_SORT:
            return None
        return (0, [(term.name, 1)])
    if kind is Num:
        return (term.value, [])
    if kind is Add:
        a, b = linearize(env, term.left), linearize(env, term.right)
        return None if a is None or b is None else _add(a, b)
    if kind is Scale:
        a = linearize(env, term.term)
        return None if a is None else _smul(term.coefficient, a)
    return None


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _smul(k, a):
    return (k * a[0], [(n, k * m) for n, m in a[1]])


def _sub(a, b):
    return _add(a, _smul(-1, b))


def _shift(a, z):
    return (a[0] + z, a[1])


def _collect(form):
    totals: dict[str, int] = {}
    for name, k in form[1]:
        totals[name] = totals.get(name, 0) + k
    return form[0], totals


def constraint(env, item: Signed):
    f, p = item.formula, item.positive
    if type(f) not in (Le, Lt, Eq):
        return None
    x, y = linearize(env, f.left), linearize(env, f.right)
    if x is None or y is None:
        return None
    if type(f) is Le:
        return (_sub(y, x), False) if p else (_shift(_sub(x, y), -1), False)
    if type(f) is Lt:
        return (_shift(_sub(y, x), -1), False) if p else (_sub(x, y), False)
    return (_sub(y, x), True) if p else None


def _combo(env, branch: Branch, derived, literals, cuts):
    total = (0, [])
    for index, k in literals:
        if not 0 <= index < len(branch.formulas):
            return None
        c = constraint(env, branch.formulas[index])
        if c is None or not (c[1] or k >= 0):
            return None
        total = _add(total, _smul(k, c[0]))
    for index, k in cuts:
        if not 0 <= index < len(derived) or k < 0:
            return None
        total = _add(total, _smul(k, derived[index]))
    return total


def farkas_closes(env, branch: Branch, node) -> bool:
    derived = []
    for cut in node["cuts"]:
        form = _combo(env, branch, derived, cut["literals"], cut["cuts"])
        if form is None:
            return False
        constant, totals = _collect(form)
        g = cut["divisor"]
        if not (g > 0 and all(k % g == 0 for k in totals.values())):
            return False
        derived.append((constant // g, [(n, k // g) for n, k in totals.items()]))
    form = _combo(env, branch, derived, node["literals"], node["final_cuts"])
    if form is None:
        return False
    constant, totals = _collect(form)
    return all(k == 0 for k in totals.values()) and constant < 0


# ------------------------------------------------------------------ closing

def _term_token(bindings, term):
    if type(term) is Const:
        return "c:" + term.name
    if type(term) is Var:
        return bindings[term.index] if 0 <= term.index < len(bindings) else None
    return None


def closed_term(term) -> bool:
    kind = type(term)
    if kind in (Const, Num):
        return True
    if kind is Add:
        return closed_term(term.left) and closed_term(term.right)
    if kind is Scale:
        return closed_term(term.term)
    return False


def _has_le(branch: Branch, t, u) -> bool:
    target = Le(t, u)
    return any(a.positive and a.formula == target for a in branch.formulas)


def _object_eq(branch: Branch, x, y) -> bool:
    for a in branch.formulas:
        if a.positive and type(a.formula) is Eq:
            x2, y2 = _term_token(a.bindings, a.formula.left), _term_token(a.bindings, a.formula.right)
            if x2 is not None and y2 is not None and ((x2 == x and y2 == y) or (x2 == y and y2 == x)):
                return True
    return False


def same_value(env, branch: Branch, bs, t, cs, u) -> bool:
    x, y = _term_token(bs, t), _term_token(cs, u)
    if x is not None and y is not None:
        if (token_sort(env, branch, x) is not None and x == y) or _object_eq(branch, x, y):
            return True
    if t == u and linearize(env, t) is not None:
        return True
    return closed_term(t) and closed_term(u) and _has_le(branch, t, u) and _has_le(branch, u, t)


def _self_closed(env, branch: Branch, a: Signed) -> bool:
    f = a.formula
    if type(f) is Bottom and a.positive:
        return True
    if type(f) is Top and not a.positive:
        return True
    return type(f) is Eq and not a.positive and same_value(env, branch, a.bindings, f.left, a.bindings, f.right)


def _complementary(env, branch: Branch, p: Signed, n: Signed) -> bool:
    if not p.positive or n.positive:
        return False
    if p.formula == n.formula and p.bindings == n.bindings:
        return True
    f, g = p.formula, n.formula
    if type(f) is Unary and type(g) is Unary:
        return f.predicate == g.predicate and same_value(env, branch, p.bindings, f.term, n.bindings, g.term)
    if type(f) is Binary and type(g) is Binary:
        return (f.predicate == g.predicate
                and same_value(env, branch, p.bindings, f.left, n.bindings, g.left)
                and same_value(env, branch, p.bindings, f.right, n.bindings, g.right))
    return False


def closed(env, branch: Branch) -> bool:
    return (any(_self_closed(env, branch, a) for a in branch.formulas)
            or any(_complementary(env, branch, p, n) for p in branch.formulas for n in branch.formulas))


def split_atom(env, formula) -> bool:
    return (type(formula) in (Le, Lt) and linearize(env, formula.left) is not None
            and linearize(env, formula.right) is not None)


def neq_split(env, branch: Branch, index):
    if type(index) is not int or isinstance(index, bool) or not 0 <= index < len(branch.formulas):
        return None
    a = branch.formulas[index]
    f = a.formula
    if type(f) is not Eq or a.positive:
        return None
    if linearize(env, f.left) is None or linearize(env, f.right) is None:
        return None
    return [branch.add([Signed(Lt(f.left, f.right), True, a.bindings)]),
            branch.add([Signed(Lt(f.right, f.left), True, a.bindings)])]


# --------------------------------------------------------------- the trace

def _nat(value):
    if type(value) is not int or isinstance(value, bool) or value < 0:
        raise InvalidTrace("expected a natural number")
    return value


def _fields(node, required, optional=()):
    if type(node) is not dict:
        raise InvalidTrace("trace node must be an object")
    keys = set(node)
    if not set(required) <= keys or not keys <= set(required) | set(optional):
        raise InvalidTrace("trace node fields do not match")


def _pairs(value):
    if type(value) is not list:
        raise InvalidTrace("multipliers must be an array")
    result = []
    for item in value:
        if type(item) is not list or len(item) != 2 or type(item[1]) is not str:
            raise InvalidTrace("invalid multiplier pair")
        result.append((_nat(item[0]), _integer(item[1])))
    return result


def _integer(text):
    try:
        return decimal_from_wire(text)
    except VEError as exc:
        raise InvalidTrace(str(exc)) from exc


def decode_trace(node, fuel=REPLAY_FUEL):
    """Decode the whole trace first, as the Lean wire adapter does."""
    if fuel == 0:
        raise InvalidTrace("certificate expansion depth exceeds 124")
    if type(node) is not dict or type(node.get("rule")) is not str:
        raise InvalidTrace("trace node must be an object with a rule")
    rule = node["rule"]

    def children():
        if type(node["children"]) is not list:
            raise InvalidTrace("children must be an array")
        return [decode_trace(child, fuel - 1) for child in node["children"]]

    if rule == "close":
        _fields(node, ("rule",))
        return {"rule": "close"}
    if rule == "expand":
        _fields(node, ("rule", "at", "children"), ("parameter",))
        if "parameter" in node and type(node["parameter"]) is not str:
            raise InvalidTrace("parameter must be a string")
        return {"rule": "expand", "at": _nat(node["at"]), "parameter": node.get("parameter"),
                "children": children()}
    if rule == "order-split@1":
        _fields(node, ("rule", "formula", "children"))
        try:
            formula = _Decoder().decode(node["formula"])
        except (VEError, RecursionError) as exc:
            raise InvalidTrace(f"invalid split formula: {exc}") from exc
        return {"rule": rule, "formula": formula, "children": children()}
    if rule == "order-neq@1":
        _fields(node, ("rule", "at", "children"))
        return {"rule": rule, "at": _nat(node["at"]), "children": children()}
    if rule == "order-farkas@1":
        _fields(node, ("rule", "cuts", "literals", "final_cuts"))
        if type(node["cuts"]) is not list:
            raise InvalidTrace("cuts must be an array")
        cuts = []
        for cut in node["cuts"]:
            _fields(cut, ("literals", "cuts", "divisor"))
            if type(cut["divisor"]) is not str:
                raise InvalidTrace("divisor must be a decimal string")
            cuts.append({"literals": _pairs(cut["literals"]), "cuts": _pairs(cut["cuts"]),
                         "divisor": _integer(cut["divisor"])})
        return {"rule": rule, "cuts": cuts, "literals": _pairs(node["literals"]),
                "final_cuts": _pairs(node["final_cuts"])}
    raise InvalidTrace("unknown tableau rule")


class _Replayer:
    def __init__(self, env, maximum):
        self.env, self.maximum, self.steps = env, maximum, 0

    def children(self, branches, nodes, fuel):
        if len(branches) != len(nodes):
            return False
        return all(self.replay(b, n, fuel) for b, n in zip(branches, nodes))

    def replay(self, branch: Branch, node, fuel=REPLAY_FUEL) -> bool:
        if fuel == 0:
            return False
        self.steps += 1
        if self.steps > self.maximum:
            raise Budget
        if not (_scoped(branch) and _known(self.env, branch)):
            return False
        rule = node["rule"]
        if rule == "close":
            return closed(self.env, branch)
        if rule == "order-farkas@1":
            return farkas_closes(self.env, branch, node)
        if rule == "expand":
            branches = next_branches(self.env, branch, node["at"], node["parameter"])
            return branches is not None and self.children(branches, node["children"], fuel - 1)
        if rule == "order-split@1":
            f = node["formula"]
            if not split_atom(self.env, f):
                return False
            return self.children([branch.add([Signed(f, True)]), branch.add([Signed(f, False)])],
                                 node["children"], fuel - 1)
        branches = neq_split(self.env, branch, node["at"])
        return branches is not None and self.children(branches, node["children"], fuel - 1)


def initial(premises, conclusion) -> Branch:
    return Branch([Signed(f, True) for f in premises] + [Signed(conclusion, False)])


def replay_trace(env, premises, conclusion, trace, max_steps) -> tuple[bool, int]:
    decoded = decode_trace(trace)
    replayer = _Replayer(env, max_steps)
    return replayer.replay(initial(premises, conclusion), decoded), replayer.steps


# ------------------------------------------------------------ proof search
# Everything below is untrusted: its output is replayed before it is used.

def _constraints(env, branch: Branch):
    rows = []
    for index, item in enumerate(branch.formulas):
        c = constraint(env, item)
        if c is None:
            continue
        constant, totals = _collect(c[0])
        rows.append((index, constant, totals, c[1]))
    return rows


def _gcd_all(values):
    g = 0
    for v in values:
        g = math.gcd(g, v)
    return g


class _Row:
    """A derived constraint 0 <= constant + sum coeffs, with its provenance."""
    __slots__ = ("constant", "coeffs", "literals", "cuts")

    def __init__(self, constant, coeffs, literals, cuts):
        self.constant, self.coeffs = constant, {k: v for k, v in coeffs.items() if v}
        self.literals, self.cuts = literals, cuts


def _merge(a: dict, ka: int, b: dict, kb: int) -> dict:
    result = {k: v * ka for k, v in a.items()}
    for k, v in b.items():
        result[k] = result.get(k, 0) + v * kb
    return {k: v for k, v in result.items() if v}


def _combine(a: _Row, ka: int, b: _Row, kb: int) -> _Row:
    return _Row(a.constant * ka + b.constant * kb, _merge(a.coeffs, ka, b.coeffs, kb),
                _merge(a.literals, ka, b.literals, kb), _merge(a.cuts, ka, b.cuts, kb))


def _fourier_motzkin(rows: list[_Row], limit=4000):
    """Return a row with no coefficients and negative constant, or (None, stages)."""
    stages = [rows]
    current = rows
    while True:
        for row in current:
            if not row.coeffs and row.constant < 0:
                return row, stages
        names = sorted({n for r in current for n in r.coeffs})
        if not names:
            return None, stages
        # Eliminate the variable producing the fewest new rows.
        def cost(n):
            pos = sum(1 for r in current if r.coeffs.get(n, 0) > 0)
            neg = sum(1 for r in current if r.coeffs.get(n, 0) < 0)
            return pos * neg - pos - neg
        name = min(names, key=cost)
        keep = [r for r in current if name not in r.coeffs]
        pos = [r for r in current if r.coeffs.get(name, 0) > 0]
        neg = [r for r in current if r.coeffs.get(name, 0) < 0]
        if len(keep) + len(pos) * len(neg) > limit:
            raise Budget
        seen = set()
        new = []
        for p in pos:
            for q in neg:
                a, b = p.coeffs[name], -q.coeffs[name]
                g = math.gcd(a, b)
                row = _combine(p, b // g, q, a // g)
                key = (row.constant, tuple(sorted(row.coeffs.items())))
                if key not in seen:
                    seen.add(key)
                    new.append(row)
        current = keep + new
        stages.append(current)


def _rational_point(stages):
    """Back-substitute a rational point satisfying the first stage's rows."""
    values: dict[str, Fraction] = {}
    for stage in reversed(stages):
        names = sorted({n for r in stage for n in r.coeffs} - set(values))
        for name in names:
            lo, hi = None, None
            for r in stage:
                k = r.coeffs.get(name, 0)
                if not k or any(n not in values and n != name for n in r.coeffs):
                    continue
                rest = r.constant + sum(Fraction(v) * values[n] for n, v in r.coeffs.items() if n != name)
                bound = Fraction(-rest, k)
                if k > 0:
                    lo = bound if lo is None else max(lo, bound)
                else:
                    hi = bound if hi is None else min(hi, bound)
            if lo is not None and hi is not None:
                ceil_lo = math.ceil(lo)
                value = Fraction(ceil_lo) if ceil_lo <= hi else lo
            elif lo is not None:
                value = Fraction(math.ceil(lo))
            elif hi is not None:
                value = Fraction(math.floor(hi))
            else:
                value = Fraction(0)
            values[name] = value
    return values


class _Search:
    def __init__(self, env, max_steps):
        self.env, self.max_steps, self.steps = env, max_steps, 0

    def tick(self):
        self.steps += 1
        if self.steps > self.max_steps:
            raise Budget

    def farkas(self, branch: Branch):
        rows = []
        for index, constant, totals, equality in _constraints(self.env, branch):
            rows.append(_Row(constant, totals, {index: 1}, {}))
            if equality:
                rows.append(_Row(-constant, {n: -k for n, k in totals.items()}, {index: -1}, {}))
        if not rows:
            return None, None
        # Chvatal-Gomory tightening of every input row with a nontrivial gcd.
        cuts = []
        tightened = []
        for row in rows:
            g = _gcd_all(row.coeffs.values())
            if g > 1 and row.constant % g:
                cuts.append({"literals": sorted(row.literals.items()), "cuts": [], "divisor": g})
                tightened.append(_Row(row.constant // g, {n: k // g for n, k in row.coeffs.items()},
                                      {}, {len(cuts) - 1: 1}))
            else:
                tightened.append(row)
        found, stages = _fourier_motzkin(tightened)
        if found is not None:
            used = sorted(found.cuts)
            renumber = {old: new for new, old in enumerate(used)}
            node = {"rule": "order-farkas@1",
                    "cuts": [_cut_wire(cuts[i]) for i in used],
                    "literals": [[i, str(k)] for i, k in sorted(found.literals.items())],
                    "final_cuts": [[renumber[i], str(k)] for i, k in sorted(found.cuts.items())]}
            return node, None
        return None, stages

    def prove(self, branch: Branch, depth=0):
        self.tick()
        if depth >= MAX_TABLEAU_DEPTH - 1:
            return None
        if closed(self.env, branch):
            return {"rule": "close"}
        node, stages = self.farkas(branch)
        if node is not None:
            return node
        for step in self.candidates(branch, stages):
            kind = step[0]
            if kind == "split":
                formula = step[1]
                children = [branch.add([Signed(formula, True)]), branch.add([Signed(formula, False)])]
                result = {"rule": "order-split@1", "formula": _to_data(formula)}
            elif kind == "neq":
                children = neq_split(self.env, branch, step[1])
                result = {"rule": "order-neq@1", "at": step[1]}
            else:
                children = next_branches(self.env, branch, step[1], step[2])
                result = {"rule": "expand", "at": step[1]}
                if step[2] is not None:
                    result["parameter"] = step[2]
            traces = []
            for child in children:
                trace = self.prove(child, depth + 1)
                if trace is None:
                    return None
                traces.append(trace)
            result["children"] = traces
            return result
        return None

    def candidates(self, branch: Branch, stages):
        env = self.env
        present = {(a.formula, a.positive, a.bindings) for a in branch.formulas}
        order = {"one": 0, "delta": 2, "two": 3}
        pending = []
        for index, item in enumerate(branch.formulas):
            rule = _rule(item)
            if rule[0] in order and index not in branch.expanded:
                pending.append((order[rule[0]], index, None))
        for index, item in enumerate(branch.formulas):
            f = item.formula
            if (type(f) is Eq and not item.positive and linearize(env, f.left) is not None
                    and linearize(env, f.right) is not None
                    and (Lt(f.left, f.right), True, item.bindings) not in present
                    and (Lt(f.right, f.left), True, item.bindings) not in present):
                pending.append((1, index, "neq"))
        pending.sort(key=lambda x: (x[0], x[1]))
        for rank, index, tag in pending:
            if rank >= 2:
                break
            yield ("neq", index) if tag == "neq" else ("expand", index, None)
        # Certified argument equalities for complementary predicate atoms.
        for p in branch.formulas:
            for n in branch.formulas:
                if not p.positive or n.positive or type(p.formula) is not type(n.formula):
                    continue
                if type(p.formula) not in (Unary, Binary) or p.formula.predicate != n.formula.predicate:
                    continue
                pairs = ([(p.formula.term, n.formula.term)] if type(p.formula) is Unary else
                         [(p.formula.left, n.formula.left), (p.formula.right, n.formula.right)])
                if not all(same_value(env, branch, p.bindings, t, n.bindings, u)
                           or (closed_term(t) and closed_term(u) and _linear_equal(env, t, u))
                           for t, u in pairs):
                    continue
                for t, u in pairs:
                    if same_value(env, branch, p.bindings, t, n.bindings, u):
                        continue
                    for a, b in ((t, u), (u, t)):
                        if (Le(a, b), True, ()) not in present and (Le(a, b), False, ()) not in present:
                            yield ("split", Le(a, b))
                            return
        for rank, index, tag in pending:
            if rank >= 2:
                yield ("expand", index, None)
        # Universal instantiation with every available parameter of the sort.
        tokens = [("c:" + name, d.sort) for name, d in sorted(env.constants.items())]
        tokens += [(f"w:{i}", s) for i, s in enumerate(branch.witnesses)]
        for index, item in enumerate(branch.formulas):
            rule = _rule(item)
            if rule[0] != "gamma":
                continue
            for token, sort in tokens:
                if sort == rule[1] and (index, token) not in branch.instantiated:
                    added = Signed(rule[2], item.positive, (token,) + item.bindings)
                    if (added.formula, added.positive, added.bindings) not in present:
                        yield ("expand", index, token)
                        return
        # Integer branch and bound on a fractional coordinate.
        if stages is not None:
            point = _rational_point(stages)
            for name, value in sorted(point.items()):
                if value.denominator != 1:
                    yield ("split", Le(Const(name), Num(math.floor(value))))
                    return


def _linear_equal(env, t, u):
    a, b = linearize(env, t), linearize(env, u)
    if a is None or b is None:
        return False
    ca, ta = _collect(a)
    cb, tb = _collect(b)
    return ca == cb and {k: v for k, v in ta.items() if v} == {k: v for k, v in tb.items() if v}


def _cut_wire(cut):
    return {"literals": [[i, str(k)] for i, k in cut["literals"]],
            "cuts": [[i, str(k)] for i, k in cut["cuts"]], "divisor": str(cut["divisor"])}


def search(env, premises, conclusion, max_steps) -> tuple[dict | None, int]:
    searcher = _Search(env, max_steps)
    try:
        trace = searcher.prove(initial(premises, conclusion))
    except (Budget, RecursionError):
        return None, searcher.steps
    return trace, searcher.steps
