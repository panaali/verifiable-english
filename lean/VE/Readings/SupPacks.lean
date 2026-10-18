import VE.Readings.SupExtra
import VE.NormDefaults.Packs

/-! Premise packs on the superposed readings route (docs/spec/premise-packs.md 2.11): carried families concatenate,
so one family per pack gives the family of the packs' `X`, in `X` order (`transfers_nil` is the empty case). -/
namespace VE.Readings
universe u

/-- 2.11: carried families concatenate. -/
theorem transfers_append (D : Doc) (Q₁ Q₂ : List VE.Formula) (Q₁c Q₂c : Choice → List VE.Formula)
    (h₁ : Transfers.{u} D Q₁ Q₁c) (h₂ : Transfers.{u} D Q₂ Q₂c) :
    Transfers.{u} D (Q₁ ++ Q₂) (fun c => Q₁c c ++ Q₂c c) := by
  refine ⟨fun c hc a ha => ?_, fun c hc B hB he => ?_⟩
  · rcases List.mem_append.mp ha with ha | ha
    · exact h₁.1 c hc a ha
    · exact h₂.1 c hc a ha
  · rw [VE.Compose.sat_append, VE.Compose.sat_append]
    exact and_congr (h₁.2 c hc B hB he) (h₂.2 c hc B hB he)

/-- 2.11: one family per pack gives the family of `X`. -/
theorem transfers_X (D : Doc) (qs : List VE.NormDefaults.Packs.Pack)
    (Qc : VE.NormDefaults.Packs.Pack → Choice → List VE.Formula)
    (h : ∀ p ∈ qs, Transfers.{u} D (p.labelled.map (·.2)) (Qc p)) :
    Transfers.{u} D (VE.NormDefaults.Packs.X qs) (fun c => qs.flatMap (fun p => Qc p c)) := by
  induction qs with
  | nil => exact transfers_nil D
  | cons p ps ih =>
    have hX : VE.NormDefaults.Packs.X (p :: ps) =
        p.labelled.map (·.2) ++ VE.NormDefaults.Packs.X ps := by
      simp [VE.NormDefaults.Packs.X, VE.NormDefaults.Packs.labelledX]
    rw [hX]
    exact transfers_append D _ _ (Qc p) (fun c => ps.flatMap (fun p => Qc p c))
      (h p (List.mem_cons_self ..)) (ih (fun q hq => h q (List.mem_cons_of_mem _ hq)))

end VE.Readings
