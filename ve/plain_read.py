# ve-layer: 4 (plain-text reader: an untrusted deriver builds a document from the text and the word list; Lean reads it)
"""`ve read`: a plain text with no front matter, read with the built-in word list (plain vocabulary, version 1).

The text's lines must each be in one of the shapes below; the deriver (untrusted Python) classifies every line, derives
the vocabulary from the word list (`ve/lexicon`, oewn-2025), shows it, and builds an ordinary `ve-document@1` with one
fence per rule or fact line. Lean then reads that document as any other: its coverage table must show every byte
CHECKED before any question is answered, and every answer is Lean's (`ve.ask`). Anything the deriver is unsure of is
refused by name, with the one line that fixes it where there is one; nothing is guessed and no line is ever skipped.

Shapes (one sentence each; several sentences may share a line):
  Every <noun> who|that is [not] <word> [and is [not] <word>] is [not] <word>.
  <Name> is a|an <noun>.          (says what a name is; exactly one per name)
  <Name> is [not] <word>.
  Is <Name> <word>?               (a question; every one is answered)
  Words: <word> (property of <noun>)   /   Words: <noun> (kind of thing)   (a declaration, for a word not in the list)

What Lean checks and what it does not: Lean checks that the derived vocabulary is well-formed and reads every sentence
one way over it; it does not check that the vocabulary was derived from the word list. The line classifier, the
fencing, the name-to-kind binding and the shown list are untrusted and tested only (prompts of row plain-vocabulary-1126,
design (d) 5). A word has one meaning within a text: a property word with more than one sense in the list is always
shown with its sense count, because the text is read with one meaning for it throughout.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from functools import lru_cache
import hashlib
from importlib.resources import files
import json
from pathlib import Path
import re
import sys
import tempfile

from .errors import CheckerUnavailable, ResourceLimit, VEError

FORMAT = "ve-plain-read@1"
EXIT_READ, EXIT_UNKNOWN, EXIT_NOT_READ, EXIT_LIMIT, EXIT_UNAVAILABLE = 0, 3, 2, 4, 5
MAX_TEXT_BYTES = 64_000
_WORD = r"[a-z][a-z'-]*"
_NAME = r"[A-Z][a-z]+"
RULE = re.compile(rf"^Every ({_WORD}) (who|that) is( not)? ({_WORD})(?: and is( not)? ({_WORD}))? is( not)? ({_WORD})\.$")
KIND = re.compile(rf"^({_NAME}) is (a|an) ({_WORD})\.$")
FACT = re.compile(rf"^({_NAME}) is( not)? ({_WORD})\.$")
QUESTION = re.compile(rf"^Is ({_NAME}) ({_WORD})\?$")
WORDS_PROPERTY = re.compile(rf"^Words: ({_WORD}) \(property of ({_WORD})\)$")
WORDS_KIND = re.compile(rf"^Words: ({_WORD}) \(kind of thing\)$")
# Near misses, for a refusal that says what is wrong: two words where the shape takes one.
_SLOT = r"[A-Za-z][A-Za-z'-]*"
KIND_TWO = re.compile(rf"^({_NAME}) is (a|an) ({_SLOT}) ({_SLOT})\.$")
FACT_TWO = re.compile(rf"^({_NAME}) is( not)? ({_SLOT}(?: {_SLOT})+)\.$")
RULE_LOOSE = re.compile(r"^Every \S+ (?:who|that) is .*\.$")
SHAPES = ("Every <noun> who|that is [not] <word> [and is [not] <word>] is [not] <word>.",
          "<Name> is a|an <noun>.", "<Name> is [not] <word>.", "Is <Name> <word>?",
          "Words: <word> (property of <noun>)", "Words: <noun> (kind of thing)")
# Irregular plurals for a kind's display (the shapes never use a plural; Lean's vocabulary needs one).
_PLURALS = {"person": "people", "child": "children", "man": "men", "woman": "women", "foot": "feet",
            "tooth": "teeth", "mouse": "mice", "goose": "geese", "sheep": "sheep", "deer": "deer", "fish": "fish",
            "staff": "staff", "ox": "oxen"}


@dataclass(frozen=True)
class Sentence:
    """One sentence of the text: where it is, its words as written, and the shape it is in (None: no shape)."""
    line: int
    index: int  # 1-based position within its line
    text: str
    shape: str | None
    groups: tuple = ()

    @property
    def where(self) -> str:
        return f"line {self.line}" if self.index == 1 else f"line {self.line} (sentence {self.index})"


@dataclass(frozen=True)
class Refusal:
    """Why the text is not read: a code, where, the word, the message, and the offered fix (a whole line), if any."""
    code: str
    line: int
    word: str
    message: str
    fix: str | None = None
    replaces: int | None = None  # the fix replaces this line (else it is added)

    def as_dict(self) -> dict:
        return {"code": self.code, "line": self.line, "word": self.word, "message": self.message,
                "fix": self.fix, "replaces": self.replaces}


@dataclass
class Derived:
    """What the deriver found: the sentences, the vocabulary rows shown to the writer, the document, the refusals."""
    sentences: list = field(default_factory=list)
    refusals: list = field(default_factory=list)
    kinds: dict = field(default_factory=dict)        # noun -> {"senses": n, "declared": line | None}
    properties: dict = field(default_factory=dict)   # word -> {"kind": noun, "classes": [...], "lemmas": [...], ...}
    names: dict = field(default_factory=dict)        # Name -> {"kind": noun, "line": n}
    statements: list = field(default_factory=list)   # the rule and fact sentences, in text order
    questions: list = field(default_factory=list)    # the question sentences, in text order
    raw: bytes | None = None                         # the derived ve-document@1, when nothing is refused


@lru_cache(maxsize=1)
def lexicon_digest() -> str:
    """SHA-256 of the word list the derivation reads; it is in every derived description, so in every identity."""
    from .lexicon import VERSION
    return hashlib.sha256(files("ve.lexicon").joinpath(VERSION + ".json").read_bytes()).hexdigest()


def _entries(word: str):
    from .lexicon import _index
    index, _ = _index()
    return index.get(word, ())


def _fits(word: str, classes: set) -> list:
    """The word list's analyses of `word` whose class fits a slot: (class, lemma, sense keys)."""
    return [row for row in _entries(word) if row[0] in classes]


