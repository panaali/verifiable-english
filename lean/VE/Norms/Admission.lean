import VE.Norms.Replay
import VE.Route.Admission

/-! W2 admission on the norms route. Norm content is decoded as a rule only for
active `norm` units. Its FOL premises are regenerated from that rule set; graph
leaves may name those premises, while every other leaf follows W2 admission. -/
namespace VE.Norms.Admission
open Lean
open VE.Route.Admission
open VE.Bridge (exactFields stringField)
universe u

/-- Norm content by the kind of its unit (Python `admit_norm_document`): an
active `norm` unit contributes a layer; a quoted unit keeps its content
inactive; under any other kind norm content is rejected, never discarded. -/
inductive NormContent where
  | active (content : Json)
  | quoted (content : Json)

/-- The one table of norm content roles by unit kind, read by every route that
splits a document's norms (this admission and the document mode). -/
def normRole (kind : Kind) (content : Json) : Except String NormContent :=
  if kind == .norm then pure (.active content)
  else if kind.quoted then pure (.quoted content)
  else throw "norm content requires a norm or quoted kind"

/-- Remove norm content only from the copy passed to the FOL unit decoder.
The original source document remains intact for report identity. -/
def splitUnit (j : Json) : Except String (Json × Option NormContent) := do
  match j.getObjVal? "content" with
  | .ok content =>
    if (content.getObjVal? "norm").toBool then
      let norm ← normRole (← decodeKind 16 (← j.getObjVal? "kind")) content
      let obj ← VE.Bridge.fields j
      return (Json.mkObj (obj.filter (·.1 != "content")), some norm)
    else return (j, none)
  | .error _ => return (j, none)

/-- The FOL copy of the document, the active norm objects and the quoted ones. -/
def splitDocument (j : Json) : Except String (Json × Json × List Json) := do
  let units ← (← (← j.getObjVal? "units").getArr?).toList.mapM splitUnit
  let clean := j.setObjVal! "units" (Json.arr (units.map Prod.fst).toArray)
  let active := Json.arr (units.filterMap (fun u => match u.2 with
    | some (.active c) => some c
    | _ => none)).toArray
  let quoted := units.filterMap (fun u => match u.2 with
    | some (.quoted c) => some c
    | _ => none)
  pure (clean, active, quoted)

/-- A quoted norm never contributes a layer, but it is still a norm object over
the source environment: every single-rule check of `validate` applies. Its
precedence edges name rules of the quoted source and are not resolved here. -/
def checkQuoted (src : Wire.Source) (j : Json) : Except String Unit := do
  let N ← Wire.decodeNorm j
  validate ⟨src.D.E, src.D.lits, ⟨src.D.T.regulated, [], [{ N with over := [] }]⟩⟩

/-- Exact regenerated layer leaf, with no unit pointer. -/
def LayerLeaf (src : Wire.Source) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    ((syms src.D.T).filterMap (fun | .reg r => some r | .defn _ => none)).any
      (fun r => decide (w.claim.label = "layer:norms:" ++ r.name ∧
        w.claim.formula = elabPremise src.D.T r))) = true

instance (src : Wire.Source) (w : WireNode) : Decidable (LayerLeaf src w) := by
  unfold LayerLeaf
  infer_instance

/-- A `background:profile` leaf equal to a regenerated pair premise (3.1),
with no unit pointer. W2's own Background has no profile generator. -/
def ProfileLeaf (src : Wire.Source) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone && w.claim.label == "background:profile" &&
    (pairPremises src.D.T).any (fun a => decide (w.claim.formula = a))) = true

instance (src : Wire.Source) (w : WireNode) : Decidable (ProfileLeaf src w) := by
  unfold ProfileLeaf
  infer_instance

def NodeAdmitted (src : Wire.Source) (D : VE.Route.Admission.Doc) (w : WireNode) : Prop :=
  VE.Route.Admission.NodeAdmitted D w ∨ LayerLeaf src w ∨ ProfileLeaf src w

instance (src : Wire.Source) (D : VE.Route.Admission.Doc) (w : WireNode) :
    Decidable (NodeAdmitted src D w) := by
  unfold NodeAdmitted; infer_instance

