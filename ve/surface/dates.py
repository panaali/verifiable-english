"""Date arithmetic for written legal items (date-arith; manage-agents reviews/spare/date-arith/PROPOSAL.md).

The written form (PROPOSAL sections 2.1-2.4) is lowered here to `ve-quantity@1` formulas whose date
expressions Lean works out while decoding (`VE.Time.Wire.elabCal`): a day term `["cal", E]` and a
formula `["cal_cmp", op, E1, E2]`, with `E` one of `["date", "YYYY-MM-DD"]` (1900..9999),
`["plus_months", E, k, reading]`, `["plus_days", E, k]` (k >= 0), `["month_first", E]`,
`["month_last", E]` and `["nth_weekday", n, w, month, year]` (w: 0 = Monday).

"the day after D" is D plus 1 day and "D plus N days|weeks" is D plus that many days (date-arith-day-after). For a
date the case may lack or a concluded date (a day constant c) the term c + k is never a ground expression: a
comparison `t op c + k` (k >= 1) lowers to today's nodes (`shift_days` for "on"; `date_after`/`date_no_later` with
`within_days` for the four orders), so no Lean node is added. Such a term is compared only: it is never a `Let`
value, a rule's conclusion, a period's day or the base of a month, year or minus offset (C3, refused).

This lowering is the shell's: it substitutes the case's dates and the `Let` values, expands the age,
period and week wordings into those nodes, and copies a rule per role (a `Let` sentence that mentions
"the person" is lowered per role too, so each role's rules read that role's dates). It is tested,
not Lean-checked.

A fact over a span of days ("throughout the qualifying week", "any day falling within the week", "for the
week immediately preceding", "for twelve weeks before": a unit singular or plural, a count in digits or
words, its hyphen ASCII or Unicode) is refused (CANNOT): the written form has no reading of it, and the
facts map or the W6 grammar must not read it as a plain fact (rtt2 S4, S10).
Lean computes the arithmetic on the dates supplied here and binds them into the statement's meaning
id (`calInputs`), so a wrong case date is visible in the report, not caught.

Two rules from the design challenge (CHALLENGE.md C2, C3) are enforced here:

* C2: two `If` rules that conclude the same date are refused unless their conditions are
  written exclusive (one rule's condition has, as a top-level `and` part, the negation of a part of
  the other's), since two different concluded values make the premises inconsistent. A rule
  concludes every day constant its lowered conclusion mentions, whatever the wording (an equality
  either way round, "equals", a comparison, a capital letter, the facts map or the W6 grammar): the
  key is the constant in the formula, not the text. A rule never concludes a case date or a date
  the case may lack, nor compares fixed dates only; a `Let` sentence never names a day constant.
* C3: a named date the case may lack (`may_lack`) lowers to an ordinary day constant compared with
  today's nodes (`date_on`, `date_before`, `date_after`, `date_no_later`, `within_days`), never to a
  ground expression; it cannot be offset by months or years or used in a `Let`. A case that gives
  it adds the fact `date_on(constant, date)`; a case that lacks it adds nothing.

A 29 February birth date offset by whole years has no day in a common year; with no reading the
age is refused (Lean's `MissingDay`), never guessed (CHALLENGE.md C11).
"""
from __future__ import annotations

import re

from ..ast import numeral_value
from ..errors import ResourceLimit, SyntaxError, VEError

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
ORDINALS = ("first", "second", "third", "fourth")
MAX_READINGS = 10_000
_OPS = ((" is on or before ", "on_or_before"), (" is on or after ", "on_or_after"), (" is before ", "before"),
        (" is after ", "after"), (" is on ", "on"))
# The comparison read from the other side: `a op b` is `b _MIRROR[op] a`.
_MIRROR = {"before": "after", "after": "before", "on": "on", "on_or_before": "on_or_after",
           "on_or_after": "on_or_before"}
# The existing date node and argument order for each comparison over day terms.
_DAY_NODES = {"before": ("date_before", False), "after": ("date_after", False), "on": ("date_on", False),
              "on_or_before": ("date_no_later", False), "on_or_after": ("date_no_later", True)}


