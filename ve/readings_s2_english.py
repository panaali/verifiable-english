"""The English of S2a (composition-s2.md section 2; composition.md 2.1), registered and gated.

Every wording S2a shows is a template of `TEMPLATES` whose slots are closed classes: the document's sentence
numbers, the readings of its open sets (`<reading>`), the counts, and per result the one `<conclusion>` (the
canonical VE sentence of the conclusion, in italics) or the one `<situation>` (the pulled situation of the model
shown). `derivations` reads a sentence against every registered template, S1's report sentences included, and
enumerates every derivation; `gated` admits a sentence only when it has exactly one derivation and that derivation
is of the template it was built from (W7's all-derivations gate). The `<conclusion>` slot is also read back by the
existing English parser, which admits it only with one derivation, to the conclusion's own formula. No sentence
here can be written by an author as document content: none is a VE statement.

E11 is not registered: the lifting lemma holds (4.4), so it is a non-wording (2.4, G5).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .errors import VEError

QUIET = ("A way of reading a sentence that is not taken adds nothing: its exception, switch, "
         "limitation and bar conditions hold nowhere.")
OVER_BUDGET = "VE did not check every way of reading the open sentences: there are more than 64."
PROVIDED = "This holds provided that:"

# Grammar elements: a literal string; ("slot", name); ("ref", production); ("rep", [elements]); ("any",).
_N, _K, _READING = ("slot", "n"), ("slot", "k"), ("slot", "reading")
_SERIES = [_N, ("rep", [", ", _N]), " and ", _N]

PRODUCTIONS = {
    "citation": [["sentence ", _N], ["sentences ", *_SERIES]],
    "result": [
        ["no two rules on the same act contradict each other."],                                   # R1
        ["the conclusion follows: ", ("slot", "conclusion")],                                       # R2
        ["the conclusion does not follow. It fails here: ", ("slot", "situation"), "."],            # R3
        ["two rules contradict each other here: ", ("slot", "situation"), "."],                     # R4
        ["the sentences of this document can all be true together, as here: ", ("slot", "situation"), "."],  # R5
        ["the sentences of this document cannot all be true together."],                           # R6
    ],
}
RESULTS = {"conflict_free": 0, "follows": 1, "countermodel": 2, "conflict": 3, "premise_model": 4,
           "inconsistent": 5}

TEMPLATES = {
    # S2a (2.2 and composition.md 2.1)
    "E3": [PROVIDED],
    "E4": ["Sentence ", _N, " is read in exactly one of its ", _K, " listed ways."],
    "E6": ["If sentence ", _N, " is read as ", _READING, ", sentence ", _N, " is read as ", _READING, "."],
    "E6b": ["Sentence ", _N, " is not read as ", _READING, " while sentence ", _N, " is read as ", _READING, "."],
    "E7": ["Sentence ", _N, " is not read as ", _READING, ", because of ", ("ref", "citation"), "."],
    "E8": [QUIET],
    "E10": ["Under every reading of the ", _K, " open sentences, ", ("ref", "result")],
    "E12": ["Read sentence ", _N, " as ", _READING, ("rep", [" and sentence ", _N, " as ", _READING]), ": ",
            ("ref", "result")],
    "E13": ["This does not depend on how sentence ", _N, " is read."],
    "E17": ["No compatible way of reading the open sentences reads sentence ", _N, " as ", _READING, "."],
    "E26": ["Under every reading of the open sentence, ", ("ref", "result")],
    "E27": ["Under no reading of the ", _K, " open sentences does the conclusion follow."],
    "E28": [OVER_BUDGET],
    "E29": ["The readings of ", ("ref", "citation"), " were checked one way at a time, not together."],
    # S1's report sentences (composition-s1.md 2.2), registered with their leads, so that no S2a sentence can be
    # read as one of them; their slots are read as any text here, which only widens what counts as ambiguous.
    "E5": ["Sentences ", *_SERIES, " are read with the same ", ("any",)],
    "E14": ["This sentence says ", ("any",)],
    "E16": ["These two readings are about different acts: ", ("any",)],
    "E19": ["These two readings differ here: ", ("any",)],
    "E22": ["Where this sentence applies and a rule that says ", ("any",)],
    "E23": ["Under (1), a rule on the same act that says ", ("any",)],
    "E24": ["These two readings differ in a checked situation that VE cannot yet show in words."],
    "E25": ["It is not certified that these two readings differ only where ", ("any",)],
}
S2A = ("E3", "E4", "E6", "E6b", "E7", "E8", "E10", "E12", "E13", "E17", "E26", "E27", "E28", "E29")


@dataclass
class Slots:
    """The closed classes of one document's slots: display numbers, reading names, and the conclusions and
    situations of the results shown."""
    numbers: set = field(default_factory=set)
    readings: set = field(default_factory=set)
    conclusions: set = field(default_factory=set)
    situations: set = field(default_factory=set)

    def options(self, name):
        if name == "n":
            return self.numbers
        if name == "reading":
            return self.readings
        if name == "conclusion":
            return self.conclusions
        if name == "situation":
            return self.situations
        raise VEError(f"InvalidInput: unknown S2 slot {name}")


_NUMERAL = re.compile(r"[1-9][0-9]*")


def _match(elements, text, pos, slots, binds):
    """Every (end position, bindings) at which `elements` derives `text[pos:end]`."""
    if not elements:
        yield pos, binds
        return
    head, rest = elements[0], elements[1:]
    if type(head) is str:
        if text.startswith(head, pos):
            yield from _match(rest, text, pos + len(head), slots, binds)
        return
    kind = head[0]
    if kind == "slot":
        if head[1] == "k":
            numeral = _NUMERAL.match(text, pos)
            if numeral:
                yield from _match(rest, text, numeral.end(), slots, binds + ((head[1], numeral.group()),))
            return
        for option in slots.options(head[1]):
            if option and text.startswith(option, pos):
                yield from _match(rest, text, pos + len(option), slots, binds + ((head[1], option),))
        return
    if kind == "ref":
        for k, alternative in enumerate(PRODUCTIONS[head[1]]):
            for end, inner in _match(alternative, text, pos, slots, binds + ((head[1], k),)):
                yield from _match(rest, text, end, slots, inner)
        return
    if kind == "rep":
        yield from _match(rest, text, pos, slots, binds)
        for end, inner in _match(head[1], text, pos, slots, binds):
            if end > pos:
                yield from _match([head, *rest], text, end, slots, inner)
        return
    if kind == "any":
        for end in range(len(text), pos, -1):
            yield from _match(rest, text, end, slots, binds)
        return
    raise VEError("InvalidInput: invalid S2 grammar element")


def derivations(text, slots):
    """Every derivation of `text` from a registered template: (template, bindings)."""
    return [(name, binds) for name, elements in TEMPLATES.items()
            for end, binds in _match(elements, text, 0, slots, ()) if end == len(text)]


def gated(intended, text, slots):
    """W7's all-derivations gate: `text` has exactly one derivation, from `intended`; and no generated name, no
    reserved prefix and no `may not` (2.4, G6, G9)."""
    if type(text) is not str or any(x in text for x in ("ve__", "rd-", "soft__", "rights__", "may not")):
        raise VEError(f"InvalidInput: S2 wording {intended} shows a generated name or `may not`")
    found = derivations(text, slots)
    if len(found) != 1 or found[0][0] != intended:
        raise VEError(f"InvalidInput: S2 wording {intended} has {len(found)} derivations: {text}")
    return text


# ---------------------------------------------------------------------------------------------------------------
# The sentences, each built from its template and gated before it is returned


def _series(parts):
    parts = list(parts)
    if not parts:
        raise VEError("InvalidInput: S2 wording needs a sentence")
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def citation(numbers):
    numbers = [str(n) for n in numbers]
    return f"sentence {numbers[0]}" if len(numbers) == 1 else f"sentences {_series(numbers)}"


def result_sentence(kind, *, conclusion=None, situation=None):
    """R1 to R6 (2.1), un-gated: a result sentence is shown only inside E10, E12 or E26."""
    if kind == "conflict_free":
        return "no two rules on the same act contradict each other."
    if kind == "follows":
        return f"the conclusion follows: {conclusion}"
    if kind == "countermodel":
        return f"the conclusion does not follow. It fails here: {situation}."
    if kind == "conflict":
        return f"two rules contradict each other here: {situation}."
    if kind == "premise_model":
        return f"the sentences of this document can all be true together, as here: {situation}."
    if kind == "inconsistent":
        return "the sentences of this document cannot all be true together."
    raise VEError("InvalidInput: unknown S2 result sentence")


def every_result(open_count, kind, slots, *, conclusion=None):
    """E26 for one open sentence, E10 for more (2.3 items 1 and 7): certificate-based results only."""
    if kind not in ("conflict_free", "follows", "inconsistent"):
        raise VEError("InvalidInput: every-reading wording needs certificates")
    result = result_sentence(kind, conclusion=conclusion)
    if open_count == 1:
        return gated("E26", f"Under every reading of the open sentence, {result}", slots)
    return gated("E10", f"Under every reading of the {open_count} open sentences, {result}", slots)


def named_result(readings, kind, slots, *, conclusion=None, situation=None):
    """E12: `readings` is [(sentence number, reading name)], in source order. A model's result names the complete
    choice it encodes (2.3 item 3); a certificate's exactly the assumed candidates (item 2)."""
    readings = list(readings)
    if not readings:
        raise VEError("InvalidInput: E12 needs a named reading")
    subjects = " and ".join(f"sentence {number} as {name}" for number, name in readings)
    result = result_sentence(kind, conclusion=conclusion, situation=situation)
    return gated("E12", f"Read {subjects}: {result}", slots)


