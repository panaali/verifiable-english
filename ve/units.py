"""W6 annotated quantities. Admission precedes erasure into the frozen integer AST.

Python gives early diagnostics and regeneration; the Lean `quantity` route
(`VE.Time`) is the authority for admission, erasure and certificate binding.
"""
from __future__ import annotations

from datetime import date, timedelta
import re

from .ast import decimal_from_wire, MAX_NUMERAL_CHARS
from .environment import INT_SORT, STRING_SORT, valid_identifier
from .errors import ResourceLimit, TypeMismatch, UnsupportedProfile, VEError
from .wire import canonical_json, digest, require_fields

SCHEMA = "ve-units@1"
DIMENSIONLESS = "dimensionless"
DAY = {"scale": "1", "display": {"kind": "iso_date"}}
ELAPSED_DAY = {"scale": "1", "display": {"kind": "decimal", "label": "days"}}
_DATE_MAX = (date(9999, 12, 31) - date(1970, 1, 1)).days
_DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\Z", re.ASCII)
_ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z", re.ASCII)
_SLOT = re.compile(r"0|[1-9][0-9]*\Z", re.ASCII)
# Exactly the characters for which Python's str.isspace() holds, listed so that
# Rust and Lean check the same display-string rule.
SPACES = frozenset(map(chr, (9, 10, 11, 12, 13, 28, 29, 30, 31, 32, 0x85, 0xA0, 0x1680,
                             *range(0x2000, 0x200B), 0x2028, 0x2029, 0x202F, 0x205F, 0x3000)))
# Characters a decimal amount can begin or end with. A display affix must not
# touch the amount with one of these, so an affixed literal is never also a
# bare decimal, a date, or a literal with an affix on the other side.
_AMOUNT_CHARS = frozenset("-.0123456789")
POINTS_SUFFIX = " percentage points"
W6_PROFILES = (("order@0", "relational-fol@0", "time@0"),
               ("documents@1", "order@0", "relational-fol@0", "time@0"))
NUMBERS2 = "$int quantification requires the missing numbers2 route"


def _fields(value, required, optional=(), path=""):
    if type(value) is not dict:
        raise VEError(f"Invalid object {path}")
    require_fields(value, set(required) | (set(value) & set(optional)), path=path)


def validate_units(schema, raw):
    if schema != SCHEMA:
        raise UnsupportedProfile(f"Unsupported unit schema {schema}")
    if type(raw) is not dict:
        raise VEError("units must be an object")
    if len(raw) > 64:
        raise ResourceLimit("At most 64 unit tags")
    for tag, record in raw.items():
        if not valid_identifier(tag) or tag == DIMENSIONLESS:
            raise VEError(f"Invalid unit tag {tag!r}")
        _fields(record, ("scale", "display"), path=f"/units/{tag}")
        scale = decimal_from_wire(record["scale"])
        if scale <= 0 or str(scale)[0] != "1" or set(str(scale)[1:]) - {"0"}:
            raise VEError(f"UnitScale({tag}): expected a positive power of ten")
        display = record["display"]
        if type(display) is not dict or "kind" not in display:
            raise VEError(f"Invalid display for {tag}")
        kind = display["kind"]
        if kind == "percent":
            _fields(display, ("kind",))
        elif kind == "money":
            _fields(display, ("kind", "currency"), ("input_symbol",))
            currency = display["currency"]
            if type(currency) is not str or not re.fullmatch(r"[A-Z]{3}", currency):
                raise VEError(f"Invalid currency for {tag}")
            if "input_symbol" in display:
                display_string(display["input_symbol"], trailing_space=True)
        elif kind == "decimal":
            _fields(display, ("kind", "label"), ("placement",))
            display_string(display["label"])
            if display.get("placement", "suffix") not in ("prefix", "suffix"):
                raise VEError(f"Invalid placement for {tag}")
        elif kind == "iso_date":
            _fields(display, ("kind",))
            if tag != "day" or scale != 1:
                raise VEError("iso_date requires day at scale 1")
        else:
            raise VEError(f"Unknown display kind {kind}")
        if tag == "day" and record != DAY:
            raise VEError("Reserved unit day has a fixed declaration")
        if tag == "elapsed_day" and record != ELAPSED_DAY:
            raise VEError("Reserved unit elapsed_day has a fixed declaration")
    check_display_injective(raw)
    return raw


