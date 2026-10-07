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

Readings under unspecified defaults (docs/spec/readings-defaults.md 2.1 and 2.2) add E30, E31, E32 and the result R7,
and reuse norm-defaults' filled-gap sentence after a shown situation (one per filled gap the result depends on, read
here as part of the result, so the gate reads the whole line) and its pair sentence as an E3 line. Their `<clause>`
slot is a closed class: the point clauses of the situations shown (`ve/norm_defaults_english.py` `point_clause`).
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
# After a shown situation: one sentence per filled gap the result depends on (readings-defaults 2.2; norm-defaults 3.2).
_GAPS = ("rep", [" Here the text does not say whether ", ("slot", "clause"), "; this situation answers '",
                 ("slot", "answer"), "'."])
CHECKED_ALONE = ("was checked by itself, with the terms its readings declare; VE did not check it together with "
                 "the other sentences.")
EACH_ALONE = "Each open sentence below was checked by itself, under each of its readings."

PRODUCTIONS = {
    "citation": [["sentence ", _N], ["sentences ", *_SERIES]],
    "result": [
        ["no two rules on the same act contradict each other."],                                   # R1
        ["the conclusion follows: ", ("slot", "conclusion")],                                       # R2
        ["the conclusion does not follow. It fails here: ", ("slot", "situation"), ".", _GAPS],     # R3
        ["two rules contradict each other here: ", ("slot", "situation"), ".", _GAPS],              # R4
        ["the sentences of this document can all be true together, as here: ", ("slot", "situation"), ".",
         _GAPS],                                                                                    # R5
        ["the sentences of this document cannot all be true together."],                           # R6
        ["the text does not say whether ", ("slot", "clause"), ": no rule decides this situation."],  # R7
    ],
}
RESULTS = {"conflict_free": 0, "follows": 1, "countermodel": 2, "conflict": 3, "premise_model": 4,
           "inconsistent": 5, "undecided": 6}
SITUATION_RESULTS = ("countermodel", "conflict", "premise_model")

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
    # Readings under unspecified defaults (readings-defaults 2.1): a sentence checked by itself (a component)
    "E30": ["Under every reading of sentence ", _N, ", ", ("ref", "result")],
    "E31": ["Sentence ", _N, " ", CHECKED_ALONE],
    "E32": [EACH_ALONE],
    # norm-defaults 4.1's pair sentence as an E3 line (readings-defaults 2.2), registered with its lead; its body is
    # norm-defaults' own and is read as any text here, which only widens what counts as ambiguous.
    "P1": ["Whenever ", ("any",)],
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
DEFAULTS = ("E30", "E31", "E32", "P1")


@dataclass
class Slots:
    """The closed classes of one document's slots: display numbers, reading names, and the conclusions and
    situations of the results shown."""
    numbers: set = field(default_factory=set)
    readings: set = field(default_factory=set)
    conclusions: set = field(default_factory=set)
    situations: set = field(default_factory=set)
    clauses: set = field(default_factory=set)
    # The completion's reserved name prefixes, hidden like generated names (readings-defaults 2.5) only where the
    # document's environment reserves them (`environment.reserved_prefixes`). Without an environment, every one.
    reserved: tuple = field(default_factory=lambda: _all_reserved())

    def options(self, name):
        if name == "n":
            return self.numbers
        if name == "reading":
            return self.readings
        if name == "conclusion":
            return self.conclusions
        if name == "situation":
            return self.situations
        if name == "clause":
            return self.clauses
        if name == "answer":
            return ANSWERS
        raise VEError(f"InvalidInput: unknown S2 slot {name}")


_NUMERAL = re.compile(r"[1-9][0-9]*")
ANSWERS = frozenset({"yes", "no"})
# Names no wording shows (2.4, G6; readings-defaults 2.5): generated vocabulary, qualified rule names and `may not`;
# and, under `norm-defaults@0` only, the completion's reserved names (`Slots.reserved`).
_HIDDEN = ("ve__", "rd-", "soft__", "rights__", "may not")  # relay-lint: non-wording


def _all_reserved():
    from .environment import RESERVED_PREFIXES
    return RESERVED_PREFIXES


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
    reserved prefix of the document's environment and no `may not` (2.4, G6, G9)."""
    if type(text) is not str or any(x in text for x in (*_HIDDEN, *slots.reserved)):
        raise VEError(f"InvalidInput: S2 wording {intended} shows a generated name or `may not`")
    found = derivations(text, slots)
    if len(found) != 1 or found[0][0] != intended:
        raise VEError(f"InvalidInput: S2 wording {intended} has {len(found)} derivations: {text}")
    return text


