import ResponseShape

/-! The checked projection of the W2 wrapper. Content admission is not a field
of this row; the wrapper carries source partition and coverage only. -/
namespace ResponseShape.Schemas.Document
open Lean ResponseShape

def unit : Shape :=
  n [obj, .required ["id", "span", "kind", "meaning", "support", "status"],
    closed [
      ("id", str), ("span", n [arr, .items (ref "common.json#/$defs/nat")]),
      ("kind", .bool true), ("meaning", .bool true), ("support", str),
      ("status", str), ("parent_id", str)]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    n [obj,
      .required ["id", "status", "document_id", "source_id", "source", "units", "coverage"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("document_id", ref "common.json#/$defs/hex64"),
        ("source_id", ref "common.json#/$defs/hex64"),
        ("source", str),
        ("units", n [arr, .items (ref "#/$defs/unit")]),
        ("coverage", n [obj,
          .required ["source_bytes", "accounted_bytes", "coverage_percent", "bytes_by_kind",
            "bytes_by_status", "unformalised_reasons", "residual", "residual_total"],
          closed [
            ("source_bytes", ref "common.json#/$defs/nat"),
            ("accounted_bytes", ref "common.json#/$defs/nat"),
            ("coverage_percent", .const (toJson (100 : Nat))),
            ("bytes_by_kind", obj), ("bytes_by_status", obj),
            ("unformalised_reasons", obj), ("residual", obj),
            ("residual_total", ref "common.json#/$defs/nat")]])]]]

def file : File where
  name := "document.json"
  comment := some "Mode document: W2 wrapper byte partition, inferred unit statuses and base coverage."
  top := [("row", «row»)]
  defs := [("unit", .schema unit)]

end ResponseShape.Schemas.Document
