import VE.Defaults.Zone
import VE.Defaults.Wire

/-! The `defaults-zone` kind (docs/spec/defeasible.md 3.8 and 4; plan 2.7, batch DF-5): the zone of an outcome at a
tuple of one finite situation, with weighing's record and the observed outcomes, by df-5a's `defaultZoneOf`, with
DE10's form (`zoneFormOf`), `forcedAllOf` (both from one `zoneMin`) and the rows that follow DE10 (DE11, DE10f, DE13).

The request names a situation (`model`, `situationX`), a `record` of decisions by key (`decisionKeyJson`), the
`observations` and the `query` (an outcome and a tuple); the record's and the observations' sizes are charged before
any entry is decoded (`zoneSizes`). Each decoded value is bound to the request's field by a theorem: a decision to
its key's strings (`decisionOf_mem`), an outcome to its name (`outcomeOf_mem`), a tuple to its ids and sorts
(`tupleIn_typed`), an entry's value to its Bool (`recordEntry_sound`, `obsEntry_sound`), and the record and the
observations entry by entry in request order (`replayZoneOn_sound`). Lean selects every English row and owns its
words (`zoneHeads`, `zoneLineWords`, `zoneJoins`, generated into `ve/defaults_words.json`); Python fills their slots.
-/
namespace VE.Defaults.Wire
open Lean
open VE.Defaults
open VE.Bridge (Entity)
open VE.SoftNorms (DecisionKey keyedDecisions)
open VE.NormDefaults.Wire (LayeredU)

/-- At most this many observed outcomes are read; each is checked on every assignment (the evaluator rule). -/
def maxZoneObservations : Nat := 1024

/-- The charge on the sizes alone, before any record entry or observation is decoded (the evaluator rule): more than
    `maxZoneRecord` record entries is `zoneCharge`'s `record size` (`zoneSizes_record`), more than
    `maxZoneObservations` observed outcomes `observations size`. -/
def zoneSizes (record obs : Nat) : Option (DefaultZone Entity) :=
  if maxZoneRecord < record then some (.unknown (.branch [] "record size")) else
  if maxZoneObservations < obs then some (.unknown (.branch [] "observations size")) else none

/-- A decision by its key: `{"excepted": r}`, `{"off": r, "party": π}` or `{"outweighs": a, "lower": L,
    "higher": H}`, one of the document's `keyedDecisions` (`decisionOf_mem`), with its predicate name and sorts. -/
def decisionOf (L : LayeredU) (j : Json) : Except String (DecisionKey × String × List String) :=
  key >>= fun k => match (keyedDecisions L.D).find? (·.1 == k) with
    | some e => pure e
    | none => throw "InvalidInput: the record names a decision the document does not have"
where
  key : Except String DecisionKey := do
    let s (k : String) : Except String String := do (← j.getObjVal? k).getStr?
    let names := (← VE.Bridge.fields j).map (·.1)
    if names == ["excepted"] then .excepted <$> s "excepted"
    else if names == ["off", "party"] then .off <$> s "off" <*> s "party"
    else if names == ["higher", "lower", "outweighs"] then .outweighs <$> s "outweighs" <*> s "lower" <*> s "higher"
    else throw "InvalidInput: a decision is named by excepted, by off and party, or by outweighs, lower and higher"

/-- A regulated outcome of the document by the request's name (`outcomeOf_mem`). -/
def outcomeOf (L : LayeredU) (j : Json) : Except String VE.Norms.Regulated :=
  (j.getObjVal? "outcome" >>= Json.getStr?) >>= fun n => match L.U.D.T.regulated.find? (·.name == n) with
    | some r => pure r
    | none => throw s!"InvalidInput: {n} is not a regulated outcome of the document"

/-- The request's `tuple`, typed by `sorts` in the situation (`tupleIn_typed`). -/
def tupleIn (M : VE.FiniteModel Entity) (sorts : List String) (j : Json) : Except String (List Entity) :=
  (·.val) <$> VE.NormDefaults.Wire.tupleOf M sorts (j.getObjValD "tuple")

