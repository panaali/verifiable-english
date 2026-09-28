import VE.Order.Consequence

/-! The W6 finite-evaluation budget (units-schema gate 4).

Python and Rust charge one unit per formula-node visit, never per term, and stop
with `ResourceLimit` (UNKNOWN) when a visit finds `MAX_EVALUATIONS = 1,000,000`
units already spent. Connectives short-circuit and a quantifier stops at the
first decisive entity. `evalB` is that evaluator: it returns the value and the
work spent, or `none` for UNKNOWN. When it returns a value, the value is the
reference evaluator's (`evalB_sound`), so the budget only ever turns an answer
into UNKNOWN, never into a different answer. -/
namespace VE.Time
open VE.Order

/-- Python/Rust `MAX_EVALUATIONS`. -/
def maxEvaluations : Nat := 1000000

/-! Relation membership in constant time, as Python's `frozenset` and Rust's
`BTreeSet` tables: a hash set per listed predicate, the list otherwise. -/

/-- A hash set of rows for each listed predicate. -/
def relIndex {β : Type} [BEq β] [Hashable β] (rel : String → List (List β)) (ps : List String) :
    Std.HashMap String (Std.HashSet (List β)) :=
  ps.foldr (fun p m => m.insert p (Std.HashSet.ofList (rel p))) {}

/-- Whether `row` is in `rel p`, through the index when it lists `p`. -/
def memIn {β : Type} [BEq β] [Hashable β] (rel : String → List (List β))
    (idx : Std.HashMap String (Std.HashSet (List β))) (p : String) (row : List β) : Bool :=
  match idx[p]? with
  | some h => h.contains row
  | none => (rel p).contains row

theorem memIn_relIndex {β : Type} [BEq β] [LawfulBEq β] [Hashable β]
    (rel : String → List (List β)) (ps : List String) (p : String) (row : List β) :
    memIn rel (relIndex rel ps) p row = true ↔ row ∈ rel p := by
  induction ps with
  | nil => simp [memIn, relIndex]
  | cons q ps ih =>
    simp only [memIn, relIndex, List.foldr_cons] at ih ⊢
    rw [Std.HashMap.getElem?_insert]
    by_cases h : q = p
    · subst h
      simp [Std.HashSet.contains_ofList]
    · have hb : (q == p) = false := beq_eq_false_iff_ne.mpr h
      simp only [hb, Bool.false_eq_true, ↓reduceIte]
      exact ih

