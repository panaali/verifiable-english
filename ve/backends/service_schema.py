"""Compiled validators for the Lean service response schemas.

`lean_service_schema/*.json` is the only description of response shapes; this module
compiles it (dialect: `lean_service_schema/README.md`) into closures. A validator is
`check(value, ctx, fuel)` and raises `Invalid` on the first violation. Recursion is
bounded by the schemas' `x-fuel` limits (at most 64 formula and 64 term levels), and
arbitrary JSON (echoed ids, `const`) is compared without recursion.
"""
from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import re

DIRECTORY = Path(__file__).resolve().parent / "lean_service_schema"
MODES = ("evaluate", "check-certificate", "order", "route", "norms", "english",
         "environment", "model", "identity")


class Invalid(Exception):
    """The value is not valid under the schema."""


class SchemaError(Exception):
    """A schema file uses something outside the dialect."""


def same_json(left: object, right: object) -> bool:
    """JSON equality without Python's bool/int or int/float coercion, and without recursion."""
    pending = [(left, right)]
    while pending:
        a, b = pending.pop()
        if _kind(a) != _kind(b):
            return False
        if isinstance(a, dict):
            if a.keys() != b.keys():
                return False
            pending.extend((value, b[key]) for key, value in a.items())
        elif isinstance(a, list):
            if len(a) != len(b):
                return False
            pending.extend(zip(a, b))
        elif a != b:
            return False
    return True


