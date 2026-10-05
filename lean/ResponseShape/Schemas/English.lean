import VE.Service.EnglishRun
import ResponseShape

/-! The source of `ve/backends/lean_service_schema/english.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.English
open Lean ResponseShape

def error : Shape :=
  n [
    obj,
    .required ["status", "error"],
    closed [("status", constS "error"), ("error", ref "common.json#/$defs/text")]]

def run : Shape :=
  n [
    obj,
    .required ["admissible", "covers", "results"],
    closed [
      ("admissible", .type ["boolean"]),
      ("covers", .type ["boolean"]),
      ("results", n [arr, .zip "/cases" (ref "#/$defs/item")])]]

def token : Shape :=
  decidedBy "English.ServiceRun.decodeTok" (fun j => match VE.English.ServiceRun.decodeTok j with
      | .ok tok => j == VE.English.ServiceRun.encodeTok tok
      | .error _ => false) <|
  c "EnglishRun.encodeTok: a word, or a label [letter, index]." [
    .anyOf [str, n [arr, .prefixItems [str, ref "common.json#/$defs/nat"], .minItems 2, .maxItems 2]]]

def item : Shape :=
  c
    "EnglishRun.runCase for the case at the same position. That a rendering comes exactly with a check, a roundtrip needs a checked rendering and only nonempty formulas are checked is the service's."
    [
      obj,
      .required ["parsed", "checked", "rendered", "roundtrip"],
      closed [
        ("parsed", .anyOf [.type ["null"], ref "common.json#/$defs/generated_formulas"]),
        ("checked", .type ["boolean"]),
        ("rendered", .anyOf [.type ["null"], n [arr, .items (ref "#/$defs/token")]]),
        ("roundtrip", .type ["boolean"])]]

def «row» : Shape :=
  .anyOf [ref "common.json#/$defs/case_error", ref "#/$defs/error", ref "#/$defs/run"]

def file : File where
  name := "english.json"
  comment := some "Mode english: Service.Protocol.englishReported (the generated copy of VE/English/Run.lean). One result per requested case."
  top := [("row", «row»)]
  defs := [
    ("error", .schema error),
    ("run", .schema run),
    ("token", .schema token),
    ("item", .schema item)]

end ResponseShape.Schemas.English
