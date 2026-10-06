import VE.Attribution.Wire

/-! W2 admission under `reports@0` (spec 9.3, 9.4): the unchanged W2 graph
checker at `E_reports`, with report and assessment leaves carrying exactly the
regenerated signed premise of their unit, bridge leaves admitted by
`BridgeAdmitted` (root ones coincide with the legacy rule,
`bridge_root_is_legacy`), and every other label by the unchanged `LeafAdmitted`
on the W2 view. Certificates of graph deductions bind `environment_id` of the
regenerated `E_reports` (the inner binding of 3.4) and carry the reports
envelope `{"environment_id", "document_id"}` they were produced for, which must
be the recomputed `(environment_id(E), document_id(D))` (the outer binding of
3.4): generated names are ordinal, so the inner binding alone survives a changed
tense or payload. The admission records the recomputed envelope. -/
namespace VE.Reports
open Lean
open VE.Route.Admission (WireNode LeafAdmitted AssertedUnit CitationsClosed ChoicesCompatible)
open VE.Order.ProfileGate (bind_ok)
open VE.Bridge (exactFields stringField)
universe u

/-- 9.4: the wire. The admitted record carries the decoded document, the
decoded wire nodes, the graph, the report and the recomputed envelope. -/
structure ReportsAdmitted where
  D : ReportDoc
  wires : List VE.Route.Admission.WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
  /-- (environment_id(E), document_id(D)), recomputed from the raw input -/
  envelope : String × String
  /-- the raw graph nodes, each certificate with its outer binding -/
  graphNodes : List Json

/-- The leaf rule under the profile. -/
def ReportsLeafAdmitted (D : ReportDoc) (w : VE.Route.Admission.WireNode) : Prop :=
  (∃ u ∈ D.units, w.claim.label = "report:" ++ u.id ∧ unitPremise D u = some w.claim.formula ∧
     (u.content.isReport = true ∨ ∃ n, u.content = .negated n ∧ n.isReport = true)) ∨
  (∃ u ∈ D.units, w.claim.label = "assessment:" ++ u.id ∧ unitPremise D u = some w.claim.formula ∧
     (u.content.isAssessment = true ∨ ∃ n, u.content = .negated n ∧ n.isAssessment = true)) ∨
  (BridgeAdmitted D w.claim ∧ (w.unit = none ∨ ∃ l, parseBridge w.claim.label = some l ∧ w.unit = some l.path.unit)) ∨
  VE.Route.Admission.LeafAdmitted (w2Doc D) w

def ReportsNodeAdmitted (D : ReportDoc) (w : VE.Route.Admission.WireNode) : Prop :=
  match w.deduction with
  | some _ => w.claim.label = "asserted" ∧ ∀ u, w.unit = some u → VE.Route.Admission.AssertedUnit (w2Doc D) u w.claim.formula
  | none => ReportsLeafAdmitted D w

/-! ## The executable leaf check and its soundness -/

def isReportStatement : Content → Bool
  | .report .. => true
  | .negated n => n.isReport
  | _ => false

def isAssessStatement : Content → Bool
  | .assessment .. => true
  | .negated n => n.isAssessment
  | _ => false

theorem isReportStatement_spec {x : Content} (h : isReportStatement x = true) :
    x.isReport = true ∨ ∃ n, x = .negated n ∧ n.isReport = true := by
  cases x <;> simp_all [isReportStatement, Content.isReport]

theorem isAssessStatement_spec {x : Content} (h : isAssessStatement x = true) :
    x.isAssessment = true ∨ ∃ n, x = .negated n ∧ n.isAssessment = true := by
  cases x <;> simp_all [isAssessStatement, Content.isAssessment]

def Content.isDefinition : Content → Bool
  | .definition .. => true
  | _ => false

