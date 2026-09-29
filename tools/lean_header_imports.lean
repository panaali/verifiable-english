/-
Print, one JSON line per file argument, the modules the pinned toolchain's
own header parser (`Lean.Parser.parseHeader`) reads as imports, and whether it
reported an error. `tests/test_lean_import_reader.py` runs it with
`lean --run tools/lean_header_imports.lean FILE...` as the oracle for
`tools/check_lean_imports.imports`: every header that reader accepts must read
here, without error, as the same modules.
-/
import Lean

open Lean

def main (files : List String) : IO Unit := do
  for file in files do
    let input ← IO.FS.readFile file
    let (header, _, messages) ← Parser.parseHeader (Parser.mkInputContext input file)
    let error := messages.hasErrors
    -- With an error the header syntax may be incomplete, and a file whose
    -- header fails to parse never compiles, so its imports are not reported.
    let modules := if error then #[] else
      (Elab.headerToImports header (includeInit := false)).map (·.module.toString (escape := false))
    IO.println (Json.compress (Json.mkObj [("imports", toJson modules), ("error", toJson error)]))
