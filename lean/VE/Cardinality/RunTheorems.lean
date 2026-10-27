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
theorem regionsJson_constants (E : CEnv) (fs : List CFormula) :
    (regionsJson E fs).getObjVal? "constants" = .ok (toJson ((regionTable E fs).map fun e =>
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

/-- A runner's answer is its row; a refusal is an error row, and in a certificate case it says `valid: false`, so a
refused certificate is never reported valid. -/
theorem runCaseReported_ok {j r : Json} (h : runCase j = .ok r) : runCaseReported j = r := by
  simp [runCaseReported, h]

theorem runCaseReported_error {j : Json} {m : String} (h : runCase j = .error m) :
    runCaseReported j = Json.mkObj ([("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str m)] ++
      (if (j.getObjValD "kind").getStr?.toOption == some "certificate" then [("valid", .bool false)] else [])) := by
  simp [runCaseReported, h]

end VE.Cardinality.Run
