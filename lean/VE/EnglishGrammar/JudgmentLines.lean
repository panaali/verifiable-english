import VE.EnglishGrammar.Actions
import VE.EnglishGrammar.Evaluative
import VE.Judgments.Decl
import VE.Words.Situation

/-! The English rows of judgment terms (`judgments@0`, docs/spec/judgment-terms.md 9.1, 9.2 and 9.5; plan 2.4, JT-3): the
declaration line, parsed in authoring to a W2 record and its predicate; the legend and the neutral status line; and
the authoring refusal. JT-E1r and JT-E1s failed, so the lines are in today's identifier wording: the predicate's
fallback wording filled with its sorts (DRI 2026-10-31, jt-e1s item 1). They read no template and declare none. They
state what the document declares; whether a reader understands which answers turn on which judgment stays open. The
legend and status lines reach the document report in jt-3b (DRI 2026-11-02, jt-3 item 2). -/

namespace VE.EnglishGrammar.JudgmentLines
open Lean VE.Judgments

def articled (noun : String) : String := VE.Words.article noun ++ " " ++ noun

/-- What fills each slot: the sort with its article; a sort already written is marked, so that the line does not say
the two differ (spec 9). -/
def slotNouns (args : List String) : List String :=
  args.mapIdx fun i s => articled s ++ (if (args.take i).contains s then " (the same or another)" else "")

/-- The predicate's identifier wording with its slots filled; none for an arity with no such wording. -/
def atom (name : String) (args : List String) : Option String :=
  (match fallbackWording name args.length with
    | some t => some t
    | none => if 3 ≤ args.length then mechanicalWording name args.length else none).map fun t =>
    (slotNouns args).zipIdx.foldl (fun out (p : String × Nat) => out.replace s!"\{{p.2}}" p.1) t

def noDeciderTail : String := "; the text does not say who makes it."

/-- The declaration (9.1, 2.4), in the legend and in authoring. It names the decider, or says the text names none. -/
def declarationLine (j : Judgment) : Option String :=
  (atom j.name j.arguments).map fun a =>
    "Whether " ++ a ++ " is a judgment" ++
      (if j.decidedBy == "unstated" then noDeciderTail else " for the " ++ j.decidedBy.replace "_" " " ++ ".")

/-- The record's factors (2.4), shown and never premises; none when it has none. -/
def factorsLine (j : Judgment) : Option String :=
  if j.factors.isEmpty then none else some ("The text mentions these points: " ++ "; ".intercalate j.factors ++ ".")

/-- A bound term's legend (2.4): its declaration, then its factors when it has any. -/
def legendLines (j : Judgment) : List String := (declarationLine j).toList ++ (factorsLine j).toList

/-- A unit's status line (9.2): neutral, since a criterion unit uses a judgment to limit it and does not depend on it.
None for a unit that uses no judgment or a judgment with no wording. -/
def statusLine (js : List Judgment) : Option String := do
  let atoms ← js.mapM (fun j => atom j.name j.arguments)
  let whethers := atoms.map ("whether " ++ ·)
  match whethers.reverse with
  | [] => none
  | [w] => some s!"Open: this uses the judgment {w}."
  | w :: rest => some s!"Open: this uses the judgments {", ".intercalate rest.reverse} and {w}."

def lineFault : String :=
  "JudgmentLine: a declaration reads 'Whether <the predicate's wording> is a judgment for the <decider>.' or 'Whether " ++
    "<the predicate's wording> is a judgment; the text does not say who makes it.'"

/-- The words after each article of an atom (the sorts), and the predicate's name: the quoted word, or the one after
"relation". `parseLine` accepts them only if they render back to the line. -/
def atomParts (a : String) : String × List String :=
  let ws := a.splitOn " "
  let after (keys : List String) : List String :=
    ((ws.zip (ws.drop 1)).filter (keys.contains ·.1)).map (·.2)
  (((after ["as", "relation"]).head?.getD "").replace "\"" "", after ["a", "an"])

/-- `j`, if `line` is the line `j` renders to. An empty word of the decider ("for the .", two spaces) is no spelling of
a token. -/
def renderingTo (line : String) (j : Judgment) : Option Judgment :=
  if (j.decidedBy.splitOn "_").any (·.isEmpty) then none
  else if declarationLine j == some line then some j else none

/-- The one reading of a declaration line: the judgment whose line it is, or none. Accepting only what renders back
to the same bytes is what makes it one reading, with no second spelling (`parseLine_renders`). -/
def parseLine (line : String) : Option Judgment :=
  match line.splitOn " is a judgment" with
  | [head, tail] =>
    let decider := if tail == noDeciderTail then "unstated" else
      (((tail.dropPrefix? " for the ").map (·.toString)).getD "").dropRight 1 |>.replace " " "_"
    let parts := atomParts (head.drop 8)
    renderingTo line ⟨parts.1, parts.2, decider, []⟩
  | _ => none

theorem renderingTo_renders {line : String} {j k : Judgment} (h : renderingTo line k = some j) :
    declarationLine j = some line := by
  unfold renderingTo at h
  split at h
  · cases h
  · split at h
    · rename_i hr
      cases h
      simpa using hr
    · cases h

