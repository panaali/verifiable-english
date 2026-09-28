import VE.SpeechActs.Consequence
import VE.Norms.Replay
import VE.Route.Admission
import Std.Data.TreeMap.Raw.Lemmas
import Std.Data.TreeMap.Raw.WF

/-! The `speech-acts@0` decoder (docs/spec/speech-acts.md 1.6, 3.1, 3.2 and 8.6).

The frozen P0 envelope gate does not know `speech-acts@0`, and its envelope
decoder rejects a `speech_acts` field. `decodeSpeechEnvironmentFull` therefore
runs the profile allowlist of 1.6 (exactly `norms@0`, `relational-fol@0` and
`speech-acts@0`), rejects W3 definitions and W5 flags with the route, decodes
the scope block strictly (unknown fields rejected), strips exactly the block
and the profile, decodes the rest with W1's unchanged `decodeNormsEnvironment`
and keeps the original environment for identity.

The scope block is a top-level field `speech_acts` of the environment object
(the placement `scope_in_identity`, 8.5, states); the canonical environment
(`canonicalEnvironmentJson`) is W1's act-normalised environment with the block
replaced by its canonical encoding, so `environment_id` binds the scope.

`decodeDocument` reads the units of a speech-act document (3.2): W2 kinds plus
`binding`; command content only under `instruction` or a quoted kind, question
content only under `question` or a quoted kind, norm content only under `norm`
or a quoted kind (rejected, never discarded, otherwise); active commands and
norms, dormant (quoted, non-specified) commands with their single-unit checks,
questions, authored bindings merged into the scope (`BindingConflict`,
`DuplicateDeclaration`), fixed asserted units, and the derived query records,
whose premise ids must be exactly the asserted units before the unit that asks
(`QueryMismatch`). The result is a `SpeechDoc` accepted by `WellFormedSpeech`.
Wordings (`ModeMismatch`) need the English layer (plan item 3) and are not
checked here. -/
namespace VE.SpeechActs.Wire
open Lean
open VE.Bridge (exactFields fields stringField strings)
open VE.Norms (Regulated Node background elaborate)

def speechProfile : String := "speech-acts@0"

/-- 1.6: the profiles this route admits, and nothing else. -/
def allowlist : List String := ["norms@0", "relational-fol@0", "speech-acts@0"]

def invalidBlock : String := "InvalidInput: speech_acts block"

/-! ## The scope block -/

/-- The canonical encoding of a scope: `task`, then `addressee` and `definites` when present. -/
def encodeScope (sc : Scope) : Json :=
  Json.mkObj ([("task", Json.str sc.task)] ++
    (match sc.addressee with
     | some (s, c) => [("addressee", Json.mkObj [("sort", .str s), ("constant", .str c)])]
     | none => []) ++
    (if sc.definites.isEmpty then [] else
      [("definites", Json.mkObj (sc.definites.map (fun (p, c) => (p, Json.str c))))]))

def keysWithin (j : Json) (allowed : List String) : Except String (List (String × Json)) := do
  let fs ← match fields j with
    | .ok fs => pure fs
    | .error _ => throw invalidBlock
  unless fs.all (fun kv => allowed.contains kv.1) do throw invalidBlock
  pure fs

/-- A definite phrase in its normal form: single spaces, first word `the`, at most 80 bytes, words of letters,
apostrophes and hyphens. -/
def phraseOk (p : String) : Bool :=
  let ws := VE.Norms.Wire.words p
  " ".intercalate ws == p && p.utf8ByteSize ≤ 80 && ws.length ≥ 2 && ws.head? == some "the" &&
    ws.all VE.Norms.Wire.actWord

/-- The structural decoding of the block (3.1); declarations are checked against the environment later. -/
def parseScope (block : Json) : Except String Scope := do
  let fs ← keysWithin block ["task", "addressee", "definites"]
  let task ← match fs.find? (·.1 == "task") with
    | some (_, .str t) => pure t
    | _ => throw invalidBlock
  let addressee ← match fs.find? (·.1 == "addressee") with
    | none => pure none
    | some (_, a) => do
      let afs ← keysWithin a ["sort", "constant"]
      match afs.find? (·.1 == "sort"), afs.find? (·.1 == "constant") with
      | some (_, .str s), some (_, .str c) => pure (some (s, c))
      | _, _ => throw invalidBlock
  let definites ← match fs.find? (·.1 == "definites") with
    | none => pure []
    | some (_, d) => do
      let dfs ← match fields d with
        | .ok xs => pure xs
        | .error _ => throw invalidBlock
      dfs.mapM fun (p, c) => match c with
        | .str c => pure (p, c)
        | _ => throw invalidBlock
  unless definites.all (fun (p, _) => phraseOk p) do throw invalidBlock
  pure ⟨task, addressee, VE.Norms.sortBy (fun a b => decide (a.1 < b.1)) definites⟩

/-- The environment without the speech-act block and profile: the input of W1's decoder. -/
def stripSpeech (environment : Json) : Except String Json := do
  let profiles ← strings (← environment.getObjVal? "profiles")
  let fs ← fields environment
  pure ((Json.mkObj (fs.filter (·.1 != "speech_acts"))).setObjVal! "profiles"
    (toJson (profiles.filter (· != speechProfile))))

