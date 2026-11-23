"""Date arithmetic for written legal items (date-arith; manage-agents reviews/spare/date-arith/PROPOSAL.md).

The written form (PROPOSAL sections 2.1-2.4) is lowered here to `ve-quantity@1` formulas whose date
expressions Lean works out while decoding (`VE.Time.Wire.elabCal`): a day term `["cal", E]` and a
formula `["cal_cmp", op, E1, E2]`, with `E` one of `["date", "YYYY-MM-DD"]` (1900..9999),
`["plus_months", E, k, reading]`, `["plus_days", E, k]` (k >= 0), `["month_first", E]`,
`["month_last", E]` and `["nth_weekday", n, w, month, year]` (w: 0 = Monday).

This lowering is the shell's: it substitutes the case's dates and the `Let` values, expands the age,
period and week wordings into those nodes, and copies a rule per role. It is tested, not Lean-checked.
Lean computes the arithmetic on the dates supplied here and binds them into the statement's meaning
id (`calInputs`), so a wrong case date is visible in the report, not caught.

Two rules from the design challenge (CHALLENGE.md C2, C3) are enforced here:

* C2: two `If` rules that conclude the same date name are refused unless their conditions are
  written exclusive (one rule's condition has, as a top-level `and` part, the negation of a part of
  the other's), since two different concluded values make the premises inconsistent.
* C3: a named date the case may lack (`may_lack`) lowers to an ordinary day constant compared with
  today's nodes (`date_on`, `date_before`, `date_after`, `date_no_later`, `within_days`), never to a
  ground expression; it cannot be offset by months or years or used in a `Let`. A case that gives
  it adds the fact `date_on(constant, date)`; a case that lacks it adds nothing.

A 29 February birth date offset by whole years has no day in a common year; with no reading the
age is refused (Lean's `MissingDay`), never guessed (CHALLENGE.md C11).
"""
from __future__ import annotations

import re

from ..errors import ResourceLimit, SyntaxError

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
ORDINALS = ("first", "second", "third", "fourth")
MAX_READINGS = 10_000
_OPS = ((" is on or before ", "on_or_before"), (" is on or after ", "on_or_after"), (" is before ", "before"),
        (" is after ", "after"), (" is on ", "on"))
# The existing date node and argument order for each comparison over day terms.
_DAY_NODES = {"before": ("date_before", False), "after": ("date_after", False), "on": ("date_on", False),
              "on_or_before": ("date_no_later", False), "on_or_after": ("date_no_later", True)}


class DateRuleError(SyntaxError):
    """A written date item the lowering refuses (the message names the rule)."""


def _ordinal(text):
    m = re.fullmatch(r"([1-9][0-9]*)(?:st|nd|rd|th)", text)
    return int(m[1]) if m else None