/-- A record entry: a decision of the document at a tuple of its sorts, with its value (`recordEntry_sound`). -/
def recordEntry (L : LayeredU) (M : VE.FiniteModel Entity) (e : Json) :
    Except String ((String × List Entity) × Bool) := do
  VE.Bridge.exactFields e ["decision", "tuple", "value"]
  let (_, n, ss) ← decisionOf L (← e.getObjVal? "decision")
  pure ((n, ← tupleIn M ss e), ← (← e.getObjVal? "value").getBool?)

/-- An observation: a regulated outcome at a tuple of its sorts, with its value (`obsEntry_sound`). -/
def obsEntry (L : LayeredU) (M : VE.FiniteModel Entity) (e : Json) :
    Except String ((VE.Norms.Regulated × List Entity) × Bool) := do
  VE.Bridge.exactFields e ["outcome", "tuple", "value"]
  let r ← outcomeOf L e
  pure ((r, ← tupleIn M (VE.NormDefaults.sortsOf L.U.D r.name) e), ← (← e.getObjVal? "value").getBool?)

/-- A decoded request: `early` is `zoneSizes`'s answer, and then `record` and `obs` are not decoded (empty). -/
structure ZoneReplay where
  v : DefaultsView
  S : VE.NormDefaults.Wire.SituationG v.L.U
  early : Option (DefaultZone Entity)
  record : List ((String × List Entity) × Bool)
  obs : List ((VE.Norms.Regulated × List Entity) × Bool)
  r : VE.Norms.Regulated
  vs : List Entity

def ZoneReplay.X (x : ZoneReplay) : List (String × VE.Formula) := VE.NormDefaults.Packs.labelledX x.v.L.packs

/-- The enumeration (`zoneMin`), read once by `zoneFields`: `zoneSizes`'s answer when it stopped the decoding
    (`ZoneReplay.min_ok`). -/
def ZoneReplay.min (x : ZoneReplay) : Except (DefaultZone Entity) (List (List (String × List Entity))) :=
  match x.early with
  | some z => .error z
  | none => zoneMin x.v.L x.X x.S.M x.record x.obs

/-- The request, in this order: the situation (its decision tables empty), the query, the sizes (`zoneSizes`), then
    each record entry and each observation (`replayZoneOn_sound`). -/
def replayZoneOn (v : DefaultsView) (j : Json) : Except String ZoneReplay := do
  let S ← VE.NormDefaults.Wire.situationX v.L (← j.getObjVal? "model")
  let _ ← (if (VE.SoftNorms.decisionNames v.L.D).any (fun n => !(S.M.relations n).isEmpty) then
    throw "InvalidInput: the situation's decision tables are empty; a fixed decision goes in the record"
    else pure () : Except String Unit)
  let q ← j.getObjVal? "query"
  VE.Bridge.exactFields q ["outcome", "tuple"]
  let r ← outcomeOf v.L q
  let vs ← tupleIn S.M (VE.NormDefaults.sortsOf v.L.U.D r.name) q
  let recordJ ← (← j.getObjVal? "record").getArr?
  let obsJ ← (← j.getObjVal? "observations").getArr?
  match zoneSizes recordJ.size obsJ.size with
  | some z => pure ⟨v, S, some z, [], [], r, vs⟩
  | none => pure ⟨v, S, none, ← recordJ.toList.mapM (recordEntry v.L S.M), ← obsJ.toList.mapM (obsEntry v.L S.M), r, vs⟩

/-! ## What the request's decoding gives (the ties of the decoders to the request) -/

theorem replayBind_ok {ε α β : Type} {x : Except ε α} {f : α → Except ε β} {b : β} (h : (x >>= f) = .ok b) :
    ∃ a, x = .ok a ∧ f a = .ok b := by
  cases x with
  | error e => cases h
  | ok a => exact ⟨a, rfl, h⟩

theorem replayGetStr_mapM : ∀ {l : List Json} {ids : List String}, l.mapM Json.getStr? = .ok ids → l = ids.map .str
  | [], ids, h => by cases h; rfl
  | x :: l, ids, h => by
    rw [List.mapM_cons] at h
    obtain ⟨y, hx, h⟩ := replayBind_ok h
    obtain ⟨ys, hl, h⟩ := replayBind_ok h
    cases h
    cases x <;> try (cases hx; done)
    cases hx
    simp [replayGetStr_mapM hl]

