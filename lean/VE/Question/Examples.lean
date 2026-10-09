import VE.Question.Texts
import VE.EnglishGrammar.ReadExamples
import VE.EnglishGrammar.Run

namespace VE.Question
open VE.EnglishGrammar

#guard shape auxiliaries "Is it the case that every member is eligible?" =
  .caseThat "every member is eligible"
#guard shape auxiliaries "Is every member eligible?" =
  .fronted "is" "every member eligible"
#guard shape auxiliaries "Is every member eligible" = .notQuestion
#guard shape auxiliaries "Who is eligible?" = .other "Who"
#guard gaps "every member eligible" = [6, 13]
#guard gaps "Ann, bo" = [5]
#guard candidates auxiliaries "Is every member eligible?" =
  [⟨.fronted "is" 6, "every is member eligible."⟩,
   ⟨.fronted "is" 13, "every member is eligible."⟩]
#guard candidates auxiliaries "Is it the case that every member is eligible?" =
  [⟨.caseThat, "every member is eligible."⟩]
#guard indefiniteSwaps auxiliaries "Is a member eligible?" =
  some ("a", "Is every member eligible?", "Is some member eligible?")
#guard mapSpan ⟨.fronted "is" 6, "every is and."⟩ caseFrame.utf8ByteSize (5, 8) = (0, 9)
#guard mapSpan ⟨.fronted "is" 5, "\"é\" is and."⟩ caseFrame.utf8ByteSize (0, 4) = (3, 7)
#guard let q := "Is every and?"
  let p := mapSpan ⟨.fronted "is" 6, "every is and."⟩ caseFrame.utf8ByteSize (5, 8)
  decide (VE.EnglishGrammar.Run.codepointsBefore q p.1 ≤
    VE.EnglishGrammar.Run.codepointsBefore q p.2 ∧
    VE.EnglishGrammar.Run.codepointsBefore q p.2 ≤ q.length)
#guard let q := "Is \"é\" and?"
  let p := mapSpan ⟨.fronted "is" 5, "\"é\" is and."⟩ caseFrame.utf8ByteSize (0, 4)
  decide (VE.EnglishGrammar.Run.codepointsBefore q p.1 = 3 ∧
    VE.EnglishGrammar.Run.codepointsBefore q p.2 = 6 ∧
    VE.EnglishGrammar.Run.codepointsBefore q p.2 ≤ q.length)
#guard ("Is every member eligible?".utf8ByteSize ≤ maxQuestionBytes)

/-- The Q1 group fixture's vocabulary, built by the same fixture decoder used by the English reader. -/
def groupEnv : Env := VE.EnglishGrammar.ReadExamples.env
  (VE.EnglishGrammar.ReadExamples.envJson false [("member", none)]
    [("registered", ["member"], "{0} is registered", none),
     ("eligible", ["member"], "{0} is eligible", none),
     ("verified", ["member"], "{0} is verified", none)]
    [("ann", "member"), ("bo", "member")])

def groupLex : Lexicon := {
  nouns := [("member", "member")], letters := [("member", "M")],
  wordings := [("registered", "{0} is registered"), ("eligible", "{0} is eligible"),
    ("verified", "{0} is verified")],
  negatives := [], aliases := [], spellings := [("ann", "ann"), ("bo", "bo")] }

def isOne (o : Outcome) : Bool := match o with | .one .. => true | _ => false
def isNone (o : Outcome) : Bool := match o with | .none .. => true | _ => false
def isIndefinite (o : Outcome) : Bool := match o with | .indefinite .. => true | _ => false

#guard formText auxiliaries ==
  "VE answers questions that begin with \"Is\", \"Must\" or \"May\", or with \"Is it the case that\" followed by a sentence."
#guard formText ["is"] ==
  "VE answers questions that begin with \"Is\", or with \"Is it the case that\" followed by a sentence."
#guard groupLex.policyOk groupEnv {} == true
#guard match readQuestion auxiliaries groupEnv {} groupLex 2100000 "Is every member eligible?" with
  | .one c φ => c == ⟨.fronted "is" 13, "every member is eligible."⟩ &&
      φ == .all "member" (.pred "eligible" [.var 0])
  | _ => false
#guard isOne (readQuestion auxiliaries groupEnv {} groupLex 2100000
  "Is it the case that every member is eligible?")
#guard match readQuestion auxiliaries groupEnv {} groupLex 0 "Is every member eligible?" with
  | .budget c => c == ⟨.fronted "is" 6, "every is member eligible."⟩
  | _ => false
#guard match readQuestion auxiliaries groupEnv {} groupLex 2100000 "Is a member eligible?" with
  | .indefinite art rs => art == "a" &&
      rs == ["Is every member eligible?", "Is some member eligible?"]
  | _ => false
#guard match readQuestion auxiliaries groupEnv {} groupLex 2100000 "Must Ann be eligible?" with
  | .none (some c) => c == ⟨.fronted "must" 4, "Ann must be eligible."⟩
  | _ => false
#guard isNone (readQuestion auxiliaries groupEnv {} groupLex 2100000
  "Is it the case that every member is happy?")

end VE.Question
