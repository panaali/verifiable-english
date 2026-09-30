import VE.Rights.Wire
import VE.SoftNorms.Admission

/-! W2 admission on a regenerated rights document. The source units stay in document
order for rights correlation; the copy sent to W2's formula decoder has their content
removed, so no rights object is ever decoded as an asserted FOL formula. -/
namespace VE.Rights.Admission
open Lean
open VE.Norms
open VE.Rights.Wire
open VE.Route.Admission
open VE.Norms.Admission (checkBindings)
open VE.SoftNorms (soften envPrime)

def splitUnit (u : Json) : Except String (Json × Option Json) := do
  let kind ← u.getObjVal? "kind"
  let content := u.getObjValD "content"
  let tag := match content with
    | .obj fields => fields.toList.map (·.1)
    | _ => []
  let active := match kind with
    | .str "right" => tag == ["right"]
    | .str "right_lines" => tag == ["right_lines"]
    | .str "limitation" => tag == ["limitation"]
    | .str "bar" => tag == ["bar"]
    | .str "norm" => tag == ["norm"] || tag == ["cites", "norm"]
    | _ => false
  if active then
    let fields ← VE.Bridge.fields u
    let clean := Json.mkObj (fields.filter (·.1 != "content"))
    return (clean.setObjVal! "kind" (.str "norm"), some content)
  if tag.contains "right" || tag.contains "right_lines" ||
      tag.contains "limitation" || tag.contains "bar" || tag.contains "norm" then
    throw "InvalidInput: rights content requires its matching active unit kind"
  return (u, none)

