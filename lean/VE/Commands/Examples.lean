import VE.Commands.Read
import VE.EnglishGrammar.E2Examples
import VE.Scope.Govern

/-! The fixtures of docs/spec/commands-imperatives.md section 5: the W rows over `E_web`, SA section 9's command rows
over F0, each limit at its boundary, and the 59 pinned web segments of the research's section 2.1. -/

namespace VE.Commands.Examples

open Lean (Json)
open VE.SpeechActs.Wire (SpeechEnvironment decodeSpeechEnvironmentFull readingsBound)
open VE.EnglishGrammar (Env Lexicon TranslateOutcome workBudget)

def sortEntry (s : String) : String × Json := (s, Json.mkObj [("description", .str s)])

def constEntry (c : String × String) : String × Json :=
  (c.1, Json.mkObj [("sort", .str c.2), ("description", .str c.1)])

/-- A predicate; a regulated one carries its role and act. -/
def predEntry (name : String) (args : List String) (role : Option (String × String)) (word : Option String := none)
    (dual : Option String := none) : String × Json :=
  (name, Json.mkObj ([("arguments", Lean.toJson args), ("description", .str name)] ++
    (word.toList.map fun w => ("verbalisation", .str w)) ++
    (role.toList.map fun (r, act) => ("regulated", Json.mkObj
      ([("role", .str r), ("default", .str (if r == "obligation" then "deny" else "allow")), ("act", .str act)] ++
        dual.toList.map fun d => ("permission", .str d))))))

def obligation (name : String) (args : List String) (act : String) (dual : Option String := none) : String × Json :=
  predEntry name args (some ("obligation", act)) none dual

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

/-- `E_web` (section 5). -/
def E_web : Json :=
  envOf ["user", "control", "ledger", "text", "reading", "token"] actsWeb
    [("reader", "user"), ("draft", "reading"), ("assistant", "control"), ("calls", "ledger"),
     ("question1", "text"), ("meaning1", "text"), ("token1", "token")]
    "webapp-copy" (some ("user", "reader")) definitesWeb

def web (s : String) (b : Nat := workBudget) : Outcome := read E_web s b

def approvedDraft : VE.Formula := .unary "approved" (.const "draft")


def noReadingOutcome : Outcome := .ofText Texts.noReading

def isRefused (code text : String) (o : Outcome) : Bool := o == .refused code text

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

/-! ## W16 and W32: SA section 9's command rows over F0 -/

def actsF0 : List (String × Json) :=
  [obligation "click_required" ["user", "control"] "{0} click {1}" (some "click_permitted"),
   permission "click_permitted" ["user", "control"] "{0} click {1}",
   permission "share_permitted" ["user", "token"] "{0} share {1}",
   obligation "submit_required" ["user", "query"] "{0} submit a proof of {1}" (some "submit_permitted"),
   permission "submit_permitted" ["user", "query"] "{0} submit a proof of {1}",
   obligation "open_required" ["user", "desk"] "{0} open {1}" (some "open_permitted"),
   permission "open_permitted" ["user", "desk"] "{0} open {1}",
   predEntry "disabled" ["control"] none (some "{0} is disabled"),
   predEntry "cat" ["thing"] none (some "{0} is a cat"),
   predEntry "animal" ["thing"] none (some "{0} is an animal")]

def constsF0 : List (String × String) :=
  [("alice", "user"), ("check", "control"), ("token1", "token"), ("desk1", "desk"), ("atlas", "service"),
   ("beacon", "service"), ("tom", "thing"), ("q1", "query")]

def sortsF0 : List String := ["user", "control", "token", "desk", "service", "thing", "query"]

def definitesF0 : List (String × String) :=
  [("the token", "token1"), ("the desk", "desk1"), ("the writing desk", "desk1")]

def scopedF0 (you : Option (String × String)) (definites := definitesF0) : Json :=
  envOf sortsF0 actsF0 constsF0 "t1" you definites

def f0 (s : String) : Outcome := read (scopedF0 (some ("user", "alice"))) s

def disabledCheck : VE.Formula := .unary "disabled" (.const "check")

