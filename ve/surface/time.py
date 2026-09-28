"""Controlled W6 quantity wordings for explicit, identity-bound constant names.

This is a local authoring surface. The document route remains gated until the
whole-grammar all-derivations and Lean correspondence checks are connected.
"""
from __future__ import annotations

import re
from itertools import product

from ..errors import AmbiguousDerivation, SyntaxError, UnsupportedProfile, VEError
from ..units import DIMENSIONLESS, decimal_exact, elaborate_quantity, render_coordinate

_DEC = r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z", re.ASCII)


def _constant_readings(env, phrase):
    return [["const", decl.unit or DIMENSIONLESS, name]
            if decl.sort == "$int" else ["const", name]
            for name, decl in env.constants.items() if decl.verbalisation == phrase]


def _literal_readings(env, phrase):
    readings = []
    if _DATE.fullmatch(phrase) and "day" in env.units:
        readings.append(["date", phrase])
    if re.fullmatch(_DEC, phrase, re.ASCII):
        readings.append(["decimal", DIMENSIONLESS, phrase])
    for tag, record in env.units.items():
        display = record["display"]
        kind = display["kind"]
        if kind == "percent" and phrase.endswith("%"):
            amount = phrase[:-1]
        elif kind == "money" and phrase.startswith(display["currency"] + " "):
            amount = phrase[len(display["currency"]) + 1:]
        elif kind == "money" and display.get("input_symbol") and phrase.startswith(display["input_symbol"]):
            amount = phrase[len(display["input_symbol"]):]
        elif kind == "decimal":
            label = display["label"]
            if display.get("placement") == "prefix" and phrase.startswith(label + " "):
                amount = phrase[len(label) + 1:]
            elif display.get("placement", "suffix") == "suffix" and phrase.endswith(" " + label):
                amount = phrase[:-(len(label) + 1)]
            else:
                continue
        else:
            continue
        if re.fullmatch(_DEC, amount, re.ASCII):
            # Grid precision and range are verified again by elaborate_quantity.
            decimal_exact(amount, tag, env)
            readings.append(["decimal", tag, amount])
    return readings


def _terms(env, phrase):
    return _constant_readings(env, phrase) + _literal_readings(env, phrase)


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
    rules = (
        (" equals ", "eq", False),
        (" is less than ", "lt", False),
        (" is greater than ", "lt", True),
        (" is at most ", "le", False),
        (" is at least ", "le", True),
        (" is on ", "date_on", False),
        (" is before ", "date_before", False),
        (" is after ", "date_after", False),
        (" is no later than ", "date_no_later", False),
    )
    readings = []
    rejected = []
    def offer(operation, phrases, suffix=()):
        for terms in product(*(_terms(env, phrase) for phrase in phrases)):
            payload = {"format": "ve-quantity@1", "formula": [operation, *terms, *suffix]}
            try:
                canonical, _ = elaborate_quantity(env, payload)
            except VEError as exc:
                rejected.append(exc)
                continue
            readings.append(canonical)

    within = re.fullmatch(r"(.+?) is on or after (.+?) and on or before (0|[1-9][0-9]*) days after (.+)", text)
    if within and within[2] == within[4]:
        offer("within_days", (within[1][0].lower() + within[1][1:], within[2]), (within[3],))
    shifted = re.fullmatch(r"(.+?) is (0|[1-9][0-9]*) days after (.+)", text)
    if shifted:
        offer("shift_days", (shifted[1][0].lower() + shifted[1][1:], shifted[3]), (shifted[2],))
    elapsed = re.fullmatch(r"The elapsed duration from (.+?) to (.+?) equals (.+)", text)
    if elapsed:
        offer("elapsed_days", (elapsed[1], elapsed[2], elapsed[3]))
    points = re.fullmatch(r"(.+?) minus (.+?) equals (.+) percentage points", text)
    if points:
        percent_tags = [tag for tag, record in env.units.items()
                        if record["display"]["kind"] == "percent"]
        if len(percent_tags) == 1:
            tag = percent_tags[0]
            for left, right in product(_terms(env, points[1][0].lower() + points[1][1:]),
                                       _terms(env, points[2])):
                payload = {"format": "ve-quantity@1", "formula": ["eq",
                    ["add", tag, left, ["scale", tag, "-1", right]],
                    ["decimal", tag, points[3]]]}
                try:
                    canonical, _ = elaborate_quantity(env, payload)
                except VEError as exc:
                    rejected.append(exc)
                    continue
                readings.append(canonical)
    for connector, operation, reverse in rules:
        if text.count(connector) != 1:
            continue
        left, right = text.split(connector)
        if not left or not right:
            continue
        # Sentence-initial capitalization affects presentation only. The
        # vocabulary still supplies the full approved phrase.
        left = left[0].lower() + left[1:]
        for lt in _terms(env, left):
            for rt in _terms(env, right):
                pair = (rt, lt) if reverse else (lt, rt)
                payload = {"format": "ve-quantity@1", "formula": [operation, *pair]}
                try:
                    canonical, _ = elaborate_quantity(env, payload)
                except VEError as exc:
                    rejected.append(exc)
                    continue
                readings.append(canonical)
    if not readings:
        if len(rejected) == 1:
            raise rejected[0]
        raise SyntaxError("No W6 quantity reading")
    if len(readings) != 1:
        raise AmbiguousDerivation(f"W6 quantity sentence has {len(readings)} derivations")
    return readings[0]


