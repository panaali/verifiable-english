import VE.EnglishGrammar.Run
import VE.EnglishGrammar.ReadExamples

/-! The acceptance fixtures of docs/spec/english-lean-s3.md section 8, as `#guard` checks on the real
English grammar `grammar E L`, the reader `read`, `admit` and `firstChecked`.

The environments `FO`, `FD`, `FA`, `FR` and `FM` of section 8 are written as `ve.core@0.2` environment JSON,
decoded by `Env.decode` after the boundary of spec 2.3 (`Run.environmentId`) admitted them, so `read` runs the
typed check over the typing view. Verdicts count derivations per sentence with the parser at cap 2; outcomes
are `read`'s, summarised as in `ReadExamples`.
-/

namespace VE.EnglishGrammar.ProfileExamples
open Lean VE.Grammar VE.EnglishGrammar VE.EnglishGrammar.ReadExamples

/-! ## Environments and lexicons -/

/-- A predicate of a fixture: name, argument sorts, and extra fields of its entry. -/
abbrev Pred := String × List String × List (String × Json)

def worded (w : String) : List (String × Json) := [("verbalisation", .str w)]

/-- A `ve.core@0.2` environment: profiles, sorts, predicates, constants and extra top-level fields. -/
def routeEnv (profiles : List String) (sorts : List String) (preds : List Pred) (consts : List (String × String))
    (extra : List (String × Json) := []) : Json :=
  Json.mkObj ([("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [
      ("sorts", Json.mkObj (sorts.map fun s => (s, Json.mkObj [("description", .str "A sort.")]))),
      ("predicates", Json.mkObj (preds.map fun (p, args, more) => (p, Json.mkObj ([("arguments", toJson args),
        ("description", .str "A predicate.")] ++ more)))),
      ("constants", Json.mkObj (consts.map fun (c, s) => (c, Json.mkObj [("sort", .str s),
        ("description", .str "A constant.")])))])] ++ extra)

/-- The environment after the boundary of spec 2.3: admitted by `Run.environmentId`, then decoded. -/
def admitted (j : Json) : Except String Env := do
  let _ ← Run.environmentId j
  Env.decode j (Json.mkObj [])

def envOf (j : Json) : Env :=
  match admitted j with
  | .ok E => E
  | .error _ => emptyEnv

def basePreds : List Pred :=
  [("deployed", ["service"], worded "{0} is deployed"),
   ("reviewed", ["service"], worded "{0} is reviewed" ++ [("negative_verbalisation", .str "{0} is not reviewed")]),
   ("owns", ["person", "service"], worded "{0} owns {1}" ++ [("negative_verbalisation", .str "{0} does not own {1}")])]

/-! ### `FO` (8.1) -/

def jFO : Json := routeEnv ["order@0", "relational-fol@0"] ["person", "service"]
  (basePreds ++ [("costs", ["service", "$int"], worded "{0} costs {1}"), ("exceeds", ["$int", "$int"], worded "{0} exceeds {1}")])
  [("alice", "person"), ("legacy", "service"), ("budget", "$int"), ("limit", "$int")]
def FO : Env := envOf jFO
def LO : Lexicon := { LF with
  wordings := LF.wordings ++ [("costs", "{0} costs {1}"), ("exceeds", "{0} exceeds {1}")],
  spellings := LF.spellings ++ [("budget", "budget"), ("limit", "limit")] }

/-! ### `FD` (8.2) -/

def flags : List (String × Json) := [("functional", .bool true), ("total", .bool true)]
def jFD : Json := routeEnv ["data@0", "relational-fol@0"] ["person", "service"]
  (basePreds ++ [("senior", ["person"], worded "{0} is senior"), ("owner_of", ["service", "person"], flags),
    ("backup_of", ["service", "service"], flags)])
  [("alice", "person"), ("legacy", "service")]
def FD : Env := envOf jFD
def LD : Lexicon := { LF with
  wordings := LF.wordings ++ [("senior", "{0} is senior"),
    ("owner_of", "{0} has the recorded relation \"owner_of\" to {1}"),
    ("backup_of", "{0} has the recorded relation \"backup_of\" to {1}")] }

/-! ### `FA` (8.3) and `FR` (8.4) -/

def altBlock : Json := Json.mkObj [("chooser", .str "agent"), ("action", .str "action"), ("harm", .str "harm"),
  ("available", .str "available"), ("leads_to", .str "leads_to"), ("outcomes", .str "signed")]
def altPreds : List Pred :=
  [("available", ["action", "agent"], worded "{0} is available to {1}"),
   ("leads_to", ["action", "harm"], worded "{0} leads to {1}"), ("safe", ["action"], worded "{0} is safe")]
def altConsts : List (String × String) := [("wait", "action"), ("robot", "agent"), ("injury", "harm")]
def jFA : Json := routeEnv ["alternatives@0", "norms@0", "relational-fol@0"] ["action", "agent", "harm"] altPreds
  altConsts [("alternatives", altBlock)]
def FA : Env := envOf jFA
def LA : Lexicon := {
  nouns := [("action", "action"), ("agent", "agent"), ("harm", "harm")],
  letters := [("action", "A"), ("agent", "G"), ("harm", "H")],
  wordings := [("available", "{0} is available to {1}"), ("leads_to", "{0} leads to {1}"), ("safe", "{0} is safe"),
    ("avoidable", "{0} is avoidable by {1}"), ("unavoidable", "{0} is unavoidable by {1}"),
    ("allows", "{0} allows {1} to happen"), ("prevents", "{0} prevents {1}")],
  negatives := [],
  aliases := [("avoidable", "{0} is preventable by {1}", false), ("allows", "{0} lets {1} happen", false),
    ("leads_to", "{0} does not lead to {1}", true)],
  spellings := [("wait", "wait"), ("robot", "robot"), ("injury", "injury")] }