def admitNodes (src : Wire.Source) (D : VE.Route.Admission.Doc) (ws : List WireNode) :
    Except String Unit :=
  match ws.find? (fun w => !decide (NodeAdmitted src D w)) with
  | some w => .error (VE.Route.Admission.nodeDiagnostic D w)
  | none => .ok ()

theorem admitNodes_ok (src : Wire.Source) (D : VE.Route.Admission.Doc)
    (ws : List WireNode) (h : admitNodes src D ws = .ok ()) :
    ∀ w ∈ ws, NodeAdmitted src D w := by
  unfold admitNodes at h
  split at h
  · cases h
  · rename_i hf
    intro w hw
    have := List.find?_eq_none.mp hf w hw
    simpa using this

/-! ## Certificate bindings

P0 `checkBindings`, restated as a list traversal so that its success yields a
per-node binding fact; same checks, same order, same diagnostics. -/

open VE.Order.ProfileGate (bind_ok)

theorem mapM_ok_mem {ε α β : Type} (f : α → Except ε β) :
    ∀ (l : List α) (r : List β), l.mapM f = .ok r → ∀ y ∈ r, ∃ x ∈ l, f x = .ok y := by
  intro l
  induction l with
  | nil => intro r h y hy; simp [List.mapM_nil, pure, Except.pure] at h; subst h; cases hy
  | cons a l ih =>
    intro r h y hy
    rw [List.mapM_cons] at h
    obtain ⟨b, hb, h⟩ := bind_ok h
    obtain ⟨bs, hbs, h⟩ := bind_ok h
    cases h
    rcases List.mem_cons.mp hy with rfl | hy
    · exact ⟨a, List.mem_cons_self .., hb⟩
    · obtain ⟨x, hx, hf⟩ := ih bs hbs y hy
      exact ⟨x, List.mem_cons_of_mem _ hx, hf⟩

theorem forM_ok {ε α : Type} (f : α → Except ε Unit) :
    ∀ (l : List α), l.forM f = .ok () → ∀ x ∈ l, f x = .ok () := by
  intro l
  induction l with
  | nil => intro _ x hx; cases hx
  | cons a l ih =>
    intro h x hx
    simp only [List.forM] at h
    obtain ⟨u, hu, h⟩ := bind_ok h
    rcases List.mem_cons.mp hx with rfl | hx
    · exact hu
    · exact ih h x hx

/-- The source ASTs of a deduction's premise nodes, in order. -/
def premiseAsts (nodes : List (WireNode × Json)) (edge : VE.Graph.Edge VE.Tableau.Certificate) :
    Except String (List Json) :=
  edge.premises.mapM fun p =>
    match nodes.find? (fun n => n.1.claim.name == p) with
    | some n => pure n.2
    | none => throw s!"dangling premise {p}"

def nodeBinding (profiles : List String) (environment : Json) (nodes : List (WireNode × Json))
    (x : WireNode × Json) : Except String Unit :=
  match x.1.deduction with
  | none => pure ()
  | some edge => do
    VE.Route.Wire.bindingOk profiles environment (← premiseAsts nodes edge) x.2
      edge.certificate.environment_id edge.certificate.premise_meaning_ids
      edge.certificate.conclusion_meaning_id

def checkBindings (profiles : List String) (environment : Json) (nodes : List (WireNode × Json)) :
    Except String Unit :=
  nodes.forM (nodeBinding profiles environment nodes)

/-- A deduction's certificate names, by `ve.core@0.2` identity, the canonical
source environment, its premise nodes' source ASTs in order and its own AST. -/
def CertificateBound (profiles : List String) (environment : Json) (nodes : List (WireNode × Json))
    (x : WireNode × Json) : Prop :=
  ∀ edge, x.1.deduction = some edge → ∃ envId asts pids cid,
    VE.Route.Wire.environmentId profiles environment = .ok envId ∧
    premiseAsts nodes edge = .ok asts ∧
    asts.mapM (VE.Route.Wire.meaningId profiles envId) = .ok pids ∧
    VE.Route.Wire.meaningId profiles envId x.2 = .ok cid ∧
    edge.certificate.environment_id = envId ∧ edge.certificate.premise_meaning_ids = pids ∧
    edge.certificate.conclusion_meaning_id = cid

