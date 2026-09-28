import VE.Discourse.Wire

/-! # `admitDiscourse` over `ve-document@2` (docs/spec/discourse.md 3.5, 4.1, 4.5, 4.7, 4.8)

The profile adapter: `ve.discourse@1` is outside the frozen profile registry, so the wrapper
validates the original envelope, then calls every frozen function on
`(baseProfiles, baseEnvironment)`, the profile list and the environment JSON without it, as
`Norms/Replay.lean` does for `norms@0`. A `ve-document@1` input is delegated unchanged to
`VE.Route.Admission.admitDocument` when the profile is off (a loaded `@1` text through the
admission object its front matter translates to), and is the profile-gate error when it is on.

A `@2` document is its loaded text (`Loader`): the front matter, the source, the fences and the
sibling files. It is admitted in this order: the document table and the integrity of every
imported and embedded document (4.1(10): stored bytes re-fingerprint to the pinned `source_id`,
the declared pins agree with the import table, each stored document decodes and its recomputed
`document_id` is the pinned one, the chain has no repeated source id and is within depth 4), the
nesting budget, the wrapper (3.5), the front matter under the base pair, the manifest,
`definitions_version`, the document sort, `wellFormed` (4.1(2)-(8), which validates every bound
unit), the explicit statuses, the recorded bound content, the projection to W2 (each bound
unit's elaborated formula in place of its content; a unit whose presupposition has no carrier
stays pending and gets no content), the unchanged W2 admission on the base pair, the
post-admission table checks (groups, carriers, labels), the composition gate (4.8) and the
second phase: validity claims from the three outcomes of 4.7, each other document checked under
its own environment and profiles. Identities are the Python loader's (`source_id`,
`document_id`, the inner and wrapper report ids) under the base pair; the wrapper report binds
the original profile list. -/
namespace VE.Discourse
open Lean
open VE.Route.Admission (Doc DocUnit WireNode AssertedUnit parseLabel)
open VE.Route (Wire.RouteVocabulary)

/-! ## The profile adapter (3.5) -/

def discourseProfile : String := "ve.discourse@1"

def baseProfiles (profiles : List String) : List String := profiles.filter (· != "ve.discourse@1")

def baseEnvironment (environment : Json) : Json :=
  environment.setObjVal! "profiles" (toJson (baseProfiles ((VE.Route.Gate.profilesOf environment).toOption.getD [])))

/-- The document format: the `format` of a W2 admission object, else of a loaded front matter. -/
def formatOf (j : Json) : Option String :=
  match (j.getObjValD "format").getStr?.toOption with
  | some f => some f
  | none => ((Loader.metaOf j).getObjValD "format").getStr?.toOption

/-- The original envelope: sorted, unique, both base and discourse profiles, the environment's
`profiles` equal to the list, format `@2`; and the frozen gate on the base pair (FOL family). -/
def wrapperOk (profiles : List String) (environment : Json) (j : Json) : Except String Unit := runAll [
  fun _ => req (decide (profiles.Pairwise (· < ·))) (VE.Route.Gate.unsupported "profiles must be sorted and unique"),
  fun _ => req (profiles.contains "relational-fol@0") (VE.Route.Gate.unsupported "Missing profile relational-fol@0"),
  fun _ => req (profiles.contains discourseProfile) "UnsupportedProfile: ve-document@2 requires ve.discourse@1",
  fun _ => req (match VE.Route.Gate.profilesOf environment with | .ok ps => ps == profiles | .error _ => false)
    (VE.Route.Gate.unsupported "environment profiles differ from the declared list"),
  fun _ => req (formatOf j == some "ve-document@2") "UnsupportedProfile: ve.discourse@1 requires ve-document@2",
  fun _ => req (match VE.Route.Gate.profilesOf (baseEnvironment environment) with
      | .ok ps => ps == baseProfiles profiles
      | .error _ => false) (VE.Route.Gate.unsupported "base environment profiles"),
  fun _ => match VE.Route.Gate.decodeEnvelope (baseEnvironment environment) with
    | .ok e => req (e.family == .fol) (VE.Route.Gate.unsupported "discourse admission requires the FOL family")
    | .error e => .error e]

/-- The route vocabulary of the base pair. -/
def baseVocabulary (environment : Json) : Except String Wire.RouteVocabulary := do
  let e ← VE.Route.Gate.decodeEnvelope (baseEnvironment environment)
  VE.Route.Run.decodeRouteVocabulary e

/-! ## The result -/

/-- 4.7: the three outcomes of checking another document. Rejection is a completed
diagnostic; a resource limit, or a feature the Lean route does not implement, leaves the check
incomplete (`unknown`), never a rejection. -/
def outcomeOf' {α : Type} : Except String α → ImportOutcome
  | .ok _ => .admitted
  | .error e => if e.startsWith "ResourceLimit" || e.startsWith "NotImplemented" then .unknown e else .rejected e

structure Admitted where
  doc : DDoc
  base : VE.Route.Admission.Admitted
  projected : Json
  documentId : String
  reportId : String
  bound : String → Option VE.Formula
  joint : Except String (List Choice)
  presuppositions : String → Option PresuppositionCarrier
  pending : List (String × String)
  validity : String → Option Verdict
  selfTruth : List String
  premiseUnits : List String
  environmentId : String
  innerReportId : String
  boundIds : List (String × String)
  references : Json
  front : Loader.Front
  profiles : List String
  claims : List Validity

