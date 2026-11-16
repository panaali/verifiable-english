-- ve-layer: 4 (examples of the metered runner split, which they import)
import VE.Route.MeteredSplit
import VE.Route.MeteredProfileExamples

/-! Examples of the `metered` mode's three runners (kb-4b): which runner each environment's case goes to, and that the
mode's entry answers each as before (`runCaseReported_today` states it for every case; these pin a few by value). -/
namespace VE.Route.MeteredSplitExamples
open Lean
open VE.Route.MeteredProfileExamples (parsed environmentText modelText formula diagnostic)

def folList : String := VE.Route.MeteredProfileExamples.fol
def naryList : String := VE.Route.MeteredProfileExamples.nary

/-- A frozen `ve.core@0` envelope over the sort `point` and the predicate `upper`. -/
def legacyText : String :=
  r#"{"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20", "vocabulary": {"sorts": {"point": {"description": "point"}}, "predicates": {"upper": {"arguments": ["point"], "description": "upper"}}, "constants": {}}}"#

/-- The profile-examples environment (`norms@0` with a regulated pair) under other profile lists. -/
def withProfiles (profiles : String) : Json := parsed (environmentText profiles true)

def acts : Json := withProfiles r#"["acts@0", "norms@0", "relational-fol@0"]"#
def judgments : Json := withProfiles r#"["documents@1", "judgments@0", "norms@0", "relational-fol@0"]"#
def judgmentsReadings : Json := withProfiles r#"["documents@1", "judgments@0", "norms@0", "readings@1", "relational-fol@0"]"#

