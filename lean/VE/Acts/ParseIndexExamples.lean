import VE.Acts.Readings
import VE.Acts.GrammarExamples
import Lean.Elab.Term
import Lean.Compiler.CSimpAttr

/-! ap-parse-index's fixtures: the steps of a growing vocabulary, the hashed indexes, and the compiled forms.

L6 (`V5`'s 64 readings) with `n` more frames, up to the 128 of D-31. A row is charged every rule and rule position, so
the steps grow by the same 1,984 with each frame, and the step budget bounds the time (`VE.Grammar` header: a step
costs at most a constant times `cap` plus the sentence length plus the longest exclusion list; measured at most 0.69
microseconds per step on the VM from 2 to 128 frames, docs/act-phrases/ap-parse-index/REPORT.md). A step count does not
see a step's time; the deadline fixtures of `tests/test_ap_parse_index.py` do.
The grammar is built once per read, in time near-linear in the frames (`closed_eq_fast`, `build_eq_fast`). -/

namespace VE.Acts.ParseIndexExamples
open VE.Acts VE.Acts.Examples

def padFrames (n : Nat) : List Frame :=
  (List.range n).map fun i => fr ("seek" ++ String.mk [Char.ofNat (97 + i / 26), Char.ofNat (97 + i % 26)]) [""] [] []
def l6Fixed : List String := ["first", "second", "third", "fourth", "fifth", "sixth"].map fun n => s!"the {n} city"
def l6 : String := "{0} to seek and to enjoy asylum" ++ String.join (l6Fixed.map (" in " ++ ·))
def l6Steps (n : Nat) : Option Nat :=
  (grammar ⟨V5.frames ++ padFrames n, []⟩).prepare.steps rawCap stepBudget
    ((Lexical.lex l6Fixed l6).toOption.getD []).toArray

#guard framesOk ⟨V5.frames ++ padFrames 126, []⟩ && !framesOk ⟨V5.frames ++ padFrames 127, []⟩
#guard [0, 30, 62, 126].all fun n => l6Steps n == some (23152 + 1984 * n)
-- the hashed first occurrences and first places, directly (`firstsGo_eq`, `idxGo_getD`)
#guard firstsGo ∅ ["S", "J", "S", "FW"] == ["S", "J", "FW"] &&
  ["S", "J", "FW", "x"].map (fun y => (idxGo ["S", "J", "S", "FW"] 0 ∅).getD y 4) == [0, 1, 3, 4]

/-- Whether compiled code runs the forms that build the grammar and read the rule table once, and skip an empty
suffix (each `@[csimp]` lemma of ap-parse-index is installed), read when the check elaborates. -/
syntax (name := onceInstalled) "once_installed%" : term

open Lean Elab Term in
@[term_elab onceInstalled] def elabOnceInstalled : TermElab := fun _ _ => do
  let m := (Lean.Compiler.CSimp.ext.getState (← getEnv)).map
  return toExpr ([``closed, ``build, ``VE.Grammar.combine, ``readings, ``read].all m.contains)

#guard once_installed%

end VE.Acts.ParseIndexExamples
