import ResponseShape

/-! The source of `ve/backends/lean_service_schema/bundle.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Bundle
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    n [
      obj,
      .required ["id", "status", "checked", "lemmas"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("checked", n [ref "common.json#/$defs/nat", .count "/lemmas"]),
        ("lemmas", n [arr, .items (ref "common.json#/$defs/hex64"), .equals "/lemmas/*/meaning_id"])]]]

def file : File where
  name := "bundle.json"
  comment := some "Lemma bundle over any family (Service.FamilyBundle.bundleCase): every requested lemma is checked, in order, under its meaning id (binding to the request's lemmas); citation soundness is FamilyBundle.bundle_sound."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.Bundle
