import VE.Json
import VE.Order.ProfileGate
import VE.CertificateWire
import VE.Order.Surface
import VE.Route.Run
import VE.Norms.Run
import VE.Service.EnglishRun
import VE.EnglishGrammar.Run
import VE.Service.Standalone
import VE.Service.Graph
import VE.Service.Readings
import VE.Service.Family
import VE.Service.FamilyBundle
import VE.Service.FamilyNorms
import VE.SoftNorms.Run
import VE.Rights.Run
import VE.SpeechActs.Run
import VE.Attribution.Run
import VE.Alternatives.Run
import VE.Risk.Run
import VE.Risk.Eval
import VE.Time.Document
import VE.NormDefaults.Run
import VE.Discourse.Run
import VE.Readings.Run
import VE.Service.Diagnose
import Std.Data.HashMap

/-! # `ve_service` protocol (docs/spec/SEMANTICS-MIGRATION-PLAN.md, stage 1)

Glue only: nothing here decides a verdict. A request line is

    {"id": string, "mode": string, "cases": [...], "budget"?: {"cases"?: n, "bytes"?: n}}

and its response line is `{"counts", "id", "mode", "results", "status": "ok"}`. Result
`i` is `{"digest", "index": i, "result"}`: `result` is the output of the existing runner
for the mode on case `i` (`runMode`, pinned per mode below) and `digest` is the SHA-256
of the case's text as split from the request (`caseDigest`), so the client can bind
every result to the case it sent. A decoded request that cannot be answered gets a
request error `{"digests", "error", "id", "mode", "status": "error"}`, bound like a
response: its nonce, its mode and the digests of its cases (`null` when its cases text
does not split into cases). Only a line whose envelope cannot be decoded gets the unbound
line error `{"error", "id", "status": "error"}`, which answers no request. Non-English cases are decoded by `VE.JsonInput.parseCases`, the one-shot
batch decoder; English and `risk-eval` use `Lean.Json.parse`, their one-shot runners' decoder.

Budgets are deterministic functions of the request: its size in bytes and its number
of cases, each capped by the service limits; exceeding one is `ResourceLimit`. Work
inside a runner is not budgeted here (the reference runners have no work budget).

The one state the service keeps is its table of environment handles
(docs/LEAN-FIRST-PLAN.md, F2, batch 2; `Handles` below): a request may register
environments (`"environments": {digest: environment}`, each key the SHA-256 of its value's
text), and a case may then name one by `environment_handle` in place of its `environment`.
The case is answered as the same case with that environment (`Handles.expand`); a handle
the table does not hold makes the request a bound `CheckerUnavailable` request error, which
the client answers by sending the environment again.

Trusted, as for the one-shot runners: the member splitter `objectMembers` and the
restricted decoder `VE.JsonInput`, which have no refinement theorem. -/
namespace VE.Service
open Lean

/-- Longest accepted request line, as the one-shot runners' input cap. -/
def maxLineBytes : Nat := 16777216
/-- Most cases in one request. -/
def maxCases : Nat := 4096

inductive Mode where
  | evaluate | checkCertificate | order | route | norms | english | englishRead | englishGrammar | englishCheck
  | environment | model | check | identity
  | parse | graph | readings | bundle | familyNorms
  | softNorms | rights | speechActs | reports | alternatives | risk | riskEval | quantity | normDefaults
  | discourse | readingsRoute | diagnose
  deriving DecidableEq, Repr

def Mode.name : Mode → String
  | .evaluate => "evaluate"
  | .checkCertificate => "check-certificate"
  | .order => "order"
  | .route => "route"
  | .norms => "norms"
  | .english => "english"
  | .englishRead => "english.read"
  | .englishGrammar => "english.grammar"
  | .englishCheck => "english.check"
  | .environment => "environment"
  | .model => "model"
  | .check => "check"
  | .identity => "identity"
  | .parse => "parse"
  | .graph => "graph"
  | .readings => "readings"
  | .bundle => "bundle"
  | .familyNorms => "family-norms"
  | .softNorms => "soft-norms"
  | .rights => "rights"
  | .speechActs => "speech-acts"
  | .reports => "reports"
  | .alternatives => "alternatives"
  | .risk => "risk"
  | .riskEval => "risk-eval"
  | .quantity => "quantity"
  | .normDefaults => "norm-defaults"
  | .discourse => "discourse"
  | .readingsRoute => "readings-route"
  | .diagnose => "diagnose"

def modes : List Mode := [.evaluate, .checkCertificate, .order, .route, .norms, .english,
  .englishRead, .englishGrammar, .englishCheck,
  .environment, .model, .check, .identity, .parse, .graph, .readings, .bundle, .familyNorms,
  .softNorms, .rights, .speechActs, .reports, .alternatives, .risk, .riskEval, .quantity, .normDefaults,
  .discourse, .readingsRoute, .diagnose]

def Mode.ofName? (name : String) : Option Mode := modes.find? (·.name == name)

/-- English cases are carried as their original JSON text in a `Json.str`, since
`Json.compress` changes number tokens such as `0.0` into `0`. The one-shot runner
must parse the original text itself. Its exit-2 failure becomes an error record. -/
def englishReported (j : Json) : Json :=
  let raw := match j with | .str text => text | _ => j.compress
  match VE.English.ServiceRun.run raw with
  | .ok result => result
  | .error message => Json.mkObj [("status", .str "error"), ("error", .str message)]

