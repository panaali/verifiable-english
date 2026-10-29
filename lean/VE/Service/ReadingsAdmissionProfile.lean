import VE.Service.Protocol

/-! Optional, diagnostic-only timings for the readings route. The service still answers
     through its ordinary pure runner; these probes do not feed an answer. -/
namespace VE.Service.ReadingsAdmissionProfile
open Lean VE.Readings VE.Readings.Wire VE.Readings.Run

def cpuTicks : IO Nat := do
  try
    let stat ← IO.FS.readFile "/proc/self/stat"
    let fields := (((stat.splitOn ") ").getLast?).getD "").splitOn " "
    return ((fields.getD 11 "0").toNat?).getD 0 + ((fields.getD 12 "0").toNat?).getD 0
  catch _ => return 0

def timed (caseId part stage : String) (work : Unit → Except String α) (size : α → Nat) : IO (Except String α) := do
  let start ← IO.monoNanosNow
  let cpuStart ← cpuTicks
  let result := work ()
  let (status, count, error) := match result with
    | .ok value => ("ok", size value, "")
    | .error e => ("error", 0, e)
  let stop ← IO.monoNanosNow
  let cpuStop ← cpuTicks
  (← IO.getStderr).putStrLn <| (Json.mkObj
    [("case", .str caseId), ("part", .str part), ("stage", .str stage),
     ("status", .str status), ("error", .str error), ("items", toJson count),
     ("nanos", toJson (stop - start)), ("cpu_ticks", toJson (cpuStop - cpuStart))]).compress
  return result

def profileND (caseId part : String) (b : Admitted2) : IO Bool := do
  let .ok f ← timed caseId part "admitNDFull" (fun _ => admitNDFull b)
    (fun f => f.r.N.D.sets.length) | return false
  let re := b.a.re
  let N : NDoc := ⟨b.D, unspecOf re b.D⟩
  let _ ← timed caseId part "ndTextWith"
    (fun _ => .ok (ndTextWith re N b.a.side)) (fun e => if e.isSome then 1 else 0)
  let re' := filledEnvironment re N
  let doc' : Decoded2 := ⟨(fillDoc N).items, b.a.doc.itemsJ, b.a.doc.units⟩
  let _ ← timed caseId part "filledAdmission" (fun _ => admitDecoded re' doc') (fun a => a.D.sets.length)
  let _ ← timed caseId part "choiceStepText"
    (fun _ => .ok (choiceStepText re N)) (fun e => if e.isSome then 1 else 0)
  for R in f.fa.a.D.sets.filter contentBearing do
    if let some RJ := setJ f.fa.a.doc R.id then
      let _ ← timed caseId R.id "distinguishingModels"
        (fun _ => setPairsWith (ndPairFacts f) f.fa.a R RJ) (·.length)
  return true

def profileS2 (caseId part : String) (environment document : Json) : IO (Option Admitted2) := do
  let .ok b ← timed caseId part "admitS2" (fun _ => admitS2 environment document)
    (fun b => b.D.sets.length) | return none
  return some b

/-- Replay the admission path of `admitComponent` or unsplit `runOne`.
    The returned S2 admission is used only for a verdict's later completion. -/
def profileComponent (caseId part kind : String) (split : Bool) (environment document : Json) :
    IO (Option (Option Admitted2)) := do
  if kind == "readings-validate" || kind == "readings-separate" then
    let .ok a ← timed caseId part "admitReadings" (fun _ => admitReadings environment document)
      (fun a => a.D.sets.length) | return none
    if underCompletion a.re a.D then
      let .ok b ← timed caseId part "admitS2Of" (fun _ => admitS2Of a document)
        (fun b => b.D.sets.length) | return none
      unless (← profileND caseId part b) do return none
    else if split then
      let .ok _ ← timed caseId part "splitAdmissible"
        (fun _ => splitAdmissible a.re a.D a) (fun _ => 0) | return none
    return some none
  let some b ← profileS2 caseId part environment document | return none
  if underCompletion b.a.re b.D then
    unless (← profileND caseId part b) do return none
  else if split then
    let .ok _ ← timed caseId part "splitAdmissible"
      (fun _ => splitAdmissible b.a.re b.D b) (fun _ => 0) | return none
  return some (some b)

