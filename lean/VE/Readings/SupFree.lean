import VE.Readings.UpSlot

/-! Conflict-freedom under every reading, in one check (docs/spec/composition-s2.md 4.4, 8.4
`superpose_conflict_free`; no non-emptiness hypothesis on either side).

`sup D` is conflict-free under the slot and the atoms of `A` exactly when every compatible choice that takes `A`'s
candidates has a conflict-free document. Downward, a slot-admissible base encodes such a choice
(`encodes_unique`, `encodes_atoms`), pulls back to an admissible base of its document (`base_down`), and the two
conflict-freedoms agree there (`superpose_conflict_iff`). Upward, a base of the choice's document with an element is
lifted (`upB`); the conflict formulas of the document read the pulled lift as they read the base (they are typed
over the document's base vocabulary, which holds no choice symbol). A base with no element has no typed tuple of a
regulated predicate's sorts, which have one or two places, so it is conflict-free outright. -/
namespace VE.Readings
open VE.Norms (envAt size Regulated tupleVal Sat ConstantsTyped)
open VE.SoftNorms (SoftNode SoftDoc soften canon envPrime)
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP ConflictFreeP)
universe u

theorem conflictFree_empty {Dd : VE.Norms.Doc} (hv : VE.Norms.Valid Dd) (B : VE.Structure.{u})
    (hne : ¬ Nonempty B.Carrier) : VE.Norms.ConflictFree Dd B := by
  have hnil : ∀ (ss : List String) (vs : List B.Carrier), VE.Norms.Arity ss → ¬ VE.TupleTyped B ss vs := by
    intro ss vs ha ht
    cases ss with
    | nil => simp [VE.Norms.Arity] at ha
    | cons s ss =>
      cases vs with
      | nil => exact ht
      | cons v _ => exact hne ⟨v⟩
  refine ⟨fun r hr vs hvs _ => hnil _ vs (VE.Norms.regulated_arity hv (hv.regulated r hr)) hvs,
    fun pr hpr vs hvs _ => ?_⟩
  obtain ⟨_, ⟨i, r, hi, _, hrs, _⟩, _⟩ := VE.Norms.pair_members hv hpr
  have ha := VE.Norms.regulated_arity hv (List.mem_of_getElem? hi)
  rw [hrs] at ha
  exact hnil _ vs ha hvs

