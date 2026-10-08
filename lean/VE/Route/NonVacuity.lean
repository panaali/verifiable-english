import VE.Route.Budget

/-! Python's conservative search-side non-vacuity condition, expressed once
for the four Lean formula families. Family adapters expose only tree shape. -/
namespace VE.Route.NonVacuity

inductive View (α : Type) where
  | leaf
  | unary (child : α)
  | binary (left right : α)
  | disjunction (left right : α)
  | implication (antecedent consequent : α)
  | universal (sort : String) (body : α)
  | existential (sort : String) (body : α)

abbrev Hits := List (List Nat × Bool)

def record (hits : Hits) (path : List Nat) (value : Bool) : Hits :=
  if hits.any (fun h => h.1 == path) then
    hits.map (fun h => if h.1 == path then (path, h.2 || value) else h)
  else (path, value) :: hits

def viewF : VE.Formula → View VE.Formula
  | .not a => .unary a
  | .and a b => .binary a b
  | .or a b => .disjunction a b
  | .implies a b => .implication a b
  | .all s a => .universal s a
  | .ex s a => .existential s a
  | _ => .leaf

def viewC : VE.Closure.Formula → View VE.Closure.Formula
  | .not a => .unary a
  | .and a b => .binary a b
  | .or a b => .disjunction a b
  | .implies a b => .implication a b
  | .all s a => .universal s a
  | .ex s a => .existential s a
  | _ => .leaf

def viewN : VE.Core.Formula → View VE.Core.Formula
  | .not a => .unary a
  | .and a b => .binary a b
  | .or a b => .disjunction a b
  | .implies a b => .implication a b
  | .all s a => .universal s a
  | .ex s a => .existential s a
  | _ => .leaf

def viewB : VE.Order.Formula → View VE.Order.Formula
  | .not a => .unary a
  | .and a b => .binary a b
  | .or a b => .disjunction a b
  | .implies a b => .implication a b
  | .all s a => .universal s a
  | .ex s a => .existential s a
  | _ => .leaf

/-- The shared traversal owns the condition and charging order. `eval` is the
family's already proved metered evaluator, so antecedent truth is never
reimplemented here. -/
structure Ops (α ρ σ entity : Type) where
  view : α → View α
  tick : σ → Option σ
  eval : α → ρ → σ → Option (Bool × σ)
  domain : String → List entity
  bind : String → entity → ρ → ρ

def guards {α ρ σ entity : Type} (ops : Ops α ρ σ entity) :
    Nat → α → σ → Option (List α × σ)
  | 0, _, _ => none
  | fuel + 1, node, state => do
    let state ← ops.tick state
    match ops.view node with
    | .disjunction a b =>
      let (left, state) ← guards ops fuel a state
      let (right, state) ← guards ops fuel b state
      pure (left ++ right, state)
    | .unary a => pure ([a], state)
    | _ => pure ([], state)

def hit {α ρ σ entity : Type} (ops : Ops α ρ σ entity)
    (guards : List α) (ρ₀ : ρ) (path : List Nat) (hits : Hits) (state : σ) :
    Option (Hits × σ) := do
  let mut state := state
  let mut value := true
  for guard in guards do
    if value then
      let (b, next) ← ops.eval guard ρ₀ state
      value := b
      state := next
  pure (record hits path value, state)

def walk {α ρ σ entity : Type} (ops : Ops α ρ σ entity) (semantic : Bool) :
    Nat → α → ρ → List Nat → Bool → Bool → Hits → σ → Option (Hits × σ × Bool)
  | 0, _, _, _, _, _, _, _ => none
  | fuel + 1, node, valuation, path, universal, inClause, hits, state => do
    let state ← ops.tick state
    match ops.view node with
    | .leaf => pure (hits, state, true)
    | .unary child =>
      walk ops semantic fuel child valuation (path ++ [0]) universal false hits state
    | .binary left right =>
      let (hits, state, a) ← walk ops semantic fuel left valuation (path ++ [0]) universal false hits state
      let (hits, state, b) ← walk ops semantic fuel right valuation (path ++ [1]) universal false hits state
      pure (hits, state, a && b)
    | .disjunction left right =>
      let (hits, state) ← if semantic && universal && !inClause then do
        let (gs, state) ← guards ops fuel node state
        if gs.isEmpty then pure (hits, state) else hit ops gs valuation path hits state
        else pure (hits, state)
      let (hits, state, a) ← walk ops semantic fuel left valuation (path ++ [0]) universal true hits state
      let (hits, state, b) ← walk ops semantic fuel right valuation (path ++ [1]) universal true hits state
      pure (hits, state, a && b)
    | .implication antecedent consequent =>
      let (hits, state) ← hit ops [antecedent] valuation path hits state
      let (hits, state, a) ← walk ops semantic fuel antecedent valuation (path ++ [0]) universal false hits state
      let (hits, state, b) ← walk ops semantic fuel consequent valuation (path ++ [1]) universal false hits state
      pure (hits, state, a && b)
    | .universal sort child =>
      let mut hits := hits
      let mut state := state
      let mut ok := !(ops.domain sort).isEmpty
      for entity in ops.domain sort do
        let (hs, next, valid) ← walk ops semantic fuel child (ops.bind sort entity valuation)
          (path ++ [0]) true false hits state
        hits := hs
        state := next
        ok := ok && valid
      pure (hits, state, ok)
    | .existential sort child =>
      let mut hits := hits
      let mut state := state
      let mut ok := !(ops.domain sort).isEmpty
      for entity in ops.domain sort do
        let (hs, next, valid) ← walk ops semantic fuel child (ops.bind sort entity valuation)
          (path ++ [0]) universal false hits state
        hits := hs
        state := next
        ok := ok && valid
      pure (hits, state, ok)

def check {α ρ σ entity : Type} (ops : Ops α ρ σ entity)
    (formula : α) (valuation : ρ) (state : σ) (semantic : Bool) : Option (Bool × σ) := do
  let (hits, state, ok) ← walk ops semantic 65 formula valuation [] false false [] state
  pure (ok && hits.all Prod.snd, state)

end VE.Route.NonVacuity
