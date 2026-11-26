"""Sums of amounts for written legal items (statute-feature-sums-build; manage-agents
reviews/spare/statute-corpus/feature-sums/PROPOSAL.md v2).

An amount may be the SUM of amounts the rules or the case already fix, written in one of four forms:

* named terms (2.1): "X equals A plus B." and "X equals the sum of A, B, ... and Z." (the W6 quantity grammar,
  ve/surface/time.py, reads and renders them with exactly one reading);
* over the case's items (2.2): "X equals the sum, over each <kind> that <condition>, of <the kind's amount>."
  (the condition may be left out: "over each <kind>, of ...");
* over the days of a period (2.3): "X equals the sum, over each day of the period beginning with <A> and ending
  with <B>, of <the day's amount>." (optionally "... ending with <B> on which <condition>, of ...");
* over the weeks of a period: "X equals the sum, over each week of the period beginning with <A> and ending with
  <B>, of <the week's amount>." (the period is a whole number of weeks; a partial week is refused).

This lowering is the shell's, as the date lowering (dates.py) is: for one case it expands a written sum into a
ground add chain over named constants (PROPOSAL 2.4, 6) and returns the environment with the step constants it
adds, the quantity statements and their checked-English read-back. Lean checks the statements as it checks any
add chain today: no Lean node, no kernel rule, no division and no rounding is added. The read-back lists every
item or day, so a wrong period end or a missing item is visible there; the template sentence's own parse checks
only that it has one reading (PROPOSAL 4).

Soundness rules (PROPOSAL 2.5, 2.6), each a refusal (`SumRuleError`), never a default:

* an item sum needs the case's completeness premise ("The payments of this case are exactly p4 and p5.", given as
  case["items"]["payment"] = ["p4", "p5"]); without it the sum is refused, and with it and no item the sum is 0;
* every summand is a constant of the environment with the sum's unit; a missing one is refused, never read as 0;
* every condition atom is decided TRUE or FALSE for every item or day (stated in case["facts"] or decided by the
  caller's `decide`); an unknown atom is refused, naming the item or day and the atom (open world);
* period ends are dates every case gives (a written date, a case date, a `Let`-free offset in days of one); a
  concluded date or a date the case may lack does not bound a sum; a period whose start is after its end is
  refused (a case error, not 0);
* more than MAX_SUM_TERMS (60) summands is refused at run time (Lean's quantity decoder takes a term depth of 64);
* a running or cumulative total ("the first day on which the total reaches ...", a sum whose own amount appears in
  its condition, its summand or its period) is CANNOT;
* a sum's amount is defined by exactly one sum: two sums of one case that conclude the same amount are refused
  (`lower_sum_items`).
"""
from __future__ import annotations

import re
from datetime import date, timedelta

from ..ast import numeral_value
from ..environment import Environment
from ..errors import ResourceLimit, SyntaxError, VEError
from ..units import elaborate_quantity, sentence_initial
from .time import MAX_SUM_TERMS, _SUM_KINDS, _chain, parse_w6_sentence, render_w6_sentence

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December")
_EPOCH = date(1970, 1, 1)
# Words that make a sum a running or cumulative total compared day by day (PROPOSAL 2.6): CANNOT.
_RUNNING = re.compile(r"\b(?:running|cumulative|cumulatively|so far|to date|"
                      r"first (?:day|week|date) (?:on|in) which|reaches or (?:passes|exceeds)|"
                      r"total (?:reaches|exceeds|passes))\b", re.IGNORECASE)
_PERIOD = re.compile(r"(?P<x>.+?) equals the sum, over each (?P<unit>day|week) of the period beginning with "
                     r"(?P<a>.+?) and ending with (?P<b>.+?)(?: on which (?P<cond>.+?))?, of (?P<amt>.+)")
_ITEMS = re.compile(r"(?P<x>.+?) equals the sum, over each (?P<kind>[a-z][a-z ]*?)(?: that (?P<cond>.+?))?, "
                    r"of (?P<amt>.+)")


class SumRuleError(SyntaxError):
    """A written sum the lowering refuses (the message names the rule)."""


