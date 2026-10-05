import VE.EnglishGrammar.Read
import VE.EnglishGrammar.Fixed.Version
import VE.Service.Standalone
import VE.Json

/-! The `ve_english_route` executable (docs/spec/english-lean-s2.md 2.10, 4.3 and 4.4; base spec 2.12 and
4.1 to 4.3), invoked as `lean/.lake/build/bin/ve_english_route MODE [cases.json|-]`, one row per case.

* `english.read`: a case `{"id", "environment", "overlay"?, "lexicon", "source", "mode", "cap"}`. The
  environment is the one Python validated; the overlay is the English vocabulary overlay, applied by
  `Env.decode`, so `read` gets the empty `Overlay` (record L11); the lexicon is the export of
  `ve.english_grammar` (`ve.english-lexicon@1`) and must name the environment. Mode `authoring` runs `read`
  at cap 2 and the budget `workBudget`; mode `translation` runs `translate` at the case's cap. The answer
  is the response of base 4.3 with the six identities of base 2.12, computed here from the case.
* `english.grammar`: a case `{"id", "environment", "overlay"?, "lexicon"}`; the answer is the export of
  spec 4.4: the identities but the source's, the nonterminal names, the ranks and every rule of
  `grammar E L` with its index, tag, sides and action text.

A case that cannot be read is an `error` row; every outcome of the reader, `invalidGrammar` included, is an
`ok` row whose `result` carries it. The canonical strict text of a reading is the adapter's: Python's
printer renders the formulas (one owner of the printer), so `one` carries no `canonical` field.

S3 (docs/spec/english-lean-s3.md 2.3, D18): an environment that names `alternatives@0` or `risk@0`, or carries
their blocks, is admitted at the boundary in three parts: its declarations are validated as submitted by the
routes' own source decoders (`Alternatives.Wire.decodeAltSource`, `Risk.Wire.decodeRiskSource`, with an empty
document); the family decoders validate its typing view (`typingView`); its identity is
`Standalone.environmentIdOf` over the submitted environment. `Route.Gate.decodeEnvelope` is not edited.
`riskView_eq` and `alternativesView_eq` prove that the typing view of `Encode.lean` is built by the service's
own reductions.
-/

namespace VE.EnglishGrammar.Run
open Lean VE.Grammar VE.EnglishGrammar

/-! ## Texts -/

/-- The fixed text of a rejection (base 4.2, spec 3.2); `i` is the sentence's index from zero, written from
one. -/
def rejectText (i : Nat) : Reject → String
  | .sourceTooLong => "The text is longer than 65,536 bytes."
  | .textTooLong => "The text is longer than 10,000 characters after spaces are collapsed."
  | .badCharacter o => s!"The character at position {o} cannot appear outside a quoted name."
  | .openQuote o => s!"The quoted name that starts at position {o} is not closed."
  | .badNumeral o => s!"The number at position {o} is not written in canonical form."
  | .emptyDocument => "Write at least one statement ending with a period."
  | .emptySentence k => s!"Sentence {k + 1} is empty."
  | .unterminated => "The text after the last period is not a sentence. End it with a period."
  | .badSpacing o => s!"The spacing at position {o} is not allowed: write no space before a period or at the " ++
    "start, one after a period, and one between words and quoted names."
  | .unboundReference => s!"Sentence {i + 1} uses a name before introducing it."
  | .shadowedName => s!"Sentence {i + 1} introduces a name that is already in use."
  | .sortMismatch => s!"Sentence {i + 1} relates two things of different kinds where the same kind is required."
  | .markerDepth => s!"Sentence {i + 1} uses a list marker that does not fit its depth."
  | .nestingLimit => s!"Sentence {i + 1} is nested more than 64 levels deep."
  | .numeralBound => s!"Sentence {i + 1} contains a number that is too long."
  | .coefficientNotNumeral => s!"Sentence {i + 1} multiplies by something that is not a number."
  | .pronounUnresolved =>
    s!"Sentence {i + 1} uses \"it\", and it is not settled what \"it\" refers to. Repeat the name."
  | .blockedWording "natural-negation" => "Use an explicit for every clause for negation."
  | .blockedWording w => s!"Sentence {i + 1} uses the blocked wording {w}."
  | .coordinationRepeated => s!"Sentence {i + 1} lists the same name or the same property twice in one list."
  | .coordinationForm => s!"Sentence {i + 1} lists three names or three properties where that form is not " ++
    "available. Use it only as a whole sentence, with each name written as it is declared."
  | .naturalScoped =>
    s!"Sentence {i + 1} uses a some, no or every clause inside another clause. Write it with for every or there is."
  | .relativeForm => s!"Sentence {i + 1} uses a wording as a relative clause where that form is not " ++
    "available. Write the clause in full, with for every or there is."
  | .internal => "The reader found no meaning for a derivation."

