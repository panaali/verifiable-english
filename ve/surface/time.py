"""Controlled W6 quantity wordings for explicit, identity-bound constant names.

This is a local authoring surface. The document route remains gated until the
whole-grammar all-derivations and Lean correspondence checks are connected.
Within this grammar every rule is tried at every occurrence of its connectors,
so a sentence with two derivations is rejected rather than read one way.
"""
from __future__ import annotations

import re
from itertools import product

from ..errors import AmbiguousDerivation, ResourceLimit, SyntaxError, UnsupportedProfile, VEError
from ..units import (DIMENSIONLESS, POINTS_SUFFIX, day_number, decimal_exact, elaborate_quantity,
                     render_coordinate, sentence_initial)

_DEC = r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"
_NAT = re.compile(r"0|[1-9][0-9]*\Z", re.ASCII)
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z", re.ASCII)
_MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December")
# Candidate derivations tried per sentence; exhaustion rejects naming this budget.
MAX_DERIVATIONS = 10_000

# (connectors in order, operation, reversed operands); each connector separates
# two nonempty operand phrases. The first phrase starts the sentence.
_COMPARISONS = (
    ((" equals ",), "eq", False),
    ((" is less than ",), "lt", False),
    ((" is greater than ",), "lt", True),
    ((" is at most ",), "le", False),
    ((" is at least ",), "le", True),
    ((" is on ",), "date_on", False),
    ((" is before ",), "date_before", False),
    ((" is after ",), "date_after", False),
    ((" is no later than ",), "date_no_later", False),
)
_WITHIN = (" is on or after ", " and on or before ", " days after ")
_SHIFT = (" is ", " days after ")
_ELAPSED_PREFIX = "The elapsed duration from "
_ELAPSED = (" to ", " equals ")
_POINTS = (" minus ", " equals ")


def _constant_readings(env, phrase, initial):
    """A constant matches its approved phrase; at sentence start also its
    capitalized form. Literals are never case-folded."""
    return [["const", decl.unit or DIMENSIONLESS, name]
            if decl.sort == "$int" else ["const", name]
            for name, decl in env.constants.items()
            if decl.verbalisation is not None and
            (decl.verbalisation == phrase or initial and sentence_initial(decl.verbalisation) == phrase)]


def _literal_readings(env, phrase):
    readings = []
    if _DATE.fullmatch(phrase) and "day" in env.units:
        readings.append(["date", phrase])
    long_date = re.fullmatch(r"([1-9]|[12][0-9]|3[01]) ([A-Z][a-z]+) ([0-9]{4})", phrase)
    if long_date and long_date[2] in _MONTHS and "day" in env.units:
        iso = f"{long_date[3]}-{_MONTHS.index(long_date[2])+1:02d}-{int(long_date[1]):02d}"
        day_number(iso)
        readings.append(["date", iso])
    if re.fullmatch(_DEC, phrase, re.ASCII):
        readings.append(["decimal", DIMENSIONLESS, phrase])
    for tag, record in env.units.items():
        display = record["display"]
        kind = display["kind"]
        if kind == "percent" and phrase.endswith("%"):
            amounts = [phrase[:-1]]
        elif kind == "money":
            prefixes = [display["currency"] + " "] + ([display["input_symbol"]]
                                                      if "input_symbol" in display else [])
            amounts = [phrase[len(p):] for p in prefixes if phrase.startswith(p)]
        elif kind == "decimal":
            label = display["label"]
            if display.get("placement") == "prefix" and phrase.startswith(label + " "):
                amounts = [phrase[len(label) + 1:]]
            elif display.get("placement", "suffix") == "suffix" and phrase.endswith(" " + label):
                amounts = [phrase[:-(len(label) + 1)]]
            else:
                continue
        else:
            continue
        for amount in amounts:
            if re.fullmatch(_DEC, amount, re.ASCII):
                # Grid precision and range are verified again by elaborate_quantity.
                decimal_exact(amount, tag, env)
                readings.append(["decimal", tag, amount])
    return readings


def _terms(env, phrase, initial=False):
    return _constant_readings(env, phrase, initial) + _literal_readings(env, phrase)


