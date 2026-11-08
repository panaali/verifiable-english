import VE.EnglishGrammar.JudgmentLines

/-! The rows of `VE.EnglishGrammar.JudgmentLines` (spec 9.1, 9.2, 9.5; plan 2.4), on the accepting and the refusing side. -/

namespace VE.EnglishGrammar.JudgmentLinesExamples
open Lean VE.EnglishGrammar VE.EnglishGrammar.JudgmentLines VE.Judgments

def arbitrary : Judgment := ⟨"arbitrary", ["act"], "unstated", []⟩
def governed : Judgment := ⟨"arbitrary", ["act"], "governance_function", []⟩
def unfair : Judgment := ⟨"treats_unfairly", ["person", "person"], "unstated", []⟩
def weighs : Judgment := ⟨"weighs", ["person", "act", "act"], "court", []⟩
def noWording : Judgment := ⟨"held", [], "unstated", []⟩

def arbitraryLine : String :=
  "Whether an act is classified as \"arbitrary\" is a judgment; the text does not say who makes it."
def governedLine : String := "Whether an act is classified as \"arbitrary\" is a judgment for the governance function."
def unfairLine : String :=
  "Whether a person has the recorded relation \"treats_unfairly\" to a person (the same or another) is a judgment; " ++
    "the text does not say who makes it."
def weighsLine : String :=
  "Whether a person has recorded relation weighs with argument two an act and argument three an act (the same or " ++
    "another) is a judgment for the court."

-- The declaration row names the decider, or says the text names none, one line per term.
#guard declarationLine arbitrary == some arbitraryLine
#guard declarationLine governed == some governedLine
#guard declarationLine unfair == some unfairLine
#guard declarationLine weighs == some weighsLine
#guard declarationLine noWording == none
#guard atom "lists" ["person", "act", "act", "person"] == some ("a person has recorded relation lists with argument " ++
  "two an act and argument three an act (the same or another) and argument four a person (the same or another)")
#guard atom "lists" (List.replicate 7 "act") == none

-- Round trip, accepting: each line reads to its record, and only to it.
#guard [arbitrary, governed, unfair, weighs].all fun j => (declarationLine j).bind parseLine == some j
-- Round trip, refusing: every other spelling of a line has no reading.
#guard ["Whether", arbitraryLine ++ " ", " " ++ arbitraryLine, arbitraryLine.dropRight 1, governedLine.replace "the governance" "governance",
    governedLine.replace "an act" "a act", governedLine.replace "an act" "an  act", governedLine.replace "Whether" "whether",
    governedLine.replace "for the governance function" "for the unstated", governedLine.replace "\"arbitrary\"" "arbitrary",
    governedLine.replace "for the governance function." "for the ."].all (parseLine · == none)
#guard parseLine (arbitraryLine ++ " And whether an act is a judgment.") == none
#guard parseLine (governedLine.replace "the governance" "the  governance") == none
#guard parseLine (governedLine.replace "Whether" "Weather") == none

-- The legend: the declaration with its decider, then the factors when there are any.
#guard legendLines governed == [governedLine]
#guard legendLines { arbitrary with factors := ["the Declaration gives no test", "see the preamble"] } ==
  [arbitraryLine, "The text mentions these points: the Declaration gives no test; see the preamble."]
#guard legendLines noWording == []
#guard factorsLine { arbitrary with factors := ["one point"] } == some "The text mentions these points: one point."
#guard factorsLine arbitrary == none

-- The status line says "uses": neutral, in the order given, and no line without a judgment.
#guard statusLine [arbitrary] == some "Open: this uses the judgment whether an act is classified as \"arbitrary\"."
#guard statusLine [arbitrary, unfair] == some ("Open: this uses the judgments whether an act is classified as " ++
  "\"arbitrary\" and whether a person has the recorded relation \"treats_unfairly\" to a person (the same or another).")
#guard statusLine [arbitrary, governed, weighs] == some ("Open: this uses the judgments whether an act is classified " ++
  "as \"arbitrary\", whether an act is classified as \"arbitrary\" and whether a person has recorded relation weighs " ++
  "with argument two an act and argument three an act (the same or another).")
#guard statusLine [] == none
#guard statusLine [arbitrary, noWording] == none

-- A W2 record and its predicate; W2's check and the admission's decider check answer for them.
def errorOf (r : Except String (Json × String × List String)) : String :=
  match r with
  | .error e => e
  | .ok _ => ""
#guard (readDeclaration governedLine "udhr").toOption == some (recordJson governed "udhr", "arbitrary", ["act"])
#guard ((readDeclaration unfairLine "udhr").toOption.map (·.2)) == some ("treats_unfairly", ["person", "person"])
#guard (recordJson governed "udhr").getObjValD "decided_by" == .str "governance_function"
#guard (recordJson governed "udhr").getObjValD "jurisdiction" == .str "udhr"
#guard errorOf (readDeclaration "No line." "udhr") == lineFault
#guard errorOf (readDeclaration (governedLine.replace "governance function" "unresolved decider") "udhr") ==
  "JudgmentDecider: arbitrary"
#guard errorOf (readDeclaration governedLine "two words") == "open term needs a decision role and jurisdiction"
#guard (readDeclaration weighsLine "udhr").toOption.map (·.2.2) == some ["person", "act", "act"]

