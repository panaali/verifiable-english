"""The question-answering statement gate reads Lean declarations with the shared scanner (item qa-stmt-scanner).

`tools/question_statements.py` compares Q1's and Q2's Lean declarations with the approved text of
docs/spec/question-answering.md 5.1 and 5.2. Its private line scanner ended a definition, a structure or an inductive
at a blank line or a column-0 `/--` line, so a changed line after either was not compared (review sc-2d-f1, "Outside
this item"). It now reads both sides with `check_readings_defaults_statements.declarations`: a declaration runs to the
next Lean command at column 0. Each probe below changes one approved declaration in a copy of the Lean sources, after
a blank line or after a column-0 doc comment, and the gate must fail by name. The shared `proof_cut` keeps a `let`'s
or a `have`'s own `:=` in the statement, so the text after `let span := ..` in a Q1 statement is compared too.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest

from tools import check_readings_defaults_statements as RD

ROOT = Path(__file__).resolve().parents[1]
SPEC = (ROOT / "docs/spec/question-answering.md").read_text()
Q1_SPEC = SPEC.split("### 5.1 Q1", 1)[1].split("### 5.2 Q2", 1)[0]
Q2_SPEC = SPEC.split("### 5.2 Q2", 1)[1].split("## 6. Limits", 1)[0]


def _approved(section: str, kinds: tuple[str, ...]) -> dict[tuple[str, str], list[str]]:
    """The approved declarations of `kinds` in a spec section's ```lean block, read by the shared scanner."""
    return RD.declarations(section.split("```lean", 1)[1].split("```", 1)[0], True, kinds)


Q1_PREDICATES = sorted(_approved(Q1_SPEC, ("def",)))
Q2_TYPES = sorted(_approved(Q2_SPEC, ("structure", "inductive")))
# The approved Q2 definitions with a body (a signature-only one is checked by Lean, not by its text).
Q2_BODIES = sorted(key for key, texts in _approved(Q2_SPEC, ("def",)).items() if ":=" in texts[0] or "|" in texts[0])
BLANK, DOC = "\n\n", "\n/-- doc -/\n"


