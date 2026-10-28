import VE.Events.Premises
import VE.NormDefaults.Packs

/-! The `events` block on the wire (docs/spec/events-time-causation.md 1.2, 1.3, 4 and 6.3; plan 2.9): `decodeEvents`
reads the block and checks it against the environment's vocabulary in the order of spec 4, items 2 to 7, then gives
the decoded block, the regenerated environment (`regenEnv`) and the `events` premise pack. The profile row (item 1)
is AR-10's table's and the open-term check of item 5 (`LinkNotOpen`) reads the document; both are the route's (et-4b).
The named dates are constants of the regenerated environment, as `unsaid__` names are (plan 2.8), so the pack
declares no name of its own and `Packs.assemble` checks it as a constraint pack. -/
namespace VE.Events
open Lean
open VE.Time (Civil parseIso)
open VE.Bridge (fields strings)

/-- The decoded block, the regenerated environment and the origins of the pack's labels. -/
structure EventsDecoded where
  V : EventsEnv
  E : VE.Environment
  origins : List (String × VE.NormDefaults.Packs.RequestPath)
  typed : EventsTyped E V = true

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
  if by_.utf8ByteSize > 64 then throw (invalid ".links.decided_by")
  pure (p, form, if by_ == "unstated" then none else some by_)

/-! ## Items 3 to 7, in order -/

/-- The first fault of a list of checks, each a fault condition and its text. -/
def firstFault (cs : List (Bool × String)) : Except String Unit :=
  match cs.find? (·.1) with
  | some c => throw c.2
  | none => pure ()

/-- The first name already seen, or listed earlier. -/
def repeatOf (seen : List String) : List String → Option String
  | [] => none
  | n :: ns => if seen.contains n then some n else repeatOf (n :: seen) ns

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

/-- Item 7: every generated premise within `limit` nodes. -/
def checkPremiseSize (limit : Nat) (ls : List (String × VE.Formula)) : Except String Unit :=
  firstFault (ls.map fun (l, a) => (decide (VE.Bridge.formulaNodes a > limit), s!"ResourceLimit: events premise {l}"))

/-- Spec 1.2 and 4: `none` without the block; otherwise the block, checked in order, its regenerated environment. -/
def decodeEvents (environment : Json) : Except String (Option EventsDecoded) :=
  match environment.getObjVal? "events" with
  | .error _ => pure none
  | .ok b => do
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
    let W := vocabView environment
    let V0 : EventsEnv := ⟨day, before, events, states, [], none, []⟩
    checkDay W V0 (raw.map (·.1))
    checkRoles W V0
    let links ← checkLinks W V0 raw
    let (ds, a) ← checkDates W dates anchor
    let V : EventsEnv := { V0 with dates := ds, anchor := a, links := links }
    checkPremiseSize VE.Limits.maxNodes (eventsLabelled V)
    if h : WellFormedEvents W.env V = true then
      pure (some ⟨V, regenEnv W.env V, [], regen_typed W.env V h⟩)
    else throw "InvalidInput: events"

/-- Spec 6.3: the `events` pack, last in `packOrder`; its labels are `eventsLabelled` (1.4). -/
def eventsPack (d : EventsDecoded) : VE.NormDefaults.Packs.Pack :=
  { id := "events", kind := .constraint, decls := [], consts := [], labelled := eventsLabelled d.V,
    origins := d.origins }

/-- An absent block gives no pack (PK-1's rule then leaves X as the other packs' X). -/
theorem eventsX_absent (environment : Lean.Json) (h : (environment.getObjVal? "events").toOption = none) :
    decodeEvents environment = .ok none := by
  unfold decodeEvents
  cases he : environment.getObjVal? "events" with
  | error => rfl
  | ok b => rw [he] at h; cases h

end VE.Events
