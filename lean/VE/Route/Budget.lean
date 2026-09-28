import VE.Bridge
import VE.Closure.Consequence
import VE.Core.Consequence
import VE.Definitions.Layer
import VE.Order.Wire
import VE.Time.Budget
import VE.Route.Closure

/-! The Python/Rust evaluation budget on the `route` subcommand.

Python `_Evaluator.tick` and Rust `Evaluator::tick` charge one unit per formula
visit and stop with `ResourceLimit` when a visit finds `MAX_EVALUATIONS =
1,000,000` units spent; connectives short-circuit and quantifiers stop at the
first decisive entity (`VE.Time.evalB` is the same evaluator for order
formulas). A reachability node also charges its closure's construction, once
per edge and outer bindings (the closure cache): one unit per named row or the
body's own visits at every pair, then per Warshall pivot one unit per entity
and one per incoming × outgoing pair. Nothing here runs unmetered: the defined
tables of a model are built by the same evaluator under one shared budget and
the tuple limit, one candidate row at a time.

Each evaluator returns a value only when the reference evaluator has that value
(`evalF_sound`, `evalC_sound`, `evalN_sound` and the countermodel forms), so the
budget turns answers into `ResourceLimit`, never into different answers.
Closure values are read from the reference evaluator; the metered construction
only decides whether the budget suffices. -/
namespace VE.Route.Budget
open VE.Time (charge charge_some quantB quantB_sound maxEvaluations)

abbrev Entity := VE.Bridge.Entity

def budgetExhausted : String :=
  "ResourceLimit: formula-node evaluation budget MAX_EVALUATIONS=1000000 exhausted"

/-! ## Relational formulas -/

/-- The budgeted evaluator for `VE.Formula`; `w` is the work already spent. -/
def evalF {α : Type} [DecidableEq α] (mem : String → List α → Bool) (M : VE.FiniteModel α)
    (limit : Nat) :
    List α → VE.Formula → Nat → Option (Bool × Nat)
  | ρ, .not a, w => charge limit w fun w => (evalF mem M limit ρ a w).map fun r => (!r.1, r.2)
  | ρ, .and a b, w => charge limit w fun w => match evalF mem M limit ρ a w with
    | none => none
    | some (true, w) => evalF mem M limit ρ b w
    | some (false, w) => some (false, w)
  | ρ, .or a b, w => charge limit w fun w => match evalF mem M limit ρ a w with
    | none => none
    | some (true, w) => some (true, w)
    | some (false, w) => evalF mem M limit ρ b w
  | ρ, .implies a b, w => charge limit w fun w => match evalF mem M limit ρ a w with
    | none => none
    | some (true, w) => evalF mem M limit ρ b w
    | some (false, w) => some (true, w)
  | ρ, .all s a, w => charge limit w fun w =>
    quantB true (fun v => evalF mem M limit (v :: ρ) a) (M.domains s) w
  | ρ, .ex s a, w => charge limit w fun w =>
    quantB false (fun v => evalF mem M limit (v :: ρ) a) (M.domains s) w
  | ρ, .unary p t, w => charge limit w fun w => some ((match t.denote M.asStructure ρ with
      | some v => mem p [v]
      | none => false), w)
  | ρ, .binary p t u, w => charge limit w fun w =>
    some ((match t.denote M.asStructure ρ, u.denote M.asStructure ρ with
      | some v, some x => mem p [v, x]
      | _, _ => false), w)
  | ρ, f, w => charge limit w fun w => some (f.eval M ρ, w)

/-- A budgeted relational value is the reference value. -/
theorem evalF_sound {α : Type} [DecidableEq α] (mem : String → List α → Bool) (M : VE.FiniteModel α)
    (limit : Nat) (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) :
    ∀ (f : VE.Formula) (ρ : List α) (w : Nat) (r : Bool × Nat),
      evalF mem M limit ρ f w = some r → r.1 = f.eval M ρ := by
  intro f
  induction f with
  | top | bottom | eq =>
    intro ρ w r h
    have h := charge_some h
    simp only [Option.some.injEq] at h
    subst h; rfl
  | unary p t =>
    intro ρ w r h
    have h := charge_some h
    simp only [Option.some.injEq] at h
    subst h
    simp only [VE.Formula.eval]
    cases t.denote M.asStructure ρ with
    | none => rfl
    | some v => exact Bool.eq_iff_iff.mpr (by simp [hmem])
  | binary p t u =>
    intro ρ w r h
    have h := charge_some h
    simp only [Option.some.injEq] at h
    subst h
    simp only [VE.Formula.eval]
    cases t.denote M.asStructure ρ <;> cases u.denote M.asStructure ρ <;> try rfl
    exact Bool.eq_iff_iff.mpr (by simp [hmem])
  | not a ih =>
    intro ρ w r h
    have h := charge_some h
    cases ha : evalF mem M limit ρ a (w + 1) with
    | none => rw [ha] at h; cases h
    | some x =>
      rw [ha] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [VE.Formula.eval, ih ρ _ x ha]
  | and a b ia ib =>
    intro ρ w r h
    have h := charge_some h
    simp only at h
    split at h
    · cases h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [VE.Formula.eval, ← this, Bool.true_and]
      exact ib ρ _ _ h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Formula.eval, ← this]
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
      simp [VE.Formula.eval, ← this]
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [VE.Formula.eval, ← this, Bool.false_or]
      exact ib ρ _ _ h
  | implies a b ia ib =>
    intro ρ w r h
    have h := charge_some h
    simp only at h
    split at h
    · cases h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [VE.Formula.eval, ← this, Bool.not_true, Bool.false_or]
      exact ib ρ _ _ h
    · rename_i w' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Formula.eval, ← this]
  | all s a ih =>
    intro ρ w r h
    have h := charge_some h
    have := quantB_sound true _ (fun v => a.eval M (v :: ρ)) (M.domains s)
      (fun v _ w r hv => ih _ w r hv) _ r h
    simpa [VE.Formula.eval] using this
  | ex s a ih =>
    intro ρ w r h
    have h := charge_some h
    have := quantB_sound false _ (fun v => a.eval M (v :: ρ)) (M.domains s)
      (fun v _ w r hv => ih _ w r hv) _ r h
    simpa [VE.Formula.eval] using this

