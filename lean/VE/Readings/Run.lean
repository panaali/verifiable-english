import VE.Readings.Wire
import VE.Readings.Scan
import VE.NormDefaults.Run
import VE.Rights.Run

/-! The `ve_readings_route` executable (docs/spec/composition-s1.md 8.4), invoked as
`lean/.lake/build/bin/ve_readings_route <cases.json|->`. Each case is `{"id", "kind", "environment", "document",
...}` with `readings@1` in the environment's profiles and the document of `Wire.lean`.

* `readings-validate`: the checks of 4.1 in order, then the answer regenerated from the decoded document: per
  content-bearing set in source order and per candidate, whether it is pending, the chain's document hash of
  `one D s i` (the hash of the chain's own route over its units), its owned and shared keys with their generated
  names, and its chain findings with the suffix ` under <set>@<v>:<i>`; per pair of candidates neither of which is
  pending, in index order, the situation recorded for it and `separated`; the findings of 4.6. Or the first
  diagnostic. A document with no content-bearing set answers `content_bearing: false` and is today's.
* `readings-separate`: `set`, `situation` (an id of the set's `situations`) and `other` (the other reading's id);
  the witness is the situation's. The answer is `separated`, the witness's completion (`witness_admissible`,
  `witness_value`), the other side's (`other_admissible`: some assignment of its owned tables is admissible;
  `other_value`, present when it owns no key); or the diagnostic of 4.5 step 1. `separated: true` is
  `Wire.readings_wire_separate_sound`'s hypothesis.
* Every other kind: `readings@1` is stripped from the profiles and the case is run by the lower route's runner
  (`dispatch` on the list without `readings@1`). -/
namespace VE.Readings.Run
open Lean
open VE.Readings
open VE.Readings.Wire
open VE.Bridge (stringField strings)

def optBool : Option Bool → Json
  | some b => .bool b
  | none => .null

/-! ## The chain's document hash of `one D s i` -/

/-- The unit contents of `one D s i` in source order, as written (formulas are not hashed). -/
def oneJson (D : Doc) (itemsJ : List ItemJ) (s : String) (i : Nat) : List Json :=
  let keep := fun u => (attached D u).all (· == s)
  itemsJ.flatMap (fun it => match it with
    | .fixed u j => if keep u && !(j matches .arr _) then [j] else []
    | .bar u j => if keep u then [j] else []
    | .set R => if R.id == s then
        match R.readings[i]? with
        | some r => if r.content matches .obj _ then [r.content] else []
        | none => []
      else [])

def documentHash (a : Admitted) (s : String) (i : Nat) : Except String String :=
  let units := oneJson a.D a.doc.itemsJ s i
  match a.re.chain with
  | .rights => VE.Rights.Wire.rightsDocumentHash a.re.lower a.re.lowerJson
      (Json.arr ((Json.mkObj [("source_units", toJson a.doc.units)] :: units).toArray))
  | .soft => VE.SoftNorms.Wire.softDocumentHash a.re.lower a.re.lowerJson (Json.arr units.toArray)
  | .norms => VE.Norms.Replay.documentHash a.re.lower a.re.lowerJson (Json.arr units.toArray)

/-! ## Per candidate -/

def keyEntry (X : VE.Rights.RightsDoc) (k : GenKey) : Json :=
  Json.mkObj [("key", keyJson k), ("name", .str ((((genKeys X).find? (·.1 == k)).map (·.2.1)).getD ""))]

/-- The chain findings that need no certificate (4.4, plan F5) of candidate i's document X, on the rights chain. -/
def findingsOf (a : Admitted) (R : ReadingSet) (i : Nat) (X : VE.Rights.RightsDoc) : List String :=
  match a.re.chain with
  | .rights =>
    ((VE.Rights.limitationScope X []).map (·.text) ++ (VE.Rights.noDistinction X).map (·.text)).map
      (· ++ s!" under {R.id}@{R.version}:{i}")
  | _ => []

def chainFindings (a : Admitted) (R : ReadingSet) (i : Nat) : List String := findingsOf a R i (one a.D R.id i).1

/-- A candidate's row as specified: its document `one D s i` is built for the keys and again for the findings. -/
def candidateJsonSpec (a : Admitted) (R : ReadingSet) (i : Nat) : Except String Json := do
  let some c := R.candidates[i]? | throw "InvalidInput: invalid reading"
  match c.content with
  | none => pure (Json.mkObj [("id", .str c.id), ("index", toJson i), ("pending", .bool true)])
  | some _ =>
    let X := (one a.D R.id i).1
    let keys := VE.SoftNorms.dedup ((genKeys X).map (·.1))
    pure (Json.mkObj [("id", .str c.id), ("index", toJson i), ("pending", .bool false),
      ("document_hash", .str (← documentHash a R.id i)),
      ("owned", Json.arr ((keys.filter (owned a.D R.id i)).map (keyEntry X)).toArray),
      ("shared", Json.arr ((keys.filter (fun k => !owned a.D R.id i k)).map (keyEntry X)).toArray),
      ("findings", toJson (chainFindings a R i))])

