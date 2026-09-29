import VE.Rights.Route
import VE.Norms.Checks

/-! Concrete rights documents in the shapes of the item-1 fixtures (docs/spec/rights.md 10)
and build-time regression checks on them (`#guard`: the build fails if one is false).

* Well-formedness and the exact diagnostic texts (α, β, γ, ε, η, ο, π, ρ, υ, φ): these show
  that `WellFormedRights` accepts the documents the theorems are about. The frozen soft
  validator inside it does not reduce in the kernel (`mergeSort`, `startsWith`), so these
  are compiled evaluations, not kernel proofs.
* Outcomes on finite base models: a line's selection is read off `selectsR D N°` and the
  completed outcome off `O_p°` of `T″′`, evaluated by `Formula.eval` (on a base-admissible
  structure these are the selection and outcome at the canonical expansion, `circ_canon`).
* The audit `limitationScope` on γ with an adopter's exception, uncited and cited; on μ's
  collisions (strict blocking by another right's line, dominance under an uncited and a cited
  ranking); on ψ's bar across the dual pair; on σ's same-effect and opposite-effect blocking;
  on κ's default and strict force.

Arity is at most two in the Lean formula language, so the ternary `nary@0` fixtures (μ, ψ)
are represented by their binary shapes on `publish_about(person, person)` below. -/
namespace VE.Rights.Examples
open VE.Norms (Regulated Node tupleVal)
open VE.Norms.Checks (envOf perm oblig)
open VE.SoftNorms (SoftNode SoftDoc SoftEnv soften)

def noSoft : SoftEnv := ⟨[], [], [], [], .strict, none, none, [], []⟩

def strictNode (name pred : String) (sign : Bool) (guard : VE.Formula := .top) (carve : List VE.Formula := [])
    (over : List String := []) : SoftNode :=
  { name := name, pred := pred, sign := sign, guard := guard, carveOuts := carve, over := over,
    mode := .strict, rank := none, alterable := [], exception := none, hard := false }

def defaultNode (name pred : String) (sign : Bool) (guard : VE.Formula := .top) : SoftNode :=
  { strictNode name pred sign guard with mode := .default, exception := some ⟨some "unstated", [], [], []⟩ }

def line (kind : Kind) (n : SoftNode) (slot : Option Nat := none) : SourceLine :=
  ⟨kind, some n, none, none, [], slot, []⟩

def mkRights (sorts : List String) (base : List (String × List String)) (regs : List Regulated)
    (outside : List SoftNode) (block : RightsEnv) (rs : List Right) (limits : List Limitation) (bars : List Bar) :
    RightsDoc where
  soft := ⟨envOf sorts (base ++ regs.map (fun r => (r.name, r.sorts))), [], noSoft, ⟨regs, [], outside⟩⟩
  rights := block
  rs := rs
  limits := limits
  bars := bars
  outsideCites := []
  sourceUnits := ["u1", "u082"]

def block : RightsEnv := ⟨["person"], ["state", "person"], [], []⟩

/-- The diagnostic of `validateRights`, `ok` when well-formed. -/
def diag (D : RightsDoc) : String :=
  match validateRights D with
  | .ok () => "ok"
  | .error e => e

/-- The instance named `n`. -/
def lineNamed (D : RightsDoc) (n : String) : Option Line := ((linesOf D).map (·.2)).find? (·.node.name == n)

def noLine : Line := ⟨"", line .claim (strictNode "" "" false), .claim, .claim, strictNode "" "" false, none⟩

/-- The instance named `n` (a placeholder when absent, which no check below expects). -/
def lineAt (D : RightsDoc) (n : String) : Line := (lineNamed D n).getD noLine

/-- `selects″_N°` of the instance named `n` at a tuple of a finite base model. -/
def selectsAt (D : RightsDoc) (n : String) (M : VE.FiniteModel String) (vs : List String) : Bool :=
  match lineNamed D n with
  | some N => (outcomeSubst D (selectsR D N)).eval M (tupleVal vs)
  | none => false

