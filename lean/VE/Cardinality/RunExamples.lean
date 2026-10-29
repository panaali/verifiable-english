import VE.Cardinality.Run
import VE.Cardinality.WireExamples

/-! Fixtures of the cardinality certificate check and case runner (docs/spec/quantities.md 4.1–4.2, 9.1: FA1's
certificate through the runner, FA1b, FA11's binding mismatches, a forged region table and erased problem, P1–P3).

Each `#guard` runs the runner on a JSON case, as the service will, and fails the build when an answer, a text or the
order of two texts changes. FA1's certificate replays the trace Python's untrusted search found
(`VE.Cardinality.Examples.fa1Trace`), bound to the identities the admission case answers. -/
namespace VE.Cardinality.RunExamples
open Lean VE.Cardinality VE.Cardinality.Wire VE.Cardinality.Run
open VE.Cardinality.WireExamples (p env st fa1Premises fa1Conclusion decoded)

def case (kind : String) (environment : Json) (premises : List Json) (conclusion : Json)
    (more : List (String × Json) := []) : Json :=
  Json.mkObj ([("id", .str "c"), ("kind", .str kind), ("environment", environment),
    ("premises", Json.arr premises.toArray), ("conclusion", conclusion)] ++ more)

def answer (j : Json) : Json := runCaseReported j
def err (j : Json) : String := ((answer j).getObjValD "error").getStr?.toOption.getD ""
def status (j : Json) : Json := (answer j).getObjValD "status"

def envId : String := ((decoded env).map (·.1.1)).getD ""
def w6Id : String := ((decoded env).map (·.1.2.1)).getD ""
def targetId : String := ((decoded env).map (·.1.2.2)).getD ""

/-! ## FA1: admission, the region table, the regenerated problem and a replayed certificate -/

def fa1Admission : Json := answer (case "admission" env fa1Premises fa1Conclusion)

#guard fa1Admission.getObjValD "status" == .str "ok"
#guard ((fa1Admission.getObjValD "regions").getObjValD "constants").getArr?.toOption.map
  (·.toList.map (·.getObjValD "constant")) == some ((["00", "01", "10", "11"]).map
    fun b => .str s!"cardinality__fomc_policymaker__{b}")
#guard (fa1Admission.getObjValD "regions").getObjValD "predicates" ==
  p r#"{"fomc_policymaker": ["expects_further_increase", "expects_rates_to_stay"]}"#
-- 4 region premises, 2 bridges and the 4 erased premises.
#guard (((fa1Admission.getObjValD "erased").getObjValD "premises").getArr?.toOption.map (·.size)) == some 10
#guard (fa1Admission.getObjValD "environment_id", fa1Admission.getObjValD "w6_environment_id",
  fa1Admission.getObjValD "w6_target_environment_id") == (.str envId, .str w6Id, .str targetId)
-- The statements' cardinality meaning ids are the decoder's; the erased problem's are W6a's own.
#guard ((fa1Admission.getObjValD "conclusion").getObjValD "meaning_id") ==
  .str (WireExamples.meaningId (fa1Conclusion.getObjValD "formula"))
#guard ((fa1Admission.getObjValD "conclusion").getObjValD "formula") == (fa1Conclusion.getObjValD "formula")
#guard ((fa1Admission.getObjValD "erased").getObjValD "conclusion").getObjValD "meaning_id" !=
  (fa1Admission.getObjValD "conclusion").getObjValD "meaning_id"
-- Golden identities: FA1's conclusion in the cardinality environment, and the regenerated conclusion and first
-- premise (a region premise) in W6a's two (annotated, core).
#guard (fa1Admission.getObjValD "conclusion").getObjValD "meaning_id" ==
  .str "cdc39856d173011b8acddc122c08690bc453f232202dd5813a65b54f5661b1c5"
