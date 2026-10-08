import VE.EnglishGrammar.Read
import VE.EnglishGrammar.Fixed.Version
import VE.EnglishGrammar.Fixed.Tables
import VE.Service.Standalone
import VE.Json
import VE.NormDefaults.Wire
import VE.SoftNorms.Wire
import VE.EnglishGrammar.Advice
import VE.EnglishGrammar.Diagnose
import VE.SpeechActs.Wire
import VE.Attribution.Wire
import VE.Readings.Wire

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

/-- `IllTyped`'s text names the first sentence whose formula, with those before it, fails the typed check,
when the mode can find it. -/
def illTypedText : Option Nat → String
  | some i => s!"Sentence {i + 1} was read, and its formula does not pass the type check."
  | none => "The text was read, and its formulas do not pass the type check."
def notOneSentenceText : String := "This text has more than one sentence. Translation mode reads exactly one."

/-- What a refused request did not do, by the mode that refused it: `english.read` reads no text,
`english.grammar` exports no grammar, `english.check` checks no candidate. -/
def notDone (mode : String) : String :=
  if mode == "english.grammar" then "No grammar was exported."
  else if mode == "english.check" then "No candidate was checked." else "No text was read."

/-- `InvalidGrammar`'s text: the fault and, for a refused vocabulary, the first failure, so the relay shows
Lean's text and writes none of its own. -/
def invalidGrammarText (mode fault : String) (failure : Option Failure) : String :=
  s!"The vocabulary selection was not accepted (invalidGrammar {fault}" ++
    (match failure with
     | some (c, k, n) => s!": {c} {k} {n}"
     | none => "") ++ s!"). {notDone mode}"

/-- The rewrites of a sentence `every action available to C cannot lead to H` (Python's text,
`english.py:78–82`): `chooser` and `harm` are the sentence's own words. -/
def riskEveryCannotText (i : Nat) (chooser harm : String) : String :=
  s!"Sentence {i + 1} has two readings. Choose whether no available action might lead to the harm: 'it is not " ++
  s!"the case that there is an action such that both that action is available to {chooser} and that action " ++
  s!"might lead to {harm}'; or some available action cannot lead to it: 'there is an action such that both " ++
  s!"that action is available to {chooser} and that action cannot lead to {harm}'."

def codeClasses : List (String × String) :=
  [("SourceTooLong", "ResourceLimit"), ("TextTooLong", "ResourceLimit"), ("BadCharacter", "SyntaxError"),
   ("OpenQuote", "SyntaxError"), ("BadNumeral", "SyntaxError"), ("EmptyDocument", "SyntaxError"),
   ("EmptySentence", "SyntaxError"), ("Unterminated", "SyntaxError"), ("BadSpacing", "SyntaxError"),
   ("UnboundReference", "SyntaxError"), ("ShadowedName", "SyntaxError"), ("SortMismatch", "SyntaxError"),
   ("MarkerDepth", "SyntaxError"), ("NestingLimit", "ResourceLimit"), ("NumeralBound", "ResourceLimit"),
   ("CoefficientNotNumeral", "SyntaxError"), ("PronounUnresolved", "SyntaxError"),
   ("BlockedWording", "SyntaxError"), ("CoordinationRepeated", "SyntaxError"), ("CoordinationForm", "SyntaxError"),
   ("NaturalScoped", "SyntaxError"), ("RelativeForm", "SyntaxError"), ("Internal", "CheckerUnavailable"),
   ("NoDerivation", "SyntaxError"), ("Ambiguous", "AmbiguousDerivation"), ("Budget", "ResourceLimit"),
   ("InvalidGrammar", "CheckerUnavailable"), ("ConclusionWithoutPremise", "SyntaxError"),
   ("ConclusionNotDerived", "SyntaxError"), ("IllTyped", "TypeMismatch"), ("NotOneSentence", "SyntaxError"),
   ("InvalidOverlay", "VEError")]

