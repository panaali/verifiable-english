"""Q1.4b's check of its saved A/B (plan Q1.4; DRI 2026-10-27 item 4, DRI 2026-10-28 items 1-5, DRI note 2026-10-28c).

The corpus starts with Q1.4's (`../../q1-4/evidence/speech_ab.py write`): base.json.gz is it recorded at the merge
base (`VE_AB_ROOT`), head.json.gz at this item's head, each grown by `augment SOURCE OUT [JOBS]` with the cases of
`extra_cases` not yet recorded; `delta BASE HEAD OUT` writes delta.json (`summary`: the counts and the `verdict` and
`lint` rows) and `delta-md DELTA FIRST` DELTA.md's class (d) rows. A `verdict` row must be in exactly one signed class.
2026-10-27 item 4: (a) `gloss`, a declared gloss the base read as its one predicate and Lean's lexicon refuses; (b)
`folded`, a name the base matched after folding its case and Lean refuses; (c) `quantified`, the six `Is every/some
service reviewed?` in Q1.4's environments, which the base refused as `UnknownAlternative` and Lean reads with a
quantifier. 2026-10-28: item 1 `negative`, a declared negative verbalisation; item 2 `bare_name` and `quoted_name`,
a name with a digit or underscore; item 3 `determiner`, a grammar determiner outside (c); items 4 and 5
`unverbalised`, a predicate declared without a verbalisation; item 5 `opening`, any other verdict change of an `Is `
question this item added. The added questions are `opening_cases`: every word each environment declares in every
place of every grammar rule's sentence, every pair in every two places, case, spacing and nesting variants, in every
environment the evidence asks in. A `class` or `wording` row must keep R1's (a) and (b) or be R2's rule O1, as in
Q1.4. `check` (and `audit`, the same check) recomputes every row from the two recordings and exits 1 on a `lint`
row, a verdict outside its class, a class whose count is not the recorded one (so an empty delta or a head-against-
head comparison fails too), a delta.json that is not the recordings' summary, or a question `coverage` finds unasked.
"""
from __future__ import annotations

import functools
import gzip
import itertools
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "q1-4" / "evidence"))

import speech_ab  # noqa: E402

NEGATIVE_SUBJECTS = ("atlas", "beacon")
SPECIAL_NAMES = ("atlas2", "atlas_two", "beacon2", "beacon_two")
GRAMMAR = Path(__file__).resolve().parents[4] / "ve/english_grammar/relational-fol@0.json"
UNVERBALISED = "checked"
EXTRA_ENVS = ("negative", "names", "unverbalised")


def determiners() -> tuple[str, ...]:
    """The words the grammar puts before a noun phrase: the first terminal of every rule whose next symbol is a
    declaration or a natural subject (`every`, `some`, `no`). Read from the grammar source, so a determiner the
    grammar gains is a corpus case before anyone lists it."""
    rules = json.loads(GRAMMAR.read_text())
    return tuple(sorted({r["rhs"][0] for r in rules if len(r["rhs"]) > 1 and type(r["rhs"][0]) is str
                         and r["rhs"][1] in ({"n": "declaration"}, {"n": "natural_subject"})}))


def reader_cases() -> list[tuple[str, str, str]]:
    """(env, wording, predicate word) over the reader's dimensions: subject (a name, or each grammar determiner over
    a sort) x predicate declaration (with a verbalisation in `speech`; without one in `unverbalised`, as declared
    and capitalised) x polarity."""
    forms = {"speech": ("reviewed",), "unverbalised": (UNVERBALISED, UNVERBALISED.capitalize())}
    subjects = {"speech": (), "unverbalised": ("atlas",)}
    return [(env, f"Is {subject} {polarity}{word}?", word)
            for env, words in forms.items() for word in words
            for subject in (*subjects[env], *(f"{det} service" for det in determiners()))
            for polarity in ("", "not ")]


def _spellings(raw: dict, word: str) -> list[list[str]]:
    """The predicate's spellings after its subject, both polarities: its verbalisation (Lean's default words `is
    <word>` when it has none) and its declared negative verbalisation (`is not <word>` when it has none), so the
    corpus asks every opening with each form the environment gives it (recheck 1 F6)."""
    declared = raw["vocabulary"]["predicates"][word]
    forms = (declared.get("verbalisation") or f"{{0}} is {word}",
             declared.get("negative_verbalisation") or f"{{0}} is not {word}")
    return [form.removeprefix("{0} ").split() for form in forms]


# The word categories each slot is spelled from (`vocabulary`); the grammar's other vocabulary categories are spelled
# from them as `ve/english.py` builds them (an atom is a name and a predicate form, `natural_subject` an adjective and a
# noun, ...); `relation` and `object_relative` need a two-place verbalisation, which no added environment declares
# (`coverage` fails if one does).
WORD_CATEGORIES = ("constant", "noun", "label", "adjective", "relative")
COMPOSITE = {"atom": ("constant", "relative"), "copula_relative": ("is", "adjective"),
             "copula_adjective": ("adjective",), "natural_subject": ("adjective", "noun"),
             "owner_clause": ("has", "an", "owner")}
UNFILLED = ("relation", "object_relative")
HOLE = object()  # where a nonterminal goes in a sentence being built
NEST = "nest "  # the tag prefix of a sentence nested in another rule's formula place (`nest_tag`)


def vocabulary(raw: dict) -> dict[str, list[tuple[str, ...]]]:
    """Every word the environment `raw` declares, by word category, as the alternatives a slot of that category is
    spelled with (DRI note 2026-10-28c (a)): `constant` every declared constant, bare and quoted (the spellings the
    reader accepts); `noun` every sort's singular and plural (the sort's name when it declares none, which Lean
    reads); `label` every sort's variable letter numbered 1; `adjective` every one-place predicate whose form is
    `is <word>` (`ve/natural.py`'s adjective); `relative` each one-place predicate's two forms (`_spellings`). Built from
    the whole declaration, never from a chosen word; the first alternative of each is of the first one-place
    predicate's sort, so each rule's first sentence is well sorted."""
    from ve.environment import Environment
    from ve.printer import _fluent_variable_letters

    v = raw["vocabulary"]
    unary = [name for name, p in v["predicates"].items() if len(p["arguments"]) == 1]
    first = v["predicates"][unary[0]]["arguments"][0] if unary else None
    sorts = sorted(v["sorts"], key=lambda s: s != first)
    nouns = {s: [v["sorts"][s]["verbalisation"][n] for n in ("singular", "plural")] if "verbalisation" in v["sorts"][s]
             else [s] for s in sorts}
    letters = _fluent_variable_letters({s: nouns[s][0] for s in sorts}, Environment(raw))
    forms = {name: _spellings(raw, name) for name in unary}
    return {"constant": [(spelling,) for c in sorted(v["constants"], key=lambda c: v["constants"][c]["sort"] != first)
                         for spelling in (c, f'"{c}"')],
            "noun": [(noun,) for s in sorts for noun in nouns[s]],
            "label": [(letters[s] + "1",) for s in sorts],
            "adjective": [(f[0][1],) for f in forms.values() if len(f[0]) == 2 and f[0][0] == "is"
                          and re.fullmatch("[a-z]+", f[0][1])],
            "relative": [tuple(form) for f in forms.values() for form in f]}


