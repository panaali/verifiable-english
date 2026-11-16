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

end VE.Route.MeteredSplitExamples
