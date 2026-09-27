import VE.Json
import VE.Order.ProfileGate
import VE.CertificateWire
import VE.Order.Surface
import VE.Route.Run
import VE.Norms.Run
import VE.Service.EnglishRun

/-! # `ve_service` protocol (docs/spec/SEMANTICS-MIGRATION-PLAN.md, stage 1)

Glue only: nothing here decides a verdict. A request line is

    {"id": string, "mode": string, "cases": [...], "budget"?: {"cases"?: n, "bytes"?: n}}

and its response line is `{"counts", "id", "mode", "results", "status": "ok"}`, whose
`results` are, case for case and in order, the output of the existing runner for the
mode (`runMode`, pinned per mode below), or a line error `{"error", "id", "status":
"error"}`. Non-English cases are decoded by `VE.JsonInput.parseCases`, the one-shot
batch decoder; English uses `Lean.Json.parse`, its one-shot decoder. No state
is kept between lines.

Budgets are deterministic functions of the request: its size in bytes and its number
of cases, each capped by the service limits; exceeding one is `ResourceLimit`. Work
inside a runner is not budgeted here (the reference runners have no work budget).

Trusted, as for the one-shot runners: the member splitter `objectMembers` and the
restricted decoder `VE.JsonInput`, which have no refinement theorem. -/
namespace VE.Service
open Lean

/-- Longest accepted request line, as the one-shot runners' input cap. -/
def maxLineBytes : Nat := 16777216
/-- Most cases in one request. -/
def maxCases : Nat := 4096

inductive Mode where
  | evaluate | checkCertificate | order | route | norms | english
  deriving DecidableEq, Repr

def Mode.name : Mode → String
  | .evaluate => "evaluate"
  | .checkCertificate => "check-certificate"
  | .order => "order"
  | .route => "route"
  | .norms => "norms"
  | .english => "english"

def modes : List Mode := [.evaluate, .checkCertificate, .order, .route, .norms, .english]

def Mode.ofName? (name : String) : Option Mode := modes.find? (·.name == name)

/-- The English runner reads one `{environment, lexicon, cases}` object. Its one-shot
failure (a message on stderr, exit 2) becomes an error record. -/
def englishReported (j : Json) : Json :=
  match VE.English.ServiceRun.run j.compress with
  | .ok result => result
  | .error message => Json.mkObj [("status", .str "error"), ("error", .str message)]

/-- One decoded case: the reported output of the existing runner for the mode.
`evaluate`, `check-certificate`, `order` and `route` are the `ve_conformance`
subcommands, `norms` is `ve_norms_route`, `english` is `VE/English/Run.lean`. -/
def runMode : Mode → Json → Json
  | .evaluate, j => VE.Order.runEvaluationCaseReported j
  | .checkCertificate, j => VE.CertificateWire.runCaseReported j
  | .order, j => VE.Order.Surface.runCaseReported j
  | .route, j => VE.Route.Run.runCaseReported j
  | .norms, j => VE.Norms.Run.runCaseReported j
  | .english, j => englishReported j

/-- A case the batch decoder rejected on its own (JSON depth): the one-shot record. -/
def caseError (m : Mode) (index : Nat) (message : String) : Json :=
  Json.mkObj ([("status", .str "error"), ("case_index", toJson index), ("error", .str message)] ++
    if m == .checkCertificate || m == .order then [("valid", .bool false)] else [])

def caseResult (m : Mode) (index : Nat) : Except String Json → Json
  | .ok j => runMode m j
  | .error message => caseError m index message

structure Budget where
  cases : Nat := maxCases
  bytes : Nat := maxLineBytes

structure Request where
  id : String
  mode : Mode
  budget : Budget
  /-- The raw text of the `cases` array, decoded by the mode's runner decoder. -/
  cases : String

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
  let mut budget : Budget := {}
  let mut cases : Option String := none
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
    else if key == "budget" then budget ← decodeBudget raw
    else if key == "cases" then cases := some raw.trim
    else throw s!"unknown request field {key}"
  match id, mode, cases with
  | some i, some m, some c => pure { id := i, mode := m, budget, cases := c }
  | none, _, _ => throw "request field id is missing"
  | _, none, _ => throw "request field mode is missing"
  | _, _, none => throw "request field cases is missing"

/-- The per-case results: exactly `caseResult` in request order. -/
def results (r : Request) (cases : Array (Except String Json)) : Array Json :=
  cases.mapIdx (caseResult r.mode)

