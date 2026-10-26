import VE.Cardinality.Run
import VE.Cardinality.Examples

/-! Fixtures of the `ve-cardinality@1` wire (docs/spec/quantities.md 4.1–4.3, 9.1: FA1, FA1b, FA8 and FA9 at the
wire, a forged region table and erased problem, FA11, FA13, and each diagnostic of 4.2).

Each `#guard` runs the runner on a JSON case, as the service will, and fails the build when an answer, a text or the
order of two texts changes. FA1's certificate replays the trace Python's untrusted search found
(`VE.Cardinality.Examples.fa1Trace`), bound to the identities the admission case answers. -/
namespace VE.Cardinality.WireExamples
open Lean VE.Cardinality VE.Cardinality.Wire

def p (s : String) : Json := (Json.parse s).toOption.getD .null

/-- FA1's vocabulary as a `ve-cardinality@1` environment (FA11), with two `bp` and two `day` constants for the ratio
fixtures and five more predicates on the finite sort for the limits. -/
def env : Json := p r#"{"language": "ve.core@0.2",
  "profiles": ["cardinality@0", "order@0", "relational-fol@0", "time@0"],
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "vocabulary": {"sorts": {"fomc_policymaker": {"description": "FOMC policymaker"}, "user": {"description": "user"}},
    "predicates": {
      "expects_further_increase": {"arguments": ["fomc_policymaker"], "description": "expects a further increase"},
      "expects_rates_to_stay": {"arguments": ["fomc_policymaker"], "description": "expects rates to stay"},
      "curious": {"arguments": ["user"], "description": "is curious"},
      "advises": {"arguments": ["fomc_policymaker", "fomc_policymaker"], "description": "advises"},
      "a1": {"arguments": ["fomc_policymaker"], "description": "a1"},
      "a2": {"arguments": ["fomc_policymaker"], "description": "a2"},
      "a3": {"arguments": ["fomc_policymaker"], "description": "a3"},
      "a4": {"arguments": ["fomc_policymaker"], "description": "a4"},
      "a5": {"arguments": ["fomc_policymaker"], "description": "a5"}},
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

def case (kind : String) (environment : Json) (premises : List Json) (conclusion : Json)
    (more : List (String × Json) := []) : Json :=
  Json.mkObj ([("id", .str "c"), ("kind", .str kind), ("environment", environment),
    ("premises", Json.arr premises.toArray), ("conclusion", conclusion)] ++ more)

def answer (j : Json) : Json := runCaseReported j
def err (j : Json) : String := ((answer j).getObjValD "error").getStr?.toOption.getD ""
/-- The error of admitting one statement, alone, in `e`. -/
def refusal (formula : String) (e : Json := env) : String := err (case "admission" e [] (st formula))

/-! ## FA11: the projection and the two identities -/

/-- The decoded environment's three identities (cardinality, W6a annotated, W6a target), its projection's profiles
and its finite sorts. -/
def decoded (e : Json) : Option ((String × String × String) × List String × List String) :=
  (decodeEnvironment e).toOption.map fun w =>
    ((w.environmentId, w.w6.environmentId, w.w6.targetId), w.w6.profiles, w.env.finite)
def envId : String := ((decoded env).map (·.1.1)).getD ""
def w6Id : String := ((decoded env).map (·.1.2.1)).getD ""
def targetId : String := ((decoded env).map (·.1.2.2)).getD ""

#guard (projectW6 env).toOption.map (·.getObjValD "profiles") == some (p r#"["order@0", "relational-fol@0", "time@0"]"#)
#guard (decoded env).map (·.2) == some (["order@0", "relational-fol@0", "time@0"], ["fomc_policymaker"])
#guard envId != w6Id && envId != targetId && w6Id != targetId && envId != ""
-- With `documents@1` the projection is W6a's second list; its identity differs again.
def envDocs : Json := env.setObjVal! "profiles"
  (p r#"["cardinality@0", "documents@1", "order@0", "relational-fol@0", "time@0"]"#)
#guard (decoded envDocs).map (·.2.1) == some ["documents@1", "order@0", "relational-fol@0", "time@0"]
#guard (decoded envDocs).map (·.1.1) != some envId
-- Draft 1's E4 (the profiles kept) is refused by W6a's decoder.
#guard (VE.Time.Wire.decodeEnvironment ((VE.Time.Wire.dropFields env ["cardinality_schema", "cardinality"]).toOption.get!)
  matches .error "UnsupportedProfile: ve-units@1 requires exactly order@0, relational-fol@0 and time@0, optionally with documents@1")

/-! ## FA1: admission, the region table, the regenerated problem and a replayed certificate -/

def fa1Premises : List Json := [st r#"["count", "fomc_policymaker", [["1", ["any"]]], "eq", "18"]"#,
  st r#"["count", "fomc_policymaker", [["1", ["is", "expects_further_increase"]]], "eq", "16"]"#,
  st r#"["count", "fomc_policymaker", [["1", ["is", "expects_rates_to_stay"]]], "eq", "2"]"#,
  st r#"["quantity", ["forall", "fomc_policymaker", ["not", ["and", ["unary", "expects_further_increase", ["var", 0]],
    ["unary", "expects_rates_to_stay", ["var", 0]]]]]]"#]