/-- The ids `strings` reads are the array's: it is their JSON (`toJson`, as `entityIds` writes them). -/
theorem replayStrings_eq {t : Json} {ids : List String} (h : VE.Bridge.strings t = .ok ids) : t = toJson ids := by
  unfold VE.Bridge.strings at h
  obtain ⟨arr, harr, h⟩ := replayBind_ok h
  cases t with
  | arr a =>
    obtain rfl : a = arr := by cases harr; rfl
    have := replayGetStr_mapM h
    show Json.arr a = Json.arr (ids.toArray.map toJson)
    congr 1
    apply Array.ext'
    simp [this]; intros; rfl
  | _ => cases harr

/-- The key the request names is its fields' (`decisionKeyJson`'s): each of the key's strings is the request's
    string at that field. -/
theorem decisionOf_key {j : Json} {k : DecisionKey} (h : decisionOf.key j = .ok k) :
    match (generalizing := false) k with
    | .excepted r => VE.Bridge.stringField j "excepted" = .ok r
    | .off r π => VE.Bridge.stringField j "off" = .ok r ∧ VE.Bridge.stringField j "party" = .ok π
    | .outweighs a lo hi => VE.Bridge.stringField j "outweighs" = .ok a ∧ VE.Bridge.stringField j "lower" = .ok lo ∧
        VE.Bridge.stringField j "higher" = .ok hi := by
  unfold decisionOf.key at h
  dsimp only at h
  obtain ⟨names, -, h⟩ := replayBind_ok h
  split at h
  · cases h1 : VE.Bridge.stringField j "excepted" <;> unfold VE.Bridge.stringField at h1 <;> rw [h1] at h <;>
      cases h; rfl
  · split at h
    · cases h1 : VE.Bridge.stringField j "off" <;> cases h2 : VE.Bridge.stringField j "party" <;>
        unfold VE.Bridge.stringField at h1 h2 <;> rw [h1, h2] at h <;> cases h; exact ⟨rfl, rfl⟩
    · split at h
      · cases h1 : VE.Bridge.stringField j "outweighs" <;> cases h2 : VE.Bridge.stringField j "lower" <;>
          cases h3 : VE.Bridge.stringField j "higher" <;>
          unfold VE.Bridge.stringField at h1 h2 h3 <;> rw [h1, h2, h3] at h <;> cases h; exact ⟨rfl, rfl, rfl⟩
      · cases h

/-- A decision the request names is one of the document's keyed decisions, the one of the request's key: each of
    its key's strings is the request's at that field (`decisionOf_key`). -/