/-- One decoded case: the reported output of the existing runner for the mode.
`evaluate`, `check-certificate`, `order` and `route` are the `ve_conformance`
subcommands, `norms` is `ve_norms_route`, `english` is `VE/English/Run.lean`; the
statement-layer modes from `soft-norms` on are the per-case functions of the one-shot route
executables (docs/LEAN-FIRST-PLAN.md, batch 1), which leave the default build targets. -/
def runMode : Mode → Json → Json
  | .evaluate, j => VE.Order.runEvaluationCaseReported j
  | .checkCertificate, j => VE.CertificateWire.runCaseReported j
  | .order, j => VE.Order.Surface.runCaseReported j
  | .route, j => VE.Route.Run.runCaseReported j
  | .norms, j => VE.Norms.Run.runCaseReported j
  | .english, j => englishReported j
  | .englishRead, j => VE.EnglishGrammar.Run.readCaseReported j
  | .englishGrammar, j => VE.EnglishGrammar.Run.grammarCaseReported j
  | .englishCheck, j => VE.EnglishGrammar.Run.checkCaseReported j
  | .environment, j => Standalone.reported Standalone.environmentCase j
  | .model, j => Standalone.reported Standalone.modelCase j
  | .check, j => Standalone.reported Standalone.checkCase j
  | .identity, j => Standalone.reported Standalone.identityCase j
  | .parse, j => Standalone.reported Standalone.parseCase j
  | .graph, j => Standalone.reported Family.graphMode j
  | .readings, j => Standalone.reported Family.readingsMode j
  | .bundle, j => Standalone.reported FamilyBundle.bundleCase j
  | .familyNorms, j => FamilyNorms.runCaseReported j
  | .softNorms, j => VE.SoftNorms.Run.runCaseReported j
  | .rights, j => VE.Rights.Run.runCaseReported j
  | .speechActs, j => VE.SpeechActs.Run.runCaseReported j
  | .reports, j => VE.Reports.Run.runCaseReported j
  | .alternatives, j => VE.Alternatives.Run.runCaseReported j
  | .risk, j => VE.Risk.Run.runCaseReported j
  | .riskEval, j => VE.Risk.Eval.runCaseReported j
  | .quantity, j => VE.Time.Wire.runCaseReported j VE.Time.Document.extension
  | .normDefaults, j => VE.NormDefaults.Run.runCaseReported j
  | .discourse, j => VE.Discourse.Run.runCaseReported j
  | .readingsRoute, j => VE.Readings.Run.runCaseReported j
  | .diagnose, j => Diagnose.diagnoseCase j

/-- A case the batch decoder rejected on its own (JSON depth): the one-shot record. -/
def caseError (m : Mode) (index : Nat) (message : String) : Json :=
  Json.mkObj ([("status", .str "error"), ("case_index", toJson index), ("error", .str message)] ++
    if m == .checkCertificate || m == .order then [("valid", .bool false)] else [])

def caseResult (m : Mode) (index : Nat) : Except String Json → Json
  | .ok j => runMode m j
  | .error message => caseError m index message

/-! ## Diagnostic codes (docs/LEAN-FIRST-PLAN.md, batch 0)

Every rejection the service returns carries `code`, the public diagnostic code of its
message, so that a client relays Lean's code and text and classifies nothing itself. The
code is derived from the runner's `Class:` prefix by `rejectionCode`, the one place that
does it. It is set beside the runner's result in the bound entry (`bound`), so no runner
and no runner row changes. -/

/-- The public diagnostic codes a rejection can carry (`ve/errors.py`). A runner prefix that
is not one of them (`DependencyCycle`, `ShadowedVariable`, ...) is `InvalidInput`. -/
def rejectionCodes : List String := ["InvalidInput", "SyntaxError", "UnknownSymbol",
  "DuplicateDeclaration", "UnboundVariable", "TypeMismatch", "InvalidModel", "UnsupportedProfile",
  "ResourceLimit", "AdmissionError", "CheckerUnavailable"]

/-- The code of a rejection message: `InvalidModel` when it names a generator
(`Route.Run.generatorOf`), else its text up to the first `:` when that is a public code, else
`InvalidInput`. -/
def rejectionCode (message : String) : String :=
  if (VE.Route.Run.generatorOf message).isSome then "InvalidModel"
  else
    let head := (message.splitOn ":").headD message
    if rejectionCodes.contains head then head else "InvalidInput"

/-- The members set beside a rejection with message `m`: its code, and the generator an
`InvalidModel(generator)` message names (as `Route.Run.runCaseReported` reports it in its row). -/
def codeMembers (m : String) : List (String × Json) :=
  ("code", .str (rejectionCode m)) :: match VE.Route.Run.generatorOf m with
    | some g => [("generator", .str g)]
    | none => []

/-- The members set beside a runner result: `codeMembers` of its message for an error row
(`status` "error" with a text `error`), none for every other result. -/
def coding (result : Json) : List (String × Json) :=
  match result.getObjValD "status", result.getObjValD "error" with
  | .str "error", .str message => codeMembers message
  | _, _ => []

#guard rejectionCode "UnknownSymbol: Unknown predicate p" == "UnknownSymbol"
#guard rejectionCode "InvalidModel(definitions): x" == "InvalidModel"
#guard rejectionCode "DependencyCycle: a -> a" == "InvalidInput"
#guard rejectionCode "String expected" == "InvalidInput"
#guard rejectionCode "ResourceLimit" == "ResourceLimit"

structure Budget where
  cases : Nat := maxCases
  bytes : Nat := maxLineBytes