theorem parseLine_renders {line : String} {j : Judgment} (h : parseLine line = some j) :
    declarationLine j = some line := by
  unfold parseLine at h
  split at h
  · exact renderingTo_renders h
  · cases h

/-- The W2 record of a parsed line (spec 1): its name, sorts and decider, with the document's jurisdiction. -/
def recordJson (j : Judgment) (jurisdiction : String) : Json :=
  Json.mkObj [("name", .str j.name), ("arguments", toJson j.arguments), ("decided_by", .str j.decidedBy),
    ("necessary", toJson ([] : List String)), ("sufficient", toJson ([] : List String)),
    ("factors", toJson ([] : List String)), ("precedents", toJson ([] : List String)),
    ("jurisdiction", .str jurisdiction), ("version", toJson (1 : Nat))]

/-- No vocabulary: a declaration line brings its own predicate, and W2's check reads a vocabulary only for criteria. -/
def noVocabulary : VE.Route.Wire.RouteVocabulary :=
  { vocabulary := ⟨[], [], []⟩, sourceVocabulary := ⟨[], [], []⟩, validNames := rfl, literals := [], nodup := .nil,
    definitions := [], chain := trivial }

/-- A declaration line, read in authoring to its W2 record and its predicate. The record passes W2's own check and
`judgments@0`'s admission over the line's predicate, so a refused decider is refused by their owner. -/
def readDeclaration (line jurisdiction : String) : Except String (Json × String × List String) := do
  let some j := parseLine line | throw lineFault
  let record := recordJson j jurisdiction
  let rs ← records noVocabulary (.arr #[record]) false (some fun _ => pure ())
  let _ ← admit (VE.Bridge.Vocabulary.environment ⟨[], [(j.name, j.arguments)], []⟩) [] [] rs
  pure (record, j.name, j.arguments)

/-! ### The authoring refusal (9.5) -/

/-- The most bound names one request may send. -/
def maxJudgments : Nat := 4096

/-- The predicates of a reading, in its order. -/
def preds : EFormula → List String
  | .top | .bottom | .eq _ _ | .lt _ _ | .le _ _ => []
  | .pred p _ | .reachNamed _ p _ _ => [p]
  | .not a | .all _ a | .ex _ a | .reachBody _ _ a _ _ => preds a
  | .and a b | .or a b | .implies a b => preds a ++ preds b

/-- The word after a row's word or phrase in `ws`, when it is a word. -/
def wordAfter (word ws : List String) : Option String :=
  (List.range ws.length).findSome? fun i =>
    if (ws.drop i).take word.length == word then
      ((ws.drop (i + word.length)).head?).filter fun w => !w.isEmpty && w.all Char.isAlpha
    else none

/-- 9.5's refusal, for a predicate with words `ws` matching `row`; `sort` is its first argument's (DRI 2026-11-02, jt-3
item 4). An adjective row with a singular noun in the reading (the word after it, else the sort) uses 9.5's own
definition; every other row quotes the word or phrase as written. Not measured by JT-E1. -/
def refusalText (row : EvaluativeRow) (ws : List String) (sort : Option String) : String :=
  let w := " ".intercalate row.word
  let next := wordAfter row.word ws
  let written := if row.word == ["overly"] then " ".intercalate (w :: next.toList) else w
  let noun := (next <|> sort).filter fun n => !n.isEmpty && !n.endsWith "s"
  let defined := match noun with
    | some n => if row.word.length == 1 && !w.endsWith "ly" then articled (w ++ " " ++ n.replace "_" " ") else ""
    | none => ""
  let defined := if defined.isEmpty then "\"" ++ written ++ "\"" else defined
  s!"'{written.capitalize}' is a judgment. Say who decides it ('… is a judgment for the operator'), or define it " ++
    s!"('In this document, {defined} means …')."

/-- Whether the environment defines `p` by W3 (its entry's `defined`), which spec 7 leaves out: a defined word is not
undeclared, as 9.5's own rewrite asks. -/
def isDefined (E : Env) (p : String) : Bool :=
  ((((E.source.getObjValD "vocabulary").getObjValD "predicates").getObjValD p).getObjVal? "defined").toOption.isSome

/-- A reading's base predicates (spec 7's `preds`), each with its words. -/
def readingPreds (E : Env) (f : EFormula) : List (String × List String) :=
  ((preds f).filter (!isDefined E ·)).map fun p => (p, predicateWords p ((E.predicate? p).bind (·.wording)))

/-- The first sentence whose reading has a predicate `undeclaredEvaluative` lists, with 9.5's text for the first such
predicate. It binds per predicate, as spec 7 and 8.4 do: a bound name binds itself and no other predicate that shares
its word. -/
def refusal (E : Env) (J : List String) (fs : List EFormula) : Option (Nat × String) :=
  fs.zipIdx.findSome? fun (f, i) =>
    let ps := readingPreds E f
    (undeclaredEvaluative evaluativeRows ps J).head?.bind fun p => do
      let ws ← ps.lookup p
      let row ← evaluativeRows.find? (·.matches ws)
      pure (i, refusalText row ws ((E.predicate? p).bind (·.args.head?)))

end VE.EnglishGrammar.JudgmentLines
