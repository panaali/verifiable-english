import VE.EnglishGrammar.Extends

/-! The acceptance fixtures of docs/spec/english-lean-s2.md section 8, as `#guard` checks on the real
English grammar `grammar E L` and the reader `read`.

`F` and `LF` are base 8.5's environment (`examples/fluent/environment.json`) and lexicon; the other
environments are the variants section 8 names. Verdicts count derivations per sentence with the parser
at cap 2; outcomes are `read`'s, summarised so that they compare by `==`.
-/

namespace VE.EnglishGrammar.ReadExamples
open Lean VE.Grammar VE.EnglishGrammar

/-! ## Environments and lexicons -/

/-- A predicate declaration of a fixture: name, argument sorts, wording, negative. -/
abbrev PredSpec := String × List String × String × Option String

/-- A `ve.core@0` environment as JSON, or the `ve.core@0.1` closure one. A sort's noun is given when it
is not the sort's name. -/
def envJson (closure : Bool) (sorts : List (String × Option String)) (preds : List PredSpec)
    (consts : List (String × String)) : Json :=
  let sortEntry := fun (s : String × Option String) => (s.1, Json.mkObj ([("description", .str "A sort.")] ++
    match s.2 with
    | some n => [("verbalisation", Json.mkObj [("singular", .str n), ("plural", .str (n ++ "s"))])]
    | none => []))
  let predEntry := fun (p : PredSpec) => (p.1, Json.mkObj ([("arguments", toJson p.2.1),
    ("description", .str "A predicate."), ("verbalisation", .str p.2.2.1)] ++
    match p.2.2.2 with
    | some n => [("negative_verbalisation", .str n)]
    | none => []))
  let vocabulary := Json.mkObj [("sorts", Json.mkObj (sorts.map sortEntry)),
    ("predicates", Json.mkObj (preds.map predEntry)),
    ("constants", Json.mkObj (consts.map fun (c, s) => (c, Json.mkObj [("sort", .str s),
      ("description", .str "A constant.")])))]
  if closure then
    Json.mkObj [("language", .str "ve.core@0.1"), ("profiles", toJson ["closure@0", "relational-fol@0"]),
      ("spec_revision", .str "ve-v0.1-closure-2026-09-21"), ("vocabulary", vocabulary)]
  else
    Json.mkObj [("language", .str "ve.core@0"), ("profile", .str "relational-fol@0"),
      ("spec_revision", .str "ve-v0-draft-2026-09-20"), ("vocabulary", vocabulary)]

def emptyEnv : Env := { sorts := [], predicates := [], constants := [] }

/-- The decoded environment, with an overlay of constant display forms. -/
def env (j : Json) (displays : List (String × String) := []) : Env :=
  let overlay := Json.mkObj [("constants", Json.mkObj (displays.map fun (c, d) =>
    (c, Json.mkObj [("verbalisation", .str d)])))]
  match Env.decode j overlay with
  | .ok E => E
  | .error _ => emptyEnv

def predsF : List PredSpec :=
  [("deployed", ["service"], "{0} is deployed", none),
   ("reviewed", ["service"], "{0} is reviewed", some "{0} is not reviewed"),
   ("owns", ["person", "service"], "{0} owns {1}", some "{0} does not own {1}")]

def sortsF : List (String × Option String) := [("person", none), ("service", none)]
def constsF : List (String × String) := [("alice", "person"), ("legacy", "service")]

def F : Env := env (envJson false sortsF predsF constsF)
def FC : Env := env (envJson true sortsF predsF constsF)

def LF : Lexicon := {
  nouns := [("person", "person"), ("service", "service")],
  letters := [("person", "P"), ("service", "S")],
  wordings := [("deployed", "{0} is deployed"), ("owns", "{0} owns {1}"), ("reviewed", "{0} is reviewed")],
  negatives := [("owns", "{0} does not own {1}"), ("reviewed", "{0} is not reviewed")],
  aliases := [],
  spellings := [("alice", "alice"), ("legacy", "legacy")] }

/-- The extended `F` of e34: the services `beta` and `gamma`. -/
def F3 : Env := env (envJson false sortsF predsF (constsF ++ [("beta", "service"), ("gamma", "service")]))
def LF3 : Lexicon := { LF with spellings := LF.spellings ++ [("beta", "beta"), ("gamma", "gamma")] }

/-- `FD` of `tests/test_natural.py`: one more sort whose noun is `deployed service`. -/
def FD : Env := env (envJson false (sortsF ++ [("dservice", some "deployed service")]) predsF constsF)
def LFD : Lexicon := { LF with
  nouns := LF.nouns ++ [("dservice", "deployed service")], letters := LF.letters ++ [("dservice", "D")] }

