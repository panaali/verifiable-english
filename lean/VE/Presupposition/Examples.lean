import VE.Presupposition.Rows
import VE.Presupposition.Rules
import VE.Presupposition.Agree
import VE.Presupposition.Wire
import VE.Discourse.Descriptions
import VE.Finite

/-! # Formula-level fixtures (docs/spec/presupposition.md 7.1, 7.2)

Rows "4.1" (builders), "4.2" (`locate`, `cls`), S2, S3, S4, S5, S9 and S21 (frame and goal
values in each listed model), the shallow-frame class facts used by S12 and S25-S27, and the
readings and rows of 4.3 and 4.4: S1 and its definedness row, S12, S13, S16, S20, S23, S24, S25,
and S26's whole-unit values; the rules of 4.5: S14 and S22's formula-level rows; 4.6's S8; and the pilot formulas P1-P4 and P13. Each `pre` and `strong` is built by `definite`, `plural` or
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

-- S14: a rule on `answer_required(agent, situation)`. `tupleVal` reads an (agent, situation) pair as `[situation, agent]`.
def reg14 : VE.Norms.Regulated :=
  { name := "answer_required", sorts := ["agent", "situation"], allowByDefault := false, role := .plain,
    act := none, permission := none }
def rule14 (name : String) (sign : Bool) (guard : VE.Formula) (carveOuts : List VE.Formula := [])
    (over : List String := []) : VE.Norms.Node :=
  { name := name, pred := "answer_required", sign := sign, guard := guard, carveOuts := carveOuts, over := over }
def tree14 (nodes : List VE.Norms.Node) : VE.Norms.Tree := { regulated := [reg14], definitions := [], nodes := nodes }
def pre14 : VE.Formula :=
  .ex "request" (.and (.binary "request_in" (.var 0) (.var 1)) (.binary "addressed_to" (.var 0) (.var 2)))
def noAddressee14 : VE.Formula := .ex "request" (.binary "request_in" (.var 0) (.var 1))
def onDuty : VE.Formula := .unary "on_duty" (.var 1)
def r14a : VE.Norms.Node := rule14 "r1" true pre14
def r14b : VE.Norms.Node := rule14 "r1" true noAddressee14
def r14other : VE.Norms.Node := rule14 "r2" true onDuty
def m14 : VE.FiniteModel String :=
  model [("agent", ["ag1", "ag2"]), ("situation", ["s1"]), ("request", ["q"])]
    [("request_in", [["q", "s1"]]), ("addressed_to", [["q", "ag1"]]), ("on_duty", [["ag2"]])] []