def _senses(rows) -> int:
    return sum(len(keys) for _, _, keys in rows)


def plural(noun: str) -> str:
    if noun in _PLURALS:
        return _PLURALS[noun]
    if re.search(r"[^aeiou]y$", noun):
        return noun[:-1] + "ies"
    if re.search(r"(s|x|z|ch|sh)$", noun):
        return noun + "es"
    return noun + "s"


def split_text(text: str) -> list:
    """Every sentence of the text with its line, classified. Blank lines are the only thing not a sentence."""
    out = []
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        pieces = [p for p in re.split(r"(?<=[.?])\s+", stripped) if p]
        for index, piece in enumerate(pieces, 1):
            for shape, pattern in (("rule", RULE), ("kind", KIND), ("fact", FACT), ("question", QUESTION),
                                   ("words-property", WORDS_PROPERTY), ("words-kind", WORDS_KIND)):
                m = pattern.match(piece)
                if m:
                    out.append(Sentence(number, index, piece, shape, m.groups()))
                    break
            else:
                out.append(Sentence(number, index, piece, None))
    return out


def _off_shape(s: Sentence) -> Refusal:
    m = KIND_TWO.match(s.text)
    if m and m.group(4).islower() and m.group(3).islower():
        name, article, first, second = m.groups()
        return Refusal("TWO_WORDS", s.line, f"{first} {second}",
                       f"{s.where}: \"{s.text}\" has two words where the shape takes one noun ('{first} {second}'). "
                       f"Write what {name} is in one line and the property in another.",
                       f"{name} is {'an' if second[0] in 'aeiou' else 'a'} {second}. {name} is {first}.", s.line)
    m = FACT_TWO.match(s.text)
    if m and m.group(3).islower() and not m.group(3).startswith(("a ", "an ")):
        return Refusal("TWO_WORDS", s.line, m.group(3),
                       f"{s.where}: \"{s.text}\" has more than one word where the shape takes one ('{m.group(3)}'). "
                       "VE reads one word there; choose one word that means it (no line can be offered without "
                       "guessing what you mean).")
    if RULE_LOOSE.match(s.text):
        return Refusal("UNKNOWN_LINE", s.line, "",
                       f"{s.where}: \"{s.text}\" starts like a rule but is not in the rule shape (one word after each "
                       "'is', at most two conditions joined by 'and'). The whole text is refused; no line is skipped.")
    return Refusal("UNKNOWN_LINE", s.line, "",
                   f"{s.where}: \"{s.text}\" is not in a shape VE reads. The whole text is refused; no line is "
                   "skipped. The shapes: " + "; ".join(SHAPES) + ".")


