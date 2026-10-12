"""Compiled validators for the Lean service response schemas.

`lean_service_schema/*.json` is the only description of response shapes; this module
compiles it (dialect: `lean_service_schema/README.md`) into closures. The schemas
describe binding to the request and well-formedness only; the service is the semantic
authority (docs/spec/lean-service.md, threat model), so nothing here re-derives what
the runners compute. A validator is
`check(value, ctx, fuel)` and raises `Invalid` on the first violation. Tagged grammars
(formulas and terms) are checked with an explicit stack, so a generated formula of any
depth is checked without recursion; `x-fuel` limits the formulas the Lean decoders read
to 64 levels. Arbitrary JSON (echoed ids, `const`) is compared without recursion.
"""
from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import re
import reprlib

DIRECTORY = Path(__file__).resolve().parent / "lean_service_schema"
MODES = ("evaluate", "check-certificate", "order", "route", "norms", "english",
         "english.read", "english.grammar", "english.check",
         "environment", "model", "check", "identity", "parse", "graph", "readings", "readings-choices", "bundle", "family-norms",
         "soft-norms", "rights", "speech-acts", "reports", "alternatives", "risk", "risk-eval", "quantity",
         "norm-defaults", "discourse", "readings-route", "diagnose", "document", "english.question")


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
    """The request data a value is checked against: a case (rows) or the request
    (envelope); for a result, also its position, the mode's row and its case digest."""
    __slots__ = ("value", "index", "rows", "digest")

    def __init__(self, value: object, index: int | None = None, rows=None, digest: str | None = None):
        self.value, self.index, self.rows, self.digest = value, index, rows, digest


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
        if _is_grammar(schema):
            return _Grammar(self, schema, base)
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
        return _Grammar(self, {"x-tagged": table}, base)

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

    def _x_references(self, rule, schema, base):
        def check(value, ctx, fuel):
            entries = _resolve(value, rule["array"])
            members = _resolve(ctx.value, rule["in"])
            if not isinstance(entries, list) or not isinstance(members, list) or any(
                    not isinstance(entry, dict) or type(entry.get(rule["field"])) is not str or
                    not any(same_json(entry[rule["field"]], member) for member in members)
                    for entry in entries):
                _fail(f"{rule['array']} contains an unbound {rule['field']} outside the request's {rule['in']}")
        return check

    def _x_claim_nodes(self, pointers, schema, base):
        def check(value, ctx, fuel):
            for pointer in pointers:
                claims = _resolve(value, pointer)
                nodes = _resolve(ctx.value, "/document/graph/nodes")
                is_array = isinstance(claims, list)
                if isinstance(claims, dict):
                    claims = [claims]
                if not isinstance(claims, list) or not isinstance(nodes, list) or not (is_array or claims):
                    _fail(f"{pointer} contains a claim outside the request graph")
                fields = ("name", "ast", "label")
                def projection(claim):
                    return tuple(claim.get(key, _MISSING) for key in fields)
                if any(not isinstance(claim, dict) or not any(
                        isinstance(node, dict) and all(same_json(a, b) for a, b in
                            zip(projection(claim), projection(node))) for node in nodes)
                        for claim in claims):
                    _fail(f"{pointer} contains a claim outside the request graph")
        return check

    def _x_max_steps(self, limits, schema, base):
        def check(value, ctx, fuel):
            requested = _resolve(ctx.value, "/max_steps")
            limit = limits["default"] if requested is _MISSING else min(requested, limits["cap"]) if (
                _kind(requested) == "integer" and requested >= 0) else None
            if _kind(value) != "integer" or limit is None or value > limit:
                _fail("steps exceed the request's max_steps")
        return check

    def _x_background_bound(self, flag, schema, base):
        def check(value, ctx, fuel):
            predicates = _resolve(ctx.value, "/environment/vocabulary/predicates")
            constants = _resolve(ctx.value, "/environment/vocabulary/constants")
            soft = _resolve(ctx.value, "/soft_premises")
            if not isinstance(predicates, dict) or not isinstance(constants, dict):
                _fail("background exceeds what the request vocabulary generates")
            bound = 4 * len(predicates) + len(constants) * (len(constants) - 1) // 2 + (
                len(soft) if isinstance(soft, list) else 0)
            if _kind(value) != "integer" or value > bound:
                _fail("background exceeds what the request vocabulary generates")
        return check

    def _x_index(self, flag, schema, base):
        def check(value, ctx, fuel):
            if _kind(value) != "integer" or value != ctx.index:
                _fail("is not the result's position")
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

    def _x_zip_or_empty(self, rule, schema, base):
        pointer, sub = rule["of"], self.compile(rule["items"], base)

        def check(value, ctx, fuel):
            contexts = _resolve(ctx.value, pointer)
            if contexts is _MISSING:
                contexts = []
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

    def _x_count_where(self, rule, schema, base):
        where = self.compile(rule["where"], base)

        def check(value, ctx, fuel):
            elements, expected = _resolve(value, rule["array"]), _resolve(value, rule["equals"])
            if not isinstance(elements, list) or _kind(expected) != "integer" or expected != sum(
                    _valid(where, x, ctx, fuel) for x in elements):
                _fail(f"{rule['equals']} does not count {rule['array']}")
        return check

    def _x_count_presence(self, rule, schema, base):
        def check(value, ctx, fuel):
            item, expected = _resolve(value, rule["value"]), _resolve(value, rule["equals"])
            if item is _MISSING or _kind(expected) != "integer" or expected != int(item is not None):
                _fail(f"{rule['equals']} does not count the presence of {rule['value']}")
        return check

    def _x_reading_plan(self, flag, schema, base):
        """Bind a Lean choice plan to the submitted set sizes and coupling IDs.

        Completeness and compatibility are Lean decisions. This checks only
        that every returned index, label and count can name request data.
        """
        def check(value, ctx, fuel):
            case = ctx.value
            sets, couplings, limit = case.get("set_meta"), case.get("couplings"), case.get("limit")
            if (not isinstance(sets, list) or not isinstance(couplings, list)
                    or _kind(limit) != "integer" or limit < 0):
                _fail("invalid readings plan request")
            sizes = []
            for reading_set in sets:
                if (not isinstance(reading_set, dict) or type(reading_set.get("id")) is not str
                        or type(reading_set.get("unit", reading_set["id"])) is not str
                        or not isinstance(reading_set.get("readings"), list)):
                    _fail("invalid reading set in the request")
                sizes.append(len(reading_set["readings"]))
            if any(not isinstance(c, dict) or type(c.get("id")) is not str for c in couplings):
                _fail("invalid coupling in the request")
            if value["route"] == "enumerate":
                choices = value["choices"]
                if not choices or len(choices) > limit or len({tuple(choice) for choice in choices}) != len(choices):
                    _fail("extra or repeated choice")
                for choice in choices:
                    if (len(choice) != len(sizes) or any(_kind(index) != "integer" or index < 0
                            or index >= size for index, size in zip(choice, sizes))):
                        _fail("choice index is not in the request")
                if value["conditional_on"] != ["coupling:" + c["id"] for c in couplings]:
                    _fail("coupling labels are not in the request")
            else:
                product = 1
                for size in sizes:
                    product *= size
                if (value["budget"]["max_choices"] != limit or
                        not limit < value["choice_count"] <= product):
                    _fail("choice count is not bound to the request")
                units = {s.get("unit", s.get("id")) for s in sets}
                if any(unit not in units for unit in value["units"]):
                    _fail("open unit is not in the request")
        return check

    def _x_rows(self, bound, schema, base):
        sub = self.compile(bound, base)

        def check(value, ctx, fuel):
            cases, digests = _resolve(ctx.value, "/cases"), _resolve(ctx.value, "/digests")
            if (not isinstance(value, list) or not isinstance(cases, list) or not isinstance(digests, list)
                    or not len(value) == len(cases) == len(digests)):
                _fail("one result per case")
            for index, (result, case, digest) in enumerate(zip(value, cases, digests)):
                try:
                    sub(result, Context(case, index, ctx.rows, digest), {})
                except Invalid as exc:
                    raise Invalid(f"result {index}: {exc}") from None
        return check

    def _x_digest(self, flag, schema, base):
        def check(value, ctx, fuel):
            if not isinstance(value, str) or value != ctx.digest:
                _fail("is not the digest of the result's case")
        return check

    def _x_row(self, flag, schema, base):
        def check(value, ctx, fuel):
            ctx.rows(value, Context(ctx.value, ctx.index), {})
        return check


