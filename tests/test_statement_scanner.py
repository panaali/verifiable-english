"""The shared declaration scanner of the statement gates reads a declaration's extent as Lean does (review sc-2d-f1 F2).

Every statement gate (RD-1 to RD-6, RD-9/SC-1, PC-3, PC-9, PC-2a and the scope 5.4 gate) reads Lean declarations
through `tools/check_readings_defaults_statements.py`'s `declarations`. A declaration runs to the next Lean command
keyword at column 0 in code: a blank line or a comment of any kind inside it, a doc comment `/-- -/` or `/-! -/` at
column 0 too (review sc-2d-f1 F3), never ends it, nor does a `|` constructor line or a structure field line at column
0; a declaration inside a comment is not one, and a `--` or `/-` inside a string or character literal is not a
comment. The one case that still ends a declaration early is a term line at column 0 that starts with `#` or `@[`
(an array literal `#[..]`), which is read as a command (`#check`, `@[simp]`): the DRI ruling on F3 grades it C.
"""

from __future__ import annotations

import pytest

from tools import check_pc3_statements as PC3
from tools import check_readings_defaults_statements as RD

SCANNERS = {"rd": lambda text: RD.declarations(text, statements_only=True, kinds=PC3.KINDS),
            "pc3": PC3.declarations}

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
    # Review sc-2d-f1 F3: Lean reads a doc comment at column 0 before a constructor or a field as its doc, inside the
    # declaration (checked with `lake env lean`), so the constructor or field after it is compared.
    "doc comment before a constructor": ("inductive I\n  | a | b\n/-- doc -/\n  | extra\n/-- doc -/\n| more\n"
                                         "  deriving Repr\n\ndef P : Prop := True\n",
                                         {("inductive", "I"): ["inductive I | a | b | extra | more deriving Repr"],
                                          ("def", "P"): ["def P : Prop := True"]}),
    "doc comment before a column-0 field": ("structure S where\n/-- doc -/\nx : Nat\n/-- doc -/\ny : Nat\n"
                                            "/-- doc -/\nz : Nat\n\ntheorem t : True := trivial\n",
                                            {("structure", "S"): ["structure S where x : Nat y : Nat z : Nat"],
                                             ("theorem", "t"): ["theorem t : True"]}),
    # Lean ends a term at a `/--` or a `/-!`; the scanner drops it as a comment and reads on, so text after it is
    # compared (longer, never shorter).
    "doc comments in a body": ("def P : Prop :=\n  True\n/-- doc -/\n  ∧ False\n/-! note -/\n∧ True\n",
                               {("def", "P"): ["def P : Prop := True ∧ False ∧ True"]}),
}

# The named exception of the records: a term line at column 0 that starts with `#` or `@[` is read as a command.
EARLY_ENDS = {"array literal": ("def a : Array Nat :=\n#[1]\n", {("def", "a"): ["def a : Array Nat :="]}),
              "attribute-like line": ("def P : Prop :=\n@[x] True\n", {("def", "P"): ["def P : Prop :="]})}


@pytest.mark.parametrize("scanner", SCANNERS)
@pytest.mark.parametrize("case", CASES)
def test_the_scanner_reads_a_declaration_as_lean_does(scanner, case):
    source, expected = CASES[case]
    assert SCANNERS[scanner](source) == expected


@pytest.mark.parametrize("case", EARLY_ENDS)
def test_the_records_name_the_one_column_0_line_that_ends_a_declaration_early(case):
    """The records say what the scanner does: a column-0 `#` or `@[` line ends a declaration (a C note on F3)."""
    source, expected = EARLY_ENDS[case]
    assert PC3.declarations(source) == expected


@pytest.mark.parametrize("command", RD.COMMANDS)
def test_every_command_ends_a_declaration_after_a_doc_comment(command):
    """A doc comment is not a command, so the command after it is what ends the declaration before it, for every
    command the scanner lists (the doc comment is dropped)."""
    word = command.replace(r"\s+", " ")
    source = f"def P : Prop :=\n  True\n/-- doc -/\n{word} x\n"
    assert PC3.declarations(source)[("def", "P")] == ["def P : Prop := True"]


