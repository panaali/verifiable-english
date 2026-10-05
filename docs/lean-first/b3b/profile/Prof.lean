import VE.Readings.Run
/-! Lean-first batch 3b: where the readings route spends its CPU (plan F5; for batches 3c to 3e).

    cd docs/lean-first/b3b/profile && lake build && .lake/build/bin/prof CASE.json MODE [SET]

`CASE.json` is a `ve_readings_route` case file (`udhr_timing.py dump`). Each line is one step, its wall time and
this process's CPU time (user + system, from `/proc/self/stat`, 10 ms resolution). Modes:

* `blocks`: decoding, attachment, `free D` and the first content-bearing candidate's `one D s i`, its elaboration
  and its validation, step by step.
* `ssc`: `softSemanticCheck` on that candidate and the same function with `soften D` and its layered environments
  computed once (`softSemanticCheckHoisted`, plan F5d); both answers are printed. (The library function rebuilds
  `envAt`, and with it the stratum order, for each formula it types; the compiler does not hoist it there.)
* `split`: admission, then per content-bearing set its rows, its pairs and its findings.
* `pair SET`: after admission, the first pair of `SET`, step by step, with the probe's formulas built and
  evaluated separately. -/
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

open VE.SoftNorms in
/-- `softSemanticCheck` with `soften D` and its two layered environments computed once. -/
def softSemanticCheckHoisted (D : SoftDoc) : Bool :=
  let S := soften D
  let E0 := VE.Norms.envAt S 0
  let En := VE.Norms.envAt S (VE.Norms.size S)
  VE.Norms.WellFormed S &&
  decide (D.T.nodes.map (·.name)).Nodup &&
  decide (D.T.regulated.map (·.name)).Nodup &&
  decide ((VE.Norms.pairs D.base.T).map (·.req)).Nodup &&
  decide ((VE.Norms.pairs D.base.T).map (·.perm)).Nodup &&
  (VE.Norms.pairs D.base.T).all (fun pr => !((VE.Norms.pairs D.base.T).map (·.req)).contains pr.perm) &&
  D.T.nodes.all (fun N => (D.T.regulated.map (·.name)).contains N.pred) &&
  D.soft.outranks.all (fun e => D.soft.ranks.contains e.1 && D.soft.ranks.contains e.2) &&
  (VE.Route.dependencyOrder (rankNodes D.soft)).isOk &&
  decide (D.soft.below = closureOf D.soft.ranks D.soft.outranks) &&
  D.T.nodes.all (fun N => N.mode != .default ||
    N.over.all (fun m => (D.T.nodes.find? (·.name == m)).all (·.mode == .default))) &&
  decide (decisionNames D).Nodup &&
  (decisionNames D).all (fun n => (D.E.predicates n).isNone) &&
  D.T.nodes.all (fun N => (N.guard :: N.carveOuts).all (fun φ => φ.check D.E (sortsOf D N.pred).reverse)) &&
  (softPremises D).all (fun φ => φ.check E0 []) &&
  D.T.nodes.all (fun N => (selects' D N).check En (sortsOf D N.pred).reverse) &&
  (collidingPairs D).all (fun x => sortsOf D x.1.pred == sortsOf D x.2.pred) &&
  D.T.regulated.all (fun r => (D.E.predicates r.name).isSome) &&
  D.T.regulated.all (fun r =>
    [strictPos D r.name, strictNeg D r.name, defaultPos D r.name, defaultNeg D r.name].all
      (fun φ => φ.check En r.sorts.reverse))

def admitted (env docJ : Json) : IO Admitted := do
  match ← tm "admitReadings" (fun _ => admitReadings env docJ) with
  | .ok a => pure a
  | .error e => throw (IO.userError e)

def main (args : List String) : IO Unit := do
  let path :: mode :: rest := args | throw (IO.userError "usage: prof CASE.json blocks|ssc|split|pair SET")
  let some (Except.ok j) := (VE.JsonInput.parseCases (← IO.FS.readFile path)).toOption.bind (·[0]?)
    | throw (IO.userError "no case")
  let env := j.getObjValD "environment"
  let docJ := j.getObjValD "document"
  let re ← match ← tm "decodeEnvironment" (fun _ => decodeEnvironment env) with
    | .ok r => pure r | .error e => throw (IO.userError e)
  let doc ← match ← tm "decodeDocument" (fun _ => decodeDocument re docJ) with
    | .ok r => pure r | .error e => throw (IO.userError e)
  let D := docOf re doc
  let sets := D.sets.filter contentBearing
  IO.println s!"items {D.items.length}, fixed units {(fixedNames D).length}, sets {D.sets.length}, content-bearing {sets.length}"
  let some R := sets.head? | return
  let X := one D R.id 0
  let S := VE.Rights.correlate X.1
  match mode with
  | "blocks" =>
    let _ ← tm "attached table" (fun _ => attachedIter D D.items.length (attachedLevel0 D))
    let fr ← tm "free" (fun _ => free D)
    let _ ← tm "chainText free" (fun _ => chainText D.chain fr)
    let _ ← tm "one" (fun _ => one D R.id 0)
    IO.println s!"one: {X.1.soft.T.nodes.length} nodes, {X.1.rs.length} rights; regulated {S.T.regulated.length}"
    let _ ← tm "correlate" (fun _ => VE.Rights.correlate X.1)
    let _ ← tm "genKeys" (fun _ => genKeys X.1)
    let _ ← tm "checkRights" (fun _ => VE.Rights.checkRights X.1)
    let _ ← tm "checkSoft" (fun _ => VE.SoftNorms.checkSoft S)
    let _ ← tm "targets" (fun _ => VE.Norms.targets (VE.SoftNorms.soften S))
    let _ ← tm "softSemanticCheck" (fun _ => VE.SoftNorms.softSemanticCheck S)
    let _ ← tm "rightsSemanticCheck" (fun _ => VE.Rights.rightsSemanticCheck X.1)
    let _ ← tm "validateRights" (fun _ => VE.Rights.validateRights X.1)
    let _ ← tm "chainText one" (fun _ => chainText D.chain X)
    let _ ← tm "sideWF one" (fun _ => sideWF D X)
    let _ ← tm "limitationScope" (fun _ => VE.Rights.limitationScope X.1 [])
    let _ ← tm "noDistinction" (fun _ => VE.Rights.noDistinction X.1)
  | "ssc" =>
    let _ ← tm "layerNames" (fun _ => VE.Norms.layerNames (VE.SoftNorms.soften S).T)
    let a ← tm "softSemanticCheck" (fun _ => VE.SoftNorms.softSemanticCheck S)
    let b ← tm "softSemanticCheckHoisted" (fun _ => softSemanticCheckHoisted S)
    IO.println s!"answers {a} {b}"
  | "split" =>
    let a ← admitted env docJ
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
    let a ← admitted env docJ
    let some R := D.sets.find? (·.id == name) | throw (IO.userError "no such set")
    let some RJ := setJ a.doc R.id | return
    let (some x, some y, some rj) := (R.candidates[0]?, R.candidates[1]?, RJ.readings[0]?) | return
    let some sid := rj.models.lookup y.id | return
    let some entry := RJ.situations.lookup sid | return
    let w := match entry.getObjValD "witness" with | .str w => w | _ => ""
    let otherName := if w == x.id then y.id else x.id
    let .ok (r, _) ← tm "replayPair" (fun _ => replayPair a R.id sid otherName) | IO.println "refused"
    let (M, s) := (r.σ.base, R.id)
    let Ti := tablesFor r.D s r.witness (r.σ.fixed ++ r.σ.decisions)
    let Tj := tablesFor r.D s r.other r.σ.fixed
    let _ ← tm "situationWF" (fun _ => situationWF r.D s r.witness r.other r.σ)
    let _ ← tm "sideValid witness" (fun _ => sideValid r.D s r.witness M Ti)
    let _ ← tm "sideValue witness" (fun _ => sideValue r.D s r.witness M Ti r.σ.probe)
    let gs := assignments r.D s r.other M
    IO.println s!"other side: {gs.length} assignments"
    let _ ← tm "sideValid other, every assignment" (fun _ => gs.map (fun G => sideValid r.D s r.other M (Tj ++ G)))
    let _ ← tm "sideValue other, every assignment" (fun _ =>
      gs.map (fun G => sideValue r.D s r.other M (Tj ++ G) r.σ.probe))
    let XW := (one r.D s r.witness).1
    let T := VE.SoftNorms.soften (VE.Rights.correlate XW)
    if let .outcome p vs := r.σ.probe then
      if let some rr := (VE.Rights.correlate XW).T.regulated.find? (·.name == p) then
        let cf ← tm "conflict formula, built" (fun _ => VE.Norms.conflict T rr)
        let ob ← tm "outcome formula, built" (fun _ => VE.Norms.outcomeBase T p)
        let MT := tablesModel XW M Ti
        let _ ← tm "conflict formula, evaluated" (fun _ => cf.eval MT (VE.Norms.tupleVal vs))
        let _ ← tm "outcome formula, evaluated" (fun _ => ob.eval MT (VE.Norms.tupleVal vs))
    let _ ← tm "pairFacts" (fun _ => pairFacts a s sid otherName)
  | _ => throw (IO.userError s!"unknown mode {mode}")
