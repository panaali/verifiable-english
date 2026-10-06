import ResponseShape

/-! The source of `ve/backends/lean_service_schema/readings.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Readings
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    n [
      obj,
      .required ["id", "status", "verdict"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("verdict", n [enumS ["ALL", "NONE", "SOME"], .equals "/verdict"])]]]

def file : File where
  name := "readings.json"
  comment := some "Reading-set verdict (Service.Readings.readingsCase): the submitted ALL, NONE or SOME verdict, confirmed only when Lean's rebuilt premises and the evidence check (readings_all_sound, readings_none_sound, readings_some_sound)."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.Readings
