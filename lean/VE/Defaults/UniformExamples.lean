import VE.Defaults.Route
import VE.Defaults.WireExamples
import VE.NormDefaults.PacksExamples
import VE.Defaults.MeaningExamples

/-! Fixtures F9.1 to F9.7 (docs/spec/profile-composition.md 4, plan PC-9): the two typed priority graphs, each with
its own check, and the "no exception" statements of `Defaults/Uniform.lean` with the guard of `defaultsRows`. The
packs with conditions are built by hand (no pack on main states one, `decodeLayered_conditions`). -/
namespace VE.Defaults.UniformFixtures
open Lean VE.Defaults VE.Defaults.Fixtures VE.Defaults.WireFixtures
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
/-- A kind's answer through the table, or its refusal's text. -/
def shown (e : Except String (Option Json)) : Json :=
  match e with | .ok (some a) => a | .ok none => .str "none" | .error e => .str ("error: " ++ e)
def with_ (L : LayeredU) (p : Pack) : LayeredU := { L with packs := L.packs ++ [p] }
def askK (L : LayeredU) (p : Pack) (k : String) : Json := shown (layeredKindCase (with_ L p) "c" k (req piEnv piR k))
def refusedP : Json := .str ("error: " ++ providerRefusal)

-- F9.3: every defaults kind refuses with `providerRefusal`; E1d's text is `providerE1d`, which no route produces yet
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
-- `packConditions`: every pack, every condition stated for the key, in pack order, and none stated for another key
#guard holds dπ fun L =>
  packConditions [wPack "x" [(.excepted "r1", medical), (key, .bottom), (.excepted "r1", .top)],
      wPack "y" [(.off "r1" "user", .top), (.excepted "r1", .bottom)]] (.excepted "r1") == [medical, .top, .bottom] &&
    packConditions (with_ L (wPack "weighing" cond)).packs (.excepted "r1") == []