theorem decisionOf_mem {L : LayeredU} {j : Json} {e : DecisionKey × String × List String}
    (h : decisionOf L j = .ok e) : e ∈ keyedDecisions L.D ∧ decisionOf.key j = .ok e.1 ∧
    match e.1 with
    | .excepted r => VE.Bridge.stringField j "excepted" = .ok r
    | .off r π => VE.Bridge.stringField j "off" = .ok r ∧ VE.Bridge.stringField j "party" = .ok π
    | .outweighs a lo hi => VE.Bridge.stringField j "outweighs" = .ok a ∧ VE.Bridge.stringField j "lower" = .ok lo ∧
        VE.Bridge.stringField j "higher" = .ok hi := by
  unfold decisionOf at h
  obtain ⟨k, hk, h⟩ := replayBind_ok h
  split at h
  · rename_i he; cases h
    have hk' : e.1 = k :=
      beq_iff_eq.mp (List.find?_some (p := fun x : DecisionKey × String × List String => x.1 == k) he)
    have hkey : decisionOf.key j = .ok e.1 := hk.trans (congrArg Except.ok hk'.symm)
    exact ⟨List.mem_of_find?_eq_some he, hkey, decisionOf_key hkey⟩
  · cases h

/-- An outcome the request names is a regulated outcome of the document, of the name the request gives. -/
theorem outcomeOf_mem {L : LayeredU} {j : Json} {r : VE.Norms.Regulated} (h : outcomeOf L j = .ok r) :
    r ∈ L.U.D.T.regulated ∧ ((j.getObjVal? "outcome") >>= Json.getStr?) = .ok r.name := by
  unfold outcomeOf at h
  obtain ⟨n, hn, h⟩ := replayBind_ok h
  split at h
  · rename_i hr; cases h
    have hname : r.name = n := beq_iff_eq.mp (List.find?_some (p := fun x : VE.Norms.Regulated => x.name == n) hr)
    exact ⟨List.mem_of_find?_eq_some hr, hn.trans (congrArg Except.ok hname.symm)⟩
  · cases h

/-- A tuple the request gives is the request's: its `tuple` is the tuple's ids (`entityIds`), each of the sort in
    `sorts` at its place, and the tuple is typed by `sorts` in the situation. -/
theorem tupleIn_typed {M : VE.FiniteModel Entity} {ss : List String} {j : Json} {vs : List Entity}
    (h : tupleIn M ss j = .ok vs) :
    VE.TupleTyped M.asStructure ss vs ∧ vs.map Prod.fst = ss ∧ j.getObjValD "tuple" = entityIds vs := by
  unfold tupleIn at h
  cases ht : VE.NormDefaults.Wire.tupleOf M ss (j.getObjValD "tuple") with
  | error e => rw [ht] at h; cases h
  | ok t =>
    rw [ht] at h; cases h
    refine ⟨(VE.NormDefaults.mem_allTuples M ss t.val).mp t.property, ?_⟩
    unfold VE.NormDefaults.Wire.tupleOf at ht
    obtain ⟨ids, hids, ht⟩ := replayBind_ok ht
    dsimp only at ht
    split at ht
    · rename_i hl; cases ht
      simp only [Bool.and_eq_true, beq_iff_eq] at hl
      refine ⟨List.map_fst_zip (by omega), ?_⟩
      rw [entityIds, List.map_snd_zip (by omega)]
      exact replayStrings_eq hids
    · cases ht

/-- A record entry is the request's: the keyed decision its `decision` names (`decisionOf_mem`: by the request's
    key), at its `tuple`'s ids (`entityIds`) of that decision's sorts, typed in the situation, with its `value`. -/
theorem recordEntry_sound {L : LayeredU} {M : VE.FiniteModel Entity} {e : Json} {a : (String × List Entity) × Bool}
    (h : recordEntry L M e = .ok a) :
    ∃ d k ss, e.getObjVal? "decision" = .ok d ∧ decisionOf L d = .ok (k, a.1.1, ss) ∧
      (k, a.1.1, ss) ∈ keyedDecisions L.D ∧ e.getObjValD "tuple" = entityIds a.1.2 ∧ a.1.2.map Prod.fst = ss ∧
      VE.TupleTyped M.asStructure ss a.1.2 ∧ ((e.getObjVal? "value") >>= Json.getBool?) = .ok a.2 := by
  unfold recordEntry at h
  obtain ⟨_, -, h⟩ := replayBind_ok h
  obtain ⟨d, hd, h⟩ := replayBind_ok h
  obtain ⟨⟨k, n, ss⟩, hk, h⟩ := replayBind_ok h
  obtain ⟨vs, hv, h⟩ := replayBind_ok h
  obtain ⟨vj, hvj, h⟩ := replayBind_ok h
  obtain ⟨b, hb, h⟩ := replayBind_ok h
  cases h
  obtain ⟨ht, hs, hj⟩ := tupleIn_typed hv
  exact ⟨d, k, ss, hd, hk, (decisionOf_mem hk).1, hj, hs, ht, by rw [hvj]; exact hb⟩

/-- An observation is the request's: the regulated outcome of its `outcome`'s name, at its `tuple`'s ids
    (`entityIds`) of the outcome's sorts, typed in the situation, with its `value`. -/
