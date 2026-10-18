import VE.Norms.Tree

/-! The one scan of open names in formulas (docs/spec/judgment-terms.md section 3). Rights' `nodeOpen` and the
judgments' dependence (`VE.Judgments.dependsOn`) both call it. This file imports only `VE.Norms.Tree`, so rights can
import it. -/

namespace VE.Judgments

/-- The names of `J` that the formulas `fs` mention, in `J`'s order: the one scan of open names in formulas. -/
def opensIn (J : List String) (fs : List VE.Formula) : List String :=
  J.filter fun j => fs.any fun φ => (VE.Norms.preds φ).contains j

theorem opensIn_iff (J fs j) : j ∈ opensIn J fs ↔ j ∈ J ∧ ∃ φ ∈ fs, j ∈ VE.Norms.preds φ := by
  simp [opensIn, List.mem_filter, List.any_eq_true]

/-- The scan finds a name exactly when some formula mentions one of `J`. -/
theorem opensIn_isEmpty (J : List String) (fs : List VE.Formula) :
    (!(opensIn J fs).isEmpty) = fs.any (fun f => (VE.Norms.preds f).any J.contains) := by
  apply Bool.eq_iff_iff.mpr
  simp only [Bool.not_eq_true', List.isEmpty_eq_false_iff_exists_mem, opensIn_iff, List.any_eq_true,
    List.contains_iff_mem]
  constructor
  · rintro ⟨j, hj, φ, hφ, hp⟩; exact ⟨φ, hφ, j, hp, hj⟩
  · rintro ⟨φ, hφ, j, hp, hj⟩; exact ⟨j, hj, φ, hφ, hp⟩

end VE.Judgments
