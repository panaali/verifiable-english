import VE.EnglishGrammar.Catalogue

/-! The fixed rules of the profile `order@0` (docs/spec/english-lean-s3.md 2.5), in the format of
`tools/english_grammar_gen.py`: one `FixedRow` per row of spec 2.5's table in its order, and the action of each
rule as the `act` text of the `english.grammar` export. Written by the Lean work item of S3 from the spec's
table; S3.0's generator renders this module from `ve/english_grammar/order@0.json` and must give the same rows.
Fixed rule `k` of a profile list's table has `act := k` (`fixedRules`). -/

namespace VE.EnglishGrammar
open VE.Grammar

/-- The action of each fixed rule of the table, as the `act` text of the `english.grammar` export. -/
def orderActs : Array String := #[
  "through",
  "intNegate",
  "intConst",
  "through",
  "intBracket",
  "intTwice",
  "intConst",
  "intBracket",
  "intNegate",
  "numeral false",
  "numeral true",
  "op",
  "op",
  "op",
  "unit",
  "unit",
  "unit",
  "unit",
  "unit",
  "unit",
  "intCmp eq false",
  "intCmp lt false",
  "intCmp le false",
  "intCmp lt true",
  "intCmp le true"
]

/-- The fixed rows of `order@0`. -/
def orderRows : Array FixedRow := #[
  { tag := "int-term.atom", lhs := 37, act := .through, rhs := [.n 38] },
  { tag := "int-term.minus", lhs := 37, act := .intNegate, rhs := [.n 44, .n 39] },
  { tag := "int-atom.constant", lhs := 38, act := .intConst, rhs := [.n 40] },
  { tag := "int-atom.numeral", lhs := 38, act := .through, rhs := [.n 42] },
  { tag := "int-atom.bracket", lhs := 38, act := .intBracket, rhs := [.n 45, .n 37, .n 43, .n 37, .n 46] },
  { tag := "int-atom.twice", lhs := 38, act := .intTwice, rhs := [.t (.kw "twice"), .t (.kw "the"), .n 41] },
  { tag := "int-neg.constant", lhs := 39, act := .intConst, rhs := [.n 40] },
  { tag := "int-neg.bracket", lhs := 39, act := .intBracket, rhs := [.n 45, .n 37, .n 43, .n 37, .n 46] },
  { tag := "int-neg.minus", lhs := 39, act := .intNegate, rhs := [.n 44, .n 39] },
  { tag := "numeral.plain", lhs := 42, act := (.numeral false), rhs := [.t (.cls .numeral)] },
  { tag := "numeral.signed", lhs := 42, act := (.numeral true), rhs := [.n 44, .t (.cls .numeral)] },
  { tag := "int-op.plus", lhs := 43, act := .op, rhs := [.t (.exact (.punct "+" false false))] },
  { tag := "int-op.minus", lhs := 43, act := .op, rhs := [.t (.exact (.punct "-" false false))] },
  { tag := "int-op.times", lhs := 43, act := .op, rhs := [.t (.exact (.punct "*" false false))] },
  { tag := "minus.free", lhs := 44, act := .unit, rhs := [.t (.exact (.punct "-" false true))] },
  { tag := "minus.glued", lhs := 44, act := .unit, rhs := [.t (.exact (.punct "-" true true))] },
  { tag := "lbracket.free", lhs := 45, act := .unit, rhs := [.t (.exact (.punct "[" false true))] },
  { tag := "lbracket.glued", lhs := 45, act := .unit, rhs := [.t (.exact (.punct "[" true true))] },
  { tag := "rbracket.free", lhs := 46, act := .unit, rhs := [.t (.exact (.punct "]" true false))] },
  { tag := "rbracket.glued", lhs := 46, act := .unit, rhs := [.t (.exact (.punct "]" true true))] },
  { tag := "atom.int-eq", lhs := 3, act := (.intCmp .eq false), rhs := [.n 37, .t (.content "is"), .t (.content "the"), .t (.content "same"), .t (.content "as"), .n 37] },
  { tag := "atom.less", lhs := 3, act := (.intCmp .lt false), rhs := [.n 37, .t (.content "is"), .t (.content "less"), .t (.content "than"), .n 37] },
  { tag := "atom.at-most", lhs := 3, act := (.intCmp .le false), rhs := [.n 37, .t (.content "is"), .t (.content "at"), .t (.content "most"), .n 37] },
  { tag := "atom.more", lhs := 3, act := (.intCmp .lt true), rhs := [.n 37, .t (.content "is"), .t (.content "more"), .t (.content "than"), .n 37] },
  { tag := "atom.at-least", lhs := 3, act := (.intCmp .le true), rhs := [.n 37, .t (.content "is"), .t (.content "at"), .t (.content "least"), .n 37] }
]

#guard orderRows.size == 25
#guard orderActs.size == orderRows.size
#guard terminatorFree ({ rules := orderRows.mapIdx fun i r => { lhs := r.lhs, rhs := r.rhs, act := i, tag := r.tag }, start := 0, rank := ranksStaged } : Grammar Terminal)

end VE.EnglishGrammar
