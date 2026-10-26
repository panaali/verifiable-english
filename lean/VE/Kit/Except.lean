/-! Facts about `Except` that every route's proofs share (consolidation step 4a). -/
namespace VE.Kit.Except

/-- A successful bind: the first step succeeded and the continuation succeeded on its value. -/
theorem bind_ok {ε α β : Type} {x : Except ε α} {f : α → Except ε β} {b : β}
    (h : (x >>= f) = .ok b) : ∃ a, x = .ok a ∧ f a = .ok b := by
  cases x with
  | error e => cases h
  | ok a => exact ⟨a, rfl, h⟩

end VE.Kit.Except