/-- Every node along the path is present and none is a quoted package: the
path's scope is the author's. -/
def authorPath (D : ReportDoc) (p : Path) : Bool :=
  (List.range (p.depth + 1)).all fun k =>
    match parentAt D p.unit k with
    | some x => !x.isDefinition
    | none => false

theorem enterScope_author (s : Pinned) {x : Content} (hx : x.isDefinition = false) : enterScope s x = s := by
  cases x <;> simp_all [enterScope, Content.isDefinition]

theorem scopeAux_author (D : ReportDoc) (u : String) :
    ∀ n, (∀ k ≤ n, ∃ x, parentAt D u k = some x ∧ x.isDefinition = false) →
      scopeAux D u n = some (authorScope D)
  | 0, h => by
    obtain ⟨x, hx, hd⟩ := h 0 (Nat.le_refl _)
    simp [scopeAux, hx, enterScope_author _ hd]
  | n + 1, h => by
    have ih := scopeAux_author D u n (fun k hk => h k (Nat.le_succ_of_le hk))
    obtain ⟨x, hx, hd⟩ := h (n + 1) (Nat.le_refl _)
    simp [scopeAux, ih, hx, enterScope_author _ hd]

theorem authorPath_env {D : ReportDoc} {p : Path} (h : authorPath D p = true) : envAt D p = some D.E := by
  unfold envAt scopeAt
  rw [scopeAux_author D p.unit p.depth]
  · rfl
  · intro k hk
    have := List.all_eq_true.mp h k (List.mem_range.mpr (Nat.lt_succ_of_le hk))
    cases hx : parentAt D p.unit k with
    | none => simp [hx] at this
    | some x => exact ⟨x, rfl, by simpa [hx] using this⟩

def bridgeLeafB (D : ReportDoc) (w : VE.Route.Admission.WireNode) : Bool :=
  match parseBridge w.claim.label with
  | none => false
  | some l =>
    (isAssessmentAt D l.path || holderAt D l.path == some l.agent) &&
    decide (bridgeFormula D l.path = some w.claim.formula) && authorPath D l.path &&
    (match l with
     | .root .. => true
     | .nested _ u n => D.bridges.any (fun b => b.target == ⟨u, n⟩)) &&
    (w.unit.isNone || w.unit == some l.path.unit)

/-- The two bridge-specific diagnostics precede the generic graph rejection. -/
def bridgeLeafDiagnostic (D : ReportDoc) (w : VE.Route.Admission.WireNode) : Option String :=
  match parseBridge w.claim.label with
  | none => none
  | some l =>
    if !(isAssessmentAt D l.path || holderAt D l.path == some l.agent) then
      some s!"BridgeHolder: {l.path.unit}, {l.path.depth}"
    else match l with
      | .root .. => none
      | .nested _ u n =>
        if D.bridges.any (fun b => b.target == ⟨u, n⟩) then none
        else some s!"MissingBridgeRecord: {u}, {n}"

theorem bridgeLeafB_sound {D : ReportDoc} {w : VE.Route.Admission.WireNode} (h : bridgeLeafB D w = true) :
    BridgeAdmitted D w.claim ∧ (w.unit = none ∨ ∃ l, parseBridge w.claim.label = some l ∧ w.unit = some l.path.unit) := by
  unfold bridgeLeafB at h
  cases hp : parseBridge w.claim.label with
  | none => simp [hp] at h
  | some l =>
    rw [hp] at h
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, Option.isNone_iff_eq_none, decide_eq_true_eq] at h
    obtain ⟨⟨⟨⟨hho, hbf⟩, hauth⟩, hrec⟩, hunit⟩ := h
    refine ⟨⟨l, hp, hho, hbf, authorPath_env hauth, ?_⟩, ?_⟩
    · cases l with
      | root => trivial
      | nested a u n =>
        simp only [List.any_eq_true, beq_iff_eq] at hrec
        exact hrec
    · rcases hunit with hu | hu
      · exact Or.inl hu
      · exact Or.inr ⟨l, rfl, hu⟩

