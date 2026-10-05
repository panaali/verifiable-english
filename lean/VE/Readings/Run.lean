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

/-- A candidate's row, its document built once (plan F5b). -/
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
      ("findings", toJson (findingsOf a R i X))])

theorem candidateJson_eq (a : Admitted) (R : ReadingSet) (i : Nat) :
    candidateJson a R i = candidateJsonSpec a R i := rfl

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
  let Ti := tablesFor r.D s r.witness (r.σ.fixed ++ r.σ.decisions)
  if cells r.D s r.other M > maxCells then throw "ResourceLimit: decision assignments"
  let Tj := tablesFor r.D s r.other r.σ.fixed
  pure ⟨r, sj.witness, separates r.D s r.witness r.other r.σ, sideValid r.D s r.witness M Ti,
    sideValue r.D s r.witness M Ti r.σ.probe,
    (assignments r.D s r.other M).any (fun G => sideValid r.D s r.other M (Tj ++ G)),
    if ownedKeys r.D s r.other = [] then sideValue r.D s r.other M Tj r.σ.probe else none⟩

/-- Candidate j's completions over M: per assignment G of its owned tables, whether it is admissible with the
    tables T ++ G, and the probe's value, evaluated when first asked for and then kept. -/
def completions {α : Type} [DecidableEq α] (D : Doc) (s : String) (j : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) (q : Probe α) : List (Bool × Thunk (Option Bool)) :=
  (assignments D s j M).map (fun G => (sideValid D s j M (T ++ G), Thunk.mk (fun _ => sideValue D s j M (T ++ G) q)))

/-- `separates` with the witness's completion and the other side's completions given. -/
def separatesWith {α : Type} [DecidableEq α] (D : Doc) (s : String) (i j : Nat) (σ : Situation α)
    (valid : Bool) (value : Option Bool) (others : List (Bool × Thunk (Option Bool))) : Bool :=
  situationWF D s i j σ && valid && value == some σ.value && decide (cells D s j σ.base ≤ maxCells) &&
  others.all (fun o => !(o.1 && o.2.get == some σ.value))

theorem separatesWith_eq {α : Type} [DecidableEq α] (D : Doc) (s : String) (i j : Nat) (σ : Situation α) :
    separatesWith D s i j σ (sideValid D s i σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)))
      (sideValue D s i σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)) σ.probe)
      (completions D s j σ.base (tablesFor D s j σ.fixed) σ.probe) = separates D s i j σ := by
  simp only [separatesWith, separates, completions, List.all_map, Function.comp_def]
  rfl

theorem assignments_of_ownedKeys_nil {α : Type} [DecidableEq α] (D : Doc) (s : String) (j : Nat)
    (M : VE.FiniteModel α) (h : ownedKeys D s j = []) : assignments D s j M = [[]] := by
  unfold assignments
  rw [h]
  rfl

/-- The facts of one pair, each side's completion evaluated once (plan F5b): the witness's for `separates` and for
    its two fields, the other side's for `separates`, `other_admissible` and `other_value`. -/
def pairFacts (a : Admitted) (s : String) (sid other : String) : Except String PairFacts := do
  let (r, sj) ← replayPair a s sid other
  let M := r.σ.base
  let Ti := tablesFor r.D s r.witness (r.σ.fixed ++ r.σ.decisions)
  if cells r.D s r.other M > maxCells then throw "ResourceLimit: decision assignments"
  let Tj := tablesFor r.D s r.other r.σ.fixed
  let valid := sideValid r.D s r.witness M Ti
  let value := sideValue r.D s r.witness M Ti r.σ.probe
  let others := completions r.D s r.other M Tj r.σ.probe
  pure ⟨r, sj.witness, separatesWith r.D s r.witness r.other r.σ valid value others, valid, value,
    others.any (·.1),
    if ownedKeys r.D s r.other = [] then (others.head?.map (·.2.get)).getD none else none⟩

theorem pairFacts_eq (a : Admitted) (s : String) (sid other : String) :
    pairFacts a s sid other = pairFactsSpec a s sid other := by
  unfold pairFacts pairFactsSpec
  simp only [bind, Except.bind]
  split
  · rfl
  · rename_i v _
    obtain ⟨r, sj⟩ := v
    dsimp only
    split
    · rfl
    · rw [separatesWith_eq]
      have hany : (completions r.D s r.other r.σ.base (tablesFor r.D s r.other r.σ.fixed) r.σ.probe).any (·.1) =
          (assignments r.D s r.other r.σ.base).any
            (fun G => sideValid r.D s r.other r.σ.base (tablesFor r.D s r.other r.σ.fixed ++ G)) := by
        simp only [completions, List.any_map, Function.comp_def]
      rw [hany]
      by_cases ho : ownedKeys r.D s r.other = []
      · simp only [ho, if_true, completions, assignments_of_ownedKeys_nil _ _ _ _ ho, List.map_cons, List.map_nil,
          List.head?_cons, Option.map_some, Option.getD_some, List.append_nil]
        rfl
      · simp only [ho, if_false]

/-! ### Each candidate's layers computed once per set (plan F5d) -/

/-- `completions` from candidate j's side. -/
def completionsOn {α : Type} [DecidableEq α] (D : Doc) (s : String) (j : Nat) (P : Side) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) (q : Probe α) : List (Bool × Thunk (Option Bool)) :=
  (assignmentsOn D s j P M).map (fun G => (sideValidOn P M (T ++ G), Thunk.mk (fun _ => sideValueOn P M (T ++ G) q)))

