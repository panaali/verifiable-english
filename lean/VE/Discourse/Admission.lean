import VE.Discourse.Wire

/-! # `admitDiscourse` over `ve-document@2` (docs/spec/discourse.md 3.5, 4.1, 4.5, 4.7, 4.8)

The profile adapter: `ve.discourse@1` is outside the frozen profile registry, so the wrapper
validates the original envelope, then calls every frozen function on
`(baseProfiles, baseEnvironment)`, the profile list and the environment JSON without it, as
`Norms/Replay.lean` does for `norms@0`. A `ve-document@1` input is delegated unchanged to
`VE.Route.Admission.admitDocument` when the profile is off, and is the profile-gate error when
it is on.

A `@2` document is admitted in this order: import and embedding integrity (4.1(10)), the
nesting budget, the wrapper (3.5), the source, units and manifest under the base pair,
`definitions_version`, the document sort, `wellFormed` (4.1(2)-(8), which validates every
bound unit), the recorded bound content, the projection to W2 (each bound unit's elaborated
formula in place of its content; a unit whose presupposition has no carrier stays pending
and gets no content), the unchanged W2 admission on the base pair, the post-admission table
checks (groups, carriers, labels), the composition gate (4.8) and the second phase: validity
claims from the three outcomes of 4.7. Identities are computed under the base pair and the
wrapper report binds the original profile list. -/
namespace VE.Discourse
open Lean
open VE.Route.Admission (Doc DocUnit WireNode AssertedUnit parseLabel)
open VE.Route (Wire.RouteVocabulary)

/-! ## The profile adapter (3.5) -/

def discourseProfile : String := "ve.discourse@1"

def baseProfiles (profiles : List String) : List String := profiles.filter (· != "ve.discourse@1")

def baseEnvironment (environment : Json) : Json :=
  environment.setObjVal! "profiles" (toJson (baseProfiles ((VE.Route.Gate.profilesOf environment).toOption.getD [])))

def formatOf (j : Json) : Option String := (j.getObjValD "format").getStr?.toOption

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

/-! ## The result -/

/-- 4.7: the three outcomes of checking another document; rejection is a completed diagnostic. -/
def outcomeOf' {α : Type} : Except String α → ImportOutcome
  | .ok _ => .admitted
  | .error e => if e.startsWith "ResourceLimit" then .unknown e else .rejected e

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

def outcomeOf : Except String Admitted → ImportOutcome := outcomeOf'

def emptyManifest : Manifest :=
  ⟨"", "", [], [], [], [], [], [], [], [], [], [], []⟩

/-- The asserted units with content: the document's premises. -/
def premiseUnitsOf (b : VE.Route.Admission.Admitted) : List String :=
  (b.doc.units.filter fun x => decide (x.kind = .asserted) && x.content.isSome).map DocUnit.id

/-- A `@1` admission seen as a discourse result with an empty manifest. -/
def lift1 (res : VE.Route.Admission.Admitted) : Admitted :=
  { doc := ⟨res.rv.environment, res.doc, emptyManifest, "", fun _ => none⟩, base := res, projected := .null,
    documentId := "", reportId := "", bound := fun _ => none, joint := .error "UnsupportedProfile: no discourse manifest",
    presuppositions := fun _ => none, pending := [], validity := fun _ => none, selfTruth := [],
    premiseUnits := premiseUnitsOf res }

/-! ## Imports and embedded documents -/

def parsedOf (b : ByteArray) : Json := ((VE.JsonInput.parse ((String.fromUTF8? b).getD "")).toOption).getD .null
def envOf (b : ByteArray) : Json := (parsedOf b).getObjValD "environment"
def jsonOf (b : ByteArray) : Json := (parsedOf b).getObjValD "document"

def emptyRV : Wire.RouteVocabulary :=
  { vocabulary := ⟨[], [], []⟩, literals := [], nodup := List.nodup_nil, definitions := [], chain := trivial }

def rvOf (b : ByteArray) : Wire.RouteVocabulary :=
  let env := envOf b
  let ps := (VE.Route.Gate.profilesOf env).toOption.getD []
  (VE.Route.Wire.decodeVocabulary (baseProfiles ps) (env.getObjValD "vocabulary")).toOption.getD emptyRV

/-- The source identity of a stored document: the fingerprint of its prose. -/
def sourceIdOf (b : ByteArray) : String := Wire.sourceId (Wire.prose (jsonOf b))

