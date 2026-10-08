import VE.Route.Run
import VE.Route.WireSound
import VE.Norms.FlaggedSpec

/-! The claims of `VE.Route.WireSound` at the public entry `Route.Run.runCase`
(docs/CONSOLIDATION-PLAN.md step 2a, item 4). A case whose envelope decodes to
the FOL, closure or order family and whose kind is `certificate`,
`countermodel` or `evaluate` is answered by `Wire.runFol`, `Wire.runClosure` or
`Wire.runOrder` on the vocabulary decoded from that envelope
(`dispatch_fol`, `dispatch_closure`, `dispatch_order`); each family then has one
corollary per kind: the certificate one read off the answer's `valid` field, the
countermodel and evaluate ones stating what its `refutes` and `values` fields mean.
The FOL and closure certificate corollaries also carry `BaseClaim` through the
composed layer `fullLayer`, whose decoder fact `FlagsBase` (no flag names a
defined predicate) is `Norms.FlaggedSpec.decodeVocabulary_flag_not_defined`.
The `closureNary` family (`Core.Wire.run`, `Core.Layers.run`) is not covered
here (plan step 5a). -/
namespace VE.Route.RunSound
open Lean
open VE.Route.Wire
open VE.Route.WireSound
open VE.Order.ProfileGate (bind_ok)
universe u

/-- Every successful case decodes its `id` and gated envelope, then dispatches. -/
theorem runCase_dispatch (j out : Json) (h : Run.runCase j = .ok out) :
    ∃ id e, VE.Bridge.stringField j "id" = .ok id ∧
      Gate.decodeEnvelope (j.getObjValD "environment") = .ok e ∧
      Run.dispatch id (j.getObjValD "environment") e j = .ok out := by
  unfold Run.runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨e, he, h⟩ := bind_ok h
  rw [← getObjValD_of_ok henv] at he h
  exact ⟨id, e, hid, he, h⟩

/-- The three kinds the family runners answer. -/
def RunnerKind (k : String) : Prop := k = "certificate" ∨ k = "countermodel" ∨ k = "evaluate"

theorem runnerKind_ne {k : String} (hk : RunnerKind k) :
    (k == "dependency-order") = false ∧ (k == "label") = false ∧ (k == "admission") = false ∧
      (k == "background") = false ∧ (k == "bundle") = false := by
  rcases hk with rfl | rfl | rfl <;> exact ⟨rfl, rfl, rfl, rfl, rfl⟩

/-- On the FOL family the three kinds are answered by `runFol`. -/
theorem dispatch_fol (id : String) (environment : Json) (e : Gate.Envelope) (j out : Json)
    (k : String) (hk : Run.caseKind j = .ok k) (hr : RunnerKind k) (hf : e.family = .fol)
    (h : Run.dispatch id environment e j = .ok out) :
    ∃ rv, Run.decodeRouteVocabulary e = .ok rv ∧ runFol e.profiles environment rv id k j = .ok out := by
  obtain ⟨h1, h2, h3, h4, h5⟩ := runnerKind_ne hr
  unfold Run.dispatch at h
  rw [hk] at h
  simp only [bind, Except.bind, h1, h2, Bool.false_eq_true, ↓reduceIte, hf] at h
  obtain ⟨rv, hrv, h⟩ := bind_ok h
  simp only [h3, h4, h5, Bool.false_eq_true, ↓reduceIte] at h
  exact ⟨rv, hrv, h⟩

/-- On the closure family the three kinds are answered by `runClosure`. -/
theorem dispatch_closure (id : String) (environment : Json) (e : Gate.Envelope) (j out : Json)
    (k : String) (hk : Run.caseKind j = .ok k) (hr : RunnerKind k) (hf : e.family = .closure)
    (h : Run.dispatch id environment e j = .ok out) :
    ∃ rv, Run.decodeRouteVocabulary e = .ok rv ∧
      runClosure e.profiles environment rv id k j = .ok out := by
  obtain ⟨h1, h2, h3, h4, h5⟩ := runnerKind_ne hr
  unfold Run.dispatch at h
  rw [hk] at h
  simp only [bind, Except.bind, h1, h2, h3, h5, Bool.false_eq_true, ↓reduceIte, hf] at h
  obtain ⟨rv, hrv, h⟩ := bind_ok h
  simp only [h4, Bool.false_eq_true, ↓reduceIte] at h
  exact ⟨rv, hrv, h⟩