def s1_gated(lead, text):
    """S1's report sentences read against every registered wording, S2a's included (2.2 and composition.md 2): the
    sentence has exactly one derivation, by its own lead (E19 to E21 share one lead), so no sentence of S1 can be
    read as one of S2a's. Their own slots are S1's (composition-s1.md 2.1) and are read as any text here."""
    found = derivations(text, Slots())
    if len(found) != 1 or found[0][0] != lead:
        raise VEError(f"InvalidInput: S1 wording {lead} has {len(found)} derivations: {text}")
    return text


# ---------------------------------------------------------------------------------------------------------------
# The `<reading>` slot (readings-defaults 2.3, review A4) and canonical sentences


@dataclass(frozen=True)
class Unnamed:
    """A reading the `<reading>` slot cannot show, with the refusal an answer that names it gets. Only such an
    answer is refused: the other answers of the document are shown as before."""
    reason: str


def sentence_slots(set_id, sentences, verbs=None, keys=None):
    """The `<reading>` names of one set (readings-defaults 2.3; review A4 and its B), one per candidate, distinct
    for distinct contents. `sentences[i]` is candidate i's full rendered sentence (a rule's notes included) or an
    `Unnamed`; `verbs[i]` a rule candidate's deontic verb, else None; `keys[i]` the candidate's content identity
    (default: every candidate different).

    The italic verb when every candidate has a verb and the full sentences differ only in it (the first occurrence
    of each verb replaced, they are one frame); otherwise each sentence, in italics, without its final period. A
    sentence that would show two different contents names neither of them; candidates with the same content share
    their sentence."""
    count = len(sentences)
    verbs = [None] * count if verbs is None else list(verbs)
    keys = list(range(count)) if keys is None else list(keys)
    if count and all(type(text) is str and verb is not None and f" {verb} " in text
                     for text, verb in zip(sentences, verbs)):
        frames = {text.replace(f" {verb} ", " _ ", 1) for text, verb in zip(sentences, verbs)}
        if len(frames) == 1 and len(set(verbs)) == count:
            return [f"*{verb}*" for verb in verbs]
    names = [text if type(text) is not str else f"*{text[:-1] if text.endswith('.') else text}*"
             for text in sentences]
    contents = {}
    for name, key in zip(names, keys):
        if type(name) is str:
            contents.setdefault(name, set()).add(key)
    return [Unnamed(f"two different readings of {set_id} are shown by the same sentence")
            if type(name) is str and len(contents[name]) > 1 else name for name in names]


def shown(name):
    """A `<reading>` name as an answer shows it: an `Unnamed` reading is refused here, where an answer names it."""
    if type(name) is not str:
        raise VEError(f"InvalidInput: {name.reason}")
    return name


def named_pair(set_id, names, i, j):
    """`names` when readings `i` and `j` can both be shown; a pair never names a reading the slot cannot show."""
    shown(names[i]), shown(names[j])
    return names


def canonical_sentence(frame, formula, failure):
    """A formula's canonical sentence on the existing English surface, admitted only when that surface's
    all-derivations parser reads it back to the formula itself; else `InvalidInput: <failure>`, also when the
    surface has no writable form for it (the renderer's ValueError) or its parser refuses it. A resource limit is
    not a failure to read back and is raised as it is."""
    from .ast import Document as Formulas
    from .english import parse_english
    from .errors import ResourceLimit
    from .printer import render
    try:
        text = render(Formulas((formula,)), frame, "ve_english").strip()
        read = parse_english(frame, text).formulas
    except ResourceLimit:
        raise
    except ValueError:  # VEError is a ValueError
        raise VEError(f"InvalidInput: {failure}") from None
    if read != (formula,):
        raise VEError(f"InvalidInput: {failure}")
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


def gap_sentences(gaps):
    """norm-defaults 3.2's filled-gap sentences, one per `(clause, value)`, in the order given: the gaps the result
    depends on (readings-defaults 2.2; Lean's plan lists them). Each follows the shown situation."""
    out = []
    for clause, value in gaps:
        if type(clause) is not str or not clause or type(value) is not bool:
            raise VEError("InvalidInput: a filled gap needs its clause and a yes or no answer")
        out.append(f" Here the text does not say whether {clause}; this situation answers '{'yes' if value else 'no'}'.")
    return "".join(out)