class _Derivations:
    def __init__(self, env):
        self.env, self.readings, self.rejected, self.work = env, [], [], 0

    def tick(self):
        self.work += 1
        if self.work > MAX_DERIVATIONS:
            raise ResourceLimit(f"W6 quantity derivation budget MAX_DERIVATIONS={MAX_DERIVATIONS} exhausted")

    def splits(self, text, connectors):
        """Every way to write text as p0 + c0 + p1 + ... with nonempty phrases.
        Each connector occurrence tried is charged to the derivation budget."""
        if not connectors:
            if text:
                yield (text,)
            return
        connector = connectors[0]
        start = text.find(connector, 1)
        while start != -1:
            self.tick()
            for rest in self.splits(text[start + len(connector):], connectors[1:]):
                yield (text[:start], *rest)
            start = text.find(connector, start + 1)

    def offer(self, formula):
        self.tick()
        try:
            canonical, _ = elaborate_quantity(self.env, {"format": "ve-quantity@1", "formula": formula})
        except VEError as exc:
            self.rejected.append(exc)
            return
        self.readings.append(canonical)

    def terms(self, *phrases):
        """Readings of each phrase; the first phrase starts the sentence."""
        return product(*(_terms(self.env, p, i == 0) for i, p in enumerate(phrases)))


def parse_quantity_sentence(env, source):
    """Enumerate every derivation in this restricted W6 sentence grammar."""
    if env.unit_schema is None:
        raise UnsupportedProfile("quantity English requires ve-units@1")
    if type(source) is not str or len(source.encode("utf-8")) > 65536:
        raise SyntaxError("Invalid quantity sentence")
    source = " ".join(source.split())
    if not source.endswith("."):
        raise SyntaxError("Quantity sentence requires a full stop")
    text = source[:-1]
    d = _Derivations(env)
    for left, day, count, origin in d.splits(text, _WITHIN):
        if day == origin and _NAT.fullmatch(count):
            for pair in d.terms(left, day):
                d.offer(["within_days", *pair, count])
    for left, count, origin in d.splits(text, _SHIFT):
        if _NAT.fullmatch(count):
            for pair in d.terms(left, origin):
                d.offer(["shift_days", *pair, count])
    if text.startswith(_ELAPSED_PREFIX):
        for start, end, value in d.splits(text[len(_ELAPSED_PREFIX):], _ELAPSED):
            for start_t, end_t, value_t in product(*(_terms(env, p) for p in (start, end, value))):
                d.offer(["elapsed_days", start_t, end_t, value_t])
    if text.endswith(POINTS_SUFFIX):
        percent_tags = [tag for tag, record in env.units.items()
                        if record["display"]["kind"] == "percent"]
        for first, second, amount in d.splits(text[:-len(POINTS_SUFFIX)], _POINTS):
            for tag in percent_tags:
                for left, right in d.terms(first, second):
                    d.offer(["eq", ["add", tag, left, ["scale", tag, "-1", right]],
                             ["decimal", tag, amount]])
    for connectors, operation, reverse in _COMPARISONS:
        for left, right in d.splits(text, connectors):
            for lt, rt in d.terms(left, right):
                d.offer([operation, *((rt, lt) if reverse else (lt, rt))])
    if not d.readings:
        if len(d.rejected) == 1:
            raise d.rejected[0]
        raise SyntaxError("No W6 quantity reading")
    if len(d.readings) != 1:
        raise AmbiguousDerivation(f"W6 quantity sentence has {len(d.readings)} derivations")
    return d.readings[0]


def _core_readings(env, source, grammar):
    """Readings of the frozen English or strict grammar over the erased target,
    each taken as dimensionless source input through annotated admission."""
    from ..ast import formula_to_data
    from ..units import erased_environment
    target = erased_environment(env)
    if grammar == "english":
        from ..english import parse_english as parse
    else:
        from ..parser import parse
    document = parse(target, source)
    if len(document.formulas) != 1:
        raise SyntaxError("each VE fence must contain exactly one sentence")
    payload = {"format": "ve-quantity@1", "formula": formula_to_data(target, document.formulas[0])}
    canonical, _ = elaborate_quantity(env, payload)
    return canonical