/-- The canonical environment (3.1, 3.5): W1's act normalisation, and the block replaced by its canonical
encoding. `environment_id` is computed over this with the environment's complete profile list. -/
def canonicalEnvironmentJson (environment : Json) : Except String Json := do
  let sc ← parseScope (← environment.getObjVal? "speech_acts")
  let c ← VE.Norms.Wire.canonicalEnvironmentJson environment
  let fs ← fields c
  pure (Json.obj ((Std.TreeMap.Raw.ofList (fs.filter (·.1 != "speech_acts")) compare).insert
    "speech_acts" (encodeScope sc)))

/-- The profile gate of 1.6, with the section 7 diagnostics. -/
def profileGate (profiles : List String) : Except String Unit := do
  unless decide (profiles.Pairwise (· < ·)) do
    throw (VE.Route.Gate.unsupported "profiles must be sorted and unique")
  unless profiles.contains speechProfile do throw "UnsupportedProfile: speech-acts@0 is required"
  unless profiles.contains "norms@0" do throw "UnsupportedProfile: speech-acts@0 requires norms@0"
  for p in profiles do
    unless allowlist.contains p do throw s!"UnsupportedProfile: speech-acts@0 with {p}"

/-- A decoded speech-act environment: W1's decoding of the stripped environment, the scope block, the original
profiles and JSON, and the canonical environment. -/
structure SpeechEnvironment where
  ne : VE.Norms.Wire.NormsEnvironment
  scope : Scope
  profiles : List String
  json : Json
  canonical : Json

def profilesField (environment : Json) : Except String (List String) :=
  match environment.getObjVal? "profiles" >>= strings with
  | .ok ps => pure ps
  | .error _ => throw (VE.Route.Gate.unsupported "profiles must be a sorted unique array")

def predicatesOf (environment : Json) : Except String (List (String × Json)) :=
  match environment.getObjVal? "vocabulary" >>= (·.getObjVal? "predicates") >>= fields with
  | .ok ps => pure ps
  | .error _ => throw "InvalidInput: environment vocabulary"

/-- W3 definitions and W5 flags are rejected with the route (1.6). -/
def checkDeclarations (preds : List (String × Json)) : Except String Unit :=
  preds.forM fun (_, e) => do
    if (e.getObjVal? "defined").isOk then throw "UnsupportedProfile: speech-acts@0 with definitions"
    if (e.getObjVal? "functional").isOk || (e.getObjVal? "total").isOk then
      throw "UnsupportedProfile: speech-acts@0 with data flags"

def blockOf (environment : Json) : Except String Json :=
  match environment.getObjVal? "speech_acts" with
  | .ok b => pure b
  | .error _ => throw invalidBlock

/-- A definite phrase is not a constant name, a sort noun or a keyword (1.1). -/
def checkPhrases (ne : VE.Norms.Wire.NormsEnvironment) (sc : Scope) : Except String Unit :=
  sc.definites.forM fun (p, _) => do
    let v := ne.rv.vocabulary
    if v.constants.any (·.1 == p) || v.sorts.contains p || VE.Norms.Wire.actReserved.contains p.toLower then
      throw invalidBlock

def decodeSpeechEnvironmentFull (environment : Json) : Except String SpeechEnvironment := do
  let profiles ← profilesField environment
  profileGate profiles
  let preds ← predicatesOf environment
  checkDeclarations preds
  let block ← blockOf environment
  let sc ← parseScope block
  let canonical ← canonicalEnvironmentJson environment
  let stripped ← stripSpeech environment
  let ne ← VE.Norms.Wire.decodeNormsEnvironment stripped
  checkPhrases ne sc
  pure ⟨ne, sc, profiles, environment, canonical⟩

/-- 8.5's signature: the complete environment, the scope and the validated regulated declarations. -/
def decodeSpeechEnvironment (environment : Json) :
    Except String (VE.Environment × Scope × List Regulated) :=
  (decodeSpeechEnvironmentFull environment).map (fun se => (se.ne.rv.environment, se.scope, se.ne.regulated))

/-! ## `scope_in_identity` -/

theorem getObjVal_insert (l : List (String × Json)) (k : String) (v : Json) :
    (Json.obj ((Std.TreeMap.Raw.ofList l compare).insert k v)).getObjVal? k = .ok v := by
  simp only [Json.getObjVal?]
  rw [Std.TreeMap.Raw.get?_eq_getElem?, Std.TreeMap.Raw.getElem?_insert_self Std.TreeMap.Raw.WF.ofList]
  rfl

