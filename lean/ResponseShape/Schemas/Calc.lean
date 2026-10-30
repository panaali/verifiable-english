import ResponseShape
import VE.Calc.Run

/-! The `calc` row (math-evidence spec 3.4, ME-2): the case's `meaning_id` and one row per request claim, in
order (`x-zip`), each naming its claim by the request's id (`x-equals`); or the case's refusal. An unknown row
carries one of Lean's reason texts (`VE.Calc.Run.words`); every other row's reason is `null`. A row's reproduction
is `"unknown"` exactly when the case names a software convention (`x-select` on the case). A row's kind is its
request entry's (`kind`). Every row has Lean's line and no finding (a standalone case is no translated document);
a claim row also has its sides, one per expression of the request's claim, its display, only for a rounding claim,
and its tie flag (`known`). -/
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

/-- A claim's sides: one per expression of the request's claim, each `item`. -/
def sides (item : Shape) : Shape :=
  n [arr, .items item, .anyOf [n [.onCase (form roundings), .minItems 1, .maxItems 1],
    n [.onCase (form ["within"]), .minItems 3, .maxItems 3], n [.onCase (form comparisons), .minItems 2, .maxItems 2]]]

/-- 2.5's display: a decimal truncated toward zero, then "…" when a nonzero remainder was dropped. -/
def truncated : Shape :=
  n [str, .pattern (.seq (Re.optional (.lit "-")) (.seq (.alt (.lit "0") digits) (.seq (Re.optional (.seq (.lit ".")
    (.seq (.cls [('0', '9')]) (.star (.cls [('0', '9')]))))) (Re.optional (.lit "…")))))]

/-- `yes` for a claim of one of the forms `ops`, `no` for any other. -/
def byForm (ops : List String) (yes no : Shape) : Shape :=
  .anyOf [n [.onCase (form ops), yes], n [.onCase (.not (form ops)), no]]

def null : Shape := .type ["null"]

/-- A name and its exact value, as spec 3.4 writes a free coefficient or a checked point. -/
def valuedName : Shape := n [arr, .minItems 2, .maxItems 2, .prefixItems [str, ref "#/$defs/exact"]]

def fact : Shape := n [obj, .required ["const", "coeffs", "strict"], closed [
  ("const", ref "#/$defs/exact"), ("coeffs", n [arr, .items valuedName]), ("strict", .type ["boolean"])]]

def step : Shape := .anyOf [
  n [obj, .required ["farkas"], closed [("farkas", n [obj, .required ["goal", "weights"], closed [
    ("goal", fact), ("weights", n [arr, .minItems 1, .items (ref "#/$defs/exact")])]])]],
  n [obj, .required ["square"], closed [("square", n [obj, .required ["square", "root", "a", "b"], closed [
    ("square", str), ("root", str), ("a", ref "#/$defs/exact"), ("b", ref "#/$defs/exact")]])]]]

def certificate : Shape := n [arr, .minItems 1, .items (ref "#/$defs/step")]
def counterexample : Shape := n [arr, .items valuedName]

def shownMembers (cert cx : Shape) : List (String × Shape) :=
  [("certificate", cert), ("counterexample", cx)]

/-- A tie flag `t`: the skeleton keeps the enumeration (a tie is a boolean or null), the client also its type. -/
def flag (t : String) : Shape := n [.type [t], .enum [.bool true, .bool false, .null]]

/-- A claim row's members beyond a follows row's (`known`, `undefinedMembers`, `unknownMembers`): its sides (`VE.Calc.Run.sides`), its display
(`VE.Calc.Run.display`) and its tie flag (`VE.Calc.Run.tie`, 2.2), by its outcome. A claim that holds or fails has
every side, a rounding claim its display and a `rounds` claim its tie flag; an undefined or unknown claim has a side
without a value, and an unknown one no display, nor a `rounds` claim's tie flag. Any other claim's tie is `false`. -/
def known : List (String × Shape) :=
  [("sides", sides (ref "#/$defs/exact")), ("display", byForm roundings truncated null),
    ("tie", byForm ["rounds"] (flag "boolean") (.const (.bool false)))]

