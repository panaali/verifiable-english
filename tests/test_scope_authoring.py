"""SC-7: scope's authoring wordings (docs/spec/scope.md 2.2, 5.8, 7.8). Lean decides (`Pinned.parseGovernor`,
`Pinned.renderGovernor`, `Pinned.paraphrase`, `lean/VE/Scope/Authoring.lean`); each row of 2.2, F5a and the refused
variants are `#guard`s in `lean/VE/Scope/AuthoringExamples.lean`, checked by every `lake build`. No Python reads a
wording: the IDE wiring through the relay is sc-7b. These tests tie the Lean text to the spec's."""
from __future__ import annotations

import json
import re
from pathlib import Path
import subprocess
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor

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
# sc-7 recheck F8 and F9: the PROBE wordings, verbatim (the `\u` escapes are Lean's, as the probes write them)
F8_WORDINGS = ("The rules below are called the x‼ The rules below are called the y.", "The hard constraints apply only where x⁉ y.",
               "The hard constraints apply only where x؟ y.", "The hard constraints apply only where x｡ y.",
               "The hard constraints apply only where x﹖ y.", "The hard constraints apply only where x। y.")
F9_WORDINGS = ("The rules below are called the x.\u200B The rules below are called the y.",
               "The hard constraints apply only where x.\u2060 y.", "The hard constraints apply only where x.\u0301 y.")
F7_TERMINATORS = ".?!:…‽。？！：．"
CLOSER_EXTRAS = set("\"'＂＇>*_`~")


def ranges(*spans: tuple[int, int]) -> set[str]:
    return {chr(n) for a, b in spans for n in range(a, b + 1)}


# Python's unicodedata has neither property, so both are literal ranges. Sentence_Terminal: Unicode 15.1's (the ICU 74
# of this checkout's Node, `/\p{Sentence_Terminal}/u`) with Unicode 16.0's additions, Balinese U+1B4E, U+1B4F and U+1B7F,
# Tulu-Tigalari U+113D4 and U+113D5, Kirat Rai U+16D6E and U+16D6F (PropList.txt 16.0.0).
STERM_16 = ranges(
    (0x21, 0x21), (0x2E, 0x2E), (0x3F, 0x3F), (0x589, 0x589), (0x61D, 0x61F), (0x6D4, 0x6D4), (0x700, 0x702),
    (0x7F9, 0x7F9), (0x837, 0x837), (0x839, 0x839), (0x83D, 0x83E), (0x964, 0x965), (0x104A, 0x104B),
    (0x1362, 0x1362), (0x1367, 0x1368), (0x166E, 0x166E), (0x1735, 0x1736), (0x17D4, 0x17D5), (0x1803, 0x1803),
    (0x1809, 0x1809), (0x1944, 0x1945), (0x1AA8, 0x1AAB), (0x1B4E, 0x1B4F), (0x1B5A, 0x1B5B), (0x1B5E, 0x1B5F),
    (0x1B7D, 0x1B7F), (0x1C3B, 0x1C3C), (0x1C7E, 0x1C7F), (0x203C, 0x203D), (0x2047, 0x2049), (0x2E2E, 0x2E2E),
    (0x2E3C, 0x2E3C), (0x2E53, 0x2E54), (0x3002, 0x3002), (0xA4FF, 0xA4FF), (0xA60E, 0xA60F), (0xA6F3, 0xA6F3),
    (0xA6F7, 0xA6F7), (0xA876, 0xA877), (0xA8CE, 0xA8CF), (0xA92F, 0xA92F), (0xA9C8, 0xA9C9), (0xAA5D, 0xAA5F),
    (0xAAF0, 0xAAF1), (0xABEB, 0xABEB), (0xFE52, 0xFE52), (0xFE56, 0xFE57), (0xFF01, 0xFF01), (0xFF0E, 0xFF0E),
    (0xFF1F, 0xFF1F), (0xFF61, 0xFF61), (0x10A56, 0x10A57), (0x10F55, 0x10F59), (0x10F86, 0x10F89),
    (0x11047, 0x11048), (0x110BE, 0x110C1), (0x11141, 0x11143), (0x111C5, 0x111C6), (0x111CD, 0x111CD),
    (0x111DE, 0x111DF), (0x11238, 0x11239), (0x1123B, 0x1123C), (0x112A9, 0x112A9), (0x113D4, 0x113D5),
    (0x1144B, 0x1144C), (0x115C2, 0x115C3), (0x115C9, 0x115D7), (0x11641, 0x11642), (0x1173C, 0x1173E),
    (0x11944, 0x11944), (0x11946, 0x11946), (0x11A42, 0x11A43), (0x11A9B, 0x11A9C), (0x11C41, 0x11C42),
    (0x11EF7, 0x11EF8), (0x11F43, 0x11F44), (0x16A6E, 0x16A6F), (0x16AF5, 0x16AF5), (0x16B37, 0x16B38),
    (0x16B44, 0x16B44), (0x16D6E, 0x16D6F), (0x16E98, 0x16E98), (0x1BC9F, 0x1BC9F), (0x1DA88, 0x1DA88),)
