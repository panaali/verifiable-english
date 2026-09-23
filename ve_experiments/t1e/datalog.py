"""A small TRUSTED Datalog engine for the T1e Datalog arm (stratified negation, bottom-up).

Syntax (a Souffle-like subset): one clause per line, `head :- lit, lit, ... .` or a fact `head.`;
`%` starts a comment line. A literal is `p(t1, ..., tn)` or `!p(t1, ..., tn)`; a term is a variable
(`[A-Z_][A-Za-z0-9_]*`) or a constant (`[a-z][a-z0-9_]*` or a double-quoted string). Rules must be
range-restricted (every head variable and every variable of a negated literal occurs in a positive
body literal) and stratified (no predicate depends negatively on itself through recursion).

Evaluation: strata in dependency order, naive fixpoint per stratum. Standard library only; this
file, like the VE checker and the Python interpreter, is on the trusted side of the Datalog arm.
"""
from __future__ import annotations

import re

_TERM = r'(?:[A-Za-z_][A-Za-z0-9_]*|"[^"]*")'
_ATOM = re.compile(r'\s*(!?)\s*([a-z][a-z0-9_]*)\s*\(\s*(' + _TERM + r'(?:\s*,\s*' + _TERM + r')*)?\s*\)\s*')


class DatalogError(ValueError):
    pass


def is_var(t):
    return t[0].isupper() or t[0] == '_'


def _atom(text):
    m = _ATOM.fullmatch(text)
    if not m:
        raise DatalogError(f'bad literal {text!r}')
    neg, pred, args = m.groups()
    terms = tuple(a.strip() for a in args.split(',')) if args else ()
    return (bool(neg), pred, terms)


def _split_body(body):
    out, depth, cur = [], 0, ''
    for ch in body:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


def parse_clause(line):
    """'h(X, Y) :- a(X, Y), !b(Y).' -> (head, [literals]); head is (False, pred, terms)."""
    s = line.strip()
    if not s.endswith('.'):
        raise DatalogError(f'clause must end with ".": {line!r}')
    s = s[:-1]
    head, sep, body = s.partition(':-')
    h = _atom(head)
    if h[0]:
        raise DatalogError('negated head')
    lits = [_atom(x) for x in _split_body(body)] if sep else []
    if sep and not lits:
        raise DatalogError('empty body')
    pos_vars = {t for neg, _, ts in lits if not neg for t in ts if is_var(t)}
    for t in h[2]:
        if is_var(t) and t not in pos_vars:
            raise DatalogError(f'head variable {t} not range-restricted')
    for neg, _, ts in lits:
        if neg and any(is_var(t) and t not in pos_vars for t in ts):
            raise DatalogError('unsafe negation')
    return h, lits


def format_clause(clause):
    (_, hp, ht), lits = clause
    head = f'{hp}({", ".join(ht)})'
    if not lits:
        return head + '.'
    return head + ' :- ' + ', '.join(('!' if n else '') + f'{p}({", ".join(ts)})' for n, p, ts in lits) + '.'


def parse_program(text):
    clauses = []
    for line in text.split('\n'):
        s = line.strip()
        if not s or s.startswith('%'):
            continue
        clauses.append(parse_clause(s))
    return clauses


def _strata(clauses, edb):
    idb = sorted({h[1] for h, _ in clauses})
    level = {p: 0 for p in idb}
    for _ in range(len(idb) + 2):
        changed = False
        for (_, hp, _), lits in clauses:
            for neg, p, _ in lits:
                if p in level:
                    need = level[p] + (1 if neg else 0)
                    if level[hp] < need:
                        level[hp] = need
                        changed = True
        if not changed:
            return level
        if max(level.values()) > len(idb):
            break
    raise DatalogError('program is not stratified')


def _const(t):
    return t[1:-1] if t.startswith('"') else t


def _match(lits, db, binding):
    if not lits:
        yield binding
        return
    neg, p, ts = lits[0]
    if neg:
        tup = tuple(binding[t] if is_var(t) else _const(t) for t in ts)
        if tup not in db.get(p, ()):
            yield from _match(lits[1:], db, binding)
        return
    for tup in db.get(p, ()):
        if len(tup) != len(ts):
            continue
        b = dict(binding)
        ok = True
        for t, v in zip(ts, tup):
            if is_var(t):
                if b.setdefault(t, v) != v:
                    ok = False
                    break
            elif _const(t) != v:
                ok = False
                break
        if ok:
            yield from _match(lits[1:], db, b)


def evaluate(clauses, edb, max_facts=2_000_000):
    """edb: {pred: set of tuples}. Returns the least stratified model (dict pred -> set)."""
    db = {p: set(v) for p, v in edb.items()}
    for (_, hp, _), _ in clauses:
        if hp in edb:
            raise DatalogError(f'clause defines input relation {hp}')
    level = _strata(clauses, edb)
    for stratum in sorted(set(level.values())):
        mine = [c for c in clauses if level[c[0][1]] == stratum]
        for (_, hp, _), _ in mine:
            db.setdefault(hp, set())
        while True:
            new = 0
            for (_, hp, ht), lits in mine:
                # positive literals first, negated last (range restriction guarantees binding)
                ordered = [l for l in lits if not l[0]] + [l for l in lits if l[0]]
                for b in list(_match(ordered, db, {})):
                    tup = tuple(b[t] if is_var(t) else _const(t) for t in ht)
                    if tup not in db[hp]:
                        db[hp].add(tup)
                        new += 1
            if sum(len(v) for v in db.values()) > max_facts:
                raise DatalogError('fact limit exceeded')
            if not new:
                break
    return db
