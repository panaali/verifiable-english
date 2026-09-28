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

/-- What `prepare` establishes: the wrapper passed, the identities under the base pair, the
manifest decoded from the block and mapped to token spans, and the validity bindings kept
apart from the document the admission reads. -/
structure PrepareFacts (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (P : Prepared) : Prop where
  wrapper : wrapperOk profiles environment j = .ok ()
  env : P.doc.E = rv.environment
  envId : VE.Route.Wire.environmentId (baseProfiles profiles) (baseEnvironment environment) = .ok P.environmentId
  sourceId : P.doc.sourceId = Loader.sourceId (baseProfiles profiles) (Loader.sourceOf j)
  manifest : ∃ K₀ K, Wire.decodeManifest P.doc.sets (Loader.filesOf j) P.environmentId
      ((Loader.metaOf j).getObjValD "discourse") = .ok K₀ ∧
    Wire.toTokenSpans ⟨Loader.sourceOf j, lex (Loader.sourceOf j)⟩ P.doc.base K₀ = .ok K ∧
    P.doc.K = { K with validity := [] } ∧ P.claims = K.validity

theorem prepare_facts (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (P : Prepared) (h : prepare profiles environment rv j = .ok P) : PrepareFacts profiles environment rv j P := by
  unfold prepare at h
  obtain ⟨_, hw, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨envId, henv, h⟩ := bind_ok h
  obtain ⟨front, _, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨K₀, hK₀, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨K, hK, h⟩ := bind_ok h
  simp only [pure, Except.pure, Except.ok.injEq] at h
  subst h
  exact ⟨hw, rfl, henv, rfl, ⟨K₀, K, hK₀, hK, rfl, rfl⟩⟩

theorem validity_stripped_of_prepare (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (P : Prepared) (h : prepare profiles environment rv j = .ok P) : P.doc.K.validity = [] := by
  obtain ⟨_, _, _, _, K₀, K, _, _, hK, _⟩ := prepare_facts profiles environment rv j P h
  rw [hK]

/-- What the validity-free core establishes about its result. -/
structure CoreFacts (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (D : DDoc)
    (envId : String) (C : CoreResult) : Prop where
  definitions : D.K.definitionsVersion = envId
  wf : wellFormed D = .ok ()
  base : VE.Route.Admission.admitDocument (baseProfiles profiles) (baseEnvironment environment) rv C.projected = .ok C.base
  pending : C.pending = pendingIn D C.base.wires C.base.doc (premiseUnitsOf C.base)
  post : postOk D C.base C.bound C.pending = .ok ()
  bindings : bindingsOk D C.base C.bound (baseProfiles profiles) envId = .ok ()
  bound : ∀ u, C.bound u ≠ none → (C.pending.map Prod.fst).contains u = false ∧
    C.bound u = (if (boundUnits D).contains u then (validate D u).toOption else none)
  boundPending : ∀ u, (C.pending.map Prod.fst).contains u = true → C.bound u = none

theorem core_facts (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (D : DDoc)
    (front : Loader.Front) (envId : String) (C : CoreResult)
    (h : admitCore profiles environment rv D front envId = .ok C) : CoreFacts profiles environment rv D envId C := by
  unfold admitCore at h
  try dsimp only at h
  obtain ⟨_, hdef, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, hwf, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, _, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨b, hb, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, _, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, hpost, h⟩ := bind_ok h
  obtain ⟨_, hbind, h⟩ := bind_ok h
  simp only [pure, Except.pure, Except.ok.injEq] at h
  subst h
  refine ⟨by simpa using (req_ok _ _).mp hdef, hwf, hb, rfl, hpost, hbind, ?_, ?_⟩
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

/-- Everything a successful `admit2` establishes about its result. -/
structure Admit2Facts (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (check : ByteArray → ImportOutcome) (res : Admitted) : Prop where
  prepared : PrepareFacts profiles environment rv j ⟨res.doc, res.front, res.environmentId, res.claims⟩
  core : admitCore profiles environment rv res.doc res.front res.environmentId =
    .ok ⟨res.base, res.projected, res.bound, res.pending⟩
  facts : CoreFacts profiles environment rv res.doc res.environmentId ⟨res.base, res.projected, res.bound, res.pending⟩
  premises : res.premiseUnits = premiseUnitsOf res.base
  claims : claimsOk res.doc res.claims = .ok ()
  validityPost : validityPostOk res.doc res.claims res.base res.bound = .ok ()
  choices : choicesOk res.doc.K res.base = .ok ()
  joint : res.joint = compatibleChoices res.doc.K (activeSets res.doc) 64
  gate : ∀ cs, res.joint = .ok cs → gateOk res.base (gateChoices res.doc cs) = .ok ()
  presuppositions : res.presuppositions = fun id =>
    ((presupMentions res.doc).find? (·.id == id)).bind (carrierIn res.doc res.base.wires res.base.doc res.premiseUnits)
  validity : res.validity = fun u =>
    (res.claims.find? (·.unit == u)).bind (verdictFor res.doc (selfOutcome res.joint) check)
  selfTruth : res.selfTruth = res.doc.K.selfTruth
  documentId : Loader.documentId j = .ok res.documentId
  references : res.references = referencesJson (Loader.metaOf j) res.pending
  reportId : wrapperReportId profiles res.environmentId res.documentId res.innerReportId res.references
    (validityJsonOf res.claims res.validity) = .ok res.reportId
  profiles : res.profiles = profiles

theorem Admit2Facts.wrapper {profiles environment rv j check res} (F : Admit2Facts profiles environment rv j check res) :
    wrapperOk profiles environment j = .ok () := F.prepared.wrapper
theorem Admit2Facts.wf {profiles environment rv j check res} (F : Admit2Facts profiles environment rv j check res) :
    wellFormed res.doc = .ok () := F.facts.wf
theorem Admit2Facts.base {profiles environment rv j check res} (F : Admit2Facts profiles environment rv j check res) :
    VE.Route.Admission.admitDocument (baseProfiles profiles) (baseEnvironment environment) rv res.projected = .ok res.base :=
  F.facts.base
theorem Admit2Facts.pending {profiles environment rv j check res} (F : Admit2Facts profiles environment rv j check res) :
    res.pending = pendingIn res.doc res.base.wires res.base.doc res.premiseUnits := by
  rw [F.premises]; exact F.facts.pending
theorem Admit2Facts.post {profiles environment rv j check res} (F : Admit2Facts profiles environment rv j check res) :
    postOk res.doc res.base res.bound res.pending = .ok () := F.facts.post
theorem Admit2Facts.bound {profiles environment rv j check res} (F : Admit2Facts profiles environment rv j check res) :
    ∀ u, res.bound u ≠ none → (res.pending.map Prod.fst).contains u = false ∧
      res.bound u = (if (boundUnits res.doc).contains u then (validate res.doc u).toOption else none) :=
  F.facts.bound
theorem Admit2Facts.boundPending {profiles environment rv j check res} (F : Admit2Facts profiles environment rv j check res) :
    ∀ u, (res.pending.map Prod.fst).contains u = true → res.bound u = none := F.facts.boundPending
theorem Admit2Facts.env {profiles environment rv j check res} (F : Admit2Facts profiles environment rv j check res) :
    res.doc.E = rv.environment := F.prepared.env

theorem admit2_facts (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (check : ByteArray → ImportOutcome) (res : Admitted) (h : admit2 profiles environment rv j check = .ok res) :
    Admit2Facts profiles environment rv j check res := by
  unfold admit2 at h
  obtain ⟨P, hP, h⟩ := bind_ok h
  obtain ⟨C, hC, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, hcl, h⟩ := bind_ok h
  obtain ⟨_, hvp, h⟩ := bind_ok h
  obtain ⟨_, hch, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, hgate, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨docId, hdoc, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  try dsimp only at h
  obtain ⟨_, hrep, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  try dsimp only at h
  simp only [pure, Except.pure, Except.ok.injEq] at h
  subst h
  refine ⟨prepare_facts profiles environment rv j P hP, hC, core_facts _ _ _ _ _ _ C hC, rfl, hcl, hvp, hch, rfl,
    ?_, rfl, rfl, rfl, hdoc, rfl, hrep, rfl⟩
  intro cs hcs
  simp only at hcs
  rw [hcs] at hgate
  simpa [Except.map, jointGate] using hgate

/-! ## The two paths of `admitDiscourse` -/

theorem admitAt_cases (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (check : Option (ByteArray → ImportOutcome)) (res : Admitted)
    (h : admitAt profiles environment rv j check = .ok res) :
    ((formatOf j == some "ve-document@1" || formatOf j == none) = true ∧
      ∃ w r, VE.Route.Admission.admitDocument profiles environment rv w = .ok r ∧ res = lift1 r) ∨
    (formatOf j = some "ve-document@2" ∧ Loader.isPayload j = true ∧ ∃ docs imports c,
      Wire.decodeTables (Loader.filesOf j) ((Loader.metaOf j).getObjValD "discourse") = .ok (docs, imports) ∧
      integrityOk j docs imports = .ok () ∧ check = some c ∧ admit2 profiles environment rv j c = .ok res) := by
  unfold admitAt at h
  split at h
  · rename_i h1
    split at h
    · cases h
    · split at h
      · cases ha : admit1 profiles environment rv j with
        | error e => rw [ha] at h; cases h
        | ok r =>
          rw [ha] at h
          simp only [Except.map, Except.ok.injEq] at h
          unfold admit1 at ha
          obtain ⟨_, _, ha⟩ := bind_ok ha
          obtain ⟨front, _, ha⟩ := bind_ok ha
          obtain ⟨_, _, ha⟩ := bind_ok ha
          exact Or.inl ⟨h1, front.w2, r, ha, h.symm⟩
      · cases hr : VE.Route.Admission.admitDocument profiles environment rv j with
        | error e => rw [hr] at h; cases h
        | ok r =>
          rw [hr] at h
          simp only [Except.map, Except.ok.injEq] at h
          exact Or.inl ⟨h1, j, r, hr, h.symm⟩
  · split at h
    · cases h
    · rename_i h2
      simp only [bne_iff_ne, ne_eq, Decidable.not_not, beq_iff_eq] at h2
      split at h
      · cases h
      · rename_i hp
        simp only [Bool.not_eq_true', Bool.not_eq_false] at hp
        split at h
        · cases h
        · rename_i docs imports ht
          split at h
          · cases h
          · rename_i v hi
            split at h
            · cases h
            · rename_i c
              exact Or.inr ⟨h2, by simpa using hp, docs, imports, c, ht, by cases v; exact hi, rfl, h⟩

theorem admit_cases (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res) :
    ((formatOf j == some "ve-document@1" || formatOf j == none) = true ∧
      ∃ w r, VE.Route.Admission.admitDocument profiles environment rv w = .ok r ∧ res = lift1 r) ∨
    (formatOf j = some "ve-document@2" ∧ Loader.isPayload j = true ∧ ∃ docs imports n, fuel = n + 1 ∧
      Wire.decodeTables (Loader.filesOf j) ((Loader.metaOf j).getObjValD "discourse") = .ok (docs, imports) ∧
      integrityOk j docs imports = .ok () ∧
      admit2 profiles environment rv j (checkImport (j.getObjValD "files") · n) = .ok res) := by
  cases fuel with
  | zero =>
    rcases admitAt_cases profiles environment rv j none res h with h | ⟨_, _, _, _, _, _, _, hc, _⟩
    · exact Or.inl h
    · cases hc
  | succ n =>
    rcases admitAt_cases profiles environment rv j _ res h with h | ⟨h2, hp, docs, imports, c, ht, hi, hc, ha⟩
    · exact Or.inl h
    · cases hc
      exact Or.inr ⟨h2, hp, docs, imports, n, rfl, ht, hi, ha⟩

/-! ## 9.6: the `@1` path and the profile adapter -/

theorem formatOf_of (j : Json) (s : String) (h : (j.getObjValD "format").getStr? = .ok s) : formatOf j = some s := by
  simp [formatOf, h, Except.toOption]

theorem getObjValD_ok (j : Json) (k : String) (s : String) (h : (j.getObjValD k).getStr? = .ok s) :
    (j.getObjVal? k).toBool = true := by
  cases hj : j.getObjVal? k with
  | ok v => rfl
  | error e =>
    have : j.getObjValD k = .null := by simp [Json.getObjValD, hj, Except.toOption]
    rw [this] at h
    cases h

theorem not_payload_of_format (j : Json) (s : String) (h : (j.getObjValD "format").getStr? = .ok s) :
    Loader.isPayload j = false := by
  simp [Loader.isPayload, getObjValD_ok j "format" s h]

/-- The `@1` path is delegated unchanged when the profile is off. -/
theorem format1_unchanged (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (h1 : (j.getObjValD "format").getStr? = .ok "ve-document@1") (hp : "ve.discourse@1" ∉ profiles) :
    admitDiscourse profiles environment rv j fuel = (VE.Route.Admission.admitDocument profiles environment rv j).map lift1 := by
  have hf := formatOf_of j _ h1
  have hn := not_payload_of_format j _ h1
  cases fuel <;> simp [admitDiscourse, admitAt, hf, hn, discourseProfile, hp]

/-- With the profile on, a `@1` document is the profile-gate error, never a silent delegation. -/
theorem format1_profile_requires_format2 (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (h1 : formatOf j = some "ve-document@1") (hp : "ve.discourse@1" ∈ profiles) :
    admitDiscourse profiles environment rv j fuel = .error "UnsupportedProfile: ve.discourse@1 requires ve-document@2" := by
  cases fuel <;> simp [admitDiscourse, admitAt, h1, discourseProfile, hp]

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
discourse checks; its document identity is the Python loader's over the same bytes. -/
theorem admission_projects (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted)
    (h2 : formatOf j = some "ve-document@2")
    (h : admitDiscourse profiles environment rv j fuel = .ok res) :
    VE.Route.Admission.admitDocument (baseProfiles profiles) (baseEnvironment environment) rv res.projected = .ok res.base ∧
    WellFormedDiscourse res.doc = true ∧
    (∀ u A, res.bound u = some A → validate res.doc u = .ok A) ∧
    Loader.documentId j = .ok res.documentId := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨hfm, _⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · rw [h2] at hfm
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

structure PostFacts (D : DDoc) (b : VE.Route.Admission.Admitted) (bound : String → Option VE.Formula)
    (pending : List (String × String)) : Prop where
  groupedNodup : (D.K.groups.flatMap Group.spans).Nodup
  groups : ∀ g ∈ D.K.groups,
    (b.doc.readingSets.any fun rs => rs.id == g.set && rs.version == g.version &&
        (groupFormula D g).any fun φ => rs.readings[g.reading]? == some φ) = true ∧
    (b.report.assumptions.filter fun l => setOfLabel l.label = some (g.set, g.version)).length ≤ 1 ∧
    ∀ u ∈ g.spans, ((unitOf b.doc u).bind VE.Route.Admission.DocUnit.content == none && (bound u).isNone &&
        !(premiseUnitsOf b).contains u && !(pending.map Prod.fst).contains u &&
        (b.report.assumptions.all fun l => l.label != "asserted" || unitOfLeaf b l != some u)) = true
  selfTruth : ∀ u ∈ D.K.selfTruth, (!(premiseUnitsOf b).contains u && (bound u).isNone &&
      (unitOf D.base u).bind VE.Route.Admission.DocUnit.content == none) = true
  documentsNodup : (D.K.documents.map DocName.name).Nodup
  mentionsNodup : (D.K.mentions.map Mention.id).Nodup
  importsNodup : (D.K.imports.map Import.key).Nodup
  groupedLabels : ∀ u ∈ D.K.groups.flatMap Group.spans, (!D.K.selfTruth.contains u) = true
  acyclic : ∃ order, VE.Route.dependencyOrder (importNodes D) = .ok order
  depth : depthOf D ≤ 4

theorem postOk_facts (D : DDoc) (b : VE.Route.Admission.Admitted) (bound : String → Option VE.Formula)
    (pending : List (String × String)) (h : postOk D b bound pending = .ok ()) : PostFacts D b bound pending := by
  unfold postOk at h
  simp only [runAll_cons, runAll_nil, and_true] at h
  obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩ := h
  refine ⟨dup_nodup h1, fun g hg => ?_, fun u hu => ?_, dup_nodup h4, dup_nodup h5, dup_nodup h6,
    fun u hu => ?_, ?_, by simpa using (req_ok _ _).mp h9⟩
  · have hg' := (allOk_iff _ _).mp h2 g hg
    simp only [runAll_cons, runAll_nil, and_true, req_ok, decide_eq_true_eq] at hg'
    obtain ⟨a, c, d⟩ := hg'
    exact ⟨a, c, fun u hu => (req_ok _ _).mp ((allOk_iff _ _).mp d u hu)⟩
  · exact (req_ok _ _).mp ((allOk_iff _ _).mp h3 u hu)
  · exact (req_ok _ _).mp ((allOk_iff _ _).mp h7 u hu)
  · cases ho : VE.Route.dependencyOrder (importNodes D) with
    | ok order => exact ⟨order, rfl⟩
    | error e => simp [ho] at h8

/-- The second phase's facts about the validity bindings. -/
structure ValidityFacts (D : DDoc) (claims : List Validity) (b : VE.Route.Admission.Admitted)
    (bound : String → Option VE.Formula) : Prop where
  notPremise : ∀ v ∈ claims, (!(premiseUnitsOf b).contains v.unit && (bound v.unit).isNone) = true
  nodup : (claims.map Validity.unit).Nodup
  notGrouped : ∀ u ∈ D.K.groups.flatMap Group.spans, (!(claims.map Validity.unit).contains u) = true

theorem validityPostOk_facts (D : DDoc) (claims : List Validity) (b : VE.Route.Admission.Admitted)
    (bound : String → Option VE.Formula) (h : validityPostOk D claims b bound = .ok ()) :
    ValidityFacts D claims b bound := by
  unfold validityPostOk at h
  simp only [runAll_cons, runAll_nil, and_true] at h
  obtain ⟨h1, h2, h3⟩ := h
  exact ⟨fun v hv => (req_ok _ _).mp ((allOk_iff _ _).mp h1 v hv), dup_nodup h2,
    fun u hu => (req_ok _ _).mp ((allOk_iff _ _).mp h3 u hu)⟩

/-- A successful `@2` admission's facts, with its post-admission checks. -/
theorem admit_facts2 (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (check : ByteArray → ImportOutcome) (res : Admitted) (h : admit2 profiles environment rv j check = .ok res) :
    Admit2Facts profiles environment rv j check res ∧ PostFacts res.doc res.base res.bound res.pending ∧
      ValidityFacts res.doc res.claims res.base res.bound := by
  have F := admit2_facts profiles environment rv j check res h
  exact ⟨F, postOk_facts _ _ _ _ F.post, validityPostOk_facts _ _ _ _ F.validityPost⟩

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
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, hr, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · obtain ⟨_, _, _, _, _, _, _, hs, hn, _, hc, hch⟩ := VE.Route.Admission.admit_report_sound.{u} _ _ _ _ _ hr
    exact ⟨hs, hn, hc, hch⟩
  · obtain ⟨F, _, _⟩ := admit_facts2 profiles environment rv j _ res ha
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
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, hr, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
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
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · exact absurd hm (by simp [lift1, emptyManifest])
  · obtain ⟨F, P, V⟩ := admit_facts2 profiles environment rv j _ res ha
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

theorem statusOf_grouped (res : Admitted) (P : PostFacts res.doc res.base res.bound res.pending)
    (V : ValidityFacts res.doc res.claims res.base res.bound)
    (hv : res.validity = fun u => (res.claims.find? (·.unit == u)).bind (verdictFor res.doc so check))
    (hs : res.selfTruth = res.doc.K.selfTruth)
    (g : Group) (hg : g ∈ res.doc.K.groups) (u : String) (hu : u ∈ g.spans) :
    statusOf res u = loadedStatus res.doc (g.spans.headD u) := by
  have hin : u ∈ res.doc.K.groups.flatMap Group.spans := List.mem_flatMap.mpr ⟨g, hg, hu⟩
  have hl := P.groupedLabels u hin
  have hc := V.notGrouped u hin
  simp only [Bool.not_eq_true', List.contains_iff_mem] at hl hc
  have hp := (P.groups g hg).2.2 u hu
  simp only [Bool.and_eq_true, Bool.not_eq_true'] at hp
  unfold statusOf
  have h1 : res.selfTruth.contains u = false := by rw [hs]; simpa using hl
  have h2 : res.validity u = none := by
    rw [hv]
    simp only
    have : res.claims.find? (·.unit == u) = none := by
      apply List.find?_eq_none.mpr
      intro v hv' he
      simp only [beq_iff_eq] at he
      exact absurd (List.mem_map.mpr ⟨v, hv', he⟩) (by simpa using hc)
    rw [this]; rfl
  simp only [h1, Bool.false_eq_true, if_false, h2, hp.1.2, unitStatus]
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
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · exact absurd hg (by simp [lift1, emptyManifest])
  · obtain ⟨F, P, V⟩ := admit_facts2 profiles environment rv j _ res ha
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
      obtain ⟨⟨⟨⟨hc, hb⟩, hp⟩, _⟩, _⟩ := hx
      have hhead : g.spans.head! ∈ g.spans := by
        cases hsp : g.spans with
        | nil => rw [hsp] at hu; cases hu
        | cons x xs => exact List.mem_cons_self
      refine ⟨hc, hb, by rw [F.premises]; simpa using hp, ?_⟩
      rw [statusOf_grouped res P V F.validity F.selfTruth g hg u hu,
        statusOf_grouped res P V F.validity F.selfTruth g hg _ hhead]
      cases hsp : g.spans with
      | nil => rw [hsp] at hu; cases hu
      | cons x xs => rfl

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
    ∃ c ∈ cs, ExtendsTo ch (c ++ authoredChoice res.doc) := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · cases hcs
  · obtain ⟨F, _, _⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨c', hc', he⟩ := (gate_facts (F.gate cs hcs)).1 L hL ch hch
    obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hc'
    exact ⟨c, hc, he⟩

/-- The merged transitive assumptions of the reported graph result extend to a validated
compatible choice. -/
theorem report_extends_joint (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (cs : List Choice) (hcs : res.joint = .ok cs)
    (ch : List (String × String))
    (hch : VE.Definitions.Bundle.leafChoices (res.base.report.assumptions.map (fun l => (l.label, l.formula))) = .ok ch) :
    ∃ c ∈ cs, ExtendsTo ch (c ++ authoredChoice res.doc) := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · cases hcs
  · obtain ⟨F, _, _⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨c', hc', he⟩ := (gate_facts (F.gate cs hcs)).2 ch hch
    obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hc'
    exact ⟨c, hc, he⟩

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
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · simp [lift1] at hb
  · obtain ⟨F, _, _⟩ := admit_facts2 profiles environment rv j _ res ha
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
      · rcases List.mem_append.mp hv with hv | hv
        · obtain ⟨L, _, rfl⟩ := List.mem_map.mp hv; rfl
        · rw [List.mem_singleton] at hv; rw [hv]
      · cases hv


/-! ## 9.6: validity claims and the truth boundary -/

theorem validity_find (res : Admitted) (V : ValidityFacts res.doc res.claims res.base res.bound) (v : Validity)
    (hv : v ∈ res.claims) : res.claims.find? (·.unit == v.unit) = some v :=
  find_key Validity.unit _ v V.nodup hv

theorem document_find (res : Admitted) (P : PostFacts res.doc res.base res.bound res.pending) (d : DocName)
    (hd : d ∈ res.doc.K.documents) : res.doc.K.documents.find? (·.name == d.name) = some d :=
  find_key DocName.name _ d P.documentsNodup hd

/-- 4.7: a validity claim about this document follows the document's own outcome: `admitted`
when the admission completed, `unknown` when its joint set hit the budget. -/
theorem validity_self_outcome (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (v : Validity) (hv : v ∈ res.claims) (hs : refersSelf res.doc v.document) :
    res.validity v.unit = some (verdictOf v.holds (selfOutcome res.joint)) := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · exact absurd hv (by simp [lift1, emptyManifest])
  · obtain ⟨F, P, V⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨d, hd, hname, hself⟩ := hs
    rw [F.validity]
    simp only
    rw [validity_find res V v hv]
    simp only [Option.bind_some, verdictFor]
    rw [← hname, document_find res P d hd]
    simp [hself]

/-- 4.7: in a completed admission a validity claim about this document is `checked` exactly
when it asserts validity. -/
theorem validity_self (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (v : Validity) (hv : v ∈ res.claims) (hs : refersSelf res.doc v.document) (hc : jointUnknown res.joint = none) :
    res.validity v.unit = some (if v.holds then .checked else .refuted) := by
  rw [validity_self_outcome profiles environment rv j fuel res h v hv hs]
  simp [selfOutcome, hc, verdictOf]

/-- 4.7: when this document's joint set hit the budget its own outcome is unknown, so a claim
about it is `unconfirmed` for either polarity (never `checked`). -/
theorem validity_self_unknown (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (v : Validity) (hv : v ∈ res.claims) (hs : refersSelf res.doc v.document) (e : String)
    (hc : jointUnknown res.joint = some e) :
    res.validity v.unit = some (.unconfirmed e) := by
  rw [validity_self_outcome profiles environment rv j fuel res h v hv hs]
  simp [selfOutcome, hc, verdictOf]

/-- 4.7: an import whose own admission answers `admitted: UNKNOWN` (its joint set hit the budget)
is an `unknown` outcome, never `admitted`. -/
theorem outcome_unknown_of_joint (res : Admitted) (e : String) (hc : jointUnknown res.joint = some e) :
    outcomeOf (.ok res) = .unknown e := by
  simp [outcomeOf, selfOutcome, hc]

/-- An import's verdict follows its outcome: absent bytes are `unconfirmed`, stored bytes are
checked one level down under the stored document's own environment and profiles
(`outcomeWith`), never the importing document's. -/
theorem validity_import (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j (fuel + 1) = .ok res)
    (v : Validity) (hv : v ∈ res.claims) (key : String) (hi : refersImport res.doc v.document key)
    (imp : Import) (hk : imp ∈ res.doc.K.imports ∧ imp.key = key) :
    (imp.bytes = none → res.validity v.unit = some (.unconfirmed "import bytes absent")) ∧
    (∀ b, imp.bytes = some b →
      res.validity v.unit = some (verdictOf v.holds (checkImport (j.getObjValD "files") b fuel))) ∧
    (∀ b, imp.bytes = some b → checkImport (j.getObjValD "files") b fuel =
      outcomeWith (fun ps env rv p => admitDiscourse ps env rv p fuel) (j.getObjValD "files") b) := by
  rcases admit_cases profiles environment rv j (fuel + 1) res h with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, hn, _, _, ha⟩
  · exact absurd hv (by simp [lift1, emptyManifest])
  · cases hn
    obtain ⟨F, P, V⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨d, hd, hname, hrefers⟩ := hi
    have himp : res.doc.K.imports.find? (·.key == key) = some imp := by
      rw [← hk.2]; exact find_key Import.key _ imp P.importsNodup hk.1
    have hval : res.validity v.unit = match imp.bytes with
        | none => some (.unconfirmed "import bytes absent")
        | some b => some (verdictOf v.holds (checkImport (j.getObjValD "files") b fuel)) := by
      rw [F.validity]
      simp only
      rw [validity_find res V v hv]
      simp only [Option.bind_some, verdictFor]
      rw [← hname, document_find res P d hd]
      simp only [hrefers, himp]
      cases imp.bytes <;> rfl
    refine ⟨fun hb => by rw [hval, hb], fun b hb => by rw [hval, hb], fun _ _ => rfl⟩

theorem validity_unknown_never_checked (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j (fuel + 1) = .ok res)
    (v : Validity) (hv : v ∈ res.claims) (key : String) (hi : refersImport res.doc v.document key) (imp : Import)
    (hk : imp ∈ res.doc.K.imports ∧ imp.key = key) (b : ByteArray) (hb : imp.bytes = some b) (r : String)
    (hu : checkImport (j.getObjValD "files") b fuel = .unknown r) :
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

theorem integrity_stale (j : Json) (docs : List DocName) (imports : List Import) (imp : Import)
    (hk : imp ∈ imports) (b : ByteArray) (hb : imp.bytes = some b) (hne : sourceIdOf b ≠ imp.sourceId) :
    ∃ x, integrityOk j docs imports = .error ("StaleTarget: " ++ x) := by
  let stage : Import → Except String Unit := fun imp => match imp.bytes with
    | some b => req (sourceIdOf b == imp.sourceId) ("StaleTarget: " ++ importName docs imp.key)
    | none => .ok ()
  have hfail : stage imp ≠ .ok () := by
    simp only [stage, hb]
    intro hr
    exact hne (by simpa using (req_ok _ _).mp hr)
  cases hs : allOk imports stage with
  | ok v =>
    exact absurd ((allOk_iff _ _).mp (by cases v; exact hs) imp hk) hfail
  | error e =>
    have hint : integrityOk j docs imports = .error e := by unfold integrityOk; exact runAll_head_error _ _ e hs
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
    (j : Json) (fuel : Nat) (h2 : formatOf j = some "ve-document@2") (hp : Loader.isPayload j = true)
    (imp : Import) (hk : imp ∈ importsOf j)
    (b : ByteArray) (hb : imp.bytes = some b) (hne : sourceIdOf b ≠ imp.sourceId) :
    ∃ x, admitDiscourse profiles environment rv j fuel = .error ("StaleTarget: " ++ x) := by
  unfold importsOf tablesOf at hk
  cases hK : Wire.decodeTables (Loader.filesOf j) ((Loader.metaOf j).getObjValD "discourse") with
  | error e => rw [hK] at hk; simp [Except.toOption] at hk
  | ok T =>
    rw [hK] at hk
    obtain ⟨docs, imports⟩ := T
    simp only [Except.toOption, Option.getD_some] at hk
    obtain ⟨x, hx⟩ := integrity_stale j docs imports imp hk b hb hne
    refine ⟨x, ?_⟩
    cases fuel <;> simp [admitDiscourse, admitAt, h2, hp, hK, hx]

/-- A validity claim is never a premise and never bound. -/
theorem validity_never_premise (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (v : Validity) (hv : v ∈ res.claims) : v.unit ∉ res.premiseUnits ∧ res.bound v.unit = none := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · exact absurd hv (by simp [lift1, emptyManifest])
  · obtain ⟨F, P, V⟩ := admit_facts2 profiles environment rv j _ res ha
    have := V.notPremise v hv
    simp only [Bool.and_eq_true, Bool.not_eq_true', Option.isNone_iff_eq_none] at this
    rw [F.premises]
    exact ⟨by simpa using this.1, this.2⟩

/-- The truth boundary: a self-truth unit has no content, is never a premise and is never CHECKED. -/
theorem self_truth_never_content (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (u : String) (hu : u ∈ res.selfTruth) :
    (unitOf res.doc.base u).bind VE.Route.Admission.DocUnit.content = none ∧ u ∉ res.premiseUnits ∧
    res.bound u = none ∧ statusOf res u = "LABELLED" := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · exact absurd hu (by simp [lift1])
  · obtain ⟨F, P, V⟩ := admit_facts2 profiles environment rv j _ res ha
    have hu' : u ∈ res.doc.K.selfTruth := by rw [← F.selfTruth]; exact hu
    have := P.selfTruth u hu'
    simp only [Bool.and_eq_true, Bool.not_eq_true', Option.isNone_iff_eq_none, beq_iff_eq] at this
    refine ⟨this.2, by rw [F.premises]; simpa using this.1.1, this.1.2, ?_⟩
    unfold statusOf
    rw [if_pos (List.contains_iff_mem.mpr hu)]

/-- Stratification: the embed/import chain is acyclic by source id and bounded. -/
theorem import_acyclic (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res) :
    VE.Route.DagAcyclic (importNodes res.doc) ∧ depthOf res.doc ≤ 4 := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · refine ⟨?_, by simp [depthOf, chainDepth, storedOfDoc, lift1, emptyManifest]⟩
    intro a hp
    have edge : ∀ x y, VE.Route.DepEdge (importNodes (lift1 r).doc) x y → False := by
      rintro x y ⟨m, hm, _, hy⟩
      simp [importNodes, importNodesAt, storedOfDoc, dedupNodes, lift1, emptyManifest] at hm
      subst hm
      simp [VE.Route.deps] at hy
    have nopath : ∀ x y, VE.Route.DepPath (importNodes (lift1 r).doc) x y → False := by
      intro x y hxy
      induction hxy with
      | edge he => exact edge _ _ he
      | trans _ _ ih _ => exact ih
    exact nopath a a hp
  · obtain ⟨_, P, _⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨order, ho⟩ := P.acyclic
    exact ⟨(VE.Route.dag_acyclic _ order ho).2.2.2, P.depth⟩

end VE.Discourse

namespace VE.Discourse
open Lean
open VE.Order.ProfileGate (bind_ok)

/-! ## 9.6: validity independence, the wire binding, stale targets -/

/-- 4.7: admission never reads a validity binding. The document the admission reads holds none
(the bindings are kept apart as `claims` and read only in the second phase), and the W2 result
is the validity-free core's on that document. -/
theorem validity_stripped (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) (res : Admitted) (h2 : formatOf j = some "ve-document@2")
    (h : admitDiscourse profiles environment rv j fuel = .ok res) :
    res.doc.K.validity = [] ∧
    admitCore profiles environment rv res.doc res.front res.environmentId = .ok ⟨res.base, res.projected, res.bound, res.pending⟩ := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨hfm, _⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · rw [h2] at hfm; simp at hfm
  · obtain ⟨F, _, _⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨_, _, _, _, K₀, K, _, _, hK, _⟩ := F.prepared
    exact ⟨by rw [hK], F.core⟩

/-- 4.7, relationally: two admissions of documents that differ only in their validity bindings
(the same admitted document and front matter) have the same W2 result, bound formulas and
pending units. -/
theorem validity_independent (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j j' : Json) (fuel : Nat) (res res' : Admitted)
    (h2 : formatOf j = some "ve-document@2") (h2' : formatOf j' = some "ve-document@2")
    (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (h' : admitDiscourse profiles environment rv j' fuel = .ok res')
    (hdoc : res.doc = res'.doc) (hfront : res.front = res'.front) :
    res.base = res'.base ∧ res.bound = res'.bound ∧ res.pending = res'.pending ∧ res.projected = res'.projected := by
  have e1 : VE.Route.Wire.environmentId (baseProfiles profiles) (baseEnvironment environment) = .ok res.environmentId := by
    rcases admit_cases profiles environment rv j fuel res h with ⟨hfm, _⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
    · rw [h2] at hfm; simp at hfm
    · exact (admit_facts2 profiles environment rv j _ res ha).1.prepared.envId
  have e2 : VE.Route.Wire.environmentId (baseProfiles profiles) (baseEnvironment environment) = .ok res'.environmentId := by
    rcases admit_cases profiles environment rv j' fuel res' h' with ⟨hfm, _⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
    · rw [h2'] at hfm; simp at hfm
    · exact (admit_facts2 profiles environment rv j' _ res' ha).1.prepared.envId
  have he : res.environmentId = res'.environmentId := Except.ok.inj (e1.symm.trans e2)
  have c1 := (validity_stripped profiles environment rv j fuel res h2 h).2
  have c2 := (validity_stripped profiles environment rv j' fuel res' h2' h').2
  rw [hdoc, hfront, he, c2] at c1
  have := (Except.ok.inj c1).symm
  simp only [CoreResult.mk.injEq] at this
  exact ⟨this.1, this.2.2.1, this.2.2.2, this.2.1⟩

/-- The meaning id a bound unit's elaboration has under the base pair (3.3). -/
def boundMeaningId (res : Admitted) (u : String) : Option String :=
  (res.bound u).bind fun A =>
    (VE.Route.Wire.meaningId (baseProfiles res.profiles) res.environmentId (VE.Route.Wire.encodeFormula A)).toOption

/-- The certificates the admission accepted for deductions formalising unit `u`. -/
def acceptedCertificates (res : Admitted) (u : String) : List VE.Tableau.Certificate :=
  res.base.wires.filterMap fun w => if w.unit == some u then w.deduction.map (·.certificate) else none

/-- What the binding check establishes. -/
theorem bindings_facts {D : DDoc} {b : VE.Route.Admission.Admitted} {bound : String → Option VE.Formula}
    {bp : List String} {envId : String} (h : bindingsOk D b bound bp envId = .ok ()) :
    (∀ u ∈ boundUnits D, ∀ A, bound u = some A → ∃ mid, VE.Route.Wire.meaningId bp envId (VE.Route.Wire.encodeFormula A) = .ok mid) ∧
    ∀ w ∈ b.wires, ∀ edge, w.deduction = some edge → edge.certificate.environment_id = envId ∧
      ∀ A, w.unit.bind bound = some A → ∃ mid, VE.Route.Wire.meaningId bp envId (VE.Route.Wire.encodeFormula A) = .ok mid ∧
        edge.certificate.conclusion_meaning_id = mid := by
  unfold bindingsOk at h
  simp only [runAll_cons, runAll_nil, and_true] at h
  obtain ⟨h1, h2⟩ := h
  refine ⟨fun u hu A hA => ?_, fun w hw edge he => ?_⟩
  · have := (allOk_iff _ _).mp h1 u hu
    simp only [hA] at this
    cases hm : VE.Route.Wire.meaningId bp envId (VE.Route.Wire.encodeFormula A) with
    | ok mid => exact ⟨mid, rfl⟩
    | error e => rw [hm] at this; cases this
  · have := (allOk_iff _ _).mp h2 w hw
    simp only [he, runAll_cons, runAll_nil, and_true] at this
    obtain ⟨hid, hc⟩ := this
    refine ⟨by simpa using (req_ok _ _).mp hid, fun A hA => ?_⟩
    simp only [hA] at hc
    cases hm : VE.Route.Wire.meaningId bp envId (VE.Route.Wire.encodeFormula A) with
    | ok mid => rw [hm] at hc; exact ⟨mid, rfl, by simpa using (req_ok _ _).mp hc⟩
    | error e => rw [hm] at hc; cases hc

theorem bound_mem {D : DDoc} {bound : String → Option VE.Formula} {pending : List (String × String)}
    (hb : ∀ u, bound u ≠ none → (pending.map Prod.fst).contains u = false ∧
      bound u = (if (boundUnits D).contains u then (validate D u).toOption else none))
    (u : String) (A : VE.Formula) (h : bound u = some A) : u ∈ boundUnits D := by
  have := (hb u (by rw [h]; simp)).2
  rw [h] at this
  split at this
  · rename_i hc; simpa using hc
  · cases this

/-- Binding (3.3): every result is bound to the identities recomputed under the base pair and to
the regenerated tables; the wrapper report binds the original profile declaration and the `@2`
document identity. The manifest is the decoded block with its spans mapped to tokens and its
validity bindings kept apart (lean/DISCOURSE.md). -/
theorem discourse_wire_binding (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted) (h2 : formatOf j = some "ve-document@2")
    (h : admitDiscourse profiles environment rv j fuel = .ok res) :
    res.doc.sourceId = Loader.sourceId (baseProfiles profiles) (Loader.sourceOf j) ∧
    (∃ K₀ K, Wire.decodeManifest res.doc.sets (Loader.filesOf j) res.environmentId
        ((Loader.metaOf j).getObjValD "discourse") = .ok K₀ ∧
      Wire.toTokenSpans ⟨Loader.sourceOf j, lex (Loader.sourceOf j)⟩ res.doc.base K₀ = .ok K ∧
      res.doc.K = { K with validity := [] } ∧ res.claims = K.validity) ∧
    VE.Route.Wire.environmentId (baseProfiles profiles) (baseEnvironment environment) = .ok res.environmentId ∧
    res.doc.K.definitionsVersion = res.environmentId ∧
    (∀ u A, res.bound u = some A → ∃ mid, VE.Route.Wire.meaningId (baseProfiles profiles) res.environmentId
        (VE.Route.Wire.encodeFormula A) = .ok mid ∧ boundMeaningId res u = some mid) ∧
    (∀ w ∈ res.base.wires, ∀ edge, w.deduction = some edge → edge.certificate.environment_id = res.environmentId) ∧
    Loader.documentId j = .ok res.documentId ∧
    wrapperReportId profiles res.environmentId res.documentId res.innerReportId res.references
      (validityJsonOf res.claims res.validity) = .ok res.reportId := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨hfm, _⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · rw [h2] at hfm; simp at hfm
  · obtain ⟨F, _, _⟩ := admit_facts2 profiles environment rv j _ res ha
    obtain ⟨hb1, hb2⟩ := bindings_facts F.facts.bindings
    refine ⟨F.prepared.sourceId, F.prepared.manifest, F.prepared.envId, F.facts.definitions, fun u A hA => ?_,
      fun w hw edge he => (hb2 w hw edge he).1, F.documentId, F.reportId⟩
    obtain ⟨mid, hm⟩ := hb1 u (bound_mem F.facts.bound u A hA) A hA
    refine ⟨mid, hm, ?_⟩
    simp [boundMeaningId, hA, F.profiles, hm, Except.toOption]

/-- Stale rejection over the bound evidence envelope (3.3, P0 3.9): a certificate accepted for `u`
carries the meaning id of `u`'s elaboration; under another admission where `u`'s elaboration has
another meaning id (a retargeted mention, the occurrence hypothesis), that certificate, with its
envelope unchanged, is not accepted. -/
theorem stale_target_rejected (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j j' : Json) (fuel : Nat) (res res' : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (h' : admitDiscourse profiles environment rv j' fuel = .ok res')
    (u : String) (mid mid' : String) (hmid : boundMeaningId res u = some mid)
    (hmid' : boundMeaningId res' u = some mid') (hne : mid ≠ mid')
    (c : VE.Tableau.Certificate) (hc : c ∈ acceptedCertificates res u) (henv : c.conclusion_meaning_id = mid) :
    c ∉ acceptedCertificates res' u := by
  intro hc'
  rcases admit_cases profiles environment rv j' fuel res' h' with ⟨_, _, r, _, rfl⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · simp [boundMeaningId, lift1] at hmid'
  · obtain ⟨F, _, _⟩ := admit_facts2 profiles environment rv j' _ res' ha
    obtain ⟨_, hb2⟩ := bindings_facts F.facts.bindings
    obtain ⟨w, hw, hwc⟩ := List.mem_filterMap.mp hc'
    split at hwc
    · rename_i hu
      simp only [beq_iff_eq] at hu
      cases hd : w.deduction with
      | none => rw [hd] at hwc; cases hwc
      | some edge =>
        rw [hd] at hwc
        simp only [Option.map_some, Option.some.injEq] at hwc
        subst hwc
        simp only [boundMeaningId] at hmid'
        cases hA : res'.bound u with
        | none => rw [hA] at hmid'; cases hmid'
        | some A =>
          rw [hA] at hmid'
          obtain ⟨_, hbind⟩ := hb2 w hw edge hd
          obtain ⟨mid'', hm'', hconc⟩ := hbind A (by rw [hu]; exact hA)
          rw [F.profiles] at hmid'
          simp only [Option.bind_some, hm'', Except.toOption, Option.some.injEq] at hmid'
          exact hne (henv.symm.trans (hconc.trans hmid'))
    · cases hwc

/-! ## 9.4: the recorded choices and the composition gate's rejection -/

/-- The manifest's recorded reading choices are the lemmas' labels (via `original_index`, 1.5). -/
theorem manifest_choices_are_labels (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (fuel : Nat) (res : Admitted) (h2 : formatOf j = some "ve-document@2")
    (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (L : VE.Route.Admission.Lemma) (hL : L ∈ res.base.doc.lemmas) :
    VE.Definitions.Bundle.leafChoices (leafList L) = .ok (choicesAsLabels res.doc.K.choices L) := by
  rcases admit_cases profiles environment rv j fuel res h with ⟨hfm, _⟩ | ⟨_, _, _, _, n, _, _, _, ha⟩
  · rw [h2] at hfm; simp at hfm
  · obtain ⟨F, _, _⟩ := admit_facts2 profiles environment rv j _ res ha
    have := (allOk_iff _ _).mp F.choices L hL
    cases hl : VE.Definitions.Bundle.leafChoices (leafList L) with
    | error e => rw [hl] at this; cases this
    | ok ch =>
      rw [hl] at this
      have hq := (req_ok _ _).mp this
      simp only [beq_iff_eq] at hq
      rw [hq]

theorem allOk_first_error {α : Type} (f : α → Except String Unit) (e : String) (x : α) :
    ∀ (pre post : List α), (∀ y ∈ pre, f y = .ok ()) → f x = .error e → allOk (pre ++ x :: post) f = .error e
  | [], post, _, hx => by
    unfold allOk
    simp only [List.nil_append, List.map_cons]
    exact runAll_head_error _ _ e hx
  | y :: ys, post, hpre, hx => by
    have hy := hpre y List.mem_cons_self
    have rest := allOk_first_error f e x ys post (fun z hz => hpre z (List.mem_cons_of_mem _ hz)) hx
    unfold allOk at rest ⊢
    simp only [List.cons_append, List.map_cons]
    unfold runAll
    simp only [hy]
    exact rest

/-- 4.8, the composition gate: on a completed joint set, a lemma whose transitive choices extend
to no compatible choice rejects the document with the named diagnostic, once every stage before
the gate has passed and every earlier lemma extends (the statement's `w3Passes`). -/
theorem extension_rejected (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (j : Json) (n : Nat) (h2 : formatOf j = some "ve-document@2") (hp : Loader.isPayload j = true)
    (docs : List DocName) (imports : List Import)
    (ht : Wire.decodeTables (Loader.filesOf j) ((Loader.metaOf j).getObjValD "discourse") = .ok (docs, imports))
    (hi : integrityOk j docs imports = .ok ())
    (P : Prepared) (hP : prepare profiles environment rv j = .ok P)
    (C : CoreResult) (hC : admitCore profiles environment rv P.doc P.front P.environmentId = .ok C)
    (hcl : claimsOk P.doc P.claims = .ok ()) (hvp : validityPostOk P.doc P.claims C.base C.bound = .ok ())
    (hch : choicesOk P.doc.K C.base = .ok ())
    (cs : List Choice) (hcs : compatibleChoices P.doc.K (activeSets P.doc) 64 = .ok cs)
    (pre post : List VE.Route.Admission.Lemma) (L : VE.Route.Admission.Lemma)
    (hL : C.base.doc.lemmas = pre ++ L :: post)
    (hpre : ∀ L' ∈ pre, ∃ ch', VE.Definitions.Bundle.leafChoices (leafList L') = .ok ch' ∧
      (gateChoices P.doc cs).any (extendsTo ch') = true)
    (ch : List (String × String)) (hchL : VE.Definitions.Bundle.leafChoices (leafList L) = .ok ch)
    (hno : ∀ c ∈ cs, ¬ ExtendsTo ch (c ++ authoredChoice P.doc)) :
    admitDiscourse profiles environment rv j (n + 1) = .error ("InvalidCompatibility: citation " ++ L.name) := by
  have hgate : gateOk C.base (gateChoices P.doc cs) = .error ("InvalidCompatibility: citation " ++ L.name) := by
    unfold gateOk
    apply runAll_head_error
    rw [hL]
    apply allOk_first_error
    · intro L' hL'
      obtain ⟨ch', h1, h2⟩ := hpre L' hL'
      simp only [h1, h2, req, if_true]
    · have hany : (gateChoices P.doc cs).any (extendsTo ch) = false := by
        cases hc : (gateChoices P.doc cs).any (extendsTo ch) with
        | false => rfl
        | true =>
          obtain ⟨c', hcm, he⟩ := List.any_eq_true.mp hc
          obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hcm
          exact absurd ((extendsTo_iff ch _).mp he) (hno c hc)
      simp only [hchL, hany, req, Bool.false_eq_true, if_false]
  have hadmit : ∀ check, admit2 profiles environment rv j check = .error ("InvalidCompatibility: citation " ++ L.name) := by
    intro check
    unfold admit2
    simp only [hP, hC, hcl, hvp, hch, hcs, Except.map, jointGate, hgate, bind, Except.bind]
  simp [admitDiscourse, admitAt, h2, hp, ht, hi, hadmit]

end VE.Discourse
