"""Independent reference interpreter for the Cedar subset used by the P3 items.

Stdlib only. Written from the Cedar language documentation, not from any VE code.

Public API:
    authorize(policy_text, linked, entities, request, schema_extn=None) -> bool
    explain(policy_text, linked, entities, request, schema_extn=None) -> dict

`schema_extn` (optional) stands in for Cedar's schema-based entity parsing: a map
{entity_type: {attr: "datetime" | "duration"}} saying which *bare string* entity
attributes the schema types as extension values (Cedar's "implicit constructor").
The implicit escape {"fn": ..., "arg": ...} (without "__extn") is always accepted.
"""
from __future__ import annotations

import calendar
import re
from dataclasses import dataclass

I64_MIN, I64_MAX = -(2 ** 63), 2 ** 63 - 1
MS_PER_DAY = 86_400_000


class CedarError(Exception):
    """Evaluation error: the enclosing policy is skipped."""


class ParseError(Exception):
    pass


# ------------------------------------------------------------------ lexer

_TOKEN_RE = re.compile(r"""
    (?P<ws>\s+|//[^\n]*)
  | (?P<str>"(?:[^"\\]|\\.)*")
  | (?P<int>\d+)
  | (?P<ident>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<op>::|==|!=|<=|>=|&&|\|\||[<>!()\[\]{},;.@?+\-*:])
""", re.VERBOSE | re.DOTALL)

_ESCAPES = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", "0": "\0", "'": "'", '"': '"'}


def _unescape(body: str, pattern: bool = False):
    """Decode a string literal body. For `like` patterns return a list of chars
    where an unescaped `*` is the wildcard object None."""
    out, i = [], 0
    while i < len(body):
        c = body[i]
        if c == "\\":
            n = body[i + 1]
            if n in _ESCAPES:
                out.append(_ESCAPES[n]); i += 2
            elif n == "*" and pattern:
                out.append("*"); i += 2
            elif n == "u":
                m = re.match(r"u\{([0-9a-fA-F]{1,6})\}", body[i + 1:])
                if not m:
                    raise ParseError("bad \\u escape")
                out.append(chr(int(m.group(1), 16))); i += 1 + m.end()
            else:
                raise ParseError(f"bad escape \\{n}")
        else:
            out.append(None if (c == "*" and pattern) else c); i += 1
    return out if pattern else "".join(out)


def tokenize(text: str) -> list:
    toks, pos = [], 0
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if not m:
            raise ParseError(f"unexpected character {text[pos]!r} at {pos}")
        pos = m.end()
        kind = m.lastgroup
        if kind != "ws":
            toks.append((kind, m.group()))
    toks.append(("eof", ""))
    return toks


# ------------------------------------------------------------------ values

@dataclass(frozen=True)
class EUID:
    type: str
    id: str

    def __str__(self):
        return f'{self.type}::"{self.id}"'


@dataclass(frozen=True)
class DateTime:
    ms: int  # milliseconds since the Unix epoch, UTC


@dataclass(frozen=True)
class Duration:
    ms: int


class CSet:
    """Cedar set: structural membership, order-irrelevant."""

    def __init__(self, items):
        self.items = []
        for x in items:
            if not any(ceq(x, y) for y in self.items):
                self.items.append(x)

    def has(self, v) -> bool:
        return any(ceq(v, y) for y in self.items)


def tname(v) -> str:
    if isinstance(v, bool): return "bool"
    if isinstance(v, int): return "long"
    if isinstance(v, str): return "string"
    if isinstance(v, EUID): return "entity"
    if isinstance(v, CSet): return "set"
    if isinstance(v, dict): return "record"
    if isinstance(v, DateTime): return "datetime"
    if isinstance(v, Duration): return "duration"
    raise TypeError(f"not a Cedar value: {v!r}")


def ceq(a, b) -> bool:
    """Structural equality; values of different types are simply unequal."""
    ta, tb = tname(a), tname(b)
    if ta != tb:
        return False
    if ta == "set":
        return all(b.has(x) for x in a.items) and all(a.has(y) for y in b.items)
    if ta == "record":
        return a.keys() == b.keys() and all(ceq(a[k], b[k]) for k in a)
    return a == b


