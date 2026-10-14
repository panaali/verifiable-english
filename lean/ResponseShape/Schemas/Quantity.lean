import ResponseShape

/-! The source of `ve/backends/lean_service_schema/quantity.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Quantity
open Lean ResponseShape

def kind : Def :=
  .group none [
    ("admission", kindIs "admission"),
    ("countermodel", kindIs "countermodel"),
    ("certificate", kindIs "certificate"),
    ("count", kindIs "count"),
    ("day", kindIs "day"),
    ("civil", kindIs "civil"),
    ("lower", kindIs "lower"),
    ("render", kindIs "render"),
    ("document", kindIs "document")]

def error : Shape :=
  c
    "Time.Wire.runCaseReported: the request's id (null if absent) and the message, with valid: false exactly for a certificate case."
    [
      obj,
      .required ["id", "status", "error"],
      closed [
        ("id", .echo "/id"),
        ("status", constS "error"),
        ("error", ref "common.json#/$defs/text"),
        ("valid", .const (.bool false))],
      .ite (.onCase (ref "#/$defs/kind/certificate")) (.required ["valid"]) (.not (.required ["valid"]))]

def q_term : Shape :=
  c "Time.Wire.encTerm: an object constant is [const, name], a quantity constant [const, tag, name]." [
    .anyOf [
      .tagged [
        ("var", [ref "common.json#/$defs/nat"]),
        ("const", [str]),
        ("num", [str, ref "common.json#/$defs/integer_text"]),
        ("add", [str, ref "#/$defs/q_term", ref "#/$defs/q_term"]),
        ("scale", [str, ref "common.json#/$defs/integer_text", ref "#/$defs/q_term"])],
      .tagged [("const", [str, str])]]]

def q_formula : Shape :=
  c "Time.Wire.encQ: the order formulas with quantity terms and the date and day predicates." [
    .tagged [
      ("top", []),
      ("bottom", []),
      ("unary", [str, ref "#/$defs/q_term"]),
      ("binary", [str, ref "#/$defs/q_term", ref "#/$defs/q_term"]),
      ("eq", [ref "#/$defs/q_term", ref "#/$defs/q_term"]),
      ("lt", [ref "#/$defs/q_term", ref "#/$defs/q_term"]),
      ("le", [ref "#/$defs/q_term", ref "#/$defs/q_term"]),
      ("not", [ref "#/$defs/q_formula"]),
      ("and", [ref "#/$defs/q_formula", ref "#/$defs/q_formula"]),
      ("or", [ref "#/$defs/q_formula", ref "#/$defs/q_formula"]),
      ("implies", [ref "#/$defs/q_formula", ref "#/$defs/q_formula"]),
      ("forall", [str, ref "#/$defs/q_formula"]),
      ("exists", [str, ref "#/$defs/q_formula"]),
      ("date_on", [ref "#/$defs/q_term", ref "#/$defs/q_term"]),
      ("date_before", [ref "#/$defs/q_term", ref "#/$defs/q_term"]),
      ("date_after", [ref "#/$defs/q_term", ref "#/$defs/q_term"]),
      ("date_no_later", [ref "#/$defs/q_term", ref "#/$defs/q_term"]),
      ("within_days", [ref "#/$defs/q_term", ref "#/$defs/q_term", ref "common.json#/$defs/integer_text"]),
      ("shift_days", [ref "#/$defs/q_term", ref "#/$defs/q_term", ref "common.json#/$defs/integer_text"]),
      ("elapsed_days", [ref "#/$defs/q_term", ref "#/$defs/q_term", ref "#/$defs/q_term"])]]

def core_term : Shape :=
  c "Time.Wire.encCoreTerm: Order.Wire.decodeTerm's grammar at any depth." [
    .tagged [
      ("var", [ref "common.json#/$defs/nat"]),
      ("const", [str]),
      ("num", [ref "common.json#/$defs/integer_text"]),
      ("add", [ref "#/$defs/core_term", ref "#/$defs/core_term"]),
      ("scale", [ref "common.json#/$defs/integer_text", ref "#/$defs/core_term"])]]

def core_formula : Shape :=
  c
    "Time.Wire.encCore of an erased or generated formula: Order.Wire.decodeFormula's grammar at any depth (a count expansion is generated)."
    [
      .tagged [
        ("top", []),
        ("bottom", []),
        ("unary", [str, ref "#/$defs/core_term"]),
        ("binary", [str, ref "#/$defs/core_term", ref "#/$defs/core_term"]),
        ("eq", [ref "#/$defs/core_term", ref "#/$defs/core_term"]),
        ("lt", [ref "#/$defs/core_term", ref "#/$defs/core_term"]),
        ("le", [ref "#/$defs/core_term", ref "#/$defs/core_term"]),
        ("not", [ref "#/$defs/core_formula"]),
        ("and", [ref "#/$defs/core_formula", ref "#/$defs/core_formula"]),
        ("or", [ref "#/$defs/core_formula", ref "#/$defs/core_formula"]),
        ("implies", [ref "#/$defs/core_formula", ref "#/$defs/core_formula"]),
        ("forall", [str, ref "#/$defs/core_formula"]),
        ("exists", [str, ref "#/$defs/core_formula"])]]

def admission : Shape :=
  c
    "Time.Wire.runCase admission: the quantity's encodings and identities, and its value and evaluation count exactly when the case supplies a model."
    [
      obj,
      .required ["id", "status", "assurance", "Q", "core", "meaning_id", "core_meaning_id", "environment_id", "target_environment_id"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("assurance", constS "lean-admitted"),
        ("Q", ref "#/$defs/q_formula"),
        ("core", ref "#/$defs/core_formula"),
        ("meaning_id", ref "common.json#/$defs/hex64"),
        ("core_meaning_id", ref "common.json#/$defs/hex64"),
        ("environment_id", ref "common.json#/$defs/hex64"),
        ("target_environment_id", ref "common.json#/$defs/hex64"),
        ("value", .type ["boolean"]),
        ("evaluations", ref "common.json#/$defs/nat")],
      .ite (.onCase (.required ["model"])) (.required ["value", "evaluations"]) (.not (.anyOf [
            .required ["value"],
            .required ["evaluations"]]))]

def identities : Def :=
  .group (some "The premises' and conclusion's identities, quantity and core, one per requested premise.") [
    ("premise_meaning_ids", n [arr, .items (ref "common.json#/$defs/hex64"), .length "/premises"]),
    ("core_premise_meaning_ids", n [arr, .items (ref "common.json#/$defs/hex64"), .length "/premises"])]

def countermodel : Shape :=
  c "Time.Wire.runCase countermodel." [
    obj,
    .required ["id", "status", "refutes", "premise_meaning_ids", "conclusion_meaning_id", "core_premise_meaning_ids", "core_conclusion_meaning_id", "environment_id", "target_environment_id"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("refutes", .type ["boolean"]),
      ("premise_meaning_ids", ref "#/$defs/identities/premise_meaning_ids"),
      ("conclusion_meaning_id", ref "common.json#/$defs/hex64"),
      ("core_premise_meaning_ids", ref "#/$defs/identities/core_premise_meaning_ids"),
      ("core_conclusion_meaning_id", ref "common.json#/$defs/hex64"),
      ("environment_id", ref "common.json#/$defs/hex64"),
      ("target_environment_id", ref "common.json#/$defs/hex64")]]

def certificate : Shape :=
  c "Time.Wire.runCase certificate." [
    obj,
    .required ["id", "status", "valid", "premise_meaning_ids", "conclusion_meaning_id", "core_premise_meaning_ids", "core_conclusion_meaning_id", "environment_id", "target_environment_id"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("valid", .type ["boolean"]),
      ("premise_meaning_ids", ref "#/$defs/identities/premise_meaning_ids"),
      ("conclusion_meaning_id", ref "common.json#/$defs/hex64"),
      ("core_premise_meaning_ids", ref "#/$defs/identities/core_premise_meaning_ids"),
      ("core_conclusion_meaning_id", ref "common.json#/$defs/hex64"),
      ("environment_id", ref "common.json#/$defs/hex64"),
      ("target_environment_id", ref "common.json#/$defs/hex64")]]

def count : Shape :=
  c "Time.Wire.runCount: the counting quantifier's expansion." [
    obj,
    .required ["id", "status", "expansion"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("expansion", ref "#/$defs/core_formula")]]

def day : Shape :=
  n [
    obj,
    .required ["id", "status", "day"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("day", ref "common.json#/$defs/nat")]]

def civil : Shape :=
  n [
    obj,
    .required ["id", "status", "date"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("date", n [
        str,
        .pattern (.seq (.rep (.cls [('0', '9')]) 4 4) (.seq (.lit "-") (.seq (.rep (.cls [('0', '9')]) 2 2) (.seq (.lit "-") (.rep (.cls [('0', '9')]) 2 2)))))])]]

def lower : Shape :=
  n [
    obj,
    .required ["id", "status", "coordinate"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("coordinate", ref "common.json#/$defs/integer_text")]]

def render : Shape :=
  n [
    obj,
    .required ["id", "status", "amount"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("amount", n [
        str,
        .pattern (.seq (Re.optional (.lit "-")) (.seq (.cls [('0', '9')]) (.seq (.star (.cls [('0', '9')])) (Re.optional (.seq (.lit ".") (.seq (.cls [('0', '9')]) (.star (.cls [('0', '9')]))))))))])]]

def claim : Shape :=
  c
    "Time.Document.claimJson: a node of the request's graph with its quantity and meaning identity; the default label is omitted."
    [
      obj,
      .required ["name", "quantity", "meaning_id"],
      closed [
        ("name", str),
        ("quantity", n [
          obj,
          .required ["format", "formula", "traces"],
          closed [
            ("format", constS "ve-quantity@1"),
            ("formula", ref "#/$defs/q_formula"),
            ("traces", n [arr, .maxItems 0])]]),
        ("meaning_id", ref "common.json#/$defs/hex64"),
        ("label", n [str, .not (constS "asserted")])]]

def document : Shape :=
  c "Time.Document.runDocument: the admitted quantity document's report and identities." [
    obj,
    .references "/report/assumptions" "name" "/document/graph/nodes/*/name",
    .required ["id", "status", "admitted", "assurance", "report", "report_id", "environment_id", "kinds"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("admitted", .const (.bool true)),
      ("assurance", constS "lean-admitted"),
      ("report", n [
        obj,
        .required ["root", "assumptions"],
        closed [
          ("root", n [ref "#/$defs/claim", props [("name", .equals "/document/graph/root")]]),
          ("assumptions", n [arr, .items (ref "#/$defs/claim")])]]),
      ("report_id", ref "common.json#/$defs/hex64"),
      ("environment_id", ref "common.json#/$defs/hex64"),
      ("kinds", n [arr, .items (ref "common.json#/$defs/kind"), .equals "/document/units/*/kind"])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "#/$defs/error",
    .select [
      (ref "common.json#/$defs/no_kind", ref "#/$defs/admission"),
      (ref "#/$defs/kind/admission", ref "#/$defs/admission"),
      (ref "#/$defs/kind/countermodel", ref "#/$defs/countermodel"),
      (ref "#/$defs/kind/certificate", ref "#/$defs/certificate"),
      (ref "#/$defs/kind/count", ref "#/$defs/count"),
      (ref "#/$defs/kind/day", ref "#/$defs/day"),
      (ref "#/$defs/kind/civil", ref "#/$defs/civil"),
      (ref "#/$defs/kind/lower", ref "#/$defs/lower"),
      (ref "#/$defs/kind/render", ref "#/$defs/render"),
      (ref "#/$defs/kind/document", ref "#/$defs/document")]]

def file : File where
  name := "quantity.json"
  comment := some "Mode quantity: Time.Wire.runCaseReported with Time.Document.extension (formerly ve_quantity). No delegation: the case kind (default admission) selects the answer."
  top := [("row", «row»)]
  defs := [
    ("kind", kind),
    ("error", .schema error),
    ("q_term", .schema q_term),
    ("q_formula", .schema q_formula),
    ("core_term", .schema core_term),
    ("core_formula", .schema core_formula),
    ("admission", .schema admission),
    ("identities", identities),
    ("countermodel", .schema countermodel),
    ("certificate", .schema certificate),
    ("count", .schema count),
    ("day", .schema day),
    ("civil", .schema civil),
    ("lower", .schema lower),
    ("render", .schema render),
    ("claim", .schema claim),
    ("document", .schema document)]

end ResponseShape.Schemas.Quantity
