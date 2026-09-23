import VE.Order.Gate

/-! A general profile gate for every JSON entry point. `Gate.lean` checks two
exact envelopes; here every envelope is covered. Decoding an environment
succeeds only if its declared profiles are exactly the closure list (language
`ve.core@0.1`) or it is a v0 environment (language `ve.core@0`, singular
`profile` = `relational-fol@0`) with no `profiles` field at all. Consequently
no envelope that declares `order@0` passes any current decoder, on either the
certificate route or the evaluation route, whatever its `language` field. -/
namespace VE.Order
open Lean

def closureProfiles : List String := ["closure@0", "relational-fol@0"]

/-- The accepted profile declarations of an environment object. -/
def ProfilesAccepted (env : Json) : Prop :=
  (VE.Bridge.stringField env "language" = .ok "ve.core@0.1" ∧
    (env.getObjVal? "profiles" >>= VE.Bridge.strings) = .ok closureProfiles ∧
    ∀ p, env.getObjVal? "profile" ≠ .ok p) ∨
  (VE.Bridge.stringField env "language" = .ok "ve.core@0" ∧
    VE.Bridge.stringField env "profile" = .ok "relational-fol@0" ∧
    ∀ p, env.getObjVal? "profiles" ≠ .ok p)

/-- The evaluation-route dispatch on `language` used by `ve_conformance`. -/
def runEvaluationCase (j : Json) : Except String Json :=
  if (j.getObjValD "environment").getObjValD "language" == .str "ve.core@0.1"
  then VE.Closure.Bridge.runCase j else VE.Bridge.runCase j

def runEvaluationCaseReported (j : Json) : Json :=
  match runEvaluationCase j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"),
      ("status", .str "error"), ("error", .str message)]

namespace ProfileGate

theorem bind_ok {ε α β : Type} {x : Except ε α} {f : α → Except ε β} {b : β}
    (h : (x >>= f) = .ok b) : ∃ a, x = .ok a ∧ f a = .ok b := by
  cases x with
  | error e => cases h
  | ok a => exact ⟨a, rfl, h⟩

/-- A duplicate-free list contained in another is no longer than it. -/
theorem nodup_length_le {a l : List String} (hn : a.Nodup) (hs : ∀ x ∈ a, x ∈ l) :
    a.length ≤ l.length := by
  induction a generalizing l with
  | nil => simp
  | cons y a ih =>
    have hy : y ∈ l := hs y (List.mem_cons_self ..)
    have hn' := List.nodup_cons.mp hn
    have hle := ih (l := l.erase y) hn'.2 (fun x hx => by
      have hne : x ≠ y := fun h => hn'.1 (h ▸ hx)
      exact (List.mem_erase_of_ne hne).mpr (hs x (List.mem_cons_of_mem _ hx)))
    rw [List.length_erase_of_mem hy] at hle
    have : 0 < l.length := List.length_pos_of_mem hy
    simp only [List.length_cons]
    omega

/-- `exactFields` admits no key outside the expected (duplicate-free) list,
even for raw JSON objects whose trees contain repeated keys. -/
theorem exactFields_keys {j : Json} {expected : List String} {u : Unit}
    (hn : expected.Nodup) (h : VE.Bridge.exactFields j expected = .ok u) :
    ∃ fs, VE.Bridge.fields j = .ok fs ∧ ∀ k ∈ fs.map Prod.fst, k ∈ expected := by
  unfold VE.Bridge.exactFields at h
  obtain ⟨fs, hfs, h⟩ := bind_ok h
  refine ⟨fs, hfs, fun k hk => ?_⟩
  dsimp only at h
  split at h
  · rename_i hc
    simp only [Bool.and_eq_true, beq_iff_eq, List.all_eq_true, List.contains_iff_mem] at hc
    by_cases hk' : k ∈ expected
    · exact hk'
    have hle := nodup_length_le (a := k :: expected) (l := fs.map Prod.fst)
      (List.nodup_cons.mpr ⟨hk', hn⟩) (fun x hx => by
        rcases List.mem_cons.mp hx with rfl | hx
        · exact hk
        · exact hc.2 x hx)
    simp only [List.length_cons] at hle
    omega
  · cases h

open Std.DTreeMap.Internal in
theorem impl_get_mem {t : Impl String (fun _ => Json)} {k : String} {v : Json}
    (h : Impl.Const.get? t k = some v) : (k, v) ∈ Impl.Const.toList t := by
  rw [Impl.Const.toList_eq_toListModel_map]
  induction t with
  | leaf => simp [Impl.Const.get?] at h
  | inner sz k' v' l r il ir =>
    simp only [Impl.Const.get?] at h
    split at h
    · simp [il h]
    · simp [ir h]
    · rename_i hc
      cases h
      have := Std.LawfulEqOrd.eq_of_compare hc
      subst this
      simp