# Default_Ignorable_Code_Point: Unicode 16.0's DerivedCoreProperties.txt (the same ranges as 15.1's ICU 74 lists).
DEFAULT_IGNORABLE_16 = ranges(
    (0xAD, 0xAD), (0x34F, 0x34F), (0x61C, 0x61C), (0x115F, 0x1160), (0x17B4, 0x17B5), (0x180B, 0x180F),
    (0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x206F), (0x3164, 0x3164), (0xFE00, 0xFE0F), (0xFEFF, 0xFEFF),
    (0xFFA0, 0xFFA0), (0xFFF0, 0xFFF8), (0x1BCA0, 0x1BCA3), (0x1D173, 0x1D17A), (0xE0000, 0xE0FFF),)
SCALARS = [chr(n) for n in range(sys.maxunicode + 1) if not 0xD800 <= n <= 0xDFFF]
# What `clause`'s docstring names. Python's unicodedata is 16.0.0, the docstrings' version (checked below), so no
# version difference enters these sets; a later Python fails that check before it compares them.
TERMINATORS = STERM_16 | {":"} | {c for c in SCALARS
                                  if (k := unicodedata.normalize("NFKC", c)) and k[-1] in STERM_16 | {":"}}
INVISIBLE = {c for c in SCALARS if unicodedata.category(c) in ("Cf", "Mn", "Me")} | DEFAULT_IGNORABLE_16 | {"\u2800"}
CLOSERS = {c for c in SCALARS if unicodedata.category(c) in ("Pe", "Pf", "Pi")} | CLOSER_EXTRAS
# What `wordChar`'s docstring refuses: `str.isspace`, C0, DEL and C1, and the five fillers drawn as a space.
NOT_WORD = ({c for c in SCALARS if c.isspace() or ord(c) < 0x20 or 0x7F <= ord(c) <= 0x9F}
            | {chr(n) for n in (0x115F, 0x1160, 0x2800, 0x3164, 0xFFA0)})

# Lean is the oracle: over the Unicode scalar values from LO to HI, the characters that are no `wordChar`, the
# `wordChar`s `clause` refuses after "x" (the sentence ends) and after "x." (the sentence ends, closers and invisible
# characters); every sentence end t of TERMS and invisible character c of MARKS that `clause` accepts as "x" t c (and,
# for F7's eleven sentence ends, as "x" t ")" c and "x" t c ")"); the probe wordings' verdicts; and the three
# docstrings as the compiled environment has them. Each run is one chunk; `swept` runs the chunks side by side, since
# the interpreter takes about 60 microseconds a `clause` and the sweep makes about 3.5 million.
SWEEP = """import Lean
import VE.Scope.Authoring
open Lean VE.Scope.Pinned
def codes (j : String) : Array Nat :=
  (Json.parse j).toOption.getD .null |>.getArr?.toOption.getD #[] |>.filterMap (·.getNat?.toOption)
def sweep : Array Nat × Array Nat × Array Nat × Array (Nat × Nat) := Id.run do
  let mut nonWord := #[]; let mut ends := #[]; let mut refused := #[]; let mut hidden := #[]
  for n in [LO:HI] do
    if n.isValidChar then
      let c := Char.ofNat n
      if !wordChar c then nonWord := nonWord.push n
      else
        if !clause ("x" ++ c.toString) then ends := ends.push n
        if !clause ("x." ++ c.toString) then refused := refused.push n
  let marks := codes (MARKS)
  for t in codes (TERMS) do
    for m in marks do
      let (t, m) := ((Char.ofNat t).toString, (Char.ofNat m).toString)
      let mixed := if FIRST.contains t.front then ["x" ++ t ++ ")" ++ m, "x" ++ t ++ m ++ ")"] else []
      for w in ("x" ++ t ++ m) :: mixed do
        if clause w then hidden := hidden.push (t.front.toNat, m.front.toNat)
  return (nonWord, ends, refused, hidden)
def verdicts (ws : String) : Array Bool := (Json.parse ws).toOption.getD .null |>.getArr?.toOption.getD #[] |>.map
  fun w => (parseGovernor (w.getStr?.toOption.getD "")).isSome
#eval show CoreM Unit from do
  let env ← getEnv
  let (nonWord, ends, refused, hidden) := sweep
  IO.println (Json.mkObj [("non_word", toJson nonWord), ("ends", toJson ends), ("refused", toJson refused),
    ("hidden", toJson hidden), ("closers", toJson (← findDocString? env ``closers)),
    ("clause", toJson (← findDocString? env ``clause)), ("word_char", toJson (← findDocString? env ``wordChar)),
    ("accepted", toJson ((WORDINGS).map verdicts))]).compress
"""
CHUNKS = 8


