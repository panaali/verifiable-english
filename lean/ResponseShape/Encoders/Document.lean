import ResponseShape.Encoders.Common
import VE.Service.ScopeAdmission

namespace ResponseShape.Encoders.Document
open Lean ResponseShape ResponseShape.Skeletons

theorem meaning_fits (j : Json) (m : VE.Service.Document.Meaning) :
    Fits j (skel% "document.json#/$defs/meaning") m.json := by
  cases m <;> simp only [VE.Service.Document.Meaning.json] <;> fits

/-- A row's kind: W2's rendered kind, or the name of a rights source kind (`Service.Document.RightsKind.names`). -/
theorem rowKind_fits (j : Json) (k : VE.Service.Document.RowKind) :
    Fits j (.alt [.strIn ["asserted", "norm", "definition", "question", "instruction", "example", "exposition",
      "analogy", "explanation", "meta"], .kindNot "string", .strIn VE.Service.Document.RightsKind.names]) k.json := by
  cases k with
  | route k => cases k <;> simp only [VE.Service.Document.RowKind.json, VE.Route.Admission.renderKind] <;> fits
  | rights k => cases k <;> exact Fits.altTail (Fits.altTail (Fits.altHead (Fits.strIn_lit (by decide))))

theorem unit_fits (j : Json) (u : VE.Service.Document.RowUnit) :
    Fits j (skel% "document.json#/$defs/unit") (VE.Service.Document.unitJson u) := by
  cases h : u.parent <;> cases hc : u.content <;> cases hm : u.meaningId <;>
    simp [VE.Service.Document.unitJson, h, hc, hm] <;> fits using meaning_fits
  all_goals exact rowKind_fits j u.kind

