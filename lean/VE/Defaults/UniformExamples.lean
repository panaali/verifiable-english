import VE.Defaults.RouteExamples
import VE.NormDefaults.PacksExamples
import VE.Defaults.MeaningExamples

/-! Fixtures F9.1 to F9.7 (docs/spec/profile-composition.md 4, plan PC-9): the two typed priority graphs, each with
its own check, and the "no exception" statements of `Defaults/Uniform.lean` with the guard of `defaultsRows`. The
packs with conditions are built by hand (no pack on main states one, `decodeLayered_conditions`). -/
namespace VE.Defaults.UniformFixtures
open Lean VE.Defaults VE.Defaults.Fixtures VE.Defaults.WireFixtures VE.Defaults.RouteFixtures
open VE.NormDefaults.Packs (Pack)
open VE.NormDefaults.Wire (LayeredU layeredKindCase decodeLayered)

/-! ## F9.1, F9.2: priority is two typed graphs, each with its owner's check -/

/-- Rule `a` over rule `b` (W1), and rank `b` outranks rank `a` (soft). -/
def abSoft : String := r#"{"ranks":["a","b"],"outranks":[["b","a"]],"outranking":{"mode":"strict"}}"#
def over (r : String) (o : String) : String := r.replace "\"over\":[]" ("\"over\":[\"" ++ o ++ "\"]")
def dAB : Except String LayeredU :=
  layered (envJ [xReq, xPerm] abSoft) [over (ruleJ "a" "x_required" true dfltJ) "b", ruleJ "b" "x_required" false dfltJ]

-- F9.1 (condition): the document is not refused, and each graph is its own check's acyclic node list
#guard holds dAB fun L =>
  VE.Norms.precedenceNodes L.D.base.T == [⟨"a", ["b"]⟩, ⟨"b", []⟩] &&
  VE.SoftNorms.rankNodes L.D.soft == [⟨"a", []⟩, ⟨"b", ["a"]⟩] &&
  (VE.Route.dependencyOrder (VE.Norms.precedenceNodes L.D.base.T)).isOk &&
  (VE.Route.dependencyOrder (VE.SoftNorms.rankNodes L.D.soft)).isOk
-- draft 1's single graph over the same strings is a cycle (stub); no route builds it
#guard match VE.Route.dependencyOrder [⟨"a", ["b"]⟩, ⟨"b", ["a"]⟩] with
  | .error e => e == "DependencyCycle: a, b" | .ok _ => false
-- `precedence_apart`: W1's nodes are the same whatever rank pairs are stated
#guard holds dAB fun L => [[], [("a", "b")], [("b", "a"), ("a", "b")]].all fun o =>
  VE.Norms.precedenceNodes ({ L.D with soft := { L.D.soft with outranks := o } } : VE.SoftNorms.SoftDoc).base.T ==
    VE.Norms.precedenceNodes L.D.base.T
-- F9.2: a cycle in one graph is refused by W1's precedence check, with its cycle diagnostic
#guard match layered (envJ [xReq, xPerm] strictSoft)
    [over (ruleJ "a" "x_required" true dfltJ) "b", over (ruleJ "b" "x_required" false dfltJ) "a"] with
  | .error e => e == "DependencyCycle: a, b" | .ok _ => false

/-! ## F9.3 to F9.7: the defaults kinds and provider conditions -/

/-- Disclosure outranks privacy, holistically; `r2` (privacy) may outweigh `r1` (disclosure) on `x_permitted`. -/
def piSoft : String :=
  r#"{"ranks":["disclosure","privacy"],"outranks":[["disclosure","privacy"]],"outranking":{"mode":"holistic","decided_by":"assistant"}}"#
def piEnv : Json := envJ [xReq, xPerm, baseJ "medical"] piSoft
def piR : List String := [ruleJ "r1" "x_required" true (dfltJ (extra := ",\"rank\":\"disclosure\"")),
  ruleJ "r2" "x_permitted" false (dfltJ (extra := ",\"rank\":\"privacy\""))]
