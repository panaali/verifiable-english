import VE.Senses.RunExamples

/-! The members sn-b6c adds to a `senses.read` route answer, as `#guard` checks: each text of spec 3.2 and plan 2.8
with its slots filled, exactly as the spec words it; each sense-map entry's gloss and bytes in its source. -/

namespace VE.Senses.TextsExamples
open Lean VE.EnglishGrammar VE.Senses VE.Senses.Fixtures VE.Senses.Run VE.Senses.RunExamples

-- the texts, slot by slot (spec 3.2; plan 2.8 for Mixed and Unneeded)
#guard unknownGlossText F 0 "funny" "purple" ==
  "Line 1 says funny means purple. The senses of funny here are: amusing; strange. Use one of them."
#guard tooManyText 2 ["warm", "cool", "mild"] ==
  "Sentence 3 uses three words with no chosen sense: warm, cool and mild. Choose a sense for at least one of them first."
#guard divergeText 0 "near" "beside" "beside bob" (.referent "bob") ==
  "Sentence 1 uses near with no chosen sense, and its senses do not agree on what the sentence is about: read as " ++
  "beside it mentions bob, read as beside bob it does not. Later sentences depend on that, so choose: add the line " ++
  "\"In this document, near means beside.\" (or beside bob), or write near (meaning beside)."
#guard divergeText 1 "w" "a" "b" .binder ==
  "Sentence 2 uses w with no chosen sense, and its senses do not agree on whether the sentence speaks of every or " ++
  "some thing of a kind: read as a it does, read as b it does not. Later sentences depend on that, so choose: add " ++
  "the line \"In this document, w means a.\" (or b), or write w (meaning a)."
#guard noSenseFitsText F 0 "funny" ==
  "Sentence 1 has no reading under any sense of funny. The senses of funny here are: amusing; strange."
#guard mixedText "funny" [("amusing", [1, 4]), ("strange", [1, 3])] ==
  "The word funny is used in two senses here: amusing (sentences 2, 5) and strange (sentences 2, 4)."
#guard mixedText "funny" [("amusing", [2]), ("strange", [3])] ==
  "The word funny is used in two senses here: amusing (sentence 3) and strange (sentence 4)."
#guard unneededText "odd" == "The line for odd is not needed: odd has one sense."

-- the two candidates a divergence names, the one that mentions the referent first, as `openUnit` finds them
#guard (do
  let sents ← (lex "Alice is near bob.").toOption
  let (A, k, body, used, P) ← bodyOf Fn { caseJ with E := EJn, L := LJn } workBudget sents.toList
  divergeGlosses Fn A EJn LJn used P workBudget k 0 body "near" (.referent "bob")) == some ("beside", "beside bob")

/-- A route answer's reading. -/
def reading (s : String) : Json := ((runCaseReported (src s)).getObjValD "result").getObjValD "reading"

/-- Each sense-map entry's gloss and the bytes of `s` its span covers. -/
def entries (s : String) : List (String × String) :=
  match (reading s).getObjValD "sense_map" with
  | .arr es => es.toList.map fun e =>
    let n (k : String) : Nat := ((e.getObjValD k).getNat?).toOption.getD 0
    (((e.getObjValD "gloss").getStr?).toOption.getD "",
     (String.fromUTF8? (s.toUTF8.extract (n "byte_start") (n "byte_stop"))).getD "")
  | _ => []

-- bytes over a preamble, line breaks and double spaces; a glossed head covers its gloss; both candidates of an open
-- unit share their word's bytes, each with its own sense's gloss
#guard entries ("In this document, funny means amusing.\nIn this document, odd means strange.\n\nEvery  funny joke is odd. The riddle is funny (meaning strange).") ==
  [("amusing", "funny"), ("strange", "odd"), ("strange", "funny (meaning strange)")]
#guard entries "The riddle is funny." == [("amusing", "funny"), ("strange", "funny")]
-- a fence answer has glosses and no bytes
#guard match (((runCaseReported (fenced ["The riddle is funny.\n"] ["u1"] ["u1"])).getObjValD "result").getObjValD
    "reading").getObjValD "sense_map" with
  | .arr es => es.all fun e => (e.getObjValD "gloss").getStr?.toOption.isSome && (e.getObjVal? "byte_start").toOption.isNone
  | _ => false

-- the warnings and an open unit's text on a source answer
#guard (reading "In this document, tells means says aloud. Alice tells the riddle.").getObjValD "warnings" ==
  Json.arr #[Json.mkObj [("code", "Unneeded"), ("word", "tells"),
    ("text", "The line for tells is not needed: tells has one sense.")]]
#guard ((((reading "The riddle is funny.").getObjValD "units").getArrVal? 0).toOption.map (·.getObjValD "text")) ==
  some (.str ("Sentence 1 uses funny, which has two senses here: amusing; strange. Add the line \"In this document, " ++
    "funny means amusing.\" or write funny (meaning strange)."))
-- NoSenseFits beside S2's `none`: one unresolved word, no candidate
#guard (reading "Alice is funny.").getObjValD "hint" == Json.mkObj [("code", "NoSenseFits"),
  ("text", "Sentence 1 has no reading under any sense of funny. The senses of funny here are: amusing; strange.")]
-- a refusal under front-matter defaults has no source: S2's fields as they are, every one of them
#guard (((runCaseReported (fenced ["Alice is funny.\n"] ["u1"] [] [("funny", 1)])).getObjValD "result").getObjValD
  "reading").compress == "{\"class\":\"TypeMismatch\",\"code\":\"IllTyped\",\"status\":\"rejected\"," ++
  "\"text\":\"The text was read, and its formulas do not pass the type check.\"}"

end VE.Senses.TextsExamples
