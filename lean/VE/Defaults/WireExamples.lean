import VE.Defaults.Wire
import VE.Defaults.Examples

/-! The wire answers of DF-1a's fixtures (docs/spec/defeasible.md 8.1, 5): DF-θ, the view's diagnostics, and the
`defaults-elaborate`, `defaults-coherence`, `defaults-certificate` and `defaults-model` answers of DF-α to DF-ω, each
computed by `viewOf` and `defaultsCase` on a JSON request, with the documents of `Examples.lean`, and three more: DF-γb
(DF-γ with r1 guarded by `⊥`, so the pair is kept apart by its guard), DF-γ2 (two pairs, a two-entity tuple) and DF-γ3
(two pairs that share their second rule, one kept apart by its guard).

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
    ans (req αEnv γR "defaults-elaborate") "deciders" == toJson (decidersOf L.D) &&
    ans (req αEnv γR "defaults-elaborate") "coherence_targets" ==
      toJson [Json.arr #[.str "r1", .str "r2", fJ (VE.NormDefaults.Wire.cohPremiseU L.U L.D P Q)]]
  | _ => false

/-! ## `defaults-coherence`: COHERENT, COLLISION, UNKNOWN (DF-γ, DF-γ′, DF-γb, DF-ω) and diagnostic 5 -/

def pairsJ (st : String) : Json := toJson [Json.mkObj [("rules", toJson ["r1", "r2"]), ("status", .str st)]]
/-- The situation shown, its `x_required` gaps filled at `rows` (these fixtures leave only `x_required` unspecified). -/
def sitJ (rows : List (List String) := []) : Json :=
  Json.mkObj [("filling", Json.mkObj [("unsaid__x_required", toJson rows)])]
-- DF-γ: the collision at {} checks; the tuple Lean finds and DE7a's one decider; named reversed, it is no collision
#guard holds dγ fun L =>
  let a := answer (req αEnv γR "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2"]), ("collision", collJ L "r1" "r2")])
  a.getObjValD "verdict" == .str "COLLISION" && a.getObjValD "pairs" == pairsJ "collision" &&
  a.getObjValD "collision" == Json.mkObj [("rules", toJson ["r1", "r2"]), ("tuple", toJson ["e_assistant"]),
    ("deciders", toJson ["assistant"])] &&
  a.getObjValD "situation" == sitJ &&
  ans (req αEnv γR "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2"]), ("collision", collJ L "r2" "r1")])
    "pairs" == pairsJ "unknown"
-- df-1ac review F3: a collision naming a rule the document does not declare is refused, first or second
#guard holds dγ fun L => [("r9", "r2"), ("r1", "r9")].all fun (m, n) =>
  answer (req αEnv γR "defaults-coherence" [("collision", collJ L m n)]) ==
    .str ("InvalidInput: a collision names an undeclared rule r9")
-- the collision's filling is decoded: a table for a predicate the text settles is refused
#guard holds dγ fun L => answer (req αEnv γR "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2"]),
    ("collision", (collJ L "r1" "r2").setObjVal! "filling" (Json.mkObj [("unsaid__x_permitted", toJson ([] : List Json))]))]) ==
  .str "InvalidInput: unknown filling table unsaid__x_permitted"
-- DF-γ′: DE7b's two deciders, in pair order
#guard holds (layered γ'Env γ'R) fun L => (ans (req γ'Env γ'R "defaults-coherence"
  [("coherence", toJson [pairJ "r1" "r2"]), ("collision", collJ L "r1" "r2")]) "collision").getObjValD "deciders" ==
    toJson ["assistant", "operator"]
-- DF-ω: DF-δ without its pair certificate and with no collision: UNKNOWN, never COLLISION
#guard answer (req δEnv δR "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2"])]) ==
  VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN"), ("pairs", pairsJ "unknown")]
-- DF-δ: a collision that names the pair but does not check (the weighing decides it): UNKNOWN, the pair unknown and
-- no `collision` member
#guard holds (layered δEnv δR) fun L => answer (req δEnv δR "defaults-coherence"
  [("coherence", toJson [pairJ "r1" "r2"]), ("collision", collJ L "r1" "r2")]) ==
  VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN"), ("pairs", pairsJ "unknown")]
-- diagnostic 5: a non-empty pair list must be `coherence_targets`, in order (one pair fewer, reversed, one more)
#guard [toJson [pairJ "r2" "r1"], toJson [pairJ "r1" "r2", pairJ "r1" "r2"], toJson [pairJ "r1" "r1"]].all fun c =>
  answer (req δEnv δR "defaults-coherence" [("coherence", c)]) == .str pairText
