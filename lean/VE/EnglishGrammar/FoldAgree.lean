import VE.EnglishGrammar.Token
import VE.Discourse.Access

/-! The test of spec R13: the case-folding table of the English instance is the table of the discourse
lexer. The English reader does not import the discourse modules; only this file and the audit manifest
do. -/

namespace VE.EnglishGrammar

/-- The English fold of a character is the discourse fold, or the character itself where the discourse
fold has none. -/
theorem foldChar_agrees (c : Char) : foldChar c = (VE.Discourse.foldChar c).getD c := by
  unfold foldChar VE.Discourse.foldChar
  split <;> (try split) <;> (try split) <;> (try split) <;> simp_all

end VE.EnglishGrammar
