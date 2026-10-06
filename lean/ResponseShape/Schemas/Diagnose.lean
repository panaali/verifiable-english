import ResponseShape

/-! The source of `ve/backends/lean_service_schema/diagnose.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Diagnose
open Lean ResponseShape

def record : Shape :=
  c
    "WireContract.Engine.record of the first finding: the case's contract and revision, the failed check, its phase, code and class, the JSON pointer it names, the rendered text and the template's arguments (strings)."
    [
      obj,
      .required ["contract", "revision", "check", "phase", "code", "class", "path", "text", "args"],
      closed [
        ("contract", n [str, .equals "/unit"]),
        ("revision", ref "common.json#/$defs/nat"),
        ("check", ref "common.json#/$defs/text"),
        ("phase", ref "common.json#/$defs/text"),
        ("code", ref "common.json#/$defs/text"),
        ("class", ref "common.json#/$defs/code"),
        ("path", n [str, .pattern (Re.optional (Re.prefixes ["/"]))]),
        ("text", str),
        ("args", ref "common.json#/$defs/string_map")]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [
      obj,
      .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [
      obj,
      .required ["id", "status", "outcome"],
      closed [
        ("id", .echo "/id"),
        ("status", constS "ok"),
        ("outcome", enumS ["clean", "fault"]),
        ("diagnostic", ref "#/$defs/record")],
      .ite (props [("outcome", constS "fault")]) (.required ["diagnostic"]) (.not (.required ["diagnostic"]))]]

def file : File where
  name := "diagnose.json"
  comment := some "Mode diagnose: Service.Diagnose.diagnoseCase over a case with a member unit, the row ve_diagnose <unit> prints for the case (WireContract.Diagnose.diagnoseCase). Diagnostic only: it decides no verdict."
  top := [("row", «row»)]
  defs := [
    ("record", .schema record)]

end ResponseShape.Schemas.Diagnose