section Up
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) (B₀ : VE.Structure.{u}) (e : B₀.Carrier)
  (hB₀ : VE.SoftNorms.BaseAdmissible' (choiceDoc D c).1.soft B₀)
include hh hc hB₀

/-- The choice's document reads its conflict formulas on the pulled lift as on `B₀`. -/
theorem up_conflictFree
    (hcf : VE.Norms.ConflictFree (soften (choiceDoc D c).1.soft) (pull D c (upB D c B₀ e))) :
    VE.Norms.ConflictFree (soften (choiceDoc D c).1.soft) B₀ := by
  have hvY := choice_valid hh hc
  have hadm := hB₀.1.1
  have lift : ∀ (φ : VE.Formula) (Γ : List String), φ.WellFormed (envAt (soften (choiceDoc D c).1.soft) 0) Γ →
      φ.WellFormed (envPrime (choiceDoc D c).1.soft) Γ := fun φ Γ h =>
    VE.Norms.wf_mono (E := envAt (soften (choiceDoc D c).1.soft) 0) (E' := envPrime (choiceDoc D c).1.soft)
      rfl rfl (fun r ss h => envAt_sub h) φ Γ h
  have regFree : ∀ r ∈ (choiceDoc D c).1.soft.T.regulated, ∀ s ∈ r.sorts, s ≠ "ve__reading" := by
    intro r hr s hs
    have hsym := hvY.regulated r hr
    have h1 := (choice_decl hh hsym).2.2 s hs
    rw [envPrime_sorts, choice_E c] at h1
    rintro rfl
    exact frame_sorts_free hh.wf h1
  have ttp : ∀ (ss : List String) (vs : List B₀.Carrier), VE.TupleTyped B₀ ss vs →
      VE.TupleTyped (pull D c (upB D c B₀ e)) ss vs := fun ss vs h =>
    (VE.Route.Examples.tupleTyped_relation (upB D c B₀ e) _ ss vs).mpr (tt_up h)
  refine ⟨fun r hr vs hvs hx => ?_, fun pr hpr vs hvs hx => ?_⟩
  · obtain ⟨k, hk⟩ := VE.Norms.mem_syms_index (hvY.regulated r hr)
    have hw := VE.Norms.conflict_wellFormed hvY hk
    exact hcf.1 r hr vs (ttp _ vs hvs) ((pull_up hh B₀ e hadm _ _ (lift _ _ hw) _).mpr hx)
  · have hw := VE.Norms.pairConflict_wellFormed hvY hpr
    exact hcf.2 pr hpr vs (ttp _ vs hvs) ((pull_up hh B₀ e hadm _ _ (lift _ _ hw) _).mpr hx)

end Up

theorem superpose_conflict_free (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome) :
    ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A) ↔
      ∀ c, Compatible D c → (∀ x ∈ A, x ∈ c) → VE.Rights.RightsConflictFree.{u} (choiceDoc D c).1 := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  constructor
  · intro hcf c hc hAc B₀ hB
    have hYn := choiceDoc_noRights D c hh.noRights
    rw [(correlate_noRights _ hYn).1]
    have hB₀ : VE.SoftNorms.BaseAdmissible' (choiceDoc D c).1.soft B₀ := by
      have := hB.1; rwa [(correlate_noRights _ hYn).1] at this
    by_cases hne : Nonempty B₀.Carrier
    · obtain ⟨e⟩ := hne
      have hcm : complete D c = true := by
        simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
      have henc := upB_encodes hh.ready hc B₀ e
      have hBs : BaseAdmissibleP (correlate (sup D).1) (slotP D) (upB D c B₀ e) := by
        rw [sup_correlate hh]
        refine ⟨⟨⟨upB_admissible hh hc B₀ e hB₀.1.1, upB_literals hh B₀ e hB₀.1.2⟩, ?_⟩, upB_slot hh hc B₀ e⟩
        intro a ha
        rcases List.mem_append.mp ha with ha | ha
        · exact upB_exc hh hc B₀ e hB₀ a ha
        · exact upB_coh hh hc B₀ e hB₀ a ha
      have hBA : BaseAdmissibleP (correlate (sup D).1) (slotUnder D A) (upB D c B₀ e) :=
        ⟨hBs.1, fun a ha => by
          rcases List.mem_append.mp ha with ha | ha
          · exact hBs.2 a ha
          · exact (encodes_atoms D c hcm _ henc A).mpr hAc a ha⟩
      have hX := hcf _ hBA
      have hY := (superpose_conflict_iff D h hch hs c hc _ hBs henc).mp hX
      rw [choice_correlate hh c] at hY
      exact up_conflictFree hh hc B₀ e hB₀ hY
    · exact conflictFree_empty (choice_valid hh hc) B₀ hne
  · intro hall B hB
    have hBs : BaseAdmissibleP (correlate (sup D).1) (slotP D) B :=
      ⟨hB.1, fun a ha => hB.2 a (List.mem_append_left _ ha)⟩
    obtain ⟨c, hc, he, _⟩ := encodes_unique D h hch hs B hBs
    have hcm : complete D c = true := by
      simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
    have hAc := (encodes_atoms D c hcm B he A).mp (fun a ha => hB.2 a (List.mem_append_right _ ha))
    have hY := hall c hc hAc _ (base_down D h hch hs c hc B hBs he)
    exact (superpose_conflict_iff D h hch hs c hc B hBs he).mpr hY

end VE.Readings