theorem obsEntry_sound {L : LayeredU} {M : VE.FiniteModel Entity} {e : Json}
    {a : (VE.Norms.Regulated × List Entity) × Bool} (h : obsEntry L M e = .ok a) :
    outcomeOf L e = .ok a.1.1 ∧ a.1.1 ∈ L.U.D.T.regulated ∧ ((e.getObjVal? "outcome") >>= Json.getStr?) = .ok a.1.1.name ∧
      e.getObjValD "tuple" = entityIds a.1.2 ∧ a.1.2.map Prod.fst = VE.NormDefaults.sortsOf L.U.D a.1.1.name ∧
      VE.TupleTyped M.asStructure (VE.NormDefaults.sortsOf L.U.D a.1.1.name) a.1.2 ∧
      ((e.getObjVal? "value") >>= Json.getBool?) = .ok a.2 := by
  unfold obsEntry at h
  obtain ⟨_, -, h⟩ := replayBind_ok h
  obtain ⟨r, hr, h⟩ := replayBind_ok h
  obtain ⟨vs, hv, h⟩ := replayBind_ok h
  obtain ⟨vj, hvj, h⟩ := replayBind_ok h
  obtain ⟨b, hb, h⟩ := replayBind_ok h
  cases h
  obtain ⟨ht, hs, hj⟩ := tupleIn_typed hv
  exact ⟨hr, (outcomeOf_mem hr).1, (outcomeOf_mem hr).2, hj, hs, ht, by rw [hvj]; exact hb⟩

/-- Past a size, the answer is the charge's: for the record exactly `zoneCharge`'s, whatever the situation. -/
theorem zoneSizes_record {L : LayeredU} {M : VE.FiniteModel Entity} {record : List ((String × List Entity) × Bool)}
    (n : Nat) (h : maxZoneRecord < record.length) : zoneSizes record.length n = zoneCharge L M record := by
  simp [zoneSizes, zoneCharge, h]

/-- Within the sizes, nothing is charged; past the observations' bound with the record within its own, the answer is
    `observations size`: with `zoneSizes_record`, each of `zoneSizes`'s answers. -/
theorem zoneSizes_none_iff (record obs : Nat) :
    zoneSizes record obs = none ↔ record ≤ maxZoneRecord ∧ obs ≤ maxZoneObservations := by
  unfold zoneSizes; by_cases h1 : maxZoneRecord < record <;> by_cases h2 : maxZoneObservations < obs <;> simp [h1, h2] <;> omega

theorem zoneSizes_observations {record obs : Nat} (hr : record ≤ maxZoneRecord) (ho : maxZoneObservations < obs) :
    zoneSizes record obs = some (.unknown (.branch [] "observations size")) := by
  simp [zoneSizes, ho, Nat.not_lt.mpr hr]

/-- The enumeration is `zoneSizes`'s answer when the sizes stopped the decoding, otherwise `zoneMin`'s on the decoded
    request. -/
theorem ZoneReplay.min_early {x : ZoneReplay} {z : DefaultZone Entity} (h : x.early = some z) : x.min = .error z := by
  simp [ZoneReplay.min, h]

theorem ZoneReplay.min_none {x : ZoneReplay} (h : x.early = none) : x.min = zoneMin x.v.L x.X x.S.M x.record x.obs := by
  simp [ZoneReplay.min, h]

/-- An enumeration the replay answers is `zoneMin`'s on the decoded request, read after the sizes passed. -/
theorem ZoneReplay.min_ok {x : ZoneReplay} {Min : List (List (String × List Entity))} (h : x.min = .ok Min) :
    x.early = none ∧ zoneMin x.v.L x.X x.S.M x.record x.obs = .ok Min := by
  unfold ZoneReplay.min at h
  split at h
  · cases h
  · rename_i he; exact ⟨he, h⟩

/-- What the replay decodes is the request's: the situation is `situationX`'s of its `model`; the query's outcome and
    tuple are `outcomeOf`'s and `tupleIn`'s of its `query` (`outcomeOf_mem`, `tupleIn_typed`); `early` is
    `zoneSizes`'s answer on the sizes of its `record` and `observations`; with no early answer, the record and the
    observations are, entry by entry and in request order, `recordEntry`'s and `obsEntry`'s of the request's entries
    (`recordEntry_sound`, `obsEntry_sound`); with one, nothing else is decoded. -/
