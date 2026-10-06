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
from .limits import MAX_NODES
from .wire import canonical_json, digest

SCHEMA = "ve-units@1"
DIMENSIONLESS = "dimensionless"
DAY = {"scale": "1", "display": {"kind": "iso_date"}}
ELAPSED_DAY = {"scale": "1", "display": {"kind": "decimal", "label": "days"}}
_DATE_MAX = (date(9999, 12, 31) - date(1970, 1, 1)).days
_DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\Z", re.ASCII)
_ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z", re.ASCII)
_SLOT = re.compile(r"0|[1-9][0-9]*\Z", re.ASCII)
# Exactly the characters for which Python's str.isspace() holds, listed so that
# Lean's W6 decoder checks the same display-string rule.
SPACES = frozenset(map(chr, (9, 10, 11, 12, 13, 28, 29, 30, 31, 32, 0x85, 0xA0, 0x1680,
                             *range(0x2000, 0x200B), 0x2028, 0x2029, 0x202F, 0x205F, 0x3000)))
# Characters a decimal amount can begin or end with. A display affix must not
# touch the amount with one of these, so an affixed literal is never also a
# bare decimal, a date, or a literal with an affix on the other side.
_AMOUNT_CHARS = frozenset("-.0123456789")
POINTS_SUFFIX = " percentage points"
W6_PROFILES = (("order@0", "relational-fol@0", "time@0"),
               ("documents@1", "order@0", "relational-fol@0", "time@0"))
# risk@0 carries the unit extension on its own route (risk.md 1, 3.1); the
# frozen quantity-route tuples and their diagnostic above are unchanged.
RISK_UNIT_PROFILES = (("alternatives@0", "norms@0", "relational-fol@0", "risk@0"),)
W6_PROFILE_TEXT = ("ve-units@1 requires exactly order@0, relational-fol@0 and time@0, "
                   "optionally with documents@1")


def quote(s):
    """Lean's `String.quote`, which the Lean W6 decoder uses in its texts."""
    escapes = {"\n": "\\n", "\t": "\\t", "\\": "\\\\", '"': '\\"'}
    return '"' + "".join(escapes.get(c) or (f"\\x{ord(c):02x}" if ord(c) <= 31 or c == "\x7f" else c)
                         for c in s) + '"'


def _object(value):
    if type(value) is not dict:
        raise VEError("object expected")
    return value


def _string(value):
    if type(value) is not str:
        raise VEError("String expected")
    return value


def _fields(value, required, optional=()):
    """Lean's `exactFields` (no optional fields) and `shape`, with their texts."""
    got = f"got [{', '.join(sorted(_object(value)))}]"
    if optional:
        if not set(required) <= set(value) or not set(value) <= set(required) | set(optional):
            raise VEError(f"fields do not match: required [{', '.join(required)}], "
                          f"optional [{', '.join(optional)}], {got}")
    elif set(value) != set(required):
        raise VEError(f"fields do not match: expected [{', '.join(required)}], {got}")


def _scale(tag, text):
    """Lean's `decodeScale`: a canonical integer that is a positive power of ten."""
    _string(text)
    if len(text) > MAX_NUMERAL_CHARS:
        raise ResourceLimit("numeral length")
    if not re.fullmatch(r"-?[0-9]+", text, re.ASCII):
        raise VEError("invalid integer")
    if str(int(text)) != text:
        raise VEError("non-canonical integer")
    if text[0] != "1" or set(text[1:]) - {"0"}:
        raise VEError(f"UnitScale({tag}): expected a positive power of ten")
    return int(text)


