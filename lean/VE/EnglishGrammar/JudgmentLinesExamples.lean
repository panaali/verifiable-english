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

-- The status line says "uses": neutral, in the order given, and no line without a judgment.
#guard statusLine [arbitrary] == some "Open: this uses the judgment whether an act is classified as \"arbitrary\"."
#guard statusLine [arbitrary, unfair] == some ("Open: this uses the judgments whether an act is classified as " ++
  "\"arbitrary\" and whether a person has the recorded relation \"treats_unfairly\" to a person (the same or another).")
#guard statusLine [arbitrary, governed, weighs] == some ("Open: this uses the judgments whether an act is classified " ++
  "as \"arbitrary\", whether an act is classified as \"arbitrary\" and whether a person has recorded relation weighs " ++
  "with argument two an act and argument three an act (the same or another).")
#guard statusLine [] == none
#guard statusLine [arbitrary, noWording] == none

-- The mode: a W2 record and its predicate, W2's check and the admission's decider check, the line's limit.
def lineRequest (line : String) (jurisdiction : String := "udhr") : Json :=
  Json.mkObj [("id", .str "d"), ("line", .str line), ("jurisdiction", .str jurisdiction)]
def errorOf (j : Json) : String := ((j.getObjValD "error").getStr?).toOption.getD ""

#guard (runCaseReported (lineRequest governedLine)).getObjValD "record" == recordJson governed "udhr"
#guard (runCaseReported (lineRequest unfairLine)).getObjValD "predicate" ==
  Json.mkObj [("name", .str "treats_unfairly"), ("arguments", toJson ["person", "person"])]
#guard errorOf (runCaseReported (lineRequest "No line.")) == lineFault
#guard errorOf (runCaseReported (lineRequest (governedLine.replace "governance function" "unresolved decider"))) ==
  "JudgmentDecider: arbitrary"
#guard errorOf (runCaseReported (lineRequest governedLine "two words")) == "open term needs a decision role and jurisdiction"
#guard errorOf (runCaseReported (Json.mkObj [("id", .str "d"), ("line", .str governedLine)])) != ""
def longLine (k : Nat) : String := governedLine.replace "governance function" (String.mk (List.replicate k 'x'))
def spare : Nat := maxLineChars - (governedLine.length - "governance function".length)
-- At the limit the line is read, and W2's check (a token's length) answers; one character more is the limit's.
#guard (longLine spare).length == maxLineChars && (parseLine (longLine spare)).isSome &&
  errorOf (runCaseReported (lineRequest (longLine spare))) == "open term needs a decision role and jurisdiction"
#guard errorOf (runCaseReported (lineRequest (longLine (spare + 1)))) ==
  s!"ResourceLimit: a declaration line has at most {maxLineChars} characters"

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
      pred "sense__just_1", pred "defined_fair"],
    source := Json.mkObj [("definitions", Json.arr #[Json.mkObj [("name", .str "defined_fair")]])] }
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

end VE.EnglishGrammar.JudgmentLinesExamples
