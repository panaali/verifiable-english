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

MUTANTS = {
    # The review's seven (ap-2 review F1).
    "31a-128-refused": _replace("128 < fs.length", "128 ≤ fs.length"),
    "31d-to-head-accepted": _replace("f.head.find? resv.contains", "f.head.find? mresv.contains"),
    "wordOk-without-actWord": _replace("VE.Norms.Wire.actWord w && w == w.toLower", "w == w.toLower"),
    "31q-without-wordOk": _replace("!wordOk a || resv.contains a", "resv.contains a"),
    "31r-without-head-words": _replace("mwords.contains a || fs.any (·.head.contains a)", "mwords.contains a"),
    "31k-before-31g": _moved(ROWS.index("31k"), ROWS.index("31g")),
    "stepBudget-1000000": _replace("def stepBudget : Nat := 2100000", "def stepBudget : Nat := 1000000", "read"),
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


@pytest.mark.parametrize("name", sorted(MUTANTS))
def test_every_seeded_mutant_fails_a_fixture(lake, tmp_path, name):
    syntax, read, examples = _sources()
    mutated = MUTANTS[name](syntax, read)
    assert mutated != (syntax, read), f"{name} changes nothing"
    done = _elaborate(lake, tmp_path, _assemble(*mutated, examples))
    out = done.stdout + done.stderr
    assert done.returncode != 0, f"{name} survives every #guard"
    assert out.count(": error:") == out.count(GUARD_FAILED) > 0, f"{name} fails before a #guard:\n{out}"