structure Request where
  id : String
  mode : Mode
  /-- The raw text of the `budget` member, if any, decoded by `decodeBudget` when the request
  runs, so that a malformed budget is a request error bound to the request. -/
  budgetText : Option String := none
  /-- The raw text of the `cases` array, decoded by the mode's runner decoder. -/
  cases : String
  /-- The raw text of the `environments` member, if any: the environments the request
  registers (`register`). -/
  environmentsText : Option String := none

/-- Split a JSON object's text into top-level `(key, value)` texts without decoding
them. Quotes, escapes and bracket depth are tracked as in the batch splitter of
`VE.JsonInput`; every piece is then decoded by the restricted decoder, which requires
it to be exactly one value. -/
def objectMembers (text : String) : Except String (Array (String × String)) := do
  let text := text.trim
  unless text.startsWith "{" && text.endsWith "}" do throw "request must be a JSON object"
  let body := (text.drop 1).dropRight 1
  if body.trim.isEmpty then return #[]
  let mut members : Array (String × String) := #[]
  let mut key : Option String := none
  let mut start : String.Pos := 0
  let mut depth := 0
  let mut quoted := false
  let mut escaped := false
  let mut i : String.Pos := 0
  while i < body.endPos do
    let c := body.get i
    let next := body.next i
    if quoted then
      if escaped then escaped := false
      else if c == '\\' then escaped := true
      else if c == '"' then quoted := false
    else if c == '"' then quoted := true
    else if c == '[' || c == '{' then depth := depth + 1
    else if c == ']' || c == '}' then
      if depth == 0 then throw "unexpected request delimiter"
      depth := depth - 1
    else if depth == 0 && c == ':' && key.isNone then
      key := some (body.extract start i)
      start := next
    else if depth == 0 && c == ',' then
      match key with
      | some k => members := members.push (k, body.extract start i)
      | none => throw "request member without a value"
      key := none
      start := next
    i := next
  if quoted || depth != 0 then throw "unterminated request"
  match key with
  | some k => return members.push (k, body.extract start body.endPos)
  | none => throw "request member without a value"

def decodeString (what raw : String) : Except String String := do
  match ← VE.JsonInput.parse raw with
  | .str s => pure s
  | _ => throw s!"request {what} must be a string"

def decodeBudget (raw : String) : Except String Budget := do
  let j ← VE.JsonInput.parse raw
  let fields ← match j with
    | .obj _ => j.getObj?
    | _ => throw "request field budget must be an object"
  for (k, _) in fields.toList do
    unless k == "cases" || k == "bytes" do throw s!"unknown budget field {k}"
  let capped (k : String) (hard : Nat) : Except String Nat :=
    match j.getObjVal? k with
    | .ok v => do pure (min (← v.getNat?) hard)
    | .error _ => pure hard
  pure { cases := ← capped "cases" maxCases, bytes := ← capped "bytes" maxLineBytes }

/-- The request id, when one can be read, so that a line error still answers it. -/
def requestId? (members : Array (String × String)) : Option String :=
  members.findSome? fun (k, v) =>
    match decodeString "key" k, decodeString "id" v with
    | .ok "id", .ok id => some id
    | _, _ => none

def decodeRequest (members : Array (String × String)) : Except String Request := do
  let mut seen : List String := []
  let mut id : Option String := none
  let mut mode : Option Mode := none
  let mut budgetText : Option String := none
  let mut cases : Option String := none
  let mut environmentsText : Option String := none
  for (rawKey, raw) in members do
    let key ← decodeString "key" rawKey
    if seen.contains key then throw s!"duplicate request field {key}"
    seen := key :: seen
    if key == "id" then id := some (← decodeString "id" raw)
    else if key == "mode" then
      let name ← decodeString "mode" raw
      match Mode.ofName? name with
      | some m => mode := some m
      | none => throw s!"unknown mode {name}"
    else if key == "budget" then budgetText := some raw
    else if key == "cases" then cases := some raw.trim
    else if key == "environments" then environmentsText := some raw
    else throw s!"unknown request field {key}"
  match id, mode, cases with
  | some i, some m, some c => pure { id := i, mode := m, budgetText, cases := c, environmentsText }
  | none, _, _ => throw "request field id is missing"
  | _, none, _ => throw "request field mode is missing"
  | _, _, none => throw "request field cases is missing"

/-- The per-case results: exactly `caseResult` in request order. -/
def results (r : Request) (cases : Array (Except String Json)) : Array Json :=
  cases.mapIdx (caseResult r.mode)

/-! ## Case digests

SHA-256 (FIPS 180-4) for binding results to cases. `VE.CertificateWire.sha256` computes
the same function; this copy keeps the round state in unboxed arguments and reuses one
message schedule, so the digest of a 4 MiB request costs a small part of its decoding.
The `#guard`s pin it to the standard vectors and to `CertificateWire.sha256`. -/
namespace Sha256

private def roundConstants : Array UInt32 := #[
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

@[inline] private def rotr (x n : UInt32) : UInt32 := (x >>> n) ||| (x <<< (32 - n))

/-- Words `i` to 15 of the message schedule: the block at `offset`, big-endian. -/
private def load (bytes : ByteArray) (offset : Nat) (w : Array UInt32) (i : Nat) : Array UInt32 :=
  if i < 16 then
    let j := offset + 4 * i
    load bytes offset (w.set! i ((bytes.get! j).toUInt32 <<< 24 ||| (bytes.get! (j+1)).toUInt32 <<< 16 |||
      (bytes.get! (j+2)).toUInt32 <<< 8 ||| (bytes.get! (j+3)).toUInt32)) (i + 1)
  else w
