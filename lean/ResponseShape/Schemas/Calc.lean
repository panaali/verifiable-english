import ResponseShape
import VE.Calc.Run

/-! The `calc` row (math-evidence spec 3.4, ME-2): the case's `meaning_id` and one row per request claim, in
order (`x-zip`), each naming its claim by the request's id (`x-equals`); or the case's refusal. An unknown row
carries one of Lean's reason texts (`VE.Calc.Run.words`); every other row's reason is `null`. A row's reproduction
is `"unknown"` exactly when the case names a software convention (`x-select` on the case). A row's kind is its
request entry's (`kind`). Every row has Lean's line and no finding (a standalone case is no translated document);
a claim row also has its sides, one per expression of the request's claim, its display, only for a rounding claim,
and its tie flag, `false` but for a `rounds` claim (`claimMembers`). -/
namespace ResponseShape.Schemas.Calc
open Lean ResponseShape

/-- The reason texts of an unknown row: `Run.words` of every unknown outcome. -/
def reasons : List String := VE.Calc.Run.outcomes.filterMap (VE.Calc.Run.words · |>.2)

/-- A request entry whose check is a derivation, `["follows", …]`. -/
def derivation : Shape := n [.required ["claim"], props [("claim", n [arr, .minItems 1, .prefixItems [constS "follows"]])]]

/-- A request entry whose check is a claim of one of the forms `ops` (3.1). -/
def form (ops : List String) : Shape :=
  n [.required ["claim"], props [("claim", n [arr, .minItems 1, .prefixItems [enumS ops]])]]

/-- The claim forms of one expression (the rounding claims) and of two (the comparisons, `VE.Calc.Wire`'s). -/
def roundings : List String := ["rounds", "rounds-down", "rounds-up"]
def comparisons : List String := VE.Calc.Wire.comparisons.map (·.1)

def digits : Re := .seq (.cls [('1', '9')]) (.star (.cls [('0', '9')]))

def exact : Shape :=
  c "VE.Calc.Run.exact: an exact value, a reduced fraction \"n/d\" or an integer \"n\"." [str,
    .pattern (.alt (.lit "0") (.seq (Re.optional (.lit "-")) (.seq digits (Re.optional (.seq (.lit "/") digits)))))]

/-- A claim's sides: one per expression of the request's claim, each its exact value or `null`. -/
def sides : Shape :=
  c "VE.Calc.Run.sides: each expression's exact value, or null where it has none (undefined, or beyond a limit)." [
    arr, .items (.anyOf [ref "#/$defs/exact", .type ["null"]]),
    .anyOf [n [.onCase (form roundings), .minItems 1, .maxItems 1], n [.onCase (form ["within"]), .minItems 3,
      .maxItems 3], n [.onCase (form comparisons), .minItems 2, .maxItems 2]]]

/-- 2.5's display: a decimal truncated toward zero, then "…" when a nonzero remainder was dropped. -/
def display : Shape :=
  c "VE.Calc.Run.display: a rounding claim's value truncated at two places beyond the printed ones, or null." [
    .anyOf [n [.onCase (form roundings), .anyOf [n [str, .pattern (.seq (Re.optional (.lit "-")) (.seq
        (.alt (.lit "0") digits) (.seq (Re.optional (.seq (.lit ".") (.seq (.cls [('0', '9')])
          (.star (.cls [('0', '9')]))))) (Re.optional (.lit "…")))))], .type ["null"]]],
      n [.onCase (.not (form roundings)), .type ["null"]]]]

def tie : Shape :=
  c "VE.Calc.Run.tie: 2.2's tie flag, null for a rounds claim without a known value; false for any other claim." [
    .anyOf [n [.onCase (form ["rounds"]), .type ["boolean", "null"]], n [.onCase (.not (form ["rounds"])),
      .const (.bool false)]]]

/-- A row's fields: its kind, its outcome, reason and reproduction, and the members `more` of its kind. -/
def fields (kind : Shape) (more : List (String × Shape)) (outcome reason reproduction : Shape) : Shape :=
  n [obj, .required (["status", "claim", "claim_id", "kind", "outcome", "reason", "line", "finding",
      "reproduction"] ++ more.map (·.1)),
    closed ([
      ("status", constS "ok"),
      ("claim", n [str, .equals "/id"]),
      ("claim_id", ref "common.json#/$defs/hex64"),
      ("kind", kind),
      ("outcome", outcome),
      ("reason", reason),
      ("line", c "VE.Calc.Run.line: Lean's English (11.1), or null beyond 11.2's nesting rule." [
        .anyOf [ref "common.json#/$defs/text", .type ["null"]]]),
      ("finding", c "VE.Calc.Run.rowJson: a standalone case is no translated document (2.5, 13.6)." [.type ["null"]]),
      ("reproduction", reproduction)] ++ more)]

/-- A row's kind is the form of the request's check: `"follows"` for a derivation, `"claim"` for any other entry. -/
def claimKind : Shape := n [constS "claim", .onCase (.not derivation)]
def followsKind : Shape := n [constS "follows", .onCase derivation]

/-- A claim row's members beyond a follows row's: its sides, display and tie. -/
def claimMembers : List (String × Shape) := [("sides", ref "#/$defs/sides"), ("display", display), ("tie", tie)]

def decided : Shape := enumS ["holds", "fails", "undefined"]

def claimRow (reproduction : Shape) : Shape :=
  c "VE.Calc.Run.rowJson: a decided row (holds, fails, undefined) has no reason; an unknown row has Lean's." [
    .anyOf [fields claimKind claimMembers decided (.type ["null"]) reproduction,
      fields claimKind claimMembers (constS "unknown") (enumS reasons) reproduction,
      fields followsKind [] decided (.type ["null"]) reproduction,
      fields followsKind [] (constS "unknown") (enumS reasons) reproduction]]

def answer (rowDef : String) : Shape :=
  c "VE.Calc.Run.runCaseReported: the case's meaning_id (spec 3.3) and one row per request claim, in order." [
    obj, .required ["status", "meaning_id", "rows"],
    closed [
      ("status", constS "ok"),
      ("meaning_id", ref "common.json#/$defs/hex64"),
      ("rows", n [arr, .zip "/claims" (ref s!"#/$defs/{rowDef}")])]]

def refusal : Shape :=
  c "VE.Calc.Run.runCaseReported: the decoder's refusal of the case (spec 3.2, 13.1)." [
    obj, .required ["status", "error"],
    closed [("status", constS "error"), ("error", ref "common.json#/$defs/text")]]

def «row» : Shape :=
  .select [
    (n [obj, .not (.required ["software"])],
      .anyOf [ref "common.json#/$defs/case_error", ref "#/$defs/refusal", ref "#/$defs/answer"]),
    (.bool true, .anyOf [ref "common.json#/$defs/case_error", ref "#/$defs/refusal", ref "#/$defs/answer_software"])]

def file : File where
  name := "calc.json"
  comment := some "Mode calc: VE.Calc.Run.runCaseReported, the claims of a ve-calc@0 case (math-evidence ME-2)."
  top := [("row", «row»)]
  defs := [("claim_row", .schema (claimRow (.type ["null"]))),
    ("claim_row_software", .schema (claimRow (constS "unknown"))),
    ("answer", .schema (answer "claim_row")), ("answer_software", .schema (answer "claim_row_software")),
    ("refusal", .schema refusal), ("exact", .schema exact), ("sides", .schema sides)]

end ResponseShape.Schemas.Calc