def illTypedText : String := "The text was read, and its formulas do not pass the type check."
def notOneSentenceText : String := "This text has more than one sentence. Translation mode reads exactly one."
def invalidGrammarText : String := "The vocabulary selection sent with this text was not accepted. No text was read."

/-! ## The request -/

def pairs (j : Json) (name : String) : Except String (List (String × String)) := do
  (← (← j.getObjVal? name).getArr?).toList.mapM fun
    | .arr #[.str a, .str b] => pure (a, b)
    | _ => throw s!"InvalidInput: lexicon {name}: every entry is a pair of strings"

def triples (j : Json) (name : String) : Except String (List (String × String × Bool)) := do
  (← (← j.getObjVal? name).getArr?).toList.mapM fun
    | .arr #[.str a, .str b, .bool c] => pure (a, b, c)
    | _ => throw s!"InvalidInput: lexicon {name}: every entry is two strings and a Boolean"

def lexiconFormat : String := "ve.english-lexicon@1"

/-- The lexicon of the export of `ve.english_grammar` (base 5.8), which must name the environment. -/
def decodeLexicon (environmentId : String) (j : Json) : Except String Lexicon := do
  VE.Bridge.exactFields j ["format", "environment_id", "nouns", "letters", "wordings", "negatives", "aliases",
    "spellings"]
  unless (← VE.Bridge.stringField j "format") == lexiconFormat do
    throw s!"InvalidInput: the lexicon format is not {lexiconFormat}"
  unless (← VE.Bridge.stringField j "environment_id") == environmentId do
    throw "InvalidInput: the lexicon names another environment"
  pure { nouns := ← pairs j "nouns", letters := ← pairs j "letters", wordings := ← pairs j "wordings",
         negatives := ← pairs j "negatives", aliases := ← triples j "aliases", spellings := ← pairs j "spellings" }

/-- The typing view of `Encode.lean` is the service's: `riskView` is `Standalone.riskReduced` and
`alternativesView` is `Standalone.alternativesReduced` (S3 spec 2.3, part 2). -/
theorem riskView_eq : riskView = VE.Service.Standalone.riskReduced := rfl

theorem alternativesView_eq : alternativesView = VE.Service.Standalone.alternativesReduced := rfl

/-- Whether an environment names a profile with a block, or carries a block (S3 spec 2.3). -/
def declaresBlock (environment : Json) : Bool :=
  let ps := (VE.Route.Gate.profilesOf environment).toOption.getD []
  ps.contains "alternatives@0" || ps.contains "risk@0" ||
    (environment.getObjVal? "alternatives").isOk || (environment.getObjVal? "risk").isOk