#guard let e := fa1Admission.getObjValD "erased"
  ((e.getObjValD "conclusion").getObjValD "meaning_id", (e.getObjValD "conclusion").getObjValD "core_meaning_id",
    ((e.getObjValD "premises").getArr?.toOption.getD #[])[0]!.getObjValD "meaning_id") ==
  (.str "1693582034e41a1247c1992096ede677b3d42fee76465104b56d9d0836fc326f",
    .str "e038e0dd3d095b66f455c6ee7201fe3b2ed7dd76550f7912bfcd44a33335c13a",
    .str "a5e780ecae8ceccd555127a3cda629b7e732c8d3cce1d75254e49d21999d7317")
-- Golden region table and regenerated formulas: every constant's sort and bits, and the erased conclusion's and a
-- region premise's `Q` and `core` (QT-A4's search runs on these, and nothing outside Lean recomputes them).
#guard fa1Admission.getObjValD "regions" == p r#"{"predicates": {"fomc_policymaker": ["expects_further_increase",
  "expects_rates_to_stay"]}, "constants": [
  {"constant": "cardinality__fomc_policymaker__00", "sort": "fomc_policymaker", "bits": "00"},
  {"constant": "cardinality__fomc_policymaker__01", "sort": "fomc_policymaker", "bits": "01"},
  {"constant": "cardinality__fomc_policymaker__10", "sort": "fomc_policymaker", "bits": "10"},
  {"constant": "cardinality__fomc_policymaker__11", "sort": "fomc_policymaker", "bits": "11"}]}"#
