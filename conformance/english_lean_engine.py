"""Executable reference of the English-in-Lean grammar engine (item 1, tier A, and the English matching).

This is test code, written from `docs/spec/english-lean.md` sections 2.4 to 2.8, 5.2 to 5.7 and the
matching of 5.8. It is no part of any admission path and it decides nothing for a user. It exists for
three reasons:

1. to run the hand-derived expectations of the engine corpus (spec 8.1 to 8.3 and 8.7,
   `conformance/english-lean/engine.json`) before any Lean is written (statement review checklist,
   item 15);
2. to be the oracle that the Lean prototype of S1a is compared with: same grammars, same inputs, same
   verdicts and the same tree sets below the cap;
3. to measure the step counter of 2.6 on Python's side while S1a measures it in Lean.

The parser is the algorithm of 2.6: rows from the last position to the first, nonterminals in
increasing rank within a row, then the rule-suffix entries of the row; every entry and suffix entry
keeps at most `cap` members (the cap invariant); a final pass re-checks every returned tree with
`derives` and removes duplicates. A step is one rule attempt at a position (failed or not), one suffix
attempt at a position, or one combination of an entry member with a suffix member. When the steps of a
sentence exceed the budget, the result is `None`, never a shorter list.

A second, independent relation (`derives_brute`) and an exhaustive enumerator (`enumerate_all`) are the
brute-force side of fixture g18. They share no code with the table.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable


# ---------------------------------------------------------------- symbols, rules, grammars (5.2)

@dataclass(frozen=True)
class T:
    """A terminal symbol."""
    a: Any


@dataclass(frozen=True)
class N:
    """A nonterminal symbol: a number below `len(rank)`."""
    A: int


@dataclass(frozen=True)
class Rule:
    lhs: int
    rhs: tuple
    act: int = 0
    tag: str = ''


@dataclass(frozen=True)
class Grammar:
    rules: tuple
    start: int
    rank: tuple


def rule_wf(G: Grammar, R: Rule) -> bool:
    """W1 to W3 for one rule, exactly as `Rule.wf` of 5.2."""
    size = len(G.rank)
    if not R.lhs < size or not R.rhs:
        return False
    if not all(isinstance(X, T) or X.A < size for X in R.rhs):
        return False
    first = R.rhs[0]
    return not isinstance(first, N) or G.rank[first.A] < G.rank[R.lhs]


def grammar_wf(G: Grammar) -> bool:
    return G.start < len(G.rank) and all(rule_wf(G, R) for R in G.rules)


# ---------------------------------------------------------------- trees and derivations (5.3)

@dataclass(frozen=True)
class Leaf:
    tok: Any


@dataclass(frozen=True)
class Node:
    rule: int
    kids: tuple


def tree_yield(t) -> list:
    out = []
    stack = [t]
    while stack:
        u = stack.pop()
        if isinstance(u, Leaf):
            out.append(u.tok)
        else:
            stack.extend(reversed(u.kids))
    return out


def derives(G: Grammar, accepts: Callable, X, t) -> bool:
    """`Tree.derives` of 5.3."""
    if isinstance(X, T):
        return isinstance(t, Leaf) and bool(accepts(X.a, t.tok))
    if not isinstance(t, Node) or not 0 <= t.rule < len(G.rules):
        return False
    R = G.rules[t.rule]
    return (R.lhs == X.A and len(R.rhs) == len(t.kids)
            and all(derives(G, accepts, Y, u) for Y, u in zip(R.rhs, t.kids)))


def is_derivation(G: Grammar, accepts: Callable, w: list, t) -> bool:
    """`Derives G (.n G.start) w t`."""
    return derives(G, accepts, N(G.start), t) and tree_yield(t) == list(w)


# ---------------------------------------------------------------- the parser (2.6, 5.4)

class BudgetExceeded(Exception):
    pass


@dataclass
class ParseStats:
    steps: int = 0
    entries: int = 0          # stored entry members (trees)
    suffix_members: int = 0   # stored suffix-entry members (lists of trees)


def _add(bucket: dict, j: int, item, cap: int) -> None:
    members = bucket.setdefault(j, [])
    if len(members) < cap and item not in members:
        members.append(item)


def parse(G: Grammar, accepts: Callable, cap: int, budget: int | None, w: list,
          stats: ParseStats | None = None):
    """Up to `cap` derivations of the start symbol over `w`; `None` when the step budget is exceeded.

    `budget=None` means no limit (used by measurement only)."""
    stats = stats if stats is not None else ParseStats()
    n = len(w)
    size = len(G.rank)
    order = sorted(range(size), key=lambda A: (G.rank[A], A))
    by_lhs: dict[int, list[int]] = {}
    for r, R in enumerate(G.rules):
        by_lhs.setdefault(R.lhs, []).append(r)
    # entry[i][A] : {j: [tree]}; suffix[p][(r, d)] : {j: [tuple of trees]} for d >= 1.
    entry: list[dict] = [dict() for _ in range(n + 1)]
    suffix: list[dict] = [dict() for _ in range(n + 1)]

    def step(k: int = 1) -> None:
        stats.steps += k
        if budget is not None and stats.steps > budget:
            raise BudgetExceeded

    def first(X, i: int) -> dict:
        """The members of symbol `X` starting at `i`, by end position."""
        if isinstance(X, T):
            return {i + 1: [Leaf(w[i])]} if i < n and accepts(X.a, w[i]) else {}
        if not X.A < size:
            return {}
        return entry[i].get(X.A, {})

    try:
        for i in range(n - 1, -1, -1):
            for A in order:
                bucket: dict = {}
                for r in by_lhs.get(A, ()):
                    R = G.rules[r]
                    step()                       # one rule attempt at position i
                    if not R.rhs:
                        continue
                    heads = first(R.rhs[0], i)
                    if len(R.rhs) == 1:
                        for j, ts in heads.items():
                            for t in ts:
                                step()
                                _add(bucket, j, Node(r, (t,)), cap)
                        continue
                    for k, ts in heads.items():
                        rests = suffix[k].get((r, 1), {}) if k <= n else {}
                        for j, tails in rests.items():
                            for t in ts:
                                for tail in tails:
                                    step()      # one combination
                                    _add(bucket, j, Node(r, (t,) + tail), cap)
                if bucket:
                    entry[i][A] = bucket
                    stats.entries += sum(len(v) for v in bucket.values())
            # suffix entries of row i, from the last position of each rule to the second
            for r, R in enumerate(G.rules):
                for d in range(len(R.rhs) - 1, 0, -1):
                    step()                       # one suffix attempt at position i
                    heads = first(R.rhs[d], i)
                    bucket = {}
                    if d == len(R.rhs) - 1:
                        for j, ts in heads.items():
                            for t in ts:
                                step()
                                _add(bucket, j, (t,), cap)
                    else:
                        for k, ts in heads.items():
                            rests = suffix[k].get((r, d + 1), {}) if k <= n else {}
                            for j, tails in rests.items():
                                for t in ts:
                                    for tail in tails:
                                        step()
                                        _add(bucket, j, (t,) + tail, cap)
                    if bucket:
                        suffix[i][(r, d)] = bucket
                        stats.suffix_members += sum(len(v) for v in bucket.values())
    except BudgetExceeded:
        return None
    found = entry[0].get(G.start, {}).get(n, []) if n and G.start < size else []
    # The last pass: re-check every tree, remove duplicates.
    out = []
    for t in found:
        if is_derivation(G, accepts, w, t) and t not in out:
            out.append(t)
    return out[:cap]


def verdict(G: Grammar, accepts: Callable, budget: int | None, w: list):
    """`('zero',)`, `('one', t)`, `('many', t, u)` or `None` (budget)."""
    ts = parse(G, accepts, 2, budget, w)
    if ts is None:
        return None
    if not ts:
        return ('zero',)
    if len(ts) == 1:
        return ('one', ts[0])
    return ('many', ts[0], ts[1])


# ---------------------------------------------------------------- the brute-force side (g18)

def derives_brute(G: Grammar, accepts: Callable, X, t) -> bool:
    """A second implementation of the relation, written from 2.5 with an explicit stack."""
    stack = [(X, t)]
    while stack:
        Y, u = stack.pop()
        if isinstance(Y, T):
            if not isinstance(u, Leaf) or not accepts(Y.a, u.tok):
                return False
            continue
        if isinstance(u, Leaf) or u.rule < 0 or u.rule >= len(G.rules):
            return False
        R = G.rules[u.rule]
        if R.lhs != Y.A or len(R.rhs) != len(u.kids):
            return False
        stack.extend(zip(R.rhs, u.kids))
    return True


def enumerate_all(G: Grammar, accepts: Callable, w: list, limit: int = 100_000) -> list:
    """Every derivation of the start symbol over `w`, for a well-formed grammar, by span splitting.

    Each candidate is checked with `derives_brute`. Raises when more than `limit` trees exist."""
    assert grammar_wf(G)
    memo: dict = {}

    def trees(X, i: int, j: int) -> list:
        key = (X, i, j)
        if key in memo:
            return memo[key]
        memo[key] = []
        out = []
        if isinstance(X, T):
            if j == i + 1 and accepts(X.a, w[i]):
                out.append(Leaf(w[i]))
        else:
            for r, R in enumerate(G.rules):
                if R.lhs == X.A:
                    for kids in seqs(R.rhs, i, j):
                        out.append(Node(r, kids))
                        if len(out) > limit:
                            raise OverflowError('too many derivations')
        memo[key] = out
        return out

    def seqs(rhs: tuple, i: int, j: int) -> Iterable[tuple]:
        if not rhs:
            if i == j:
                yield ()
            return
        # every symbol covers at least one token in a well-formed grammar
        for k in range(i + 1, j - len(rhs) + 2):
            for t in trees(rhs[0], i, k):
                for rest in seqs(rhs[1:], k, j):
                    yield (t,) + rest

    if not w:
        return []
    result = trees(N(G.start), 0, len(w))
    assert all(derives_brute(G, accepts, N(G.start), t) and tree_yield(t) == list(w) for t in result)
    return result


# ---------------------------------------------------------------- meanings (2.7, 5.5)

@dataclass(frozen=True)
class Action:
    args: tuple
    out: str
    run: Callable = field(compare=False)


@dataclass(frozen=True)
class Sig:
    tok: str = 'tok'


def sym_ty(sig: Sig, ty: Callable, X) -> str:
    return sig.tok if isinstance(X, T) else ty(X.A)


def grammar_typed(G: Grammar, sig: Sig, ty: Callable, acts: list) -> bool:
    for R in G.rules:
        if not 0 <= R.act < len(acts):
            return False
        a = acts[R.act]
        if tuple(a.args) != tuple(sym_ty(sig, ty, X) for X in R.rhs) or a.out != ty(R.lhs):
            return False
    return True


def tree_sem(G: Grammar, sig: Sig, acts: list, t):
    """`Tree.sem`: a pair (type, value) or `None`."""
    if isinstance(t, Leaf):
        return (sig.tok, t.tok)
    if not 0 <= t.rule < len(G.rules):
        return None
    R = G.rules[t.rule]
    if not 0 <= R.act < len(acts):
        return None
    a = acts[R.act]
    vals = [tree_sem(G, sig, acts, u) for u in t.kids]
    if any(v is None for v in vals) or [v[0] for v in vals] != list(a.args):
        return None
    return (a.out, a.run(*[v[1] for v in vals]))


# ---------------------------------------------------------------- readings and documents (2.8, 5.6)

class Rejected(Exception):
    """A declared rejection from a meaning function."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