def validate_units(schema, raw):
    """The unit records, with the texts of Lean's `decodeUnit` and in its (sorted) tag order."""
    if schema != SCHEMA:
        raise UnsupportedProfile("Unsupported unit schema")
    if type(raw) is not dict:
        raise VEError("units must be an object")
    if len(raw) > 64:
        raise ResourceLimit("At most 64 unit tags")
    for tag, record in sorted(raw.items()):
        if not valid_identifier(tag) or tag == DIMENSIONLESS:
            raise VEError(f"Invalid unit tag {quote(tag)}")
        _fields(record, ("scale", "display"))
        scale = _scale(tag, record["scale"])
        display = record["display"]
        if type(display) is not dict or "kind" not in display:
            raise VEError(f"Invalid display for {tag}")
        kind = _string(display["kind"])
        if kind == "percent":
            _fields(display, ("kind",))
        elif kind == "money":
            _fields(display, ("kind", "currency"), ("input_symbol",))
            currency = _string(display["currency"])
            if not re.fullmatch(r"[A-Z]{3}", currency):
                raise VEError(f"Invalid currency for {tag}")
            if "input_symbol" in display:
                display_string(_string(display["input_symbol"]), trailing_space=True)
        elif kind == "decimal":
            _fields(display, ("kind", "label"), ("placement",))
            display_string(_string(display["label"]))
            if _string(display.get("placement", "suffix")) not in ("prefix", "suffix"):
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


def display_string(s, *, trailing_space=False, what="Display string"):
    """Nonempty words of non-space characters joined by single spaces.

    An input symbol may end in one space ("EUR "). Other whitespace, and
    spacing the sentence normalizer would rewrite, is rejected."""
    if type(s) is not str or not s:
        raise VEError(f"{what} must be nonempty")
    if len(s) > 256:
        raise ResourceLimit(f"{what} exceeds 256 characters")
    words = s.split(" ")
    if trailing_space and len(words) > 1 and words[-1] == "":
        words = words[:-1]
    if any(not word or SPACES & set(word) for word in words):
        raise VEError(f"{what} {quote(s)} must be whitespace-normalized")
    return s


def sentence_initial(words):
    """The sentence-initial spelling of a name: its first letter ASCII-uppercased."""
    first = words[:1]
    return (first.upper() if "a" <= first <= "z" else first) + words[1:]


def check_verbalisations(constants):
    """Constant names are spelled so that the sentence normalizer keeps them and
    no two share a spelling, even when one starts a sentence. Then a rendered
    name is read back as exactly its own constant. Names are checked in sorted
    order, as the Lean decoder reads a JSON object."""
    spellings = {}
    for name, decl in sorted(constants.items()):
        if decl.verbalisation is None:
            continue
        display_string(decl.verbalisation, what="Verbalisation")
        key = sentence_initial(decl.verbalisation)
        if key in spellings:
            raise VEError(f"VerbalisationCollision({spellings[key]}, {name})")
        spellings[key] = name


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
    forms = display_affixes(dict(sorted(units.items())))
    for side, text, _ in forms:
        edge = text[0] if side == "prefix" else text[-1]
        if edge in _AMOUNT_CHARS:
            raise VEError(f"DisplayCollision({quote(text)} touches the amount)")
    for i, (side, text, _) in enumerate(forms):
        for other_side, other, _ in forms[i + 1:]:
            if side != other_side:
                continue
            extends = (text.startswith(other) or other.startswith(text) if side == "prefix"
                       else text.endswith(other) or other.endswith(text))
            if extends:
                raise VEError(f"DisplayCollision({quote(text)}, {quote(other)})")


def validate_tag(tag, units):
    if type(tag) is not str or (tag != DIMENSIONLESS and (units is None or tag not in units)):
        raise VEError(f"UnknownUnit({tag})")
    return tag


def validate_slot_units(raw, args, units):
    if type(raw) is not dict:
        raise VEError("argument_units must be an object")
    result = {}
    for slot, tag in sorted(raw.items()):
        if type(slot) is not str or not _SLOT.fullmatch(slot) or int(slot) >= len(args):
            raise VEError(f"Invalid argument unit slot {slot}")
        if args[int(slot)] != INT_SORT:
            raise VEError(f"Unit on non-integer slot {slot}")
        result[slot] = validate_tag(_string(tag), units)
    return {slot: result[slot] for slot in raw}


def validate_extension(profiles, units, sorts, constants):
    """Route-level W6 environment conditions, after the vocabulary is decoded."""
    if tuple(profiles) not in W6_PROFILES + RISK_UNIT_PROFILES:
        raise UnsupportedProfile(W6_PROFILE_TEXT)
    for tag in (DIMENSIONLESS, *sorted(units)):
        if tag in sorts:
            raise VEError(f"Unit tag {tag} collides with a declared sort")
    if any(decl.sort == STRING_SORT for decl in constants.values()):
        raise UnsupportedProfile("$string literals are not admitted with ve-units@1")
    check_verbalisations(constants)