def at1 : List String := VE.Norms.tupleVal ["ag1", "s1"]
def at2 : List String := VE.Norms.tupleVal ["ag2", "s1"]
def dec14 (T : VE.Norms.Tree) (ρ : List String) : Bool := evAt m14 ρ (VE.Norms.decides T "answer_required" true)
def app14 (N : VE.Norms.Node) (ρ : List String) : Bool := evAt m14 ρ (VE.Norms.applies N)
#guard at1 == ["s1", "ag1"]
-- S14a (guard = `pre`): the goal holds, and the conditioned rule decides where the original does.
#guard ev m14 (ruleGoal reg14 r14a pre14) == true
#guard (dec14 (tree14 [r14a]) at1, dec14 (conditionRule (tree14 [r14a]) "r1" pre14) at1) == (true, true)
#guard (dec14 (tree14 [r14a]) at2, dec14 (conditionRule (tree14 [r14a]) "r1" pre14) at2) == (false, false)
-- S14b (guard without the addressee): the goal fails (M3 makes it true), and `rule_collapse_decides`' hypothesis is needed.
#guard ev m14 (ruleGoal reg14 r14b pre14) == false
#guard (dec14 (tree14 [r14b]) at1, dec14 (conditionRule (tree14 [r14b]) "r1" pre14) at1) == (true, true)
#guard (app14 r14b at2, evAt m14 at2 pre14) == (true, false)
#guard (dec14 (tree14 [r14b]) at2, dec14 (conditionRule (tree14 [r14b]) "r1" pre14) at2) == (true, false)
-- `condition_applies`, both directions; the last rows need the node's own guard and carve-outs.
#guard (app14 r14b at1, evAt m14 at1 pre14, app14 (conditionNode r14b pre14) at1) == (true, true, true)
#guard (app14 r14b at2, evAt m14 at2 pre14, app14 (conditionNode r14b pre14) at2) == (true, false, false)
#guard (app14 r14other at1, evAt m14 at1 pre14, app14 (conditionNode r14other pre14) at1) == (false, true, false)
#guard app14 (conditionNode (rule14 "r3" true .top [onDuty]) .top) at2 == false
#guard app14 (conditionNode (rule14 "r3" true .top [onDuty]) .top) at1 == true
-- The other rule: conditioning `r1` leaves `r2` deciding, conditioning `r2` does not; an unnamed rule keeps its node.
#guard dec14 (conditionRule (tree14 [r14a, r14other]) "r1" pre14) at2 == true
#guard dec14 (conditionRule (tree14 [r14a, r14other]) "r2" pre14) at2 == false
#guard dec14 (conditionRule (tree14 [r14a, r14other]) "absent" pre14) at2 == true
-- `conditionRule_shape`: only the named rule's guard moves.
#guard (conditionRule (tree14 [r14a, r14other]) "r1" pre14).nodes == [conditionNode r14a pre14, r14other]
#guard (conditionRule (tree14 [r14a, r14other]) "r1" pre14).regulated == [reg14]
#guard (conditionNode r14a pre14).guard == .and pre14 pre14
-- Exceptions read the conditioned tree: `r4` (over `r1`) blocks `r1` while it applies, and not once its condition fails.
def t14ex : VE.Norms.Tree := tree14 [rule14 "r1" true .top, rule14 "r4" false .top [] ["r1"]]
#guard dec14 t14ex at1 == false
#guard dec14 (conditionRule t14ex "r4" .bottom) at1 == true
-- `conditioned_contributes_nothing`: false where the condition is, and the node still selects where it holds.
#guard evAt m14 at2 (VE.Norms.selects (tree14 [r14b]) 1 (conditionNode r14b pre14)) == false
#guard evAt m14 at1 (VE.Norms.selects (tree14 [r14b]) 1 (conditionNode r14b pre14)) == true
-- The goal binds the regulated sorts, whatever the node's `over`.
#guard ruleGoal reg14 (rule14 "r1" true pre14 [] ["r9"]) pre14 ==
  .all "agent" (.all "situation" (.implies (VE.Norms.applies (rule14 "r1" true pre14 [] ["r9"])) pre14))

-- `rule_collapse_typed`'s `hname` is needed: the goal holds for `r14a`, and a second rule named `r1` changes the decision.
def t14dup : VE.Norms.Tree := tree14 [r14a, rule14 "r1" true .top]
#guard ev m14 (ruleGoal reg14 r14a pre14) == true
#guard (dec14 t14dup at2, dec14 (conditionRule t14dup r14a.name pre14) at2) == (true, false)

-- S22's formula-level rows: `p(situation)` is `unspecified` (`allowByDefault` is the placeholder deny); two rules on `p`
-- with guard `g`, one goal. `SatUnder` and `SameModels` over these picks are PS-2a's.
def reg22 : VE.Norms.Regulated :=
  { name := "p", sorts := ["situation"], allowByDefault := false, role := .plain, act := none, permission := none }
def rule22 (name : String) : VE.Norms.Node :=
  { name := name, pred := "p", sign := true, guard := .unary "g" (.var 0), carveOuts := [], over := [] }
