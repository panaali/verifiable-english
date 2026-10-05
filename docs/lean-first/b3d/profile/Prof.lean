import VE.Readings.Run
/-! Lean-first batch 3d: where a UDHR validation and a pair spend their CPU, step by step (plan F5d).

    cd docs/lean-first/b3d/profile && lake build && .lake/build/bin/prof CASE.json MODE [SET]

`CASE.json` is a `ve_readings_route` case file (`docs/lean-first/b3b/udhr_timing.py dump`). Each line is one step,
its wall time and this process's CPU time (user + system, from `/proc/self/stat`, 10 ms resolution). Modes:

* `prims`: on the first content-bearing candidate's `correlate (one D s i)`, the primitives a validation repeats
  (`soften`, the layer order, `envAt`, `semanticCheck`, the expansion table), then each specified check beside the
  function that replaces it (`targets`/`targetsIn`, `checkSoft`/`checkSoftOnce`, `softSemanticCheck`/
  `softSemanticCheckOnce`, `validateRights`/`validateRightsOnce`), with both answers compared.
* `split`: admission, then per content-bearing set its rows, its pairs (`setPairs`, each candidate's side built
  once for the set) and its findings.
* `pair SET`: after admission, the first pair of `SET` by `pairFactsSpec` (each side built for the pair; batch 3b's
  `pairFacts` before the batch 3d review) and by `pairFactsIn` (each side built once), with both answers compared.
-/
open Lean VE.Readings VE.Readings.Wire VE.Readings.Run

@[noinline, never_extract] def force {α : Type} (f : Unit → α) : IO α := pure (f ())

def cpu : IO Nat := do
  let s ← IO.FS.readFile "/proc/self/stat"
  let fs := ((s.splitOn ") ").getLast!).splitOn " "
  pure (fs[11]!.toNat! + fs[12]!.toNat!)

def tm {α : Type} (label : String) (f : Unit → α) : IO α := do
  let c0 ← cpu
  let t0 ← IO.monoNanosNow
  let r ← force f
  let t1 ← IO.monoNanosNow
  let c1 ← cpu
  IO.println s!"{label}: wall {(t1 - t0).toFloat / 1e9} s, cpu {(c1 - c0).toFloat / 100} s"
  pure r

