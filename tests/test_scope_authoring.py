"""SC-7: scope's authoring wordings (docs/spec/scope.md 2.2, 5.8, 7.8). Lean decides (`Pinned.parseGovernor`,
`Pinned.renderGovernor`, `Pinned.paraphrase`, `lean/VE/Scope/Authoring.lean`); each row of 2.2, F5a and the refused
variants are `#guard`s in `lean/VE/Scope/AuthoringExamples.lean`, checked by every `lake build`. No Python reads a
wording: the IDE wiring through the relay is sc-7b. These tests tie the Lean text to the spec's."""
from __future__ import annotations

import json
import re
from pathlib import Path
import subprocess
import string
import sys
import unicodedata

import pytest

from tests.lean_build import LEAN, lean_build
from tests.subprocesses import HANG_TIMEOUT
from tests.test_scope_5_4_statements import statement

ROOT = Path(__file__).resolve().parents[1]
AUTHORING = ROOT / "lean/VE/Scope/Authoring.lean"
EXAMPLES = ROOT / "lean/VE/Scope/AuthoringExamples.lean"
SPEC = ROOT / "docs/spec/scope.md"
sys.path.insert(0, str(ROOT / "tools"))
import lake_outputs  # noqa: E402


def spec_5_8() -> str:
    spec = SPEC.read_text()
    start = spec.index("### 5.8 SC-6")
    return spec[start:spec.index("### 6.", start)]


def test_the_round_trip_statements_are_spec_5_8s_text():
    for name in ("scope_parseRender", "scope_renderParse"):
        want = statement(spec_5_8(), name)
        assert want is not None, name
        assert statement(AUTHORING.read_text(), name) == want, name


def test_the_statement_gate_sees_a_changed_conclusion():
    changed = AUTHORING.read_text().replace("Pinned.renderGovernor b = w", "Pinned.renderGovernor b = w ++ \"\"", 1)
    assert statement(changed, "scope_parseRender") != statement(spec_5_8(), "scope_parseRender")


def test_f5a_guards_u0170_s01s_wording_as_the_spec_quotes_it():
    """F5a (7.8): the wording the Lean fixture parses to no governor is 2.1's quotation of u0170.s01, byte for byte."""
    quoted = re.search(r'\(u0170\.s01, "([^"]+)"\)', " ".join(SPEC.read_text().split()))
    assert quoted is not None
    examples = EXAMPLES.read_text()
    assert f'def u0170s01 := "{quoted.group(1)}"' in examples
    assert "#guard parseGovernor u0170s01 == none" in examples


def test_each_row_of_2_2_has_a_round_trip_and_a_paraphrase_guard():
    examples = EXAMPLES.read_text()
    for row in ("wFrame", "wNamed", "wNarrow", "wInPlace", "wCarve", "wPrecedes", "wWhen", "wTitle", "wFrontier"):
        assert f"#guard trip {row} " in examples, row
        assert f"#guard para {row} " in examples, row


def test_review_f1_no_slot_ends_a_sentence_is_guarded():
    """sc-7 review F1: the review's probe (a question heading, an exclamation heading, a question condition) is a
    `#guard` that `lake build` checks, and the sweep guard covers every slot: a "When"/"If" heading, a narrowing, a
    carve-out, the "Notwithstanding" section and rule, the frontier, the list name and the "In place of" name."""
    examples = EXAMPLES.read_text()
    probe = ('#guard ["## When should Claude refuse?", "### If in doubt, ask!", '
             '"The hard constraints apply only where is the act irreversible?."].all\n'
             '  fun w => ((parseGovernor w).map (·.getObjValD "effect")).all (· == Json.str "title")')
    assert probe in examples
    sweep = examples[examples.index("-- every slot, every sentence end"):]
    sweep = sweep[:sweep.index("].all (parseGovernor · == none)")]
    for start in ("## When ", "## If ", "The hard constraints apply only where ", "The hard constraints do not apply when ",
                  "Notwithstanding the rules of section 3, ", "Notwithstanding the rules of section 3?",
                  "This applies only where ", "The rules below are called the x.", "The hard constraints. ",
                  "In place of their own condition, the x."):
        assert f'"{start}' in sweep, start


