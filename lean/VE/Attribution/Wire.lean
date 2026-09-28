import VE.Attribution.Bridge
import VE.Norms.Wire

/-! The `reports@0` wire decoder (spec 3, 4.1, 9.4). Nothing on the wire
supplies `E_reports`, a key, a generated name, a premise, an open term or a
bridge formula: they are regenerated from the decoded document.

* The environment is the P0 envelope with the reports gate in place of the
  frozen classifier's family check (`reportsGate`, a function around
  `VE.Route.Gate.classify`), and a `reports` block in the vocabulary
  (`{"holders": [...], "evidence": "<sort>"}`). Constants may carry an optional
  `verbalisation`; it is removed before the frozen P0 vocabulary decoder runs,
  and a holder's may not be "the stated assessment". The original environment
  JSON is kept for identity.
* The document is a W2 document whose units of kind `attributed` or `hedged`
  may carry `report`, `assessment` or `negated` content (the report units);
  every other unit is a W2 unit (asserted units with an `ast`, labelled units
  with none). The kind decoder is W2's with the act `wants` added. A report
  unit carries `meaning` and `support`; every unit's span, meaning and support
  are decoded (`decodeMeta`), checked by `metaOk` and hashed into `document_id`.
* Optional absent values are absent keys (`literal`, `reference_time`, a
  package's `content`): the frozen restricted JSON parser rejects `null`.
* `{"fence": …}` content (surface text) is not decoded by the Lean route. -/
namespace VE.Reports.Wire
open Lean
open VE.Bridge (exactFields fields stringField strings displayFields)
open VE.Route.Admission (Kind token require)

def language : String := VE.Route.Gate.language

/-! ## Environment -/

structure ReportsEnvironment where
  profiles : List String
  rv : VE.Route.Wire.RouteVocabulary
  holders : List String
  evidence : String
  /-- the raw environment, hashed for identity -/
  json : Json
  /-- the author's declared predicate names (4.1 step 7 counts them) -/
  predicateNames : List String

def decodeEnvironment (environment : Json) : Except String ReportsEnvironment := do
  exactFields environment ["language", "profiles", "spec_revision", "vocabulary"]
  let l ← stringField environment "language"
  require (l == language) (VE.Route.Gate.unsupported "Unsupported language")
  let ps ← VE.Route.Gate.profilesOf environment
  require (decide (ps.Pairwise (· < ·))) (VE.Route.Gate.unsupported "profiles must be sorted and unique")
  match reportsGate ps with
  | .error e => throw e
  | .ok () => pure ()
  let revision ← stringField environment "spec_revision"
  require (revision == VE.Route.Gate.specRevision)
    (VE.Route.Gate.unsupported s!"Unsupported specification revision {revision}")
  let vocab ← environment.getObjVal? "vocabulary"
  let block ← match vocab.getObjVal? "reports" with
    | .ok b => pure b
    | .error _ => throw (VE.Route.Gate.unsupported "reports@0 needs a reports block")
  displayFields vocab ["sorts", "predicates", "constants", "reports"] []
  exactFields block ["holders", "evidence"]
  let holders ← strings (← block.getObjVal? "holders")
  let evidence ← stringField block "evidence"
  let predicates ← fields (← vocab.getObjVal? "predicates")
  for (p, _) in predicates do
    require (!p.startsWith "reports__") s!"InvalidInput: author predicate {p} begins with reports__"
  let constants ← fields (← vocab.getObjVal? "constants")
  let stripped ← constants.mapM fun (c, e) => do
    match e.getObjVal? "verbalisation" with
    | .ok v =>
      VE.Bridge.displayString v
      pure ((c, Json.mkObj ((← fields e).filter (·.1 != "verbalisation"))), some (c, ← v.getStr?))
    | .error _ => pure ((c, e), none)
  let vocab' := Json.mkObj [("sorts", vocab.getObjValD "sorts"), ("predicates", vocab.getObjValD "predicates"),
    ("constants", Json.mkObj (stripped.map Prod.fst))]
  let rv ← VE.Route.Wire.decodeVocabulary (ps.erase reportsProfile) vocab'
  require rv.definitions.isEmpty "UnsupportedProfile: reports@0 with definitions@0 layers"
  require (!holders.isEmpty && holders.length ≤ 8 && holders.eraseDups.length == holders.length)
    "InvalidInput: holders must be 1 to 8 distinct sorts"
  for s in holders do
    require (rv.vocabulary.sorts.contains s) s!"UnknownSymbol: holder sort {s}"
  require (rv.vocabulary.sorts.contains evidence) "UnknownSymbol: evidence sort"
  for (c, w) in stripped.filterMap Prod.snd do
    -- ASCII case-insensitively: no holder may display as the assessment, even
    -- capitalised at the start of a sentence (2.1); Python compares alike.
    if w.toLower == "the stated assessment" && (rv.environment.constants c).any holders.contains then
      throw "InvalidInput: holder verbalisation reserved"
  pure ⟨ps, rv, holders, evidence, environment, predicates.map Prod.fst⟩