def _i64(n: int) -> int:
    if not I64_MIN <= n <= I64_MAX:
        raise CedarError("integer overflow")
    return n


def parse_datetime(s: str) -> DateTime:
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})"
                     r"(?:T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{3}))?(Z|[+-]\d{4}))?", s)
    if not m:
        raise CedarError(f"invalid datetime {s!r}")
    y, mo, d, hh, mi, ss, frac, tz = m.groups()
    y, mo, d = int(y), int(mo), int(d)
    hh, mi, ss = int(hh or 0), int(mi or 0), int(ss or 0)
    if not (1 <= mo <= 12 and 1 <= d <= calendar.monthrange(y, mo)[1]
            and hh < 24 and mi < 60 and ss < 60):
        raise CedarError(f"invalid datetime {s!r}")
    secs = calendar.timegm((y, mo, d, hh, mi, ss, 0, 0, 0))
    ms = secs * 1000 + int(frac or 0)
    if tz and tz != "Z":
        oh, om = int(tz[1:3]), int(tz[3:5])
        if oh >= 24 or om >= 60:
            raise CedarError(f"invalid datetime offset {s!r}")
        off = (oh * 60 + om) * 60_000
        ms -= off if tz[0] == "+" else -off  # local = UTC + offset
    return DateTime(_i64(ms))


def parse_duration(s: str) -> Duration:
    m = re.fullmatch(r"(-?)(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m(?!s))?(?:(\d+)s)?(?:(\d+)ms)?", s)
    if not m or not any(m.groups()[1:]):
        raise CedarError(f"invalid duration {s!r}")
    sign, d, h, mi, sec, ms = m.groups()
    total = (int(d or 0) * MS_PER_DAY + int(h or 0) * 3_600_000 + int(mi or 0) * 60_000
             + int(sec or 0) * 1000 + int(ms or 0))
    return Duration(_i64(-total if sign else total))


EXTN_CONSTRUCTORS = {"datetime": parse_datetime, "duration": parse_duration}


def call_extn(fn: str, arg):
    if fn not in EXTN_CONSTRUCTORS:
        raise CedarError(f"unsupported extension function {fn}")
    if tname(arg) != "string":
        raise CedarError(f"{fn}() expects a string")
    return EXTN_CONSTRUCTORS[fn](arg)


def parse_uid(s: str) -> EUID:
    """Parse `A::B::"id"` into an EUID."""
    p = _Parser(tokenize(s))
    uid = p.entity_ref()
    p.expect("eof")
    return uid


def from_json(v):
    """Convert a normalised entity/context JSON value into a Cedar value."""
    if isinstance(v, dict):
        if set(v) == {"__entity"}:
            e = v["__entity"]
            return parse_uid(e) if isinstance(e, str) else EUID(e["type"], e["id"])
        if set(v) == {"__extn"}:
            return call_extn(v["__extn"]["fn"], v["__extn"]["arg"])
        if set(v) == {"fn", "arg"} and v["fn"] in EXTN_CONSTRUCTORS:
            return call_extn(v["fn"], v["arg"])  # schema-based implicit escape
        return {k: from_json(x) for k, x in v.items()}
    if isinstance(v, list):
        return CSet(from_json(x) for x in v)
    if isinstance(v, (bool, int, str)):
        return v
    raise ValueError(f"unsupported JSON value {v!r}")


# ------------------------------------------------------------------ parser
# AST nodes are tuples whose first element is a tag.

RELOPS = {"==", "!=", "<", "<=", ">", ">=", "in"}
VARS = {"principal", "action", "resource", "context"}


