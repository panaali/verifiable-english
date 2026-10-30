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
    ("norm-defaults-report", kindIs "norm-defaults-report"),
    ("defaults-elaborate", kindIs "defaults-elaborate"),
    ("defaults-coherence", kindIs "defaults-coherence"),
    ("defaults-certificate", kindIs "defaults-certificate"),
    ("defaults-model", kindIs "defaults-model")]

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
          ("description", n [str, .minLength 1])]])]),
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
      "environment_id", "document_hash", "wordings"]),
      closed (elaborateFields ++ [("filled_environment_id", str), ("fill_hash", str),
        ("fill_labels", ref "common.json#/$defs/strings"), ("environment_id", str),
        ("document_hash", str),
        ("wordings", c "Norms.Wire.plainWordings of the source: one wording per plain predicate with an act, by its name."
          [ref "common.json#/$defs/string_map"])])]

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

def soft_admission : Shape :=
  c "NormDefaults.Admission.encodeAdmittedX (the soft branch's admission, Run.runCase's soft dispatch): W2's admission answer on the filled soft tree and the open coherence premises the report assumes, as the soft route's admission answer lists them." [
    obj,
    .required ["id", "status", "admitted", "report", "report_id", "kinds", "conditional_on"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("admitted", .const (.bool true)),
      ("report", ref "common.json#/$defs/bound_report"),
      ("report_id", ref "common.json#/$defs/hex64"),
      ("kinds", n [arr, .items (ref "common.json#/$defs/kind"), .equals "/document/units/*/kind"]),
      ("conditional_on", ref "soft-norms.json#/$defs/coherence_labels")]]

def defaults_elaborate : Shape :=
  c "Defaults.Wire.elaborateFields (defaults-elaborate): Dflt_T's labelled premises, then each colliding pair's two rule names and coherence premise (Defaults.Wire.elaborateRows)." [
    obj,
    .required ["id", "status", "deciders", "default_premises", "coherence_targets"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("deciders", ref "common.json#/$defs/strings"),
      ("default_premises", n [arr, .items (n [arr, .prefixItems [ref "common.json#/$defs/text",
        ref "common.json#/$defs/generated_formula"], .minItems 2, .maxItems 2])]),
      ("coherence_targets", n [arr, .items (n [arr, .prefixItems [str, str, ref "common.json#/$defs/generated_formula"],
        .minItems 3, .maxItems 3])])]]

/-- The situation a default answer shows (`Defaults.Wire.situationJson`). -/
def defaults_situation : Shape :=
  c "Defaults.Wire.situationJson: every unsaid table of the checked filled situation (NormDefaults.Wire.witnessRow), rows as entity ids." [
    obj,
    .required ["filling"],
    closed [("filling", n [obj, .object [] (some (n [arr, .items (ref "common.json#/$defs/strings")]))])]]

def defaults_coherence : Shape :=
  c "Defaults.Wire.coherenceFields (defaults-coherence): the verdict and each colliding pair's status; with COLLISION, the pair the request's collision names, the tuple Lean finds (collisionTuple), DE7's deciders (giveWayDeciders) and the situation." [
    obj,
    .required ["id", "status", "verdict", "pairs"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("verdict", enumS ["COHERENT", "COLLISION", "UNKNOWN"]),
      ("pairs", n [arr, .items (n [obj, .required ["rules", "status"],
        closed [("rules", ref "common.json#/$defs/string_pair"), ("status", enumS ["resolved", "collision", "unknown"])]])]),
      ("collision", n [obj, .required ["rules", "tuple", "deciders"],
        closed [("rules", n [ref "common.json#/$defs/string_pair", .equals "/collision/rules"]),
          ("tuple", ref "common.json#/$defs/strings"), ("deciders", ref "common.json#/$defs/strings")]]),
      ("situation", ref "#/$defs/defaults_situation")],
    .ite (props [("verdict", constS "COLLISION")]) (.required ["collision", "situation"])
      (.allOf [.not (.required ["collision"]), .not (.required ["situation"])])]

def defaults_certificate : Shape :=
  c "Defaults.Wire.certFields (defaults-certificate): FOLLOWS with its basis, form and kept assumptions (defaults_certificate_sound), or UNKNOWN with its reason (CertReplay.reason)." [
    obj,
    .required ["id", "status", "verdict"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("verdict", enumS ["FOLLOWS", "UNKNOWN"]),
      ("basis", enumS ["strict", "needs", "unsettled"]),
      ("form", enumS ["short", "long"]),
      ("assumptions", ref "common.json#/$defs/strings"),
      ("deciders", ref "common.json#/$defs/strings"),
      ("reason", str)],
    .ite (props [("verdict", constS "FOLLOWS")])
      (.allOf [.required ["basis", "form", "assumptions", "deciders"], .not (.required ["reason"])])
      (.allOf [.required ["reason"], .not (.required ["basis"]), .not (.required ["form"]),
        .not (.required ["assumptions"]), .not (.required ["deciders"])])]

