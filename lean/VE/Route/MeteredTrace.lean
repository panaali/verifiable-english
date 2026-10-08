import VE.Route.NonVacuity
import VE.Route.Metered

/-! Explanations are display data. Values and charging come only from the
proved budgeted evaluators; this traversal runs after a value is known. -/
namespace VE.Route.MeteredTrace
open Lean
open VE.Route

def bindingsJson (bindings : List (String × String)) : Json :=
  Json.arr ((bindings.zipIdx.map fun ((sort, name), index) => Json.mkObj
    [("debruijn_index", toJson index), ("sort", .str sort), ("local_id", .str name)]).toArray)

def node (kind : String) (value : Option Bool) (bindings : List (String × String))
    (detail : String) (children : List Json) : Json :=
  Json.mkObj [("kind", .str kind), ("value", value.map Json.bool |>.getD Json.null),
    ("bindings", bindingsJson bindings), ("detail", .str detail),
    ("children", Json.arr children.toArray)]

def tupleText (items : List String) : String :=
  "(" ++ String.intercalate ", " (items.map (fun x => "'" ++ x ++ "'")) ++
    (if items.length == 1 then "," else "") ++ ")"

structure Ops (α ρ entity : Type) where
  view : α → NonVacuity.View α
  eval : α → ρ → Bool
  domain : String → List entity
  bind : String → entity → ρ → ρ
  entityId : entity → String
  leafKind : α → String
  leafDetail : α → ρ → String

def render {α ρ entity : Type} (ops : Ops α ρ entity) :
    Nat → α → ρ → List (String × String) → Json
  | 0, _, _, bindings => node "resource_limit" none bindings "formula depth exhausted" []
  | fuel + 1, formula, valuation, bindings =>
    let value := ops.eval formula valuation
    match ops.view formula with
    | .leaf => node (ops.leafKind formula) (some value) bindings
        (ops.leafDetail formula valuation) []
    | .unary child =>
      node "not" (some value) bindings ""
        [render ops fuel child valuation bindings]
    | .binary left right =>
      let a := render ops fuel left valuation bindings
      if ops.eval left valuation then
        node "and" (some value) bindings ""
          [a, render ops fuel right valuation bindings]
      else node "and" (some value) bindings "right branch not needed" [a]
    | .disjunction left right =>
      let a := render ops fuel left valuation bindings
      if ops.eval left valuation then
        node "or" (some value) bindings "right branch not needed" [a]
      else node "or" (some value) bindings ""
        [a, render ops fuel right valuation bindings]
    | .implication antecedent consequent =>
      let a := render ops fuel antecedent valuation bindings
      if ops.eval antecedent valuation then
        node "implies" (some value) bindings ""
          [a, render ops fuel consequent valuation bindings]
      else node "implies" (some value) bindings
        "vacuously true: antecedent is false" [a]
    | .universal sort child =>
      let entities := ops.domain sort
      if entities.isEmpty then
        node "forall" (some true) bindings "vacuously true: domain is empty" []
      else
        let rec visitAll (remaining : List entity) (children : List Json) : List Json × String :=
          match remaining with
          | [] => (children, "all entities checked")
          | e :: es =>
            let childVal := ops.eval child (ops.bind sort e valuation)
            let trace := render ops fuel child (ops.bind sort e valuation)
              ((sort, ops.entityId e) :: bindings)
            let children := children ++ [trace]
            if childVal then visitAll es children else (children, s!"counterexample {ops.entityId e}")
        let (children, detail) := visitAll entities []
        node "forall" (some value) bindings detail children
    | .existential sort child =>
      let entities := ops.domain sort
      if entities.isEmpty then
        node "exists" (some false) bindings "false: domain is empty" []
      else
        let rec visitEx (remaining : List entity) (children : List Json) : List Json × String :=
          match remaining with
          | [] => (children, "no witness")
          | e :: es =>
            let childVal := ops.eval child (ops.bind sort e valuation)
            let trace := render ops fuel child (ops.bind sort e valuation)
              ((sort, ops.entityId e) :: bindings)
            let children := children ++ [trace]
            if childVal then (children, s!"witness {ops.entityId e}") else visitEx es children
        let (children, detail) := visitEx entities []
        node "exists" (some value) bindings detail children

