import VE.EnglishGrammar.Norm.Run
import VE.EnglishGrammar.Norm.OwnersExamples
import VE.EnglishGrammar.Norm.Examples
import VE.EnglishGrammar.JudgmentRunExamples

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
-- E2: a clause with a span is `unformalised` (DRI 2026-11-09 item 2), with its span row and no statements.
#guard get (.ok [.rule ⟨1, []⟩ cSpan]) ["status", "code", "class", "statements"] ==
  str ["unformalised", "UnformalisedSpan", "VEError"] ++ [.null]
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
#guard get (.misplaced (.strayConsequence 2)) ["status", "code", "class", "sentence", "text"] ==
  str ["rejected", "StrayConsequence", "SyntaxError"] ++ [toJson 2] ++
    str ["Sentence 3 is a rule sentence outside a block, or a second one in its block."]
#guard get (.misplaced (.noConsequence 1)) ["code", "class", "sentence"] == str ["NoConsequence", "SyntaxError"] ++
    [toJson 1] &&
  get (.misplaced (.strayCarveOut 1)) ["code", "class", "sentence"] == str ["StrayCarveOut", "SyntaxError"] ++ [toJson 1]
-- E6, E7: no derivation, the budget (UNKNOWN), and a lexical refusal.
#guard get (.stopped 1 .noDerivation) ["status", "code", "class", "sentence"] ==
  str ["none", "NoDerivation", "SyntaxError"] ++ [toJson 1]
#guard get (.stopped 1 .budget) ["status", "code", "class", "sentence"] ==
  str ["budget", "Budget", "ResourceLimit"] ++ [toJson 1]
#guard get (.lexical .emptyDocument) ["status", "code", "class", "text", "sentence"] ==
  str ["rejected", "EmptyDocument", "SyntaxError", "Write at least one statement ending with a period."] ++ [.null]
-- an invalid grammar and a lexical refusal that names its character (its span, in code points)
#guard get (.invalidGrammar .notWellFormed) ["status", "code", "class", "fault", "sentence"] ==
  str ["invalidGrammar", "InvalidGrammar", "CheckerUnavailable", "notWellFormed"] ++ [.null]
#guard get (.lexical (.badCharacter 3)) ["status", "code", "class", "span", "sentence"] ==
  str ["rejected", "BadCharacter", "SyntaxError"] ++ [Json.arr #[3, 4], .null]
-- a lexical outcome's text is `rejectText 0` (the lexer's own refusals name no sentence; spec 2.3)
#guard get (.lexical .nestingLimit) ["text"] == str ["Sentence 1 is nested more than 64 levels deep."]
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
-- only a translation-mode statement is refused: no statements over no blocks are rows, none of them one
#guard Run.oneSpans "" [] == some [] && Run.oneSpans "" [.source []] == none &&
  Run.oneSpans "Rule 1. X.\nRule 2. Y." [.rule ⟨1, []⟩ cPub, .source []] == none
-- fewer blocks than statements is `Internal` too (E12 has more): `zip` must never drop a statement
#guard get (.ok [.rule ⟨1, []⟩ cPub, .rule ⟨2, []⟩ cPub]) ["status", "code", "class", "text", "sentence"] == internalRow
-- M10's spans are bytes, not code points: "ë" is two bytes, so the second block starts at byte 14 (character 13)
#guard Run.statementSpans "Rule 1. Zoë.\nRule 2. Y." == [(0, 13), (14, 24)] &&
  match (result (.ok [.rule ⟨1, []⟩ cPub, .rule ⟨2, []⟩ cPub]) "Rule 1. Zoë.\nRule 2. Y.").getObjValD "statements" with
  | .arr rows => rows.toList.map (·.getObjValD "span") == [Json.arr #[0, 13], Json.arr #[14, 24]]
  | _ => false
-- E13: a block over two lines is one span, from the lexer's positions: header to period.
-- a sentence that opens with no word (a quotation, a numeral) continues its block; only "Rule" opens one
#guard Run.statementSpans "Rule 1. X.\n\"Rule\" 2 is quoted." == [(0, 30)] &&
  Run.statementSpans "Rule 1. X.\n2 rules hold." == [(0, 24)]
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
-- every coded answer above carries its code's class from the one code table (M8)
#guard (notOne ++ [NormOutcome.misplaced (.expectedRule 0 1), .misplaced (.noConsequence 1), .misplaced (.strayCarveOut 1),
    .invalidGrammar .notWellFormed]).all fun (o : NormOutcome) =>
  match (result o).getObjValD "code" with
  | .str k => (result o).getObjValD "class" == ((VE.EnglishGrammar.Run.codeClasses.lookup k).map Json.str).getD .null &&
    (VE.EnglishGrammar.Run.codeClasses.lookup k).isSome
  | _ => false
