import ResponseShape

/-! The source of `ve/backends/lean_service_schema/environment.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Environment
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    n [
      obj,
      .required ["id", "status", "environment_id", "profiles", "family", "acts"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("environment_id", ref "common.json#/$defs/hex64"),
        ("profiles", n [ref "common.json#/$defs/strings", .equals "/environment/profiles"]),
        ("family", enumS ["fol", "closure", "closure+n-ary", "order"]),
        ("acts", c "Norms.Wire.canonicalActs: the canonical act of each regulated predicate with an act, by its name, as the identity hashes it; Python stores it and binds the names to the request." [ref "common.json#/$defs/string_map"])]],
    c "The frozen v0 envelope (ve.core@0) names its one profile in `profile`." [
      obj,
      .required ["id", "status", "environment_id", "profile", "family"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("environment_id", ref "common.json#/$defs/hex64"),
        ("profile", n [str, .equals "/environment/profile"]),
        ("family", constS "fol")]]]

def file : File where
  name := "environment.json"
  comment := some "Standalone Route.Gate and vocabulary validation, or a frozen pre-route envelope's decoder (Standalone.decodeLegacy)."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.Environment
