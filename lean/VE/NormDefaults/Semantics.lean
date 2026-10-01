import VE.NormDefaults.FillCheck

/-! The direct semantics with the `unspecified` completion (docs/spec/norm-defaults.md
2.2 and 7): W1's `IntendedAt` with its third clause dropped for unspecified
predicates, and `fill_intended`, the faithfulness of W1's layer on `T‴` to it.

`Value3` is W1's `Value` with a fourth outcome, `unsaid`, where no rule decides an
unspecified predicate. `IntendedAt3` asks nothing there. `Expansion3` is an
expansion in source terms: no unsaid predicates. `fill_intended` is W1's
`catalaValue` case split with `fill_decides`: on `T‴` the elaboration of `p` is
`IntendedAt3` plus "`p` agrees with its filling `unsaid__p` at the gaps". -/
namespace VE.NormDefaults
open VE.Norms VE.Route
universe u

inductive Outcome3 | yes | no | unsaid | conflict
  deriving DecidableEq, Repr

noncomputable def value3 (P N : Prop) (c : Completion) : Outcome3 := by
  classical
  exact if P ∧ N then .conflict else if P then .yes else if N then .no else
    match c with | .allow => .yes | .deny => .no | .unspecified => .unsaid

noncomputable def Value3 (U : UDoc) (r : Regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) : Outcome3 :=
  value3 (DecidesD U.D.T S (tupleVal vs) r.name true) (DecidesD U.D.T S (tupleVal vs) r.name false)
    (completionOf U r)

def IntendedAt3 (U : UDoc) (r : Regulated) (S : VE.Structure.{u}) : Prop :=
  ∀ vs, VE.TupleTyped S r.sorts vs →
    match Value3 U r (forget [r.name] S) vs with
    | .yes => S.relation r.name vs | .no => ¬ S.relation r.name vs | .unsaid => True | .conflict => False

/-- Expansions in source terms (2.2): no unsaid predicates. -/
def Expansion3 (U : UDoc) (B S : VE.Structure.{u}) : Prop :=
  restrictAll U.D.T S = B ∧ S.Admissible (envAt U.D (size U.D)) ∧ Sat S (background U.D) ∧
    ∀ r ∈ U.D.T.regulated, IntendedAt3 U r S

/-! ## The case splits -/

theorem value3_holds (P N R : Prop) (c : Completion) :
    (match value3 P N c with
      | .yes => R | .no => ¬ R | .unsaid => True | .conflict => False) ↔
    ((P → R) ∧ (N → ¬ R) ∧ (¬ P ∧ ¬ N → (c = .allow → R) ∧ (c = .deny → ¬ R))) := by
  classical
  unfold value3
  by_cases hP : P <;> by_cases hN : N <;> cases c <;> simp [hP, hN]

/-- A completed predicate: W1's value and the three-valued one say the same. -/
theorem catala_completed (P N R : Prop) (d : Bool) :
    (∃ b, catalaValue P N d = some b ∧ (R ↔ b = true)) ↔
      (match value3 P N (if d then .allow else .deny) with
        | .yes => R | .no => ¬ R | .unsaid => True | .conflict => False) := by
  rw [catalaValue_spec, value3_holds]
  cases d <;> simp

/-- An unspecified predicate on `T‴`: W1's value with the synthetic rule is the
three-valued one plus agreement with the filling at the gaps. -/
theorem catala_unspecified (P N R V : Prop) :
    (∃ b, catalaValue (P ∨ (V ∧ ¬ P ∧ ¬ N)) N false = some b ∧ (R ↔ b = true)) ↔
      (match value3 P N .unspecified with
        | .yes => R | .no => ¬ R | .unsaid => True | .conflict => False) ∧
      (value3 P N .unspecified = .unsaid → (R ↔ V)) := by
  classical
  rw [catalaValue_spec, value3_holds]
  unfold value3
  by_cases hP : P <;> by_cases hN : N <;> by_cases hV : V <;> simp [hP, hN, hV]

/-! ## Faithfulness -/

theorem completionOf_unspec {U : UDoc} {r : Regulated} (h : r.name ∈ U.unspec) :
    completionOf U r = .unspecified := by simp [completionOf, h]

theorem completionOf_other {U : UDoc} {r : Regulated} (h : r.name ∉ U.unspec) :
    completionOf U r = if r.allowByDefault then .allow else .deny := by
  simp only [completionOf, h, if_false]

theorem unsaidName_ne_regulated {U : UDoc} (hu : UValid U) {r : Regulated} (hr : r ∈ U.D.T.regulated)
    (p : String) (hp : p ∈ U.unspec) : unsaidName p ≠ r.name := by
  intro e
  have := hu.declared_pred hr
  rw [← e, hu.freshPred p hp] at this
  cases this

/-- `fill_intended`: faithfulness of the W1 layer on `T‴` to the direct semantics
of 2.2 plus agreement with the filling. -/
theorem fill_intended (U : UDoc) (h : WellFormedU U = true) (r : Regulated) (hr : r ∈ U.D.T.regulated)
    (S : VE.Structure.{u}) :
    IntendedAt (fill U).T r S ↔
      IntendedAt3 U r S ∧
      (r.name ∈ U.unspec → ∀ vs, VE.TupleTyped S r.sorts vs →
        Value3 U r (forget [r.name] S) vs = .unsaid →
          (S.relation r.name vs ↔ S.relation (unsaidName r.name) vs)) := by
  have hu := uvalid h
  unfold IntendedAt IntendedAt3
  by_cases hp : r.name ∈ U.unspec
  · simp only [hp, forall_const]
    rw [← forall_and]
    apply forall_congr'
    intro vs
    rw [← imp_and]
    apply imp_congr_right
    intro hvs
    obtain ⟨r', hr', hrn, hra⟩ := hu.declared _ hp
    have hrr : r' = r := hu.regulated_eq hr' hr hrn
    subst hrr
    have hfd := fill_decides U h r'.name hp (forget [r'.name] S) (tupleVal vs)
    have hatom : (atom (unsaidName r'.name) (sortsOf U.D r'.name)).denote (forget [r'.name] S) (tupleVal vs) ↔
        S.relation (unsaidName r'.name) vs := by
      rw [sortsOf_reg hu hr', atom_denote (forget [r'.name] S) _ _ (hu.ok.2.2.1 r' hr').2.1 vs
        ((tupleTyped_forget _ S _ vs).mpr hvs)]
      exact forget_relation S (by simpa using unsaidName_ne_regulated hu hr' r'.name hp) vs
    simp only [Value, hra, Value3, completionOf_unspec hp]
    rw [hfd.1, hfd.2, hatom]
    exact catala_unspecified _ _ _ _
  · simp only [hp, false_implies, and_true]
    apply forall_congr'
    intro vs
    apply imp_congr_right
    intro _
    have hno : ∀ sign, DecidesD (fill U).T (forget [r.name] S) (tupleVal vs) r.name sign ↔
        DecidesD U.D.T (forget [r.name] S) (tupleVal vs) r.name sign := by
      intro sign
      rw [decidesD_fill hu]
      constructor
      · rintro (h' | ⟨_, _, _, _, hp', _⟩)
        · exact h'
        · exact absurd hp' hp
      · exact Or.inl
    simp only [Value, Value3, completionOf_other hp, hno]
    exact catala_completed _ _ _ _

end VE.NormDefaults
