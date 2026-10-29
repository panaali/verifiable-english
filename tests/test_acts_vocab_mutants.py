"""Seeded mutants of the act grammar's vocabulary check and limits each fail a fixture (ap-2 review F1).

`lean/VE/Acts/GrammarExamples.lean` pins `checkVocab` (spec 1.4, the texts and order of D-31) and the limits of D2
with `#guard`s. The review found seven mutants that kept every guard passing: 128 frames refused, *to* accepted as a
head word, `wordOk` without `actWord`, 31q without `wordOk`, 31r without its head-word half, 31k checked before 31g,
and a step budget of 1,000,000. This test plants those seven, the other halves and limits of the same kind, and a
mutant for every way a D-31 row or its place can be lost, generated from `checkVocab`'s own source: each condition
dropped, and each two adjacent conditions swapped (a permutation that is not the identity swaps some adjacent pair).
`_generated` adds a mutant for every list of 1.4's check read only in part (its first or last element alone, or
without its first or last; reviews F7 and F11) and for every marker list swapped for another (F7, F10).

Each mutant is elaborated with `lake env lean`, with the proofs of `Read.lean` cut out, so a fixture must catch it:
it must fail, and only at `#guard`s (a mutant that does not elaborate proves nothing). The unmutated sources must
elaborate cleanly, and every mutation must change the source exactly once.
"""
from __future__ import annotations

import re
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, ROOT, lean_build

ACTS = LEAN / "VE/Acts"
SPEC = ROOT / "docs/spec/act-phrases.md"
GUARD_FAILED = "did not evaluate to `true`"


def _sources() -> tuple[str, str, str]:
    """`Syntax.lean` with the words it reads from `Lexical.lean` (`Tok`, `joinWords`, `clauseWords`, their one owner
    since ap-1a) in front of its own definitions, as ap-2 wrote them there; then `Read.lean` and `GrammarExamples.lean`."""
    syntax, read, examples = ((ACTS / f"{name}.lean").read_text() for name in ("Syntax", "Read", "GrammarExamples"))
    lexical = (ACTS / "Lexical.lean").read_text()
    words = lexical[lexical.index("namespace VE.Acts.Lexical\n"):lexical.index("/-- The limits of 12")]
    words = words.replace("open VE.Norms.Wire (actReserved words actWord scanSlots)\n", "") + "end VE.Acts.Lexical\n\n"
    at = syntax.index("namespace VE.Acts\n")
    syntax = syntax[:at].replace("import VE.Acts.Lexical\n", "import VE.Acts.LexicalBase\n") + words + syntax[at:]
    return syntax, read, examples


def _split_imports(text: str) -> tuple[list[str], str]:
    lines = text.split("\n")
    imports = [line for line in lines if line.startswith("import ")]
    return imports, "\n".join(line for line in lines if not line.startswith("import "))


# What the sweep's mutants (`_sweep`) write in place of a comparison: `a ≼ₘ b` says `a` begins `b` (a string by its
# characters, a list by its elements), `a ≽ₘ b` that `b` begins `a`, `⋠ₘ` and `⋡ₘ` their negations; `xs.preContains y`
# says `y` begins an element of `xs`, `xs.containsPre y` that an element begins `y`.
PRELUDE = """
namespace VEMutant
class Pre (α : Type) where pre : α → α → Bool
instance : Pre String := ⟨fun a b => b.startsWith a⟩
instance {β : Type} [BEq β] : Pre (List β) := ⟨fun a b => a.isPrefixOf b⟩
def sup {α : Type} [Pre α] (a b : α) : Bool := Pre.pre b a
def npre {α : Type} [Pre α] (a b : α) : Bool := !Pre.pre a b
def nsup {α : Type} [Pre α] (a b : α) : Bool := !Pre.pre b a
end VEMutant
infix:50 " ≼ₘ " => VEMutant.Pre.pre
infix:50 " ≽ₘ " => VEMutant.sup
infix:50 " ⋠ₘ " => VEMutant.npre
infix:50 " ⋡ₘ " => VEMutant.nsup
def List.preContains {α : Type} [VEMutant.Pre α] (xs : List α) (y : α) : Bool := xs.any (VEMutant.Pre.pre y ·)
def List.containsPre {α : Type} [VEMutant.Pre α] (xs : List α) (y : α) : Bool := xs.any (VEMutant.Pre.pre · y)
def List.revPrefixOf {α : Type} [BEq α] (a b : List α) : Bool := b.isPrefixOf a
def List.beqOf {α : Type} [BEq α] (a b : List α) : Bool := a == b
"""


INLINED = {"import VE.Acts.Syntax", "import VE.Acts.Read"}


def _assemble(syntax: str, read: str, examples: str) -> str:
    """One file: the three modules' bodies, with the imports they take from outside `VE.Acts`, the sweep's `PRELUDE`,
    and no proofs."""
    read = read[:read.index("section Proofs")] + "end VE.Acts\n"
    imports, bodies = [], []
    for text in (syntax, read, examples):
        own, body = _split_imports(text)
        imports += [line for line in own if line not in INLINED and line not in imports]
        bodies.append(body)
    return "\n".join(imports) + "\n" + PRELUDE + "\n".join(bodies)


def _check_vocab(syntax: str) -> tuple[list[str], list[list[str]], list[str]]:
    """`checkVocab`'s source as (the lines before its first condition, one block of lines per condition, the rest).

    A condition starts at a line indented by two spaces that begins with `if ` or `for `; the body ends at the first
    line that is blank or not indented."""
    lines = syntax.split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("def checkVocab "))
    end = next(i for i in range(start + 1, len(lines)) if not lines[i].startswith(" "))
    first = next(i for i in range(start, end) if re.match(r"  (if|for) ", lines[i]))
    blocks: list[list[str]] = []
    for line in lines[first:end]:
        if re.match(r"  (if|for) ", line):
            blocks.append([line])
        else:
            blocks[-1].append(line)
    return lines[:first], blocks, lines[end:]


def _with_blocks(syntax: str, order: list[int]) -> str:
    head, blocks, tail = _check_vocab(syntax)
    return "\n".join(head + [line for i in order for line in blocks[i]] + tail)


def _d31() -> list[tuple[str, str]]:
    """D-31's rows of the specification, in order: (row, text)."""
    rows = re.findall(r"^\| (31[a-z]) \| [^\n]*\| `([^`\n]+)` \|$", SPEC.read_text(), re.M)
    assert [row for row, _ in rows] == [f"31{chr(c)}" for c in range(ord("a"), ord("s") + 1)], rows
    return rows


def _replace(old: str, new: str, where: str = "syntax"):
    def mutate(syntax: str, read: str) -> tuple[str, str]:
        text = syntax if where == "syntax" else read
        assert text.count(old) == 1, f"{old!r} occurs {text.count(old)} times"
        text = text.replace(old, new)
        return (text, read) if where == "syntax" else (syntax, text)
    return mutate


def _order(order_of):
    def mutate(syntax: str, read: str) -> tuple[str, str]:
        return _with_blocks(syntax, order_of(len(_check_vocab(syntax)[1]))), read
    return mutate


def _moved(source: int, target: int):
    """Condition `source` moved to just before condition `target`."""
    def order(n: int) -> list[int]:
        rest = [i for i in range(n) if i != source]
        return rest[:target] + [source] + rest[target:]
    return _order(order)


