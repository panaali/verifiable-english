import VE.Route.MeteredRun
import VE.Route.MeteredProofs

/-! Wire theorems of the `metered` mode's `evaluate-budgeted` kind (kernel boundary, KB-7).

`MeteredProofs` proves each family's metered evaluator against the total evaluator. This file
carries those theorems to the wire: an answer of `runCase` to an `evaluate-budgeted` case is the
encoding of a metered result over the formulas and the model that the case's own decoders read,
and a completed value of that result is the truth of every formula in that model. A value of
`null` (the budget was spent) asserts nothing.

The conclusions name decoders, `Metered.Result`, `Metered.resultFields`, `Wire.ok` and each
family's total evaluator; no budgeted evaluator and no index appears in them. -/
namespace VE.Route.MeteredRun
open Lean
open VE.Route
open VE.Order.ProfileGate (bind_ok)

/-- An `evaluate-budgeted` answer for `result`: the case's id, status `ok`, and under
`evaluation` the result's fields (`status`, `value`, `evaluations`) followed by an explanation
(the optional trace, about which nothing is stated here). -/
def EncodesEvaluation (id : String) (result : Metered.Result) (answer : Json) : Prop :=
  ∃ explanation : Json, answer = Wire.ok id
    [("evaluation", Json.mkObj (Metered.resultFields result ++ [("explanation", explanation)]))]

/-- An evaluation request decodes the document with the family's list decoder, and the document
is not empty. -/
theorem request_evaluate {α : Type} (q : Query) (formula : Json → Except String α)
    (formulas : Json → Except String (List α)) (r : Request α) (hq : q.nonVacuity = false)
    (h : request q formula formulas = .ok r) :
    ∃ fs, formulas q.input = .ok fs ∧ fs ≠ [] ∧ r = .evaluate fs := by
  unfold request at h
  simp only [hq, Bool.false_eq_true, ↓reduceIte] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨fs, hfs, h⟩ := bind_ok h
  by_cases he : fs.isEmpty = true
  · rw [if_pos he] at h
    cases h
  · rw [if_neg he] at h
    cases h
    exact ⟨fs, hfs, fun hn => he (by simp [hn]), rfl⟩

/-- The evaluation branch of `answer` encodes the session's document result. -/
theorem answer_evaluate {α ρ σ entity : Type} (q : Query) (s : Session α ρ σ entity) (fs : List α) :
    EncodesEvaluation q.id (s.document fs) (answer q s (.evaluate fs)) :=
  ⟨_, rfl⟩

/-- First-order family: the answer encodes a result whose completed value is the truth of every
decoded formula in the decoded model. -/
theorem run_fol_sound (q : Query) (checked : VE.Service.Standalone.Validated) (p : Prepared)
    (model answer : Json) (h : run q checked p model = .ok answer)
    (hfam : checked.envelope.family = .fol) (hq : q.nonVacuity = false) :
    ∃ (rv : Wire.RouteVocabulary) (fs : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
      (result : Metered.Result),
      p.route.get = .ok rv ∧
      Wire.decodeFormulas rv.environment q.input (checked.envelope.profiles.contains "data@0") = .ok fs ∧
      fs ≠ [] ∧
      Wire.decodeDataModel rv model = .ok M ∧
      EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval M []) := by
  unfold run at h
  simp only [hfam] at h
  obtain ⟨rv, hrv, h⟩ := bind_ok h
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨M, hM, h⟩ := bind_ok h
  obtain ⟨fs, hfs, hne, rfl⟩ := request_evaluate q _ _ r hq hr
  cases h
  refine ⟨rv, fs, M, _, hrv, hfs, hne, hM, answer_evaluate q _ fs, ?_⟩
  intro b hb
  exact MeteredProofs.fol_sound _ M q.limit (fun p row => Budget.tableMem_iff _ M p row) fs b hb