def riskBlock : Json := Json.mkObj [
  ("severity", Json.mkObj [("sort", .str "severity"), ("classes", toJson ["minor", "catastrophic"]),
    ("more_severe", toJson [["catastrophic", "minor"]]), ("unranked", Json.arr #[]),
    ("decided_by", .str "the fixture author")]),
  ("harm_classes", toJson [["injury", "catastrophic"]]), ("unexamined", .str "possible")]
def jFR : Json := routeEnv ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"] ["action", "agent", "harm"]
  altPreds altConsts [("alternatives", altBlock), ("risk", riskBlock)]
def FR : Env := envOf jFR
def LR : Lexicon := { LA with
  nouns := LA.nouns ++ [("severity", "severity")], letters := LA.letters ++ [("severity", "V")],
  wordings := (LA.wordings.filter (·.1 != "prevents")) ++ [("prevents", "{0} might prevent {1}"),
    ("risk__might_lead_to", "{0} might lead to {1}"), ("risk__class", "{0} is {1}"),
    ("risk__or_worse", "{0} is {1} or worse"), ("risk__less_worst", "{0} has a less severe worst case than {1}"),
    ("risk__more_severe", "{0} is more severe than {1}")],
  negatives := [("leads_to", "{0} might not lead to {1}"), ("risk__might_lead_to", "{0} cannot lead to {1}")],
  aliases := LA.aliases.filter (·.1 != "leads_to"),
  spellings := LA.spellings ++ [("minor", "minor"), ("catastrophic", "catastrophic")] }

/-! ### `FM` (8.5) -/

def regulated (role act : String) : List (String × Json) :=
  [("regulated", Json.mkObj [("role", .str role), ("default", .str "deny"), ("act", .str act)])]
def jFM : Json := routeEnv ["norms@0", "relational-fol@0"] ["person", "service"]
  (basePreds ++ [("access", ["person", "service"], regulated "permission" "{0} access {1}"),
    ("review", ["person", "service"], regulated "obligation" "{0} review {1}")])
  [("alice", "person"), ("legacy", "service")]
def FM : Env := envOf jFM
def LM : Lexicon := { LF with
  wordings := LF.wordings ++ [("access", "{0} may access {1}"), ("review", "{0} must review {1}")] }


/-! ## Shorthands -/

def n (k : Int) : ETerm := .num k
def costs (x : ETerm) : EFormula := b "costs" (c "legacy") x
def signs (k : Nat) : String := String.mk (List.replicate k '-')
def nines (k : Nat) : String := String.mk (List.replicate k '9')
def nineValue (k : Nat) : Int := (10 : Int) ^ k - 1
def scaleN : Nat → ETerm → ETerm
  | 0, t => t
  | k + 1, t => .scale (-1) (scaleN k t)

/-! ## 8.1 `order@0` -/

#guard verdicts FO LO "Legacy costs 5." == one && rd FO LO "Legacy costs 5." == ok1 (costs (n 5))
#guard rd FO LO "Legacy costs -5." == ok1 (costs (n (-5)))
#guard rd FO LO "Legacy costs -0." == ok1 (costs (n 0))
#guard rd FO LO "Legacy costs [budget + 1]." == ok1 (costs (.add (c "budget") (n 1)))
#guard rd FO LO "Legacy costs [budget - limit]." == ok1 (costs (.add (c "budget") (.scale (-1) (c "limit"))))
#guard rd FO LO "Legacy costs [3 * budget]." == ok1 (costs (.scale 3 (c "budget")))
#guard rd FO LO "Legacy costs [-3 * budget]." == ok1 (costs (.scale (-3) (c "budget")))
#guard verdicts FO LO "Legacy costs [budget * limit]." == one &&
  rd FO LO "Legacy costs [budget * limit]." == rej .coefficientNotNumeral
#guard rd FO LO "Legacy costs [[budget + 1] * limit]." == rej .coefficientNotNumeral
#guard rd FO LO "Legacy costs twice the budget." == ok1 (costs (.scale 2 (c "budget")))
#guard rd FO LO "Legacy costs -budget." == ok1 (costs (.scale (-1) (c "budget")))
#guard rd FO LO "Legacy costs --budget." == ok1 (costs (.scale (-1) (.scale (-1) (c "budget"))))
#guard rd FO LO "Legacy costs -[budget + 1]." == ok1 (costs (.scale (-1) (.add (c "budget") (n 1))))
#guard rd FO LO "Legacy costs [budget - -5]." == ok1 (costs (.add (c "budget") (.scale (-1) (n (-5)))))
#guard rd FO LO "Legacy costs [[budget + 1] + [2 * limit]]." ==
  ok1 (costs (.add (.add (c "budget") (n 1)) (.scale 2 (c "limit"))))
#guard rd FO LO "Legacy costs [[budget + 1] + [limit * 2]]." == rej .coefficientNotNumeral
#guard rd FO LO "Budget is at most 5." == ok1 (.le (c "budget") (n 5)) &&
  rd FO LO "Budget IS AT MOST 5." == ok1 (.le (c "budget") (n 5))
#guard rd FO LO "Budget is less than limit." == ok1 (.lt (c "budget") (c "limit")) &&
  rd FO LO "Budget is more than limit." == ok1 (.lt (c "limit") (c "budget"))
#guard rd FO LO "Budget is at least [limit + 1]." == ok1 (.le (.add (c "limit") (n 1)) (c "budget"))
#guard rd FO LO "Budget is the same as limit." == ok1 (.eq (c "budget") (c "limit")) &&
  rd FO LO "Budget exceeds limit." == ok1 (b "exceeds" (c "budget") (c "limit"))
#guard rd FO LO "Every service that costs 5 is reviewed." ==
  ok1 (.all "service" (.implies (b "costs" (v 0) (n 5)) (u "reviewed" (v 0))))
#guard rd FO LO "Every service costs twice the budget." == ok1 (.all "service" (b "costs" (v 0) (.scale 2 (c "budget"))))
-- or20 to or26: no derivation
#guard ["Legacy costs --5.", "Legacy costs -twice the budget.", "Legacy costs - budget.", "Legacy costs [budget+1].",
  "Legacy costs [budget +1].", "Legacy costs [ budget + 1].", "Legacy costs [budget + 1 ].", "Legacy costs legacy.",
  "Legacy is the same as budget.", "Budget is the same as legacy.", "Legacy costs twice the 5."].all
  (verdicts FO LO · == zero)
#guard rd FO LO "Legacy costs 007." == .lexical (.badNumeral 13)
#guard rd FO LO "Legacy is deployed. It costs 5." == .ok [(u "deployed" (c "legacy"), false), (costs (n 5), false)]
#guard rd FO LO "It costs 5." == rej .pronounUnresolved && rd FO LO "That service costs 5." == rej .unboundReference
-- or29 to or33: the depth of an integer term
#guard rd FO LO ("Legacy costs " ++ signs 63 ++ "budget.") == ok1 (costs (scaleN 63 (c "budget")))
#guard verdicts FO LO ("Legacy costs " ++ signs 64 ++ "budget.") == one &&
  rd FO LO ("Legacy costs " ++ signs 64 ++ "budget.") == rej .nestingLimit
#guard rd FO LO ("Legacy costs [[budget * limit] + " ++ signs 64 ++ "budget].") == rej .nestingLimit
#guard rd FO LO ("That service costs " ++ signs 64 ++ "budget.") == rej .unboundReference
#guard rd FO LO ("Budget is at most " ++ signs 64 ++ "budget.") == rej .nestingLimit &&
  rd FO LO ("[budget * limit] is at most " ++ signs 64 ++ "budget.") == rej .nestingLimit
