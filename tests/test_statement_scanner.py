"""The shared declaration scanner of the statement gates reads a declaration's extent as Lean does (review sc-2d-f1 F2).

Every statement gate (RD-1 to RD-6, RD-9/SC-1, PC-3, PC-9, PC-2a and the scope 5.4 gate) reads Lean declarations
through `tools/check_readings_defaults_statements.py`'s `declarations`. A declaration runs to the next Lean command
at column 0 in code: a blank line or a comment inside it never ends it, a declaration inside a comment is not one, and
a `--` or `/-` inside a string or character literal is not a comment.
"""

from __future__ import annotations

import pytest

from tools import check_pc3_statements as PC3
from tools import check_readings_defaults_statements as RD

SCANNERS = {"rd": lambda text: RD.declarations(text, statements_only=True), "pc3": PC3.declarations}

# (Lean source, the declarations the scanner must read from it)
CASES = {
    "blank line in a body": ("def P : Prop :=\n  True\n\n  ∧ False\n\ntheorem t : P := sorry\n",
                             {("def", "P"): ["def P : Prop := True ∧ False"], ("theorem", "t"): ["theorem t : P"]}),
    "blank line in a statement": ("theorem t (a : Nat)\n\n    (b : Nat) : a = b\n\n  ∨ False := by\n  sorry\n",
                                  {("theorem", "t"): ["theorem t (a : Nat) (b : Nat) : a = b ∨ False"]}),
    "comments in a body": ("def P : Prop :=\n  True\n-- c\n  ∧ /- d -/ False\n/- e\n/- f -/ -/\n  ∧ True\nend X\n",
                           {("def", "P"): ["def P : Prop := True ∧ False ∧ True"]}),
    "column-0 continuation": ("def P : Prop :=\nTrue\n∧ False\n", {("def", "P"): ["def P : Prop := True ∧ False"]}),
    "commented-out declaration": ("/-\ntheorem t : True := trivial\n-/\n-- def P : Prop := True\n", {}),
    "declaration in a doc comment": ("/-- doc\ntheorem t : True := trivial\n-/\ndef P : Prop := True\n",
                                     {("def", "P"): ["def P : Prop := True"]}),
    "comment marks in literals": ('def s : String :=\n  "a -- b /- c"\n\n  ++ r#"d "-- e"#\n'
                                  "def c : List Char :=\n  ['\"', '-', c']\n\n  ++ []\n",
                                  {("def", "s"): ['def s : String := "a -- b /- c" ++ r#"d "-- e"#'],
                                   ("def", "c"): ["def c : List Char := ['\"', '-', c'] ++ []"]}),
    "commands end it": ("def P : Prop := True\n/-- doc -/\ndef Q : Prop := True\n@[simp]\ntheorem t : Q := trivial\n"
                        "set_option x 1 in\ndef R : Prop := True\nattribute [simp] R\n#check R\n",
                        {("def", "P"): ["def P : Prop := True"], ("def", "Q"): ["def Q : Prop := True"],
                         ("theorem", "t"): ["theorem t : Q"], ("def", "R"): ["def R : Prop := True"]}),
}


@pytest.mark.parametrize("scanner", SCANNERS)
@pytest.mark.parametrize("case", CASES)
def test_the_scanner_reads_a_declaration_as_lean_does(scanner, case):
    source, expected = CASES[case]
    assert SCANNERS[scanner](source) == expected


def test_the_span_ends_at_the_last_code_of_the_declaration():
    """`span` leaves out the trailing blank lines and comments, so a change appended to it lands in the declaration."""
    source = "def P : Prop :=\n  True\n\n  ∧ False\n\n-- c\n\ntheorem t : P := sorry\n"
    start, stop = RD.span(source, "def", "P")
    assert source[start:stop] == "def P : Prop :=\n  True\n\n  ∧ False"
    with pytest.raises(KeyError):
        RD.span(source, "def", "Q")
