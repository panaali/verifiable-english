import ResponseShape
import VE.EnglishGrammar.Run

/-! The source of `ve/backends/lean_service_schema/english.statement.json` (`file`; `tools/response_schemas.py`
writes it): the `english.statement` mode's row (`VE.EnglishGrammar.Norm.Run.statementCaseReported`,
docs/spec/en-e3-norm.md 2.3, recipe step 2), typed to the leaves. The members of each status are
`Run.statementFields`', and a status's `code` is one of its `Run.statementStatusCodes` list; `rendered` is EN-3's
(kind `render`) and joins with it. The relay binds numbers, spans and identities to the request (spec 2.4). -/
namespace ResponseShape.Schemas.EnglishStatement
open Lean ResponseShape
open VE.EnglishGrammar.Run (statementFields statementStatusCodes codeClasses)

def nat : Shape := ref "common.json#/$defs/nat"

def pair : Shape := n [arr, .prefixItems [nat, nat], .minItems 2, .maxItems 2]

def ruleRow : Shape :=
  c "Norm.Run.statementRow of a rule block: its number, its header's targets, its W1 node and its byte span." [
    obj, .required ["kind", "number", "exception_to", "node", "span"],
    closed [("kind", constS "rule"), ("number", nat), ("exception_to", n [arr, .items nat]),
      ("node", n [obj, .required ["norm"], closed [("norm", ref "common.json#/$defs/norm_node")]]),
      ("span", pair)]]

def precedenceRow : Shape :=
  c "Norm.Run.statementRow of a precedence line: rule `rule` takes precedence over rule `over`." [
    obj, .required ["kind", "rule", "over"],
    closed [("kind", constS "precedence"), ("rule", nat), ("over", nat)]]

def spanRow : Shape :=
  c "Norm.Run.spanRow: a phrase read and not formalised, its bytes, row, meaning owner and place." [
    obj, .required ["start", "stop", "row", "owner", "place"],
    closed [("start", nat), ("stop", nat), ("row", str), ("owner", str),
      ("place", enumS ["act", "guard", "carve_out", "bearer"])]]

def treeRow : Shape :=
  c "Run.treeRows: one node of a witness tree, its rule tag and token span [start, stop)." [
    arr, .prefixItems [str, nat, nat], .minItems 3, .maxItems 3]

def identities : Shape :=
  c "Norm.Run.answerWith: the source's SHA-256 and english.read's case identities (Run.decodeCase)." [
    obj, .required ["source_sha256", "environment_id", "lexicon_id", "grammar_id", "actions_version"],
    closed [("source_sha256", ref "common.json#/$defs/hex64"), ("environment_id", ref "common.json#/$defs/hex64"),
      ("overlay_digest", ref "common.json#/$defs/hex64"), ("lexicon_id", ref "common.json#/$defs/hex64"),
      ("grammar_id", ref "common.json#/$defs/hex64"), ("actions_version", ref "common.json#/$defs/text")]]

/-- A member's shape in a status's object (`statementFields`' names). -/
def member (status : String) : String → Shape
  | "statements" => n [arr, .minItems 1, .items (.anyOf [ref "#/$defs/rule_row", ref "#/$defs/precedence_row"])]
  | "code" => enumS ((statementStatusCodes.lookup status).getD [])
  | "text" => ref "common.json#/$defs/text"
  | "class" => enumS (codeClasses.map (·.2)).eraseDups
  | "sentence" => nat
  | "spans" => n [arr, .minItems 1, .items (ref "#/$defs/span_row")]
  | "witnesses" => n [arr, .minItems 2, .maxItems 2, .items (n [arr, .items (ref "#/$defs/tree_row")])]
  | "fault" => enumS ["lexicon", "notWellFormed", "notTyped"]
  | "failure" => n [arr, .prefixItems [str, str, str], .minItems 3, .maxItems 3]
  | "span" => pair
  | _ => .bool false

/-- One object per status of `statementFields` but EN-3's `rendered`. -/
def answer : Shape :=
  .anyOf ((statementFields.filter (·.1 != "rendered")).map fun (s, req, opt) =>
    n [obj, .required (["status"] ++ req ++ ["identities"]),
      closed ([("status", constS s)] ++ (req ++ opt).map (fun m => (m, member s m)) ++
        [("identities", ref "#/$defs/identities")])])

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [obj, .required ["id", "status", "result"],
      closed [("id", n [str, .equals "/id"]), ("status", constS "ok"), ("result", ref "#/$defs/answer")]]]

def file : File where
  name := "english.statement.json"
  comment := some "Mode english.statement: Norm.Run.statementCaseReported. readNorm's outcome for one rule-block text."
  top := [("row", «row»)]
  defs := [("rule_row", .schema ruleRow), ("precedence_row", .schema precedenceRow), ("span_row", .schema spanRow),
    ("tree_row", .schema treeRow),
    ("identities", .schema identities), ("answer", .schema answer)]

end ResponseShape.Schemas.EnglishStatement
