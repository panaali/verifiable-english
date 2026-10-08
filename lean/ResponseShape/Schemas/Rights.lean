import VE.Service.Protocol
import ResponseShape
import ResponseShape.CaseDeciders

/-! The source of `ve/backends/lean_service_schema/rights.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Rights
open Lean ResponseShape

def rights_path : Shape :=
  decidedCase .rightsPath <|
  c
    "Rights.Run.usesRightsPath: the rights@0 profile, the vocabulary's rights block, a rights-* kind, or a rights unit (right, right_lines, limitation or bar) in a document array or in a document's units' content."
    [
      obj,
      .anyOf [
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["profiles"],
              props [("profiles", n [arr, .contains (constS "rights@0")])]])]],
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["vocabulary"],
              props [("vocabulary", n [obj, .required ["rights"]])]])]],
        n [.required ["kind"], props [("kind", n [str, .pattern (Re.prefixes ["rights-"])])]],
        n [.required ["document"], props [("document", n [arr, .contains (ref "#/$defs/rights_unit")])]],
        n [
          .required ["document"],
          props [
            ("document", n [
              obj,
              .required ["units"],
              props [
                ("units", n [
                  arr,
                  .contains (n [obj, .required ["content"], props [("content", ref "#/$defs/rights_unit")]])])]])]]]]

def rights_unit : Shape :=
  n [obj, .anyOf [.required ["right"], .required ["right_lines"], .required ["limitation"], .required ["bar"]]]

def kind : Def :=
  .group none [
    ("admission", kindIs "admission"),
    ("rights-elaborate", kindIs "rights-elaborate"),
    ("rights-projections", kindIs "rights-projections"),
    ("rights-scope", kindIs "rights-scope"),
    ("rights-certificate", kindIs "rights-certificate"),
    ("rights-bar", kindIs "rights-bar"),
    ("rights-conflict", kindIs "rights-conflict")]

def conditional_labels : Shape :=
  c "Open coherence premises and limitation premises (Rights.Wire.openCoherence, limPremisesLabelled)." [
    arr,
    .items (n [str, .pattern (Re.prefixes ["soft:coherence:", "rights:limitation:"])])]

def admission : Shape :=
  c
    "Rights.Run.encodeAdmitted: W2's admission answer; kinds are the units' kinds as written (rights units included), and the open premises the report assumes."
    [
      obj,
      .required ["id", "status", "admitted", "report", "report_id", "kinds", "conditional_on"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("admitted", .const (.bool true)),
        ("report", ref "common.json#/$defs/bound_report"),
        ("report_id", ref "common.json#/$defs/hex64"),
        ("kinds", n [arr, .equals "/document/units/*/kind"]),
        ("conditional_on", ref "#/$defs/conditional_labels")]]

def node : Shape :=
  c "Rights.Run.nodeJson." [
    obj,
    .required ["name", "predicate", "sign", "mode", "guard", "unless", "over", "hard"],
    closed [
      ("name", str),
      ("predicate", str),
      ("sign", .type ["boolean"]),
      ("mode", enumS ["strict", "default"]),
      ("guard", ref "common.json#/$defs/generated_formula"),
      ("unless", ref "common.json#/$defs/generated_formulas"),
      ("over", ref "common.json#/$defs/strings"),
      ("hard", .type ["boolean"])]]

def «instance» : Shape :=
  enumS ["claim", "liberty", "immunity", "powerLiberty", "powerRecognition"]

def narrowings : Shape :=
  c
    "Rights.Run.narrowingsJson: per line, whether a limitation scopes it and each narrowing mechanism with its licence (null when none)."
    [
      arr,
      .items (n [
          obj,
          .required ["right", "rule", "in_scope", "mechanisms"],
          closed [
            ("right", str),
            ("rule", str),
            ("in_scope", .type ["boolean"]),
            ("mechanisms", n [
              arr,
              .items (n [
                  obj,
                  .required ["mechanism", "target", "conclusion", "licence"],
                  closed [
                    ("mechanism", ref "common.json#/$defs/text"),
                    ("target", ref "common.json#/$defs/text"),
                    ("conclusion", ref "common.json#/$defs/generated_formula"),
                    ("licence", .anyOf [.const .null, ref "common.json#/$defs/text"])]])])]])]

def findings : Shape :=
  n [arr, .items (ref "common.json#/$defs/text")]

def elaborate : Shape :=
  c
    "Rights.Run.regenerated: E'' (primeJsonR), the generated predicates, the lines, the limitation premises, the bar nodes, the rights Background, the narrowings, the distinction rows and findings, then every SoftNorms.Wire.regeneratedCore field over the correlated document but its environment_prime."
    [
      obj,
      .required ["id", "status", "environment_prime", "generated", "wordings", "unit_open", "lines", "limitations", "bars", "rights_background", "narrowings", "distinction", "findings", "decisions", "derived", "order", "background", "premises", "colliding_pairs", "conflict_targets", "conditional_on", "fragment", "warnings"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("environment_prime", ref "common.json#/$defs/environment"),
        ("wordings", ref "common.json#/$defs/string_map"),
        ("unit_open", n [arr, .items (.type ["boolean"]), .length "/document"]),
        ("generated", n [
          arr,
          .items (.anyOf [
              n [
                obj,
                .required ["name", "kind", "limitation", "act"],
                closed [
                  ("name", n [str, .pattern (Re.prefixes ["rights__lim__"])]),
                  ("kind", constS "lim"),
                  ("limitation", str),
                  ("act", str)]],
              n [
                obj,
                .required ["name", "kind", "limitation", "act", "condition"],
                closed [
                  ("name", n [str, .pattern (Re.prefixes ["rights__cond__"])]),
                  ("kind", constS "cond"),
                  ("limitation", str),
                  ("act", str),
                  ("condition", str)]],
              n [
                obj,
                .required ["name", "kind", "predicate"],
                closed [
                  ("name", n [str, .pattern (Re.prefixes ["rights__bar__"])]),
                  ("kind", constS "aimed"),
                  ("predicate", str)]]])]),
        ("lines", n [
          arr,
          .items (n [
              obj,
              .required ["right", "kind", "instance", "rule", "predicate", "holder_slot", "node"],
              closed [
                ("right", str),
                ("kind", enumS ["claim", "liberty", "immunity", "power"]),
                ("instance", ref "#/$defs/instance"),
                ("rule", str),
                ("predicate", str),
                ("holder_slot", ref "common.json#/$defs/nat"),
                ("node", ref "#/$defs/node"),
                ("bearer", str),
                ("source_line", str)],
              .ite (.required ["bearer"]) (.required ["source_line"]) (.not (.required ["source_line"]))])]),
        ("limitations", n [
          arr,
          .items (n [
              ref "common.json#/$defs/labelled",
              props [("label", .pattern (Re.prefixes ["rights:limitation:"]))]])]),
        ("bars", n [arr, .items (ref "#/$defs/node")]),
        ("rights_background", n [
          arr,
          .items (n [
              obj,
              .required ["generator", "ast", "label"],
              closed [
                ("generator", constS "rights"),
                ("ast", ref "common.json#/$defs/generated_formula"),
                ("label", n [str, .pattern (Re.prefixes ["rights:limitation:"])])]])]),
        ("narrowings", ref "#/$defs/narrowings"),
        ("distinction", n [
          arr,
          .items (n [
              obj,
              .required ["predicate", "independent", "hits"],
              closed [
                ("predicate", str),
                ("independent", .type ["boolean"]),
                ("hits", n [
                  arr,
                  .items (n [
                      obj,
                      .required ["rule", "right", "protected", "cited"],
                      closed [("rule", str), ("right", str), ("protected", str), ("cited", .type ["boolean"])]])])]])]),
        ("findings", ref "#/$defs/findings"),
        ("decisions", ref "soft-norms.json#/$defs/elaborated/decisions"),
        ("derived", ref "soft-norms.json#/$defs/elaborated/derived"),
        ("order", ref "common.json#/$defs/strings"),
        ("background", ref "soft-norms.json#/$defs/background"),
        ("premises", ref "common.json#/$defs/layer_premises"),
        ("colliding_pairs", ref "soft-norms.json#/$defs/elaborated/colliding_pairs"),
        ("conflict_targets", ref "common.json#/$defs/conflict_targets"),
        ("conditional_on", ref "soft-norms.json#/$defs/coherence_labels"),
        ("fragment", .type ["boolean"]),
        ("warnings", ref "common.json#/$defs/nonempty_strings")]]

def projections : Shape :=
  c "Rights.Run.projectionsResult: the selected line instances by holder and by bearer (entryJson)." [
    obj,
    .required ["id", "status", "rights_of", "duties_of"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("rights_of", ref "#/$defs/entries"),
      ("duties_of", ref "#/$defs/entries")]]

def entries : Shape :=
  n [
    arr,
    .items (n [
        obj,
        .required ["right", "rule", "instance", "tuple"],
        closed [
          ("right", str),
          ("rule", str),
          ("instance", ref "#/$defs/instance"),
          ("tuple", ref "common.json#/$defs/strings")]])]

def scope : Shape :=
  c
    "Rights.Run.runRightsKind rights-scope: the unlicensed-limitation findings, whether there are none, and the narrowings with certified licences."
    [
      obj,
      .required ["id", "status", "findings", "licensed", "narrowings"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("findings", ref "#/$defs/findings"),
        ("licensed", .type ["boolean"]),
        ("narrowings", ref "#/$defs/narrowings")],
      .ite (props [("findings", .maxItems 0)]) (props [("licensed", .const (.bool true))]) (props [
          ("licensed", .const (.bool false))])]

def certificate : Shape :=
  c "Rights.Run.runRightsKind rights-certificate." [
    obj,
    .required ["id", "status", "valid", "background", "layers", "conditional_on"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("valid", .type ["boolean"]),
      ("background", ref "common.json#/$defs/nat"),
      ("layers", ref "common.json#/$defs/nat"),
      ("conditional_on", ref "#/$defs/conditional_labels")]]

def bar : Shape :=
  c "Rights.Run.barResult: one row per barred predicate, under the rule reading or the query reading." [
    obj,
    .required ["id", "status", "bars"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("bars", n [
        arr,
        .items (.anyOf [
            n [
              obj,
              .required ["predicate", "aimed", "reading", "barred", "blocked_defaults", "composition_candidates", "composition_conflicts"],
              closed [
                ("predicate", str),
                ("aimed", n [str, .pattern (Re.prefixes ["rights__bar__"])]),
                ("reading", constS "rule"),
                ("barred", ref "common.json#/$defs/strings"),
                ("blocked_defaults", ref "common.json#/$defs/strings"),
                ("composition_candidates", ref "common.json#/$defs/strings"),
                ("composition_conflicts", n [arr, .maxItems 0])]],
            n [
              obj,
              .required ["predicate", "aimed", "reading", "target"],
              closed [
                ("predicate", str),
                ("aimed", n [str, .pattern (Re.prefixes ["rights__bar__"])]),
                ("reading", constS "query"),
                ("target", ref "common.json#/$defs/generated_formula"),
                ("entailed", .type ["boolean"])]]])])]]

def packages : Shape :=
  c "Rights.Run.runRightsKind rights-conflict over certificate packages: detail exactly beside UNKNOWN." [
    obj,
    .required ["id", "status", "verdict", "status_text", "targets", "conditional_on"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("verdict", enumS ["CONFLICT-FREE", "UNKNOWN"]),
      ("status_text", ref "common.json#/$defs/text"),
      ("targets", ref "common.json#/$defs/strings"),
      ("conditional_on", ref "#/$defs/conditional_labels"),
      ("detail", ref "common.json#/$defs/text")],
    .ite (props [("verdict", constS "UNKNOWN")]) (.required ["detail"]) (.not (.required ["detail"]))]

def «row» : Shape :=
  .select [
    (ref "#/$defs/rights_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      .select [
        (ref "#/$defs/kind/admission", ref "#/$defs/admission"),
        (ref "#/$defs/kind/rights-elaborate", ref "#/$defs/elaborate"),
        (ref "#/$defs/kind/rights-projections", ref "#/$defs/projections"),
        (ref "#/$defs/kind/rights-scope", ref "#/$defs/scope"),
        (ref "#/$defs/kind/rights-certificate", ref "#/$defs/certificate"),
        (ref "#/$defs/kind/rights-bar", ref "#/$defs/bar"),
        (.allOf [ref "#/$defs/kind/rights-conflict", .required ["witness"]], ref "soft-norms.json#/$defs/witness"),
        (ref "#/$defs/kind/rights-conflict", ref "#/$defs/packages")]]),
    ((.bool true), ref "soft-norms.json#/row")]

def file : File where
  name := "rights.json"
  comment := some "Mode rights: Rights.Run.runCaseReported (formerly ve_rights_route). A case on the rights path (Rights.Run.usesRightsPath) is answered by the rights runner (runRightsKind); every other case is delegated unchanged to the soft-norms mode's runner."
  top := [("row", «row»)]
  defs := [
    ("rights_path", .schema rights_path),
    ("rights_unit", .schema rights_unit),
    ("kind", kind),
    ("conditional_labels", .schema conditional_labels),
    ("admission", .schema admission),
    ("node", .schema node),
    ("instance", .schema «instance»),
    ("narrowings", .schema narrowings),
    ("findings", .schema findings),
    ("elaborate", .schema elaborate),
    ("projections", .schema projections),
    ("entries", .schema entries),
    ("scope", .schema scope),
    ("certificate", .schema certificate),
    ("bar", .schema bar),
    ("packages", .schema packages)]

end ResponseShape.Schemas.Rights