/-! ## Kinds: W2's decoder with the act `wants` -/

def reportActs : List String := VE.Route.Admission.acts ++ ["wants"]

def decodeKind : Nat → Json → Except String Kind
  | 0, _ => .error "ResourceLimit: kind depth exceeds 16"
  | _ + 1, .str s => match VE.Route.Admission.atomicKind s with
    | some k => .ok k
    | none => .error s!"unknown kind {s}"
  | n + 1, .arr a => match a.toList with
    | [.str "attributed", .str agent, .str act, body] =>
      if token agent && reportActs.contains act then (decodeKind n body).map (.attributed agent act)
      else .error "invalid attributed kind"
    | [.str "hedged", .str m, body] =>
      if VE.Route.Admission.modalities.contains m then (decodeKind n body).map (.hedged m)
      else .error "invalid hedged kind"
    | [.str "causal", .str r, c, e] =>
      if VE.Route.Admission.relations.contains r then
        match decodeKind n c, decodeKind n e with
        | .ok c', .ok e' => .ok (.causal r c' e')
        | .error m, _ => .error m
        | _, .error m => .error m
      else .error "invalid causal kind"
    | [.str "unformalised", .str r] =>
      if token r then .ok (.unformalised r) else .error "invalid unformalised reason"
    | _ => .error "invalid kind"
  | _ + 1, _ => .error "invalid kind"

/-! ## Content trees -/

/-- Section 8's text exactly (no unit suffix), as Python raises it. -/
def decodeAct : String → Except String Act
  | "says" => pure .says
  | "believes" => pure .believes
  | "wants" => pure .wants
  | "intends" => pure .intends
  | a => throw s!"UnsupportedAct: {a} (reports@0 admits says, believes, wants, intends)"

def decodeJudgment : String → Except String Judgment
  | "may" => pure .may
  | "probably" => pure .probably
  | j => throw s!"InvalidInput: unknown judgment {j}"

/-- A quoted W1 block: its pinned environment decoded by the frozen norms decoder. -/
def decodeNormNode (j : Json) : Except String Content := do
  exactFields j ["environment", "norms"]
  let env ← j.getObjVal? "environment"
  let src ← VE.Norms.Wire.decodeSource env (← j.getObjVal? "norms")
  let canonical ← VE.Norms.Wire.canonicalEnvironmentJson env
  let id ← VE.Route.Wire.environmentId src.ne.profiles canonical
  pure (.norm ⟨src.D.E, id, VE.Route.Background.literals src.D.lits, src.ne.profiles⟩ src.D)