theorem nodeBinding_bound (profiles : List String) (environment : Json)
    (nodes : List (WireNode × Json)) (x : WireNode × Json)
    (h : nodeBinding profiles environment nodes x = .ok ()) :
    CertificateBound profiles environment nodes x := by
  intro edge hedge
  unfold nodeBinding at h
  rw [hedge] at h
  obtain ⟨asts, hasts, h⟩ := bind_ok h
  unfold VE.Route.Wire.bindingOk at h
  obtain ⟨envId, he, h⟩ := bind_ok h
  obtain ⟨pids, hp, h⟩ := bind_ok h
  obtain ⟨cid, hc, h⟩ := bind_ok h
  refine ⟨envId, asts, pids, cid, he, hasts, hp, hc, ?_⟩
  by_cases hb : (edge.certificate.environment_id == envId &&
      edge.certificate.premise_meaning_ids == pids && edge.certificate.conclusion_meaning_id == cid) = true
  · simp only [Bool.and_eq_true, beq_iff_eq] at hb
    exact ⟨hb.1.1, hb.1.2, hb.2⟩
  · simp only [hb] at h
    cases h

theorem checkBindings_bound (profiles : List String) (environment : Json)
    (nodes : List (WireNode × Json)) (h : checkBindings profiles environment nodes = .ok ()) :
    ∀ x ∈ nodes, CertificateBound profiles environment nodes x := fun x hx =>
  nodeBinding_bound profiles environment nodes x (forM_ok _ nodes h x hx)

/-- A decoded node carries the source AST its claim formula was decoded from. -/
theorem decodeNode_ast (E : VE.Environment) (data : Bool) (j : Json) (x : WireNode × Json)
    (h : VE.Route.Admission.decodeNode E data j = .ok x) :
    j.getObjVal? "ast" = .ok x.2 ∧
      VE.Route.Wire.decodeClosed E x.2 (data && !x.1.claim.label.startsWith "background:") =
        .ok x.1.claim.formula := by
  unfold VE.Route.Admission.decodeNode at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨a, ha, h⟩ := bind_ok h
  -- Label, formula, unit and deduction are decoded in sequence.
  simp only [bind, Except.bind, pure, Except.pure, Functor.map, Except.map] at h
  repeat' split at h
  all_goals first
    | (cases h; done)
    | (injection h with h; subst h; simp_all)

theorem getArr_ok {j : Json} {a : Array Json} (h : j.getArr? = .ok a) : j = .arr a := by
  cases j <;> simp [Json.getArr?] at h
  · cases h; rfl

/-! ## Admission -/

structure Admitted where
  src : Wire.Source
  doc : VE.Route.Admission.Doc
  /-- The canonical source environment (Python `Environment.to_dict()`). -/
  canonical : Json
  graphJson : Json
  /-- The raw graph nodes and their decodings, with each node's source AST. -/
  nodes : Array Json
  decoded : List (WireNode × Json)
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
  kinds : List Json

/-- Python `admit_norm_document`'s envelope gates, checked before the document:
the `norms@0` profile, then the FOL family, with Python's diagnostics. -/
def envelopeGate (environment : Json) : Except String Unit := do
  let e ← VE.Route.Gate.decodeEnvelope environment
  unless e.profiles.contains "norms@0" do throw "UnsupportedProfile: norms@0 is required"
  unless e.family == .fol do
    throw (VE.Route.Gate.unsupported "norm document admission is FOL-only")

