import ResponseShape.FitsTactic
import VE.Service.Protocol

/-! Encoders several modes share: the claims and reports of an admission (`Route.Run.claimJson`,
`Norms.Run.reportJson`). -/

namespace ResponseShape.Encoders.Common
open Lean ResponseShape ResponseShape.Skeletons

variable {req : Json}

/-- `Route.Run.caseKind` (default `evaluate`) of a case that is an object. -/
theorem caseKind_read {j w : Json} {k' kind : String} (hobj : j.getObjVal? k' = .ok w)
    (h : VE.Route.Run.caseKind j = .ok kind) : KindRead "evaluate" j kind := by
  unfold VE.Route.Run.caseKind at h
  split at h
  · exact .inl (CaseCond.getObjValD_of_str ‹_› h)
  · cases h
    exact .inr ⟨CaseCond.lacks_of_error hobj ‹_›, rfl⟩

/-- `VE.Bridge.stringField` of a case: it is an object. -/
theorem stringField_obj {j : Json} {k s : String} (h : VE.Bridge.stringField j k = .ok s) :
    ∃ w, j.getObjVal? k = .ok w := by
  unfold VE.Bridge.stringField at h
  cases hv : j.getObjVal? k with
  | error e => rw [hv] at h; cases h
  | ok w => exact ⟨w, rfl⟩

theorem str_of_getStr {v : Json} {s : String} (h : v.getStr? = .ok s) : v = .str s := by
  cases v <;> simp_all [Json.getStr?] <;> cases h <;> rfl

theorem getObjValD_of_as {j : Json} {k s : String} (h : j.getObjValAs? String k = .ok s) : j.getObjValD k = .str s :=
  str_of_getStr h

theorem getObjValD_of_stringField {j : Json} {k s : String} (h : VE.Bridge.stringField j k = .ok s) :
    j.getObjValD k = .str s := by
  unfold VE.Bridge.stringField at h
  cases hv : j.getObjVal? k with
  | error e => rw [hv] at h; cases h
  | ok v =>
    rw [hv] at h
    exact CaseCond.getObjValD_of_str hv h

/-- The case's `kind` value, tested as the runner tests it. -/
theorem kind_holds_of_val {j v : Json} {k : String} (h : j.getObjVal? "kind" = .ok v)
    (hs : (v.getStr?.toOption == some k) = true) : (CaseCond.kind k).holds j = true := by
  simp only [CaseCond.holds, CaseCond.getObjValD_eq, h]
  exact hs

/-- An object case with no `kind` (an `if let .ok kind := ...` that failed). -/
theorem lacks_of_none {j w : Json} {k k' : String} (hobj : j.getObjVal? k' = .ok w)
    (h : ∀ v, j.getObjVal? k = .ok v → False) : (CaseCond.lacks k).holds j = true := by
  cases hv : j.getObjVal? k with
  | ok v => exact (h v hv).elim
  | error e => exact CaseCond.lacks_of_error hobj hv

theorem claimJson_fits (c : VE.Graph.Claim) :
    Fits req (skel% "common.json#/$defs/claim") (VE.Route.Run.claimJson c) := by
  unfold VE.Route.Run.claimJson
  fits

theorem reportJson_fits (r : VE.Graph.Report) :
    Fits req (skel% "common.json#/$defs/bound_report") (VE.Norms.Run.reportJson r) := by
  unfold VE.Norms.Run.reportJson
  fits
  all_goals exact claimJson_fits _

end ResponseShape.Encoders.Common

namespace ResponseShape

/-- In a runner that read its id (`stringField j "id"`) and its kind (`Route.Run.caseKind j`): the
kind the case has (`KindRead`), split into a case with that `kind` string and one without a kind
(read as `evaluate`), the runner's tests of the kind evaluated (`kind_norm`). -/
macro "read_kind" : tactic =>
  `(tactic|(obtain ⟨_, hobj⟩ := Encoders.Common.stringField_obj ‹VE.Bridge.stringField _ "id" = .ok _›
            have hK := Encoders.Common.caseKind_read hobj ‹VE.Route.Run.caseKind _ = .ok _›
            rcases hK with hK | ⟨hK, hd⟩
            all_goals (try subst hd)
            all_goals kind_norm))

end ResponseShape
