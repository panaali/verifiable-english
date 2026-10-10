import VE.Readings.ComponentsWire

/-! The computed fixtures of RD-4b (docs/spec/readings-defaults.md 8.4), each a `#guard`: 1.10's rule (`fixedDecided`,
`setDecided`) on the rows the spec lists, each direction, including SR4's case (CONFLICT under one choice and UNKNOWN
under the other is not decided, though the folded status is CONFLICT); and the wire's order of `decided_units`
(`documentOrder`: the document's own order, whichever component a unit is in). The service fixtures are in
`tests/test_readings_components_document.py`. -/
namespace VE.Readings.ComponentsExamples
open Lean
open VE.Readings VE.Readings.Run

def c0 : Choice := [("rs_1", 0)]
def c1 : Choice := [("rs_1", 1)]
def rows2 (a b : ChoiceResult) : List (Choice × ChoiceResult) := [(c0, a), (c1, b)]

/-! `fixedDecided`: true for (CONFLICT-FREE, `model`), false for (CONFLICT-FREE, UNKNOWN) and (UNKNOWN, `model`) -/
#guard fixedDecided .free .model
#guard !fixedDecided .free .unknown
#guard !fixedDecided .unknown .model
#guard fixedDecided .conflict .inconsistent

/-! `setDecided` (SR4) over two choices -/
#guard setDecided (rows2 .free .free) [.model, .dead, .narrowed, .inconsistent]
#guard setDecided (rows2 .conflict .free) [.model, .model]
#guard !setDecided (rows2 .free .free) [.model, .unknown]
#guard !setDecided (rows2 .free .unknown) [.model, .model]
-- SR4: a single folded status (CONFLICT) would hide the UNKNOWN under `c1`; read per choice it is not decided.
#guard foldConflict (rows2 .conflict .unknown) == .conflict
#guard !setDecided (rows2 .conflict .unknown) [.model, .model]

/-! `decided_units` in the document's order: a companion's sentence before the main one keeps its place -/
def docJ (ids : List String) : Json :=
  Json.mkObj [("units", Json.arr (ids.map (fun u => Json.mkObj [("id", .str u)])).toArray)]
#guard documentOrder (docJ ["u_a", "u0", "u_b"]) ["u0", "u_a", "u_b"] == ["u_a", "u0", "u_b"]
#guard documentOrder (docJ ["u0", "u_a", "u_b"]) ["u_b", "u0"] == ["u0", "u_b"]
#guard documentOrder (docJ ["u0", "u_a"]) [] == []

end VE.Readings.ComponentsExamples
