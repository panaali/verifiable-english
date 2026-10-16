import ResponseShape.Schemas.Common

/-! The source of `ve/backends/lean_service_schema/graph.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Graph
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    n [
      obj,
      .required ["id", "status", "report", "assumptions", "supporting_edges", "background"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("report", n [
          obj,
          .required ["root", "assumptions"],
          closed [("root", str), ("assumptions", ref "common.json#/$defs/strings")]]),
        ("assumptions", ref "common.json#/$defs/strings"),
        ("supporting_edges", ref "common.json#/$defs/strings"),
        ("background", n [
          arr,
          .items (n [obj, .required ["label", "ast"], closed [("label", n [str, .pattern (.seq (.lit "background:") (Re.oneOf VE.Route.Background.generators))]), ("ast", ref "common.json#/$defs/generated_formula")]])])]]]

def file : File where
  name := "graph.json"
  comment := some "Graph composition (Service.Graph.graphCase): the checked report of the root's dependency cone by claim name, the compatibility projection (named leaves and supporting deductions in declaration order) and the regenerated Background leaves."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.Graph
