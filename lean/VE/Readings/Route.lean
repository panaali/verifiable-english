import VE.Readings.Assertions

/-! The route of a `readings@1` document and the regenerated elaboration (docs/spec/composition-s2.md 1.1, 1.8,
3, 4.1, 4.6).

`routeOf` is the table of 1.1, read on the decoded document: W2's route when no open set is content-bearing, the
pending row when a candidate is pending, the abstention when `norm-defaults@0` is in the list, the superposed route
on the soft and norms chains when `superposable D`, the enumerated route otherwise (the rights chain until S2b
unconditionally). `notSuperposable` is the finding of 1.8 with its cause, computed on the soft and norms chains
only. `elaborateFields` is the `readings-elaborate` answer of section 3, regenerated from the decoded document. -/
namespace VE.Readings
open Lean
open VE.Norms (envAt size)
open VE.SoftNorms (SoftNode SoftDoc soften decisions)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content Labelled)
universe u

inductive Route
  | w2 | pending | abstention | superposed | enumerated
  deriving DecidableEq, Repr

def Route.text : Route → String
  | .w2 => "w2"
  | .pending => "pending"
  | .abstention => "abstention"
  | .superposed => "superposed"
  | .enumerated => "enumerated"

/-- 1.1, in its row order: the first row that applies. -/
def routeOf (normDefaults : Bool) (D : Doc) : Route :=
  if !(D.sets.any Wire.contentBearing) then .w2
  else if D.sets.any (fun R => R.candidates.any (·.content.isNone)) then .pending
  else if normDefaults then .abstention
  else if D.chain != .rights && superposable D then .superposed
  else .enumerated

theorem routeOf_superposed {nd : Bool} {D : Doc} (h : routeOf nd D = .superposed) :
    D.chain ≠ .rights ∧ superposable D = true := by
  unfold routeOf at h
  split at h
  · cases h
  · split at h
    · cases h
    · split at h
      · cases h
      · split at h
        · rename_i hs
          simp only [Bool.and_eq_true, bne_iff_ne, ne_eq] at hs
          exact hs
        · cases h

/-! ## The checks of 4.5 (spec 8.4) -/

/-- checkCertificate on background′ ++ slot ++ atoms ++ layers ++ assertions ++ Γ for correlate (sup D).1. -/
def supCertificateCheck (D : Doc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate) : Bool :=
  let X := correlate (sup D).1
  VE.Tableau.checkCertificate (envAt (soften X) (size (soften X)))
    (VE.Compose.backgroundP X (slotUnder D A) ++ VE.Norms.elaborate (soften X).T ++ ((sup D).2 ++ Γ)) φ cert

/-- The finite validity of the base background with the slot and the atoms, and of the assertions and Γ read on the
    base through the outcome substitution. -/
def supModelCheck {α : Type u} [DecidableEq α] (D : Doc) (A : Choice) (Γ : List VE.Formula)
    (M : VE.FiniteModel α) : Bool :=
  let X := correlate (sup D).1
  VE.Compose.backgroundValidP X (slotUnder D A) M && ((sup D).2 ++ Γ).all (fun a => (VE.SoftNorms.circ X a).eval M [])

/-! ## The finding of 1.8 -/

/-- The first fixed rule's interface name whose candidates give it different `over` lists, with its set. -/
def firstNonUniform (D : Doc) : Option (String × String) :=
  D.items.findSome? (fun it => match it with
    | .fixed _ (.norm N) _ => N.over.findSome? (fun n =>
        (D.sets.find? (fun R => (interfaceOf R).contains ("rule", n) && !uniformOn R n)).map (fun R => (R.id, n)))
    | _ => none)

/-- The names of a `DependencyCycle: a, b, c` diagnostic. -/
def cycleNames (e : String) : Option (List String) :=
  if e.startsWith "DependencyCycle: " then some ((e.drop 17).splitOn ", ") else none

/-- The open sets with a candidate rule on, or named by, a node of the cycle. -/
def cycleSets (D : Doc) (names : List String) : List String :=
  ((List.range D.sets.length).filter (fun m =>
    (List.range (setSize D m)).any (fun i =>
      (((D.sets[m]?).bind (·.candidates[i]?)).bind (·.content)).any (fun c => match c with
        | .norm N => names.contains N.pred || names.contains (qualify (position D m i) N.name)
        | _ => false)))).filterMap (fun m => (D.sets[m]?).map (·.id))

