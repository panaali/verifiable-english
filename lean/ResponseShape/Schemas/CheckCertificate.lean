import ResponseShape

/-! The source of `ve/backends/lean_service_schema/check-certificate.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.CheckCertificate
open Lean ResponseShape

def certificate : Shape :=
  n [
    obj,
    .required ["id", "status", "valid"],
    closed [("id", n [str, .equals "/id"]), ("status", constS "ok"), ("valid", .type ["boolean"])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error_valid",
    ref "common.json#/$defs/error_valid",
    ref "#/$defs/certificate"]

def file : File where
  name := "check-certificate.json"
  comment := some "Mode check-certificate: CertificateWire.runCaseReported."
  top := [("row", «row»)]
  defs := [
    ("certificate", .schema certificate)]

end ResponseShape.Schemas.CheckCertificate