-- the identities: the source's SHA-256 beside the case's (spec 8: b9f1e10d…94e1, E12 9d4519a2…94ba, E13 8512791f…0be7)
def sha (o : NormOutcome) (s : String := "Rule 1. X.") : String :=
  match ((result o s).getObjValD "identities").getObjValD "source_sha256" with | .str h => h | _ => ""
#guard ((result (.stopped 1 .budget)).getObjValD "identities").getObjValD "environment_id" == .str "env" &&
  sha (.stopped 1 .budget) == "b9f1e10dd9b146f928cd661dd716561decb1c7b41a7cf58e9680e90ff3ce94e1" &&
  (sha (.ok [.rule ⟨1, []⟩ cPub]) "Rule 1. X.\nRule 2. Y.").startsWith "9d4519a2" &&
  (sha (.ok [.rule ⟨1, []⟩ cPub]) "Rule 1. X.\nRule 2. Y.").endsWith "94ba" &&
  sha (.ok [.rule ⟨1, []⟩ cPub]) "Rule 1.\nX." == "8512791f5f0c966294769fe99141449daf9ef986cdaa0ac63f70ad95a2da0be7"
-- every `rejected` answer above names a sentence exactly when its code is not unsentenced
#guard (notOne ++ [NormOutcome.misplaced (.expectedRule 0 1)]).all fun (o : NormOutcome) =>
  match (result o).getObjValD "status", (result o).getObjValD "code" with
  | .str "rejected", .str k =>
    ((result o).getObjValD "sentence" == Json.null) == VE.EnglishGrammar.Run.statementUnsentenced.contains k
  | .str "rejected", _ => false
  | _, _ => true