def t22 : VE.Norms.Tree := { regulated := [reg22], definitions := [], nodes := [rule22 "r1", rule22 "r2"] }
def pre22 : VE.Formula := .ex "entity" (.unary "instruction" (.var 0))
def mixed22 : VE.Norms.Tree := conditionRule t22 "r2" pre22
def m22 (ps : List (List String)) : VE.FiniteModel String :=
  model [("situation", ["s1", "s2"]), ("entity", ["i1"])]
    [("g", [["s1"]]), ("instruction", [["i1"]]), ("p", ps)] []
def m22p : VE.FiniteModel String := m22 [["s1"], ["s2"]]
#guard ev m22p (ruleGoal reg22 (rule22 "r1") pre22) && ev m22p (ruleGoal reg22 (rule22 "r2") pre22)
-- Off the goal the rules still make the goal fail: no instruction, and `g(s1)`.
#guard ev (model [("situation", ["s1", "s2"]), ("entity", ["i1"])] [("g", [["s1"]])] [])
  (ruleGoal reg22 (rule22 "r1") pre22) == false
-- The mixed pick and its representative decide alike: at `s1`, not at `s2`.
#guard [t22, mixed22].map (fun T => (evAt m22p ["s1"] (VE.Norms.pos T "p"), evAt m22p ["s2"] (VE.Norms.pos T "p"))) ==
  [(true, false), (true, false)]
#guard [t22, mixed22].all (fun T => [["s1"], ["s2"]].all (fun ρ => !evAt m22p ρ (VE.Norms.neg T "p")))
-- The raw W1 side: the placeholder deny makes `p(s2)` fail in both picks, and only `p(s2)` (the same model without it passes).
#guard [t22, mixed22].map (fun T => (VE.Norms.elaborate T).all (ev m22p)) == [false, false]
#guard [t22, mixed22].map (fun T => [["s1"], ["s2"]].map (fun ρ => evAt m22p ρ (VE.Norms.elabBody T reg22))) ==
  [[true, false], [true, false]]
#guard [t22, mixed22].map (fun T => (VE.Norms.elaborate T).all (ev (m22 [["s1"]]))) == [true, true]
-- `unsaid_iff` on the `unspecified` cell: `s2` (no rule decides) is `unsaid`, `s1` (a rule decides) is not.
theorem s22_pos_s1 : evAt m22p ["s1"] (VE.Norms.pos mixed22 "p") = true := by decide
theorem s22_pos_s2 : evAt m22p ["s2"] (VE.Norms.pos mixed22 "p") = false := by decide
theorem s22_neg_s2 : evAt m22p ["s2"] (VE.Norms.neg mixed22 "p") = false := by decide
example : VE.NormDefaults.value3 (evAt m22p ["s2"] (VE.Norms.pos mixed22 "p") = true)
    (evAt m22p ["s2"] (VE.Norms.neg mixed22 "p") = true) .unspecified = .unsaid :=
  (unsaid_iff _ _).mpr ⟨by simp [s22_pos_s2], by simp [s22_neg_s2]⟩
example : VE.NormDefaults.value3 (evAt m22p ["s1"] (VE.Norms.pos mixed22 "p") = true)
    (evAt m22p ["s1"] (VE.Norms.neg mixed22 "p") = true) .unspecified ≠ .unsaid :=
  fun h => ((unsaid_iff _ _).mp h).1 s22_pos_s1

-- S8: `resides_in` total and functional; "the State wherein Alice resides". The last model is one more direction: total F.
def flag8 : VE.Data.Background.Flag :=
  { name := "resides_in", source := "person", target := "state", functional := true, total := true }
def u8 : VE.Formula := Frame.hole.goal (VE.Discourse.uniqueD "state" (.binary "resides_in" (.const "alice") (.var 0)))
def m8 (rows : List (List String)) : VE.FiniteModel String :=
  model [("person", ["alice"]), ("state", ["ohio", "iowa"])] [("resides_in", rows)] [("alice", "alice")]
def row8 (M : VE.FiniteModel String) : Bool × Bool × Bool :=
  (ev M (VE.Data.Background.functionalPremise flag8), ev M (VE.Data.Background.totalPremise flag8), ev M u8)
