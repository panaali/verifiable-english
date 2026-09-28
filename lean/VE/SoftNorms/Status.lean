import VE.SoftNorms.RankProof

/-! The classification of colliding pairs (docs/spec/soft-norms.md 6.2) and its
soundness.

For `{M, N} ∈ CP(T)`: RANK-RESOLVED when the ranks are comparable (theorem
`rank_resolves`; no search, the coherence conjunct is valid, `coh_rank_valid`);
DISJOINT with an accepted certificate for the conjunct over
`Background_base(E′) ++ Exc_T` (`disjoint_sound`); WEIGHING POINT with a checked
finite witness over `E′_base` satisfying that same coherence-free background
(`weighing_point_sound`); UNKNOWN otherwise. No coherence conjunct is ever part
of a classification background, so none can discharge another (fixture τ). -/
namespace VE.SoftNorms
open VE.Norms
universe u

inductive PairStatus | rankResolved | disjoint | weighingPoint | unknown
  deriving DecidableEq, Repr

def PairStatus.text : PairStatus → String
  | .rankResolved => "RANK-RESOLVED"
  | .disjoint => "DISJOINT"
  | .weighingPoint => "WEIGHING POINT"
  | .unknown => "UNKNOWN"

/-- `Background_base(E′) ++ Exc_T`: the classification background, with every coherence
conjunct excluded. -/
def classificationBackground (D : SoftDoc) : List VE.Formula := VE.Norms.backgroundBase (soften D) ++ excPremises D

/-- Its base form: the RANK-RESOLVED conjunct of `Coh_T` holds in every structure. -/
theorem coh_rank_valid (D : SoftDoc) (h : WellFormedSoft D = true) (M N : SoftNode)
    (hc : (M, N) ∈ collidingPairs D) (hcmp : Comparable D M N = true) (B : VE.Structure.{u}) :
    (cohPremise D M N).denote B [] :=
  coh_rank_valid_unconditional D h M N hc hcmp B

/-- 6.2: a DISJOINT certificate proves the conjunct in every base-admissible structure
satisfying `Exc_T`. -/
theorem disjoint_sound (D : SoftDoc) (_h : WellFormedSoft D = true) (M N : SoftNode)
    (_hc : (M, N) ∈ collidingPairs D) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (envAt (soften D) 0) (VE.Norms.backgroundBase (soften D) ++ excPremises D)
      (cohPremise D M N) c = true) :
    ∀ B : VE.Structure.{u}, VE.Norms.BaseAdmissible (soften D) B → Sat B (excPremises D) →
      (cohPremise D M N).denote B [] := by
  intro B hB he
  apply VE.Tableau.checkCertificate_sound.{u} _ _ _ c acc B hB.1
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact hB.2 a ha
  · exact he a ha

/-- 6.2: a WEIGHING POINT witness refutes the conjunct, and with it the unconditional
conflict-freedom claim. -/
theorem weighing_point_sound {α : Type u} [DecidableEq α] (D : SoftDoc) (h : WellFormedSoft D = true)
    (M N : SoftNode) (hc : (M, N) ∈ collidingPairs D) (Mo : VE.FiniteModel α)
    (valid : Mo.Valid (envAt (soften D) 0)) (hb : classificationBackgroundValid D Mo = true)
    (vs : List α) (typed : VE.TupleTyped Mo.asStructure (actSorts D M) vs)
    (hw : (VE.Formula.and (circ D (selects' D M)) (circ D (selects' D N))).eval Mo (tupleVal vs) = true) :
    ¬ (cohPremise D M N).denote Mo.asStructure [] ∧
      ¬ (∀ B : VE.Structure.{u}, VE.Norms.BaseAdmissible (soften D) B → VE.Norms.ConflictFree (soften D) B) := by
  have hn : ¬ (cohPremise D M N).denote Mo.asStructure [] := by
    rw [cohPremise, bindAll_denote_nil]
    intro hall
    exact hall vs typed ((VE.eval_iff_denote Mo _ _).mp hw)
  refine ⟨hn, fun hall => hn ?_⟩
  simp only [classificationBackgroundValid, Bool.and_eq_true] at hb
  have hB := baseAdmissible_of_valid _ Mo valid hb.1
  have := (soft_conflict_decomposition D h _ hB).mp (hall _ hB)
  exact this.2.2 _ (List.mem_map.mpr ⟨(M, N), hc, rfl⟩)

end VE.SoftNorms