/-- A quoted W3 package: its pinned environment decoded by the frozen P0 and W3
decoders, and its optional statement over that environment. -/
def decodeDefinitionNode (j : Json) : Except String Content := do
  displayFields j ["environment"] ["content"]
  let env ← j.getObjVal? "environment"
  let e ← VE.Route.Gate.decodeEnvelope env
  require (e.family == .fol && e.profiles.contains "definitions@0")
    (VE.Route.Gate.unsupported "a quoted definition package needs definitions@0 on the FOL family")
  let rv ← VE.Route.Wire.decodeVocabulary e.profiles e.vocabulary
  let id ← VE.Route.Wire.environmentId e.profiles env
  let st ← match j.getObjVal? "content" with
    | .ok c => do
      exactFields c ["ast"]
      pure (some (← VE.Route.Wire.decodeClosed rv.environment (← c.getObjVal? "ast")))
    | .error _ => pure none
  pure (.definition ⟨rv.environment, id, VE.Definitions.background rv.definitions rv.literals, e.profiles⟩
    rv.definitions st)

def decodeLiteral (o : Json) : Except String (Option String) :=
  match o.getObjVal? "literal" with
  | .ok (.str w) =>
    if w.isEmpty then throw "InvalidInput: literal"
    else if w.utf8ByteSize ≤ 4096 then pure (some w) else throw "ResourceLimit: literal bytes"
  | .ok _ => throw "InvalidInput: literal"
  | .error _ => pure none

/-- One content node, recursively (fuel bounds recursion; 4.1 step 4's depth
bound is checked by `WellFormedReports`). -/
def decodeContent (E : VE.Environment) (unit : String) : Nat → Json → Except String Content
  | 0, _ => throw "ResourceLimit: content depth"
  | n + 1, j => do
    let ks := (← fields j).map Prod.fst
    match ks with
    | ["ast"] => pure (.formula (← VE.Route.Wire.decodeClosed E (← j.getObjVal? "ast")))
    | ["fence"] => throw "UnsupportedProfile: fence content is not decoded by the Lean reports route"
    | ["report"] =>
      let r ← j.getObjVal? "report"
      displayFields r ["holder", "act", "context", "content"] ["literal"]
      let h ← stringField r "holder"
      let act ← decodeAct (← stringField r "act")
      let c ← stringField r "context"
      let lit ← decodeLiteral r
      let body ← decodeContent E unit n (← r.getObjVal? "content")
      pure (.report h act c body lit)
    | ["assessment"] =>
      let r ← j.getObjVal? "assessment"
      exactFields r ["judgment", "record", "content"]
      let jd ← decodeJudgment (← stringField r "judgment")
      let a ← stringField r "record"
      let body ← decodeContent E unit n (← r.getObjVal? "content")
      pure (.assessment jd a body)
    | ["negated"] =>
      let inner ← decodeContent E unit n (← j.getObjVal? "negated")
      require (inner.isReport || inner.isAssessment) s!"InvalidInput: negated operand in {unit}"
      pure (.negated inner)
    | ["norm"] => decodeNormNode (← j.getObjVal? "norm")
    | ["definition"] => decodeDefinitionNode (← j.getObjVal? "definition")
    | _ => throw s!"InvalidInput: invalid content for {unit}"

/-! ## Front matter -/

def decodeTense : String → Except String Tense
  | "present" => pure .present
  | "past" => pure .past
  | "perfect" => pure .perfect
  | t => throw s!"ContextTense: {t}"

def decodeContext (j : Json) : Except String Context := do
  displayFields j ["id", "tense", "description"] ["reference_time"]
  let id ← stringField j "id"
  require (token id) s!"InvalidInput: invalid context id {id}"
  let tense ← match decodeTense (← stringField j "tense") with
    | .ok t => pure t
    | .error _ => throw s!"ContextTense: {id}"
  let rt ← match j.getObjVal? "reference_time" with
    | .ok v => do
      let t ← v.getStr?
      require (token t) s!"InvalidInput: invalid reference time for {id}"
      pure (some t)
    | .error _ => pure none
  let d ← stringField j "description"
  require (!d.isEmpty) s!"InvalidInput: context {id} description"
  require (d.utf8ByteSize ≤ 200) "ResourceLimit: context description"
  pure ⟨id, tense, rt, d⟩

