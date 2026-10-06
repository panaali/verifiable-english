import ResponseShape

/-! The source of `ve/backends/lean_service_schema/check.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Check
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    n [
      obj,
      .required ["id", "status", "well_typed", "meaning_id", "Q", "core", "environment_id", "target_environment_id"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("well_typed", .const (.bool true)),
        ("meaning_id", ref "common.json#/$defs/hex64"),
        ("Q", ref "quantity.json#/$defs/q_formula"),
        ("core", arr),
        ("environment_id", ref "common.json#/$defs/hex64"),
        ("target_environment_id", ref "common.json#/$defs/hex64")]],
    n [
      obj,
      .required ["id", "status", "well_typed", "meaning_id"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("well_typed", .const (.bool true)),
        ("meaning_id", ref "common.json#/$defs/hex64")]]]

def file : File where
  name := "check.json"
  comment := some "Standalone checked formula or document with recomputed meaning identity."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.Check
