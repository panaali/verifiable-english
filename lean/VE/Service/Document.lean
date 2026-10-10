import VE.Service.Standalone
import VE.Discourse.Admission
import VE.Alternatives.Run
import VE.Risk.Run
import VE.NormDefaults.Run
import VE.Readings.Run
import VE.EnglishGrammar.Run
import VE.Attribution.Preflight

/-! # The `document` service mode: the `ve-document@1` wrapper (docs/LEAN-FIRST-PLAN.md, row 16a)

A case is `{"id", "document"}`, the document text Python's `ve/document.py` reads. The mode does what
`load_document` and the wrapper part of `check_document` (`_report`: the claim graph's admission and the
narrowing choices, then `coverage`) do, in their order and with their texts: the front matter, the fences, the
units and their spans, `MIXED` parts, every unit's content, meaning and status, the open terms, the reading sets
with their status fold, the couplings and completions gates, lemmas, narrowings and removable weights, the graph's
W2 admission, the identities, and the coverage tables with their residual counts. The steps it shares with the
discourse route are `VE.Discourse.Loader`'s, read in their `python` mode; every formula is checked by the `check`
mode's typed decoder with Python's typing texts (`formulaCheck`). An `alternatives@0` or `risk@0` document is
composed from that block's own route, as Python composes it: the block route decodes the environment, admits the
claim graph and owns the coverage line (`alternatives` and its residual counts, `Alternatives.Wire.coverage`).

What the mode cannot decide yet is `CheckerUnavailable`, never a verdict (`unavailable`): a `ve-document@2`
document (the discourse route's), a document with `senses` (the senses route's), front matter Python's JSON
reader reads as other values (`NaN`, `Infinity`, a number other than a natural at most 2^53-1, and `null`
anywhere but a unit's `content` or `status` or a part's `content`), an
environment outside the plain `ve.core@0.2` envelope or with a profile outside `ownedProfiles` (each such profile's
loader adds checks and coverage lines its own Lean route owns), regulated or norm content, fenced English or strict
content, a distinguishing model the Lean model decoder refuses, and a claim graph the Lean admission route defers.
`ve/document.py` keeps its own path for exactly these answers (batch 16b, `docs/lean-first/b16b/DELTA.md`). -/
namespace VE.Service.Document
open Lean
open VE.Discourse
open VE.Bridge (stringField fields)
open VE.Route.Admission (token)

def unavailable (what : String) : String := "CheckerUnavailable: " ++ what

/-- The profiles whose document semantics this mode owns: the FOL family with the statement layers whose
`load_document` steps and coverage lines are the plain wrapper's. A document listing any other profile is
`CheckerUnavailable` before its environment is decoded (its own loader would add checks this mode lacks). -/
def ownedProfiles : List String :=
  ["alternatives@0", "data@0", "definitions@0", "documents@1", "norm-defaults@0", "norms@0",
   "readings@1", "relational-fol@0", "risk@0", "time@0"]

/-- The statement block whose route this mode composes: none, `alternatives@0`, or `risk@0` (over its
alternatives block). -/
inductive Block | none | alternatives | risk
  deriving DecidableEq

def blockOf (profiles : List String) : Block :=
  if profiles.contains "risk@0" then .risk else if profiles.contains "alternatives@0" then .alternatives else .none

/-- The keys of the `ve.core@0.2` envelope (`Route.Gate.decodeEnvelope`), with the composed block's own. -/
def envelopeKeys (b : Block) : List String :=
  ["language", "profiles", "spec_revision", "vocabulary"] ++
    match b with
    | .none => []
    | .alternatives => ["alternatives"]
    | .risk => ["alternatives", "risk"]

/-- `listed_profiles`: the profiles of environment JSON when they are a list of strings, else none. -/
def listedProfiles (environment : Json) : List String :=
  (VE.Route.Gate.profilesOf environment).toOption.getD []

/-- The lower norms environment on which the readings route builds each free document. -/
def lowerReadings (environment : Json) : Json :=
  environment.setObjVal! "profiles" (toJson ((listedProfiles environment).filter (· != "readings@1")))

/-! ## The front matter -/

/-- Whether Python's JSON reader may read a front matter Lean.Json.parse refuses: Python's non-standard
constants. An over-approximation: it only turns a rejection into `CheckerUnavailable`. -/
def pythonMayRead (front : String) : Bool :=
  ["NaN", "Infinity"].any fun t => (front.splitOn t).length > 1

/-- The largest number the document mode reads, `VE.JsonInput`'s bound. -/
def maxNumber : Nat := 9007199254740991

def hexDigit (c : Char) : Option Nat :=
  if c.isDigit then some (c.toNat - '0'.toNat)
  else if 'a' ≤ c && c ≤ 'f' then some (c.toNat - 'a'.toNat + 10)
  else if 'A' ≤ c && c ≤ 'F' then some (c.toNat - 'A'.toNat + 10)
  else none

def hex4 (a b c d : Char) : Option Nat := do
  pure ((← hexDigit a) * 4096 + (← hexDigit b) * 256 + (← hexDigit c) * 16 + (← hexDigit d))

def numberChar (c : Char) : Bool := c.isDigit || c == '-' || c == '+' || c == '.' || c == 'e' || c == 'E'

/-- What of a JSON text `Lean.Json.parse` reads that Python's `json.loads` reads as another value. -/
inductive Foreign
  /-- A number other than a natural at most `maxNumber`: Python reads `2e0` and `2.0` as floats and `-0` as an
  integer, where Lean reads naturals or other numbers, so a span, a version or an index would be decided
  differently. Python decides it (`CheckerUnavailable`). -/
  | number
  /-- An unpaired surrogate escape: a Python string no UTF-8 text holds. Both loaders refuse it with the JSON
  boundary's diagnostic after the metadata and body checks (`loneSurrogate` in `split`; `_no_lone_surrogate`). -/
  | surrogate
  /-- The lexer's fuel ran out (fail closed). -/
  | exhausted
  deriving DecidableEq

/-- The JSON boundary's diagnostic of a lone surrogate (docs/spec/v0-language.md; `ve.wire.LONE_SURROGATE`). -/
def loneSurrogate : String := "JSON strings must not contain lone UTF-16 surrogates"

/-- The first lexeme of a JSON text whose kind is `.surrogate` (with `surrogates`) or `.number` (without), or
`.exhausted`. Read only after `Lean.Json.parse` accepted the text, so its strings and numbers are well formed;
`quoted` is whether the lexer is inside a string. -/
def foreignLexeme (surrogates : Bool) : Nat → Bool → List Char → Option Foreign
  | _, _, [] => none
  | 0, _, _ :: _ => some .exhausted
  | fuel + 1, true, '"' :: cs => foreignLexeme surrogates fuel false cs
  | fuel + 1, true, '\\' :: 'u' :: a :: b :: c :: d :: cs =>
    -- Whether this escape is a lone surrogate; the lexer then goes on once, past it (a strict `let` of the
    -- continuation would run it at every escape, exponentially).
    let paired := match cs with
      | '\\' :: 'u' :: e :: f :: g :: h :: _ => (hex4 e f g h).any fun w => 0xDC00 ≤ w && w < 0xE000
      | _ => false
    match hex4 a b c d with
    | some v =>
      if 0xD800 ≤ v && v < 0xDC00 && paired then foreignLexeme surrogates fuel true (cs.drop 6)
      else if 0xD800 ≤ v && v < 0xE000 && surrogates then some .surrogate
      else foreignLexeme surrogates fuel true cs
    | none => foreignLexeme surrogates fuel true cs
  | fuel + 1, true, '\\' :: _ :: cs => foreignLexeme surrogates fuel true cs
  | fuel + 1, true, _ :: cs => foreignLexeme surrogates fuel true cs
  | fuel + 1, false, '"' :: cs => foreignLexeme surrogates fuel true cs
  | fuel + 1, false, c :: cs =>
    if c == '-' || c.isDigit then
      let token := (c :: cs).takeWhile numberChar
      if surrogates || token.all Char.isDigit && (String.mk token).toNat! ≤ maxNumber then
        foreignLexeme surrogates fuel false (cs.drop (token.length - 1))
      else some .number
    else foreignLexeme surrogates fuel false cs

