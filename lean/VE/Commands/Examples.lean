import VE.Commands.Read
import VE.EnglishGrammar.E2Examples

/-! The fixtures of docs/spec/commands-imperatives.md section 5: the W rows over `E_web`
(F0's rows and the other 50 web segments are ci-1b's), and each limit at its boundary. -/

namespace VE.Commands.Examples

open Lean (Json)
open VE.SpeechActs.Wire (SpeechEnvironment decodeSpeechEnvironmentFull readingsBound)
open VE.EnglishGrammar (Env Lexicon TranslateOutcome workBudget)

def sortEntry (s : String) : String × Json := (s, Json.mkObj [("description", .str s)])

def constEntry (c : String × String) : String × Json :=
  (c.1, Json.mkObj [("sort", .str c.2), ("description", .str c.1)])

/-- A predicate; a regulated one carries its role and act. -/
def predEntry (name : String) (args : List String) (role : Option (String × String)) (word : Option String := none) :
    String × Json :=
  (name, Json.mkObj ([("arguments", Lean.toJson args), ("description", .str name)] ++
    (word.toList.map fun w => ("verbalisation", .str w)) ++
    (role.toList.map fun (r, act) => ("regulated", Json.mkObj
      [("role", .str r), ("default", .str (if r == "obligation" then "deny" else "allow")), ("act", .str act)]))))

def obligation (name : String) (args : List String) (act : String) : String × Json :=
  predEntry name args (some ("obligation", act))

def permission (name : String) (args : List String) (act : String) : String × Json :=
  predEntry name args (some ("permission", act))

def envOf (sorts : List String) (preds : List (String × Json)) (consts : List (String × String))
    (task : String) (you : Option (String × String)) (definites : List (String × String)) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("profiles", Lean.toJson ["norms@0", "relational-fol@0", "speech-acts@0"]),
    ("speech_acts", Json.mkObj ([("task", .str task), ("definites", Json.mkObj (definites.map fun (p, c) => (p, .str c)))] ++
      (you.toList.map fun (s, c) => ("addressee", Json.mkObj [("sort", .str s), ("constant", .str c)])))),
    ("vocabulary", Json.mkObj [("sorts", Json.mkObj (sorts.map sortEntry)), ("predicates", Json.mkObj preds),
      ("constants", Json.mkObj (consts.map constEntry))])]

/-- english-lean's environment and the lexicon Python's producer selects, with one letter per sort. -/
def lexOf (j : Json) : Except String (Env × Lexicon) := do
  let E ← Env.decode (← VE.Compose.decidingEnvironment j) (Json.mkObj [])
  let L := VE.EnglishGrammar.E2Examples.portLex E
  pure (E, { L with letters := E.sorts.zipIdx.map fun (s, i) => (s.name, s!"{Char.ofNat (65 + i)}") })

/-- A wording read over the environment `j` and its own scope. A fixture that does not decode is its error. -/
def read (j : Json) (s : String) (b : Nat := workBudget) : Outcome :=
  match decodeSpeechEnvironmentFull j, lexOf j with
  | .ok se, .ok (E, L) => readCommand se se.scope E L b s
  | .error e, _ | _, .error e => .refused "fixture" e

def actsWeb : List (String × Json) :=
  [obligation "click_check_required" ["user"] "{0} click Check rule conflict",
   obligation "click_review_required" ["user"] "{0} click Review meaning",
   obligation "click_ask_required" ["user"] "{0} click Ask",
   obligation "choose_vocabulary_required" ["user"] "{0} choose a listed rule vocabulary",
   obligation "choose_revision_required" ["user"] "{0} choose a unit revision to restore",
   obligation "use_required" ["user", "control"] "{0} use {1}",
   obligation "check_required" ["user", "ledger"] "{0} check {1}",
   obligation "write_required" ["user", "text"] "{0} write {1} as a statement",
   obligation "review_required" ["user", "text"] "{0} review {1}",
   obligation "review_meaning_required" ["user"] "{0} review the meaning",
   permission "share_permitted" ["user", "token"] "{0} share {1}",
   predEntry "approved" ["reading"] none (some "{0} is approved")]

def definitesWeb : List (String × String) :=
  [("the document assistant control", "assistant"), ("the meaning", "meaning1"),
   ("the private server calls ledger", "calls"), ("the question", "question1"), ("the token", "token1")]