def display_string(s, *, trailing_space=False):
    """Nonempty words of non-space characters joined by single spaces.

    An input symbol may end in one space ("EUR "). Other whitespace, and
    spacing the sentence normalizer would rewrite, is rejected."""
    if type(s) is not str or not s:
        raise VEError("Display string must be nonempty")
    if len(s) > 256:
        raise ResourceLimit("Display string exceeds 256 characters")
    words = s.split(" ")
    if trailing_space and len(words) > 1 and words[-1] == "":
        words = words[:-1]
    if any(not word or SPACES & set(word) for word in words):
        raise VEError(f"Display string {s!r} must be whitespace-normalized")
    return s


def display_affixes(units):
    """Every enabled literal affix as (side, text, tag), including input aliases.

    A literal is an amount with exactly one affix: a prefix before it or a suffix
    after it. The percentage-point wording is an enabled suffix alias of the
    percent tag."""
    forms = []
    for tag, record in units.items():
        display = record["display"]
        kind = display["kind"]
        if kind == "percent":
            forms += [("suffix", "%", tag), ("suffix", POINTS_SUFFIX, tag)]
        elif kind == "money":
            forms.append(("prefix", display["currency"] + " ", tag))
            if "input_symbol" in display:
                forms.append(("prefix", display["input_symbol"], tag))
        elif kind == "decimal":
            if display.get("placement", "suffix") == "prefix":
                forms.append(("prefix", display["label"] + " ", tag))
            else:
                forms.append(("suffix", " " + display["label"], tag))
    return forms


def check_display_injective(units):
    """Reject any two enabled literal forms that can spell one string.

    Canonical displays and input aliases are one class: no affix may extend
    another on the same side, even for the same tag, and no affix may touch the
    amount with a digit, sign or point. Then every literal string has at most one
    (tag, amount) reading; bare decimals and dates carry no affix at all."""
    forms = display_affixes(units)
    for side, text, _ in forms:
        edge = text[0] if side == "prefix" else text[-1]
        if edge in _AMOUNT_CHARS:
            raise VEError(f"DisplayCollision({text!r} touches the amount)")
    for i, (side, text, _) in enumerate(forms):
        for other_side, other, _ in forms[i + 1:]:
            if side != other_side:
                continue
            extends = (text.startswith(other) or other.startswith(text) if side == "prefix"
                       else text.endswith(other) or other.endswith(text))
            if extends:
                raise VEError(f"DisplayCollision({text!r}, {other!r})")


def validate_tag(tag, units):
    if type(tag) is not str or (tag != DIMENSIONLESS and (units is None or tag not in units)):
        raise VEError(f"UnknownUnit({tag})")
    return tag


def validate_slot_units(raw, args, units):
    if type(raw) is not dict:
        raise VEError("argument_units must be an object")
    result = {}
    for slot, tag in raw.items():
        if type(slot) is not str or not _SLOT.fullmatch(slot) or int(slot) >= len(args):
            raise VEError(f"Invalid argument unit slot {slot}")
        if args[int(slot)] != INT_SORT:
            raise VEError(f"Unit on non-integer slot {slot}")
        result[slot] = validate_tag(tag, units)
    return result


def validate_extension(profiles, units, sorts, constants):
    """Route-level W6 environment conditions, after the vocabulary is decoded."""
    if tuple(profiles) not in W6_PROFILES:
        raise UnsupportedProfile("ve-units@1 requires exactly order@0, relational-fol@0 and "
                                 "time@0, optionally with documents@1")
    for tag in (DIMENSIONLESS, *units):
        if tag in sorts:
            raise VEError(f"Unit tag {tag} collides with a declared sort")
    if any(decl.sort == STRING_SORT for decl in constants.values()):
        raise UnsupportedProfile("$string literals are not admitted with ve-units@1")