/-- Required document admission: regenerated norm layers, W2 provenance,
certificate bindings, graph checking, citations and reading choices. -/
def admitDocument (environment document : Json) : Except String Admitted := do
  envelopeGate environment
  VE.Bridge.displayFields document ["units", "graph"]
    ["lemmas", "open_terms", "reading_sets", "narrowings"]
  let (clean, norms, quoted) ← splitDocument document
  let src ← Wire.decodeSource environment norms (flags := true)
  quoted.forM (checkQuoted src)
  let D₀ ← VE.Route.Admission.decodeDoc src.ne.rv (src.ne.profiles.contains "data@0") clean
  let D := { D₀ with literals := src.ne.rv.literals }
  let graphJson ← document.getObjVal? "graph"
  exactFields graphJson ["root", "nodes"]
  let root ← stringField graphJson "root"
  let nodeArray ← (← graphJson.getObjVal? "nodes").getArr?
  VE.Route.Admission.require (nodeArray.size ≤ 1000) "ResourceLimit: graph node count"
  let decoded ← nodeArray.toList.mapM (VE.Route.Admission.decodeNode src.ne.rv.environment (src.ne.profiles.contains "data@0"))
  let canonical ← Wire.canonicalEnvironmentJson environment
  checkBindings src.ne.profiles canonical decoded
  let wires := decoded.map Prod.fst
  admitNodes src D wires
  let g : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  let r ← VE.Route.Admission.checkGraph src.ne.rv.environment g
  VE.Route.Admission.require (decide (CitationsClosed D r))
    "AdmissionError: a cited lemma's leaves are missing from the report"
  VE.Route.Admission.require (decide (ChoicesCompatible r))
    "AdmissionError: incompatible reading choices"
  pure ⟨src, D, canonical, graphJson, nodeArray, decoded, wires, g, r,
    D.units.map (fun x => renderKind x.kind)⟩

/-- Decoder soundness from the raw source: the active norm objects decode to
the well-formed tree whose layers are regenerated, every quoted norm passes the
single-rule checks, the W2 document is decoded from the same source with the
environment's literals, and every graph node is decoded from the source graph
with the AST that its certificate binds. -/
def SourceDecoded (environment document : Json) (res : Admitted) : Prop :=
  (∃ clean norms quoted, splitDocument document = .ok (clean, norms, quoted) ∧
    Wire.decodeSource environment norms (flags := true) = .ok res.src ∧
    (∀ q ∈ quoted, checkQuoted res.src q = .ok ()) ∧
    ∃ D₀, VE.Route.Admission.decodeDoc res.src.ne.rv (res.src.ne.profiles.contains "data@0") clean = .ok D₀ ∧
      res.doc = { D₀ with literals := res.src.ne.rv.literals }) ∧
  WellFormed res.src.D = true ∧ res.src.D.E = res.src.ne.rv.environment ∧
  res.src.D.lits = res.src.ne.rv.literals ∧
  document.getObjVal? "graph" = .ok res.graphJson ∧
  res.graphJson.getObjVal? "nodes" = .ok (Json.arr res.nodes) ∧
  stringField res.graphJson "root" = .ok res.graph.root ∧
  res.wires = res.decoded.map Prod.fst ∧ res.graph.nodes = res.wires.map WireNode.toNode ∧
  (∀ x ∈ res.decoded, ∃ j ∈ res.nodes.toList,
    VE.Route.Admission.decodeNode res.src.ne.rv.environment (res.src.ne.profiles.contains "data@0") j = .ok x ∧
    j.getObjVal? "ast" = .ok x.2 ∧
    VE.Route.Wire.decodeClosed res.src.ne.rv.environment x.2
      ((res.src.ne.profiles.contains "data@0") && !x.1.claim.label.startsWith "background:") =
        .ok x.1.claim.formula)

/-- Every certificate is bound to the recomputed canonical source environment
and the source ASTs of its premises and conclusion. -/
def CertificatesBound (environment : Json) (res : Admitted) : Prop :=
  Wire.canonicalEnvironmentJson environment = .ok res.canonical ∧
  ∀ x ∈ res.decoded, CertificateBound res.src.ne.profiles res.canonical res.decoded x

/-- The norms extension of W2's admission relation: a sound checked graph,
every node admitted by W2 provenance, as an exact regenerated layer leaf or as
a regenerated pair-premise profile leaf,
each assumption exactly a decoded leaf, closed citations and compatible
reading choices. -/
def ReportAdmitted (res : Admitted) : Prop :=
  VE.Graph.SoundReport.{0} res.src.ne.rv.environment res.graph res.report ∧
  (∀ w ∈ res.wires, NodeAdmitted res.src res.doc w) ∧
  (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
    w.claim = leaf ∧ w.deduction = none ∧ NodeAdmitted res.src res.doc w) ∧
  CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report