/-- `E_web` (section 5), with its addressee and definites to vary. -/
def webWith (you : Option (String × String)) (definites : List (String × String)) : Json :=
  envOf ["user", "control", "ledger", "text", "reading", "token"] actsWeb
    [("reader", "user"), ("draft", "reading"), ("assistant", "control"), ("calls", "ledger"),
     ("question1", "text"), ("meaning1", "text"), ("token1", "token")]
    "webapp-copy" you definites

def E_web : Json := webWith (some ("user", "reader")) definitesWeb

def web (s : String) (b : Nat := workBudget) : Outcome := read E_web s b

def approvedDraft : VE.Formula := .unary "approved" (.const "draft")


def noReadingOutcome : Outcome := .ofText Texts.noReading

/-! ## W1 to W9: the rows that read -/

#guard web "Click Check rule conflict." == .one ⟨.require, "click_check_required", [], .top⟩
#guard web "Click Review meaning." == .one ⟨.require, "click_review_required", [], .top⟩
#guard web "Choose a listed rule vocabulary." == .one ⟨.require, "choose_vocabulary_required", [], .top⟩
#guard web "Choose a unit revision to restore." == .one ⟨.require, "choose_revision_required", [], .top⟩
#guard web "Use the document assistant control." ==
  .one ⟨.require, "use_required", [⟨"assistant", "the document assistant control"⟩], .top⟩
#guard web "Check the private server calls ledger." ==
  .one ⟨.require, "check_required", [⟨"calls", "the private server calls ledger"⟩], .top⟩
#guard web "Write the question as a statement." ==
  .one ⟨.require, "write_required", [⟨"question1", "the question"⟩], .top⟩
#guard web "Click Check rule conflict, if draft is approved." ==
  .one ⟨.require, "click_check_required", [], approvedDraft⟩
#guard web "Do not share the token." == .one ⟨.forbid, "share_permitted", [⟨"token1", "the token"⟩], .top⟩

/-! ## W10: two act matches, both kept; W11 to W15, refused -/

#guard web "Review the meaning." == .many
  [⟨.require, "review_meaning_required", [], .top⟩,
   ⟨.require, "review_required", [⟨"meaning1", "the meaning"⟩], .top⟩]
#guard web "Click Use this wording under the one you mean." == noReadingOutcome
#guard web "Choose authoring or translation mode." == noReadingOutcome
#guard web "Open “Vocabulary & small world” to fix it." == .refused "InvalidInput" "non-ASCII speech wording"
#guard web "Then click Ask." == noReadingOutcome
#guard web "You may close the desk." == .refused "PermissionNotCommand" "use an equality-guarded W1 rule"
#guard "InvalidInput: " ++ Texts.nonAscii.2 == VE.SpeechActs.Wire.nonAsciiWording

/-! ## W17: the decision on a constructed outcome; no condition over `E_web` has two derivations -/

def se0 : Option SpeechEnvironment := (decodeSpeechEnvironmentFull E_web).toOption
def lex0 : Except String (Env × Lexicon) := lexOf E_web

/-- A translation of two readings; `complete` says whether the set is whole. -/
def twoReadings (complete : Bool) : TranslateOutcome :=
  let r := (VE.EnglishGrammar.EFormula.pred "approved" [.const "draft"], false, VE.EnglishGrammar.DState.init)
  .readings [r, (.not r.1, false, r.2.2)] complete

#guard match se0, lex0 with
  | some se, .ok (E, L) =>
    (match guardOfOutcome se E L "c" (twoReadings true) with
      | .error (.ambiguous gs) => gs == [approvedDraft, .not approvedDraft]
      | _ => false) &&
    (match guardOfOutcome se E L "c" (twoReadings false) with
      | .error .limit => true
      | _ => false)
  | _, _ => false

/-! ## W17 over a real lexicon: V4 lets modal predicates share a form, so a condition can have two derivations -/

/-- An environment whose two obligations give the modal form of `reader must go`, in the sorts and spellings given. -/
def goEnv (a b : String × String × String) : Json :=
  envOf ["user", "service", "reading"]
    [obligation a.1 [a.2.1] a.2.2, obligation b.1 [b.2.1] b.2.2, obligation "click_ask_required" ["user"] "{0} click Ask"]
    [("reader", "user"), ("bot", "service"), ("draft", "reading")] "t" (some ("user", "reader")) []

