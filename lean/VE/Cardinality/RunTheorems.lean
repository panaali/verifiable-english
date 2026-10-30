import VE.Cardinality.Run

/-! Statements about the cardinality certificate decoder and the case runner (`Run.lean`), kept apart from
`RunExamples.lean` so a seeded bug in either is caught by a `#guard` there, not only by a proof here. -/
namespace VE.Cardinality.Run
open Lean

/-- A decoded certificate is the request's: its format is `ve-cardinality-certificate@1`, its identities are the
request's members, and its W6a part is W6a's decoding of the request's `w6` member. -/
theorem decodeCertificate_sound {j : Json} {cert : CardCertificate} (h : decodeCertificate j = .ok cert) :
    VE.Bridge.stringField j "format" = .ok "ve-cardinality-certificate@1" ∧
      VE.Bridge.stringField j "environment_id" = .ok cert.environmentId ∧
      VE.Bridge.stringField j "conclusion_meaning_id" = .ok cert.conclusionId ∧
      ∃ x, j.getObjVal? "w6" = .ok x ∧ VE.Time.Wire.decodeW6Certificate x = .ok cert.w6 := by
  unfold decodeCertificate at h
  split at h
  · rename_i heq
    cases h
    simp only [bind, Except.bind, pure, Except.pure] at heq
    repeat' split at heq
    all_goals first | cases heq | skip
    refine ⟨?_, ‹_›, ‹_›, _, ‹_›, ‹_›⟩
    simp_all
  · cases h

/-- The region table's constants are `regionTable`'s, in its order, each with its name, sort and bits. -/
theorem regionsJson_constants (R : RegionData) (table : List (String × String × Region)) :
    (regionsJson R table).getObjVal? "constants" = .ok (toJson (table.map fun e =>
      Json.mkObj [("constant", .str e.1), ("sort", .str e.2.1), ("bits", .str (bitString e.2.2))])) := by
  rfl

/-- The regenerated conclusion's row is `erasedProblem`'s conclusion, annotated and erased, with its W6a identities. -/
theorem erasedJson_conclusion {w : CardEnv} {ps : List CFormula} {c : CFormula} {pids : List (String × String)}
    {cid : String × String} (h : erasedIds w ps c = .ok (pids, cid)) :
    (erasedJson w ps c).map (·.getObjVal? "conclusion") = .ok (.ok (Json.mkObj
      [("Q", VE.Time.Wire.encQ (erasedProblem w.env ps c).2),
        ("core", VE.Time.Wire.encCore (erasedProblem w.env ps c).2.erase), ("meaning_id", .str cid.1),
        ("core_meaning_id", .str cid.2)])) := by
  unfold erasedJson
  rw [h]
  rfl

/-- The runner's erased problem (`problemJson`) is `erasedJson`'s, on the regenerated problem and its identities. -/
theorem erasedJson_problemJson (w : CardEnv) (ps : List CFormula) (c : CFormula) :
    erasedJson w ps c = (erasedIds w ps c).map (problemJson (erasedProblem w.env ps c)) := by
  unfold erasedJson
  cases erasedIds w ps c <;> rfl

/-- A runner's answer is its row; a refusal is an error row, and in a certificate case it says `valid: false`, so a
refused certificate is never reported valid. -/
theorem runCaseReported_ok {j r : Json} (h : runCase j = .ok r) : runCaseReported j = r := by
  simp [runCaseReported, h]