def derive(text: str) -> Derived:
    """Classify every sentence and derive the vocabulary; on no refusal, the document Lean will read (`raw`)."""
    from .environment import RESERVED
    d = Derived(sentences=split_text(text))
    refuse = d.refusals.append
    for s in d.sentences:
        if s.shape is None:
            refuse(_off_shape(s))
    # Declarations: kinds and properties the writer declared (offered lines), then the names' kinds.
    declared_kinds, declared_props = {}, {}
    for s in d.sentences:
        if s.shape == "words-kind":
            declared_kinds.setdefault(s.groups[0], s.line)
        elif s.shape == "words-property":
            word, noun = s.groups
            if word in declared_props and declared_props[word][0] != noun:
                refuse(Refusal("WORD_TWO_KINDS", s.line, word,
                               f"{s.where}: '{word}' is declared for two kinds ({declared_props[word][0]}, {noun})."))
            declared_props.setdefault(word, (noun, s.line))
    kind_lines = {}
    for s in d.sentences:
        if s.shape == "kind":
            name, _, noun = s.groups
            kind_lines.setdefault(name, []).append((s, noun))
    for name, rows in kind_lines.items():
        if len(rows) > 1:
            where = ", ".join(r[0].where for r in rows)
            refuse(Refusal("NAME_TWO_KINDS", rows[1][0].line, name,
                           f"{name} is said to be a kind of thing {len(rows)} times ({where}); each name needs exactly "
                           f"one '{name} is a <noun>.' line. Remove all but one."))
        d.names[name] = {"kind": rows[0][1], "line": rows[0][0].line}
    # Kinds: every binder noun and every noun after 'is a'.
    noun_uses = {}
    for s in d.sentences:
        if s.shape == "rule":
            noun_uses.setdefault(s.groups[0], s)
        elif s.shape == "kind":
            noun_uses.setdefault(s.groups[2], s)
        elif s.shape == "words-property":
            noun_uses.setdefault(s.groups[1], s)
    for noun, s in noun_uses.items():
        rows = _fits(noun, {"noun"})
        if noun in declared_kinds:
            d.kinds[noun] = {"senses": _senses(rows), "declared": declared_kinds[noun], "in_list": bool(rows)}
        elif rows:
            d.kinds[noun] = {"senses": _senses(rows), "declared": None, "in_list": True}
        else:
            refuse(Refusal("UNKNOWN_WORD", s.line, noun,
                           f"{s.where}: '{noun}' is not a noun in the word list (oewn-2025), so VE does not know it "
                           f"as a kind of thing.", f"Words: {noun} (kind of thing)"))
    # Names used in facts and questions need exactly one 'is a' line.
    nouns = sorted(noun_uses)
    two_word_kinds = {m.group(1) for s in d.sentences if s.shape is None and (m := KIND_TWO.match(s.text))}
    for s in d.sentences:
        if s.shape in ("fact", "question") and s.groups[0] not in d.names:
            name = s.groups[0]
            if name in two_word_kinds or any(r.code == "NAME_NO_KIND" and r.word == name for r in d.refusals):
                continue
            fix = f"{name} is {'an' if nouns[0][0] in 'aeiou' else 'a'} {nouns[0]}." if len(nouns) == 1 else None
            refuse(Refusal("NAME_NO_KIND", s.line, name,
                           f"{s.where}: VE does not know what {name} is: no line says '{name} is a <noun>.'"
                           + ("" if fix else " (the text has more than one kind of thing, so VE offers no line)."),
                           fix))
    # Property words and the one kind each belongs to.
    uses = {}  # word -> [(sentence, kind)]
    for s in d.sentences:
        if s.shape == "rule":
            noun, _, _, w1, _, w2, _, w3 = s.groups
            for w in (w1, w2, w3):
                if w:
                    uses.setdefault(w, []).append((s, noun))
        elif s.shape in ("fact", "question"):
            name, w = s.groups[0], s.groups[-1]
            kind = d.names.get(name, {}).get("kind")
            if kind:
                uses.setdefault(w, []).append((s, kind))
        elif s.shape == "words-property":
            uses.setdefault(s.groups[0], []).append((s, s.groups[1]))
    for word, rows in uses.items():
        kinds = sorted({k for _, k in rows})
        first = rows[0][0]
        if len(kinds) > 1:
            places = "; ".join(f"{k} ({', '.join(sorted({r[0].where for r in rows if r[1] == k}))})" for k in kinds)
            refuse(Refusal("WORD_TWO_KINDS", first.line, word,
                           f"'{word}' is used for {len(kinds)} kinds of thing: {places}. A word belongs to one kind of "
                           "thing in a text; use a different word for one of them."))
            continue
        kind = kinds[0]
        if word in noun_uses:
            refuse(Refusal("WORD_IS_KIND", first.line, word, f"{first.where}: '{word}' is used both as a kind of "
                           "thing and as a property; use a different word for one of them."))
            continue
        fitting = _fits(word, {"adjective", "participle"})
        entry = {"kind": kind, "classes": sorted({c for c, _, _ in fitting}),
                 "lemmas": sorted({lemma for c, lemma, _ in fitting if c == "participle"}),
                 "senses": _senses(fitting), "declared": None, "lines": sorted({r[0].line for r in rows})}
        if word in declared_props and declared_props[word][0] == kind:
            entry["declared"] = declared_props[word][1]
        elif not fitting:
            classes = sorted({c for c, _, _ in _entries(word)})
            why = (f"is in the word list only as {' and '.join(classes)}" if classes
                   else "is not in the word list (oewn-2025)")
            refuse(Refusal("UNKNOWN_WORD", first.line, word,
                           f"{first.where}: '{word}' {why}; after 'is' VE reads an adjective or a past participle.",
                           f"Words: {word} (property of {kind})"))
            continue
        d.properties[word] = entry
    # Words the reading would confuse: hyphens, reserved words, a word that is also a kind or a name.
    names_lower = {n.lower(): n for n in d.names}
    for word, entry in list(d.properties.items()):
        line = entry["lines"][0]
        if "-" in word or "'" in word:
            refuse(Refusal("HYPHEN", line, word, f"line {line}: '{word}' has a hyphen or apostrophe; VE reads a "
                           "property word written as one plain word (no line can be offered without guessing)."))
        elif word in RESERVED:
            refuse(Refusal("RESERVED_WORD", line, word, f"line {line}: '{word}' is one of VE's structure words and "
                           "cannot be a property word."))
        elif word in d.kinds:
            refuse(Refusal("WORD_IS_KIND", line, word, f"line {line}: '{word}' is used both as a kind of thing and "
                           "as a property; use a different word for one of them."))
        elif word in names_lower:
            refuse(Refusal("WORD_IS_NAME", line, word, f"line {line}: '{word}' is both a name "
                           f"({names_lower[word]}) and a property word; rename one of them."))
    for noun in list(d.kinds):
        if "-" in noun or "'" in noun or noun in RESERVED:
            refuse(Refusal("RESERVED_WORD" if noun in RESERVED else "HYPHEN", noun_uses[noun].line, noun,
                           f"line {noun_uses[noun].line}: '{noun}' cannot be read as a kind of thing (a hyphen, "
                           "apostrophe or structure word)."))
        elif noun in names_lower:
            refuse(Refusal("WORD_IS_NAME", noun_uses[noun].line, noun, f"line {noun_uses[noun].line}: '{noun}' is "
                           f"both a name ({names_lower[noun]}) and a kind of thing; rename one of them."))
    # un-/non- next to its base: VE would not read "unpaid" as "not paid"; the fix writes "not".
    for word in list(d.properties):
        for prefix in ("un", "non"):
            base = word[len(prefix):]
            if word.startswith(prefix) and base in d.properties:
                for s in d.sentences:
                    if s.shape in ("rule", "fact") and re.search(rf"\bis (not )?{word}\b", s.text):
                        fixed = re.sub(rf"\bis (not )?{word}\b", lambda m: f"is {base}" if m.group(1) else
                                       f"is not {base}", s.text)
                        refuse(Refusal("NEGATED_PAIR", s.line, word,
                                       f"{s.where}: '{word}' is used next to '{base}'; VE does not read '{word}' as "
                                       f"'not {base}' (it would be a separate word). Write 'not {base}'.",
                                       fixed, s.line))
                    elif s.shape == "question" and s.groups[1] == word:
                        refuse(Refusal("NEGATED_PAIR", s.line, word,
                                       f"{s.where}: '{word}' is asked next to '{base}'; a question cannot say 'not'. "
                                       f"Ask 'Is {s.groups[0]} {base}?' instead.", f"Is {s.groups[0]} {base}?",
                                       s.line))
    d.statements = [s for s in d.sentences if s.shape in ("rule", "fact")]
    d.questions = [s for s in d.sentences if s.shape == "question"]
    if not d.refusals and not d.statements:
        refuse(Refusal("NO_STATEMENT", 0, "", "the text has no rule or fact line to read."))
    if not d.refusals:
        d.raw = document(d)
        lint = _wording_lint(d)
        for word, problem in lint:
            line = d.properties[word]["lines"][0]
            refuse(Refusal("WORDING_REFUSED", line, word, f"line {line}: VE's wording check does not accept "
                           f"'{word}' as a property word here ({problem})."))
        if lint:
            d.raw = None
    d.refusals.sort(key=lambda r: (r.line, r.code, r.word))
    return d