_ORDER = ("$ref", "type", "enum", "const", "pattern", "minLength", "maxLength", "minimum", "required",
          "properties", "additionalProperties", "prefixItems", "items", "minItems", "maxItems",
          "contains", "anyOf", "allOf", "not", "if", "x-tagged", "x-echo", "x-equals", "x-length",
          "x-count", "x-references", "x-claim-nodes", "x-max-steps", "x-background-bound",
          "x-index", "x-digest", "x-zip", "x-zip-or-empty", "x-case",
          "x-select", "x-count-where", "x-count-presence", "x-reading-plan", "x-rows",
          "x-row")
_KEYWORDS = frozenset(_ORDER) | {"then", "else", "$defs", "$comment", "$id", "x-fuel"}


def _valid(check, value, ctx, fuel) -> bool:
    try:
        check(value, ctx, fuel)
        return True
    except Invalid:
        return False


_SHORT = reprlib.Repr(maxlevel=3, maxlist=4, maxdict=4, maxstring=40, maxother=40)


def _short(value: object) -> str:
    """A bounded rendering: `reprlib` stops at depth 3, so a deep value never recurses."""
    text = _SHORT.repr(value)
    return text if len(text) <= 60 else text[:57] + "..."


_GRAMMAR_KEYS = frozenset({"x-tagged", "x-fuel", "$comment"})


