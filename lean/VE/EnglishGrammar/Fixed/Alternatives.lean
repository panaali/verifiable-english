import VE.EnglishGrammar.Catalogue

/-! The fixed rules of the profile `alternatives@0` (docs/spec/english-lean-s3.md 2.5), in the format of
`tools/english_grammar_gen.py`: one `FixedRow` per row of spec 2.5's table in its order, and the action of each
rule as the `act` text of the `english.grammar` export. Written by the Lean work item of S3 from the spec's
table; S3.0's generator renders this module from `ve/english_grammar/alternatives@0.json` and must give the same rows.
Fixed rule `k` of a profile list's table has `act := k` (`fixedRules`). -/

namespace VE.EnglishGrammar
open VE.Grammar

/-- The action of each fixed rule of the table, as the `act` text of the `english.grammar` export. -/
def alternativesActs : Array String := #[
  "nest",
  "through",
  "relOr",
  "relOr",
  "relAnd",
  "through",
  "verbSubject",
  "verbSame"
]

/-- The fixed rows of `alternatives@0`. -/
def alternativesRows : Array FixedRow := #[
  { tag := "formula.alternatives", lhs := 2, act := .nest, rhs := [.n 47] },
  { tag := "verb-phrase.one", lhs := 48, act := .through, rhs := [.n 49] },
  { tag := "verb-phrase.either", lhs := 48, act := .relOr, rhs := [.t (.kw "either"), .n 49, .t (.kw "or"), .n 49] },
  { tag := "verb-phrase.either-both", lhs := 48, act := .relOr, rhs := [.t (.kw "either"), .n 49, .t (.kw "or"), .n 49, .t (.exact (.punct "," true false)), .t (.kw "or"), .t (.kw "both")] },
  { tag := "verb-phrase.both", lhs := 48, act := .relAnd, rhs := [.t (.kw "both"), .n 49, .t (.kw "and"), .n 49] },
  { tag := "verb-atom.relative", lhs := 49, act := .through, rhs := [.n 21] },
  { tag := "verb-atom.subject", lhs := 49, act := .verbSubject, rhs := [.n 50, .n 21] },
  { tag := "verb-atom.same", lhs := 49, act := .verbSame, rhs := [.n 50, .t (.content "is"), .t (.content "the"), .t (.content "same"), .t (.content "as"), .n 17] }
]

#guard alternativesRows.size == 8
#guard alternativesActs.size == alternativesRows.size
#guard terminatorFree ({ rules := alternativesRows.mapIdx fun i r => { lhs := r.lhs, rhs := r.rhs, act := i, tag := r.tag }, start := 0, rank := ranksStaged } : Grammar Terminal)

end VE.EnglishGrammar