/-- A quantifier loop: stop at the first entity whose value differs from
`universal`; with no such entity the value is `universal`. -/
def quantB {β : Type} (universal : Bool) (step : β → Nat → Option (Bool × Nat)) :
    List β → Nat → Option (Bool × Nat)
  | [], w => some (universal, w)
  | v :: vs, w => match step v w with
    | none => none
    | some (b, w') => if b = universal then quantB universal step vs w' else some (!universal, w')

/-- Charge one formula-node visit (Python `tick`): fail when `w ≥ limit`. -/
def charge (limit w : Nat) (k : Nat → Option (Bool × Nat)) : Option (Bool × Nat) :=
  if limit ≤ w then none else k (w + 1)

/-- The budgeted evaluator; `w` is the work already spent. Atoms read their
table through `mem` (`memIn` over `relIndex`), which must agree with list
membership (`evalB_sound`). -/
def evalB {α : Type} [DecidableEq α] (mem : String → List (Value α) → Bool) (M : FiniteModel α)
    (limit : Nat) : List (Value α) → Formula → Nat → Option (Bool × Nat)
  | ρ, .not a, w => charge limit w fun w => (evalB mem M limit ρ a w).map fun r => (!r.1, r.2)
  | ρ, .and a b, w => charge limit w fun w => match evalB mem M limit ρ a w with
    | none => none
    | some (true, w) => evalB mem M limit ρ b w
    | some (false, w) => some (false, w)
  | ρ, .or a b, w => charge limit w fun w => match evalB mem M limit ρ a w with
    | none => none
    | some (true, w) => some (true, w)
    | some (false, w) => evalB mem M limit ρ b w
  | ρ, .implies a b, w => charge limit w fun w => match evalB mem M limit ρ a w with
    | none => none
    | some (true, w) => evalB mem M limit ρ b w
    | some (false, w) => some (true, w)
  | ρ, .all s a, w => charge limit w fun w =>
    quantB true (fun v => evalB mem M limit (.inl v :: ρ) a) (M.domains s) w
  | ρ, .ex s a, w => charge limit w fun w =>
    quantB false (fun v => evalB mem M limit (.inl v :: ρ) a) (M.domains s) w
  | ρ, .unary p t, w => charge limit w fun w => some ((match t.denote M.asStructure ρ with
      | some v => mem p [v]
      | none => false), w)
  | ρ, .binary p t u, w => charge limit w fun w =>
    some ((match t.denote M.asStructure ρ, u.denote M.asStructure ρ with
      | some v, some x => mem p [v, x]
      | _, _ => false), w)
  | ρ, f, w => charge limit w fun w => some (f.eval M ρ, w)

theorem quantB_sound {β : Type} (universal : Bool) (step : β → Nat → Option (Bool × Nat))
    (g : β → Bool) : ∀ (l : List β),
    (∀ v ∈ l, ∀ w r, step v w = some r → r.1 = g v) →
    ∀ w r, quantB universal step l w = some r →
      r.1 = (if universal then l.all g else l.any g)
  | [], _, w, r, h => by
    simp only [quantB, Option.some.injEq] at h
    subst h; cases universal <;> rfl
  | v :: vs, hs, w, r, h => by
    simp only [quantB] at h
    split at h
    · cases h
    · rename_i b w' hstep
      have hb : b = g v := hs v (List.mem_cons_self ..) w (b, w') hstep
      split at h
      · rename_i hu
        have := quantB_sound universal step g vs
          (fun x hx => hs x (List.mem_cons_of_mem _ hx)) w' r h
        rw [this]
        subst hb
        cases universal <;> simp [List.all_cons, List.any_cons, hu]
      · rename_i hu
        simp only [Option.some.injEq] at h
        subst h
        subst hb
        cases universal <;> cases hg : g v <;> simp_all

theorem charge_some {limit w : Nat} {k : Nat → Option (Bool × Nat)} {r : Bool × Nat}
    (h : charge limit w k = some r) : k (w + 1) = some r := by
  unfold charge at h
  split at h
  · cases h
  · exact h

/-- **Budget soundness.** A budgeted value is the reference evaluator's value. -/
theorem evalB_sound {α : Type} [DecidableEq α] (mem : String → List (Value α) → Bool)
    (M : FiniteModel α) (limit : Nat) (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) :
    ∀ (f : Formula) (ρ : List (Value α)) (w : Nat) (r : Bool × Nat),
      evalB mem M limit ρ f w = some r → r.1 = f.eval M ρ := by
  intro f
  induction f with
  | top | bottom | eq | lt | le =>
    intro ρ w r h
    have h := charge_some h
    simp only [Option.some.injEq] at h
    subst h; rfl
  | unary p t =>
    intro ρ w r h
    have h := charge_some h
    simp only [Option.some.injEq] at h
    subst h
    simp only [Formula.eval]
    cases t.denote M.asStructure ρ with
    | none => rfl
    | some v => exact Bool.eq_iff_iff.mpr (by simp [hmem])
  | binary p t u =>
    intro ρ w r h
    have h := charge_some h
    simp only [Option.some.injEq] at h
    subst h
    simp only [Formula.eval]
    cases t.denote M.asStructure ρ <;> cases u.denote M.asStructure ρ <;> try rfl
    exact Bool.eq_iff_iff.mpr (by simp [hmem])
  | not a ih =>
    intro ρ w r h
    have h := charge_some h
    cases ha : evalB mem M limit ρ a (w + 1) with
    | none => rw [ha] at h; cases h
    | some x =>
      rw [ha] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [Formula.eval, ih ρ _ x ha]
  | and a b ia ib =>
    intro ρ w r h
    have h := charge_some h
    simp only at h
    split at h
    · cases h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Formula.eval, ← this, Bool.true_and]
      exact ib ρ _ _ h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [Formula.eval, ← this]
  | or a b ia ib =>
    intro ρ w r h
    have h := charge_some h
    simp only at h
    split at h
    · cases h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [Formula.eval, ← this]
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Formula.eval, ← this, Bool.false_or]
      exact ib ρ _ _ h
  | implies a b ia ib =>
    intro ρ w r h
    have h := charge_some h
    simp only at h
    split at h
    · cases h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Formula.eval, ← this, Bool.not_true, Bool.false_or]
      exact ib ρ _ _ h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [Formula.eval, ← this]
  | all s a ih =>
    intro ρ w r h
    have h := charge_some h
    have := quantB_sound true _ (fun v => a.eval M (.inl v :: ρ)) (M.domains s)
      (fun v _ w r hv => ih _ w r hv) _ r h
    simpa [Formula.eval] using this
  | ex s a ih =>
    intro ρ w r h
    have h := charge_some h
    have := quantB_sound false _ (fun v => a.eval M (.inl v :: ρ)) (M.domains s)
      (fun v _ w r hv => ih _ w r hv) _ r h
    simpa [Formula.eval] using this

/-- The countermodel check under one shared budget, premises first in order,
stopping at the first false premise (Python `_check_countermodel_values`,
Rust `order_case`). `none` is UNKNOWN. -/
def refutesB {α : Type} [DecidableEq α] (mem : String → List (Value α) → Bool) (M : FiniteModel α)
    (limit : Nat) : List Formula → Formula → Nat → Option Bool
  | [], c, w => (evalB mem M limit [] c w).map (fun r => !r.1)
  | p :: ps, c, w => match evalB mem M limit [] p w with
    | none => none
    | some (false, _) => some false
    | some (true, w) => refutesB mem M limit ps c w

