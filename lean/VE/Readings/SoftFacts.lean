import VE.Readings.Lines
import VE.NormDefaults.Check

/-! Facts that a well-formed soft document guarantees, read off the executable checks: every rule name is a
W1 rule name (`[a-z][a-z0-9-]*`), every `over` entry names a rule on the same predicate (both through
`VE.NormDefaults.wellFormed_iff` on `soften D`), and every alterable party of a rule is a declared party whose
name is a soft name (`checkSoftEnv`, `checkSoftRule`). -/
namespace VE.Readings
open VE.SoftNorms (SoftNode SoftDoc soften WellFormedSoft checkSoft checkSoftEnv checkSoftRule validSoftName
  primeNode)
open VE.NormDefaults (ebind_ok ethrow_ok forIn_each)

theorem wellFormedSoft_check (D : SoftDoc) (h : WellFormedSoft D = true) : checkSoft D = .ok () := by
  unfold WellFormedSoft VE.SoftNorms.validateSoft at h
  split at h
  · rename_i heq
    split at heq
    · cases heq
    · rename_i he; exact he
  · cases h

theorem checkSoft_parts (D : SoftDoc) (h : checkSoft D = .ok ()) :
    checkSoftEnv D = .ok () ∧ ∀ N ∈ D.T.nodes, checkSoftRule D N = .ok () := by
  unfold checkSoft at h
  obtain ⟨_, h1, h⟩ := (ebind_ok _ _ _).mp h
  refine ⟨by cases ‹PUnit›; exact h1, ?_⟩
  obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨_, h5, _⟩ := (ebind_ok _ _ _).mp h
  intro N hN
  have := forIn_each _ (fun x t r hr => ?_) _ _ _ h5 N hN
  · obtain ⟨_, _, hc⟩ := this
    obtain ⟨u, hu, _⟩ := (ebind_ok _ _ _).mp hc
    cases u; exact hu
  · obtain ⟨_, _, hr⟩ := (ebind_ok _ _ _).mp hr
    cases hr
    exact ⟨_, rfl⟩

end VE.Readings

namespace VE.Readings
open VE.SoftNorms (SoftNode SoftDoc checkSoftEnv checkSoftRule validSoftName)
open VE.NormDefaults (ebind_ok ethrow_ok forIn_each)

theorem checkSoftEnv_names (D : SoftDoc) (h : checkSoftEnv D = .ok ()) :
    ∀ x ∈ D.soft.ranks ++ D.soft.parties, validSoftName x = true := by
  unfold checkSoftEnv at h
  dsimp only at h
  by_cases c1 : D.soft.parties.length > 8
  · rw [if_pos c1] at h; exact (throw_bind_ok h).elim
  rw [if_neg c1] at h
  obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
  by_cases c2 : D.soft.ranks.length > 16
  · rw [if_pos c2] at h; exact (throw_bind_ok h).elim
  rw [if_neg c2] at h
  obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
  cases c3 : VE.SoftNorms.dupOf D.soft.ranks with
  | some a => rw [c3] at h; exact (throw_bind_ok h).elim
  | none =>
  rw [c3] at h
  obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
  cases c4 : VE.SoftNorms.dupOf D.soft.parties with
  | some a => rw [c4] at h; exact (throw_bind_ok h).elim
  | none =>
  rw [c4] at h
  obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨_, h1, _⟩ := (ebind_ok _ _ _).mp h
  intro x hx
  have := forIn_each _ (fun x t r hr => ?_) _ _ _ h1 x hx
  · obtain ⟨_, _, hc⟩ := this
    split at hc
    · rename_i hv; exact hv
    · exact (throw_bind_ok hc).elim
  · split at hr
    · obtain ⟨_, _, hr⟩ := (ebind_ok _ _ _).mp hr; cases hr; exact ⟨_, rfl⟩
    · exact (throw_bind_ok hr).elim

theorem checkSoftRule_parties (D : SoftDoc) (N : SoftNode) (h : checkSoftRule D N = .ok ()) :
    ∀ π ∈ N.alterable, π ∈ D.soft.parties := by
  unfold checkSoftRule at h
  dsimp only at h
  cases hr : N.rank with
  | some a =>
    rw [hr] at h
    dsimp only at h
    by_cases c : D.soft.ranks.contains a = true
    · rw [if_pos c] at h
      obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
      by_cases c' : VE.SoftNorms.sortedDistinct N.alterable = true
      · rw [if_pos c'] at h
        obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
        obtain ⟨_, h1, _⟩ := (ebind_ok _ _ _).mp h
        intro π hπ
        have := forIn_each _ (fun x t r hr => ?_) _ _ _ h1 π hπ
        · obtain ⟨_, _, hc⟩ := this
          by_cases cc : D.soft.parties.contains π = true
          · simpa using cc
          · rw [if_neg cc] at hc; exact (throw_bind_ok hc).elim
        · by_cases cc : D.soft.parties.contains x = true
          · rw [if_pos cc] at hr
            obtain ⟨_, _, hr⟩ := (ebind_ok _ _ _).mp hr; cases hr; exact ⟨_, rfl⟩
          · rw [if_neg cc] at hr; exact (throw_bind_ok hr).elim
      · rw [if_neg c'] at h; exact (throw_bind_ok h).elim
    · rw [if_neg c] at h; exact (throw_bind_ok h).elim
  | none =>
    rw [hr] at h
    dsimp only at h
    obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
    by_cases c' : VE.SoftNorms.sortedDistinct N.alterable = true
    · rw [if_pos c'] at h
      obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
      obtain ⟨_, h1, _⟩ := (ebind_ok _ _ _).mp h
      intro π hπ
      have := forIn_each _ (fun x t r hr => ?_) _ _ _ h1 π hπ
      · obtain ⟨_, _, hc⟩ := this
        by_cases cc : D.soft.parties.contains π = true
        · simpa using cc
        · rw [if_neg cc] at hc; exact (throw_bind_ok hc).elim
      · by_cases cc : D.soft.parties.contains x = true
        · rw [if_pos cc] at hr
          obtain ⟨_, _, hr⟩ := (ebind_ok _ _ _).mp hr; cases hr; exact ⟨_, rfl⟩
        · rw [if_neg cc] at hr; exact (throw_bind_ok hr).elim
    · rw [if_neg c'] at h; exact (throw_bind_ok h).elim

end VE.Readings
