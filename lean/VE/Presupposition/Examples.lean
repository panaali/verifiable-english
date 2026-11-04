import VE.Presupposition.Rows
import VE.Discourse.Descriptions
import VE.Finite

/-! # Formula-level fixtures (docs/spec/presupposition.md 7.1, 7.2)

Rows "4.1" (builders), "4.2" (`locate`, `cls`), S2, S3, S4, S5, S9 and S21 (frame and goal
values in each listed model), the shallow-frame class facts used by S12 and S25-S27, and the
readings and rows of 4.3 and 4.4: S1 and its definedness row, S12, S13, S16, S20, S23, S24, S25,
and S26's whole-unit values. Each `pre` and `strong` is built by `definite`, `plural` or
`generic`; a guard beside each pins it to the literal formula (`definite 0`'s are discourse's
`uniqueD` and `assertive`, `plural`'s are `∃x:σ D` and `∃x:σ D ∧ ∀x:σ (D → P)`). -/
namespace VE.Presupposition.Examples
open VE.Presupposition

def model (doms : List (String × List String)) (rels : List (String × List (List String)))
    (consts : List (String × String)) : VE.FiniteModel String where
  domains s := ((doms.find? (fun x => x.1 == s)).map (·.2)).getD []
  constants c := (consts.find? (fun x => x.1 == c)).map (·.2)
  relations p := ((rels.find? (fun x => x.1 == p)).map (·.2)).getD []

def ev (M : VE.FiniteModel String) (a : VE.Formula) : Bool := a.eval M []

def owner : VE.Formula := .unary "owner" (.var 0)
def ready : VE.Formula := .unary "ready" (.var 0)
def busy : VE.Formula := .unary "busy" (.var 0)
def manager : VE.Formula := .unary "manager" (.var 0)
def rOwner : Reading := definite 0 "entity" owner ready
def rManager : Reading := definite 0 "entity" manager busy
def theOwnerU : VE.Formula := rOwner.pre
def theOwner : VE.Formula := rOwner.strong
def theManager : VE.Formula := rManager.strong

-- 4.1: `definite 0`'s `pre` and `strong` are discourse's formulas; the weakening skips index 1, also under a binder.
#guard theOwnerU == VE.Discourse.uniqueD "entity" owner
#guard theOwner == VE.Discourse.assertive "entity" owner ready
#guard theManager == VE.Discourse.assertive "entity" manager busy
#guard rOwner.weak == VE.Discourse.presupposed "entity" owner ready
#guard VE.Discourse.raise1 1 (.binary "request_in" (.var 0) (.var 1)) == .binary "request_in" (.var 0) (.var 2)
#guard VE.Discourse.raise1 0 (.binary "request_in" (.var 0) (.var 1)) == .binary "request_in" (.var 0) (.var 1)
#guard VE.Discourse.raise1 1 (.ex "entity" (.binary "r" (.var 1) (.var 2))) ==
  .ex "entity" (.binary "r" (.var 1) (.var 3))
#guard VE.Discourse.raise1 2 (.binary "r" (.var 1) (.var 2)) == .binary "r" (.var 2) (.var 3)
#guard VE.Discourse.uniqueOpen 1 "entity" (.binary "r" (.var 0) (.var 1)) ==
  VE.Discourse.uniqueAt "entity" (.binary "r" (.var 0) (.var 1)) (.binary "r" (.var 0) (.var 2))
#guard VE.Discourse.assertiveOpen 1 "entity" (.binary "r" (.var 0) (.var 1)) ready ==
  VE.Discourse.assertiveAt "entity" (.binary "r" (.var 0) (.var 1)) (.binary "r" (.var 0) (.var 2)) ready

-- 4.2: `locate` inverts `plug`; the classes, through quantifiers and conjuncts.
#guard Frame.locate (.not theOwner) [0] == some (.notF .hole, theOwner)
#guard Frame.locate (.or theOwner theManager) [1] == some (.orR theOwner .hole, theManager)
#guard Frame.locate theOwner [2] == none
#guard (Frame.notF .hole).cls == .negated
#guard (Frame.allF "entity" (.andR .top (.impR .top .hole))).cls == .consequent
#guard (Frame.orL .hole .top).cls == .disjunct
#guard [Frame.hole, .exF "entity" (.andL (.impL .hole .top) .top), .orR .top .hole].map Frame.cls ==
  [.top, .antecedent, .disjunct]
#guard (Frame.allF "a" (.exF "b" (.andR .top .hole))).binders == ["b", "a"]
#guard (Frame.allF "a" (.exF "b" (.allF "c" .hole))).binders == ["c", "b", "a"]
#guard (Frame.allF "a" (.exF "b" (.andR .top .hole))).plug .bottom == .all "a" (.ex "b" (.and .top .bottom))
#guard (Frame.exF "a" (.orR .top (.impR .top .hole))).close .bottom == .all "a" .bottom

-- S2: a conditional's antecedent gives the goal `U → U`, true in every model.
def mgrOf : VE.Formula := .binary "manager_of" (.var 0) (.const "alice")
def rMgr : Reading := definite 0 "entity" mgrOf ready
def theMgrU : VE.Formula := rMgr.pre
def theMgr : VE.Formula := rMgr.strong
#guard theMgrU == VE.Discourse.uniqueD "entity" mgrOf && theMgr == VE.Discourse.assertive "entity" mgrOf ready
def mAliceNone : VE.FiniteModel String := model [("entity", ["alice", "m1", "m2"])] [] [("alice", "alice")]
def mAliceOne : VE.FiniteModel String :=
  model [("entity", ["alice", "m1", "m2"])] [("manager_of", [["m1", "alice"]]), ("ready", [["m1"]])]
    [("alice", "alice")]
def mAliceTwo : VE.FiniteModel String :=
  model [("entity", ["alice", "m1", "m2"])] [("manager_of", [["m1", "alice"], ["m2", "alice"]])]
    [("alice", "alice")]
#guard Frame.locate (.implies theMgrU theMgr) [1] == some (Frame.impR theMgrU .hole, theMgr)
#guard (Frame.impR theMgrU .hole).goal theMgrU == .implies theMgrU theMgrU
#guard [mAliceNone, mAliceOne, mAliceTwo].map (fun M => ev M ((Frame.impR theMgrU .hole).goal theMgrU)) ==
  [true, true, true]
#guard [mAliceNone, mAliceOne, mAliceTwo].map (fun M => (ev M theMgrU, ev M theMgr)) ==
  [(false, false), (true, true), (false, false)]
example (S : VE.Structure) (ρ : VE.Valuation S) : ((Frame.impR theMgrU .hole).goal theMgrU).denote S ρ :=
  (goal_denote _ _ S ρ).mpr fun _ h => h.2 ▸ h.1

-- S3: "Alice's manager is not ready.": the goal passes the negation, S1's goal.
#guard Frame.locate (.not theMgr) [0] == some (.notF .hole, theMgr)
#guard (Frame.notF .hole).goal theMgrU == Frame.hole.goal theMgrU

-- S4: the right disjunct gains the left one's negation (M1 drops it: false where Alice has no manager).
def rPl : Reading := plural "entity" mgrOf ready
def thePlU : VE.Formula := rPl.pre
def thePl : VE.Formula := rPl.strong
#guard thePlU == .ex "entity" mgrOf && thePl == .and (.ex "entity" mgrOf) (.all "entity" (.implies mgrOf ready))
def noMgr : VE.Formula := .not (.ex "entity" mgrOf)
def f4 : Frame := .orR noMgr .hole
#guard Frame.locate (.or noMgr thePl) [1] == some (f4, thePl)
#guard f4.goal thePlU == .implies (.not noMgr) (.ex "entity" mgrOf)
#guard [mAliceNone, mAliceOne].map (fun M => ev M (f4.goal thePlU)) == [true, true]
#guard !ev mAliceNone (.implies noMgr (.ex "entity" mgrOf))

-- S5: the restrictor proves the goal (a); without it the goal fails (b); `ex` closes universally (c).
def person : VE.Formula := .unary "person" (.var 0)
def mgrOfX : VE.Formula := .binary "manager_of" (.var 0) (.var 1)
def rTheir : Reading := plural "entity" mgrOfX (.binary "trusts" (.var 1) (.var 0))
def theirU : VE.Formula := rTheir.pre
def their : VE.Formula := rTheir.strong
#guard theirU == .ex "entity" mgrOfX &&
  their == .and theirU (.all "entity" (.implies mgrOfX (.binary "trusts" (.var 1) (.var 0))))
def f5a : Frame := .allF "entity" (.impR (.and person theirU) .hole)
def f5b : Frame := .allF "entity" (.impR person .hole)
def f5c : Frame := .exF "entity" (.andR person .hole)
def m5 : VE.FiniteModel String :=
  model [("entity", ["p1", "p2", "m"])]
    [("person", [["p1"], ["p2"]]), ("manager_of", [["m", "p1"]]), ("trusts", [["p1", "m"]])] []
#guard f5a.goal theirU == .all "entity" (.implies (.and person theirU) theirU)
#guard ev m5 (f5a.goal theirU) && !ev m5 (f5b.goal theirU)
#guard f5c.goal theirU == f5b.goal theirU
#guard ev m5 (f5c.plug their) && !ev m5 (f5c.goal theirU)

-- S9: the right conjunct does not filter (incremental local context): the goal is `U`, not `U → U`.
#guard Frame.locate (.and theMgr theMgrU) [0] == some (Frame.andL .hole theMgrU, theMgr)
#guard (Frame.andL .hole theMgrU).goal theMgrU == theMgrU
#guard !ev mAliceNone ((Frame.andL .hole theMgrU).goal theMgrU)

-- S21: "If the shop is open, then the owner is ready.": goal `open(shop) → U`, F T T.
def isOpen : VE.Formula := .unary "open" (.const "shop")
def consF : Frame := .impR isOpen .hole
def shopOpenNoOwner : VE.FiniteModel String :=
  model [("entity", ["shop", "a"])] [("open", [["shop"]])] [("shop", "shop")]
def shopClosed : VE.FiniteModel String := model [("entity", ["shop", "a"])] [] [("shop", "shop")]
def shopOpenOwnerReady : VE.FiniteModel String :=
  model [("entity", ["shop", "a"])] [("open", [["shop"]]), ("owner", [["a"]]), ("ready", [["a"]])] [("shop", "shop")]
#guard Frame.locate (.implies isOpen theOwner) [1] == some (consF, theOwner)
#guard consF.goal theOwnerU == .implies isOpen theOwnerU
#guard [shopOpenNoOwner, shopClosed, shopOpenOwnerReady].map (fun M => ev M (consF.goal theOwnerU)) ==
  [false, true, true]
#guard [shopOpenNoOwner, shopClosed, shopOpenOwnerReady].map (fun M => ev M (assertedAt consF rOwner)) ==
  [false, true, true]
#guard [shopOpenNoOwner, shopClosed, shopOpenOwnerReady].map (fun M => ev M (conditionedAt consF rOwner)) ==
  [true, true, true]

-- S12, S25-S27: `not ·` and a root antecedent are shallow; the other negated frames are not.
#guard decide (Frame.notF .hole).shallow && decide (Frame.impL .hole .top).shallow
#guard [Frame.notF (.notF .hole), .notF (.andL .hole .top), .notF (.orL .hole .top), .andL (.notF .hole) .top].all
  (fun f => f.cls == .negated && !decide f.shallow)
-- the seven classes are distinct; `cls` gives no rule class (PS-2a's rule positions give `ruleAct` and `ruleGuard`)
def allClasses : List PositionClass := [.top, .negated, .antecedent, .consequent, .disjunct, .ruleAct, .ruleGuard]
#guard allClasses.eraseDups.length == 7
#guard !decide Frame.hole.shallow && !decide (Frame.impR .top .hole).shallow &&
  !decide (Frame.impL (.notF .hole) .top).shallow


/-! ## 4.3 and 4.4: readings, root carriers, `carried` and the rows -/

def mNone : VE.FiniteModel String := model [("entity", ["a"])] [] []
def mOne : VE.FiniteModel String := model [("entity", ["a"])] [("owner", [["a"]]), ("ready", [["a"]])] []
def mOneUnready : VE.FiniteModel String := model [("entity", ["a"])] [("owner", [["a"]])] []
def mTwoOneUnready : VE.FiniteModel String :=
  model [("entity", ["a", "b"])] [("owner", [["a"], ["b"]]), ("ready", [["a"]])] []
def mTwoReady : VE.FiniteModel String :=
  model [("entity", ["a", "b"])] [("owner", [["a"], ["b"]]), ("ready", [["a"], ["b"]])] []
def s1Models : List (VE.FiniteModel String) := [mNone, mOne, mOneUnready, mTwoOneUnready, mTwoReady]

-- S1 (definedness), `DefinedAt` both directions: true with both sides true in one; false through `U` in none;
-- false through weak in one-unready.
#guard ev mOne theOwner && ev mOne theOwnerU && ev mOne rOwner.weak
#guard !ev mNone theOwner && !ev mNone theOwnerU && ev mNone rOwner.weak
#guard !ev mOneUnready theOwner && ev mOneUnready theOwnerU && !ev mOneUnready rOwner.weak
#guard s1Models.all (fun M => ev M rOwner.strong == (ev M rOwner.pre && ev M rOwner.weak))

-- S1, S13: asserted `U ∧ strong` F T F F F; conditioned `U → strong` T T F T T; weak in two-one-unready F.
#guard s1Models.map (fun M => ev M (assertedAt .hole rOwner)) == [false, true, false, false, false]
#guard s1Models.map (fun M => ev M (conditionedAt .hole rOwner)) == [true, true, false, true, true]
#guard !ev mTwoOneUnready rOwner.weak
-- `carriers_on_goal`, true side (S1 one): asserted = conditioned = weak = T.
#guard ev mOne (assertedAt .hole rOwner) && ev mOne (conditionedAt .hole rOwner) &&
  ev mOne (inPlaceAt .hole rOwner) && ev mOne (Frame.hole.plug rOwner.weak)

-- S12 (`not ·`, shallow) over none, one, one-unready, two-one-unready.
def negF : Frame := .notF .hole
def s12Models : List (VE.FiniteModel String) := [mNone, mOne, mOneUnready, mTwoOneUnready]
#guard s12Models.map (fun M => ev M (assertedAt negF rOwner)) == [false, false, true, false]
#guard s12Models.map (fun M => ev M (conditionedAt negF rOwner)) == [true, false, true, true]
#guard s12Models.map (fun M => ev M (inPlaceAt negF rOwner)) == [true, false, true, true]
-- draft 1's local carriers at none: "asserted" `¬strong` T, "conditioned" `¬weak` F
#guard ev mNone (negF.plug rOwner.strong) && !ev mNone (negF.plug rOwner.weak)
-- `plug_congr`, `collapse`: both plugs F in one, both T in one-unready (`U` holds in both)
#guard !ev mOne (negF.plug rOwner.strong) && !ev mOne (negF.plug rOwner.weak)
#guard ev mOneUnready (negF.plug rOwner.strong) && ev mOneUnready (negF.plug rOwner.weak)
-- `carriers_on_goal`, false side (S12 one): asserted = conditioned = in place = weak plug = F.
#guard !ev mOne (assertedAt negF rOwner) && !ev mOne (conditionedAt negF rOwner) &&
  !ev mOne (inPlaceAt negF rOwner) && !ev mOne (negF.plug rOwner.weak)
-- `inPlace_iff_conditioned_shallow`, true side: the whole unit, in place and conditioned, T F T T alike.
def unitAt (f : Frame) (m : Root) : VE.Formula := carried [(m, f.goal rOwner.pre)] (f.plug rOwner.strong)
#guard unitAt negF .bare == inPlaceAt negF rOwner && unitAt negF .conditioned == conditionedAt negF rOwner
#guard s12Models.map (fun M => ev M (unitAt negF .bare)) == [true, false, true, true] &&
  s12Models.map (fun M => ev M (unitAt negF .conditioned)) == [true, false, true, true]

-- S25 (`not (not ·)`, negated, not shallow): in place F, conditioned T at none: the false side.
def negNegF : Frame := .notF (.notF .hole)
#guard negNegF.cls == .negated && !decide negNegF.shallow
#guard !ev mNone (inPlaceAt negNegF rOwner) && ev mNone (conditionedAt negNegF rOwner)
#guard !ev mNone (unitAt negNegF .bare) && ev mNone (unitAt negNegF .conditioned)

-- S26's whole unit (`generic`): `B = ¬¬(q ∧ ⊤)`, the inner conditioned on `p`; with `p` false the outer's
-- in place `p → B` is T and its asserted `q ∧ (p → B)` is F.
def pAtom : VE.Formula := .unary "p" (.const "c")
def q26 : VE.Formula := .and pAtom .top
def b26 : VE.Formula := .not (.not (.and q26 .top))
def m26 : VE.FiniteModel String := model [("entity", ["c"])] [] [("c", "c")]
#guard Frame.locate b26 [0, 0] == some (negNegF, (generic q26 .top).strong)
#guard Frame.locate b26 [0, 0, 0] == some (.notF (.notF (.andL .hole .top)), (generic pAtom .top).strong)
#guard ev m26 (carried [(.bare, q26), (.conditioned, pAtom)] b26) &&
  !ev m26 (carried [(.asserted, q26), (.conditioned, pAtom)] b26)

-- S16: "The owner is ready, or the manager is busy." (owner asserted, manager conditioned).
def b16 : VE.Formula := .or theOwner theManager
def gOwner : VE.Formula := (Frame.orL .hole theManager).goal rOwner.pre
def gManager : VE.Formula := (Frame.orR theOwner .hole).goal rManager.pre
def ms16 : List (Root × VE.Formula) := [(.asserted, gOwner), (.conditioned, gManager)]
def u16 : VE.Formula := carried ms16 b16
def wrong16 : VE.Formula := .implies gManager (.and gOwner b16)
#guard u16 == .and gOwner (.implies gManager b16)
def kNeither : VE.FiniteModel String := model [("entity", ["a"])] [] []
def kOwner : VE.FiniteModel String := model [("entity", ["a"])] [("owner", [["a"]]), ("ready", [["a"]])] []
def kOwnerOnly : VE.FiniteModel String := model [("entity", ["a"])] [("owner", [["a"]])] []
def kBothFalse : VE.FiniteModel String := model [("entity", ["a", "b"])] [("owner", [["a"]]), ("manager", [["b"]])] []
def s16Models : List (VE.FiniteModel String) := [kNeither, kOwner, kOwnerOnly, kBothFalse]
-- `carried_denote`: F T T F (neither: an asserted goal fails; unready owner, idle manager: goals hold, `B` fails)
#guard s16Models.map (fun M => ev M u16) == [false, true, true, false]
#guard s16Models.map (fun M => (ev M gOwner, ev M gManager, ev M b16)) ==
  [(false, false, false), (true, true, true), (true, false, false), (true, true, false)]
-- M4's nesting (conditions outside the asserted goals) is T in neither
#guard ev kNeither wrong16 && !ev kNeither u16
-- `carried_conditioned_off` (manager's goal off): unready owner, no manager: unit T = owner's goal T;
-- neither: unit F = owner's goal F.
#guard !ev kOwnerOnly gManager && ev kOwnerOnly u16 && ev kOwnerOnly gOwner
#guard !ev kNeither gManager && !ev kNeither u16 && !ev kNeither gOwner
-- `carried_on_goals` (every non-bare goal holds): one ready owner: unit T = `B` T;
-- unready owner, idle manager: unit F = `B` F.
def s16Tied : List (VE.FiniteModel String) := [kOwner, kBothFalse]
#guard s16Tied.all (fun M => ev M gOwner && ev M gManager) && ev kOwner u16 && ev kOwner b16
#guard ev kBothFalse gOwner && ev kBothFalse gManager && !ev kBothFalse u16 && !ev kBothFalse b16
-- `carried_idle`: the manager's goal bare or conditioned alike where its failure gives `B` (it holds there);
-- in unready owner, no manager its failure does not give `B`, and the two differ
def u16bare : VE.Formula := carried [(.asserted, gOwner), (.bare, gManager)] b16
#guard s16Tied.all (fun M => ev M u16bare == ev M u16) && !ev kOwnerOnly u16bare && ev kOwnerOnly u16

-- `peel_carried`: two asserted, one conditioned, a bare one ignored; one binder fewer peels too little.
def ms3 : List (Root × VE.Formula) := [(.asserted, gOwner), (.bare, .top), (.conditioned, gManager), (.asserted, .top)]
#guard carried ms3 b16 == .and gOwner (.and .top (.implies gManager b16))
#guard peel 1 1 u16 == some b16 && peel 2 1 (carried ms3 b16) == some b16
#guard peel 1 1 (carried ms3 b16) == none && peel 2 0 (carried ms3 b16) == some (.implies gManager b16)
#guard peel 0 0 b16 == some b16 && peel 1 0 b16 == none && peel 0 1 b16 == none
-- two conditioned goals nest in block order, after the asserted one
def ms2c : List (Root × VE.Formula) := [(.conditioned, gOwner), (.asserted, .top), (.conditioned, gManager)]
#guard carried ms2c b16 == .and .top (.implies gOwner (.implies gManager b16)) && peel 1 2 (carried ms2c b16) == some b16

-- `plural_defined`, `generic_defined` at the S2 models and S26's model, both sides of each.
#guard [mAliceNone, mAliceOne, mAliceTwo].all (fun M => ev M rPl.strong == (ev M rPl.pre && ev M rPl.weak))
#guard [mAliceNone, mAliceOne, mAliceTwo].map (fun M => (ev M rPl.pre, ev M rPl.weak)) ==
  [(false, true), (true, true), (true, false)]
#guard (generic pAtom .top).strong == .and pAtom .top && (generic pAtom .top).weak == .implies pAtom .top
#guard !ev m26 (generic pAtom .top).strong && !ev m26 (generic pAtom .top).pre && ev m26 (generic pAtom .top).weak

-- S20 (a rule act takes no body), the rows' arguments and errors.
def reqIn : VE.Formula := .binary "request_in" (.var 0) (.var 1)
#guard (match buildPre "plural" 2 (some "entity", some reqIn, some .top, none) with
  | .error e => e == "body" | .ok _ => false)
#guard (match buildPre "plural" 2 (some "entity", some reqIn, none, none) with
  | .ok p => p == .ex "entity" reqIn | .error _ => false)
#guard (match buildReading "titles" 0 (none, none, none, none) with | .error e => e == "row" | .ok _ => false)
#guard (match buildPre "titles" 0 (none, none, none, some .top) with | .error e => e == "row" | .ok _ => false)
#guard (match buildReading "definite" 0 (some "entity", some owner, some ready, none) with
  | .ok r => r == rOwner | .error _ => false)
