import VE.NormDefaults.Wire
import VE.Norms.Run

/-! The `ve_norm_defaults_route` executable (docs/spec/norm-defaults.md 3, 6 and 8),
invoked as `lean/.lake/build/bin/ve_norm_defaults_route <cases.json|->`. The frozen
norms route is unchanged; this executable adds the `norm-defaults@0` branch and
delegates every other case to it.

* `norm-defaults-elaborate`: `norms` → the regenerated outputs of `fill U`
  (`Wire.regeneratedU`), or the decoder's diagnostic.
* `norm-defaults-conflict`: `norms` and `packages` (target of `fill U` → package)
  → `CONFLICT-FREE` when every target's certificate is bound and accepted over
  `E‴_base` and `Background_base(E‴) ++ Fill_T` (`Wire.normDefaults_wire_conflict_sound`),
  else `UNKNOWN` with the first failing target.
* `norm-defaults-certificate`: `norms`, `premises`, `conclusion`, `certificate` →
  `valid` over `Background(E‴) ++ Fill_T ++ layer premises of T‴ ++ premises`
  (`Wire.normDefaults_wire_acceptance`).
* A case with the profile or an `unspecified` default but another kind is
  `UnsupportedProfile`; every other case goes to `VE.Norms.Run.runCase`. -/
namespace VE.NormDefaults.Run
open Lean

/-- A norm-defaults construct: the profile, an `unspecified` default, or a
`norm-defaults-*` case kind. -/
def usesNormDefaultsPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "norm-defaults-"
    | _ => false
  Wire.hasProfile env || !(Wire.unspecifiedNames env).isEmpty || kind

/-- The first target of `fill U` without an accepted certificate. -/
def firstFailureU (r : Wire.ConflictReplayU) : Option String :=
  (((VE.Norms.targets (fill r.s.U)).zip r.certs).find? (fun (t, c) => match c with
    | some c => !VE.Tableau.checkCertificate (VE.Norms.envAt (fill r.s.U) 0) (Wire.baseBackgroundU r.s.U)
        (VE.Norms.targetConclusion t) c
    | none => true)).map (fun (t, c) =>
      if c.isSome then s!"invalid certificate for {t.1}" else s!"missing certificate for {t.1}")

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  let env := j.getObjValD "environment"
  if !Wire.hasProfile env && !(Wire.unspecifiedNames env).isEmpty then
    throw "UnsupportedProfile: unspecified completion requires norm-defaults@0"
  if kind == "norm-defaults-elaborate" then
    let s ← Wire.decodeSourceU (← j.getObjVal? "environment") (j.getObjValD "norms")
    return VE.Route.Wire.ok id (Wire.regeneratedU s.U)
  if kind == "norm-defaults-conflict" then
    let res ← Wire.replayConflictU j
    let verdict := if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN"
    return VE.Route.Wire.ok id ([("verdict", .str verdict),
      ("targets", toJson ((VE.Norms.targets (fill res.s.U)).map (·.1)))] ++
      match firstFailureU res with
      | some d => if res.conflictFree then [] else [("detail", .str d)]
      | none => [])
  if kind == "norm-defaults-certificate" then
    let r ← Wire.replayEntailmentU j
    return VE.Route.Wire.ok id [("valid", .bool r.valid),
      ("premises", toJson (Wire.premisesU r.s.U []).length)]
  if usesNormDefaultsPath j then
    throw s!"UnsupportedProfile: case kind {kind} is not available on the norm-defaults route"
  VE.Norms.Run.runCase j

def runCaseReported (j : Json) : Json :=
  if usesNormDefaultsPath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str message)]
  else VE.Norms.Run.runCaseReported j

end VE.NormDefaults.Run

open Lean in
def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_norm_defaults_route [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => VE.NormDefaults.Run.runCaseReported j
      | .error message => Json.mkObj [("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0
