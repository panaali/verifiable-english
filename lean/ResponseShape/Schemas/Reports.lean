import VE.Service.Protocol
import ResponseShape

/-! The source of `ve/backends/lean_service_schema/reports.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Reports
open Lean ResponseShape

def reports_path : Shape :=
  decidedBy "Reports.Run.usesReportsPath" VE.Reports.Run.usesReportsPath <|
  c "Reports.Run.usesReportsPath: the reports@0 profile or a reports-* kind." [
    obj,
    .anyOf [
      n [
        .required ["environment"],
        props [
          ("environment", n [
            obj,
            .required ["profiles"],
            props [("profiles", n [arr, .contains (constS "reports@0")])]])]],
      n [.required ["kind"], props [("kind", n [str, .pattern (Re.prefixes ["reports-"])])]]]]

def kind : Def :=
  .group none [
    ("admission", kindIs "admission"),
    ("reports-elaborate", kindIs "reports-elaborate"),
    ("reports-certificate", kindIs "reports-certificate"),
    ("reports-countermodel", kindIs "reports-countermodel"),
    ("reports-scoped", kindIs "reports-scoped"),
    ("reports-status", kindIs "reports-status")]

def report_kind : Shape :=
  c
    "Route.Admission.renderKind of Attribution.Bridge.kindOf: a report's attributed kind (acts says, believes, wants, intends) or an assessment's hedged kind (could, likely), over an asserted, norm or definition body. Content depth is at most 16 (Wire.decodeContent)."
    [
      .fuel "report_kind" 32,
      .anyOf [
        enumS ["asserted", "norm", "definition"],
        n [
          arr,
          .tagged [
            ("attributed", [
              ref "common.json#/$defs/text",
              enumS ["says", "believes", "wants", "intends"],
              ref "#/$defs/report_kind"]),
            ("hedged", [enumS ["could", "likely"], ref "#/$defs/report_kind"])]]]]

def envelope : Shape :=
  c "Reports.Run.envelopeJson: the environment and document identities a certificate's envelope must name." [
    obj,
    .required ["environment_id", "document_id"],
    closed [
      ("environment_id", ref "common.json#/$defs/hex64_or_empty"),
      ("document_id", ref "common.json#/$defs/hex64_or_empty")]]

def key : Shape :=
  c "Attribution.Wire.generated: a report key or an assessment key." [
    .anyOf [
      n [
        obj,
        .required ["act", "holder_sort", "context", "complement_id"],
        closed [
          ("act", enumS ["says", "believes", "wants", "intends"]),
          ("holder_sort", str),
          ("context", str),
          ("complement_id", ref "common.json#/$defs/hex64_or_empty")]],
      n [
        obj,
        .required ["judgment", "assessment", "content_id"],
        closed [
          ("judgment", enumS ["may", "probably"]),
          ("assessment", str),
          ("content_id", ref "common.json#/$defs/hex64_or_empty")]]]]

def status_word : Shape :=
  enumS ["UNFORMALISED", "OPEN", "UNKNOWN", "LABELLED", "CHECKED"]

def verdict : Shape :=
  c "Reports.Run.scopedVerdict: one scoped check's verdict; UNKNOWN for unreplayable payloads has no scope." [
    .anyOf [
      n [
        obj,
        .required ["id", "status", "detail"],
        closed [("id", str), ("status", constS "UNKNOWN"), ("detail", constS "payloads")]],
      n [
        obj,
        .required ["id", "environment_id", "background", "status"],
        closed [
          ("id", str),
          ("environment_id", str),
          ("background", ref "common.json#/$defs/nat"),
          ("status", enumS ["FOLLOWS", "PAYLOADS INCONSISTENT", "DOES NOT FOLLOW"])]],
      n [
        obj,
        .required ["id", "environment_id", "background", "status", "detail"],
        closed [
          ("id", str),
          ("environment_id", str),
          ("background", ref "common.json#/$defs/nat"),
          ("status", constS "UNKNOWN"),
          ("detail", enumS [
            "witness does not refute",
            "witness replay over a quoted package's scope is not implemented",
            "envelope",
            "certificate does not replay",
            "no evidence"])]]]]

def admission : Shape :=
  c
    "Reports.Run.encodeAdmitted: W2's admission answer over the reports document, its envelope, and the kinds of the report, assessment and negated units."
    [
      obj,
      .required ["id", "status", "admitted", "report", "report_id", "envelope", "kinds"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("admitted", .const (.bool true)),
        ("report", ref "common.json#/$defs/bound_report"),
        ("report_id", ref "common.json#/$defs/hex64"),
        ("envelope", ref "#/$defs/envelope"),
        ("kinds", n [arr, .items (ref "#/$defs/report_kind")])]]

def elaborate : Shape :=
  c
    "Reports.Run.elaborated: E_reports' identity, the generated predicates with their keys, the premises, the open assessment terms with their records, the bridge formulas, the content identities, the envelope and the warnings."
    [
      obj,
      .required ["id", "status", "environment_reports_id", "keys", "premises", "open_terms", "bridge_formulas", "content_ids", "envelope", "warnings"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("environment_reports_id", ref "common.json#/$defs/hex64_or_empty"),
        ("keys", n [
          arr,
          .items (n [
              obj,
              .required ["name", "arguments", "key"],
              closed [
                ("name", n [str, .pattern (Re.prefixes ["reports__"])]),
                ("arguments", ref "common.json#/$defs/strings"),
                ("key", ref "#/$defs/key")]])]),
        ("premises", n [
          arr,
          .items (n [
              ref "common.json#/$defs/labelled",
              props [("label", .pattern (Re.prefixes ["report:", "assessment:"]))]])]),
        ("open_terms", n [
          arr,
          .items (n [
              obj,
              .required ["name", "arguments"],
              closed [
                ("name", str),
                ("arguments", ref "common.json#/$defs/strings"),
                ("record", n [
                  obj,
                  .required ["id", "context", "decided_by", "necessary", "sufficient", "factors", "precedents", "jurisdiction", "version"],
                  closed [
                    ("id", str),
                    ("context", str),
                    ("decided_by", str),
                    ("necessary", ref "common.json#/$defs/generated_formulas"),
                    ("sufficient", ref "common.json#/$defs/generated_formulas"),
                    ("factors", ref "common.json#/$defs/strings"),
                    ("precedents", ref "common.json#/$defs/strings"),
                    ("jurisdiction", str),
                    ("version", ref "common.json#/$defs/nat")]])]])]),
        ("bridge_formulas", n [
          arr,
          .items (n [
              obj,
              .required ["id", "unit", "depth"],
              closed [
                ("id", str),
                ("unit", str),
                ("depth", ref "common.json#/$defs/nat"),
                ("ast", ref "common.json#/$defs/generated_formula")]])]),
        ("content_ids", n [
          arr,
          .items (n [
              obj,
              .required ["unit", "content_id"],
              closed [("unit", str), ("content_id", ref "common.json#/$defs/hex64_or_empty")]])]),
        ("envelope", ref "#/$defs/envelope"),
        ("warnings", n [arr, .items (n [str, .pattern (Re.prefixes ["unreviewed act "])])])]]

def certificate : Shape :=
  c "Reports.Run.runCertificate: the certificate's verdict with both bindings." [
    obj,
    .required ["id", "status", "valid", "environment_reports_id", "envelope", "bindings"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("valid", .type ["boolean"]),
      ("environment_reports_id", ref "common.json#/$defs/hex64_or_empty"),
      ("envelope", ref "#/$defs/envelope"),
      ("bindings", n [
        obj,
        .required ["inner", "envelope"],
        closed [("inner", .type ["boolean"]), ("envelope", .type ["boolean"])]])]]

def countermodel : Shape :=
  c "Reports.Run.countermodelAnswer: whether the model refutes, and each generated predicate's table." [
    obj,
    .required ["id", "status", "refutes", "source_model"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("refutes", .type ["boolean"]),
      ("source_model", n [
        arr,
        .items (n [
            obj,
            .required ["name", "key", "holds_of"],
            closed [("name", str), ("key", ref "#/$defs/key"), ("holds_of", ref "common.json#/$defs/strings")]])])]]

def envelope_binding : Shape :=
  n [obj, .required ["envelope"], closed [("envelope", .type ["boolean"])]]

def «scoped» : Shape :=
  c "Reports.Run.runCaseReported reports-scoped: one verdict per scoped check." [
    obj,
    .required ["id", "status", "scoped", "envelope", "bindings"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("scoped", n [arr, .items (ref "#/$defs/verdict")]),
      ("envelope", ref "#/$defs/envelope"),
      ("bindings", ref "#/$defs/envelope_binding")]]

def status : Shape :=
  c
    "Reports.Run.runStatus: every unit's status with its nested results, the scoped verdicts and the document's status."
    [
      obj,
      .required ["id", "status", "units", "scoped", "document_status", "envelope", "bindings"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("units", n [
          arr,
          .items (n [
              obj,
              .required ["id", "status", "nested"],
              closed [
                ("id", str),
                ("status", ref "#/$defs/status_word"),
                ("nested", n [
                  arr,
                  .items (.anyOf [
                      n [
                        obj,
                        .required ["item", "path", "name", "status"],
                        closed [
                          ("item", constS "assessment"),
                          ("path", n [str, .pattern (Re.optional (.seq (.lit "1") (.star (.lit ".1"))))]),
                          ("name", str),
                          ("status", constS "OPEN")]],
                      n [
                        obj,
                        .required ["item", "path", "act", "status"],
                        closed [
                          ("item", constS "act"),
                          ("path", n [
                            str,
                            .pattern (Re.optional (.seq (.cls [('1', '1'), ('2', '2')]) (.star (.seq (.lit ".") (.cls [('1', '1'), ('2', '2')])))))]),
                          ("act", str),
                          ("status", constS "LABELLED")]],
                      n [
                        obj,
                        .required ["item", "path", "reason", "status"],
                        closed [
                          ("item", constS "unformalised"),
                          ("path", n [
                            str,
                            .pattern (Re.optional (.seq (.cls [('1', '1'), ('2', '2')]) (.star (.seq (.lit ".") (.cls [('1', '1'), ('2', '2')])))))]),
                          ("reason", str),
                          ("status", constS "UNFORMALISED")]]])])]])]),
        ("scoped", n [arr, .items (ref "#/$defs/verdict")]),
        ("document_status", ref "#/$defs/status_word"),
        ("envelope", ref "#/$defs/envelope"),
        ("bindings", ref "#/$defs/envelope_binding")]]

def «row» : Shape :=
  .select [
    (ref "#/$defs/reports_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      .select [
        (ref "#/$defs/kind/admission", ref "#/$defs/admission"),
        (ref "#/$defs/kind/reports-elaborate", ref "#/$defs/elaborate"),
        (ref "#/$defs/kind/reports-certificate", ref "#/$defs/certificate"),
        (ref "#/$defs/kind/reports-countermodel", ref "#/$defs/countermodel"),
        (ref "#/$defs/kind/reports-scoped", ref "#/$defs/scoped"),
        (ref "#/$defs/kind/reports-status", ref "#/$defs/status")]]),
    ((.bool true), ref "route.json#/row")]

def file : File where
  name := "reports.json"
  comment := some "Mode reports: Reports.Run.runCaseReported (lean/VE/Attribution/Run.lean, formerly ve_reports_route). A case on the reports path (usesReportsPath) is answered by the reports runner; every other case is delegated unchanged to the route mode's runner."
  top := [("row", «row»)]
  defs := [
    ("reports_path", .schema reports_path),
    ("kind", kind),
    ("report_kind", .schema report_kind),
    ("envelope", .schema envelope),
    ("key", .schema key),
    ("status_word", .schema status_word),
    ("verdict", .schema verdict),
    ("admission", .schema admission),
    ("elaborate", .schema elaborate),
    ("certificate", .schema certificate),
    ("countermodel", .schema countermodel),
    ("envelope_binding", .schema envelope_binding),
    ("scoped", .schema «scoped»),
    ("status", .schema status)]

end ResponseShape.Schemas.Reports
