import VE.Cardinality.Wire
import VE.Cardinality.Examples

/-! Fixtures of the `ve-cardinality@1` decoders (docs/spec/quantities.md 4.1–4.3, 9.1: FA1 decoded, FA8 and FA9 at
the wire, FA11's projection and identities, FA13, and each environment and statement text of 4.2).

Each `#guard` decodes JSON as a request carries it and fails the build when a decoded statement, an identity, a text
or the order of two texts changes. -/
namespace VE.Cardinality.WireExamples
open Lean VE.Cardinality VE.Cardinality.Wire

def p (s : String) : Json := (Json.parse s).toOption.getD .null

/-- FA1's vocabulary as a `ve-cardinality@1` environment (FA11), with two `bp` and two `day` constants for the ratio
fixtures. -/
def env : Json := p r#"{"language": "ve.core@0.2",
  "profiles": ["cardinality@0", "order@0", "relational-fol@0", "time@0"],
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "vocabulary": {"sorts": {"fomc_policymaker": {"description": "FOMC policymaker"}, "user": {"description": "user"}},
    "predicates": {
      "expects_further_increase": {"arguments": ["fomc_policymaker"], "description": "expects a further increase"},
      "expects_rates_to_stay": {"arguments": ["fomc_policymaker"], "description": "expects rates to stay"},
      "curious": {"arguments": ["user"], "description": "is curious"},
      "advises": {"arguments": ["fomc_policymaker", "fomc_policymaker"], "description": "advises"}},
    "constants": {"sept": {"sort": "$int", "unit": "bp", "description": "the September estimate"},
      "june": {"sort": "$int", "unit": "bp", "description": "the June estimate"},
      "d1": {"sort": "$int", "unit": "day", "description": "the first date"},
      "d2": {"sort": "$int", "unit": "day", "description": "the second date"}}},
  "unit_schema": "ve-units@1",
  "units": {"bp": {"scale": "100", "display": {"kind": "percent"}},
    "day": {"scale": "1", "display": {"kind": "iso_date"}}},
  "cardinality_schema": "ve-cardinality@1",
  "cardinality": {"finite_sorts": ["fomc_policymaker"]}}"#

def st (formula : String) : Json := Json.mkObj [("format", .str "ve-cardinality@1"), ("formula", p formula)]

/-- Each statement decoded in `e`: its formula and meaning id, or the first refusal. -/
def decode (statements : List Json) (e : Json := env) : Except String (List (CFormula × String)) := do
  let w ← decodeEnvironment e
  statements.mapM fun j => do
    let a ← decodeStatement w j
    pure (a.formula, a.meaningId)

def refusal (formula : String) (e : Json := env) : String :=
  match decode [st formula] e with
  | .ok _ => "admitted"
  | .error m => m

def admitted (formula : String) : Bool := refusal formula == "admitted"

def meaningId (formula : Json) (e : Json := env) : String :=
  match decode [Json.mkObj [("format", .str "ve-cardinality@1"), ("formula", formula)]] e with
  | .ok [(_, m)] => m
  | _ => ""

/-! ## FA11: the projection and the two identities -/

/-- The decoded environment's three identities (cardinality, W6a annotated, W6a target), its projection's profiles
and its finite sorts. -/
def decoded (e : Json) : Option ((String × String × String) × List String × List String) :=
  (decodeEnvironment e).toOption.map fun w =>
    ((w.environmentId, w.w6.environmentId, w.w6.targetId), w.w6.profiles, w.env.finite)

#guard (projectW6 env).toOption.map (·.getObjValD "profiles") == some (p r#"["order@0", "relational-fol@0", "time@0"]"#)
#guard (decoded env).map (·.2) == some (["order@0", "relational-fol@0", "time@0"], ["fomc_policymaker"])
#guard match decoded env with
  | some ((c, w6, t), _) => c != w6 && c != t && w6 != t && c.length == 64
  | none => false