/-- Any key found by lookup is listed by `fields`, for every (raw) object. -/
theorem getObjVal_mem {j : Json} {k : String} {v : Json} (h : j.getObjVal? k = .ok v) :
    ∃ fs, VE.Bridge.fields j = .ok fs ∧ k ∈ fs.map Prod.fst := by
  cases j with
  | obj kvs =>
    simp only [Json.getObjVal?] at h
    split at h
    · rename_i w hw
      cases h
      have := impl_get_mem (t := kvs.inner.inner) hw
      exact ⟨_, rfl, List.mem_map.mpr ⟨(k, v), this, rfl⟩⟩
    · cases h
  | _ => simp [Json.getObjVal?] at h <;> cases h

end ProfileGate
open ProfileGate

/-- The closure decoder succeeds only on language `ve.core@0.1` with exactly
the declared profile list `["closure@0", "relational-fol@0"]` and no singular
`profile` field. -/
theorem closure_decode_profiles (env : Json) (v : VE.Bridge.Vocabulary)
    (h : VE.Closure.Bridge.decodeEnvironment env = .ok v) :
    VE.Bridge.stringField env "language" = .ok "ve.core@0.1" ∧
    (env.getObjVal? "profiles" >>= VE.Bridge.strings) = .ok closureProfiles ∧
    ∀ p, env.getObjVal? "profile" ≠ .ok p := by
  unfold VE.Closure.Bridge.decodeEnvironment at h
  obtain ⟨_, hx, h⟩ := bind_ok h
  obtain ⟨l, hl, h⟩ := bind_ok h
  obtain ⟨pj, hpj, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  obtain ⟨sr, _, h⟩ := bind_ok h
  dsimp only at h
  split at h
  · rename_i hc
    simp only [Bool.and_eq_true, beq_iff_eq] at hc
    obtain ⟨⟨rfl, rfl⟩, _⟩ := hc
    refine ⟨hl, by simp [hpj, bind, Except.bind, hps, closureProfiles], fun p hp => ?_⟩
    obtain ⟨fs, hfs, hk⟩ := exactFields_keys (by decide) hx
    obtain ⟨fs', hfs', hp'⟩ := getObjVal_mem hp
    rw [hfs] at hfs'
    cases hfs'
    have := hk _ hp'
    simp at this
  · cases h

/-- The v0 decoder succeeds only on language `ve.core@0` with singular profile
`relational-fol@0` and no `profiles` field. -/
theorem v0_decode_profiles (env : Json) (v : VE.Bridge.Vocabulary)
    (h : VE.Bridge.decodeEnvironment env = .ok v) :
    VE.Bridge.stringField env "language" = .ok "ve.core@0" ∧
    VE.Bridge.stringField env "profile" = .ok "relational-fol@0" ∧
    ∀ p, env.getObjVal? "profiles" ≠ .ok p := by
  unfold VE.Bridge.decodeEnvironment at h
  obtain ⟨_, hx, h⟩ := bind_ok h
  obtain ⟨l, hl, h⟩ := bind_ok h
  obtain ⟨pr, hpr, h⟩ := bind_ok h
  obtain ⟨sr, _, h⟩ := bind_ok h
  dsimp only at h
  split at h
  · rename_i hc
    simp only [Bool.and_eq_true, beq_iff_eq] at hc
    obtain ⟨⟨rfl, rfl⟩, _⟩ := hc
    refine ⟨hl, hpr, fun p hp => ?_⟩
    obtain ⟨fs, hfs, hk⟩ := exactFields_keys (by decide) hx
    obtain ⟨fs', hfs', hp'⟩ := getObjVal_mem hp
    rw [hfs] at hfs'
    cases hfs'
    have := hk _ hp'
    simp at this
  · cases h

theorem decode_profiles_accepted (env : Json) (v : VE.Bridge.Vocabulary)
    (h : VE.Closure.Bridge.decodeEnvironment env = .ok v ∨
      VE.Bridge.decodeEnvironment env = .ok v) : ProfilesAccepted env := by
  rcases h with h | h
  · exact Or.inl (closure_decode_profiles env v h)
  · exact Or.inr (v0_decode_profiles env v h)

theorem v0_runCase_profiles (j r : Json) (h : VE.Bridge.runCase j = .ok r) :
    ∃ env, j.getObjVal? "environment" = .ok env ∧ ProfilesAccepted env := by
  unfold VE.Bridge.runCase at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨env, he, h⟩ := bind_ok h
  obtain ⟨v, hv, _⟩ := bind_ok h
  exact ⟨env, he, decode_profiles_accepted env v (Or.inr hv)⟩

theorem closure_runCase_profiles (j r : Json) (h : VE.Closure.Bridge.runCase j = .ok r) :
    ∃ env, j.getObjVal? "environment" = .ok env ∧ ProfilesAccepted env := by
  unfold VE.Closure.Bridge.runCase at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨env, he, h⟩ := bind_ok h
  obtain ⟨v, hv, _⟩ := bind_ok h
  exact ⟨env, he, decode_profiles_accepted env v (Or.inl hv)⟩

