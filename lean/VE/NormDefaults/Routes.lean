import VE.NormDefaults.Evidence
import VE.Rights.Semantics
import VE.Alternatives.Followable

/-! Route corollaries (docs/spec/norm-defaults.md 3.3 and 7): `fill` runs last on
every route (`fill(soften T)`, `fill(soften(correlate D))`, `fill(inlineTree A)`),
so `Value3` on each route reads that route's decisions.

`fill_soft_value` (by `decidesD_soften`), `excepted_lifts` (the collapse of the
plan's section 0 removed: an excepted sole default rule leaves an unspecified act
unsaid) with its deny companion, `fill_rights_value` (by `decidesD_soften` and
`VE.Rights.decides_eq`, the content of `correlate_faithful`) and
`followableU_sound` (FOLLOWABLE on the filled tree, `Fill_T` in the background). -/
namespace VE.NormDefaults
open VE.Norms VE.Route
open VE.SoftNorms (SoftDoc SoftNode soften DecidesSoftD SelectsSoftD AppliesSoftD EffD EligibleD LiveD exceptedF
  decidesD_soften rankFuel)
universe u

/-! ## Soft norms -/

/-- `fill_soft_value`: on the soft route the three-valued value reads soft decisions. -/
theorem fill_soft_value (D : SoftDoc) (unspec : List String) (h : WellFormedU ⟨soften D, unspec⟩ = true)
    (r : Regulated) (hr : r ∈ D.T.regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) :
    Value3 ⟨soften D, unspec⟩ r S vs =
      value3 (DecidesSoftD D S (tupleVal vs) r.name true) (DecidesSoftD D S (tupleVal vs) r.name false)
        (completionOf ⟨soften D, unspec⟩ r) := by
  have _ := h
  have _ := hr
  unfold Value3
  rw [propext (decidesD_soften D S (tupleVal vs) r.name true), propext (decidesD_soften D S (tupleVal vs) r.name false)]

/-- An excepted default rule never selects. -/
theorem excepted_not_selects (D : SoftDoc) {N : SoftNode} (hd : N.mode = .default) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (hx : (exceptedF D N).denote S ρ) (f : Nat) : ¬ SelectsSoftD D S ρ f N := by
  rintro ⟨happ, _⟩
  simp only [AppliesSoftD, hd] at happ
  have helig : EligibleD D S ρ N := by
    cases hg : rankFuel D with
    | zero => rw [hg] at happ; exact happ
    | succ g => rw [hg] at happ; exact happ.1
  exact helig.2.1.2.2.2 hd hx

theorem excepted_undecided (D : SoftDoc) (p : String) {N : SoftNode} (hN : VE.SoftNorms.rulesOn D p = [N])
    (hd : N.mode = .default) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (hx : (exceptedF D N).denote S ρ)
    (sign : Bool) : ¬ DecidesSoftD D S ρ p sign := by
  rintro ⟨M, hM, _, hsel⟩
  rw [hN, List.mem_singleton] at hM
  subst hM
  exact excepted_not_selects D hd S ρ hx _ hsel

/-- `excepted_lifts`: the collapse of section 0 removed: an excepted sole default
rule leaves an unspecified act unsaid. -/
theorem excepted_lifts (D : SoftDoc) (unspec : List String) (h : WellFormedU ⟨soften D, unspec⟩ = true)
    (r : Regulated) (hr : r.name ∈ unspec) (N : SoftNode) (hN : VE.SoftNorms.rulesOn D r.name = [N])
    (hd : N.mode = .default) (S : VE.Structure.{u}) (vs : List S.Carrier)
    (hx : (exceptedF D N).denote S (tupleVal vs)) :
    Value3 ⟨soften D, unspec⟩ r S vs = .unsaid := by
  have _ := h
  unfold Value3
  rw [propext (decidesD_soften D S (tupleVal vs) r.name true), propext (decidesD_soften D S (tupleVal vs) r.name false)]
  have h₁ := excepted_undecided D r.name hN hd S _ hx true
  have h₂ := excepted_undecided D r.name hN hd S _ hx false
  simp only [completionOf, hr, if_true]
  unfold value3
  simp [h₁, h₂]

/-- `excepted_collapses_under_deny`: with a deny completion the same situation is
"not permitted" (the collapse, kept as a regression). -/
theorem excepted_collapses_under_deny (D : SoftDoc) (unspec : List String) (h : WellFormedU ⟨soften D, unspec⟩ = true)
    (r : Regulated) (hr : r.name ∉ unspec) (hdeny : r.allowByDefault = false) (N : SoftNode)
    (hN : VE.SoftNorms.rulesOn D r.name = [N]) (hd : N.mode = .default) (S : VE.Structure.{u}) (vs : List S.Carrier)
    (hx : (exceptedF D N).denote S (tupleVal vs)) :
    Value3 ⟨soften D, unspec⟩ r S vs = .no := by
  have _ := h
  unfold Value3
  rw [propext (decidesD_soften D S (tupleVal vs) r.name true), propext (decidesD_soften D S (tupleVal vs) r.name false)]
  have h₁ := excepted_undecided D r.name hN hd S _ hx true
  have h₂ := excepted_undecided D r.name hN hd S _ hx false
  simp only [completionOf, hr, if_false, hdeny, Bool.false_eq_true]
  unfold value3
  simp [h₁, h₂]

