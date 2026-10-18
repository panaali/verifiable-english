"""Seeded mutants of the act grammar's vocabulary check and limits each fail a fixture (ap-2 review F1).

`lean/VE/Acts/GrammarExamples.lean` pins `checkVocab` (spec 1.4, the texts and order of D-31) and the limits of D2
with `#guard`s. The review found seven mutants that kept every guard passing: 128 frames refused, *to* accepted as a
head word, `wordOk` without `actWord`, 31q without `wordOk`, 31r without its head-word half, 31k checked before 31g,
and a step budget of 1,000,000. This test plants those seven, the other halves and limits of the same kind, and a
mutant for every way a D-31 row or its place can be lost, generated from `checkVocab`'s own source: each condition
dropped, and each two adjacent conditions swapped (a permutation that is not the identity swaps some adjacent pair).

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
    return tuple((ACTS / f"{name}.lean").read_text() for name in ("Syntax", "Read", "GrammarExamples"))


def _split_imports(text: str) -> tuple[list[str], str]:
    lines = text.split("\n")
    imports = [line for line in lines if line.startswith("import ")]
    return imports, "\n".join(line for line in lines if not line.startswith("import "))


def _assemble(syntax: str, read: str, examples: str) -> str:
    """One file: the three modules' bodies, with the imports they take from outside `VE.Acts`, and no proofs."""
    read = read[:read.index("section Proofs")] + "end VE.Acts\n"
    imports, bodies = [], []
    for text in (syntax, read, examples):
        own, body = _split_imports(text)
        imports += [line for line in own if not line.startswith("import VE.Acts.") and line not in imports]
        bodies.append(body)
    return "\n".join(imports) + "\n" + "\n".join(bodies)


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

# The definitions of 1.4 whose lists the generated mutants below cut or swap.
SCOPE = ("def wordsOf ", "def firstDup ", "def checkVocab ")
# A method on a list, and a position that takes a list as its argument.
LIST_METHOD = re.compile(r"\.(find\?|any|all|contains|isPrefixOf|isEmpty|flatMap|map|filter|length|head\?)(?![\w?])")
LIST_ARGUMENT = re.compile(r"\bfor \w+ in |\bfirstDup |\.isPrefixOf |\.intercalate ")
NAME = "._·?'"
# A frame's marker lists, as `checkVocab` writes them (`ms f` is the two without `""`); each stands for the others.
SIBLINGS = ["(f.markers ++ f.mods)", '(f.markers.filter (· ≠ ""))', "(ms f)", "f.markers", "f.split", "f.mods"]
SIBLING = re.compile("|".join([re.escape(s) for s in SIBLINGS[:3]] + [r"\bms f\b"] +
                              [rf"\b{re.escape(s)}\b" for s in SIBLINGS[3:]]))


def _span(text: str, start: str) -> tuple[int, int]:
    """Where the definition that begins with `start` is: its first line to the next line that is not indented."""
    lines, offset = text.split("\n"), 0
    for i, line in enumerate(lines):
        if line.startswith(start):
            end = next(k for k in range(i + 1, len(lines)) if not lines[k].startswith(" "))
            return offset, offset + sum(len(line) + 1 for line in lines[i:end])
        offset += len(line) + 1
    raise AssertionError(f"no {start!r}")


def _term_before(text: str, end: int) -> int:
    """The start of the term that ends at `end`: a balanced group, or a name such as `f.head` or `·.head`."""
    if text[end - 1] == ")":
        depth, i = 0, end - 1
        while (depth := depth + {")": 1, "(": -1}.get(text[i], 0)) != 0:
            i -= 1
        return i
    i = end
    while text[i - 1].isalnum() or text[i - 1] in NAME:
        i -= 1
    return i


def _term_after(text: str, start: int) -> int:
    """The end of the term that starts at `start`: a balanced group, an application up to `do`, or a name."""
    if text[start] == "(":
        depth, i = 0, start
        while (depth := depth + {"(": 1, ")": -1}.get(text[i], 0)) != 0:
            i += 1
        return i + 1
    if text[start - 3:start] == "in ":
        return text.index(" do", start)
    i = start
    while text[i].isalnum() or text[i] in NAME:
        i += 1
    return i


def _list_terms(syntax: str) -> list[tuple[int, int]]:
    """Every list the definitions of `SCOPE` range over: each receiver of a list method and each list argument, but not
    the argument of a definition's own recursive call (Lean refuses a recursion whose argument does not shrink)."""
    terms = set()
    for scope in SCOPE:
        lo, hi = _span(syntax, scope)
        terms |= {(_term_before(syntax, m.start()), m.start()) for m in LIST_METHOD.finditer(syntax, lo, hi)}
        terms |= {(m.end(), _term_after(syntax, m.end())) for m in LIST_ARGUMENT.finditer(syntax, lo, hi)
                  if m.group() != scope.split()[1] + " "}
    return sorted((start, end) for start, end in terms if start < end)


