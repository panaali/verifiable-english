import VE.Service.Document
import VE.NormDefaults.LayeredEntail
import VE.NormDefaults.LayeredAdmission
import VE.Calc.Ties

/-! PC-2a: the theorems of `ve document check` on the soft chain under `norm-defaults@0`
(docs/spec/profile-composition.md 3.2). `requestOf` and `layeredOf` stand in `Service/Document.lean`, whose `check`
calls `layeredOf`. PC-2 (3), "two entry points, one answer", holds by construction: the document mode and the
`norm-defaults` mode run the one `decodeLayered`, and the parity test (F2.3, tests/test_document_chain.py) checks the
retired Python branch against it. -/

namespace VE.Service.DocumentChain
open Lean
open VE.Service.Document

universe u

/-- A case's environment is `E.lower` as the relay sends it. -/
theorem requestOf_environment (E : Env) (front : Json) (units : List SourceUnit)
    (hr : VE.NormDefaults.Wire.layeredRoute (wireJson 257 E.lower) = some "soft-norms@0")
    (hv : (VE.Compose.listedProfiles (wireJson 257 E.lower)).contains "events@0" = false) :
    (requestOf E front units).getObjVal? "environment" = .ok (wireJson 257 E.lower) := by
  unfold requestOf
  simp only [hr, hv, bne_self_eq_false, Bool.false_or, if_false, Bool.false_eq_true]
  apply VE.Calc.Run.mkObj_get
  · cases (front.getObjVal? "completions") <;> simp [Except.toOption]
  · simp

/-- A document's layered route is the soft branch with no events hook: `requestOf` makes a case on no other route
and on no list with `events@0`. -/
theorem layeredOf_soft (E : Env) (front : Json) (units : List SourceUnit) (L : VE.NormDefaults.Wire.LayeredU)
    (h : layeredOf E front units = .ok L) :
    ∃ environment norms, VE.NormDefaults.Wire.decodeSoftU environment norms = .ok L := by
  unfold layeredOf VE.NormDefaults.Wire.decodeLayered at h
  obtain ⟨environment, he, h⟩ := VE.Order.ProfileGate.bind_ok h
  by_cases hr : VE.NormDefaults.Wire.layeredRoute (wireJson 257 E.lower) = some "soft-norms@0"
  · by_cases hv : (VE.Compose.listedProfiles (wireJson 257 E.lower)).contains "events@0" = true
    · have hm : "events@0" ∈ VE.Compose.listedProfiles (wireJson 257 E.lower) := by simpa using hv
      have hn : requestOf E front units = .null := by simp [requestOf, hr, hm]
      rw [hn] at he
      cases he
    · have hv' : (VE.Compose.listedProfiles (wireJson 257 E.lower)).contains "events@0" = false := by simpa using hv
      rw [requestOf_environment E front units hr hv'] at he
      cases he
      obtain ⟨H, hH, h⟩ := VE.Order.ProfileGate.bind_ok h
      have hH' : H = none := by
        unfold VE.Events.eventsHook at hH
        rw [if_neg hv] at hH
        cases hH
        rfl
      subst hH'
      rw [hr] at h
      exact ⟨_, _, h⟩
  · have hn : requestOf E front units = .null := by simp [requestOf, hr]
    rw [hn] at he
    cases he

/-- PC-2a (1). A soft document gets today's packs. -/
theorem layeredOf_ids (E : Env) (front : Json) (units : List SourceUnit) (L : VE.NormDefaults.Wire.LayeredU)
    (h : layeredOf E front units = .ok L) (hs : E.soft = true) : L.packs.map (·.id) = ["soft"] := by
  have _ := hs
  obtain ⟨environment, norms, hL⟩ := layeredOf_soft E front units L h
  obtain ⟨_, src, _, _, _, _, hl, _⟩ := VE.NormDefaults.Wire.decodeSoftU_source environment norms L hL
  simp [hl, VE.NormDefaults.Wire.softPack, VE.NormDefaults.Wire.hookPacks, VE.NormDefaults.Wire.hookBlock]

/-- PC-2a (2). `acceptanceX` at the document's layered document, applied directly: `L.wfU`, and
`decodeSoftU_X_wellFormed` (LayeredAdmission.lean:53) or, for rights, `decodeRightsU_X_wellFormed`. -/
theorem layeredOf_entails (E : Env) (front : Json) (units : List SourceUnit) (L : VE.NormDefaults.Wire.LayeredU)
    (h : layeredOf E front units = .ok L) (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (VE.Norms.envAt (VE.NormDefaults.fill L.U) (VE.Norms.size (VE.NormDefaults.fill L.U)))
      (VE.NormDefaults.Wire.premisesX L.U L.X Γ) φ cert = true) :
    VE.NormDefaults.EntailsX.{u} L.U L.X Γ φ := by
  obtain ⟨environment, norms, hL⟩ := layeredOf_soft E front units L h
  exact VE.NormDefaults.acceptanceX L.U L.wfU L.X
    (VE.NormDefaults.Wire.decodeSoftU_X_wellFormed environment norms L hL) Γ φ cert hv

end VE.Service.DocumentChain
