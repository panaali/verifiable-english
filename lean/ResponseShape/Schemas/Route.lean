import ResponseShape

/-! The source of `ve/backends/lean_service_schema/route.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Route
open Lean ResponseShape

def kind : Def :=
  .group none [
    ("evaluate", kindIs "evaluate"),
    ("countermodel", kindIs "countermodel"),
    ("certificate", kindIs "certificate"),
    ("dependency-order", kindIs "dependency-order"),
    ("bundle", kindIs "bundle"),
    ("background", kindIs "background"),
    ("label", kindIs "label"),
    ("admission", kindIs "admission")]

def error : Shape :=
  c
    "Route.Run.runCaseReported: the generator of an InvalidModel message (generatorOf, the service's); valid: false iff the request kind is certificate."
    [
      obj,
      .required ["id", "status", "error"],
      closed [
        ("id", .echo "/id"),
        ("status", constS "error"),
        ("error", ref "common.json#/$defs/text"),
        ("generator", str),
        ("valid", .const (.bool false))],
      .ite (.onCase (ref "#/$defs/kind/certificate")) (.required ["valid"]) (.not (.required ["valid"]))]

def evaluate : Shape :=
  n [
    obj,
    .required ["id", "status", "values"],
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("values", ref "common.json#/$defs/values")]]

def countermodel : Shape :=
  n [
    obj,
    .required ["id", "status", "refutes"],
    closed [("id", n [str, .equals "/id"]), ("status", constS "ok"), ("refutes", .type ["boolean"])]]

def certificate : Shape :=
  c "background: the number of regenerated Background premises (fullBackground); its value is the service's." [
    obj,
    .required ["id", "status", "valid", "background", "steps"],
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("valid", .type ["boolean"]),
      ("background", n [ref "common.json#/$defs/nat", .backgroundBound]),
      ("steps", n [ref "common.json#/$defs/nat", .maxSteps])]]

def «dependency-order» : Shape :=
  c
    "Route.dependencyOrder: that the order passes verifyOrder for the request's nodes (dag_acyclic) is the service's."
    [
      obj,
      .required ["id", "status", "order"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("order", ref "common.json#/$defs/strings")]]

def bundle : Shape :=
  c
    "Definitions.Bundle.runBundle: every requested lemma is checked, in order, under its meaning id (binding to the request's lemmas)."
    [
      obj,
      .required ["id", "status", "checked", "lemmas"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("checked", n [ref "common.json#/$defs/nat", .count "/lemmas"]),
        ("lemmas", n [arr, .items (ref "common.json#/$defs/hex64"), .equals "/lemmas/*/meaning_id"])]]

def background : Shape :=
  c
    "Route.Wire.runBackground: the regenerated Background twice, with one generator per premise; its contents are the service's."
    [
      obj,
      .required ["id", "status", "background", "premises", "generators"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("background", ref "common.json#/$defs/generated_formulas"),
        ("premises", ref "common.json#/$defs/generated_formulas"),
        ("generators", n [arr, .items (ref "common.json#/$defs/generator")])]]

def label : Shape :=
  c "The canonical label is the requested one (parseLabel_render)." [
    obj,
    .required ["id", "status", "label"],
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("label", n [ref "common.json#/$defs/label", .equals "/label"])]]

def ok : Shape :=
  c "The answer the case kind selects (Route.Run.dispatch)." [
    .select [
      (ref "common.json#/$defs/no_kind", ref "#/$defs/evaluate"),
      (ref "#/$defs/kind/evaluate", ref "#/$defs/evaluate"),
      (ref "#/$defs/kind/countermodel", ref "#/$defs/countermodel"),
      (ref "#/$defs/kind/certificate", ref "#/$defs/certificate"),
      (ref "#/$defs/kind/dependency-order", ref "#/$defs/dependency-order"),
      (ref "#/$defs/kind/bundle", ref "#/$defs/bundle"),
      (ref "#/$defs/kind/background", ref "#/$defs/background"),
      (ref "#/$defs/kind/label", ref "#/$defs/label"),
      (ref "#/$defs/kind/admission", ref "common.json#/$defs/admission")]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "#/$defs/error",
    ref "#/$defs/ok"]

def file : File where
  name := "route.json"
  comment := some "Mode route: Route.Run.runCaseReported. The case kind (default evaluate) selects the result shape."
  top := [("row", «row»)]
  defs := [
    ("kind", kind),
    ("error", .schema error),
    ("evaluate", .schema evaluate),
    ("countermodel", .schema countermodel),
    ("certificate", .schema certificate),
    ("dependency-order", .schema «dependency-order»),
    ("bundle", .schema bundle),
    ("background", .schema background),
    ("label", .schema label),
    ("ok", .schema ok)]

end ResponseShape.Schemas.Route