termination_by 16 - i

/-- Words `i` to 63 of the message schedule. -/
private def extend (w : Array UInt32) (i : Nat) : Array UInt32 :=
  if i < 64 then
    let x := w[i-15]!
    let y := w[i-2]!
    let s0 := rotr x 7 ^^^ rotr x 18 ^^^ (x >>> 3)
    let s1 := rotr y 17 ^^^ rotr y 19 ^^^ (y >>> 10)
    extend (w.set! i (w[i-16]! + s0 + w[i-7]! + s1)) (i + 1)
  else w
termination_by 64 - i

/-- The message schedule of the block at `offset`, written into `w` (64 words). -/
private def schedule (bytes : ByteArray) (offset : Nat) (w : Array UInt32) : Array UInt32 :=
  extend (load bytes offset w 0) 16

structure State where
  (a b c d e f g h : UInt32)

/-- Rounds `i` to 63 of the compression function. -/
private def rounds (w : Array UInt32) (i : Nat) (a b c d e f g h : UInt32) : State :=
  if i < 64 then
    let s1 := rotr e 6 ^^^ rotr e 11 ^^^ rotr e 25
    let ch := (e &&& f) ^^^ ((~~~e) &&& g)
    let t1 := h + s1 + ch + roundConstants[i]! + w[i]!
    let s0 := rotr a 2 ^^^ rotr a 13 ^^^ rotr a 22
    let maj := (a &&& b) ^^^ (a &&& c) ^^^ (b &&& c)
    rounds w (i + 1) (t1 + s0 + maj) a b c (d + t1) e f g
  else ⟨a, b, c, d, e, f, g, h⟩
termination_by 64 - i

private def blocks (bytes : ByteArray) (w : Array UInt32) (block : Nat) (s : State) : State :=
  if 64 * block + 64 ≤ bytes.size then
    let w := schedule bytes (64 * block) w
    let r := rounds w 0 s.a s.b s.c s.d s.e s.f s.g s.h
    blocks bytes w (block + 1) ⟨s.a + r.a, s.b + r.b, s.c + r.c, s.d + r.d, s.e + r.e, s.f + r.f,
      s.g + r.g, s.h + r.h⟩
  else s
termination_by bytes.size - 64 * block

private def hex (word : UInt32) : String :=
  String.mk ((List.range 8).map fun i => Nat.digitChar ((word.toNat / 16 ^ (7 - i)) % 16))

def digest (input : ByteArray) : String := Id.run do
  let bitLength := input.size * 8
  let mut bytes := input.push 128
  let padding := (64 - ((bytes.size + 8) % 64)) % 64
  for _ in [0:padding] do bytes := bytes.push 0
  for i in [0:8] do bytes := bytes.push ((bitLength / 2 ^ (8 * (7 - i))) % 256).toUInt8
  let s := blocks bytes (Array.replicate 64 0) 0
    ⟨0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19⟩
  return hex s.a ++ hex s.b ++ hex s.c ++ hex s.d ++ hex s.e ++ hex s.f ++ hex s.g ++ hex s.h

#guard digest "".toUTF8 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
#guard digest "abc".toUTF8 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
#guard digest "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq".toUTF8 ==
  "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
#guard (List.range 130).all fun n =>
  let s := String.mk ((List.range n).map fun i => Char.ofNat (32 + (i * 7) % 90))
  digest s.toUTF8 == VE.CertificateWire.sha256 s.toUTF8

end Sha256

/-- The binding identity of a case: the SHA-256 of its text in the request's `cases`
array, split as `VE.JsonInput.caseTexts` splits it and trimmed of JSON whitespace. -/
def caseDigest (text : String) : String := Sha256.digest text.trim.toUTF8

/-- JSON whitespace, `Char.isWhitespace` on bytes. -/
private def space (b : UInt8) : Bool := b == 32 || b == 9 || b == 10 || b == 13

/-- The bytes `[start, stop)` trimmed of JSON whitespace. -/
private def trimmed (bytes : ByteArray) (start stop : Nat) : ByteArray := Id.run do
  let mut i := start
  let mut j := stop
  while i < j && space bytes[i]! do i := i + 1
  while i < j && space bytes[j - 1]! do j := j - 1
  return bytes.extract i j

/-- The case boundaries of the body bytes `[i, stop)`: the positions of the commas outside
strings and brackets, in reverse order; `none` if a bracket is unbalanced or a string
unterminated. -/
private def commas (bytes : ByteArray) (stop : Nat) (i depth : Nat) (quoted escaped : Bool)
    (acc : List Nat) : Option (List Nat) :=
  if h : i < stop then
    let c := bytes[i]!
    if quoted then
      if escaped then commas bytes stop (i + 1) depth true false acc
      else if c == 92 then commas bytes stop (i + 1) depth true true acc
      else commas bytes stop (i + 1) depth (c != 34) false acc
    else if c == 34 then commas bytes stop (i + 1) depth true false acc
    else if c == 91 || c == 123 then commas bytes stop (i + 1) (depth + 1) false false acc
    else if c == 93 || c == 125 then
      if depth == 0 then none else commas bytes stop (i + 1) (depth - 1) false false acc
    else if c == 44 && depth == 0 then commas bytes stop (i + 1) depth false false (i :: acc)
    else commas bytes stop (i + 1) depth false false acc
  else if quoted || depth != 0 then none else some acc
