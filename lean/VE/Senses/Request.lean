import VE.EnglishGrammar.SensesRequest
import VE.Senses.Document

/-! The senses route's request: E2's check of the submitted lexicon (`sensesRequest`), then the reader of a
source or of a document's English fences and front-matter defaults (`readDocument`, RD-8). With no defaults a
source reads as `sensesRequest` reads it (`documentRequest_source`). -/

namespace VE.Senses
open VE.EnglishGrammar

def documentRequest (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (A : Assignment) (t : SenseText) :
    Except String SensesOutcome :=
  if L.policyOk E {} then readDocument D E L b A t else .ok (.invalidGrammar .lexicon)

theorem documentRequest_policy : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (A : Assignment)
    (t : SenseText), L.policyOk E {} = true → documentRequest D E L b A t = readDocument D E L b A t := by
  intro D E L b A t h
  simp [documentRequest, h]

theorem documentRequest_source : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String),
    documentRequest D E L b ⟨[]⟩ (.source s) = .ok (sensesRequest D E L b s) := by
  intro D E L b s
  unfold documentRequest sensesRequest
  cases L.policyOk E {} <;> simp [readDocument_source]

end VE.Senses