def closed_classes() -> dict[str, list[tuple]]:
    """The grammar's closed word classes, each a nonterminal all of whose rules are words only (a marker, a list
    marker, an article, a count, a relative pronoun), as slot alternatives: one per rule, in rule order. Read from the
    grammar source, so a class or word the grammar gains is a slot before anyone lists it."""
    rules = json.loads(GRAMMAR.read_text())
    tok = lambda s: (s["p"],) if type(s) is dict and s.get("before") else _symbol(s)
    by = {}
    for r in rules:
        by.setdefault(r["lhs"], []).append(r["rhs"])
    return {lhs: [tuple(tok(s) for s in rhs) for rhs in alts] for lhs, alts in by.items()
            if all(_symbol(s) is not None for rhs in alts for s in rhs)}


def slot_words(raw: dict) -> dict[str, list[tuple]]:
    """Each slot category's alternatives: the environment's words (`vocabulary`) and the grammar's closed classes."""
    return vocabulary(raw) | closed_classes()


class _Slot(str):
    """A word category's place in a sentence, filled with each of its alternatives when the sentence is spelled;
    while sentences are built it weighs as its first alternative."""


def _symbol(s) -> str | None:
    """A rule symbol's terminal text (a word, a case-folded word, a punctuation mark), or None for a nonterminal."""
    return s if type(s) is str else s.get("c", s.get("p"))


def _join(tokens: list) -> str:
    """Spell tokens as the grammar does: a punctuation symbol marked `before` follows its word without a space."""
    text = ""
    for t in tokens:
        text += t[0] if type(t) is tuple else (" " if text else "") + t
    return text


def opening_templates(raw: dict) -> dict[str, list]:
    """One sentence per grammar rule, so every way a sentence can open (a marker, `it is not the case that`, `there
    is a`, `this is impossible`, a determiner, a term, a listing, ...) is a corpus case. Each rule is put in the
    shortest sentence that reaches its left-hand side, with every other nonterminal at its shortest expansion; read
    from the grammar source and the environment's words, so a rule the grammar gains is a case before anyone lists
    it. Returns tag -> the sentence as tokens: a word, a `before` punctuation mark as a 1-tuple, or a `_Slot` of a
    word category or closed class (`slot_words`). A rule no sentence reaches is absent. Also, under `nest_tag`, each
    rule's sentence that is a formula (`nestable`) in each formula place of each rule (DRI note 2026-10-28c hunt 1:
    `Is it not the case that every service is reviewed?`)."""
    rules = json.loads(GRAMMAR.read_text())
    words = slot_words(raw)
    tok = lambda s: (s["p"],) if type(s) is dict and s.get("before") else _symbol(s)
    size = lambda tokens: sum(len(words[t][0]) if type(t) is _Slot else 1 for t in tokens)
    shortest = {c: [_Slot(c)] for c, alternatives in words.items() if alternatives}
    shortest |= {c: [_Slot(p) if p in WORD_CATEGORIES else p for p in parts] for c, parts in COMPOSITE.items()
                 if all(p not in WORD_CATEGORIES or words[p] for p in parts)}
    changed = True
    while changed:  # the shortest expansion of each nonterminal, to a fixed point
        changed = False
        for r in rules:
            if all(_symbol(s) is not None or s["n"] in shortest for s in r["rhs"]):
                out = [t for s in r["rhs"] for t in ([tok(s)] if _symbol(s) is not None else shortest[s["n"]])]
                if r["lhs"] not in shortest or size(out) < size(shortest[r["lhs"]]):
                    shortest[r["lhs"]], changed = out, True
    hole = HOLE
    context = {"sentence": [hole]}  # the shortest sentence with a hole where the nonterminal goes
    changed = True
    while changed:
        changed = False
        for r in rules:
            if r["lhs"] not in context:
                continue
            for i, s in enumerate(r["rhs"]):
                if _symbol(s) is not None or any(_symbol(o) is None and o["n"] not in shortest
                                                 for j, o in enumerate(r["rhs"]) if j != i):
                    continue
                inner = [t for j, o in enumerate(r["rhs"]) for t in (
                    [hole] if j == i else [tok(o)] if _symbol(o) is not None else shortest[o["n"]])]
                at = context[r["lhs"]].index(hole)
                out = context[r["lhs"]][:at] + inner + context[r["lhs"]][at + 1:]
                if s["n"] not in context or size(out) < size(context[s["n"]]):
                    context[s["n"]], changed = out, True
    templates = {}
    for r in rules:
        if r["lhs"] in context and all(_symbol(s) is not None or s["n"] in shortest for s in r["rhs"]):
            body = [t for s in r["rhs"] for t in ([tok(s)] if _symbol(s) is not None else shortest[s["n"]])]
            at = context[r["lhs"]].index(hole)
            templates[r["tag"]] = context[r["lhs"]][:at] + body + context[r["lhs"]][at + 1:]
    assert context["formula"] == [hole]  # every rule below `sentence` and `marker` has a formula as its sentence
    formulas = nestable(rules, templates)
    for r in rules:  # hunt 1: each such rule's sentence in each place of a rule that takes a formula
        for i, s in enumerate(r["rhs"]):
            if r["tag"] in templates and s == {"n": "formula"}:
                outer = [t for j, o in enumerate(r["rhs"]) for t in (
                    [hole] if j == i else [tok(o)] if _symbol(o) is not None else shortest[o["n"]])]
                at = context[r["lhs"]].index(hole)
                outer = context[r["lhs"]][:at] + outer + context[r["lhs"]][at + 1:]
                for f in formulas:
                    at = outer.index(hole)
                    templates[nest_tag(r["tag"], i, f)] = outer[:at] + templates[f] + outer[at + 1:]
    return templates


def nestable(rules: list[dict], templates: dict) -> list[str]:
    """The rules whose sentence is a formula (all but `sentence` and `marker` rules), which a formula place takes."""
    return [r["tag"] for r in rules if r["lhs"] not in ("sentence", "marker") and r["tag"] in templates]


def nest_tag(outer: str, place: int, inner: str) -> str:
    """The tag of the sentence with formula rule `inner`'s sentence in rule `outer`'s formula at `place`."""
    return f"{NEST}{outer}@{place} {inner}"