/-- Base v2 and v3: `owns` on its fallback, without and with the declared negative. -/
def LFv2 : Lexicon := { LF with
  wordings := [("deployed", "{0} is deployed"), ("owns", "{0} has the recorded relation \"owns\" to {1}"),
    ("reviewed", "{0} is reviewed")],
  negatives := [("reviewed", "{0} is not reviewed")] }
def LFv3 : Lexicon := { LFv2 with negatives := [("owns", "{0} does not own {1}"), ("reviewed", "{0} is not reviewed")] }

/-- `F` with one more declaration and its selected wording. -/
def withPred (p : PredSpec) (consts : List (String × String) := []) : Env :=
  env (envJson false sortsF (predsF ++ [p]) (constsF ++ consts))
def lexWith (p : String) (w : String) (spellings : List (String × String) := []) : Lexicon :=
  { LF with wordings := LF.wordings ++ [(p, w)], spellings := LF.spellings ++ spellings }

/-- e51: `owner_of` over `service × person`, worded with a word first. -/
def F51 : Env := withPred ("owner_of", ["service", "person"], "the owner of {0} is {1}", none)
def L51 : Lexicon := lexWith "owner_of" "the owner of {0} is {1}"

/-- e52: `follows` over `person × person`, worded `{1}` first. -/
def F52 : Env := withPred ("follows", ["person", "person"], "{1} follows {0}", none)
def L52 : Lexicon := lexWith "follows" "{1} follows {0}"

/-- e53: `related` over `person × person`, worded `{1} {0} are related`, with the persons `bob` and
`alice bob`. -/
def F53 : Env := env (envJson false sortsF (predsF ++ [("related", ["person", "person"], "{1} {0} are related", none)])
  (constsF ++ [("bob", "person"), ("alicebob", "person")])) [("alicebob", "alice bob")]
def L53 : Lexicon := lexWith "related" "{1} {0} are related" [("bob", "bob"), ("alicebob", "alice bob")]

/-- c1 to c3: a service constant displayed `the api`. -/
def Fapi : Env := env (envJson false sortsF predsF (constsF ++ [("api", "service")])) [("api", "the api")]
def Lapi : Lexicon := { LF with spellings := LF.spellings ++ [("api", "the api")] }

/-- l4: `deployed` declared `{0} is v1.2 compliant` and selected. -/
def F4 : Env := env (envJson false sortsF
  [("deployed", ["service"], "{0} is v1.2 compliant", none), predsF[1]!, predsF[2]!] constsF)
def L4 : Lexicon := { LF with
  wordings := [("deployed", "{0} is v1.2 compliant"), ("owns", "{0} owns {1}"), ("reviewed", "{0} is reviewed")] }

/-! ## Verdicts and outcomes -/

inductive V where
  | lexError (r : Reject)
  | budget
  | count (n : Nat)
  deriving DecidableEq, Repr

/-- The number of derivations of each sentence (cap 2), or the lexer's rejection. -/
def verdicts (E : Env) (L : Lexicon) (s : String) : List V :=
  match lex s with
  | .error r => [.lexError r]
  | .ok sents => sents.toList.map fun w =>
      match parse (grammar E L) 2 workBudget w with
      | none => .budget
      | some ts => .count ts.length

def one : List V := [.count 1]
def zero : List V := [.count 0]
def many : List V := [.count 2]

/-- A sentence outcome without its trees. -/
inductive O where
  | ok | none | many | rejected (r : Reject) | budget
  deriving DecidableEq, Repr

/-- `read`'s outcome without trees. -/
inductive R where
  | ok (rs : List (EFormula × Bool))
  | invalid (g : GrammarFault)
  | lexical (r : Reject)
  | stopped (i : Nat) (o : O)
  | illTyped
  deriving DecidableEq, Repr

def summary : ReadOutcome → R
  | .ok rs => .ok rs
  | .invalidGrammar g => .invalid g
  | .lexical r => .lexical r
  | .stopped i o => .stopped i (match o with
    | .ok _ _ => .ok
    | .noDerivation => .none
    | .ambiguous _ _ => .many
    | .rejected r => .rejected r
    | .budget => .budget)
  | .illTyped => .illTyped

def rd (E : Env) (L : Lexicon) (s : String) : R := summary (read E {} L workBudget s)

def rej (r : Reject) (i : Nat := 0) : R := .stopped i (.rejected r)