/-- Replay the extra main admission of `admitChecked`, then its delegation. -/
def profileChecked (caseId part kind : String) (environment document : Json) :
    IO (Option (Option Admitted2)) := do
  if kind == "readings-elaborate" || kind == "readings-choice" then
    let some b ← profileS2 caseId part environment document | return none
    if b.a.re.lower.contains "norm-defaults@0" && b.a.re.chain == .norms && routeOf true b.D == .w2 then
      let some fixed ← profileS2 caseId part environment (fixedPart document) | return none
      unless (← profileND caseId part fixed) do return none
      return some (some fixed)
  profileComponent caseId part kind true environment document

/-- Replay `admitPart`, which stops at the first failed product component. -/
def profileProductPart (caseId part : String) (environment document : Json) : IO Bool := do
  let some b ← profileS2 caseId part environment document | return false
  let .ok _ := requireCompletion b | return false
  match routeOf true b.D with
  | .enumerated => profileND caseId part b
  | .w2 => do
      let some fixed ← profileS2 caseId part environment (fixedPart document) | return false
      profileND caseId part fixed
  | _ => return false

def profileAdmissions (caseId kind : String) (j : Json)
    (parts : List (String × Json × Json)) : IO Unit := do
  let .ok named := componentOfCase j | return
  if parts.length > 1 && kind == "readings-verdicts" && named.isNone then
    let .ok question := VE.Bridge.stringField j "question" | return
    unless verdictsQuestions.contains question do return
    for (part, env, doc) in parts do
      unless (← profileProductPart caseId part env doc) do return
    return
  if parts.length > 1 then
    let mut selected : Option Admitted2 := none
    for (part, env, doc) in parts do
      let result ← if part == "main" then profileChecked caseId part kind env doc
        else profileComponent caseId part kind true env doc
      let some b := result | return
      if part == named.getD "main" then selected := b
    if kind == "readings-verdicts" then
      if let some b := selected then
        if underCompletion b.a.re b.D then
          let .ok _ := verdictsRequest b j | return
          unless routeND (⟨b.D, unspecOf b.a.re b.D⟩ : NDoc) == .superposed &&
              (j.getObjVal? "budget").isOk do
            let _ ← profileND caseId (named.getD "main") b
    return
  let c := named.getD "main"
  if c != "main" then return
  let some (_, env, doc) := parts.head? | return
  let some b ← profileComponent caseId "main" kind false env doc | return
  if kind == "readings-verdicts" then
    if let some b := b then
      if underCompletion b.a.re b.D then
        let .ok _ := verdictsRequest b j | return
        unless routeND (⟨b.D, unspecOf b.a.re b.D⟩ : NDoc) == .superposed &&
            (j.getObjVal? "budget").isOk do
          let _ ← profileND caseId "main" b

def profileCase (j : Json) : IO Unit := do
  let .str caseId := j.getObjValD "id" | return
  let .ok environment := j.getObjVal? "environment" | return
  let .ok document := j.getObjVal? "document" | return
  let .ok kind := VE.Route.Run.caseKind j | return
  let .ok parts ← timed caseId "" "splitCase" (fun _ => splitCase environment document) (·.length) | return
  profileAdmissions caseId kind j parts
  let _ ← timed caseId "" "runCase" (fun _ => runCase j) (fun r => r.compress.length)

def profileLine (handles : VE.Service.Handles) (line : String) : IO Unit := do
  if (← IO.getEnv "VE_READINGS_STAGE_TIMES") != some "1" then return
  let .ok members := VE.Service.objectMembers line | return
  let .ok request := VE.Service.decodeRequest members | return
  unless request.mode == .readingsRoute do return
  let .ok registered := VE.Service.register handles request | return
  let .ok cases := VE.Service.decodeCases request | return
  let .ok expanded := VE.Service.expandCases registered request.mode cases | return
  for case in expanded do
    if let .ok j := case then profileCase j

end VE.Service.ReadingsAdmissionProfile
