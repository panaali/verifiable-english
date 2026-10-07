"""The spacing of the integer marks: Lean reads exactly the spacing Python reads (spec R1; english-lean-e2.md 13).

The E2.5 reverse corpus found Lean reading an integer mark glued to a word on the side away from its term
(`costs-limit`, `at least[budget - 24]`, `[a + b]and`), which Python refuses. The class is every spacing of
`[`, `]` and a sign next to a word or another mark, so this test takes texts with nested terms and, at every
integer mark, removes, adds or widens the whitespace on each side, and compares the two readers' verdicts and
formulas at the dispatched boundary.
"""

import re

import pytest

from conformance import english_lean_e2_evidence as E


SEEDS = [
    "Some fourth service costs [-budget + -5].",
    "Every service named S1 costs -[[budget + 1] - --limit].",
    "Twice the limit is at least [budget - -24].",
    "Either -8 is reserved or this is impossible, or both.",
    "If budget is at most [limit + 1], then -26 is more than -[--budget + 17].",
    "Every deployed service costs [[2 * budget] + -limit].",
    "Twice the limit is at most --budget.",
]
# The texts of the reverse corpus that Lean read and Python refused, one per shape.
FOUND = [
    "Both twice the limit is at least[budget - -24]and twice the limit is at most -6.",
    "Some fourth service costs-limit.",
    "Every service named S1 costs-11.",
    "Either-8 is reserved or this is impossible, or both.",
    "There is a third service that costs-[[-limit - -10] + -budget].",
    "-26 is more than-[--budget + 17].",
]


@pytest.fixture(scope="module")
def order():
    if not E.CONFIGS:
        E._setup()
        E.CONFIGS.extend(E.configurations())
    return next(i for i, c in enumerate(E.CONFIGS) if c[0] == "order")


def mutants(text: str) -> list[str]:
    """At every `[`, `]` and `-`, each side's whitespace removed, added or widened."""
    out = []
    for m in re.finditer(r"[\[\]-]", text):
        for side in (m.start(), m.end()):
            left, right = text[:side], text[side:]
            if left.endswith(" "):
                out.append(left.rstrip(" ") + right)
                out.append(left + " " + right)
            elif right.startswith(" "):
                out.append(left + right.lstrip(" "))
            elif 0 < side < len(text):
                out.append(left + " " + right)
    return sorted(set(out) - {text})


def test_the_mutants_cover_every_side_of_every_mark():
    found = mutants(SEEDS[0])
    assert {"Some fourth service costs [ -budget + -5].", "Some fourth service costs[-budget + -5].",
            "Some fourth service costs [-budget + -5] .", "Some fourth service costs [-budget +-5].",
            "Some fourth service costs [-budget + -5 ]."} <= set(found)
    assert "Every service named S1 costs -[[budget + 1]- --limit]." in mutants(SEEDS[1])


def test_lean_reads_the_spacing_of_the_integer_marks_that_python_reads(order):
    texts = SEEDS + FOUND + [m for s in SEEDS + FOUND for m in mutants(s)]
    assert len(texts) > 100
    lean = E.lean_outcomes(order, texts)
    differences = []
    for text, answer in zip(texts, lean, strict=True):
        python = E.python_outcome((order, text))
        classes, right = E.compare(python, answer)
        if {"verdict", "formulas"} & set(classes):
            differences.append((text, python.get("code"), right.get("verdict")))
    assert differences == []
    # The seeds are read; the texts the reverse corpus found are not.
    assert [a["status"] for a in lean[:len(SEEDS)]] == ["one"] * len(SEEDS)
    assert [a["status"] for a in lean[len(SEEDS):len(SEEDS) + len(FOUND)]] == ["none"] * len(FOUND)