-- or34, or35: the numeral bound
#guard rd FO LO ("Legacy costs " ++ nines 40 ++ ".") == ok1 (costs (n (nineValue 40))) &&
  rd FO LO ("Legacy costs " ++ nines 41 ++ ".") == rej .numeralBound
#guard rd FO LO ("Legacy costs -" ++ nines 39 ++ ".") == ok1 (costs (n (-nineValue 39))) &&
  rd FO LO ("Legacy costs -" ++ nines 40 ++ ".") == rej .numeralBound
-- or36: S2's b1 and b3
#guard verdicts FO LO "Every service is reviewed." == one &&
  verdicts FO LO "For every service that is deployed, there is a person who owns that service." == one
-- or37: a quoted integer spelling
def jFO2 : Json := routeEnv ["order@0", "relational-fol@0"] ["person", "service"]
  (basePreds ++ [("costs", ["service", "$int"], worded "{0} costs {1}"), ("exceeds", ["$int", "$int"], worded "{0} exceeds {1}")])
  [("alice", "person"), ("legacy", "service"), ("budget", "$int"), ("limit", "$int"), ("budget_cap", "$int")]
def FO2 : Env := envOf jFO2
def LO2 : Lexicon := { LO with spellings := LO.spellings ++ [("budget_cap", "\"budget_cap\"")] }
#guard LO2.valid FO2 {}
#guard verdicts FO2 LO2 "\"budget_cap\" is at most 5." == one &&
  rd FO2 LO2 "\"budget_cap\" is at most 5." == ok1 (.le (c "budget_cap") (n 5))
#guard verdicts FO2 LO2 "Legacy costs \"budget_cap\"." == one &&
  rd FO2 LO2 "Legacy costs \"budget_cap\"." == ok1 (costs (c "budget_cap"))
#guard verdicts FO2 LO2 "Legacy costs twice the \"budget_cap\"." == zero
-- or38: a term too deep before a malformed part has no derivation (the agreed difference of 2.11)
#guard rd FO LO (signs 64 ++ "budget exceeds [ limit + 1].") == .stopped 0 .none &&
  rd FO LO ("Legacy costs " ++ signs 64 ++ "[ limit + 1].") == .stopped 0 .none

/-! ## 8.2 `data@0` -/

-- `Env.decode` reads the vocabulary in key order, so the first attribute is `backup_of`
#guard LD.valid FD {} && valueSorts FD == ["service", "person"]
#guard rd FD LD "The owner_of of legacy is alice." == ok1 (b "owner_of" (c "legacy") (c "alice"))
#guard rd FD LD "Legacy has the recorded relation \"owner_of\" to alice." == ok1 (b "owner_of" (c "legacy") (c "alice"))
#guard rd FD LD "The owner_of of legacy is senior." ==
  ok1 (.ex "person" (.and (b "owner_of" (c "legacy") (v 0)) (u "senior" (v 0))))
#guard verdicts FD LD "The owner_of of legacy is deployed." == zero
#guard rd FD LD "The backup_of of legacy is deployed." ==
  ok1 (.ex "service" (.and (b "backup_of" (c "legacy") (v 0)) (u "deployed" (v 0))))
#guard rd FD LD "For every service, the owner_of of that service is senior." ==
  ok1 (.all "service" (.ex "person" (.and (b "owner_of" (v 1) (v 0)) (u "senior" (v 0)))))
#guard ["The owns of alice is legacy.", "The Owner_of of legacy is alice.",
  "If legacy is deployed, then The owner_of of legacy is alice.",
  "Every service that the owner_of of that service is alice is reviewed."].all (verdicts FD LD · == zero)
#guard rd FD LD "If legacy is deployed, then the owner_of of legacy is alice." ==
  ok1 (.implies (u "deployed" (c "legacy")) (b "owner_of" (c "legacy") (c "alice")))
#guard rd FD LD "Legacy is deployed. The backup_of of it is legacy." ==
  .ok [(u "deployed" (c "legacy"), false), (b "backup_of" (c "legacy") (c "legacy"), false)]
#guard rd FD LD "Legacy is deployed. The backup_of of legacy is it." ==
  .ok [(u "deployed" (c "legacy"), false), (b "backup_of" (c "legacy") (c "legacy"), false)]
#guard rd FD LD "Legacy is deployed. The backup_of of it is deployed." ==
  .ok [(u "deployed" (c "legacy"), false),
    (.ex "service" (.and (b "backup_of" (c "legacy") (v 0)) (u "deployed" (v 0))), false)]
#guard rd FD LD "Legacy is deployed. If legacy is deployed, then the backup_of of it is legacy." ==
  rej .pronounUnresolved 1
#guard rd FD LD "The backup_of of it is legacy." == rej .pronounUnresolved
-- da17 to da20: the six pairs, factored, in Python's shape, and with the property nonterminals renumbered
def pairs6 : List String := ["owner_of", "backup_of"].flatMap fun r =>
  ["senior", "deployed", "reviewed"].map fun p => "The " ++ r ++ " of legacy is " ++ p ++ "."
#guard pairs6.map (verdicts FD LD) == [one, zero, zero, zero, one, one]

/-- `FP`: the grammar of `FD` in Python's shape: no property nonterminal, one rule `atom → the r of term is p`
per attribute `r` and property `p` of its value sort, each with the action of that pair. -/
def pythonShape (E : Env) (L : Lexicon) : Grammar Terminal × Array (Action sig) :=
  let G := grammar E L
  let keep := G.rules.filter fun r => r.lhs < ntProperty && !(r.rhs.any fun | .n k => decide (ntProperty ≤ k) | _ => false)
  let pairs := E.predicates.flatMap fun d => match d.args, valueSortOf d with
    | [_, s], some _ => (E.predicates.filter (·.args == [s])).map fun p => (d.name, s, p.name)
    | _, _ => []
  let base := (acts E L).size
  let rules := pairs.toArray.mapIdx fun i (r, _, p) =>
    ({ lhs := ntAtom, rhs := [.t (.kw "the"), .t (.kw r), .t (.kw "of"), .n ntTerm, .t (.kw "is"), .t (.kw p)],
       act := base + i, tag := "attribute." ++ r ++ "." ++ p } : Rule Terminal)
  let actions := pairs.toArray.map fun (r, s, p) =>
    (build [.term] .formula (fun xs c => do
      let t ← xs.1 c
      pure (.ex s (.and (.pred r [t.term.lift, .var 0]) (.pred p [.var 0])))) [.tok, .tok, .tok, .term, .tok, .tok])
  ({ rules := keep ++ rules, start := 0, rank := ranksStaged }, acts E L ++ actions)

def FPG : Grammar Terminal := (pythonShape FD LD).1
def FPacts : Array (Action sig) := (pythonShape FD LD).2
#guard FPG.wf && terminatorFree FPG && FPG.typed sig ntTy FPacts