ROWS = [row for row, _ in _d31()]

# The definitions whose lists and case folds the generated mutants below cut or swap: every definition of
# `Syntax.lean`, read from its source (1.4's check, the word lists of 1.2 it reads, and the terminals of 5.1; ap-2
# review F13: `Term.accepts` was missing from a hand-written list).
SCOPE = tuple(f"def {name} " for name in re.findall(r"^def ([\w.]+) ", _sources()[0], re.M))
# A method on a list, and a position that takes a list as its argument.
LIST_METHOD = re.compile(r"\.(find\?|any|all|contains|isPrefixOf|isEmpty|flatMap|map|filter|length|head\?)(?![\w?])")
LIST_ARGUMENT = re.compile(r"\bfor \w+ in |\bfirstDup |\.isPrefixOf |\.intercalate ")
# The methods whose result is a list again, so a binding whose value starts with a list and one of them is a list.
LIST_RESULT = ("flatMap", "filter", "map", "take")
NAME = "._·?'"
CLOSE, OPEN = {")": "(", "]": "["}, {"(": ")", "[": "]"}
# A frame's marker lists, as `checkVocab` writes them (`ms f` is the two without `""`); each stands for the others.
SIBLINGS = ["(f.markers ++ f.mods)", '(f.markers.filter (· ≠ ""))', "(ms f)", "f.markers", "f.split", "f.mods"]
SIBLING = [re.escape(s) for s in SIBLINGS[:3]] + [r"\bms f\b"] + [rf"\b{re.escape(s)}\b" for s in SIBLINGS[3:]]


def _span(text: str, start: str) -> tuple[int, int]:
    """Where the definition that begins with `start` is: its first line to the next line that is not indented."""
    lines, offset = text.split("\n"), 0
    for i, line in enumerate(lines):
        if line.startswith(start):
            end = next(k for k in range(i + 1, len(lines)) if not lines[k].startswith(" "))
            return offset, offset + sum(len(line) + 1 for line in lines[i:end])
        offset += len(line) + 1
    raise AssertionError(f"no {start!r}")


def _masked(text: str) -> str:
    """`text` with the inside of every string literal blanked (same length), so a word or bracket in a message is never
    read as code."""
    return re.sub(r'"[^"\n]*"', lambda m: '"' + " " * (len(m.group()) - 2) + '"', text)


def _term_before(text: str, end: int) -> int:
    """The start of the term that ends at `end`: a balanced group or list, or a name such as `f.head` or `·.head`."""
    if text[end - 1] in CLOSE:
        close, depth, i = text[end - 1], 0, end - 1
        while (depth := depth + {close: 1, CLOSE[close]: -1}.get(text[i], 0)) != 0:
            i -= 1
        return i
    i = end
    while text[i - 1].isalnum() or text[i - 1] in NAME:
        i -= 1
    return i


def _term_after(text: str, start: int) -> int:
    """The end of the term that starts at `start`: a balanced group or list, an application up to `do`, or a name."""
    if text[start] in OPEN:
        opening, depth, i = text[start], 0, start
        while (depth := depth + {opening: 1, OPEN[opening]: -1}.get(text[i], 0)) != 0:
            i += 1
        return i + 1
    if text[start - 3:start] == "in ":
        return text.index(" do", start)
    i = start
    while text[i].isalnum() or text[i] in NAME:
        i += 1
    return i


def _result_is_list(signature: str) -> bool:
    """A declared type `A → B → C` is a list's when its result `C` is."""
    return signature.split("→")[-1].strip().startswith("List")


def _arity(binders: str) -> int:
    return binders.count("(")


def _list_fields_of_constructors(syntax: str) -> dict[str, list[int]]:
    """For each constructor of an `inductive` of `syntax`, the positions of its arguments declared `List`."""
    positions: dict[str, list[int]] = {}
    for block in re.findall(r"^inductive \w+([^\n]*\n(?:  [^\n]*\n)*)", syntax, re.M):
        for ctor, binders in re.findall(r"\| (\w+)((?: \([^()]*\))*)", block):
            names = [(name, kind.strip()) for names, kind in re.findall(r"\(([^():]+):([^()]*)\)", binders)
                     for name in names.split()]
            positions[ctor] = [i for i, (_, kind) in enumerate(names) if kind.startswith("List")]
    return positions


def _in_pattern(text: str, start: int) -> bool:
    """Whether `start` is in the pattern of a match arm (`  | .adv ws, .word v =>`), where a name is bound."""
    line = text.rindex("\n", 0, start) + 1
    return text.startswith("  | ", line) and "=>" not in text[line:start]


def _list_names(syntax: str) -> tuple[set[str], dict[str, int], dict[str, int]]:
    """The names whose values are lists, read from the declarations of `syntax` (the type checker's job, done for this
    file's small set of forms): the structure fields declared `List`, the definitions whose result is a `List`, and
    the local names: the lets of `checkVocab` that are annotated `List` or bound to a list, and the names a match arm
    of a definition of `SCOPE` binds to a constructor's argument declared `List` (ap-2 review F13: `ws` and `ex` of
    `Term.accepts`), each with its number of arguments."""
    fields = {name for block in re.findall(r"^structure \w+ where\n((?:  .*\n)+)", syntax, re.M)
              for name in re.findall(r"^  (\w+) : List\b", block, re.M)}
    defs = {name.rsplit(".", 1)[-1]: _arity(binders) + len(signature.split("→")) - 1
            for name, binders, signature in re.findall(r"^def ([\w.]+)((?: \([^()]*\))*) : ([^\n]*?)(?: :=.*)?$",
                                                       syntax, re.M) if _result_is_list(signature)}
    lets: dict[str, int] = {}
    ctors = _list_fields_of_constructors(syntax)
    for scope in SCOPE:
        lo, hi = _span(syntax, scope)
        for pattern in re.findall(r"^  \| (.*?) =>", syntax[lo:hi], re.M):
            for ctor, args in re.findall(r"\.(\w+)((?: \w+)*)", pattern):
                lets |= {args.split()[i]: 0 for i in ctors.get(ctor, []) if i < len(args.split())}
    lets.pop("_", None)
    lo, hi = _span(syntax, "def checkVocab ")
    for name, binders, annotation, value in re.findall(r"^  let (\w+)((?: \([^()]*\))*)(?: : ([^\n]*?))? := (.*)$",
                                                       _masked(syntax[lo:hi]), re.M):
        atoms = _atom_pattern(fields, defs, lets)
        lead = atoms.match(value)
        rest = value[lead.end():] if lead else None
        if (_result_is_list(annotation) if annotation else
                rest is not None and (rest == "" or rest.startswith(" ++ ") or
                                      re.match(rf"\.({'|'.join(LIST_RESULT)})\b", rest))):
            lets[name] = _arity(binders)
    return fields, defs, lets