def covering(sizes: list[int]) -> list[tuple[int, ...]]:
    """Rows of alternative indexes, one per slot: the all-first row, each row that changes one slot of it (each slot
    varied on its own: `Is there a service that is not reviewed?`), then greedy rows until every two slots have taken
    every pair of their alternatives together (a pairwise covering array, deterministic). The full product of every
    environment's words is about 22 million sentences (FOLLOW-UP in REPORT.md); these are what `coverage` requires."""
    n = len(sizes)
    if n < 2:
        return list(itertools.product(*map(range, sizes)))
    rows = list(dict.fromkeys([(0,) * n] + [(0,) * k + (v,) + (0,) * (n - k - 1)
                                            for k in range(n) for v in range(1, sizes[k])]))
    uncovered = {(i, a, j, b) for i, j in itertools.combinations(range(n), 2)
                 for a in range(sizes[i]) for b in range(sizes[j])}
    uncovered -= {(p, row[p], q, row[q]) for row in rows for p, q in itertools.combinations(range(n), 2)}
    while uncovered:
        i, a, j, b = min(uncovered)
        row = [None] * n
        row[i], row[j] = a, b
        for k in range(n):
            if row[k] is None:
                gain = lambda v: sum(((p, row[p], k, v) if p < k else (k, v, p, row[p])) in uncovered
                                     for p in range(n) if row[p] is not None)
                row[k] = max(range(sizes[k]), key=lambda v: (gain(v), -v))
        uncovered -= {(p, row[p], q, row[q]) for p, q in itertools.combinations(range(n), 2)}
        rows.append(tuple(row))
    return rows


def opening_sentences(raw: dict) -> dict[str, tuple[list, list[tuple]]]:
    """tag -> (`opening_templates`' sentence, its fills): each fill is one alternative of `slot_words` per slot, in
    the rows of `covering`, so every slot is spelled with every declared word of its category and every two slots
    with every pair of them (`Is "atlas2" the same as beacon?`, each polarity in each place); a nested sentence
    (`nest_tag`) is spelled once, with each slot's first word."""
    words = slot_words(raw)
    out = {}
    for tag, template in opening_templates(raw).items():
        slots = [t for t in template if type(t) is _Slot]
        rows = covering([len(words[s]) for s in slots]) if not tag.startswith(NEST) else [(0,) * len(slots)]
        out[tag] = (template, [tuple(words[s][i] for s, i in zip(slots, row)) for row in rows])
    return out


def spell(template: list, fills: tuple) -> list:
    """The template's tokens with each slot replaced by its fill's words."""
    it = iter(fills)
    return [w for t in template for w in (next(it) if type(t) is _Slot else [t])]


def questions(tokens: list) -> list[str]:
    """The sentence asked with the auxiliary taken out, once for each `is` it has (the inverse of the question reader
    putting the auxiliary back in one gap, spec 2.2)."""
    return [f"Is {_join(tokens[:i] + tokens[i + 1:])}?" for i, t in enumerate(tokens) if t == "is"]


def variants(tokens: list) -> list[tuple[str, str]]:
    """(axis, question) for a rule's sentence (DRI note 2026-10-28c hunts 1 and 2): `case`, each word capitalised and
    in capitals, one at a time (`Is Every service reviewed?`); `space`, each of its questions with each gap doubled,
    and with each of Q1.4's space characters (`speech_ab.SPACES`) before it, after it and in its first gap."""
    out = [("case", q) for i, t in enumerate(tokens) if type(t) is str and t.isalpha()
           for v in dict.fromkeys((t.capitalize(), t.upper())) if v != t
           for q in questions(tokens[:i] + [v] + tokens[i + 1:])]
    for q in questions(tokens):
        gaps = [i for i, c in enumerate(q) if c == " "]
        out += [("space", q[:i] + " " + q[i:]) for i in gaps]
        out += [("space", q + c) for c in speech_ab.SPACES] + [("space", c + q) for c in speech_ab.SPACES]
        out += [("space", q[:gaps[0]] + c + q[gaps[0] + 1:]) for c in speech_ab.SPACES if c != " "]
    return out


def base_shaped(template: list) -> bool:
    """Whether the sentence is `<name> <predicate form>`, the one shape the base reads as `Is <name> <words>?`: its
    `variants` are asked for every row, so each name and each declared form in each case and spacing (hunt 2: `Is
    BEACON reviewed?`, `Is atlas reviewed YET never reviewed?`); other rules' for their first row."""
    return template == [_Slot("constant"), _Slot("relative")]


# The deleted branch's own pattern at the merge base (`parse_speech`, ve/speech_english.py at de7cb4022).
BASE_PATTERN = re.compile(r"Is ([A-Za-z][A-Za-z0-9_]*) (.+)\?")


def base_members(raw: dict) -> list[tuple[str, ...]]:
    """The member shapes of the base's acceptance set in `raw` (`in_base_set`): `<name> <declared form>` as tokens,
    for every constant the base's pattern can name and every one-place predicate of its sort whose verbalisation is
    `{0} is <words>` (the base compared the rest with the verbalisation only, never a negative one)."""
    v = raw["vocabulary"]
    return [(c, *p["verbalisation"].removeprefix("{0} ").split()) for c, d in v["constants"].items()
            if BASE_PATTERN.fullmatch(f"Is {c} x?") for p in v["predicates"].values()
            if p["arguments"] == [d["sort"]] and p.get("verbalisation", "").startswith("{0} is ")]


def in_base_set(raw: dict, wording: str) -> bool:
    """DRI 2026-10-28 b item 1 (a): whether `wording` is in the base's acceptance set of the `Is ` branch this item
    deleted, the wordings base `_copular` read: `Is <name> <declared form>?` for exactly one member of `base_members`,
    the name and the form up to ASCII case (`ascii_fold`) and the whole up to the space `wording_text` trims for every
    reader. A wording the base read outside the F1 prefixes is in it (`outside_base_set`); every verdict change of a
    member is a recorded delta.json row (`coverage` asks every member shape in every `variants` form), and every head
    reading outside it is the relay's and `ve ask`'s (tests/test_speech_polar_lean.py, the relay and differential
    tests)."""
    from ve.errors import VEError
    from ve.speech_acts import ascii_fold, wording_text
    try:
        text = wording_text(wording)
    except VEError:
        return False
    if not BASE_PATTERN.fullmatch(text):
        return False
    return sum(ascii_fold(text) == ascii_fold(questions(list(m))[0]) for m in base_members(raw)) == 1


