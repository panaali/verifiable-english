import VE.Discourse.Positions
import VE.Discourse.ComposeKeys
import VE.Compose.Dispatch
import VE.Service.Document

/-! # Discourse on the chain: documents, cases and the composed admission (docs/spec/discourse.md 14.4 to 14.6)

A `ve.discourse@1` document with a chain construct (14.2, `chainConstructs`) on a list with `norms@0` takes the
composed path: the wrapper checks of 3.5 (1), the document table and integrity, `definitions_version`, the manifest
checks of 4.1 with `resolveDocument` (`chainChecks`: `resolveWith`, the `@1` part under the document mode's
`Document.check` on its front matter and fence-free source, then today's `wellFormed` on `chainDDoc`,
`composed_wellFormed`), and the admission of the route `dispatch` chooses for the base list on `chainDocument` of the
resolved payload. Every other input is today's `admitDiscourse` (`composed_unchanged`).

Item cmp-s4 builds the composed path without the fence compiler's slot steps (14.3 steps 1 and 3 to 7, item
cmp-s4ab), so four inputs are named abstentions on it, as the loader's are today (11): a fenced unit
(`NotImplemented: fenced content on the chain`), a body fence no unit binds (the loader's own
`NotImplemented: fenced English or strict content`, `Loader.fencesOk`; so no fence goes unread, `composed_fenceless`),
a prose unit with a recorded formula-producing mention (`NotImplemented: a bound prose unit on the chain`), and the
groups, constraints, validity claims and reading sets of 14.5 step 1. A JSON content with such a mention is `MentionNotSlot` (14.3 step 6). Every other content's
`resolveContent` answer is the content as written (`resolve_identity`: it has no slot), so `resolveDocument`
answers its input. -/
namespace VE.Discourse
open Lean

/-! ## The composed path (14.2) -/

/-- The content keys of a chain construct (14.2). -/
def chainKeys : List String := ["norm", "right", "right_lines", "limitation", "bar", "fence"]

/-- The one key of a unit's or part's `content`, if it has exactly one. -/
def contentKey (u : Json) : Option String :=
  match u.getObjValD "content" with
  | .obj kvs => match kvs.toList with
    | [(k, _)] => some k
    | _ => none
  | _ => none