/-- The act in two sorts (S3's case): both readings derive, and the one of the other sort does not decode. -/
def goSorts : Json := goEnv ("go_user_required", "user", "{0} go") ("go_service_required", "service", "{0} go")

/-- The act in one sort, in two spellings the wire keeps apart: both readings derive and both decode, two guards. -/
def goCase : Json := goEnv ("go_a_required", "user", "{0} go") ("go_b_required", "user", "{0} Go")

/-- Whether `j`'s lexicon passes V1 to V5 and the sentence `reader must go.` has two derivations, the set whole. -/
def derivesTwo (j : Json) : Bool :=
  match lexOf j with
  | .ok (E, L) =>
    VE.EnglishGrammar.Lexicon.valid E {} L &&
    match VE.EnglishGrammar.translateRequest E {} L maxCandidates workBudget "reader must go." with
    | .readings rs complete => rs.length == 2 && complete
    | _ => false
  | .error _ => false

#guard derivesTwo goSorts
#guard read goSorts "Click Ask, if reader must go." ==
  .refused "IllTyped" "The condition was read, and its formula does not pass the type check."

def goA : VE.Formula := .unary "go_a_required" (.const "reader")
def goB : VE.Formula := .unary "go_b_required" (.const "reader")

#guard derivesTwo goCase
#guard match decodeSpeechEnvironmentFull goCase, lexOf goCase with
  | .ok se, .ok (E, L) => guardsOf se E L workBudget "reader must go" == [goA, goB]
  | _, _ => false
#guard read goCase "Click Ask, if reader must go." ==
  .many [⟨.require, "click_ask_required", [], goA⟩, ⟨.require, "click_ask_required", [], goB⟩]

/-! ## W18 to W30 -/

#guard web "Click Check rule conflict, if draft is approved." 0 == .limit
#guard web "Click Check rule conflict, if draft is approvable." == .refused "NoDerivation"
  "The condition has no reading with the current vocabulary. Unknown English phrase 'is approvable'. Nearest declared wordings: 'is approved'; 'assistant'; 'calls'."
#guard web "Click Check rule conflict, if the reading is approved." == .refused "NoDerivation"
  "The condition has no reading with the current vocabulary. Unknown English phrase 'the reading'. Nearest declared wordings: 'reading'; '\"meaning1\"'; 'reader'."
#guard web "Click Check rule conflict, if Draft is approved." ==
  .one ⟨.require, "click_check_required", [], approvedDraft⟩
#guard web "Do not click Ask." == .refused "MissingPermissionRole" "{0} click Ask"
#guard web "Share the token." == .refused "MissingObligationRole" "{0} share {1}"
#guard web "Please click Ask." == .refused "InvalidInput" "please needs author approval"
#guard web "Click Ask and Review meaning." == .refused "CoordinatedActs" "split into two commands"
#guard web "Do not click Ask and Review meaning." == noReadingOutcome
#guard web "  click ask.  " == .one ⟨.require, "click_ask_required", [], .top⟩
#guard web "Click  Ask." == noReadingOutcome
#guard web "Click Ask" == noReadingOutcome
#guard web "" == .refused "InvalidInput" "speech wording"
#guard web "   " == .refused "InvalidInput" "speech wording"

/-! ## Section 4's rows 6 and 7, S33's first match per constants -/

#guard read (webWith none definitesWeb) "Click Ask." == .refused "UnboundSlot" "you"
#guard read (webWith (some ("control", "assistant")) definitesWeb) "Click Ask." == .refused "TypeMismatch" "addressee"
#guard read (webWith (some ("user", "reader")) [("the Token", "token1"), ("the token", "token1")])
    "Do not share the token." == .one ⟨.forbid, "share_permitted", [⟨"token1", "the Token"⟩], .top⟩

/-! ## W31: `manyOf` on constructed lists; every limit at its boundary -/

def nReadings (n : Nat) : List Reading := (List.range n).map fun i => ⟨.require, s!"a{i}", [], .top⟩

#guard manyOf (nReadings 2) == .many (nReadings 2)
#guard manyOf (nReadings readingsBound) == .many (nReadings readingsBound)
#guard manyOf (nReadings (readingsBound + 1)) == .limit
#guard readingsBound == 64

/-- "Click Ask" with a final condition of spaces, `n` bytes in all. -/
def wordingOf (n : Nat) : String := "Click Ask," ++ String.mk (List.replicate (n - 11) ' ') ++ "."

#guard (wordingOf 400).utf8ByteSize == 400 && (wordingOf 401).utf8ByteSize == 401
#guard web (wordingOf 400) == noReadingOutcome
#guard web (wordingOf 401) == .limit

/-- 63 acts over 65 constants of `text` and one act over `n` constants of `mark`: `4095 + n` fill tuples, within the
decoder's 64 regulated predicates. -/
def envWith (n : Nat) : Json :=
  envOf ["user", "text", "mark"]
    (obligation "mark_required" ["user", "mark"] "{0} mark {1}" ::
      (List.range 63).map fun i =>
        let verb := s!"w{Char.ofNat (97 + i / 26)}{Char.ofNat (97 + i % 26)}"
        obligation s!"{verb}_required" ["user", "text"] s!"\{0} {verb} \{1}")
    (("reader", "user") :: (List.range 65).map (fun i => (s!"t{i}", "text")) ++
      (List.range n).map fun i => (s!"m{i}", "mark"))
    "webapp-copy" (some ("user", "reader")) []

def tuplesOf (j : Json) : Nat :=
  match decodeSpeechEnvironmentFull j with
  | .ok se => tupleCount se se.scope
  | .error _ => 0

#guard tuplesOf E_web == 20
#guard tuplesOf (envWith 1) == maxCandidates
#guard read (envWith 1) "Wah t7." == .one ⟨.require, "wah_required", [⟨"t7", "t7"⟩], .top⟩
#guard tuplesOf (envWith 2) == maxCandidates + 1
#guard read (envWith 2) "Wah t7." == .limit

/-! ## `readCommand_typed_of_facts`' hypothesis holds of the fixtures' decoded environments -/

#guard [E_web, envWith 1].all fun j => match decodeSpeechEnvironmentFull j with
  | .ok se => declared se
  | .error _ => false

/-! ## Each value read once, and within its limit: with no act match the condition is not read; with two, section 4's
row 11; a very large wording stops at the first limit -/

#guard match se0, lex0 with
  | some se, .ok (E, L) =>
    match conditionOf se E L 0 ⟨.require, "x", some "draft is approved"⟩ [] with
    | .ok .top => true
    | _ => false
  | _, _ => false
#guard web "Click nothing, if draft is approved." 0 == noReadingOutcome
#guard web "Review the meaning, if draft is approved." 0 == .ofText Texts.actsMatch
#guard web (String.mk (List.replicate 100000 'a')) == .limit

/-! ## The tables a later row reads -/

#guard Texts.limitText == "VE stopped reading this command at its work limit."
#guard Texts.classOf "UnboundSlot" == some "VEError" && Texts.classOf "NoDerivation" == some "SyntaxError" &&
  Texts.classOf "absent" == none
#guard match se0, lex0 with
  | some se, .ok (E, L) => guardsOf se E L workBudget "draft is approved" == [approvedDraft] &&
      guardsOf se E L 0 "draft is approved" == []
  | _, _ => false

/-! ## What a mutant of the reader changes (docs/commands-imperatives/ci-1/trust-mutants.json) -/

/-- Three constants named alike under folding, one of them twice; acts with another slot 0, no role, no verb. -/
def extraEnv : Json :=
  envOf ["user", "service", "reading", "token"]
    [permission "share_permitted" ["user", "token"] "{0} share {1}", obligation "aa_required" ["service"] "{0} aa",
     obligation "bb_required" ["user"] "{0} bb", obligation "bare_required" ["user", "token"] "{0} {1}",
     ("seen", Json.mkObj [("arguments", Lean.toJson ["user"]), ("description", .str "seen"),
       ("regulated", Json.mkObj [("role", .str "plain"), ("default", .str "deny")])]),
     predEntry "approved" ["reading"] none (some "{0} is approved")]
    [("reader", "user"), ("atlas", "service"), ("draft", "reading"), ("c1", "token"), ("c2", "token"), ("c3", "token")]
    "webapp-copy" (some ("user", "reader"))
    [("the TOKEN", "c1"), ("the Token", "c2"), ("the tOken", "c3"), ("the token", "c3")]

#guard read extraEnv "Do not share the token." == .many
  [⟨.forbid, "share_permitted", [⟨"c1", "the TOKEN"⟩], .top⟩, ⟨.forbid, "share_permitted", [⟨"c2", "the Token"⟩], .top⟩,
   ⟨.forbid, "share_permitted", [⟨"c3", "the tOken"⟩], .top⟩]
#guard read extraEnv "Bb." == .one ⟨.require, "bb_required", [], .top⟩
#guard read extraEnv "Aa." == .refused "TypeMismatch" "addressee"
#guard read extraEnv "." == noReadingOutcome
#guard read extraEnv "C1." == noReadingOutcome
#guard web "Click Ask, if Click Ask, if draft is approved." == noReadingOutcome
#guard web "Use assistant." == .one ⟨.require, "use_required", [⟨"assistant", "assistant"⟩], .top⟩
#guard read (webWith (some ("user", "reader")) [("the key", "token1"), ("the token", "token1")])
    "Do not share the token." == .one ⟨.forbid, "share_permitted", [⟨"token1", "the token"⟩], .top⟩
#guard (readingsOf ⟨.require, "x", none⟩ [("a", []), ("b", [])] [.top, .bottom]).length == 4

/-! ## `readCommand_typed`'s `hw` (reviews/dri-decisions-20261102-ci-1.md item 1): every fixture environment passes
`jsonWF?`, so `hw` excludes none; over the one misordered raw tree below, which fails it, the statement without `hw` is
false, and `declared` is too -/

#guard [E_web, webWith none definitesWeb, webWith (some ("control", "assistant")) definitesWeb,
  webWith (some ("user", "reader")) [("the Token", "token1"), ("the token", "token1")],
  webWith (some ("user", "reader")) [("the key", "token1"), ("the token", "token1")],
  envWith 1, envWith 2, goSorts, goCase, extraEnv].all VE.Scope.jsonWF?