theorem codeClasses_total : ∀ r : Reject, (codeClasses.lookup r.code).isSome = true := by
  intro r
  cases r <;> rfl

/-- Every code of `Reject.code`, in constructor order. -/
def rejectCodes : List String :=
  ["SourceTooLong", "TextTooLong", "BadCharacter", "OpenQuote", "BadNumeral", "EmptyDocument", "EmptySentence",
   "Unterminated", "BadSpacing", "UnboundReference", "ShadowedName", "SortMismatch", "MarkerDepth", "NestingLimit",
   "NumeralBound", "CoefficientNotNumeral", "PronounUnresolved", "BlockedWording", "CoordinationRepeated",
   "CoordinationForm", "NaturalScoped", "RelativeForm", "Internal"]

theorem rejectCodes_total : ∀ r : Reject, r.code ∈ rejectCodes := by
  intro r
  cases r <;> simp [Reject.code, rejectCodes]

/-- The codes each status of a response may carry (spec 4.4), exported by `english.grammar` with the class
table: together they are the relay's whole table of codes, classes and statuses. -/
def statusCodes : List (String × List String) :=
  [("none", ["NoDerivation"]), ("many", ["Ambiguous"]), ("budget", ["Budget"]),
   ("invalidGrammar", ["InvalidGrammar", "InvalidOverlay"]),
   ("rejected", rejectCodes ++ ["ConclusionWithoutPremise", "IllTyped", "NotOneSentence"])]

theorem statusCodes_classed : ∀ s ∈ statusCodes, ∀ c ∈ s.2, (codeClasses.lookup c).isSome = true := by
  decide

/-- The rejection codes that name no sentence: the lexer's, which refuse the whole source before any sentence is
read, and translation mode's `NotOneSentence`. Every other refusal names its sentence (spec 4.4). -/
def unsentencedCodes : List String :=
  ["SourceTooLong", "TextTooLong", "BadCharacter", "OpenQuote", "BadNumeral", "EmptyDocument", "EmptySentence",
   "Unterminated", "BadSpacing", "NotOneSentence"]

def noPremiseText (i : Nat) : String :=
  s!"Sentence {i + 1} is marked as a conclusion, and no earlier sentence is a premise."
/-- The obligation's `unproved`: the relay puts the entailment operation's status for `{status}`, verbatim. -/
def unprovedText (i : Nat) : String :=
  s!"Sentence {i + 1} is marked as a conclusion, and no checked derivation from the earlier premises was found: " ++
    "{status}"


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
  ps.contains "alternatives@0" || ps.contains "risk@0" || ps.contains "norm-defaults@0" ||
    ps.contains "soft-norms@0" || ps.contains "reports@0" || ps.contains "readings@1" ||
    ps.contains "speech-acts@0" || (environment.getObjVal? "speech_acts").isOk ||
    (environment.getObjVal? "units").isOk ||
    (environment.getObjVal? "unit_schema").isOk ||
    (environment.getObjVal? "alternatives").isOk || (environment.getObjVal? "risk").isOk

/-- The submitted environment without the statement layers' profiles and declarations (`readings@1`,
`reports@0`, `speech-acts@0`, `rights@0`), which the block routes do not combine with their own; those are
validated by their own decoders below, and the typing view drops them. -/
def layerView (environment : Json) : Json := Id.run do
  let vocabulary := environment.getObjValD "vocabulary"
  let profiles := (VE.Route.Gate.profilesOf environment).toOption.getD []
  let profiles := profiles.filter (fun p => p != "readings@1" && p != "reports@0" &&
    p != "speech-acts@0" && p != "rights@0")
  let vocabulary := VE.Risk.Wire.dropField "reports" (VE.Risk.Wire.dropField "rights" vocabulary)
  let environment := VE.Risk.Wire.dropField "speech_acts" environment
  return (environment.setObjVal! "profiles" (toJson profiles)).setObjVal! "vocabulary" vocabulary