def _tool():
    spec = importlib.util.spec_from_file_location("question_statements", ROOT / "tools/question_statements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _with_suffix(source: str, kind: str, name: str, gap: str) -> str:
    """`source` with `gap` (a blank line or a column-0 doc comment) and one more line at the end of the compared text
    of `kind name`: a field `extra : Nat` to a structure and a constructor `| extra` to an inductive (before a
    `deriving` clause), `∧ False` to a definition, and to a theorem's statement before its proof's `:=`."""
    start, stop = RD.span(source, kind, name)
    code = RD.lex(source)[0][start:stop]
    if kind == "theorem":
        at = start + len(code[:RD.proof_cut(code)].rstrip())
    elif "\n  deriving" in code:
        at = start + code.index("\n  deriving")
    else:
        at = stop
    line = {"structure": "extra : Nat", "inductive": "| extra"}.get(kind, "  ∧ False")
    return source[:at] + gap + line + "\n" + source[at:]


def _copies(tmp_path: Path, sources: list[Path], kind: str, name: str, gap: str) -> list[Path]:
    """`sources` copied under `tmp_path`, the file that declares `kind name` changed by `_with_suffix`."""
    out, changed = [], 0
    for source in sources:
        text = source.read_text()
        if (kind, name) in RD.declarations(text, True, (kind,)):
            text, changed = _with_suffix(text, kind, name, gap), changed + 1
        target = tmp_path / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        out.append(target)
    assert changed == 1, f"{kind} {name} is declared {changed} times"
    return out


def _q1_fails(tool, monkeypatch, capsys, sources) -> str:
    """Run the Q1 gate on `sources`; it must fail (exit 1). Its output."""
    monkeypatch.setattr(tool, "SOURCES", sources)
    monkeypatch.setattr(sys, "argv", ["question_statements.py"])
    with pytest.raises(SystemExit) as stop:
        tool.main()
    assert stop.value.code == 1
    return capsys.readouterr().out


def test_the_probe_sets_are_the_approved_ones():
    assert len(Q1_PREDICATES) == 5 and len(Q2_TYPES) == 14 and len(Q2_BODIES) == 37


@pytest.mark.parametrize("gap", [BLANK, DOC], ids=["blank line", "doc comment"])
@pytest.mark.parametrize("kind, name", Q1_PREDICATES, ids=lambda v: str(v))
def test_q1_compares_a_predicate_line_after_a_gap(tmp_path, monkeypatch, capsys, kind, name, gap):
    """PROBE: a line added to an approved Q1 predicate after a blank line or a column-0 doc comment is compared."""
    tool = _tool()
    out = _q1_fails(tool, monkeypatch, capsys, _copies(tmp_path, tool.SOURCES, kind, name, gap))
    assert "Changed or missing predicates:" in out and name in out.split("Changed or missing predicates:", 1)[1]


@pytest.mark.parametrize("name", ["readQuestion_one", "mapSpan_valid"])
def test_q1_compares_a_statement_line_after_a_blank_line(tmp_path, monkeypatch, capsys, name):
    tool = _tool()
    out = _q1_fails(tool, monkeypatch, capsys, _copies(tmp_path, tool.SOURCES, "theorem", name, BLANK))
    assert f"Mismatched statements: {name}" in out


@pytest.mark.parametrize("name", ["mapSpan_valid", "mapSpan_codepoints_valid"])
def test_q1_compares_the_statement_after_a_let(tmp_path, monkeypatch, capsys, name):
    """The text after `let span := ..` in a Q1 statement is compared: the `let`'s `:=` does not end the statement."""
    tool = _tool()
    old = "span.2 ≤ q"
    out = []
    for source in tool.SOURCES:
        text = source.read_text()
        if ("theorem", name) in RD.declarations(text, True, ("theorem",)):
            start, stop = RD.span(text, "theorem", name)
            at = text.index(old, text.index("let span :=", start))
            assert at < stop
            text = text[:at] + "span.2 < q" + text[at + len(old):]
        out.append(tmp_path / source.name)
        out[-1].write_text(text)
    assert f"Mismatched statements: {name}" in _q1_fails(tool, monkeypatch, capsys, out)


@pytest.mark.parametrize("kind, name", Q2_TYPES, ids=lambda v: str(v))
def test_q2_compares_a_field_or_constructor_after_a_column_0_doc_comment(tmp_path, monkeypatch, capsys, kind, name):
    """PROBE: a field or constructor added at column 0 after a column-0 doc comment (Lean reads it inside the
    declaration, review sc-2d-f1 F3) in an approved Q2 structure or inductive is compared."""
    tool = _tool()
    monkeypatch.setattr(tool, "Q2_SOURCES", _copies(tmp_path, tool.Q2_SOURCES, kind, name, DOC))
    assert tool.q2(lean=False) == 1
    assert f"changed {name}: NOT LISTED" in capsys.readouterr().out


@pytest.mark.parametrize("kind, name", Q2_BODIES, ids=lambda v: str(v))
def test_q2_compares_a_definition_line_after_a_blank_line(tmp_path, monkeypatch, capsys, kind, name):
    """PROBE: a line added to an approved Q2 definition's body after a blank line is compared."""
    tool = _tool()
    monkeypatch.setattr(tool, "Q2_SOURCES", _copies(tmp_path, tool.Q2_SOURCES, kind, name, BLANK))
    assert tool.q2(lean=False) == 1
    assert f"changed {name}: NOT LISTED" in capsys.readouterr().out


COPY = "namespace Other\ndef HasReading : Prop := True\nend Other\n"


@pytest.mark.parametrize("where", ["same file before", "same file after", "other file before", "other file after"])
def test_a_name_declared_twice_equals_no_approved_text(tmp_path, monkeypatch, capsys, where):
    """A second copy of an approved predicate (another namespace, in the same file or another one, before or after
    the approved one) is compared too: the gate keeps no single copy and drops the other."""
    tool = _tool()
    sources = []
    for source in tool.SOURCES:
        text = source.read_text()
        if ("def", "HasReading") in RD.declarations(text, True, ("def",)):
            if where == "same file after":
                text += "\n" + COPY
            elif where == "same file before":
                at = text.rfind("\n\n", 0, RD.span(text, "def", "HasReading")[0]) + 2
                text = text[:at] + COPY + "\n" + text[at:]
        sources.append(tmp_path / source.name)
        sources[-1].write_text(text)
    other = tmp_path / "Other.lean"
    other.write_text("namespace VE.Question\n" + COPY + "end VE.Question\n")
    if where == "other file before":
        sources.insert(0, other)
    elif where == "other file after":
        sources.append(other)
    out = _q1_fails(tool, monkeypatch, capsys, sources)
    assert "HasReading" in out.split("Changed or missing predicates:", 1)[1]


def test_proof_cut_keeps_a_let_or_have_binding():
    for statement in ("theorem t : let s := 1\n  s = 1", "theorem t : have h : True := trivial\n  True",
                      "theorem t (n : Nat) : let a := n; let b := a\n  b = n"):
        assert RD.proof_cut(statement + " := by rfl") == len(statement) + 1
    assert RD.proof_cut("theorem letter : True := trivial") == len("theorem letter : True ")


# Review qa-stmt-scanner F1: a Lean source is read whole, never through the ```lean fences of its doc comments (only
# the spec is read from its fences). Each reader of a source is probed: a copy of the file that declares `kind name`
# opens with a module doc quoting the approved declaration in a ```lean fence, and the declaration itself changes.
Q1_THEOREMS = sorted(_approved(Q1_SPEC, ("theorem",)))
Q2_THEOREMS = sorted(_approved(Q2_SPEC, ("theorem",)))
FENCED = ([("q1", key) for key in Q1_THEOREMS + Q1_PREDICATES]
          + [("q2", key) for key in Q2_THEOREMS + Q2_BODIES + Q2_TYPES])


def _quote(text: str, kind: str, name: str) -> str:
    """A module doc that quotes the declaration `kind name` of `text` in a ```lean fence."""
    start, stop = RD.span(text, kind, name)
    return "/-! A quoted declaration:\n```lean\n" + text[start:stop].rstrip() + "\n```\n-/\n"


def _fenced_copies(tmp_path: Path, sources: list[Path], keys: list[tuple[str, str]], change: bool) -> list[Path]:
    """`sources` copied under `tmp_path`; each file opens with a module doc per declaration of `keys` it declares,
    quoting it in a ```lean fence, and, if `change` (one key), has that declaration changed by `_with_suffix`."""
    out, found = [], 0
    for source in sources:
        text = source.read_text()
        mine = [(kind, name) for kind, name in keys if (kind, name) in RD.declarations(text, True, (kind,))]
        quoted = "".join(_quote(text, kind, name) for kind, name in mine)
        if change and mine:
            text = _with_suffix(text, *mine[0], "\n")
        found += len(mine)
        target = tmp_path / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(quoted + text)
        out.append(target)
    assert found == len(keys), f"{keys}: {found} declarations found"
    return out


def _gate(tool, monkeypatch, capsys, part: str, sources: list[Path]) -> tuple[int, str]:
    """Run the Q1 or the Q2 text gate on `sources`: its exit code and output."""
    if part == "q2":
        monkeypatch.setattr(tool, "Q2_SOURCES", sources)
        code = tool.q2(lean=False)
    else:
        monkeypatch.setattr(tool, "SOURCES", sources)
        monkeypatch.setattr(sys, "argv", ["question_statements.py"])
        try:
            tool.main()
            code = 0
        except SystemExit as stop:
            code = stop.code
    return code, capsys.readouterr().out


@pytest.mark.parametrize("part", ["q1", "q2"])
def test_a_doc_fence_quoting_every_approved_declaration_changes_nothing(tmp_path, monkeypatch, capsys, part):
    """Every approved declaration quoted in a ```lean fence of its file's doc comments: the gate still passes, so a
    quote is never read as a second declaration either."""
    tool = _tool()
    sources = tool.SOURCES if part == "q1" else tool.Q2_SOURCES
    keys = [key for where, key in FENCED if where == part]
    code, out = _gate(tool, monkeypatch, capsys, part, _fenced_copies(tmp_path, sources, keys, False))
    assert code == 0, out


@pytest.mark.parametrize("part, key", FENCED, ids=lambda v: str(v))
def test_a_source_is_read_whole_not_through_a_doc_fence(tmp_path, monkeypatch, capsys, part, key):
    """PROBE F1: a changed approved declaration fails the gate by name although a doc comment of its file quotes the
    approved text in a ```lean fence: a source is read whole, its code compared, never the quote."""
    kind, name = key
    tool = _tool()
    sources = tool.SOURCES if part == "q1" else tool.Q2_SOURCES
    code, out = _gate(tool, monkeypatch, capsys, part, _fenced_copies(tmp_path, sources, [key], True))
    assert code == 1, out
    named = {"theorem": "Mismatched statements:" if part == "q1" else "Statements differing in text:",
             "def": "Changed or missing predicates:" if part == "q1" else f"changed {name}: NOT LISTED"}
    marker = named.get(kind, f"changed {name}: NOT LISTED")
    assert marker in out, out
    assert name in marker or name in [n.strip() for n in out.split(marker, 1)[1].splitlines()[0].split(",")], out


def test_the_readers_take_only_spec_or_source_code():
    """The readers refuse raw text, so no caller can read a source through a spec's fences or a spec's prose as code;
    a spec section without a ```lean block is an error, not code."""
    tool = _tool()
    for read in (tool.statements, tool.definitions, tool.types):
        with pytest.raises(TypeError):
            read("def HasReading : Prop := True")
    with pytest.raises(SystemExit):
        tool.spec_code("prose\ndef HasReading : Prop := True\n")
    fenced = "/-! ```lean\ndef HasReading : Prop := True\n``` -/\ndef HasReading : Prop := False\n"
    assert tool.definitions(tool.Code([fenced])) == {"HasReading": "def HasReading : Prop := False"}
    assert tool.definitions(tool.spec_code("x\n```lean\ndef A : Prop := True\n```\n")) == {"A": "def A : Prop := True"}