def response (r : Request) (cases : Array (Except String Json)) : Json :=
  let rs := results r cases
  Json.mkObj [("id", .str r.id), ("status", .str "ok"), ("mode", .str r.mode.name),
    ("results", .arr rs),
    ("counts", Json.mkObj [("cases", toJson cases.size), ("bytes", toJson r.cases.utf8ByteSize),
      ("errors", toJson (rs.filter (·.getObjValD "status" == .str "error")).size)])]

/-- English's one-shot input uses Lean.Json.parse, so decode its service batch
with the same parser. Other modes retain the restricted runner batch decoder. -/
def parseEnglishCases (text : String) : Except String (Array (Except String Json)) := do
  let j ← Json.parse text
  let cases ← j.getArr?
  pure (cases.map .ok)

def decodeCases (r : Request) : Except String (Array (Except String Json)) :=
  if r.mode == .english then parseEnglishCases r.cases else VE.JsonInput.parseCases r.cases

def runRequest (r : Request) : Except String Json := do
  let bytes := r.cases.utf8ByteSize
  if bytes > r.budget.bytes then
    throw s!"ResourceLimit: cases are {bytes} bytes; budget is {r.budget.bytes}"
  unless r.cases.trim.startsWith "[" do throw "request field cases must be an array"
  let cases ← decodeCases r
  if cases.size > r.budget.cases then
    throw s!"ResourceLimit: batch has {cases.size} cases; budget is {r.budget.cases}"
  pure (response r cases)

def lineError (id : Option String) (message : String) : Json :=
  Json.mkObj [("id", match id with | some s => .str s | none => .null),
    ("status", .str "error"), ("error", .str message)]

/-- The response to one request line. -/
def respond (line : String) : Json :=
  match objectMembers line with
  | .error message => lineError none message
  | .ok members =>
    match decodeRequest members >>= runRequest with
    | .ok answer => answer
    | .error message => lineError (requestId? members) message

/-- One input line (with its newline, if any): blank lines are skipped, an over-long
line gets one error record without being decoded. -/
def handleLine (line : String) : Option Json :=
  if line.utf8ByteSize > maxLineBytes + 1 then
    some (lineError none s!"ResourceLimit: request line exceeds {maxLineBytes} bytes")
  else if line.trim.isEmpty then none
  else some (respond line)

/-- The first line the service prints. The build hash is computed by the supervisor,
which hashes the executable it starts. -/
def handshake : Json :=
  Json.mkObj [("service", .str "ve-lean@1"), ("protocol", toJson (1 : Nat)),
    ("lean", .str Lean.versionString), ("modes", toJson (modes.map Mode.name)),
    ("limits", Json.mkObj [("max_line_bytes", toJson maxLineBytes),
      ("max_cases", toJson maxCases), ("json_depth", toJson (256 : Nat))])]

/-! ## Dispatch pins (statement review: each mode is exactly its existing runner) -/

theorem runMode_evaluate (j : Json) : runMode .evaluate j = VE.Order.runEvaluationCaseReported j := rfl
theorem runMode_checkCertificate (j : Json) :
    runMode .checkCertificate j = VE.CertificateWire.runCaseReported j := rfl
theorem runMode_order (j : Json) : runMode .order j = VE.Order.Surface.runCaseReported j := rfl
theorem runMode_route (j : Json) : runMode .route j = VE.Route.Run.runCaseReported j := rfl
theorem runMode_norms (j : Json) : runMode .norms j = VE.Norms.Run.runCaseReported j := rfl
theorem runMode_english (j : Json) :
    runMode .english j = match VE.English.ServiceRun.run j.compress with
      | .ok result => result
      | .error message => Json.mkObj [("status", .str "error"), ("error", .str message)] := rfl

theorem caseResult_ok (m : Mode) (i : Nat) (j : Json) : caseResult m i (.ok j) = runMode m j := rfl

/-- A request within its budget whose cases decode is answered with `results`, the
existing runner applied to every case in order. -/
theorem runRequest_ok (r : Request) (cases : Array (Except String Json))
    (hb : r.cases.utf8ByteSize ≤ r.budget.bytes) (ha : r.cases.trim.startsWith "[" = true)
    (hp : decodeCases r = .ok cases)
    (hc : cases.size ≤ r.budget.cases) :
    runRequest r = .ok (response r cases) := by
  simp [runRequest, Nat.not_lt.mpr hb, ha, hp, Nat.not_lt.mpr hc, bind, Except.bind, pure,
    Except.pure]

theorem results_eq (r : Request) (cases : Array (Except String Json)) (i : Nat) (h : i < cases.size) :
    (results r cases)[i]? = some (caseResult r.mode i cases[i]) := by
  simp [results, h]

end VE.Service