class _Parser:
    def __init__(self, toks):
        self.toks, self.i = toks, 0

    def peek(self, k=0):
        return self.toks[self.i + k]

    def at(self, val, k=0):
        t = self.toks[self.i + k]
        return t[0] in ("op", "ident") and t[1] == val

    def next(self):
        t = self.toks[self.i]; self.i += 1
        return t

    def expect(self, kind_or_val):
        t = self.next()
        if t[0] == kind_or_val or (t[0] in ("op", "ident") and t[1] == kind_or_val):
            return t
        raise ParseError(f"expected {kind_or_val!r}, got {t[1]!r}")

    # ---- policies
    def policies(self) -> list:
        out = []
        while self.peek()[0] != "eof":
            out.append(self.policy())
        return out

    def policy(self) -> dict:
        annots = {}
        while self.at("@"):
            self.next()
            name = self.expect("ident")[1]
            val = None
            if self.at("("):
                self.next(); val = _unescape(self.expect("str")[1][1:-1]); self.expect(")")
            annots[name] = val
        effect = self.expect("ident")[1]
        if effect not in ("permit", "forbid"):
            raise ParseError(f"bad effect {effect}")
        self.expect("(")
        scope = [self.scope_elem("principal"), None, None]
        self.expect(","); scope[1] = self.scope_elem("action")
        self.expect(","); scope[2] = self.scope_elem("resource")
        self.expect(")")
        conds = []
        while self.at("when") or self.at("unless"):
            kind = self.next()[1]
            self.expect("{"); conds.append((kind, self.expr())); self.expect("}")
        self.expect(";")
        return {"effect": effect, "annotations": annots, "scope": scope, "conds": conds}

    def scope_ref(self):
        if self.at("?"):
            self.next()
            return ("slot", "?" + self.expect("ident")[1])
        if self.at("["):
            self.next()
            items = []
            while not self.at("]"):
                items.append(self.entity_ref())
                if not self.at("]"):
                    self.expect(",")
            self.next()
            return ("set", items)
        return ("uid", self.entity_ref())

    def scope_elem(self, var):
        self.expect(var)
        if self.at("=="):
            self.next(); return ("==", self.scope_ref())
        if self.at("in"):
            self.next(); return ("in", self.scope_ref())
        if self.at("is"):
            self.next(); typ = self.path()
            if self.at("in"):
                self.next(); return ("is_in", typ, self.scope_ref())
            return ("is", typ)
        return ("any",)

    def path(self) -> str:
        parts = [self.expect("ident")[1]]
        while self.at("::") and self.peek(1)[0] == "ident":
            self.next(); parts.append(self.next()[1])
        return "::".join(parts)

    def entity_ref(self) -> EUID:
        typ = self.path()
        self.expect("::")
        return EUID(typ, _unescape(self.expect("str")[1][1:-1]))

    # ---- expressions
    def expr(self):
        if self.at("if"):
            self.next(); c = self.expr(); self.expect("then"); a = self.expr()
            self.expect("else"); b = self.expr()
            return ("if", c, a, b)
        return self.or_()

    def or_(self):
        e = self.and_()
        while self.at("||"):
            self.next(); e = ("||", e, self.and_())
        return e

    def and_(self):
        e = self.relation()
        while self.at("&&"):
            self.next(); e = ("&&", e, self.relation())
        return e

    def relation(self):
        e = self.add()
        t = self.peek()
        if t[0] in ("op", "ident") and t[1] in RELOPS:
            self.next(); return ("rel", t[1], e, self.add())
        if self.at("has"):
            self.next()
            t = self.next()
            if t[0] == "str":
                return ("has", e, _unescape(t[1][1:-1]))
            if t[0] != "ident":
                raise ParseError("bad has")
            return ("has", e, t[1])
        if self.at("like"):
            self.next()
            return ("like", e, _unescape(self.expect("str")[1][1:-1], pattern=True))
        if self.at("is"):
            self.next(); typ = self.path()
            if self.at("in"):
                self.next(); return ("is", e, typ, self.add())
            return ("is", e, typ, None)
        return e

    def add(self):
        e = self.mult()
        while self.at("+") or self.at("-"):
            op = self.next()[1]; e = ("arith", op, e, self.mult())
        return e

    def mult(self):
        e = self.unary()
        while self.at("*"):
            self.next(); e = ("arith", "*", e, self.unary())
        return e

    def unary(self):
        if self.at("!"):
            self.next(); return ("!", self.unary())
        if self.at("-"):
            self.next()
            if self.peek()[0] == "int":
                return ("lit", -int(self.next()[1]))
            return ("neg", self.unary())
        return self.member()

    def member(self):
        e = self.primary()
        while True:
            if self.at("."):
                self.next(); name = self.expect("ident")[1]
                if self.at("("):
                    e = ("method", e, name, self.args())
                else:
                    e = ("attr", e, name)
            elif self.at("["):
                self.next(); key = _unescape(self.expect("str")[1][1:-1]); self.expect("]")
                e = ("attr", e, key)
            else:
                return e

    def args(self):
        self.expect("(")
        out = []
        while not self.at(")"):
            out.append(self.expr())
            if not self.at(")"):
                self.expect(",")
        self.next()
        return out

    def primary(self):
        kind, val = self.peek()
        if kind == "int":
            self.next(); return ("lit", int(val))
        if kind == "str":
            self.next(); return ("lit", _unescape(val[1:-1]))
        if self.at("true") or self.at("false"):
            self.next(); return ("lit", val == "true")
        if self.at("("):
            self.next(); e = self.expr(); self.expect(")"); return e
        if self.at("["):
            self.next(); items = []
            while not self.at("]"):
                items.append(self.expr())
                if not self.at("]"):
                    self.expect(",")
            self.next()
            return ("setlit", items)
        if self.at("{"):
            self.next(); fields = []
            while not self.at("}"):
                t = self.next()
                key = _unescape(t[1][1:-1]) if t[0] == "str" else t[1]
                self.expect(":"); fields.append((key, self.expr()))
                if not self.at("}"):
                    self.expect(",")
            self.next()
            return ("reclit", fields)
        if self.at("?"):
            self.next(); return ("slot", "?" + self.expect("ident")[1])
        if kind == "ident":
            if val in VARS and not self.at("::", 1):
                self.next(); return ("var", val)
            if self.at("(", 1):
                self.next(); return ("call", val, self.args())
            return ("lit", self.entity_ref())
        raise ParseError(f"unexpected token {val!r}")


