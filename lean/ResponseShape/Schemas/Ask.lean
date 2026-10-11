import ResponseShape
import VE.Ask.Run

/-! The `ask` row (docs/spec/question-answering.md 4.2, 8; plan 4.8), every field typed. An answered question carries
the asked sentence, its formula, the lead, Lean's lines with their metadata, one row per compatible choice, the
unused sentences and the unchecked reading names; a question VE does not read with one meaning carries
`english.question`'s status, code, class and text. The relay binds every id, choice, reading, source, quote and
unused unit to the request (`ve.ask.answer_problem`). -/
namespace ResponseShape.Schemas.Ask
open Lean ResponseShape

def pairNat : Shape := n [arr, .prefixItems [str, ref "common.json#/$defs/nat"], .minItems 2, .maxItems 2]

/-- `Readings.choiceJson`: each open set with the index of its candidate. -/
def choice : Shape := c "Readings.choiceJson: [set, index] per open set." [arr, .items (ref "#/$defs/pair_nat")]

/-- `VE.Ask.Run.sourceJson`. -/
def source : Shape :=
  c "VE.Ask.Run.sourceJson: where a cited premise comes from." [
    .anyOf [
      n [obj, .required ["kind", "unit"], closed [("kind", constS "unit"), ("unit", ref "common.json#/$defs/token")]],
      n [obj, .required ["kind", "predicate"], closed [("kind", constS "rules"), ("predicate", str)]],
      n [obj, .required ["kind", "name"], closed [("kind", constS "definition"), ("name", str)]],
      n [obj, .required ["kind"], closed [("kind", constS "background")]],
      n [obj, .required ["kind", "required", "permission"],
        closed [("kind", constS "pair"), ("required", str), ("permission", str)]],
      n [obj, .required ["kind", "required", "permission"],
        closed [("kind", constS "fill"), ("required", str), ("permission", str)]]]]

/-- `Readings.Wire.gapsJson`: a filled gap, its predicate, its tuple's ids and the filling's answer. -/
def gap : Shape :=
  n [arr, .prefixItems [str, ref "common.json#/$defs/strings", .type ["boolean"]], .minItems 3, .maxItems 3]

/-- A line's cited source, or null (null is `const null`, which the skeleton keeps; `type null` is any value). -/
def sourceOrNull : Shape := .anyOf [.const .null, ref "#/$defs/source"]

def line : Shape :=
  c "VE.Ask.Run.lineJson: a line of the answer, its text Lean's lineText of its metadata." [
    obj, .required ["frame", "text", "source", "quote", "readings", "witness", "unchecked"],
    closed [
      ("frame", n [str, .minLength 1]), ("text", n [str, .minLength 1]),
      ("source", ref "#/$defs/source_or_null"),
      ("quote", .anyOf [.const .null, n [arr, .prefixItems [ref "common.json#/$defs/token", str],
        .minItems 2, .maxItems 2]]),
      ("readings", n [arr, .items (ref "#/$defs/pair_nat")]),
      ("witness", .anyOf [.const .null, ref "#/$defs/choice"]),
      ("unchecked", .type ["boolean"])]]

def leads : List String := ["yes", "no", "notSettled", "notNecessarily", "unknown"]
def reasons : List String := ["X1", "X2", "X3", "X4", "X5", "X6"]

/-- A row's reason (`Row.reason`): null unless the lead is unknown. -/
def reason : Shape := .anyOf [.const .null, enumS reasons]

def row : Shape :=
  c "VE.Ask.Run.rowJson: one compatible choice, its lead, its reason, its citations and its countermodel's gaps." [
    obj, .required ["choice", "lead", "reason", "cited", "gaps"],
    closed [
      ("choice", ref "#/$defs/choice"), ("lead", enumS leads),
      ("reason", ref "#/$defs/reason"),
      ("cited", n [arr, .items (ref "#/$defs/source")]),
      ("gaps", n [arr, .items (ref "#/$defs/gap")])]]

def name : Shape :=
  n [obj, .required ["set", "index", "text"],
    closed [("set", str), ("index", ref "common.json#/$defs/nat"), ("text", str)]]

def identities : Shape :=
  n [obj, .required ["source_sha256", "environment_id", "lexicon_id", "grammar_id", "actions_version",
      "question_version", "document_id"],
    closed [("source_sha256", ref "common.json#/$defs/hex64"), ("environment_id", ref "common.json#/$defs/hex64"),
      ("lexicon_id", ref "common.json#/$defs/hex64"), ("grammar_id", ref "common.json#/$defs/hex64"),
      ("actions_version", str), ("question_version", str), ("document_id", ref "common.json#/$defs/hex64")]]

/-- `EnglishGrammar.EFormula.encode`: the question's formula, decided by its decoder. -/
def englishFormula : Shape :=
  decidedBy "EnglishGrammar.EFormula.decode" (fun j => (VE.EnglishGrammar.EFormula.decode j).isSome) <|
    c "EnglishGrammar.EFormula.encode of the question's formula: EFormula.decode's grammar." [arr, .minItems 1]

def answered : Shape :=
  n [obj, .required ["status", "route", "form", "sentence", "ast", "spans", "lead", "text", "lines", "rows",
      "unused", "unchecked_names", "identities"],
    closed [
      ("status", constS "answered"), ("route", enumS ["readings", "plain", "norm-defaults"]),
      ("form", enumS ["caseThat", "fronted"]), ("sentence", n [str, .minLength 1]),
      ("ast", ref "#/$defs/english_formula"),
      ("spans", n [arr, .items (n [arr, .prefixItems [ref "common.json#/$defs/nat", ref "common.json#/$defs/nat"],
        .minItems 2, .maxItems 2])]),
      ("lead", enumS (leads ++ ["by_reading"])),
      ("text", n [arr, .items str]),
      ("lines", n [arr, .minItems 1, .items (ref "#/$defs/line")]),
      ("rows", n [arr, .minItems 1, .items (ref "#/$defs/row")]),
      ("unused", n [arr, .items (ref "common.json#/$defs/token")]),
      ("unchecked_names", n [arr, .items (ref "#/$defs/name")]),
      ("identities", ref "#/$defs/identities")]]

def refused : Shape :=
  c "A question VE does not read with one meaning: english.question's status, code, class and text." [
    obj, .required ["status", "code", "class", "text", "identities"],
    closed [("status", str), ("code", str), ("class", str), ("text", str),
      ("identities", ref "#/$defs/identities")]]

def «row'» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [obj, .required ["id", "status", "result"],
      closed [("id", n [str, .equals "/id"]), ("status", constS "ok"),
        ("result", .anyOf [ref "#/$defs/answered", ref "#/$defs/refused"])]]]

def file : File where
  name := "ask.json"
  comment := some "Lean question answer: the lines Lean renders from its checked answer, every field typed."
  top := [("row", «row'»)]
  defs := [("pair_nat", .schema pairNat), ("choice", .schema choice), ("source", .schema source),
    ("source_or_null", .schema sourceOrNull), ("gap", .schema gap), ("reason", .schema reason),
    ("line", .schema line), ("row", .schema row), ("name", .schema name), ("identities", .schema identities),
    ("english_formula", .schema englishFormula), ("answered", .schema answered), ("refused", .schema refused)]

end ResponseShape.Schemas.Ask
