import VE.Discourse.WellFormed
import VE.English.Proofs

/-! # English correspondence of the reviewed presentation (docs/spec/discourse.md 6, 9.5)

`Meaning := VE.Formula`: an assignment is provenance validated separately
(`validate_slots_recorded`), not part of the meaning, because the expansion has no slots. The
reviewed presentation of a bound unit is the canonical core rendering of its elaborated
formula; `presentation_expands` shows it parses, through the unchanged core parser, to exactly
that formula, and `discourse_parseRender` is the round trip on the discourse surface. The
lexicon hypothesis `LexiconCovers` is the core lexicon's admission and coverage conditions.

`UniqueDerivation`, `ParseSound` and `OneReading` are stated over the discourse *source*
surface (`discourseSourceSurface`): there a text is a unit's source tokens, `parse` is the
validator, and a derivation is a well-sorted derivation of an admitted unit with an accessible
assignment (the competitors `Accepted` compares). On the presentation surface of 9.5 `parse`
reads core English while a derivation yields discourse English, so a parse result is in general
not the reading of a derivation of that same text; the round trip is stated there and the
derivation obligations here (lean/DISCOURSE.md). -/
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

/-! ## The discourse source surface (9.5: UniqueDerivation, ParseSound, OneReading) -/

/-- A derivation of an admitted unit that some accessible assignment elaborates to a closed,
well-typed formula: a type-checking competitor of the unit's accepted resolution (4.3). -/
def SourceDerives (D : DDoc) (x : String × DTree) : Prop :=
  ∃ s A, D.text x.1 = some s ∧ validate D x.1 = .ok A ∧ Derives D x.1 s x.2 ∧
    ∃ σ, (∀ m ∈ x.2.slots, Acc D m (σ m)) ∧ ∃ A', elaborateD D x.2 σ = some A' ∧ A'.check D.E [] = true

/-- The source surface: texts are a unit and its tokens, `parse` is the validator on the unit's
own text, a derivation carries its unit, and its reading is the elaboration under the recorded
targets. -/
def discourseSourceSurface (D : DDoc) : VE.English.Surface where
  Text := String × List Tok
  Meaning := VE.Formula
  Derivation := String × DTree
  admitted := fun A => ∃ u, validate D u = .ok A
  render := fun A => (unitOfFormula D A, (D.text (unitOfFormula D A)).getD [])
  parse := fun t => if D.text t.1 = some t.2 then (validate D t.1).toOption else none
  derives := SourceDerives D
  yield := fun x => (x.1, (D.text x.1).getD [])
  reading := fun x => elaborateD D x.2 (recordedAssignment D x.2)

/-- One derivation per text: every type-checking competitor of an admitted unit has the accepted
tree and slots (`Accepted`'s uniqueness clause). -/
theorem discourse_uniqueDerivation (D : DDoc) : VE.English.UniqueDerivation (discourseSourceSurface D) := by
  rintro ⟨u, d⟩ ⟨u', d'⟩ ⟨s, A, hs, hv, hd, σ, hacc, B, he, hc⟩ ⟨s', A', hs', hv', hd', σ', hacc', B', he', hc'⟩ hy
  simp only [discourseSourceSurface, Prod.mk.injEq] at hy
  obtain ⟨rfl, _⟩ := hy
  rw [hs] at hs'
  cases hs'
  obtain ⟨d₀, σ₀, _, _, _, _, hall⟩ := validate_accepted D u A s hs hv
  obtain ⟨ht, hsl, _⟩ := hall d σ B hd hacc he hc
  obtain ⟨ht', hsl', _⟩ := hall d' σ' B' hd' hacc' he' hc'
  rcases d with ⟨t, sl⟩
  rcases d' with ⟨t', sl'⟩
  show (u, DTree.mk t sl) = (u, DTree.mk t' sl')
  simp only at ht hsl ht' hsl'
  rw [ht.trans ht'.symm, hsl.trans hsl'.symm]

/-- Every parse is the reading of a derivation of that text. -/
theorem discourse_parseSound (D : DDoc) : VE.English.ParseSound (discourseSourceSurface D) := by
  rintro ⟨u, s⟩ A hp
  simp only [discourseSourceSurface] at hp
  split at hp
  · rename_i hs
    cases hv : validate D u with
    | error e => rw [hv] at hp; cases hp
    | ok A₀ =>
      rw [hv] at hp
      simp only [Except.toOption, Option.some.injEq] at hp
      subst hp
      obtain ⟨_, s', d, vec, A₁, rest, rvec, hs', _, hc, _, hr, hacc, _, _, hA, hck⟩ := validate_ok D u A₀ hv
      rw [hs] at hs'
      cases hs'
      have hmem : (d, vec, A₁) ∈ typedComps D (derivs D u s) := by rw [hc]; exact List.mem_cons_self
      obtain ⟨hdm, _, _, _⟩ := (mem_typedComps D _ d vec A₁).mp hmem
      obtain ⟨hlen, _⟩ := mapM_recorded D d.slots rvec hr
      refine ⟨(u, d), ⟨s, A₀, hs, hv, (mem_derivs D u s d).mp hdm, assignOf d.slots rvec,
        zip_all_assign (fun m t => accB D m t) d.slots rvec hlen hacc, A₀, hA, hck⟩, ?_, ?_⟩
      · simp [discourseSourceSurface, hs]
      · show elaborateD D d (assignOf d.slots ((recordedVec D d).getD [])) = some A₀
        rw [hr]
        exact hA
  · cases hp

/-- One reading per accepted text: every derivation of a text the validator accepts reads as the
validated formula. -/
theorem discourse_oneReading (D : DDoc) : VE.English.OneReading (discourseSourceSurface D) :=
  VE.English.oneReading_of (discourse_parseSound D) (discourse_uniqueDerivation D)

end VE.Discourse