/-- The norms routes also enforce document-scope restrictions on flags, definitions and literals. Those
declarations are checked on the submitted environment by `validated (typingView environment)` below. Remove
only those declarations from the norms routes' view, so the routes can check the W6 annotations without
deciding whether an unrelated profile may be combined with them (md1c). -/
def blockRouteView (environment : Json) : Json := Id.run do
  let environment := layerView environment
  let vocabulary := environment.getObjValD "vocabulary"
  let predicates := VE.Risk.Wire.mapEntries (fun entry =>
    VE.Risk.Wire.dropField "defined" (VE.Risk.Wire.dropField "total"
      (VE.Risk.Wire.dropField "functional" entry))) (vocabulary.getObjValD "predicates")
  let constants := match VE.Bridge.fields (vocabulary.getObjValD "constants") with
    | .ok cs => Json.mkObj (cs.filter fun (_, entry) => entry.getObjValD "sort" != .str "$string")
    | .error _ => vocabulary.getObjValD "constants"
  return environment.setObjVal! "vocabulary"
    ((vocabulary.setObjVal! "predicates" predicates).setObjVal! "constants" constants)

/-- The optional fields of an English request: the overlay, and `generated` (E2.6). -/
def optionalFields (j : Json) : List String :=
  ["overlay", "generated"].filter fun k => (j.getObjVal? k).toOption.isSome

/-- Whether the request reads Python's generated soft frame (`SoftEnvironment(prime, generated=True)`: the soft
route's `E′` with its `soft__` decision predicates). Present only as `true`. -/
def generatedFrame (j : Json) : Except String Bool :=
  match j.getObjVal? "generated" with
  | .error _ => pure false
  | .ok (.bool true) => pure true
  | .ok _ => throw "InvalidInput: generated is true when present"

/-- A generated soft frame as the soft route reads it (`check_soft_source(..., generated=True)`): without the
`soft__` predicates the route generated, which a submitted environment may not declare. -/
def generatedView (environment : Json) : Json :=
  let vocabulary := environment.getObjValD "vocabulary"
  let predicates := match VE.Bridge.fields (vocabulary.getObjValD "predicates") with
    | .ok ps => Json.mkObj (ps.filter fun (p, _) => !p.startsWith "soft__")
    | .error _ => vocabulary.getObjValD "predicates"
  environment.setObjVal! "vocabulary" (vocabulary.setObjVal! "predicates" predicates)