def importsOf (j : Json) : List Import :=
  ((Wire.decodeManifest (j.getObjValD "discourse")).toOption.map Manifest.imports).getD []

/-- The byte slice of a unit of the prose. -/
def unitBytes (prose : String) (x : DocUnit) : ByteArray := prose.toUTF8.extract x.start x.stop

/-- The source ids reachable through the stored imports, to depth `n`. -/
def importChain : Nat → List ByteArray → Option (List String)
  | _, [] => some []
  | 0, _ :: _ => none
  | n + 1, b :: bs => do
    let inner := (importsOf (jsonOf b)).filterMap Import.bytes
    let rest ← importChain n inner
    let more ← importChain (n + 1) bs |>.orElse fun _ => none
    pure (sourceIdOf b :: rest ++ more)
termination_by n bs => (n, bs.length)
decreasing_by all_goals simp_wf <;> omega

/-- The import graph of the stored chain: each document's source id names the source ids it
imports (to depth `n`). -/
def importNodesAt : Nat → List ByteArray → List VE.Route.DepNode
  | 0, _ => []
  | n + 1, bs => bs.flatMap fun b =>
      let K := importsOf (jsonOf b)
      ⟨sourceIdOf b, K.map Import.sourceId⟩ :: importNodesAt n (K.filterMap Import.bytes)

def dedupNodes : List VE.Route.DepNode → List VE.Route.DepNode
  | [] => []
  | n :: ns => if (ns.map VE.Route.DepNode.name).contains n.name then dedupNodes ns else n :: dedupNodes ns

/-- The import graph of a document: its own node, then the stored chain. -/
def importNodes (D : DDoc) : List VE.Route.DepNode :=
  dedupNodes (⟨D.sourceId, D.K.imports.map Import.sourceId⟩ :: importNodesAt 4 (D.K.imports.filterMap Import.bytes))

/-- The nesting depth of the stored chain (5 means beyond the budget). -/
def chainDepth : Nat → List ByteArray → Nat
  | _, [] => 0
  | 0, _ :: _ => 5
  | n + 1, bs => 1 + (bs.map fun b => chainDepth n ((importsOf (jsonOf b)).filterMap Import.bytes)).foldl max 0

def depthOf (D : DDoc) : Nat := chainDepth 5 (D.K.imports.filterMap Import.bytes)

/-- 4.1(10): stored bytes re-fingerprint to their pins, the chain has no repeated source id,
and nesting is within the budget. -/
def integrityOk (j : Json) (K : Manifest) : Except String Unit := runAll [
  fun _ => allOk K.imports fun imp => match imp.bytes with
    | some b => req (sourceIdOf b == imp.sourceId)
        ("StaleTarget: " ++ ((K.documents.find? fun d => d.refers == .imported imp.key).map DocName.name).getD imp.key)
    | none => .ok (),
  fun _ => match dupOf (K.imports.map Import.key) with
    | some k => .error ("DuplicateDeclaration: import " ++ k)
    | none => .ok (),
  fun _ => match importChain 4 (K.imports.filterMap Import.bytes) with
    | none => .error "ResourceLimit: document nesting"
    | some ids =>
      let own := Wire.sourceId (Wire.prose j)
      match dupOf (own :: ids) with
      | some i => .error ("ImportCycle: " ++ i)
      | none => .ok ()]

/-! ## The discourse admission -/

/-- The graph nodes of a document object, decoded as W2 does. -/
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

/-- The W2 document object with each bound unit's elaborated formula as its content. -/
def projectUnits (j : Json) (content : String → Option VE.Formula) : Json :=
  match j.getObjValD "units" with
  | .arr us => Json.arr (us.map fun u => match (u.getObjValD "id").getStr?.toOption.bind content with
      | some A => u.setObjVal! "content" (VE.Route.Wire.encodeFormula A)
      | none => u)
  | other => other

def project (j : Json) (content : String → Option VE.Formula) : Json :=
  let keep := ["graph", "lemmas", "open_terms", "reading_sets", "narrowings"]
  match j with
  | .obj kvs => Json.mkObj (("units", projectUnits j content) ::
      kvs.toList.filter fun (k, _) => keep.contains k)
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