def one_reading(number, count, slots):
    return gated("E4", f"Sentence {number} is read in exactly one of its {count} listed ways.", slots)


def quiet(slots):
    return gated("E8", QUIET, slots)


def provided(slots):
    return gated("E3", PROVIDED, slots)


def narrowed(number, reading, cited, slots):
    return gated("E7", f"Sentence {number} is not read as {reading}, because of {citation(cited)}.", slots)


def independent(number, slots):
    return gated("E13", f"This does not depend on how sentence {number} is read.", slots)


def dead_reading(number, reading, slots):
    return gated("E17", f"No compatible way of reading the open sentences reads sentence {number} as {reading}.",
                 slots)


def none_result(open_count, slots):
    if open_count < 2:
        raise VEError("InvalidInput: E27 needs at least two open sentences")
    return gated("E27", f"Under no reading of the {open_count} open sentences does the conclusion follow.", slots)


def over_budget(slots):
    return gated("E28", OVER_BUDGET, slots)


def not_superposed(numbers, slots):
    return gated("E29", f"The readings of {citation(numbers)} were checked one way at a time, not together.",
                 slots)


def requires(first, second, slots):
    """E6 (`requires`): registered and gated; no S2a document has a constraint (0)."""
    (n, a), (m, b) = first, second
    return gated("E6", f"If sentence {n} is read as {a}, sentence {m} is read as {b}.", slots)


def excludes(first, second, slots):
    (n, a), (m, b) = first, second
    return gated("E6b", f"Sentence {n} is not read as {a} while sentence {m} is read as {b}.", slots)


__all__ = ["OVER_BUDGET", "PROVIDED", "QUIET", "S2A", "Slots", "TEMPLATES", "citation", "dead_reading",
           "derivations", "every_result", "excludes", "gated", "independent", "named_result", "narrowed",
           "none_result", "not_superposed", "one_reading", "over_budget", "provided", "quiet", "requires",
           "result_sentence"]
