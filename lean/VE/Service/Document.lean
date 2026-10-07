import VE.Service.Standalone
import VE.Discourse.Loader

/-! The W2 document wrapper. This mode reports the byte partition, inferred
statuses, and the part of coverage determined by the wrapper itself. Statement
layer residuals are supplied by their owning routes in a later composition. -/
namespace VE.Service.Document
open Lean
open VE.Discourse
open VE.Bridge (stringField fields)

def allowedMetadata (format : String) : List String :=
  ["format", "environment", "units", "open_terms", "reading_sets", "narrowings",
   "couplings", "weights", "graph", "lemmas", "contexts", "assessments", "bridges",
   "scoped", "completions"] ++ (if format == "ve-document@2" then ["discourse"] else [])

structure Unit where
  id : String
  span : Nat × Nat
  kind : Json
  meaning : Json
  support : String
  status : String
  parent : Option String

def kindName (kind : Json) : String :=
  match kind with
  | .str s => s
  | .arr xs => (xs[0]?.getD Json.null).getStr?.toOption.getD ""
  | _ => ""

def sourceUnit (source : String) (environment : Json) (openNames : List String) (cursor : Nat)
    (seen : List String) (parents : List String) (parent : Option String)
    (u : Json) : Except String Unit := do
  let keys ← (fields u).mapError (fun _ => "invalid unit schema")
  let names := keys.map Prod.fst
  let required := ["id", "span", "kind", "meaning", "support"]
  unless required.all names.contains &&
      names.all (required ++ ["content", "surface", "meaning_id", "status"]).contains do
    throw "invalid unit schema"
  let id ← stringField u "id"
  unless VE.Route.Admission.token id && !seen.contains id && !parents.contains id do
    throw "duplicate or invalid unit id"
  let (a, b) ← Loader.spanOf (← u.getObjVal? "span")
  unless a == cursor && cursor < b && b ≤ source.utf8ByteSize do
    throw "unit spans must partition every source byte in order"
  if Loader.cutsCharacter source a b then throw "unit span cuts a UTF-8 character"
  let kind ← u.getObjVal? "kind"
  let _ ← VE.Route.Admission.decodeKind 16 kind
  let meaning ← u.getObjVal? "meaning"
  let meaningStatus ← Loader.meaningStatus openNames meaning
  let support ← stringField u "support"
  unless Loader.supports.contains support do throw "invalid support"
  let content := (u.getObjVal? "content").toOption
  if meaningStatus == "unformalised" && content.isSome then
    throw "unformalised unit cannot assert content"
  if let some content := content then
    match ← fields content with
    | [("ast", ast)] =>
      let checked ← Standalone.checkCase (Json.mkObj
        [("id", .str id), ("environment", environment), ("ast", ast)])
      match u.getObjVal? "meaning_id" with
      | .ok stated =>
        unless checked.getObjValD "meaning_id" == stated do
          throw "unit meaning id does not match content"
      | .error _ => pure ()
    | _ => throw "CheckerUnavailable: document content requires its Lean profile route"
  if kindName kind == "unformalised" then
    match kind, meaning with
    | .arr xs, .obj _ =>
      unless meaning.getObjValD "unformalised" == xs[1]?.getD Json.null do
        throw s!"InvalidInput: unformalised kind reason does not match meaning of {id}"
    | _, _ => throw s!"InvalidInput: unformalised kind reason does not match meaning of {id}"
  let status := Loader.w2Status content.isSome meaningStatus
  match u.getObjVal? "status" with
  | .ok (.str explicit) =>
    unless Loader.statuses.contains explicit do throw "invalid unit status"
    unless explicit == status do throw "unit status contradicts content, meaning, or active reading set"
  | .ok _ => throw "invalid unit status"
  | .error _ => pure ()
  pure ⟨id, (a, b), kind, meaning, support, status, parent⟩

def unitsOf (source : String) (environment : Json) (openNames : List String) (raw : List Json) :
    Except String (List Unit) := do
  let parents ← Loader.mixedParents raw
  let mut units : List Unit := []
  let mut cursor := 0
  for u in raw do
    let parts ← Loader.partsOf u
    let parent := if parts == [u] then none else (u.getObjValD "id").getStr?.toOption
    for part in parts do
      let unit ← sourceUnit source environment openNames cursor (units.map (·.id)) parents parent part
      units := units ++ [unit]
      cursor := unit.span.2
  unless cursor == source.utf8ByteSize do throw "unit spans do not partition all source bytes"
  pure units

def addCount (xs : List (String × Nat)) (name : String) (n : Nat) : List (String × Nat) :=
  if xs.any (·.1 == name) then xs.map (fun (k, v) => (k, if k == name then v + n else v))
  else xs ++ [(name, n)]