def read_sentence(G: Grammar, accepts: Callable, mu: Callable, st, budget, w: list):
    """`readSentence`: (outcome, state). `mu(st, t)` returns (A, c, st2) or raises `Rejected`."""
    v = verdict(G, accepts, budget, w)
    if v is None:
        return ('budget',), st
    if v[0] == 'zero':
        return ('noDerivation',), st
    if v[0] == 'many':
        return ('ambiguous', v[1], v[2]), st
    try:
        A, c, st2 = mu(st, v[1])
    except Rejected as r:
        return ('rejected', r.code), st
    return ('ok', A, c), st2


def read_document(G: Grammar, accepts: Callable, mu: Callable, st, budget, ws: list):
    rs = []
    for i, w in enumerate(ws):
        o, st2 = read_sentence(G, accepts, mu, st, budget, w)
        if o[0] != 'ok':
            return ('stopped', i, o), st
        rs.append((o[1], o[2]))
        st = st2
    return ('ok', rs), st


def reading_set(mu: Callable, st, ts: list) -> list:
    out = []
    for t in ts:
        try:
            out.append(mu(st, t))
        except Rejected:
            pass
    return out


# ---------------------------------------------------------------- extensions (2.11, 5.7)

@dataclass(frozen=True)
class RuleMap:
    rule: Callable
    nt: Callable


