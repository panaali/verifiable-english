import VE.Bridge
import VE.Closure.Bridge
import VE.CertificateWire
import VE.Order.Wire

open Lean

def main (args : List String) : IO UInt32 := do
  let (certificates, order, paths) := match args with
    | "check-certificate" :: rest => (true, false, rest)
    | "order" :: rest => (false, true, rest)
    | _ => (false, false, args)
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_conformance [check-certificate|order] [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j =>
        if order then VE.Order.Wire.runCaseReported j
        else if certificates then VE.CertificateWire.runCaseReported j
        else if (j.getObjValD "environment").getObjValD "language" == .str "ve.core@0.1"
        then VE.Closure.Bridge.runCaseReported j else VE.Bridge.runCaseReported j
      | .error message => Json.mkObj ([("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)] ++
          if certificates || order then [("valid", .bool false)] else [])
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0