def leafB (D : ReportDoc) (w : VE.Route.Admission.WireNode) : Bool :=
  D.units.any (fun u => w.claim.label == "report:" ++ u.id && decide (unitPremise D u = some w.claim.formula) &&
    isReportStatement u.content) ||
  D.units.any (fun u => w.claim.label == "assessment:" ++ u.id && decide (unitPremise D u = some w.claim.formula) &&
    isAssessStatement u.content) ||
  bridgeLeafB D w ||
  decide (VE.Route.Admission.LeafAdmitted (w2Doc D) w)

theorem leafB_sound {D : ReportDoc} {w : VE.Route.Admission.WireNode} (h : leafB D w = true) :
    ReportsLeafAdmitted D w := by
  unfold leafB at h
  simp only [Bool.or_eq_true, List.any_eq_true, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at h
  rcases h with ((⟨u, hu, ⟨hl, hp⟩, hs⟩ | ⟨u, hu, ⟨hl, hp⟩, hs⟩) | hb) | hw
  · exact Or.inl ⟨u, hu, hl, hp, isReportStatement_spec hs⟩
  · exact Or.inr (Or.inl ⟨u, hu, hl, hp, isAssessStatement_spec hs⟩)
  · exact Or.inr (Or.inr (Or.inl (bridgeLeafB_sound hb)))
  · exact Or.inr (Or.inr (Or.inr hw))

def nodeB (D : ReportDoc) (w : VE.Route.Admission.WireNode) : Bool :=
  match w.deduction with
  | some _ => decide (w.claim.label = "asserted" ∧
      ∀ u ∈ w.unit.toList, VE.Route.Admission.AssertedUnit (w2Doc D) u w.claim.formula)
  | none => leafB D w

theorem nodeB_sound {D : ReportDoc} {w : VE.Route.Admission.WireNode} (h : nodeB D w = true) :
    ReportsNodeAdmitted D w := by
  unfold nodeB at h
  unfold ReportsNodeAdmitted
  split
  · rename_i e he
    rw [he] at h
    simp only [decide_eq_true_eq] at h
    exact ⟨h.1, fun u hu => h.2 u (by simp [hu])⟩
  · rename_i he
    rw [he] at h
    exact leafB_sound h

def admitNodes (D : ReportDoc) (ws : List VE.Route.Admission.WireNode) : Except String _root_.Unit :=
  match ws.find? (fun w => !nodeB D w) with
  | some w => .error (VE.Route.Admission.nodeDiagnostic (w2Doc D) w)
  | none => .ok ()

theorem admitNodes_ok (D : ReportDoc) (ws : List VE.Route.Admission.WireNode) (x : _root_.Unit)
    (h : admitNodes D ws = .ok x) : ∀ w ∈ ws, ReportsNodeAdmitted D w := by
  unfold admitNodes at h
  split at h
  · cases h
  · rename_i hf
    intro w hw
    have := List.find?_eq_none.mp hf w hw
    exact nodeB_sound (by simpa using this)

/-! ## The outer binding of graph certificates (3.4) -/

/-- The reports envelope, exactly: `{"environment_id", "document_id"}` with the
recomputed values (as `Run.outerBound` checks a `reports-certificate` case). -/
def envelopeMatches (envId docId : String) (e : Json) : Bool :=
  e.getObjValD "environment_id" == .str envId && e.getObjValD "document_id" == .str docId &&
    (exactFields e ["environment_id", "document_id"]).toBool

def hasField (n : Json) (k : String) : Bool := (n.getObjVal? k).toBool

/-- A graph node with a certificate carries the recomputed envelope; a node
without one carries none. -/
def nodeOuterOk (envId docId : String) (n : Json) : Bool :=
  if hasField n "certificate" then envelopeMatches envId docId (n.getObjValD "envelope")
  else !hasField n "envelope"

def outerDiagnostic (n : Json) : String :=
  let name := (n.getObjValD "name").getStr?.toOption.getD "?"
  if !hasField n "certificate" then s!"InvalidInput: envelope without a certificate on node {name}"
  else if !hasField n "envelope" then s!"AdmissionError: the certificate of node {name} lacks the reports envelope"
  else s!"AdmissionError: the certificate of node {name} is bound to another document or environment"

def checkOuter (envId docId : String) (ns : List Json) : Except String _root_.Unit :=
  match ns.find? (fun n => !nodeOuterOk envId docId n) with
  | some n => .error (outerDiagnostic n)
  | none => .ok ()

theorem checkOuter_ok {envId docId : String} {ns : List Json} {x : _root_.Unit}
    (h : checkOuter envId docId ns = .ok x) : ∀ n ∈ ns, nodeOuterOk envId docId n = true := by
  unfold checkOuter at h
  split at h
  · cases h
  · rename_i hf
    intro n hn
    simpa using List.find?_eq_none.mp hf n hn

/-- The node as the frozen W2 decoder reads it: without the reports envelope. -/
def stripEnvelope : Json → Json
  | .obj kvs => .obj (kvs.erase "envelope")
  | n => n

/-! ## Admission -/

/-- Admission of a W2 document under `reports@0`: decode and check the reports
document, decode the graph at E_reports, bind every deduction to
`environment_id(E_reports)`, check every node, check the graph with the
unchanged W2 checker, and record the envelope. -/
def admissionReports (profiles : List String) (environment : Json) (j : Json) :
    Except String ReportsAdmitted := do
  let c ← Wire.decodeDocument environment j
  let D := c.dec.D
  VE.Route.Admission.require (c.dec.re.profiles == profiles) "InvalidInput: profiles"
  let envId ← VE.Route.Wire.environmentId profiles environment
  let graphJson ← j.getObjVal? "graph"
  exactFields graphJson ["root", "nodes"]
  let root ← stringField graphJson "root"
  let nodeArray ← (← graphJson.getObjVal? "nodes").getArr?
  VE.Route.Admission.require (nodeArray.size ≤ 1000) "ResourceLimit: graph node count"
  checkOuter envId (documentId D) nodeArray.toList
  let decoded ← (nodeArray.toList.map stripEnvelope).mapM (VE.Route.Admission.decodeNode (envReports D) false)
  VE.Route.Admission.checkBindings profiles (Wire.environmentReportsJson environment D) decoded
  let wires := decoded.map Prod.fst
  let diagnosis := wires.findSome? (bridgeLeafDiagnostic D)
  VE.Route.Admission.require diagnosis.isNone (diagnosis.getD "")
  admitNodes D wires
  let g : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  let r ← VE.Route.Admission.checkGraph (envReports D) g
  VE.Route.Admission.require (decide (CitationsClosed (w2Doc D) r))
    "AdmissionError: a cited lemma's leaves are missing from the report"
  VE.Route.Admission.require (decide (ChoicesCompatible r)) "AdmissionError: incompatible reading choices"
  pure ⟨D, wires, g, r, (envId, documentId D), nodeArray.toList⟩

/-- Mirrors VE.Route.Admission.admit_report_sound conjunct for conjunct, with
the envelope added. The spec's envelope conjunct compares an `Except` with a
string; it is stated here as the success of the recomputation (lean/REPORTS.md,
deviations), and the decoded document is the one the raw input decodes to.
Every node of the input graph that carries a certificate carries exactly the
recomputed reports envelope (3.4's outer binding). -/
theorem reports_admission_sound (profiles : List String) (environment : Json) (j : Json) (res : ReportsAdmitted)
    (h : admissionReports profiles environment j = .ok res) :
    WellFormedReports res.D = true ∧
    (∃ c, Wire.decodeDocument environment j = .ok c ∧ c.dec.D = res.D) ∧
    VE.Route.Wire.environmentId profiles environment = .ok res.envelope.1 ∧ res.envelope.2 = documentId res.D ∧
    (∃ g ns, j.getObjVal? "graph" = .ok g ∧ g.getObjVal? "nodes" = .ok ns ∧ ns.getArr? = .ok res.graphNodes.toArray) ∧
    (∀ n ∈ res.graphNodes, hasField n "certificate" = true →
      envelopeMatches res.envelope.1 res.envelope.2 (n.getObjValD "envelope") = true) ∧
    res.graph.nodes = res.wires.map VE.Route.Admission.WireNode.toNode ∧
    VE.Graph.Acyclic res.graph ∧ (res.graph.nodes.map (fun n => n.claim.name)).Nodup ∧
    res.report.root.name = res.graph.root ∧
    VE.Graph.SoundReport.{u} (envReports res.D) res.graph res.report ∧
    (∀ w ∈ res.wires, ReportsNodeAdmitted res.D w) ∧
    (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
       w.claim = leaf ∧ w.deduction = none ∧ ReportsLeafAdmitted res.D w) ∧
    VE.Route.Admission.CitationsClosed (w2Doc res.D) res.report ∧ VE.Route.Admission.ChoicesCompatible res.report := by
  unfold admissionReports at h
  obtain ⟨c, hc, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨envId, henv, h⟩ := bind_ok h
  obtain ⟨gj, hgj, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨root, _, h⟩ := bind_ok h
  obtain ⟨nj, hnj, h⟩ := bind_ok h
  obtain ⟨arr, harr, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, hout, h⟩ := bind_ok h
  obtain ⟨decoded, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, hadm, h⟩ := bind_ok h
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨_, hcit, h⟩ := bind_ok h
  obtain ⟨_, hch, h⟩ := bind_ok h
  cases h
  have hnodes := admitNodes_ok _ _ _ hadm
  obtain ⟨hacyc, hnd, hroot, hsound⟩ :=
    VE.Graph.check_sound.{u} _ _ r (VE.Route.Admission.checkGraph_ok _ _ r hr)
  have houter : ∀ n ∈ arr.toList, hasField n "certificate" = true →
      envelopeMatches envId (documentId c.dec.D) (n.getObjValD "envelope") = true := by
    intro n hn hcert
    have := checkOuter_ok hout n hn
    simpa [nodeOuterOk, hcert] using this
  refine ⟨c.wf, ⟨c, hc, rfl⟩, henv, rfl, ⟨gj, nj, hgj, hnj, by simpa using harr⟩, houter, rfl, hacyc, hnd, hroot,
    hsound, hnodes, ?_,
    of_decide_eq_true (VE.Route.Gate.require_ok hcit), of_decide_eq_true (VE.Route.Gate.require_ok hch)⟩
  intro leaf hl
  obtain ⟨node, hn, hcl, hde⟩ := (hsound.2.2.1 leaf hl).2
  obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hn
  refine ⟨w, hw, hcl, hde, ?_⟩
  have := hnodes w hw
  unfold ReportsNodeAdmitted at this
  simp only [VE.Route.Admission.WireNode.toNode] at hde
  rw [hde] at this
  exact this

/-- As VE.Route.Admission.admit_labels_decoded: every assumption of the report
is a decoded leaf with exactly its decoded label, name and formula. -/
theorem reports_labels_decoded (profiles : List String) (environment : Json) (j : Json) (res : ReportsAdmitted)
    (h : admissionReports profiles environment j = .ok res) :
    ∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
      w.claim.label = leaf.label ∧ w.claim.name = leaf.name ∧ w.claim.formula = leaf.formula := by
  intro leaf hl
  obtain ⟨w, hw, rfl, _, _⟩ :=
    (reports_admission_sound.{0} profiles environment j res h).2.2.2.2.2.2.2.2.2.2.2.2.1 leaf hl
  exact ⟨w, hw, rfl, rfl, rfl⟩

end VE.Reports
