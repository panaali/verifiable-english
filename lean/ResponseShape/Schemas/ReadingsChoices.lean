import ResponseShape

/-! Source of `readings-choices.json`; regenerate with tools/regen_generated.py. -/
namespace ResponseShape.Schemas.ReadingsChoices
open Lean ResponseShape

def verdict : Shape := n [
  obj, .required ["id", "status", "verdict"],
  closed [
    ("id", n [str, .equals "/id"]),
    ("status", constS "ok"),
    ("verdict", enumS ["ALL", "NONE", "SOME", "UNKNOWN"])]]

def enumerate : Shape := n [
  obj, .required ["id", "status", "route", "choices", "conditional_on"],
  closed [
    ("id", n [str, .equals "/id"]),
    ("status", constS "ok"),
    ("route", constS "enumerate"),
    ("choices", n [arr, .items (n [arr, .items (ref "common.json#/$defs/nat")])]),
    ("conditional_on", n [arr, .items str])],
  .readingPlan]

def unknown : Shape := n [
  obj, .required ["id", "status", "route", "budget", "choice_count", "units"],
  closed [
    ("id", n [str, .equals "/id"]),
    ("status", constS "ok"),
    ("route", constS "UNKNOWN"),
    ("budget", n [obj, .required ["max_choices"], closed [
      ("max_choices", ref "common.json#/$defs/nat")]]),
    ("choice_count", ref "common.json#/$defs/nat"),
    ("units", n [arr, .items str])],
  .readingPlan]

def plan : Shape := .anyOf [enumerate, unknown]

def «row» : Shape := .anyOf [
  ref "common.json#/$defs/case_error",
  ref "common.json#/$defs/error",
  plan,
  verdict]

def file : File where
  name := "readings-choices.json"
  comment := some "Lean checks every proposed choice and returns the verdict or compatible choice plan."
  top := [("row", «row»)]
  defs := [
    ("verdict", .schema verdict),
    ("plan", .schema plan)]

end ResponseShape.Schemas.ReadingsChoices
