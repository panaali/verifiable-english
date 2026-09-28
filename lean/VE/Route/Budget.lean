import VE.Bridge
import VE.Closure.Consequence
import VE.Core.Consequence
import VE.Definitions.Layer
import VE.Order.Wire
import VE.Time.Budget

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
def evalF {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (limit : Nat) :
    List α → VE.Formula → Nat → Option (Bool × Nat)
  | ρ, .not a, w => charge limit w fun w => (evalF M limit ρ a w).map fun r => (!r.1, r.2)
  | ρ, .and a b, w => charge limit w fun w => match evalF M limit ρ a w with
    | none => none
    | some (true, w) => evalF M limit ρ b w
    | some (false, w) => some (false, w)
  | ρ, .or a b, w => charge limit w fun w => match evalF M limit ρ a w with
    | none => none
    | some (true, w) => some (true, w)
    | some (false, w) => evalF M limit ρ b w
  | ρ, .implies a b, w => charge limit w fun w => match evalF M limit ρ a w with
    | none => none
    | some (true, w) => evalF M limit ρ b w
    | some (false, w) => some (true, w)
  | ρ, .all s a, w => charge limit w fun w =>
    quantB true (fun v => evalF M limit (v :: ρ) a) (M.domains s) w
  | ρ, .ex s a, w => charge limit w fun w =>
    quantB false (fun v => evalF M limit (v :: ρ) a) (M.domains s) w
  | ρ, f, w => charge limit w fun w => some (f.eval M ρ, w)

/-- A budgeted relational value is the reference value. -/
theorem evalF_sound {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (limit : Nat) :
    ∀ (f : VE.Formula) (ρ : List α) (w : Nat) (r : Bool × Nat),
      evalF M limit ρ f w = some r → r.1 = f.eval M ρ := by
  intro f
  induction f with
  | top | bottom | unary | binary | eq =>
    intro ρ w r h
    have h := charge_some h
    simp only [Option.some.injEq] at h
    subst h; rfl
  | not a ih =>
    intro ρ w r h
    have h := charge_some h
    cases ha : evalF M limit ρ a (w + 1) with
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
def refutesF {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (limit : Nat) :
    List VE.Formula → VE.Formula → Nat → Option Bool
  | [], c, w => (evalF M limit [] c w).map (fun r => !r.1)
  | p :: ps, c, w => match evalF M limit [] p w with
    | none => none
    | some (false, _) => some false
    | some (true, w) => refutesF M limit ps c w

theorem refutesF_sound {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (limit : Nat) :
    ∀ (ps : List VE.Formula) (c : VE.Formula) (w : Nat) (b : Bool),
      refutesF M limit ps c w = some b → b = VE.countermodelCheck M ps c
  | [], c, w, b, h => by
    simp only [refutesF] at h
    cases hc : evalF M limit [] c w with
    | none => rw [hc] at h; cases h
    | some x =>
      rw [hc] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [VE.countermodelCheck, evalF_sound M limit c [] w x hc]
  | p :: ps, c, w, b, h => by
    simp only [refutesF] at h
    split at h
    · cases h
    · rename_i w' hp
      have := evalF_sound M limit p [] w _ hp
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.countermodelCheck, ← this]
    · rename_i w' hp
      have := evalF_sound M limit p [] w _ hp
      rw [refutesF_sound M limit ps c w' b h]
      simp [VE.countermodelCheck, ← this]

/-- Each formula of a document under its own budget, as Rust `evaluate_formula`
and Python's per-formula evaluation; the first exhausted formula is UNKNOWN. -/
def valuesF {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (fs : List VE.Formula) :
    Except String (List Bool) :=
  fs.mapM fun f => match evalF M maxEvaluations [] f 0 with
    | some (b, _) => .ok b
    | none => .error budgetExhausted

theorem valuesF_sound {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (fs : List VE.Formula)
    (vs : List Bool) (h : valuesF M fs = .ok vs) : vs = fs.map (fun f => f.eval M []) := by
  induction fs generalizing vs with
  | nil => simp only [valuesF, List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h; simp [← h]
  | cons f fs ih =>
    simp only [valuesF, List.mapM_cons] at h ih
    cases hf : evalF M maxEvaluations [] f 0 with
    | none => rw [hf] at h; cases h
    | some r =>
      obtain ⟨b, w⟩ := r
      rw [hf] at h
      cases hr : List.mapM (fun f => match evalF M maxEvaluations [] f 0 with
          | some (b, _) => Except.ok b
          | none => Except.error budgetExhausted) fs with
      | error e => rw [hr] at h; cases h
      | ok bs =>
        rw [hr] at h
        simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
        subst h
        have hb := evalF_sound M _ f [] 0 (b, w) hf
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

/-- Each order formula under its own budget (Rust `order_case`). -/
def orderValues {α : Type} [DecidableEq α] (M : VE.Order.FiniteModel α)
    (fs : List VE.Order.Formula) : Except String (List Bool) :=
  fs.mapM fun f => match VE.Time.evalB M maxEvaluations [] f 0 with
    | some (b, _) => .ok b
    | none => .error budgetExhausted

theorem orderValues_sound {α : Type} [DecidableEq α] (M : VE.Order.FiniteModel α)
    (fs : List VE.Order.Formula) (vs : List Bool) (h : orderValues M fs = .ok vs) :
    vs = fs.map (fun f => f.eval M []) := by
  induction fs generalizing vs with
  | nil => simp only [orderValues, List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h; simp [← h]
  | cons f fs ih =>
    simp only [orderValues, List.mapM_cons] at h ih
    cases hf : VE.Time.evalB M maxEvaluations [] f 0 with
    | none => rw [hf] at h; cases h
    | some r =>
      obtain ⟨b, w⟩ := r
      rw [hf] at h
      cases hr : List.mapM (fun f => match VE.Time.evalB M maxEvaluations [] f 0 with
          | some (b, _) => Except.ok b
          | none => Except.error budgetExhausted) fs with
      | error e => rw [hr] at h; cases h
      | ok bs =>
        rw [hr] at h
        simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
        subst h
        have hb := VE.Time.evalB_sound M _ f [] 0 (b, w) hf
        simp only at hb
        rw [ih bs hr, hb]
        rfl

/-- Budgeted order values on the sorted presentation are the reference values
on the submitted model. -/
theorem orderValues_sorted_sound (d : VE.Order.ModelData VE.Order.Wire.Entity)
    (fs : List VE.Order.Formula) (vs : List Bool)
    (h : orderValues (sortOrderData d).toModel fs = .ok vs) :
    vs = fs.map (fun f => f.eval d.toModel []) := by
  rw [orderValues_sound _ fs vs h]
  exact List.map_congr_left fun f _ =>
    VE.Time.eval_domains_perm (sortOrderData d).toModel d.toModel rfl rfl (sortOrderData_perm d) f []

/-- A budgeted order countermodel verdict on the sorted presentation is the
reference verdict on the submitted model. -/
theorem refutesB_sortOrderData_sound (d : VE.Order.ModelData VE.Order.Wire.Entity) (limit : Nat)
    (ps : List VE.Order.Formula) (c : VE.Order.Formula) (w : Nat) (b : Bool)
    (h : VE.Time.refutesB (sortOrderData d).toModel limit ps c w = some b) :
    b = VE.Order.countermodelCheck d.toModel ps c := by
  rw [VE.Time.refutesB_sound _ limit ps c w b h]
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
def tableB (M : VE.FiniteModel Entity) (body : VE.Formula) :
    List String → List Entity → Nat × Nat × List (List Entity) →
      Except String (Nat × Nat × List (List Entity))
  | [], acc, (w, n, rows) => match evalF M maxEvaluations acc body w with
    | none => .error definitionBudget
    | some (true, w) => if n + 1 > 100000 then .error tupleLimit else .ok (w, n + 1, acc.reverse :: rows)
    | some (false, w) => .ok (w, n, rows)
  | s :: ss, acc, st => (M.domains s).foldlM (fun st v => tableB M body ss (v :: acc) st) st

/-- Every defined table in dependency order under one budget, starting from
the supplied tuples (Python `FiniteModel.from_dict`, Rust `FiniteModel::from_value`). -/
def computeDefinedB (d : VE.Bridge.ModelData) (ds : List VE.Definitions.Def) :
    Except String VE.Bridge.ModelData := do
  let base := (d.relations.map (fun p => p.2.length)).foldl (· + ·) 0
  let (d, _, _) ← ds.foldlM (fun (d, w, n) (x : VE.Definitions.Def) => do
      let (w, n, rows) ← tableB d.toModel x.body x.args [] (w, n, [])
      pure ({ d with relations := d.relations ++ [(x.name, rows.reverse)] }, w, n)) (d, 0, base)
  pure d

/-! ## Closure charges -/

deriving instance Hashable for VE.Term
deriving instance Hashable for VE.Closure.Kind
deriving instance Hashable for VE.Closure.Formula
deriving instance Hashable for VE.Core.Kind
deriving instance Hashable for VE.Core.Formula

/-- Work spent and the closures already built, by edge and outer bindings. -/
structure Meter (K : Type) [BEq K] [Hashable K] where
  work : Nat
  cache : Std.HashSet (K × List Entity)

def tickM {K : Type} [BEq K] [Hashable K] (limit : Nat) (s : Meter K)
    (k : Meter K → Option (Bool × Meter K)) : Option (Bool × Meter K) :=
  if limit ≤ s.work then none else k { s with work := s.work + 1 }

theorem tickM_some {K : Type} [BEq K] [Hashable K] {limit : Nat} {s : Meter K}
    {k : Meter K → Option (Bool × Meter K)} {r : Bool × Meter K} (h : tickM limit s k = some r) :
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

theorem quantS_sound {β σ : Type} (universal : Bool) (step : β → σ → Option (Bool × σ))
    (g : β → Bool) : ∀ (l : List β),
    (∀ v ∈ l, ∀ s r, step v s = some r → r.1 = g v) →
    ∀ s r, quantS universal step l s = some r →
      r.1 = (if universal then l.all g else l.any g)
  | [], _, s, r, h => by
    simp only [quantS, Option.some.injEq] at h
    subst h; cases universal <;> rfl
  | v :: vs, hs, s, r, h => by
    simp only [quantS] at h
    split at h
    · cases h
    · rename_i b s' hstep
      have hb : b = g v := hs v (List.mem_cons_self ..) s (b, s') hstep
      split at h
      · rename_i hu
        have := quantS_sound universal step g vs
          (fun x hx => hs x (List.mem_cons_of_mem _ hx)) s' r h
        rw [this]
        subst hb
        cases universal <;> simp [List.all_cons, List.any_cons, hu]
      · rename_i hu
        simp only [Option.some.injEq] at h
        subst h
        subst hb
        cases universal <;> cases hg : g v <;> simp_all

abbrev Edges := Std.HashSet (Entity × Entity)

/-- Warshall charges over `domain` from `es`, as Python and Rust materialize
each pivot: one unit per entity, then one per incoming × outgoing pair, whose
edges are added before the next pivot. `none` when the budget runs out. -/
def warshallWork (limit : Nat) (domain : List Entity) : List Entity → Edges → Nat → Option Nat
  | [], _, w => some w
  | pivot :: rest, es, w =>
    let w := w + domain.length
    if limit < w then none else
    let incoming := domain.filter (fun x => es.contains (x, pivot))
    let outgoing := domain.filter (fun y => es.contains (pivot, y))
    let w := w + incoming.length * outgoing.length
    if limit < w then none else
    warshallWork limit domain rest
      (incoming.foldl (fun es x => outgoing.foldl (fun es y => es.insert (x, y)) es) es) w

/-- A named edge relation: one unit per row, then Warshall over its endpoints in
Python `sorted` / Rust index order (one sort, so local-id order). -/
def namedWork (limit : Nat) (rows : List (List Entity)) (w : Nat) : Option Nat :=
  let w := w + rows.length
  if limit < w then none else
  let es : Edges := rows.foldl (fun es row => match row with
    | [a, b] => es.insert (a, b)
    | _ => es) {}
  let ends : Std.HashSet Entity := es.fold (fun s e => (s.insert e.1).insert e.2) {}
  let domain := ends.toList.mergeSort fun a b => decide (a.2 < b.2) || (a.2 == b.2 && decide (a.1 ≤ b.1))
  warshallWork limit domain domain es w

/-- The body of a body-edge closure at every (x, y) of its sort, x slowest,
with valuation `y :: x :: ρ`, collecting the true pairs. -/
def forPairs {σ : Type} (step : Entity → Entity → σ → Option (Bool × σ)) (domain : List Entity) :
    List Entity → Edges → σ → Option (Edges × σ)
  | [], es, s => some (es, s)
  | x :: xs, es, s => match row x domain es s with
    | none => none
    | some (es, s) => forPairs step domain xs es s
where
  row (x : Entity) : List Entity → Edges → σ → Option (Edges × σ)
    | [], es, s => some (es, s)
    | y :: ys, es, s => match step x y s with
      | none => none
      | some (b, s) => row x ys (if b then es.insert (x, y) else es) s

/-! ## Closure formulas -/

/-- A closure's cache key without its bindings: Python `f.edge`, Rust `Edge`. -/
inductive EdgeKey (F : Type) where
  | named (relation : String)
  | body (sort : String) (formula : F)
  deriving BEq, Hashable

abbrev CKey := EdgeKey VE.Closure.Formula

/-- The budgeted closure evaluator; closure values come from the reference
evaluator once the closure's construction has been charged. -/
def evalC (M : VE.FiniteModel Entity) (limit : Nat) :
    List Entity → VE.Closure.Formula → Meter CKey → Option (Bool × Meter CKey)
  | ρ, .not a, s => tickM limit s fun s => (evalC M limit ρ a s).map fun r => (!r.1, r.2)
  | ρ, .and a b, s => tickM limit s fun s => match evalC M limit ρ a s with
    | none => none
    | some (true, s) => evalC M limit ρ b s
    | some (false, s) => some (false, s)
  | ρ, .or a b, s => tickM limit s fun s => match evalC M limit ρ a s with
    | none => none
    | some (true, s) => some (true, s)
    | some (false, s) => evalC M limit ρ b s
  | ρ, .implies a b, s => tickM limit s fun s => match evalC M limit ρ a s with
    | none => none
    | some (true, s) => evalC M limit ρ b s
    | some (false, s) => some (true, s)
  | ρ, .all x a, s => tickM limit s fun s =>
    quantS true (fun v => evalC M limit (v :: ρ) a) (M.domains x) s
  | ρ, .ex x a, s => tickM limit s fun s =>
    quantS false (fun v => evalC M limit (v :: ρ) a) (M.domains x) s
  | ρ, .reachNamed k p t u, s => tickM limit s fun s =>
    let value := (VE.Closure.Formula.reachNamed k p t u).eval M ρ
    let key : CKey × List Entity := (.named p, ρ)
    if s.cache.contains key then some (value, s) else
    (namedWork limit (M.relations p) s.work).map fun w => (value, ⟨w, s.cache.insert key⟩)
  | ρ, .reachBody k x a t u, s => tickM limit s fun s =>
    let value := (VE.Closure.Formula.reachBody k x a t u).eval M ρ
    let key : CKey × List Entity := (.body x a, ρ)
    if s.cache.contains key then some (value, s) else
    match forPairs (fun v w => evalC M limit (w :: v :: ρ) a) (M.domains x) (M.domains x) {} s with
    | none => none
    | some (es, s) => (warshallWork limit (M.domains x) (M.domains x) es s.work).map
        fun w => (value, ⟨w, s.cache.insert key⟩)
  | ρ, f, s => tickM limit s fun s => some (f.eval M ρ, s)

theorem evalC_sound (M : VE.FiniteModel Entity) (limit : Nat) :
    ∀ (f : VE.Closure.Formula) (ρ : List Entity) (s : Meter CKey) (r : Bool × Meter CKey),
      evalC M limit ρ f s = some r → r.1 = f.eval M ρ := by
  intro f
  induction f with
  | top | bottom | unary | binary | eq =>
    intro ρ s r h
    have h := tickM_some h
    simp only [Option.some.injEq] at h
    subst h; rfl
  | reachNamed k p t u =>
    intro ρ s r h
    have h := tickM_some h
    simp only at h
    split at h
    · simp only [Option.some.injEq] at h; subst h; rfl
    · obtain ⟨w, _, hw⟩ := Option.map_eq_some_iff.mp h
      subst hw; rfl
  | reachBody k x a t u _ =>
    intro ρ s r h
    have h := tickM_some h
    simp only at h
    split at h
    · simp only [Option.some.injEq] at h; subst h; rfl
    · split at h
      · cases h
      · obtain ⟨w, _, hw⟩ := Option.map_eq_some_iff.mp h
        subst hw; rfl
  | not a ih =>
    intro ρ s r h
    have h := tickM_some h
    cases ha : evalC M limit ρ a { s with work := s.work + 1 } with
    | none => rw [ha] at h; cases h
    | some x =>
      rw [ha] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [VE.Closure.Formula.eval, ih ρ _ x ha]
  | and a b ia ib =>
    intro ρ s r h
    have h := tickM_some h
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [VE.Closure.Formula.eval, ← this, Bool.true_and]
      exact ib ρ _ _ h
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Closure.Formula.eval, ← this]
  | or a b ia ib =>
    intro ρ s r h
    have h := tickM_some h
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Closure.Formula.eval, ← this]
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [VE.Closure.Formula.eval, ← this, Bool.false_or]
      exact ib ρ _ _ h
  | implies a b ia ib =>
    intro ρ s r h
    have h := tickM_some h
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [VE.Closure.Formula.eval, ← this, Bool.not_true, Bool.false_or]
      exact ib ρ _ _ h
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Closure.Formula.eval, ← this]
  | all x a ih =>
    intro ρ s r h
    have h := tickM_some h
    have := quantS_sound true _ (fun v => a.eval M (v :: ρ)) (M.domains x)
      (fun v _ s r hv => ih _ s r hv) _ r h
    simpa [VE.Closure.Formula.eval] using this
  | ex x a ih =>
    intro ρ s r h
    have h := tickM_some h
    have := quantS_sound false _ (fun v => a.eval M (v :: ρ)) (M.domains x)
      (fun v _ s r hv => ih _ s r hv) _ r h
    simpa [VE.Closure.Formula.eval] using this

/-- Premises first under one budget, a fresh closure cache per formula (Python
witness checking, Rust `clear_closures`). -/
def refutesC (M : VE.FiniteModel Entity) (limit : Nat) :
    List VE.Closure.Formula → VE.Closure.Formula → Nat → Option Bool
  | [], c, w => (evalC M limit [] c ⟨w, {}⟩).map (fun r => !r.1)
  | p :: ps, c, w => match evalC M limit [] p ⟨w, {}⟩ with
    | none => none
    | some (false, _) => some false
    | some (true, s) => refutesC M limit ps c s.work

theorem refutesC_sound (M : VE.FiniteModel Entity) (limit : Nat) :
    ∀ (ps : List VE.Closure.Formula) (c : VE.Closure.Formula) (w : Nat) (b : Bool),
      refutesC M limit ps c w = some b → b = VE.Closure.countermodelCheck M ps c
  | [], c, w, b, h => by
    simp only [refutesC] at h
    cases hc : evalC M limit [] c ⟨w, {}⟩ with
    | none => rw [hc] at h; cases h
    | some x =>
      rw [hc] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [VE.Closure.countermodelCheck, evalC_sound M limit c [] _ x hc]
  | p :: ps, c, w, b, h => by
    simp only [refutesC] at h
    split at h
    · cases h
    · rename_i s' hp
      have := evalC_sound M limit p [] _ _ hp
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Closure.countermodelCheck, ← this]
    · rename_i s' hp
      have := evalC_sound M limit p [] _ _ hp
      rw [refutesC_sound M limit ps c _ b h]
      simp [VE.Closure.countermodelCheck, ← this]

def valuesC (M : VE.FiniteModel Entity) (fs : List VE.Closure.Formula) :
    Except String (List Bool) :=
  fs.mapM fun f => match evalC M maxEvaluations [] f ⟨0, {}⟩ with
    | some (b, _) => .ok b
    | none => .error budgetExhausted

theorem valuesC_sound (M : VE.FiniteModel Entity) (fs : List VE.Closure.Formula)
    (vs : List Bool) (h : valuesC M fs = .ok vs) : vs = fs.map (fun f => f.eval M []) := by
  induction fs generalizing vs with
  | nil => simp only [valuesC, List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h; simp [← h]
  | cons f fs ih =>
    simp only [valuesC, List.mapM_cons] at h ih
    cases hf : evalC M maxEvaluations [] f ⟨0, {}⟩ with
    | none => rw [hf] at h; cases h
    | some r =>
      obtain ⟨b, s⟩ := r
      rw [hf] at h
      cases hr : List.mapM (fun f => match evalC M maxEvaluations [] f ⟨0, {}⟩ with
          | some (b, _) => Except.ok b
          | none => Except.error budgetExhausted) fs with
      | error e => rw [hr] at h; cases h
      | ok bs =>
        rw [hr] at h
        simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
        subst h
        have hb := evalC_sound M _ f [] _ (b, s) hf
        simp only at hb
        rw [ih bs hr, hb]
        rfl

/-! ## Closure with n-ary atoms -/

abbrev NKey := EdgeKey VE.Core.Formula

/-- The same budgeted evaluator over `VE.Core.Formula` (n-ary atoms are leaves). -/
def evalN (M : VE.FiniteModel Entity) (limit : Nat) :
    List Entity → VE.Core.Formula → Meter NKey → Option (Bool × Meter NKey)
  | ρ, .not a, s => tickM limit s fun s => (evalN M limit ρ a s).map fun r => (!r.1, r.2)
  | ρ, .and a b, s => tickM limit s fun s => match evalN M limit ρ a s with
    | none => none
    | some (true, s) => evalN M limit ρ b s
    | some (false, s) => some (false, s)
  | ρ, .or a b, s => tickM limit s fun s => match evalN M limit ρ a s with
    | none => none
    | some (true, s) => some (true, s)
    | some (false, s) => evalN M limit ρ b s
  | ρ, .implies a b, s => tickM limit s fun s => match evalN M limit ρ a s with
    | none => none
    | some (true, s) => evalN M limit ρ b s
    | some (false, s) => some (true, s)
  | ρ, .all x a, s => tickM limit s fun s =>
    quantS true (fun v => evalN M limit (v :: ρ) a) (M.domains x) s
  | ρ, .ex x a, s => tickM limit s fun s =>
    quantS false (fun v => evalN M limit (v :: ρ) a) (M.domains x) s
  | ρ, .reachNamed k p t u, s => tickM limit s fun s =>
    let value := (VE.Core.Formula.reachNamed k p t u).eval M ρ
    let key : NKey × List Entity := (.named p, ρ)
    if s.cache.contains key then some (value, s) else
    (namedWork limit (M.relations p) s.work).map fun w => (value, ⟨w, s.cache.insert key⟩)
  | ρ, .reachBody k x a t u, s => tickM limit s fun s =>
    let value := (VE.Core.Formula.reachBody k x a t u).eval M ρ
    let key : NKey × List Entity := (.body x a, ρ)
    if s.cache.contains key then some (value, s) else
    match forPairs (fun v w => evalN M limit (w :: v :: ρ) a) (M.domains x) (M.domains x) {} s with
    | none => none
    | some (es, s) => (warshallWork limit (M.domains x) (M.domains x) es s.work).map
        fun w => (value, ⟨w, s.cache.insert key⟩)
  | ρ, f, s => tickM limit s fun s => some (f.eval M ρ, s)

theorem evalN_sound (M : VE.FiniteModel Entity) (limit : Nat) :
    ∀ (f : VE.Core.Formula) (ρ : List Entity) (s : Meter NKey) (r : Bool × Meter NKey),
      evalN M limit ρ f s = some r → r.1 = f.eval M ρ := by
  intro f
  induction f with
  | top | bottom | unary | binary | atom | eq =>
    intro ρ s r h
    have h := tickM_some h
    simp only [Option.some.injEq] at h
    subst h; rfl
  | reachNamed k p t u =>
    intro ρ s r h
    have h := tickM_some h
    simp only at h
    split at h
    · simp only [Option.some.injEq] at h; subst h; rfl
    · obtain ⟨w, _, hw⟩ := Option.map_eq_some_iff.mp h
      subst hw; rfl
  | reachBody k x a t u _ =>
    intro ρ s r h
    have h := tickM_some h
    simp only at h
    split at h
    · simp only [Option.some.injEq] at h; subst h; rfl
    · split at h
      · cases h
      · obtain ⟨w, _, hw⟩ := Option.map_eq_some_iff.mp h
        subst hw; rfl
  | not a ih =>
    intro ρ s r h
    have h := tickM_some h
    cases ha : evalN M limit ρ a { s with work := s.work + 1 } with
    | none => rw [ha] at h; cases h
    | some x =>
      rw [ha] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [VE.Core.Formula.eval, ih ρ _ x ha]
  | and a b ia ib =>
    intro ρ s r h
    have h := tickM_some h
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [VE.Core.Formula.eval, ← this, Bool.true_and]
      exact ib ρ _ _ h
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Core.Formula.eval, ← this]
  | or a b ia ib =>
    intro ρ s r h
    have h := tickM_some h
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Core.Formula.eval, ← this]
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [VE.Core.Formula.eval, ← this, Bool.false_or]
      exact ib ρ _ _ h
  | implies a b ia ib =>
    intro ρ s r h
    have h := tickM_some h
    simp only at h
    split at h
    · cases h
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [VE.Core.Formula.eval, ← this, Bool.not_true, Bool.false_or]
      exact ib ρ _ _ h
    · rename_i s' ha
      have := ia ρ _ _ ha
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Core.Formula.eval, ← this]
  | all x a ih =>
    intro ρ s r h
    have h := tickM_some h
    have := quantS_sound true _ (fun v => a.eval M (v :: ρ)) (M.domains x)
      (fun v _ s r hv => ih _ s r hv) _ r h
    simpa [VE.Core.Formula.eval] using this
  | ex x a ih =>
    intro ρ s r h
    have h := tickM_some h
    have := quantS_sound false _ (fun v => a.eval M (v :: ρ)) (M.domains x)
      (fun v _ s r hv => ih _ s r hv) _ r h
    simpa [VE.Core.Formula.eval] using this

def refutesN (M : VE.FiniteModel Entity) (limit : Nat) :
    List VE.Core.Formula → VE.Core.Formula → Nat → Option Bool
  | [], c, w => (evalN M limit [] c ⟨w, {}⟩).map (fun r => !r.1)
  | p :: ps, c, w => match evalN M limit [] p ⟨w, {}⟩ with
    | none => none
    | some (false, _) => some false
    | some (true, s) => refutesN M limit ps c s.work

theorem refutesN_sound (M : VE.FiniteModel Entity) (limit : Nat) :
    ∀ (ps : List VE.Core.Formula) (c : VE.Core.Formula) (w : Nat) (b : Bool),
      refutesN M limit ps c w = some b → b = VE.Core.countermodelCheck M ps c
  | [], c, w, b, h => by
    simp only [refutesN] at h
    cases hc : evalN M limit [] c ⟨w, {}⟩ with
    | none => rw [hc] at h; cases h
    | some x =>
      rw [hc] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [VE.Core.countermodelCheck, evalN_sound M limit c [] _ x hc]
  | p :: ps, c, w, b, h => by
    simp only [refutesN] at h
    split at h
    · cases h
    · rename_i s' hp
      have := evalN_sound M limit p [] _ _ hp
      simp only [Option.some.injEq] at h
      subst h
      simp [VE.Core.countermodelCheck, ← this]
    · rename_i s' hp
      have := evalN_sound M limit p [] _ _ hp
      rw [refutesN_sound M limit ps c _ b h]
      simp [VE.Core.countermodelCheck, ← this]

def valuesN (M : VE.FiniteModel Entity) (fs : List VE.Core.Formula) :
    Except String (List Bool) :=
  fs.mapM fun f => match evalN M maxEvaluations [] f ⟨0, {}⟩ with
    | some (b, _) => .ok b
    | none => .error budgetExhausted

theorem valuesN_sound (M : VE.FiniteModel Entity) (fs : List VE.Core.Formula)
    (vs : List Bool) (h : valuesN M fs = .ok vs) : vs = fs.map (fun f => f.eval M []) := by
  induction fs generalizing vs with
  | nil => simp only [valuesN, List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h; simp [← h]
  | cons f fs ih =>
    simp only [valuesN, List.mapM_cons] at h ih
    cases hf : evalN M maxEvaluations [] f ⟨0, {}⟩ with
    | none => rw [hf] at h; cases h
    | some r =>
      obtain ⟨b, s⟩ := r
      rw [hf] at h
      cases hr : List.mapM (fun f => match evalN M maxEvaluations [] f ⟨0, {}⟩ with
          | some (b, _) => Except.ok b
          | none => Except.error budgetExhausted) fs with
      | error e => rw [hr] at h; cases h
      | ok bs =>
        rw [hr] at h
        simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
        subst h
        have hb := evalN_sound M _ f [] _ (b, s) hf
        simp only at hb
        rw [ih bs hr, hb]
        rfl

end VE.Route.Budget