def rule_map_tree(e: RuleMap, t):
    if isinstance(t, Leaf):
        return t
    return Node(e.rule(t.rule), tuple(rule_map_tree(e, u) for u in t.kids))


def rule_map_ok(e: RuleMap, G: Grammar, G2: Grammar, acts: list, acts2: list) -> tuple[bool, str]:
    """`RuleMap.Ok`, with the name of the first failing clause."""
    if e.nt(G.start) != G2.start:
        return False, 'start'
    images = [e.rule(r) for r in range(len(G.rules))]
    if len(set(images)) != len(images):
        return False, 'injective'
    for r, R in enumerate(G.rules):
        r2 = e.rule(r)
        if not 0 <= r2 < len(G2.rules):
            return False, 'rules'
        R2 = G2.rules[r2]
        rhs = tuple(X if isinstance(X, T) else N(e.nt(X.A)) for X in R.rhs)
        if R2.lhs != e.nt(R.lhs) or R2.rhs != rhs:
            return False, 'rules'
        a = acts[R.act] if 0 <= R.act < len(acts) else None
        a2 = acts2[R2.act] if 0 <= R2.act < len(acts2) else None
        if a is not a2:
            return False, 'actions'
    return True, ''


# ---------------------------------------------------------------- the English matching (2.3, 5.8)
#
# Tokens: ('word', text, initial), ('quoted', name), ('label', letter, index), ('numeral', value),
# ('punct', text, glued_before, glued_after). Terminals: ('kw', s), ('content', s), ('exact', tok), ('cls', ('numeral',)),
# ('cls', ('label', letter)).