termination_by stop - i

/-- `caseDigest` of every case text of a `cases` array, in one pass over its UTF-8 bytes
with `VE.JsonInput.caseTexts`'s rules: the trimmed array's body is split at the commas
outside strings and brackets. Delimiters are ASCII, and no byte of a multi-byte UTF-8
character is ASCII, so the byte split is the character split. -/
def caseDigests (text : String) : Except String (Array String) := do
  let bytes := text.toUTF8
  let mut lo := 0
  let mut hi := bytes.size
  while lo < hi && space bytes[lo]! do lo := lo + 1
  while lo < hi && space bytes[hi - 1]! do hi := hi - 1
  unless lo + 1 < hi && bytes[lo]! == 91 && bytes[hi - 1]! == 93 do
    throw "request field cases must be an array"
  if (trimmed bytes (lo + 1) (hi - 1)).isEmpty then return #[]
  let some cuts := commas bytes (hi - 1) (lo + 1) 0 false false [] | throw "unbalanced batch array"
  let bounds := (lo :: cuts.reverse) ++ [hi - 1]
  return ((bounds.zip bounds.tail).map fun (a, b) => Sha256.digest (trimmed bytes (a + 1) b)).toArray

#guard ["[]", " [ ] ", "[1]", " [ {\"a\":\"x,]\\\"\"} ,\t[1,2]\r, \"é,ü\" ,3] "].all fun t =>
  match caseDigests t, VE.JsonInput.caseTexts t with
  | .ok ds, .ok ts => ds == ts.map caseDigest
  | _, _ => false

/-- Result `i` with its binding, the case's position and digest, and the `coding` of a
rejection. -/
def bound (index : Nat) (digest : String) (result : Json) : Json :=
  Json.mkObj ([("index", toJson index), ("digest", .str digest), ("result", result)] ++ coding result)

/-- Results, each bound to its position and its case digest in `digests`. -/
def bindResults (rs : Array Json) (digests : Array String) : Array Json :=
  rs.mapIdx fun i x => bound i (digests.getD i "") x

/-- The response to a request whose cases decode to `cases` and whose case digests are
`digests` (one per case). The results are computed once, for both `results` and
`counts`. -/
def response (r : Request) (cases : Array (Except String Json)) (digests : Array String) : Json :=
  let rs := results r cases
  Json.mkObj [("id", .str r.id), ("status", .str "ok"), ("mode", .str r.mode.name),
    ("results", .arr (bindResults rs digests)),
    ("counts", Json.mkObj [("cases", toJson cases.size), ("bytes", toJson r.cases.utf8ByteSize),
      ("errors", toJson (rs.filter (·.getObjValD "status" == .str "error")).size)])]

/-- Check the complete English batch with Lean.Json.parse, like the one-shot
runner, then preserve each case's source text for its second parse. -/
def parseEnglishCases (text : String) : Except String (Array (Except String Json)) := do
  let j ← Json.parse text
  let cases ← j.getArr?
  let raw ← VE.JsonInput.caseTexts text
  unless raw.size == cases.size do throw "English batch split mismatch"
  pure (raw.map fun source => .ok (.str source))

/-- The `risk-eval` batch, read with Lean.Json.parse as its former one-shot runner `ve_risk_eval`
read it (its cases carry JSON values the restricted decoder refuses, such as null). -/
def parseLeanCases (text : String) : Except String (Array (Except String Json)) := do
  let cases ← (← Json.parse text).getArr?
  pure (cases.map .ok)

def decodeCases (r : Request) : Except String (Array (Except String Json)) :=
  if r.mode == .english then parseEnglishCases r.cases
  else if r.mode == .riskEval then parseLeanCases r.cases
  else VE.JsonInput.parseCases r.cases

/-! ## Environment handles (docs/LEAN-FIRST-PLAN.md, F2, batch 2)

A call with a real environment spent most of its CPU on the environment's bytes: splitting,
digesting and decoding the request text again on every call (section 3.4). A request may
therefore register environments once, and later cases name them by digest. The table is
content-addressed: a key is accepted only as the SHA-256 of its value's text (`caseDigest`),
so a handle names exactly one environment text. It holds at most `maxHandles` environments
of at most `maxHandleBytes` in all; registering beyond either bound first empties it.

A case that names a handle and no environment is answered as the case with the registered
environment in place of the handle (`expand_hit`, `runRequest_ok`); every other case is
answered as before (`expand_plain`). English and `risk-eval` cases are never expanded: their
decoders are not the restricted one the table parses with. -/

def maxHandles : Nat := 64
def maxHandleBytes : Nat := 67108864
/-- The case member naming a registered environment. -/
def handleKey : String := "environment_handle"

structure Handles where
  table : Std.HashMap String Json := {}
  bytes : Nat := 0

/-- Register `env`, whose text has `size` bytes, under `digest`: unchanged when the digest is
held; otherwise the table, emptied first if it would exceed a bound, with the entry added. -/
def Handles.insert (h : Handles) (digest : String) (env : Json) (size : Nat) : Handles :=
  if h.table.contains digest then h
  else
    let base : Handles :=
      if h.table.size + 1 > maxHandles || h.bytes + size > maxHandleBytes then {} else h
    { table := base.table.insert digest env, bytes := base.bytes + size }

