import VE.Readings.BaseDown
import VE.Readings.Route

/-! A checked model of `sup D` is a situation of the reading its atoms encode (docs/spec/composition-s2.md 4.4,
4.5, 8.4 `superpose_conflict_witness`, `superpose_countermodel`).

The model is a slot-admissible base of `sup D` (`baseAdmissibleP_of_valid`); it encodes one compatible choice
(`encodes_unique`), which takes the assumed candidates (`encodes_atoms`); pulled, it is an admissible base of that
choice's document (`base_down`). A conflict witness refutes `sup D`'s conflict-freedom on the model, hence the
choice's on the pulled base (`superpose_conflict_iff`). The model check evaluates the assertions and `Γ` through
the outcome substitution, which is their truth on the expansion (`circ_canon`); `superpose_situation` carries them,
and the falsity of `φ`, to the choice's expansion of the pulled base. -/
namespace VE.Readings
open VE.Norms (envAt size Regulated tupleVal Sat ConstantsTyped targets)
open VE.SoftNorms (SoftNode SoftDoc soften canon envPrime circ)
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP backgroundValidP)
universe u

/-- Well-formedness is monotone in the sorts, constants and predicates declared. -/
theorem wf_sub {E E' : VE.Environment} (hs : ∀ s ∈ E.sorts, s ∈ E'.sorts)
    (hc : ∀ x s, E.constants x = some s → E'.constants x = some s)
    (hp : ∀ r ss, E.predicates r = some ss → E'.predicates r = some ss) :
    ∀ (a : VE.Formula) (Γ : List String), a.WellFormed E Γ → a.WellFormed E' Γ := by
  have ht : ∀ (Γ : List String) (t : VE.Term) (s : String), t.sortOf E Γ = some s → t.sortOf E' Γ = some s := by
    intro Γ t s h
    cases t with
    | var i => exact h
    | const x => exact hc x s h
  intro a
  induction a with
  | top | bottom => intro _ h; exact h
  | unary r t =>
    intro Γ ⟨s, hr, h1⟩
    exact ⟨s, hp _ _ hr, ht _ _ _ h1⟩
  | binary r t w =>
    intro Γ ⟨s, s', hr, h1, h2⟩
    exact ⟨s, s', hp _ _ hr, ht _ _ _ h1, ht _ _ _ h2⟩
  | eq t w =>
    intro Γ ⟨s, h1, h2⟩
    exact ⟨s, ht _ _ _ h1, ht _ _ _ h2⟩
  | not a ih => intro Γ h; exact ih Γ h
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro Γ h; exact ⟨ia Γ h.1, ib Γ h.2⟩
  | all s a ih | ex s a ih =>
    intro Γ h; exact ⟨hs _ h.1, ih _ h.2⟩

section Lift
variable {D : Doc} (hh : Hyps D)
include hh

/-- A sentence over the shared vocabulary is one over `sup D`'s complete vocabulary. -/
theorem shared_lift {φ : VE.Formula} {Γ : List String} (hφ : φ.WellFormed (sharedEnv D) Γ) :
    φ.WellFormed (envAt (soften (sup D).1.soft) (size (soften (sup D).1.soft))) Γ := by
  have hd : (VE.Norms.layerNames (soften (sup D).1.soft).T).drop (size (soften (sup D).1.soft)) = [] := by
    simp [VE.Norms.layerNames, VE.Norms.size]
  refine wf_sub ?_ ?_ ?_ φ Γ hφ
  · intro s hs
    rw [sharedEnv_sorts] at hs
    show s ∈ (sup D).1.soft.E.sorts
    rw [sup_E]
    unfold choiceEnv
    split
    · exact hs
    · exact List.mem_append_left _ hs
  · intro x s hx
    rw [sharedEnv_constants] at hx
    exact frame_const_sup hh hx
  · intro p ss hp
    have h1 := free_envPrime_sub hh [] (sharedEnv_sub hh hp)
    have h2 := envPrime_nameMap hh [] h1
    rw [nameMap_shared hh [] (by rw [sharedEnv_sub hh hp]; simp)] at h2
    simp only [envAt, hd, VE.Norms.hide, List.not_mem_nil, if_false]
    exact h2

end Lift

theorem typed_nil (S : VE.Structure.{u}) : VE.Valuation.Typed S [] [] := fun i s h => by simp at h

theorem superpose_conflict_witness {α : Type u} [DecidableEq α] (D : Doc) (h : WellFormedDoc D = true)
    (hch : D.chain ≠ .rights) (hs : superposable D = true) (A : Choice)
    (t : String × List String × VE.Formula) (ht : t ∈ targets (soften (correlate (sup D).1)))
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (soften (correlate (sup D).1)) 0))
    (hb : backgroundValidP (correlate (sup D).1) (slotUnder D A) M = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure t.2.1 vs) (hw : t.2.2.eval M (tupleVal vs) = true) :
    ∃ c, Compatible D c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes D c M.asStructure ∧
      VE.Rights.BaseAdmissibleR (choiceDoc D c).1 (pull D c M.asStructure) ∧
      ¬ VE.Norms.ConflictFree (soften (correlate (choiceDoc D c).1)) (pull D c M.asStructure) := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  have hB := VE.Compose.baseAdmissibleP_of_valid _ _ M valid hb
  have hBs : BaseAdmissibleP (correlate (sup D).1) (slotP D) M.asStructure :=
    ⟨hB.1, fun a ha => hB.2 a (List.mem_append_left _ ha)⟩
  obtain ⟨c, hc, he, _⟩ := encodes_unique D h hch hs M.asStructure hBs
  have hcomp : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hA := (encodes_atoms D c hcomp M.asStructure he A).mp (fun a ha => hB.2 a (List.mem_append_right _ ha))
  have hwf : VE.SoftNorms.WellFormedSoft (correlate (sup D).1) := by
    rw [sup_correlate hh]; exact sup_wfSoft hh
  have hn := (VE.Compose.slot_conflict_witness_sound _ hwf _ t ht M valid hb vs typed hw).1
  exact ⟨c, hc, hA, he, base_down D h hch hs c hc _ hBs he,
    fun hcf => hn ((superpose_conflict_iff D h hch hs c hc _ hBs he).mpr hcf)⟩

