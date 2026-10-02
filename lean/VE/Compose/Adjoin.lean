import VE.Compose.Slot

/-! The lifting lemma (docs/spec/composition.md 9.5; composition-s2.md 4.4, 8.2).

`adjoinOne B` is `B` with one new element that lies in no sort and in no tuple. Every term and formula denotes in
it as in `B` under the valuation mapped through `some`, so admissibility, base admissibility relative to a slot and
the truth of every closed formula are preserved. A base with an empty carrier is thereby lifted to one with an
element, which is how `superpose_all` drops the non-emptiness hypothesis. -/
namespace VE.Compose
open VE.Norms (Sat)
universe u

/-- B with one new element that lies in no sort and in no tuple. -/
def adjoinOne (B : VE.Structure.{u}) : VE.Structure.{u} where
  Carrier := Option B.Carrier
  domain s v := ∃ x, v = some x ∧ B.domain s x
  constant c := (B.constant c).map some
  relation p vs := ∃ xs, vs = xs.map some ∧ B.relation p xs

theorem adjoin_term (B : VE.Structure.{u}) (ρ : VE.Valuation B) (t : VE.Term) :
    t.denote (adjoinOne B) (ρ.map some) = (t.denote B ρ).map some := by
  cases t with
  | var i => simp [VE.Term.denote]
  | const c => rfl

theorem adjoin_relation (B : VE.Structure.{u}) (p : String) (xs : List B.Carrier) :
    (adjoinOne B).relation p (xs.map some) ↔ B.relation p xs := by
  constructor
  · rintro ⟨ys, hys, h⟩
    have : ys = xs := ((List.map_inj_right (fun _ _ h => Option.some.inj h)).mp hys).symm
    exact this ▸ h
  · intro h; exact ⟨xs, rfl, h⟩

theorem adjoin_denote (B : VE.Structure.{u}) (φ : VE.Formula) (ρ : VE.Valuation B) :
    φ.denote (adjoinOne B) (ρ.map some) ↔ φ.denote B ρ := by
  induction φ generalizing ρ with
  | top | bottom => exact Iff.rfl
  | unary p t =>
    simp only [VE.Formula.denote, adjoin_term]
    constructor
    · rintro ⟨v, hv, hr⟩
      obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.mp hv
      exact ⟨x, hx, (adjoin_relation B p [x]).mp hr⟩
    · rintro ⟨x, hx, hr⟩
      exact ⟨some x, by rw [hx]; rfl, (adjoin_relation B p [x]).mpr hr⟩
  | binary p t t' =>
    simp only [VE.Formula.denote, adjoin_term]
    constructor
    · rintro ⟨v, w, hv, hw, hr⟩
      obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.mp hv
      obtain ⟨y, hy, rfl⟩ := Option.map_eq_some_iff.mp hw
      exact ⟨x, y, hx, hy, (adjoin_relation B p [x, y]).mp hr⟩
    · rintro ⟨x, y, hx, hy, hr⟩
      exact ⟨some x, some y, by rw [hx]; rfl, by rw [hy]; rfl, (adjoin_relation B p [x, y]).mpr hr⟩
  | eq t t' =>
    simp only [VE.Formula.denote, adjoin_term]
    constructor
    · rintro ⟨v, hv, hw⟩
      obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.mp hv
      obtain ⟨y, hy, he⟩ := Option.map_eq_some_iff.mp hw
      cases he
      exact ⟨x, hx, hy⟩
    · rintro ⟨x, hx, hy⟩
      exact ⟨some x, by rw [hx]; rfl, by rw [hy]; rfl⟩
  | not a ih => exact not_congr (ih ρ)
  | and a b ia ib => exact and_congr (ia ρ) (ib ρ)
  | or a b ia ib => exact or_congr (ia ρ) (ib ρ)
  | implies a b ia ib => exact imp_congr (ia ρ) (ib ρ)
  | all s a ih =>
    simp only [VE.Formula.denote]
    constructor
    · intro h x hx
      exact (ih (x :: ρ)).mp (h (some x) ⟨x, rfl, hx⟩)
    · rintro h v ⟨x, rfl, hx⟩
      exact (ih (x :: ρ)).mpr (h x hx)
  | ex s a ih =>
    simp only [VE.Formula.denote]
    constructor
    · rintro ⟨v, ⟨x, rfl, hx⟩, h⟩
      exact ⟨x, hx, (ih (x :: ρ)).mp h⟩
    · rintro ⟨x, hx, h⟩
      exact ⟨some x, ⟨x, rfl, hx⟩, (ih (x :: ρ)).mpr h⟩

theorem adjoin_tupleTyped (B : VE.Structure.{u}) :
    ∀ (ss : List String) (xs : List B.Carrier),
      VE.TupleTyped (adjoinOne B) ss (xs.map some) ↔ VE.TupleTyped B ss xs
  | [], [] => Iff.rfl
  | [], _ :: _ => Iff.rfl
  | _ :: _, [] => Iff.rfl
  | s :: ss, x :: xs => by
    show ((∃ y, some x = some y ∧ B.domain s y) ∧ _) ↔ (B.domain s x ∧ _)
    rw [adjoin_tupleTyped B ss xs]
    constructor
    · rintro ⟨⟨y, hy, hd⟩, h⟩
      cases hy
      exact ⟨hd, h⟩
    · rintro ⟨hd, h⟩
      exact ⟨⟨x, rfl, hd⟩, h⟩

theorem adjoin_admissible (E : VE.Environment) (B : VE.Structure.{u}) :
    (adjoinOne B).Admissible E ↔ B.Admissible E := by
  constructor
  · rintro ⟨hc, hr⟩
    refine ⟨fun c s hs => ?_, fun p xs h => ?_⟩
    · obtain ⟨v, hv, ⟨x, rfl, hx⟩⟩ := hc c s hs
      obtain ⟨y, hy, he⟩ := Option.map_eq_some_iff.mp hv
      cases he
      exact ⟨x, hy, hx⟩
    · obtain ⟨ss, hss, ht⟩ := hr p (xs.map some) ⟨xs, rfl, h⟩
      exact ⟨ss, hss, (adjoin_tupleTyped B ss xs).mp ht⟩
  · rintro ⟨hc, hr⟩
    refine ⟨fun c s hs => ?_, fun p vs h => ?_⟩
    · obtain ⟨x, hx, hd⟩ := hc c s hs
      exact ⟨some x, by show (B.constant c).map some = _; rw [hx]; rfl, x, rfl, hd⟩
    · obtain ⟨xs, rfl, h⟩ := h
      obtain ⟨ss, hss, ht⟩ := hr p xs h
      exact ⟨ss, hss, (adjoin_tupleTyped B ss xs).mpr ht⟩

theorem adjoin_nonempty (B : VE.Structure.{u}) : Nonempty (adjoinOne B).Carrier := ⟨(none : Option B.Carrier)⟩

theorem adjoin_sat (B : VE.Structure.{u}) (L : List VE.Formula) : Sat (adjoinOne B) L ↔ Sat B L :=
  ⟨fun h a ha => (adjoin_denote B a []).mp (h a ha), fun h a ha => (adjoin_denote B a []).mpr (h a ha)⟩

theorem adjoin_baseAdmissibleP (X : VE.SoftNorms.SoftDoc) (P : List VE.Formula) (B : VE.Structure.{u}) :
    BaseAdmissibleP X P (adjoinOne B) ↔ BaseAdmissibleP X P B := by
  simp only [BaseAdmissibleP, VE.SoftNorms.BaseAdmissible', VE.Norms.BaseAdmissible, adjoin_admissible, adjoin_sat]

end VE.Compose