def verdictsIn (G : Grammar Terminal) (s : String) : List V :=
  match lex s with
  | .error r => [.lexError r]
  | .ok sents => sents.toList.map fun w => match parse G 2 workBudget w with
    | none => .budget
    | some ts => .count ts.length

/-- The outcome of one sentence from the initial state in a grammar, summarised. -/
def outcomeIn (G : Grammar Terminal) (A : Array (Action sig)) (s : String) : Option O :=
  match lex s with
  | .ok sents => match sents.toList with
    | [w] => some (match (readSentence G (meaning G A) DState.init workBudget w).1 with
      | .ok _ _ => .ok
      | .noDerivation => .none
      | .ambiguous _ _ => .many
      | .rejected r => .rejected r
      | .budget => .budget)
    | _ => none
  | .error _ => none

def formulaIn (G : Grammar Terminal) (A : Array (Action sig)) (s : String) : Option EFormula :=
  match lex s with
  | .ok sents => match sents.toList with
    | [w] => match (readSentence G (meaning G A) DState.init workBudget w).1 with
      | .ok f _ => some f
      | _ => none
    | _ => none
  | .error _ => none

#guard pairs6.map (verdictsIn FPG) == [one, zero, zero, zero, one, one]
#guard pairs6.map (fun s => (outcomeIn FPG FPacts s, formulaIn FPG FPacts s)) ==
  pairs6.map (fun s => (outcomeIn (grammar FD LD) (acts FD LD) s, formulaIn (grammar FD LD) (acts FD LD) s))
-- da20: a third value sort first renumbers the property nonterminals; the outcomes stay
def jFD3 : Json := routeEnv ["data@0", "relational-fol@0"] ["area", "person", "service"]
  ([("area_of", ["service", "area"], flags)] ++ basePreds ++ [("senior", ["person"], worded "{0} is senior"),
    ("owner_of", ["service", "person"], flags), ("backup_of", ["service", "service"], flags)])
  [("alice", "person"), ("legacy", "service")]
def FD3 : Env := envOf jFD3
def LD3 : Lexicon := { LD with
  nouns := LD.nouns ++ [("area", "area")], letters := LD.letters ++ [("area", "R")],
  wordings := LD.wordings ++ [("area_of", "{0} has the recorded relation \"area_of\" to {1}")] }
#guard LD3.valid FD3 {} && valueSorts FD3 == ["area", "service", "person"]
#guard pairs6.map (fun s => (outcomeIn (grammar FD3 LD3) (acts FD3 LD3) s, formulaIn (grammar FD3 LD3) (acts FD3 LD3) s)) ==
  pairs6.map (fun s => (outcomeIn (grammar FD LD) (acts FD LD) s, formulaIn (grammar FD LD) (acts FD LD) s))

/-! ## 8.3 `alternatives@0` -/

def r : ETerm := c "robot"
def Av (o : ETerm) : EFormula := b "available" (v 0) o
def D (i : Nat) : EFormula := .not (.eq (v 0) (v i))
def S : EFormula := u "safe" (v 0)
def Ld : EFormula := b "leads_to" (v 0) (c "injury")
def act (f : EFormula) : EFormula := .all "action" f

#guard LA.valid FA {} && LA.failures FA {} == []
#guard verdicts FA LA "Every action available to robot is safe." == one &&
  rd FA LA "Every action available to robot is safe." == ok1 (act (.implies (Av r) S))
#guard rd FA LA "For every action, every other action available to robot is safe." ==
  ok1 (act (act (.implies (.and (Av r) (D 1)) S)))
#guard rd FA LA "For every action, another action available to robot is safe." ==
  ok1 (act (.ex "action" (.and (.and (Av r) (D 1)) S)))
#guard verdicts FA LA "Every other action available to robot is safe." == one &&
  rd FA LA "Every other action available to robot is safe." == rej .unboundReference &&
  rd FA LA "Another action available to robot is safe." == rej .unboundReference
#guard rd FA LA "For every action named A1, for every action named A2, every other action available to robot is safe." ==
  ok1 (act (act (act (.implies (.and (Av r) (D 1)) S))))
#guard rd FA LA ("For every action named A1, for every action named A2, every other action available to robot " ++
  "excluding A1 is safe.") == ok1 (act (act (act (.implies (.and (Av r) (D 2)) S))))
#guard rd FA LA ("For every action named A1, for every action named A2, another action available to robot " ++
  "excluding A1 is safe.") == ok1 (act (act (.ex "action" (.and (.and (Av r) (D 2)) S))))
#guard rd FA LA "For every action, every other action available to robot excluding robot is safe." == rej .sortMismatch
#guard rd FA LA ("For every agent, for every action, every other action available to robot excluding that agent " ++
  "is safe.") == rej .sortMismatch
#guard verdicts FA LA "Every action available to robot excluding robot is safe." == zero
#guard rd FA LA "For every action, every other action available to robot that other action leads to injury." ==
  ok1 (act (act (.implies (.and (Av r) (D 1)) Ld)))
#guard rd FA LA "For every action, another action available to robot either is safe or leads to injury." ==
  ok1 (act (.ex "action" (.and (.and (Av r) (D 1)) (.or S Ld))))
#guard rd FA LA "For every action, another action available to robot either is safe or leads to injury, or both." ==
  ok1 (act (.ex "action" (.and (.and (Av r) (D 1)) (.or S Ld))))
#guard rd FA LA "For every action, another action available to robot both is safe and leads to injury." ==
  ok1 (act (.ex "action" (.and (.and (Av r) (D 1)) (.and S Ld))))
#guard rd FA LA ("For every action, every other action available to robot either that other action is safe or " ++
  "leads to injury.") == ok1 (act (act (.implies (.and (Av r) (D 1)) (.or S Ld))))
#guard rd FA LA "For every action, another action available to robot that other action is the same as wait." ==
  ok1 (act (.ex "action" (.and (.and (Av r) (D 1)) (.eq (v 0) (c "wait")))))
#guard verdicts FA LA "For every action, every other action available to robot is the same as wait." == zero
#guard rd FA LA "Every action available to robot that action is safe." == ok1 (act (.implies (Av r) S))
#guard verdicts FA LA "Every action available to robot that other action is safe." == one &&
  rd FA LA "Every action available to robot that other action is safe." == rej .unboundReference
#guard rd FA LA "For every action, every other action available to robot that action is safe." == rej .unboundReference
#guard verdicts FA LA "For every action, that other action is safe." == one &&
  rd FA LA "For every action, that other action is safe." == rej .unboundReference
#guard rd FA LA "Every action available to it is safe." == rej .pronounUnresolved &&
  rd FA LA "Every action available to that agent is safe." == rej .unboundReference
