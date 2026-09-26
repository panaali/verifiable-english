import VE.Norms.Wire

/-! The `ve_norms_route` executable (docs/spec/norms.md 11.4), invoked as
`lean/.lake/build/bin/ve_norms_route <cases.json|->`. Each case is
`{"id", "environment", "kind", ...}`.

* `norms-elaborate`: `norms` (an array of norm objects, 3.2) → the regenerated
  layer order, Background (with generators), labelled layer premises
  (`layer:norms:<p>`), conflict targets (`p` and `r->m`, with argument sorts)
  and the fragment flag; or the shared diagnostic of `validate`.
* Any case without a norm construct (no `norms@0` profile, no `regulated`
  field, no `norms`) is delegated unchanged to P0 `Route.Run.runCase`. A norm
  input never falls back to P0 after a failed decode.

Admission of W2 documents with norm units and conflict-certificate packages
(11.4 steps 2-5) are not implemented yet and are rejected explicitly. -/
namespace VE.Norms.Run
open Lean

/-- The executable dispatch test for norm profiles and constructs. -/
def usesNormsPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let profiles := match env.getObjValD "profiles" with
    | .arr ps => ps.toList.any (· == .str "norms@0")
    | _ => false
  let regulated := match (env.getObjValD "vocabulary").getObjValD "predicates" with
    | .obj kvs => kvs.toList.any (fun (_, e) => (e.getObjVal? "regulated").toBool)
    | _ => false
  profiles || regulated || (j.getObjVal? "norms").toBool

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if kind == "norms-elaborate" then
    let environment ← j.getObjVal? "environment"
    let (_, ⟨D, _⟩) ← Wire.decodeSource environment (j.getObjValD "norms")
    return VE.Route.Wire.ok id (Wire.regenerated D)
  if usesNormsPath j then
    throw s!"UnsupportedProfile: case kind {kind} is not available on the norms route"
  VE.Route.Run.runCase j

def runCaseReported (j : Json) : Json :=
  if usesNormsPath j || j.getObjValD "kind" == .str "norms-elaborate" then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str message)]
  else VE.Route.Run.runCaseReported j

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_norms_route [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j
      | .error message => Json.mkObj [("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.Norms.Run