def groupStatus (D : DDoc) (g : Group) : String :=
  match groupFormula D g with
  | some _ => if ((D.base.readingSets.find? fun rs => rs.id == g.set && rs.version == g.version).map
      (·.readings.length)) == some 1 then "CHECKED" else "OPEN"
  | none => "UNFORMALISED"

/-- Post-admission checks on the W2 result: group readings, fragments, labels. -/
def postOk (D : DDoc) (b : VE.Route.Admission.Admitted) (bound : String → Option VE.Formula) : Except String Unit :=
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
        !(premiseUnitsOf b).contains u && (b.report.assumptions.all fun l => l.label != "asserted" || unitOfLeaf b l != some u))
      ("IndependentFragment: " ++ u)],
  fun _ => allOk D.K.validity fun v => req (!(premiseUnitsOf b).contains v.unit && (bound v.unit).isNone)
    ("InvalidInput: validity unit " ++ v.unit),
  fun _ => allOk D.K.selfTruth fun u => req (!(premiseUnitsOf b).contains u && (bound u).isNone &&
      (unitOf D.base u).bind DocUnit.content == none)
    ("InvalidInput: self-truth unit " ++ u),
  fun _ => match dupOf (D.K.validity.map Validity.unit) with
    | some u => .error ("DuplicateDeclaration: validity " ++ u)
    | none => .ok (),
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
    req (!D.K.selfTruth.contains u && !(D.K.validity.map Validity.unit).contains u) ("IndependentFragment: " ++ u),
  fun _ => match VE.Route.dependencyOrder (importNodes D) with
    | .ok _ => .ok ()
    | .error e => .error ("ImportCycle: " ++ e),
  fun _ => req (decide (depthOf D ≤ 4)) "ResourceLimit: document nesting"]

/-- The second phase: a validity claim's verdict from the outcome of checking its document. -/
def verdictFor (D : DDoc) (prose : String) (check : ByteArray → ImportOutcome) (v : Validity) : Option Verdict :=
  match D.K.documents.find? (·.name == v.document) with
  | some d => match d.refers with
    | .self => some (if v.holds then .checked else .refuted)
    | .imported k => match D.K.imports.find? (·.key == k) with
      | some imp => match imp.bytes with
        | none => some (.unconfirmed "import bytes absent")
        | some b => some (verdictOf v.holds (check b))
      | none => none
    | .embedded u => match unitOf D.base u with
      | some x => some (verdictOf v.holds (check (unitBytes prose x)))
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