/-! Formula shorthands. -/
def u (p : String) (t : ETerm) : EFormula := .pred p [t]
def b (p : String) (t t2 : ETerm) : EFormula := .pred p [t, t2]
def c (x : String) : ETerm := .const x
def v (i : Nat) : ETerm := .var i
def ok1 (A : EFormula) : R := .ok [(A, false)]

/-! ## The grammar of `F` and `LF` (spec 8.1, section 12) -/

#guard LF.valid F {} && LF.failures F {} == []
#guard (grammar F LF).rules.size == 117 && (fixedRules F.profiles).size == 88 && (lexRules F LF).size == 29
#guard (grammar F LF).rules.foldl (fun n r => n + r.rhs.length) 0 == 479
#guard (grammar F LF).wf && terminatorFree (grammar F LF)
#guard (grammar F LF).typed sig (ty F LF) (acts F LF)
#guard ntNames.size == 37 && ranks.size == 37
#guard (relationalFolRows.toList.map (·.rhs.length)).foldl max 0 == 28
-- every fixed action fits its row: no fixed rule is refused by the typed check
#guard (relationalFolRows.toList.zip fixedActs.toList).all fun (r, a) =>
  @decide (a.args = rhsTys r.rhs) (@instDecidableEqList _ sig.decEq _ _) && @decide (a.out = ntTy r.lhs) (sig.decEq _ _)
-- the tags of the fixed table are distinct
#guard (relationalFolRows.toList.map (·.tag)).eraseDups.length == 88

/-! ## 8.1 Verdicts -/

#guard verdicts F LF "Every service is reviewed." == one
#guard verdicts F LF "Every service that is deployed is reviewed." == one
#guard verdicts F LF "For every service that is deployed, there is a person who owns that service." == one
#guard verdicts F LF "Alice owns legacy." == one
#guard verdicts F LF "Legacy is not reviewed." == one
#guard verdicts F LF "Both legacy is deployed and legacy is reviewed." == one
#guard verdicts F LF "Legacy is deployed. It is reviewed." == [.count 1, .count 1]
#guard verdicts F LF "Legacy is deployed. Therefore legacy is deployed." == [.count 1, .count 1]
#guard verdicts F LF "For every service named S1, S1 is reviewed." == one
#guard verdicts F LF "There is a service such that that service is deployed." == one
#guard verdicts F LF "If legacy is deployed, then legacy is reviewed." == one
#guard verdicts F LF "Either legacy is deployed or legacy is reviewed, or both." == one
#guard verdicts F LF "This holds in all cases." == one
#guard verdicts F LF "Legacy is the same as legacy." == one
#guard verdicts F LF "It is not the case that legacy is deployed." == one
#guard verdicts F LF "For every person who owns legacy, that person owns legacy." == one
#guard verdicts F LF "Every person who owns legacy owns legacy." == one
#guard verdicts F LF "For every service that is deployed and is reviewed, and is deployed, that service is reviewed." == one
#guard verdicts F LF "For every service that is deployed, and is reviewed and is deployed, that service is reviewed." == one
#guard verdicts F LF "Every service that alice owns is reviewed." == one
#guard verdicts F LF "All of the following hold: first clause: legacy is deployed; end first clause; second clause: legacy is reviewed; end second clause." == one
#guard verdicts F LF "Both of the following hold: (a) legacy is deployed; (b) legacy is reviewed." == one
#guard verdicts F LF "If the following holds: (a) legacy is deployed; then the following holds: (b) legacy is reviewed." == one
#guard verdicts F LF "EVERY service is reviewed." == zero
#guard verdicts F LF "Every sevice is reviewed." == zero
#guard verdicts F LF "Every service is reviewed" == [.lexError .unterminated]
#guard verdicts F LF "Every service is deployed or reviewed, or both." == zero
#guard verdicts F LF "For every person, if that person is deployed and that person is reviewed, then that person is reviewed." == zero
#guard verdicts F LF "No service that is deployed is not reviewed." == zero
#guard verdicts F LF "Either legacy is deployed or legacy is reviewed , or both." == zero
#guard verdicts F LF "For every service that is deployed , there is a person who owns that service." == zero
#guard verdicts F LF "Alice does not own legacy." == one
#guard verdicts F LF "Every person who does not own legacy owns legacy." == one
#guard verdicts F LF "Legacy, alice and legacy are deployed." == one
#guard verdicts F LF "Legacy is deployed, reviewed and deployed." == one
#guard verdicts F LF "Some service is deployed." == one
#guard verdicts F LF "No service is deployed." == one
#guard verdicts F LF "Every deployed service is reviewed." == one
#guard verdicts F LF "Every deployed service has an owner." == one
#guard verdicts F LF "Every service has an owner." == one
#guard verdicts F LF "Every deployed service is reviewed and has an owner." == one
#guard verdicts F LF "Some service is deployed and reviewed." == one
#guard verdicts F LF "Some service is deployed and is reviewed." == one
#guard verdicts F LF "Every deployed service is not reviewed." == one
#guard verdicts F LF "Starting from legacy, legacy is reachable by one or more \"owns\" steps." == zero
#guard verdicts F LF "Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a service satisfies this condition: that service is deployed." == one
#guard verdicts F LF "Starting from legacy, legacy is reachable by one or more steps, where a step from a service to a service satisfies the following: (a) that service is deployed." == one
#guard verdicts F LF "It, alice and legacy are deployed." == one
#guard verdicts F LF "For every service named P1, P1 is reviewed." == one
#guard verdicts F LF "Every deployed service is not reviewed and has an owner." == one
#guard verdicts F LF "Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a second service satisfies this condition: that service is deployed." == one
#guard verdicts F LF "Starting from legacy, legacy is reachable by one or more steps, where a step from a service to a second service satisfies the following: (a) that service is deployed." == one
#guard verdicts F3 LF3 "For every person, legacy, beta and gamma are deployed." == one
#guard verdicts F3 LF3 "The legacy, beta and gamma are deployed." == one
#guard verdicts F LF "Legacy is deployed. It, alice and legacy are deployed." == [.count 1, .count 1]
#guard verdicts F3 LF3 "Legacy, beta and gamma are deployed." == one

