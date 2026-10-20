import VE.Defaults.Wire
import VE.Defaults.Examples

/-! The wire answers of DF-1a's fixtures (docs/spec/defeasible.md 8.1, 5): DF-θ, the view's diagnostics, and the
`defaults-elaborate`, `defaults-coherence` and `defaults-certificate` answers of DF-α to DF-ω, each computed by
`viewOf` and `defaultsCase` on a JSON request, with the documents of `Examples.lean`.

Certificates are written here and bound to their premise list as a producer binds them (`boundJ`): `cNeeds` proves
`∀a. ¬excepted_r1(a)` from `Dflt_T`'s premise, `cStrict` proves `∀a. e → e`, and DF-γb's pair (DF-γ with r1 guarded
by `⊥`) is kept apart by its guard. Certificates of `∀a. x_required(a)` and of DF-δ's coherence premise are found by
the untrusted search (df-1b). -/
namespace VE.Defaults.WireFixtures
open Lean
open VE.Defaults VE.Defaults.Fixtures VE.Defaults.Wire
open VE.NormDefaults (fill)
open VE.Tableau.Trace

def rulesJ (rules : List String) : Json := (Json.parse ("[" ++ ",".intercalate rules ++ "]")).toOption.get!
def req (env : Json) (rules : List String) (kind : String) (more : List (String × Json) := []) : Json :=
  Json.mkObj ([("id", .str "c"), ("kind", .str kind), ("environment", env), ("norms", rulesJ rules)] ++ more)
/-- The row a case answers, or its refusal's text. -/
def answer (j : Json) : Json :=
  match (do defaultsCase (← viewOf j) "c" ((j.getObjValD "kind").getStr?.toOption.getD "") j) with
  | .ok (some a) => a
  | .ok none => .str "none"
  | .error e => .str e
def ans (j : Json) (k : String) : Json := (answer j).getObjValD k

def traceJ : VE.Tableau.Trace → Json
  | .close => Json.mkObj [("rule", .str "close")]
  | .expand i p cs => Json.mkObj ([("rule", .str "expand"), ("at", toJson i),
      ("children", Json.arr (cs.attach.map fun ⟨c, _⟩ => traceJ c).toArray)] ++
      (p.map fun s => [("parameter", Json.str s)]).getD [])
/-- A certificate of `ps ⊢ φ` bound to the source environment as `bindingOk` reads it. -/
def boundJ (env : Json) (ps : List VE.Formula) (φ : VE.Formula) (t : VE.Tableau.Trace) : Json := Id.run do
  let profiles := VE.NormDefaults.Wire.profilesOf env
  let some envJ := (VE.NormDefaults.Wire.canonicalEnvironmentJsonU env).toOption | Json.null
  let some envId := (VE.Route.Wire.environmentId profiles envJ).toOption | Json.null
  let mid := fun a => ((VE.Route.Wire.meaningId profiles envId (VE.NormDefaults.Wire.enc a)).toOption).getD ""
  Json.mkObj [("checker_version", .str "ve-tableau-checker@2"), ("environment_id", .str envId),
    ("premise_meaning_ids", toJson (ps.map mid)), ("conclusion_meaning_id", .str (mid φ)), ("trace", traceJ t)]

def model (j : Json) : Json := Json.mkObj [("model", j), ("filling", Json.mkObj [])]
def fJ (φ : VE.Formula) : Json := VE.NormDefaults.Wire.enc φ
def pairJ (m n : String) (c : Json := .null) : Json := Json.mkObj [("rules", toJson [m, n]), ("certificate", c)]
def collJ (L : VE.NormDefaults.Wire.LayeredU) (m n : String) : Json :=
  (model (modelJ L [])).setObjVal! "rules" (toJson [m, n])