# sc-7 review F7: the review's PROBE F7 and the DRI note's two more wordings, each refused (`parseGovernor` is none)
F7_WORDINGS = ("## If the user says 'stop.'", "The rules below are called the x.' The rules below are called the y.",
               "The hard constraints apply only where x.} y.", "The hard constraints apply only where x。」 y.",
               "The hard constraints apply only where x.› y.", "The hard constraints apply only where x.） y.")
# sc-7 recheck F8, F9 and F10: the PROBE wordings, verbatim (the `\u` escapes are Lean's, as the probes write them)
F8_WORDINGS = ("The rules below are called the x‼ The rules below are called the y.", "The hard constraints apply only where x⁉ y.",
               "The hard constraints apply only where x؟ y.", "The hard constraints apply only where x｡ y.",
               "The hard constraints apply only where x﹖ y.", "The hard constraints apply only where x। y.")
F9_WORDINGS = ("The rules below are called the x.​ The rules below are called the y.",
               "The hard constraints apply only where x.⁠ y.", "The hard constraints apply only where x.́ y.")
F10_WORDINGS = ("The hard constraints apply only where x⳹ y.", "The hard constraints apply only where x⳺ y.",
                "The rules below are called the x⳻ The rules below are called the y.")
# the recheck's deferred blank-looking characters after a ".": U+1D159, U+E000 and U+FFFC, as a condition and a list name
BLANK_WORDINGS = tuple(w for c in ("\U0001D159", "", "￼")
                       for w in (f"The hard constraints apply only where x.{c} y.",
                                 f"The rules below are called the x.{c} The rules below are called the y.",
                                 # sc-7-f11: joined, the character in place of the space
                                 f"The rules below are called the x.{c}The rules below are called the y.",
                                 f"The hard constraints apply only where the x.{c}The rules below are called the y."))
CLOSER_EXTRAS = set("\"'＂＇>*_`~")
# `clause`'s allow-list as the DRI note 2026-11-09 (c) states it, written here apart from the Lean code: ASCII letters and
# digits, the Latin letters of U+00C0..U+024F but U+00D7 and U+00F7, and eleven ASCII punctuation characters; less
# U+01C3 "ǃ" (a letter drawn as "!", left out by this round).
ALLOW_PUNCTUATION = ",;-%/&+=#$@"
ALLOW = (set(string.ascii_letters + string.digits) | ({chr(n) for n in range(0xC0, 0x250)} - {"×", "÷", "ǃ"})
         | set(ALLOW_PUNCTUATION))
ALLOW_DOC = ("once its trailing `closers` are dropped, a word is not empty and ends in an allow-listed character, and no "
             "other: an ASCII letter or digit, a Latin letter of U+00C0 to U+024F but U+00D7, U+00F7 and U+01C3 (\"ǃ\"), "
             f"or one of `{ALLOW_PUNCTUATION}`.")
SCALARS = [chr(n) for n in range(sys.maxunicode + 1) if not 0xD800 <= n <= 0xDFFF]
CLOSERS = {c for c in SCALARS if unicodedata.category(c) in ("Pe", "Pf", "Pi")} | CLOSER_EXTRAS
# What `wordChar`'s docstring refuses: `str.isspace`, C0, DEL and C1, and the five fillers drawn as a space.
NOT_WORD = ({c for c in SCALARS if c.isspace() or ord(c) < 0x20 or 0x7F <= ord(c) <= 0x9F}
            | {chr(n) for n in (0x115F, 0x1160, 0x2800, 0x3164, 0xFFA0)})

