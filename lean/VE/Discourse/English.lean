import VE.Discourse.WellFormed
import VE.English.Proofs

/-! # English correspondence of the reviewed presentation (docs/spec/discourse.md 6, 9.5)

`Meaning := VE.Formula`: an assignment is provenance validated separately
(`validate_slots_recorded`), not part of the meaning, because the expansion has no slots. The
reviewed presentation of a bound unit is the canonical core rendering of its elaborated
formula; `presentation_expands` shows it parses, through the unchanged core parser, to exactly
that formula, and `discourse_parseRender` is the round trip on the discourse surface. The
lexicon hypothesis `LexiconCovers` is the core lexicon's admission and coverage conditions.

Not stated here (lean/DISCOURSE.md): `UniqueDerivation`, `ParseSound` and `OneReading` for the
surface of 9.5, because there `parse` reads the presentation (core English) while a derivation
yields the source text (discourse English), so a parse result is in general not the reading of
a derivation of that same text. Uniqueness of the accepted derivation is `accepted_unique` and
`Accepted`'s own clause. -/
namespace VE.Discourse
open VE.English (Tok Lexicon)

/-- The lexicon admission and coverage hypothesis. -/
def LexiconCovers (L : Lexicon) (E : VE.Environment) : Prop := VE.English.Admitted L ∧ VE.English.Covers L E

/-- The reviewed presentation of a unit: the canonical core rendering of its elaborated formula. -/
def presentation (D : DDoc) (L : Lexicon) (u : String) : List Tok :=
  match validate D u with
  | .ok A => VE.English.render L [A]
  | .error _ => []

/-- A unit whose validated formula is `A` (the first bound unit), for rendering a meaning. -/
def unitOfFormula (D : DDoc) (A : VE.Formula) : String :=
  ((boundUnits D).find? fun u => match validate D u with
    | .ok B => B == A
    | .error _ => false).getD ""

/-- The recorded targets of a derivation's slots, as an assignment. -/
def recordedAssignment (D : DDoc) (d : DTree) : Assignment := assignOf d.slots ((recordedVec D d).getD [])

def discourseSurface (D : DDoc) (L : Lexicon) : VE.English.Surface where
  Text := List Tok
  Meaning := VE.Formula
  Derivation := DTree
  admitted := fun A => ∃ u, validate D u = .ok A
  render := fun A => VE.English.render L [A]
  parse := fun s => match VE.English.parse D.E L s with
    | some [A] => some A
    | _ => none
  derives := fun d => ∃ u s, D.text u = some s ∧ Derives D u s d
  yield := fun d => ((d.slots.head?.map Slot.unit).bind D.text).getD []
  reading := fun d => elaborateD D d (recordedAssignment D d)

/-- The reviewed presentation is ordinary English with the same formula: the expansion parses,
through the unchanged core parser, to exactly the elaborated formula. -/
theorem presentation_expands (D : DDoc) (h : WellFormedDiscourse D = true) (L : Lexicon)
    (hL : LexiconCovers L D.E) (u : String) (A : VE.Formula) (hv : validate D u = .ok A) :
    VE.English.parse D.E L (presentation D L u) = some [A] := by
  unfold presentation
  rw [hv]
  exact VE.English.core_parse_render hL.1 hL.2 [A] ⟨by simp, by simp [validate_closed D u A hv]⟩

/-- The round trip on the discourse surface: parsing the rendering of an admitted meaning gives
that meaning back. -/
theorem discourse_parseRender (D : DDoc) (h : WellFormedDiscourse D = true) (L : Lexicon)
    (hL : LexiconCovers L D.E) : VE.English.ParseRender (discourseSurface D L) := by
  intro A ⟨u, hv⟩
  have hp : VE.English.parse D.E L (VE.English.render L [A]) = some [A] :=
    VE.English.core_parse_render hL.1 hL.2 [A] ⟨by simp, by simp [validate_closed D u A hv]⟩
  show (match VE.English.parse D.E L (VE.English.render L [A]) with
    | some [A] => some A
    | _ => none) = some A
  rw [hp]

/-- Injectivity of the canonical renderer on admitted meanings follows. -/
theorem discourse_renderInjective (D : DDoc) (h : WellFormedDiscourse D = true) (L : Lexicon)
    (hL : LexiconCovers L D.E) : VE.English.RenderInjective (discourseSurface D L) :=
  VE.English.renderInjective_of_parseRender (discourse_parseRender D h L hL)

end VE.Discourse
