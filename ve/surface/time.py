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
from ..limits import MAX_SOURCE_BYTES
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
# Money subtraction (relb F2): "A equals B minus C." reads eq(A, B + (-1)*C) for a money tag.
_MINUS = (" equals ", " minus ")
# Operations with a controlled quantity wording, and the yes/no connectives the
# splice reads around them (relb F1).
_QUANTITY_OPS = ("eq", "lt", "le", "date_on", "date_before", "date_after", "date_no_later",
                 "within_days", "shift_days", "elapsed_days")
_FRAME_OPS = ("and", "or", "not", "implies")


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
    """Readings and rejections of one text. `budget` is a one-element list shared
    by every _Derivations of one sentence, so the splice's span readings, frames
    and joined readings are all charged to one MAX_DERIVATIONS budget."""

    def __init__(self, env, budget=None):
        self.env, self.readings, self.rejected = env, [], []
        self.budget = [0] if budget is None else budget

    @property
    def work(self):
        return self.budget[0]

    def tick(self):
        self.budget[0] += 1
        if self.budget[0] > MAX_DERIVATIONS:
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
    if type(source) is not str or len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise SyntaxError("Invalid quantity sentence")
    source = " ".join(source.split())
    if not source.endswith("."):
        raise SyntaxError("Quantity sentence requires a full stop")
    d = _Derivations(env)
    _quantity_readings(env, source[:-1], d)
    if not d.readings:
        if len(d.rejected) == 1:
            raise d.rejected[0]
        raise SyntaxError("No W6 quantity reading")
    if len(d.readings) != 1:
        raise AmbiguousDerivation(f"W6 quantity sentence has {len(d.readings)} derivations")
    return d.readings[0]


def _quantity_readings(env, text, d):
    """Offer every derivation of `text` (a sentence without its full stop) in the
    quantity grammar to `d`; admitted readings collect in d.readings."""
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
    money_tags = [tag for tag, record in env.units.items() if record["display"]["kind"] == "money"]
    if money_tags:
        for first, second, third in d.splits(text, _MINUS):
            for tag in money_tags:
                for a, b, c in d.terms(first, second, third):
                    d.offer(["eq", a, ["add", tag, b, ["scale", tag, "-1", c]]])
    for connectors, operation, reverse in _COMPARISONS:
        for left, right in d.splits(text, connectors):
            for lt, rt in d.terms(left, right):
                d.offer([operation, *((rt, lt) if reverse else (lt, rt))])


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


# --- the splice (relb F1): quantity wordings inside the core English frame -----

_SPLICE_TARGETS = {}