-- df-1ac review F3: DF-ω's `[]`, `"coherence": null` and no member send no pair certificate: UNKNOWN, as `[none]`
#guard [some (toJson ([] : List Json)), some .null, none].all fun c =>
  answer (req δEnv δR "defaults-coherence" ((c.map (fun c => [("coherence", c)])).getD [])) ==
    VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN"), ("pairs", pairsJ "unknown")]
-- a pair list that is not a list is refused
#guard answer (req δEnv δR "defaults-coherence" [("coherence", .str "x")]) == .str "array expected"
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

/-- DF-γ2: DF-γ on a two-place act, with a third rule r3 against r1 whose exception the operator decides: two pairs,
    and a tuple of two entities. -/
def γ2Env : Json := envJ [regJ "x_required" "[\"assistant\",\"assistant\"]" "obligation" "unspecified"
    ",\"act\":\"{0} help {1}\",\"permission\":\"x_permitted\"",
  regJ "x_permitted" "[\"assistant\",\"assistant\"]" "permission" "allow" ",\"act\":\"{0} help {1}\""] operatorSoft
def γ2R : List String := γR ++ [ruleJ "r3" "x_permitted" false (dfltJ (dec := "operator"))]
def γ2Coll (L : VE.NormDefaults.Wire.LayeredU) (m n : String) : Json :=
  answer (req γ2Env γ2R "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2", pairJ "r1" "r3"]),
    ("collision", collJ L m n)])
#guard holds (layered γ2Env γ2R) fun L =>
  let st (a b : String) : Json := toJson [Json.mkObj [("rules", toJson ["r1", "r2"]), ("status", .str a)],
    Json.mkObj [("rules", toJson ["r1", "r3"]), ("status", .str b)]]
  let coll (n : String) (ds : List String) : Json := Json.mkObj [("rules", toJson ["r1", n]),
    ("tuple", toJson ["e_assistant", "e_assistant"]), ("deciders", toJson ds)]
  ((ans (req γ2Env γ2R "defaults-elaborate") "coherence_targets").getArr?.toOption.getD #[]).map
    (fun t => (t.getArrVal? 0 |>.toOption, t.getArrVal? 1 |>.toOption)) == #[(some (Json.str "r1"), some (Json.str "r2")), (some (Json.str "r1"), some (Json.str "r3"))] &&
  (γ2Coll L "r1" "r3").getObjValD "pairs" == st "unknown" "collision" &&
  (γ2Coll L "r1" "r3").getObjValD "collision" == coll "r3" ["assistant", "operator"] &&
  (γ2Coll L "r1" "r2").getObjValD "pairs" == st "collision" "unknown" &&
  (γ2Coll L "r1" "r2").getObjValD "collision" == coll "r2" ["assistant"]

/-- DF-γ3: r1 (guarded by `⊥`) and r2 against r3, so the pairs r1/r3 and r2/r3 share their second rule and only r2/r3
    can collide: a collision is shown on the pair it names by both rules, with that pair's tuple (review F5). -/
def γ3R : List String := [(ruleJ "r1" "x_required" true dfltJ).replace "[\"top\"]" "[\"bottom\"]",
  ruleJ "r2" "x_required" true dfltJ, ruleJ "r3" "x_permitted" false dfltJ]
def γ3Coll (L : VE.NormDefaults.Wire.LayeredU) (m n : String) : Json :=
  answer (req αEnv γ3R "defaults-coherence" [("coherence", toJson [pairJ "r1" "r3", pairJ "r2" "r3"]),
    ("collision", collJ L m n)])
#guard holds (layered αEnv γ3R) fun L =>
  let st (a b : String) : Json := toJson [Json.mkObj [("rules", toJson ["r1", "r3"]), ("status", .str a)],
    Json.mkObj [("rules", toJson ["r2", "r3"]), ("status", .str b)]]
  γ3Coll L "r2" "r3" == VE.Route.Wire.ok "c" [("verdict", .str "COLLISION"), ("pairs", st "unknown" "collision"),
    ("collision", Json.mkObj [("rules", toJson ["r2", "r3"]), ("tuple", toJson ["e_assistant"]),
      ("deciders", toJson ["assistant"])]), ("situation", sitJ)] &&
  γ3Coll L "r1" "r3" == VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN"), ("pairs", st "unknown" "unknown")]

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
  VE.Route.Wire.ok "c" [("verdict", .str "FOLLOWS"), ("basis", .str basis), ("form", .str form),
    ("assumptions", toJson as), ("deciders", toJson (["assistant"] : List String))]
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
-- the collision first, whether or not a certificate was sent
#guard answer ((γCase true).setObjVal! "certificate" .null) == unknownBecause "with no exception, rules r1 and r2 conflict"
-- DF-δ: a collision that names the pair but does not check (the weighing decides it) is never the reason
#guard holds (layered δEnv δR) fun L => answer (req δEnv δR "defaults-certificate" [("premises", toJson ([] : List Json)),
    ("conclusion", fJ notExc), ("coherence", toJson [pairJ "r1" "r2"]), ("collision", collJ L "r1" "r2")]) ==
  unknownBecause "no-exception coherence not checked"