class DateRuleError(SyntaxError):
    """A written date item the lowering refuses (the message names the rule)."""


class DateRuleBound(DateRuleError):
    """CANNOT: a count, day or year in the item text has more than `MAX_COUNT_DIGITS` digits. Never converted,
    never read some other way: every handler that tries another reading after a `DateRuleError` re-raises it."""


# A count of years, months, weeks or days, an ordinal, a day of the month or a year read from the item or the
# case: at most this many digits (date-arith full gate, test_numeral_conversion). 999999 days is past 1900..9999.
MAX_COUNT_DIGITS = 6


def _count(text):
    """The value of a digit run read from a date item, or CANNOT above `MAX_COUNT_DIGITS` digits (refused, not
    converted: `int` of a long digit string raises a bare ValueError past the interpreter's digit limit)."""
    if not re.fullmatch(r"[0-9]+", text):
        raise DateRuleError(f"DateRule: {text!r} is not a count in digits")
    if len(text) > MAX_COUNT_DIGITS:
        raise DateRuleBound(f"CANNOT (DateRuleBound): a count of {len(text)} digits; a date item reads at most "
                            f"{MAX_COUNT_DIGITS}")
    return numeral_value(text)


def _case_year(name, value):
    """A year the case fixes: an int or a digit string, at most `MAX_COUNT_DIGITS` digits (CANNOT above)."""
    if type(value) is int:
        if not 0 <= value < 10 ** MAX_COUNT_DIGITS:
            raise DateRuleBound(f"CANNOT (DateRuleBound): the year {name!r} lies outside "
                                f"0..{10 ** MAX_COUNT_DIGITS - 1}")
        return value
    if isinstance(value, str):
        return _count(value)
    raise DateRuleError(f"DateRule: the year {name!r} is not a number")


# A count in a duration-span phrase: digits, or a written count up to "nine hundred and ninety-nine" (Codex
# re-check MEDIUM 1: "for twelve weeks immediately preceding").
_ONES = r"one|two|three|four|five|six|seven|eight|nine"
_UNDER_100 = (rf"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[- ](?:{_ONES}))?|ten|eleven|twelve|"
              rf"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|{_ONES}")
_COUNT = rf"(?:[0-9]+|(?:a|{_ONES}) hundred(?:(?: and)? (?:{_UNDER_100}))?|{_UNDER_100})"
# A fact that must hold on every day, or on some day, of a span of days (rtt2 S4, S10). A duration span is
# "for" + an optional article + an optional count (digits or written) + a unit, singular or plural ("for the
# week immediately preceding", "for twelve weeks before", "for a period of 12 weeks ending with").
_SPAN = re.compile(r"\b(?:throughout|any day|every day|each day|some day|all days|a day (?:in|within|falling|of)|"
                   r"days? falling (?:in|within)|any time|all times|at no time|for the (?:whole|entire)|continuously|"
                   rf"for (?:the |a |an |any |each |every )?(?:(?:continuous )?period of )?(?:{_COUNT} )?"
                   r"(?:day|week|month|year)s? (?:immediately )?"
                   r"(?:preceding|before|after|following|prior to|ending|beginning|starting))\b", re.IGNORECASE)
# For the span check only: a Unicode hyphen or dash (U+2010..U+2015, U+2212) reads as "-" and a no-break space
# (U+00A0, U+2007, U+202F) as " ", so "for twenty\u2011six weeks before" is refused exactly as its ASCII form is
# (Codex re-check 2 MEDIUM). Other paths read the sentence as written.
_SPAN_FOLD = str.maketrans({**{c: "-" for c in "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"},
                            **{c: " " for c in "\u00a0\u2007\u202f"}})
# The nodes whose arguments are day terms (today's date nodes and ve-units@1 comparisons of days).
_DAY_TERMS = ("num", "cal", "const")