class _Item:
    """One item's lowering state: the case, the `Let` values, the constants and the facts."""

    def __init__(self, env, case, may_lack, facts, roles):
        self.env, self.facts, self.roles = env, dict(facts or {}), list(roles or ["the person"])
        self.dates = dict((case or {}).get("dates", {}))
        self.years = dict((case or {}).get("years", {}))
        self.may_lack = set(may_lack or ())
        self.lets, self.work = {}, 0
        self.day_constants = {decl.verbalisation: name for name, decl in env.constants.items()
                              if decl.verbalisation and decl.sort == "$int" and decl.unit == "day"}

    def tick(self):
        self.work += 1
        if self.work > MAX_READINGS:
            raise ResourceLimit(f"date lowering budget MAX_READINGS={MAX_READINGS} exhausted")

    # --- dates (PROPOSAL 2.1): ("ground", E) or ("const", constant name) ---------------------------------

    def date(self, text):
        text = text.strip()
        self.tick()
        m = re.fullmatch(r"(.+?) (plus|minus) (.+?)(?:,? \(?reading: (last|next) day\)?)?", text)
        if m and self._offset(m[3]) is not None:
            months, days = self._offset(m[3])
            base = self.date(m[1])
            sign = -1 if m[2] == "minus" else 1
            if base[0] == "const":
                raise DateRuleError(f"DateRule: a date the case may lack ({text!r}) is offset only in a period "
                                    "wording (C3)")
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
        m = re.fullmatch(r"([1-9]|[12][0-9]|3[01]) ([A-Z][a-z]+) ([0-9]{4})", text)
        if m and m[2] in MONTHS:
            return ("ground", ["date", f"{m[3]}-{MONTHS.index(m[2]) + 1:02d}-{int(m[1]):02d}"])
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
            year = int(m[4]) if re.fullmatch(r"[0-9]{4}", m[4]) else self.year(m[4])
            return ("ground", ["nth_weekday", ORDINALS.index(m[1]) + 1, WEEKDAYS.index(m[2]),
                               MONTHS.index(m[3]) + 1, year])
        m = re.fullmatch(r"the last day of the period of ([1-9][0-9]*) days beginning with (.+)", text)
        if m:
            return ("ground", ["plus_days", self.ground(m[2], text), str(int(m[1]) - 1)])
        m = re.fullmatch(r"the (\S+) day of the period beginning with (.+)", text)
        if m and _ordinal(m[1]):
            return ("ground", ["plus_days", self.ground(m[2], text), str(_ordinal(m[1]) - 1)])
        m = re.fullmatch(r"the last day of the week beginning (.+)", text)
        if m:
            return ("ground", ["plus_days", self.ground(m[1], text), "6"])
        m = re.fullmatch(r"the day (.+) attains the age of ([0-9]+) years?(?: and ([0-9]+) months?)?"
                         r"(?:,? \(?reading: (last|next) day\)?)?", text)
        if m:
            months = 12 * int(m[2]) + int(m[3] or 0)
            return ("ground", ["plus_months", self.birth(m[1]), str(months), m[4] or "none"])
        return self.named(text)

    def _offset(self, text):
        """`N years and M months and ...`: (months, days), or None."""
        months = days = 0
        for part in text.split(" and "):
            m = re.fullmatch(r"([0-9]+) (year|month|week|day)s?", part.strip())
            if not m:
                return None
            n = int(m[1])
            months += {"year": 12 * n, "month": n}.get(m[2], 0)
            days += {"week": 7 * n, "day": n}.get(m[2], 0)
        return months, days

    def ground(self, text, whole):
        kind, e = self.date(text)
        if kind != "ground":
            raise DateRuleError(f"DateRule: {whole!r} needs a date every case gives; {text!r} may be absent (C3)")
        return e

    def birth(self, role):
        return self.ground(f"the birth date of {role}", f"the birth date of {role}")

    def year(self, name):
        if name not in self.years:
            raise DateRuleError(f"DateRule: the year {name!r} is not fixed by the case or a Let sentence")
        return int(self.years[name])

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
        return ["cal", d[1]] if d[0] == "ground" else ["const", "day", d[1]]

    # --- comparisons and ages (2.2, 2.3) ------------------------------------------------------------------

    def compare(self, op, a, b):
        if a[0] == "ground" and b[0] == "ground":
            return ["cal_cmp", op, a[1], b[1]]
        node, swap = _DAY_NODES[op]
        x, y = self.term(a), self.term(b)
        return [node, y, x] if swap else [node, x, y]

    def condition(self, text):
        """Readings of one condition without connectives."""
        out = []
        m = re.fullmatch(r"(.+?) (?:has attained the age of|is aged at least) ([0-9]+)(?: years?)?"
                         r"(?: and ([0-9]+) months?)? on (.+)", text)
        if m:
            out.append(self.age(m[1], int(m[2]), int(m[3] or 0), m[4]))
        m = re.fullmatch(r"(.+?) has reached (?:his|her|their|its) (\S+) birthday on (.+)", text)
        if m and _ordinal(m[2]):
            out.append(self.age(m[1], _ordinal(m[2]), 0, m[3]))
        m = re.fullmatch(r"(.+?) is under the age of ([0-9]+)(?: years?)? on (.+)", text)
        if m:
            out.append(["not", self.age(m[1], int(m[2]), 0, m[3])])
        m = re.fullmatch(r"(.+?) is in the period of ([1-9][0-9]*) days beginning with (.+)", text)
        if m:
            out.append(self.window(m[1], m[3], int(m[2]) - 1))
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
            except Exception as exc:  # no date reading and no fact reading: the date rule's refusal says why
                raise errors[0] if errors else DateRuleError(f"DateRule: no reading of the condition {text!r} "
                                                             f"({exc})") from exc
        return out

    def age(self, role, years, months, on):
        return self.compare("on_or_before", ("ground", ["plus_months", self.birth(role), str(12 * years + months),
                                                         "none"]), self.date(on))

    def window(self, day, start, extra):
        """`day` lies in `start` to `start` plus `extra` days."""
        d, s = self.date(day), self.date(start)
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
                except DateRuleError:
                    continue
                readings += [[node, a, b] for a in left for b in right]
            if readings:
                break  # `or` binds looser than `and`: an `or` reading is the whole sentence's
        if not readings and text.startswith("not "):
            try:
                readings += [["not", a] for a in self.conditions(text[4:])]
            except DateRuleError:
                pass
        if not readings:
            readings += self.condition(text)
        distinct = {repr(r): r for r in readings}
        if not distinct:
            raise DateRuleError(f"DateRule: no reading of the condition {text!r}")
        return list(distinct.values())


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
        m = re.fullmatch(r"Let (the .+?) be (.+)", body)
        if m:
            name, value = m[1], m[2]
            if name in item.lets or name in item.years or name in item.dates:
                raise DateRuleError(f"DateRule: {name!r} has one value")
            if re.fullmatch(r"[0-9]{4}", value):
                item.years[name] = int(value)
                continue
            d = item.date(value)
            if d[0] != "ground":
                raise DateRuleError(f"DateRule: a Let value needs dates every case gives ({sentence!r}; C3)")
            item.lets[name] = d
            continue
        m = re.fullmatch(r"If (.+), then (.+)", body)
        if not m:
            raise DateRuleError(f"DateRule: not a Let or If sentence: {sentence!r}")
        copies = [(r, body.replace("the person", r)) for r in item.roles] if "the person" in body else [(None, body)]
        for _, copy in copies:
            m = re.fullmatch(r"If (.+), then (.+)", copy)
            readings = item.conditions(m[1])
            if len(readings) != 1:
                raise DateRuleError(f"DateRule: the conditions of {sentence!r} have {len(readings)} readings")
            concluded, conclusion = _conclusion(item, m[2])
            rules.append((concluded, readings[0], conclusion, sentence))
    by_name = {}
    for concluded, condition, _, sentence in rules:
        if concluded is None:
            continue
        for other_condition, other in by_name.get(concluded, []):
            if not written_exclusive(condition, other_condition):
                raise DateRuleError(f"DateRuleOverlap: {other!r} and {sentence!r} both conclude {concluded!r} and "
                                    "their conditions are not written exclusive (C2)")
        by_name.setdefault(concluded, []).append((condition, sentence))
    formulas = [["implies", condition, conclusion] for _, condition, conclusion, _ in rules] + case_facts
    return {"premises": [{"format": "ve-quantity@1", "formula": f} for f in formulas],
            "rules": [(sentence, ["implies", c, k]) for _, c, k, sentence in rules], "case_facts": case_facts}


def _conclusion(item, text):
    """(concluded date name or None, formula)."""
    m = re.fullmatch(r"(the .+?) is (.+)", text)
    if m and m[1] in item.day_constants and m[1] not in item.dates and m[1] not in item.may_lack:
        value = item.date(m[2])
        if value[0] == "ground" and value[1][0] == "date" and value[1][1] < "1970":
            raise DateRuleError(f"DateRule: a concluded date lies in 1970..9999 ({text!r})")
        return m[1], ["date_on", ["const", "day", item.day_constants[m[1]]], item.term(value)]
    if text in item.facts:
        return None, item.facts[text]
    return None, item.fact(text)
