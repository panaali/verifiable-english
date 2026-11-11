"""ps-2ab-rule-firstob: `admit`'s rule check names the rule's first obligation, else none (ps-2ac review F2).

The block of review F2: p1 a claim on u1, p2 a rule act on r2, and rule r1 given two different nodes. `admit`
refuses it in step 5's rule check, which named the block's first obligation (`PresuppositionMismatch: p1: rule`)
though p1 is no obligation of r1. No service mode runs `admit` yet (PS-4 puts its report in the document answer),
so the test elaborates the block with `lake env lean` against the built `VE.Presupposition.Admit`, under
`tmp_path`, and reads the diagnostic Lean prints. Lean decides every answer; Python only compares the text.
The same block's `#guard`s are in `lean/VE/Presupposition/Run.lean`'s guard section.
"""
from __future__ import annotations

import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

IMPORT = "VE.Presupposition.Run"

# The block, built from the presupposition examples only (they are on main before this item, so the test runs there).
SOURCE = f"""import {IMPORT}
open VE.Presupposition VE.Presupposition.Examples
def r1twin : VE.Norms.Node := {{ rule22 "r1" with guard := .top }}
def blockF2 (extra : List VE.Norms.Node) (p3 : Bool) : PDoc :=
  docA ([cu "u0" theOwnerU, cu "u1" theOwner, cu "u2" (ruleGoal (reg7) (rule22 "r2") pre22), ⟨"u8", true, .rule "r2"⟩] ++
      (if p3 then [cu "u3" (ruleGoal (reg7) (rule22 "r1") pre22), ⟨"u9", true, .rule "r1"⟩] else []))
    ([pA (.assumed "u0"), {{ p7 (.assumed "u2") with id := "p2", unit := "u8", position := .ruleAct "r2" }}] ++
      (if p3 then [{{ p7 (.assumed "u3") with id := "p3", unit := "u9" }}] else []))
    (tree7 ([rule22 "r1"] ++ extra ++ [rule22 "r2"])) true ["p"]
#eval IO.println ("ANSWER one-node " ++ errOf (admit (blockF2 [] false)))
#eval IO.println ("ANSWER two-nodes " ++ errOf (admit (blockF2 [r1twin] false)))
#eval IO.println ("ANSWER two-nodes-p3 " ++ errOf (admit (blockF2 [r1twin] true)))
"""


@pytest.fixture(scope="module")
def answers(tmp_path_factory) -> dict[str, str]:
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    source = tmp_path_factory.mktemp("rule_ob") / "RuleOb.lean"
    source.write_text(SOURCE)
    run = subprocess.run([lake, "env", "lean", str(source)], cwd=LEAN, capture_output=True, text=True,
                         timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr
    rows = [line.split(" ", 2) for line in run.stdout.splitlines() if line.startswith("ANSWER ")]
    found = {name: text for _, name, text in rows}
    assert len(found) == len(rows) == 3, run.stdout
    return found


def test_one_node_is_admitted(answers):
    assert answers["one-node"] == "admitted"


def test_rule_without_obligation_names_none(answers):
    # the rule check's refusal; not p1 (the block's first, a claim on u1), not p2 (the tree check's first rule act)
    text = answers["two-nodes"]
    assert text == "PresuppositionMismatch: : rule"
    assert "p1" not in text and "p2" not in text


def test_rule_with_obligation_names_its_first(answers):
    # r1's own act p3 comes after r2's p2: the rule check names p3
    assert answers["two-nodes-p3"] == "PresuppositionMismatch: p3: rule"
