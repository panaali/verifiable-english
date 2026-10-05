import ResponseShape

/-! The source of `ve/backends/lean_service_schema/readings-route.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.ReadingsRoute
open Lean ResponseShape

def kind : Def :=
  .group none [
    ("readings-validate", kindIs "readings-validate"),
    ("readings-separate", kindIs "readings-separate")]

def pair : Shape :=
  c
    "Readings.Run.pairJson: a separating situation's facts; other_value exactly when the other reading owns no generated key."
    [
      obj,
      .required ["situation", "witness", "separated", "witness_admissible", "witness_value", "other_admissible"],
      closed [
        ("situation", str),
        ("witness", str),
        ("separated", .type ["boolean"]),
        ("witness_admissible", .type ["boolean"]),
        ("witness_value", .type ["boolean", "null"]),
        ("other_admissible", .type ["boolean"]),
        ("other_value", .type ["boolean", "null"])]]

def key : Shape :=
  c "Readings.Wire key JSON: one generated key." [
    .anyOf [
      n [obj, .required ["excepted"], closed [("excepted", str), ("bearer", str)]],
      n [obj, .required ["off", "party"], closed [("off", str), ("party", str), ("bearer", str)]],
      n [
        obj,
        .required ["outweighs", "lower", "higher"],
        closed [("outweighs", str), ("lower", str), ("higher", str)]],
      n [obj, .required ["lim", "act"], closed [("lim", str), ("act", str)]],
      n [obj, .required ["cond", "act", "condition"], closed [("cond", str), ("act", str), ("condition", str)]],
      n [obj, .required ["aimed"], closed [("aimed", str)]]]]

def keys : Shape :=
  n [arr, .items (n [obj, .required ["key", "name"], closed [("key", ref "#/$defs/key"), ("name", str)]])]

def candidate : Shape :=
  c
    "Readings.Run.candidateJson: a pending candidate, or its document hash, owned and shared keys and findings."
    [
      .anyOf [
        n [
          obj,
          .required ["id", "index", "pending"],
          closed [("id", str), ("index", ref "common.json#/$defs/nat"), ("pending", .const (.bool true))]],
        n [
          obj,
          .required ["id", "index", "pending", "document_hash", "owned", "shared", "findings"],
          closed [
            ("id", str),
            ("index", ref "common.json#/$defs/nat"),
            ("pending", .const (.bool false)),
            ("document_hash", ref "common.json#/$defs/hex64"),
            ("owned", ref "#/$defs/keys"),
            ("shared", ref "#/$defs/keys"),
            ("findings", ref "common.json#/$defs/nonempty_strings")]]]]

def validate : Shape :=
  c "Readings.Run.validateResult: no content-bearing set, or one entry per content-bearing open set." [
    .anyOf [
      n [
        obj,
        .required ["id", "status", "content_bearing"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("content_bearing", .const (.bool false))]],
      n [
        obj,
        .required ["id", "status", "content_bearing", "sets"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("content_bearing", .const (.bool true)),
          ("sets", n [
            arr,
            .items (n [
                obj,
                .required ["set", "version", "candidates", "pairs", "findings"],
                closed [
                  ("set", str),
                  ("version", ref "common.json#/$defs/nat"),
                  ("candidates", n [arr, .items (ref "#/$defs/candidate")]),
                  ("pairs", n [
                    arr,
                    .items (n [
                        obj,
                        .required ["reading", "other", "pair"],
                        closed [("reading", str), ("other", str), ("pair", ref "#/$defs/pair")]])]),
                  ("findings", n [
                    arr,
                    .items (n [
                        str,
                        .pattern (Re.prefixes ["SeparatedByDecisionOnly: ", "SeparatedByActOnly: "])])])]])])]]]]

def separate : Shape :=
  c "Readings.Run.runCase readings-separate: the requested set and situation's pair facts." [
    obj,
    .required ["id", "status", "set", "pair"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("set", n [str, .equals "/set"]),
      ("pair", n [ref "#/$defs/pair", props [("situation", .equals "/situation")]])]]

def «row» : Shape :=
  .select [
    (ref "#/$defs/kind/readings-validate", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/validate"]),
    (ref "#/$defs/kind/readings-separate", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/separate"]),
    ((.bool true), .anyOf [
      ref "rights.json#/row",
      ref "soft-norms.json#/row",
      ref "norm-defaults.json#/row",
      ref "norms.json#/row"])]

def file : File where
  name := "readings-route.json"
  comment := some "Mode readings-route: Readings.Run.runCaseReported (formerly ve_readings_route). readings-validate and readings-separate are the readings runner's; every other case goes, with readings@1 stripped from its profiles, to the runner Compose.dispatch names (rights, soft-norms or norm-defaults, else norms; Readings.Run.runLower). The client does not evaluate Compose.dispatch, so such a row is any of those four modes' rows for the case."
  top := [("row", «row»)]
  defs := [
    ("kind", kind),
    ("pair", .schema pair),
    ("key", .schema key),
    ("keys", .schema keys),
    ("candidate", .schema candidate),
    ("validate", .schema validate),
    ("separate", .schema separate)]

end ResponseShape.Schemas.ReadingsRoute