-- d1 to d4: the constructed ambiguity under `FD`
#guard LFD.valid FD {}
#guard verdicts FD LFD "Every deployed service is reviewed." == many
#guard verdicts FD LFD "It is not the case that every deployed service is reviewed." == many
#guard verdicts FD LFD "Every DEPLOYED service is reviewed." == many
#guard verdicts FD LFD "Every service is reviewed." == one
#guard rd FD LFD "Every deployed service is reviewed." == .stopped 0 .many

-- k1, k2: W4 in both directions on grammars built by hand
def GW4bad : Grammar Terminal :=
  { rules := #[{ lhs := 0, rhs := [.t (.kw "x"), .t (.exact (.punct "." false false))], act := 0, tag := "" }],
    start := 0, rank := #[0] }
def GW4ok : Grammar Terminal := { rules := #[{ lhs := 0, rhs := [.t (.kw "x")], act := 0, tag := "" }], start := 0, rank := #[0] }
#guard GW4bad.wf && !terminatorFree GW4bad
#guard GW4ok.wf && terminatorFree GW4ok

-- c1 to c3: the capitalised spelling of a constant spelled `the api` (`kwMid`)
#guard Lapi.valid Fapi {}
#guard verdicts Fapi Lapi "The api is reviewed." == one
#guard verdicts Fapi Lapi "Alice owns The api." == one
#guard verdicts Fapi Lapi "Alice owns the api." == one
#guard rd Fapi Lapi "Alice owns The api." == ok1 (b "owns" (c "alice") (c "api"))
#guard rd Fapi Lapi "The api is reviewed." == ok1 (u "reviewed" (c "api"))

/-! ## 8.2 Meanings -/

#guard rd F LF "Every service is reviewed." == ok1 (.all "service" (u "reviewed" (v 0)))
#guard rd F LF "Alice owns legacy." == ok1 (b "owns" (c "alice") (c "legacy"))
#guard rd F LF "Legacy is not reviewed." == ok1 (.not (u "reviewed" (c "legacy")))
#guard rd F LF "Alice does not own legacy." == ok1 (.not (b "owns" (c "alice") (c "legacy")))
#guard rd F LF "Legacy is deployed. It is reviewed." ==
  .ok [(u "deployed" (c "legacy"), false), (u "reviewed" (c "legacy"), false)]
#guard rd F LF "For every service named S1, S1 is reviewed." == ok1 (.all "service" (u "reviewed" (v 0)))
#guard rd F LF "There is a service such that that service is deployed." == ok1 (.ex "service" (u "deployed" (v 0)))
#guard rd F LF "If legacy is deployed, then legacy is reviewed." ==
  ok1 (.implies (u "deployed" (c "legacy")) (u "reviewed" (c "legacy")))
#guard rd F LF "Either legacy is deployed or legacy is reviewed, or both." ==
  ok1 (.or (u "deployed" (c "legacy")) (u "reviewed" (c "legacy")))
#guard rd F LF "This holds in all cases." == ok1 .top
#guard rd F LF "Legacy is the same as legacy." == ok1 (.eq (c "legacy") (c "legacy"))
#guard rd F LF "For every person who owns legacy, that person owns legacy." ==
  ok1 (.all "person" (.implies (b "owns" (v 0) (c "legacy")) (b "owns" (v 0) (c "legacy"))))
#guard rd F LF "Every person who does not own legacy owns legacy." ==
  ok1 (.all "person" (.implies (.not (b "owns" (v 0) (c "legacy"))) (b "owns" (v 0) (c "legacy"))))
-- e29, e30: the two associations of the three-atom guards
#guard rd F LF "For every service that is deployed and is reviewed, and is deployed, that service is reviewed." ==
  ok1 (.all "service" (.implies (.and (.and (u "deployed" (v 0)) (u "reviewed" (v 0))) (u "deployed" (v 0)))
    (u "reviewed" (v 0))))
#guard rd F LF "For every service that is deployed, and is reviewed and is deployed, that service is reviewed." ==
  ok1 (.all "service" (.implies (.and (u "deployed" (v 0)) (.and (u "reviewed" (v 0)) (u "deployed" (v 0))))
    (u "reviewed" (v 0))))
-- e31: the object relative
#guard rd F LF "Every service that alice owns is reviewed." ==
  ok1 (.all "service" (.implies (b "owns" (c "alice") (v 0)) (u "reviewed" (v 0))))
-- e32, e33: listings and their markers
#guard rd F LF "All of the following hold: first clause: legacy is deployed; end first clause; second clause: legacy is reviewed; end second clause." ==
  ok1 (.and (u "deployed" (c "legacy")) (u "reviewed" (c "legacy")))
#guard rd F LF "Both of the following hold: (a) legacy is deployed; (b) legacy is reviewed." ==
  ok1 (.and (u "deployed" (c "legacy")) (u "reviewed" (c "legacy")))
#guard rd F LF "Both of the following hold: (i) legacy is deployed; (ii) legacy is reviewed." == rej .markerDepth
#guard rd F LF "Both of the following hold: (a) both of the following hold: (i) legacy is deployed; (ii) legacy is reviewed; (b) legacy is reviewed." ==
  ok1 (.and (.and (u "deployed" (c "legacy")) (u "reviewed" (c "legacy"))) (u "reviewed" (c "legacy")))
#guard rd F LF "Both of the following hold: (a) both of the following hold: (a) legacy is deployed; (b) legacy is reviewed; (b) legacy is reviewed." ==
  rej .markerDepth
-- e34, e35: coordination
#guard rd F LF "Legacy, alice and legacy are deployed." == rej .coordinationRepeated
#guard rd F3 LF3 "Legacy, beta and gamma are deployed." ==
  ok1 (.and (u "deployed" (c "legacy")) (.and (u "deployed" (c "beta")) (u "deployed" (c "gamma"))))
#guard rd F3 LF3 "Legacy, alice and beta are deployed." == rej .sortMismatch
#guard rd F3 LF3 "Legacy, beta or gamma is deployed." ==
  ok1 (.or (u "deployed" (c "legacy")) (.or (u "deployed" (c "beta")) (u "deployed" (c "gamma"))))
#guard rd F LF "Legacy is deployed, reviewed and deployed." == rej .coordinationRepeated
#guard rd F LF "Legacy is deployed, reviewed and not reviewed." == .stopped 0 .none
-- e36 to e41: the natural clauses
#guard rd F LF "Some service is deployed." == ok1 (.ex "service" (u "deployed" (v 0)))
#guard rd F LF "No service is deployed." == ok1 (.not (.ex "service" (u "deployed" (v 0))))
#guard rd F LF "Every deployed service is reviewed." ==
  ok1 (.all "service" (.implies (u "deployed" (v 0)) (u "reviewed" (v 0))))
#guard rd F LF "Every deployed service has an owner." ==
  ok1 (.all "service" (.implies (u "deployed" (v 0)) (.ex "person" (b "owns" (v 0) (v 1)))))
#guard rd F LF "Every service has an owner." == ok1 (.all "service" (.ex "person" (b "owns" (v 0) (v 1))))
#guard rd F LF "Every deployed service is reviewed and has an owner." ==
  ok1 (.all "service" (.implies (u "deployed" (v 0)) (.and (u "reviewed" (v 0)) (.ex "person" (b "owns" (v 0) (v 1))))))
#guard rd F LF "Some service is deployed and reviewed." ==
  ok1 (.ex "service" (.and (u "deployed" (v 0)) (u "reviewed" (v 0))))
#guard rd F LF "Some service is deployed and is reviewed." ==
  ok1 (.ex "service" (.and (u "deployed" (v 0)) (u "reviewed" (v 0))))
#guard rd F LF "Every deployed service is not reviewed." == rej (.blockedWording "natural-negation")
-- e42: a natural clause under a binder
#guard rd F LF "For every person, some service is deployed." == rej .naturalScoped
-- e43: reach
#guard rd F LF "Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a service satisfies this condition: that service is deployed." ==
  rej .shadowedName
#guard rd F LF "Starting from legacy, legacy is reachable by one or more steps, where a step from a service to a service satisfies the following: (a) that service is deployed." ==
  rej .shadowedName
#guard rd F LF "Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a second service satisfies this condition: that service is deployed." ==
  .illTyped
#guard rd F LF "Starting from legacy, legacy is reachable by one or more steps, where a step from a service to a second service satisfies the following: (a) that service is deployed." ==
  .illTyped
#guard rd FC LF "Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a second service satisfies this condition: that service is deployed." ==
  ok1 (.reachBody true "service" (u "deployed" (v 1)) (c "legacy") (c "legacy"))
#guard rd FC LF "Starting from legacy, legacy is reachable by one or more steps, where a step from a service to a second service satisfies the following: (a) that service is deployed." ==
  ok1 (.reachBody false "service" (u "deployed" (v 1)) (c "legacy") (c "legacy"))
#guard rd FC LF "Starting from legacy, alice is reachable by one or more steps, where a step from a service to a second person satisfies this condition: that service is deployed." ==
  rej .sortMismatch
-- e44 to e46: the `it` rule
#guard rd F LF "Legacy is deployed. Therefore it is deployed." ==
  .ok [(u "deployed" (c "legacy"), false), (u "deployed" (c "legacy"), true)]
#guard rd F LF "Legacy is deployed. Alice owns it." == rej .pronounUnresolved 1
#guard rd F LF "Legacy is deployed. For every service, it is reviewed." == rej .pronounUnresolved 1
#guard rd F LF "Some service is deployed. It is reviewed." == rej .pronounUnresolved 1
#guard rd F LF "Alice owns legacy. It is reviewed." == rej .pronounUnresolved 1
-- an earlier binder blocks `it` even with one referent (`_has_discourse_binder`); a reach body binds nothing
#guard rd F LF "Legacy is deployed. Some service is deployed. It is reviewed." == rej .pronounUnresolved 2
#guard rd F LF "Legacy is deployed. Legacy is reviewed. It is reviewed." ==
  .ok [(u "deployed" (c "legacy"), false), (u "reviewed" (c "legacy"), false), (u "reviewed" (c "legacy"), false)]
#guard rd FC LF "Legacy is deployed. Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a second service satisfies this condition: that service is deployed. It is reviewed." ==
  .ok [(u "deployed" (c "legacy"), false),
    (.reachBody true "service" (u "deployed" (v 1)) (c "legacy") (c "legacy"), false), (u "reviewed" (c "legacy"), false)]
-- the nesting limit (`english.py:1369`): 63 negations are read, 64 exceed 64 levels
def negations (k : Nat) : String :=
  "It is not the case that " ++ String.join (List.replicate (k - 1) "it is not the case that ") ++ "legacy is deployed."
#guard rd F LF (negations 63) == ok1 (Nat.repeat EFormula.not 63 (u "deployed" (c "legacy")))
#guard rd F LF (negations 64) == rej .nestingLimit
-- e48 to e50
#guard rd F LF "For every service named P1, P1 is reviewed." == rej .sortMismatch
#guard rd F LF "Every deployed service is not reviewed and has an owner." == rej (.blockedWording "natural-negation")
#guard rd F LF "It, alice and legacy are deployed." == rej .pronounUnresolved
#guard rd F3 LF3 "For every person, legacy, beta and gamma are deployed." == rej .coordinationForm
#guard rd F3 LF3 "The legacy, beta and gamma are deployed." == rej .coordinationForm
#guard rd F LF "Legacy is deployed. It, alice and legacy are deployed." == rej .coordinationForm 1
-- e51 to e53: the subject relatives of wordings that do not begin with `{0}`
#guard L51.valid F51 {}
#guard verdicts F51 L51 "Every service that the owner of that service is alice is reviewed." == one
#guard rd F51 L51 "Every service that the owner of that service is alice is reviewed." == .illTyped
#guard L52.valid F52 {}
#guard verdicts F52 L52 "Every person who follows alice owns legacy." == one
#guard rd F52 L52 "Every person who follows alice owns legacy." == rej .relativeForm
#guard rd F52 L52 "Bob follows alice." == .stopped 0 .none
#guard rd F52 L52 "Alice follows alice." == ok1 (b "follows" (c "alice") (c "alice"))
#guard L53.valid F53 {}
#guard verdicts F53 L53 "Every person alice bob are related." == one
#guard rd F53 L53 "Every person alice bob are related." == rej .relativeForm
#guard rd F53 L53 "Bob alice are related." == ok1 (b "related" (c "alice") (c "bob"))

/-! ## 8.3 Lexicon and mutation replay -/

#guard LFv2.valid F {}
#guard !LFv3.valid F {} && LFv3.failures F {} == [("V5", "negative", "owns")]
#guard verdicts F LFv2 "Alice owns legacy." == zero
#guard verdicts F LFv2 "Alice has the recorded relation \"owns\" to legacy." == one
#guard verdicts F LFv2 "For every service that is deployed, there is a person who owns that service." == zero
#guard verdicts F LFv2 "Every service is reviewed." == one
#guard verdicts F LFv2 "Legacy is deployed. It is reviewed." == [.count 1, .count 1]
#guard rd F LFv2 "Alice has the recorded relation \"owns\" to legacy." == ok1 (b "owns" (c "alice") (c "legacy"))
#guard rd F LFv3 "Alice owns legacy." == .invalid .lexicon
-- l4: a wording that lexes as two sentences is not valid (V3)
#guard !L4.valid F4 {} && L4.failures F4 {} == [("V3", "predicate", "deployed")]

/-! ## 8.4 Translation mode -/

def tr (E : Env) (L : Lexicon) (cap : Nat) (s : String) : Option (Nat × Bool) :=
  match translate E {} L cap workBudget s with
  | .readings rs complete => some (rs.length, complete)
  | _ => none

-- under `FD`, d1's two trees both have a meaning
#guard tr FD LFD 2 "Every deployed service is reviewed." == some (2, false)
#guard tr FD LFD 3 "Every deployed service is reviewed." == some (2, true)
#guard tr F LF 2 "Every service is reviewed." == some (1, true)
#guard (match translate F {} LF 2 workBudget "Legacy is deployed. Legacy is reviewed." with
  | .notOneSentence => true
  | _ => false)
#guard (match translate F {} LF 0 workBudget "Every service is reviewed." with
  | .readings [] false => true
  | _ => false)