def outside_base_set(records: list[dict]) -> list[dict]:
    """The records of a base recording the base read through the deleted `Is ` branch (a reading whose trimmed wording
    starts with `Is ` but with no F1 prefix, which Lean read at both ends) that `in_base_set` does not hold for."""
    from ve.backends.english_lean import QUESTION_CALLERS, SPEECH_CALLER
    from ve.errors import VEError
    from ve.speech_acts import wording_text
    out = []
    for r in records:
        try:
            text = wording_text(r["wording"])
        except VEError:
            continue
        # The F1 prefixes: the contract's list without F2's fronted `Is ` (which q1-4bb added to it).
        f1 = tuple(prefix for prefix in QUESTION_CALLERS[SPEECH_CALLER] if prefix != "Is ")
        if ("content" in r["outcome"] and text.startswith("Is ") and not text.startswith(f1)
                and not in_base_set(extra_environments()[r["env"]], r["wording"])):
            out.append(r)
    return out


@functools.cache
def all_sentences() -> dict[str, dict]:
    """env -> `opening_sentences` for every environment of `extra_environments`, computed once per run."""
    return {env: opening_sentences(raw) for env, raw in extra_environments().items()}


@functools.cache
def opening_cases() -> list[tuple[str, str, str]]:
    """(env, wording, tag): every question of every sentence of `all_sentences`, and the `variants` of each rule's
    first sentence (tagged `<axis> <rule tag>`); computed once per run."""
    cases = {}
    for env, sentences in all_sentences().items():
        for tag, (template, rows) in sentences.items():
            for fills in rows:
                for wording in questions(spell(template, fills)):
                    cases.setdefault((env, wording), tag)
            if not tag.startswith(NEST):
                for fills in rows if base_shaped(template) else rows[:1]:
                    for axis, wording in variants(spell(template, fills)):
                        cases.setdefault((env, wording), f"{axis} {tag}")
    return [(env, wording, tag) for (env, wording), tag in cases.items()]


def coverage(sentences: dict[str, dict], recorded: set) -> list[str]:
    """What the corpus left unasked; the corpus is complete only when this is empty (DRI note 2026-10-28c (a)). For
    every environment of `extra_environments`, every grammar rule has a sentence unless it needs a category the
    environment cannot fill, and in each rule's sentence every two slots were spelled with every pair of the words
    `slot_words` gives their categories, and each slot with each word on its own (the rule's first sentence with that
    one slot changed), in sentences whose questions are all in
    `recorded` (the saved corpus's (env, wording) pairs); each `variants` question of its first sentence (of every
    sentence, for a `base_shaped` rule) is in
    `recorded`; and each `nestable` rule's sentence was asked in each formula place of the rule (`nest_tag`). A rule
    whose sentence cannot have an `is` is no question and is skipped. `sentences` is env -> `opening_sentences`."""
    rules = json.loads(GRAMMAR.read_text())
    categories = ({s["n"] for r in rules for s in r["rhs"] if type(s) is dict and "n" in s}
                  - {r["lhs"] for r in rules})
    missing = [f"category {c}: spelled by nothing" for c in sorted(
        categories - set(WORD_CATEGORIES) - set(COMPOSITE) - set(UNFILLED))]
    for env, raw in extra_environments().items():
        binary = [n for n, p in raw["vocabulary"]["predicates"].items()
                  if len(p["arguments"]) == 2 and "verbalisation" in p]
        if binary:
            missing.append(f"{env}: two-place verbalisations {binary}, which no slot spells")
        if env not in sentences:
            missing.append(f"{env}: environment never asked")
            continue
        for member in base_members(raw):  # DRI 2026-10-28 b item 1 (a): every member shape of the base's set
            for axis, q in [("words", questions(list(member))[0]), *variants(list(member))]:
                if (env, q) not in recorded:
                    missing.append(f"{env} base set {' '.join(member)!r}: {KINDS[axis]} {q!r} never asked")
        words = slot_words(raw)
        filled = {c for c, alternatives in words.items() if alternatives}
        filled |= {c for c, parts in COMPOSITE.items() if all(p not in WORD_CATEGORIES or p in filled for p in parts)}
        changed = True
        while changed:  # the nonterminals some sentence can spell
            changed = False
            for r in rules:
                if r["lhs"] not in filled and all(_symbol(s) is not None or s["n"] in filled for s in r["rhs"]):
                    filled.add(r["lhs"])
                    changed = True
        for r in rules:
            tag = r["tag"]
            if tag not in sentences[env]:
                if all(_symbol(s) is not None or s["n"] in filled for s in r["rhs"]):
                    missing.append(f"{env} {tag}: grammar rule with no sentence")
                continue
            template, rows = sentences[env][tag]
            slots = [t for t in template if type(t) is _Slot]
            if "is" not in template and not any("is" in w for s in slots for w in words[s]):
                continue
            for fills in itertools.product(*(words[s] for s in slots)) if base_shaped(template) else [
                    tuple(words[s][0] for s in slots)]:
                for axis, q in variants(spell(template, fills)):
                    if (env, q) not in recorded:
                        missing.append(f"{env} {tag}: {axis} variant {q!r} never asked")
            for i, s in enumerate(r["rhs"]):
                for f in nestable(rules, sentences[env]):
                    nested = sentences[env].get(nest_tag(tag, i, f)) if s == {"n": "formula"} else ()
                    if nested == ():
                        continue
                    if nested is None or not any(all((env, q) in recorded for q in questions(spell(nested[0], fill)))
                                                 for fill in nested[1]):
                        missing.append(f"{env} {tag}: {f} in formula place {i} never asked")
            asked = [f for f in rows if len(f) == len(slots)
                     and (qs := questions(spell(template, f))) and all((env, q) in recorded for q in qs)]
            first = tuple(words[s][0] for s in slots)
            for i, s in enumerate(slots):  # each slot varied on its own from the first sentence
                for a in words[s][1:]:
                    if first[:i] + (a,) + first[i + 1:] not in asked:
                        missing.append(f"{env} {tag}: slot {i + 1} ({s}) {' '.join(a)!r} alone never asked")
            for (i, s), (j, t) in itertools.combinations_with_replacement(enumerate(slots), 2):
                seen = {(f[i], f[j]) for f in asked}
                for a in words[s]:
                    for b in (words[t] if i != j else [a]):
                        if (a, b) not in seen:
                            missing.append(f"{env} {tag}: slot {i + 1} ({s}) {' '.join(a)!r}" + (
                                "" if i == j else f" with slot {j + 1} ({t}) {' '.join(b)!r}") + " never asked")
    return missing




def extra_environments() -> dict[str, dict]:
    """The environments of the added cases: Q1.4's (`speech_ab.environments`) and the three this item adds, so every
    environment the evidence asks in is asked in every opening (DRI note 2026-10-28c (b), hunt 1)."""
    from test_speech_acts import environment

    negative = environment().to_dict()
    negative["vocabulary"]["predicates"]["reviewed"]["negative_verbalisation"] = "{0} is not reviewed"
    named = environment().to_dict()
    for name in SPECIAL_NAMES:
        named["vocabulary"]["constants"][name] = {"sort": "service", "description": name}
    unverbalised = environment().to_dict()
    unverbalised["vocabulary"]["predicates"][UNVERBALISED] = {"arguments": ["service"], "description": UNVERBALISED}
    return {**speech_ab.environments(), "negative": negative, "names": named, "unverbalised": unverbalised}


