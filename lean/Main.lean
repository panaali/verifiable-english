import VE.Bridge
import VE.Closure.Bridge
import VE.CertificateWire
import VE.Order.ProfileGate

open Lean

def main (args : List String) : IO UInt32 := do
  let (certificates, paths) := match args with
    | "check-certificate" :: rest => (true, rest)
    | _ => (false, args)
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_conformance [check-certificate] [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j =>
        if certificates then VE.CertificateWire.runCaseReported j
        else VE.Order.runEvaluationCaseReported j
      | .error message => Json.mkObj ([("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)] ++
          if certificates then [("valid", .bool false)] else [])
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0