def decimal_exact(text, tag, env):
    validate_tag(tag, env.units)
    if type(text) is str and len(text) > MAX_NUMERAL_CHARS:
        raise ResourceLimit(f"Decimal literal exceeds {MAX_NUMERAL_CHARS} characters")
    if type(text) is not str or not _DECIMAL.fullmatch(text):
        raise VEError(f"Invalid decimal literal {text!r}")
    scale = 1 if tag == DIMENSIONLESS else int(env.units[tag]["scale"])
    sign = -1 if text.startswith("-") else 1
    digits = text.lstrip("-").split(".")
    places = len(digits[1]) if len(digits) == 2 else 0
    numerator = sign * int("".join(digits)) * scale
    divisor = 10 ** places
    if numerator % divisor:
        raise VEError(f"UnitPrecision({tag}, scale={scale})")
    coordinate = numerator // divisor
    if len(str(coordinate)) > MAX_NUMERAL_CHARS:
        raise ResourceLimit("Lowered integer exceeds 40 characters")
    return coordinate


def day_number(iso):
    if type(iso) is not str or not _ISO.fullmatch(iso):
        raise VEError(f"InvalidDate({iso})")
    try:
        d = date.fromisoformat(iso)
    except ValueError as exc:
        raise VEError(f"InvalidDate({iso})") from exc
    n = (d - date(1970, 1, 1)).days
    if n < 0:
        raise VEError(f"DateRange({iso})")
    return n


def iso_date(coordinate):
    if type(coordinate) is not int or not 0 <= coordinate <= _DATE_MAX:
        raise VEError(f"DateRange({coordinate})")
    return (date(1970, 1, 1) + timedelta(days=coordinate)).isoformat()