/-- The W2 document without rights content, and the rights source: the document's unit ids
(what a citation may name, 3.2) followed by the active rights and outside norm contents. -/
def splitDocument (document : Json) : Except String (Json × Json) := do
  let raw := (← (← document.getObjVal? "units").getArr?).toList
  let units ← raw.mapM splitUnit
  let ids ← raw.mapM (fun u => VE.Bridge.stringField u "id")
  let clean := document.setObjVal! "units" (Json.arr (units.map Prod.fst).toArray)
  let active := Json.arr (#[Json.mkObj [("source_units", toJson ids)]] ++ (units.filterMap Prod.snd).toArray)
  return (clean, active)

def checkCites (ids : List String) (cites : Json) : Except String Unit := do
  if cites == .null then return ()
  let entries ← VE.Bridge.fields cites
  for (_, targets) in entries do
    let names ← VE.Bridge.strings targets
    if names.isEmpty then throw "InvalidInput: cites must list unit ids"
    for n in names do
      unless ids.contains n do throw s!"UnknownSymbol: unit {n}"

def checkSourceCites (document : Json) : Except String Unit := do
  let units := (← (← document.getObjVal? "units").getArr?).toList
  let ids ← units.mapM (fun u => VE.Bridge.stringField u "id")
  for u in units do
    let content := u.getObjValD "content"
    let lines := if (content.getObjVal? "right").toBool then
        (content.getObjValD "right").getObjValD "lines"
      else (content.getObjValD "right_lines").getObjValD "lines"
    match lines with
    | .arr ls =>
      for line in ls do
        checkCites ids (line.getObjValD "cites")
    | _ => pure ()
    if (content.getObjVal? "norm").toBool && (content.getObjVal? "cites").toBool then
      checkCites ids (content.getObjValD "cites")

def readingRef (j : Json) : Except String (String × Nat) := do
  VE.Bridge.exactFields j ["set", "version"]
  return (← VE.Bridge.stringField j "set", ← (← j.getObjVal? "version").getNat?)

def labelValues (sets : List Json) (ref : String × Nat) (axis : String) : List String :=
  match sets.find? (fun s => s.getObjValD "id" == .str ref.1 &&
      (s.getObjValD "version").getNat?.toOption == some ref.2) with
  | none => []
  | some s => match s.getObjValD "labels" with
    | .arr labels => labels.toList.filterMap (fun l =>
        (l.getObjValD axis).getStr?.toOption)
    | _ => []

/-- The active version of a set is its latest one, as on the Python route. -/
def activeVersion (sets : List Json) (name : String) : Option Nat :=
  (sets.filterMap (fun s =>
    if s.getObjValD "id" == .str name then (s.getObjValD "version").getNat?.toOption
    else none)).max?

/-- Whether one reading per coupled set can be chosen so that every coupling agrees on its
axis (6.2): a joint search over complete choices, not one axis at a time. Each set's readings
are first reduced to their distinct values on the coupled axes. -/
def jointlySatisfiable (constraints : List (String × List String)) :
    List (String × List Json) → List (String × Json) → Bool
  | [], _ => true
  | (name, labels) :: rest, chosen =>
    labels.any (fun lab =>
      constraints.all (fun (axis, members) => !members.contains name ||
        chosen.all (fun (other, previous) => !members.contains other ||
          previous.getObjValD axis == lab.getObjValD axis)) &&
      jointlySatisfiable constraints rest ((name, lab) :: chosen))

def validateCouplings (document : Json) : Except String (List String) := do
  let units := (← (← document.getObjVal? "units").getArr?).toList
  let unitIds ← units.mapM (fun u => VE.Bridge.stringField u "id")
  let sets := match document.getObjValD "reading_sets" with
    | .arr xs => xs.toList
    | _ => []
  let couplings ← match document.getObjVal? "couplings" with
    | .ok (.arr xs) => pure xs.toList
    | .ok _ => throw "invalid couplings"
    | .error _ => pure []
  if couplings.length > 8 then throw "ResourceLimit: couplings"
  let mut ids : List String := []
  for c in couplings do
    VE.Bridge.exactFields c ["id", "axis", "sets", "by", "reason_spans"]
    let id ← VE.Bridge.stringField c "id"
    let axis ← VE.Bridge.stringField c "axis"
    let author ← VE.Bridge.stringField c "by"
    unless token id && token axis && token author && !ids.contains id do
      throw "invalid coupling"
    ids := ids ++ [id]
    let reason ← VE.Bridge.strings (c.getObjValD "reason_spans")
    unless !reason.isEmpty && reason.all unitIds.contains do
      throw "invalid coupling"
    let refs ← (← (c.getObjValD "sets").getArr?).toList.mapM readingRef
    unless refs.length ≥ 2 && (refs.map (·.1)).eraseDups.length == refs.length do
      throw "invalid coupling set"
    for ref in refs do
      let some s := sets.find? (fun s => s.getObjValD "id" == .str ref.1 &&
          (s.getObjValD "version").getNat?.toOption == some ref.2)
        | throw "invalid coupling set"
      unless activeVersion sets ref.1 == some ref.2 do throw "invalid coupling set"
      let readings := match s.getObjValD "readings" with
        | .arr xs => xs.toList
        | _ => []
      let values := labelValues sets ref axis
      unless values.length == readings.length && values.all token do
        throw s!"CouplingLabelMissing: {id}, {ref.1}"
    let common := labelValues sets refs.head! axis
    unless common.any (fun v => refs.all (fun ref => (labelValues sets ref axis).contains v)) do
      throw s!"CouplingLabelMissing: {id}, {refs.head!.1}"
  -- The couplings together must allow a complete choice (6.2).
  let constraints := couplings.map (fun c =>
    ((c.getObjValD "axis").getStr?.toOption.getD "",
     match c.getObjValD "sets" with
     | .arr xs => xs.toList.filterMap (fun r => (r.getObjValD "set").getStr?.toOption)
     | _ => []))
  let axes := (constraints.map (·.1)).eraseDups
  let names := (constraints.flatMap (·.2)).eraseDups
  let vars := names.map (fun name =>
    let labels := match sets.find? (fun s => s.getObjValD "id" == .str name &&
        (s.getObjValD "version").getNat?.toOption == activeVersion sets name) with
      | some s => match s.getObjValD "labels" with
        | .arr ls => ls.toList
        | _ => []
      | none => []
    (name, (labels.map (fun l => Json.mkObj (axes.map (fun a => (a, l.getObjValD a))))).eraseDups))
  unless jointlySatisfiable constraints vars [] do
    throw s!"CouplingUnsatisfiable: {String.intercalate ", " (VE.Route.sortStrings ids)}"
  return ids

def selectedValue (document : Json) (report : VE.Graph.Report) (set : String)
    (version : Nat) (axis : String) : Option String := Id.run do
  let sets := match document.getObjValD "reading_sets" with
    | .arr xs => xs.toList
    | _ => []
  let values := labelValues sets (set, version) axis
  for claim in report.assumptions do
    match parseLabel claim.label with
    | some (.readings name v (some i)) =>
      if name == set && v == version then return values[i]?
    | some (.readings name v none) =>
      if name == set && v == version && values.eraseDups.length == 1 then
        return values.head?
    | _ => pure ()
  return none

def CouplingChoicesCompatible (document : Json) (report : VE.Graph.Report) : Bool := Id.run do
  let couplings := match document.getObjValD "couplings" with
    | .arr xs => xs.toList
    | _ => []
  let sets := match document.getObjValD "reading_sets" with
    | .arr xs => xs.toList
    | _ => []
  for c in couplings do
    let axis := (c.getObjValD "axis").getStr?.toOption.getD ""
    let refs : List (String × Nat) := match c.getObjValD "sets" with
      | .arr xs => xs.toList.filterMap (fun (r : Json) =>
          match (r.getObjValD "set").getStr?.toOption,
                (r.getObjValD "version").getNat?.toOption with
          | some name, some version => some (name, version)
          | _, _ => none)
      | _ => []
    let mut members := refs.map (·.1)
    for _ in [:couplings.length] do
      for other in couplings do
        if other.getObjValD "axis" == .str axis then
          let os := match other.getObjValD "sets" with
            | .arr xs => xs.toList.filterMap (fun r => (r.getObjValD "set").getStr?.toOption)
            | _ => []
          if os.any members.contains then members := (members ++ os).eraseDups
    let componentRefs := sets.filterMap (fun s =>
      let name := (s.getObjValD "id").getStr?.toOption.getD ""
      if members.contains name then
        (s.getObjValD "version").getNat?.toOption.map (name, ·)
      else none)
    let values := componentRefs.filterMap (fun ref => selectedValue document report ref.1 ref.2 axis)
    if values.eraseDups.length > 1 then return false
    if report.assumptions.any (fun claim => claim.label == "coupling:" ++
        ((c.getObjValD "id").getStr?.toOption.getD "")) &&
        !(refs.all (fun ref => (selectedValue document report ref.1 ref.2 axis).isSome)) then
      return false
  return true

structure Admitted where
  src : RightsSource
  doc : VE.Route.Admission.Doc
  prime : Json
  graphJson : Json
  nodes : Array Json
  decoded : List (WireNode × Json)
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
  kinds : List Json
  couplingIds : List String

def decodeRightsDoc (src : RightsSource) (document : Json) : Except String VE.Route.Admission.Doc := do
  let E := envPrime (correlate src.D)
  let data := src.re.profiles.contains "data@0"
  let units ← (← (← document.getObjVal? "units").getArr?).toList.mapM (decodeUnit E data)
  require (units.length ≤ 10000) "ResourceLimit: unit count"
  require ((units.map DocUnit.id).eraseDups.length == units.length) "duplicate unit id"
  require (sortedSpans units) "unit spans must be sorted and non-overlapping"
  let optional := fun (key : String) => match document.getObjVal? key with
    | .ok v => v.getArr?.map Array.toList
    | .error _ => pure []
  let lemmas ← (← optional "lemmas").mapM (decodeLemma E data)
  require ((lemmas.map Lemma.name).eraseDups.length == lemmas.length) "duplicate lemma"
  let openTerms ← tokens (Json.arr (← optional "open_terms").toArray)
  let readingSets ← (← optional "reading_sets").mapM fun j => do
    let fields ← VE.Bridge.fields j
    decodeReadingSet E data (Json.mkObj (fields.filter (·.1 != "labels")))
  require ((readingSets.map (fun r => (r.id, r.version))).eraseDups.length == readingSets.length)
    "duplicate reading set version"
  let narrowings ← tokens (Json.arr (← optional "narrowings").toArray)
  return ⟨src.re.se.ne.rv.literals, src.re.se.ne.rv.flags, units, lemmas, openTerms,
    readingSets, narrowings⟩

def LayerLeaf (src : RightsSource) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    ((syms (soften (correlate src.D)).T).filterMap
      (fun | .reg r => some r | .defn _ => none)).any
      (fun r => decide (w.claim.label = "layer:norms:" ++ r.name ∧
        w.claim.formula = elabPremise (soften (correlate src.D)).T r))) = true