def defaults_model : Shape :=
  c "Defaults.Wire.modelFields (defaults-model): DOES-NOT-FOLLOW with the situation and each exception the text's own conditions force there (defaults_model_sound, forcedAt_sound), or UNKNOWN." [
    obj,
    .required ["id", "status", "verdict"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("verdict", enumS ["DOES-NOT-FOLLOW", "UNKNOWN"]),
      ("situation", ref "#/$defs/defaults_situation"),
      ("forced", n [arr, .items (n [obj, .required ["rule", "condition", "tuple"],
        closed [("rule", str), ("condition", ref "common.json#/$defs/nat"), ("tuple", ref "common.json#/$defs/strings")]])])],
    .ite (props [("verdict", constS "DOES-NOT-FOLLOW")]) (.required ["situation", "forced"])
      (.allOf [.not (.required ["situation"]), .not (.required ["forced"])])]

def «row» : Shape :=
  .select [
    (ref "#/$defs/norm_defaults_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      .select [
        (ref "#/$defs/kind/admission", .anyOf [ref "common.json#/$defs/admission", ref "#/$defs/soft_admission"]),
        (ref "#/$defs/kind/norm-defaults-elaborate", .anyOf [ref "#/$defs/elaborate", ref "#/$defs/layered_elaborate"]),
        (.allOf [ref "#/$defs/kind/norm-defaults-conflict", .required ["witness"]], ref "#/$defs/witness_conflict"),
        (ref "#/$defs/kind/norm-defaults-conflict", ref "common.json#/$defs/packages_conflict"),
        (ref "#/$defs/kind/norm-defaults-status", ref "#/$defs/status"),
        (.allOf [ref "#/$defs/kind/norm-defaults-gaps", .required ["model"]], ref "#/$defs/gaps_model"),
        (ref "#/$defs/kind/norm-defaults-gaps", ref "#/$defs/gaps"),
        (ref "#/$defs/kind/norm-defaults-certificate", ref "#/$defs/certificate"),
        (ref "#/$defs/kind/norm-defaults-report", ref "#/$defs/report_row"),
        (ref "#/$defs/kind/defaults-elaborate", ref "#/$defs/defaults_elaborate"),
        (ref "#/$defs/kind/defaults-coherence", ref "#/$defs/defaults_coherence"),
        (ref "#/$defs/kind/defaults-certificate", ref "#/$defs/defaults_certificate"),
        (ref "#/$defs/kind/defaults-model", ref "#/$defs/defaults_model")]]),
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
    ("soft_admission", .schema soft_admission),
    ("report_line", .schema report_line),
    ("report_row", .schema report_row),
    ("defaults_elaborate", .schema defaults_elaborate),
    ("defaults_situation", .schema defaults_situation),
    ("defaults_coherence", .schema defaults_coherence),
    ("defaults_certificate", .schema defaults_certificate),
    ("defaults_model", .schema defaults_model)]


/- The plain `elaborate` row as `tools/response_schemas.py` renders it (ap-1be): a closed object whose every member is
required, `wordings` (`Norms.Run.wordingsJson`) a `string_map` beside the base's members. -/
#guard (ResponseShape.render "norm-defaults.json" 64 elaborate).toOption.map (fun j => (j.getObjValD "type",
    j.getObjValD "additionalProperties", j.getObjValD "required", (j.getObjValD "properties").getObj?.toOption.map
    (·.toList.map (·.1)), ((j.getObjValD "properties").getObjValD "wordings").getObjValD "$ref")) ==
  some (.str "object", .bool false, toJson ["id", "status", "order", "background", "premises", "conflict_targets",
    "fragment", "fill", "unspecified", "unsaid", "reached", "fragment_fill", "filled_environment_id", "fill_hash",
    "fill_labels", "environment_id", "document_hash", "wordings"], some ["background", "conflict_targets",
    "document_hash", "environment_id", "fill", "fill_hash", "fill_labels", "filled_environment_id", "fragment",
    "fragment_fill", "id", "order", "premises", "reached", "status", "unsaid", "unspecified", "wordings"],
    .str "common.json#/$defs/string_map")

end ResponseShape.Schemas.NormDefaults