/-- The table after registering one member of `environments`: its key must be the SHA-256 of
its value's text, and the value is parsed by the restricted decoder one level shallower than a
case (an environment sits inside its case), so it is read exactly as it would be inside a case. -/
def registerOne (h : Handles) (member : String × String) : Except String Handles := do
  let digest ← decodeString "environment handle" member.1
  unless caseDigest member.2 == digest do
    throw s!"InvalidInput: environment handle {digest} is not the SHA-256 of its text"
  let env ← VE.JsonInput.parse member.2.trim 254
  pure (h.insert digest env member.2.trim.utf8ByteSize)

/-- The table after the request's `environments` member, registered in order. -/
def register (h : Handles) (r : Request) : Except String Handles := do
  match r.environmentsText with
  | none => pure h
  | some text =>
    let members ← match objectMembers text with
      | .ok members => pure members
      | .error _ => throw "InvalidInput: request field environments must be an object"
    members.foldlM registerOne h

/-- A case with its handle replaced by the registered environment. -/
def Handles.expand (h : Handles) (j : Json) : Except String Json :=
  match j with
  | .obj kvs =>
    match j.getObjVal? handleKey, j.getObjVal? "environment" with
    | .ok (.str d), .error _ =>
      match h.table[d]? with
      | some env => pure (.obj ((kvs.erase handleKey).insert "environment" env))
      | none => throw s!"CheckerUnavailable: environment handle {d} is not registered"
    | _, _ => pure j
  | _ => pure j

/-- Every decoded case expanded (`Handles.expand`), except in the English and `risk-eval`
modes. -/
def expandCases (h : Handles) (m : Mode) (cases : Array (Except String Json)) :
    Except String (Array (Except String Json)) :=
  if m == .english || m == .riskEval then pure cases
  else cases.mapM fun
    | .ok j => .ok <$> h.expand j
    | .error message => pure (.error message)

/-- The request's budget: the service limits, lowered by its `budget` member. -/
def Request.budget (r : Request) : Except String Budget :=
  match r.budgetText with
  | some raw => decodeBudget raw
  | none => pure {}

def runRequest (h : Handles) (r : Request) : Except String Json := do
  let budget ← r.budget
  let bytes := r.cases.utf8ByteSize
  if bytes > budget.bytes then
    throw s!"ResourceLimit: cases are {bytes} bytes; budget is {budget.bytes}"
  unless r.cases.trim.startsWith "[" do throw "request field cases must be an array"
  let cases ← decodeCases r
  if cases.size > budget.cases then
    throw s!"ResourceLimit: batch has {cases.size} cases; budget is {budget.cases}"
  let digests ← caseDigests r.cases
  unless digests.size == cases.size do throw "batch split mismatch"
  pure (response r (← expandCases h r.mode cases) digests)

/-- The error for a line whose envelope cannot be decoded: it answers no request, so
it carries the id when one can be read and no binding. -/
def lineError (id : Option String) (message : String) : Json :=
  Json.mkObj [("id", match id with | some s => .str s | none => .null),
    ("status", .str "error"), ("error", .str message)]

/-- The case digests of a request error: `caseDigests` of the cases text, `null` when it
does not split into cases. -/
def errorDigests (cases : String) : Json :=
  match caseDigests cases with
  | .ok digests => toJson digests
  | .error _ => .null

/-- The error for a decoded request that cannot be answered (budget, batch decoding),
bound like a response: its nonce, its mode and the digests of its cases, with its code. -/
def requestError (r : Request) (message : String) : Json :=
  Json.mkObj [("id", .str r.id), ("status", .str "error"), ("mode", .str r.mode.name),
    ("digests", errorDigests r.cases), ("error", .str message), ("code", .str (rejectionCode message))]