#guard row8 (m8 [["alice", "ohio"]]) == (true, true, true)
#guard row8 (m8 [["alice", "ohio"], ["alice", "iowa"]]) == (false, true, false)
#guard row8 (m8 []) == (true, false, false)
#guard VE.Data.Background.premises flag8 ==
  [VE.Data.Background.functionalPremise flag8, VE.Data.Background.totalPremise flag8]

-- `discourse_definite_is_row`: at 0 the row is discourse's description; open over a binder it is not.
#guard (definite 0 "entity" owner ready).pre == VE.Discourse.uniqueD "entity" owner
#guard (definite 1 "entity" opOf ready).pre != VE.Discourse.uniqueD "entity" opOf

-- P1-P4: the heading formulas (`buildPre row 0`); their obligations are PS-2a's admission rows A24 and A25, their English PS-6r's.
def guidelineOf : VE.Formula := .binary "guideline_of" (.var 0) (.const "anthropic")
def missionOf : VE.Formula := .binary "mission_of" (.var 0) (.const "anthropic")
def openProblem : VE.Formula := .ex "entity" (.unary "open_problem" (.var 0))
def preIs (row : String) (a : Option String × Option VE.Formula × Option VE.Formula × Option VE.Formula)
    (p : VE.Formula) : Bool :=
  match buildPre row 0 a with | .ok q => q == p | .error _ => false
#guard preIs "plural" (some "entity", some coreValueOf, none, none) (.ex "entity" coreValueOf)
#guard preIs "plural" (some "entity", some guidelineOf, none, none) (.ex "entity" guidelineOf)
#guard preIs "generic" (none, none, none, some openProblem) openProblem
#guard preIs "definite" (some "entity", some missionOf, none, none) (VE.Discourse.uniqueD "entity" missionOf)
-- Each formula separates a model where it holds from one where it does not; P4 two missions from one.
def mP (rels : List (String × List (List String))) : VE.FiniteModel String :=
  model [("entity", ["a", "b", "anthropic", "claude"])] rels [("anthropic", "anthropic"), ("claude", "claude")]
#guard [ev (mP [("core_value_of", [["a", "claude"]])]) (.ex "entity" coreValueOf), ev (mP []) (.ex "entity" coreValueOf)] ==
  [true, false]
#guard [ev (mP [("guideline_of", [["a", "anthropic"]])]) (.ex "entity" guidelineOf), ev (mP []) (.ex "entity" guidelineOf)] ==
  [true, false]
#guard [ev (mP [("open_problem", [["a"]])]) openProblem, ev (mP []) openProblem] == [true, false]
#guard [[["a", "anthropic"]], [["a", "anthropic"], ["b", "anthropic"]], []].map
    (fun rows => ev (mP [("mission_of", rows)]) (VE.Discourse.uniqueD "entity" missionOf)) == [true, false, false]

-- P13: S8 on the 14th Amendment use case's vocabulary, "the State wherein they reside": the description is open over the person.
def stateOf : VE.Formula := .binary "resides_in" (.var 1) (.var 0)
def r13 : Reading := definite 1 "state" stateOf (.unary "citizen_of_state" (.var 0))
def goal13 : VE.Formula := (Frame.allF "person" .hole).goal r13.pre
def m13 (doms : List String) (rows : List (List String)) : VE.FiniteModel String :=
  model [("person", ["alice", "bob"]), ("state", doms)] [("resides_in", rows)] []
def row13 (M : VE.FiniteModel String) : Bool × Bool × Bool :=
  (ev M (VE.Data.Background.functionalPremise flag8), ev M (VE.Data.Background.totalPremise flag8), ev M goal13)
#guard goal13 == .all "person" (VE.Discourse.uniqueOpen 1 "state" stateOf)
#guard row13 (m13 ["arizona"] [["alice", "arizona"], ["bob", "arizona"]]) == (true, true, true)
#guard row13 (m13 ["arizona", "ohio"] [["alice", "arizona"], ["alice", "ohio"], ["bob", "arizona"]]) == (false, true, false)
#guard row13 (m13 ["arizona"] [["alice", "arizona"]]) == (true, false, false)