/-- A budgeted countermodel verdict is the reference verdict. -/
theorem refutesB_sound {α : Type} [DecidableEq α] (mem : String → List (Value α) → Bool)
    (M : FiniteModel α) (limit : Nat) (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) :
    ∀ (ps : List Formula) (c : Formula) (w : Nat) (b : Bool),
      refutesB mem M limit ps c w = some b → b = countermodelCheck M ps c
  | [], c, w, b, h => by
    simp only [refutesB] at h
    cases hc : evalB mem M limit [] c w with
    | none => rw [hc] at h; cases h
    | some x =>
      rw [hc] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [countermodelCheck, evalB_sound mem M limit hmem c [] w x hc]
  | p :: ps, c, w, b, h => by
    simp only [refutesB] at h
    split at h
    · cases h
    · rename_i w' hp
      have := evalB_sound mem M limit hmem p [] w _ hp
      simp only [Option.some.injEq] at h
      subst h
      simp [countermodelCheck, ← this]
    · rename_i w' hp
      have := evalB_sound mem M limit hmem p [] w _ hp
      rw [refutesB_sound mem M limit hmem ps c w' b h]
      simp [countermodelCheck, ← this]

theorem denote_domains_irrelevant {α : Type} (M N : FiniteModel α)
    (hc : M.constants = N.constants) (ρ : List (Value α)) :
    ∀ t : Term, t.denote M.asStructure ρ = t.denote N.asStructure ρ
  | .var _ | .num _ => rfl
  | .const c => by simp [Term.denote, FiniteModel.asStructure, hc]
  | .add t u => by
    simp only [Term.denote, denote_domains_irrelevant M N hc ρ t, denote_domains_irrelevant M N hc ρ u]
    rcases Term.denote N.asStructure ρ t with _ | _ | _ <;>
      rcases Term.denote N.asStructure ρ u with _ | _ | _ <;> rfl
  | .scale _ t => by
    simp only [Term.denote, denote_domains_irrelevant M N hc ρ t]
    rcases Term.denote N.asStructure ρ t with _ | _ | _ <;> rfl

/-- **Domain order is irrelevant to reference values.** Quantifiers read a
domain through `List.all`/`List.any`, so a reordered presentation of the same
entities has the same values; only the budgeted evaluator's work depends on the
order, which is why the runners present every domain in Python/Rust order. -/
theorem eval_domains_perm {α : Type} [DecidableEq α] (M N : FiniteModel α)
    (hc : M.constants = N.constants) (hr : M.relations = N.relations)
    (hd : ∀ s, (M.domains s).Perm (N.domains s)) :
    ∀ (f : Formula) (ρ : List (Value α)), f.eval M ρ = f.eval N ρ := by
  intro f
  induction f with
  | top | bottom => intro ρ; rfl
  | unary p t =>
    intro ρ
    simp only [Formula.eval, denote_domains_irrelevant M N hc ρ t, hr]
    rcases Term.denote N.asStructure ρ t with _ | _ <;> simp [hr]
  | binary p t u =>
    intro ρ
    simp only [Formula.eval, denote_domains_irrelevant M N hc ρ t,
      denote_domains_irrelevant M N hc ρ u]
    rcases Term.denote N.asStructure ρ t with _ | _ <;>
      rcases Term.denote N.asStructure ρ u with _ | _ <;> simp [hr]
  | eq t u =>
    intro ρ
    simp only [Formula.eval, denote_domains_irrelevant M N hc ρ t,
      denote_domains_irrelevant M N hc ρ u]
    rcases Term.denote N.asStructure ρ t with _ | _ <;>
      rcases Term.denote N.asStructure ρ u with _ | _ <;> rfl
  | lt t u | le t u =>
    intro ρ
    simp only [Formula.eval, denote_domains_irrelevant M N hc ρ t,
      denote_domains_irrelevant M N hc ρ u]
  | not a ih => intro ρ; simp only [Formula.eval, ih ρ]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro ρ; simp only [Formula.eval, ia ρ, ib ρ]
  | all s a ih =>
    intro ρ
    simp only [Formula.eval, ih]
    apply Bool.eq_iff_iff.mpr
    simp only [List.all_eq_true]
    exact ⟨fun h v hv => h v ((hd s).mem_iff.mpr hv), fun h v hv => h v ((hd s).mem_iff.mp hv)⟩
  | ex s a ih =>
    intro ρ
    simp only [Formula.eval, ih]
    apply Bool.eq_iff_iff.mpr
    simp only [List.any_eq_true]
    exact ⟨fun ⟨v, hv, h⟩ => ⟨v, (hd s).mem_iff.mp hv, h⟩,
      fun ⟨v, hv, h⟩ => ⟨v, (hd s).mem_iff.mpr hv, h⟩⟩

theorem countermodelCheck_domains_perm {α : Type} [DecidableEq α] (M N : FiniteModel α)
    (hc : M.constants = N.constants) (hr : M.relations = N.relations)
    (hd : ∀ s, (M.domains s).Perm (N.domains s)) (ps : List Formula) (c : Formula) :
    countermodelCheck M ps c = countermodelCheck N ps c := by
  simp only [countermodelCheck, eval_domains_perm M N hc hr hd]

end VE.Time