def lean_string(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def sweep_chunk(directory: Path, index: int) -> dict:
    """Chunk `index` of `CHUNKS`: an equal share of the scalar values and every `CHUNKS`-th sentence end."""
    wordings = "#[" + ", ".join(lean_string(json.dumps(ws, ensure_ascii=False))
                                for ws in (F7_WORDINGS, F8_WORDINGS, F9_WORDINGS)) + "]"
    lo, hi = (sys.maxunicode + 1) * index // CHUNKS, (sys.maxunicode + 1) * (index + 1) // CHUNKS
    source = directory / f"Sweep{index}.lean"
    source.write_text(SWEEP.replace("WORDINGS", wordings).replace("[LO:HI]", f"[{lo}:{hi}]")
                      .replace("TERMS", lean_string(json.dumps(sorted(map(ord, TERMINATORS))[index::CHUNKS])))
                      .replace("FIRST", lean_string(F7_TERMINATORS))
                      .replace("MARKS", lean_string(json.dumps(sorted(map(ord, INVISIBLE))))))
    done = subprocess.run([lake_outputs.lean_executable(None, "lake"), "env", "lean", str(source)], cwd=LEAN,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout + done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def swept(tmp_path_factory) -> dict:
    """The chunks' answers, the lists joined (each chunk's docstrings and verdicts are the same: the first one's)."""
    lean_build("VE")
    directory = tmp_path_factory.mktemp("closers")
    with ThreadPoolExecutor(CHUNKS) as pool:
        parts = list(pool.map(lambda index: sweep_chunk(directory, index), range(CHUNKS)))
    joined = dict(parts[0])
    for key in ("non_word", "ends", "refused", "hidden"):
        joined[key] = [item for part in parts for item in part[key]]
    return joined


def test_review_f7_the_probe_wordings_are_refused(swept):
    """sc-7 review F7: a sentence end before `'`, `}`, `›`, `」` or `）` was read as a narrowing or a list name."""
    assert swept["accepted"][0] == [False] * len(F7_WORDINGS)
    examples = EXAMPLES.read_text()
    for wording in F7_WORDINGS:
        assert json.dumps(wording, ensure_ascii=False) in examples, wording


def test_the_docstrings_name_unicode_16_0_the_version_of_this_python():
    """The sets below are Python's unicodedata; they are the docstrings' sets only if both are Unicode 16.0."""
    assert unicodedata.unidata_version.startswith("16.0."), unicodedata.unidata_version


def test_review_f7_clause_refuses_exactly_the_documented_closers(swept):
    """sc-7 review F7 (the class), with F8's sentence ends and F9's invisible characters: after a ".", `clause` refuses
    exactly the word characters its docstrings name: the sentence ends, every character of the Unicode version's Pe,
    Pf and Pi categories that `closers` cites and its listed quotes, `>` and Markdown marks, and the invisible
    characters. A missing closer (the review's `'`) or a refused character the docstrings do not name fails."""
    closers = swept["closers"]
    version = re.search(r"Unicode (\d+\.\d+)'s categories Pe \(closing\s+brackets\), Pf and Pi", closers)
    assert version is not None, closers
    assert unicodedata.unidata_version.startswith(version.group(1) + "."), (version.group(1),
                                                                            unicodedata.unidata_version)
    for c in CLOSER_EXTRAS:
        assert (f"`` {c} ``" if c == "`" else f"`{c}`") in closers, c
    refused, named = {chr(n) for n in swept["refused"]}, (TERMINATORS | CLOSERS | INVISIBLE) - NOT_WORD
    assert refused == named, {"refused, not named": sorted(refused - named),
                              "named, not refused": sorted(named - refused)}


def test_review_f8_clause_refuses_exactly_the_documented_sentence_ends(swept):
    """sc-7 recheck F8: `clause` read "‼", "⁉", "؟", "｡", "﹖" and "।" as letters, so "the x‼ The rules below are
    called the y" was one list name. The class: the sentence ends `clause` refuses at a word's end are exactly its
    docstring's, Unicode 16.0's Sentence_Terminal, ":" and every character whose NFKC form ends in one of them; the
    probe is refused; and the F8 guard of AuthoringExamples.lean names each one F7's eleven do not, once."""
    clause = " ".join(swept["clause"].split())
    for phrase in ("no Unicode 16.0 Sentence_Terminal, no \":\" and none whose NFKC form ends in one of them",
                   "(\"…\", \"：\", \"︖\", \"⒈\", \"㏂\")"):
        assert phrase in clause, phrase
    ends = {chr(n) for n in swept["ends"]}
    assert ends == TERMINATORS, {"refused, not named": sorted(ends - TERMINATORS),
                                 "named, not refused": sorted(TERMINATORS - ends)}
    assert not TERMINATORS & (CLOSERS | INVISIBLE | NOT_WORD)
    assert swept["accepted"][1] == [False] * len(F8_WORDINGS)
    examples = EXAMPLES.read_text()
    probe = "#guard [" + ", ".join(json.dumps(w, ensure_ascii=False) for w in F8_WORDINGS)
    assert probe + "].all (VE.Scope.Pinned.parseGovernor · == none)" in examples
    guard = re.search(r'#guard "([^"]+)"\.toList\.all fun t =>\n  \[t\.toString, ', examples)
    assert guard is not None
    added = guard.group(1)
    assert len(added) == len(set(added)) and set(added) == TERMINATORS - set(F7_TERMINATORS)
    assert set("‼⁉⁈⁇؟۔｡﹖﹗﹒։።।") <= set(added)


def test_review_f9_no_invisible_character_hides_a_sentence_end(swept):
    """sc-7 recheck F9: `clause` dropped only `closers` before it read a word's last character, so U+200B, U+2060,
    U+00AD, U+FE0F or U+0301 after a "." hid it. The class (the DRI note's amended set): every character of Unicode
    16.0's Cf, Mn and Me, of Default_Ignorable_Code_Point and U+2800 is refused after every sentence end (and after
    and before a closer after F7's eleven); the docstrings name the set; and the probe and the DRI note's guards are in the
    examples."""
    clause, word_char = " ".join(swept["clause"].split()), " ".join(swept["word_char"].split())
    assert ("Once its trailing `closers` and characters of Unicode 16.0's Cf, Mn, Me, Default_Ignorable_Code_Point "
            "and U+2800 are dropped (mixed in any order)") in clause
    assert "`wordChar` refuses U+115F, U+1160, U+2800, U+3164, U+FFA0 anywhere" in clause
    assert ("no control character (C0, DEL and C1: below U+0020, and U+007F to U+009F) and no filler drawn as a space "
            "(U+115F, U+1160, U+2800, U+3164, U+FFA0)") in word_char
    assert {chr(n) for n in swept["non_word"]} == NOT_WORD
    assert len(INVISIBLE) == 5977 and len(TERMINATORS) == 199  # Unicode 16.0 (pinned above): the sweep is not vacuous
    assert swept["hidden"] == []
    assert swept["accepted"][2] == [False] * len(F9_WORDINGS)
    examples = EXAMPLES.read_text()
    probe = "#guard [" + ", ".join(json.dumps(w).replace("\\u200b", "\\u200B") for w in F9_WORDINGS)
    assert probe + "].all (VE.Scope.Pinned.parseGovernor · == none)" in examples
    for guard in ('"The hard constraints apply only where x.\\u00AD y."', '"The hard constraints apply only where x.\\uFE0F y."',
                  '"The hard constraints apply only where x.)\\u0301 y."', '#guard !clause "x.\\u3164"',
                  '#guard !clause "x.\\u115F"', '#guard !clause "x.\\u1160"', '#guard !clause "x.\\uFFA0"',
                  '#guard !clause "x.\\u2800"'):
        assert guard in examples, guard