def document {α ρ σ entity : Type} (ops : Ops α ρ entity)
    (step : α → σ → Option (Bool × σ)) (initial : σ) (valuation : ρ) (fs : List α)
    (result : Metered.Result) (maxEvaluations maxTraceNodes : Nat) : Json :=
  let rec collect (items : List α) (state : σ) (done : List Json) (index : Nat) : List Json × Nat :=
    match items with
    | [] => (done, index)
    | f :: rest =>
      match step f state with
      | none => (done, index)
      | some (b, state') =>
        let done := done ++ [render ops 65 f valuation []]
        if b then collect rest state' done (index + 1) else (done, index)
  let (children, index) := collect fs initial [] 0
  if result.status == "ResourceLimit" then
    node "resource_limit" none []
      (if maxTraceNodes < maxEvaluations then "trace-node budget exhausted"
       else "formula-node evaluation budget exhausted") children
  else if result.status == "Violated" then
    node "document" (some false) [] s!"statement {index + 1} violated" children
  else node "document" (some true) [] "all statements satisfied" children

abbrev Entity := VE.Bridge.Entity

def localF (M : VE.FiniteModel Entity) (ρ : List Entity) (t : VE.Term) : String :=
  (t.denote M.asStructure ρ).map Prod.snd |>.getD "?"

def kindF : VE.Formula → String
  | .top => "top"
  | .bottom => "bottom"
  | .unary .. => "unary"
  | .binary .. => "binary"
  | .eq .. => "equality"
  | _ => ""

def detailF (M : VE.FiniteModel Entity) (f : VE.Formula) (ρ : List Entity) : String :=
  match f with
  | .unary p t => p ++ tupleText [localF M ρ t]
  | .binary p t u => p ++ tupleText [localF M ρ t, localF M ρ u]
  | .eq t u => s!"{localF M ρ t} equals {localF M ρ u}"
  | _ => ""

def fol (M : VE.FiniteModel Entity) : Ops VE.Formula (List Entity) Entity where
  view := NonVacuity.viewF
  eval := fun f ρ => f.eval M ρ
  domain := M.domains
  bind := fun _ e ρ => e :: ρ
  entityId := Prod.snd
  leafKind := kindF
  leafDetail := fun f ρ => detailF M f ρ

def kindC : VE.Closure.Formula → String
  | .top => "top"
  | .bottom => "bottom"
  | .unary .. => "unary"
  | .binary .. => "binary"
  | .eq .. => "equality"
  | .reachNamed .. | .reachBody .. => "reach"
  | _ => ""

def reachKind : VE.Closure.Kind → String
  | .plus => "plus"
  | .star => "star"

def detailC (M : VE.FiniteModel Entity) (f : VE.Closure.Formula) (ρ : List Entity) : String :=
  match f with
  | .unary p t => p ++ tupleText [localF M ρ t]
  | .binary p t u => p ++ tupleText [localF M ρ t, localF M ρ u]
  | .eq t u => s!"{localF M ρ t} equals {localF M ρ u}"
  | .reachNamed k _ t u | .reachBody k _ _ t u =>
    s!"{reachKind k}: {localF M ρ t} to {localF M ρ u}; finite directed paths"
  | _ => ""

def closure (M : VE.FiniteModel Entity) : Ops VE.Closure.Formula (List Entity) Entity where
  view := NonVacuity.viewC
  eval := fun f ρ => f.eval M ρ
  domain := M.domains
  bind := fun _ e ρ => e :: ρ
  entityId := Prod.snd
  leafKind := kindC
  leafDetail := fun f ρ => detailC M f ρ

def kindN : VE.Core.Formula → String
  | .top => "top"
  | .bottom => "bottom"
  | .unary .. => "unary"
  | .binary .. => "binary"
  | .atom .. => "atom"
  | .eq .. => "equality"
  | .reachNamed .. | .reachBody .. => "reach"
  | _ => ""

def reachKindN : VE.Core.Kind → String
  | .plus => "plus"
  | .star => "star"

def detailN (M : VE.FiniteModel Entity) (f : VE.Core.Formula) (ρ : List Entity) : String :=
  match f with
  | .unary p t => p ++ tupleText [localF M ρ t]
  | .binary p t u => p ++ tupleText [localF M ρ t, localF M ρ u]
  | .atom p ts => p ++ tupleText (ts.map (localF M ρ))
  | .eq t u => s!"{localF M ρ t} equals {localF M ρ u}"
  | .reachNamed k _ t u | .reachBody k _ _ t u =>
    s!"{reachKindN k}: {localF M ρ t} to {localF M ρ u}; finite directed paths"
  | _ => ""

def core (M : VE.FiniteModel Entity) : Ops VE.Core.Formula (List Entity) Entity where
  view := NonVacuity.viewN
  eval := fun f ρ => f.eval M ρ
  domain := M.domains
  bind := fun _ e ρ => e :: ρ
  entityId := Prod.snd
  leafKind := kindN
  leafDetail := fun f ρ => detailN M f ρ

def orderValue : VE.Order.Value Entity → String
  | .inl e => e.2
  | .inr n => toString n

def localB (M : VE.Order.FiniteModel Entity) (ρ : List (VE.Order.Value Entity))
    (t : VE.Order.Term) : String :=
  (t.denote M.asStructure ρ).map orderValue |>.getD "?"

def kindB : VE.Order.Formula → String
  | .top => "top"
  | .bottom => "bottom"
  | .unary .. => "unary"
  | .binary .. => "binary"
  | .eq .. => "equality"
  | .lt .. | .le .. => "comparison"
  | _ => ""

def detailB (M : VE.Order.FiniteModel Entity) (f : VE.Order.Formula)
    (ρ : List (VE.Order.Value Entity)) : String :=
  match f with
  | .unary p t => p ++ tupleText [localB M ρ t]
  | .binary p t u => p ++ tupleText [localB M ρ t, localB M ρ u]
  | .eq t u => s!"{localB M ρ t} equals {localB M ρ u}"
  | .lt t u => s!"{localB M ρ t} < {localB M ρ u}"
  | .le t u => s!"{localB M ρ t} <= {localB M ρ u}"
  | _ => ""

def order (M : VE.Order.FiniteModel Entity) :
    Ops VE.Order.Formula (List (VE.Order.Value Entity)) Entity where
  view := NonVacuity.viewB
  eval := fun f ρ => f.eval M ρ
  domain := M.domains
  bind := fun _ e ρ => .inl e :: ρ
  entityId := Prod.snd
  leafKind := kindB
  leafDetail := fun f ρ => detailB M f ρ

end VE.Route.MeteredTrace