-- With `documents@1` the projection is W6a's second list, and the identity is another.
def envDocs : Json := env.setObjVal! "profiles"
  (p r#"["cardinality@0", "documents@1", "order@0", "relational-fol@0", "time@0"]"#)
#guard (decoded envDocs).map (·.2.1) == some ["documents@1", "order@0", "relational-fol@0", "time@0"]
#guard (decoded envDocs).map (·.1.1) != (decoded env).map (·.1.1)
-- Draft 1's E4 (the profiles kept) is refused by W6a's decoder.
#guard (VE.Time.Wire.decodeEnvironment ((VE.Time.Wire.dropFields env ["cardinality_schema", "cardinality"]).toOption.get!)
  matches .error "UnsupportedProfile: ve-units@1 requires exactly order@0, relational-fol@0 and time@0, optionally with documents@1")

/-! ## FA1: the wire decodes exactly the core's statements, whose certificate `fa1_entails` replays -/

def fa1Premises : List Json := [st r#"["count", "fomc_policymaker", [["1", ["any"]]], "eq", "18"]"#,
  st r#"["count", "fomc_policymaker", [["1", ["is", "expects_further_increase"]]], "eq", "16"]"#,
  st r#"["count", "fomc_policymaker", [["1", ["is", "expects_rates_to_stay"]]], "eq", "2"]"#,
  st r#"["quantity", ["forall", "fomc_policymaker", ["not", ["and", ["unary", "expects_further_increase", ["var", 0]],
    ["unary", "expects_rates_to_stay", ["var", 0]]]]]]"#]
def fa1Conclusion : Json := st r#"["quantity", ["forall", "fomc_policymaker", ["or",
  ["unary", "expects_further_increase", ["var", 0]], ["unary", "expects_rates_to_stay", ["var", 0]]]]]"#

#guard (decode (fa1Premises ++ [fa1Conclusion])).toOption.map (·.map (·.1)) ==
  some (Examples.fa1 ++ [Examples.fa1Conclusion])
-- FA1b: the problem without the exclusion premise decodes to the core's FA1b.
#guard (decode fa1Premises.dropLast).toOption.map (·.map (·.1)) == some Examples.fa1.dropLast
-- The canonical encoding reads back as itself, so the identity is over what was decoded.
#guard (decode (fa1Premises ++ [fa1Conclusion])).toOption.map (·.map (encode ·.1)) ==
  some ((fa1Premises ++ [fa1Conclusion]).map (·.getObjValD "formula"))

/-! ## Identities: what the meaning id binds -/

def ratio (printed : String) : Json :=
  p s!"[\"rounds_to\", \"ties_up\", [\"quantity\", [\"const\", \"bp\", \"sept\"]], [\"quantity\", [\"const\", \"bp\", \"june\"]], \"{printed}\"]"
-- "0.30" and "0.3" are different claims; one statement has one id in each environment, which it binds.
#guard meaningId (ratio "0.30") != meaningId (ratio "0.3") && meaningId (ratio "0.3") != ""
#guard meaningId (ratio "0.30") == meaningId (ratio "0.30") && meaningId (ratio "0.30") != meaningId (ratio "0.30") envDocs
-- The rule and the order of the operands are bound too.
#guard meaningId (ratio "1") != meaningId (p r#"["rounds_to", "half_even", ["quantity", ["const", "bp", "sept"]],
  ["quantity", ["const", "bp", "june"]], "1"]"#)
#guard meaningId (ratio "1") != meaningId (p r#"["rounds_to", "ties_up", ["quantity", ["const", "bp", "june"]],
  ["quantity", ["const", "bp", "sept"]], "1"]"#)
-- A spelling W6a canonicalises (`-0`) is the same statement.
#guard meaningId (ratio "-0.0") == meaningId (ratio "0.0")

/-! ## FA8 and FA9 at the wire: the hostile set -/