/-- The alternatives route's coverage line fits the document schema's `block_coverage` (its cells as relayed,
with the document's own narrowings). -/
theorem block_coverage_fits (j : Json) (A : VE.Alternatives.AltDoc) (environment units narrowings : Json) :
    Fits j (skel% "document.json#/$defs/block_coverage")
      (VE.Alternatives.Wire.coverage A environment units narrowings) := by
  unfold VE.Alternatives.Wire.coverage
  fits
  case h_2 x completion item heq hx =>
    simp only [List.mem_flatMap, List.mem_filterMap] at hx
    rcases hx with ⟨action, _, harm, _, h⟩
    split at h <;> simp only [Option.some.injEq, reduceCtorEq] at h
    subst_vars
    fits
    all_goals
      split at heq <;> simp only [Option.some.injEq, reduceCtorEq] at heq
      subst_vars
      fits

/-- The cells the row relays are the line's `alternatives` field. -/
theorem cells_fits (j : Json) (b : VE.Service.Document.BlockCoverage) :
    Fits j (skel% "document.json#/$defs/cells") (b.line.getObjValD "alternatives") := by
  have hk : b.line.getObjVal? "alternatives" = .ok (b.line.getObjValD "alternatives") := by
    show (VE.Alternatives.Wire.coverage b.doc b.environment b.units b.narrowings).getObjVal? "alternatives" =
      .ok ((VE.Alternatives.Wire.coverage b.doc b.environment b.units b.narrowings).getObjValD "alternatives")
    unfold VE.Alternatives.Wire.coverage
    rfl
  exact Fits.getObjVal (block_coverage_fits j b.doc b.environment b.units b.narrowings) hk

theorem coverage_fits (j front : Json) (units : List VE.Service.Document.SourceUnit) (n : Nat)
    (block : Option VE.Service.Document.BlockCoverage) :
    Fits j (skel% "document.json#/$defs/coverage") (VE.Service.Document.coverageJson front units n block) := by
  unfold VE.Service.Document.coverageJson
  split <;> fits using cells_fits

theorem usage_fits (j : Json) (m : List (String × List String) × List String) :
    Fits j (skel% "document.json#/$defs/judgments") (VE.Service.Document.usageJson m) := by
  unfold VE.Service.Document.usageJson
  fits

theorem composedNode_fits (j : Json) (id : String) (n : VE.Norms.Node) :
    Fits j (skel% "document.json#/$defs/composed_reading")
      (Json.mkObj [("id", .str id), ("content", VE.Reports.encodeNode n)]) := by
  unfold VE.Reports.encodeNode
  fits

theorem composedReadingRow_fits (j reading : Json) :
    OkFits j (skel% "document.json#/$defs/composed_reading")
      (VE.Service.Document.composedReadingRow reading) := by
  unfold VE.Service.Document.composedReadingRow
  okfits
  split
  · unfold VE.Reports.encodeNode
    fits
    all_goals (simp only [Skel.field] <;> fits)
  · exact composedNode_fits j _ _

theorem composedList_fits (j : Json) (s : Skel) (xs : List Json)
    (h : ∀ x ∈ xs, Fits j s x) : Fits j (.arr [] s) (toJson xs) := by
  apply Fits.arrOf
  intro x hx
  exact h x (by simpa only [toJson, List.toJson,
    show (toJson : Json → Json) = id from rfl, Array.map_id, List.mem_toArray] using hx)

theorem composedSetRow_fits (j out authored : Json) :
    OkFits j (skel% "document.json#/$defs/composed_set")
      (VE.Service.Document.composedSetRow out authored) := by
  unfold VE.Service.Document.composedSetRow
  okfits
  all_goals
    rename_i readings hreadings
    have hrows := OkP.mapM (fun r _ => composedReadingRow_fits j r) readings hreadings
    fits using composedList_fits j _ readings hrows

theorem document_fits (j : Json) : OkFits j Skeletons.document (VE.Service.Document.checkCore j) := by
  unfold VE.Service.Document.checkCore VE.Service.Document.encode
  okfits
  all_goals split
  all_goals (try simp only [VE.Route.Wire.ok, List.cons_append, List.nil_append, List.append_nil])
  all_goals (try fits using coverage_fits, usage_fits)
  all_goals
    apply Fits.arrOf
    intro x hx
    simp only [show (toJson : Json → Json) = id from rfl, Array.map_id,
      List.mem_toArray, List.mem_map] at hx
    obtain ⟨u, _, rfl⟩ := hx
    exact unit_fits j u

/-! scope@0 (SC-1b): the fold of a governor unit's status keeps the row's shape. -/

theorem statusOf_ne {s : String} {t : VE.Reports.Status} (h : VE.Scope.statusOf s = some t) : t ≠ .unknown := by
  unfold VE.Scope.statusOf at h; split at h <;> cases h <;> nofun

theorem fold_status_mem (st : String → Option VE.Reports.Status) (hst : ∀ u t, st u = some t → t ≠ .unknown)
    (us : List String) : ((VE.Scope.governorStatus st us).getD .unformalised).render ∈ VE.Discourse.Loader.statuses := by
  cases h : VE.Scope.governorStatus st us with
  | none => decide
  | some t =>
    obtain ⟨u, _, hu⟩ := (VE.Scope.governor_status_weakest st us t h).2.2
    have := hst u t hu
    cases t <;> first | decide | exact absurd rfl this

theorem unit_status_fits (j : Json) (u : VE.Service.Document.RowUnit) {s : String}
    (hs : s ∈ VE.Discourse.Loader.statuses) :
    Fits j (skel% "document.json#/$defs/unit") ((VE.Service.Document.unitJson u).setObjVal! "status" (.str s)) := by
  cases h : u.parent <;> cases hc : u.content <;> cases hm : u.meaningId <;>
    simp only [VE.Service.Document.unitJson, h, hc, hm, Option.toList, List.map_nil, List.map_cons,
      List.append_nil, List.cons_append, List.nil_append] <;>
    refine Fits.setObj (by keys_ok) ?_ (Fits.strIn hs) <;>
    simp only [List.filter_cons, List.filter_nil, String.reduceBNe, bne_self_eq_false, Bool.false_eq_true,
      ↓reduceIte] <;> fields_split <;> fits using meaning_fits
  all_goals exact rowKind_fits j u.kind

theorem units_mem {c : VE.Service.Document.Checked} {xs : Array Json} {a : Json}
    (heq : toJson (c.rows.map VE.Service.Document.unitJson) = Json.arr xs) (h : a ∈ xs.toList) :
    ∃ u, a = VE.Service.Document.unitJson u := by
  simp only [toJson, List.toJson] at heq
  injection heq with hx
  subst hx
  simp at h
  obtain ⟨u, _, rfl⟩ := h
  exact ⟨u, rfl⟩

open VE.Service.Document in
theorem fold_fits (j : Json) (D : VE.Scope.SDoc) (id : String) (c : VE.Service.Document.Checked) :
    Fits j Skeletons.document (VE.Scope.foldGovernors D (VE.Service.Document.encode id c)) := by

  have e : ∀ k v, (k, v) ∈ [("id", Json.str id), ("status", .str "ok"), ("document_id", .str c.documentId),
      ("source_id", .str c.sourceId), ("source", .str c.source), ("units", toJson (c.rows.map unitJson)),
      ("coverage", coverageJson c.front c.units c.source.utf8ByteSize c.block)] →
      (encode id c).getObjValD k = v := by
    intro k v hk
    simp only [List.mem_cons, Prod.mk.injEq, List.not_mem_nil, or_false] at hk
    rcases hk with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;>
      (unfold encode; split <;> rfl)
  unfold VE.Scope.foldGovernors
  simp only [e "id" (.str id) (by simp), e "status" (.str "ok") (by simp),
    e "document_id" (.str c.documentId) (by simp), e "source_id" (.str c.sourceId) (by simp),
    e "source" (.str c.source) (by simp), e "units" _ (List.mem_cons_of_mem _ (List.mem_cons_of_mem _
      (List.mem_cons_of_mem _ (List.mem_cons_of_mem _ (List.mem_cons_of_mem _ (List.mem_cons_self ..)))))),
    e "coverage" (coverageJson c.front c.units c.source.utf8ByteSize c.block) (by simp)]
  fits
  case h_1.isTrue a _ xs heq hm _ =>
    obtain ⟨u, rfl⟩ := units_mem heq hm
    exact unit_fits j u
  case h_1.isFalse a _ xs heq hm _ =>
    obtain ⟨u, rfl⟩ := units_mem heq hm
    exact unit_status_fits j u (fold_status_mem _ (fun _ _ h => by
      simp only [Option.bind_eq_some_iff] at h; obtain ⟨_, _, h⟩ := h; exact statusOf_ne h) _)
  case h_2 hne => exact (hne _ rfl).elim
  case h_1 =>
    unfold coverageJson
    split <;> refine Fits.setObj (by keys_ok) ?_ (Fits.any _) <;>
      simp only [List.filter_cons, List.filter_nil, String.reduceBNe, bne_self_eq_false, Bool.false_eq_true,
        ↓reduceIte, List.cons_append, List.nil_append] <;> fields_split <;> fits using cells_fits

open VE.Service.Document in
theorem fold_with_readings_fits (j : Json) (D : VE.Scope.SDoc) (id : String)
    (c : VE.Service.Document.Checked) (rs : Json)
    (hrs : Fits j (skel% "document.json#/$defs/composed_readings") rs) :
    Fits j Skeletons.document
      ((VE.Scope.foldGovernors D (VE.Service.Document.encode id c)).setObjVal! "composed_readings" rs) := by
  have e : ∀ k v, (k, v) ∈ [("id", Json.str id), ("status", .str "ok"), ("document_id", .str c.documentId),
      ("source_id", .str c.sourceId), ("source", .str c.source), ("units", toJson (c.rows.map unitJson)),
      ("coverage", coverageJson c.front c.units c.source.utf8ByteSize c.block)] →
      (encode id c).getObjValD k = v := by
    intro k v hk
    simp only [List.mem_cons, Prod.mk.injEq, List.not_mem_nil, or_false] at hk
    rcases hk with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;>
      (unfold encode; split <;> rfl)
  unfold VE.Scope.foldGovernors
  simp only [e "id" (.str id) (by simp), e "status" (.str "ok") (by simp),
    e "document_id" (.str c.documentId) (by simp), e "source_id" (.str c.sourceId) (by simp),
    e "source" (.str c.source) (by simp), e "units" _ (List.mem_cons_of_mem _ (List.mem_cons_of_mem _
      (List.mem_cons_of_mem _ (List.mem_cons_of_mem _ (List.mem_cons_of_mem _ (List.mem_cons_self ..)))))),
    e "coverage" (coverageJson c.front c.units c.source.utf8ByteSize c.block) (by simp)]
  fits using hrs
  case h_1.isTrue a _ xs heq hm _ =>
    obtain ⟨u, rfl⟩ := units_mem heq hm
    exact unit_fits j u
  case h_1.isFalse a _ xs heq hm _ =>
    obtain ⟨u, rfl⟩ := units_mem heq hm
    exact unit_status_fits j u (fold_status_mem _ (fun _ _ h => by
      simp only [Option.bind_eq_some_iff] at h; obtain ⟨_, _, h⟩ := h; exact statusOf_ne h) _)
  case h_2 hne => exact (hne _ rfl).elim
  case h_1 =>
    unfold coverageJson
    split <;> refine Fits.setObj (by keys_ok) ?_ (Fits.any _) <;>
      simp only [List.filter_cons, List.filter_nil, String.reduceBNe, bne_self_eq_false, Bool.false_eq_true,
        ↓reduceIte, List.cons_append, List.nil_append] <;> fields_split <;> fits using cells_fits

/-- The entry without scope's branch answers an encoded row. -/
theorem checkCore_encode {j a : Json} (h : VE.Service.Document.checkCore j = .ok a) :
    ∃ id c, a = VE.Service.Document.encode id c := by
  unfold VE.Service.Document.checkCore at h
  obtain ⟨id, _, h⟩ := VE.Scope.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Scope.bind_ok h
  dsimp only at h
  split at h <;> obtain ⟨_, _, h⟩ := VE.Scope.bind_ok h <;> try cases ‹_ = Except.ok _›
  all_goals obtain ⟨c, _, h⟩ := VE.Scope.bind_ok h; exact ⟨id, c, (Except.ok.inj h).symm⟩

theorem checkDoc_fits (j : Json) : OkFits j Skeletons.document (VE.Service.Document.checkDoc j) := by
  unfold VE.Service.Document.checkDoc
  split
  · okfits
    rename_i a h
    obtain ⟨id, c, rfl⟩ := checkCore_encode h
    exact fold_fits j _ id c
  · exact document_fits j

theorem checkDocSets_fits (j : Json) : OkFits j Skeletons.document (VE.Service.Document.checkDocSets j) := by
  unfold VE.Service.Document.checkDocSets
  split
  · okfits
    rename_i a h
    obtain ⟨id, c, rfl⟩ := checkCore_encode h
    exact fold_fits j _ id c
  · exact document_fits j

theorem composedReadings_fits (j : Json) (D : VE.Scope.SDoc) (out : Json) :
    OkFits j (skel% "document.json#/$defs/composed_readings")
      (VE.Service.Document.composedReadings D out) := by
  unfold VE.Service.Document.composedReadings
  okfits
  rename_i rows hrows
  exact composedList_fits j _ rows (OkP.mapM (fun r _ => composedSetRow_fits j out r) rows hrows)

theorem checkDocSetsAnswered_fits (j : Json) :
    OkFits j Skeletons.document (VE.Service.Document.checkDocSetsAnswered j) := by
  unfold VE.Service.Document.checkDocSetsAnswered
  okfits
  · exact checkDocSets_fits j _ ‹_›
  · exact checkDocSets_fits j _ ‹_›
  · rename_i answer hcheck hscope D hD hnon out hout rs hrs
    have hscope' : "scope@0" ∈ VE.Service.Document.profilesOf j := Classical.byContradiction hscope
    obtain ⟨D₀, out₀, a, hD₀, hout₀, ha, heq⟩ := VE.Scope.scope_admission_sets j answer hcheck hscope'
    have hdeq : D₀ = D := by rw [hD] at hD₀; cases hD₀; rfl
    subst D₀
    have houteq : out₀ = out := by
      rw [← VE.Scope.governSetsFast_eq D] at hout₀
      rw [hout] at hout₀
      cases hout₀
      rfl
    subst out₀
    obtain ⟨id, c, hc⟩ := checkCore_encode ha
    rw [heq, hc]
    exact fold_with_readings_fits j D id c rs (composedReadings_fits j D out rs hrs)

theorem locatedRow_fits (j : Json) (message : String) (at_ : VE.Service.Document.Located) :
    Fits j Skeletons.document (VE.Service.Document.locatedRow j message at_) := by
  unfold VE.Service.Document.locatedRow
  split
  · fits
  · unfold VE.Service.ParseDiagnostic.span
    fits
  · fits

theorem runCaseReported_fits (j : Json) :
    Fits j Skeletons.document (VE.Service.Document.runCaseReported j) := by
  unfold VE.Service.Document.runCaseReported
  split
  · exact checkDocSetsAnswered_fits j _ ‹_›
  · split
    · exact locatedRow_fits j _ _
    · unfold VE.Service.Standalone.reported
      fits

end ResponseShape.Encoders.Document