def decodeAssessment (E : VE.Environment) (j : Json) : Except String Assessment := do
  let id ← stringField j "id"
  require ((j.getObjVal? "decided_by").toBool) s!"InvalidInput: assessment {id} needs decided_by"
  exactFields j ["id", "context", "decided_by", "necessary", "sufficient", "factors", "precedents",
    "jurisdiction", "version"]
  require (token id) s!"InvalidInput: invalid assessment id {id}"
  let context ← stringField j "context"
  let decidedBy ← stringField j "decided_by"
  let necessary ← VE.Route.Wire.decodeFormulas E (← j.getObjVal? "necessary")
  let sufficient ← VE.Route.Wire.decodeFormulas E (← j.getObjVal? "sufficient")
  let factors ← strings (← j.getObjVal? "factors")
  let precedents ← strings (← j.getObjVal? "precedents")
  let jurisdiction ← stringField j "jurisdiction"
  let version ← (← j.getObjVal? "version").getNat?
  -- W2's open-term schema (`ve/openterms.py`): a token jurisdiction, non-empty
  -- factors and precedents, a positive version.
  require (token jurisdiction && version ≥ 1 && (factors ++ precedents).all (!·.isEmpty))
    s!"InvalidInput: assessment {id}"
  pure ⟨id, context, decidedBy, necessary, sufficient, factors, precedents, jurisdiction, version⟩

/-- A wire path: a unit id alone (depth 0) or `{"unit", "path"}` with `path` in `1(.1)*`. -/
def decodePath (j : Json) : Except String Path := do
  match j with
  | .str u => pure ⟨u, 0⟩
  | _ =>
    exactFields j ["unit", "path"]
    let u ← stringField j "unit"
    let p ← stringField j "path"
    match parsePath p with
    | some n => pure ⟨u, n⟩
    | none => throw s!"InvalidInput: bridge path {p}"

def decodeBridge (j : Json) : Except String Bridge := do
  displayFields j ["id", "unit", "accepted_by", "reason"] ["path"]
  let id ← stringField j "id"
  let u ← stringField j "unit"
  let depth ← match j.getObjVal? "path" with
    | .ok p => do
      let s ← p.getStr?
      match parsePath s with
      | some n => pure n
      | none => throw s!"InvalidInput: bridge path {s}"
    | .error _ => pure 0
  pure ⟨id, ⟨u, depth⟩, ← stringField j "accepted_by", ← strings (← j.getObjVal? "reason")⟩

/-- A scoped check with its optional certificate and the certificate's
envelope (3.4); an envelope without a certificate is malformed. -/
def decodeScoped (j : Json) : Except String (ScopedCheck × Option (Json × Option Json)) := do
  displayFields j ["id", "payloads", "conclusion"] ["certificate", "envelope"]
  let id ← stringField j "id"
  let payloads ← (← (← j.getObjVal? "payloads").getArr?).toList.mapM decodePath
  let c ← j.getObjVal? "conclusion"
  exactFields c ["ast"]
  let conclusion ← VE.Bridge.decodeFormula 64 (← c.getObjVal? "ast")
  let certificate := (j.getObjVal? "certificate").toOption
  let envelope := (j.getObjVal? "envelope").toOption
  require (certificate.isSome || envelope.isNone) s!"InvalidInput: envelope without a certificate on scoped check {id}"
  pure (⟨id, payloads, conclusion⟩, certificate.map (·, envelope))

/-! ## Documents -/

/-- A decoded unit: a report unit (its content tree) or a W2 unit. -/
inductive DecodedUnit where
  | reports (u : Unit) (start stop : Nat) (kind : Kind)
  | w2 (u : VE.Route.Admission.DocUnit)

def DecodedUnit.id : DecodedUnit → String
  | .reports u .. => u.id
  | .w2 u => u.id

def DecodedUnit.span : DecodedUnit → Nat × Nat
  | .reports _ a b _ => (a, b)
  | .w2 u => (u.start, u.stop)

def DecodedUnit.kind : DecodedUnit → Kind
  | .reports _ _ _ k => k
  | .w2 u => u.kind