/-- Everything a successful admission establishes about its raw input. -/
theorem admitDocument_spec (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) :
    SourceDecoded environment document res ∧ CertificatesBound environment res ∧
    VE.Graph.SoundReport.{u} res.src.ne.rv.environment res.graph res.report ∧
    (∀ w ∈ res.wires, NodeAdmitted res.src res.doc w) ∧
    (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
      w.claim = leaf ∧ w.deduction = none ∧ NodeAdmitted res.src res.doc w) ∧
    CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report := by
  unfold admitDocument at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨⟨clean, norms, quoted⟩, hsplit, h⟩ := bind_ok h
  obtain ⟨src, hsrc, h⟩ := bind_ok h
  obtain ⟨_, hq, h⟩ := bind_ok h
  obtain ⟨D₀, hD, h⟩ := bind_ok h
  obtain ⟨graphJson, hg, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨root, hroot, h⟩ := bind_ok h
  obtain ⟨nj, hnj, h⟩ := bind_ok h
  obtain ⟨nodeArray, harr, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨decoded, hdec, h⟩ := bind_ok h
  obtain ⟨canonical, hcan, h⟩ := bind_ok h
  obtain ⟨_, hbind, h⟩ := bind_ok h
  obtain ⟨_, hadm, h⟩ := bind_ok h
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨_, hc, h⟩ := bind_ok h
  obtain ⟨_, hch, h⟩ := bind_ok h
  cases h
  have hnodes := admitNodes_ok src _ (decoded.map Prod.fst) hadm
  obtain ⟨_, _, _, hsound⟩ := VE.Graph.check_sound.{u} src.ne.rv.environment _ r
    (VE.Route.Admission.checkGraph_ok _ _ r hr)
  have hnj' : nj = Json.arr nodeArray := getArr_ok harr
  subst hnj'
  refine ⟨⟨⟨clean, norms, quoted, hsplit, hsrc, forM_ok _ quoted hq, D₀, hD, rfl⟩,
      src.wf, src.env, src.lits, hg, hnj, hroot, rfl, rfl, ?_⟩,
    ⟨hcan, checkBindings_bound _ _ decoded hbind⟩, hsound, hnodes, ?_,
    of_decide_eq_true (VE.Route.Gate.require_ok hc),
    of_decide_eq_true (VE.Route.Gate.require_ok hch)⟩
  · intro x hx
    obtain ⟨j, hj, hd⟩ := mapM_ok_mem _ _ decoded hdec x hx
    exact ⟨j, hj, hd, decodeNode_ast _ _ j x hd⟩
  · intro leaf hl
    obtain ⟨node, hn, hcl, hde⟩ := (hsound.2.2.1 leaf hl).2
    obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hn
    exact ⟨w, hw, hcl, hde, hnodes w hw⟩

/-- A successful admission has a sound checked graph and every submitted node
is admitted either by W2's ordinary provenance rules or by a regenerated norm
layer. Each report assumption is exactly one of those decoded leaves. -/
theorem norms_wire_admission_sound (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) :
    VE.Graph.SoundReport.{u} res.src.ne.rv.environment res.graph res.report ∧
    (∀ w ∈ res.wires, NodeAdmitted res.src res.doc w) ∧
    (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
      w.claim = leaf ∧ w.deduction = none ∧ NodeAdmitted res.src res.doc w) :=
  let ⟨_, _, hsound, hnodes, hleaves, _⟩ := admitDocument_spec.{u} environment document res h
  ⟨hsound, hnodes, hleaves⟩

theorem layerLeaf_formula (src : Wire.Source) (w : WireNode) (h : LayerLeaf src w) :
    w.claim.formula ∈ elaborate src.D.T := by
  simp only [LayerLeaf, Bool.and_eq_true] at h
  have ha := h.2
  obtain ⟨r, hr, he⟩ := List.any_eq_true.mp ha
  have heq : w.claim.label = "layer:norms:" ++ r.name ∧
      w.claim.formula = elabPremise src.D.T r := of_decide_eq_true he
  rw [heq.2]
  change elabPremise src.D.T r ∈
    (syms src.D.T).filterMap (fun | .reg r => some (elabPremise src.D.T r) | .defn _ => none)
  obtain ⟨q, hq, hqr⟩ := List.mem_filterMap.mp
    (show r ∈ (syms src.D.T).filterMap (fun | .reg r => some r | .defn _ => none) from hr)
  cases q with
  | reg r' =>
    simp only [Option.some.injEq] at hqr
    subst hqr
    exact List.mem_filterMap.mpr ⟨.reg r', hq, rfl⟩
  | defn d => cases hqr