def _is_grammar(schema: object) -> bool:
    """A tagged grammar: `x-tagged`, optionally with `x-fuel`, and nothing else."""
    return isinstance(schema, dict) and "x-tagged" in schema and set(schema) <= _GRAMMAR_KEYS


class _Grammar:
    """A tagged grammar checked with an explicit stack. An argument whose schema is a
    `$ref` to a grammar is pushed rather than called, so a formula of any depth is
    checked without Python recursion; `x-fuel` counts the entries as before."""

    def __init__(self, compiler: Compiler, schema: dict, base: str):
        rule = schema.get("x-fuel")
        self.counter = None if rule is None else compiler.counters.setdefault(rule["counter"], len(compiler.counters))
        self.limit = None if rule is None else rule["limit"]
        self.table = {tag: [self._slot(compiler, sub, base) for sub in slots]
                      for tag, slots in schema["x-tagged"].items()}

    @staticmethod
    def _slot(compiler: Compiler, sub: object, base: str):
        if isinstance(sub, dict) and set(sub) - {"$comment"} == {"$ref"}:
            name, _, pointer = sub["$ref"].partition("#")
            if _is_grammar(_resolve(compiler.documents.get(name or base, {}), pointer)):
                return compiler.ref(base, sub["$ref"])  # a cell: its grammar is pushed
        return compiler.compile(sub, base)

    def __call__(self, value, ctx, fuel):
        pending = [(self, value, fuel)]
        while pending:
            grammar, value, fuel = pending.pop()
            if grammar.counter is not None:
                used = fuel.get(grammar.counter, 0) + 1
                if used > grammar.limit:
                    _fail(f"nesting exceeds the Lean decoder fuel {grammar.limit}")
                fuel = {**fuel, grammar.counter: used}
            if not isinstance(value, list) or not value or not isinstance(value[0], str):
                _fail(f"expected a tagged array, got {_short(value)}")
            slots = grammar.table.get(value[0])
            if slots is None:
                _fail(f"unknown tag {_short(value[0])}")
            if len(value) != len(slots) + 1:
                _fail(f"{value[0]} takes {len(slots)} arguments")
            for element, slot in zip(value[1:], slots):
                if isinstance(slot, list):
                    pending.append((slot[0], element, fuel))
                else:
                    slot(element, ctx, fuel)


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
    (`{"id", "mode", "cases", "digests", "bytes"}`)."""
    RESPONSE[0](response, Context(request, rows=ROWS[mode][0]), {})
