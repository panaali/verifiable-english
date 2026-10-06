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
    ("norms-conflict", kindIs "norms-conflict")]

def «norms-elaborate» : Shape :=
  c
    "Norms.Wire.regenerated: one layer (order entry, premise) per regulated predicate; Background in generator order; one conflict target per layer, then per profile pair. These lists are the service's (Lean invariants and Python parity in tests/test_lean_service_schema.py)."
    [
      obj,
      .required ["id", "status", "order", "background", "premises", "conflict_targets", "fragment"],
      closed [
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
                ("ast", ref "common.json#/$defs/generated_formula")]])]),
        ("premises", n [
          arr,
          .items (n [
              obj,
              .required ["label", "ast"],
              closed [
                ("label", n [str, .pattern (Re.prefixes ["layer:norms:"])]),
                ("ast", ref "common.json#/$defs/generated_formula")]])]),
        ("conflict_targets", n [
          arr,
          .items (n [
              obj,
              .required ["target", "sorts", "ast"],
              closed [
                ("target", str),
                ("sorts", ref "common.json#/$defs/strings"),
                ("ast", ref "common.json#/$defs/generated_formula")]])]),
        ("fragment", .type ["boolean"])]]

def «norms-certificate» : Shape :=
  n [
    obj,
    .required ["id", "status", "valid", "background", "layers"],
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("valid", .type ["boolean"]),
      ("background", ref "common.json#/$defs/nat"),
      ("layers", ref "common.json#/$defs/nat")]]

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
        (ref "#/$defs/kind/norms-conflict", ref "#/$defs/norms-conflict")]]),
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
    ("norms-conflict", .schema «norms-conflict»)]

end ResponseShape.Schemas.Norms