class SumRuleBound(SumRuleError):
    """CANNOT: more than MAX_SUM_TERMS summands in one case (a case-size limit, refused at run time)."""


class SumRuleRunning(SumRuleError):
    """CANNOT: a running or cumulative total (PROPOSAL 2.6)."""


def long_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


# Any spelling of a marker is a marker (review A3: "[Outside: ...", "[OUTSIDE : ..."); a word OUTSIDE with no marker
# shape is refused too.
_OUTSIDE = re.compile(r"\[\s*OUTSIDE\s*:\s*([a-z]+)\s*:([^\]]*)\]", re.IGNORECASE)
_OUTSIDE_KINDS = ("product", "multiple", "rounding")
# Words an OUTSIDE marker may not hide (PROPOSAL 2.6, F9): a sum, a period end, an item condition or an exclusion.
# A word list cannot close this (review A3): an "other" marker (free text) is refused in a sum item whatever its
# words, and the judges enforce the rest (F9).
_HIDDEN = re.compile(r"\b(?:sum|sums|total|totals|aggregate|added|add|plus|together|each day|each week|for each|"
                     r"period|beginning|ending|other than|excluding|except|unless|only|not|disregard|disregarded|save|"
                     r"counted|count|include|includes|including|first day|first week|on which|in which|reaches|"
                     r"passes|exceeds)\b", re.IGNORECASE)
# A day or week condition that may hide a running total (review A4): a word about the days before, or a comparison
# of an amount. A word list cannot close this either; the judges enforce the rest (PROPOSAL 2.6).
_RUNNING_CONDITION = re.compile(r"\b(?:yet|already|until|by then|earlier|previous|preceding|remaining|balance|"
                                r"exhausted|used up|met|reached|limit)\b", re.IGNORECASE)
_TEMPLATE = re.compile(r"The .+ of this case are exactly <listed by the case>\.")


def lower_written_item(env, text, case=None, **options):
    """A whole written item: lines of sentences, completeness templates ("The payments of this case are exactly
    <listed by the case>."; the case gives the list) and OUTSIDE markers. Refused (CANNOT) when any part, an OUTSIDE
    marker included, is a running or cumulative total, or when an OUTSIDE marker hides a sum, a period end, an item
    condition or an exclusion (F9). Every sum sentence is lowered (`lower_sum_items`); the other sentences are
    returned as written, for the caller's grammar. Returns {"sums": [...], "other": [sentences]}."""
    running = _RUNNING.search(text)
    if running:
        raise SumRuleRunning(f"CANNOT (SumRuleRunning): {running[0]!r} in the item is a running or cumulative total "
                             "compared day by day (PROPOSAL 2.6)")
    for marker in _OUTSIDE.finditer(text):
        if marker[1].lower() not in _OUTSIDE_KINDS:
            raise SumRuleError(f"CANNOT (SumRuleOutside): the OUTSIDE marker {marker[0]!r} is of kind {marker[1]!r}; in "
                               f"a sum item only {', '.join(_OUTSIDE_KINDS)} markers are kept (free text may hide a sum, "
                               "a period end, an item condition or an exclusion; F9)")
        hidden = _HIDDEN.search(marker[2])
        if hidden:
            raise SumRuleError(f"CANNOT (SumRuleOutside): the OUTSIDE marker {marker[0]!r} hides {hidden[0]!r}: no "
                               "sum, period end, item condition or exclusion sits inside an OUTSIDE marker (F9)")
    rest = _OUTSIDE.sub(" ", text)
    if re.search(r"\[[^\]]*\boutside\b", rest, re.IGNORECASE):
        raise SumRuleError("CANNOT (SumRuleOutside): a marker that is not of the form [OUTSIDE: <kind>: <words>]")
    sentences = [s.strip() for s in re.split(r"(?<=\.)\s+", " ".join(rest.split())) if s.strip()]
    sums, other = [], []
    for s in sentences:
        if _TEMPLATE.fullmatch(s):
            continue
        # A rule ("If ..., then X equals A plus B.") is the W6 grammar's, not a sum definition (review C).
        is_sum = not s.startswith("If ") and (" equals the sum" in s or re.search(r" equals .+ plus ", s))
        (sums if is_sum else other).append(s)
    lowered = lower_sum_items(env, sums, case, **options)
    # A sum's amount is defined by its sum only (PROPOSAL 2.5, review B1): another sentence of the item that gives it
    # a value is refused. No wording check can tell a harmless mention from one that gives a value ("GBP 1.00 equals
    # the total.", a rule's conclusion, or a condition whose rule concludes something false), so every other sentence
    # of the item that mentions the amount is refused; a rule that tests a total goes in another item (Opus review B1
    # of the promotion to main and its re-review).
    for item in lowered:
        phrase = env_phrase(item["environment"], item["concludes"])
        mention = re.compile(rf"(?<![\w-]){re.escape(phrase)}(?![\w-])", re.IGNORECASE)
        for s in other:
            if mention.search(s):
                raise SumRuleError(f"SumRule: {s!r} gives a value to {phrase!r}, which its sum defines; an amount a "
                                   "sum defines is defined once (PROPOSAL 2.5)")
    return {"sums": lowered, "other": other}


