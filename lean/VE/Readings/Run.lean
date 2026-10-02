import VE.Readings.Wire
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

/-- The chain findings that need no certificate (4.4, plan F5), on the rights chain. -/
def chainFindings (a : Admitted) (R : ReadingSet) (i : Nat) : List String :=
  match a.re.chain with
  | .rights =>
    let X := (one a.D R.id i).1
    ((VE.Rights.limitationScope X []).map (·.text) ++ (VE.Rights.noDistinction X).map (·.text)).map
      (· ++ s!" under {R.id}@{R.version}:{i}")
  | _ => []

def candidateJson (a : Admitted) (R : ReadingSet) (i : Nat) : Except String Json := do
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

def pairFacts (a : Admitted) (s : String) (sid other : String) : Except String PairFacts := do
  let (r, sj) ← replayPair a s sid other
  let M := r.σ.base
  let Ti := tablesFor r.D s r.witness (r.σ.fixed ++ r.σ.decisions)
  if cells r.D s r.other M > maxCells then throw "ResourceLimit: decision assignments"
  let Tj := tablesFor r.D s r.other r.σ.fixed
  pure ⟨r, sj.witness, separates r.D s r.witness r.other r.σ, sideValid r.D s r.witness M Ti,
    sideValue r.D s r.witness M Ti r.σ.probe,
    (assignments r.D s r.other M).any (fun G => sideValid r.D s r.other M (Tj ++ G)),
    if ownedKeys r.D s r.other = [] then sideValue r.D s r.other M Tj r.σ.probe else none⟩

def pairJson (f : PairFacts) (sid : String) : Json :=
  Json.mkObj ([("situation", .str sid), ("witness", .str f.witnessName), ("separated", .bool f.separated),
    ("witness_admissible", .bool f.witnessValid), ("witness_value", optBool f.witnessValue),
    ("other_admissible", .bool f.otherAdmissible)] ++
    (if ownedKeys f.replay.D f.replay.set f.replay.other = [] then [("other_value", optBool f.otherValue)] else []))

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

/-- 4.6: the findings of an admitted set, per unordered pair. -/
def setFindings (a : Admitted) (R : ReadingSet) : List String :=
  let n := R.candidates.length
  (List.range n).flatMap (fun i => ((List.range n).filter (i < ·)).flatMap (fun j =>
    (if (decisionOnly a.D R.id i j).isSome then [decisionOnlyText R.id i j]
     else if (decisionOnly a.D R.id j i).isSome then [decisionOnlyText R.id j i] else []) ++
    (if (actOnly a.D R.id i j).isSome then [s!"SeparatedByActOnly: {R.id}: {i}, {j}"] else [])))

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