theorem runCaseReported_error {j : Json} {m : String} (h : runCase j = .error m) :
    runCaseReported j = Json.mkObj ([("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str m)] ++
      (if (j.getObjValD "kind").getStr?.toOption == some "certificate" then [("valid", .bool false)] else [])) := by
  simp [runCaseReported, h]

/-! ### P3 charged as the problem is built (`chargedNodes`) -/

theorem foldl_add_ge : ∀ (xs : List Nat) (u : Nat), u ≤ xs.foldl (· + ·) u
  | [], _ => Nat.le_refl _
  | x :: xs, u => Nat.le_trans (Nat.le_add_right u x) (foldl_add_ge xs (u + x))

theorem foldl_capped_ge (M : Nat) : ∀ (xs : List Nat) (u : Nat),
    u ≤ xs.foldl (fun a n => if a > M then a else a + n) u
  | [], _ => Nat.le_refl _
  | x :: xs, u => by
    simp only [List.foldl_cons]
    split
    · exact foldl_capped_ge M xs u
    · exact Nat.le_trans (Nat.le_add_right u x) (foldl_capped_ge M xs (u + x))

/-- A sum that stops adding once it passes `M` passes `M` exactly when the whole sum does. -/
theorem foldl_capped_gt (M : Nat) : ∀ (xs : List Nat) (u : Nat),
    xs.foldl (fun a n => if a > M then a else a + n) u > M ↔ xs.foldl (· + ·) u > M
  | [], _ => Iff.rfl
  | x :: xs, u => by
    simp only [List.foldl_cons]
    by_cases h : u > M
    · simp only [h, if_true]
      exact ⟨fun _ => Nat.lt_of_lt_of_le h (Nat.le_trans (Nat.le_add_right u x) (foldl_add_ge xs (u + x))),
        fun _ => Nat.lt_of_lt_of_le h (foldl_capped_ge M xs u)⟩
    · simp only [h, if_false]
      exact foldl_capped_gt M xs (u + x)

/-- The erased problem, built in the charge's order: the conclusion, then `erasedProblem`'s premises. -/
theorem erasedThunks_built (E : CEnv) (ps : List CFormula) (c : CFormula) :
    (erasedThunks E (regionData E (c :: ps)) (regionTable E (c :: ps)) ps c).map (· ()) =
      (erasedProblem E ps c).2 :: (erasedProblem E ps c).1 := by
  simp [erasedThunks, erasedProblem, nonnegPremises, bridgePremises, regionData_predsOn, regionData_universals,
    List.map_append, List.map_map, Function.comp_def]

/-- The charged P3 answers as W6a's aggregate limit on the whole erased problem: the same verdict and text. -/
theorem problemChecks_eq (E : CEnv) (ps : List CFormula) (c : CFormula) :
    problemChecks E ps c = (problemLimits E (c :: ps) >>= fun _ =>
      VE.Time.Wire.quantityLimits.aggregate ((erasedProblem E ps c).2 :: (erasedProblem E ps c).1)) := by
  have e : chargedNodes E ps c > VE.Limits.maxNodes ↔ (((erasedProblem E ps c).2 :: (erasedProblem E ps c).1).map
      (VE.Order.Wire.formulaNodes ·.erase)).foldl (· + ·) 0 > VE.Limits.maxNodes := by
    unfold chargedNodes
    rw [← List.foldl_map (f := fun q : Unit → VE.Time.QFormula => VE.Order.Wire.formulaNodes (q ()).erase)
      (g := fun a n => if a > VE.Limits.maxNodes then a else a + n), foldl_capped_gt, ← erasedThunks_built,
      List.map_map]
    rfl
  unfold problemChecks VE.Time.Wire.quantityLimits.aggregate
  simp only [e]
  rfl

/-! ### The erased problem built once, by the charge (`charge`, `checkedProblem`) -/

theorem charge_over {acc : Nat × List VE.Time.QFormula} (h : acc.1 > VE.Limits.maxNodes) :
    ∀ qs : List (Unit → VE.Time.QFormula), qs.foldl charge acc = acc
  | [] => rfl
  | q :: qs => by simp only [List.foldl_cons, charge, if_pos h]; exact charge_over h qs

/-- The charge's count is `chargedNodes`' sum. -/
theorem charge_fst : ∀ (qs : List (Unit → VE.Time.QFormula)) (acc : Nat × List VE.Time.QFormula),
    (qs.foldl charge acc).1 = qs.foldl (fun used q =>
      if used > VE.Limits.maxNodes then used else used + VE.Order.Wire.formulaNodes (q ()).erase) acc.1
  | [], _ => rfl
  | q :: qs, acc => by
    simp only [List.foldl_cons]
    rw [charge_fst qs]
    unfold charge
    split <;> rfl

/-- Within the limit, the charge has built every formula, in order. -/
theorem charge_snd : ∀ (qs : List (Unit → VE.Time.QFormula)) (acc : Nat × List VE.Time.QFormula),
    (qs.foldl charge acc).1 ≤ VE.Limits.maxNodes → (qs.foldl charge acc).2 = (qs.map (· ())).reverse ++ acc.2
  | [], _, _ => by simp
  | q :: qs, acc, h => by
    simp only [List.foldl_cons] at h ⊢
    by_cases hc : acc.1 > VE.Limits.maxNodes
    · rw [show charge acc q = acc by simp [charge, hc], charge_over hc] at h
      omega
    · have hq : charge acc q = (acc.1 + VE.Order.Wire.formulaNodes (q ()).erase, q () :: acc.2) := by
        simp [charge, hc]
      rw [hq] at h ⊢
      rw [charge_snd qs _ h]
      simp

/-- The runner's checks are `problemChecks`, and what they answer is `regionData`, `regionTable` and
`erasedProblem`: the region structure and the erased problem computed once are the problem's. -/
theorem checkedProblem_eq (E : CEnv) (ps : List CFormula) (c : CFormula) :
    checkedProblem E ps c = (problemChecks E ps c).map fun _ =>
      (regionData E (c :: ps), regionTable E (c :: ps), erasedProblem E ps c) := by
  unfold checkedProblem problemChecks
  rw [checkedRegions_eq]
  cases problemLimits E (c :: ps) with
  | error e => rfl
  | ok u =>
    simp only [Except.map, bind, Except.bind, regionData_table]
    have hf := charge_fst (erasedThunks E (regionData E (c :: ps)) (regionTable E (c :: ps)) ps c) (0, [])
    rw [← chargedNodes] at hf
    rw [hf]
    split
    · rfl
    · rename_i hle
      rw [charge_snd _ _ (by rw [charge_fst]; exact Nat.le_of_not_gt hle)]
      simp [erasedThunks_built, ofCharged, pure, Except.pure]

/-- The runner's certificate verdict, on what `checkedProblem` and `idsOf` answered, is `checkCertificate`'s. -/
theorem checkErased_eq {w : CardEnv} (ps : List (CAdmission w)) (c : CAdmission w) {R : RegionData}
    {table : List (String × String × Region)} {ep : List VE.Time.QFormula × VE.Time.QFormula}
    {ids : List (String × String) × (String × String)} (cert : CardCertificate)
    (hp : checkedProblem w.env (ps.map (·.formula)) c.formula = .ok (R, table, ep)) (hi : idsOf w ep = .ok ids) :
    checkErased ps c table ep ids cert = checkCertificate ps c cert := by
  rw [checkedProblem_eq] at hp
  cases h : problemChecks w.env (ps.map (·.formula)) c.formula with
  | error e => rw [h] at hp; cases hp
  | ok u =>
    rw [h] at hp
    cases hp
    unfold checkCertificate
    rw [h, show erasedIds w (ps.map (·.formula)) c.formula = .ok ids from hi]

end VE.Cardinality.Run