def env_phrase(env, name):
    return env.constants[name].verbalisation


def lower_sum_items(env, texts, case=None, **options):
    """Several written sums of one case, each lowered in turn on the environment the one before returns. Two sums
    that conclude one amount are refused: a sum's amount is a fresh constant defined once (PROPOSAL 2.5)."""
    out, concluded, uses = [], {}, {}
    for text in texts:
        lowered = lower_sum_item(env, text, case, **options)
        name = lowered["concludes"]
        if name in concluded:
            if [p["formula"] for p in concluded[name][1]["premises"]] == [p["formula"] for p in lowered["premises"]]:
                continue  # the same formula twice (PROPOSAL 2.5 allows it)
            raise SumRuleError(f"SumRule: {concluded[name][0]!r} and {text!r} both define {name!r}; an amount is the "
                               "sum of one written sum (PROPOSAL 2.5)")
        concluded[name] = (text, lowered)
        steps = set(lowered["environment"].constants) - set(env.constants)
        uses[name] = {c for p in lowered["premises"] for c in _constants_in(p["formula"])} - steps - {name}
        env = lowered["environment"]
        out.append(lowered)
    # A sum's amount is fresh (PROPOSAL 2.5): no sum may read, through any chain of sums, an amount that is defined by
    # a sum reading it (review A2: x = a + y and y = b + x make the premises inconsistent).
    def reaches(start, seen):
        for c in uses.get(start, ()):
            if c == target:
                return True
            if c not in seen:
                seen.add(c)
                if reaches(c, seen):
                    return True
        return False
    for target in uses:
        if reaches(target, set()):
            raise SumRuleRunning(f"CANNOT (SumRuleCycle): the sum of {target!r} reads, through other sums, its own "
                                 "amount; a sum's amount is fresh (PROPOSAL 2.5)")
    return out


def _constants_in(f, out=None):
    out = set() if out is None else out
    if isinstance(f, list):
        if len(f) == 3 and f[0] == "const" and isinstance(f[2], str):
            out.add(f[2])
        elif len(f) == 2 and f[0] == "const" and isinstance(f[1], str):
            out.add(f[1])
        else:
            for x in f[1:]:
                _constants_in(x, out)
    return out


def lower_sum_item(env, text, case=None, *, facts=None, decide=None):
    """Lower one written sum sentence for one case.

    `case`: {"items": {"payment": ["p4", "p5"]}, "dates": {"the notice day": "2026-03-30"},
    "facts": [formula, ...]} (the case's completeness premises, its dates and its stated facts). `facts`: readings
    of condition sentences ({"the payment (p4) is held as security for the tenancy": formula}); others go to the
    W6 English grammar. `decide(formula)`: True, False or None for a condition atom the case does not state.
    Returns {"environment", "premises" (quantity statements), "readback" (checked English sentences, the
    completeness premise first), "terms" (the summand constants in order), "concludes" (the sum's constant)}."""
    case = case or {}
    text = " ".join(text.split())
    if not text.endswith("."):
        raise SumRuleError(f"SumRule: a sentence ends with a full stop: {text!r}")
    body = text[:-1]
    running = _RUNNING.search(body)
    if running:
        raise SumRuleRunning(f"CANNOT (SumRuleRunning): {running[0]!r} in {text!r} is a running or cumulative "
                             "total compared day by day (PROPOSAL 2.6)")
    m = _PERIOD.fullmatch(body)
    if m:
        return _lower_period(env, text, m, case, facts, decide)
    if "equals the sum, over each " in body:
        m = _ITEMS.fullmatch(body)
        if not m or " day of the period" in m["kind"] or m["kind"] in ("day", "week"):
            raise SumRuleError(f"SumRule: not a written sum form: {text!r}")
        return _lower_items(env, text, m, case, facts, decide)
    if " equals the sum" in body or " plus " in body:
        return _lower_named(env, text)
    raise SumRuleError(f"SumRule: not a written sum: {text!r}")