def dπ : Except String LayeredU := layered piEnv piR
def medical : VE.Formula := .unary "medical" (.var 0)
def key : VE.SoftNorms.DecisionKey := .outweighs "x_permitted" "privacy" "disclosure"
/-- "Privacy outweighs disclosure when the data are medical": the hand-built pack of F9.3 (WG-3 does not exist). -/
def cond : List (VE.SoftNorms.DecisionKey × VE.Formula) := [(key, medical)]
def wPack (i : String) (cs : List (VE.SoftNorms.DecisionKey × VE.Formula)) : Pack :=
  ⟨i, .constraint, [], [], [("p:0", .all "assistant"
    (.implies medical (.unary (VE.SoftNorms.outweighsName "x_permitted" "privacy" "disclosure") (.var 0))))], [], cs⟩
def with_ (L : LayeredU) (p : Pack) : LayeredU := { L with packs := L.packs ++ [p] }
def askK (L : LayeredU) (p : Pack) (k : String) : Json := shown (layeredKindCase (with_ L p) "c" k (req piEnv piR k))
def refusedP : Json := .str ("error: " ++ providerRefusal)

-- F9.3: every defaults kind refuses, with `providerRefusal` and its sentence E1d
#guard holds dπ fun L => VE.NormDefaults.Wire.defaultsKinds.all fun k => askK L (wPack "weighing" cond) k == refusedP
#guard providerRefusal == "UnsupportedProfile: defaults with provider conditions is not implemented"
#guard providerE1d == "This question assumes no exception, and this document's providers state decision conditions. VE cannot check these two together yet. Nothing in this document was checked."
-- today's premises would assume "the data are never medical"; the uniform ones take the decision only where they are
#guard holds dπ fun L =>
  (dfltLabelled L.D).getLast? == some ("default:ranking:privacy:disclosure:x_permitted",
    VE.Norms.bindAll ["assistant"] (.not (VE.SoftNorms.outweighsF L.D "x_permitted" "privacy" "disclosure"))) &&
  (dfltUniformLabelled L.D (with_ L (wPack "weighing" cond)).packs).getLast? ==
    some ("default:ranking:privacy:disclosure:x_permitted", VE.Norms.bindAll ["assistant"]
      (.implies (VE.SoftNorms.outweighsF L.D "x_permitted" "privacy" "disclosure") (VE.Norms.anyF [medical])))
-- a condition on an exception or a switch is looked up by the rule's decision key
#guard holds dπ fun L =>
  packConditions [wPack "x" [(.excepted "r1", medical), (.off "r1" "user", .top), (key, .bottom)]] (.excepted "r1") ==
    [medical] && packConditions (with_ L (wPack "weighing" cond)).packs (.excepted "r1") == []

-- `leastUniform`, one branch at a time (DRI decision 2026-11-02, pc-9, item 2): a decision's least table holds at a
-- one-element situation where its stated provider condition holds, and not where it fails
open VE.Defaults.MeaningFixtures (sit a1 offOf) in
instance leastUDec (D : VE.SoftNorms.SoftDoc) (qs : List Pack) (L : LayeredU) (on : List String) (p : String)
    (vs : List Entity) : Decidable (leastUniform D qs (sit L on) p vs) := by
  unfold leastUniform; infer_instance
