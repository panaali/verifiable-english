import VE.Core.Paths

namespace VE.Core
universe u

inductive Formula where
  | top
  | bottom
  | unary (predicate : String) (term : Term)
  | binary (predicate : String) (left right : Term)
  | atom (predicate : String) (terms : List Term)
  | eq (left right : Term)
  | not (body : Formula)
  | and (left right : Formula)
  | or (left right : Formula)
  | implies (left right : Formula)
  | all (sort : String) (body : Formula)
  | ex (sort : String) (body : Formula)
  | reachNamed (kind : Kind) (relation : String) (left right : Term)
  | reachBody (kind : Kind) (sort : String) (body : Formula) (left right : Term)
  deriving DecidableEq, Repr, BEq

/-- Typing does not infer undeclared sorts or permit equality across sorts. -/
def Formula.WellFormed (E : Environment) (Γ : List String) : Formula → Prop
  | .top | .bottom => True
  | .unary p t => ∃ s, E.predicates p = some [s] ∧ t.sortOf E Γ = some s
  | .binary p t u => ∃ s r, E.predicates p = some [s, r] ∧
      t.sortOf E Γ = some s ∧ u.sortOf E Γ = some r
  | .atom p ts => 3 ≤ ts.length ∧ ts.length ≤ 6 ∧
      ∃ ss, E.predicates p = some ss ∧ ts.mapM (·.sortOf E Γ) = some ss
  | .eq t u => ∃ s, t.sortOf E Γ = some s ∧ u.sortOf E Γ = some s
  | .not a => a.WellFormed E Γ
  | .and a b | .or a b | .implies a b => a.WellFormed E Γ ∧ b.WellFormed E Γ
  | .all s a | .ex s a => s ∈ E.sorts ∧ a.WellFormed E (s :: Γ)

  | .reachNamed _ p t u => ∃ s, E.predicates p = some [s, s] ∧
      t.sortOf E Γ = some s ∧ u.sortOf E Γ = some s
  | .reachBody _ s a t u => s ∈ E.sorts ∧ a.WellFormed E (s :: s :: Γ) ∧
      t.sortOf E Γ = some s ∧ u.sortOf E Γ = some s

/-- A total executable scope, arity and sort checker. -/
def Formula.check (E : Environment) (Γ : List String) : Formula → Bool
  | .top | .bottom => true
  | .unary p t => match E.predicates p, t.sortOf E Γ with
      | some [s], some r => s == r
      | _, _ => false
  | .binary p t u => match E.predicates p, t.sortOf E Γ, u.sortOf E Γ with
      | some [s, r], some s', some r' => s == s' && r == r'
      | _, _, _ => false
  | .atom p ts => decide (3 ≤ ts.length) && decide (ts.length ≤ 6) &&
      match E.predicates p, ts.mapM (·.sortOf E Γ) with
      | some ss, some actual => ss == actual
      | _, _ => false
  | .eq t u => match t.sortOf E Γ, u.sortOf E Γ with
      | some s, some r => s == r
      | _, _ => false
  | .not a => a.check E Γ
  | .and a b | .or a b | .implies a b => a.check E Γ && b.check E Γ
  | .all s a | .ex s a => E.sorts.contains s && a.check E (s :: Γ)

  | .reachNamed _ p t u => match E.predicates p, t.sortOf E Γ, u.sortOf E Γ with
      | some [s, r], some s', some r' => s == r && s == s' && s == r'
      | _, _, _ => false
  | .reachBody _ s a t u => E.sorts.contains s && a.check E (s :: s :: Γ) &&
      decide (t.sortOf E Γ = some s) && decide (u.sortOf E Γ = some s)

/-- The two edge variants lower injectively to separate recursive constructors,
so Lean's ordinary structural recursor includes the Body induction hypothesis. -/
inductive Edge where
  | named (relation : String)
  | body (sort : String) (formula : Formula)
  deriving DecidableEq, Repr, BEq

def Formula.reach (k : Kind) (e : Edge) (t u : Term) : Formula :=
  match e with
  | .named r => .reachNamed k r t u
  | .body s a => .reachBody k s a t u

def Formula.denote (S : Structure) (ρ : Valuation S) : Formula → Prop
  | .top => True
  | .bottom => False
  | .unary p t => ∃ v, t.denote S ρ = some v ∧ S.relation p [v]
  | .binary p t u => ∃ v w, t.denote S ρ = some v ∧
      u.denote S ρ = some w ∧ S.relation p [v, w]
  | .atom p ts => ∃ vs, ts.mapM (·.denote S ρ) = some vs ∧ S.relation p vs
  | .eq t u => ∃ v, t.denote S ρ = some v ∧ u.denote S ρ = some v
  | .not a => ¬ a.denote S ρ
  | .and a b => a.denote S ρ ∧ b.denote S ρ
  | .or a b => a.denote S ρ ∨ b.denote S ρ
  | .implies a b => a.denote S ρ → b.denote S ρ
  | .all s a => ∀ v, S.domain s v → a.denote S (v :: ρ)
  | .ex s a => ∃ v, S.domain s v ∧ a.denote S (v :: ρ)

  | .reachNamed k p t u => ∃ v w, t.denote S ρ = some v ∧
      u.denote S ρ = some w ∧ Reachable k (fun a b => S.relation p [a, b]) v w
  | .reachBody k s a t u => ∃ v w, t.denote S ρ = some v ∧
      u.denote S ρ = some w ∧ Reachable k
        (fun x y => S.domain s x ∧ S.domain s y ∧ a.denote S (y :: x :: ρ)) v w