/-- `ReadingsNotSuperposable: <sets>` and its cause (1.8, 7), on the soft and norms chains; `none` when the
    document is superposable. -/
def notSuperposable (D : Doc) : Option (String × String) :=
  if D.chain == .rights then none
  else if !supReady D then some (", ".intercalate (D.sets.map (·.id)), "the shape of the reading sets")
  else match firstNonUniform D with
    | some (s, n) => some (s, s!"precedence under {n}")
    | none => match Wire.chainText D.chain (sup D) with
      | some e =>
        let sets := match cycleNames e with
          | some names => cycleSets D names
          | none => D.sets.map (·.id)
        some (", ".intercalate sets, e)
      | none => none

def notSuperposableText (sets : String) : String := s!"ReadingsNotSuperposable: {sets}"

/-- The narrowings not in force: recorded on a version that is not the active one (1.2, 6). -/
def staleNarrowings (D : Doc) : List String :=
  (D.narrowings.filter (fun N => (inForce D N).isNone)).map (·.id)

/-! ## The regenerated answer -/

def enc (a : VE.Formula) : Json := VE.Route.Wire.encodeFormula a

def choiceJson (c : Choice) : Json := Json.arr (c.map (fun x => Json.arr #[.str x.1, toJson x.2])).toArray

def exceptionJson (e : VE.SoftNorms.Exception) : Json :=
  Json.mkObj [("decided_by", match e.decidedBy with | some d => .str d | none => .null),
    ("sufficient", Json.arr (e.sufficient.map enc).toArray), ("necessary", Json.arr (e.necessary.map enc).toArray),
    ("factors", toJson e.factors)]

/-- A rule of `sup D` in canonical wire form. -/
def softNodeJson (N : SoftNode) : Json :=
  Json.mkObj [("name", .str N.name), ("predicate", .str N.pred), ("sign", .bool N.sign),
    ("mode", .str (if N.mode == .strict then "strict" else "default")), ("guard", enc N.guard),
    ("unless", Json.arr (N.carveOuts.map enc).toArray), ("over", toJson N.over),
    ("rank", match N.rank with | some r => .str r | none => .null), ("alterable", toJson N.alterable),
    ("exception", match N.exception with | some e => exceptionJson e | none => .null), ("hard", .bool N.hard)]

def contentJson : Content → Json
  | .assertion φ => Json.mkObj [("assertion", enc φ)]
  | .norm N => Json.mkObj [("norm", softNodeJson N)]
  | c => Json.mkObj [("kind", .str c.kind)]

/-- The units of `sup D` in source order: a fixed unit with its copied content, each candidate gated, with its
    canonical position. -/
def supUnits (D : Doc) : List Json :=
  (D.items.foldl (fun (acc : List Json × Nat) it => match it with
    | .fixed u c _ => (acc.1 ++ [Json.mkObj [("unit", .str u), ("content", contentJson (copyContent D c))]], acc.2)
    | .bar u _ => (acc.1 ++ [Json.mkObj [("unit", .str u), ("content", Json.mkObj [("kind", .str "bar")])]], acc.2)
    | .set R => (acc.1 ++ (List.range R.candidates.length).filterMap (fun i =>
        (R.candidates[i]?.bind (·.content)).map (fun c => Json.mkObj [("unit", .str R.unit), ("set", .str R.id),
          ("version", toJson R.version), ("index", toJson i), ("position", toJson (position D acc.2 i)),
          ("content", contentJson (gateContent D acc.2 i c))])), acc.2 + 1)) ([], 0)).1

def vocabularyJson (D : Doc) : Json :=
  if D.sets.isEmpty then Json.mkObj [("sorts", Json.arr #[]), ("constants", Json.mkObj []), ("predicates", Json.arr #[])]
  else Json.mkObj [("sorts", toJson ["ve__reading"]), ("constants", Json.mkObj [("ve__here", .str "ve__reading")]),
    ("predicates", Json.arr ((bitDecls D).map (fun d => Json.mkObj [("name", .str d.1), ("arguments", toJson d.2)])).toArray)]

def slotJson (D : Doc) : Json :=
  Json.arr ((slotLabelled D).map (fun x => Json.mkObj [("label", .str x.1), ("ast", enc x.2)])).toArray

/-- A candidate's own names (its declared rule and that rule's decision predicates) with their names in `sup D`. -/
def candidateNames (D : Doc) (m i : Nat) (a : Candidate) : List (String × String) :=
  match a.content with
  | some (.norm N) =>
    let q := { N with name := qualify (position D m i) N.name }
    [(N.name, q.name)] ++
      (if N.mode == .default then [(VE.SoftNorms.exceptedName N, VE.SoftNorms.exceptedName q)] else []) ++
      N.alterable.map (fun π => (VE.SoftNorms.offName N π, VE.SoftNorms.offName q π))
  | _ => []

def candidateJson (D : Doc) (m i : Nat) (a : Candidate) : Json :=
  Json.mkObj [("index", toJson i), ("id", .str a.id), ("position", toJson (position D m i)),
    ("names", Json.arr ((candidateNames D m i a).map (fun x => Json.arr #[.str x.1, .str x.2])).toArray)]

def setNamesJson (D : Doc) (m : Nat) (R : ReadingSet) : Json :=
  Json.mkObj [("set", .str R.id), ("version", toJson R.version), ("candidates",
    Json.arr ((List.range R.candidates.length).filterMap (fun i => (R.candidates[i]?).map (candidateJson D m i))).toArray)]

/-- Per set and candidate: its position and the name map of its own names into `sup D`. -/
def nameMapJson (D : Doc) : Json :=
  Json.arr ((List.range D.sets.length).filterMap (fun m => (D.sets[m]?).map (setNamesJson D m))).toArray

/-- The compatible choices up to 64, or `over`. -/
def choicesJson (D : Doc) : List (String × Json) :=
  let cs := choices D
  if cs.length ≤ maxChoices then [("choice_count", toJson cs.length), ("choices", Json.arr (cs.map choiceJson).toArray)]
  else [("choice_count", .str "over 64"), ("choices", .str "over")]

/-- The sizes of `sup D` against the chain's limits (10): sorts, predicates, and the nodes of the unfolded rules. -/
def sizesJson (D : Doc) (basePredicates : Nat) : Json :=
  let X := (sup D).1.soft
  let nodes := ((soften X).T.nodes.map (fun N => (N.guard :: N.carveOuts).map VE.Bridge.formulaNodes)).flatten.sum
  Json.mkObj [("sorts", toJson X.E.sorts.length), ("predicates", toJson (basePredicates + (bitDecls D).length +
      (decisions X).length)), ("nodes", toJson nodes),
    ("limits", Json.mkObj [("sorts", toJson 32), ("predicates", toJson 256), ("nodes", toJson 10000)])]

/-- The `readings-elaborate` answer (3): the route; on the soft and norms chains past the first three rows the
    finding of 1.8; on the superposed route the choice vocabulary, the units of `sup D`, the labelled slot, the
    name map, the compatible choices and the sizes; on the enumerated route the compatible choices. -/
def elaborateFields (normDefaults : Bool) (basePredicates : Nat) (D : Doc) : List (String × Json) :=
  let route := routeOf normDefaults D
  let head : List (String × Json) := [("route", .str route.text)]
  match route with
  | .w2 | .pending | .abstention => head
  | .superposed =>
    head ++ [("finding", .null), ("narrowings_stale", toJson (staleNarrowings D)),
      ("vocabulary", vocabularyJson D), ("units", Json.arr (supUnits D).toArray), ("slot", slotJson D),
      ("names", nameMapJson D)] ++ choicesJson D ++ [("sizes", sizesJson D basePredicates)]
  | .enumerated =>
    head ++ [("finding", match notSuperposable D with
        | some (sets, cause) => Json.mkObj [("text", .str (notSuperposableText sets)), ("cause", .str cause)]
        | none => .null),
      ("narrowings_stale", toJson (staleNarrowings D))] ++ choicesJson D

end VE.Readings