/-! ## 4.7's wire layer (PS-2aa): carriers, the table's shape, the readings of an open set, restriction paths -/

-- Roots and candidates: only asserted and conditioned have a root of their own; proved and unresolved stand for no
-- candidate; the core candidates are assumed, conditioned and asserted.
def allCarriers : List Carrier :=
  [.proved "n", .assumed "u", .conditioned, .asserted, .inPlace, .unconditional "u", .unresolved]
def allCandidates : List Candidate := [.assumed, .conditioned, .asserted, .inPlace, .unconditional]
#guard allCarriers.map Carrier.root == [.bare, .bare, .conditioned, .asserted, .bare, .bare, .bare]
#guard allCarriers.map Carrier.cand ==
  [none, some .assumed, some .conditioned, some .asserted, some .inPlace, some .unconditional, none]
#guard allCandidates.map Candidate.root == [.bare, .conditioned, .asserted, .bare, .bare]
#guard allCandidates.map Candidate.core == [true, true, true, false, false]
#guard allCarriers.all (fun c => (c.cand.map Candidate.root).getD .bare == c.root)
#guard ({ sort := some "entity", body := some ready } : Args).tuple == (some "entity", none, some ready, none)
-- R-10: a heading is a position of its own, not the root path; a rule act is named by its rule.
#guard Position.heading != .path [] && Position.ruleAct "r1" != .ruleAct "r2" && Position.path [0] != .path [1]

-- table (7.1), `tableOk` (7.2): the fixture table and the empty table pass; `[asserted]` everywhere, at a rule act
-- alone, `[assumed, asserted]` and `[inPlace]` alone in the negated cell fail (R-2); `[conditioned, inPlace]` passes.
def fixtureTable : CandidateTable := fun _ pc => match pc with
  | .negated => [.assumed, .conditioned, .inPlace]
  | _ => [.assumed, .conditioned]
#guard tableOk rowNames fixtureTable
#guard tableOk rowNames candidateTable
#guard !tableOk rowNames (fun _ _ => [.asserted])
#guard !tableOk rowNames (fun _ pc => if pc == .ruleAct then [.asserted] else [])
#guard !tableOk rowNames (fun _ _ => [.assumed, .asserted])
#guard !tableOk rowNames (fun _ pc => if pc == .negated then [.inPlace] else [])
#guard tableOk rowNames (fun _ pc => if pc == .negated then [.conditioned, .inPlace] else [])
-- `cellOk`'s other clauses: no repeats; in place only in a negated or antecedent cell; unconditional only in a
-- consequent cell; asserted anywhere but a rule act. `tableOk` reads every listed row and class, the rule guard too.
#guard !cellOk .top [.conditioned, .conditioned] && cellOk .top [.assumed, .conditioned]
#guard cellOk .antecedent [.conditioned, .inPlace] && !cellOk .top [.conditioned, .inPlace]
#guard cellOk .consequent [.unconditional] && !cellOk .top [.unconditional]
#guard cellOk .top [.asserted] && !cellOk .ruleAct [.asserted] && !cellOk .top [.assumed, .asserted]
#guard !tableOk rowNames (fun r pc => if r == "generic" && pc == .ruleGuard then [.unconditional] else [])
#guard tableOk [] (fun _ _ => [.assumed, .asserted])

-- S12 (R-4): `not ·` is shallow; under the fixture table's negated cell `[assumed, conditioned, inPlace]` a recorded
-- in place is allowed, as are the cell's other candidates; asserted, outside the cell, is not.
def ob12 : Obligation :=
  { id := "p1", unit := "u12", span := (0, 0), row := "definite", position := .path [0],
    args := { sort := some "entity", restriction := some owner, body := some ready }, carrier := .unresolved }
def chk12 : Checked :=
  { ob := ob12, frame := negF, pre := rOwner.pre, reading := some rOwner, goal := negF.goal rOwner.pre,
    pos := .negated }
