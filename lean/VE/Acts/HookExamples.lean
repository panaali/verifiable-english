import VE.Service.ActsExamples
import VE.Acts.HookTwins

/-! The acts hook (kb-4a), computed: what each instance of `Norms.Wire.ActsHook` answers and where the norms mode's
dispatch sends a case. The equality theorems are `VE.Acts.HookToday` and `VE.Acts.HookTwins`; these checks pin the
behaviours they relate on fixtures of `VE.Service.ActsExamples` and `VE.Acts.DecodeExamples`. -/

namespace VE.Acts.HookExamples
open Lean VE.Norms.Wire VE.Service.ActsExamples
open VE.Acts.DecodeExamples (norms27 manyEnv manyRules)

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