/-- On the order family the three kinds are answered by `runOrder`. -/
theorem dispatch_order (id : String) (environment : Json) (e : Gate.Envelope) (j out : Json)
    (k : String) (hk : Run.caseKind j = .ok k) (hr : RunnerKind k) (hf : e.family = .order)
    (h : Run.dispatch id environment e j = .ok out) :
    ∃ rv, decodeOrderVocabulary e.vocabulary = .ok rv ∧
      runOrder e.profiles environment rv id k j = .ok out := by
  obtain ⟨h1, h2, h3, h4, _⟩ := runnerKind_ne hr
  unfold Run.dispatch at h
  rw [hk] at h
  simp only [bind, Except.bind, h1, h2, h3, Bool.false_eq_true, ↓reduceIte, hf] at h
  obtain ⟨rv, hrv, h⟩ := bind_ok h
  simp only [h4, Bool.false_eq_true, ↓reduceIte] at h
  exact ⟨rv, hrv, h⟩

/-- The route's vocabulary decoder keeps flags off the defined predicates. -/
theorem decodeRouteVocabulary_flagsBase (e : Gate.Envelope) (rv : RouteVocabulary)
    (h : Run.decodeRouteVocabulary e = .ok rv) : FlagsBase rv := by
  unfold Run.decodeRouteVocabulary Typed.routeVocabulary at h
  obtain ⟨rv', hrv, h⟩ := bind_ok h
  split at h
  · cases h
    exact VE.Norms.FlaggedSpec.decodeVocabulary_flag_not_defined _ _ _ hrv
  · cases h

/-! ## FOL -/

/-- A FOL `certificate` case answered `"valid": true` at the public entry:
the vocabulary decodes, the certificate is bound, the decoded conclusion holds
in every intended structure satisfying the decoded premises, and (for premises
and conclusion without defined predicates) in every `BaseAdmissible` structure
satisfying them. -/
theorem route_fol_certificate (j out : Json) (h : Run.runCase j = .ok out)
    (hk : Run.caseKind j = .ok "certificate") (e : Gate.Envelope)
    (he : Gate.decodeEnvelope (j.getObjValD "environment") = .ok e) (hf : e.family = .fol)
    (hv : out.getObjValD "valid" = .bool true) :
    ∃ rv, Run.decodeRouteVocabulary e = .ok rv ∧ ∃ hb : FlagsBase rv,
      (∃ cert, VE.CertificateWire.decodeCertificate (j.getObjValD "certificate") = .ok cert ∧
        folRunner.{u}.Bound e.profiles (j.getObjValD "environment") rv j cert) ∧
      CertificateClaim folFamily.{u} rv j ∧ BaseClaim folFamily.{u} rv hb j := by
  obtain ⟨id, e', _, he', hd⟩ := runCase_dispatch j out h
  rw [he] at he'
  cases he'
  obtain ⟨rv, hrv, hrun⟩ := dispatch_fol id _ e j out _ hk (Or.inl rfl) hf hd
  have hb := decodeRouteVocabulary_flagsBase e rv hrv
  exact ⟨rv, hrv, hb, runFol_certificate_acceptance _ _ rv hb id j out hrun hv⟩

