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

/-- Every admission's kinds are its units' rendered kinds. -/
theorem admitDocument_kinds (environment document : Json) :
    OkP (fun res : Admission.Admitted => Common.KindsRendered res.kinds) (Admission.admitDocument environment document) := by
  unfold Admission.admitDocument
  okfits
  all_goals exact Common.kindsRendered_map _ _

theorem admission_fits (id reportId : String) (res : Admission.Admitted) (hk : Common.KindsRendered res.kinds) :
    Fits req (skel% "soft-norms.json#/$defs/admission") (encodeAdmitted id reportId res) := by
  unfold encodeAdmitted VE.Route.Wire.ok
  fits using Common.kind_fits hk
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
    | (unfold runAdmission; okfits; fits_from admission_fits _ _ _ (admitDocument_kinds _ _ _ ‹Admission.admitDocument _ _ = .ok _›))
    | exact runSoftKind_fits _ _ _ ‹_› hp (KindRead.of_str ‹_›)
    | exact runSoftKind_fits _ _ _ ‹_› hp (Or.inr ⟨‹_›, rfl⟩)

/-! ## The code of a soft rejection

`reportedCode` gives the code of the validation table's failing check (`Phases.checkSource`) or of
the message's prefix (`softDiagnosticCode`). Every such code is one `soft-norms.json#/$defs/error`
allows: `errorCodes` is read from that shape's skeleton, so a code the shape drops fails here. -/

/-- The codes of `soft-norms.json#/$defs/error`, read from its skeleton. -/
def errorCodes : List String :=
  match skel% "soft-norms.json#/$defs/error" with
  | .obj fs ex _ _ => match Skel.field fs ex "code" with
    | .strIn vs => vs
    | _ => []
  | _ => []

abbrev CodeOk (f : Phases.Fault) : Prop := f.code ∈ errorCodes

theorem fail_ok {α : Type} {c m : String} (h : c ∈ errorCodes) : ErrP CodeOk (Phases.fail c m : Phases.Check α) :=
  ErrP.error h

theorem inherited_ok {α : Type} {x : Except String α} {c : String} (h : c ∈ errorCodes) :
    ErrP CodeOk (Phases.inherited x c) := by
  unfold Phases.inherited
  split
  · exact ErrP.ok
  · exact ErrP.error h

/-- The checks of a phase that throw with a literal code. -/
macro "codes_ok" : tactic =>
  `(tactic|(errfits
            all_goals first
              | (apply fail_ok; decide +kernel)
              | (apply inherited_ok; decide +kernel)
              | skip))

theorem envelope_ok (e n : Json) : ErrP CodeOk (Phases.envelope e n) := by
  unfold Phases.envelope Phases.normArray
  codes_ok

theorem softNames_ok (b : Json) (f : String) (n : Nat) : ErrP CodeOk (Phases.softNames b f n) := by
  unfold Phases.softNames
  codes_ok

theorem softPairs_ok (b : Json) (f c : String) (hc : c ∈ errorCodes) : ErrP CodeOk (Phases.softPairs b f c) := by
  unfold Phases.softPairs
  errfits
  -- `#[.str a, .str b]`: the element as an array of two strings, or not.
  all_goals try (name_disc; rcases disc with
    (_ | _ | _ | _ | ⟨_ | ⟨(_ | _ | _ | a | _ | _), _ | ⟨(_ | _ | _ | b | _ | _), _ | ⟨c, rest⟩⟩⟩⟩ | _))
  all_goals first
    | (apply fail_ok; decide +kernel)
    | (errp_whnf; first
        | exact ErrP.error hc
        | with_reducible apply ‹∀ _ _, ErrP _ _›)

theorem declarations_ok (e : Json) (ps : List String) : ErrP CodeOk (Phases.declarations e ps) := by
  unfold Phases.declarations
  codes_ok
  all_goals first
    | exact softNames_ok _ _ _
    | exact softPairs_ok _ _ _ (by decide +kernel)

