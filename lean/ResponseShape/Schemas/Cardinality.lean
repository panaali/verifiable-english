import ResponseShape

/-! The source of `ve/backends/lean_service_schema/cardinality.json` (`file`; `tools/response_schemas.py` writes it):
the `cardinality` mode's row (`VE.Cardinality.Run.runCaseReported`, docs/spec/quantities.md 4.1–4.2). An answer
carries the cardinality and W6a identities under separate names, one statement per request premise
(`x-length`), and, for an admission, the region table, each constant of a request's finite sort
(`x-references`), and the regenerated erased problem with its W6a identities. -/
namespace ResponseShape.Schemas.Cardinality
open Lean ResponseShape

def kind : Def :=
  .group none [
    ("admission", kindIs "admission"),
    ("certificate", kindIs "certificate"),
    ("document", kindIs "document")]

def error : Shape :=
  c
    "Cardinality.Run.runCaseReported: the request's id (null if absent) and the message, with valid: false exactly for a certificate case."
    [
      obj,
      .required ["id", "status", "error"],
      closed [
        ("id", .echo "/id"),
        ("status", constS "error"),
        ("error", ref "common.json#/$defs/text"),
        ("valid", .const (.bool false))],
      .ite (.onCase (ref "#/$defs/kind/certificate")) (.required ["valid"]) (.not (.required ["valid"]))]

def body : Shape :=
  c "Cardinality.Wire.encBody: a Boolean combination of unary atoms on the counted object." [
    .tagged [
      ("is", [str]),
      ("any", []),
      ("not", [ref "#/$defs/body"]),
      ("and", [ref "#/$defs/body", ref "#/$defs/body"]),
      ("or", [ref "#/$defs/body", ref "#/$defs/body"])]]

def operand : Shape :=
  c "Cardinality.Wire.encOperand: a closed W6a term or a count." [
    .tagged [
      ("quantity", [ref "quantity.json#/$defs/q_term"]),
      ("count", [str, ref "#/$defs/body"])]]

def printed : Shape :=
  c "Cardinality.Wire.encPrinted: a decimal (Time.renderAmount)." [str,
    .pattern (.seq (Re.optional (.lit "-")) (.seq (.cls [('0', '9')]) (.seq (.star (.cls [('0', '9')]))
      (Re.optional (.seq (.lit ".") (.seq (.cls [('0', '9')]) (.star (.cls [('0', '9')]))))))))]

def rule : Shape := enumS ["ties_up", "half_even", "down", "up"]

def formula : Shape :=
  c "Cardinality.Wire.encode: the canonical ve-cardinality@1 formula (spec 4.1)." [
    .tagged [
      ("quantity", [ref "quantity.json#/$defs/q_formula"]),
      ("count", [str, n [arr, .items (n [arr, .minItems 2, .maxItems 2,
          .prefixItems [ref "common.json#/$defs/integer_text", ref "#/$defs/body"]])],
        enumS ["lt", "le", "eq"], ref "common.json#/$defs/integer_text"]),
      ("proportion", [str, ref "#/$defs/body", ref "#/$defs/body", enumS ["gt", "ge", "lt", "le", "eq"],
        ref "common.json#/$defs/integer_text", ref "common.json#/$defs/integer_text"]),
      ("rounds_to", [ref "#/$defs/rule", ref "#/$defs/operand", ref "#/$defs/operand", ref "#/$defs/printed"]),
      ("percent_of", [ref "#/$defs/operand", ref "#/$defs/operand", ref "#/$defs/printed"]),
      ("percent_rounds_to", [ref "#/$defs/rule", ref "#/$defs/operand", ref "#/$defs/operand",
        ref "#/$defs/printed"]),
      ("not", [ref "#/$defs/formula"]),
      ("and", [ref "#/$defs/formula", ref "#/$defs/formula"]),
      ("or", [ref "#/$defs/formula", ref "#/$defs/formula"]),
      ("implies", [ref "#/$defs/formula", ref "#/$defs/formula"])]]

def statement : Shape :=
  c "Cardinality.Run.statementJson: a statement's cardinality meaning id and canonical formula." [
    obj,
    .required ["meaning_id", "formula"],
    closed [("meaning_id", ref "common.json#/$defs/hex64"), ("formula", ref "#/$defs/formula")]]