/-- `O_p°` of `T″′` at a tuple of a finite base model. -/
def outcomeAt (D : RightsDoc) (p : String) (M : VE.FiniteModel String) (vs : List String) : Bool :=
  (VE.Norms.outcomeBase (soften (correlate D)) p).eval M (tupleVal vs)

def model (rels : List (String × List (List String))) : VE.FiniteModel String where
  domains s := match s with
    | "state" => ["Texas"]
    | "person" => ["Ann", "Bob"]
    | "idea" => ["I"]
    | _ => []
  constants _ := none
  relations p := ((rels.find? (·.1 == p)).map (·.2)).getD []

/-! ## (α) Art. 3: a duty is not a breach -/

def alpha : RightsDoc :=
  mkRights ["state", "person"] []
    [oblig "deprive_required" ["state", "person"] false (some "deprive_permitted") "{0} deprive {1} of life",
     perm "deprive_permitted" ["state", "person"] true "{0} deprive {1} of life"]
    [] block
    [⟨"r3", "person", .top, [line .claim (strictNode "no-deprivation" "deprive_permitted" false)]⟩] [] []

#guard diag alpha == "ok"
-- the line selects unconditionally, so `O_{deprive_permitted}(Texas, Ann)` is false
#guard selectsAt alpha "no-deprivation" (model []) ["Texas", "Ann"]
#guard !outcomeAt alpha "deprive_permitted" (model []) ["Texas", "Ann"]
#guard (linesOf alpha).map (fun RN => (RN.1, holderSlot alpha RN.2, dutyKind RN.2)) == [("r3", 1, true)]
-- no limitation, power, fan-out or bar, every `H_R` top: `correlate D = flattenTop D`
#guard (correlate alpha).T.nodes == (flattenTop alpha).T.nodes

/-! ## (β) Art. 5: fan-out -/

def tortureRegs : List Regulated :=
  [perm "torture_permitted_state" ["state", "person"] true "{0} torture {1}",
   perm "torture_permitted_person" ["person", "person"] true "{0} torture {1}"]

def fanLine (m : List (String × String)) (alterable : List String := []) : SourceLine :=
  ⟨.claim, some { strictNode "no-torture" "torture_permitted_state" false with alterable := alterable }, none, none, m,
   none, []⟩

def beta (m : List (String × String)) : RightsDoc :=
  mkRights ["state", "person"] [] tortureRegs [] block [⟨"r5", "person", .top, [fanLine m]⟩] [] []

def fanMap : List (String × String) := [("state", "torture_permitted_state"), ("person", "torture_permitted_person")]

#guard diag (beta fanMap) == "ok"
#guard (linesOf (beta fanMap)).map (fun RN => (RN.2.node.name, RN.2.node.pred, RN.2.bearer)) ==
  [("rights-fan-1", "torture_permitted_person", some "person"), ("rights-fan-2", "torture_permitted_state", some "state")]
#guard diag (beta [("state", "torture_permitted_state")]) == "FanOutUndeclared: no-torture, person"

/-! ## (γ) Art. 9 under limitation 29 -/

def l29 : Limitation :=
  ⟨"l29", none, none, some "unstated",
   [⟨"determined_by_law", true, "the limitation is determined by law", none⟩,
    ⟨"solely_for_permitted_purpose", true, "the limitation is solely for a permitted purpose", none⟩], []⟩

def arrestClaim : SourceLine :=
  line .claim (strictNode "no-arbitrary-arrest" "arrest_permitted" false (.binary "arbitrary_arrest" (.var 1) (.var 0)))

def gamma : RightsDoc :=
  mkRights ["state", "person"] [("arbitrary_arrest", ["state", "person"]), ("journalist", ["person"])]
    [perm "arrest_permitted" ["state", "person"] true "{0} arrest {1}"]
    [] block [⟨"r9", "person", .top, [arrestClaim]⟩] [l29] []

#guard diag gamma == "ok"
#guard genDecls gamma ==
  [("rights__lim__1", ["state", "person"]), ("rights__cond__1", ["state", "person"]), ("rights__cond__2", ["state", "person"])]
