import VE.Commands.Read
import VE.EnglishGrammar.E2Examples

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

/-- `E_web` (section 5). -/
def E_web : Json :=
  envOf ["user", "control", "ledger", "text", "reading", "token"] actsWeb
    [("reader", "user"), ("draft", "reading"), ("assistant", "control"), ("calls", "ledger"),
     ("question1", "text"), ("meaning1", "text"), ("token1", "token")]
    "webapp-copy" (some ("user", "reader")) definitesWeb

def web (s : String) (b : Nat := workBudget) : Outcome := read E_web s b

def approvedDraft : VE.Formula := .unary "approved" (.const "draft")


end VE.Commands.Examples