def render_coordinate(tag, coordinate, env):
    validate_tag(tag, env.units)
    if tag == DIMENSIONLESS:
        return str(coordinate)
    record = env.units[tag]
    kind = record["display"]["kind"]
    if kind == "iso_date":
        return iso_date(coordinate)
    scale = int(record["scale"])
    precision = len(str(scale)) - 1
    amount = ("-" if coordinate < 0 else "") + str(abs(coordinate) // scale)
    if precision:
        amount += "." + str(abs(coordinate) % scale).zfill(precision)
    display = record["display"]
    if kind == "percent":
        return amount + "%"
    if kind == "money":
        return display["currency"] + " " + amount
    label = display["label"]
    return label + " " + amount if display.get("placement") == "prefix" else amount + " " + label


# Statement types keep unit tags and user sorts in separate namespaces, so a
# sort spelled like a tag is never a quantity type.
def _unit(tag):
    return ("unit", tag)


def _sort(name):
    return ("sort", name)


def _same(a, b):
    if a != b:
        if a[0] == b[0] == "unit":
            raise TypeMismatch(f"UnitMismatch({a[1]},{b[1]})")
        raise TypeMismatch(f"TypeMismatch({a[0]} {a[1]},{b[0]} {b[1]})")
    return a


def _need(node, tag, arity):
    if type(node) is not list or len(node) != arity or node[0] != tag:
        raise VEError(f"Invalid {tag} node")


_TEMPORAL = ("date_on", "date_before", "date_after", "date_no_later", "within_days",
             "shift_days", "elapsed_days")
_W6B = ("sunday", "excluded_sundays", "forall_date", "exists_date", "trace_all", "trace_some")


class _Elaborator:
    """Formula and term depth are budgeted separately (each at most 64), as in
    the frozen checker; every array node counts toward 10,000."""

    def __init__(self, env):
        if env.unit_schema != SCHEMA:
            raise UnsupportedProfile("quantities require ve-units@1")
        self.env = env
        self.nodes = 0

    def tick(self, depth):
        self.nodes += 1
        if self.nodes > 10000 or depth > 64:
            raise ResourceLimit("Quantity AST exceeds node or depth limit")

    def tag(self, tag):
        return validate_tag(tag, self.env.units)

    def term(self, node, context=(), depth=1):
        """Return (type, annotated term, erased term); context lists user sorts."""
        self.tick(depth)
        if type(node) is not list or not node or type(node[0]) is not str:
            raise VEError("Invalid quantity term")
        op, arity = node[0], len(node)
        if op == "var" and arity == 2:
            index = node[1]
            if type(index) is not int or not 0 <= index < len(context):
                raise VEError(f"Unbound variable {index!r}")
            return _sort(context[index]), node, node
        if op == "var" and arity == 3:
            raise UnsupportedProfile(NUMBERS2)
        if op == "const" and arity in (2, 3):
            name = node[-1]
            decl = self.env.constants.get(name) if type(name) is str else None
            if decl is None:
                raise VEError(f"Unknown constant {name!r}")
            if decl.sort != INT_SORT:
                if arity == 3:
                    raise TypeMismatch(f"Unit on object constant {name}")
                return _sort(decl.sort), node, node
            tag = self.tag(node[1]) if arity == 3 else DIMENSIONLESS
            _same(_unit(tag), _unit(decl.unit or DIMENSIONLESS))
            return _unit(tag), ["const", tag, name], ["const", name]
        if op in ("num", "decimal") and arity == 3 or op == "num" and arity == 2:
            tag = self.tag(node[1]) if arity == 3 else DIMENSIONLESS
            text = node[-1]
            coordinate = decimal_from_wire(text) if op == "num" else decimal_exact(text, tag, self.env)
            return _unit(tag), ["num", tag, str(coordinate)], ["num", str(coordinate)]
        if op == "date" and arity == 2:
            # The literal names the reserved tag; it must be declared like any other.
            tag = self.tag("day")
            coordinate = day_number(node[1])
            return _unit(tag), ["num", tag, str(coordinate)], ["num", str(coordinate)]
        if op in ("add", "scale") and arity in (3, 4):
            tag = self.tag(node[1]) if arity == 4 else DIMENSIONLESS
            if op == "scale":
                coefficient = decimal_from_wire(node[-2])
                found, q, core = self.term(node[-1], context, depth + 1)
                _same(_unit(tag), found)
                if tag == "day":
                    raise TypeMismatch("Calendar dates cannot be scaled")
                return _unit(tag), ["scale", tag, str(coefficient), q], ["scale", str(coefficient), core]
            left, lq, lc = self.term(node[-2], context, depth + 1)
            right, rq, rc = self.term(node[-1], context, depth + 1)
            _same(_unit(tag), _same(left, right))
            if tag == "day":
                raise TypeMismatch("Calendar dates cannot be added")
            return _unit(tag), ["add", tag, lq, rq], ["add", lc, rc]
        raise VEError(f"Invalid quantity term {op}")

    def formula(self, node, context=(), depth=1):
        self.tick(depth)
        if type(node) is not list or not node or type(node[0]) is not str:
            raise VEError("Invalid quantity formula")
        op = node[0]
        if op in ("top", "bottom") and len(node) == 1:
            return node, node
        if op in ("eq", "lt", "le") and len(node) == 3:
            lt, lq, lc = self.term(node[1], context)
            rt, rq, rc = self.term(node[2], context)
            _same(lt, rt)
            if op != "eq" and lt[0] != "unit":
                raise TypeMismatch("Order needs quantity terms")
            return [op, lq, rq], [op, lc, rc]
        if op in ("unary", "binary"):
            if len(node) != (3 if op == "unary" else 4) or type(node[1]) is not str:
                raise VEError(f"Invalid {op} arity")
            decl = self.env.predicates.get(node[1])
            args = node[2:]
            if decl is None or len(args) != len(decl.arguments):
                raise VEError(f"Unknown predicate or arity {node[1]}")
            units = decl.argument_units or {}
            terms = [self.term(t, context) for t in args]
            for i, (found, _, _) in enumerate(terms):
                sort = decl.arguments[i]
                _same(found, _unit(units.get(str(i), DIMENSIONLESS)) if sort == INT_SORT else _sort(sort))
            return [op, node[1], *(t[1] for t in terms)], [op, node[1], *(t[2] for t in terms)]
        if op == "atom":
            raise UnsupportedProfile("n-ary atoms are not admitted on the order@0 quantity route")
        if op == "not" and len(node) == 2:
            q, c = self.formula(node[1], context, depth + 1)
            return [op, q], [op, c]
        if op in ("and", "or", "implies") and len(node) == 3:
            lq, lc = self.formula(node[1], context, depth + 1)
            rq, rc = self.formula(node[2], context, depth + 1)
            return [op, lq, rq], [op, lc, rc]
        if op in ("forall", "exists"):
            if len(node) in (3, 4) and node[1] == INT_SORT:
                raise UnsupportedProfile(NUMBERS2)
            if len(node) != 3 or type(node[1]) is not str or node[1] not in self.env.sorts:
                raise VEError("Invalid quantity binder")
            q, c = self.formula(node[2], (node[1], *context), depth + 1)
            return [op, node[1], q], [op, node[1], c]
        if op in _TEMPORAL:
            return self.temporal(node, context)
        if op in _W6B:
            raise UnsupportedProfile(NUMBERS2)
        raise VEError(f"Unknown quantity formula {op}")

    def temporal(self, node, context):
        op = node[0]
        _need(node, op, 4 if op in ("within_days", "shift_days", "elapsed_days") else 3)
        a, aq, ac = self.term(node[1], context)
        b, bq, bc = self.term(node[2], context)
        day = _unit(self.tag("day"))
        _same(a, day); _same(b, day)
        guard = lambda x: ["and", ["le", ["num", "0"], x], ["le", x, ["num", str(_DATE_MAX)]]]
        both = ["and", guard(ac), guard(bc)]
        if op == "date_on": body = ["eq", ac, bc]
        elif op == "date_before": body = ["lt", ac, bc]
        elif op == "date_after": body = ["lt", bc, ac]
        elif op == "date_no_later": body = ["le", ac, bc]
        elif op == "elapsed_days":
            v, vq, vc = self.term(node[3], context)
            _same(v, _unit(self.tag("elapsed_day")))
            body = ["eq", vc, ["add", bc, ["scale", "-1", ac]]]
            return [op, aq, bq, vq], ["and", both, body]
        else:
            n = decimal_from_wire(node[3])
            if n < 0:
                raise VEError("Day offset must be nonnegative")
            upper = ["add", bc, ["num", str(n)]]
            body = (["and", ["le", bc, ac], ["le", ac, upper]] if op == "within_days"
                    else ["eq", ac, upper])
            return [op, aq, bq, str(n)], ["and", both, body]
        return [op, aq, bq], ["and", both, body]


def elaborate_quantity(env, payload):
    """Return canonical annotated payload and regenerated frozen-core formula data."""
    _fields(payload, ("format", "formula"), ("traces", "Q"))
    if payload["format"] != "ve-quantity@1":
        raise VEError("Unsupported quantity format")
    traces = payload.get("traces", [])
    if type(traces) is not list:
        raise VEError("traces must be an array")
    if traces:
        # Trace declarations exist only for trace_all/trace_some, which need
        # integer binders; Rust and Lean gate them identically.
        raise UnsupportedProfile("trace declarations require the missing numbers2 route")
    q, core = _Elaborator(env).formula(payload["formula"])
    if "Q" in payload and canonical_json(payload["Q"]) != canonical_json(q):
        raise VEError("Quantity Q differs from regenerated formula")
    # The target vocabulary has the same symbols and checker profile, with only
    # W6 declaration fields removed. The frozen checker validates regenerated
    # data in that independently identified environment.
    from .ast import formula_from_data
    formula_from_data(erased_environment(env), core)
    return {"format": "ve-quantity@1", "formula": q, "traces": []}, core


def erased_data(data):
    """The core target environment data for W6 environment data."""
    data = canonical_copy(data)
    del data["unit_schema"]
    del data["units"]
    for declaration in data["vocabulary"]["predicates"].values():
        declaration.pop("argument_units", None)
    for declaration in data["vocabulary"]["constants"].values():
        declaration.pop("unit", None)
        declaration.pop("verbalisation", None)
    return data


def canonical_copy(data):
    from .wire import loads_json
    return loads_json(canonical_json(data))


def erased_environment(env):
    """Regenerate the core target environment; never trust a supplied target ID."""
    from .environment import Environment
    if env.unit_schema != SCHEMA:
        raise UnsupportedProfile("quantities require ve-units@1")
    return Environment(erased_data(env.to_dict()))


def quantity_meaning_id(env, payload):
    canonical, _ = elaborate_quantity(env, payload)
    return digest(f"ve-meaning-{env.identity_version}\n",
                  {"environment_id": env.environment_id, "ast": canonical})