/-- A candidate's row, its document read once from the request's table (plan F5b). -/
def candidateJson (a : Admitted) (R : ReadingSet) (i : Nat) : Except String Json := do
  let some c := R.candidates[i]? | throw "InvalidInput: invalid reading"
  match c.content with
  | none => pure (Json.mkObj [("id", .str c.id), ("index", toJson i), ("pending", .bool true)])
  | some _ =>
    let X := (a.side R.id i).1
    let keys := VE.SoftNorms.dedup ((genKeys X).map (·.1))
    pure (Json.mkObj [("id", .str c.id), ("index", toJson i), ("pending", .bool false),
      ("document_hash", .str (← documentHash a R.id i)),
      ("owned", Json.arr ((keys.filter (owned a.D R.id i)).map (keyEntry X)).toArray),
      ("shared", Json.arr ((keys.filter (fun k => !owned a.D R.id i k)).map (keyEntry X)).toArray),
      ("findings", toJson (findingsOf a R i X))])

theorem candidateJson_eq (a : Admitted) (R : ReadingSet) (i : Nat) :
    candidateJson a R i = candidateJsonSpec a R i := by
  simp only [candidateJson, candidateJsonSpec, chainFindings, Admitted.side_eq]

/-! ## Per pair -/

/-- The facts of one checked pair: the replay, the witness's and the other side's completions. -/
structure PairFacts where
  replay : SeparateReplay
  witnessName : String
  separated : Bool
  witnessValid : Bool
  witnessValue : Option Bool
  otherAdmissible : Bool
  otherValue : Option Bool

/-- The facts of one pair as specified: `separates`, then each side's completions evaluated again. -/
def pairFactsSpec (a : Admitted) (s : String) (sid other : String) : Except String PairFacts := do
  let (r, sj) ← replayPair a s sid other
  let M := r.σ.base
  let Ti := tablesFor r.D r.set r.witness (r.σ.fixed ++ r.σ.decisions)
  if cells r.D r.set r.other M > maxCells then throw "ResourceLimit: decision assignments"
  let Tj := tablesFor r.D r.set r.other r.σ.fixed
  pure ⟨r, sj.witness, separates r.D r.set r.witness r.other r.σ, sideValid r.D r.set r.witness M Ti,
    sideValue r.D r.set r.witness M Ti r.σ.probe,
    (assignments r.D r.set r.other M).any (fun G => sideValid r.D r.set r.other M (Tj ++ G)),
    if ownedKeys r.D r.set r.other = [] then sideValue r.D r.set r.other M Tj r.σ.probe else none⟩

/-- The facts of one pair, each side's documents read from the request's table and each completion evaluated at
    most once and only when needed (plan F5b): the witness's for `separated` and its two fields; with no owned key
    the other side's one completion for `separated`, `other_admissible` and `other_value`; otherwise the other
    side's completions through `otherScan`. `situationWF` is the replay's `shape` and the bound was checked, so
    neither is evaluated again. -/
def pairFacts (a : Admitted) (s : String) (sid other : String) : Except String PairFacts := do
  let (r, sj) ← replayPair a s sid other
  let M := r.σ.base
  let ks := ownedKeysOf r.D r.set r.other r.Xj.1
  if cellsOf ks r.Xj.1 M > maxCells then throw "ResourceLimit: decision assignments"
  let Ti := tablesForOf r.Xi.1 (r.σ.fixed ++ r.σ.decisions)
  let Tj := tablesForOf r.Xj.1 r.σ.fixed
  let valid := sideValidOf r.Xi.1 M Ti
  let value := sideValueOf r.Xi M Ti r.σ.probe
  let want := valid && value == some r.σ.value
  if ks = [] then
    let ok := sideValidOf r.Xj.1 M Tj
    let v := sideValueOf r.Xj M Tj r.σ.probe
    pure ⟨r, sj.witness, want && !(ok && v == some r.σ.value), valid, value, ok, v⟩
  else
    let o := otherScan (m := Id) (pure ()) (pure ()) r.Xj M Tj r.σ.probe r.σ.value want (assignmentsOf ks r.Xj.1 M)
    pure ⟨r, sj.witness, want && !o.1, valid, value, o.2, none⟩

