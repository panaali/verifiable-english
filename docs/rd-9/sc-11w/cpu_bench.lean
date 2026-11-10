/- sc-11w's CPU bench (docs/rd-9/sc-11w/cpu.md): the `main` of a throwaway Lake package that requires this worktree's
`lean/` (`[[require]] name = "veReference"`, `path = "<worktree>/lean"`; `[[lean_exe]] name = "bench"`, `root = "Bench"`),
built by `lake build bench` and run as `/usr/bin/time -f %U ./.lake/build/bin/bench <case> <value>`: one case, one value
per process, so user CPU is that value's (plus the environment decode and the document build, a few ms). -/
import VE.Readings.SoftSupWireExamples
open Lean VE.Readings VE.Readings.Wire VE.Readings.SoftSupWireExamples
open VE.Rights.Examples (strictNode)

/-- `NSDbig n` and `m` guarded fixed rules of `k` nodes (`NSDsized` on `NSDbig 2`). -/
def withRules (n m k : Nat) : NDoc := ⟨{ (NSDbig n).D with items := (NSDbig n).D.items ++ (List.range m).map (fun i =>
  .fixed s!"g{i}" (.norm (strictNode s!"guarded-{i}" (["x_required", "x_permitted", "y_permitted"][i % 3]!) true
    (sized k))) []) }, ["y_permitted"]⟩

def cases : List (String × NDoc) :=
  [("wideGuard191", wideGuard191), ("wideGuard767", wideGuard767), ("wideGuard3071", wideGuard3071),
   ("NSDheavy", NSDheavy), ("NSDbig8", NSDbig 8), ("atCharge", atCharge), ("overCharge", overCharge),
   ("at8x2048", NSDsized 3 679 0), ("at32x512", NSDsized 27 18 15), ("at64x256", NSDsized 59 4 9),
   ("at6sets16x1024", withRules 6 3 331)]

/-- `sdCheckWork` as main evaluates it without the csimp: every premise of `softXL` built, then counted. -/
def slowWork (N : NDoc) : Nat :=
  (checkedChoices N.D).length * ((softXL N (sup N.D).1).length + ((sup N.D).1.soft.T.nodes.map
    (fun M => (M.guard :: M.carveOuts).map VE.Bridge.formulaNodes)).flatten.sum)

def main (args : List String) : IO Unit := do
  let .ok re := decodeEnvironment (envWith 0) | IO.println "environment"
  let some N := cases.lookup (args.headD "") | IO.println s!"cases: {cases.map (·.1)}"
  let t0 ← IO.monoNanosNow
  let out := match args.getD 1 "route" with
    | "route" => s!"routeSD {(routeSD re N).text}"
    | "charge" => s!"sdSizeCharge {sdSizeCharge N}, sdSuperposable {sdSuperposable N}"
    | "reads" => s!"superposable {superposable N.D}, WellFormedU {VE.NormDefaults.WellFormedU (supU N)}"
    | "work" => s!"sdCheckWork {sdCheckWork N}"
    | "slowwork" => s!"sdCheckWork without the csimp {slowWork N}"
    | v => s!"values: route charge reads work slowwork, not {v}"
  IO.println out
  let t1 ← IO.monoNanosNow
  IO.println s!"wall ms {(t1 - t0) / 1000000}"
