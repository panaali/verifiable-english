import VE.Presupposition.Frame
import VE.Discourse.Descriptions
import VE.Finite

/-! # Frame-level fixtures (docs/spec/presupposition.md 7.1)

Rows "4.1" (builders), "4.2" (`locate`, `cls`), S2, S3, S4, S5, S9 and S21 (frame and goal
values in each listed model), and the shallow-frame class facts used by S12 and S25-S27.
`Rows.lean` is ps-1b's, so each `pre` and `strong` is written here as a literal formula:
`definite 0`'s are discourse's `uniqueD` and `assertive`, `plural`'s are `∃x:σ D` and
`∃x:σ D ∧ ∀x:σ (D → P)`. -/
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
def theOwnerU : VE.Formula := VE.Discourse.uniqueD "entity" owner
def theOwner : VE.Formula := VE.Discourse.assertive "entity" owner ready
def theManager : VE.Formula := VE.Discourse.assertive "entity" (.unary "manager" (.var 0)) (.unary "busy" (.var 0))

-- 4.1: the closed open forms are discourse's formulas; the weakening skips index 1, also under a binder.
#guard VE.Discourse.uniqueOpen 0 "entity" owner == theOwnerU
#guard VE.Discourse.assertiveOpen 0 "entity" owner ready == theOwner
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
def theMgrU : VE.Formula := VE.Discourse.uniqueD "entity" mgrOf
def theMgr : VE.Formula := VE.Discourse.assertive "entity" mgrOf ready
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
def thePlU : VE.Formula := .ex "entity" mgrOf
def thePl : VE.Formula := .and (.ex "entity" mgrOf) (.all "entity" (.implies mgrOf ready))
def noMgr : VE.Formula := .not (.ex "entity" mgrOf)
def f4 : Frame := .orR noMgr .hole
#guard Frame.locate (.or noMgr thePl) [1] == some (f4, thePl)
#guard f4.goal thePlU == .implies (.not noMgr) (.ex "entity" mgrOf)
#guard [mAliceNone, mAliceOne].map (fun M => ev M (f4.goal thePlU)) == [true, true]
#guard !ev mAliceNone (.implies noMgr (.ex "entity" mgrOf))

-- S5: the restrictor proves the goal (a); without it the goal fails (b); `ex` closes universally (c).
def person : VE.Formula := .unary "person" (.var 0)
def mgrOfX : VE.Formula := .binary "manager_of" (.var 0) (.var 1)
def theirU : VE.Formula := .ex "entity" mgrOfX
def their : VE.Formula := .and theirU (.all "entity" (.implies mgrOfX (.binary "trusts" (.var 1) (.var 0))))
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

-- S12, S25-S27: `not ·` and a root antecedent are shallow; the other negated frames are not.
#guard decide (Frame.notF .hole).shallow && decide (Frame.impL .hole .top).shallow
#guard [Frame.notF (.notF .hole), .notF (.andL .hole .top), .notF (.orL .hole .top), .andL (.notF .hole) .top].all
  (fun f => f.cls == .negated && !decide f.shallow)
-- the seven classes are distinct; `cls` gives no rule class (PS-2a's rule positions give `ruleAct` and `ruleGuard`)
def allClasses : List PositionClass := [.top, .negated, .antecedent, .consequent, .disjunct, .ruleAct, .ruleGuard]
#guard allClasses.eraseDups.length == 7
#guard !decide Frame.hole.shallow && !decide (Frame.impR .top .hole).shallow &&
  !decide (Frame.impL (.notF .hole) .top).shallow

end VE.Presupposition.Examples
