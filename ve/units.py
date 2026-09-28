"""W6 annotated quantities. Admission precedes erasure into the frozen integer AST.

This module deliberately does not issue certificates: a quantity wrapper needs the
Lean route's independent admission and an outer binding to its annotated identity.
"""
from __future__ import annotations

from datetime import date, timedelta
import re

from .ast import decimal_from_wire, MAX_NUMERAL_CHARS
from .environment import INT_SORT, valid_identifier
from .errors import ResourceLimit, UnsupportedProfile, VEError
from .wire import digest, require_fields

SCHEMA = "ve-units@1"
DIMENSIONLESS = "dimensionless"
DAY = {"scale": "1", "display": {"kind": "iso_date"}}
ELAPSED_DAY = {"scale": "1", "display": {"kind": "decimal", "label": "days"}}
_DATE_MAX = (date(9999, 12, 31) - date(1970, 1, 1)).days
_DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\Z", re.ASCII)
_ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z", re.ASCII)
_SLOT = re.compile(r"0|[1-9][0-9]*\Z", re.ASCII)


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
    seen = set()
    money_codes = set()
    decimal_prefixes = set()
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
            key = (kind,)
        elif kind == "money":
            _fields(display, ("kind", "currency"), ("input_symbol",))
            currency = display["currency"]
            if type(currency) is not str or not re.fullmatch(r"[A-Z]{3}", currency):
                raise VEError(f"Invalid currency for {tag}")
            key = (kind, currency)
            money_codes.add(currency)
            symbol = display.get("input_symbol")
            if symbol is not None:
                _bounded(symbol)
                if ("symbol", symbol) in seen:
                    raise VEError(f"DisplayCollision({symbol})")
                seen.add(("symbol", symbol))
        elif kind == "decimal":
            _fields(display, ("kind", "label"), ("placement",))
            _bounded(display["label"])
            if display.get("placement", "suffix") not in ("prefix", "suffix"):
                raise VEError(f"Invalid placement for {tag}")
            key = (kind, display["label"])
            if display.get("placement") == "prefix":
                decimal_prefixes.add(display["label"])
        elif kind == "iso_date":
            _fields(display, ("kind",))
            if tag != "day" or scale != 1:
                raise VEError("iso_date requires day at scale 1")
            key = (kind,)
        else:
            raise VEError(f"Unknown display kind {kind}")
        if key in seen:
            raise VEError(f"DisplayCollision({key})")
        seen.add(key)
        if tag == "day" and record != DAY:
            raise VEError("Reserved unit day has a fixed declaration")
        if tag == "elapsed_day" and record != ELAPSED_DAY:
            raise VEError("Reserved unit elapsed_day has a fixed declaration")
    if money_codes & decimal_prefixes:
        raise VEError(f"DisplayCollision({sorted(money_codes & decimal_prefixes)[0]})")
    return raw


def _bounded(s):
    if type(s) is not str or not s:
        raise VEError("Display string must be nonempty")
    if len(s) > 256:
        raise ResourceLimit("Display string exceeds 256 characters")


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


def decimal_exact(text, tag, env):
    validate_tag(tag, env.units)
    if type(text) is not str or len(text) > MAX_NUMERAL_CHARS or not _DECIMAL.fullmatch(text):
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


def _same(a, b):
    if a != b:
        raise VEError(f"UnitMismatch({a},{b})")
    return a


def _need(node, tag, arity):
    if type(node) is not list or len(node) != arity or node[0] != tag:
        raise VEError(f"Invalid {tag} node")


