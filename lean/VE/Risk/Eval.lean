import VE.Risk.Wire
import VE.Risk.Record
import VE.Risk.Derive

/-! The risk differential harness of docs/spec/risk.md 8.3 (`ve_service` mode `risk-eval`). It
is not part of the risk route and decides nothing a user sees: it exposes the trusted
condition functions on raw conditions over a given box, so tests can compare `possibleE`,
`certainE` and `witnessE` with brute-force enumeration and with Rust. Each case is
`{"environment", "quantities": [{"name", "tag", "lo", "hi"}], "conditions": [condition, …]}`
with grid coordinates; the environment is a risk environment (its units give the tags'
grids). Per condition the answer is the V7 diagnostic (`RiskUnestimated`,
`RiskConditionShared`, `RiskEqualityCoefficient`, or an elaboration error) or `possible`,
`certain` and the canonical witness. -/

namespace VE.Risk.Eval
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

/-- One case's row: `{"status": "ok", "results"}` or `{"status": "error", "error"}`. -/
def runCaseReported (j : Json) : Json :=
  match evalCase j with
  | .ok r => Json.mkObj [("status", .str "ok"), ("results", r)]
  | .error e => Json.mkObj [("status", .str "error"), ("error", .str e)]

end VE.Risk.Eval
