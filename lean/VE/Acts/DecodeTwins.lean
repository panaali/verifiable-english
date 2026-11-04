import VE.Norms.FlaggedSpec
import VE.Norms.RunSound
import VE.NormDefaults.Run

/-! The twins of the reached soundness theorems (docs/spec/act-phrases.md 6.4): each entry point's theorem at the
decoder it runs an `acts@0` document on, stated with `decodeElaboratedFlagged` or `decodeElaboratedU` and `e.U'` where
the source's has `decodeSource` or `decodeSourceU` and `src.D` or `s.U`. Each is the existing proof, read through the
`In` form the route's own theorem instantiates; `Elaborated` and `ElaboratedDoc` carry the decoder's equation. The
statements of the existing theorems are unchanged. -/

namespace VE.Acts.Decode
open Lean VE.Norms VE.NormDefaults
open VE.Norms.Flagged (flagPremises baseEnv baseBackground BaseConflictFree Witness)
universe u

/-! ## The decoders -/

theorem elaborated_definitions (e : ElaboratedU) : e.U'.D.T.definitions = e.s.src.D.T.definitions := by
  obtain ⟨_, _, hU, _⟩ := elaborateMap_ok e.hE
  rw [hU, ← e.s.doc, ← e.hU]
  rfl

theorem decodeElaboratedFlagged_source {environment norms : Json} {e : ElaboratedU}
    (h : decodeElaboratedFlagged environment norms = .ok e) :
    Wire.decodeSource environment norms (flags := true) = .ok e.s.src := by
  unfold decodeElaboratedFlagged at h
  cases hd : Wire.decodeSource environment norms (flags := true) with
  | error err => simp [hd, bind, Except.bind] at h
  | ok src =>
    rw [hd] at h
    rw [elaborateSource_s h]
    rfl

/-- The elaborating decoder keeps a flag from naming a definition, as `decodeFlagged` does. -/
theorem flaggedSource_flag_not_defined (environment norms : Json) (s : Wire.Source)
    (h : flaggedSource environment norms = .ok s) :
    ∀ f ∈ s.ne.rv.flags, ∀ d ∈ s.D.T.definitions, f.name ≠ d.name := by
  obtain ⟨e, he, hD, hf⟩ := flaggedSource_elaborated h
  rw [hf, hD, elaborated_definitions]
  exact VE.Norms.FlaggedSpec.decodeSource_flag_not_defined _ _ _ _ (decodeElaboratedFlagged_source he)

/-- `s` reads the elaborated document of `environment` and `norms` on the norm-defaults route. -/
def ElaboratedDoc (environment norms : Json) (s : Wire.SourceU) : Prop :=
  ∃ e, decodeElaboratedU environment norms = .ok e ∧ s.U = e.U'

theorem elaboratedU_elaborated {environment norms : Json} {s : Wire.SourceU}
    (h : elaboratedU environment norms = .ok s) : ElaboratedDoc environment norms s := by
  unfold elaboratedU at h
  cases hd : decodeElaboratedU environment norms with
  | error err => simp [hd, bind, Except.bind] at h
  | ok e =>
    rw [hd] at h
    exact ⟨e, hd, (sourceOf_U h).1⟩

/-! ## The norms route -/

theorem norms_flagged_acceptance_elaborated (j : Json) (r : Replay.EntailmentReplay)
    (h : VE.Norms.Flagged.replayEntailmentIn flaggedSource j = .ok r) (hv : VE.Norms.Flagged.valid r = true) :
    Elaborated (j.getObjValD "environment") (j.getObjValD "norms") r.src ∧
    (∀ S : VE.Structure.{u}, S.Admissible (envAt r.src.D (size r.src.D)) →
      Sat S (flagPremises r.src) → holdsCatala r.src.D.T S →
      definitionsHold r.src.D S → profileHold r.src.D S → Sat S (backgroundBase r.src.D) →
      Sat S r.premises → r.conclusion.denote S []) ∧
    (flagPremises r.src = [] →
      (∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → ConflictFree r.src.D B) →
      (∀ a ∈ r.premises, a.WellFormed (envAt r.src.D 0) []) → r.conclusion.WellFormed (envAt r.src.D 0) [] →
      ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → Sat B r.premises → r.conclusion.denote B []) :=
  let ⟨hd, rest⟩ := VE.Norms.Flagged.norms_flagged_acceptanceIn.{u} flaggedSource j r h hv
  ⟨flaggedSource_elaborated hd, rest⟩