/-- Closure family. -/
theorem run_closure_sound (q : Query) (checked : VE.Service.Standalone.Validated) (p : Prepared)
    (model answer : Json) (h : run q checked p model = .ok answer)
    (hfam : checked.envelope.family = .closure) (hq : q.nonVacuity = false) :
    ∃ (rv : Wire.RouteVocabulary) (fs : List VE.Closure.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
      (result : Metered.Result),
      p.route.get = .ok rv ∧
      VE.Closure.Bridge.decodeFormulas rv.environment q.input = .ok fs ∧
      fs ≠ [] ∧
      Wire.decodeDataModel rv model = .ok M ∧
      EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval M []) := by
  unfold run at h
  simp only [hfam] at h
  obtain ⟨rv, hrv, h⟩ := bind_ok h
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨M, hM, h⟩ := bind_ok h
  obtain ⟨fs, hfs, hne, rfl⟩ := request_evaluate q _ _ r hq hr
  cases h
  refine ⟨rv, fs, M, _, hrv, hfs, hne, hM, answer_evaluate q _ fs, ?_⟩
  intro b hb
  exact MeteredProofs.closure_sound _ M q.limit (fun p row => Budget.tableMem_iff _ M p row) fs b hb

/-- Core family (closure with n-ary atoms). -/
theorem run_core_sound (q : Query) (checked : VE.Service.Standalone.Validated) (p : Prepared)
    (model answer : Json) (h : run q checked p model = .ok answer)
    (hfam : checked.envelope.family = .closureNary) (hq : q.nonVacuity = false) :
    ∃ (v : VE.Bridge.Vocabulary) (fs : List VE.Core.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
      (result : Metered.Result),
      p.core.get = .ok v ∧
      VE.Core.Bridge.decodeFormulas v.environment q.input = .ok fs ∧
      fs ≠ [] ∧
      VE.Core.Wire.decodeModel v model = .ok M ∧
      EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval M []) := by
  unfold run at h
  simp only [hfam] at h
  obtain ⟨v, hv, h⟩ := bind_ok h
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨M, hM, h⟩ := bind_ok h
  obtain ⟨fs, hfs, hne, rfl⟩ := request_evaluate q _ _ r hq hr
  cases h
  refine ⟨v, fs, M, _, hv, hfs, hne, hM, answer_evaluate q _ fs, ?_⟩
  intro b hb
  exact MeteredProofs.core_sound _ M q.limit (fun p row => Budget.tableMem_iff _ M p row) fs b hb

/-- Order family: the value is the truth in the model as it was submitted (the runner
evaluates a sorted presentation of it, which has the same truths). -/
theorem run_order_sound (q : Query) (checked : VE.Service.Standalone.Validated) (p : Prepared)
    (model answer : Json) (h : run q checked p model = .ok answer)
    (hfam : checked.envelope.family = .order) (hq : q.nonVacuity = false) :
    ∃ (rv : Wire.RouteOrderVocabulary) (fs : List VE.Order.Formula)
      (d : VE.Order.ModelData VE.Order.Wire.Entity) (result : Metered.Result),
      p.order.get = .ok rv ∧
      VE.Order.Wire.decodeFormulas rv.vocabulary.environment q.input = .ok fs ∧
      fs ≠ [] ∧
      Wire.decodeOrderModel rv model = .ok d ∧
      EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval d.toModel []) := by
  unfold run at h
  simp only [hfam] at h
  obtain ⟨rv, hrv, h⟩ := bind_ok h
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨d, hd, h⟩ := bind_ok h
  obtain ⟨fs, hfs, hne, rfl⟩ := request_evaluate q _ _ r hq hr
  cases h
  refine ⟨rv, fs, d, _, hrv, hfs, hne, hd, answer_evaluate q _ fs, ?_⟩
  intro b hb
  rw [MeteredProofs.order_sound _ (Budget.sortOrderData d).toModel q.limit
    (fun p row => Budget.orderMem_iff _ _ p row) fs b hb]
  exact congrArg (fun g => fs.all g) (funext fun f =>
    VE.Time.eval_domains_perm (Budget.sortOrderData d).toModel d.toModel rfl rfl
      (Budget.sortOrderData_perm d) f [])