def environment(d: Derived) -> dict:
    """The derived environment: one sort per kind, one unary predicate per property word, one constant per name.
    Descriptions name the word and the word list with its digest, and no gloss: no sense the writer did not choose
    enters the identity."""
    from .profiles import BASE, LANGUAGE, SPEC_REVISION
    from .lexicon import VERSION
    source = f"{VERSION} sha256:{lexicon_digest()[:16]}"

    def origin(kind, word, declared):
        return (f"{kind} '{word}' declared in the text (line {declared})" if declared else
                f"{kind} '{word}' read from {source}")

    sorts = {noun: {"description": origin("noun", noun, row["declared"]),
                    "verbalisation": {"singular": noun, "plural": plural(noun)}} for noun, row in sorted(d.kinds.items())}
    predicates = {word: {"arguments": [row["kind"]], "description": origin("word", word, row["declared"]),
                         "verbalisation": "{0} is " + word, "negative_verbalisation": "{0} is not " + word}
                  for word, row in sorted(d.properties.items())}
    constants = {name.lower(): {"sort": row["kind"], "description": name} for name, row in sorted(d.names.items())}
    return {"language": LANGUAGE, "profiles": ["documents@1", BASE], "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": sorts, "predicates": predicates, "constants": constants}}


def document(d: Derived) -> bytes:
    """The ve-document@1 Lean reads: the rule and fact sentences as the source, one fence and one CHECKED unit each."""
    source = "".join(s.text + "\n" for s in d.statements)
    units, offset = [], 0
    for i, s in enumerate(d.statements, 1):
        end = offset + len((s.text + "\n").encode("utf-8"))
        units.append({"id": f"u{i}", "span": [offset, end], "status": "CHECKED", "kind": "asserted",
                      "meaning": "specified", "support": "none", "surface": "english", "content": {"fence": f"u{i}"}})
        offset = end
    meta = {"format": "ve-document@1", "environment": environment(d), "units": units}
    fences = "".join(f"```ve u{i}\n{s.text}\n```\n" for i, s in enumerate(d.statements, 1))
    return ("---\n" + json.dumps(meta, indent=1, sort_keys=True) + "\n---\n" + source + fences).encode("utf-8")