def reportContentKeys : List String := ["report", "assessment", "negated"]

/-- W2's meaning status, as `ve/document.py` reads it. -/
def decodeMeaning (j : Json) : Except String Meaning := do
  if j == .str "specified" then return .specified
  match ← fields j with
  | [("open", v)] => pure (.«open» (← strings v))
  | [("contextual", .str s)] => pure (.contextual s)
  | [("unformalised", .str r)] => pure (.unformalised r)
  | _ => throw "invalid meaning status"

/-- A unit's W2 metadata: its span and, when present, meaning and support. -/
def decodeMeta (j : Json) : Except String UnitMeta := do
  let id ← stringField j "id"
  let (start, stop) ← match (← (← j.getObjVal? "span").getArr?).toList with
    | [a, b] => pure (← a.getNat?, ← b.getNat?)
    | _ => throw "invalid span"
  let meaning ← match j.getObjVal? "meaning" with
    | .ok m => some <$> decodeMeaning m
    | .error _ => pure none
  let support ← match j.getObjVal? "support" with
    | .ok v => some <$> v.getStr?
    | .error _ => pure none
  pure ⟨id, start, stop, meaning, support⟩

def decodeUnit (E : VE.Environment) (j : Json) : Except String DecodedUnit := do
  let id ← stringField j "id"
  require (token id) s!"invalid unit id {id}"
  let (start, stop) ← match (← (← j.getObjVal? "span").getArr?).toList with
    | [a, b] => pure (← a.getNat?, ← b.getNat?)
    | _ => throw "invalid span"
  require (start ≤ stop) "invalid span"
  let kind ← decodeKind 16 (← j.getObjVal? "kind")
  match j.getObjVal? "content" with
  | .ok content =>
    let ks := (← fields content).map Prod.fst
    if ks.any reportContentKeys.contains then
      displayFields j ["id", "span", "kind", "content", "meaning", "support"] []
      let c ← decodeContent E id 40 content
      require c.isStatement s!"InvalidInput: invalid content for {id}"
      require (kind == kindOf c) s!"KindMismatch: {id}"
      pure (.reports ⟨id, c⟩ start stop kind)
    else
      displayFields j ["id", "span", "kind", "content"] ["meaning", "support"]
      require (!kind.quoted) s!"InvalidInput: invalid content for {id}"
      exactFields content ["ast"]
      let a ← VE.Route.Wire.decodeClosed E (← content.getObjVal? "ast")
      pure (.w2 ⟨id, start, stop, kind, some a⟩)
  | .error _ =>
    displayFields j ["id", "span", "kind"] ["meaning", "support"]
    pure (.w2 ⟨id, start, stop, kind, none⟩)

def sortedSpans : List (Nat × Nat) → Bool
  | a :: b :: rest => a.2 ≤ b.1 && sortedSpans (b :: rest)
  | _ => true

/-- A decoded reports document: the environment, the document, the raw unit
decodings and the scoped checks' optional certificates, each with its optional
envelope. -/
structure Decoded where
  re : ReportsEnvironment
  D : ReportDoc
  units : List DecodedUnit
  scopedCertificates : List (String × Json × Option Json)
  /-- the document's environment and literals are the decoded vocabulary's -/
  hE : D.E = re.rv.environment
  hlits : D.lits = re.rv.literals

def optionalArray (j : Json) (key : String) : Except String (List Json) :=
  match j.getObjVal? key with
  | .ok v => v.getArr?.map Array.toList
  | .error _ => pure []

