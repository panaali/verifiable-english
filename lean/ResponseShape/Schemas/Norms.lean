import VE.Service.Protocol
import ResponseShape
import ResponseShape.CaseDeciders

/-! The source of `ve/backends/lean_service_schema/norms.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Norms
open Lean ResponseShape

def norms_path : Shape :=
  decidedCase .normsPath <|
  c
    "Norms.Run.usesNormsPath (a regulated predicate, a norms field, a norms-* kind or a unit with norm content) or Plain.layered (a profile of Plain.statementLayers: reports@0, soft-norms@0, rights@0 or speech-acts@0)."
    [
      obj,
      .anyOf [
        .required ["norms"],
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["profiles"],
              props [
                ("profiles", n [
                  arr,
                  .contains (enumS VE.Norms.Plain.statementLayers)])]])]],
        n [.required ["kind"], props [("kind", n [str, .pattern (Re.prefixes ["norms-"])])]],
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["vocabulary"],
              props [
                ("vocabulary", n [
                  obj,
                  .required ["predicates"],
                  props [
                    ("predicates", n [obj, .not (.object [] (some (.not (n [obj, .required ["regulated"]]))))])]])]])]],
        n [
          .required ["document"],
          props [
            ("document", n [
              obj,
              .required ["units"],
              props [
                ("units", n [
                  arr,
                  .contains (n [obj, .required ["content"], props [("content", n [obj, .required ["norm"]])]])])]])]]]]

def kind : Def :=
  .group none [
    ("admission", kindIs "admission"),
    ("background", kindIs "background"),
    ("norms-elaborate", kindIs "norms-elaborate"),
    ("norms-certificate", kindIs "norms-certificate"),
    ("norms-conflict", kindIs "norms-conflict"),
    ("acts-elaborate", kindIs "acts-elaborate")]

/-- The `norms-elaborate` row over `formula`, with the `extra` members one route adds (required). -/
def elaborateWith (formula : Shape) (extra : List (String × Shape) := []) : Shape :=
  c
    "Norms.Wire.regenerated: one layer (order entry, premise) per regulated predicate; Background in generator order; one conflict target per layer, then per profile pair. These lists are the service's (Lean invariants and Python parity in tests/test_lean_service_schema.py)."
    [
      obj,
      .required (["id", "status", "order", "background", "premises", "conflict_targets", "fragment"] ++
        extra.map (·.1)),
      closed ([
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("order", ref "common.json#/$defs/strings"),
        ("background", n [
          arr,
          .items (n [
              obj,
              .required ["generator", "ast"],
              closed [
                ("generator", enumS ["flags", "definitions", "literals", "profile"]),
                ("ast", formula)]])]),
        ("premises", n [
          arr,
          .items (n [
              obj,
              .required ["label", "ast"],
              closed [
                ("label", n [str, .pattern (Re.prefixes ["layer:norms:"])]),
                ("ast", formula)]])]),
        ("conflict_targets", n [
          arr,
          .items (n [
              obj,
              .required ["target", "sorts", "ast"],
              closed [
                ("target", str),
                ("sorts", ref "common.json#/$defs/strings"),
                ("ast", formula)]])]),
        ("fragment", .type ["boolean"])] ++ extra)]

/-- The norms route's row also gives the wording of each plain act by its predicate (`Norms.Wire.plainWordings`,
act-phrases 2.1), which Python binds to the request's plain acts and displays. -/
def «norms-elaborate» : Shape := elaborateWith (ref "common.json#/$defs/generated_formula")
  [("wordings", c "Norms.Wire.plainWordings: one wording per plain predicate with an act, by its name."
    [ref "common.json#/$defs/string_map"])]

def «norms-certificate» : Shape :=
  n [
    obj,
    .required ["id", "status", "valid", "background", "layers", "steps"],
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("valid", .type ["boolean"]),
      ("background", n [ref "common.json#/$defs/nat", .backgroundBound]),
      ("layers", ref "common.json#/$defs/nat"),
      ("steps", n [ref "common.json#/$defs/nat", .maxSteps])]]

def «norms-witness» : Shape :=
  c "Norms.Flagged.witnessFrom (norms_flagged_witness_sound): the requested target; the regenerated targets are the service's." [
    obj,
    .required ["id", "status", "verdict", "target", "targets"],
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("verdict", enumS ["CONFLICT", "UNKNOWN"]),
      ("target", n [str, .equals "/witness/target"]),
      ("targets", ref "common.json#/$defs/strings")]]

def «norms-conflict» : Shape :=
  c "Norms.Flagged.replayConflict (norms_flagged_conflict_free; the verdict, its detail and the targets are the service's)." [
    obj,
    .required ["id", "status", "verdict", "targets"],
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("verdict", enumS ["CONFLICT-FREE", "UNKNOWN"]),
      ("targets", ref "common.json#/$defs/strings"),
      ("detail", str)]]

/-- The `acts-elaborate` row (act-phrases 6.7), shared with the norm-defaults mode. -/
def «acts-elaborate» : Shape :=
  c "Acts.Run.runElaborate (runElaborate_fits): the elaborated document's parts, part rules, joined acts kept whole and, per split source, its parts with D-28's text; or REFUSED with the elaboration's diagnostic and every list empty. Python binds each source, index and copied field to the request (ve/norms.py bound_elaboration)." [
    obj,
    .required ["id", "status", "environment_id", "verdict", "predicates", "rules", "kept", "split"],
    .ite (props [("verdict", constS "REFUSED")]) (.required ["diagnostic"]) (.not (.required ["diagnostic"])),
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("environment_id", ref "common.json#/$defs/hex64"),
      ("verdict", enumS ["ELABORATED", "REFUSED"]),
      ("diagnostic", str),
      ("predicates", n [arr, .items (n [obj,
        .required ["name", "source", "index", "sorts", "role", "default", "act", "permission"],
        closed [
          ("name", str), ("source", str), ("index", ref "common.json#/$defs/nat"),
          ("sorts", ref "common.json#/$defs/strings"),
          ("role", enumS ["permission", "obligation", "plain"]),
          ("default", enumS ["allow", "deny", "unspecified"]),
          ("act", .anyOf [str, .type ["null"]]), ("permission", .anyOf [str, .type ["null"]])]])]),
      ("rules", n [arr, .items (n [obj,
        .required ["name", "source", "index", "pred", "sign", "guard", "unless", "over"],
        closed [
          ("name", str), ("source", str), ("index", ref "common.json#/$defs/nat"), ("pred", str),
          ("sign", .type ["boolean"]), ("guard", ref "common.json#/$defs/generated_formula"),
          ("unless", ref "common.json#/$defs/generated_formulas"),
          ("over", ref "common.json#/$defs/strings")]])]),
      ("kept", ref "common.json#/$defs/strings"),
      ("split", n [arr, .items (n [obj, .required ["source", "parts", "text"],
        closed [("source", str), ("parts", ref "common.json#/$defs/strings"), ("text", str)]])])]]

def «row» : Shape :=
  .select [
    (ref "#/$defs/norms_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/error",
      .select [
        (ref "common.json#/$defs/no_kind", ref "route.json#/$defs/evaluate"),
        (ref "#/$defs/kind/admission", ref "common.json#/$defs/admission"),
        (ref "#/$defs/kind/background", ref "route.json#/$defs/background"),
        (ref "route.json#/$defs/kind/evaluate", ref "route.json#/$defs/evaluate"),
        (ref "route.json#/$defs/kind/countermodel", ref "route.json#/$defs/countermodel"),
        (ref "route.json#/$defs/kind/certificate", ref "route.json#/$defs/certificate"),
        (ref "#/$defs/kind/norms-elaborate", ref "#/$defs/norms-elaborate"),
        (ref "#/$defs/kind/norms-certificate", ref "#/$defs/norms-certificate"),
        (.allOf [ref "#/$defs/kind/norms-conflict", .required ["witness"]], ref "#/$defs/norms-witness"),
        (ref "#/$defs/kind/norms-conflict", ref "#/$defs/norms-conflict"),
        (ref "#/$defs/kind/acts-elaborate", ref "#/$defs/acts-elaborate")]]),
    ((.bool true), ref "route.json#/row")]

def file : File where
  name := "norms.json"
  comment := some "Mode norms: Norms.Run.runCaseReported. A case on the norms path (Norms.Run.usesNormsPath) is answered by the norms runner (a case without a kind is an evaluation, Route.Run.caseKind's default, answered through Norms.Plain.run); every other case is delegated unchanged to route."
  top := [("row", «row»)]
  defs := [
    ("norms_path", .schema norms_path),
    ("kind", kind),
    ("norms-elaborate", .schema «norms-elaborate»),
    ("norms-certificate", .schema «norms-certificate»),
    ("norms-witness", .schema «norms-witness»),
    ("norms-conflict", .schema «norms-conflict»),
    ("acts-elaborate", .schema «acts-elaborate»)]

/- The `norms-elaborate` row as `tools/response_schemas.py` renders it, pinned (ap-1bb): every member required and
closed, `wordings` a `string_map` beside the regenerated lists the encoder theorem reads. -/
#guard (ResponseShape.render "norms.json" 64 «norms-elaborate»).toOption.map (·.compress) == some
  "{\"$comment\":\"Norms.Wire.regenerated: one layer (order entry, premise) per regulated predicate; Background in generator order; one conflict target per layer, then per profile pair. These lists are the service's (Lean invariants and Python parity in tests/test_lean_service_schema.py).\",\"additionalProperties\":false,\"properties\":{\"background\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"ast\":{\"$ref\":\"common.json#/$defs/generated_formula\"},\"generator\":{\"enum\":[\"flags\",\"definitions\",\"literals\",\"profile\"]}},\"required\":[\"generator\",\"ast\"],\"type\":\"object\"},\"type\":\"array\"},\"conflict_targets\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"ast\":{\"$ref\":\"common.json#/$defs/generated_formula\"},\"sorts\":{\"$ref\":\"common.json#/$defs/strings\"},\"target\":{\"type\":\"string\"}},\"required\":[\"target\",\"sorts\",\"ast\"],\"type\":\"object\"},\"type\":\"array\"},\"fragment\":{\"type\":\"boolean\"},\"id\":{\"type\":\"string\",\"x-equals\":\"/id\"},\"order\":{\"$ref\":\"common.json#/$defs/strings\"},\"premises\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"ast\":{\"$ref\":\"common.json#/$defs/generated_formula\"},\"label\":{\"pattern\":\"layer:norms:.*\",\"type\":\"string\"}},\"required\":[\"label\",\"ast\"],\"type\":\"object\"},\"type\":\"array\"},\"status\":{\"const\":\"ok\"},\"wordings\":{\"$comment\":\"Norms.Wire.plainWordings: one wording per plain predicate with an act, by its name.\",\"$ref\":\"common.json#/$defs/string_map\"}},\"required\":[\"id\",\"status\",\"order\",\"background\",\"premises\",\"conflict_targets\",\"fragment\",\"wordings\"],\"type\":\"object\"}"

/- ap-3dc: the `acts-elaborate` row, the mode's row selection, its kinds and its definitions, as rendered, pinned. -/
#guard (ResponseShape.render "norms.json" 64 «acts-elaborate»).toOption.map (·.compress) == some
  "{\"$comment\":\"Acts.Run.runElaborate (runElaborate_fits): the elaborated document's parts, part rules, joined acts kept whole and, per split source, its parts with D-28's text; or REFUSED with the elaboration's diagnostic and every list empty. Python binds each source, index and copied field to the request (ve/norms.py bound_elaboration).\",\"additionalProperties\":false,\"else\":{\"not\":{\"required\":[\"diagnostic\"]}},\"if\":{\"properties\":{\"verdict\":{\"const\":\"REFUSED\"}}},\"properties\":{\"diagnostic\":{\"type\":\"string\"},\"environment_id\":{\"$ref\":\"common.json#/$defs/hex64\"},\"id\":{\"type\":\"string\",\"x-equals\":\"/id\"},\"kept\":{\"$ref\":\"common.json#/$defs/strings\"},\"predicates\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"act\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"null\"}]},\"default\":{\"enum\":[\"allow\",\"deny\",\"unspecified\"]},\"index\":{\"$ref\":\"common.json#/$defs/nat\"},\"name\":{\"type\":\"string\"},\"permission\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"null\"}]},\"role\":{\"enum\":[\"permission\",\"obligation\",\"plain\"]},\"sorts\":{\"$ref\":\"common.json#/$defs/strings\"},\"source\":{\"type\":\"string\"}},\"required\":[\"name\",\"source\",\"index\",\"sorts\",\"role\",\"default\",\"act\",\"permission\"],\"type\":\"object\"},\"type\":\"array\"},\"rules\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"guard\":{\"$ref\":\"common.json#/$defs/generated_formula\"},\"index\":{\"$ref\":\"common.json#/$defs/nat\"},\"name\":{\"type\":\"string\"},\"over\":{\"$ref\":\"common.json#/$defs/strings\"},\"pred\":{\"type\":\"string\"},\"sign\":{\"type\":\"boolean\"},\"source\":{\"type\":\"string\"},\"unless\":{\"$ref\":\"common.json#/$defs/generated_formulas\"}},\"required\":[\"name\",\"source\",\"index\",\"pred\",\"sign\",\"guard\",\"unless\",\"over\"],\"type\":\"object\"},\"type\":\"array\"},\"split\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"parts\":{\"$ref\":\"common.json#/$defs/strings\"},\"source\":{\"type\":\"string\"},\"text\":{\"type\":\"string\"}},\"required\":[\"source\",\"parts\",\"text\"],\"type\":\"object\"},\"type\":\"array\"},\"status\":{\"const\":\"ok\"},\"verdict\":{\"enum\":[\"ELABORATED\",\"REFUSED\"]}},\"required\":[\"id\",\"status\",\"environment_id\",\"verdict\",\"predicates\",\"rules\",\"kept\",\"split\"],\"then\":{\"required\":[\"diagnostic\"]},\"type\":\"object\"}"
#guard (ResponseShape.render "norms.json" 64 «row»).toOption.map (·.compress) == some
  "{\"x-select\":[{\"then\":{\"anyOf\":[{\"$ref\":\"common.json#/$defs/case_error\"},{\"$ref\":\"common.json#/$defs/error\"},{\"x-select\":[{\"then\":{\"$ref\":\"route.json#/$defs/evaluate\"},\"when\":{\"$ref\":\"common.json#/$defs/no_kind\"}},{\"then\":{\"$ref\":\"common.json#/$defs/admission\"},\"when\":{\"$ref\":\"#/$defs/kind/admission\"}},{\"then\":{\"$ref\":\"route.json#/$defs/background\"},\"when\":{\"$ref\":\"#/$defs/kind/background\"}},{\"then\":{\"$ref\":\"route.json#/$defs/evaluate\"},\"when\":{\"$ref\":\"route.json#/$defs/kind/evaluate\"}},{\"then\":{\"$ref\":\"route.json#/$defs/countermodel\"},\"when\":{\"$ref\":\"route.json#/$defs/kind/countermodel\"}},{\"then\":{\"$ref\":\"route.json#/$defs/certificate\"},\"when\":{\"$ref\":\"route.json#/$defs/kind/certificate\"}},{\"then\":{\"$ref\":\"#/$defs/norms-elaborate\"},\"when\":{\"$ref\":\"#/$defs/kind/norms-elaborate\"}},{\"then\":{\"$ref\":\"#/$defs/norms-certificate\"},\"when\":{\"$ref\":\"#/$defs/kind/norms-certificate\"}},{\"then\":{\"$ref\":\"#/$defs/norms-witness\"},\"when\":{\"allOf\":[{\"$ref\":\"#/$defs/kind/norms-conflict\"},{\"required\":[\"witness\"]}]}},{\"then\":{\"$ref\":\"#/$defs/norms-conflict\"},\"when\":{\"$ref\":\"#/$defs/kind/norms-conflict\"}},{\"then\":{\"$ref\":\"#/$defs/acts-elaborate\"},\"when\":{\"$ref\":\"#/$defs/kind/acts-elaborate\"}}]}]},\"when\":{\"$ref\":\"#/$defs/norms_path\"}},{\"then\":{\"$ref\":\"route.json#/row\"},\"when\":true}]}"
#guard (match kind with | .group _ es => es.map (·.1) | _ => []) ==
  ["admission", "background", "norms-elaborate", "norms-certificate", "norms-conflict", "acts-elaborate"]
#guard file.defs.map (·.1) ==
  ["norms_path", "kind", "norms-elaborate", "norms-certificate", "norms-witness", "norms-conflict", "acts-elaborate"]

end ResponseShape.Schemas.Norms
