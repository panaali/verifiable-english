import VE.Defaults.Zone
import VE.Defaults.Wire

/-! The `defaults-zone` kind (docs/spec/defeasible.md 3.8 and 4; plan 2.7, batch DF-5): the zone of an outcome at a
tuple of one finite situation, with weighing's record and the observed outcomes, by df-5a's `defaultZoneOf`, with
DE10's form (`zoneFormOf`), `forcedAllOf` and the rows that follow DE10 (DE11, DE10f, DE13).

The request names a situation (`model`, `situationX`), a `record` of decisions by key (`decisionKeyJson`), the
`observations` and the `query` (an outcome and a tuple). Lean selects every English row; Python renders them. -/
namespace VE.Defaults.Wire
open Lean
open VE.Defaults
open VE.Bridge (Entity)
open VE.SoftNorms (DecisionKey keyedDecisions)
open VE.NormDefaults.Wire (LayeredU)

/-- At most this many observed outcomes are read; each is checked on every assignment (the evaluator rule). -/
def maxZoneObservations : Nat := 1024

/-- A decision by its key: `{"excepted": r}`, `{"off": r, "party": π}` or `{"outweighs": a, "lower": L,
    "higher": H}`, one of the document's `keyedDecisions`, with its predicate name and sorts. -/
def decisionOf (L : LayeredU) (j : Json) : Except String (DecisionKey × String × List String) := do
  let s (k : String) : Except String String := do (← j.getObjVal? k).getStr?
  let names := (← VE.Bridge.fields j).map (·.1)
  let k : DecisionKey ←
    if names == ["excepted"] then .excepted <$> s "excepted"
    else if names == ["off", "party"] then .off <$> s "off" <*> s "party"
    else if names == ["higher", "lower", "outweighs"] then .outweighs <$> s "outweighs" <*> s "lower" <*> s "higher"
    else throw "InvalidInput: a decision is named by excepted, by off and party, or by outweighs, lower and higher"
  match (keyedDecisions L.D).find? (·.1 == k) with
  | some e => pure e
  | none => throw "InvalidInput: the record names a decision the document does not have"

/-- A regulated outcome of the document by name. -/
def outcomeOf (L : LayeredU) (j : Json) : Except String VE.Norms.Regulated := do
  let n ← (← j.getObjVal? "outcome").getStr?
  match L.U.D.T.regulated.find? (·.name == n) with
  | some r => pure r
  | none => throw s!"InvalidInput: {n} is not a regulated outcome of the document"

def tupleIn (M : VE.FiniteModel Entity) (sorts : List String) (j : Json) : Except String (List Entity) :=
  (·.val) <$> VE.NormDefaults.Wire.tupleOf M sorts (j.getObjValD "tuple")

structure ZoneReplay where
  v : DefaultsView
  S : VE.NormDefaults.Wire.SituationG v.L.U
  record : List ((String × List Entity) × Bool)
  obs : List ((VE.Norms.Regulated × List Entity) × Bool)
  r : VE.Norms.Regulated
  vs : List Entity

def ZoneReplay.X (x : ZoneReplay) : List (String × VE.Formula) := VE.NormDefaults.Packs.labelledX x.v.L.packs

/-- The zone (`defaultZoneOf`); past `maxZoneObservations` observed outcomes, `unknown` before anything is listed. -/
def ZoneReplay.zone (x : ZoneReplay) : DefaultZone Entity :=
  if maxZoneObservations < x.obs.length then .unknown (.branch [] "observations size") else
  defaultZoneOf x.v.L x.X x.S.M x.record x.obs x.r x.vs []

def replayZoneOn (v : DefaultsView) (j : Json) : Except String ZoneReplay := do
  let S ← VE.NormDefaults.Wire.situationX v.L (← j.getObjVal? "model")
  let record ← (← (← j.getObjVal? "record").getArr?).toList.mapM fun e => do
    VE.Bridge.exactFields e ["decision", "tuple", "value"]
    let (_, n, ss) ← decisionOf v.L (← e.getObjVal? "decision")
    pure ((n, ← tupleIn S.M ss e), ← (← e.getObjVal? "value").getBool?)
  let obs ← (← (← j.getObjVal? "observations").getArr?).toList.mapM fun e => do
    VE.Bridge.exactFields e ["outcome", "tuple", "value"]
    let r ← outcomeOf v.L e
    pure ((r, ← tupleIn S.M (VE.NormDefaults.sortsOf v.L.U.D r.name) e), ← (← e.getObjVal? "value").getBool?)
  let q ← j.getObjVal? "query"
  VE.Bridge.exactFields q ["outcome", "tuple"]
  let r ← outcomeOf v.L q
  pure ⟨v, S, record, obs, r, ← tupleIn S.M (VE.NormDefaults.sortsOf v.L.U.D r.name) q⟩

