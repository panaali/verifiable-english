# ve-layer: 4 (word meanings for `ve read`: untrusted Python that builds hidden documents and compares Lean's answers)
"""`ve read` with word meanings (word senses, version 1; row word-senses-v1, ruling 2026-11-27).

A word may carry more than one meaning in a text. This module decides nothing about meanings itself: it builds hidden
`ve read` documents (ve/plain_read.py), has Lean read and answer each one, and only compares Lean's answers.

Layer 1, a word on two kinds of thing: each (word, kind) is its own word with no link between them. Every sentence in
version 1 talks about one kind, so the text is read as one hidden document per kind, each in the writer's own wording.
Each such document also asks Lean one probe question (restating one of its facts), so Lean checks that the sentences
about every kind can all be true together; if Lean finds that one kind's sentences cannot (X3), or cannot check it
(X6), no question about any kind is answered. (One document for the whole text is not used: on main's Lean the
consistency check of such a whole text runs out (X6) where each kind's own check does not. That the whole text can be
true when each kind's sentences can rests on the kinds sharing no word, name or sentence: an untrusted step.)

Layer 2, a word used in more than one sentence on one kind: a meaning check raises the word or not.
  - With the writer's yes (stored in their settings, reversible; the editor's assist mode counts as that yes), the text
    is sent twice to the reader program the writer set; the word is raised if either run raises it (the trigger:
    ve/word_senses_prompt.txt; the reader answers JSON, one verdict per word). Without that yes nothing leaves the machine and
    the word list alone raises a word used more than once on one kind that has more than one meaning in the list.
  - For a raised word Lean answers every question twice: over the text as written (one meaning) and over a hidden
    text where each statement use of every raised word is its own word. Python compares the two checked answers:
    equal = the meaning does not matter, the answer stands; different = the question is asked (interactive) or
    answered both ways. A question on the raised word itself is answered once per statement use. A text whose
    sentences cannot all be true together with one meaning (Lean's reason X3), or whose consistency Lean could not
    check (X6), is not answered from the split text.
  - VE has no mode that merges a raised word silently.

Layer 3, the writer settles a meaning in plain English: "free (no charge)" after a use, "Here 'free' means not in
use." after the sentence it explains, or "In this text, free means no charge." for every bare use. Two glosses make
two words (each its own hidden word); one gloss for every use makes one word, which is not raised again.

Untrusted steps that affect an answer (tested only; none is in Lean), nine: the trigger; assigning each sentence its
kind; the per-kind documents and their probes (with the claim that consistent kinds make a consistent text); reading
the writer's glosses (layer 3); the hidden words; mapping Lean's lines back to the writer's words; rewriting a question
onto one use's or one meaning's hidden word; the X3/X6 rule (no split answer, and with a word on two kinds no answer at
all, when any kind's sentences are not known to be consistent); and the compare. A hidden word is the writer's word with a coined ending, declared with a
`Words:` line, so Lean reads it like any declared word, "is not" included.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from importlib.resources import files
import json
import os
from pathlib import Path
import re
import shlex
import sys

from . import plain_read as pr
from .backends.process_limits import run_text_program
from .errors import CheckerUnavailable, ResourceLimit, VEError

FORMAT = "ve-plain-read@2"   # ve-plain-read@1 (ve/plain_read.py) plus sentence numbers, both-ways answers, the
                             # meaning check and the questions for the writer
READER_RUNS = 2
READER_TIMEOUT_DEFAULT = 180.0   # seconds per reader run; VE_WORD_READER_TIMEOUT overrides it
VERDICTS = ("same", "differ", "unsure")
_HERE = re.compile(r"^Here '([a-z][a-z'-]*)' means (.+)\.$")
_DEFAULT = re.compile(r"^In this (?:text|document), '?([a-z][a-z'-]*)'? means (.+)\.$")
_GLOSSED = re.compile(r"\bis( not)? ([a-z][a-z'-]*) \(([^()]*)\)")
_GLOSSED_QUESTION = re.compile(r"^Is ([A-Z][a-z]+) ([a-z][a-z'-]*) \(([^()]*)\)\?$")
_GLOSS_OK = re.compile(r"^[a-z][a-z' -]*$")
_GLOSS_HEDGE = {"or", "if", "unless", "maybe", "perhaps", "sometimes", "either", "except", "possibly"}
_GLOSS_LOGIC = {"not", "no", "yes", "and", "or", "if", "true", "false"}
_PLAIN = {"Yes": "Yes", "No": "No", "not determined": "the text does not settle this",
          "no answer": "VE could not decide this", "cannot check": "VE cannot check that reading yet"}


def prompt() -> str:
    """The frozen reader prompt (hashed before the build; tests pin its sha256)."""
    return files("ve").joinpath("word_senses_prompt.txt").read_text(encoding="utf-8")


# --- the writer's yes: stored in their settings, reversible --------------------------------------------------------

CONSENT_QUESTION = (
    "VE can check whether a word you use in more than one sentence means the same thing each time. To do that it "
    "sends the sentences of the text you are reading, numbered, and the list of those words (nothing else: no file "
    "name, no other file) to the reader program you set{command}. That program may pass them to an AI service outside "
    "this computer. Without your yes VE sends nothing and uses its word list alone. You can take the yes back at any "
    "time with `ve read --reader-off`. Send texts this way from now on? Type yes to agree: ")


def settings_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "ve" / "settings.json"


def load_settings() -> dict:
    try:
        data = json.loads(settings_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_settings(data: dict) -> None:
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def consent_given(command: str | None) -> bool:
    """The writer's stored yes for exactly this reader program: a yes given for one program (or for none) never
    covers another."""
    row = load_settings().get("word_reader")
    return (bool(command) and isinstance(row, dict) and row.get("consent") is True
            and row.get("consent_command") == command)


def consent_withdrawn() -> bool:
    row = load_settings().get("word_reader")
    return isinstance(row, dict) and row.get("consent") is False


def give_consent(command: str | None, *, store: bool = False) -> None:
    """Store the yes for `command` (the program the writer was shown); `store`: also make it the stored program."""
    data = load_settings()
    row = data.get("word_reader") if isinstance(data.get("word_reader"), dict) else {}
    row["consent"] = True
    row["consent_command"] = command
    if store and command:
        row["command"] = command
    data["word_reader"] = row
    _save_settings(data)


def withdraw_consent() -> None:
    data = load_settings()
    row = data.get("word_reader") if isinstance(data.get("word_reader"), dict) else {}
    row["consent"] = False
    row.pop("consent_command", None)
    data["word_reader"] = row
    _save_settings(data)


def reader_command() -> str | None:
    command = os.environ.get("VE_WORD_READER")
    if command:
        return command
    row = load_settings().get("word_reader")
    return row.get("command") if isinstance(row, dict) and isinstance(row.get("command"), str) else None


def command_reader(command: str):
    """The reader program as a function: input text -> its standard output, or None (failed, timed out)."""
    def run(text: str) -> str | None:
        try:
            argv = shlex.split(command)
        except ValueError:
            return None
        return run_text_program(argv, text, timeout=reader_timeout()) if argv else None
    return run


def reader_timeout() -> float:
    """Seconds one reader run may take: VE_WORD_READER_TIMEOUT if it is a positive number, else the default."""
    try:
        seconds = float(os.environ.get("VE_WORD_READER_TIMEOUT", ""))
    except ValueError:
        return READER_TIMEOUT_DEFAULT
    return seconds if seconds > 0 else READER_TIMEOUT_DEFAULT


# --- the text: sentences, glosses, uses ----------------------------------------------------------------------------

@dataclass
class Piece:
    """One sentence of the text as written: its number (1-based over the whole text), line, and cleaned form."""
    number: int
    line: int
    text: str
    clean: str | None          # the sentence with its glosses removed (None: a gloss sentence, not read as a shape)
    glosses: dict = field(default_factory=dict)  # word -> gloss given in brackets in this sentence


@dataclass
class Use:
    number: int                # the sentence number
    word: str
    kind: str
    statement: bool            # a rule or fact (False: a question)
    gloss: str | None = None


def normal_gloss(gloss: str) -> str | None:
    """The gloss as plain words for one meaning, or None: not letters, too long, hedged ("or not", "if late", "maybe
    busy") or made only of logical words ("not", "yes")."""
    g = " ".join(gloss.strip().lower().split())
    if g.startswith("meaning "):
        g = g[len("meaning "):]
    words = set(g.split())
    if not g or not _GLOSS_OK.match(g) or len(g.split()) > 6 or words & _GLOSS_HEDGE or words <= _GLOSS_LOGIC:
        return None
    return g


def pieces(text: str) -> tuple[list, list]:
    """The text's sentences (numbered as the reader and the writer see them) and the refusals of unreadable glosses."""
    out, refusals, number = [], [], 0
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        for piece in [p for p in re.split(r"(?<=[.?])\s+", stripped) if p]:
            number += 1
            if _HERE.match(piece) or _DEFAULT.match(piece):
                out.append(Piece(number, line_no, piece, None))
                continue
            glosses = {}
            question = _GLOSSED_QUESTION.match(piece)
            for m in [question] if question else _GLOSSED.finditer(piece):
                g = normal_gloss(m.group(3))
                if g is None:
                    refusals.append(pr.Refusal("GLOSS_UNREAD", line_no, m.group(2),
                                               f"sentence {number}: VE reads the meaning in brackets after "
                                               f"'{m.group(2)}' as a few plain words for one meaning (letters only; no "
                                               f"'or', 'if', 'unless' or 'maybe'), as in "
                                               f"\"{m.group(2)} (no charge)\"; it does not read \"({m.group(3)})\"."))
                elif glosses.get(m.group(2), g) != g:
                    refusals.append(pr.Refusal("GLOSS_UNREAD", line_no, m.group(2),
                                               f"sentence {number} gives '{m.group(2)}' two meanings; give it one."))
                else:
                    glosses[m.group(2)] = g
            clean = (f"Is {question.group(1)} {question.group(2)}?" if question else
                     _GLOSSED.sub(lambda m: f"is{m.group(1) or ''} {m.group(2)}", piece))
            out.append(Piece(number, line_no, piece, clean, glosses))
    return out, refusals


def clean_text(ps: list, keep=lambda p: True) -> str:
    """The text with gloss sentences and brackets removed (and only the kept sentences), on its original lines."""
    lines = {}
    for p in ps:
        if p.clean is not None and keep(p):
            lines.setdefault(p.line, []).append(p.clean)
    last = max((p.line for p in ps), default=0)
    return "".join(" ".join(lines.get(n, [])) + "\n" for n in range(1, last + 1))


def _classified(ps: list) -> dict:
    """Each read sentence's shape and groups (plain_read's own classifier), by sentence number."""
    out = {}
    for p in ps:
        if p.clean is None:
            continue
        s = pr.split_text(p.clean)
        out[p.number] = s[0] if len(s) == 1 else None
    return out


def _kind_of(s, names: dict) -> str | None:
    if s is None or s.shape is None:
        return None
    if s.shape == "rule":
        return s.groups[0]
    if s.shape == "kind":
        return s.groups[2]
    if s.shape in ("fact", "question"):
        return names.get(s.groups[0])
    if s.shape == "words-property":
        return s.groups[1]
    if s.shape == "words-kind":
        return s.groups[0]
    return None


def _words_in(s) -> list:
    if s.shape == "rule":
        return [w for w in (s.groups[3], s.groups[5], s.groups[7]) if w]
    if s.shape in ("fact", "question"):
        return [s.groups[-1]]
    return []


def uses_of(ps: list, shapes: dict, names: dict) -> list:
    """Every property-word use: (sentence, word, kind, statement?, gloss). A sentence's gloss sentences apply: a
    "Here 'w' means g." to the sentence before it; "In this text, w means g." to every bare use of w."""
    here, default = {}, {}
    previous = None
    for p in ps:
        if p.clean is None:
            m = _HERE.match(p.text)
            if m and previous is not None:
                here[(previous, m.group(1))] = normal_gloss(m.group(2))
            m = _DEFAULT.match(p.text)
            if m:
                default[m.group(1)] = normal_gloss(m.group(2))
            continue
        previous = p.number
    out = []
    for p in ps:
        s = shapes.get(p.number)
        if s is None or s.shape not in ("rule", "fact", "question"):
            continue
        kind = _kind_of(s, names)
        if kind is None:
            continue
        for w in dict.fromkeys(_words_in(s)):
            g = p.glosses.get(w) or here.get((p.number, w)) or default.get(w)
            out.append(Use(p.number, w, kind, s.shape != "question", g))
    return out


def gloss_refusals(ps: list, shapes: dict) -> list:
    """A "Here" sentence must follow a sentence that uses its word; a gloss must be plain words; a word is given at
    most one meaning for the whole text, and at most one in each sentence (brackets and "Here" agreeing)."""
    out, previous = [], None
    by_number = {p.number: p for p in ps}
    defaults, heres = {}, {}
    for p in ps:
        if p.clean is None:
            m = _HERE.match(p.text) or _DEFAULT.match(p.text)
            word, g = m.group(1), normal_gloss(m.group(2))
            if g is None:
                out.append(pr.Refusal("GLOSS_UNREAD", p.line, word, f"sentence {p.number}: VE reads the meaning "
                                      f"as a few plain words for one meaning (letters only; no 'or', 'if', 'unless' "
                                      f"or 'maybe'); it does not read \"{m.group(2)}\"."))
            elif _HERE.match(p.text):
                s = shapes.get(previous) if previous else None
                if s is None or word not in _words_in(s):
                    out.append(pr.Refusal("GLOSS_UNREAD", p.line, word,
                                          f"sentence {p.number}: \"{p.text}\" explains the sentence just before it, "
                                          f"which does not use '{word}'. Put it right after the sentence it "
                                          "explains."))
                else:
                    inline = by_number[previous].glosses.get(word)
                    first = heres.setdefault((previous, word), g)
                    if first != g or (inline and inline != g):
                        out.append(pr.Refusal("GLOSS_UNREAD", p.line, word,
                                              f"sentence {p.number} gives '{word}' in sentence {previous} a second "
                                              f"meaning ('{inline if inline and inline != g else first}' and '{g}'); "
                                              "give it one."))
            elif defaults.setdefault(word, g) != g:
                out.append(pr.Refusal("GLOSS_UNREAD", p.line, word,
                                      f"sentence {p.number} gives '{word}' a second meaning for the whole text "
                                      f"('{defaults[word]}' and '{g}'); give one, or write the meaning in brackets "
                                      f"after each use of '{word}'."))
            continue
        previous = p.number
    return out


# --- words: groups, hidden words, the meaning check ----------------------------------------------------------------

@dataclass
class Word:
    """One (word, kind) of the text and how it is read."""
    word: str
    kind: str
    label: str
    uses: list
    glosses: list = field(default_factory=list)   # distinct glosses in order of first use
    settled: str = ""                              # "" / "one" (one gloss for every use) / "split" (two or more)
    senses: int = 0
    declared: bool = False
    check: dict = field(default_factory=dict)      # the meaning check: {"by": "reader"|"list", "runs": [...]}
    raised: bool = False

    @property
    def splits(self) -> bool:
        """Raised, and used in two or more statements: only then can splitting it change an answer."""
        return self.raised and len(self.statements) >= 2

    @property
    def sentences(self) -> list:
        return sorted({u.number for u in self.uses})

    @property
    def statements(self) -> list:
        return sorted({u.number for u in self.uses if u.statement})


def _count(n: int) -> str:
    return {2: "two", 3: "three", 4: "four", 5: "five"}.get(n, str(n))


def article(noun: str) -> str:
    return "an" if noun[:1] in "aeiou" else "a"


def words_of(uses: list) -> dict:
    kinds = {}
    for u in uses:
        kinds.setdefault(u.word, set()).add(u.kind)
    out = {}
    for u in uses:
        key = (u.word, u.kind)
        if key not in out:
            label = u.word if len(kinds[u.word]) == 1 else f"{u.word}, of {article(u.kind)} {u.kind}"
            out[key] = Word(u.word, u.kind, label, [])
        out[key].uses.append(u)
    for w in out.values():
        w.glosses = list(dict.fromkeys(u.gloss for u in w.uses if u.gloss))
        statements = [u for u in w.uses if u.statement]
        if w.glosses and statements and all(u.gloss for u in statements):
            # every statement use says its meaning: one gloss = one word, settled; two or more = that many words (a
            # bare question on such a word is answered once per meaning)
            w.settled = "one" if len(w.glosses) == 1 else "split"
    return out


def candidates(words: dict) -> list:
    """Words the meaning check looks at: used in two or more sentences on one kind, not settled by the writer."""
    return sorted((w for w in words.values() if len(w.sentences) >= 2 and not w.settled), key=lambda w: w.label)


def reader_input(ps: list, cands: list) -> str:
    numbered = "\n".join(f"{p.number}. {p.text}" for p in ps)
    listed = ", ".join(f'"{w.label}" (sentences {", ".join(map(str, w.sentences))})' for w in cands)
    return f"{prompt().rstrip(chr(10))}\n\nTEXT:\n{numbered}\n\nWORDS: {listed}"


def parse_reader(out: str | None, labels: list) -> dict:
    """The reader's verdict per label: same / differ / unsure, or missing (no usable answer counts as not same)."""
    verdicts = {label: "missing" for label in labels}
    if not out:
        return verdicts
    body = out.strip()
    lines = body.splitlines()
    if lines and lines[0].startswith("```"):
        body = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()
    try:
        data = json.loads(body)
    except ValueError:
        return verdicts
    if not isinstance(data, dict):
        return verdicts
    for label in labels:
        row = data.get(label)
        if isinstance(row, dict) and row.get("verdict") in VERDICTS:
            verdicts[label] = row["verdict"]
    return verdicts


def run_raises(verdict: str, word: Word) -> bool:
    many = word.declared or word.senses > 1
    return verdict == "differ" or (verdict != "same" and many)


def meaning_check(ps: list, cands: list, reader) -> None:
    """Set each candidate's check and raised flag. `reader`: None (word list alone) or input -> output."""
    if not cands:
        return
    if reader is None:
        for w in cands:
            w.check = {"by": "list"}
            w.raised = w.senses > 1
        return
    text = reader_input(ps, cands)
    labels = [w.label for w in cands]
    runs = [parse_reader(reader(text), labels) for _ in range(READER_RUNS)]
    for w in cands:
        verdicts = [r[w.label] for r in runs]
        w.check = {"by": "reader", "runs": verdicts}
        w.raised = any(run_raises(v, w) for v in verdicts)


# --- hidden documents ----------------------------------------------------------------------------------------------

def coined(word: str, taken: set, n: int) -> str:
    """A plain hidden word for one meaning of `word`: the word with a coined ending no text word or list word has."""
    from .lexicon import analyses
    letters = "abcdefghijklmnopqrstuvwxyz"
    i = n
    while True:
        tag = "zq" + letters[i % 26] + (letters[i // 26 - 1] if i >= 26 else "")
        token = word + tag
        if token not in taken and not analyses(token):
            taken.add(token)
            return token
        i += 26


def _rename(sentence: str, word: str, token: str) -> str:
    return re.sub(rf"(?<=\bis ){re.escape(word)}\b|(?<=\bis not ){re.escape(word)}\b", token, sentence)


@dataclass
class Hidden:
    """One hidden document: its text (statements on their original lines, then declarations, then questions) and,
    for each question line, which writer question it stands for and how."""
    text: str
    asks: list            # [(question number, branch key)] in the order of the question lines
    tokens: dict          # hidden word -> (word, how it is shown)
    asked: dict = field(default_factory=dict)  # question number -> the writer's word it asks about


def hidden(ps: list, shapes: dict, kind_of: dict, kind, words: dict, split: set, taken: set,
           probe: bool = False) -> Hidden:
    """The hidden document for one kind (None: the whole text): settled glosses as their own words; `split`: the
    (word, kind) keys whose every statement use is its own word; `probe`: also ask one question that makes Lean check
    that the document's sentences can all be true together (its ask is (0, ("probe",)))."""
    rename = {}   # (sentence number, word) -> token
    tokens = {}
    declare = []  # (token, its Words: line)
    by_gloss = {}  # (word, kind, gloss) -> token
    for (word, k), w in sorted(words.items()):
        if kind is not None and k != kind:
            continue
        if (word, k) in split and len(w.statements) >= 2:
            for i, number in enumerate(w.statements):
                token = coined(word, taken, i)
                rename[(number, word)] = token
                tokens[token] = (word, f"{word} (as in sentence {number})")
                declare.append((token, f"Words: {token} (property of {k})"))
        elif w.settled == "split":
            for i, g in enumerate(w.glosses):
                token = coined(word, taken, i)
                by_gloss[(word, k, g)] = token
                tokens[token] = (word, f"{word} ({g})")
                declare.append((token, f"Words: {token} (property of {k})"))
            for u in w.uses:
                if u.gloss:
                    rename[(u.number, word)] = by_gloss[(word, k, u.gloss)]
    lines = {}
    questions = []
    for p in ps:
        s = shapes.get(p.number)
        if p.clean is None or (kind is not None and kind_of.get(p.number) != kind):
            continue
        if s is not None and s.shape == "question":
            questions.append((p, s))
            continue
        text = p.clean
        for word in _words_in(s) if s is not None else []:
            if (p.number, word) in rename:
                text = _rename(text, word, rename[(p.number, word)])
        lines.setdefault(p.line, []).append(text)
    last = max((p.line for p in ps), default=0)
    body = [" ".join(lines.get(n, [])) for n in range(1, last + 1)]
    asks, asked, qlines = [], {}, []
    for p, s in questions:
        name, word = s.groups
        asked[p.number] = word
        k = kind_of.get(p.number)
        w = words.get((word, k))
        if w is not None and (word, w.kind) in split and len(w.statements) >= 2:
            for number in w.statements:
                qlines.append(f"Is {name} {rename[(number, word)]}?")
                asks.append((p.number, ("use", number)))
        elif w is not None and w.settled == "split" and not p.glosses.get(word) and not _glossed_question(ps, p, w):
            for g in w.glosses:
                qlines.append(f"Is {name} {by_gloss[(word, k, g)]}?")
                asks.append((p.number, ("meaning", g)))
        elif w is not None and w.settled == "split":
            g = p.glosses.get(word) or _glossed_question(ps, p, w)
            qlines.append(f"Is {name} {by_gloss[(word, k, g)]}?")
            asks.append((p.number, ("plain",)))
        else:
            qlines.append(f"Is {name} {rename[(p.number, word)]}?" if (p.number, word) in rename else p.clean)
            asks.append((p.number, ("plain",)))
    if probe and kind is not None:
        line = _probe(body, ps, shapes, kind_of, kind, words)
        if line:
            qlines.append(line)
            asks.append((0, ("probe",)))
    used = set(re.findall(r"[a-z][a-z'-]*", "\n".join(body + qlines)))
    body += [line for token, line in declare if token in used] + qlines
    return Hidden("".join(x + "\n" for x in body), asks, tokens, asked)


def _probe(body: list, ps: list, shapes: dict, kind_of: dict, kind: str, words: dict) -> str | None:
    """A question Lean can prove from one fact of this kind ("Pass is used." -> "Is Pass used?"): proving it makes Lean
    check that the sentences can all be true together. With no fact, a question on a name of this kind (if they
    cannot all be true, Lean proves anything). None: the kind has no name, and its rules alone constrain nothing."""
    for line in body:
        for sentence in re.split(r"(?<=[.?])\s+", line):
            m = pr.FACT.match(sentence)
            if m:
                return f"Is {m.group(1)} {m.group(3)}?"
    names = [s.groups[0] for n, s in shapes.items() if s is not None and s.shape == "kind" and kind_of.get(n) == kind]
    props = sorted(word for word, k in words if k == kind)
    return f"Is {names[0]} {props[0]}?" if names and props else None


def _glossed_question(ps, p, w) -> str | None:
    u = next((u for u in w.uses if u.number == p.number), None)
    return u.gloss if u else None


def _shown(lines: list, tokens: dict) -> list:
    """Lean's lines with each hidden word put back as the writer's word and the meaning it stands for."""
    if not tokens:
        return list(lines)
    pattern = re.compile(r"\b(" + "|".join(sorted(map(re.escape, tokens), key=len, reverse=True)) + r")\b")
    return [pattern.sub(lambda m: tokens[m.group(1)][1], x) for x in lines]


def _shown_refusal(r, tokens: dict):
    """A refusal from a hidden document, with each hidden word put back as the writer's word."""
    if not tokens:
        return r
    shown = lambda x: _shown([x], tokens)[0] if isinstance(x, str) else x
    return pr.Refusal(r.code, r.line, shown(r.word), shown(r.message), shown(r.fix), shown(r.replaces))


def _lean(hid: Hidden, name: str, scratch: Path | None) -> dict:
    """Lean's read of one hidden document (ve/plain_read.read: every byte CHECKED before any answer)."""
    return pr.read(name, hid.text, scratch)


# --- reading -------------------------------------------------------------------------------------------------------

def _not_read(result: dict, refusals: list) -> dict:
    d = pr.Derived(refusals=sorted(refusals, key=lambda r: (r.line, r.code, r.word)))
    return {**result, "status": "refused", "refusals": [r.as_dict() for r in d.refusals],
            "text": pr.refusal_lines(d)}


def _which(numbers: list) -> str:
    n = [str(x) for x in numbers]
    if len(n) == 1:
        return f"sentence {n[0]}"
    return "sentences " + ", ".join(n[:-1]) + " and " + n[-1]


_ONE_MEANING = ": this text reads it with ONE meaning throughout, check every use means the same"


def vocabulary(words: dict, derived: list, ps: list) -> list:
    """'I read these words as: ...': plain_read's lines for each hidden document (hidden words left out; its "ONE
    meaning" clause left out for a word this module checks or the writer settled), then each word read as two words,
    and each word the meaning check looked at, in plain English."""
    out = ["I read these words as:"]
    seen = set()
    checked = {w.word for w in words.values() if w.check or w.settled}
    for d in derived:
        for line in pr.vocabulary_lines(d)[1:]:
            m = re.match(r"^  ([a-z][a-z'-]*): ", line)
            if m and m.group(1) in checked:
                line = line.replace(_ONE_MEANING, "")
            if line not in seen and not re.match(r"^  [a-z'-]+zq[a-z]+: ", line):
                seen.add(line)
                out.append(line)
    by_word = {}
    for w in words.values():
        by_word.setdefault(w.word, []).append(w)
    for word, ws in sorted(by_word.items()):
        if len(ws) > 1:
            parts = " / ".join(f"{word}, of {article(w.kind)} {w.kind} ({_which(w.sentences)})" for w in ws)
            out.append(f"  {parts}: read as {_count(len(ws))} separate words")
        for w in ws:
            name = w.label
            if w.settled == "split":
                parts = " / ".join(f"{name} ({g}) ({_which(sorted({u.number for u in w.uses if u.gloss == g}))})"
                                   for g in w.glosses)
                out.append(f"  {parts}: read as {_count(len(w.glosses))} separate words, as you wrote")
            elif w.settled == "one":
                out.append(f"  {name} ({w.glosses[0]}) ({_which(w.sentences)}): read as one meaning, as you wrote")
            elif w.glosses:
                given = sorted({u.number for u in w.uses if u.gloss})
                out.append(f"  {name}: the meaning in brackets in {_which(given)} ('{w.glosses[0]}') is not used: VE "
                           f"reads a meaning only when every rule and fact using '{word}' says it (or write \"In this "
                           f"text, {word} means {w.glosses[0]}.\")")
            if w.check and not w.settled:
                many = ("not in the word list" if w.declared and not w.senses else
                        f"{w.senses} meaning{'s' if w.senses != 1 else ''} in the word list")
                if w.check["by"] == "reader":
                    said = " and ".join(dict.fromkeys(w.check["runs"]))
                    how = f"meaning check: the reader said {said.replace('missing', 'nothing usable')}; {many}"
                else:
                    how = f"meaning check: word list alone; {many}"
                if w.splits:
                    out.append(f"  {name} ({_which(w.sentences)}): may mean different things ({how}); VE checks "
                               "whether that changes an answer, and asks or answers both ways where it does")
                elif w.raised:
                    out.append(f"  {name} ({_which(w.sentences)}): may mean different things ({how}); "
                               + (f"only {_which(w.statements)} states it, so a question on it is read in the "
                                  f"meaning of {_which(w.statements)}" if w.statements else
                                  "no rule or fact states it"))
                else:
                    out.append(f"  {name} ({_which(w.sentences)}): read as ONE meaning ({how})")
    return out


def read(path, text: str, *, reader=None, scratch: Path | None = None) -> dict:
    """Read a plain text: words on two kinds and glossed words as separate words, the meaning check on the rest,
    Lean's answers over the hidden documents compared. `reader`: None (word list alone; nothing leaves the machine)
    or a function from the reader input to its output (called only after the writer's yes)."""
    ps, refusals = pieces(text)
    shapes = _classified(ps)
    refusals += gloss_refusals(ps, shapes)
    whole = pr.derive(clean_text(ps))
    result = {"format": FORMAT, "lexicon": {"version": "oewn-2025", "sha256": pr.lexicon_digest()},
              "meaning_check": "reader" if reader is not None else "word list"}
    refusals += [r for r in whole.refusals if r.code != "WORD_TWO_KINDS"]
    if refusals:
        return _not_read({**result, "vocabulary": []}, refusals)
    names = {n: row["kind"] for n, row in whole.names.items()}
    kind_of = {n: _kind_of(s, names) for n, s in shapes.items()}
    uses = uses_of(ps, shapes, names)
    words = words_of(uses)
    for w in words.values():
        bare = [u.number for u in w.uses if u.statement and not u.gloss]
        if len(w.glosses) > 1 and bare:
            shown = "; ".join(f"'{g}' ({_which(sorted({u.number for u in w.uses if u.gloss == g}))})"
                              for g in w.glosses)
            refusals.append(pr.Refusal("MEANING_NOT_SAID", min(p.line for p in ps if p.number == bare[0]), w.word,
                                       f"{_which(bare)} uses '{w.word}' without saying which meaning, and the text "
                                       f"gives it {len(w.glosses)}: {shown}. Write the meaning in brackets after "
                                       f"'{w.word}' there, for example \"{w.word} ({w.glosses[0]})\"."))
    if refusals:
        return _not_read({**result, "vocabulary": []}, refusals)
    two_kinds = len({w.word for w in words.values()}) < len(words)
    kinds = sorted({k for k in kind_of.values() if k}) if two_kinds else [None]
    taken = {w.word for w in words.values()} | {u for u in re.findall(r"[a-z][a-z'-]*", text.lower())}
    merged = {k: hidden(ps, shapes, kind_of, k, words, set(), set(taken), probe=two_kinds) for k in kinds}
    derived = {k: pr.derive(h.text) for k, h in merged.items()}
    problems = [_shown_refusal(r, merged[k].tokens) for k, d in derived.items() for r in d.refusals]
    if problems:
        return _not_read({**result, "vocabulary": []}, problems)
    for (word, k), w in words.items():
        row = derived[k if two_kinds else None].properties.get(word)
        if row is not None:
            w.senses, w.declared = row["senses"], bool(row["declared"])
    cands = candidates(words)
    meaning_check(ps, cands, reader)
    result["reader_runs"] = READER_RUNS if reader is not None and cands else 0
    result["vocabulary"] = vocabulary(words, list(derived.values()), ps)[1:]
    lines = ["I read these words as:", *result["vocabulary"]]
    answers = {}
    stem = (Path(path).name.split(".")[0] or "text")
    firsts = {}
    for k in kinds:
        first = _lean(merged[k], f"{stem}-{k}" if k else stem, scratch)
        if first["status"] != "read":
            return _not_read(result, [_shown_refusal(pr.Refusal(r["code"], r["line"], r["word"], r["message"],
                                                                r.get("fix"), r.get("replaces")), merged[k].tokens)
                                      for r in first["refusals"]])
        firsts[k] = first
    # X3: the sentences cannot all be true together; X6: Lean could not check that they can. Either way the text as
    # written is not known to be consistent: VE never answers from the split text, and with a word on two kinds it
    # answers nothing about any kind (each kind's document, probe included, is one part of the text).
    unsure = {k: sorted({"X3", "X6"} & {r for a in f["answers"] for r in (a.get("reasons") or ())})
              for k, f in firsts.items()}
    unsure = {k: v for k, v in unsure.items() if v}
    coverage, checked_lines = [], []
    for k in kinds:
        first = firsts[k]
        coverage.append(first.get("coverage"))
        head = first["text"][:next((i for i, x in enumerate(first["text"]) if x.startswith("Question (")),
                                   len(first["text"]))]
        checked = [x for x in head if x.startswith(("Lean read every sentence", "  Sentence "))]
        if k is not None:
            checked = [f"Sentences about {pr.plural(k)}:"] + ["  " + x for x in checked]
        checked_lines.extend(_shown(checked, merged[k].tokens))
        raised_words = [w for key, w in sorted(words.items()) if w.splits and (k is None or w.kind == k)]
        second, second_doc = None, None
        if raised_words and not unsure:
            second_doc = hidden(ps, shapes, kind_of, k, words, {(w.word, w.kind) for w in raised_words}, set(taken),
                                probe=two_kinds)
            second = _lean(second_doc, f"{stem}-{k}-split" if k else f"{stem}-split", scratch)
        _compare(answers, merged[k], first, second, second_doc, raised_words, bool(unsure))
    if two_kinds and unsure:
        for number, a in answers.items():
            k = kind_of.get(number)
            if k in unsure or ("X3" not in {r for v in unsure.values() for r in v} and a["answer"] == "not determined"):
                continue
            bad = sorted(unsure)
            why = "; ".join((f"the sentences about {pr.plural(x)} cannot all be true together, so the whole text "
                             "cannot either") if "X3" in unsure[x] else
                            f"VE could not check that the sentences about {pr.plural(x)} can all be true together"
                            for x in bad)
            answers[number] = {"lead": "unknown", "answer": "no answer",
                               "reasons": sorted({r for x in bad for r in unsure[x]}),
                               "text": [f"VE does not answer this: {why}."]}
    lines.extend(checked_lines)
    numbers = {p.number: p for p in ps}
    out_answers = []
    if any(a.get("both_ways") for a in answers.values()):
        lines.append("(VE's sentence numbers count every sentence of your text in order, questions included.)")
    for number in sorted(answers):
        a = answers[number]
        p = numbers[number]
        a = {"line": p.line, "sentence": number, "question": p.text, **a}
        out_answers.append(a)
        where = next((x.where for x in pr.split_text(clean_text([p])) if x.shape == "question"), f"line {p.line}")
        lines.append(f"Question ({where}): {p.text}")
        lines.extend("  " + x for x in a["text"])
    if not answers:
        lines.append("The text has no question (a line 'Is <Name> <word>?').")
    asks = _questions_for_writer(out_answers, words)
    return {**result, "status": "read", "answers": out_answers, "questions_for_writer": asks, "coverage": coverage,
            "text": lines}


def _branch_answers(read_result: dict, hid: Hidden) -> dict:
    """{question number: {branch: (answer, lean lines)}} from one hidden document's read. Lean's answers must be to
    the hidden document's own question lines, in order; anything else is not trusted."""
    lines = [x for x in hid.text.splitlines() if x.startswith("Is ")]
    got = read_result["answers"]
    if len(got) != len(hid.asks) or len(lines) != len(hid.asks) or any(
            a.get("question") != q for a, q in zip(got, lines)):
        raise CheckerUnavailable("CheckerUnavailable: Lean's answers do not match the hidden document's questions")
    out = {}
    for (number, branch), a in zip(hid.asks, got):
        out.setdefault(number, {})[branch] = (a["answer"], _shown(a["text"], hid.tokens), a.get("lead"))
    return out


def _compare(answers: dict, first_doc: Hidden, first: dict, second: dict | None, second_doc: Hidden | None,
             raised: list, inconsistent: bool, kind_of: dict | None = None) -> None:
    """Python's only part in "does the difference matter": compare Lean's answers, never reason about them.
    `kind_of` (texts with a word on two kinds): name only the raised words of the question's kind."""
    one = _branch_answers(first, first_doc)
    if second is None:
        two = {}
    elif second["status"] != "read":  # the split reading is not one Lean reads: never a plain answer
        two = {}
        for n, b in second_doc.asks:
            two.setdefault(n, {})[b] = ("cannot check", [], None)
    else:
        two = _branch_answers(second, second_doc)
    for number, branches in one.items():
        if number == 0:   # the consistency probe: its reasons count, its answer is not shown
            continue
        words = [w for w in raised if kind_of is None or w.kind == kind_of.get(number)] or list(raised)
        names = " and ".join(f"'{w.label}'" for w in words)
        where = "; ".join(f"{w.label}: {_which(w.statements)}" for w in words)
        each = (f"{'it means' if len(words) == 1 else 'each means'} the same in all "
                f"{'its' if len(words) == 1 else 'their'} sentences ({where})")
        note = []
        if inconsistent and words:
            note = ["(This reads " + "; ".join(f"'{w.label}' with one meaning in {_which(w.statements)}"
                                               for w in words) + ".)"]
        other = two.get(number)
        if ("plain",) not in branches:   # a question on a word the writer glossed two ways: one branch per meaning
            per = {b[1]: v[0] for b, v in branches.items()}
            split = {b[1]: v[0] for b, v in (other or {}).items() if b[0] == "meaning"}
            differs = [g for g in per if g in split and split[g] != per[g]]
            if len(set(per.values())) == 1 and not differs:
                same, said, lead = next(iter(branches.values()))
                answers[number] = {"lead": lead, "answer": same, "text": said + note}
                continue
            word = _word_of(first_doc, number)
            parts = [f"if '{word}' here means {g}: {_PLAIN[v]}" + (
                f" if {names} {'means' if len(words) == 1 else 'mean'} the same in all {'its' if len(words) == 1 else 'their'} "
                f"sentences ({where}), and {_PLAIN[split[g]]} if not" if g in differs else "") for g, v in per.items()]
            both = {"meanings": [{"meaning": g, "answer": v, **({"different": split[g]} if g in differs else {})}
                                 for g, v in per.items()]}
            if differs:
                both["words"] = [w.label for w in words]
            answers[number] = {"lead": None, "answer": "depends on meaning", "both_ways": both,
                               "text": ["Depends on which meaning is meant: " + "; ".join(parts) + "."] + note}
            continue
        same, said, lead = branches[("plain",)]
        if other is None:
            answers[number] = {"lead": lead, "answer": same, "text": said + note}
            continue
        if ("plain",) in other:
            split = other[("plain",)][0]
            if split == same:
                answers[number] = {"lead": lead, "answer": same, "text": said}
                continue
            text = [f"Depends on what {names} mean{'s' if len(words) == 1 else ''}. If {each}: {_PLAIN[same]}. "
                    f"If not: {_PLAIN[split]}."]
            answers[number] = {"lead": lead, "answer": "depends on meaning",
                               "both_ways": {"words": [w.label for w in words], "same": same, "different": split},
                               "text": text + ["If the meaning is the same, Lean's answer:"] + ["  " + x for x in said]}
        else:
            per = {b[1]: v[0] for b, v in other.items()}
            if all(v == same for v in per.values()):
                answers[number] = {"lead": lead, "answer": same, "text": said}
                continue
            word = _word_of(first_doc, number)
            others = [w.label for w in words if w.word != word]
            text = [f"Depends on what '{word}' means. If it means the same throughout: {_PLAIN[same]}. "
                    + "If '" + word + "' here means what it means in " + "; in ".join(
                        f"sentence {n}: {_PLAIN[v]}" for n, v in sorted(per.items())) + "."
                    + (f" In the readings by sentence, each use of {' and '.join(repr(x) for x in others)} is also "
                       "read as its own word." if others else "")]
            answers[number] = {"lead": lead, "answer": "depends on meaning",
                               "both_ways": {"words": [w.label for w in words], "same": same,
                                             "uses": [{"sentence": n, "answer": v} for n, v in sorted(per.items())]},
                               "text": text + ["If the meaning is the same, Lean's answer:"] + ["  " + x for x in said]}


def _word_of(doc: Hidden, number: int) -> str:
    return doc.asked[number]


def _questions_for_writer(answers: list, words: dict) -> list:
    """The plain questions VE asks the writer in interactive use: one per raised word whose meaning changes an
    answer ("In sentence 2 and sentence 4, does 'free' mean the same thing?")."""
    out = []
    for a in answers:
        for label in (a.get("both_ways") or {}).get("words", []):
            w = next(x for x in words.values() if x.label == label)
            q = f"In {_which(w.statements)}, does '{w.word}' mean the same thing{' each time' if len(w.statements) > 2 else ''}?"
            row = {"word": w.word, "kind": w.kind, "sentences": w.statements, "question": q}
            if row not in out:
                out.append(row)
    return out


# --- interactive use: the writer's reply goes into the text as plain English ---------------------------------------

def with_gloss(text: str, number: int, word: str, gloss: str) -> str:
    """The text with "(gloss)" written after `word` in sentence `number` (its line's other sentences kept)."""
    lines = text.splitlines()
    count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        parts = [x for x in re.split(r"(?<=[.?])\s+", stripped) if x]
        if count + len(parts) >= number:
            k = number - count - 1
            parts[k] = re.sub(rf"\bis( not)? {re.escape(word)}\b(?! \()", lambda m: f"is{m.group(1) or ''} {word} ({gloss})",
                              parts[k], count=1)
            lines[i] = " ".join(parts)
            break
        count += len(parts)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def settle(text: str, question: dict, same: bool, glosses) -> str:
    """Apply the writer's reply to one question: the same meaning (one gloss on every use) or a meaning per use."""
    for number in question["sentences"]:
        gloss = glosses if same else glosses[number]
        text = with_gloss(text, number, question["word"], gloss)
    return text


def reader_for(assist: bool = False):
    """The reader to use: only with a reader program set and the writer's stored yes for that very program (or the
    editor's assist mode, which counts as a yes unless the writer took the yes back); otherwise None, and nothing
    leaves the machine."""
    command = reader_command()
    if command and (consent_given(command) or (assist and not consent_withdrawn())):
        return command_reader(command)
    return None


def interactive(path: Path, text: str, reader, ask, scratch: Path | None = None) -> tuple[str, dict]:
    """Read, ask the writer one plain question per raised word whose meaning changes an answer, write each reply into
    the text as a gloss, and read again. `ask(prompt) -> reply`. Returns (the new text, the last result)."""
    result = read(path, text, reader=reader, scratch=scratch)
    for q in result.get("questions_for_writer", []):
        reply = ask(q["question"] + " (yes/no) ").strip().lower()
        if reply not in ("yes", "y", "no", "n"):
            continue
        if reply.startswith("y"):
            gloss = normal_gloss(ask(f"In a few words, what does '{q['word']}' mean there? "))
            if gloss:
                text = settle(text, q, True, gloss)
        else:
            glosses = {n: normal_gloss(ask(f"In a few words, what does '{q['word']}' mean in sentence {n}? "))
                       for n in q["sentences"]}
            if all(glosses.values()):
                text = settle(text, q, False, glosses)
    return text, read(path, text, reader=reader, scratch=scratch)


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ve read",
        description="Read a plain text with no front matter: show the words VE read, have Lean check every sentence, "
                    "and answer each question line in it, in Lean's words. Anything unsure is refused by name; where "
                    "a word's meaning changes an answer, VE asks (--ask) or answers both ways.")
    parser.add_argument("text", nargs="?", help="a plain text file (no JSON front matter)")
    parser.add_argument("--json", action="store_true", help="print the whole result as JSON")
    parser.add_argument("--ask", action="store_true",
                        help="ask about each word whose meaning changes an answer, and write your reply into the text")
    parser.add_argument("--reader-yes", action="store_true",
                        help="say yes, once, to sending texts to your reader program for the meaning check")
    parser.add_argument("--reader-off", action="store_true", help="take that yes back: send nothing from now on")
    parser.add_argument("--reader-command", help="the reader program to store with --reader-yes")
    return parser


def main(argv=None) -> int:
    parser_ = parser()
    options = parser_.parse_args(argv)
    if options.reader_off:
        withdraw_consent()
        print("VE will send nothing to a reader program from now on; it checks meanings with its word list alone.")
        if not options.text:
            return 0
    if options.reader_yes:
        command = options.reader_command or reader_command()
        sys.stdout.write(CONSENT_QUESTION.format(command=f" ({command})" if command else ""))
        sys.stdout.flush()
        reply = sys.stdin.readline().strip().lower()
        if reply in ("yes", "y"):
            give_consent(command, store=bool(options.reader_command))
            print("Saved in " + str(settings_path()) + "." + (
                f" The yes covers this reader program only ({command})." if command else
                " No reader program is set yet, so VE sends nothing: say yes again with --reader-command."))
        else:
            print("Nothing changed: VE sends nothing.")
        if not options.text:
            return 0
    if not options.text:
        parser_.error("a text file is needed")
    try:
        with Path(options.text).open("rb") as stream:
            raw = stream.read(pr.MAX_TEXT_BYTES + 1)
        if len(raw) > pr.MAX_TEXT_BYTES:
            raise ResourceLimit(f"ResourceLimit: {options.text!r} exceeds {pr.MAX_TEXT_BYTES} bytes")
        if raw.startswith(b"---\n"):
            raise VEError("this file has front matter: it is a ve-document; ask it with `ve ask`")
        text = raw.decode("utf-8")
        reader = reader_for()
        if options.ask:
            new, result = interactive(Path(options.text), text, reader, input)
            if new != text:
                Path(options.text).write_text(new, encoding="utf-8")
                result["text"].insert(0, f"Your replies were written into {options.text} as meanings in brackets.")
        else:
            result = read(options.text, text, reader=reader)
    except CheckerUnavailable as exc:
        print(str(exc), file=sys.stderr)
        return pr.EXIT_UNAVAILABLE
    except ResourceLimit as exc:
        print(str(exc), file=sys.stderr)
        return pr.EXIT_LIMIT
    except (VEError, OSError, UnicodeError) as exc:
        print(str(exc), file=sys.stderr)
        return pr.EXIT_NOT_READ
    command = reader_command()
    if result["status"] == "read" and result["meaning_check"] == "word list" and command and not consent_given(command):
        result["text"].insert(1, "  (meaning check: word list alone; VE sends your text nowhere until you say yes "
                                 "for this reader program with `ve read --reader-yes`)")
    if result.get("reader_runs"):
        result["text"].insert(1, f"  (meaning check: your text was sent to the reader program ({command}), "
                                 f"{_count(result['reader_runs'])} times{' for each reading' if options.ask else ''}; "
                                 "take the yes back with `ve read --reader-off`)")
    print(json.dumps(result, ensure_ascii=False, indent=2) if options.json else "\n".join(result["text"]))
    if result["status"] != "read":
        return pr.EXIT_NOT_READ
    unsure = any(a.get("lead") in (None, "unknown") or a.get("both_ways") for a in result["answers"])
    return pr.EXIT_UNKNOWN if unsure else pr.EXIT_READ