def fa1Conclusion : Json := st r#"["quantity", ["forall", "fomc_policymaker", ["or",
  ["unary", "expects_further_increase", ["var", 0]], ["unary", "expects_rates_to_stay", ["var", 0]]]]]"#

def fa1Admission : Json := answer (case "admission" env fa1Premises fa1Conclusion)

-- The wire decodes exactly the core's FA1 statements.
#guard match decodeEnvironment env with
  | .ok w => (fa1Premises.mapM (decodeStatement w)).toOption.map (·.map (·.formula)) == some Examples.fa1 &&
      (decodeStatement w fa1Conclusion).toOption.map (·.formula) == some Examples.fa1Conclusion
  | .error _ => false
#guard fa1Admission.getObjValD "status" == .str "ok"
#guard ((fa1Admission.getObjValD "regions").getObjValD "constants").getArr?.toOption.map
  (·.toList.map (·.getObjValD "constant")) == some ((["00", "01", "10", "11"]).map
    fun b => .str s!"cardinality__fomc_policymaker__{b}")
#guard (fa1Admission.getObjValD "regions").getObjValD "predicates" ==
  p r#"{"fomc_policymaker": ["expects_further_increase", "expects_rates_to_stay"]}"#
-- 4 region premises, 2 bridges and the 4 erased premises.
#guard (((fa1Admission.getObjValD "erased").getObjValD "premises").getArr?.toOption.map (·.size)) == some 10
#guard (fa1Admission.getObjValD "environment_id", fa1Admission.getObjValD "w6_environment_id") ==
  (.str envId, .str w6Id)
-- The canonical formula is echoed; reordered object keys in the request are the same statement.
#guard ((fa1Admission.getObjValD "conclusion").getObjValD "formula") == (fa1Conclusion.getObjValD "formula")