#guard refusal r#"["count", "user", [["1", ["is", "curious"]]], "le", "2"]"# == "CardinalityNotFinite(user)"
#guard refusal r#"["count", "fomc_policymaker", [["1", ["is", "advises"]]], "le", "2"]"# ==
  "TypeMismatch: advises is not a unary predicate of sort fomc_policymaker"
#guard refusal r#"["count", "fomc_policymaker", [["1", ["not", ["is", "curious"]]]], "le", "2"]"# ==
  "TypeMismatch: curious is not a unary predicate of sort fomc_policymaker"
def share (num den : String) : String :=
  s!"[\"proportion\", \"fomc_policymaker\", [\"any\"], [\"is\", \"expects_rates_to_stay\"], \"gt\", \"{num}\", \"{den}\"]"
#guard refusal (share "3" "2") == "ProportionRange(3 in 2)"
#guard refusal (share "0" "0") == "ProportionRange(0 in 0)"
#guard refusal (share "-1" "2") == "ProportionRange(-1 in 2)"
#guard admitted (share "1" "2") && admitted (share "2" "2") && admitted (share "0" "1")
#guard admitted r#"["count", "fomc_policymaker", [["1", ["is", "expects_further_increase"]]], "eq", "16"]"#
-- 65 terms (S7); 64 pass.
def terms (n : Nat) : String :=
  "[\"count\", \"fomc_policymaker\", [" ++ ", ".intercalate (List.replicate n "[\"1\", [\"any\"]]") ++ "], \"le\", \"7\"]"
#guard refusal (terms 65) == "ResourceLimit: At most 64 terms in a count"
#guard admitted (terms 64)
-- FA9a: a declared constant with the region prefix (E8), and a sort and a predicate with it.
def declaring (field name entry : String) : Json :=
  let voc := env.getObjValD "vocabulary"
  env.setObjVal! "vocabulary" (voc.setObjVal! field ((voc.getObjValD field).setObjVal! name (p entry)))
#guard refusal (terms 1) (declaring "constants" "cardinality__fomc_policymaker__0" r#"{"sort": "$int", "description": "five"}"#) ==
  "ReservedName: cardinality__ is reserved for region constants (cardinality__fomc_policymaker__0)"
#guard refusal (terms 1) (declaring "sorts" "cardinality__x" r#"{"description": "x"}"#) ==
  "ReservedName: cardinality__ is reserved for region constants (cardinality__x)"
#guard refusal (terms 1) (declaring "predicates" "cardinality__p" r#"{"arguments": ["user"], "description": "p"}"#) ==
  "ReservedName: cardinality__ is reserved for region constants (cardinality__p)"
#guard admitted (terms 1) &&
  refusal (terms 1) (declaring "constants" "cardinality_x" r#"{"sort": "$int", "description": "x"}"#) == "admitted"
-- FA9e: ratios of dates, of mixed tags, and rules that are decoded but not admitted.
def ratioOf (rule x y : String) : String :=
  s!"[\"rounds_to\", \"{rule}\", [\"quantity\", [\"const\", {x}]], [\"quantity\", [\"const\", {y}]], \"1\"]"
#guard refusal (ratioOf "ties_up" "\"day\", \"d1\"" "\"day\", \"d2\"") ==
  "TypeMismatch: a ratio of calendar dates has no meaning; durations use elapsed_day"
#guard refusal (ratioOf "ties_up" "\"bp\", \"sept\"" "\"day\", \"d2\"") == "TypeMismatch: UnitMismatch(bp,day)"
#guard refusal (ratioOf "down" "\"bp\", \"sept\"" "\"bp\", \"june\"") == "UnsupportedRounding(down)"
#guard refusal (ratioOf "up" "\"bp\", \"sept\"" "\"bp\", \"june\"") == "UnsupportedRounding(up)"
#guard admitted (ratioOf "half_even" "\"bp\", \"sept\"" "\"bp\", \"june\"")
#guard admitted r#"["percent_rounds_to", "ties_up", ["count", "fomc_policymaker", ["is", "expects_further_increase"]],
  ["count", "fomc_policymaker", ["any"]], "0.30"]"#
