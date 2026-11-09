import VE.EnglishGrammar.Norm.Run
import VE.EnglishGrammar.Norm.OwnersExamples

/-! EN-2's answers, fixtures E1-E14 and E16 (docs/spec/en-e3-norm.md section 8; E15 is EN-3's): `answerWith` on given
reader outcomes. The source is "Rule 1. X." unless a row names another; it feeds only the rule rows' spans and
`source_sha256`. Every coded row carries its class from `Run.codeClasses` (M8). -/

namespace VE.EnglishGrammar.Norm.RunExamples
open Lean VE.EnglishGrammar VE.EnglishGrammar.Norm VE.EnglishGrammar.Norm.OwnersExamples
open VE.EnglishGrammar.LexiconFixtures

def caseOf : VE.EnglishGrammar.Run.Case :=
  { E := envF, O := {}, L := LF, overlayFailure := none, identities := [("environment_id", .str "env")] }
def fixed (o : NormOutcome) : Run.Reader := ⟨fun _ _ _ _ _ => o, fun _ _ => #["r0", "r1"]⟩
def result (o : NormOutcome) (s : String := "Rule 1. X.") : Json :=
  Run.resultOf (Run.answerWith (fixed o) "c1" caseOf s)
/-- The members `ks` of the answer to `o`, in order (`null` for an absent one). -/
def get (o : NormOutcome) (ks : List String) (s : String := "Rule 1. X.") : List Json :=
  ks.map (result o s).getObjValD
def str (xs : List String) : List Json := xs.map .str

-- E1: two blocks and a precedence line; one row per statement, each rule row with its block's byte span.
def sE1 : String := "Rule 1. X.\nRule 2. Y.\nRule 2 takes precedence over rule 1."
def oE1 : NormOutcome := .ok [.rule ⟨1, []⟩ cPub, .rule ⟨2, []⟩ cPub, .precedence 2 1]
#guard Run.statementSpans sE1 == [(0, 10), (11, 21), (22, 58)]
#guard (result oE1 sE1).compress == "{\"identities\":{\"environment_id\":\"env\",\"source_sha256\":" ++
  "\"1713bb5f6762c08b78b239653372972ac0965e6a9b05a1bd1a7e087c255308d1\"},\"statements\":[{\"exception_to\":[]," ++
  "\"kind\":\"rule\",\"node\":{\"norm\":{\"guard\":[\"unary\",\"publicly_deployed\",[\"var\",0]],\"name\":\"rule-1\"," ++
  "\"over\":[],\"predicate\":\"in_scope\",\"sign\":true,\"unless\":[]}},\"number\":1,\"span\":[0,10]}," ++
  "{\"exception_to\":[],\"kind\":\"rule\",\"node\":{\"norm\":{\"guard\":[\"unary\",\"publicly_deployed\",[\"var\",0]]," ++
  "\"name\":\"rule-2\",\"over\":[\"rule-1\"],\"predicate\":\"in_scope\",\"sign\":true,\"unless\":[]}},\"number\":2," ++
  "\"span\":[11,21]},{\"kind\":\"precedence\",\"over\":1,\"rule\":2}],\"status\":\"one\"}"
-- E2: a clause with a span is `partial`, with its span row and no statements.
#guard get (.ok [.rule ⟨1, []⟩ cSpan]) ["status", "code", "class", "statements"] ==
  str ["partial", "UnformalisedSpan", "VEError"] ++ [.null]
#guard (result (.ok [.rule ⟨1, []⟩ cSpan])).getObjValD "spans" == Json.arr #[Json.mkObj [("start", 30), ("stop", 46),
  ("row", "every|norm.modifier|norms@0"), ("owner", "ET-T1"), ("place", "act")]]
-- E3: the decoder's refusals; each resource limit is `NodeLimit`, any other refusal `NodeRefused`.
#guard get (.ok [.rule ⟨1, []⟩ cBad]) ["status", "code", "class", "text"] ==
  str ["rejected", "NodeLimit", "ResourceLimit", "ResourceLimit: formula depth exceeds 64"]
#guard get (.ok [.rule ⟨1, []⟩ cWide]) ["status", "code", "class", "text"] ==
  str ["rejected", "NodeLimit", "ResourceLimit", "ResourceLimit: AST exceeds depth or node budget"]
