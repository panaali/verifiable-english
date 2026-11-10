/- sc-11w's CPU bench (docs/rd-9/sc-11w/cpu.md): the `main` of a throwaway Lake package that requires this worktree's
`lean/` (`[[require]] name = "veReference"`, `path = "<worktree>/lean"`; `[[lean_exe]] name = "bench"`, `root = "Bench"`),
built by `lake build bench` and run as `/usr/bin/time -f %U ./.lake/build/bin/bench <case> <value>`: one case, one value
per process, so user CPU is that value's (plus the environment decode and the document build, a few ms). The documents
are SoftSupWireExamples.lean's, restated here so the bench builds without that module's `#guard`s. -/
import VE.Readings.SoftSupWire
import VE.Readings.SoftSupExamples
open Lean VE.Readings VE.Readings.Wire
open VE.Readings.SoftSeparateExamples (frame4 mustX needNotX)
open VE.Readings.Examples (docK cand binarySet)
open VE.Rights.Examples (strictNode)

def envJ : Json := Json.mkObj [("language", "ve.core@0.2"), ("spec_revision", "ve-v0.2-expand2-2026-09-25"),
  ("profiles", toJson ["norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]),
  ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("agent", Json.mkObj [("description", "agent")])]),
    ("predicates", Json.mkObj []), ("constants", Json.mkObj [])])]
def wide : Nat → VE.Formula
  | 0 => .unary "c" (.var 0)
  | k + 1 => .and (wide k) (wide k)
def sized : Nat → VE.Formula
  | 0 | 1 => .top
  | 2 => .unary "c" (.var 0)
  | n + 3 => .and (sized ((n + 2) / 2)) (sized (n + 2 - (n + 2) / 2))
decreasing_by all_goals omega
def softSet (k : Nat) (g : VE.Formula := .top) : Item :=
  .set ⟨s!"rs{k}", s!"u{k + 1}", 1, [cand "strict" (strictNode s!"must-x-{k}" "x_required" true g),
    cand "default" { mustX with name := s!"must-x-{k}" }]⟩
def NSDbig (n : Nat) (g : VE.Formula := .top) : NDoc :=
  ⟨docK (.fixed "u0" (.norm needNotX) [] :: (List.range n).map (fun k => softSet k (if k == 0 then g else .top)))
    .soft frame4, ["y_permitted"]⟩
/-- `NSDbig n` and `m` guarded fixed rules of formula `g k` (SoftSupWireExamples' `NSDheavy`, `NSDsized`). -/
def withRules (n m : Nat) (g : Nat → VE.Formula) : NDoc := ⟨{ (NSDbig n).D with items := ((NSDbig n).D.items ++
  (List.range m).map (fun i => .fixed s!"g{i}" (.norm (strictNode s!"guarded-{i}"
    (["x_required", "x_permitted", "y_permitted"][i % 3]!) true (g i))) [])) }, ["y_permitted"]⟩
/-- `NSDbig n` and `k` sets of two assertions (`binarySet`). -/
def withSets (n k : Nat) : NDoc := ⟨{ (NSDbig n).D with items := ((NSDbig n).D.items ++ (List.range k).map
  (binarySet ∘ (· + n))) }, ["y_permitted"]⟩
/-- `NSDbig n` and one set of `k` assertion candidates. -/
def withCandidates (n k : Nat) : NDoc := ⟨{ (NSDbig n).D with items := (NSDbig n).D.items ++ [.set ⟨"wc", "uwc", 1,
  (List.range k).map fun i => ⟨s!"c{i}", some (.assertion .top), [], []⟩⟩] }, ["y_permitted"]⟩

def cases : List (String × NDoc) :=
  [("wideGuard191", NSDbig 8 (wide 6)), ("wideGuard767", NSDbig 8 (wide 8)), ("wideGuard3071", NSDbig 6 (wide 10)),
   ("NSDheavy", withRules 6 10 fun _ => wide 4), ("NSDbig8", NSDbig 8), ("heavyIn", withRules 6 9 fun _ => wide 4),
   ("atCharge", withRules 2 9 fun i => sized (if i < 3 then 113 else 112)),
   ("overCharge", withRules 2 22 fun i => sized (if i < 2 then 26 else 25)),
   ("at8x2048", withRules 2 1 fun _ => sized 2035), ("at32x512", withRules 2 25 fun i => sized (if i < 24 then 20 else 19)),
   ("sets300", withSets 1 300), ("cands5000", withCandidates 1 5000)] ++
  ((List.range 9).map fun e => (s!"rules{e}", withRules 2 (2 ^ e) fun _ => sized 1)) ++
  ((List.range 9).map fun e => (s!"guard{e}", withRules 2 3 fun _ => sized (2 ^ (e + 3)))) ++
  ((List.range 9).map fun e => (s!"sets{e}", withSets 1 (2 ^ e))) ++
  ((List.range 13).map fun e => (s!"cands{e}", withCandidates 1 (2 ^ e)))

/-- `sdCheckWork` as main evaluates it without the csimp: every premise of `softXL` built, then counted. -/
def slowWork (N : NDoc) : Nat :=
  (checkedChoices N.D).length * ((softXL N (sup N.D).1).length + ((sup N.D).1.soft.T.nodes.map
    (fun M => (M.guard :: M.carveOuts).map VE.Bridge.formulaNodes)).flatten.sum)

def main (args : List String) : IO Unit := do
  let .ok re := decodeEnvironment envJ | IO.println "environment"
  let some N := cases.lookup (args.headD "") | IO.println s!"cases: {cases.map (·.1)}"
  let t0 ← IO.monoNanosNow
  let out := match args.getD 1 "route" with
    | "route" => s!"routeSD {(routeSD re N).text}"
    | "charge" => s!"sdSizeCharge {sdSizeCharge N}, sdSuperposable {sdSuperposable N}"
    | "reads" => s!"superposable {superposable N.D}, WellFormedU {VE.NormDefaults.WellFormedU (supU N)}"
    | "choices" => s!"checkedChoices {(checkedChoices N.D).length}"
    | "work" => s!"sdCheckWork {sdCheckWork N}"
    | "slowwork" => s!"sdCheckWork without the csimp {slowWork N}"
    | v => s!"values: route charge reads choices work slowwork, not {v}"
  IO.println out
  let t1 ← IO.monoNanosNow
  IO.println s!"wall ms {(t1 - t0) / 1000000}"