/-- The units of a front matter, each `MIXED` unit followed by its parts. -/
def unitsAndParts (front : Json) : List Json :=
  ((front.getObjValD "units").getArr?.toOption.getD #[]).toList.flatMap fun u =>
    u :: ((u.getObjValD "parts").getArr?.toOption.getD #[]).toList

def chainConstructs (environment j : Json) : Bool :=
  let vocabulary := environment.getObjValD "vocabulary"
  let predicates := match vocabulary.getObjValD "predicates" with
    | .obj kvs => kvs.toList.map Prod.snd
    | _ => []
  (vocabulary.getObjVal? "soft").toBool || (vocabulary.getObjVal? "rights").toBool ||
    predicates.any (fun p => (p.getObjVal? "regulated").toBool) ||
    (unitsAndParts (Loader.metaOf j)).any fun u => (contentKey u).any chainKeys.contains

/-! ## Documents and cases (14.4) -/

/-- The route `dispatch` chooses for the base list, run on the base environment and a resolved document. -/
def dispatchAdmission (ps : List String) (environment document : Json) : Except String Json :=
  match VE.Compose.dispatch ps with
  | .ok .norms => VE.Norms.Run.runAdmission "" environment document
  | .ok .normDefaults => VE.NormDefaults.Run.runAdmission "" environment document
  | .ok .soft => VE.SoftNorms.Run.runAdmission "" environment document
  | .ok .rights => VE.Rights.Run.runAdmission "" environment document
  | .ok .readings => .error "UnsupportedProfile: ve.discourse@1 with readings@1"
  | .ok .clauses => .error "UnsupportedProfile: ve.discourse@1 with right-clauses@0"
  | .ok r => .error (VE.Compose.refusal "ve.discourse@1" r)
  | .error e => .error e

/-- 14.5 step 1's chain decoder: the environment decoder of the route `dispatch` chooses for the base list, run
without a document (each checks the FOL family); a list no chain route reads is `dispatchAdmission`'s refusal. -/
def chainEnvironment (ps : List String) (be : Json) : Except String VE.Norms.Wire.NormsEnvironment :=
  match VE.Compose.dispatch ps with
  | .ok .norms => VE.Norms.Wire.decodeNormsEnvironment be
  | .ok .normDefaults => VE.NormDefaults.Wire.decodeEnvironmentU be
  | .ok .soft => (VE.SoftNorms.Phases.checkSource be (.arr #[])).map (·.ne) |>.mapError (·.message)
  | .ok .rights => (·.se.ne) <$> VE.Rights.Wire.decodeRightsEnvironment be
  | _ => match dispatchAdmission ps be .null with
    | .error e => .error e
    | .ok _ => .error (VE.Route.Gate.unsupported "discourse admission requires the FOL family")

/-- `chainBase` over a decoded base environment `ne` (`chainEnvironment`'s, read once on the composed path). -/
def chainBaseWith (ne : VE.Norms.Wire.NormsEnvironment) (environment j : Json) :
    Except String (VE.Route.Wire.RouteVocabulary × Manifest × String) := do
  let be := baseEnvironment environment
  let bp := baseProfiles ((VE.Route.Gate.profilesOf environment).toOption.getD [])
  let canonical ← VE.Norms.Wire.canonicalEnvironmentJson be
  let envId ← VE.Route.Wire.environmentId bp canonical
  let K ← Wire.decodeManifest [] (Loader.filesOf j) envId ((Loader.metaOf j).getObjValD "discourse")
  pure (ne.rv, K, envId)

/-- The chain decoder's vocabulary of the base pair (`chainEnvironment`: `chainDDoc` reads it), the manifest of
a loaded payload, and the chain route's environment id of the base pair (the id its certificates bind, 14.5 step 3). -/
def chainBase (environment j : Json) : Except String (VE.Route.Wire.RouteVocabulary × Manifest × String) := do
  let be := baseEnvironment environment
  chainBaseWith (← chainEnvironment (baseProfiles ((VE.Route.Gate.profilesOf environment).toOption.getD [])) be)
    environment j

/-- 14.3 step 6 and the abstentions of this item, for one unit or part: a JSON content keeps its answer (it has
no slot), a fenced content and a bound prose unit are named abstentions. -/
def contentOk (K : Manifest) (u : Json) : Except String Unit :=
  let ms := formulaMentions K ((u.getObjValD "id").getStr?.toOption.getD "")
  let bound := Loader.notImplemented "a bound prose unit on the chain"
  match contentKey u with
  | some "fence" => .error (Loader.notImplemented "fenced content on the chain")
  | some k => if chainKeys.contains k then (match ms with
      | m :: _ => .error ("MentionNotSlot: " ++ m.id)
      | [] => .ok ())
    else if ms.isEmpty then .ok () else .error bound
  | none => if ms.isEmpty then .ok () else .error bound

/-- `resolveDocument` over a decoded manifest: each unit's and part's `contentOk`, then the loader's refusal of a body
fence no unit binds (`Loader.fencesOk`; a bound fence is `contentOk`'s abstention). -/
def resolveWith (K : Manifest) (j : Json) : Except String Json := do
  (unitsAndParts (Loader.metaOf j)).forM (contentOk K)
  Loader.fencesOk (Loader.fencesOf j)
  pure j

/-- The `@2` payload with every formula position closed: each bound prose unit's content is today's projection
    (`project`, its `validate` formula, a pending unit withheld as today); each content-bearing unit's and part's
    content is its `resolveContent` answer in its route's wire form; each fenced unit's content replaces its
    `{"fence": …}` and its fence is removed from `fences`. Every other byte of the payload is kept. -/
def resolveDocument (environment j : Json) : Except String Json := do
  let (_, K, _) ← chainBase environment j
  resolveWith K j

/-- A resolved payload written out as a `ve-document@1` text over `source`: its front matter with `environment` the
base environment, `format` `ve-document@1` and no `discourse` key. -/
def writtenText (environment r : Json) (source : String) : Json :=
  let front := match ((Loader.metaOf r).setObjVal! "environment" (baseEnvironment environment)).setObjVal! "format"
      (.str "ve-document@1") with
    | .obj kvs => Json.obj (kvs.erase "discourse")
    | f => f
  .str ("---\n" ++ front.compress ++ "\n---\n" ++ source)

/-- A unit or part as W2 reads it on the composed path: its id, span and kind, and its content only when it is an
`ast` formula (a chain content is no W2 formula: the chain route reads it, `chainUnit`). -/
def formulaUnit (u : Json) : Json :=
  Json.mkObj ([("id", u.getObjValD "id"), ("span", u.getObjValD "span"), ("kind", u.getObjValD "kind")] ++
    match (u.getObjValD "content").getObjVal? "ast" with
    | .ok f => [("content", f)]
    | .error _ => [])

/-- The document `prepare` builds, on the composed path (14.5 step 4): the mentions on tokens, W2's units carrying
their `ast` formulas, each chain content's unit a unit with meaning (`DDoc.chain`); the document sort checked as
today. -/
def chainDDoc (rv : VE.Route.Wire.RouteVocabulary) (environment j : Json) (K : Manifest) : Except String DDoc := do
  let bp := baseProfiles ((VE.Route.Gate.profilesOf environment).toOption.getD [])
  let front := Loader.metaOf j
  let units := (← (← (front.getObjValD "units").getArr?).toList.mapM Loader.partsOf).flatten
  let openTerms := ((Loader.optionalList front "open_terms").getArr?.toOption.getD #[]).map (·.getObjValD "name")
  let base₀ ← VE.Route.Admission.decodeDoc rv (bp.contains "data@0") (Json.mkObj [
    ("units", .arr (units.map formulaUnit).toArray), ("lemmas", Loader.optionalList front "lemmas"),
    ("open_terms", .arr openTerms)])
  let base := { base₀ with literals := rv.literals, flags := rv.flags }
  let prose := Loader.sourceOf j
  let src : Wire.Source := ⟨prose⟩
  let tokK ← Wire.toTokenSpans src base K
  documentSortOk rv tokK
  let chain := (units.filter fun u => (contentKey u).any chainKeys.contains).filterMap fun u =>
    (u.getObjValD "id").getStr?.toOption
  pure
    { E := rv.environment, base, K := tokK, sourceId := Loader.sourceId bp prose, text := src.text base, sets := [],
      status := [], prose, files := j.getObjValD "files", nouns := sortNouns environment, chain }

/-- 14.5 steps 4 and 5 on a payload, its resolved payload: the manifest checks of 4.1 with this item's steps of
14.3. In order: `resolveWith` (each unit's 14.3 step 6 and this item's abstentions, `contentOk`, then the loader's
refusal of an unbound body fence); 4.1(1), the `@1` part (`Document.check` without the claim graph, on the
written-out text under the base pair: its front matter and the fence-free source, which is the whole body once
`resolveWith` has refused every fence; every unit check, the byte partition and each chain content's own checks);
then `wellFormed` (4.1(2) to (8)) on `chainDDoc`. These are the functions today's admission runs. -/
def chainChecks (rv : VE.Route.Wire.RouteVocabulary) (environment j : Json) (K : Manifest) : Except String Json := do
  let resolved ← resolveWith K j
  let _ ← VE.Service.Document.check (← (writtenText environment j (Loader.sourceOf j)).getStr?) (withGraph := false)
  wellFormed (← chainDDoc rv environment j K)
  pure resolved

/-- What `resolveWith` passes has no body fence (review cmp-s4 F7): the source `Document.check` reads is the whole
body. -/
theorem resolveWith_fenceless (K : Manifest) (j r : Json) (h : resolveWith K j = .ok r) : Loader.fencesOf j = [] := by
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, hf, _⟩ := VE.Order.ProfileGate.bind_ok h
  cases hfs : Loader.fencesOf j with
  | nil => rfl
  | cons _ _ => simp [Loader.fencesOk, hfs] at hf

/-- What `chainChecks` passes is a well-formed document (4.1) whose resolved payload is `resolveWith`'s. -/
theorem chainChecks_wellFormed (rv : VE.Route.Wire.RouteVocabulary) (environment j r : Json) (K : Manifest)
    (h : chainChecks rv environment j K = .ok r) :
    resolveWith K j = .ok r ∧ ∃ D, chainDDoc rv environment j K = .ok D ∧ wellFormed D = .ok () := by
  unfold chainChecks at h
  obtain ⟨_, hr, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨D, hD, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, hw, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  exact ⟨hr, D, hD, hw⟩

/-- The environment (`E` before any generated symbol: the declared vocabulary the chain's decoder reads, norms
    4.1) and the manifest of a case `{"id", "document"}`, from its document's front matter, under the base pair. -/
def caseManifest (j : Json) : Except String (VE.Environment × Manifest) := do
  let s ← Loader.splitText (← VE.Bridge.stringField j "document")
  let environment := s.front.getObjValD "environment"
  let p := Loader.payload s (j.getObjValD "files")
  let b ← chainBase environment p
  -- a manifest handed out has passed 14.5 step 4, as the composed path's has
  let _ ← chainChecks b.1 environment p b.2.1
  pure (b.1.environment, b.2.1)

/-- A manifest `caseManifest` hands out is the manifest of a well-formed document (14.5 step 4). -/
theorem caseManifest_wellFormed (j : Json) (E : VE.Environment) (K : Manifest) (h : caseManifest j = .ok (E, K)) :
    ∃ rv environment p D, chainDDoc rv environment p K = .ok D ∧ wellFormed D = .ok () := by
  unfold caseManifest at h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, hc, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  exact ⟨_, _, _, (chainChecks_wellFormed _ _ _ _ _ hc).2⟩

/-- `f` on each field of an object, its key kept; any other value unchanged. -/
def editObj (f : String → Json → Json) : Json → Json
  | .obj kvs => .obj (kvs.map f)
  | j => j

/-- `f` on each element of an array; any other value unchanged. -/
def editArr (f : Json → Json) : Json → Json
  | .arr xs => .arr (xs.map f)
  | j => j

/-- A unit with its `content` set to `null`, and each of its parts. -/
def unitFree (u : Json) : Json :=
  editObj (fun k v => if k == "content" then .null
    else if k == "parts" then editArr (editObj fun k v => if k == "content" then .null else v) v else v) u

/-- A front matter without the keys resolution rewrites: `environment.profiles`, `format`, `discourse`, and every
unit's and part's `content` (`null`). -/
def frontShape (front : Json) : Json :=
  match editObj (fun k v => if k == "units" then editArr unitFree v
      else if k == "environment" then (match v with | .obj e => .obj (e.erase "profiles") | v => v) else v) front with
  | .obj kvs => .obj ((kvs.erase "format").erase "discourse")
  | front => front

/-- A document text's source and its front matter's shape, as canonical text. -/
def textShape (d : Json) : Option (String × String) := do
  let s ← (Loader.splitText (← d.getStr?.toOption)).toOption
  pure (s.source, (frontShape s.front).compress)

/-- A case's id and its document's shape (`textShape`). -/
def caseParts (j : Json) : Option String × Option (String × String) :=
  ((j.getObjValD "id").getStr?.toOption, textShape (j.getObjValD "document"))

/-- What resolution may not touch: a payload with every unit's and part's `content` set to `null` and `fences`
    emptied; for a case, its id, the source, and the front matter with `environment.profiles`, `format` and
    `discourse` removed and every `content` set to `null`. -/
def contentFree (j : Json) : Json :=
  editObj (fun k v => if k == "metadata" then editObj (fun k v => if k == "units" then editArr unitFree v else v) v
    else if k == "fences" then Json.mkObj [] else v) j
def caseShape (j : Json) : Json :=
  let (id, shape) := caseParts j
  Json.mkObj [("id", match id with | some i => .str i | none => .null),
    ("document", match shape with | some (source, front) => Json.arr #[.str source, .str front] | none => .null)]

/-- `resolveCase` on a case that lists `ve.discourse@1`. -/
def resolveOn (j : Json) : Except String Json := do
  let d := j.getObjValD "document"
  let s ← Loader.splitText (← d.getStr?)
  let environment := s.front.getObjValD "environment"
  let r ← resolveDocument environment (Loader.payload s (j.getObjValD "files"))
  let text := writtenText environment r s.source
  -- regenerated, never trusted (3.4): the written-out text must keep the case's source and front matter
  let j' := j.setObjVal! "document" text
  if caseParts j' == caseParts j then pure j' else throw "InvalidInput: the resolved text does not keep the document's shape"

/-- RESOLVE on a case: the case with its `document` replaced by the written-out text of `resolveDocument` under the
    front matter's environment: the front matter's `environment` replaced by `baseEnvironment` of it, `format`
    `ve-document@1`, the `discourse` key removed, printed as `"---\n" ++ front.compress ++ "\n---\n" ++ body`, the body
    being the case's body with its fences removed. A case whose profiles lack `ve.discourse@1` is unchanged. -/
def resolveCase (j : Json) : Except String Json :=
  if (VE.Service.Document.profilesOf j).contains "ve.discourse@1" then resolveOn j else pure j

theorem resolveDocument_keeps (environment j r : Json) (h : resolveDocument environment j = .ok r) :
    contentFree r = contentFree j := by
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h; rfl

theorem resolveCase_keeps (j j' : Json) (h : resolveCase j = .ok j') : caseShape j' = caseShape j := by
  unfold resolveCase at h
  split at h
  · unfold resolveOn at h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    simp only at h
    split at h
    · rename_i hs
      cases h
      unfold caseShape
      rw [beq_iff_eq.mp hs]
    · cases h
  · cases h; rfl

theorem resolveCase_off (j : Json) (h : "ve.discourse@1" ∉ VE.Service.Document.profilesOf j) : resolveCase j = .ok j := by
  have : (VE.Service.Document.profilesOf j).contains "ve.discourse@1" = false := by simpa using h
  simp only [resolveCase, this, Bool.false_eq_true, ↓reduceIte]; rfl


/-! ## The composed admission (14.5) -/

/-- A unit or part of a resolved front matter as the chain route reads it: its id, span and kind, and its content
in wire form (an `ast` content its formula, any other content as written). -/
def chainUnit (u : Json) : Json :=
  Json.mkObj ([("id", u.getObjValD "id"), ("span", u.getObjValD "span"), ("kind", u.getObjValD "kind")] ++
    match u.getObjVal? "content" with
    | .ok c => [("content", (c.getObjVal? "ast").toOption.getD c)]
    | .error _ => [])

/-- The W2 admission object of a resolved payload, each unit's content in its route's wire form: norm, rights and
    resolved fence contents passed through, built without `baseVocabulary` or `loadPayload` (the loader's
    `admissionObject` holds formulas only, `Loader.lean`). -/
def chainDocument (environment resolved : Json) : Except String Json := do
  let front := Loader.metaOf resolved
  let graph ← (front.getObjVal? "graph").mapError fun _ => Loader.notImplemented "a document without a claim graph"
  let units ← (← (front.getObjValD "units").getArr?).toList.mapM Loader.partsOf
  let openTerms := ((Loader.optionalList front "open_terms").getArr?.toOption.getD #[]).map (·.getObjValD "name")
  -- no reading sets and no narrowings: step 1 refuses reading sets, and `chainChecks`'s load refuses a narrowing
  -- that cites none (`narrowing cites unknown reading set version`)
  pure (Json.mkObj [("units", Json.arr (units.flatten.map chainUnit).toArray), ("graph", graph),
    ("lemmas", Loader.optionalList front "lemmas"), ("open_terms", .arr openTerms),
    ("reading_sets", .arr #[]), ("narrowings", .arr #[])])

/-- The composed path's result. -/
structure ChainAdmitted where
  route : VE.Compose.Route         -- `dispatch (baseProfiles profiles)`
  resolved : Json                  -- `resolveDocument`'s answer
  inner : Json                     -- the chain route's answer, verbatim
  documentId : String              -- the `@2` `document_id` (3.3)
  reportId : String                -- the wrapper report id (3.5 (4)) over `inner`'s report id
  references : Json                -- the reference lines (7.1)

inductive Composed
  | today (res : Admitted)         -- today's discourse admission
  | chain (c : ChainAdmitted)

/-- Every `conditional_on` list of an answer, in pre-order. -/
def conditionalOnOf (a : Json) : List Json :=
  match a with
  | .obj ⟨⟨t⟩⟩ => tree t
  | .arr ⟨xs⟩ => list xs
  | _ => []
where
  tree : Std.DTreeMap.Internal.Impl String (fun _ => Json) → List Json
    | .leaf => []
    | .inner _ k v l r => tree l ++
        ((if k == "conditional_on" then (match v with | .arr _ => [v] | _ => []) else []) ++ conditionalOnOf v) ++
        tree r
  list : List Json → List Json
    | [] => []
    | x :: xs => conditionalOnOf x ++ list xs

/-- 14.5 step 1's named abstentions: groups, compatibility constraints, validity claims and reading sets. -/
def chainAbstentions (front : Json) : Except String Unit := do
  let d := front.getObjValD "discourse"
  for (key, name) in [("groups", "groups"), ("constraints", "constraints"), ("validity", "validity claims")] do
    if (d.getObjValD key).getArr?.toOption.any (!·.isEmpty) then throw (Loader.notImplemented (name ++ " on the chain"))
  if (front.getObjValD "reading_sets").getArr?.toOption.any (!·.isEmpty) then throw (Loader.notImplemented "reading sets on the chain")

/-- The reference lines of a front matter (7.1), refused if one carries a `conditional_on` list (regenerated,
never trusted: the mention decoder admits no such key). -/
def chainReferences (front : Json) : Except String Json :=
  let r := referencesJson front []
  if (conditionalOnOf r).isEmpty then .ok r else .error "InvalidInput: a reference line carries conditional_on"

/-- The composed path (14.5 steps 1 to 7; step 1's family check is `chainEnvironment`, whose decoded environment
step 3 reads; step 4 is `chainChecks`). The chain document is charged against `Loader.maxDocumentBytes`, the
loader's limit on a document text, before the chain route reads it. -/
def admitChain (profiles : List String) (environment j : Json) : Except String ChainAdmitted := do
  runAll (envelopeChecks profiles environment j)
  let be := baseEnvironment environment
  let ne ← chainEnvironment (baseProfiles profiles) be
  chainAbstentions (Loader.metaOf j)
  let tables := tablesOf j
  integrityOk j tables.1 tables.2
  let b ← chainBaseWith ne environment j
  req (b.2.1.definitionsVersion == b.2.2) ("StaleTarget: definitions@" ++ b.2.1.definitionsVersion)
  let resolved ← chainChecks b.1 environment j b.2.1
  let route ← VE.Compose.dispatch (baseProfiles profiles)
  let d ← chainDocument be resolved
  req (d.compress.utf8ByteSize ≤ Loader.maxDocumentBytes) "ResourceLimit: chain document bytes"
  let inner ← dispatchAdmission (baseProfiles profiles) be d
  let documentId ← Loader.documentId j
  let references ← chainReferences (Loader.metaOf j)
  let reportId ← wrapperReportId profiles b.2.2 documentId
    ((inner.getObjValD "report_id").getStr?.toOption.getD "") references (Json.mkObj [])
  pure ⟨route, resolved, inner, documentId, reportId, references⟩

/-- The discourse route's entry from S4 on (14.2: the composed path, else today's). -/
def admitComposed (profiles : List String) (environment j : Json) : Except String Composed :=
  if "norms@0" ∈ profiles ∧ "ve.discourse@1" ∈ profiles ∧ chainConstructs environment j = true then
    .chain <$> admitChain profiles environment j
  else match baseVocabulary environment with
    | .ok rv => (admitDiscourse profiles environment rv j fuelBudget).map .today
    | .error e => .error e

/-- The members of `composedJson`, in key order. -/
def composedFields (c : ChainAdmitted) : List (String × Json) :=
  [("document_id", .str c.documentId), ("inner", c.inner),
    ("inner_report_id", .str ((c.inner.getObjValD "report_id").getStr?.toOption.getD "")),
    ("references", c.references), ("report_id", .str c.reportId)]

/-- The wire answer of a composed admission: the wrapper fields of 3.5 (4) and 7, and `inner` verbatim. -/
def composedJson (c : ChainAdmitted) : Json :=
  Json.mkObj (composedFields c)

theorem admitChain_of (profiles : List String) (environment j : Json) (c : ChainAdmitted)
    (h : admitComposed profiles environment j = .ok (.chain c)) :
    ("norms@0" ∈ profiles ∧ "ve.discourse@1" ∈ profiles ∧ chainConstructs environment j = true) ∧
      admitChain profiles environment j = .ok c := by
  unfold admitComposed at h
  split at h
  · rename_i hc
    refine ⟨hc, ?_⟩
    cases ha : admitChain profiles environment j <;> rw [ha] at h <;> cases h; rfl
  · split at h
    · cases ha : admitDiscourse profiles environment _ j fuelBudget <;> rw [ha] at h <;> cases h
    · cases h

/-- The envelope checks fix the environment's profile list. -/
theorem envelopeChecks_profiles (profiles : List String) (environment j : Json)
    (h : runAll (envelopeChecks profiles environment j) = .ok ()) :
    VE.Route.Gate.profilesOf environment = .ok profiles := by
  unfold envelopeChecks at h
  simp only [runAll_cons, runAll_nil, and_true] at h
  obtain ⟨_, _, _, h4, _⟩ := h
  cases hq : VE.Route.Gate.profilesOf environment with
  | error e => rw [hq] at h4; simp [req] at h4
  | ok ps => rw [hq] at h4; simp only [req_ok, beq_iff_eq] at h4; rw [h4]

/-- On the composed path, `chainBase` is the decoded environment's `chainBaseWith`. -/
theorem chainBase_of (profiles : List String) (environment j : Json) (ne : VE.Norms.Wire.NormsEnvironment)
    (hw : runAll (envelopeChecks profiles environment j) = .ok ())
    (hne : chainEnvironment (baseProfiles profiles) (baseEnvironment environment) = .ok ne) :
    chainBase environment j = chainBaseWith ne environment j := by
  simp only [chainBase, envelopeChecks_profiles profiles environment j hw, Except.toOption, Option.getD, hne]
  rfl

/-- The composed admission is the chain's admission of the resolved document. -/
theorem composed_admission (profiles : List String) (environment j : Json) (c : ChainAdmitted)
    (h : admitComposed profiles environment j = .ok (.chain c)) :
    resolveDocument environment j = .ok c.resolved ∧
      VE.Compose.dispatch (baseProfiles profiles) = .ok c.route ∧
      ∃ d, chainDocument (baseEnvironment environment) c.resolved = .ok d ∧
        dispatchAdmission (baseProfiles profiles) (baseEnvironment environment) d = .ok c.inner := by
  have h := (admitChain_of profiles environment j c h).2
  unfold admitChain at h
  obtain ⟨_, hw, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨ne, hne, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨b, hb, h⟩ := VE.Order.ProfileGate.bind_ok h
  rw [← chainBase_of profiles environment j ne hw hne] at hb
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨resolved, hr, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨route, hroute, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨d, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨inner, hi, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  refine ⟨?_, hroute, d, hd, hi⟩
  simp only [resolveDocument, hb]; exact (chainChecks_wellFormed _ _ _ _ _ hr).1

/-- Only the composed path answers `.chain`. -/
theorem composed_path (profiles : List String) (environment j : Json) (c : ChainAdmitted)
    (h : admitComposed profiles environment j = .ok (.chain c)) :
    "norms@0" ∈ profiles ∧ "ve.discourse@1" ∈ profiles ∧ chainConstructs environment j = true :=
  (admitChain_of profiles environment j c h).1


/-- 14.5 step 4: the composed path admits only a document that is well-formed (4.1) as `chainDDoc` reads it. -/
theorem composed_wellFormed (profiles : List String) (environment j : Json) (c : ChainAdmitted)
    (h : admitComposed profiles environment j = .ok (.chain c)) :
    ∃ b D, chainBase environment j = .ok b ∧ chainDDoc b.1 environment j b.2.1 = .ok D ∧ wellFormed D = .ok () := by
  have h := (admitChain_of profiles environment j c h).2
  unfold admitChain at h
  obtain ⟨_, hw, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨ne, hne, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨b, hb, h⟩ := VE.Order.ProfileGate.bind_ok h
  rw [← chainBase_of profiles environment j ne hw hne] at hb
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, hc, _⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, D, hD, hw⟩ := chainChecks_wellFormed _ _ _ _ _ hc
  exact ⟨b, D, hb, hD, hw⟩

/-- The composed path admits no document with a body fence: none goes unread (review cmp-s4 F7). -/
theorem composed_fenceless (profiles : List String) (environment j : Json) (c : ChainAdmitted)
    (h : admitComposed profiles environment j = .ok (.chain c)) : Loader.fencesOf j = [] := by
  obtain ⟨b, _, h⟩ := VE.Order.ProfileGate.bind_ok (composed_admission profiles environment j c h).1
  exact resolveWith_fenceless _ _ _ h

theorem chainReferences_ok (front r : Json) (h : chainReferences front = .ok r) : conditionalOnOf r = [] := by
  unfold chainReferences at h
  simp only at h
  split at h
  · rename_i he; cases h; exact List.isEmpty_iff.mp he
  · cases h

/-- Discourse 5 and composition.md 5.5: no binding discharges, hides or reorders a coherence, limitation or choice
    premise; every `conditional_on` list of the answer is the chain route's, in its order. -/
theorem conditions_retained (profiles : List String) (environment j : Json) (c : ChainAdmitted)
    (h : admitComposed profiles environment j = .ok (.chain c)) :
    conditionalOnOf (composedJson c) = conditionalOnOf c.inner := by
  have h := (admitChain_of profiles environment j c h).2
  unfold admitChain at h
  have hrefs : conditionalOnOf c.references = [] := by
    iterate 12 obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨r, hr, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    cases h; exact chainReferences_ok _ r hr
  simp only [composedJson, composedFields, Json.mkObj, Std.TreeMap.Raw.ofList, Std.DTreeMap.Raw.Const.ofList,
    Std.DTreeMap.Internal.Impl.Const.ofList, Std.DTreeMap.Internal.Impl.Const.insertMany]
  simp (config := {decide := true}) [Std.DTreeMap.Internal.Impl.insert, Std.DTreeMap.Internal.Impl.empty,
    Std.DTreeMap.Internal.Impl.balanceL, Std.DTreeMap.Internal.Impl.balanceR, Std.DTreeMap.Internal.Impl.size,
    conditionalOnOf, conditionalOnOf.tree, hrefs, cmp_i_d, cmp_ir_d, cmp_ir_i, cmp_rf_i, cmp_rf_ir, cmp_rp_i, cmp_rp_ir,
    cmp_rp_rf]

/-! ## Identity cases (14.6) -/

/-- Existing discourse documents are untouched (plan S4, rule 5; composition.md 13.5): off the composed path the
    answer is today's. -/
theorem composed_unchanged (profiles : List String) (environment j : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (hv : baseVocabulary environment = .ok rv)
    (h : "norms@0" ∉ profiles ∨ "ve.discourse@1" ∉ profiles ∨ chainConstructs environment j = false) :
    admitComposed profiles environment j = (admitDiscourse profiles environment rv j fuelBudget).map .today := by
  have hc : ¬("norms@0" ∈ profiles ∧ "ve.discourse@1" ∈ profiles ∧ chainConstructs environment j = true) := by
    rintro ⟨a, b, c⟩; rcases h with h | h | h <;> simp_all
  simp only [admitComposed, hc, ↓reduceIte, hv]

/-- The plan's statement, the case without `norms@0`. -/
theorem composed_base_unchanged (profiles : List String) (environment j : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (hv : baseVocabulary environment = .ok rv) (h : "norms@0" ∉ profiles) :
    admitComposed profiles environment j = (admitDiscourse profiles environment rv j fuelBudget).map .today :=
  composed_unchanged profiles environment j rv hv (.inl h)

/-- Off the composed path a vocabulary error is today's error. -/
theorem composed_unchanged_error (profiles : List String) (environment j : Json) (e : String)
    (hv : baseVocabulary environment = .error e)
    (h : "norms@0" ∉ profiles ∨ "ve.discourse@1" ∉ profiles ∨ chainConstructs environment j = false) :
    admitComposed profiles environment j = .error e := by
  have hc : ¬("norms@0" ∈ profiles ∧ "ve.discourse@1" ∈ profiles ∧ chainConstructs environment j = true) := by
    rintro ⟨a, b, c⟩; rcases h with h | h | h <;> simp_all
  simp only [admitComposed, hc, ↓reduceIte, hv]

end VE.Discourse