#guard [("[0, 2]", none), ("[0, 2e0]", some Foreign.number), ("[2.0]", some .number), ("[-0]", some .number),
  ("[9007199254740991]", none), ("[9007199254740992]", some .number), ("[\"2.0 -1 1e3\"]", none),
  ("[\"\\ud83d\\ude00\"]", none), ("[\"\\ud800\"]", some .surrogate), ("[\"\\udc00x\"]", some .surrogate),
  ("[\"\\ud800\\u0041\"]", some .surrogate), ("[\"\\\\ud800\"]", none)].all fun (t, r) =>
    foreignLexeme (r == some .surrogate) (t.length + 1) false t.toList == r &&
      foreignLexeme (r != some .surrogate) (t.length + 1) false t.toList == none

-- Linear in the escapes: 4,000 of them (a strict continuation took longer than the service deadline at 200).
#guard let t := "[\"" ++ String.join (List.replicate 4000 "\\u00e9") ++ "\", 1]"
  foreignLexeme true (t.length + 1) false t.toList == none && foreignLexeme false (t.length + 1) false t.toList == none

#guard foreignLexeme true 100 false "[\"\\ud800\", 2e0]".toList == some .surrogate &&
  foreignLexeme false 100 false "[\"\\ud800\", 2e0]".toList == some .number

/-- The members whose `null` the mode reads as Python's loader reads it, as absent (`unit.get(...)`): a unit's or
a `MIXED` part's `content` and a unit's `status`. -/
def nullableUnitKeys (part : Bool) : List String := if part then ["content"] else ["content", "status"]

/-- The first `null` of the front matter outside `nullableUnitKeys`. Python's loader reads `null` per field (absent
for some, a wrong type for others, with its own texts); the mode reads only these, and any other is Python's. -/
def hasNull : Nat → Json → Bool
  | 0, _ => true
  | _, .null => true
  | fuel + 1, .arr xs => xs.any (hasNull fuel)
  | fuel + 1, .obj kvs => kvs.toList.any fun (_, v) => hasNull fuel v
  | _, _ => false

/-- A `MIXED` part holds a `null` outside `nullableUnitKeys true`. -/
def partHasStrayNull (p : Json) : Bool :=
  match p with
  | .obj kvs => kvs.toList.any fun (k, v) =>
    if v == .null then !(nullableUnitKeys true).contains k else hasNull 257 v
  | v => hasNull 257 v

/-- A unit holds a `null` outside `nullableUnitKeys false`, or one of its `MIXED` parts does. -/
def unitHasStrayNull (u : Json) : Bool :=
  match u with
  | .obj kvs => kvs.toList.any fun (k, v) =>
    if v == .null then !(nullableUnitKeys false).contains k
    else match k, v with
      | "parts", .arr ps => ps.any partHasStrayNull
      | _, _ => hasNull 257 v
  | v => hasNull 257 v

/-- A readings candidate's absent content is written `null` by the @1 pilot loader. The readings route reads it
as pending. Other nulls in a reading set still belong to Python's JSON path. -/
def readingSetHasStrayNull (set : Json) : Bool :=
  match set with
  | .obj kvs => kvs.toList.any fun (k, v) =>
    if k == "readings" then match v with
      | .arr rs => rs.any fun r => match r with
        | .obj fields => fields.toList.any fun (key, value) =>
            if key == "content" && value == .null then false else hasNull 257 value
        | other => hasNull 257 other
      | other => hasNull 257 other
    else hasNull 257 v
  | v => hasNull 257 v

def strayNull (front : Json) : Option String :=
  match front with
  | .obj kvs => kvs.toList.findSome? fun (k, v) =>
    let stray := match k, v with
      | "units", .arr us => us.any unitHasStrayNull
      | "reading_sets", .arr sets => sets.any readingSetHasStrayNull
      | _, _ => hasNull 257 v
    if stray then some k else none
  | v => if hasNull 257 v then some "front matter" else none

/-- Cap nesting before `Lean.Json.parse`, whose recursive parser can overflow the process
stack on an untrusted document string. Quotes and escapes do not change nesting. -/
def frontDepth (front : String) : Except String Unit := do
  let mut depth : Nat := 0
  let mut quoted := false
  let mut escaped := false
  for c in front.toList do
    if quoted then
      if escaped then escaped := false
      else if c == '\\' then escaped := true
      else if c == '"' then quoted := false
    else if c == '"' then quoted := true
    else if c == '[' || c == '{' then
      depth := depth + 1
      if depth > 256 then throw "ResourceLimit: JSON depth exceeds 256"
    else if c == ']' || c == '}' then
      depth := depth - 1

def frontJson (front : String) : Except String Json := do
  let _ ← frontDepth front
  match Json.parse front with
  | .ok j =>
    match foreignLexeme false (front.length + 1) false front.toList with
    | some .number => throw (unavailable
        "front matter outside the document mode's JSON reader: a number other than a natural at most 2^53-1")
    | some _ => throw (unavailable "front matter outside the document mode's JSON reader: lexer fuel")
    | none => pure ()
    if let some key := strayNull j then
      throw (unavailable ("front matter outside the document mode's JSON reader: null in " ++ key))
    pure j
  | .error e =>
    let text := Loader.frontJsonError e
    if text == "invalid JSON front matter" && pythonMayRead front then
      .error (unavailable "front matter outside the restricted JSON reader (Python-only JSON values)")
    else .error text

/-- `_no_lone_surrogate`, which Python's loader runs right after `_split`: a lone surrogate escape anywhere in the
front matter is the JSON boundary's diagnostic. -/
def noLoneSurrogate (front : String) : Except String Unit :=
  match foreignLexeme true (front.length + 1) false front.toList with
  | some .surrogate => throw loneSurrogate
  | some _ => throw (unavailable "front matter outside the document mode's JSON reader: lexer fuel")
  | none => pure ()

/-- `_split` with `is_discourse_text` first: the metadata keys, the couplings and completions gates, then the
body. -/
def split (t : String) : Except String Loader.Split := do
  let (front, body) ← Loader.frontText t
  let fm ← frontJson front
  if fm.getObjValD "format" == .str "ve-document@2" then
    throw (unavailable "a ve-document@2 document is admitted by the discourse route")
  -- RD-8: `senses` is a key `_split` allows; the senses route reads those documents' English fences.
  if (fm.getObjVal? "senses").isOk then
    throw (unavailable "a document with senses is read by the Lean senses route")
  let _ ← Loader.checkMetadata Loader.documentMetadata fm
  let listed := listedProfiles (fm.getObjValD "environment")
  if (fm.getObjVal? "couplings").isOk && !(listed.contains "rights@0" || listed.contains "readings@1") then
    throw "UnsupportedProfile: rights@0 is required for couplings"
  if (fm.getObjVal? "completions").isOk && !listed.contains "norm-defaults@0" then
    throw "UnsupportedProfile: norm-defaults@0 is required for completions"
  let (source, fences) ← Loader.bodyOf (Loader.linesOf body) (python := true)
  noLoneSurrogate front
  pure ⟨fm, source, fences⟩

