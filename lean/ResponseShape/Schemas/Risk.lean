import VE.Service.Protocol
import ResponseShape

/-! The source of `ve/backends/lean_service_schema/risk.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Risk
open Lean ResponseShape

def risk_path : Shape :=
  decidedBy "Risk.Run.usesRiskPath" VE.Risk.Run.usesRiskPath <|
  c "Risk.Run.usesRiskPath: the risk@0 profile, the environment's risk block or a risk-* kind." [
    obj,
    .anyOf [
      n [
        .required ["environment"],
        props [
          ("environment", n [
            obj,
            .required ["profiles"],
            props [("profiles", n [arr, .contains (constS "risk@0")])]])]],
      n [.required ["environment"], props [("environment", n [obj, .required ["risk"]])]],
      n [.required ["kind"], props [("kind", n [str, .pattern (Re.prefixes ["risk-"])])]]]]

def kind : Def :=
  .group none [
    ("admission", kindIs "admission"),
    ("risk-elaborate", kindIs "risk-elaborate"),
    ("risk-decision", kindIs "risk-decision"),
    ("risk-conflict", kindIs "risk-conflict"),
    ("risk-followable", kindIs "risk-followable"),
    ("risk-audit", kindIs "risk-audit"),
    ("risk-certificate", kindIs "risk-certificate")]

def risk_labels : Shape :=
  c "Risk.Background.riskPremiseLabels." [
    arr,
    .items (enumS [
        "risk:certain_possible",
        "risk:severity_closure",
        "risk:classes_distinct",
        "risk:order",
        "risk:class_functional",
        "risk:class"])]

def admission : Shape :=
  c "Risk.Run.encodeAdmitted: W2's admission answer, conditional on the source labels and the risk premises." [
    obj,
    .required ["id", "status", "admitted", "report", "report_id", "kinds", "conditional_on"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("admitted", .const (.bool true)),
      ("report", ref "common.json#/$defs/bound_report"),
      ("report_id", ref "common.json#/$defs/hex64"),
      ("kinds", n [arr, .items (ref "common.json#/$defs/kind"), .equals "/document/units/*/kind"]),
      ("conditional_on", ref "common.json#/$defs/strings")]]

def elaborate : Shape :=
  c
    "Risk.Wire.regenerated: the policy identities, E_risk's generated vocabulary, the legend, the risk premises, the unranked severity pairs, then the alternatives fields of the inlined tree and Norms.Wire.regenerated."
    [
      obj,
      .required ["id", "status", "environment_id", "document_hash", "e_risk", "legend", "risk_premises", "unranked_severities", "inlined", "alternatives", "base_premises", "followable", "unmapped_obligations", "order", "background", "premises", "conflict_targets", "fragment"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("environment_id", ref "common.json#/$defs/hex64"),
        ("document_hash", ref "common.json#/$defs/hex64"),
        ("e_risk", n [
          obj,
          .required ["sort", "classes", "predicates", "words"],
          closed [
            ("sort", str),
            ("classes", ref "common.json#/$defs/strings"),
            ("predicates", n [obj, .object [] (some (ref "common.json#/$defs/strings"))]),
            ("words", n [
              obj,
              .required ["risk__or_worse", "risk__less_worst"],
              closed [
                ("risk__or_worse", ref "common.json#/$defs/string_pair"),
                ("risk__less_worst", ref "common.json#/$defs/string_pair")]])]]),
        ("legend", ref "common.json#/$defs/nonempty_strings"),
        ("risk_premises", n [
          arr,
          .items (n [
              ref "common.json#/$defs/labelled",
              props [
                ("label", enumS [
                  "risk:certain_possible",
                  "risk:severity_closure",
                  "risk:classes_distinct",
                  "risk:order",
                  "risk:class_functional",
                  "risk:class"])]])]),
        ("unranked_severities", n [arr, .items (ref "common.json#/$defs/string_pair")]),
        ("inlined", ref "alternatives.json#/$defs/regenerated/inlined"),
        ("alternatives", ref "alternatives.json#/$defs/regenerated/alternatives"),
        ("base_premises", ref "common.json#/$defs/labelled_list"),
        ("followable", ref "alternatives.json#/$defs/regenerated/followable"),
        ("unmapped_obligations", ref "alternatives.json#/$defs/regenerated/unmapped_obligations"),
        ("order", ref "common.json#/$defs/strings"),
        ("background", ref "common.json#/$defs/norms_background"),
        ("premises", ref "common.json#/$defs/layer_premises"),
        ("conflict_targets", ref "common.json#/$defs/conflict_targets"),
        ("fragment", .type ["boolean"])]]

def cell : Shape :=
  n [obj, .required ["alternative", "harm"], closed [("alternative", str), ("harm", str)]]

def endpoint : Def :=
  .group (some "Risk.Run.endpointJson and dirName.") [
    ("estimate", str),
    ("side", enumS ["lo", "hi"]),
    ("direction", enumS ["down", "up"])]

def decision : Shape :=
  c "Risk.Run.runDecision: the identities, then a CONFLICT or the per-alternative evaluation." [
    .anyOf [
      n [
        obj,
        .required ["id", "status", "environment_id", "document_hash", "decision_record_id", "verdict", "target", "tuple", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("environment_id", ref "common.json#/$defs/hex64"),
          ("document_hash", ref "common.json#/$defs/hex64"),
          ("decision_record_id", ref "common.json#/$defs/hex64_or_empty"),
          ("verdict", constS "CONFLICT"),
          ("target", str),
          ("tuple", ref "common.json#/$defs/strings"),
          ("text", ref "common.json#/$defs/text")]],
      n [
        obj,
        .required ["id", "status", "environment_id", "document_hash", "decision_record_id", "tables", "statuses", "worst_cases", "margins", "record_invalid", "record_conflict", "lines", "legend", "clear", "conditional_on", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("environment_id", ref "common.json#/$defs/hex64"),
          ("document_hash", ref "common.json#/$defs/hex64"),
          ("decision_record_id", ref "common.json#/$defs/hex64_or_empty"),
          ("tables", n [
            obj,
            .required ["might", "leads"],
            closed [
              ("might", n [
                arr,
                .items (n [
                    obj,
                    .required ["alternative", "harm"],
                    closed [
                      ("alternative", str),
                      ("harm", str),
                      ("witness", n [
                        arr,
                        .items (n [
                            obj,
                            .required ["quantity", "value"],
                            closed [("quantity", str), ("value", str)]])])]])]),
              ("leads", n [arr, .items (ref "#/$defs/cell")])]]),
          ("statuses", n [
            arr,
            .items (n [
                obj,
                .required ["alternative", "permitted", "required", "clear", "rules", "by_default"],
                closed [
                  ("alternative", str),
                  ("permitted", .type ["boolean"]),
                  ("required", .type ["boolean"]),
                  ("clear", .type ["boolean"]),
                  ("rules", n [arr, .items (n [.type ["integer"], .minimum 1])]),
                  ("by_default", .type ["boolean"])],
                .ite (props [("rules", .maxItems 0)]) (props [("by_default", .const (.bool true))]) (props [
                    ("by_default", .const (.bool false))])])]),
          ("worst_cases", n [
            obj,
            .object [] (some (n [
                  arr,
                  .items (n [obj, .required ["harm", "class"], closed [("harm", str), ("class", str)]])]))]),
          ("margins", n [
            arr,
            .items (n [
                obj,
                .required ["estimate", "side", "alternative", "direction"],
                closed [
                  ("estimate", ref "#/$defs/endpoint/estimate"),
                  ("side", ref "#/$defs/endpoint/side"),
                  ("alternative", str),
                  ("direction", ref "#/$defs/endpoint/direction"),
                  ("nearest", str),
                  ("no_single_valid_change", .const (.bool true))],
                .anyOf [
                  n [.required ["nearest"], .not (.required ["no_single_valid_change"])],
                  n [.required ["no_single_valid_change"], .not (.required ["nearest"])]]])]),
          ("record_invalid", n [
            arr,
            .items (n [
                obj,
                .required ["estimate", "side", "direction", "value", "diagnostic"],
                closed [
                  ("estimate", ref "#/$defs/endpoint/estimate"),
                  ("side", ref "#/$defs/endpoint/side"),
                  ("direction", ref "#/$defs/endpoint/direction"),
                  ("value", str),
                  ("diagnostic", ref "common.json#/$defs/text")]])]),
          ("record_conflict", n [
            arr,
            .items (n [
                obj,
                .required ["estimate", "side", "direction", "value"],
                closed [
                  ("estimate", ref "#/$defs/endpoint/estimate"),
                  ("side", ref "#/$defs/endpoint/side"),
                  ("direction", ref "#/$defs/endpoint/direction"),
                  ("value", str)]])]),
          ("lines", n [
            obj,
            .required ["unexamined_possible", "assumed_ruled_out", "point_estimates", "default_decided", "dilemmas"],
            closed [
              ("unexamined_possible", ref "common.json#/$defs/strings"),
              ("assumed_ruled_out", n [
                obj,
                .required ["decider", "cells"],
                closed [("decider", str), ("cells", ref "common.json#/$defs/strings")]]),
              ("point_estimates", ref "common.json#/$defs/strings"),
              ("default_decided", ref "common.json#/$defs/strings"),
              ("dilemmas", n [ref "common.json#/$defs/strings", .maxItems 1])]]),
          ("legend", n [ref "common.json#/$defs/nonempty_strings", .maxItems 3]),
          ("clear", ref "common.json#/$defs/strings"),
          ("conditional_on", ref "common.json#/$defs/strings"),
          ("text", ref "common.json#/$defs/text")]]]]

def conflict : Shape :=
  c "Risk.Run.runConflict over certificate packages: the verdict and the targets (no detail)." [
    obj,
    .required ["id", "status", "verdict", "targets"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("verdict", enumS ["CONFLICT-FREE", "UNKNOWN"]),
      ("targets", ref "common.json#/$defs/strings")]]

def followable_witness : Shape :=
  c "Risk.Run.runFollowable with a dilemma witness." [
    .anyOf [
      n [
        obj,
        .required ["id", "status", "verdict", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", enumS ["not computed", "UNKNOWN"]),
          ("text", ref "common.json#/$defs/text")]],
      n [
        obj,
        .required ["id", "status", "verdict", "chooser", "diagnosis", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", constS "DILEMMA"),
          ("chooser", n [str, .equals "/witness/chooser"]),
          ("diagnosis", ref "common.json#/$defs/text"),
          ("text", ref "common.json#/$defs/text")]]]]

def followable : Shape :=
  c "Risk.Run.runFollowable over a certificate package: FOLLOWABLE carries the source labels and no text." [
    .anyOf [
      n [
        obj,
        .required ["id", "status", "verdict", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", enumS ["not computed", "UNKNOWN"]),
          ("text", ref "common.json#/$defs/text")]],
      n [
        obj,
        .required ["id", "status", "verdict", "conditional_on"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", constS "FOLLOWABLE"),
          ("conditional_on", ref "common.json#/$defs/strings")]]]]

def audit : Shape :=
  c "Risk.Run.runAudit: the audited alternative and the answers to the three audit questions." [
    obj,
    .required ["id", "status", "alternative", "q1", "q2", "procedure", "q3", "not_concluded"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("alternative", str),
      ("q1", ref "common.json#/$defs/text"),
      ("q2", ref "common.json#/$defs/text"),
      ("procedure", ref "common.json#/$defs/strings"),
      ("q3", ref "common.json#/$defs/strings"),
      ("not_concluded", n [ref "common.json#/$defs/strings", .maxItems 1])]]

def certificate : Shape :=
  c "Risk.Run.runCertificate: the certificate's verdict and the premises it is conditional on." [
    obj,
    .required ["id", "status", "valid", "conditional_on"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("valid", .type ["boolean"]),
      ("conditional_on", ref "common.json#/$defs/strings")]]

def «row» : Shape :=
  .select [
    (ref "#/$defs/risk_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      .select [
        (ref "#/$defs/kind/admission", ref "#/$defs/admission"),
        (ref "#/$defs/kind/risk-elaborate", ref "#/$defs/elaborate"),
        (ref "#/$defs/kind/risk-decision", ref "#/$defs/decision"),
        (.allOf [ref "#/$defs/kind/risk-conflict", .required ["witness"]], ref "alternatives.json#/$defs/conflict_witness"),
        (ref "#/$defs/kind/risk-conflict", ref "#/$defs/conflict"),
        (.allOf [ref "#/$defs/kind/risk-followable", .required ["witness"]], ref "#/$defs/followable_witness"),
        (ref "#/$defs/kind/risk-followable", ref "#/$defs/followable"),
        (ref "#/$defs/kind/risk-audit", ref "#/$defs/audit"),
        (ref "#/$defs/kind/risk-certificate", ref "#/$defs/certificate")]]),
    ((.bool true), ref "alternatives.json#/row")]

def file : File where
  name := "risk.json"
  comment := some "Mode risk: Risk.Run.runCaseReported (formerly ve_risk_route). A case on the risk path (usesRiskPath) is answered by the risk runner; every other case is delegated unchanged to the alternatives mode's runner."
  top := [("row", «row»)]
  defs := [
    ("risk_path", .schema risk_path),
    ("kind", kind),
    ("risk_labels", .schema risk_labels),
    ("admission", .schema admission),
    ("elaborate", .schema elaborate),
    ("cell", .schema cell),
    ("endpoint", endpoint),
    ("decision", .schema decision),
    ("conflict", .schema conflict),
    ("followable_witness", .schema followable_witness),
    ("followable", .schema followable),
    ("audit", .schema audit),
    ("certificate", .schema certificate)]

end ResponseShape.Schemas.Risk