/-! ## The rows after DE10 -/

/-- One true decision of the completion shown, as DE10 lists it: DE11 when a stated sufficient condition of the
    rule's exception holds there (its index), DE10f when `forcedAll` lists it, DE13 otherwise. -/
inductive ZoneLine
  | stated (rule : String) (condition : Nat) (vs : List Entity)
  | forced (rule : String) (vs : List Entity)
  | assumed (k : DecisionKey) (vs : List Entity)

/-- The true decisions of the completion `w` (the record's, the switches off, and `w`'s enumerated atoms), in
    `keyedDecisions` order then tuple order, each with its row. -/
def zoneLines (x : ZoneReplay) (forced : List (String × List Entity)) (w : List ((String × List Entity) × Bool)) :
    List ZoneLine :=
  let L := x.v.L
  let rec' := x.record ++ switchesOffRecord L.D x.S.M x.record
  let A := w.filterMap (fun e => if e.2 then some e.1 else none)
  let V := VE.NormDefaults.coneAtomVX x.S.M (VE.Weighing.openNames L) rec' (w.map (·.1)) A
  (keyedDecisions L.D).flatMap fun (k, n, ss) => (VE.NormDefaults.allTuples x.S.M ss).filterMap fun vs =>
    if V n vs != some true then none else
    match k with
    | .excepted rule =>
      let conds := ((L.D.T.nodes.find? (·.name == rule)).bind (·.exception)).map (·.sufficient) |>.getD []
      match conds.findIdx? (fun C => VE.NormDefaults.kleene x.S.M V (VE.Norms.tupleVal vs) C == some true) with
      | some i => some (.stated rule i vs)
      | none => some (if forced.contains (n, vs) then .forced rule vs else .assumed k vs)
    | _ => some (.assumed k vs)

def ZoneLine.json : ZoneLine → Json
  | .stated r i vs => Json.mkObj [("row", .str "DE11"), ("rule", .str r), ("condition", toJson i), ("tuple", entityIds vs)]
  | .forced r vs => Json.mkObj [("row", .str "DE10f"), ("rule", .str r), ("tuple", entityIds vs)]
  | .assumed k vs => Json.mkObj [("row", .str "DE13"), ("decision", VE.SoftNorms.Wire.decisionKeyJson k),
      ("tuple", entityIds vs)]

/-- The rule of an exception atom, by its key (`keyedDecisions`), for `forced_all`. -/
def exceptedRule (D : VE.SoftNorms.SoftDoc) (n : String) : String :=
  match (keyedDecisions D).find? (·.2.1 == n) with
  | some (.excepted r, _) => r
  | _ => n

/-- The answer: the zone; with `by default` or `left to`, DE10's form, `forced_all` and the completions shown (one,
    or the two that differ), each a list of rows. `forcedAllOf` and `zoneFormOf` are read only for those two zones,
    which come from a complete, nonempty enumeration; were either `none` there, the answer is `unknown`. -/
def zoneFields (x : ZoneReplay) : List (String × Json) :=
  let unknownF (why : String) : List (String × Json) := [("zone", .str "unknown"), ("reason", .str why)]
  let shown (tag : String) (value : List (String × Json)) (ws : List (List ((String × List Entity) × Bool))) :
      List (String × Json) :=
    match zoneFormOf x.v.L x.S.M x.record, forcedAllOf x.v.L x.X x.S.M x.record x.obs [] with
    | some f, some fs =>
      [("zone", .str tag)] ++ value ++
      [("form", .str (formLabel f)),
       ("forced_all", Json.arr (fs.map (fun (n, vs) => Json.mkObj [("rule", .str (exceptedRule x.v.L.D n)),
          ("tuple", entityIds vs)])).toArray),
       ("completions", Json.arr (ws.map (fun w => Json.arr ((zoneLines x fs w).map ZoneLine.json).toArray)).toArray)]
    | _, _ => unknownF "size"
  match x.zone with
  | .byDefault b w => shown "byDefault" [("value", .bool b)] [w]
  | .leftTo _ w₁ w₂ => shown "leftTo" [] [w₁, w₂]
  | .notSaid _ _ => [("zone", .str "notSaid")]
  | .noCompletion l => [("zone", .str "noCompletion"), ("labels", toJson l)]
  | .unknown (.budget n k) => unknownF s!"budget: {n} open atoms, over {k}"
  | .unknown (.branch _ why) => unknownF why

/-- `defaults-zone`, then the other `defaults-*` kinds (`defaultsCase`). -/
def zoneCase (v : DefaultsView) (id kind : String) (j : Json) : Except String (Option Json) :=
  if kind == "defaults-zone" then (fun x => some (VE.Route.Wire.ok id (zoneFields x))) <$> replayZoneOn v j
  else defaultsCase v id kind j

end VE.Defaults.Wire