def test_the_span_ends_at_the_last_code_of_the_declaration():
    """`span` leaves out the trailing blank lines and comments, so a change appended to it lands in the declaration."""
    source = "def P : Prop :=\n  True\n\n  ∧ False\n\n-- c\n\n/-- doc of t -/\ntheorem t : P := sorry\n"
    start, stop = RD.span(source, "def", "P")
    assert source[start:stop] == "def P : Prop :=\n  True\n\n  ∧ False"
    with pytest.raises(KeyError):
        RD.span(source, "def", "Q")


def _with_doc_suffix(source: str, kind: str, name: str) -> str:
    """`source` with a column-0 doc comment and a column-0 line added at the end of the compared text of `kind name`:
    a constructor `| extra` to an inductive, a field `extra : Nat` to a structure (before its `deriving` clause),
    `∧ True` to a definition, and to a theorem's statement before its proof's `:=`."""
    start, stop = RD.span(source, kind, name)
    code = RD.lex(source)[0][start:stop]
    if kind == "theorem":
        at = start + RD.proof_cut(code)
    elif "\n  deriving" in code:
        at = start + code.index("\n  deriving")
    else:
        at = stop
    suffix = {"inductive": "| extra", "structure": "extra : Nat"}.get(kind, "∧ True")
    return source[:at] + f"\n/-- doc -/\n{suffix}\n" + source[at:]


def _pc3_built():
    return sorted(key for key in PC3.approved() if key[1] not in PC3.LATER)


def _pc3_sources(tmp_path, kind=None, name=None):
    """PC-3's sources copied to `tmp_path`, the one that holds `kind name` (if any) changed by `_with_doc_suffix`."""
    sources = []
    for source in PC3.SOURCES:
        text = source.read_text()
        if (kind, name) in PC3.declarations(text):
            text = _with_doc_suffix(text, kind, name)
        sources.append(tmp_path / source.name)
        sources[-1].write_text(text)
    return sources


def test_probe_f3_a_constructor_after_a_column_0_doc_comment_is_compared(tmp_path, capsys):
    """PROBE F3 (review sc-2d-f1): a constructor added after a column-0 doc comment inside `inductive Interface` is
    read as part of it, and the PC-3 gate fails by name."""
    source = PC3.SOURCES[0].read_text()
    k = "| pack (id : String) | outside\n"
    assert k in source
    changed = source.replace(k, k + "/-- doc -/\n  | extra\n", 1)
    assert "extra" in PC3.declarations(changed)[("inductive", "Interface")][0]
    sources = _pc3_sources(tmp_path)
    sources[0].write_text(changed)
    assert PC3.main(sources) == 1
    assert "Interface: inductive differs" in capsys.readouterr().out


@pytest.mark.parametrize("kind, name", _pc3_built(), ids=lambda v: str(v))
def test_pc3_compares_a_line_after_a_column_0_doc_comment(tmp_path, capsys, kind, name):
    """The class of F3 over every declaration PC-3 compares: a column-0 doc comment never hides the line after it.
    The scanner reads the added line inside the declaration (a declaration cut short before its `deriving` clause
    would also differ, so the gate's answer alone does not show it)."""
    sources = _pc3_sources(tmp_path, kind, name)
    texts = [t for source in sources for t in PC3.declarations(source.read_text()).get((kind, name), [])]
    assert len(texts) == 1 and ("extra" if kind in ("inductive", "structure") else "∧ True") in texts[0]
    assert PC3.main(sources) == 1
    assert f"{name}: {kind} differs" in capsys.readouterr().out


def test_rd1_compares_a_column_0_field_after_a_column_0_doc_comment(tmp_path, capsys, monkeypatch):
    """F3's structure case through the RD-1 gate: a field added at column 0 after a column-0 doc comment in
    `structure NDoc` is compared."""
    path = tmp_path / "Unspecified.lean"
    path.write_text(_with_doc_suffix(RD.SOURCE.read_text(), "structure", "NDoc"))
    monkeypatch.setattr(RD, "SOURCE", path)
    assert RD.main() == 1
    assert "NDoc: structure differs" in capsys.readouterr().out