/-- What an `evaluate-budgeted` answer means, by the family of the case's environment: the
vocabulary, the formulas and the model are what the family's decoders read from the case; the
answer encodes a metered result; a completed value of it is the truth of every formula. -/
def EvaluationAnswer (q : Query) (checked : VE.Service.Standalone.Validated) (p : Prepared)
    (model answer : Json) : Prop :=
  match checked.envelope.family with
  | .fol =>
    ∃ (rv : Wire.RouteVocabulary) (fs : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
      (result : Metered.Result),
      p.route.get = .ok rv ∧
      Wire.decodeFormulas rv.environment q.input (checked.envelope.profiles.contains "data@0") = .ok fs ∧
      fs ≠ [] ∧ Wire.decodeDataModel rv model = .ok M ∧ EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval M [])
  | .closure =>
    ∃ (rv : Wire.RouteVocabulary) (fs : List VE.Closure.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
      (result : Metered.Result),
      p.route.get = .ok rv ∧ VE.Closure.Bridge.decodeFormulas rv.environment q.input = .ok fs ∧
      fs ≠ [] ∧ Wire.decodeDataModel rv model = .ok M ∧ EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval M [])
  | .closureNary =>
    ∃ (v : VE.Bridge.Vocabulary) (fs : List VE.Core.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
      (result : Metered.Result),
      p.core.get = .ok v ∧ VE.Core.Bridge.decodeFormulas v.environment q.input = .ok fs ∧
      fs ≠ [] ∧ VE.Core.Wire.decodeModel v model = .ok M ∧ EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval M [])
  | .order =>
    ∃ (rv : Wire.RouteOrderVocabulary) (fs : List VE.Order.Formula)
      (d : VE.Order.ModelData VE.Order.Wire.Entity) (result : Metered.Result),
      p.order.get = .ok rv ∧ VE.Order.Wire.decodeFormulas rv.vocabulary.environment q.input = .ok fs ∧
      fs ≠ [] ∧ Wire.decodeOrderModel rv model = .ok d ∧ EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval d.toModel [])

theorem run_evaluation_sound (q : Query) (checked : VE.Service.Standalone.Validated) (p : Prepared)
    (model answer : Json) (h : run q checked p model = .ok answer) (hq : q.nonVacuity = false) :
    EvaluationAnswer q checked p model answer := by
  unfold EvaluationAnswer
  cases hfam : checked.envelope.family with
  | fol => exact run_fol_sound q checked p model answer h hfam hq
  | closure => exact run_closure_sound q checked p model answer h hfam hq
  | closureNary => exact run_core_sound q checked p model answer h hfam hq
  | order => exact run_order_sound q checked p model answer h hfam hq

/-- The model a case evaluates: its `model` field, and under a layered core environment that
model with its defined tables added by `Core.Layers.completeModel`. -/
def CaseModel (j : Json) (checked : VE.Service.Standalone.Validated) (p : Prepared) (model : Json) :
    Prop :=
  ∃ given, j.getObjVal? "model" = .ok given ∧
    match checked.layers with
    | some layered => ∃ L, p.layered.get = .ok L ∧
        VE.Core.Layers.completeModel L layered given = .ok model
    | none => model = given

/-- An evaluation query is not a non-vacuity query. -/
theorem query_evaluate (j : Json) (id : String) (q : Query) (h : query j id false = .ok q) :
    q.nonVacuity = false ∧ q.id = id := by
  unfold query at h
  simp only [Bool.false_eq_true, ↓reduceIte] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  exact ⟨rfl, rfl⟩

