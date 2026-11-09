"""cmp-s3a-cfr-2: a rule name on two structured lines gets rights' own `DuplicateDeclaration` text.

The right-clauses head (`checkClauses`, lean/VE/RightClauses/Plain.lean) refused an entry whose rule is on two source
lines with `InvalidInput: invalid clauses of rule <n>`, where rights (lean/VE/Rights/Correlate.lean `checkRights`)
says `DuplicateDeclaration: rule <n>`. `entryError` now answers with rights' own text when rights' first fault is
that duplicate. Lean is the oracle: the check elaborates under `tmp_path` and prints the head's answer and rights'
answer for the document a decoder builds from two lines named `equal-access` (one entry per line).
"""
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

# The probe imports `Plain` and rights' fixtures only (not RightClauses.Examples, whose `#guard`s fail its build
# under a seeded bug), so a seeded break shows here as a failed assertion.
CHECK = """import VE.RightClauses.Plain
import VE.Rights.Examples
open VE.RightClauses VE.Rights.Examples

def accessLine (n : String) : VE.Rights.SourceLine :=
  line .claim (strictNode n "public_service_access_required" true .top)
def twice (holders : List String := ["person"]) (n := "equal-access") : VE.Rights.RightsDoc :=
  mkRights ["state", "person"] [("country_of", ["state", "person"])]
    [VE.Norms.Checks.oblig "public_service_access_required" ["state", "person"] false none "{0} grant {1} access"]
    [] { block with holders } [⟨"r21", "person", .top, [accessLine n, accessLine n]⟩] [] []
def entries (D : VE.Rights.RightsDoc) (n := "equal-access") : ClauseDoc :=
  ⟨D, [("r21", n, ⟨accessLine n, [], none, [], (0, 100)⟩), ("r21", n, ⟨accessLine n, [], none, [], (0, 100)⟩)], []⟩
def text : Except String Unit → String
  | .ok () => "ok"
  | .error e => e

#eval IO.println ("head:" ++ text (checkClauses (entries (twice))))
#eval IO.println ("rights:" ++ text (VE.Rights.checkRights (twice)))
#eval IO.println ("head-right:" ++ text (checkClauses (entries (twice (n := "r21")) "r21")))
#eval IO.println ("rights-right:" ++ text (VE.Rights.checkRights (twice (n := "r21"))))
#eval IO.println ("head-no-block:" ++ text (checkClauses (entries (twice []))))
#eval IO.println ("rights-no-block:" ++ text (VE.Rights.checkRights (twice [])))
"""

DUPLICATE = "DuplicateDeclaration: rule equal-access"
INVALID = "InvalidInput: invalid clauses of rule equal-access"
LABELS = {"head", "rights", "head-right", "rights-right", "head-no-block", "rights-no-block"}


def answers(output: str) -> dict:
    """The `<label>:<text>` lines the check prints, by label (the text to the end of the line, unstripped)."""
    found = {}
    for line in output.splitlines():
        label, colon, text = line.partition(":")
        if colon and label in LABELS:
            assert label not in found, line
            found[label] = text
    return found


def same_bytes(head: str, rights: str) -> bool:
    """The DRI's condition (dri-decisions-20261109-lp0801.md item 1): the head's text is rights' text, byte for byte."""
    return head.encode() == rights.encode()


@pytest.fixture(scope="module")
def elaborated(tmp_path_factory):
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    source = tmp_path_factory.mktemp("cfr2") / "Duplicate.lean"
    source.write_text(CHECK)
    run = subprocess.run([lake, "env", "lean", str(source)], cwd=LEAN, capture_output=True, text=True,
                         timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr
    return answers(run.stdout)


def test_answers_read_only_labelled_lines():
    assert answers("head:a b\nx.lean:1:0: info: head:c\nrights:DuplicateDeclaration: rule n\n") == {
        "head": "a b", "rights": "DuplicateDeclaration: rule n"}


def test_same_bytes_refuses_every_one_character_edit():
    assert same_bytes(DUPLICATE, DUPLICATE)
    for i in range(len(DUPLICATE)):
        assert not same_bytes(DUPLICATE[:i] + DUPLICATE[i + 1:], DUPLICATE)
        assert not same_bytes(DUPLICATE[:i] + "#" + DUPLICATE[i + 1:], DUPLICATE)
    assert not same_bytes(DUPLICATE + ".", DUPLICATE)


def test_clause_entries_preserve_duplicate_rule_diagnostic(elaborated):
    # Two structured lines named `equal-access`: the head answers with rights' own text, byte for byte.
    assert elaborated["rights"] == DUPLICATE
    assert same_bytes(elaborated["head"], elaborated["rights"])
    assert elaborated["head"] != INVALID


def test_clause_entries_take_rights_first_duplicate_text(elaborated):
    # The rule named like its right: rights' first fault is `DuplicateDeclaration: right r21`; the head's text is
    # rights' text, byte for byte, not a text of its own (the DRI's signed condition, lp0801 item 1).
    assert elaborated["rights-right"] == "DuplicateDeclaration: right r21"
    assert same_bytes(elaborated["head-right"], elaborated["rights-right"])


def test_clause_entries_keep_invalid_clauses_when_rights_faults_first(elaborated):
    # Rights' first fault is not the duplicate (an empty rights block): the head keeps its own text.
    assert elaborated["rights-no-block"] == "InvalidInput: invalid rights block"
    assert elaborated["head-no-block"] == INVALID
