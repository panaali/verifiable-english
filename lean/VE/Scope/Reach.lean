import VE.Scope.Govern
import VE.Rights.Tree

/-! SC-6 (docs/spec/scope.md 5.8, 7.8): the rights a reach reaches. "The rights and freedoms set forth in this
    Declaration" reaches the document's right units, and a rights@0 limitation's `scope` is generated from that reach
    (`Pinned.withReach`) in place of a stand-in open term. A bar has no scope in rights@0, since it reads every right,
    so its reach must reach every right (`Pinned.withBarReach`). rights@0 is read here, never changed: its
    `Limitation` and `Bar` are the decoded values (`VE.Rights.Wire`), and the right a unit carries is read from the
    unit's content as rights 3.2 writes it. -/

namespace VE.Scope
open Lean

namespace Pinned

/-- The right whose lines a unit's content carries: `{"right": {"name": r, …}}` or
    `{"right_lines": {"right": r, …}}` (rights 3.2); none for any other content. -/
def rightOf (c : Json) : Option String :=
  match keysOf c with
  | ["right"] => ((c.getObjValD "right").getObjValD "name").getStr?.toOption
  | ["right_lines"] => ((c.getObjValD "right_lines").getObjValD "right").getStr?.toOption
  | _ => none

/-- The rights whose lines the units `us` carry, each once, in the order of `us`. -/
def rightNames (D : SDoc) (us : List String) : List String :=
  (us.filterMap fun u => rightOf (contentOf D.doc u)).eraseDups

/-- A right is in a limitation's scope as a whole (every line of it), so a reach that holds some units of a right
    and not others is refused. -/
def wholeRights (D : SDoc) (g : Governor) (us : List String) : Except String Unit := do
  let rs := rightNames D us
  for u in unitIds D.doc do
    if (rightOf (contentOf D.doc u)).any rs.contains && !us.contains u then
      throw s!"ScopeReach: {g.id}"

/-- The limitation `L` with its scope generated from `g`'s reach: the rights the reach reaches. -/
def withReach (D : SDoc) (g : Governor) (L : VE.Rights.Limitation) : Except String VE.Rights.Limitation := do
  let us ← covered D g.reach
  wholeRights D g us
  pure { L with scope := some (rightNames D us) }

/-- The bar `B` as rights@0 reads it (over every right), admitted only when `g`'s reach holds every unit of the
    document that carries a right's lines. -/
def withBarReach (D : SDoc) (g : Governor) (B : VE.Rights.Bar) : Except String VE.Rights.Bar := do
  let us ← covered D g.reach
  unless (unitIds D.doc).all (fun u => (rightOf (contentOf D.doc u)).isNone || us.contains u) do
    throw s!"ScopeReach: {g.id}"
  pure B

end Pinned

theorem limitation_scope_of_reach (D : SDoc) (g : Governor) (L L' : VE.Rights.Limitation)
    (h : Pinned.withReach D g L = .ok L') (us : List String) (hc : covered D g.reach = .ok us) :
    L'.scope = some (Pinned.rightNames D us) ∧ { L' with scope := L.scope } = L := by
  unfold Pinned.withReach at h
  rw [hc] at h
  simp only [bind, Except.bind] at h
  split at h
  · cases h
  · cases h; exact ⟨rfl, rfl⟩

/-- A bar's reach changes nothing in the bar, and holds every right line of the document. -/
theorem bar_reach_every_right (D : SDoc) (g : Governor) (B B' : VE.Rights.Bar)
    (h : Pinned.withBarReach D g B = .ok B') (us : List String) (hc : covered D g.reach = .ok us) :
    B' = B ∧ ∀ u ∈ unitIds D.doc, (Pinned.rightOf (contentOf D.doc u)).isSome → u ∈ us := by
  unfold Pinned.withBarReach at h
  rw [hc] at h
  simp only [bind, Except.bind] at h
  split at h
  · rename_i hall
    cases h
    refine ⟨rfl, fun u hu hs => ?_⟩
    have := List.all_eq_true.mp hall u hu
    simp only [Option.isNone_iff_eq_none, Bool.or_eq_true, decide_eq_true_eq, List.contains_iff_mem] at this
    rcases this with h₁ | h₂
    · simp [h₁] at hs
    · exact h₂
  · cases h

end VE.Scope