def _wording_lint(d: Derived) -> list:
    """VE's own English wording check over the derived vocabulary: each property word must keep its plain wording
    and its negative; anything it would replace or drop is refused by name (english.py's lint, 276-399)."""
    from .english import EnglishVocabulary
    from .environment import Environment
    try:
        words = EnglishVocabulary(Environment(environment(d)))
    except VEError as exc:
        return [(next(iter(sorted(d.properties)), ""), str(exc))]
    out = []
    for word in sorted(d.properties):
        if words.predicates.get(word) != "{0} is " + word:
            out.append((word, f"it would be shown as {words.predicates.get(word)!r}"))
        elif words.negatives.get(word) != "{0} is not " + word:
            out.append((word, "its negative 'is not' wording is not accepted"))
    return out


def vocabulary_lines(d: Derived) -> list:
    """'I read these words as: ...', one line per word: shown before any answer, every time."""
    out = ["I read these words as:"]
    for noun, row in sorted(d.kinds.items()):
        how = (f"declared in the text, line {row['declared']}" if row["declared"] else
               f"noun; {row['senses']} sense{'s' if row['senses'] != 1 else ''} in the list")
        out.append(f"  {noun}: a kind of thing ({how})")
    for word, row in sorted(d.properties.items()):
        if row["declared"]:
            how = f"declared in the text, line {row['declared']}"
        else:
            classes = []
            if "adjective" in row["classes"]:
                classes.append("adjective")
            if row["lemmas"]:
                classes.append("participle of " + "/".join(row["lemmas"]))
            how = " or ".join(classes)
            if row["senses"] > 1:
                how += (f"; {row['senses']} senses in the list: this text reads it with ONE meaning throughout, "
                        "check every use means the same")
            else:
                how += "; 1 sense in the list"
        out.append(f"  {word}: a property of {plural(row['kind'])} ({how})")
    for name, row in sorted(d.names.items()):
        out.append(f"  {name}: {'an' if row['kind'][0] in 'aeiou' else 'a'} {row['kind']} (line {row['line']})")
    return out


