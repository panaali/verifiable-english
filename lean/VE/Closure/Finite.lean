import VE.Closure.Syntax
import VE.Core.Finite

/-! `VE.Core.Finite` under the names the Closure proofs and statements use: every declaration keeps
its Closure name, as an abbreviation, a definition through the embedding `Formula.toCore`, or a
corollary with the identical statement. -/
namespace VE.Closure
universe u

abbrev namedEdges {α : Type u} (rows : List (List α)) : List (α × α) := VE.Core.namedEdges rows

theorem mem_namedEdges {α : Type u} (rows : List (List α)) (a b : α) :
    (a, b) ∈ namedEdges rows ↔ [a, b] ∈ rows := VE.Core.mem_namedEdges rows a b

abbrev bodyEdges {α : Type u} (domain : List α) (f : α → α → Bool) : List (α × α) :=
  VE.Core.bodyEdges domain f

theorem mem_bodyEdges {α : Type u} (domain : List α) (f : α → α → Bool) (a b : α) :
    (a, b) ∈ bodyEdges domain f ↔ a ∈ domain ∧ b ∈ domain ∧ f a b = true :=
  VE.Core.mem_bodyEdges domain f a b

/-- Finite evaluation is Core's on the embedding. -/
def Formula.eval {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ρ : List α) (a : Formula) : Bool :=
  a.toCore.eval M ρ

/-- Equality of base relations transports finite paths and both closures. -/
theorem reachable_congr {α : Type u} (k : Kind) (R Q : α → α → Prop)
    (h : ∀ x y, R x y ↔ Q x y) (a b : α) :
    Reachable k R a b ↔ Reachable k Q a b := VE.Core.reachable_congr k R Q h a b

/-- P6, for every raw formula and valuation; in particular for all typed closed
claims in valid finite structures. Core's theorem on the embedding. -/
theorem eval_iff_denote {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ρ : List α) (a : Formula) :
    a.eval M ρ = true ↔ a.denote M.asStructure ρ := VE.Core.eval_iff_denote M ρ a.toCore

theorem eval_false_iff_not_denote {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ρ : List α) (a : Formula) :
    a.eval M ρ = false ↔ ¬ a.denote M.asStructure ρ :=
  VE.Core.eval_false_iff_not_denote M ρ a.toCore

end VE.Closure