/-- A trace as the order certificate wire spells it. -/
def traceJson : VE.Order.Tableau.Trace → Json
  | .close => p r#"{"rule": "close"}"#
  | .expand i _ cs => Json.mkObj [("rule", .str "expand"), ("at", toJson i),
      ("children", Json.arr (cs.attach.map fun ⟨c, _⟩ => traceJson c).toArray)]
  | .neq i cs => Json.mkObj [("rule", .str "order-neq@1"), ("at", toJson i),
      ("children", Json.arr (cs.attach.map fun ⟨c, _⟩ => traceJson c).toArray)]
  | .farkas _ f => Json.mkObj [("rule", .str "order-farkas@1"), ("cuts", Json.arr #[]),
      ("literals", Json.arr (f.literals.map fun (i, k) => Json.arr #[toJson i, .str (toString k)]).toArray),
      ("final_cuts", Json.arr #[])]
  | .split _ _ => .null

def ids (xs : Json) (field : String) : Json :=
  Json.arr ((xs.getArr?.toOption.getD #[]).map (·.getObjValD field))

/-- A certificate bound to the identities an admission answer `a` states, around `trace`. -/
def certificate (a : Json) (trace : VE.Order.Tableau.Trace) : Json :=
  let e := a.getObjValD "erased"
  Json.mkObj [("format", .str "ve-cardinality-certificate@1"), ("environment_id", a.getObjValD "environment_id"),
    ("premise_meaning_ids", ids (a.getObjValD "premises") "meaning_id"),
    ("conclusion_meaning_id", (a.getObjValD "conclusion").getObjValD "meaning_id"),
    ("w6", Json.mkObj [("format", .str "ve-quantity-certificate@1"),
      ("environment_id", a.getObjValD "w6_environment_id"),
      ("premise_meaning_ids", ids (e.getObjValD "premises") "meaning_id"),
      ("conclusion_meaning_id", (e.getObjValD "conclusion").getObjValD "meaning_id"),
      ("core", Json.mkObj [("checker_version", .str VE.Order.Tableau.checkerVersion),
        ("environment_id", a.getObjValD "w6_target_environment_id"),
        ("premise_meaning_ids", ids (e.getObjValD "premises") "core_meaning_id"),
        ("conclusion_meaning_id", (e.getObjValD "conclusion").getObjValD "core_meaning_id"),
        ("trace", traceJson trace)])])]

def certify (premises : List Json) (conclusion : Json) (cert : Json) : Json :=
  answer (case "certificate" env premises conclusion [("certificate", cert)])

#guard (certify fa1Premises fa1Conclusion (certificate fa1Admission Examples.fa1Trace)).getObjValD "valid" == .bool true

/-! ## FA1b: without the exclusion premise the same trace does not close the regenerated problem -/

def fa1bAdmission : Json := answer (case "admission" env fa1Premises.dropLast fa1Conclusion)
#guard (((fa1bAdmission.getObjValD "erased").getObjValD "premises").getArr?.toOption.map (·.size)) == some 8
#guard certify fa1Premises.dropLast fa1Conclusion (certificate fa1bAdmission Examples.fa1Trace) ==
  Json.mkObj [("id", .str "c"), ("status", .str "ok"), ("valid", .bool false),
    ("environment_id", .str envId), ("w6_environment_id", .str w6Id),
    ("w6_target_environment_id", .str targetId),
    ("premises", fa1bAdmission.getObjValD "premises"), ("conclusion", fa1bAdmission.getObjValD "conclusion")]

/-! ## FA11's binding mismatches, and a certificate for other statements -/

def fa1Cert : Json := certificate fa1Admission Examples.fa1Trace
-- The cardinality identity replaced by the projection's W6a identity.
#guard err (case "certificate" env fa1Premises fa1Conclusion
  [("certificate", fa1Cert.setObjVal! "environment_id" (.str w6Id))]) == stale
-- The W6a part naming the original environment's identity.
#guard err (case "certificate" env fa1Premises fa1Conclusion [("certificate", fa1Cert.setObjVal! "w6"
  ((fa1Cert.getObjValD "w6").setObjVal! "environment_id" (.str envId)))]) == VE.Time.Wire.staleW6
-- The core part naming the projection's annotated identity instead of its target.
#guard err (case "certificate" env fa1Premises fa1Conclusion [("certificate", fa1Cert.setObjVal! "w6"
  ((fa1Cert.getObjValD "w6").setObjVal! "core" (((fa1Cert.getObjValD "w6").getObjValD "core").setObjVal!
    "environment_id" (.str w6Id))))]) == VE.Time.Wire.staleCore
-- FA1's certificate offered for FA1b's statements.
#guard err (case "certificate" env fa1Premises.dropLast fa1Conclusion [("certificate", fa1Cert)]) == stale
#guard (err (case "certificate" env fa1Premises fa1Conclusion [("certificate", p "{}")])).startsWith
  "Invalid cardinality certificate: "