def extra_cases() -> list[tuple[str, str, dict]]:
    """Environment/wording pairs missed by the original Cartesian corpus.

    Keep these outside Q1.4's corpus: that earlier batch's saved evidence is
    frozen.  Both spellings of service names, both subjects of a declared
    negative verbalisation, `reader_cases` and `opening_cases` exercise whole classes, not one reproducer.
    """
    raws = extra_environments()
    return ([(env, wording, raws[env]) for env, wording in named_cases()]
            + [(env, wording, raws[env]) for env, wording, _ in reader_cases()]
            + [(env, wording, raws[env]) for env, wording, _ in opening_cases()])


def named_cases() -> list[tuple[str, str]]:
    """(env, wording) of DRI 2026-10-28 items 1 and 2: both subjects of a declared negative verbalisation, both
    spellings of each special name."""
    return ([("negative", f"Is {name} not reviewed?") for name in NEGATIVE_SUBJECTS]
            + [("names", f"Is {spelling} reviewed?") for name in SPECIAL_NAMES for spelling in (name, f'"{name}"')])


# Loop recheck 1 of fix round 5 (q1-4b-c281354-looprecheck1.final.md): F8-F11 (REPORT.md's open O1-O4) and F13, `Is `
# wordings outside the base's acceptance set that Lean reads at head and the corpus never asked. DRI 2026-10-28 b
# item 1: covered by the relay and differential tests, not by delta.json rows.
RECHECKED = [("speech", "Is Beacon the same as beacon?"), ("speech", "Is Every service REVIEWED?"),
             ("speech", "Is it not the case that if atlas is reviewed, then either atlas is reviewed or atlas is "
                        "reviewed, or both?"),
             ("glossed", "Is it not the case that no Service is reviewed?"),
             ("negative", "Is Every service not reviewed?"), ("negative", "Is there a Service that is not reviewed?")]
HUNT_SEED = 20261028
HUNT_SAMPLE = 1500  # per generator: the differential test runs `ve ask` three times a wording, under 2 min with -n 16
NESTS = (("it", "is", "not", "the", "case", "that"), ("therefore",), ("it", "follows", "that"),
         ("if", "this", "holds", "in", "all", "cases", (",",), "then"))


@functools.cache
def _corpus_keys() -> frozenset[tuple[str, str]]:
    """The (env, wording) pairs of every recording's corpus: Q1.4's and `extra_cases`."""
    return _keys(q14_cases) | frozenset((env, wording) for env, wording, _ in extra_cases())


def _words(tokens: list) -> list[int]:
    return [i for i, t in enumerate(tokens) if type(t) is str and t.isalpha()]


def hunt_one() -> list[tuple[str, str, str]]:
    """Hunt 1 of fix round 5 (DRI note 2026-10-28c (b)), as (env, wording, axis) outside the corpus: on each rule's
    first sentence, each word capitalised and in capitals; the sentence under each of `NESTS` and as the antecedent
    of an `if`; each constant slot filled with a definite or `you`/`it`; `is`/`IS` for `Is`, a doubled space, a space
    before `?` and a trailing space; and each regulated act framed as `permitted to`, `required to`, ...."""
    raws, out = extra_environments(), {}

    def add(env, wording, axis):
        if (env, wording) not in _corpus_keys():
            out.setdefault((env, wording), axis)

    for env, sentences in all_sentences().items():
        definites = [*raws[env]["speech_acts"].get("definites", {}), "you", "it"]
        for tag, (template, rows) in sentences.items():
            tokens = spell(template, rows[0])
            for i in _words(tokens):
                for v in (tokens[i].capitalize(), tokens[i].upper()):
                    for q in questions(tokens[:i] + [v] + tokens[i + 1:]) if v != tokens[i] else ():
                        add(env, q, "case " + tag)
            for wrap in NESTS:
                for q in questions([*wrap, *tokens]):
                    add(env, q, "nest " + tag)
            for q in questions(["if", *tokens, (",",), "then", "this", "holds", "in", "all", "cases"]):
                add(env, q, "nest-if " + tag)
            slots = [k for k, t in enumerate(template) if type(t) is _Slot]
            for n, k in enumerate(slots):
                for d in definites if template[k] == "constant" else ():
                    for q in questions(spell(template, rows[0][:n] + (tuple(d.split()),) + rows[0][n + 1:])):
                        add(env, q, "definite " + tag)
            for q in questions(tokens):
                add(env, "is" + q[2:], "lower-is " + tag)
                add(env, "IS" + q[2:], "upper-is " + tag)
                add(env, q.replace(" ", "  ", 2).replace("  ", " ", 1), "space " + tag)
                add(env, q[:-1] + " ?", "space-q " + tag)
                add(env, q + " ", "trail " + tag)
    for env, raw in raws.items():
        consts = raw["vocabulary"]["constants"]
        for p in raw["vocabulary"]["predicates"].values():
            if not (act := p.get("regulated", {}).get("act")):
                continue
            for x, y in itertools.product(*([c for c, d in consts.items() if d["sort"] == s] for s in p["arguments"])):
                body = act.format(x, y).split()
                for frame in ("permitted to", "required to", "allowed to", "obliged to"):
                    add(env, f"Is {x} {frame} {' '.join(body[1:])}?", "regulated")
                add(env, f"Is it the case that {act.format(x, y)}?", "regulated")
    return [(env, wording, axis) for (env, wording), axis in out.items()]


