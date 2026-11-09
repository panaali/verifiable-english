import VE.Readings.SoftSupWire
import VE.Readings.SoftSeparateExamples
open Lean VE.Readings VE.Readings.Wire
open VE.Readings.SoftSeparateExamples (frame4 mustX needNotX)
open VE.Readings.Examples (docK cand)
open VE.Rights.Examples (strictNode)
def envJ : Json := Json.mkObj [("language", "ve.core@0.2"), ("spec_revision", "ve-v0.2-expand2-2026-09-25"),
  ("profiles", toJson ["norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]),
  ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("agent", Json.mkObj [("description", "agent")])]),
    ("predicates", Json.mkObj []), ("constants", Json.mkObj [])])]
def wide : Nat → VE.Formula
  | 0 => .unary "c" (.var 0)
  | k + 1 => .and (wide k) (wide k)
def softSet (k : Nat) (g : VE.Formula := .top) : Item :=
  .set ⟨s!"rs{k}", s!"u{k + 1}", 1, [cand "strict" (strictNode s!"must-x-{k}" "x_required" true g),
    cand "default" { mustX with name := s!"must-x-{k}" }]⟩
def NSDbig (n : Nat) (g : VE.Formula := .top) : NDoc :=
  ⟨docK (.fixed "u0" (.norm needNotX) [] :: (List.range n).map (fun k => softSet k (if k == 0 then g else .top))) .soft frame4,
    ["y_permitted"]⟩
def main (args : List String) : IO Unit := do
  let n := (args.head?.bind String.toNat?).getD 10
  let .ok re := decodeEnvironment envJ | IO.println "env"
  let w := (args.tail.head?.bind String.toNat?)
  let N := match w with | some e => NSDbig n (wide e) | none => NSDbig n
  let t0 ← IO.monoNanosNow
  let r := routeSD re N
  IO.println s!"sets {n}: route {r.text}, work {sdCheckWork N}"
  let t1 ← IO.monoNanosNow
  IO.println s!"ms {(t1 - t0) / 1000000}"
