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
    ("norm-defaults-certificate", kindIs "norm-defaults-certificate"),
    ("norm-defaults-report", kindIs "norm-defaults-report")]

/-- The fields of `elaborate`, shared with `layered_elaborate`. -/
def elaborateFields : List (String × Shape) := [
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
        .required ["name", "sorts", "description"],
        closed [
          ("name", n [str, .pattern (Re.prefixes ["unsaid__"])]),
          ("sorts", ref "common.json#/$defs/strings"),
          ("description", str)]])]),
  ("reached", n [
    arr,
    .items (n [
        obj,
        .required ["predicate", "sorts", "ast"],
        closed [
          ("predicate", str),
          ("sorts", ref "common.json#/$defs/strings"),
          ("ast", ref "common.json#/$defs/generated_formula")]])]),
  ("fragment_fill", .type ["boolean"])]

def elaborateRequired : List String :=
  ["id", "status", "order", "background", "premises", "conflict_targets", "fragment", "fill", "unspecified", "unsaid", "reached", "fragment_fill"]

def elaborate : Shape :=
  c
    "NormDefaults.Wire.regeneratedU: Norms.Wire.regenerated of fill U, then Fill_T, the unspecified predicates, their unsaid predicates, the default-reached targets and the fragment flag of fill U."
    [obj, .required (elaborateRequired ++ ["filled_environment_id", "fill_hash", "fill_labels",
      "environment_id", "document_hash"]),
      closed (elaborateFields ++ [("filled_environment_id", str), ("fill_hash", str),
        ("fill_labels", ref "common.json#/$defs/strings"), ("environment_id", str),
        ("document_hash", str)])]

def base_environment : Shape :=
  copied "the route's base environment regenerated from the request's environment (its soft or rights block removed), compared whole with Python's by the caller" <| c
    "NormDefaults.Wire.withUnsaid of SoftNorms.Wire.basePrimeJson or Rights.Wire.basePrimeJsonR: Norms.Replay.baseEnvironmentJson of the request environment, with the decision predicates and the unsaid predicates added."
    [
      obj,
      .required ["language", "profiles", "spec_revision", "vocabulary"],
      closed [
        ("language", n [str, .equals "/environment/language"]),
        ("profiles", ref "common.json#/$defs/strings"),
        ("spec_revision", n [str, .equals "/environment/spec_revision"]),
        ("vocabulary", n [
          obj,
          .required ["sorts", "predicates", "constants"],
          closed [
            ("sorts", n [obj, .equals "/environment/vocabulary/sorts"]),
            ("constants", n [obj, .equals "/environment/vocabulary/constants"]),
            ("predicates", n [
              obj,
              .object [] (some (n [obj, .required ["arguments"], props [("arguments", ref "common.json#/$defs/strings")]]))])]])]]

def layered_elaborate : Shape :=
  c
    "NormDefaults.Wire.layeredElaborate (the soft and rights branches): regeneratedU of fill U, then the soft and rights layer premises of the route's base, its environment id and document hash, and its base environment."
    [
      obj,
      .required (elaborateRequired ++ ["soft", "rights", "environment_id", "document_hash", "base_environment"]),
      closed (elaborateFields ++ [
        ("soft", ref "common.json#/$defs/labelled_list"),
        ("rights", ref "common.json#/$defs/labelled_list"),
        ("environment_id", str),
        ("document_hash", str),
        ("base_environment", ref "#/$defs/base_environment")])]

def report_line : Shape :=
  c
    "NormDefaults.Wire.LineU.toJson: one regulated predicate's lines (spec 3.2); `witness` (NormDefaults.Wire.WitnessRow.toJson: the tuple's entity ids and every unsaid table of the checked filled situation) and `value` (NormDefaults.Wire.completedLabel: the completion's value where no author rule decides) exactly on a reachable line."
    [
      obj,
      .required ["predicate", "completion", "reached", "lines", "inherits_from"],
      closed [
        ("predicate", str),
        ("completion", enumS ["deny", "allow", "unspecified"]),
        ("reached", enumS ["none", "reachable", "unknown"]),
        ("lines", ref "common.json#/$defs/strings"),
        ("inherits_from", ref "common.json#/$defs/strings"),
        ("value", enumS ["yes", "no", "unsaid"]),
        ("witness", n [
          obj,
          .required ["tuple", "filling"],
          closed [
            ("tuple", ref "common.json#/$defs/strings"),
            ("filling", n [obj, .object [] (some (n [arr, .items (ref "common.json#/$defs/strings")]))])]])],
      .ite (.required ["witness"]) (.required ["value"]) (.not (.required ["value"]))]