def hunt_two(seed: int = HUNT_SEED) -> list[tuple[str, str, str]]:
    """Hunt 2 of fix round 5, as (env, wording, axis) outside the corpus: on up to three rows of each rule, a word
    capitalised and then a second in capitals (two variants at once, O2); a tab for a space, two doubled spaces, a
    leading space, `Isn't` for `Is`, `ſ` for `s`; and on up to 60 nested sentences, the sentence nested again (two
    deep, O3), in an `if` with itself, with a word capitalised (a variant inside a nesting, O4) and a doubled space."""
    import random
    rnd, out = random.Random(seed), {}

    def add(env, wording, axis):
        if (env, wording) not in _corpus_keys():
            out.setdefault((env, wording), axis)

    for env, sentences in all_sentences().items():
        for tag in [t for t in sentences if not t.startswith(NEST)]:
            template, rows = sentences[tag]
            for fills in rnd.sample(rows, min(3, len(rows))):
                tokens = spell(template, fills)
                for _ in range(2):
                    i, j = rnd.choice(_words(tokens)), rnd.choice(_words(tokens))
                    once = tokens[:i] + [tokens[i].capitalize()] + tokens[i + 1:]
                    for q in questions(once):
                        add(env, q, "case-row " + tag)
                    for q in questions(once[:j] + [once[j].upper()] + once[j + 1:]):
                        add(env, q, "case-two " + tag)
                for q in questions(tokens):
                    gaps = [k for k, c in enumerate(q) if c == " "]
                    k = rnd.choice(gaps)
                    add(env, q[:k] + "\t" + q[k + 1:], "space-row " + tag)
                    a, b = rnd.sample(gaps, 2) if len(gaps) > 1 else (gaps[0], gaps[0])
                    add(env, q[:a] + "  " + q[a + 1:b] + "  " + q[b + 1:] if a < b else q, "space-two " + tag)
                    add(env, " " + q, "lead " + tag)
                    add(env, "Isn't" + q[2:], "isnt " + tag)
                    add(env, q[:3] + q[3:].replace("s", "ſ", 1), "unicode " + tag)
        nests = [t for t in sentences if t.startswith(NEST)]
        for tag in rnd.sample(nests, min(60, len(nests))):
            template, rows = sentences[tag]
            tokens = spell(template, rows[0])
            for q in questions([*NESTS[0], *tokens]):
                add(env, q, "nest2 " + tag)
            for q in questions(["if", *tokens, (",",), "then", *tokens]):
                add(env, q, "nest2-if " + tag)
            i = rnd.choice(_words(tokens))
            for q in questions(tokens[:i] + [tokens[i].capitalize()] + tokens[i + 1:]):
                add(env, q, "nest-case " + tag)
            for q in questions(tokens):
                add(env, q.replace(" ", "  ", 1), "nest-space " + tag)
    return [(env, wording, axis) for (env, wording), axis in out.items()]


@functools.cache
def hunt_sample(size: int = HUNT_SAMPLE, seed: int = HUNT_SEED) -> tuple[tuple[str, str, str], ...]:
    """A fixed-seed sample of `size` candidates of each hunt generator (DRI 2026-10-28 b item 1 (c)), then
    `RECHECKED`, as (env, wording, generator); recorded at the base in evidence/hunt-base.json.gz (`hunt`)."""
    import random
    out = {}
    for name, generator in (("hunt_one", hunt_one), ("hunt_two", hunt_two)):
        candidates = sorted({(env, wording) for env, wording, _ in generator()})
        for env, wording in random.Random(seed).sample(candidates, min(size, len(candidates))):
            out.setdefault((env, wording), name)
    for env, wording in RECHECKED:
        out.setdefault((env, wording), "rechecked")
    return tuple((env, wording, name) for (env, wording), name in out.items())


def hunt(out: str, jobs: int = 1) -> None:
    """Record `hunt_sample` with this checkout's parser (VE_AB_ROOT selects the base's) as a saved corpus."""
    cases = [(env, wording) for env, wording, _ in hunt_sample()]
    save([{"env": env, "wording": wording, "outcome": outcome}
          for (env, wording), outcome in zip(cases, outcomes(cases, jobs))], out)


def load(path) -> list[dict]:
    """A saved corpus: a list of {env, wording, outcome}, gzipped when its name ends in `.gz`."""
    path = Path(path)
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_text())


def save(rows: list[dict], path) -> None:
    """Write a saved corpus, gzipped (reproducibly: no time stamp) when its name ends in `.gz`."""
    path = Path(path)
    if path.suffix == ".gz":
        path.write_bytes(gzip.compress(json.dumps(rows, sort_keys=True).encode() + b"\n", mtime=0))
    else:
        path.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")


@functools.cache
def _environment(env: str):
    from ve.environment import Environment
    return Environment(extra_environments()[env])


def _outcomes(batch: list[tuple[str, str]]) -> list[dict]:
    """`speech_ab.outcome` of each (env, wording), in a worker of `outcomes`."""
    return [speech_ab.outcome(_environment(env), wording) for env, wording in batch]


def outcomes(cases: list[tuple[str, str]], jobs: int = 1) -> list[dict]:
    """`speech_ab.outcome` of each (env, wording) in order, in `jobs` processes (each with its own Lean service)."""
    batches = [cases[i:i + 200] for i in range(0, len(cases), 200)]
    if jobs <= 1:
        return [o for batch in batches for o in _outcomes(batch)]
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(jobs, mp_context=multiprocessing.get_context("spawn")) as pool:
        return [o for done in pool.map(_outcomes, batches) for o in done]


def augment(source: str, out: str, jobs: int = 1) -> None:
    """Append the new cases to a saved base/head corpus using this checkout's parser, in `jobs` processes.

    VE_AB_ROOT selects the base parser when recording base answers; the corpus
    and this script always come from the current checkout.
    """
    rows = load(source)
    keys = {(row["env"], row["wording"]) for row in rows}
    new = []
    for env_name, wording, _ in extra_cases():
        if (env_name, wording) not in keys:  # in Q1.4's corpus, or recorded by an earlier augment
            keys.add((env_name, wording))
            new.append((env_name, wording))
    rows += [{"env": env, "wording": wording, "outcome": outcome}
             for (env, wording), outcome in zip(new, outcomes(new, jobs))]
    save(rows, out)


def code_worded() -> frozenset[str]:
    """The codes whose class writes `Code: text` (`ve.errors._CodeWorded`)."""
    from ve import errors
    return frozenset(c.code for c in vars(errors).values()
                     if isinstance(c, type) and issubclass(c, errors._CodeWorded) and c is not errors._CodeWorded)


def rerecord(source: str, out: str, jobs: int = 1) -> int:
    """Re-record, with this checkout's parser, every record of a saved corpus whose outcome has a `code_worded` code
    (the loop recheck's relay fix: `read_question` now raises Lean's lines verbatim, so only those messages change);
    the rest are kept. Returns how many were re-recorded."""
    rows = load(source)
    stale = [i for i, r in enumerate(rows) if r["outcome"].get("code") in code_worded()]
    for i, outcome in zip(stale, outcomes([(rows[i]["env"], rows[i]["wording"]) for i in stale], jobs)):
        rows[i] = {**rows[i], "outcome": outcome}
    save(rows, out)
    return len(stale)


def compared(base: list[dict], head: list[dict]) -> list[dict]:
    """Every row whose outcome differs between the two recordings, classed by Q1.4's `speech_ab.kind_of`."""
    if [(r["env"], r["wording"]) for r in base] != [(r["env"], r["wording"]) for r in head]:
        raise SystemExit("the two runs do not cover the same corpus")
    return [{"class": k, "env": b["env"], "wording": b["wording"], "base": b["outcome"], "head": h["outcome"]}
            for b, h in zip(base, head) if (k := speech_ab.kind_of(b["outcome"], h["outcome"])) is not None]