def _day_constants_in(f):
    """The day constants a formula mentions, in order, and whether it mentions a day term at all."""
    found, any_day = [], False
    stack = [f]
    while stack:
        x = stack.pop()
        if not isinstance(x, list) or not x:
            continue
        # A raw ["date", iso] term (the W6 grammar's and the facts map's spelling of a fixed day) is a day term
        # too (Codex re-check MEDIUM 2), so a conclusion over fixed dates only is refused whichever path lowered it.
        if x[0] == "date" and len(x) == 2 and isinstance(x[1], str):
            any_day = True
            continue
        if x[0] == "cal_cmp" or x[0] == "cal" or (x[0] in ("num", "const") and len(x) == 3 and x[1] == "day"):
            any_day = True
            if x[0] == "const" and x[2] not in found:
                found.append(x[2])
            if x[0] != "cal_cmp":
                continue
        stack.extend(reversed(x[1:]))
    return found, any_day


def _ordinal(text):
    m = re.fullmatch(r"([1-9][0-9]*)(?:st|nd|rd|th)", text)
    return _count(m[1]) if m else None


class _Item:
    """One item's lowering state: the case, the `Let` values, the constants and the facts."""

    def __init__(self, env, case, may_lack, facts, roles):
        self.env, self.facts, self.roles = env, dict(facts or {}), list(roles or ["the person"])
        self.dates = dict((case or {}).get("dates", {}))
        self.years = dict((case or {}).get("years", {}))
        self.may_lack = {name.replace("the person", role) for name in may_lack or () for role in self.roles} | set(
            may_lack or ())
        self.work, self.scope, self.let_scopes, self.let_years = 0, None, {}, {}
        self.day_constants = {decl.verbalisation: name for name, decl in env.constants.items()
                              if decl.verbalisation and decl.sort == "$int" and decl.unit == "day"}

    @property
    def lets(self):
        """The `Let` values of the current scope: None for a rule not copied per role, else the role."""
        return self.let_scopes.setdefault(self.scope, {})

    def tick(self):
        self.work += 1
        if self.work > MAX_READINGS:
            raise ResourceLimit(f"date lowering budget MAX_READINGS={MAX_READINGS} exhausted")

    # --- dates (PROPOSAL 2.1): ("ground", E), ("const", constant name) or ("shifted", constant name, k >= 1),
    # the day k days after the constant's day (date-arith-day-after) --------------------------------------------

    def date(self, text):
        text = text.strip()
        self.tick()
        m = re.fullmatch(r"(.+?) (plus|minus) (.+?)(?:,? \(?reading: (last|next) day\)?)?", text)
        if m and self._offset(m[3]) is not None:
            months, days = self._offset(m[3])
            base = self.date(m[1])
            sign = -1 if m[2] == "minus" else 1
            if base[0] != "ground":
                # A wording that names months or years is refused even with a count of 0 (Opus review C1).
                if sign > 0 and not months and not m[4] and not re.search(r"\b(?:year|month)s?\b", m[3]):
                    return self.shift(base, days, text)
                raise DateRuleError(f"DateRule: a date the case may lack ({text!r}) is offset forward by days or "
                                    "weeks only, or in a period wording (C3)")
            e = base[1]
            if months:
                e = ["plus_months", e, str(sign * months), m[4] or "none"]
            elif m[4]:
                raise DateRuleError(f"DateRule: a reading follows a month or year offset only ({text!r})")
            if days:
                if sign < 0:
                    raise DateRuleError(f"DateRule: a ground date minus days or weeks is not supported ({text!r})")
                e = ["plus_days", e, str(days)]
            return ("ground", e)
        # A name the case, a Let or a day constant gives keeps its reading (the wording below is not tried on it).
        m = re.fullmatch(r"the day after (.+)", text)
        if m and not self.is_name(text):
            return self.shift(self.date(m[1]), 1, text)
        m = re.fullmatch(r"([1-9]|[12][0-9]|3[01]) ([A-Z][a-z]+) ([0-9]{4})", text)
        if m and m[2] in MONTHS:
            return ("ground", ["date", f"{m[3]}-{MONTHS.index(m[2]) + 1:02d}-{_count(m[1]):02d}"])
        m = re.fullmatch(r"the first day of the month of (.+)", text)
        if m:
            return ("ground", ["month_first", self.ground(m[1], text)])
        m = re.fullmatch(r"the last day of the month of (.+)", text)
        if m:
            return ("ground", ["month_last", self.ground(m[1], text)])
        m = re.fullmatch(r"the last day of the (\S+) month after the month of (.+)", text)
        if m and _ordinal(m[1]):
            return ("ground", ["month_last", ["plus_months", ["month_first", self.ground(m[2], text)],
                                              str(_ordinal(m[1])), "none"]])
        m = re.fullmatch(r"the (first|second|third|fourth) ([A-Z][a-z]+) in ([A-Z][a-z]+) (?:of )?(.+)", text)
        if m and m[2] in WEEKDAYS and m[3] in MONTHS:
            year = _count(m[4]) if re.fullmatch(r"[0-9]{4}", m[4]) else self.year(m[4])
            return ("ground", ["nth_weekday", ORDINALS.index(m[1]) + 1, WEEKDAYS.index(m[2]),
                               MONTHS.index(m[3]) + 1, year])
        m = re.fullmatch(r"the last day of the period of ([1-9][0-9]*) days beginning with (.+)", text)
        if m:
            return ("ground", ["plus_days", self.ground(m[2], text), str(_count(m[1]) - 1)])
        m = re.fullmatch(r"the (\S+) day of the period beginning with (.+)", text)
        if m and _ordinal(m[1]):
            return ("ground", ["plus_days", self.ground(m[2], text), str(_ordinal(m[1]) - 1)])
        m = re.fullmatch(r"the last day of the week beginning (.+)", text)
        if m:
            return ("ground", ["plus_days", self.ground(m[1], text), "6"])
        m = re.fullmatch(r"the day (.+) attains the age of ([0-9]+) years?(?: and ([0-9]+) months?)?"
                         r"(?:,? \(?reading: (last|next) day\)?)?", text)
        if m:
            months = 12 * _count(m[2]) + _count(m[3] or "0")
            return ("ground", ["plus_months", self.birth(m[1]), str(months), m[4] or "none"])
        return self.named(text)

    def _offset(self, text):
        """`N years and M months and ...`: (months, days), or None."""
        months = days = 0
        for part in text.split(" and "):
            m = re.fullmatch(r"([0-9]+) (year|month|week|day)s?", part.strip())
            if not m:
                return None
            n = _count(m[1])
            months += {"year": 12 * n, "month": n}.get(m[2], 0)
            days += {"week": 7 * n, "day": n}.get(m[2], 0)
        return months, days

    def is_name(self, text):
        return (text in self.lets or text in self.may_lack or text in self.day_constants or text in self.dates)

    def shift(self, d, k, text):
        """The day `k` (>= 0) days after the date `d`: a ground `plus_days`, or ("shifted", constant, total)."""
        if k == 0:
            return d
        if d[0] == "ground":
            return ("ground", ["plus_days", d[1], str(k)])
        total = k + (d[2] if d[0] == "shifted" else 0)
        if total >= 10 ** MAX_COUNT_DIGITS:
            raise DateRuleBound(f"CANNOT (DateRuleBound): {text!r} is {total} days after a day constant; a date "
                                f"item reads at most {10 ** MAX_COUNT_DIGITS - 1}")
        return ("shifted", d[1], total)

    def ground(self, text, whole):
        d = self.date(text)
        if d[0] != "ground":
            raise DateRuleError(f"DateRule: {whole!r} needs a date every case gives; {text!r} may be absent (C3)")
        return d[1]

    def birth(self, role):
        return self.ground(f"the birth date of {role}", f"the birth date of {role}")

    def year(self, name):
        scoped = self.let_years.get(self.scope, {})
        if name in scoped:
            return scoped[name]  # a Let year: _count of four digits
        if name not in self.years:
            raise DateRuleError(f"DateRule: the year {name!r} is not fixed by the case or a Let sentence")
        return _case_year(name, self.years[name])

    def named(self, text):
        if text in self.lets:
            return self.lets[text]
        if text in self.may_lack:
            if text not in self.day_constants:
                raise DateRuleError(f"DateRule: {text!r} may be absent and has no day constant (C3)")
            return ("const", self.day_constants[text])
        if text in self.day_constants and text not in self.dates:
            return ("const", self.day_constants[text])  # a concluded date: an ordinary date of the logic
        if text in self.dates:
            if self.dates[text] is None:
                raise DateRuleError(f"DateRule: the case lacks {text!r}; name it in may_lack (C3)")
            return ("ground", ["date", self.dates[text]])
        raise DateRuleError(f"DateRule: no date reading of {text!r}")

    def term(self, d):
        if d[0] == "shifted":
            raise DateRuleError(f"DateRule: a day {d[2]} days after {d[1]!r} (a date the case may lack or a "
                                "concluded date) is compared only, never used as a day term (C3)")
        return ["cal", d[1]] if d[0] == "ground" else ["const", "day", d[1]]

    # --- comparisons and ages (2.2, 2.3) ------------------------------------------------------------------

    def compare(self, op, a, b):
        if a[0] == "shifted" or b[0] == "shifted":
            (x, i), (y, j) = _unshift(a), _unshift(b)
            # x + i op y + j: the smaller offset cancels, the larger stays on its side.
            if i >= j:
                return self.offset_compare(_MIRROR[op], y, x, i - j)
            return self.offset_compare(op, x, y, j - i)
        if a[0] == "ground" and b[0] == "ground":
            return ["cal_cmp", op, a[1], b[1]]
        node, swap = _DAY_NODES[op]
        x, y = self.term(a), self.term(b)
        return [node, y, x] if swap else [node, x, y]

    def offset_compare(self, op, t, base, k):
        """`t op base + k` (k >= 0, `t` and `base` ground or constant) over today's nodes only."""
        if k == 0:
            return self.compare(op, t, base)
        if base[0] == "ground":
            return self.compare(op, t, ("ground", ["plus_days", base[1], str(k)]))
        if t[0] == "ground" and t[1][0] == "date" and t[1][1] < "1970":
            raise DateRuleError("DateRule: a comparison with a day after a date the case may lack needs dates "
                                "from 1970")
        x, b = self.term(t), self.term(base)

        def within(n):  # x is on or after b and on or before b + n (both days valid)
            return ["within_days", x, b, str(n)]
        # The positive node in each `and`/`or` holds only of valid days, so a `not within` never holds alone.
        return {"on": lambda: ["shift_days", x, b, str(k)],
                "after": lambda: ["and", ["date_after", x, b], ["not", within(k)]],
                "on_or_after": lambda: ["and", ["date_after", x, b], ["not", within(k - 1)]],
                "before": lambda: ["or", ["date_no_later", x, b], within(k - 1)],
                "on_or_before": lambda: ["or", ["date_no_later", x, b], within(k)]}[op]()

    def condition(self, text):
        """Readings of one condition without connectives."""
        out = []
        m = re.fullmatch(r"(.+?) (?:has attained the age of|is aged at least) ([0-9]+)(?: years?)?"
                         r"(?: and ([0-9]+) months?)? on (.+)", text)
        if m:
            out.append(self.age(m[1], _count(m[2]), _count(m[3] or "0"), m[4]))
        m = re.fullmatch(r"(.+?) has reached (?:his|her|their|its) (\S+) birthday on (.+)", text)
        if m and _ordinal(m[2]):
            out.append(self.age(m[1], _ordinal(m[2]), 0, m[3]))
        m = re.fullmatch(r"(.+?) is under the age of ([0-9]+)(?: years?)? on (.+)", text)
        if m:
            out.append(["not", self.age(m[1], _count(m[2]), 0, m[3])])
        m = re.fullmatch(r"(.+?) is in the period of ([1-9][0-9]*) days beginning with (.+)", text)
        if m:
            out.append(self.window(m[1], m[3], _count(m[2]) - 1))
        m = re.fullmatch(r"(.+?) is in the week beginning (.+)", text)
        if m:
            out.append(self.window(m[1], m[2], 6))
        m = re.fullmatch(r"(.+?) is in or before the week beginning (.+)", text)
        if m:
            out.append(self.compare("on_or_before", self.date(m[1]),
                                    ("ground", ["plus_days", self.ground(m[2], text), "6"])))
        m = re.fullmatch(r"(.+?) is in the period (.+?) to (.+)", text)
        if m and not m[2].startswith("of "):
            d = self.date(m[1])
            out.append(["and", self.compare("on_or_after", d, self.date(m[2])),
                        self.compare("on_or_before", d, self.date(m[3]))])
        errors = []
        for connector, op in _OPS:
            start = text.find(connector)
            while start > 0:
                self.tick()
                try:
                    out.append(self.compare(op, self.date(text[:start]), self.date(text[start + len(connector):])))
                except DateRuleBound:
                    raise
                except DateRuleError as exc:
                    errors.append(exc)
                start = text.find(connector, start + 1)
        if text in self.facts:
            out.append(self.facts[text])
        elif not out:
            try:
                out.append(self.fact(text))
            except ResourceLimit:
                raise
            except VEError as exc:  # an input diagnostic only: CheckerUnavailable and any other error propagate
                raise errors[0] if errors else DateRuleError(f"DateRule: no reading of the condition {text!r} "
                                                             f"({exc})") from exc
        return out

    def age(self, role, years, months, on):
        return self.compare("on_or_before", ("ground", ["plus_months", self.birth(role), str(12 * years + months),
                                                         "none"]), self.date(on))

    def window(self, day, start, extra):
        """`day` lies in `start` to `start` plus `extra` days."""
        d, s = self.date(day), self.date(start)
        if "shifted" in (d[0], s[0]):
            return ["and", self.compare("on_or_after", d, s),
                    self.compare("on_or_before", d, self.shift(s, extra, start))]
        if s[0] == "const":
            if d[0] == "ground" and d[1][0] == "date" and d[1][1] < "1970":
                raise DateRuleError("DateRule: a period of a date the case may lack needs dates from 1970")
            return ["within_days", self.term(d), self.term(s), str(extra)]
        return ["and", self.compare("on_or_after", d, s),
                self.compare("on_or_before", d, ("ground", ["plus_days", s[1], str(extra)]))]

    def fact(self, text):
        from .time import parse_w6_sentence
        sentence = text[:1].upper() + text[1:] + "."
        return parse_w6_sentence(self.env, sentence)["formula"]

    def conditions(self, text):
        """Every reading of `and`/`or`/`not`/brackets over conditions; one distinct reading is required."""
        text = text.strip()
        self.tick()
        readings = []
        if text.startswith("(") and _closes(text) == len(text) - 1:
            readings += self.conditions(text[1:-1])
        for word, node in ((" or ", "or"), (" and ", "and")):
            depth_ok = [i for i in _top_level(text, word)]
            for i in depth_ok:
                try:
                    left, right = self.conditions(text[:i]), self.conditions(text[i + len(word):])
                except DateRuleBound:
                    raise
                except DateRuleError:
                    continue
                readings += [[node, a, b] for a in left for b in right]
            if readings:
                break  # `or` binds looser than `and`: an `or` reading is the whole sentence's
        if not readings and text.startswith("not "):
            try:
                readings += [["not", a] for a in self.conditions(text[4:])]
            except DateRuleBound:
                raise
            except DateRuleError:
                pass
        if not readings:
            readings += self.condition(text)
        distinct = {repr(r): r for r in readings}
        if not distinct:
            raise DateRuleError(f"DateRule: no reading of the condition {text!r}")
        return list(distinct.values())


