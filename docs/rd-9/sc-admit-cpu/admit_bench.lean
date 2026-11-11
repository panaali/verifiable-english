/- sc-admit-cpu's CPU bench (docs/rd-9/sc-admit-cpu/cpu.md): the `main` of a throwaway Lake package that requires this
worktree's `lean/` (`[[require]] name = "veReference"`, `path = "<worktree>/lean"`; `[[lean_exe]] name = "bench"`,
`root = "Bench"`), built by `lake build bench` and run as `/usr/bin/time -f %U ./.lake/build/bin/bench <mode> <file>`,
one mode per process, on a request `admit_docs.py` wrote (`{"case", "environment", "document"}`).

Modes (each also reads and parses the file; `parse` is that floor alone):
- `admit`: `admitSD environment document`, the whole admission of a soft-chain document (SoftWire.lean `admitSD`).
- `s2`: `admitS2` alone, S1's and S2a's admission; `admit` minus `s2` is `admitSDOf`'s own cost.
- `sup`: `admitS2`, then `sup D` built (what `readings-dead` reads through `deadCheck`/`unsatCheck`).
- `check`: not timed. The admitted document's items, chain, couplings, narrowings and unspecified predicates against the
  Lean `NDoc` the case restates (docs/rd-9/sc-11w/cpu_bench.lean's, restated here), with its choices and
  `sdSizeCharge`. -/
import VE.Readings.SoftSupWire
import VE.Readings.SoftSeparateExamples
import VE.Readings.SoftWireExamples
open Lean VE.Readings VE.Readings.Wire
open VE.Readings.SoftSeparateExamples (frame4 mustX needNotX)
open VE.Readings.Examples (docK cand)
open VE.Rights.Examples (strictNode)

def wide : Nat → VE.Formula
  | 0 => .unary "c" (.var 0)
  | k + 1 => .and (wide k) (wide k)
def softSet (k : Nat) (g : VE.Formula := .top) : Item :=
  .set ⟨s!"rs{k}", s!"u{k + 1}", 1, [cand "strict" (strictNode s!"must-x-{k}" "x_required" true g),
    cand "default" { mustX with name := s!"must-x-{k}" }]⟩
def NSDbig (n : Nat) (g : VE.Formula := .top) : NDoc :=
  ⟨docK (.fixed "u0" (.norm needNotX) [] :: (List.range n).map (fun k => softSet k (if k == 0 then g else .top)))
    .soft frame4, ["y_permitted"]⟩
def withRules (n m : Nat) (g : Nat → VE.Formula) : NDoc := ⟨{ (NSDbig n).D with items := ((NSDbig n).D.items ++
  (List.range m).map (fun i => .fixed s!"g{i}" (.norm (strictNode s!"guarded-{i}"
    (["x_required", "x_permitted", "y_permitted"][i % 3]!) true (g i))) [])) }, ["y_permitted"]⟩

def expected : String → Option NDoc
  | "NSDbig6" => some (NSDbig 6)
  | "wideGuard767" => some (NSDbig 8 (wide 8))
  | "wideGuard3071" => some (NSDbig 6 (wide 10))
  | "wideGuard191" => some (NSDbig 8 (wide 6))
  | "NSDbig8" => some (NSDbig 8)
  | "NSDheavy" => some (withRules 6 10 fun _ => wide 4)
  | "heavyIn" => some (withRules 6 9 fun _ => wide 4)
  | "atLimit" => some VE.Readings.SoftWireExamples.atLimit
  | "overLimit" => some VE.Readings.SoftWireExamples.overLimit
  | c => if c.startsWith "rules" then (c.drop 5).toNat?.map fun m => withRules 6 m fun _ => wide 4
    else if c.startsWith "guard" then (c.drop 5).toNat?.map fun e => withRules 6 9 fun _ => wide e
    else if c.startsWith "few" then match (c.drop 3).splitOn "x" with
      | [n, m] => n.toNat?.bind fun n => m.toNat?.map fun m => withRules n m fun _ => .top
      | _ => none
    else if c.startsWith "R" then match (c.drop 1).splitOn "_" with
      | [n, m, e] => n.toNat?.bind fun n => m.toNat?.map fun m =>
          withRules n m fun _ => if e == "t" then .top else wide (e.toNat?.getD 0)
      | _ => none
    else if c.startsWith "top" then (c.drop 3).toNat?.map fun m => withRules 6 m fun _ => .top
    else none

def summary : Except String α → String
  | .ok _ => "ok"
  | .error e => s!"error: {e.take 160}"

def main (args : List String) : IO UInt32 := do
  let [mode, file] := args | IO.eprintln "usage: bench <parse|admit|s2|sup|check> <file>"; return 2
  let .ok j := Json.parse (← IO.FS.readFile file) | IO.eprintln "bad json"; return 2
  let case := (j.getObjValAs? String "case").toOption.getD "?"
  let env := j.getObjValD "environment"
  let doc := j.getObjValD "document"
  let t0 ← IO.monoNanosNow
  let out : String ← match mode with
    | "parse" => pure s!"parsed {(doc.getObjValD "units").getArr?.toOption.map (·.size) |>.getD 0} units"
    | "admit" => pure (summary (admitSD env doc))
    | "s2" => pure (summary (admitS2 env doc))
    | "sup" => pure (match admitS2 env doc with
        | .ok b => s!"sup: {(sup b.D).1.soft.T.nodes.length} nodes, {(sup b.D).2.length} assertions"
        | .error e => s!"error: {e.take 160}")
    | "free" | "texts" | "chain" | "nd" => pure (match admitS2 env doc with
        | .ok b =>
          let re := b.a.re
          let N : NDoc := ⟨b.D, unspecOf re b.D⟩
          let cs := if (choices N.D).length ≤ maxChoices then choices N.D else []
          match mode with
          | "free" => s!"ndTextWith: {(ndTextWith re N b.a.side).isSome}"
          | "texts" => s!"{cs.length} per-choice texts: {((cs.findSome? (sdChoiceText re N)).map (·.take 120))}"
          | "chain" => s!"{cs.length} choiceChainText: {(cs.filterMap (choiceChainText N.D)).length} some"
          | _ => s!"{cs.length} ndDocTextG on choiceU: {(cs.filterMap fun c =>
              ndDocTextG re (decisionCount (choiceDoc N.D c).1) (choiceU N c)).length} some"
        | .error e => s!"error: {e.take 160}")
    | "check" => pure (match decodeEnvironment env, expected case with
        | .ok re, some N => match decodeDocument re doc with
          | .ok d =>
            -- the decoded document, as S1's admission reads it (`docOf`), whether or not it is admitted
            let M : NDoc := ⟨docOf re d, unspecOf re (docOf re d)⟩
            let same := decide (M.D.items = N.D.items) && decide (M.D.chain = N.D.chain) && M.D.couplings.isEmpty &&
              M.D.narrowings.isEmpty && M.unspec == N.unspec && sdSizeCharge M == sdSizeCharge N
            s!"same as the Lean NDoc: {same}; choices {(choices M.D).length}; sdSizeCharge {sdSizeCharge M}; " ++
              s!"admitSD {summary (admitSD env doc)}"
          | .error e => s!"decode error: {e.take 160}"
        | .error e, _ => s!"environment error: {e.take 160}"
        | _, none => "no Lean NDoc for this case")
    | m => pure s!"unknown mode {m}"
  let t1 ← IO.monoNanosNow
  IO.println s!"{case} {mode}: {out} ({(t1 - t0) / 1000000} ms)"
  return 0
