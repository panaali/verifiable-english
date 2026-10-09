import VE.Route.Metered

/-! A completed metered document has the value of the total evaluator, hence
by each family's `eval_iff_denote` it has its finite-model denotation. -/
namespace VE.Route.MeteredProofs
open VE.Route

theorem fol_sound (mem : String → List VE.Bridge.Entity → Bool)
    (M : VE.FiniteModel VE.Bridge.Entity) (limit : Nat)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p)
    (fs : List VE.Formula) (b : Bool)
    (h : (Metered.evaluate (fun f w => Budget.evalF mem M limit [] f w) limit fs).value = some b) :
    b = fs.all (fun f => f.eval M []) := by
  exact Metered.scan_sound _ _ limit
    (fun f w b w' hf => Budget.evalF_sound mem M limit hmem f [] w (b, w') hf)
    fs 0 b h

theorem order_sound (mem : String → List (VE.Order.Value VE.Order.Wire.Entity) → Bool)
    (M : VE.Order.FiniteModel VE.Order.Wire.Entity) (limit : Nat)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p)
    (fs : List VE.Order.Formula) (b : Bool)
    (h : (Metered.evaluate (fun f w => VE.Time.evalB mem M limit [] f w) limit fs).value = some b) :
    b = fs.all (fun f => f.eval M []) := by
  exact Metered.scan_sound _ _ limit
    (fun f w b w' hf => VE.Time.evalB_sound mem M limit hmem f [] w (b, w') hf)
    fs 0 b h

theorem closure_sound (mem : String → List VE.Bridge.Entity → Bool)
    (M : VE.FiniteModel VE.Bridge.Entity) (limit : Nat)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p)
    (fs : List VE.Closure.Formula) (b : Bool)
    (h : (Metered.scanState (fun f s => Budget.evalC mem M limit [] f s)
      (fun s => s.work) limit fs ⟨0, {}⟩).value = some b) :
    b = fs.all (fun f => f.eval M []) := by
  exact Metered.scanState_sound _ _ limit _
    (VE.Route.Closure.CacheOK (Budget.closureRel M))
    (fun f s b s' hp hf => Budget.evalC_sound mem M limit hmem f [] s (b, s') hp hf)
    fs ⟨0, {}⟩ b (VE.Route.Closure.cacheOK_empty _ 0) h

theorem core_sound (mem : String → List VE.Bridge.Entity → Bool)
    (M : VE.FiniteModel VE.Bridge.Entity) (limit : Nat)
    (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p)
    (fs : List VE.Core.Formula) (b : Bool)
    (h : (Metered.scanState (fun f s => Budget.evalN mem M limit [] f s)
      (fun s => s.work) limit fs ⟨0, {}⟩).value = some b) :
    b = fs.all (fun f => f.eval M []) := by
  exact Metered.scanState_sound _ _ limit _
    (VE.Route.Closure.CacheOK (Budget.closureRelN M))
    (fun f s b s' hp hf => Budget.evalN_sound mem M limit hmem f [] s (b, s') hp hf)
    fs ⟨0, {}⟩ b (VE.Route.Closure.cacheOK_empty _ 0) h

end VE.Route.MeteredProofs