/-- A checked model on sup D is a situation of the reading its atoms encode; with φ it is a countermodel there.
    The premise model of 4.5 is the case Γ := [], φ := ⊥. -/
theorem superpose_countermodel {α : Type u} [DecidableEq α] (D : Doc) (h : WellFormedDoc D = true)
    (hch : D.chain ≠ .rights) (hs : superposable D = true) (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (soften (correlate (sup D).1)) 0)) (hm : supModelCheck D A Γ M = true)
    (hn : (circ (correlate (sup D).1) φ).eval M [] = false) :
    ∃ c, Compatible D c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes D c M.asStructure ∧
      VE.Rights.BaseAdmissibleR (choiceDoc D c).1 (pull D c M.asStructure) ∧
      Sat (expand (choiceDoc D c).1 (pull D c M.asStructure)) ((choiceDoc D c).2 ++ Γ) ∧
      ¬ φ.denote (expand (choiceDoc D c).1 (pull D c M.asStructure)) [] := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  simp only [supModelCheck, Bool.and_eq_true, List.all_eq_true] at hm
  obtain ⟨hb, hall⟩ := hm
  have hB := VE.Compose.baseAdmissibleP_of_valid _ _ M valid hb
  have hBs : BaseAdmissibleP (correlate (sup D).1) (slotP D) M.asStructure :=
    ⟨hB.1, fun a ha => hB.2 a (List.mem_append_left _ ha)⟩
  obtain ⟨c, hc, he, _⟩ := encodes_unique D h hch hs M.asStructure hBs
  have hcomp : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hA := (encodes_atoms D c hcomp M.asStructure he A).mp (fun a ha => hB.2 a (List.mem_append_right _ ha))
  obtain ⟨_, hsh, has⟩ := superpose_situation D h hch hs c hc _ hBs he
  -- the model's truth through the outcome substitution is truth on the expansion
  have hBX := hBs
  rw [sup_correlate hh] at hBX
  have hcirc : ∀ a : VE.Formula, a.WellFormed (envAt (soften (sup D).1.soft) (size (soften (sup D).1.soft))) [] →
      ((circ (correlate (sup D).1) a).eval M [] = true ↔ a.denote (expand (sup D).1 M.asStructure) []) := by
    intro a ha
    rw [VE.eval_iff_denote, expand, sup_correlate hh]
    exact VE.SoftNorms.circ_canon (sup_softValid hh) _ hBX.1.1 a [] ha [] (typed_nil _)
  have hsupwf : ∀ a ∈ (sup D).2, a.WellFormed (envAt (soften (sup D).1.soft) (size (soften (sup D).1.soft))) [] := by
    have hw : sideWF D (sup D) = true := by
      have := hs; simp only [superposable, Bool.and_eq_true] at this; exact this.2
    simp only [sideWF, Bool.and_eq_true, List.all_eq_true] at hw
    intro a ha
    have := (VE.check_iff_wellFormed _ _ _).mp (hw.2 a ha)
    rwa [sup_correlate hh] at this
  refine ⟨c, hc, hA, he, base_down D h hch hs c hc _ hBs he, fun a ha => ?_, fun hφY => ?_⟩
  · rcases List.mem_append.mp ha with ha | ha
    · exact (has.mp (fun b hb => (hcirc b (hsupwf b hb)).mp (hall b (List.mem_append_left _ hb)))) a ha
    · exact (hsh a (hΓ a ha)).mp ((hcirc a (shared_lift hh (hΓ a ha))).mp (hall a (List.mem_append_right _ ha)))
  · have := (hcirc φ (shared_lift hh hφ)).mpr ((hsh φ hφ).mpr hφY)
    rw [hn] at this; cases this

end VE.Readings