def ProfileLeaf (src : RightsSource) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone && w.claim.label == "background:profile" &&
    (pairPremises (soften (correlate src.D)).T).any (fun a => decide (w.claim.formula = a))) = true

def SoftLeaf (src : RightsSource) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    (VE.SoftNorms.Wire.softLabelled (correlate src.D)).any
      (fun (l, a) => decide (w.claim.label = l ∧ w.claim.formula = a))) = true

def RightsLeaf (src : RightsSource) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    (limPremisesLabelled src.D).any
      (fun (l, a) => decide (w.claim.label = l ∧ w.claim.formula = a))) = true

def CouplingLeaf (ids : List String) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone && w.claim.formula == .top &&
    ids.any (fun id => w.claim.label == "coupling:" ++ id)) = true

instance (src : RightsSource) (w : WireNode) : Decidable (ProfileLeaf src w) := by
  unfold ProfileLeaf; infer_instance
instance (src : RightsSource) (w : WireNode) : Decidable (LayerLeaf src w) := by
  unfold LayerLeaf; infer_instance
instance (src : RightsSource) (w : WireNode) : Decidable (SoftLeaf src w) := by
  unfold SoftLeaf; infer_instance
instance (src : RightsSource) (w : WireNode) : Decidable (RightsLeaf src w) := by
  unfold RightsLeaf; infer_instance
