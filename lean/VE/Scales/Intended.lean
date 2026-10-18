import VE.Scales.Syntax

/-! The meaning of a dimension, stated directly over a structure, without the generated formulas
(docs/spec/quantities.md 6.2). -/
namespace VE.Scales
universe u

/-- The meaning of a dimension in a structure, stated directly. -/
structure Intended (S : VE.Structure.{u}) (d : Dimension) : Prop where
  irrefl : ∀ x, S.domain d.sort x → ¬ S.relation d.more [x, x]
  trans : ∀ x y z, S.domain d.sort x → S.domain d.sort y → S.domain d.sort z →
    S.relation d.more [x, y] → S.relation d.more [y, z] → S.relation d.more [x, z]
  sameRefl : ∀ e, d.same = some e → ∀ x, S.domain d.sort x → S.relation e [x, x]
  sameSymm : ∀ e, d.same = some e → ∀ x y, S.relation e [x, y] → S.relation e [y, x]
  sameTrans : ∀ e, d.same = some e → ∀ x y z,
    S.relation e [x, y] → S.relation e [y, z] → S.relation e [x, z]
  sameNotMore : ∀ e, d.same = some e → ∀ x y, S.relation e [x, y] → ¬ S.relation d.more [x, y]
  sameLeft : ∀ e, d.same = some e → ∀ x y z,
    S.relation e [x, y] → S.relation d.more [y, z] → S.relation d.more [x, z]
  sameRight : ∀ e, d.same = some e → ∀ x y z,
    S.relation d.more [x, y] → S.relation e [y, z] → S.relation d.more [x, z]
  total : d.comparable = true → ∀ e, d.same = some e → ∀ x y, S.domain d.sort x → S.domain d.sort y →
    S.relation d.more [x, y] ∨ S.relation d.more [y, x] ∨ S.relation e [x, y]
  closed : ∀ g ∈ d.grades, ∀ x y, S.relation g.name [y] →
    (g.direction = .upper → S.relation d.more [x, y] → S.relation g.name [x]) ∧
    (g.direction = .lower → S.relation d.more [y, x] → S.relation g.name [x]) ∧
    (∀ e, d.same = some e → S.relation e [x, y] → S.relation g.name [x])
  aboveImp : ∀ p ∈ d.above, ∀ x, S.relation p.1 [x] → S.relation p.2 [x]

end VE.Scales