def parse_policies(text: str) -> list:
    return _Parser(tokenize(text)).policies()


# ------------------------------------------------------------------ evaluation

class Store:
    def __init__(self, entities, schema_extn=None):
        self.attrs, self.parents = {}, {}
        schema_extn = schema_extn or {}
        for e in entities:
            uid = parse_uid(e["uid"])
            hints = schema_extn.get(uid.type, {})
            attrs = {}
            for k, v in (e.get("attrs") or {}).items():
                if k in hints and isinstance(v, str):
                    attrs[k] = call_extn(hints[k], v)  # schema implicit constructor
                else:
                    attrs[k] = from_json(v)
            self.attrs[uid] = attrs
            self.parents[uid] = [parse_uid(p) for p in e.get("parents", [])]

    def is_descendant(self, e: EUID, anc: EUID) -> bool:
        """Reflexive-transitive `in` over the parents relation."""
        seen, todo = set(), [e]
        while todo:
            x = todo.pop()
            if x == anc:
                return True
            if x not in seen:
                seen.add(x)
                todo.extend(self.parents.get(x, []))
        return False


def _want(v, t, what):
    if tname(v) != t:
        raise CedarError(f"{what}: expected {t}, got {tname(v)}")
    return v


class Evaluator:
    def __init__(self, store: Store, request: dict, slots: dict):
        self.store, self.slots = store, slots
        self.env = {"principal": request["principal"], "action": request["action"],
                    "resource": request["resource"], "context": request["context"]}

    def in_(self, lhs, rhs) -> bool:
        _want(lhs, "entity", "in (left)")
        if tname(rhs) == "set":
            # P3 correction (see REPORT.md): Cedar's spec type-checks every member before
            # testing membership (cedar-spec Evaluator.lean `inₛ`: vs.mapOrErr asEntityUID),
            # so a non-entity member is an error regardless of order.
            members = [_want(x, "entity", "in (set member)") for x in rhs.items]
            return any(self.store.is_descendant(lhs, x) for x in members)
        return self.store.is_descendant(lhs, _want(rhs, "entity", "in (right)"))

    def get_attr(self, v, name):
        t = tname(v)
        if t == "record":
            if name not in v:
                raise CedarError(f"record has no attribute {name}")
            return v[name]
        if t == "entity":
            if v not in self.store.attrs:
                raise CedarError(f"entity {v} does not exist")
            if name not in self.store.attrs[v]:
                raise CedarError(f"entity {v} has no attribute {name}")
            return self.store.attrs[v][name]
        raise CedarError(f"attribute access on {t}")

    def has_attr(self, v, name) -> bool:
        t = tname(v)
        if t == "record":
            return name in v
        if t == "entity":
            return name in self.store.attrs.get(v, {})
        raise CedarError(f"`has` on {t}")

    def bool_(self, node, what) -> bool:
        return _want(self.ev(node), "bool", what)

    def ev(self, n):
        tag = n[0]
        if tag == "lit":
            return n[1]
        if tag == "var":
            return self.env[n[1]]
        if tag == "slot":
            if n[1] not in self.slots:
                raise CedarError(f"unfilled slot {n[1]}")
            return self.slots[n[1]]
        if tag == "if":
            return self.ev(n[2]) if self.bool_(n[1], "if") else self.ev(n[3])
        if tag == "&&":
            return self.bool_(n[1], "&&") and self.bool_(n[2], "&&")
        if tag == "||":
            return self.bool_(n[1], "||") or self.bool_(n[2], "||")
        if tag == "!":
            return not self.bool_(n[1], "!")
        if tag == "neg":
            return _i64(-_want(self.ev(n[1]), "long", "unary -"))
        if tag == "arith":
            a = _want(self.ev(n[2]), "long", n[1]); b = _want(self.ev(n[3]), "long", n[1])
            return _i64(a + b if n[1] == "+" else a - b if n[1] == "-" else a * b)
        if tag == "rel":
            return self.rel(n[1], self.ev(n[2]), self.ev(n[3]))
        if tag == "has":
            return self.has_attr(self.ev(n[1]), n[2])
        if tag == "like":
            return _like(_want(self.ev(n[1]), "string", "like"), n[2])
        if tag == "is":
            v = _want(self.ev(n[1]), "entity", "is")
            if v.type != n[2]:
                return False
            return True if n[3] is None else self.in_(v, self.ev(n[3]))
        if tag == "attr":
            return self.get_attr(self.ev(n[1]), n[2])
        if tag == "setlit":
            return CSet(self.ev(x) for x in n[1])
        if tag == "reclit":
            return {k: self.ev(x) for k, x in n[1]}
        if tag == "call":
            args = [self.ev(a) for a in n[2]]
            if len(args) != 1:
                raise CedarError(f"{n[1]}() takes one argument")
            return call_extn(n[1], args[0])
        if tag == "method":
            return self.method(self.ev(n[1]), n[2], [self.ev(a) for a in n[3]])
        raise AssertionError(tag)

    def rel(self, op, a, b):
        if op == "==":
            return ceq(a, b)
        if op == "!=":
            return not ceq(a, b)
        if op == "in":
            return self.in_(a, b)
        ta, tb = tname(a), tname(b)
        if ta != tb or ta not in ("long", "datetime", "duration"):
            raise CedarError(f"{op} on {ta} and {tb}")
        x, y = (a, b) if ta == "long" else (a.ms, b.ms)
        return {"<": x < y, "<=": x <= y, ">": x > y, ">=": x >= y}[op]

    def method(self, recv, name, args):
        t = tname(recv)
        if t == "set" and name in ("contains", "containsAll", "containsAny"):
            if len(args) != 1:
                raise CedarError(f"{name} takes one argument")
            if name == "contains":
                return recv.has(args[0])
            other = _want(args[0], "set", name)
            if name == "containsAll":
                return all(recv.has(x) for x in other.items)
            return any(recv.has(x) for x in other.items)
        if t == "set" and name == "isEmpty" and not args:
            return not recv.items
        if t == "datetime":
            if name == "offset" and len(args) == 1:
                return DateTime(_i64(recv.ms + _want(args[0], "duration", "offset").ms))
            if name == "durationSince" and len(args) == 1:
                return Duration(_i64(recv.ms - _want(args[0], "datetime", "durationSince").ms))
            if name == "toDate" and not args:
                return DateTime(recv.ms - recv.ms % MS_PER_DAY)
            if name == "toTime" and not args:
                return Duration(recv.ms % MS_PER_DAY)
        if t == "duration" and not args:
            div = {"toMilliseconds": 1, "toSeconds": 1000, "toMinutes": 60_000,
                   "toHours": 3_600_000, "toDays": MS_PER_DAY}.get(name)
            if div:
                q = abs(recv.ms) // div  # Rust integer division truncates toward zero
                return -q if recv.ms < 0 else q
        raise CedarError(f"no method {name} on {t}")


