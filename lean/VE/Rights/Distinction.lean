import VE.Rights.Scope

/-! `noDistinction` and the restricted invariance claim (docs/spec/rights.md 4.6, 9.2).

For a right-derived predicate `p` the audit reports `independent` when `cone(p)` (soft-norms
7.4's cone on `T″′`) contains no protected predicate; the invariance theorem is exactly
`cone_independent` with `Q := protected`, on those predicates only. Otherwise the lines
on or below `p` whose guard or carve-outs mention a protected predicate are listed, each
cited (`cites["guard"]`) or uncited (the finding `ProtectedInCone`). Nothing is claimed
about the deciders of open terms. -/
namespace VE.Rights
open VE.SoftNorms (cone)
universe u

/-- The right-derived predicates, first occurrence kept. -/
def rightDerivedPreds (D : RightsDoc) : List String := VE.SoftNorms.dedup ((linesOf D).map (·.2.node.pred))

/-- `independent` is reported for `p`: its cone is protected-free. -/
def independentReported (D : RightsDoc) (p : String) : Bool :=
  (cone (correlate D) p).all (fun q => !D.rights.protected.contains q)

/-- The line instances on `p` or on a predicate of its cone whose guard or carve-outs in `T″`
mention a protected predicate: line, protected predicate, cited. -/
def distinctionHits (D : RightsDoc) (p : String) : List (Line × String × Bool) :=
  (linesOf D).flatMap (fun RN =>
    let N := RN.2
    if N.node.pred == p || (cone (correlate D) p).contains N.node.pred then
      (VE.SoftNorms.dedup (((nodeOf D N).guard :: (nodeOf D N).carveOuts).flatMap VE.Norms.preds)).filterMap
        (fun q => if D.rights.protected.contains q then some (N, q, hasKey N.source.cites "guard") else none)
    else [])

/-- The audit: every uncited hit on a predicate not reported `independent`. -/
def noDistinction (D : RightsDoc) : List Finding :=
  (rightDerivedPreds D).flatMap (fun p =>
    if independentReported D p then []
    else (distinctionHits D p).filterMap (fun hit =>
      if hit.2.2 then none
      else some ⟨"ProtectedInCone", hit.1.node.name, hit.1.right, "",
        s!"ProtectedInCone: {hit.2.1} in rule {hit.1.node.name} on right {hit.1.right}"⟩))

/-- Well-formedness puts every right-derived predicate among `T″`'s regulated names. -/
theorem rightDerived_regulated (D : RightsDoc) (h : WellFormedRights D = true) (p : String)
    (hp : rightDerived D p = true) : p ∈ VE.Norms.regulatedNames (correlate D).base.T := by
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ (correlate_wellFormed D h)
  obtain ⟨RN, hRN, he⟩ := List.any_eq_true.mp hp
  have hpe : RN.2.node.pred = p := by simpa using he
  have := hsv.predReg (nodeOf D RN.2) (lineNode_correlate D (R := RN.1) hRN)
  rw [← hpe]
  exact this

/-- 4.6: exactly `cone_independent` with `Q := protected`, on a protected-free cone. -/
theorem no_distinction_sound (D : RightsDoc) (h : WellFormedRights D = true) (p : String)
    (hp : rightDerived D p = true)
    (hcone : ∀ q ∈ cone (correlate D) p, q ∉ D.rights.protected)
    (B : VE.Structure.{u}) (R : String → List B.Carrier → Prop)
    (hR : ∀ q vs, q ∉ D.rights.protected → (R q vs ↔ B.relation q vs)) (vs : List B.Carrier) :
    (VE.Norms.outcomeBase (VE.SoftNorms.soften (correlate D)) p).denote { B with relation := R } (VE.Norms.tupleVal vs) ↔
      (VE.Norms.outcomeBase (VE.SoftNorms.soften (correlate D)) p).denote B (VE.Norms.tupleVal vs) :=
  VE.SoftNorms.cone_independent (correlate D) (correlate_wellFormed D h) p (rightDerived_regulated D h p hp)
    D.rights.protected hcone B R hR vs

/-- The audit agrees with the hypothesis: `independent` is reported for `p` iff the cone is protected-free. -/
theorem noDistinction_sound (D : RightsDoc) (_h : WellFormedRights D = true) (p : String)
    (_hp : rightDerived D p = true) (hi : independentReported D p = true) :
    ∀ q ∈ cone (correlate D) p, q ∉ D.rights.protected := by
  intro q hq hmem
  have := List.all_eq_true.mp hi q hq
  simp [hmem] at this

theorem independentReported_iff (D : RightsDoc) (p : String) :
    independentReported D p = true ↔ ∀ q ∈ cone (correlate D) p, q ∉ D.rights.protected := by
  simp [independentReported, List.all_eq_true]

end VE.Rights
