import VE.Readings.Situation

/-! Conflict-freedom of `sup D` and of a reading's document (docs/spec/composition-s2.md 4.4, 8.4
`superpose_conflict_iff`).

W1's conflict formulas are read on a base through the outcome substitution; on a document whose softened form is
`Valid` they are the decisions of the canonical interpretation (`conflict_canon_valid`, `outcome_canon_valid`, the forms of
`VE.SoftNorms.conflict_canon` and `outcome_canon` that ask only `Valid` of the softened document, since a reading's
document is not known to pass the chain's size limits). On a base of `sup D` that encodes `c`, the decisions of the
two canonical interpretations agree (`superpose_faithful`'s simulation, then Lemma K), so each conflict formula of one
document holds exactly when the same formula of the other does. -/
namespace VE.Readings
open VE.Norms (envAt size Regulated tupleVal Sat ConstantsTyped)
open VE.SoftNorms (SoftNode SoftDoc soften canon DecidesSoftD envPrime)
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP)
universe u

section Canon
variable {Z : SoftDoc} (hv : VE.Norms.Valid (soften Z)) (B : VE.Structure.{u})
  (hc : ConstantsTyped (soften Z) B)
include hv hc

theorem conflict_canon_valid {r : Regulated} (hr : r ∈ Z.T.regulated) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (VE.Norms.conflict (soften Z) r).denote B (tupleVal vs) ↔
      DecidesSoftD Z (canon (soften Z) B) (tupleVal vs) r.name true ∧
        DecidesSoftD Z (canon (soften Z) B) (tupleVal vs) r.name false := by
  have hk := VE.Norms.index_before hv hr
  have hT := VE.Norms.rulesTyped_of_valid hv hk
  have hρ := VE.Norms.tupleVal_typed B _ vs hvs
  simp only [VE.Norms.conflict, VE.Norms.pos, VE.Norms.neg, VE.Formula.denote]
  rw [VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.decides_wellFormed hT true) _ hρ,
    VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.decides_wellFormed hT false) _ hρ,
    VE.Norms.decides_denote, VE.Norms.decides_denote, VE.SoftNorms.decidesD_soften, VE.SoftNorms.decidesD_soften]

theorem outcome_canon_valid {r : Regulated} (hr : r ∈ Z.T.regulated) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (VE.Norms.outcomeBase (soften Z) r.name).denote B (tupleVal vs) ↔
      (if r.allowByDefault then ¬ DecidesSoftD Z (canon (soften Z) B) (tupleVal vs) r.name false
       else DecidesSoftD Z (canon (soften Z) B) (tupleVal vs) r.name true) := by
  have hk := VE.Norms.index_before hv hr
  have hT := VE.Norms.rulesTyped_of_valid hv hk
  have hρ := VE.Norms.tupleVal_typed B _ vs hvs
  simp only [VE.Norms.outcomeBase, VE.Norms.find_regulated hv hk]
  rw [VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.outcome_wellFormed hT) _ hρ, VE.Norms.outcome_denote,
    VE.Norms.pos, VE.Norms.neg, VE.Norms.decides_denote, VE.Norms.decides_denote, VE.SoftNorms.decidesD_soften,
    VE.SoftNorms.decidesD_soften]

end Canon

section CF
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) (B : VE.Structure.{u})
  (hcB : ConstantsTyped (soften (sup D).1.soft) B) (he : Encodes D c B)
include hh

include hcB in
theorem constantsTyped_pull : ConstantsTyped (soften (choiceDoc D c).1.soft) (pull D c B) := by
  intro x s hx
  rw [soften_E, envPrime_constants, choice_E c] at hx
  exact hcB x s (frame_const_sup hh hx)

include hc hcB he in
/-- On a base that encodes `c`, the two canonical interpretations decide alike. -/
theorem decides_iff {r : Regulated} (hr : r ∈ (choiceDoc D c).1.soft.T.regulated) (vs : List B.Carrier)
    (sign : Bool) :
    DecidesSoftD (sup D).1.soft (canon (soften (sup D).1.soft) B) (tupleVal vs) r.name sign ↔
      DecidesSoftD (choiceDoc D c).1.soft (canon (soften (choiceDoc D c).1.soft) (pull D c B)) (tupleVal vs)
        r.name sign :=
  (sim_decides (faithful_sim hh hc (canon (soften (sup D).1.soft) B) (encodes_canon hh B he) (tupleVal vs))
    r.name sign).trans
    (decides_pull_canon hh hc B (fun x s h => (hcB x s h).imp fun _ h => h.1) he hr _ sign)

include hc hcB he in
theorem outcomeBase_iff (n : String) (vs : List B.Carrier)
    (hvs : ∀ r, (choiceDoc D c).1.soft.T.regulated.find? (·.name == n) = some r → VE.TupleTyped B r.sorts vs) :
    (VE.Norms.outcomeBase (soften (sup D).1.soft) n).denote B (tupleVal vs) ↔
      (VE.Norms.outcomeBase (soften (choiceDoc D c).1.soft) n).denote (pull D c B) (tupleVal vs) := by
  have eX : (soften (sup D).1.soft).T.regulated = (choiceDoc D c).1.soft.T.regulated := regs_eq c
  have eY : (soften (choiceDoc D c).1.soft).T.regulated = (choiceDoc D c).1.soft.T.regulated := rfl
  cases hf : (choiceDoc D c).1.soft.T.regulated.find? (·.name == n) with
  | none => simp only [VE.Norms.outcomeBase, eX, eY, hf]; exact Iff.rfl
  | some r =>
    have hr := List.mem_of_find?_eq_some hf
    have hn : r.name = n := by simpa using List.find?_some hf
    subst hn
    rw [outcome_canon_valid (sup_valid hh) B hcB (by rw [regs_eq c]; exact hr) vs (hvs r hf),
      outcome_canon_valid (choice_valid hh hc) (pull D c B) (constantsTyped_pull hh B hcB) hr vs
        ((VE.Route.Examples.tupleTyped_relation B _ _ vs).mpr (hvs r hf))]
    simp only [decides_iff hh hc B hcB he hr vs]

