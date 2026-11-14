import VE.Acts.DecodeExamples
import VE.Acts.HookTwins

/-! The acts hook (kb-4a), computed: what each instance of `Norms.Wire.ActsHook` answers and where the norms mode's
dispatch sends a case. The equality theorems are `VE.Acts.HookToday` and `VE.Acts.HookTwins`; these checks pin the
behaviours they relate. The fixtures are those of `VE.Service.ActsExamples` (A1-A3 of act-phrases 11.1) and
`VE.Acts.DecodeExamples` (the joined act A6), built here so that this module imports no service mode. -/

namespace VE.Acts.HookExamples
open Lean VE.Norms.Wire
open VE.Acts.DecodeExamples (norms27 manyEnv manyRules envOf plain6 block6)

def a1 := "{0} in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"
def a2 := "{0} to equal pay for equal work without any discrimination"
def a3 := "{0} to the protection of the moral and material interests resulting from {1}"
def fxs : List String := ["a fair and public hearing by an independent and impartial tribunal",
  "equal pay for equal work", "the moral and material interests"]
def desc (d : String) : Json := Json.mkObj [("description", .str d)]
def pred (args : List String) (reg : List (String × Json)) : Json :=
  Json.mkObj [("arguments", toJson args), ("description", .str "d"), ("regulated", Json.mkObj reg)]
def plainReg (act form : String) : List (String × Json) :=
  [("role", .str "plain"), ("default", .str "deny"), ("act", .str act), ("form", .str form)]
def perm (act : String) : List (String × Json) := [("role", .str "permission"), ("default", .str "allow"), ("act", .str act)]
/-- An environment with `profiles`, the predicates `preds`, the constants `consts` and, when given, the `acts` block. -/
def env (profiles : List String) (preds : List (String × Json)) (acts : Option Json := none)
    (consts : List (String × Json) := []) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj ([("sorts", Json.mkObj [("person", desc "person"), ("case", desc "case")]),
      ("predicates", Json.mkObj preds), ("constants", Json.mkObj consts)] ++ acts.toList.map ("acts", ·)))]
def block (fx : List String) : Json := Json.mkObj [("fixed", toJson fx)]
def actsP : List String := ["acts@0", "norms@0", "relational-fol@0"]
/-- A1, A2 (plain, with their forms) and A3 (a permission), with their fixed phrases. -/
def envA (profiles : List String := actsP) : Json :=
  env profiles [("heard", pred ["person", "case"] (plainReg a1 "is entitled")),
    ("paid", pred ["person"] (plainReg a2 "has the right")), ("protected", pred ["person", "case"] (perm a3))]
    (some (block fxs))
