import VE.Readings.Wire
import VE.Readings.Scan
import VE.Readings.SupRun
import VE.Readings.UnspecifiedWire
import VE.Readings.Companions
import VE.NormDefaults.Run
import VE.Rights.Run

/-! The `ve_service` mode `readings-route` (docs/spec/composition-s1.md 8.4), formerly the one-shot `ve_readings_route`. Each case is `{"id", "kind", "environment", "document",
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
* The case kinds of S2a (`readings-elaborate`, `readings-conflict`, `readings-certificate`, `readings-model`,
  `readings-dead`, `readings-choice`): `SupRun.lean` (docs/spec/composition-s2.md 3).
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

/-! ### Each candidate's layers computed once per set (plan F5d), the other side scanned lazily (`pairEval`,
    `Scan.lean`) -/

/-- A replay is of the admitted document and the requested set. -/
theorem replayPair_doc {a : Admitted} {s sid other : String} {r : SeparateReplay} {sj : SituationJ}
    (h : replayPair a s sid other = .ok (r, sj)) : r.D = a.D ∧ r.set = s := by
  unfold replayPair at h
  simp only [bind, Except.bind] at h
  repeat' (first | (split at h) | (cases h; exact ⟨rfl, rfl⟩))
  all_goals (first | (cases h) | skip)

/-- The facts of one pair, candidate i's side read from `side i` (plan F5d): the bound on the other side's cells,
    then `pairEval` in `Id`. -/
def pairFactsIn (a : Admitted) (side : Nat → Side) (s : String) (sid other : String) : Except String PairFacts := do
  let (r, sj) ← replayPair a s sid other
  let Pj := side r.other
  if cellsOn r.D s r.other Pj r.σ.base > maxCells then throw "ResourceLimit: decision assignments"
  let (sep, valid, value, oa, ov) :=
    pairEval (m := Id) (pure ()) (pure ()) r.D s r.witness r.other (side r.witness) Pj r.σ
  pure ⟨r, sj.witness, sep, valid, value, oa, ov⟩

theorem pairFactsIn_eq (a : Admitted) (side : Nat → Side) (s : String) (sid other : String)
    (h : ∀ i, side i = sideOf a.D s i) : pairFactsIn a side s sid other = pairFactsSpec a s sid other := by
  unfold pairFactsIn pairFactsSpec
  simp only [bind, Except.bind]
  split
  · rfl
  · rename_i v hr
    obtain ⟨r, sj⟩ := v
    obtain ⟨hD, hS⟩ := replayPair_doc hr
    simp only [h, ← hD, hS, cellsOn_sideOf]
    split
    · rfl
    · rename_i hc
      rw [pairEval_id _ _ _ _ _ (Nat.le_of_not_gt hc)]

/-- Candidate i of set s's side, its document read from the request's table (plan F5b), so not built again. -/
def sideIn (a : Admitted) (s : String) (i : Nat) : Side := sideOfDoc (a.side s i)

theorem sideIn_eq (a : Admitted) (s : String) (i : Nat) : sideIn a s i = sideOf a.D s i := by
  simp only [sideIn, sideOf, Admitted.side_eq]

/-- Every candidate's side of set `s`, each built when first read. -/
def sidesOf (a : Admitted) (s : String) (n : Nat) : List (Thunk Side) :=
  (List.range n).map (fun i => Thunk.mk (fun _ => sideIn a s i))

def sideAt (a : Admitted) (s : String) (sides : List (Thunk Side)) (i : Nat) : Side :=
  match sides[i]? with
  | some t => t.get
  | none => sideIn a s i

theorem sideAt_sidesOf (a : Admitted) (s : String) (n i : Nat) : sideAt a s (sidesOf a s n) i = sideOf a.D s i := by
  unfold sideAt sidesOf
  by_cases hi : i < n
  · simp [hi, Thunk.get, sideIn_eq]
  · simp [hi, sideIn_eq]

def pairJson (f : PairFacts) (sid : String) : Json :=
  Json.mkObj ([("situation", .str sid), ("witness", .str f.witnessName), ("separated", .bool f.separated),
    ("witness_admissible", .bool f.witnessValid), ("witness_value", optBool f.witnessValue),
    ("other_admissible", .bool f.otherAdmissible)] ++
    (if ownedKeysOf f.replay.D f.replay.set f.replay.other f.replay.Xj.1 = [] then [("other_value", optBool f.otherValue)]
     else []))

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
      let f ← pairFactsSpec a R.id sid otherName
      unless f.witnessValid do throw "distinguishing model violates a generated premise"
      unless f.separated do throw "distinguishing model does not separate readings"
      out := out ++ [Json.mkObj [("reading", .str x.id), ("other", .str y.id), ("pair", pairJson f sid)]]
  pure out

/-- `setPairsSpec` with each candidate's side built once for the set (plan F5d, `setPairs_eq`), each pair's facts
    read through `adjust` (`id` here; under the unspecified completion `ndPairFacts`, readings-defaults.md 4.2). -/
def setPairsWith (adjust : PairFacts → PairFacts) (a : Admitted) (R : ReadingSet) (RJ : SetJ) :
    Except String (List Json) := do
  let sides := sidesOf a R.id R.candidates.length
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
      let f := adjust (← pairFactsIn a (sideAt a R.id sides) R.id sid otherName)
      unless f.witnessValid do throw "distinguishing model violates a generated premise"
      unless f.separated do throw "distinguishing model does not separate readings"
      out := out ++ [Json.mkObj [("reading", .str x.id), ("other", .str y.id), ("pair", pairJson f sid)]]
  pure out

def setPairs (a : Admitted) (R : ReadingSet) (RJ : SetJ) : Except String (List Json) := setPairsWith id a R RJ

theorem setPairs_eq (a : Admitted) (R : ReadingSet) (RJ : SetJ) : setPairs a R RJ = setPairsSpec a R RJ := by
  have h : ∀ sid other, pairFactsIn a (sideAt a R.id (sidesOf a R.id R.candidates.length)) R.id sid other =
      pairFactsSpec a R.id sid other := fun sid other => pairFactsIn_eq a _ R.id sid other (sideAt_sidesOf a R.id _)
  simp only [setPairs, setPairsWith, setPairsSpec, h, id]

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

def validateResultWith (adjust : PairFacts → PairFacts) (a : Admitted) : Except String (List (String × Json)) := do
  let sets := a.D.sets.filter contentBearing
  if sets.isEmpty then return [("content_bearing", .bool false)]
  let mut rows : List Json := []
  for R in sets do
    let some RJ := setJ a.doc R.id | throw invalidSet
    let cands ← (List.range R.candidates.length).mapM (candidateJson a R)
    let pairs ← setPairsWith adjust a R RJ
    rows := rows ++ [Json.mkObj [("set", .str R.id), ("version", toJson R.version),
      ("candidates", Json.arr cands.toArray), ("pairs", Json.arr pairs.toArray),
      ("findings", toJson (setFindings a R))]]
  pure [("content_bearing", .bool true), ("sets", Json.arr rows.toArray)]

def validateResult (a : Admitted) : Except String (List (String × Json)) := validateResultWith id a

/-! ## Under the unspecified completion (readings-defaults.md 3, 4.2; plan RD-2a) -/

/-- The facts of a pair read under the completion: the witness is admissible only when its `Fill_T` holds on the base
    (4.2; else `distinguishing model violates a generated premise`), its document read from the request's table
    (`fillHoldsOf_eq`). `separated` is the scan's on the filled document, which is `separates (fillDoc N)`
    (`separates_filled`), the hypothesis of `readings_wire_nd_separate_sound`. -/
def ndPairFacts (f : AdmittedNDFull) (p : PairFacts) : PairFacts :=
  { p with witnessValid := p.witnessValid &&
      fillHoldsOf f.r.N (f.r.b.a.side p.replay.set p.replay.witness).1 p.replay.σ.base }

/-- `readings-validate` under the completion: S1's rows on the filled document, then `fill_premises` per reading and
    `filled` once (3). -/
def runValidateND (id : String) (f : AdmittedNDFull) : Except String Json := do
  let rows ← validateResultWith (ndPairFacts f) f.fa.a
  pure (VE.Route.Wire.ok id (rows ++ [("fill_premises", fillPremisesJson f.r.N f.r.b.a.side),
    ("filled", ← filledJson f.r)]))

/-- `readings-separate` under the completion: S1's pair on the filled document (`replaySeparateU`'s replay). -/
def runSeparateND (id : String) (f : AdmittedNDFull) (j : Json) : Except String Json := do
  let s ← stringField j "set"
  let sid ← stringField j "situation"
  let p ← pairFactsIn f.fa.a (sideIn f.fa.a s) s sid (← stringField j "other")
  pure (VE.Route.Wire.ok id [("set", .str s), ("pair", pairJson (ndPairFacts f p) sid)])

/-- The S2a kinds under the completion: elaborate and choice as `UnspecifiedWire.lean` answers them, dead as today
    (it reads no rule), and the superposed kinds refused until RD-6. A document of such an environment without a
    content-bearing set, or of any other environment, is today's (S1 4.9). `b` is the case's one admission. -/
def runS2ND (lower : List String → Json → Json) (id kind : String) (b : Admitted2) (j : Json) : Except String Json := do
  if !underCompletion b.a.re b.D then return ← runS2 lower id kind b j
  let f ← admitNDFull b
  if kind == "readings-elaborate" then return ← runElaborateND id f.r
  if kind == "readings-choice" then return ← runChoiceND id f.r j
  if kind == "readings-dead" then return ← deadAnswer id f.r.N.D j
  throw (completionRefusal f.r.N.D)

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

/-- A case of the lower route named by `dispatch` on the profiles without `readings@1`. -/
def runLowerWith (lower : List String) (j : Json) : Json :=
  match VE.Compose.dispatch lower with
  | .ok .rights => VE.Rights.Run.runCaseReported j
  | .ok .soft => VE.SoftNorms.Run.runCaseReported j
  | .ok .normDefaults => VE.NormDefaults.Run.runCaseReported j
  | _ => VE.Norms.Run.runCaseReported j

/-- `readings-validate` on one case of the split: S1's admission, continued by the completion's where it applies. -/
def validateOne (id : String) (environment document : Json) : Except String Json := do
  let a ← admitReadings environment document
  if underCompletion a.re a.D then
    return ← runValidateND id (← admitNDFull (← admitS2Of a document))
  return VE.Route.Wire.ok id (← validateResult a)

/-- `readings-elaborate` on one case of the split (`runS2ND`'s dispatch). -/
def elaborateOne (j : Json) (id : String) (environment document : Json) : Except String Json := do
  runS2ND runLowerWith id "readings-elaborate" (← admitS2 environment document) j

/-- Every readings kind on one case of the split admits that case's document once: S1's `admitReadings`, continued
    by S2a's admission (`admitS2Of`) and the completion's (`admitNDFull`) where the kind reads them. -/
def runOne (j : Json) (id kind : String) (environment document : Json) : Except String Json := do
  if kind == "readings-validate" then return ← validateOne id environment document
  if kind == "readings-separate" then
    let a ← admitReadings environment document
    if underCompletion a.re a.D then
      return ← runSeparateND id (← admitNDFull (← admitS2Of a document)) j
    let s ← stringField j "set"
    let sid ← stringField j "situation"
    let f ← pairFactsIn a (sideIn a s) s sid (← stringField j "other")
    return VE.Route.Wire.ok id [("set", .str s), ("pair", pairJson f sid)]
  if s2Kinds.contains kind then
    return ← runS2ND runLowerWith id kind (← admitS2 environment document) j
  throw s!"UnsupportedProfile: case kind {kind} is not available on the readings route"

def unknownComponent (c : String) : String :=
  s!"InvalidInput: component {c} is not main or a reading set with its own vocabulary"

/-- The `component` a kind names (readings-defaults.md 3): `main` when absent. -/
def componentOfCase (j : Json) : Except String (Option String) :=
  match j.getObjVal? "component" with
  | .ok (.str c) => pure (some c)
  | .ok _ => throw (unknownComponent "")
  | .error _ => pure none

def componentRow (name : String) (answer : Json) : Json :=
  Json.mkObj [("component", .str name), ("answer", answer)]

/-- The last admission stage needed by a readings kind. Each constructor retains the admitted document for the
    answer, so no component is decoded or admitted again after the whole split has passed admission. -/
inductive ComponentAdmission where
  | s1 (a : Admitted)
  | s2 (b : Admitted2)
  | nd (f : AdmittedNDFull)

/-- Admit a component without running a query on it. Admission of the split runs in source order before dispatch. -/
def admitComponent (kind : String) (environment document : Json) : Except String ComponentAdmission := do
  if kind == "readings-validate" || kind == "readings-separate" then
    let a ← admitReadings environment document
    if underCompletion a.re a.D then
      return .nd (← admitNDFull (← admitS2Of a document))
    return .s1 a
  let b ← admitS2 environment document
  if underCompletion b.a.re b.D then
    return .nd (← admitNDFull b)
  return .s2 b

/-- One answer from its already admitted component. The request fields are read only for the named component. -/
def runAdmitted (j : Json) (id kind : String) (ready : ComponentAdmission) : Except String Json := do
  if kind == "readings-validate" then
    match ready with
    | .s1 a => return VE.Route.Wire.ok id (← validateResult a)
    | .nd f => return ← runValidateND id f
    | .s2 b => return VE.Route.Wire.ok id (← validateResult b.a)
  if kind == "readings-separate" then
    match ready with
    | .nd f => return ← runSeparateND id f j
    | .s1 a | .s2 ⟨a, _, _, _⟩ =>
      let s ← stringField j "set"
      let sid ← stringField j "situation"
      let f ← pairFactsIn a (sideIn a s) s sid (← stringField j "other")
      return VE.Route.Wire.ok id [("set", .str s), ("pair", pairJson f sid)]
  match ready with
  | .s2 b => runS2 runLowerWith id kind b j
  | .nd f =>
    if kind == "readings-elaborate" then return ← runElaborateND id f.r
    if kind == "readings-choice" then return ← runChoiceND id f.r j
    if kind == "readings-dead" then return ← deadAnswer id f.r.N.D j
    throw (completionRefusal f.r.N.D)
  | .s1 _ => throw s!"UnsupportedProfile: case kind {kind} is not available on the readings route"

def admitComponents (kind : String) (parts : List (String × Json × Json)) : Except String (List (String × ComponentAdmission)) :=
  parts.mapM (fun p => do pure (p.1, ← admitComponent kind p.2.1 p.2.2))

def runAdmittedComponents (j : Json) (id kind : String) (parts : List (String × ComponentAdmission)) :
    Except String Json := do
  let rows ← parts.mapM (fun p => do pure (componentRow p.1 (← runAdmitted j id kind p.2)))
  pure (VE.Route.Wire.ok id [("components", Json.arr rows.toArray)])

/-- `readings-validate` or `readings-elaborate` per case of the split, `main` first (4.1 step 0): the first error
    of any case is the answer. -/
def runComponents (j : Json) (id kind : String) (parts : List (String × Json × Json)) : Except String Json := do
  let rows ← parts.mapM (fun p => do
    let a ← if kind == "readings-validate" then validateOne id p.2.1 p.2.2 else elaborateOne j id p.2.1 p.2.2
    pure (componentRow p.1 a))
  pure (VE.Route.Wire.ok id [("components", Json.arr rows.toArray)])

/-- Every readings kind first splits the case (readings-defaults.md 3, `splitCase`). A document without companion
    sets is one case, `main`, run as before. Otherwise `readings-validate` and `readings-elaborate` answer per
    case unless the request names a `component`, and every other kind runs on the case it names (`main` when it
    names none). -/
def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  unless kind == "readings-validate" || kind == "readings-separate" || s2Kinds.contains kind do
    throw s!"UnsupportedProfile: case kind {kind} is not available on the readings route"
  let environment ← j.getObjVal? "environment"
  let document ← j.getObjVal? "document"
  let parts ← splitCase environment document
  let named ← componentOfCase j
  if parts.length > 1 then
    let ready ← admitComponents kind parts
    if named.isNone && (kind == "readings-validate" || kind == "readings-elaborate") then
      return ← runAdmittedComponents j id kind ready
    let c := named.getD "main"
    match ready.find? (·.1 == c) with
    | some p => return ← runAdmitted j id kind p.2
    | none => throw (unknownComponent c)
  let c := named.getD "main"
  match parts.find? (·.1 == c) with
  | some p => runOne j id kind p.2.1 p.2.2
  | none => throw (unknownComponent c)

def runCaseReported (j : Json) : Json :=
  match VE.Route.Run.caseKind j with
  | .ok k =>
    if k == "readings-validate" || k == "readings-separate" || s2Kinds.contains k then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]
    else runLower j
  | _ => runLower j

end VE.Readings.Run