/-- A W2 `background:<g>` leaf. -/
def backgroundLeaf (c : VE.Graph.Claim) : Bool :=
  match parseLabel c.label with
  | some (.background _) => true
  | _ => false

/-- The report assumptions that stay explicit hypotheses: every leaf that is
neither a regenerated layer leaf nor a regenerated Background leaf. -/
def otherAssumptions (res : Admitted) : List VE.Graph.Claim :=
  res.report.assumptions.filter (fun c =>
    !backgroundLeaf c && !decide (∃ w ∈ res.wires, w.claim = c ∧ LayerLeaf res.src w))

/-- Semantic report consequence: in every admissible structure satisfying the
regenerated Background and layer premises, the remaining report assumptions
entail the report's root. Layer leaves are discharged by the elaborations and
Background leaves by the regenerated literal and pair premises. -/
theorem norms_wire_report_consequence (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) (S : VE.Structure.{u})
    (hS : S.Admissible res.src.ne.rv.environment)
    (hflags : Sat S (VE.Data.Background.generate res.doc.flags))
    (hregen : Sat S (background res.src.D ++ elaborate res.src.D.T))
    (hother : Sat S ((otherAssumptions res).map (·.formula))) :
    res.report.root.formula.denote S [] := by
  obtain ⟨⟨⟨_, _, _, _, _, _, _, _, hdoc⟩, _, _, hlits, _⟩, _, hsound, _, hleaves, _⟩ :=
    admitDocument_spec.{u} environment document res h
  apply hsound.2.2.2.1 S hS
  intro a ha
  obtain ⟨leaf, hl, rfl⟩ := List.mem_map.mp ha
  by_cases hlayer : ∃ w ∈ res.wires, w.claim = leaf ∧ LayerLeaf res.src w
  · obtain ⟨w, _, hwl, hw⟩ := hlayer
    rw [← hwl]
    exact hregen _ (List.mem_append_right _ (layerLeaf_formula res.src w hw))
  by_cases hb : backgroundLeaf leaf = true
  · obtain ⟨w, hw, hwl, hde, hadm⟩ := hleaves leaf hl
    rcases hadm with hadm | hadm | hadm
    · unfold VE.Route.Admission.NodeAdmitted at hadm
      rw [hde] at hadm
      unfold backgroundLeaf at hb
      unfold LeafAdmitted at hadm
      rw [hwl] at hadm
      split at hb
      · rename_i g hg
        rw [hg] at hadm
        obtain ⟨_, p, hp, hpe⟩ := hadm
        subst hpe
        rcases List.mem_append.mp hp with hp | hp
        · obtain ⟨b, hbm, hbe⟩ := List.mem_map.mp hp
          simp only [Prod.mk.injEq] at hbe
          rw [← hbe.1]
          exact hflags b hbm
        · obtain ⟨b, hbm, hbe⟩ := List.mem_map.mp hp
          simp only [Prod.mk.injEq] at hbe
          rw [← hbe.1]
          apply hregen
          apply List.mem_append_left
          unfold background backgroundBase
          apply List.mem_append_left
          apply List.mem_append_right
          rw [hlits, ← (show res.doc.literals = res.src.ne.rv.literals by rw [hdoc])]
          exact hbm
      · cases hb
    · exact absurd ⟨w, hw, hwl, hadm⟩ hlayer
    · simp only [ProfileLeaf, Bool.and_eq_true] at hadm
      obtain ⟨a, ha, hfa⟩ := List.any_eq_true.mp hadm.2
      rw [← hwl, of_decide_eq_true hfa]
      apply hregen
      apply List.mem_append_left
      unfold background
      exact List.mem_append_right _ ha
  · apply hother
    apply List.mem_map_of_mem
    simp only [otherAssumptions, List.mem_filter]
    refine ⟨hl, ?_⟩
    simp only [Bool.not_eq_true] at hb
    simp [hb, hlayer]

end VE.Norms.Admission