/-- The `@2` admission at a positive nesting budget; `check` evaluates an embedded or
imported document one level down. -/
def admit2 (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json)
    (check : ByteArray → ImportOutcome) : Except String Admitted := do
  wrapperOk profiles environment j
  let bp := baseProfiles profiles
  let be := baseEnvironment environment
  let data := bp.contains "data@0"
  let prose ← VE.Bridge.stringField j "prose"
  let K₀ ← Wire.decodeManifest (← j.getObjVal? "discourse")
  let base₀ ← VE.Route.Admission.decodeDoc rv data j
  let base := { base₀ with literals := rv.literals, flags := rv.flags }
  req (base.units.all fun x => decide (x.stop ≤ prose.utf8ByteSize)) "InvalidInput: unit span outside the prose"
  let src : Wire.Source := ⟨prose, lex prose⟩
  let K ← Wire.toTokenSpans src base K₀
  let D : DDoc := ⟨rv.environment, base, K, Wire.sourceId prose, src.text base⟩
  let envId ← VE.Route.Wire.environmentId bp be
  req (K.definitionsVersion == envId) ("StaleTarget: definitions@" ++ K.definitionsVersion)
  req (rv.vocabulary.constants.all fun (c, s) => s != K.documentSort || K.documents.any (·.name == c))
    ("InvalidInput: document sort " ++ K.documentSort ++ " has other constants")
  wellFormed D
  let boundAll : String → Option VE.Formula := fun u =>
    if (boundUnits D).contains u then (validate D u).toOption else none
  allOk (boundUnits D) fun u => match (unitOf base u).bind DocUnit.content, boundAll u with
    | some c, some A => req (c == A) ("ManifestMismatch: bound." ++ u)
    | _, _ => .ok ()
  -- pending units, decided on the submitted graph before projection
  let pre := pendingIn D (rawWires rv data j) base (((base.units.filter fun x =>
    decide (x.kind = .asserted) && x.content.isSome).map DocUnit.id))
  let projected := project j fun u => if (pre.map Prod.fst).contains u then none else boundAll u
  let res ← VE.Route.Admission.admitDocument bp be rv projected
  let premises := premiseUnitsOf res
  let pending := pendingIn D res.wires res.doc premises
  let bound : String → Option VE.Formula := fun u =>
    if (pending.map Prod.fst).contains u || (pre.map Prod.fst).contains u then none else boundAll u
  postOk D res bound
  let joint := compatibleChoices K (activeSets D) 64
  jointGate res joint
  let validity : String → Option Verdict := fun u =>
    (K.validity.find? (·.unit == u)).bind (verdictFor D (Wire.prose j) check)
  let documentId ← Wire.documentId2 (Wire.frontMatter j) (Wire.prose j) (Wire.fences j)
  let innerReportId ← VE.CertificateWire.digest s!"ve-report-{VE.Route.Wire.identityVersion bp}\n"
    (Json.mkObj [("environment_id", .str envId), ("document", projected), ("report", reportJson res.report)])
  let references := Json.arr (K.mentions.map fun m => Json.mkObj [("mention", .str m.id),
    ("status", .str (if (pending.map Prod.snd).contains ("PresuppositionUnresolved: " ++ m.id) then "pending" else
      if formulaForm m.form then "resolved" else "navigation"))]).toArray
  let validityJson := Json.arr (K.validity.map fun v => Json.mkObj [("unit", .str v.unit),
    ("verdict", .str ((validity v.unit).map verdictText |>.getD "none"))]).toArray
  let reportId ← VE.CertificateWire.digest "ve-discourse-report@1\n" (Json.mkObj [
    ("profiles", toJson profiles), ("environment_id", .str envId), ("document_id", .str documentId),
    ("report_id", .str innerReportId), ("references", references), ("validity", validityJson)])
  let presuppositions : String → Option PresuppositionCarrier := fun id =>
    ((presupMentions D).find? (·.id == id)).bind (carrierIn D res.wires res.doc premises)
  pure { doc := D, base := res, projected, documentId, reportId, bound, joint, presuppositions, pending,
         validity, selfTruth := K.selfTruth, premiseUnits := premises }

/-- One admission step: `@1` delegation, then (for `@2`) the manifest, integrity, the
nesting budget (`none` is an exhausted budget) and `admit2`. -/
def admitAt (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json)
    (check : Option (ByteArray → ImportOutcome)) : Except String Admitted :=
  if formatOf j == some "ve-document@1" || formatOf j == none then
    if profiles.contains discourseProfile then .error "UnsupportedProfile: ve.discourse@1 requires ve-document@2"
    else (VE.Route.Admission.admitDocument profiles environment rv j).map lift1
  else if formatOf j != some "ve-document@2" then .error "InvalidInput: unknown document format"
  else match Wire.decodeManifest (j.getObjValD "discourse") with
    | .error e => .error e
    | .ok K₀ => match integrityOk j K₀ with
      | .error e => .error e
      | .ok _ => match check with
        | none => .error "ResourceLimit: document nesting"
        | some c => admit2 profiles environment rv j c

/-- The discourse admission with a nesting budget: the second phase checks other documents
one level down. -/
def admitDiscourse (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json) :
    Nat → Except String Admitted
  | 0 => admitAt profiles environment rv j none
  | n + 1 => admitAt profiles environment rv j (some fun b =>
      outcomeOf (admitDiscourse profiles (envOf b) (rvOf b) (jsonOf b) n))

/-- Checking a stored or embedded document one level down. -/
def checkImport (profiles : List String) (b : ByteArray) (fuel : Nat) : ImportOutcome :=
  outcomeOf (admitDiscourse profiles (envOf b) (rvOf b) (jsonOf b) fuel)

def statusOf (res : Admitted) (u : String) : String :=
  if res.selfTruth.contains u then "LABELLED"
  else match res.validity u with
  | some .checked => "CHECKED"
  | some _ => "LABELLED"
  | none => match groupOf res.doc u with
    | some g => groupStatus res.doc g
    | none => if (res.pending.map Prod.fst).contains u then "PENDING"
      else match (unitOf res.base.doc u).bind DocUnit.content with
        | some _ => "CHECKED"
        | none => "LABELLED"

end VE.Discourse
