import VE.Question.Texts
import VE.Question.Run
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

-- G24: speech acts' auxiliaries (`["is"]`, Q1.4) on G.
#guard match readQuestion ["is"] groupEnv {} groupLex 2100000 "Is Ann eligible?" with
  | .one c φ => c == ⟨.fronted "is" 4, "Ann is eligible."⟩ && φ == .pred "eligible" [.const "ann"]
  | _ => false
#guard match readQuestion ["is"] groupEnv {} groupLex 2100000 "Must Ann be eligible?" with
  | .form wh => !wh
  | _ => false
#guard formText ["is"] ==
  "VE answers questions that begin with \"Is\", or with \"Is it the case that\" followed by a sentence."
#guard isOne (readQuestion ["is"] groupEnv {} groupLex 2100000 "Is it the case that Ann is eligible?")

-- G21: the work budget 0 stops at the first candidate (`Budget`), which the mode reports as row 9.
#guard match Run.outcomeFields [] "Is every member eligible?" groupEnv groupLex
    (readQuestion auxiliaries groupEnv {} groupLex 0 "Is every member eligible?") with
  | .ok fs => fs.lookup "code" == some (.str "Budget") && fs.lookup "status" == some (.str "budget") &&
      fs.lookup "text" == some (.str "VE stopped reading this question at its work limit.") &&
      fs.lookup "span" == some (Lean.Json.arr #[Lean.toJson (0 : Nat), Lean.toJson (25 : Nat)])
  | .error _ => false

-- The A0 gate (spec 3.3; `VE.Question.Frames`): the line passes only as A0, with its sentence's own formula.
#guard let φ := EFormula.all "member" (.pred "eligible" [.var 0])
  askedGate groupEnv {} groupLex 2100000 φ "You asked whether every member is eligible." &&
  !askedGate groupEnv {} groupLex 2100000 φ "You asked whether every member is verified." &&
  !askedGate groupEnv {} groupLex 2100000 φ "You asked whether every member is happy." &&
  !askedGate groupEnv {} groupLex 2100000 φ "You asked whether every member is eligible" &&
  !askedGate groupEnv {} groupLex 2100000 φ "Yes." &&
  !askedGate groupEnv {} groupLex 2100000 φ "Sentence 1 says: \"You asked whether every member is eligible.\""
#guard frameReadings "Yes." = [("A1", [])]
#guard frameReadings "You asked whether Ann is eligible." = [("A0", ["Ann is eligible"])]
#guard (frameReadings "If sentence 1 means \"a\", yes.").length == 1
#guard frameReadings "You asked about Ann." = []

-- The moved-word rule (`VE.Question.Moved`): the clause after `who` in G11's one candidate is tokens [3, 5).
#guard match oneTree groupEnv groupLex 2100000 "every member who is registered is eligible." with
  | some (toks, t) => clauses (toks.map (·.1)) 0 t == [(3, 5)] &&
      inClause (toks.map (·.1)) t 3 && !inClause (toks.map (·.1)) t 5
  | none => false
#guard movedOut groupEnv groupLex 2100000 ⟨.fronted "is" 17, "every member who is registered is eligible."⟩
#guard !movedOut groupEnv groupLex 2100000 ⟨.fronted "is" 31, "every member who is registered is eligible."⟩
#guard !movedOut groupEnv groupLex 2100000 ⟨.caseThat, "every member who is registered is eligible."⟩
-- A put-back word that is not a token start, or a sentence with no single tree, counts as moved.
#guard movedOut groupEnv groupLex 2100000 ⟨.fronted "is" 18, "every member who is registered is eligible."⟩
#guard movedOut groupEnv groupLex 2100000 ⟨.fronted "is" 6, "every is member eligible."⟩
#guard match ask auxiliaries groupEnv {} groupLex 2100000 "Is every member who registered is eligible?" with
  | .moved c rs => c.sentence == "every member who is registered is eligible." &&
      rs == ["Is every member who is registered eligible?"]
  | _ => false
#guard askable auxiliaries groupEnv {} groupLex 2100000 "Is every member who is registered eligible?"
#guard !askable auxiliaries groupEnv {} groupLex 2100000 "Is every member who registered is eligible?"
-- Before the ruling, readQuestion offered the moved question as the indefinite rephrasing (G27).
#guard match readQuestion auxiliaries groupEnv {} groupLex 2100000 "Is a member who registered is eligible?" with
  | .indefinite _ rs => rs == ["Is every member who registered is eligible?"]
  | _ => false
#guard match ask auxiliaries groupEnv {} groupLex 2100000 "Is a member who registered is eligible?" with
  | .read (.none _) => true
  | _ => false

end VE.Question