def _unshift(d):
    """(the date without its day offset, the offset)."""
    return (("const", d[1]), d[2]) if d[0] == "shifted" else (d, 0)


def _closes(text):
    depth = 0
    for i, c in enumerate(text):
        depth += (c == "(") - (c == ")")
        if depth == 0:
            return i
    return -1


def _top_level(text, word):
    depth, out, i = 0, [], 0
    while i < len(text):
        c = text[i]
        depth += (c == "(") - (c == ")")
        if depth == 0 and text.startswith(word, i):
            out.append(i)
        i += 1
    return out


def _conjuncts(f):
    return _conjuncts(f[1]) + _conjuncts(f[2]) if f[0] == "and" else [f]


def written_exclusive(a, b):
    """C2: one condition has, as a top-level `and` part, the negation of a part of the other."""
    ca, cb = _conjuncts(a), _conjuncts(b)
    return any(["not", x] in cb for x in ca) or any(["not", x] in ca for x in cb)


def lower_date_item(env, text, case=None, *, may_lack=(), facts=None, roles=None):
    """Lower one written item: its `Let` and `If ..., then ...` sentences.

    `case`: {"dates": {"the birth date of the person": "1960-06-27", ...}, "years": {"the winter year": 2026}}
    (a date the case lacks is None). `may_lack`: named dates some case may lack (C3). `facts`: optional
    readings of ordinary facts ({"the person is a man": formula}); others go to the W6 English grammar.
    `roles`: the role phrases a rule written with "the person" is copied for (default: just "the person").
    Returns {"premises": [quantity statements], "rules": [(sentence, formula)], "case_facts": [...]}.
    """
    item = _Item(env, case, may_lack, facts, roles)
    sentences = [s.strip() for s in re.split(r"(?<=\.)\s+", " ".join(text.split())) if s.strip()]
    rules, case_facts = [], []
    for name in sorted(item.may_lack):
        if item.dates.get(name) is not None:
            if name not in item.day_constants:
                raise DateRuleError(f"DateRule: {name!r} may be absent and has no day constant (C3)")
            case_facts.append(["date_on", ["const", "day", item.day_constants[name]], ["date", item.dates[name]]])
    for sentence in sentences:
        if not sentence.endswith("."):
            raise DateRuleError(f"DateRule: a sentence ends with a full stop: {sentence!r}")
        body = sentence[:-1]
        span = _SPAN.search(body.translate(_SPAN_FOLD))
        if span:
            raise DateRuleError(f"CANNOT (DateRuleSpan): {span[0]!r} in {sentence!r} is a fact over a span of days; "
                                "the written form does not read it and it is not read as a plain fact")
        m = re.fullmatch(r"Let (the .+?) be (.+)", body)
        if m:
            # Lowered once for rules not copied per role (the text as written) and once per role, so a rule
            # copied for the partner reads the partner's dates (Opus H3).
            for scope in [None, *item.roles]:
                item.scope = scope
                name, value = m[1], m[2]
                if scope is not None:
                    name, value = name.replace("the person", scope), value.replace("the person", scope)
                years = item.let_years.setdefault(scope, {})
                if name in item.lets or name in item.years or name in years or name in item.dates or (
                        name in item.may_lack):
                    raise DateRuleError(f"DateRule: {name!r} has one value (a case date or a date the case may lack "
                                        "is never set by a Let sentence)")
                if name in item.day_constants:
                    raise DateRuleError(f"DateRuleLet: {name!r} is a date of the logic (the day constant "
                                        f"{item.day_constants[name]!r}, which a rule may conclude); a Let sentence "
                                        "does not set it (C2)")
                if re.fullmatch(r"[0-9]{4}", value):
                    years[name] = _count(value)
                    continue
                d = item.date(value)
                if d[0] != "ground":
                    raise DateRuleError(f"DateRule: a Let value needs dates every case gives ({sentence!r}; C3)")
                item.lets[name] = d
            item.scope = None
            continue
        m = re.fullmatch(r"If (.+), then (.+)", body)
        if not m:
            raise DateRuleError(f"DateRule: not a Let or If sentence: {sentence!r}")
        copies = [(r, body.replace("the person", r)) for r in item.roles] if "the person" in body else [(None, body)]
        for scope, copy in copies:
            item.scope = scope
            m = re.fullmatch(r"If (.+), then (.+)", copy)
            readings = item.conditions(m[1])
            if len(readings) != 1:
                raise DateRuleError(f"DateRule: the conditions of {sentence!r} have {len(readings)} readings")
            concluded, conclusion = _conclusion(item, m[2])
            rules += [(c, readings[0], conclusion, sentence) for c in concluded] or [
                (None, readings[0], conclusion, sentence)]
        item.scope = None
    check_concluded_overlap([(concluded, condition, sentence) for concluded, condition, _, sentence in rules])
    # A rule that concludes two constants is one rule: one premise, one entry per constant in `concluded`.
    once = list({(repr(c), repr(k), s): (c, k, s) for _, c, k, s in rules}.values())
    formulas = [["implies", condition, conclusion] for condition, conclusion, _ in once] + case_facts
    return {"premises": [{"format": "ve-quantity@1", "formula": f} for f in formulas],
            "rules": [(sentence, ["implies", c, k]) for c, k, sentence in once], "case_facts": case_facts,
            "concluded": [(concluded, condition, sentence) for concluded, condition, _, sentence in rules
                          if concluded is not None]}


