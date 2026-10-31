import VE.Senses.Run
import VE.Senses.Fixtures

/-! The runner's projection helpers (senses plan 2.6, 2.7, B6) as `#guard` checks: the projected lexicon is one
`english.read` reads back; preamble lines project as a document with those lines does; a candidate's identities
are its projection's; and a fault's status is `senses.read`'s. -/

namespace VE.Senses.RunExamples
open Lean VE.EnglishGrammar VE.Senses VE.Senses.Fixtures VE.Senses.Run

def caseJ : VE.EnglishGrammar.Run.Case := { E := EJ, O := {}, L := LJ, overlayFailure := none, identities := [] }

def lineFunny2 : String := "In this document, funny means strange."

/-- A lexicon with an entry in every list, a negated alias among them. -/
def LA : Lexicon :=
  { nouns := LJ.nouns, letters := LJ.letters, wordings := [("p", "{0} is p")],
    negatives := [("p", "{0} is not p")], aliases := [("p", "{0} is q", true), ("p", "{0} is r", false)],
    spellings := LJ.spellings }

#guard [LJ, LA].all fun L => match VE.EnglishGrammar.Run.decodeLexicon "e" (lexiconJson "e" L) with
  | .ok L' => reprStr L' == reprStr L
  | .error _ => false
#guard (VE.EnglishGrammar.Run.decodeLexicon "f" (lexiconJson "e" LJ)).toOption.isNone

/-- The projection of `lines` over `used`, against `project` under the assignment the lines give. -/
def sameAs (lines : String) (A : List (String × Nat)) (used : List String) : Bool :=
  match linesProjection F caseJ workBudget lines used, project F ⟨A⟩ EJ LJ used with
  | .ok (.ok P), .ok Q => P.envJson == Q.envJson && reprStr P.map == reprStr Q.map && reprStr P.lexicon == reprStr Q.lexicon
  | _, _ => false

#guard sameAs lineFunny2 [("funny", 2)] ["funny"]
#guard sameAs (lineFunny2 ++ "\nIn this document, tells means says aloud.") [("funny", 2), ("tells", 1)] ["funny", "tells"]
#guard sameAs "" [] ["funny", "tells"]
#guard !sameAs lineFunny2 [("funny", 1)] ["funny"]
#guard match linesProjection F caseJ workBudget (lineFunny2 ++ " The riddle is funny.") ["funny"] with
  | .error e => e == "InvalidInput: sentence 2 of the lines is not a preamble line"
  | .ok _ => false
#guard match linesProjection F caseJ workBudget "In this document, funny means purple." ["funny"] with
  | .ok (.error f) => f.code == "UnknownGloss"
  | _ => false

#guard match project F ⟨[]⟩ EJ LJ ["funny", "tells"], project F ⟨[]⟩ EJ LJ [] with
  | .ok P, .ok Q => usedOf P == ["funny", "tells"] && usedOf Q == []
  | _, _ => false

/-- The identities of the projection of `lines` over `funny`. -/
def idsOf (lines : String) : List (String × Json) :=
  match linesProjection F caseJ workBudget lines ["funny"] with
  | .ok (.ok P) => match projectionIds caseJ P with
    | .ok (lexicon, ids) => ids ++ [("lexicon", lexicon)]
    | .error _ => []
  | _ => []

#guard match idsOf lineFunny2, idsOf "In this document, funny means amusing.", project F ⟨[("funny", 2)]⟩ EJ LJ ["funny"] with
  | [("environment_id", .str e2), ("lexicon_id", .str l2), ("grammar_id", .str g2), ("lexicon", lex)],
    [("environment_id", .str e1), ("lexicon_id", .str l1), ("grammar_id", .str g1), _], .ok Q =>
    e2 != e1 && l2 != l1 && g2 == g1 &&
    (VE.EnglishGrammar.Run.environmentId Q.envJson).toOption == some e2 &&
    (VE.CertificateWire.digest "ve-english-lexicon-v1\n" lex).toOption == some l2 &&
    (VE.EnglishGrammar.Run.grammarId EJ.profiles).toOption == some g2 && lex.getObjValD "environment_id" == .str e2
  | _, _, _ => false

#guard (faultJson (.preambleBudget 0)).getObjValD "status" == .str "budget"
#guard (faultJson (.unknownWord 0 "x")).getObjValD "status" == .str "rejected"
#guard (faultJson (.unknownWord 0 "x")).getObjValD "code" == .str "UnknownWord"

end VE.Senses.RunExamples
