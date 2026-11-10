import VE.Events.Premises
import VE.NormDefaults.Packs
import VE.Compose.Dispatch
import Std.Data.HashSet

/-! The `events` block on the wire (docs/spec/events-time-causation.md 1.2, 1.3, 4 and 6.3; plan 2.9): `decodeEvents`
reads the block and checks it against the environment's vocabulary in the order of spec 4, items 2 to 7, then gives
the decoded block, the regenerated environment (`regenEnv`) and the `events` premise pack. `eventsHook` is what a
layered decoder runs first: the profile row (item 1, AR-10's table), the block with the open-term check of item 5
(`LinkNotOpen`, which reads the case's open terms) and the environment the route decodes. The named dates are constants of the regenerated environment, as `unsaid__` names are (plan 2.8), so the pack
declares no name of its own and `Packs.assemble` checks it as a constraint pack. -/
namespace VE.Events
open Lean
open VE.Time (Civil parseIso)
open VE.Bridge (fields strings)

/-- The decoded block, the regenerated environment and the origins of the pack's labels. `labelled` is `eventsLabelled
V`, evaluated once, by the decoder that charges its size. -/
structure EventsDecoded where
  V : EventsEnv
  E : VE.Environment
  origins : List (String × VE.NormDefaults.Packs.RequestPath)
  typed : EventsTyped E V = true
  labelled : List (String × VE.Formula)
  labelled_eq : labelled = eventsLabelled V

/-! ## The vocabulary, as the block reads it -/

/-- The declared sorts, predicates and constants, read without judging their shape (the route's decoder does). -/
structure VocabView where
  sorts : List String
  preds : List (String × Json)
  consts : List (String × Json)

def vocabView (environment : Json) : VocabView :=
  let v := environment.getObjValD "vocabulary"
  let fs := fun (k : String) => (fields (v.getObjValD k)).toOption.getD []
  ⟨(fs "sorts").map (·.1), fs "predicates", fs "constants"⟩

def VocabView.args (W : VocabView) (p : String) : Option (List String) :=
  (W.preds.lookup p).bind fun e => (strings (e.getObjValD "arguments")).toOption

def VocabView.wording (W : VocabView) (p : String) : Option String :=
  (W.preds.lookup p).bind fun e => (e.getObjValD "verbalisation").getStr?.toOption

/-- Regulated or defined: `before`, a role and a link are neither. -/
def VocabView.decided (W : VocabView) (p : String) : Bool :=
  (W.preds.lookup p).any fun e => (e.getObjVal? "regulated").isOk || (e.getObjVal? "defined").isOk

def VocabView.names (W : VocabView) : List String := W.sorts ++ W.preds.map (·.1) ++ W.consts.map (·.1)

/-- The author's environment `E` of `WellFormedEvents`. -/
def VocabView.env (W : VocabView) : VE.Environment :=
  ⟨W.sorts, W.args, fun c => (W.consts.lookup c).bind fun e => (e.getObjValD "sort").getStr?.toOption⟩

/-! ## Item 2: the block's shape -/

def invalid (path : String) : String := s!"InvalidInput: events{path}"

/-- An object with exactly these required fields and at most these optional ones. -/
def objectAt (j : Json) (path : String) (required optional : List String) : Except String Unit := do
  let ks ← (fields j).mapError fun _ => invalid path
  if let some (k, _) := ks.find? (fun (k, _) => !(required ++ optional).contains k) then
    throw (invalid s!"{path}.{k}")
  if let some k := required.find? (fun k => !ks.any (·.1 == k)) then throw (invalid s!"{path}.{k}")

def strAt (j : Json) (path k : String) : Except String String :=
  (j.getObjValD k).getStr?.mapError fun _ => invalid s!"{path}.{k}"

def arrAt (j : Json) (path k : String) : Except String (List Json) :=
  ((j.getObjValD k).getArr?.map (·.toList)).mapError fun _ => invalid s!"{path}.{k}"

def decodeEventSort (j : Json) : Except String EventSort := do
  objectAt j ".events" ["sort", "on"] []
  pure ⟨← strAt j ".events" "sort", ← strAt j ".events" "on"⟩

def decodeStateSort (j : Json) : Except String StateSort := do
  objectAt j ".states" ["sort", "begins", "ends"] []
  pure ⟨← strAt j ".states" "sort", ← strAt j ".states" "begins", ← strAt j ".states" "ends"⟩

/-- A link as written: its predicate, form and decider (`unstated` is the explicit absence). -/
def decodeLinkRaw (j : Json) : Except String (String × LinkForm × Option String) := do
  objectAt j ".links" ["predicate", "form", "decided_by"] []
  let p ← strAt j ".links" "predicate"
  let form ← match ← strAt j ".links" "form" with
    | "contributed" => pure LinkForm.contributed
    | "necessary" => pure LinkForm.necessary
    | _ => throw (invalid ".links.form")
  let by_ ← strAt j ".links" "decided_by"
  if by_.utf8ByteSize > VE.Limits.maxIdentifierBytes then throw (invalid ".links.decided_by")
  pure (p, form, if by_ == "unstated" then none else some by_)

/-! ## Items 3 to 7, in order -/

/-- The first fault of a list of checks, each a fault condition and its text. -/
def firstFault (cs : List (Bool × String)) : Except String Unit :=
  match cs.find? (·.1) with
  | some c => throw c.2
  | none => pure ()

/-- The first name already seen, or listed earlier, in one pass over a list of any size. -/
def repeatOf (seen : List String) (ns : List String) : Option String :=
  (ns.foldl (fun (acc : Option String × Std.HashSet String) n => match acc.1 with
    | some r => (some r, acc.2)
    | none => if acc.2.contains n then (some n, acc.2) else (none, acc.2.insert n))
    (none, Std.HashSet.ofList seen)).1

def roleSig (W : VocabView) (day s p : String) : Bool × String := (W.args p != some [s, day], s!"EventsSort: {p}")

/-- Item 3: the day sort and `before`, and no regulated or defined `before`, role or link. -/
def checkDay (W : VocabView) (V : EventsEnv) (linkPreds : List String) : Except String Unit :=
  firstFault ([(!W.sorts.contains V.day, s!"EventsSort: {V.day}"),
    (W.args V.before != some [V.day, V.day], s!"EventsSort: {V.before}"),
    (W.wording V.before != some beforeWording, s!"EventsVerbalisation: {V.before}")] ++
    (V.before :: rolePreds V ++ linkPreds).map fun p => (W.decided p, s!"EventsRegulated: {p}"))

/-- Item 4: event and state sorts and their roles. -/
def checkRoles (W : VocabView) (V : EventsEnv) : Except String Unit := do
  firstFault ((roleSorts V).map fun s => (!W.sorts.contains s || s == V.day, s!"EventsSort: {s}"))
  if let some s := repeatOf [] (eventSorts V) then throw s!"DuplicateDeclaration: event sort {s}"
  if let some s := repeatOf (eventSorts V) (stateSorts V) then throw s!"DuplicateDeclaration: state sort {s}"
  firstFault (V.events.map (fun e => roleSig W V.day e.sort e.on) ++
    V.states.flatMap fun s => [roleSig W V.day s.sort s.begins, roleSig W V.day s.sort s.ends])
  firstFault ((rolePreds V).map fun p => (!(W.wording p).any roleWordingOk, s!"EventsVerbalisation: {p}"))
  if let some p := repeatOf [V.before] (rolePreds V) then throw s!"DuplicateDeclaration: role {p}"

/-- Item 5 (without `LinkNotOpen`, the route's): each link's signature and wording, then no repeated predicate. -/
def checkLinks (W : VocabView) (V : EventsEnv) (raw : List (String × LinkForm × Option String)) :
    Except String (List Link) := do
  let ls ← raw.mapM fun (p, form, by_) => match W.args p with
    | some [c, e] => if (roleSorts V).contains c && (roleSorts V).contains e then pure (Link.mk p form c e by_)
      else throw s!"EventsSort: {p}"
    | _ => throw s!"EventsSort: {p}"
  firstFault (ls.map fun l => (W.wording l.predicate != some (linkWording l.form), s!"EventsVerbalisation: {l.predicate}"))
  if let some p := repeatOf (V.before :: rolePreds V) (ls.map (·.predicate)) then
    throw s!"DuplicateDeclaration: link {p}"
  pure ls

/-- `date__`, the prefix PK-1's table gives the `events` pack. -/
def ownedByEvents (n : String) : Bool :=
  VE.NormDefaults.Packs.reservedPrefixes.any fun (o, x) => o == "events" && n.startsWith x

/-- Item 6: the dates parse (`parseIso`'s texts), are unique, at most `maxDates` with the anchor, sorted by
    `Civil.num`; no declared name has the reserved prefix. -/
def checkDates (W : VocabView) (raw : List String) (anchor : Option String) :
    Except String (List Civil × Option Civil) := do
  let ds ← raw.mapM parseIso
  let a ← anchor.mapM parseIso
  if let some iso := repeatOf [] (ds.map (·.iso)) then throw s!"DuplicateDeclaration: date {iso}"
  let all := (ds ++ (a.filter (!ds.contains ·)).toList).mergeSort (fun x y => decide (x.num ≤ y.num))
  if all.length > maxDates then throw "ResourceLimit: events dates"
  if let some n := W.names.find? ownedByEvents then throw s!"EventsReserved: {n}"
  pure (all, a)

/-- Item 7: every generated premise within `limit` nodes, then the whole pack, whose size is charged once. -/
def checkPremiseSize (limit : Nat) (ls : List (String × VE.Formula)) : Except String Unit := do
  let sized := ls.map fun (l, a) => (l, VE.Bridge.formulaNodes a)
  firstFault (sized.map fun (l, n) => (decide (n > limit), s!"ResourceLimit: events premise {l}"))
  if (sized.map (·.2)).sum > limit then throw "ResourceLimit: events premises"

/-- Item 5's last check: each link is an open term of the case with the same decider. -/
def checkOpen (opens : List (String × String)) (ls : List Link) : Except String Unit :=
  firstFault (ls.map fun l =>
    (!opens.contains (l.predicate, l.decidedBy.getD "unstated"), s!"LinkNotOpen: {l.predicate}"))

/-- The block through item 5, before the check that needs the case's open terms. -/
structure BlockLinks where
  W : VocabView
  V0 : EventsEnv
  links : List Link
  dates : List String
  anchor : Option String

/-- Items 2 to 5 without `LinkNotOpen`. The role and link count is charged first: every later step reads those lists
    against each other, and the link pairs of `link_weaker` are quadratic in it. -/
def decodeThroughLinks (environment b : Json) : Except String BlockLinks := do
  objectAt b "" ["day", "before", "events", "states", "dates", "links"] ["anchor"]
  let day ← strAt b "" "day"
  let before ← strAt b "" "before"
  let events ← (← arrAt b "" "events").mapM decodeEventSort
  let states ← (← arrAt b "" "states").mapM decodeStateSort
  let dates ← (strings (b.getObjValD "dates")).mapError fun _ => invalid ".dates"
  let anchor ← match b.getObjVal? "anchor" with
    | .ok a => some <$> (a.getStr?.mapError fun _ => invalid ".anchor")
    | .error _ => pure none
  let raw ← (← arrAt b "" "links").mapM decodeLinkRaw
  if events.length + 2 * states.length + raw.length > VE.Limits.maxPredicates then
    throw "ResourceLimit: events premises"
  let W := vocabView environment
  let V0 : EventsEnv := ⟨day, before, events, states, [], none, []⟩
  checkDay W V0 (raw.map (·.1))
  checkRoles W V0
  pure ⟨W, V0, ← checkLinks W V0 raw, dates, anchor⟩

/-- Items 6 and 7 on a block that passed item 5. -/
def finishEvents (r : BlockLinks) : Except String EventsDecoded := do
  let (ds, a) ← checkDates r.W r.dates r.anchor
  let V : EventsEnv := { r.V0 with dates := ds, anchor := a, links := r.links }
  let labelled := eventsLabelled V
  checkPremiseSize VE.Limits.maxNodes labelled
  if h : WellFormedEvents r.W.env V = true then
    pure ⟨V, regenEnv r.W.env V, [], regen_typed r.W.env V h, labelled, rfl⟩
  else throw "InvalidInput: events"

/-- `decodeEvents` with a check of the links between items 5 and 6 (`checkOpen` on the route). -/
def decodeEventsWith (open_ : List Link → Except String Unit) (environment : Lean.Json) :
    Except String (Option EventsDecoded) :=
  match environment.getObjVal? "events" with
  | .error _ => pure none
  | .ok b => do
    let r ← decodeThroughLinks environment b
    open_ r.links
    some <$> finishEvents r

/-- Spec 1.2 and 4: `none` without the block; otherwise the block, checked in order, its regenerated environment. -/
def decodeEvents (environment : Lean.Json) : Except String (Option EventsDecoded) :=
  decodeEventsWith (fun _ => pure ()) environment

/-- A route's check of the links only refuses: what it passes is `decodeEvents`' own result. -/
theorem decodeEventsWith_ok {c : List Link → Except String Unit} {environment : Lean.Json} {r : Option EventsDecoded}
    (h : decodeEventsWith c environment = .ok r) : decodeEvents environment = .ok r := by
  unfold decodeEvents decodeEventsWith at *
  split at h
  · exact h
  · obtain ⟨b, hb, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    simp only [bind, Except.bind, hb]
    exact h

/-- Spec 6.3: the `events` pack, last in `packOrder`; its labels are `eventsLabelled` (1.4). -/
def eventsPack (d : EventsDecoded) : VE.NormDefaults.Packs.Pack :=
  { id := "events", kind := .constraint, decls := [], consts := [], labelled := d.labelled,
    origins := d.origins, conditions := [] }

/-- An absent block gives no pack (PK-1's rule then leaves X as the other packs' X). -/
theorem eventsX_absent (environment : Lean.Json) (h : (environment.getObjVal? "events").toOption = none) :
    decodeEvents environment = .ok none := by
  unfold decodeEvents decodeEventsWith
  cases he : environment.getObjVal? "events" with
  | error => rfl
  | ok b => rw [he] at h; cases h

/-! ## The route's hook (spec 3, 4) -/

/-- The open terms of a case as `(name, decider)` (`Loader.openTermNames` owns their schema): a row without both names
nothing, so its link is not open. -/
def openTermsOf (terms : Json) : List (String × String) :=
  match terms with
  | .arr ts => ts.toList.filterMap fun t =>
    match (t.getObjValD "name").getStr?, (t.getObjValD "decided_by").getStr? with
    | .ok n, .ok d => some (n, d)
    | _, _ => none
  | _ => []

/-- What a layered decoder reads from the hook: the environment it decodes, and the decoded block. -/
structure EventsHook where
  view : Json
  decoded : Option EventsDecoded

/-- The environment a layered route decodes: no block, no `events@0`, one constant of the day sort per named date. Its
identities keep reading the environment as written, so the block is in the bytes they bind. -/
def routeView (environment : Json) (d : Option EventsDecoded) : Except String Json := do
  let vocab ← environment.getObjVal? "vocabulary"
  let constants ← fields (← vocab.getObjVal? "constants")
  let dated := (d.map fun d => d.V.dates.map fun D => (dateName D, Json.mkObj [("sort", .str d.V.day),
    ("description", .str (if d.V.anchor == some D then "the date of this document" else D.iso))])).getD []
  let profiles := (VE.Compose.listedProfiles environment).filter (· != "events@0")
  let bare := Json.mkObj ((← fields environment).filter (·.1 != "events"))
  pure ((bare.setObjVal! "profiles" (toJson profiles)).setObjVal! "vocabulary"
    (vocab.setObjVal! "constants" (Json.mkObj (constants ++ dated))))

/-- `none` for a list without `events@0`, which every decoder reads as before, a block included. Otherwise the row
(item 1), the block (items 2 to 7) and the environment the route decodes. -/
def eventsHook (environment terms : Json) : Except String (Option EventsHook) := do
  if (VE.Compose.listedProfiles environment).contains "events@0" then
    let _ ← VE.Compose.gateOf VE.Compose.profileTable (VE.Compose.listedProfiles environment)
    let d ← decodeEventsWith (checkOpen (openTermsOf terms)) environment
    pure (some ⟨← routeView environment d, d⟩)
  else pure none

end VE.Events
