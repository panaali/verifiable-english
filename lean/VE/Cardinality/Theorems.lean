import VE.Cardinality.Erase
import VE.Time.Count

/-! Theorems of `cardinality@0` that do not need erasure's soundness (docs/spec/quantities.md 3.6, 3.7): counts over
a declared finite sort exist and are unique, region constants are nonnegative where they are region sizes, and a
proportion holds exactly when its population is nonempty and its share compares as written. The count atoms for W6a's
four counting forms are defined here; their agreement theorems come with erasure's soundness (QT-A1b). -/
namespace VE.Cardinality
open VE.Time (TStructure)
universe u

/-- Some duplicate-free list holds exactly the members of `xs` with `P`. -/
theorem exists_nodup_filter {α : Type u} (P : α → Prop) :
    ∀ xs : List α, ∃ ys : List α, ys.Nodup ∧ ∀ x, x ∈ ys ↔ x ∈ xs ∧ P x
  | [] => ⟨[], List.nodup_nil, by simp⟩
  | a :: xs => by
    classical
    obtain ⟨ys, hnd, hys⟩ := exists_nodup_filter P xs
    by_cases h : P a ∧ a ∉ ys
    · refine ⟨a :: ys, List.nodup_cons.mpr ⟨h.2, hnd⟩, fun x => ?_⟩
      simp only [List.mem_cons, hys]
      constructor
      · rintro (rfl | ⟨hx, hp⟩)
        · exact ⟨Or.inl rfl, h.1⟩
        · exact ⟨Or.inr hx, hp⟩
      · rintro ⟨rfl | hx, hp⟩
        · exact Or.inl rfl
        · exact Or.inr ⟨hx, hp⟩
    · refine ⟨ys, hnd, fun x => ?_⟩
      rw [hys]
      constructor
      · rintro ⟨hx, hp⟩; exact ⟨List.mem_cons_of_mem a hx, hp⟩
      · rintro ⟨hx, hp⟩
        rcases List.mem_cons.mp hx with rfl | hx
        · exact (hys x).mp (Classical.not_not.mp fun hn => h ⟨hp, hn⟩)
        · exact ⟨hx, hp⟩

/-- Two duplicate-free lists with the same members have the same length. -/
theorem nodup_length_eq {α : Type u} :
    ∀ {xs ys : List α}, xs.Nodup → ys.Nodup → (∀ x, x ∈ xs ↔ x ∈ ys) → xs.length = ys.length
  | [], ys, _, _, h => by
    cases ys with
    | nil => rfl
    | cons y _ => exact absurd ((h y).mpr (List.mem_cons_self ..)) (List.not_mem_nil)
  | a :: xs, ys, hx, hy, h => by
    classical
    have ha : a ∈ ys := (h a).mp (List.mem_cons_self ..)
    obtain ⟨hna, hxs⟩ := List.nodup_cons.mp hx
    have hlen := nodup_length_eq hxs (hy.erase a) fun x => by
      rw [List.Nodup.mem_erase_iff hy, ← h x, List.mem_cons]
      constructor
      · intro hm; exact ⟨fun he => hna (he ▸ hm), Or.inr hm⟩
      · rintro ⟨hne, rfl | hm⟩
        · exact absurd rfl hne
        · exact hm
    rw [List.length_cons, hlen, List.length_erase_of_mem ha]
    have : 0 < ys.length := List.length_pos_of_mem ha
    omega

/-- On an admissible structure every count over a declared finite sort exists and is unique, so a count atom and its
negation mean what they say. -/
theorem hasCount_exists_unique {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) :
    ∃ n, HasCount T s b n ∧ ∀ m, HasCount T s b m → m = n := by
  obtain ⟨xs, hxs⟩ := hT.2 s hs
  obtain ⟨ys, hnd, hys⟩ := exists_nodup_filter (fun x => b.holds T x) xs
  have hc : ∀ x, x ∈ ys ↔ T.objects s x ∧ b.holds T x := fun x => by rw [hys, hxs]
  refine ⟨ys.length, ⟨ys, hnd, rfl, hc⟩, ?_⟩
  rintro m ⟨zs, hz, rfl, hzs⟩
  exact nodup_length_eq hz hnd fun x => by rw [hzs, hc]

/-- A count is unique. -/
theorem hasCount_unique {α : Type u} {T : TStructure α} {s : String} {b : Body} {n m : Nat}
    (hn : HasCount T s b n) (hm : HasCount T s b m) : n = m := by
  obtain ⟨xs, hx, rfl, hxs⟩ := hn
  obtain ⟨ys, hy, rfl, hys⟩ := hm
  exact nodup_length_eq hx hy fun x => by rw [hxs, hys]

/-- Each region premise `0 ≤ n` holds where region constants are region sizes. -/
theorem nonneg_hold {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) :
    ∀ a ∈ nonnegPremises E fs, a.tdenote (withRegions E fs T) [] := by
  intro a ha
  obtain ⟨e, he, rfl⟩ := List.mem_map.mp ha
  have hs : ((regionTable E fs).find? (·.1 == e.1)).isSome := List.find?_isSome.mpr ⟨e, he, by simp⟩
  obtain ⟨⟨c, s, r⟩, hf⟩ := Option.isSome_iff_exists.mp hs
  refine ⟨dl, 0, regionSize T s (regionBody (predsOn E fs s) r), rfl, ?_, by omega⟩
  simp [VE.Time.QTerm.tdenote, withRegions, hf]

set_option linter.unusedVariables false in
/-- A proportion holds exactly when the population is nonempty and the share compares as written. -/
theorem proportion_holds_iff {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T) (p : Proportion)
    (hp : Admitted E (.proportion p)) :
    (CFormula.proportion p).holds T ↔
      ∃ n m : Nat, HasCount T p.sort p.whole n ∧ HasCount T p.sort (.and p.whole p.part) m ∧ 0 < n ∧
        p.cmp.holds ((m : Int) * p.den) ((n : Int) * p.num) := by
  simp only [CFormula.holds, Proportion.holds, Int.mul_comm (p.den : Int), Int.mul_comm (p.num : Int)]

/-! ## W6a's four counting forms as count atoms -/

/-- "At least n": `-1 · #b ≤ -n`; "at most n": `#b ≤ n`; "exactly n": `#b = n`. -/
def atLeastAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(-1, b)], .le, -(n : Int)⟩
def atMostAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(1, b)], .le, n⟩
def exactlyAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(1, b)], .eq, n⟩
/-- "Exactly n of the m": exactly m selected and exactly n of them with the property (W6a's `nOfM`). -/
def nOfMFormula (s : String) (n m : Nat) (sel prop : Body) : CFormula :=
  .and (.count (exactlyAtom s sel m)) (.count (exactlyAtom s (.and sel prop) n))

/-- The body as an order@0 formula on the counted variable (de Bruijn index 0). -/
def Body.toFormula : Body → VE.Order.Formula
  | .atom p => .unary p (.var 0)
  | .any => .top
  | .not b => .not b.toFormula
  | .and a b => .and a.toFormula b.toFormula
  | .or a b => .or a.toFormula b.toFormula

end VE.Cardinality