/-- Why a successful admission is still incomplete (4.1(8)): its joint set hit the budget, so the
admission and every reading-dependent verdict are UNKNOWN (`admitted: UNKNOWN`). -/
def jointUnknown : Except String (List Choice) → Option String
  | .error e => if e.startsWith "ResourceLimit" then some e else none
  | .ok _ => none

/-- A document's own outcome from its (successful) admission's joint set: `admitted` only when
the admission completed. -/
def selfOutcome (joint : Except String (List Choice)) : ImportOutcome :=
  match jointUnknown joint with
  | some e => .unknown e
  | none => .admitted

/-- 4.7: an admission that answers `admitted: UNKNOWN` is `unknown`, never `admitted`. -/
def outcomeOf : Except String Admitted → ImportOutcome
  | .ok res => selfOutcome res.joint
  | .error e => outcomeOf' (α := Unit) (.error e)

def emptyManifest : Manifest :=
  ⟨"", "", [], [], [], [], [], [], [], [], [], [], []⟩

/-- The asserted units with content: the document's premises. -/
def premiseUnitsOf (b : VE.Route.Admission.Admitted) : List String :=
  (b.doc.units.filter fun x => decide (x.kind = .asserted) && x.content.isSome).map DocUnit.id

/-- A `@1` admission seen as a discourse result with an empty manifest. -/
def lift1 (res : VE.Route.Admission.Admitted) : Admitted :=
  { doc := { E := res.rv.environment, base := res.doc, K := emptyManifest, sourceId := "", text := fun _ => none,
             sets := [], status := [], prose := "", files := .null },
    base := res, projected := .null,
    documentId := "", reportId := "", bound := fun _ => none, joint := .error "UnsupportedProfile: no discourse manifest",
    presuppositions := fun _ => none, pending := [], validity := fun _ => none, selfTruth := [],
    premiseUnits := premiseUnitsOf res, environmentId := "", innerReportId := "", boundIds := [],
    references := Json.arr #[], front := ⟨"", .null, [], [], []⟩, profiles := [], claims := [] }

/-! ## Imported and embedded documents (4.1(10)) -/

/-- A stored or embedded document text, loaded with the importing document's sibling files. -/
def storedPayload (files : Json) (b : ByteArray) : Except String Json := do
  match String.fromUTF8? b with
  | some t => pure (Loader.payload (← Loader.splitText t) files)
  | none => throw "document is not UTF-8"

def envOfPayload (p : Json) : Json := (Loader.metaOf p).getObjValD "environment"

/-- The source identity of stored bytes under their own base profiles (Python's `source_id`);
bytes that do not split as a document are fingerprinted whole. -/
def sourceIdOf (b : ByteArray) : String :=
  match (String.fromUTF8? b).map Loader.splitText with
  | some (.ok s) =>
    let ps := (VE.Route.Gate.profilesOf (s.front.getObjValD "environment")).toOption.getD []
    Loader.sourceId (baseProfiles ps) s.source
  | _ => VE.CertificateWire.sha256 b

/-- A loaded document's own source identity. -/
def ownSourceId (j : Json) : String :=
  let ps := (VE.Route.Gate.profilesOf (envOfPayload j)).toOption.getD []
  Loader.sourceId (baseProfiles ps) (Loader.sourceOf j)

/-- The raw byte span of a unit of the front matter. -/
def rawUnitSpan (j : Json) (u : String) : Option (Nat × Nat) :=
  match (Loader.metaOf j).getObjValD "units" with
  | .arr us => (us.toList.find? fun x => (x.getObjValD "id").getStr?.toOption == some u).bind fun x =>
      (Loader.spanOf (x.getObjValD "span")).toOption
  | _ => none

/-- The bytes of an embedded unit. -/
def embeddedBytes (j : Json) (u : String) : Option ByteArray :=
  (rawUnitSpan j u).map fun (a, b) => (Loader.sourceOf j).toUTF8.extract a b

/-- The document table and imports of a loaded document (`([], [])` when they do not decode). -/
def tablesOf (j : Json) : List DocName × List Import :=
  (Wire.decodeTables (Loader.filesOf j) ((Loader.metaOf j).getObjValD "discourse")).toOption.getD ([], [])

def importsOf (j : Json) : List Import := (tablesOf j).2

/-- The stored documents a loaded document names: stored import bytes and embedded units. -/
def storedOf (j : Json) (docs : List DocName) (imports : List Import) : List ByteArray :=
  imports.filterMap Import.bytes ++ docs.filterMap fun d => match d.refers with
    | .embedded u => embeddedBytes j u
    | _ => none

def childrenOf (files : Json) (b : ByteArray) : List ByteArray :=
  match storedPayload files b with
  | .ok p => storedOf p (tablesOf p).1 (tablesOf p).2
  | .error _ => []

/-- The source ids reachable through the stored chain, to depth `n` (`none`: deeper). -/
def importChain (files : Json) : Nat → List ByteArray → Option (List String)
  | _, [] => some []
  | 0, _ :: _ => none
  | n + 1, b :: bs => do
    let rest ← importChain files n (childrenOf files b)
    let more ← importChain files (n + 1) bs
    pure (sourceIdOf b :: rest ++ more)
termination_by n bs => (n, bs.length)
decreasing_by all_goals simp_wf <;> omega

/-- The name of the document declared over an import key. -/
def importName (docs : List DocName) (key : String) : String :=
  ((docs.find? fun d => d.refers == .imported key).map DocName.name).getD key

/-- The reading sets of a front matter by id, version and reading ids (their formulas are not
read): what decoding a discourse block needs to name readings (1.5). -/
def setIdsOf (front : Json) : List FrontSet :=
  match front.getObjValD "reading_sets" with
  | .arr xs => xs.toList.filterMap fun x => do
    let id ← (x.getObjValD "id").getStr?.toOption
    let unit ← (x.getObjValD "unit").getStr?.toOption
    let version ← (x.getObjValD "version").getNat?.toOption
    let status ← (x.getObjValD "status").getStr?.toOption
    let readings ← match x.getObjValD "readings" with
      | .arr rs => some rs.toList
      | _ => none
    pure ⟨id, unit, version, status, readings.filterMap fun r => (r.getObjValD "id").getStr?.toOption.map (·, .top)⟩
  | _ => []

/-- A stored document decodes (its text, envelope and, for `@2`, its whole discourse block, as
the importing document's own block is decoded) and carries the pinned identities. -/
def storedOk (files : Json) (name : String) (b : ByteArray) (sid did : Option String) : Except String Unit := do
  let fail := fun (e : String) => "InvalidInput: document " ++ name ++ ": " ++ e
  let p ← (storedPayload files b).mapError fail
  let env := envOfPayload p
  let _ ← (VE.Route.Gate.profilesOf env).mapError fail
  let _ ← (VE.Route.Gate.decodeEnvelope (baseEnvironment env)).mapError fail
  let block := (Loader.metaOf p).getObjValD "discourse"
  let _ ← (Wire.decodeTables (Loader.filesOf p) block).mapError fail
  if formatOf p == some "ve-document@2" then
    let _ ← (Wire.decodeManifest (setIdsOf (Loader.metaOf p)) (Loader.filesOf p) "" block).mapError fail
  if let some s := sid then req (sourceIdOf b == s) ("StaleTarget: " ++ name)
  let doc ← (Loader.documentId p).mapError fail
  if let some d := did then req (doc == d) ("StaleTarget: " ++ name)

/-- 4.1(10): stored bytes re-fingerprint to their pins, the declared pins agree with the
import table, every stored and embedded document decodes with its pinned `document_id`, the
chain has no repeated source id, and nesting is within the budget. -/
def integrityOk (j : Json) (docs : List DocName) (imports : List Import) : Except String Unit :=
  let files := j.getObjValD "files"
  runAll [
  fun _ => allOk imports fun imp => match imp.bytes with
    | some b => req (sourceIdOf b == imp.sourceId) ("StaleTarget: " ++ importName docs imp.key)
    | none => .ok (),
  fun _ => match dupOf (imports.map Import.key) with
    | some k => .error ("DuplicateDeclaration: import " ++ k)
    | none => .ok (),
  fun _ => allOk docs fun d => match d.refers with
    | .imported k => match imports.find? (·.key == k) with
      | some imp => req (d.sourceId == some imp.sourceId && d.documentId == some imp.documentId)
          ("ManifestMismatch: documents." ++ d.name)
      | none => .error ("UnknownDocument: " ++ d.name)
    | _ => .ok (),
  fun _ => allOk imports fun imp => match imp.bytes with
    | some b => storedOk files (importName docs imp.key) b (some imp.sourceId) (some imp.documentId)
    | none => .ok (),
  fun _ => allOk docs fun d => match d.refers with
    | .embedded u => match embeddedBytes j u with
      | some b => storedOk files d.name b d.sourceId d.documentId
      | none => .error ("UnknownDocument: " ++ d.name)
    | _ => .ok (),
  fun _ => match importChain files 4 (storedOf j docs imports) with
    | none => .error "ResourceLimit: document nesting"
    | some ids => match dupOf (ownSourceId j :: ids) with
      | some i => .error ("ImportCycle: " ++ i)
      | none => .ok ()]

/-- The import graph of a document (its stored imports and embedded units): each source id
names the source ids it embeds or imports, to depth 4. -/
def importNodesAt (files : Json) : Nat → List ByteArray → List VE.Route.DepNode
  | 0, _ => []
  | n + 1, bs => bs.flatMap fun b =>
      ⟨sourceIdOf b, (childrenOf files b).map sourceIdOf⟩ :: importNodesAt files n (childrenOf files b)

def dedupNodes : List VE.Route.DepNode → List VE.Route.DepNode
  | [] => []
  | n :: ns => if (ns.map VE.Route.DepNode.name).contains n.name then dedupNodes ns else n :: dedupNodes ns

/-- The stored documents of a discourse document. -/
def storedOfDoc (D : DDoc) : List ByteArray :=
  D.K.imports.filterMap Import.bytes ++ D.K.documents.filterMap fun d => match d.refers with
    | .embedded u => (unitOf D.base u).map fun x => D.prose.toUTF8.extract x.start x.stop
    | _ => none

def importNodes (D : DDoc) : List VE.Route.DepNode :=
  dedupNodes (⟨D.sourceId, (storedOfDoc D).map sourceIdOf⟩ :: importNodesAt D.files 4 (storedOfDoc D))

/-- The nesting depth of the stored chain (5 means beyond the budget). -/
def chainDepth (files : Json) : Nat → List ByteArray → Nat
  | _, [] => 0
  | 0, _ :: _ => 5
  | n + 1, bs => 1 + (bs.map fun b => chainDepth files n (childrenOf files b)).foldl max 0

def depthOf (D : DDoc) : Nat := chainDepth D.files 5 (storedOfDoc D)

/-! ## The discourse admission -/

/-- The graph nodes of a W2 admission object, decoded as W2 does. -/
def rawWires (rv : Wire.RouteVocabulary) (data : Bool) (j : Json) : List WireNode :=
  ((do
    let g ← j.getObjVal? "graph"
    let ns ← (← g.getObjVal? "nodes").getArr?
    ns.toList.mapM (VE.Route.Admission.decodeNode rv.environment data)).toOption.map (List.map Prod.fst)).getD []

def presupMentions (D : DDoc) : List Mention := D.K.mentions.filter (·.reading == some .presuppositional)

/-- The carrier of a presuppositional mention's `U(D)` in an admitted W2 result: a certified
unit-less `asserted` deduction node, or the explicit asserted unit it names. -/
def carrierIn (D : DDoc) (wires : List WireNode) (doc : Doc) (premises : List String) (m : Mention) :
    Option PresuppositionCarrier :=
  match m.restriction, restrictionSort D m with
  | some Dr, some σ =>
    match wires.find? (fun w => w.unit.isNone && w.deduction.isSome && w.claim.label == "asserted" &&
        w.claim.formula == uniqueD σ Dr) with
    | some w => some (.proved w.claim.name)
    | none => match m.presuppositionUnit with
      | some u => if decide (AssertedUnit doc u (uniqueD σ Dr)) && premises.contains u then some (.assumed u) else none
      | none => none
  | _, _ => none

def pendingIn (D : DDoc) (wires : List WireNode) (doc : Doc) (premises : List String) : List (String × String) :=
  (presupMentions D).filterMap fun m =>
    if carrierIn D wires doc premises m = none then some (m.unit, "PresuppositionUnresolved: " ++ m.id) else none

/-- A unit object without its `content` field. -/
def withoutContent : Json → Json
  | .obj kvs => Json.mkObj (kvs.toList.filter fun (k, _) => k != "content")
  | j => j

/-- The W2 document object with each bound unit's elaborated formula as its content, and no
content at all for a withheld unit (a pending presupposition, 4.5): a pending unit is never a
premise, whatever content it was submitted with; `project` also drops its reading sets. -/
def projectUnits (j : Json) (content : String → Option VE.Formula) (withheld : String → Bool) : Json :=
  match j.getObjValD "units" with
  | .arr us => Json.arr (us.map fun u =>
      let id := (u.getObjValD "id").getStr?.toOption
      match id.bind content with
      | some A => u.setObjVal! "content" (VE.Route.Wire.encodeFormula A)
      | none => if id.any withheld then withoutContent u else u)
  | other => other

/-- The W2 reading sets without the sets `withheldSet` names: a withheld unit's readings never
reach W2 either, so a label naming one is W2's unknown-set rejection. -/
def projectSets (j : Json) (withheldSet : String → Bool) : Json :=
  match j.getObjValD "reading_sets" with
  | .arr ss => Json.arr (ss.filter fun s => !(s.getObjValD "id").getStr?.toOption.any withheldSet)
  | other => other

def project (j : Json) (content : String → Option VE.Formula) (withheld : String → Bool)
    (withheldSet : String → Bool) : Json :=
  let keep := ["graph", "lemmas", "open_terms", "narrowings"]
  match j with
  | .obj kvs => Json.mkObj (("units", projectUnits j content withheld) ::
      ("reading_sets", projectSets j withheldSet) :: kvs.toList.filter fun (k, _) => keep.contains k)
  | _ => j

def unitOfLeaf (b : VE.Route.Admission.Admitted) (l : VE.Graph.Claim) : Option String :=
  (b.wires.find? fun w => w.claim == l && w.deduction.isNone).bind WireNode.unit

def setOfLabel (s : String) : Option (String × Nat) :=
  match parseLabel s with
  | some (.readings set v _) => some (set, v)
  | _ => none

def leafList (L : VE.Route.Admission.Lemma) : List VE.Definitions.Bundle.Leaf := L.leaves.map fun (f, l) => (l, f)

def reportLeaves (r : VE.Graph.Report) : List VE.Definitions.Bundle.Leaf := r.assumptions.map fun l => (l.label, l.formula)

/-- 4.8, the composition gate over a completed joint set. -/
def gateOk (b : VE.Route.Admission.Admitted) (cs : List Choice) : Except String Unit := runAll [
  fun _ => allOk b.doc.lemmas fun L => match VE.Definitions.Bundle.leafChoices (leafList L) with
    | .ok ch => req (cs.any (extendsTo ch)) ("InvalidCompatibility: citation " ++ L.name)
    | .error e => .error e,
  fun _ => match VE.Definitions.Bundle.leafChoices (reportLeaves b.report) with
    | .ok ch => req (cs.any (extendsTo ch)) ("InvalidCompatibility: report " ++ b.report.root.name)
    | .error e => .error e]

/-- The composition gate runs over a completed joint set; an unfinished one leaves it UNKNOWN. -/
def jointGate (b : VE.Route.Admission.Admitted) : Except String (List Choice) → Except String Unit
  | .ok cs => gateOk b cs
  | .error _ => .ok ()

/-- The group a unit belongs to (a unit is in at most one group). -/
def groupOf (D : DDoc) (u : String) : Option Group := D.K.groups.find? fun g => g.spans.contains u

/-- A unit's W2 status as the loader computed it (3.2); a unit the loader did not see (a `@1`
admission object) is CHECKED with content and LABELLED without. -/
def loadedStatus (D : DDoc) (u : String) : String :=
  match D.status.find? (·.1 == u) with
  | some (_, s) => s
  | none => if ((unitOf D.base u).bind DocUnit.content).isSome then "CHECKED" else "LABELLED"

/-- W2's status of a unit: a group span has its owning set's status, which W2 places on the
group's first span (1.5, 3.2). -/
def unitStatus (D : DDoc) (u : String) : String :=
  match groupOf D u with
  | some g => loadedStatus D (g.spans.headD u)
  | none => loadedStatus D u

/-- Post-admission checks on the W2 result: group readings, fragments, labels. -/
def postOk (D : DDoc) (b : VE.Route.Admission.Admitted) (bound : String → Option VE.Formula)
    (pending : List (String × String)) : Except String Unit :=
  runAll [
  fun _ => match dupOf (D.K.groups.flatMap Group.spans) with
    | some u => .error ("IndependentFragment: " ++ u)
    | none => .ok (),
  fun _ => allOk D.K.groups fun g => runAll [
    fun _ => req ((b.doc.readingSets.any fun rs => rs.id == g.set && rs.version == g.version &&
        (groupFormula D g).any fun φ => rs.readings[g.reading]? == some φ))
      ("InvalidInput: reading " ++ toString g.reading ++ " not in " ++ g.set ++ "@" ++ toString g.version),
    fun _ => req (decide ((b.report.assumptions.filter fun l => setOfLabel l.label = some (g.set, g.version)).length ≤ 1))
      ("IndependentFragment: " ++ ((g.spans.head?).getD g.set)),
    fun _ => allOk g.spans fun u => req ((unitOf b.doc u).bind DocUnit.content == none && (bound u).isNone &&
        !(premiseUnitsOf b).contains u && !(pending.map Prod.fst).contains u &&
        (b.report.assumptions.all fun l => l.label != "asserted" || unitOfLeaf b l != some u))
      ("IndependentFragment: " ++ u)],
  fun _ => allOk D.K.selfTruth fun u => req (!(premiseUnitsOf b).contains u && (bound u).isNone &&
      (unitOf D.base u).bind DocUnit.content == none)
    ("InvalidInput: self-truth unit " ++ u),
  fun _ => match dupOf (D.K.documents.map DocName.name) with
    | some d => .error ("DuplicateDeclaration: document " ++ d)
    | none => .ok (),
  fun _ => match dupOf (D.K.mentions.map Mention.id) with
    | some m => .error ("DuplicateDeclaration: mention " ++ m)
    | none => .ok (),
  fun _ => match dupOf (D.K.imports.map Import.key) with
    | some k => .error ("DuplicateDeclaration: import " ++ k)
    | none => .ok (),
  fun _ => allOk (D.K.groups.flatMap Group.spans) fun u =>
    req (!D.K.selfTruth.contains u) ("IndependentFragment: " ++ u),
  fun _ => match VE.Route.dependencyOrder (importNodes D) with
    | .ok _ => .ok ()
    | .error e => .error ("ImportCycle: " ++ e),
  fun _ => req (decide (depthOf D ≤ 4)) "ResourceLimit: document nesting"]

/-- The second phase: a validity claim's verdict from the outcome of checking its document;
`self` is this document's own outcome (`unknown` when its joint set hit the budget). -/
def verdictFor (D : DDoc) (self : ImportOutcome) (check : ByteArray → ImportOutcome) (v : Validity) :
    Option Verdict :=
  match D.K.documents.find? (·.name == v.document) with
  | some d => match d.refers with
    | .self => some (verdictOf v.holds self)
    | .imported k => match D.K.imports.find? (·.key == k) with
      | some imp => match imp.bytes with
        | none => some (.unconfirmed "import bytes absent")
        | some b => some (verdictOf v.holds (check b))
      | none => none
    | .embedded u => match unitOf D.base u with
      | some x => some (verdictOf v.holds (check (D.prose.toUTF8.extract x.start x.stop)))
      | none => some (.unconfirmed "embedded bytes absent")
    | .part _ => none
  | none => none

def claimJson (c : VE.Graph.Claim) : Json := VE.Route.Run.claimJson c

def reportJson (r : VE.Graph.Report) : Json :=
  Json.mkObj [("root", claimJson r.root), ("assumptions", Json.arr (r.assumptions.map claimJson).toArray)]

def verdictText : Verdict → String
  | .checked => "checked"
  | .refuted => "refuted"
  | .unconfirmed r => "unconfirmed (" ++ r ++ ")"

def locationForm (f : String) : Bool := f == "section_ref" || f == "navigation"

/-- 7.1: one reference line per recorded mention, in manifest order, with the recorded target:
`resolved` (elaborated and checked), `navigation` (a location binding) or `pending`. -/
def referencesJson (front : Json) (pending : List (String × String)) : Json :=
  let raw := match (front.getObjValD "discourse").getObjValD "mentions" with
    | .arr ms => ms.toList
    | _ => []
  Json.arr (raw.map fun m =>
    let id := (m.getObjValD "id").getStr?.toOption.getD ""
    let form := (m.getObjValD "form").getStr?.toOption.getD ""
    Json.mkObj [("mention", .str id), ("unit", m.getObjValD "unit"), ("form", .str form),
      ("target", m.getObjValD "target"),
      ("status", .str (if (pending.map Prod.snd).contains ("PresuppositionUnresolved: " ++ id) then "pending"
        else if locationForm form then "navigation" else "resolved"))]).toArray

/-- The prepared discourse document (the part of the admission before well-formedness): the
wrapper, the front matter under the base pair, the manifest and the token spans. -/
structure Prepared where
  doc : DDoc
  front : Loader.Front
  environmentId : String
  claims : List Validity

def prepare (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json) :
    Except String Prepared := do
  wrapperOk profiles environment j
  let bp := baseProfiles profiles
  let be := baseEnvironment environment
  let data := bp.contains "data@0"
  let envId ← VE.Route.Wire.environmentId bp be
  let front ← Loader.loadPayload rv bp envId j
  let prose := Loader.sourceOf j
  let K₀ ← Wire.decodeManifest front.sets (Loader.filesOf j) envId ((Loader.metaOf j).getObjValD "discourse")
  let base₀ ← VE.Route.Admission.decodeDoc rv data front.w2
  let base := { base₀ with literals := rv.literals, flags := rv.flags }
  let src : Wire.Source := ⟨prose, lex prose⟩
  let K ← Wire.toTokenSpans src base K₀
  -- the document the admission reads holds no validity binding (4.7): the bindings are kept
  -- apart and read only in the second phase
  pure ⟨{ E := rv.environment, base, K := { K with validity := [] }, sourceId := Loader.sourceId bp prose,
          text := src.text base, sets := front.sets, status := front.status, prose, files := j.getObjValD "files" },
        front, envId, K.validity⟩

/-- 3.3: every certificate of the admitted graph is bound to the environment identity under the
base pair, and a deduction formalising a bound unit is bound to the meaning id of that unit's
elaboration; every bound formula has a meaning id. -/
def bindingsOk (D : DDoc) (res : VE.Route.Admission.Admitted) (bound : String → Option VE.Formula)
    (bp : List String) (envId : String) : Except String Unit := runAll [
  fun _ => allOk (boundUnits D) fun u => match bound u with
    | some A => (VE.Route.Wire.meaningId bp envId (VE.Route.Wire.encodeFormula A)).map fun _ => ()
    | none => .ok (),
  fun _ => allOk res.wires fun w => match w.deduction with
    | none => .ok ()
    | some edge => runAll [
      fun _ => req (edge.certificate.environment_id == envId) ("StaleTarget: certificate " ++ w.claim.name),
      fun _ => match w.unit.bind bound with
        | some A => match VE.Route.Wire.meaningId bp envId (VE.Route.Wire.encodeFormula A) with
          | .ok mid => req (edge.certificate.conclusion_meaning_id == mid) ("StaleTarget: certificate " ++ w.claim.name)
          | .error e => .error e
        | none => .ok ()]]

/-- The validity-free core of a `@2` admission: everything W2 sees is computed from it. -/
structure CoreResult where
  base : VE.Route.Admission.Admitted
  projected : Json
  bound : String → Option VE.Formula
  pending : List (String × String)

/-- The core admission of a prepared document (called on the document with every validity
binding removed, 4.7): the document checks, the projection, W2 on the base pair, the table
checks after it and the certificate bindings. -/
def admitCore (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (D : DDoc)
    (front : Loader.Front) (envId : String) : Except String CoreResult := do
  let K := D.K
  let base := D.base
  let bp := baseProfiles profiles
  let be := baseEnvironment environment
  let data := bp.contains "data@0"
  req (K.definitionsVersion == envId) ("StaleTarget: definitions@" ++ K.definitionsVersion)
  req (rv.vocabulary.constants.all fun (c, s) => s != K.documentSort || K.documents.any (·.name == c))
    ("InvalidInput: document sort " ++ K.documentSort ++ " has other constants")
  wellFormed D
  Loader.explicitOk (D.status.map fun (u, _) => (u, unitStatus D u)) front.explicit
  let boundAll : String → Option VE.Formula := fun u =>
    if (boundUnits D).contains u then (validate D u).toOption else none
  -- a bound unit's recorded meaning, its content and every reading of its active set, is its
  -- elaboration: a reading set is never a way around slot regeneration
  allOk (boundUnits D) fun u => match boundAll u with
    | some A => req (((unitOf base u).bind DocUnit.content).all (· == A) &&
        (D.sets.filter (·.unit == u)).all fun rs => rs.readings.all fun x => x.2 == A)
        ("ManifestMismatch: bound." ++ u)
    | none => .ok ()
  -- pending units, decided on the submitted graph before projection
  let pre := pendingIn D (rawWires rv data front.w2) base (((base.units.filter fun x =>
    decide (x.kind = .asserted) && x.content.isSome).map DocUnit.id))
  let withheld : String → Bool := fun u => (pre.map Prod.fst).contains u
  -- a unit with an active reading set speaks through its readings only (W2 drops its content);
  -- a withheld unit's content and reading sets never reach W2
  let projected := project front.w2 (fun u => if withheld u || setUnit D u then none else boundAll u)
    withheld (fun s => D.sets.any fun rs => rs.id == s && withheld rs.unit)
  let res ← VE.Route.Admission.admitDocument bp be rv projected
  let premises := premiseUnitsOf res
  let pending := pendingIn D res.wires res.doc premises
  -- a carrier that was itself withheld leaves its mention pending after projection: fail closed
  req (pending == pre) "InvalidInput: a presupposition carrier is itself pending"
  let bound : String → Option VE.Formula := fun u =>
    if (pending.map Prod.fst).contains u || (pre.map Prod.fst).contains u then none else boundAll u
  postOk D res bound pending
  bindingsOk D res bound bp envId
  pure ⟨res, projected, bound, pending⟩

/-- The second phase's table checks: a validity claim is never a premise and never bound. -/
def validityPostOk (D : DDoc) (claims : List Validity) (b : VE.Route.Admission.Admitted)
    (bound : String → Option VE.Formula) : Except String Unit := runAll [
  fun _ => allOk claims fun v => req (!(premiseUnitsOf b).contains v.unit && (bound v.unit).isNone)
    ("InvalidInput: validity unit " ++ v.unit),
  fun _ => match dupOf (claims.map Validity.unit) with
    | some u => .error ("DuplicateDeclaration: validity " ++ u)
    | none => .ok (),
  fun _ => allOk (D.K.groups.flatMap Group.spans) fun u =>
    req (!(claims.map Validity.unit).contains u) ("IndependentFragment: " ++ u)]

/-- The label a lemma's leaves carry for a reading set, with the manifest's recorded choice in
place of a concrete one (via `original_index`, 1.5); `v:all` is kept (it selects no branch). -/
def recordedLabel (ρ : List (String × Nat × Nat)) (set label : String) : String :=
  match ρ.find? (·.1 == set) with
  | some (_, v, i) => if label == toString v ++ ":all" then label else toString v ++ ":" ++ toString i
  | none => label

/-- 9.4: a lemma's reading choices, as the manifest records them. -/
def choicesAsLabels (ρ : List (String × Nat × Nat)) (L : VE.Route.Admission.Lemma) : List (String × String) :=
  ((VE.Definitions.Bundle.leafChoices (leafList L)).toOption.getD []).map fun (s, r) => (s, recordedLabel ρ s r)

/-- The recorded reading choices are the lemmas' labels (`manifest_choices_are_labels`). -/
def choicesOk (K : Manifest) (b : VE.Route.Admission.Admitted) : Except String Unit :=
  allOk b.doc.lemmas fun L => match VE.Definitions.Bundle.leafChoices (leafList L) with
    | .ok ch => req (ch == choicesAsLabels K.choices L) ("ManifestMismatch: choices." ++ L.name)
    | .error e => .error e

/-- The wrapper report identity (3.3). -/
def wrapperReportId (profiles : List String) (envId documentId innerReportId : String) (references validity : Json) :
    Except String String :=
  VE.CertificateWire.digest "ve-discourse-report@1\n" (Json.mkObj [
    ("profiles", toJson profiles), ("environment_id", .str envId), ("document_id", .str documentId),
    ("report_id", .str innerReportId), ("references", references), ("validity", validity)])

/-- The validity lines of the report. -/
def validityJsonOf (claims : List Validity) (validity : String → Option Verdict) : Json :=
  Json.arr (claims.map fun v => Json.mkObj [("unit", .str v.unit),
    ("verdict", .str ((validity v.unit).map verdictText |>.getD "none"))]).toArray

/-- The `@2` admission at a positive nesting budget; `check` evaluates an embedded or
imported document one level down. The core admits the prepared document, which holds no
validity binding; the bindings are checked and evaluated only in the second phase (4.7). -/
def admit2 (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json)
    (check : ByteArray → ImportOutcome) : Except String Admitted := do
  let P ← prepare profiles environment rv j
  let C ← admitCore profiles environment rv P.doc P.front P.environmentId
  let D := P.doc
  let K := D.K
  let envId := P.environmentId
  let bp := baseProfiles profiles
  let res := C.base
  -- the second phase: the validity bindings and the composition gate
  claimsOk D P.claims
  validityPostOk D P.claims res C.bound
  choicesOk K res
  let joint := compatibleChoices K (activeSets D) 64
  jointGate res joint
  let validity : String → Option Verdict := fun u =>
    (P.claims.find? (·.unit == u)).bind (verdictFor D (selfOutcome joint) check)
  let documentId ← Loader.documentId j
  let innerReportId ← VE.CertificateWire.digest s!"ve-report-{VE.Route.Wire.identityVersion bp}\n"
    (Json.mkObj [("environment_id", .str envId), ("document", .str documentId), ("report", reportJson res.report)])
  let references := referencesJson (Loader.metaOf j) C.pending
  let reportId ← wrapperReportId profiles envId documentId innerReportId references (validityJsonOf P.claims validity)
  let boundIds ← (boundUnits D).eraseDups.filterMapM fun u => match C.bound u with
    | some A => do pure (some (u, ← VE.Route.Wire.meaningId bp envId (VE.Route.Wire.encodeFormula A)))
    | none => pure none
  let premises := premiseUnitsOf res
  let presuppositions : String → Option PresuppositionCarrier := fun id =>
    ((presupMentions D).find? (·.id == id)).bind (carrierIn D res.wires res.doc premises)
  pure { doc := D, base := res, projected := C.projected, documentId, reportId, bound := C.bound, joint,
         presuppositions, pending := C.pending, validity, selfTruth := K.selfTruth, premiseUnits := premises,
         environmentId := envId, innerReportId, boundIds, references, front := P.front, profiles,
         claims := P.claims }

/-- A loaded `@1` text: its front matter's admission object, under its own (discourse-free)
profiles. -/
def admit1 (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json) :
    Except String VE.Route.Admission.Admitted := do
  let envId ← VE.Route.Wire.environmentId profiles environment
  let front ← Loader.loadPayload rv profiles envId j
  Loader.explicitOk front.status front.explicit
  VE.Route.Admission.admitDocument profiles environment rv front.w2

/-- One admission step: `@1` delegation, then (for `@2`) the document table, integrity, the
nesting budget (`none` is an exhausted budget) and `admit2`. -/
def admitAt (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json)
    (check : Option (ByteArray → ImportOutcome)) : Except String Admitted :=
  if formatOf j == some "ve-document@1" || formatOf j == none then
    if profiles.contains discourseProfile then .error "UnsupportedProfile: ve.discourse@1 requires ve-document@2"
    else if Loader.isPayload j then (admit1 profiles environment rv j).map lift1
    else (VE.Route.Admission.admitDocument profiles environment rv j).map lift1
  else if formatOf j != some "ve-document@2" then .error "InvalidInput: unknown document format"
  else if !Loader.isPayload j then .error "InvalidInput: a ve-document@2 input is its document text"
  else match Wire.decodeTables (Loader.filesOf j) ((Loader.metaOf j).getObjValD "discourse") with
    | .error e => .error e
    | .ok (docs, imports) => match integrityOk j docs imports with
      | .error e => .error e
      | .ok _ => match check with
        | none => .error "ResourceLimit: document nesting"
        | some c => admit2 profiles environment rv j c

/-- Checking a stored document with a given admission: under its own environment and profiles
(never the importing document's). -/
def outcomeWith (check : List String → Json → Wire.RouteVocabulary → Json → Except String Admitted)
    (files : Json) (b : ByteArray) : ImportOutcome :=
  match storedPayload files b with
  | .error e => .unknown ("InvalidInput: " ++ e)
  | .ok p =>
    let env := envOfPayload p
    match VE.Route.Gate.profilesOf env, baseVocabulary env with
    | .ok ps, .ok rv => outcomeOf (check ps env rv p)
    | .error e, _ => .rejected e
    | _, .error e => .rejected e

/-- The discourse admission with a nesting budget: the second phase checks other documents
one level down, each under its own environment. -/
def admitDiscourse (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json) :
    Nat → Except String Admitted
  | 0 => admitAt profiles environment rv j none
  | n + 1 => admitAt profiles environment rv j (some (outcomeWith
      (fun ps env rv' p => admitDiscourse ps env rv' p n) (j.getObjValD "files")))

/-- Checking a stored or embedded document one level down. -/
def checkImport (files : Json) (b : ByteArray) (fuel : Nat) : ImportOutcome :=
  outcomeWith (fun ps env rv p => admitDiscourse ps env rv p fuel) files b

/-- 4.1(8), 4.8: the verdicts that depend on reading choices, UNKNOWN when the joint set's
validation did not complete: every lemma's citation extension and the report's. -/
def readingVerdicts (res : Admitted) : List (String × String) :=
  match res.joint with
  | .error e => if e.startsWith "ResourceLimit" then
      (res.base.doc.lemmas.map fun L => ("citation " ++ L.name, "UNKNOWN (joint choices)")) ++
      [("report " ++ res.base.report.root.name, "UNKNOWN (joint choices)")]
    else []
  | .ok _ => []

/-- 3.2: a self-truth unit is LABELLED; a validity claim is CHECKED when its verdict is
`checked`, LABELLED otherwise; a pending unit (4.5) is OPEN (no new status, 13.12); every other
unit has W2's status (a group span its owning set's). -/
def statusOf (res : Admitted) (u : String) : String :=
  if res.selfTruth.contains u then "LABELLED"
  else match res.validity u with
  | some .checked => "CHECKED"
  | some _ => "LABELLED"
  | none => if (res.pending.map Prod.fst).contains u then "OPEN" else unitStatus res.doc u

end VE.Discourse
