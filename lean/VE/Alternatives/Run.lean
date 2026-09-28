import VE.Alternatives.Replay
import VE.Norms.Run

/-! The `ve_alternatives_route` executable (docs/spec/alternatives.md 7.3), invoked as
`lean/.lake/build/bin/ve_alternatives_route <cases.json|->`. Each case is
`{"id", "kind", "environment", "norms", "units"?, ...}` with the `alternatives` block in the
environment and `alternatives@0`, `norms@0` among its profiles.

* `alt-elaborate` → the inlined norm objects, the slot premises (`alternatives:*`), the base
  units (with `alternatives:table_complete` under `complete_by`), the followability formulas
  (`∀r. followable°(r)`, `followable°`, `clear°`), the unmapped obligations, and W1's
  regenerated order, Background, layer premises, conflict targets and fragment flag.
* `alt-validate` with `scenario` (`model`, signed `outcomes` rows) → `InvalidModel(alternatives)`
  or, first, a CONFLICT witness if a regenerated conflict formula holds on the model
  (`scenarioConflict_sound`), else the per-chooser scenario report bound to `model_id`.
* `alt-conflict` with `packages` → CONFLICT-FREE (`alternatives_wire_conflict_sound`) or UNKNOWN;
  with `witness` (`model`, `outcomes`, `target`, `tuple`) → CONFLICT (`alt_conflict_witness_sound`)
  or UNKNOWN.
* `alt-followable` with `packages` and `package` → FOLLOWABLE (`alternatives_wire_followable_sound`);
  with `packages` and `witness` (`model`, `outcomes`, `chooser`) → DILEMMA
  (`alternatives_wire_dilemma_sound`) with the untrusted diagnosis; UNKNOWN otherwise; `not
  computed: conflict status UNKNOWN` without CONFLICT-FREE packages for the same source.
* `alt-certificate` → `valid` (`alternatives_wire_acceptance`).
* Any case without the profile, the block or an `alt-*` kind is delegated unchanged to
  `VE.Norms.Run`. W2 `admission` with the block is not implemented and is rejected. -/
namespace VE.Alternatives.Run
open Lean
open VE.Norms
open Replay

def usesAltPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let profile := match env.getObjValD "profiles" with
    | .arr ps => ps.toList.contains (.str "alternatives@0")
    | _ => false
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "alt-"
    | _ => false
  profile || (env.getObjVal? "alternatives").toBool || kind

def ok (id : String) (fields : List (String × Json)) : Json := VE.Route.Wire.ok id fields

def ids (xs : List VE.Bridge.Entity) : Json := toJson (xs.map (·.2))
def joined (xs : List VE.Bridge.Entity) : String := ", ".intercalate (xs.map (·.2))

def notComputed : String := "not computed: conflict status UNKNOWN"

/-! ## Rendering (untrusted) -/

def dutyText (r : VE.Bridge.Entity) (d : String × List VE.Bridge.Entity) : String :=
  s!"{d.1}({", ".intercalate ((r :: d.2).map (·.2))})"

def diagnosisText (r : VE.Bridge.Entity) : Diagnosis VE.Bridge.Entity → String
  | .noAlternatives => "no alternatives"
  | .nonePermitted => "NONE-PERMITTED: every available action is forbidden"
  | .overRequired req => s!"OVER-REQUIRED({joined req}): {joined req} are all required"
  | .undischargeable d => s!"UNDISCHARGEABLE({dutyText r d}): {dutyText r d} is required here and no permitted available action discharges it"
  | .jointlyUndischargeable ds =>
    let t := ", ".intercalate (ds.map (dutyText r))
    s!"JOINTLY-UNDISCHARGEABLE({t}): each of {t} is discharged by some permitted available action, but no single action discharges all of them"
  | .clear as => s!"clear: {joined as}"

/-- An act phrase without its slots (`{0} prevent {1}` → `prevent`). -/
def actWords (act : String) : String :=
  " ".intercalate ((act.splitOn " ").filter (fun w => !(w.startsWith "{" && w.endsWith "}")))

def unmappedText (A : AltDoc) : String :=
  match Wire.unmappedObligations A with
  | [] => "none"
  | rs => ", ".intercalate (rs.map (fun r => s!"{r.name} ({actWords (r.act.getD "")})"))

def modelId (src : Wire.AltSource) (environment : Json) (sc : Scenario src) : String :=
  match environmentId src.profiles environment with
  | .ok envId => (VE.CertificateWire.digest s!"ve-model-{VE.Route.Wire.identityVersion src.profiles}\n"
      (Json.mkObj [("environment_id", .str envId), ("model", sc.json),
        ("outcomes", toJson (sc.rows.map (fun r => [r.action, r.harm, toString r.leadsTo])))])).toOption.getD ""
  | .error _ => ""