/-- Part 1 of the boundary (S3 spec 2.3): check the profile blocks and W6 declarations by the route
decoders on the submitted environment (without the statement layers), using an empty document. The
alternatives environment scope validates other profiles' declarations with their owner while preserving
fixed role predicates. -/
def validateDeclarations (environment : Json) (generated : Bool := false) : Except String Unit := do
  -- A generated soft frame is checked by every route as the soft route checks it: without its `soft__` predicates.
  let environment := if generated then generatedView environment else environment
  let ps := (VE.Route.Gate.profilesOf environment).toOption.getD []
  if ps.contains "risk@0" || (environment.getObjVal? "risk").isOk then
    let _ ← VE.Risk.Wire.decodeRiskSource (layerView environment) (Json.mkObj [("norms", Json.arr #[])])
  else if ps.contains "alternatives@0" || (environment.getObjVal? "alternatives").isOk then
    let _ ← VE.Alternatives.Wire.decodeAltSource (layerView environment) (Json.arr #[]) (Json.arr #[])
      .environment
  if ps.contains "norm-defaults@0" then
    let _ ← VE.NormDefaults.Wire.decodeSourceU (blockRouteView environment) (Json.arr #[])
  else if ps.contains "soft-norms@0" then
    let _ ← VE.SoftNorms.Wire.decodeSoftSource (blockRouteView environment) (Json.arr #[])
  if ((environment.getObjVal? "units").isOk || (environment.getObjVal? "unit_schema").isOk) &&
      !ps.contains "risk@0" then
    let ext ← VE.Risk.Wire.extended environment
    let units ← VE.Risk.Wire.decodeUnits environment
    VE.Risk.Wire.checkVocabularyUnits environment units ext
    VE.Risk.Wire.checkExtension environment units
  -- The statement-layer profiles: their declarations are validated as submitted by their routes' own
  -- environment decoders before the typing view drops them (review B2 of E2).
  if ps.contains "speech-acts@0" || (environment.getObjVal? "speech_acts").isOk then
    let _ ← VE.SpeechActs.Wire.decodeSpeechEnvironmentFull environment
  if ps.contains "reports@0" then
    let _ ← VE.Reports.Wire.decodeEnvironment environment
  if ps.contains "readings@1" then
    let _ ← VE.Readings.Wire.decodeEnvironment environment

/-- The environment identity, as the typing service computes it; for an environment with a profile block, after
the three parts of the boundary (S3 spec 2.3). -/
def environmentId (environment : Json) (generated : Bool := false) : Except String String := do
  if declaresBlock environment then
    validateDeclarations environment generated
    let _ ← VE.Service.Standalone.validated (← typingView environment)
    VE.Service.Standalone.environmentIdOf (← VE.Route.Gate.profilesOf environment) environment
  else
    let row ← VE.Service.Standalone.environmentCase (Json.mkObj [("id", .str "e"), ("environment", environment)])
    VE.Bridge.stringField row "environment_id"

/-- The tables of the profiles that have one, with the SHA-256 of each JSON source (spec 2.5, 2.10; S3
2.14): the generated list, never a copy. -/
def tables : List (String × String) := tableSources

/-- The digest of the environment's profiles that have a table, in the environment's order (base 2.12). -/
def grammarId (profiles : List String) : Except String String :=
  VE.CertificateWire.digest "ve-english-grammar-v1\n"
    (Json.arr (profiles.filterMap fun p => (VE.Bridge.lookup tables p).map fun h =>
      Json.arr #[.str p, .str h]).toArray)

/-- A decoded case: the reader's inputs and the identities that do not depend on the source. -/
structure Case where
  E : Env
  O : Overlay
  L : Lexicon
  overlayFailure : Option Failure
  identities : List (String × Json)

def decodeCase (j : Json) : Except String Case := do
  let environment ← j.getObjVal? "environment"
  let overlay ← match j.getObjVal? "overlay" with
    | .ok (.obj o) => pure (Json.obj o)
    | .ok _ => throw "InvalidInput: the overlay is not an object"
    | .error _ => pure (Json.mkObj [])
  let generated ← generatedFrame j
  let envId ← environmentId environment generated
  let lexicon ← j.getObjVal? "lexicon"
  let lexiconEnvId ← environmentId (displayJson environment overlay) generated
  let L ← decodeLexicon lexiconEnvId lexicon
  let E ← Env.decode environment overlay
  let O ← Overlay.decode overlay
  let overlayFailure := overlayCheck E O
  let overlayDigest ← match j.getObjVal? "overlay" with
    | .ok o => pure [("overlay_digest", Json.str (← VE.CertificateWire.digest "ve-english-vocabulary-v1\n" o))]
    | .error _ => pure []
  pure { E, O, L, overlayFailure, identities := [("environment_id", .str envId)] ++ overlayDigest ++
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

/-- A lexer byte boundary measured in source code points. -/
def codepointsBefore (source : String) (offset : Nat) : Nat :=
  (source.toList.foldl (fun (bytes, count) c =>
    if bytes < offset then (bytes + c.utf8Size, count + 1) else (bytes, count)) (0, 0)).2

/-- Python's sentence spans include the final period and exclude the following separator. -/
def sentenceSpans (source : String) : List (Nat × Nat) :=
  match lexSpans source with
  | .error _ => []
  | .ok sentences => sentences.toList.filterMap fun sent => do
      let first ← sent.toList.head?
      let last ← sent.toList.getLast?
      pure (codepointsBefore source first.2.1, codepointsBefore source (last.2.2 + 1))

def spanJson (span : Nat × Nat) : Json := Json.arr #[toJson span.1, toJson span.2]

/-! ## `english.read` -/

def status (s : String) : List (String × Json) := [("status", .str s)]

def coded (code text : String) : List (String × Json) :=
  [("code", .str code), ("text", .str text)] ++
    (codeClasses.lookup code |>.toList.map fun cls => ("class", Json.str cls))

def failureJson (E : Env) (L : Lexicon) : List (String × Json) :=
  match lexiconFailure E {} L with
  | some (c, k, n) => [("failure", Json.arr #[.str c, .str k, .str n])]
  | none => []

def faultName : GrammarFault → String
  | .lexicon => "lexicon"
  | .notWellFormed => "notWellFormed"
  | .notTyped => "notTyped"

def invalidFields (mode : String) (c : Case) (g : GrammarFault) : List (String × Json) :=
  let failure := if g == .lexicon then lexiconFailure c.E {} c.L else none
  status "invalidGrammar" ++ coded "InvalidGrammar" (invalidGrammarText mode (faultName g) failure) ++
    [("fault", .str (faultName g))] ++ (if g == .lexicon then failureJson c.E c.L else [])

def invalidOverlayFields (mode : String) (f : Failure) : List (String × Json) :=
  status "invalidGrammar" ++ coded "InvalidOverlay" (overlayText f ++ " " ++ notDone mode) ++
    [("failure", Json.arr #[.str f.1, .str f.2.1, .str f.2.2])]

def budgetFields (i : Nat) : List (String × Json) :=
  status "budget" ++ coded "Budget" s!"Sentence {i + 1} needs more work than the limit allows. No verdict was reached." ++
    [("sentence", toJson i)]

/-- `NoDerivation` for sentence `i`: Lean's text, then what the sentence needs where it stops and the span of
that place (`diagnose`, spec 4.5); the text alone when the budget does not allow finding it. -/
def noReadingFields (c : Case) (source : String) (i : Nat) : List (String × Json) :=
  let text := s!"Sentence {i + 1} has no reading with the current vocabulary."
  let found := match lexSpans source with
    | .ok sents => (sents[i]?).bind (diagnose c.E c.L source)
    | .error _ => none
  match found with
  | some d => status "none" ++ coded "NoDerivation" (text ++ " " ++ d.text) ++
      [("span", spanJson (codepointsBefore source d.span.1, codepointsBefore source d.span.2))]
  | none => status "none" ++ coded "NoDerivation" text

/-- The code points of the offending character of a lexical rejection that names one (spec 4.4). -/
def lexicalSpan (source : String) : Reject → Option (Nat × Nat)
  | .badCharacter o | .openQuote o | .badNumeral o | .badSpacing o =>
    let start := codepointsBefore source o
    some (start, min (start + 1) source.length)
  | _ => none

/-- The first sentence whose formula, with the formulas before it, fails the typed check: the sentence an
`IllTyped` refusal names (spec 4.4). `read` checks the whole document; this finds the prefix that fails. -/
def illTypedSentence (c : Case) (source : String) : Nat :=
  match lex source with
  | .error _ => 0
  | .ok sents =>
    match readDocument (grammar c.E c.L) (meaning (grammar c.E c.L) (acts c.E c.L)) DState.init workBudget
        sents.toList with
    | (.ok rs, _) =>
      let fs := rs.map (·.1)
      ((List.range fs.length).find? fun i => !typedDocument c.E (fs.take (i + 1))).getD 0
    | _ => 0

/-- The source text from the start of token `a` to the end of token `b` of a sentence. -/
def between (source : String) (toks : Array Spanned) (a b : Nat) : Option String := do
  let first ← toks[a]?
  let last ← toks[b]?
  if a ≤ b then pure (source.extract ⟨first.2.1⟩ ⟨last.2.2⟩) else none

/-- The chooser and the harm of `every action available to C cannot lead to H`, as the sentence writes them. -/
def everyCannotParts (source : String) (toks : Array Spanned) : Option (String × String) := do
  let words := toks.toList.map fun t => match t.1 with
    | .word w _ => some (fold w)
    | _ => none
  let avail ← (List.range words.length).find? fun k =>
    words[k]? == some (some "available") && words[k + 1]? == some (some "to")
  let cannot ← (List.range words.length).find? fun m =>
    avail + 2 < m && words[m]? == some (some "cannot") && words[m + 1]? == some (some "lead") &&
      words[m + 2]? == some (some "to")
  let chooser ← between source toks (avail + 2) (cannot - 1)
  let harm ← between source toks (cannot + 3) (toks.size - 1)
  pure (chooser, harm)

/-- The text of a rejection of sentence `i`; a blocked wording with rewrites names the sentence's words. -/
def rejectionText (source : String) (i : Nat) (r : Reject) : String :=
  match r with
  | .blockedWording "risk-every-cannot" =>
    let parts := match lexSpans source with
      | .ok sents => (sents[i]?).bind (everyCannotParts source)
      | .error _ => none
    let (chooser, harm) := parts.getD ("the chooser", "the harm")
    riskEveryCannotText i chooser harm
  | _ => rejectText i r

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
  if let some f := c.overlayFailure then return invalidOverlayFields "english.read" f
  let G := grammar c.E c.L
  let tags := G.rules.map (·.tag)
  match admitRequest c.E {} c.L workBudget source with
  | .ok rs obs =>
    pure (status "one" ++ [("ast", Json.arr (rs.map (·.1.encode)).toArray),
      ("conclusions", toJson ((List.range rs.length).filter fun i => (rs[i]?.map (·.2)).getD false)),
      ("derivation", Json.arr (← derivations G source).toArray),
      ("obligations", Json.arr (obs.map (fun (i, js) => Json.mkObj
        [("conclusion", toJson i), ("premises", toJson js), ("unproved", .str (unprovedText i))])).toArray),
      ("spans", toJson ((sentenceSpans source).map spanJson))])
  | .noPremise i => pure (status "rejected" ++ coded "ConclusionWithoutPremise" (noPremiseText i) ++
      [("sentence", toJson i)])
  | .refused (.ok _) => throw "a refused reading cannot be ok"
  | .refused (.invalidGrammar g) => pure (invalidFields "english.read" c g)
  | .refused (.lexical r) => pure (status "rejected" ++ coded r.code (rejectText 0 r) ++
      ((lexicalSpan source r).toList.map fun s => ("span", spanJson s)))
  | .refused (.illTyped) =>
    let i := illTypedSentence c source
    pure (status "rejected" ++ coded "IllTyped" (illTypedText (some i)) ++ [("sentence", toJson i)])
  | .refused (.stopped i o) =>
    let pos := [("sentence", toJson i)]
    match o with
    | .ok _ _ => throw "a stopped reading cannot be ok"
    | .noDerivation => pure (noReadingFields c source i ++ pos)
    | .ambiguous t u => pure (status "many" ++ coded "Ambiguous"
        s!"Sentence {i + 1} can be read in more than one way. Two of the ways are shown." ++ pos ++
        [("witnesses", Json.arr #[treeJson tags t, treeJson tags u])])
    | .rejected r => pure (status "rejected" ++ coded r.code (rejectionText source i r) ++ pos)
    | .budget => pure (budgetFields i)

def readingJson (r : EFormula × Bool × DState) : Json :=
  Json.mkObj [("formula", r.1.encode), ("mark", .bool r.2.1), ("referents", toJson r.2.2.referents),
    ("binder_seen", .bool r.2.2.binderSeen)]

/-- Translation mode (base 4.3): the status counts the readings that have a meaning. A set that is not
complete is a verdict only when it already has two readings (`many`); with fewer it is `budget`, never
`none` or `one`: the parser stopped at the cap. -/
def translation (c : Case) (cap : Nat) (source : String) : List (String × Json) :=
  if let some f := c.overlayFailure then invalidOverlayFields "english.read" f else
  match translateRequest c.E {} c.L cap workBudget source with
  | .readings rs complete =>
    let found := [("readings", Json.arr (rs.map readingJson).toArray), ("complete", .bool complete)]
    if 2 ≤ rs.length then
      status "many" ++ coded "Ambiguous" "Sentence 1 can be read in more than one way." ++ found
    else if !complete then budgetFields 0 ++ found
    else if rs.isEmpty then
      noReadingFields c source 0 ++ found
    else status "one" ++ found
  | .invalidGrammar g => invalidFields "english.read" c g
  | .lexical r => status "rejected" ++ coded r.code (rejectText 0 r) ++
      ((lexicalSpan source r).toList.map fun s => ("span", spanJson s))
  | .notOneSentence => status "rejected" ++ coded "NotOneSentence" notOneSentenceText
  | .budget => budgetFields 0

/-- What every refusal of a reading adds (spec 4.4), in `english.read` and `senses.read` alike: the span of the
sentence it names, or of the whole source when it names none (a lexical rejection already carries its
character's), and Lean's advice for a sentence without a reading or that the reader refused (spec 4.3). -/
def refusalExtras (profiles : List String) (source : String) (fields : List (String × Json)) :
    List (String × Json) :=
  let status := (VE.Bridge.lookup fields "status").getD .null
  let sentence := (VE.Bridge.lookup fields "sentence").bind (fun j => j.getNat?.toOption)
  let fields := if [.str "rejected", .str "none", .str "many", .str "budget"].contains status &&
      (VE.Bridge.lookup fields "span").isNone then
    let span := ((sentence.bind fun i => (sentenceSpans source)[i]?)).getD (0, source.length)
    fields ++ [("span", spanJson span)]
  else fields
  if status == .str "none" || (status == .str "rejected" && sentence.isSome) then
    let toks := match lex source with
      | .ok ss => ((ss[sentence.getD 0]?).getD #[]).toList
      | .error _ => []
    match advice profiles toks with
    | some (name, tip) => fields ++ [("advice", Json.mkObj [("id", .str name), ("text", .str tip)])]
    | none => fields
  else fields

def readCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j ((["id", "environment", "lexicon", "source", "mode", "cap"] ++
    optionalFields j))
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
  let fields := refusalExtras c.E.profiles source fields
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

/-- The port's selection (spec 2.3): Python's choice of every predicate's wording and negative, every noun and
every spelling, as V6 compares a lexicon with it. Exported so the parity harness (spec 2.10) compares the port
with Python's `EnglishVocabulary` symbol by symbol; it decides nothing here. -/
def policyJson (E : Env) : Json :=
  let chosen := E.predicates.filterMap fun d => (policyPredicate E {} d.name).map (d.name, ·)
  Json.mkObj [("wordings", toJson (chosen.map fun (p, w, _) => (p, w))),
    ("negatives", toJson (chosen.filterMap fun (p, _, n) => n.map (p, ·))),
    ("nouns", toJson (policyNouns E {})), ("spellings", toJson (policySpellings E {}))]

def grammarCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j ((["id", "environment", "lexicon"] ++
    optionalFields j))
  let id ← VE.Bridge.stringField j "id"
  let c ← decodeCase j
  if let some f := c.overlayFailure then
    return VE.Route.Wire.ok id [("result", Json.mkObj (invalidOverlayFields "english.grammar" f ++
      [("identities", Json.mkObj c.identities)]))]
  if let some g := grammarFault c.E {} c.L then
    return VE.Route.Wire.ok id [("result", Json.mkObj (invalidFields "english.grammar" c g ++
      [("identities", Json.mkObj c.identities)]))]
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
  let awJson : AdvWord → Json
    | .w w => .str w
    | .any => .str "*"
    | .anyBut w => Json.mkObj [("anyBut", .str w)]
  let advice := adviceRows.map fun r => Json.mkObj
    [("id", .str r.id), ("profile", .str r.profile),
     ("patterns", toJson (r.patterns.map fun pat => pat.map awJson)), ("text", .str r.text)]
  pure (VE.Route.Wire.ok id [("result", Json.mkObj [("identities", Json.mkObj c.identities),
    ("nonterminals", toJson names), ("ranks", toJson G.rank), ("rules", Json.arr rules.toArray),
    ("codes", toJson codeClasses), ("statuses", toJson statusCodes), ("unsentenced", toJson unsentencedCodes),
    ("advice", toJson advice),
    ("policy", policyJson c.E)])])

def checkCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j ((["id", "environment", "lexicon", "formulas", "marks", "candidates"] ++
    optionalFields j))
  let id ← VE.Bridge.stringField j "id"
  let c ← decodeCase j
  let result (fields : List (String × Json)) :=
    VE.Route.Wire.ok id [("result", Json.mkObj (fields ++ [("identities", Json.mkObj c.identities)]))]
  if let some f := c.overlayFailure then return result (invalidOverlayFields "english.check" f)
  if let some g := grammarFault c.E {} c.L then return result (invalidFields "english.check" c g)
  let raw ← (← j.getObjVal? "formulas").getArr?
  let formulas ← raw.toList.mapM fun f =>
    match EFormula.decode f with
    | some A => pure A
    | none => throw "InvalidInput: formula is not an English wire formula"
  let marks ← (← (← j.getObjVal? "marks").getArr?).toList.mapM Json.getBool?
  unless formulas.length == marks.length do throw "InvalidInput: one mark is required for each formula"
  let candidates ← VE.Bridge.strings (← j.getObjVal? "candidates")
  let rs := formulas.zip marks
  let fields := match checkRequest c.E {} c.L workBudget rs candidates with
    | some i => [("index", toJson i)]
    | none => []
  return result fields

/-! ## The executable -/

def runCaseReported (mode : String) (j : Json) : Json :=
  let run := if mode == "english.grammar" then grammarCase j
    else if mode == "english.check" then checkCase j else readCase j
  match run with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

def readCaseReported (j : Json) : Json := runCaseReported "english.read" j
def grammarCaseReported (j : Json) : Json := runCaseReported "english.grammar" j
def checkCaseReported (j : Json) : Json := runCaseReported "english.check" j

/-- The one-shot S2 transport remains in use until the Python E2 relay switches to the service.
Its reader accepts the S2 result fields exactly. Keep the E2 additions on the service mode. -/
def legacyRow (mode : String) (request row : Json) : Json :=
  if mode != "english.read" then row else
  match VE.Bridge.fields (row.getObjValD "result") with
  | .error _ => row
  | .ok fields =>
    let fields := fields.filter fun (name, _) =>
      !["class", "span", "spans", "advice", "obligations"].contains name
    let fields := if fields.lookup "status" == some (.str "invalidGrammar") then
      match decodeCase request with
      | .error _ => fields
      | .ok c => match (c.L.failures c.E {}).head? with
        | none => fields
        | some (code, kind, name) => (fields.filter (·.1 != "failure")) ++
          [("failure", Json.arr #[.str code, .str kind, .str name])]
    else fields
    row.setObjVal! "result" (Json.mkObj fields)

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
      | .ok j => legacyRow mode j (runCaseReported mode j)
      | .error message => Json.mkObj [("status", .str "error"), ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.EnglishGrammar.Run