/-- The countermodel check under one shared budget, premises first, stopping
at the first false premise (Python `_check_countermodel_values`, Rust
`CountermodelProblem::values`). `none` is UNKNOWN. -/
def refutesF {α : Type} [DecidableEq α] (mem : String → List α → Bool) (M : VE.FiniteModel α)
    (limit : Nat) :
    List VE.Formula → VE.Formula → Nat → Option Bool
  | [], c, w => (evalF mem M limit [] c w).map (fun r => !r.1)
  | p :: ps, c, w => match evalF mem M limit [] p w with
    | none => none
    | some (false, _) => some false
    | some (true, w) => refutesF mem M limit ps c w

theorem refutesF_sound {α : Type} [DecidableEq α] (mem : String → List α → Bool) (M : VE.FiniteModel α)
    (limit : Nat) (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) :
    ∀ (ps : List VE.Formula) (c : VE.Formula) (w : Nat) (b : Bool),
      refutesF mem M limit ps c w = some b → b = VE.countermodelCheck M ps c
  | [], c, w, b, h => by
    simp only [refutesF] at h
    cases hc : evalF mem M limit [] c w with
    | none => rw [hc] at h; cases h
    | some x =>
      rw [hc] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [VE.countermodelCheck, evalF_sound mem M limit hmem c [] w x hc]
  | p :: ps, c, w, b, h => by
    simp only [refutesF] at h
    split at h
    · cases h
    · rename_i w' hp
      have := evalF_sound mem M limit hmem p [] w _ hp
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.countermodelCheck, ← this]
    · rename_i w' hp
      have := evalF_sound mem M limit hmem p [] w _ hp
      rw [refutesF_sound mem M limit hmem ps c w' b h]
      simp [VE.countermodelCheck, ← this]

/-- Each formula of a document under its own budget, as Rust `evaluate_formula`
and Python's per-formula evaluation; the first exhausted formula is UNKNOWN. -/
def valuesF {α : Type} [DecidableEq α] (mem : String → List α → Bool) (M : VE.FiniteModel α)
    (fs : List VE.Formula) :
    Except String (List Bool) :=
  fs.mapM fun f => match evalF mem M maxEvaluations [] f 0 with
    | some (b, _) => .ok b
    | none => .error budgetExhausted

theorem valuesF_sound {α : Type} [DecidableEq α] (mem : String → List α → Bool) (M : VE.FiniteModel α)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) (fs : List VE.Formula)
    (vs : List Bool) (h : valuesF mem M fs = .ok vs) : vs = fs.map (fun f => f.eval M []) := by
  induction fs generalizing vs with
  | nil => simp only [valuesF, List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h; simp [← h]
  | cons f fs ih =>
    simp only [valuesF, List.mapM_cons] at h ih
    cases hf : evalF mem M maxEvaluations [] f 0 with
    | none => rw [hf] at h; cases h
    | some r =>
      obtain ⟨b, w⟩ := r
      rw [hf] at h
      cases hr : List.mapM (fun f => match evalF mem M maxEvaluations [] f 0 with
          | some (b, _) => Except.ok b
          | none => Except.error budgetExhausted) fs with
      | error e => rw [hr] at h; cases h
      | ok bs =>
        rw [hr] at h
        simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
        subst h
        have hb := evalF_sound mem M _ hmem f [] 0 (b, w) hf
        simp only at hb
        rw [ih bs hr, hb]
        rfl

/-! ## Order formulas -/

/-- Each submitted domain in Python `sorted` and Rust `sort` order (local
identifiers are ASCII, so code-point, byte and `String` order agree). A budgeted
quantifier stops at the first decisive entity, so its work, and whether the
budget runs out, depends on this order; values never do (`eval_domains_perm`). -/
def sortOrderData (d : VE.Order.ModelData VE.Order.Wire.Entity) :
    VE.Order.ModelData VE.Order.Wire.Entity :=
  { d with domains := d.domains.map fun p => (p.1, p.2.mergeSort fun a b => decide (a.2 ≤ b.2)) }

theorem lookup_map {β γ : Type} (f : β → γ) (xs : List (String × β)) (k : String) :
    VE.Order.lookup (xs.map (fun p => (p.1, f p.2))) k = (VE.Order.lookup xs k).map f := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    by_cases h : x.1 = k
    · simp [VE.Order.lookup, h]
    · have hb : (x.1 == k) = false := beq_eq_false_iff_ne.mpr h
      simp only [VE.Order.lookup, List.map_cons, List.find?_cons, hb] at ih ⊢
      exact ih

theorem sortOrderData_perm (d : VE.Order.ModelData VE.Order.Wire.Entity) (s : String) :
    ((sortOrderData d).toModel.domains s).Perm (d.toModel.domains s) := by
  simp only [sortOrderData, VE.Order.ModelData.toModel,
    lookup_map (fun xs : List VE.Order.Wire.Entity => xs.mergeSort fun a b => decide (a.2 ≤ b.2))]
  cases VE.Order.lookup d.domains s <;> simp [List.mergeSort_perm]

instance hashableValue {α : Type} [Hashable α] : Hashable (VE.Order.Value α) where
  hash
    | .inl a => mixHash 3 (hash a)
    | .inr z => mixHash 5 (hash z)

/-! An index is data: callers build it once (`let idx := ...`) and pass
`orderMem M idx` or `tableMem M idx`, so no lookup rebuilds it. -/

/-- A hash set of order rows, cells compared by decidable equality. -/
abbrev OrderRows (α : Type) [DecidableEq α] [Hashable α] :=
  @Std.HashSet (List (VE.Order.Value α)) (@List.instBEq _ instBEqOfDecidableEq) _

/-- A hash index of the listed predicates' order tables. -/
def orderIndex {α : Type} [DecidableEq α] [Hashable α] (ps : List String)
    (M : VE.Order.FiniteModel α) : Std.HashMap String (OrderRows α) :=
  @VE.Time.relIndex _ instBEqOfDecidableEq _ M.relations ps

def orderMem {α : Type} [DecidableEq α] [Hashable α] (M : VE.Order.FiniteModel α)
    (idx : Std.HashMap String (OrderRows α))
    (p : String) (row : List (VE.Order.Value α)) : Bool :=
  @VE.Time.memIn _ instBEqOfDecidableEq _ M.relations idx p row

theorem orderMem_iff {α : Type} [DecidableEq α] [Hashable α] (ps : List String)
    (M : VE.Order.FiniteModel α) (p : String) (row : List (VE.Order.Value α)) :
    orderMem M (orderIndex ps M) p row = true ↔ row ∈ M.relations p :=
  @VE.Time.memIn_relIndex _ instBEqOfDecidableEq _ _ M.relations ps p row

/-- A hash index of the listed predicates' relational tables. -/
def tableIndex {α : Type} [BEq α] [Hashable α] (ps : List String) (M : VE.FiniteModel α) :
    Std.HashMap String (Std.HashSet (List α)) :=
  VE.Time.relIndex M.relations ps

def tableMem {α : Type} [BEq α] [Hashable α] (M : VE.FiniteModel α)
    (idx : Std.HashMap String (Std.HashSet (List α))) (p : String) (row : List α) : Bool :=
  VE.Time.memIn M.relations idx p row

theorem tableMem_iff {α : Type} [BEq α] [LawfulBEq α] [Hashable α] (ps : List String)
    (M : VE.FiniteModel α) (p : String) (row : List α) :
    tableMem M (tableIndex ps M) p row = true ↔ row ∈ M.relations p :=
  VE.Time.memIn_relIndex M.relations ps p row

/-- Each order formula under its own budget (Rust `order_case`). -/
def orderValues {α : Type} [DecidableEq α] (mem : String → List (VE.Order.Value α) → Bool)
    (M : VE.Order.FiniteModel α) (fs : List VE.Order.Formula) : Except String (List Bool) :=
  fs.mapM fun f => match VE.Time.evalB mem M maxEvaluations [] f 0 with
    | some (b, _) => .ok b
    | none => .error budgetExhausted

theorem orderValues_sound {α : Type} [DecidableEq α] (mem : String → List (VE.Order.Value α) → Bool)
    (M : VE.Order.FiniteModel α) (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p)
    (fs : List VE.Order.Formula) (vs : List Bool) (h : orderValues mem M fs = .ok vs) :
    vs = fs.map (fun f => f.eval M []) := by
  induction fs generalizing vs with
  | nil => simp only [orderValues, List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h; simp [← h]
  | cons f fs ih =>
    simp only [orderValues, List.mapM_cons] at h ih
    cases hf : VE.Time.evalB mem M maxEvaluations [] f 0 with
    | none => rw [hf] at h; cases h
    | some r =>
      obtain ⟨b, w⟩ := r
      rw [hf] at h
      cases hr : List.mapM (fun f => match VE.Time.evalB mem M maxEvaluations [] f 0 with
          | some (b, _) => Except.ok b
          | none => Except.error budgetExhausted) fs with
      | error e => rw [hr] at h; cases h
      | ok bs =>
        rw [hr] at h
        simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
        subst h
        have hb := VE.Time.evalB_sound mem M _ hmem f [] 0 (b, w) hf
        simp only at hb
        rw [ih bs hr, hb]
        rfl

/-- Budgeted order values on the sorted presentation are the reference values
on the submitted model. -/
theorem orderValues_sorted_sound (d : VE.Order.ModelData VE.Order.Wire.Entity) (ps : List String)
    (fs : List VE.Order.Formula) (vs : List Bool)
    (h : orderValues (orderMem (sortOrderData d).toModel (orderIndex ps (sortOrderData d).toModel))
      (sortOrderData d).toModel fs = .ok vs) :
    vs = fs.map (fun f => f.eval d.toModel []) := by
  rw [orderValues_sound _ _ (orderMem_iff ps _) fs vs h]
  exact List.map_congr_left fun f _ =>
    VE.Time.eval_domains_perm (sortOrderData d).toModel d.toModel rfl rfl (sortOrderData_perm d) f []

/-- A budgeted order countermodel verdict on the sorted presentation is the
reference verdict on the submitted model. -/
theorem refutesB_sortOrderData_sound (d : VE.Order.ModelData VE.Order.Wire.Entity) (limit : Nat)
    (names : List String) (ps : List VE.Order.Formula) (c : VE.Order.Formula) (w : Nat) (b : Bool)
    (h : VE.Time.refutesB (orderMem (sortOrderData d).toModel (orderIndex names (sortOrderData d).toModel))
      (sortOrderData d).toModel limit ps c w = some b) :
    b = VE.Order.countermodelCheck d.toModel ps c := by
  rw [VE.Time.refutesB_sound _ _ limit (orderMem_iff names _) ps c w b h]
  exact VE.Time.countermodelCheck_domains_perm (sortOrderData d).toModel d.toModel rfl rfl
    (sortOrderData_perm d) ps c

/-! ## Defined tables -/

def definitionBudget : String := "ResourceLimit: Definition model evaluation budget exhausted"
def tupleLimit : String := "ResourceLimit: tuple count"

/-- The candidate rows of one definition, one at a time in Python `product`
order (the first argument varies slowest; `acc` is the reversed prefix, which
is the body's valuation), each charged to the shared budget; a true row counts
toward the 100,000-tuple limit at once. The state is (work, tuples, rows in
reverse candidate order). -/
def tableB (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (body : VE.Formula) :
    List String → List Entity → Nat × Nat × List (List Entity) →
      Except String (Nat × Nat × List (List Entity))
  | [], acc, (w, n, rows) => match evalF mem M maxEvaluations acc body w with
    | none => .error definitionBudget
    | some (true, w) => if n + 1 > 100000 then .error tupleLimit else .ok (w, n + 1, acc.reverse :: rows)
    | some (false, w) => .ok (w, n, rows)
  | s :: ss, acc, st => (M.domains s).foldlM (fun st v => tableB mem M body ss (v :: acc) st) st

/-- Every defined table in dependency order under one budget, starting from
the supplied tuples (Python `FiniteModel.from_dict`, Rust `FiniteModel::from_value`). -/
def computeDefinedB (d : VE.Bridge.ModelData) (ds : List VE.Definitions.Def) :
    Except String VE.Bridge.ModelData := do
  let base := (d.relations.map (fun p => p.2.length)).foldl (· + ·) 0
  let (d, _, _) ← ds.foldlM (fun (d, w, n) (x : VE.Definitions.Def) => do
      let M := d.toModel
      let idx := tableIndex (d.relations.map Prod.fst) M
      let (w, n, rows) ← tableB (tableMem M idx) M x.body x.args [] (w, n, [])
      pure ({ d with relations := d.relations ++ [(x.name, rows.reverse)] }, w, n)) (d, 0, base)
  pure d

/-! ## Closure charges -/

deriving instance Hashable for VE.Term
deriving instance Hashable for VE.Closure.Kind
deriving instance Hashable for VE.Closure.Formula
deriving instance Hashable for VE.Core.Kind
deriving instance Hashable for VE.Core.Formula

open VE.Route.Closure (Edges Meter EdgeKey CacheOK reachValue namedClosure warshallRun forPairs)

/-- Charge one formula visit (Python `tick`) and keep the closures. -/
def tickM {F : Type} [DecidableEq F] [Hashable F] (limit : Nat) (s : Meter F)
    (k : Meter F → Option (Bool × Meter F)) : Option (Bool × Meter F) :=
  if limit ≤ s.work then none else k { s with work := s.work + 1 }

theorem tickM_some {F : Type} [DecidableEq F] [Hashable F] {limit : Nat} {s : Meter F}
    {k : Meter F → Option (Bool × Meter F)} {r : Bool × Meter F} (h : tickM limit s k = some r) :
    k { s with work := s.work + 1 } = some r := by
  unfold tickM at h
  split at h
  · cases h
  · exact h

/-- A quantifier loop threading any state (`quantB` threads only work). -/
def quantS {β σ : Type} (universal : Bool) (step : β → σ → Option (Bool × σ)) :
    List β → σ → Option (Bool × σ)
  | [], s => some (universal, s)
  | v :: vs, s => match step v s with
    | none => none
    | some (b, s') => if b = universal then quantS universal step vs s' else some (!universal, s')

/-- A quantifier loop's value is the reference value, and it keeps any
invariant its steps keep. -/
theorem quantS_sound {β σ : Type} (P : σ → Prop) (universal : Bool)
    (step : β → σ → Option (Bool × σ)) (g : β → Bool) : ∀ (l : List β),
    (∀ v ∈ l, ∀ s r, P s → step v s = some r → r.1 = g v ∧ P r.2) →
    ∀ s r, P s → quantS universal step l s = some r →
      r.1 = (if universal then l.all g else l.any g) ∧ P r.2
  | [], _, s, r, hs, h => by
    simp only [quantS, Option.some.injEq] at h
    subst h; cases universal <;> exact ⟨rfl, hs⟩
  | v :: vs, hst, s, r, hs, h => by
    simp only [quantS] at h
    split at h
    · cases h
    · rename_i b s' hstep
      obtain ⟨hb, hs'⟩ := hst v (List.mem_cons_self ..) s (b, s') hs hstep
      simp only at hb
      split at h
      · rename_i hu
        obtain ⟨hr, hP⟩ := quantS_sound P universal step g vs
          (fun x hx => hst x (List.mem_cons_of_mem _ hx)) s' r hs' h
        refine ⟨?_, hP⟩
        rw [hr]
        subst hb
        cases universal <;> simp [List.all_cons, List.any_cons, hu]
      · rename_i hu
        simp only [Option.some.injEq] at h
        subst h
        subst hb
        refine ⟨?_, hs'⟩
        cases universal <;> cases hg : g v <;> simp_all

/-! ## Closure formulas -/

/-- The edges of a cached closure: a named relation's rows, or the body's true
pairs over its sort under the key's outer bindings. -/
def closureRel (M : VE.FiniteModel Entity) :
    EdgeKey VE.Closure.Formula × List Entity → Entity → Entity → Prop
  | (.named p, _) => fun x y => [x, y] ∈ M.relations p
  | (.body s a, ρ) => fun x y => x ∈ M.domains s ∧ y ∈ M.domains s ∧ a.eval M (y :: x :: ρ) = true

theorem named_value (M : VE.FiniteModel Entity) (k : VE.Closure.Kind) (p : String) (t u : VE.Term)
    (ρ : List Entity) (c : Edges)
    (hc : ∀ a b, c.contains (a, b) = true ↔ VE.Closure.Path (fun x y => [x, y] ∈ M.relations p) a b) :
    reachValue (decide (k = .star)) c (t.denote M.asStructure ρ) (u.denote M.asStructure ρ) =
      (VE.Closure.Formula.reachNamed k p t u).eval M ρ := by
  simp only [VE.Closure.Formula.eval]
  cases t.denote M.asStructure ρ <;> cases u.denote M.asStructure ρ <;> try rfl
  exact VE.Route.Closure.reachValue_closure k c _ _ (VE.Closure.mem_namedEdges _) hc _ _

theorem body_value (M : VE.FiniteModel Entity) (k : VE.Closure.Kind) (x : String)
    (a : VE.Closure.Formula) (t u : VE.Term) (ρ : List Entity) (c : Edges)
    (hc : ∀ v w, c.contains (v, w) = true ↔ VE.Closure.Path (closureRel M (.body x a, ρ)) v w) :
    reachValue (decide (k = .star)) c (t.denote M.asStructure ρ) (u.denote M.asStructure ρ) =
      (VE.Closure.Formula.reachBody k x a t u).eval M ρ := by
  simp only [VE.Closure.Formula.eval]
  cases t.denote M.asStructure ρ <;> cases u.denote M.asStructure ρ <;> try rfl
  exact VE.Route.Closure.reachValue_closure k c _ _ (VE.Closure.mem_bodyEdges _ _) hc _ _

/-- The budgeted closure evaluator. A reachability node charges its visit and,
unless its closure is cached for these bindings, the closure's construction;
its value is read from the closure (`evalC_sound`). -/
def evalC (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (limit : Nat) :
    List Entity → VE.Closure.Formula → Meter VE.Closure.Formula →
      Option (Bool × Meter VE.Closure.Formula)
  | ρ, .not a, s => tickM limit s fun s => (evalC mem M limit ρ a s).map fun r => (!r.1, r.2)
  | ρ, .and a b, s => tickM limit s fun s => match evalC mem M limit ρ a s with
    | none => none
    | some (true, s) => evalC mem M limit ρ b s
    | some (false, s) => some (false, s)
  | ρ, .or a b, s => tickM limit s fun s => match evalC mem M limit ρ a s with
    | none => none
    | some (true, s) => some (true, s)
    | some (false, s) => evalC mem M limit ρ b s
  | ρ, .implies a b, s => tickM limit s fun s => match evalC mem M limit ρ a s with
    | none => none
    | some (true, s) => evalC mem M limit ρ b s
    | some (false, s) => some (true, s)
  | ρ, .all x a, s => tickM limit s fun s =>
    quantS true (fun v => evalC mem M limit (v :: ρ) a) (M.domains x) s
  | ρ, .ex x a, s => tickM limit s fun s =>
    quantS false (fun v => evalC mem M limit (v :: ρ) a) (M.domains x) s
  | ρ, .reachNamed k p t u, s => tickM limit s fun s =>
    let value := fun c => reachValue (decide (k = .star)) c (t.denote M.asStructure ρ) (u.denote M.asStructure ρ)
    let key := (EdgeKey.named p, ρ)
    match s.cache[key]? with
    | some c => some (value c, s)
    | none => (namedClosure limit (M.relations p) s.work).map
        fun r => (value r.1, ⟨r.2, s.cache.insert key r.1⟩)
  | ρ, .reachBody k x a t u, s => tickM limit s fun s =>
    let value := fun c => reachValue (decide (k = .star)) c (t.denote M.asStructure ρ) (u.denote M.asStructure ρ)
    let key := (EdgeKey.body x a, ρ)
    match s.cache[key]? with
    | some c => some (value c, s)
    | none =>
      match forPairs (fun v w => evalC mem M limit (w :: v :: ρ) a) (M.domains x) (M.domains x) {} s with
      | none => none
      | some (es, s) => (warshallRun limit (M.domains x) (M.domains x) es s.work).map
          fun r => (value r.1, ⟨r.2, s.cache.insert key r.1⟩)
  | ρ, .unary p t, s => tickM limit s fun s => some ((match t.denote M.asStructure ρ with
      | some v => mem p [v]
      | none => false), s)
  | ρ, .binary p t u, s => tickM limit s fun s =>
    some ((match t.denote M.asStructure ρ, u.denote M.asStructure ρ with
      | some v, some x => mem p [v, x]
      | _, _ => false), s)
  | ρ, f, s => tickM limit s fun s => some (f.eval M ρ, s)

/-- A budgeted closure value is the reference value, and every cached closure
stays the finite paths of its edges. -/
theorem evalC_sound (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (limit : Nat)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) :
    ∀ (f : VE.Closure.Formula) (ρ : List Entity) (s : Meter VE.Closure.Formula)
      (r : Bool × Meter VE.Closure.Formula), CacheOK (closureRel M) s →
      evalC mem M limit ρ f s = some r → r.1 = f.eval M ρ ∧ CacheOK (closureRel M) r.2 := by
  intro f
  induction f with
  | top | bottom | eq =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    simp only [Option.some.injEq] at h
    subst h; exact ⟨rfl, hs⟩
  | unary p t =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    simp only [Option.some.injEq] at h
    subst h
    refine ⟨?_, hs⟩
    simp only [VE.Closure.Formula.eval]
    cases t.denote M.asStructure ρ with
    | none => rfl
    | some v => exact Bool.eq_iff_iff.mpr (by simp [hmem])
  | binary p t u =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    simp only [Option.some.injEq] at h
    subst h
    refine ⟨?_, hs⟩
    simp only [VE.Closure.Formula.eval]
    cases t.denote M.asStructure ρ <;> cases u.denote M.asStructure ρ <;> try rfl
    exact Bool.eq_iff_iff.mpr (by simp [hmem])
  | reachNamed k p t u =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    simp only at h
    split at h
    · rename_i c hcache
      simp only [Option.some.injEq] at h
      subst h
      exact ⟨named_value M k p t u ρ c (hs _ c hcache), hs⟩
    · obtain ⟨⟨c, w⟩, hn, rfl⟩ := Option.map_eq_some_iff.mp h
      have hc := VE.Route.Closure.namedClosure_spec _ _ _ c w hn
      exact ⟨named_value M k p t u ρ c hc, VE.Route.Closure.cacheOK_insert hs (EdgeKey.named p, ρ) c hc w⟩
  | reachBody k x a t u ih =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    simp only at h
    split at h
    · rename_i c hcache
      simp only [Option.some.injEq] at h
      subst h
      exact ⟨body_value M k x a t u ρ c (hs _ c hcache), hs⟩
    · split at h
      · cases h
      · rename_i es s₁ hpairs
        obtain ⟨⟨c, w⟩, hw, rfl⟩ := Option.map_eq_some_iff.mp h
        obtain ⟨hs₁, hes⟩ := VE.Route.Closure.forPairs_spec (CacheOK (closureRel M))
          (fun v w => a.eval M (w :: v :: ρ)) _
          (fun v w s r hs h => ih (w :: v :: ρ) s r hs h) (M.domains x) (M.domains x) {} es _ s₁ hs hpairs
        have hes' : ∀ v w, es.contains (v, w) = true ↔
            v ∈ M.domains x ∧ w ∈ M.domains x ∧ a.eval M (w :: v :: ρ) = true := by
          intro v w; rw [hes]; simp
        have hc := VE.Route.Closure.bodyClosure_spec limit (M.domains x) _ es hes' _ c w hw
        exact ⟨body_value M k x a t u ρ c hc, VE.Route.Closure.cacheOK_insert hs₁ (EdgeKey.body x a, ρ) c hc w⟩
  | not a ih =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    cases ha : evalC mem M limit ρ a { s with work := s.work + 1 } with
    | none => rw [ha] at h; cases h
    | some x =>
      rw [ha] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      obtain ⟨hx, hP⟩ := ih ρ _ x hs ha
      exact ⟨by simp [VE.Closure.Formula.eval, hx], hP⟩
  | and a b ia ib =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      obtain ⟨hr, hP'⟩ := ib ρ _ _ hP h
      exact ⟨by simp only [VE.Closure.Formula.eval, ← hv, Bool.true_and]; exact hr, hP'⟩
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      simp only [Option.some.injEq] at h
      subst h
      exact ⟨by simp [VE.Closure.Formula.eval, ← hv], hP⟩
  | or a b ia ib =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      simp only [Option.some.injEq] at h
      subst h
      exact ⟨by simp [VE.Closure.Formula.eval, ← hv], hP⟩
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      obtain ⟨hr, hP'⟩ := ib ρ _ _ hP h
      exact ⟨by simp only [VE.Closure.Formula.eval, ← hv, Bool.false_or]; exact hr, hP'⟩
  | implies a b ia ib =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      obtain ⟨hr, hP'⟩ := ib ρ _ _ hP h
      exact ⟨by simp only [VE.Closure.Formula.eval, ← hv, Bool.not_true, Bool.false_or]; exact hr, hP'⟩
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      simp only [Option.some.injEq] at h
      subst h
      exact ⟨by simp [VE.Closure.Formula.eval, ← hv], hP⟩
  | all x a ih =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    obtain ⟨hv, hP⟩ := quantS_sound (CacheOK (closureRel M)) true _ (fun v => a.eval M (v :: ρ))
      (M.domains x) (fun v _ s r hs hv => ih _ s r hs hv) _ r hs h
    exact ⟨by simpa [VE.Closure.Formula.eval] using hv, hP⟩
  | ex x a ih =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRel M) { s with work := s.work + 1 } := hs
    obtain ⟨hv, hP⟩ := quantS_sound (CacheOK (closureRel M)) false _ (fun v => a.eval M (v :: ρ))
      (M.domains x) (fun v _ s r hs hv => ih _ s r hs hv) _ r hs h
    exact ⟨by simpa [VE.Closure.Formula.eval] using hv, hP⟩

/-- Premises first under one budget, a fresh closure cache per formula (Python
witness checking, Rust `clear_closures`). -/
def refutesC (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (limit : Nat) :
    List VE.Closure.Formula → VE.Closure.Formula → Nat → Option Bool
  | [], c, w => (evalC mem M limit [] c ⟨w, {}⟩).map (fun r => !r.1)
  | p :: ps, c, w => match evalC mem M limit [] p ⟨w, {}⟩ with
    | none => none
    | some (false, _) => some false
    | some (true, s) => refutesC mem M limit ps c s.work

theorem refutesC_sound (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (limit : Nat)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) :
    ∀ (ps : List VE.Closure.Formula) (c : VE.Closure.Formula) (w : Nat) (b : Bool),
      refutesC mem M limit ps c w = some b → b = VE.Closure.countermodelCheck M ps c
  | [], c, w, b, h => by
    simp only [refutesC] at h
    cases hc : evalC mem M limit [] c ⟨w, {}⟩ with
    | none => rw [hc] at h; cases h
    | some x =>
      rw [hc] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [VE.Closure.countermodelCheck,
        (evalC_sound mem M limit hmem c [] _ x (VE.Route.Closure.cacheOK_empty _ w) hc).1]
  | p :: ps, c, w, b, h => by
    simp only [refutesC] at h
    split at h
    · cases h
    · rename_i s' hp
      have := (evalC_sound mem M limit hmem p [] _ _ (VE.Route.Closure.cacheOK_empty _ w) hp).1
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Closure.countermodelCheck, ← this]
    · rename_i s' hp
      have := (evalC_sound mem M limit hmem p [] _ _ (VE.Route.Closure.cacheOK_empty _ w) hp).1
      rw [refutesC_sound mem M limit hmem ps c _ b h]
      simp [VE.Closure.countermodelCheck, ← this]

def valuesC (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (fs : List VE.Closure.Formula) :
    Except String (List Bool) :=
  fs.mapM fun f => match evalC mem M maxEvaluations [] f ⟨0, {}⟩ with
    | some (b, _) => .ok b
    | none => .error budgetExhausted

theorem valuesC_sound (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) (fs : List VE.Closure.Formula)
    (vs : List Bool) (h : valuesC mem M fs = .ok vs) : vs = fs.map (fun f => f.eval M []) := by
  induction fs generalizing vs with
  | nil => simp only [valuesC, List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h; simp [← h]
  | cons f fs ih =>
    simp only [valuesC, List.mapM_cons] at h ih
    cases hf : evalC mem M maxEvaluations [] f ⟨0, {}⟩ with
    | none => rw [hf] at h; cases h
    | some r =>
      obtain ⟨b, s⟩ := r
      rw [hf] at h
      cases hr : List.mapM (fun f => match evalC mem M maxEvaluations [] f ⟨0, {}⟩ with
          | some (b, _) => Except.ok b
          | none => Except.error budgetExhausted) fs with
      | error e => rw [hr] at h; cases h
      | ok bs =>
        rw [hr] at h
        simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
        subst h
        have hb := (evalC_sound mem M _ hmem f [] _ (b, s) (VE.Route.Closure.cacheOK_empty _ 0) hf).1
        simp only at hb
        rw [ih bs hr, hb]
        rfl

/-! ## Closure with n-ary atoms -/

/-- The edges of a cached closure: a named relation's rows, or the body's true
pairs over its sort under the key's outer bindings. -/
def closureRelN (M : VE.FiniteModel Entity) :
    EdgeKey VE.Core.Formula × List Entity → Entity → Entity → Prop
  | (.named p, _) => fun x y => [x, y] ∈ M.relations p
  | (.body s a, ρ) => fun x y => x ∈ M.domains s ∧ y ∈ M.domains s ∧ a.eval M (y :: x :: ρ) = true

theorem named_valueN (M : VE.FiniteModel Entity) (k : VE.Core.Kind) (p : String) (t u : VE.Term)
    (ρ : List Entity) (c : Edges)
    (hc : ∀ a b, c.contains (a, b) = true ↔ VE.Closure.Path (fun x y => [x, y] ∈ M.relations p) a b) :
    reachValue (decide (k = .star)) c (t.denote M.asStructure ρ) (u.denote M.asStructure ρ) =
      (VE.Core.Formula.reachNamed k p t u).eval M ρ := by
  simp only [VE.Core.Formula.eval]
  cases t.denote M.asStructure ρ <;> cases u.denote M.asStructure ρ <;> try rfl
  exact VE.Route.Closure.reachValue_core k c _ _ (VE.Core.mem_namedEdges _) hc _ _

theorem body_valueN (M : VE.FiniteModel Entity) (k : VE.Core.Kind) (x : String)
    (a : VE.Core.Formula) (t u : VE.Term) (ρ : List Entity) (c : Edges)
    (hc : ∀ v w, c.contains (v, w) = true ↔ VE.Closure.Path (closureRelN M (.body x a, ρ)) v w) :
    reachValue (decide (k = .star)) c (t.denote M.asStructure ρ) (u.denote M.asStructure ρ) =
      (VE.Core.Formula.reachBody k x a t u).eval M ρ := by
  simp only [VE.Core.Formula.eval]
  cases t.denote M.asStructure ρ <;> cases u.denote M.asStructure ρ <;> try rfl
  exact VE.Route.Closure.reachValue_core k c _ _ (VE.Core.mem_bodyEdges _ _) hc _ _

/-- The budgeted closure evaluator. A reachability node charges its visit and,
unless its closure is cached for these bindings, the closure's construction;
its value is read from the closure (`evalN_sound`). -/
def evalN (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (limit : Nat) :
    List Entity → VE.Core.Formula → Meter VE.Core.Formula →
      Option (Bool × Meter VE.Core.Formula)
  | ρ, .not a, s => tickM limit s fun s => (evalN mem M limit ρ a s).map fun r => (!r.1, r.2)
  | ρ, .and a b, s => tickM limit s fun s => match evalN mem M limit ρ a s with
    | none => none
    | some (true, s) => evalN mem M limit ρ b s
    | some (false, s) => some (false, s)
  | ρ, .or a b, s => tickM limit s fun s => match evalN mem M limit ρ a s with
    | none => none
    | some (true, s) => some (true, s)
    | some (false, s) => evalN mem M limit ρ b s
  | ρ, .implies a b, s => tickM limit s fun s => match evalN mem M limit ρ a s with
    | none => none
    | some (true, s) => evalN mem M limit ρ b s
    | some (false, s) => some (true, s)
  | ρ, .all x a, s => tickM limit s fun s =>
    quantS true (fun v => evalN mem M limit (v :: ρ) a) (M.domains x) s
  | ρ, .ex x a, s => tickM limit s fun s =>
    quantS false (fun v => evalN mem M limit (v :: ρ) a) (M.domains x) s
  | ρ, .reachNamed k p t u, s => tickM limit s fun s =>
    let value := fun c => reachValue (decide (k = .star)) c (t.denote M.asStructure ρ) (u.denote M.asStructure ρ)
    let key := (EdgeKey.named p, ρ)
    match s.cache[key]? with
    | some c => some (value c, s)
    | none => (namedClosure limit (M.relations p) s.work).map
        fun r => (value r.1, ⟨r.2, s.cache.insert key r.1⟩)
  | ρ, .reachBody k x a t u, s => tickM limit s fun s =>
    let value := fun c => reachValue (decide (k = .star)) c (t.denote M.asStructure ρ) (u.denote M.asStructure ρ)
    let key := (EdgeKey.body x a, ρ)
    match s.cache[key]? with
    | some c => some (value c, s)
    | none =>
      match forPairs (fun v w => evalN mem M limit (w :: v :: ρ) a) (M.domains x) (M.domains x) {} s with
      | none => none
      | some (es, s) => (warshallRun limit (M.domains x) (M.domains x) es s.work).map
          fun r => (value r.1, ⟨r.2, s.cache.insert key r.1⟩)
  | ρ, .unary p t, s => tickM limit s fun s => some ((match t.denote M.asStructure ρ with
      | some v => mem p [v]
      | none => false), s)
  | ρ, .binary p t u, s => tickM limit s fun s =>
    some ((match t.denote M.asStructure ρ, u.denote M.asStructure ρ with
      | some v, some x => mem p [v, x]
      | _, _ => false), s)
  | ρ, .atom p ts, s => tickM limit s fun s =>
    some ((match ts.mapM (·.denote M.asStructure ρ) with
      | some vs => mem p vs
      | none => false), s)
  | ρ, f, s => tickM limit s fun s => some (f.eval M ρ, s)

/-- A budgeted closure value is the reference value, and every cached closure
stays the finite paths of its edges. -/
theorem evalN_sound (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (limit : Nat)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) :
    ∀ (f : VE.Core.Formula) (ρ : List Entity) (s : Meter VE.Core.Formula)
      (r : Bool × Meter VE.Core.Formula), CacheOK (closureRelN M) s →
      evalN mem M limit ρ f s = some r → r.1 = f.eval M ρ ∧ CacheOK (closureRelN M) r.2 := by
  intro f
  induction f with
  | top | bottom | eq =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    simp only [Option.some.injEq] at h
    subst h; exact ⟨rfl, hs⟩
  | unary p t =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    simp only [Option.some.injEq] at h
    subst h
    refine ⟨?_, hs⟩
    simp only [VE.Core.Formula.eval]
    cases t.denote M.asStructure ρ with
    | none => rfl
    | some v => exact Bool.eq_iff_iff.mpr (by simp [hmem])
  | binary p t u =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    simp only [Option.some.injEq] at h
    subst h
    refine ⟨?_, hs⟩
    simp only [VE.Core.Formula.eval]
    cases t.denote M.asStructure ρ <;> cases u.denote M.asStructure ρ <;> try rfl
    exact Bool.eq_iff_iff.mpr (by simp [hmem])
  | atom p ts =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    simp only [Option.some.injEq] at h
    subst h
    refine ⟨?_, hs⟩
    simp only [VE.Core.Formula.eval]
    cases ts.mapM (·.denote M.asStructure ρ) with
    | none => rfl
    | some vs => exact Bool.eq_iff_iff.mpr (by simp [hmem])
  | reachNamed k p t u =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    simp only at h
    split at h
    · rename_i c hcache
      simp only [Option.some.injEq] at h
      subst h
      exact ⟨named_valueN M k p t u ρ c (hs _ c hcache), hs⟩
    · obtain ⟨⟨c, w⟩, hn, rfl⟩ := Option.map_eq_some_iff.mp h
      have hc := VE.Route.Closure.namedClosure_spec _ _ _ c w hn
      exact ⟨named_valueN M k p t u ρ c hc, VE.Route.Closure.cacheOK_insert hs (EdgeKey.named p, ρ) c hc w⟩
  | reachBody k x a t u ih =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    simp only at h
    split at h
    · rename_i c hcache
      simp only [Option.some.injEq] at h
      subst h
      exact ⟨body_valueN M k x a t u ρ c (hs _ c hcache), hs⟩
    · split at h
      · cases h
      · rename_i es s₁ hpairs
        obtain ⟨⟨c, w⟩, hw, rfl⟩ := Option.map_eq_some_iff.mp h
        obtain ⟨hs₁, hes⟩ := VE.Route.Closure.forPairs_spec (CacheOK (closureRelN M))
          (fun v w => a.eval M (w :: v :: ρ)) _
          (fun v w s r hs h => ih (w :: v :: ρ) s r hs h) (M.domains x) (M.domains x) {} es _ s₁ hs hpairs
        have hes' : ∀ v w, es.contains (v, w) = true ↔
            v ∈ M.domains x ∧ w ∈ M.domains x ∧ a.eval M (w :: v :: ρ) = true := by
          intro v w; rw [hes]; simp
        have hc := VE.Route.Closure.bodyClosure_spec limit (M.domains x) _ es hes' _ c w hw
        exact ⟨body_valueN M k x a t u ρ c hc, VE.Route.Closure.cacheOK_insert hs₁ (EdgeKey.body x a, ρ) c hc w⟩
  | not a ih =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    cases ha : evalN mem M limit ρ a { s with work := s.work + 1 } with
    | none => rw [ha] at h; cases h
    | some x =>
      rw [ha] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      obtain ⟨hx, hP⟩ := ih ρ _ x hs ha
      exact ⟨by simp [VE.Core.Formula.eval, hx], hP⟩
  | and a b ia ib =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      obtain ⟨hr, hP'⟩ := ib ρ _ _ hP h
      exact ⟨by simp only [VE.Core.Formula.eval, ← hv, Bool.true_and]; exact hr, hP'⟩
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      simp only [Option.some.injEq] at h
      subst h
      exact ⟨by simp [VE.Core.Formula.eval, ← hv], hP⟩
  | or a b ia ib =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      simp only [Option.some.injEq] at h
      subst h
      exact ⟨by simp [VE.Core.Formula.eval, ← hv], hP⟩
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      obtain ⟨hr, hP'⟩ := ib ρ _ _ hP h
      exact ⟨by simp only [VE.Core.Formula.eval, ← hv, Bool.false_or]; exact hr, hP'⟩
  | implies a b ia ib =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      obtain ⟨hr, hP'⟩ := ib ρ _ _ hP h
      exact ⟨by simp only [VE.Core.Formula.eval, ← hv, Bool.not_true, Bool.false_or]; exact hr, hP'⟩
    · rename_i s' ha
      obtain ⟨hv, hP⟩ := ia ρ _ _ hs ha
      simp only [Option.some.injEq] at h
      subst h
      exact ⟨by simp [VE.Core.Formula.eval, ← hv], hP⟩
  | all x a ih =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    obtain ⟨hv, hP⟩ := quantS_sound (CacheOK (closureRelN M)) true _ (fun v => a.eval M (v :: ρ))
      (M.domains x) (fun v _ s r hs hv => ih _ s r hs hv) _ r hs h
    exact ⟨by simpa [VE.Core.Formula.eval] using hv, hP⟩
  | ex x a ih =>
    intro ρ s r hs h
    have h := tickM_some h
    have hs : CacheOK (closureRelN M) { s with work := s.work + 1 } := hs
    obtain ⟨hv, hP⟩ := quantS_sound (CacheOK (closureRelN M)) false _ (fun v => a.eval M (v :: ρ))
      (M.domains x) (fun v _ s r hs hv => ih _ s r hs hv) _ r hs h
    exact ⟨by simpa [VE.Core.Formula.eval] using hv, hP⟩

/-- Premises first under one budget, a fresh closure cache per formula (Python
witness checking, Rust `clear_closures`). -/
def refutesN (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (limit : Nat) :
    List VE.Core.Formula → VE.Core.Formula → Nat → Option Bool
  | [], c, w => (evalN mem M limit [] c ⟨w, {}⟩).map (fun r => !r.1)
  | p :: ps, c, w => match evalN mem M limit [] p ⟨w, {}⟩ with
    | none => none
    | some (false, _) => some false
    | some (true, s) => refutesN mem M limit ps c s.work

theorem refutesN_sound (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (limit : Nat)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) :
    ∀ (ps : List VE.Core.Formula) (c : VE.Core.Formula) (w : Nat) (b : Bool),
      refutesN mem M limit ps c w = some b → b = VE.Core.countermodelCheck M ps c
  | [], c, w, b, h => by
    simp only [refutesN] at h
    cases hc : evalN mem M limit [] c ⟨w, {}⟩ with
    | none => rw [hc] at h; cases h
    | some x =>
      rw [hc] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [VE.Core.countermodelCheck,
        (evalN_sound mem M limit hmem c [] _ x (VE.Route.Closure.cacheOK_empty _ w) hc).1]
  | p :: ps, c, w, b, h => by
    simp only [refutesN] at h
    split at h
    · cases h
    · rename_i s' hp
      have := (evalN_sound mem M limit hmem p [] _ _ (VE.Route.Closure.cacheOK_empty _ w) hp).1
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Core.countermodelCheck, ← this]
    · rename_i s' hp
      have := (evalN_sound mem M limit hmem p [] _ _ (VE.Route.Closure.cacheOK_empty _ w) hp).1
      rw [refutesN_sound mem M limit hmem ps c _ b h]
      simp [VE.Core.countermodelCheck, ← this]

def valuesN (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity) (fs : List VE.Core.Formula) :
    Except String (List Bool) :=
  fs.mapM fun f => match evalN mem M maxEvaluations [] f ⟨0, {}⟩ with
    | some (b, _) => .ok b
    | none => .error budgetExhausted

theorem valuesN_sound (mem : String → List Entity → Bool) (M : VE.FiniteModel Entity)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) (fs : List VE.Core.Formula)
    (vs : List Bool) (h : valuesN mem M fs = .ok vs) : vs = fs.map (fun f => f.eval M []) := by
  induction fs generalizing vs with
  | nil => simp only [valuesN, List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h; simp [← h]
  | cons f fs ih =>
    simp only [valuesN, List.mapM_cons] at h ih
    cases hf : evalN mem M maxEvaluations [] f ⟨0, {}⟩ with
    | none => rw [hf] at h; cases h
    | some r =>
      obtain ⟨b, s⟩ := r
      rw [hf] at h
      cases hr : List.mapM (fun f => match evalN mem M maxEvaluations [] f ⟨0, {}⟩ with
          | some (b, _) => Except.ok b
          | none => Except.error budgetExhausted) fs with
      | error e => rw [hr] at h; cases h
      | ok bs =>
        rw [hr] at h
        simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
        subst h
        have hb := (evalN_sound mem M _ hmem f [] _ (b, s) (VE.Route.Closure.cacheOK_empty _ 0) hf).1
        simp only at hb
        rw [ih bs hr, hb]
        rfl

end VE.Route.Budget