def render_quantity_sentence(env, canonical):
    """Render the admitted literal/constant comparison wordings without tags."""
    checked, _ = elaborate_quantity(env, canonical)
    if checked != canonical or canonical["traces"]:
        raise UnsupportedProfile("Quantity wording cannot omit canonical annotations or trace declarations")
    formula = canonical["formula"]
    if formula[0] not in ("eq", "lt", "le", "date_on", "date_before",
                          "date_after", "date_no_later", "within_days", "shift_days",
                          "elapsed_days"):
        raise UnsupportedProfile("No controlled W6 wording for this operation")
    if len(formula) != (4 if formula[0] in ("within_days", "shift_days", "elapsed_days") else 3):
        raise SyntaxError("Invalid quantity comparison")
    def term(node):
        if node[0] == "num" and len(node) == 3:
            return render_coordinate(node[1], int(node[2]), env)
        if node[0] == "const":
            name = node[-1]
            declaration = env.constants.get(name)
            if declaration is not None and declaration.verbalisation is not None:
                return declaration.verbalisation
        raise UnsupportedProfile("Quantity English requires named constants or literals")
    if (formula[0] == "eq" and formula[1][0] == "add" and
            formula[1][3][0] == "scale" and formula[1][3][2] == "-1" and
            formula[2][0] == "num" and formula[1][1] == formula[2][1] and
            formula[2][1] in env.units and
            env.units[formula[2][1]]["display"]["kind"] == "percent"):
        first = term(formula[1][2])
        second = term(formula[1][3][3])
        amount = render_coordinate(formula[2][1], int(formula[2][2]), env).removesuffix("%")
        return first[0].upper() + first[1:] + f" minus {second} equals {amount} percentage points."
    if formula[0] == "elapsed_days":
        return (f"The elapsed duration from {term(formula[1])} to {term(formula[2])} "
                f"equals {term(formula[3])}.")
    left, right = term(formula[1]), term(formula[2])
    if formula[0] == "within_days":
        return (left[0].upper() + left[1:] + f" is on or after {right} and on or before "
                f"{formula[3]} days after {right}.")
    if formula[0] == "shift_days":
        return left[0].upper() + left[1:] + f" is {formula[3]} days after {right}."
    connector = {"eq": " equals ", "lt": " is less than ", "le": " is at most ",
                 "date_on": " is on ", "date_before": " is before ",
                 "date_after": " is after ", "date_no_later": " is no later than "}[formula[0]]
    return left[0].upper() + left[1:] + connector + right + "."