-- E17 (the runner's limit, DRI rule 2026-10-27): the real reader on a large well-formed request ends within the lexer's
-- text limit (`maxTextChars`, 10,000 characters): 300 blocks read as `one` with one row per block; 330 are refused.
def big (n : Nat) : String := "\n".intercalate ((List.range n).map fun i => s!"Rule {i + 1}. Every act may be done.")
def caseTwo : VE.EnglishGrammar.Run.Case :=
  { E := Norm.Examples.two, O := {}, L := Norm.Examples.L2, overlayFailure := none, identities := [] }
#guard collapsedLength (big 300) ≤ maxTextChars && collapsedLength (big 330) > maxTextChars
#guard match (Run.resultOf (Run.answer "c" caseTwo (big 300))).getObjValD "statements" with
  | .arr rows => rows.size == 300 && rows[299]?.map (·.getObjValD "span") == some (Json.arr #[9759, 9791])
  | _ => false
#guard (Run.resultOf (Run.answer "c" caseTwo (big 330))).getObjValD "code" == .str "TextTooLong"

-- E15's kind-`blocks` rows (the EN-2 request): another kind and an extra member are refused before the case is
-- decoded; a well-formed request reaches `decodeCase`.
def request (kind : String) (extra : List (String × Json) := []) : Json :=
  Json.mkObj ([("id", Json.str "c"), ("environment", Json.mkObj []), ("lexicon", Json.mkObj []),
    ("kind", Json.str kind), ("source", Json.str "Rule 1. X.")] ++ extra)
def errorOf (j : Json) : Json := (Run.statementCaseReported j).getObjValD "error"
#guard errorOf (request "lines") == .str "InvalidInput: english.statement reads kind blocks or render"
#guard errorOf (request "blocks" [("mode", "authoring")]) == .str ("fields do not match: expected [id, environment, " ++
  "lexicon, kind, source], got [environment, id, kind, lexicon, mode, source]")
#guard errorOf (request "blocks") ==
  .str "fields do not match: expected [language, profiles, spec_revision, vocabulary], got []" &&
  (Run.statementCaseReported (request "blocks")).getObjValD "status" == .str "error"

-- A full case through the whole mode (`JudgmentRunExamples`' environment and lexicon): the optional `overlay` member is
-- read (its digest joins the identities); `english.grammar` exports english.statement's three tables (M9).
open VE.EnglishGrammar.JudgmentRunExamples (environment lexicon) in
def wholeRow (extra : List (String × Json) := []) : Json :=
  Run.statementCaseReported (Json.mkObj ([("id", Json.str "s"), ("environment", environment),
    ("lexicon", lexicon), ("kind", Json.str "blocks"), ("source", Json.str "Atlas is published.")] ++ extra))
def whole (extra : List (String × Json) := []) : Json := Run.resultOf (wholeRow extra)
#guard ["status", "code", "sentence"].map (whole).getObjValD == str ["none", "NoDerivation"] ++ [toJson 0] &&
  ((whole).getObjValD "identities").getObjValD "overlay_digest" == .null
#guard ["status", "code"].map (whole [("overlay", Json.mkObj [])]).getObjValD == str ["none", "NoDerivation"] &&
  (((whole [("overlay", Json.mkObj [])]).getObjValD "identities").getObjValD "overlay_digest").getStr?.isOk
-- the opposite direction: `id`, `kind` or `source` retyped is an error row, never an answer
#guard (wholeRow).getObjValD "status" == .str "ok" && ["id", "kind", "source"].all fun k =>
  [Json.num 7, .null, .arr #[]].all fun v => (wholeRow [(k, v)]).getObjValD "status" == .str "error"
open VE.EnglishGrammar.JudgmentRunExamples (environment lexicon) in
def grammarExport : Json := ((VE.EnglishGrammar.Run.grammarCase (Json.mkObj [("id", Json.str "g"),
  ("environment", environment), ("lexicon", lexicon)])).toOption.getD .null).getObjValD "result"
#guard grammarExport.getObjValD "statement_statuses" == toJson VE.EnglishGrammar.Run.statementStatusCodes &&
  grammarExport.getObjValD "statement_fields" == toJson VE.EnglishGrammar.Run.statementFields &&
  grammarExport.getObjValD "statement_unsentenced" == toJson VE.EnglishGrammar.Run.statementUnsentenced &&
  grammarExport.getObjValD "codes" == toJson VE.EnglishGrammar.Run.codeClasses

-- f18 through the real reader (`leanReader`): an ambiguous condition stops the reading at its rule sentence, with both
-- trees under `normGrammar`'s rule tags (`normTags`).
def caseD : VE.EnglishGrammar.Run.Case :=
  { E := Norm.Examples.fd, O := {}, L := Norm.Examples.LD, overlayFailure := none, identities := [] }
def f18 : Json :=
  Run.resultOf (Run.answer "c" caseD "Rule 1. Every service may be used, if every deployed service is reviewed.")
#guard ["status", "code", "sentence"].map f18.getObjValD == str ["many", "Ambiguous"] ++ [toJson 1]
#guard f18.getObjValD "witnesses" == Json.arr #[
  Json.arr #[Json.arr #["norm.clause-if", 0, 12], Json.arr #["consequence.used", 0, 5], Json.arr #["formula.universal", 7, 12],
    Json.arr #["universal.relative", 7, 12], Json.arr #["declaration.noun", 8, 10], Json.arr #["noun.dservice", 8, 10],
    Json.arr #["relative.reviewed", 10, 12]],
  Json.arr #[Json.arr #["norm.clause-if", 0, 12], Json.arr #["consequence.used", 0, 5], Json.arr #["formula.natural", 7, 12],
    Json.arr #["natural.every", 7, 12], Json.arr #["natural-every.subject", 7, 12],
    Json.arr #["natural-subject.deployed", 8, 10], Json.arr #["natural-tail.relative", 10, 12],
    Json.arr #["relative.reviewed", 10, 12]]]

end VE.EnglishGrammar.Norm.RunExamples