def decodeDocumentRaw (environment document : Json) : Except String Decoded := do
  let re ← decodeEnvironment environment
  let E := re.rv.environment
  displayFields document ["units"] ["graph", "lemmas", "open_terms", "reading_sets", "narrowings",
    "contexts", "assessments", "bridges", "scoped"]
  let unitsJson := (← (← document.getObjVal? "units").getArr?).toList
  let units ← unitsJson.mapM (decodeUnit E)
  let metas ← unitsJson.mapM decodeMeta
  require (units.length ≤ 10000) "ResourceLimit: unit count"
  require ((units.map DecodedUnit.id).eraseDups.length == units.length) "duplicate unit id"
  require (sortedSpans (units.map DecodedUnit.span)) "unit spans must be sorted and non-overlapping"
  let contexts ← (← optionalArray document "contexts").mapM decodeContext
  require (contexts.length ≤ 256) "ResourceLimit: contexts"
  let assessments ← (← optionalArray document "assessments").mapM (decodeAssessment E)
  require (assessments.length ≤ 256) "ResourceLimit: assessments"
  let bridges ← (← optionalArray document "bridges").mapM decodeBridge
  let scopedChecks ← (← optionalArray document "scoped").mapM decodeScoped
  let lemmas ← (← optionalArray document "lemmas").mapM (VE.Route.Admission.decodeLemma E false)
  require ((lemmas.map VE.Route.Admission.Lemma.name).eraseDups.length == lemmas.length) "duplicate lemma"
  let openTerms ← VE.Route.Admission.tokens (Json.arr (← optionalArray document "open_terms").toArray)
  let readingSets ← (← optionalArray document "reading_sets").mapM (VE.Route.Admission.decodeReadingSet E false)
  require ((readingSets.map (fun r => (r.id, r.version))).eraseDups.length == readingSets.length)
    "duplicate reading set version"
  let narrowings ← VE.Route.Admission.tokens (Json.arr (← optionalArray document "narrowings").toArray)
  let reportUnits := units.filterMap fun | .reports u .. => some u | .w2 _ => none
  let w2Units := units.filterMap fun | .w2 u => some u | .reports .. => none
  let w2 : VE.Route.Admission.Doc := ⟨re.rv.literals, re.rv.flags, w2Units, lemmas, openTerms, readingSets,
    narrowings⟩
  let envId ← VE.Route.Wire.environmentId re.profiles environment
  let D : ReportDoc := ⟨E, re.rv.literals, re.holders, re.evidence, contexts, assessments, reportUnits,
    bridges, scopedChecks.map Prod.fst, re.profiles, envId, w2, re.predicateNames, metas⟩
  pure ⟨re, D, units, scopedChecks.filterMap fun (s, c) => c.map fun (cj, e) => (s.id, cj, e), rfl, rfl⟩

/-! ## Diagnostics of 4.1, in the order of section 8 (untrusted text) -/

/-- The first id that occurs twice. -/
def firstDup : List String → Option String
  | [] => none
  | x :: xs => if xs.contains x then some x else firstDup xs

