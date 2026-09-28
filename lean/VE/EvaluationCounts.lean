import VE.Bridge
import VE.Closure.Bridge
import VE.Core.Bridge
import VE.Order.Wire
import VE.Route.Wire

/-! # An evaluation answer has one value per submitted formula

Every evaluation runner (the default mode through `VE.Bridge.runCase` and
`VE.Closure.Bridge.runCase`, `route` through `VE.Route.Wire` and
`VE.Core.Wire`, `order` through `VE.Order.Wire`) decodes the case's `ast`
array with one of the decoders below and answers `values := fs.map eval`. Each
decoder returns exactly one formula per element of the submitted array, so an
`ok` row's `values` has the length of the case's `ast`, which the Python
backend requires (the manifest's `counts`: `values` counts `case.ast`). -/
namespace VE.EvaluationCounts
open Lean
open VE.Order.ProfileGate (bind_ok)

theorem mapM_length {ε α β : Type} (f : α → Except ε β) :
    ∀ (l : List α) (r : List β), l.mapM f = .ok r → r.length = l.length := by
  intro l
  induction l with
  | nil => intro r h; simp [List.mapM_nil, pure, Except.pure] at h; subst h; rfl
  | cons a l ih =>
    intro r h
    rw [List.mapM_cons] at h
    obtain ⟨b, _, h⟩ := bind_ok h
    obtain ⟨bs, hbs, h⟩ := bind_ok h
    cases h
    simp [ih bs hbs]

theorem legacy_decodeDocument_length {E d} (j : Json) (h : VE.Bridge.decodeDocument E j = .ok d) :
    ∃ arr, j.getArr? = .ok arr ∧ d.formulas.length = arr.size := by
  unfold VE.Bridge.decodeDocument at h
  obtain ⟨arr, harr, h⟩ := bind_ok h
  obtain ⟨fs, hfs, h⟩ := bind_ok h
  refine ⟨arr, harr, ?_⟩
  have hl := mapM_length _ _ _ hfs
  revert h
  repeat' split
  all_goals intro h
  all_goals first
    | (cases h; simpa using hl)
    | (simp_all [bind, Except.bind, pure, Except.pure]; done)

theorem closure_decodeFormulas_length {E fs} (j : Json) (h : VE.Closure.Bridge.decodeFormulas E j = .ok fs) :
    ∃ arr, j.getArr? = .ok arr ∧ fs.length = arr.size := by
  unfold VE.Closure.Bridge.decodeFormulas at h
  obtain ⟨arr, harr, h⟩ := bind_ok h
  obtain ⟨fs, hfs, h⟩ := bind_ok h
  refine ⟨arr, harr, ?_⟩
  have hl := mapM_length _ _ _ hfs
  revert h
  repeat' split
  all_goals intro h
  all_goals first
    | (cases h; simpa using hl)
    | (simp_all [bind, Except.bind, pure, Except.pure]; done)

theorem core_decodeFormulas_length {E fs} (j : Json) (h : VE.Core.Bridge.decodeFormulas E j = .ok fs) :
    ∃ arr, j.getArr? = .ok arr ∧ fs.length = arr.size := by
  unfold VE.Core.Bridge.decodeFormulas at h
  obtain ⟨arr, harr, h⟩ := bind_ok h
  obtain ⟨fs, hfs, h⟩ := bind_ok h
  refine ⟨arr, harr, ?_⟩
  -- the `for` loop of checks
  obtain ⟨_, _, h⟩ := bind_ok h
  have hl := mapM_length _ _ _ hfs
  revert h
  repeat' split
  all_goals intro h
  all_goals first
    | (cases h; simpa using hl)
    | (simp_all [bind, Except.bind, pure, Except.pure]; done)

theorem order_decodeFormulas_length {E fs} (j : Json) (h : VE.Order.Wire.decodeFormulas E j = .ok fs) :
    ∃ arr, j.getArr? = .ok arr ∧ fs.length = arr.size := by
  unfold VE.Order.Wire.decodeFormulas at h
  obtain ⟨arr, harr, h⟩ := bind_ok h
  obtain ⟨fs, hfs, h⟩ := bind_ok h
  refine ⟨arr, harr, ?_⟩
  have hl := mapM_length _ _ _ hfs
  revert h
  repeat' split
  all_goals intro h
  all_goals first
    | (cases h; simpa using hl)
    | (simp_all [bind, Except.bind, pure, Except.pure]; done)

theorem route_decodeFormulas_length {E fs} (j : Json) (data : Bool) (h : VE.Route.Wire.decodeFormulas E j data = .ok fs) :
    ∃ arr, j.getArr? = .ok arr ∧ fs.length = arr.size := by
  unfold VE.Route.Wire.decodeFormulas at h
  obtain ⟨arr, harr, h⟩ := bind_ok h
  obtain ⟨fs, hfs, h⟩ := bind_ok h
  refine ⟨arr, harr, ?_⟩
  have hl := mapM_length _ _ _ hfs
  revert h
  repeat' split
  all_goals intro h
  all_goals first
    | (cases h; simpa using hl)
    | (simp_all [bind, Except.bind, pure, Except.pure]; done)

end VE.EvaluationCounts