/-- 4.7: the per-chooser evaluation of a validated scenario on which no conflict formula holds. -/
def chooserReport (A : AltDoc) (M : VE.FiniteModel VE.Bridge.Entity) (r : VE.Bridge.Entity) : Json × String :=
  let alts := availOf M A.alt.available r
  let harms := M.domains A.alt.harm
  let perm := alts.filter (permittedAt A M)
  let req := alts.filter (requiredAt A M)
  let clear := alts.filter (fun a => (clearF A).eval M (tupleVal [r, a]))
  let marked (p : Option String) := match p with
    | some p => alts.filter (fun a => (M.relations p).contains [a])
    | none => []
  let taken := marked A.alt.taken
  let pairs (F : VE.Formula) := alts.flatMap (fun a => (harms.filter (fun h => F.eval M (tupleVal [a, h]))).map
    (fun h => toJson [a.2, h.2]))
  let text := if alts.isEmpty then s!"no alternatives at {r.2}"
    else if clear.isEmpty then s!"no clear action at {r.2}: {diagnosisText r (diagnose A M r)}"
    else s!"{r.2} has a clear action: {joined clear}"
  let fields := [("chooser", .str r.2), ("alternatives", ids alts), ("inaction", ids (marked A.alt.inaction)),
    ("permitted", ids perm), ("required", ids req),
    ("avoidable", ids (harms.filter (fun h => (avoidableF A.alt).eval M (tupleVal [h, r])))),
    ("unavoidable", ids (harms.filter (fun h => (unavoidableF A.alt).eval M (tupleVal [h, r])))),
    ("allows", Json.arr (pairs (allowsF A.alt)).toArray), ("prevents", Json.arr (pairs (preventsF A.alt)).toArray),
    ("clear", ids clear), ("text", .str text)] ++
    (if A.alt.taken.isSome then
      [("violations", ids (alts.filter (fun a => requiredAt A M a && !taken.contains a))),
       ("breaches", ids (alts.filter (fun a => !permittedAt A M a && taken.contains a)))] else [])
  (Json.mkObj fields, text)

/-- Missing rows under `complete_by`, read as negative (1.4). -/
def assumedHarmFree (A : AltDoc) (M : VE.FiniteModel VE.Bridge.Entity) (rows : List Row) : List String :=
  match A.alt.outcomes with
  | .signed => []
  | .completeBy d => (M.relations A.alt.available).flatMap fun t => match t with
    | [a, _] => (M.domains A.alt.harm).filterMap fun h =>
        if rows.any (fun row => rowDenotes M row a h) then none else some s!"{a.2}/{h.2} ({d})"
    | _ => []

/-! ## Cases -/

def conflictStatus (src : Wire.AltSource) (j : Json) : Bool :=
  altConflictFreeCheck src.A (conflictCerts src (j.getObjValD "environment") (j.getObjValD "norms")
    (j.getObjValD "units") (j.getObjValD "packages"))

def runValidate (id : String) (j : Json) : Except String Json := do
  let src ← sourceOf j
  let environment ← j.getObjVal? "environment"
  let sc ← decodeScenario src (← j.getObjVal? "scenario")
  match validateAlternativesWith src.labels src.A sc.M sc.rows with
  | .error e => throw e
  | .ok () => pure ()
  let mid := modelId src environment sc
  match scenarioConflict src.A sc.M with
  | some (t, vs) =>
    return ok id [("verdict", .str "CONFLICT"), ("target", .str t.1), ("tuple", ids vs), ("model_id", .str mid),
      ("text", .str s!"scenario (model {mid}): CONFLICT at ({joined vs}) on {t.1}; no per-chooser evaluation")]
  | none =>
    let reports := (sc.M.domains src.A.alt.chooser).map (chooserReport src.A sc.M)
    let document := if (j.getObjVal? "packages").toBool then
        (if conflictStatus src j then "also a dilemma witness for the document (conflict status CONFLICT-FREE)"
          else "document followability not computed: conflict status UNKNOWN")
      else "document followability not computed: conflict status UNKNOWN"
    let failing := reports.any (fun (_, t) => t.startsWith "no clear action")
    return ok id [("model_id", .str mid), ("choosers", Json.arr (reports.map Prod.fst).toArray),
      ("assumed_harm_free", toJson (assumedHarmFree src.A sc.M sc.rows)),
      ("unmapped_obligations", .str (unmappedText src.A)),
      ("conditional_on", toJson (if src.A.alt.outcomes == .signed then [] else ["alternatives:table_complete"])),
      ("text", .str (s!"scenario (model {mid}): " ++ "; ".intercalate (reports.map Prod.snd) ++
        s!"; unmapped obligations: {unmappedText src.A}" ++ (if failing then s!"; {document}" else "")))]