#guard let e := fa1Admission.getObjValD "erased"
  let q := fun (j : Json) => (j.getObjValD "Q", j.getObjValD "core")
  let all := p r#"["forall", "fomc_policymaker", ["or", ["unary", "expects_further_increase", ["var", 0]],
    ["unary", "expects_rates_to_stay", ["var", 0]]]]"#
  (q (e.getObjValD "conclusion"), q ((e.getObjValD "premises").getArr?.toOption.getD #[])[0]!) == ((all, all),
    (p r#"["le", ["num", "dimensionless", "0"], ["const", "dimensionless", "cardinality__fomc_policymaker__00"]]"#,
     p r#"["le", ["num", "0"], ["const", "cardinality__fomc_policymaker__00"]]"#))
-- Spec 4.2's binding texts.
#guard (stale, VE.Time.Wire.staleW6, VE.Time.Wire.staleCore) ==
  ("cardinality certificate is stale or bound to different statements",
    "W6 certificate is stale or bound to different annotated statements",
    "core certificate is stale or bound to a different regenerated problem")
-- No `kind` is an admission case; another kind is refused, with no `valid`.
#guard answer ((case "admission" env fa1Premises fa1Conclusion).setObjVal! "kind" (.str "admission")) ==
  answer (Json.mkObj [("id", .str "c"), ("environment", env), ("premises", Json.arr fa1Premises.toArray),
    ("conclusion", fa1Conclusion)])
#guard answer (case "countermodel" env fa1Premises fa1Conclusion) ==
  p r#"{"id": "c", "status": "error", "error": "unknown case kind countermodel"}"#

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

def fa1Cert : Json := certificate fa1Admission Examples.fa1Trace

#guard certify fa1Premises fa1Conclusion fa1Cert ==
  Json.mkObj [("id", .str "c"), ("status", .str "ok"), ("valid", .bool true),
    ("environment_id", .str envId), ("w6_environment_id", .str w6Id), ("w6_target_environment_id", .str targetId),
    ("premises", fa1Admission.getObjValD "premises"), ("conclusion", fa1Admission.getObjValD "conclusion")]

/-! ## FA1b: without the exclusion premise the same trace does not close the regenerated problem -/

def fa1bAdmission : Json := answer (case "admission" env fa1Premises.dropLast fa1Conclusion)
#guard (((fa1bAdmission.getObjValD "erased").getObjValD "premises").getArr?.toOption.map (·.size)) == some 8
#guard certify fa1Premises.dropLast fa1Conclusion (certificate fa1bAdmission Examples.fa1Trace) ==
  Json.mkObj [("id", .str "c"), ("status", .str "ok"), ("valid", .bool false),
    ("environment_id", .str envId), ("w6_environment_id", .str w6Id), ("w6_target_environment_id", .str targetId),
    ("premises", fa1bAdmission.getObjValD "premises"), ("conclusion", fa1bAdmission.getObjValD "conclusion")]

/-! ## FA11's binding mismatches: each identity of each of the three bindings -/

def w6 : Json := fa1Cert.getObjValD "w6"
def core : Json := w6.getObjValD "core"
def withW6 (field : String) (v : Json) : Json := fa1Cert.setObjVal! "w6" (w6.setObjVal! field v)
def withCore (field : String) (v : Json) : Json := withW6 "core" (core.setObjVal! field v)
def refused (cert : Json) : String := err (case "certificate" env fa1Premises fa1Conclusion [("certificate", cert)])
def reversed (j : Json) : Json := Json.arr ((j.getArr?.toOption.getD #[]).toList.reverse.toArray)
def other : Json := .str (WireExamples.meaningId (p r#"["quantity", ["top"]]"#))

-- The cardinality identity replaced by the projection's W6a identity (FA11).
#guard refused (fa1Cert.setObjVal! "environment_id" (.str w6Id)) == stale
#guard refused (fa1Cert.setObjVal! "premise_meaning_ids" (reversed (fa1Cert.getObjValD "premise_meaning_ids"))) ==
  stale
#guard refused (fa1Cert.setObjVal! "conclusion_meaning_id" other) == stale
-- The W6a part naming the original environment's identity (FA11), its statements reordered, another conclusion.
#guard refused (withW6 "environment_id" (.str envId)) == VE.Time.Wire.staleW6
#guard refused (withW6 "premise_meaning_ids" (reversed (w6.getObjValD "premise_meaning_ids"))) == VE.Time.Wire.staleW6
#guard refused (withW6 "conclusion_meaning_id" (core.getObjValD "conclusion_meaning_id")) == VE.Time.Wire.staleW6
-- The core part naming the projection's annotated identity instead of its target, and the annotated ids.
#guard refused (withCore "environment_id" (.str w6Id)) == VE.Time.Wire.staleCore
#guard refused (withCore "premise_meaning_ids" (w6.getObjValD "premise_meaning_ids")) == VE.Time.Wire.staleCore
#guard refused (withCore "conclusion_meaning_id" (w6.getObjValD "conclusion_meaning_id")) == VE.Time.Wire.staleCore
-- FA1's certificate offered for FA1b's statements.
#guard err (case "certificate" env fa1Premises.dropLast fa1Conclusion [("certificate", fa1Cert)]) == stale
-- Not a cardinality certificate: refused with W6a's text inside, and never valid.
#guard refused (fa1Cert.setObjVal! "format" (.str "ve-quantity-certificate@1")) ==
  "Invalid cardinality certificate: Unsupported cardinality certificate format"
#guard refused (fa1Cert.setObjVal! "extra" (.str "x")) |>.startsWith "Invalid cardinality certificate: "
#guard refused w6 |>.startsWith "Invalid cardinality certificate: "
#guard refused (withW6 "format" (.str "ve-cardinality-certificate@1")) ==
  "Invalid cardinality certificate: Invalid quantity certificate: Unsupported quantity certificate format"
#guard answer (case "certificate" env fa1Premises fa1Conclusion [("certificate", p "{}")]) ==
  Json.mkObj [("id", .str "c"), ("status", .str "error"), ("error", .str (refused (p "{}"))),
    ("valid", .bool false)]

/-- A check's answer as text: its refusal, or "true" or "false". -/
def said (r : Except String Bool) : String :=
  match r with
  | .ok b => toString b
  | .error e => e

/-! ## The replay's step limit (10,000 steps), at and past it, on the decoded certificate -/

/-- FA1's decoded statements and certificate, with its trace replaced by one of `10000 + extra` steps, at most 101
children per node and two levels deep (a 10,000-child node overflows the stack of Lean on aarch64). -/
def steps (extra : Nat) : String := said do
  let w ← decodeEnvironment env
  let ps ← fa1Premises.mapM (decodeStatement w)
  let c ← decodeStatement w fa1Conclusion
  let cert ← decodeCertificate fa1Cert
  let trace := .expand 0 none (List.replicate extra .close ++
    List.replicate 99 (.expand 0 none (List.replicate 100 .close)))
  checkCertificate ps c { cert with w6.core.trace := trace }

#guard steps 1 == VE.Route.Steps.stepLimit
#guard steps 0 == "false"

/-! ## A forged region table and a forged erased problem -/

def regions : Json := fa1Admission.getObjValD "regions"
def erased : Json := fa1Admission.getObjValD "erased"
-- The regenerated ones, claimed, are accepted.
#guard answer (case "admission" env fa1Premises fa1Conclusion [("regions", regions), ("erased", erased)]) ==
  fa1Admission
#guard (certify fa1Premises fa1Conclusion fa1Cert) ==
  answer (case "certificate" env fa1Premises fa1Conclusion [("certificate", fa1Cert), ("regions", regions),
    ("erased", erased)])
#guard err (case "admission" env fa1Premises fa1Conclusion [("regions", regions.setObjVal! "predicates"
  (p r#"{"fomc_policymaker": ["expects_rates_to_stay", "expects_further_increase"]}"#))]) ==
  "region table differs from the regenerated one"
#guard err (case "admission" env fa1Premises fa1Conclusion [("erased", erased.setObjVal! "premises"
  (Json.arr (((erased.getObjValD "premises").getArr?.toOption.getD #[]).toList.drop 1).toArray))]) ==
  "erased problem differs from the regenerated one"
-- A claim the canonical writer refuses (nested past its depth) is not the regenerated one either.
#guard err (case "admission" env fa1Premises fa1Conclusion [("regions", (List.range 300).foldl
  (fun j _ => Json.arr #[j]) (.str "x"))]) == "region table differs from the regenerated one"
-- Forged claims are refused before the certificate is read, in a certificate case too.
#guard err (case "certificate" env fa1Premises fa1Conclusion [("certificate", fa1Cert), ("erased", p "[]")]) ==
  "erased problem differs from the regenerated one"
#guard err (case "certificate" env fa1Premises fa1Conclusion [("certificate", p "{}"), ("regions", erased)]) ==
  "region table differs from the regenerated one"

/-! ## P1–P3: the problem limits, at and past each bound, after every statement and before any claim -/

def obj (j : Json) (more : List (String × Json)) : Json := more.foldl (fun j kv => j.setObjVal! kv.1 kv.2) j
def vocab : Json := env.getObjValD "vocabulary"

/-- `env` with sorts `s1`…`sn` declared finite beside FOMC policymakers. -/
def sortsEnv (n : Nat) : Json :=
  let names := (List.range n).map (s!"s{·}")
  (env.setObjVal! "vocabulary" (vocab.setObjVal! "sorts" (obj (vocab.getObjValD "sorts")
    (names.map (·, p r#"{"description": "a sort"}"#))))).setObjVal! "cardinality"
    (Json.mkObj [("finite_sorts", toJson ("fomc_policymaker" :: names))])

def countAny (s : String) : Json := st s!"[\"count\", \"{s}\", [[\"1\", [\"any\"]]], \"le\", \"7\"]"

/-- A problem that counts `n` sorts: `s1`…`s(n-1)` in its premises, FOMC policymakers in its conclusion. -/
def counting (n : Nat) : Json :=
  case "admission" (sortsEnv n) (((List.range (n - 1)).map (s!"s{·}")).map countAny) (countAny "fomc_policymaker")

#guard err (counting 9) == "ResourceLimit: At most 8 counted sorts"
#guard status (counting 8) == .str "ok"
-- Two counted sorts, the conclusion's first: each has its predicates (none) and its one region constant.
#guard (answer (counting 2)).getObjValD "regions" == p r#"{"predicates": {"fomc_policymaker": [], "s0": []},
  "constants": [{"constant": "cardinality__fomc_policymaker__", "sort": "fomc_policymaker", "bits": ""},
    {"constant": "cardinality__s0__", "sort": "s0", "bits": ""}]}"#

/-- `env` with predicates `a1`…`a5` on FOMC policymakers: seven unary predicates on the finite sort. -/
def predsEnv : Json :=
  env.setObjVal! "vocabulary" (vocab.setObjVal! "predicates" (obj (vocab.getObjValD "predicates")
    ((List.range 5).map fun i => (s!"a{i + 1}", p r#"{"arguments": ["fomc_policymaker"], "description": "a"}"#))))

def mentioning (k : Nat) : Json :=
  let names := ((List.range 5).map (s!"a{· + 1}") ++ ["expects_further_increase", "expects_rates_to_stay"]).take k
  st s!"[\"count\", \"fomc_policymaker\", [{", ".intercalate (names.map (s!"[\"1\", [\"is\", \"{·}\"]]"))}], \"le\", \"7\"]"

-- Seven predicates on the finite sort: an admitted statement, a refused problem (P2); six pass. Spread over two
-- statements, they are one problem's predicates.
#guard err (case "admission" predsEnv [] (mentioning 7)) ==
  "ResourceLimit: At most 6 predicates on counted sort fomc_policymaker (64 regions)"
#guard status (case "admission" predsEnv [] (mentioning 6)) == .str "ok"
#guard err (case "admission" predsEnv [mentioning 6] (st
  r#"["count", "fomc_policymaker", [["1", ["is", "expects_rates_to_stay"]]], "le", "7"]"#)) ==
  "ResourceLimit: At most 6 predicates on counted sort fomc_policymaker (64 regions)"
-- P1 before P2: nine sorts, one of them with seven predicates.
#guard err (case "admission" (obj (sortsEnv 9) [("vocabulary", predsEnv.getObjValD "vocabulary" |>.setObjVal! "sorts"
  ((sortsEnv 9).getObjValD "vocabulary" |>.getObjValD "sorts"))]) (((List.range 8).map (s!"s{·}")).map countAny)
  (mentioning 7)) == "ResourceLimit: At most 8 counted sorts"

/-- Six predicates (64 regions) and `n` terms, each a sum of all 64 region constants after erasure. -/
def wide (n : Nat) : Json :=
  st s!"[\"count\", \"fomc_policymaker\", [{", ".intercalate
    ((List.replicate n "[\"1\", [\"any\"]]") ++ ((List.range 5).map (s!"[\"1\", [\"is\", \"a{· + 1}\"]]")) ++
      ["[\"1\", [\"is\", \"expects_further_increase\"]]"])}], \"le\", \"7\"]"

/-- The erased problem's node count, as W6a's aggregate limit counts it. -/
def erasedNodes (ps : List Json) (c : Json) : Nat :=
  match (do
      let w ← decodeEnvironment predsEnv
      let ps ← ps.mapM (decodeStatement w)
      let c ← decodeStatement w c
      pure ((erasedProblem w.env (ps.map (·.formula)) c.formula).2 :: (erasedProblem w.env (ps.map (·.formula))
        c.formula).1) : Except String _) with
  | .ok qs => (qs.map (VE.Order.Wire.formulaNodes ·.erase)).foldl (· + ·) 0
  | .error _ => 0

def top : Json := st r#"["quantity", ["top"]]"#
/-- `wide 58` and `k` premises "top" (one node each): the erased problem has 10,000 nodes at `k = 10000 - base`. -/
def base : Nat := erasedNodes [] (wide 58)
#guard base < 10000 && erasedNodes [top] (wide 58) == base + 1
#guard erasedNodes (List.replicate (10000 - base) top) (wide 58) == 10000
#guard status (case "admission" predsEnv (List.replicate (10000 - base) top) (wide 58)) == .str "ok"
#guard err (case "admission" predsEnv (List.replicate (10001 - base) top) (wide 58)) == VE.Time.Wire.aggregateLimit
-- P3 is checked before a certificate is read, and `checkCertificate` checks it again.
#guard err (case "certificate" predsEnv (List.replicate (10001 - base) top) (wide 58) [("certificate", p "{}")]) ==
  VE.Time.Wire.aggregateLimit
#guard said (do
    let w ← decodeEnvironment predsEnv
    let ps ← (List.replicate (10001 - base) top).mapM (decodeStatement w)
    checkCertificate ps (← decodeStatement w (wide 58)) (← decodeCertificate fa1Cert)) == VE.Time.Wire.aggregateLimit
-- P3 is charged as the problem is built (`chargedNodes`). A 64-term count erases to over 8,000 nodes, 64 times its
-- terms' source, and one of them is admitted; 200 of them (1.6 million erased nodes) stop after two, past the limit,
-- with W6a's text.
def anyCount : Json :=
  st s!"[\"count\", \"fomc_policymaker\", [{", ".intercalate (List.replicate 64 "[\"1\", [\"any\"]]")}], \"le\", \"7\"]"
def charged (ps : List Json) (c : Json) : Nat :=
  match (do
      let w ← decodeEnvironment predsEnv
      pure (chargedNodes w.env ((← ps.mapM (decodeStatement w)).map (·.formula)) (← decodeStatement w c).formula) :
      Except String Nat) with
  | .ok n => n
  | .error _ => 0
#guard erasedNodes [mentioning 6, anyCount] top - erasedNodes [mentioning 6] top > 8000
#guard status (case "admission" predsEnv [mentioning 6, anyCount] top) == .str "ok"
#guard charged [mentioning 6, anyCount] top == erasedNodes [mentioning 6, anyCount] top
#guard let n := charged (mentioning 6 :: List.replicate 200 anyCount) top; 10000 < n && n < 20000
#guard err (case "admission" predsEnv (mentioning 6 :: List.replicate 200 anyCount) top) == VE.Time.Wire.aggregateLimit
-- A statement's own fault comes before the problem's limits.
#guard err (case "admission" predsEnv [mentioning 7] (st r#"["count", "user", [["1", ["any"]]], "le", "2"]"#)) ==
  "CardinalityNotFinite(user)"

/-! ## The plan's seeded bug, at the runner: a count over a sort not declared finite is refused -/

#guard err (case "admission" env [] (st r#"["count", "user", [["1", ["is", "curious"]]], "le", "2"]"#)) ==
  "CardinalityNotFinite(user)"

end VE.Cardinality.RunExamples
