import VE.Acts.Decode
import VE.Compose.Dispatch

/-! The `acts-elaborate` case kind of the `norms` and `norm-defaults` modes (act-phrases 6.7, C18): the elaborated
document of an `acts@0` case and the map from each generated part to its source, which Python binds to the request
and relays. One runner answers both modes; each passes the decoder its route reads before elaboration
(`Norms.Wire.decodeSource` with its flags, or `NormDefaults.Wire.decodeSourceU`).

The row is `ELABORATED` with the parts' declarations (`predicates`), the part rules (`rules`), the joined acts that
did not split (`kept`) and, per split source, its parts and D-28's text (`split`); or `REFUSED` with the
elaboration's diagnostic and every list empty. A refusal of the decoder itself (the act check's D-15 to D-18) is the
case's error, as on every other kind. Each list is read off `e.U'` and `e.M` once: the decoded document is bounded by
the decoder's limits (64 regulated predicates, 256 rules) and the elaboration by step 6's (6.3). -/

namespace VE.Acts.Run
open Lean VE.Acts VE.NormDefaults

def roleJson : VE.Norms.Role → Json
  | .permission => "permission"
  | .obligation => "obligation"
  | .plain => "plain"

def completionJson (U : UDoc) (r : VE.Norms.Regulated) : Json :=
  match completionOf U r with
  | .allow => "allow"
  | .deny => "deny"
  | .unspecified => "unspecified"

def optJson : Option String → Json
  | some s => .str s
  | none => .null

/-- One row per part declared in `U'`, with its source and index from `M.preds`. -/
def predicatesJson (U' : UDoc) (M : SplitMap) : Json :=
  Json.arr (U'.D.T.regulated.filterMap fun r => (M.preds.find? (·.1 == r.name)).map fun (_, p, i) =>
    Json.mkObj [("name", .str r.name), ("source", .str p), ("index", toJson i), ("sorts", toJson r.sorts),
      ("role", roleJson r.role), ("default", completionJson U' r), ("act", optJson r.act),
      ("permission", optJson r.permission)]).toArray

/-- One row per part rule in `U'`, with its source rule and index from `M.rules`. -/
def rulesJson (U' : UDoc) (M : SplitMap) : Json :=
  Json.arr (U'.D.T.nodes.filterMap fun N => (M.rules.find? (·.1 == N.name)).map fun (_, n, i) =>
    Json.mkObj [("name", .str N.name), ("source", .str n), ("index", toJson i), ("pred", .str N.pred),
      ("sign", .bool N.sign), ("guard", VE.Norms.Wire.enc N.guard),
      ("unless", Json.arr (N.carveOuts.map VE.Norms.Wire.enc).toArray), ("over", toJson N.over)]).toArray

/-- D-28: the refusal of a model, data or question that names the split source `p`. -/
def partsText (p : String) (parts : List String) : String :=
  s!"InvalidInput: name one of its parts: {p} is split into {", ".intercalate parts}"

/-- Per split source, in the map's order: its parts in index order and D-28's text. -/
def splitRows (M : SplitMap) : Json :=
  Json.arr ((M.preds.map (·.2.1)).eraseDups.map fun p =>
    let parts := (M.preds.filter (·.2.1 == p)).map (·.1)
    Json.mkObj [("source", .str p), ("parts", toJson parts), ("text", .str (partsText p parts))]).toArray

/-- The elaborated row's lists. -/
def elaboratedFields (e : VE.Acts.Decode.ElaboratedU) : List (String × Json) :=
  [("predicates", predicatesJson e.U' e.M), ("rules", rulesJson e.U' e.M),
   ("kept", toJson ((e.D.acts.map (·.1)).filter fun p => !e.M.preds.any (·.2.1 == p))),
   ("split", splitRows e.M)]

def emptyFields : List (String × Json) :=
  [("predicates", Json.arr #[]), ("rules", Json.arr #[]), ("kept", Json.arr #[]), ("split", Json.arr #[])]

/-- `acts-elaborate`: the case's source decoded by `decode`, then `elaborateSource` and `sourceOf`, as the route
that reads it runs them (6.4); the identity is the route's own (`Flagged.decodePackage`). -/
def runElaborate (decode : Json → Json → Except String VE.NormDefaults.Wire.SourceU) (j : Json) :
    Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let written ← j.getObjVal? "environment"
  let environment ← VE.Compose.decidingEnvironment written
  if (VE.Norms.Wire.actsProfiles true environment).isEmpty then
    throw "UnsupportedProfile: acts-elaborate requires acts@0"
  let s ← decode environment (j.getObjValD "norms")
  let envId ← VE.Route.Wire.environmentId s.src.ne.profiles (← VE.Norms.Wire.canonicalEnvironmentJson written)
  match VE.Acts.Decode.elaborateSource environment s >>= fun e => (VE.Acts.Decode.sourceOf e).map fun _ => e with
  | .ok e => pure (VE.Route.Wire.ok id
      ([("environment_id", .str envId), ("verdict", .str "ELABORATED")] ++ elaboratedFields e))
  | .error d => pure (VE.Route.Wire.ok id
      ([("environment_id", .str envId), ("verdict", .str "REFUSED"), ("diagnostic", .str d)] ++ emptyFields))

/-- The norms route's decoder before elaboration (`Acts.Decode.decodeElaboratedFlagged`'s first step). -/
def normsSource (environment norms : Json) : Except String VE.NormDefaults.Wire.SourceU :=
  VE.Acts.Decode.plainU <$> VE.Norms.Wire.decodeSource environment norms (flags := true)

def isElaborate (j : Json) : Bool :=
  match j.getObjValD "kind" with
  | .str k => k == "acts-elaborate"
  | _ => false

/-! ### The `act-readings` mode (act-phrases 7, AP-4)

The readings of one act phrase under a rule's modal words, and their paraphrases, which the translator's tool writes
into a reading set that `sourceCheck` then checks. Lean lexes the phrase: `tokens` is each token's UTF-8 byte span in
the request's `phrase`, and each act's `from` the indices of the tokens its text reads. The request is charged
against the act phrase's 400 bytes (`Lexical.maxActBytes`), the fixed phrases' and frames' limits (`decodeFixed`,
`checkVocab`) and the parse limits (`rawCap`, `stepBudget`, 64 readings): the phrase is lexed once, its readings
listed once (`phraseReadings`, at most 64: `phraseReadings_length`) and paraphrased once. -/

/-- Each token's UTF-8 byte span in `s` as written: its text (`tokStr`, folded, single-spaced) read after the
    whitespace before it. `none` only for a slot written with leading zeros. -/
def spans (fx : List String) (s : String) (ts : List Lexical.Tok) : Option (List (Nat × Nat)) :=
  let ws : Char → Bool := VE.Norms.Wire.pyWhitespace
  let rec skip : List Char → Nat → List Char × Nat
    | c :: cs, p => if ws c then skip cs (p + c.utf8Size) else (c :: cs, p)
    | [], p => ([], p)
  let rec read : List Char → List Char → Nat → Option (List Char × Nat)
    | [], cs, p => some (cs, p)
    | x :: t, c :: cs, p =>
      if x == ' ' then (if ws c then let (r, q) := skip cs (p + c.utf8Size); read t r q else none)
      else if (if c.toNat == 0x2019 then '\'' else c) == x then read t cs (p + c.utf8Size) else none
    | _ :: _, [], _ => none
  (ts.foldlM (fun (acc : List (Nat × Nat) × List Char × Nat) t => do
    let (r, p) := skip acc.2.1 acc.2.2
    let (r', q) ← read (tokStr fx t).toList r p
    pure (acc.1 ++ [(p, q)], r', q)) ([], s.toList, 0)).map Prod.fst

/-- One token, read as the grammar's terminals read a word (`Term.accepts`: case-insensitively). -/
def sameTok : Lexical.Tok → Lexical.Tok → Bool
  | .word v, .word w => v.toLower == w.toLower
  | t, u => t == u

/-- An act's `from`: each of its tokens `xs` in order placed at a phrase token of `ps`, first rightmost as a
    subsequence (each at the last equal token before the next one's), then each one left at the first equal token
    not yet used; a token the rendering adds that the phrase lacks (*to* after *has the right*) has none. The
    indices are in range and none occurs twice. -/
def fromOf (ps xs : List Lexical.Tok) : List Nat :=
  let ips := (List.range ps.length).zip ps
  let placed := (xs.foldr (fun x (acc : List (Option Nat) × Nat) =>
    match ((ips.take acc.2).reverse.find? (sameTok x ·.2)) with
    | some (i, _) => (some i :: acc.1, i)
    | none => (none :: acc.1, acc.2)) ([], ps.length)).1
  ((xs.zip placed).foldl (fun (acc : List Nat × List Nat) (x, o) => match o with
    | some i => (acc.1 ++ [i], acc.2)
    | none => match ips.find? (fun (i, t) => sameTok x t && !acc.2.contains i) with
      | some (i, _) => (acc.1 ++ [i], acc.2 ++ [i])
      | none => acc) ([], placed.filterMap id)).1

/-- One simple act of a reading: `act`, its text as a predicate declares it (*to* exactly when `plain`, as
    `Sources.expected` renders it); `text`, the act under the modal (`sentence`); `from`, its tokens in the phrase. -/
def actJson (fx : List String) (op : Op) (f : Option Lexical.Form) (plain : Bool) (ps : List Lexical.Tok) (x : Simple) :
    Except String Json := do
  let act := Simple.text fx (some plain) x
  pure (Json.mkObj [("act", .str act), ("text", .str (sentence fx op f x)),
    ("from", toJson (fromOf ps (← Lexical.lex fx act)))])

/-- One reading: its simple acts in order and its paraphrase. -/
def readingJson (fx : List String) (op : Op) (f : Option Lexical.Form) (plain : Bool) (ps : List Lexical.Tok)
    (x : List Simple × String) : Except String Json := do
  let acts ← x.1.mapM (actJson fx op f plain ps)
  pure (Json.mkObj [("acts", Json.arr acts.toArray), ("paraphrase", .str x.2)])

/-- The readings' rows: their paraphrases first, refused with D-32 (`paraphrases`, "this act phrase") when two read
    the same, then each reading's acts. -/
def rowsOf (fx : List String) (op : Op) (f : Option Lexical.Form) (plain : Bool) (ps : List Lexical.Tok)
    (Rs : List (List Simple)) : Except String (List Json) := do
  let texts ← paraphrases fx op f "this act phrase" Rs
  (Rs.zip texts).mapM (readingJson fx op f plain ps)

/-- The `LISTED` row: the phrase's token spans, then each reading's acts and paraphrase. The limits come first: the
    act phrase's 400 bytes, the lexing (`decodeFixed`'s limits), the parse limits; then D-32 (`paraphrases`). -/
def listReadings (id : String) (fx : List String) (V : Vocab) (op : Op) (f : Option Lexical.Form) (plain : Bool)
    (phrase : String) : Except String Json := do
  if Lexical.maxActBytes < phrase.utf8ByteSize then
    throw s!"ResourceLimit: this act phrase is over {Lexical.maxActBytes} bytes"
  let ts ← (Lexical.lex fx phrase).mapError fun e =>
    if e == "comma" then "InvalidInput: this act phrase ends with a comma" else e
  let some sp := spans fx phrase ts | throw "InvalidInput: this act phrase writes a slot with a leading zero"
  match phraseReadings V op rawCap stepBudget ts.toArray with
  | .limit => throw "ResourceLimit: this act phrase has too many readings to list; split the sentence"
  | .ok [] => throw "InvalidInput: this act phrase has no reading under the declared frames and its modal words"
  | .ok Rs =>
    let rows ← rowsOf fx op f plain ts Rs
    pure (VE.Route.Wire.ok id [("verdict", .str "LISTED"),
      ("tokens", Json.arr (sp.map fun (a, b) => Json.arr #[toJson a, toJson b]).toArray),
      ("readings", Json.arr rows.toArray)])

/-- A refusal's verdict: `LIMIT` exactly when it is a `ResourceLimit`, else `REFUSED`. -/
def verdictOf (d : String) : String := if d.startsWith "ResourceLimit:" then "LIMIT" else "REFUSED"

/-- A refusal of the phrase: its verdict and diagnostic, both lists empty. -/
def refusedRow (id d : String) : Json :=
  VE.Route.Wire.ok id [("verdict", .str (verdictOf d)), ("tokens", Json.arr #[]), ("readings", Json.arr #[]),
    ("diagnostic", .str d)]

/-- The request's members (7): `form`, a plain act's form, may be absent (the service's JSON has no `null`). -/
def decodeRequest (j : Json) :
    Except String (String × String × List String × VE.Norms.Role × Bool × Option Lexical.Form) := do
  VE.Bridge.exactFields j (["id", "phrase", "fixed", "frames", "adverbs", "role", "sign"] ++
    if (j.getObjVal? "form").isOk then ["form"] else [])
  let role ← match j.getObjValD "role" with
    | .str "permission" => pure VE.Norms.Role.permission
    | .str "obligation" => pure .obligation
    | .str "plain" => pure .plain
    | _ => throw "InvalidInput: role is not permission, obligation or plain"
  let .bool sign := j.getObjValD "sign" | throw "InvalidInput: sign is not a boolean"
  let f ← match j.getObjVal? "form" with
    | .error _ => pure none
    | .ok (.str t) => match Lexical.Form.ofText? t with
      | some f => pure (some f)
      | none => throw "InvalidInput: form is not has the right or is entitled"
    | _ => throw "InvalidInput: form is not has the right or is entitled"
  pure (← VE.Bridge.stringField j "id", ← VE.Bridge.stringField j "phrase", ← VE.Bridge.strings (j.getObjValD "fixed"),
    role, sign, f)

/-- The frames and adverbs (`decodeVocab`, D-31), the op of the role and sign (`opOf`), then `listReadings`. -/
def listed (j : Json) (id phrase : String) (fx : List String) (role : VE.Norms.Role) (sign : Bool)
    (f : Option Lexical.Form) : Except String Json := do
  let V ← VE.Acts.Wire.decodeVocab (Json.mkObj [("frames", j.getObjValD "frames"), ("adverbs", j.getObjValD "adverbs")])
  let some op := opOf ⟨"", [], false, role, none, none⟩ sign
    | throw "InvalidInput: this act phrase has no modal word: a plain act with sign false"
  listReadings id fx V op f (role == .plain) phrase

/-- `act-readings`: a malformed request is the case's error, a refusal of its content a `REFUSED` or `LIMIT` row. -/
def runActReadings (j : Json) : Except String Json := do
  let (id, phrase, fx, role, sign, f) ← decodeRequest j
  pure (match listed j id phrase fx role sign f with
    | .ok row => row
    | .error d => refusedRow id d)

def actReadingsReported (j : Json) : Json :=
  match runActReadings j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end VE.Acts.Run