theorem pairFacts_eq (a : Admitted) (s : String) (sid other : String) :
    pairFacts a s sid other = pairFactsSpec a s sid other := by
  unfold pairFacts pairFactsSpec
  simp only [bind, Except.bind]
  split
  · rfl
  · rename_i v _
    obtain ⟨r, sj⟩ := v
    dsimp only
    have hs := r.shape
    rw [r.hXi, r.hXj]
    simp only [cells, ownedKeys, tablesFor, sideValid, sideValue, assignments, separates, hs, Bool.true_and]
    split
    · rfl
    · rename_i hc
      have hc' : decide (cellsOf (ownedKeysOf r.D r.set r.other (one r.D r.set r.other).1)
          (one r.D r.set r.other).1 r.σ.base ≤ maxCells) = true := by simpa using hc
      by_cases ho : ownedKeysOf r.D r.set r.other (one r.D r.set r.other).1 = []
      · simp only [ho, if_true, assignmentsOf, cellsOf, List.foldr_nil, List.all_cons, List.all_nil, List.any_cons,
          List.any_nil, List.append_nil, Bool.and_true, Bool.or_false, List.map_nil, List.sum_nil, Nat.zero_le,
          decide_true]
      · simp only [ho, if_false]
        rw [otherScan_id]
        simp only [hc', Bool.and_true, and_not_and_any]

def pairJson (f : PairFacts) (sid : String) : Json :=
  Json.mkObj ([("situation", .str sid), ("witness", .str f.witnessName), ("separated", .bool f.separated),
    ("witness_admissible", .bool f.witnessValid), ("witness_value", optBool f.witnessValue),
    ("other_admissible", .bool f.otherAdmissible)] ++
    (if ownedKeysOf f.replay.D f.replay.set f.replay.other f.replay.Xj.1 = [] then [("other_value", optBool f.otherValue)]
     else []))

/-- 4.5 for every pair of a set, neither pending, in index order: each must be separated by its situation. -/
def setPairs (a : Admitted) (R : ReadingSet) (RJ : SetJ) : Except String (List Json) := do
  let mut out : List Json := []
  for (x, ix) in R.candidates.zip (List.range R.candidates.length) do
    for (y, iy) in R.candidates.zip (List.range R.candidates.length) do
      if ix == iy || x.content.isNone || y.content.isNone then continue
      let some rj := RJ.readings[ix]? | throw "invalid reading"
      let some sid := rj.models.lookup y.id | throw "each other reading needs a distinguishing model id"
      let some entry := RJ.situations.lookup sid | throw "distinguishing model id does not match model"
      let w := match entry.getObjValD "witness" with
        | .str w => w
        | _ => ""
      -- The situation is recorded for this pair: its witness is one of the two readings. A third reading as
      -- witness would check another pair and leave this one uncompared.
      unless w == x.id || w == y.id do throw s!"InvalidInput: invalid situation {sid}"
      let otherName := if w == x.id then y.id else x.id
      let f ← pairFacts a R.id sid otherName
      unless f.witnessValid do throw "distinguishing model violates a generated premise"
      unless f.separated do throw "distinguishing model does not separate readings"
      out := out ++ [Json.mkObj [("reading", .str x.id), ("other", .str y.id), ("pair", pairJson f sid)]]
  pure out

/-- The finding of 1.7 for strict twin `i` and default twin `j`. Its theorem `decision_only_sound` is not proved
    yet (`lean/READINGS.md`), so the finding says on its face that it is not certified, and nothing reads it as a
    checked result (DRI ruling 2 of 2026-10-02). -/
def decisionOnlyText (s : String) (i j : Nat) : String :=
  s!"SeparatedByDecisionOnly: {s}: {i}, {j} (not certified)"

/-- 4.6: the findings of an admitted set, per unordered pair, as specified. -/
def setFindingsSpec (a : Admitted) (R : ReadingSet) : List String :=
  let n := R.candidates.length
  (List.range n).flatMap (fun i => ((List.range n).filter (i < ·)).flatMap (fun j =>
    (if (decisionOnly a.D R.id i j).isSome then [decisionOnlyText R.id i j]
     else if (decisionOnly a.D R.id j i).isSome then [decisionOnlyText R.id j i] else []) ++
    (if (actOnly a.D R.id i j).isSome then [s!"SeparatedByActOnly: {R.id}: {i}, {j}"] else [])))

/-- Candidate i of set s has no content: neither finding of 4.6 holds for a pair with it. -/
def pendingIn (D : Doc) (s : String) (i : Nat) : Bool := ((candidate D s i).bind (·.content)).isNone

/-- 4.6, each candidate's document read from the request's table, which holds no pending candidate's: a pair
    with a pending candidate has no finding (`pairFindings_pending`) and its sides are not read. -/
def setFindings (a : Admitted) (R : ReadingSet) : List String :=
  let n := R.candidates.length
  let X := a.side R.id
  (List.range n).flatMap (fun i => if pendingIn a.D R.id i then [] else
    ((List.range n).filter (i < ·)).flatMap (fun j => if pendingIn a.D R.id j then [] else
    (if (decisionOnlyOf a.D R.id i j (X i) (X j)).isSome then [decisionOnlyText R.id i j]
     else if (decisionOnlyOf a.D R.id j i (X j) (X i)).isSome then [decisionOnlyText R.id j i] else []) ++
    (if (actOnlyOf a.D R.id i j (X i) (X j)).isSome then [s!"SeparatedByActOnly: {R.id}: {i}, {j}"] else [])))

theorem pairFindings_pending (D : Doc) (s : String) (i j : Nat) (h : (pendingIn D s i || pendingIn D s j) = true)
    (Xi Xj : VE.Rights.RightsDoc × List VE.Formula) :
    decisionOnlyOf D s i j Xi Xj = none ∧ decisionOnlyOf D s j i Xj Xi = none ∧ actOnlyOf D s i j Xi Xj = none := by
  unfold pendingIn at h
  unfold decisionOnlyOf actOnlyOf
  cases hi : (candidate D s i).bind (·.content) <;> cases hj : (candidate D s j).bind (·.content) <;>
    simp_all

theorem setFindings_eq (a : Admitted) (R : ReadingSet) : setFindings a R = setFindingsSpec a R := by
  simp only [setFindings, setFindingsSpec, decisionOnly, actOnly, Admitted.side_eq]
  congr 1
  funext i
  split
  · rename_i hi
    symm
    refine List.flatMap_eq_nil_iff.mpr (fun j _ => ?_)
    obtain ⟨h1, h2, h3⟩ := pairFindings_pending a.D R.id i j (by simp [hi]) (one a.D R.id i) (one a.D R.id j)
    simp [h1, h2, h3]
  · congr 1
    funext j
    split
    · rename_i hj
      obtain ⟨h1, h2, h3⟩ := pairFindings_pending a.D R.id i j (by simp [hj]) (one a.D R.id i) (one a.D R.id j)
      simp [h1, h2, h3]
    · rfl

def validateResult (a : Admitted) : Except String (List (String × Json)) := do
  let sets := a.D.sets.filter contentBearing
  if sets.isEmpty then return [("content_bearing", .bool false)]
  let mut rows : List Json := []
  for R in sets do
    let some RJ := setJ a.doc R.id | throw invalidSet
    let cands ← (List.range R.candidates.length).mapM (candidateJson a R)
    let pairs ← setPairs a R RJ
    rows := rows ++ [Json.mkObj [("set", .str R.id), ("version", toJson R.version),
      ("candidates", Json.arr cands.toArray), ("pairs", Json.arr pairs.toArray),
      ("findings", toJson (setFindings a R))]]
  pure [("content_bearing", .bool true), ("sets", Json.arr rows.toArray)]

/-! ## Dispatch -/

/-- The case with `readings@1` stripped, run by the lower route's runner. -/
def runLower (j : Json) : Json :=
  match (j.getObjValD "environment").getObjVal? "profiles" >>= strings with
  | .error _ => VE.Rights.Run.runCaseReported j
  | .ok ps =>
    let lower := ps.filter (· != readingsProfile)
    let j' := match stripReadings (j.getObjValD "environment") with
      | .ok env => j.setObjVal! "environment" env
      | .error _ => j
    match VE.Compose.dispatch lower with
    | .ok .rights => VE.Rights.Run.runCaseReported j'
    | .ok .soft => VE.SoftNorms.Run.runCaseReported j'
    | .ok .normDefaults => VE.NormDefaults.Run.runCaseReported j'
    | _ => VE.Norms.Run.runCaseReported j'

def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if kind == "readings-validate" then
    let a ← admitReadings (← j.getObjVal? "environment") (← j.getObjVal? "document")
    return VE.Route.Wire.ok id (← validateResult a)
  if kind == "readings-separate" then
    let a ← admitReadings (← j.getObjVal? "environment") (← j.getObjVal? "document")
    let s ← stringField j "set"
    let sid ← stringField j "situation"
    let f ← pairFacts a s sid (← stringField j "other")
    return VE.Route.Wire.ok id [("set", .str s), ("pair", pairJson f sid)]
  throw s!"UnsupportedProfile: case kind {kind} is not available on the readings route"

def runCaseReported (j : Json) : Json :=
  match VE.Route.Run.caseKind j with
  | .ok "readings-validate" | .ok "readings-separate" =>
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]
  | _ => runLower j

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_readings_route [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j
      | .error message => Json.mkObj [("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.Readings.Run
