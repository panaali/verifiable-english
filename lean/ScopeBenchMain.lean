import VE.Service.Document

/-! B1's measurement of the scope layout and the run path (docs/spec/scope-PLAN.md, benchmark B1).

    lake build ve_scope_bench
    .lake/build/bin/ve_scope_bench <case.json> layout|govern

The case is the document mode's (`tools/bench/scope_b1.py` writes B1's). `layout` reads the case's scope block
(`VE.Scope.decodeScope`: the front matter and the layout of its units, 1.2); `govern` then runs the run path
`VE.Scope.governFast` on it. Each prints one JSON object: the layout's rows, the list run of the block's first
governor unit, and under `govern` the run path's answer (`ok` with the units whose content it changed, or its
refusal). Measurement only: no document check reads it, and it runs no chain. -/

open Lean (Json toJson)

namespace ScopeBench

def row (x : VE.Layout.Unit) : Json :=
  Json.mkObj [("id", x.id), ("span", toJson [x.span.1, x.span.2]), ("item", toJson x.item),
    ("midLine", toJson x.midLine), ("lead", toJson x.lead), ("label", toJson x.label), ("para", toJson x.para)]

/-- The units whose content the answer `out` changed from the document's. -/
def changed (D : VE.Scope.SDoc) (out : Json) : List String :=
  (VE.Scope.unitIds D.doc).filter fun u => VE.Scope.contentOf out u != VE.Scope.contentOf D.doc u

def report (D : VE.Scope.SDoc) (govern : Bool) : Json :=
  let lead := (D.governors.head?.map (·.unit)).getD ""
  let run : Json := match VE.Layout.listRun D.layout lead with
    | .ok us => toJson us
    | .error e => Json.mkObj [("error", e)]
  let answer : Json := if !govern then .null else match VE.Scope.governFast D with
    | .ok out => Json.mkObj [("ok", toJson (changed D out))]
    | .error e => Json.mkObj [("error", e)]
  Json.mkObj [("layout", .arr (D.layout.map row).toArray), ("lead", lead), ("run", run), ("governFast", answer)]

end ScopeBench

def main (args : List String) : IO UInt32 := do
  match args with
  | [path, stage] =>
    unless stage == "layout" || stage == "govern" do
      IO.eprintln s!"unknown stage {stage}: layout or govern"
      return 2
    match Json.parse (← IO.FS.readFile path) >>= VE.Scope.decodeScope with
    | .ok D =>
      IO.println (ScopeBench.report D (stage == "govern")).compress
      return 0
    | .error e =>
      IO.println (Json.mkObj [("error", e)]).compress
      return 1
  | _ =>
    IO.eprintln "usage: ve_scope_bench <case.json> layout|govern"
    return 2