def caseOf (environment : Json) (required permitted : String) : Json :=
  Json.mkObj [("id", .str "e"), ("kind", .str "evaluate-budgeted"), ("environment", environment),
    ("model", parsed (modelText required permitted)), ("ast", .arr #[formula]),
    ("max_evaluations", toJson (1000 : Nat))]

/-- A case on the frozen envelope, whose model has `upper` only (of `a`). -/
def legacy : Json :=
  Json.mkObj [("id", .str "e"), ("kind", .str "evaluate-budgeted"), ("environment", parsed legacyText),
    ("model", parsed r#"{"complete": true, "domains": {"point": ["a", "b"]}, "constants": {}, "relations": {"upper": [["a"]]}}"#),
    ("ast", .arr #[formula]), ("max_evaluations", toJson (1000 : Nat))]

def cases : List Json :=
  [legacy, caseOf (withProfiles folList) "[[\"a\"]]" "[[\"a\"]]",
   caseOf (withProfiles folList) "[[\"a\"]]" "[]", caseOf (withProfiles naryList) "[]" "[]", caseOf acts "[]" "[]",
   caseOf judgments "[]" "[]", caseOf judgmentsReadings "[]" "[]",
   Json.mkObj [("id", .str "e"), ("kind", .str "evaluate-budgeted")]]

/-- The arm each case goes to: frozen envelope, acts, current. -/
def arm (j : Json) : String :=
  if VE.Route.MeteredRun.legacyCase j then "legacy" else if VE.Route.MeteredRun.actsCase j then "acts" else "current"

#guard cases.map arm == ["legacy", "current", "current", "current", "acts", "current", "current", "current"]

-- The frozen envelope is answered (its value is the formula's: `upper` holds of `a` only, so `∀ upper` fails).
#guard match VE.Route.MeteredRun.runCaseLegacy legacy with
  | .ok a => (a.getObjValD "evaluation").getObjValD "value" == .bool false
  | .error _ => false

-- The current runner checks the norms profile, with the `model` mode's diagnostic.
#guard match VE.Route.MeteredRun.runCaseCurrent (caseOf (withProfiles folList) "[[\"a\"]]" "[]") with
  | .error e => e == diagnostic
  | .ok _ => false

-- A `judgments@0` environment with a profile the route gate refuses is refused by the current runner.
#guard (VE.Route.MeteredRun.runCaseCurrent (caseOf judgmentsReadings "[]" "[]")).toOption.isNone

-- The entry answers every example as `reportedWith` of today's prepared environment does.
#guard cases.all fun j => (VE.Route.MeteredRun.runCaseReported j).compress ==
  (VE.Route.MeteredRun.reportedWith (VE.Route.MeteredRun.prepare <$> j.getObjVal? "environment") j).compress

/-- A layered core environment: `p` is defined over `base2` (`definitions@0` on the core family). -/
def layeredText : String :=
  r#"{"language": "ve.core@0.2", "profiles": ["closure@0", "data@0", "definitions@0", "nary@0", "relational-fol@0"], "spec_revision": "ve-v0.2-expand2-2026-09-25", "vocabulary": {"sorts": {"point": {"description": "point"}}, "constants": {}, "predicates": {"base2": {"arguments": ["point", "point"], "description": "base"}, "p": {"arguments": ["point", "point"], "description": "p", "defined": {"arguments": ["point", "point"], "body": ["binary", "base2", ["var", 1], ["var", 0]]}}}}}"#

/-- What a validation yields, as text: the refusal, or the envelope, the decodable JSON and the layers. -/
def shown : Except String VE.Service.Standalone.Validated → String
  | .error e => "error: " ++ e
  | .ok v => s!"{v.envelope.profiles} {repr v.envelope.family} {v.envelope.vocabulary.compress} " ++
      s!"{v.decodable.compress} {v.layers.map Json.compress}"

def environments : List Json :=
  [parsed legacyText, withProfiles folList, withProfiles naryList, acts, judgments, judgmentsReadings,
   parsed layeredText, parsed (environmentText folList false)]

-- `validated` (every mode's) reads each environment, with and without typing, as its body before kb-4b did.
#guard environments.all fun e => [true, false].all fun t =>
  shown (VE.Service.Standalone.validated e t) == shown (VE.Service.Standalone.Today.validated e t)

-- The current runner's validation is today's wherever it runs (no `acts@0`), and refuses an `acts@0` view.
#guard (environments.filter fun e => !VE.Service.Standalone.readsApart e && !VE.Service.Standalone.isLegacy e).all
  fun e => shown (VE.Service.Standalone.evaluableCurrent e) == shown (VE.Service.Standalone.evaluableActs e)
#guard shown (VE.Service.Standalone.evaluableCurrent acts) == "error: UnsupportedProfile: acts@0 needs the acts decoder"

-- A layered core environment keeps its layers apart without typing (the current runner) and not with it.
#guard (VE.Service.Standalone.evaluableCurrent (parsed layeredText)).toOption.map (·.layers.isSome) == some true
#guard (VE.Service.Standalone.validated (parsed layeredText) true).toOption.map (·.layers.isSome) == some false

-- The current runner's norms profile is the model mode's on the environments it reads.
#guard (environments.filter fun e => !VE.Service.Standalone.readsApart e && !VE.Service.Standalone.isLegacy e).all
  fun e => ((VE.Route.MeteredRun.prepareCurrent e).profile.get.toOption.map (·.isSome)) ==
    ((VE.Route.MeteredRun.prepare e).profile.get.toOption.map (·.isSome))

-- The model-view profiles are the four `modelEnvironment` reads apart before `typingReduced` (`risk@0`,
-- `alternatives@0`, `readings@1`, `norm-defaults@0`, lean/VE/Service/Standalone.lean `modelEnvironment`), each refused
-- by the route gate; `modelViewDropped` reads them on objects the proofs cannot see as well-formed (REPORT D1).
#guard VE.Service.Standalone.modelViewProfiles == ["risk@0", "alternatives@0", "readings@1", "norm-defaults@0"]
#guard VE.Service.Standalone.modelViewProfiles.all fun p => !VE.Route.Gate.known p

end VE.Route.MeteredSplitExamples