def αEnv : Json := envJ [xReq, xPerm] strictSoft
def αR : List String := [ruleJ "r1" "x_required" true dfltJ]
def γR : List String := [ruleJ "r1" "x_required" true dfltJ, ruleJ "r2" "x_permitted" false dfltJ]
/-- DF-γb: DF-γ with r1 guarded by `⊥`, so the pair never collides. -/
def γbR : List String := [(ruleJ "r1" "x_required" true dfltJ).replace "[\"top\"]" "[\"bottom\"]",
  ruleJ "r2" "x_permitted" false dfltJ]
def γ'Env : Json := envJ [xReq, xPerm] operatorSoft
def γ'R : List String := [ruleJ "r1" "x_required" true dfltJ, ruleJ "r2" "x_permitted" false (dfltJ (dec := "operator"))]
def δEnv : Json := envJ [xReq, xPerm] holisticSoft
def δR : List String := [ruleJ "r1" "x_required" true (dfltJ (extra := ",\"rank\":\"safety\"")),
  ruleJ "r2" "x_permitted" false (dfltJ (extra := ",\"rank\":\"helpfulness\""))]
def βEnv : Json := envJ [xReq, xPerm, baseJ "urgent"] strictSoft
def βR : List String := [ruleJ "r1" "x_required" true (dfltJ [un "urgent"])]
def dγb : Except String VE.NormDefaults.Wire.LayeredU := layered αEnv γbR

/-! ## DF-θ and the view's diagnostics (section 5: the decoder's refusals, then 7, 1, 2, 6, 4) -/

def envW : Json := αEnv.setObjVal! "profiles"
  (toJson ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0", "weighing@0"])
-- DF-θ: the layered decoder refuses `weighing@0` on main, before diagnostic 1; diagnostic 1 on a decoded document
#guard answer (req envW αR "defaults-elaborate") == .str "UnsupportedProfile: Unsupported profile weighing@0"
#guard holds dα fun L => match viewRest (req envW αR "x") L with | .error e => e == weighingText | .ok _ => false
def rest (L : VE.NormDefaults.Wire.LayeredU) : String :=
  match viewRest (req αEnv αR "x") L with | .error e => e | .ok _ => "ok"
-- diagnostic 2: a later pack's premise names a decision; 6: two rules share a name; 4: a condition past `MAX_DEPTH`
#guard holds dα fun L => rest { L with packs := L.packs ++ [⟨"rights", .constraint, [], [], [("lim:0", exAt exc1)], []⟩] } ==
  "InvalidInput: answers that assume no exception need premises that name no decision: lim:0"
#guard holds dα fun L =>
  let D := { L.D with T := { L.D.T with nodes := L.D.T.nodes ++ L.D.T.nodes } }
  rest { L with D := D, packs := [VE.NormDefaults.Wire.softPack L.U D] } ==
    "InvalidInput: two generated default premises share the label default:exception:r1"
#guard holds dβ fun L => rest { L with D := deepen L.D, packs := [VE.NormDefaults.Wire.softPack L.U (deepen L.D)] } ==
  "ResourceLimit: generated default premise default:exception:r1"
-- `X` that does not start with the soft pack's premises: diagnostic 7's text (never on a decoded document)
#guard holds dβ fun L => rest { L with packs := [] } == notWellFormedText && rest L == "ok"

/-! ## `defaults-elaborate` (DF-γ) -/

#guard holds dγ fun L => match VE.SoftNorms.collidingPairs L.D with
  | [(P, Q)] => ans (req αEnv γR "defaults-elaborate") "default_premises" ==
      toJson ((dfltLabelled L.D).map fun (l, a) => Json.arr #[.str l, fJ a]) &&
    ans (req αEnv γR "defaults-elaborate") "coherence_targets" ==
      toJson [Json.arr #[.str "r1", .str "r2", fJ (VE.NormDefaults.Wire.cohPremiseU L.U L.D P Q)]]
  | _ => false

/-! ## `defaults-coherence`: COHERENT, COLLISION, UNKNOWN (DF-γ, DF-γ′, DF-γb, DF-ω) and diagnostic 5 -/

def pairsJ (st : String) : Json := toJson [Json.mkObj [("rules", toJson ["r1", "r2"]), ("status", .str st)]]
-- DF-γ: the collision at {} checks; the tuple Lean finds and DE7a's one decider; named reversed, it is no collision
#guard holds dγ fun L =>
  let a := answer (req αEnv γR "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2"]), ("collision", collJ L "r1" "r2")])
  a.getObjValD "verdict" == .str "COLLISION" && a.getObjValD "pairs" == pairsJ "collision" &&
  a.getObjValD "collision" == Json.mkObj [("rules", toJson ["r1", "r2"]), ("tuple", toJson ["e_assistant"]),
    ("deciders", toJson ["assistant"])] &&
  ans (req αEnv γR "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2"]), ("collision", collJ L "r2" "r1")])
    "pairs" == pairsJ "unknown"