# --- named terms (2.1) -----------------------------------------------------------------------------------------

def _lower_named(env, text):
    try:
        canonical = parse_w6_sentence(env, text)
    except ResourceLimit as exc:
        if "SumBound" in str(exc):
            raise SumRuleBound(str(exc)) from exc
        raise
    formula = canonical["formula"]
    if formula[0] != "eq" or formula[2][0] != "add" or formula[1][0] != "const":
        raise SumRuleError(f"SumRule: {text!r} is not a sum of named terms")
    leaves, node = [], formula[2]
    while node[0] == "add" and node[2][0] in ("const", "num"):
        leaves.append(node[2])
        node = node[3]
    leaves.append(node)
    if any(leaf[0] not in ("const", "num") for leaf in leaves):
        raise SumRuleError(f"SumRule: {text!r} is not a sum of named terms")
    x = formula[1][-1]
    if any(leaf[0] == "const" and leaf[-1] == x for leaf in leaves):
        raise SumRuleRunning(f"CANNOT (SumRuleRunning): {text!r} adds its own amount")
    named = [leaf[-1] for leaf in leaves if leaf[0] == "const"]
    if len(set(named)) != len(named):
        raise SumRuleError(f"SumRule: {text!r} adds one amount more than once: a multiple, not a sum (PROPOSAL 2.0; "
                           "written [OUTSIDE: multiple: ...])")
    checks = []
    return {"environment": env, "premises": [canonical], "readback": _checked_readback(env, [canonical], checks),
            "readback_checks": checks, "terms": [leaf[-1] if leaf[0] == "const" else leaf for leaf in leaves], "concludes": x}


def _checked_readback(env, statements, checks=None):
    """Each statement's checked English, read back to that statement alone (PROPOSAL 4, review B2): a line with no
    reading, another reading or two readings refuses the sum. The whole W6 English grammar reads each line. A long
    sum line whose terms have " is " in them (e.g. "... to which the employee is entitled for 14 June 2026") can
    exhaust the splice's span budget (MAX_DERIVATIONS); such a line alone is read by the two grammars that can read
    a whole sentence, the quantity grammar (every tiling of the sum) and the core English grammar, and must have
    exactly one reading there; `checks` records which check each line had ("w6" or "quantity+core")."""
    from .time import _core_readings, parse_quantity_sentence
    lines = []
    for s in statements:
        line = render_w6_sentence(env, s)
        try:
            back, how = parse_w6_sentence(env, line), "w6"
        except ResourceLimit as exc:
            if "MAX_DERIVATIONS" not in str(exc) or s["formula"][0] != "eq" or s["formula"][2][0] != "add":
                raise
            try:
                back, how = parse_quantity_sentence(env, line), "quantity+core"
            except VEError as inner:
                raise SumRuleError(f"SumRule: the read-back {line!r} does not read back ({inner})") from inner
            try:
                _core_readings(env, line, "english")
            except ResourceLimit:
                raise
            except VEError:
                pass
            else:
                raise SumRuleError(f"SumRule: the read-back {line!r} has a second reading in the core grammar")
        except VEError as exc:
            raise SumRuleError(f"SumRule: the read-back {line!r} does not read back ({exc})") from exc
        if back != s:
            raise SumRuleError(f"SumRule: the read-back {line!r} reads as another statement")
        if checks is not None:
            checks.append(how)
        lines.append(line)
    return lines