/-- A default rule with two stated sufficient conditions and two switches. -/
def dS : Except String LayeredU := layered (envJ [xReq, xPerm, baseJ "urgent", baseJ "calm", baseJ "medical"]
    r#"{"parties":["operator","user"],"outranking":{"mode":"strict"}}"#)
  [ruleJ "r1" "x_required" true (dfltJ [un "urgent", un "calm"] ",\"alterable\":[\"operator\",\"user\"]")]
/-- Conditions stated for the source rule `src` of a split part. -/
def srcConds : List (VE.SoftNorms.DecisionKey × VE.Formula) := [(.excepted "src", medical), (.excepted "src", .top),
  (.off "src" "operator", medical), (.off "src" "user", .top), (.off "src" "user", .bottom)]

-- `dfltUniformOf` reads a rule's conditions by its decision key, `decisionRule N`: a part split from `src` reads every
-- condition stated for `src`, beside its own sufficient conditions, and none stated for its own name (the split
-- itself and F6.7 are PC-6's)
#guard holds dS fun L => match L.D.T.nodes with
  | N :: _ => let P := { N with splitFrom := some "src" }
    let ss := VE.SoftNorms.sortsOf L.D N.pred
    let suff := (N.exception.map (·.sufficient)).getD []
    let off (π : String) (cs : List VE.Formula) := ("default:switch:r1:" ++ π,
      VE.Norms.bindAll ss (.implies (VE.Norms.atom (VE.SoftNorms.offName P π) ss) (VE.Norms.anyF cs)))
    suff.length == 2 && dfltUniformOf L.D [wPack "w" srcConds] P ==
      [("default:exception:r1", VE.Norms.bindAll ss
        (.implies (VE.SoftNorms.exceptedF L.D P) (VE.Norms.anyF (suff ++ [medical, .top])))),
       off "operator" [medical], off "user" [.top, .bottom]] &&
    dfltUniformOf L.D [wPack "w" srcConds] N == dfltOf L.D N
  | [] => false

-- `leastUniform`, one branch at a time (DRI decision 2026-11-02, pc-9, item 2): a decision's least table holds at a
-- one-element situation where one of its stated conditions holds, and not where none does, nor at another name
open VE.Defaults.MeaningFixtures (sit a1 offOf) in
instance leastUDec (D : VE.SoftNorms.SoftDoc) (qs : List Pack) (L : LayeredU) (on : List String) (p : String)
    (vs : List Entity) : Decidable (leastUniform D qs (sit L on) p vs) := by
  unfold leastUniform; infer_instance
open VE.Defaults.MeaningFixtures (sit a1 offOf) in
#guard holds dS fun L =>
  let q₁ := [wPack "w" [(.excepted "r1", .bottom), (.excepted "r1", medical)]]
  let q₂ := [wPack "w" [(.excepted "r1", medical), (.excepted "r1", .bottom)]]
  [q₁, q₂].all (fun qs => decide (leastUniform L.D qs (sit L ["medical"]) exc1 a1)) &&
  decide (leastUniform L.D [] (sit L ["urgent"]) exc1 a1) && decide (leastUniform L.D [] (sit L ["calm"]) exc1 a1) &&
  !decide (leastUniform L.D q₁ (sit L []) exc1 a1) && !decide (leastUniform L.D q₁ (sit L ["medical"]) "a" a1)
open VE.Defaults.MeaningFixtures (sit a1 offOf) in
#guard holds dS fun L => let qs := [wPack "w" [(.off "r1" "user", medical)]]
  decide (leastUniform L.D qs (sit L ["medical"]) (offOf L 1) a1) &&
    !decide (leastUniform L.D qs (sit L []) (offOf L 1) a1) &&
    !decide (leastUniform L.D qs (sit L ["medical"]) (offOf L 0) a1) &&
    !decide (leastUniform L.D qs (sit L ["medical"]) "a" a1)
open VE.Defaults.MeaningFixtures (sit a1 offOf) in
#guard holds dπ fun L => let w := VE.SoftNorms.outweighsName "x_permitted" "privacy" "disclosure"
  decide (leastUniform L.D [wPack "w" cond] (sit L ["medical"]) w a1) &&
    !decide (leastUniform L.D [wPack "w" cond] (sit L []) w a1) &&
    !decide (leastUniform L.D [wPack "w" cond] (sit L ["medical"]) "a" a1)

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
/-- Two acts, each a colliding pair under holistic outranking: two `outweighs` decisions. -/
def d2T : Except String LayeredU := layered (envJ [xReq, xPerm,
    regJ "y_required" "[\"assistant\"]" "obligation" "unspecified" ",\"act\":\"{0} do y\",\"permission\":\"y_permitted\"",
    regJ "y_permitted" "[\"assistant\"]" "permission" "allow" ",\"act\":\"{0} do y\""] piSoft)
  (piR ++ [ruleJ "r3" "y_required" true (dfltJ (extra := ",\"rank\":\"disclosure\"")),
    ruleJ "r4" "y_permitted" false (dfltJ (extra := ",\"rank\":\"privacy\""))])
#guard holds d2T fun L => (VE.SoftNorms.outweighsTriples L.D).length == 2
#guard [dα, dβ, dγ, dγ', dδ, dδs, dδo, dπ, dAB, dS, d2T].all fun d => holds d fun L =>
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

/-! ## `ConditionsExact` refuses an unbacked decision and admits F9.3's shape (sa-no-exception)

DRI decision 2026-11-02, pc9-decide-check, items 2 and 3 (the refutation of the old statement stays in
reviews/pc9-decide-check-20261102.lean). One default rule `r1` with no sufficient condition, a base predicate `c`,
nothing unspecified; its exception decision `d` and the stated condition `c(x)`. `wEx` forces `d` with no condition
behind it (`∃x d(x)`): on the base {a, b} with `c = {a}`, `d = {b}`, a default base where `dfltUniform` fails, the
least table `d = c` is admissible and no switch is on, but it is not below `d`, so `ConditionsExact` is false
(`exact_refuses`). `wImp` has F9.3's `wPack` premise `C → d`, and `ConditionsExact` holds (`exact_holds`). -/
namespace Exact
open VE.NormDefaults (UDoc)
open VE.NormDefaults.Wire (BaseAdmissibleX)
open VE.Norms (Sat)
universe u

def nc : VE.SoftNorms.SoftNode :=
  ⟨⟨"r1", "x_required", true, .top, [], []⟩, .default, none, [], some ⟨some "assistant", [], [], []⟩, false, none⟩

def Dc : VE.SoftNorms.SoftDoc where
  E.sorts := ["assistant"]
  E.constants _ := none
  E.predicates p := if p = "x_required" ∨ p = "x_permitted" ∨ p = "c" then some ["assistant"] else none
  lits := []
  soft.parties := []
  soft.ranks := []
  soft.outranks := []
  soft.ties := []
  soft.outranking := .strict
  soft.outrankingDecider := none
  soft.exceptionDecider := none
  soft.instructionOf := []
  soft.below := []
  T.regulated := [
    ⟨"x_permitted", ["assistant"], true, .permission, some "{0} do x", none⟩,
    ⟨"x_required", ["assistant"], false, .obligation, some "{0} do x", some "x_permitted"⟩]
  T.definitions := []
  T.nodes := [nc]

def Uc : UDoc := ⟨VE.SoftNorms.soften Dc, []⟩
def dcJ : Except String LayeredU :=
  layered (envJ [xReq "deny", xPerm, baseJ "c"] strictSoft) [ruleJ "r1" "x_required" true dfltJ]
def dName : String := "soft__excepted__r1"
def cC : VE.Formula := .unary "c" (.var 0)
def exD : VE.Formula := .ex "assistant" (.unary dName (.var 0))
def exC : VE.Formula := .ex "assistant" cC
def impCD : VE.Formula := .all "assistant" (.implies cC (.unary dName (.var 0)))
def wEx : Pack := ⟨"weighing", .constraint, [], [], [("p:0", exD), ("p:1", exC)], [], [(.excepted "r1", cC)]⟩
def wImp : Pack := ⟨"weighing", .constraint, [], [], [("p:0", impCD)], [], [(.excepted "r1", cC)]⟩

-- the literal is the decoded document, well-formed (`dfltUniform_sound`'s `h` and `hD`), and `assemble` takes both packs
#guard holds dcJ fun L => L.D.T == Dc.T && L.D.soft == Dc.soft && L.D.lits == Dc.lits && L.D.E.sorts == Dc.E.sorts &&
  L.U.unspec == Uc.unspec && L.U.D.T == Uc.D.T && ["x_required", "x_permitted", "c", dName, "r1"].all
    fun p => L.D.E.predicates p == Dc.E.predicates p && L.U.D.E.predicates p == Uc.D.E.predicates p
#guard VE.SoftNorms.WellFormedSoft Dc && VE.NormDefaults.WellFormedU Uc
#guard [wEx, wImp].all fun w => match VE.NormDefaults.Packs.assembleIn VE.NormDefaults.Packs.reservedPrefixes
    (VE.Norms.envAt (VE.NormDefaults.fill Uc) 0) 0 [w] with
  | .ok ps => ps.length == 1 | .error _ => false

theorem X_ex : VE.NormDefaults.Packs.X [wEx] = [exD, exC] := rfl
theorem X_imp : VE.NormDefaults.Packs.X [wImp] = [impCD] := rfl
theorem cond_ex : packConditions [wEx] (.excepted "r1") = [cC] := rfl
theorem cond_imp : packConditions [wImp] (.excepted "r1") = [cC] := rfl

theorem exceptedName_c : VE.SoftNorms.exceptedName nc = dName :=
  String.ext (by simp [VE.SoftNorms.exceptedName, VE.SoftNorms.ruleKey, VE.Readings.map_data, nc, dName])
theorem decisions_c : VE.SoftNorms.decisions Dc = [(dName, ["assistant"])] := by
  show [(VE.SoftNorms.exceptedName nc, ["assistant"])] ++ [] ++ [] = _
  rw [exceptedName_c]; rfl
theorem decisionNames_c : VE.SoftNorms.decisionNames Dc = [dName] := by simp [VE.SoftNorms.decisionNames, decisions_c]

/-- `soften Dc` with r1's exception name written out. -/
def Sc : VE.Norms.Doc where
  E := { Dc.E with predicates := fun p => if p = dName then some ["assistant"] else Dc.E.predicates p }
  lits := []
  T.regulated := Dc.T.regulated
  T.definitions := []
  T.nodes := [⟨"r1", "x_required", true, .top,
    [.or (.or (.or (.unary dName (.var 0)) .bottom) (.or (.or (.or (.or .bottom .bottom) .bottom) .bottom) .bottom)) .bottom],
    []⟩]

theorem Uc_eq : Uc = ⟨Sc, []⟩ := by
  have hE : VE.SoftNorms.envPrime Dc = Sc.E := by
    unfold VE.SoftNorms.envPrime
    rw [decisions_c]
    refine congrArg (fun f => ({ Dc.E with predicates := f } : VE.Environment)) (funext fun p => ?_)
    by_cases h : p = dName
    · subst h; rfl
    · simp [List.find?, beq_false_of_ne (Ne.symm h), h]
  have hN : Dc.T.nodes.map (VE.SoftNorms.primeNode Dc) = Sc.T.nodes := by
    show [VE.SoftNorms.primeNode Dc nc] = _
    simp only [VE.SoftNorms.primeNode, VE.SoftNorms.derivedList, VE.SoftNorms.derived, VE.SoftNorms.exceptedF,
      exceptedName_c]
    rfl
  show (⟨⟨VE.SoftNorms.envPrime Dc, [], ⟨Dc.T.regulated, [], Dc.T.nodes.map (VE.SoftNorms.primeNode Dc)⟩⟩, []⟩ :
    UDoc) = _
  rw [hE, hN]
  rfl

theorem pred_d : (VE.Norms.envAt (VE.NormDefaults.fill Uc) 0).predicates dName = some ["assistant"] := by
  rw [Uc_eq]; decide
theorem pred_cc : (VE.Norms.envAt (VE.NormDefaults.fill Uc) 0).predicates "c" = some ["assistant"] := by
  rw [Uc_eq]; decide

theorem switchesOff_c (B : VE.Structure.{u}) : SwitchesOff Dc B := by
  have h : (dfltLabelled Dc).filter (fun a => a.1.startsWith "default:switch:") = [] := by
    show [("default:exception:r1", _)].filter _ = []
    simp [VE.Defaults.MeaningFixtures.switch_π]
  unfold SwitchesOff
  rw [h]
  exact fun _ h => nomatch h

/-- Admissibility on this document: typed tables and the packs' premises (the base background and fill are empty). -/
theorem admissible_c (qs : List Pack) (S : VE.Structure.{u})
    (hrel : ∀ n vs, S.relation n vs → ∃ ss, (VE.Norms.envAt (VE.NormDefaults.fill Uc) 0).predicates n = some ss ∧
      VE.TupleTyped S ss vs) (hX : Sat S (VE.NormDefaults.Packs.X qs)) :
    BaseAdmissibleX Uc (VE.NormDefaults.Packs.X qs) S := by
  refine ⟨⟨⟨⟨fun c s h => (nomatch h), hrel⟩, ?_⟩, fun _ h => nomatch h⟩, hX⟩
  show Sat S (VE.Route.Background.literals [])
  simp [Sat, VE.Route.Background.literals, VE.Route.sortStrings, VE.Route.Background.pairs]

theorem open_rel (B : VE.Structure.{u}) (δ F : String → List B.Carrier → Prop) (n : String) (vs : List B.Carrier) :
    (withOpen Uc Dc B δ F).relation n vs ↔ if n = dName then δ n vs else B.relation n vs := by
  show (if n ∈ VE.SoftNorms.decisionNames Dc then δ n vs else if n ∈ VE.NormDefaults.unsaidNames Uc then F n vs
    else B.relation n vs) ↔ _
  rw [decisionNames_c, show VE.NormDefaults.unsaidNames Uc = [] from rfl]
  simp

/-- With `c(x)` the only stated condition, the least table is `d = c` on typed tuples. -/
theorem least_iff {qs : List Pack} (hq : packConditions qs (.excepted "r1") = [cC]) (B : VE.Structure.{u})
    (p : String) (vs : List B.Carrier) : leastUniform Dc qs B p vs ↔
      p = dName ∧ VE.TupleTyped B ["assistant"] vs ∧ cC.denote B (VE.Norms.tupleVal vs) := by
  have hc : ((nc.exception.map (·.sufficient)).getD []) ++
      packConditions qs (.excepted (VE.SoftNorms.decisionRule nc)) = [cC] := by rw [← hq]; rfl
  constructor
  · rintro (⟨N, hN, -, rfl, hvs, C, hC, hd⟩ | ⟨N, hN, π, hπ, -⟩ | ⟨t, ht, -⟩)
    · cases List.mem_singleton.mp hN
      rw [hc, List.mem_singleton] at hC
      subst hC
      exact ⟨exceptedName_c, hvs, hd⟩
    · cases List.mem_singleton.mp hN
      exact nomatch hπ
    · exact nomatch ht
  · rintro ⟨rfl, hvs, hd⟩
    exact Or.inl ⟨nc, List.mem_singleton.mpr rfl, rfl, exceptedName_c.symm, hvs, cC, by rw [hc]; simp, hd⟩

/-- The least tables keep every base typed. -/
theorem least_typed {qs : List Pack} (hq : packConditions qs (.excepted "r1") = [cC]) (B : VE.Structure.{u})
    (hrel : ∀ n vs, B.relation n vs → ∃ ss, (VE.Norms.envAt (VE.NormDefaults.fill Uc) 0).predicates n = some ss ∧
      VE.TupleTyped B ss vs) (n : String) (vs : List B.Carrier)
    (h : (withOpen Uc Dc B (leastUniform Dc qs B) B.relation).relation n vs) :
    ∃ ss, (VE.Norms.envAt (VE.NormDefaults.fill Uc) 0).predicates n = some ss ∧
      VE.TupleTyped (withOpen Uc Dc B (leastUniform Dc qs B) B.relation) ss vs := by
  have h' := (open_rel B _ _ n vs).mp h
  by_cases hn : n = dName
  · subst hn
    rw [if_pos rfl] at h'
    exact ⟨_, pred_d, (VE.Norms.tupleTyped_relation B _ _ vs).mpr ((least_iff hq B _ vs).mp h').2.1⟩
  · rw [if_neg hn] at h'
    obtain ⟨ss, hss, ht⟩ := hrel n vs h'
    exact ⟨ss, hss, (VE.Norms.tupleTyped_relation B _ _ vs).mpr ht⟩

/-- `false` is `a`, `true` is `b`: `c = {a}`, `d = {b}`. -/
def Bc : VE.Structure.{0} where
  Carrier := Bool
  domain s _ := s = "assistant"
  constant _ := none
  relation n vs := (n = "c" ∧ vs = [false]) ∨ (n = dName ∧ vs = [true])

theorem rel_d {vs : List Bool} (h : Bc.relation dName vs) : vs = [true] := by
  rcases h with ⟨h, -⟩ | ⟨-, h⟩
  · exact absurd h (by decide)
  · exact h

/-- The counterexample's base is a default base of `wEx`, and `dfltUniform` fails there (`d(b)`, not `c(b)`). -/
theorem defaultBase_c : DefaultBase Uc Dc (VE.NormDefaults.Packs.X [wEx]) Bc ∧ ¬ Sat Bc (dfltUniform Dc [wEx]) := by
  refine ⟨⟨admissible_c _ Bc (fun n vs h => ?_) ?_, switchesOff_c _, fun δ F hle hadm _ p hp vs hB => ?_⟩, fun h => ?_⟩
  · rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
    · exact ⟨_, pred_cc, rfl, trivial⟩
    · exact ⟨_, pred_d, rfl, trivial⟩
  · show ∀ φ ∈ [exD, exC], φ.denote Bc []
    simp only [List.mem_cons, List.not_mem_nil, or_false]
    rintro φ (rfl | rfl)
    · exact ⟨true, rfl, true, rfl, Or.inr ⟨rfl, rfl⟩⟩
    · exact ⟨false, rfl, false, rfl, Or.inl ⟨rfl, rfl⟩⟩
  · rw [decisionNames_c, List.mem_singleton] at hp
    subst hp
    obtain rfl := rel_d hB
    obtain ⟨v, -, w, hw, hr⟩ := hadm.2 exD (by rw [X_ex]; simp)
    obtain rfl : v = w := Option.some.inj hw
    have hδ := (open_rel Bc δ F _ _).mp hr
    rw [if_pos rfl] at hδ
    rw [← rel_d (hle dName (by rw [decisionNames_c]; simp) [v] hδ)]
    exact hδ
  · have hp := h _ (List.mem_singleton.mpr rfl)
    rw [VE.Norms.bindAll_denote_nil] at hp
    have hb : VE.TupleTyped Bc ["assistant"] [true] := ⟨rfl, trivial⟩
    have hx : (VE.SoftNorms.exceptedF Dc nc).denote Bc (VE.Norms.tupleVal [true]) :=
      (VE.Norms.atom_denote Bc _ _ (Or.inl rfl) [true] hb).mpr (by rw [exceptedName_c]; exact Or.inr ⟨rfl, rfl⟩)
    obtain ⟨C, hC, hCd⟩ := (VE.Norms.anyF_denote _ _ _).mp (hp [true] hb hx)
    obtain rfl := List.mem_singleton.mp hC
    obtain ⟨w, hw, hr⟩ := hCd
    obtain rfl : true = w := Option.some.inj hw
    rcases hr with ⟨-, h⟩ | ⟨h, -⟩
    · exact absurd (show ([true] : List Bool) = [false] from h) (by decide)
    · exact absurd h (by decide)

/-- `wEx`: the least table keeps every admissible base admissible with no switch on (the conjunct the old statement
had), and the bound refuses the document at `Bc`, so `dfltUniform_sound` says nothing of it. -/
theorem exact_refuses : (∀ B : VE.Structure.{u}, BaseAdmissibleX Uc (VE.NormDefaults.Packs.X [wEx]) B →
      ∃ F : String → List B.Carrier → Prop,
        BaseAdmissibleX Uc (VE.NormDefaults.Packs.X [wEx]) (withOpen Uc Dc B (leastUniform Dc [wEx] B) F) ∧
        SwitchesOff Dc (withOpen Uc Dc B (leastUniform Dc [wEx] B) F)) ∧ ¬ ConditionsExact.{0} Uc Dc [wEx] := by
  refine ⟨fun B hB => ?_, fun h => ?_⟩
  · obtain ⟨⟨⟨⟨-, hrel⟩, -⟩, -⟩, hX⟩ := hB
    obtain ⟨v, hv, w, hw, hr⟩ := hX exC (by rw [X_ex]; simp)
    obtain rfl : v = w := Option.some.inj hw
    refine ⟨B.relation, admissible_c _ _ (least_typed cond_ex B hrel) ?_, switchesOff_c _⟩
    have hl : leastUniform Dc [wEx] B dName [v] := (least_iff cond_ex B _ [v]).mpr ⟨rfl, ⟨hv, trivial⟩, v, rfl, hr⟩
    have hd := (open_rel B _ B.relation dName [v]).mpr (by rw [if_pos rfl]; exact hl)
    have hc := (open_rel B (leastUniform Dc [wEx] B) B.relation "c" [v]).mpr (by rw [if_neg (by decide)]; exact hr)
    rw [X_ex]
    simp only [Sat, List.mem_cons, List.not_mem_nil, or_false]
    rintro φ (rfl | rfl)
    · exact ⟨v, hv, v, rfl, hd⟩
    · exact ⟨v, hv, v, rfl, hc⟩
  · have hb := (h Bc defaultBase_c.1.1).2 dName [false]
      ((least_iff cond_ex Bc _ [false]).mpr ⟨rfl, ⟨rfl, trivial⟩, false, rfl, Or.inl ⟨rfl, rfl⟩⟩)
    exact absurd (show ([false] : List Bool) = [true] from rel_d hb) (by decide)

/-- `wImp` (F9.3's shape, premise `C → d`): `ConditionsExact` holds, so `dfltUniform_sound` applies. -/
theorem exact_holds : ConditionsExact.{u} Uc Dc [wImp] := by
  intro B hB
  obtain ⟨⟨⟨⟨-, hrel⟩, -⟩, -⟩, hX⟩ := hB
  have himp : impCD.denote B [] := hX impCD (by rw [X_imp]; simp)
  refine ⟨⟨B.relation, admissible_c _ _ (least_typed cond_imp B hrel) ?_, switchesOff_c _⟩, fun p vs h => ?_⟩
  · rw [X_imp]
    simp only [Sat, List.mem_singleton]
    rintro φ rfl v hv ⟨w, hw, hc⟩
    obtain rfl : v = w := Option.some.inj hw
    have hc' : B.relation "c" [v] := by
      have := (open_rel B (leastUniform Dc [wImp] B) B.relation "c" [v]).mp hc
      rwa [if_neg (by decide)] at this
    have hl : leastUniform Dc [wImp] B dName [v] :=
      (least_iff cond_imp B _ [v]).mpr ⟨rfl, ⟨hv, trivial⟩, v, rfl, hc'⟩
    exact ⟨v, rfl, (open_rel B _ B.relation dName [v]).mpr (by rw [if_pos rfl]; exact hl)⟩
  · obtain ⟨rfl, hvs, w, hw, hc⟩ := (least_iff cond_imp B p vs).mp h
    match vs, hvs, hw with
    | [v], ⟨hv, _⟩, hw =>
      obtain rfl : v = w := Option.some.inj hw
      obtain ⟨u, hu, hd⟩ := himp v hv ⟨v, rfl, hc⟩
      obtain rfl : v = u := Option.some.inj hu
      exact hd

/-- `dfltUniform_sound` on `wImp`: every default base takes `d` only where `c` holds. -/
theorem sound_holds (h : VE.NormDefaults.WellFormedU Uc = true) (hD : VE.SoftNorms.WellFormedSoft Dc = true)
    (B : VE.Structure.{u}) (hB : DefaultBase Uc Dc (VE.NormDefaults.Packs.X [wImp]) B) :
    Sat B (dfltUniform Dc [wImp]) :=
  dfltUniform_sound Uc h Dc rfl hD [wImp] exact_holds B hB

end Exact

end VE.Defaults.UniformFixtures