/-! ## The environment -/

/-- The block routes' document with no norms and no units, as Python's `coverage` sends it. -/
def emptySource : Json := Json.mkObj [("norms", Json.arr #[]), ("units", Json.arr #[])]

/-- The @1 document identity includes authored nulls, while certificate identities do not. -/
def documentId (doc : Loader.Split) : Except String String := do
  let format ← stringField doc.front "format"
  let payload := Json.mkObj [("metadata", Loader.identityMetadata doc.front),
    ("source", .str doc.source), ("fences", Json.mkObj (doc.fences.map fun (u, t) => (u, Json.str t)))]
  match VE.CertificateWire.documentDigest (format ++ "\n") payload with
  | .ok digest => pure digest
  | .error e => throw (if e.startsWith "ResourceLimit" then e else
      unavailable "document identity contains a JSON number outside the document mode")

/-- The checked environment of a document and what its checks read: the environment as written (its profiles
and identity bind every meaning id), its typing envelope (a composed block's profile and fields replaced by the
words they declare, `Standalone.typingReduced`) and route vocabulary. -/
structure Env where
  json : Json
  checked : Standalone.Validated
  rv : VE.Route.Wire.RouteVocabulary
  profiles : List String
  envId : String
  block : Block

def Env.data (E : Env) : Bool := E.profiles.contains "data@0"

/-! ## Python's names for the decoders' rejections

The verdict on an environment, a formula or a claim graph is always the mode's decoders'. Several of them read
their input with Lean's generic accessors, whose texts (`object expected`, `String expected`, `array expected`,
`invalid indexed formula`, `invalid signature: p`) name neither the field, nor the value, nor the fault, where
`Environment` and `formula_from_data`, which answered before batch 16b, name all three (16b looprecheck1: DRI
rule 2(a)–(c), no name, location or specificity lost). After a decoder rejects, these walks go through the input
in Python's order and name the first fault they find with Python's text. A walk stops at the first step it does
not model and the decoder's own text stands; it never accepts anything. -/

/-- A step of a walk: `.error (some m)` is the first fault, as Python names it; `.error none` stops the walk. -/
abbrev Walk := Except (Option String)

def fault {α : Type} (m : String) : Walk α := .error (some m)
def stop {α : Type} : Walk α := .error none

def walked (w : Walk Unit) : Option String :=
  match w with
  | .error m => m
  | .ok () => none

/-- `require_fields` passes: an object with exactly these members. Its failure carries a `path` this mode's error
row cannot hold yet (batch 12's located decoders), so the walk stops there. -/
def exactly (j : Json) (names : List String) : Walk Unit := do
  let .obj kvs := j | stop
  let keys := kvs.toList.map Prod.fst
  unless keys.length == names.eraseDups.length && names.all keys.contains do stop

def pyR (s : String) : String := TypingDiagnostic.pyRepr s

/-- The frozen v0 envelope is chosen for an unrecognised string language on a plain document (Python
`Environment._decode`). Report its field-set fault before considering the modern route's language gate.
The expected names come from the route envelope table, with its one v0 spelling change. -/
def legacyEnvelopeFault (environment : Json) : Option String :=
  let expected := (envelopeKeys .none).map fun k => if k == "profiles" then "profile" else k
  match environment with
  | .obj kvs =>
    let keys := kvs.toList.map Prod.fst
    let missing := (expected.filter (!keys.contains ·)).mergeSort (fun a b => decide (a ≤ b))
    let unknown := (keys.filter (!expected.contains ·)).mergeSort (fun a b => decide (a ≤ b))
    if missing.isEmpty && unknown.isEmpty then none else
      let renderList := fun (xs : List String) => "[" ++ ", ".intercalate (xs.map pyR) ++ "]"
      some s!"Incorrect fields (missing={renderList missing}, unknown={renderList unknown})"
  | _ => some "Expected a JSON object"

/-- `_description`. -/
def describedBy (j : Json) : Walk Unit :=
  match j with
  | .str s => if s.isEmpty then fault "Descriptions must be nonempty Unicode strings" else pure ()
  | _ => fault "Descriptions must be nonempty Unicode strings"

/-- `_verbalisation`. -/
def verbalisedBy (j : Json) : Walk Unit :=
  match j with
  | .str s =>
    if s.isEmpty then fault "Verbalisations must be nonempty strings"
    else if s.length > 256 then fault "ResourceLimit: Verbalisation exceeds 256 characters" else pure ()
  | _ => fault "Verbalisations must be nonempty strings"

/-- `formula_from_data`'s diagnostic for a formula a decoder rejected: Python's AST decoder
(`Reports.Preflight.decoderFault`, the one Lean walk of `_Decoder`), then its type checker
(`TypingDiagnostic.diagnose`). -/
def formulaFault (profiles : List String) (vocabulary ast : Json) : Option String :=
  (VE.Reports.Preflight.decoderFault ast).orElse fun _ => TypingDiagnostic.diagnose profiles vocabulary [ast]

/-- `Environment` for the plain (no block) `ve.core@0.2` envelope of an owned profile, in its order: the envelope,
the vocabulary's three tables, the declaration names, the sorts, predicates and constants, then the definition
bodies (`compile_definitions`: arguments, then `_Decoder`). Tables are walked in Lean's key order, which is
Python's for one fault. -/
def vocabularyFault (environment : Json) : Option String := walked do
  let profiles := listedProfiles environment
  unless blockOf profiles == .none && !profiles.contains "nary@0" && !profiles.contains "order@0" do stop
  -- The envelope: its fields, language, profile family and revision, as `Gate.decodeEnvelope` and Python agree.
  exactly environment (envelopeKeys .none)
  unless (VE.Route.Gate.decodeEnvelope environment).isOk do stop
  let vocabulary := environment.getObjValD "vocabulary"
  exactly vocabulary ["sorts", "predicates", "constants"]
  let table := fun (kind : String) => match vocabulary.getObjValD kind with
    | .obj kvs => (pure kvs.toList : Walk _)
    | _ => fault s!"{kind} must be an object"
  let sorts ← table "sorts"
  let predicates ← table "predicates"
  let constants ← table "constants"
  if sorts.length > 32 || predicates.length > 256 then stop
  let mut seen : List String := []
  for (name, _) in sorts ++ predicates ++ constants do
    if name.length > 64 then fault "ResourceLimit: Identifier exceeds 64 ASCII bytes"
    unless VE.Surface.identifier name do fault s!"Invalid ASCII identifier: {pyR name}"
    if seen.contains name then fault s!"DuplicateDeclaration: Symbol {pyR name} is declared in multiple categories"
    if VE.Surface.reserved.contains name || VE.Surface.generatedName name then
      fault s!"DuplicateDeclaration: Schema identifier {pyR name} is reserved"
    seen := name :: seen
  let sortNames := sorts.map Prod.fst
  let present := fun (entry : Json) (key : String) => (entry.getObjVal? key).isOk
  for (_, entry) in sorts do
    exactly entry (["description"] ++ if present entry "verbalisation" then ["verbalisation"] else [])
    if let .ok words := entry.getObjVal? "verbalisation" then
      exactly words ["singular", "plural"]
      verbalisedBy (words.getObjValD "singular")
      verbalisedBy (words.getObjValD "plural")
    describedBy (entry.getObjValD "description")
  let data := profiles.contains "data@0"
  let definitions := profiles.contains "definitions@0"
  for (name, entry) in predicates do
    if present entry "functional" || present entry "total" || present entry "regulated" ||
        present entry "argument_units" then stop
    let defined := definitions && present entry "defined"
    exactly entry (["arguments", "description"] ++ (if defined then ["defined"] else []) ++
      (["verbalisation", "negative_verbalisation"].filter (present entry)))
    let arity := "Predicate arguments must be an array of one to 2 sort identifiers"
    let arguments := match entry.getObjValD "arguments" with
      | .arr xs => xs.toList
      | _ => []
    unless 1 ≤ arguments.length && arguments.length ≤ 2 do fault arity
    for sort in arguments do
      match sort with
      | .str s => unless sortNames.contains s || (data && s == VE.Route.Background.stringSort) do
          fault s!"UnknownSymbol: Undeclared predicate argument sort: {pyR s}"
      | other => fault s!"UnknownSymbol: Undeclared predicate argument sort: {TypingDiagnostic.pyValue other}"
    for key in ["verbalisation", "negative_verbalisation"] do
      if let .ok words := entry.getObjVal? key then verbalisedBy words
    if defined then
      let payload := entry.getObjValD "defined"
      exactly payload ["arguments", "body"]
      unless payload.getObjValD "arguments" == .arr arguments.toArray do
        fault s!"Definition {pyR name} arguments differ from its declaration"
    describedBy (entry.getObjValD "description")
  for (_, entry) in constants do
    let literal := entry.getObjValD "sort" == .str VE.Route.Background.stringSort
    exactly entry (["sort"] ++ (if !literal || present entry "description" then ["description"] else []) ++
      (if present entry "verbalisation" then ["verbalisation"] else []))
    match entry.getObjValD "sort" with
    | .str s => unless sortNames.contains s || s == VE.Route.Background.stringSort do
        fault s!"UnknownSymbol: Undeclared constant sort: {pyR s}"
    | other => fault s!"UnknownSymbol: Undeclared constant sort: {TypingDiagnostic.pyValue other}"
    if present entry "description" then describedBy (entry.getObjValD "description")
    if let .ok words := entry.getObjVal? "verbalisation" then verbalisedBy words
  if (constants.filter fun (_, e) => e.getObjValD "sort" == .str VE.Route.Background.stringSort).length > 64 then
    stop
  -- `_compile_python`'s structural loop: each body is decoded, in declaration order, before any is typed.
  for (_, entry) in predicates do
    if definitions then
      if let .ok payload := entry.getObjVal? "defined" then
        if let some m := VE.Reports.Preflight.decoderFault (payload.getObjValD "body") then fault m
        -- Python then rejects reachability, and orders and types the bodies: the decoder's text stands.

/-- The decoders of `environmentOf`, after its gates. -/
def decodedEnvironment (environment : Json) (block : Block) : Except String Env := do
  -- A composed block's route decodes the environment first, as Python's `Environment` routes it.
  match block with
  | .alternatives => let _ ← VE.Alternatives.Wire.decodeAltSource environment (Json.arr #[]) .null .environment
  | .risk => let _ ← VE.Risk.Wire.decodeRiskSource environment emptySource
  | .none => pure ()
  let profiles := listedProfiles environment
  let defaults := profiles.contains "norm-defaults@0"
  let readings := profiles.contains "readings@1"
  if readings then
    let _ ← VE.Readings.Wire.decodeEnvironment environment
  if defaults then
    let _ ← VE.NormDefaults.Wire.decodeEnvironmentU
      (if readings then lowerReadings environment else environment)
  -- The typing envelope: risk's declarations replaced by the words they declare, then the alternatives words.
  let typing ← if block == .risk then Standalone.riskReduced environment
    else if defaults then
      VE.NormDefaults.Wire.placeholderJson (if readings then lowerReadings environment else environment)
    else pure environment
  let checked ← Standalone.validated typing (typing := block != .none)
  let e := checked.envelope
  unless e.family == .fol do
    throw (unavailable s!"document checks on the {e.family.name} family need its Lean route")
  let predicates ← fields (← e.vocabulary.getObjVal? "predicates")
  -- Without a block, Python admits a graph over regulated predicates on the norms route; a block route admits
  -- its own graph, and both build the (empty) norm document of the declarations alone.
  if block == .none && !defaults && e.profiles.contains "norms@0" &&
      predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
    throw (unavailable "regulated predicates need the Lean norms route")
  let rv ← VE.Route.Run.decodeRouteVocabulary e
  let profiles ← VE.Route.Gate.profilesOf environment
  pure ⟨environment, checked, rv, profiles, ← Standalone.environmentIdOf profiles environment, block⟩

/-- `base_environment`, the profile gate (before any decoding, so an unowned profile is never rejected by a
decoder that does not read it), then the envelope decoder. -/
def environmentOf (environment : Json) : Except String Env := do
  match environment.getObjValD "profiles" with
  | .arr ps => if ps.contains (.str VE.Discourse.discourseProfile) then
      throw "UnsupportedProfile: ve.discourse@1 requires ve-document@2"
  | _ => pure ()
  if Standalone.isLegacy environment then
    throw (unavailable "a document over a ve.core@0 or ve.core@0.1 environment needs its legacy route")
  let listed := listedProfiles environment
  if let some p := listed.find? (!ownedProfiles.contains ·) then
    throw (unavailable s!"document checks under {p} need its Lean profile route")
  if listed.contains "readings@1" && !listed.contains "norm-defaults@0" then
    throw (unavailable "readings@1 documents need the Lean readings route")
  let block := blockOf listed
  if listed.contains "norm-defaults@0" && block != .none then
    throw (unavailable "norm-defaults with alternatives or risk needs its composed Lean route")
  if let some key := ["unit_schema", "units"].find? (fun k => (environment.getObjVal? k).isOk) then
    throw (unavailable s!"the environment block {key} needs its Lean route's decoder")
  if block == .none then
    if let .str language := environment.getObjValD "language" then
      if language != VE.Route.Gate.language then
        if let some message := legacyEnvelopeFault environment then throw message
        throw "UnsupportedProfile: Unsupported language, semantic profile, or specification revision"
  let keys := ((fields environment).toOption.getD []).map Prod.fst
  if let some k := keys.find? (!(envelopeKeys block).contains ·) then
    throw (unavailable s!"the environment block {k} needs its Lean route's decoder")
  match decodedEnvironment environment block with
  | .ok E => pure E
  | .error m => throw (if m.startsWith "CheckerUnavailable" then m else (vocabularyFault environment).getD m)

/-- `formula_from_data` over the document's environment: the `check` mode's typed decoder, its rejection named as
Python names it (`formulaFault`: its AST decoder, then its type checker). -/
def formulaCheck (E : Env) (ast : Json) : Except String Unit :=
  match Standalone.decodeTyped E.checked ast true with
  | .ok () => .ok ()
  | .error message => .error ((formulaFault E.checked.envelope.profiles E.checked.envelope.vocabulary ast).getD message)

/-- A checked formula and its `meaning_id`. -/
def formulaOf (E : Env) (ast : Json) : Except String (VE.Formula × String) := do
  formulaCheck E ast
  let f ← VE.Route.Wire.decodeClosed E.rv.environment ast E.data
  pure (f, ← VE.Route.Wire.meaningId E.profiles E.envId (VE.Route.Wire.encodeFormula f))

/-! ## Units -/

inductive UnitContent
  | formula (value : VE.Formula)
  | norm (value : VE.Norms.Node)

def UnitContent.json : UnitContent → Json
  | .formula f => VE.Route.Wire.encodeFormula f
  | .norm n => VE.Alternatives.Wire.encodeNode n

structure SourceUnit where
  id : String
  span : Nat × Nat
  kind : Json
  meaning : Json
  support : String
  status : String
  parent : Option String
  content : Option UnitContent := none
  meaningId : Option String := none
  explicit : Option String := none

/-! The answer's units are typed (`RowUnit`): each field is rendered from a decoded value, so the response schema
names every field's domain and the encoder's theorems (`ResponseShape.Encoders.Document.unit_fits`) prove the
rendered rows fit it. The value lists are `Loader`'s (`#guard`s below). -/

/-- `Loader.supports`. -/
inductive Support | assumption | certificate | observation | calculation | statistical | testimony | adapter | none
  deriving DecidableEq, Repr

def Support.all : List Support :=
  [.assumption, .certificate, .observation, .calculation, .statistical, .testimony, .adapter, .none]

def Support.name : Support → String
  | .assumption => "assumption" | .certificate => "certificate" | .observation => "observation"
  | .calculation => "calculation" | .statistical => "statistical" | .testimony => "testimony"
  | .adapter => "adapter" | .none => "none"

def Support.ofName? (s : String) : Option Support := Support.all.find? (·.name == s)

#guard Support.all.map Support.name == Loader.supports

/-- `Loader.statuses`: a unit's W2 status. -/
inductive UnitStatus | checked | opened | labelled | unformalised
  deriving DecidableEq, Repr

def UnitStatus.all : List UnitStatus := [.checked, .opened, .labelled, .unformalised]

def UnitStatus.name : UnitStatus → String
  | .checked => "CHECKED" | .opened => "OPEN" | .labelled => "LABELLED" | .unformalised => "UNFORMALISED"

def UnitStatus.ofName? (s : String) : Option UnitStatus := UnitStatus.all.find? (·.name == s)

#guard UnitStatus.all.map UnitStatus.name == Loader.statuses

/-- A meaning `Loader.meaningStatus` accepts: `specified`, or one member `contextual`, `open` or `unformalised`. -/
inductive Meaning
  | specified
  | contextual (detail : String)
  | openTerms (names : List String)
  | unformalised (reason : String)

def Meaning.json : Meaning → Json
  | .specified => .str "specified"
  | .contextual d => Json.mkObj [("contextual", .str d)]
  | .openTerms names => Json.mkObj [("open", Json.arr (names.map Json.str).toArray)]
  | .unformalised r => Json.mkObj [("unformalised", .str r)]

/-- The meaning `Loader.meaningStatus` accepted, typed: `Meaning.json` of it is the meaning as written. -/
def Meaning.ofJson? (j : Json) : Option Meaning :=
  match j with
  | .str "specified" => some .specified
  | .obj _ => match (fields j).toOption with
    | some [("contextual", .str d)] => some (.contextual d)
    | some [("open", .arr xs)] => (xs.toList.mapM fun (x : Json) => x.getStr?.toOption).map .openTerms
    | some [("unformalised", .str r)] => some (.unformalised r)
    | _ => none
  | _ => none

/-- A unit of the answer, typed. -/
structure RowUnit where
  id : String
  span : Nat × Nat
  kind : VE.Route.Admission.Kind
  meaning : Meaning
  support : Support
  status : UnitStatus
  parent : Option String
  content : Option UnitContent
  meaningId : Option String

def kindName (kind : Json) : String :=
  match kind with
  | .str s => s
  | .arr xs => (xs[0]?.getD Json.null).getStr?.toOption.getD ""
  | _ => ""

/-- `_content` for the owned profiles: the unit's checked formula and `meaning_id`, or the reason it has none
here. -/
def contentOf (E : Env) (fences : List (String × String)) (lexicon : Option Json)
    (u : Json) (id : String) (content : Json) :
    Except String (UnitContent × String) := do
  let one := "unit content must bind one formula or norm"
  let (key, value) ← match content with
    | .obj kvs => match kvs.toList with
      | [kv] => pure kv
      | _ => throw one
    | _ => throw one
  if key == "quantity" then throw "UnsupportedProfile: quantity content requires ve-units@1"
  if key == "norm" then
    if E.profiles.contains "norm-defaults@0" then
      let node ← (VE.Norms.Wire.decodeNorm content).mapError fun e =>
        if e == "Natural number expected" then
          unavailable "a malformed norm formula is outside this document decoder"
        else if e == "object expected" then
          "Expected a JSON object"
        else e
      let encoded := VE.Alternatives.Wire.encodeNode node
      return (.norm node, ← VE.Route.Wire.meaningId E.profiles E.envId encoded)
    if E.profiles.contains "norms@0" then throw (unavailable "norm content needs the Lean norms route")
    throw "UnsupportedProfile: norms@0 is required"
  if ["right", "right_lines", "limitation", "bar"].contains key then throw "UnsupportedProfile: rights@0 is required"
  if key == "ast" then
    let (f, mid) ← formulaOf E value
    return (.formula f, mid)
  unless key == "fence" && value == .str id do throw "unit fence must match its id"
  unless (fences.map Prod.fst).contains id do throw "missing VE fence"
  unless u.getObjValD "surface" == .str "english" || u.getObjValD "surface" == .str "strict" do
    throw "fenced content needs english or strict surface"
  if u.getObjValD "surface" == .str "strict" then
    let source := ((fences.lookup id).getD "").trim
    let parsed ← (VE.Service.Standalone.parseCase (Json.mkObj
      [("id", .str id), ("environment", E.checked.decodable), ("source", .str source)])).mapError
        (fun _ => unavailable "the strict fence needs a surface parser outside this document envelope")
    let ast ← (← parsed.getObjVal? "ast").getArr?
    unless ast.size == 1 do throw "each VE fence must contain exactly one sentence"
    let (f, mid) ← formulaOf E (ast[0]!)
    return (.formula f, mid)
  if let some lexicon := lexicon then
    let parsed ← VE.EnglishGrammar.Run.readCase (Json.mkObj
      [("id", .str id), ("environment", E.json), ("lexicon", lexicon),
       ("source", .str ((fences.lookup id).getD "")), ("mode", .str "authoring"), ("cap", toJson (2 : Nat))])
    let result ← parsed.getObjVal? "result"
    unless result.getObjValD "status" == .str "one" do
      throw ((result.getObjValD "class").getStr?.toOption.getD "VEError" ++ ": " ++
        (result.getObjValD "text").getStr?.toOption.getD "English fence was not read")
    let ast ← (← result.getObjVal? "ast").getArr?
    unless ast.size == 1 do throw "each VE fence must contain exactly one sentence"
    let (f, mid) ← formulaOf E (ast[0]!)
    return (.formula f, mid)
  throw (unavailable "fenced English or strict content needs the Lean surface parser")

/-- `load_document`'s checks of one unit at byte `cursor`, in Python's order. -/
def sourceUnit (E : Env) (source : String) (fences : List (String × String)) (lexicon : Option Json)
    (openNames : List String)
    (cursor : Nat) (seen parents : List String) (parent : Option String) (u : Json) : Except String SourceUnit := do
  let keys ← (fields u).mapError (fun _ => "invalid unit schema")
  let names := keys.map Prod.fst
  let required := ["id", "span", "kind", "meaning", "support"]
  unless required.all names.contains &&
      names.all (required ++ ["content", "surface", "meaning_id", "status"]).contains do
    throw "invalid unit schema"
  let id := (u.getObjValD "id").getStr?.toOption.getD ""
  unless token id && !seen.contains id && !parents.contains id do
    throw "duplicate or invalid unit id"
  let (a, b) ← (Loader.spanOf (u.getObjValD "span")).mapError
    (fun _ => "unit spans must partition every source byte in order")
  unless a == cursor && cursor < b && b ≤ source.utf8ByteSize do
    throw "unit spans must partition every source byte in order"
  if Loader.cutsCharacter source a b then throw "unit span cuts a UTF-8 character"
  let kind := u.getObjValD "kind"
  let _ ← VE.Route.Admission.decodeKind 16 kind
  let meaning := u.getObjValD "meaning"
  let meaningStatus ← Loader.meaningStatus openNames meaning (python := true)
  let support := (u.getObjValD "support").getStr?.toOption.getD ""
  unless Loader.supports.contains support do throw "invalid support"
  let compiled ← match u.getObjVal? "content" with
    | .ok .null => pure none
    | .ok content => some <$> contentOf E fences lexicon u id content
    | .error _ => pure none
  if let some (.norm _) := compiled.map Prod.fst then
    unless kind == .str "norm" do throw "norm content requires a norm or quoted kind"
  if let .arr xs := kind then
    if xs[0]? == some (.str "unformalised") && meaning != Json.mkObj [("unformalised", xs[1]?.getD .null)] then
      throw s!"InvalidInput: unformalised kind reason does not match meaning of {id}"
  if meaningStatus == "unformalised" && compiled.isSome then
    throw "unformalised unit cannot assert content"
  if let (.ok stated, some (_, mid)) := (u.getObjVal? "meaning_id", compiled) then
    unless stated == .str mid do throw "unit meaning id does not match content"
  let explicit ← match u.getObjVal? "status" with
    | .ok (.str s) => if Loader.statuses.contains s then pure (some s) else throw "invalid unit status"
    | .ok .null => pure none
    | .ok _ => throw "invalid unit status"
    | .error _ => pure none
  pure { id, span := (a, b), kind, meaning, support, parent, explicit,
         content := compiled.map Prod.fst, meaningId := compiled.map Prod.snd,
         status := Loader.w2Status compiled.isSome meaningStatus }

/-- `_parts` interleaved with the unit loop, as Python's generator runs: a `MIXED` part is checked against its
parent's cursor, then compiled, before the next part is read; the parent's end is checked after its last part. -/
def unitsOf (E : Env) (source : String) (fences : List (String × String)) (lexicon : Option Json)
    (openNames : List String)
    (raw : List Json) : Except String (List SourceUnit) := do
  let parents ← Loader.mixedParents raw
  let mut units : Array SourceUnit := #[]
  let mut cursor := 0
  for u in raw do
    match ← Loader.mixedOf u with
    | none =>
      let unit ← sourceUnit E source fences lexicon openNames cursor (units.toList.map (·.id)) parents none u
      units := units.push unit
      cursor := unit.span.2
    | some ((a, b), parts) =>
      let parent := (u.getObjValD "id").getStr?.toOption
      let mut inner := a
      for p in parts do
        Loader.partOk inner p
        let unit ← sourceUnit E source fences lexicon openNames cursor (units.toList.map (·.id)) parents parent p
        units := units.push unit
        cursor := unit.span.2
        inner := unit.span.2
      unless inner == b do throw Loader.partitionText
  unless cursor == source.utf8ByteSize do throw "unit spans do not partition all source bytes"
  pure units.toList

/-! ## Coverage -/

def addCount (xs : List (String × Nat)) (name : String) (n : Nat) : List (String × Nat) :=
  if xs.any (·.1 == name) then xs.map (fun (k, v) => (k, if k == name then v + n else v))
  else xs ++ [(name, n)]

def counts (units : List SourceUnit) (key : SourceUnit → String) : List (String × Nat) :=
  units.foldl (fun acc u => addCount acc (key u) (u.span.2 - u.span.1)) []

def reasons (units : List SourceUnit) : List (String × Nat) :=
  units.foldl (fun acc u => match u.meaning.getObjVal? "unformalised" with
    | .ok (.str reason) => addCount acc reason 1
    | _ => acc) []

def countJson (xs : List (String × Nat)) : Json :=
  Json.mkObj (xs.map fun (k, v) => (k, toJson v))

/-- The labels of the graph's nodes, as `coverage` reads them: string labels of object nodes. -/
def graphLabels (front : Json) : List String :=
  match (front.getObjValD "graph").getObjValD "nodes" with
  | .arr xs => xs.toList.filterMap fun n => match n with
    | .obj _ => (n.getObjValD "label").getStr?.toOption
    | _ => none
  | _ => []

/-- `coverage`'s residual counts of the wrapper itself. -/
def residual (front : Json) (units : List SourceUnit) : List (String × Nat) :=
  let count (key : String) := match front.getObjValD key with
    | .arr xs => xs.toList
    | _ => []
  [("open_terms", (count "open_terms").length),
   ("assumptions", (units.filter (·.support == "assumption")).length),
   ("bridge_leaves", ((graphLabels front).filter (·.startsWith "bridge:accepts(")).length),
   ("unresolved_reading_sets", ((count "reading_sets").filter (·.getObjValD "status" == .str "open")).length)]

/-- A unit of the answer. A unit with content carries its checked formula and `meaning_id`, so a caller builds its
document from them and never recomputes an identity (docs/LEAN-FIRST-PLAN.md rules 2 and 5, batch 16b). -/
def unitJson (u : RowUnit) : Json :=
  Json.mkObj ([("id", .str u.id), ("span", toJson [u.span.1, u.span.2]),
    ("kind", VE.Route.Admission.renderKind u.kind), ("meaning", u.meaning.json), ("support", .str u.support.name),
    ("status", .str u.status.name)] ++
    (u.parent.toList.map fun p => ("parent_id", .str p)) ++
    (u.content.toList.map fun f => ("content", f.json)) ++
    (u.meaningId.toList.map fun m => ("meaning_id", .str m)))

/-- The typed answer unit of a checked unit. Its kind and meaning were decoded by `sourceUnit` (`decodeKind 16`,
`Loader.meaningStatus`) and its support and status are `Loader`'s, so no case refuses; one that did would be
`CheckerUnavailable`, never another row. `decodeKind_render` and `Meaning.ofJson?` make the rendered kind and
meaning the ones written, which the receiver also checks (`_bind_document_answer`). -/
def rowOf (u : SourceUnit) : Except String RowUnit := do
  let untyped := unavailable s!"unit {u.id} outside the typed answer"
  let kind ← (VE.Route.Admission.decodeKind 16 u.kind).mapError fun _ => untyped
  let some meaning := Meaning.ofJson? u.meaning | throw untyped
  let some support := Support.ofName? u.support | throw untyped
  let some status := UnitStatus.ofName? u.status | throw untyped
  pure { id := u.id, span := u.span, kind, meaning, support, status, parent := u.parent,
         content := u.content, meaningId := u.meaningId }

/-- A composed block's coverage line, as its route computes it (`Alternatives.Wire.coverage` over the block's
source and the document's units and narrowings). -/
structure BlockCoverage where
  doc : VE.Alternatives.AltDoc
  environment : Json
  units : Json
  narrowings : Json

def BlockCoverage.line (b : BlockCoverage) : Json :=
  VE.Alternatives.Wire.coverage b.doc b.environment b.units b.narrowings

/-- The line's residual counts. -/
def BlockCoverage.residual (b : BlockCoverage) : List (String × Nat) :=
  match b.line.getObjValD "residual" with
  | .obj kvs => kvs.toList.map fun (k, v) => (k, v.getNat?.toOption.getD 0)
  | _ => []

/-- The units as Python's `coverage` hands them to the block route (`coverage_units`): each unit's id, kind,
support and checked content. -/
def coverageUnits (units : List SourceUnit) : Json :=
  Json.arr (units.map fun u => Json.mkObj [("id", .str u.id), ("kind", u.kind), ("support", .str u.support),
    ("content", match u.content with
      | some f => f.json
      | none => .null)]).toArray

/-- `coverage`'s block line (`alt-elaborate` or `risk-elaborate` with `coverage_units`, the call Python relays):
the alternatives route's `Wire.coverage` over the block's source with no norms. -/
def blockCoverage (E : Env) (front : Json) (units : List SourceUnit) : Except String (Option BlockCoverage) := do
  let A ← match E.block with
    | .none => return none
    | .alternatives => do
      let src ← VE.Alternatives.Replay.sourceOf (Json.mkObj [("environment", E.json), ("norms", Json.arr #[])])
      pure src.A
    | .risk => do
      let src ← VE.Risk.Wire.decodeRiskSource E.json emptySource
      pure (VE.Risk.toAlt src.R)
  pure (some ⟨A, E.json, coverageUnits units, Loader.optionalList front "narrowings"⟩)

/-- The coverage object of `coverage(doc)`: the wrapper's tables and residual counts, then a composed block's line
and its counts (Python's `residual.update`). -/
def coverageJson (front : Json) (units : List SourceUnit) (sourceBytes : Nat) (block : Option BlockCoverage) :
    Json :=
  let rest := (residual front units).foldl (fun acc (k, v) => addCount acc k v)
    ((block.map (·.residual)).getD [])
  let tables := [("source_bytes", toJson sourceBytes), ("accounted_bytes", toJson sourceBytes),
    ("coverage_percent", toJson (100 : Nat)), ("bytes_by_kind", countJson (counts units (kindName ∘ SourceUnit.kind))),
    ("bytes_by_status", countJson (counts units SourceUnit.status)), ("unformalised_reasons", countJson (reasons units)),
    ("residual", countJson rest), ("residual_total", toJson ((rest.map Prod.snd).sum))]
  match block with
  | none => Json.mkObj tables
  | some b => Json.mkObj (tables ++ [("alternatives", b.line.getObjValD "alternatives")])

/-! ## The claim graph -/

/-- The graph's node labels as `_report` parses them: `parse_label` of an object node's label. -/
def parsedLabels (graph : Json) : List VE.Route.Admission.Label :=
  match graph.getObjValD "nodes" with
  | .arr xs => xs.toList.filterMap fun n => match n with
    | .obj _ => (n.getObjValD "label").getStr?.toOption.bind VE.Route.Admission.parseLabel
    | _ => none
  | _ => []

/-- The texts the admission route's formula decoders reject a node's formula with (`Bridge.decodeTerm`,
`decodeFormula`, `Route.Wire.decodeClosed` and Lean's accessors): they name no node, value or fault. -/
def formulaDecoderTexts : List String :=
  ["invalid indexed formula", "invalid indexed term", "ill-typed or unbound formula", "ill-typed or unbound conclusion",
   "ill-typed or unbound premise", "array expected", "String expected", "Natural number expected"]

/-- `_decode_node`'s formula, node by node in order, for a graph the admission route rejected with one of
`formulaDecoderTexts`: the first node formula Python's decoder or type checker rejects. A generated
(`background:`) node is typed by its generator's route, so the walk stops there. -/
def graphFault (E : Env) (nodes : List Json) : Option String := walked do
  for node in nodes do
    unless node matches .obj _ do stop
    if ((node.getObjValD "label").getStr?.toOption.getD "").startsWith "background:" then stop
    if let some m := formulaFault E.checked.envelope.profiles E.checked.envelope.vocabulary (node.getObjValD "ast") then
      fault m

/-- `_report`'s claim-graph part for the owned profiles: the reading checks of the graph's labels, W2 admission
(the route's `admission`), then `_check_narrowing_choices` over the admitted report's labels. -/
def admitGraph (E : Env) (front graph : Json) (units : List SourceUnit) (all active : List (FrontSet × List Bool))
    (openNames narrowings : List String) : Except String Unit := do
  let nodes := match graph.getObjValD "nodes" with
    | .arr xs => xs.toList
    | _ => []
  -- `_unresolved_norm_reading`: an active reading of kind `norm` (every reading here has content).
  let normReading := active.any fun (s, _) => s.readings.any fun (r, _) =>
    (((front.getObjValD "reading_sets").getArr?.toOption.getD #[]).toList.any fun j =>
      j.getObjValD "id" == .str s.id && j.getObjValD "version" == toJson s.version &&
      ((j.getObjValD "readings").getArr?.toOption.getD #[]).toList.any fun c =>
        c.getObjValD "id" == .str r && c.getObjValD "kind" == .str "norm")
  if normReading && nodes.any (fun n => ((n.getObjValD "label").getStr?.toOption.getD "").startsWith "layer:norms:") then
    throw "non-assertion norm reading admission needs an elaborator"
  for label in parsedLabels graph do
    if let .readings set version _ := label then
      match active.find? fun (s, _) => s.id == set && s.version == version with
      | none => throw "graph cites a stale or unknown reading set version"
      | some (_, kinds) => unless kinds.all id do throw "non-assertion reading admission needs an elaborator"
  let document := Loader.admissionObject (units.map fun u =>
      (u.id, u.span, u.kind, u.content.bind fun c => match c with
        | .formula f => some f | .norm _ => none)) active graph front openNames narrowings
  let document := if E.profiles.contains "norm-defaults@0" then
    let activeIds := active.map (·.1.unit)
    let rows := ((document.getObjValD "units").getArr?.toOption.getD #[]).toList.zip units |>.map fun (j, u) =>
      match u.content with
      | some (.norm n) => if activeIds.contains u.id then j else
          j.setObjVal! "content" (VE.Alternatives.Wire.encodeNode n)
      | _ => j
    document.setObjVal! "units" (Json.arr rows.toArray)
    else document
  let admitted := match E.block with
    -- The route's own admission case (its gates, such as the definitions deferral, then `runAdmit`), as
    -- Python's `admit_document` asks it.
    | .none => if E.profiles.contains "norm-defaults@0" then
        VE.NormDefaults.Run.runAdmission "admission"
          (if E.profiles.contains "readings@1" then lowerReadings E.json else E.json) document
      else VE.Route.Run.dispatch "admission" E.json E.checked.envelope
        (Json.mkObj [("kind", .str "admission"), ("document", document)])
    | .alternatives => VE.Alternatives.Run.runAdmission "admission" E.json document
    | .risk => VE.Risk.Run.runAdmission "admission" E.json document
  let answer ← match admitted with
    | .ok a => pure a
    | .error e =>
      if e.startsWith "UnsupportedProfile" then throw (unavailable ("claim graph: " ++ e))
      else if E.block == .none && formulaDecoderTexts.contains e then throw ((graphFault E nodes).getD e)
      else throw e
  let labels := (((answer.getObjValD "report").getObjValD "assumptions").getArr?.toOption.getD #[]).toList.filterMap
    fun a => (a.getObjValD "label").getStr?.toOption
  let parsed := labels.filterMap VE.Route.Admission.parseLabel
  let sets := ((front.getObjValD "narrowings").getArr?.toOption.getD #[]).toList
  for n in sets do
    let nid := (n.getObjValD "id").getStr?.toOption.getD ""
    unless labels.contains ("narrowing:" ++ nid) do continue
    let set := (n.getObjValD "set").getStr?.toOption.getD ""
    let version := (n.getObjValD "version").getNat?.toOption.getD 0
    let keeps := ((n.getObjValD "keeps").getArr?.toOption.getD #[]).toList
    let readings := match all.find? fun (s, _) => s.id == set && s.version == version with
      | some (s, _) => s.readings.map Prod.fst
      | none => []
    for label in parsed do
      if let .readings s v (some i) := label then
        if s == set && v == version then
          unless keeps.contains (.str (readings.getD i "")) do
            throw "reading choice conflicts with narrowing"

/-- The readings route admits and validates the candidate documents. This projection carries only the W2 wrapper's
set ids, active statuses and asserted candidate formulas. A norm or pending candidate contributes no W2 formula. -/
def readingsSets (E : Env) (front : Json) (units : List SourceUnit) : Except String (List (FrontSet × List Bool)) := do
  let rawSets ← match Loader.optionalList front "reading_sets" with
    | .arr xs => pure xs.toList
    | _ => throw "reading_sets must be a list"
  let w2Sets := rawSets.filter fun set =>
    match set.getObjValD "readings" with
    | .arr rs => rs.all fun r => r.getObjValD "content" == .null ||
        (r.getObjValD "content").getObjValD "norm" == .null &&
        (r.getObjValD "content").getObjValD "right" == .null &&
        (r.getObjValD "content").getObjValD "right_lines" == .null &&
        (r.getObjValD "content").getObjValD "limitation" == .null
    | _ => false
  let w2 ← Loader.compileSets E.rv E.profiles E.envId (units.map (·.id))
    (Json.arr w2Sets.toArray) (python := true) (formula := formulaCheck E)
    (modelRefused := some (unavailable "a distinguishing model the Lean model decoder refuses"))
  let unitJson := units.map fun u => Json.mkObj ([("id", .str u.id), ("kind", u.kind)] ++
    u.content.toList.map fun c => ("content", c.json))
  let document := Json.mkObj [("units", Json.arr unitJson.toArray),
    ("reading_sets", Loader.optionalList front "reading_sets")]
  let _ ← VE.Readings.Run.runCase (Json.mkObj [("id", .str "readings"),
    ("kind", .str "readings-validate"), ("environment", E.json), ("document", document)])
  rawSets.mapM fun setJson => do
    let set ← VE.Readings.Wire.decodeSet setJson
    if let some found := w2.find? fun (r, _) => r.id == set.id && r.version == set.version then
      return found
    let readings ← set.readings.mapM fun r => do
      let f ← if r.kind == some "asserted" && r.content != .null then
        VE.Route.Wire.decodeClosed E.rv.environment r.content E.data
      else pure VE.Formula.top
      pure (r.id, f)
    let kinds := set.readings.map fun r => r.kind == some "asserted" && r.content != .null
    pure (⟨set.id, set.unit, set.version, set.status, readings⟩, kinds)

/-! ## The case -/

/-- The checked document: its identities, its source and units, and what its coverage reads. -/
structure Checked where
  documentId : String
  sourceId : String
  source : String
  units : List SourceUnit
  rows : List RowUnit
  front : Json
  block : Option BlockCoverage

/-- `withGraph := false` is `load_document` alone: everything but `_report`'s claim-graph part (its reading checks, W2
admission and the narrowing choices), which `check_document` adds (batch 16b). -/
def check (text : String) (withGraph : Bool := true) (lexicon : Option Json := none) : Except String Checked := do
  let doc ← split text
  let front := doc.front
  if doc.source.isEmpty then throw "document source is empty"
  let environment := front.getObjValD "environment"
  unless environment matches .obj _ do throw "document needs an embedded environment"
  let E ← environmentOf environment
  if ["contexts", "assessments", "bridges", "scoped"].any (front.getObjVal? · |>.isOk) then
    throw "unknown document metadata"
  let openNames ← Loader.openTermNames E.rv (Loader.optionalList front "open_terms") (python := true)
    (data := E.data) (formula := some (formulaCheck E))
  let raw ← match front.getObjValD "units" with
    | .arr xs => if xs.isEmpty then throw "document needs units" else pure xs.toList
    | _ => throw "document needs units"
  let units ← unitsOf E doc.source doc.fences lexicon openNames raw
  let authored := raw.flatMap fun u => match u.getObjVal? "parts" with
    | .ok (.arr ps) => ps.toList
    | _ => [u]
  let used := authored.filterMap fun u =>
    let id := (u.getObjValD "id").getStr?.toOption
    if (u.getObjValD "content").getObjValD "fence" == .str (id.getD "") then id else none
  unless (doc.fences.map Prod.fst).all used.contains do throw "unbound VE fence"
  let unitIds := units.map (·.id)
  if E.profiles.contains "norm-defaults@0" then
    let normUnits := units.filterMap fun u => match u.content with
      | some (.norm n) => some (VE.Alternatives.Wire.encodeNode n)
      | _ => none
    let source ← VE.NormDefaults.Wire.decodeSourceU
      (if E.profiles.contains "readings@1" then lowerReadings E.json else E.json)
      (Json.arr normUnits.toArray)
    let block := (front.getObjVal? "completions").toOption.getD (Json.mkObj [])
    let _ ← VE.NormDefaults.Wire.validateCompletions source.U block unitIds
  let all ← if E.profiles.contains "readings@1" then readingsSets E front units else
    Loader.compileSets E.rv E.profiles E.envId unitIds (Loader.optionalList front "reading_sets")
      (python := true) (formula := formulaCheck E)
      (modelRefused := some (unavailable "a distinguishing model the Lean model decoder refuses"))
  let active := Loader.activeOf all
  let units := units.map fun u => { u with status := Loader.foldStatus active u.id u.status }
  if units.any (fun u => u.explicit.any (· != u.status)) then
    throw "unit status contradicts content, meaning, or active reading set"
  Loader.checkLemmas front
  for u in units do
    if u.kind == .str "asserted" && u.content.isNone && !(all.any (·.1.unit == u.id)) then
      throw "asserted unit needs content or a reading set"
  let narrowings ← Loader.narrowingIds (all.map fun (s, _) => (s.id, s.version, s.readings.map Prod.fst))
    unitIds (Loader.optionalList front "narrowings") (python := true)
  Loader.checkWeights front
  -- `_report`: the coverage (a block route's line may reject), then the claim graph.
  let block ← blockCoverage E front units
  if let .ok graph := front.getObjVal? "graph" then
    if withGraph then admitGraph E front graph units all active openNames narrowings
  pure ⟨← documentId doc, Loader.sourceId E.profiles doc.source,
    doc.source, units, ← units.mapM rowOf, front, block⟩

def encode (id : String) (c : Checked) : Json :=
  VE.Route.Wire.ok id [("document_id", .str c.documentId), ("source_id", .str c.sourceId),
    ("source", .str c.source), ("units", toJson (c.rows.map unitJson)),
    ("coverage", coverageJson c.front c.units c.source.utf8ByteSize c.block)]

/-- A case `{"id", "document"}`, with `"admit": false` for `load_document` alone. -/
def documentCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let text ← stringField j "document"
  let withGraph ← match j.getObjVal? "admit" with
    | .ok (.bool b) => pure b
    | .ok _ => throw "InvalidInput: admit must be a boolean"
    | .error _ => pure true
  let lexicon := (j.getObjVal? "lexicon").toOption
  pure (encode id (← check text withGraph lexicon))

def runCaseReported (j : Json) : Json := Standalone.reported documentCase j

end VE.Service.Document