#guard (match buildReading "plural" 0 (some "entity", some mgrOf, some ready, none) with
  | .ok r => r == rPl | .error _ => false)
#guard (match buildReading "generic" 0 (none, none, some .top, some pAtom) with
  | .ok r => r == generic pAtom .top | .error _ => false)
#guard ["definite", "plural", "generic"].all (fun row =>
  match buildReading row 0 (some "entity", none, some ready, some .top) with | .error e => e == "arguments" | _ => false)
#guard (match buildPre "definite" 1 (some "entity", some reqIn, none, none) with
  | .ok p => p == VE.Discourse.uniqueOpen 1 "entity" reqIn | .error _ => false)
#guard (match buildPre "generic" 2 (none, none, none, some pAtom) with | .ok p => p == pAtom | .error _ => false)
#guard ["definite", "generic"].all (fun row =>
  match buildPre row 0 (some "entity", some owner, some .top, some .top) with | .error e => e == "body" | _ => false)
#guard (match buildPre "definite" 0 (none, some owner, none, none) with | .error e => e == "arguments" | _ => false)
-- at a content position, `buildPre` and `(buildReading …).pre` agree for a definite and a plural
#guard [("definite", rOwner), ("plural", plural "entity" owner ready)].all (fun (row, r) =>
  (buildPre row 0 (some "entity", some owner, none, none)).toOption == some r.pre &&
  ((buildReading row 0 (some "entity", some owner, some ready, none)).map Reading.pre).toOption == some r.pre)

