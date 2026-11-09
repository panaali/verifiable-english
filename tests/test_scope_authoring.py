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
# What the docstrings of `Pinned.closers` and `Pinned.clause` name besides Unicode's Pe, Pf and Pi.
TERMINATORS = set(".?!:…‽。？！：．")
CLOSER_EXTRAS = set("\"'＂＇>*_`~")

# Lean is the oracle: the characters `clause` refuses after a ".", over every Unicode scalar value that is a
# `wordChar`, the F7 wordings' verdicts, and the two docstrings as the compiled environment has them.
SWEEP = """import Lean
import VE.Scope.Authoring
open Lean VE.Scope.Pinned
def refused : Array Nat := Id.run do
  let mut out := #[]
  for n in [0:0x110000] do
    if n.isValidChar then
      let c := Char.ofNat n
      if wordChar c && !clause ("x." ++ c.toString) then out := out.push n
  return out
#eval show CoreM Unit from do
  let env ← getEnv
  IO.println (Json.mkObj [("refused", toJson refused), ("closers", toJson (← findDocString? env ``closers)),
    ("clause", toJson (← findDocString? env ``clause)),
    ("accepted", toJson ((Json.parse (WORDINGS)).toOption.getD .null |>.getArr?.toOption.getD #[] |>.map
      fun w => (parseGovernor (w.getStr?.toOption.getD "")).isSome))]).compress
"""


@pytest.fixture(scope="module")
def swept(tmp_path_factory) -> dict:
    lean_build("VE")
    source = tmp_path_factory.mktemp("closers") / "Closers.lean"
    source.write_text(SWEEP.replace("WORDINGS", json.dumps(json.dumps(F7_WORDINGS, ensure_ascii=False),
                                                             ensure_ascii=False)))
    done = subprocess.run([lake_outputs.lean_executable(None, "lake"), "env", "lean", str(source)], cwd=LEAN,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout + done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


def test_review_f7_the_probe_wordings_are_refused(swept):
    """sc-7 review F7: a sentence end before `'`, `}`, `›`, `」` or `）` was read as a narrowing or a list name."""
    assert swept["accepted"] == [False] * len(F7_WORDINGS)
    examples = EXAMPLES.read_text()
    for wording in F7_WORDINGS:
        assert json.dumps(wording, ensure_ascii=False) in examples, wording


def test_review_f7_clause_refuses_exactly_the_documented_closers(swept):
    """sc-7 review F7 (the class): after a ".", `clause` refuses exactly the sentence ends and the closers its
    docstrings name: every character of the Unicode version's Pe, Pf and Pi categories that `closers` cites, and its
    listed quotes, `>` and Markdown marks. A missing closer (the review's `'`) or a refused character the docstrings
    do not name fails."""
    closers, clause = swept["closers"], swept["clause"]
    version = re.search(r"Unicode (\d+\.\d+)'s categories Pe \(closing\s+brackets\), Pf and Pi", closers)
    assert version is not None, closers
    assert unicodedata.unidata_version.startswith(version.group(1) + "."), (version.group(1),
                                                                            unicodedata.unidata_version)
    for c in CLOSER_EXTRAS:
        assert (f"`` {c} ``" if c == "`" else f"`{c}`") in closers, c
    for c in TERMINATORS:
        assert f'"{c}"' in clause, c
    assert "before any `closers`" in clause
    categories = {chr(n) for n in range(sys.maxunicode + 1) if unicodedata.category(chr(n)) in ("Pe", "Pf", "Pi")}
    refused, named = {chr(n) for n in swept["refused"]}, TERMINATORS | categories | CLOSER_EXTRAS
    assert refused == named, {"refused, not named": sorted(refused - named),
                              "named, not refused": sorted(named - refused)}