-- DF-γ′: DE7b's two deciders, in pair order
#guard holds (layered γ'Env γ'R) fun L => (ans (req γ'Env γ'R "defaults-coherence"
  [("coherence", toJson [pairJ "r1" "r2"]), ("collision", collJ L "r1" "r2")]) "collision").getObjValD "deciders" ==
    toJson ["assistant", "operator"]
-- DF-ω: DF-δ without its pair certificate and with no collision: UNKNOWN, never COLLISION
#guard answer (req δEnv δR "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2"])]) ==
  VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN"), ("pairs", pairsJ "unknown")]
-- diagnostic 5: the pair list must be `coherence_targets`, in order
#guard [toJson ([] : List Json), toJson [pairJ "r2" "r1"], toJson [pairJ "r1" "r2", pairJ "r1" "r2"]].all fun c =>
  answer (req δEnv δR "defaults-coherence" [("coherence", c)]) == .str pairText
-- DF-γb: the pair's certificate checks (COHERENT, resolved); without it the pair is unknown. DF-α: no pair
def γbCert : Json := match dγb with
  | .ok L => match VE.SoftNorms.collidingPairs L.D with
    | [(P, Q)] => boundJ αEnv (VE.Norms.backgroundBase (fill L.U) ++ (VE.SoftNorms.excPremises L.D ++ [] ++
        dfltPremises L.D) ++ VE.NormDefaults.fillPremises L.U) (VE.NormDefaults.Wire.cohPremiseU L.U L.D P Q)
        (expand 3 none [expand 4 none [expand 5 none [expand 6 none [expand 8 none [close]]]]])
    | _ => .null
  | .error _ => .null
#guard answer (req αEnv γbR "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2" γbCert])]) ==
  VE.Route.Wire.ok "c" [("verdict", .str "COHERENT"), ("pairs", pairsJ "resolved")]
#guard answer (req αEnv γbR "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2"])]) ==
  VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN"), ("pairs", pairsJ "unknown")]
#guard answer (req αEnv αR "defaults-coherence") == VE.Route.Wire.ok "c" [("verdict", .str "COHERENT"), ("pairs", toJson ([] : List Json))]

/-! ## `defaults-certificate` (DF-α, DF-α′, DF-ζ's basis, DF-γ, DF-η, DF-ι, DF-κ) -/

/-- A `defaults-certificate` request on DF-α for `φ` with certificate trace `t` over `premisesX U (defaultX D X) []`. -/
def αCase (φ : VE.Formula) (t : Option VE.Tableau.Trace) (more : List (String × Json)) : Json := match dα with
  | .ok L => req αEnv αR "defaults-certificate" ([("premises", toJson ([] : List Json)), ("conclusion", fJ φ)] ++
      (t.map fun t => [("certificate", boundJ αEnv (ps L []) φ t)]).getD [] ++ more)
  | .error _ => .null
def αModels (strict : List String) : List (String × Json) := match dα with
  | .ok L => [("model", model (modelJ L [])), ("strict_model", model (modelJ L strict))]
  | .error _ => []
