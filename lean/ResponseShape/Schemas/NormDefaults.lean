import VE.Service.Protocol
import ResponseShape
import ResponseShape.CaseDeciders

/-! The source of `ve/backends/lean_service_schema/norm-defaults.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.NormDefaults
open Lean ResponseShape

def norm_defaults_path : Shape :=
  decidedCase .normDefaultsPath <|
  c
    "NormDefaults.Run.usesNormDefaultsPath: the norm-defaults@0 profile in a profile list of strings (Wire.hasProfile), a regulated predicate whose default is unspecified (Wire.unspecifiedNames), or a norm-defaults-* kind."
    [
      obj,
      .anyOf [
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["profiles"],
              props [("profiles", n [arr, .items str, .contains (constS "norm-defaults@0")])]])]],
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
                    ("predicates", n [
                      obj,
                      .not (.object [] (some (.not (n [
                                obj,
                                .required ["regulated"],
                                props [
                                  ("regulated", n [
                                    obj,
                                    .required ["default"],
                                    props [("default", constS "unspecified")]])]]))))])]])]])]],
        n [.required ["kind"], props [("kind", n [str, .pattern (Re.prefixes ["norm-defaults-"])])]]]]

def kind : Def :=
  .group none [
    ("admission", kindIs "admission"),
    ("norm-defaults-elaborate", kindIs "norm-defaults-elaborate"),
    ("norm-defaults-conflict", kindIs "norm-defaults-conflict"),
    ("norm-defaults-status", kindIs "norm-defaults-status"),
    ("norm-defaults-gaps", kindIs "norm-defaults-gaps"),
    ("norm-defaults-certificate", kindIs "norm-defaults-certificate")]

def elaborate : Shape :=
  c
    "NormDefaults.Wire.regeneratedU: Norms.Wire.regenerated of fill U, then Fill_T, the unspecified predicates, their unsaid predicates, the default-reached targets and the fragment flag of fill U."
    [
      obj,
      .required ["id", "status", "order", "background", "premises", "conflict_targets", "fragment", "fill", "unspecified", "unsaid", "reached", "fragment_fill"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("order", ref "common.json#/$defs/strings"),
        ("background", ref "common.json#/$defs/norms_background"),
        ("premises", ref "common.json#/$defs/layer_premises"),
        ("conflict_targets", ref "common.json#/$defs/conflict_targets"),
        ("fragment", .type ["boolean"]),
        ("fill", n [
          arr,
          .items (n [
              obj,
              .required ["generator", "ast"],
              closed [("generator", constS "fill"), ("ast", ref "common.json#/$defs/generated_formula")]])]),
        ("unspecified", ref "common.json#/$defs/strings"),
        ("unsaid", n [
          arr,
          .items (n [
              obj,
              .required ["name", "sorts"],
              closed [
                ("name", n [str, .pattern (Re.prefixes ["unsaid__"])]),
                ("sorts", ref "common.json#/$defs/strings")]])]),
        ("reached", n [
          arr,
          .items (n [
              obj,
              .required ["predicate", "sorts", "ast"],
              closed [
                ("predicate", str),
                ("sorts", ref "common.json#/$defs/strings"),
                ("ast", ref "common.json#/$defs/generated_formula")]])]),
        ("fragment_fill", .type ["boolean"])]]

def status : Shape :=
  c "NormDefaults.Run.runOtherCase norm-defaults-status: the requested predicate's point status." [
    obj,
    .required ["id", "status", "point_status", "predicate"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("point_status", enumS ["SETTLED yes", "SETTLED no", "UNDECIDED", "UNKNOWN"]),
      ("predicate", n [str, .equals "/predicate"])]]

def gaps_model : Shape :=
  c "norm-defaults-gaps with a model: whether the default is reached in it." [
    obj,
    .required ["id", "status", "gaps", "predicate"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("gaps", enumS ["reachable", "unknown"]),
      ("predicate", n [str, .equals "/predicate"])]]

def gaps : Shape :=
  c "norm-defaults-gaps without a model: whether a certificate shows no gap." [
    obj,
    .required ["id", "status", "gaps", "predicate"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("gaps", enumS ["none", "unknown"]),
      ("predicate", n [str, .equals "/predicate"])]]

def certificate : Shape :=
  c "norm-defaults-certificate: the replay's verdict and its premise count." [
    obj,
    .required ["id", "status", "valid", "premises"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("valid", .type ["boolean"]),
      ("premises", ref "common.json#/$defs/nat")]]

def «row» : Shape :=
  .select [
    (ref "#/$defs/norm_defaults_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      .select [
        (ref "#/$defs/kind/admission", ref "common.json#/$defs/admission"),
        (ref "#/$defs/kind/norm-defaults-elaborate", ref "#/$defs/elaborate"),
        (.allOf [ref "#/$defs/kind/norm-defaults-conflict", .required ["witness"]], ref "common.json#/$defs/witness_conflict"),
        (ref "#/$defs/kind/norm-defaults-conflict", ref "common.json#/$defs/packages_conflict"),
        (ref "#/$defs/kind/norm-defaults-status", ref "#/$defs/status"),
        (.allOf [ref "#/$defs/kind/norm-defaults-gaps", .required ["model"]], ref "#/$defs/gaps_model"),
        (ref "#/$defs/kind/norm-defaults-gaps", ref "#/$defs/gaps"),
        (ref "#/$defs/kind/norm-defaults-certificate", ref "#/$defs/certificate")]]),
    ((.bool true), ref "norms.json#/row")]

def file : File where
  name := "norm-defaults.json"
  comment := some "Mode norm-defaults: NormDefaults.Run.runCaseReported (formerly ve_norm_defaults_route). A case on the norm-defaults path (usesNormDefaultsPath) is answered by the norm-defaults runner; every other case is delegated unchanged to the norms mode's runner."
  top := [("row", «row»)]
  defs := [
    ("norm_defaults_path", .schema norm_defaults_path),
    ("kind", kind),
    ("elaborate", .schema elaborate),
    ("status", .schema status),
    ("gaps_model", .schema gaps_model),
    ("gaps", .schema gaps),
    ("certificate", .schema certificate)]

end ResponseShape.Schemas.NormDefaults
