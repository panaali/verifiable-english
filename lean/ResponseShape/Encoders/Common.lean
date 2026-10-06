import ResponseShape.FitsTactic
import VE.Service.Protocol

/-! Encoders several modes share: the claims and reports of an admission (`Route.Run.claimJson`,
`Norms.Run.reportJson`). -/

namespace ResponseShape.Encoders.Common
open Lean ResponseShape ResponseShape.Skeletons

variable {req : Json}

/-- `Service.rejectionCode` gives one of the public codes (`common.json#/$defs/code`). -/
theorem rejectionCode_fits (m : String) :
    Fits req (skel% "common.json#/$defs/code") (.str (VE.Service.rejectionCode m)) := by
  unfold VE.Service.rejectionCode
  split
  · fits
  · dsimp only
    split
    · exact Fits.strIn (List.contains_iff_mem.mp ‹_›)
    · fits

/-! ### Kinds

An atomic kind renders as its word, any other as a tagged array (`Route.Admission.renderKind`), and
every admission's `kinds` are its units' rendered kinds (`KindsRendered`). -/

abbrev kindSkel : Skel :=
  .alt [.strIn ["asserted", "norm", "definition", "question", "instruction", "example", "exposition", "analogy",
    "explanation", "meta"], .kindNot "string"]

theorem renderKind_fits (k : VE.Route.Admission.Kind) : Fits req kindSkel (VE.Route.Admission.renderKind k) := by
  cases k <;> simp only [VE.Route.Admission.renderKind] <;> fits

/-- The kinds of an admission: each a unit's rendered kind. -/
def KindsRendered (ks : List Json) : Prop := ∀ k ∈ ks, ∃ kd, k = VE.Route.Admission.renderKind kd

theorem kind_fits {ks : List Json} (h : KindsRendered ks) {k : Json} (hk : k ∈ ks) : Fits req kindSkel k := by
  obtain ⟨kd, rfl⟩ := h k hk
  exact renderKind_fits kd

theorem kindsRendered_map {α : Type} (us : List α) (f : α → VE.Route.Admission.Kind) :
    KindsRendered (us.map fun x => VE.Route.Admission.renderKind (f x)) := by
  intro k hk
  obtain ⟨u, _, rfl⟩ := List.mem_map.mp hk
  exact ⟨_, rfl⟩

theorem admitDocument_kinds (ps : List String) (env : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json) :
    OkP (fun res : VE.Route.Admission.Admitted => KindsRendered res.kinds)
      (VE.Route.Admission.admitDocument ps env rv j) := by
  unfold VE.Route.Admission.admitDocument
  okfits
  exact kindsRendered_map _ _

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

/-- A decision predicate added to the regenerated environment has the predicate-entry shape. -/
theorem decisionEntry_fits (sorts : List String) :
    Fits req (skel% "common.json#/$defs/environment_predicate")
      (VE.SoftNorms.Wire.decisionEntry sorts) := by
  unfold VE.SoftNorms.Wire.decisionEntry
  fits

/-- A rights predicate added to the regenerated environment has the same entry shape. -/
theorem generatedEntry_fits (sorts : List String) (description verbalisation : String) :
    Fits req (skel% "common.json#/$defs/environment_predicate")
      (VE.Rights.Wire.generatedEntry sorts description verbalisation) := by
  unfold VE.Rights.Wire.generatedEntry
  fits

end ResponseShape.Encoders.Common

namespace ResponseShape
open Lean Meta Elab Tactic in
/-- The hypothesis whose type is `lhs = Except.ok _` with `lhs` an application of `fn` whose
argument `i` is the string `arg` (found by its form, never by unfolding the runners). -/
def findOkHyp (fn : Name) (arity : Nat) (argIdx : Nat) (arg : String) : TacticM (Option Expr) := withMainContext do
  for d in ← getLCtx do
    if d.isImplementationDetail then continue
    let ty := (← instantiateMVars d.type).consumeMData
    let some (_, l, r) := ty.eq? | continue
    let l := l.consumeMData
    unless l.isAppOfArity fn arity && r.consumeMData.isAppOfArity ``Except.ok 3 do continue
    if argIdx < arity then
      unless FitsTactic.strLit? l.getAppArgs[argIdx]! == some arg do continue
    return some d.toExpr
  return none

open Lean Meta Elab Tactic in
/-- In a runner that read its id (`stringField j "id"`) and its kind (`Route.Run.caseKind j`): the
kind the case has (`KindRead`, from `hobj : j.getObjVal? "id" = .ok _`), split into a case with
that `kind` string and one without a kind (read as `evaluate`), the runner's tests of the kind
evaluated (`kind_norm`). The runner's facts are found by their form, never by unfolding. -/
elab "read_kind" : tactic => do
  withMainContext do
    let some hid ← findOkHyp ``VE.Bridge.stringField 2 1 "id" | throwError "read_kind: no id read"
    let hobjE ← mkAppM ``Encoders.Common.stringField_obj #[hid]
    let (_, g) ← (← getMainGoal).note `hobjE hobjE
    replaceMainGoal [g]
  evalTactic (← `(tactic| obtain ⟨_, $(mkIdent `hobj):ident⟩ := $(mkIdent `hobjE):ident))
  withMainContext do
    let some hk ← findOkHyp ``VE.Route.Run.caseKind 1 1 "" | throwError "read_kind: no kind read"
    let some ho ← findOkHyp ``Lean.Json.getObjVal? 2 1 "id" | throwError "read_kind: not an object"
    let hK ← mkAppM ``Encoders.Common.caseKind_read #[ho, hk]
    let (_, g) ← (← getMainGoal).note `hK hK
    replaceMainGoal [g]
  let hKi := mkIdent `hK
  evalTactic (← `(tactic| rcases $hKi:ident with $hKi:ident | ⟨$hKi:ident, hd⟩))
  evalTactic (← `(tactic| all_goals (try subst hd)))
  evalTactic (← `(tactic| all_goals kind_norm))

end ResponseShape