/-- DF-β: `∀a. excepted_r1(a) → urgent(a)` uses `Dflt_T`'s premise with its stated condition (index 2 of 6). -/
def excUrgent : VE.Formula := .all "assistant" (.implies (.unary exc1 (.var 0)) (.unary "urgent" (.var 0)))
-- form long: the kept assumption has a stated condition; basis needs (the strict countermodel {excepted r1} checks)
#guard holds dβ fun L => answer (req βEnv βR "defaults-certificate" [("premises", toJson ([] : List Json)),
    ("conclusion", fJ excUrgent), ("certificate", boundJ βEnv (ps L []) excUrgent
      (expand 6 none [expand 7 none [expand 2 (some "w:0") [expand 10 none [close, expand 11 none [close, close]]]]])),
    ("model", model (modelJ L [])), ("strict_model", model (modelJ L [exc1]))]) ==
  follows "needs" "long" [excN "r1"]

/-- DF-β with the question's fact `∃a. urgent(a)` (`sent`) and a certificate of `excUrgent` bound to `ps L bound`;
    with the fact, every premise after `Dflt_T`'s moves up by one. -/
def βFact (bound sent : List VE.Formula) : Json := match dβ with
  | .ok L => req βEnv βR "defaults-certificate" [("premises", toJson (sent.map fJ)), ("conclusion", fJ excUrgent),
      ("certificate", boundJ βEnv (ps L bound) excUrgent
        (expand 7 none [expand 8 none [expand 2 (some "w:0") [expand 11 none [close, expand 12 none [close, close]]]]])),
      ("model", model (modelJ L ["urgent", exc1]))]
  | .error _ => .null
-- review F1's sweep: the certificate binds to the question's own premises
#guard answer (βFact [exAt "urgent"] [exAt "urgent"]) == follows "unsettled" "long" [excN "r1"]
-- DF-κ both ways: bound to the list with one premise added, or sent with one premise more than it is bound to
#guard answer (βFact [exAt "urgent"] []) == unknownBecause "no certificate"
#guard answer (βFact [] [exAt "urgent"]) == unknownBecause "no certificate"

/-- DF-γb on the certificate kind: `cNeeds`'s argument over DF-γb's premises and the empty-domain model, with the
    pair list `coherence`. -/
def γbCase (coherence : Json) : Json := match dγb with
  | .ok L => req αEnv γbR "defaults-certificate" [("premises", toJson ([] : List Json)), ("conclusion", fJ notExc),
      ("certificate", boundJ αEnv (ps L []) notExc
        (expand 7 none [expand 8 none [expand 2 (some "w:0") [expand 10 none [close, close]]]])),
      ("coherence", coherence), ("model", model (emptyJ L))]
  | .error _ => .null
-- the pair's certificate from `coherence` resolves the gate; without it, UNKNOWN; diagnostic 5 on this kind
#guard answer (γbCase (toJson [pairJ "r1" "r2" γbCert])) == follows "unsettled" "short" [excN "r1"]
#guard answer (γbCase (toJson [pairJ "r1" "r2"])) == unknownBecause "no-exception coherence not checked"
#guard answer (γbCase (toJson ([] : List Json))) == unknownBecause "no-exception coherence not checked"
#guard answer (γbCase (toJson [pairJ "r2" "r1" γbCert])) == .str pairText

/-! ## `defaults-model` (DF-β (i), DF-α's default model) -/