# --- shared ----------------------------------------------------------------------------------------------------

def _constant(env, phrase, initial=False):
    """The one $int constant whose phrase is `phrase` (sentence-initial capital allowed at the start)."""
    found = [name for name, decl in env.constants.items()
             if decl.sort == "$int" and decl.verbalisation is not None and
             (decl.verbalisation == phrase or initial and sentence_initial(decl.verbalisation) == phrase)]
    if len(found) != 1:
        raise SumRuleError(f"SumRule: {phrase!r} names {len(found)} amounts of the environment; a summand or a sum "
                           "is one named amount (a missing summand is never read as 0)")
    return found[0]


def _unit(env, name):
    decl = env.constants[name]
    tag = decl.unit
    if tag not in env.units or env.units[tag]["display"]["kind"] not in _SUM_KINDS:
        raise SumRuleError(f"SumRule: {decl.verbalisation!r} is not an amount of money or a decimal quantity")
    return tag


def _check_not_running(x_phrase, text, *parts):
    for part in parts:
        if part and x_phrase.lower() in part.lower():
            raise SumRuleRunning(f"CANNOT (SumRuleRunning): {text!r} reads its own amount {x_phrase!r} in its "
                                 "condition, summand or period: a running total (PROPOSAL 2.6)")


def _with_steps(env, steps):
    """The environment with fresh step constants: [(name, unit, phrase)]."""
    if not steps:
        return env
    data = env.to_dict()
    constants = data["vocabulary"]["constants"]
    phrases = {decl.verbalisation for decl in env.constants.values() if decl.verbalisation}
    for name, tag, phrase in steps:
        if name in constants or phrase in phrases:
            raise SumRuleError(f"SumRule: the step amount {phrase!r} is already named in the environment; two "
                               "amounts never share one phrase (PROPOSAL 4, F5)")
        phrases.add(phrase)
        constants[name] = {"sort": "$int", "unit": tag, "description": phrase, "verbalisation": phrase}
    return Environment(data)


def _fresh(env, base, count):
    stem = base
    while any(n.startswith(stem) for n in env.constants):
        stem += "_x"
    return [f"{stem}_{k + 1}" for k in range(count)]


def _condition(env, sentence, facts):
    if sentence in (facts or {}):
        return facts[sentence]
    try:
        return parse_w6_sentence(env, sentence_initial(sentence) + ".")["formula"]
    except (ResourceLimit,):
        raise
    except VEError as exc:
        raise SumRuleError(f"SumRule: the condition {sentence!r} has no reading ({exc})") from exc


def _compares_amount(env, f):
    """Whether a formula mentions a money or decimal amount (a constant or a literal of such a unit)."""
    if isinstance(f, list):
        if f and f[0] in ("const", "decimal", "num") and len(f) == 3 and f[1] in env.units:
            return env.units[f[1]]["display"]["kind"] in _SUM_KINDS
        return any(_compares_amount(env, x) for x in f[1:])
    return False


def _atoms(f, out):
    if f[0] in ("and", "or", "implies"):
        for g in f[1:]:
            _atoms(g, out)
    elif f[0] == "not":
        _atoms(f[1], out)
    else:
        out.append(f)
    return out


def _decided(f, stated, decide):
    if f in stated:
        return True
    if ["not", f] in stated:
        return False
    return decide(f) if decide is not None else None


def _guarded(names, amounts, conditions, tag, case, decide, where):
    """Per item or day: the step constant equals the amount when the condition holds and 0 when it does not.
    Every atom of every condition must be decided (open world, PROPOSAL 2.2 F3)."""
    stated = list(case.get("facts", []))
    premises = []
    for name, amount, condition, label in zip(names, amounts, conditions, where):
        for atom in _atoms(condition, []):
            if _decided(atom, stated, decide) is None:
                raise SumRuleError(f"SumRule: the condition atom {atom!r} is not stated or decided TRUE or FALSE "
                                   f"for {label}; the sum is refused (open world, PROPOSAL 2.2)")
        step = ["const", tag, name]
        premises.append(["implies", condition, ["eq", step, ["const", tag, amount]]])
        premises.append(["implies", ["not", condition], ["eq", step, ["decimal", tag, "0"]]])
    return premises