theorem replayZoneOn_sound {v : DefaultsView} {j : Json} {x : ZoneReplay} (h : replayZoneOn v j = .ok x) :
    x.v = v ∧
    (∃ m S, j.getObjVal? "model" = .ok m ∧ VE.NormDefaults.Wire.situationX v.L m = .ok S ∧ S.M = x.S.M) ∧
    (∃ q, j.getObjVal? "query" = .ok q ∧ outcomeOf v.L q = .ok x.r ∧
      tupleIn x.S.M (VE.NormDefaults.sortsOf v.L.U.D x.r.name) q = .ok x.vs) ∧
    ∃ recordJ obsJ, ((j.getObjVal? "record") >>= Json.getArr?) = .ok recordJ ∧
      ((j.getObjVal? "observations") >>= Json.getArr?) = .ok obsJ ∧ x.early = zoneSizes recordJ.size obsJ.size ∧
      (x.early = none → recordJ.toList.mapM (recordEntry v.L x.S.M) = .ok x.record ∧
        obsJ.toList.mapM (obsEntry v.L x.S.M) = .ok x.obs) ∧
      (x.early ≠ none → x.record = [] ∧ x.obs = []) := by
  unfold replayZoneOn at h
  obtain ⟨m, hm, h⟩ := replayBind_ok h
  obtain ⟨S, hS, h⟩ := replayBind_ok h
  obtain ⟨_, -, h⟩ := replayBind_ok h
  obtain ⟨q, hq, h⟩ := replayBind_ok h
  obtain ⟨_, -, h⟩ := replayBind_ok h
  obtain ⟨r, hr, h⟩ := replayBind_ok h
  obtain ⟨vs, hvs, h⟩ := replayBind_ok h
  obtain ⟨rj, hrj, h⟩ := replayBind_ok h
  obtain ⟨recordJ, hrec, h⟩ := replayBind_ok h
  obtain ⟨oj, hoj, h⟩ := replayBind_ok h
  obtain ⟨obsJ, hobs, h⟩ := replayBind_ok h
  have hR : ((j.getObjVal? "record") >>= Json.getArr?) = .ok recordJ := by rw [hrj]; exact hrec
  have hO : ((j.getObjVal? "observations") >>= Json.getArr?) = .ok obsJ := by rw [hoj]; exact hobs
  split at h
  · rename_i z hz
    cases h
    exact ⟨rfl, ⟨m, S, hm, hS, rfl⟩, ⟨q, hq, hr, hvs⟩, recordJ, obsJ, hR, hO, hz.symm, by simp, fun _ => ⟨rfl, rfl⟩⟩
  · rename_i hz
    obtain ⟨record, hrecs, h⟩ := replayBind_ok h
    obtain ⟨obs, hobss, h⟩ := replayBind_ok h
    cases h
    exact ⟨rfl, ⟨m, S, hm, hS, rfl⟩, ⟨q, hq, hr, hvs⟩, recordJ, obsJ, hR, hO, hz.symm,
      fun _ => ⟨hrecs, hobss⟩, fun hn => absurd rfl hn⟩

/-! ## The rows after DE10 -/

/-- One true decision of the completion shown, as DE10 lists it: DE11 when a stated sufficient condition of the
    rule's exception holds there (its index), DE10f when `forcedAll` lists it, DE13 otherwise. -/
inductive ZoneLine
  | stated (rule : String) (condition : Nat) (vs : List Entity)
  | forced (rule : String) (vs : List Entity)
  | assumed (k : DecisionKey) (vs : List Entity)

/-- The true decisions of the completion `w` (the record's and `w`'s enumerated atoms; a switch the record leaves
    off is off in every completion, so no row names it), in `keyedDecisions` order then tuple order, each with its
    row. -/
def zoneLines (x : ZoneReplay) (forced : List (String × List Entity)) (w : List ((String × List Entity) × Bool)) :
    List ZoneLine :=
  let L := x.v.L
  let rec' := x.record
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