instance (ids : List String) (w : WireNode) : Decidable (CouplingLeaf ids w) := by
  unfold CouplingLeaf; infer_instance

def NodeAdmitted (src : RightsSource) (D : VE.Route.Admission.Doc)
    (ids : List String) (w : WireNode) : Prop :=
  VE.Route.Admission.NodeAdmitted D w ∨ LayerLeaf src w ∨ ProfileLeaf src w ∨
    SoftLeaf src w ∨ RightsLeaf src w ∨ CouplingLeaf ids w

instance (src : RightsSource) (D : VE.Route.Admission.Doc) (ids : List String)
    (w : WireNode) : Decidable (NodeAdmitted src D ids w) := by
  unfold NodeAdmitted; infer_instance

def admitNodes (src : RightsSource) (D : VE.Route.Admission.Doc) (ids : List String)
    (ws : List WireNode) :
    Except String Unit :=
  match ws.find? (fun w => !decide (NodeAdmitted src D ids w)) with
  | some w => .error (nodeDiagnostic D w)
  | none => .ok ()

theorem admitNodes_ok (src : RightsSource) (D : VE.Route.Admission.Doc) (ids : List String)
    (ws : List WireNode) (h : admitNodes src D ids ws = .ok ()) :
    ∀ w ∈ ws, NodeAdmitted src D ids w := by
  unfold admitNodes at h
  split at h
  · cases h
  · rename_i hf
    intro w hw
    have := List.find?_eq_none.mp hf w hw
    simpa using this