def summary(base: list[dict], head: list[dict], rows: list[dict] | None = None) -> dict:
    """delta.json: the record and class counts of `compared` (`rows`, when the caller has it), and its `verdict` and
    `lint` rows (the ones a ruling signs); its `class` and `wording` rows are recomputed from the recordings by
    `check`."""
    rows = compared(base, head) if rows is None else rows
    return {"records": len(base), "counts": {k: sum(r["class"] == k for r in rows)
                                             for k in ("verdict", "class", "wording", "lint")},
            "rows": [r for r in rows if r["class"] in ("verdict", "lint")]}


GLOSS_PREDICATES = {name for name, _ in speech_ab.GLOSSES} | {"cat"}


def _named(r: dict) -> tuple[str, str] | None:
    """The name as the wording writes it and the constant the base read, for a base polar reading of one constant."""
    body = r["base"].get("content", {}).get("body")
    if r["base"].get("kind") != "question" or type(body) is not list or body[0] != "unary":
        return None
    return r["wording"].split(" ")[1], body[2][1]


def gloss(r: dict) -> bool:
    named = _named(r)
    return (r["class"] == "verdict" and (r["env"], r["wording"]) in _keys(q14_cases) and named is not None and named[0] == named[1]
            and r["base"]["content"]["body"][1] in GLOSS_PREDICATES and r["head"].get("code") == "SyntaxError")


def folded(r: dict) -> bool:
    named = _named(r)
    return (r["class"] == "verdict" and (r["env"], r["wording"]) in _keys(q14_cases) and named is not None and named[0] != named[1]
            and named[0].casefold() == named[1] and named[0] != named[1].capitalize()
            and r["head"].get("code") == "SyntaxError")


def quantified(r: dict) -> bool:
    word = r["wording"].split(" ")[1]
    body = r["head"].get("content", {}).get("body")
    return (r["class"] == "verdict" and r["env"] not in EXTRA_ENVS and word in ("every", "some")
            and r["wording"] == f"Is {word} service reviewed?"
            and r["base"].get("message") == f"UnknownAlternative: wording, {word}" and type(body) is list
            and body[0] == {"every": "forall", "some": "exists"}[word])


def negative(r: dict) -> bool:
    name = r["wording"].split()[1]
    return (r["class"] == "verdict" and r["env"] == "negative" and name in NEGATIVE_SUBJECTS
            and r["wording"] == f"Is {name} not reviewed?" and r["base"].get("code") == "SyntaxError"
            and r["head"].get("content", {}).get("body") == ["not", ["unary", "reviewed", ["const", name]]])


def _spelled(r: dict, quoted: bool) -> bool:
    """Item 2: the bare spelling goes from polar to `SyntaxError`, the quoted one from `InvalidInput` to polar."""
    name = r["wording"].removeprefix("Is ").removesuffix(" reviewed?").strip('"')
    if r["class"] != "verdict" or r["env"] != "names" or name not in SPECIAL_NAMES or r["wording"] != (
            f'Is "{name}" reviewed?' if quoted else f"Is {name} reviewed?"):
        return False
    atom = ["unary", "reviewed", ["const", name]]
    read, refused = (r["head"], r["base"]) if quoted else (r["base"], r["head"])
    return read.get("content", {}).get("body") == atom and refused.get("code") == (
        "InvalidInput" if quoted else "SyntaxError")


# The formula a determiner's question has over its predicate's atom (spec 2.2-2.4 as Lean reads it); a determiner
# the grammar gains and this table lacks fails the audit with a KeyError until its reading is recorded here.
QUANTIFIED = {"every": lambda atom: ["forall", "service", atom], "some": lambda atom: ["exists", "service", atom],
              "no": lambda atom: ["not", ["exists", "service", atom]]}


def _reads(r: dict, predicate: str) -> bool:
    """The head is the reading of `Is <subject> <predicate>?`: the atom of the name, or the determiner's formula."""
    subject = r["wording"].split(" ")[1]
    body = r["head"].get("content", {}).get("body")
    if subject in determiners():
        return body == QUANTIFIED[subject](["unary", predicate, ["var", 0]])
    return body == ["unary", predicate, ["const", subject]]


def determiner(r: dict) -> bool:
    word = r["wording"].split(" ")[1]
    return (r["class"] == "verdict" and r["env"] == "speech" and word in set(determiners()) - {"every", "some"}
            and r["wording"] == f"Is {word} service reviewed?"
            and r["base"].get("message") == f"UnknownAlternative: wording, {word}" and _reads(r, "reviewed"))


def unverbalised(r: dict) -> bool:
    return (r["class"] == "verdict" and r["env"] == "unverbalised" and (r["env"], r["wording"]) in _keys(
        reader_cases) and r["base"].get("code") in (
        "SyntaxError", "InvalidInput") and r["wording"].removesuffix("?").split()[-1].casefold() == UNVERBALISED
            and _reads(r, UNVERBALISED))


@functools.cache
def _keys(cases) -> frozenset[tuple[str, str]]:
    """The (env, wording) pairs of `named_cases`, `reader_cases` or `q14_cases`, computed once per run."""
    return frozenset((env, wording) for env, wording, *_ in cases())


def q14_cases() -> list[tuple[str, str]]:
    """Q1.4's corpus (`speech_ab.write`), which every recording starts with."""
    return [(env, wording) for env in speech_ab.environments() for wording in speech_ab.wordings()]


def opening(r: dict) -> bool:
    """Item 5 (class (d)): a verdict change of an `Is ` question (after any leading space) this item added, outside
    Q1.4's corpus and the cases recorded before it (`named_cases`, `reader_cases`), in either direction (item 5 signs
    any `Is ` verdict change meeting (i)-(iii)); that the head's verdict and text are `ve ask`'s is the test's to show
    (`test_every_opening_verdict_row_is_read_as_ve_ask_reads_it`), and that every question of the class is asked is
    `coverage`'s."""
    return (r["class"] == "verdict" and r["wording"].lstrip("".join(speech_ab.SPACES)).startswith("Is ")
            and (r["env"], r["wording"]) not in _earlier())


@functools.cache
def _earlier() -> frozenset[tuple[str, str]]:
    """The cases recorded before class (d): Q1.4's corpus, `reader_cases` and `named_cases`."""
    return _keys(q14_cases) | _keys(reader_cases) | _keys(named_cases)


# Each class, its decision (manage-agents/reviews/) and its count in the recorded delta.
CLASSES = {"gloss": gloss, "folded": folded, "quantified": quantified, "negative": negative,
           "bare_name": lambda r: _spelled(r, False), "quoted_name": lambda r: _spelled(r, True),
           "determiner": determiner, "unverbalised": unverbalised, "opening": opening}