/-- KB-7, on the runner every entry of the mode calls (`runCaseReported` with the case's own
environment, the service's handle path with a kept `Prepared`): an answer to an
`evaluate-budgeted` case encodes, under the case's id, a metered result over the formulas and
the model that the prepared environment's family decoders read from the case, and a completed
value of that result is the truth of every one of those formulas in that model. -/
theorem runWith_sound (prepared : Except String Prepared) (j answer : Json)
    (h : runWith prepared j = .ok answer)
    (hk : VE.Bridge.stringField j "kind" = .ok "evaluate-budgeted") :
    ∃ (id : String) (p : Prepared) (checked : VE.Service.Standalone.Validated) (model : Json)
      (q : Query),
      VE.Bridge.stringField j "id" = .ok id ∧
      prepared = .ok p ∧
      p.checked = .ok checked ∧
      CaseModel j checked p model ∧
      query j id false = .ok q ∧ q.id = id ∧
      EvaluationAnswer q checked p model answer := by
  unfold runWith at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have hkind' : kind = "evaluate-budgeted" := by rw [hk] at hkind; cases hkind; rfl
  subst hkind'
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨p, hp, h⟩ := bind_ok h
  obtain ⟨checked, hchecked, h⟩ := bind_ok h
  obtain ⟨given, hgiven, h⟩ := bind_ok h
  cases hl : checked.layers with
  | none =>
    simp only [hl] at h
    obtain ⟨model, hmodel, h⟩ := bind_ok h
    cases hmodel
    obtain ⟨q, hq, h⟩ := bind_ok h
    have hq' : query j id false = .ok q := hq
    obtain ⟨hnv, hqid⟩ := query_evaluate j id q hq'
    refine ⟨id, p, checked, given, q, hid, hp, hchecked, ⟨given, hgiven, ?_⟩, hq', hqid,
      run_evaluation_sound q checked p given answer h hnv⟩
    rw [hl]
  | some layered =>
    simp only [hl] at h
    obtain ⟨L, hL, h⟩ := bind_ok h
    obtain ⟨model, hmodel, h⟩ := bind_ok h
    obtain ⟨q, hq, h⟩ := bind_ok h
    have hq' : query j id false = .ok q := hq
    obtain ⟨hnv, hqid⟩ := query_evaluate j id q hq'
    refine ⟨id, p, checked, model, q, hid, hp, hchecked, ⟨given, hgiven, ?_⟩, hq', hqid,
      run_evaluation_sound q checked p model answer h hnv⟩
    rw [hl]
    exact ⟨L, hL, hmodel⟩

/-- KB-7, for a case answered with its own environment (`runCase`): the prepared environment
is `prepare` of the case's `environment` field, which the service's validation accepts. -/
theorem metered_wire_sound (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Bridge.stringField j "kind" = .ok "evaluate-budgeted") :
    ∃ (id : String) (environment : Json) (checked : VE.Service.Standalone.Validated) (model : Json)
      (q : Query),
      VE.Bridge.stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok environment ∧
      VE.Service.Standalone.evaluable environment = .ok checked ∧
      CaseModel j checked (prepare environment) model ∧
      query j id false = .ok q ∧ q.id = id ∧
      EvaluationAnswer q checked (prepare environment) model answer := by
  obtain ⟨id, p, checked, model, q, hid, hp, hchecked, hmodel, hq, hqid, hs⟩ :=
    runWith_sound _ j answer h hk
  cases henv : j.getObjVal? "environment" with
  | error e => rw [henv] at hp; cases hp
  | ok environment =>
    rw [henv] at hp
    cases hp
    exact ⟨id, environment, checked, model, q, hid, rfl, hchecked, hmodel, hq, hqid, hs⟩

/-- The mode's entry answers with the runner's answer whenever the runner accepts. -/
theorem reportedWith_ok (prepared : Except String Prepared) (j answer : Json)
    (h : runWith prepared j = .ok answer) : reportedWith prepared j = answer := by
  simp [reportedWith, h]

end VE.Route.MeteredRun
