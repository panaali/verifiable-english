import VE.Bridge
import VE.CertificateWire

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
  match VE.JsonInput.parse input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok j =>
    let cases := match j with
      | .arr xs => xs
      | _ => #[j]
    let results := cases.map (if certificates then VE.CertificateWire.runCaseReported else VE.Bridge.runCaseReported)
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0