#guard get (.ok [.rule ⟨1, []⟩ cAtom]) ["status", "code", "class", "text", "sentence"] ==
  str ["rejected", "NodeRefused", "VEError", "invalid indexed formula"] ++ [.null]
-- E4, E5, E9: a block fault names its sentence, except `UnknownRule`.
#guard get (.misplaced (.expectedRule 0 1)) ["status", "code", "class", "sentence", "text"] ==
  str ["rejected", "ExpectedRule", "SyntaxError"] ++ [toJson 0] ++
    str ["Sentence 1 starts a block that is not numbered 1. Start it with \"Rule 1.\""]
#guard get (.misplaced (.unknownRule 3)) ["status", "code", "class", "sentence", "text"] ==
  str ["rejected", "UnknownRule", "VEError"] ++ [.null] ++ str ["The text names rule 3, and it has no rule 3."]
#guard get (.misplaced (.strayConsequence 2)) ["status", "code", "sentence", "text"] ==
  str ["rejected", "StrayConsequence"] ++ [toJson 2] ++
    str ["Sentence 3 is a rule sentence outside a block, or a second one in its block."]
#guard get (.misplaced (.noConsequence 1)) ["code", "sentence"] == str ["NoConsequence"] ++ [toJson 1] &&
  get (.misplaced (.strayCarveOut 1)) ["code", "sentence"] == str ["StrayCarveOut"] ++ [toJson 1]
-- E6, E7: no derivation, the budget (UNKNOWN), and a lexical refusal.
#guard get (.stopped 1 .noDerivation) ["status", "code", "class", "sentence"] ==
  str ["none", "NoDerivation", "SyntaxError"] ++ [toJson 1]
#guard get (.stopped 1 .budget) ["status", "code", "class", "sentence"] ==
  str ["budget", "Budget", "ResourceLimit"] ++ [toJson 1]
#guard get (.lexical .emptyDocument) ["status", "code", "class", "text", "sentence"] ==
  str ["rejected", "EmptyDocument", "SyntaxError", "Write at least one statement ending with a period."] ++ [.null]
-- E10: `many` names its sentence and shows both trees, with the reader's rule tags.
def tA : VE.Grammar.Tree Tok := .node 0 [.leaf (.word "X" true)]
def tB : VE.Grammar.Tree Tok := .node 1 [.leaf (.word "X" true)]
#guard get (.stopped 1 (.ambiguous tA tB)) ["status", "code", "class", "sentence", "witnesses"] ==
  str ["many", "Ambiguous", "AmbiguousDerivation"] ++ [toJson 1,
    Json.arr #[Json.arr #[Json.arr #[.str "r0", toJson 0, toJson 1]], Json.arr #[Json.arr #[.str "r1", toJson 0, toJson 1]]]]
-- E11, E12: a translation-mode statement, and statements that are not the text's blocks, are `Internal`.
def internalRow : List Json :=
  str ["rejected", "Internal", "CheckerUnavailable", Run.rowsInternalText] ++ [.null]
#guard get (.ok [.source []]) ["status", "code", "class", "text", "sentence"] == internalRow
#guard get (.ok [.rule ⟨1, []⟩ cPub]) ["status", "code", "class", "text", "sentence"] "Rule 1. X.\nRule 2. Y." == internalRow
-- E13: a block over two lines is one span, from the lexer's positions: header to period.
#guard Run.statementSpans "Rule 1.\nX." == [(0, 10)] &&
  get (.ok [.rule ⟨1, []⟩ cPub]) ["status"] "Rule 1.\nX." == str ["one"] &&
  (result (.ok [.rule ⟨1, []⟩ cPub]) "Rule 1.\nX.").getObjValD "statements" == Json.arr #[Json.mkObj [
    ("kind", "rule"), ("number", 1), ("exception_to", Json.arr #[]), ("span", Json.arr #[0, 10]),
    ("node", cPub.wire "rule-1" [])]]
-- E14: the rows a Python-admitted text makes `lean-unknown` (the budget, or a code of class ResourceLimit), and those
-- it does not; the comparator is Python's (en-e3b's `tests/test_english_statement_shadow.py`).
def leanUnknown (row : Json) : Bool :=
  row.getObjValD "status" == .str "budget" || row.getObjValD "class" == .str "ResourceLimit"
