import ResponseShape

/-! The source of `ve/backends/lean_service_schema/model.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Model
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    n [
      obj,
      .required ["id", "status", "valid", "model_id"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("valid", .const (.bool true)),
        ("model_id", ref "common.json#/$defs/hex64")]]]

def file : File where
  name := "model.json"
  comment := some "Standalone checked finite model and recomputed identity."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.Model