def refusal_lines(d: Derived) -> list:
    out = [f"Not read: {len(d.refusals)} problem{'s' if len(d.refusals) != 1 else ''}; nothing is answered."]
    for r in d.refusals:
        out.append("- " + r.message)
        if r.fix:
            out.append(("  Fix (replace line %d with): " % r.replaces if r.replaces else "  Fix (add this line): ")
                       + r.fix)
    return out


_LEADS = {"yes": "Yes", "no": "No", "notSettled": "not determined", "notNecessarily": "not determined",
          "unknown": "no answer"}


def _locate(path: Path, d: Derived, check) -> list:
    """The statement lines Lean refuses on their own (each in a one-sentence document), for a refusal that names them."""
    bad = []
    for s in d.statements:
        one = Derived(kinds=d.kinds, properties=d.properties, names=d.names, statements=[s])
        one_path = path.with_name("one-" + path.name)
        one_path.write_bytes(document(one))
        try:
            check(one_path)
        except (VEError, CheckerUnavailable, ResourceLimit) as exc:
            bad.append((s, str(exc)))
    return bad


def read(path, text: str, scratch: Path | None = None) -> dict:
    """Derive, have Lean check the document (every byte CHECKED), then ask Lean each question. Returns the result.
    `scratch`: an empty directory for the derived document (default: a temporary one, removed after)."""
    d = derive(text)
    result = {"format": FORMAT, "vocabulary": vocabulary_lines(d)[1:], "refusals": [r.as_dict() for r in d.refusals],
              "lexicon": {"version": "oewn-2025", "sha256": lexicon_digest()}}
    if d.refusals:
        return {**result, "status": "refused", "text": refusal_lines(d)}
    # Lean reads the derived document as a file of its own, in an empty directory (nothing beside it is read).
    name = (Path(path).name.split(".")[0] or "text") + ".derived.ve.md"
    if scratch is not None:
        derived = Path(scratch) / name
        derived.write_bytes(d.raw)
        return _lean_read(derived, d, result)
    with tempfile.TemporaryDirectory(prefix="ve-read-") as directory:
        derived = Path(directory) / name
        derived.write_bytes(d.raw)
        return _lean_read(derived, d, result)