#guard (limPremisesLabelled gamma).map (·.1) ==
  ["rights:limitation:l29:arrest_permitted:necessary:determined_by_law",
   "rights:limitation:l29:arrest_permitted:necessary:solely_for_permitted_purpose"]
-- arbitrary and the limitation false: the line selects and arrest is forbidden
#guard selectsAt gamma "no-arbitrary-arrest" (model [("arbitrary_arrest", [["Texas", "Ann"]])]) ["Texas", "Ann"]
#guard !outcomeAt gamma "arrest_permitted" (model [("arbitrary_arrest", [["Texas", "Ann"]])]) ["Texas", "Ann"]
-- where the limitation holds the line is silent and the allow default decides
#guard !selectsAt gamma "no-arbitrary-arrest"
  (model [("arbitrary_arrest", [["Texas", "Ann"]]), ("rights__lim__1", [["Texas", "Ann"]])]) ["Texas", "Ann"]
#guard outcomeAt gamma "arrest_permitted"
  (model [("arbitrary_arrest", [["Texas", "Ann"]]), ("rights__lim__1", [["Texas", "Ann"]])]) ["Texas", "Ann"]
#guard limitationScope gamma [] == []

/-- γ with the adopter's `Rule 7 (exception to claim 1 of right 9). Every state may arrest each
person, if that person is a journalist.`, uncited. -/
def gamma7 : RightsDoc :=
  { gamma with soft := { gamma.soft with T := { gamma.soft.T with nodes :=
      [strictNode "rule-7" "arrest_permitted" true (.unary "journalist" (.var 0)) [] ["no-arbitrary-arrest"]] } } }

#guard diag gamma7 == "ok"
#guard (limitationScope gamma7 []).map (·.text) ==
  ["UnlicensedLimitation: exception rule-7 of rule no-arbitrary-arrest on right r9"]
-- the same rule citing the narrowing of the line: licensed, no finding
#guard limitationScope { gamma7 with outsideCites := [("rule-7", [("narrows:no-arbitrary-arrest", ["u082"])])] } [] == []
-- a citation to a unit the source does not have licenses nothing: the document is rejected
#guard diag { gamma7 with outsideCites := [("rule-7", [("narrows:no-arbitrary-arrest", ["u9"])])] } ==
  "UnknownSymbol: unit u9"
#guard diag { gamma with rs := [⟨"r9", "person", .top, [{ arrestClaim with cites := [("unless:1", ["u9"])] }]⟩] } ==
  "UnknownSymbol: unit u9"

/-! ## (ρ) two limitations -/

def rho : RightsDoc := { gamma with limits := [l29, ⟨"l29b", some ["r9"], none, some "unstated", [], []⟩] }

#guard diag rho == "ok"
-- only the second limitation holds: the pack holds, the line is silent
#guard !selectsAt rho "no-arbitrary-arrest"
  (model [("arbitrary_arrest", [["Texas", "Ann"]]), ("rights__lim__2", [["Texas", "Ann"]])]) ["Texas", "Ann"]

/-! ## (ε) Art. 16: a power with a holder guard; a power-only limitation -/

def epsilon : RightsDoc :=
  mkRights ["state", "person"] [("of_full_age", ["person"]), ("married", ["person"])]
    [perm "marry_permitted" ["person", "person"] true "{0} marry {1}",
     oblig "recognise_marriage_required" ["state", "person"] false none "{0} recognise the marriage of {1}",
     oblig "register_marriage_required" ["state", "person"] false none "{0} register the marriage of {1}"]
    [] ⟨["person"], ["state", "person"], [], [⟨"marry_permitted", 0, "married", some "recognise_marriage_required"⟩]⟩
    [⟨"r16", "person", .unary "of_full_age" (.var 0),
      [⟨.power, none, some (strictNode "may-marry" "marry_permitted" true),
        some (strictNode "recognise-marriage" "recognise_marriage_required" true), [], none, []⟩,
       line .claim (strictNode "register-marriage" "register_marriage_required" true)]⟩]
    [⟨"lp", none, some [.power], some "unstated", [], []⟩] []

#guard diag epsilon == "ok"
#guard (linesOf epsilon).map (fun RN => (RN.2.node.name, repr RN.2.ikind |>.pretty, repr RN.2.kind |>.pretty,
    (limPackList epsilon RN.2).length)) ==
  [("may-marry", "VE.Rights.IKind.powerLiberty", "VE.Rights.Kind.power", 1),
   ("recognise-marriage", "VE.Rights.IKind.powerRecognition", "VE.Rights.Kind.power", 1),
   ("register-marriage", "VE.Rights.IKind.claim", "VE.Rights.Kind.claim", 0)]
-- Ann of full age: the recognition duty and the liberty to marry select
#guard selectsAt epsilon "recognise-marriage" (model [("of_full_age", [["Ann"]])]) ["Texas", "Ann"]
#guard selectsAt epsilon "may-marry" (model [("of_full_age", [["Ann"]])]) ["Ann", "Bob"]
#guard outcomeAt epsilon "recognise_marriage_required" (model [("of_full_age", [["Ann"]])]) ["Texas", "Ann"]
-- Ann not of full age: neither instance selects
#guard !selectsAt epsilon "recognise-marriage" (model []) ["Texas", "Ann"]
#guard !selectsAt epsilon "may-marry" (model []) ["Ann", "Bob"]

/-! ## (η) Art. 19 and 30: the bar, rule reading -/

def impartRegs : List Regulated :=
  [oblig "impart_required" ["person", "idea"] false (some "impart_permitted") "{0} impart {1}",
   perm "impart_permitted" ["person", "idea"] true "{0} impart {1}"]

def eta (outside : List SoftNode := []) (liberty : SoftNode := strictNode "may-impart" "impart_permitted" true) :
    RightsDoc :=
  mkRights ["person", "idea"] [] impartRegs outside ⟨["person"], ["person"], [], []⟩
    [⟨"r19", "person", .top, [line .liberty liberty]⟩] [] [⟨"b30", .rule, some "unstated"⟩]

def aimed : VE.FiniteModel String := model [("rights__bar__1", [["Ann", "I"]])]

#guard diag (eta) == "ok"
#guard (barNodes (eta)).map (fun B => (B.name, B.pred, B.sign, B.over, B.hard)) ==
  [("rights-bar-1", "impart_permitted", false, ["may-impart"], true)]
-- where the act is aimed at destruction the liberty does not select and the act is forbidden
#guard !selectsAt (eta) "may-impart" aimed ["Ann", "I"]
#guard !outcomeAt (eta) "impart_permitted" aimed ["Ann", "I"]
#guard selectsAt (eta) "may-impart" (model []) ["Ann", "I"]
#guard outcomeAt (eta) "impart_permitted" (model []) ["Ann", "I"]
-- the default variant (`generally may`) likewise
#guard diag (eta [] (defaultNode "may-impart" "impart_permitted" true)) == "ok"
#guard !selectsAt (eta [] (defaultNode "may-impart" "impart_permitted" true)) "may-impart" aimed ["Ann", "I"]
-- an outside default `should impart` (a `require` on the dual) is blocked by the bar there
#guard diag (eta [defaultNode "should-impart" "impart_required" true]) == "ok"
#guard !outcomeAt (eta [defaultNode "should-impart" "impart_required" true]) "impart_required" aimed ["Ann", "I"]
#guard outcomeAt (eta [defaultNode "should-impart" "impart_required" true]) "impart_required" (model []) ["Ann", "I"]

/-! ## Diagnostics (ο, π, υ, φ and the shape table) -/

def seven (k : Nat) : RightsDoc :=
  mkRights ["state", "person"] [("arbitrary_arrest", ["state", "person"])]
    [perm "arrest_permitted" ["state", "person"] true "{0} arrest {1}"] [] block
    [⟨"r9", "person", .top, [line .claim (strictNode "no-arrest" "arrest_permitted" false .top
      ((List.range k).map (fun _ => .binary "arbitrary_arrest" (.var 1) (.var 0))))]⟩] [l29] []

#guard diag (seven 7) == "ResourceLimit: carve-outs of rule no-arrest"
#guard diag (seven 6) == "ok"
#guard diag { gamma with limits := [{ l29 with decidedBy := none }] } == "MissingExceptionDecider: limitation l29"
#guard diag { eta with bars := [⟨"b30", .rule, some "unstated"⟩, ⟨"b31", .query, some "unstated"⟩] } ==
  "DuplicateDeclaration: bar"

def arrestDoc (rs : List Right) : RightsDoc :=
  mkRights ["state", "person"] [] [perm "arrest_permitted" ["state", "person"] true "{0} arrest {1}"] [] block rs [] []

#guard diag (arrestDoc [⟨"r9", "person", .top, [line .claim (strictNode "rights-x" "arrest_permitted" false)]⟩]) ==
  "InvalidInput: name rights-x begins with rights-"
#guard diag (arrestDoc [⟨"rights-9", "person", .top, [line .claim (strictNode "x" "arrest_permitted" false)]⟩]) ==
  "InvalidInput: name rights-9 begins with rights-"
#guard diag (arrestDoc [⟨"r9", "person", .top, []⟩]) == "RightWithoutIncident: r9"
#guard diag (arrestDoc [⟨"r9", "person", .top, [line .liberty (strictNode "x" "arrest_permitted" false)]⟩]) ==
  "IncidentShape: x on right r9"
#guard diag (arrestDoc [⟨"r9", "person", .top, [line .claim (strictNode "x" "arrest_permitted" false (over := ["rights-bar-1"]))]⟩]) ==
  "UnknownSymbol: rule rights-bar-1"

def longParty : String := String.mk (List.replicate 64 'a')
def party39 : String := String.mk (List.replicate 39 'a')

def betaSwitch (π : String) : RightsDoc :=
  let d := beta fanMap
  { d with soft := { d.soft with soft := { noSoft with parties := [π] } },
           rs := [⟨"r5", "person", .top, [fanLine fanMap [π]]⟩] }

#guard diag (betaSwitch longParty) == s!"ResourceLimit: identifier soft__off__rights_fan_1__{longParty} exceeds 64 bytes"
#guard diag (betaSwitch party39) == "ok"

def phi (slot : Nat) : RightsDoc :=
  mkRights ["state", "person"] [("has_nationality", ["person"])]
    [perm "deprive_of_nationality_permitted" ["state", "person"] true "{0} deprive {1} of nationality"] []
    ⟨["person"], ["state", "person"], [], [⟨"deprive_of_nationality_permitted", slot, "has_nationality", none⟩]⟩
    [⟨"r15", "person", .top, [line .immunity (strictNode "no-deprivation" "deprive_of_nationality_permitted" false)]⟩]
    [] []

#guard diag (phi 1) == "ok"
#guard diag (phi 0) == "InvalidInput: alters deprive_of_nationality_permitted"

/-! ## (μ) collisions, binary shape

`publish_about(person, person)` stands for μ's ternary act: the liberty of right 19 has the
holder at the subject slot 0, the claim of right 12 at the object slot 1. Both lines are in scope
of limitation 29 so the audit ranges over them; each default line cites its exception. -/

def publishRegs : List Regulated :=
  [oblig "publish_about_required" ["person", "person"] false (some "publish_about_permitted") "{0} publish about {1}",
   perm "publish_about_permitted" ["person", "person"] true "{0} publish about {1}"]

def ranked : SoftEnv :=
  { noSoft with ranks := ["dignity", "expression"], outranks := [("dignity", "expression")],
                below := VE.SoftNorms.closureOf ["dignity", "expression"] [("dignity", "expression")] }

def citedLine (kind : Kind) (n : SoftNode) (slot : Option Nat) (cites : List (String × List String)) : SourceLine :=
  ⟨kind, some n, none, none, [], slot, cites⟩

def exceptionCite : List (String × List String) := [("exception", ["u1"])]

def mu (liberty claim : SoftNode) (libertyCites claimCites : List (String × List String)) (bars : List Bar := []) :
    RightsDoc :=
  let d := mkRights ["person"] [("attacks_honour", ["person", "person"])] publishRegs [] ⟨["person"], ["person"], [], []⟩
    [⟨"r19", "person", .top, [citedLine .liberty liberty none libertyCites]⟩,
     ⟨"r12", "person", .top, [citedLine .claim claim (some 1) claimCites]⟩] [l29] bars
  { d with soft := { d.soft with soft := ranked } }

def mayPublish : SoftNode := { defaultNode "may-publish" "publish_about_permitted" true with rank := some "expression" }
def noAttack : SoftNode :=
  { defaultNode "no-attack" "publish_about_permitted" false (.binary "attacks_honour" (.var 1) (.var 0)) with
    rank := some "dignity" }

#guard diag (mu mayPublish noAttack exceptionCite exceptionCite) == "ok"
-- both default and ranked: the liberty of right 19 is dominated by the claim of right 12
#guard (narrowings (mu mayPublish noAttack exceptionCite exceptionCite)
    (lineAt (mu mayPublish noAttack exceptionCite exceptionCite) "may-publish")).contains (.dominatedBy "no-attack")
-- an uncited rank is no collision: the dominance is a finding (fixture μ, 13.6)
#guard (limitationScope (mu mayPublish noAttack exceptionCite exceptionCite) []).map (·.text) ==
  ["UnlicensedLimitation: dominatedBy no-attack of rule may-publish on right r19"]
-- the rank cited on the dominated line, or on the dominating line: a collision resolved by a cited ranking
#guard limitationScope (mu mayPublish noAttack (exceptionCite ++ [("rank", ["u1"])]) exceptionCite) [] == []
#guard limitationScope (mu mayPublish noAttack exceptionCite (exceptionCite ++ [("rank", ["u1"])])) [] == []
#guard rightCollision (mu mayPublish noAttack exceptionCite (exceptionCite ++ [("rank", ["u1"])]))
  (lineAt (mu mayPublish noAttack exceptionCite exceptionCite) "may-publish") (.dominatedBy "no-attack")
#guard !rightCollision (mu mayPublish noAttack exceptionCite exceptionCite)
  (lineAt (mu mayPublish noAttack exceptionCite exceptionCite) "may-publish") (.dominatedBy "no-attack")
-- the strict liberty blocks the default claim: another right's strict line collides, no finding
def strictPublish : SoftNode := strictNode "may-publish" "publish_about_permitted" true
#guard diag (mu strictPublish noAttack [] exceptionCite) == "ok"
#guard limitationScope (mu strictPublish noAttack [] exceptionCite) [] == []
#guard rightCollision (mu strictPublish noAttack [] exceptionCite)
  (lineAt (mu strictPublish noAttack [] exceptionCite) "no-attack") (.blockedBy "may-publish")

/-! ## (ψ) the bar across the dual pair, binary shape

A default positive claim of right 12 on the dual obligation `publish_about_required` (holder at
the object slot 1) under the rule reading of the bar, with the strict liberty of right 19 making
`publish_about_permitted` right-derived. -/

def shouldPublish : SoftNode := defaultNode "should-publish" "publish_about_required" true
def barRule : Bar := ⟨"b30", .rule, some "unstated"⟩

def psi (claim : SoftNode) (withLiberty : Bool := true) : RightsDoc :=
  let d := mu strictPublish claim [] exceptionCite [barRule]
  if withLiberty then d else { d with rs := d.rs.filter (·.name != "r19") }

def psiLine (D : RightsDoc) (n : String) : Line := lineAt D n

def aimedPsi : VE.FiniteModel String := model [("rights__bar__1", [["Ann", "Bob"]])]

#guard diag (psi shouldPublish) == "ok"
#guard barReach (psi shouldPublish) (psiLine (psi shouldPublish) "should-publish") == some "publish_about_permitted"
#guard (narrowings (psi shouldPublish) (psiLine (psi shouldPublish) "should-publish")).contains .bar
-- the claim is blocked across the pair where the act is aimed at destruction; nothing is unlicensed
#guard limitationScope (psi shouldPublish) [] == []
#guard !selectsAt (psi shouldPublish) "should-publish" aimedPsi ["Ann", "Bob"]
#guard !outcomeAt (psi shouldPublish) "publish_about_required" aimedPsi ["Ann", "Bob"]
#guard !outcomeAt (psi shouldPublish) "publish_about_permitted" aimedPsi ["Ann", "Bob"]
#guard selectsAt (psi shouldPublish) "should-publish" (model []) ["Ann", "Bob"]
-- the same claim as strict `must publish`: not blocked, no bar reach, it selects (the pair conflict of 4.7)
#guard barReach (psi (strictNode "should-publish" "publish_about_required" true))
  (psiLine (psi (strictNode "should-publish" "publish_about_required" true)) "should-publish") == none
#guard selectsAt (psi (strictNode "should-publish" "publish_about_required" true)) "should-publish" aimedPsi ["Ann", "Bob"]
-- without the liberty of right 19 the permission is not right-derived: no bar reach, the claim selects
#guard diag (psi shouldPublish false) == "ok"
#guard barReach (psi shouldPublish false) (psiLine (psi shouldPublish false) "should-publish") == none
#guard selectsAt (psi shouldPublish false) "should-publish" (model []) ["Ann", "Bob"]

/-! ## (σ) same-effect strict blocking and (κ) force under limitation 29 -/

def sigma (outside : List SoftNode) (cites : List (String × List (String × List String)) := []) : RightsDoc :=
  let d := mkRights ["person", "idea"] [("journalist", ["person"])] impartRegs outside ⟨["person"], ["person"], [], []⟩
    [⟨"r19", "person", .top, [citedLine .liberty (defaultNode "may-impart" "impart_permitted" true) none exceptionCite]⟩]
    [l29] []
  { d with outsideCites := cites }

def rule4 (sign : Bool) : SoftNode := strictNode "rule-4" "impart_permitted" sign (.unary "journalist" (.var 1))

#guard diag (sigma [rule4 true]) == "ok"
-- a strict rule of the line's own effect: listed, licensed by construction, no finding
#guard (narrowings (sigma [rule4 true]) (psiLine (sigma [rule4 true]) "may-impart")).contains (.blockedBy "rule-4")
#guard sameEffectStrict (sigma [rule4 true]) (psiLine (sigma [rule4 true]) "may-impart") "rule-4"
#guard limitationScope (sigma [rule4 true]) [] == []
-- the opposite effect outside rights: unlicensed unless the rule cites the narrowing
#guard (limitationScope (sigma [rule4 false]) []).map (·.text) ==
  ["UnlicensedLimitation: blockedBy rule-4 of rule may-impart on right r19"]
#guard limitationScope (sigma [rule4 false] [("rule-4", [("narrows:may-impart", ["u1"])])]) [] == []

def securityRegs : List Regulated :=
  [oblig "secure_required" ["state", "person"] false (some "secure_permitted") "{0} secure social security for {1}",
   perm "secure_permitted" ["state", "person"] true "{0} secure social security for {1}"]

def kappa (n : SoftNode) (cites : List (String × List String)) : RightsDoc :=
  mkRights ["state", "person"] [] securityRegs [] block [⟨"r25", "person", .top, [citedLine .claim n none cites]⟩] [l29] []

-- the default choice: its exception is uncited, a finding; the strict choice has no exception
#guard (limitationScope (kappa (defaultNode "secure" "secure_required" true) []) []).map (·.text) ==
  ["UnlicensedLimitation: exception of rule secure on right r25"]
#guard limitationScope (kappa (strictNode "secure" "secure_required" true) []) [] == []
-- Art. 22: the exception cites its source clause, licensed
#guard limitationScope (kappa (defaultNode "secure" "secure_required" true) exceptionCite) [] == []

end VE.Rights.Examples
