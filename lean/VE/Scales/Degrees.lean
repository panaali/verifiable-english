import VE.Scales.Intended

/-! Degrees (docs/spec/quantities.md 6.2): on a comparable dimension, the intended meaning is exactly a
degree map into a strict linear order that gives the comparative and the equative, with each graded
word closed in its direction (Kennedy's degrees and Klein's relations agree). The degrees are the
classes of "as much as" over the sort's objects, with the objects outside the sort in one lowest class. -/
namespace VE.Scales
open VE
universe u

/-- A strict linear order, stated directly (the Lean tree uses no library). -/
structure StrictLinear {L : Type u} (lt : L → L → Prop) : Prop where
  irrefl : ∀ a, ¬ lt a a
  trans : ∀ a b c, lt a b → lt b c → lt a c
  connex : ∀ a b, lt a b ∨ a = b ∨ lt b a

section degrees
variable (S : Structure.{u}) (d : Dimension) (e : String)

/-- "As much as" over the sort's objects; the objects outside the sort are one class. -/
def asMuch (x y : S.Carrier) : Prop :=
  (S.domain d.sort x ∧ S.domain d.sort y ∧ S.relation e [x, y]) ∨ (¬ S.domain d.sort x ∧ ¬ S.domain d.sort y)

/-- `x` lies below `y`: both in the sort and `y` more than `x`, or only `y` in the sort. -/
def below (x y : S.Carrier) : Prop :=
  (S.domain d.sort y ∧ S.domain d.sort x ∧ S.relation d.more [y, x]) ∨ (S.domain d.sort y ∧ ¬ S.domain d.sort x)

variable {S d e}

/-- "As much as" is an equivalence when the dimension has its intended meaning. -/
def degreeSetoid (h : Intended S d) (he : d.same = some e) : Setoid S.Carrier where
  r := asMuch S d e
  iseqv := by
    refine ⟨fun x => ?_, fun {x y} hxy => ?_, fun {x y z} hxy hyz => ?_⟩
    · by_cases hx : S.domain d.sort x
      · exact .inl ⟨hx, hx, h.sameRefl e he x hx⟩
      · exact .inr ⟨hx, hx⟩
    · rcases hxy with ⟨hx, hy, r⟩ | ⟨hx, hy⟩
      · exact .inl ⟨hy, hx, h.sameSymm e he x y r⟩
      · exact .inr ⟨hy, hx⟩
    · rcases hxy with ⟨hx, hy, r⟩ | ⟨hx, hy⟩ <;> rcases hyz with ⟨hy', hz, r'⟩ | ⟨hy', hz⟩
      · exact .inl ⟨hx, hz, h.sameTrans e he x y z r r'⟩
      · exact absurd hy hy'
      · exact absurd hy' hy
      · exact .inr ⟨hx, hz⟩

theorem below_of (h : Intended S d) (he : d.same = some e) {a a' b b' : S.Carrier}
    (ha : asMuch S d e a a') (hb : asMuch S d e b b') (hab : below S d a b) : below S d a' b' := by
  rcases hab with ⟨hbs, has, hm⟩ | ⟨hbs, hna⟩
  · rcases ha with ⟨-, ha', hea⟩ | ⟨hna, -⟩
    · rcases hb with ⟨-, hb', heb⟩ | ⟨hnb, -⟩
      · exact .inl ⟨hb', ha', h.sameRight e he _ _ _ (h.sameLeft e he _ _ _ (h.sameSymm e he _ _ heb) hm) hea⟩
      · exact absurd hbs hnb
    · exact absurd has hna
  · rcases hb with ⟨-, hb', -⟩ | ⟨hnb, -⟩
    · rcases ha with ⟨has, -, -⟩ | ⟨-, hna'⟩
      · exact absurd has hna
      · exact .inr ⟨hb', hna'⟩
    · exact absurd hbs hnb

end degrees

