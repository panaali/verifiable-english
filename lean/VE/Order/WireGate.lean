import VE.Order.ProfileGate
import VE.Order.Surface

/-! The profile gate for the separate `order` route. The two existing routes
are unchanged, so `profile_gate` and `order_profile_gate` still hold for them:
no envelope declaring order@0 passes the certificate or evaluation route. The
order route succeeds only if the language is `ve.core@0.1` and the declared
profile list is exactly `["order@0", "relational-fol@0"]`. Hence an envelope
declaring both closure@0 and order@0 is rejected by all three routes. -/
namespace VE.Order
open Lean
open ProfileGate

def OrderProfilesAccepted (env : Json) : Prop :=
  VE.Bridge.stringField env "language" = .ok "ve.core@0.1" ∧
    (env.getObjVal? "profiles" >>= VE.Bridge.strings) = .ok Wire.orderProfiles

theorem order_decode_profiles (env : Json) (v : Vocabulary)
    (h : Wire.decodeEnvironment env = .ok v) : OrderProfilesAccepted env := by
  unfold Wire.decodeEnvironment at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨l, hl, h⟩ := bind_ok h
  obtain ⟨pj, hpj, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  obtain ⟨sr, _, h⟩ := bind_ok h
  dsimp only at h
  split at h
  · rename_i hc
    simp only [Bool.and_eq_true, beq_iff_eq] at hc
    obtain ⟨⟨hl', hp'⟩, _⟩ := hc
    subst hl' hp'
    exact ⟨hl, by simp [hpj, bind, Except.bind, hps]⟩
  · cases h

/-- Every successful order-route case declares exactly the order-only list. -/
theorem order_route_gate (j r : Json) (h : Wire.runCase j = .ok r) :
    ∃ env, j.getObjVal? "environment" = .ok env ∧ OrderProfilesAccepted env := by
  unfold Wire.runCase at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨env, he, h⟩ := bind_ok h
  obtain ⟨v, hv, _⟩ := bind_ok h
  exact ⟨env, he, order_decode_profiles env v hv⟩

/-- The executable dispatcher also gates the new surface case. -/
theorem surface_route_gate (j r : Json) (h : Surface.runCase j = .ok r) :
    ∃ env, j.getObjVal? "environment" = .ok env ∧ OrderProfilesAccepted env := by
  unfold Surface.runCase at h
  obtain ⟨_, _, h⟩ := bind_ok h
  split at h
  · exact order_route_gate j r h
  · obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨env, he, h⟩ := bind_ok h
    obtain ⟨v, hv, _⟩ := bind_ok h
    exact ⟨env, he, order_decode_profiles env v hv⟩

/-- closure@0 x order@0 stays rejected: an environment whose declared profiles
contain closure@0 and order@0 fails on every route of `ve_conformance`. -/
theorem combined_profiles_rejected (j r env : Json) (ps : List String)
    (he : j.getObjVal? "environment" = .ok env)
    (hp : (env.getObjVal? "profiles" >>= VE.Bridge.strings) = .ok ps)
    (hc : "closure@0" ∈ ps) (ho : "order@0" ∈ ps) :
    VE.CertificateWire.runCase j ≠ .ok r ∧ runEvaluationCase j ≠ .ok r ∧
      Surface.runCase j ≠ .ok r := by
  obtain ⟨h1, h2⟩ := order_profile_gate j r env ps he hp ho
  refine ⟨h1, h2, fun h => ?_⟩
  obtain ⟨env', he', _, hps⟩ := surface_route_gate j r h
  rw [he] at he'
  cases he'
  rw [hp] at hps
  cases hps
  simp [Wire.orderProfiles] at hc

end VE.Order