DECIDED = {"gloss": 10, "folded": 3, "quantified": 6,  # dri-decisions-20261027-featureplan-gates.md item 4
           "negative": len(NEGATIVE_SUBJECTS), "bare_name": len(SPECIAL_NAMES),  # dri-decisions-20261028-q1-4b.md
           "quoted_name": len(SPECIAL_NAMES), "determiner": 1, "unverbalised": 8,  # items 1, 2, 2, 3, 4 and 5
           "opening": 6608}  # item 5


@functools.cache
def recordings(folder: str) -> tuple[list[dict], list[dict], list[dict]]:
    """The saved base and head corpora in `folder` and their `compared` rows, read once per run."""
    base, head = load(Path(folder) / "base.json.gz"), load(Path(folder) / "head.json.gz")
    return base, head, compared(base, head)


@functools.cache
def hunt_recording(folder: str) -> list[dict]:
    """The saved base recording of `hunt_sample` in `folder` (hunt-base.json.gz), read once per run."""
    return load(Path(folder) / "hunt-base.json.gz")


def audit(rows: list[dict]) -> tuple[dict, list[dict]]:
    """Each class's count over `rows`, and the failing rows: a `lint` row, a `verdict` row not in exactly one signed
    class, a `class` or `wording` row that neither keeps R1 nor is O1."""
    counts = {name: sum(map(test, rows)) for name, test in CLASSES.items()}
    return counts, [r for r in rows if r["class"] == "lint"
                    or r["class"] == "verdict" and sum(test(r) for test in CLASSES.values()) != 1
                    or r["class"] in ("class", "wording") and not speech_ab.order_o1(r) and not speech_ab.keeps(r)]


def check(delta_path: str) -> int:
    """The audit: delta.json is `summary` of base.json.gz and head.json.gz beside it, `audit` finds no failing row
    and the recorded counts, and the corpus is complete (`coverage`); any other case exits 1."""
    base, head, rows = recordings(str(Path(delta_path).parent))
    same = json.loads(Path(delta_path).read_text()) == summary(base, head, rows)
    counts, bad = audit(rows)
    for r in bad:
        print("fails:", r["class"], r["env"], repr(r["wording"]), r["base"].get("message"), "->",
              r["head"].get("message"))
    if not same:
        print("fails: delta.json is not the summary of base.json.gz and head.json.gz")
    missing = coverage(all_sentences(), {(r["env"], r["wording"]) for r in head})
    for line in missing[:20]:
        print("unasked:", line)
    outside = outside_base_set(base + hunt_recording(str(Path(delta_path).parent)))
    for r in outside:
        print("fails: the base read", r["env"], repr(r["wording"]), "outside its acceptance set (`in_base_set`)")
    refusals = [r for r in rows if r["class"] in ("class", "wording")]
    o1 = [r for r in refusals if speech_ab.order_o1(r)]
    print(json.dumps({"rows": len(rows), **counts, "O1": len(o1), "R1": len(refusals) - len(o1),
                      "failing": len(bad), "unasked": len(missing), "outside_base_set": len(outside)}))
    return 1 if bad or counts != DECIDED or not same or missing or outside else 0


KINDS = {"words": "opening", "case": "case variant", "space": "spacing variant", "nest": "nested in",
         "earlier": "a case an earlier generator asked (still recorded)"}


def _group(r: dict, tags: dict) -> tuple[str, str]:
    """A class (d) row's DELTA group: the axis that asked it (`KINDS`) and its rule (a nested one's outer rule)."""
    tag = tags.get((r["env"], r["wording"]))
    if tag is None:
        return "earlier", ""
    if tag.startswith(NEST):
        return "nest", tag.split()[1].split("@")[0]
    parts = tag.split()
    return (parts[0], parts[1]) if len(parts) == 2 else ("words", parts[0])


def _cell(outcome: dict) -> str:
    if "error" in outcome:
        return f"`{outcome.get('code')}` {outcome.get('message', '')[:100]}".replace("|", "\\|")
    return f"polar `{json.dumps(outcome['content'].get('body'))}`"


TRIMMED = " (compared on wording_text, reviews/dri-decisions-20261028-q1-4b-b.md item 2)"


def trimmed(r: dict) -> bool:
    """Whether the row's wording has space around it that `wording_text` trims for every reader (DRI 2026-10-28 b
    item 2: its condition test compares the speech caller with `ve ask` on the trimmed wording)."""
    from ve.speech_acts import wording_text
    return wording_text(r["wording"]) != r["wording"]


def delta_md(delta_path: str, first: int) -> str:
    """DELTA.md's class (d) rows, one per `_group`, numbered from P`first`: its count, environments and first row;
    the Ruling cell of a group holding a `trimmed` row says it is compared on `wording_text` (`TRIMMED`)."""
    tags = {(env, wording): tag for env, wording, tag in opening_cases()}
    groups = {}
    for r in json.loads(Path(delta_path).read_text())["rows"]:
        if opening(r):
            groups.setdefault(_group(r, tags), []).append(r)
    test = "tests/test_speech_polar_lean.py::test_every_opening_verdict_row_is_read_as_ve_ask_reads_it"
    return "".join(
        f"| P{n} | (d) {KINDS[kind]}" + (f", rule `{rule}`" if rule else "") + f", {len(rows):,} rows | "
        f"{', '.join(sorted({r['env'] for r in rows}))} | `{json.dumps(rows[0]['wording'])[1:-1]}` | "
        f"{_cell(rows[0]['base'])} | {_cell(rows[0]['head'])} | SIGNED by the DRI 2026-10-28 "
        f"(reviews/dri-decisions-20261028-q1-4b.md item 5)" + (TRIMMED if any(map(trimmed, rows)) else "")
        + f"; condition test `{test}` |\n"
        for n, ((kind, rule), rows) in enumerate(sorted(groups.items()), first))


if __name__ == "__main__":
    if sys.argv[1:2] == ["augment"] and len(sys.argv) in (4, 5):
        augment(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) == 5 else 1)
    elif sys.argv[1:2] == ["rerecord"] and len(sys.argv) in (4, 5):
        print(rerecord(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) == 5 else 1), "re-recorded")
    elif sys.argv[1:2] == ["hunt"] and len(sys.argv) in (3, 4):
        hunt(sys.argv[2], int(sys.argv[3]) if len(sys.argv) == 4 else 1)
    elif sys.argv[1:2] == ["delta-md"] and len(sys.argv) == 4:
        sys.stdout.write(delta_md(sys.argv[2], int(sys.argv[3])))
    elif sys.argv[1:2] == ["delta"] and len(sys.argv) == 5:
        Path(sys.argv[4]).write_text(json.dumps(summary(load(sys.argv[2]), load(sys.argv[3])), indent=1,
                                                sort_keys=True) + "\n")
    elif sys.argv[1:2] not in (["check"], ["audit"]) or len(sys.argv) != 3:
        raise SystemExit(__doc__)
    else:
        raise SystemExit(check(sys.argv[2]))
