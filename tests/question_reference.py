"""An independent Python reading of a question (docs/spec/question-answering.md 2, 3.1 and 4.1), for the differential
test `tests/test_question_differential.py`.

Lean is the only question reader VE runs (`english.question`, lean-only). This module is a second implementation of
the same definitions, written from the spec and sharing no code with `VE.Question`: the question's shape (2.1), its
gaps and candidates (2.2), what each candidate gives (2.3), the order of the outcomes (2.4), the indefinite
rephrasings (3.2) and the moved-word rule of the DRI ruling of 2026-10-09 (3.1, 4.1 row 11a). Each candidate is read
by Python's own English reader, which the English comparator holds to Lean's for single sentences: the Lark
all-derivations parse (`require_unique_derivation`) counts the derivations and gives the tree whose clauses the
moved-word rule reads, and the hand parser (`_python_reading`) gives the formula. It is test code: no product path
imports it.

`read(env, words, question)` gives the outcome as the differential compares it: `status`, the `code` where the
outcome fixes it, and for `one` the form, the asked sentence and the formula (wire data), and the rephrasings where
there are any. An outcome this reader cannot decide the way Lean does is `{"status": "excluded", "reason": ...}`:
a candidate's work budget (Python's reader has none) and a lexical refusal other than spacing before the `?`.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

AUXILIARIES = ("is", "must", "may")
CASE_FRAME = "Is it the case that "
WH_WORDS = ("Who", "What", "Which", "Whom", "Whose", "Where", "When", "Why", "How")
MAX_QUESTION_BYTES, MAX_TOKENS, MAX_CANDIDATES = 4096, 300, 64
CLAUSE_WORDS = ("who", "that", "which")
# E2's punctuation characters (spec english-lean 2.2): any other visible character outside a quoted name is refused.
PUNCTUATION = ",;:()[]+-*"
# The lexical refusals this reader decides; any other is excluded.
LEXICAL = ("BadSpacing", "BadCharacter", "EmptySentence")

# The tokens of 2.2 as this reader splits them: a quoted name, a run of letters, digits and underscores, or one
# other visible character. The differential's inputs are ASCII words, quoted names and punctuation.
TOKEN = re.compile(r'"[^"]*"|\w+|[^\w\s]')


def lexical_fault(outside: str) -> str | None:
    """The first lexical refusal of `body + "."` by position (E2's lexer scans left to right), quoted names blanked:
    a bad character, an empty sentence (a period with nothing since the last), or a space before a period (before
    the added one: a space before the question's `?`)."""
    content = False
    text = outside + "."
    for i, ch in enumerate(text):
        if ch == ".":
            if not content:
                return "EmptySentence"
            if text[i - 1] == " ":
                return "BadSpacing"
            content = False
        elif not (ch.isalnum() or ch in " _" or ch in PUNCTUATION):
            return "BadCharacter"
        elif ch != " ":
            content = True
    return None


class Excluded(Exception):
    """An outcome this reader does not decide as Lean does (the module docstring names each)."""


def tokens(text: str) -> list[tuple[str, int, int]]:
    return [(m.group(), m.start(), m.end()) for m in TOKEN.finditer(text)]


def is_punct(token: str) -> bool:
    return not (token[0] == '"' or token[0].isalnum() or token[0] == "_")


def capitalise(word: str) -> str:
    return word[:1].upper() + word[1:]


@dataclass(frozen=True)
class Candidate:
    form: str            # "caseThat" or "fronted"
    aux: str | None
    gap: int | None      # the byte offset in the rest where the auxiliary is put back
    sentence: str


def shape(question: str):
    """2.1: `("notQuestion",)`, `("caseThat", body)`, `("fronted", aux, rest)` or `("other", first word)`."""
    if not question.endswith("?") or question.count("?") != 1:
        return ("notQuestion",)
    s = question[:-1]
    if s.startswith(CASE_FRAME):
        return ("caseThat", s[len(CASE_FRAME):])
    for aux in AUXILIARIES:
        if s.startswith(capitalise(aux) + " "):
            return ("fronted", aux, s[len(aux) + 1:])
    return ("other", s.split(" ")[0])


def one_sentence(text: str) -> bool:
    """`text + "."` is one sentence: no period inside it."""
    return all(t != "." for t, _, _ in tokens(text))


def gaps(rest: str) -> list[int]:
    """2.2: the byte offset of every token after the first that is not punctuation."""
    if not one_sentence(rest):
        return []
    return [len(rest[:a].encode()) for t, a, _ in tokens(rest)[1:] if not is_punct(t)]


def insert_at(rest: str, aux: str, gap: int) -> str:
    raw = rest.encode()
    return (raw[:gap] + aux.encode() + b" " + raw[gap:]).decode() + "."


def candidates(question: str) -> list[Candidate]:
    sh = shape(question)
    if sh[0] == "caseThat":
        return [Candidate("caseThat", None, None, sh[1] + ".")] if one_sentence(sh[1]) else []
    if sh[0] == "fronted":
        _, aux, rest = sh
        return [Candidate("fronted", aux, g, insert_at(rest, aux, g)) for g in gaps(rest)]
    return []


class Reader:
    """Python's English reader over one environment, with the candidates' results remembered."""

    def __init__(self, env, words):
        self.env, self.words, self.memo, self.kinds = env, words, {}, None

    def got(self, sentence: str):
        """2.3: `("none",)`, `("many",)`, `("one", wire formula)` or `("refused", why)`."""
        if sentence not in self.memo:
            self.memo[sentence] = self._got(sentence)
        return self.memo[sentence]

    def _got(self, sentence: str):
        from ve.ast import _to_data
        from ve.english import _python_reading
        from ve.errors import AmbiguousDerivation, ResourceLimit, SyntaxError, VEError
        from ve.surface.unambiguity import require_unique_derivation
        try:
            require_unique_derivation(self.env, sentence)
        except AmbiguousDerivation:
            return ("many",)
        except ResourceLimit:
            return ("budget",)
        except SyntaxError:
            return ("none",)
        try:
            reading = _python_reading(self.env, sentence, self.words, {})
        except ResourceLimit:
            return ("budget",)
        except VEError as exc:
            return ("refused", type(exc).__name__)
        if reading.conclusions:
            return ("refused", "QuestionWithMarker")
        formulas = reading.document.formulas
        if len(formulas) != 1:
            return ("refused", "notOne")
        return ("one", _to_data(formulas[0]))

    def tree(self, sentence: str):
        from ve.surface.unambiguity import require_unique_derivation
        return require_unique_derivation(self.env, sentence)

    # ------------------------------------------------------------------ 2.4: the order

    def classify(self, question: str):
        sh = shape(question)
        if sh[0] == "notQuestion":
            return ("notQuestion",)
        if sh[0] == "other":
            return ("form", sh[1] in WH_WORDS)
        if len(question.encode()) > MAX_QUESTION_BYTES:
            return ("limit",)
        body = sh[1] if sh[0] == "caseThat" else sh[2]
        outside = re.sub(r'"[^"]*"', lambda m: "_" * len(m.group()), body)
        if not body or body != body.lstrip() or "  " in body or not outside.isascii() or '"' in outside:
            raise Excluded("a lexical refusal other than spacing before the question mark, a bad character or an "
                           "empty sentence")
        lexical = lexical_fault(outside)
        if lexical is not None:
            return ("lexical", lexical)
        if not one_sentence(body):
            return ("notQuestion",)
        if len(tokens(body)) > MAX_TOKENS:
            return ("limit",)
        cs = candidates(question)
        if len(cs) > MAX_CANDIDATES:
            return ("limit",)
        gs = [(c, self.got(c.sentence)) for c in cs]
        if any(g[0] == "budget" for _, g in gs):
            raise Excluded("a candidate's work budget")
        if any(g == ("refused", "notOne") for _, g in gs):
            return ("notQuestion",)
        many = next((c for c, g in gs if g[0] == "many"), None)
        if many is not None:
            return ("ambiguous", many)
        firsts = []
        for c, g in gs:
            if g[0] == "one" and all(g[1] != f for _, f in firsts):
                firsts.append((c, g[1]))
        if len(firsts) == 1:
            return ("one", *firsts[0])
        if not firsts:
            refused = next(((c, g) for c, g in gs if g[0] == "refused"), None)
            if refused is not None:
                return ("refused", refused[0], refused[1][1])
            return ("none",)
        return ("meanings", [f"{CASE_FRAME}{c.sentence[:-1]}?" for c, _ in firsts])

    def offered(self, questions: list[str]) -> list[str]:
        """3.2: the questions that read with one meaning, each meaning once, in order."""
        seen, out = [], []
        for q in questions:
            try:
                o = self.classify(q)
            except Excluded:
                continue
            if o[0] == "one" and o[2] not in seen:
                seen.append(o[2])
                out.append(q)
        return out

    def read_question(self, question: str):
        o = self.classify(question)
        if o[0] != "none":
            return o
        sh = shape(question)
        frame = CASE_FRAME if sh[0] == "caseThat" else capitalise(sh[1]) + " "
        body = sh[1] if sh[0] == "caseThat" else sh[2]
        for art in ("a", "an"):
            if body.startswith(art + " "):
                rest = body[len(art) + 1:]
                rs = self.offered([f"{frame}every {rest}?", f"{frame}some {rest}?"])
                return ("indefinite", art, rs) if rs else o
        return o

    # ------------------------------------------------------------------ the moved-word rule (3.1, 4.1 row 11a)

    def sentence_kinds(self) -> set[str]:
        """The node names of a sentence in a Lark derivation: each alternative of the grammar's inlined `?formula`
        rule, under its own name or the alias of each of its rules, read from Lark's parsed rules."""
        if self.kinds is None:
            from ve.english import english_lark_grammar
            from ve.surface.unambiguity import _parser
            rules = _parser(english_lark_grammar(self.env)).rules
            alternatives = {r.expansion[0].name for r in rules if r.origin.name == "formula"}
            self.kinds = {str(r.alias or r.origin.name) for r in rules if r.origin.name in alternatives}
        return self.kinds

    def clauses(self, sentence: str) -> list[tuple[int, int]]:
        """The character spans of the clauses of the sentence's one Lark derivation: a constituent right after a
        `who`, `that` or `which` inside its parent, to the parent's end when that constituent is a word; and a part,
        a sentence whose parent is a sentence (the `?formula` rule is inlined, so a rule that only passes a sentence
        through leaves no node)."""
        from lark import Token, Tree
        tree = self.tree(sentence)
        kinds = self.sentence_kinds()
        found = []

        def word_before(pos):
            m = re.search(r"(\w+)\s*$", sentence[:pos])
            return (m.group(1).lower(), m.start(1)) if m else (None, None)

        def walk(node):
            if not isinstance(node, Tree) or getattr(node.meta, "empty", True):
                return
            for child in node.children:
                start = child.start_pos if isinstance(child, Token) else (
                    None if getattr(child.meta, "empty", True) else child.meta.start_pos)
                if start is None:
                    continue
                word, at = word_before(start)
                if word in CLAUSE_WORDS and at >= node.meta.start_pos:
                    end = node.meta.end_pos if isinstance(child, Token) else child.meta.end_pos
                    found.append((start, end))
                elif isinstance(child, Tree) and str(node.data) in kinds and str(child.data) in kinds:
                    found.append((start, child.meta.end_pos))
                walk(child)
        walk(tree)
        return found

    def moved_out(self, c: Candidate) -> bool:
        if c.form != "fronted":
            return False
        at = len(c.sentence.encode()[:c.gap].decode())
        return any(a <= at < b for a, b in self.clauses(c.sentence))

    def askable(self, question: str) -> bool:
        try:
            o = self.read_question(question)
        except Excluded:
            return False
        return o[0] == "one" and not self.moved_out(o[1])

    def moved_rephrasings(self, c: Candidate) -> list[str]:
        spans = self.clauses(c.sentence)
        gap = len(c.sentence.encode()[:c.gap].decode())
        fronted = [f"{capitalise(c.aux)} {c.sentence[:x]}{c.sentence[y + 1:-1]}?"
                   for j, (t, x, y) in enumerate(tokens(c.sentence))
                   if j != 0 and t == c.aux and x != gap and not any(a <= x < b for a, b in spans)]
        return self.offered([q for q in [*fronted, f"{CASE_FRAME}{c.sentence[:-1]}?"] if self.askable(q)])

    def ask(self, question: str) -> dict:
        """What the mode shows, as the differential compares it."""
        try:
            o = self.read_question(question)
        except Excluded as exc:
            return {"status": "excluded", "reason": str(exc)}
        kind = o[0]
        if kind == "one":
            c, formula = o[1], o[2]
            if self.moved_out(c):
                rs = self.moved_rephrasings(c)
                return {"status": "moved", "code": "QuestionWordMoved", **({"rephrasings": rs} if rs else {})}
            return {"status": "one", "form": c.form, "sentence": c.sentence, "ast": formula}
        if kind == "indefinite":
            rs = [r for r in o[2] if self.askable(r)]
            if not rs:
                return {"status": "none", "code": "NoDerivation"}
            return {"status": "indefinite", "code": "IndefiniteQuestion", "rephrasings": rs}
        return {"notQuestion": {"status": "notQuestion", "code": "NotOneQuestion"},
                "form": {"status": "none", "code": "QuestionForm"},
                "limit": {"status": "budget", "code": "QuestionTooLong"},
                "ambiguous": {"status": "many", "code": "Ambiguous"},
                "none": {"status": "none", "code": "NoDerivation"},
                }.get(kind) or (
            {"status": "many", "code": "AmbiguousQuestion", "rephrasings": o[1]} if kind == "meanings" else
            {"status": "rejected", "code": o[1]} if kind == "lexical" else
            {"status": "rejected", **({"code": "QuestionWithMarker"} if o[2] == "QuestionWithMarker" else {})})


def lean_view(result: dict) -> dict:
    """Lean's `english.question` result as `Reader.ask` gives it: the fields the reference reader decides."""
    status = result["status"]
    if status == "one":
        return {k: result[k] for k in ("status", "form", "sentence", "ast")}
    view = {"status": status}
    if status != "rejected" or result.get("code") in ("QuestionWithMarker", *LEXICAL):
        view["code"] = result["code"]
    if "rephrasings" in result:
        view["rephrasings"] = result["rephrasings"]
    return view