#guard carrierAllowed fixtureTable chk12 .inPlace && carrierAllowed fixtureTable chk12 .assumed &&
  carrierAllowed fixtureTable chk12 .conditioned && !carrierAllowed fixtureTable chk12 .asserted
-- the cell is read at the obligation's own class: at the top cell in place is not listed
#guard !carrierAllowed fixtureTable { chk12 with pos := .top } .inPlace
#guard !carrierAllowed candidateTable chk12 .assumed

-- S25 (R-4): `not (not ·)` is negated but not shallow: a recorded in place is refused, conditioned is not.
def chk25 : Checked := { chk12 with frame := negNegF, ob := { ob12 with position := .path [0, 0] } }
#guard !carrierAllowed fixtureTable chk25 .inPlace && carrierAllowed fixtureTable chk25 .conditioned

-- S27 (R-4, A23): other negated frames that are not shallow: `carrierAllowed … inPlace` is false at each.
def nestedFrames : List Frame := [.notF (.andL .hole .top), .notF (.orL .hole .top), .andL (.notF .hole) .top]
#guard nestedFrames.all (fun f => !carrierAllowed fixtureTable { chk12 with frame := f } .inPlace)
#guard nestedFrames.all (fun f => carrierAllowed fixtureTable { chk12 with frame := f } .conditioned)
-- a root antecedent is shallow: in place is allowed in the antecedent cell of a table that lists it
#guard carrierAllowed (fun _ _ => [.conditioned, .inPlace]) { chk12 with frame := .impL .hole .top, pos := .antecedent }
  .inPlace

-- S26 (R-4): two triggers in one unit, the outer unresolved at `not (not ·)`, the inner recorded conditioned:
-- `unitModes` gives the unit's roots and goals in block order (the outer bare until a reading picks it).
def outer26 : Checked :=
  { ob := { id := "o", unit := "u26", span := (0, 0), row := "generic", position := .path [0, 0],
            args := { body := some .top, pre := some q26 }, carrier := .unresolved },
    frame := negNegF, pre := q26, reading := some (generic q26 .top), goal := q26, pos := .negated }
def inner26 : Checked :=
  { ob := { id := "i", unit := "u26", span := (0, 0), row := "generic", position := .path [0, 0, 0],
            args := { body := some .top, pre := some pAtom }, carrier := .conditioned },
    frame := .notF (.notF (.andL .hole .top)), pre := pAtom, reading := some (generic pAtom .top), goal := pAtom,
    pos := .negated }
def emptyTree : VE.Norms.Tree := { regulated := [], definitions := [], nodes := [] }
def rep26 : Report := { checked := [outer26, inner26, chk12], bases := [("u26", b26)], baseTree := emptyTree }
#guard unitModes rep26 "u26" == [(.bare, q26), (.conditioned, pAtom)] && unitModes rep26 "u12" == [(.bare, chk12.goal)]
#guard unitModes { rep26 with checked := [{ outer26 with ob := { outer26.ob with carrier := .asserted } }] } "u26" ==
  [(.asserted, q26)]
#guard !carrierAllowed fixtureTable outer26 .inPlace && carrierAllowed fixtureTable outer26 .assumed

-- `ruleConditions`: the conditions recorded on a rule, in block order; unresolved, assumed and other rules' are not.
def chkR (i : String) (n : String) (c : Carrier) (pre : VE.Formula) : Checked :=
  { ob := { id := i, unit := "ur", span := (0, 0), row := "plural", position := .ruleAct n, args := {},
            carrier := c },
    frame := .hole, pre := pre, reading := none, goal := pre, pos := .ruleAct }
def repR : Report :=
  { checked := [chkR "a" "r1" .unresolved pAtom, chkR "b" "r1" .conditioned q26, chkR "c" "r1" (.assumed "u0") owner,
      chkR "d" "r2" .conditioned busy, chkR "e" "r1" .conditioned ready],
    bases := [], baseTree := emptyTree }