/-- The executable checker recognizes exactly the independent typing predicate. -/
theorem check_iff_wellFormed (E : Environment) (Γ : List String) (a : Formula) :
    a.check E Γ = true ↔ a.WellFormed E Γ := by
  induction a generalizing Γ with
  | top | bottom => simp [Formula.check, Formula.WellFormed]
  | unary p t =>
    simp only [Formula.check, Formula.WellFormed]
    cases hp : E.predicates p with
    | none => simp
    | some ss =>
      cases ss with
      | nil => simp
      | cons s ss =>
        cases ss with
        | nil => cases ht : t.sortOf E Γ <;> simp_all <;> exact eq_comm
        | cons r ss => simp
  | binary p t u =>
    simp only [Formula.check, Formula.WellFormed]
    cases hp : E.predicates p with
    | none => simp
    | some ss =>
      cases ss with
      | nil => simp
      | cons s ss =>
        cases ss with
        | nil => simp
        | cons r ss =>
          cases ss with
          | nil => cases ht : t.sortOf E Γ <;> cases hu : u.sortOf E Γ <;>
              simp_all
          | cons q ss => simp
  | atom p ts =>
    simp only [Formula.check, Formula.WellFormed, Bool.and_eq_true, decide_eq_true_eq]
    cases hp : E.predicates p <;> cases ht : ts.mapM (·.sortOf E Γ) <;>
      simp_all [and_assoc] <;> intro _ _ <;> exact eq_comm
  | eq t u =>
    simp only [Formula.check, Formula.WellFormed]
    cases ht : t.sortOf E Γ <;> cases hu : u.sortOf E Γ <;> simp <;> exact eq_comm
  | not a ih => exact ih Γ
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    simp [Formula.check, Formula.WellFormed, ia, ib]
  | all s a ih | ex s a ih =>
    simp [Formula.check, Formula.WellFormed, ih]

  | reachNamed k p t u =>
    simp only [Formula.check, Formula.WellFormed]
    cases hp : E.predicates p with
    | none => simp
    | some ss =>
      cases ss with
      | nil => simp
      | cons s ss =>
        cases ss with
        | nil => simp
        | cons r ss =>
          cases ss with
          | nil => cases ht : t.sortOf E Γ <;> cases hu : u.sortOf E Γ <;>
              simp_all <;> grind
          | cons q ss => simp
  | reachBody k s a t u ih =>
    simp [Formula.check, Formula.WellFormed, ih, and_assoc]

/-- The v0 embedding changes no constructor, term, index, or sort. -/
def embed : VE.Formula → Formula
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p t
  | .binary p t u => .binary p t u
  | .eq t u => .eq t u
  | .not a => .not (embed a)
  | .and a b => .and (embed a) (embed b)
  | .or a b => .or (embed a) (embed b)
  | .implies a b => .implies (embed a) (embed b)
  | .all s a => .all s (embed a)
  | .ex s a => .ex s (embed a)

theorem conservativity (S : Structure) (ρ : Valuation S) (a : VE.Formula) :
    (embed a).denote S ρ ↔ a.denote S ρ := by
  induction a generalizing ρ <;> simp_all [embed, Formula.denote, VE.Formula.denote]

def erase : Formula → Option VE.Formula
  | .top => some .top
  | .bottom => some .bottom
  | .unary p t => some (.unary p t)
  | .binary p t u => some (.binary p t u)
  | .eq t u => some (.eq t u)
  | .not a => return .not (← erase a)
  | .and a b => return .and (← erase a) (← erase b)
  | .or a b => return .or (← erase a) (← erase b)
  | .implies a b => return .implies (← erase a) (← erase b)
  | .all s a => return .all s (← erase a)
  | .ex s a => return .ex s (← erase a)
  | .atom .. | .reachNamed .. | .reachBody .. => none

theorem erase_embed (a : VE.Formula) : erase (embed a) = some a := by
  induction a <;> simp_all [erase, embed]

theorem embed_of_erase (a : Formula) (b : VE.Formula) (h : erase a = some b) :
    embed b = a := by
  induction a generalizing b <;> simp only [erase, bind, pure, Option.bind_eq_some_iff, Option.some.injEq, reduceCtorEq] at h <;>
    grind [embed]

/-- Every Reach-free new formula (recognized by erase) has exactly the old denotation. -/
theorem conservativity_without_reach (S : Structure) (ρ : Valuation S)
    (a : Formula) (b : VE.Formula) (h : erase a = some b) :
    a.denote S ρ ↔ b.denote S ρ := by
  rw [← embed_of_erase a b h]
  exact conservativity S ρ b

end VE.Core
