import ResponseShape

/-! The source of `ve/backends/lean_service_schema/identity.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Identity
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    n [
      obj,
      .required ["id", "status", "kind", "identity_id"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("kind", n [enumS ["source", "meaning", "model", "claim", "edge"], .equals "/kind"]),
        ("identity_id", ref "common.json#/$defs/hex64")]]]

def file : File where
  name := "identity.json"
  comment := some "Standalone domain-separated identity recomputation."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.Identity