def _splice_target(env, count, avoid):
    """A copy of the erased environment with `count` fresh yes/no stand-ins: one
    fresh sort, one fresh constant of it and `count` fresh unary predicates over
    it, all named apart from the environment's names and from the text `avoid`.
    Returns the target, the stand-in predicate names and each stand-in's core
    wording (no full stop)."""
    from ..english import render_english
    from ..ast import formula_from_data
    from ..environment import Environment
    from ..units import erased_data
    data = erased_data(env.to_dict())
    vocabulary = data["vocabulary"]
    taken = set(vocabulary["sorts"]) | set(vocabulary["predicates"]) | set(vocabulary["constants"])
    base = "w6_splice"
    while any(n.startswith(base) for n in taken) or base in avoid:
        base += "_x"
    count = -(-max(count, 1) // 8) * 8  # declared in blocks of 8: fewer distinct environments
    key = (env.environment_id, base, count)
    if key not in _SPLICE_TARGETS:
        sort, slot = base, base + "_slot"
        predicates = [f"{base}_{k + 1}" for k in range(count)]
        vocabulary["sorts"][sort] = {"description": "A stand-in for a quantity wording."}
        vocabulary["constants"][slot] = {"sort": sort, "description": "A stand-in for a quantity wording."}
        for name in predicates:
            vocabulary["predicates"][name] = {"arguments": [sort],
                                              "description": "A stand-in for a quantity wording."}
        target = Environment(data)
        words = [render_english(formula_from_data(target, ["unary", p, ["const", slot]]), target).strip()
                 .removesuffix(".") for p in predicates]
        if len(_SPLICE_TARGETS) >= 32:
            _SPLICE_TARGETS.clear()
        _SPLICE_TARGETS[key] = (target, slot, predicates, words)
    return _SPLICE_TARGETS[key]


def _span_bounds(env, text):
    """Word-aligned positions where a quantity reading can start and end. Every
    derivation of the quantity grammar starts with a term or the elapsed prefix
    and ends with a term or the points suffix, so no readable span is skipped."""
    names = [w for decl in env.constants.values() if decl.verbalisation is not None
             for w in {decl.verbalisation, sentence_initial(decl.verbalisation)}]
    prefixes, suffixes = [], []
    for record in env.units.values():
        display = record["display"]
        if display["kind"] == "money":
            prefixes += [display["currency"] + " "] + ([display["input_symbol"]] if "input_symbol" in display else [])
        elif display["kind"] == "decimal":
            if display.get("placement") == "prefix":
                prefixes.append(display["label"] + " ")
            else:
                suffixes.append(" " + display["label"])
    elapsed = (_ELAPSED_PREFIX, _ELAPSED_PREFIX[:1].lower() + _ELAPSED_PREFIX[1:])
    starts, ends = [], []
    for i in range(len(text)):
        if (i == 0 or text[i - 1] == " ") and (
                "0" <= text[i] <= "9" or text[i] == "-" or
                any(text.startswith(w, i) for w in (*names, *prefixes, *elapsed))):
            starts.append(i)
    for j in range(1, len(text) + 1):
        if (j == len(text) or text[j] in " ,;:") and (
                "0" <= text[j - 1] <= "9" or text[j - 1] == "%" or
                any(text.endswith(w, 0, j) for w in (*names, *suffixes, POINTS_SUFFIX))):
            ends.append(j)
    return starts, ends


def _quantity_spans(env, text, d):
    """Every word-aligned span of `text` (a sentence without its full stop), other
    than the whole text, that the quantity grammar reads alone: (start, end, its
    readings). Each span tried and its derivations are charged to d's budget."""
    starts, ends = _span_bounds(env, text)
    spans = []
    for i in starts:
        for j in ends:
            if j <= i or (i, j) == (0, len(text)):
                continue
            d.tick()
            phrase = text[i:j] if i == 0 else sentence_initial(text[i:j])
            sub = _Derivations(env, d.budget)
            try:
                _quantity_readings(env, phrase, sub)
            except ResourceLimit:
                raise
            except VEError:
                continue
            if sub.readings:
                spans.append((i, j, sub.readings))
    return spans


def _splice_readings(env, source):
    """Every reading of `source` that puts quantity wordings inside the core
    English frame. For each word-aligned span the quantity grammar reads alone
    (with every reading it has) and every non-overlapping choice of such spans,
    each chosen span is replaced by a fresh yes/no stand-in, the frame is read by
    the core English grammar over the erased environment plus the stand-ins, the
    span readings are put back, and Lean admits the joined statement. The whole
    sentence as one span is the quantity grammar's own reading and the empty
    choice is the core grammar's, so neither is repeated here. Every span tried,
    choice, frame and joined reading is charged to one MAX_DERIVATIONS budget."""
    from ..ast import formula_to_data
    from ..english import parse_english
    if type(source) is not str or len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        return []
    source = " ".join(source.split())
    if not source.endswith("."):
        return []
    text = source[:-1]
    d = _Derivations(env)
    spans = _quantity_spans(env, text, d)
    if not spans:
        return []
    target, slot, predicates, words = _splice_target(env, len(spans), source)
    fresh = {slot, *predicates}

    def choices(start, chosen):
        for k in range(start, len(spans)):
            i, j, _ = spans[k]
            if chosen and spans[chosen[-1]][1] >= i:
                continue
            d.tick()
            yield chosen + [k]
            yield from choices(k + 1, chosen + [k])

    def put_back(node, back):
        if isinstance(node, list):
            if len(node) == 3 and node[0] == "unary" and node[1] in back and node[2] == ["const", slot]:
                return back[node[1]]
            return [put_back(x, back) for x in node]
        return node

    def mentions_fresh(node):
        return (any(mentions_fresh(x) for x in node) if isinstance(node, list)
                else node in fresh)

    def stand_ins(node, out):
        if isinstance(node, list):
            if len(node) == 3 and node[0] == "unary" and node[2] == ["const", slot]:
                out.append(node[1])
            for x in node:
                stand_ins(x, out)
        return out

    for chosen in choices(0, []):
        frame, last = [], 0
        for n, k in enumerate(chosen):
            i, j, _ = spans[k]
            frame += [text[last:i], words[n]]
            last = j
        frame_text = "".join(frame + [text[last:], "."])
        d.tick()
        try:
            document = parse_english(target, frame_text)
        except (AmbiguousDerivation, ResourceLimit):
            raise
        except VEError:
            continue
        if len(document.formulas) != 1:
            continue
        data = formula_to_data(target, document.formulas[0])
        if sorted(stand_ins(data, [])) != sorted(predicates[:len(chosen)]):
            continue  # each chosen span must be read exactly once, as its own stand-in
        for picks in product(*(spans[k][2] for k in chosen)):
            joined = put_back(data, {predicates[n]: pick["formula"] for n, pick in enumerate(picks)})
            if not mentions_fresh(joined):
                d.offer(joined)
    return d.readings


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
    if surface == "english":
        # The splice's readings count with the other grammars'. A span or frame it
        # cannot read is no reading, not an error of the sentence: the messages of
        # the two grammars above stay the ones reported.
        from ..wire import canonical_json
        try:
            spliced = _splice_readings(env, source)
        except (AmbiguousDerivation, ResourceLimit):
            raise
        except VEError:
            spliced = []
        for canonical in spliced:
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
    return _quantity_wording(env, canonical["formula"], True) + "."


def _quantity_wording(env, formula, initial):
    """The quantity wording of one admitted comparison, without its full stop;
    `initial` says whether it starts the sentence."""
    if formula[0] not in _QUANTITY_OPS:
        raise UnsupportedProfile("No controlled W6 wording for this operation")

    def term(node, first=False):
        if node[0] == "num" and len(node) == 3:
            return render_coordinate(node[1], int(node[2]), env)
        if node[0] == "const":
            declaration = env.constants.get(node[-1])
            if declaration is not None and declaration.verbalisation is not None:
                words = declaration.verbalisation
                return sentence_initial(words) if first and initial else words
        raise UnsupportedProfile("Quantity English requires named constants or literals")

    def kind(tag):
        return env.units[tag]["display"]["kind"] if tag in env.units else None

    if (formula[0] == "eq" and formula[1][0] == "add" and
            formula[1][3][0] == "scale" and formula[1][3][2] == "-1" and
            formula[2][0] == "num" and formula[1][1] == formula[2][1] and
            kind(formula[2][1]) == "percent"):
        amount = render_coordinate(formula[2][1], int(formula[2][2]), env).removesuffix("%")
        return (f"{term(formula[1][2], True)} minus {term(formula[1][3][3])} equals "
                f"{amount}{POINTS_SUFFIX}")
    if (formula[0] == "eq" and formula[2][0] == "add" and
            formula[2][3][0] == "scale" and formula[2][3][2] == "-1" and
            formula[2][1] == formula[2][3][1] and kind(formula[2][1]) == "money"):
        return f"{term(formula[1], True)} equals {term(formula[2][2])} minus {term(formula[2][3][3])}"
    if formula[0] == "elapsed_days":
        prefix = _ELAPSED_PREFIX if initial else _ELAPSED_PREFIX[:1].lower() + _ELAPSED_PREFIX[1:]
        return f"{prefix}{term(formula[1])} to {term(formula[2])} equals {term(formula[3])}"
    left, right = term(formula[1], True), term(formula[2])
    if formula[0] == "within_days":
        return f"{left} is on or after {right} and on or before {formula[3]} days after {right}"
    if formula[0] == "shift_days":
        return f"{left} is {formula[3]} days after {right}"
    connector = {"eq": " equals ", "lt": " is less than ", "le": " is at most ",
                 "date_on": " is on ", "date_before": " is before ",
                 "date_after": " is after ", "date_no_later": " is no later than "}[formula[0]]
    return left + connector + right


def render_w6_sentence(env, canonical):
    """One sentence for an admitted ve-units@1 statement: the quantity wording
    when the whole statement is one comparison, else the splice's layout (relb
    F1): each comparison under if/and/or/not becomes a fresh yes/no stand-in, the
    core English renderer lays out the frame over the erased environment plus the
    stand-ins, and each stand-in's wording is replaced by its comparison's
    quantity wording. parse_w6_sentence reads the result back through the splice."""
    try:
        return render_quantity_sentence(env, canonical)
    except UnsupportedProfile:
        pass
    from ..ast import formula_from_data
    from ..english import render_english
    checked, _ = elaborate_quantity(env, canonical)
    if checked != canonical or canonical["traces"]:
        raise UnsupportedProfile("Quantity wording cannot omit canonical annotations or trace declarations")
    atoms = []

    def frame(node, slot, predicates):
        if node[0] in _FRAME_OPS:
            return [node[0], *(frame(x, slot, predicates) for x in node[1:])]
        if node[0] in _QUANTITY_OPS:
            try:
                _quantity_wording(env, node, False)
            except UnsupportedProfile:
                return node
            atoms.append(node)
            return ["unary", predicates[len(atoms) - 1], ["const", slot]]
        return node

    def count(node):
        return (1 if node[0] in _QUANTITY_OPS else
                sum(count(x) for x in node[1:]) if node[0] in _FRAME_OPS else 0)

    target, slot, predicates, words = _splice_target(env, count(canonical["formula"]), "")
    data = frame(canonical["formula"], slot, predicates)
    text = render_english(formula_from_data(target, data), target).strip()
    for n, atom in enumerate(atoms):
        at = text.find(words[n])
        if at == -1 or text.find(words[n], at + 1) != -1:
            raise UnsupportedProfile("The core English layout does not keep each quantity stand-in once")
        text = text[:at] + _quantity_wording(env, atom, at == 0) + text[at + len(words[n]):]
    return text if text.endswith(".") else text + "."


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