-- S23 (R-10): a heading's `pre` over the empty context; with a body, the error is `body`.
def coreValueOf : VE.Formula := .binary "core_value_of" (.var 0) (.const "claude")
#guard (match buildPre "plural" 0 (some "entity", some coreValueOf, none, none) with
  | .ok p => p == .ex "entity" coreValueOf | .error _ => false)
#guard (match buildPre "plural" 0 (some "entity", some coreValueOf, some .top, none) with
  | .error e => e == "body" | .ok _ => false)

-- S24 (R-14): open descriptions; `raise1` is needed for the inner binder.
def opOf : VE.Formula := .binary "operator_of" (.var 0) (.var 1)
def theOp : Reading := definite 1 "entity" opOf ready
def all24 : VE.Formula := .all "situation" theOp.pre
def wrong24 : VE.Formula := .all "situation" (VE.Discourse.uniqueAt "entity" opOf opOf)
def m24one : VE.FiniteModel String :=
  model [("situation", ["s1", "s2"]), ("entity", ["a", "b", "c"])]
    [("operator_of", [["a", "s1"], ["b", "s2"]]), ("ready", [["a"]])] []
def m24two : VE.FiniteModel String :=
  model [("situation", ["s1", "s2"]), ("entity", ["a", "b", "c"])]
    [("operator_of", [["a", "s1"], ["b", "s1"], ["c", "s2"]]), ("ready", [["a"]])] []
def evAt (M : VE.FiniteModel String) (ρ : List String) (a : VE.Formula) : Bool := a.eval M ρ
#guard [m24one, m24two].map (fun M => ev M all24) == [true, false]
#guard [m24one, m24two].map (fun M => ev M wrong24) == [true, true]
#guard [m24one, m24two].all (fun M => [["s1"], ["s2"]].all (fun ρ =>
  evAt M ρ theOp.strong == (evAt M ρ theOp.pre && evAt M ρ theOp.weak)))
#guard [["s1"], ["s2"]].map (fun ρ => (evAt m24two ρ theOp.pre, evAt m24two ρ theOp.strong)) ==
  [(false, false), (true, false)]

end VE.Presupposition.Examples