#guard tuplesOf (scopedF0 (some ("user", "alice"))) == 12
#guard f0 "Click Check." == .one ⟨.require, "click_required", [⟨"check", "check"⟩], .top⟩
#guard f0 "Do not share the token." == .one ⟨.forbid, "share_permitted", [⟨"token1", "the token"⟩], .top⟩
#guard f0 "Open the desk." == .one ⟨.require, "open_required", [⟨"desk1", "the desk"⟩], .top⟩
#guard f0 "Do not open the desk." == .one ⟨.forbid, "open_permitted", [⟨"desk1", "the desk"⟩], .top⟩
#guard f0 "Click Check, if check is disabled." ==
  .one ⟨.require, "click_required", [⟨"check", "check"⟩], disabledCheck⟩
#guard read (scopedF0 none) "Click Check." == .refused "UnboundSlot" "you"
#guard read (scopedF0 (some ("user", "alice")) []) "Share the token." == noReadingOutcome
#guard f0 "Share the token." == .refused "MissingObligationRole" "{0} share {1}"
#guard f0 "Click Check and save." == .refused "CoordinatedActs" "split into two commands"
#guard f0 "You may close the desk." == .refused "PermissionNotCommand" "use an equality-guarded W1 rule"
#guard f0 "Please click Check." == .refused "InvalidInput" "please needs author approval"
#guard f0 "Open the writing desk." == .one ⟨.require, "open_required", [⟨"desk1", "the writing desk"⟩], .top⟩
#guard f0 "Choose authoring or translation mode." == noReadingOutcome
#guard read (scopedF0 (some ("service", "atlas"))) "Click Check." == .refused "TypeMismatch" "addressee"
#guard f0 "Prove that tom is an animal using these premises." == noReadingOutcome

def twoSpellings : List (String × String) := [("the Desk", "desk1"), ("the desk", "desk1")]

#guard read (scopedF0 (some ("user", "alice")) twoSpellings) "Open the desk." ==
  .one ⟨.require, "open_required", [⟨"desk1", "the Desk"⟩], .top⟩
#guard read (scopedF0 (some ("user", "alice")) twoSpellings) "Open the desk, if check is disabled." ==
  .one ⟨.require, "open_required", [⟨"desk1", "the Desk"⟩], disabledCheck⟩

/-! ## The 59 pinned web segments (research 2.1, catalogue blob `1ff7a7b72`) -/

def segments : List (String × String) :=
  [("uweb.index.38_0", "Evaluate the conclusion in a tiny world, then ask whether it follows from the assumptions in every world."),
   ("uweb.index.40_1", "Change the facts of a scenario and VE decides it again."),
   ("uweb.index.46_0", "For a new word, choose what kind of thing it names."),
   ("uweb.index.108_1", "Edit JSON to bring your own vocabulary or world."),
   ("uweb.index.132_0", "Write the question as a statement."),
   ("uweb.index.133_0", "Write what must, must not, or may happen."),
   ("uweb.index.133_1", "Add an exception or precedence, then check for a conflict in plain English."),
   ("uweb.app.162_0", "Check “{}”. {}"),
   ("uweb.app.191_1", "Restate the sentence or give an example."),
   ("uweb.app.262_1", "Open “Vocabulary & small world” to fix it."),
   ("uweb.app.267_1", "Change example now?"),
   ("uweb.tour.490_0", "Click Check rule conflict."),
   ("uweb.tour.491_0", "Click Review meaning."),
   ("uweb.tour.492_0", "Click Use this wording under the one you mean."),
   ("uweb.tour.507_0", "If the reading says what you meant, click Approve selected meaning."),
   ("uweb.tour.508_1", "Click Review meaning."),
   ("uweb.tour.511_0", "Look at Nearest declared wordings: “may read the handbook” is the closest one."),
   ("uweb.tour.511_1", "Names such as may_read are internal; skip them."),
   ("uweb.tour.513_0", "Make rule 4 an exception to rule 1: change “Rule 4.” to “Rule 4 (exception to rule 1).”"),
   ("uweb.tour.515_1", "Check that it says what you meant."),
   ("uweb.tour.520_0", "Now try your own sentences."),
   ("uweb.tour.537_0", "Skip it at any time."),
   ("uweb.tour.544_1", "Start again from step 3."),
   ("uweb.tour.551_0", "Then click Ask."),
   ("uweb.tour.552_0", "Then click Check rule conflict."),
   ("uweb.tour.555_0", "To fix it, change print back to read and click Review meaning."),
   ("uweb.tour.559_1", "To ask “May a new employee read the handbook?”, write this statement to test."),
   ("uweb.server.650_1", "Try again shortly."),
   ("uweb.server.651_1", "Try later; the daily cap resets at UTC midnight."),
   ("uweb.server.658_0", "Choose a listed rule vocabulary."),
   ("uweb.server.659_0", "Choose a scenario and its listed facts."),
   ("uweb.server.664_0", "Enter rules in English, up to 6000 characters."),
   ("uweb.server.677_0", "The checker is busy right now; try again in a minute."),
   ("uweb.server.690_1", "Reload its latest revision."),
   ("uweb.server.691_0", "Too many login attempts."),
   ("uweb.server.693_0", "Use the document assistant control."),
   ("uweb.server.697_0", "Write the question as one statement of at most 1000 characters."),
   ("uweb.worker.793_0", "Check exactly one conclusion at a time."),
   ("uweb.worker.801_0", "Select one sentence at a time for assistance."),
   ("uweb.worker.802_1", "Check the private server calls ledger."),
   ("uweb.drafts.881_0", "Approve one reading at a time."),
   ("uweb.drafts.885_0", "Choose a unit revision to restore."),
   ("uweb.drafts.886_0", "Choose authoring or translation mode."),
   ("uweb.drafts.887_0", "Choose declared kinds of things for the new word."),
   ("uweb.drafts.888_0", "Choose person, property, or relation."),
   ("uweb.drafts.889_0", "Confirm who acts on whom for a relation."),
   ("uweb.drafts.890_0", "Describe the new word in at most 300 characters."),
   ("uweb.drafts.897_0", "Enter a clarification or restatement."),
   ("uweb.drafts.898_0", "Enter a reason to keep this unit unresolved."),
   ("uweb.drafts.899_0", "Enter one glossary sentence."),
   ("uweb.drafts.900_0", "Enter up to 6000 characters of English."),
   ("uweb.drafts.902_0", "Give one positive and one negative example for the new word."),
   ("uweb.drafts.906_0", "Mode is fixed for this document; start a new document to change it."),
   ("uweb.drafts.927_1", "Reload its latest revision."),
   ("uweb.drafts.933_0", "Use one lower-case word for the new term."),
   ("uweb.rules.1088_0", "Ask about one statement at a time."),
   ("uweb.rules.1091_0", "Choose a listed rule vocabulary."),
   ("uweb.rules.1111_0", "Write the question as one statement, such as: Every employee who is new may read the handbook."),
   ("uweb.examples.1243_1", "Remove the review rule in the IDE to find a countermodel.")]

