import ResponseShape
import VE.Calc.Run

/-! The `calc` row (math-evidence spec 3.4, ME-2): the case's `meaning_id` and one row per request claim, in
order (`x-zip`), each naming its claim by the request's id (`x-equals`); or the case's refusal. An unknown row
carries one of Lean's reason texts (`VE.Calc.Run.words`); every other row's reason is `null`. A row's reproduction
is `"unknown"` exactly when the case names a software convention (`x-select` on the case). A row's kind is its
request entry's (`kind`). -/
namespace ResponseShape.Schemas.Calc
open Lean ResponseShape

/-- The reason texts of an unknown row: `Run.words` of every unknown outcome. -/
def reasons : List String := VE.Calc.Run.outcomes.filterMap (VE.Calc.Run.words · |>.2)

/-- A row's kind is the form of the request's check: `"follows"` for a derivation, `"claim"` for any other entry. -/
def kind : Shape :=
  .anyOf [n [constS "claim", .onCase (props [("claim", .not (n [arr, .prefixItems [constS "follows"]]))])],
    n [constS "follows", .equals "/claim/0"]]

/-- A row's fields, with its outcome, reason and reproduction. -/
def fields (outcome reason reproduction : Shape) : Shape :=
  n [obj, .required ["status", "claim", "claim_id", "kind", "outcome", "reason", "reproduction"],
    closed [
      ("status", constS "ok"),
      ("claim", n [str, .equals "/id"]),
      ("claim_id", ref "common.json#/$defs/hex64"),
      ("kind", kind),
      ("outcome", outcome),
      ("reason", reason),
      ("reproduction", reproduction)]]

def claimRow (reproduction : Shape) : Shape :=
  c "VE.Calc.Run.rowJson: a decided row (holds, fails, undefined) has no reason; an unknown row has Lean's." [
    .anyOf [fields (enumS ["holds", "fails", "undefined"]) (.type ["null"]) reproduction,
      fields (constS "unknown") (enumS reasons) reproduction]]

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
    ("refusal", .schema refusal)]

end ResponseShape.Schemas.Calc