/-- A FOL `countermodel` case at the public entry: `refutes` is `true` exactly
when the decoded, intended model refutes the decoded premises and conclusion
(`countermodelAnswer_refutes` gives the refuting case). -/
theorem route_fol_countermodel (j out : Json) (h : Run.runCase j = .ok out)
    (hk : Run.caseKind j = .ok "countermodel") (e : Gate.Envelope)
    (he : Gate.decodeEnvelope (j.getObjValD "environment") = .ok e) (hf : e.family = .fol) :
    ∃ rv, Run.decodeRouteVocabulary e = .ok rv ∧ CountermodelAnswer folFamily routeModel rv j out := by
  obtain ⟨id, e', _, he', hd⟩ := runCase_dispatch j out h
  rw [he] at he'
  cases he'
  obtain ⟨rv, hrv, hrun⟩ := dispatch_fol id _ e j out _ hk (Or.inr (Or.inl rfl)) hf hd
  exact ⟨rv, hrv, runFol_countermodel _ _ rv id j out hrun⟩

/-- A FOL `evaluate` case at the public entry. -/
theorem route_fol_evaluate (j out : Json) (h : Run.runCase j = .ok out)
    (hk : Run.caseKind j = .ok "evaluate") (e : Gate.Envelope)
    (he : Gate.decodeEnvelope (j.getObjValD "environment") = .ok e) (hf : e.family = .fol) :
    ∃ rv, Run.decodeRouteVocabulary e = .ok rv ∧ EvaluateClaim folFamily routeModel rv j out := by
  obtain ⟨id, e', _, he', hd⟩ := runCase_dispatch j out h
  rw [he] at he'
  cases he'
  obtain ⟨rv, hrv, hrun⟩ := dispatch_fol id _ e j out _ hk (Or.inr (Or.inr rfl)) hf hd
  exact ⟨rv, hrv, runFol_evaluate _ _ rv id j out hrun⟩

/-! ## Closure -/

/-- A closure `certificate` case answered `"valid": true` at the public entry. -/
theorem route_closure_certificate (j out : Json) (h : Run.runCase j = .ok out)
    (hk : Run.caseKind j = .ok "certificate") (e : Gate.Envelope)
    (he : Gate.decodeEnvelope (j.getObjValD "environment") = .ok e) (hf : e.family = .closure)
    (hv : out.getObjValD "valid" = .bool true) :
    ∃ rv, Run.decodeRouteVocabulary e = .ok rv ∧ ∃ hb : FlagsBase rv,
      (∃ cert, VE.CertificateWire.decodeClosureCertificate (j.getObjValD "certificate") = .ok cert ∧
        closureRunner.{u}.Bound e.profiles (j.getObjValD "environment") rv j cert) ∧
      CertificateClaim closureFamily.{u} rv j ∧ BaseClaim closureFamily.{u} rv hb j := by
  obtain ⟨id, e', _, he', hd⟩ := runCase_dispatch j out h
  rw [he] at he'
  cases he'
  obtain ⟨rv, hrv, hrun⟩ := dispatch_closure id _ e j out _ hk (Or.inl rfl) hf hd
  have hb := decodeRouteVocabulary_flagsBase e rv hrv
  exact ⟨rv, hrv, hb, runClosure_certificate_acceptance _ _ rv hb id j out hrun hv⟩

/-- A closure `countermodel` case at the public entry. -/
theorem route_closure_countermodel (j out : Json) (h : Run.runCase j = .ok out)
    (hk : Run.caseKind j = .ok "countermodel") (e : Gate.Envelope)
    (he : Gate.decodeEnvelope (j.getObjValD "environment") = .ok e) (hf : e.family = .closure) :
    ∃ rv, Run.decodeRouteVocabulary e = .ok rv ∧ CountermodelAnswer closureFamily routeModel rv j out := by
  obtain ⟨id, e', _, he', hd⟩ := runCase_dispatch j out h
  rw [he] at he'
  cases he'
  obtain ⟨rv, hrv, hrun⟩ := dispatch_closure id _ e j out _ hk (Or.inr (Or.inl rfl)) hf hd
  exact ⟨rv, hrv, runClosure_countermodel _ _ rv id j out hrun⟩