def dOff : Except String LayeredU := layered (envJ [xReq, xPerm, baseJ "medical"]
  r#"{"parties":["user"],"outranking":{"mode":"strict"}}"#) [ruleJ "r0" "x_required" true ",\"alterable\":[\"user\"]"]
open VE.Defaults.MeaningFixtures (sit a1 offOf) in
#guard holds dπ fun L => let qs := [wPack "w" [(.excepted "r1", medical)]]
  decide (leastUniform L.D qs (sit L ["medical"]) exc1 a1) && !decide (leastUniform L.D qs (sit L []) exc1 a1)
open VE.Defaults.MeaningFixtures (sit a1 offOf) in
#guard holds dOff fun L => let qs := [wPack "w" [(.off "r0" "user", medical)]]
  decide (leastUniform L.D qs (sit L ["medical"]) (offOf L 0) a1) &&
    !decide (leastUniform L.D qs (sit L []) (offOf L 0) a1)
open VE.Defaults.MeaningFixtures (sit a1 offOf) in
#guard holds dπ fun L => let w := VE.SoftNorms.outweighsName "x_permitted" "privacy" "disclosure"
  decide (leastUniform L.D [wPack "w" cond] (sit L ["medical"]) w a1) &&
    !decide (leastUniform L.D [wPack "w" cond] (sit L []) w a1)

-- `dfltUniformOf` reads a rule's conditions by its decision key, `decisionRule N`: a part split from `src` reads the
-- conditions stated for `src`, not for its own name (the split itself and F6.7 are PC-6's)
#guard holds dπ fun L => match L.D.T.nodes with
  | N :: _ => let P := { N with splitFrom := some "src" }
    let exc (cs : List VE.Formula) := some ("default:exception:r1",
      VE.Norms.bindAll (VE.SoftNorms.sortsOf L.D N.pred) (.implies (VE.SoftNorms.exceptedF L.D P) (VE.Norms.anyF cs)))
    (dfltUniformOf L.D [wPack "w" [(.excepted "src", medical)]] P).head? == exc [medical] &&
      (dfltUniformOf L.D [wPack "w" [(.excepted "r1", medical)]] P).head? == exc []
  | [] => false
#guard holds dOff fun L => match L.D.T.nodes with
  | N :: _ => let P := { N with splitFrom := some "src" }
    let ss := VE.SoftNorms.sortsOf L.D N.pred
    dfltUniformOf L.D [wPack "w" [(.off "src" "user", medical)]] P == [("default:switch:r0:user",
      VE.Norms.bindAll ss (.implies (VE.Norms.atom (VE.SoftNorms.offName P "user") ss) (VE.Norms.anyF [medical])))]
  | [] => false

-- F9.4: the same pack with `conditions = []` is not refused, and its premises are today's
#guard holds dπ fun L => VE.NormDefaults.Wire.defaultsKinds.all fun k =>
  askK L (wPack "weighing" []) k == shown (layeredKindCase L "c" k (req piEnv piR k)) && askK L (wPack "weighing" []) k != refusedP
#guard holds dπ fun L => dfltUniformLabelled L.D (with_ L (wPack "weighing" [])).packs == dfltLabelled L.D

-- F9.5: on every decoded source (today's `[soft]` and `[soft, rights]`) the uniform premises are `dfltPremises`, and
-- the guard never refuses: no answer on main changes
theorem decodeLayered_uniform {j : Json} {L : LayeredU} (h : decodeLayered j = .ok L) :
    dfltUniform L.D L.packs = dfltPremises L.D ∧ providerConditions L.packs = false := by
  have hc := VE.NormDefaults.Packs.Fixtures.decodeLayered_conditions h
  refine ⟨by simp only [dfltUniform, dfltPremises, dfltUniform_legacy L.D L.packs hc], ?_⟩
  simp only [providerConditions, List.any_eq_false]
  intro p hp
  simp [hc p hp]
#guard [dα, dβ, dγ, dγ', dδ, dδs, dδo, dπ, dAB].all fun d => holds d fun L =>
  dfltUniform L.D L.packs == dfltPremises L.D && !providerConditions L.packs

-- F9.6: a pack with another id is refused the same way; no produced text names `weighing`
#guard holds dπ fun L => VE.NormDefaults.Wire.defaultsKinds.all fun k => askK L (wPack "scales" cond) k == refusedP
#guard [providerRefusal, providerE1d].all fun s => (s.splitOn "weighing").length == 1

-- F9.7 (condition): asked without the flag (every other kind), the document routes as F9.4's does, byte for byte
def otherKinds : List String := ["norm-defaults-elaborate", "norm-defaults-conflict", "norm-defaults-status",
  "norm-defaults-report", "norm-defaults-gaps", "norm-defaults-certificate", "admission"]
#guard holds dπ fun L => otherKinds.all fun k =>
  askK L (wPack "weighing" cond) k == askK L (wPack "weighing" []) k && askK L (wPack "weighing" cond) k != refusedP
#guard holds dπ fun L => (askK L (wPack "weighing" cond) "norm-defaults-elaborate").getObjValD "status" == .str "ok"

end VE.Defaults.UniformFixtures
