import ResponseShape.Encoders.Norms

/-! The `soft-norms` mode (`SoftNorms.Run.runCaseReported`) against `soft-norms.json#/row`. A case
off the soft path is the norms mode's, whose rows are rows of this mode. -/

namespace ResponseShape.Encoders.SoftNorms
open Lean ResponseShape ResponseShape.Skeletons
open VE.SoftNorms VE.SoftNorms.Wire VE.SoftNorms.Run

variable {req : Json}

/-- Every newly generated decision entry uses the environment's predicate-entry shape. -/
theorem decision_entries_fit (D : SoftDoc) :
    ∀ p ∈ decisions D,
      Fits req (skel% "common.json#/$defs/environment_predicate") (decisionEntry p.2) := by
  intro p _
  exact Common.decisionEntry_fits _

/-- The environment field of elaboration is the prime environment encoded from its source. -/
theorem regenerated_environment (D : SoftDoc) (env : Json) :
    (regenerated D env).lookup "environment_prime" =
      some ((primeJson D env).toOption.getD .null) := by
  rfl

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

theorem elaborate_fits (id : String) (D : SoftDoc) (env : Json) :
    Fits req (skel% "soft-norms.json#/$defs/elaborate") (VE.Route.Wire.ok id (regenerated D env)) := by
  unfold VE.Route.Wire.ok regenerated bgEntry
  fits
  all_goals first
    | exact Fits.softEnvironment D env (decision_entries_fit D) rfl
    | (exfalso; rename_i x hx h; have := softLabelled_nonempty D x hx; simp_all)

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

theorem runSoftKind_fits (id kind : String) (j : Json) {w : Json} (hobj : j.getObjVal? "id" = .ok w)
    (hp : usesSoftPath j = true) (hK : KindRead "evaluate" j kind) :
    OkFits j Skeletons.softNorms (runSoftKind id kind j) := by
  unfold runSoftKind
  simp only []
  rcases hK with hK | ⟨hK, hd⟩
  all_goals (try subst hd)
  all_goals okfits
  all_goals kind_norm
  all_goals first
    | fits_from elaborate_fits _ _ _
    | fits_from pairs_fits _ _ _ _ _ _ ‹_›
    | (try simp only [VE.Route.Wire.ok]); fits
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

/-- The norms mode's rows, off the soft path, are rows of this mode. -/
theorem of_norms {v : Json} (hp : usesSoftPath req = false) (h : Fits req Skeletons.norms v) :
    Fits req Skeletons.softNorms v :=
  Fits.onCaseE (by simpa [CaseCond.holds, CaseDecider.fn] using hp) h

theorem runCase_fits (j : Json) (hp : usesSoftPath j = true) :
    OkFits j Skeletons.softNorms (runCase j) := by
  unfold runCase
  okfits
  all_goals first
    | (exfalso; simp_all; done)
    | read_kind
  all_goals first
    | (unfold runAdmission; okfits; fits_from admission_fits _ _ _)
    | exact runSoftKind_fits _ _ _ ‹_› hp (KindRead.of_str ‹_›)
    | exact runSoftKind_fits _ _ _ ‹_› hp (Or.inr ⟨‹_›, rfl⟩)

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) :
    Fits j Skeletons.softNorms (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j ‹_› _ ‹_›
    · fits
  · exact of_norms (Bool.eq_false_iff.mpr ‹_›) (Norms.runCaseReported_fits j hj)

end ResponseShape.Encoders.SoftNorms