def decimal_digits(text):
    return sum(c in "0123456789" for c in text)


def decimal_exact(text, tag, env):
    """Lower a decimal literal of at most 40 digits (sign and point uncounted).

    Every admitted coordinate (at most 40 characters) renders on any declared
    scale (at most 39 places) with at most 40 digits, so rendering reparses."""
    validate_tag(tag, env.units)
    if type(text) is str and decimal_digits(text) > MAX_NUMERAL_CHARS:
        raise ResourceLimit(f"Decimal literal exceeds {MAX_NUMERAL_CHARS} digits")
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


def _checked_quantity(env, payload):
    """Lean's W6 typing and erasure answer for one annotated statement."""
    from .backends.relay import decide
    [row] = decide("check", [{"id": "quantity", "environment": env.to_dict(),
                              "quantity": payload}])
    if row["environment_id"] != env.environment_id:
        from .errors import CheckerUnavailable
        raise CheckerUnavailable("CheckerUnavailable: W6 environment identity mismatch")
    return row


def elaborate_quantity(env, payload):
    """Return Lean's canonical annotated statement and erased core."""
    row = _checked_quantity(env, payload)
    return {"format": "ve-quantity@1", "formula": row["Q"], "traces": []}, row["core"]


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


def core_formula(env, payload):
    """The erased target environment and the regenerated core formula of an
    admitted statement, for checks that run on the frozen checker."""
    from .ast import formula_from_data
    _, core = elaborate_quantity(env, payload)
    target = erased_environment(env)
    return target, formula_from_data(target, core)


def quantity_meaning_id(env, payload):
    return _checked_quantity(env, payload)["meaning_id"]


# --- Quantity evidence: a core order certificate wrapped by the annotated binding

CERTIFICATE_FORMAT = "ve-quantity-certificate@1"


def _core_problem(env, premises, conclusion):
    """Read each admitted core and identity from Lean for the certificate generator."""
    from .ast import formula_from_data
    target = erased_environment(env)
    rows = [_checked_quantity(env, p) for p in (*premises, conclusion)]
    ids = [row["meaning_id"] for row in rows]
    cores = [formula_from_data(target, row["core"]) for row in rows]
    check_quantity_limits(cores)
    return target, ids, cores


AGGREGATE_LIMIT = "premises and conclusion exceed aggregate 10000-node limit"


def check_quantity_limits(cores):
    """The static limits of a quantity problem, after each statement's own limits
    and before any model is decoded, certificate read or evaluation run: the
    regenerated cores (premises, then the conclusion) have at most 10,000 formula
    and term nodes together (Lean `quantityLimits`). The certificate generator stops
    here (rule 3: an untrusted generator's budget); Lean decides every replay."""
    from .search import _node_count
    if sum(_node_count(core) for core in cores) > MAX_NODES:
        raise ResourceLimit(AGGREGATE_LIMIT)


def prove_quantity(env, premises, conclusion, *, max_steps=10_000):
    """Search an order certificate for the regenerated problem and bind it to the
    annotated statements. Returns None when search is inconclusive."""
    from .entailment import prove_entailment
    target, ids, cores = _core_problem(env, premises, conclusion)
    result = prove_entailment(target, cores[:-1], cores[-1], max_steps=max_steps)
    if result.certificate is None:
        return None
    return {"format": CERTIFICATE_FORMAT, "environment_id": env.environment_id,
            "premise_meaning_ids": ids[:-1], "conclusion_meaning_id": ids[-1],
            "core": result.certificate}


def check_quantity_certificate(env, premises, conclusion, certificate):
    """Lean's replay of the bound quantity certificate, within Lean's step limit."""
    from .backends.relay import decide
    [row] = decide("quantity", [{"id": "certificate", "kind": "certificate",
                                "environment": env.to_dict(), "premises": premises,
                                "conclusion": conclusion, "certificate": certificate}])
    return row["valid"]


def quantity_countermodel(env, premises, conclusion, model_data):
    """Return Lean's checked countermodel verdict."""
    from .backends.relay import decide
    [row] = decide("quantity", [{"id": "countermodel", "kind": "countermodel",
                                "environment": env.to_dict(), "premises": premises,
                                "conclusion": conclusion, "model": model_data}])
    return row["refutes"]