def runConflictWitness (id : String) (j : Json) : Except String Json := do
  let src ← sourceOf j
  let w ← j.getObjVal? "witness"
  let sc ← decodeScenario src w
  let name ← VE.Bridge.stringField w "target"
  unless backgroundValidAlt src.A sc.M do throw (VE.Route.Wire.invalidModel "alternatives")
  let some t := (targets (inlineTree src.A)).find? (·.1 == name) | throw s!"InvalidInput: unknown conflict target {name}"
  let tuple ← (← VE.Bridge.strings (← w.getObjVal? "tuple")).zip t.2.1 |>.mapM (fun (x, s) => entity sc.M s x)
  unless tuple.length == t.2.1.length do throw "InvalidInput: witness tuple has the wrong length or sort"
  let conflict := t.2.2.eval sc.M (tupleVal tuple)
  return ok id [("verdict", .str (if conflict then "CONFLICT" else "UNKNOWN")), ("target", .str t.1)]

def runConflict (id : String) (j : Json) : Except String Json := do
  if (j.getObjVal? "witness").toBool then return ← runConflictWitness id j
  let res ← replayAltConflict j
  let verdict := if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN"
  return ok id ([("verdict", .str verdict), ("targets", toJson ((targets (inlineTree res.src.A)).map (·.1)))] ++
    match firstFailure res with
    | some d => if res.conflictFree then [] else [("detail", .str d)]
    | none => [])

def followableText (src : Wire.AltSource) (certId : String) : String :=
  let mapped := ", ".intercalate (src.A.alt.fulfilments.map (fun f =>
    actWords (((findReg src.A.T f.obligation).bind (·.act)).getD f.obligation)))
  let conditional := match src.labels with
    | [] => "nothing"
    | ls => ", ".intercalate ls
  let existence := if src.A.alt.inaction.isSome then "E1, E2" else "E1"
  let existence := if src.A.alt.outcomes == .signed then existence ++ ", E3" else existence
  s!"FOLLOWABLE: at every choice some available action is permitted, forgoes no required alternative and " ++
  s!"discharges the mapped obligations ({mapped}); unmapped obligations: {unmappedText src.A}; conditional on " ++
  s!"{conditional}; certificate {certId}. Certified over every structure satisfying the slot premises; " ++
  s!"existence facts ({existence}) are validated on situations and not assumed."

def runFollowable (id : String) (j : Json) : Except String Json := do
  if (j.getObjVal? "witness").toBool then
    let ⟨src, w⟩ ← replayDilemma j
    unless altConflictFreeCheck src.A w.certs do
      return ok id [("verdict", .str "not computed"), ("text", .str notComputed)]
    match validateAlternativesWith src.labels src.A w.M w.rows with
    | .error e => throw e
    | .ok () => pure ()
    if scenarioConflict src.A w.M |>.isSome then
      throw "InvalidInput: the witness is a CONFLICT witness, not a dilemma"
    if w.dilemma then
      let d := diagnosisText w.r (diagnose src.A w.M w.r)
      return ok id [("verdict", .str "DILEMMA"), ("chooser", .str w.r.2), ("diagnosis", .str d),
        ("text", .str s!"DILEMMA at {w.r.2}: no available action complies with the mapped obligations and the declared action constraints here; {d}. This is a situation the rules do not cover, not a verdict that they are wrong.")]
    return ok id [("verdict", .str "UNKNOWN"), ("text", .str "UNKNOWN: the witness chooser has a clear action")]
  let res ← replayFollowable j
  unless res.conflictFree do
    return ok id [("verdict", .str "not computed"), ("text", .str notComputed)]
  if res.followable then
    let certId := (VE.CertificateWire.digest "ve-alternatives-certificate\n"
      ((j.getObjValD "package").getObjValD "certificate")).toOption.getD ""
    return ok id [("verdict", .str "FOLLOWABLE"), ("conditional_on", toJson res.src.labels),
      ("text", .str (followableText res.src certId))]
  return ok id [("verdict", .str "UNKNOWN"),
    ("text", .str "UNKNOWN: no accepted followability certificate for this source")]

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if kind == "alt-elaborate" then
    let src ← sourceOf j
    return ok id (Wire.regenerated src)
  if kind == "alt-validate" then return ← runValidate id j
  if kind == "alt-conflict" then return ← runConflict id j
  if kind == "alt-followable" then return ← runFollowable id j
  if kind == "alt-certificate" then
    let r ← replayAltEntailment j
    return ok id [("valid", .bool r.valid), ("background", toJson (backgroundAlt r.src.A).length),
      ("layers", toJson (elaborate (inlineTree r.src.A).T).length),
      ("conditional_on", toJson (altPremiseLabels r.src.A))]
  throw s!"UnsupportedProfile: case kind {kind} is not available on the alternatives route"

def runCaseReported (j : Json) : Json :=
  if usesAltPath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]
  else VE.Norms.Run.runCaseReported j

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_alternatives_route [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j
      | .error message => Json.mkObj [("status", .str "error"), ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.Alternatives.Run
