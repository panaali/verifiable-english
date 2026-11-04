import VE.Service.Protocol
import ResponseShape
import ResponseShape.CaseDeciders

/-! The source of `ve/backends/lean_service_schema/reports.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Reports
open Lean ResponseShape

def reports_path : Shape :=
  decidedCase .reportsPath <|
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
    ("reports-content", kindIs "reports-content"),
    ("reports-certificate", kindIs "reports-certificate"),
    ("reports-countermodel", kindIs "reports-countermodel"),
    ("reports-scoped", kindIs "reports-scoped"),
    ("reports-status", kindIs "reports-status"),
    ("reports-wants", kindIs "reports-wants")]

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

def counts : Shape := n [obj, .object [] (some (ref "common.json#/$defs/nat"))]

def object_map : Shape := n [obj, .object [] (some (n [obj,
  .object [] (some (.type ["null", "boolean", "integer", "number", "string", "array", "object"]))]))]

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
            "not replayed",
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
      .required ["id", "status", "environment_reports_id", "environment_reports", "keys", "premises", "open_terms", "bridge_formulas", "content_ids", "meaning_ids", "envelope", "warnings"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("environment_reports_id", ref "common.json#/$defs/hex64_or_empty"),
        ("environment_reports", copied
          "Attribution.Wire.environmentReportsJson copies the decoded request environment and extends its vocabulary predicates; the Python caller compares the whole regenerated identity."
          <| n [
            obj,
            .required ["language", "profiles", "spec_revision", "vocabulary"],
            .object [
              ("language", str),
              ("profiles", ref "common.json#/$defs/strings"),
              ("spec_revision", str),
              ("vocabulary", n [
                obj,
                .required ["sorts", "predicates", "constants"],
                .object [
                  ("sorts", object_map),
                  ("predicates", object_map),
                  ("constants", object_map)]
                  (some (.type ["null", "boolean", "integer", "number", "string", "array", "object"]))])]
              (some (.type ["null", "boolean", "integer", "number", "string", "array", "object"]))]),
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
        ("meaning_ids", n [arr, .items (n [obj, .required ["unit", "meaning_id"],
          closed [("unit", str), ("meaning_id", ref "common.json#/$defs/hex64_or_empty")]])]),
        ("envelope", ref "#/$defs/envelope"),
        ("warnings", n [arr, .items (n [str, .pattern (Re.prefixes ["unreviewed act "])])])]]

def content : Shape := n [obj, .required ["id", "status", "meaning_id"],
  closed [("id", ref "common.json#/$defs/id_ok"), ("status", constS "ok"),
    ("meaning_id", ref "common.json#/$defs/hex64_or_empty")]]

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

def boundVerdicts : Shape := n [
  arr,
  .zipOrEmpty "/document/scoped" (n [ref "#/$defs/verdict",
    props [("id", n [str, .equals "/id"])]])]

def nested : Shape := .anyOf [
  n [obj, .required ["item", "path", "name", "status"],
    closed [("item", constS "assessment"),
      ("path", n [str, .pattern (Re.optional (.seq (.lit "1") (.star (.lit ".1"))))]),
      ("name", str), ("status", constS "OPEN")]],
  n [obj, .required ["item", "path", "act", "status"],
    closed [("item", constS "act"),
      ("path", n [str, .pattern (Re.optional (.seq (.cls [('1', '1'), ('2', '2')])
        (.star (.seq (.lit ".") (.cls [('1', '1'), ('2', '2')])))))]),
      ("act", str), ("status", constS "LABELLED")]],
  n [obj, .required ["item", "path", "reason", "status"],
    closed [("item", constS "unformalised"),
      ("path", n [str, .pattern (Re.optional (.seq (.cls [('1', '1'), ('2', '2')])
        (.star (.seq (.lit ".") (.cls [('1', '1'), ('2', '2')])))))]),
      ("reason", str), ("status", constS "UNFORMALISED")]]]

def status : Shape :=
  c
    "Reports.Run.runStatus: every unit's status with its nested results, the scoped verdicts and the document's status."
    [
      obj,
      .required ["id", "status", "units", "scoped", "document_status", "status_text", "residual_lines", "envelope", "bindings"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("units", n [
          arr,
          .zip "/document/units" (n [obj, .required ["id", "status", "nested"], closed [
            ("id", n [str, .equals "/id"]), ("status", ref "#/$defs/status_word"),
            ("nested", n [arr, .items (ref "#/$defs/nested")])]])]),
        ("scoped", boundVerdicts),
        ("document_status", ref "#/$defs/status_word"),
        ("status_text", n [arr, .items str]),
        ("residual_lines", n [obj,
          .required ["open_terms", "reports", "assessments", "literal_quotations", "scoped_checks", "unreviewed_acts", "unformalised_kinds"],
          closed [("open_terms", ref "common.json#/$defs/strings"),
            ("reports", ref "#/$defs/counts"), ("assessments", ref "#/$defs/counts"),
            ("literal_quotations", n [arr, .items (n [obj, .required ["unit", "path"],
              closed [("unit", str), ("path", str)]])]),
            ("scoped_checks", boundVerdicts),
            ("unreviewed_acts", ref "#/$defs/counts"),
            ("unformalised_kinds", ref "#/$defs/counts")]]),
        ("envelope", ref "#/$defs/envelope"),
        ("bindings", ref "#/$defs/envelope_binding")]]

def wants : Shape :=
  c "Reports.Run.runWants: each phrase sent with its infinitive under the wants test (null where refused), each infinitive sent with its finite form, in order." [
    obj,
    .required ["id", "status", "phrases", "infinitives"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("phrases", n [arr, .zip "/phrases" (n [obj, .required ["phrase", "infinitive"],
        closed [("phrase", n [str, .equals ""]), ("infinitive", .type ["string", "null"])]])]),
      ("infinitives", n [arr, .zip "/infinitives" (n [obj, .required ["infinitive", "finite"],
        closed [("infinitive", n [str, .equals ""]), ("finite", str)]])])]]

def «row» : Shape :=
  .select [
    (ref "#/$defs/reports_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      .select [
        (ref "#/$defs/kind/admission", ref "#/$defs/admission"),
        (ref "#/$defs/kind/reports-elaborate", ref "#/$defs/elaborate"),
        (ref "#/$defs/kind/reports-content", ref "#/$defs/content"),
        (ref "#/$defs/kind/reports-certificate", ref "#/$defs/certificate"),
        (ref "#/$defs/kind/reports-countermodel", ref "#/$defs/countermodel"),
        (ref "#/$defs/kind/reports-scoped", ref "#/$defs/scoped"),
        (ref "#/$defs/kind/reports-status", ref "#/$defs/status"),
        (ref "#/$defs/kind/reports-wants", ref "#/$defs/wants")]]),
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
    ("nested", .schema nested),
    ("counts", .schema counts),
    ("verdict", .schema verdict),
    ("admission", .schema admission),
    ("elaborate", .schema elaborate),
    ("content", .schema content),
    ("certificate", .schema certificate),
    ("countermodel", .schema countermodel),
    ("envelope_binding", .schema envelope_binding),
    ("scoped", .schema «scoped»),
    ("status", .schema status),
    ("wants", .schema wants)]

/-! The `reports-wants` row and the mode's kind table, row and definitions as rendered: a dropped
type, member, requirement, binding, kind or definition changes them. -/
#guard (match kind with | .group _ entries => entries.map (·.1) | .schema _ => []) == ["admission",
  "reports-elaborate", "reports-content", "reports-certificate", "reports-countermodel", "reports-scoped",
  "reports-status", "reports-wants"]
#guard (ResponseShape.render "reports.json" 64 «row»).toOption.map Json.compress == some r##"{"x-select":[{"then":{"anyOf":[{"$ref":"common.json#/$defs/case_error"},{"$ref":"common.json#/$defs/route_path_error"},{"x-select":[{"then":{"$ref":"#/$defs/admission"},"when":{"$ref":"#/$defs/kind/admission"}},{"then":{"$ref":"#/$defs/elaborate"},"when":{"$ref":"#/$defs/kind/reports-elaborate"}},{"then":{"$ref":"#/$defs/content"},"when":{"$ref":"#/$defs/kind/reports-content"}},{"then":{"$ref":"#/$defs/certificate"},"when":{"$ref":"#/$defs/kind/reports-certificate"}},{"then":{"$ref":"#/$defs/countermodel"},"when":{"$ref":"#/$defs/kind/reports-countermodel"}},{"then":{"$ref":"#/$defs/scoped"},"when":{"$ref":"#/$defs/kind/reports-scoped"}},{"then":{"$ref":"#/$defs/status"},"when":{"$ref":"#/$defs/kind/reports-status"}},{"then":{"$ref":"#/$defs/wants"},"when":{"$ref":"#/$defs/kind/reports-wants"}}]}]},"when":{"$ref":"#/$defs/reports_path"}},{"then":{"$ref":"route.json#/row"},"when":true}]}"##
#guard file.top.map (·.1) == ["row"] && file.defs.map (·.1) == ["reports_path", "kind", "report_kind",
  "envelope", "key", "status_word", "nested", "counts", "verdict", "admission", "elaborate", "content",
  "certificate", "countermodel", "envelope_binding", "scoped", "status", "wants"]
#guard (ResponseShape.render "reports.json" 64 wants).toOption.map Json.compress == some r##"{"$comment":"Reports.Run.runWants: each phrase sent with its infinitive under the wants test (null where refused), each infinitive sent with its finite form, in order.","additionalProperties":false,"properties":{"id":{"$ref":"common.json#/$defs/id_ok"},"infinitives":{"type":"array","x-zip":{"items":{"additionalProperties":false,"properties":{"finite":{"type":"string"},"infinitive":{"type":"string","x-equals":""}},"required":["infinitive","finite"],"type":"object"},"of":"/infinitives"}},"phrases":{"type":"array","x-zip":{"items":{"additionalProperties":false,"properties":{"infinitive":{"type":["string","null"]},"phrase":{"type":"string","x-equals":""}},"required":["phrase","infinitive"],"type":"object"},"of":"/phrases"}},"status":{"const":"ok"}},"required":["id","status","phrases","infinitives"],"type":"object"}"##

end ResponseShape.Schemas.Reports