#guard [result (.stopped 1 .budget), result (.ok [.rule ⟨1, []⟩ cBad]), result (.ok [.rule ⟨1, []⟩ cWide])].all leanUnknown
#guard ![result (.ok [.rule ⟨1, []⟩ cAtom]), result (.misplaced (.strayConsequence 2)), result oE1 sE1,
  result (.stopped 1 .noDerivation)].any leanUnknown
-- E16: a stop names its sentence exactly when `stopNamesSentence` holds (M11).
#guard get (.stopped 1 (.rejected .internal)) ["status", "code", "class", "text", "sentence"] ==
  str ["rejected", "Internal", "CheckerUnavailable", "The reader found no meaning for a derivation."] ++ [.null]
#guard get (.stopped 1 (.ok (.precedence 1 1) false)) ["status", "code", "class", "text", "sentence"] ==
  str ["rejected", "Internal", "CheckerUnavailable", "The reader found no meaning for a derivation."] ++ [.null]
#guard get (.stopped 1 (.rejected .emptyDocument)) ["code", "sentence"] == str ["EmptyDocument"] ++ [.null]
#guard get (.stopped 1 (.rejected .nestingLimit)) ["status", "code", "class", "text", "sentence"] ==
  str ["rejected", "NestingLimit", "ResourceLimit", "Sentence 2 is nested more than 64 levels deep."] ++ [toJson 1]
-- every `Reject`, in constructor order: its stop names the sentence exactly when its code is not unsentenced
def rejectAll : List Reject :=
  [.sourceTooLong, .textTooLong, .badCharacter 0, .openQuote 0, .badNumeral 0, .emptyDocument, .emptySentence 0,
   .unterminated, .badSpacing 0, .unboundReference, .shadowedName, .sortMismatch, .markerDepth, .nestingLimit,
   .numeralBound, .coefficientNotNumeral, .pronounUnresolved, .blockedWording "natural-negation",
   .coordinationRepeated, .coordinationForm, .naturalScoped, .relativeForm, .internal]
#guard rejectAll.map Reject.code == VE.EnglishGrammar.Run.rejectCodes
#guard rejectAll.all fun r =>
  ((result (.stopped 1 (.rejected r))).getObjValD "sentence" == .null) ==
    VE.EnglishGrammar.Run.statementUnsentenced.contains r.code
#guard !Run.stopNamesSentence (.ok (.precedence 1 1) false) && !Run.stopNamesSentence (.rejected .internal) &&
  Run.stopNamesSentence (.rejected .nestingLimit) && Run.stopNamesSentence .noDerivation &&
  Run.stopNamesSentence (.ambiguous tA tB) && Run.stopNamesSentence .budget
-- E8: never `one` (the other direction of `answer_one_iff`); an overlay failure is `invalidGrammar`.
def notOne : List NormOutcome :=
  [.stopped 1 .noDerivation, .stopped 1 .budget, .misplaced (.unknownRule 3), .lexical .emptyDocument,
   .ok [.rule ⟨1, []⟩ cSpan], .ok [.rule ⟨1, []⟩ cBad], .ok [.rule ⟨1, []⟩ cWide], .ok [.rule ⟨1, []⟩ cAtom],
   .misplaced (.strayConsequence 2), .stopped 1 (.ambiguous tA tB), .ok [.source []], .stopped 1 (.rejected .internal),
   .stopped 1 (.ok (.precedence 1 1) false), .stopped 1 (.rejected .emptyDocument), .stopped 1 (.rejected .nestingLimit)]
#guard notOne.all fun o => (result o).getObjValD "status" != .str "one"
#guard (Run.resultOf (Run.answerWith (fixed oE1) "c1"
  { caseOf with overlayFailure := some ("O1", "constant", "alice") } sE1)).getObjValD "status" == .str "invalidGrammar"
-- every `rejected` answer above names a sentence exactly when its code is not unsentenced
#guard (notOne ++ [NormOutcome.misplaced (.expectedRule 0 1)]).all fun (o : NormOutcome) =>
  match (result o).getObjValD "status", (result o).getObjValD "code" with
  | .str "rejected", .str k =>
    ((result o).getObjValD "sentence" == Json.null) == VE.EnglishGrammar.Run.statementUnsentenced.contains k
  | .str "rejected", _ => false
  | _, _ => true

end VE.EnglishGrammar.Norm.RunExamples
