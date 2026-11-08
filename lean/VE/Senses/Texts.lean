import VE.Senses.Document

/-! The texts of the new outcomes on a `senses.read` answer (docs/spec/senses.md 3.2; plan 2.8), batch sn-b6c.

Each is a fixed Lean text with its slots, relayed verbatim. A sentence or line number is shown as S2 shows one,
from 1. `Unresolved` is `unresolvedText` (`VE.Senses.Document`). The two candidates a `CandidatesDiverge` text
names are re-found as `openUnit` found them (`divergeGlosses`), since the fault keeps only their difference.
-/

namespace VE.Senses
open VE.Grammar VE.EnglishGrammar

/-- `gloss₁; gloss₂`: the glosses of a word's senses, in the dictionary's order. -/
def glossList (D : Dictionary) (w : String) : String := "; ".intercalate ((D.sensesOf w).map (·.gloss))

/-- `UnknownGloss` (3.2), `line` from 0. -/
def unknownGlossText (D : Dictionary) (line : Nat) (w g : String) : String :=
  "Line " ++ toString (line + 1) ++ " says " ++ w ++ " means " ++ g ++ ". The senses of " ++ w ++ " here are: " ++
    glossList D w ++ ". Use one of them."

/-- `TooManyCandidates` (3.2), `sentence` from 0. -/
def tooManyText (sentence : Nat) (words : List String) : String :=
  "Sentence " ++ toString (sentence + 1) ++ " uses " ++ countWord words.length ++ " words with no chosen sense: " ++
    andList words ++ ". Choose a sense for at least one of them first."

/-- `CandidatesDiverge` (3.2) for one word `w`: read as `g1` the sentence mentions the referent (or speaks of every
or some thing of a kind), read as `g2` it does not. -/
def divergeText (sentence : Nat) (w g1 g2 : String) (why : Divergence) : String :=
  let what := match why with
    | .referent x => "what the sentence is about: read as " ++ g1 ++ " it mentions " ++ x ++ ", read as " ++ g2 ++
        " it does not"
    | .binder => "whether the sentence speaks of every or some thing of a kind: read as " ++ g1 ++ " it does, read as " ++
        g2 ++ " it does not"
  "Sentence " ++ toString (sentence + 1) ++ " uses " ++ w ++ " with no chosen sense, and its senses do not agree on " ++
    what ++ ". Later sentences depend on that, so choose: add the line \"In this document, " ++ w ++ " means " ++ g1 ++
    ".\" (or " ++ g2 ++ "), or write " ++ w ++ " (meaning " ++ g1 ++ ")."

/-- `NoSenseFits` (3.2), the hint beside S2's `none` for a sentence with one unresolved word `w`. -/
def noSenseFitsText (D : Dictionary) (sentence : Nat) (w : String) : String :=
  "Sentence " ++ toString (sentence + 1) ++ " has no reading under any sense of " ++ w ++ ". The senses of " ++ w ++
    " here are: " ++ glossList D w ++ "."

/-- The `Mixed` warning (plan 2.8) for `w`, each sense's gloss with the sentences (from 0) it is used in. -/
def mixedText (w : String) (uses : List (String × List Nat)) : String :=
  "The word " ++ w ++ " is used in " ++ countWord uses.length ++ " senses here: " ++
    andList (uses.map fun (g, ns) => g ++ " (" ++ (if ns.length == 1 then "sentence " else "sentences ") ++
      ", ".intercalate (ns.map fun n => toString (n + 1)) ++ ")") ++ "."

/-- The `Unneeded` warning (plan 2.8) for a line of a word with one sense (`unneeded`). -/
def unneededText (w : String) : String := "The line for " ++ w ++ " is not needed: " ++ w ++ " has one sense."

/-- The glosses of the two candidates of body sentence `i` (of the text, preamble's `k` lines first) whose states
differ, as `openUnit` finds them: the first candidate and the first whose state differs from its. The one under
which the sentence mentions the referent, or speaks of every or some thing (`why`), comes first. -/
def divergeGlosses (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) (P : Projection)
    (b k i : Nat) (body : List (Array Tok)) (w : String) (why : Divergence) : Option (String × String) := do
  let (units, _) ← (readBody D A E L used P b k 0 DState.init (body.take (i - k))).toOption
  let cs ← (candidatesOf D A E L used b i (stateBefore units (i - k)) (← body[i - k]?) (choicesOf D [w]) 0).toOption
  let (c1, s1, _) ← cs.head?
  let (c2, _, _) ← cs.find? (·.2.1 != s1)
  let first := match why with
    | .referent x => s1.referents.contains x
    | .binder => s1.binderSeen
  pure (if first then (choiceGloss D c1 w, choiceGloss D c2 w) else (choiceGloss D c2 w, choiceGloss D c1 w))

end VE.Senses