/-- `arguments` twice: `getObjVal?` finds the first, and `Json.mkObj (fields entry)` keeps the second. -/
def rawShare : String × Json :=
  ("share_permitted",
    match (permission "share_permitted" ["user", "token"] "{0} share {1}").2 with
    | .obj kvs =>
      let l : Std.TreeMap.Raw String Json compare :=
        Std.TreeMap.Raw.ofList [("arguments", Lean.toJson ["user", "token"])] compare
      let r : Std.TreeMap.Raw String Json compare := Std.TreeMap.Raw.ofList
        [("regulated", kvs["regulated"]?.getD .null), ("arguments", Lean.toJson ["user", "control"])] compare
      .obj ⟨⟨.inner 4 "description" (.str "x") l.inner.inner r.inner.inner⟩⟩
    | _ => .null)

def rawEnv : Json := envOf ["user", "control", "ledger", "text", "reading", "token"]
    (actsWeb.filter (·.1 != "share_permitted") ++ [rawShare])
    [("reader", "user"), ("draft", "reading"), ("assistant", "control"), ("calls", "ledger"),
     ("question1", "text"), ("meaning1", "text"), ("token1", "token")]
    "webapp-copy" (some ("user", "reader")) definitesWeb

#guard !VE.Scope.jsonWF? rawEnv
#guard match decodeSpeechEnvironmentFull rawEnv, lexOf E_web with
  | .ok se, .ok (E, L) =>
    !declared se &&
    match readCommand se se.scope E L workBudget "Do not share the token." with
    | .one r =>
      let D : VE.SpeechActs.SpeechDoc := ⟨se.ne.rv.environment, [], se.scope, se.ne.regulated, [], [], [], [], []⟩
      VE.SpeechActs.scopeOk D && !VE.SpeechActs.commandOk D (r.command "u")
    | _ => false
  | _, _ => false

