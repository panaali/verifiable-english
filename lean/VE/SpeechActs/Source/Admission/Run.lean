import VE.SpeechActs.Source.Run
import VE.Norms.Run

/-! # Speech-act admission over the decoded source (docs/spec/speech-acts.md 8.5, 8.6 `admission`)

The `admission` case kind of `ve_speech_acts_route` reads the same `ve-document@2` payload as `speech-source`
(`{"metadata", "source", "fences"}`, with the case's optional `premise_status`), decodes it with
`decodeSpeechSource` (every record replayed), and admits its claim graph as W2 admits a document:

* the P0 document actually admitted is W2's projection of the source (`p0Json`): every unit except `binding` units
  (3.2: P0's frozen kind decoder has no `binding`), each with its formula content unless its latest reading set
  decides it, the latest all-assertion reading sets as P0's formula-only sets, the declared open-term names (the
  `intended-reading.<u>` terms included), the narrowing ids, the lemmas and the graph;
* a node is admitted by P0's provenance rules, as a regenerated layer or profile leaf of `policy(D)` (W1's
  `Norms.Admission.NodeAdmitted`), or as one of exactly two route-local leaves: `speech:presupposition:<u>`, equal to
  `presupposition D q` (an assumption the report keeps), and `speech:answer:<u>:<a>`, equal to `H ∧ F` of a
  certificate-supported answer record over `premises D` (discharged by that record's accepted certificate). There
  is no compliance leaf and no checker-generated `done` fact: a leaf claiming one has no provenance (4.6);
* every certificate is bound to the canonical environment and its nodes' ASTs, the graph is checked by the
  unchanged W2 checker, citations are closed and reading choices compatible;
* the wire report expands each certificate-supported answer leaf with the bound `premises D` inputs; the exact graph
  report remains in `SpeechAdmitted` for the soundness and consequence theorems. The report id hashes the expanded
  report with the canonical environment id and 3.5 document id.

Each check's success is carried as a field of `SpeechAdmitted`, so the theorems below read it off the result. -/
namespace VE.SpeechActs.Source.Admission
open Lean
open VE.Bridge (stringField exactFields fields)
open VE.Route.Admission (WireNode Doc CitationsClosed ChoicesCompatible)
open VE.Discourse
open VE.Norms (Sat background backgroundBase elaborate)
universe u

/-! ## The P0 projection (W2's, binding units withheld) -/

def isBinding (u : SourceUnit) : Bool := u.kind == .str "binding"

/-- The same formula projection for a fixed unit and for an asserted reading.
The speech schema wraps formula ASTs in `{"ast": ...}`; P0 expects the AST itself. -/
def formulaAst (content : Json) : Json :=
  match fields content with
  | .ok [("ast", a)] => a
  | _ => content

/-- A unit's formula content as W2 sends it to P0 (`{"ast": a}` or the bare AST); command, question, binding and
norm content is speech content, never a P0 formula. -/
def formulaContent (u : SourceUnit) : Option Json :=
  match u.content with
  | some (.arr xs) => some (.arr xs)
  | some c => match fields c with
    | .ok [("ast", _)] => some (formulaAst c)
    | _ => none
  | none => none

/-- The latest version of each unit's reading set (1.5). -/
def latestSets (src : SpeechSource) : List SetInfo :=
  src.sets.filter fun s => (latestOf src.sets s.unit).any (·.version == s.version)

/-- W2's projection of the source (8.5): the P0 document sent to `admit_document`. -/
def p0Json (src : SpeechSource) (graph : Json) : Json :=
  let latest := latestSets src
  let decided := latest.map (·.unit)
  let units := (src.units.filter (!isBinding ·)).map fun u =>
    Json.mkObj ([("id", .str u.id), ("span", Json.arr #[toJson u.span.1, toJson u.span.2]), ("kind", u.kind)] ++
      match formulaContent u with
      | some a => if decided.contains u.id then [] else [("content", a)]
      | none => [])
  let sets := (latest.filter fun s => s.readings.all fun r => r.getObjValD "kind" == .str "asserted").map fun s =>
    Json.mkObj [("id", .str s.id), ("version", toJson s.version),
      ("readings", Json.arr (s.readings.map (fun r => formulaAst (r.getObjValD "content"))).toArray)]
  let narrowings := match Loader.optionalList src.metadata "narrowings" with
    | .arr ns => ns.toList.map fun (n : Json) => n.getObjValD "id"
    | _ => []
  Json.mkObj [("units", Json.arr units.toArray), ("graph", graph),
    ("lemmas", Loader.optionalList src.metadata "lemmas"),
    ("open_terms", Json.arr (src.openTerms.map (·.getObjValD "name")).toArray),
    ("reading_sets", Json.arr sets.toArray), ("narrowings", Json.arr narrowings.toArray)]

/-! ## The two route-local leaves (8.5) -/

def presuppositionLabel (u : String) : String := "speech:presupposition:" ++ u
def answerLabel (u a : String) : String := "speech:answer:" ++ u ++ ":" ++ a

/-- `speech:presupposition:<u>`: exactly `presupposition D q` of a question `u`, no unit pointer, no deduction. -/
def PresuppositionLeaf (dec : Wire.Decoded) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone && dec.D.questions.any fun q =>
    w.claim.label == presuppositionLabel q.unit && decide (w.claim.formula = presupposition dec.D q)) = true

instance (dec : Wire.Decoded) (w : WireNode) : Decidable (PresuppositionLeaf dec w) := by
  unfold PresuppositionLeaf; infer_instance

/-- The label and formula of a certificate-supported answer record: `H ∧ F` over `premises D`. -/
def certifiedAnswer {dec : Wire.Decoded} (r : AnswerRecord dec) : Option (String × VE.Formula) :=
  match r.replay with
  | .certificate a φ _ _ _ => some (answerLabel r.q.unit (Run.answerText a), .and (presupposition dec.D r.q) φ)
  | _ => none

/-- `speech:answer:<u>:<a>`: exactly `H ∧ F` of a certificate-supported answer record, no unit pointer, no
deduction. -/
def AnswerLeaf (src : SpeechSource) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone && src.answers.answers.any fun r => match certifiedAnswer r with
    | some (l, φ) => w.claim.label == l && decide (w.claim.formula = φ)
    | none => false) = true

instance (src : SpeechSource) (w : WireNode) : Decidable (AnswerLeaf src w) := by
  unfold AnswerLeaf; infer_instance

/-- W1's decoded norm source of the regenerated policy (stated so that proofs rewrite instead of unfolding). -/
theorem normsSource_D (dec : Wire.Decoded) : (Run.normsSource dec).D = policy dec.D := rfl

/-- The speech extension of W1's admission relation: P0's provenance, a regenerated layer or profile leaf of
`policy(D)`, or one of the two speech leaves. -/
def NodeAdmitted (src : SpeechSource) (D : Doc) (w : WireNode) : Prop :=
  VE.Norms.Admission.NodeAdmitted (Run.normsSource src.dec) D w ∨ PresuppositionLeaf src.dec w ∨ AnswerLeaf src w

instance (src : SpeechSource) (D : Doc) (w : WireNode) : Decidable (NodeAdmitted src D w) := by
  unfold NodeAdmitted; infer_instance

/-- P0's diagnostic, except that a route-local label (`speech:`, `layer:`) P0 cannot parse is named as a label
whose node is not admitted, not as an invalid label. -/
def nodeDiagnostic (D : Doc) (w : WireNode) : String :=
  if w.unit.isNone && (w.claim.label.startsWith "speech:" || w.claim.label.startsWith "layer:") then
    s!"AdmissionError: node {w.claim.name} is not admitted under label {w.claim.label}"
  else VE.Route.Admission.nodeDiagnostic D w

def admitNodes (src : SpeechSource) (D : Doc) (ws : List WireNode) : Except String Unit :=
  match ws.find? (fun w => !decide (NodeAdmitted src D w)) with
  | some w => .error (nodeDiagnostic D w)
  | none => .ok ()

theorem admitNodes_ok (src : SpeechSource) (D : Doc) (ws : List WireNode) (h : admitNodes src D ws = .ok ()) :
    ∀ w ∈ ws, NodeAdmitted src D w := by
  unfold admitNodes at h
  split at h
  · cases h
  · rename_i hf
    intro w hw
    have := List.find?_eq_none.mp hf w hw
    simpa using this

/-! ## Admission -/

/-- A successful speech-act admission (8.5's `SpeechAdmitted`), with the success of every check it ran. -/
structure SpeechAdmitted where
  payload : Json
  evidence : Json
  src : SpeechSource
  srcPayload : src.payload = payload
  decodedSrc : decodeSpeechSource payload evidence = .ok ⟨src, srcPayload⟩
  graphJson : Json
  graphOf : src.metadata.getObjVal? "graph" = .ok graphJson
  /-- the P0 document actually admitted -/
  p0 : Doc
  decodedP0 : ∃ D₀, VE.Route.Admission.decodeDoc src.dec.se.ne.rv (src.dec.se.profiles.contains "data@0")
    (p0Json src graphJson) = .ok D₀ ∧ p0 = { D₀ with literals := src.dec.se.ne.rv.literals }
  decoded : List (WireNode × Json)
  bound : VE.Norms.Admission.checkBindings src.dec.se.profiles src.dec.se.canonical decoded = .ok ()
  wires : List WireNode
  wires_eq : wires = decoded.map Prod.fst
  admitted : ∀ w ∈ wires, NodeAdmitted src p0 w
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  graph_nodes : graph.nodes = wires.map WireNode.toNode
  report : VE.Graph.Report
  checked : VE.Route.Admission.checkGraph src.dec.se.ne.rv.environment graph = .ok report
  citations : CitationsClosed p0 report
  choices : ChoicesCompatible report
  /-- 3.2: exactly the non-binding units reach P0, in document order -/
  withheld : p0.units.map (·.id) = (src.units.filter (!isBinding ·)).map (·.id)
  distinct : (src.units.map (·.id)).Nodup
  /-- 6: every unit, a binding unit included, is classed by the coverage projection -/
  classed : src.cov.rows.map (·.id) = src.units.map (·.id)

def SpeechAdmitted.kinds (adm : SpeechAdmitted) : List Json :=
  adm.p0.units.map fun x => VE.Route.Admission.renderKind x.kind

/-- The ordered premise inputs bound into an answer certificate, with their source provenance.
Background and layer claims use generated names; asserted claims keep their unit ids. -/
def answerPremiseClaims (src : SpeechSource) (answer : String) : List VE.Graph.Claim :=
  let p := policy src.dec.D
  let bg := ((VE.Norms.definitionPremises p.T).map (fun a => ("background:definitions", a)) ++
    (VE.Norms.backgroundBase p).map (fun a => ("background:literals", a)) ++
    (VE.Norms.pairPremises p.T).map (fun a => ("background:profile", a)))
  let layers := (VE.Norms.syms p.T).filterMap fun
    | .reg r => some ("layer:norms:" ++ r.name, VE.Norms.elabPremise p.T r)
    | .defn _ => none
  let generated := (bg ++ layers).zipIdx.map fun ((label, formula), i) =>
    ({ name := answer ++ ":premise:" ++ toString i, formula, label } : VE.Graph.Claim)
  let asserted := src.dec.D.asserted.map fun (name, formula) =>
    ({ name, formula, label := "asserted" } : VE.Graph.Claim)
  generated ++ asserted

/-- The provenance expansion lists exactly the formulas to which the accepted answer certificate is bound. -/
theorem answerPremiseClaims_formulas (src : SpeechSource) (answer : String) :
    (answerPremiseClaims src answer).map (·.formula) = premises src.dec.D := by
  have indexed (xs : List (String × VE.Formula)) (i : Nat) :
      ((xs.zipIdx i).map fun ((label, formula), n) =>
        ({ name := answer ++ ":premise:" ++ toString n, formula, label } : VE.Graph.Claim)).map
          (·.formula) = xs.map Prod.snd := by
    induction xs generalizing i with
    | nil => simp
    | cons x xs ih => simp [List.zipIdx, ih]
  have layers (xs : List VE.Norms.Sym) :
      (xs.filterMap (fun
        | .reg r => some ("layer:norms:" ++ r.name, VE.Norms.elabPremise (policy src.dec.D).T r)
        | .defn _ => none)).map Prod.snd =
      xs.filterMap (fun
        | .reg r => some (VE.Norms.elabPremise (policy src.dec.D).T r)
        | .defn _ => none) := by
    induction xs with
    | nil => simp
    | cons x xs ih => cases x <;> simp [ih]
  simp [answerPremiseClaims, indexed, premises, VE.Norms.background, VE.Norms.elaborate,
    VE.Norms.definitionPremises, VE.Norms.backgroundBase, layers, assertedFormulas, Function.comp_def]
  rfl

/-- A graph answer leaf abbreviates a checked certificate over `premises D`. Expand each such
leaf in the wire report with the certificate's bound premise inputs, retaining the exact
graph report separately for `SoundReport` and consequence proofs. -/
def reportedReport (adm : SpeechAdmitted) : VE.Graph.Report :=
  { adm.report with assumptions := adm.report.assumptions.flatMap fun leaf =>
      if adm.src.answers.answers.any (fun r => match certifiedAnswer r with
          | some (label, formula) => leaf.label == label && decide (leaf.formula = formula)
          | none => false) then
        leaf :: answerPremiseClaims adm.src leaf.label
      else [leaf] }

def admitSpeech (payload evidence : Json) :
    Except String { adm : SpeechAdmitted // adm.payload = payload ∧ adm.evidence = evidence } := do
  match hs : decodeSpeechSource payload evidence with
  | .error e => throw e
  | .ok ⟨src, hp⟩ =>
  match hg : src.metadata.getObjVal? "graph" with
  | .error _ => throw (VE.Discourse.Loader.notImplemented "a document without a claim graph")
  | .ok graph =>
  let rv := src.dec.se.ne.rv
  let data := src.dec.se.profiles.contains "data@0"
  match hd : VE.Route.Admission.decodeDoc rv data (p0Json src graph) with
  | .error e => throw e
  | .ok D₀ =>
  let D := { D₀ with literals := rv.literals }
  exactFields graph ["root", "nodes"]
  let root ← stringField graph "root"
  let nodeArray ← (← graph.getObjVal? "nodes").getArr?
  VE.Route.Admission.require (nodeArray.size ≤ 1000) "ResourceLimit: graph node count"
  let decoded ← nodeArray.toList.mapM (VE.Route.Admission.decodeNode rv.environment data)
  match hb : VE.Norms.Admission.checkBindings src.dec.se.profiles src.dec.se.canonical decoded with
  | .error e => throw e
  | .ok () =>
  let wires := decoded.map Prod.fst
  match ha : admitNodes src D wires with
  | .error e => throw e
  | .ok () =>
  let g : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  match hr : VE.Route.Admission.checkGraph rv.environment g with
  | .error e => throw e
  | .ok r =>
  if hc : CitationsClosed D r then
    if hch : ChoicesCompatible r then
      if hw : D.units.map (·.id) = (src.units.filter (!isBinding ·)).map (·.id) then
        if hn : (src.units.map (·.id)).Nodup then
          if hcl : src.cov.rows.map (·.id) = src.units.map (·.id) then
            pure ⟨⟨payload, evidence, src, hp, hs, graph, hg, D, ⟨D₀, hd, rfl⟩, decoded, hb, wires, rfl,
              admitNodes_ok src D wires ha, g, rfl, r, hr, hc, hch, hw, hn, hcl⟩, rfl, rfl⟩
          else throw "AdmissionError: the coverage projection does not class every unit"
        else throw "duplicate or invalid unit id"
      else throw "AdmissionError: the P0 projection does not hold exactly the non-binding units"
    else throw "AdmissionError: incompatible reading choices"
  else throw "AdmissionError: a cited lemma's leaves are missing from the report"

/-! ## The report identity and the answer -/

/-- Report identity over the complete validated source (3.5): the canonical environment id, the document id
recomputed from the retained identity payload, and the checked graph report with answer support expanded. -/
def reportId (adm : SpeechAdmitted) : Except String String := do
  let envId ← VE.Route.Wire.environmentId adm.src.dec.se.profiles adm.src.dec.se.canonical
  let docId ← adm.src.documentId
  VE.CertificateWire.digest (VE.Norms.Run.reportDomain adm.src.dec.se.profiles)
    (VE.Norms.Run.reportPayload envId (.str docId) (reportedReport adm))

def encodeAdmitted (id reportId : String) (adm : SpeechAdmitted) : Json :=
  VE.Route.Wire.ok id [("admitted", .bool true), ("report", VE.Norms.Run.reportJson (reportedReport adm)),
    ("report_id", .str reportId), ("document_id", .str (adm.src.documentId.toOption.getD "")),
    ("kinds", Json.arr adm.kinds.toArray),
    ("classes", Json.arr (adm.src.cov.rows.map fun r => Json.mkObj [("id", .str r.id), ("class", .str r.cls)]).toArray),
    ("status_text", toJson (statusText adm.src))]

def runAdmission (id : String) (payload evidence : Json) : Except String Json := do
  let adm ← admitSpeech payload evidence
  let rid ← reportId adm.1
  return encodeAdmitted id rid adm.1

/-! ## Theorems -/

theorem eq_of_map_nodup {α β : Type} {f : α → β} :
    ∀ {l : List α}, (l.map f).Nodup → ∀ {x y : α}, x ∈ l → y ∈ l → f x = f y → x = y
  | [], _, _, _, hx, _, _ => by cases hx
  | a :: l, h, x, y, hx, hy, hxy => by
    rw [List.map_cons, List.nodup_cons] at h
    rcases List.mem_cons.mp hx with hxa | hx' <;> rcases List.mem_cons.mp hy with hya | hy'
    · rw [hxa, hya]
    · have : f a ∈ l.map f := by rw [← hxa, hxy]; exact List.mem_map_of_mem hy'
      exact absurd this h.1
    · have : f a ∈ l.map f := by rw [← hya, ← hxy]; exact List.mem_map_of_mem hx'
      exact absurd this h.1
    · exact eq_of_map_nodup h.2 hx' hy' hxy

theorem admissible_En (D : SpeechDoc) (S : VE.Structure.{u}) : S.Admissible (En D) ↔ S.Admissible D.E := by
  unfold VE.Structure.Admissible
  simp only [Run.En_predicates]
  exact Iff.rfl

/-- The P0 document holds exactly the source's non-binding units, and every unit, binding units included, is in
the identity payload (`source_retained`) and classed by the coverage projection (8.5 `bindings_withheld`). -/
theorem bindings_withheld (adm : SpeechAdmitted) :
    (∀ u ∈ adm.src.units, isBinding u = true →
      (∀ p ∈ adm.p0.units, p.id ≠ u.id) ∧ u.id ∈ adm.src.cov.rows.map (·.id)) ∧
    (∀ u ∈ adm.src.units, isBinding u = false → ∃ p ∈ adm.p0.units, p.id = u.id) := by
  have hw := adm.withheld
  have hn := adm.distinct
  refine ⟨fun u hu hb => ⟨fun p hp hpu => ?_, ?_⟩, fun u hu hb => ?_⟩
  · have hmem : p.id ∈ (adm.src.units.filter (!isBinding ·)).map (·.id) := hw ▸ List.mem_map_of_mem hp
    obtain ⟨v, hv, hvid⟩ := List.mem_map.mp hmem
    have hvf := List.mem_filter.mp hv
    have huv : v = u := eq_of_map_nodup hn hvf.1 hu (hvid.trans hpu)
    subst huv
    simp [hb] at hvf
  · rw [adm.classed]; exact List.mem_map_of_mem hu
  · have hmem : u.id ∈ (adm.src.units.filter (!isBinding ·)).map (·.id) :=
      List.mem_map_of_mem (List.mem_filter.mpr ⟨hu, by simp [hb]⟩)
    rw [← hw] at hmem
    obtain ⟨p, hp, hpid⟩ := List.mem_map.mp hmem
    exact ⟨p, hp, hpid⟩

/-- Which commands are active (8.5 `active_commands`): exactly the active instruction units of the decoded core
(1.2: kind `instruction`, specified meaning, command content, bound slots, no pending reading set). -/
theorem active_commands (src : SpeechSource) (c : Command) :
    c ∈ src.dec.D.commands ↔ ∃ u ∈ src.dec.units, Wire.activeCommand u = some c := by
  rw [src.dec.commands_eq, List.mem_filterMap]

/-- The checked report is sound for the graph (the unchanged W2 checker). -/
theorem report_sound (adm : SpeechAdmitted) :
    VE.Graph.SoundReport.{u} adm.src.dec.se.ne.rv.environment adm.graph adm.report :=
  (VE.Graph.check_sound.{u} _ _ _ (VE.Route.Admission.checkGraph_ok _ _ _ adm.checked)).2.2.2

/-- Every certificate names the canonical environment and its premise nodes' and its own source ASTs. -/
theorem certificates_bound (adm : SpeechAdmitted) :
    ∀ x ∈ adm.decoded, VE.Norms.Admission.CertificateBound adm.src.dec.se.profiles adm.src.dec.se.canonical
      adm.decoded x :=
  VE.Norms.Admission.checkBindings_bound _ _ _ adm.bound

/-- 8.5's `ReportAdmitted`: the speech extension of W1's admission relation over the P0 projection. -/
def ReportAdmitted (adm : SpeechAdmitted) : Prop :=
  VE.Graph.SoundReport.{0} adm.src.dec.se.ne.rv.environment adm.graph adm.report ∧
  (∀ w ∈ adm.wires, NodeAdmitted adm.src adm.p0 w) ∧
  (∀ leaf ∈ adm.report.assumptions, ∃ w ∈ adm.wires,
    w.claim = leaf ∧ w.deduction = none ∧ NodeAdmitted adm.src adm.p0 w) ∧
  CitationsClosed adm.p0 adm.report ∧ ChoicesCompatible adm.report

theorem leaves_admitted (adm : SpeechAdmitted) :
    ∀ leaf ∈ adm.report.assumptions, ∃ w ∈ adm.wires,
      w.claim = leaf ∧ w.deduction = none ∧ NodeAdmitted adm.src adm.p0 w := by
  intro leaf hl
  obtain ⟨node, hn, hcl, hde⟩ := ((report_sound.{0} adm).2.2.1 leaf hl).2
  rw [adm.graph_nodes] at hn
  obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hn
  exact ⟨w, hw, hcl, hde, adm.admitted w hw⟩

theorem reportAdmitted (adm : SpeechAdmitted) : ReportAdmitted adm :=
  ⟨report_sound adm, adm.admitted, leaves_admitted adm, adm.citations, adm.choices⟩

/-- A leaf `premises D` (with the flag premises) discharges: a regenerated layer or profile leaf, an answer leaf,
or a W2 Background leaf admitted by P0's provenance. -/
def Discharged (adm : SpeechAdmitted) (w : WireNode) : Prop :=
  VE.Norms.Admission.LayerLeaf (Run.normsSource adm.src.dec) w ∨
  VE.Norms.Admission.ProfileLeaf (Run.normsSource adm.src.dec) w ∨ AnswerLeaf adm.src w ∨
  (w.deduction.isNone = true ∧ VE.Norms.Admission.backgroundLeaf w.claim = true ∧
    VE.Route.Admission.NodeAdmitted adm.p0 w)

instance (adm : SpeechAdmitted) (w : WireNode) : Decidable (Discharged adm w) := by
  unfold Discharged; infer_instance

/-- The report assumptions that stay explicit hypotheses: every leaf no discharged node carries; presupposition
leaves among them. -/
def otherAssumptions (adm : SpeechAdmitted) : List VE.Graph.Claim :=
  adm.report.assumptions.filter (fun c => !decide (∃ w ∈ adm.wires, w.claim = c ∧ Discharged adm w))

/-- A certificate-supported answer's leaf formula is entailed by `premises D` (its accepted certificate). -/
theorem certifiedAnswer_entailed {dec : Wire.Decoded} (r : AnswerRecord dec) (l : String) (ψ : VE.Formula)
    (h : certifiedAnswer r = some (l, ψ)) : VE.Entails.{u} (En dec.D) (premises dec.D) ψ := by
  unfold certifiedAnswer at h
  have ha := r.accepted
  generalize r.replay = x at ha h
  cases x with
  | certificate a φ hφ c s =>
    simp only [Option.some.injEq, Prod.mk.injEq] at h
    rw [← h.2]
    exact VE.Tableau.checkCertificate_sound _ _ _ c ha
  | _ => cases h

theorem answerLeaf_entailed (src : SpeechSource) (w : WireNode) (h : AnswerLeaf src w) (S : VE.Structure.{u})
    (hS : S.Admissible (En src.dec.D)) (hp : Sat S (premises src.dec.D)) : w.claim.formula.denote S [] := by
  simp only [AnswerLeaf, Bool.and_eq_true] at h
  obtain ⟨r, _, hr⟩ := List.any_eq_true.mp h.2
  revert hr
  match hc : certifiedAnswer r with
  | some (l, ψ) =>
    intro hr
    simp only [Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at hr
    rw [hr.2]
    exact certifiedAnswer_entailed r l ψ hc S hS hp
  | none => intro hr; cases hr

/-- Semantic report consequence: in every admissible structure satisfying the flag premises, the regenerated
`premises D` (Background, the elaborated policy, the asserted units) and the remaining assumptions (presupposition
leaves among them), the report's root holds. Layer leaves are discharged by the elaborations, Background leaves
by the regenerated literal and pair premises, and answer leaves by their records' accepted certificates. -/
theorem report_consequence (adm : SpeechAdmitted) (S : VE.Structure.{u})
    (hS : S.Admissible (En adm.src.dec.D))
    (hflags : Sat S (VE.Data.Background.generate adm.p0.flags))
    (hprem : Sat S (premises adm.src.dec.D))
    (hother : Sat S ((otherAssumptions adm).map (·.formula))) :
    adm.report.root.formula.denote S [] := by
  have hS' : S.Admissible adm.src.dec.se.ne.rv.environment := by
    rw [← adm.src.dec.env]; exact (admissible_En _ S).mp hS
  have hsound := report_sound.{u} adm
  have hleaves := leaves_admitted adm
  obtain ⟨D₀, _, hdoc⟩ := adm.decodedP0
  have hprem' : Sat S (background (policy adm.src.dec.D) ++ elaborate (policy adm.src.dec.D).T ++
      assertedFormulas adm.src.dec.D) := hprem
  have hbg : ∀ a ∈ background (policy adm.src.dec.D), a.denote S [] := fun a ha =>
    hprem' a (List.mem_append_left _ (List.mem_append_left _ ha))
  have hel : ∀ a ∈ elaborate (policy adm.src.dec.D).T, a.denote S [] := fun a ha =>
    hprem' a (List.mem_append_left _ (List.mem_append_right _ ha))
  apply hsound.2.2.2.1 S hS'
  intro a ha
  obtain ⟨leaf, hl, rfl⟩ := List.mem_map.mp ha
  by_cases hdis : ∃ w ∈ adm.wires, w.claim = leaf ∧ Discharged adm w
  · obtain ⟨w, _, hwl, hw⟩ := hdis
    rw [← hwl]
    rcases hw with hw | hw | hw | ⟨hde, hb, hadm⟩
    · have h := VE.Norms.Admission.layerLeaf_formula _ w hw
      rw [normsSource_D] at h
      exact hel _ h
    · simp only [VE.Norms.Admission.ProfileLeaf, Bool.and_eq_true] at hw
      obtain ⟨a, ha, hfa⟩ := List.any_eq_true.mp hw.2
      rw [normsSource_D] at ha
      rw [of_decide_eq_true hfa]
      apply hbg
      unfold background
      exact List.mem_append_right _ ha
    · exact answerLeaf_entailed adm.src w hw S hS hprem
    · unfold VE.Route.Admission.NodeAdmitted at hadm
      rw [Option.isNone_iff_eq_none.mp hde] at hadm
      unfold VE.Norms.Admission.backgroundLeaf at hb
      unfold VE.Route.Admission.LeafAdmitted at hadm
      split at hb
      · rename_i g hg
        rw [hg] at hadm
        obtain ⟨_, p, hp, hpe⟩ := hadm
        rcases List.mem_append.mp hp with hp | hp
        · obtain ⟨b, hbm, hbe⟩ := List.mem_map.mp hp
          rw [hpe] at hbe
          simp only [Prod.mk.injEq] at hbe
          rw [← hbe.1]
          exact hflags b hbm
        · obtain ⟨b, hbm, hbe⟩ := List.mem_map.mp hp
          rw [hpe] at hbe
          simp only [Prod.mk.injEq] at hbe
          rw [← hbe.1]
          apply hbg
          unfold background backgroundBase
          apply List.mem_append_left
          apply List.mem_append_right
          have hl' : adm.p0.literals = (policy adm.src.dec.D).lits := by
            rw [hdoc]; exact adm.src.dec.lits.symm
          rw [← hl']
          exact hbm
      · cases hb
  · apply hother
    apply List.mem_map_of_mem
    simp only [otherAssumptions, List.mem_filter]
    exact ⟨hl, by simp [hdis]⟩

/-- Every record of the decoded source is established by its evidence (3.3, 5.3, 5.4). -/
def RecordsSound (src : SpeechSource) : Prop :=
  (∀ r ∈ src.answers.answers, ∀ a φ hφ c s, r.replay = .certificate a φ hφ c s →
    ∀ S : VE.Structure.{u}, S.Admissible (En src.dec.D) → Sat S (premises src.dec.D) →
      AnswersAt src.dec.D r.q S a) ∧
  (∀ r ∈ src.answers.answers, ∀ a φ hφ c s, r.replay = .conditional a φ hφ c s →
    ∀ S : VE.Structure.{u}, S.Admissible (En src.dec.D) → Sat S (premises src.dec.D) →
      (presupposition src.dec.D r.q).denote S [] → AnswersAt src.dec.D r.q S a) ∧
  (∀ j ∈ src.answers.judgments, match j with
    | .follows r => VE.Entails.{u} (En src.dec.D) (queryPremises src.dec.D r.qr) r.qr.target
    | .gap r => ¬ VE.Entails.{u} (En src.dec.D) (queryPremises src.dec.D r.qr) r.qr.target) ∧
  (∀ c ∈ src.compliance, match c with
    | .certificate r => VE.Entails.{u} (En src.dec.D) (queryPremises src.dec.D r.qr) r.qr.target
    | .external r => r.entry ∈ src.dec.D.asserted ∧ DoneFact src.dec.D r.c r.entry.2)

theorem records_sound (src : SpeechSource) : RecordsSound.{u} src := by
  refine ⟨fun r hr => (answers_sound src r hr).1, fun r hr => (answers_sound src r hr).2.1, fun j hj => ?_,
    fun c hc => ?_⟩
  · cases j with
    | follows r => exact query_records_sound src r (Or.inl hj)
    | gap r => exact gap_records_sound src r hj
  · cases c with
    | certificate r => exact query_records_sound src r (Or.inr hc)
    | external r => exact ⟨r.asserted, r.fact⟩

/-- Every binding is the recomputed one: certificates name the canonical environment and their source ASTs, and
the report id is P0's digest of the canonical environment id, the 3.5 document id recomputed from the retained
payload, and the reported graph result with answer support expanded. Equality of digests, not injectivity of SHA-256. -/
def BindingsMatchSourceAndRegeneration (adm : SpeechAdmitted) (rid : String) : Prop :=
  (∀ x ∈ adm.decoded, VE.Norms.Admission.CertificateBound adm.src.dec.se.profiles adm.src.dec.se.canonical
    adm.decoded x) ∧
  ∃ envId docId, VE.Route.Wire.environmentId adm.src.dec.se.profiles adm.src.dec.se.canonical = .ok envId ∧
    adm.src.documentId = .ok docId ∧
    VE.CertificateWire.digest (VE.Norms.Run.reportDomain adm.src.dec.se.profiles)
      (VE.Norms.Run.reportPayload envId (.str docId) (reportedReport adm)) = .ok rid

theorem runAdmission_sound (id : String) (payload evidence a : Json)
    (h : runAdmission id payload evidence = .ok a) :
    ∃ adm : SpeechAdmitted, ∃ rid, (admitSpeech payload evidence).toOption.map (·.1) = some adm ∧
      adm.payload = payload ∧ adm.evidence = evidence ∧
      a = encodeAdmitted id rid adm ∧ BindingsMatchSourceAndRegeneration adm rid := by
  unfold runAdmission at h
  obtain ⟨⟨adm, hpe⟩, ha, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨rid, hr, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  unfold reportId at hr
  obtain ⟨envId, he, hr⟩ := VE.Order.ProfileGate.bind_ok hr
  obtain ⟨docId, hd, hr⟩ := VE.Order.ProfileGate.bind_ok hr
  exact ⟨adm, rid, by simp [ha, Except.toOption], hpe.1, hpe.2, rfl, certificates_bound adm, envId, docId, he, hd,
    hr⟩

end VE.SpeechActs.Source.Admission

/-! ## The entry point of `ve_speech_acts_route` -/

namespace VE.SpeechActs.Source
open Lean
open VE.Bridge (stringField)
open VE.Norms (Sat)
universe u

/-- A speech-act admission case: kind `admission` with a `ve-document@2` payload `{"metadata", "source",
"fences"}` (8.6). -/
def isSourceAdmission (j : Json) : Bool :=
  (VE.Route.Run.caseKind j).toOption == some "admission" && VE.Discourse.Loader.isPayload (j.getObjValD "document")

def admissionPayloadError : String :=
  "InvalidInput: speech-act admission reads the ve-document@2 payload {\"metadata\", \"source\", \"fences\"}"

/-- The cases this wrapper answers itself: `speech-source`, and `admission` of a payload or of a speech input. -/
def usesSourcePath (j : Json) : Bool :=
  (VE.Route.Run.caseKind j).toOption == some "speech-source" || isSourceAdmission j ||
    ((VE.Route.Run.caseKind j).toOption == some "admission" && Run.usesSpeechPath j)

def runCase (j : Json) : Except String Json := do
  if (VE.Route.Run.caseKind j).toOption == some "speech-source" then
    let id ← stringField j "id"
    let src ← decodeSpeechSource (← j.getObjVal? "document") (j.getObjValD "premise_status")
    return VE.Route.Wire.ok id (report src.1)
  if isSourceAdmission j then
    let id ← stringField j "id"
    return ← Admission.runAdmission id (j.getObjValD "document") (j.getObjValD "premise_status")
  if (VE.Route.Run.caseKind j).toOption == some "admission" && Run.usesSpeechPath j then
    throw admissionPayloadError
  Run.runCase j

def runCaseReported (j : Json) : Json :=
  if usesSourcePath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]
  else Run.runCaseReported j

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_speech_acts_route [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j
      | .error message => Json.mkObj [("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

/-- 8.5's `speech_wire_acceptance`, from the public entry point: an `admission` answer for a payload is exactly the
encoding of a checked `SpeechAdmitted` whose source is the payload's decoding (every record replayed), whose core
is well formed, whose bindings and report id are recomputed from the source and the regeneration, whose report is
admitted by the speech extension of W1's relation, which is a semantic consequence of the flag premises,
`premises D` and its remaining assumptions, and every record of which is established by its evidence. -/
theorem speech_wire_acceptance (j a : Json) (h : runCase j = .ok a)
    (hk : VE.Route.Run.caseKind j = .ok "admission")
    (hp : VE.Discourse.Loader.isPayload (j.getObjValD "document") = true) :
    ∃ (adm : Admission.SpeechAdmitted) (id rid : String),
      stringField j "id" = .ok id ∧
      adm.payload = j.getObjValD "document" ∧ adm.evidence = j.getObjValD "premise_status" ∧
      decodeSpeechSource adm.payload adm.evidence = .ok ⟨adm.src, adm.srcPayload⟩ ∧
      WellFormedSpeech adm.src.dec.D = true ∧
      a = Admission.encodeAdmitted id rid adm ∧
      Admission.BindingsMatchSourceAndRegeneration adm rid ∧ Admission.ReportAdmitted adm ∧
      (∀ S : VE.Structure.{u}, S.Admissible (En adm.src.dec.D) →
        Sat S (VE.Data.Background.generate adm.p0.flags) → Sat S (premises adm.src.dec.D) →
        Sat S ((Admission.otherAssumptions adm).map (·.formula)) → adm.report.root.formula.denote S []) ∧
      Admission.RecordsSound.{u} adm.src := by
  have hs : ((VE.Route.Run.caseKind j).toOption == some "speech-source") = false := by
    rw [hk]; decide
  have ha : isSourceAdmission j = true := by
    simp only [isSourceAdmission, hk, hp, Except.toOption, Bool.and_true]; decide
  unfold runCase at h
  simp only [hs, ha, Bool.false_eq_true, if_false, if_true] at h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨id, hid, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨answer, hr, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  obtain ⟨adm, rid, _, hpay, hev, rfl, hbind⟩ := Admission.runAdmission_sound id _ _ a hr
  exact ⟨adm, id, rid, hid, hpay, hev, adm.decodedSrc ▸ (hpay ▸ hev ▸ rfl), adm.src.dec.wf, rfl, hbind,
    Admission.reportAdmitted adm, fun S hS hf hpr ho => Admission.report_consequence adm S hS hf hpr ho,
    Admission.records_sound adm.src⟩

end VE.SpeechActs.Source