/-! ## 8.5 The widenings, measured on the derivation counts -/

/-- The three proposed rules of spec 2.12; not in the generated table. -/
def widenings : List (Rule Terminal) :=
  [{ lhs := ntAtom, act := 0, tag := "widen.or-both.adjectives",
     rhs := [.n ntTerm, .t (.kw "is"), .n ntAdjective, .t (.kw "or"), .n ntAdjective,
       .t (.exact (.punct "," true false)), .t (.kw "or"), .t (.kw "both")] },
   { lhs := ntRelative, act := 0, tag := "widen.or-both.relative",
     rhs := [.t (.kw "is"), .n ntAdjective, .t (.kw "or"), .n ntAdjective,
       .t (.exact (.punct "," true false)), .t (.kw "or"), .t (.kw "both")] },
   { lhs := 5, act := 0, tag := "widen.if-and-then",
     rhs := [.t (.kw "if"), .n ntAtom, .t (.kw "and"), .n ntAtom, .t (.exact (.punct "," true false)),
       .t (.kw "then"), .n 2] }]

def GFw : Grammar Terminal := { grammar F LF with rules := (grammar F LF).rules ++ widenings.toArray }

def wverdict (s : String) : List V :=
  match lex s with
  | .error r => [.lexError r]
  | .ok sents => sents.toList.map fun w =>
      match parse GFw 2 workBudget w with
      | none => .budget
      | some ts => .count ts.length