/-- The row a line is shown as (spec 4), and for DE13 the kind of its decision (`decisionKeyJson`'s key). -/
def ZoneLine.row : ZoneLine → String
  | .stated .. => "DE11" | .forced .. => "DE10f" | .assumed .. => "DE13"

def ZoneLine.kind : ZoneLine → String
  | .assumed (.excepted _) _ => "excepted" | .assumed (.off ..) _ => "off" | .assumed (.outweighs ..) _ => "outweighs"
  | _ => ""

def ZoneLine.json (l : ZoneLine) : Json :=
  Json.mkObj ([("row", .str l.row)] ++ match l with
    | .stated r i vs => [("rule", .str r), ("condition", toJson i), ("tuple", entityIds vs)]
    | .forced r vs => [("rule", .str r), ("tuple", entityIds vs)]
    | .assumed k vs => [("decision", VE.SoftNorms.Wire.decisionKeyJson k), ("tuple", entityIds vs)])

/-! ## The words of the rows (spec 4; `ve/defaults_words.json` is generated from them by `ZoneWordsMain.lean`)

Each row is keyed by the answer's fields that select it, so the renderer chooses nothing: DE10's three forms by the
zone and `form`, a line by its `row` and `kind`. The slots in braces are the existing renderers' text: `{result}` the
query's clause (the `words` mode), `{rule}`, `{tuple}` (the ids, joined by `zoneJoins`' `tuple`), `{condition}` the
rule's stated condition at the tuple, `{party}` soft's decider phrase, `{act}`, `{lower}` and `{higher}` the
ranking's act phrase and ranks, `{first}` and `{second}` the two completions' lines in their `inline` words, joined
by `zoneJoins`' `and` (REPORT, recorded choice 2). -/

/-- DE10, DE10′ and DE10″: zone, `form`, row, words. -/
def zoneHeads : List (String × String × String × String) :=
  [("byDefault", "short", "DE10", "With no exceptions here that could be dropped, alone or together, {result}."),
   ("byDefault", "long", "DE10′", "With no assumptions here that could be dropped, alone or together, {result}."),
   ("leftTo", "short", "DE10″", "With no exceptions here that could be dropped, alone or together, the answer " ++
      "depends on which rule gives way: {first}, or {second}."),
   ("leftTo", "long", "DE10″", "With no assumptions here that could be dropped, alone or together, the answer " ++
      "depends on which rule gives way: {first}, or {second}.")]

/-- DE11, DE10f and DE13's three: `row`, `kind`, the sentence, its words inside DE10″. -/
def zoneLineWords : List (String × String × String × String) :=
  [("DE11", "", "The text's own exception to rule {rule} applies here: {condition}.",
      "the text's own exception to rule {rule} applies here: {condition}"),
   ("DE10f", "", "The facts here force the exception to rule {rule} for {tuple}.",
      "the facts here force the exception to rule {rule} for {tuple}"),
   ("DE13", "excepted", "This assumes that the exception to rule {rule} applies to {tuple}.",
      "the exception to rule {rule} applies to {tuple}"),
   ("DE13", "off", "This assumes that {party} has turned rule {rule} off for {tuple}.",
      "{party} has turned rule {rule} off for {tuple}"),
   ("DE13", "outweighs", "This assumes that, on {act}, the {lower} consideration outweighs the {higher} consideration.",
      "on {act}, the {lower} consideration outweighs the {higher} consideration")]

def zoneJoins : List (String × String) := [("tuple", ", "), ("and", " and ")]

/-- `ve/defaults_words.json` (`ZoneWordsMain.lean` prints it): each row with the answer's fields that select it. -/
def zoneWordsJson : Json := Json.mkObj [
  ("heads", toJson (zoneHeads.map fun (z, f, r, w) =>
    Json.mkObj [("zone", .str z), ("form", .str f), ("row", .str r), ("words", .str w)])),
  ("lines", toJson (zoneLineWords.map fun (r, k, s, i) =>
    Json.mkObj [("row", .str r), ("kind", .str k), ("sentence", .str s), ("inline", .str i)])),
  ("joins", Json.mkObj (zoneJoins.map fun (k, w) => (k, .str w)))]

/-- Every row Lean selects has its words, once: DE10's form for each zone shown and each `form`, and each line. -/
theorem zoneWords_complete (f : Form) (l : ZoneLine) :
    (zoneHeads.filter fun h => h.1 == "byDefault" && h.2.1 == formLabel f).length = 1 ∧
    (zoneHeads.filter fun h => h.1 == "leftTo" && h.2.1 == formLabel f).length = 1 ∧
    (zoneLineWords.filter fun w => w.1 == l.row && w.2.1 == l.kind).length = 1 := by
  rcases l with _ | _ | ⟨_ | _ | _, _⟩ <;> cases f <;> simp only [ZoneLine.row, ZoneLine.kind] <;> decide