def main (args : List String) : IO Unit := do
  let path :: mode :: rest := args | throw (IO.userError "usage: prof CASE.json prims|split|pair SET")
  let some (Except.ok j) := (VE.JsonInput.parseCases (← IO.FS.readFile path)).toOption.bind (·[0]?)
    | throw (IO.userError "no case")
  let env := j.getObjValD "environment"
  let docJ := j.getObjValD "document"
  let .ok re := decodeEnvironment env | throw (IO.userError "environment")
  let .ok doc := decodeDocument re docJ | throw (IO.userError "document")
  let D := docOf re doc
  let sets := D.sets.filter contentBearing
  let some R := sets.head? | return
  let X := one D R.id 0
  let C := VE.Rights.correlate X.1
  match mode with
  | "prims" =>
    let S ← tm "soften" (fun _ => VE.SoftNorms.soften C)
    IO.println s!"nodes {C.T.nodes.length}, regulated {C.T.regulated.length}, definitions {C.T.definitions.length}, colliding {(VE.SoftNorms.collidingPairs C).length}"
    let _ ← tm "stratumNodes" (fun _ => VE.Norms.stratumNodes S.T)
    let _ ← tm "order" (fun _ => VE.Norms.order S.T)
    let ss ← tm "syms" (fun _ => VE.Norms.syms S.T)
    IO.println s!"syms {ss.length}"
    let _ ← tm "envAt 0" (fun _ => VE.Norms.envAt S 0)
    let _ ← tm "size" (fun _ => VE.Norms.size S)
    let _ ← tm "check (W1, height by recursion)" (fun _ => VE.Norms.check S)
    let _ ← tm "checkW1" (fun _ => VE.SoftNorms.checkW1 S)
    let _ ← tm "semanticCheck" (fun _ => VE.Norms.semanticCheck S)
    let _ ← tm "WellFormed soften" (fun _ => VE.Norms.WellFormed S)
    let _ ← tm "softPremises" (fun _ => VE.SoftNorms.softPremises C)
    let _ ← tm "selects' every node" (fun _ => C.T.nodes.map (VE.SoftNorms.selects' C))
    let _ ← tm "defaultPos every regulated" (fun _ => C.T.regulated.map (fun r => VE.SoftNorms.defaultPos C r.name))
    let _ ← tm "strictPos every regulated" (fun _ => C.T.regulated.map (fun r => VE.SoftNorms.strictPos C r.name))
    let _ ← tm "targets" (fun _ => VE.Norms.targets S)
    let L ← tm "layersOf" (fun _ => VE.Norms.layersOf S)
    let _ ← tm "targetsIn" (fun _ => VE.Norms.targetsIn S L)
    IO.println s!"targets = targetsIn: {(VE.Norms.targets S).map (·.2.2) == (VE.Norms.targetsIn S L).map (·.2.2)}"
    let _ ← tm "background" (fun _ => VE.Norms.background S)
    let _ ← tm "generatedSizes" (fun _ => VE.SoftNorms.generatedSizes C)
    let _ ← tm "derivedSizes" (fun _ => VE.SoftNorms.derivedSizes C)
    let a ← tm "checkSoft" (fun _ => VE.SoftNorms.checkSoft C)
    let b ← tm "checkSoftOnce" (fun _ => VE.SoftNorms.checkSoftOnce C)
    IO.println s!"checkSoft = checkSoftOnce: {a.toBool == b.toBool}"
    let a ← tm "softSemanticCheck" (fun _ => VE.SoftNorms.softSemanticCheck C)
    let b ← tm "softSemanticCheckOnce" (fun _ => VE.SoftNorms.softSemanticCheckOnce C)
    IO.println s!"softSemanticCheck = softSemanticCheckOnce: {a == b}"
    let _ ← tm "checkRights" (fun _ => VE.Rights.checkRights X.1)
    let _ ← tm "rightsSemanticCheck" (fun _ => VE.Rights.rightsSemanticCheck X.1)
    let a ← tm "validateRights" (fun _ => VE.Rights.validateRights X.1)
    let b ← tm "validateRightsOnce" (fun _ => VE.Rights.validateRightsOnce X.1)
    IO.println s!"validateRights = validateRightsOnce: {a.toBool == b.toBool}"
    let a ← tm "chainTextSpec" (fun _ => chainTextSpec D.chain X)
    let b ← tm "chainText" (fun _ => chainText D.chain X)
    IO.println s!"chainTextSpec = chainText: {a == b}"
  | "split" =>
    let a ← match ← tm "admitReadings" (fun _ => admitReadings env docJ) with
      | .ok a => pure a
      | .error e => throw (IO.userError e)
    let mut np := 0
    for R in sets do
      let some RJ := setJ a.doc R.id | return
      let _ ← tm s!"rows {R.id}" (fun _ => (List.range R.candidates.length).mapM (candidateJson a R))
      let ps ← tm s!"pairs {R.id}" (fun _ => setPairs a R RJ)
      let _ ← tm s!"findings {R.id}" (fun _ => setFindings a R)
      np := np + ((ps.toOption.map List.length).getD 0)
    IO.println s!"candidates {(sets.map (·.candidates.length)).sum}, pairs {np}"
  | "pair" =>
    let some name := rest.head? | throw (IO.userError "pair needs a set id")
    let .ok a := admitReadings env docJ | throw (IO.userError "not admitted")
    let some R := D.sets.find? (·.id == name) | throw (IO.userError "no such set")
    let some RJ := setJ a.doc R.id | return
    let (some x, some y, some rj) := (R.candidates[0]?, R.candidates[1]?, RJ.readings[0]?) | return
    let some sid := rj.models.lookup y.id | return
    let some entry := RJ.situations.lookup sid | return
    let w := match entry.getObjValD "witness" with | .str w => w | _ => ""
    let otherName := if w == x.id then y.id else x.id
    let f ← tm "pairFactsSpec" (fun _ => pairFactsSpec a R.id sid otherName)
    let sides := sidesOf a.D R.id R.candidates.length
    let g ← tm "pairFactsIn, sides built" (fun _ => pairFactsIn a (sideAt a.D R.id sides) R.id sid otherName)
    let h ← tm "pairFactsIn, sides read again" (fun _ => pairFactsIn a (sideAt a.D R.id sides) R.id sid otherName)
    let facts := fun (r : Except String PairFacts) => match r with
      | .ok f => (f.separated, f.witnessValid, f.witnessValue, f.otherAdmissible, f.otherValue)
      | .error _ => (false, false, none, false, none)
    IO.println s!"pairFactsSpec = pairFactsIn: {facts f == facts g && facts g == facts h}"
  | _ => throw (IO.userError s!"unknown mode {mode}")