theorem norms_flagged_conflict_sound_elaborated (j : Json) (r : VE.Norms.Flagged.ConflictReplay) (h : VE.Norms.Flagged.replayConflictIn flaggedSource j = .ok r)
    (hv : r.conflictFree = true) :
    Elaborated (j.getObjValD "environment") (j.getObjValD "norms") r.src ∧
    (r.plain = true → ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → ConflictFree r.src.D B) ∧
    (r.plain = false → ∀ S : VE.Structure.{u}, S.Admissible (baseEnv r.src.D) →
      Sat S (baseBackground r.src) → BaseConflictFree r.src S) :=
  let ⟨hd, rest⟩ := VE.Norms.Flagged.norms_flagged_conflict_soundIn.{u} flaggedSource j r h hv
  ⟨flaggedSource_elaborated hd, rest⟩

theorem norms_flagged_witness_sound_elaborated (j : Json) (src : Wire.Source) (w : Witness src)
    (h : VE.Norms.Flagged.replayWitnessIn flaggedSource j = .ok ⟨src, w⟩) (hw : w.conflict = true) :
    Elaborated (j.getObjValD "environment") (j.getObjValD "norms") src ∧
    BaseAdmissible src.D w.M.asStructure ∧ Sat w.M.asStructure (flagPremises src) ∧
    ¬ ConflictFree src.D w.M.asStructure ∧
      ¬ (∀ B : VE.Structure.{0}, BaseAdmissible src.D B → Sat B (flagPremises src) → ConflictFree src.D B) :=
  let ⟨hd, rest⟩ := VE.Norms.Flagged.norms_flagged_witness_soundIn flaggedSource j src w h hw
  ⟨flaggedSource_elaborated hd, rest⟩

theorem norms_flagged_conflict_free_elaborated (j : Json) (r : VE.Norms.Flagged.ConflictReplay)
    (h : VE.Norms.Flagged.replayConflictIn flaggedSource j = .ok r) (hv : r.conflictFree = true) :
    Elaborated (j.getObjValD "environment") (j.getObjValD "norms") r.src ∧
    ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → Sat B (flagPremises r.src) → ConflictFree r.src.D B :=
  let ⟨hd, rest⟩ := VE.Norms.FlaggedSpec.norms_flagged_conflict_freeIn.{u} flaggedSource
    flaggedSource_flag_not_defined j r h hv
  ⟨flaggedSource_elaborated hd, rest⟩

theorem norms_wire_certificate_acceptance_elaborated (j answer : Json) (h : VE.Norms.Run.runCaseIn flaggedSource j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "norms-certificate")
    (hv : answer.getObjValD "valid" = .bool true) :
    ∃ r : VE.Norms.Replay.EntailmentReplay, VE.Norms.Flagged.replayEntailmentIn flaggedSource j = .ok r ∧
    Elaborated (j.getObjValD "environment") (j.getObjValD "norms") r.src ∧
    (∀ S : VE.Structure.{u}, S.Admissible (envAt r.src.D (size r.src.D)) →
      Sat S (flagPremises r.src) → holdsCatala r.src.D.T S →
      definitionsHold r.src.D S → profileHold r.src.D S → Sat S (backgroundBase r.src.D) →
      Sat S r.premises → r.conclusion.denote S []) ∧
    (flagPremises r.src = [] →
      (∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → ConflictFree r.src.D B) →
      (∀ a ∈ r.premises, a.WellFormed (envAt r.src.D 0) []) → r.conclusion.WellFormed (envAt r.src.D 0) [] →
      ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → Sat B r.premises → r.conclusion.denote B []) :=
  let ⟨r, hr, hd, rest⟩ := VE.Norms.RunSound.norms_wire_certificate_acceptanceIn.{u} flaggedSource j answer h hk hv
  ⟨r, hr, flaggedSource_elaborated hd, rest⟩

