import VE.Service.Protocol
import ResponseShape
import ResponseShape.CaseDeciders

/-! The source of `ve/backends/lean_service_schema/discourse.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Discourse
open Lean ResponseShape

def discourse_path : Shape :=
  decidedCase .discoursePath <|
  c
    "Discourse.Run.usesDiscoursePath: a document text, the ve.discourse@1 profile in a profile list of strings (Route.Gate.profilesOf), or a discourse-* kind."
    [
      obj,
      .anyOf [
        n [.required ["document"], props [("document", str)]],
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["profiles"],
              props [("profiles", n [arr, .items str, .contains (constS "ve.discourse@1")])]])]],
        n [.required ["kind"], props [("kind", n [str, .pattern (Re.prefixes ["discourse-"])])]]]]

def kind : Def :=
  .group none [
    ("admission", kindIs "admission"),
    ("discourse-validity", kindIs "discourse-validity"),
    ("discourse-resolve", kindIs "discourse-resolve"),
    ("discourse-joint", kindIs "discourse-joint")]

def target_kind : Shape :=
  enumS ["entity", "predicate", "unit", "anchor", "rule", "claim", "document"]

def reference : Shape :=
  c
    "Discourse.Admission.referencesJson: a mention, its unit, its form, its front-matter target (Wire.decodeTarget's fields) and its status."
    [
      obj,
      .required ["mention", "unit", "form", "target", "status"],
      closed [
        ("mention", str),
        ("unit", str),
        ("form", enumS [
          "pronoun",
          "demonstrative",
          "definite",
          "ordinal_pair",
          "such",
          "possessive",
          "plural",
          "section_ref",
          "definition_ref",
          "document_name",
          "citation",
          "navigation"]),
        ("target", copied "the mention's front-matter target, copied from the request's document (Discourse.Admission.referencesJson)" <| n [
          obj,
          .required ["kind"],
          closed [
            ("kind", ref "#/$defs/target_kind"),
            ("name", str),
            ("version", ref "common.json#/$defs/nat"),
            ("members", ref "common.json#/$defs/strings"),
            ("pair", ref "common.json#/$defs/string_pair"),
            ("units", ref "common.json#/$defs/strings"),
            ("content_name", str)]]),
        ("status", enumS ["pending", "navigation", "resolved"])]]

def validity_map : Shape :=
  c "Discourse.Admission.verdictText per validity-claim unit." [
    obj,
    .object [] (some (n [
          str,
          .pattern (.alt (.lit "checked") (.alt (.lit "refuted") (.alt (.lit "none") (Re.prefixes ["unconfirmed ("]))))]))]

def joint_count : Shape :=
  c "The number of compatible joint choices, or the joint error." [
    .anyOf [n [.type ["integer"], .minimum 1], ref "common.json#/$defs/text"]]

/-- The members of every admission, its joint set's aside. -/
def admissionFields : List (String × Shape) := [
  ("id", ref "common.json#/$defs/id_ok"),
  ("status", constS "ok"),
  ("admitted", .enum [(.bool true), (.str "UNKNOWN")]),
  ("reading_verdicts", n [obj, .object [] (some (constS "UNKNOWN (joint choices)"))]),
  ("report", ref "common.json#/$defs/report"),
  ("report_id", ref "common.json#/$defs/hex64_or_empty"),
  ("inner_report_id", ref "common.json#/$defs/hex64_or_empty"),
  ("document_id", ref "common.json#/$defs/hex64_or_empty"),
  ("source_id", ref "common.json#/$defs/hex64_or_empty"),
  ("environment_id", ref "common.json#/$defs/hex64_or_empty"),
  ("definitions_version", ref "common.json#/$defs/hex64_or_empty"),
  ("kinds", n [arr, .items (ref "common.json#/$defs/kind")]),
  ("references", n [arr, .items (ref "#/$defs/reference")]),
  ("bound", n [obj, .object [] (some (ref "common.json#/$defs/generated_formula"))]),
  ("meaning_ids", n [obj, .object [] (some (ref "common.json#/$defs/hex64"))]),
  ("presuppositions", n [
    obj,
    .object [] (some (n [str, .pattern (Re.prefixes ["discourse:presupposition:"])]))]),
  ("pending", n [
    arr,
    .items (n [
        arr,
        .minItems 2,
        .maxItems 2,
        .prefixItems [str, n [str, .pattern (Re.prefixes ["PresuppositionUnresolved: "])]]])]),
  ("validity", ref "#/$defs/validity_map"),
  ("self_truth", ref "common.json#/$defs/strings"),
  ("statuses", n [obj, .object [] (some (enumS ["CHECKED", "OPEN", "LABELLED", "UNFORMALISED"]))])]

def admissionRequired : List String :=
  ["id", "status", "admitted", "reading_verdicts", "report", "report_id", "inner_report_id", "document_id", "source_id", "environment_id", "definitions_version", "kinds", "references", "bound", "meaning_ids", "presuppositions", "pending", "validity", "self_truth", "statuses", "joint"]

def admission : Shape :=
  c
    "Discourse.Run.encodeAdmission: the wrapper's admission (ve-document@2, or a lifted ve-document@1 text whose identities are empty and whose joint is the missing manifest). A completed joint set has its count, its choices and their disjunction (Discourse.Run.jointFields); a set over its budget has its diagnostic and neither."
    [
      .anyOf [
        n [
          obj,
          .required (admissionRequired ++ ["joint_choices", "joint_formula"]),
          closed (admissionFields ++ [
            ("joint", n [.type ["integer"], .minimum 1]),
            ("joint_choices", ref "#/$defs/choices"),
            ("joint_formula", ref "common.json#/$defs/generated_formula")])],
        n [
          obj,
          .required admissionRequired,
          closed (admissionFields ++ [("joint", ref "common.json#/$defs/text")])]]]

def choices : Shape :=
  c "Discourse.Run.choicesJson: per compatible choice, [set, version, reading index] for each active open set." [
    arr,
    .minItems 1,
    .items (n [
        arr,
        .items (n [
            arr,
            .minItems 3,
            .maxItems 3,
            .prefixItems [str, ref "common.json#/$defs/nat", ref "common.json#/$defs/nat"]])])]

def validity : Shape :=
  c "Discourse.Run discourse-validity: each validity claim's verdict." [
    obj,
    .required ["id", "status", "validity"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("validity", ref "#/$defs/validity_map")]]

def resolved_target : Shape :=
  c "Discourse.Run.targetJson: members and units only when nonempty." [
    obj,
    .required ["kind"],
    closed [
      ("kind", ref "#/$defs/target_kind"),
      ("name", str),
      ("members", n [ref "common.json#/$defs/strings", .minItems 1]),
      ("pair", ref "common.json#/$defs/string_pair"),
      ("units", n [ref "common.json#/$defs/strings", .minItems 1])]]

def resolve : Shape :=
  c
    "Discourse.Run.runResolve: each bound unit's resolution, each mention's accessible and recorded targets, well-formedness and the joint count."
    [
      obj,
      .required ["id", "status", "units", "mentions", "well_formed", "environment_id", "source_id", "joint"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("units", n [
          obj,
          .object [] (some (.anyOf [
                n [
                  obj,
                  .required ["status", "formula", "meaning_id"],
                  closed [
                    ("status", constS "resolved"),
                    ("formula", ref "common.json#/$defs/generated_formula"),
                    ("meaning_id", ref "common.json#/$defs/hex64")]],
                n [
                  obj,
                  .required ["status", "error"],
                  closed [("status", constS "error"), ("error", ref "common.json#/$defs/text")]]]))]),
        ("mentions", n [
          obj,
          .object [] (some (n [
                obj,
                .required ["accessible", "recorded", "accessible_recorded"],
                closed [
                  ("accessible", n [arr, .items (ref "#/$defs/resolved_target")]),
                  ("recorded", ref "#/$defs/resolved_target"),
                  ("accessible_recorded", .type ["boolean"]),
                  ("pin", ref "common.json#/$defs/nat")]]))]),
        ("well_formed", ref "common.json#/$defs/text"),
        ("environment_id", ref "common.json#/$defs/hex64"),
        ("source_id", ref "common.json#/$defs/hex64"),
        ("joint", ref "#/$defs/joint_count")]]

def joint : Shape :=
  c "Discourse.Run.runJoint: the compatible choices and their disjunction, or the diagnostic." [
    .anyOf [
      n [
        obj,
        .required ["id", "status", "verdict", "choices", "joint"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", constS "COMPLETE"),
          ("choices", ref "#/$defs/choices"),
          ("joint", ref "common.json#/$defs/generated_formula")]],
      n [
        obj,
        .required ["id", "status", "verdict", "diagnostic"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", enumS ["UNKNOWN", "INVALID"]),
          ("diagnostic", ref "common.json#/$defs/text")]]]]

def «row» : Shape :=
  .select [
    (ref "#/$defs/discourse_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      .select [
        (ref "#/$defs/kind/admission", ref "#/$defs/admission"),
        (ref "#/$defs/kind/discourse-validity", ref "#/$defs/validity"),
        (ref "#/$defs/kind/discourse-resolve", ref "#/$defs/resolve"),
        (ref "#/$defs/kind/discourse-joint", ref "#/$defs/joint")]]),
    ((.bool true), ref "route.json#/row")]

def file : File where
  name := "discourse.json"
  comment := some "Mode discourse: Discourse.Run.runCaseReported (formerly ve_discourse_route). A case on the discourse path (usesDiscoursePath) is answered by the discourse runner; every other case is delegated unchanged to the route mode's runner."
  top := [("row", «row»)]
  defs := [
    ("discourse_path", .schema discourse_path),
    ("kind", kind),
    ("target_kind", .schema target_kind),
    ("reference", .schema reference),
    ("validity_map", .schema validity_map),
    ("joint_count", .schema joint_count),
    ("choices", .schema choices),
    ("admission", .schema admission),
    ("validity", .schema validity),
    ("resolved_target", .schema resolved_target),
    ("resolve", .schema resolve),
    ("joint", .schema joint)]

end ResponseShape.Schemas.Discourse
