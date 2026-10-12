import ResponseShape

/-! The source of `ve/backends/lean_service_schema/order.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Order
open Lean ResponseShape

def kind : Def :=
  .group none [
    ("surface", kindIs "surface"),
    ("evaluate", kindIs "evaluate"),
    ("countermodel", kindIs "countermodel"),
    ("certificate", kindIs "certificate")]

def surface : Shape :=
  c
    "runCase re-decodes each parsed formula with Wire.decodeFormula 64, so the generated formulas are within order_formula. That Order.Surface.parse accepts only a nonempty document is the service's."
    [
      obj,
      .required ["id", "status", "ast"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("ast", n [arr, .items (ref "common.json#/$defs/order_formula")])]]

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
  n [
    obj,
    .required ["id", "status", "valid", "steps"],
    closed [("id", n [str, .equals "/id"]), ("status", constS "ok"),
      ("valid", .type ["boolean"]), ("steps", n [ref "common.json#/$defs/nat", .maxSteps])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error_valid",
    ref "common.json#/$defs/error_valid",
    .select [
      (ref "#/$defs/kind/surface", ref "#/$defs/surface"),
      (ref "#/$defs/kind/evaluate", ref "#/$defs/evaluate"),
      (ref "#/$defs/kind/countermodel", ref "#/$defs/countermodel"),
      (ref "#/$defs/kind/certificate", ref "#/$defs/certificate")]]

def file : File where
  name := "order.json"
  comment := some "Mode order: Order.Surface.runCaseReported (Order.Wire.runCase). The kind field is required."
  top := [("row", «row»)]
  defs := [
    ("kind", kind),
    ("surface", .schema surface),
    ("evaluate", .schema evaluate),
    ("countermodel", .schema countermodel),
    ("certificate", .schema certificate)]

end ResponseShape.Schemas.Order
