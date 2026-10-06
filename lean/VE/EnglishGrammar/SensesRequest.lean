import VE.Senses.Read

/-! E2 checks the document's submitted lexicon before entering the senses reader.
The reader may then project a separate lexicon from the dictionary. -/

namespace VE.EnglishGrammar
open VE.Senses

def sensesRequest (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String) : SensesOutcome :=
  if L.policyOk E {} then readWithSenses D E L b s else .invalidGrammar .lexicon

theorem sensesRequest_policy : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String),
  L.policyOk E {} = true → sensesRequest D E L b s = readWithSenses D E L b s := by
  intro D E L b s h
  simp [sensesRequest, h]

end VE.EnglishGrammar