/-- A closure `evaluate` case at the public entry. -/
theorem route_closure_evaluate (j out : Json) (h : Run.runCase j = .ok out)
    (hk : Run.caseKind j = .ok "evaluate") (e : Gate.Envelope)
    (he : Gate.decodeEnvelope (j.getObjValD "environment") = .ok e) (hf : e.family = .closure) :
    ∃ rv, Run.decodeRouteVocabulary e = .ok rv ∧ EvaluateClaim closureFamily routeModel rv j out := by
  obtain ⟨id, e', _, he', hd⟩ := runCase_dispatch j out h
  rw [he] at he'
  cases he'
  obtain ⟨rv, hrv, hrun⟩ := dispatch_closure id _ e j out _ hk (Or.inr (Or.inr rfl)) hf hd
  exact ⟨rv, hrv, runClosure_evaluate _ _ rv id j out hrun⟩

/-! ## Order -/

/-- An order `certificate` case answered `"valid": true` at the public entry. -/
theorem route_order_certificate (j out : Json) (h : Run.runCase j = .ok out)
    (hk : Run.caseKind j = .ok "certificate") (e : Gate.Envelope)
    (he : Gate.decodeEnvelope (j.getObjValD "environment") = .ok e) (hf : e.family = .order)
    (hv : out.getObjValD "valid" = .bool true) :
    ∃ rv, decodeOrderVocabulary e.vocabulary = .ok rv ∧
      (∃ cert, VE.Order.Wire.decodeCertificate (j.getObjValD "certificate") = .ok cert ∧
        orderRunner.{u}.Bound e.profiles (j.getObjValD "environment") rv j cert) ∧
      CertificateClaim orderFamily.{u} rv j ∧ BaseClaim orderFamily.{u} rv trivial j := by
  obtain ⟨id, e', _, he', hd⟩ := runCase_dispatch j out h
  rw [he] at he'
  cases he'
  obtain ⟨rv, hrv, hrun⟩ := dispatch_order id _ e j out _ hk (Or.inl rfl) hf hd
  exact ⟨rv, hrv, runOrder_certificate_acceptance _ _ rv id j out hrun hv⟩

/-- An order `countermodel` case at the public entry. -/
theorem route_order_countermodel (j out : Json) (h : Run.runCase j = .ok out)
    (hk : Run.caseKind j = .ok "countermodel") (e : Gate.Envelope)
    (he : Gate.decodeEnvelope (j.getObjValD "environment") = .ok e) (hf : e.family = .order) :
    ∃ rv, decodeOrderVocabulary e.vocabulary = .ok rv ∧ CountermodelAnswer orderFamily orderModel rv j out := by
  obtain ⟨id, e', _, he', hd⟩ := runCase_dispatch j out h
  rw [he] at he'
  cases he'
  obtain ⟨rv, hrv, hrun⟩ := dispatch_order id _ e j out _ hk (Or.inr (Or.inl rfl)) hf hd
  exact ⟨rv, hrv, runOrder_countermodel _ _ rv id j out hrun⟩

/-- An order `evaluate` case at the public entry. -/
theorem route_order_evaluate (j out : Json) (h : Run.runCase j = .ok out)
    (hk : Run.caseKind j = .ok "evaluate") (e : Gate.Envelope)
    (he : Gate.decodeEnvelope (j.getObjValD "environment") = .ok e) (hf : e.family = .order) :
    ∃ rv, decodeOrderVocabulary e.vocabulary = .ok rv ∧ EvaluateClaim orderFamily orderModel rv j out := by
  obtain ⟨id, e', _, he', hd⟩ := runCase_dispatch j out h
  rw [he] at he'
  cases he'
  obtain ⟨rv, hrv, hrun⟩ := dispatch_order id _ e j out _ hk (Or.inr (Or.inr rfl)) hf hd
  exact ⟨rv, hrv, runOrder_evaluate _ _ rv id j out hrun⟩

end VE.Route.RunSound