#guard (answer (case "certificate" env fa1Premises fa1Conclusion [("certificate", p "{}")])).getObjValD "valid" ==
  .bool false

/-! ## A forged region table and a forged erased problem -/

def regions : Json := fa1Admission.getObjValD "regions"
def erased : Json := fa1Admission.getObjValD "erased"
-- The regenerated ones, claimed, are accepted.
#guard (answer (case "admission" env fa1Premises fa1Conclusion [("regions", regions), ("erased", erased)])) ==
  fa1Admission
#guard err (case "admission" env fa1Premises fa1Conclusion [("regions", regions.setObjVal! "predicates"
  (p r#"{"fomc_policymaker": ["expects_rates_to_stay", "expects_further_increase"]}"#))]) ==
  "region table differs from the regenerated one"
#guard err (case "admission" env fa1Premises fa1Conclusion [("erased", erased.setObjVal! "premises"
  (Json.arr (((erased.getObjValD "premises").getArr?.toOption.getD #[]).toList.drop 1).toArray))]) ==
  "erased problem differs from the regenerated one"
#guard err (case "certificate" env fa1Premises fa1Conclusion [("certificate", fa1Cert), ("erased", p "[]")]) ==
  "erased problem differs from the regenerated one"

/-! ## FA8 and FA9 at the wire: the hostile set, each with its diagnostic -/

#guard refusal r#"["count", "user", [["1", ["is", "curious"]]], "ge", "2"]"# ==
  "Unknown cardinality operator ge"
#guard refusal r#"["count", "user", [["1", ["is", "curious"]]], "le", "2"]"# == "CardinalityNotFinite(user)"
#guard refusal r#"["count", "fomc_policymaker", [["1", ["is", "advises"]]], "le", "2"]"# ==
  "TypeMismatch: advises is not a unary predicate of sort fomc_policymaker"
#guard refusal r#"["count", "fomc_policymaker", [["1", ["not", ["is", "curious"]]]], "le", "2"]"# ==
  "TypeMismatch: curious is not a unary predicate of sort fomc_policymaker"
#guard refusal r#"["proportion", "fomc_policymaker", ["any"], ["is", "a1"], "gt", "3", "2"]"# ==
  "ProportionRange(3 in 2)"
#guard refusal r#"["proportion", "fomc_policymaker", ["any"], ["is", "a1"], "gt", "0", "0"]"# ==
  "ProportionRange(0 in 0)"
#guard refusal r#"["proportion", "fomc_policymaker", ["any"], ["is", "a1"], "gt", "-1", "2"]"# ==
  "ProportionRange(-1 in 2)"
#guard (answer (case "admission" env [] (st r#"["count", "fomc_policymaker", [["1", ["is", "a1"]]], "eq", "16"]"#)
  )).getObjValD "status" == .str "ok"
-- Seven predicates on the finite sort: admitted statement, refused problem (P2); six pass.
def seven : String := r#"["count", "fomc_policymaker", [["1", ["is", "a1"]], ["1", ["is", "a2"]], ["1", ["is", "a3"]],
  ["1", ["is", "a4"]], ["1", ["is", "a5"]], ["1", ["is", "expects_further_increase"]],
  ["1", ["is", "expects_rates_to_stay"]]], "le", "7"]"#
#guard refusal seven == "ResourceLimit: At most 6 predicates on counted sort fomc_policymaker (64 regions)"
#guard (answer (case "admission" env [] (st (seven.replace r#"["1", ["is", "a1"]], "# "")))).getObjValD "status" ==
  .str "ok"
-- 65 terms (S7); 64 pass.
def terms (n : Nat) : String :=
  "[\"count\", \"fomc_policymaker\", [" ++ ", ".intercalate (List.replicate n "[\"1\", [\"any\"]]") ++ "], \"le\", \"7\"]"