TERMINATOR = ('punct', '.')


def _ascii_alnum(c: str) -> bool:
    return c.isascii() and c.isalnum()


def fold_char(c: str) -> str:
    """`foldChar` of 5.8: ASCII letters to lower case; `İ`, `ı` to `i`; `ſ` to `s`; Kelvin sign to `k`."""
    if _ascii_alnum(c):
        return c.lower()
    if c in ('İ', 'ı'):
        return 'i'
    if c == 'ſ':
        return 's'
    if c == 'K':
        return 'k'
    return c


def fold(s: str) -> str:
    return ''.join(fold_char(c) for c in s)


def capitalise(s: str) -> str:
    """The first character in ASCII upper case (Lean's `Char.toUpper` is ASCII only)."""
    if not s:
        return s
    c = s[0]
    return (c.upper() if c.isascii() else c) + s[1:]


def tok_plain(tok: tuple) -> tuple:
    return ('word', tok[1], False) if tok[0] == 'word' else tok


def cls_accepts(c: tuple, tok: tuple) -> bool:
    if c[0] == 'numeral':
        return tok[0] == 'numeral'
    if c[0] == 'label':
        return tok[0] == 'label' and tok[1] == c[1]
    return False


def terminal_accepts(a: tuple, tok: tuple) -> bool:
    """`Terminal.accepts` of 5.8."""
    kind = a[0]
    if kind == 'kw':
        return tok[0] == 'word' and (tok[1] == a[1] or (tok[2] and tok[1] == capitalise(a[1])))
    if kind == 'content':
        return tok[0] == 'word' and fold(tok[1]) == fold(a[1])
    if kind == 'exact':
        return tok_plain(tok) == tok_plain(a[1])
    if kind == 'cls':
        return cls_accepts(a[1], tok)
    return False


def terminator_free(G: Grammar) -> bool:
    """W4: no terminal of any rule accepts the terminator."""
    return all(not (isinstance(X, T) and terminal_accepts(X.a, TERMINATOR))
               for R in G.rules for X in R.rhs)


# ---------------------------------------------------------------- the JSON form of the corpus