def _atom_pattern(fields, defs: dict[str, int], lets: dict[str, int]) -> re.Pattern:
    """A list-valued name: a list field of a name or `·`, a list definition or let (with `Lexical.` or not) applied to
    as many arguments as it takes, or a list literal. A function's arguments are read by `_atoms`."""
    names = [rf"(?:\w+\.)*{re.escape(n)}" for n, k in {**defs, **lets}.items() if k == 0]
    funcs = [re.escape(n) for n, k in {**defs, **lets}.items() if k > 0]
    parts = [rf"(?:(?<![\w.·])[A-Za-z_]\w*|·)\.(?:{'|'.join(sorted(fields))})(?![\w?'])"] if fields else []
    parts += [rf"(?<![\w.]){n}(?![\w?'])" for n in names]
    parts += [rf"(?<![\w.])(?P<f{i}>{n})(?![\w?'])" for i, n in enumerate(funcs)]
    parts.append(r"\[[^\[\]]+\]")
    return re.compile("|".join(parts))


def _atoms(syntax: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """In the definitions of `SCOPE`: every occurrence of a list-valued name (not where a `def`, `let` or match arm
    binds it), and every list
    function named without its argument (`flatMap wordsOf`), whose results are lists built inside that argument."""
    text = _masked(syntax)
    pattern = _atom_pattern(*_list_names(syntax))
    atoms, bare = [], []
    for scope in SCOPE:
        lo, hi = _span(text, scope)
        for m in pattern.finditer(text, lo, hi):
            if re.search(r"(?:\bdef|\blet) $", text[max(0, m.start() - 4):m.start()]) or _in_pattern(text, m.start()):
                continue
            if not any(k.startswith("f") and v is not None for k, v in m.groupdict().items()):
                atoms.append(m.span())
            elif text[m.end()] == " " and (text[m.end() + 1].isalnum() or text[m.end() + 1] in "(·["):
                atoms.append((m.start(), _term_after(text, m.end() + 1)))
            else:
                bare.append(m.span())
    return atoms, bare


def _list_terms(syntax: str) -> list[tuple[int, int]]:
    """Every list the definitions of `SCOPE` range over: each receiver of a list method and each list argument, but not
    the argument of a definition's own recursive call (Lean refuses a recursion whose argument does not shrink); each
    operand of `++`; each value of a list binding; each list a `flatMap`'s function builds; and every occurrence of a
    list-valued name (`_atoms`), wherever it stands. A term that is another one in parentheses is the same list."""
    text, terms = _masked(syntax), set()
    for scope in SCOPE:
        lo, hi = _span(text, scope)
        terms |= {(_term_before(text, m.start()), m.start()) for m in LIST_METHOD.finditer(text, lo, hi)}
        terms |= {(m.end(), _term_after(text, m.end())) for m in LIST_ARGUMENT.finditer(text, lo, hi)
                  if m.group() != scope.split()[1] + " "}
        terms |= {(_term_before(text, m.start()), m.start()) for m in re.finditer(r" \+\+ ", text[:hi]) if lo <= m.start()}
        terms |= {(m.end(), _term_after(text, m.end())) for m in re.finditer(r" \+\+ ", text[:hi]) if lo <= m.start()}
        terms |= {(m.end(), _term_after(text, m.start() + len(".flatMap ")) - 1)
                  for m in re.finditer(r"\.flatMap \(fun \w+ => ", text[:hi]) if lo <= m.start()}
    _, defs, lets = _list_names(syntax)
    lo, hi = _span(text, "def checkVocab ")
    for m in re.finditer(r"^(?:def|  let) (\w+)[^\n]*? := (?!do$)(.+)$", text, re.M):
        if m.group(1) in defs or (m.group(1) in lets and lo <= m.start() < hi):
            terms.add(m.span(2))
    terms |= set(_atoms(syntax)[0])
    terms = {(s, e) for s, e in terms if s < e}
    return sorted((s, e) for s, e in terms if not ((s - 1, e + 1) in terms and text[s - 1] == "(" and text[e] == ")"))


# The ways a condition reads only part of a list (ap-2 reviews F7 and F11): one element at either end, or all but one
# end. Each is a Lean method chain applied to the list.
CUTS = {"first-only": "take 1", "last-only": "reverse.take 1", "without-first": "drop 1", "without-last": "dropLast"}


def _cut(term: str, cut: str) -> str:
    """`term` cut by `cut`, one of `CUTS`. A `·` term stays the function's argument, so it is piped."""
    if term.startswith("·"):
        return f"{term}.{cut} |>"
    whole = term.startswith("(") and _term_after(term, 0) == len(term)
    return f"({term if whole or ' ' not in term else f'({term})'}.{cut})"


# The ways a case fold reads only part of a word (ap-2 review F14: `decapitalize` for `toLower`): the word as its list
# of characters, the part of `CUTS` folded and the rest kept, each `{x}` the word.
FOLD = re.compile(r"(?<![\w.])(\w+)\.(toLower|toUpper)(?![\w?'])")
CASE_CUTS = {
    "first-only": "String.mk (({x}.toList.take 1).map Char.{fold} ++ {x}.toList.drop 1)",
    "last-only": "String.mk ({x}.toList.dropLast ++ ({x}.toList.reverse.take 1).map Char.{fold})",
    "without-first": "String.mk ({x}.toList.take 1 ++ ({x}.toList.drop 1).map Char.{fold})",
    "without-last": "String.mk ({x}.toList.dropLast.map Char.{fold} ++ {x}.toList.reverse.take 1)",
}
assert set(CASE_CUTS) == set(CUTS)


def _folds(syntax: str) -> list[re.Match]:
    """Every case fold of a word in the definitions of `SCOPE` (`v.toLower`)."""
    text = _masked(syntax)
    return [m for scope in SCOPE for m in FOLD.finditer(text, *_span(text, scope))]


def _slug(term: str) -> str:
    return re.sub(r"[^A-Za-z0-9.]+", "-", term.replace("++", "and").replace("≠", "ne")).strip("-.")


def _at(start: int, end: int, new: str):
    def mutate(syntax: str, read: str) -> tuple[str, str]:
        return syntax[:start] + new + syntax[end:], read
    return mutate


def _generated() -> dict:
    """Two kinds of mutant for every list of 1.4's check, numbered in source order within a name:

    - **part of the list** (ap-2 review F7: 31c and 31r read only a head's first word; F11: 31f and 31s skip the first
      or the last frame, 31s reads a head's first word only when it has two; F13: `Term.accepts` reads one adverb or
      excluded word): each list cut in each way of `CUTS`, so a condition must be pinned with its fault in a later
      element, in an earlier one, at the start and at the end (a word, marker, frame, adverb or excluded word);
    - **part of the word** (F14: a case fold of its first letter only): each case fold cut in each way of
      `CASE_CUTS`, so a case check must be pinned with a capital past the first letter and with one at the end;
    - **another marker list** (F7: 31o over markers only, 31i over modifiers too, 31g without `""`): each of a
      frame's marker lists replaced by each of the others, so a condition must be pinned on the list 1.4 names."""
    syntax = _sources()[0]
    mutants: dict = {}

    def add(name: str, mutate) -> None:
        k = sum(1 for other in mutants if other.rsplit("-", 1)[0] == name)
        mutants[f"{name}-{k + 1}"] = mutate

    for kind, cut in CUTS.items():
        for start, end in _list_terms(syntax):
            add(f"{kind}-{_slug(syntax[start:end])}", _at(start, end, _cut(syntax[start:end], cut)))
        for start, end in _atoms(syntax)[1]:
            add(f"{kind}-each-{syntax[start:end]}", _at(start, end, f"(fun x => ({syntax[start:end]} x).{cut})"))
        for m in _folds(syntax):
            add(f"case-{kind}-{m.group()}", _at(*m.span(), f"({CASE_CUTS[kind].format(x=m[1], fold=m[2])})"))
    for start, end in _siblings(syntax):
        own = "(ms f)" if syntax[start:end] == "ms f" else syntax[start:end]
        defines_ms = syntax.startswith("  let ms ", syntax.rindex("\n", 0, start) + 1)
        for other in SIBLINGS:
            if other != own and not (defines_ms and other == "(ms f)"):
                add(f"{_slug(own)}-as-{_slug(other)}", _at(start, end, other))
    return mutants


def _siblings(syntax: str) -> list[tuple[int, int]]:
    """Every occurrence in `checkVocab` of a frame's marker list, the operands of `(f.markers ++ f.mods)` among them
    (ap-2 review F10); `ms f` in parentheses is the same list as `(ms f)`."""
    lo, hi = _span(syntax, "def checkVocab ")
    spans = {m.span() for s in SIBLING for m in re.finditer(s, syntax[:hi]) if lo <= m.start()}
    return sorted((s, e) for s, e in spans if not ((s - 1, e + 1) in spans and syntax[s - 1] == "("))


def _definitions(text: str) -> list[tuple[str, int, int]]:
    """Every definition of a module (of `Read.lean`, those before its proofs), as (name, start, end)."""
    text = text[:text.index("section Proofs")] if "section Proofs" in text else text
    return [(name, *_span(text, f"def {name} ")) for name in re.findall(r"^def ([\w.]+)[ \n]", text, re.M)]


def _inductives(texts: tuple[str, ...]) -> dict[str, dict[str, list[str]]]:
    """For each `inductive` of `texts`, its constructors, each with the types of its arguments (`Tok.fixed`:
    `["Nat"]`)."""
    found: dict[str, dict[str, list[str]]] = {}
    for text in texts:
        for name, block in re.findall(r"^inductive (\w+)([^\n]*(?:\n  [^\n]*)*)", text, re.M):
            found[name] = {ctor: [kind.strip() for names, kind in re.findall(r"\(([^():]+):([^()]*)\)", binders)
                                  for _ in names.split()]
                           for ctor, binders in re.findall(r"\| (\w+)((?: \([^()]*\))*)", block)}
    return found


def _nullary(inductives: dict[str, dict[str, list[str]]]) -> dict[str, list[str]]:
    """For each `inductive` with two constructors without arguments or more, those constructors (and `Bool`'s two)."""
    groups = {"Bool": ["true", "false"]}
    for name, ctors in inductives.items():
        names = [f".{c}" for c, kinds in ctors.items() if not kinds]
        if len(names) > 1:
            groups[name] = names
    return groups


def _top_level(pattern: str, sep: str = ",") -> list[tuple[int, int]]:
    """The spans of `pattern`'s parts between the separators that are not inside a bracket."""
    spans, depth, start = [], 0, 0
    for i, ch in enumerate(pattern):
        depth += {"(": 1, "[": 1, ")": -1, "]": -1}.get(ch, 0)
        if ch == sep and depth == 0:
            spans.append((start, i))
            start = i + 1
    spans.append((start, len(pattern)))
    return [(s + len(pattern[s:e]) - len(pattern[s:e].lstrip()), e - (len(pattern[s:e]) - len(pattern[s:e].rstrip())))
            for s, e in spans]


BOUND = re.compile(r"(?<![\w.])([a-zA-Zα-ωΑ-Ω][\w']*)")
NOT_BOUND = {"none", "some", "true", "false"}


def _arms(text: str, lo: int, hi: int) -> list[dict]:
    """The match arms between `lo` and `hi`: where the pattern and the body are, the names the pattern binds, and the
    arms of the same `match` (same indentation, one after the other)."""
    arms = []
    for m in re.finditer(r"^( +)\| (.*?) =>(.*)$", text[:hi], re.M):
        if m.start() < lo:
            continue
        indent = len(m.group(1))
        end = next((k.start() for k in re.finditer(r"^ *\| ", text[m.end():hi], re.M)
                    if len(k.group()) - 2 <= indent), hi - m.end()) + m.end()
        bound = {b for b in BOUND.findall(m.group(2)) if b not in NOT_BOUND}
        arms.append({"indent": indent, "pattern": m.span(2), "body": (m.start(3), end), "bound": bound})
    for i, arm in enumerate(arms):
        arm["later"] = []
        for later in arms[i + 1:]:
            if later["indent"] != arm["indent"]:
                break
            arm["later"].append(later)
    return arms


def _sweep() -> dict:
    """The sweep of the acting DRI's note for ap-2 review F15: in every definition of `Syntax.lean` and `Read.lean`
    (before its proofs), each match arm and each comparison changed in turn.

    - **arms**: each argument of a pattern made `_` (unless it binds a name the arm reads), each constructor in a
      pattern made each other constructor of its `inductive` with the same argument types (the `inductive` of an argument
      that the definition's type names, such as `Tok` in `Term → Tok → Bool`; otherwise the one `inductive` with a
      constructor of that name, and none if two have one, such as `ok`), each number in a pattern made `_`, each `_` that a constructor declares `Nat` made `0` and `(_ + 1)`, each arm dropped when a later arm
      of its `match` matches everything, and each body that is `true`, `false` or a constructor without arguments of
      the result's `inductive` that has others made each of the others;
    - **comparisons**: each `==`, `!=` and `≠` negated and made a prefix test either way round (`≼ₘ`, `≽ₘ`; the
      word begins the keyword, or the keyword begins the word), each `contains` made a prefix test either way round,
      each `isPrefixOf` made the reverse prefix test, a suffix test and an equality, each `<` made `≤` and back;
    - **logic and numbers**: each `&&` made `||` and back, each `!` dropped, each number one more and one less.

    A definition over a type variable (`firsts`) has no prefix test, so its comparisons are only negated. Mutants that
    Lean refuses (an arm made redundant) are in `UNWRITABLE`, each with its reason."""
    sources = {"syntax": _sources()[0], "read": _sources()[1]}
    inductives = _inductives(tuple(sources.values()))
    nullary = _nullary(inductives)
    mutants: dict = {}

    def add(op: str, name: str, where: str, start: int, end: int, new: str) -> None:
        stem = f"sweep-{op}-{name}"
        k = sum(1 for other in mutants if other.rsplit("-", 1)[0] == stem)
        mutants[f"{stem}-{k + 1}"] = _at_in(where, start, end, new)

    for where, source in sources.items():
        text = _masked(source)
        for name, lo, hi in _definitions(source):
            signature = text[lo:text.find(":=", lo, hi) if ":=" in text[lo:hi] else text.index("\n", lo)]
            generic = "α" in signature
            result = re.split(r" : | → ", signature.strip())[-1].split()[0]
            # The types a definition by pattern matching (`def Term.accepts : Term → Tok → Bool`) matches on.
            scrutinees = [k.strip() for k in signature.split(" : ", 1)[1].split("→")[:-1]] if "(" not in signature else []
            for arm in _arms(text, lo, hi):
                p0, p1 = arm["pattern"]
                body = text[arm["body"][0]:arm["body"][1]]
                for position, (s, e) in enumerate(_top_level(text[p0:p1])):
                    part = text[p0 + s:p0 + e]
                    if part != "_" and not any(re.search(rf"(?<![\w.]){re.escape(b)}(?![\w'])", body)
                                               for b in BOUND.findall(part) if b not in NOT_BOUND):
                        add("wildcard", name, where, p0 + s, p0 + e, "_")
                    owner = {}
                    for c in re.finditer(r"(?<![\w.])\.(\w+)", part):
                        owners = [ctors for ctors in inductives.values() if c[1] in ctors]
                        if c.start() == 0 and arm["indent"] == 2 and position < len(scrutinees):
                            owners = [inductives[scrutinees[position]]] if scrutinees[position] in inductives else []
                        if c.start() == 0:
                            owner = owners[0] if len(owners) == 1 else {}
                        for other, k in owners[0].items() if len(owners) == 1 else ():
                            if other != c[1] and k == owners[0][c[1]]:
                                add("ctor-swap", name, where, p0 + s + c.start(), p0 + s + c.end(), f".{other}")
                    ctor = re.match(r"\.(\w+) ", part)
                    for i, (a0, a1) in enumerate(_top_level(part[ctor.end():], " ") if ctor else []):
                        arg, at = part[ctor.end() + a0:ctor.end() + a1], p0 + s + ctor.end()
                        if re.fullmatch(r"\d+|\(_ \+ \d+\)", arg):
                            add("wildcard-index", name, where, at + a0, at + a1, "_")
                        if arg == "_" and owner.get(ctor[1], [])[i:i + 1] == ["Nat"]:
                            add("index-0", name, where, at + a0, at + a1, "0")
                            add("index-succ", name, where, at + a0, at + a1, "(_ + 1)")
                if any(all(t == "_" for t in re.split(r"\s*,\s*", text[slice(*la["pattern"])])) for la in arm["later"]):
                    line = text.rindex("\n", 0, p0) + 1
                    add("drop-arm", name, where, line, text.index("\n", arm["body"][0]) + 1, "")
                b0, b1 = arm["body"]
                value = text[b0:b1].strip()
                for other in nullary.get(result, []) if value in nullary.get(result, []) else []:
                    if other != value:
                        at = b0 + text[b0:b1].index(value)
                        add("arm-value", name, where, at, at + len(value), other)
            for m in re.finditer(r" (==|!=|≠) ", text[:hi]):
                if m.start() < lo:
                    continue
                negated = {"==": " != ", "!=": " == ", "≠": " = "}[m[1]]
                add("negate", name, where, *m.span(), negated)
                if not generic:
                    for op in ((" ≼ₘ ", " ≽ₘ ") if m[1] == "==" else (" ⋠ₘ ", " ⋡ₘ ")):
                        add("prefix", name, where, *m.span(), op)
            for m in re.finditer(r"\.contains\b", text[:hi]):
                if m.start() >= lo and not generic:
                    add("contains-prefix", name, where, *m.span(), ".preContains")
                    add("contains-prefix", name, where, *m.span(), ".containsPre")
            for m in re.finditer(r"\.isPrefixOf\b", text[:hi]):
                if m.start() >= lo:
                    for other in (".revPrefixOf", ".isSuffixOf", ".beqOf"):
                        add("prefix-other", name, where, *m.span(), other)
            for m in re.finditer(r" (<|≤) ", text[:hi]):
                if m.start() >= lo:
                    add("strict", name, where, *m.span(), " ≤ " if m[1] == "<" else " < ")
            for m in re.finditer(r" (&&|\|\|) ", text[:hi]):
                if m.start() >= lo:
                    add("and-or", name, where, *m.span(), " || " if m[1] == "&&" else " && ")
            for m in re.finditer(r"(?<!\w)!(?!=)", text[:hi]):
                if m.start() >= lo:
                    add("not-dropped", name, where, *m.span(), "")
            for m in re.finditer(r"(?<![\w.])\d+(?![\w.])", text[:hi]):
                if m.start() >= lo:
                    add("number-up", name, where, *m.span(), str(int(m[0]) + 1))
                    if int(m[0]) > 0:
                        add("number-down", name, where, *m.span(), str(int(m[0]) - 1))
    return mutants


def _at_in(where: str, start: int, end: int, new: str):
    def mutate(syntax: str, read: str) -> tuple[str, str]:
        if where == "syntax":
            return syntax[:start] + new + syntax[end:], read
        return syntax, read[:start] + new + read[end:]
    return mutate


# Generated mutants that change no answer of `checkVocab`, so no fixture can kill them, each with the reason.
EQUIVALENT: dict[str, str] = {
    "first-only-head-1": "31b: a head's first word is absent exactly when the head is empty",
    "first-only-f.head-6": "31s: the first word of a head's first word is its first word",
    "first-only-wordsOf-m-2": "31l: a marker's words cut to the first are empty exactly when its words are",
    "ms-f-as-f.markers-and-f.mods-1": "the marker words: `\"\"` has no words, so it adds none",
    "ms-f-as-f.markers-and-f.mods-3": "31m: `\"\"` has no words, so it adds no word to check",
    "ms-f-as-f.markers-and-f.mods-4": "31n: `\"\"` has no words, so it adds no word to check",
    "ms-f-as-f.markers-and-f.mods-6": "31o: no marker begins `\"\"`, since 31l refused every other marker without words",
    "f.markers-as-f.markers.filter-ne-4": "31k: 31j refused an empty modifier marker, so `\"\"` matches none",
    # `ms f` with a list repeated or filtered twice (F10): `ms f` is read only through `find?` and `contains` and as
    # 31o's `for` with its `n != m`, and a repeated element changes none of their answers.
    "f.markers-as-f.markers-and-f.mods-1": "`ms f` is `f.markers ++ f.mods ++ f.mods`: the modifiers again",
    "f.markers-as-f.markers.filter-ne-1": "`ms f` filters `\"\"` out of the argument markers twice",
    "f.mods-as-f.markers-and-f.mods-1": "`ms f` is `f.markers ++ f.markers ++ f.mods`: the argument markers again",
    # The other end of a list (F11).
    "last-only-head-1": "31b: a head's last word is absent exactly when the head is empty",
    "last-only-wordsOf-m-2": "31l: a marker's words cut to the last are empty exactly when its words are",
    "without-last-g.head-2": "31f: a head other than `g.head` begins `g.head` exactly when it begins `g.head` without "
                             "its last word, being shorter",
    "without-last-wordsOf-n-1": "31o: 31l made each marker its words joined by single spaces, so two distinct markers "
                                "have distinct words, and one's words begin the other's only if they are shorter",
    # The sweep (ap-2 review F15): a comparison made a prefix test where only equal values pass it.
    "sweep-prefix-wordOk-1": "`w.toLower` has as many letters as `w`, so `w` begins it exactly when the two are equal",
    "sweep-prefix-wordOk-2": "`w.toLower` has as many letters as `w`, so it begins `w` exactly when the two are equal",
    "sweep-prefix-wordsOf-1": "only `\"\"` begins `\"\"`, so a piece that does not begin it is a piece other than `\"\"`",
    "sweep-prefix-checkVocab-1": "`ms f`: only `\"\"` begins `\"\"`, so a marker that does not begin it is not `\"\"`",
    "sweep-prefix-checkVocab-3": "31f: `f.head` begins `g.head`, so `g.head` begins `f.head` only when the two are equal",
    "sweep-prefix-checkVocab-5": "31l: a marker's words joined by single spaces are never longer than the marker, so the "
                                 "marker begins them only when the two are equal",
    "sweep-prefix-checkVocab-7": "31l: only `[]` begins `[]`",
    "sweep-prefix-checkVocab-9": "31o: 31l made `n` and `m` their words joined by single spaces, and `m`'s words begin "
                                 "`n`'s, so `n` is at least as long as `m` and begins it only when the two are equal",
    "sweep-contains-prefix-checkVocab-6": "31j: a modifier marker begins `\"\"` exactly when it is `\"\"`",
    "sweep-contains-prefix-clauseWords-2": "no word of `actReserved` but a join word begins with a join word (`and`, "
                                           "`or`, `nor`, `for`), and `clauseWords`'s list is pinned",
    "sweep-wildcard-valueOf-1": "the last arm of `valueOf`'s match: `.error _` is the only case the arm before leaves",
}

# The sweep's mutants that Lean refuses, each with its reason: each makes a later arm of its match redundant, so it is
# not a function a fixture could run (`test_an_unwritable_mutant_is_refused_by_lean`).
UNWRITABLE: dict[str, str] = {
    "sweep-wildcard-firstDup-1": "`| _ => none` leaves `x :: xs` nothing to match",
    "sweep-wildcard-firsts-1": "`| _ => []` leaves `x :: xs` nothing to match",
    "sweep-wildcard-listing-1": "`| _ => .limit` leaves `some ts` nothing to match",
    "sweep-wildcard-readIn-1": "`| _ => .limit` leaves the three `.ok` arms nothing to match",
    "sweep-wildcard-readIn-2": "`| _ => .none` leaves `.ok [A]` and `.ok (A :: B :: _)` nothing to match",
    "sweep-ctor-swap-Term.accepts-20": "`.fill ws, .word v` before `.fill ex, .word v` leaves the second nothing",
    "sweep-ctor-swap-Term.accepts-21": "`.adv ex, .word v` after `.adv ws, .word v` matches nothing",
}

MUTANTS = {
    # The review's seven (ap-2 review F1).
    "31a-128-refused": _replace("128 < fs.length", "128 ≤ fs.length"),
    "31d-to-head-accepted": _replace("f.head.find? resv.contains", "f.head.find? mresv.contains"),
    "wordOk-without-actWord": _replace("VE.Norms.Wire.actWord w && w == w.toLower", "w == w.toLower"),
    "31q-without-wordOk": _replace("!wordOk a || resv.contains a", "resv.contains a"),
    "31r-without-head-words": _replace("mwords.contains a || fs.any (·.head.contains a)", "mwords.contains a"),
    "31k-before-31g": _moved(ROWS.index("31k"), ROWS.index("31g")),
    "stepBudget-1000000": _replace("def stepBudget : Nat := 2100000", "def stepBudget : Nat := 1000000", "read"),
    # The review's six of the same class (ap-2 review F7), as it wrote them; `_generated` makes each of them again.
    "31o-outer-markers-only": _replace("    for m in ms f do", '    for m in f.markers.filter (· ≠ "") do'),
    "31o-inner-modifiers-only": _replace("(ms f).find? (fun n => n != m", "f.mods.find? (fun n => n != m"),
    "31c-first-head-word": _replace("f.head.find? (!wordOk ·)", "(f.head.take 1).find? (!wordOk ·)"),
    "31r-first-head-word": _replace("fs.any (·.head.contains a)", "fs.any (fun f => (f.head.take 1).contains a)"),
    "31i-modifier-split": _replace("f.split.find? (!f.markers.contains ·)",
                                   "f.split.find? (!(f.markers ++ f.mods).contains ·)"),
    "31g-without-direct-object": _replace("firstDup f.markers", 'firstDup (f.markers.filter (· ≠ ""))'),
    # The review's two in an operand of `++` and in a list a function argument builds (ap-2 review F10), as it wrote
    # them; `_generated` makes them again (`first-only-each-wordsOf-1`, `first-only-f.mods-1`).
    "mwords-first-word-of-a-marker": _replace("fs.flatMap (fun f => (ms f).flatMap wordsOf)",
                                              "fs.flatMap (fun f => (ms f).flatMap (fun m => (wordsOf m).take 1))"),
    "ms-first-modifier-only": _replace("(f.markers ++ f.mods).filter", "(f.markers ++ f.mods.take 1).filter"),
    # The review's four at the other end of a list (ap-2 review F11), as it wrote them; `_generated` makes each of them
    # again (`REVIEW_F11`).
    "31f-g-not-first": _replace("if let some g := fs.find?", "if let some g := (fs.drop 1).find?"),
    "31f-f-not-last": _replace("  for f in fs do\n    if let some g :=", "  for f in fs.dropLast do\n    if let some g :="),
    "31s-f-not-first": _replace("  for f in fs do\n    if let some w := f.head.head?",
                                "  for f in fs.drop 1 do\n    if let some w := f.head.head?"),
    "31s-one-word-head": _replace("f.head.head?", "f.head.dropLast.head?"),
    # The review's four in `Term.accepts` (ap-2 review F13) and four case folds of a first letter only (F14), as it
    # wrote them; `_generated` makes each of them again (`REVIEW_F13`, `REVIEW_F14`).
    "accepts-adv-first-only": _replace("ws.contains v.toLower", "(ws.take 1).contains v.toLower"),
    "accepts-adv-last-only": _replace("ws.contains v.toLower", "(ws.reverse.take 1).contains v.toLower"),
    "accepts-fill-first-only": _replace("!ex.contains v.toLower", "!(ex.take 1).contains v.toLower"),
    "accepts-fill-last-only": _replace("!ex.contains v.toLower", "!(ex.reverse.take 1).contains v.toLower"),
    "accepts-kw-decapitalize": _replace("v.toLower == w", "v.decapitalize == w"),
    "accepts-adv-decapitalize": _replace("ws.contains v.toLower", "ws.contains v.decapitalize"),
    "accepts-fill-decapitalize": _replace("!ex.contains v.toLower", "!ex.contains v.decapitalize"),
    "wordOk-decapitalize": _replace("w == w.toLower", "w == w.decapitalize"),
    # The review's five in `Term.accepts` (ap-2 review F15), as it wrote them; the sweep makes each of them again
    # (`REVIEW_F15`); and F16's `firstDup` that names a later duplicate.
    "accepts-fixed-any-token": _replace("| .fixed, .fixed _ => true", "| .fixed, _ => true"),
    "accepts-comma-any-token": _replace("| .comma, .comma => true", "| .comma, _ => true"),
    "accepts-fixed-not-0": _replace("| .fixed, .fixed _ => true", "| .fixed, .fixed (_ + 1) => true"),
    "accepts-kw-own-prefix": _replace("v.toLower == w", "w.startsWith v.toLower"),
    "accepts-adv-own-prefix": _replace("ws.contains v.toLower", "ws.any (·.startsWith v.toLower)"),
    "firstDup-later-duplicate": _replace("if xs.contains x then some x else firstDup xs",
                                         "(firstDup xs).orElse fun _ => if xs.contains x then some x else none"),
    # The same kinds elsewhere: the other halves and word lists, and each limit one off.
    "31a-129-accepted": _replace("128 < fs.length", "129 < fs.length"),
    "wordOk-without-lower-case": _replace("VE.Norms.Wire.actWord w && w == w.toLower", "VE.Norms.Wire.actWord w"),
    "31q-without-reserved": _replace("!wordOk a || resv.contains a", "!wordOk a"),
    "31q-to-adverb-accepted": _replace("!wordOk a || resv.contains a", "!wordOk a || mresv.contains a"),
    "31r-without-marker-words": _replace("mwords.contains a || fs.any (·.head.contains a)",
                                         "fs.any (·.head.contains a)"),
    "31n-to-marker-refused": _replace("((ms f).flatMap wordsOf).find? mresv.contains",
                                      "((ms f).flatMap wordsOf).find? resv.contains"),
    "31s-any-head-word": _replace("if let some w := f.head.head? then",
                                  "if let some w := f.head.find? mwords.contains then"),
    "rawCap-257": _replace("def rawCap : Nat := 256", "def rawCap : Nat := 257", "read"),
    "maxReadings-65": _replace("def maxReadings : Nat := 64", "def maxReadings : Nat := 65", "read"),
    "stepBudget-2100001": _replace("def stepBudget : Nat := 2100000", "def stepBudget : Nat := 2100001", "read"),
    # Every D-31 row dropped, and every two adjacent rows swapped.
    **{f"{row}-dropped": _order(lambda n, i=i: [j for j in range(n) if j != i]) for i, row in enumerate(ROWS)},
    **{f"{ROWS[i]}-{ROWS[i + 1]}-swapped": _order(lambda n, i=i: [*range(i), i + 1, i, *range(i + 2, n)])
       for i in range(len(ROWS) - 1)},
    # Every list of 1.4's check cut to its first element, and every marker list swapped for another (F7).
    **_generated(),
    # Every match arm and every comparison of `Syntax.lean` and `Read.lean` changed in turn (F15).
    **_sweep(),
}


# The review's four (F11) and the generated mutant that makes each again.
REVIEW_F11 = {"31f-g-not-first": "without-first-fs-8", "31f-f-not-last": "without-last-fs-7",
              "31s-f-not-first": "without-first-fs-19", "31s-one-word-head": "without-last-f.head-6"}
# The review's four in `Term.accepts` (F13) and the generated mutant that makes each again.
REVIEW_F13 = {"accepts-adv-first-only": "first-only-ws-1", "accepts-adv-last-only": "last-only-ws-1",
              "accepts-fill-first-only": "first-only-ex-1", "accepts-fill-last-only": "last-only-ex-1"}
# The review's four case folds (F14), `decapitalize` folding the first letter only, and the generated one that folds
# the first letter only of the same fold.
REVIEW_F14 = {"accepts-kw-decapitalize": "case-first-only-v.toLower-1",
              "accepts-adv-decapitalize": "case-first-only-v.toLower-2",
              "accepts-fill-decapitalize": "case-first-only-v.toLower-3",
              "wordOk-decapitalize": "case-first-only-w.toLower-1"}

# The review's five (F15) and the sweep's mutant that makes each again: the same arm of `Term.accepts` changed, with the
# same answers (`test_the_sweep_covers_every_arm_and_comparison`).
REVIEW_F15 = {"accepts-fixed-any-token": "sweep-wildcard-Term.accepts-6",
              "accepts-comma-any-token": "sweep-wildcard-Term.accepts-8",
              "accepts-fixed-not-0": "sweep-index-succ-Term.accepts-1",
              "accepts-kw-own-prefix": "sweep-prefix-Term.accepts-1",
              "accepts-adv-own-prefix": "sweep-contains-prefix-Term.accepts-1"}


def _errors(out: str) -> list[str]:
    """The errors of an elaboration, each by its code (`lean.redundantMatchAlt`), `""` for one without a code."""
    return re.findall(r": error(?:\(([\w.]+)\))?:", out)


def _killed(out: str) -> bool:
    """Every error is a `#guard` that failed, and there is one."""
    return 0 < out.count(GUARD_FAILED) == len(_errors(out))


@pytest.fixture(scope="module")
def lake():
    path = shutil.which("lake")
    if path is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    return path


def _elaborate(lake: str, tmp_path, source: str) -> subprocess.CompletedProcess:
    file = tmp_path / "ActsMutant.lean"
    file.write_text(source)
    return subprocess.run([lake, "env", "lean", str(file)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)


def test_check_vocab_has_one_condition_per_d31_row_in_d31s_order():
    """The mutants are generated from `checkVocab`'s blocks: there is one per D-31 row, and block i raises row i's
    text (every fixed piece of it, between the placeholders)."""
    _, blocks, _ = _check_vocab(_sources()[0])
    rows = _d31()
    assert len(blocks) == len(rows)
    for (row, text), block in zip(rows, blocks):
        source = "\n".join(block)
        for piece in re.split(r"\{[a-z]\}", text):
            assert piece in source, (row, piece)


def test_the_unmutated_sources_elaborate_cleanly(lake, tmp_path):
    done = _elaborate(lake, tmp_path, _assemble(*_sources()))
    assert done.returncode == 0 and "error" not in done.stdout + done.stderr, done.stdout + done.stderr


@pytest.mark.parametrize("name", sorted(set(MUTANTS) - set(EQUIVALENT) - set(UNWRITABLE)))
def test_every_seeded_mutant_fails_a_fixture(lake, tmp_path, name):
    syntax, read, examples = _sources()
    mutated = MUTANTS[name](syntax, read)
    assert mutated != (syntax, read), f"{name} changes nothing"
    done = _elaborate(lake, tmp_path, _assemble(*mutated, examples))
    out = done.stdout + done.stderr
    assert done.returncode != 0, f"{name} survives every #guard"
    assert _killed(out), f"{name} fails before a #guard, or not only at #guards:\n{out}"


@pytest.mark.parametrize("name", sorted(UNWRITABLE))
def test_an_unwritable_mutant_is_refused_by_lean(lake, tmp_path, name):
    """A mutant listed as unwritable is refused by Lean for a redundant arm, and for nothing else but `#guard`s: if
    Lean accepts it, a fixture must kill it, and the list is wrong."""
    syntax, read, examples = _sources()
    done = _elaborate(lake, tmp_path, _assemble(*MUTANTS[name](syntax, read), examples))
    errors = _errors(done.stdout + done.stderr)
    assert "lean.redundantMatchAlt" in errors, f"{name} ({UNWRITABLE[name]}) is not refused:\n{done.stdout}"
    assert set(errors) <= {"lean.redundantMatchAlt", ""}, errors
    assert errors.count("") == (done.stdout + done.stderr).count(GUARD_FAILED), done.stdout


def test_the_killed_check_counts_errors_with_a_code():
    """An error with a code (`error(lean.redundantMatchAlt):`) is an error: a mutant that Lean refuses is not counted
    as killed by the `#guard`s that fail after it (the check before ap-2 review F15 counted only `: error:`)."""
    guard = f"F.lean:9:0: error: Expression\n  x == y\n{GUARD_FAILED}\n"
    assert _killed(guard) and not _killed("")
    assert not _killed("F.lean:3:2: error(lean.redundantMatchAlt): Redundant alternative\n" + guard)
    assert not _killed("F.lean:3:2: error: unknown identifier 'x'\n" + guard)


def test_the_sweep_covers_every_arm_and_comparison():
    """The sweep changes every match arm and every comparison of `Syntax.lean` and `Read.lean`'s definitions: each
    arm of `Term.accepts` has its pattern's arguments made `_` or its constructors swapped, and each comparison is
    negated; the review's five (F15) are made again, each changing the same line; every equivalent or unwritable mutant
    is the sweep's or generated."""
    syntax, read, _ = _sources()
    sweep = _sweep()
    for where, source in (("syntax", syntax), ("read", read)):
        text = _masked(source)
        for name, lo, hi in _definitions(source):
            comparisons = len(re.findall(r" (==|!=|≠) ", text[lo:hi]))
            assert len([n for n in sweep if n.startswith(f"sweep-negate-{name}-")]) == comparisons, name
            contains = len(re.findall(r"\.contains\b", text[lo:hi]))
            if "α" not in text[lo:text.index("\n", lo)]:
                assert len([n for n in sweep if n.startswith(f"sweep-contains-prefix-{name}-")]) == 2 * contains, name
    lo, hi = _span(_masked(syntax), "def Term.accepts ")
    arms = _arms(_masked(syntax), lo, hi)
    assert len(arms) == 8
    changed = {n.rsplit("-", 1)[0] for n in sweep if "-Term.accepts-" in n}
    assert {"sweep-wildcard-Term.accepts", "sweep-ctor-swap-Term.accepts", "sweep-drop-arm-Term.accepts",
            "sweep-arm-value-Term.accepts", "sweep-index-succ-Term.accepts", "sweep-index-0-Term.accepts",
            "sweep-wildcard-index-Term.accepts", "sweep-prefix-Term.accepts",
            "sweep-contains-prefix-Term.accepts"} <= changed
    for review, name in REVIEW_F15.items():
        lines = [[i for i, (a, b) in enumerate(zip(syntax.split("\n"), MUTANTS[m](syntax, read)[0].split("\n")))
                  if a != b] for m in (review, name)]
        assert lines[0] == lines[1] and len(lines[0]) == 1, (review, name)
    assert set(UNWRITABLE) <= set(sweep)
    assert set(EQUIVALENT) <= set(sweep) | set(_generated())


def test_the_generated_mutants_cover_every_list_of_the_check():
    """Each list of 1.4's check is cut once, the lists the review named are among them, and every equivalent mutant
    is a generated one."""
    syntax = _sources()[0]
    generated = _generated()
    terms, (atoms, bare) = _list_terms(syntax), _atoms(syntax)
    # F11: every list is cut in each way of `CUTS`, at both ends.
    for kind in CUTS:
        assert len([n for n in generated if n.startswith(f"{kind}-") and not n.startswith(f"{kind}-each-")]) == \
            len(terms), kind
        assert len([n for n in generated if n.startswith(f"{kind}-each-")]) == len(bare) > 0, kind
    # The review's four are generated: each is the same source as its generated mutant, up to parentheses.
    syntax_read = _sources()[:2]
    for review, name in {**REVIEW_F11, **REVIEW_F13}.items():
        same = [re.sub(r"[()]", "", MUTANTS[m](*syntax_read)[0]) for m in (review, name)]
        assert same[0] == same[1], (review, name)
    # F14: each of the review's folds is cut by a generated mutant at the same fold, the only one on its line.
    for review, name in REVIEW_F14.items():
        changed = [[i for i, (a, b) in enumerate(zip(syntax.split("\n"), MUTANTS[m](*syntax_read)[0].split("\n")))
                    if a != b] for m in (review, name)]
        assert changed[0] == changed[1] and len(changed[0]) == 1, (review, name)
        assert syntax.split("\n")[changed[0][0]].count("toLower") == 1, review
    # F13: every definition of `Syntax.lean` is in scope, `Term.accepts` among them, and its two lists are cut.
    assert set(SCOPE) == {f"def {n} " for n in re.findall(r"^def ([\w.]+)", syntax, re.M)} >= {"def Term.accepts "}
    assert {syntax[s:e] for s, e in terms} >= {"ws", "ex"}
    # F14: every case fold is cut in each way of `CASE_CUTS`.
    folds = _folds(syntax)
    assert [m.group() for m in folds] == ["v.toLower", "v.toLower", "v.toLower", "w.toLower"]
    for kind in CASE_CUTS:
        assert len([n for n in generated if n.startswith(f"case-{kind}-")]) == len(folds), kind
    for term in ("f.head", "·.head", "f.markers", "f.split", "f.mods", "(ms f)", "ms f", "fs", "V.adverbs", "mwords",
                 "g.head", "wordsOf m", "V.frames", "Lexical.clauseWords", '["and", "or", "nor", "to", "be"]',
                 "(ms f).flatMap wordsOf"):
        assert any(syntax[s:e] == term for s, e in terms), term
    # F10: both operands of `ms f`'s `++`, and each `wordsOf` a `flatMap` takes, are cut.
    line = syntax.index("  let ms ")
    assert {syntax[s:e] for s, e in terms if line < s < syntax.index("\n", line)} >= {"f.markers", "f.mods"}
    assert {syntax[s:e] for s, e in bare} == {"wordsOf"} and len(bare) == syntax.count("flatMap wordsOf")
    # Every occurrence of a list-valued name is cut where it stands, alone or in parentheses.
    for s, e in atoms:
        assert (s, e) in terms or (s - 1, e + 1) in terms, syntax[s:e]
    assert {n for n in EQUIVALENT if not n.startswith("sweep-")} <= set(generated)


def test_the_list_valued_names_are_read_from_the_declarations():
    """`_list_names` types the names of `Syntax.lean` from their declarations: every list field, every definition whose
    result is a list (not `firstDup`, which takes one), every let of `checkVocab` bound to a list (not `hd`) and every
    name a match arm binds to a constructor's `List` argument (`ws` and `ex` of `Term.accepts`, not `w` or `v`)."""
    syntax = _sources()[0]
    fields, defs, lets = _list_names(syntax)
    assert fields == {"head", "markers", "split", "mods", "frames", "adverbs"}
    assert defs == {"joinWords": 0, "clauseWords": 0, "wordsOf": 1}
    assert lets == {"fs": 0, "resv": 0, "mresv": 0, "ms": 1, "mwords": 0, "ws": 0, "ex": 0}
    assert {c: p for c, p in _list_fields_of_constructors(syntax).items() if p} == {"adv": [0], "fill": [0]}


@pytest.mark.parametrize("name", sorted(EQUIVALENT))
def test_an_equivalent_mutant_elaborates_and_passes_every_fixture(lake, tmp_path, name):
    """A mutant listed as equivalent changes the source and still passes: if a fixture kills it, it was not
    equivalent, and the list is wrong."""
    syntax, read, examples = _sources()
    mutated = MUTANTS[name](syntax, read)
    assert mutated != (syntax, read)
    done = _elaborate(lake, tmp_path, _assemble(*mutated, examples))
    assert done.returncode == 0, f"{name} ({EQUIVALENT[name]}) fails:\n{done.stdout + done.stderr}"