theorem norms_wire_conflict_free_elaborated (j answer : Json) (h : VE.Norms.Run.runCaseIn flaggedSource j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "norms-conflict")
    (hverdict : answer.getObjValD "verdict" = .str "CONFLICT-FREE") :
    ∃ src : Wire.Source,
      Elaborated (j.getObjValD "environment") (j.getObjValD "norms") src ∧
      ∀ B : VE.Structure.{u}, BaseAdmissible src.D B → Sat B (flagPremises src) → ConflictFree src.D B :=
  let ⟨src, hd, rest⟩ := VE.Norms.FlaggedSpec.norms_wire_conflict_freeIn.{u} flaggedSource flaggedSource_flag_not_defined j answer h hk hverdict
  ⟨src, flaggedSource_elaborated hd, rest⟩

theorem norms_wire_conflict_refuted_elaborated (j answer : Json) (h : VE.Norms.Run.runCaseIn flaggedSource j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "norms-conflict")
    (hverdict : answer.getObjValD "verdict" = .str "CONFLICT") :
    ∃ src : Wire.Source,
      Elaborated (j.getObjValD "environment") (j.getObjValD "norms") src ∧
      ¬ ∀ B : VE.Structure.{0}, BaseAdmissible src.D B → Sat B (flagPremises src) → ConflictFree src.D B :=
  let ⟨src, hd, rest⟩ := VE.Norms.FlaggedSpec.norms_wire_conflict_refutedIn flaggedSource j answer h hk hverdict
  ⟨src, flaggedSource_elaborated hd, rest⟩

/-- The route never answers CONFLICT-FREE and CONFLICT for one elaborated document. -/
theorem norms_wire_conflict_exclusive_elaborated (j₁ j₂ a₁ a₂ : Json)
    (h₁ : VE.Norms.Run.runCaseIn flaggedSource j₁ = .ok a₁) (hk₁ : VE.Route.Run.caseKind j₁ = .ok "norms-conflict")
    (h₂ : VE.Norms.Run.runCaseIn flaggedSource j₂ = .ok a₂) (hk₂ : VE.Route.Run.caseKind j₂ = .ok "norms-conflict")
    (he : j₁.getObjValD "environment" = j₂.getObjValD "environment")
    (hn : j₁.getObjValD "norms" = j₂.getObjValD "norms")
    (hv₁ : a₁.getObjValD "verdict" = .str "CONFLICT-FREE") :
    a₂.getObjValD "verdict" ≠ .str "CONFLICT" :=
  VE.Norms.FlaggedSpec.norms_wire_conflict_exclusiveIn flaggedSource flaggedSource_flag_not_defined j₁ j₂ a₁ a₂
    h₁ hk₁ h₂ hk₂ he hn hv₁

/-- The admission branch: the full admission obligation, on the elaborated document. -/
theorem norms_wire_acceptance_elaborated (j answer : Json) (h : VE.Norms.Run.runCaseIn flaggedSource j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : VE.Norms.Run.usesNormsPath j = true) :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      VE.Norms.Run.AdmissionAnswerIn flaggedSource id (j.getObjValD "environment") (j.getObjValD "document") answer :=
  VE.Norms.Run.norms_wire_acceptanceIn flaggedSource j answer h hk hn

/-- `admitDocumentIn`'s source is the elaborated document of the document's own norms. -/
theorem admission_elaborated (environment document : Json) (res : VE.Norms.Admission.Admitted)
    (h : VE.Norms.Admission.admitDocumentIn flaggedSource environment document = .ok res) :
    ∃ clean norms quoted, VE.Norms.Admission.splitDocument document = .ok (clean, norms, quoted) ∧
      Elaborated environment norms res.src ∧
      VE.Graph.SoundReport.{u} res.src.ne.rv.environment res.graph res.report := by
  obtain ⟨⟨⟨clean, norms, quoted, hs, hd, _⟩, _⟩, _, hsound, _⟩ :=
    VE.Norms.Admission.admitDocument_specIn.{u} flaggedSource environment document res h
  exact ⟨clean, norms, quoted, hs, flaggedSource_elaborated hd, hsound⟩

/-! ## The norm-defaults route -/

