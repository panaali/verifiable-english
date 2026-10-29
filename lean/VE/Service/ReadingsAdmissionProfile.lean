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

def profileCase (j : Json) : IO Unit := do
  let .str caseId := j.getObjValD "id" | return
  let .ok environment := j.getObjVal? "environment" | return
  let .ok document := j.getObjVal? "document" | return
  let .ok kind := VE.Route.Run.caseKind j | return
  let .ok parts ← timed caseId "" "splitCase" (fun _ => splitCase environment document) (·.length) | return
  let named := componentOfCase j
  for (part, env, doc) in parts do
    let .ok b ← timed caseId part "admitS2" (fun _ => admitS2 env doc) (fun b => b.D.sets.length) | continue
    -- The split's checked main case and W2 product cases admit the fixed units
    -- once more, then complete that admission even with no remaining sets.
    let w2 := b.a.re.lower.contains "norm-defaults@0" && b.a.re.chain == .norms && routeOf true b.D == .w2
    let checkedMain := parts.length > 1 && part == "main" &&
      (kind == "readings-elaborate" || kind == "readings-choice")
    let product := kind == "readings-verdicts" && parts.length > 1 &&
      (match named with | .ok none => true | _ => false)
    let fixed := w2 && (checkedMain || product)
    let admitted ← if fixed then
      timed caseId part "admitS2" (fun _ => admitS2 env (fixedPart doc)) (fun b => b.D.sets.length)
      else pure (.ok b)
    if fixed || underCompletion b.a.re b.D then
      if let .ok b' := admitted then
        if let .ok f ← timed caseId part "admitNDFull" (fun _ => admitNDFull b') (fun f => f.r.N.D.sets.length) then
          let re := b'.a.re
          let N : NDoc := ⟨b'.D, unspecOf re b'.D⟩
          let _ ← timed caseId part "ndTextWith"
            (fun _ => .ok (ndTextWith re N b'.a.side)) (fun e => if e.isSome then 1 else 0)
          let re' := filledEnvironment re N
          let doc' : Decoded2 := ⟨(fillDoc N).items, b'.a.doc.itemsJ, b'.a.doc.units⟩
          let _ ← timed caseId part "filledAdmission" (fun _ => admitDecoded re' doc') (fun a => a.D.sets.length)
          let _ ← timed caseId part "choiceStepText"
            (fun _ => .ok (choiceStepText re N)) (fun e => if e.isSome then 1 else 0)
          for R in f.fa.a.D.sets.filter contentBearing do
            if let some RJ := setJ f.fa.a.doc R.id then
              let _ ← timed caseId R.id "distinguishingModels"
                (fun _ => setPairsWith (ndPairFacts f) f.fa.a R RJ) (·.length)
    else
      for R in b.a.D.sets.filter contentBearing do
        if let some RJ := setJ b.a.doc R.id then
          let _ ← timed caseId R.id "distinguishingModels" (fun _ => setPairs b.a R RJ) (·.length)
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
