import VE.Judgments.Undeclared

/-! The evaluative words of english-lean's catalogue (docs/spec/judgment-terms-PLAN.md 2.4's catalogue row, O15;
spec 7): the one row list `judgments@0`'s report `undeclared_evaluative` reads. A row is a word and the phrases in
which it has another sense; senses owns the numbered senses and their `sense__<word>_<n>` projection (synthesis
round 2, edit 3), so a row carries no sense of its own. -/

namespace VE.EnglishGrammar

/-- The evaluative words: in translation each is a bound judgment, never a definition the checker chooses. Each row
keeps the phrases in which its word has another sense, so "due date", "due to", "just as", "necessary condition" and
"effective date" match no row. A row is one word (spec 7), so the phrase "good judgment" is not a row here (jt-3p). -/
def evaluativeRows : List VE.Judgments.EvaluativeRow :=
  (["reasonable", "appropriate", "appropriately", "arbitrary", "arbitrarily", "fair", "legitimate", "genuine",
    "genuinely", "adequate", "overly"].map fun w => ⟨w, []⟩) ++
  [⟨"just", [["just", "as"]]⟩, ⟨"effective", [["effective", "date"]]⟩,
   ⟨"necessary", [["necessary", "condition"]]⟩, ⟨"due", [["due", "date"], ["due", "to"]]⟩]

end VE.EnglishGrammar