#guard GFw.wf && terminatorFree GFw
#guard wverdict "Every service is deployed or reviewed, or both." == one
#guard wverdict "For every person, if that person is deployed and that person is reviewed, then that person is reviewed." == one
#guard wverdict "Either legacy is deployed or legacy is reviewed, or both." == one
#guard wverdict "If legacy is deployed, then legacy is reviewed." == one
#guard wverdict "Legacy is deployed, reviewed and deployed." == one
#guard wverdict "Every service that is deployed is reviewed." == one
#guard wverdict "No service that is deployed is not reviewed." == zero

/-! ## 8.6 Steps -/

def steps (E : Env) (L : Lexicon) (s : String) : List (Option Nat) :=
  match lex s with
  | .error _ => []
  | .ok sents => sents.toList.map fun w => (grammar E L).prepare.steps 2 workBudget w

#guard steps F LF "For every service that is deployed, there is a person who owns that service." == [some 7331]
#guard steps F LF "All of the following hold: first clause: legacy is deployed; end first clause; second clause: legacy is reviewed; end second clause." == [some 13162]
#guard steps FD LFD "Every deployed service is reviewed." == [some 2514]

/-! ## 8.7 Extensions, on the decidable parts of `Extends` -/

/-- `envSub` and `lexiconSub` as Boolean checks, for the fixtures. -/
def envSubB (E E2 : Env) : Bool :=
  E.profiles == ["relational-fol@0"] && E2.profiles == E.profiles &&
  E.sorts.all (fun s => E2.sorts.any (·.name == s.name)) &&
  E.predicates.all (fun p => E2.predicates.any fun q => q.name == p.name && q.arity == p.arity && q.args == p.args) &&
  E.constants.all (fun d => E2.constants.any fun d2 => d2.name == d.name && d2.sort == d.sort)

