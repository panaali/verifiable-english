import VE.Risk.Eval

/-! `ve_risk_eval`: the one-shot form of the risk differential harness (`VE.Risk.Eval`,
docs/spec/risk.md 8.3), outside the default targets; callers use the `ve_service` mode
`risk-eval`. It reads the case array with Lean's own JSON parser. -/
open Lean

def main (_ : List String) : IO UInt32 := do
  let input ← (← IO.getStdin).readToEnd
  match Json.parse input with
  | .error e =>
    (← IO.getStderr).putStrLn e
    return 2
  | .ok (.arr cases) =>
    (← IO.getStdout).putStrLn (Json.arr (cases.map VE.Risk.Eval.runCaseReported)).compress
    return 0
  | .ok _ =>
    (← IO.getStderr).putStrLn "expected an array of cases"
    return 2
