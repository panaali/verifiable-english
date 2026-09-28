import VE.Discourse.Admission

/-! # The admission theorems (docs/spec/discourse.md 9.3, 9.4, 9.6)

Every statement is about a successful `admitDiscourse` on raw JSON. `admit_cases` splits the
result into the `@1` delegation (`lift1` of W2's admission) and the `@2` path, whose facts
(`Admit2Facts`, `PostFacts`) are read off the ordered checks of `admit2`: the profile adapter,
well-formedness, the W2 admission of the projection on the base pair, the post-admission table
checks, the composition gate and the second-phase validity verdicts. -/
namespace VE.Discourse
universe u
open Lean
open VE.Order.ProfileGate (bind_ok)
open VE.Route.Admission (parseLabel AssertedUnit)

/-- Everything a successful `admit2` establishes about its result. -/
structure Admit2Facts (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (check : ByteArray → ImportOutcome) (res : Admitted) : Prop where
  wrapper : wrapperOk profiles environment j = .ok ()
  wf : wellFormed res.doc = .ok ()
  base : VE.Route.Admission.admitDocument (baseProfiles profiles) (baseEnvironment environment) rv res.projected = .ok res.base
  premises : res.premiseUnits = premiseUnitsOf res.base
  pending : res.pending = pendingIn res.doc res.base.wires res.base.doc res.premiseUnits
  post : postOk res.doc res.base res.bound = .ok ()
  bound : ∀ u, res.bound u ≠ none → (res.pending.map Prod.fst).contains u = false ∧
    res.bound u = (if (boundUnits res.doc).contains u then (validate res.doc u).toOption else none)
  boundPending : ∀ u, (res.pending.map Prod.fst).contains u = true → res.bound u = none
  joint : res.joint = compatibleChoices res.doc.K (activeSets res.doc) 64
  gate : ∀ cs, res.joint = .ok cs → gateOk res.base cs = .ok ()
  presuppositions : res.presuppositions = fun id =>
    ((presupMentions res.doc).find? (·.id == id)).bind (carrierIn res.doc res.base.wires res.base.doc res.premiseUnits)
  validity : res.validity = fun u => (res.doc.K.validity.find? (·.unit == u)).bind
    (verdictFor res.doc (Wire.prose j) check)
  selfTruth : res.selfTruth = res.doc.K.selfTruth
  documentId : Wire.documentId2 (Wire.frontMatter j) (Wire.prose j) (Wire.fences j) = .ok res.documentId
  env : res.doc.E = rv.environment

theorem admit2_facts (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (check : ByteArray → ImportOutcome) (res : Admitted) (h : admit2 profiles environment rv j check = .ok res) :
    Admit2Facts profiles environment rv j check res := by
  unfold admit2 at h
  obtain ⟨_, hw, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨prose, hprose, h⟩ := bind_ok h
  obtain ⟨dj, hdj, h⟩ := bind_ok h
  obtain ⟨K₀, hK₀, h⟩ := bind_ok h
  obtain ⟨base₀, hb₀, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, _, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨K, hK, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨envId, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, hwf, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, _, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨b, hb, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, hpost, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, hgate, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨docId, hdoc, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, _, h⟩ := bind_ok h
  simp only [pure, Except.pure, Except.ok.injEq] at h
  subst h
  refine ⟨hw, hwf, hb, rfl, rfl, hpost, ?_, ?_, rfl, ?_, rfl, rfl, rfl, hdoc, rfl⟩
  · intro u hu
    simp only at hu ⊢
    split at hu
    · exact absurd rfl hu
    · rename_i hc
      simp only [Bool.or_eq_true, not_or, Bool.not_eq_true] at hc
      refine ⟨hc.1, ?_⟩
      simp only [hc.1, hc.2, Bool.false_or, Bool.false_eq_true, if_false]
  · intro u hu
    dsimp only
    split
    · rfl
    · rename_i hc
      exfalso
      apply hc
      simp only [Bool.or_eq_true]
      exact Or.inl hu
  · intro cs hcs
    simp only at hcs
    rw [hcs] at hgate
    exact hgate

/-! ## The two paths of `admitDiscourse` -/

theorem admitAt_cases (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (check : Option (ByteArray → ImportOutcome)) (res : Admitted)
    (h : admitAt profiles environment rv j check = .ok res) :
    ((formatOf j == some "ve-document@1" || formatOf j == none) = true ∧
      ∃ r, VE.Route.Admission.admitDocument profiles environment rv j = .ok r ∧ res = lift1 r) ∨
    (formatOf j = some "ve-document@2" ∧ ∃ K₀ c, Wire.decodeManifest (j.getObjValD "discourse") = .ok K₀ ∧
      integrityOk j K₀ = .ok () ∧ check = some c ∧ admit2 profiles environment rv j c = .ok res) := by
  unfold admitAt at h
  split at h
  · split at h
    · cases h
    · cases hr : VE.Route.Admission.admitDocument profiles environment rv j with
      | error e => rw [hr] at h; cases h
      | ok r =>
        rw [hr] at h
        simp only [Except.map, Except.ok.injEq] at h
        rename_i h1 _
        exact Or.inl ⟨h1, r, rfl, h.symm⟩
  · rename_i h1
    split at h
    · cases h
    · rename_i h2
      simp only [bne_iff_ne, ne_eq, Decidable.not_not, beq_iff_eq] at h2
      split at h
      · cases h
      · rename_i K₀ hK
        split at h
        · cases h
        · rename_i v hi
          split at h
          · cases h
          · rename_i c
            exact Or.inr ⟨h2, K₀, c, hK, by cases v; exact hi, rfl, h⟩

theorem admit_cases (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res) :
    ((formatOf j == some "ve-document@1" || formatOf j == none) = true ∧
      ∃ r, VE.Route.Admission.admitDocument profiles environment rv j = .ok r ∧ res = lift1 r) ∨
    (formatOf j = some "ve-document@2" ∧ ∃ K₀ n, fuel = n + 1 ∧ Wire.decodeManifest (j.getObjValD "discourse") = .ok K₀ ∧
      integrityOk j K₀ = .ok () ∧ admit2 profiles environment rv j (fun b => checkImport profiles b n) = .ok res) := by
  cases fuel with
  | zero =>
    rcases admitAt_cases profiles environment rv j none res h with h | ⟨_, _, _, _, _, hc, _⟩
    · exact Or.inl h
    · cases hc
  | succ n =>
    rcases admitAt_cases profiles environment rv j _ res h with h | ⟨h2, K₀, c, hK, hi, hc, ha⟩
    · exact Or.inl h
    · cases hc
      exact Or.inr ⟨h2, K₀, n, rfl, hK, hi, ha⟩

/-! ## 9.6: the `@1` path and the profile adapter -/

theorem formatOf_of (j : Json) (s : String) (h : (j.getObjValD "format").getStr? = .ok s) : formatOf j = some s := by
  simp [formatOf, h, Except.toOption]

/-- The `@1` path is delegated unchanged when the profile is off. -/
theorem format1_unchanged (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (h1 : (j.getObjValD "format").getStr? = .ok "ve-document@1") (hp : "ve.discourse@1" ∉ profiles) :
    admitDiscourse profiles environment rv j fuel = (VE.Route.Admission.admitDocument profiles environment rv j).map lift1 := by
  have hf := formatOf_of j _ h1
  cases fuel <;> simp [admitDiscourse, admitAt, hf, discourseProfile, hp]

/-- With the profile on, a `@1` document is the profile-gate error, never a silent delegation. -/
theorem format1_profile_requires_format2 (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (h1 : (j.getObjValD "format").getStr? = .ok "ve-document@1") (hp : "ve.discourse@1" ∈ profiles) :
    admitDiscourse profiles environment rv j fuel = .error "UnsupportedProfile: ve.discourse@1 requires ve-document@2" := by
  have hf := formatOf_of j _ h1
  cases fuel <;> simp [admitDiscourse, admitAt, hf, discourseProfile, hp]

/-- 3.5: the frozen gate runs on the base pair, and its verdict on the base list is unchanged. -/
theorem profile_adapter_base (profiles : List String) (environment : Json) (j : Json)
    (hw : wrapperOk profiles environment j = .ok ()) :
    VE.Route.Gate.profilesOf (baseEnvironment environment) = .ok (baseProfiles profiles) ∧
    "ve.discourse@1" ∉ baseProfiles profiles ∧
    (VE.Route.Gate.decodeEnvelope (baseEnvironment environment)).map VE.Route.Gate.Envelope.family =
      VE.Route.Gate.classify (baseProfiles profiles) := by
  unfold wrapperOk at hw
  simp only [runAll_cons, runAll_nil, and_true] at hw
  obtain ⟨_, _, _, _, _, h6, h7⟩ := hw
  have hp : VE.Route.Gate.profilesOf (baseEnvironment environment) = .ok (baseProfiles profiles) := by
    cases hq : VE.Route.Gate.profilesOf (baseEnvironment environment) with
    | error e => rw [hq] at h6; simp [req] at h6
    | ok ps =>
      rw [hq] at h6
      simp only [req_ok, beq_iff_eq] at h6
      rw [h6]
  refine ⟨hp, by simp [baseProfiles], ?_⟩
  cases he : VE.Route.Gate.decodeEnvelope (baseEnvironment environment) with
  | error e => rw [he] at h7; cases h7
  | ok e =>
    obtain ⟨_, hpe, ha⟩ := VE.Route.Gate.decodeEnvelope_sound _ e he
    rw [hp] at hpe
    have hpe' := Except.ok.inj hpe
    rw [hpe'] at *
    simp only [Except.map]
    exact (VE.Route.Gate.classify_complete _ _ ha).symm

/-- The `@2` admission is W2's admission of the projected document under the base pair, plus the
discourse checks. -/
theorem admission_projects (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted)
    (h2 : (j.getObjValD "format").getStr? = .ok "ve-document@2")
    (h : admitDiscourse profiles environment rv j fuel = .ok res) :
    VE.Route.Admission.admitDocument (baseProfiles profiles) (baseEnvironment environment) rv res.projected = .ok res.base ∧
    WellFormedDiscourse res.doc = true ∧
    (∀ u A, res.bound u = some A → validate res.doc u = .ok A) ∧
    Wire.documentId2 (Wire.frontMatter j) (Wire.prose j) (Wire.fences j) = .ok res.documentId := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨hfm, _⟩ | ⟨_, K₀, n, _, _, _, ha⟩
  · have hf := formatOf_of j _ h2
    rw [hf] at hfm
    simp at hfm
  · have F := admit2_facts profiles environment rv j _ res ha
    refine ⟨F.base, by simp [WellFormedDiscourse, F.wf, Except.toBool], fun u A hA => ?_, F.documentId⟩
    obtain ⟨_, hb⟩ := F.bound u (by rw [hA]; simp)
    rw [hA] at hb
    split at hb
    · cases hv : validate res.doc u with
      | ok A' => rw [hv] at hb; simp [Except.toOption] at hb; rw [hb]
      | error e => rw [hv] at hb; simp [Except.toOption] at hb
    · cases hb


/-! ## Post-admission facts -/

theorem dup_nodup {xs : List String} {f : String → String}
    (h : (match dupOf xs with | some a => (Except.error (f a) : Except String Unit) | none => .ok ()) = .ok ()) :
    xs.Nodup := by
  cases hd : dupOf xs with
  | none => exact dupOf_none xs hd
  | some a => rw [hd] at h; cases h

structure PostFacts (D : DDoc) (b : VE.Route.Admission.Admitted) (bound : String → Option VE.Formula) : Prop where
  groupedNodup : (D.K.groups.flatMap Group.spans).Nodup
  groups : ∀ g ∈ D.K.groups,
    (b.doc.readingSets.any fun rs => rs.id == g.set && rs.version == g.version &&
        (groupFormula D g).any fun φ => rs.readings[g.reading]? == some φ) = true ∧
    (b.report.assumptions.filter fun l => setOfLabel l.label = some (g.set, g.version)).length ≤ 1 ∧
    ∀ u ∈ g.spans, ((unitOf b.doc u).bind VE.Route.Admission.DocUnit.content == none && (bound u).isNone &&
        !(premiseUnitsOf b).contains u &&
        (b.report.assumptions.all fun l => l.label != "asserted" || unitOfLeaf b l != some u)) = true
  validity : ∀ v ∈ D.K.validity, (!(premiseUnitsOf b).contains v.unit && (bound v.unit).isNone) = true
  selfTruth : ∀ u ∈ D.K.selfTruth, (!(premiseUnitsOf b).contains u && (bound u).isNone &&
      (unitOf D.base u).bind VE.Route.Admission.DocUnit.content == none) = true
  validityNodup : (D.K.validity.map Validity.unit).Nodup
  documentsNodup : (D.K.documents.map DocName.name).Nodup
  mentionsNodup : (D.K.mentions.map Mention.id).Nodup
  importsNodup : (D.K.imports.map Import.key).Nodup
  groupedLabels : ∀ u ∈ D.K.groups.flatMap Group.spans,
    (!D.K.selfTruth.contains u && !(D.K.validity.map Validity.unit).contains u) = true

theorem postOk_facts (D : DDoc) (b : VE.Route.Admission.Admitted) (bound : String → Option VE.Formula)
    (h : postOk D b bound = .ok ()) : PostFacts D b bound := by
  unfold postOk at h
  simp only [runAll_cons, runAll_nil, and_true] at h
  obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩ := h
  refine ⟨dup_nodup h1, fun g hg => ?_, fun v hv => ?_, fun u hu => ?_, dup_nodup h5, dup_nodup h6,
    dup_nodup h7, dup_nodup h8, fun u hu => ?_⟩
  · have hg' := (allOk_iff _ _).mp h2 g hg
    simp only [runAll_cons, runAll_nil, and_true, req_ok, decide_eq_true_eq] at hg'
    obtain ⟨a, c, d⟩ := hg'
    exact ⟨a, c, fun u hu => (req_ok _ _).mp ((allOk_iff _ _).mp d u hu)⟩
  · exact (req_ok _ _).mp ((allOk_iff _ _).mp h3 v hv)
  · exact (req_ok _ _).mp ((allOk_iff _ _).mp h4 u hu)
  · exact (req_ok _ _).mp ((allOk_iff _ _).mp h9 u hu)

/-- A successful `@2` admission's facts, with its post-admission checks. -/
theorem admit_facts2 (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (check : ByteArray → ImportOutcome) (res : Admitted) (h : admit2 profiles environment rv j check = .ok res) :
    Admit2Facts profiles environment rv j check res ∧ PostFacts res.doc res.base res.bound := by
  have F := admit2_facts profiles environment rv j check res h
  exact ⟨F, postOk_facts _ _ _ F.post⟩

theorem find_key {α : Type} (key : α → String) : ∀ (xs : List α) (x : α), (xs.map key).Nodup → x ∈ xs →
    xs.find? (fun y => key y == key x) = some x
  | [], _, _, hx => nomatch hx
  | y :: ys, x, hn, hx => by
    rw [List.map_cons, List.nodup_cons] at hn
    rcases List.mem_cons.mp hx with rfl | hx
    · simp
    · have hne : key y ≠ key x := fun e => hn.1 (e ▸ List.mem_map_of_mem hx)
      have hb : (key y == key x) = false := by simpa using hne
      simp only [List.find?_cons, hb]
      exact find_key key ys x hn.2 hx

/-! ## 9.3: report soundness, labels and carriers -/

theorem lift1_base_sound (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (r : VE.Route.Admission.Admitted) (h : VE.Route.Admission.admitDocument profiles environment rv j = .ok r) :
    (lift1 r).base = r := rfl

/-- The W2 soundness statement transfers verbatim to the elaborated document (reused:
`admit_report_sound`). -/
theorem discourse_report_sound (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res) :
    VE.Graph.SoundReport.{u} rv.environment res.base.graph res.base.report ∧
    (∀ w ∈ res.base.wires, VE.Route.Admission.NodeAdmitted res.base.doc w) ∧
    VE.Route.Admission.CitationsClosed res.base.doc res.base.report ∧
    VE.Route.Admission.ChoicesCompatible res.base.report := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, r, hr, rfl⟩ | ⟨_, _, n, _, _, _, ha⟩
  · obtain ⟨_, _, _, _, _, _, _, hs, hn, _, hc, hch⟩ := VE.Route.Admission.admit_report_sound.{u} _ _ _ _ _ hr
    exact ⟨hs, hn, hc, hch⟩
  · obtain ⟨F, _⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨_, _, _, _, _, _, _, hs, hn, _, hc, hch⟩ := VE.Route.Admission.admit_report_sound.{u} _ _ _ _ _ F.base
    exact ⟨hs, hn, hc, hch⟩

/-- No `discourse:*` label exists in the report: every assumption carries a W2 label. -/
theorem no_discourse_label (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res) :
    ∀ leaf ∈ res.base.report.assumptions, (parseLabel leaf.label).isSome := by
  have key : ∀ (p : List String) (e : Json) (d : Json) (r : VE.Route.Admission.Admitted),
      VE.Route.Admission.admitDocument p e rv d = .ok r → ∀ leaf ∈ r.report.assumptions, (parseLabel leaf.label).isSome := by
    intro p e d r hr leaf hl
    obtain ⟨_, _, _, _, _, _, _, _, _, hleaf, _, _⟩ := VE.Route.Admission.admit_report_sound.{0} _ _ _ _ _ hr
    obtain ⟨w, _, hw, _, hadm⟩ := hleaf leaf hl
    unfold VE.Route.Admission.LeafAdmitted at hadm
    rw [← hw]
    split at hadm <;> first | simp_all | exact hadm.elim
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, r, hr, rfl⟩ | ⟨_, _, n, _, _, _, ha⟩
  · exact key _ _ _ r hr
  · exact key _ _ _ _ (admit2_facts profiles environment rv j _ res ha).base


theorem carrier_cases (D : DDoc) (wires : List VE.Route.Admission.WireNode) (doc : VE.Route.Admission.Doc)
    (premises : List String) (m : Mention) (Dr : VE.Formula) (hD : m.restriction = some Dr) (σ : String)
    (hσ : restrictionSort D m = some σ) :
    (∃ n w, carrierIn D wires doc premises m = some (.proved n) ∧ w ∈ wires ∧ w.claim.name = n ∧
      w.unit = none ∧ w.deduction.isSome ∧ w.claim.label = "asserted" ∧ w.claim.formula = uniqueD σ Dr) ∨
    (∃ u, carrierIn D wires doc premises m = some (.assumed u) ∧ m.presuppositionUnit = some u ∧
      AssertedUnit doc u (uniqueD σ Dr) ∧ u ∈ premises) ∨
    carrierIn D wires doc premises m = none := by
  unfold carrierIn
  rw [hD, hσ]
  simp only
  cases hw : wires.find? (fun w => w.unit.isNone && w.deduction.isSome && w.claim.label == "asserted" &&
      w.claim.formula == uniqueD σ Dr) with
  | some w =>
    have hp := List.find?_some hw
    simp only [Bool.and_eq_true, beq_iff_eq, Option.isNone_iff_eq_none] at hp
    exact Or.inl ⟨w.claim.name, w, rfl, List.mem_of_find?_eq_some hw, rfl, hp.1.1.1, hp.1.1.2, hp.1.2, hp.2⟩
  | none =>
    simp only
    cases hu : m.presuppositionUnit with
    | none => exact Or.inr (Or.inr rfl)
    | some u =>
      simp only
      split
      · rename_i hc
        simp only [Bool.and_eq_true, decide_eq_true_eq, List.contains_iff_mem] at hc
        exact Or.inr (Or.inl ⟨u, rfl, rfl, hc.1, hc.2⟩)
      · exact Or.inr (Or.inr rfl)

/-- The two carriers (4.5): in an admitted document every presuppositional mention's U(D) is
either a certified unit-less `asserted` deduction node or an explicit asserted unit named by
`presuppositionUnit`, and otherwise the unit is pending with the named diagnostic. -/
theorem presupposition_carried (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (m : Mention) (hm : m ∈ res.doc.K.mentions)
    (hr : m.reading = some .presuppositional) (Dr : VE.Formula) (hD : m.restriction = some Dr)
    (σ : String) (hσ : restrictionSort res.doc m = some σ) :
    (∃ n w, res.presuppositions m.id = some (.proved n) ∧ w ∈ res.base.wires ∧ w.claim.name = n ∧
       w.unit = none ∧ w.deduction.isSome ∧ w.claim.label = "asserted" ∧ w.claim.formula = uniqueD σ Dr) ∨
    (∃ u, res.presuppositions m.id = some (.assumed u) ∧ m.presuppositionUnit = some u ∧
       AssertedUnit res.base.doc u (uniqueD σ Dr) ∧ u ∈ res.premiseUnits) ∨
    (res.presuppositions m.id = none ∧ (m.unit, "PresuppositionUnresolved: " ++ m.id) ∈ res.pending ∧
       res.bound m.unit = none) := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, r, _, rfl⟩ | ⟨_, _, n, _, _, _, ha⟩
  · exact absurd hm (by simp [lift1, emptyManifest])
  · obtain ⟨F, P⟩ := admit_facts2 profiles environment rv j _ res ha
    have hmp : m ∈ presupMentions res.doc := List.mem_filter.mpr ⟨hm, by simp [hr]⟩
    have hnd : ((presupMentions res.doc).map Mention.id).Nodup :=
      P.mentionsNodup.sublist ((List.filter_sublist).map _)
    have hpres : res.presuppositions m.id = carrierIn res.doc res.base.wires res.base.doc res.premiseUnits m := by
      rw [F.presuppositions]
      simp only
      rw [find_key Mention.id _ m hnd hmp]
      rfl
    rw [hpres]
    rcases carrier_cases res.doc res.base.wires res.base.doc res.premiseUnits m Dr hD σ hσ with h1 | h1 | h1
    · exact Or.inl h1
    · exact Or.inr (Or.inl h1)
    · have hpend : (m.unit, "PresuppositionUnresolved: " ++ m.id) ∈ res.pending := by
        rw [F.pending]
        unfold pendingIn
        exact List.mem_filterMap.mpr ⟨m, hmp, by simp [h1]⟩
      refine Or.inr (Or.inr ⟨h1, hpend, F.boundPending _ ?_⟩)
      simp only [List.contains_iff_mem, List.mem_map]
      exact ⟨_, hpend, rfl⟩


theorem find_group : ∀ (gs : List Group) (g : Group) (u : String), (gs.flatMap Group.spans).Nodup → g ∈ gs →
    u ∈ g.spans → gs.find? (fun g' => g'.spans.contains u) = some g
  | [], _, _, _, hg, _ => nomatch hg
  | g₀ :: gs, g, u, hn, hg, hu => by
    rw [List.flatMap_cons, List.nodup_append] at hn
    rcases List.mem_cons.mp hg with rfl | hg
    · simp [hu]
    · have hnot : u ∉ g₀.spans := fun h₀ =>
        hn.2.2 u h₀ u (List.mem_flatMap.mpr ⟨g, hg, hu⟩) rfl
      have hb : g₀.spans.contains u = false := by simpa using hnot
      simp only [List.find?_cons, hb]
      exact find_group gs g u hn.2.1 hg hu

theorem statusOf_grouped (res : Admitted) (P : PostFacts res.doc res.base res.bound)
    (hv : res.validity = fun u => (res.doc.K.validity.find? (·.unit == u)).bind
      (verdictFor res.doc (Wire.prose j) check))
    (hs : res.selfTruth = res.doc.K.selfTruth)
    (g : Group) (hg : g ∈ res.doc.K.groups) (u : String) (hu : u ∈ g.spans) :
    statusOf res u = groupStatus res.doc g := by
  have hin : u ∈ res.doc.K.groups.flatMap Group.spans := List.mem_flatMap.mpr ⟨g, hg, hu⟩
  have hl := P.groupedLabels u hin
  simp only [Bool.and_eq_true, Bool.not_eq_true', List.contains_iff_mem] at hl
  unfold statusOf
  have h1 : res.selfTruth.contains u = false := by rw [hs]; simpa using hl.1
  have h2 : res.validity u = none := by
    rw [hv]
    simp only
    have : res.doc.K.validity.find? (·.unit == u) = none := by
      apply List.find?_eq_none.mpr
      intro v hv' he
      simp only [beq_iff_eq] at he
      exact absurd (List.mem_map.mpr ⟨v, hv', he⟩) (by simpa using hl.2)
    rw [this]; rfl
  simp only [h1, Bool.false_eq_true, if_false, h2]
  unfold groupOf
  rw [find_group _ g u P.groupedNodup hg hu]

/-- 4.6: a group's reading is one formula regenerated per group; at most one leaf carries the
owning set; every span has the owning set's status, no content, no bound formula and is no
premise unit. -/
theorem group_single_assertion (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (g : Group) (hg : g ∈ res.doc.K.groups) :
    (∃ rs ∈ res.base.doc.readingSets, rs.id = g.set ∧ rs.version = g.version ∧
       ∃ φ, groupFormula res.doc g = some φ ∧ rs.readings[g.reading]? = some φ) ∧
    owningUnit res.doc g = g.spans.head? ∧
    (res.base.report.assumptions.filter (fun l => setOfLabel l.label = some (g.set, g.version))).length ≤ 1 ∧
    (∀ l ∈ res.base.report.assumptions, l.label = "asserted" → ∀ u ∈ g.spans, unitOfLeaf res.base l ≠ some u) ∧
    ∀ u ∈ g.spans, (unitOf res.base.doc u).bind VE.Route.Admission.DocUnit.content = none ∧ res.bound u = none ∧
      u ∉ res.premiseUnits ∧ statusOf res u = statusOf res (g.spans.head!) := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, r, _, rfl⟩ | ⟨_, _, n, _, _, _, ha⟩
  · exact absurd hg (by simp [lift1, emptyManifest])
  · obtain ⟨F, P⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨hrs, hcount, hspans⟩ := P.groups g hg
    refine ⟨?_, rfl, hcount, ?_, fun u hu => ?_⟩
    · obtain ⟨rs, hrs, hc⟩ := List.any_eq_true.mp hrs
      simp only [Bool.and_eq_true, beq_iff_eq, Option.any_eq_true] at hc
      obtain ⟨⟨hid, hv⟩, φ, hφ, hr⟩ := hc
      exact ⟨rs, hrs, hid, hv, φ, hφ, by simpa using hr⟩
    · intro l hl hlab u hu
      have := hspans u hu
      simp only [Bool.and_eq_true, List.all_eq_true, Bool.or_eq_true, bne_iff_ne, ne_eq] at this
      rcases this.2 l hl with h' | h'
      · exact absurd hlab h'
      · exact h'
    · have hx := hspans u hu
      simp only [Bool.and_eq_true, beq_iff_eq, Option.isNone_iff_eq_none, Bool.not_eq_true',
        List.contains_iff_mem] at hx
      obtain ⟨⟨⟨hc, hb⟩, hp⟩, _⟩ := hx
      have hhead : g.spans.head! ∈ g.spans := by
        cases hsp : g.spans with
        | nil => rw [hsp] at hu; cases hu
        | cons x xs => exact List.mem_cons_self
      refine ⟨hc, hb, by rw [F.premises]; simpa using hp, ?_⟩
      rw [statusOf_grouped res P F.validity F.selfTruth g hg u hu,
        statusOf_grouped res P F.validity F.selfTruth g hg _ hhead]

/-! ## 9.4: the composition gate -/

theorem gate_facts {b : VE.Route.Admission.Admitted} {cs : List Choice} (h : gateOk b cs = .ok ()) :
    (∀ L ∈ b.doc.lemmas, ∀ ch, VE.Definitions.Bundle.leafChoices (leafList L) = .ok ch → ∃ c ∈ cs, ExtendsTo ch c) ∧
    (∀ ch, VE.Definitions.Bundle.leafChoices (reportLeaves b.report) = .ok ch → ∃ c ∈ cs, ExtendsTo ch c) := by
  unfold gateOk at h
  simp only [runAll_cons, runAll_nil, and_true] at h
  obtain ⟨h1, h2⟩ := h
  constructor
  · intro L hL ch hch
    have := (allOk_iff _ _).mp h1 L hL
    rw [hch] at this
    obtain ⟨c, hc, he⟩ := List.any_eq_true.mp ((req_ok _ _).mp this)
    exact ⟨c, hc, (extendsTo_iff ch c).mp he⟩
  · intro ch hch
    rw [hch] at h2
    obtain ⟨c, hc, he⟩ := List.any_eq_true.mp ((req_ok _ _).mp h2)
    exact ⟨c, hc, (extendsTo_iff ch c).mp he⟩

/-- 4.8, the composition gate: each lemma's transitive choices extend to a validated compatible
choice (W2 lemma leaves, as label and formula). -/
theorem citation_extends_joint (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (cs : List Choice) (hcs : res.joint = .ok cs)
    (L : VE.Route.Admission.Lemma) (hL : L ∈ res.base.doc.lemmas) (ch : List (String × String))
    (hch : VE.Definitions.Bundle.leafChoices (leafList L) = .ok ch) :
    ∃ c ∈ cs, ExtendsTo ch c := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, r, _, rfl⟩ | ⟨_, _, n, _, _, _, ha⟩
  · cases hcs
  · obtain ⟨F, _⟩ := admit_facts2 profiles environment rv j _ res ha
    exact (gate_facts (F.gate cs hcs)).1 L hL ch hch

/-- The merged transitive assumptions of the reported graph result extend to a validated
compatible choice. -/
theorem report_extends_joint (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (cs : List Choice) (hcs : res.joint = .ok cs)
    (ch : List (String × String))
    (hch : VE.Definitions.Bundle.leafChoices (res.base.report.assumptions.map (fun l => (l.label, l.formula))) = .ok ch) :
    ∃ c ∈ cs, ExtendsTo ch c := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, r, _, rfl⟩ | ⟨_, _, n, _, _, _, ha⟩
  · cases hcs
  · obtain ⟨F, _⟩ := admit_facts2 profiles environment rv j _ res ha
    exact (gate_facts (F.gate cs hcs)).2 ch hch

/-- The per-lemma verdicts that depend on reading choices: UNKNOWN when the joint set is. -/
def readingVerdicts (res : Admitted) : List (String × String) :=
  match res.joint with
  | .error e => if e.startsWith "ResourceLimit" then res.base.doc.lemmas.map fun L => (L.name, "UNKNOWN (joint choices)")
    else []
  | .ok _ => []

def CompatibilityDiagnostic (s : String) : Prop := ∃ x, s = "InvalidCompatibility" ++ x

theorem pending_not_compatibility (s : String) : ¬ CompatibilityDiagnostic ("PresuppositionUnresolved: " ++ s) := by
  rintro ⟨x, hx⟩
  have := congrArg (fun t => t.toList.head?) hx
  simp at this

/-- An unfinished enumeration leaves every reading-dependent verdict UNKNOWN and is never a
compatibility rejection. -/
theorem extension_unknown (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (hb : res.joint = .error "ResourceLimit: joint choices") :
    (∀ e, e ∈ res.pending → ¬ CompatibilityDiagnostic e.2) ∧
    ∀ v ∈ readingVerdicts res, v.2 = "UNKNOWN (joint choices)" := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, r, _, rfl⟩ | ⟨_, _, n, _, _, _, ha⟩
  · simp [lift1] at hb
  · obtain ⟨F, _⟩ := admit_facts2 profiles environment rv j _ res ha
    refine ⟨fun e he => ?_, fun v hv => ?_⟩
    · rw [F.pending] at he
      unfold pendingIn at he
      obtain ⟨m, _, hm⟩ := List.mem_filterMap.mp he
      split at hm
      · cases hm; exact pending_not_compatibility _
      · cases hm
    · unfold readingVerdicts at hv
      rw [hb] at hv
      simp only at hv
      split at hv
      · obtain ⟨L, _, rfl⟩ := List.mem_map.mp hv; rfl
      · cases hv


/-! ## 9.6: validity claims and the truth boundary -/

theorem validity_find (res : Admitted) (P : PostFacts res.doc res.base res.bound) (v : Validity)
    (hv : v ∈ res.doc.K.validity) : res.doc.K.validity.find? (·.unit == v.unit) = some v :=
  find_key Validity.unit _ v P.validityNodup hv

theorem document_find (res : Admitted) (P : PostFacts res.doc res.base res.bound) (d : DocName)
    (hd : d ∈ res.doc.K.documents) : res.doc.K.documents.find? (·.name == d.name) = some d :=
  find_key DocName.name _ d P.documentsNodup hd

/-- 4.7: a validity claim about this document is `checked` exactly when it asserts validity. -/
theorem validity_self (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (v : Validity) (hv : v ∈ res.doc.K.validity) (hs : refersSelf res.doc v.document) :
    res.validity v.unit = some (if v.holds then .checked else .refuted) := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, r, _, rfl⟩ | ⟨_, _, n, _, _, _, ha⟩
  · exact absurd hv (by simp [lift1, emptyManifest])
  · obtain ⟨F, P⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨d, hd, hname, hself⟩ := hs
    rw [F.validity]
    simp only
    rw [validity_find res P v hv]
    simp only [Option.bind_some, verdictFor]
    rw [← hname, document_find res P d hd]
    simp [hself]

/-- An import's verdict follows its outcome: absent bytes are `unconfirmed`, stored bytes are
checked one level down. -/
theorem validity_import (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j (fuel + 1) = .ok res)
    (v : Validity) (hv : v ∈ res.doc.K.validity) (key : String) (hi : refersImport res.doc v.document key)
    (imp : Import) (hk : imp ∈ res.doc.K.imports ∧ imp.key = key) :
    (imp.bytes = none → res.validity v.unit = some (.unconfirmed "import bytes absent")) ∧
    (∀ b, imp.bytes = some b → res.validity v.unit = some (verdictOf v.holds (checkImport profiles b fuel))) ∧
    (∀ b, imp.bytes = some b → checkImport profiles b fuel =
      outcomeOf (admitDiscourse profiles (envOf b) (rvOf b) (jsonOf b) fuel)) := by
  rcases admit_cases profiles environment rv j (fuel + 1) res h with ⟨_, r, _, rfl⟩ | ⟨_, _, n, hn, _, _, ha⟩
  · exact absurd hv (by simp [lift1, emptyManifest])
  · cases hn
    obtain ⟨F, P⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨d, hd, hname, hrefers⟩ := hi
    have himp : res.doc.K.imports.find? (·.key == key) = some imp := by
      rw [← hk.2]; exact find_key Import.key _ imp P.importsNodup hk.1
    have hval : res.validity v.unit = match imp.bytes with
        | none => some (.unconfirmed "import bytes absent")
        | some b => some (verdictOf v.holds (checkImport profiles b fuel)) := by
      rw [F.validity]
      simp only
      rw [validity_find res P v hv]
      simp only [Option.bind_some, verdictFor]
      rw [← hname, document_find res P d hd]
      simp only [hrefers, himp]
      cases imp.bytes <;> rfl
    refine ⟨fun hb => by rw [hval, hb], fun b hb => by rw [hval, hb], fun _ _ => rfl⟩

theorem validity_unknown_never_checked (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j (fuel + 1) = .ok res)
    (v : Validity) (hv : v ∈ res.doc.K.validity) (key : String) (hi : refersImport res.doc v.document key) (imp : Import)
    (hk : imp ∈ res.doc.K.imports ∧ imp.key = key) (b : ByteArray) (hb : imp.bytes = some b) (r : String)
    (hu : checkImport profiles b fuel = .unknown r) :
    res.validity v.unit = some (.unconfirmed r) := by
  rw [(validity_import profiles environment rv j fuel res h v hv key hi imp hk).2.1 b hb, hu]
  rfl

theorem runAll_error : ∀ (fs : List (Unit → Except String Unit)) (e : String), runAll fs = .error e →
    ∃ f ∈ fs, f () = .error e
  | [], _, h => by cases h
  | f :: fs, e, h => by
    unfold runAll at h
    split at h
    · obtain ⟨g, hg, hge⟩ := runAll_error fs e h
      exact ⟨g, List.mem_cons_of_mem _ hg, hge⟩
    · rename_i e' he
      cases h
      exact ⟨f, List.mem_cons_self, he⟩

theorem runAll_head_error (f : Unit → Except String Unit) (fs : List (Unit → Except String Unit)) (e : String)
    (h : f () = .error e) : runAll (f :: fs) = .error e := by
  show (match f () with | .ok _ => runAll fs | .error e => .error e) = _
  rw [h]

theorem integrity_stale (j : Json) (K : Manifest) (imp : Import) (hk : imp ∈ K.imports) (b : ByteArray)
    (hb : imp.bytes = some b) (hne : sourceIdOf b ≠ imp.sourceId) :
    ∃ x, integrityOk j K = .error ("StaleTarget: " ++ x) := by
  let stage : Import → Except String Unit := fun imp => match imp.bytes with
    | some b => req (sourceIdOf b == imp.sourceId)
        ("StaleTarget: " ++ ((K.documents.find? fun d => d.refers == .imported imp.key).map DocName.name).getD imp.key)
    | none => .ok ()
  have hfail : stage imp ≠ .ok () := by
    simp only [stage, hb]
    intro hr
    exact hne (by simpa using (req_ok _ _).mp hr)
  cases hs : allOk K.imports stage with
  | ok v =>
    exact absurd ((allOk_iff _ _).mp (by cases v; exact hs) imp hk) hfail
  | error e =>
    have hint : integrityOk j K = .error e := runAll_head_error _ _ e hs
    obtain ⟨f, hf, hfe⟩ := runAll_error _ e hs
    obtain ⟨y, _, rfl⟩ := List.mem_map.mp hf
    simp only [stage] at hfe
    split at hfe
    · unfold req at hfe
      split at hfe
      · cases hfe
      · injection hfe with hfe
        exact ⟨_, by rw [hint, ← hfe]⟩
    · cases hfe

/-- Import integrity is a well-formedness condition of a `@2` document: stored bytes with
another source id reject the importing document with `StaleTarget`. -/
theorem stale_import_rejected (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (h2 : (j.getObjValD "format").getStr? = .ok "ve-document@2")
    (imp : Import) (hk : imp ∈ importsOf j)
    (b : ByteArray) (hb : imp.bytes = some b) (hne : sourceIdOf b ≠ imp.sourceId) :
    ∃ x, admitDiscourse profiles environment rv j fuel = .error ("StaleTarget: " ++ x) := by
  have hf := formatOf_of j _ h2
  unfold importsOf at hk
  cases hK : Wire.decodeManifest (j.getObjValD "discourse") with
  | error e => rw [hK] at hk; simp [Except.toOption] at hk
  | ok K =>
    rw [hK] at hk
    simp only [Except.toOption, Option.map_some, Option.getD_some] at hk
    obtain ⟨x, hx⟩ := integrity_stale j K imp hk b hb hne
    refine ⟨x, ?_⟩
    cases fuel <;> simp [admitDiscourse, admitAt, hf, hK, hx]

/-- A validity claim is never a premise and never bound. -/
theorem validity_never_premise (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (v : Validity) (hv : v ∈ res.doc.K.validity) : v.unit ∉ res.premiseUnits ∧ res.bound v.unit = none := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, r, _, rfl⟩ | ⟨_, _, n, _, _, _, ha⟩
  · exact absurd hv (by simp [lift1, emptyManifest])
  · obtain ⟨F, P⟩ := admit_facts2 profiles environment rv j _ res ha
    have := P.validity v hv
    simp only [Bool.and_eq_true, Bool.not_eq_true', Option.isNone_iff_eq_none] at this
    rw [F.premises]
    exact ⟨by simpa using this.1, this.2⟩

/-- The truth boundary: a self-truth unit has no content, is never a premise and is never CHECKED. -/
theorem self_truth_never_content (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (u : String) (hu : u ∈ res.selfTruth) :
    (unitOf res.doc.base u).bind VE.Route.Admission.DocUnit.content = none ∧ u ∉ res.premiseUnits ∧
    res.bound u = none ∧ statusOf res u = "LABELLED" := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, r, _, rfl⟩ | ⟨_, _, n, _, _, _, ha⟩
  · exact absurd hu (by simp [lift1])
  · obtain ⟨F, P⟩ := admit_facts2 profiles environment rv j _ res ha
    have hu' : u ∈ res.doc.K.selfTruth := by rw [← F.selfTruth]; exact hu
    have := P.selfTruth u hu'
    simp only [Bool.and_eq_true, Bool.not_eq_true', Option.isNone_iff_eq_none, beq_iff_eq] at this
    refine ⟨this.2, by rw [F.premises]; simpa using this.1.1, this.1.2, ?_⟩
    unfold statusOf
    rw [if_pos (List.contains_iff_mem.mpr hu)]

end VE.Discourse