def _kind(value: object) -> str:
    if value is None:
        return "null"
    if type(value) is bool:
        return "boolean"
    if type(value) is int or isinstance(value, Decimal) and value == value.to_integral_value():
        return "integer"
    if isinstance(value, (float, Decimal)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "other"


_MISSING = object()


def _resolve(root: object, pointer: str) -> object:
    """The value at a JSON pointer; `*` maps the rest over an array. `_MISSING` if absent."""
    tokens = [t.replace("~1", "/").replace("~0", "~") for t in pointer.split("/")[1:]] if pointer else []

    def walk(node, i):
        while i < len(tokens):
            token = tokens[i]
            if token == "*":
                if not isinstance(node, list):
                    return _MISSING
                out = []
                for element in node:
                    value = walk(element, i + 1)
                    if value is _MISSING:
                        return _MISSING
                    out.append(value)
                return out
            if not isinstance(node, dict) or token not in node:
                return _MISSING
            node = node[token]
            i += 1
        return node

    return walk(root, 0)


class Context:
    """The request data a value is checked against: a case (rows) or the request (envelope)."""
    __slots__ = ("value", "index", "rows")

    def __init__(self, value: object, index: int | None = None, rows=None):
        self.value, self.index, self.rows = value, index, rows


def _fail(message: str):
    raise Invalid(message)


class Compiler:
    """Loads every schema file and compiles schemas on demand, sharing `$ref` targets."""

    def __init__(self, directory: Path = DIRECTORY):
        self.documents = {path.name: json.loads(path.read_text()) for path in sorted(directory.glob("*.json"))}
        self.counters: dict[str, int] = {}
        self._compiled: dict[tuple[str, str], list] = {}

    def ref(self, base: str, reference: str):
        name, _, pointer = reference.partition("#")
        name = name or base
        if name not in self.documents:
            raise SchemaError(f"unknown schema file {name}")
        key = (name, pointer)
        cell = self._compiled.get(key)
        if cell is None:
            cell = self._compiled[key] = [None]
            target = _resolve(self.documents[name], pointer)
            if target is _MISSING:
                raise SchemaError(f"unresolved $ref {reference} in {base}")
            cell[0] = self.compile(target, name)
        return cell

    def compile(self, schema: object, base: str):
        if schema is True:
            return lambda value, ctx, fuel: None
        if schema is False:
            return lambda value, ctx, fuel: _fail("no value is valid here")
        if not isinstance(schema, dict):
            raise SchemaError(f"schema must be an object or boolean: {schema!r}")
        unknown = set(schema) - _KEYWORDS
        if unknown:
            raise SchemaError(f"unsupported keywords {sorted(unknown)} in {base}")
        checks = []
        for keyword in _ORDER:
            if keyword in schema:
                check = getattr(self, "_" + keyword.replace("-", "_").lstrip("$"))(schema[keyword], schema, base)
                if check is not None:
                    checks.append(check)
        fuel_rule = schema.get("x-fuel")
        if fuel_rule is not None:
            counter = self.counters.setdefault(fuel_rule["counter"], len(self.counters))
            limit = fuel_rule["limit"]

            def fuelled(value, ctx, fuel):
                used = fuel.get(counter, 0) + 1
                if used > limit:
                    _fail(f"nesting exceeds the Lean decoder fuel {limit}")
                fuel = {**fuel, counter: used}
                for check in checks:
                    check(value, ctx, fuel)
            return fuelled
        if len(checks) == 1:
            return checks[0]

        def conjunction(value, ctx, fuel):
            for check in checks:
                check(value, ctx, fuel)
        return conjunction

    # Standard keywords

    def _ref(self, reference, schema, base):
        cell = self.ref(base, reference)
        return lambda value, ctx, fuel: cell[0](value, ctx, fuel)

    def _type(self, names, schema, base):
        allowed = frozenset([names] if isinstance(names, str) else names)

        def check(value, ctx, fuel):
            if _kind(value) not in allowed:
                _fail(f"expected {'/'.join(sorted(allowed))}")
        return check

    def _enum(self, options, schema, base):
        def check(value, ctx, fuel):
            if not any(same_json(value, option) for option in options):
                _fail(f"{_short(value)} is not one of {options}")
        return check

    def _const(self, expected, schema, base):
        def check(value, ctx, fuel):
            if not same_json(value, expected):
                _fail(f"{_short(value)} is not {expected!r}")
        return check

    def _pattern(self, pattern, schema, base):
        compiled = re.compile(pattern, re.DOTALL)

        def check(value, ctx, fuel):
            if isinstance(value, str) and compiled.fullmatch(value) is None:
                _fail(f"{_short(value)} does not match {pattern}")
        return check

    def _minLength(self, n, schema, base):
        def check(value, ctx, fuel):
            if isinstance(value, str) and len(value) < n:
                _fail(f"string shorter than {n}")
        return check

    def _maxLength(self, n, schema, base):
        def check(value, ctx, fuel):
            if isinstance(value, str) and len(value) > n:
                _fail(f"string longer than {n}")
        return check

    def _minimum(self, n, schema, base):
        def check(value, ctx, fuel):
            if _kind(value) in ("integer", "number") and value < n:
                _fail(f"{value} is below {n}")
        return check

    def _required(self, names, schema, base):
        def check(value, ctx, fuel):
            if isinstance(value, dict):
                for name in names:
                    if name not in value:
                        _fail(f"missing field {name}")
        return check

    def _properties(self, properties, schema, base):
        compiled = [(name, self.compile(sub, base)) for name, sub in properties.items()]

        def check(value, ctx, fuel):
            if isinstance(value, dict):
                for name, sub in compiled:
                    if name in value:
                        try:
                            sub(value[name], ctx, fuel)
                        except Invalid as exc:
                            raise Invalid(f"{name}: {exc}") from None
        return check

    def _additionalProperties(self, extra, schema, base):
        known = frozenset(schema.get("properties", ()))
        sub = None if extra is False else self.compile(extra, base)

        def check(value, ctx, fuel):
            if isinstance(value, dict):
                for name in value:
                    if name not in known:
                        if sub is None:
                            _fail(f"unexpected field {name}")
                        try:
                            sub(value[name], ctx, fuel)
                        except Invalid as exc:
                            raise Invalid(f"{name}: {exc}") from None
        return check

    def _prefixItems(self, items, schema, base):
        compiled = [self.compile(sub, base) for sub in items]

        def check(value, ctx, fuel):
            if isinstance(value, list):
                for i, (element, sub) in enumerate(zip(value, compiled)):
                    try:
                        sub(element, ctx, fuel)
                    except Invalid as exc:
                        raise Invalid(f"[{i}]: {exc}") from None
        return check

    def _items(self, items, schema, base):
        sub = self.compile(items, base)
        skip = len(schema.get("prefixItems", ()))

        def check(value, ctx, fuel):
            if isinstance(value, list):
                for i in range(skip, len(value)):
                    try:
                        sub(value[i], ctx, fuel)
                    except Invalid as exc:
                        raise Invalid(f"[{i}]: {exc}") from None
        return check

    def _minItems(self, n, schema, base):
        def check(value, ctx, fuel):
            if isinstance(value, list) and len(value) < n:
                _fail(f"fewer than {n} elements")
        return check

    def _maxItems(self, n, schema, base):
        def check(value, ctx, fuel):
            if isinstance(value, list) and len(value) > n:
                _fail(f"more than {n} elements")
        return check

    def _contains(self, sub_schema, schema, base):
        sub = self.compile(sub_schema, base)

        def check(value, ctx, fuel):
            if isinstance(value, list) and not any(_valid(sub, x, ctx, fuel) for x in value):
                _fail("no element is valid")
        return check

    def _anyOf(self, branches, schema, base):
        compiled = [self.compile(sub, base) for sub in branches]

        def check(value, ctx, fuel):
            reasons = []
            for sub in compiled:
                try:
                    sub(value, ctx, fuel)
                    return
                except Invalid as exc:
                    reasons.append(str(exc))
            _fail("no alternative is valid (" + "; ".join(reasons) + ")")
        return check

    def _allOf(self, branches, schema, base):
        compiled = [self.compile(sub, base) for sub in branches]

        def check(value, ctx, fuel):
            for sub in compiled:
                sub(value, ctx, fuel)
        return check

    def _not(self, sub_schema, schema, base):
        sub = self.compile(sub_schema, base)

        def check(value, ctx, fuel):
            if _valid(sub, value, ctx, fuel):
                _fail("a forbidden form is present")
        return check

    def _if(self, condition, schema, base):
        test = self.compile(condition, base)
        then = self.compile(schema.get("then", True), base)
        otherwise = self.compile(schema.get("else", True), base)

        def check(value, ctx, fuel):
            (then if _valid(test, value, ctx, fuel) else otherwise)(value, ctx, fuel)
        return check

    # Extensions (lean_service_schema/README.md)

    def _x_tagged(self, table, schema, base):
        compiled = {tag: [self.compile(sub, base) for sub in slots] for tag, slots in table.items()}

        def check(value, ctx, fuel):
            if not isinstance(value, list) or not value or not isinstance(value[0], str):
                _fail(f"expected a tagged array, got {_short(value)}")
            slots = compiled.get(value[0])
            if slots is None:
                _fail(f"unknown tag {_short(value[0])}")
            if len(value) != len(slots) + 1:
                _fail(f"{value[0]} takes {len(slots)} arguments")
            for element, sub in zip(value[1:], slots):
                sub(element, ctx, fuel)
        return check

    def _x_fuel(self, rule, schema, base):
        return None  # applied by `compile` around every other keyword

    def _x_echo(self, pointer, schema, base):
        def check(value, ctx, fuel):
            expected = _resolve(ctx.value, pointer)
            if not same_json(value, None if expected is _MISSING else expected):
                _fail(f"does not echo the request's {pointer}")
        return check

    def _x_equals(self, pointer, schema, base):
        def check(value, ctx, fuel):
            expected = _resolve(ctx.value, pointer)
            if expected is _MISSING or not same_json(value, expected):
                _fail(f"does not equal the request's {pointer}")
        return check

    def _x_length(self, pointer, schema, base):
        def check(value, ctx, fuel):
            expected = _resolve(ctx.value, pointer)
            if not isinstance(expected, list) or not isinstance(value, list) or len(value) != len(expected):
                _fail(f"length differs from the request's {pointer}")
        return check

    def _x_count(self, pointer, schema, base):
        def check(value, ctx, fuel):
            expected = _resolve(ctx.value, pointer)
            if not isinstance(expected, list) or _kind(value) != "integer" or value != len(expected):
                _fail(f"is not the number of the request's {pointer}")
        return check

    def _x_index(self, flag, schema, base):
        def check(value, ctx, fuel):
            if _kind(value) != "integer" or value != ctx.index:
                _fail("is not the result's position")
        return check

    def _x_member(self, rule, schema, base):
        pointer, keys = rule["of"], tuple(rule["keys"])
        where = self.compile(rule.get("where", True), base)

        def project(x):
            return {k: x[k] for k in keys if k in x} if isinstance(x, dict) else _MISSING

        def check(value, ctx, fuel):
            elements = _resolve(ctx.value, pointer)
            mine = project(value)
            if (not isinstance(elements, list) or mine is _MISSING
                    or not any(same_json(mine, project(x)) and _valid(where, x, ctx, {})
                               for x in elements if isinstance(x, dict))):
                _fail(f"is not one of the request's {pointer}")
        return check

    def _x_dependency_order(self, pointer, schema, base):
        def check(value, ctx, fuel):
            nodes = _resolve(ctx.value, pointer)
            if not _verify_order(nodes, value):
                _fail(f"is not a dependency order of the request's {pointer}")
        return check

    def _x_zip(self, rule, schema, base):
        pointer, sub = rule["of"], self.compile(rule["items"], base)

        def check(value, ctx, fuel):
            contexts = _resolve(ctx.value, pointer)
            if not isinstance(value, list) or not isinstance(contexts, list) or len(value) != len(contexts):
                _fail(f"not one element per element of the request's {pointer}")
            for i, (element, context) in enumerate(zip(value, contexts)):
                try:
                    sub(element, Context(context, i), fuel)
                except Invalid as exc:
                    raise Invalid(f"[{i}]: {exc}") from None
        return check

    def _x_case(self, sub_schema, schema, base):
        sub = self.compile(sub_schema, base)
        return lambda value, ctx, fuel: sub(ctx.value, ctx, {})

    def _x_select(self, entries, schema, base):
        compiled = [(self.compile(e["when"], base), self.compile(e["then"], base)) for e in entries]

        def check(value, ctx, fuel):
            for when, then in compiled:
                if _valid(when, ctx.value, ctx, {}):
                    then(value, ctx, fuel)
                    return
            _fail("no result is possible for this request")
        return check

    def _x_same(self, pairs, schema, base):
        def check(value, ctx, fuel):
            for p, q in pairs:
                a, b = _resolve(value, p), _resolve(value, q)
                if a is _MISSING or b is _MISSING or not same_json(a, b):
                    _fail(f"{p} differs from {q}")
        return check

    def _x_same_length(self, pairs, schema, base):
        def check(value, ctx, fuel):
            for p, q in pairs:
                a, b = _resolve(value, p), _resolve(value, q)
                if not isinstance(a, list) or not isinstance(b, list) or len(a) != len(b):
                    _fail(f"{p} and {q} differ in length")
        return check

    def _x_in(self, pairs, schema, base):
        def check(value, ctx, fuel):
            for p, q in pairs:
                a, b = _resolve(value, p), _resolve(value, q)
                if a is _MISSING or not isinstance(b, list) or not any(same_json(a, x) for x in b):
                    _fail(f"{p} is not in {q}")
        return check

    def _x_capture(self, rule, schema, base):
        compiled = re.compile(rule["pattern"], re.DOTALL)

        def check(value, ctx, fuel):
            source, target = _resolve(value, rule["source"]), _resolve(value, rule["target"])
            match = compiled.match(source) if isinstance(source, str) else None
            if match is None or target is _MISSING or not same_json(target, match.group(1)):
                _fail(f"{rule['target']} is not captured from {rule['source']}")
        return check

    def _x_count_where(self, rule, schema, base):
        where = self.compile(rule["where"], base)

        def check(value, ctx, fuel):
            elements, expected = _resolve(value, rule["array"]), _resolve(value, rule["equals"])
            if not isinstance(elements, list) or _kind(expected) != "integer" or expected != sum(
                    _valid(where, x, ctx, fuel) for x in elements):
                _fail(f"{rule['equals']} does not count {rule['array']}")
        return check

    def _x_rows(self, flag, schema, base):
        def check(value, ctx, fuel):
            cases = _resolve(ctx.value, "/cases")
            if not isinstance(value, list) or not isinstance(cases, list) or len(value) != len(cases):
                _fail("one result per case")
            row = ctx.rows
            for index, (result, case) in enumerate(zip(value, cases)):
                try:
                    row(result, Context(case, index), {})
                except Invalid as exc:
                    raise Invalid(f"result {index}: {exc}") from None
        return check


_ORDER = ("$ref", "type", "enum", "const", "pattern", "minLength", "maxLength", "minimum", "required",
          "properties", "additionalProperties", "prefixItems", "items", "minItems", "maxItems",
          "contains", "anyOf", "allOf", "not", "if", "x-tagged", "x-echo", "x-equals", "x-length",
          "x-count", "x-index", "x-member", "x-dependency-order", "x-zip", "x-case", "x-select", "x-same",
          "x-same-length", "x-in", "x-capture", "x-count-where", "x-rows")
_KEYWORDS = frozenset(_ORDER) | {"then", "else", "$defs", "$comment", "$id", "x-fuel"}


def _valid(check, value, ctx, fuel) -> bool:
    try:
        check(value, ctx, fuel)
        return True
    except Invalid:
        return False


def _short(value: object) -> str:
    text = repr(value)
    return text if len(text) <= 60 else text[:57] + "..."


def _verify_order(nodes: object, order: object) -> bool:
    """Route.Wire.decodeNodes, then Route.dependencyOrder's success conditions: unique
    names and `verifyOrder` (a permutation with every dependency strictly earlier)."""
    if not isinstance(nodes, list) or len(nodes) > 256 or not isinstance(order, list):
        return False
    names, mentions = [], []
    for node in nodes:
        if (not isinstance(node, dict) or set(node) != {"name", "mentions"}
                or not isinstance(node["name"], str) or not isinstance(node["mentions"], list)
                or not all(isinstance(m, str) for m in node["mentions"])):
            return False
        names.append(node["name"])
        mentions.append(node["mentions"])
    if len(set(names)) != len(names) or not all(isinstance(x, str) for x in order):
        return False
    if len(set(order)) != len(order) or set(order) != set(names):
        return False
    position = {name: i for i, name in enumerate(order)}
    return all(position[m] < position[name]
               for name, ms in zip(names, mentions) for m in ms if m in position)


_compiler = Compiler()
ROWS = {mode: _compiler.ref(f"{mode}.json", "#/row") for mode in MODES}
RESPONSE = _compiler.ref("envelope.json", "#/response")
HANDSHAKE = _compiler.ref("envelope.json", "#/handshake")


def check_handshake(handshake: object) -> None:
    """Raise `Invalid` unless `handshake` is a first line this client can use."""
    HANDSHAKE[0](handshake, Context(None), {})


def check_row(mode: str, row: object, case: object, index: int) -> None:
    """Raise `Invalid` unless `row` is a possible result for `case` at `index`."""
    ROWS[mode][0](row, Context(case, index), {})


def check_response(mode: str, response: object, request: dict) -> None:
    """Raise `Invalid` unless `response` is a possible response line for `request`
    (`{"id", "mode", "cases", "bytes"}`)."""
    RESPONSE[0](response, Context(request, rows=ROWS[mode][0]), {})
