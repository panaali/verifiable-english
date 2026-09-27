import VE.Norms.Conflict

/-! The decidable fragment (docs/spec/norms.md section 7), in its proof-gated
form. `InFragment` is decided syntactically: every conflict formula is
quantifier-free (closure and `$int` terms do not exist in the FOL formula type,
and before W5 no `functional`/`total` flag and no adapter predicate exists, so
the base admissibility theory is literal distinctness, which is ground).

`conflict_smallModel`: a conflict witness in the fragment restricts to a finite
substructure on the witness tuple plus the constants, with per-sort size at
most `max 1 (constants of the sort + witness variables of the sort)`; empty
sorts stay empty. The environment's constants are supplied as a finite list
`cs` covering every declared constant (the decoded vocabulary's constant list).

This file proves the restriction theorem only. The completeness consequence
(`conflict_complete`, "no small witness implies CONFLICT-FREE") is not stated
here: CONFLICT-FREE still requires a tableau certificate (binding decision 9.4)
until an enumerator is proved against this bound. -/
namespace VE.Norms
open VE.Route (Unique)
universe u

def Formula.qfree : VE.Formula → Bool
  | .all _ _ | .ex _ _ => false
  | .not a => Formula.qfree a
  | .and a b | .or a b | .implies a b => Formula.qfree a && Formula.qfree b
  | _ => true

/-- `InFragment E T` (7.1), syntactically. -/
def InFragment (D : Doc) : Bool :=
  D.T.regulated.all (fun r => Formula.qfree (conflict D r)) &&
    (pairs D.T).all (fun pr => Formula.qfree (pairConflict D pr))

def constantsOfSort (D : Doc) (cs : List String) (s : String) : Nat :=
  (cs.filter (fun c => D.E.constants c == some s)).length

def witnessVarsOfSort (sorts : List String) (s : String) : Nat := sorts.count s

section Restrict
open Classical

variable (D : Doc) (cs : List String) (S : VE.Structure.{u}) (sorts : List String) (vs : List S.Carrier)

/-- The elements of sort `s` denoted by constants, then the witness components of sort `s`. -/
noncomputable def subDomain (s : String) : List S.Carrier :=
  cs.filterMap (fun c => if D.E.constants c = some s then S.constant c else none) ++
    (sorts.zip vs).filterMap (fun p => if p.1 = s then some p.2 else none)

noncomputable def subRelation (p : String) : List (List S.Carrier) :=
  match (envAt D 0).predicates p with
  | some [s] => ((subDomain D cs S sorts vs s).map (fun v => [v])).filter (fun w => decide (S.relation p w))
  | some [s, t] => ((subDomain D cs S sorts vs s).flatMap
      (fun v => (subDomain D cs S sorts vs t).map (fun w => [v, w]))).filter (fun w => decide (S.relation p w))
  | _ => []

/-- The finite substructure on the constants and the witness tuple. -/
noncomputable def subModel : VE.FiniteModel S.Carrier where
  domains := subDomain D cs S sorts vs
  constants := S.constant
  relations := subRelation D cs S sorts vs

end Restrict

theorem length_filterMap_le {α β : Type _} (f : α → Option β) (l : List α) :
    (l.filterMap f).length ≤ l.length := by
  induction l with
  | nil => simp
  | cons a l ih =>
    simp only [List.filterMap_cons]
    cases f a <;> simp <;> omega

theorem subDomain_length (D : Doc) (cs : List String) (S : VE.Structure.{u}) (sorts : List String)
    (vs : List S.Carrier) (s : String) :
    (subDomain D cs S sorts vs s).length ≤ constantsOfSort D cs s + witnessVarsOfSort sorts s := by
  classical
  unfold subDomain constantsOfSort witnessVarsOfSort
  rw [List.length_append]
  apply Nat.add_le_add
  · induction cs with
    | nil => simp
    | cons c cs ih =>
      simp only [List.filterMap_cons, List.filter_cons]
      by_cases hc : D.E.constants c = some s
      · simp only [hc, if_true, beq_self_eq_true]
        cases S.constant c <;> simp <;> omega
      · have : (D.E.constants c == some s) = false := by simpa using hc
        simp only [hc, if_false, this]
        exact ih
  · induction sorts generalizing vs with
    | nil => simp
    | cons t ts ih =>
      cases vs with
      | nil => simp
      | cons v vs =>
        simp only [List.zip_cons_cons, List.filterMap_cons, List.count_cons]
        by_cases ht : t = s
        · subst ht; simp only [if_true, List.length_cons, beq_self_eq_true]; have := ih vs; simp; omega
        · have : (t == s) = false := by simpa using ht
          simp only [ht, if_false, this]
          have := ih vs; simpa using this

theorem mem_subDomain_const {D : Doc} {cs : List String} {S : VE.Structure.{u}} {sorts : List String}
    {vs : List S.Carrier} {c s : String} {v : S.Carrier} (hc : c ∈ cs) (hcs : D.E.constants c = some s)
    (hv : S.constant c = some v) : v ∈ subDomain D cs S sorts vs s := by
  classical
  unfold subDomain
  apply List.mem_append_left
  exact List.mem_filterMap.mpr ⟨c, hc, by simp [hcs, hv]⟩

theorem tupleTyped_of_mem_zip (S' : VE.Structure.{u}) :
    ∀ (ss : List String) (ws : List S'.Carrier), ws.length = ss.length →
      (∀ s w, (s, w) ∈ ss.zip ws → S'.domain s w) → VE.TupleTyped S' ss ws
  | [], [], _, _ => trivial
  | s :: ss, w :: ws, hl, hd =>
    ⟨hd s w (by simp), tupleTyped_of_mem_zip S' ss ws (by simpa using hl)
      (fun s' w' h => hd s' w' (by simp [h]))⟩
  | [], _ :: _, hl, _ => by simp at hl
  | _ :: _, [], hl, _ => by simp at hl

theorem subModel_witness (D : Doc) (cs : List String) (S : VE.Structure.{u}) (sorts : List String)
    (vs : List S.Carrier) (h : VE.TupleTyped S sorts vs) :
    VE.TupleTyped (subModel D cs S sorts vs).asStructure sorts vs := by
  classical
  refine tupleTyped_of_mem_zip (subModel D cs S sorts vs).asStructure sorts vs (tupleTyped_length h) ?_
  intro s w hm
  show w ∈ subDomain D cs S sorts vs s
  unfold subDomain
  apply List.mem_append_right
  exact List.mem_filterMap.mpr ⟨(s, w), hm, by simp⟩

theorem term_denote_subModel (D : Doc) (cs : List String) (S : VE.Structure.{u}) (sorts : List String)
    (vs : List S.Carrier) (ρ : List S.Carrier) (t : VE.Term) :
    t.denote (subModel D cs S sorts vs).asStructure ρ = t.denote S ρ := by
  cases t <;> rfl

section QF
variable (D : Doc) (cs : List String) (hcs : ∀ c s, D.E.constants c = some s → c ∈ cs)
  (S : VE.Structure.{u}) (hS : S.Admissible (envAt D 0)) (sorts : List String) (vs : List S.Carrier)
include hcs hS

theorem subModel_constants :
    ∀ c s, (envAt D 0).constants c = some s →
      ∃ v, (subModel D cs S sorts vs).asStructure.constant c = some v ∧
        (subModel D cs S sorts vs).asStructure.domain s v := by
  intro c s hc
  obtain ⟨v, hv, _⟩ := hS.1 c s hc
  exact ⟨v, hv, mem_subDomain_const (hcs c s hc) hc hv⟩

theorem subModel_valid : (subModel D cs S sorts vs).Valid (envAt D 0) := by
  classical
  refine ⟨subModel_constants D cs hcs S hS sorts vs, fun p ws hp => ?_⟩
  change ws ∈ subRelation D cs S sorts vs p at hp
  unfold subRelation at hp
  split at hp
  · rename_i s hps
    obtain ⟨hm, _⟩ := List.mem_filter.mp hp
    obtain ⟨v, hv, rfl⟩ := List.mem_map.mp hm
    exact ⟨[s], hps, hv, trivial⟩
  · rename_i s t hps
    obtain ⟨hm, _⟩ := List.mem_filter.mp hp
    obtain ⟨v, hv, hm⟩ := List.mem_flatMap.mp hm
    obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hm
    exact ⟨[s, t], hps, hv, hw, trivial⟩
  · cases hp

theorem subModel_denote : ∀ (φ : VE.Formula), Formula.qfree φ = true →
    ∀ (Γ : List String), φ.WellFormed (envAt D 0) Γ → ∀ (ρ : List S.Carrier),
      VE.Valuation.Typed (subModel D cs S sorts vs).asStructure Γ ρ →
      (φ.denote (subModel D cs S sorts vs).asStructure ρ ↔ φ.denote S ρ) := by
  classical
  intro φ
  induction φ with
  | top | bottom => intros; exact Iff.rfl
  | unary p t =>
    intro _ Γ ⟨s, hp, ht⟩ ρ hρ
    obtain ⟨v, hv, hd⟩ := term_defined_consts (subModel_constants D cs hcs S hS sorts vs) hρ ht
    rw [term_denote_subModel] at hv
    simp only [VE.Formula.denote]
    rw [term_denote_subModel, hv]
    change (∃ v', some v = some v' ∧ [v'] ∈ subRelation D cs S sorts vs p) ↔ _
    unfold subRelation
    rw [hp]
    constructor
    · rintro ⟨v', hv', hm⟩
      cases hv'
      exact ⟨v, rfl, of_decide_eq_true (List.mem_filter.mp hm).2⟩
    · rintro ⟨v', hv', hr⟩
      cases hv'
      exact ⟨v, rfl, List.mem_filter.mpr ⟨List.mem_map.mpr ⟨v, hd, rfl⟩, decide_eq_true hr⟩⟩
  | binary p t u =>
    intro _ Γ ⟨s, s', hp, ht, hu⟩ ρ hρ
    obtain ⟨v, hv, hd⟩ := term_defined_consts (subModel_constants D cs hcs S hS sorts vs) hρ ht
    obtain ⟨w, hw, hd'⟩ := term_defined_consts (subModel_constants D cs hcs S hS sorts vs) hρ hu
    rw [term_denote_subModel] at hv hw
    simp only [VE.Formula.denote]
    rw [term_denote_subModel, term_denote_subModel, hv, hw]
    change (∃ a b, some v = some a ∧ some w = some b ∧ [a, b] ∈ subRelation D cs S sorts vs p) ↔ _
    unfold subRelation
    rw [hp]
    constructor
    · rintro ⟨a, b, ha, hb, hm⟩
      cases ha; cases hb
      exact ⟨v, w, rfl, rfl, of_decide_eq_true (List.mem_filter.mp hm).2⟩
    · rintro ⟨a, b, ha, hb, hr⟩
      cases ha; cases hb
      exact ⟨v, w, rfl, rfl, List.mem_filter.mpr ⟨List.mem_flatMap.mpr ⟨v, hd,
        List.mem_map.mpr ⟨w, hd', rfl⟩⟩, decide_eq_true hr⟩⟩
  | eq t u => intros; exact Iff.rfl
  | not a ih =>
    intro hq Γ hw ρ hρ
    simp only [VE.Formula.denote]; rw [ih hq Γ hw ρ hρ]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro hq Γ hw ρ hρ
    simp only [Formula.qfree, Bool.and_eq_true] at hq
    simp only [VE.Formula.denote]; rw [ia hq.1 Γ hw.1 ρ hρ, ib hq.2 Γ hw.2 ρ hρ]
  | all s a _ | ex s a _ => intro hq; cases hq

end QF

/-- A quantifier-free base formula true at a typed tuple of a base-admissible
structure is true at the same tuple of the finite substructure on the constants
and the tuple. -/
theorem restrict_witness (D : Doc) (cs : List String) (hcs : ∀ c s, D.E.constants c = some s → c ∈ cs)
    (S : VE.Structure.{u}) (hS : BaseAdmissible D S) (sorts : List String) (vs : List S.Carrier)
    (typed : VE.TupleTyped S sorts vs) (φ : VE.Formula) (hq : Formula.qfree φ = true)
    (hw : φ.WellFormed (envAt D 0) sorts.reverse) (hden : φ.denote S (tupleVal vs)) :
    ∃ (α : Type u) (inst : DecidableEq α) (M : VE.FiniteModel α) (ws : List α),
      M.Valid (envAt D 0) ∧ @backgroundValid α inst D M = true ∧
      VE.TupleTyped M.asStructure sorts ws ∧
      (∀ s, (M.domains s).length ≤ max 1 (constantsOfSort D cs s + witnessVarsOfSort sorts s)) ∧
      @VE.Formula.eval α inst M (tupleVal ws) φ = true := by
  classical
  refine ⟨S.Carrier, inferInstance, subModel D cs S sorts vs, vs,
    subModel_valid D cs hcs S hS.1 sorts vs, ?_, subModel_witness D cs S sorts vs typed,
    fun s => Nat.le_trans (subDomain_length D cs S sorts vs s) (Nat.le_max_right _ _), ?_⟩
  · apply List.all_eq_true.mpr
    intro a ha
    apply (VE.eval_iff_denote _ [] a).mpr
    obtain ⟨pr, _, rfl⟩ := List.mem_map.mp ha
    rw [VE.Route.Background.literalPremise_denote]
    exact (VE.Route.Background.literalPremise_denote S pr).mp (hS.2 _ ha)
  · apply (VE.eval_iff_denote _ _ φ).mpr
    exact (subModel_denote D cs hcs S hS.1 sorts vs φ hq _ hw _
      (tupleVal_typed (subModel D cs S sorts vs).asStructure sorts vs
        (subModel_witness D cs S sorts vs typed))).mpr hden

/-- `conflict_smallModel` (7.2): in the fragment, a conflict witness restricts to
a finite valid base model on the witness tuple plus the constants. -/
theorem conflict_smallModel (D : Doc) (h : WellFormed D = true) (hf : InFragment D = true)
    (cs : List String) (hcs : ∀ c s, D.E.constants c = some s → c ∈ cs)
    (r : Regulated) (hr : r ∈ D.T.regulated) (S : VE.Structure.{u}) (hS : BaseAdmissible D S)
    (vs : List S.Carrier) (typed : VE.TupleTyped S r.sorts vs)
    (hw : (conflict D r).denote S (tupleVal vs)) :
    ∃ (α : Type u) (inst : DecidableEq α) (M : VE.FiniteModel α) (ws : List α),
      M.Valid (envAt D 0) ∧ @backgroundValid α inst D M = true ∧
      VE.TupleTyped M.asStructure r.sorts ws ∧
      (∀ s, (M.domains s).length ≤ max 1 (constantsOfSort D cs s + witnessVarsOfSort r.sorts s)) ∧
      @VE.Formula.eval α inst M (tupleVal ws) (conflict D r) = true := by
  have hv := valid_of_wellFormed D h
  obtain ⟨k, hk⟩ := mem_syms_index (hv.regulated r hr)
  simp only [InFragment, Bool.and_eq_true, List.all_eq_true] at hf
  exact restrict_witness D cs hcs S hS r.sorts vs typed _ (hf.1 r hr) (conflict_wellFormed hv hk) hw

/-- The same restriction for a declared pair's conflict formula. -/
theorem conflict_pair_smallModel (D : Doc) (h : WellFormed D = true) (hf : InFragment D = true)
    (cs : List String) (hcs : ∀ c s, D.E.constants c = some s → c ∈ cs)
    (pr : Pair) (hpr : pr ∈ pairs D.T) (S : VE.Structure.{u}) (hS : BaseAdmissible D S)
    (vs : List S.Carrier) (typed : VE.TupleTyped S pr.sorts vs)
    (hw : (pairConflict D pr).denote S (tupleVal vs)) :
    ∃ (α : Type u) (inst : DecidableEq α) (M : VE.FiniteModel α) (ws : List α),
      M.Valid (envAt D 0) ∧ @backgroundValid α inst D M = true ∧
      VE.TupleTyped M.asStructure pr.sorts ws ∧
      (∀ s, (M.domains s).length ≤ max 1 (constantsOfSort D cs s + witnessVarsOfSort pr.sorts s)) ∧
      @VE.Formula.eval α inst M (tupleVal ws) (pairConflict D pr) = true := by
  have hv := valid_of_wellFormed D h
  simp only [InFragment, Bool.and_eq_true, List.all_eq_true] at hf
  exact restrict_witness D cs hcs S hS pr.sorts vs typed _ (hf.2 pr hpr)
    (pairConflict_wellFormed hv hpr) hw

end VE.Norms