def _finish(env, text, x, tag, premises, terms, first_readback=()):
    """The sum's equation over `terms`, every statement elaborated (Lean admits each) and read back."""
    if len(terms) > MAX_SUM_TERMS:
        raise SumRuleBound(f"CANNOT (SumBound): {text!r} has {len(terms)} summands in this case; at most "
                           f"MAX_SUM_TERMS={MAX_SUM_TERMS} (refused at run time)")
    leaves = [["const", tag, t] for t in terms]
    total = (["decimal", tag, "0"] if not leaves else leaves[0] if len(leaves) == 1 else _chain(tag, leaves))
    statements = []
    for f in [*premises, ["eq", ["const", tag, x], total]]:
        canonical, _ = elaborate_quantity(env, {"format": "ve-quantity@1", "formula": f})
        statements.append(canonical)
    checks = []
    readback = [*first_readback, *_checked_readback(env, statements, checks)]
    return {"environment": env, "premises": statements, "readback": readback, "readback_checks": checks,
            "terms": terms, "concludes": x}


# --- over the case's items (2.2) -------------------------------------------------------------------------------

def _lower_items(env, text, m, case, facts, decide):
    kind, cond, amt = m["kind"], m["cond"], m["amt"]
    x = _constant(env, m["x"], True)
    tag = _unit(env, x)
    _check_not_running(env.constants[x].verbalisation, text, cond, amt)
    items = case.get("items", {})
    if kind not in items:
        raise SumRuleError(f"SumRule: the case does not list its {kind}s exactly (no completeness premise for "
                           f"{text!r}); the sum is refused, never 0 (PROPOSAL 2.2 F4)")
    listed = list(items[kind])
    if len(set(listed)) != len(listed):
        raise SumRuleError(f"SumRule: the case lists a {kind} twice: {listed!r}")
    if len(listed) > MAX_SUM_TERMS:
        raise SumRuleBound(f"CANNOT (SumBound): {text!r} has {len(listed)} {kind}s in this case; at most "
                           f"MAX_SUM_TERMS={MAX_SUM_TERMS} (refused at run time)")
    the = f"the {kind}"
    if len(re.findall(rf"\b{re.escape(the)}\b", amt)) != 1:
        raise SumRuleError(f"SumRule: the summand {amt!r} names {the!r} exactly once")
    amounts = []
    for i in listed:
        name = _constant(env, re.sub(rf"\b{re.escape(the)}\b", f"{the} ({i})", amt))
        if _unit(env, name) != tag:
            raise SumRuleError(f"SumRule: the summand of {i} is not in the unit of the sum")
        amounts.append(name)
    premise = (f"The {_plural(kind)} of this case are exactly "
               f"{', '.join(listed[:-1]) + ' and ' + listed[-1] if len(listed) > 1 else ''.join(listed) or 'none'}.")
    if cond is None:
        return _finish(env, text, x, tag, [], amounts, [premise])
    names = _fresh(env, "sum_step", len(listed))
    env2 = _with_steps(env, [(n, tag, f"the amount counted for {the} ({i})") for n, i in zip(names, listed)])
    conditions = [_condition(env2, f"{the} ({i}) {cond}", facts) for i in listed]
    premises = _guarded(names, amounts, conditions, tag, case, decide, [f"{the} ({i})" for i in listed])
    return _finish(env2, text, x, tag, premises, names, [premise])


def _plural(kind):
    *head, last = kind.split(" ")
    if last == "child":
        last = "children"
    elif last == "person":
        last = "persons"
    elif last.endswith("y") and last[-2:-1] not in "aeiou":
        last = last[:-1] + "ies"
    elif last.endswith(("s", "x", "ch", "sh")):
        last += "es"
    else:
        last += "s"
    return " ".join([*head, last])


# --- over the days or weeks of a period (2.3) ------------------------------------------------------------------