def lexiconSubB (L L2 : Lexicon) : Bool :=
  L.nouns.all (L2.nouns.contains ·) && L.letters.all (L2.letters.contains ·) &&
  L.wordings.all (L2.wordings.contains ·) && L.negatives.all (L2.negatives.contains ·) &&
  L.aliases.all (L2.aliases.contains ·) && L.spellings.all (L2.spellings.contains ·)

def extendsB (E : Env) (L : Lexicon) (E2 : Env) (L2 : Lexicon) : Bool :=
  envSubB E E2 && lexiconSubB L L2 && L.valid E {} && L2.valid E2 {}

-- q5: `reviewed` and `audited` on their fallbacks
def F2 : Env := withPred ("audited", ["service"], "{0} is audited", none)
def LF2fb : Lexicon := { LF with
  wordings := [("audited", "{0} is classified as \"audited\""), ("deployed", "{0} is deployed"),
    ("owns", "{0} owns {1}"), ("reviewed", "{0} is classified as \"reviewed\"")],
  negatives := [("owns", "{0} does not own {1}")] }
#guard LF2fb.valid F2 {}
#guard !extendsB F LF F2 LF2fb
#guard verdicts F2 LF2fb "Legacy is reviewed." == zero
-- q6: `archived` added with its own wording
def F6 : Env := withPred ("archived", ["service"], "{0} is archived", none)
def L6 : Lexicon := lexWith "archived" "{0} is archived"
#guard extendsB F LF F6 L6
#guard (lexRows F LF).all (lexRows F6 L6).contains
#guard verdicts F6 L6 "Every service that is deployed is reviewed." == one
#guard verdicts F6 L6 "It, alice and legacy are deployed." == one
#guard verdicts F6 L6 "Every deployed service is not reviewed and has an owner." == one
-- q7: `owns` re-declared over `service × person`
def F7 : Env := env (envJson false sortsF
  [predsF[0]!, predsF[1]!, ("owns", ["service", "person"], "{0} owns {1}", some "{0} does not own {1}")] constsF)