#guard ruleConditions repR "r1" == [q26, ready] && ruleConditions repR "r2" == [busy] && ruleConditions repR "r3" == []
-- at a rule act the fixture table's cell is `[assumed, conditioned]`: asserted and in place are never allowed
#guard carrierAllowed fixtureTable (chkR "a" "r1" .unresolved pAtom) .conditioned &&
  !carrierAllowed fixtureTable (chkR "a" "r1" .unresolved pAtom) .asserted &&
  !carrierAllowed fixtureTable (chkR "a" "r1" .unresolved pAtom) .inPlace

-- R-D6: restriction paths point at `D` in `strong`; the body `P` sits at `[0, 1, 1]` (definite) and `[1, 0, 1]`
-- (plural), outside every restriction path; a generic row has no restriction.
#guard (Frame.locate rOwner.strong [0, 0]).map (·.2) == some owner
#guard (Frame.locate rOwner.strong [0, 1, 0, 0, 0]).map (·.2) == some owner
#guard (Frame.locate rOwner.strong [0, 1, 1]).map (·.2) == some ready
#guard (Frame.locate rPl.strong [0, 0]).map (·.2) == some mgrOf
#guard (Frame.locate rPl.strong [1, 0, 0]).map (·.2) == some mgrOf
#guard (Frame.locate rPl.strong [1, 0, 1]).map (·.2) == some ready
#guard entersRestriction "definite" [] [0, 0] && entersRestriction "definite" [] [0, 1, 0, 0, 0, 1]
#guard !entersRestriction "definite" [] [0, 1, 1] && !entersRestriction "plural" [] [1, 0, 1]
#guard !entersRestriction "plural" [1] [1, 1, 0, 1] && entersRestriction "plural" [1] [1, 1, 0, 0]
#guard !entersRestriction "plural" [1] [0, 0] && entersRestriction "plural" [1] [1, 0, 0]
#guard restrictionPaths "generic" == [] && !entersRestriction "generic" [] [0] && !entersRestriction "generic" [] []
-- a prefix of a restriction path does not enter it (the containment runs one way)
#guard !entersRestriction "definite" [] [0] && !entersRestriction "plural" [1] [1]

-- Positions inside each list (trust-mutants survivors): the refused candidate not first, not last; the bad cell in
-- the first and the middle row and in each class; an obligation path of two steps; a conditioned first obligation.
#guard !cellOk .top [.asserted, .assumed] && !cellOk .negated [.assumed, .inPlace] && !cellOk .negated [.inPlace, .assumed]
#guard cellOk .negated [.inPlace, .conditioned] && !cellOk .ruleAct [.asserted, .conditioned] &&
  !cellOk .top [.unconditional, .assumed]
def badAt (r : String) (c : PositionClass) (cell : List Candidate) : CandidateTable :=
  fun r' pc => if r' == r && pc == c then cell else []
#guard [PositionClass.top, .antecedent, .disjunct, .ruleGuard].all (fun c =>
  ["definite", "plural"].all (fun r => !tableOk rowNames (badAt r c [.unconditional])))
#guard !tableOk rowNames (badAt "definite" .consequent [.conditioned, .inPlace]) &&
  tableOk rowNames (badAt "definite" .consequent [.unconditional])
#guard !entersRestriction "definite" [] [0, 1, 0, 0, 1] && (Frame.locate rOwner.strong [0, 1, 0, 0, 1]).map (·.2) ==
  some (.eq (.var 0) (.var 1))
#guard !entersRestriction "plural" [] [0] && entersRestriction "plural" [] [0, 0] && !entersRestriction "plural" [] [1, 0]
#guard entersRestriction "plural" [1, 1] [1, 1, 0, 0, 2] && !entersRestriction "plural" [1, 0] [1, 0, 0]
#guard ruleConditions { repR with checked := repR.checked.drop 1 } "r1" == [q26, ready]

end VE.Presupposition.Examples