/-- A `defaults-model` request with no premises, the conclusion `φ` and the one-element situation `on`. -/
def modelCase (env : Json) (rules : List String) (L : VE.NormDefaults.Wire.LayeredU) (φ : VE.Formula)
    (on : List String) : Json :=
  req env rules "defaults-model" [("premises", toJson ([] : List Json)), ("conclusion", fJ φ), ("model", model (modelJ L on))]
def doesNotFollow (forced : List (String × Nat)) : Json := VE.Route.Wire.ok "c" [("verdict", .str "DOES-NOT-FOLLOW"),
  ("situation", sitJ), ("forced", toJson (forced.map fun (r, i) => Json.mkObj [("rule", .str r), ("condition", toJson i),
    ("tuple", toJson ["e_assistant"])]))]
-- DF-β (i): the countermodel {urgent, excepted_r1} checks, with r1's exception forced by condition 0 (`urgent`)
#guard holds dβ fun L => answer (modelCase βEnv βR L xAll ["urgent", exc1]) == doesNotFollow [("r1", 0)]
-- review F1: the question's premises are read. The same situation satisfies `∃a. urgent(a)` but not
-- `∀a. ¬urgent(a)`: UNKNOWN there, never DOES-NOT-FOLLOW
#guard holds dβ fun L => [(exAt "urgent", doesNotFollow [("r1", 0)]),
    (.all "assistant" (.not (.unary "urgent" (.var 0))), VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN")])].all
  fun (p, a) => answer ((modelCase βEnv βR L xAll ["urgent", exc1]).setObjVal! "premises" (toJson [fJ p])) == a
-- the filling is read: with `unsaid__x_required` at the assistant, `F_x_required` requires x there, so the same
-- situation (x not done) no longer checks
#guard holds dβ fun L => answer ((modelCase βEnv βR L xAll ["urgent", exc1]).setObjVal! "model" (Json.mkObj
    [("model", modelJ L ["urgent", exc1]), ("filling", Json.mkObj [("unsaid__x_required", toJson [["e_assistant"]])])])) ==
  VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN")]
-- {excepted_r1} without urgent violates `Dflt_T`, and the empty domain satisfies the conclusion: UNKNOWN, no `forced`
#guard holds dβ fun L => answer (modelCase βEnv βR L xAll [exc1]) == VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN")]
#guard holds dβ fun L => answer ((modelCase βEnv βR L xAll []).setObjVal! "model" (model (emptyJ L))) ==
  VE.Route.Wire.ok "c" [("verdict", .str "UNKNOWN")]
-- DF-α's default model {} refutes `∀a. excepted_r1(a)` with no exception forced (DE6's short form)
#guard holds dα fun L => answer (modelCase αEnv αR L (.all "assistant" (.unary exc1 (.var 0))) []) == doesNotFollow []
/-- DF-β2: r1's exception has two stated conditions (`calm`, then `urgent`), r2's one (`urgent`), at two assistants,
    both urgent and both excepted from both rules: four forced entries, in rule order, then tuple order, r1's at
    condition 1. -/
def β2Env : Json := envJ [xReq, xPerm, baseJ "urgent", baseJ "calm"] strictSoft
def β2R : List String := [ruleJ "r1" "x_required" true (dfltJ [un "calm", un "urgent"]),
  ruleJ "r2" "x_permitted" false (dfltJ [un "urgent"])]
#guard holds (layered β2Env β2R) fun L =>
  let two : Json := Json.mkObj [("complete", true),
    ("domains", Json.mkObj (L.sitVocab.sorts.map fun s => (s, toJson ["e1", "e2"]))), ("constants", Json.mkObj []),
    ("relations", Json.mkObj (L.sitVocab.predicates.map fun (p, _) =>
      (p, toJson (if ["urgent", exc1, "soft__excepted__r2"].contains p then [["e1"], ["e2"]] else ([] : List (List String))))))]
  let row (r : String) (i : Nat) (e : String) : Json :=
    Json.mkObj [("rule", .str r), ("condition", toJson i), ("tuple", toJson [e])]
  answer ((modelCase β2Env β2R L xAll []).setObjVal! "model" (model two)) == VE.Route.Wire.ok "c"
    [("verdict", .str "DOES-NOT-FOLLOW"), ("situation", sitJ), ("forced", toJson [row "r1" 1 "e1", row "r1" 1 "e2", row "r2" 0 "e1", row "r2" 0 "e2"])]

/-! ## Other kinds -/

#guard ["defaults-other", "norm-defaults-elaborate"].all fun k =>
  answer (req αEnv αR k) == .str "none"

end VE.Defaults.WireFixtures