def counts (units : List Unit) (key : Unit → String) : List (String × Nat) :=
  units.foldl (fun acc u => addCount acc (key u) (u.span.2 - u.span.1)) []

def reasons (units : List Unit) : List (String × Nat) :=
  units.foldl (fun acc u => match u.meaning.getObjVal? "unformalised" with
    | .ok (.str reason) => addCount acc reason 1
    | _ => acc) []

def countJson (xs : List (String × Nat)) : Json :=
  Json.mkObj (xs.map fun (k, v) => (k, toJson v))

def residual (front : Json) (units : List Unit) : Except String (List (String × Nat)) := do
  let openTerms ← match front.getObjValD "open_terms" with
    | .null => pure #[]
    | .arr xs => pure xs
    | _ => throw "open_terms must be a list"
  let sets ← match front.getObjValD "reading_sets" with
    | .null => pure #[]
    | .arr xs => pure xs
    | _ => throw "reading_sets must be a list"
  let labels := match (front.getObjValD "graph").getObjValD "nodes" with
    | .arr xs => xs.toList.filterMap fun (n : Json) =>
      (n.getObjVal? "label").toOption.bind (fun value => value.getStr?.toOption)
    | _ => []
  pure [("open_terms", openTerms.size),
    ("assumptions", (units.filter (·.support == "assumption")).length),
    ("bridge_leaves", (labels.filter (fun (label : String) => label.startsWith "bridge:accepts(")).length),
    ("unresolved_reading_sets", (sets.toList.filter (fun s => s.getObjValD "status" == .str "open")).length)]

def unitJson (u : Unit) : Json :=
  Json.mkObj ([("id", .str u.id), ("span", toJson [u.span.1, u.span.2]),
    ("kind", u.kind), ("meaning", u.meaning), ("support", .str u.support),
    ("status", .str u.status)] ++
    (u.parent.toList.map fun p => ("parent_id", .str p)))

/-- The shared W2 open-term decoder owns the names and the full schema. -/
def openNamesOf (environment : Json) (items : Json) : Except String (List String) := do
  let checked ← Standalone.validated environment
  let rv ← VE.Route.Run.decodeRouteVocabulary checked.envelope
  Loader.openTermNames rv items true (checked.envelope.profiles.contains "data@0")

def documentCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let text ← stringField j "document"
  let split ← Loader.splitTextWith allowedMetadata text
  unless !split.source.isEmpty do throw "document source is empty"
  let front := split.front
  let environment ← front.getObjVal? "environment"
  let _ ← Standalone.environmentCase (Json.mkObj
    [("id", .str id), ("environment", environment)])
  let raw ← match front.getObjValD "units" with
    | .arr xs => if xs.isEmpty then throw "document needs units" else pure xs.toList
    | _ => throw "document needs units"
  let openTerms := front.getObjValD "open_terms"
  let names ← if openTerms == .null then pure [] else openNamesOf environment openTerms
  let sets := front.getObjValD "reading_sets"
  unless sets == .null || sets == Json.arr #[] do
    throw "CheckerUnavailable: document reading sets require Lean reading-set composition"
  let profiles := (VE.Route.Gate.profilesOf environment).toOption.getD []
  if profiles.any (["reports@0", "alternatives@0", "risk@0", "soft-norms@0", "rights@0",
      "norm-defaults@0", "readings@1"].contains) then
    throw "CheckerUnavailable: document coverage requires its Lean profile route"
  let units ← unitsOf split.source environment names raw
  let byKind := counts units (kindName ∘ Unit.kind)
  let byStatus := counts units Unit.status
  let sourceBytes := split.source.utf8ByteSize
  unless (byKind.map Prod.snd).sum == sourceBytes && (byStatus.map Prod.snd).sum == sourceBytes do
    throw "coverage tables do not total the source bytes"
  let rest ← residual front units
  let payload := Loader.payload split (Json.mkObj [])
  let docId ← Loader.documentId payload
  let sourceId := Loader.sourceId profiles split.source
  let cov := Json.mkObj [("source_bytes", toJson sourceBytes), ("accounted_bytes", toJson sourceBytes),
    ("coverage_percent", toJson (100 : Nat)), ("bytes_by_kind", countJson byKind),
    ("bytes_by_status", countJson byStatus), ("unformalised_reasons", countJson (reasons units)),
    ("residual", countJson rest), ("residual_total", toJson ((rest.map Prod.snd).sum))]
  pure (VE.Route.Wire.ok id [("document_id", .str docId), ("source_id", .str sourceId),
    ("source", .str split.source), ("units", toJson (units.map unitJson)), ("coverage", cov)])

def runCaseReported (j : Json) : Json := Standalone.reported documentCase j

end VE.Service.Document