#guard rd FA LA "For every agent, every action available to that agent is safe." ==
  ok1 (.all "agent" (act (.implies (Av (v 1)) S)))
#guard ["For every action, every other action available to robot That other action is safe.",
  "Every Action available to robot is safe.", "Every action Available to robot is safe.",
  "Every action available to robot wait is safe.", "Every action available to robot this holds in all cases."].all
  (verdicts FA LA · == zero)
#guard rd FA LA "For every action, every other action available to robot is the same as that other action." ==
  .stopped 0 .none
#guard rd FA LA ("For every action, another action available to robot that other action is the same as " ++
  "That Other Action.") == ok1 (act (.ex "action" (.and (.and (Av r) (D 1)) (.eq (v 0) (v 0)))))
#guard rd FA LA "Injury is preventable by robot." == ok1 (b "avoidable" (c "injury") r) &&
  rd FA LA "Injury is avoidable by robot." == ok1 (b "avoidable" (c "injury") r)
#guard rd FA LA "Wait lets injury happen." == ok1 (b "allows" (c "wait") (c "injury")) &&
  rd FA LA "Wait does not lead to injury." == ok1 (.not (b "leads_to" (c "wait") (c "injury"))) &&
  rd FA LA "Wait prevents injury." == ok1 (b "prevents" (c "wait") (c "injury"))
#guard rd FA LA "Wait is safe. Therefore every action available to robot is safe." ==
  .ok [(u "safe" (c "wait"), false), (act (.implies (Av r) S), true)]
#guard rd FA LA "For every action, every action available to robot is safe." == ok1 (act (act (.implies (Av r) S)))
#guard verdicts FA LA "Wait cannot lead to injury." == zero
-- al36 to al38: the action sort on its quoted fallback noun
def LA2 : Lexicon := { LA with nouns := [("action", "entity of sort \"action\""), ("agent", "agent"), ("harm", "harm")] }
#guard LA2.valid FA {}
#guard verdicts FA LA2 "Every entity of sort \"action\" available to robot is safe." == one &&
  rd FA LA2 "Every entity of sort \"action\" available to robot is safe." == ok1 (act (.implies (Av r) S))
#guard rd FA LA2 ("For every entity of sort \"action\", every other entity of sort \"action\" available to robot " ++
  "that other entity of sort \"action\" is safe.") == ok1 (act (act (.implies (.and (Av r) (D 1)) S)))
#guard verdicts FA LA2 "Every entity of sort \"Action\" available to robot is safe." == zero &&
  verdicts FA LA2 "Every Entity of sort \"action\" available to robot is safe." == zero

/-! ## 8.4 `risk@0` -/

def M (a h : ETerm) : EFormula := b "risk__might_lead_to" a h
def w : ETerm := c "wait"
def inj : ETerm := c "injury"

#guard LR.valid FR {}
#guard rd FR LR "Wait might lead to injury." == ok1 (M w inj)
#guard rd FR LR "Wait cannot lead to injury." == ok1 (.not (M w inj))
#guard rd FR LR "Wait might not lead to injury." == ok1 (.not (b "leads_to" w inj)) &&
  rd FR LR "Wait leads to injury." == ok1 (b "leads_to" w inj)
#guard rd FR LR "Injury is catastrophic." == ok1 (b "risk__class" inj (c "catastrophic"))
#guard rd FR LR "Injury is minor or worse." == ok1 (b "risk__or_worse" inj (c "minor"))
#guard rd FR LR "Wait has a less severe worst case than wait." == ok1 (b "risk__less_worst" w w)
#guard verdicts FR LR "Catastrophic is more severe than minor." == one &&
  rd FR LR "Catastrophic is more severe than minor." == ok1 (b "risk__more_severe" (c "catastrophic") (c "minor"))
#guard rd FR LR "Wait might prevent injury." == ok1 (b "prevents" w inj)
#guard rd FR LR "For every harm that is catastrophic, wait cannot lead to that harm." ==
  ok1 (.all "harm" (.implies (b "risk__class" (v 0) (c "catastrophic")) (.not (M w (v 0)))))
#guard verdicts FR LR "Every action available to robot cannot lead to injury." == one &&
  rd FR LR "Every action available to robot cannot lead to injury." == rej (.blockedWording "risk-every-cannot")
#guard rd FR LR "Every action available to robot either is safe or cannot lead to injury." ==
    rej (.blockedWording "risk-every-cannot") &&
  rd FR LR "Every action available to robot both cannot lead to injury and is safe." ==
    rej (.blockedWording "risk-every-cannot")
#guard rd FR LR "For every action, every other action available to robot cannot lead to injury." ==
  ok1 (act (act (.implies (.and (Av r) (D 1)) (.not (M (v 0) inj)))))
#guard rd FR LR "For every action, another action available to robot cannot lead to injury." ==
  ok1 (act (.ex "action" (.and (.and (Av r) (D 1)) (.not (M (v 0) inj)))))
#guard rd FR LR "Every action available to robot might not lead to injury." == ok1 (act (.implies (Av r) (.not Ld)))
#guard rd FR LR "Every action available to robot might lead to injury." == ok1 (act (.implies (Av r) (M (v 0) inj)))
-- ri16: the guard's action with its flag argument false, and true
def ri16 (risk : Bool) : Except Reject EFormula :=
  runGuard .every "action" "action" "available" risk (fun _ => .ok ⟨r, none⟩) none
    (fun _ => .ok (.not (M (v 0) inj))) (Ctx.start DState.init)
#guard (match ri16 false with | .ok f => f == act (.implies (Av r) (.not (M (v 0) inj))) | .error _ => false)
#guard (match ri16 true with | .error e => e == .blockedWording "risk-every-cannot" | .ok _ => false)
#guard ["Wait may lead to injury.", "Wait does not lead to injury.", "Wait could lead to injury.", "Wait risks injury.",
  "Wait is likely to lead to injury.", "Wait increases the risk of injury.", "Wait certainly leads to injury.",
  "Wait prevents injury.", "Wait is safer than wait.", "Wait leads to injury unless wait is safe.",
  "Wait cannot lead to injury exactly when wait is safe.", "Wait causes injury.", "Wait results in injury."].all
  (verdicts FR LR · == zero)

/-! ## 8.5 Modal atoms -/

#guard LM.valid FM {}
#guard rd FM LM "Alice may access legacy." == ok1 (b "access" (c "alice") (c "legacy")) &&
  rd FM LM "Alice must review legacy." == ok1 (b "review" (c "alice") (c "legacy"))
#guard rd FM LM "Every person who may access legacy owns legacy." ==
  ok1 (.all "person" (.implies (b "access" (v 0) (c "legacy")) (b "owns" (v 0) (c "legacy"))))
