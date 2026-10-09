import VE.Senses.Document
import VE.Senses.Fixtures

/-! The fixtures of RD-8 (readings-defaults plan, section 6), as `#guard` checks: the senses spec's s1, s9,
s16 and s22 as a document's English fences read as `ve senses check` reads their text; front-matter
defaults read as the same text with the lines written; the refusals of a request. -/

namespace VE.Senses.DocumentExamples
open VE.Grammar VE.EnglishGrammar VE.Senses VE.Senses.Fixtures

/-- A request's outcome without trees and projection, or the text of its refusal. -/
def rd (A : List (String × Nat)) (t : SenseText) (D : Dictionary := F) (b : Nat := workBudget) :
    Except String Out :=
  (readDocument D EJ LJ b ⟨A⟩ t).map out

def is (x : Except String Out) (y : Out) : Bool :=
  match x with
  | .ok o => o == y
  | .error _ => false

def refused (x : Except String Out) (text : String) : Bool :=
  match x with
  | .error e => e == text
  | .ok _ => false

/-- `fenceUnits` of a fence request. -/
def units (A : List (String × Nat)) (fs : List String) : List (Option Nat) :=
  match documentInput F ⟨A⟩ (.fences fs) with
  | .ok (.ok (d, sents)) => fenceUnits F workBudget d sents fs.length
  | _ => []

/-- The English of each open unit of a request, as the runner writes it (`documentText`). -/
def texts (D : Dictionary) (A : List (String × Nat)) (t : SenseText) : List String :=
  match readDocument D EJ LJ workBudget ⟨A⟩ t, documentInput D ⟨A⟩ t with
  | .ok (.ok us _ _ _ _), .ok (.ok (d, sents)) =>
    (us.mapIdx fun i u => (i, u)).filterMap fun (i, u) =>
      if u.candidates.isEmpty then none else some (documentText D ⟨A⟩ d (sents.length - us.length + i) u)
  | _, _ => []

def s9 : String := doc [lineFunny, "In this document, odd means strange.", "Every funny joke is odd."]
def s16 : String := "The riddle is odd."
def s22 : String := "Both the riddle is odd and the riddle is funny (meaning strange)."

/-! ## A source with no defaults reads as `ve senses check` reads it (`readDocument_source`) -/

#guard [J, s9, s16, s22, "Alice tells the riddle."].all fun s => is (rd [] (.source s)) (rs F EJ LJ s)

/-! ## s1, s9, s16, s22 as fences: the same formulas and the same refusals -/

#guard is (rd [] (.fences (lineFunny :: Jbody))) (rs F EJ LJ J)                                   -- s1
#guard is (rd [] (.fences (lineFunny :: Jbody))) (.stopped 1 .none)
#guard is (rd [] (.fences [lineFunny, "In this document, odd means strange.", "Every funny joke is odd."]))
  (rs F EJ LJ s9)                                                                                 -- s9
#guard units [] [lineFunny, "In this document, odd means strange.", "Every funny joke is odd."] ==
  [none, none, some 0]
#guard is (rd [] (.fences [s16])) (rs F EJ LJ s16)                                                -- s16
#guard is (rd [] (.fences [s22])) (rs F EJ LJ s22)                                                -- s22
#guard units [] [s16] == [some 0]

/-! ## Front-matter defaults read as the same text with the lines written -/

#guard is (rd [("funny", 1), ("odd", 1)] (.fences ["Every funny joke is odd."])) (rs F EJ LJ s9)
#guard is (rd [("funny", 1), ("odd", 1)] (.source "Every funny joke is odd.")) (rs F EJ LJ s9)
#guard units [("funny", 1), ("odd", 1)] ["Every funny joke is odd."] == [some 0]
#guard is (rd [("funny", 1)] (.fences Jbody)) (rs F EJ LJ J)
#guard is (rd [("odd", 1)] (.fences [s16])) (rs F EJ LJ (doc ["In this document, odd means strange.", s16]))
-- a default resolves the open unit of s16
#guard match rd [("odd", 1)] (.fences [s16]) with
  | .ok (.ok [u] _ _ _) => u.candidates.isEmpty && u.formula.isSome
  | _ => false

/-! ## Refusals of a request, in order -/