def erased : Shape :=
  c "Cardinality.Run.erasedJson: a regenerated W6a formula with its annotated and core identities." [
    obj,
    .required ["Q", "core", "meaning_id", "core_meaning_id"],
    closed [
      ("Q", ref "quantity.json#/$defs/q_formula"),
      ("core", ref "quantity.json#/$defs/core_formula"),
      ("meaning_id", ref "common.json#/$defs/hex64"),
      ("core_meaning_id", ref "common.json#/$defs/hex64")]]

/-- The members every `ok` answer has. -/
def envIds : List (String × Shape) := [
  ("id", ref "common.json#/$defs/id_ok"),
  ("status", constS "ok"),
  ("environment_id", ref "common.json#/$defs/hex64"),
  ("w6_environment_id", ref "common.json#/$defs/hex64"),
  ("w6_target_environment_id", ref "common.json#/$defs/hex64")]

/-- The members of an admission or certificate answer. -/
def answer : List (String × Shape) := envIds ++ [
  ("premises", n [arr, .items (ref "#/$defs/statement"), .length "/premises"]),
  ("conclusion", ref "#/$defs/statement")]

def answerFields : List String := answer.map (·.1)

def regions : Shape :=
  c "Cardinality.Run.regionsJson: each counted sort's predicates, then every region constant with its sort and bits." [
    obj,
    .required ["predicates", "constants"],
    closed [
      ("predicates", n [obj, .object [] (some (n [arr, .items str, .maxItems 6]))]),
      ("constants", n [arr, .maxItems 512, .items (n [
        obj,
        .required ["constant", "sort", "bits"],
        closed [
          ("constant", n [str, .pattern (.seq (.lit "cardinality__") (.star (.cls [(' ', '~')])))]),
          ("sort", str),
          ("bits", n [str, .pattern (.rep (.cls [('0', '1')]) 0 6)])]])])]]

def problem : Shape :=
  c "Cardinality.Run.erasedJson: the regenerated W6a problem, premises then conclusion." [
    obj,
    .required ["premises", "conclusion"],
    closed [("premises", n [arr, .items (ref "#/$defs/erased")]), ("conclusion", ref "#/$defs/erased")]]

def admission : Shape :=
  c "Cardinality.Run.runCase admission: the statements, the region table and the regenerated erased problem." [
    obj,
    .references "/regions/constants" "sort" "/environment/cardinality/finite_sorts",
    .required (answerFields ++ ["regions", "erased"]),
    closed (answer ++ [("regions", ref "#/$defs/regions"), ("erased", ref "#/$defs/problem")])]

def certificate : Shape :=
  c "Cardinality.Run.runCase certificate: the replayed certificate's verdict beside the statements." [
    obj,
    .required ("valid" :: answerFields),
    closed (("valid", .type ["boolean"]) :: answer)]

def claim : Shape :=
  c "Cardinality.Run.claimJson: a node of the request's graph with its meaning id and canonical formula." [
    obj,
    .required ["name", "meaning_id", "formula"],
    closed [("name", str), ("meaning_id", ref "common.json#/$defs/hex64"), ("formula", ref "#/$defs/formula")]]

def document : Shape :=
  c "Cardinality.Run.runCase document: the admitted graph's report, its root and the leaves it rests on." [
    obj,
    .references "/report/leaves" "name" "/document/nodes/*/name",
    .required (envIds.map (·.1) ++ ["report"]),
    closed (envIds ++ [("report", n [
      obj,
      .required ["root", "leaves"],
      closed [
        ("root", n [ref "#/$defs/claim", props [("name", .equals "/document/root")]]),
        ("leaves", n [arr, .items (ref "#/$defs/claim")])]])])]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "#/$defs/error",
    .select [
      (ref "common.json#/$defs/no_kind", ref "#/$defs/admission"),
      (ref "#/$defs/kind/admission", ref "#/$defs/admission"),
      (ref "#/$defs/kind/certificate", ref "#/$defs/certificate"),
      (ref "#/$defs/kind/document", ref "#/$defs/document")]]

def file : File where
  name := "cardinality.json"
  comment := some "Mode cardinality: Cardinality.Run.runCaseReported. The case kind (default admission) selects the answer."
  top := [("row", «row»)]
  defs := [
    ("kind", kind),
    ("error", .schema error),
    ("body", .schema body),
    ("operand", .schema operand),
    ("printed", .schema printed),
    ("rule", .schema rule),
    ("formula", .schema formula),
    ("statement", .schema statement),
    ("erased", .schema erased),
    ("regions", .schema regions),
    ("problem", .schema problem),
    ("admission", .schema admission),
    ("certificate", .schema certificate),
    ("claim", .schema claim),
    ("document", .schema document)]

end ResponseShape.Schemas.Cardinality