-- 9.5's refusal, each form (DRI 2026-11-02, jt-3 item 4). The first sentence is 9.5's for every row.
def rowOf (w : List String) : EvaluativeRow := ⟨w, []⟩
def text (w ws : List String) (sort : Option String := none) : String := refusalText (rowOf w) ws sort
#guard text ["reasonable"] ["reasonable", "limit"] == "'Reasonable' is a judgment. Say who decides it ('… is a " ++
  "judgment for the operator'), or define it ('In this document, a reasonable limit means …')."
#guard text ["arbitrary"] ["arbitrary", "arrest"] == "'Arbitrary' is a judgment. Say who decides it ('… is a judgment " ++
  "for the operator'), or define it ('In this document, an arbitrary arrest means …')."
#guard text ["arbitrary"] ["arbitrary", "0", "is", "arbitrary"] (some "public_act") == "'Arbitrary' is a judgment. Say " ++
  "who decides it ('… is a judgment for the operator'), or define it ('In this document, an arbitrary public act means …')."
def quoted (w : String) : String :=
  s!"'{w.capitalize}' is a judgment. Say who decides it ('… is a judgment for the operator'), or define it " ++
    s!"('In this document, \"{w}\" means …')."
#guard text ["arbitrarily"] ["acts", "arbitrarily"] (some "act") == quoted "arbitrarily"
#guard text ["good", "judgment"] ["good", "judgment", "use"] (some "act") == quoted "good judgment"
#guard text ["overly"] ["overly", "cautious"] == quoted "overly cautious"
#guard text ["reasonable"] ["reasonable"] == quoted "reasonable"
#guard text ["reasonable"] ["reasonable", "grounds"] (some "act") == quoted "reasonable"

def pred (name : String) (wording : Option String := none) : PredDecl :=
  { name, arity := 1, wording, args := ["limit"] }
def env : Env :=
  { sorts := [], constants := [],
    predicates := [pred "reasonable_limit", pred "reasonable_grounds", pred "due_date", pred "arrest", pred "rule_ok" (some "{0} is fair"),
      pred "sense__just_1", pred "defined_fair", pred "fair_defined", pred "good_judgment", pred "arbitrary",
      { pred "just" with args := ["act", "limit"] }],
    source := Json.mkObj [("vocabulary", Json.mkObj [("predicates", Json.mkObj
      ((["defined_fair", "fair_defined"].map fun p => (p, Json.mkObj [("defined", Json.mkObj [])])) ++
        [("rule_ok", Json.mkObj [("description", .str "not defined")])]))])] }
def holds (p : String) : EFormula := .pred p [.const "x"]
def firstNamed (J : List String) (fs : List EFormula) : Option (Nat × String) :=
  (refusal env J fs).map fun (i, t) => (i, (t.splitOn "' is")[0]!)

#guard preds (.and (holds "a") (.implies (.not (holds "b")) (.ex "s" (.or (holds "a") (holds "c"))))) == ["a", "b", "a", "c"]
#guard preds (.reachNamed false "r" (.const "x") (.const "y")) == ["r"]
#guard preds (.reachBody false "s" (holds "b") (.const "x") (.const "y")) == ["b"]
#guard preds (.eq (.const "x") (.const "y")) == []
-- Accepting and refusing: bound per predicate, and in the reading's order.
#guard firstNamed [] [holds "reasonable_limit"] == some (0, "'Reasonable")
#guard firstNamed ["reasonable_limit"] [holds "reasonable_limit"] == none
#guard firstNamed ["reasonable_grounds"] [holds "reasonable_limit"] == some (0, "'Reasonable")
#guard (refusal env ["reasonable_limit"] [holds "reasonable_limit", holds "reasonable_grounds"]).map (·.1) == some 1
#guard (refusal env [] [.and (holds "rule_ok") (holds "reasonable_limit")]).map (·.2.startsWith "'Fair") == some true
-- Another sense, no evaluative word, a template's word, a sense projection, a W3-defined name.
#guard firstNamed [] [holds "due_date", holds "arrest"] == none
#guard firstNamed [] [holds "rule_ok"] == some (0, "'Fair")
#guard firstNamed [] [holds "sense__just_1"] == some (0, "'Just")
#guard firstNamed ["sense__just_1"] [holds "sense__just_1"] == none
#guard firstNamed [] [holds "defined_fair"] == none
#guard firstNamed [] [holds "fair_defined"] == none
#guard firstNamed [] [holds "good_judgment"] == some (0, "'Good judgment")
-- The first such sentence, its first such predicate, and the first argument's sort for the noun.
#guard firstNamed [] [holds "reasonable_limit", holds "rule_ok"] == some (0, "'Reasonable")
#guard firstNamed [] [.and (holds "arrest") (holds "reasonable_limit")] == some (0, "'Reasonable")
#guard (refusal env [] [holds "arbitrary"]).map (·.2) == some (text ["arbitrary"] ["arbitrary"] (some "limit"))
#guard (refusal env [] [holds "just"]).map (·.2) == some (text ["just"] ["just"] (some "act"))

end VE.EnglishGrammar.JudgmentLinesExamples