def admitDocument (environment document : Json) : Except String Admitted := do
  VE.Bridge.displayFields document ["units", "graph"]
    ["lemmas", "open_terms", "reading_sets", "narrowings", "couplings"]
  checkSourceCites document
  let couplingIds ← validateCouplings document
  let (clean, active) ← splitDocument document
  let src ← decodeRightsSource environment active
  let D ← decodeRightsDoc src clean
  let graphJson ← document.getObjVal? "graph"
  VE.Bridge.exactFields graphJson ["root", "nodes"]
  let root ← VE.Bridge.stringField graphJson "root"
  let nodes ← (← graphJson.getObjVal? "nodes").getArr?
  require (nodes.size ≤ 1000) "ResourceLimit: graph node count"
  let E := envPrime (correlate src.D)
  let decoded ← nodes.toList.mapM (decodeNode E (src.re.profiles.contains "data@0"))
  let prime ← primeJsonR src.D environment
  VE.Norms.Admission.checkBindings src.re.profiles prime decoded
  let wires := decoded.map Prod.fst
  admitNodes src D couplingIds wires
  let graph : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  let report ← checkGraph E graph
  require (decide (CitationsClosed D report))
    "AdmissionError: a cited lemma's leaves are missing from the report"
  require (decide (ChoicesCompatible report))
    "AdmissionError: incompatible reading choices"
  require (CouplingChoicesCompatible document report)
    "AdmissionError: incompatible coupled reading choices"
  let originalUnits := (← (← document.getObjVal? "units").getArr?).toList
  return ⟨src, D, prime, graphJson, nodes, decoded, wires, graph, report,
    originalUnits.map (·.getObjValD "kind"), couplingIds⟩

open VE.Order.ProfileGate (bind_ok) in
theorem admitDocument_spec (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) :
    WellFormedRights res.src.D = true ∧
    primeJsonR res.src.D environment = .ok res.prime ∧
    VE.Norms.Admission.checkBindings res.src.re.profiles res.prime res.decoded = .ok () ∧
    VE.Graph.SoundReport.{0} (envPrime (correlate res.src.D)) res.graph res.report ∧
    (∀ w ∈ res.wires, NodeAdmitted res.src res.doc res.couplingIds w) ∧
    CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report ∧
    CouplingChoicesCompatible document res.report = true := by
  unfold admitDocument at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨couplingIds, _, h⟩ := bind_ok h
  obtain ⟨⟨clean, active⟩, _, h⟩ := bind_ok h
  obtain ⟨src, _, h⟩ := bind_ok h
  obtain ⟨D, _, h⟩ := bind_ok h
  obtain ⟨graphJson, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨root, _, h⟩ := bind_ok h
  obtain ⟨nodesJson, _, h⟩ := bind_ok h
  obtain ⟨nodes, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨decoded, _, h⟩ := bind_ok h
  obtain ⟨prime, hprime, h⟩ := bind_ok h
  obtain ⟨_, hbound, h⟩ := bind_ok h
  obtain ⟨_, hadmitted, h⟩ := bind_ok h
  obtain ⟨report, hreport, h⟩ := bind_ok h
  obtain ⟨_, hcites, h⟩ := bind_ok h
  obtain ⟨_, hchoices, h⟩ := bind_ok h
  obtain ⟨_, hcoupling, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  obtain ⟨_, _, _, hsound⟩ := VE.Graph.check_sound.{0} (envPrime (correlate src.D)) _ report
    (checkGraph_ok _ _ report hreport)
  exact ⟨src.wf, hprime, hbound, hsound,
    admitNodes_ok src D couplingIds (decoded.map Prod.fst) hadmitted,
    of_decide_eq_true (VE.Route.Gate.require_ok hcites),
    of_decide_eq_true (VE.Route.Gate.require_ok hchoices),
    VE.Route.Gate.require_ok hcoupling⟩

def otherAssumptions (res : Admitted) : List VE.Graph.Claim :=
  res.report.assumptions.filter (fun c =>
    !decide (∃ w ∈ res.wires, w.claim = c ∧
      (LayerLeaf res.src w ∨ ProfileLeaf res.src w ∨
        SoftLeaf res.src w ∨ RightsLeaf res.src w)))

theorem layerLeaf_formula (src : RightsSource) (w : WireNode) (h : LayerLeaf src w) :
    w.claim.formula ∈ elaborate (soften (correlate src.D)).T := by
  simp only [LayerLeaf, Bool.and_eq_true] at h
  obtain ⟨r, hr, he⟩ := List.any_eq_true.mp h.2
  have heq : w.claim.label = "layer:norms:" ++ r.name ∧
      w.claim.formula = elabPremise (soften (correlate src.D)).T r := of_decide_eq_true he
  rw [heq.2]
  change elabPremise (soften (correlate src.D)).T r ∈
    (syms (soften (correlate src.D)).T).filterMap
      (fun | .reg r => some (elabPremise (soften (correlate src.D)).T r) | .defn _ => none)
  obtain ⟨q, hq, hqr⟩ := List.mem_filterMap.mp
    (show r ∈ (syms (soften (correlate src.D)).T).filterMap
      (fun | .reg r => some r | .defn _ => none) from hr)
  cases q with
  | reg r' =>
    simp only [Option.some.injEq] at hqr
    subst hqr
    exact List.mem_filterMap.mpr ⟨.reg r', hq, rfl⟩
  | defn d => cases hqr