def _like(s: str, pat: list) -> bool:
    rx = "".join(".*" if c is None else re.escape(c) for c in pat)
    return re.fullmatch(rx, s, re.DOTALL) is not None


# ------------------------------------------------------------------ policy set

def _has_slot(p) -> bool:
    def ref_slot(r):
        return r is not None and r[0] == "slot"
    return any(ref_slot(el[-1]) for el in p["scope"] if el[0] in ("==", "in", "is_in"))


def instantiate(policy_text: str, linked: list) -> list:
    """Return the evaluable policies: static ones plus one instance per template link."""
    parsed = parse_policies(policy_text)
    by_id, out = {}, []
    for i, p in enumerate(parsed):
        pid = p["annotations"].get("id") or f"policy{i}"
        p["id"] = pid
        if _has_slot(p):
            by_id[pid] = p
        else:
            out.append((p, {}))
    for link in linked or []:
        tmpl = by_id[link["template_id"]]
        slots = {k: parse_uid(v) for k, v in link["args"].items()}
        out.append((dict(tmpl, id=link["link_id"]), slots))
    return out


def _scope_ok(ev: Evaluator, var: str, el) -> bool:
    v = ev.env[var]

    def ref(r):
        if r[0] == "slot":
            return ev.ev(r)
        if r[0] == "set":
            return CSet(r[1])
        return r[1]

    kind = el[0]
    if kind == "any":
        return True
    if kind == "==":
        return ceq(v, ref(el[1]))
    if kind == "in":
        return ev.in_(v, ref(el[1]))
    if kind == "is":
        return v.type == el[1]
    if kind == "is_in":
        return v.type == el[1] and ev.in_(v, ref(el[2]))
    raise AssertionError(kind)