/-- **Degrees**: on a comparable dimension the intended meaning is a degree map into a strict linear order, with each
graded word closed in its direction (Kennedy's degrees and Klein's relations agree). -/
theorem intended_iff_degrees (S : VE.Structure.{u}) (d : Dimension) (e : String)
    (hc : d.comparable = true) (he : d.same = some e)
    (htyped : ∀ x y, S.relation d.more [x, y] ∨ S.relation e [x, y] → S.domain d.sort x ∧ S.domain d.sort y) :
    Intended S d ↔ ∃ (L : Type u) (lt : L → L → Prop) (_ : StrictLinear lt) (deg : S.Carrier → L),
      (∀ x y, S.domain d.sort x → S.domain d.sort y →
        (S.relation d.more [x, y] ↔ lt (deg y) (deg x)) ∧ (S.relation e [x, y] ↔ deg x = deg y)) ∧
      (∀ g ∈ d.grades, ∀ x y, S.domain d.sort x → S.domain d.sort y → S.relation g.name [y] →
        (g.direction = .upper → ¬ lt (deg x) (deg y) → S.relation g.name [x]) ∧
        (g.direction = .lower → ¬ lt (deg y) (deg x) → S.relation g.name [x])) ∧
      (∀ p ∈ d.above, ∀ x, S.relation p.1 [x] → S.relation p.2 [x]) := by
  constructor
  · intro h
    let s := degreeSetoid h he
    let lt : Quotient s → Quotient s → Prop := Quotient.lift₂ (below S d)
      fun _ _ _ _ ha hb => propext ⟨below_of h he ha hb, below_of h he (s.symm ha) (s.symm hb)⟩
    have hlt : ∀ a b, lt (Quotient.mk s a) (Quotient.mk s b) ↔ below S d a b := fun _ _ => Iff.rfl
    have heq : ∀ a b, Quotient.mk s a = Quotient.mk s b ↔ asMuch S d e a b :=
      fun _ _ => ⟨Quotient.exact, fun h => Quotient.sound (s := s) h⟩
    have hsl : StrictLinear lt := by
      refine ⟨fun a => ?_, fun a b c => ?_, fun a b => ?_⟩
      · induction a using Quotient.ind
        rw [hlt]
        rintro (⟨-, has, hm⟩ | ⟨has, hna⟩)
        · exact h.irrefl _ has hm
        · exact hna has
      · induction a using Quotient.ind; induction b using Quotient.ind; induction c using Quotient.ind
        rw [hlt, hlt, hlt]
        rintro (⟨hbs, has, hm⟩ | ⟨hbs, hna⟩) (⟨hcs, hbs', hm'⟩ | ⟨hcs, hnb⟩)
        · exact .inl ⟨hcs, has, h.trans _ _ _ hcs hbs' has hm' hm⟩
        · exact absurd hbs hnb
        · exact .inr ⟨hcs, hna⟩
        · exact absurd hbs hnb
      · induction a using Quotient.ind; induction b using Quotient.ind
        rename_i a b
        rw [hlt, hlt, heq]
        by_cases ha : S.domain d.sort a <;> by_cases hb : S.domain d.sort b
        · rcases h.total hc e he a b ha hb with hm | hm | r
          · exact .inr (.inr (.inl ⟨ha, hb, hm⟩))
          · exact .inl (.inl ⟨hb, ha, hm⟩)
          · exact .inr (.inl (.inl ⟨ha, hb, r⟩))
        · exact .inr (.inr (.inr ⟨ha, hb⟩))
        · exact .inl (.inr ⟨hb, ha⟩)
        · exact .inr (.inl (.inr ⟨ha, hb⟩))
    refine ⟨Quotient s, lt, hsl, Quotient.mk s, fun x y hx hy => ?_, fun g hg x y hx hy hgy => ?_, h.aboveImp⟩
    · rw [hlt, heq]
      constructor
      · exact ⟨fun hm => .inl ⟨hx, hy, hm⟩, fun hb => hb.elim (·.2.2) fun hb => absurd hy hb.2⟩
      · exact ⟨fun r => .inl ⟨hx, hy, r⟩, fun hm => hm.elim (·.2.2) fun hm => absurd hx hm.1⟩
    · rw [hlt, hlt]
      have hcl := h.closed g hg x y hgy
      refine ⟨fun hup hn => ?_, fun hlow hn => ?_⟩ <;> rcases h.total hc e he x y hx hy with hm | hm | r
      · exact hcl.1 hup hm
      · exact absurd (.inl ⟨hy, hx, hm⟩) hn
      · exact hcl.2.2 e he r
      · exact absurd (.inl ⟨hx, hy, hm⟩) hn
      · exact hcl.2.1 hlow hm
      · exact hcl.2.2 e he r
  · rintro ⟨L, lt, hsl, deg, hd, hgr, habove⟩
    have asymm : ∀ a b, lt a b → ¬ lt b a := fun a b h₁ h₂ => hsl.irrefl a (hsl.trans _ _ _ h₁ h₂)
    have more : ∀ {x y}, S.relation d.more [x, y] → S.domain d.sort x ∧ S.domain d.sort y ∧ lt (deg y) (deg x) :=
      fun {x y} hm => have ht := htyped x y (.inl hm); ⟨ht.1, ht.2, ((hd x y ht.1 ht.2).1).mp hm⟩
    have same : ∀ {x y}, S.relation e [x, y] → S.domain d.sort x ∧ S.domain d.sort y ∧ deg x = deg y :=
      fun {x y} r => have ht := htyped x y (.inr r); ⟨ht.1, ht.2, ((hd x y ht.1 ht.2).2).mp r⟩
    have toMore : ∀ {x y}, S.domain d.sort x → S.domain d.sort y → lt (deg y) (deg x) → S.relation d.more [x, y] :=
      fun {x y} hx hy => ((hd x y hx hy).1).mpr
    have toSame : ∀ {x y}, S.domain d.sort x → S.domain d.sort y → deg x = deg y → S.relation e [x, y] :=
      fun {x y} hx hy => ((hd x y hx hy).2).mpr
    have hdir : ∀ g : Grade, g.direction = .upper ∨ g.direction = .lower := by
      intro g; cases g.direction <;> simp
    refine ⟨fun x _ hm => hsl.irrefl _ (more hm).2.2, fun x y z hx _ hz h₁ h₂ =>
      toMore hx hz (hsl.trans _ _ _ (more h₂).2.2 (more h₁).2.2), fun e' he' x hx => ?_,
      fun e' he' x y r => ?_, fun e' he' x y z r₁ r₂ => ?_, fun e' he' x y r hm => ?_,
      fun e' he' x y z r hm => ?_, fun e' he' x y z hm r => ?_, fun _ e' he' x y hx hy => ?_,
      fun g hg x y hy => ⟨fun hup hm => ?_, fun hlow hm => ?_, fun e' he' r => ?_⟩, habove⟩ <;>
      (try (rw [he] at he'; cases he'))
    · exact toSame hx hx rfl
    · obtain ⟨hx, hy, hxy⟩ := same r; exact toSame hy hx hxy.symm
    · obtain ⟨hx, -, hxy⟩ := same r₁; obtain ⟨-, hz, hyz⟩ := same r₂; exact toSame hx hz (hxy.trans hyz)
    · obtain ⟨-, -, hxy⟩ := same r; obtain ⟨-, -, hl⟩ := more hm; rw [hxy] at hl; exact hsl.irrefl _ hl
    · obtain ⟨hx, -, hxy⟩ := same r; obtain ⟨-, hz, hl⟩ := more hm; rw [← hxy] at hl; exact toMore hx hz hl
    · obtain ⟨hx, -, hl⟩ := more hm; obtain ⟨-, hz, hyz⟩ := same r; rw [hyz] at hl; exact toMore hx hz hl
    · rcases hsl.connex (deg x) (deg y) with hl | hq | hl
      · exact .inr (.inl (toMore hy hx hl))
      · exact .inr (.inr (toSame hx hy hq))
      · exact .inl (toMore hx hy hl)
    · obtain ⟨hx, hy', hl⟩ := more hm; exact (hgr g hg x y hx hy' hy).1 hup (asymm _ _ hl)
    · obtain ⟨hy', hx, hl⟩ := more hm; exact (hgr g hg x y hx hy' hy).2 hlow (asymm _ _ hl)
    · obtain ⟨hx, hy', hq⟩ := same r
      rcases hdir g with hd' | hd'
      · exact (hgr g hg x y hx hy' hy).1 hd' (hq ▸ hsl.irrefl _)
      · exact (hgr g hg x y hx hy' hy).2 hd' (hq ▸ hsl.irrefl _)

end VE.Scales
