import VE.Risk.Run

/-! `ve_risk_eval`: the differential harness of docs/spec/risk.md 8.3. It is not
part of `ve_risk_route` and decides nothing a user sees: it exposes the trusted
condition functions on raw conditions over a given box, so tests can compare
`possibleE`, `certainE` and `witnessE` with brute-force enumeration and with
Rust. Each case is `{"environment", "quantities": [{"name", "tag", "lo", "hi"}],
"conditions": [condition, …]}` with grid coordinates; the environment is a risk
environment (its units give the tags' grids). Per condition the answer is the
V7 diagnostic (`RiskUnestimated`, `RiskConditionShared`, `RiskEqualityCoefficient`,
or an elaboration error) or `possible`, `certain` and the canonical witness. -/
open Lean VE.Risk

def evalCondition (R : RiskDoc) (qs : List Quantity) (b : Box) (j : Json) : Json :=
  match elabCond R qs 64 j with
  | .error (_, e) => Json.mkObj [("error", .str e)]
  | .ok c =>
    if !Scoped b c then
      Json.mkObj [("error", .str s!"RiskUnestimated: {(c.atomNames.find? (!b.mem ·)).getD ""}")]
    else match sharedName b c, unitBad b c with
      | some q, _ => Json.mkObj [("error", .str s!"RiskConditionShared: {q}")]
      | none, some q => Json.mkObj [("error", .str s!"RiskEqualityCoefficient: {q}")]
      | none, none =>
        Json.mkObj [("possible", .bool (possibleE b c)), ("certain", .bool (certainE b c)),
          ("witness", match witnessE b c with
            | some v => Json.mkObj (b.entries.map fun e => (e.name, toJson (v e.name)))
            | none => .null)]

def evalCase (j : Json) : Except String Json := do
  let src ← VE.Risk.Wire.decodeRiskSource (j.getObjValD "environment") (Json.mkObj [("norms", Json.arr #[])])
  let rows ← match j.getObjValD "quantities" with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: quantities"
  let entries ← rows.mapM fun x => do
    let name ← x.getObjValAs? String "name"
    let tag ← x.getObjValAs? String "tag"
    let lo ← x.getObjValAs? Int "lo"
    let hi ← x.getObjValAs? Int "hi"
    pure (⟨name, tag, lo, hi⟩ : BoxEntry)
  let b : Box := ⟨entries⟩
  let qs : List Quantity := entries.map fun e => ⟨e.name, e.name, e.tag, none⟩
  let conds ← match j.getObjValD "conditions" with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: conditions"
  pure (Json.arr (conds.map (evalCondition src.R qs b)).toArray)

def main (_ : List String) : IO UInt32 := do
  let input ← (← IO.getStdin).readToEnd
  match Json.parse input with
  | .error e =>
    (← IO.getStderr).putStrLn e
    return 2
  | .ok (.arr cases) =>
    let out := cases.map fun c => match evalCase c with
      | .ok r => Json.mkObj [("status", .str "ok"), ("results", r)]
      | .error e => Json.mkObj [("status", .str "error"), ("error", .str e)]
    (← IO.getStdout).putStrLn (Json.arr out).compress
    return 0
  | .ok _ =>
    (← IO.getStderr).putStrLn "expected an array of cases"
    return 2
