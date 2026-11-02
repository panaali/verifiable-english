import VE.Scope.Theorems

/-! SC-4's statements (docs/spec/scope.md 5.6): a graph governor that adds no edge is refused (`no_effect_refused`),
    and a forward declaration is admitted exactly when a later unit of its anchor has a base rule whose `over` names
    its rule (`forward_exception_sound`, `forward_exception_complete`). The check is `admitBlock`'s step 9
    (`forwardsOk`, `Govern.lean`), so every statement whose hypothesis is an admitted block covers it unchanged. -/

namespace VE.Scope
open Lean
open VE.SoftNorms (SoftNode)

theorem mapM_ok_all {α β ε : Type} (f : α → Except ε β) :
    ∀ l : List α, (∀ x ∈ l, (f x).isOk = true) → ∃ ys, l.mapM f = .ok ys
  | [], _ => ⟨[], rfl⟩
  | x :: l, h => by
    cases hx : f x with
    | error e => have := h x List.mem_cons_self; rw [hx] at this; cases this
    | ok y =>
      obtain ⟨ys, hys⟩ := mapM_ok_all f l fun z hz => h z (List.mem_cons_of_mem x hz)
      exact ⟨y :: ys, by simp [List.mapM_cons, hx, hys, bind, Except.bind, pure, Except.pure]⟩

theorem noEffect_prefix (a : String) : (toString "ScopeNoEffect: " ++ toString a).startsWith "ScopeNoEffect" = true := by
  have := VE.Readings.startsWith_append_ascii "ScopeNoEffect" (": " ++ a) (by decide)
  simpa only [toString, String.append_assoc] using this

theorem no_effect_refused (D : SDoc) (h₀ : admitBlock D = .ok ()) (h₁ : orderCheck D = .ok ())
    (hc : ∀ u ∈ affected D, (composed D u).isOk = true) (t : List (String × SoftNode)) (ht : ruleTable D = .ok t)
    (g : Governor) (hg : g ∈ D.governors) (hgr : graph g.effect = true) (he : edgesOf D (fun v => t.lookup v) g = []) :
    ∃ e, govern D = .error e ∧ e.startsWith "ScopeNoEffect" = true := by
  have hne : D.governors.isEmpty = false := by
    cases h : D.governors with
    | nil => rw [h] at hg; cases hg
    | cons => rfl
  obtain ⟨comp, hcomp⟩ := mapM_ok_all (fun u => do pure (u, ← composed D u)) (affected D) fun u hu => by
    have := hc u hu
    cases h : composed D u with
    | error e => rw [h] at this; cases this
    | ok o => show (composed D u >>= fun x => pure (u, x)).isOk = true; rw [h]; rfl
  have hgo : g ∈ (ordered D).filter (graph ·.effect) := List.mem_filter.mpr ⟨List.mem_mergeSort.mpr hg, hgr⟩
  simp only [bind, Except.bind] at hcomp
  simp only [govern, h₀, hne, h₁, hcomp, ht, bind, Except.bind, Bool.false_eq_true, ↓reduceIte]
  split
  · next e heq =>
    refine ⟨e, rfl, forIn_error (fun e => e.startsWith "ScopeNoEffect" = true) _ (fun x e hx => ?_) _ e heq⟩
    revert hx
    repeat' split
    all_goals intro hx
    all_goals first
      | (cases hx; done)
      | (rename_i hh; cases hh; done)
      | (cases hx; exact noEffect_prefix _)
  · next v heq =>
    cases v
    have hall := (VE.NormDefaults.forIn_unit_ok _ ?_ _).mp heq
    · have := hall g hgo
      simp [he] at this
    · intro x r hx
      revert hx
      repeat' split
      all_goals intro hx
      all_goals first
        | (cases hx; done)
        | (cases hx; rfl)

theorem forward_exception_sound (D : SDoc) (w r a : String) (h : forwardCheck D w r a = .ok ()) :
    ∃ x o N, x ∈ laterUnitsIn D a w ∧ baseObj D x = .ok o ∧ VE.Readings.Wire.decodeNorm D.re o = .ok N ∧
      r ∈ N.over := by
  unfold forwardCheck at h
  split at h
  · next hany =>
    obtain ⟨x, hx, hp⟩ := List.any_eq_true.mp hany
    cases ho : baseObj D x with
    | error _ => simp [ho, Except.toOption] at hp
    | ok o =>
      cases hN : VE.Readings.Wire.decodeNorm D.re o with
      | error _ => simp [ho, hN, Except.toOption] at hp
      | ok N => exact ⟨x, o, N, hx, ho, hN, by simpa [ho, hN, Except.toOption] using hp⟩
  · cases h

theorem forward_exception_complete (D : SDoc) (w r a : String) (x : String) (o : Json) (N : SoftNode)
    (hx : x ∈ laterUnitsIn D a w) (ho : baseObj D x = .ok o) (hN : VE.Readings.Wire.decodeNorm D.re o = .ok N)
    (hr : r ∈ N.over) : forwardCheck D w r a = .ok () := by
  unfold forwardCheck
  rw [if_pos (List.any_eq_true.mpr ⟨x, hx, by simp [ho, hN, Except.toOption, hr]⟩)]

end VE.Scope