def parse_w6_sentence(env, source, surface="english"):
    """One sentence in a ve-units@1 environment, across every grammar that applies.

    English is the whole grammar: the quantity wordings above plus the frozen
    English grammar over the erased target, whose readings are dimensionless
    source input and must pass the same annotated admission. Each grammar tries
    every derivation; distinct admitted readings across them reject as
    ambiguous, and a sentence with none rejects. Strict text has only the frozen
    grammar."""
    readings, rejected = {}, []
    grammars = [("quantity", None), ("core", "english")] if surface == "english" else [("core", "strict")]
    for name, grammar in grammars:
        try:
            canonical = (parse_quantity_sentence(env, source) if name == "quantity"
                         else _core_readings(env, source, grammar))
        except AmbiguousDerivation:
            raise
        except (ResourceLimit, UnsupportedProfile):
            raise
        except VEError as exc:
            rejected.append(exc)
            continue
        from ..wire import canonical_json
        readings[canonical_json(canonical)] = canonical
    if len(readings) > 1:
        raise AmbiguousDerivation(f"W6 sentence has {len(readings)} derivations across the English grammar")
    if not readings:
        specific = [e for e in rejected
                    if not str(e).startswith(("No W6 quantity reading", "Unknown English"))
                    and getattr(getattr(e, "lean_reading", None), "status", None) != "none"]
        raise specific[0] if len(specific) == 1 else SyntaxError("No W6 reading in any grammar")
    return next(iter(readings.values()))


def render_quantity_sentence(env, canonical):
    """Render the admitted literal/constant comparison wordings without tags.

    Only a sentence-initial constant name is capitalized; literals keep their
    canonical display so that parsing recovers the same tag and amount."""
    checked, _ = elaborate_quantity(env, canonical)
    if checked != canonical or canonical["traces"]:
        raise UnsupportedProfile("Quantity wording cannot omit canonical annotations or trace declarations")
    formula = canonical["formula"]
    if formula[0] not in ("eq", "lt", "le", "date_on", "date_before",
                          "date_after", "date_no_later", "within_days", "shift_days",
                          "elapsed_days"):
        raise UnsupportedProfile("No controlled W6 wording for this operation")

    def term(node, initial=False):
        if node[0] == "num" and len(node) == 3:
            return render_coordinate(node[1], int(node[2]), env)
        if node[0] == "const":
            declaration = env.constants.get(node[-1])
            if declaration is not None and declaration.verbalisation is not None:
                words = declaration.verbalisation
                return sentence_initial(words) if initial else words
        raise UnsupportedProfile("Quantity English requires named constants or literals")

    if (formula[0] == "eq" and formula[1][0] == "add" and
            formula[1][3][0] == "scale" and formula[1][3][2] == "-1" and
            formula[2][0] == "num" and formula[1][1] == formula[2][1] and
            formula[2][1] in env.units and
            env.units[formula[2][1]]["display"]["kind"] == "percent"):
        amount = render_coordinate(formula[2][1], int(formula[2][2]), env).removesuffix("%")
        return (f"{term(formula[1][2], True)} minus {term(formula[1][3][3])} equals "
                f"{amount}{POINTS_SUFFIX}.")
    if formula[0] == "elapsed_days":
        return (f"{_ELAPSED_PREFIX}{term(formula[1])} to {term(formula[2])} "
                f"equals {term(formula[3])}.")
    left, right = term(formula[1], True), term(formula[2])
    if formula[0] == "within_days":
        return f"{left} is on or after {right} and on or before {formula[3]} days after {right}."
    if formula[0] == "shift_days":
        return f"{left} is {formula[3]} days after {right}."
    connector = {"eq": " equals ", "lt": " is less than ", "le": " is at most ",
                 "date_on": " is on ", "date_before": " is before ",
                 "date_after": " is after ", "date_no_later": " is no later than "}[formula[0]]
    return left + connector + right + "."


def render_quantity_witness(env, model_data):
    """A finite model of the erased target in document terms (W8 de-elaboration):
    every integer constant with its unit restored, dates as ISO dates, scaled
    coordinates as decimals with their display. A coordinate outside the
    calendar range is named as a day number, never rounded into a date."""
    from ..model import FiniteModel
    from ..units import erased_environment
    target = erased_environment(env)
    constants = FiniteModel.from_dict(target, model_data).constants
    lines = []
    for name, decl in env.constants.items():
        if decl.sort != "$int" or name not in constants:
            continue
        tag = decl.unit or DIMENSIONLESS
        coordinate = int(constants[name])
        try:
            value = render_coordinate(tag, coordinate, env)
        except VEError:
            value = f"day number {coordinate} (outside 1970-01-01 to 9999-12-31)"
        words = sentence_initial(decl.verbalisation) if decl.verbalisation else name
        lines.append(f"{words} is {value}.")
    return lines