#guard LF.valid F7 {}
#guard !extendsB F LF F7 LF
#guard !(lexRows F LF).all (lexRows F7 LF).contains

/-! ## The wire form (e47, the Lean half) -/

#guard (EFormula.all "service" (.implies (u "deployed" (v 0)) (.ex "person" (b "owns" (v 0) (v 1))))).encode.compress ==
  "[\"forall\",\"service\",[\"implies\",[\"unary\",\"deployed\",[\"var\",0]],[\"exists\",\"person\",[\"binary\",\"owns\",[\"var\",0],[\"var\",1]]]]]"
#guard (EFormula.reachBody true "service" (u "deployed" (v 1)) (c "legacy") (c "legacy")).encode.compress ==
  "[\"reach\",\"star\",[\"body\",\"service\",[\"unary\",\"deployed\",[\"var\",1]]],[\"const\",\"legacy\"],[\"const\",\"legacy\"]]"
#guard (EFormula.pred "owner_of" [v 0, v 0, c "alice"]).encode.compress ==
  "[\"atom\",\"owner_of\",[[\"var\",0],[\"var\",0],[\"const\",\"alice\"]]]"

/-! ## The document state -/

#guard (DState.init.after (.and (u "deployed" (c "legacy")) (b "owns" (c "alice") (c "legacy")))) ==
  ⟨["alice", "legacy"], false⟩
#guard (DState.init.after (.not (.ex "service" (u "deployed" (v 0))))).binderSeen
#guard (DState.init.after (.pred "owner_of" [v 0, c "legacy", c "alice"])).referents == []

end VE.EnglishGrammar.ReadExamples