def _lean_read(path: Path, d: Derived, result: dict) -> dict:
    from .ask import answer
    from .document.report import check_document
    try:
        checked = check_document(path)
    except VEError as exc:
        bad = _locate(path, d, check_document)
        rows = [Refusal("LEAN_REFUSED", s.line, "", f"{s.where}: Lean does not read \"{s.text}\": {msg}")
                for s, msg in bad] or [Refusal("LEAN_REFUSED", 0, "", f"Lean does not read the text: {exc}")]
        d.refusals.extend(rows)
        return {**result, "status": "refused", "refusals": [r.as_dict() for r in d.refusals],
                "text": refusal_lines(d)}
    coverage = checked.get("coverage") or {}
    total = coverage.get("source_bytes")
    complete = (coverage.get("coverage_percent") == 100 and total == len("".join(s.text + "\n" for s in d.statements)
                                                                         .encode("utf-8"))
                and coverage.get("bytes_by_status") == {"CHECKED": total} and coverage.get("accounted_bytes") == total)
    result["coverage"] = coverage
    result["document_id"] = checked.get("document_id")
    if not complete:
        d.refusals.append(Refusal("NOT_ALL_CHECKED", 0, "", "Lean's coverage table does not show every sentence "
                                  f"CHECKED: {json.dumps(coverage.get('bytes_by_status'))}"))
        return {**result, "status": "refused", "refusals": [r.as_dict() for r in d.refusals],
                "text": refusal_lines(d)}
    lines = vocabulary_lines(d)
    lines.append(f"Lean read every sentence: {len(d.statements)} of {len(d.statements)} CHECKED "
                 f"({total} of {total} bytes, 100%).")
    for i, s in enumerate(d.statements, 1):
        lines.append(f"  Sentence {i} ({s.where}): \"{s.text}\" CHECKED")
    answers = []
    for q in d.questions:
        lines.append(f"Question ({q.where}): {q.text}")
        try:
            got = answer(path, d.raw, q.text)
            lead = got.get("lead")
            said = got["text"] if got.get("status") == "answered" else [str(got.get("text"))]
            answers.append({"line": q.line, "question": q.text, "lead": lead, "answer": _LEADS.get(lead, "no answer"),
                            "text": said})
            lines.extend("  " + x for x in said)
        except (VEError, CheckerUnavailable, ResourceLimit) as exc:
            answers.append({"line": q.line, "question": q.text, "lead": None, "answer": "no answer",
                            "text": [str(exc)]})
            lines.append(f"  Not answered: {exc}")
    if not d.questions:
        lines.append("The text has no question (a line 'Is <Name> <word>?').")
    return {**result, "status": "read", "answers": answers, "text": lines}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ve read",
        description="Read a plain text with no front matter: show the words VE read, have Lean check every sentence, "
                    "and answer each question line in it, in Lean's words. Anything unsure is refused by name.")
    parser.add_argument("text", help="a plain text file (no JSON front matter)")
    parser.add_argument("--json", action="store_true", help="print the whole result as JSON")
    options = parser.parse_args(argv)
    try:
        raw = Path(options.text).read_bytes()
        if len(raw) > MAX_TEXT_BYTES:
            raise ResourceLimit(f"ResourceLimit: {options.text!r} exceeds {MAX_TEXT_BYTES} bytes")
        if raw.startswith(b"---\n"):
            raise VEError("this file has front matter: it is a ve-document; ask it with `ve ask`")
        result = read(options.text, raw.decode("utf-8"))
    except CheckerUnavailable as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_UNAVAILABLE
    except ResourceLimit as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_LIMIT
    except (VEError, OSError, UnicodeError) as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_NOT_READ
    print(json.dumps(result, ensure_ascii=False, indent=2) if options.json else "\n".join(result["text"]))
    if result["status"] != "read":
        return EXIT_NOT_READ
    return EXIT_UNKNOWN if any(a["lead"] in (None, "unknown") for a in result["answers"]) else EXIT_READ