/-- The outcome of readings of these formulas, each with its mark. -/
def outcomeOf (rs : List (VE.EnglishGrammar.EFormula × Bool)) : TranslateOutcome :=
  .readings (rs.map fun (f, m) => (f, m, VE.EnglishGrammar.DState.init)) true

def approvedE : VE.EnglishGrammar.EFormula := .pred "approved" [.const "draft"]

#guard match se0, lex0 with
  | some se, .ok (E, L) =>
    let unread (o : TranslateOutcome) : String × String := match guardOfOutcome se E L "c" o with
      | .error (.unread c t) => (c, t)
      | _ => ("", "")
    let marked := ("ConclusionWithoutPremise", "The condition is marked as a conclusion, and no earlier sentence is a premise.")
    unread (outcomeOf [(approvedE, false), (approvedE, true)]) == marked &&
      unread (outcomeOf [(approvedE, true), (approvedE, false)]) == marked &&
      unread (outcomeOf [(.pred "approved" [.const "calls"], false)]) ==
        ("IllTyped", "The condition was read, and its formula does not pass the type check.")
  | _, _ => false

/-- A reading set of `n` readings. -/
def readingSet (n : Nat) : Json :=
  Json.mkObj [("reading_sets", .arr #[Json.mkObj [("unit", .str "u"), ("readings", .arr
    (List.replicate n (Json.mkObj [("kind", .str "asserted"), ("content", .null)])).toArray)]])]

#guard [1, 2, readingsBound].all fun n => (VE.SpeechActs.Wire.readingCandidates (readingSet n)).toOption.isSome
#guard [0, readingsBound + 1].all fun n => (VE.SpeechActs.Wire.readingCandidates (readingSet n)).toOption.isNone

end VE.Commands.Examples