/-- Part 1 of the boundary (S3 spec 2.3): the profile list, the blocks and the W6 unit declarations validated
as submitted, by the source decoder of the risk route when `risk@0` is named or a `risk` block is present, and
by the alternatives route's otherwise, each with an empty document. -/
def validateDeclarations (environment : Json) : Except String Unit := do
  let ps := (VE.Route.Gate.profilesOf environment).toOption.getD []
  if ps.contains "risk@0" || (environment.getObjVal? "risk").isOk then
    let _ ← VE.Risk.Wire.decodeRiskSource environment (Json.mkObj [("norms", Json.arr #[])])
  else
    let _ ← VE.Alternatives.Wire.decodeAltSource environment (Json.arr #[]) (Json.arr #[])

/-- The environment identity, as the typing service computes it; for an environment with a profile block, after
the three parts of the boundary (S3 spec 2.3). -/
def environmentId (environment : Json) : Except String String := do
  if declaresBlock environment then
    validateDeclarations environment
    let _ ← VE.Service.Standalone.validated (← typingView environment)
    VE.Service.Standalone.environmentIdOf (← VE.Route.Gate.profilesOf environment) environment
  else
    let row ← VE.Service.Standalone.environmentCase (Json.mkObj [("id", .str "e"), ("environment", environment)])
    VE.Bridge.stringField row "environment_id"

/-- The tables of the profiles that have one, with the SHA-256 of each JSON source (spec 2.5, 2.10). -/
def tables : List (String × String) := [(baseProfile, relationalFolSha256)]

/-- The digest of the environment's profiles that have a table, in the environment's order (base 2.12). -/
def grammarId (profiles : List String) : Except String String :=
  VE.CertificateWire.digest "ve-english-grammar-v1\n"
    (Json.arr (profiles.filterMap fun p => (VE.Bridge.lookup tables p).map fun h =>
      Json.arr #[.str p, .str h]).toArray)

/-- A decoded case: the reader's inputs and the identities that do not depend on the source. -/
structure Case where
  E : Env
  L : Lexicon
  identities : List (String × Json)

def decodeCase (j : Json) : Except String Case := do
  let environment ← j.getObjVal? "environment"
  let overlay ← match j.getObjVal? "overlay" with
    | .ok (.obj o) => pure (Json.obj o)
    | .ok _ => throw "InvalidInput: the overlay is not an object"
    | .error _ => pure (Json.mkObj [])
  let envId ← environmentId environment
  let lexicon ← j.getObjVal? "lexicon"
  let L ← decodeLexicon envId lexicon
  let E ← Env.decode environment overlay
  let overlayDigest ← match j.getObjVal? "overlay" with
    | .ok o => pure [("overlay_digest", Json.str (← VE.CertificateWire.digest "ve-english-vocabulary-v1\n" o))]
    | .error _ => pure []
  pure { E, L, identities := [("environment_id", .str envId)] ++ overlayDigest ++
    [("lexicon_id", .str (← VE.CertificateWire.digest "ve-english-lexicon-v1\n" lexicon)),
     ("grammar_id", .str (← grammarId E.profiles)),
     ("actions_version", .str Fixed.actionsVersion)] }

/-! ## Trees -/

mutual
/-- A tree as rule tags along a pre-order walk, each with its token span `[start, end)` (spec 4.3). -/
def treeRows (tags : Array String) (start : Nat) : Tree Tok → List Json × Nat
  | .leaf _ => ([], start + 1)
  | .node r kids =>
    let (rows, stop) := kidsRows tags start kids
    (Json.arr #[.str (tags[r]?.getD ""), toJson start, toJson stop] :: rows, stop)

def kidsRows (tags : Array String) (start : Nat) : List (Tree Tok) → List Json × Nat
  | [] => ([], start)
  | t :: ts =>
    let (a, mid) := treeRows tags start t
    let (b, stop) := kidsRows tags mid ts
    (a ++ b, stop)
end

def treeJson (tags : Array String) (t : Tree Tok) : Json := Json.arr (treeRows tags 0 t).1.toArray

/-! ## `english.read` -/

def status (s : String) : List (String × Json) := [("status", .str s)]

def coded (code text : String) : List (String × Json) := [("code", .str code), ("text", .str text)]

def failureJson (E : Env) (L : Lexicon) : List (String × Json) :=
  match L.failures E {} with
  | (c, k, n) :: _ => [("failure", Json.arr #[.str c, .str k, .str n])]
  | [] => []

def faultName : GrammarFault → String
  | .lexicon => "lexicon"
  | .notWellFormed => "notWellFormed"
  | .notTyped => "notTyped"

def invalidFields (c : Case) (g : GrammarFault) : List (String × Json) :=
  status "invalidGrammar" ++ coded "InvalidGrammar" invalidGrammarText ++ [("fault", .str (faultName g))] ++
    (if g == .lexicon then failureJson c.E c.L else [])

def budgetFields (i : Nat) : List (String × Json) :=
  status "budget" ++ coded "Budget" s!"Sentence {i + 1} needs more work than the limit allows. No verdict was reached." ++
    [("sentence", toJson i)]

/-- The derivation of each sentence of an accepted text: the parser's one tree, read again. -/
def derivations (G : Grammar Terminal) (source : String) : Except String (List Json) := do
  let tags := G.rules.map (·.tag)
  match lex source with
  | .error _ => throw "the accepted text does not lex"
  | .ok sents => sents.toList.mapM fun w =>
      match verdict G workBudget w with
      | some (.one t) => pure (treeJson tags t)
      | _ => throw "an accepted sentence has no single tree"

def authoring (c : Case) (source : String) : Except String (List (String × Json)) := do
  let G := grammar c.E c.L
  let tags := G.rules.map (·.tag)
  match read c.E {} c.L workBudget source with
  | .ok rs =>
    pure (status "one" ++ [("ast", Json.arr (rs.map (·.1.encode)).toArray),
      ("conclusions", toJson ((List.range rs.length).filter fun i => (rs[i]?.map (·.2)).getD false)),
      ("derivation", Json.arr (← derivations G source).toArray)])
  | .invalidGrammar g => pure (invalidFields c g)
  | .lexical r => pure (status "rejected" ++ coded r.code (rejectText 0 r))
  | .illTyped => pure (status "rejected" ++ coded "IllTyped" illTypedText)
  | .stopped i o =>
    let pos := [("sentence", toJson i)]
    match o with
    | .ok _ _ => throw "a stopped reading cannot be ok"
    | .noDerivation => pure (status "none" ++ coded "NoDerivation"
        s!"Sentence {i + 1} has no reading with the current vocabulary." ++ pos)
    | .ambiguous t u => pure (status "many" ++ coded "Ambiguous"
        s!"Sentence {i + 1} can be read in more than one way. Two of the ways are shown." ++ pos ++
        [("witnesses", Json.arr #[treeJson tags t, treeJson tags u])])
    | .rejected r => pure (status "rejected" ++ coded r.code (rejectText i r) ++ pos)
    | .budget => pure (budgetFields i)

def readingJson (r : EFormula × Bool × DState) : Json :=
  Json.mkObj [("formula", r.1.encode), ("mark", .bool r.2.1), ("referents", toJson r.2.2.referents),
    ("binder_seen", .bool r.2.2.binderSeen)]

/-- Translation mode (base 4.3): the status counts the readings that have a meaning. A set that is not
complete is a verdict only when it already has two readings (`many`); with fewer it is `budget`, never
`none` or `one`: the parser stopped at the cap. -/
def translation (c : Case) (cap : Nat) (source : String) : List (String × Json) :=
  match translate c.E {} c.L cap workBudget source with
  | .readings rs complete =>
    let found := [("readings", Json.arr (rs.map readingJson).toArray), ("complete", .bool complete)]
    if 2 ≤ rs.length then
      status "many" ++ coded "Ambiguous" "Sentence 1 can be read in more than one way." ++ found
    else if !complete then budgetFields 0 ++ found
    else if rs.isEmpty then
      status "none" ++ coded "NoDerivation" "Sentence 1 has no reading with the current vocabulary." ++ found
    else status "one" ++ found
  | .invalidGrammar g => invalidFields c g
  | .lexical r => status "rejected" ++ coded r.code (rejectText 0 r)
  | .notOneSentence => status "rejected" ++ coded "NotOneSentence" notOneSentenceText
  | .budget => budgetFields 0

def readCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j ((["id", "environment", "lexicon", "source", "mode", "cap"] ++
    if (j.getObjVal? "overlay").toOption.isSome then ["overlay"] else []))
  let id ← VE.Bridge.stringField j "id"
  let c ← decodeCase j
  let source ← VE.Bridge.stringField j "source"
  let cap ← (← j.getObjVal? "cap").getNat?
  let identities := Json.mkObj ([("source_sha256", .str (VE.CertificateWire.sha256 source.toUTF8))] ++ c.identities)
  let fields ← match ← VE.Bridge.stringField j "mode" with
    | "authoring" => do
      unless cap == 2 do throw "InvalidInput: authoring mode reads at cap 2"
      authoring c source
    | "translation" => pure (translation c cap source)
    | m => throw s!"InvalidInput: unknown reading mode {m}"
  pure (VE.Route.Wire.ok id [("result", Json.mkObj (fields ++ [("identities", identities)]))])

/-! ## `english.grammar` -/

def tokJson : Tok → Json
  | .word t _ => Json.mkObj [("w", .str t)]
  | .quoted n => Json.mkObj [("q", .str n)]
  | .label l i => Json.mkObj [("label", .str l), ("index", toJson i)]
  | .numeral v => Json.mkObj [("num", .str (toString v))]
  | .punct p b a => Json.mkObj [("p", .str p), ("before", .bool b), ("after", .bool a)]

/-- A symbol in the encoding of spec 2.9 and 4.4; an `exact` word, label or numeral, which no rule of the
base profile has, as its token. -/
def symJson (names : Array String) : Sym Terminal → Json
  | .n i => Json.mkObj [("n", .str (names[i]?.getD ""))]
  | .t (.kw s) => .str s
  | .t (.kwMid s) => Json.mkObj [("kwMid", .str s)]
  | .t (.content s) => Json.mkObj [("c", .str s)]
  | .t (.exact t) => tokJson t
  | .t (.cls .numeral) => Json.mkObj [("cls", .str "numeral")]
  | .t (.cls (.label l)) => Json.mkObj [("cls", .str "label"), ("letter", .str l)]

def q (s : String) : String := (Json.str s).compress

def boolText (b : Bool) : String := if b then "true" else "false"

/-- A lexical action's text: its name, then its data, a string quoted, an order as a JSON array. -/
def lexActText : LexAct → String
  | .pred p o n => s!"pred {q p} {(toJson o).compress} {boolText n}"
  | .relSubject p o n => s!"relSubject {q p} {(toJson o).compress} {boolText n}"
  | .relObject p n => s!"relObject {q p} {boolText n}"
  | .noun s n => s!"noun {q s} {q n}"
  | .label s => s!"label {q s}"
  | .const c s nf => s!"const {q c} {q s} {boolText nf}"
  | .adjective p s => s!"adjective {q p} {q s}"
  | .natSubject p s n => s!"natSubject {q p} {q s} {q n}"
  | .copulaRel p => s!"copulaRel {q p}"
  | .owner s1 s2 => s!"owner {q s1} {q s2}"
  | .relation r => s!"relation {q r}"
  | .attribute r => s!"attribute {q r}"
  | .attributeProperty r s => s!"attributeProperty {q r} {q s}"
  | .guard m x a n av risk => s!"guard {m.name} {boolText x} {q a} {q n} {q av} {boolText risk}"
  | .altHead ref => s!"altHead {q ref}"
  | .termOther n => s!"termOther {q n}"

def grammarCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j ((["id", "environment", "lexicon"] ++
    if (j.getObjVal? "overlay").toOption.isSome then ["overlay"] else []))
  let id ← VE.Bridge.stringField j "id"
  let c ← decodeCase j
  let G := grammar c.E c.L
  let fixed := (fixedTable c.E.profiles).size
  let texts := fixedActTexts c.E.profiles
  let lexical := (lexRows c.E c.L).toArray
  -- the catalogue of the profile list, then `property_i` for the `i`-th value sort (S3 spec 2.4)
  let names := ntNamesFor c.E.profiles ++
    ((List.range (valueSorts c.E).length).map fun i => s!"property_{i}").toArray
  let rules := (List.range G.rules.size).filterMap fun i => G.rules[i]?.map fun r =>
    Json.mkObj [("index", toJson i), ("tag", .str r.tag), ("lhs", .str (names[r.lhs]?.getD "")),
      ("act", .str (if i < fixed then texts[i]?.getD "" else
        ((lexical[i - fixed]?).map (lexActText ·.act)).getD "")),
      ("rhs", Json.arr (r.rhs.map (symJson names)).toArray)]
  pure (VE.Route.Wire.ok id [("result", Json.mkObj [("identities", Json.mkObj c.identities),
    ("nonterminals", toJson names), ("ranks", toJson G.rank), ("rules", Json.arr rules.toArray)])])

/-! ## The executable -/

def runCaseReported (mode : String) (j : Json) : Json :=
  let run := if mode == "english.grammar" then grammarCase j else readCase j
  match run with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

def main (args : List String) : IO UInt32 := do
  let usage := "usage: ve_english_route english.read|english.grammar [cases.json|-]"
  let (mode, paths) := match args with
    | m :: rest => (m, rest)
    | [] => ("", [])
  unless mode == "english.read" || mode == "english.grammar" do
    (← IO.getStderr).putStrLn usage
    return 2
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn usage
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported mode j
      | .error message => Json.mkObj [("status", .str "error"), ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.EnglishGrammar.Run