end CF

theorem superpose_conflict_iff (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (c : Choice) (hc : Compatible D c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) (he : Encodes D c B) :
    VE.Norms.ConflictFree (soften (correlate (sup D).1)) B ↔
      VE.Norms.ConflictFree (soften (correlate (choiceDoc D c).1)) (pull D c B) := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  rw [sup_correlate hh, choice_correlate hh c]
  have hcB : ConstantsTyped (soften (sup D).1.soft) B := by
    have := hB.1.1.1.1; rw [sup_correlate hh] at this; exact this
  have hvY := choice_valid hh hc
  have hcY := constantsTyped_pull hh (c := c) B hcB
  have eX : (soften (sup D).1.soft).T.regulated = (choiceDoc D c).1.soft.T.regulated := regs_eq c
  have hpairs : VE.Norms.pairs (soften (sup D).1.soft).T = VE.Norms.pairs (soften (choiceDoc D c).1.soft).T := by
    unfold VE.Norms.pairs; rw [eX]; rfl
  have hconf : ∀ r ∈ (choiceDoc D c).1.soft.T.regulated, ∀ vs : List B.Carrier, VE.TupleTyped B r.sorts vs →
      ((VE.Norms.conflict (soften (sup D).1.soft) r).denote B (tupleVal vs) ↔
        (VE.Norms.conflict (soften (choiceDoc D c).1.soft) r).denote (pull D c B) (tupleVal vs)) := by
    intro r hr vs hvs
    rw [conflict_canon_valid (sup_valid hh) B hcB (by rw [regs_eq c]; exact hr) vs hvs,
      conflict_canon_valid hvY (pull D c B) hcY hr vs ((VE.Route.Examples.tupleTyped_relation B _ _ vs).mpr hvs), decides_iff hh hc B hcB he hr vs true,
      decides_iff hh hc B hcB he hr vs false]
  have hpair : ∀ pr ∈ VE.Norms.pairs (soften (choiceDoc D c).1.soft).T, ∀ vs : List B.Carrier,
      VE.TupleTyped B pr.sorts vs →
      ((VE.Norms.pairConflict (soften (sup D).1.soft) pr).denote B (tupleVal vs) ↔
        (VE.Norms.pairConflict (soften (choiceDoc D c).1.soft) pr).denote (pull D c B) (tupleVal vs)) := by
    intro pr hpr vs hvs
    obtain ⟨_, ⟨i, r, hi, hrn, hrs, _⟩, ⟨j, m, hj, hmn, hms, _⟩⟩ := VE.Norms.pair_members hvY hpr
    have hfr := VE.Norms.find_regulated hvY hi
    have hfm := VE.Norms.find_regulated hvY hj
    rw [hrn] at hfr
    rw [hmn] at hfm
    have typed : ∀ n r', (choiceDoc D c).1.soft.T.regulated.find? (·.name == n) = some r' →
        (n = pr.req ∨ n = pr.perm) → VE.TupleTyped B r'.sorts vs := by
      rintro n r' hf (rfl | rfl)
      · have : r' = r := Option.some.inj (hf.symm.trans hfr)
        rw [this, hrs]; exact hvs
      · have : r' = m := Option.some.inj (hf.symm.trans hfm)
        rw [this, hms]; exact hvs
    simp only [VE.Norms.pairConflict, VE.Formula.denote]
    rw [outcomeBase_iff hh hc B hcB he pr.req vs (fun r' hf => typed _ r' hf (Or.inl rfl)),
      outcomeBase_iff hh hc B hcB he pr.perm vs (fun r' hf => typed _ r' hf (Or.inr rfl))]
  unfold VE.Norms.ConflictFree
  rw [hpairs]
  have tp : ∀ ss (vs : List B.Carrier), VE.TupleTyped (pull D c B) ss vs ↔ VE.TupleTyped B ss vs :=
    fun ss vs => VE.Route.Examples.tupleTyped_relation B _ ss vs
  constructor
  · rintro ⟨h1, h2⟩
    refine ⟨fun r hr vs hvs => fun hx => ?_, fun pr hpr vs hvs => fun hx => ?_⟩
    · exact h1 r (by rw [eX]; exact hr) vs ((tp _ vs).mp hvs) ((hconf r hr vs ((tp _ vs).mp hvs)).mpr hx)
    · exact h2 pr hpr vs ((tp _ vs).mp hvs) ((hpair pr hpr vs ((tp _ vs).mp hvs)).mpr hx)
  · rintro ⟨h1, h2⟩
    refine ⟨fun r hr vs hvs => fun hx => ?_, fun pr hpr vs hvs => fun hx => ?_⟩
    · have hr' : r ∈ (choiceDoc D c).1.soft.T.regulated := by rw [← regs_eq c]; exact hr
      exact h1 r hr' vs ((tp _ vs).mpr hvs) ((hconf r hr' vs hvs).mp hx)
    · exact h2 pr hpr vs ((tp _ vs).mpr hvs) ((hpair pr hpr vs hvs).mp hx)

end VE.Readings