def terminal_from_json(x) -> tuple:
    """The rule-source notation of spec 2.10: a string is `kw`; `{"c"}` content; `{"p"}` punctuation;
    `{"q"}` a quoted identifier; `{"w"}` an exact word; `{"cls"}` a token class."""
    if isinstance(x, str):
        return ('kw', x)
    if 'c' in x:
        return ('content', x['c'])
    if 'p' in x:
        return ('exact', ('punct', x['p']))
    if 'q' in x:
        return ('exact', ('quoted', x['q']))
    if 'w' in x:
        return ('exact', ('word', x['w'], False))
    if 'cls' in x:
        c = x['cls']
        return ('cls', ('numeral',)) if c == 'numeral' else ('cls', ('label', c['label']))
    raise ValueError(f'unknown terminal {x!r}')


def token_from_json(x) -> tuple:
    """A string is a non-initial word; `{"w", "initial"}`, `{"q"}`, `{"label", "index"}`, `{"num"}`,
    `{"p"}` are the other forms."""
    if isinstance(x, str):
        return ('word', x, False)
    if 'w' in x:
        return ('word', x['w'], bool(x.get('initial', False)))
    if 'q' in x:
        return ('quoted', x['q'])
    if 'label' in x:
        return ('label', x['label'], x['index'])
    if 'num' in x:
        return ('numeral', x['num'])
    if 'p' in x:
        if 'glued_before' in x or 'glued_after' in x:
            return ('punct', x['p'], x.get('glued_before', False), x.get('glued_after', False))
        return ('punct', x['p'])
    raise ValueError(f'unknown token {x!r}')


def token_to_json(tok: tuple):
    kind = tok[0]
    if kind == 'word':
        return {'w': tok[1], 'initial': True} if tok[2] else tok[1]
    if kind == 'quoted':
        return {'q': tok[1]}
    if kind == 'label':
        return {'label': tok[1], 'index': tok[2]}
    if kind == 'numeral':
        return {'num': tok[1]}
    return ({'p': tok[1], 'glued_before': tok[2], 'glued_after': tok[3]}
            if len(tok) == 4 else {'p': tok[1]})


def grammar_from_json(g: dict) -> tuple[Grammar, list[str]]:
    """`{"nonterminals": [[name, rank], ...], "start": name, "rules": [{"tag", "lhs", "rhs"}]}`.

    A right-hand symbol `{"n": name}` is a nonterminal; a name that is not declared is given the
    number `len(nonterminals)` and beyond, which is out of range (for W1 fixtures). `"act"` is
    optional and defaults to 0."""
    names = [name for name, _ in g['nonterminals']]
    rank = tuple(r for _, r in g['nonterminals'])
    extra: list[str] = []

    def nt(name: str) -> int:
        if name in names:
            return names.index(name)
        if name not in extra:
            extra.append(name)
        return len(names) + extra.index(name)

    rules = []
    for rj in g['rules']:
        rhs = tuple(N(nt(x['n'])) if isinstance(x, dict) and 'n' in x else T(terminal_from_json(x))
                    for x in rj['rhs'])
        rules.append(Rule(nt(rj['lhs']), rhs, rj.get('act', 0), rj['tag']))
    return Grammar(tuple(rules), nt(g['start']), rank), names + extra


def tree_to_json(G: Grammar, t):
    if isinstance(t, Leaf):
        return token_to_json(t.tok)
    return {'r': G.rules[t.rule].tag, 'kids': [tree_to_json(G, u) for u in t.kids]}


def tree_from_json(G: Grammar, x):
    if isinstance(x, dict) and 'r' in x:
        tags = [R.tag for R in G.rules]
        return Node(tags.index(x['r']), tuple(tree_from_json(G, u) for u in x['kids']))
    return Leaf(token_from_json(x))


def show_tree(G: Grammar, t) -> str:
    """The notation of spec section 8: `r0(a, r1(b))`."""
    if isinstance(t, Leaf):
        tok = t.tok
        return {'word': lambda: tok[1], 'quoted': lambda: f'"{tok[1]}"',
                'label': lambda: f'{tok[1]}{tok[2]}', 'numeral': lambda: str(tok[1]),
                'punct': lambda: tok[1]}[tok[0]]()
    return f"{G.rules[t.rule].tag}({', '.join(show_tree(G, u) for u in t.kids)})"
