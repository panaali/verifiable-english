import VE.Norms.Checks
import VE.Norms.Layer

/-! Actual frozen P0 `Layer` values for concrete documents (docs/spec/norms.md
10.1(c), (m), (o) and 10.11).

Well-formedness of a concrete document is checked by kernel reduction
(`decide +kernel`, audited like every other proof). Conflict-freedom of these documents is
discharged by `ground_conflictFree`: when every conflict formula mentions no
predicate and no quantifier (all rules unconditional), its truth value is a
constant, computed by `groundValue`. With global base conflict-freedom,
`conflictFree_prefix` gives each layer's `hc`, so `layer` and the composed
`route` are constructed as definitions, not assumed. -/
namespace VE.Norms
universe u

/-- The constant truth value of a formula without atoms and quantifiers. -/
def groundValue : VE.Formula → Option Bool
  | .top => some true
  | .bottom => some false
  | .not a => (groundValue a).map (!·)
  | .and a b => match groundValue a, groundValue b with
    | some x, some y => some (x && y)
    | _, _ => none
  | .or a b => match groundValue a, groundValue b with
    | some x, some y => some (x || y)
    | _, _ => none
  | .implies a b => match groundValue a, groundValue b with
    | some x, some y => some (!x || y)
    | _, _ => none
  | _ => none

theorem groundValue_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    ∀ (a : VE.Formula) (b : Bool), groundValue a = some b → (a.denote S ρ ↔ b = true)
  | .top, b, h => by cases h; simp [VE.Formula.denote]
  | .bottom, b, h => by cases h; simp [VE.Formula.denote]
  | .not a, b, h => by
    simp only [groundValue, Option.map_eq_some_iff] at h
    obtain ⟨x, hx, rfl⟩ := h
    simp only [VE.Formula.denote, groundValue_denote S ρ a x hx]
    cases x <;> simp
  | .and a c, b, h => by
    simp only [groundValue] at h
    split at h
    · rename_i x y hx hy
      cases h
      simp only [VE.Formula.denote, groundValue_denote S ρ a x hx, groundValue_denote S ρ c y hy]
      cases x <;> cases y <;> simp
    · cases h
  | .or a c, b, h => by
    simp only [groundValue] at h
    split at h
    · rename_i x y hx hy
      cases h
      simp only [VE.Formula.denote, groundValue_denote S ρ a x hx, groundValue_denote S ρ c y hy]
      cases x <;> cases y <;> simp
    · cases h
  | .implies a c, b, h => by
    simp only [groundValue] at h
    split at h
    · rename_i x y hx hy
      cases h
      simp only [VE.Formula.denote, groundValue_denote S ρ a x hx, groundValue_denote S ρ c y hy]
      cases x <;> cases y <;> simp
    · cases h
  | .unary _ _, _, h | .binary _ _ _, _, h | .eq _ _, _, h | .all _ _, _, h | .ex _ _, _, h => by
    cases h

/-- Every conflict formula is constantly false. -/
def groundConflictFree (D : Doc) : Bool :=
  D.T.regulated.all (fun r => groundValue (conflict D r) == some false) &&
    (pairs D.T).all (fun pr => groundValue (pairConflict D pr) == some false)

theorem ground_conflictFree (D : Doc) (h : groundConflictFree D = true) (B : VE.Structure.{u})
    (_ : BaseAdmissible D B) : ConflictFree D B := by
  simp only [groundConflictFree, Bool.and_eq_true, List.all_eq_true, beq_iff_eq] at h
  exact ⟨fun r hr vs _ hc => by simpa using (groundValue_denote B _ _ false (h.1 r hr)).mp hc,
    fun pr hpr vs _ hc => by simpa using (groundValue_denote B _ _ false (h.2 pr hpr)).mp hc⟩

namespace Examples
open VE.Norms.Checks

theorem doc_c_wellFormed : WellFormed doc_c = true := by decide +kernel
theorem doc_c_ground : groundConflictFree doc_c = true := by decide +kernel
theorem doc_m_wellFormed : WellFormed doc_m = true := by decide +kernel
theorem doc_m_ground : groundConflictFree doc_m = true := by decide +kernel
theorem doc_o_wellFormed : WellFormed doc_o = true := by decide +kernel
theorem doc_o_ground : groundConflictFree doc_o = true := by decide +kernel