def report_row : Shape :=
  c "NormDefaults.Wire.ReportG.toJson (norm-defaults-report): the lines of every regulated predicate, the residual and the findings." [
    obj,
    .required ["id", "status", "report", "residual", "findings"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("report", n [arr, .items (ref "#/$defs/report_line")]),
      ("residual", n [
        obj,
        .required ["gaps", "ungrounded_defaults"],
        closed [("gaps", ref "common.json#/$defs/strings"), ("ungrounded_defaults", ref "common.json#/$defs/nat")]]),
      ("findings", ref "common.json#/$defs/strings")]]

/-- An unsaid atom: its regulated predicate and the tuple's entity ids. -/
def atom : Shape :=
  n [obj, .required ["predicate", "tuple"],
    closed [("predicate", str), ("tuple", ref "common.json#/$defs/strings")]]

def status : Shape :=
  c "NormDefaults.Run.runOtherCase and Wire.runLayered norm-defaults-status: the requested predicate's point status, then NormDefaults.Wire.statusFields: the tuple's entity ids, the deciding author rules and the atoms where two UNDECIDED fillings differ." [
    obj,
    .required ["id", "status", "point_status", "predicate", "tuple", "rules", "differs"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("point_status", enumS ["SETTLED yes", "SETTLED no", "UNDECIDED", "UNKNOWN"]),
      ("predicate", n [str, .equals "/predicate"]),
      ("tuple", ref "common.json#/$defs/strings"),
      ("rules", ref "common.json#/$defs/strings"),
      ("differs", n [arr, .items (ref "#/$defs/atom")])]]

def witness_conflict : Shape :=
  c "A conflict witness replay (NormDefaults.Wire.replayWitnessU and Wire.witnessConflictX): the requested target; exactly a CONFLICT also carries NormDefaults.Wire.conflictFields: the tuple's entity ids, the kind, the deciding assignment and the deciding author rules." [
    obj,
    .required ["id", "status", "verdict", "target", "targets"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("verdict", enumS ["CONFLICT", "UNKNOWN"]),
      ("target", n [str, .equals "/witness/target"]),
      ("targets", ref "common.json#/$defs/strings"),
      ("tuple", ref "common.json#/$defs/strings"),
      ("kind", enumS ["settled", "latent"]),
      ("under", n [arr, .items (n [obj, .required ["predicate", "tuple", "value"],
        closed [("predicate", str), ("tuple", ref "common.json#/$defs/strings"), ("value", .type ["boolean"])]])]),
      ("rules", ref "common.json#/$defs/strings")],
    .ite (props [("verdict", constS "CONFLICT")]) (.required ["tuple", "kind", "under", "rules"])
      (.allOf [.not (.required ["tuple"]), .not (.required ["kind"]), .not (.required ["under"]),
        .not (.required ["rules"])])]

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
        (ref "#/$defs/kind/norm-defaults-elaborate", .anyOf [ref "#/$defs/elaborate", ref "#/$defs/layered_elaborate"]),
        (.allOf [ref "#/$defs/kind/norm-defaults-conflict", .required ["witness"]], ref "#/$defs/witness_conflict"),
        (ref "#/$defs/kind/norm-defaults-conflict", ref "common.json#/$defs/packages_conflict"),
        (ref "#/$defs/kind/norm-defaults-status", ref "#/$defs/status"),
        (.allOf [ref "#/$defs/kind/norm-defaults-gaps", .required ["model"]], ref "#/$defs/gaps_model"),
        (ref "#/$defs/kind/norm-defaults-gaps", ref "#/$defs/gaps"),
        (ref "#/$defs/kind/norm-defaults-certificate", ref "#/$defs/certificate"),
        (ref "#/$defs/kind/norm-defaults-report", ref "#/$defs/report_row")]]),
    ((.bool true), ref "norms.json#/row")]

def file : File where
  name := "norm-defaults.json"
  comment := some "Mode norm-defaults: NormDefaults.Run.runCaseReported (formerly ve_norm_defaults_route). A case on the norm-defaults path (usesNormDefaultsPath) is answered by the norm-defaults runner; every other case is delegated unchanged to the norms mode's runner."
  top := [("row", «row»)]
  defs := [
    ("norm_defaults_path", .schema norm_defaults_path),
    ("kind", kind),
    ("elaborate", .schema elaborate),
    ("base_environment", .schema base_environment),
    ("layered_elaborate", .schema layered_elaborate),
    ("atom", .schema atom),
    ("status", .schema status),
    ("witness_conflict", .schema witness_conflict),
    ("gaps_model", .schema gaps_model),
    ("gaps", .schema gaps),
    ("certificate", .schema certificate),
    ("report_line", .schema report_line),
    ("report_row", .schema report_row)]

end ResponseShape.Schemas.NormDefaults
