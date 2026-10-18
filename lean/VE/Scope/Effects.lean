import VE.Readings.Companions

/-! Scope's effects on a rule's JSON object (scope@0, docs/spec/scope.md 1.4, 1.5.2 and 4.2): conditions and
    `own`, the order table, and the join of a lead-in's part with an item's part. Scope decodes no rule field. -/

namespace VE.Scope
open Lean

def depthLimit : Nat := 64

inductive Effect
  | frame (part : Json)
  | reguard (c : Json)
  | carveOut (c : Json)
  | precedes
  | yields
  | title

def members (j : Json) : List (String × Json) := (VE.Bridge.fields j).toOption.getD []

/-- An object's members as lookup reads them: each listed key once, with the value `getObjVal?` finds. On a
    well-formed object this is `VE.Bridge.fields`; on any other value it keeps `mergeParts_keys` true. -/
def lookups (j : Json) : Except String (List (String × Json)) := do
  let fs ← VE.Bridge.fields j
  pure (VE.Readings.Wire.firstKeys (fs.filterMap fun kv => (j.getObjVal? kv.1).toOption.map (kv.1, ·)))

/-! Conditions and `own` -/

def hasOwn : Nat → Json → Bool
  | 0, _ => false
  | n + 1, j => match j with
    | .str s => s == "own"
    | .arr xs => xs.toList.any (hasOwn n)
    | .obj _ => (members j).any (fun kv => hasOwn n kv.2)
    | _ => false

def depthOk : Nat → Json → Bool
  | 0, _ => false
  | n + 1, j => match j with
    | .arr xs => xs.toList.all (depthOk n)
    | .obj _ => (members j).all (fun kv => depthOk n kv.2)
    | _ => true

/-- `own` occurs under no binder of the base guard grammar. -/
def ownSafe : Nat → Json → Bool
  | 0, _ => true
  | n + 1, j => match j with
    | .arr xs => match xs.toList with
      | [.str "forall", _, a] => !hasOwn n a
      | [.str "exists", _, a] => !hasOwn n a
      | ys => ys.all (ownSafe n)
    | .obj _ => (members j).all (fun kv => ownSafe n kv.2)
    | _ => true

/-- Every JSON string value `"own"` in `c`, at any depth, replaced by `g`. -/
def substOwn (g : Json) : Nat → Json → Json
  | 0, j => j
  | n + 1, j => match j with
    | .str s => if s == "own" then g else j
    | .arr xs => .arr (xs.map (substOwn g n))
    | .obj kvs => .obj (kvs.map fun _ v => substOwn g n v)
    | _ => j

def narrowing (c : Json) : Option Json := match c with
  | .arr #[.str "and", .str "own", C] => if hasOwn depthLimit C then none else some C
  | _ => none

def Commutes : Effect → Effect → Bool
  | .reguard c₁, .reguard c₂ => (narrowing c₁).isSome && (narrowing c₂).isSome
  | .reguard c, .carveOut d => (narrowing c).isSome && !hasOwn depthLimit d
  | .carveOut d, .reguard c => (narrowing c).isSome && !hasOwn depthLimit d
  | .carveOut d₁, .carveOut d₂ => !hasOwn depthLimit d₁ && !hasOwn depthLimit d₂
  | _, _ => false

/-! Joining parts -/

def mergeParts (u : String) (lead item : Json) : Except String Json := do
  let bad := s!"InvalidInput: scope@0 parts of {u} must be objects"
  let ls ← (lookups lead).mapError (fun _ => bad)
  let is ← (lookups item).mapError (fun _ => bad)
  match ls.find? (fun kv => is.any (·.1 == kv.1)) with
  | some (k, _) => throw s!"ScopeConflict: {u}: {k}"
  | none => pure (Json.mkObj (ls ++ is))

end VE.Scope
