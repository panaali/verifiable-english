import VE.Norms.Wire
import VE.Readings.Strings

/-! Theorems of `VE.Acts.Lexical` stated above both `Norms.Wire` and `Acts.Lexical` (docs/spec/act-phrases.md 4.3),
where the string lemmas they use are available. -/

namespace VE.Acts.Lexical

/-- A plain predicate's wording begins with its subject slot. -/
theorem wording_subject_first (f : Form) (act : String) (_h : act.startsWith "{0} " = true) :
    (wording f act).startsWith "{0} " = true := by
  unfold wording
  rw [String.append_assoc, String.append_assoc]
  exact VE.Readings.startsWith_append_ascii _ _ (by decide)

end VE.Acts.Lexical
