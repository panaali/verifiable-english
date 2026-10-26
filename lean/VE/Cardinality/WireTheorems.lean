import VE.Cardinality.Wire

/-! What the `ve-cardinality@1` decoders establish (docs/spec/quantities.md 4.1–4.3), apart from their fixtures, so
a seeded bug in a decoder is caught by `VE.Cardinality.WireExamples`' guards as well as here. -/
namespace VE.Cardinality.Wire
open Lean
open VE.Order.ProfileGate (bind_ok)

/-- E2's lists project onto W6a's own: an environment past E2 meets W6a's profile check at E4. -/
theorem profileLists_projected {ps : List String} (h : ps ∈ profileLists) :
    ps.filter (· != "cardinality@0") ∈ VE.Time.Wire.w6Profiles := by
  simp only [profileLists, List.mem_map] at h
  obtain ⟨l, hl, rfl⟩ := h
  simp only [VE.Time.Wire.w6Profiles, List.mem_cons, List.not_mem_nil, or_false] at hl
  rcases hl with rfl | rfl <;> decide

/-- E6: at most 64 finite sorts are declared. -/
theorem finiteSorts_length {env : Json} {xs : List String} (h : finiteSorts env = .ok xs) :
    xs.length ≤ maxFiniteSorts := by
  unfold finiteSorts at h
  split at h
  · simp only [bind, Except.bind] at h
    split at h
    · cases h
    · cases h; omega
  · cases h

/-- What the environment decoder establishes (spec 4.1, 4.3): its identity is the original environment's, under a
profile list E2 admits; `w6` is W6a's decoding of the projection; and the cardinality environment is W6a's vocabulary
with the declared finite sorts. -/
theorem decodeEnvironment_sound {env : Json} {w : CardEnv} (h : decodeEnvironment env = .ok w) :
    (∃ ps, ps ∈ profileLists ∧ VE.Route.Wire.environmentId ps env = .ok w.environmentId) ∧
    (∃ j, projectW6 env = .ok j ∧ VE.Time.Wire.decodeEnvironment j = .ok w.w6) ∧
    ∃ finite, finiteSorts env = .ok finite ∧ w.env = ⟨w.w6.vocab.env, finite⟩ := by
  unfold decodeEnvironment at h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨ps, -, h⟩ := bind_ok h
  simp only at h
  split at h
  case isFalse => cases h
  rename_i hps
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  split at h
  case isFalse => cases h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨j, hj, h⟩ := bind_ok h
  obtain ⟨w6, hw6, h⟩ := bind_ok h
  obtain ⟨finite, hf, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨id, hid, h⟩ := bind_ok h
  split at h
  case isFalse => cases h
  cases h
  exact ⟨⟨ps, List.contains_iff_mem.mp hps, hid⟩, ⟨j, hj, hw6⟩, finite, hf, rfl⟩

/-- A decoded statement's meaning id is over the canonical object of the admitted formula, in the cardinality
environment's identity. -/
theorem decodeStatement_identity {w : CardEnv} {j : Json} {a : CAdmission w} (h : decodeStatement w j = .ok a) :
    VE.Route.Wire.meaningId w.profiles w.environmentId (canonical a.formula) = .ok a.meaningId := by
  unfold decodeStatement at h
  simp only at h
  split at h
  case isFalse => cases h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  split at h
  · cases h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨f, -, h⟩ := bind_ok h
  split at h
  case isFalse => cases h
  obtain ⟨m, hm, h⟩ := bind_ok h
  cases h
  exact hm

end VE.Cardinality.Wire