def _day(env, phrase, case, text):
    """A period end: a date every case gives, as a day number Lean works out (dates.py reads the wording; "D minus
    N days" is read here, subtracting whole days)."""
    from .dates import DateRuleError, _Item
    minus = re.fullmatch(r"(.+?) minus ([0-9]{1,4}) (day|week)s?", phrase)
    back = 0
    if minus:
        phrase, back = minus[1], numeral_value(minus[2]) * (7 if minus[3] == "week" else 1)
    item = _Item(env, {"dates": case.get("dates", {})}, (), {}, None)
    try:
        reading = item.date(phrase)
    except ResourceLimit:
        raise
    except DateRuleError as exc:
        raise SumRuleError(f"SumRule: the period end {phrase!r} has no date reading ({exc})") from exc
    if reading[0] != "ground":
        raise SumRuleError(f"SumRule: the period end {phrase!r} is not a date every case gives (a concluded date or a "
                           f"date the case may lack does not bound a sum; {text!r})")
    canonical, _ = elaborate_quantity(env, {"format": "ve-quantity@1",
                                            "formula": ["date_on", ["cal", reading[1]], ["cal", reading[1]]]})
    return numeral_value(canonical["formula"][1][2]) - back


def _lower_period(env, text, m, case, facts, decide):
    unit, cond, amt = m["unit"], m["cond"], m["amt"]
    if "day" not in env.units:
        raise SumRuleError("SumRule: a sum over days needs the day unit")
    x = _constant(env, m["x"], True)
    tag = _unit(env, x)
    x_phrase = env.constants[x].verbalisation
    _check_not_running(x_phrase, text, cond, amt, m["a"], m["b"])
    if cond and _RUNNING_CONDITION.search(cond):
        raise SumRuleRunning(f"CANNOT (SumRuleRunning): the day condition {cond!r} of {text!r} may be a running total "
                             f"({_RUNNING_CONDITION.search(cond)[0]!r}); PROPOSAL 2.6")
    a, b = _day(env, m["a"], case, text), _day(env, m["b"], case, text)
    if a > b:
        raise SumRuleError(f"SumRule: the period of {text!r} begins after it ends ({a} > {b} as day numbers); a case "
                           "error, refused, not 0 (PROPOSAL 2.3)")
    step = 1 if unit == "day" else 7
    if (b - a + 1) % step:
        raise SumRuleError(f"CANNOT (SumRule): the period of {text!r} is not a whole number of weeks (a partial week)")
    count = (b - a + 1) // step
    if count > MAX_SUM_TERMS:
        raise SumRuleBound(f"CANNOT (SumBound): {text!r} has {count} {unit}s in this case; at most "
                           f"MAX_SUM_TERMS={MAX_SUM_TERMS} (refused at run time)")
    the = f"the {unit}"
    if len(re.findall(rf"\b{re.escape(the)}\b", amt)) != 1:
        raise SumRuleError(f"SumRule: the summand {amt!r} names {the!r} exactly once")
    starts = [(_EPOCH + timedelta(days=a + k * step)).isoformat() for k in range(count)]
    words = [long_date(s) if unit == "day" else f"the week beginning {long_date(s)}" for s in starts]
    amounts = []
    for w in words:
        phrase = re.sub(rf"\b{re.escape(the)}\b", w, amt)
        name = _constant(env, phrase)
        if _unit(env, name) != tag:
            raise SumRuleError(f"SumRule: the summand for {w} is not in the unit of the sum")
        amounts.append(name)
    if cond is None:
        return _finish(env, text, x, tag, [], amounts)
    names = _fresh(env, "sum_step", count)
    env2 = _with_steps(env, [(n, tag, f"the amount counted for {w}") for n, w in zip(names, words)])
    conditions = [_condition(env2, f"{cond} on {w}" if unit == "day" else f"{cond} in {w}", facts) for w in words]
    for w, c in zip(words, conditions):
        if _compares_amount(env2, c):
            raise SumRuleRunning(f"CANNOT (SumRuleRunning): the condition for {w} compares an amount; a day or week "
                                 "condition on an amount may be a running total (PROPOSAL 2.6, review A4)")
    premises = _guarded(names, amounts, conditions, tag, case, decide, words)
    return _finish(env2, text, x, tag, premises, names)