#guard verdicts FM LM "Alice may not access legacy." == zero && verdicts FM LM "Alice access legacy." == zero

/-! ## 8.6 The lexicon -/

#guard LD.valid FD {} && LA.failures FA {} == [] && LR.valid FR {}
def withoutForm (E : Env) (p : String) : Env := { E with forms := { E.forms with wordings := E.forms.wordings.filter (·.1 != p) } }
def LR4 : Lexicon := { LR with wordings := LR.wordings.filter (·.1 != "risk__more_severe") }
#guard LR4.failures (withoutForm FR "risk__more_severe") {} == [("V1", "predicate", "risk__more_severe")]
#guard LR4.failures FR {} == [("V1", "predicate", "risk__more_severe")]
#guard LR.failures (withoutForm FR "risk__more_severe") {} == [("V2", "predicate", "risk__more_severe")]
#guard { LR with negatives := LR.negatives ++ [("risk__class", "{0} is not {1}")] }.failures FR {} ==
  [("V2", "negative", "risk__class")]
#guard { LR with aliases := LR.aliases ++ [("leads_to", "{0} does not lead to {1}", true)] }.failures FR {} ==
  [("V2", "alias", "leads_to")]
#guard LM.valid FM {}
-- lx9b to lx9d: a modal predicate's declared, mechanical and fallback wordings are not honest
def jFMd : Json := routeEnv ["norms@0", "relational-fol@0"] ["person", "service"]
  (basePreds ++ [("access", ["person", "service"], regulated "permission" "{0} access {1}" ++ worded "{0} accesses {1}"),
    ("review", ["person", "service"], regulated "obligation" "{0} review {1}")])
  [("alice", "person"), ("legacy", "service")]
def FMd : Env := envOf jFMd
def selecting (p wording : String) : Lexicon := { LM with wordings := LM.wordings.map fun e => if e.1 == p then (p, wording) else e }
#guard LM.valid FMd {} && (selecting "access" "{0} accesses {1}").failures FMd {} == [("V2", "predicate", "access")]
#guard (selecting "access" "{0} access {1}").failures FM {} == [("V2", "predicate", "access")]
#guard (selecting "access" "{0} has the recorded relation \"access\" to {1}").failures FM {} ==
  [("V2", "predicate", "access")]
#guard LM.failures (withoutForm (withoutForm FM "access") "review") {} ==
  [("V2", "predicate", "access"), ("V2", "predicate", "review")]
-- lx11: a modal predicate has no negative
def jFMn : Json := routeEnv ["norms@0", "relational-fol@0"] ["person", "service"]
  (basePreds ++ [("access", ["person", "service"], regulated "permission" "{0} access {1}" ++
      [("negative_verbalisation", .str "{0} may not access {1}")]),
    ("review", ["person", "service"], regulated "obligation" "{0} review {1}")])
  [("alice", "person"), ("legacy", "service")]
#guard { LM with negatives := LM.negatives ++ [("access", "{0} may not access {1}")] }.failures (envOf jFMn) {} ==
  [("V5", "negative", "access")]
-- lx12, lx13: subject first
def forms23 : List String :=
  ["{0} is avoidable by {1}", "{0} is unavoidable by {1}", "{0} allows {1} to happen", "{0} prevents {1}",
   "{0} might prevent {1}", "{0} is preventable by {1}", "{0} lets {1} happen", "{0} does not lead to {1}",
   "{0} might lead to {1}", "{0} is {1}", "{0} is {1} or worse", "{0} has a less severe worst case than {1}",
   "{0} is more severe than {1}", "{0} might not lead to {1}", "{0} cannot lead to {1}", "{0} may access {1}",
   "{0} must review {1}"]
def entries (L : Lexicon) : List String := L.wordings.map (·.2) ++ L.negatives.map (·.2) ++ L.aliases.map (·.2.1)
#guard idioms1.length == 13 && idioms2.length == 25
#guard (idioms1 ++ idioms2 ++ forms23 ++ ["deployed", "owns", "x"].filterMap (mechanicalWording · 1) ++
  ["owns"].filterMap (mechanicalWording · 2) ++ ["related"].filterMap (mechanicalWording · 3) ++
  ["owns"].filterMap (fallbackWording · 1) ++ ["owns"].filterMap (fallbackWording · 2) ++
  [LF, LD, LA, LR, LM].flatMap entries ++ ["{0} {1} are related", "{0} gives {1} away"]).all subjectFirst
#guard ["the owner of {0} is {1}", "{1} follows {0}", "{1} {0} are related"].all (!subjectFirst ·)

/-! ## 8.7 Ambiguity, the combined grammar, the readability sentences -/

-- am1: a severity class spelled `safe`
def FRam : Env := { FR with constants := FR.constants.map fun d => if d.name == "minor" then { d with display := some "safe" } else d }
def LRam : Lexicon := { LR with spellings := LR.spellings.map fun e => if e.1 == "minor" then ("minor", "safe") else e }
#guard LRam.valid FRam {}
#guard verdicts FRam LRam "Wait is safe." == many && verdicts FR LR "Wait is safe." == one
-- am2: a person spelled `senior`
def FDam : Env := { FD with constants := FD.constants ++ [{ name := "bob", sort := "person", display := some "senior" }] }
def LDam : Lexicon := { LD with spellings := LD.spellings ++ [("bob", "senior")] }
#guard LDam.valid FDam {}
#guard verdicts FDam LDam "The owner_of of legacy is senior." == many &&
  verdicts FDam LDam "The owner_of of legacy is alice." == one
-- cb1: `FD`'s vocabulary with the rows of every profile and four rows that begin with `int_term`, written as Lean
-- data (the route has no family with all five profiles); 201 rules here, the stub's construction is not given
def Fcb : Env := { FD with
  profiles := ["alternatives@0", "data@0", "norms@0", "order@0", "relational-fol@0"],
  sorts := FD.sorts ++ [{ name := "action" }, { name := "agent" }, { name := "harm" }],
  predicates := FD.predicates ++ [{ name := "costs", arity := 2, args := ["service", "$int"] },
    { name := "exceeds", arity := 2, args := ["$int", "$int"] }, { name := "spent_on", arity := 2, args := ["$int", "service"] },
    { name := "available", arity := 2, args := ["service", "person"] },
    { name := "positive", arity := 1, args := ["$int"] }],
  constants := FD.constants ++ [{ name := "budget", sort := "$int" }],
  alternatives := some
    { action := "service", chooser := "person", harm := "service", available := "available", leadsTo := "owns" } }
def Lcb : Lexicon := { LD with
  wordings := LD.wordings ++ [("costs", "{0} costs {1}"), ("exceeds", "{0} exceeds {1}"), ("spent_on", "{0} is spent on {1}"),
    ("available", "{0} is available to {1}"), ("positive", "{0} is positive")],
  spellings := LD.spellings ++ [("budget", "budget")] }
