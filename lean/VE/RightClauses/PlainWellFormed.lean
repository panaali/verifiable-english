import VE.RightClauses.PlainWellFormed.RightsSem

/-! `plain_wellFormed` (docs/spec/right-clauses.md 8.3; rule 2, source in, same kind out): when the structured lines
check and the rights document is well formed, `plain D` is well formed or its check reports a resource limit.

The plain guard adds base conjuncts typed in the line's context and changes no name, predicate, edge or precedence
(`PWF.correlate_mapG`, `PWF.ghyp`): `checkRights` reads the same document (`PWF.checkRights_plain`), every soft and
W1 check but a size limit reads the same answer (`PWF.validateSoft_mapG`), the identifier check reads the same names
(`PWF.decisionNames_mapG`) and every formula the rights facts type still types (`PWF.rightsSemanticCheck_plain`). -/
namespace VE.RightClauses
open VE.Rights (WellFormedRights validateRights)

/-- Rule 2 (source in, same kind out): the only new way the successor's check can fail is a resource limit, since
    the plain guard adds base conjuncts typed in the line's context and changes no name, predicate, edge or
    precedence. -/
theorem plain_wellFormed (D : ClauseDoc) (h : WellFormedClauses D = true) (h0 : WellFormedRights D.doc = true) :
  WellFormedRights (plain D) = true ∨
    ∃ e, validateRights (plain D) = .error e ∧ "ResourceLimit: ".isPrefixOf e = true := by
  have F := PWF.facts D h0
  have hsoft : PWF.OkOrRL (VE.SoftNorms.validateSoft (VE.Rights.correlate (plain D))) := by
    rw [PWF.correlate_mapG F]; exact PWF.validateSoft_mapG (PWF.ghyp F h) F.soft
  have hdec : VE.SoftNorms.decisionNames (VE.Rights.correlate (plain D)) =
      VE.SoftNorms.decisionNames (VE.Rights.correlate D.doc) := by
    rw [PWF.correlate_mapG F, PWF.decisionNames_mapG]
  have hv : validateRights (plain D) = .ok () ∨ ∃ e, validateRights (plain D) = .error e ∧ PWF.RL e := by
    unfold validateRights
    rw [PWF.checkRights_plain, F.rights]
    rcases hsoft with hs | ⟨e, he, hre⟩
    · left
      simp only [hs, hdec, F.ident, PWF.rightsSemanticCheck_plain F h, if_true]
    · right; exact ⟨e, by simp only [he], hre⟩
  rcases hv with hv | ⟨e, he, hre⟩
  · left; unfold WellFormedRights; rw [hv]
  · right; exact ⟨e, he, hre.isPrefixOf⟩

end VE.RightClauses