def _first_only(term: str) -> str:
    """`term` cut to its first element. A `·` term stays the function's argument, so it is piped."""
    if term.startswith("·"):
        return f"{term}.take 1 |>"
    whole = term.startswith("(") and _term_after(term, 0) == len(term)
    return f"({term if whole or ' ' not in term else f'({term})'}.take 1)"


def _slug(term: str) -> str:
    return re.sub(r"[^A-Za-z0-9.]+", "-", term.replace("++", "and").replace("≠", "ne")).strip("-.")


def _at(start: int, end: int, new: str):
    def mutate(syntax: str, read: str) -> tuple[str, str]:
        return syntax[:start] + new + syntax[end:], read
    return mutate


def _generated() -> dict:
    """Two kinds of mutant for every list of 1.4's check, numbered in source order within a name:

    - **first only** (ap-2 review F7: 31c and 31r read only a head's first word): each list cut to its first element,
      so a condition must be pinned with its fault in a later element (a later word, marker, frame or adverb);
    - **another marker list** (F7: 31o over markers only, 31i over modifiers too, 31g without `""`): each of a
      frame's marker lists replaced by each of the others, so a condition must be pinned on the list 1.4 names."""
    syntax = _sources()[0]
    mutants: dict = {}

    def add(name: str, mutate) -> None:
        k = sum(1 for other in mutants if other.rsplit("-", 1)[0] == name)
        mutants[f"{name}-{k + 1}"] = mutate

    for start, end in _list_terms(syntax):
        add(f"first-only-{_slug(syntax[start:end])}", _at(start, end, _first_only(syntax[start:end])))
    lo, hi = _span(syntax, "def checkVocab ")
    for m in SIBLING.finditer(syntax, lo, hi):
        own = "(ms f)" if m.group() == "ms f" else m.group()
        defines_ms = syntax.startswith("  let ms ", syntax.rindex("\n", 0, m.start()) + 1)
        for other in SIBLINGS:
            if other != own and not (defines_ms and other == "(ms f)"):
                add(f"{_slug(own)}-as-{_slug(other)}", _at(m.start(), m.end(), other))
    return mutants


# Generated mutants that change no answer of `checkVocab`, so no fixture can kill them, each with the reason.
EQUIVALENT: dict[str, str] = {
    "first-only-head-1": "31b: a head's first word is absent exactly when the head is empty",
    "first-only-f.head-5": "31s: the first word of a head's first word is its first word",
    "ms-f-as-f.markers-and-f.mods-1": "the marker words: `\"\"` has no words, so it adds none",
    "ms-f-as-f.markers-and-f.mods-3": "31m: `\"\"` has no words, so it adds no word to check",
    "ms-f-as-f.markers-and-f.mods-4": "31n: `\"\"` has no words, so it adds no word to check",
    "ms-f-as-f.markers-and-f.mods-6": "31o: no marker begins `\"\"`, since 31l refused every other marker without words",
    "f.markers-as-f.markers.filter-ne-3": "31k: 31j refused an empty modifier marker, so `\"\"` matches none",
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
}


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


@pytest.mark.parametrize("name", sorted(set(MUTANTS) - set(EQUIVALENT)))
def test_every_seeded_mutant_fails_a_fixture(lake, tmp_path, name):
    syntax, read, examples = _sources()
    mutated = MUTANTS[name](syntax, read)
    assert mutated != (syntax, read), f"{name} changes nothing"
    done = _elaborate(lake, tmp_path, _assemble(*mutated, examples))
    out = done.stdout + done.stderr
    assert done.returncode != 0, f"{name} survives every #guard"
    assert out.count(": error:") == out.count(GUARD_FAILED) > 0, f"{name} fails before a #guard:\n{out}"


def test_the_generated_mutants_cover_every_list_of_the_check():
    """Each list of 1.4's check is cut once, the lists the review named are among them, and every equivalent mutant
    is a generated one."""
    syntax = _sources()[0]
    generated = _generated()
    assert len([n for n in generated if n.startswith("first-only-")]) == len(_list_terms(syntax))
    for term in ("f.head", "·.head", "f.markers", "f.split", "f.mods", "(ms f)", "ms f", "fs", "V.adverbs", "mwords"):
        assert any(syntax[s:e] == term for s, e in _list_terms(syntax)), term
    assert set(EQUIVALENT) <= set(generated)


@pytest.mark.parametrize("name", sorted(EQUIVALENT))
def test_an_equivalent_mutant_elaborates_and_passes_every_fixture(lake, tmp_path, name):
    """A mutant listed as equivalent changes the source and still passes: if a fixture kills it, it was not
    equivalent, and the list is wrong."""
    syntax, read, examples = _sources()
    mutated = MUTANTS[name](syntax, read)
    assert mutated != (syntax, read)
    done = _elaborate(lake, tmp_path, _assemble(*mutated, examples))
    assert done.returncode == 0, f"{name} ({EQUIVALENT[name]}) fails:\n{done.stdout + done.stderr}"