theorem canonical_scope (environment b : Json) (sc : Scope)
    (hs : (environment.getObjVal? "speech_acts" >>= parseScope) = .ok sc)
    (h : canonicalEnvironmentJson environment = .ok b) : b.getObjVal? "speech_acts" = .ok (encodeScope sc) := by
  unfold canonicalEnvironmentJson at h
  obtain ⟨blk, hblk, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨sc', hsc', h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨c, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨fs, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  rw [hblk] at hs
  have : sc' = sc := by
    simp only [bind, Except.bind] at hs
    rw [hsc'] at hs
    cases hs; rfl
  subst this
  exact getObjVal_insert _ _ _

/-- The scope is in the canonical environment bytes (3.5). -/
theorem scope_in_identity (j : Json) (E : VE.Environment) (sc : Scope) (rs : List Regulated)
    (h : Wire.decodeSpeechEnvironment j = .ok (E, sc, rs)) :
    ∃ b : Json, (Wire.canonicalEnvironmentJson j).toOption = some b ∧
      b.getObjVal? "speech_acts" = .ok (Wire.encodeScope sc) := by
  unfold decodeSpeechEnvironment at h
  cases hf : decodeSpeechEnvironmentFull j with
  | error e => rw [hf] at h; cases h
  | ok se =>
    rw [hf] at h
    simp only [Except.map, Except.ok.injEq, Prod.mk.injEq] at h
    obtain ⟨_, rfl, _⟩ := h
    unfold decodeSpeechEnvironmentFull at hf
    obtain ⟨_, _, hf⟩ := VE.Order.ProfileGate.bind_ok hf
    obtain ⟨_, _, hf⟩ := VE.Order.ProfileGate.bind_ok hf
    obtain ⟨_, _, hf⟩ := VE.Order.ProfileGate.bind_ok hf
    obtain ⟨_, _, hf⟩ := VE.Order.ProfileGate.bind_ok hf
    obtain ⟨blk, hblk, hf⟩ := VE.Order.ProfileGate.bind_ok hf
    obtain ⟨sc', hsc', hf⟩ := VE.Order.ProfileGate.bind_ok hf
    obtain ⟨b, hb, hf⟩ := VE.Order.ProfileGate.bind_ok hf
    obtain ⟨_, _, hf⟩ := VE.Order.ProfileGate.bind_ok hf
    obtain ⟨_, _, hf⟩ := VE.Order.ProfileGate.bind_ok hf
    obtain ⟨_, _, hf⟩ := VE.Order.ProfileGate.bind_ok hf
    cases hf
    have hblk' : j.getObjVal? "speech_acts" = .ok blk := by
      unfold blockOf at hblk
      split at hblk
      · rename_i b hb; cases hblk; exact hb
      · cases hblk
    refine ⟨b, by rw [hb]; rfl, canonical_scope j b _ ?_ hb⟩
    rw [hblk']
    exact hsc'

/-! ## Units (3.2) -/

def encodeForce : Force → Json
  | .require => .str "require"
  | .forbid => .str "forbid"

def modeName : Mode → String
  | .polar => "polar"
  | .whichAll => "which_all"
  | .whichOne => "which_one"
  | .follows => "follows"
  | .reading => "reading"

def decodeMode : Json → Except String Mode
  | .str "polar" => pure .polar
  | .str "which_all" => pure .whichAll
  | .str "which_one" => pure .whichOne
  | .str "follows" => pure .follows
  | .str "reading" => pure .reading
  | _ => throw "InvalidInput: mode"

def encodeAnswer : Answer → Json
  | .yes => .str "yes"
  | .no => .str "no"
  | .one a => Json.mkObj [("one", .str a)]
  | .all S => Json.mkObj [("all", toJson S)]

def decodeAnswer (j : Json) : Except String Answer :=
  match j with
  | .str "yes" => pure .yes
  | .str "no" => pure .no
  | _ => match j.getObjVal? "one", j.getObjVal? "all" with
    | .ok (.str a), .error _ => pure (.one a)
    | .error _, .ok s => do pure (.all (← strings s))
    | _, _ => throw "InvalidInput: answer"

/-- Command content `{"force", "act", "args", "guard"?}` (3.2). -/
def decodeCommand (E : VE.Environment) (u : String) (j : Json) : Except String Command := do
  let bad := s!"InvalidInput: invalid command fields for {u}"
  match VE.Bridge.displayFields j ["force", "act", "args"] ["guard"] with
  | .ok () => pure ()
  | .error _ => throw bad
  let force ← match j.getObjValD "force" with
    | .str "require" => pure Force.require
    | .str "forbid" => pure Force.forbid
    | _ => throw "InvalidInput: force"
  let act ← match j.getObjValD "act" with
    | .str a => pure a
    | _ => throw bad
  let args ← match strings (j.getObjValD "args") with
    | .ok xs => pure xs
    | .error _ => throw bad
  let guard ← match j.getObjVal? "guard" with
    | .ok g => VE.Route.Wire.decodeClosed E g
    | .error _ => pure .top
  pure ⟨u, force, act, args, guard⟩

/-- Question content (3.2): `mode`, and per mode `body`, `sort`/`domain`, `query` or `set`/`version`. -/
def decodeQuestion (u : String) (j : Json) : Except String Question := do
  let bad := s!"InvalidInput: invalid question fields for {u}"
  let mode ← decodeMode (j.getObjValD "mode")
  let (required, optional) : List String × List String := match mode with
    | .polar => (["mode", "body"], [])
    | .whichAll | .whichOne => (["mode", "sort", "domain", "body"], [])
    | .follows => (["mode", "query"], [])
    | .reading => (["mode", "set", "version"], [])
  match VE.Bridge.displayFields j required optional with
  | .ok () => pure ()
  | .error _ => throw bad
  let body ← match mode with
    | .polar | .whichAll | .whichOne => VE.Bridge.decodeFormula 64 (j.getObjValD "body")
    | _ => pure .top
  let sort ← match mode with
    | .whichAll | .whichOne => match j.getObjValD "sort" with
      | .str s => pure (some s)
      | _ => throw bad
    | _ => pure none
  let domain ← match mode with
    | .whichAll | .whichOne => match strings (j.getObjValD "domain") with
      | .ok xs => pure xs
      | .error _ => throw bad
    | _ => pure []
  let query ← match mode with
    | .follows => match j.getObjValD "query" with
      | .str q => pure (some q)
      | _ => throw bad
    | _ => pure none
  let readingSet ← match mode with
    | .reading => match j.getObjValD "set", (j.getObjValD "version").getNat? with
      | .str s, .ok v => pure (some (s, v))
      | _, _ => throw bad
    | _ => pure none
  pure ⟨u, mode, body, sort, domain, query, readingSet⟩

/-- An authored binding: exactly one legend entry. -/
inductive Binding
  | you (constant : String)
  | phrase (phrase constant : String)
  | task (task : String)

def decodeBinding (u : String) (j : Json) : Except String Binding := do
  let bad := s!"InvalidInput: invalid binding fields for {u}"
  let fs ← match fields j with
    | .ok fs => pure fs
    | .error _ => throw bad
  match fs with
  | [("you", .str c)] => pure (.you c)
  | [("task", .str t)] => pure (.task t)
  | _ => match j.getObjValD "phrase", j.getObjValD "constant", fs.length with
    | .str p, .str c, 2 => if phraseOk p then pure (.phrase p c) else throw bad
    | _, _, _ => throw bad

/-- What a decoded unit contributes. -/
inductive Role
  | command (c : Command)
  | question (q : Question)
  | binding (b : Binding)
  | norm (n : Node)
  | asserted (φ : VE.Formula)
  | other

structure SpeechUnitInfo where
  id : String
  start : Nat
  stop : Nat
  /-- the rendered kind (P0's form, or `"binding"`) -/
  kind : Json
  meaning : Json
  role : Role
  /-- the latest version of the unit's W2 reading set is open (pending); an authored latest version has
  already supplied the chosen kind and content, and earlier versions are history -/
  pending : Bool := false

def contentTag (content : Json) : Option String :=
  match content with
  | .obj _ =>
    if (content.getObjVal? "command").isOk then some "command"
    else if (content.getObjVal? "question").isOk then some "question"
    else if (content.getObjVal? "binding").isOk then some "binding"
    else if (content.getObjVal? "norm").isOk then some "norm"
    else if (content.getObjVal? "ast").isOk then some "ast"
    else none
  | _ => none

/-- A meaning is `specified` when stated so or absent. -/
def specified (meaning : Json) : Bool := meaning == .null || meaning == .str "specified"

def decodeUnit (E : VE.Environment) (j : Json) : Except String SpeechUnitInfo := do
  VE.Bridge.displayFields j ["id", "span", "kind"] ["meaning", "support", "content"]
  let id ← stringField j "id"
  unless VE.Route.Admission.token id do throw s!"invalid unit id {id}"
  let (start, stop) ← match (← (← j.getObjVal? "span").getArr?).toList with
    | [a, b] => pure (← a.getNat?, ← b.getNat?)
    | _ => throw "invalid span"
  unless start ≤ stop do throw "invalid span"
  let kindJ ← j.getObjVal? "kind"
  let meaning := j.getObjValD "meaning"
  let content? := (j.getObjVal? "content").toOption
  if (meaning.getObjVal? "unformalised").isOk && content?.isSome then
    throw "unformalised unit cannot assert content"
  if kindJ == .str "binding" then
    let some content := content? | throw s!"InvalidInput: invalid binding fields for {id}"
    unless contentTag content == some "binding" do throw s!"InvalidInput: invalid binding fields for {id}"
    let b ← decodeBinding id (content.getObjValD "binding")
    return ⟨id, start, stop, kindJ, meaning, .binding b, false⟩
  let kind ← VE.Route.Admission.decodeKind 16 kindJ
  let role ← match content? with
    | none => pure Role.other
    | some content => match contentTag content with
      | some "command" =>
        if kind == .instruction || kind.quoted then
          pure (Role.command (← decodeCommand E id (content.getObjValD "command")))
        else throw "command content requires an instruction or quoted kind"
      | some "question" =>
        if kind == .question then pure (Role.question (← decodeQuestion id (content.getObjValD "question")))
        else if kind.quoted then do
          let _ ← decodeQuestion id (content.getObjValD "question")
          pure Role.other
        else throw "question content requires a question or quoted kind"
      | some "binding" => throw s!"InvalidInput: binding content requires the binding kind for {id}"
      | some "norm" =>
        if kind == .norm || kind.quoted then pure (Role.norm (← VE.Norms.Wire.decodeNorm content))
        else throw "norm content requires a norm or quoted kind"
      | tag =>
        -- A formula: the P0 route's bare AST, or W2's `{"ast": ...}`.
        let φ ← VE.Route.Wire.decodeClosed E (if tag == some "ast" then content.getObjValD "ast" else content)
        pure (if kind == .asserted then Role.asserted φ else Role.other)
  pure ⟨id, start, stop, VE.Route.Admission.renderKind kind, meaning, role, false⟩

/-- 1.2: a command unit is active exactly when its kind is `instruction`, its meaning `specified` and it is not
the source unit of a pending reading set (its slots are bound by `WellFormedSpeech`). Every other command unit
is dormant. -/
def activeCommand (u : SpeechUnitInfo) : Option Command :=
  match u.role with
  | .command c => if u.kind == .str "instruction" && specified u.meaning && !u.pending then some c else none
  | _ => none

/-- An author norm is active when its kind is `norm` and it is not pending (quoted norms are dormant). -/
def activeNorm (u : SpeechUnitInfo) : Option Node :=
  match u.role with
  | .norm n => if u.kind == .str "norm" && !u.pending then some n else none
  | _ => none

/-- W2's fixed asserted premises: asserted units with content, not pending (an authored singleton choice has
supplied its unit's content, 1.5). -/
def fixedAssertion (u : SpeechUnitInfo) : Option (String × VE.Formula) :=
  match u.role with
  | .asserted φ => if !u.pending then some (u.id, φ) else none
  | _ => none

/-- What one W2 reading-set version says about its source unit: still `open` (pending), or the author's
signed singleton choice with the chosen reading's kind and content (`none` while unelaborated). -/
inductive ReadingState
  | pending
  | authored (kind : Json) (content : Option Json)

def readingSetsError : String :=
  "InvalidInput: reading sets on the speech-acts route need their unit, version and status"

/-- The author's signature of an authored version: a W2 token. -/
def signed (r : Json) : Bool :=
  match r.getObjVal? "signature" with
  | .ok (.str s) => VE.Route.Admission.token s
  | _ => false

/-- The W2 reading-set versions of a document (`ve/readings.py`: `unit`, `version`, `status`, and the one
reading of an authored version), one entry per version. Only a signed version is a choice: an authored version
without the author's signature token, or an open one carrying one, is rejected as by W2's
`validate_reading_sets`. -/
def readingStates (document : Json) : Except String (List (String × Nat × ReadingState)) := do
  match document.getObjVal? "reading_sets" with
  | .error _ => pure []
  | .ok rs =>
    let items ← match rs.getArr? with
      | .ok xs => pure xs.toList
      | .error _ => throw readingSetsError
    let states ← items.mapM fun r => do
      match r.getObjVal? "unit", (r.getObjValD "version").getNat?, r.getObjVal? "status" with
      | .ok (.str _), .ok 0, .ok (.str "open") | .ok (.str _), .ok 0, .ok (.str "authored") =>
        throw "invalid or duplicate reading set version"
      | .ok (.str u), .ok v, .ok (.str "open") =>
        if (r.getObjVal? "signature").isOk then throw "open reading set cannot have an author signature"
        pure (u, v, ReadingState.pending)
      | .ok (.str u), .ok v, .ok (.str "authored") =>
        match (r.getObjValD "readings").getArr? with
        | .ok #[c] =>
          unless (c.getObjVal? "kind").isOk && (c.getObjVal? "content").isOk && signed r do
            throw "authored reading needs one signed choice"
          let content := match c.getObjValD "content" with
            | .null => none
            | x => some x
          pure (u, v, ReadingState.authored (c.getObjValD "kind") content)
        | _ => throw "authored reading needs one signed choice"
      | _, _, _ => throw readingSetsError
    let keys := states.map (fun (u, v, _) => (u, v))
    unless keys.eraseDups.length == keys.length do throw "invalid or duplicate reading set version"
    pure states

/-- 1.2 and 1.5: the latest version of a unit's reading set decides (W2's `active_reading_sets`); earlier
versions are history. -/
def latestState (states : List (String × Nat × ReadingState)) (u : String) : Option ReadingState :=
  let mine := states.filter (·.1 == u)
  match (mine.map (·.2.1)).max? with
  | none => none
  | some v => (mine.find? (·.2.1 == v)).map (·.2.2)

/-- The unit as its latest reading set leaves it: an authored choice supplies the kind, a specified meaning
and the content (W2's formula-only assertion candidates are bare ASTs, which `decodeUnit` reads). -/
def chosenUnit (j : Json) (kind : Json) (content : Option Json) : Except String Json := do
  let fs ← fields j
  let kept := fs.filter (fun kv => kv.1 != "kind" && kv.1 != "meaning" && kv.1 != "content")
  pure (Json.mkObj (kept ++ [("kind", kind), ("meaning", .str "specified")] ++
    match content with
    | some c => [("content", c)]
    | none => []))

/-- Decode one unit under the document's reading sets. -/
def decodeUnitIn (E : VE.Environment) (states : List (String × Nat × ReadingState)) (j : Json) :
    Except String SpeechUnitInfo := do
  let id := match j.getObjValD "id" with
    | .str i => i
    | _ => ""
  match latestState states id with
  | some .pending => pure { (← decodeUnit E j) with pending := true }
  | some (.authored kind content) => decodeUnit E (← chosenUnit j kind content)
  | none =>
    if j.getObjValD "kind" == .str "asserted" && !(j.getObjVal? "content").isOk &&
        !states.any (·.1 == id) then
      throw "asserted unit needs content or a reading set"
    decodeUnit E j

/-- A query record `{"id", "premises", "target": {"ast"}}` (3.2), before regeneration. -/
def decodeQuery (E : VE.Environment) (j : Json) : Except String (String × List String × VE.Formula) := do
  exactFields j ["id", "premises", "target"]
  let id ← stringField j "id"
  let premises ← strings (← j.getObjVal? "premises")
  let t ← j.getObjVal? "target"
  exactFields t ["ast"]
  pure (id, premises, ← VE.Route.Wire.decodeClosed E (← t.getObjVal? "ast"))

/-! ## The document -/

/-- Merge the authored bindings into the environment's scope (1.1). -/
def mergeBindings (E : VE.Environment) (sc : Scope) : List Binding → Except String Scope
  | [] => pure sc
  | b :: bs => do
    let sc' ← match b with
      | .task t => if t == sc.task then pure sc else throw "BindingConflict: task"
      | .you c => match sc.addressee with
        | some (_, c') => if c == c' then pure sc else throw "BindingConflict: you"
        | none => match E.constants c with
          | some s => pure { sc with addressee := some (s, c) }
          | none => throw s!"UnknownSymbol: {c}"
      | .phrase p c => match sc.definites.find? (·.1 == p) with
        | some (_, c') => if c == c' then pure sc else throw s!"BindingConflict: {p}"
        | none =>
          let ds := VE.Norms.sortBy (fun a b => decide (a.1 < b.1)) ((p, c) :: sc.definites)
          pure { sc with definites := ds }
    mergeBindings E sc' bs

/-- The single-binding checks of a binding that is not merged (a pending unit's or a candidate's), as the block's
own entry: a task token, a declared constant, a phrase that `checkPhrases` accepts. -/
def checkBinding (ne : VE.Norms.Wire.NormsEnvironment) : Binding → Except String Unit
  | .task t => unless VE.Route.Admission.token t do throw invalidBlock
  | .you c => unless (ne.rv.environment.constants c).isSome do throw s!"UnknownSymbol: {c}"
  | .phrase p c => do
    checkPhrases ne ⟨"t", none, [(p, c)]⟩
    unless (ne.rv.environment.constants c).isSome do throw s!"UnknownSymbol: {c}"

def bindingKey : Binding → String
  | .you _ => "you"
  | .phrase p _ => p
  | .task _ => "task"

/-! ## Reading candidates (6) -/

/-- Every reading of every reading-set version: its unit, kind and content (`none` while unelaborated), in W2's
shape (1 to 64 readings, each with its kind and content). -/
def readingCandidates (document : Json) : Except String (List (String × Json × Option Json)) := do
  match document.getObjVal? "reading_sets" with
  | .error _ => pure []
  | .ok rs =>
    let items ← match rs.getArr? with
      | .ok xs => pure xs.toList
      | .error _ => throw readingSetsError
    let per ← items.mapM fun r => do
      let u := match r.getObjValD "unit" with
        | .str u => u
        | _ => ""
      let cs ← match (r.getObjValD "readings").getArr? with
        | .ok cs => if 1 ≤ cs.size && cs.size ≤ 64 then pure cs.toList else throw "reading sets hold 1 to 64 readings"
        | .error _ => throw "reading sets hold 1 to 64 readings"
      cs.mapM fun c => do
        unless (c.getObjVal? "kind").isOk && (c.getObjVal? "content").isOk do throw "invalid reading"
        pure (u, c.getObjValD "kind", match c.getObjValD "content" with
          | .null => none
          | x => some x)
    pure per.flatten

/-- The bare kind of a kind: itself, or the last element of a nested one. -/
def bareKind : Json → Option String
  | .str k => some k
  | .arr xs => match xs.back? with
    | some (.str k) => some k
    | _ => none
  | _ => none

/-- The bare kind each tagged content belongs to (W2's kinds, and `binding`). -/
def candidateKind : String → Option String
  | "ast" => some "asserted"
  | "norm" => some "norm"
  | "command" => some "instruction"
  | "question" => some "question"
  | "binding" => some "binding"
  | _ => none

/-- A candidate command's single-unit checks: the realising predicate, its role and the argument sorts after the
addressee's slot, and the guard. A candidate is never active, so the addressee is not required. -/
def checkCandidateCommand (se : SpeechEnvironment) (c : Command) : Except String Unit := do
  let E := se.ne.rv.environment
  let r ← match se.ne.regulated.find? (·.name == c.act), E.predicates c.act with
    | some r, _ => pure r
    | none, some _ => throw s!"Missing{if c.force = .require then "Obligation" else "Permission"}Role: {c.act}"
    | none, none => throw s!"UnknownSymbol: regulated predicate {c.act}"
  if c.force = .require && r.role != .obligation then throw s!"MissingObligationRole: {r.act.getD c.act}"
  if c.force = .forbid && r.role != .permission then throw s!"MissingPermissionRole: {r.act.getD c.act}"
  unless E.predicates c.act == some r.sorts && constsTyped E c.args r.sorts.tail do
    throw s!"TypeMismatch: command args for {c.unit}"
  VE.Norms.typeDiagnostic E [] c.guard
  unless c.guard.check E [] do throw s!"InvalidInput: invalid command fields for {c.unit}"

/-- One reading candidate of unit `u`, checked as the unit would be were it chosen (6): its kind, its content of
that kind (a malformed candidate is rejected, never counted; `none` is unelaborated), and the query it asks about,
if any, which is regenerated at `u` (1.4). -/
def checkCandidate (se : SpeechEnvironment) (scope : Scope) (u : String) (kind : Json) (content? : Option Json) :
    Except String (Option String) := do
  let E := se.ne.rv.environment
  let bad := "invalid speech reading content"
  unless kind == .str "binding" do
    let _ ← VE.Route.Admission.decodeKind 16 kind
  let some content := content? | return none
  let (tag, value) ← match content with
    | .arr _ => pure ("ast", content)
    | .obj _ => match fields content with
      | .ok [(t, v)] => pure (t, v)
      | _ => throw bad
    | _ => throw bad
  unless (candidateKind tag).isSome && bareKind kind == candidateKind tag do throw bad
  match tag with
  | "ast" =>
    let _ ← VE.Route.Wire.decodeClosed E value
    pure none
  | "command" =>
    let c ← decodeCommand E u value
    checkCandidateCommand se c
    pure (match E.predicates c.act with
      | some (_ :: ss) => ((ss.zip c.args).find? (·.1 == "query")).map Prod.snd
      | _ => none)
  | "question" =>
    let q ← decodeQuestion u value
    if q.mode == .follows then return q.query
    if q.mode == .reading && u.utf8ByteSize > 47 then throw "ResourceLimit: open-term name"
    validateSpeech ⟨E, se.ne.rv.literals, scope, se.ne.regulated, [], [], [q], [], []⟩
    pure none
  | "norm" =>
    let n ← VE.Norms.Wire.decodeNorm content
    VE.Norms.validate ⟨E, se.ne.rv.literals, ⟨se.ne.regulated, [], [{ n with over := [] }]⟩⟩
    pure none
  | _ =>
    checkBinding se.ne (← decodeBinding u value)
    pure none

/-- The unit that asks about a query: a follows question or a proof-task command (a slot of sort `query`). -/
def queryOf (E : VE.Environment) (u : SpeechUnitInfo) : Option String :=
  match u.role with
  | .question q => if q.mode == .follows then q.query else none
  | .command c => match E.predicates c.act with
    | some (_ :: ss) => ((ss.zip c.args).find? (·.1 == "query")).map Prod.snd
    | _ => none
  | _ => none

/-- A decoded speech-act document: its environment, units and the well-formed semantic core. -/
structure Decoded where
  se : SpeechEnvironment
  units : List SpeechUnitInfo
  D : SpeechDoc
  wf : WellFormedSpeech D = true
  env : D.E = se.ne.rv.environment
  lits : D.lits = se.ne.rv.literals
  commands_eq : D.commands = units.filterMap activeCommand
  norms_eq : D.norms = units.filterMap activeNorm
  asserted_eq : D.asserted = units.filterMap fixedAssertion

def decodeDocument (environment document : Json) : Except String Decoded := do
  let se ← decodeSpeechEnvironmentFull environment
  let E := se.ne.rv.environment
  VE.Bridge.displayFields document ["units"]
    ["queries", "answers", "compliance", "graph", "lemmas", "open_terms", "reading_sets", "narrowings"]
  let states ← readingStates document
  let units ← (← (← document.getObjVal? "units").getArr?).toList.mapM (decodeUnitIn E states)
  unless units.length ≤ 10000 do throw "ResourceLimit: unit count"
  unless (units.map (·.id)).eraseDups.length == units.length do throw "duplicate unit id"
  unless states.all (fun s => units.any (·.id == s.1)) do throw "invalid reading set unit or status"
  unless VE.Route.Admission.sortedSpans (units.map (fun u => ⟨u.id, u.start, u.stop, .asserted, none⟩)) do
    throw "unit spans must be sorted and non-overlapping"
  -- Authored bindings (1.1). A binding unit whose reading set is open is pending (1.5): it supplies no entry
  -- and declares nothing, and keeps its single-binding checks.
  for u in units do
    if let .binding b := u.role then
      if u.pending then checkBinding se.ne b
  let bindings := units.filterMap (fun u => match u.role with
    | .binding b => if u.pending then none else some b
    | _ => none)
  let keys := bindings.map bindingKey
  if let some k := keys.find? (fun k => keys.count k > 1) then
    throw s!"DuplicateDeclaration: binding {k}"
  let scope ← mergeBindings E se.scope bindings
  checkPhrases se.ne scope
  -- 1.1 and 3.5: a binding that supplies a scope entry supplies it to the canonical environment, so the
  -- environment id every meaning id and certificate binds is the effective scope's.
  let se := { se with scope, canonical := se.canonical.setObjVal! "speech_acts" (encodeScope scope) }
  -- Reading questions: the derived open-term meaning (4.6).
  for u in units do
    if let .question q := u.role then
      if q.mode == .reading then
        if u.id.utf8ByteSize > 47 then throw "ResourceLimit: open-term name"
        unless u.meaning == Json.mkObj [("open", Json.arr #[.str ("intended-reading." ++ u.id)])] do
          throw s!"InvalidInput: invalid question fields for {u.id}"
  let asserted := units.filterMap fixedAssertion
  let norms := units.filterMap activeNorm
  let commands := units.filterMap activeCommand
  let questions := units.filterMap (fun u => match u.role with | .question q => some q | _ => none)
  -- Quoted norms and dormant commands keep every single-unit check.
  for u in units do
    match u.role with
    | .norm n =>
      if (activeNorm u).isNone then
        VE.Norms.validate ⟨E, se.ne.rv.literals, ⟨se.ne.regulated, [], [{ n with over := [] }]⟩⟩
    | .command c =>
      if (activeCommand u).isNone && (specified u.meaning || !(u.kind == .str "instruction")) then
        validateSpeech ⟨E, se.ne.rv.literals, scope, se.ne.regulated, [], [c], [], [], []⟩
    | _ => pure ()
  -- Query records (1.4): derived, compared with the regeneration at every unit that asks.
  let rawQueries ← match document.getObjVal? "queries" with
    | .ok q => (← q.getArr?).toList.mapM (decodeQuery E)
    | .error _ => pure []
  unless (rawQueries.map (·.1)).eraseDups.length == rawQueries.length do throw "InvalidInput: duplicate query"
  -- Reading candidates (6), each checked as its unit would be were it chosen; one that asks about a query is a
  -- consumer at its unit.
  let mut candidateAsks : List (String × String) := []
  for (u, kind, content?) in ← readingCandidates document do
    if let some qid ← checkCandidate se scope u kind content? then candidateAsks := candidateAsks ++ [(u, qid)]
  let mut before : List String := []
  let mut asked : List String := []
  for u in units do
    for qid in (queryOf E u).toList ++ (candidateAsks.filter (·.1 == u.id)).map Prod.snd do
      match rawQueries.find? (·.1 == qid) with
      | none => throw s!"QueryMismatch: {u.id}"
      | some (_, ids, _) => unless ids == before do throw s!"QueryMismatch: {u.id}"
      asked := qid :: asked
    if (fixedAssertion u).isSome then before := before ++ [u.id]
  -- A record no unit asks about cannot be regenerated from the document (1.4).
  if let some (qid, _, _) := rawQueries.find? (fun q => !asked.contains q.1) then
    throw s!"QueryMismatch: {qid}"
  let queries := rawQueries.map (fun (id, ids, t) =>
    ({ id, premiseIds := ids, premises := (asserted.filter (fun a => a.1 ∈ ids)).map Prod.snd, target := t } : Query))
  let D : SpeechDoc := ⟨E, se.ne.rv.literals, scope, se.ne.regulated, norms, commands, questions, queries, asserted⟩
  match hv : validateSpeech D with
  | .error e => throw e
  | .ok () => pure ⟨se, units, D, by unfold WellFormedSpeech; rw [hv], rfl, rfl, rfl, rfl, rfl⟩

/-- Which units are active (1.2), for the decoded document: a command is in the semantic core exactly when some
unit of kind `instruction` with `specified` meaning, not the source of a pending reading set, carries it. -/
theorem decoded_active_commands (dec : Decoded) (c : Command) :
    c ∈ dec.D.commands ↔ ∃ u ∈ dec.units, u.role = .command c ∧ (u.kind == .str "instruction") = true ∧
      specified u.meaning = true ∧ u.pending = false := by
  rw [dec.commands_eq, List.mem_filterMap]
  constructor
  · rintro ⟨u, hu, ha⟩
    unfold activeCommand at ha
    split at ha
    · rename_i c' hr
      split at ha
      · rename_i hc
        cases ha
        simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
        exact ⟨u, hu, hr, hc.1.1, hc.1.2, hc.2⟩
      · cases ha
    · cases ha
  · rintro ⟨u, hu, hr, hk, hs, hp⟩
    refine ⟨u, hu, ?_⟩
    simp [activeCommand, hr, hk, hs, hp]

/-- Questions, bindings, answer and compliance records and dormant units reach no premise: the premises of the
decoded document are regenerated from its active norms, active commands and fixed assertions alone. -/
theorem decoded_premises (dec : Decoded) :
    premises dec.D = background (policy dec.D) ++ elaborate (policy dec.D).T ++
      (dec.units.filterMap fixedAssertion).map Prod.snd ∧
    (policy dec.D).T.nodes = dec.units.filterMap activeNorm ++ (dec.units.filterMap activeCommand).map (demand dec.D) := by
  refine ⟨by rw [premises, assertedFormulas, dec.asserted_eq], by rw [policy_nodes, dec.norms_eq, dec.commands_eq]⟩

end VE.SpeechActs.Wire