def Gcb : Grammar Terminal := grammar Fcb Lcb
#guard Gcb.wf && terminatorFree Gcb && Gcb.typed sig (ty Fcb Lcb) (acts Fcb Lcb) && Gcb.rules.size == 201
#guard ((lexRows Fcb Lcb).filter (·.rhs.head? == some (.n ntIntTerm))).length == 4
#guard ["Legacy costs [budget + 1].", "The owner_of of legacy is senior.", "Every service that is deployed is reviewed.",
  "Every service available to alice costs 5."].all (verdicts Fcb Lcb · == one)
#guard verdicts FO LO "Every service is deployed or reviewed, or both." == zero &&
  verdicts FD LD "Every service is deployed or reviewed, or both." == zero &&
  verdicts Fcb Lcb "Every service is deployed or reviewed, or both." == zero
#guard verdicts FO LO
    "For every person, if that person is deployed and that person is reviewed, then that person is reviewed." == zero &&
  verdicts Fcb Lcb
    "For every person, if that person is deployed and that person is reviewed, then that person is reviewed." == zero
#guard verdicts FO LO "No service that is deployed is not reviewed." == zero &&
  verdicts FD LD "No service that is deployed is not reviewed." == zero &&
  verdicts Fcb Lcb "No service that is deployed is not reviewed." == zero

/-! ## 8.9 Admission -/

def ad (s : String) : Option (List (EFormula × Bool) × List (Nat × List Nat)) ⊕ Option Nat :=
  match admit F {} LF workBudget s with
  | .ok rs obs => .inl (some (rs, obs))
  | .noPremise i => .inr (some i)
  | .refused _ => .inr none
def dl : EFormula := u "deployed" (c "legacy")
def rv : EFormula := u "reviewed" (c "legacy")
#guard ad "Legacy is deployed. Therefore legacy is deployed." == .inl (some ([(dl, false), (dl, true)], [(1, [0])]))
#guard ad "Legacy is deployed." == .inl (some ([(dl, false)], []))
#guard ad "Therefore legacy is deployed." == .inr (some 0)
#guard ad "Therefore legacy is deployed. So legacy is deployed." == .inr (some 0)
#guard ad "Legacy is deployed. So legacy is reviewed. Legacy is reviewed. Hence legacy is deployed." ==
  .inl (some ([(dl, false), (rv, true), (rv, false), (dl, true)], [(1, [0]), (3, [0, 2])]))
#guard ad "Every sevice is reviewed." == .inr none
def marks (ms : List Bool) : List (EFormula × Bool) := ms.map (dl, ·)
#guard obligations (marks [false, true]) == [(1, [0])] && obligations (marks [true]) == [(0, [])] &&
  obligations (marks [false, true, false, true]) == [(1, [0]), (3, [0, 2])] &&
  obligations (marks [true, true]) == [(0, []), (1, [])] && obligations (marks [false, false]) == []
#guard firstChecked F {} LF workBudget [(dl, false)]
  ["Legacy is reviewed.", "Legacy is deployed", "Legacy is deployed.", "legacy is deployed."] == some 2
#guard firstChecked F {} LF workBudget [(dl, false)] ["Legacy is reviewed."] == none

/-! ## 8.10 Sizes and steps -/

#guard orderRows.size == 25 && alternativesRows.size == 8 &&
  ((lexRows FA LA).filter fun r => r.lhs == ntAltGuard || r.lhs == ntAltHead || r.tag.startsWith "term.that-other").length == 8
def size (E : Env) (L : Lexicon) : Nat × Nat :=
  ((grammar E L).rules.size, (grammar E L).rules.foldl (fun n r => n + r.rhs.length) 0)
-- `FO` has one rule more than spec 8.10's stub figure (159 and 575): `relation → "exceeds"`, which the S2
-- relation family and Python's grammar give a binary predicate over one sort, `$int` included
#guard size FO LO == (160, 576) && size FD LD == (147, 587) && size FA LA == (159, 646) && size FR LR == (185, 746)
-- sz3: 128 attributes into one sort with 128 properties: 384 rows factored, 16,512 in Python's shape
def Fsz : Env := {
  sorts := [{ name := "item" }, { name := "kind" }],
  predicates := (List.range 128).map (fun i =>
      { name := s!"attr{i}", arity := 2, args := ["item", "kind"], functional := true, total := true }) ++
    (List.range 128).map (fun i => { name := s!"prop{i}", arity := 1, args := ["kind"] }),
  constants := [], profiles := ["data@0", "relational-fol@0"] }
#guard ((Fsz.predicates.flatMap (attributeRows Fsz)) ++ Fsz.predicates.flatMap (propertyRows Fsz)).length == 384
#guard 128 * 128 + 128 == 16512
-- sz4 on `FO`, and on `FO` without `relation → "exceeds"`, which reproduces spec 8.10's stub figures
def withoutRow (G : Grammar Terminal) (tag : String) : Grammar Terminal := { G with rules := G.rules.filter (·.tag != tag) }
def stepsIn (G : Grammar Terminal) (s : String) : List (Option Nat) :=
  match lex s with
  | .error _ => []
  | .ok sents => sents.toList.map fun w => G.prepare.steps 2 workBudget w
def sz4 : List String := ["For every service that is deployed, there is a person who owns that service.",
  "Legacy costs [[budget + 1] + [2 * limit]].", "Budget is at least [limit + 1]."]
#guard sz4.map (steps FO LO) == [[some 8816], [some 8812], [some 5271]]
#guard sz4.map (stepsIn (withoutRow (grammar FO LO) "relation.exceeds")) == [[some 8801], [some 8797], [some 5262]]
#guard steps FD LD "For every service, the owner_of of that service is senior." == [some 6606]
#guard steps FA LA ("For every action named A1, for every action named A2, every other action available to robot " ++
  "excluding A1 is safe.") == [some 14503]
#guard steps FA LA "For every action, another action available to robot either is safe or leads to injury, or both." ==
  [some 12571]
#guard steps FR LR "For every action, every other action available to robot cannot lead to injury." == [some 10697]
-- sz7 to sz9: the rank certificates
#guard ({ grammar F LF with rank := ranks } : Grammar Terminal).wf && ({ grammar F LF with rank := ranksStaged } : Grammar Terminal).wf
#guard !({ grammar FO LO with rank := ranks } : Grammar Terminal).wf
#guard [["relational-fol@0"], ["closure@0", "relational-fol@0"], ["norms@0", "relational-fol@0"]].all (ranksFor · == ranks)
#guard [["order@0", "relational-fol@0"], ["data@0", "relational-fol@0"], ["alternatives@0", "norms@0", "relational-fol@0"]].all
  (ranksFor · == ranksStaged)