class _Elaborator:
    def __init__(self, env):
        if env.unit_schema != SCHEMA:
            raise UnsupportedProfile("quantities require ve-units@1")
        self.env = env
        self.nodes = 0

    def tick(self, depth):
        self.nodes += 1
        if self.nodes > 10000 or depth > 64:
            raise ResourceLimit("Quantity AST exceeds node or depth limit")

    def term(self, node, context=(), depth=1):
        self.tick(depth)
        if type(node) is not list or not node:
            raise VEError("Invalid quantity term")
        op = node[0]
        if op == "const" and len(node) == 2:
            decl = self.env.constants.get(node[1])
            if decl is not None:
                if decl.sort != INT_SORT:
                    return decl.sort, node, node
                _same(DIMENSIONLESS, decl.unit or DIMENSIONLESS)
                return DIMENSIONLESS, ["const", DIMENSIONLESS, node[1]], node
        if op == "var" and len(node) == 2:
            index = node[1]
            if type(index) is int and 0 <= index < len(context):
                if context[index][0] != INT_SORT:
                    return context[index][0], node, node
                _same(DIMENSIONLESS, context[index][1])
                return DIMENSIONLESS, ["var", DIMENSIONLESS, index], node
        if op == "num" and len(node) == 2:
            coordinate = decimal_from_wire(node[1])
            return DIMENSIONLESS, ["num", DIMENSIONLESS, str(coordinate)], ["num", str(coordinate)]
        if op == "add" and len(node) == 3:
            return self.term(["add", DIMENSIONLESS, node[1], node[2]], context, depth)
        if op == "scale" and len(node) == 3:
            return self.term(["scale", DIMENSIONLESS, node[1], node[2]], context, depth)
        if op in ("num", "decimal", "date"):
            if op == "date":
                _need(node, op, 2)
                tag, coordinate = "day", day_number(node[1])
            else:
                _need(node, op, 3)
                tag = validate_tag(node[1], self.env.units)
                coordinate = decimal_from_wire(node[2]) if op == "num" else decimal_exact(node[2], tag, self.env)
            return tag, ["num", tag, str(coordinate)], ["num", str(coordinate)]
        if op == "const":
            _need(node, op, 3)
            tag = validate_tag(node[1], self.env.units)
            decl = self.env.constants.get(node[2])
            if decl is None or decl.sort != INT_SORT:
                raise VEError(f"Unknown integer constant {node[2]}")
            _same(tag, decl.unit or DIMENSIONLESS)
            return tag, node, ["const", node[2]]
        if op == "var":
            _need(node, op, 3)
            tag = validate_tag(node[1], self.env.units)
            index = node[2]
            if type(index) is not int or not 0 <= index < len(context) or context[index][0] != INT_SORT:
                raise VEError(f"Unbound integer variable {index}")
            _same(tag, context[index][1])
            return tag, node, ["var", index]
        if op == "scale":
            _need(node, op, 4)
            tag = validate_tag(node[1], self.env.units)
            coefficient = decimal_from_wire(node[2])
            found, q, core = self.term(node[3], context, depth + 1)
            _same(tag, found)
            if tag == "day":
                raise VEError("Calendar dates cannot be scaled")
            return tag, ["scale", tag, str(coefficient), q], ["scale", str(coefficient), core]
        if op == "add":
            _need(node, op, 4)
            tag = validate_tag(node[1], self.env.units)
            left, lq, lc = self.term(node[2], context, depth + 1)
            right, rq, rc = self.term(node[3], context, depth + 1)
            _same(tag, _same(left, right))
            if tag == "day":
                raise VEError("Calendar dates cannot be added")
            return tag, ["add", tag, lq, rq], ["add", lc, rc]
        raise VEError(f"Invalid quantity term {op}")

    def formula(self, node, context=(), depth=1):
        self.tick(depth)
        if type(node) is not list or not node:
            raise VEError("Invalid quantity formula")
        op = node[0]
        if op in ("top", "bottom") and len(node) == 1:
            return node, node
        if op in ("eq", "lt", "le") and len(node) == 3:
            lt, lq, lc = self.term(node[1], context)
            rt, rq, rc = self.term(node[2], context)
            _same(lt, rt)
            if op != "eq" and lt != INT_SORT and lt not in self.env.units and lt != DIMENSIONLESS:
                raise VEError("Order needs integer terms")
            return [op, lq, rq], [op, lc, rc]
        if op in ("unary", "binary", "atom"):
            if op == "unary" and len(node) == 3:
                args = [node[2]]
            elif op == "binary" and len(node) == 4:
                args = node[2:]
            elif op == "atom" and len(node) == 3 and type(node[2]) is list:
                args = node[2]
            else:
                raise VEError(f"Invalid {op} arity")
            decl = self.env.predicates.get(node[1])
            if decl is None or len(args) != len(decl.arguments):
                raise VEError(f"Unknown predicate or arity {node[1]}")
            terms = [self.term(t, context) for t in args]
            for i, (found, _, _) in enumerate(terms):
                expected = decl.argument_units.get(str(i), DIMENSIONLESS) if decl.arguments[i] == INT_SORT else decl.arguments[i]
                _same(found, expected)
            qargs, cargs = [t[1] for t in terms], [t[2] for t in terms]
            if op == "atom":
                return [op, node[1], qargs], [op, node[1], cargs]
            return [op, node[1], *qargs], [op, node[1], *cargs]
        if op == "not" and len(node) == 2:
            q, c = self.formula(node[1], context, depth + 1)
            return [op, q], [op, c]
        if op in ("and", "or", "implies") and len(node) == 3:
            lq, lc = self.formula(node[1], context, depth + 1)
            rq, rc = self.formula(node[2], context, depth + 1)
            return [op, lq, rq], [op, lc, rc]
        if op in ("forall", "exists"):
            if len(node) in (3, 4) and node[1] == INT_SORT:
                raise UnsupportedProfile("$int quantification requires the missing numbers2 route")
            if len(node) != 3 or node[1] not in self.env.sorts:
                raise VEError("Invalid quantity binder")
            q, c = self.formula(node[2], ((node[1], None), *context), depth + 1)
            return [op, node[1], q], [op, node[1], c]
        if op in ("date_on", "date_before", "date_after", "date_no_later", "within_days", "shift_days", "elapsed_days"):
            return self.temporal(node, context, depth)
        if op in ("sunday", "excluded_sundays", "forall_date", "exists_date", "trace_all", "trace_some"):
            raise UnsupportedProfile("$int quantification requires the missing numbers2 route")
        raise VEError(f"Unknown quantity formula {op}")

    def temporal(self, node, context, depth):
        op = node[0]
        if op in ("date_on", "date_before", "date_after", "date_no_later"):
            _need(node, op, 3)
        else:
            _need(node, op, 4)
        a, aq, ac = self.term(node[1], context)
        b, bq, bc = self.term(node[2], context)
        _same(a, "day"); _same(b, "day")
        guard = lambda x: ["and", ["le", ["num", "0"], x], ["le", x, ["num", str(_DATE_MAX)]]]
        both = ["and", guard(ac), guard(bc)]
        if op == "date_on": body = ["eq", ac, bc]
        elif op == "date_before": body = ["lt", ac, bc]
        elif op == "date_after": body = ["lt", bc, ac]
        elif op == "date_no_later": body = ["le", ac, bc]
        else:
            if op == "elapsed_days":
                v, vq, vc = self.term(node[3], context)
                _same(v, "elapsed_day")
                body = ["eq", vc, ["add", bc, ["scale", "-1", ac]]]
                return [op, aq, bq, vq], ["and", both, body]
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
    # W6b declarations are identity-bound even on an otherwise ground claim.
    names = set()
    checked = []
    for t in traces:
        _fields(t, ("name", "tick_tag", "origin", "horizon"))
        if not valid_identifier(t["name"]) or t["name"] in names:
            raise VEError("Duplicate or invalid trace name")
        names.add(t["name"])
        tag = validate_tag(t["tick_tag"], env.units)
        if tag != DIMENSIONLESS and (env.units[tag]["scale"] != "1" or tag == "day"):
            raise VEError("Trace tick tag must be scale-1 and non-date")
        decl = env.constants.get(t["origin"])
        if decl is None or decl.sort not in env.sorts:
            raise VEError("Trace origin must be a declared user-sort event constant")
        if decimal_from_wire(t["horizon"]) < 0:
            raise VEError("Trace horizon must be nonnegative")
        checked.append(t)
    q, core = _Elaborator(env).formula(payload["formula"])
    if "Q" in payload and payload["Q"] != q:
        raise VEError("Quantity Q differs from regenerated formula")
    # The target vocabulary has the same symbols and checker profile, with only
    # W6 declaration fields removed. The frozen checker validates regenerated
    # data in that independently identified environment.
    from .ast import formula_from_data
    formula_from_data(erased_environment(env), core)
    return {"format": "ve-quantity@1", "formula": q,
            "traces": sorted(checked, key=lambda t: t["name"])}, core


def erased_environment(env):
    """Regenerate the core target environment; never trust a supplied target ID."""
    from .environment import Environment
    if env.unit_schema != SCHEMA:
        raise UnsupportedProfile("quantities require ve-units@1")
    data = env.to_dict()
    del data["unit_schema"]
    del data["units"]
    for declaration in data["vocabulary"]["predicates"].values():
        declaration.pop("argument_units", None)
    for declaration in data["vocabulary"]["constants"].values():
        declaration.pop("unit", None)
    return Environment(data)


def quantity_meaning_id(env, payload):
    canonical, _ = elaborate_quantity(env, payload)
    return digest(f"ve-meaning-{env.identity_version}\n",
                  {"environment_id": env.environment_id, "ast": canonical})