theorem required_mem_c : oblig "required" act false (some "permitted") ∈ doc_c.T.regulated := by
  decide +kernel
theorem permitted_mem_c : perm "permitted" act false ∈ doc_c.T.regulated := by decide +kernel
theorem areq_mem_m : oblig "areq" act false (some "bperm") ∈ doc_m.T.regulated := by decide +kernel
theorem bperm_mem_m : perm "bperm" act false ∈ doc_m.T.regulated := by decide +kernel

/-- The `layer` of a regulated predicate of a document proved well-formed and
constantly conflict-free, with its `hc` from `conflictFree_prefix`. -/
def groundLayer (D : Doc) (h : WellFormed D = true) (hg : groundConflictFree D = true) (r : Regulated)
    (hr : r ∈ D.T.regulated) : VE.Route.Layer VE.Route.fol.{u} Unit :=
  layer D h r hr (fun S₀ h₀ => conflictFree_prefix D h r hr (ground_conflictFree D hg) S₀ h₀)

/-- 10.1(c): both frozen layers of the repaired required/permitted document. -/
def layer_c_permitted : VE.Route.Layer VE.Route.fol.{0} Unit :=
  groundLayer doc_c doc_c_wellFormed doc_c_ground _ permitted_mem_c
def layer_c_required : VE.Route.Layer VE.Route.fol.{0} Unit :=
  groundLayer doc_c doc_c_wellFormed doc_c_ground _ required_mem_c

/-- 10.1(m): both frozen layers of the obligation-first pair with no rules. -/
def layer_m_areq : VE.Route.Layer VE.Route.fol.{0} Unit :=
  groundLayer doc_m doc_m_wellFormed doc_m_ground _ areq_mem_m
def layer_m_bperm : VE.Route.Layer VE.Route.fol.{0} Unit :=
  groundLayer doc_m doc_m_wellFormed doc_m_ground _ bperm_mem_m

/-- 10.1(c) and (o): the composed routes (the second has a definition layer
between the permission and the obligation). -/
def route_c : Chain.{0} doc_c (size doc_c) :=
  route doc_c (valid_of_wellFormed _ doc_c_wellFormed) (ground_conflictFree doc_c doc_c_ground)
def route_o : Chain.{0} doc_o (size doc_o) :=
  route doc_o (valid_of_wellFormed _ doc_o_wellFormed) (ground_conflictFree doc_o doc_o_ground)

theorem layer_c_permitted_premises :
    layer_c_permitted.premises () = [elabPremise doc_c.T (perm "permitted" act false)] := rfl
theorem layer_c_layers_compose : layer_c_required.E_in = layer_c_permitted.E_out ∧
    ∀ S, layer_c_required.Admissible_in S ↔ layer_c_permitted.Admissible_out S := by
  refine ⟨?_, fun S => ?_⟩
  · show envAt doc_c (before doc_c "required") = envAt doc_c (before doc_c "permitted" + 1)
    rw [show before doc_c "required" = 1 by decide +kernel, show before doc_c "permitted" = 0 by decide +kernel]
  · show PrefixAdmissible doc_c (before doc_c "required") S ↔
      PrefixAdmissible doc_c (before doc_c "permitted" + 1) S
    rw [show before doc_c "required" = 1 by decide +kernel, show before doc_c "permitted" = 0 by decide +kernel]
theorem route_o_premises : route_o.R.premises () = elaborate doc_o.T :=
  route_premises (valid_of_wellFormed _ doc_o_wellFormed) (ground_conflictFree doc_o doc_o_ground) ()
theorem route_o_size : size doc_o = 3 := by decide +kernel

/-- The unique document expansion of (o) exists over every base-admissible structure. -/
theorem doc_o_expands (B : VE.Structure.{u}) (hB : BaseAdmissible doc_o B) :
    VE.Route.Unique (DocumentExpansion doc_o B) :=
  (conflictFree_expands_document doc_o doc_o_wellFormed B hB).mpr (ground_conflictFree doc_o doc_o_ground B hB)

end Examples
end VE.Norms
