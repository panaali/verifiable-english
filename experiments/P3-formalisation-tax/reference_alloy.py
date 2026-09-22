"""A small, independent Alloy evaluator (stdlib only).

    evaluate(sources: dict, target: dict, instance: dict | None) -> bool

Parses the verbatim Alloy module text (paragraphs: sig, fact, assert, pred, fun; module/open
headers and run/check commands are skipped) and evaluates a target paragraph/formula on a
finite instance, or performs a brute-force bounded `check` of an assertion.

Relations are frozensets of tuples of atom names (strings).  Formulas evaluate to bool.
Precedence follows the Alloy 4 grammar (low -> high):
  let/quantifiers | || | <=> | => (else) | && | ! | comparison | multiplicity (no/some/lone/one)
  | + - | # | ++ | & | -> | <: :> | [] (box join, looser than dot) | . | ~ ^ * (unary)
"""

from __future__ import annotations

import itertools
import re

# --------------------------------------------------------------------------------------
# Lexer
# --------------------------------------------------------------------------------------

_TOKEN_RE = re.compile(
    r"""
    (?P<ws>\s+)
  | (?P<lcomment>(//|--)[^\n]*)
  | (?P<bcomment>/\*.*?\*/)
  | (?P<num>\d+)
  | (?P<ident>@?[A-Za-z_$][A-Za-z0-9_'"$]*)
  | (?P<op><=>|=>|->|<:|:>|\+\+|&&|\|\||!=|=<|>=|<=|>>>|<<|>>|[-+&|!~^*#.,:;=<>(){}\[\]/@])
    """,
    re.VERBOSE | re.DOTALL,
)


def tokenize(text: str) -> list:
    toks = []
    pos = 0
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if not m:
            raise SyntaxError(f"cannot tokenize at {text[pos:pos + 30]!r}")
        kind = m.lastgroup
        if kind == "num":
            toks.append(("num", m.group()))
        elif kind == "ident":
            toks.append(("id", m.group()))
        elif kind == "op":
            toks.append(("op", m.group()))
        pos = m.end()
    return toks


KEYWORDS = {
    "all", "no", "some", "lone", "one", "set", "let", "not", "and", "or", "implies", "iff",
    "else", "in", "disj", "none", "univ", "iden", "sig", "abstract", "extends", "fact",
    "assert", "pred", "fun", "run", "check", "module", "open", "as", "for", "but", "expect",
    "exactly", "enum", "private", "this", "sum", "Int", "int",
}
PARAGRAPH_START = {"abstract", "sig", "fact", "assert", "pred", "fun", "run", "check", "module",
                   "open", "one", "lone", "some", "enum", "private"}
QUANTS = {"all", "no", "some", "lone", "one"}
MULTS = {"no", "some", "lone", "one", "set"}

# --------------------------------------------------------------------------------------
# AST (plain tuples):  ("name", s) ("num", n) ("unop", op, e) ("binop", op, a, b)
#   ("cmp", op, neg, a, b) ("mult", q, e) ("not", f) ("and"/"or"/"iff", a, b)
#   ("implies", a, b, else_or_None) ("quant", q, decls, body) ("let", binds, body)
#   ("block", [f...]) ("box", base, [args]) ("compr", decls, body) ("card", e)
#   ("arrow", lm, rm, a, b)    decls: list of (names, disj, expr)
# --------------------------------------------------------------------------------------


