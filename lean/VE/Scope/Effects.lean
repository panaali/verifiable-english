import VE.Readings.Companions

/-! Scope's effects on a rule's JSON object (scope@0, docs/spec/scope.md 1.5.2 and 4.2): the join of a lead-in's
    part with an item's part. Scope decodes no rule field. -/

namespace VE.Scope
open Lean

/-- An object's members as lookup reads them: each listed key once, with the value `getObjVal?` finds. On a
    well-formed object this is `VE.Bridge.fields`; on any other value it keeps `mergeParts_keys` true. -/
def lookups (j : Json) : Except String (List (String × Json)) := do
  let fs ← VE.Bridge.fields j
  pure (VE.Readings.Wire.firstKeys (fs.filterMap fun kv => (j.getObjVal? kv.1).toOption.map (kv.1, ·)))

/-! Joining parts -/

def mergeParts (u : String) (lead item : Json) : Except String Json := do
  let bad := s!"InvalidInput: scope@0 parts of {u} must be objects"
  let ls ← (lookups lead).mapError (fun _ => bad)
  let is ← (lookups item).mapError (fun _ => bad)
  match ls.find? (fun kv => is.any (·.1 == kv.1)) with
  | some (k, _) => throw s!"ScopeConflict: {u}: {k}"
  | none => pure (Json.mkObj (ls ++ is))

end VE.Scope