def firstFailure (D : ReportDoc) : String :=
  let nodes := allNodes D
  let bad := nodes.find? (fun x => !nodeOk D x)
  let unitOfNode := fun (x : Content) =>
    (D.units.find? (fun u => u.content.nodes.any fun y => canonicalObject D y == canonicalObject D x)).map (·.id)
  match firstDup (D.contexts.map (·.id)), firstDup (D.assessments.map (·.id)),
      firstDup (D.bridges.map (·.id)), firstDup (D.«scoped».map (·.id)) with
  | some c, _, _, _ => s!"DuplicateDeclaration: context {c}"
  | _, some a, _, _ => s!"DuplicateDeclaration: assessment {a}"
  | _, _, some b, _ => s!"DuplicateDeclaration: bridge {b}"
  | _, _, _, some s => s!"DuplicateDeclaration: scoped {s}"
  | none, none, none, none =>
  match D.assessments.find? (fun a => !assessmentOk D a) with
  | some a =>
    if D.E.constants a.context != some D.evidence then s!"UnknownSymbol: evidence context {a.context}"
    else if !token a.decidedBy then s!"InvalidInput: assessment {a.id} needs decided_by"
    else s!"OpenComplement: assessment {a.id} criteria"
  | none =>
  match D.units.find? (fun u => u.content.depth > 16) with
  | some u => s!"ResourceLimit: content depth in {u.id}"
  | none =>
  match bad with
  | some x =>
    let u := (unitOfNode x).getD "?"
    match x with
    | .report h _ c _ _ =>
      if D.E.constants h == none then s!"UnknownHolder: {h}"
      else if (holderSort D h).isNone then s!"HolderSort: {h} is not of a holder sort"
      else s!"UnknownContext: {c}"
    | .assessment _ a _ => s!"UnknownAssessment: {a}"
    | .negated _ => s!"InvalidInput: negated operand in {u}"
    | _ => s!"OpenComplement: {u}"
  | none =>
  if !(decide (∀ a ∈ digestTable D, ∀ b ∈ digestTable D, a.1 = b.1 → a.2 = b.2)) then
    "HashCollision: two distinct canonical objects with one digest"
  else match D.«scoped».find? (fun s => !scopedOk D s) with
  | some s =>
    if s.payloads.length > 64 then "ResourceLimit: scoped payloads"
    else if s.payloads.any (fun p => match contentAt D p with | some (.formula _) => false | _ => true) then
      s!"ScopedTarget: {s.id}"
    else s!"ScopedEnvironment: {s.id}"
  | none =>
  match D.bridges.find? (fun b => !bridgeOk D b) with
  | some b =>
    if (contentAt D b.target).isNone then s!"BridgeTarget: {b.target.unit}"
    else s!"BridgeKindMismatch: {b.target.unit}, {b.target.depth}"
  | none =>
  match D.unitMeta.find? (fun m => !metaOk D m) with
  | some m =>
    if !(m.support.all supports.contains) then s!"InvalidInput: support of {m.id}"
    else s!"InvalidInput: meaning of {m.id}"
  | none =>
  if !((names D).all (fun n => (D.E.predicates n).isNone && decide (n.utf8ByteSize ≤ 64)) &&
      decide (names D).Nodup && decide (D.authorPredicates.length + (names D).length ≤ maxPredicates)) then
    "ResourceLimit: MAX_PREDICATES"
  else "InvalidInput: the document is not well-formed"

/-- A decoded, well-formed reports document. -/
structure Checked where
  dec : Decoded
  wf : WellFormedReports dec.D = true

def decodeDocument (environment document : Json) : Except String Checked := do
  let dec ← decodeDocumentRaw environment document
  if h : WellFormedReports dec.D = true then pure ⟨dec, h⟩
  else throw (firstFailure dec.D)

/-! ## Regenerated identities -/

/-- The name, key and signature of every generated predicate. -/
def generated (D : ReportDoc) : List (String × List String × Json) :=
  (keys D).map (fun k => (reportName D k, [k.sort], Json.mkObj [("act", .str k.act.name),
      ("holder_sort", .str k.sort), ("context", .str k.ctx), ("complement_id", .str k.content)])) ++
  (akeys D).map (fun k => (assessName D k, [D.evidence], Json.mkObj [("judgment", .str k.j.name),
      ("assessment", .str k.a), ("content_id", .str k.content)]))

/-- The environment JSON of E_reports: the raw environment with one predicate
declaration per key; its `environment_id` is the inner binding of 3.4. -/
def environmentReportsJson (environment : Json) (D : ReportDoc) : Json :=
  let vocab := environment.getObjValD "vocabulary"
  let preds := (generated D).foldl (fun p (n, ss, key) =>
    p.setObjVal! n (Json.mkObj [("arguments", toJson ss),
      ("description", .str s!"generated by reports@0 for {key.compress}")])) (vocab.getObjValD "predicates")
  environment.setObjVal! "vocabulary" (vocab.setObjVal! "predicates" preds)

/-- The model vocabulary of E_reports: the author's model vocabulary and one
unary table per generated predicate. -/
def reportsModelVocabulary (re : ReportsEnvironment) (D : ReportDoc) : VE.Bridge.Vocabulary :=
  { re.rv.modelVocabulary with
    predicates := re.rv.modelVocabulary.predicates ++ (generated D).map (fun (n, ss, _) => (n, ss)) }

end VE.Reports.Wire