/-! ## Rights -/

/-- `fill_rights_value`: on the rights route the three-valued value reads the
rights decisions. It takes `WellFormedRights D`, which `correlate_faithful` needs
and `WellFormedU` does not give. -/
theorem fill_rights_value (D : VE.Rights.RightsDoc) (unspec : List String)
    (h : VE.Rights.WellFormedRights D = true) (r : Regulated) (hr : r ∈ (VE.Rights.correlate D).T.regulated)
    (S : VE.Structure.{u}) (vs : List S.Carrier) :
    Value3 ⟨soften (VE.Rights.correlate D), unspec⟩ r S vs =
      value3 (VE.Rights.DecidesR D S (tupleVal vs) r.name true) (VE.Rights.DecidesR D S (tupleVal vs) r.name false)
        (completionOf ⟨soften (VE.Rights.correlate D), unspec⟩ r) := by
  have _ := hr
  have hv := VE.Rights.rightsValid_of_wellFormed D h
  unfold Value3
  rw [propext (decidesD_soften _ S (tupleVal vs) r.name true), propext (decidesD_soften _ S (tupleVal vs) r.name false),
    propext (VE.Rights.decides_eq hv S (tupleVal vs) r.name true),
    propext (VE.Rights.decides_eq hv S (tupleVal vs) r.name false)]

/-! ## Followability -/

section Alt
open VE.Alternatives

/-- `O_p°` of the filled inlined document. -/
def oBaseU (A : AltDoc) (unspec : List String) (n : String) : VE.Formula :=
  outcomeBase (fill ⟨inlineTree A, unspec⟩) n

/-- Alternatives 4.6's formulas, regenerated on the filled tree. -/
def performedFU (A : AltDoc) (unspec : List String) : VE.Formula :=
  match A.alt.performed with
  | none => .top
  | some (m, q) => .and (inst [.var 0] (oBaseU A unspec m))
      (.all A.alt.action (.implies (.and (.binary A.alt.available (.var 0) (.var 2))
        (inst [.var 0] (oBaseU A unspec q))) (.eq (.var 0) (.var 1))))

def fulfilFU (A : AltDoc) (unspec : List String) (f : Fulfilment) : VE.Formula :=
  match findReg A.T f.obligation with
  | some ro => match ro.sorts.tail with
    | [] => .implies (inst [.var 1] (oBaseU A unspec f.obligation)) (inst [.var 0] f.body)
    | [s] => .all s (.implies (inst [.var 0, .var 2] (oBaseU A unspec f.obligation)) (inst [.var 0, .var 1] f.body))
    | _ => .top
  | none => .top

def clearFU (A : AltDoc) (unspec : List String) : VE.Formula :=
  .and (.binary A.alt.available (.var 0) (.var 1))
    (.and (performedFU A unspec) (allF (A.alt.fulfilments.map (fulfilFU A unspec))))

def followableFU (A : AltDoc) (unspec : List String) : VE.Formula :=
  .implies (.ex A.alt.action (.binary A.alt.available (.var 0) (.var 1))) (.ex A.alt.action (clearFU A unspec))

def allFollowableU (A : AltDoc) (unspec : List String) : VE.Formula := bindAll [A.alt.chooser] (followableFU A unspec)

/-- `Background_baseAlt(E‴) ++ Fill_T`. -/
def backgroundBaseAltU (A : AltDoc) (unspec : List String) : List VE.Formula :=
  backgroundBase (fill ⟨inlineTree A, unspec⟩) ++ altPremises A ++ fillPremises ⟨inlineTree A, unspec⟩

def BaseAdmissibleAltU (A : AltDoc) (unspec : List String) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissibleU ⟨inlineTree A, unspec⟩ B ∧ Sat B (altPremises A)

/-- `followableU_sound`: FOLLOWABLE requires a clear alternative under every
admissible filling; a checked certificate gives it. -/
theorem followableU_sound (A : AltDoc) (unspec : List String) (h : WellFormedU ⟨inlineTree A, unspec⟩ = true)
    (hc : ConflictFreeU.{u} ⟨inlineTree A, unspec⟩) (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (fill ⟨inlineTree A, unspec⟩) 0)
      (backgroundBaseAltU A unspec ++ A.Γ) (allFollowableU A unspec) c = true) :
    ∀ B : VE.Structure.{u}, BaseAdmissibleAltU A unspec B → Sat B A.Γ → (allFollowableU A unspec).denote B [] := by
  have _ := h
  have _ := hc
  intro B hB hΓ
  apply VE.Tableau.checkCertificate_sound.{u} _ _ _ c ok B hB.1.1.1
  intro a ha
  simp only [backgroundBaseAltU, List.mem_append] at ha
  rcases ha with ((ha | ha) | ha) | ha
  · exact hB.1.1.2 a ha
  · exact hB.2 a ha
  · exact hB.1.2 a ha
  · exact hΓ a ha

end Alt

end VE.NormDefaults