theorem completionsOn_sideOf {α : Type} [DecidableEq α] (D : Doc) (s : String) (j : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) (q : Probe α) :
    completionsOn D s j (sideOf D s j) M T q = completions D s j M T q := by
  simp only [completionsOn, completions, assignmentsOn_sideOf, sideValidOn_sideOf, sideValueOn_sideOf]

/-- A replay is of the admitted document and the requested set. -/
theorem replayPair_doc {a : Admitted} {s sid other : String} {r : SeparateReplay} {sj : SituationJ}
    (h : replayPair a s sid other = .ok (r, sj)) : r.D = a.D ∧ r.set = s := by
  unfold replayPair at h
  simp only [bind, Except.bind] at h
  repeat' (first | (split at h) | (cases h; exact ⟨rfl, rfl⟩))
  all_goals (first | (cases h) | skip)

/-- `pairFacts` with each side's completions read from `side`, candidate i's side `side i`. -/
def pairFactsIn (a : Admitted) (side : Nat → Side) (s : String) (sid other : String) : Except String PairFacts := do
  let (r, sj) ← replayPair a s sid other
  let M := r.σ.base
  let Pi := side r.witness
  let Pj := side r.other
  let Ti := tablesFor r.D s r.witness (r.σ.fixed ++ r.σ.decisions)
  if cellsOn r.D s r.other Pj M > maxCells then throw "ResourceLimit: decision assignments"
  let Tj := tablesFor r.D s r.other r.σ.fixed
  let valid := sideValidOn Pi M Ti
  let value := sideValueOn Pi M Ti r.σ.probe
  let others := completionsOn r.D s r.other Pj M Tj r.σ.probe
  pure ⟨r, sj.witness, separatesWith r.D s r.witness r.other r.σ valid value others, valid, value,
    others.any (·.1),
    if ownedKeys r.D s r.other = [] then (others.head?.map (·.2.get)).getD none else none⟩

theorem pairFactsIn_eq (a : Admitted) (side : Nat → Side) (s : String) (sid other : String)
    (h : ∀ i, side i = sideOf a.D s i) : pairFactsIn a side s sid other = pairFacts a s sid other := by
  unfold pairFactsIn pairFacts
  simp only [bind, Except.bind]
  split
  · rfl
  · rename_i v hr
    obtain ⟨r, sj⟩ := v
    have hD := (replayPair_doc hr).1
    simp only [h, ← hD, cellsOn_sideOf, sideValidOn_sideOf, sideValueOn_sideOf, completionsOn_sideOf]

/-- Every candidate's side of set `s`, each built when first read. -/
def sidesOf (D : Doc) (s : String) (n : Nat) : List (Thunk Side) :=
  (List.range n).map (fun i => Thunk.mk (fun _ => sideOf D s i))

def sideAt (D : Doc) (s : String) (sides : List (Thunk Side)) (i : Nat) : Side :=
  match sides[i]? with
  | some t => t.get
  | none => sideOf D s i

theorem sideAt_sidesOf (D : Doc) (s : String) (n i : Nat) : sideAt D s (sidesOf D s n) i = sideOf D s i := by
  unfold sideAt sidesOf
  by_cases hi : i < n
  · simp [hi, Thunk.get]
  · simp [hi]

def pairJson (f : PairFacts) (sid : String) : Json :=
  Json.mkObj ([("situation", .str sid), ("witness", .str f.witnessName), ("separated", .bool f.separated),
    ("witness_admissible", .bool f.witnessValid), ("witness_value", optBool f.witnessValue),
    ("other_admissible", .bool f.otherAdmissible)] ++
    (if ownedKeys f.replay.D f.replay.set f.replay.other = [] then [("other_value", optBool f.otherValue)] else []))

/-- 4.5 for every pair of a set, neither pending, in index order: each must be separated by its situation. As
    specified: each pair builds both sides' layers. -/
def setPairsSpec (a : Admitted) (R : ReadingSet) (RJ : SetJ) : Except String (List Json) := do
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

/-- `setPairsSpec` with each candidate's side built once for the set (plan F5d, `setPairs_eq`). -/
def setPairs (a : Admitted) (R : ReadingSet) (RJ : SetJ) : Except String (List Json) := do
  let sides := sidesOf a.D R.id R.candidates.length
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
      let f ← pairFactsIn a (sideAt a.D R.id sides) R.id sid otherName
      unless f.witnessValid do throw "distinguishing model violates a generated premise"
      unless f.separated do throw "distinguishing model does not separate readings"
      out := out ++ [Json.mkObj [("reading", .str x.id), ("other", .str y.id), ("pair", pairJson f sid)]]
  pure out

theorem setPairs_eq (a : Admitted) (R : ReadingSet) (RJ : SetJ) : setPairs a R RJ = setPairsSpec a R RJ := by
  have h : ∀ sid other, pairFactsIn a (sideAt a.D R.id (sidesOf a.D R.id R.candidates.length)) R.id sid other =
      pairFacts a R.id sid other := fun sid other => pairFactsIn_eq a _ R.id sid other (sideAt_sidesOf a.D R.id _)
  simp only [setPairs, setPairsSpec, h]

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
    let f ← pairFactsIn a (sideOf a.D s) s sid (← stringField j "other")
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
