import VE.Judgments.Status
import VE.SoftNorms.Tree
import VE.NormDefaults.Packs

/-! Judgment terms beside the soft chain (docs/spec/profile-composition.md 3.1, PC-1; owner judgment-terms). A soft
rule's unit reads its author rule: the guard and the author carve-outs, never what the soft route generates from it
(`primeNode`'s derived carve-out reads opponents' guards, so it is no reader of the unit's own text). The rights
chain's reader (`rightsAuthorFormulas`, `blockFormulas`) is pc-1g's. -/

namespace VE.Judgments

/-- PC-1 (1). Formulas whose every predicate is reserved, or already read, change no scan. -/
theorem opensIn_generated (J : List String) (fs gs : List VE.Formula)
    (hJ : ∀ j ∈ J, VE.NormDefaults.Packs.reserved j = false)
    (hg : ∀ g ∈ gs, ∀ p ∈ VE.Norms.preds g,
      VE.NormDefaults.Packs.reserved p = true ∨ ∃ f ∈ fs, p ∈ VE.Norms.preds f) :
    opensIn J (fs ++ gs) = opensIn J fs := by
  unfold opensIn
  apply List.filter_congr
  intro j hj
  simp only [List.any_append, Bool.or_eq_left_iff_imp, List.any_eq_true, List.contains_iff_mem]
  rintro ⟨g, hg', hp⟩
  rcases hg g hg' j hp with hr | ⟨f, hf, hpf⟩
  · exact absurd hr (by simp [hJ j hj])
  · exact ⟨f, hf, hpf⟩

/-- PC-1 (2). What a soft rule's unit reads: its author rule (guard and author carve-outs). -/
def softContent (N : VE.SoftNorms.SoftNode) : Content := .rule N.toNode

theorem softContent_formulas (N : VE.SoftNorms.SoftNode) : (softContent N).formulas = N.guard :: N.carveOuts := rfl

end VE.Judgments