def undefinedMembers : List (String × Shape) :=
  [("sides", n [sides (.anyOf [ref "#/$defs/exact", null]), .contains null]),
    ("display", byForm roundings (.anyOf [truncated, null]) null),
    ("tie", byForm ["rounds"] (flag "boolean") (.const (.bool false)))]

def unknownMembers : List (String × Shape) :=
  [("sides", n [sides (.anyOf [ref "#/$defs/exact", null]), .contains null]), ("display", null),
    ("tie", byForm ["rounds"] (flag "null") (.const (.bool false)))]

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

def claimRow (reproduction : Shape) : Shape :=
  c "VE.Calc.Run.rowJson: a decided row (holds, fails, undefined) has no reason; an unknown row has Lean's." [
    .anyOf [fields claimKind known (enumS ["holds", "fails"]) null reproduction,
      fields claimKind undefinedMembers (constS "undefined") null reproduction,
      fields claimKind unknownMembers (constS "unknown") (enumS reasons) reproduction,
      fields followsKind (shownMembers certificate null) (constS "holds") null reproduction,
      fields followsKind (shownMembers null counterexample) (constS "fails") null reproduction,
      fields followsKind (shownMembers null null) (constS "undefined") null reproduction,
      fields followsKind (shownMembers null null) (constS "unknown") (enumS reasons) reproduction]]

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
    ("refusal", .schema refusal), ("exact", .schema exact), ("step", .schema step)]

/-! The wire forms of spec 3.4: these rendered shapes catch a dropped type, required field or bound. -/
#guard (ResponseShape.render "calc.json" 64 valuedName).toOption.map Lean.Json.compress == some r##"{"maxItems":2,"minItems":2,"prefixItems":[{"type":"string"},{"$ref":"#/$defs/exact"}],"type":"array"}"##
#guard (ResponseShape.render "calc.json" 64 fact).toOption.map Lean.Json.compress == some r##"{"additionalProperties":false,"properties":{"coeffs":{"items":{"maxItems":2,"minItems":2,"prefixItems":[{"type":"string"},{"$ref":"#/$defs/exact"}],"type":"array"},"type":"array"},"const":{"$ref":"#/$defs/exact"},"strict":{"type":"boolean"}},"required":["const","coeffs","strict"],"type":"object"}"##
#guard (ResponseShape.render "calc.json" 64 step).toOption.map Lean.Json.compress == some r##"{"anyOf":[{"additionalProperties":false,"properties":{"farkas":{"additionalProperties":false,"properties":{"goal":{"additionalProperties":false,"properties":{"coeffs":{"items":{"maxItems":2,"minItems":2,"prefixItems":[{"type":"string"},{"$ref":"#/$defs/exact"}],"type":"array"},"type":"array"},"const":{"$ref":"#/$defs/exact"},"strict":{"type":"boolean"}},"required":["const","coeffs","strict"],"type":"object"},"weights":{"items":{"$ref":"#/$defs/exact"},"minItems":1,"type":"array"}},"required":["goal","weights"],"type":"object"}},"required":["farkas"],"type":"object"},{"additionalProperties":false,"properties":{"square":{"additionalProperties":false,"properties":{"a":{"$ref":"#/$defs/exact"},"b":{"$ref":"#/$defs/exact"},"root":{"type":"string"},"square":{"type":"string"}},"required":["square","root","a","b"],"type":"object"}},"required":["square"],"type":"object"}]}"##
#guard (ResponseShape.render "calc.json" 64 certificate).toOption.map Lean.Json.compress == some r##"{"items":{"$ref":"#/$defs/step"},"minItems":1,"type":"array"}"##
#guard (ResponseShape.render "calc.json" 64 counterexample).toOption.map Lean.Json.compress == some r##"{"items":{"maxItems":2,"minItems":2,"prefixItems":[{"type":"string"},{"$ref":"#/$defs/exact"}],"type":"array"},"type":"array"}"##
#guard (shownMembers certificate null).map (·.1) == ["certificate", "counterexample"]
#guard (shownMembers null counterexample).map (·.1) == ["certificate", "counterexample"]

end ResponseShape.Schemas.Calc