def _satisfied(p, ev: Evaluator) -> bool:
    for var, el in zip(("principal", "action", "resource"), p["scope"]):
        if not _scope_ok(ev, var, el):
            return False
    for kind, cond in p["conds"]:
        val = ev.bool_(cond, kind)
        if val != (kind == "when"):
            return False
    return True


def _request(request: dict) -> dict:
    return {"principal": parse_uid(request["principal"]), "action": parse_uid(request["action"]),
            "resource": parse_uid(request["resource"]),
            "context": from_json(request.get("context") or {})}


def explain(policy_text, linked, entities, request, schema_extn=None) -> dict:
    store = Store(entities, schema_extn)
    req = _request(request)
    res = {"permit": [], "forbid": [], "errors": {}}
    for p, slots in instantiate(policy_text, linked):
        try:
            if _satisfied(p, Evaluator(store, req, slots)):
                res[p["effect"]].append(p["id"])
        except CedarError as err:
            res["errors"][p["id"]] = str(err)
    res["decision"] = "allow" if res["permit"] and not res["forbid"] else "deny"
    return res


def authorize(policy_text: str, linked: list, entities: list, request: dict,
              schema_extn: dict | None = None) -> bool:
    """True iff Cedar would return Allow."""
    return explain(policy_text, linked, entities, request, schema_extn)["decision"] == "allow"