theorem normDefaults_wire_conflict_sound_elaborated (j : Json) (res : Wire.ConflictReplayU)
    (h : Wire.replayConflictUIn elaboratedU j = .ok res) (hv : res.conflictFree = true) :
    ∃ e, decodeElaboratedU (j.getObjValD "environment") (j.getObjValD "norms") = .ok e ∧ ConflictFreeU.{u} e.U' := by
  obtain ⟨hd, hc⟩ := Wire.normDefaults_wire_conflict_soundIn.{u} elaboratedU j res h hv
  obtain ⟨e, he, hU⟩ := elaboratedU_elaborated hd
  exact ⟨e, he, hU ▸ hc⟩

theorem normDefaults_wire_witness_sound_elaborated (j : Json) (s : Wire.SourceU) (w : Wire.WitnessDataU s)
    (h : Wire.replayWitnessUIn elaboratedU j = .ok ⟨s, w⟩) (hw : w.conflict = true) :
    ∃ e, decodeElaboratedU (j.getObjValD "environment") (j.getObjValD "norms") = .ok e ∧ ¬ ConflictFreeU.{0} e.U' := by
  obtain ⟨hd, hc⟩ := Wire.normDefaults_wire_witness_soundIn elaboratedU j s w h hw
  obtain ⟨e, he, hU⟩ := elaboratedU_elaborated hd
  exact ⟨e, he, hU ▸ hc⟩

theorem normDefaults_wire_acceptance_elaborated (j : Json) (r : Wire.EntailmentReplayU)
    (h : Wire.replayEntailmentUIn elaboratedU j = .ok r) (hv : r.valid = true) :
    ElaboratedDoc (j.getObjValD "environment") (j.getObjValD "norms") r.s ∧
    ∀ S : VE.Structure.{u}, BaseAdmissibleU r.s.U (restrictAll (fill r.s.U).T S) →
      DocumentExpansion (fill r.s.U) (restrictAll (fill r.s.U).T S) S → Sat S r.premises →
      r.conclusion.denote S [] :=
  let ⟨hd, rest⟩ := Wire.normDefaults_wire_acceptanceIn.{u} elaboratedU j r h hv
  ⟨elaboratedU_elaborated hd, rest⟩

theorem normDefaults_wire_status_sound_elaborated (j : Json) (d : Wire.StatusDataIn elaboratedU j)
    (_h : Wire.replayStatusIn elaboratedU j = .ok d) :
    ElaboratedDoc (j.getObjValD "environment") (j.getObjValD "norms") d.s ∧
    (∀ b, d.status = .settled b → SettledAs.{0} d.s.U d.M.asStructure d.r d.tuple b) ∧
    (d.status = .undecided → UndecidedAt.{0} d.s.U d.M.asStructure d.r d.tuple) :=
  let ⟨hd, rest⟩ := Wire.normDefaults_wire_status_soundIn elaboratedU j d _h
  ⟨elaboratedU_elaborated hd, rest⟩

theorem normDefaults_wire_report_sound_elaborated (j : Json) (rep : Wire.ReportUIn elaboratedU j)
    (_h : Wire.reportFromIn elaboratedU j = .ok rep) :
    ElaboratedDoc (j.getObjValD "environment") (j.getObjValD "norms") rep.s ∧
      Wire.ReportSound (Wire.normsSource rep.s rep.profiled j) rep.rep :=
  let ⟨hd, rest⟩ := Wire.normDefaults_wire_report_soundIn elaboratedU j rep _h
  ⟨elaboratedU_elaborated hd, rest⟩

/-- The admission branch: the full admission obligation on `fill e.U'`. -/
theorem normDefaults_wire_admission_elaborated (j answer : Json)
    (h : VE.NormDefaults.Run.runCaseIn elaboratedU j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission")
    (hp : Wire.hasProfile (j.getObjValD "environment") = true)
    (hs : Wire.layeredRoute (j.getObjValD "environment") ≠ some "soft-norms@0") :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      VE.NormDefaults.Run.AdmissionAnswerUIn elaboratedU id (j.getObjValD "environment") (j.getObjValD "document")
        answer :=
  VE.NormDefaults.Run.normDefaults_wire_admissionIn elaboratedU j answer h hk hp hs

end VE.Acts.Decode