theorem certificate_runCase_profiles (j r : Json)
    (h : VE.CertificateWire.runCase j = .ok r) :
    ∃ env, j.getObjVal? "environment" = .ok env ∧ ProfilesAccepted env := by
  unfold VE.CertificateWire.runCase at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨env, he, h⟩ := bind_ok h
  refine ⟨env, he, ?_⟩
  dsimp only at h
  split at h
  · obtain ⟨r', hr, _⟩ := bind_ok h
    unfold VE.CertificateWire.runClosureCase at hr
    obtain ⟨_, _, hr⟩ := bind_ok hr
    obtain ⟨env', he', hr⟩ := bind_ok hr
    rw [he] at he'
    cases he'
    obtain ⟨v, hv, _⟩ := bind_ok hr
    exact decode_profiles_accepted env v (Or.inl hv)
  · obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨v, hv, _⟩ := bind_ok h
    exact decode_profiles_accepted env v (Or.inr hv)

/-- General profile gate. For every JSON case on either route, and whichever
branch the `language` dispatch takes, success implies the case's environment
declares exactly one accepted profile list: the closure list, or the v0 form
with no `profiles` field. -/
theorem profile_gate (j r : Json)
    (h : VE.CertificateWire.runCase j = .ok r ∨ runEvaluationCase j = .ok r) :
    ∃ env, j.getObjVal? "environment" = .ok env ∧ ProfilesAccepted env := by
  rcases h with h | h
  · exact certificate_runCase_profiles j r h
  · unfold runEvaluationCase at h
    split at h
    · exact closure_runCase_profiles j r h
    · exact v0_runCase_profiles j r h

/-- An environment whose declared profiles mention `order@0` is never accepted. -/
theorem order_not_accepted (env : Json) (ps : List String)
    (hp : (env.getObjVal? "profiles" >>= VE.Bridge.strings) = .ok ps)
    (ho : "order@0" ∈ ps) : ¬ ProfilesAccepted env := by
  rintro (⟨_, hc, _⟩ | ⟨_, _, hn⟩)
  · rw [hc] at hp
    cases hp
    simp [closureProfiles] at ho
  · obtain ⟨pj, hpj, _⟩ := bind_ok hp
    exact hn pj hpj

/-- A singular `"profile": "order@0"` field is never accepted either, whatever
the language: the closure form has no `profile` field and the v0 form requires
`relational-fol@0`. -/
theorem singular_order_not_accepted (env : Json)
    (hp : env.getObjVal? "profile" = .ok (.str "order@0")) : ¬ ProfilesAccepted env := by
  rintro (⟨_, _, hn⟩ | ⟨_, hr, _⟩)
  · exact hn _ hp
  · simp [VE.Bridge.stringField, hp, bind, Except.bind, Json.getStr?] at hr
    have := congrArg (fun x : Except String String => match x with | .ok s => s | .error _ => "") hr
    exact absurd this (by decide)

theorem singular_order_profile_gate (j r env : Json)
    (he : j.getObjVal? "environment" = .ok env)
    (hp : env.getObjVal? "profile" = .ok (.str "order@0")) :
    VE.CertificateWire.runCase j ≠ .ok r ∧ runEvaluationCase j ≠ .ok r := by
  constructor <;> intro h
  · obtain ⟨env', he', ha⟩ := profile_gate j r (Or.inl h)
    rw [he] at he'; cases he'
    exact singular_order_not_accepted env hp ha
  · obtain ⟨env', he', ha⟩ := profile_gate j r (Or.inr h)
    rw [he] at he'; cases he'
    exact singular_order_not_accepted env hp ha

/-- Therefore no case whose environment declares `order@0` succeeds, on either
route, for any other field values. -/
theorem order_profile_gate (j r env : Json) (ps : List String)
    (he : j.getObjVal? "environment" = .ok env)
    (hp : (env.getObjVal? "profiles" >>= VE.Bridge.strings) = .ok ps)
    (ho : "order@0" ∈ ps) :
    VE.CertificateWire.runCase j ≠ .ok r ∧ runEvaluationCase j ≠ .ok r := by
  constructor <;> intro h
  · obtain ⟨env', he', ha⟩ := profile_gate j r (Or.inl h)
    rw [he] at he'; cases he'
    exact order_not_accepted env ps hp ho ha
  · obtain ⟨env', he', ha⟩ := profile_gate j r (Or.inr h)
    rw [he] at he'; cases he'
    exact order_not_accepted env ps hp ho ha

end VE.Order

namespace VE.Order
/-- The binary's evaluation route is unchanged by routing it through
`runEvaluationCaseReported`: it is the previous inline dispatch. -/
theorem runEvaluationCaseReported_eq (j : Lean.Json) :
    runEvaluationCaseReported j =
      if (j.getObjValD "environment").getObjValD "language" == .str "ve.core@0.1"
      then VE.Closure.Bridge.runCaseReported j else VE.Bridge.runCaseReported j := by
  unfold runEvaluationCaseReported runEvaluationCase
  by_cases h : ((j.getObjValD "environment").getObjValD "language" ==
      Lean.Json.str "ve.core@0.1") = true
  · simp only [h, if_true]; rfl
  · simp only [h]; rfl
end VE.Order