theorem profileChecks_ok (ps : List String) (ne : VE.Norms.Wire.NormsEnvironment) :
    ErrP CodeOk (Phases.profileChecks ps ne) := by
  unfold Phases.profileChecks Phases.unsupported
  codes_ok

theorem exceptionFields_ok (d : Option String) (n : String) (j : Json) :
    ErrP CodeOk (Phases.exceptionFields d n j) := by
  unfold Phases.exceptionFields
  codes_ok

theorem ruleFields_ok (d : Option String) (j : Json) : ErrP CodeOk (Phases.ruleFields d j) := by
  unfold Phases.ruleFields
  codes_ok
  all_goals exact exceptionFields_ok _ _ _

theorem environmentReferences_ok (s : SoftEnv) : ErrP CodeOk (Phases.environmentReferences s) := by
  unfold Phases.environmentReferences
  codes_ok

theorem typed_ok (E : VE.Environment) (Γ : List String) (φ : VE.Formula) (m : String) :
    ErrP CodeOk (Phases.typed E Γ φ m) := by
  unfold Phases.typed
  codes_ok

theorem ruleReferences_ok (ne : VE.Norms.Wire.NormsEnvironment) (s : SoftEnv) (N : SoftNode) :
    ErrP CodeOk (Phases.ruleReferences ne s N) := by
  unfold Phases.ruleReferences
  codes_ok
  all_goals exact typed_ok _ _ _ _

theorem documentReferences_ok (ne : VE.Norms.Wire.NormsEnvironment) (s : SoftEnv) (ns : List SoftNode) :
    ErrP CodeOk (Phases.documentReferences ne s ns) := by
  unfold Phases.documentReferences
  codes_ok
  all_goals exact ruleReferences_ok _ _ _

theorem rankSemantics_ok (s : SoftEnv) : ErrP CodeOk (Phases.rankSemantics s) := by
  unfold Phases.rankSemantics
  codes_ok

/-- Every check of the validation table fails with a code of `soft-norms.json#/$defs/error`. -/
theorem checkSource_ok (e n : Json) : ErrP CodeOk (Phases.checkSource e n) := by
  unfold Phases.checkSource
  errfits
  all_goals first
    | exact envelope_ok _ _
    | exact declarations_ok _ _
    | exact profileChecks_ok _ _
    | exact ruleFields_ok _ _
    | exact environmentReferences_ok _
    | exact documentReferences_ok _ _ _
    | exact rankSemantics_ok _

set_option maxRecDepth 10000 in
theorem softDiagnosticCode_mem (m : String) : softDiagnosticCode m ∈ errorCodes := by
  unfold softDiagnosticCode
  dsimp only [Id.run]
  split
  · decide +kernel
  split
  · decide +kernel
  split
  · -- One of the prefix table's codes.
    rename_i h
    have hm := List.mem_of_find?_eq_some h
    clear h
    simp only [List.mem_cons, Prod.mk.injEq, List.not_mem_nil, or_false] at hm
    repeat' (first | (obtain ⟨_, rfl⟩ | hm := hm) | (obtain ⟨_, rfl⟩ := hm))
    all_goals (subst_vars; decide +kernel)
  split
  · decide +kernel
  · decide +kernel

theorem reportedCode_mem (j : Json) (m : String) : reportedCode j m ∈ errorCodes := by
  unfold reportedCode
  dsimp only
  split
  · split
    · exact checkSource_ok _ _ _ ‹_›
    · exact softDiagnosticCode_mem m
  · exact softDiagnosticCode_mem m

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) :
    Fits j Skeletons.softNorms (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j ‹_› _ ‹_›
    · fits
      exact Fits.strIn (reportedCode_mem _ _)
  · exact of_norms (Bool.eq_false_iff.mpr ‹_›) (Norms.runCaseReported_fits j hj)

end ResponseShape.Encoders.SoftNorms