# Lean is the oracle, in one process: one `#eval` over every Unicode scalar value c gives the characters that are no
# `wordChar` and those for which `clause` accepts "x" c, "x" c ")", "x." c and "x." c "y"; the probe wordings' verdicts; and the
# three docstrings as the compiled environment has them (about a minute: the interpreter takes about 18 microseconds
# a `clause`).
SWEEP = """import Lean
import VE.Scope.Authoring
open Lean VE.Scope.Pinned
def sweep : Array Nat × Array Nat × Array Nat × Array Nat × Array Nat := Id.run do
  let mut nonWord := #[]; let mut bare := #[]; let mut closed := #[]; let mut dotted := #[]; let mut joined := #[]
  for n in [0:0x110000] do
    if n.isValidChar then
      let c := Char.ofNat n
      if !wordChar c then nonWord := nonWord.push n
      if clause ("x" ++ c.toString) then bare := bare.push n
      if clause ("x" ++ c.toString ++ ")") then closed := closed.push n
      if clause ("x." ++ c.toString) then dotted := dotted.push n
      if clause ("x." ++ c.toString ++ "y") then joined := joined.push n
  return (nonWord, bare, closed, dotted, joined)
def verdicts (ws : String) : Array Bool := (Json.parse ws).toOption.getD .null |>.getArr?.toOption.getD #[] |>.map
  fun w => (parseGovernor (w.getStr?.toOption.getD "")).isSome
#eval show CoreM Unit from do
  let env ← getEnv
  let (nonWord, bare, closed, dotted, joined) := sweep
  IO.println (Json.mkObj [("non_word", toJson nonWord), ("bare", toJson bare), ("closed", toJson closed),
    ("dotted", toJson dotted), ("joined", toJson joined), ("closers", toJson (← findDocString? env ``closers)),
    ("clause", toJson (← findDocString? env ``clause)), ("word_char", toJson (← findDocString? env ``wordChar)),
    ("accepted", toJson ((WORDINGS).map verdicts))]).compress
"""
PROBES = (F7_WORDINGS, F8_WORDINGS, F9_WORDINGS, F10_WORDINGS, BLANK_WORDINGS)


