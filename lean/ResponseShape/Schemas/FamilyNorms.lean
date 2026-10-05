import ResponseShape

/-! The source of `ve/backends/lean_service_schema/family-norms.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.FamilyNorms
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    .select [
      (ref "norms.json#/$defs/kind/norms-elaborate", ref "norms.json#/$defs/norms-elaborate"),
      (ref "norms.json#/$defs/kind/norms-certificate", ref "norms.json#/$defs/norms-certificate"),
      (.allOf [ref "norms.json#/$defs/kind/norms-conflict", .required ["witness"]], ref "norms.json#/$defs/norms-witness"),
      (ref "norms.json#/$defs/kind/norms-conflict", ref "norms.json#/$defs/norms-conflict"),
      ((.bool true), (.bool false))]]

def file : File where
  name := "family-norms.json"
  comment := some "Mode family-norms: Service.FamilyNorms.runCase, the norms route's regenerating cases on the closure, core and order families (regeneration over the FOL view, certificates checked by the family checker); the rows are the norms route's."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.FamilyNorms