class Parser:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    # -- helpers
    def peek(self, k=0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else ("eof", "")

    def val(self, k=0):
        return self.peek(k)[1]

    def at(self, *vals):
        return self.peek()[0] in ("op", "id") and self.val() in vals

    def eat(self, v):
        if self.val() != v:
            raise SyntaxError(f"expected {v!r}, got {self.val()!r} at token {self.i}: "
                              f"{' '.join(x[1] for x in self.t[self.i:self.i + 12])}")
        self.i += 1

    def accept(self, v):
        if self.peek()[0] in ("op", "id") and self.val() == v:
            self.i += 1
            return True
        return False

    def ident(self):
        kind, v = self.peek()
        if kind != "id":
            raise SyntaxError(f"expected identifier, got {v!r}")
        self.i += 1
        return v

    # -- declarations "a, b: e, c: e2"
    def looks_like_decls(self):
        j = 0
        if self.val(j) == "disj":
            j += 1
        while True:
            kind, v = self.peek(j)
            if kind != "id" or v in KEYWORDS:
                return False
            j += 1
            if self.val(j) == ",":
                j += 1
                continue
            return self.val(j) == ":"

    def decls(self):
        out = []
        while True:
            disj = self.accept("disj")
            names = [self.ident()]
            while self.accept(","):
                names.append(self.ident())
            self.eat(":")
            disj = self.accept("disj") or disj
            mult = None
            if self.at("one", "lone", "some", "set") and not self.looks_like_decls_at(1):
                mult = self.val()
                self.i += 1
            e = self.expr_union()
            out.append((names, disj, e, mult))
            if self.val() == "," and self.looks_like_decls_at(1):
                self.i += 1
                continue
            return out

    def looks_like_decls_at(self, k):
        save = self.i
        self.i += k
        try:
            return self.looks_like_decls()
        finally:
            self.i = save

    # -- formula/expression (unified)
    def expr(self):
        if self.at("let"):
            return self.let_expr()
        if self.at(*QUANTS) and self.looks_like_decls_at(1):
            return self.quant_expr()
        return self.or_expr()

    def let_expr(self):
        self.eat("let")
        binds = []
        while True:
            n = self.ident()
            self.eat("=")
            binds.append((n, self.expr_union()))
            if not self.accept(","):
                break
        body = self.body()
        return ("let", binds, body)

    def body(self):
        if self.accept("|"):
            return self.expr()
        if self.at("{"):
            return self.block()
        raise SyntaxError(f"expected '|' or block, got {self.val()!r}")

    def quant_expr(self):
        q = self.val()
        self.i += 1
        d = self.decls()
        return ("quant", q, d, self.body())

    def block(self):
        self.eat("{")
        items = []
        while not self.at("}"):
            items.append(self.expr())
        self.eat("}")
        return ("block", items)

    def or_expr(self):
        a = self.iff_expr()
        while self.at("||", "or"):
            self.i += 1
            a = ("or", a, self.iff_expr())
        return a

    def iff_expr(self):
        a = self.implies_expr()
        while self.at("<=>", "iff"):
            self.i += 1
            a = ("iff", a, self.implies_expr())
        return a

    def implies_expr(self):
        a = self.and_expr()
        if self.at("=>", "implies"):
            self.i += 1
            b = self.implies_rhs()
            c = None
            if self.accept("else"):
                c = self.implies_rhs()
            return ("implies", a, b, c)
        return a

    def implies_rhs(self):
        if self.at("let") or (self.at(*QUANTS) and self.looks_like_decls_at(1)):
            return self.expr()
        return self.implies_expr()

    def and_expr(self):
        a = self.not_expr()
        while self.at("&&", "and"):
            self.i += 1
            a = ("and", a, self.not_rhs())
        return a

    def not_rhs(self):
        if self.at("let") or (self.at(*QUANTS) and self.looks_like_decls_at(1)):
            return self.expr()
        return self.not_expr()

    def not_expr(self):
        if self.at("!", "not") and not (self.val(1) in ("in",)):
            self.i += 1
            return ("not", self.not_rhs())
        return self.cmp_expr()

    def cmp_expr(self):
        if self.at("let") or (self.at(*QUANTS) and self.looks_like_decls_at(1)):
            return self.expr()
        if self.at(*MULTS):
            q = self.val()
            self.i += 1
            return ("mult", q, self.expr_union())
        a = self.expr_union()
        neg = False
        if self.at("!", "not") and self.val(1) in ("in", "=", "<", ">", "=<", ">=", "<="):
            neg = True
            self.i += 1
        if self.at("in", "=", "!=", "<", ">", "=<", ">=", "<="):
            op = self.val()
            self.i += 1
            b = self.expr_union()
            if op == "!=":
                op, neg = "=", True
            return ("cmp", op, neg, a, b)
        if neg:
            raise SyntaxError("dangling negation")
        return a

    # expression levels
    def expr_union(self):
        a = self.expr_card()
        while self.at("+", "-"):
            op = self.val()
            self.i += 1
            a = ("binop", op, a, self.expr_card())
        return a

    def expr_card(self):
        if self.accept("#"):
            return ("card", self.expr_card())
        return self.expr_override()

    def expr_override(self):
        a = self.expr_inter()
        while self.accept("++"):
            a = ("binop", "++", a, self.expr_inter())
        return a

    def expr_inter(self):
        a = self.expr_arrow()
        while self.accept("&"):
            a = ("binop", "&", a, self.expr_arrow())
        return a

    def expr_arrow(self):
        a = self.expr_restrict()
        while True:
            lm = None
            if self.at("some", "one", "lone", "set") and self.val(1) == "->":
                lm = self.val()
                self.i += 1
            if not self.accept("->"):
                if lm:
                    self.i -= 1
                return a
            rm = None
            if self.at("some", "one", "lone", "set"):
                rm = self.val()
                self.i += 1
            a = ("arrow", lm, rm, a, self.expr_restrict())

    def expr_restrict(self):
        a = self.expr_box()
        while self.at("<:", ":>"):
            op = self.val()
            self.i += 1
            a = ("binop", op, a, self.expr_box())
        return a

    def expr_box(self):
        a = self.expr_dot()
        while True:
            if self.at("["):
                self.i += 1
                args = []
                if not self.at("]"):
                    args.append(self.expr())
                    while self.accept(","):
                        args.append(self.expr())
                self.eat("]")
                a = ("box", a, args)
            elif self.at("."):
                self.i += 1
                a = ("binop", ".", a, self.expr_unary())
            else:
                return a

    def expr_dot(self):
        a = self.expr_unary()
        while self.at(".") :
            self.i += 1
            a = ("binop", ".", a, self.expr_unary())
        return a

    def expr_unary(self):
        if self.at("~", "^", "*"):
            op = self.val()
            self.i += 1
            return ("unop", op, self.expr_unary())
        return self.primary()

    def primary(self):
        kind, v = self.peek()
        if v == "(" and kind == "op":
            self.i += 1
            e = self.expr()
            self.eat(")")
            return e
        if v == "{" and kind == "op":
            if self.looks_like_decls_at(1):
                self.i += 1
                d = self.decls()
                body = self.body()
                self.eat("}")
                return ("compr", d, body)
            return self.block()
        if kind == "num":
            self.i += 1
            return ("num", int(v))
        if kind == "id":
            if v in ("let",) or (v in QUANTS and self.looks_like_decls_at(1)):
                return self.expr()
            if v in KEYWORDS and v not in ("none", "univ", "iden", "this", "Int", "int"):
                raise SyntaxError(f"unexpected keyword {v!r}")
            self.i += 1
            return ("name", v)
        raise SyntaxError(f"unexpected token {v!r} at {self.i}")


# --------------------------------------------------------------------------------------
# Module (paragraph) parsing
# --------------------------------------------------------------------------------------


class Module:
    def __init__(self):
        self.sigs = {}  # name -> dict(abstract, mult, parent, subset_of, fields[(name, declAST)], fact)
        self.sig_order = []
        self.facts = []  # list of (name or None, AST)
        self.asserts = {}
        self.preds = {}  # name -> (params[(name, typeAST)], bodyAST)
        self.funs = {}

    def field_owner(self):
        out = {}
        for s, d in self.sigs.items():
            for f, _ in d["fields"]:
                out[f] = s
        return out


def _skip_path(p: Parser):
    p.ident()
    while p.accept("/"):
        p.ident()
    if p.at("["):
        depth = 0
        while True:
            if p.at("["):
                depth += 1
            elif p.at("]"):
                depth -= 1
            p.i += 1
            if depth == 0:
                break


def _params(p: Parser):
    params = []
    close = None
    if p.accept("["):
        close = "]"
    elif p.accept("("):
        close = ")"
    else:
        return params
    while not p.at(close):
        names = [p.ident()]
        while p.accept(","):
            names.append(p.ident())
        p.eat(":")
        p.accept("disj")
        start = p.i
        depth = 0
        while not (depth == 0 and (p.at(",") or p.at(close))):
            if p.at("[", "(", "{"):
                depth += 1
            elif p.at("]", ")", "}"):
                depth -= 1
            p.i += 1
        typ = p.t[start:p.i]
        for n in names:
            params.append((n, typ))
        p.accept(",")
    p.eat(close)
    return params


def parse_module(text: str, mod: Module | None = None) -> Module:
    mod = mod or Module()
    p = Parser(tokenize(text))
    while p.peek()[0] != "eof":
        v = p.val()
        if v == "module":
            p.i += 1
            _skip_path(p)
        elif v == "open":
            p.i += 1
            _skip_path(p)
            if p.accept("as"):
                p.ident()
        elif v in ("run", "check"):
            p.i += 1
            if p.at("{"):
                p.block()
            while p.peek()[0] != "eof" and p.val() not in PARAGRAPH_START:
                p.i += 1
        elif v == "private":
            p.i += 1
        elif v in ("abstract", "sig") or (v in ("one", "lone", "some") and p.val(1) in ("sig", "abstract")):
            abstract = False
            mult = None
            while p.at("abstract", "one", "lone", "some"):
                if p.val() == "abstract":
                    abstract = True
                else:
                    mult = p.val()
                p.i += 1
            p.eat("sig")
            names = [p.ident()]
            while p.accept(","):
                names.append(p.ident())
            parent = None
            subset = None
            if p.accept("extends"):
                parent = p.ident()
            elif p.accept("in"):
                subset = [p.ident()]
                while p.accept("+"):
                    subset.append(p.ident())
            p.eat("{")
            fields = []
            while not p.at("}"):
                fnames = [p.ident()]
                while p.accept(","):
                    fnames.append(p.ident())
                p.eat(":")
                p.accept("disj")
                mult_f = None
                if p.at("one", "lone", "some", "set") and p.val(1) != "->":
                    mult_f = p.val()
                    p.i += 1
                e = p.expr_union()
                for fn in fnames:
                    fields.append((fn, (mult_f, e)))
                if not p.accept(","):
                    break
            p.eat("}")
            fact = p.block() if p.at("{") else None
            for n in names:
                mod.sigs[n] = dict(abstract=abstract, mult=mult, parent=parent, subset=subset,
                                   fields=fields, fact=fact)
                mod.sig_order.append(n)
        elif v == "fact":
            p.i += 1
            name = p.ident() if p.peek()[0] == "id" else None
            mod.facts.append((name, p.block()))
        elif v == "assert":
            p.i += 1
            name = p.ident()
            mod.asserts[name] = p.block()
        elif v in ("pred", "fun"):
            p.i += 1
            name = p.ident()
            if p.accept("."):  # receiver form  pred Sig.name[...]
                recv = name
                name = p.ident()
                params = [("this", [("id", recv)])] + _params(p)
            else:
                params = _params(p)
            if v == "fun":
                p.eat(":")
                depth = 0
                while not (depth == 0 and p.at("{")):
                    if p.at("[", "("):
                        depth += 1
                    elif p.at("]", ")"):
                        depth -= 1
                    p.i += 1
                mod.funs[name] = (params, p.block())
            else:
                mod.preds[name] = (params, p.block())
        elif v == "enum":
            raise NotImplementedError("enum")
        else:
            raise SyntaxError(f"unexpected top-level token {v!r} at {p.i}")
    return mod


# --------------------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------------------

EMPTY = frozenset()


def rel_join(a, b):
    idx = {}
    for t in b:
        idx.setdefault(t[0], []).append(t[1:])
    out = set()
    for s in a:
        for rest in idx.get(s[-1], ()):
            tup = s[:-1] + rest
            if tup:
                out.add(tup)
    return frozenset(out)


def closure(r):
    res = set(r)
    while True:
        new = set(rel_join(frozenset(res), r)) - res
        if not new:
            return frozenset(res)
        res |= new


class Env:
    def __init__(self, mod: Module, rels: dict, univ: frozenset, this_fields=None):
        self.mod = mod
        self.rels = rels  # sig and field names -> relation
        self.univ = univ
        self.iden = frozenset((a, a) for (a,) in univ)
        self.this_fields = this_fields or set()  # field names implicitly prefixed with this.


class Evaluator:
    def __init__(self, env: Env):
        self.env = env

    # --- name resolution
    def callable(self, name, scope):
        if name in scope:
            return None
        m = self.env.mod
        if name in m.preds:
            return ("pred",) + m.preds[name]
        if name in m.funs:
            return ("fun",) + m.funs[name]
        return None

    def call(self, kind_params_body, args, scope):
        kind, params, body = kind_params_body
        if len(params) != len(args):
            raise TypeError(f"arity mismatch: {len(params)} params, {len(args)} args")
        new_scope = {}
        for (pn, _), a in zip(params, args):
            new_scope[pn] = self.ev(a, scope)
        return self.ev(body, new_scope)

    def name(self, v, scope):
        env = self.env
        if v in scope:
            return scope[v]
        raw = v[1:] if v.startswith("@") else v
        if v in env.this_fields and "this" in scope:
            return rel_join(scope["this"], env.rels[v])
        if raw in env.rels:
            return env.rels[raw]
        if raw == "univ":
            return env.univ
        if raw == "none":
            return EMPTY
        if raw == "iden":
            return env.iden
        c = self.callable(raw, scope)
        if c is not None:
            return self.call(c, [], scope)
        raise NameError(f"unknown name {v!r}")

    # --- main
    def ev(self, n, scope):
        k = n[0]
        if k == "name":
            return self.name(n[1], scope)
        if k == "num":
            return n[1]
        if k == "unop":
            e = self.rel(n[2], scope)
            if n[1] == "~":
                return frozenset(tuple(reversed(t)) for t in e)
            if n[1] == "^":
                return closure(e)
            if n[1] == "*":
                return closure(e) | self.env.iden
        if k == "binop":
            op = n[1]
            if op == ".":
                # dot-call:  x.f  ==  f[x]
                if n[3][0] == "name":
                    c = self.callable(n[3][1], scope)
                    if c is not None:
                        return self.call(c, [n[2]], scope)
                return rel_join(self.rel(n[2], scope), self.rel(n[3], scope))
            a, b = self.rel(n[2], scope), self.rel(n[3], scope)
            if op == "+":
                return a | b
            if op == "-":
                return a - b
            if op == "&":
                return a & b
            if op == "++":
                dom = {t[0] for t in b}
                return frozenset(t for t in a if t[0] not in dom) | b
            if op == "<:":
                s = {t[0] for t in a}
                return frozenset(t for t in b if t[0] in s)
            if op == ":>":
                s = {t[0] for t in b}
                return frozenset(t for t in a if t[-1] in s)
        if k == "arrow":
            a, b = self.rel(n[3], scope), self.rel(n[4], scope)
            return frozenset(x + y for x in a for y in b)
        if k == "box":
            base, args = n[1], n[2]
            if base[0] == "name":
                c = self.callable(base[1], scope)
                if c is not None:
                    return self.call(c, args, scope)
            if base[0] == "binop" and base[1] == "." and base[3][0] == "name":
                c = self.callable(base[3][1], scope)
                if c is not None:
                    return self.call(c, [base[2]] + list(args), scope)
            r = self.rel(base, scope)
            for a in args:
                r = rel_join(self.rel(a, scope), r)
            return r
        if k == "card":
            return len(self.rel(n[1], scope))
        if k == "cmp":
            op, neg, a, b = n[1], n[2], self.ev(n[3], scope), self.ev(n[4], scope)
            if op == "in":
                res = a <= b
            elif op == "=":
                res = a == b
            else:
                res = {"<": a < b, ">": a > b, "=<": a <= b, "<=": a <= b, ">=": a >= b}[op]
            return (not res) if neg else res
        if k == "mult":
            e = self.rel(n[2], scope)
            return {"no": len(e) == 0, "some": len(e) > 0, "lone": len(e) <= 1,
                    "one": len(e) == 1, "set": True}[n[1]]
        if k == "not":
            return not self.form(n[1], scope)
        if k == "and":
            return self.form(n[1], scope) and self.form(n[2], scope)
        if k == "or":
            return self.form(n[1], scope) or self.form(n[2], scope)
        if k == "iff":
            return self.form(n[1], scope) == self.form(n[2], scope)
        if k == "implies":
            if self.form(n[1], scope):
                return self.form(n[2], scope)
            return self.form(n[3], scope) if n[3] is not None else True
        if k == "block":
            items = n[1]
            if len(items) == 1:
                return self.ev(items[0], scope)
            return all(self.form(x, scope) for x in items)
        if k == "let":
            s = dict(scope)
            for name, e in n[1]:
                s[name] = self.ev(e, s)
            return self.ev(n[2], s)
        if k == "quant":
            q, decls, body = n[1], n[2], n[3]
            count = 0
            for s in self.bindings(decls, scope):
                ok = self.form(body, s)
                if q == "all" and not ok:
                    return False
                if q == "some" and ok:
                    return True
                if ok:
                    count += 1
                    if q in ("no", "lone", "one") and count > (0 if q == "no" else 1):
                        return False
            return {"all": True, "some": False, "no": count == 0, "lone": count <= 1,
                    "one": count == 1}[q]
        if k == "compr":
            decls, body = n[1], n[2]
            out = set()
            for s in self.bindings(decls, scope):
                if self.form(body, s):
                    tup = ()
                    for names, _, _, _ in decls:
                        for nm in names:
                            tup += next(iter(s[nm]))
                    out.add(tup)
            return frozenset(out)
        raise ValueError(f"cannot evaluate node {n!r}")

    def rel(self, n, scope):
        v = self.ev(n, scope)
        if not isinstance(v, frozenset):
            raise TypeError(f"expected relation, got {v!r} for {n!r}")
        return v

    def form(self, n, scope):
        v = self.ev(n, scope)
        if not isinstance(v, bool):
            raise TypeError(f"expected formula, got {v!r} for {n!r}")
        return v

    def bindings(self, decls, scope):
        """Enumerate variable assignments.  Multi-variable `one`/`lone` quantifiers count
        combinations (Alloy 4 translates them as a comprehension), which is what we do by
        enumerating the cartesian product of all declared variables."""
        flat = []
        for names, disj, e, mult in decls:
            if mult not in (None, "one"):
                raise NotImplementedError("higher-order quantification")
            for nm in names:
                flat.append((nm, e, disj, tuple(names)))

        def rec(i, s, used):
            if i == len(flat):
                yield s
                return
            nm, e, disj, group = flat[i]
            dom = self.rel(e, s)
            for t in sorted(dom):
                if len(t) != 1:
                    raise NotImplementedError("non-unary quantifier domain")
                if disj and any(used.get(g) == t for g in group if g != nm):
                    continue
                s2 = dict(s)
                s2[nm] = frozenset([t])
                u2 = dict(used)
                u2[nm] = t
                yield from rec(i + 1, s2, u2)

        yield from rec(0, dict(scope), {})


# --------------------------------------------------------------------------------------
# Instances and targets
# --------------------------------------------------------------------------------------


def load_module(sources: dict) -> Module:
    mod = Module()
    # main module last is irrelevant; paragraphs live in one namespace
    for name in sorted(sources, key=lambda n: (n != "source.als", n)):
        parse_module(sources[name], mod)
    return mod


def build_env(mod: Module, instance: dict) -> Env:
    rels = {}
    atoms = set()
    for s, lst in (instance.get("sigs") or {}).items():
        rels[s] = frozenset((a,) for a in lst)
        atoms.update(lst)
    for f, tuples in (instance.get("fields") or {}).items():
        rels[f] = frozenset(tuple(t) for t in tuples)
        for t in tuples:
            if not set(t) <= atoms:
                raise ValueError(f"field {f} mentions atoms outside all sigs: {t}")
    # declared sigs not listed in the instance are empty
    for s in mod.sigs:
        rels.setdefault(s, EMPTY)
    return Env(mod, rels, frozenset((a,) for a in atoms))


def _binding_scope(env: Env, bindings: dict) -> dict:
    scope = {}
    for k, v in (bindings or {}).items():
        if v in env.rels and v not in {a for (a,) in env.univ}:
            scope[k] = env.rels[v]
        else:
            scope[k] = frozenset([(v,)])
    return scope


def _formula_ast(text):
    p = Parser(tokenize(text))
    items = []
    while p.peek()[0] != "eof":
        items.append(p.expr())
    return ("block", items)


def evaluate(sources: dict, target: dict, instance: dict | None) -> bool:
    mod = load_module(sources)
    kind = target["kind"]
    if kind == "check":
        return bounded_check(mod, target["name"], int(target["scope"]))
    env = build_env(mod, instance)
    ev = Evaluator(env)
    scope = _binding_scope(env, instance.get("bindings"))
    if kind == "fact":
        if "name" in target and target["name"] is not None:
            body = [b for (n, b) in mod.facts if n == target["name"]]
            if len(body) != 1:
                raise KeyError(f"fact {target['name']!r} not found uniquely")
            return ev.form(body[0], {})
        return ev.form(mod.facts[int(target["index"])][1], {})
    if kind == "pred":
        params, body = mod.preds[target["name"]]
        names = [pn for pn, _ in params]
        args = target.get("args") or names
        if len(args) != len(names):
            raise TypeError("pred arity mismatch")
        s = {pn: scope[a] for pn, a in zip(names, args)}
        return ev.form(body, s)
    if kind == "assert":
        return ev.form(mod.asserts[target["name"]], {})
    if kind == "formula":
        return ev.form(_formula_ast(target["text"]), scope)
    raise ValueError(f"unknown target kind {kind}")


# --------------------------------------------------------------------------------------
# Bounded check (brute force)
# --------------------------------------------------------------------------------------


def _children(mod):
    ch = {s: [] for s in mod.sigs}
    for s, d in mod.sigs.items():
        if d["parent"]:
            ch[d["parent"]].append(s)
    return ch


def _descendants(mod, ch, s):
    out = [s]
    for c in ch[s]:
        out += _descendants(mod, ch, c)
    return out


def _ancestors(mod, s):
    out = [s]
    while mod.sigs[s]["parent"]:
        s = mod.sigs[s]["parent"]
        out.append(s)
    return out


def _mult_ok(m, n):
    return {None: True, "set": True, "some": n >= 1, "one": n == 1, "lone": n <= 1}[m]


def _sig_assignments(mod, k):
    """Yield dict sig -> frozenset of atoms (symmetry-broken on class order)."""
    if any(d["subset"] for d in mod.sigs.values()):
        raise NotImplementedError("subset sigs (sig X in Y)")
    ch = _children(mod)
    tops = [s for s in mod.sig_order if not mod.sigs[s]["parent"]]
    per_top = []
    for t in tops:
        desc = _descendants(mod, ch, t)
        classes = [s for s in desc if not mod.sigs[s]["abstract"] or not ch[s]]
        options = []
        tm = mod.sigs[t]["mult"]
        sizes = {"one": [1], "lone": [0, 1], "some": range(1, k + 1)}.get(tm, range(0, k + 1))
        for n in sizes:
            atoms = [f"{t}${i}" for i in range(n)]
            for combo in itertools.combinations_with_replacement(range(len(classes)), n):
                members = {s: set() for s in desc}
                for a, ci in zip(atoms, combo):
                    for anc in _ancestors(mod, classes[ci]):
                        members[anc].add(a)
                if all(_mult_ok(mod.sigs[s]["mult"], len(members[s])) and len(members[s]) <= k
                       for s in desc):
                    options.append({s: frozenset((a,) for a in m) for s, m in members.items()})
        per_top.append(options)
    for combo in itertools.product(*per_top):
        out = {}
        for d in combo:
            out.update(d)
        yield out


def _field_options(ev, scope, decl):
    """All relations r (without the owner column) allowed by a field declaration."""
    mult, e = decl
    if e[0] == "arrow":
        lm, rm = e[1], e[2]
        A, B = ev.rel(e[3], scope), ev.rel(e[4], scope)
        if any(len(t) != 1 for t in A | B):
            raise NotImplementedError("nested arrow field")
        pairs = [a + b for a in sorted(A) for b in sorted(B)]
        for bits in itertools.product([0, 1], repeat=len(pairs)):
            r = frozenset(p for p, bit in zip(pairs, bits) if bit)
            if all(_mult_ok(rm, sum(1 for t in r if t[0] == a[0])) for a in A) and \
               all(_mult_ok(lm, sum(1 for t in r if t[1] == b[0])) for b in B):
                yield r
        return
    dom = sorted(ev.rel(e, scope))
    m = mult or "one"
    for n in range(len(dom) + 1):
        if not _mult_ok(m, n):
            continue
        for sub in itertools.combinations(dom, n):
            yield frozenset(sub)


def _all_fields(mod):
    out = []
    for s in mod.sig_order:
        for f, decl in mod.sigs[s]["fields"]:
            out.append((s, f, decl))
    return out


def _inherited_fields(mod, s):
    out = set()
    for a in _ancestors(mod, s):
        out |= {f for f, _ in mod.sigs[a]["fields"]}
    return out


def bounded_check(mod: Module, assert_name: str, k: int) -> bool:
    """True iff no instance within scope k satisfies all facts and violates the assertion."""
    body = mod.asserts[assert_name]
    fields = _all_fields(mod)
    for sigrels in _sig_assignments(mod, k):
        univ = frozenset().union(*sigrels.values()) if sigrels else EMPTY
        slots = []  # (field, owner atom, decl, owner sig)
        for s, f, decl in fields:
            for (a,) in sorted(sigrels[s]):
                slots.append((f, a, decl, s))

        rels = dict(sigrels)
        for _, f, _ in fields:
            rels[f] = EMPTY

        def assign(i):
            if i == len(slots):
                yield dict(rels)
                return
            f, a, decl, s = slots[i]
            env = Env(mod, dict(rels), univ, this_fields=_inherited_fields(mod, s))
            ev = Evaluator(env)
            for r in list(_field_options(ev, {"this": frozenset([(a,)])}, decl)):
                old = rels[f]
                rels[f] = old | frozenset((a,) + t for t in r)
                yield from assign(i + 1)
                rels[f] = old

        for full in assign(0):
            env = Env(mod, full, univ)
            ev = Evaluator(env)
            if not all(ev.form(b, {}) for _, b in mod.facts):
                continue
            ok = True
            for s, d in mod.sigs.items():
                if d["fact"] is None:
                    continue
                env_s = Env(mod, full, univ, this_fields=_inherited_fields(mod, s))
                ev_s = Evaluator(env_s)
                for t in full[s]:
                    if not ev_s.form(d["fact"], {"this": frozenset([t])}):
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            if not ev.form(body, {}):
                return False
    return True