def lean_string(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def chars(codes: list[int]) -> set[str]:
    return {chr(n) for n in codes}


@pytest.fixture(scope="module")
def swept(tmp_path_factory) -> dict:
    """The sweep's answer: one Lean process over every scalar value."""
    lean_build("VE")
    source = tmp_path_factory.mktemp("clause") / "Sweep.lean"
    wordings = "#[" + ", ".join(lean_string(json.dumps(ws, ensure_ascii=False)) for ws in PROBES) + "]"
    source.write_text(SWEEP.replace("WORDINGS", wordings))
    done = subprocess.run([lake_outputs.lean_executable(None, "lake"), "env", "lean", str(source)], cwd=LEAN,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout + done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


def test_review_f7_the_probe_wordings_are_refused(swept):
    """sc-7 review F7: a sentence end before `'`, `}`, `›`, `」` or `）` was read as a narrowing or a list name."""
    assert swept["accepted"][0] == [False] * len(F7_WORDINGS)
    examples = EXAMPLES.read_text()
    for wording in F7_WORDINGS:
        assert json.dumps(wording, ensure_ascii=False) in examples, wording


def test_the_docstrings_name_unicode_16_0_the_version_of_this_python():
    """`CLOSERS` is Python's unicodedata; it is `closers`' set only if both are Unicode 16.0."""
    assert unicodedata.unidata_version.startswith("16.0."), unicodedata.unidata_version


def test_clause_accepts_exactly_its_documented_allow_list(swept):
    """sc-7 recheck F10 and the DRI note 2026-11-09 (c), the class of F7, F8, F9 and F10 (a character at a word's end
    that hides a sentence end): for every Unicode scalar value c, `clause` accepts "x" c and "x" c ")" exactly when c
    is a word character in the allow-list or a closer (dropped, leaving "x"), "x." c exactly when c is in the
    allow-list, and "x." c "y" exactly when c is a word character in the allow-list or a closer (sc-7-f11: a "." inside
    a word is followed by no other character, so none stands in for a space after it). The docstring states the allow-list as `ALLOW` does and names no enumerated Unicode set; `closers` is
    Unicode 16.0's Pe, Pf and Pi with its listed extras."""
    clause, closers = " ".join(swept["clause"].split()), swept["closers"]
    assert ALLOW_DOC in clause, clause
    for gone in ("Sentence_Terminal", "NFKC", "Default_Ignorable", "Cf, Mn", "16.0"):
        assert gone not in clause, gone
    version = re.search(r"Unicode (\d+\.\d+)'s categories Pe \(closing\s+brackets\), Pf and Pi", closers)
    assert version is not None, closers
    assert unicodedata.unidata_version.startswith(version.group(1) + "."), (version.group(1),
                                                                            unicodedata.unidata_version)
    for c in CLOSER_EXTRAS:
        assert (f"`` {c} ``" if c == "`" else f"`{c}`") in closers, c
    assert len(ALLOW) == 26 * 2 + 10 + (0x250 - 0xC0 - 3) + 11 == 470 and not ALLOW & (CLOSERS | NOT_WORD)
    for key, want in (("bare", (ALLOW | CLOSERS) - NOT_WORD), ("closed", (ALLOW | CLOSERS) - NOT_WORD), ("dotted", ALLOW),
                      ("joined", (ALLOW | CLOSERS) - NOT_WORD)):
        got = chars(swept[key])
        assert got == want, {key: {"accepted, not allowed": sorted(got - want), "allowed, not accepted": sorted(want - got)}}


def test_word_char_refuses_exactly_its_documented_characters(swept):
    """`wordChar` refuses spaces, C0, DEL and C1 and the five fillers drawn as a space, and nothing else."""
    word_char = " ".join(swept["word_char"].split())
    assert ("no control character (C0, DEL and C1: below U+0020, and U+007F to U+009F) and no filler drawn as a space "
            "(U+115F, U+1160, U+2800, U+3164, U+FFA0)") in word_char
    assert chars(swept["non_word"]) == NOT_WORD


def test_review_f8_f9_f10_the_probe_wordings_are_refused_and_guarded(swept):
    """sc-7 recheck F8, F9 and F10: each probe wording (and the recheck's deferred U+1D159, U+E000 and U+FFFC after a
    ".", spaced and joined: sc-7-f11) is refused, and the PROBE F8, F9 and F10 guards of AuthoringExamples.lean stay, verbatim."""
    assert swept["accepted"][1:] == [[False] * len(ws) for ws in PROBES[1:]]
    examples = EXAMPLES.read_text()
    def lean_escaped(wording: str) -> str:  # json's \uxxxx escapes, with Lean's upper-case hex digits as the probes write them
        return re.sub(r"\\u([0-9a-f]{4})", lambda m: "\\u" + m.group(1).upper(), json.dumps(wording))
    for wordings, render in ((F8_WORDINGS, lambda w: json.dumps(w, ensure_ascii=False)), (F9_WORDINGS, lean_escaped),
                             (F10_WORDINGS, lean_escaped)):
        probe = "#guard [" + ", ".join(map(render, wordings))
        assert probe + "].all (VE.Scope.Pinned.parseGovernor · == none)" in examples, wordings
    for guard in ('"The hard constraints apply only where x.\\uFFFC y."', '"The hard constraints apply only where x.\\uE000 y."',
                  '#guard [0x1D159, 0xE000, 0xFFFC].all', '#guard !clause "x.\\u3164"', '#guard !clause "x.\\u2800"',
                  '#guard [0x1D159, 0xFFFC, 0xE000].all fun n => let c := Char.ofNat n',
                  '(slotsJoined s!"{t}{Char.ofNat n}").all (parseGovernor · == none)'):
        assert guard in examples, guard