/-- The response to one request line, and the handle table after it: a request registers its
environments (`register`) before it runs, and a request whose registration fails changes no
handle. -/
def respond (h : Handles) (line : String) : Json × Handles :=
  match objectMembers line with
  | .error message => (lineError none message, h)
  | .ok members =>
    match decodeRequest members with
    | .error message => (lineError (requestId? members) message, h)
    | .ok r =>
      match register h r with
      | .error message => (requestError r message, h)
      | .ok h' =>
        match runRequest h' r with
        | .ok answer => (answer, h')
        | .error message => (requestError r message, h')

/-- One input line (with its newline, if any): blank lines are skipped, an over-long
line gets one error record without being decoded. -/
def handleLine (h : Handles) (line : String) : Option Json × Handles :=
  if line.utf8ByteSize > maxLineBytes + 1 then
    (some (lineError none s!"ResourceLimit: request line exceeds {maxLineBytes} bytes"), h)
  else if line.trim.isEmpty then (none, h)
  else
    let (answer, h') := respond h line
    (some answer, h')

/-- The first line the service prints. The build hash is computed by the supervisor,
which hashes the executable it starts. `handles` states the handle table's member and bounds,
which the client mirrors (`Handles.insert`). -/
def handshake : Json :=
  Json.mkObj [("service", .str "ve-lean@1"), ("protocol", toJson (2 : Nat)),
    ("lean", .str Lean.versionString), ("modes", toJson (modes.map Mode.name)),
    ("codes", toJson rejectionCodes), ("limits", Json.mkObj [("max_line_bytes", toJson maxLineBytes),
      ("max_cases", toJson maxCases), ("json_depth", toJson (256 : Nat))]),
    ("handles", Json.mkObj [("member", .str handleKey), ("max", toJson maxHandles),
      ("max_bytes", toJson maxHandleBytes)])]

/-! ## Dispatch pins (statement review: each mode is exactly its existing runner) -/

theorem runMode_evaluate (j : Json) : runMode .evaluate j = VE.Order.runEvaluationCaseReported j := rfl
theorem runMode_checkCertificate (j : Json) :
    runMode .checkCertificate j = VE.CertificateWire.runCaseReported j := rfl
theorem runMode_order (j : Json) : runMode .order j = VE.Order.Surface.runCaseReported j := rfl
theorem runMode_route (j : Json) : runMode .route j = VE.Route.Run.runCaseReported j := rfl
theorem runMode_norms (j : Json) : runMode .norms j = VE.Norms.Run.runCaseReported j := rfl
theorem runMode_english (j : Json) :
    runMode .english j = match VE.English.ServiceRun.run
        (match j with | .str text => text | _ => j.compress) with
      | .ok result => result
      | .error message => Json.mkObj [("status", .str "error"), ("error", .str message)] := rfl
theorem runMode_englishRead (j : Json) :
    runMode .englishRead j = VE.EnglishGrammar.Run.readCaseReported j := rfl
theorem runMode_englishGrammar (j : Json) :
    runMode .englishGrammar j = VE.EnglishGrammar.Run.grammarCaseReported j := rfl
theorem runMode_englishCheck (j : Json) :
    runMode .englishCheck j = VE.EnglishGrammar.Run.checkCaseReported j := rfl
theorem runMode_environment (j : Json) :
    runMode .environment j = Standalone.reported Standalone.environmentCase j := rfl
theorem runMode_model (j : Json) :
    runMode .model j = Standalone.reported Standalone.modelCase j := rfl
theorem runMode_check (j : Json) :
    runMode .check j = Standalone.reported Standalone.checkCase j := rfl
theorem runMode_identity (j : Json) :
    runMode .identity j = Standalone.reported Standalone.identityCase j := rfl
theorem runMode_parse (j : Json) :
    runMode .parse j = Standalone.reported Standalone.parseCase j := rfl
theorem runMode_graph (j : Json) :
    runMode .graph j = Standalone.reported Family.graphMode j := rfl
theorem runMode_readings (j : Json) :
    runMode .readings j = Standalone.reported Family.readingsMode j := rfl
theorem runMode_bundle (j : Json) :
    runMode .bundle j = Standalone.reported FamilyBundle.bundleCase j := rfl
theorem runMode_familyNorms (j : Json) :
    runMode .familyNorms j = FamilyNorms.runCaseReported j := rfl
theorem runMode_softNorms (j : Json) : runMode .softNorms j = VE.SoftNorms.Run.runCaseReported j := rfl
theorem runMode_rights (j : Json) : runMode .rights j = VE.Rights.Run.runCaseReported j := rfl
theorem runMode_speechActs (j : Json) : runMode .speechActs j = VE.SpeechActs.Run.runCaseReported j := rfl
theorem runMode_reports (j : Json) : runMode .reports j = VE.Reports.Run.runCaseReported j := rfl
theorem runMode_alternatives (j : Json) :
    runMode .alternatives j = VE.Alternatives.Run.runCaseReported j := rfl
theorem runMode_risk (j : Json) : runMode .risk j = VE.Risk.Run.runCaseReported j := rfl
theorem runMode_riskEval (j : Json) : runMode .riskEval j = VE.Risk.Eval.runCaseReported j := rfl
theorem runMode_quantity (j : Json) :
    runMode .quantity j = VE.Time.Wire.runCaseReported j VE.Time.Document.extension := rfl
theorem runMode_normDefaults (j : Json) :
    runMode .normDefaults j = VE.NormDefaults.Run.runCaseReported j := rfl
theorem runMode_discourse (j : Json) : runMode .discourse j = VE.Discourse.Run.runCaseReported j := rfl
theorem runMode_readingsRoute (j : Json) :
    runMode .readingsRoute j = VE.Readings.Run.runCaseReported j := rfl
theorem runMode_diagnose (j : Json) : runMode .diagnose j = Diagnose.diagnoseCase j := rfl


theorem caseResult_ok (m : Mode) (i : Nat) (j : Json) : caseResult m i (.ok j) = runMode m j := rfl

/-- A request within its budget whose cases decode, one digest per case, is answered with
`response`: `results`, the existing runner applied to every case in order, each bound
to its case digest. -/
theorem runRequest_ok (h : Handles) (r : Request) (budget : Budget) (cases expanded : Array (Except String Json))
    (digests : Array String) (hq : r.budget = .ok budget)
    (hb : r.cases.utf8ByteSize ≤ budget.bytes) (ha : r.cases.trim.startsWith "[" = true)
    (hp : decodeCases r = .ok cases)
    (hc : cases.size ≤ budget.cases)
    (ht : caseDigests r.cases = .ok digests) (hn : digests.size = cases.size)
    (hx : expandCases h r.mode cases = .ok expanded) :
    runRequest h r = .ok (response r expanded digests) := by
  simp [runRequest, hq, Nat.not_lt.mpr hb, ha, hp, Nat.not_lt.mpr hc, ht, hn, hx, bind, Except.bind, pure,
    Except.pure]

/-- A case that names no handle is answered as it was sent. -/
theorem expand_plain (h : Handles) (j : Json) (hj : ∀ d, j.getObjVal? handleKey ≠ .ok (.str d)) :
    h.expand j = .ok j := by
  unfold Handles.expand
  split
  · next kvs =>
    split
    · next d _ hd _ => exact absurd hd (hj d)
    · rfl
  · rfl

/-- A case that names a registered handle and no environment is answered as the case with
that environment in place of the handle. -/
theorem expand_hit (h : Handles) (kvs : Std.TreeMap.Raw String Json compare) (d : String) (env : Json)
    (hd : (Json.obj kvs).getObjVal? handleKey = .ok (.str d))
    (he : ∀ e, (Json.obj kvs).getObjVal? "environment" ≠ .ok e)
    (ht : h.table[d]? = some env) :
    h.expand (.obj kvs) = .ok (.obj ((kvs.erase handleKey).insert "environment" env)) := by
  unfold Handles.expand
  cases hv : (Json.obj kvs).getObjVal? "environment" with
  | ok e => exact absurd hv (he e)
  | error _ => simp [hd, ht, pure, Except.pure]

/-- A case that names a handle the table does not hold makes the request unavailable. -/
theorem expand_miss (h : Handles) (kvs : Std.TreeMap.Raw String Json compare) (d : String)
    (hd : (Json.obj kvs).getObjVal? handleKey = .ok (.str d))
    (he : ∀ e, (Json.obj kvs).getObjVal? "environment" ≠ .ok e)
    (ht : h.table[d]? = none) :
    h.expand (.obj kvs) = .error s!"CheckerUnavailable: environment handle {d} is not registered" := by
  unfold Handles.expand
  cases hv : (Json.obj kvs).getObjVal? "environment" with
  | ok e => exact absurd hv (he e)
  | error _ => simp [hd, ht, throw, throwThe, MonadExceptOf.throw]

/-- English and `risk-eval` cases are never expanded. -/
theorem expandCases_unexpanded (h : Handles) (m : Mode) (cases : Array (Except String Json))
    (hm : m = .english ∨ m = .riskEval) : expandCases h m cases = .ok cases := by
  rcases hm with rfl | rfl <;> rfl

/-- A request without an `environments` member changes no handle. -/
theorem register_none (h : Handles) (r : Request) (hr : r.environmentsText = none) :
    register h r = .ok h := by
  simp [register, hr, pure, Except.pure]

/-- Registration is content-addressed: a key that is not the SHA-256 of its value's text is
refused. -/
theorem registerOne_digest (h : Handles) (key raw digest : String)
    (hk : decodeString "environment handle" key = .ok digest) (hd : caseDigest raw ≠ digest) :
    registerOne h (key, raw) =
      .error s!"InvalidInput: environment handle {digest} is not the SHA-256 of its text" := by
  simp [registerOne, hk, hd, bind, Except.bind]

/-- A registered environment is the restricted decoding of its text, under its digest. -/
theorem registerOne_ok (h : Handles) (key raw : String) (env : Json)
    (hk : decodeString "environment handle" key = .ok (caseDigest raw))
    (hp : VE.JsonInput.parse raw.trim 254 = .ok env) :
    registerOne h (key, raw) = .ok (h.insert (caseDigest raw) env raw.trim.utf8ByteSize) := by
  simp [registerOne, hk, hp, bind, Except.bind, pure, Except.pure]

/-- Every error for a decoded request is bound to it: a line whose envelope decodes to `r`
is answered with `r`'s response or with `requestError r`, which carries `r`'s nonce, mode
and case digests. -/
theorem respond_decoded (h : Handles) (line : String) (members : Array (String × String)) (r : Request)
    (hm : objectMembers line = .ok members) (hr : decodeRequest members = .ok r) :
    (respond h line).1 = match register h r with
      | .error message => requestError r message
      | .ok h' => match runRequest h' r with
        | .ok answer => answer
        | .error message => requestError r message := by
  simp only [respond, hm, hr]
  split <;> (try split) <;> rfl

theorem results_eq (r : Request) (cases : Array (Except String Json)) (i : Nat) (h : i < cases.size) :
    (results r cases)[i]? = some (caseResult r.mode i cases[i]) := by
  simp [results, h]

/-- Result `i` of a response is case `i`'s runner result, bound to its position and to
its case digest. -/
theorem boundResults_eq (r : Request) (cases : Array (Except String Json)) (digests : Array String)
    (i : Nat) (h : i < cases.size) :
    (bindResults (results r cases) digests)[i]? =
      some (bound i (digests.getD i "") (caseResult r.mode i cases[i])) := by
  simp [bindResults, results, h]

/-- A bound entry is the runner's result unchanged, beside its position, its digest and its
`coding`. -/
theorem bound_eq (index : Nat) (digest : String) (result : Json) :
    bound index digest result = Json.mkObj ([("index", toJson index), ("digest", .str digest),
      ("result", result)] ++ coding result) := rfl

/-- Nothing is set beside a result whose status is not "error". -/
theorem coding_of_status (result : Json) (h : result.getObjValD "status" ≠ .str "error") :
    coding result = [] := by
  unfold coding
  split
  · simp_all
  · rfl

/-- Beside a rejection with message `m`: exactly `codeMembers m`, its code first. -/
theorem coding_error (result : Json) (m : String) (hs : result.getObjValD "status" = .str "error")
    (he : result.getObjValD "error" = .str m) :
    coding result = codeMembers m := by
  simp [coding, hs, he]

/-- Every code is a public diagnostic code. -/
theorem rejectionCode_mem (m : String) : rejectionCode m ∈ rejectionCodes := by
  unfold rejectionCode
  split
  · simp [rejectionCodes]
  · dsimp only
    split
    · next h => exact List.contains_iff_mem.mp h
    · simp [rejectionCodes]

end VE.Service