/-- The segments that read (the nine of W1 to W7), and the two other kinds of refusal; the rest have no reading. -/
def oneIds : List String :=
  ["uweb.index.132_0", "uweb.tour.490_0", "uweb.tour.491_0", "uweb.tour.508_1", "uweb.server.658_0",
   "uweb.server.693_0", "uweb.worker.802_1", "uweb.drafts.885_0", "uweb.rules.1091_0"]

def coordinatedIds : List String :=
  ["uweb.index.40_1", "uweb.tour.555_0", "uweb.server.659_0", "uweb.drafts.902_0"]

def nonAsciiIds : List String :=
  ["uweb.app.162_0", "uweb.app.262_1", "uweb.tour.511_0", "uweb.tour.513_0", "uweb.tour.559_1"]

#guard segments.length == 59
#guard ((segments.filter (oneIds.contains ·.1)).map (·.2.utf8ByteSize)).sum == 273
#guard segments.all fun (i, t) =>
  match web t with
  | .one _ => oneIds.contains i
  | o =>
    o == (if coordinatedIds.contains i then .ofText Texts.coordinated
      else if nonAsciiIds.contains i then .ofText Texts.nonAscii else noReadingOutcome)

/-! ## `readCommand_typed`'s `JsonWF` (reviews/dri-decisions-20261102-ci-1.md): every fixture environment passes the
check, and over the one misordered raw object below the statement without `JsonWF` is false. -/

#guard [E_web, envWith 1, envWith 2, scopedF0 none, scopedF0 (some ("user", "alice")),
  scopedF0 (some ("service", "atlas")), scopedF0 (some ("user", "alice")) [],
  scopedF0 (some ("user", "alice")) twoSpellings].all VE.Scope.jsonWF?

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
    match readCommand se se.scope E L workBudget "Do not share the token." with
    | .one r =>
      let D : VE.SpeechActs.SpeechDoc := ⟨se.ne.rv.environment, [], se.scope, se.ne.regulated, [], [], [], [], []⟩
      VE.SpeechActs.scopeOk D && !VE.SpeechActs.commandOk D (r.command "u")
    | _ => false
  | _, _ => false

end VE.Commands.Examples