def result_sentence(kind, *, conclusion=None, situation=None, clause=None, gaps=()):
    """R1 to R7 (2.1; readings-defaults 2.1), un-gated: a result sentence is shown only inside E10, E12, E26 or
    E30. A shown situation (R3 to R5) is followed by its filled-gap sentences; no other result has any."""
    gaps = tuple(gaps)
    if gaps and kind not in SITUATION_RESULTS:
        raise VEError("InvalidInput: only a shown situation is followed by filled gaps")
    if kind == "conflict_free":
        return "no two rules on the same act contradict each other."
    if kind == "follows":
        return f"the conclusion follows: {conclusion}"
    if kind == "countermodel":
        return f"the conclusion does not follow. It fails here: {situation}.{gap_sentences(gaps)}"
    if kind == "conflict":
        return f"two rules contradict each other here: {situation}.{gap_sentences(gaps)}"
    if kind == "premise_model":
        return f"the sentences of this document can all be true together, as here: {situation}.{gap_sentences(gaps)}"
    if kind == "inconsistent":
        return "the sentences of this document cannot all be true together."
    if kind == "undecided":
        return f"the text does not say whether {clause}: no rule decides this situation."
    raise VEError("InvalidInput: unknown S2 result sentence")


def every_result(open_count, kind, slots, *, conclusion=None):
    """E26 for one open sentence, E10 for more (2.3 items 1 and 7): certificate-based results only."""
    if kind not in ("conflict_free", "follows", "inconsistent"):
        raise VEError("InvalidInput: every-reading wording needs certificates")
    result = result_sentence(kind, conclusion=conclusion)
    if open_count == 1:
        return gated("E26", f"Under every reading of the open sentence, {result}", slots)
    return gated("E10", f"Under every reading of the {open_count} open sentences, {result}", slots)


def every_result_of_sentence(number, kind, slots, *, conclusion=None):
    """E30 (readings-defaults 2.1): E26 for a sentence checked by itself (a companion component), certificate-based
    results only, as E26."""
    if kind not in ("conflict_free", "follows", "inconsistent"):
        raise VEError("InvalidInput: every-reading wording needs certificates")
    result = result_sentence(kind, conclusion=conclusion)
    return gated("E30", f"Under every reading of sentence {number}, {result}", slots)


def checked_alone(number, slots):
    """E31: sentence `number` is a component, checked with its readings' merged terms and no other sentence."""
    return gated("E31", f"Sentence {number} {CHECKED_ALONE}", slots)


def each_alone(slots):
    """E32: the lines after it are per-component answers, claiming their product and nothing more."""
    return gated("E32", EACH_ALONE, slots)


def pair_line(text, slots):
    """norm-defaults 4.1's pair sentence as the E3 line of a used `unsaid:pair:<r>,<m>` label (readings-defaults
    2.2): read against every registered wording, it has exactly one derivation, by its own lead."""
    return gated("P1", text, slots)


def named_result(readings, kind, slots, *, conclusion=None, situation=None, clause=None, gaps=()):
    """E12: `readings` is [(sentence number, reading name)], in source order. A model's result names the complete
    choice it encodes (2.3 item 3); a certificate's exactly the assumed candidates (item 2). `gaps` are the filled
    gaps a shown situation's result depends on, `clause` R7's undecided point (readings-defaults 2.1, 2.2)."""
    readings = list(readings)
    if not readings:
        raise VEError("InvalidInput: E12 needs a named reading")
    subjects = " and ".join(f"sentence {number} as {name}" for number, name in readings)
    result = result_sentence(kind, conclusion=conclusion, situation=situation, clause=clause, gaps=gaps)
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


__all__ = ["ANSWERS", "CHECKED_ALONE", "canonical_sentence", "named_pair", "sentence_slots", "shown", "Unnamed",
           "DEFAULTS", "EACH_ALONE", "OVER_BUDGET", "PROVIDED", "QUIET", "S2A", "Slots",
           "TEMPLATES", "checked_alone", "citation", "dead_reading", "derivations", "each_alone", "every_result",
           "every_result_of_sentence", "excludes", "gap_sentences", "gated", "independent", "named_result",
           "narrowed", "none_result", "not_superposed", "one_reading", "over_budget", "pair_line", "provided",
           "quiet", "requires", "result_sentence", "s1_gated"]