theorem softLeaf_formula (src : RightsSource) (w : WireNode) (h : SoftLeaf src w) :
    w.claim.formula ∈ VE.SoftNorms.softPremises (correlate src.D) := by
  simp only [SoftLeaf, Bool.and_eq_true] at h
  obtain ⟨⟨l, a⟩, hm, he⟩ := List.any_eq_true.mp h.2
  have heq : w.claim.label = l ∧ w.claim.formula = a := of_decide_eq_true he
  rw [heq.2]
  simp only [VE.SoftNorms.Wire.softLabelled, List.mem_append, List.mem_map] at hm
  rcases hm with hm | ⟨⟨M, N⟩, hc, he'⟩
  · exact List.mem_append_left _ (List.of_mem_zip hm).2
  · simp only [Prod.mk.injEq] at he'
    rw [← he'.2]
    exact List.mem_append_right _ (List.mem_map.mpr ⟨(M, N), hc, rfl⟩)

theorem rightsLeaf_formula (src : RightsSource) (w : WireNode) (h : RightsLeaf src w) :
    w.claim.formula ∈ limPremises src.D := by
  simp only [RightsLeaf, Bool.and_eq_true] at h
  obtain ⟨⟨l, a⟩, hm, he⟩ := List.any_eq_true.mp h.2
  have heq : w.claim.label = l ∧ w.claim.formula = a := of_decide_eq_true he
  rw [heq.2]
  exact List.mem_map.mpr ⟨(l, a), hm, rfl⟩

theorem rights_wire_report_consequence (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) (S : VE.Structure.{0})
    (hS : S.Admissible (envPrime (correlate res.src.D)))
    (hregen : Sat S (backgroundR res.src.D ++ elaborate (soften (correlate res.src.D)).T))
    (hother : Sat S ((otherAssumptions res).map (·.formula))) :
    res.report.root.formula.denote S [] := by
  obtain ⟨_, _, _, hsound, _, _, _⟩ := admitDocument_spec environment document res h
  apply hsound.2.2.2.1 S hS
  intro a ha
  obtain ⟨leaf, hl, rfl⟩ := List.mem_map.mp ha
  by_cases hgenerated : ∃ w ∈ res.wires, w.claim = leaf ∧
      (LayerLeaf res.src w ∨ ProfileLeaf res.src w ∨
       SoftLeaf res.src w ∨ RightsLeaf res.src w)
  · obtain ⟨w, _, hwl, hw⟩ := hgenerated
    rw [← hwl]
    rcases hw with hw | hw | hw | hw
    · exact hregen _ (List.mem_append_right _ (layerLeaf_formula res.src w hw))
    · simp only [ProfileLeaf, Bool.and_eq_true] at hw
      obtain ⟨a, ha, hfa⟩ := List.any_eq_true.mp hw.2
      rw [of_decide_eq_true hfa]
      apply hregen
      apply List.mem_append_left
      unfold backgroundR VE.SoftNorms.background'
      exact List.mem_append_left _ (List.mem_append_left _ (List.mem_append_right _ ha))
    · apply hregen
      apply List.mem_append_left
      unfold backgroundR VE.SoftNorms.background'
      exact List.mem_append_left _ (List.mem_append_right _ (softLeaf_formula res.src w hw))
    · exact hregen _ (List.mem_append_left _ (by
        unfold backgroundR
        exact List.mem_append_right _ (rightsLeaf_formula res.src w hw)))
  · apply hother
    apply List.mem_map_of_mem
    simp only [otherAssumptions, List.mem_filter]
    exact ⟨hl, by simp [hgenerated]⟩

end VE.Rights.Admission
