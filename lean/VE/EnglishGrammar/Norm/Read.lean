import VE.EnglishGrammar.Norm.Rules

/-! The reader of authored W1 rule blocks (docs/spec/english-lean-s6.md 2.6): `read`'s checks on the norm grammar,
then `lex`, then `readDocument` from `NState.init`, then `assemble`. Each sentence has exactly one derivation and
its piece is computed from it once; the pieces are assembled into statements. -/

namespace VE.EnglishGrammar.Norm
open VE.Grammar VE.EnglishGrammar

inductive NormOutcome where
  | ok (rs : List NormStatement)
  | invalidGrammar (why : GrammarFault)
  | lexical (r : Reject)
  | stopped (index : Nat) (o : VE.Grammar.Outcome Tok Reject Piece)
  | misplaced (f : BlockFault)

/-- `read`'s checks, on the norm grammar, in `read`'s order. The start type is `.norm`. Then `lex`, then
`readDocument` from `NState.init`, then `assemble`. -/
def readNorm (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : NormOutcome :=
  if !L.valid E O then .invalidGrammar .lexicon
  else if !((normGrammar E L).wf && terminatorFree (normGrammar E L)) then .invalidGrammar .notWellFormed
  else if !((normGrammar E L).typed sig (normTy E L) (normActs E L) &&
      decide (normTy E L (normGrammar E L).start = .norm)) then .invalidGrammar .notTyped
  else match lex s with
    | .error r => .lexical r
    | .ok sents =>
      match readDocument (normGrammar E L) (normMeaning (normGrammar E L) (normActs E L)) NState.init b
          sents.toList with
      | (.ok ps, _) =>
        match assemble (ps.map (·.1)) with
        | .ok rs => .ok rs
        | .error f => .misplaced f
      | (.stopped i o, _) => .stopped i o

def NormOneReading (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs : List NormStatement) : Prop :=
  L.valid E O = true ∧
  ∃ sents ps st2, lex s = .ok sents ∧
    VE.Grammar.DocOneReading (normGrammar E L) (normMeaning (normGrammar E L) (normActs E L)) NState.init
      (sents.toList.map (·.toList)) (ps.map (·, false)) st2 ∧
    assemble ps = .ok rs

end VE.EnglishGrammar.Norm