/-- A line's row and kind read back as the one kind of line they name: DE11, DE10f and DE13's three are distinct, so
    each line has its own words row (`zoneWords_complete`). -/
theorem zoneLine_rows_distinct (vs : List Entity) :
    ([ZoneLine.stated "" 0 vs, .forced "" vs, .assumed (.excepted "") vs, .assumed (.off "" "") vs,
      .assumed (.outweighs "" "" "") vs].map fun l => (l.row, l.kind)) =
    [("DE11", ""), ("DE10f", ""), ("DE13", "excepted"), ("DE13", "off"), ("DE13", "outweighs")] := rfl

/-- The rule of an exception atom, by its key (`keyedDecisions`), for `forced_all`. -/
def exceptedRule (D : VE.SoftNorms.SoftDoc) (n : String) : String :=
  match (keyedDecisions D).find? (·.2.1 == n) with
  | some (.excepted r, _) => r
  | _ => n

/-- The answer for the zone `zone` and the list `forced` (`defaultZoneOf` and `forcedAllOf`, from `zoneFields`'s one
    enumeration): with `by default` or `left to`, DE10's form, `forced_all` and the completions shown (one, or the
    two that differ), each a list of rows. `forced` and `zoneFormOf` are read only for those two zones, which come
    from a complete, nonempty enumeration; were either `none` there, the answer is `unknown`. -/
def zoneFieldsOf (x : ZoneReplay) (zone : DefaultZone Entity) (forced : Option (List (String × List Entity))) :
    List (String × Json) :=
  let unknownF (why : String) : List (String × Json) := [("zone", .str "unknown"), ("reason", .str why)]
  let shown (tag : String) (value : List (String × Json)) (ws : List (List ((String × List Entity) × Bool))) :
      List (String × Json) :=
    match zoneFormOf x.v.L x.S.M x.record, forced with
    | some f, some fs =>
      [("zone", .str tag)] ++ value ++
      [("form", .str (formLabel f)),
       ("forced_all", Json.arr (fs.map (fun (n, vs) => Json.mkObj [("rule", .str (exceptedRule x.v.L.D n)),
          ("tuple", entityIds vs)])).toArray),
       ("completions", Json.arr (ws.map (fun w => Json.arr ((zoneLines x fs w).map ZoneLine.json).toArray)).toArray)]
    | _, _ => unknownF "size"
  match zone with
  | .byDefault b w => shown "byDefault" [("value", .bool b)] [w]
  | .leftTo _ w₁ w₂ => shown "leftTo" [] [w₁, w₂]
  | .notSaid _ _ => [("zone", .str "notSaid")]
  | .noCompletion l => [("zone", .str "noCompletion"), ("labels", toJson l)]
  | .unknown (.budget n k) => unknownF s!"budget: {n} open atoms, over {k}"
  | .unknown (.branch _ why) => unknownF why

/-- The answer, with `zoneMin` evaluated once and given to `zoneOfMin` and `forcedOfMin` (`defaultZoneOf_eq`,
    `forcedAllOf_eq`; DRI 2026-11-04, df-5 item 2). -/
def zoneFields (x : ZoneReplay) : List (String × Json) :=
  let m := x.min
  zoneFieldsOf x (match m with | .error z => z | .ok Min => zoneOfMin x.v.L x.S.M x.record x.r x.vs Min)
    (match m with | .error _ => none | .ok Min => forcedOfMin x.v.L x.S.M x.record Min)

/-- `defaults-zone`, then the other `defaults-*` kinds (`defaultsCase`). -/
def zoneCase (v : DefaultsView) (id kind : String) (j : Json) : Except String (Option Json) :=
  if kind == "defaults-zone" then (fun x => some (VE.Route.Wire.ok id (zoneFields x))) <$> replayZoneOn v j
  else defaultsCase v id kind j

end VE.Defaults.Wire