#guard admitted r#"["percent_of", ["quantity", ["const", "bp", "sept"]], ["quantity", ["const", "bp", "june"]], "105"]"#
#guard refusal r#"["percent_of", ["count", "fomc_policymaker", ["any"]], ["quantity", ["const", "bp", "june"]], "1"]"# ==
  "TypeMismatch: UnitMismatch(dimensionless,bp)"

/-! ## The other statement texts (S1–S4), each once -/

#guard refusal (ratioOf "nearest" "\"bp\", \"sept\"" "\"bp\", \"june\"") == "Unknown rounding rule nearest"
#guard refusal r#"["percent_of", ["quantity", ["const", "bp", "sept"]], ["quantity", ["const", "bp", "june"]], "1.0.5"]"# ==
  "Invalid decimal literal \"1.0.5\""
#guard refusal r#"["count", "fomc_policymaker", [["01", ["any"]]], "le", "2"]"# == "non-canonical integer"
#guard refusal r#"["count", "fomc_policymaker", [["1", ["any"]]], "ge", "2"]"# == "Unknown cardinality operator ge"
#guard refusal r#"["count", "fomc_policymaker", [["1", ["every"]]], "le", "2"]"# == "Unknown cardinality operator every"
#guard refusal r#"["count", "fomc_policymaker", [["1", ["is"]]], "le", "2"]"# == "Invalid cardinality formula"
#guard refusal r#"["most", "fomc_policymaker"]"# == "Unknown cardinality operator most"
#guard refusal r#"["quantity", ["lt", ["const", "bp", "sept"], ["const", "day", "d1"]]]"# ==
  "TypeMismatch: UnitMismatch(bp,day)"
#guard refusal r#"["percent_of", ["quantity", ["const", "fomc_policymaker", "x"]], ["quantity", ["const", "bp", "june"]], "1"]"# ==
  "Unknown constant \"x\""
#guard (decode [Json.mkObj [("format", .str "ve-cardinality@2"), ("formula", p r#"["any"]"#)]] matches
  .error "Unsupported cardinality format")
#guard (decode [(st (terms 1)).setObjVal! "Q" (p "[]")] matches .error "Unsupported cardinality format")
-- Formula depth 65 (S2's depth, by the pass's fuel); 64 decode.
def nested (n : Nat) : String := (List.replicate (n - 1) "[\"not\", ").foldr (· ++ ·) (terms 1 ++ "".pushn ']' (n - 1))
#guard refusal (nested 65) == VE.Time.Wire.depthLimit && admitted (nested 64)

/-! ## The environment's texts, E1–E8, each once and in order -/

#guard (refusal (terms 1) (env.setObjVal! "extra" (p "1"))).startsWith "fields do not match"
def e2 : String :=
  "UnsupportedProfile: cardinality@0 requires order@0, relational-fol@0 and time@0, optionally with documents@1"
#guard refusal (terms 1) (env.setObjVal! "profiles" (p r#"["order@0", "relational-fol@0", "time@0"]"#)) == e2
#guard refusal (terms 1) (env.setObjVal! "profiles" (p r#"["cardinality@0", "norms@0", "order@0", "relational-fol@0",
  "time@0"]"#)) == e2
-- E2 before E3, E3 before E4, E4 (W6a's own text) before E5.
#guard refusal (terms 1) ((env.setObjVal! "profiles" (p r#"["cardinality@0", "order@0"]"#)).setObjVal!
  "cardinality_schema" (.str "x")) == e2
#guard refusal (terms 1) ((env.setObjVal! "cardinality_schema" (.str "ve-cardinality@2")).setObjVal! "spec_revision"
  (.str "x")) == "UnsupportedProfile: Unsupported cardinality schema"