/-! ## 8.11 Extensions, on the decidable parts of `Extends` -/

-- ex1: one more integer constant and one more predicate
def jFOx : Json := routeEnv ["order@0", "relational-fol@0"] ["person", "service"]
  (basePreds ++ [("costs", ["service", "$int"], worded "{0} costs {1}"), ("exceeds", ["$int", "$int"], worded "{0} exceeds {1}"),
    ("archived", ["service"], worded "{0} is archived")])
  [("alice", "person"), ("legacy", "service"), ("budget", "$int"), ("limit", "$int"), ("cap", "$int")]
def FOx : Env := envOf jFOx
def LOx : Lexicon := { LO with
  wordings := LO.wordings ++ [("archived", "{0} is archived")], spellings := LO.spellings ++ [("cap", "cap")] }
#guard extendsB FO LO FOx LOx && (lexRows FO LO).all (lexRows FOx LOx).contains
#guard rd FOx LOx "Legacy costs [budget - limit]." == ok1 (costs (.add (c "budget") (.scale (-1) (c "limit")))) &&
  rd FOx LOx "Legacy costs [budget * limit]." == rej .coefficientNotNumeral
-- ex2: a new attribute whose value sort comes first renames the property nonterminals
#guard extendsB FD LD FD3 LD3
#guard ["The owner_of of legacy is alice.", "The owner_of of legacy is senior.", "The backup_of of legacy is deployed.",
  "For every service, the owner_of of that service is senior."].all fun s => rd FD LD s == rd FD3 LD3 s
#guard !(lexRows FD LD).all (lexRows FD3 LD3).contains
-- ex3: a flag changed; ex4: the profile list changed
def jFDnt : Json := routeEnv ["data@0", "relational-fol@0"] ["person", "service"]
  (basePreds ++ [("senior", ["person"], worded "{0} is senior"), ("owner_of", ["service", "person"], [("functional", .bool true)]),
    ("backup_of", ["service", "service"], flags)])
  [("alice", "person"), ("legacy", "service")]
#guard !envSubB FD (envOf jFDnt) && !envSubB F FO

/-! ## 8.12 The boundary (ev1, ev8 to ev13) -/

def grammarIdOf (ps : List String) : Option String := (Run.grammarId ps).toOption
#guard grammarIdOf ["relational-fol@0"] == grammarIdOf F.profiles && (grammarIdOf F.profiles).isSome
def idOf (j : Json) : Option String := (Run.environmentId j).toOption
#guard idOf jFA == (VE.Alternatives.Replay.environmentId ["alternatives@0", "norms@0", "relational-fol@0"] jFA).toOption &&
  (idOf jFA).isSome
#guard idOf jFR == (VE.Alternatives.Replay.environmentId ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"] jFR).toOption &&
  (idOf jFR).isSome
-- ev10: an act phrase with doubled spaces gives the same forms and the same identity
def jFMsp : Json := routeEnv ["norms@0", "relational-fol@0"] ["person", "service"]
  (basePreds ++ [("access", ["person", "service"], regulated "permission" "{0}  access   {1}"),
    ("review", ["person", "service"], regulated "obligation" "{0} review {1}")])
  [("alice", "person"), ("legacy", "service")]
#guard idOf jFMsp == idOf jFM && (idOf jFM).isSome && (envOf jFMsp).forms.wordings == FM.forms.wordings
#guard rd (envOf jFMsp) LM "Alice may access legacy." == ok1 (b "access" (c "alice") (c "legacy"))
-- ev11: the W6 unit extension on `FR`
def withUnits (j : Json) (argUnits : Json) (constUnit : Option String) : Json :=
  let vocab := j.getObjValD "vocabulary"
  let preds := vocab.getObjValD "predicates"
  let preds := preds.setObjVal! "leads_to" ((preds.getObjValD "leads_to").setObjVal! "argument_units" argUnits)
  let consts := vocab.getObjValD "constants"
  let wait := (consts.getObjValD "wait").setObjVal! "verbalisation" (.str "wait")
  let consts := consts.setObjVal! "wait" (match constUnit with
    | some t => wait.setObjVal! "unit" (.str t)
    | none => wait)
  ((j.setObjVal! "unit_schema" (.str VE.Time.Wire.schema)).setObjVal! "units"
    (Json.mkObj [("usd", Json.mkObj [("scale", .str "100"),
      ("display", Json.mkObj [("kind", .str "money"), ("currency", .str "USD")])])])).setObjVal! "vocabulary"
    ((vocab.setObjVal! "predicates" preds).setObjVal! "constants" consts)
def jFRu : Json := withUnits jFR (Json.mkObj []) none
#guard (idOf jFRu).isSome && idOf jFRu != idOf jFR &&
  idOf jFRu == (VE.Service.Standalone.environmentIdOf ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"] jFRu).toOption
#guard rd (envOf jFRu) LR "Wait might lead to injury." == ok1 (M w inj) &&
  rd (envOf jFRu) LR "Injury is catastrophic." == ok1 (b "risk__class" inj (c "catastrophic"))
-- ev12: malformed profile declarations are refused before the reader runs
def drop (j : Json) (k : String) : Json := VE.Risk.Wire.dropField k j
#guard (idOf (drop jFA "alternatives")).isNone
#guard (idOf (routeEnv ["norms@0", "relational-fol@0"] ["action", "agent", "harm"] altPreds altConsts
  [("alternatives", altBlock)])).isNone
#guard (idOf (routeEnv ["norms@0", "relational-fol@0", "risk@0"] ["action", "agent", "harm"] altPreds altConsts
  [("risk", riskBlock)])).isNone
#guard (idOf (jFA.setObjVal! "alternatives" (altBlock.setObjVal! "colour" (.str "red")))).isNone
#guard (idOf (jFA.setObjVal! "alternatives" (altBlock.setObjVal! "harm" (.str "danger")))).isNone
#guard (Env.decode (drop jFA "alternatives") (Json.mkObj [])).toOption.isNone
-- ev13: malformed unit declarations
#guard (idOf (drop jFRu "unit_schema")).isNone
#guard (idOf (withUnits jFR (Json.mkObj [("1", .str "usd")]) none)).isNone
#guard (idOf (withUnits jFR (Json.mkObj [("1", .str "eur")]) none)).isNone
#guard (idOf (withUnits jFR (Json.mkObj []) (some "usd"))).isNone

/-! E2 scanner fixtures: Unicode case folding, hyphenated tokens and word boundaries. -/
#guard pyLower "Kİ" == "ki\u0307"
#guard tokens "Audit-Case" == ["Audit-Case"]
#guard wordOccurs "foo" " foo bar"

end VE.EnglishGrammar.ProfileExamples
