import ResponseShape.Encoders.Norms

/-! The `soft-norms` mode (`SoftNorms.Run.runCaseReported`) against `soft-norms.json#/row`. A case
off the soft path is the norms mode's, whose rows are rows of this mode. -/

namespace ResponseShape.Encoders.SoftNorms
open Lean ResponseShape ResponseShape.Skeletons
open VE.SoftNorms VE.SoftNorms.Wire VE.SoftNorms.Run

variable {req : Json}

/-- Every soft premise label is a nonempty `soft:...` label (so `bgEntry` gives it a `label`). -/
theorem softLabelled_nonempty (D : SoftDoc) : ∀ x ∈ softLabelled D, x.1.isEmpty = false := by
  intro x hx
  simp only [softLabelled, List.mem_append, List.mem_map] at hx
  rcases hx with hx | ⟨⟨M, N⟩, _, rfl⟩
  · have := List.of_mem_zip hx
    simp only [excLabels, List.mem_flatMap] at this
    obtain ⟨⟨N, _, h⟩, _⟩ := this
    split at h
    · simp only [List.mem_append, List.mem_map, List.mem_range] at h
      rcases h with ⟨i, _, h⟩ | ⟨i, _, h⟩ <;> (rw [← h]; simp +decide [isEmpty_append, toString])
    · cases h
  · simp +decide [cohLabel, isEmpty_append, toString]

set_option maxHeartbeats 1000000 in
theorem elaborate_fits (id : String) (D : SoftDoc) (env : Json) (documentHash : String)
    (overlaps cycles : Option (List Json)) :
    Fits req (skel% "soft-norms.json#/$defs/elaborate")
      (VE.Route.Wire.ok id (regenerated D env ++ [("document_hash", .str documentHash)] ++
        overlaps.toList.map (fun value => ("overlaps", toJson value)) ++
        cycles.toList.map (fun value => ("override_cycles", toJson value)))) := by
  cases overlaps <;> cases cycles <;>
    simp only [Option.toList, List.map_cons, List.map_nil, List.append_nil] <;>
    unfold VE.Route.Wire.ok regenerated regeneratedCore bgEntry <;> fits
  all_goals (try { exfalso; rename_i x hx h; have := softLabelled_nonempty D x hx; simp_all })

/-- A pair's status and detail: a detail exactly beside a weighing point or UNKNOWN. -/
def Classified (r : PairStatus × String) : Prop :=
  (r.1 = .rankResolved ∨ r.1 = .disjoint) ∧ r.2.isEmpty = true ∨
    (r.1 = .weighingPoint ∨ r.1 = .unknown) ∧ r.2.isEmpty = false

theorem classify_ok (src : SoftSource) (environment norms pairs : Json) (M N : SoftNode) :
    OkP Classified (classify src environment norms pairs M N) := by
  unfold classify
  okfits
  all_goals simp +decide [Classified]

theorem pairs_fits (id : String) (src : SoftSource) (environment norms pairs : Json) (l : List (String × Json))
    (h : pairsResult src environment norms pairs = .ok l) :
    Fits req (skel% "soft-norms.json#/$defs/pairs") (VE.Route.Wire.ok id l) := by
  unfold pairsResult at h
  revert h
  apply OkP.bind
  intro rows hrows
  have hrows := OkP.mapM (Q := fun (r : String × PairStatus × Json) => ∃ M N detail, Classified (r.2.1, detail) ∧
      r.2.2 = Json.mkObj ([("pair", toJson [M.name, N.name]), ("label", .str (cohLabel M N)),
        ("status", .str r.2.1.text)] ++ (if detail.isEmpty then [] else [("detail", .str detail)])))
    (f := fun (MN : SoftNode × SoftNode) => do
      let (st, detail) ← classify src environment norms pairs MN.1 MN.2
      pure (cohLabel MN.1 MN.2, st, Json.mkObj ([("pair", toJson [MN.1.name, MN.2.name]),
        ("label", .str (cohLabel MN.1 MN.2)), ("status", .str st.text)] ++
        (if detail.isEmpty then [] else [("detail", .str detail)]))))
    (xs := collidingPairs src.D) (fun ⟨M, N⟩ _ => by
      apply OkP.bind
      intro ⟨st, detail⟩ hc
      exact OkP.pure ⟨M, N, detail, classify_ok src environment norms pairs M N _ hc, rfl⟩) rows hrows
  apply OkP.pure
  unfold VE.Route.Wire.ok
  fits
  rename_i r hr
  obtain ⟨M, N, detail, hc, he⟩ := hrows r hr
  simp only [Classified] at hc
  rw [he]
  rcases hc with ⟨hs | hs, hd⟩ | ⟨hs | hs, hd⟩ <;> simp only [hs, hd, PairStatus.text] <;> fits

/-- Not conflict-free: some target's certificate is missing or fails, which `firstFailure` names. -/
theorem firstFailure_of_not_free (j : Json) (res : SoftConflictReplay) (h : replaySoftConflict j = .ok res)
    (hf : res.conflictFree = false) : (firstFailure res).isSome = true := by
  unfold replaySoftConflict at h
  obtain ⟨env, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨src, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  simp only [SoftConflictReplay.conflictFree, softConflictFreeCheck, List.length_map, beq_self_eq_true,
    Bool.true_and, List.all_eq_false] at hf
  obtain ⟨⟨t, c⟩, hm, hc⟩ := hf
  simp only [firstFailure, Option.isSome_map]
  rw [List.find?_isSome]
  exact ⟨(t, c), hm, by cases c <;> simp_all⟩

set_option maxHeartbeats 1000000 in
theorem runSoftKind_fits (id kind : String) (j : Json) :
    OkFits req Skeletons.softNorms (runSoftKind id kind j) := by
  unfold runSoftKind
  simp only []
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  · fits_as "soft-norms.json#/$defs/rule"
    fits
  · fits_as "soft-norms.json#/$defs/rules"
    fits
  · fits_as "soft-norms.json#/$defs/elaborate"
    exact elaborate_fits _ _ _ _ _ _
  · fits_as "soft-norms.json#/$defs/pairs"
    exact pairs_fits _ _ _ _ _ _ ‹_›
  all_goals fits
  -- Not conflict-free with no failing target: impossible (`firstFailure_of_not_free`).
  all_goals
    exfalso
    have := firstFailure_of_not_free j _ ‹replaySoftConflict j = .ok _› (by simp_all)
    simp_all

theorem admission_fits (id reportId : String) (res : Admission.Admitted) :
    Fits req (skel% "soft-norms.json#/$defs/admission") (encodeAdmitted id reportId res) := by
  unfold encodeAdmitted VE.Route.Wire.ok
  fits
  all_goals exact Common.claimJson_fits _

/-- The norms mode's rows are rows of this mode. -/
theorem of_norms {v : Json} (h : Fits req Skeletons.norms v) : Fits req Skeletons.softNorms v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem runCase_fits (j : Json) :
    OkFits req Skeletons.softNorms (runCase j) := by
  unfold runCase
  okfits
  · unfold runAdmission
    okfits
    fits_as "soft-norms.json#/$defs/admission"
    exact admission_fits _ _ _
  · exact OkP.of (Norms.runCase_fits j) fun _ => of_norms
  · exact runSoftKind_fits _ _ _

theorem runCaseReported_fits (j : Json) :
    Fits j Skeletons.softNorms (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · exact of_norms (Norms.runCaseReported_fits j)

end ResponseShape.Encoders.SoftNorms