def check_concluded_overlap(rules):
    """C2 over (concluded day constant or None, condition, sentence) rules: two rules that conclude one day
    constant must have conditions written exclusive."""
    by_name = {}
    for concluded, condition, sentence in rules:
        if concluded is None:
            continue
        for other_condition, other in by_name.get(concluded, []):
            if not written_exclusive(condition, other_condition):
                raise DateRuleError(f"DateRuleOverlap: {other!r} and {sentence!r} both conclude {concluded!r} and "
                                    "their conditions are not written exclusive (C2)")
        by_name.setdefault(concluded, []).append((condition, sentence))


def lower_date_items(env, texts, case=None, **options):
    """Several items of one case, each lowered by `lower_date_item`, with C2 checked over all their rules
    together (two items that conclude one date are compared too). Returns the per-item results."""
    lowered = [lower_date_item(env, text, case, **options) for text in texts]
    check_concluded_overlap([rule for item in lowered for rule in item["concluded"]])
    return lowered


def _conclusion(item, text):
    """([concluded day constants], formula): C2's key is every day constant the lowered formula mentions
    (Codex H1), whichever path lowered it."""
    formula, errors = None, []
    for m in re.finditer(r" is (?:on )?", text):  # every split, so a name with " is " in it is found
        name, rest = text[:m.start()], text[m.end():]
        if name.startswith("the ") and name in item.day_constants:
            try:
                value = item.date(rest)
            except DateRuleBound:
                raise
            except DateRuleError as exc:  # e.g. "is before ...": the W6 grammar below may read it
                errors.append(exc)
                continue
            if value[0] == "shifted":
                raise DateRuleError(f"DateRule: {text!r} concludes a day after a date the case may lack or a "
                                    "concluded date; a rule concludes a day of dates every case gives (C3)")
            if value[0] == "ground" and value[1][0] == "date" and value[1][1] < "1970":
                raise DateRuleError(f"DateRule: a concluded date lies in 1970..9999 ({text!r})")
            formula = ["date_on", ["const", "day", item.day_constants[name]], item.term(value)]
            break
    if formula is None and text in item.facts:
        formula = item.facts[text]
    elif formula is None:
        try:
            formula = item.fact(text)
        except ResourceLimit:
            raise
        except VEError as exc:  # an input diagnostic only: CheckerUnavailable and any other error propagate
            if errors:
                raise errors[0] from exc
            raise
    concluded, any_day = _day_constants_in(formula)
    protected = {item.day_constants[n]: n for n in (*item.dates, *item.may_lack) if n in item.day_constants}
    for c in concluded:
        if c in protected:
            raise DateRuleError(f"DateRule: {protected[c]!r} is a case date; a rule does not conclude it (C2)")
    if any_day and not concluded:
        raise DateRuleError(f"DateRule: the conclusion {text!r} compares fixed dates only; a rule concludes a date "
                            "of the logic (C2)")
    return concluded, formula