def follows (basis form : String) (as : List String) : Json :=
  VE.Route.Wire.ok "c" [("verdict", .str "FOLLOWS"), ("basis", .str basis), ("form", .str form), ("assumptions", toJson as)]
def unknownBecause (r : String) : Json := VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN"), ("reason", .str r)]

-- DF-α: FOLLOWS, needs (the strict countermodel {excepted r1} checks), short, the one exception kept
#guard answer (αCase notExc cNeeds.trace (αModels [exc1])) == follows "needs" "short" [excN "r1"]
-- DF-α′: the strict model {} does not check, or none is sent: unsettled, never needs
#guard answer (αCase notExc cNeeds.trace (αModels [])) == follows "unsettled" "short" [excN "r1"]
#guard answer (αCase notExc cNeeds.trace ((αModels [exc1]).take 1)) == follows "unsettled" "short" [excN "r1"]
-- basis strict: the certificate keeps no `Dflt_T` label
#guard answer (αCase excSelf cStrict.trace (αModels [exc1])) == follows "strict" "short" []
-- DF-κ: no certificate, or one bound to the strict kind's premise list (one premise fewer): no certificate
#guard answer (αCase notExc none (αModels [exc1])) == unknownBecause "no certificate"
#guard match dα with
  | .ok L => answer ((αCase notExc none (αModels [exc1])).setObjVal! "certificate"
      (boundJ αEnv (VE.NormDefaults.Wire.premisesX L.U L.X []) notExc cNeeds.trace)) == unknownBecause "no certificate"
  | .error _ => false
-- no model: UNKNOWN, never FOLLOWS on the certificate alone
#guard answer (αCase notExc cNeeds.trace []) == unknownBecause "no checked situation where the premises hold with no exception"
-- DF-η: diagnostic 3
#guard answer ((αCase notExc none []).setObjVal! "premises" (toJson [fJ (exAt exc1)])) ==
  .str "InvalidInput: a question that assumes no exception may state facts only; it states whether rule r1's exception applies"
-- DF-ι: DF-β with premises no situation satisfies, the empty domain included: no checked model
#guard holds dβ fun L => answer (req βEnv βR "defaults-certificate" [("premises", toJson [fJ (exAt "urgent"),
    fJ (.all "assistant" (.not (.unary "urgent" (.var 0))))]), ("conclusion", fJ xAll), ("model", model (emptyJ L))]) ==
  unknownBecause "no checked situation where the premises hold with no exception"

/-- DF-γ's gate regression: a bound certificate of `∀a. ¬excepted_r1(a)` (`Dflt_T`'s premise is index 2 of 7) and the
    empty-domain model, an accepted consistency witness; only the gate keeps the answer from FOLLOWS. -/
def γCase (collision : Bool) : Json := match dγ with
  | .ok L => req αEnv γR "defaults-certificate" ([("premises", toJson ([] : List Json)), ("conclusion", fJ notExc),
      ("certificate", boundJ αEnv (ps L []) notExc
        (expand 7 none [expand 8 none [expand 2 (some "w:0") [expand 10 none [close, close]]]])),
      ("coherence", toJson [pairJ "r1" "r2"]), ("model", model (emptyJ L))] ++
      if collision then [("collision", collJ L "r1" "r2")] else [])
  | .error _ => .null
#guard [true, false].all fun c => match (do replayCertOn (← viewOf (γCase c)) (γCase c)) with
  | .ok x => x.certOk && x.modelOk && !x.coherent
  | .error _ => false
#guard answer (γCase true) == unknownBecause "with no exception, rules r1 and r2 conflict"
#guard answer (γCase false) == unknownBecause "no-exception coherence not checked"

/-! ## Other kinds -/

#guard ["defaults-model", "defaults-other", "norm-defaults-elaborate"].all fun k =>
  answer (req αEnv αR k) == .str "none"

end VE.Defaults.WireFixtures