#guard refused (rd [("funny", 1)] (.fences [lineFunny, "The riddle is funny."])) bothText
#guard refused (rd [("funny", 1)] (.source (doc [lineFunny, "The riddle is funny."]))) bothText
-- no defaults: the written line is the preamble
#guard is (rd [] (.fences [lineFunny, "The riddle is funny."])) (rs F EJ LJ (doc [lineFunny, "The riddle is funny."]))
-- empty defaults are no defaults
#guard is (rd [] (.fences [lineFunny, s16])) (rs F EJ LJ (doc [lineFunny, s16]))
#guard refused (rd [("funny", 3)] (.fences [s16])) (defaultText "funny" 3)
#guard refused (rd [("zany", 1)] (.fences [s16])) (defaultText "zany" 1)
#guard refused (rd [("funny", 0)] (.fences [s16])) (defaultText "funny" 0)
#guard refused (rd [] (.fences ["Alice tells the riddle. The riddle is odd."])) (fenceText 0 2)
#guard refused (rd [] (.fences [s16, "Alice tells the riddle. The riddle is odd. Alice tells it."])) (fenceText 1 3)
#guard is (rd [] (.fences ["The riddle is odd"])) (.lexical .unterminated)
#guard is (rd [] (.fences [""])) (.lexical .emptyDocument)
#guard is (rd [] (.fences [])) (.lexical .emptyDocument)
-- a lexical rejection of an earlier fence comes before the count of a later one
#guard is (rd [] (.fences ["The riddle is odd", "A. B."])) (.lexical .unterminated)
-- the dictionary comes first, as in `readWithSenses`
#guard match rd [("funny", 3)] (.fences ["A. B."]) (Fwith (swap sOdd1 { sOdd1 with gloss := "odd" })) with
  | .ok (.fault (.invalidDictionary _)) => true
  | _ => false

/-! ## The English of an open unit (senses plan 2.8; spec 3.2, R11) -/

#guard texts F [] (.fences [s16]) == ["Sentence 1 uses odd, which has two senses here, and only strange gives " ++
  "a reading of this sentence. Add the line \"In this document, odd means strange.\" to say so."]
#guard texts F [] (.fences [lineFunny, s16]) == ["Sentence 2 uses odd, which has two senses here, and only " ++
  "strange gives a reading of this sentence. Add the line \"In this document, odd means strange.\" to say so."]
#guard texts F [] (.fences [s22]) == ["Sentence 1 uses odd, which has two senses here, and only strange gives " ++
  "a reading of this sentence. Add the line \"In this document, odd means strange.\" to say so."]
-- plan 2.8's text, several candidates of one word
#guard texts F [] (.fences ["The riddle is funny."]) == ["Sentence 1 uses funny, which has two senses here: " ++
  "amusing; strange. Add the line \"In this document, funny means amusing.\" or write funny (meaning strange)."]
-- several words (s12)
#guard texts F2 [] (.source "Both alice tells the riddle and the riddle is funny.") ==
  ["Sentence 1 uses funny and tells, which have more than one sense here, and four choices of their senses " ++
   "give a reading of this sentence. Add lines such as \"In this document, funny means amusing.\" and " ++
   "\"In this document, tells means says aloud.\" to choose their senses."]
-- a resolved document has no such text
#guard texts F [("odd", 1)] (.fences [s16]) == []
-- With front-matter defaults the rendered lines are not the author's sentences, so they are not counted, and
-- a written line is refused (`bothText`), so the text asks for a default in the front matter.
#guard texts F [("funny", 1)] (.fences [s16]) == ["Sentence 1 uses odd, which has two senses here, and only " ++
  "strange gives a reading of this sentence. Add the default \"odd\": 1 to the front matter to say so."]
#guard texts F [("funny", 1)] (.fences ["Alice tells the riddle.", s16]) == ["Sentence 2 uses odd, which has two " ++
  "senses here, and only strange gives a reading of this sentence. Add the default \"odd\": 1 to the front " ++
  "matter to say so."]
#guard texts F [("odd", 1)] (.fences ["The riddle is funny."]) == ["Sentence 1 uses funny, which has two senses " ++
  "here: amusing; strange. Add the default \"funny\": 1 to the front matter or write funny (meaning strange)."]
#guard texts F2 [("odd", 1)] (.fences ["Both alice tells the riddle and the riddle is funny."]) ==
  ["Sentence 1 uses funny and tells, which have more than one sense here, and four choices of their senses " ++
   "give a reading of this sentence. Add defaults such as \"funny\": 1 and \"tells\": 1 to the front matter " ++
   "to choose their senses."]
-- the written line the old text asked for is refused under defaults
#guard refused (rd [("funny", 1)] (.fences ["In this document, odd means strange.", s16])) bothText
#guard choiceDefaults F [("funny", 1), ("odd", 1), ("zany", 1)] == "\"funny\": 1 and \"odd\": 1"
#guard countWord 2 == "two" && countWord 11 == "11" && andList ["a", "b", "c"] == "a, b and c"

end VE.Senses.DocumentExamples