#guard refusal (terms 1) ((env.setObjVal! "spec_revision" (.str "x")).setObjVal! "cardinality" (p "1")) ==
  "UnsupportedProfile: Unsupported specification revision"
def finite (sorts : String) : Json := env.setObjVal! "cardinality" (p sorts)
#guard refusal (terms 1) (finite r#"{"finite_sorts": "fomc_policymaker"}"#) ==
  "InvalidInput: cardinality.finite_sorts must be an array of sort names"
#guard refusal (terms 1) (finite r#"{"finite_sorts": [], "more": 1}"#) ==
  "InvalidInput: cardinality.finite_sorts must be an array of sort names"
#guard refusal (terms 1) (finite r#"{"finite_sorts": [1]}"#) ==
  "InvalidInput: cardinality.finite_sorts must be an array of sort names"
#guard refusal (terms 1) (finite (Json.mkObj [("finite_sorts", toJson (List.replicate 65 "x"))]).compress) ==
  "ResourceLimit: At most 64 finite sorts"
#guard refusal (terms 1) (finite r#"{"finite_sorts": ["user", "fomc_policymaker", "user"]}"#) ==
  "DuplicateDeclaration: finite sort user"
#guard refusal (terms 1) (finite r#"{"finite_sorts": ["fomc_policymaker", "users", "users"]}"#) == "UnknownSort(users)"
#guard refusal (terms 1) (finite r#"{"finite_sorts": ["users", "cardinality__x"]}"#) == "UnknownSort(users)"
-- A sort declared finite is the only one counts may name; an empty list refuses every count.
#guard refusal (terms 1) (finite r#"{"finite_sorts": []}"#) == "CardinalityNotFinite(fomc_policymaker)"
#guard (decode [st r#"["count", "user", [["1", ["is", "curious"]]], "le", "2"]"#]
  (finite r#"{"finite_sorts": ["user", "fomc_policymaker"]}"#)).isOk

/-! ## FA13: competing faults -/

-- One node, two faults: S5 before S8; S9 before S10.
#guard refusal r#"["proportion", "user", ["any"], ["is", "curious"], "gt", "3", "2"]"# == "CardinalityNotFinite(user)"
#guard refusal (ratioOf "down" "\"bp\", \"sept\"" "\"day\", \"d1\"") == "TypeMismatch: UnitMismatch(bp,day)"
-- S3 before S5 and S6 within a node, S6 before S7.
#guard refusal r#"["count", "user", [["1", ["is", "curious"]]], "ge", "2"]"# == "Unknown cardinality operator ge"
#guard refusal ((terms 65).replace "[\"any\"]]], " "[\"is\", \"curious\"]]], ") ==
  "TypeMismatch: curious is not a unary predicate of sort fomc_policymaker"
-- Two faulty nodes: the checks loop over nodes, so the left node's later check comes first, either way round.
def badCount : String := r#"["count", "user", [["1", ["is", "curious"]]], "le", "2"]"#
#guard refusal s!"[\"and\", {share "3" "2"}, {badCount}]" == "ProportionRange(3 in 2)"
#guard refusal s!"[\"and\", {badCount}, {share "3" "2"}]" == "CardinalityNotFinite(user)"
-- An operand's fault before its node's tag mismatch.
#guard refusal r#"["rounds_to", "ties_up", ["count", "user", ["is", "curious"]], ["quantity", ["const", "bp", "sept"]], "296"]"# ==
  "CardinalityNotFinite(user)"
-- Over the size limit with an unknown operator inside: S2 first (10,002 array nodes).
#guard refusal s!"[\"and\", {terms 5000}, [\"bogus\"]]" == VE.Time.Wire.depthLimit
#guard refusal s!"[\"and\", {terms 64}, [\"bogus\"]]" == "Unknown cardinality operator bogus"
-- Statements in request order: the first refusal is the first faulty statement's.
#guard decode [st badCount, st (share "3" "2")] matches .error "CardinalityNotFinite(user)"

end VE.Cardinality.WireExamples