#guard refusal (terms 65) == "ResourceLimit: At most 64 terms in a count"
#guard (answer (case "admission" env [] (st (terms 64)))).getObjValD "status" == .str "ok"
-- FA9a: a declared constant with the region prefix (E8).
def colliding : Json :=
  let voc := env.getObjValD "vocabulary"
  env.setObjVal! "vocabulary" (voc.setObjVal! "constants" ((voc.getObjValD "constants").setObjVal!
    "cardinality__fomc_policymaker__0" (p r#"{"sort": "$int", "description": "five"}"#)))
#guard refusal r#"["count", "fomc_policymaker", [["1", ["any"]]], "eq", "1"]"# colliding ==
  "ReservedName: cardinality__ is reserved for region constants (cardinality__fomc_policymaker__0)"
-- FA9e: ratios of dates, of mixed tags, and an unadmitted rule.
#guard refusal r#"["rounds_to", "ties_up", ["quantity", ["const", "day", "d1"]], ["quantity", ["const", "day", "d2"]], "1"]"# ==
  "TypeMismatch: a ratio of calendar dates has no meaning; durations use elapsed_day"
#guard refusal r#"["rounds_to", "ties_up", ["quantity", ["const", "bp", "sept"]], ["quantity", ["const", "day", "d2"]], "1"]"# ==
  "TypeMismatch: UnitMismatch(bp,day)"
#guard refusal r#"["rounds_to", "down", ["quantity", ["const", "bp", "sept"]], ["quantity", ["const", "bp", "june"]], "1"]"# ==
  "UnsupportedRounding(down)"
#guard (answer (case "admission" env [] (st r#"["rounds_to", "half_even", ["quantity", ["const", "bp", "sept"]],
  ["quantity", ["const", "bp", "june"]], "1.028"]"#))).getObjValD "status" == .str "ok"
#guard (answer (case "admission" env [] (st r#"["percent_rounds_to", "ties_up",
  ["count", "fomc_policymaker", ["is", "a1"]], ["count", "fomc_policymaker", ["any"]], "0.30"]"#))).getObjValD "status" ==
  .str "ok"

/-! ## The other texts of 4.2, each once -/

#guard refusal r#"["rounds_to", "nearest", ["quantity", ["const", "bp", "sept"]], ["quantity", ["const", "bp", "june"]], "1"]"# ==
  "Unknown rounding rule nearest"
#guard refusal r#"["percent_of", ["quantity", ["const", "bp", "sept"]], ["quantity", ["const", "bp", "june"]], "1.0.5"]"# ==
  "Invalid decimal literal \"1.0.5\""
#guard refusal r#"["count", "fomc_policymaker", [["01", ["any"]]], "le", "2"]"# == "non-canonical integer"
#guard refusal r#"["count", "fomc_policymaker", [["1", ["every"]]], "le", "2"]"# == "Unknown cardinality operator every"
#guard refusal r#"["count", "fomc_policymaker", [["1", ["is"]]], "le", "2"]"# == "Invalid cardinality formula"
#guard refusal r#"["quantity", ["lt", ["const", "bp", "sept"], ["const", "day", "d1"]]]"# ==
  "TypeMismatch: UnitMismatch(bp,day)"
#guard refusal r#"["percent_of", ["quantity", ["const", "fomc_policymaker", "x"]], ["quantity", ["const", "bp", "june"]], "1"]"# ==
  "Unknown constant \"x\""
#guard err (case "admission" env [] (Json.mkObj [("format", .str "ve-cardinality@2"), ("formula", p r#"["any"]"#)])) ==
  "Unsupported cardinality format"
#guard err (case "admission" env [] ((st r#"["any"]"#).setObjVal! "Q" (p "[]"))) == "Unsupported cardinality format"
#guard err (case "count" env [] (st r#"["any"]"#)) == "unknown case kind count"

/-! ## The environment's texts, E1–E8, each once and in order -/

def envErr (e : Json) : String := err (case "admission" e [] (st r#"["count", "fomc_policymaker", [["1", ["any"]]], "eq", "1"]"#))

#guard (envErr (env.setObjVal! "extra" (p "1"))).startsWith "fields do not match"
#guard envErr (env.setObjVal! "profiles" (p r#"["order@0", "relational-fol@0", "time@0"]"#)) ==
  "UnsupportedProfile: cardinality@0 requires order@0, relational-fol@0 and time@0, optionally with documents@1"
-- E2 before E3.
#guard envErr ((env.setObjVal! "profiles" (p r#"["cardinality@0", "order@0"]"#)).setObjVal! "cardinality_schema"
  (.str "x")) == "UnsupportedProfile: cardinality@0 requires order@0, relational-fol@0 and time@0, optionally with documents@1"
#guard envErr (env.setObjVal! "cardinality_schema" (.str "ve-cardinality@2")) ==
  "UnsupportedProfile: Unsupported cardinality schema"
-- E4: W6a's own text, before E5.
#guard envErr ((env.setObjVal! "spec_revision" (.str "x")).setObjVal! "cardinality" (p "1")) ==
  "UnsupportedProfile: Unsupported specification revision"
#guard envErr (env.setObjVal! "cardinality" (p r#"{"finite_sorts": "fomc_policymaker"}"#)) ==
  "InvalidInput: cardinality.finite_sorts must be an array of sort names"
#guard envErr (env.setObjVal! "cardinality" (p r#"{"finite_sorts": [], "more": 1}"#)) ==
  "InvalidInput: cardinality.finite_sorts must be an array of sort names"
#guard envErr (env.setObjVal! "cardinality" (Json.mkObj [("finite_sorts", toJson (List.replicate 65 "nothing"))])) ==
  "ResourceLimit: At most 64 finite sorts"
#guard envErr (env.setObjVal! "cardinality" (p r#"{"finite_sorts": ["user", "fomc_policymaker", "user"]}"#)) ==
  "DuplicateDeclaration: finite sort user"
#guard envErr (env.setObjVal! "cardinality" (p r#"{"finite_sorts": ["fomc_policymaker", "users", "users"]}"#)) ==
  "UnknownSort(users)"
-- An empty list is a well-formed environment in which every count is refused.
#guard (decodeEnvironment (env.setObjVal! "cardinality" (p r#"{"finite_sorts": []}"#))).isOk

/-! ## FA13: competing faults -/

-- One node, two faults: S5 before S8; S9 before S10.
#guard refusal r#"["proportion", "user", ["any"], ["is", "curious"], "gt", "3", "2"]"# == "CardinalityNotFinite(user)"
#guard refusal r#"["rounds_to", "down", ["quantity", ["const", "bp", "sept"]], ["quantity", ["const", "day", "d1"]], "1"]"# ==
  "TypeMismatch: UnitMismatch(bp,day)"
-- Two faulty nodes: the checks loop over nodes, so the left node's later check comes first, either way round.
def badProportion : String := r#"["proportion", "fomc_policymaker", ["any"], ["is", "a1"], "gt", "3", "2"]"#
def badCount : String := r#"["count", "user", [["1", ["is", "curious"]]], "le", "2"]"#
#guard refusal s!"[\"and\", {badProportion}, {badCount}]" == "ProportionRange(3 in 2)"
#guard refusal s!"[\"and\", {badCount}, {badProportion}]" == "CardinalityNotFinite(user)"
-- An operand's fault before its node's tag mismatch.
#guard refusal r#"["rounds_to", "ties_up", ["count", "user", ["is", "curious"]], ["quantity", ["const", "bp", "sept"]], "296"]"# ==
  "CardinalityNotFinite(user)"
-- Over the size limit with an unknown operator inside: S2 first (10,002 array nodes).
#guard refusal s!"[\"and\", {terms 5000}, [\"bogus\"]]" == VE.Time.Wire.depthLimit
#guard refusal s!"[\"and\", {terms 64}, [\"bogus\"]]" == "Unknown cardinality operator bogus"
-- Problem limits (P1–P3) come after every statement: a later statement's fault comes first.
#guard err (case "admission" env [st seven] (st badCount)) == "CardinalityNotFinite(user)"

end VE.Cardinality.WireExamples