def err {α} (e : Except String α) : String := match e with | .error m => m | .ok _ => "ok"
def rule (p : String) : Json := Json.mkObj [("norm", Json.mkObj [("name", .str "m"), ("predicate", .str p),
  ("sign", .bool true), ("guard", Json.arr #[.str "top"]), ("unless", Json.arr #[]), ("over", Json.arr #[])])]
def seek : List (String × Json) := [("p", pred ["person"] (perm "{0} seek asylum"))]
def unsorted : List (List String) := [["norms@0", "acts@0", "relational-fol@0"],
  ["acts@0", "acts@0", "norms@0", "relational-fol@0"], ["relational-fol@0", "acts@0", "norms@0"]]
def sortedRefusal := "UnsupportedProfile: profiles must be sorted and unique"
/-- A6 as a joined act under its frames (`DecodeExamples.envOf`). -/
def joinedE : Json := envOf plain6 block6 (default := "deny")
def caseOf (kind : String) (j : Json) : Json :=
  Json.mkObj [("id", .str "c"), ("kind", .str kind), ("environment", j), ("norms", norms27)]
def elabCase (j : Json) (norms : Json) : Json :=
  Json.mkObj [("id", .str "c"), ("kind", .str "acts-elaborate"), ("environment", j), ("norms", norms)]
def d4 : String := "InvalidInput: act phrase for p027 joins acts with 'or' outside a fixed phrase"

/-- A norms environment without `acts@0`: one permission with a plain act. -/
def plainEnv : Json := env ["norms@0", "relational-fol@0"] seek
def acts (j : Json) (joined : Bool := false) := decodeNormsEnvironmentWith ActsHook.acts j (acts := true) (joined := joined)
def plainD (j : Json) (acts : Bool := true) := decodeNormsEnvironmentWith ActsHook.plain j (acts := acts)
def lexical (j : Json) (joined : Bool := false) :=
  decodeNormsEnvironmentWith ActsHook.lexical j (acts := true) (joined := joined)
def view (e : Except String NormsEnvironment) : Option (List (Option String) × List String × List String) :=
  e.toOption.map fun ne => (ne.regulated.map (·.act), ne.profiles, ne.joined.map (·.1))

/-! ### `ActsHook.plain`: refuses an environment from which `acts@0` is read; elsewhere it is today's decoder -/

-- an `acts@0` environment the acts instance reads is refused, before anything else is read
#guard (view (acts envA)).isSome
#guard err (plainD envA) == actsHookRefusal
#guard err (plainD joinedE) == actsHookRefusal
-- without `acts` the profile is not read: both instances leave the envelope's refusal, as today
#guard err (plainD envA (acts := false)) == "UnsupportedProfile: Unsupported profile acts@0"
#guard err (decodeNormsEnvironmentWith ActsHook.acts envA) == err (plainD envA (acts := false))
-- an unsorted list that lists `acts@0` is not read from either: the envelope's refusal, as today
#guard unsorted.all fun ps => err (plainD (envA ps)) == sortedRefusal && err (acts (envA ps)) == sortedRefusal
-- a document without `acts@0`: the same declarations, profiles and (no) joined acts as the acts instance
#guard view (plainD plainEnv) == view (acts plainEnv)
#guard view (plainD plainEnv) == some ([some "{0} seek asylum"], ["norms@0", "relational-fol@0"], [])
-- an act `canonicalAct` refuses is refused by the plain instance with its text
#guard err (plainD (env ["norms@0", "relational-fol@0"] [("p", pred ["person"] (perm "{0}"))])) ==
  err (acts (env ["norms@0", "relational-fol@0"] [("p", pred ["person"] (perm "{0}"))]))
#guard err (plainD (env ["norms@0", "relational-fol@0"] [("p", pred ["person"] (perm "{0}"))])) != "ok"

/-! ### `ActsHook.lexical`: the acts instance without its joined-act reader -/

-- without joined acts it is the acts instance: a lexical act read under `acts@0`, a joined one refused with D-4
#guard view (lexical envA) == view (acts envA)
#guard err (lexical joinedE) == d4 && err (acts joinedE) == d4
-- with joined acts admitted the acts instance reads each joined act's meaning; the lexical one reads none
#guard ((decodeSource ActsHook.acts (manyEnv 1) (manyRules 1)).toOption.map (·.ne.joined.map (·.1))) == some ["p0"]
#guard ((decodeSource ActsHook.lexical (manyEnv 1) (manyRules 1)).toOption.map (·.ne.joined.map (·.1))) == some []

/-! ### Today's name (`decodeNormsEnvironment`, which lean/VE/EnglishGrammar/Norm/Rules.lean calls): its defaults -/

-- `acts := false`: `acts@0` is not read; `joined := false`: a joined act is refused (D-4); `displayConstants := true`
#guard err (decodeNormsEnvironment envA) == "UnsupportedProfile: Unsupported profile acts@0"
#guard err (decodeNormsEnvironment joinedE (acts := true)) == d4
#guard view (decodeNormsEnvironment envA (acts := true)) == view (acts envA)
def shown : Json := env ["norms@0", "relational-fol@0"] seek
  (consts := [("ann", Json.mkObj [("sort", .str "person"), ("description", .str "Ann"), ("verbalisation", .str "Ann")])])
#guard err (decodeNormsEnvironment shown) == "ok"
#guard err (decodeNormsEnvironmentWith ActsHook.acts shown (displayConstants := false)) != "ok"

/-! ### The route's decoders: `decodeFlagged` (plain) and `decodeFlaggedActs` (today's) -/

#guard err (decodeFlagged envA (Json.arr #[rule "heard"])) == actsHookRefusal
#guard err (decodeFlaggedActs envA (Json.arr #[rule "heard"])) == "ok"
#guard err (decodeFlagged plainEnv (Json.arr #[rule "p"])) == "ok"
#guard ((decodeFlagged plainEnv (Json.arr #[rule "p"])).toOption.map (·.ne.profiles)) ==
  ((decodeFlaggedActs plainEnv (Json.arr #[rule "p"])).toOption.map (·.ne.profiles))

/-! ### The norms mode's dispatch -/

-- which environments read `acts@0`, and which decide over one that does
#guard VE.Norms.Run.underActs joinedE && VE.Norms.Run.decidesActs joinedE
#guard !VE.Norms.Run.underActs plainEnv && !VE.Norms.Run.decidesActs plainEnv
#guard unsorted.all fun ps => !VE.Norms.Run.underActs (envA ps) && !VE.Norms.Run.decidesActs (envA ps)
-- a document layer the deciding view drops: the view still reads `acts@0`; a refused gate decides over nothing
#guard VE.Norms.Run.decidesActs (envA ["acts@0", "documents@1", "judgments@0", "norms@0", "relational-fol@0"])
#guard !VE.Norms.Run.decidesActs (envA ["acts@0", "judgments@0", "norms@0", "relational-fol@0"])
-- an environment that reads `acts@0` while the view it would decide over is refused: today's runner all the same
def judgedA : Json := envA ["acts@0", "judgments@0", "norms@0", "relational-fol@0"]
#guard VE.Norms.Run.underActs judgedA && !VE.Norms.Run.decidesActs judgedA
#guard err (VE.Norms.Run.runCaseRouted (caseOf "norms-conflict" judgedA)) ==
  err (VE.Norms.Run.runCaseActsRouted (caseOf "norms-conflict" judgedA))
#guard err (VE.Norms.Run.runCaseRouted (caseOf "norms-conflict" judgedA)) != actsHookRefusal
-- an `acts@0` case runs on today's runner (the elaborated document), a plain one on the plain runner
#guard (VE.Norms.Run.runCaseRouted (caseOf "norms-elaborate" joinedE)).toOption ==
  (VE.Norms.Run.runCaseActsRouted (caseOf "norms-elaborate" joinedE)).toOption
#guard (VE.Norms.Run.runCaseRouted (caseOf "norms-elaborate" joinedE)).toOption.isSome
#guard err (VE.Norms.Run.runCase (caseOf "norms-elaborate" joinedE)) == actsHookRefusal
def plainCase : Json := Json.mkObj [("id", .str "c"), ("kind", .str "norms-elaborate"), ("environment", plainEnv),
  ("norms", Json.arr #[rule "p"])]
#guard (VE.Norms.Run.runCaseRouted plainCase).toOption == (VE.Norms.Run.runCase plainCase).toOption
#guard (VE.Norms.Run.runCaseRouted plainCase).toOption == (VE.Norms.Run.runCaseActs plainCase).toOption
#guard (VE.Norms.Run.runCaseRouted plainCase).toOption.isSome
-- an unsorted `acts@0` list goes to the plain runner and is refused there as today
#guard err (VE.Norms.Run.runCaseRouted (caseOf "norms-conflict" (envA unsorted.head!))) == sortedRefusal
#guard err (VE.Norms.Run.runCaseRouted (caseOf "norms-conflict" (envA unsorted.head!))) ==
  err (VE.Acts.HookTwins.Today.runCaseRouted (caseOf "norms-conflict" (envA unsorted.head!)))
-- `acts-elaborate` on a plain environment: today's elaborate exit
#guard (VE.Norms.Run.runCaseRouted (elabCase plainEnv (Json.arr #[rule "p"]))).toOption ==
  (VE.Acts.Run.runElaborate VE.Acts.Run.normsSource (elabCase plainEnv (Json.arr #[rule "p"]))).toOption
#guard err (VE.Norms.Run.runCaseRouted (elabCase plainEnv (Json.arr #[rule "p"]))) ==
  "UnsupportedProfile: acts-elaborate requires acts@0"
-- admission refuses an `acts@0` environment at its envelope, before any decoder: the plain runner as today's
def doc0 : Json := Json.mkObj [("units", Json.arr #[]), ("graph", Json.mkObj [])]
#guard err (VE.Norms.Run.runAdmission "a" envA doc0) == "UnsupportedProfile: Unsupported profile acts@0"
#guard err (VE.Norms.Run.runAdmission "a" envA doc0) == err (VE.Acts.HookTwins.Today.runAdmission "a" envA doc0)

end VE.Acts.HookExamples
